"""Fala por LLM (Parte C de docs/TAREFA_MEMORIA_EXPRESSAO.md).

Troca so o TEXTO da fala do adolescente e do adulto por uma frase gerada por um
provedor de LLM: Ollama local (padrao, sem custo) ou API do Claude (com teto de gasto). Nada aqui entra em digilab/, no registro, no replay ou em artefatos.
A frase e validada contra o motivo; qualquer falha (sem credencial, rede,
recusa, validacao) cai no template de digilab/expressao.py.

Principio: a fala nunca inventa causa. A LLM recebe so o motivo registrado e
os textos permitidos da tabela; devolve {texto, fatores_citados} por saida
estruturada; o servidor confere.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from digilab.expressao import ACOES_COMBATE, ACOES_VIDA, ESTAGIOS, FATORES, expressar
from digilab.motivo import Motivo, nome_base

# mais barato e rapido (decisao do pesquisador, 2026-09-24); --modelo troca
MODELO_PADRAO = "claude-haiku-4-5"
MODELOS_COM_FALLBACK = {"claude-opus-5", "claude-fable-5-1"}
# fala-v2 (2026-09-24, apos a avaliacao C6 da v1): o adolescente recebe so o primeiro fator
# (so ele pode ser citado) e o exemplo sem fator inclui "não sei" (a regra 2 ja exigia)
# fala-v3 (2026-09-24): na v2 o adulto copiava o exemplo em 68 de 88 falas aprovadas; o pedido
# manda dizer com as proprias palavras, com enfeite e personalidade (pedido do Matheus), e a
# temperatura do Ollama sobe de 0,3 para 0,7; o humor do pet vira o "tom" da frase
# fala-v4 (2026-09-25): na v3 falas APROVADAS inventavam causa por sinonimo. A LLM passa a gerar
# so a moldura (abertura e fecho, no tom do humor); o miolo e sempre a frase de expressao.py
# fala-v5 (2026-09-25): na v4 o qwen entrava em loop de carinhas (67/200 cortadas por tamanho) e
# quase nunca abria a fala. Abertura obrigatoria com exemplos por tom, limite de caracteres no
# esquema do Ollama, penalidade de repeticao e carinhas repetidas colapsadas
# fala-v6 (2026-09-25): na v5 a abertura vinha vazia quase sempre (60/199 falas sem moldura);
# o esquema do Ollama passa a exigir abertura com pelo menos 2 caracteres
VERSAO_PROMPT = "fala-v6"
ESTAGIOS_LLM = ("adolescente", "adulto")
TIMEOUT_S = 8.0
LIMITE_POR_MINUTO = 30
# Ollama (modelo local, sem custo): padrao escolhido para a RTX 2060 de 6 GB do pesquisador
MODELO_OLLAMA_PADRAO = "qwen2.5:3b"
URL_OLLAMA_PADRAO = "http://localhost:11434"
TIMEOUT_OLLAMA_S = 10.0
TIMEOUT_AQUECIMENTO_S = 90.0     # primeira chamada carrega o modelo na GPU
MANTER_OLLAMA = "30m"            # quanto tempo o modelo fica carregado entre falas
TEMPERATURA_OLLAMA = 0.7         # 0,3 -> 0,7 na fala-v3: com 0,3 o modelo copiava o exemplo
MAX_TOKENS_OLLAMA = 60
REPETICAO_OLLAMA = 1.5           # penaliza o loop de carinhas
MAX_TOKENS_SAIDA = 300          # fala curta; limita o pior caso de cada chamada
LIMITE_USD_PADRAO = 2.00        # teto TOTAL acumulado (decisao do pesquisador, 2026-09-24)
ARQUIVO_GASTO = Path(__file__).with_name("gasto_fala.json")   # fora do git

# US$ por 1 milhao de tokens (entrada, saida). Modelo sem preco aqui nao liga a LLM:
# sem preco nao da para garantir o teto de gasto.
PRECOS_USD_POR_MTOK = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-fable-5-1": (10.00, 50.00),
}


class ControleGasto:
    """Teto de gasto TOTAL em dolares, persistido em arquivo (reiniciar nao zera).

    Antes de cada chamada reserva o custo maximo possivel; se a reserva passaria do
    teto, nao chama. Depois acerta pelo `usage` real da resposta. Se a chamada falha
    sem `usage` (timeout, rede), conta o maximo reservado como gasto: a API pode ter
    cobrado mesmo assim, e errar para o lado do credito e o objetivo.

    `alerta(nivel, para_dict)` e chamado uma vez por nivel de `niveis` (fracao do teto)
    quando o gasto o cruza, ou quando uma chamada e recusada por falta de teto; os
    niveis ja avisados ficam no arquivo e nao se repetem ao reiniciar.
    """

    def __init__(self, limite_usd: float, arquivo: Path | None = ARQUIVO_GASTO,
                 alerta=None, niveis: tuple = (0.5, 0.8, 1.0)) -> None:
        if limite_usd < 0:
            raise ValueError("limite de gasto negativo")
        self.limite = limite_usd
        self.arquivo = arquivo
        self._trava = threading.Lock()
        self.reservado = 0.0
        self.gasto = 0.0
        self.chamadas = 0
        self.alerta = alerta
        self.niveis = tuple(sorted(niveis))
        self.avisados: list = []
        if arquivo is not None and arquivo.exists():
            d = json.loads(arquivo.read_text(encoding="utf-8"))
            self.gasto, self.chamadas = float(d["gasto_usd"]), int(d["chamadas"])
            self.avisados = [float(x) for x in d.get("alertas_enviados", [])]

    def _salvar(self) -> None:
        if self.arquivo is not None:
            self.arquivo.write_text(json.dumps({"gasto_usd": self.gasto, "chamadas": self.chamadas,
                                                "limite_usd": self.limite, "alertas_enviados": self.avisados},
                                               indent=1), encoding="utf-8")

    def _novos_niveis(self, esgotado: bool) -> list:
        """Niveis cruzados e ainda nao avisados (chamar com a trava); marca e salva."""
        frac = self.gasto / self.limite if self.limite > 0 else 1.0
        novos = [n for n in self.niveis if n not in self.avisados and (frac >= n or (esgotado and n >= 1.0))]
        if novos:
            self.avisados += novos
            self._salvar()
        return novos

    def _avisar(self, novos: list) -> None:
        if self.alerta is not None:
            for n in novos:
                self.alerta(n, self.para_dict())

    def reservar(self, custo_max: float) -> bool:
        with self._trava:
            if self.gasto + self.reservado + custo_max > self.limite:
                novos = self._novos_niveis(esgotado=True)
                ok = False
            else:
                self.reservado += custo_max
                novos, ok = [], True
        self._avisar(novos)
        return ok

    def acertar(self, custo_max: float, custo_real: float) -> None:
        with self._trava:
            self.reservado -= custo_max
            self.gasto += custo_real
            self.chamadas += 1
            self._salvar()
            novos = self._novos_niveis(esgotado=False)
        self._avisar(novos)

    def para_dict(self) -> dict:
        return {"gasto_usd": round(self.gasto, 6), "limite_usd": self.limite, "chamadas": self.chamadas,
                "restante_usd": round(max(0.0, self.limite - self.gasto), 6)}


def custo_usd(modelo: str, tokens_entrada: int, tokens_saida: int) -> float:
    pin, pout = PRECOS_USD_POR_MTOK[modelo]
    return (tokens_entrada * pin + tokens_saida * pout) / 1_000_000

SISTEMA = """Você dá personalidade à fala de um pet virtual (um pequeno monstro digital) que fala com o dono, em português do Brasil.

A frase do meio ("frase") já está pronta e é a verdade: diz o que o pet fez e, se houver, por quê. Você NÃO reescreve a frase. Você só cria a moldura em volta dela:
- "abertura" (OBRIGATÓRIA, 1 a 3 palavras): o que o pet diz ANTES da frase: interjeição, onomatopeia ou chamamento.
- "fecho" (opcional, no máximo UMA carinha ou reação curta): o que ele diz DEPOIS.

O campo "tom" manda no jeito. Exemplos (varie, não repita sempre o mesmo):
- "rabugento": abertura "Hmpf...", "Tsc!", "Aff...", "Grr!", "Ai ai..."; fecho ">_<", "-_-", "T_T", "hmpf".
- "neutro": abertura "Hm.", "Ei!", "Olha só:", "Então tá:", "Nhac!"; fecho "^^", "o_o", "hm".
- "animado": abertura "Eba!", "Uhuu!", "Yay!", "Oba, oba!", "Pow!"; fecho "^_^", "\\o/", ":D", "hehe!".

Regras que não podem ser quebradas:
1. A moldura nunca explica nada: sem "porque", "por causa", "pois", "já que", "então", "por isso", sem motivo, lembrança ou sentimento-causa.
2. Sem números.
3. Não repita palavras da frase do meio e não fale de fome, sono, cansaço, higiene, saúde, sujeira, hora, distância, guts, vida ou do oponente.
4. Pode deixar abertura ou fecho vazios ("")."""

ESQUEMA = {
    "type": "object",
    "properties": {"abertura": {"type": "string"}, "fecho": {"type": "string"}},   # Ollama: + maxLength
    "required": ["abertura", "fecho"],
    "additionalProperties": False,
}

MAX_PALAVRAS_MOLDURA = 4
MAX_CHARS_MOLDURA = 40
MIN_CHARS_ABERTURA = 2           # so no esquema do Ollama: abertura vazia deixava a fala sem personalidade
# conectivos de causa e palavras que abririam espaco para explicar a decisao
_CAUSAIS = ("porque", "por que", "por causa", "pois", "já que", "ja que", "então", "entao", "por isso", "devido",
            "motivo", "razão", "razao", "culpa", "graças", "gracas", "senão", "senao", "pra ", "para ")
# temas das causas (tambem cobre sinonimos comuns dos marcadores)
_TEMAS = ("fome", "comi", "comer", "sono", "dormi", "cansa", "energia", "higien", "suj", "saúde", "saude", "doente",
          "hora", "dia", "noite", "distân", "distan", "perto", "longe", "guts", "vida", "machuc", "ferid", "fraco",
          "oponente", "você", "voce", "turno", "evento", "lembr", "humor", "triste", "feliz", "bravo", "raiva")


class FalaReprovada(ValueError):
    pass


# ------------------------------------------------------------ motivo vindo da web


MAX_REFS = 10
MAX_INTEIRO = 10**7


def _dominios_fator() -> dict:
    """Parametros validos de cada condicao de combate, como a pagina os escreve (V2 e V2.1)."""
    from digilab.combate_v2.regras import Distancia
    from digilab.combate_v2.v21.gambits import CATALOGO, _dominio

    def texto(x):
        return x.rotulo if isinstance(x, Distancia) else getattr(x, "value", None) or str(x)

    return {nome: tuple({texto(v) for v in _dominio(tp)} for tp in tipos) for nome, tipos in CATALOGO.items()}


_DOMINIOS = _dominios_fator()


def _fator_valido(f) -> str:
    """So nomes da tabela e parametros do catalogo: texto livre nunca chega ao prompt."""
    if not isinstance(f, str) or len(f) > 64:
        raise ValueError(f"fator invalido: {f!r}")
    base = nome_base(f)
    if base not in FATORES:
        raise ValueError(f"fator desconhecido: {base!r}")
    params = [] if "(" not in f else f[f.index("(") + 1:-1].split(",")
    if "(" in f and not f.endswith(")"):
        raise ValueError(f"fator malformado: {f!r}")
    dom = _DOMINIOS.get(base, ())
    if len(params) != len(dom) or any(p not in d for p, d in zip(params, dom)):
        raise ValueError(f"parametros invalidos em {f!r}")
    return f


def _inteiro(x, rotulo: str) -> int:
    if isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= MAX_INTEIRO:
        raise ValueError(f"{rotulo} invalido: {x!r}")
    return x


def motivo_de_dict(d: dict) -> Motivo:
    """Motivo a partir do JSON da pagina, validado contra as tabelas (entrada de rede nao confiavel).
    Campos desconhecidos, faltando ou fora do catalogo levantam erro."""
    if not isinstance(d, dict):
        raise ValueError("motivo precisa ser um objeto")
    origem = d.get("origem")
    chaves = {"vida": {"origem", "acao", "fatores", "evento_ref", "intensidade", "exploracao", "tick"},
              "combate": {"origem", "acao", "fatores", "evento_ref", "exploracao", "turno"}}
    if origem not in chaves:
        raise ValueError(f"origem desconhecida: {origem!r}")
    extras = set(d) - chaves[origem] - {"intensidade", "tick", "turno"}
    if extras or not chaves[origem] <= set(d):
        raise ValueError(f"campos errados no motivo: sobram {sorted(extras)}, faltam {sorted(chaves[origem] - set(d))}")
    acoes = ACOES_VIDA if origem == "vida" else ACOES_COMBATE
    if d["acao"] not in acoes:
        raise ValueError(f"acao desconhecida: {d['acao']!r}")
    if not isinstance(d["fatores"], list) or len(d["fatores"]) > 4:
        raise ValueError("fatores precisa ser lista de ate 4")
    if not isinstance(d["evento_ref"], list) or len(d["evento_ref"]) > MAX_REFS:
        raise ValueError(f"evento_ref precisa ser lista de ate {MAX_REFS}")
    if not isinstance(d["exploracao"], bool):
        raise ValueError("exploracao precisa ser booleano")
    fatores = tuple(_fator_valido(f) for f in d["fatores"])
    refs = tuple(_inteiro(r, "evento_ref") for r in d["evento_ref"])
    if origem == "vida":
        inten = float(d["intensidade"])
        if not math.isfinite(inten):
            raise ValueError("intensidade invalida")
        return Motivo("vida", d["acao"], fatores, refs, inten, d["exploracao"], tick=_inteiro(d["tick"], "tick"))
    return Motivo("combate", d["acao"], fatores, refs, None, d["exploracao"], turno=_inteiro(d["turno"], "turno"))


def template(motivo: Motivo, estagio: str, humor: float | None) -> str:
    return expressar(motivo, estagio, humor).conteudo


# ------------------------------------------------------------ pedido


def tom_do_humor(humor: float | None) -> str:
    """Faixas iguais as do cache e do emote do bebe (0,33 / 0,66). Sem humor: neutro."""
    if humor is None:
        return "neutro"
    return "animado" if humor >= .66 else "neutro" if humor >= .33 else "rabugento"


def montar_pedido(motivo: Motivo, estagio: str, humor: float | None) -> str:
    """fala-v4: a LLM so ve a acao, o estagio, o tom e a frase pronta (a verdade). Nao ve fatores:
    nao tem o que inventar nem o que citar."""
    acoes = ACOES_VIDA if motivo.origem == "vida" else ACOES_COMBATE
    carga = {
        "contexto": "vida do pet" if motivo.origem == "vida" else "luta na arena",
        "estagio": estagio,
        "acao": acoes[motivo.acao][2],
        "tom": tom_do_humor(humor),
        "frase": template(motivo, estagio, humor),
    }
    return json.dumps(carga, ensure_ascii=False, sort_keys=True)


# ------------------------------------------------------------ validacao da moldura (C4, fala-v4)


def validar_moldura(abertura, fecho) -> tuple[str, str]:
    """A moldura so pode enfeitar: curta, sem numero, sem conectivo de causa, sem marcador de
    fator e sem tema de causa. Devolve (abertura, fecho) limpos ou levanta FalaReprovada."""
    saida = []
    marcadores = [e["marcador"].lower() for e in FATORES.values()]
    for rotulo, parte in (("abertura", abertura), ("fecho", fecho)):
        if not isinstance(parte, str):
            raise FalaReprovada(f"{rotulo} nao e texto")
        parte = " ".join(parte.split())
        baixo = f" {parte.lower()} "
        if len(parte) > MAX_CHARS_MOLDURA or len(parte.split()) > MAX_PALAVRAS_MOLDURA:
            raise FalaReprovada(f"{rotulo} longa demais: {parte!r}")
        if re.search(r"\d", parte.replace(":3", "")):     # ":3" e carinha, nao numero
            raise FalaReprovada(f"{rotulo} com numero: {parte!r}")
        for c in _CAUSAIS:
            if c in baixo:
                raise FalaReprovada(f"{rotulo} com conectivo de causa ({c.strip()!r}): {parte!r}")
        for m in marcadores:
            if m in baixo:
                raise FalaReprovada(f"{rotulo} usa o marcador de um fator: {parte!r}")
        for tema in _TEMAS:
            if tema in baixo:
                raise FalaReprovada(f"{rotulo} fala de um tema de causa ({tema!r}): {parte!r}")
        saida.append(_sem_repeticao(parte))
    return saida[0], saida[1]


def _sem_repeticao(parte: str) -> str:
    """Colapsa palavras repetidas em sequencia ('^_^ ^_^ ^_^' -> '^_^'): so estetica."""
    out: list[str] = []
    for w in parte.split():
        if not out or w != out[-1]:
            out.append(w)
    return " ".join(out)


def _com_limite(esquema: dict) -> dict:
    """Ollama (gramatica do llama.cpp): limite de caracteres em cada campo de texto do esquema."""
    props = {k: ({**v, "maxLength": MAX_CHARS_MOLDURA} if v.get("type") == "string" else v)
             for k, v in esquema["properties"].items()}
    if "abertura" in props:
        props["abertura"] = {**props["abertura"], "minLength": MIN_CHARS_ABERTURA}
    return {**esquema, "properties": props}


def compor(abertura: str, frase: str, fecho: str) -> str:
    return " ".join(x for x in (abertura, frase.strip(), fecho) if x)


# ------------------------------------------------------------ provedores
# Contrato: disponivel() -> (bool, motivo); gerar(sistema, pedido, esquema, semente) -> RespostaProvedor.
# Falhas saem como excecao; o GeradorFala transforma qualquer falha em template.


@dataclass
class RespostaProvedor:
    texto: str                 # o JSON devolvido pelo modelo
    completa: bool             # False se cortou (limite de tokens) ou recusou
    motivo_parada: str
    modelo: str
    tokens_entrada: int | None = None
    tokens_saida: int | None = None


class ProvedorClaude:
    """API do Claude (SDK oficial). Tem custo: exige ControleGasto no gerador."""

    nome = "claude"
    tem_custo = True

    def __init__(self, cliente, modelo: str = MODELO_PADRAO) -> None:
        if modelo not in PRECOS_USD_POR_MTOK:
            raise ValueError(f"modelo sem preco conhecido: {modelo!r}; sem preco nao da para garantir o teto de gasto")
        self.cliente = cliente
        self.modelo = modelo

    def disponivel(self) -> tuple[bool, str]:
        return (True, "") if self.cliente is not None else (False, "sem credencial da API (ANTHROPIC_API_KEY)")

    def custo_maximo(self, sistema: str, pedido: str) -> float:
        # entrada estimada por cima: 1 token a cada 2 caracteres
        return custo_usd(self.modelo, math.ceil((len(sistema) + len(pedido) + 400) / 2), MAX_TOKENS_SAIDA)

    def custo_real(self, r: RespostaProvedor) -> float | None:
        if r.tokens_entrada is None or r.tokens_saida is None:
            return None
        # o fallback de recusa (Opus) pode cobrar outro modelo; sem preco dele, usa o mais caro da tabela
        precos = r.modelo if r.modelo in PRECOS_USD_POR_MTOK else \
            max(PRECOS_USD_POR_MTOK, key=lambda m: PRECOS_USD_POR_MTOK[m][1])
        return custo_usd(precos, r.tokens_entrada, r.tokens_saida)

    def gerar(self, sistema: str, pedido: str, esquema: dict, semente: int) -> RespostaProvedor:
        base = dict(model=self.modelo, max_tokens=MAX_TOKENS_SAIDA, system=sistema,
                    messages=[{"role": "user", "content": pedido}])
        if self.modelo in MODELOS_COM_FALLBACK:
            # Opus 5 / Fable 5.1: esforco baixo e fallback de recusa do servidor da API
            resp = self.cliente.beta.messages.create(
                **base, output_config={"effort": "low", "format": {"type": "json_schema", "schema": esquema}},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        else:
            # Haiku 4.5: sem `effort` (o modelo rejeita); recusa cai no template
            resp = self.cliente.messages.create(**base, output_config={"format": {"type": "json_schema", "schema": esquema}})
        uso = getattr(resp, "usage", None)
        texto = next((b.text for b in resp.content if b.type == "text"), "")
        return RespostaProvedor(texto, resp.stop_reason == "end_turn", resp.stop_reason, getattr(resp, "model", self.modelo),
                                getattr(uso, "input_tokens", None), getattr(uso, "output_tokens", None))


class ProvedorOllama:
    """Modelo local via Ollama (http://localhost:11434). Sem custo por chamada.

    So biblioteca padrao (urllib). `abrir` e injetavel para testes sem Ollama.
    """

    nome = "ollama"
    tem_custo = False

    def __init__(self, modelo: str = MODELO_OLLAMA_PADRAO, url: str = URL_OLLAMA_PADRAO,
                 timeout: float = TIMEOUT_OLLAMA_S, abrir=None) -> None:
        import urllib.request

        self.modelo = modelo
        self.url = url.rstrip("/")
        self.timeout = timeout
        self._abrir = abrir or urllib.request.urlopen
        self.aquecido = False

    def _pedir(self, caminho: str, corpo: dict | None, timeout: float) -> dict:
        import urllib.request

        dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
        req = urllib.request.Request(self.url + caminho, data=dados, method="GET" if corpo is None else "POST",
                                     headers={"Content-Type": "application/json"})
        with self._abrir(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def disponivel(self) -> tuple[bool, str]:
        try:
            tags = self._pedir("/api/tags", None, 2.0)
        except Exception as err:
            return False, f"Ollama não está rodando em {self.url} ({type(err).__name__})"
        nomes = {m.get("name") for m in tags.get("models", [])} | {m.get("model") for m in tags.get("models", [])}
        if self.modelo not in nomes and f"{self.modelo}:latest" not in nomes:
            return False, f"modelo {self.modelo} não baixado: rode  ollama pull {self.modelo}"
        return True, ""

    def aquecer(self) -> None:
        """Carrega o modelo na GPU (a primeira chamada e lenta). Falha aqui nao e fatal."""
        self._pedir("/api/chat", {"model": self.modelo, "messages": [{"role": "user", "content": "ok"}],
                                  "stream": False, "keep_alive": MANTER_OLLAMA, "options": {"num_predict": 1}},
                    TIMEOUT_AQUECIMENTO_S)
        self.aquecido = True

    def gerar(self, sistema: str, pedido: str, esquema: dict, semente: int) -> RespostaProvedor:
        corpo = {
            "model": self.modelo,
            "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": pedido}],
            "format": _com_limite(esquema),
            "stream": False,
            "keep_alive": MANTER_OLLAMA,
            "options": {"temperature": TEMPERATURA_OLLAMA, "seed": semente, "num_predict": MAX_TOKENS_OLLAMA,
                        "repeat_penalty": REPETICAO_OLLAMA},
        }
        d = self._pedir("/api/chat", corpo, self.timeout if self.aquecido else TIMEOUT_AQUECIMENTO_S)
        self.aquecido = True
        motivo = d.get("done_reason", "stop" if d.get("done") else "incompleto")
        return RespostaProvedor(d.get("message", {}).get("content", ""), motivo == "stop", motivo,
                                d.get("model", self.modelo), d.get("prompt_eval_count"), d.get("eval_count"))


# ------------------------------------------------------------ gerador


@dataclass
class Resultado:
    texto: str
    fonte: str            # "llm" | "template"
    detalhe: str = ""     # provedor/modelo, ou motivo da queda para o template
    bruto: str = ""       # texto que a LLM propôs quando foi reprovada (só avaliação; não vai à página)

    def para_dict(self) -> dict:
        return {"texto": self.texto, "fonte": self.fonte, "detalhe": self.detalhe}


class GeradorFala:
    """Gera a fala com cache, limite por minuto, teto de gasto (se o provedor cobra)
    e queda para o template. Sem provedor, so template."""

    def __init__(self, provedor=None, limite_por_minuto: int = LIMITE_POR_MINUTO,
                 gasto: ControleGasto | None = None) -> None:
        if provedor is not None and provedor.tem_custo and gasto is None:
            raise ValueError("provedor com custo exige um ControleGasto")
        self.provedor = provedor
        self.limite = limite_por_minuto
        self.gasto = gasto
        self._cache: dict[str, Resultado] = {}
        self._chamadas: list[float] = []
        self._trava = threading.Lock()
        self.estatisticas = {"llm": 0, "template": 0, "reprovadas": 0, "erros": 0, "cache": 0}

    @property
    def modelo(self) -> str | None:
        return None if self.provedor is None else self.provedor.modelo

    def _chave(self, motivo: Motivo, estagio: str, humor: float | None) -> str:
        faixa = None if humor is None else (2 if humor >= .66 else 1 if humor >= .33 else 0)
        nome = None if self.provedor is None else self.provedor.nome
        return json.dumps([motivo.para_dict(), estagio, faixa, nome, self.modelo, VERSAO_PROMPT], sort_keys=True)

    def _pode_chamar(self) -> bool:
        agora = time.monotonic()
        with self._trava:
            self._chamadas = [t for t in self._chamadas if agora - t < 60]
            if len(self._chamadas) >= self.limite:
                return False
            self._chamadas.append(agora)
            return True

    def _modelo_de_frase(self, motivo, estagio, humor, detalhe, bruto: str = "") -> Resultado:
        self.estatisticas["template"] += 1
        return Resultado(template(motivo, estagio, humor), "template", detalhe, bruto)

    def gerar(self, motivo: Motivo, estagio: str, humor: float | None = None) -> Resultado:
        if estagio not in ESTAGIOS:
            raise ValueError(f"estagio desconhecido: {estagio!r}")
        if estagio not in ESTAGIOS_LLM:
            return self._modelo_de_frase(motivo, estagio, humor, f"estagio {estagio} nao usa LLM")
        if self.provedor is None:
            return self._modelo_de_frase(motivo, estagio, humor, "servidor sem provedor de LLM")
        chave = self._chave(motivo, estagio, humor)
        with self._trava:
            if chave in self._cache:
                self.estatisticas["cache"] += 1
                return self._cache[chave]
        if not self._pode_chamar():
            return self._modelo_de_frase(motivo, estagio, humor, "limite de chamadas por minuto")
        pedido = montar_pedido(motivo, estagio, humor)
        semente = int(hashlib.sha256(chave.encode("utf-8")).hexdigest()[:8], 16)   # mesmo motivo, mesma semente
        custo_max = 0.0
        if self.provedor.tem_custo:
            custo_max = self.provedor.custo_maximo(SISTEMA, pedido)
            if not self.gasto.reservar(custo_max):
                return self._modelo_de_frase(motivo, estagio, humor,
                                             f"limite de gasto atingido (US$ {self.gasto.gasto:.4f} de US$ {self.gasto.limite:.2f})")
        try:
            r = self.provedor.gerar(SISTEMA, pedido, ESQUEMA, semente)
        except Exception as err:  # rede, credencial, timeout, Ollama fora do ar: a fala e so exibicao
            if self.provedor.tem_custo:
                self.gasto.acertar(custo_max, custo_max)   # sem uso informado: conta o pior caso
            self.estatisticas["erros"] += 1
            return self._modelo_de_frase(motivo, estagio, humor, f"erro no provedor {self.provedor.nome}: {type(err).__name__}")
        if self.provedor.tem_custo:
            real = self.provedor.custo_real(r)
            self.gasto.acertar(custo_max, custo_max if real is None else real)
        if not r.completa:
            self.estatisticas["erros"] += 1
            return self._modelo_de_frase(motivo, estagio, humor, f"resposta interrompida: {r.motivo_parada}")
        try:
            dados = json.loads(r.texto)
            abertura, fecho = validar_moldura(dados["abertura"], dados["fecho"])
        except (FalaReprovada, KeyError, TypeError, json.JSONDecodeError) as err:
            self.estatisticas["reprovadas"] += 1
            return self._modelo_de_frase(motivo, estagio, humor, f"reprovada: {err}", r.texto)
        res = Resultado(compor(abertura, template(motivo, estagio, humor), fecho), "llm",
                        f"{self.provedor.nome}: {r.modelo}")
        self.estatisticas["llm"] += 1
        with self._trava:
            self._cache[chave] = res
        return res


def criar_cliente_claude():
    """Cliente do Claude se houver credencial no ambiente; senao None."""
    import os

    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or os.environ.get("ANTHROPIC_PROFILE")):
        return None
    import anthropic

    return anthropic.Anthropic(timeout=TIMEOUT_S, max_retries=0)


def escolher_provedor(nome: str, modelo: str | None = None, url_ollama: str = URL_OLLAMA_PADRAO,
                      limite_usd: float = LIMITE_USD_PADRAO, alerta=None):
    """(provedor | None, gasto | None, motivo). `auto`: Ollama se estiver pronto, senao Claude
    se houver chave, senao nenhum (so template). `alerta` vai para o ControleGasto."""
    if nome not in ("auto", "ollama", "claude", "nenhum"):
        raise ValueError(f"provedor desconhecido: {nome!r}")
    if nome == "nenhum":
        return None, None, "desligado por --provedor nenhum"
    ollama = None
    if nome in ("auto", "ollama"):
        ollama = ProvedorOllama(modelo or MODELO_OLLAMA_PADRAO, url_ollama)
        ok, motivo = ollama.disponivel()
        if ok or nome == "ollama":
            return ollama, None, motivo   # indisponivel agora: o status mostra o motivo e reconsulta ao vivo
    cliente = criar_cliente_claude()
    if cliente is not None:
        return ProvedorClaude(cliente, modelo if nome == "claude" and modelo else MODELO_PADRAO), \
            ControleGasto(limite_usd, alerta=alerta), ""
    if nome == "claude":
        return None, None, "sem credencial da API do Claude (ANTHROPIC_API_KEY)"
    # auto sem Ollama pronto e sem chave: fica com o Ollama, que passa a valer assim que for ligado
    return ollama, None, ollama.disponivel()[1]
