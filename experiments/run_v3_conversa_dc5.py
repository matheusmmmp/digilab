"""O orquestrador da DC5, a voz nova (voz-v4) contra a voz do jogo (CONVERSA_PET; docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, APROVADO pelo Matheus
em 2026-11-10, D-DC5-1 a D-DC5-11). Codigo da DC5a: **nenhuma chamada a modelo de verdade roda na DC5a**; a calibracao (DC5b) e a validacao
(DC5c) usam este arquivo.

O caminho de cada fala e o do jogo, como na DC4 (`run_v3_conversa_dc4`, que nao muda e de onde vem o cliente registrado, os clientes falsos
e a fala pelo servico): as entradas (`entradas_dc5`) vao ao `ServicoFalaLivre` como a pagina as manda, e o servico gera a voz e confere pelo
verificador (`verif-v8` no dec-v2, `verif-v9` no dec-v3, contra todos os conceitos ativos, nas duas vozes). As **celulas** (secao 2) sao um
braco com uma voz:

| braco | modelo | | voz | o que a voz recebe |
|---|---|---|---|---|
| G | `gemma2:9b`, Ollama local, com a semente do turno | | `jogo` | a voz-v2 no dec-v2 e a voz-v3 no dec-v3, como o jogo (`voz_dos_conceitos` None) |
| H | `claude-haiku-5-5`, esforco low, sem semente | | `v4` | a voz-v4 (`prompt.VERSAO_VOZ_V4`), com a selecao e, no ES, as falas ja ditas |

As situacoes (secao 5), na ordem, em cada celula: as espontaneas do E3 e do E2; as sequencias espontaneas do ES (na voz-v4, as ate
`CONFIG_VOZ_V4.n_ditas` falas anteriores da sequencia vao a voz pelo `ditas_da_voz` do servico); e as conversas (roteiro x sequencia, o
historico do estagio atual, as ultimas 10 trocas, como a pagina). O pareamento e das entradas e dos roteiros, com a mesma semente do turno
no G; as saidas divergem.

As conferencias (secao 9), falhando alto: o modelo devolvido e o pedido; toda fala tem a entrada, o braco, a voz, a semente e o `usage`; a
voz de cada fala e a da celula; as quatro celulas viram as mesmas entradas e sementes; a voz do jogo e a do gabarito gravado antes da DC5
(`experiments/configs/v3_conversa_dc5/gabarito_voz_jogo.json`); a ordem dos pares e a sorteada; o gasto nao passa do teto, e a estimativa
nao passa do limite da config (a DC5b: US$ 0,50, pedido da Gerente da CONVERSA_PET). Uma queda recomeca do inicio, numa pasta nova (8).

    python experiments/run_v3_conversa_dc5.py --config experiments/configs/v3_conversa_dc5/fumaca.json --falso     # fumaca, sem modelo
    python experiments/run_v3_conversa_dc5.py --config experiments/configs/v3_conversa_dc5/calibracao.json         # DC5b
    python experiments/run_v3_conversa_dc5.py --config experiments/configs/v3_conversa_dc5/validacao.json          # DC5c, uma vez
    python experiments/run_v3_conversa_dc5.py --registro                                                           # o texto do registro
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import entradas_dc5 as en  # noqa: E402
import exportar_gabarito_voz_jogo_dc5 as gvj  # noqa: E402
import marcacao_dc5 as mc  # noqa: E402
import pre_run  # noqa: E402
import run_v3_conversa_dc4 as dc4  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402

from digilab.config import CONFIG_VOZ_V4  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab_fala_livre import prompt as pr  # noqa: E402
from digilab_fala_livre.conceitos import VERSAO_DEC_V3  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from servidor.fala_livre import ServicoFalaLivre  # noqa: E402
from servidor.fala_livre_claude import ARQUIVO_GASTO_LIVRE, ClienteClaude  # noqa: E402
from servidor.fala_llm import LIMITE_USD_LIVRE_PADRAO, ControleGasto, custo_usd  # noqa: E402

ORQUESTRADOR = "experiments/run_v3_conversa_dc5.py"
PLANO = "docs/PLANO_ANALISE_V3_CONVERSA_DC5.md"
RUBRICA = "docs/RUBRICA_DC5_FIDELIDADE.md"
PREFIXO = en.PREFIXO
FASES = ("fumaca", "calibracao", "validacao")
BRACOS = {"G": dc4.BRACOS["G"], "H": dc4.BRACOS["H"]}                            # D-DC5-2: o S sai
VOZES = ("jogo", "v4")                                                            # secao 2
CELULAS = tuple((b, v) for b in BRACOS for v in VOZES)
MODELO_VERIF = dc4.MODELO_VERIF
FAIXAS = {"calibracao": (20262900, 20263199), "validacao": (20263200, 20263499)}  # secao 7, D-DC5-1
SEMENTES_DOS_TESTES = dc4.SEMENTES_DOS_TESTES
DIR_CONFIGS = "experiments/configs/v3_conversa_dc5"
ROTEIROS = {"calibracao": f"{DIR_CONFIGS}/roteiros_calibracao.json", "validacao": f"{DIR_CONFIGS}/roteiros_validacao.json"}
CONFIGS = {"calibracao": f"{DIR_CONFIGS}/calibracao.json", "validacao": f"{DIR_CONFIGS}/validacao.json"}
FRASES_MODELO = f"{DIR_CONFIGS}/frases_modelo.json"
GABARITO_VOZ_JOGO = f"{DIR_CONFIGS}/gabarito_voz_jogo.json"
# o tamanho da fase (secao 5): a calibracao e a metade da validacao
TAMANHO = {"calibracao": {"n_e3_por_pedido": 10, "n_e2": 15, "min_ep_e2": 5, "n_sequencias": 3, "roteiros": 2,
                          "n_es": CONFIG_VOZ_V4.n_sequencias_es // 2},
           "validacao": {"n_e3_por_pedido": 20, "n_e2": 30, "min_ep_e2": 10, "n_sequencias": 3, "roteiros": 4,
                         "n_es": CONFIG_VOZ_V4.n_sequencias_es}}
DIAS, ORCAMENTO_POR_DIA = dc4.DIAS, dc4.ORCAMENTO_POR_DIA                         # secao 5: o cenario da DC3
TETO_USD = LIMITE_USD_LIVRE_PADRAO                                                # D-DC5-9: o teto de US$ 3 da fala livre
PAPEIS = dc4.PAPEIS
REGISTRO_TITULO = "## 14. O registro da rodada"
SEMENTE_MAX = dc4.SEMENTE_MAX
# o gasto que ja aconteceu antes da DC5 (o arquivo de gasto da fala livre fica fora do git, um por pasta): o fim da validacao da DC4, e na
# validacao da DC5 tambem o fim da calibracao dela
META_DC4_VALIDACAO = "artifacts_v3_conversa_dc4/validacao/meta.json"
META_CALIBRACAO = "artifacts_v3_conversa_dc5/calibracao/meta.json"
# o custo real por fala do H na DC4 (secao 8): o `pelo_usage_usd` do H sobre as falas do H da validacao da DC4
FALAS_POR_BRACO_DC4 = 162

ParadaNoTeto = dc4.ParadaNoTeto
ModeloTrocado = dc4.ModeloTrocado


# ================================================================== a config e as travas
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(plano: str) -> None:
    """o cabecalho do plano tem uma linha de status so, e ela comeca com "**Status: APROVADO pelo Matheus\""""
    cabecalho = []
    for x in plano.splitlines():
        if x.startswith("## "):
            break
        cabecalho.append(x)
    status = [x for x in cabecalho if x.startswith("**Status:")]
    if len(status) != 1 or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho: {status or 'sem a linha do status'}")


def exigir_faixa(fase: str) -> None:
    """D-DC5-1: a linha da DC5 em FAIXAS_RESERVADAS cobre a subfaixa da fase e diz que ela e da DC5"""
    if fase == "fumaca":
        return
    lo, hi = FAIXAS[fase]
    nome = {"calibracao": "a calibracao da DC5", "validacao": "a validacao da DC5"}[fase]
    if not any(a <= lo and hi <= b and f"{lo}-{hi} {nome}" in texto for a, b, texto in FAIXAS_RESERVADAS):
        raise RuntimeError(f"a subfaixa {lo}-{hi} ({nome}) nao esta em FAIXAS_RESERVADAS (D-DC5-1)")


def conferir_config(cfg: dict) -> None:
    """a config da fase e a do plano, a letra; a fumaca so nas sementes dos testes"""
    fase = cfg.get("fase")
    if fase not in FASES:
        raise ValueError(f"fase {fase!r}: so {FASES}")
    if cfg.get("plano") != PLANO:
        raise ValueError(f"o plano da config e {cfg.get('plano')!r}, nao {PLANO}")
    bases = cfg["unidades"]["bases"]
    if len(bases) != 1:
        raise ValueError("a DC5 tem uma base por fase")
    if list(cfg["bracos"]) != list(BRACOS):
        raise ValueError(f"os bracos sao {list(BRACOS)} (D-DC5-2)")
    if list(cfg["vozes"]) != list(VOZES):
        raise ValueError(f"as vozes sao {list(VOZES)} (secao 2)")
    if cfg["teto_usd"] != TETO_USD:
        raise ValueError(f"o teto e US$ {TETO_USD} (D-DC5-9)")
    lim = cfg.get("estimativa_maxima_usd")
    if lim is not None and not (isinstance(lim, (int, float)) and 0 < lim <= TETO_USD):
        raise ValueError(f"estimativa_maxima_usd invalida: {lim!r}")
    if fase == "fumaca":
        if bases[0] not in SEMENTES_DOS_TESTES:
            raise ValueError(f"a fumaca so roda nas sementes dos testes {SEMENTES_DOS_TESTES}")
        if cfg["roteiros"] != ROTEIROS["calibracao"]:
            raise ValueError("a fumaca usa os roteiros da calibracao")
        return
    lo, hi = FAIXAS[fase]
    if not lo <= bases[0] <= hi:
        raise ValueError(f"a base {bases[0]} fora da subfaixa da {fase} ({lo}-{hi}, D-DC5-1)")
    t = TAMANHO[fase]
    for k in ("n_e3_por_pedido", "n_e2", "min_ep_e2", "n_sequencias", "n_es"):
        if cfg[k] != t[k]:
            raise ValueError(f"{k} = {cfg[k]}, o plano diz {t[k]} na {fase} (secao 5)")
    if (cfg["dias"], cfg["orcamento_por_dia"]) != (DIAS, ORCAMENTO_POR_DIA):
        raise ValueError("o cenario da DC3: 14 dias, orcamento 16 (secao 5)")
    if cfg["roteiros"] != ROTEIROS[fase]:
        raise ValueError(f"a {fase} usa {ROTEIROS[fase]}")


def carregar_roteiros(cfg: dict) -> list[dict]:
    """os roteiros da fase, na ordem fixa dos papeis (secao 5). O arquivo da validacao so e aberto na validacao."""
    caminho = cfg["roteiros"]
    if caminho == ROTEIROS["validacao"] and cfg["fase"] != "validacao":
        raise RuntimeError("os roteiros da validacao so se leem na validacao (secao 5)")
    d = json.loads((RAIZ / caminho).read_text(encoding="utf-8"))
    fase_do_arquivo = "calibracao" if cfg["fase"] == "fumaca" else cfg["fase"]
    if d["fase"] != fase_do_arquivo or tuple(d["papeis"]) != PAPEIS:
        raise ValueError(f"{caminho}: a fase ou a ordem dos papeis nao e a do plano")
    rs = d["roteiros"]
    n = TAMANHO[fase_do_arquivo]["roteiros"]
    if len(rs) != n or len({r["id"] for r in rs}) != n:
        raise ValueError(f"{caminho}: {len(rs)} roteiros, o plano diz {n}")
    for r in rs:
        if tuple(t["papel"] for t in r["turnos"]) != PAPEIS:
            raise ValueError(f"{caminho}/{r['id']}: a ordem dos turnos nao e a fixa")
        for t in r["turnos"]:
            if not isinstance(t["texto"], str) or not t["texto"].strip() or len(t["texto"]) > dc4.MAX_TEXTO_JOGADOR:
                raise ValueError(f"{caminho}/{r['id']}: texto do turno {t['papel']} invalido")
    return rs


# ================================================================== a lista das frases-modelo (4.6, Q6)
def frases_modelo_de_hoje() -> dict:
    """a lista da Q6 tirada do prompt da voz do jogo: as falas dos exemplos (`EXEMPLOS_VOZ_V3`, que contem os da v1 e da v2) e a frase da
    regra 3 da voz-v2; e, a parte, as frases da regra do pedido da voz-v3b, que nenhuma das duas vozes da DC5 recebe"""
    jogo = re.findall(r'"fala": "([^"]*)"', pr.EXEMPLOS_VOZ_V3) + re.findall(r'\("([^"]*)"\)', pr.REGRA_3_VOZ_V2)
    v3b = re.findall(r'"([^"]+)"', pr.REGRA_PEDIDO_VOZ_V3B.split("Peça só isso")[0])
    return {"jogo": jogo, "v3b": [f for f in v3b if f != "P"]}


def carregar_frases_modelo() -> dict:
    """a lista congelada (o sha256 vai ao registro); falha alto se o prompt de hoje der outra"""
    d = json.loads((RAIZ / FRASES_MODELO).read_text(encoding="utf-8"))
    if {k: d[k] for k in ("jogo", "v3b")} != frases_modelo_de_hoje():
        raise RuntimeError(f"{FRASES_MODELO} nao e a lista do prompt de hoje")
    return d


# ================================================================== o registro da rodada (secao 9)
def arquivos_do_registro() -> list[str]:
    fixos = [ORQUESTRADOR, "experiments/entradas_dc5.py", "experiments/entradas_dc4.py", "experiments/montador_voz_rede.py",
             "experiments/marcacao_dc5.py", "experiments/run_v3_conversa_dc4.py", "experiments/run_v3_conversa_dc3.py",
             "experiments/exportar_gabarito_voz_jogo_dc5.py", CONFIGS["calibracao"], CONFIGS["validacao"], ROTEIROS["calibracao"],
             ROTEIROS["validacao"], FRASES_MODELO, GABARITO_VOZ_JOGO, RUBRICA, "digilab/config.py", "digilab/metrics.py",
             "servidor/fala_livre_claude.py", "servidor/fala_livre.py", "servidor/fala_llm.py"]
    return fixos + [p.relative_to(RAIZ).as_posix() for p in sorted((RAIZ / "digilab_fala_livre").glob("*.py"))]


def sha_dos_arquivos() -> dict:
    return {f: dc4.sha_arquivo(RAIZ / f) for f in arquivos_do_registro()}


def texto_do_registro() -> str:
    ln = [REGISTRO_TITULO, "", "Os sha256 de hoje (gerados por `python experiments/run_v3_conversa_dc5.py --registro`):", ""]
    ln += [f"- `{f}`: `{s}`" for f, s in sha_dos_arquivos().items()]
    return "\n".join(ln) + "\n"


def registro_do_plano(plano: str) -> dict:
    i = plano.find("\n" + REGISTRO_TITULO)
    if i < 0:
        raise RuntimeError(f"o registro da rodada ({REGISTRO_TITULO}) nao esta no plano: a validacao nao roda antes dele (secao 9)")
    j = plano.find("\n## ", i + 1)
    shas = dict(re.findall(r"^- `([^`]+)`: `([0-9a-f]{64})`$", plano[i: len(plano) if j < 0 else j], re.M))
    if not shas:
        raise RuntimeError("o registro da rodada sem os sha256")
    return shas


def exigir_registro(plano: str) -> None:
    gravado, hoje = registro_do_plano(plano), sha_dos_arquivos()
    if set(gravado) != set(hoje):
        raise RuntimeError(f"o registro lista outros arquivos: faltam {sorted(set(hoje) - set(gravado))}, sobram {sorted(set(gravado) - set(hoje))}")
    mudados = sorted(f for f in hoje if gravado[f] != hoje[f])
    if mudados:
        raise RuntimeError(f"os arquivos mudaram depois do registro da rodada: {mudados}")


def exigir_voz_do_jogo() -> None:
    """secao 9: a voz do jogo da rodada e a do gabarito gravado antes da DC5 (o texto montado para entradas fixas, byte a byte)"""
    if gvj.gabarito() != json.loads((RAIZ / GABARITO_VOZ_JOGO).read_text(encoding="utf-8")):
        raise RuntimeError("a voz do jogo mudou: o texto montado nao e o do gabarito gravado antes da DC5")


# ================================================================== o gasto e a estimativa (secao 8)
def custo_por_fala_h_dc4() -> float:
    """o custo real por fala do H na validacao da DC4 (`pelo_usage_usd` do H / 162)"""
    meta = json.loads((RAIZ / META_DC4_VALIDACAO).read_text(encoding="utf-8"))
    return meta["gasto"]["pelo_usage_usd"]["H"] / FALAS_POR_BRACO_DC4


def falas_por_celula(cfg: dict) -> int:
    t = TAMANHO["calibracao" if cfg["fase"] == "fumaca" else cfg["fase"]]
    return (3 * t["n_e3_por_pedido"] + t["n_e2"] + t["n_es"] * CONFIG_VOZ_V4.falas_por_sequencia_es
            + t["roteiros"] * t["n_sequencias"] * len(PAPEIS))


def estimativa_usd(cfg: dict) -> float:
    """secao 8: as falas do H (as duas vozes) x o custo real por fala do H na DC4 x (1 + a margem)"""
    n_h = sum(1 for b, _ in CELULAS if BRACOS[b][0] == "claude") * falas_por_celula(cfg)
    return n_h * custo_por_fala_h_dc4() * (1 + CONFIG_VOZ_V4.margem_custo)


def exigir_estimativa(cfg: dict, gasto_atual: float) -> float:
    """a estimativa cabe no teto (com o que ja foi gasto) e no limite da config, se houver; senao falha alto antes de qualquer chamada"""
    est = estimativa_usd(cfg)
    if gasto_atual + est > cfg["teto_usd"]:
        raise RuntimeError(f"a estimativa (US$ {est:.3f}) passa do teto: ja gasto US$ {gasto_atual:.3f} de {cfg['teto_usd']:.2f}")
    lim = cfg.get("estimativa_maxima_usd")
    if lim is not None and est > lim:
        raise RuntimeError(f"a estimativa (US$ {est:.3f}) passa do limite da config (US$ {lim:.2f})")
    return est


def piso_do_gasto(fase: str) -> float:
    """o gasto que ja aconteceu antes da fase: o fim da validacao da DC4 e, na validacao da DC5, tambem o da calibracao dela"""
    if fase == "fumaca":
        return 0.0
    metas = [META_DC4_VALIDACAO] + ([META_CALIBRACAO] if fase == "validacao" else [])
    fins = []
    for m in metas:
        arq = RAIZ / m
        if not arq.exists():
            raise RuntimeError(f"a {fase} sem o {m}: o gasto acumulado e o piso do teto (D-DC5-9)")
        fins.append(float(json.loads(arq.read_text(encoding="utf-8"))["gasto"]["fim_usd"]))
    return max(fins)


def clientes_reais(cfg: dict) -> dict:
    """os clientes de verdade: construir nao chama nada. O gasto e o da fala livre, com o piso (`piso_do_gasto`)."""
    gasto = dc4.gasto_com_piso(ControleGasto(cfg["teto_usd"], ARQUIVO_GASTO_LIVRE), piso_do_gasto(cfg["fase"]))
    voz = {b: ClienteOllama(m) if p == "ollama" else ClienteClaude(m, gasto) for b, (p, m) in BRACOS.items()}
    return {"voz": voz, "verif": ClienteOllama(MODELO_VERIF), "gasto": gasto, "falso": False}


def clientes_falsos(teto: float = TETO_USD) -> dict:
    gasto = ControleGasto(teto, None)
    voz = {b: dc4.ClienteFalso(m, "voz") if p == "ollama" else ClienteClaude(m, gasto, sdk=dc4.SdkFalso()) for b, (p, m) in BRACOS.items()}
    return {"voz": voz, "verif": dc4.ClienteFalso(MODELO_VERIF, "verif"), "gasto": gasto, "falso": True}


# ================================================================== o servico e as falas
class ServicoDC5(ServicoFalaLivre):
    """O servico do jogo, com o cliente da voz do braco, o verificador proprio e a voz da celula: na `jogo`, nada muda (a voz do formato e
    nenhuma fala ja dita); na `v4`, a voz-v4 e, na fala espontanea do ES, as falas ja ditas da sequencia (`self.ditas`)."""

    def __init__(self, voz_cliente, verif, voz: str) -> None:
        if voz not in VOZES:
            raise ValueError(f"voz {voz!r}")
        super().__init__(cliente=voz_cliente, ambiente={})
        self._verif_dc5, self.voz, self.ditas = verif, voz, None

    @property
    def cliente_verif(self):
        return self._verif_dc5

    def voz_dos_conceitos(self, conceitos):
        return pr.VERSAO_VOZ_V4 if self.voz == "v4" else None

    def ditas_da_voz(self, situacao: str):
        if self.ditas is not None and (self.voz != "v4" or situacao != "espontanea"):
            raise RuntimeError("as falas ja ditas so na voz-v4 e na fala espontanea (plano, 3.4)")
        return self.ditas


def semente_do_turno(base: int, item: str) -> int:
    """a semente do turno (secao 7): a mesma nas quatro celulas; o Ollama a usa, a API nao"""
    return derivar_semente(PREFIXO, base, "ollama", item) % SEMENTE_MAX


def voz_esperada(voz: str, versao_dec: str) -> str:
    if voz == "v4":
        return pr.VERSAO_VOZ_V4
    return pr.VERSAO_VOZ_V3 if versao_dec == VERSAO_DEC_V3 else pr.VERSAO_VOZ_V2


def conferir_registro(reg: dict) -> None:
    """secao 9: o da DC4 (a entrada, o braco, a semente, o usage, o modelo) e a voz da celula"""
    dc4.conferir_registro(reg)
    if reg.get("voz") not in VOZES or reg["celula"] != f"{reg['braco']}-{reg['voz']}":
        raise RuntimeError(f"a fala {reg['id']} sem a celula")
    if reg["versao_prompt"] != voz_esperada(reg["voz"], reg["versao_dec"]):
        raise RuntimeError(f"a fala {reg['id']}: a voz {reg['versao_prompt']!r}, a celula pede {voz_esperada(reg['voz'], reg['versao_dec'])!r}")
    if (reg.get("ditas") is not None) != (reg["voz"] == "v4" and reg["conjunto"] == "ES" and bool(reg["ditas"])):
        raise RuntimeError(f"a fala {reg['id']}: as falas ja ditas fora da voz-v4 no ES")


def falar(servico: ServicoDC5, chamadas: dict, braco: str, voz: str, item: str, entrada: dict, situacao: str, semente: int,
          fala_jogador: str | None = None, historico: list | None = None, ditas: list | None = None) -> dict:
    servico.ditas = ditas or None
    try:
        reg = dc4.falar(servico, chamadas, braco, f"{braco}-{voz}/{item}", entrada, situacao, semente, fala_jogador, historico)
    finally:
        servico.ditas = None
    reg.update(celula=f"{braco}-{voz}", voz=voz, item=item, ditas=ditas or None)
    conferir_registro(reg)
    return reg


def rodar_celula(braco: str, voz: str, servico: ServicoDC5, chamadas: dict, entradas: dict, roteiros: list[dict], gravar) -> list[dict]:
    base, regs = entradas["base"], []

    def guardar(reg):
        gravar(reg)
        regs.append(reg)

    for e in entradas["E3"] + entradas["E2"]:
        guardar(falar(servico, chamadas, braco, voz, e["id"], e, "espontanea", semente_do_turno(base, e["id"])))
    for seq in entradas["sequencias_es"]:
        ja = []
        for t, e in enumerate(seq["entradas"]):
            ditas = [f for f, est in ja if est == e["estagio"]][-CONFIG_VOZ_V4.n_ditas:] if voz == "v4" else []
            reg = falar(servico, chamadas, braco, voz, e["id"], e, "espontanea", semente_do_turno(base, e["id"]), ditas=ditas)
            reg.update(sequencia_es=seq["id"], turno=t)
            if reg["erro"] is None:                    # a fala generica nao e fala do pet: nao vai como ja dita
                ja.append((reg["fala"], e["estagio"]))
            guardar(reg)
    for roteiro in roteiros:
        for seq in entradas["sequencias"]:
            historico = []
            for t, turno in enumerate(roteiro["turnos"]):
                e = seq["entradas"][t]
                item = f"{roteiro['id']}-{seq['id']}-t{t}"
                hist = [h for h in historico if h[2] == e["estagio"]][-pr.MAX_TROCAS:]
                reg = falar(servico, chamadas, braco, voz, item, e, "conversa", semente_do_turno(base, item), turno["texto"], hist)
                reg.update(conversa=f"{roteiro['id']}-{seq['id']}", roteiro=roteiro["id"], sequencia=seq["id"], turno=t, papel=turno["papel"])
                historico.append([turno["texto"], reg["fala"], e["estagio"]])
                guardar(reg)
    return regs


def itens_esperados(entradas: dict, roteiros: list[dict]) -> list[str]:
    return ([e["id"] for e in entradas["E3"] + entradas["E2"]] + [e["id"] for s in entradas["sequencias_es"] for e in s["entradas"]]
            + [f"{r['id']}-{s['id']}-t{t}" for r in roteiros for s in entradas["sequencias"] for t in range(len(PAPEIS))])


def conferir_registros(regs: list[dict], entradas: dict, roteiros: list[dict], celulas) -> None:
    """o fim da rodada: cada celula com cada item uma vez, na ordem, e as quatro com as mesmas entradas e sementes"""
    esperados = itens_esperados(entradas, roteiros)
    ref = None
    for b, v in celulas:
        meus = [r for r in regs if r["celula"] == f"{b}-{v}"]
        if [r["item"] for r in meus] != esperados:
            raise RuntimeError(f"{b}-{v}: os itens nao sao os do plano")
        for r in meus:
            conferir_registro(r)
        par = [(r["item"], r["entrada"], r["semente"], r["fala_jogador"]) for r in meus]
        if ref is not None and par != ref:
            raise RuntimeError(f"{b}-{v}: as entradas ou as sementes nao sao as das outras celulas")
        ref = par


# ================================================================== os pares da naturalidade (4.5)
def sortear_pares(base: int, conversas: list[str]) -> list[dict]:
    """voz-v4 x voz do jogo, em cada braco e cada conversa: o lado de cada voz e a ordem dos pares, pela rng do fluxo `pares`"""
    rng = en.rng_do_fluxo(base, "pares")
    pares = []
    for b in BRACOS:
        for c in conversas:
            lados = ["v4", "jogo"] if rng.random() < 0.5 else ["jogo", "v4"]
            pares.append({"conversa": c, "braco": b, "esquerda": lados[0], "direita": lados[1]})
    rng.shuffle(pares)
    return [{"id": f"P{n:02d}", **p} for n, p in enumerate(pares)]


def conferir_pares(pares: list[dict], base: int, conversas: list[str]) -> None:
    if pares != sortear_pares(base, conversas):
        raise RuntimeError("a ordem dos pares nao e a sorteada (secao 9)")


# ================================================================== a rodada
def _json(caminho: Path, obj) -> None:
    caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def _meta_do_gasto(gasto: ControleGasto, inicio: float, gravadas: list[dict]) -> dict:
    return {"limite_usd": gasto.limite, "inicio_usd": round(inicio, 6), "fim_usd": round(gasto.gasto, 6),
            "da_rodada_usd": round(gasto.gasto - inicio, 6),
            "pelo_usage_usd": {f"{b}-{v}": round(sum(custo_usd(BRACOS[b][1], r["usage"]["entrada"], r["usage"]["saida"]) for r in gravadas
                                                     if r["celula"] == f"{b}-{v}" and r["usage"]["entrada"] is not None), 6)
                               for b, v in CELULAS if BRACOS[b][0] == "claude"}}


def rodar(cfg: dict, roteiros: list[dict], pasta: Path, clientes: dict, exportar=en.exportar) -> dict:
    """as entradas, as falas das quatro celulas (uma por vez), os pares, o material da marcacao e o meta. Grava cada fala na hora."""
    if pasta.exists():
        raise RuntimeError(f"a pasta {pasta} ja existe: nada se grava por cima (uma queda recomeca numa pasta nova, secao 8)")
    exigir_voz_do_jogo()
    frases = carregar_frases_modelo()
    gasto = clientes["gasto"]
    gasto_inicio = gasto.gasto
    estimativa = exigir_estimativa(cfg, gasto_inicio)
    pasta.mkdir(parents=True)
    base = cfg["unidades"]["bases"][0]
    tags = {"falso": True} if clientes["falso"] else dc4.tag_ollama(clientes["verif"])
    entradas = exportar(base, cfg["dias"], cfg["orcamento_por_dia"], cfg["n_e3_por_pedido"], cfg["n_e2"], cfg["min_ep_e2"],
                        cfg["n_sequencias"], cfg["n_es"])
    _json(pasta / "entradas.json", entradas)
    arq = (pasta / "falas.jsonl").open("w", encoding="utf-8", newline="\n")
    chamadas = {"voz": [], "verif": []}
    verif = dc4.ClienteRegistrado(clientes["verif"], "verif", chamadas["verif"])
    regs, parada, gravadas = [], None, []
    meta = {"fase": cfg["fase"], "base": base, "plano": PLANO, "plano_sha256": dc4.sha_arquivo(RAIZ / PLANO), "arquivos": sha_dos_arquivos(),
            "celulas": [f"{b}-{v}" for b, v in CELULAS], "estimativa_usd": round(estimativa, 6),
            "frases_modelo_sha256": dc4.sha_arquivo(RAIZ / FRASES_MODELO), "n_frases_modelo": {k: len(frases[k]) for k in ("jogo", "v3b")},
            "clientes_falsos": clientes["falso"], "ollama": tags, "python": platform.python_version(), "inicio": time.strftime("%Y-%m-%dT%H:%M:%S")}

    def gravar(reg: dict) -> None:
        arq.write(json.dumps(reg, ensure_ascii=False, sort_keys=True) + "\n")
        arq.flush()
        gravadas.append(reg)

    try:
        for b, v in CELULAS:
            voz = dc4.ClienteRegistrado(clientes["voz"][b], f"voz/{b}-{v}", chamadas["voz"])
            if voz.modelo != BRACOS[b][1]:
                raise ModeloTrocado(f"o braco {b} com o cliente de {voz.modelo!r}")
            regs += rodar_celula(b, v, ServicoDC5(voz, verif, v), chamadas, entradas, roteiros, gravar)
    except ParadaNoTeto as err:
        parada = str(err)
    finally:
        arq.close()
        meta["gasto"] = _meta_do_gasto(gasto, gasto_inicio, gravadas)
        meta["parada_no_teto"] = parada
        meta["modelos_devolvidos"] = {f"{b}-{v}": sorted({c["modelo_devolvido"] for c in chamadas["voz"]
                                                          if c["papel"] == f"voz/{b}-{v}" and c["modelo_devolvido"]}) for b, v in CELULAS}
        meta["verificador_devolvido"] = sorted({c["modelo_devolvido"] for c in chamadas["verif"] if c["modelo_devolvido"]})
        meta["falas"] = len(gravadas)
        meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        _json(pasta / "meta.json", meta)
    if parada is not None:
        raise ParadaNoTeto(parada + f" (a rodada parou com {len(regs)} falas no disco)")
    if gasto.gasto > gasto.limite:
        raise RuntimeError(f"o gasto passou do teto: US$ {gasto.gasto} > {gasto.limite}")
    conferir_registros(regs, entradas, roteiros, CELULAS)
    conversas = [f"{r['id']}-{s['id']}" for r in roteiros for s in entradas["sequencias"]]
    pares = sortear_pares(base, conversas)
    conferir_pares(pares, base, conversas)
    _json(pasta / "pares.json", pares)
    mc.montar(pasta / "marcacao", base, entradas, regs, pares)
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="a voz nova contra a voz do jogo, DC5 (docs/PLANO_ANALISE_V3_CONVERSA_DC5.md)")
    ap.add_argument("--config")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--falso", action="store_true", help="os clientes sem rede (so na fumaca)")
    ap.add_argument("--saida", help="outra pasta de saida (so na fumaca)")
    ap.add_argument("--registro", action="store_true", help="imprime o texto do registro da rodada e sai")
    a = ap.parse_args(argv)
    if a.registro:
        print(texto_do_registro(), end="")
        return 0
    if a.config is None:
        ap.error("--config e obrigatorio")
    if a.processos != 1:
        raise ValueError("a DC5 roda num processo so (as chamadas sao uma por vez; secao 8)")
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)                 # o H10 (D-IA-6) e a V3-D8, antes de tudo
    cfg = json.loads((RAIZ / a.config).read_text(encoding="utf-8"))
    conferir_config(cfg)
    plano = _plano()
    exigir_plano_aprovado(plano)
    exigir_faixa(cfg["fase"])
    fumaca = cfg["fase"] == "fumaca"
    if a.falso != fumaca:
        raise RuntimeError("os clientes falsos sao so da fumaca, e a fumaca so roda com eles (a DC5a nao chama modelo)")
    if a.saida is not None and not fumaca:
        raise RuntimeError("a pasta de saida da calibracao e da validacao e a da config")
    if cfg["fase"] == "validacao":
        exigir_registro(plano)
    roteiros = carregar_roteiros(cfg)
    pasta = RAIZ / (a.saida or cfg["saida"])
    clientes = clientes_falsos() if fumaca else clientes_reais(cfg)
    meta = rodar(cfg, roteiros, pasta, clientes)
    print(json.dumps({k: meta[k] for k in ("fase", "base", "falas", "estimativa_usd", "gasto", "parada_no_teto", "modelos_devolvidos")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
