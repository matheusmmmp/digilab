"""A run unica da DC3, a rede escolhendo falar (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, APROVADO pelo Matheus em 2026-11-07; DC3-1 a DC3-9).
Pergunta: com o `chamar_atencao` dividido em unidades de fala com conteudo (a subchave `fala_unidades`), o pet passa a falar mais do que
precisa quando o dono atende, e menos quando nao atende, sem cuidar pior de si quando ninguem escuta?

O desenho (secao 2): o cenario da AN4 (o da C4: o mundo do MVP, o corpo do v11, o pet sozinho, 14 dias, 16 interacoes por dia, morte
desligada), so o comedouro (DC3-1), os bracos LAB (o REL da C4, o `SUBCHAVES_AN["LAB"]` do prototipo) e LAB+F (o mesmo com a
`fala_unidades`; DC3-2), os 4 donos sem ensino cruzados com o dono que ignora (o de hoje) e o que atende (DC3-3; `DonoQueAtende`), 16 vidas
por unidade, as bases 79101, 79202, 79303, 79404 e 79505, K = 40 por base (200 unidades, 3 200 vidas), o prefixo `digibrain_prototipo`
(DC3-8). A run roda uma vez, sem calibracao nem piloto (o `ganho_conteudo` foi fixado na DC3a, nas sementes dos testes).

Em toda vida (secao 11), falhando alto: o replay bit a bit do disco (o G1), o T-CENARIO-1, o G-MECANISMO do prototipo, a `conferir_memoria`
da C4 (o papel REL nos dois bracos), os fins conhecidos lidos da `estado.py` com a config de cada braco, nenhuma unidade de fala no LAB (e as
tres no LAB+F, sempre), nenhum atendimento sem fala no passo, e a conferencia do credito da 4.4 (a fracao dos atendimentos dentro do intervalo
da opcao de fala que os provocou, com o tick da consequencia lido do motor). As medidas: as do prototipo (`orq.medidas`, `conserto=True`),
as da C5, a fala (`metrics.fala_nas_decisoes`, 4.1 e 4.2), os atendimentos, as linhas de H das unidades de fala nos dias 1, 3, 8 e 14 e a
coincidencia do conteudo com a intencao do decodificador (3.2).

A analise (secao 7), no `resultado.json`: as premissas (P-FALA, P-ATENDE, G-ELEGIVEL-EP), o gate G-ESCUTA (atende - ignora no LAB+F, a fala
pertinente por dia nos dias 8 a 14, nas 4 celulas de dono; "> 0" so com o limite inferior do IC95 pelo t acima de 0, sem margem, DC3-6), a
guarda G-COMEDOURO-DC3 (LAB+F - LAB na taxa por episodio de fome, com o dono que ignora; falha so com a classe "< 0" de A6.6 com
delta = 0,018, DC3-5), a linha de 7.4 e o descritivo da secao 8.

A trava (secao 11): o plano com "APROVADO pelo Matheus" no cabecalho, a faixa 79101...79505 em FAIXAS_RESERVADAS, o registro da run (a
secao 13 do plano, a DC3b) com os sha256 de hoje, so as bases, o K, os dias e o orcamento do plano, no maximo 4 processos, e nenhuma
gravacao por cima de uma pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa e sem o K, com menos dias
se a config pedir; a fumaca nao e dado da DC3.

    python experiments/run_v3_conversa_dc3.py --config experiments/configs/v3_conversa_dc3/conversa_dc3.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO, CONTEUDOS_FALA, TICKS_POR_DIA, ConfigDigibrain,  # noqa: E402
                            ConfigFalaUnidades)
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.digibrain.decodificador import decodificar  # noqa: E402
from digilab.digibrain.estado import EstadoDinamico  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.metrics import fala_nas_decisoes, maior_urgencia_da_fala  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_CONVERSA_DC3.md"
PREFIXO = orq.PREFIXO                                                                 # DC3-8 (o da AN4 e das C1 a C4)
FASE = "conversa_dc3"
BASES = (79101, 79202, 79303, 79404, 79505)                                           # DC3-8
K_POR_BASE = 40                                                                       # secao 6 (DC3-5): 200 unidades
FAIXA = (79101, 79505)
SAIDA = "artifacts_v3_conversa_dc3/run"                                               # secao 5
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # secao 2: 14 dias, 16 por dia
MAX_PROCESSOS = 4                                                                     # secao 6 (V3-D8)
DONOS = orq.DONOS
LUGAR = "comedouro"                                                                   # DC3-1
BRACOS = ("LAB", "LAB+F")                                                             # DC3-2
CONTROLE, TRATADO = BRACOS
MODOS = ("ignora", "atende")                                                          # DC3-3
IGNORA, ATENDE = MODOS
CELULAS = tuple((d, mo) for d in DONOS for mo in MODOS)
CHAVES_CONFIG = lr.CHAVES_CONFIG
MARGEM = 0.018                                                                        # secao 6 (DC3-5), SEM FONTE: o "~ 0" da guarda
P_FALA_LIMIAR = orq.G_PESA["limiar"]                                                  # 7.1 (DC3-7): o 0,01 da P-PASSEIO, SEM FONTE
P_ATENDE_LIMIAR = 1                                                                   # 7.1 (DC3-7): 1 atendimento por dia, SEM FONTE
G_ELEGIVEL_EP = orq.G_ELEGIVEL_EP                                                     # 7.1: a de A6.4, como esta
JANELAS_CORPO = lr.JANELAS_CORPO
MODULOS = ma.MODULOS
PAPEL_DA_MEMORIA = "REL"                                                              # os dois bracos tem a memoria do REL da C4
FALA = "chamar_atencao"
DIAS_DO_HABITO = (1, 3, 8, 14)                                                        # secao 5
DECISOES_POR_DIA = TICKS_POR_DIA // CONFIG_PADRAO.intervalo_decisao_ticks
CUIDADO = {"fome": AcaoUsuario.ALIMENTAR, "higiene": AcaoUsuario.LIMPAR, "solidao": AcaoUsuario.ACARICIAR}   # secao 2 (DC3-3)
REGISTRO_TITULO = "## 13. O registro da run"


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
    """a faixa 79101...79505 esta em FAIXAS_RESERVADAS (DC3-8); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi_) == FAIXA for lo, hi_, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (DC3-8)")


def arquivos_do_registro() -> list[str]:
    """os arquivos cujo sha256 vai ao registro da run (secao 11): este orquestrador, o do prototipo e os que ele usa, a config, o
    `config.py`, o `engine.py`, o `metrics.py`, o `mundo.py`, o `donos.py` e todo `digilab/digibrain/`. O plano fica fora (ele guarda o
    registro); o sha256 dele vai ao `meta.json`."""
    fixos = ["experiments/run_v3_conversa_dc3.py", "experiments/run_v2_digibrain_prototipo.py", "experiments/run_v2_longe_regular.py",
             "experiments/run_v2_memoria_autobio.py",
             "experiments/configs/v3_conversa_dc3/conversa_dc3.json",
             "digilab/config.py", "digilab/engine.py", "digilab/metrics.py", "digilab/mundo.py", "digilab/donos.py"]
    return fixos + [p.relative_to(RAIZ).as_posix() for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))]


def sha_dos_arquivos() -> dict:
    return {f: orq.rc._sha_arquivo(RAIZ / f) for f in arquivos_do_registro()}


def registro_do_plano(plano: str) -> dict:
    """os sha256 da secao 13 do plano (o registro da run): as linhas `- \\`<arquivo>\\`: \\`<sha256>\\``"""
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
    """o registro da run (a secao 13, num commit antes da primeira vida) com os mesmos arquivos e os sha256 de hoje; um arquivo mudado
    depois do registro recusa a run"""
    gravado, hoje = registro_do_plano(plano), sha_dos_arquivos()
    if set(gravado) != set(hoje):
        raise RuntimeError(f"o registro da run lista outros arquivos: faltam {sorted(set(hoje) - set(gravado))}, "
                           f"sobram {sorted(set(gravado) - set(hoje))}")
    mudados = sorted(f for f in hoje if gravado[f] != hoje[f])
    if mudados:
        raise RuntimeError(f"os arquivos mudaram depois do registro da run: {mudados}")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'conversa_dc3', que segue o plano a letra (secao 11): outra base, outro K, outros dias ou outro
    orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o plano sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (DC3-8), o orcamento (secao 2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (DC3-8)")
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


# ================================================================== os bracos e o dono
def config_do_braco(braco: str) -> ConfigDigibrain:
    """a ConfigDigibrain do braco (DC3-2): o LAB e o `SUBCHAVES_AN["LAB"]` do prototipo (o REL da C4, `conserto=True`); o LAB+F, o mesmo
    com a `fala_unidades`"""
    if braco not in BRACOS:
        raise ValueError(f"braco da DC3 {braco!r}: so {BRACOS}")
    lab = orq.config_do_braco("LAB", conserto=True)
    return replace(lab, fala_unidades=True) if braco == TRATADO else lab


def fins_conhecidos(braco: str) -> frozenset:
    """os fins que a `estado.py` pode dar com a config do braco (as chaves de `EstadoDinamico.fins`; a licao do #507)"""
    return frozenset(EstadoDinamico(CONFIG_PADRAO, config_do_braco(braco), CONFIG_DIGIBRAIN_INATOS).fins)


class DonoQueAtende:
    """O dono que atende (secao 2, DC3-3): o dono sintetico de hoje, mais uma regra, sem rng nova. Depois das acoes dele no passo, para cada
    decisao do pet no passo com a acao `chamar_atencao` e com orcamento no passo (as acoes abaixo do `maximo_permitido`, o teto do mesmo
    orcamento de 16 por dia), o cuidado do conteudo (CUIDADO: comida -> `alimentar`, que o `DonoComLugar` deixa no comedouro; limpeza ->
    `limpar`; companhia -> `acariciar`). O conteudo e o da unidade de fala escolhida (o LAB+F) ou, no `chamar_atencao` sem conteudo (o LAB), o
    receptor de maior urgencia do pet na decisao entre fome, higiene e solidao (empate: essa ordem; `metrics.maior_urgencia_da_fala`). Le
    so o registro do cerebro (o motivo da decisao: a escolha e as urgencias). Guarda os atendimentos e as falas sem orcamento."""

    def __init__(self, base, motivos) -> None:
        self.base = base
        self.nome = getattr(base, "nome", None)
        self._motivos = motivos                       # a lista dos motivos do cerebro (so le)
        self._k = 0
        self.atendimentos: list[dict] = []
        self.sem_orcamento: list[dict] = []

    def decidir(self, visao, rng) -> list:
        acoes = list(self.base.decidir(visao, rng))
        ms = self._motivos
        novas, self._k = range(self._k, len(ms)), len(ms)
        for k in novas:
            m = ms[k]
            if m["acao"] != FALA:
                continue
            conteudo = m["escolha"][1] if m["escolha"][1] is not None else maior_urgencia_da_fala(m["afeto"]["urgencias"])
            reg = {"passo": visao.passo, "tick": visao.estado["tick"], "k": k, "conteudo": conteudo, "acao": CUIDADO[conteudo].value}
            if len(acoes) >= visao.maximo_permitido:
                self.sem_orcamento.append(reg)
                continue
            acoes.append(CUIDADO[conteudo])
            self.atendimentos.append(reg)
        return acoes


# ================================================================== a vida
def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, cfg_fala: ConfigFalaUnidades | None = None):
    """(a fabrica do cerebro, a do motor) da vida: as do `orq.fabricas` com a config do braco da DC3 e o motor que grava o corpo (o da AN4,
    `lr.MotorGravaCorpo`). `cfg_fala`: o `ganho_conteudo` (so a calibracao da DC3a passa outro; None, o de hoje)"""
    b = orq.bancada(dias, orcamento_por_dia)
    cc = b.cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))
    cd = config_do_braco(braco)

    def fp(cfg=None):
        return orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, orq.CM, semente=semente, cfg_fala=cfg_fala), CONFIG_DIGIBRAIN_INATOS.escala)

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    return fp, fm


def viver(braco: str, modo: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, cfg_fala: ConfigFalaUnidades | None = None):
    """uma vida: o cerebro do braco, o motor que grava o corpo e o dono do modo (o `ignora` e o `DonoComLugar` de hoje; o `atende`, o mesmo
    com o `DonoQueAtende` por dentro). So le: o tick da consequencia de cada decisao (o do motor quando o `consequencia_corpo` chega, para a
    4.4) e as linhas de H das unidades de fala no fim de cada dia (antes da primeira decisao do dia seguinte; o ultimo, no fim da vida). O
    G1 rejoga a vida com as fabricas, sem nada disso. Devolve (o motor, o registro, as fabricas, o dono que atende ou None, as leituras)."""
    if modo not in MODOS:
        raise ValueError(f"modo do dono {modo!r}: so {MODOS}")
    fp, fm0 = fabricas(braco, dono, semente, dias, orcamento_por_dia, cfg_fala)
    caixa: list = []

    def fm(politica, cfg, s):
        motor = fm0(politica, cfg, s)
        caixa.append(motor)
        return motor

    registro = fp(CONFIG_PADRAO)
    c = orq.cerebro_de(registro)
    leituras = {"tick_consequencia": [], "habito": {}}
    agir, consequencia = registro.agir, registro.consequencia_corpo

    def _h() -> dict:
        H = c.m.plast.H
        return {b: list(v) for b, v in H.items() if b.startswith(FALA)}

    def agir_e_ler(obs, rng):
        k = c.k
        if k and k % DECISOES_POR_DIA == 0:
            leituras["habito"][k // DECISOES_POR_DIA] = _h()
        return agir(obs, rng)

    def consequencia_e_ler(acao, ocorrido, obs_depois):
        leituras["tick_consequencia"].append(caixa[0]._estado.tick)      # so le o relogio do motor
        return consequencia(acao, ocorrido, obs_depois)

    registro.agir, registro.consequencia_corpo = agir_e_ler, consequencia_e_ler
    base = criar_dono(dono)
    atende = DonoQueAtende(base, c.motivos) if modo == ATENDE else None
    d = DonoComLugar(atende if atende is not None else base, LUGAR, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    del registro.agir, registro.consequencia_corpo     # o registro volta a ser o da fabrica
    leituras["habito"][dias] = _h()
    if len(caixa) != 1 or caixa[0] is not motor:
        raise RuntimeError("a vida montou outro motor")
    return motor, registro, (fp, fm0), atende, leituras


# ------------------------------------------------------------------ as conferencias (secao 11)
def conferir_bracos(braco: str, c) -> None:
    """a config do cerebro e a do braco; a `fala_unidades` ligada exatamente no LAB+F; fora dela, nenhuma subchave difere do REL da C4"""
    cd = c.cd
    if cd != config_do_braco(braco):
        raise RuntimeError(f"{braco}: a config do cerebro nao e a do braco")
    if cd.fala_unidades != (braco == TRATADO):
        raise RuntimeError(f"{braco}: a fala_unidades {'desligada' if braco == TRATADO else 'ligada'}")
    rel = orq.config_do_braco("REL", conserto=True)
    if {k: v for k, v in vars(cd).items() if k != "fala_unidades"} != {k: v for k, v in vars(rel).items() if k != "fala_unidades"}:
        raise RuntimeError(f"{braco}: uma subchave fora da fala_unidades difere do REL da C4 (secao 9)")


def conferir_fala(braco: str, c) -> None:
    """secao 11: no LAB, nenhuma unidade de fala (o chamar sem conteudo, em toda decisao, e nenhuma linha de H de fala); no LAB+F, as tres
    unidades de fala em toda decisao, o chamar sem conteudo nunca, e as tres linhas de H no lugar da do chamar"""
    quer = [None] if braco == CONTROLE else list(CONTEUDOS_FALA)
    for m in c.motivos:
        tem = [u["chave"][1] for u in m["unidades"] if u["chave"][0] == FALA]
        if tem != quer:
            raise RuntimeError(f"{braco}: as unidades do chamar na decisao {m['k']} sao {tem}, nao {quer}")
        if m["acao"] == FALA and m["escolha"][1] not in quer:
            raise RuntimeError(f"{braco}: a fala da decisao {m['k']} com o conteudo {m['escolha'][1]!r}")
    linhas = [b for b in c.m.plast.H if b.startswith(FALA)]
    if linhas != ([FALA] if braco == CONTROLE else [f"{FALA}/{x}" for x in CONTEUDOS_FALA]):
        raise RuntimeError(f"{braco}: as linhas de H do chamar sao {linhas}")


def conferir_atendimentos(braco: str, modo: str, c, atende: DonoQueAtende | None, tick_consequencia: list) -> dict | None:
    """secao 11 e 4.4. Com o dono que ignora, nenhum dono que atende. Com o que atende: todo atendimento (e toda fala sem orcamento) vem de
    uma decisao de fala do mesmo passo (o tick da decisao k e k x 15, dentro do passo; o atendimento e depois dela), com o conteudo da
    escolha (LAB+F) ou o de maior urgencia (LAB), e cada decisao de fala tem um atendimento ou uma falta de orcamento, uma vez so. A
    conferencia do credito (4.4): o atendimento cai dentro do intervalo da opcao de fala que o provocou se o tick dele nao passa do tick em
    que a consequencia da opcao (uma opcao de uma decisao: a da propria decisao) chegou ao cerebro. Devolve as contagens (None no ignora)."""
    if modo == IGNORA:
        if atende is not None:
            raise RuntimeError("o dono que ignora com a regra de atender")
        return None
    passo_t = CONFIG_PADRAO.intervalo_decisao_ticks
    ms = c.motivos
    if len(tick_consequencia) != len(ms) or any(t != k * passo_t for k, t in enumerate(tick_consequencia)):
        raise RuntimeError(f"{braco}: a consequencia de uma decisao chegou fora do tick da decisao")
    vistos = set()
    for a in atende.atendimentos + atende.sem_orcamento:
        k, m = a["k"], ms[a["k"]]
        t_dec = k * passo_t
        if m["acao"] != FALA or not (a["passo"] * passo_t <= t_dec < (a["passo"] + 1) * passo_t) or a["tick"] <= t_dec:
            raise RuntimeError(f"{braco}: o atendimento {a} sem a fala no passo (decisao {k}, acao {m['acao']})")
        quer = m["escolha"][1] if braco == TRATADO else maior_urgencia_da_fala(m["afeto"]["urgencias"])
        if a["conteudo"] != quer or a["acao"] != CUIDADO[quer].value:
            raise RuntimeError(f"{braco}: o atendimento {a} nao e o cuidado do conteudo {quer!r}")
        if k in vistos:
            raise RuntimeError(f"{braco}: a fala da decisao {k} atendida duas vezes")
        vistos.add(k)
    falas = {m["k"] for m in ms if m["acao"] == FALA}     # a decisao k cai no passo k, e o dono age depois de todo passo
    if vistos != falas:
        raise RuntimeError(f"{braco}: {len(falas - vistos)} falas sem atendimento nem falta de orcamento")
    dentro = sum(1 for a in atende.atendimentos if a["tick"] <= tick_consequencia[a["k"]])
    n = len(atende.atendimentos)
    return {"atendimentos": n, "sem_orcamento": len(atende.sem_orcamento), "dentro_do_intervalo": dentro, "fora_do_intervalo": n - dentro,
            "fracao_dentro": dentro / n if n else None}


def conferir_fins(braco: str, c) -> dict:
    """os fins das intencoes da vida, por motivo (a do `hi.conferir_fins`, com os fins conhecidos da config do braco da DC3: o LAB+F nao e
    braco do prototipo). Falha alto com um fim desconhecido, com a contagem do registro diferente da do estado, ou com uma retomada ou um
    `n_susp` (a `intencao_suspensa` fica desligada nos dois bracos)."""
    if c.cd.intencao_suspensa:
        raise RuntimeError(f"{braco}: a intencao_suspensa esta ligada")
    conhecidos = fins_conhecidos(braco)
    contagem = {m: 0 for m in sorted(conhecidos)}
    for k, m in enumerate(c.motivos):
        if m.get("retomou"):
            raise RuntimeError(f"{braco}, decisao {k}: uma retomada com a intencao_suspensa desligada")
        for f in m["fins"]:
            if "n_susp" in f:
                raise RuntimeError(f"{braco}, decisao {k}: uma intencao com n_susp com a intencao_suspensa desligada")
            if f["motivo"] not in conhecidos:
                raise RuntimeError(f"{braco}, decisao {k}: o fim {f['motivo']!r} nao e dos conhecidos {sorted(conhecidos)}")
            contagem[f["motivo"]] += 1
    if contagem != dict(sorted(c.m.estado.fins.items())):
        raise RuntimeError(f"{braco}: os fins do registro {contagem} nao sao os do estado {dict(sorted(c.m.estado.fins.items()))}")
    return contagem


# ------------------------------------------------------------------ as medidas
def medidas_fala(c, dias: int) -> dict:
    """4.1 e 4.2, pela funcao do `metrics.py`: (o tick k x 15, a acao, o conteudo da fala, as urgencias) de cada decisao"""
    passo_t = CONFIG_PADRAO.intervalo_decisao_ticks
    dec = [(m["k"] * passo_t, m["acao"], m["escolha"][1] if m["acao"] == FALA else None, m["afeto"]["urgencias"]) for m in c.motivos]
    return fala_nas_decisoes(dec, dias, c.inatos.urgencia_lambda)


def medidas_atendimento(atende: DonoQueAtende | None, dias: int) -> dict | None:
    """os atendimentos por dia (o dia da decisao de fala que o provocou), por conteudo, e a media por dia nos dias 1 a 3 (a P-ATENDE)"""
    if atende is None:
        return None
    passo_t = CONFIG_PADRAO.intervalo_decisao_ticks
    por_dia = [0] * dias
    for a in atende.atendimentos:
        por_dia[a["k"] * passo_t // TICKS_POR_DIA] += 1
    n3 = min(3, dias)
    return {"por_dia": por_dia, "dias_1_3_por_dia": sum(por_dia[:n3]) / n3,
            "por_conteudo": {x: sum(1 for a in atende.atendimentos if a["conteudo"] == x) for x in CONTEUDOS_FALA},
            "sem_orcamento": len(atende.sem_orcamento)}


def coincidencia_dec(c) -> dict:
    """3.2 e 8, item 4 (so descritivo): nas falas com conteudo, quantas tem o conteudo igual a intencao do decodificador (a I-a, a mesma no
    dec-v1 e no dec-v2) na mesma decisao. A higiene nao e conceito do catalogo: nunca coincide (o relato le por conteudo)."""
    out = {x: {"falas": 0, "coincide": 0} for x in CONTEUDOS_FALA}
    for m in c.motivos:
        x = m["escolha"][1] if m["acao"] == FALA else None
        if x is None:
            continue
        out[x]["falas"] += 1
        out[x]["coincide"] += decodificar(m)["intencao"] == x
    return out


def _vida(cfg: dict, braco: str, modo: str, dono: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as falhas altas da secao 11) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, atende, leituras = viver(braco, modo, dono, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{modo}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    c = orq.cerebro_de(registro)
    conferir_bracos(braco, c)
    conferir_fala(braco, c)
    credito = conferir_atendimentos(braco, modo, c, atende, leituras["tick_consequencia"])
    orq.conferir_mecanismo(braco, registro, None)
    ma.conferir_memoria(PAPEL_DA_MEMORIA, c)
    fins = conferir_fins(braco, c)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{modo}|{dono}|{unidade['semente']}", "braco": braco, "modo": modo, "dono": dono, "lugar": LUGAR,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "fala": medidas_fala(c, cfg["dias"]), "atendimento": medidas_atendimento(atende, cfg["dias"]), "credito": credito,
            "habito": {str(d): leituras["habito"][d] for d in DIAS_DO_HABITO if d in leituras["habito"]},
            "coincidencia_dec": coincidencia_dec(c),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, modo, dono, unidade, pasta) for b in BRACOS for dono, modo in CELULAS]


# ================================================================== a analise
def por_unidade(registros: list[dict], a: tuple, b: tuple | None, medida) -> dict:
    """{(base, semente): a media, nas 4 celulas de dono, de medida(a) - medida(b)} com a e b = (braco, modo) (b None: o nivel de a). As
    celulas com None num dos lados ficam fora (a regra da AN4, 4.3); a unidade sem celula com valor fica fora."""
    idx = {(r["semente"], r["dono"], r["braco"], r["modo"]): r for r in registros}
    out = {}
    for s, base in sorted({(r["semente"], r["base"]) for r in registros}):
        ds = []
        for dono in DONOS:
            ra = idx.get((s, dono) + tuple(a))
            if ra is None:
                raise RuntimeError(f"unidade {s}, dono {dono}: falta o {a}")
            va = medida(ra)
            if b is None:
                if va is not None:
                    ds.append(va)
                continue
            rb = idx.get((s, dono) + tuple(b))
            if rb is None:
                raise RuntimeError(f"unidade {s}, dono {dono}: falta o {b}")
            vb = medida(rb)
            if va is not None and vb is not None:
                ds.append(va - vb)
        if ds:
            out[(base, s)] = sum(ds) / len(ds)
    return out


def classe(ic: dict, margem: float = MARGEM) -> dict:
    """a classe de A6.6, na ordem, com a margem da guarda (secao 6)"""
    return lr.classe(ic, margem)


def classe_sem_margem(ic: dict) -> dict:
    """DC3-6: "> 0" com o limite inferior do IC95 acima de 0, "< 0" com o superior abaixo, senao "indeterminado" (nao ha "~ 0")"""
    lo, hi_ = ic["ic_inferior"], ic["ic_superior"]
    if lo is None:
        return {"classe": "indeterminado", "motivo": ic["motivo"]}
    return {"classe": "> 0" if lo > 0 else ("< 0" if hi_ < 0 else "indeterminado"), "motivo": None}


def estimativa(difs: dict, margem: float = MARGEM) -> dict:
    """o descritivo de um valor por unidade: a media, o dp e o IC95 pelo t sobre as unidades, com a classe de A6.6"""
    return ma.estimativa(difs, margem)


EPISODIO = lr.EPISODIO
PERTINENTE_8_14 = lambda r: None if r["fala"]["dias_8_14"] is None else r["fala"]["dias_8_14"]["pertinente_por_dia"]   # noqa: E731
FRAC_FALA = lambda r: r["fala"]["vida"]["frac_fala_fora_do_dormir"]                                                     # noqa: E731
ATENDE_1_3 = lambda r: r["atendimento"]["dias_1_3_por_dia"]                                                              # noqa: E731


def _ic(c: dict) -> dict:
    return {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}


def escuta(registros: list[dict], boot: dict) -> dict:
    """7.2: o G-ESCUTA, atende - ignora no LAB+F, a fala pertinente por dia nos dias 8 a 14, nas 4 celulas de dono; passa so com a classe
    "> 0" pelo IC95 do t sem margem (DC3-6). Ao lado, o efeito detectavel com poder 0,8 pelo dp observado (secao 6), em fala por dia."""
    difs = por_unidade(registros, (TRATADO, ATENDE), (TRATADO, IGNORA), PERTINENTE_8_14)
    c = orq.contraste_t(difs, boot)
    cl = classe_sem_margem(_ic(c))
    dp = estimativa(difs)["dp"]
    return {"contraste": "G-ESCUTA: atende - ignora, no LAB+F, a fala pertinente por dia nos dias 8 a 14, nas 4 celulas de dono", **c,
            "classe": cl, "passa": cl["classe"] == "> 0", "dp": dp, "efeito_detectavel": lr.margem_efetiva(dp, c["n"])}


def guarda(registros: list[dict], boot: dict) -> dict:
    """7.3: a G-COMEDOURO-DC3, LAB+F - LAB na taxa por episodio, com o dono que ignora, nas 4 celulas; falha so com a classe "< 0" de A6.6
    com delta = 0,018"""
    difs = por_unidade(registros, (TRATADO, IGNORA), (CONTROLE, IGNORA), EPISODIO)
    c = orq.contraste_t(difs, boot)
    cl = classe(_ic(c))
    return {"contraste": "G-COMEDOURO-DC3: LAB+F - LAB, a taxa por episodio, com o dono que ignora, nas 4 celulas", **c, "classe": cl,
            "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(estimativa(difs)["dp"], c["n"]), "falha": cl["classe"] == "< 0"}


def premissas(registros: list[dict]) -> dict:
    """7.1 (DC3-7): a P-FALA (no LAB+F com o dono que ignora, a fracao das decisoes fora do dormir que sao fala, por unidade; o limite
    inferior do IC95 pelo t > 0,01), a P-ATENDE (no LAB+F com o dono que atende, os atendimentos por dia nos dias 1 a 3, por unidade; o
    limite inferior > 1) e a G-ELEGIVEL-EP (no LAB e no LAB+F com o dono que ignora, ao menos 80 % das vidas com 3 episodios de fome ou
    mais). Se uma falha, o gate e a guarda sao inconclusivos por premissa."""
    def lim(est: dict, limiar: float) -> dict:
        lo = est["ic95"]["ic_inferior"]
        return {**est, "limiar": limiar, "passa": lo is not None and lo > limiar}

    pf = lim(estimativa(por_unidade(registros, (TRATADO, IGNORA), None, FRAC_FALA)), P_FALA_LIMIAR)
    pa = lim(estimativa(por_unidade(registros, (TRATADO, ATENDE), None, ATENDE_1_3)), P_ATENDE_LIMIAR)
    elegivel = {}
    for b in BRACOS:
        vs = [r for r in registros if r["braco"] == b and r["modo"] == IGNORA]
        frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= G_ELEGIVEL_EP["episodios"]) / len(vs)
        elegivel[b] = {"frac_vidas": frac, "vidas": len(vs), "limiar": G_ELEGIVEL_EP["frac_vidas"], "passa": frac >= G_ELEGIVEL_EP["frac_vidas"]}
    eleg = {"por_braco": elegivel, "passa": all(v["passa"] for v in elegivel.values())}
    return {"P-FALA": pf, "P-ATENDE": pa, "G-ELEGIVEL-EP": eleg, "conclusivo": pf["passa"] and pa["passa"] and eleg["passa"]}


def leitura(prem: dict, esc: dict, gua: dict) -> dict:
    """7.4, na ordem (a primeira linha que serve)"""
    base = {"G-ESCUTA": esc["classe"]["classe"], "G-COMEDOURO-DC3": gua["classe"]["classe"], "sinal_da_guarda": gua["classe"]["sinal"],
            "ressalva_da_guarda": gua["ressalva_assimetria"]}
    if not prem["conclusivo"]:
        return {**base, "linha": 1, "o_que_diria": "inconclusiva por premissa", "dc3d_pode_rodar": False, "o_que_se_faz": "volta ao Matheus"}
    if esc["passa"] and not gua["falha"]:
        return {**base, "linha": 2, "o_que_diria": "a rede aprende a falar pela consequencia sem cuidar pior de si", "dc3d_pode_rodar": True,
                "o_que_se_faz": "a DC3d (o porte ao jogo, atras de chave)"}
    if esc["passa"]:
        return {**base, "linha": 3, "o_que_diria": "aprende, mas falar tira o pet da comida quando ninguem escuta", "dc3d_pode_rodar": False,
                "o_que_se_faz": "a subchave fica desligada; volta ao Matheus"}
    return {**base, "linha": 4, "o_que_diria": "o P2 de hoje nao liga a fala a resposta do dono", "dc3d_pode_rodar": False,
            "o_que_se_faz": "a subchave fica desligada; a leitura do credito (4.4) diz por que"}


# ------------------------------------------------------------------ o descritivo (secao 8; sem gate)
CHAVES = tuple((b, mo) for b in BRACOS for mo in MODOS)


def _niveis(registros: list[dict], medida, chaves: tuple = CHAVES) -> dict:
    return {f"{b}|{mo}": estimativa(por_unidade(registros, (b, mo), None, medida)) for b, mo in chaves}


def _media(vs: list):
    vs = [v for v in vs if v is not None]
    return statistics.fmean(vs) if vs else None


def descritivo_fala(registros: list[dict]) -> dict:
    """8, itens 1 e 3: a fala por dia ao longo da vida (a media das vidas, por braco, modo e dono), a EXT (dias 8 a 14 - dias 1 a 3 da
    fala por dia, no LAB+F com o dono que ignora; a previsao "< 0", sem gate), a pertinencia e a fala pertinente por janela, as falas por
    conteudo e o conteudo das falas com a maior urgencia no limiar ou abaixo (somados)"""
    out: dict = {"por_dia": {}, "por_dono": {}}
    for b, mo in CHAVES:
        vs = [r for r in registros if r["braco"] == b and r["modo"] == mo]
        dias = len(vs[0]["fala"]["falas_por_dia"]) if vs else 0
        out["por_dia"][f"{b}|{mo}"] = [_media([r["fala"]["falas_por_dia"][d] for r in vs]) for d in range(dias)]
        for dono in DONOS:
            ws = [r for r in vs if r["dono"] == dono]
            out["por_dono"][f"{b}|{mo}|{dono}"] = [_media([r["fala"]["falas_por_dia"][d] for r in ws]) for d in range(dias)]

    def janela(j: str, campo: str):
        return lambda r: None if r["fala"][j] is None else r["fala"][j][campo]

    def ext(r):
        a, b_ = r["fala"]["dias_8_14"], r["fala"]["dias_1_3"]
        return None if a is None or b_ is None else a["falas_por_dia"] - b_["falas_por_dia"]

    e = estimativa(por_unidade(registros, (TRATADO, IGNORA), None, ext))
    out["EXT"] = {**e, "classe": classe_sem_margem({**e["ic95"], "motivo": e["motivo"]}), "previsao": "< 0", "gate": None}
    for j in ("vida", "dias_1_3", "dias_8_14"):
        for campo in ("falas_por_dia", "pertinencia", "pertinente_por_dia"):
            out[f"{j}|{campo}"] = _niveis(registros, janela(j, campo))
    for campo in ("por_conteudo", "abaixo_do_limiar"):
        soma: dict = {}
        for b, mo in CHAVES:
            s: dict = {}
            for r in registros:
                if r["braco"] == b and r["modo"] == mo:
                    for k, v in r["fala"][campo].items():
                        s[k] = s.get(k, 0) + v
            soma[f"{b}|{mo}"] = dict(sorted(s.items()))
        out[campo] = soma
    return out


def descritivo_habito(registros: list[dict]) -> dict:
    """8, item 2: as linhas de H das unidades de fala (no LAB, a do chamar) nos dias 1, 3, 8 e 14, a media das vidas, por braco e modo, e a
    soma dos |H| da linha"""
    out = {}
    for b, mo in CHAVES:
        vs = [r for r in registros if r["braco"] == b and r["modo"] == mo]
        por = {}
        for d in sorted({d for r in vs for d in r["habito"]}, key=int):
            linhas = sorted({ln for r in vs for ln in r["habito"].get(d, {})})
            por[d] = {ln: {"media": [_media([r["habito"][d][ln][j] for r in vs if d in r["habito"]])
                                     for j in range(len(vs[0]["habito"][d][ln]))],
                           "soma_abs_media": _media([sum(abs(x) for x in r["habito"][d][ln]) for r in vs if d in r["habito"]])}
                      for ln in linhas}
        out[f"{b}|{mo}"] = por
    return out


def descritivo_credito(registros: list[dict]) -> dict:
    """a conferencia do credito (4.4), somada por braco: os atendimentos, os dentro e os fora do intervalo da opcao de fala, as falas sem
    orcamento, e a fracao das vidas com algum atendimento dentro"""
    out = {}
    for b in BRACOS:
        vs = [r["credito"] for r in registros if r["braco"] == b and r["modo"] == ATENDE]
        n = sum(v["atendimentos"] for v in vs)
        dentro = sum(v["dentro_do_intervalo"] for v in vs)
        out[b] = {"vidas": len(vs), "atendimentos": n, "dentro_do_intervalo": dentro, "fora_do_intervalo": n - dentro,
                  "fracao_dentro": dentro / n if n else None, "sem_orcamento": sum(v["sem_orcamento"] for v in vs),
                  "vidas_com_algum_dentro": sum(1 for v in vs if v["dentro_do_intervalo"] > 0)}
    return out


def descritivo_coincidencia(registros: list[dict]) -> dict:
    """8, item 4: a coincidencia do conteudo da fala com a intencao do decodificador, somada no LAB+F por modo e conteudo"""
    out = {}
    for mo in MODOS:
        s = {x: {"falas": 0, "coincide": 0} for x in CONTEUDOS_FALA}
        for r in registros:
            if r["braco"] == TRATADO and r["modo"] == mo:
                for x, v in r["coincidencia_dec"].items():
                    s[x]["falas"] += v["falas"]
                    s[x]["coincide"] += v["coincide"]
        out[mo] = {x: {**v, "fracao": v["coincide"] / v["falas"] if v["falas"] else None} for x, v in s.items()}
    return out


def corpo(registros: list[dict]) -> dict:
    """8, item 5: a privacao de hoje e as medidas da C5 (AD6-4), em nivel e no contraste LAB+F - LAB por modo, so "pior ou nao" (a
    classe so como descricao)"""
    def contrastes(f) -> dict:
        return {f"{mo}|LAB+F - LAB": estimativa(por_unidade(registros, (TRATADO, mo), (CONTROLE, mo), f)) for mo in MODOS}

    out = {"limiar": lr.LIMIAR_CORPO, "status": "as definicoes da AD6-4, DECIDIDAS, SEM FONTE",
           "privacao_de_hoje": {"niveis": _niveis(registros, lambda r: r["privacao"]), "contrastes": contrastes(lambda r: r["privacao"])},
           "exaustao": {"niveis": _niveis(registros, lambda r: r["exaustao"]), "contrastes": contrastes(lambda r: r["exaustao"])},
           "episodio": {"niveis": _niveis(registros, EPISODIO), "contrastes": contrastes(EPISODIO)}}
    for j in JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f), "contrastes": contrastes(f)}
    return out


NAO_DEMONSTRA = ["que o pet 'quer se comunicar' ou entende linguagem", "que a fala parece viva ao jogador (SEM FONTE; e do Matheus, jogando)",
                 "que o modular supera o A", "um tamanho de efeito fora das condicoes da run", "qualquer novidade"]


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise da secao 7, com a linha de 7.4 e o descritivo da secao 8"""
    prem, esc, gua = premissas(registros), escuta(registros, boot), guarda(registros, boot)
    return {"premissas": prem, "escuta": esc, "guarda": gua, "leitura": leitura(prem, esc, gua),
            "descritivo": {"fala": descritivo_fala(registros), "habito": descritivo_habito(registros),
                           "credito": descritivo_credito(registros), "coincidencia_dec": descritivo_coincidencia(registros),
                           "corpo": corpo(registros)},
            "margem": MARGEM, "nao_demonstra": NAO_DEMONSTRA}


# ================================================================== a run
def custo(registros: list[dict]) -> dict:
    """o custo medido por vida (CPU e parede de uma vida), por braco: a base da estimativa de parede (secao 6)"""
    out = {}
    for b in BRACOS:
        vs = [r["custo"] for r in registros if r["braco"] == b]
        out[b] = {"vidas": len(vs), "cpu_media_s": statistics.fmean(v["vida_cpu"] for v in vs),
                  "parede_media_s": statistics.fmean(v["vida_parede"] for v in vs)}
    return out


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8, secao 6)")
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
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "lugar": LUGAR,
            "bracos": {b: {**orq.SUBCHAVES_AN["LAB"], **({"fala_unidades": True} if b == TRATADO else {})} for b in BRACOS},
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


COMANDO = "python experiments/run_v3_conversa_dc3.py --config experiments/configs/v3_conversa_dc3/conversa_dc3.json --processos 4"


def texto_do_registro() -> str:
    """o corpo da secao 13 do plano (o registro da run, secao 11), gerado dos arquivos de hoje: a config, as bases, o K, a primeira e a
    ultima unidade, os bracos, as celulas, a saida, o comando e os sha256 que a trava confere. So deriva as sementes; nenhuma vida."""
    unidades = bv.unidades_derivadas(BASES, K_POR_BASE, PREFIXO)
    primeira, ultima = unidades[0], unidades[-1]
    shas = sha_dos_arquivos()
    linhas = ["- **A config:** `experiments/configs/v3_conversa_dc3/conversa_dc3.json` (o sha256 na lista abaixo).",
              f"- **As bases:** {', '.join(str(b) for b in BASES)}; **K = {K_POR_BASE} por base**, {len(unidades)} unidades, o prefixo "
              f"`{PREFIXO}`; {len(unidades) * len(BRACOS) * len(CELULAS)} vidas de {DIAS} dias, orcamento {ORCAMENTO_POR_DIA} por dia, "
              f"so o {LUGAR}.",
              f"- **A primeira unidade:** base {primeira['base']}, k {primeira['k']}, semente {primeira['semente']}, genoma {primeira['genoma']}.",
              f"- **A ultima unidade:** base {ultima['base']}, k {ultima['k']}, semente {ultima['semente']}, genoma {ultima['genoma']}.",
              f"- **Os bracos:** LAB = `{json.dumps(orq.SUBCHAVES_AN['LAB'], sort_keys=True)}` sobre a config ligada do DigiBrain; LAB+F = o "
              f"mesmo com `fala_unidades: true`.",
              f"- **As celulas:** {', '.join(f'{d}/{mo}' for d, mo in CELULAS)}.",
              f"- **A saida:** `{SAIDA}/`, que nao existe antes da run (a run recusa gravar por cima).",
              f"- **O comando:** `{COMANDO}`.",
              "- **Os sha256** (a trava confere cada um contra a arvore antes da primeira vida; o plano fica fora, porque guarda o registro):",
              ""]
    return "\n".join(linhas + [f"- `{f}`: `{h}`" for f, h in shas.items()]) + "\n"


def _imprimir_resumo(r: dict) -> None:
    """O resumo no console: ASCII puro (ensure_ascii), para nao quebrar num console cp1252 com '≈' na leitura (o #518)"""
    print(json.dumps({k: r[k] for k in ("modo", "vidas", "premissas", "escuta", "guarda", "leitura")}, indent=1,
                     ensure_ascii=True, default=str)[:4000])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config")
    ap.add_argument("--registro", action="store_true", help="imprime o corpo do registro da run (a secao 13 do plano) e sai; nenhuma vida")
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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v3_conversa_dc3/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    _imprimir_resumo(r)


if __name__ == "__main__":
    main()
