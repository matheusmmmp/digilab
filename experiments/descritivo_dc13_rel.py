"""O descritivo da D-C1-3 no cerebro padrao (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 11, A11.8; APROVADO pelo Matheus em
2026-11-06): de onde vem o ganho do REL sobre o SEM na taxa de fechamento por episodio de fome do `longe_fixo`. So leitura: nenhuma vida
nova, nenhuma semente, nenhuma faixa. O motor, o `engine.py`, o corpo, os cerebros e as medidas por vida da C4 nao mudam. Este arquivo
REUSA o `descritivo_dc13_longe_fixo.py` (a C1) por import, sem mudar aquele arquivo nem o `descritivo.json` dele (AD11-7).

Os dois estagios (A11.2):
  1. so le o `medidas.json` da C4 (D3, D6, D7, a lembranca e o H4);
  2. refaz no replay as vidas do `longe_fixo` do REL e do SEM (1 600 vidas, AD11-3) a partir dos logs da C4 (`vidas.tar.gz`), com o
     codigo do `a287ba2` (uma worktree destacada, `--codigo`): a particao de A10.4 (F-a a F-d, P-a a P-e) com os grupos de A11.4, D1, D2,
     D4, D5 e o registro das visitas do REL (com o alvo da ida e o episodio que a visita codificou).

Tres conferencias falham alto, antes de qualquer medida (A11.2): o codigo (os sha256 dos 18 modulos, dos 4 orquestradores e da config iguais
aos do `meta.json`, conferidos ANTES de importar uma linha do pacote), a fonte (o `medidas.json` descomprimido com o sha256 do `meta.json`)
e o G1 de cada vida (as medidas refeitas no replay, com o coletor das categorias e dos episodios, iguais as do `medidas.json`, menos o
`custo`; o log rejogado igual ao do disco). A soma das parcelas fecha no primario do `resultado.json`, ou falha alto. A leitura segue a
regra de A10.5 com as mudancas de A11.5. Roda uma vez (AD11-7): a saida ja existente falha alto.

Este arquivo nao importa o pacote `digilab` por conta propria: o pacote e o das fontes, da worktree de `--codigo`.

    git worktree add --detach <pasta> a287ba2
    python experiments/descritivo_dc13_rel.py --codigo <pasta> --processos 4
grava artifacts_v2_digibrain_prototipo/memoria_autobio/dc13/descritivo_rel.json
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import statistics
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import descritivo_dc13_longe_fixo as dc  # noqa: E402  (so reuso: o arquivo da C1 nao muda)

RAIZ = dc.RAIZ
PASTA_C4 = RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio"
RUN = PASTA_C4 / "run"
SAIDA = PASTA_C4 / "dc13" / "descritivo_rel.json"
DESCRITIVO_C1 = RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "dc13" / "descritivo.json"
COMMIT_DA_RUN = "a287ba20fafdc1fbbf9be7100f89d9c90f466948"
SHA_MEDIDAS = "869ff3971b91e6d848f3f9e16d1798049105442bde1968a6852daa852c153023"      # o medidas.json descomprimido (A11.2, meta.json)
# os sha256 das fontes (A11.2), conferidos nesta tarefa com o sha256sum; o comeco e o fim, ou ele inteiro
SHA_FONTES = {
    "meta.json": "6315784c…3a18",
    "medidas.json.gz": "8b48d0a2…d93b",
    "resultado.json": "6f8c91d8e2b857194de1de00145a4da817efca76eb882bcd2d090dd3101cd6d3",
    "vidas.tar.gz": "aa0c3987…0aed",
}
SHA_C1 = "28db9e82…3798"                                                   # o descritivo.json da C1 (13.6), so lido
ESTILO = "longe_fixo"
BRACOS = ("REL", "SEM")                                                    # o contraste REL - SEM (AD11-3)
DONOS = dc.DONOS
ROTULO = ("descritivo da D-C1-3 no REL (adendo 11, A11.8): so leitura, sem vida nova e sem semente; pos hoc, descritivo e gerador de "
          "hipotese (A11.6)")
PARTES_F, PARTES_P = dc.PARTES_F, dc.PARTES_P
GRUPOS = ("lembranca", "memoria_lugar", "aprendido_habito", "inato", "outro", "sem_comer_dirigida")      # A11.4, exclusivos e nesta ordem
VIDAS_ESPERADAS = 1600                                                     # 200 unidades x 4 donos x 2 bracos (AD11-3)
HIPOTESES = ("H1", "H1'", "H2", "H3", "H5")
MODULOS_LEMBRANCA = ("lembranca",)                                         # a sonda a mais, que o `MODULOS_SONDA` da C4 nao tem
CAMPOS_ESTAGIO1 = (("cadeia", "refeicoes_por_dia"), ("cadeia", "taxa"), ("cadeia_w", "elegiveis"), ("racao_na_janela", "elegiveis"),
                   ("racao_na_janela", "visiveis_em_k0"), ("racao_na_janela", "entraram_na_visao"), ("episodios_fome", "episodios"),
                   ("episodios_fome", "n"), ("episodios_fome", "fechados"), ("memoria", "com_lembranca"), ("memoria", "decidiu_vida"),
                   ("visitas_lugar_lembrado",), ("visitas_vazias",), ("influencia_vida",), ("fins_conferidos",), ("fins",))
_CACHE: dict = {}


# ================================================================== o codigo e a fonte (A11.2): conferidos antes de medir
def conferir_codigo(codigo: Path, meta: dict) -> dict:
    """os sha256 dos 18 modulos (16 de `digilab/` e 2 de `digilab_fala_livre/`), dos 4 orquestradores e da config em `codigo` sao os do
    `meta.json` da run; falha alto se nao, sem importar nada do pacote"""
    codigo = Path(codigo)
    pares = [(rel if rel.startswith("digilab_fala_livre/") else f"digilab/{rel}", sha) for rel, sha in sorted(meta["sha256"].items())]
    pares += [("experiments/run_v2_memoria_autobio.py", meta["orquestrador_sha256"]),
              ("experiments/run_v2_longe_regular.py", meta["longe_regular_sha256"]),
              ("experiments/run_v2_habito_intencao.py", meta["habito_intencao_sha256"]),
              ("experiments/run_v2_digibrain_prototipo.py", meta["prototipo_sha256"]),
              (meta["config_arquivo"], meta["config_sha256"])]
    diffs = [rel for rel, sha in pares if not (codigo / rel).is_file() or dc._sha(codigo / rel) != sha]
    if diffs:
        raise RuntimeError(f"o codigo de {codigo} nao e o da run (o meta.json, git_head {meta['git_head']}): {diffs}")
    return {"arquivos": len(pares), "iguais_ao_meta": True, "sha256": {rel: sha for rel, sha in pares}}


def carregar_medidas(caminho_gz: Path, meta: dict) -> tuple[dict, str]:
    """o `medidas.json` descomprimido, com o sha256 do `meta.json` (a fonte, A11.2); falha alto se for outro"""
    texto = gzip.decompress(Path(caminho_gz).read_bytes())
    sha = hashlib.sha256(texto).hexdigest()
    esperado = meta["artefatos_sha256"]["medidas.json"]
    if sha != esperado:
        raise RuntimeError(f"o medidas.json descomprimido (sha256 {sha}) nao e o do meta.json ({esperado})")
    return json.loads(texto), sha


def _confere_sha(nome: str, s: str, esperado: str) -> None:
    ini, _, fim = esperado.partition("…")
    if not (s == esperado if not fim else s.startswith(ini) and s.endswith(fim)):
        raise RuntimeError(f"{nome} nao e o da C4 (sha256 {s})")


def ler_fontes() -> dict:
    sha = {}
    for nome, esperado in SHA_FONTES.items():
        sha[nome] = dc._sha(RUN / nome)
        _confere_sha(nome, sha[nome], esperado)
    sha["descritivo_c1.json"] = dc._sha(DESCRITIVO_C1)
    _confere_sha("descritivo.json da C1", sha["descritivo_c1.json"], SHA_C1)
    return sha


def carregar(codigo: Path) -> SimpleNamespace:
    """o pacote e os orquestradores da C1 e da C4, so da pasta `codigo`; falha alto se um import vem de outra pasta"""
    codigo = Path(codigo).resolve()
    chave = str(codigo)
    if chave not in _CACHE:
        base = dc.carregar(codigo)
        import run_v2_memoria_autobio as ma
        import digilab_fala_livre.fatos as fatos
        for mod in (ma, fatos):
            if codigo not in Path(mod.__file__).resolve().parents:
                raise RuntimeError(f"{mod.__name__} veio de {mod.__file__}, e nao de {codigo}")
        _CACHE[chave] = SimpleNamespace(orq=base.orq, lr=base.lr, met=base.met, ma=ma)
    return _CACHE[chave]


class _OrqComLembranca:
    """o prototipo visto pela `dc._medir`: igual, mas a `MODULOS_SONDA` ganha a sonda `lembranca` (A11.4), para o grupo "lembranca" """

    def __init__(self, orq) -> None:
        self._orq = orq
        self.MODULOS_SONDA = tuple(orq.MODULOS_SONDA) + MODULOS_LEMBRANCA

    def __getattr__(self, nome):
        return getattr(self._orq, nome)


# ================================================================== o replay de uma vida (estagio 2)
def _grupo(combo: tuple) -> str:
    """o grupo exclusivo de A11.4, na ordem: 'lembranca', 'memoria (lugar)', 'aprendido e habito', 'inato' (nenhuma sonda), 'outro'"""
    if not combo:
        return "inato"
    if "lembranca" in combo:
        return "lembranca"
    if "memoria" in combo:
        return "memoria_lugar"
    if set(combo) <= {"aprendido", "habito"}:
        return "aprendido_habito"
    return "outro"


def regrupar(combos: dict) -> dict:
    """{parte: {grupo: n}} dos `combos` da `dc._medir` (chave 'parte|modulos', 'parte|inato' ou 'parte|sem_comer_dirigida')"""
    out = {p: {g: 0 for g in GRUPOS} for p in PARTES_F}
    for chave, n in combos.items():
        parte, _, resto = chave.partition("|")
        grupo = "sem_comer_dirigida" if resto == "sem_comer_dirigida" else ("inato" if resto == "inato" else _grupo(tuple(resto.split("+"))))
        out[parte][grupo] += n
    return out


def _instalar_coletor(ns, registro, categorias: dict, episodios: dict) -> None:
    """o coletor da `viver` da C4 (A9.8, item 5), com o sigma, a origem e o ponto de cada episodio: so le, nao toca em rng nem em estado"""
    c = ns.orq.cerebro_de(registro)
    agir = c.agir

    def agir_e_ler(obs, rng):
        acao = agir(obs, rng)
        for e in c.m.mem.recente:
            categorias.setdefault(e["id"], list(e["categoria"]))
            episodios.setdefault(e["id"], {"sigma": e["sigma"], "origem": e["origem"], "ponto": list(e["ponto"])})
        return acao

    c.agir = agir_e_ler


def rejogar(tarefa: tuple) -> dict:
    """uma vida: o replay do log (a `viver` da C4, com o coletor), o G1 e as medidas de A10.4 e A11.4 (so desta vida)"""
    codigo, gravada, arquivo, dias, orcamento = tarefa
    ns = carregar(codigo)
    ma, lr, orq = ns.ma, ns.lr, ns.orq
    braco, dono, lugar, semente = gravada["braco"], gravada["dono"], gravada["lugar"], gravada["semente"]
    texto = Path(arquivo).read_text(encoding="utf-8")
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento, conserto=True)
    cc = orq.bancada(dias, orcamento).cfg_corpo_de(ma.bv.EspecVida(dono, ma.gl.BRACO_V11, semente))
    categorias: dict = {}
    episodios: dict = {}
    feito = []

    def fp_coletor(cfg):
        registro = fp(cfg)
        _instalar_coletor(ns, registro, categorias, episodios)
        feito.append(registro)
        return registro

    def fm(politica, cfg, s):                                           # a mesma da `viver` da C4
        return lr.MotorGravaCorpo(politica, cfg, s, ma.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp_coletor, semente=semente, fabrica_motor=fm)
    registro = feito[0]
    del orq.cerebro_de(registro).agir                                   # o cerebro volta a ser o da fabrica
    a = orq.cerebro_de(registro).m.mem.estado_interno()["autobio"]       # o episodio do fechamento da ultima decisao nao passou pelo coletor
    for e in a["recente"] + a["duradoura"] + a["central"]:
        episodios.setdefault(e["id"], {"sigma": e["sigma"], "origem": e["origem"], "ponto": list(e["ponto"])})
    if motor.log.para_jsonl() != texto:
        raise orq.bv.ReplayDivergiu(f"{arquivo}: o log rejogado nao e o do disco")
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    ma.conferir_memoria(braco, orq.cerebro_de(registro))
    fins = ma.conferir_fins(braco, registro)
    refeita = {"vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": gravada["base"],
               "k": gravada["k"], **orq.medidas(motor, registro, braco, dias, True),
               "corpo": lr.medidas_do_corpo(motor, registro, dias), "fins_conferidos": fins,
               "memoria": ma.medidas_memoria(registro, dias, categorias)}
    sem_custo = {k: v for k, v in gravada.items() if k != "custo"}
    if json.dumps(refeita, sort_keys=True) != json.dumps(sem_custo, sort_keys=True):
        raise RuntimeError(f"G1 do descritivo: a vida {gravada['vida']} nao refaz as medidas gravadas")
    # a `_medir` da C1 (a particao, D1, D2, D4 e as idas), vista com a sonda da lembranca; o braco 'M3' so liga o registro das idas
    ns_medir = SimpleNamespace(orq=_OrqComLembranca(orq), met=ns.met)
    out = dc._medir(ns_medir, motor, registro, gravada, "M3", dono, lugar, semente)
    out["braco"] = braco
    out["F_grupo"] = regrupar(out["combos"])
    if braco == "SEM" and any(x in combo.split("|")[1].split("+") for combo in out["combos"] for x in ("memoria", "lembranca")):
        raise RuntimeError(f"{gravada['vida']}: no SEM a lembranca ou a memoria decidiu")
    out["idas"] = _acrescentar_idas(ns, motor, registro, episodios, out["idas"], dono, lugar, semente)
    out["metas"] = lr.trocas_de_meta(registro)
    out["log_sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return out


def _acrescentar_idas(ns, motor, registro, episodios: dict, idas: list, dono: str, lugar: str, semente: int) -> list:
    """A11.4, item 3: a cada ida (na ordem da `dc._idas`), o alvo e a distancia dele ao ponto fixo mais proximo, em celulas, e o episodio que
    a visita codificou (o id do `consequencia.autobio` das decisoes da ida, da que comecou a da que acabou, com a origem 'visita' e o ponto
    do alvo) com o sigma dele"""
    orq = ns.orq
    ms = orq.cerebro_de(registro).motivos
    mem = orq.cerebro_de(registro).m.mem
    sub = orq.CM.sub
    pontos = orq.DonoComLugar(orq.criar_dono(dono), lugar, semente, dono, orq.CM).pontos_fixos
    extras = []
    for k, m in enumerate(ms):
        for f in m["fins"]:
            if tuple(f["chave"][:2]) != tuple(dc.IDA):
                continue
            alvo = tuple(f["chave"][2])
            d = min(dc._distancia(math.isqrt, alvo[0], alvo[1], px, py) for px, py in pontos)
            achados = []
            for j in range(f["inicio"], k + 1):                           # a ida pode acabar na decisao em que comecou (n = 1)
                cons = ms[j]["consequencia"]
                if cons is None or cons.get("autobio") is None:
                    continue
                if cons["autobio"] not in episodios:
                    raise RuntimeError(f"o episodio {cons['autobio']} (decisao {j}) fora do coletor dos episodios")
                e = episodios[cons["autobio"]]
                if e["origem"] == "visita" and tuple(e["ponto"]) == alvo:
                    achados.append((cons["autobio"], e["sigma"]))
            extras.append({"alvo": list(alvo), "alvo_lugar": list(mem.lugar_de(*alvo)), "alvo_dist_ponto_celulas": d / sub,
                           "alvo_em_ponto_fixo": d == 0, "codificou": bool(achados), "visitas_codificadas": len(achados),
                           "sigma": achados[-1][1] if achados else None})
    if len(extras) != len(idas):
        raise RuntimeError(f"as idas do registro ({len(extras)}) nao sao as da `_idas` ({len(idas)})")
    return [{**i, **x} for i, x in zip(idas, extras)]


# ================================================================== as contas (estagio 1 e soma do estagio 2)
class Contas(dc.Contas):
    """as contas da C1, com o REL - SEM no lugar do M3* - M2 e a estimativa da C4 (a margem delta = 0,032, AD9-5)"""

    def __init__(self, ns, registros: list[dict], donos: tuple, g_esperado: float | None) -> None:
        super().__init__(SimpleNamespace(orq=ns.orq, lr=ns.ma), registros, donos, g_esperado)

    def dif(self, medida, a: str = "REL", b: str = "SEM") -> dict:
        return super().dif(medida, a, b)

    def bloco(self, medida, sinal: bool = False) -> dict:
        out = {"REL-SEM": self.est(self.dif(medida)), "niveis": {b: self.lr.estimativa(self.nivel(medida, b)) for b in BRACOS}}
        if sinal:
            out["REL-SEM"]["classe_sinal"] = dc._classe_sinal(out["REL-SEM"])
        return out


def conferir_campos(registros: list[dict]) -> None:
    """o estagio 1 usa estes campos do `medidas.json`; falha alto se faltar algum numa vida"""
    for r in registros:
        for caminho in CAMPOS_ESTAGIO1:
            x = r
            for chave in caminho:
                if not isinstance(x, dict) or chave not in x:
                    raise RuntimeError(f"{r['vida']}: falta o campo {'.'.join(caminho)} no medidas.json (A11.2, estagio 1)")
                x = x[chave]
        for mod in ("memoria", "lembranca"):
            if mod not in r["memoria"]["decidiu_vida"]:
                raise RuntimeError(f"{r['vida']}: falta memoria.decidiu_vida.{mod} no medidas.json")


def estagio1(c: Contas) -> dict:
    """D3, D6, D7, a lembranca e a conta do H4: so o `medidas.json` (A11.2, estagio 1)"""
    def ofertas(r):
        return r["cadeia_w"]["elegiveis"]

    def por_oferta(f):
        return lambda r: None if not ofertas(r) else f(r) / ofertas(r)

    d3 = {"visiveis_em_k0": c.bloco(por_oferta(lambda r: r["racao_na_janela"]["visiveis_em_k0"])),
          "entraram_na_visao": c.bloco(por_oferta(lambda r: r["racao_na_janela"]["entraram_na_visao"]))}
    d6 = {"refeicoes_por_dia": c.bloco(lambda r: r["cadeia"]["refeicoes_por_dia"]),
          "ofertas_elegiveis_por_vida": c.bloco(ofertas),
          "episodios_por_vida": c.bloco(lambda r: r["episodios_fome"]["n"]),
          "taxa_por_racao": c.bloco(lambda r: r["cadeia"]["taxa"]),
          "taxa_por_episodio": c.bloco(c.lr.EPISODIO)}
    d7 = {m: c.bloco(lambda r, m=m: r["influencia_vida"][m]) for m in sorted(c.regs[0]["influencia_vida"])}
    lembranca = {"com_lembranca": c.bloco(lambda r: r["memoria"]["com_lembranca"]),
                 "so_lembranca_mudou_a_escolha": c.bloco(lambda r: r["memoria"]["decidiu_vida"]["lembranca"]),
                 "memoria_mudou_a_escolha": c.bloco(lambda r: r["memoria"]["decidiu_vida"]["memoria"]),
                 "visitas_ao_lugar_lembrado": c.bloco(lambda r: r["visitas_lugar_lembrado"]),
                 "visitas_vazias": c.bloco(lambda r: r["visitas_vazias"])}
    classes = (d6["refeicoes_por_dia"]["REL-SEM"]["classe"]["classe"], d6["taxa_por_racao"]["REL-SEM"]["classe"]["classe"])
    h4 = {"refeicoes_por_dia": classes[0], "taxa_por_racao": classes[1], "cumpre": all(x in ("≈ 0", "< 0") for x in classes),
          "nota": "a margem delta = 0,032 (AD9-5) vale tambem para as refeicoes por dia e a taxa por racao (a letra de A10.4)"}
    return {"G": c.G, "D3": d3, "D6": d6, "D7": d7, "lembranca": lembranca, "H4": h4}


def _d5(c: Contas) -> dict:
    """as buscas pelo cheiro (D5), do `trocas_de_meta` refeito no replay: o `medidas.json` da C4 nao grava os motivos das trocas"""
    def por_oferta(f):
        return lambda r: None if not r["cadeia_w"]["elegiveis"] else f(r) / r["cadeia_w"]["elegiveis"]

    return {nome: c.bloco(por_oferta(f)) for nome, f in (
        ("achou", lambda r: r["dc13"]["metas"]["fins"]["busca"]["achou"]), ("sumiu", lambda r: r["dc13"]["metas"]["fins"]["busca"]["sumiu"]),
        ("desistiu", lambda r: r["dc13"]["metas"]["fins"]["busca"]["desistiu"]),
        ("trocou", lambda r: r["dc13"]["metas"]["fins"]["busca"]["trocou"]),
        ("trocou_pelo_reflexo", lambda r: r["dc13"]["metas"]["trocas"]["busca"]["reflexo"]),
        ("trocou_pelo_dormir_sorteado", lambda r: r["dc13"]["metas"]["trocas"]["busca"]["dormir_sorteio"]),
        ("trocou_por_outra_unidade", lambda r: r["dc13"]["metas"]["trocas"]["busca"]["outra_unidade"]))}


def estagio2(c: Contas) -> dict:
    A = {p: c.bloco(lambda r, p=p: dc._fracao(r, "F", p)) for p in PARTES_F}
    A_grupo = {p: {g: c.bloco(lambda r, p=p, g=g: dc._frac_grupo(r, p, (g,))) for g in GRUPOS} for p in PARTES_F}
    B = {p: c.bloco(lambda r, p=p: dc._fracao(r, "P", p)) for p in PARTES_P}
    soma_f = dc._soma([c.dif(lambda r, p=p: dc._fracao(r, "F", p)) for p in PARTES_F])
    soma_p = dc._soma([c.dif(lambda r, p=p: dc._fracao(r, "P", p)) for p in PARTES_P])
    for nome, soma, sinal in (("F", soma_f, 1), ("P", soma_p, -1)):
        for u, v in c.G_difs.items():
            if abs(sinal * soma[u] - v) > 1e-12:
                raise RuntimeError(f"a soma das parcelas {nome} nao fecha no ganho da unidade {u}: {sinal * soma[u]!r} e {v!r}")
    fecha = {"F": c.est(soma_f)["media"], "P": -c.est(soma_p)["media"], "G": c.G}
    if abs(fecha["F"] - c.G) > 1e-12 or abs(fecha["P"] - c.G) > 1e-12:
        raise RuntimeError(f"as somas das parcelas nao fecham em G: {fecha}")
    h = {
        "H1": c.est(c.dif(lambda r: dc._fracao(r, "F", "F-a"))),
        "H1'": c.est(c.dif(lambda r: dc._fracao(r, "F", "F-b"))),
        "H2": c.est(dc._soma([c.dif(lambda r, p=p: dc._frac_grupo(r, p, ("inato", "aprendido_habito"))) for p in ("F-c", "F-d")])),
        "H3": c.est(dc._soma([c.dif(lambda r, p=p: dc._fracao(r, "P", p)) for p in ("P-a", "P-b")], -1)),
        "H5": c.est(dc._soma([c.dif(lambda r, p=p: dc._frac_grupo(r, p, ("lembranca",))) for p in ("F-a", "F-c", "F-d")])),
        "F-d_sem_modulo": c.est(c.dif(lambda r: dc._frac_grupo(r, "F-d", ("sem_comer_dirigida",)))),
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
                        "F_por_grupo": {p: {g: sum(r["dc13"]["F_grupo"][p][g] for r in rs) for g in GRUPOS} for p in PARTES_F},
                        "fechados_nas_medidas": sum(r["episodios_fome"]["fechados"] for r in rs),
                        "diag": {k: sum(r["dc13"]["diag"][k] for r in rs) for k in rs[0]["dc13"]["diag"]},
                        "ofertas_de_racao": sum(r["dc13"]["ofertas"] for r in rs),
                        "idas": sum(len(r["dc13"]["idas"]) for r in rs)}
        s = cobertura[b]
        if sum(s["F"].values()) + sum(s["P"].values()) != s["episodios"] or sum(s["F"].values()) != s["fechados_nas_medidas"]:
            raise RuntimeError(f"{b}: a particao nao cobre cada episodio uma vez so")
        if any(sum(s["F_por_grupo"][p].values()) != s["F"][p] for p in PARTES_F):
            raise RuntimeError(f"{b}: os grupos de A11.4 nao somam as parcelas F")
    combos = {}
    for b in BRACOS:
        acc: dict = {}
        for r in c.regs:
            if r["braco"] == b:
                for k, v in r["dc13"]["combos"].items():
                    acc[k] = acc.get(k, 0) + v
        combos[b] = dict(sorted(acc.items()))
    return {"A": A, "A_por_modulo": A_grupo, "B": B, "soma_das_parcelas": fecha, "hipoteses": h, "D1": D1, "D2": D2, "D4": D4, "D5": _d5(c),
            "cobertura": cobertura, "combos_por_braco": combos, "idas": _resumo_idas(c.regs)}


def _resumo_idas(registros: list[dict]) -> dict:
    """o registro das visitas do REL (A11.4, item 3): so por braco e por estilo do dono, sem contraste e sem leitura (a LP-2). O SEM so
    entra na contagem de idas (por construcao nao tem lugar lembrado)."""
    idas = [i for r in registros if r["braco"] == "REL" for i in r["dc13"]["idas"]]

    def resumo(xs: list) -> dict:
        if not xs:
            return {"idas": 0}
        cont = lambda k: dict(sorted({v: sum(1 for i in xs if i[k] == v) for v in {i[k] for i in xs}}.items()))   # noqa: E731
        sig = [i["sigma"] for i in xs if i["codificou"]]
        return {"idas": len(xs), "decisoes_media": statistics.fmean(i["decisoes"] for i in xs),
                "decisoes_mediana": statistics.median(i["decisoes"] for i in xs), "fins": cont("motivo"),
                "custo_media": statistics.fmean(i["custo"] for i in xs), "custo_mediana": statistics.median(i["custo"] for i in xs),
                "classes_chegada": cont("classes_chegada"), "classes_seguinte": cont("classes_seguinte"),
                "frac_racao_entrou_na_vista": sum(1 for i in xs if i["racao_entrou"]) / len(xs),
                "frac_racao_entrou_e_comida_depois": sum(1 for i in xs if i["racao_entrou_e_comida_depois"]) / len(xs),
                "alvo_dist_ponto_celulas_media": statistics.fmean(i["alvo_dist_ponto_celulas"] for i in xs),
                "alvo_dist_ponto_celulas_mediana": statistics.median(i["alvo_dist_ponto_celulas"] for i in xs),
                "frac_alvo_em_ponto_fixo": sum(1 for i in xs if i["alvo_em_ponto_fixo"]) / len(xs),
                "frac_visita_codificou_episodio": sum(1 for i in xs if i["codificou"]) / len(xs),
                "visitas_com_mais_de_um_episodio": sum(1 for i in xs if i["visitas_codificadas"] > 1),
                "sigma_media": statistics.fmean(sig) if sig else None, "sigma_mediana": statistics.median(sig) if sig else None}
    return {"todas": resumo(idas), "por_dono": {d: resumo([i for i in idas if i["dono"] == d]) for d in sorted({i["dono"] for i in idas})},
            "rotulo": "so o REL, so por braco: a LP-2, sem contraste e sem leitura"}


# ================================================================== a regra de leitura (A10.5, com as mudancas de A11.5)
def ler(s1: dict, s2: dict) -> dict:
    """a regra de A10.5, na ordem, com as mudancas de A11.5: H5 = F-a + F-c + F-d no grupo 'lembranca' (sem condicao de D1); H1, H1', H3 e H4
    como em A10.5, com a condicao de D1 no H1' (AD11-4); duas ou mais que 'explicam' fora dos pares sao mistura, e uma so que 'contribui' sem
    nenhuma que 'explique' fica 'indeterminado', com a parte registrada. 'Explica a maior parte': classe '> 0' e s >= 1/2."""
    h, d1 = s2["hipoteses"], s2["D1"]["REL-SEM"]
    d1_neg = d1["classe_sinal"] == "< 0"
    d1_nao_neg = d1["ic95"]["ic_superior"] is not None and not d1["ic95"]["ic_superior"] < 0
    elegiveis = {"H1": d1_neg, "H1'": d1_nao_neg, "H2": not d1_neg, "H3": True, "H5": True}
    explicam = sorted(k for k in elegiveis if elegiveis[k] and dc._explica(h[k]))
    contribuem = sorted(k for k in elegiveis if elegiveis[k] and dc._contribui(h[k]))
    partes = {k: {"s": h[k]["s"], "media": h[k]["media"], "ic95": h[k]["ic95"], "classe": h[k]["classe"]["classe"],
                  "condicao_extra_cumprida": elegiveis[k]} for k in elegiveis}
    out = {"explicam_a_maior_parte": explicam, "contribuem": contribuem, "partes": partes,
           "D1_classe_sinal": d1["classe_sinal"], "H1_sem_D1": dc._explica(h["H1"]) and not d1_neg,
           "substituicao": dc._explica(h["H1'"]) and s2["A"]["F-c"]["REL-SEM"]["classe"]["classe"] == "< 0"}
    if s1["H4"]["cumpre"]:
        out["linha"] = "o ganho e da medida: o REL nao come mais, ele muda os episodios; as outras linhas nao se leem"
    elif len(explicam) == 1:
        out["linha"] = f"aponta para {explicam[0]}, como leitura descritiva (A11.6)"
    elif "H3" in explicam and ("H1" in explicam or "H1'" in explicam):
        out["linha"] = "mistura de posicao e custo: registrada sem escolher"
    elif len(explicam) >= 2:
        out["linha"] = f"mistura ({', '.join(explicam)} explicam ao mesmo tempo): registrada com as partes, sem escolher (A11.5)"
    elif len(contribuem) >= 2:
        out["linha"] = f"mistura ({', '.join(contribuem)} contribuem): registrada com as partes, sem escolher"
    else:
        out["linha"] = "indeterminado: o caminho nao e nenhum dos previstos; nenhuma hipotese nova se testa nos mesmos dados"
        out["F-d_sem_modulo_explica_a_maior_parte"] = dc._explica(h["F-d_sem_modulo"])
        if len(contribuem) == 1:
            out["parte_registrada"] = contribuem[0]
    if out["substituicao"]:
        out["linha"] += ". Substituicao: F-b explica e F-c fica '< 0'; nao se le H1' como ganho liquido da patrulha"
    return out


def _chave_da_leitura(leit: dict) -> tuple:
    """a linha de uma leitura (a da C1 ou a do REL) como chave comparavel: ('medida',), ('aponta', H), ('mistura', (H, ...)) ou ('indeterminado',)"""
    linha = leit["linha"]
    if linha.startswith("o ganho e da medida"):
        return ("medida",)
    if linha.startswith("aponta para"):
        return ("aponta", leit["explicam_a_maior_parte"][0])
    if linha.startswith("mistura"):
        return ("mistura", tuple(leit["explicam_a_maior_parte"] if len(leit["explicam_a_maior_parte"]) >= 2 else leit["contribuem"]))
    if linha.startswith("indeterminado"):
        return ("indeterminado",)
    raise RuntimeError(f"a linha de leitura nao e uma das previstas: {linha!r}")


def comparar_c1(leit_rel: dict, s2_rel: dict, c1: dict) -> dict:
    """A11.5 (AD11-5): a linha do REL ao lado da 13.6 (a C1), pela tabela do adendo; o s e a classe de cada parcela nas duas runs, so como
    descricao. NAO ha IC da diferenca entre as runs (faixas, contrastes e margens diferentes: 0,022 na C1 e 0,032 na C4)."""
    k_rel, k_c1 = _chave_da_leitura(leit_rel), _chave_da_leitura(c1["leitura"])
    if k_rel == ("indeterminado",):
        veredito = "o caminho do REL fica sem leitura; a da C1 nao muda"
    elif k_rel == k_c1:
        veredito = "o caminho se repete no cerebro padrao, pela mesma regra"
    else:
        veredito = "o caminho nao se transfere: ficam duas leituras, uma por cerebro, cada uma com as partes dela"
    c1_s2 = c1["estagio2"]
    lado = {"hipoteses": {k: {"c1": {"s": c1["leitura"]["partes"][k]["s"], "classe": c1["leitura"]["partes"][k]["classe"]} if k in c1["leitura"]["partes"] else None,
                              "rel": {"s": leit_rel["partes"][k]["s"], "classe": leit_rel["partes"][k]["classe"]}} for k in HIPOTESES},
            "F": {p: {"c1": {"s": c1_s2["A"][p]["M3-M2"]["s"], "classe": c1_s2["A"][p]["M3-M2"]["classe"]["classe"]},
                      "rel": {"s": s2_rel["A"][p]["REL-SEM"]["s"], "classe": s2_rel["A"][p]["REL-SEM"]["classe"]["classe"]}} for p in PARTES_F},
            "P": {p: {"c1": {"s": c1_s2["B"][p]["M3-M2"]["s"], "classe": c1_s2["B"][p]["M3-M2"]["classe"]["classe"]},
                      "rel": {"s": s2_rel["B"][p]["REL-SEM"]["s"], "classe": s2_rel["B"][p]["REL-SEM"]["classe"]["classe"]}} for p in PARTES_P}}
    return {"linha_c1": c1["leitura"]["linha"], "linha_rel": leit_rel["linha"], "veredito": veredito, "lado_a_lado": lado,
            "nota": "descritiva, sem teste entre as runs (AD11-5); uma linha igual nao diz que o mecanismo e o mesmo, so que a mesma regra aponta "
                    "para o mesmo lugar"}


# ================================================================== o principal
def principal(codigo: Path, meta: dict, medidas: dict, tar: Path, saida: Path, processos: int, fontes: dict, resultado: dict | None,
              c1: dict | None = None, donos: tuple = DONOS, so_estagio1: bool = False, vidas_esperadas: int | None = None) -> dict:
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe: o descritivo roda uma vez (AD11-7)")
    if processos > dc.MAX_PROCESSOS:
        raise SystemExit(f"ate {dc.MAX_PROCESSOS} processos (V3-D8)")
    g_esperado = None if resultado is None else resultado["primario"]["REL - SEM"]["media"]
    alvo = sorted((v for v in medidas.values() if v["lugar"] == ESTILO and v["braco"] in BRACOS and v["dono"] in donos),
                  key=lambda v: v["vida"])
    if vidas_esperadas is not None and len(alvo) != vidas_esperadas:
        raise RuntimeError(f"{len(alvo)} vidas do {ESTILO} (REL e SEM) no medidas.json; o adendo 11 pede {vidas_esperadas}")
    codigo_ok = conferir_codigo(codigo, meta)                           # 1a conferencia: antes de importar uma linha do pacote
    ns0 = carregar(codigo)
    conferir_campos(alvo)
    cfg = meta["config"]
    c_1 = Contas(ns0, alvo, donos, g_esperado)
    s1 = estagio1(c_1)
    out = {"rotulo": ROTULO, "plano": "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 11 (A11.1 a A11.9)",
           "fontes_sha256": fontes,
           "scripts": {"experiments/descritivo_dc13_rel.py": dc._sha(Path(__file__)),
                       "experiments/descritivo_dc13_longe_fixo.py": dc._sha(Path(dc.__file__))},
           "commit_da_run": meta["git_head"], "codigo": codigo_ok, "unidades": len({(v["base"], v["semente"]) for v in alvo}),
           "vidas": len(alvo), "estagio1": s1}
    if so_estagio1:
        out["rotulo"] += " [PARCIAL: so o estagio 1; nenhuma leitura]"
        out["leitura"] = {"linha": "nenhuma leitura: so o estagio 1, rotulado como parcial (A11.5)"}
        return out
    with tempfile.TemporaryDirectory() as tmp:
        logs = dc.extrair_logs(tar, alvo, Path(tmp))
        tarefas = [(str(codigo), v, str(logs[v["vida"]]), cfg["dias"], cfg["orcamento_por_dia"]) for v in alvo]
        if processos <= 1:
            saidas = [rejogar(t) for t in tarefas]
        else:
            with ProcessPoolExecutor(max_workers=processos) as pool:
                saidas = list(pool.map(rejogar, tarefas))
    por_vida = {s["vida"]: s for s in saidas}
    registros = [{**v, "dc13": por_vida[v["vida"]]} for v in alvo]
    c_2 = Contas(ns0, registros, donos, g_esperado)
    s2 = estagio2(c_2)
    leitura = ler(s1, s2)
    logs_sha = {s["vida"]: s["log_sha256"] for s in saidas}
    out.update({"g1": {"vidas_refeitas": len(saidas), "todas_iguais": True},
                "logs_sha256_do_conjunto": hashlib.sha256("".join(logs_sha[k] for k in sorted(logs_sha)).encode()).hexdigest(),
                "estagio2": s2, "leitura": leitura})
    if c1 is not None:
        out["comparacao_com_a_c1"] = comparar_c1(leitura, s2, c1)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--codigo", type=Path, required=True, help="a worktree destacada do a287ba2")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--so-estagio1", action="store_true", help="so o estagio 1, rotulado como parcial (se o estagio 2 nao vale)")
    a = ap.parse_args()
    fontes = ler_fontes()
    meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
    if meta["git_head"] != COMMIT_DA_RUN:
        raise RuntimeError("o meta.json nao e o da C4 (a287ba2)")
    medidas, sha_medidas = carregar_medidas(RUN / "medidas.json.gz", meta)
    if sha_medidas != SHA_MEDIDAS:
        raise RuntimeError(f"o medidas.json descomprimido nao e o registrado (sha256 {sha_medidas})")
    fontes["medidas.json"] = sha_medidas
    resultado = json.loads((RUN / "resultado.json").read_text(encoding="utf-8"))
    c1 = json.loads(DESCRITIVO_C1.read_text(encoding="utf-8"))
    t0 = time.perf_counter()
    d = principal(a.codigo.resolve(), meta, medidas, RUN / "vidas.tar.gz", SAIDA, a.processos, fontes, resultado, c1,
                  so_estagio1=a.so_estagio1, vidas_esperadas=VIDAS_ESPERADAS)
    destino = SAIDA.with_name("descritivo_rel_parcial.json") if a.so_estagio1 else SAIDA
    sha = dc.gravar(destino, d)
    print(f"gravado {destino.relative_to(RAIZ)} (sha256 {sha}) em {time.perf_counter() - t0:.0f} s; a leitura: {d['leitura']['linha']}")
