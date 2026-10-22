"""V3-3/V3-4, a competicao entre as regras urgentes (docs/PLANO_ANALISE_V2_V3_COMPETICAO.md; PC-1 a PC-6 decididas pelo Matheus em
2026-10-21, pela recomendacao; a tarefa: docs/TAREFA_V2_V3_COMPETICAO.md). Pela bancada do v11 (`exportar_gabarito_lobos.bancada_v11`: o
corpo com os drives novos e os gestos, o mundo `padrao`, 14 dias, 16 interacoes por dia), nos 4 donos, com a `ConfigCompeticao` ligada ou
desligada pela `Bancada.cfg_competicao` (o kappa = 16 da CR-2):
    R0       P1-c-tapa, a chave desligada (o A v11)
    R1       P1-c-tapa, a chave ligada
    R1-cong  P0-c-tapa (o mesmo corpo e o mesmo dono, sem aprender), a chave ligada (PC-5)
    P0       P0-c-tapa, a chave desligada (o instinto)

Duas fases, uma config cada (o campo "fase"):
    piloto      bases 58101...58505, K = 4 (secao 6): as margens (PC-2, PC-3), o N (o poder simulado no G-R1), a G-ABRE do piloto e o
                custo. Os numeros dele nao entram como evidencia; vao ao adendo 1 do plano, num commit antes da validacao.
    validacao   bases 59101...59505, o K do adendo 1, uma vez so (a run se recusa a gravar por cima).
Na fumaca (as sementes dos testes) as duas fases rodam sem a faixa nem o adendo; a validacao da fumaca usa as margens da propria fumaca.

Os gates (secao 9; por unidade, a media das 4 celulas; o bootstrap de 10.000 com a semente 4242):
    G-ABRE       a fracao de abertas no R1, limite inferior do IC95 > 0,05 (premissa, PC-4)
    G-R1         D_FE(R0) - D_FE(R1), as categorias da secao 9 com o Delta_R1 (primario, PC-1, PC-2)
    Holm (alfa 0,05) sobre G-R1-CONG (D_FE(R1-cong) - D_FE(R1)), G-NI-PRIV e G-NI-SAUDE (nao inferioridade, PC-3)
Toda vida e gravada e rejogada do disco bit a bit (Bancada.conferir_replay); os gates de mecanismo falham alto em toda vida.

    python experiments/run_v2_competicao.py --config experiments/configs/v2_competicao/piloto.json --processos 8
    python experiments/run_v2_competicao.py --config experiments/configs/v2_competicao/validacao.json --processos 8
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_calibracao_mundo as rc  # noqa: E402
import run_v2_validacao_mundo as rv  # noqa: E402
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA, ConfigCompeticao  # noqa: E402
from digilab.metrics import (JANELA_8_14, competicao_nas_decisoes, contraste_pareado, cuidado_preservado,  # noqa: E402
                             deficit_fome_energia, exaustao_nas_decisoes, holm, janela_dias)
from digilab.state import Estado  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_V3_COMPETICAO.md"
PREFIXO = "competicao"                                       # secao 4
BASES_PILOTO = (58101, 58202, 58303, 58404, 58505)           # secao 11 (CR-6)
BASES_VALIDACAO = (59101, 59202, 59303, 59404, 59505)
K_PILOTO = 4
SAIDA = {"piloto": "artifacts_v2_v3_competicao/piloto", "validacao": "artifacts_v2_v3_competicao/validacao"}
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")  # secao 2: as 4 celulas
DIAS, ORCAMENTO_POR_DIA = 14, 16                             # o v11 do E0 (PC-6)
KAPPA = 16                                                   # CR-2 (a etapa 0, #383)
BRACOS = {"R0": ("P1-c-tapa", False), "R1": ("P1-c-tapa", True), "R1-cong": ("P0-c-tapa", True), "P0": ("P0-c-tapa", False)}
BOOTSTRAP = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}
PODER = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8, "alfa": 0.025, "semente": 4242,
         "alfas_relato": [0.025, 0.0167]}        # secao 7; o relato dos secundarios tambem no alfa mais estrito do Holm de tres
G_ABRE = {"limiar": 0.05}                         # PC-4
HOLM = ("G-R1-CONG", "G-NI-PRIV", "G-NI-SAUDE")
LIMIAR_ESCALA = 0.001                             # PC-2: com D_FE(P0) - D_FE(R0) <= 0,001 no piloto, a margem nao tem escala
CHAVES_CONFIG = {"descricao", "plano", "fase", "unidades", "dias", "orcamento_por_dia", "kappa", "bootstrap", "poder", "g_abre", "holm"}
EXAUSTAO = 0.25                                   # a condicao do sono_exaustao (o PoliticaInstinto)


# ================================================================== a config
def _faixa(bases) -> range:
    return range(bases[0], bases[-1] + 1)


def adendo_do_piloto() -> dict:
    """As margens e o K da validacao: os do piloto (artifacts_v2_v3_competicao/piloto/resultado.json), que o adendo 1 do plano registra."""
    caminho = RAIZ / SAIDA["piloto"] / "resultado.json"
    if not caminho.exists():
        raise FileNotFoundError("a validacao precisa do piloto e do adendo 1 (secao 7): rode o piloto antes")
    if "## Adendo 1" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("o adendo 1 (as margens, o K, o poder, a G-ABRE do piloto e o custo) nao esta no plano: commit antes")
    r = json.loads(caminho.read_text(encoding="utf-8"))
    if r["margens"]["volta_ao_matheus"]:
        raise RuntimeError("PC-2: a margem do primario nao tem escala (o R0 nao ganhou do P0 no piloto); o plano volta ao Matheus")
    return {"k": r["n"]["k"], "margens": r["margens"]}


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes), 'piloto' (58101...58505, K = 4) ou 'validacao' (59101...59505, o K do adendo 1). O piloto
    recusa as bases da validacao; fora dos testes, tudo segue o plano a letra."""
    faltam = CHAVES_CONFIG - {"descricao", "plano"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    fase = cfg["fase"]
    if fase not in SAIDA:
        raise ValueError(f"fase {fase!r}: so {sorted(SAIDA)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    erros = []
    if u.get("prefixo") != PREFIXO:
        erros.append("prefixo")
    if cfg["dias"] != DIAS or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or cfg["kappa"] != KAPPA:
        erros.append("dias, orcamento ou kappa (secao 2, CR-2, PC-6)")
    if cfg["holm"] != {"alfa": 0.05} or cfg["poder"] != PODER or cfg["g_abre"] != G_ABRE or cfg["bootstrap"] != BOOTSTRAP:
        erros.append("holm, poder, g_abre ou bootstrap (secoes 7 a 9)")
    if erros:
        raise ValueError(f"config fora do plano: {erros}")
    if fase == "piloto" and set(bases) & set(_faixa(BASES_VALIDACAO)):
        raise bv.SementeSemPlano("o piloto recusa as sementes da validacao (secao 11)")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    esperadas = BASES_PILOTO if fase == "piloto" else BASES_VALIDACAO
    if bases != esperadas:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(esperadas)} ({fase}, secao 11)")
    k = K_PILOTO if fase == "piloto" else adendo_do_piloto()["k"]
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != k:
        erros.append(f"K {u['k']} (o plano: {k})")
    if erros:
        raise ValueError(f"o {fase} segue o plano a letra: {erros}")
    return fase


# ================================================================== as vidas
_BANCADAS: dict = {}


def bancada(cfg: dict, ligada: bool) -> bv.Bancada:
    """A bancada do v11 com a competicao ligada ou desligada (None: a de hoje, o G2)."""
    chave = (cfg["dias"], cfg["orcamento_por_dia"], cfg["kappa"], ligada)
    if chave not in _BANCADAS:
        b = gl.bancada_v11(cfg["dias"], cfg["orcamento_por_dia"] * cfg["dias"])
        _BANCADAS[chave] = replace(b, cfg_competicao=ConfigCompeticao(ligada=True, kappa_instinto=cfg["kappa"])) if ligada else b
    return _BANCADAS[chave]


def conferir_mecanismo(rotulo: str, ligada: bool, cerebro) -> None:
    """Os gates de mecanismo (secao 8), em toda vida: desligada, nenhuma decisao com `competicao`; ligada, o sono_exaustao forcado (a
    energia < 0,25: dormir, sem sorteio, sem disputa); o R1-cong com os pesos no prior. Falha alto."""
    for m in cerebro.motivos:
        if not ligada and "competicao" in m:
            raise RuntimeError(f"{rotulo}: decisao com competicao com a chave desligada")
        if ligada and m["percepcao"]["energia"] < EXAUSTAO and (m["regra"] != "sono_exaustao" or m["acao"] != "dormir"
                                                                 or m["u"] is not None or "competicao" in m):
            raise RuntimeError(f"{rotulo}: o sono_exaustao nao foi forcado")
    if ligada != ("competicao" in cerebro.estado_interno()):
        raise RuntimeError(f"{rotulo}: o estado interno sem o contador da competicao (ou com ele, desligada)")
    if rotulo == "R1-cong" and cerebro._pesos != cerebro._prior:
        raise RuntimeError("R1-cong: os pesos sairam do prior")


def medidas(cerebro, dias: int) -> dict:
    """As medidas da secao 5, das decisoes do proprio cerebro (o estado de cada decisao e o da `Observacao`, guardado no motivo; a decisao
    k no tick k x intervalo), pelas funcoes de metrics.py, na janela dos dias 8 a 14 (e a vida toda, descritiva)."""
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    ms = cerebro.motivos
    if len(ms) * passo != dias * TICKS_POR_DIA:
        raise RuntimeError(f"{len(ms)} decisoes em {dias} dias: o relogio da decisao nao e k x {passo}")
    ps = [(k * passo, m["percepcao"]) for k, m in enumerate(ms)]
    fe = [(t, p["fome"], p["energia"]) for t, p in ps]
    cuid = [(t, Estado(fome=p["fome"], higiene=p["higiene"], energia=p["energia"]).em_privacao(CONFIG_PADRAO), p["saude"], p["fome"])
            for t, p in ps]
    comp = [(k * passo, len(m["candidatos"]), m.get("competicao")) for k, m in enumerate(ms)]
    ex = [(t, p["energia"]) for t, p in ps]
    vida_toda = janela_dias(1, dias)
    c = cuidado_preservado(cuid, JANELA_8_14)
    return {"d_fe": deficit_fome_energia(fe, JANELA_8_14)["d_fe"], "d_fe_vida": deficit_fome_energia(fe, vida_toda)["d_fe"],
            "privacao": c["privacao"], "saude": c["saude_media"], "fome": c["fome_media"],
            "competicao": competicao_nas_decisoes(comp, JANELA_8_14), "competicao_vida": competicao_nas_decisoes(comp, vida_toda),
            "exaustao": exaustao_nas_decisoes(ex, JANELA_8_14, EXAUSTAO)["frac"],
            "acoes_abertas": dict(sorted(_contar(m["acao"] for m in ms if "competicao" in m).items())),
            "acoes_do_instinto_abertas": dict(sorted(_contar(m["competicao"]["acao_do_instinto"] for m in ms if "competicao" in m).items()))}


def _contar(xs) -> dict:
    out: dict = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


def tarefa_unidade(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    """As 16 vidas de uma unidade (4 bracos x 4 donos): gravadas, rejogadas do disco (G1), conferidas (os gates de mecanismo) e medidas."""
    out = []
    for dono in DONOS:
        for rotulo, (braco, ligada) in BRACOS.items():
            b = bancada(cfg, ligada)
            c0, p0 = time.process_time(), time.perf_counter()
            v = b.vida(bv.EspecVida(dono, braco, unidade["semente"]))
            dir_vidas = Path(pasta) / "vidas" / rotulo
            rc._guardar(b, v, dir_vidas)
            cpu, parede = time.process_time() - c0, time.perf_counter() - p0
            cerebro = bv.do_braco(v.motor.politica).cerebro
            conferir_mecanismo(rotulo, ligada, cerebro)
            out.append({"vida": f"{rotulo}|{v.nome}", "braco": rotulo, "braco_bancada": braco, "competicao_ligada": ligada, "dono": dono,
                        "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **medidas(cerebro, cfg["dias"]),
                        "custo": {"vida_cpu": cpu, "vida_parede": parede}})
    return out


# ================================================================== a analise (funcoes puras)
CATEGORIAS = {"ganha": "a disputa ajuda", "ganha, abaixo de Delta": "a disputa ajuda, abaixo de Delta", "perde": "a disputa atrapalha",
              "equivalente": "equivalente", "inconclusivo": "inconclusivo"}


def por_unidade(registros: list[dict], braco_a: str, braco_b: str, medida, sinal: int = 1) -> dict:
    """{semente: a media, nos 4 donos, de sinal x (a - b)} na medida (secao 4; PC-1). `medida` e o nome do campo ou uma funcao do registro.
    Falta de celula ou valor None falha alto."""
    ler = medida if callable(medida) else (lambda r: r[medida])
    idx = {}
    for r in registros:
        chave = (r["semente"], r["dono"], r["braco"])
        if chave in idx:
            raise RuntimeError(f"vida repetida: {chave}")
        idx[chave] = ler(r)
    out = {}
    for s in sorted({r["semente"] for r in registros}):
        ds = []
        for dono in DONOS:
            a, b = idx.get((s, dono, braco_a)), idx.get((s, dono, braco_b))
            if a is None or b is None:
                raise RuntimeError(f"unidade {s}, dono {dono}: falta {braco_a} ou {braco_b}")
            ds.append(sinal * (a - b))
        out[s] = sum(ds) / len(ds)
    return out


def nivel_por_unidade(registros: list[dict], braco: str, medida) -> dict:
    ler = medida if callable(medida) else (lambda r: r[medida])
    out: dict = {}
    for r in registros:
        if r["braco"] == braco:
            out.setdefault(r["semente"], []).append(ler(r))
    for s, v in out.items():
        if len(v) != len(DONOS):
            raise RuntimeError(f"unidade {s}: {len(v)} donos no {braco}")
    return {s: sum(v) / len(v) for s, v in sorted(out.items())}


def contraste(difs: dict, boot: dict) -> dict:
    return contraste_pareado({s: [d] for s, d in difs.items()}, boot["reamostragens"], boot["semente"])


def _media(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def margens(registros: list[dict]) -> dict:
    """As margens (secao 7), do piloto, sem ler o R1 nem o R1-cong: Delta_R1 = 1/2 [D_FE(P0) - D_FE(R0)] (PC-2); Delta_priv = 1/4 da
    privacao media do P0 e Delta_saude = 1/4 de (1 - a saude media do P0) (PC-3). Com D_FE(P0) - D_FE(R0) <= 0,001, a margem do primario
    nao tem escala, e o plano volta ao Matheus."""
    for r in registros:
        if r["braco"] not in ("P0", "R0"):
            raise RuntimeError(f"as margens nao leem o {r['braco']}")
    ganho = _media(por_unidade(registros, "P0", "R0", "d_fe").values())
    priv = _media(nivel_por_unidade(registros, "P0", "privacao").values())
    saude = _media(nivel_por_unidade(registros, "P0", "saude").values())
    return {"ganho_r0_sobre_p0": ganho, "delta_r1": 0.5 * ganho, "delta_priv": 0.25 * priv, "delta_saude": 0.25 * (1.0 - saude),
            "referencias": {"privacao_p0": priv, "saude_p0": saude}, "volta_ao_matheus": ganho <= LIMIAR_ESCALA}


def g_abre(registros: list[dict], boot: dict, limiar: float) -> dict:
    fr = nivel_por_unidade(registros, "R1", lambda r: r["competicao"]["frac_abertas"])
    r = contraste(fr, boot)
    return {"medida": "a fracao de abertas no R1 (dias 8 a 14), media por unidade", "limiar": limiar, **r,
            "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] > limiar}


def g_r1(registros: list[dict], boot: dict, delta: float) -> dict:
    r = contraste(por_unidade(registros, "R0", "R1", "d_fe"), boot)
    c = rv.categoria_g_mf1(r, delta)
    return {"contraste": "D_FE(R0) - D_FE(R1)", "delta_r1": delta, **r, "categoria": CATEGORIAS[c["categoria"]]}


def nao_inferior(registros: list[dict], pior: str, melhor: str, medida: str, delta: float, boot: dict) -> dict:
    """A nao inferioridade (secao 9): d = medida(pior) - medida(melhor), orientada para "pior"; passa com o superior do IC95 < Delta. O teste
    e o do contraste de Delta - d > 0 (o mesmo bootstrap), e o p dele vai ao Holm."""
    d = por_unidade(registros, pior, melhor, medida)
    r = contraste(d, boot)
    t = contraste({s: delta - x for s, x in d.items()}, boot)
    return {**r, "delta": delta, "orientado": t, "passa_ic": r["ic95"] is not None and r["ic95"]["ic_superior"] < delta}


def descritivos(registros: list[dict]) -> dict:
    out = {}
    for b in BRACOS:
        rs = [r for r in registros if r["braco"] == b]
        out[b] = {
            "d_fe": _media(r["d_fe"] for r in rs), "privacao": _media(r["privacao"] for r in rs), "saude": _media(r["saude"] for r in rs),
            "exaustao": _media(r["exaustao"] for r in rs),
            "frac_forcadas": _media(r["competicao"]["frac_forcadas"] for r in rs),
            "frac_abertas": _media(r["competicao"]["frac_abertas"] for r in rs),
            "por_dono": {d: {"d_fe": _media(r["d_fe"] for r in rs if r["dono"] == d),
                             "frac_abertas": _media(r["competicao"]["frac_abertas"] for r in rs if r["dono"] == d)} for d in DONOS}}
        abertas = [r["competicao"] for r in rs if r["competicao"]["abertas"]]
        out[b]["frac_abertura_decidiu"] = _media(c["frac_abertura_decidiu"] for c in abertas) if abertas else None
        out[b]["frac_aprendido_decidiu"] = _media(c["frac_aprendido_decidiu"] for c in abertas) if abertas else None
    out["r0_menos_r1_por_dono"] = {d: _media(r0["d_fe"] - r1["d_fe"] for r0 in registros for r1 in registros
                                            if r0["braco"] == "R0" and r1["braco"] == "R1" and r0["dono"] == d == r1["dono"]
                                            and r0["semente"] == r1["semente"]) for d in DONOS}
    return out


def leitura(abre: dict, primario: dict, cong_passa: bool, seguranca_passa: bool) -> str:
    if not abre["passa"]:
        return "inconclusivo por premissa: a disputa quase nao aconteceu (G-ABRE)"
    cat = primario["categoria"]
    if cat.startswith("a disputa ajuda"):
        if not seguranca_passa:
            return "o pet melhora num lado e piora no outro (a seguranca falha): registrado como esta"
        return ("a disputa ajuda, e o aprendido usa a abertura" if cong_passa
                else "a disputa ajuda, mas o ganho vem de abrir, nao de aprender")
    if cat == "equivalente":
        return "com o instinto forte, a abertura nao move a homeostase em 14 dias"
    if cat == "a disputa atrapalha":
        return "a disputa atrapalha: os descritivos dizem onde"
    return "inconclusivo: registrado com o poder"


def analisar(registros: list[dict], cfg: dict, mg: dict) -> dict:
    """A validacao (secao 9), com as margens do adendo 1 (na fumaca, as da propria fumaca)."""
    boot = cfg["bootstrap"]
    abre = g_abre(registros, boot, cfg["g_abre"]["limiar"])
    pri = g_r1(registros, boot, mg["delta_r1"])
    sec = {"G-R1-CONG": {"contraste": "D_FE(R1-cong) - D_FE(R1)", "regra": "limite inferior do IC95 > 0",
                         **contraste(por_unidade(registros, "R1-cong", "R1", "d_fe"), boot)},
           "G-NI-PRIV": {"contraste": "privacao(R1) - privacao(R0)", "regra": "superior do IC95 < Delta_priv",
                         **nao_inferior(registros, "R1", "R0", "privacao", mg["delta_priv"], boot)},
           "G-NI-SAUDE": {"contraste": "saude(R0) - saude(R1)", "regra": "superior do IC95 < Delta_saude",
                          **nao_inferior(registros, "R0", "R1", "saude", mg["delta_saude"], boot)}}
    h = holm({n: (sec[n]["orientado"] if "orientado" in sec[n] else sec[n])["p_unilateral"] for n in HOLM}, cfg["holm"]["alfa"])
    for n in HOLM:
        x = sec[n]
        if "orientado" not in x:
            x["passa_ic"] = x["ic95"] is not None and x["ic95"]["ic_inferior"] > 0.0
        x["holm"] = h[n]
        x["passa"] = x["passa_ic"] and h[n]["rejeita"]
    seguranca = sec["G-NI-PRIV"]["passa"] and sec["G-NI-SAUDE"]["passa"]
    return {"G-ABRE": abre, "G-R1": pri, "secundarios": sec, "holm_alfa": cfg["holm"]["alfa"], "holm_familia": list(HOLM),
            "margens": mg, "leitura": leitura(abre, pri, sec["G-R1-CONG"]["passa"], seguranca), "descritivos": descritivos(registros)}


def analisar_piloto(registros: list[dict], cfg: dict) -> dict:
    """O piloto (secoes 6 e 7): as margens (sem ler o R1), o K pelo poder simulado no G-R1 com o Delta_R1 (o bootstrap das diferencas R0 -
    R1 por unidade, centradas e deslocadas para o Delta_R1, 2.000 replicas por K, o teste unilateral a 0,025, semente 4242), o poder dos
    secundarios no N escolhido (so relato), a G-ABRE e o custo. Os contrastes saem so como relato: nao sao evidencia."""
    boot, poder = cfg["bootstrap"], cfg["poder"]
    n_bases = len(cfg["unidades"]["bases"])
    mg = margens([r for r in registros if r["braco"] in ("P0", "R0")])
    if mg["volta_ao_matheus"]:
        n = {"k": None, "n": None, "poder": None, "chega_ao_alvo": False, "motivo": "PC-2: a margem do primario sem escala"}
        relato = {}
    else:
        difs = list(por_unidade(registros, "R0", "R1", "d_fe").values())
        n = rc.escolher_k(difs, mg["delta_r1"], poder, poder["semente"], n_bases)
        relato = {"G-R1-CONG": rc.relato_poder(list(por_unidade(registros, "R1-cong", "R1", "d_fe").values()), mg["delta_r1"], n["n"],
                                               poder, poder["semente"])}
    so_relato = {}
    for nome, a, b, med in (("R0 - R1 em D_FE (G-R1)", "R0", "R1", "d_fe"), ("R1-cong - R1 em D_FE (G-R1-CONG)", "R1-cong", "R1", "d_fe"),
                            ("P0 - R0 em D_FE (a escala da margem)", "P0", "R0", "d_fe"),
                            ("R1 - R0 em privacao", "R1", "R0", "privacao"), ("R0 - R1 em saude", "R0", "R1", "saude")):
        d = por_unidade(registros, a, b, med)
        r = contraste(d, boot)
        vs = list(d.values())
        m = sum(vs) / len(vs)
        dp = (sum((x - m) ** 2 for x in vs) / (len(vs) - 1)) ** 0.5 if len(vs) > 1 else None
        so_relato[nome] = {"media": r["media"], "dp_unidades": dp, "ic95": r["ic95"], "n": r["n"]}
    return {"margens": mg, "n": n, "poder_secundarios": relato, "G-ABRE_piloto": g_abre(registros, boot, cfg["g_abre"]["limiar"]),
            "contrastes_so_relato": so_relato, "descritivos": descritivos(registros), "custo": custo(registros, n["k"], n_bases),
            "aviso": "o piloto serve so para as margens, o N, a G-ABRE e o custo (secao 6): nenhum numero dele e evidencia"}


def custo(registros: list[dict], k: int | None, n_bases: int) -> dict:
    por = {b: _media(r["custo"]["vida_cpu"] for r in registros if r["braco"] == b) for b in BRACOS}
    por_unidade_cpu = sum(por.values()) * len(DONOS)
    return {"cpu_por_vida": por, "cpu_por_unidade": por_unidade_cpu,
            "validacao_estimada": None if k is None else {"k": k, "vidas": n_bases * k * len(DONOS) * len(BRACOS),
                                                         "cpu_s": n_bases * k * por_unidade_cpu}}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 13)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "fase": cfg["fase"], "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "git_head": rc._git("rev-parse", "HEAD"),
            "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "bracos": {k: {"braco": b, "competicao_ligada": l} for k, (b, l) in BRACOS.items()},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "motivo.py")}
            | {"lobos.py": rc._sha_arquivo(RAIZ / "digilab" / "policies" / "lobos.py")},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    if cfg["fase"] == "validacao" and modo == "validacao":
        meta["piloto_resultado_sha256"] = rc._sha_arquivo(RAIZ / SAIDA["piloto"] / "resultado.json")
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    saidas = rc._executar([(tarefa_unidade, (cfg, u, str(pasta))) for u in unidades], processos)
    meta["vidas_parede_s"] = time.perf_counter() - t0
    registros = [r for s in saidas for r in s]
    if cfg["fase"] == "piloto":
        resultado = {"modo": modo, "fase": "piloto", "plano": PLANO, **analisar_piloto(registros, cfg)}
    else:
        mg = adendo_do_piloto()["margens"] if modo == "validacao" else margens([r for r in registros if r["braco"] in ("P0", "R0")])
        resultado = {"modo": modo, "fase": "validacao", "plano": PLANO, **analisar(registros, cfg, mg),
                     "custo": custo(registros, None, len(cfg["unidades"]["bases"]))}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_v3_competicao/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA[cfg["fase"]]
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    if cfg["fase"] == "piloto":
        print(json.dumps({"margens": r["margens"], "n": {k: r["n"].get(k) for k in ("k", "n", "poder", "chega_ao_alvo")},
                          "G-ABRE_piloto": {k: r["G-ABRE_piloto"][k] for k in ("media", "ic95", "passa")},
                          "custo": r["custo"].get("validacao_estimada")}, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"G-ABRE": {k: r["G-ABRE"][k] for k in ("media", "ic95", "passa")},
                          "G-R1": {k: r["G-R1"][k] for k in ("media", "ic95", "ic90", "categoria")},
                          "secundarios": {n: {"passa": g["passa"], "p": g["holm"]["p"]} for n, g in r["secundarios"].items()},
                          "leitura": r["leitura"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
