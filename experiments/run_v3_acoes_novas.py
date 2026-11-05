"""A run unica da AN4, o passeio ligado contra desligado (docs/PLANO_ANALISE_V3_ACOES_NOVAS.md, APROVADO pelo Matheus em 2026-11-05;
docs/TAREFA_V3_ACOES_NOVAS.md, secoes 3.6 e 4). Pergunta: o passeio (o vagar que segura o destino, a subchave `passeio` da AN2) faz o pet
com o DigiBrain modular se mover mais, sem piorar o cuidado das necessidades perto do comedouro?

O desenho (secoes 2 e 3 do plano; AN3-1, AN3-2, AN3-9): o cenario da C4 (o do MVP, os 4 donos sem ensino, 14 dias, 16 interacoes por dia,
o motor que grava o corpo para a C5), os bracos LAB (o REL da C4, `SUBCHAVES_AN["LAB"]` do orquestrador do prototipo) e LAB+P (o mesmo com
a `passeio`), as celulas 4 donos x 2 lugares (o comedouro, a guarda; o `longe_fixo`, a secundaria), 16 vidas por unidade, as bases 78101,
78202, 78303, 78404 e 78505, K = 40 por base (200 unidades, 3 200 vidas), o prefixo `digibrain_prototipo`. A run roda uma vez, sem
calibracao nem piloto.

Em toda vida (secao 11): o replay bit a bit do disco (o G1), o T-CENARIO-1, o G-MECANISMO e a conferencia do credito (com a decisao que
abre o passeio lida como a primeira dele; o desvio D-AN4-1), a `conferir_memoria` da C4 (o papel REL nos dois bracos), os fins conhecidos
lidos da `estado.py` com a config de cada braco (a licao do #507) e a conferencia do passeio (a urgencia, o alvo, o F, o LAB sem passeio).
As medidas: as do prototipo (`orq.medidas`, `conserto=True`), as da C5, o MOV (`metrics.movimento_nas_decisoes`, com a posicao de cada
decisao, gravada so para ele) e o passeio (secao 4.4).

A analise (secoes 6 a 9), no `resultado.json`: as premissas (P-PASSEIO e G-ELEGIVEL-EP), a guarda G-COMEDOURO-AN (LAB+P - LAB na taxa por
episodio de fome, nas 4 celulas do comedouro, o IC95 pelo t; falha so com a classe "< 0" de A6.6 com delta = 0,018), o MOV (LAB+P - LAB
nas 8 celulas; "o passeio move o pet" so com o limite inferior acima de 0), a linha de 7.4 e o descritivo da secao 8.

A trava (secao 11): o plano com "APROVADO pelo Matheus" no cabecalho, a faixa 78101...78505 em FAIXAS_RESERVADAS, o registro da run (a
secao 14 do plano) com os sha256 de hoje, so as bases, o K, os dias e o orcamento do plano, no maximo 4 processos, e nenhuma gravacao por
cima de uma pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa e sem o K, com menos dias se a config
pedir; a fumaca nao e dado da AN4.

    python experiments/run_v3_acoes_novas.py --config experiments/configs/v3_acoes_novas/acoes_novas.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import re
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
import run_v2_memoria_autobio as ma  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import movimento_nas_decisoes  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_ACOES_NOVAS.md"
PREFIXO = orq.PREFIXO                                                                 # secao 3 (o da reavaliacao, da L-2 e das C1 a C4)
FASE = "acoes_novas"
BASES = (78101, 78202, 78303, 78404, 78505)                                           # secao 3 (AN3-9)
K_POR_BASE = 40                                                                       # secao 6 (AN3-2): 200 unidades
FAIXA = (78101, 78505)
SAIDA = "artifacts_v3_acoes_novas/run"                                                # secao 11: a pasta-mae tem o hoje.json e o poder
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # secao 2 (AN3-1)
MAX_PROCESSOS = 4                                                                     # secao 10 (V3-D8)
DONOS = orq.DONOS
GUARDA, SECUNDARIO = "comedouro", "longe_fixo"                                        # secao 2 (AN3-1)
LUGARES = (GUARDA, SECUNDARIO)
BRACOS = ("LAB", "LAB+P")                                                             # secao 2 (AN3-1)
CONTROLE, TRATADO = BRACOS
CELULAS = tuple((d, lu) for d in DONOS for lu in LUGARES)
CHAVES_CONFIG = lr.CHAVES_CONFIG
MARGEM = 0.018                                                                        # secao 6 (AN3-2), SEM FONTE: o "~ 0"
P_PASSEIO_LIMIAR = orq.G_PESA["limiar"]                                               # 7.1 (AN3-4): o 0,01 da G-PESA, SEM FONTE
G_ELEGIVEL_EP = orq.G_ELEGIVEL_EP                                                     # 7.1: a de A6.4, como esta
JANELAS_CORPO = lr.JANELAS_CORPO
MODULOS = ma.MODULOS
PAPEL_DA_MEMORIA = "REL"                                                              # os dois bracos tem a memoria do REL da C4
PASSEIO = ["explorar", "passeio"]
VAGAR = ["explorar", "vagar"]
FINS_SEM_FRUSTRACAO = ("achou", "interrompido")                                       # o "achou" (2026-10-26) e o "interrompido" (AN-5)
REGISTRO_TITULO = "## 14. O registro da run"


# ================================================================== a config e a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(plano: str) -> None:
    """a trava da secao 11: o cabecalho do plano (antes da primeira secao) tem uma linha de status so, e ela comeca com "**Status:
    APROVADO pelo Matheus"; um status PROPOSTO, ou nenhum, recusa a run"""
    cabecalho = []
    for x in plano.splitlines():
        if x.startswith("## "):
            break
        cabecalho.append(x)
    status = [x for x in cabecalho if x.startswith("**Status:")]
    if len(status) != 1 or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho (secao 11): {status or 'sem a linha do status'}")


def exigir_faixa_reservada() -> None:
    """a faixa 78101...78505 esta em FAIXAS_RESERVADAS (secao 3); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi_) == FAIXA for lo, hi_, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (secao 3)")


def arquivos_do_registro() -> list[str]:
    """os arquivos cujo sha256 vai ao registro da run (secao 11): o orquestrador, o do prototipo (e os que ele usa), a config, o
    `config.py`, o `engine.py`, o `metrics.py`, o `mundo.py` e todo `digilab/digibrain/`. O plano fica fora (ele guarda o registro)."""
    fixos = ["experiments/run_v3_acoes_novas.py", "experiments/run_v2_digibrain_prototipo.py", "experiments/run_v2_longe_regular.py",
             "experiments/run_v2_habito_intencao.py", "experiments/run_v2_memoria_autobio.py",
             "experiments/configs/v3_acoes_novas/acoes_novas.json",
             "digilab/config.py", "digilab/engine.py", "digilab/metrics.py", "digilab/mundo.py"]
    return fixos + [p.relative_to(RAIZ).as_posix() for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))]


def sha_dos_arquivos() -> dict:
    return {f: orq.rc._sha_arquivo(RAIZ / f) for f in arquivos_do_registro()}


def registro_do_plano(plano: str) -> dict:
    """os sha256 da secao 14 do plano (o registro da run): as linhas `- \\`<arquivo>\\`: \\`<sha256>\\``"""
    i = plano.find("\n" + REGISTRO_TITULO)
    if i < 0:
        raise RuntimeError(f"o registro da run ({REGISTRO_TITULO}) nao esta no plano: nenhuma vida antes dele (secao 11)")
    j = plano.find("\n## ", i + 1)
    trecho = plano[i: len(plano) if j < 0 else j]
    shas = dict(re.findall(r"^- `([^`]+)`: `([0-9a-f]{64})`$", trecho, re.M))
    if not shas:
        raise RuntimeError("o registro da run sem os sha256")
    return shas


def exigir_registro(plano: str) -> None:
    """o registro da run (a secao 14, num commit antes da primeira vida) com os mesmos arquivos e os sha256 de hoje; um arquivo mudado
    depois do registro recusa a run (o registro novo vai num commit antes dela)"""
    gravado, hoje = registro_do_plano(plano), sha_dos_arquivos()
    if set(gravado) != set(hoje):
        raise RuntimeError(f"o registro da run lista outros arquivos: faltam {sorted(set(hoje) - set(gravado))}, "
                           f"sobram {sorted(set(gravado) - set(hoje))}")
    mudados = sorted(f for f in hoje if gravado[f] != hoje[f])
    if mudados:
        raise RuntimeError(f"os arquivos mudaram depois do registro da run: {mudados}")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'acoes_novas', que segue o plano a letra (secao 11): outra base, outro K, outros dias ou outro
    orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o plano sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (secao 3), o orcamento (secao 2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (secao 3)")
    exigir_faixa_reservada()
    plano = _plano()
    exigir_plano_aprovado(plano)
    erros = []
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_POR_BASE:
        erros.append(f"K por base {u['k']} (o plano: {K_POR_BASE})")
    if erros:
        raise ValueError(f"a {FASE} segue o plano a letra: {erros}")
    exigir_registro(plano)
    return FASE


# ================================================================== a vida
def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: a do `lr.viver` (o cerebro do conserto com as subchaves do braco, o MotorGravaCorpo), com a posicao do pet no tick de
    cada decisao (o `x, y` do `Observacao.mundo`, a entrada do `adapt.agir`; so para o MOV). So le: o G1 rejoga a vida com as fabricas sem
    o coletor e confere bit a bit. Devolve (o motor, o registro, as fabricas, as posicoes)."""
    fp, _ = orq.fabricas(braco, dono, semente, dias, orcamento_por_dia, conserto=True)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    registro = fp(CONFIG_PADRAO)
    posicoes: list[tuple] = []
    agir = registro.agir

    def agir_e_ler(obs, rng):
        if obs.mundo is None:
            raise RuntimeError("a decisao sem o mundo na Observacao: o MOV fica sem a posicao")
        posicoes.append((obs.mundo.x, obs.mundo.y))
        return agir(obs, rng)

    registro.agir = agir_e_ler
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    del registro.agir                                 # o registro volta a ser o da fabrica
    return motor, registro, (fp, fm), posicoes


def fins_conhecidos(braco: str) -> frozenset:
    """os fins que a `estado.py` pode dar com a config do braco (as chaves de `EstadoDinamico.fins`; no LAB+P, com o `interrompido`)"""
    return hi.fins_conhecidos(braco)


def conferir_fins(braco: str, registro) -> dict:
    """os fins das intencoes da vida, por motivo; falha alto com um fim desconhecido, com a contagem do registro diferente da do estado, ou
    com uma retomada ou um `n_susp` (a do orquestrador da C2)"""
    return hi.conferir_fins(braco, registro)


def conferir_bracos(braco: str, c) -> None:
    """secao 11: a config do cerebro e a do braco; a `passeio` ligada exatamente no LAB+P; a C2, a C3 e a L-2 desligadas; a memoria do REL"""
    cd = c.cd
    if cd != orq.config_do_braco(braco, conserto=True):
        raise RuntimeError(f"{braco}: a config do cerebro nao e a do braco")
    if cd.passeio != (braco == TRATADO):
        raise RuntimeError(f"{braco}: a passeio {'desligada' if braco == TRATADO else 'ligada'}")
    if cd.credito_corrida or cd.redecidir_evento or cd.intencao_suspensa:
        raise RuntimeError(f"{braco}: a C2, a C3 ou a L-2 ligada (secao 0)")


class _VistaDoCredito:
    """o cerebro visto pela conferencia do credito do prototipo, com a decisao que abre cada passeio lida como a primeira dele (o desvio
    D-AN4-1): o motivo dela tem a escolha `explorar/vagar` (o M-ARB escolheu o vagar; o `abrir_passeio` troca a chave da opcao depois,
    no `escolher_alvo`), e a opcao do passeio comeca nela. So le; o resto e o cerebro."""

    def __init__(self, c, aberturas: dict) -> None:
        self._c = c
        self.motivos = [{**m, "escolha": aberturas[m["k"]]} if m["k"] in aberturas else m for m in c.motivos]

    def __getattr__(self, nome: str):
        return getattr(self.__dict__["_c"], nome)


def _urgencia(m: dict) -> int:
    u = m["afeto"]["urgencias"]
    return max(u.get(r, 0) for r in orq.NECESSIDADES_DO_PASSEIO)


def _do_passeio(m: dict) -> bool:
    return m.get("alvo", {}).get("do_passeio") is True


def aberturas_do_passeio(braco: str, c) -> dict:
    """{k: a chave do passeio aberto na decisao k}: as decisoes `explorar/vagar` com o alvo `do_passeio`, cada uma a `inicio` de um fim
    de passeio ou do passeio em curso no fim da vida. Falha alto: uma abertura sem passeio, um passeio sem abertura, o ponto do passeio
    diferente do alvo da abertura, ou o numero de aberturas diferente do contado pelo estado."""
    if braco != TRATADO:
        return {}
    ms = c.motivos
    passeios = {f["inicio"]: f["chave"] for m in ms for f in m["fins"] if f["chave"][:2] == PASSEIO}
    I = c.m.estado.I
    if I is not None and list(I["chave"][:2]) == PASSEIO:
        passeios[I["inicio"]] = [I["chave"][0], I["chave"][1], list(I["chave"][2])]
    abre = [m["k"] for m in ms if m["escolha"][:2] == VAGAR and _do_passeio(m)]
    if sorted(passeios) != abre:
        raise RuntimeError(f"{braco}: as aberturas do passeio {abre[:5]}... nao sao os inicios dos passeios {sorted(passeios)[:5]}...")
    for k in abre:
        a = ms[k]["alvo"]
        if [a["x"], a["y"]] != list(passeios[k][2]):
            raise RuntimeError(f"{braco}: o ponto do passeio aberto na decisao {k} nao e o alvo dela")
    if len(abre) != c.m.estado.passeios:
        raise RuntimeError(f"{braco}: {len(abre)} aberturas, o estado contou {c.m.estado.passeios}")
    return {k: list(passeios[k]) for k in abre}


def conferir_frustracao(braco: str, c) -> None:
    """o F do M-ESTADO refeito do registro, decisao a decisao (secao 11: o `interrompido` nao sobe o F, AN-5): cai pelo k_f_desce no
    contexto de cada decisao e sobe pelo k_f_sobe em cada fim sem meta, salvo o `achou` e o `interrompido`, na ordem em que acontecem (os
    fins da escolha da decisao k e os da consequencia dela, antes do contexto de k + 1; o `interrompido` de k + 1, no comeco dela). Falha
    alto com o F de uma decisao diferente do refeito. Nos dois bracos: no LAB, confere o modelo."""
    e, S, mul = c.m.estado, c.S, orq.mul
    F = 0
    for k, m in enumerate(c.motivos):
        if k > 0:
            for f in c.motivos[k - 1]["fins"]:
                if f["motivo"] == "interrompido":
                    continue                                    # o da decisao k - 1, antes do contexto dela
                if not f["meta"] and f["motivo"] not in FINS_SEM_FRUSTRACAO:
                    F = F + mul(e.k_f_sobe, S - F, S)
        # o interrompido de k: no comeco dela, sem subir o F
        F = F - mul(e.k_f_desce, F, S)
        if m["estado"]["F"] != F:
            raise RuntimeError(f"{braco}: o F da decisao {k} ({m['estado']['F']}) nao e o refeito ({F}): um fim subiu o F fora da regra")


def conferir_passeio(braco: str, c) -> dict:
    """secao 11, em toda vida, falhando alto. No LAB: nenhum `do_passeio`, nenhuma intencao de tipo `passeio`, nenhum `interrompido`,
    nenhum passeio no estado. No LAB+P: a decisao que continua um passeio (a escolha `explorar/passeio`) tem a urgencia de fome, higiene,
    energia e saude no limiar ou abaixo (4.4), o passeio dela em curso no estado, o alvo no ponto dele e `do_passeio`; o `interrompido` so
    acaba passeio; o F refeito (o `interrompido` nao sobe o F). Devolve as aberturas (para a conferencia do credito)."""
    ms = c.motivos
    if braco == CONTROLE:
        for m in ms:
            if "do_passeio" in m.get("alvo", {}) or (m["estado"]["I"] is not None and m["estado"]["I"][:2] == PASSEIO) \
                    or m["escolha"][:2] == PASSEIO or any(f["motivo"] == "interrompido" or f["chave"][:2] == PASSEIO for f in m["fins"]):
                raise RuntimeError(f"LAB: o passeio na decisao {m['k']}")
        if "passeio" in c.m.estado.estado_interno() or c.m.estado.passeios:
            raise RuntimeError("LAB: o passeio no estado")
        conferir_frustracao(braco, c)
        return {}
    lam = c.inatos.urgencia_lambda
    for m in ms:
        if m["escolha"][:2] == PASSEIO:
            if _urgencia(m) > lam:
                raise RuntimeError(f"LAB+P: a decisao {m['k']} continua um passeio com a urgencia {_urgencia(m)} > {lam} (3.2)")
            if m["estado"]["I"] != m["escolha"]:
                raise RuntimeError(f"LAB+P: a decisao {m['k']} continua um passeio que nao esta em curso")
            a = m.get("alvo")
            if a is None or a["tipo"] != "ponto" or [a["x"], a["y"]] != list(m["escolha"][2]) or a["do_passeio"] is not True \
                    or a["do_mem"] is not False:
                raise RuntimeError(f"LAB+P: o alvo da decisao {m['k']} nao e o ponto do passeio em curso")
        elif _do_passeio(m) and m["escolha"][:2] != VAGAR:
            raise RuntimeError(f"LAB+P: do_passeio na decisao {m['k']}, que nao e do passeio nem o abre")
        for f in m["fins"]:
            if f["motivo"] == "interrompido" and f["chave"][:2] != PASSEIO:
                raise RuntimeError(f"LAB+P: um interrompido fora do passeio na decisao {m['k']}")
    aberturas = aberturas_do_passeio(braco, c)
    conferir_frustracao(braco, c)
    return aberturas


def conferir_mecanismo(braco: str, registro, aberturas: dict) -> None:
    """o G-MECANISMO e o credito do prototipo (`orq.conferir_mecanismo`), com a vista do credito no LAB+P (D-AN4-1)"""
    c = orq.cerebro_de(registro)
    vista = _VistaDoCredito(c, aberturas) if aberturas else c
    orq.conferir_mecanismo(braco, bv_registro(vista), None)


def bv_registro(c):
    """o registro minimo que o `orq.cerebro_de` le (so o `_interna`)"""
    class _R:
        pass
    r = _R()
    r._interna = c
    return r


def medidas_passeio(braco: str, c, dias: int) -> dict | None:
    """4.4 (so no LAB+P; no LAB, None, a licao LP-2): os passeios abertos e por dia, a duracao dos que acabaram (em decisoes), os fins por
    motivo, a P-PASSEIO (a fracao das decisoes fora do dormir que continuam um passeio), a urgencia maxima nas decisoes que abrem um
    passeio e o credito descartado pelo gesto do dono"""
    if braco != TRATADO:
        return None
    ms = c.motivos
    fins = [f for m in ms for f in m["fins"] if f["chave"][:2] == PASSEIO]
    fora = [m for m in ms if m["acao"] != "dormir"]
    abre = [m for m in ms if m["escolha"][:2] == VAGAR and _do_passeio(m)]
    por_motivo = {x: 0 for x in sorted(fins_conhecidos(braco))}
    for f in fins:
        por_motivo[f["motivo"]] += 1
    descartados = sum(1 for f in fins if f.get("credito") == "gesto")
    if descartados != c.m.estado.descartados:
        raise RuntimeError(f"LAB+P: {descartados} creditos descartados no registro, o estado contou {c.m.estado.descartados}")
    return {"abertos": c.m.estado.passeios, "por_dia": c.m.estado.passeios / dias, "acabados": len(fins),
            "duracao_media": statistics.fmean(f["n"] for f in fins) if fins else None,
            "fins": por_motivo,
            "p_passeio": sum(1 for m in fora if m["escolha"][:2] == PASSEIO) / len(fora) if fora else None,
            "decisoes_que_continuam": sum(1 for m in ms if m["escolha"][:2] == PASSEIO),
            "urgencia_na_abertura": {"n": len(abre), "maxima": max((_urgencia(m) for m in abre), default=None),
                                     "media": statistics.fmean(_urgencia(m) for m in abre) if abre else None},
            "credito_descartado": descartados}


def medidas_movimento(c, posicoes: list, dias: int) -> dict:
    """4.3: o MOV, a distancia por dia e o zigue-zague (as corridas de `explorar`), pela funcao do `metrics.py`"""
    ms = c.motivos
    if len(posicoes) != len(ms):
        raise RuntimeError(f"{len(posicoes)} posicoes para {len(ms)} decisoes")
    return movimento_nas_decisoes([(m["acao"], x, y) for m, (x, y) in zip(ms, posicoes)], dias)


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida (o motor da C1, que grava o corpo, com a posicao por decisao), gravada, rejogada do disco (G1), conferida (as falhas
    altas da secao 11) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, posicoes = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    c = orq.cerebro_de(registro)
    conferir_bracos(braco, c)
    aberturas = conferir_passeio(braco, c)
    conferir_mecanismo(braco, registro, aberturas)
    ma.conferir_memoria(PAPEL_DA_MEMORIA, c)
    fins = conferir_fins(braco, registro)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "movimento": medidas_movimento(c, posicoes, cfg["dias"]), "passeio": medidas_passeio(braco, c, cfg["dias"]),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise
def _celulas(lugar: str | None) -> tuple:
    return CELULAS if lugar is None else tuple((d, lugar) for d in DONOS)


def nivel(registros: list[dict], braco: str, medida, lugar: str | None) -> dict:
    """{(base, semente): a media da medida nas 4 celulas do lugar (None: as 8)} (a unidade de 4.1)"""
    return orq.por_unidade(registros, braco, None, medida, _celulas(lugar))


def diferenca(registros: list[dict], a: str, b: str, medida, lugar: str | None) -> dict:
    """{(base, semente): a media, nas celulas do lugar (None: as 8), de medida(a) - medida(b) no mesmo dono} (as celulas com None num dos
    bracos ficam fora, a regra do `por_unidade`)"""
    return orq.por_unidade(registros, a, b, medida, _celulas(lugar))


def classe(ic: dict, margem: float = MARGEM) -> dict:
    """a classe de A6.6 (secao 6), na ordem, com a margem deste plano"""
    return lr.classe(ic, margem)


def estimativa(difs: dict, margem: float = MARGEM) -> dict:
    """o descritivo de um valor por unidade: a media, o dp e o IC95 pelo t (A4.4.6) sobre as unidades, com a classe de A6.6"""
    return ma.estimativa(difs, margem)


EPISODIO = lr.EPISODIO
MOV = lambda r: r["movimento"]["mov"]                                                  # noqa: E731
DISTANCIA = lambda r: r["movimento"]["distancia_por_dia"]                              # noqa: E731
P_PASSEIO = lambda r: r["passeio"]["p_passeio"]                                        # noqa: E731


def _contraste(registros: list[dict], medida, lugar: str | None, rotulo: str, boot: dict) -> dict:
    difs = diferenca(registros, TRATADO, CONTROLE, medida, lugar)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    return {"contraste": rotulo, **c, "classe": classe(ic), "margem": MARGEM,
            "margem_efetiva": lr.margem_efetiva(estimativa(difs)["dp"], c["n"])}


def guarda(registros: list[dict], boot: dict) -> dict:
    """7.2: a G-COMEDOURO-AN, LAB+P - LAB na taxa por episodio nas 4 celulas do comedouro; falha so com a classe "< 0" de A6.6"""
    c = _contraste(registros, EPISODIO, GUARDA, "G-COMEDOURO-AN: LAB+P - LAB, a taxa por episodio, nas 4 celulas do comedouro", boot)
    return {**c, "falha": c["classe"]["classe"] == "< 0"}


def movimento(registros: list[dict], boot: dict) -> dict:
    """7.3: o MOV, LAB+P - LAB nas 8 celulas; "o passeio move o pet" so com o limite inferior do IC95 acima de 0. A classe sai so como
    descricao (a margem foi feita para a taxa por episodio)."""
    c = _contraste(registros, MOV, None, "MOV: LAB+P - LAB, a fracao das decisoes fora do dormir que saem do lugar, nas 8 celulas", boot)
    lo = c["ic95"]["ic_inferior"]
    return {**c, "move": lo is not None and lo > 0, "classe_so_descricao": True}


def premissas(registros: list[dict]) -> dict:
    """7.1: a P-PASSEIO (no LAB+P, nas 4 celulas do comedouro, a fracao das decisoes fora do dormir que continuam um passeio, por
    unidade; o limite inferior do IC95 pelo t > 0,01) e a G-ELEGIVEL-EP de A6.4 (no LAB e no LAB+P, no comedouro, ao menos 80 % das vidas
    com 3 episodios ou mais). Se uma falha, a guarda e inconclusiva por premissa."""
    pp = estimativa(nivel(registros, TRATADO, P_PASSEIO, GUARDA))
    pp["passa"] = pp["ic95"]["ic_inferior"] is not None and pp["ic95"]["ic_inferior"] > P_PASSEIO_LIMIAR
    pp["limiar"] = P_PASSEIO_LIMIAR
    elegivel = {}
    for b in BRACOS:
        vs = [r for r in registros if r["braco"] == b and r["lugar"] == GUARDA]
        frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= G_ELEGIVEL_EP["episodios"]) / len(vs)
        elegivel[b] = {"frac_vidas": frac, "vidas": len(vs), "limiar": G_ELEGIVEL_EP["frac_vidas"], "passa": frac >= G_ELEGIVEL_EP["frac_vidas"]}
    eleg = {"por_braco": elegivel, "passa": all(v["passa"] for v in elegivel.values())}
    return {"P-PASSEIO": pp, "G-ELEGIVEL-EP": eleg, "conclusivo": pp["passa"] and eleg["passa"]}


def leitura(prem: dict, gua: dict, mov: dict) -> dict:
    """7.4, na ordem (a primeira linha que serve). O porte (AN5) so se a guarda nao falhar (AN-7). O LONGE-AN, o corpo e o descritivo nao
    mudam a linha."""
    base = {"G-COMEDOURO-AN": gua["classe"]["classe"], "sinal_da_guarda": gua["classe"]["sinal"], "MOV_move": mov["move"],
            "ressalva_da_guarda": gua["ressalva_assimetria"]}
    if not prem["conclusivo"]:
        return {**base, "linha": 1, "o_que_diria": "inconclusivo por premissa: o passeio quase nao durou perto da racao, ou os donos nao "
                                                   "deram episodios", "an5_pode_rodar": False,
                "o_que_se_faz": "registrado; a AN5 nao roda (inconclusivo nao e 'nao falhou'); volta ao Matheus (AN3-8)"}
    if gua["falha"]:
        return {**base, "linha": 2, "o_que_diria": "a guarda falha: nestas condicoes, o passeio tira o pet do comedouro", "an5_pode_rodar": False,
                "o_que_se_faz": "registrado como esta; a passeio fica desligada; a AN5 nao roda"}
    if mov["move"]:
        return {**base, "linha": 3, "o_que_diria": "a guarda passa, e o passeio move o pet", "an5_pode_rodar": True,
                "o_que_se_faz": "a AN5 pode rodar (a AN-7); o Matheus ve no jogo"}
    return {**base, "linha": 4, "o_que_diria": "a guarda passa, e o Python nao mostra mais movimento: o passeio muda para onde o pet anda, "
                                               "nao quanto (o nulo escrito na secao 1)", "an5_pode_rodar": True,
            "o_que_se_faz": "a AN5 pode rodar (a AN-7), e o relato diz que o MOV nao subiu; o Matheus decide jogando (AN3-7)"}


# ------------------------------------------------------------------ o descritivo (secao 8; sem gate)
def _niveis(registros: list[dict], medida, bracos: tuple = BRACOS) -> dict:
    return {f"{lu}|{b}": estimativa(nivel(registros, b, medida, lu)) for lu in LUGARES for b in bracos}


def _contrastes(registros: list[dict], medida) -> dict:
    return {f"{lu}|LAB+P - LAB": estimativa(diferenca(registros, TRATADO, CONTROLE, medida, lu)) for lu in LUGARES}


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


def longe(registros: list[dict], boot: dict) -> dict:
    """8, item 1: a secundaria LONGE-AN (LAB+P - LAB na taxa por episodio, no `longe_fixo`, sem previsao de sinal, sem gate), a taxa por
    braco e lugar e os episodios de fome por vida"""
    return {"LONGE-AN": {**_contraste(registros, EPISODIO, SECUNDARIO, "LONGE-AN: LAB+P - LAB, a taxa por episodio, no longe_fixo", boot),
                         "previsao": None},
            "episodio": {"niveis": _niveis(registros, EPISODIO), "contrastes": _contrastes(registros, EPISODIO)},
            "episodios_fome_por_vida": _niveis(registros, lambda r: r["episodios_fome"]["n"])}


def zigue_zague(registros: list[dict]) -> dict:
    """8, item 2: o zigue-zague so em nivel, por braco e lugar (a LP-2): as somas das vidas, como a AN0 somou (o liquido somado sobre o
    caminho somado; os pares que invertem sobre os pares)"""
    somas = _somar(registros, lambda r: {k: r["movimento"]["zigue_zague"][k] for k in
                                         ("corridas_de_2_ou_mais", "liquido", "caminho", "pares", "pares_que_invertem")})
    return {k: {**s, "liquido_sobre_caminho": s["liquido"] / s["caminho"] if s["caminho"] else None,
                "fracao_que_inverte": s["pares_que_invertem"] / s["pares"] if s["pares"] else None} for k, s in somas.items()}


def descritivo_movimento(registros: list[dict]) -> dict:
    """8, item 2: o MOV e a distancia por dia por braco e lugar, em nivel e nos contrastes; o zigue-zague so em nivel"""
    return {"mov": {"niveis": _niveis(registros, MOV), "contrastes": _contrastes(registros, MOV)},
            "distancia_por_dia": {"niveis": _niveis(registros, DISTANCIA), "contrastes": _contrastes(registros, DISTANCIA)},
            "zigue_zague": zigue_zague(registros), "rotulo": "as classes de A6.6 fora da taxa por episodio so como descricao"}


def descritivo_passeio(registros: list[dict]) -> dict:
    """8, item 3 (so no LAB+P, por lugar, sem contraste): os passeios por dia, a duracao, os fins somados, a P-PASSEIO nos dois lugares, a
    urgencia maxima nas aberturas e o credito descartado"""
    so = (TRATADO,)
    vs = {lu: [r for r in registros if r["braco"] == TRATADO and r["lugar"] == lu] for lu in LUGARES}
    duracoes = {lu: [r["passeio"]["duracao_media"] for r in v if r["passeio"]["duracao_media"] is not None] for lu, v in vs.items()}
    urg = {lu: [r["passeio"]["urgencia_na_abertura"]["maxima"] for r in v if r["passeio"]["urgencia_na_abertura"]["maxima"] is not None]
           for lu, v in vs.items()}
    return {"por_dia": _niveis(registros, lambda r: r["passeio"]["por_dia"], so),
            "p_passeio": _niveis(registros, P_PASSEIO, so),
            "duracao_media_por_vida": {lu: statistics.fmean(d) if d else None for lu, d in duracoes.items()},
            "fins_somados": _somar(registros, lambda r: r["passeio"]["fins"], so),
            "somados": _somar(registros, lambda r: {"abertos": r["passeio"]["abertos"], "acabados": r["passeio"]["acabados"],
                                                     "decisoes_que_continuam": r["passeio"]["decisoes_que_continuam"],
                                                     "credito_descartado": r["passeio"]["credito_descartado"],
                                                     "aberturas": r["passeio"]["urgencia_na_abertura"]["n"]}, so),
            "urgencia_maxima_na_abertura": {lu: max(u) if u else None for lu, u in urg.items()}}


def corpo(registros: list[dict]) -> dict:
    """8, item 4: a privacao de hoje e as medidas da C5 (AD6-4, como estao), em nivel e nos contrastes, nos dois lugares; e a exaustao"""
    out = {"limiar": lr.LIMIAR_CORPO, "status": "as definicoes da AD6-4, DECIDIDAS, SEM FONTE",
           "privacao_de_hoje": {"niveis": _niveis(registros, lambda r: r["privacao"]), "contrastes": _contrastes(registros, lambda r: r["privacao"])},
           "exaustao": {"niveis": _niveis(registros, lambda r: r["exaustao"]), "contrastes": _contrastes(registros, lambda r: r["exaustao"])}}
    for j in JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f)}
    return out


def outros(registros: list[dict]) -> dict:
    """8, item 5: a fracao das decisoes `explorar` e as acoes por tipo, em nivel e nos contrastes; a G-PESA de cada modulo de hoje; os fins
    das intencoes somados por braco e lugar; por dono, so a media da taxa por episodio e do MOV"""
    acoes = sorted({a for r in registros for a in r["acoes"]})
    por_acao = {}
    for a in acoes:
        f = lambda r, a=a: r["acoes"].get(a, 0)              # noqa: E731
        por_acao[a] = {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f)}
    por_dono = {}
    for d in DONOS:
        for lu in LUGARES:
            for b in BRACOS:
                vs = [r for r in registros if r["dono"] == d and r["lugar"] == lu and r["braco"] == b]
                ep = [EPISODIO(r) for r in vs if EPISODIO(r) is not None]
                if vs:
                    por_dono[f"{d}|{lu}|{b}"] = {"episodio": statistics.fmean(ep) if ep else None, "mov": statistics.fmean(MOV(r) for r in vs)}
    return {"exploracao": {"niveis": _niveis(registros, lambda r: r["exploracao"]),
                           "contrastes": _contrastes(registros, lambda r: r["exploracao"])},
            "acoes_por_tipo": por_acao,
            "g_pesa_por_modulo": {m: _niveis(registros, lambda r, m=m: r["influencia"][m]) for m in MODULOS},
            "fins_somados": _somar(registros, lambda r: r["fins_conferidos"]), "por_dono": por_dono}


NAO_DEMONSTRA = ["o apego do jogador (nao se mede no Python)", "que o pet 'parece passear' ao jogador (SEM FONTE; e do Matheus, jogando)",
                 "que o modular supera o A", "um tamanho de efeito fora das condicoes da run", "qualquer novidade"]


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise das secoes 6 a 9, com a classe de cada contraste e a linha de 7.4"""
    prem, gua, mov = premissas(registros), guarda(registros, boot), movimento(registros, boot)
    return {"premissas": prem, "guarda": gua, "movimento": mov, "leitura": leitura(prem, gua, mov),
            "descritivo": {"longe": longe(registros, boot), "movimento": descritivo_movimento(registros),
                           "passeio": descritivo_passeio(registros), "corpo": corpo(registros), "outros": outros(registros)},
            "margem": MARGEM, "nao_demonstra": NAO_DEMONSTRA}


# ================================================================== a run
def custo(registros: list[dict]) -> dict:
    """o custo medido por vida (CPU e parede de uma vida), por braco: a base da estimativa de parede (secao 10)"""
    out = {}
    for b in BRACOS:
        vs = [r["custo"] for r in registros if r["braco"] == b]
        out[b] = {"vidas": len(vs), "cpu_media_s": statistics.fmean(v["vida_cpu"] for v in vs),
                  "parede_media_s": statistics.fmean(v["vida_parede"] for v in vs)}
    return out


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8, secao 10)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 11)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": {b: orq.SUBCHAVES_AN[b] for b in BRACOS},
            "fins_conhecidos": {b: sorted(fins_conhecidos(b)) for b in BRACOS}, "sha256": sha_dos_arquivos(),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    meta["custo"] = custo(registros)
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


COMANDO = "python experiments/run_v3_acoes_novas.py --config experiments/configs/v3_acoes_novas/acoes_novas.json --processos 4"


def texto_do_registro() -> str:
    """o corpo da secao 14 do plano (o registro da run, secao 11), gerado dos arquivos de hoje: a config, as bases, o K, a primeira e a
    ultima unidade, os bracos, a saida e o comando, e os sha256 que a trava confere (`exigir_registro`). So deriva as sementes; nenhuma
    vida."""
    unidades = bv.unidades_derivadas(BASES, K_POR_BASE, PREFIXO)
    primeira, ultima = unidades[0], unidades[-1]
    shas = sha_dos_arquivos()
    linhas = [f"- **A config:** `experiments/configs/v3_acoes_novas/acoes_novas.json` (o sha256 na lista abaixo).",
              f"- **As bases:** {', '.join(str(b) for b in BASES)}; **K = {K_POR_BASE} por base**, {len(unidades)} unidades, o prefixo "
              f"`{PREFIXO}`; {len(unidades) * len(BRACOS) * len(CELULAS)} vidas de {DIAS} dias, orcamento {ORCAMENTO_POR_DIA} por dia.",
              f"- **A primeira unidade:** base {primeira['base']}, k {primeira['k']}, semente {primeira['semente']}, genoma {primeira['genoma']}.",
              f"- **A ultima unidade:** base {ultima['base']}, k {ultima['k']}, semente {ultima['semente']}, genoma {ultima['genoma']}.",
              "- **Os bracos:** " + "; ".join(f"{b} = `{json.dumps(orq.SUBCHAVES_AN[b], sort_keys=True)}` sobre a `CONFIG_DIGIBRAIN_LIGADA`"
                                              for b in BRACOS) + ".",
              f"- **As celulas:** {', '.join(f'{d}/{lu}' for d, lu in CELULAS)}.",
              f"- **A saida:** `{SAIDA}/`, que nao existe antes da run (a run recusa gravar por cima).",
              f"- **O comando:** `{COMANDO}`.",
              "- **Os sha256** (a trava confere cada um contra a arvore antes da primeira vida; o plano fica fora, porque guarda o registro):",
              ""]
    return "\n".join(linhas + [f"- `{f}`: `{h}`" for f, h in shas.items()]) + "\n"


def _imprimir_resumo(r: dict) -> None:
    """O resumo no console: ASCII puro (ensure_ascii), para nao quebrar num console cp1252 com '≈' na leitura (o #518); os artefatos
    gravados nao passam por aqui."""
    print(json.dumps({k: r[k] for k in ("modo", "vidas", "premissas", "guarda", "movimento", "leitura")}, indent=1,
                     ensure_ascii=True, default=str)[:4000])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--registro", action="store_true", help="imprime o corpo do registro da run (a secao 14 do plano) e sai; nenhuma vida")
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    if a.registro:
        sys.stdout.write(texto_do_registro())
        return
    if a.config is None:
        raise SystemExit("--config e obrigatorio (ou --registro)")
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v3_acoes_novas/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    _imprimir_resumo(r)


if __name__ == "__main__":
    main()
