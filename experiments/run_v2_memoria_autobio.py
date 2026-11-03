"""A run da C4 da V3, a validacao causal da memoria autobiografica (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 9;
docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md, secao 4; docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, 7.2). Pergunta: o episodio
lembrado pelo contexto muda o que o pet faz e o desempenho onde a experiencia passada importa, mais do que nenhuma lembranca, a mais recente
ou uma sorteada? As vidas sao as da C1 (experiments/run_v2_longe_regular.py: o cenario do MVP, os 4 donos, 14 dias, 16 interacoes por dia,
o motor que grava o corpo para a C5, o G1, o T-CENARIO-1, o G-MECANISMO e o credito em toda vida), com a conferencia da memoria de A9.10.

O desenho (A9.2 e A9.3): as celulas 4 donos x 3 lugares (`longe_fixo`, o primario; comedouro, a guarda; longe sorteado, a C4-E2 e o
descritivo), os bracos REL, SEM, REC, EMB, RELsN ("REL sem negativos", a C4-E2) e REL+F (o REL com as facetas), todos o M3* do conserto
com a `memoria_autobio` (SUBCHAVES_C4 do orquestrador do prototipo), a `facetas_mem` so no REL+F, as bases 77101, 77202, 77303, 77404 e
77505, o prefixo `digibrain_prototipo`, o K de A9.6. A run roda uma vez, sem calibracao nem piloto.

A analise (A9.4 a A9.8), no `resultado.json`: o primario (a familia REL - SEM, REL - REC e REL - EMB na taxa de fechamento por episodio de
fome, nas 4 celulas do `longe_fixo`, o IC95 pelo t sobre as unidades e o Holm sobre os tres p unilaterais), a guarda G-COMEDOURO (REL - SEM
no comedouro, "nao < 0"), as premissas (P-PESA e G-ELEGIVEL-EP), as secundarias (a C4-E2 no `longe_fixo` e no sorteado, as facetas, o
REL - SEM no sorteado), a classe de cada contraste (A6.6, com a margem de A9.6), a leitura de A9.7 e o descritivo de A9.8 (a lembranca e a
sonda, os episodios e a consolidacao, as visitas, as facetas, a conferencia da fala, o corpo e o resto), sem gate.

A trava (A9.10): o adendo 9 APROVADO no cabecalho (`exigir_adendo_aprovado`; enquanto ele estiver PROPOSTO, a run e recusada), a faixa
77101...77505 reservada em `experiments/bancada/faixas.py`, so as bases, o K, os dias e o orcamento do adendo, no maximo 4 processos, e
nenhuma gravacao por cima de uma pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa e sem o K, com
menos dias se a config pedir.

    python experiments/run_v2_memoria_autobio.py --config experiments/configs/v2_memoria_autobio/memoria_autobio.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_habito_intencao as hi  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import JANELA_8_14, MODULOS_SONDA, holm, influencia_por_modulo, janela_dias  # noqa: E402
from digilab_fala_livre.fatos import _txt  # noqa: E402
from digilab_fala_livre.memoria_fala import conferir, fatos_de_memoria, memoria_do_estado  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = orq.PLANO
PREFIXO = orq.PREFIXO                                                                 # A9.3 (o da reavaliacao, da L-2 e das C1 a C3)
FASE = "memoria_autobio"
ADENDO = 9
BASES = (77101, 77202, 77303, 77404, 77505)                                           # A9.3, PROPOSTA (AD9-7)
K_POR_BASE = 40                                                                       # A9.6, PROPOSTO (AD9-5): 200 unidades
FAIXA = (77101, 77505)
SAIDA = "artifacts_v2_digibrain_prototipo/memoria_autobio/run"                        # A9.10: a pasta-mae tem o adendo9_poder.json
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # A9.2
MAX_PROCESSOS = 4                                                                     # A9.9 (V3-D8)
DONOS = orq.DONOS
PRIMARIO, GUARDA, SORTEADO = "longe_fixo", "comedouro", "longe"                       # A9.2 (AD9-3)
LUGARES = (PRIMARIO, GUARDA, SORTEADO)
BRACOS = ("REL", "SEM", "REC", "EMB", "RELsN", "REL+F")                               # A9.2 (AD9-1, AD9-2); a espec, 7.2
CONTROLE = {"REL": "rel", "SEM": "sem", "REC": "rec", "EMB": "emb", "RELsN": "rel_sem_neg", "REL+F": "rel"}
COM_FACETAS = ("REL+F",)                                                              # AD9-2: a facetas_mem so no REL+F
CONTEXTO = ("REL", "RELsN", "REL+F")                                                  # a lembranca pelo contexto (sim >= sim_min)
FAMILIA = (("REL", "SEM"), ("REL", "REC"), ("REL", "EMB"))                            # A9.4: o primario, com o Holm
CELULAS = tuple((d, lu) for d in DONOS for lu in LUGARES)
CHAVES_CONFIG = lr.CHAVES_CONFIG
MARGEM = 0.032                                                                        # A9.6, PROPOSTA (AD9-5), SEM FONTE: o "~ 0"
ALFA_FAMILIA = 0.025                                                                  # A9.4: unilateral, na familia (o Holm)
P_PESA_LIMIAR = orq.G_PESA["limiar"]                                                  # A9.5: o 0,01 da G-PESA (A6.4), SEM FONTE
G_ELEGIVEL_EP = orq.G_ELEGIVEL_EP                                                     # A9.5: a de A6.4, como esta
JANELAS_CORPO = lr.JANELAS_CORPO
MODULOS = MODULOS_SONDA + ("aprendido",)
PALAVRA_FACETA = {"cautela_comida": "cauteloso", "apego_dono": "apegado", "ousadia_longe": "ousado"}   # A9.8, item 5 (as raizes da M6)


# ================================================================== a config e a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_faixa_reservada() -> None:
    """a faixa 77101...77505 esta em FAIXAS_RESERVADAS (A9.3, A9.10); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi_) == FAIXA for lo, hi_, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (A9.3)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'memoria_autobio', que segue o adendo 9 a letra (A9.10): outra base, outro K, outros dias ou
    outro orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o adendo sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (A9.3), o orcamento (A9.2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (A9.3)")
    exigir_faixa_reservada()
    orq.exigir_adendo_aprovado(_plano(), ADENDO)
    erros = []
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_POR_BASE:
        erros.append(f"K por base {u['k']} (o plano: {K_POR_BASE})")
    if erros:
        raise ValueError(f"a {FASE} segue o adendo {ADENDO} a letra: {erros}")
    return FASE


# ================================================================== a vida
class Categorias(dict):
    """{id do episodio: a categoria}, de todo episodio que passou pela recente, lido logo depois de cada decisao (A9.8, item 5). So le: nao
    toca em rng nem em estado; a vida e o log saem os mesmos (o G1 rejoga a vida com a fabrica sem o coletor e confere bit a bit)."""


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: a do `lr.viver` (o cerebro do conserto, o MotorGravaCorpo), com o coletor das categorias no cerebro desta vida. Devolve
    (o motor, o registro, as fabricas sem o coletor, as categorias)."""
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento_por_dia, conserto=True)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    registro = fp(CONFIG_PADRAO)
    c, categorias = orq.cerebro_de(registro), Categorias()
    agir = c.agir

    def agir_e_ler(obs, rng):
        acao = agir(obs, rng)
        for e in c.m.mem.recente:                     # todo episodio novo entra na recente (codificar_autobio) e fica la ao menos um dia
            categorias.setdefault(e["id"], list(e["categoria"]))
        return acao

    c.agir = agir_e_ler
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    del c.agir                                        # o cerebro volta a ser o da fabrica (o estado interno nao muda)
    return motor, registro, (fp, fm), categorias


def fins_conhecidos(braco: str) -> frozenset:
    """os fins que a `estado.py` pode dar com a config do braco (as chaves de `EstadoDinamico.fins`; a lista nao e escrita a mao)"""
    return hi.fins_conhecidos(braco)


def conferir_fins(braco: str, registro) -> dict:
    """os fins das intencoes da vida, por motivo; falha alto com um fim desconhecido, com a contagem do registro diferente da do estado, ou
    com uma retomada ou um `n_susp` (a `intencao_suspensa` fica desligada nos seis bracos). A do orquestrador da C2."""
    return hi.conferir_fins(braco, registro)


def _guardados(c) -> list[dict]:
    a = c.m.mem.estado_interno()["autobio"]
    return a["recente"] + a["duradoura"] + a["central"]


def conferir_memoria(braco: str, c) -> None:
    """A9.10: a memoria de cada braco faz o que a tabela 7.2 da espec diz, decisao a decisao, pelo registro do cerebro. Falha alto:
      - as subchaves nao sao as do braco (a `memoria_autobio`, o `controle_mem` e a `facetas_mem` so no REL+F);
      - uma decisao sem a lembranca no motivo, ou o motivo com a faceta fora do REL+F (ou sem ela no REL+F);
      - no SEM: uma lembranca, um lugar lembrado, ou a memoria ou a lembranca decidindo;
      - no REC e no EMB: uma lembranca com `sim` diferente de 0; no REL, no RELsN e no REL+F: uma lembranca abaixo de `sim_min`;
      - no RELsN: um sigma < 0 lembrado ou guardado (MA-3);
      - a sonda `lembranca_decidiu` sem a lembranca, sem o termo L ou sem a unidade que o recebeu (o fato Q2 da fala ficaria sem lastro);
      - uma mudanca de faceta sem os ids dos episodios."""
    cd = c.cd
    if not cd.memoria_autobio or cd.controle_mem != CONTROLE[braco] or cd.facetas_mem != (braco in COM_FACETAS):
        raise RuntimeError(f"{braco}: as subchaves da memoria nao sao as do braco (A9.2)")
    sim_min = c.inatos.sim_min
    for m in c.motivos:
        lem = m.get("lembranca")
        if lem is None:
            raise RuntimeError(f"{braco}: a decisao {m['k']} sem a lembranca no motivo")
        if ("faceta" in m) != (braco in COM_FACETAS):
            raise RuntimeError(f"{braco}: a faceta no motivo da decisao {m['k']} fora do REL+F (ou sem ela no REL+F)")
        rid, so = lem["recuperado"], m["sondas"]
        if braco == "SEM" and (rid is not None or (m["memoria"] is not None and m["memoria"]["lugar"] is not None)
                               or so["memoria_decidiu"] or so["lembranca_decidiu"]):
            raise RuntimeError(f"SEM: a decisao {m['k']} lembrou, teve lugar lembrado ou a memoria decidiu")
        if rid is not None and braco in ("REC", "EMB") and lem["sim"] != 0:
            raise RuntimeError(f"{braco}: a lembranca da decisao {m['k']} com sim {lem['sim']} (o controle nao olha o contexto)")
        if rid is not None and braco in CONTEXTO and lem["sim"] < sim_min:
            raise RuntimeError(f"{braco}: a lembranca da decisao {m['k']} abaixo de sim_min")
        if braco == "RELsN" and lem["sigma"] < 0:
            raise RuntimeError(f"RELsN: a decisao {m['k']} lembrou um sigma < 0 (MA-3)")
        if so["lembranca_decidiu"] and (rid is None or lem["L"] is None or not lem["unidades"]):
            raise RuntimeError(f"{braco}: a lembranca decidiu na decisao {m['k']} sem a lembranca, o L ou a unidade")
        for mud in m.get("faceta", {}).get("mudancas", []):
            if not mud["episodios"]:
                raise RuntimeError(f"{braco}: a mudanca de faceta da decisao {m['k']} sem os ids dos episodios")
    if braco == "RELsN" and any(e["sigma"] < 0 for e in _guardados(c)):
        raise RuntimeError("RELsN: um sigma < 0 guardado no fim (MA-3)")


def _cat(categoria: list) -> str:
    return f"{categoria[0]} {categoria[1]}".replace("_", " ")


def conferencia_da_fala(c, categorias: dict) -> dict:
    """A9.8, item 5 (a ME-6; o item 2 do #536, "a medir na validacao causal"): a conferencia da M6 (`memoria_fala.conferir`, sem LLM)
    sobre alegacoes sinteticas montadas do registro da vida, decisao a decisao, com os fatos Q e Z que a fala teria naquela decisao. As
    vidas nao falam; o que se mede e se a conferencia por raiz em comum sustenta o verdadeiro e recusa o falso no registro real:
      - lembranca verdadeira: "eu lembrei do <a categoria do lembrado>" (deve ser sustentada);
      - lembranca falsa: na decisao com lembranca, a categoria de outro episodio guardado, de categoria diferente (deve ser recusada);
        na decisao sem lembranca, a do ultimo episodio guardado (deve ser recusada);
      - causa: "fiz isso porque lembrei do <o lembrado>", sustentada so se a lembranca decidiu;
      - faceta (so no REL+F): "fiquei mais/menos <faceta>" no sentido registrado (sustentada) e no contrario (recusada).
    A categoria de cada episodio sai do coletor da vida (`viver`), lida quando o episodio entrou na recente. Os episodios "ja codificados" na
    decisao k sao os dos fechamentos das decisoes anteriores (`consequencia["autobio"]`, o fechamento de k - 1 vem antes da lembranca de k).
    A falsa da decisao com lembranca e a categoria do primeiro codificado com outra (acao, classe); a da decisao sem lembranca, a do ultimo
    codificado. Um episodio lembrado ou codificado fora do coletor falha alto."""
    n = {"verdadeira": [0, 0], "falsa": [0, 0], "causa_verdadeira": [0, 0], "causa_falsa": [0, 0], "faceta_verdadeira": [0, 0],
         "faceta_falsa": [0, 0]}

    def contar(chave: str, fala: str, fatos: list[dict]) -> None:
        r = conferir(fala, fatos)
        if len(r) != 1:
            raise RuntimeError(f"a alegacao sintetica {fala!r} deu {len(r)} alegacoes")
        n[chave][0] += 1
        n[chave][1] += r[0]["sustentada"]

    codificados: list[int] = []                       # os ids codificados ate a decisao, na ordem
    for k, m in enumerate(c.motivos):
        if k > 0 and c.motivos[k - 1]["consequencia"]["autobio"] is not None:
            codificados.append(c.motivos[k - 1]["consequencia"]["autobio"])
        rid = m["lembranca"]["recuperado"]
        for i in ([rid] if rid is not None else []) + codificados[-1:]:
            if i not in categorias:
                raise RuntimeError(f"o episodio {i} (decisao {m['k']}) fora do coletor das categorias")
        decidiu = m["sondas"]["lembranca_decidiu"]
        mud = m.get("faceta", {}).get("mudancas", [])
        estado = memoria_do_estado(None if rid is None else {"episodio": rid, "categoria": categorias[rid], "decidiu": decidiu}, mud)
        fatos = [{"id": i, "tipo": t, "texto": x} for i, t, x in fatos_de_memoria(estado, _txt)]
        if rid is not None:
            cat = categorias[rid]
            contar("verdadeira", f"eu lembrei do {_cat(cat)}", fatos)
            contar("causa_verdadeira" if decidiu else "causa_falsa", f"fiz isso porque lembrei do {_cat(cat)}", fatos)
            outra = next((categorias[i] for i in codificados if categorias[i][:2] != cat[:2]), None)
            if outra is not None:
                contar("falsa", f"eu lembrei do {_cat(outra)}", fatos)
        elif codificados:
            contar("falsa", f"eu lembrei do {_cat(categorias[codificados[-1]])}", fatos)
        for x in mud:
            certo, errado = ("mais", "menos") if x["passo"] > 0 else ("menos", "mais")
            contar("faceta_verdadeira", f"fiquei {certo} {PALAVRA_FACETA[x['faceta']]}", fatos)
            contar("faceta_falsa", f"fiquei {errado} {PALAVRA_FACETA[x['faceta']]}", fatos)
    return {"alegacoes": {k: {"n": a, "sustentadas": s} for k, (a, s) in n.items()}}


def medidas_memoria(registro, dias: int, categorias: dict) -> dict:
    """A9.5 e A9.8: a lembranca (a fracao das decisoes com lembranca; a fracao das decisoes, nos dias 8 a 14 e na vida, em que a memoria
    mudou a escolha pela sonda `sem_memoria`, que tira o lugar e a lembranca, e em que so a lembranca a mudou, `sem_lembranca`; no REL+F, a
    faceta, `sem_faceta`), os episodios (codificados, com sigma < 0 na codificacao, guardados por memoria no fim, esquecidos, saidos), as
    facetas (no REL+F: o valor no fim e as mudancas) e a conferencia da fala"""
    c = orq.cerebro_de(registro)
    ms = c.motivos
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    janela = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    vida = janela_dias(1, dias)
    mods = ("memoria", "lembranca") + (("faceta",) if c.cd.facetas_mem else ())
    sondas = [(k * passo, {mod: m["sondas"][f"{mod}_decidiu"] for mod in mods}) for k, m in enumerate(ms)]
    a = c.m.mem.estado_interno()["autobio"]
    esquecidos = sum(len(x["esquecidos"]) for x in a["consolidacoes"])
    out = {"decisoes": len(ms), "com_lembranca": sum(1 for m in ms if m["lembranca"]["recuperado"] is not None) / len(ms),
           "decidiu": influencia_por_modulo(sondas, janela, mods)["frac"], "decidiu_vida": influencia_por_modulo(sondas, vida, mods)["frac"],
           "lembrou_negativo": sum(1 for m in ms if m["lembranca"]["recuperado"] is not None and m["lembranca"]["sigma"] < 0),
           "episodios": {"codificados": a["proximo_id"], "guardados": {k: len(a[k]) for k in ("recente", "duradoura", "central")},
                         "negativos_guardados": sum(1 for e in _guardados(c) if e["sigma"] < 0),
                         "consolidacoes": len(a["consolidacoes"]), "esquecidos": esquecidos, "sairam_da_recente": len(a["saidas"])},
           "facetas": None, "fala": conferencia_da_fala(c, categorias)}
    if c.cd.facetas_mem:
        p = c.m.pers.estado_interno()
        out["facetas"] = {"valores": dict(p["valores"]), "mudancas": len(p["mudancas"]),
                          "por_faceta": {f: sum(1 for x in p["mudancas"] if x["faceta"] == f) for f in PALAVRA_FACETA}}
    return out


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida (o motor da C1, que grava o corpo, com o coletor das categorias), gravada, rejogada do disco (G1), conferida (as falhas altas, os fins e a memoria
    de A9.10) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    conferir_memoria(braco, orq.cerebro_de(registro))
    fins = conferir_fins(braco, registro)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins, "memoria": medidas_memoria(registro, cfg["dias"], categorias),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise
def _celulas(lugar: str) -> tuple:
    return tuple((d, lugar) for d in DONOS)


def nivel(registros: list[dict], braco: str, medida, lugar: str) -> dict:
    """{(base, semente): a media da medida nas 4 celulas do lugar} (a unidade de A9.4)"""
    return orq.por_unidade(registros, braco, None, medida, _celulas(lugar))


def diferenca(registros: list[dict], a: str, b: str, medida, lugar: str) -> dict:
    """{(base, semente): a media, nas 4 celulas do lugar, de medida(a) - medida(b) no mesmo dono} (as celulas com None num dos bracos
    ficam fora, a regra do `por_unidade`)"""
    return orq.por_unidade(registros, a, b, medida, _celulas(lugar))


def classe(ic: dict, margem: float = MARGEM) -> dict:
    """a classe de A6.6 (A9.6), na ordem, com a margem deste adendo"""
    return lr.classe(ic, margem)


def estimativa(difs: dict, margem: float = MARGEM) -> dict:
    """o descritivo de um valor por unidade: a media, o dp e o IC95 pelo t (A4.4.6) sobre as unidades, com a classe de A6.6"""
    ic = orq.ic_t([v for _, v in sorted(difs.items())])
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]},
            "classe": classe(ic, margem), "motivo": ic["motivo"]}


EPISODIO = lr.EPISODIO
PESA_MEMORIA = lambda r: r["memoria"]["decidiu"]["memoria"]                              # noqa: E731


def _contraste(registros: list[dict], a: str, b: str, lugar: str, rotulo: str, boot: dict) -> dict:
    difs = diferenca(registros, a, b, EPISODIO, lugar)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    return {"contraste": rotulo, **c, "classe": classe(ic), "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(estimativa(difs)["dp"], c["n"])}


def primario(registros: list[dict], boot: dict) -> dict:
    """A9.4: a familia REL - SEM, REL - REC e REL - EMB na taxa por episodio, nas 4 celulas do `longe_fixo`, o t sobre as unidades; o
    Holm (alfa 0,025 unilateral na familia) sobre os tres p unilaterais; cada contraste passa se o Holm o rejeita. Ao lado: o IC95, o g1
    com a ressalva, o IC percentil do bootstrap (rotulado), a classe de A6.6 e a margem efetiva."""
    cs = {f"{a} - {b}": _contraste(registros, a, b, PRIMARIO, f"{a} - {b}, a taxa de fechamento por episodio, nas 4 celulas do longe_fixo",
                                   boot) for a, b in FAMILIA}
    h = holm({n: c["p_unilateral"] for n, c in cs.items()}, ALFA_FAMILIA)
    return {n: {**c, "holm": h[n], "passa": h[n]["rejeita"]} for n, c in cs.items()}


def guarda(registros: list[dict], boot: dict) -> dict:
    """A9.4: a G-COMEDOURO, REL - SEM nas 4 celulas do comedouro; falha so com a classe "< 0" de A6.6"""
    c = _contraste(registros, "REL", "SEM", GUARDA, "G-COMEDOURO: REL - SEM, a taxa por episodio, nas 4 celulas do comedouro", boot)
    return {**c, "menor_que_0": c["classe"]["classe"] == "< 0"}


def secundarias(registros: list[dict], boot: dict) -> dict:
    """A9.4: o mesmo teste, sem gate e sem Holm, lidas pela classe: a C4-E2 (REL - RELsN) no `longe_fixo` (sem previsao, o risco da espec,
    secao 5) e no longe sorteado (a direcao de Ho, "> 0"); as facetas (REL+F - REL no `longe_fixo`, sem previsao); e REL - SEM no
    longe sorteado (sem previsao)"""
    return {"E2-FIXO": {**_contraste(registros, "REL", "RELsN", PRIMARIO, "E2-FIXO: REL - RELsN, a taxa por episodio, no longe_fixo", boot),
                        "previsao": None},
            "E2-SORTEADO": {**_contraste(registros, "REL", "RELsN", SORTEADO, "E2-SORTEADO: REL - RELsN, a taxa por episodio, no longe "
                                         "sorteado", boot), "previsao": "> 0"},
            "FACETAS": {**_contraste(registros, "REL+F", "REL", PRIMARIO, "FACETAS: REL+F - REL, a taxa por episodio, no longe_fixo", boot),
                        "previsao": None},
            "SEM-SORTEADO": {**_contraste(registros, "REL", "SEM", SORTEADO, "SEM-SORTEADO: REL - SEM, a taxa por episodio, no longe "
                                          "sorteado", boot), "previsao": None}}


def premissas(registros: list[dict]) -> dict:
    """A9.5: a P-PESA (no REL, nas 4 celulas do `longe_fixo`, a fracao das decisoes dos dias 8 a 14 em que a memoria mudou a escolha pela
    sonda `sem_memoria`, por unidade; o limite inferior do IC95 pelo t > 0,01) e a G-ELEGIVEL-EP de A6.4 (no REL, no SEM, no REC e no EMB,
    no `longe_fixo`, ao menos 80 % das vidas com 3 episodios ou mais). Se uma falha, o primario e inconclusivo por premissa."""
    pesa = estimativa(nivel(registros, "REL", PESA_MEMORIA, PRIMARIO))
    pesa["passa"] = pesa["ic95"]["ic_inferior"] is not None and pesa["ic95"]["ic_inferior"] > P_PESA_LIMIAR
    pesa["limiar"] = P_PESA_LIMIAR
    elegivel = {}
    for b in ("REL", "SEM", "REC", "EMB"):
        vs = [r for r in registros if r["braco"] == b and r["lugar"] == PRIMARIO]
        frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= G_ELEGIVEL_EP["episodios"]) / len(vs)
        elegivel[b] = {"frac_vidas": frac, "vidas": len(vs), "limiar": G_ELEGIVEL_EP["frac_vidas"], "passa": frac >= G_ELEGIVEL_EP["frac_vidas"]}
    eleg = {"por_braco": elegivel, "passa": all(v["passa"] for v in elegivel.values())}
    return {"P-PESA": pesa, "G-ELEGIVEL-EP": eleg, "conclusivo": pesa["passa"] and eleg["passa"]}


def _lido(c: dict) -> str:
    return "> 0" if c["passa"] else c["classe"]["classe"]


def leitura(prim: dict, prem: dict, gua: dict) -> dict:
    """A9.7, na ordem (a primeira linha que serve). Em cada contraste do primario, o Holm manda: '> 0' e o Holm o rejeitar; senao a classe
    de A6.6. A guarda le so "< 0" ou nao. As secundarias e o descritivo nao mudam a linha."""
    sem, rec, emb = (_lido(prim[f"REL - {b}"]) for b in ("SEM", "REC", "EMB"))
    base = {"REL - SEM": sem, "REL - REC": rec, "REL - EMB": emb, "G-COMEDOURO": gua["classe"]["classe"],
            "ressalva": {n: c["ressalva_assimetria"] for n, c in prim.items() if c["ressalva_assimetria"]}}
    if not prem["conclusivo"]:
        return {**base, "linha": 1, "o_que_diria": "inconclusivo por premissa (A9.5): a memoria nao mudou escolhas no REL, ou os donos nao "
                                                   "deram episodios", "o_que_se_faz": "registrado; nada se decide"}
    if "> 0" in (sem, rec, emb) and gua["menor_que_0"]:
        return {**base, "linha": 2, "o_que_diria": "a memoria ajuda longe da racao e atrapalha perto dela",
                "o_que_se_faz": "registrado; volta ao Matheus; a memoria_autobio nao vira candidata"}
    if sem == rec == emb == "> 0":
        return {**base, "linha": 3, "o_que_diria": "nestas condicoes, a lembranca pelo contexto melhora o episodio de fome, e nao basta "
                                                   "lembrar qualquer episodio: nem o mais recente nem um sorteado fazem o mesmo",
                "o_que_se_faz": "a memoria_autobio (REL) vira candidata; volta ao Matheus. Nao vai ao jogo sem plano proprio"}
    if sem == "> 0":
        return {**base, "linha": 4, "o_que_diria": "lembrar ajuda, mas a relevancia pelo contexto nao se separa da recencia ou do acaso "
                                                   "(um '≈ 0' diz que nao importa; outra classe, que nao se sabe)",
                "o_que_se_faz": "registrado; o REL nao vira candidato pela relevancia; a escolha entre o REL e um controle mais simples "
                                "volta ao Matheus"}
    if sem == "≈ 0":
        return {**base, "linha": 5, "o_que_diria": "nestas condicoes, a memoria autobiografica nao move o episodio de fome; o descritivo "
                                                   "separa a lembranca que nao acontece da que acontece e nao pesa (A9.8, item 1)",
                "o_que_se_faz": "registrado; a memoria_autobio fica desligada; nenhuma mudanca da memoria sem plano proprio"}
    if sem == "< 0":
        return {**base, "linha": 6, "o_que_diria": "a memoria autobiografica piora o pet", "o_que_se_faz": "registrado como esta; a "
                                                                                                        "subchave fica desligada"}
    return {**base, "linha": 7, "o_que_diria": "nada se decide", "o_que_se_faz": "registrado como indeterminado"}


# ------------------------------------------------------------------ o descritivo (A9.8; sem gate)
def _contrastes(registros: list[dict], medida, bracos: tuple = BRACOS[1:]) -> dict:
    """REL contra cada outro braco, em cada lugar"""
    return {f"{lu}|REL - {b}": estimativa(diferenca(registros, "REL", b, medida, lu)) for lu in LUGARES for b in bracos}


def _niveis(registros: list[dict], medida, bracos: tuple = BRACOS) -> dict:
    return {f"{lu}|{b}": estimativa(nivel(registros, b, medida, lu)) for lu in LUGARES for b in bracos}


def _somar(registros: list[dict], ler, bracos: tuple = BRACOS) -> dict:
    """{lugar|braco: a soma, campo a campo, do dicionario que `ler` tira de cada vida}"""
    out = {}
    for lu in LUGARES:
        for b in bracos:
            soma: dict = {}
            for r in registros:
                if r["lugar"] == lu and r["braco"] == b:
                    for k, v in ler(r).items():
                        soma[k] = soma.get(k, 0) + v
            out[f"{lu}|{b}"] = dict(sorted(soma.items()))
    return out


def lembranca(registros: list[dict]) -> dict:
    """A9.8, item 1 (a tarefa, secao 0: a lembranca que nao acontece contra a que acontece e nao pesa): por braco e lugar, a fracao das
    decisoes com lembranca, a fracao em que a memoria mudou a escolha (`sem_memoria`) e em que so a lembranca a mudou (`sem_lembranca`),
    nos dias 8 a 14, e as lembrancas de sigma < 0; os contrastes do REL com os outros bracos nas duas fracoes"""
    com = lambda r: r["memoria"]["com_lembranca"]                                  # noqa: E731
    so_lem = lambda r: r["memoria"]["decidiu"]["lembranca"]                         # noqa: E731
    return {"com_lembranca": {"niveis": _niveis(registros, com), "contrastes": _contrastes(registros, com)},
            "memoria_decidiu": {"niveis": _niveis(registros, PESA_MEMORIA), "contrastes": _contrastes(registros, PESA_MEMORIA)},
            "lembranca_decidiu": {"niveis": _niveis(registros, so_lem), "contrastes": _contrastes(registros, so_lem)},
            "lembrou_negativo_somado": _somar(registros, lambda r: {"lembrou_negativo": r["memoria"]["lembrou_negativo"]})}


def episodios(registros: list[dict]) -> dict:
    """A9.8, item 2: os episodios por vida (codificados, guardados por memoria no fim, com sigma < 0, consolidacoes, esquecidos), somados
    por braco e lugar; as visitas ao lugar lembrado e as vazias (a C4-E1), em nivel e nos contrastes do REL"""
    ep = lambda r: {"codificados": r["memoria"]["episodios"]["codificados"],                           # noqa: E731
                    **{f"guardados_{k}": v for k, v in r["memoria"]["episodios"]["guardados"].items()},
                    **{k: r["memoria"]["episodios"][k] for k in ("negativos_guardados", "consolidacoes", "esquecidos", "sairam_da_recente")}}
    visitas = lambda r: r["visitas_lugar_lembrado"]                                 # noqa: E731
    return {"somados": _somar(registros, ep), "visitas": {"niveis": _niveis(registros, visitas), "contrastes": _contrastes(registros, visitas)},
            "visitas_somadas": _somar(registros, lambda r: {"visitas": r["visitas_lugar_lembrado"], "vazias": r["visitas_vazias"]})}


def facetas(registros: list[dict]) -> dict:
    """A9.8, item 4: so no REL+F, o valor de cada faceta no fim (nivel por lugar), as mudancas somadas e a fracao das decisoes dos dias 8 a
    14 em que a faceta mudou a escolha (`sem_faceta`)"""
    out = {f: _niveis(registros, lambda r, f=f: r["memoria"]["facetas"]["valores"][f], COM_FACETAS) for f in PALAVRA_FACETA}
    return {"valor_no_fim": out, "mudancas_somadas": _somar(registros, lambda r: r["memoria"]["facetas"]["por_faceta"], COM_FACETAS),
            "faceta_decidiu": _niveis(registros, lambda r: r["memoria"]["decidiu"]["faceta"], COM_FACETAS)}


def fala(registros: list[dict]) -> dict:
    """A9.8, item 5: a conferencia da fala sobre as alegacoes sinteticas, somada por braco e lugar: as sustentadas sobre as alegacoes de
    cada tipo (a sensibilidade nas verdadeiras; o falso sustentado nas falsas)"""
    somas = _somar(registros, lambda r: {f"{k}|{c}": v[c] for k, v in r["memoria"]["fala"]["alegacoes"].items() for c in ("n", "sustentadas")})
    fracs = {}
    for chave, s in somas.items():
        fracs[chave] = {k: (s[f"{k}|sustentadas"] / s[f"{k}|n"] if s[f"{k}|n"] else None)
                        for k in ("verdadeira", "falsa", "causa_verdadeira", "causa_falsa", "faceta_verdadeira", "faceta_falsa")}
    return {"rotulo": "a conferencia da M6 sobre alegacoes sinteticas do registro; as vidas nao falam (A9.8, item 5)", "somadas": somas,
            "frac_sustentadas": fracs}


def corpo(registros: list[dict]) -> dict:
    """A9.8, item 3: as medidas da C5 (AD6-4, como estao), a exaustao e a privacao de hoje, em nivel e nos contrastes do REL"""
    out = {"limiar": lr.LIMIAR_CORPO, "status": "as definicoes da AD6-4, DECIDIDAS, SEM FONTE",
           "privacao_de_hoje": {"niveis": _niveis(registros, lambda r: r["privacao"]), "contrastes": _contrastes(registros, lambda r: r["privacao"])},
           "exaustao": {"niveis": _niveis(registros, lambda r: r["exaustao"]), "contrastes": _contrastes(registros, lambda r: r["exaustao"])}}
    for j in JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f)}
    return out


def outros(registros: list[dict]) -> dict:
    """A9.8, item 6: a taxa por episodio por braco e lugar e os contrastes do REL; a G-PESA de cada modulo de hoje; os episodios de fome
    por vida; os fins somados; por dono, so a media da taxa por episodio"""
    por_dono = {}
    for d in DONOS:
        for lu in LUGARES:
            for b in BRACOS:
                vs = [EPISODIO(r) for r in registros if r["dono"] == d and r["lugar"] == lu and r["braco"] == b and EPISODIO(r) is not None]
                if vs:
                    por_dono[f"{d}|{lu}|{b}"] = statistics.fmean(vs)
    return {"episodio": {"niveis": _niveis(registros, EPISODIO), "contrastes": _contrastes(registros, EPISODIO)},
            "g_pesa_por_modulo": {m: _niveis(registros, lambda r, m=m: r["influencia"][m]) for m in MODULOS},
            "episodios_fome_por_vida": _niveis(registros, lambda r: r["episodios_fome"]["n"]),
            "fins_somados": _somar(registros, lambda r: r["fins_conferidos"]), "por_dono": por_dono}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise de A9.4 a A9.8, com a classe de cada contraste e a leitura"""
    prim, gua, sec, prem = primario(registros, boot), guarda(registros, boot), secundarias(registros, boot), premissas(registros)
    return {"primario": prim, "guarda": gua, "secundarias": sec, "premissas": prem, "leitura": leitura(prim, prem, gua),
            "descritivo": {"lembranca": lembranca(registros), "episodios": episodios(registros), "facetas": facetas(registros),
                           "fala": fala(registros), "corpo": corpo(registros), "outros": outros(registros)},
            "nao_demonstra": ["que o modular supera o A", "prontidao do prototipo", "tamanho de efeito fora das condicoes da run",
                              "que o mecanismo e novo", "que o pet lembra em algum sentido alem do registro e da sonda",
                              "a fidelidade de uma fala por LLM (as vidas nao falam)", "o efeito combinado com a C2 ou a C3 (MA-7)"]}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8 e A9.9)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; A9.10)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "longe_regular_sha256": rc._sha_arquivo(Path(lr.__file__)), "habito_intencao_sha256": rc._sha_arquivo(Path(hi.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": {b: orq.SUBCHAVES_C4[b] for b in BRACOS},
            "fins_conhecidos": {b: sorted(fins_conhecidos(b)) for b in BRACOS},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))}
            | {f"digilab_fala_livre/{n}": rc._sha_arquivo(RAIZ / "digilab_fala_livre" / n) for n in ("fatos.py", "memoria_fala.py")},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos),
                 **analisar(list(lidos.values()))}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "resultado.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _imprimir_resumo(r: dict) -> None:
    """O resumo no console: ASCII puro (ensure_ascii), para nao quebrar num console cp1252 com '≈' na leitura (o #518); os artefatos
    gravados nao passam por aqui."""
    print(json.dumps({k: r[k] for k in ("modo", "vidas", "primario", "guarda", "secundarias", "premissas", "leitura")}, indent=1,
                     ensure_ascii=True, default=str)[:4000])


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_digibrain_prototipo/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    _imprimir_resumo(r)


if __name__ == "__main__":
    main()
