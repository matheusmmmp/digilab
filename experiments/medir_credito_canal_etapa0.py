"""A etapa 0 do credito por canal ate o alvo (V3-9; docs/TAREFA_V2_V3_CREDITO_CANAL.md, secoes 3 a 5): as tabelas SOMBRA e a G0-PODE-MUDAR.

Medicao DESCRITIVA, nas sementes dos testes, sem run de pesquisa. Nao muda o cerebro nem o motor: embrulha tres metodos da PoliticaLobos
durante a medida, e os embrulhos so leem e chamam o original:
  - `_creditar_canais`: antes do credito de hoje, os canais da decisao vao as tabelas sombra das tres chaves de comer
    (`pedido_necessidade:comer`, `fome_moderada:comer`, `fruta_no_cenario:comer`; CC-3), pela mesma regra (`atualizar_fruta`, o mesmo
    registro da sub-decisao, o mesmo passo):
      * `escalar`: o sinal inteiro, o teto de hoje. Tem de ser a tabela de verdade, peso a peso, depois de cada credito (falha alto);
      * `c1`: um peso por grupo (CC-2: o humor, o gosto e a nutricao, que e todo o resto), cada grupo cortado no seu `prior +- teto`; o
        prior todo na nutricao (`w0_alvo`), 0 no humor e no gosto (C1, CC-1);
      * `escalar_sem_teto` e `grupos_sem_teto`: os mesmos sem corte, para a conta da linearidade (secao 0 da tarefa);
  - `_aplicar_sinal`: confere que a classe do alvo de comer so aprende pelo `_creditar_canais` (outra via, falha alto);
  - `_alvo_aprendido`: na decisao do alvo de comer, refaz a leitura de hoje e confere contra o `P` registrado (falha alto), e le a P da
    classe `comida:x` pela leitura de hoje e pela soma dos grupos da C1, e se o sorteio com o mesmo `u` mudaria de classe.
Nada disso entra na escolha: as vidas sao conferidas contra o gabarito gravado antes (`tests/gabaritos/credito_canal_vidas_de_hoje.json`,
G2), e as sombras da vida e as do replay de medicao saem iguais.

As oportunidades sao as do T1 do J5 (`BancadaPQP.medir`, adendos 7 e 8: a decisao de comer com a x ao lado e uma alternativa). O T1-R
(secao 4 da tarefa) e o T1 sem o corte da reexperiencia: todas as oportunidades depois de `T_m` na janela.

A G0-PODE-MUDAR (secao 5 da tarefa; o limiar 0,05 e PROPOSTO, SEM FONTE): se a mediana de |P_c1(x) - P_hoje(x)| nas oportunidades do T1-R
(todas as vidas juntas) for < 0,05, a C1 nao tem o que mudar, e a tarefa para antes de tocar em `digilab/`.

    python experiments/medir_credito_canal_etapa0.py      # grava artifacts_v2_v3/credito_canal_etapa0.json
"""
from __future__ import annotations

import json
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada.pet_que_pensa as bpq  # noqa: E402
import bancada_v2 as bv  # noqa: E402
import gabarito_credito_canal as gc  # noqa: E402

from digilab.events import AcaoPet  # noqa: E402
from digilab.policies import lobos  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v2_v3" / "credito_canal_etapa0.json"
BRACO = "P1"                                       # a V3-9 e o P1 sem o planejador (CC-5)
SEMENTES = gc.SEMENTES
CHAVES_COMER = ("pedido_necessidade:comer", "fome_moderada:comer", "fruta_no_cenario:comer")
GRUPOS = ("humor", "gosto", "nutricao")
LIMIAR_G0 = 0.05                                   # PROPOSTO, SEM FONTE (a tarefa, secao 5)
SEM_TETO = 1 << 62
N_ULTIMAS = 3                                      # as 3 ultimas oportunidades do T1-R (o f_R da tarefa, secao 4)


def grupo_do_canal(canal: str) -> str:
    return canal if canal in ("humor", "gosto") else "nutricao"


class _Sombra:
    """as tabelas sombra de uma politica (uma vida ou um replay) e o que a medida le delas"""

    def __init__(self, cerebro: lobos.PoliticaLobos) -> None:
        prior = cerebro._prior_alvo_mundo
        faltam = [k for k in CHAVES_COMER if k not in prior]
        if faltam:
            raise RuntimeError(f"sombra: chaves de comer sem tabela no cerebro: {faltam}")
        self.prior = {k: dict(prior[k]) for k in CHAVES_COMER}
        zero = {k: {c: 0 for c in prior[k]} for k in CHAVES_COMER}
        self.prior_g = {"humor": zero, "gosto": zero, "nutricao": self.prior}
        self.escalar = {k: dict(t) for k, t in self.prior.items()}
        self.escalar_sem_teto = {k: dict(t) for k, t in self.prior.items()}
        self.c1 = {g: {k: dict(t) for k, t in self.prior_g[g].items()} for g in GRUPOS}
        self.grupos_sem_teto = {g: {k: dict(t) for k, t in self.prior_g[g].items()} for g in GRUPOS}
        self.cortes = {"escalar": 0, **{f"c1_{g}": 0 for g in GRUPOS}}
        self.creditos: list[dict] = []
        self.decisoes: list[dict] = []
        self.dentro_do_creditar = False

    def creditar(self, cerebro, registro: dict, canais: dict, f_S: int) -> None:
        sub = registro["alvo_mundo"]
        k = sub["chave"]
        f_g = {g: 0 for g in GRUPOS}
        for canal, f in canais.items():
            f_g[grupo_do_canal(canal)] += f
        if sum(f_g.values()) != f_S:
            raise RuntimeError(f"sombra: os grupos somam {sum(f_g.values())}, o escalar e {f_S} (K-6)")
        cl, S = cerebro.cl, cerebro._escala
        self.cortes["escalar"] += lobos.atualizar_fruta(self.escalar[k], self.prior[k], sub, f_S, cl.passo, cl.teto, S)
        lobos.atualizar_fruta(self.escalar_sem_teto[k], self.prior[k], sub, f_S, cl.passo, SEM_TETO, S)
        for g in GRUPOS:
            self.cortes[f"c1_{g}"] += lobos.atualizar_fruta(self.c1[g][k], self.prior_g[g][k], sub, f_g[g], cl.passo, cl.teto, S)
            lobos.atualizar_fruta(self.grupos_sem_teto[g][k], self.prior_g[g][k], sub, f_g[g], cl.passo, SEM_TETO, S)
        self.creditos.append({"k": len(cerebro.motivos) - 1, "chave": k, "classe": sub["acao"], "f": f_S, "f_grupos": f_g})

    def conferir(self, cerebro) -> None:
        for k in CHAVES_COMER:
            if self.escalar[k] != cerebro._pesos_alvo_mundo[k]:
                raise RuntimeError(f"sombra: a tabela escalar de {k} nao e a de verdade ({self.escalar[k]} != {cerebro._pesos_alvo_mundo[k]})")

    def soma_c1(self, k: str, c: str) -> int:
        return sum(self.c1[g][k][c] for g in GRUPOS)


def _leitura(pesos_de: dict, classes: list, c_padrao: str, S: int) -> list[float]:
    """a leitura de hoje (`_alvo_aprendido`, o ramo sem o planejador): max(0, w)/S, mais 1 na classe do padrao"""
    return [max(0, pesos_de[c]) / S + (1.0 if c == c_padrao else 0.0) for c in classes]


def _p(pesos: list[float], i: int) -> float:
    total = 0.0
    for p in pesos:
        total = total + p
    return pesos[i] / total


_SOMBRAS: list = []          # (cerebro, sombra), na ordem em que as politicas aparecem (a vida, o replay do G1, o replay da medida)
_LINHAS: list = []           # as linhas do T1 que o `medir` passa ao `mudanca_de_escolha`


def _sombra_de(cerebro) -> _Sombra:
    s = cerebro.__dict__.get("_sombra_cc")
    if s is None:
        s = _Sombra(cerebro)
        cerebro.__dict__["_sombra_cc"] = s
        _SOMBRAS.append((cerebro, s))
    return s


def _instalar(x: str) -> dict:
    orig = {n: getattr(lobos.PoliticaLobos, n) for n in ("_creditar_canais", "_aplicar_sinal", "_alvo_aprendido")}
    orig_mudanca = bpq.mudanca_de_escolha

    def _creditar_canais(self, registro, canais, f_S):
        sub = registro.get("alvo_mundo")
        s = _sombra_de(self) if self._prior_alvo_mundo else None
        comer = sub is not None and sub["chave"] in CHAVES_COMER
        if comer:
            s.creditar(self, registro, canais, f_S)
            s.dentro_do_creditar = True
        try:
            orig["_creditar_canais"](self, registro, canais, f_S)
        finally:
            if comer:
                s.dentro_do_creditar = False
        if comer:
            s.conferir(self)

    def _aplicar_sinal(self, registro, f_S, consequencia=False, alvos=None):
        sub = registro.get("alvo_mundo")
        if consequencia and sub is not None and sub["chave"] in CHAVES_COMER and f_S != 0 and not _sombra_de(self).dentro_do_creditar:
            raise RuntimeError("sombra: a classe do alvo de comer aprendeu fora do _creditar_canais")
        return orig["_aplicar_sinal"](self, registro, f_S, consequencia, alvos)

    def _alvo_aprendido(self, acao, candidatos, percepcao, u):
        res = orig["_alvo_aprendido"](self, acao, candidatos, percepcao, u)
        sub = None if self._registro_decisao is None else self._registro_decisao.get("alvo_mundo")
        if acao is not AcaoPet.COMER or sub is None or sub["chave"] not in CHAVES_COMER:
            return res
        if self._plano_na_decisao is not None:
            raise RuntimeError("sombra: a etapa 0 e do P1, sem o planejador")
        if self._paladar is None:
            raise RuntimeError("sombra: o J5 da etapa 0 e com o paladar (as classes comida:<tipo>)")
        from digilab.mundo import alvo_padrao_de
        s, S, k = _sombra_de(self), self._escala, sub["chave"]
        classes = list(sub["candidatos"])
        padrao = alvo_padrao_de(acao, candidatos, percepcao, self._cfg_mundo)
        podres = {i for i, tipo, *_ in percepcao.vistos if tipo.endswith("_podre")}
        tipos = {i: tipo for i, tipo, *_ in percepcao.vistos}
        c_padrao = (("comida_podre" if padrao.id in podres else f"comida:{tipos[padrao.id]}") if padrao.tipo == "comida"
                    else lobos.CLASSE_DO_CANDIDATO.get(padrao.tipo, padrao.tipo))
        hoje = _leitura(self._pesos_alvo_mundo[k], classes, c_padrao, S)
        total = 0.0
        for p in hoje:
            total = total + p
        if {c: lobos.arred(p / total * S) for c, p in zip(classes, hoje)} != sub["P"]:
            raise RuntimeError("sombra: a leitura refeita nao e o P registrado")
        cx = f"comida:{x}"
        if cx in classes:
            i = classes.index(cx)
            c1 = _leitura({c: s.soma_c1(k, c) for c in classes}, classes, c_padrao, S)
            st = _leitura({c: sum(s.grupos_sem_teto[g][k][c] for g in GRUPOS) for c in classes}, classes, c_padrao, S)
            et = _leitura(s.escalar_sem_teto[k], classes, c_padrao, S)
            escolhida = classes.index(sub["acao"])
            s.decisoes.append({"k": len(self.motivos) - 1, "chave": k, "classes": classes, "padrao": c_padrao, "escolhida": sub["acao"],
                               "p_hoje": _p(hoje, i), "p_c1": _p(c1, i), "p_grupos_sem_teto": _p(st, i), "p_escalar_sem_teto": _p(et, i),
                               "c1_mudaria": lobos.sortear(c1, u / lobos.ESCALA_U_ALVO) != escolhida,
                               "w_x": {"hoje": self._pesos_alvo_mundo[k][cx], **{g: s.c1[g][k][cx] for g in GRUPOS}}})
        return res

    def mudanca_de_escolha(linhas, n, tick_mudanca):
        _LINHAS.append([dict(ln) for ln in linhas])
        return orig_mudanca(linhas, n, tick_mudanca)

    for n_, f in (("_creditar_canais", _creditar_canais), ("_aplicar_sinal", _aplicar_sinal), ("_alvo_aprendido", _alvo_aprendido)):
        setattr(lobos.PoliticaLobos, n_, f)
    bpq.mudanca_de_escolha = mudanca_de_escolha
    return {**orig, "mudanca": orig_mudanca}


def _desinstalar(orig: dict) -> None:
    for n in ("_creditar_canais", "_aplicar_sinal", "_alvo_aprendido"):
        setattr(lobos.PoliticaLobos, n, orig[n])
    bpq.mudanca_de_escolha = orig["mudanca"]


def _resumo_sombra(s: _Sombra) -> dict:
    return {"escalar": s.escalar, "c1": s.c1, "cortes": s.cortes, "creditos": s.creditos, "decisoes": s.decisoes}


def vida(semente: int) -> dict:
    """uma vida do T1 do P1 com as sombras: a vida (conferida contra o gabarito), o replay do G1 e o da medida; as sombras da vida e as da
    medida tem de ser iguais; as oportunidades vem das linhas do `medir`"""
    bp = gc.bancada()
    x = bp.fruta_x(semente)
    _SOMBRAS.clear()
    _LINHAS.clear()
    orig = _instalar(x)
    try:
        v = bp.vida(bv.EspecPQP(BRACO, "T1", semente))
        medida = bp.medir(v)
    finally:
        _desinstalar(orig)
    chave = f"T1|{BRACO}|{semente}"
    gabarito = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))[chave]
    if gc.impressao(v.motor) != gabarito:
        raise RuntimeError(f"G2: a vida {chave} com as sombras nao e a do gabarito")
    if len(_SOMBRAS) != 3 or len(_LINHAS) != 1:
        raise RuntimeError(f"esperadas 3 politicas (vida, G1, medida) e 1 chamada do T1; vieram {len(_SOMBRAS)} e {len(_LINHAS)}")
    resumos = [_resumo_sombra(s) for _c, s in _SOMBRAS]
    if any(r != resumos[0] for r in resumos[1:]):
        raise RuntimeError(f"{chave}: as sombras da vida e as dos replays divergem")
    cerebro, s = _SOMBRAS[-1]
    linhas = _LINHAS[0]
    if len(linhas) != len(cerebro.motivos):
        raise RuntimeError(f"{chave}: {len(linhas)} linhas do T1 e {len(cerebro.motivos)} decisoes do cerebro")
    por_k = {d["k"]: d for d in s.decisoes}
    ops = []
    for k, ln in enumerate(linhas):
        if not ln["conta"]:
            continue
        d = por_k.get(k)
        if d is None:
            raise RuntimeError(f"{chave}: a oportunidade da decisao {k} sem a leitura sombra do alvo de comer")
        if ln["sucesso"] and d["escolhida"] != f"comida:{x}":
            raise RuntimeError(f"{chave}: a decisao {k} escolheu a x, e a classe sorteada foi {d['escolhida']}")
        ops.append({"k": k, "tick": ln["tick"], "depois": ln["depois"], "sucesso": ln["sucesso"], "reexperiencia": ln["reexperiencia"],
                    **{c: d[c] for c in ("chave", "p_hoje", "p_c1", "p_grupos_sem_teto", "p_escalar_sem_teto", "c1_mudaria", "w_x")}})
    k_tm = next((k for k, ln in enumerate(linhas) if ln["depois"]), None)
    cx = f"comida:{x}"
    creditos_x = [c for c in s.creditos if c["classe"] == cx]
    dif_lin = max(abs(sum(s.grupos_sem_teto[g][k][c] for g in GRUPOS) - s.escalar_sem_teto[k][c])
                  for k in CHAVES_COMER for c in s.escalar_sem_teto[k])
    return {"semente": semente, "x": x, "tick_mudanca": v.tick_mudanca, "decisoes": len(linhas), "k_mudanca": k_tm,
            "cl": {"teto": cerebro.cl.teto, "passo": cerebro.cl.passo, "w0_alvo": cerebro.cl.w0_alvo},
            "t1": {c: medida["t1"][c] for c in ("queda", "f_antes", "f_depois", "sem_oportunidade") if c in medida["t1"]},
            "oportunidades": ops,
            "creditos_comer": len(s.creditos),
            "creditos_x": {"antes": [c for c in creditos_x if k_tm is None or c["k"] < k_tm],
                           "depois": [c for c in creditos_x if k_tm is not None and c["k"] >= k_tm]},
            "cortes_no_teto": s.cortes,
            "w_x_fim": {"hoje": {k: cerebro._pesos_alvo_mundo[k][cx] for k in CHAVES_COMER},
                        **{g: {k: s.c1[g][k][cx] for k in CHAVES_COMER} for g in GRUPOS}},
            "linearidade": {"max_dif_soma_dos_grupos_contra_escalar_sem_teto": dif_lin, "creditos": len(s.creditos),
                            "limite_do_arredondamento": len(s.creditos) * len(GRUPOS)}}


def _media(xs: list) -> float | None:
    return None if not xs else sum(xs) / len(xs)


def analisar(vidas: list[dict]) -> dict:
    depois = [o for v in vidas for o in v["oportunidades"] if o["depois"]]
    antes = [o for v in vidas for o in v["oportunidades"] if not o["depois"]]
    dif = [abs(o["p_c1"] - o["p_hoje"]) for o in depois]
    mediana = statistics.median(dif) if dif else None
    out = {"oportunidades": {"antes": len(antes), "depois_t1r": len(depois)},
           "g0_pode_mudar": {"limiar": LIMIAR_G0, "mediana_abs_dp": mediana,
                             "passa": None if mediana is None else mediana >= LIMIAR_G0,
                             "frac_abs_dp_acima_do_limiar": _media([d >= LIMIAR_G0 for d in dif]),
                             "media_dp_c1_menos_hoje": _media([o["p_c1"] - o["p_hoje"] for o in depois]),
                             "frac_c1_mudaria_a_classe": _media([o["c1_mudaria"] for o in depois])},
           "p_x_media": {"antes": {"hoje": _media([o["p_hoje"] for o in antes]), "c1": _media([o["p_c1"] for o in antes])},
                         "depois_t1r": {"hoje": _media([o["p_hoje"] for o in depois]), "c1": _media([o["p_c1"] for o in depois])}},
           "linearidade": {"max_dif": max(v["linearidade"]["max_dif_soma_dos_grupos_contra_escalar_sem_teto"] for v in vidas),
                           "dentro_do_arredondamento": all(v["linearidade"]["max_dif_soma_dos_grupos_contra_escalar_sem_teto"]
                                                           <= v["linearidade"]["limite_do_arredondamento"] for v in vidas),
                           "dif_p_grupos_sem_teto_contra_escalar_sem_teto_max": max(
                               [abs(o["p_grupos_sem_teto"] - o["p_escalar_sem_teto"]) for v in vidas for o in v["oportunidades"]],
                               default=None)},
           "cortes_no_teto": {c: sum(v["cortes_no_teto"][c] for v in vidas) for c in vidas[0]["cortes_no_teto"]},
           "cl": vidas[0]["cl"] if all(v["cl"] == vidas[0]["cl"] for v in vidas) else None,
           "max_abs_w_x_menos_prior_fim": max(abs(w - (v["cl"]["w0_alvo"] if g in ("hoje", "nutricao") else 0))
                                              for v in vidas for g, t in v["w_x_fim"].items() for w in t.values()),
           "credito_x_por_grupo": {}}
    for fase in ("antes", "depois"):
        cs = [c for v in vidas for c in v["creditos_x"][fase]]
        out["credito_x_por_grupo"][fase] = {"n": len(cs), **{g: _media([c["f_grupos"][g] for c in cs]) for g in GRUPOS},
                                            "f": _media([c["f"] for c in cs])}
    por_vida = []
    for v in vidas:
        dv = [o for o in v["oportunidades"] if o["depois"]]
        av = [o for o in v["oportunidades"] if not o["depois"]]
        por_vida.append({"semente": v["semente"], "x": v["x"], "t1": v["t1"], "oportunidades_depois": len(dv),
                         "mediana_abs_dp": statistics.median([abs(o["p_c1"] - o["p_hoje"]) for o in dv]) if dv else None,
                         "f_antes": _media([o["sucesso"] for o in av[-N_ULTIMAS:]]),
                         "f_r": _media([o["sucesso"] for o in dv[-N_ULTIMAS:]]),
                         "reexperiencias_depois": sum(o["reexperiencia"] for o in dv)})
    out["por_vida"] = por_vida
    return out


def main() -> dict:
    with ProcessPoolExecutor() as ex:
        vidas = list(ex.map(vida, SEMENTES))
    out = {"versao": 1, "config": str(gc.CONFIG.relative_to(RAIZ)).replace("\\", "/"), "duracao": gc.DURACAO, "braco": BRACO,
           "protocolo": "T1", "sementes": list(SEMENTES), "chaves": list(CHAVES_COMER), "grupos": list(GRUPOS),
           "analise": analisar(vidas), "vidas": vidas}
    ARQUIVO.parent.mkdir(exist_ok=True)
    ARQUIVO.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: x for k, x in r["analise"].items() if k != "por_vida"}, indent=1, ensure_ascii=False))
    print(json.dumps(r["analise"]["por_vida"], indent=1, ensure_ascii=False))
