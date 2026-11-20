"""CORPO C4, a validacao do teto baixo (docs/PLANO_ANALISE_V3_CORPO_C4.md, APROVADO pelo Matheus em 2026-11-20, D-C4-1 a D-C4-12).

Pergunta (secao 1): em sementes novas, o pet com o DTB passa mais tempo bem do que o pet de hoje, sem perder saude nem forrageio?

Os bracos (secao 2): o CTRL (o corpo de hoje) e o DTB (a ponte da D com teto em C/2, o braco que a C3 escolheu). As vidas sao as da C3
(`run_v3_corpo_c3`): o bloco I com o pet sozinho nas 12 celulas x 200 unidades (107001...107200, k = 1), o bloco II com um par VIVO por
unidade e braco (107301...107800, k = 1, prefixo corpo_par). Este orquestrador e proprio para o `run_v3_corpo_c3.py` ficar intacto (o
sha256 dele esta no meta.json da C3); as pecas das vidas vem de la.

A analise (secao 6): a primaria e o "Tempo bem" (`digilab.metrics.tempo_bem_nas_decisoes`, dias 1 a 14), DTB - CTRL, nas 12 celulas e
nas 11 distintas; as guardas sao a saude (12 celulas e as 6 do relapso e do aleatorio), a taxa por episodio no `longe_fixo`, o "Tempo
bem" por lugar e o S2; a saude por celula nao reprova, mas vira ressalva (D-C4-2). As premissas da secao 5.2 deixam a medida
"inconclusiva por premissa". O relogio de cada vida vai para o `custos.json`, fora do `medidas.json` (D-C4-8).

A trava (secao 0): sem o "APROVADO pelo Matheus" no cabecalho do plano, sem a faixa em FAIXAS_RESERVADAS, com a pasta de saida ja
existente ou fora das bases do plano, o orquestrador recusa; a run passa antes pelo `tools/pre_run.py` e confere o disco. A fumaca usa as
sementes dos testes.

Uso: python experiments/run_v3_corpo_c4.py --config experiments/configs/v3_corpo_c4/run.json --processos 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import run_v3_corpo_c3 as C3  # noqa: E402
import run_v3_corpo_tempo_bem as TB  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402

C2, orq, ma, lr, V, CA, A0 = C3.C2, C3.orq, C3.ma, C3.lr, C3.V, C3.CA, C3.A0
PLANO = "docs/PLANO_ANALISE_V3_CORPO_C4.md"
ORQUESTRADOR = "experiments/run_v3_corpo_c4.py"
FASE = "corpo_c4"
PREFIXO, PREFIXO_PAR = C3.PREFIXO, C3.PREFIXO_PAR
FAIXA = (107001, 107800)                                      # secao 4, D-C4-7
BASES_I = tuple(range(107001, 107201))                        # 200 sementes independentes
BASES_II = tuple(range(107301, 107801))                       # o bloco II: 500 pares (D-C4-5)
K_POR_BASE = 1
DIAS, ORCAMENTO_POR_DIA = C3.DIAS, C3.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_corpo/c4"                               # secao 7
MAX_PROCESSOS = C3.MAX_PROCESSOS
CONTROLE, TRATADO = "CTRL", "DTB"
BRACOS = (CONTROLE, TRATADO)                                  # secao 2, D-C4-3: a D e o DTL ficam fora
CELULAS, CELULAS_DISTINTAS, CELULAS_SEM_COMIDA = C3.CELULAS, C3.CELULAS_DISTINTAS, C3.CELULAS_SEM_COMIDA
PRIMARIO = C3.PRIMARIO                                        # o longe_fixo (a guarda da taxa por episodio)
LUGARES = ("comedouro", "longe", "longe_fixo")
MARGEM, ALFA = C3.MARGEM, C3.ALFA                             # 0,032 (SEM FONTE) e 0,025 unilateral (D-C4-11)
EPISODIO, SAUDE, PRIVACAO, EXAUSTAO = C3.EPISODIO, C3.SAUDE, C3.PRIVACAO, C3.EXAUSTAO
TEMPO_BEM = lambda r: r["tempo_bem"]                          # noqa: E731
TEMPO_BEM_8_14 = lambda r: r["tempo_bem_8_14"]                # noqa: E731
CHUTES = lambda r: r["chutes"]                                # noqa: E731
CHAVES_CONFIG = C3.CHAVES_CONFIG
PISO_DISCO_GB = 10                                            # secao 4, SEM FONTE
# os pisos das premissas (secao 5.2, D-C4-10, aceitos pelo Matheus em 2026-11-20; todos SEM FONTE)
PISOS = {"tempo_bem_vidas_no_piso_ou_teto_max": 0.05, "episodios_por_vida_min": 8.0, "vidas_sem_episodio_max": 0.02,
         "ticks_no_teto_min": 0.10, "pares_com_a_janela_min": 0.90, "chutes_por_vida_min": 1.0, "vidas_com_chute_min": 0.50}
P_PRIMARIA, P_BRACO = "primaria", "braco"                     # de que medida cada premissa e (a do braco pesa na primaria)
G_TAXA, G_S2 = "taxa_por_episodio_longe_fixo", "S2_tempo_ate_o_reencontro"


# ================================================================== as vidas
def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida do bloco I: a da C3 (`run_v3_corpo_c3._vida`, as mesmas conferencias), mais o "Tempo bem" e os chutes"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias, baixas = C3.viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    texto = motor.log.para_jsonl()
    arquivo.write_text(texto, encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo("REL", registro, None)
    ma.conferir_memoria("REL", orq.cerebro_de(registro))
    fins = ma.conferir_fins("REL", registro)
    C3.conferir_vida(braco, motor, registro, baixas)
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    dec = motor.decisoes_mundo
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias),
            "valuation": V.descritivo_valuation(registro, med), "acoplamento": CA.medidas_acoplamento(motor, registro, baixas),
            **C3.medidas_c3(motor, registro, cfg["dias"]),
            **TB.medidas_da_vida(registro.estados, CONFIG_PADRAO.intervalo_decisao_ticks, cfg["dias"]),
            "chutes": sum(1 for d in dec if d["brincou_com_bola"]), "brincar": sum(1 for d in dec if d["acao"] == "brincar"),
            "descartado": motor.corpo.descartado_total, "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


def tarefa_par(cfg: dict, u: dict, pasta: str) -> list[dict]:
    return [C3.par(cfg, b, u, pasta) for b in BRACOS]


# ================================================================== a analise (secao 6, escrita antes)
def _media(xs: list) -> float | None:
    return sum(xs) / len(xs) if xs else None


def _nivel(registros: list[dict], braco: str, medida, celulas) -> float | None:
    return ma.estimativa(orq.por_unidade(registros, braco, None, medida, celulas))["media"]


def _descr(registros: list[dict], medida, celulas) -> dict:
    """niveis dos dois bracos e DTB - CTRL (a media, o dp e o IC95), sem classe: so descritivo"""
    e = ma.estimativa(C3._difs(registros, medida, celulas, TRATADO))
    return {"niveis": {b: _nivel(registros, b, medida, celulas) for b in BRACOS},
            "DTB - CTRL": {k: v for k, v in e.items() if k != "classe"}}


def primaria(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """o "Tempo bem" dos dias 1 a 14, DTB - CTRL pareado por unidade, nas 12 celulas e nas 11 distintas (D-C4-9 e D-C4-11)"""
    out = {}
    for nome, cs in (("12_celulas", CELULAS), ("11_celulas", CELULAS_DISTINTAS)):
        c = orq.contraste_t(C3._difs(registros, TEMPO_BEM, cs, TRATADO), boot)
        ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
        out[nome] = {"contraste": f"{TRATADO} - CTRL, o Tempo bem dos dias 1 a 14, {nome}", **c, "classe": ma.classe(ic, MARGEM),
                     "margem": MARGEM, "niveis": {b: _nivel(registros, b, TEMPO_BEM, cs) for b in BRACOS}}
    return out


def guardas(registros: list[dict], pares: list[dict], base=CELULAS) -> dict:
    """as guardas vinculantes (D-C4-12): a saude (2), a taxa por episodio, o "Tempo bem" por lugar (3) e o S2. `base`: as 12 celulas,
    ou as 11 distintas na sensibilidade"""
    nome = "as 12 celulas" if base == CELULAS else f"as {len(base)} celulas"
    return {"saude_12_celulas": C3._guarda(registros, SAUDE, base, nome, TRATADO, "< 0"),
            "saude_sem_comida": C3._guarda(registros, SAUDE, tuple(c for c in base if c in CELULAS_SEM_COMIDA),
                                           "as celulas do relapso e do aleatorio", TRATADO, "< 0"),
            G_TAXA: C3._guarda(registros, EPISODIO, C3._celulas(PRIMARIO, base), PRIMARIO, TRATADO, "< 0"),
            **{f"tempo_bem_{lugar}": C3._guarda(registros, TEMPO_BEM, C3._celulas(lugar, base), lugar, TRATADO, "< 0") for lugar in LUGARES},
            G_S2: C3._s(pares, C2.T_REENCONTRO, TRATADO, "> 0")}


def saude_por_celula(registros: list[dict]) -> dict:
    """D-C4-2: a saude de cada uma das 6 celulas do relapso e do aleatorio; "< 0" nao reprova o braco, vira ressalva"""
    return {f"{d}|{lugar}": C3._guarda(registros, SAUDE, ((d, lugar),), f"{d}|{lugar}", TRATADO, "< 0") for d, lugar in CELULAS_SEM_COMIDA}


def premissas(registros: list[dict], pares: list[dict]) -> dict:
    """secao 5.2: o evento de cada medida, contado na propria run, contra o piso escrito antes (D-C4-10)"""
    def vidas(b, lugar=None):
        return [r for r in registros if r["braco"] == b and (lugar is None or r["lugar"] == lugar)]

    extremos = {b: _media([float(r["tempo_bem"] in (0.0, 1.0)) for r in vidas(b)]) for b in BRACOS}
    eps = {b: {"media": _media([r["episodios_fome"]["n"] for r in vidas(b, PRIMARIO)]),
               "sem_episodio": _media([float(r["episodios_fome"]["n"] == 0) for r in vidas(b, PRIMARIO)])} for b in BRACOS}
    teto = {lugar: _media([r["fracao_ticks_teto"] for r in vidas(TRATADO, lugar)]) for lugar in LUGARES}
    janela = {b: _media([float(p["janela"]["cabe"]) for p in pares if p["braco"] == b]) for b in BRACOS}
    ch = {"media": _media([r["chutes"] for r in vidas(CONTROLE, PRIMARIO)]),
          "com_chute": _media([float(r["chutes"] > 0) for r in vidas(CONTROLE, PRIMARIO)])}
    P = PISOS
    return {"tempo_bem_fora_do_piso_e_do_teto": {
                "mede": P_PRIMARIA, "valores": extremos, "piso": {"max": P["tempo_bem_vidas_no_piso_ou_teto_max"]},
                "cumpre": all(v is not None and v <= P["tempo_bem_vidas_no_piso_ou_teto_max"] for v in extremos.values())},
            "ponte_no_teto": {
                "mede": P_BRACO, "valores": teto, "piso": {"min": P["ticks_no_teto_min"]},
                "cumpre": all(v is not None and v >= P["ticks_no_teto_min"] for v in teto.values())},
            "episodios_de_fome": {
                "mede": G_TAXA, "valores": eps, "piso": {"media_min": P["episodios_por_vida_min"], "sem_episodio_max": P["vidas_sem_episodio_max"]},
                "cumpre": all(v["media"] is not None and v["media"] >= P["episodios_por_vida_min"]
                              and v["sem_episodio"] <= P["vidas_sem_episodio_max"] for v in eps.values())},
            "janela_do_reencontro": {
                "mede": G_S2, "valores": janela, "piso": {"min": P["pares_com_a_janela_min"]},
                "cumpre": all(v is not None and v >= P["pares_com_a_janela_min"] for v in janela.values())},
            "chutes_no_longe_fixo": {
                "mede": "descritivo_dos_chutes", "valores": ch, "piso": {"media_min": P["chutes_por_vida_min"], "com_chute_min": P["vidas_com_chute_min"]},
                "cumpre": ch["media"] is not None and ch["media"] >= P["chutes_por_vida_min"] and ch["com_chute"] >= P["vidas_com_chute_min"]}}


def leitura(prim: dict, g: dict, celulas: dict, prem: dict) -> dict:
    """a tabela da secao 6: confirma, confirma com ressalva, nao confirma ou indeterminado. Uma guarda com a premissa descumprida sai
    "inconclusiva por premissa": nao reprova e nao passa, e sem ela a leitura nao chega a "confirma" (fica "indeterminado")"""
    sem_premissa = sorted({p["mede"] for p in prem.values() if not p["cumpre"]})
    inconclusivas = [n for n in g if n in sem_premissa]
    reprovadas = [n for n, x in g.items() if not x["passa"] and n not in inconclusivas]
    ressalva = [n for n, x in celulas.items() if not x["passa"]]
    classes = [prim[k]["classe"]["classe"] for k in ("12_celulas", "11_celulas")]
    ps = [prim[k]["p_unilateral"] for k in ("12_celulas", "11_celulas")]
    if P_PRIMARIA in sem_premissa or P_BRACO in sem_premissa:
        veredito, motivo = "indeterminado", "a primaria e inconclusiva por premissa"
    elif any(c in ("≈ 0", "< 0") for c in classes):
        veredito, motivo = "nao confirma", "a primaria nao sai > 0 nas 12 e nas 11 celulas"
    elif any(c == "indeterminado" for c in classes):
        veredito, motivo = "indeterminado", "a primaria sai indeterminado"
    elif any(p is None or p > ALFA for p in ps):
        veredito, motivo = "nao confirma", "a primaria sai > 0 sem o p unilateral"
    elif reprovadas:
        veredito, motivo = "nao confirma", "alguma guarda reprova"
    elif inconclusivas:
        veredito, motivo = "indeterminado", "alguma guarda e inconclusiva por premissa"
    elif ressalva:
        veredito, motivo = "confirma com ressalva", "alguma celula do relapso ou do aleatorio com a saude < 0"
    else:
        veredito, motivo = "confirma", None
    return {"leitura": veredito, "motivo": motivo, "reprovadas": reprovadas, "inconclusivas_por_premissa": inconclusivas,
            "celulas_em_ressalva": ressalva, "premissas_descumpridas": sorted(n for n, p in prem.items() if not p["cumpre"]),
            "proximo": "confirma vai a C5; confirma com ressalva volta ao Matheus com a celula; o resto fica registrado e o corpo fica o de hoje"}


DESCRITIVOS = {**C3.DESCRITIVOS_C3, "privacao": PRIVACAO, "exaustao": EXAUSTAO, "tempo_bem": TEMPO_BEM, "tempo_bem_8_14": TEMPO_BEM_8_14,
               "privacao_vida": lambda r: r["privacao_vida"], "exaustao_vida": lambda r: r["exaustao_vida"], "chutes": CHUTES,
               "brincar": lambda r: r["brincar"], "taxa_por_episodio": EPISODIO}
POR_DONO = {"saude_media": SAUDE, "privacao": PRIVACAO, "exaustao": EXAUSTAO, "tempo_bem": TEMPO_BEM, "chutes": CHUTES,
            "refeicoes_por_dia": lambda r: r["cadeia"]["refeicoes_por_dia"]}


def comparacao_com_a_c3() -> dict | None:
    """os numeros da C3 (a run que escolheu o braco e o replay do "Tempo bem"), para irem ao lado dos da C4; None sem os artefatos"""
    r, t = RAIZ / "artifacts_v3_corpo" / "c3" / "resultado.json", RAIZ / "artifacts_v3_corpo" / "c3_tempo_bem" / "resumo.json"
    if not (r.exists() and t.exists()):
        return None
    c3, tb = json.loads(r.read_text(encoding="utf-8")), json.loads(t.read_text(encoding="utf-8"))
    cb = c3["criterios"][TRATADO]
    so = lambda x: {k: x[k] for k in ("media", "ic95")}       # noqa: E731
    return {"fontes_sha256": {"c3/resultado.json": bv._sha(r), "c3_tempo_bem/resumo.json": bv._sha(t)},
            "tempo_bem": {n: so(v) for n, v in tb["tempo_bem"].items()},
            "taxa_por_episodio_longe_fixo": so(cb["F"]), "guardas_da_c3": {n: so(v) for n, v in cb["B"].items()},
            "S2_tempo_ate_o_reencontro": so(cb["S"][G_S2])}


def descritivo(registros: list[dict], pares: list[dict]) -> dict:
    """secao 6, sem teste: por lugar, por dono, o "Tempo bem" por celula, os chutes, as 11 celulas, o incoerente, o bloco II e a C3"""
    grupos = (("12_celulas", CELULAS), ("11_celulas", CELULAS_DISTINTAS), *((lugar, C3._celulas(lugar)) for lugar in LUGARES))
    idx = {(r["braco"], r["dono"], r["lugar"], r["semente"]): r["log_sha256"] for r in registros}
    sementes = sorted({r["semente"] for r in registros})
    return {"por_lugar": {onde: {n: _descr(registros, f, cs) for n, f in DESCRITIVOS.items()} for onde, cs in grupos},
            "por_dono": {f"{d}|{lugar}": {n: _descr(registros, f, ((d, lugar),)) for n, f in POR_DONO.items()} for d, lugar in CELULAS},
            "as_oito_guardas_da_c3": {n: {k: v for k, v in x.items() if k not in ("passa", "reprova_com")}
                                      for n, x in C3.guardas_b(registros, TRATADO).items()},
            "chutes": {lugar: {**_descr(registros, CHUTES, C3._celulas(lugar)),
                               "fracao_vidas_com_chute": {b: _media([float(r["chutes"] > 0) for r in registros
                                                                     if r["braco"] == b and r["lugar"] == lugar]) for b in BRACOS}}
                       for lugar in LUGARES},
            "guardas_11_celulas": {n: {k: x[k] for k in ("media", "ic95", "classe", "passa")}
                                   for n, x in guardas(registros, pares, CELULAS_DISTINTAS).items()},
            "incoerente_igual_ao_atencioso": {f"{b}|{lugar}": {"vidas": len(sementes), "iguais": sum(
                1 for s in sementes if idx[(b, "atencioso", lugar, s)] == idx[(b, "incoerente", lugar, s)])} for b in BRACOS for lugar in LUGARES},
            "bloco_II": {b: {"pares": sum(1 for p in pares if p["braco"] == b),
                             "fracao_janela_cabe": _media([float(p["janela"]["cabe"]) for p in pares if p["braco"] == b]),
                             "t_reencontro_media": _media([C2.T_REENCONTRO(p) for p in pares
                                                           if p["braco"] == b and C2.T_REENCONTRO(p) is not None])} for b in BRACOS},
            "comparacao_com_a_c3": comparacao_com_a_c3()}


def analisar(registros: list[dict], pares: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    prim, g, cel, prem = primaria(registros, boot), guardas(registros, pares), saude_por_celula(registros), premissas(registros, pares)
    return {"primaria": prim, "guardas": g, "saude_por_celula": cel, "premissas": prem, "veredito": leitura(prim, g, cel, prem),
            "descritivo": descritivo(registros, pares),
            "nao_demonstra": ["nada sobre o jogo web (a chave fica desligada nele)", "nada sobre outro teto alem de C/2",
                              "nada sobre a E e a C5 com o teto", "nada sobre o social alem do substrato: nenhum mecanismo social entra"]}


# ================================================================== a trava e a run
def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u, p = cfg["unidades"], cfg["pares"]
    if u.get("prefixo") != PREFIXO or p.get("prefixo") != PREFIXO_PAR or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA:
        raise ValueError("config fora do plano: os prefixos ou o orcamento (secao 4)")
    for x in (u, p):
        if type(x.get("k")) is not int or x["k"] < 1:
            raise ValueError(f"config: o K {x.get('k')!r}")
    bases, bases_par = tuple(u["bases"]), tuple(p["bases"])
    if bases and set(bases) <= bv.SEMENTES_TESTE and set(bases_par) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS or not 1 <= p["dias"] <= A0.DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} e {p['dias']} dias: de 1 a {DIAS} e de 1 a {A0.DIAS}")
        return "fumaca"
    if bases != BASES_I or bases_par != BASES_II:
        raise bv.SementeSemPlano("bases fora do plano: so as dos testes (fumaca) ou as da secao 4")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")
    CA.exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS),
                             (f"dias do par {p['dias']} (o plano: {A0.DIAS})", p["dias"] == A0.DIAS),
                             (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K {u['k']} e {p['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE and p["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def conferir_e_apagar(pasta: Path, tar: Path) -> int:
    """secao 4: confere, arquivo a arquivo, que o `.tar.gz` tem os bytes da pasta crua, e so entao apaga a pasta. Falha alto na diferenca."""
    crus = sorted(p for p in pasta.rglob("*") if p.is_file())
    with tarfile.open(tar) as t:
        membros = {m.name: m for m in t.getmembers() if m.isfile()}
        if len(membros) != len(crus):
            raise RuntimeError(f"{tar.name}: {len(membros)} arquivos no pacote, {len(crus)} na pasta")
        for p in crus:
            m = membros.get(f"{pasta.name}/{p.relative_to(pasta).as_posix()}")
            if m is None or t.extractfile(m).read() != p.read_bytes():
                raise RuntimeError(f"{tar.name}: o arquivo {p.relative_to(pasta).as_posix()} falta ou difere da pasta crua")
    shutil.rmtree(pasta)
    return len(crus)


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 4)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    unidades_par = bv.unidades_derivadas(cfg["pares"]["bases"], int(cfg["pares"]["k"]), PREFIXO_PAR)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": V._versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "orquestrador_c3_sha256": rc._sha_arquivo(Path(C3.__file__)),
            "orquestrador_c2_sha256": rc._sha_arquivo(Path(C2.__file__)), "tempo_bem_sha256": rc._sha_arquivo(Path(TB.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "unidades_par": unidades_par, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {k: vars(v) for k, v in C3.montar(b).items()} for b in BRACOS}, "faixa": list(FAIXA), "pisos": PISOS,
            "margem": MARGEM, "alfa": ALFA, "disco_livre_gb": shutil.disk_usage(pasta).free / 2**30,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "corpo.py", "motor_corpo.py", "engine.py", "metrics.py",
                                                                         "mundo.py", "grupo.py")}
            | {f"digibrain/{q.name}": rc._sha_arquivo(q) for q in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(unidades) * len(BRACOS) * len(CELULAS):
        raise RuntimeError(f"{len(registros)} vidas, eram {len(unidades) * len(BRACOS) * len(CELULAS)}")
    t1 = time.perf_counter()
    pares = [r for s in rc._executar([(tarefa_par, (cfg, u, str(pasta))) for u in unidades_par], processos) for r in s]
    meta["pares_parede_s"] = time.perf_counter() - t1
    if len(pares) != len(unidades_par) * len(BRACOS):
        raise RuntimeError(f"{len(pares)} pares, eram {len(unidades_par) * len(BRACOS)}")
    registros.sort(key=lambda r: r["vida"])
    custos = {r["vida"]: r.pop("custo") for r in registros}            # D-C4-8: o relogio fora do medidas.json
    bv._gravar(pasta / "medidas.json", bv._dump(registros))
    bv._gravar(pasta / "custos.json", bv._dump(custos))
    bv._gravar(pasta / "pares.json", bv._dump(sorted(pares, key=lambda r: r["par"])))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    pares_lidos = json.loads((pasta / "pares.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "unidades_par": len(unidades_par),
                 "vidas": len(lidos), "pares": len(pares_lidos), **analisar(lidos, pares_lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    V.tar_deterministico(pasta / "pares", pasta / "pares.tar.gz")
    meta["pasta_crua_apagada"] = {n: conferir_e_apagar(pasta / n, pasta / f"{n}.tar.gz") for n in ("vidas", "pares")}
    nomes = ["medidas.json", "custos.json", "pares.json", "resultado.json", "vidas.tar.gz", "pares.tar.gz"]
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "pares": pares, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "pares": r["pares"], "veredito": r["veredito"],
                       "primaria": {k: {c: v[c] for c in ("media", "ic95", "p_unilateral")} for k, v in r["primaria"].items()}},
                      indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if modo_da_config(cfg) == "fumaca":
        if a.saida is None:
            raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    else:
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)             # o plano da origin/main e a V3-D8, antes de tudo
        livre = shutil.disk_usage(RAIZ).free / 2**30
        if livre < PISO_DISCO_GB:
            raise SystemExit(f"so {livre:.1f} GB livres no disco: o piso e {PISO_DISCO_GB} GB (secao 4)")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
