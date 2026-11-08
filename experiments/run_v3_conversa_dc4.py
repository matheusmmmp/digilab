"""O orquestrador da DC4, a voz da rede com modelo de verdade (CONVERSA_PET; docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, APROVADO pelo Matheus em
2026-11-08, DC4-1 a DC4-8). Codigo da DC4a: **nenhuma chamada a modelo de verdade roda aqui na DC4a**; a calibracao (DC4b) e a validacao (DC4c)
usam este arquivo.

O caminho de cada fala e o do jogo (secao 0): as entradas (`entradas_dc4`, o `dec-v2`/`dec-v3` montado como a pagina monta) vao ao
`ServicoFalaLivre` do servidor como a pagina as manda (`situacao`, `estado` so com a identidade, `conceitos`, `semente`, e na conversa a
`fala_jogador`, o `historico` de fronteira da M2 e o `comando`), e o servidor valida, gera a voz (`voz-v2`/`voz-v3`) e confere pelo verificador
(`verif-v8`/`verif-v9`). Os bracos (secao 2, DC4-2) so trocam o cliente da voz:

| braco | modelo | cliente |
|---|---|---|
| G | `gemma2:9b` | `ClienteOllama` (local), com a semente do turno |
| H | `claude-haiku-5-5` | `ClienteClaude` da M5, esforco low, sem semente (a API nao aceita) |
| S | `claude-sonnet-5-5` | idem |

O verificador e o mesmo em todos: o extrator no `gemma2:9b` local, o julgamento do codigo.

As situacoes (secao 2): a fala espontanea, uma por entrada do E3 e do E2; e a conversa, cada roteiro com cada sequencia (6 turnos, a entrada
do turno t e a decisao t da sequencia; o historico so do estagio atual, as ultimas 10 trocas, como a pagina). A mesma entrada, o mesmo estagio,
a mesma semente e o mesmo roteiro nos tres bracos (o pareamento).

As conferencias (secao 9), falhando alto:
- o modelo que o cliente devolve e o pedido (`modelo_confere`; a API pode devolver o id com sufixo de data, `<pedido>-AAAAMMDD`);
- toda fala tem a entrada, o braco, a semente e o `usage` (o `usage` pode faltar so na chamada que falhou, registrada com o erro);
- a ordem dos pares e a sorteada (`conferir_pares`);
- o gasto nao passa do teto: antes de cada chamada da API o custo maximo e conferido contra o teto (`ParadaNoTeto`), e a rodada para ali,
  com o que ja foi gravado no disco.

As travas: o plano com "APROVADO pelo Matheus" no cabecalho; o `tools/pre_run.py` (o H10, D-IA-6: o plano daqui e o da `origin/main`; a base
numa faixa reservada; uma run por vez; no maximo 4 processos); a linha da CONVERSA_PET em `FAIXAS_RESERVADAS` com as subfaixas da DC4
(DC4-1); a config da fase igual a do plano (DC4-5, DC4-6); os roteiros da validacao so lidos na validacao; na validacao, o registro da rodada
(a secao 13 do plano, `--registro`) com os sha256 de hoje. A fumaca (as sementes dos testes) so roda com os clientes falsos (`--falso`), e
os clientes falsos so na fumaca.

    python experiments/run_v3_conversa_dc4.py --config experiments/configs/v3_conversa_dc4/fumaca.json --falso     # fumaca, sem modelo
    python experiments/run_v3_conversa_dc4.py --config experiments/configs/v3_conversa_dc4/calibracao.json         # DC4b
    python experiments/run_v3_conversa_dc4.py --config experiments/configs/v3_conversa_dc4/validacao.json          # DC4c, uma vez
    python experiments/run_v3_conversa_dc4.py --registro                                                           # o texto da secao 13
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import entradas_dc4 as en  # noqa: E402
import marcacao_dc4 as mc  # noqa: E402
import pre_run  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402

from digilab.protocol import derivar_semente  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama, Resposta  # noqa: E402
from digilab_fala_livre.prompt import MAX_TROCAS  # noqa: E402
from servidor.fala_livre import MAX_TEXTO_JOGADOR, ServicoFalaLivre  # noqa: E402
from servidor.fala_livre_claude import ARQUIVO_GASTO_LIVRE, ClienteClaude, _partir  # noqa: E402
from servidor.fala_llm import LIMITE_USD_LIVRE_PADRAO, ControleGasto, custo_usd  # noqa: E402

ORQUESTRADOR = "experiments/run_v3_conversa_dc4.py"
PLANO = "docs/PLANO_ANALISE_V3_CONVERSA_DC4.md"
RUBRICA = "docs/RUBRICA_DC4_FIDELIDADE.md"
PREFIXO = en.PREFIXO
FASES = ("fumaca", "calibracao", "validacao")
BRACOS = {"G": ("ollama", "gemma2:9b"), "H": ("claude", "claude-haiku-5-5"), "S": ("claude", "claude-sonnet-5-5")}   # DC4-2
MODELO_VERIF = "gemma2:9b"                                                        # secao 2: o extrator, igual em todos os bracos
FAIXAS = {"calibracao": (20262200, 20262499), "validacao": (20262500, 20262899)}   # secao 7, DC4-1
SEMENTES_DOS_TESTES = (101, 202, 303, 404, 505)
ROTEIROS = {"calibracao": "experiments/configs/v3_conversa_dc4/roteiros_calibracao.json",
            "validacao": "experiments/configs/v3_conversa_dc4/roteiros_validacao.json"}
CONFIGS = {"calibracao": "experiments/configs/v3_conversa_dc4/calibracao.json", "validacao": "experiments/configs/v3_conversa_dc4/validacao.json"}
# o tamanho da fase (secao 3 e DC4-5): E3 por pedido, E2, as lembrancas com episodio no E2, as sequencias e os roteiros
TAMANHO = {"calibracao": {"n_e3_por_pedido": 10, "n_e2": 15, "min_ep_e2": 5, "n_sequencias": 3, "roteiros": 2},
           "validacao": {"n_e3_por_pedido": 20, "n_e2": 30, "min_ep_e2": 10, "n_sequencias": 3, "roteiros": 4}}
DIAS, ORCAMENTO_POR_DIA = 14, 16                                                  # secao 3: o cenario da DC3
TETO_USD = LIMITE_USD_LIVRE_PADRAO                                                # DC4-6: o teto de US$ 3 da fala livre
PAPEIS = ("cumprimento", "como_esta", "lembranca_falsa", "injecao", "pedido_acao", "pergunta_aberta")   # secao 3, a ordem fixa
PAPEL_INJECAO = "injecao"
REGISTRO_TITULO = "## 13. O registro da rodada"
SEMENTE_MAX = 2**31                                                               # o `_semente` do servidor: 0 <= s < 2**31


class ParadaNoTeto(RuntimeError):
    """A proxima chamada da API passaria do teto: a rodada para (secao 9). Nao e OSError: nao vira fala generica."""


class ModeloTrocado(RuntimeError):
    """O cliente devolveu outro modelo que o pedido (secao 9)."""


# ================================================================== a config e as travas
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(plano: str) -> None:
    """o cabecalho do plano (antes da primeira secao) tem uma linha de status so, e ela comeca com "**Status: APROVADO pelo Matheus\""""
    cabecalho = []
    for x in plano.splitlines():
        if x.startswith("## "):
            break
        cabecalho.append(x)
    status = [x for x in cabecalho if x.startswith("**Status:")]
    if len(status) != 1 or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho: {status or 'sem a linha do status'}")


def exigir_faixa(fase: str) -> None:
    """DC4-1: a linha da CONVERSA_PET em FAIXAS_RESERVADAS cobre a subfaixa da fase e diz que ela e da DC4"""
    if fase == "fumaca":
        return
    lo, hi = FAIXAS[fase]
    nome = {"calibracao": "a calibracao da DC4", "validacao": "a validacao da DC4"}[fase]
    if not any(a <= lo and hi <= b and f"{lo}-{hi} {nome}" in texto for a, b, texto in FAIXAS_RESERVADAS):
        raise RuntimeError(f"a subfaixa {lo}-{hi} ({nome}) nao esta em FAIXAS_RESERVADAS (DC4-1)")


def conferir_config(cfg: dict) -> None:
    """a config da fase e a do plano, a letra (DC4-1, DC4-2, DC4-5, DC4-6); a fumaca so nas sementes dos testes"""
    fase = cfg.get("fase")
    if fase not in FASES:
        raise ValueError(f"fase {fase!r}: so {FASES}")
    if cfg.get("plano") != PLANO:
        raise ValueError(f"o plano da config e {cfg.get('plano')!r}, nao {PLANO}")
    bases = cfg["unidades"]["bases"]
    if len(bases) != 1:
        raise ValueError("a DC4 tem uma base por fase")
    if list(cfg["bracos"]) != list(BRACOS):
        raise ValueError(f"os bracos sao {list(BRACOS)} (DC4-2)")
    if cfg["teto_usd"] != TETO_USD:
        raise ValueError(f"o teto e US$ {TETO_USD} (DC4-6)")
    if fase == "fumaca":
        if bases[0] not in SEMENTES_DOS_TESTES:
            raise ValueError(f"a fumaca so roda nas sementes dos testes {SEMENTES_DOS_TESTES}")
        if cfg["roteiros"] != ROTEIROS["calibracao"]:
            raise ValueError("a fumaca usa os roteiros da calibracao")
        return
    lo, hi = FAIXAS[fase]
    if not lo <= bases[0] <= hi:
        raise ValueError(f"a base {bases[0]} fora da subfaixa da {fase} ({lo}-{hi}, DC4-1)")
    t = TAMANHO[fase]
    for k in ("n_e3_por_pedido", "n_e2", "min_ep_e2", "n_sequencias"):
        if cfg[k] != t[k]:
            raise ValueError(f"{k} = {cfg[k]}, o plano diz {t[k]} na {fase} (secao 3, DC4-5)")
    if (cfg["dias"], cfg["orcamento_por_dia"]) != (DIAS, ORCAMENTO_POR_DIA):
        raise ValueError("o cenario da DC3: 14 dias, orcamento 16 (secao 3)")
    if cfg["roteiros"] != ROTEIROS[fase]:
        raise ValueError(f"a {fase} usa {ROTEIROS[fase]}")


def carregar_roteiros(cfg: dict) -> list[dict]:
    """os roteiros da fase, na ordem fixa dos papeis (secao 3). O arquivo da validacao so e aberto na validacao (fechado ate a rodada unica)."""
    caminho = cfg["roteiros"]
    if caminho == ROTEIROS["validacao"] and cfg["fase"] != "validacao":
        raise RuntimeError("os roteiros da validacao so se leem na validacao (secao 3)")
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
            if not isinstance(t["texto"], str) or not t["texto"].strip() or len(t["texto"]) > MAX_TEXTO_JOGADOR:
                raise ValueError(f"{caminho}/{r['id']}: texto do turno {t['papel']} invalido")
    return rs


def sha_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def arquivos_do_registro() -> list[str]:
    """os arquivos cujo sha256 vai ao registro da rodada (secao 9): este orquestrador e os que ele usa, as configs, os roteiros, a rubrica,
    `digilab_fala_livre/*.py` e o servidor da fala livre (o cliente Claude, o servico e o gasto)"""
    fixos = [ORQUESTRADOR, "experiments/entradas_dc4.py", "experiments/montador_voz_rede.py", "experiments/marcacao_dc4.py",
             "experiments/run_v3_conversa_dc3.py", CONFIGS["calibracao"], CONFIGS["validacao"], ROTEIROS["calibracao"], ROTEIROS["validacao"],
             RUBRICA, "servidor/fala_livre_claude.py", "servidor/fala_livre.py", "servidor/fala_llm.py"]
    return fixos + [p.relative_to(RAIZ).as_posix() for p in sorted((RAIZ / "digilab_fala_livre").glob("*.py"))]


def sha_dos_arquivos() -> dict:
    return {f: sha_arquivo(RAIZ / f) for f in arquivos_do_registro()}


def texto_do_registro() -> str:
    """o texto da secao 13 do plano (a DC4b o completa com as versoes dos modelos e a tag do Ollama, e o commita antes da validacao)"""
    ln = [REGISTRO_TITULO, "", "Os sha256 de hoje (gerados por `python experiments/run_v3_conversa_dc4.py --registro`):", ""]
    ln += [f"- `{f}`: `{s}`" for f, s in sha_dos_arquivos().items()]
    return "\n".join(ln) + "\n"


def registro_do_plano(plano: str) -> dict:
    import re
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


# ================================================================== os clientes
def modelo_confere(pedido: str, devolvido) -> bool:
    """o devolvido e o pedido, ou o pedido com o sufixo de data da API (`claude-haiku-5-5-20261101`)"""
    return isinstance(devolvido, str) and (devolvido == pedido or (devolvido.startswith(pedido + "-") and devolvido[len(pedido) + 1:].isdigit()))


class ClienteRegistrado:
    """Embrulha um cliente (Ollama, Claude ou falso) com a mesma interface: grava cada chamada (o modelo pedido e o devolvido, os tokens, a
    latencia, a semente e o erro), confere o modelo devolvido e, num cliente com gasto, para antes da chamada que passaria do teto."""

    def __init__(self, inner, papel: str, chamadas: list) -> None:
        self.inner, self.papel, self.chamadas = inner, papel, chamadas
        self.modelo = inner.modelo

    @property
    def carregado(self):
        return getattr(self.inner, "carregado", True)

    def conversar(self, mensagens: list[dict], esquema: dict, max_tokens: int, semente: int) -> Resposta:
        gasto = getattr(self.inner, "gasto", None)
        if gasto is not None:
            sistema, conversa = _partir(mensagens)
            custo = self.inner.custo_maximo(sistema, conversa, max_tokens)
            if gasto.gasto + gasto.reservado + custo > gasto.limite:
                raise ParadaNoTeto(f"a proxima chamada ({self.modelo}, ate US$ {custo:.4f}) passaria do teto de US$ {gasto.limite:.2f} "
                                   f"(gasto US$ {gasto.gasto:.4f})")
        reg = {"papel": self.papel, "modelo_pedido": self.modelo, "semente": semente, "max_tokens": max_tokens}
        try:
            r = self.inner.conversar(mensagens, esquema, max_tokens, semente)
        except OSError as err:
            reg.update(erro=f"{type(err).__name__}: {err}", modelo_devolvido=None, tokens_entrada=None, tokens_saida=None, latencia_s=None,
                       completa=None)
            self.chamadas.append(reg)
            raise
        reg.update(erro=None, modelo_devolvido=r.modelo, tokens_entrada=r.tokens_entrada, tokens_saida=r.tokens_saida,
                   latencia_s=r.latencia_s, completa=r.completa)
        self.chamadas.append(reg)
        if not modelo_confere(self.modelo, r.modelo):
            raise ModeloTrocado(f"pedi {self.modelo!r} e veio {r.modelo!r}")
        return r


class ServicoDC4(ServicoFalaLivre):
    """O servico da fala livre do jogo, com o cliente da voz do braco e o verificador proprio (o `gemma2:9b` de todos os bracos)."""

    def __init__(self, voz, verif) -> None:
        super().__init__(cliente=voz, ambiente={})
        self._verif_dc4 = verif

    @property
    def cliente_verif(self):
        return self._verif_dc4


class ClienteFalso:
    """Cliente sem rede (fumaca e testes): a voz devolve uma fala curta que depende so da semente; o verificador, nenhuma afirmacao."""

    FALAS = ("Oi! Me dá comida?", "Tô aqui.", "Fica comigo?", "Hmm, acho que tô com sono.", "Me limpa?")

    def __init__(self, modelo: str, papel: str) -> None:
        self.modelo, self.papel, self.carregado = modelo, papel, True

    def conversar(self, mensagens, esquema, max_tokens, semente) -> Resposta:
        if self.papel == "verif":
            return Resposta(json.dumps({"afirmacoes": []}), self.modelo, 0.0, 50, 5, True)
        d = {"fala": self.FALAS[semente % len(self.FALAS)], "fatos_citados": []}
        if "comando" in esquema["properties"]:
            d["comando"] = None
        return Resposta(json.dumps(d, ensure_ascii=False), self.modelo, 0.0, 1000, 20, True)


class SdkFalso:
    """O SDK da API sem rede (so na fumaca): a resposta tem o modelo pedido, o `usage` e uma fala curta"""

    def __init__(self) -> None:
        self.messages = self

    def create(self, **kw):
        texto = json.dumps({"fala": "Oi! Me dá comida?", "fatos_citados": [],
                            **({"comando": None} if "comando" in kw["output_config"]["format"]["schema"]["properties"] else {})},
                           ensure_ascii=False)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=texto)], stop_reason="end_turn", model=kw["model"],
                               usage=SimpleNamespace(input_tokens=1500, output_tokens=30))


def clientes_reais(cfg: dict) -> dict:
    """os clientes de verdade (calibracao e validacao): construir nao chama nada (o SDK so e importado na primeira chamada)"""
    gasto = ControleGasto(cfg["teto_usd"], ARQUIVO_GASTO_LIVRE)
    voz = {b: ClienteOllama(m) if p == "ollama" else ClienteClaude(m, gasto) for b, (p, m) in BRACOS.items()}
    return {"voz": voz, "verif": ClienteOllama(MODELO_VERIF), "gasto": gasto, "falso": False}


def clientes_falsos(teto: float = TETO_USD) -> dict:
    """os clientes da fumaca: o G e o verificador falsos; o H e o S, o `ClienteClaude` de verdade sobre o `SdkFalso`, com o gasto so na
    memoria (nunca o arquivo da fala livre)"""
    gasto = ControleGasto(teto, None)
    voz = {b: ClienteFalso(m, "voz") if p == "ollama" else ClienteClaude(m, gasto, sdk=SdkFalso()) for b, (p, m) in BRACOS.items()}
    return {"voz": voz, "verif": ClienteFalso(MODELO_VERIF, "verif"), "gasto": gasto, "falso": True}


def tag_ollama(cliente) -> dict:
    """a tag do modelo no Ollama (o digest e a data), para o registro da rodada (secao 9). So nos clientes de verdade."""
    import urllib.request
    with cliente._abrir(urllib.request.Request(cliente.url + "/api/tags", method="GET"), timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
    m = next((x for x in d.get("models", []) if x.get("name") == cliente.modelo or x.get("model") == cliente.modelo), None)
    if m is None:
        raise RuntimeError(f"o Ollama nao tem o {cliente.modelo}")
    return {"modelo": cliente.modelo, "digest": m.get("digest"), "modified_at": m.get("modified_at"), "size": m.get("size")}


# ================================================================== as falas
def semente_do_turno(base: int, item: str) -> int:
    """a semente do turno (secao 7): a mesma nos tres bracos; o Ollama a usa, a API nao"""
    return derivar_semente(PREFIXO, base, "ollama", item) % SEMENTE_MAX


def marcou(verif: dict | None) -> bool | None:
    """o verificador marcou a fala (4.3): alguma afirmacao sem sustento, citado inexistente, manipulacao ou falha do extrator (a falha conta
    como marcou, o jogo cairia na fala generica). None na fala generica (nao ha o que conferir)."""
    if verif is None:
        return None
    return bool(verif["erro"] or verif["nao_suportadas"] or verif["citados_inexistentes"] or verif["manipulacao"])


def conferir_registro(reg: dict) -> None:
    """secao 9: toda fala tem a entrada, o braco, a semente e o usage (o usage so falta na chamada que falhou, com o erro registrado)"""
    for k in ("entrada", "braco", "semente", "fala", "chamada_voz"):
        if reg.get(k) is None:
            raise RuntimeError(f"a fala sem {k}: {reg.get('id')}")
    cv = reg["chamada_voz"]
    if cv["erro"] is None:
        if not all(isinstance(reg["usage"][k], int) for k in ("entrada", "saida")):
            raise RuntimeError(f"a fala {reg['id']} sem o usage")
        if not modelo_confere(BRACOS[reg["braco"]][1], cv["modelo_devolvido"]):
            raise RuntimeError(f"a fala {reg['id']} com o modelo {cv['modelo_devolvido']!r}")
    elif reg["erro"] is None:
        raise RuntimeError(f"a fala {reg['id']}: a chamada falhou e a fala nao e a generica")


def falar(servico: ServicoDC4, chamadas: dict, braco: str, rid: str, entrada: dict, situacao: str, semente: int,
          fala_jogador: str | None = None, historico: list | None = None) -> dict:
    """uma fala pelo servico do jogo: o pedido que a pagina mandaria e o que voltou, com as chamadas da voz e do verificador"""
    iv, jv = len(chamadas["voz"]), len(chamadas["verif"])
    pedido = {"situacao": situacao, "estado": entrada["estado"], "conceitos": entrada["conceitos"], "semente": semente,
              "historico": historico or []}
    if situacao == "conversa":
        pedido.update(fala_jogador=fala_jogador, comando=True)
    t0 = time.perf_counter()
    r = servico.fala(pedido)
    lat = time.perf_counter() - t0
    voz, verif = chamadas["voz"][iv:], chamadas["verif"][jv:]
    if len(voz) != 1:
        raise RuntimeError(f"{rid}: {len(voz)} chamadas da voz")
    v = r["verificacao"]
    reg = {"id": rid, "braco": braco, "entrada": entrada["id"], "conjunto": entrada["conjunto"], "situacao": situacao, "semente": semente,
           "estagio": entrada["estagio"], "pedido_rede": entrada["pedido_rede"], "versao_dec": entrada["conceitos"]["versao"],
           "fala_jogador": fala_jogador, "historico": historico or [], "fala": r["fala"], "erro": r["erro"], "comando": r["comando"], "versao_prompt": r["versao_prompt"],
           "verificacao": v, "versao_verificador": None if v is None else v["versao"], "marcou": marcou(v),
           "usage": {"entrada": voz[0]["tokens_entrada"], "saida": voz[0]["tokens_saida"]}, "chamada_voz": voz[0], "chamadas_verif": verif,
           "latencia_voz_s": voz[0]["latencia_s"], "latencia_turno_s": lat}
    conferir_registro(reg)
    return reg


def tarefas_do_braco(entradas: dict, roteiros: list[dict]) -> list[tuple]:
    """(tipo, dados) na ordem da rodada: as espontaneas do E3, as do E2, as conversas (roteiro x sequencia)"""
    out = [("espontanea", e) for e in entradas["E3"] + entradas["E2"]]
    out += [("conversa", (r, s)) for r in roteiros for s in entradas["sequencias"]]
    return out


def rodar_braco(braco: str, servico: ServicoDC4, chamadas: dict, entradas: dict, roteiros: list[dict], gravar) -> list[dict]:
    base, regs = entradas["base"], []
    for tipo, dados in tarefas_do_braco(entradas, roteiros):
        if tipo == "espontanea":
            reg = falar(servico, chamadas, braco, f"{braco}/{dados['id']}", dados, "espontanea", semente_do_turno(base, dados["id"]))
            gravar(reg)
            regs.append(reg)
            continue
        roteiro, seq = dados
        historico = []
        for t, turno in enumerate(roteiro["turnos"]):
            e = seq["entradas"][t]
            item = f"{roteiro['id']}-{seq['id']}-t{t}"
            hist = [h for h in historico if h[2] == e["estagio"]][-MAX_TROCAS:]          # a fronteira da M2: so o estagio atual
            reg = falar(servico, chamadas, braco, f"{braco}/{item}", e, "conversa", semente_do_turno(base, item), turno["texto"], hist)
            reg.update(conversa=f"{roteiro['id']}-{seq['id']}", roteiro=roteiro["id"], sequencia=seq["id"], turno=t, papel=turno["papel"])
            historico.append([turno["texto"], reg["fala"], e["estagio"]])
            gravar(reg)
            regs.append(reg)
    return regs


def conferir_registros(regs: list[dict], entradas: dict, roteiros: list[dict], bracos) -> None:
    """o fim da rodada: cada braco com cada espontanea uma vez e cada turno de cada conversa uma vez, todos conferidos"""
    for b in bracos:
        meus = [r for r in regs if r["braco"] == b]
        esp = sorted(r["entrada"] for r in meus if r["situacao"] == "espontanea")
        if esp != sorted(e["id"] for e in entradas["E3"] + entradas["E2"]):
            raise RuntimeError(f"{b}: as espontaneas nao sao as entradas")
        conv = sorted((r["conversa"], r["turno"]) for r in meus if r["situacao"] == "conversa")
        if conv != sorted((f"{r['id']}-{s['id']}", t) for r in roteiros for s in entradas["sequencias"] for t in range(len(PAPEIS))):
            raise RuntimeError(f"{b}: os turnos das conversas nao sao os do plano")
        for r in meus:
            conferir_registro(r)


# ================================================================== os pares (4.5)
def sortear_pares(base: int, conversas: list[str]) -> list[dict]:
    """H x G e S x G em cada conversa (secao 4.5): o lado de cada braco e a ordem dos pares, pela rng do fluxo `pares`"""
    rng = en.rng_do_fluxo(base, "pares")
    pares = []
    for c in conversas:
        for outro in ("H", "S"):
            lados = [outro, "G"] if rng.random() < 0.5 else ["G", outro]
            pares.append({"conversa": c, "comparacao": f"{outro}xG", "esquerda": lados[0], "direita": lados[1]})
    rng.shuffle(pares)
    return [{"id": f"P{n:02d}", **p} for n, p in enumerate(pares)]


def conferir_pares(pares: list[dict], base: int, conversas: list[str]) -> None:
    if pares != sortear_pares(base, conversas):
        raise RuntimeError("a ordem dos pares nao e a sorteada (secao 9)")


# ================================================================== a rodada
def _json(caminho: Path, obj) -> None:
    caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def rodar(cfg: dict, roteiros: list[dict], pasta: Path, clientes: dict, exportar=en.exportar) -> dict:
    """as entradas, as falas dos tres bracos (um por vez), os pares, o material da marcacao e o meta. Grava cada fala no disco na hora."""
    if pasta.exists():
        raise RuntimeError(f"a pasta {pasta} ja existe: nada se grava por cima")
    pasta.mkdir(parents=True)
    base = cfg["unidades"]["bases"][0]
    gasto = clientes["gasto"]
    gasto_inicio = gasto.gasto
    tags = {"falso": True} if clientes["falso"] else tag_ollama(clientes["verif"])
    entradas = exportar(base, cfg["dias"], cfg["orcamento_por_dia"], cfg["n_e3_por_pedido"], cfg["n_e2"], cfg["min_ep_e2"], cfg["n_sequencias"])
    _json(pasta / "entradas.json", entradas)
    arq = (pasta / "falas.jsonl").open("w", encoding="utf-8", newline="\n")
    chamadas = {"voz": [], "verif": []}
    verif = ClienteRegistrado(clientes["verif"], "verif", chamadas["verif"])
    regs, parada = [], None
    meta = {"fase": cfg["fase"], "base": base, "plano": PLANO, "plano_sha256": sha_arquivo(RAIZ / PLANO), "arquivos": sha_dos_arquivos(),
            "clientes_falsos": clientes["falso"], "ollama": tags, "python": platform.python_version()}

    def gravar(reg: dict) -> None:
        arq.write(json.dumps(reg, ensure_ascii=False, sort_keys=True) + "\n")
        arq.flush()

    try:
        for b in cfg["bracos"]:
            voz = ClienteRegistrado(clientes["voz"][b], f"voz/{b}", chamadas["voz"])
            if voz.modelo != BRACOS[b][1]:
                raise ModeloTrocado(f"o braco {b} com o cliente de {voz.modelo!r}")
            regs += rodar_braco(b, ServicoDC4(voz, verif), chamadas, entradas, roteiros, gravar)
    except ParadaNoTeto as err:
        parada = str(err)
    finally:
        arq.close()
        meta["gasto"] = {"limite_usd": gasto.limite, "inicio_usd": round(gasto_inicio, 6), "fim_usd": round(gasto.gasto, 6),
                         "da_rodada_usd": round(gasto.gasto - gasto_inicio, 6),
                         "pelo_usage_usd": {b: round(sum(custo_usd(BRACOS[b][1], r["usage"]["entrada"], r["usage"]["saida"]) for r in regs
                                                         if r["braco"] == b and r["usage"]["entrada"] is not None), 6)
                                            for b in cfg["bracos"] if BRACOS[b][0] == "claude"}}
        meta["parada_no_teto"] = parada
        meta["modelos_devolvidos"] = {b: sorted({c["modelo_devolvido"] for c in chamadas["voz"] if c["papel"] == f"voz/{b}" and c["modelo_devolvido"]})
                                      for b in cfg["bracos"]}
        meta["verificador_devolvido"] = sorted({c["modelo_devolvido"] for c in chamadas["verif"] if c["modelo_devolvido"]})
        meta["falas"] = len(regs)
        _json(pasta / "meta.json", meta)
    if parada is not None:
        raise ParadaNoTeto(parada + f" (a rodada parou com {len(regs)} falas no disco)")
    if gasto.gasto > gasto.limite:
        raise RuntimeError(f"o gasto passou do teto: US$ {gasto.gasto} > {gasto.limite}")
    conferir_registros(regs, entradas, roteiros, cfg["bracos"])
    conversas = [f"{r['id']}-{s['id']}" for r in roteiros for s in entradas["sequencias"]]
    pares = sortear_pares(base, conversas)
    conferir_pares(pares, base, conversas)
    _json(pasta / "pares.json", pares)
    mc.montar(pasta / "marcacao", base, entradas, regs, pares)
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="a avaliacao da voz da rede, DC4 (docs/PLANO_ANALISE_V3_CONVERSA_DC4.md)")
    ap.add_argument("--config")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--falso", action="store_true", help="os clientes sem rede (so na fumaca)")
    ap.add_argument("--saida", help="outra pasta de saida (so na fumaca)")
    ap.add_argument("--registro", action="store_true", help="imprime o texto da secao 13 do plano (o registro da rodada) e sai")
    a = ap.parse_args(argv)
    if a.registro:
        print(texto_do_registro(), end="")
        return 0
    if a.config is None:
        ap.error("--config e obrigatorio")
    if a.processos != 1:
        raise ValueError("a DC4 roda num processo so (as chamadas sao uma por vez; secao 8)")
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)                 # o H10 (D-IA-6) e a V3-D8, antes de tudo
    cfg = json.loads((RAIZ / a.config).read_text(encoding="utf-8"))
    conferir_config(cfg)
    plano = _plano()
    exigir_plano_aprovado(plano)
    exigir_faixa(cfg["fase"])
    fumaca = cfg["fase"] == "fumaca"
    if a.falso != fumaca:
        raise RuntimeError("os clientes falsos sao so da fumaca, e a fumaca so roda com eles (a DC4a nao chama modelo)")
    if a.saida is not None and not fumaca:
        raise RuntimeError("a pasta de saida da calibracao e da validacao e a da config")
    if cfg["fase"] == "validacao":
        exigir_registro(plano)
    roteiros = carregar_roteiros(cfg)
    pasta = RAIZ / (a.saida or cfg["saida"])
    clientes = clientes_falsos() if fumaca else clientes_reais(cfg)
    meta = rodar(cfg, roteiros, pasta, clientes)
    print(json.dumps({k: meta[k] for k in ("fase", "base", "falas", "gasto", "parada_no_teto", "modelos_devolvidos")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
