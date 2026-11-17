"""A decomposicao da D-C1-3 na LONGE_GEOMETRIA (docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secao 8, item 3; D-LG-3): o caminho do ganho da
memoria (as parcelas F-a a F-d e P-a a P-e do adendo 10 da C1, A10.4) no `longe_fixo` e no `longe_ancora`, no M3* - M2 e no PAD - M2,
para ver se o caminho muda com a repeticao. So leitura: nenhuma vida nova, nenhuma semente, nenhuma faixa. Descritivo, sem gate: nada
aqui muda a leitura da secao 7 nem o `resultado.json` da run.

O que e igual ao descritivo da C1 (`experiments/descritivo_dc13_longe_fixo.py`, que este reusa):
  - a particao de cada episodio de fome (A10.4): F-a a F-d nos fechados, P-a a P-e nos perdidos, e o modulo que decidiu o comer;
  - D1 (a distancia na queda), D4 (o corpo na queda) e o registro das idas (agora no M3* e no PAD);
  - o estagio 1, so do `medidas.json` (D3, D5, D6, D7 e a conta do H4), por lugar e por contraste.
O que muda:
  - os lugares e os contrastes: (`longe_fixo`, `longe_ancora`) x (M3* - M2, PAD - M2), os niveis dos 4 bracos ao lado;
  - o D2 (a distancia ao ponto fixo mais proximo) so no `longe_fixo`: no `longe_ancora` cada racao cai num ponto novo;
  - a parte do ganho (`s`) so onde o ganho G do lugar e positivo (no `longe_ancora` ele fica perto de 0 ou abaixo);
  - a decomposicao da interacao: como G = soma das F (e = - soma das P) em cada lugar, o I (G no `longe_fixo` - G no `longe_ancora`,
    pareado por unidade) se reparte parcela a parcela. A soma das parcelas tem de fechar no I-M3 e no I-PAD do `resultado.json`.

Duas conferencias falham alto, antes de qualquer medida: o codigo (os sha256 do `meta.json` da run, conferidos ANTES de importar o
pacote, na worktree de `--codigo`) e o G1 de cada vida (o log rejogado igual ao do disco; as medidas refeitas iguais as do `medidas.json`,
menos o `custo`; os lugares das racoes refeitos do motor iguais aos gravados). Roda uma vez: a saida ja existente falha alto.

    git worktree add --detach <pasta> 58a22928
    python experiments/descritivo_dc13_longe_geometria.py --codigo <pasta> --processos 4
grava artifacts_v3_longe_geometria/dc13/descritivo.json
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))
import descritivo_dc13_longe_fixo as c1d  # noqa: E402  (so a biblioteca padrao no topo; nao importa o pacote digilab)

RUN = RAIZ / "artifacts_v3_longe_geometria" / "run"
SAIDA = RAIZ / "artifacts_v3_longe_geometria" / "dc13" / "descritivo.json"
COMMIT_DA_RUN = "58a229283dd63e9db66206fd23f151031850006c"
SHA_FONTES = {                                   # os do meta.json e os do RESULTADO_V3_LONGE_GEOMETRIA.md, secao 1
    "meta.json": "6ddaa2a1ac201b40aea7f3a9c819166a08097710d5e9da0f76800435fcb130f4",
    "resultado.json": "6760525f935512c6ae930358a1d4205880aa1483ef1b9527a4bb7b6c5e3cbc96",
    "medidas.json.gz": "ff379334b683059051fb0aaa16b360976b736b478520007ffb7c27e237143d08",
    "vidas.tar.gz": "471941bb928178d7eb1eab9ea2fcdd2013ba5301a090d263e97d85c9d19ae669",
}
SHA_MEDIDAS = "63a0c1b3a280e06bc628a37183ff17363831dff7a4718672e394761bfeae5f1c"   # o medidas.json descomprimido (meta.json)
LUGARES = ("longe_fixo", "longe_ancora")
CONTRASTES = (("M3", "M2"), ("PAD", "M2"))
BRACOS = ("PAD", "M3", "M2", "M0")
COM_IDAS = ("PAD", "M3")
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
ROTULO = ("descritivo da secao 8, item 3, do plano da LONGE_GEOMETRIA (a decomposicao da D-C1-3 do adendo 10 da C1, A10.4): so leitura, "
          "sem vida nova e sem semente; sem gate e sem regra de leitura; nada aqui muda a secao 7")
MAX_PROCESSOS = 4                                                    # V3-D8
PARTES_F, PARTES_P, GRUPOS = c1d.PARTES_F, c1d.PARTES_P, c1d.GRUPOS
BUSCA, COMER_COMIDA, IDA, MOTIVO_P = c1d.BUSCA, c1d.COMER_COMIDA, c1d.IDA, c1d.MOTIVO_P
_CACHE: dict = {}


# ================================================================== o codigo: conferido antes de importar
def conferir_codigo(codigo: Path, meta: dict) -> dict:
    """os sha256 dos modulos de `digilab/` do meta.json, do orquestrador, do prototipo, da C1, da C4 e da config em `codigo` sao os da run;
    falha alto se nao, sem importar nada do pacote"""
    codigo = Path(codigo)
    pares = [(f"digilab/{rel}", sha) for rel, sha in sorted(meta["sha256"].items())]
    pares += [("experiments/run_v3_longe_geometria.py", meta["orquestrador_sha256"]),
              ("experiments/run_v2_digibrain_prototipo.py", meta["prototipo_sha256"]),
              ("experiments/run_v2_longe_regular.py", meta["c1_sha256"]),
              ("experiments/run_v2_memoria_autobio.py", meta["c4_sha256"]),
              (meta["config_arquivo"], meta["config_sha256"])]
    diffs = [rel for rel, sha in pares if not (codigo / rel).is_file() or c1d._sha(codigo / rel) != sha]
    if diffs:
        raise RuntimeError(f"o codigo de {codigo} nao e o da run (o meta.json, git_head {meta['git_head']}): {diffs}")
    return {"arquivos": len(pares), "iguais_ao_meta": True, "sha256": {rel: sha for rel, sha in pares}}


def carregar(codigo: Path) -> SimpleNamespace:
    """importa o pacote e o orquestrador da run da pasta `codigo` (e so dela); falha alto se o import vem de outra pasta"""
    codigo = Path(codigo).resolve()
    chave = str(codigo)
    if chave in _CACHE:
        return _CACHE[chave]
    for p in (str(codigo), str(codigo / "experiments")):
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    import run_v3_longe_geometria as lg
    import run_v2_digibrain_prototipo as orq
    import run_v2_longe_regular as lr
    import digilab.metrics as met
    from digilab.config import CONFIG_PADRAO
    for mod in (lg, orq, lr, met):
        if codigo not in Path(mod.__file__).resolve().parents:
            raise RuntimeError(f"{mod.__name__} veio de {mod.__file__}, e nao de {codigo}")
    _CACHE[chave] = SimpleNamespace(lg=lg, orq=orq, lr=lr, met=met, CONFIG_PADRAO=CONFIG_PADRAO)
    return _CACHE[chave]


# ================================================================== o replay de uma vida
def _lugares_do_motor(ns, motor) -> dict:
    """a conferencia da construcao refeita das racoes que o dono deixou no motor (o `lugares_da_vida` da run le o dono)"""
    cm, lg = ns.orq.CM, ns.lg
    cx, cy = lg.centro_da_celula(cm.layout.comedouro, cm)
    racoes = [d for d in motor.deixadas if d["tipo"] == "racao"]
    por_dir: dict = {}
    hist: dict = {}
    for d in racoes:
        k = str(ns.lg.direcao_do_comedouro(d["x"], d["y"]))
        por_dir[k] = por_dir.get(k, 0) + 1
        c = str(lg.distancia(d["x"] - cx, d["y"] - cy) // cm.sub)
        hist[c] = hist.get(c, 0) + 1
    return {"racoes": len(racoes), "distintos": len({(d["x"], d["y"]) for d in racoes}),
            "por_direcao": dict(sorted(por_dir.items(), key=lambda kv: int(kv[0]))),
            "distancia_celulas": dict(sorted(hist.items(), key=lambda kv: int(kv[0])))}


def rejogar(tarefa: tuple) -> dict:
    """uma vida: o replay do log, o G1 e as medidas de A10.4 (so desta vida; a soma e os contrastes ficam no principal)"""
    codigo, gravada, arquivo, dias, orcamento = tarefa
    ns = carregar(codigo)
    lg, orq, lr = ns.lg, ns.orq, ns.lr
    braco, dono, lugar, semente = gravada["braco"], gravada["dono"], gravada["lugar"], gravada["semente"]
    texto = Path(arquivo).read_text(encoding="utf-8")
    fp, _ = orq.fabricas(lg.BRACO_DO_ORQ[braco], dono, semente, dias, orcamento, conserto=True)
    cc = orq.bancada(dias, orcamento).cfg_corpo_de(lg.bv.EspecVida(dono, lg.gl.BRACO_V11, semente))

    def fm(politica, cfg, s):                                           # a mesma do `viver` da run
        return lr.MotorGravaCorpo(politica, cfg, s, lg.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise lg.bv.ReplayDivergiu(f"{arquivo}: o log rejogado nao e o do disco")
    registro = motor.politica
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(lg.BRACO_DO_ORQ[braco], registro, None)
    refeita = {"vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": gravada["base"],
               "k": gravada["k"], **orq.medidas(motor, registro, lg.BRACO_DO_ORQ[braco], dias, True),
               "corpo": lr.medidas_do_corpo(motor, registro, dias), "metas": lr.trocas_de_meta(registro),
               "lugares": _lugares_do_motor(ns, motor)}
    sem_custo = {k: v for k, v in gravada.items() if k != "custo"}
    if json.dumps(refeita, sort_keys=True) != json.dumps(sem_custo, sort_keys=True):
        raise RuntimeError(f"G1 do descritivo: a vida {gravada['vida']} nao refaz as medidas gravadas")
    out = _medir(ns, motor, registro, gravada, braco, dono, lugar, semente)
    out["log_sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return out


def _medir(ns, motor, registro, gravada: dict, braco: str, dono: str, lugar: str, semente: int) -> dict:
    """a particao de A10.4, D1, D2 e D4 e as idas; e o `_medir` da C1 com duas mudancas: os pontos fixos so no `longe_fixo` (no
    `longe_ancora` cada racao cai num ponto novo) e as idas no M3* e no PAD"""
    import bisect
    orq, met = ns.orq, ns.met
    isqrt = math.isqrt
    g = orq.geometria()
    cm = orq.CM
    raio_visao, corte = g["raio_visao"], g["corte_d0"]
    passo = ns.CONFIG_PADRAO.intervalo_decisao_ticks
    entrada = motor.entrada_mundo
    ms = orq.cerebro_de(registro).motivos
    dm = motor.decisoes_mundo
    n = len(ms)
    if len(dm) != n or any(d["tick"] - entrada != k * passo for k, d in enumerate(dm)):
        raise RuntimeError(f"{gravada['vida']}: as decisoes do mundo nao sao as do cerebro, no tick k x {passo}")
    pos = [tuple(d["antes"]) for d in dm]
    maduro, idade_max = cm.maduro_racao_min, cm.maduro_racao_min + cm.prazo_podre_min
    k_comida = {c["id"]: (c["tick"] - entrada) // passo for c in motor.consumos_mundo}
    racoes = {d["id"]: d for d in sorted((d for d in motor.deixadas if d["tipo"] == "racao"), key=lambda d: (d["tick"], d["id"]))}
    t0s = [d["tick"] - entrada for d in racoes.values()]
    lista = list(racoes.values())
    pontos = ns.lg.dono_do_lugar(dono, lugar, semente).pontos_fixos if lugar == "longe_fixo" else ()
    if lugar == "longe_fixo" and (not pontos or {(d["x"], d["y"]) for d in lista} - set(pontos)):
        raise RuntimeError(f"{gravada['vida']}: uma queda de racao fora dos pontos fixos")

    def dist(k: int, d: dict) -> int:
        return c1d._distancia(isqrt, pos[k][0], pos[k][1], d["x"], d["y"])

    def no_chao(k: int, prazo: int) -> list:
        t = k * passo
        i = bisect.bisect_left(t0s, t - prazo + 1)
        j = bisect.bisect_right(t0s, t)
        return [d for d in lista[i:j] if orq._no_chao(d["tick"] - entrada, k_comida.get(d["id"]), k, passo, prazo)]

    def visivel(k: int, d: dict) -> bool:
        return orq._no_chao(d["tick"] - entrada, k_comida.get(d["id"]), k, passo, idade_max) and dist(k, d) <= raio_visao

    consumo_em = {(c["tick"] - entrada) // passo: c["id"] for c in motor.consumos_mundo if c["id"] in racoes}
    episodios = gravada["episodios_fome"]["episodios"]
    F = {p: 0 for p in PARTES_F}
    P = {p: 0 for p in PARTES_P}
    F_grupo = {p: {x: 0 for x in GRUPOS} for p in PARTES_F}
    combos: dict = {}
    diag = {"fa_alvo_fora_da_vista": 0, "visivel_em_k0_imatura": 0, "fechou_sem_entrada_na_vista": 0, "p_sem_racao_visivel": 0}
    rotulos = []
    for k_i, d0, _w, fim, motivo in episodios:
        of = {d["id"]: dist(k_i, d) for d in no_chao(k_i, maduro)}
        if not of or min(of.values()) != d0:
            raise RuntimeError(f"{gravada['vida']}: a oferta da abertura {k_i} nao da o d0 gravado")
        if motivo == "fechou":
            alvo = consumo_em.get(fim)
            if alvo is None:
                raise RuntimeError(f"{gravada['vida']}: o episodio fechado em {fim} sem a racao comida")
            d_alvo = racoes[alvo]
            if d0 <= raio_visao:
                parte = "F-a"
                diag["fa_alvo_fora_da_vista"] += not visivel(k_i, d_alvo)
            else:
                k_e = next((k for k in range(k_i, fim + 1) if visivel(k, d_alvo)), None)
                if k_e is None:
                    parte = "F-d"
                    diag["fechou_sem_entrada_na_vista"] += 1
                elif k_e == k_i:
                    parte = "F-d"
                    diag["visivel_em_k0_imatura"] += 1
                else:
                    ec = ms[k_e - 1]["escolha"][:2]
                    parte = "F-b" if ec == IDA else ("F-c" if ec == BUSCA else "F-d")
            k_dir = next((k for k in range(k_i, fim + 1) if ms[k]["escolha"][:2] == COMER_COMIDA and ms[k]["escolha"][2] == alvo), None)
            if k_dir is None:
                grupo, combo = "sem_comer_dirigida", ()
            else:
                s = ms[k_dir]["sondas"]
                combo = tuple(sorted(m for m in orq.MODULOS_SONDA + ("aprendido",) if s[f"{m}_decidiu"]))
                grupo = c1d._grupo(combo)
            F[parte] += 1
            F_grupo[parte][grupo] += 1
            chave = f"{parte}|{'+'.join(combo) if combo else ('inato' if k_dir is not None else 'sem_comer_dirigida')}"
            combos[chave] = combos.get(chave, 0) + 1
            rotulos.append((k_i, parte))
        else:
            alvo = min(of, key=lambda i: (of[i], i))
            d_alvo = racoes[alvo]
            k_e = next((k for k in range(k_i, fim + 1) if visivel(k, d_alvo)), None)
            diag["p_sem_racao_visivel"] += k_e is None
            antes_da_vista = range(k_i, fim + 1 if k_e is None else k_e)
            if any(ms[k]["acao"] == "dormir" for k in antes_da_vista):
                parte = "P-a"
            elif any(f["motivo"] == "trocou" and f["chave"][:2] in (BUSCA, COMER_COMIDA)
                     for k in range(k_i, fim + 1) if ms[k]["reflexo"] for f in ms[k]["fins"]):
                parte = "P-b"
            else:
                parte = MOTIVO_P[motivo]
            P[parte] += 1
            rotulos.append((k_i, parte))
    ne = len(episodios)
    if len({k for k, _ in rotulos}) != ne or sum(F.values()) + sum(P.values()) != ne:
        raise RuntimeError(f"{gravada['vida']}: a particao nao cobre cada episodio uma vez so")
    if sum(F.values()) != gravada["episodios_fome"]["fechados"]:
        raise RuntimeError(f"{gravada['vida']}: as parcelas F nao somam os episodios fechados")
    for k in range(n - 1):
        if tuple(dm[k + 1]["antes"]) != (dm[k]["x"], dm[k]["y"]):
            raise RuntimeError(f"{gravada['vida']}: o pet andou entre as decisoes {k} e {k + 1}")
    d1, d4 = [], []
    serie = motor.serie_corpo
    nomes = ("fome", "higiene", "energia", "humor", "saude")
    for d in lista:
        t0 = d["tick"] - entrada
        k0 = -(-t0 // passo)
        if k0 >= n or t0 >= len(serie):
            continue
        d1.append(dist(k0, d))
        d4.append([met._escala01(nome, v) for nome, v in zip(nomes, serie[t0][1:])])
    comedouro = motor.mundo.comedouro
    sub = cm.sub
    dc = [c1d._distancia(isqrt, x, y, comedouro[0], comedouro[1]) for x, y in pos]
    d2 = {"dist_comedouro_celulas": statistics.fmean(dc) / sub}
    if pontos:
        dp = [min(c1d._distancia(isqrt, x, y, px, py) for px, py in pontos) for x, y in pos]
        d2.update({"dist_ponto_celulas": statistics.fmean(dp) / sub, "frac_na_visao": sum(1 for x in dp if x < raio_visao) / n,
                   "frac_no_cheiro": sum(1 for x in dp if x < corte) / n})
    return {
        "vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": gravada["base"],
        "n": ne, "F": F, "P": P, "F_grupo": F_grupo, "combos": combos, "diag": diag, "ofertas": len(lista),
        "D1": statistics.fmean(d1) / sub if d1 else None,
        "D4": None if not d4 else {"menor": statistics.fmean(min(e) for e in d4),
                                   **{nome: statistics.fmean(e[i] for e in d4) for i, nome in enumerate(nomes)}},
        "D2": d2,
        "idas": c1d._idas(ns, ms, serie, pos, lista, visivel, k_comida, passo, dono) if braco in COM_IDAS else None,
    }


# ================================================================== as contas
class Contas:
    """as contas de um lugar e de um contraste (a - b), sobre os registros de vida (as medidas da run e o `dc13` do estagio 2)"""

    def __init__(self, ns, registros: list[dict], lugar: str, a: str, b: str, g_esperado: float | None) -> None:
        self.orq, self.lr = ns.orq, ns.lr
        self.regs = registros
        self.a, self.b = a, b
        self.celulas = tuple((d, lugar) for d in DONOS)
        self.G_difs = self.dif(self.lr.EPISODIO)
        self.G = self.lr.estimativa(self.G_difs)["media"]
        if g_esperado is not None and abs(self.G - g_esperado) > 1e-12:
            raise RuntimeError(f"o G de {lugar}, {a} - {b} ({self.G!r}) nao e o da escada do resultado.json ({g_esperado!r})")

    def dif(self, medida, a: str | None = None, b: str | None = None) -> dict:
        return self.orq.por_unidade(self.regs, a or self.a, b or self.b, medida, self.celulas)

    def nivel(self, medida, braco: str) -> dict:
        return self.orq.por_unidade(self.regs, braco, None, medida, self.celulas)

    def est(self, difs: dict) -> dict:
        e = self.lr.estimativa(difs)
        e["s"] = e["media"] / self.G if e["media"] is not None and self.G > 0 else None   # a parte do ganho, so com G > 0
        return e

    def bloco(self, medida, sinal: bool = False) -> dict:
        out = {"contraste": self.est(self.dif(medida)), "niveis": {br: self.lr.estimativa(self.nivel(medida, br)) for br in BRACOS}}
        if sinal:
            out["contraste"]["classe_sinal"] = c1d._classe_sinal(out["contraste"])
        return out


def estagio1(c: Contas) -> dict:
    """D3, D5, D6, D7 e a conta do H4, so do `medidas.json` (o estagio 1 da C1, por lugar e por contraste)"""
    s1 = c1d.estagio1(_Adaptador(c))
    return s1


class _Adaptador:
    """deixa as funcoes da C1 (que esperam o bloco 'M3-M2') lerem uma Contas daqui"""

    def __init__(self, c: Contas) -> None:
        self.c = c
        self.G = c.G
        self.regs = c.regs
        self.lr = c.lr

    def bloco(self, medida, sinal: bool = False) -> dict:
        b = self.c.bloco(medida, sinal)
        return {"M3-M2": b["contraste"], "niveis": b["niveis"]}


def estagio2(c: Contas) -> dict:
    A = {p: c.bloco(lambda r, p=p: c1d._fracao(r, "F", p)) for p in PARTES_F}
    A_grupo = {p: {g: c.bloco(lambda r, p=p, g=g: c1d._frac_grupo(r, p, (g,))) for g in GRUPOS} for p in PARTES_F}
    B = {p: c.bloco(lambda r, p=p: c1d._fracao(r, "P", p)) for p in PARTES_P}
    soma_f = c1d._soma([c.dif(lambda r, p=p: c1d._fracao(r, "F", p)) for p in PARTES_F])
    soma_p = c1d._soma([c.dif(lambda r, p=p: c1d._fracao(r, "P", p)) for p in PARTES_P])
    for nome, soma, sinal in (("F", soma_f, 1), ("P", soma_p, -1)):
        for u, v in c.G_difs.items():
            if abs(sinal * soma[u] - v) > 1e-12:
                raise RuntimeError(f"a soma das parcelas {nome} nao fecha no ganho da unidade {u}: {sinal * soma[u]!r} e {v!r}")
    fecha = {"F": c.est(soma_f)["media"], "P": -c.est(soma_p)["media"], "G": c.G}
    h = {
        "H1": c.est(c.dif(lambda r: c1d._fracao(r, "F", "F-a"))),
        "H1'": c.est(c.dif(lambda r: c1d._fracao(r, "F", "F-b"))),
        "H2": c.est(c1d._soma([c.dif(lambda r, p=p: c1d._frac_grupo(r, p, ("inato", "aprendido_habito"))) for p in ("F-c", "F-d")])),
        "H3": c.est(c1d._soma([c.dif(lambda r, p=p: c1d._fracao(r, "P", p)) for p in ("P-a", "P-b")], -1)),
        "F-d_sem_modulo": c.est(c.dif(lambda r: c1d._frac_grupo(r, "F-d", ("sem_comer_dirigida",)))),
    }
    D1 = c.bloco(lambda r: r["dc13"]["D1"], sinal=True)
    D4 = {nome: c.bloco(lambda r, nome=nome: None if r["dc13"]["D4"] is None else r["dc13"]["D4"][nome], sinal=True)
          for nome in ("menor", "fome", "higiene", "energia", "humor", "saude")}
    chaves_d2 = sorted(c.regs[0]["dc13"]["D2"]) if c.regs else []
    D2 = {nome: c.bloco(lambda r, nome=nome: r["dc13"]["D2"][nome], sinal=nome.startswith("dist")) for nome in chaves_d2}
    return {"A": A, "A_por_modulo": A_grupo, "B": B, "soma_das_parcelas": fecha, "somas_por_hipotese_da_c1": h, "D1": D1, "D2": D2,
            "D4": D4}


def cobertura(registros: list[dict]) -> dict:
    out = {}
    for lugar in LUGARES:
        for b in BRACOS:
            rs = [r for r in registros if r["braco"] == b and r["lugar"] == lugar]
            s = {"vidas": len(rs), "episodios": sum(r["dc13"]["n"] for r in rs),
                 "F": {p: sum(r["dc13"]["F"][p] for r in rs) for p in PARTES_F},
                 "P": {p: sum(r["dc13"]["P"][p] for r in rs) for p in PARTES_P},
                 "fechados_nas_medidas": sum(r["episodios_fome"]["fechados"] for r in rs),
                 "diag": {k: sum(r["dc13"]["diag"][k] for r in rs) for k in rs[0]["dc13"]["diag"]} if rs else {},
                 "ofertas_de_racao": sum(r["dc13"]["ofertas"] for r in rs)}
            if sum(s["F"].values()) + sum(s["P"].values()) != s["episodios"] or sum(s["F"].values()) != s["fechados_nas_medidas"]:
                raise RuntimeError(f"{lugar}, {b}: a particao nao cobre cada episodio uma vez so")
            acc: dict = {}
            for r in rs:
                for k, v in r["dc13"]["combos"].items():
                    acc[k] = acc.get(k, 0) + v
            s["combos"] = dict(sorted(acc.items()))
            out[f"{lugar}|{b}"] = s
    return out


def idas(registros: list[dict]) -> dict:
    """o registro das visitas por braco e por lugar, como na C1: sem contraste e sem leitura (o `_resumo_idas` da C1 so le o braco
    "M3", entao cada braco passa por ele com esse rotulo; o rotulo de saida dele diz "so o M3*", e aqui vale para o braco da chave)"""
    out = {}
    for b in COM_IDAS:
        for lugar in LUGARES:
            regs = [r for r in registros if r["braco"] == b and r["lugar"] == lugar]
            out[f"{lugar}|{b}"] = c1d._resumo_idas([{**r, "braco": "M3"} for r in regs])
    return out


def interacao(ns, registros: list[dict], a: str, b: str, i_esperado: float | None) -> dict:
    """a decomposicao do I (a - b no `longe_fixo` menos o mesmo no `longe_ancora`, pareado por unidade) pelas parcelas F e P; as somas
    tem de fechar no I do `resultado.json`"""
    orq, lr = ns.orq, ns.lr

    def i_de(medida) -> dict:
        g1 = orq.por_unidade(registros, a, b, medida, tuple((d, "longe_fixo") for d in DONOS))
        g2 = orq.por_unidade(registros, a, b, medida, tuple((d, "longe_ancora") for d in DONOS))
        return {u: g1[u] - g2[u] for u in sorted(set(g1) & set(g2))}

    I_difs = i_de(lr.EPISODIO)
    I = lr.estimativa(I_difs)["media"]
    if i_esperado is not None and abs(I - i_esperado) > 1e-12:
        raise RuntimeError(f"o I de {a} - {b} ({I!r}) nao e o primario do resultado.json ({i_esperado!r})")

    def est(difs: dict) -> dict:
        e = lr.estimativa(difs)
        e["s"] = e["media"] / I if e["media"] is not None and I > 0 else None
        return e

    partes_f = {p: i_de(lambda r, p=p: c1d._fracao(r, "F", p)) for p in PARTES_F}
    partes_p = {p: i_de(lambda r, p=p: c1d._fracao(r, "P", p)) for p in PARTES_P}
    soma_f, soma_p = c1d._soma(list(partes_f.values())), c1d._soma(list(partes_p.values()))
    for nome, soma, sinal in (("F", soma_f, 1), ("P", soma_p, -1)):
        for u, v in I_difs.items():
            if abs(sinal * soma[u] - v) > 1e-12:
                raise RuntimeError(f"a soma das parcelas {nome} nao fecha no I da unidade {u}")
    grupos = {p: {g: est(i_de(lambda r, p=p, g=g: c1d._frac_grupo(r, p, (g,)))) for g in GRUPOS} for p in PARTES_F}
    return {"I": I, "n": len(I_difs), "F": {p: est(d) for p, d in partes_f.items()}, "P": {p: est(d) for p, d in partes_p.items()},
            "F_por_modulo": grupos, "fecha": {"F": lr.estimativa(soma_f)["media"], "P": -lr.estimativa(soma_p)["media"], "I": I}}


# ================================================================== o principal
def ler_fontes() -> dict:
    sha = {}
    for nome, esperado in SHA_FONTES.items():
        s = c1d._sha(RUN / nome)
        if s != esperado:
            raise RuntimeError(f"{nome} nao e o da run (sha256 {s})")
        sha[nome] = s
    return sha


def ler_medidas(caminho: Path) -> dict:
    bruto = gzip.decompress(caminho.read_bytes())
    if hashlib.sha256(bruto).hexdigest() != SHA_MEDIDAS:
        raise RuntimeError("o medidas.json descomprimido nao e o do meta.json")
    return json.loads(bruto.decode("utf-8"))


def extrair_logs(tar: Path, vidas: list[dict], pasta: Path) -> dict:
    por_nome = {f"vidas/{v['braco']}/{v['dono']}_{v['lugar']}_{v['semente']}.jsonl": v["vida"] for v in vidas}
    out = {}
    with tarfile.open(tar, "r:gz") as t:
        for m in t:
            if m.name in por_nome and m.isfile():
                destino = pasta / f"{m.name.split('/')[1]}_{Path(m.name).name}"
                destino.write_bytes(t.extractfile(m).read())
                out[por_nome[m.name]] = destino
    if len(out) != len(vidas):
        raise FileNotFoundError(f"{len(vidas) - len(out)} logs faltam no {tar}")
    return out


def principal(codigo: Path, meta: dict, medidas: dict, tar: Path, saida: Path, processos: int, fontes: dict, resultado: dict | None,
              filtro=None) -> dict:
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe: o descritivo roda uma vez")
    if processos > MAX_PROCESSOS:
        raise SystemExit(f"ate {MAX_PROCESSOS} processos (V3-D8)")
    alvo = sorted((v for v in medidas.values() if v["lugar"] in LUGARES and v["braco"] in BRACOS and (filtro is None or filtro(v))),
                  key=lambda v: v["vida"])
    codigo_ok = conferir_codigo(codigo, meta)                           # 1a conferencia: antes de importar uma linha do pacote
    ns = carregar(codigo)
    cfg = meta["config"]
    esc = None if resultado is None else resultado["descritivo"]["escada_do_ganho"]
    prim = None if resultado is None else resultado["primarios"]
    out = {"rotulo": ROTULO, "plano": "docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secao 8, item 3 (D-LG-3)", "fontes_sha256": fontes,
           "script": {"arquivo": "experiments/descritivo_dc13_longe_geometria.py", "sha256": c1d._sha(Path(__file__)),
                      "reusa": {"arquivo": "experiments/descritivo_dc13_longe_fixo.py", "sha256": c1d._sha(Path(c1d.__file__))}},
           "commit_da_run": meta["git_head"], "codigo": codigo_ok, "vidas": len(alvo),
           "unidades": len({(v["base"], v["semente"]) for v in alvo})}
    with tempfile.TemporaryDirectory() as tmp:
        logs = extrair_logs(tar, alvo, Path(tmp))
        tarefas = [(str(codigo), v, str(logs[v["vida"]]), cfg["dias"], cfg["orcamento_por_dia"]) for v in alvo]
        if processos <= 1:
            saidas = [rejogar(t) for t in tarefas]
        else:
            with ProcessPoolExecutor(max_workers=processos) as pool:
                saidas = list(pool.map(rejogar, tarefas, chunksize=8))
    por_vida = {s["vida"]: s for s in saidas}
    registros = [{**v, "dc13": por_vida[v["vida"]]} for v in alvo]
    blocos = {}
    for lugar in LUGARES:
        for a, b in CONTRASTES:
            g_esp = None if esc is None else esc[a][lugar]["media"]
            c = Contas(ns, registros, lugar, a, b, g_esp)
            blocos[f"{lugar}|{a}-{b}"] = {"G": c.G, "estagio1": estagio1(c), "estagio2": estagio2(c)}
    nomes_i = {"M3": "I-M3", "PAD": "I-PAD"}
    inter = {f"{a}-{b}": interacao(ns, registros, a, b, None if prim is None else prim[nomes_i[a]]["media"]) for a, b in CONTRASTES}
    logs_sha = {s["vida"]: s["log_sha256"] for s in saidas}
    out.update({"g1": {"vidas_refeitas": len(saidas), "todas_iguais": True},
                "logs_sha256_do_conjunto": hashlib.sha256("".join(logs_sha[k] for k in sorted(logs_sha)).encode()).hexdigest(),
                "por_lugar_e_contraste": blocos, "interacao": inter, "cobertura": cobertura(registros), "idas": idas(registros),
                "nao_demonstra": ["uma causa: as parcelas sao descritivas (A10.6 da C1)", "a separacao do lado e da ancora (secao 10)",
                                  "nada que mude a leitura da secao 7"]})
    return out


def gravar(caminho: Path, dados: dict) -> str:
    texto = json.dumps(dados, sort_keys=True, indent=1, ensure_ascii=False) + "\n"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--codigo", type=Path, required=True, help="a worktree destacada do 58a22928")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--fumaca", type=Path, default=None,
                    help="so as 2 primeiras unidades de cada base, gravado neste caminho (fora do artifacts), sem as conferencias do G e do I")
    a = ap.parse_args()
    fontes = ler_fontes()
    meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
    if meta["git_head"] != COMMIT_DA_RUN:
        raise RuntimeError("o meta.json nao e o da run (58a22928)")
    medidas = ler_medidas(RUN / "medidas.json.gz")
    resultado = json.loads((RUN / "resultado.json").read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    if a.fumaca is not None:
        if RAIZ / "artifacts_v3_longe_geometria" in a.fumaca.resolve().parents:
            raise SystemExit("a fumaca grava fora do artifacts_v3_longe_geometria/")
        d = principal(a.codigo.resolve(), meta, medidas, RUN / "vidas.tar.gz", a.fumaca, a.processos, fontes, None,
                      filtro=lambda v: v["k"] < 2)
        d["rotulo"] += " [FUMACA: so 2 unidades por base; nao e resultado]"
        destino = a.fumaca
    else:
        d = principal(a.codigo.resolve(), meta, medidas, RUN / "vidas.tar.gz", SAIDA, a.processos, fontes, resultado)
        destino = SAIDA
    d["git_head_do_script"] = _git("rev-parse", "HEAD")
    sha = gravar(destino, d)
    print(f"gravado {destino} (sha256 {sha}) em {time.perf_counter() - t0:.0f} s; {d['vidas']} vidas")
