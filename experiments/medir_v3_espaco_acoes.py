"""V3, o espaco de acoes e as oportunidades de escolha do cerebro A (docs/TAREFA_V2_V3.md; docs/futuro/v3_espaco_acoes.md).

Medicao DESCRITIVA, sem gate e sem plano de analise, nas sementes dos testes (101...505), como o E0
(`experiments/medir_e0_influencia_aprendido.py`). Nao muda o cerebro nem o motor: so le o que a politica registra e, para o credito, embrulha
o `_aplicar_sinal` do cerebro durante a medida (o embrulho chama o original e anota os pesos antes e depois; a vida e a mesma, conferido pelo
sha do estado interno contra a vida sem o embrulho).

Quatro coisas separadas (a tarefa, secao 3, item 2, e os criterios de aceitacao):
  1. o inventario: as acoes de cada regra no prior do cerebro (o que o A pode escolher em cada contexto), as acoes que so existem em regras
     forcadas, as acoes com alvo e as classes do alvo no mundo fisico;
  2. a prioridade fixa: em cada decisao, as regras do instinto cuja condicao vale (a mesma conta de `PoliticaInstinto.agir`, sem a ordem),
     conferidas contra a regra registrada (a primeira que vale na ordem tem de ser ela; diverge, falha alto). Numa decisao forcada, as
     outras regras que tambem valem e a uniao dos candidatos delas sao as propostas que a prioridade fecha;
  3. o credito: cada aplicacao do sinal (a consequencia pelo corpo e os gestos), com o numero de candidatos da decisao creditada e se algum
     peso mudou de verdade (a regra da L1 multiplica por S*1[a=a*] - P_a, zero com um candidato so);
  4. a diversidade por contexto: por regra, a entropia da politica na decisao (H(P)) contra a do prior com os mesmos impulsos (H(P0)), e a
     frequencia empirica das acoes.
E, no mundo fisico (o braco P1-alvo do MUNDO-ALVO, vidas curtas): as subdecisoes do alvo (quantos candidatos e classes por decisao de comer
e explorar, e quantas vezes o alvo aprendido escolheu outra classe que a do padrao do motor).
E o J5 (o T1 do piloto do adendo 7, na config da fumaca dele, com as sementes dos testes e a duracao do piloto, 7 + 5 dias): depois da
mudanca (a x passa a fazer mal, dada na mao), quantas vezes o proprio pet come a x (o que credita a politica) contra as vezes que a recebe na
mao (que so os modelos do planejador veem, G-SEM-CREDITO), o peso da classe `comida:x` do alvo aprendido e o humor previsto da x no modelo
do desfecho, na mudanca e no fim.

    python experiments/medir_v3_espaco_acoes.py      # grava artifacts_v2_v3/espaco_acoes.json
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402

from digilab.config import CONFIG_LOBOS, CONFIG_PADRAO  # noqa: E402
from digilab.events import ACOES_PET_HOJE, AcaoPet  # noqa: E402
from digilab.policies import lobos  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v2_v3" / "espaco_acoes.json"
DIAS = 14
ORCAMENTO = 16 * DIAS
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = tuple(sorted(bv.SEMENTES_TESTE))
# a ordem e as regras do PoliticaInstinto.agir (digilab/policy.py); a conferencia contra a regra registrada fecha a correspondencia
ORDEM_INSTINTO = ("sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono", "fome_moderada", "tempo_livre")
MUNDO_ALVO = RAIZ / "experiments" / "configs" / "v2_mundo_alvo" / "fumaca_piloto.json"
DIAS_MUNDO = 4
J5 = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca_piloto_adendo7.json"
J5_DURACAO = {"d_a": 7, "janela": 5}            # a do piloto do adendo 7 (o plano, A7.8), aqui com as sementes dos testes
J5_BRACOS = ("P1", "P1-plan")


def regras_que_valem(p: dict, cfg=CONFIG_PADRAO) -> list[str]:
    """As regras do instinto cuja condicao vale na percepcao `p` (o `percepcao` do motivo), na ordem do instinto. O tempo livre vale sempre
    (e o caso de nada mais valer). Os limiares sao os literais de `PoliticaInstinto.agir`; o abandono, ticks sem cuidado > a janela, e
    o `ticks_sem_cuidado` da percepcao (ticks / escala, cortado em 1) acima da janela / escala."""
    janela = cfg.janela_atencao_ticks / CONFIG_LOBOS.escala_ticks_desde_cuidado
    valem = []
    if p["energia"] < 0.25:
        valem.append("sono_exaustao")
    if p["dormindo"] > 0.5 and p["energia"] < 0.85:
        valem.append("sono_continuar")
    if cfg.e_noite(int(p["hora"] * 1440)) and p["energia"] < 0.55:
        valem.append("sono_noite")
    if p["fome"] < 0.25 or p["higiene"] < 0.25:
        valem.append("pedido_necessidade")
    if p["ticks_sem_cuidado"] > janela:
        valem.append("abandono")
    if p["fome"] < 0.45:
        valem.append("fome_moderada")
    valem.append("tempo_livre")
    return valem


def candidatos_da_regra(regra: str, p: dict) -> set[str]:
    """os candidatos que o instinto propoe em cada regra (o abandono, emburrar ou chamar pelo humor)"""
    if regra in ("sono_exaustao", "sono_continuar", "sono_noite"):
        return {AcaoPet.DORMIR.value}
    if regra == "pedido_necessidade":
        return {AcaoPet.CHAMAR_ATENCAO.value}
    if regra == "abandono":
        return {AcaoPet.EMBURRAR.value if p["humor"] < 0.35 else AcaoPet.CHAMAR_ATENCAO.value}
    if regra == "fome_moderada":
        return {AcaoPet.COMER.value, AcaoPet.CHAMAR_ATENCAO.value}
    return {AcaoPet.OCIOSO.value, AcaoPet.EXPLORAR.value, AcaoPet.BRINCAR.value, AcaoPet.CHAMAR_ATENCAO.value}


def _entropia(ps: list[float]) -> float:
    return -sum(p * math.log2(p) for p in ps if p > 0)


def _vida(args: tuple) -> dict:
    dono, semente, embrulhar = args
    creditos: list[dict] = []
    original = lobos.PoliticaLobos._aplicar_sinal
    if embrulhar:
        def espiao(self, registro, f_S, consequencia=False, alvos=None):
            antes = (copy.deepcopy(self._pesos[registro["regra"]]), copy.deepcopy(self._pesos_corpo.get(registro["regra"])))
            original(self, registro, f_S, consequencia, alvos)
            depois = (self._pesos[registro["regra"]], self._pesos_corpo.get(registro["regra"]))
            creditos.append({"regra": registro["regra"], "n_cand": len(registro["candidatos"]), "f": f_S, "consequencia": consequencia,
                             "mudou": antes != depois})
        lobos.PoliticaLobos._aplicar_sinal = espiao
    try:
        b = gl.bancada_v11(DIAS, ORCAMENTO)
        v = b.vida(bv.EspecVida(dono, gl.BRACO_V11, semente))
    finally:
        lobos.PoliticaLobos._aplicar_sinal = original
    pol = v.motor.politica
    interno = pol.estado_interno()
    sha = hashlib.sha256(json.dumps(interno, sort_keys=True).encode()).hexdigest()
    if not embrulhar:
        return {"sha": sha}
    decs = []
    for m in pol.motivos:
        p = m["percepcao"]
        valem = regras_que_valem(p)
        if valem[0] != m["regra"]:
            raise RuntimeError(f"as regras refeitas ({valem}) nao dao a regra registrada {m['regra']!r}")
        cands = m["candidatos"]
        if set(cands) != candidatos_da_regra(m["regra"], p):
            raise RuntimeError(f"os candidatos refeitos da regra {m['regra']} nao sao os registrados {cands}")
        uniao = set().union(*(candidatos_da_regra(r, p) for r in valem))
        uniao_sem_livre = set().union(*(candidatos_da_regra(r, p) for r in valem if r != "tempo_livre"))
        c = m["contribuicoes"]
        if len(cands) > 1:
            efet = [m["pesos"][a] for a in cands]
            imp = [c["impulsos"][a] for a in cands]
            hp, hp0 = _entropia([x / sum(efet) for x in efet]), _entropia([x / sum(imp) for x in imp])
        else:
            hp = hp0 = 0.0
        decs.append({"regra": m["regra"], "acao": m["acao"], "n_cand": len(cands), "valem": valem,
                     "n_uniao": len(uniao), "n_uniao_sem_livre": len(uniao_sem_livre), "h": hp, "h0": hp0})
    return {"dono": dono, "semente": semente, "sha": sha, "decisoes": decs, "creditos": creditos}


def _frac(n, total):
    return None if not total else n / total


def analisar_v11(vidas: list[dict]) -> dict:
    todas = [d for v in vidas for d in v["decisoes"]]
    forcadas = [d for d in todas if d["n_cand"] == 1]
    por_regra = defaultdict(list)
    for d in todas:
        por_regra[d["regra"]].append(d)
    prioridade = {}
    for r, ds in sorted(por_regra.items()):
        outras = Counter(o for d in ds for o in d["valem"][1:] if o != "tempo_livre")
        prioridade[r] = {
            "n": len(ds), "frac_do_total": len(ds) / len(todas), "candidatos": sorted({d["n_cand"] for d in ds}),
            "frac_com_outra_regra_urgente": _frac(sum(any(o != "tempo_livre" for o in d["valem"][1:]) for d in ds), len(ds)),
            "outras_regras_que_valem": {k: v / len(ds) for k, v in sorted(outras.items())},
            "uniao_media_com_tempo_livre": sum(d["n_uniao"] for d in ds) / len(ds),
            "uniao_media_so_urgentes": sum(d["n_uniao_sem_livre"] for d in ds) / len(ds),
            "acoes": dict(sorted(Counter(d["acao"] for d in ds).items())),
            "h_politica_media": sum(d["h"] for d in ds) / len(ds), "h_prior_media": sum(d["h0"] for d in ds) / len(ds),
            "h_empirica": _entropia([n / len(ds) for n in Counter(d["acao"] for d in ds).values()]),
        }
    creditos = [c for v in vidas for c in v["creditos"]]
    def resumo_credito(cs):
        return {"aplicacoes": len(cs), "com_peso_mudado": sum(c["mudou"] for c in cs),
                "frac_mudou": _frac(sum(c["mudou"] for c in cs), len(cs)),
                "abs_f": sum(abs(c["f"]) for c in cs)}
    cred_um = [c for c in creditos if c["n_cand"] == 1]
    cred_esc = [c for c in creditos if c["n_cand"] > 1]
    abs_total = sum(abs(c["f"]) for c in creditos)
    return {
        "n_decisoes": len(todas),
        "frac_forcadas": len(forcadas) / len(todas),
        "forcadas_com_outra_regra_urgente": _frac(sum(any(o != "tempo_livre" for o in d["valem"][1:]) for d in forcadas), len(forcadas)),
        "forcadas_uniao_media_com_tempo_livre": sum(d["n_uniao"] for d in forcadas) / len(forcadas),
        "forcadas_uniao_media_so_urgentes": sum(d["n_uniao_sem_livre"] for d in forcadas) / len(forcadas),
        "forcadas_com_uniao_so_urgentes_maior_que_1": _frac(sum(d["n_uniao_sem_livre"] > 1 for d in forcadas), len(forcadas)),
        "acoes_por_frequencia": dict(sorted(Counter(d["acao"] for d in todas).items())),
        "por_regra": prioridade,
        "credito": {"forcadas": resumo_credito(cred_um), "com_escolha": resumo_credito(cred_esc),
                    "frac_abs_f_nas_forcadas": _frac(sum(abs(c["f"]) for c in cred_um), abs_total),
                    "por_regra": {r: resumo_credito([c for c in creditos if c["regra"] == r])
                                  for r in sorted({c["regra"] for c in creditos})}},
        "por_dono": {d: {"frac_forcadas": _frac(sum(x["n_cand"] == 1 for v in vidas if v["dono"] == d for x in v["decisoes"]),
                                                sum(len(v["decisoes"]) for v in vidas if v["dono"] == d)),
                         "frac_abs_f_nas_forcadas": _frac(sum(abs(c["f"]) for v in vidas if v["dono"] == d for c in v["creditos"]
                                                              if c["n_cand"] == 1),
                                                          sum(abs(c["f"]) for v in vidas if v["dono"] == d for c in v["creditos"]))}
                     for d in DONOS},
    }


def inventario() -> dict:
    """o que o A pode escolher em cada contexto: as linhas nao nulas do prior (o v11, sem o mundo; o cerebro do mundo fisico com o banheiro)"""
    from digilab.config import CONFIG_CORPO_BANHEIRO, CONFIG_MUNDO_LIGADA, ConfigBanheiro
    def acoes_por_regra(c):
        return {r: [a.value for a in ACOES_PET_HOJE + (AcaoPet.ALIVIAR,) if a in t and (any(t[a]) or a is AcaoPet.ALIVIAR)]
                for r, t in c._prior.items()}
    v11 = lobos.PoliticaLobos(CONFIG_PADRAO, gl.bancada_v11(DIAS, ORCAMENTO).cfg_lobos)
    mundo = lobos.PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CONFIG_MUNDO_LIGADA, cfg_corpo=CONFIG_CORPO_BANHEIRO,
                                cfg_banheiro=ConfigBanheiro(ligada=True))
    a_v11 = acoes_por_regra(v11)
    forcadas = {r for r, acs in a_v11.items() if len(acs) == 1}
    so_forcadas = sorted({a for r in forcadas for a in a_v11[r]} - {a for r, acs in a_v11.items() if r not in forcadas for a in acs})
    return {"acoes_pet_hoje": [a.value for a in ACOES_PET_HOJE], "v11": a_v11, "v11_regras_forcadas": sorted(forcadas),
            "v11_acoes_so_em_regras_forcadas": so_forcadas, "mundo_fisico_com_banheiro": acoes_por_regra(mundo),
            "acoes_com_alvo_no_mundo": [a.value for a in lobos.ACOES_COM_ALVO_MUNDO] + [AcaoPet.ALIVIAR.value],
            "classes_do_alvo": {a.value: list(cl) for a, cl in lobos.CLASSES_ALVO.items()},
            "regras_com_alvo": {r: [a.value for a in acs] for r, acs in lobos.REGRAS_ALVO.items()},
            "alvos_do_alivio": list(lobos.ALVOS_ALIVIO)}


def _vida_mundo(args: tuple) -> dict:
    """uma vida curta do P1-alvo no mundo fisico (a config da fumaca do piloto do MUNDO-ALVO, com as sementes dos testes): as subdecisoes"""
    dono, semente = args
    import run_v2_mundo_alvo as rma
    cfg = {**json.loads(MUNDO_ALVO.read_text(encoding="utf-8")), "dias": DIAS_MUNDO, "orcamento": 16 * DIAS_MUNDO}
    b = bv.bancada_da_config(rma.config_bancada(cfg))
    v = b.vida(bv.EspecVida(dono, "P1-alvo", semente, None, rma.MUNDO, lugar="comedouro"))
    out = []
    for m in v.motor.politica.motivos:
        al = m.get("alvo_aprendido")
        mu = m.get("mundo")
        if al is None or mu is None or "candidatos" not in mu:
            continue
        out.append({"acao": m["acao"], "n_candidatos": len(mu["candidatos"]), "classes": len(al["classes"]),
                    "fora_do_padrao": al["alvo"] is not None and al["alvo"] != al["padrao"]})
    return {"dono": dono, "semente": semente, "decisoes": out}


def analisar_mundo(vidas: list[dict]) -> dict:
    out = {}
    for acao in ("comer", "explorar", "brincar"):
        ds = [d for v in vidas for d in v["decisoes"] if d["acao"] == acao]
        if not ds:
            continue
        out[acao] = {"n": len(ds), "candidatos_medio": sum(d["n_candidatos"] for d in ds) / len(ds),
                     "classes_medio": sum(d["classes"] for d in ds) / len(ds),
                     "frac_mais_de_uma_classe": _frac(sum(d["classes"] > 1 for d in ds), len(ds)),
                     "frac_alvo_fora_do_padrao": _frac(sum(d["fora_do_padrao"] for d in ds), len(ds))}
    return out


def _vida_j5(args: tuple) -> dict:
    """uma vida do T1: os consumos da x antes e depois da mudanca, pela propria decisao e pela mao; o peso da classe comida:x (soma das
    regras do comer) e, com o planejador, o humor previsto da x, no fim de cada decisao (pelo embrulho do agir, que so le)"""
    braco, semente = args
    import run_v2_piloto_pet_que_pensa_adendo7 as p7
    cfg = {**json.loads(J5.read_text(encoding="utf-8")), **J5_DURACAO}
    bp = bv.bancada_pqp_da_config(p7.config_do_piloto(cfg))
    serie = []
    original = lobos.PoliticaLobos.agir

    def agir(self, obs, rng):
        x = getattr(self, "_v3_x", None)
        if x is not None:
            classe = sum(t[f"comida:{x}"] for k, t in self._pesos_alvo_mundo.items() if k.endswith(":comer"))
            humor = self._modelo_mundo.desfecho_de(x)["humor"] if self._modelo_mundo is not None and self._modelo_mundo.receptores else None
            serie.append((len(self.motivos), classe, humor))
        return original(self, obs, rng)
    lobos.PoliticaLobos.agir = agir
    lobos.PoliticaLobos._v3_x = bp.fruta_x(semente)
    try:
        v = bp.vida(bv.EspecPQP(braco, "T1", semente))
    finally:
        lobos.PoliticaLobos.agir = original
        del lobos.PoliticaLobos._v3_x
    tm, x = v.tick_mudanca, v.x
    k_tm = next(i for i, (k, _, _) in enumerate(serie) if k * 15 >= tm)
    xs = [c for c in v.motor.consumos_mundo if c["tipo"] == x and c["situacao"] == "madura"]
    # o sinal das decisoes depois da mudanca em que o proprio pet comeu a x (o motivo guarda o sinal pelo corpo: f dos drives, a parte do
    # humor nele e o gosto)
    sinais = []
    for k, m in enumerate(bv.do_braco(v.motor.politica).cerebro.motivos):
        mu, sc = m.get("mundo", {}), m.get("sinal_corpo")
        if k * 15 >= tm and mu.get("comeu") == x and mu.get("como") != "mao" and sc is not None:
            sinais.append({"f_drives": sc["f"], "humor": sc["drives"].get("humor", 0), "gosto": sc.get("gosto", 0)})
    return {"braco": braco, "semente": semente, "x": x, "tick_mudanca": tm,
            "x_proprio_antes": sum(c["como"] != "mao" and c["tick"] < tm for c in xs),
            "x_proprio_depois": sum(c["como"] != "mao" and c["tick"] >= tm for c in xs),
            "x_na_mao": sum(c["como"] == "mao" for c in xs),
            "classe_x_na_mudanca": serie[k_tm][1], "classe_x_no_fim": serie[-1][1],
            "humor_previsto_x_na_mudanca": serie[k_tm][2], "humor_previsto_x_no_fim": serie[-1][2],
            "sinal_x_proprio_depois": sinais}


def analisar_j5(vidas: list[dict]) -> dict:
    out = {}
    for b in J5_BRACOS:
        vs = [v for v in vidas if v["braco"] == b]
        out[b] = {"vidas": vs,
                  "x_proprio_depois_total": sum(v["x_proprio_depois"] for v in vs), "x_na_mao_total": sum(v["x_na_mao"] for v in vs),
                  "vidas_sem_x_proprio_depois": sum(v["x_proprio_depois"] == 0 for v in vs),
                  "classe_x_desceu": sum(v["classe_x_no_fim"] < v["classe_x_na_mudanca"] for v in vs),
                  "sinal_x_proprio_depois": {
                      "n": sum(len(v["sinal_x_proprio_depois"]) for v in vs),
                      "f_drives_medio": _frac(sum(s["f_drives"] for v in vs for s in v["sinal_x_proprio_depois"]),
                                              sum(len(v["sinal_x_proprio_depois"]) for v in vs)),
                      "gosto_medio": _frac(sum(s["gosto"] for v in vs for s in v["sinal_x_proprio_depois"]),
                                           sum(len(v["sinal_x_proprio_depois"]) for v in vs)),
                      "frac_total_positivo": _frac(sum(s["f_drives"] + s["gosto"] > 0 for v in vs for s in v["sinal_x_proprio_depois"]),
                                                   sum(len(v["sinal_x_proprio_depois"]) for v in vs)),
                      "frac_gosto_maior_que_perda": _frac(sum(s["gosto"] > -s["f_drives"] for v in vs for s in v["sinal_x_proprio_depois"]
                                                              if s["f_drives"] < 0),
                                                          sum(s["f_drives"] < 0 for v in vs for s in v["sinal_x_proprio_depois"]))},
                  "humor_previsto_desceu": sum(v["humor_previsto_x_no_fim"] is not None and v["humor_previsto_x_na_mudanca"] is not None
                                               and v["humor_previsto_x_no_fim"] < v["humor_previsto_x_na_mudanca"] for v in vs)}
    return out


def main() -> None:
    especs = [(d, s) for d in DONOS for s in SEMENTES]
    with ProcessPoolExecutor() as ex:
        vidas = list(ex.map(_vida, [(d, s, True) for d, s in especs]))
        puras = list(ex.map(_vida, [(d, s, False) for d, s in especs]))
        mundo = list(ex.map(_vida_mundo, especs))
        j5 = list(ex.map(_vida_j5, [(b, s) for b in J5_BRACOS for s in SEMENTES]))
    for v, p in zip(vidas, puras):
        if v["sha"] != p["sha"]:
            raise RuntimeError(f"o embrulho do credito mudou a vida {v['dono']}@{v['semente']}")
    out = {"versao": 1, "braco": gl.BRACO_V11, "dias": DIAS, "orcamento": ORCAMENTO, "donos": list(DONOS), "sementes": list(SEMENTES),
           "inventario": inventario(), "v11": analisar_v11(vidas),
           "mundo_fisico": {"config": str(MUNDO_ALVO.relative_to(RAIZ)).replace("\\", "/"), "braco": "P1-alvo", "dias": DIAS_MUNDO,
                            "subdecisoes": analisar_mundo(mundo)},
           "j5": {"config": str(J5.relative_to(RAIZ)).replace("\\", "/"), "duracao": J5_DURACAO, "protocolo": "T1",
                  "analise": analisar_j5(j5)}}
    ARQUIVO.parent.mkdir(exist_ok=True)
    ARQUIVO.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out["v11"][k] for k in ("frac_forcadas", "forcadas_com_outra_regra_urgente",
                                                 "forcadas_uniao_media_so_urgentes", "credito")}, indent=1))
    print(json.dumps(out["mundo_fisico"], indent=1))
    print(json.dumps({b: {k: x for k, x in r.items() if k != "vidas"} for b, r in out["j5"]["analise"].items()}, indent=1))


if __name__ == "__main__":
    main()
