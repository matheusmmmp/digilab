"""O descritivo da D-C1-3 (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 10, A10.8; APROVADO pelo Matheus em 2026-11-06):
de onde vem o ganho do M3* sobre o M2 na taxa de fechamento por episodio de fome do `longe_fixo`. So leitura: nenhuma vida nova, nenhuma
semente, nenhuma faixa. O motor, o `engine.py`, o corpo, os cerebros e as medidas por vida da C1 nao mudam.

Os dois estagios (A10.2):
  1. so le o `medidas.json` da C1 (D3, D5, D6, D7 e o H4);
  2. refaz no replay as vidas do `longe_fixo` (M2, M3* e M0, 1 800 vidas) a partir dos logs da C1 (`vidas.tar.gz`), com o codigo do
     `7683c0e` (uma worktree destacada, `--codigo`): a particao de A10.4 (F-a a F-d, P-a a P-e), D1, D2, D4 e o registro das visitas.

Duas conferencias falham alto, antes de qualquer medida: o codigo (os sha256 dos 15 modulos de `digilab/`, do orquestrador, do prototipo e
da config iguais aos do `meta.json`, conferidos ANTES de importar uma linha do pacote) e o G1 de cada vida (as medidas refeitas no replay
iguais as do `medidas.json`, menos o `custo`; o log rejogado igual ao do disco). A soma das parcelas tem de fechar no primario do
`resultado.json`, ou falha alto. A leitura segue a regra de A10.5, escrita antes. Roda uma vez (AD10-7): a saida ja existente falha alto.

Este arquivo nao importa o pacote `digilab` por conta propria: o pacote e o das fontes, da worktree de `--codigo`.

    git worktree add --detach <pasta> 7683c0e
    python experiments/descritivo_dc13_longe_fixo.py --codigo <pasta> --processos 4
grava artifacts_v2_digibrain_prototipo/longe_regular/dc13/descritivo.json
"""
from __future__ import annotations

import argparse
import bisect
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
PASTA_C1 = RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular"
RUN = PASTA_C1 / "run"
SAIDA = PASTA_C1 / "dc13" / "descritivo.json"
COMMIT_DA_RUN = "7683c0e1f83a9526421208b4a23d90cd476148ff"
# os sha256 das fontes (A10.2), conferidos nesta tarefa com o sha256sum e iguais ao `meta.json` e a secao 13 do RESULTADO
SHA_FONTES = {                          # o comeco e o fim do sha256 (A10.2) ou ele inteiro (o do meta.json da run e o da secao 13)
    "meta.json": "b2cb111a…4770",
    "medidas.json": "5a4fb207eaa11750ba40ffc80da1879febd822a5305545356fb091b664a4722d",
    "resultado.json": "b18727455922c2fb3047694e1228620ab136014796a68c008c20cac014a21209",
    "vidas.tar.gz": "a1fb0010…f7ee",
}
ESTILO = "longe_fixo"
BRACOS = ("M2", "M3", "M0")             # o contraste M3* - M2; o M0 ao lado, so como nivel (AD10-3)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
ROTULO = ("descritivo da D-C1-3 (adendo 10, A10.8): so leitura, sem vida nova e sem semente; pos hoc, descritivo e gerador de hipotese "
          "(A10.6)")
MAX_PROCESSOS = 4                                                    # V3-D8
FRACAO_MAIOR_PARTE = 0.5                                             # A10.5, PROPOSTO, SEM FONTE
PARTES_F = ("F-a", "F-b", "F-c", "F-d")
PARTES_P = ("P-a", "P-b", "P-c", "P-d", "P-e")
GRUPOS = ("inato", "aprendido_habito", "memoria", "outro", "sem_comer_dirigida")
BUSCA, COMER_COMIDA, IDA = ["comer", "cheiro"], ["comer", "comida"], ["explorar", "ponto"]
MOTIVO_P = {"janela_vencida": "P-c", "saciado_por_outra_comida": "P-d", "vida_acabou": "P-e"}
_CACHE: dict = {}


# ================================================================== o codigo (A10.2): conferido antes de importar
def _sha(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def conferir_codigo(codigo: Path, meta: dict) -> dict:
    """os sha256 dos 15 modulos de `digilab/`, do orquestrador, do prototipo e da config em `codigo` sao os do `meta.json` da run;
    falha alto se nao, sem importar nada do pacote"""
    codigo = Path(codigo)
    pares = [(f"digilab/{rel}", sha) for rel, sha in sorted(meta["sha256"].items())]
    pares += [("experiments/run_v2_longe_regular.py", meta["orquestrador_sha256"]),
              ("experiments/run_v2_digibrain_prototipo.py", meta["prototipo_sha256"]),
              (meta["config_arquivo"], meta["config_sha256"])]
    diffs = []
    for rel, sha in pares:
        arq = codigo / rel
        if not arq.is_file() or _sha(arq) != sha:
            diffs.append(rel)
    if diffs:
        raise RuntimeError(f"o codigo de {codigo} nao e o da run (o meta.json, git_head {meta['git_head']}): {diffs}")
    return {"arquivos": len(pares), "iguais_ao_meta": True, "sha256": {rel: sha for rel, sha in pares}}


def carregar(codigo: Path) -> SimpleNamespace:
    """importa o pacote e o orquestrador da C1 da pasta `codigo` (e so dela); falha alto se o import vem de outra pasta"""
    codigo = Path(codigo).resolve()
    chave = str(codigo)
    if chave in _CACHE:
        return _CACHE[chave]
    for p in (str(codigo), str(codigo / "experiments")):
        if p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    import run_v2_digibrain_prototipo as orq
    import run_v2_longe_regular as lr
    import digilab.metrics as met
    for mod in (orq, lr, met):
        if codigo not in Path(mod.__file__).resolve().parents:
            raise RuntimeError(f"{mod.__name__} veio de {mod.__file__}, e nao de {codigo}")
    _CACHE[chave] = SimpleNamespace(orq=orq, lr=lr, met=met)
    return _CACHE[chave]


# ================================================================== o replay de uma vida (estagio 2)
def _distancia(isqrt, ax: int, ay: int, bx: int, by: int) -> int:
    return isqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by))


def _grupo(combo: tuple) -> str:
    """o modulo (ou os modulos) que decidiu(ram) a decisao: o grupo exclusivo de A10.4, 'nenhum' e o inato"""
    if not combo:
        return "inato"
    if "memoria" in combo:
        return "memoria"
    if set(combo) <= {"aprendido", "habito"}:
        return "aprendido_habito"
    return "outro"


def rejogar(tarefa: tuple) -> dict:
    """uma vida: o replay do log, o G1 e as medidas de A10.4 (so desta vida; a soma e o contraste ficam no principal)"""
    codigo, gravada, arquivo, dias, orcamento = tarefa
    ns = carregar(codigo)
    lr, orq, met = ns.lr, ns.orq, ns.met
    braco, dono, lugar, semente = gravada["braco"], gravada["dono"], gravada["lugar"], gravada["semente"]
    texto = Path(arquivo).read_text(encoding="utf-8")
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento, conserto=True)
    cc = orq.bancada(dias, orcamento).cfg_corpo_de(lr.bv.EspecVida(dono, lr.gl.BRACO_V11, semente))

    def fm(politica, cfg, s):                                           # a mesma do `viver` da C1
        return lr.MotorGravaCorpo(politica, cfg, s, lr.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise orq.bv.ReplayDivergiu(f"{arquivo}: o log rejogado nao e o do disco")
    registro = motor.politica
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    refeita = {"vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": gravada["base"],
               "k": gravada["k"], **orq.medidas(motor, registro, braco, dias, True),
               "corpo": lr.medidas_do_corpo(motor, registro, dias), "metas": lr.trocas_de_meta(registro)}
    sem_custo = {k: v for k, v in gravada.items() if k != "custo"}
    if json.dumps(refeita, sort_keys=True) != json.dumps(sem_custo, sort_keys=True):
        raise RuntimeError(f"G1 do descritivo: a vida {gravada['vida']} nao refaz as medidas gravadas")
    out = _medir(ns, motor, registro, gravada, braco, dono, lugar, semente)
    out["log_sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return out


def _medir(ns, motor, registro, gravada: dict, braco: str, dono: str, lugar: str, semente: int) -> dict:
    orq, met = ns.orq, ns.met
    isqrt = math.isqrt
    g = orq.geometria()
    cm = orq.CM
    raio_visao, corte = g["raio_visao"], g["corte_d0"]
    passo = orq.CONFIG_PADRAO.intervalo_decisao_ticks
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
    pontos = orq.DonoComLugar(orq.criar_dono(dono), lugar, semente, dono, cm).pontos_fixos
    if not pontos or {(d["x"], d["y"]) for d in lista} - set(pontos):
        raise RuntimeError(f"{gravada['vida']}: uma queda de racao fora dos pontos fixos (A6.2)")

    def dist(k: int, d: dict) -> int:
        return _distancia(isqrt, pos[k][0], pos[k][1], d["x"], d["y"])

    def no_chao(k: int, prazo: int) -> list:
        """as racoes no chao na decisao k com menos de `prazo` ticks (o `_no_chao` do orquestrador)"""
        t = k * passo
        i = bisect.bisect_left(t0s, t - prazo + 1)
        j = bisect.bisect_right(t0s, t)
        return [d for d in lista[i:j] if orq._no_chao(d["tick"] - entrada, k_comida.get(d["id"]), k, passo, prazo)]

    def visivel(k: int, d: dict) -> bool:
        return orq._no_chao(d["tick"] - entrada, k_comida.get(d["id"]), k, passo, idade_max) and dist(k, d) <= raio_visao

    consumo_em = {}
    for c in motor.consumos_mundo:
        if c["id"] in racoes:
            consumo_em[(c["tick"] - entrada) // passo] = c["id"]
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
                    ec = ms[k_e - 1]["escolha"][:2]                      # a escolha em curso na decisao que levou a vista
                    parte = "F-b" if ec == IDA else ("F-c" if ec == BUSCA else "F-d")
            k_dir = next((k for k in range(k_i, fim + 1) if ms[k]["escolha"][:2] == COMER_COMIDA and ms[k]["escolha"][2] == alvo), None)
            if k_dir is None:
                grupo, combo = "sem_comer_dirigida", ()
            else:
                s = ms[k_dir]["sondas"]
                combo = tuple(sorted(m for m in orq.MODULOS_SONDA + ("aprendido",) if s[f"{m}_decidiu"]))
                grupo = _grupo(combo)
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

    # D1, D4: a queda de cada racao do dono. O pet so anda no tick da decisao (conferido: antes[k + 1] = (x, y) de k), entao a
    # posicao no tick da queda t0 e a da decisao k0 = teto(t0 / passo).
    for k in range(n - 1):
        if tuple(dm[k + 1]["antes"]) != (dm[k]["x"], dm[k]["y"]):
            raise RuntimeError(f"{gravada['vida']}: o pet andou entre as decisoes {k} e {k + 1}")
    d1, d4 = [], []
    serie = motor.serie_corpo
    for d in lista:
        t0 = d["tick"] - entrada
        k0 = -(-t0 // passo)
        if k0 >= n or t0 >= len(serie):
            continue
        d1.append(dist(k0, d))
        d4.append([met._escala01(nome, v) for nome, v in zip(("fome", "higiene", "energia", "humor", "saude"), serie[t0][1:])])
    # D2: a distancia ao ponto fixo mais proximo em cada decisao (e ao comedouro, ao lado, sem leitura)
    comedouro = motor.mundo.comedouro
    dp = [min(_distancia(isqrt, x, y, px, py) for px, py in pontos) for x, y in pos]
    dc = [_distancia(isqrt, x, y, comedouro[0], comedouro[1]) for x, y in pos]
    sub = cm.sub
    d2 = {"dist_ponto_celulas": statistics.fmean(dp) / sub, "dist_comedouro_celulas": statistics.fmean(dc) / sub,
          "frac_na_visao": sum(1 for x in dp if x < raio_visao) / n, "frac_no_cheiro": sum(1 for x in dp if x < corte) / n}
    return {
        "vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": gravada["base"],
        "n": ne, "F": F, "P": P, "F_grupo": F_grupo, "combos": combos, "diag": diag, "ofertas": len(lista),
        "D1": statistics.fmean(d1) / sub if d1 else None,
        "D4": None if not d4 else {"menor": statistics.fmean(min(e) for e in d4),
                                   **{nome: statistics.fmean(e[i] for e in d4)
                                      for i, nome in enumerate(("fome", "higiene", "energia", "humor", "saude"))}},
        "D2": d2,
        "idas": _idas(ns, ms, serie, pos, lista, visivel, k_comida, passo, dono) if braco == "M3" else None,
    }


def _idas(ns, ms: list, serie: list, pos: list, lista: list, visivel, k_comida: dict, passo: int, dono: str) -> list:
    """o registro de cada visita (A10.4, D; a espec, secao 5): so no M3*. A ida acaba no fim da intencao explorar/ponto."""
    met = ns.met
    n = len(ms)

    def menor(t: int) -> float:
        return min(met._escala01(nome, v) for nome, v in zip(("fome", "higiene", "energia", "humor", "saude"), serie[t][1:]))

    def classes(k: int) -> str:
        if k >= n:
            return "fim_da_vida"
        tipos = sorted({d["tipo"] for d in lista if visivel(k, d)})
        return "+".join(tipos) if tipos else "nenhuma"

    out = []
    for k, m in enumerate(ms):
        for f in m["fins"]:
            if f["chave"][:2] != IDA:
                continue
            ini = f["inicio"]
            entrou = [d for d in lista if not visivel(ini, d) and any(visivel(kk, d) for kk in range(ini + 1, k + 1))]
            comidas = [d for d in entrou if k_comida.get(d["id"]) is not None and k_comida[d["id"]] >= k]
            out.append({"dono": dono, "decisoes": f["n"], "motivo": f["motivo"], "custo": menor(min(k * passo, len(serie) - 1))
                        - menor(ini * passo), "classes_chegada": classes(k), "classes_seguinte": classes(k + 1),
                        "racao_entrou": len(entrou) > 0, "racao_entrou_e_comida_depois": len(comidas) > 0})
    return out


# ================================================================== as contas (estagio 1 e soma do estagio 2)
def _fracao(r: dict, bloco: str, parte: str):
    return None if not r["dc13"]["n"] else r["dc13"][bloco][parte] / r["dc13"]["n"]


def _frac_grupo(r: dict, parte: str, grupos: tuple):
    return None if not r["dc13"]["n"] else sum(r["dc13"]["F_grupo"][parte][g] for g in grupos) / r["dc13"]["n"]


def _classe_sinal(est: dict) -> str:
    """D1, D2 e D4 estao em celulas: sem margem de '~ 0'; a classe sai so pelo sinal (A10.4)"""
    lo, hi = est["ic95"]["ic_inferior"], est["ic95"]["ic_superior"]
    if lo is None:
        return "indeterminado"
    return "> 0" if lo > 0 else ("< 0" if hi < 0 else "indeterminado")


def _soma(partes: list[dict], sinal: int = 1) -> dict:
    """a soma (ou a soma negada) por unidade de varias diferencas por unidade"""
    chaves = set(partes[0])
    if any(set(p) != chaves for p in partes):
        raise RuntimeError("as parcelas nao tem as mesmas unidades")
    return {k: sinal * sum(p[k] for p in partes) for k in sorted(chaves)}


class Contas:
    """as contas do descritivo sobre uma lista de registros de vida (cada um com as medidas da C1 e o `dc13` do estagio 2, quando ha)"""

    def __init__(self, ns, registros: list[dict], donos: tuple, g_esperado: float | None) -> None:
        self.orq, self.lr = ns.orq, ns.lr
        self.regs = registros
        self.celulas = tuple((d, ESTILO) for d in donos)
        self.G_difs = self.dif(self.lr.EPISODIO)
        self.G = self.lr.estimativa(self.G_difs)["media"]
        if g_esperado is not None and abs(self.G - g_esperado) > 1e-12:
            raise RuntimeError(f"o G recalculado do medidas.json ({self.G!r}) nao e o primario do resultado.json ({g_esperado!r})")
        if not self.G > 0:
            raise RuntimeError(f"G = {self.G!r}: a decomposicao pede um ganho positivo")

    def dif(self, medida, a: str = "M3", b: str = "M2") -> dict:
        return self.orq.por_unidade(self.regs, a, b, medida, self.celulas)

    def nivel(self, medida, braco: str) -> dict:
        return self.orq.por_unidade(self.regs, braco, None, medida, self.celulas)

    def est(self, difs: dict) -> dict:
        e = self.lr.estimativa(difs)
        e["s"] = e["media"] / self.G if e["media"] is not None else None
        return e

    def bloco(self, medida, sinal: bool = False) -> dict:
        """o contraste M3* - M2, e os tres niveis ao lado"""
        out = {"M3-M2": self.est(self.dif(medida)),
               "niveis": {b: self.lr.estimativa(self.nivel(medida, b)) for b in BRACOS}}
        if sinal:
            out["M3-M2"]["classe_sinal"] = _classe_sinal(out["M3-M2"])
        return out


def estagio1(c: Contas) -> dict:
    """D3, D5, D6, D7 e a conta do H4: so o `medidas.json` (A10.2, estagio 1)"""
    def ofertas(r):
        return r["cadeia_w"]["elegiveis"]

    def por_oferta(f):
        return lambda r: None if not ofertas(r) else f(r) / ofertas(r)

    d3 = {"visiveis_em_k0": c.bloco(por_oferta(lambda r: r["racao_na_janela"]["visiveis_em_k0"])),
          "entraram_na_visao": c.bloco(por_oferta(lambda r: r["racao_na_janela"]["entraram_na_visao"]))}
    d5 = {nome: c.bloco(por_oferta(f)) for nome, f in (
        ("achou", lambda r: r["metas"]["fins"]["busca"]["achou"]), ("sumiu", lambda r: r["metas"]["fins"]["busca"]["sumiu"]),
        ("desistiu", lambda r: r["metas"]["fins"]["busca"]["desistiu"]),
        ("trocou", lambda r: r["metas"]["fins"]["busca"]["trocou"]),
        ("trocou_pelo_reflexo", lambda r: r["metas"]["trocas"]["busca"]["reflexo"]),
        ("trocou_pelo_dormir_sorteado", lambda r: r["metas"]["trocas"]["busca"]["dormir_sorteio"]),
        ("trocou_por_outra_unidade", lambda r: r["metas"]["trocas"]["busca"]["outra_unidade"]))}
    d6 = {"refeicoes_por_dia": c.bloco(lambda r: r["cadeia"]["refeicoes_por_dia"]),
          "ofertas_elegiveis_por_vida": c.bloco(ofertas),
          "episodios_por_vida": c.bloco(lambda r: r["episodios_fome"]["n"]),
          "taxa_por_racao": c.bloco(lambda r: r["cadeia"]["taxa"]),
          "taxa_por_episodio": c.bloco(c.lr.EPISODIO)}
    d7 = {m: c.bloco(lambda r, m=m: r["influencia_vida"][m]) for m in sorted(c.regs[0]["influencia_vida"])}
    classes = (d6["refeicoes_por_dia"]["M3-M2"]["classe"]["classe"], d6["taxa_por_racao"]["M3-M2"]["classe"]["classe"])
    h4 = {"refeicoes_por_dia": classes[0], "taxa_por_racao": classes[1], "cumpre": all(x in ("≈ 0", "< 0") for x in classes),
          "nota": "a margem delta = 0,022 vale, como em A10.4, tambem para as refeicoes por dia (a letra de A10.4)"}
    return {"G": c.G, "D3": d3, "D5": d5, "D6": d6, "D7": d7, "H4": h4}


def estagio2(c: Contas) -> dict:
    A = {p: c.bloco(lambda r, p=p: _fracao(r, "F", p)) for p in PARTES_F}
    A_grupo = {p: {g: c.bloco(lambda r, p=p, g=g: _frac_grupo(r, p, (g,))) for g in GRUPOS} for p in PARTES_F}
    B = {p: c.bloco(lambda r, p=p: _fracao(r, "P", p)) for p in PARTES_P}
    soma_f = _soma([c.dif(lambda r, p=p: _fracao(r, "F", p)) for p in PARTES_F])
    soma_p = _soma([c.dif(lambda r, p=p: _fracao(r, "P", p)) for p in PARTES_P])
    for nome, soma, sinal in (("F", soma_f, 1), ("P", soma_p, -1)):
        for u, v in c.G_difs.items():
            if abs(sinal * soma[u] - v) > 1e-12:
                raise RuntimeError(f"a soma das parcelas {nome} nao fecha no ganho da unidade {u}: {sinal * soma[u]!r} e {v!r}")
    fecha = {"F": c.est(soma_f)["media"], "P": -c.est(soma_p)["media"], "G": c.G}
    if abs(fecha["F"] - c.G) > 1e-12 or abs(fecha["P"] - c.G) > 1e-12:
        raise RuntimeError(f"as somas das parcelas nao fecham em G: {fecha}")
    # o que cada hipotese soma (A10.5)
    h = {
        "H1": c.est(c.dif(lambda r: _fracao(r, "F", "F-a"))),
        "H1'": c.est(c.dif(lambda r: _fracao(r, "F", "F-b"))),
        "H2": c.est(_soma([c.dif(lambda r, p=p: _frac_grupo(r, p, ("inato", "aprendido_habito"))) for p in ("F-c", "F-d")])),
        "H3": c.est(_soma([c.dif(lambda r, p=p: _fracao(r, "P", p)) for p in ("P-a", "P-b")], -1)),
        "F-d_sem_modulo": c.est(c.dif(lambda r: _frac_grupo(r, "F-d", ("sem_comer_dirigida",)))),
    }
    D1, D4 = c.bloco(lambda r: r["dc13"]["D1"], sinal=True), {}
    for nome in ("menor", "fome", "higiene", "energia", "humor", "saude"):
        D4[nome] = c.bloco(lambda r, nome=nome: None if r["dc13"]["D4"] is None else r["dc13"]["D4"][nome], sinal=True)
    D2 = {nome: c.bloco(lambda r, nome=nome: r["dc13"]["D2"][nome], sinal=nome.startswith("dist")) for nome in
          ("dist_ponto_celulas", "dist_comedouro_celulas", "frac_na_visao", "frac_no_cheiro")}
    cobertura = {}
    for b in BRACOS:
        rs = [r for r in c.regs if r["braco"] == b]
        cobertura[b] = {"vidas": len(rs), "episodios": sum(r["dc13"]["n"] for r in rs),
                        "F": {p: sum(r["dc13"]["F"][p] for r in rs) for p in PARTES_F},
                        "P": {p: sum(r["dc13"]["P"][p] for r in rs) for p in PARTES_P},
                        "fechados_nas_medidas": sum(r["episodios_fome"]["fechados"] for r in rs),
                        "diag": {k: sum(r["dc13"]["diag"][k] for r in rs) for k in rs[0]["dc13"]["diag"]},
                        "ofertas_de_racao": sum(r["dc13"]["ofertas"] for r in rs)}
        s = cobertura[b]
        if sum(s["F"].values()) + sum(s["P"].values()) != s["episodios"] or sum(s["F"].values()) != s["fechados_nas_medidas"]:
            raise RuntimeError(f"{b}: a particao nao cobre cada episodio uma vez so")
    combos = {}
    for b in BRACOS:
        acc: dict = {}
        for r in c.regs:
            if r["braco"] == b:
                for k, v in r["dc13"]["combos"].items():
                    acc[k] = acc.get(k, 0) + v
        combos[b] = dict(sorted(acc.items()))
    return {"A": A, "A_por_modulo": A_grupo, "B": B, "soma_das_parcelas": fecha, "hipoteses": h, "D1": D1, "D2": D2, "D4": D4,
            "cobertura": cobertura, "combos_por_braco": combos, "idas": _resumo_idas(c.regs)}


def _resumo_idas(registros: list[dict]) -> dict:
    """o registro das visitas (A10.4, D): so o M3*, so por braco e por estilo do dono, sem contraste e sem leitura"""
    idas = [i for r in registros if r["braco"] == "M3" for i in r["dc13"]["idas"]]

    def resumo(xs: list) -> dict:
        if not xs:
            return {"idas": 0}
        cont = lambda k: dict(sorted({v: sum(1 for i in xs if i[k] == v) for v in {i[k] for i in xs}}.items()))   # noqa: E731
        return {"idas": len(xs), "decisoes_media": statistics.fmean(i["decisoes"] for i in xs),
                "decisoes_mediana": statistics.median(i["decisoes"] for i in xs), "fins": cont("motivo"),
                "custo_media": statistics.fmean(i["custo"] for i in xs), "custo_mediana": statistics.median(i["custo"] for i in xs),
                "classes_chegada": cont("classes_chegada"), "classes_seguinte": cont("classes_seguinte"),
                "frac_racao_entrou_na_vista": sum(1 for i in xs if i["racao_entrou"]) / len(xs),
                "frac_racao_entrou_e_comida_depois": sum(1 for i in xs if i["racao_entrou_e_comida_depois"]) / len(xs)}
    return {"todas": resumo(idas), "por_dono": {d: resumo([i for i in idas if i["dono"] == d]) for d in sorted({i["dono"] for i in idas})},
            "rotulo": "so o M3*, so por braco: a LP-2, sem contraste e sem leitura"}


# ================================================================== a regra de leitura (A10.5)
def _explica(est: dict) -> bool:
    return est["classe"]["classe"] == "> 0" and est["s"] is not None and est["s"] >= FRACAO_MAIOR_PARTE


def _contribui(est: dict) -> bool:
    lo = est["ic95"]["ic_inferior"]
    return lo is not None and lo > 0


def ler(s1: dict, s2: dict) -> dict:
    """a regra de A10.5, na ordem, como esta. Os termos: 'explica a maior parte' (a soma das parcelas tem a classe '> 0' e s >= 1/2) e
    'contribui' (o limite inferior do IC acima de 0). H1 pede D1 '< 0'; H1' pede D1 sem o limite superior abaixo de 0; H2 pede D1 nao '< 0'."""
    h, d1 = s2["hipoteses"], s2["D1"]["M3-M2"]
    d1_neg = d1["classe_sinal"] == "< 0"
    d1_nao_neg = d1["ic95"]["ic_superior"] is not None and not d1["ic95"]["ic_superior"] < 0
    elegiveis = {"H1": d1_neg, "H1'": d1_nao_neg, "H2": not d1_neg, "H3": True}
    explicam = sorted(k for k in elegiveis if elegiveis[k] and _explica(h[k]))
    contribuem = sorted(k for k in elegiveis if elegiveis[k] and _contribui(h[k]))
    partes = {k: {"s": h[k]["s"], "media": h[k]["media"], "ic95": h[k]["ic95"], "classe": h[k]["classe"]["classe"],
                  "condicao_extra_cumprida": elegiveis[k]} for k in elegiveis}
    out = {"explicam_a_maior_parte": explicam, "contribuem": contribuem, "partes": partes,
           "D1_classe_sinal": d1["classe_sinal"], "H1_sem_D1": _explica(h["H1"]) and not d1_neg,
           "substituicao": _explica(h["H1'"]) and s2["A"]["F-c"]["M3-M2"]["classe"]["classe"] == "< 0"}
    if s1["H4"]["cumpre"]:
        out["linha"] = "o ganho e da medida: o M3* nao come mais, ele muda os episodios; as outras linhas nao se leem"
    elif len(explicam) == 1:
        out["linha"] = f"aponta para {explicam[0]}, como leitura descritiva (A10.6)"
    elif "H3" in explicam and ("H1" in explicam or "H1'" in explicam):
        out["linha"] = "mistura de posicao e custo: registrada sem escolher"
    elif len(explicam) >= 2:
        out["linha"] = f"mistura ({', '.join(explicam)} explicam ao mesmo tempo): registrada com as partes, sem escolher"
        out["lacuna_da_regra"] = "A10.5 so prescreve as misturas H1 e H3 (ou H1' e H3); esta e tratada como mistura, sem escolher"
    elif len(contribuem) >= 2:
        out["linha"] = f"mistura ({', '.join(contribuem)} contribuem): registrada com as partes, sem escolher"
    else:
        sem_mod = h["F-d_sem_modulo"]
        out["linha"] = "indeterminado: o caminho nao e nenhum dos previstos; nenhuma hipotese nova se testa nos mesmos dados"
        out["F-d_sem_modulo_explica_a_maior_parte"] = _explica(sem_mod)
        if len(contribuem) == 1:
            out["lacuna_da_regra"] = ("uma so hipotese contribui e nenhuma explica a maior parte: A10.5 nao tem essa linha; fica "
                                      "'indeterminado', com a parte registrada")
    if out["substituicao"]:
        out["linha"] += ". Substituicao: F-b explica e F-c fica '< 0'; nao se le H1' como ganho liquido da patrulha"
    return out


# ================================================================== o principal
def ler_fontes() -> dict:
    sha = {}
    for nome, esperado in SHA_FONTES.items():
        s = _sha(RUN / nome)
        ini, _, fim = esperado.partition("…")
        if not (s == esperado if not fim else s.startswith(ini) and s.endswith(fim)):
            raise RuntimeError(f"{nome} nao e o da C1 (sha256 {s})")
        sha[nome] = s
    return sha


def extrair_logs(tar: Path, vidas: list[dict], pasta: Path) -> dict:
    """extrai do tar so os logs pedidos (nada mais), em `pasta`; devolve {vida: arquivo}"""
    por_nome = {f"vidas/{v['braco']}/{v['dono']}_{v['lugar']}_{v['semente']}.jsonl": v["vida"] for v in vidas}
    out = {}
    with tarfile.open(tar, "r:gz") as t:
        for m in t:
            if m.name in por_nome and m.isfile():
                destino = pasta / f"{m.name.split('/')[1]}_{Path(m.name).name}"
                destino.write_bytes(t.extractfile(m).read())
                out[por_nome[m.name]] = destino
    if len(out) != len(vidas):
        raise FileNotFoundError(f"{len(vidas) - len(out)} logs da C1 faltam no {tar}")
    return out


def principal(codigo: Path, meta: dict, medidas: dict, tar: Path, saida: Path, processos: int, fontes: dict, resultado: dict | None,
              donos: tuple = DONOS, so_estagio1: bool = False) -> dict:
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe: o descritivo roda uma vez (AD10-7)")
    if processos > MAX_PROCESSOS:
        raise SystemExit(f"ate {MAX_PROCESSOS} processos (V3-D8)")
    g_esperado = None if resultado is None else resultado["primario"]["media"]
    alvo = sorted((v for v in medidas.values() if v["lugar"] == ESTILO and v["braco"] in BRACOS and v["dono"] in donos),
                  key=lambda v: v["vida"])
    codigo_ok = conferir_codigo(codigo, meta)                           # 1a conferencia: antes de importar uma linha do pacote
    ns0 = carregar(codigo)
    cfg = meta["config"]
    c1 = Contas(ns0, alvo, donos, g_esperado)
    s1 = estagio1(c1)
    out = {"rotulo": ROTULO, "plano": "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 10 (A10.1 a A10.9)",
           "fontes_sha256": fontes, "script": {"arquivo": "experiments/descritivo_dc13_longe_fixo.py", "sha256": _sha(Path(__file__))},
           "commit_da_run": meta["git_head"], "codigo": codigo_ok, "unidades": len({(v["base"], v["semente"]) for v in alvo}),
           "vidas": len(alvo), "estagio1": s1}
    if so_estagio1:
        out["rotulo"] += " [PARCIAL: so o estagio 1; nenhuma leitura]"
        out["leitura"] = {"linha": "nenhuma leitura: so o estagio 1, rotulado como parcial (A10.5)"}
        return out
    with tempfile.TemporaryDirectory() as tmp:
        logs = extrair_logs(tar, alvo, Path(tmp))
        tarefas = [(str(codigo), v, str(logs[v["vida"]]), cfg["dias"], cfg["orcamento_por_dia"]) for v in alvo]
        if processos <= 1:
            saidas = [rejogar(t) for t in tarefas]
        else:
            with ProcessPoolExecutor(max_workers=processos) as pool:
                saidas = list(pool.map(rejogar, tarefas))
    por_vida = {s["vida"]: s for s in saidas}
    registros = [{**v, "dc13": por_vida[v["vida"]]} for v in alvo]
    c2 = Contas(ns0, registros, donos, g_esperado)
    s2 = estagio2(c2)
    logs_sha = {s["vida"]: s["log_sha256"] for s in saidas}
    out.update({"g1": {"vidas_refeitas": len(saidas), "todas_iguais": True},
                "logs_sha256_do_conjunto": hashlib.sha256("".join(logs_sha[k] for k in sorted(logs_sha)).encode()).hexdigest(),
                "estagio2": s2, "leitura": ler(s1, s2)})
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
    ap.add_argument("--codigo", type=Path, required=True, help="a worktree destacada do 7683c0e")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--so-estagio1", action="store_true", help="so o estagio 1, rotulado como parcial (se o estagio 2 nao vale)")
    a = ap.parse_args()
    fontes = ler_fontes()
    meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
    if meta["git_head"] != COMMIT_DA_RUN:
        raise RuntimeError("o meta.json nao e o da C1 (7683c0e)")
    medidas = json.loads((RUN / "medidas.json").read_text(encoding="utf-8"))
    resultado = json.loads((RUN / "resultado.json").read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    d = principal(a.codigo.resolve(), meta, medidas, RUN / "vidas.tar.gz", SAIDA, a.processos, fontes, resultado,
                  so_estagio1=a.so_estagio1)
    d["git_head_do_script"] = _git("rev-parse", "HEAD")
    destino = SAIDA.with_name("descritivo_parcial.json") if a.so_estagio1 else SAIDA
    sha = gravar(destino, d)
    print(f"gravado {destino.relative_to(RAIZ)} (sha256 {sha}) em {time.perf_counter() - t0:.0f} s; a leitura: {d['leitura']['linha']}")
