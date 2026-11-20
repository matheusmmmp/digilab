"""V2, MUNDO-ALVO: o mundo fisico com o alvo aprendido (docs/PLANO_ANALISE_V2_MUNDO_ALVO.md; PMA-1 a PMA-9 pela recomendacao,
autorizado pelo Matheus em 2026-10-13). Pela bancada (experiments/bancada_v2.py), no mundo da validacao do J1 (`fisico`, o `m` = 1 da
A1.9, o motor de sempre: a ordem fixa no desempate do cheiro, PMA-8), com o cerebro A do P1 do J1 (T3, montagem completa, canais) e o
corpo desligado (PMA-4). O P1-alvo e esse P1 com ConfigLobos.alvo_aprendido e o w0_alvo padrao (S/16; nada calibrado, PMA-3).

Duas fases, uma config cada (o campo "fase"):
    piloto      bases 47101...47505, K = 4 (secao 6): P0, P0z, P1, P1-alvo, P1^ac e P1-alvo^ac (acoplados ao P0z) nas 12 celulas, 72
                vidas por unidade. So para o N (o poder simulado no G-ALVO com o Delta_MF reaproveitado, PMA-2), o G-USO e o custo; os
                numeros dele nao entram como evidencia. O resultado vai ao adendo 1 do plano, num commit antes da validacao.
    validacao   bases 48101...48505, o K do adendo 1: os mesmos 6 bracos, mais o P1 e o P1-alvo no layout afastado (PMA-6): 96 por
                unidade. Uma vez so; a run se recusa a gravar por cima.
Na fumaca (as sementes dos testes) as duas fases rodam sem a faixa nem o adendo.

Os gates (secao 9; por unidade, a media das 12 celulas; o bootstrap de 10.000 com a semente 4242):
    G-MUNDO      P0z - P0 em D_FE, limite inferior do IC95 > 0 (premissa)
    G-USO        a fracao do G-USO no P1-alvo, limite inferior do IC95 > 0,05 (premissa, PMA-5)
    G-ALVO       P1 - P1-alvo em D_FE, as categorias da secao 9 com o Delta_MF (primario, PMA-1)
    Holm (alfa 0,05) sobre G-ALVO-AC (P1^ac - P1-alvo^ac), G-INSTINTO (P0 - P1-alvo), G-PERM-A e G-DIST-A
Toda vida e gravada e rejogada do disco bit a bit (Bancada.conferir_replay); o replay da medicao tambem confere.

    python experiments/run_v2_mundo_alvo.py --config experiments/configs/v2_mundo_alvo/piloto.json --processos 10
    python experiments/run_v2_mundo_alvo.py --config experiments/configs/v2_mundo_alvo/validacao.json --processos 10
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
import run_v2_calibracao_mundo as rc  # noqa: E402
import run_v2_validacao_mundo as rv  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.metrics import (classes_por_dia, contraste_distancia, holm, inclinacao_permanencia, janela_dias,  # noqa: E402
                             permanencia_media, uso_do_alvo)
from digilab.mundo import reproduzir_mundo  # noqa: E402
from digilab.policies.lobos import ESCALA_U_ALVO, sortear  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_MUNDO_ALVO.md"
PREFIXO = "mundo"                                            # secao 12: o prefixo do plano do mundo (o mundo e o mesmo)
BASES_PILOTO = (47101, 47202, 47303, 47404, 47505)           # secao 12, PMA-7
BASES_VALIDACAO = (48101, 48202, 48303, 48404, 48505)
K_PILOTO = 4
SAIDA = {"piloto": "artifacts_v2_mundo_alvo/piloto", "validacao": "artifacts_v2_mundo_alvo/validacao"}
CALIBRACAO_MUNDO = "artifacts_v2_mundo/calibracao/resultado.json"     # o m e o Delta_MF da A1.9 (PMA-2, PMA-3)
CONFIG_MUNDO = "experiments/configs/v2_mundo/calibracao.json"          # o cerebro do P1 do J1 (secao 2)
MUNDO, MUNDO_AFASTADO = "fisico", "fisico_afastado"
SUFIXO_AFASTADO = rv.SUFIXO_AFASTADO
BRACOS_FECHADOS = ("P0", "P0z", "P1", "P1-alvo")
ACOPLADOS = [{"origem": "P0z", "destino": "P1", "filtro": "nenhum"}, {"origem": "P0z", "destino": "P1-alvo", "filtro": "nenhum"}]
ROT_P1AC, ROT_P1AAC = "P1<P0z:nenhum", "P1-alvo<P0z:nenhum"
BRACOS_AFASTADO = {"piloto": [], "validacao": ["P1", "P1-alvo"]}    # PMA-6: o bloco do afastado fica, so na validacao (secao 6)
PODER = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8, "alfa": 0.025, "semente": 4242,
         "alfas_relato": [0.025, 0.0125]}      # secao 7; o relato do PA-2 e do PA-3 tambem no alfa mais estrito do Holm de quatro
G_USO = {"limiar": 0.05}                       # PMA-5
W0_ALVO_PLANO = 64                             # PMA-3: S/16, o padrao da ConfigLobos
CHAVES_DESLIGADAS = tuple(rc.CHAVES_DESLIGADAS)
HOLM = ("G-ALVO-AC", "G-INSTINTO", "G-PERM-A", "G-DIST-A")
CHAVES_CONFIG = {"descricao", "plano", "fase", "donos", "unidades", "mundo", "mundo_afastado", "lugares", "dias", "orcamento", "ponto",
                 "montagem", "lobos", "consequencia", "sonda", "bootstrap", "m", "delta_mf", "acoplados", "bracos_afastado", "holm",
                 "poder", "g_uso", "chaves_desligadas"}
DESEMPATE_CHEIRO = "a ordem fixa do motor da validacao do J1 (PMA-8; o desempate do #232 nao entra)"


# ================================================================== a config
def _faixa(bases) -> range:
    return range(bases[0], bases[-1] + 1)


def k_do_adendo() -> int:
    """O K da validacao: o do piloto (artifacts_v2_mundo_alvo/piloto/resultado.json), que o adendo 1 do plano registra."""
    caminho = RAIZ / SAIDA["piloto"] / "resultado.json"
    if not caminho.exists():
        raise FileNotFoundError("a validacao precisa do piloto e do adendo 1 (secao 7): rode o piloto antes")
    k = json.loads(caminho.read_text(encoding="utf-8"))["n"]["k"]
    if "## Adendo 1" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("o adendo 1 (o K, o poder, o G-USO do piloto e o custo) nao esta no plano: commit antes da validacao")
    return k


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes), 'piloto' (47101...47505, K = 4) ou 'validacao' (48101...48505, o K do adendo 1). O mundo, o
    cerebro e os numeros da A1.9 sao sempre os do J1. As bases do plano do mundo (31101...32505) nunca; o piloto recusa as da validacao."""
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
    if u.get("prefixo") != PREFIXO or cfg["mundo"] != MUNDO or cfg["mundo_afastado"] != MUNDO_AFASTADO:
        erros.append("prefixo ou mundos")
    if cfg["acoplados"] != ACOPLADOS or cfg["bracos_afastado"] != BRACOS_AFASTADO[fase]:
        erros.append("acoplados ou bloco afastado (secoes 3 e 6, PMA-6)")
    if cfg["holm"] != {"alfa": 0.05} or cfg["poder"] != PODER or cfg["g_uso"] != G_USO:
        erros.append("holm, poder ou g_uso (secoes 7 e 9)")
    if set(cfg["chaves_desligadas"]) != set(CHAVES_DESLIGADAS):
        erros.append("chaves_desligadas")
    if set(cfg["donos"]) - set(rc.DONOS_V1) or set(cfg["lugares"]) - set(rc.LUGARES) or not cfg["donos"] or not cfg["lugares"]:
        erros.append("donos ou lugares")
    cal = json.loads((RAIZ / CALIBRACAO_MUNDO).read_text(encoding="utf-8"))
    if cfg["m"] != cal["m_escolhido"] or cfg["delta_mf"] != cal["delta_mf"]:
        erros.append("m ou Delta_MF diferentes dos da A1.9 (PMA-2, PMA-3)")
    calcfg = json.loads((RAIZ / CONFIG_MUNDO).read_text(encoding="utf-8"))
    for k in ("ponto", "montagem", "lobos", "consequencia", "sonda"):
        if cfg[k] != calcfg[k]:
            erros.append(f"{k} diferente do P1 do J1 (secao 2)")
    if erros:
        raise ValueError(f"config fora do plano: {erros}")
    proibidas = set(rc.BASES_CALIBRACAO) | set(rc.BASES_VALIDACAO)
    if set(bases) & (set(_faixa(rc.BASES_CALIBRACAO)) | set(_faixa(rc.BASES_VALIDACAO)) | proibidas):
        raise bv.SementeSemPlano("as bases do plano do mundo (31101...32505) ja foram usadas; este plano usa 47101... e 48101...")
    if fase == "piloto" and set(bases) & set(_faixa(BASES_VALIDACAO)):
        raise bv.SementeSemPlano("o piloto recusa as sementes da validacao (secao 14)")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    esperadas = BASES_PILOTO if fase == "piloto" else BASES_VALIDACAO
    if bases != esperadas:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(esperadas)} ({fase}, secao 12)")
    k = K_PILOTO if fase == "piloto" else k_do_adendo()
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != k:
        erros.append(f"K {u['k']} (o plano: {k})")
    if tuple(sorted(cfg["donos"])) != tuple(sorted(rc.DONOS_V1)) or tuple(cfg["lugares"]) != rc.LUGARES:
        erros.append("donos ou lugares")
    if cfg["dias"] != rc.DIAS_PLANO or cfg["orcamento"] != rc.ORCAMENTO_PLANO:
        erros.append("dias ou orcamento")
    if cfg["bootstrap"] != {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}:
        erros.append("bootstrap (secao 8)")
    if erros:
        raise ValueError(f"o {fase} segue o plano a letra: {erros}")
    return fase


def config_bancada(cfg: dict) -> dict:
    out = {"bracos": list(BRACOS_FECHADOS), "donos": list(cfg["donos"]), "unidades": dict(cfg["unidades"]),
           "mundos": [cfg["mundo"]] + ([cfg["mundo_afastado"]] if cfg["bracos_afastado"] else []), "lugares": list(cfg["lugares"]),
           "dias": cfg["dias"], "orcamento": cfg["orcamento"], "ponto": cfg["ponto"], "montagem": cfg["montagem"],
           "lobos": dict(cfg["lobos"]), "consequencia": dict(cfg["consequencia"]), "sonda": dict(cfg["sonda"]),
           "bootstrap": dict(cfg["bootstrap"]), "mundo": {"mult_queda": cfg["m"]}, "acoplados": [dict(a) for a in cfg["acoplados"]]}
    if cfg.get("plano"):
        out["plano"] = cfg["plano"]
    return bv.validar_config(out)


def conferir_cerebros(b: bv.Bancada, cb: dict, unidade: dict) -> dict:
    """As chaves desligadas no P0, no P0z e no P1 (as do J1) e, no P1-alvo, so o alvo aprendido ligado, com o w0_alvo padrao (PMA-3), sem
    as classes por arvore, as entradas sociais, o modelo dos outros e a presenca da fruta; o corpo desligado (PMA-4). Falha alto."""
    out = rc.conferir_desligadas(b, cb, unidade)
    espec = bv.EspecVida(cb["donos"][0], "P1-alvo", unidade["semente"], unidade["genoma"], MUNDO, lugar=cb["lugares"][0])
    if b.cfg_corpo_de(espec) is not None or b.cfg_banheiro_de(espec) is not None:
        raise RuntimeError("P1-alvo: a bancada monta o corpo ou o banheiro")
    cer = bv.do_braco(b.politica(espec)).cerebro
    cl = cer.cl
    ligadas = [k for k in ("alvo_por_arvore", "entradas_sociais", "modelo_outros", "presenca_fruta_mundo") if getattr(cl, k)]
    if not cl.alvo_aprendido or ligadas or cl.w0_alvo != W0_ALVO_PLANO:
        raise RuntimeError(f"P1-alvo: alvo_aprendido {cl.alvo_aprendido}, w0_alvo {cl.w0_alvo}, ligadas {ligadas}")
    p1 = bv.do_braco(b.politica(bv.EspecVida(cb["donos"][0], "P1", unidade["semente"], unidade["genoma"], MUNDO,
                                             lugar=cb["lugares"][0]))).cerebro
    if p1.cl != replace(cl, alvo_aprendido=False):
        raise RuntimeError("o P1-alvo nao e o P1 com so a chave do alvo")
    out["P1-alvo"] = {"alvo_aprendido": True, "w0_alvo": cl.w0_alvo, "pesos": cer.n_pesos(), "teto_pesos": cl.maximo_pesos}
    out["P1"]["pesos"] = p1.n_pesos()
    return out


# ================================================================== o alvo (G-USO e os descritivos da secao 5)
def decisoes_com_alvo(vida: bv.VidaBancada) -> list[dict]:
    """As decisoes com alvo aprendido de uma vida (o motivo de cada decisao, com o tick do registro do mundo): a classe escolhida, a do
    padrao, a do prior com o mesmo u (secao 5: todas as classes em w0_alvo, mais 1 na do padrao) e a acao. Falha alto se o motivo e o
    registro do mundo nao tem o mesmo numero de decisoes, ou se falta o u."""
    cer = bv.do_braco(vida.motor.politica).cerebro
    if not cer.cl.alvo_aprendido:
        raise ValueError(f"{vida.nome}: o cerebro nao tem o alvo aprendido")
    motivos, regs = cer.motivos, vida.motor.decisoes_mundo
    if len(motivos) != len(regs):
        raise RuntimeError(f"{vida.nome}: {len(motivos)} motivos e {len(regs)} decisoes no registro do mundo")
    S, w0 = cer.cl.escala, cer.cl.w0_alvo
    out = []
    for mot, reg in zip(motivos, regs):
        al = mot.get("alvo_aprendido")
        if al is None or al["alvo"] is None:
            continue
        if mot["acao"] != reg["acao"]:
            raise RuntimeError(f"{vida.nome}: o motivo e o registro do mundo discordam no tick {reg['tick']}")
        u = mot["mundo"]["u"]
        classes = al["classes"]
        prior = [max(0, w0) / S + (1.0 if c == al["padrao"] else 0.0) for c in classes]
        out.append({"tick": reg["tick"], "acao": mot["acao"], "alvo": al["alvo"], "padrao": al["padrao"],
                    "prior": classes[sortear(prior, u / ESCALA_U_ALVO)], "classes": list(classes)})
    return out


def tabela_alvo_por_dia(b: bv.Bancada, vida: bv.VidaBancada, dias: int) -> list[dict]:
    """Os pesos do alvo aprendido no fim de cada dia (secao 5, descritivo): um replay da vida que guarda a tabela antes da primeira
    decisao de cada dia novo; o fim do ultimo dia e o fim da vida. O replay e conferido contra a vida (falha alto)."""
    fab, fm = b.fabrica_politica(vida.espec), b.fabrica_motor(vida.espec)
    est: dict = {"motor": None, "dia": 1, "serie": []}

    def fm_com_gancho(politica, cfg, semente):
        m = fm(politica, cfg, semente)
        est["motor"] = m
        cer = bv.do_braco(m.politica).cerebro
        agir = cer.agir

        def agir_e_guardar(obs, rng):
            t = est["motor"]._estado.tick
            while est["dia"] * TICKS_POR_DIA <= t:
                est["serie"].append({k: dict(v) for k, v in cer._pesos_alvo_mundo.items()})
                est["dia"] += 1
            return agir(obs, rng)
        cer.agir = agir_e_guardar
        return m

    r = reproduzir_mundo(vida.motor.log, fab, semente=vida.espec.semente, fabrica_motor=fm_com_gancho)
    if bv._interno(r) != bv._interno(vida.motor) or bv.resumo_motor(r) != bv.resumo_motor(vida.motor):
        raise bv.ReplayDivergiu(f"{vida.nome}: o replay da tabela do alvo diverge da vida")
    final = {k: dict(v) for k, v in bv.do_braco(r.politica).cerebro._pesos_alvo_mundo.items()}
    serie = est["serie"][:dias]
    while len(serie) < dias:
        serie.append(final)
    return serie


def janela_da_vida(dias: int) -> tuple[int, int]:
    """Os ultimos sete dias (os dias 8 a 14 numa vida de 14; secao 5), como as medidas do mundo da bancada."""
    return janela_dias(max(1, dias - 6), dias)


def medidas_alvo(b: bv.Bancada, vida: bv.VidaBancada, dias: int, tabela: bool) -> dict:
    ds = decisoes_com_alvo(vida)
    uso = uso_do_alvo([(d["tick"], d["alvo"], d["prior"]) for d in ds], janela_da_vida(dias))
    out = {"g_uso": uso, "decisoes_com_alvo_vida": len(ds),
           "fora_do_padrao": sum(1 for d in ds if d["alvo"] != d["padrao"]),
           "classes_por_dia": classes_por_dia([(d["tick"], d["acao"], d["alvo"]) for d in ds])}
    if tabela:
        out["tabela_por_dia"] = tabela_alvo_por_dia(b, vida, dias)
    return out


# ================================================================== as vidas (um processo por unidade)
_BANCADAS: dict = {}


def _bancada(cfg: dict) -> bv.Bancada:
    chave = json.dumps(cfg, sort_keys=True)
    if chave not in _BANCADAS:
        _BANCADAS[chave] = bv.bancada_da_config(config_bancada(cfg))
    return _BANCADAS[chave]


def tarefa_unidade(cfg: dict, unidade: dict, pasta: str) -> tuple[dict, dict]:
    """As vidas de uma unidade (72 no piloto, 96 na validacao): gravadas, rejogadas do disco e medidas (em cada layout o P0 primeiro: o
    piso do acerto da celula; no afastado, sem P0, o piso e o da propria vida)."""
    b = _bancada(cfg)
    dir_vidas = Path(pasta) / "vidas"
    completas, compactas = {}, {}
    for dono in cfg["donos"]:
        for lugar in cfg["lugares"]:
            feitas = []          # (vida, cpu, parede, rotulo, layout)

            def vida(braco, mundo, rotulo):
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.vida(bv.EspecVida(dono, braco, unidade["semente"], unidade["genoma"], mundo, lugar=lugar))
                rc._guardar(b, v, dir_vidas)
                feitas.append((v, time.process_time() - c0, time.perf_counter() - p0, rotulo, mundo))
                return v

            z = None
            for braco in BRACOS_FECHADOS:
                v = vida(braco, cfg["mundo"], braco)
                if braco == "P0z":
                    z = v
            for a in cfg["acoplados"]:
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.acoplar(z, a["destino"], a["filtro"])
                rc._guardar(b, v, dir_vidas)
                feitas.append((v, time.process_time() - c0, time.perf_counter() - p0, v.rotulo_braco, cfg["mundo"]))
            for braco in cfg["bracos_afastado"]:
                vida(braco, cfg["mundo_afastado"], braco + SUFIXO_AFASTADO)
            pisos = {}
            for v, cv, pv, rotulo, mundo in sorted(feitas, key=lambda f: f[3] != "P0"):
                med, cm, pm = rc._cronometrar(b.medir, v, cfg["sonda"], pisos.get(mundo))
                if rotulo == "P0":
                    pisos[mundo] = med["acerto_total"]
                med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
                tempo = {"vida_cpu": cv, "vida_parede": pv, "medir_cpu": cm, "medir_parede": pm}
                if rotulo.startswith("P1-alvo"):
                    al, ca, pa = rc._cronometrar(medidas_alvo, b, v, cfg["dias"], rotulo == "P1-alvo")
                    med["alvo"] = al
                    tempo.update({"alvo_cpu": ca, "alvo_parede": pa})
                completas[v.nome] = med
                r = rv.compacta(med, unidade, cfg["m"], tempo, rotulo)
                if "alvo" in med:
                    r["alvo"] = {k: med["alvo"][k] for k in ("g_uso", "decisoes_com_alvo_vida", "fora_do_padrao", "classes_por_dia")}
                    if "tabela_por_dia" in med["alvo"]:
                        r["alvo"]["tabela_por_dia"] = med["alvo"]["tabela_por_dia"]
                compactas[v.nome] = r
    return completas, compactas


# ================================================================== a analise (funcoes puras)
CATEGORIAS = {"ganha": "o alvo ajuda", "ganha, abaixo de Delta": "o alvo ajuda, abaixo de Delta", "perde": "o alvo atrapalha",
              "equivalente": "equivalente", "inconclusivo": "inconclusivo"}


def categoria_g_alvo(r: dict, delta: float) -> dict:
    """As categorias do G-ALVO (secao 9), exclusivas e nesta ordem: ajuda (limite inferior do IC95 > 0; "abaixo de Delta" se o
    superior do IC90 < Delta), atrapalha (superior do IC95 < 0), equivalente (o IC90 inteiro em (-Delta, +Delta)), inconclusivo. A
    mesma regra do G-MF1r do plano do mundo (rv.categoria_g_mf1), com os nomes deste plano."""
    c = rv.categoria_g_mf1(r, delta)
    return {**c, "categoria": CATEGORIAS[c["categoria"]]}


def _por_unidade_braco(registros: list[dict], rotulo: str) -> dict:
    out: dict = {}
    for r in registros:
        if r["braco"] == rotulo:
            out.setdefault(r["semente"], []).append(r)
    return out


def g_uso(registros: list[dict], boot: dict, limiar: float) -> dict:
    """G-USO (secao 9): por unidade, a media das 12 celulas da fracao do P1-alvo; passa com o limite inferior do IC95 > limiar. As
    celulas sem decisao com alvo na janela ficam fora da media, contadas."""
    por, sem = {}, 0
    for s, rs in sorted(_por_unidade_braco(registros, "P1-alvo").items()):
        fr = [r["alvo"]["g_uso"]["fracao"] for r in rs]
        sem += sum(1 for f in fr if f is None)
        fr = [f for f in fr if f is not None]
        if fr:
            por[s] = sum(fr) / len(fr)
    r = rc.contraste(por, boot)
    dec = [r2["alvo"]["g_uso"]["decisoes"] for rs in _por_unidade_braco(registros, "P1-alvo").values() for r2 in rs]
    return {"medida": "fracao das decisoes com alvo, nos ultimos 7 dias do P1-alvo, em que o alvo difere do prior com o mesmo u",
            "limiar": limiar, **r, "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] > limiar,
            "celulas_sem_decisao": sem, "decisoes_por_vida": rv._media(dec)}


def dif_inclinacoes(registros: list[dict], a: str, b: str, sobre: str, sinal: int, boot: dict) -> dict:
    """a - b nas inclinacoes da permanencia sobre `sobre`, por unidade, com as visitas das 12 celulas juntas (A1.8 do plano do mundo);
    o contraste e orientado (`sinal` x (a - b), positivo = a direcao predita). As unidades sem inclinacao num dos bracos ficam fora."""
    ia, ib = rv.inclinacoes_por_unidade(registros, a, sobre), rv.inclinacoes_por_unidade(registros, b, sobre)
    difs, sem = {}, []
    for s in sorted(set(ia) | set(ib)):
        x, y = ia.get(s, {}).get("inclinacao"), ib.get(s, {}).get("inclinacao")
        if x is None or y is None:
            sem.append(s)
            continue
        difs[s] = x - y
    r = rc.contraste({s: sinal * d for s, d in difs.items()}, boot)
    return {f"{a} - {b}": {"media": sum(difs.values()) / len(difs) if difs else None, "ic95": rv._desorientar(r["ic95"], sinal),
                           "ic90": rv._desorientar(r["ic90"], sinal)},
            "orientado": r, "sem_valor": len(sem), "n": len(difs),
            "inclinacao_media": {a: rv._media([x["inclinacao"] for x in ia.values()]),
                                 b: rv._media([x["inclinacao"] for x in ib.values()])}}


def g_dist_a(registros: list[dict], boot: dict) -> dict:
    """G-DIST-A (secao 9): [P1-alvo(afastado) - P1-alvo(padrao)] - [P1(afastado) - P1(padrao)] na permanencia media das visitas das 12
    celulas juntas (metrics.contraste_distancia). As unidades sem valor ficam fora, contadas."""
    rots = ("P1", "P1-alvo", "P1" + SUFIXO_AFASTADO, "P1-alvo" + SUFIXO_AFASTADO)
    perm = {rot: {s: permanencia_media([v for r in rs for v in r["visitas_lista"]]) for s, rs in _por_unidade_braco(registros, rot).items()}
            for rot in rots}
    difs, sem = {}, 0
    for s in sorted(perm["P1"]):
        d = contraste_distancia(perm["P1-alvo" + SUFIXO_AFASTADO].get(s), perm["P1-alvo"].get(s), perm["P1" + SUFIXO_AFASTADO].get(s),
                                perm["P1"].get(s))
        if d is None:
            sem += 1
        else:
            difs[s] = d
    return {**rc.contraste(difs, boot), "sem_valor": sem, "permanencia_media": {k: rv._media(list(v.values())) for k, v in perm.items()}}


def razao_abandono(registros: list[dict], boot: dict) -> dict:
    """A taxa no abandono (A1.8 do plano do mundo, so descritiva): P1-alvo - P1 na media das razoes por unidade."""
    por = {rot: {s: rv._media([x for r in rs for x in r["razoes_abandono"]]) for s, rs in _por_unidade_braco(registros, rot).items()}
           for rot in ("P1", "P1-alvo")}
    difs = {s: por["P1-alvo"][s] - por["P1"][s] for s in por["P1"] if por["P1"][s] is not None and por["P1-alvo"].get(s) is not None}
    return {"P1": rv._media(list(por["P1"].values())), "P1-alvo": rv._media(list(por["P1-alvo"].values())),
            "p1alvo_menos_p1": rc.contraste(difs, boot), "sem_valor": len(por["P1"]) - len(difs)}


def descritivos_alvo(registros: list[dict]) -> dict:
    """As classes escolhidas (a fracao de cada classe, por acao e por dia, juntando as vidas do P1-alvo) e os pesos do alvo no fim de
    cada dia (a media das vidas, por regra:acao e classe)."""
    rs = [r for r in registros if r["braco"] == "P1-alvo"]
    cont: dict = {}
    for r in rs:
        for acao, por_dia in r["alvo"]["classes_por_dia"].items():
            for dia, c in por_dia.items():
                alvo = cont.setdefault(acao, {}).setdefault(dia, {})
                for classe, f in c["fracao"].items():
                    alvo[classe] = alvo.get(classe, 0) + f * c["n"]
    classes = {a: {d: {"n": round(sum(cs.values())), "fracao": {k: v / sum(cs.values()) for k, v in sorted(cs.items())}}
                   for d, cs in sorted(por.items(), key=lambda x: int(x[0]))} for a, por in sorted(cont.items())}
    tab: dict = {}
    com_tabela = [r for r in rs if "tabela_por_dia" in r["alvo"]]
    for r in com_tabela:
        for d, t in enumerate(r["alvo"]["tabela_por_dia"], start=1):
            for chave, pesos in t.items():
                for classe, w in pesos.items():
                    tab.setdefault(str(d), {}).setdefault(chave, {}).setdefault(classe, []).append(w)
    pesos = {d: {ch: {c: sum(ws) / len(ws) for c, ws in sorted(cs.items())} for ch, cs in sorted(t.items())}
             for d, t in sorted(tab.items(), key=lambda x: int(x[0]))}
    fora = sum(r["alvo"]["fora_do_padrao"] for r in rs)
    total = sum(r["alvo"]["decisoes_com_alvo_vida"] for r in rs)
    return {"classes_escolhidas": classes, "pesos_fim_do_dia_media": pesos, "vidas_com_tabela": len(com_tabela),
            "fora_do_padrao_na_vida": {"decisoes": total, "fora": fora, "fracao": fora / total if total else None}}


def niveis(registros: list[dict]) -> dict:
    out = {}
    for rotulo in sorted({r["braco"] for r in registros}):
        rs = [r for r in registros if r["braco"] == rotulo]
        out[rotulo] = {k: rv._media([r[k] for r in rs]) for k in ("d_fe", "d_fe_vida", "privacao_janela", "consumos", "visitas",
                                                                 "horas_acordado", "permanencia_media")}
        out[rotulo]["vidas"] = len(rs)
    return out


def por_dono_e_lugar(registros: list[dict], celulas: list, boot: dict) -> dict:
    """P1 - P1-alvo em D_FE por dono e por lugar (secao 5, so descritivo; R-4)."""
    out = {}
    for chave, i in (("dono", 0), ("lugar", 1)):
        for x in sorted({c[i] for c in celulas}):
            cel = [c for c in celulas if c[i] == x]
            r = rc.contraste(rc.por_unidade(registros, "P1", "P1-alvo", "d_fe", cel), boot)
            out.setdefault(chave, {})[x] = {"media": r["media"], "ic95": r["ic95"]}
    return out


def custo(registros: list[dict], k: int | None, n_bases: int, n_celulas: int, processos: int) -> dict:
    """O custo medido por vida e braco (CPU e parede: a vida com a gravacao e o replay do disco, a medicao e, no P1-alvo, as medidas do
    alvo) e a estimativa da validacao no K: 72 vidas por unidade mais o bloco afastado (P1 e P1-alvo), este pelo custo deles no padrao."""
    por = {}
    for r in registros:
        c = por.setdefault(r["braco"], {"vidas": 0, "cpu_s": 0.0, "parede_s": 0.0})
        t = r["tempo"]
        c["vidas"] += 1
        c["cpu_s"] += t["vida_cpu"] + t["medir_cpu"] + t.get("alvo_cpu", 0.0)
        c["parede_s"] += t["vida_parede"] + t["medir_parede"] + t.get("alvo_parede", 0.0)
    for c in por.values():
        c["cpu_s_por_vida"] = c["cpu_s"] / c["vidas"]
        c["parede_s_por_vida"] = c["parede_s"] / c["vidas"]
    out = {"por_braco": por, "cpu_s_total": sum(c["cpu_s"] for c in por.values())}
    fechados = list(BRACOS_FECHADOS) + [ROT_P1AC, ROT_P1AAC]
    if k is not None and all(b in por for b in fechados):
        n = n_bases * k
        base = sum(por[b]["cpu_s_por_vida"] for b in fechados) * n_celulas * n
        afastado = sum(por[b]["cpu_s_por_vida"] for b in ("P1", "P1-alvo")) * n_celulas * n
        out["validacao_estimada"] = {"k": k, "n": n, "vidas": n * n_celulas * (len(fechados) + 2),
                                     "cpu_h": (base + afastado) / 3600,
                                     "parede_h_em_processos": {"processos": processos, "h": (base + afastado) / 3600 / processos}}
    return out


def leitura(g_mundo: dict, uso: dict, g_alvo: dict, ac_passa: bool) -> str:
    """A tabela de leitura da secao 9."""
    if not g_mundo["passa"]:
        return "G-MUNDO falha: explorar nao compensou nesta run; o G-ALVO e inconclusivo por premissa, e o P1 e o P1-alvo nao sao lidos."
    c = g_alvo["categoria"]
    aviso = "" if uso["passa"] else " Aviso: o G-USO falha (a categoria fica, com o aviso)."
    if c.startswith("o alvo ajuda"):
        if ac_passa:
            return ("aprender para onde ir ajuda a procurar, e o ganho e do pet: aparece tambem com o cuidado fixo. O G-INSTINTO diz se "
                    "basta para passar o instinto." + aviso)
        return ("o alvo ajuda, mas o ganho pode vir do dono reagindo ao que o P1-alvo faz: o G-ALVO-AC nao passa (registrado ao lado, "
                "sem trocar a categoria)." + aviso)
    if c == "o alvo atrapalha":
        return "o alvo atrapalha: registrado. Os descritivos das classes dizem para onde o alvo levou o pet." + aviso
    if uso["passa"]:
        return (f"G-ALVO {c}, com o G-USO passando: o pet usou o alvo e nao procurou melhor. Aponta para o credito entre decisoes "
                "(secao 11) e para o pet que planeja (J5).")
    return (f"G-ALVO {c}, com o G-USO falhando: o alvo nao foi usado (o aprendiz nao tirou o alvo do prior). Nao diz nada sobre aprender "
            "para onde ir.")


def _gates_comuns(fech: list[dict], celulas: list, cfg: dict) -> dict:
    boot, delta = cfg["bootstrap"], cfg["delta_mf"]
    gm = rc.contraste(rc.por_unidade(fech, "P0z", "P0", "d_fe", celulas), boot)
    g_mundo = {"contraste": "P0z - P0 em D_FE", **gm, "passa": gm["ic95"] is not None and gm["ic95"]["ic_inferior"] > 0.0}
    ga = rc.contraste(rc.por_unidade(fech, "P1", "P1-alvo", "d_fe", celulas), boot)
    g_alvo = {"contraste": "P1 - P1-alvo em D_FE", "delta_mf": delta, **ga, **categoria_g_alvo(ga, delta)}
    return {"G-MUNDO": g_mundo, "G-USO": g_uso(fech, boot, cfg["g_uso"]["limiar"]), "G-ALVO": g_alvo}


def analisar(registros: list[dict], cfg: dict) -> dict:
    """A validacao (secao 9)."""
    celulas = [(d, lg) for d in cfg["donos"] for lg in cfg["lugares"]]
    boot = cfg["bootstrap"]
    fech = [r for r in registros if r["mundo"] == cfg["mundo"]]
    g = _gates_comuns(fech, celulas, cfg)
    sec = {
        "G-ALVO-AC": {"contraste": "P1^ac - P1-alvo^ac em D_FE", "regra": "limite inferior do IC95 > 0",
                      **rc.contraste(rc.por_unidade(fech, ROT_P1AC, ROT_P1AAC, "d_fe", celulas), boot)},
        "G-INSTINTO": {"contraste": "P0 - P1-alvo em D_FE", "regra": "limite inferior do IC95 > 0",
                       **rc.contraste(rc.por_unidade(fech, "P0", "P1-alvo", "d_fe", celulas), boot)},
        "G-PERM-A": {"contraste": "inclinacao da permanencia sobre o custo de viagem, P1-alvo - P1", "regra": "limite inferior do IC95 > 0",
                     "declarado": "sem Delta nem poder (secao 7)", **dif_inclinacoes(fech, "P1-alvo", "P1", "custo_viagem", 1, boot)},
    }
    if cfg["bracos_afastado"]:
        sec["G-DIST-A"] = {"contraste": "[P1-alvo(afastado) - P1-alvo(padrao)] - [P1(afastado) - P1(padrao)] na permanencia media",
                           "regra": "limite inferior do IC95 > 0", "declarado": "sem Delta nem poder (secao 7)",
                           **g_dist_a(registros, boot)}
    familia = [n for n in HOLM if n in sec]

    def p_de(n):
        x = sec[n]
        return (x["orientado"] if "orientado" in x else x)["p_unilateral"]

    h = holm({n: p_de(n) for n in familia}, cfg["holm"]["alfa"])
    for n in familia:
        x = sec[n]
        ic = (x["orientado"] if "orientado" in x else x)["ic95"]
        x["passa_ic"] = ic is not None and ic["ic_inferior"] > 0.0
        x["holm"] = h[n]
        x["passa"] = x["passa_ic"] and h[n]["rejeita"]
    nao_rodados = [n for n in HOLM if n not in sec]
    return {**g, "secundarios": sec, "holm_alfa": cfg["holm"]["alfa"], "holm_familia": familia, "nao_rodados": nao_rodados,
            "leitura": leitura(g["G-MUNDO"], g["G-USO"], g["G-ALVO"], sec["G-ALVO-AC"]["passa"]),
            "p1_lido": g["G-MUNDO"]["passa"],
            "descritivos": {"niveis": niveis(registros), "alvo": descritivos_alvo(fech),
                            "g_oport": {"contraste": "inclinacao da permanencia sobre a taxa recente, P1-alvo - P1", "so_descritivo": True,
                                        **dif_inclinacoes(fech, "P1-alvo", "P1", "taxa_recente", 1, boot)},
                            "taxa_no_abandono": razao_abandono(fech, boot),
                            "p1_menos_p1alvo_por_dono_e_lugar": por_dono_e_lugar(fech, celulas, boot)},
            "desempate_cheiro": DESEMPATE_CHEIRO}


def analisar_piloto(registros: list[dict], cfg: dict, processos: int) -> dict:
    """O piloto (secoes 6 e 7): o K pelo poder simulado no G-ALVO com o Delta_MF (o bootstrap das diferencas P1 - P1-alvo por unidade,
    centradas e deslocadas para o Delta_MF, 2.000 replicas por K, o teste t unilateral a 0,025, semente 4242), o poder do PA-2 e do
    PA-3 no N escolhido (so relato), o G-USO e o custo. Os contrastes saem so como relato: nao sao evidencia."""
    celulas = [(d, lg) for d in cfg["donos"] for lg in cfg["lugares"]]
    boot, delta, poder = cfg["bootstrap"], cfg["delta_mf"], cfg["poder"]
    n_bases = len(cfg["unidades"]["bases"])
    g = _gates_comuns(registros, celulas, cfg)
    difs = list(rc.por_unidade(registros, "P1", "P1-alvo", "d_fe", celulas).values())
    n = rc.escolher_k(difs, delta, poder, poder["semente"], n_bases)
    relato = {}
    for nome, a, b in (("PA-2 (G-ALVO-AC)", ROT_P1AC, ROT_P1AAC), ("PA-3 (G-INSTINTO)", "P0", "P1-alvo")):
        d = list(rc.por_unidade(registros, a, b, "d_fe", celulas).values())
        relato[nome] = rc.relato_poder(d, delta, n["n"], poder, poder["semente"])
    so_relato = {}
    for nome, a, b in (("P1 - P1-alvo em D_FE (G-ALVO)", "P1", "P1-alvo"), ("P1^ac - P1-alvo^ac (G-ALVO-AC)", ROT_P1AC, ROT_P1AAC),
                       ("P0 - P1-alvo (G-INSTINTO)", "P0", "P1-alvo"), ("P0 - P1 (o J1)", "P0", "P1")):
        d = rc.por_unidade(registros, a, b, "d_fe", celulas)
        r = rc.contraste(d, boot)
        vs = list(d.values())
        m = sum(vs) / len(vs)
        dp = (sum((x - m) ** 2 for x in vs) / (len(vs) - 1)) ** 0.5 if len(vs) > 1 else None
        so_relato[nome] = {"media": r["media"], "dp_unidades": dp, "ic95": r["ic95"], "n": r["n"]}
    return {"G-MUNDO_piloto": g["G-MUNDO"], "G-USO_piloto": g["G-USO"], "n": n, "poder_secundarios": relato,
            "contrastes_so_relato": so_relato, "niveis": niveis(registros), "alvo": descritivos_alvo(registros),
            "custo": custo(registros, n["k"], n_bases, len(celulas), processos), "delta_mf": delta,
            "aviso": "o piloto serve so para o N, o G-USO e o custo (secao 6): nenhum numero dele e evidencia"}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 14)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    cb = config_bancada(cfg)
    b = bv.bancada_da_config(cb)
    if b.cfg_mundo.mult_queda != cfg["m"]:
        raise RuntimeError("o m da bancada nao e o da config")
    cerebros = conferir_cerebros(b, cb, unidades[0])
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "fase": cfg["fase"], "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "calibracao_mundo_sha256": rc._sha_arquivo(RAIZ / CALIBRACAO_MUNDO),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "git_head": rc._git("rev-parse", "HEAD"),
            "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "cerebros_conferidos": cerebros, "desempate_cheiro": DESEMPATE_CHEIRO, "bancada": bv.meta(cb),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    if cfg["fase"] == "validacao" and modo == "validacao":
        meta["piloto_resultado_sha256"] = rc._sha_arquivo(RAIZ / SAIDA["piloto"] / "resultado.json")
    meta["sha256"] = {"mundo.py": meta["bancada"]["mundo_sha256"], "config.py": meta["bancada"]["config_sha256"],
                      "lobos.py": meta["bancada"]["lobos_sha256"], "engine.py": meta["bancada"]["engine_sha256"],
                      "plano": meta["plano_sha256"], "config": meta["config_sha256"]}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    saidas = rc._executar([(tarefa_unidade, (cfg, u, str(pasta))) for u in unidades], processos)
    meta["vidas_parede_s"] = time.perf_counter() - t0
    completas, regs = {}, {}
    for comp, compa in saidas:
        completas.update(comp)
        regs.update(compa)
    bv._gravar(pasta / "medidas_completas.json", bv._dump(dict(sorted(completas.items()))))
    lista = list(regs.values())
    if cfg["fase"] == "piloto":
        resultado = {"modo": modo, "fase": "piloto", "plano": PLANO, **analisar_piloto(lista, cfg, processos)}
    else:
        resultado = {"modo": modo, "fase": "validacao", "plano": PLANO, **analisar(lista, cfg),
                     "custo": custo(lista, None, len(cfg["unidades"]["bases"]), 12, processos)}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump(dict(sorted(regs.items()))))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "medidas": regs, "resultado": resultado}


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_mundo_alvo/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA[cfg["fase"]]
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    if cfg["fase"] == "piloto":
        print(json.dumps({"n": {k: r["n"][k] for k in ("k", "n", "poder", "chega_ao_alvo")}, "G-USO_piloto": r["G-USO_piloto"]["media"],
                          "custo": r["custo"].get("validacao_estimada")}, indent=2))
    else:
        print(json.dumps({"G-MUNDO": {k: r["G-MUNDO"][k] for k in ("media", "ic95", "passa")},
                          "G-USO": {k: r["G-USO"][k] for k in ("media", "ic95", "passa")},
                          "G-ALVO": {k: r["G-ALVO"][k] for k in ("media", "ic95", "ic90", "categoria")},
                          "secundarios": {n: {"passa": g["passa"], "p": g["holm"]["p"]} for n, g in r["secundarios"].items()},
                          "leitura": r["leitura"]}, indent=2))


if __name__ == "__main__":
    main()
