"""A run do teste de recompensa (docs/PLANO_ANALISE_V3_PET_VIVO_RECOMPENSA.md, APROVADO): o carinho depois do comer e do brincar
deixa o pet mais tempo acordado?

Os quatro bracos do `experiments/recompensa.py` (R0, R-CORPO, R-CB, R-SORT) no pet do v38, nas 12 celulas da C4, 200 unidades
(108001...108200, k = 1), 14 dias: 9 600 vidas, uma vez. As conferencias que falham alto, antes de qualquer medida (secao 5): a C-G1
(o replay pelo log), a C-HOJE (o R0 e o v38 de hoje, byte a byte), a C-CORPO (sem a chave, nenhum credito), a C-HORA (o carinho no
passo da decisao de comer ou brincar, e o credito nela) e a C-MESMO-N (o R-SORT com o numero do R-CB). As premissas (P-EVENTO,
P-DOSE, P-SINAL) ficam registradas e nao param. As regras de leitura (secao 7) estao escritas antes: L-ACORDADO, L-PORQUE e L-BEM.

  python experiments/run_v3_pet_vivo_recompensa.py --config experiments/configs/v3_pet_vivo/recompensa.json --processos 4
  python experiments/run_v3_pet_vivo_recompensa.py --config experiments/configs/v3_pet_vivo/recompensa_fumaca.json --saida <pasta>

A run se recusa a rodar sem o plano APROVADO, sem a faixa em FAIXAS_RESERVADAS, com a pasta de saida existente, sem o `pre_run` e
com menos de 10 GB livres. A fumaca (as sementes dos testes) so serve ao custo: nenhuma medida dela e lida.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import pv2  # noqa: E402
import recompensa as rec  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v3_pet_vivo_ra as ra  # noqa: E402
import run_v3_valuation as V  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_PET_VIVO_RECOMPENSA.md"
ORQUESTRADOR = "experiments/run_v3_pet_vivo_recompensa.py"
STATUS = "**Status: APROVADO pelo Matheus"
FASE = "recompensa"
SAIDA = "artifacts_v3_pet_vivo/recompensa/run"
PREFIXO = orq.PREFIXO
BASES = tuple(range(108001, 108201))                          # RC-6: 200 sementes independentes (secao 4)
FAIXA = (108001, 108200)
K_POR_BASE = 1
DIAS = 14
ORCAMENTO_POR_DIA = orq.ORCAMENTO_POR_DIA
MAX_PROCESSOS = 4                                             # V3-D8
CELULAS = orq.CELULAS                                         # as 12 da C4: 4 donos x 3 lugares
BRACOS = rec.BRACOS
CHAVES_CONFIG = lr.CHAVES_CONFIG
LAMBDA_SONO = CONFIG_DIGIBRAIN_INATOS.lambda_sono
DELTA_A = 0.02                                                # RC-7: o tamanho relevante do T_ACORDADO; PROPOSTO, SEM FONTE
MARGEM_BEM = 0.032                                            # RC-7: a margem do "Tempo bem", a das runs anteriores (D-C4-11)
PISOS = {"carinhos_por_vida_min": 50, "vidas_com_o_piso_min": 0.95, "creditos_movem_min": 0.30}   # secao 5; PROPOSTOS, SEM FONTE
CORTE_CUSTO_H = 4.0                                           # RC-6: a projecao de parede com 4 processos
CONTRASTES = {"D1": ("R-CB", "R0"), "D2": ("R-CB", "R-SORT"), "D3": ("R-CB", "R-CORPO")}
L_DORME = "nao: com a recompensa o pet dorme mais"
L_IGUAL = "nao: fica igual"
L_SIM = "sim, fica mais tempo acordado"
L_INCONCLUSIVO = "inconclusivo"
P_NA_HORA = "pela recompensa na hora, e pelo que o pet aprende"
P_CREDITO = "pelo credito, em qualquer hora"
P_CORPO = "pelo carinho no corpo, e nao pelo que o pet aprende"
B_MELHOR, B_NAO_PIORA, B_PIORA = "o pet fica melhor", "nao piora", "piora"
MEDIDAS = {"t_acordado": lambda r: r["t_acordado"], "t_acordado_8_14": lambda r: r["t_acordado_8_14"],
           "tempo_bem": lambda r: r["tempo_bem"],
           "taxa_por_episodio": lambda r: r["episodios_fome"]["taxa"], "comer": lambda r: r["decisoes_comer"],
           "brincar": lambda r: r["decisoes_brincar"], "F_PESOS_DEC": lambda r: r["sono"]["F_PESOS_DEC"],
           "habito_comer": lambda r: r["habito"]["comer"], "habito_brincar": lambda r: r["habito"]["brincar"]}
# D-RC-15: a saude dos dias 8 a 14 (uma guarda da secao 6) nao e medida por vida: o `medir` nunca a gravou, e a analise da run
# parou nela depois das 9 600 vidas. Ela sai da analise e fica registrada como nao medida; so o replay dos logs a daria.
GUARDAS_NAO_MEDIDAS = ("saude_media",)


class RecompensaDivergiu(RuntimeError):
    """uma conferencia da secao 5 falhou, ou a analise ficou sem o que a regra le"""


# ================================================================== a vida e as conferencias
def conferir_vida(nome: str, braco: str, vida: dict) -> None:
    """C-CORPO e C-HORA numa vida (falha alto)"""
    c, dono = vida["cerebro"], vida["dono"]
    if braco in rec.COM_CREDITO:
        if c.cel != rec.ELOGIO:
            raise RecompensaDivergiu(f"C-CORPO, {nome}: a ConfigElogio do cerebro nao e a do plano")
    elif c.cel is not None or hasattr(c, "elogios"):
        raise RecompensaDivergiu(f"C-CORPO, {nome}: o cerebro tem o credito do carinho sem a chave")
    if braco not in rec.NA_HORA:
        return
    alvos = [k for k, m in enumerate(c.motivos) if m["escolha"][0] in rec.ALVOS]
    if [k for _, k in dono.carinhos] != alvos or any(p != k for p, k in dono.carinhos):
        raise RecompensaDivergiu(f"C-HORA, {nome}: os carinhos nao caem no passo de cada decisao de comer ou brincar")
    if braco == "R-CB":
        creditadas = {cr["decisao"] for e in c.elogios for cr in e["creditos"] if cr["j"] == 0}
        if not set(alvos) <= creditadas:
            raise RecompensaDivergiu(f"C-HORA, {nome}: {len(set(alvos) - creditadas)} decisoes recompensadas sem o credito")


def medir(braco: str, dias: int, vida: dict) -> dict:
    """as medidas de uma vida (secao 6), pelas funcoes do metrics.py"""
    motor, registro, c = vida["motor"], vida["registro"], vida["cerebro"]
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    acoes = [m["escolha"][0] for m in c.motivos]
    dec = [(k * passo, e[0], e[1], e[2]) for k, e in enumerate(registro.estados)]
    tb = met.tempo_bem_nas_decisoes(dec, met.janela_dias(1, dias), orq.LIMIAR_PRIVACAO, orq.LIMIAR_EXAUSTAO)
    por_dia = TICKS_POR_DIA // passo
    sono = met.medidas_caminho_sono(c.motivos, LAMBDA_SONO, passo)
    H = c.m.plast.H
    out = {**orq.medidas(motor, registro, "REL", dias, True),
           "t_acordado": met.tempo_acordado(acoes)["frac"],
           "t_acordado_8_14": met.tempo_acordado(acoes, 7 * por_dia if dias >= 14 else 0)["frac"],
           "tempo_bem": tb["frac"], "privacao_vida": tb["frac_privacao"], "exaustao_vida": tb["frac_exaustao"],
           "decisoes_comer": acoes.count("comer"), "decisoes_brincar": acoes.count("brincar"),
           "sono": {"F_PESOS": sono["F_PESOS"], "F_PESOS_DEC": sono["F_PESOS_DEC"], "decisoes": sono["decisoes"]},
           "habito": {b: sum(H[b]) for b in rec.ALVOS},
           "carinhos_a_mais": 0 if vida["dono"] is None else len(vida["dono"].carinhos),
           "carinhos_do_dono": motor.mudancas if hasattr(motor, "mudancas") else None,
           "credito": met.medidas_carinho(c.elogios) if braco in rec.COM_CREDITO else None}
    return json.loads(json.dumps(out))


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str, sorteados: list[int] | None = None) -> tuple:
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    nome = f"{braco}|{dono}|{lugar}|{semente}"
    vida = rec.viver(braco, dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"], sorteados)
    motor = vida["motor"]
    texto = motor.log.para_jsonl()
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{semente}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, vida["fabricas"], semente, arquivo.read_text(encoding="utf-8"))          # C-G1
    orq.conferir_cenario(motor, vida["registro"])
    if braco == "R0":                                                                                  # C-HOJE
        hoje, _, _ = pv2.viver("HOJE", dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"], v38=True)
        if hoje.log.para_jsonl() != texto:
            raise RecompensaDivergiu(f"C-HOJE, {nome}: o R0 nao e o pet do v38 de hoje")
    conferir_vida(nome, braco, vida)
    out = {"vida": nome, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"], "k": unidade["k"],
           **medir(braco, cfg["dias"], vida)}
    out["custo"] = {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}
    return out, vida


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    """os quatro bracos da unidade nas 12 celulas; o R-SORT depois do R-CB, com o mesmo numero de carinhos a mais (C-MESMO-N)"""
    out = []
    for dono, lugar in CELULAS:
        n_cb = None
        for braco in ("R0", "R-CORPO", "R-CB"):
            r, vida = _vida(cfg, braco, dono, lugar, unidade, pasta)
            if braco == "R-CB":
                n_cb = len(vida["dono"].carinhos)
            out.append(r)
        sorteados = rec.passos_sorteados(n_cb, rec.passos_da_vida(cfg["dias"]), unidade["semente"])
        r, _ = _vida(cfg, "R-SORT", dono, lugar, unidade, pasta, sorteados)
        if r["carinhos_a_mais"] != n_cb:
            raise RecompensaDivergiu(f"C-MESMO-N, {r['vida']}: {r['carinhos_a_mais']} carinhos a mais, o R-CB teve {n_cb}")
        out.append(r)
    return out


# ================================================================== a analise (secoes 5 a 7 do plano, escritas antes)
def _media(xs: list) -> float | None:
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def por_unidade(registros: list[dict], braco: str, medida, celulas) -> dict:
    """semente -> a media da medida nas celulas (None sem valor em nenhuma)"""
    celulas = set(celulas)
    por: dict = {}
    for r in registros:
        if r["braco"] == braco and (r["dono"], r["lugar"]) in celulas:
            por.setdefault(r["semente"], []).append(medida(r))
    return {s: _media(v) for s, v in por.items()}


def contraste(registros: list[dict], a: str, b: str, medida, celulas) -> dict:
    """a - b por unidade (a media das celulas), IC95 pelo t sobre as unidades; as unidades sem valor num dos bracos saem, contadas"""
    va, vb = por_unidade(registros, a, medida, celulas), por_unidade(registros, b, medida, celulas)
    if set(va) != set(vb):
        raise RecompensaDivergiu(f"{a} e {b} com unidades diferentes")
    difs = [va[s] - vb[s] for s in sorted(va) if va[s] is not None and vb[s] is not None]
    ic = met.ic_t(difs)
    return {"a": a, "b": b, "n": ic["n"], "sem_valor": len(va) - len(difs), "media": ic["media"], "dp": ic["dp"],
            "ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"], "motivo": ic["motivo"],
            "media_a": _media(list(va.values())), "media_b": _media(list(vb.values()))}


def premissas(registros: list[dict]) -> dict:
    """P-EVENTO (por celula), P-DOSE e P-SINAL (secao 5), no R-CB"""
    cb = [r for r in registros if r["braco"] == "R-CB"]
    if not cb:
        raise RecompensaDivergiu("nenhuma vida do R-CB")
    evento = {}
    for dono, lugar in CELULAS:
        vs = [r["carinhos_a_mais"] for r in cb if (r["dono"], r["lugar"]) == (dono, lugar)]
        if not vs:
            raise RecompensaDivergiu(f"nenhuma vida do R-CB em {dono}/{lugar}")
        frac = sum(1 for v in vs if v >= PISOS["carinhos_por_vida_min"]) / len(vs)
        evento[f"{dono}|{lugar}"] = {"vidas": len(vs), "minimo": min(vs), "media": sum(vs) / len(vs), "fracao_com_o_piso": frac,
                                    "cumpre": frac >= PISOS["vidas_com_o_piso_min"]}
    creditos = sum(r["credito"]["creditos"] for r in cb)
    movem = sum(r["credito"]["creditos_movem"] for r in cb)
    fracao = None if creditos == 0 else movem / creditos
    negativos = sum(r["credito"]["sinal_negativo"] for r in cb)
    return {"P-EVENTO": {"por_celula": evento, "cumpre": all(v["cumpre"] for v in evento.values()), "pisos": PISOS},
            "P-DOSE": {"creditos": creditos, "movem": movem, "fracao": fracao, "piso": PISOS["creditos_movem_min"],
                       "cumpre": fracao is not None and fracao >= PISOS["creditos_movem_min"]},
            "P-SINAL": {"carinhos": sum(r["credito"]["n"] for r in cb), "sinal_negativo": negativos,
                        "sinal_zero": sum(r["credito"]["sinal_zero"] for r in cb), "cumpre": negativos == 0}}


def ler_acordado(d1: dict) -> dict:
    """L-ACORDADO (secao 7), em ordem, pelo IC95 do D1 no T_ACORDADO"""
    inf, sup = d1["ic_inferior"], d1["ic_superior"]
    if inf is None or sup is None:
        return {"leitura": L_INCONCLUSIVO, "nota": "sem o IC do D1"}
    if sup < 0:
        return {"leitura": L_DORME, "nota": None}
    if -DELTA_A < inf and sup < DELTA_A:
        return {"leitura": L_IGUAL, "nota": "sobe, mas abaixo do relevante" if inf > 0 else None}
    if inf > DELTA_A:
        return {"leitura": L_SIM, "nota": None}
    return {"leitura": L_INCONCLUSIVO, "nota": None}


def ler_porque(acordado: str, d2: dict, d3: dict, dose_cumpre: bool) -> dict:
    """L-PORQUE (secao 7): so se o D1 nao for "fica igual"; com a P-DOSE falha, so a terceira leitura pode sair"""
    if acordado == L_IGUAL:
        return {"leitura": None, "nota": "o D1 e 'fica igual': nao ha o que explicar"}
    if d2["ic_inferior"] is None or d3["ic_inferior"] is None:
        return {"leitura": L_INCONCLUSIVO, "nota": "sem o IC do D2 ou do D3"}
    hora, credito = d2["ic_inferior"] > 0, d3["ic_inferior"] > 0
    if hora and credito:
        texto = P_NA_HORA
    elif credito:
        texto = P_CREDITO
    elif not hora:
        texto = P_CORPO
    else:
        return {"leitura": L_INCONCLUSIVO, "nota": "o D2 acima de 0 e o D3 nao: o plano nao previu este caso"}
    if not dose_cumpre and texto != P_CORPO:
        return {"leitura": L_INCONCLUSIVO, "nota": f"a P-DOSE falhou: '{texto}' nao pode sair"}
    return {"leitura": texto, "nota": None}


def ler_bem(d1: dict) -> dict:
    """L-BEM (secao 7), pelo IC95 do D1 no "Tempo bem" """
    inf, sup = d1["ic_inferior"], d1["ic_superior"]
    if inf is None or sup is None:
        return {"leitura": L_INCONCLUSIVO, "nota": "sem o IC do D1"}
    if inf > 0:
        return {"leitura": B_MELHOR, "nota": None}
    if inf > -MARGEM_BEM:
        return {"leitura": B_NAO_PIORA, "nota": None}
    if sup < -MARGEM_BEM:
        return {"leitura": B_PIORA, "nota": None}
    return {"leitura": L_INCONCLUSIVO, "nota": None}


def analisar(registros: list[dict]) -> dict:
    prem = premissas(registros)
    fora = [c for c in CELULAS if not prem["P-EVENTO"]["por_celula"][f"{c[0]}|{c[1]}"]["cumpre"]]
    celulas = tuple(c for c in CELULAS if c not in fora)
    if not celulas:
        raise RecompensaDivergiu("a P-EVENTO falhou em todas as celulas: nao ha o que ler")
    cont = {m: {d: contraste(registros, a, b, f, celulas) for d, (a, b) in CONTRASTES.items()} for m, f in MEDIDAS.items()}
    acordado = ler_acordado(cont["t_acordado"]["D1"])
    lugares = sorted({c[1] for c in celulas})
    donos = sorted({c[0] for c in celulas})
    recorte = lambda chave, i: {x: {m: {d: contraste(registros, a, b, MEDIDAS[m], tuple(c for c in celulas if c[i] == x))  # noqa: E731
                                        for d, (a, b) in CONTRASTES.items()} for m in ("t_acordado", "tempo_bem")} for x in chave}
    return {"premissas": prem, "celulas_da_leitura": [list(c) for c in celulas], "celulas_fora": [list(c) for c in fora],
            "contrastes": cont, "por_lugar": recorte(lugares, 1), "por_dono": recorte(donos, 0),
            "medias": {b: {m: _media(list(por_unidade(registros, b, f, celulas).values())) for m, f in MEDIDAS.items()} for b in BRACOS},
            "leitura": {"L-ACORDADO": acordado,
                        "L-PORQUE": ler_porque(acordado["leitura"], cont["t_acordado"]["D2"], cont["t_acordado"]["D3"],
                                               prem["P-DOSE"]["cumpre"]),
                        "L-BEM": ler_bem(cont["tempo_bem"]["D1"]),
                        "numeros": {"delta_a": DELTA_A, "margem_bem": MARGEM_BEM},
                        "guardas_nao_medidas": list(GUARDAS_NAO_MEDIDAS),
                        "nao_demonstra": ["nada sobre jogadores: o dono simulado recompensa toda vez e na hora",
                                          "nada sobre outras doses: o resultado vale para g = 2S e W = 1",
                                          "nada sobre outras recompensas (comida a mais, brinquedo, o credito do intervalo)",
                                          "nada sobre o corpo depois da C3 ou da C4, nem sobre o jogo web, nem fora dos 14 dias",
                                          "a separacao entre o credito e o corpo nao e perfeita: os bracos divergem depois do "
                                          "primeiro carinho, e o credito alcanca tambem os carinhos do proprio dono"]}}


# ================================================================== a run
def exigir_aprovado(plano: str) -> None:
    linhas = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not linhas or not linhas[0].startswith(STATUS):
        raise RuntimeError(f"{PLANO} nao esta APROVADO pelo Matheus: {linhas[:1] or 'sem a linha do status'}")


def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K (secao 4)")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases fora do plano: so as dos testes (fumaca) ou {BASES[0]}...{BASES[-1]} (secao 4)")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS), (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K por base {u['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def projecao_h(registros: list[dict], processos: int = MAX_PROCESSOS) -> float:
    """a projecao de parede da run inteira, pelo custo medio por vida dos registros (a fumaca)"""
    por_vida = sum(r["custo"]["vida_parede"] for r in registros) / len(registros)
    return len(BASES) * K_POR_BASE * len(BRACOS) * len(CELULAS) * por_vida / processos / 3600


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez)")
    livre = ra.exigir_disco(RAIZ)
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "recompensa_sha256": rc._sha_arquivo(Path(rec.__file__)),
            "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": list(BRACOS), "faixa": list(FAIXA),
            "config_elogio": asdict(rec.ELOGIO), "alvos": list(rec.ALVOS), "disco_livre_gb": livre,
            "numeros": {"delta_a": DELTA_A, "margem_bem": MARGEM_BEM, "pisos": PISOS, "corte_custo_h": CORTE_CUSTO_H},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "corpo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    bv._gravar(pasta / "medidas.json", bv._dump(sorted(registros, key=lambda r: r["vida"])))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    if modo == "fumaca":                                      # a fumaca so serve ao custo: nenhuma medida dela e lida
        resultado = {"modo": modo, "fase": FASE, "vidas": len(lidos), "conferencias": "passam",
                     "projecao_parede_h_4_processos": projecao_h(lidos), "corte_h": CORTE_CUSTO_H}
    else:
        resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "resultado.json", "vidas.tar.gz")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def reanalisar(pasta: Path) -> dict:
    """a analise sobre as medidas ja gravadas, sem reviver nenhuma vida (D-RC-15): a run viveu as 9 600 vidas, gravou o
    `medidas.json` e parou na analise. Recusa-se com o `resultado.json` presente e com um numero de vidas que nao e o do plano."""
    if (pasta / "resultado.json").exists() or (pasta / "vidas.tar.gz").exists():
        raise FileExistsError(f"{pasta} ja tem o resultado: a analise nao se refaz por cima")
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    if meta["modo"] != FASE or "fim" in meta:
        raise RuntimeError("so a run do plano, parada antes do fim, se reanalisa")
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    esperadas = len(meta["unidades"]) * len(BRACOS) * len(CELULAS)
    if len(lidos) != esperadas or len({r["vida"] for r in lidos}) != esperadas:
        raise RuntimeError(f"{len(lidos)} vidas no medidas.json, eram {esperadas}")
    arquivos = sum(1 for _ in (pasta / "vidas").rglob("*.jsonl"))
    if arquivos != esperadas:
        raise RuntimeError(f"{arquivos} logs em vidas/, eram {esperadas}")
    rc = orq.rc
    resultado = {"modo": FASE, "fase": FASE, "plano": PLANO, "unidades": len(meta["unidades"]), "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    meta["analise_refeita"] = {"motivo": "a analise da run parou num KeyError da guarda saude_media, depois de gravar o medidas.json; "
                                         "nenhuma vida foi revivida (D-RC-15)",
                               "guardas_nao_medidas": list(GUARDAS_NAO_MEDIDAS),
                               "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "git_head": rc._git("rev-parse", "HEAD"),
                               "medidas_gravadas_em": time.strftime("%Y-%m-%dT%H:%M:%S",
                                                                    time.localtime((pasta / "medidas.json").stat().st_mtime))}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "resultado.json", "vidas.tar.gz")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    if r["modo"] == "fumaca":
        return json.dumps(r, indent=1, ensure_ascii=True, default=str)
    d1 = r["contrastes"]["t_acordado"]["D1"]
    return json.dumps({"vidas": r["vidas"], "leitura": {k: v for k, v in r["leitura"].items() if k.startswith("L-")},
                       "D1_t_acordado": [d1["media"], d1["ic_inferior"], d1["ic_superior"]],
                       "premissas": {k: v["cumpre"] for k, v in r["premissas"].items()}}, indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", default=None)
    ap_.add_argument("--reanalisar", default=None, help="a pasta de uma run parada na analise (D-RC-15): nenhuma vida e revivida")
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--processos", type=int, default=1)
    a = ap_.parse_args()
    if a.reanalisar:
        print(_resumo(reanalisar(Path(a.reanalisar))["resultado"]))
        return
    if a.config is None:
        raise SystemExit("falta --config")
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo != "fumaca":
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
