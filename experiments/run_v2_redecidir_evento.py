"""A run da C3 da V3, a escolha refeita so por evento (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 8;
docs/TAREFA_V3_REDECIDIR_EVENTO.md, RD-1 a RD-9; docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md, RE-1 a RE-4). Pergunta: o modular quebra
as idas e as buscas no longe, em parte, porque o M-ARB refaz o sorteio a cada decisao, mesmo quando nada mudou no corpo nem no mundo? As
vidas sao as da C1 (experiments/run_v2_longe_regular.py: o cenario do MVP, os 4 donos, 14 dias, 16 interacoes por dia, o motor que grava
o corpo para a C5, o G1, o T-CENARIO-1, o G-MECANISMO e o credito em toda vida; nos bracos R, tambem o `conferir_redecidir`).

O desenho (A8.2 e A8.3): as celulas 4 donos x 3 lugares (`longe_fixo`, o primario; comedouro, a guarda; longe, so descritivo), os bracos
M3*, M3*R, M2 e M2R (o M3* e o M2 do conserto, com e sem a subchave da C3; SUBCHAVES_C3 do orquestrador do prototipo), todos com a
`intencao_suspensa` e a corrida da C2 desligadas, as bases 76101, 76202, 76303, 76404 e 76505, o prefixo `digibrain_prototipo`, o K de
A8.6. A run roda uma vez, sem calibracao nem piloto. No codigo, o M3* se chama "M3" e o M3*R, "M3R".

A analise (A8.4 a A8.8), no `resultado.json`: o primario P-R (M3*R - M3* na taxa de fechamento por episodio de fome, nas 4 celulas do
`longe_fixo`, o IC95 pelo t sobre as unidades), a guarda G-COMEDOURO (o mesmo contraste no comedouro, "nao < 0"), as premissas (P-SEGURA,
P-EVENTO e G-ELEGIVEL-EP), as secundarias S1 (M2R - M2 no `longe_fixo`) e S2 (M3*R - M3* no longe sorteado), a classe de cada contraste
(A6.6, com a margem de A8.6), a leitura da tabela de 1.5 da tarefa (A8.7) e o descritivo de A8.8 (as trocas por decisao da LP-2, os fins
de hoje rotulados, o mecanismo so por braco, o corpo, as faixas de d0, a G-PESA e os episodios), sem gate.

A trava (A8.10): o adendo 8 APROVADO no cabecalho (`exigir_adendo_aprovado`; enquanto ele estiver PROPOSTO, a run e recusada), a faixa
76101...76505 reservada em `experiments/bancada/faixas.py`, so as bases, o K, os dias e o orcamento do adendo, no maximo 4 processos, e
nenhuma gravacao por cima de uma pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa e sem o K, com
menos dias se a config pedir.

A conferencia dos fins (a licao do #507): os fins conhecidos sao as chaves de `EstadoDinamico.fins` com a config do braco (a do
orquestrador da C2, `conferir_fins`), e a contagem do registro tem de ser a do proprio estado, vida a vida; senao, falha alto.

    python experiments/run_v2_redecidir_evento.py --config experiments/configs/v2_redecidir_evento/redecidir_evento.json --processos 4
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
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_habito_intencao as hi  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.metrics import JANELA_8_14, MODULOS_SONDA, influencia_por_modulo, janela_dias  # noqa: E402

PLANO = orq.PLANO
PREFIXO = orq.PREFIXO                                                                 # A8.3 (o da reavaliacao, da L-2, da C1 e da C2)
FASE = "redecidir_evento"
ADENDO = 8
BASES = (76101, 76202, 76303, 76404, 76505)                                           # A8.3 (RD-7)
K_POR_BASE = 30                                                                       # A8.6, PROPOSTO (AD8-1): 150 unidades
FAIXA = (76101, 76505)
SAIDA = "artifacts_v2_digibrain_prototipo/redecidir_evento/run"                       # A8.10: a pasta-mae ja tem o adendo8_poder.json
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # A8.2
MAX_PROCESSOS = 4                                                                     # A8.9 (V3-D8)
DONOS = orq.DONOS
PRIMARIO, GUARDA = "longe_fixo", "comedouro"                                          # A8.2 (RD-5)
LUGARES = (PRIMARIO, GUARDA, "longe")                                                 # o longe sorteado, so descritivo (S2)
BRACOS = ("M3", "M3R", "M2", "M2R")                                                   # A8.2 (RD-1); o "M3" e o M3*, o "M3R" o M3*R
BRACOS_R = ("M3R", "M2R")
PARES = (("M3R", "M3"), ("M2R", "M2"))                                                # cada braco R contra o seu controle
CELULAS = tuple((d, lu) for d in DONOS for lu in LUGARES)
CHAVES_CONFIG = lr.CHAVES_CONFIG
MARGEM = 0.025                                                                        # A8.6, PROPOSTA (AD8-1), SEM FONTE: o "~ 0"
P_SEGURA_LIMIAR = 0.10                                                                # A8.5 (a P-SEGURA da tarefa, 4.3), SEM FONTE
P_EVENTO_LIMIAR = 0.25                                                                # A8.5 (a P-EVENTO; o limiar do C-L2-4), SEM FONTE
G_ELEGIVEL_EP = orq.G_ELEGIVEL_EP                                                     # A8.5: a de A6.4, como esta
JANELAS_CORPO = lr.JANELAS_CORPO
EVENTOS = ("E-REFLEXO", "E-RECEPTOR", "E-MUNDO", "E-FIM", "E-TETO")                   # a ordem do registro (a espec, secao 3)
MODULOS = MODULOS_SONDA + ("aprendido",)


# ================================================================== a config e a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_faixa_reservada() -> None:
    """a faixa 76101...76505 esta em FAIXAS_RESERVADAS (A8.3, A8.10); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi_) == FAIXA for lo, hi_, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (A8.3)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'redecidir_evento', que segue o adendo 8 a letra (A8.10): outra base, outro K, outros dias ou
    outro orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o adendo sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (A8.3), o orcamento (A8.2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (A8.3)")
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
def fins_conhecidos(braco: str) -> frozenset:
    """os fins que a `estado.py` pode dar com a config do braco (as chaves de `EstadoDinamico.fins`; a lista nao e escrita a mao)"""
    return hi.fins_conhecidos(braco)


def conferir_fins(braco: str, registro) -> dict:
    """A8.8, item 2: os fins das intencoes da vida, por motivo; falha alto com um fim desconhecido, com a contagem do registro diferente
    da do estado, ou com uma retomada ou um `n_susp` (a `intencao_suspensa` fica desligada nos quatro bracos). A do orquestrador da C2."""
    return hi.conferir_fins(braco, registro)


def trocas_lp2(motivos: list[dict]) -> dict:
    """A8.8, item 1 (a LP-2; a tarefa, 1.4): as trocas por decisao, a mesma conta do `orq.trocas_por_decisao` (uma decisao sem o reflexo
    cuja unidade difere da ultima escolhida sem o reflexo; a retomada nao conta), com o motivo: o dormir pelo sorteio (a unidade nova e a
    do dormir) ou outra unidade. A conta e conferida contra a do prototipo."""
    dormir, outra, ultima = 0, 0, None
    for m in motivos:
        if m["reflexo"]:
            continue
        if ultima is not None and m["escolha"] != ultima:
            if m["acao"] == "dormir":
                dormir += 1
            else:
                outra += 1
        ultima = m["escolha"]
    total = orq.trocas_por_decisao(motivos)
    if total != dormir + outra:
        raise RuntimeError(f"as trocas por decisao ({dormir + outra}) nao sao as do prototipo ({total})")
    return {"total": total, "dormir_sorteio": dormir, "outra_unidade": outra}


def medidas_redecidir(registro, dias: int) -> dict:
    """A8.5 e A8.8: as decisoes sem o reflexo e as trocas da LP-2 (todo braco); nos bracos R, tambem a escolha segurada: as decisoes
    seguradas (a fracao sobre as sem o reflexo, a P-SEGURA), as sequencias seguradas (as fechadas, as que acabaram com o E-TETO na lista
    da decisao seguinte, a P-EVENTO, e a aberta no fim da vida, fora), os eventos das decisoes sorteadas depois da primeira (cada um, e
    sozinho) e a G-PESA so nas decisoes sorteadas dos dias 8 a 14. Nos controles, os campos da escolha segurada sao None."""
    c = orq.cerebro_de(registro)
    ms = c.motivos
    sem_reflexo = sum(1 for m in ms if not m["reflexo"])
    out = {"decisoes": len(ms), "sem_reflexo": sem_reflexo, "trocas": trocas_lp2(ms)}
    if not c.cd.redecidir_evento:
        return {**out, "ligada": False, "seguradas": None, "frac_seguradas": None, "sequencias": None, "eventos": None,
                "influencia_sorteadas": None}
    seq, comp, tetos, n = 0, 0, 0, 0
    for m in ms:
        if m["segurada"]:
            n += 1
            continue
        if n:
            seq += 1
            comp += n
            tetos += "E-TETO" in m["evento"]
            n = 0
    if tetos != c.m.estado.tetos:
        raise RuntimeError(f"as sequencias que acabaram no teto ({tetos}) nao sao as do M-ESTADO ({c.m.estado.tetos})")
    seguradas = sum(1 for m in ms if m["segurada"])
    sorteadas = [m for m in ms[1:] if not m["segurada"]]
    eventos = {e: {"decisoes": sum(1 for m in sorteadas if e in m["evento"]), "sozinho": sum(1 for m in sorteadas if m["evento"] == [e])}
               for e in EVENTOS}
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    janela = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    sondas = [(k * passo, {mod: m["sondas"][f"{mod}_decidiu"] for mod in MODULOS}) for k, m in enumerate(ms) if not m["segurada"]]
    na_janela = [s for s in sondas if janela[0] <= s[0] < janela[1]]
    return {**out, "ligada": True, "seguradas": seguradas, "frac_seguradas": seguradas / sem_reflexo if sem_reflexo else None,
            "sequencias": {"fechadas": seq, "decisoes_nas_fechadas": comp, "media_n": comp / seq if seq else None, "tetos": tetos,
                           "frac_teto": tetos / seq if seq else None, "aberta_no_fim": n},
            "eventos": {"sorteadas_depois_da_primeira": len(sorteadas), "por_evento": eventos},
            "influencia_sorteadas": influencia_por_modulo(na_janela, janela, MODULOS)["frac"] if na_janela else None}


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida (o motor da C1, que grava o corpo), gravada, rejogada do disco (G1), conferida (as falhas altas, os fins e, nos
    bracos R, o `conferir_redecidir`, chamado pelo `conferir_mecanismo`) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab = lr.viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    if orq.cerebro_de(registro).cd.redecidir_evento != (braco in BRACOS_R):
        raise RuntimeError(f"{braco}: a subchave da C3 nao e a do braco (A8.2)")
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    fins = conferir_fins(braco, registro)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins, "metas": lr.trocas_de_meta(registro),
            "redecidir": medidas_redecidir(registro, cfg["dias"]),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise
def _celulas(lugar: str) -> tuple:
    return tuple((d, lugar) for d in DONOS)


def nivel(registros: list[dict], braco: str, medida, lugar: str) -> dict:
    """{(base, semente): a media da medida nas 4 celulas do lugar} (a unidade de A8.4)"""
    return orq.por_unidade(registros, braco, None, medida, _celulas(lugar))


def diferenca(registros: list[dict], a: str, b: str, medida, lugar: str) -> dict:
    """{(base, semente): a media, nas 4 celulas do lugar, de medida(a) - medida(b) no mesmo dono} (as celulas com None num dos bracos
    ficam fora, a regra do `por_unidade`)"""
    return orq.por_unidade(registros, a, b, medida, _celulas(lugar))


def classe(ic: dict, margem: float = MARGEM) -> dict:
    """a classe de A6.6 (A8.6), na ordem, com a margem deste adendo"""
    return lr.classe(ic, margem)


def estimativa(difs: dict, margem: float = MARGEM) -> dict:
    """o descritivo de um valor por unidade: a media, o dp e o IC95 pelo t (A4.4.6) sobre as unidades, com a classe de A6.6"""
    ic = orq.ic_t([v for _, v in sorted(difs.items())])
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]},
            "classe": classe(ic, margem), "motivo": ic["motivo"]}


EPISODIO = lr.EPISODIO
FRAC_SEGURADAS = lambda r: r["redecidir"]["frac_seguradas"]                              # noqa: E731
FRAC_TETO = lambda r: r["redecidir"]["sequencias"]["frac_teto"]                          # noqa: E731


def _contraste(registros: list[dict], a: str, b: str, lugar: str, rotulo: str, boot: dict) -> dict:
    difs = diferenca(registros, a, b, EPISODIO, lugar)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    return {"contraste": rotulo, **c, "classe": classe(ic), "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(estimativa(difs)["dp"], c["n"])}


def primario(registros: list[dict], boot: dict) -> dict:
    """A8.4: o P-R, M3*R - M3* na taxa por episodio, nas 4 celulas do `longe_fixo`, o IC95 pelo t sobre as unidades; passa se o limite
    inferior > 0. Ao lado: o p unilateral, o g1 com a ressalva, o IC percentil do bootstrap (rotulado) e a margem efetiva."""
    c = _contraste(registros, "M3R", "M3", PRIMARIO, "P-R: M3*R - M3*, a taxa de fechamento por episodio, nas 4 celulas do longe_fixo", boot)
    return {**c, "passa": c["ic95"]["ic_inferior"] is not None and c["ic95"]["ic_inferior"] > 0}


def guarda(registros: list[dict], boot: dict) -> dict:
    """A8.4: a G-COMEDOURO, o mesmo contraste nas 4 celulas do comedouro; falha so com a classe "< 0" de A6.6 (o IC inteiro abaixo de 0 e
    fora da margem). Sem previsao de sinal alem de "nao < 0"."""
    c = _contraste(registros, "M3R", "M3", GUARDA, "G-COMEDOURO: M3*R - M3*, a taxa por episodio, nas 4 celulas do comedouro", boot)
    return {**c, "menor_que_0": c["classe"]["classe"] == "< 0"}


def secundarias(registros: list[dict], boot: dict) -> dict:
    """A8.4: S1 (M2R - M2 no `longe_fixo`) e S2 (M3*R - M3* no longe sorteado), o mesmo teste, sem gate e sem previsao de sinal"""
    return {"S1": {**_contraste(registros, "M2R", "M2", PRIMARIO, "S1: M2R - M2, a taxa por episodio, no longe_fixo", boot), "previsao": None},
            "S2": {**_contraste(registros, "M3R", "M3", "longe", "S2: M3*R - M3*, a taxa por episodio, no longe sorteado", boot),
                   "previsao": None}}


def premissas(registros: list[dict]) -> dict:
    """A8.5: a P-SEGURA (no M3*R, nas 4 celulas do `longe_fixo`, a fracao das decisoes sem o reflexo que foram seguradas, por unidade; o
    limite inferior do IC95 pelo t >= 0,10), a P-EVENTO (no M3*R, no `longe_fixo`, a fracao das sequencias seguradas fechadas que acabaram
    com o E-TETO, por unidade; o limite superior do IC95 pelo t <= 0,25) e a G-ELEGIVEL-EP de A6.4 (no M3* e no M3*R, no `longe_fixo`, ao
    menos 80 % das vidas com 3 episodios ou mais). Se uma falha, o primario e inconclusivo por premissa."""
    segura = estimativa(nivel(registros, "M3R", FRAC_SEGURADAS, PRIMARIO))
    segura["passa"] = segura["ic95"]["ic_inferior"] is not None and segura["ic95"]["ic_inferior"] >= P_SEGURA_LIMIAR
    segura["limiar"] = P_SEGURA_LIMIAR
    evento = estimativa(nivel(registros, "M3R", FRAC_TETO, PRIMARIO))
    evento["passa"] = evento["ic95"]["ic_superior"] is not None and evento["ic95"]["ic_superior"] <= P_EVENTO_LIMIAR
    evento["limiar"] = P_EVENTO_LIMIAR
    elegivel = {}
    for b in ("M3", "M3R"):
        vs = [r for r in registros if r["braco"] == b and r["lugar"] == PRIMARIO]
        frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= G_ELEGIVEL_EP["episodios"]) / len(vs)
        elegivel[b] = {"frac_vidas": frac, "vidas": len(vs), "limiar": G_ELEGIVEL_EP["frac_vidas"], "passa": frac >= G_ELEGIVEL_EP["frac_vidas"]}
    eleg = {"por_braco": elegivel, "passa": all(v["passa"] for v in elegivel.values())}
    return {"P-SEGURA": segura, "P-EVENTO": evento, "G-ELEGIVEL-EP": eleg,
            "conclusivo": segura["passa"] and evento["passa"] and eleg["passa"]}


def leitura(prim: dict, prem: dict, gua: dict, s1: dict) -> dict:
    """A8.7, a tabela da secao 1.5 da tarefa, na ordem (a primeira linha que serve). No P-R o primario manda: '> 0' e o primario passar;
    senao a classe de A6.6. A guarda le so "< 0" ou nao. O S1 sai ao lado, pela classe, e so muda a frase da linha 2."""
    pr = "> 0" if prim["passa"] else prim["classe"]["classe"]
    base = {"P-R": pr, "G-COMEDOURO": gua["classe"]["classe"], "S1": s1["classe"]["classe"], "ressalva_primario": prim["ressalva_assimetria"]}
    if not prem["conclusivo"]:
        return {**base, "linha": "inconclusivo por premissa (A8.5): o mecanismo nao segurou, segurou por tempo e nao por evento, ou os "
                                 "donos nao deram episodios; nada se decide", "o_que_se_faz": "registrado; nada se decide"}
    if pr == "> 0" and not gua["menor_que_0"]:
        mem = {"> 0": "o efeito nao precisa da memoria", "≈ 0": "o efeito passa pelo M-MEM"}.get(base["S1"], "o S1 nao diz se o efeito "
                                                                                                    "precisa da memoria")
        return {**base, "linha": "nestas condicoes, sortear a cada decisao explica parte da falha no longe, sem custo perto da racao; " + mem,
                "o_que_se_faz": "o redecidir por evento vira candidato; volta ao Matheus. Nao vai ao jogo sem a L3"}
    if pr == "> 0":
        return {**base, "linha": "ajuda longe da racao e atrapalha perto dela",
                "o_que_se_faz": "registrado; volta ao Matheus; nao vira candidato"}
    if pr == "≈ 0":
        return {**base, "linha": "nestas condicoes, a decisao a cada passo nao e a causa: o que o gatilho alcanca (as quebras fora do "
                                 "reflexo) nao move o episodio",
                "o_que_se_faz": "registrado; a C4 segue como planejada; nenhum mecanismo novo de decisao sem plano proprio"}
    if pr == "< 0":
        return {**base, "linha": "segurar a escolha piora o pet", "o_que_se_faz": "registrado como esta; a subchave fica desligada"}
    return {**base, "linha": "registrado como indeterminado; nada se decide", "o_que_se_faz": "registrado como indeterminado"}


# ------------------------------------------------------------------ o descritivo (A8.8; sem gate)
def _contrastes(registros: list[dict], medida, pares=PARES) -> dict:
    return {f"{lu}|{a} - {b}": estimativa(diferenca(registros, a, b, medida, lu)) for lu in LUGARES for a, b in pares}


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


def trocas(registros: list[dict]) -> dict:
    """A8.8, item 1 (a LP-2): as trocas por decisao por vida, em nivel e nos contrastes de cada braco R com o seu controle, por lugar; o
    motivo (o dormir pelo sorteio ou outra unidade) so somado por braco e lugar. Ao lado, rotulados como dependentes do braco, os fins
    `trocou` por intencao de hoje (o `trocas_de_meta` da C1)."""
    total = lambda r: r["redecidir"]["trocas"]["total"]                  # noqa: E731
    return {"por_decisao": {"niveis": _niveis(registros, total), "contrastes": _contrastes(registros, total)},
            "motivo_somado": _somar(registros, lambda r: r["redecidir"]["trocas"]),
            "por_intencao_de_hoje": {"rotulo": "a contagem por intencao muda com o mecanismo (LP-2): so leitura, sem contraste",
                                     "niveis": _niveis(registros, lambda r: r["metas"]["trocas_total"]),
                                     "fins_somados": _somar(registros, lambda r: {f"{t}|{m}": n for t, ms in r["metas"]["fins"].items()
                                                                                  for m, n in ms.items()})}}


def mecanismo(registros: list[dict]) -> dict:
    """A8.8, item 2: so nos bracos R e so por braco (nenhum grupo que o mecanismo cria vira contraste; LP-2): a fracao das decisoes sem o
    reflexo seguradas, o comprimento medio das sequencias seguradas, a fracao delas que acabou no teto e, somados, os eventos das decisoes
    sorteadas (cada um e sozinho) e as sequencias"""
    eventos = _somar(registros, lambda r: {f"{e}|{k}": n for e, d in r["redecidir"]["eventos"]["por_evento"].items() for k, n in d.items()}
                     | {"sorteadas_depois_da_primeira": r["redecidir"]["eventos"]["sorteadas_depois_da_primeira"]}, BRACOS_R)
    seqs = _somar(registros, lambda r: {k: v for k, v in r["redecidir"]["sequencias"].items() if k in ("fechadas", "decisoes_nas_fechadas",
                                                                                                         "tetos", "aberta_no_fim")}, BRACOS_R)
    return {"frac_seguradas": _niveis(registros, FRAC_SEGURADAS, BRACOS_R),
            "media_n_sequencia": _niveis(registros, lambda r: r["redecidir"]["sequencias"]["media_n"], BRACOS_R),
            "frac_teto": _niveis(registros, FRAC_TETO, BRACOS_R), "eventos_somados": eventos, "sequencias_somadas": seqs}


def corpo(registros: list[dict]) -> dict:
    """A8.8, item 3: as medidas da C5 (AD6-4, como estao), a exaustao e a privacao de hoje, em nivel e nos contrastes de cada par"""
    out = {"limiar": lr.LIMIAR_CORPO, "status": "as definicoes da AD6-4, DECIDIDAS, SEM FONTE",
           "privacao_de_hoje": {"niveis": _niveis(registros, lambda r: r["privacao"]), "contrastes": _contrastes(registros, lambda r: r["privacao"])},
           "exaustao": {"niveis": _niveis(registros, lambda r: r["exaustao"]), "contrastes": _contrastes(registros, lambda r: r["exaustao"])}}
    for j in JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f)}
    return out


def faixas_d0(registros: list[dict]) -> dict:
    """A8.8, item 4: por lugar x braco x faixa de d0, os episodios (n), os fechados e a taxa (somas sobre as vidas), sem contraste. A
    ressalva da LP-2 da C1: a faixa depende de onde o pet esta, e o mecanismo muda isso."""
    g = orq.geometria()
    soma = {(lu, b): {f: [0, 0] for f in lr.FAIXAS_D0} for lu in LUGARES for b in BRACOS}
    for r in registros:
        for _k, d0, _w, _fim, motivo in r["episodios_fome"]["episodios"]:
            acum = soma[(r["lugar"], r["braco"])][lr._faixa(d0, g)]
            acum[0] += 1
            acum[1] += motivo == "fechou"
    return {"ressalva": "a faixa de d0 depende de onde o pet esta, e o mecanismo muda isso (LP-2): so leitura",
            "por_lugar_braco_faixa": {f"{lu}|{b}": {f: {"n": n, "fechados": fe, "taxa": fe / n if n else None}
                                                    for f, (n, fe) in soma[(lu, b)].items()} for lu in LUGARES for b in BRACOS}}


def outros(registros: list[dict]) -> dict:
    """A8.8, item 5: a taxa por episodio por braco e lugar e os contrastes; a G-PESA de cada modulo como hoje (as seguradas no denominador,
    com `*_decidiu` falso) e, nos bracos R, so nas decisoes sorteadas; os episodios por vida; por dono, so a media da taxa por episodio"""
    por_dono = {}
    for d in DONOS:
        for lu in LUGARES:
            for b in BRACOS:
                vs = [EPISODIO(r) for r in registros if r["dono"] == d and r["lugar"] == lu and r["braco"] == b and EPISODIO(r) is not None]
                if vs:
                    por_dono[f"{d}|{lu}|{b}"] = statistics.fmean(vs)
    return {"episodio": {"niveis": _niveis(registros, EPISODIO), "contrastes": _contrastes(registros, EPISODIO)},
            "g_pesa_por_modulo": {m: _niveis(registros, lambda r, m=m: r["influencia"][m]) for m in MODULOS},
            "g_pesa_sorteadas": {m: _niveis(registros, lambda r, m=m: None if r["redecidir"]["influencia_sorteadas"] is None
                                            else r["redecidir"]["influencia_sorteadas"][m], BRACOS_R) for m in MODULOS},
            "episodios_por_vida": _niveis(registros, lambda r: r["episodios_fome"]["n"]),
            "fins_somados": _somar(registros, lambda r: r["fins_conferidos"]), "por_dono": por_dono}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise de A8.4 a A8.8, com a classe de cada contraste e a leitura"""
    prim, gua, sec, prem = primario(registros, boot), guarda(registros, boot), secundarias(registros, boot), premissas(registros)
    return {"primario": prim, "guarda": gua, "secundarias": sec, "premissas": prem, "leitura": leitura(prim, prem, gua, sec["S1"]),
            "descritivo": {"trocas": trocas(registros), "mecanismo": mecanismo(registros), "corpo": corpo(registros),
                           "faixas_d0": faixas_d0(registros), "outros": outros(registros)},
            "nao_demonstra": ["que o modular supera o A", "prontidao do prototipo", "tamanho de efeito fora das condicoes da run",
                              "que o mecanismo e novo", "o efeito combinado com a corrida da C2 (D-C2-4)"]}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8 e A8.9)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; A8.10)")
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
            "unidades": unidades, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {**orq.SUBCHAVES_CONSERTO, **orq.SUBCHAVES_C3}[b] for b in BRACOS},
            "fins_conhecidos": {b: sorted(fins_conhecidos(b)) for b in BRACOS},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
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
