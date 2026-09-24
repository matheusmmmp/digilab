"""Fala por LLM (Parte C de docs/TAREFA_MEMORIA_EXPRESSAO.md).

Troca so o TEXTO da fala do adolescente e do adulto por uma frase gerada pelo
Claude. Nada aqui entra em digilab/, no registro, no replay ou em artefatos.
A frase e validada contra o motivo; qualquer falha (sem credencial, rede,
recusa, validacao) cai no template de digilab/expressao.py.

Principio: a fala nunca inventa causa. A LLM recebe so o motivo registrado e
os textos permitidos da tabela; devolve {texto, fatores_citados} por saida
estruturada; o servidor confere.
"""

from __future__ import annotations

import json
import re
import threading
import time
from dataclasses import dataclass

from digilab.expressao import ACOES_COMBATE, ACOES_VIDA, ESTAGIOS, FATORES, _texto_fator, expressar
from digilab.motivo import Motivo, nome_base

# mais barato e rapido (decisao do pesquisador, 2026-09-24); --modelo troca
MODELO_PADRAO = "claude-haiku-4-5"
MODELOS_COM_FALLBACK = {"claude-opus-5", "claude-fable-5-1"}
VERSAO_PROMPT = "fala-v1"
ESTAGIOS_LLM = ("adolescente", "adulto")
TIMEOUT_S = 8.0
LIMITE_POR_MINUTO = 30

SISTEMA = """Você é a voz de um pet virtual (um pequeno monstro digital) falando com o dono, em português do Brasil, em primeira pessoa.

Você recebe o MOTIVO registrado de uma decisão que o pet já tomou e deve dizer essa decisão com naturalidade e personalidade.

Regras que não podem ser quebradas:
1. Só cite como causa os fatores listados em "fatores" do motivo, com o sentido dado em "significado_dos_fatores". Nunca acrescente outra causa, sentimento-causa, lembrança ou justificativa que não esteja ali.
2. Se "fatores" estiver vazio ou "exploracao" for verdadeiro, diga que não sabe o porquê (use as palavras "não sei") e não sugira nenhuma causa.
3. Estágio "adolescente": um fragmento curto de até 6 palavras, citando no máximo o primeiro fator. Estágio "adulto": uma frase, citando no máximo dois fatores.
4. Só mencione números de evento ou turno que estejam em "evento_ref"; não invente outros números.
5. Em "fatores_citados", liste exatamente os nomes (como aparecem em "fatores") dos fatores que sua frase menciona.

O "exemplo" mostra uma forma válida de dizer o mesmo motivo; você pode variar o jeito, não o conteúdo."""

ESQUEMA = {
    "type": "object",
    "properties": {
        "texto": {"type": "string"},
        "fatores_citados": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["texto", "fatores_citados"],
    "additionalProperties": False,
}


class FalaReprovada(ValueError):
    pass


# ------------------------------------------------------------ motivo vindo da web


def motivo_de_dict(d: dict) -> Motivo:
    """Motivo a partir do JSON da pagina. Campos desconhecidos ou faltando levantam erro."""
    origem = d["origem"]
    if origem == "vida":
        return Motivo("vida", d["acao"], tuple(d["fatores"]), tuple(int(r) for r in d["evento_ref"]),
                      float(d["intensidade"]), bool(d["exploracao"]), tick=int(d["tick"]))
    if origem == "combate":
        return Motivo("combate", d["acao"], tuple(d["fatores"]), tuple(int(r) for r in d["evento_ref"]),
                      None, bool(d["exploracao"]), turno=int(d["turno"]))
    raise ValueError(f"origem desconhecida: {origem!r}")


def template(motivo: Motivo, estagio: str, humor: float | None) -> str:
    return expressar(motivo, estagio, humor).conteudo


# ------------------------------------------------------------ pedido


def _significado(fator: str) -> str:
    """Texto permitido do fator: a frase do adulto da tabela da A3, com os parametros preenchidos."""
    return _texto_fator(fator, "adulto")


def montar_pedido(motivo: Motivo, estagio: str, humor: float | None) -> str:
    acoes = ACOES_VIDA if motivo.origem == "vida" else ACOES_COMBATE
    carga = {
        "contexto": "vida do pet" if motivo.origem == "vida" else "luta na arena",
        "estagio": estagio,
        "acao": acoes[motivo.acao][2],
        "fatores": list(motivo.fatores) if not motivo.exploracao else [],
        "significado_dos_fatores": {f: _significado(f) for f in motivo.fatores} if not motivo.exploracao else {},
        "evento_ref": list(motivo.evento_ref),
        "tipo_de_referencia": "evento do registro" if motivo.origem == "vida" else "turno da luta",
        "exploracao": motivo.exploracao,
        "humor": None if humor is None else round(humor, 2),
        "exemplo": template(motivo, estagio, humor),
    }
    return json.dumps(carga, ensure_ascii=False, sort_keys=True)


# ------------------------------------------------------------ validacao (C4)

_NUM = re.compile(r"\d+")


def validar(texto: str, citados: list[str], motivo: Motivo, estagio: str) -> None:
    fatores = [] if motivo.exploracao else list(motivo.fatores)
    if not texto.strip():
        raise FalaReprovada("texto vazio")
    if not set(citados) <= set(fatores):
        raise FalaReprovada(f"cita fatores fora do motivo: {sorted(set(citados) - set(fatores))}")
    limite = 1 if estagio == "adolescente" else 2
    if len(set(citados)) > limite:
        raise FalaReprovada(f"cita {len(set(citados))} fatores; o estagio {estagio} permite {limite}")
    if estagio == "adolescente" and fatores and set(citados) - {fatores[0]}:
        raise FalaReprovada("adolescente so pode citar o primeiro fator")
    baixo = texto.lower()
    presentes = {nome_base(f) for f in fatores}
    for nome, e in FATORES.items():
        if nome not in presentes and e["marcador"].lower() in baixo:
            raise FalaReprovada(f"texto usa o marcador de um fator ausente: {nome}")
    if not fatores and "não sei" not in baixo:
        raise FalaReprovada("motivo sem fator precisa dizer que nao sabe o porque")
    permitidos = {str(r) for r in motivo.evento_ref}
    for f in fatores:
        permitidos |= set(_NUM.findall(_significado(f)))
    estranhos = set(_NUM.findall(texto)) - permitidos
    if estranhos:
        raise FalaReprovada(f"numeros fora do evento_ref/fatores: {sorted(estranhos)}")


# ------------------------------------------------------------ gerador


@dataclass
class Resultado:
    texto: str
    fonte: str            # "llm" | "template"
    detalhe: str = ""     # modelo ou motivo da queda para o template

    def para_dict(self) -> dict:
        return {"texto": self.texto, "fonte": self.fonte, "detalhe": self.detalhe}


class GeradorFala:
    """Gera a fala com cache, limite por minuto e queda para o template.

    `cliente` e um anthropic.Anthropic (ou um falso nos testes). Sem cliente, so template.
    """

    def __init__(self, cliente=None, modelo: str = MODELO_PADRAO, limite_por_minuto: int = LIMITE_POR_MINUTO) -> None:
        self.cliente = cliente
        self.modelo = modelo
        self.limite = limite_por_minuto
        self._cache: dict[str, Resultado] = {}
        self._chamadas: list[float] = []
        self._trava = threading.Lock()
        self.estatisticas = {"llm": 0, "template": 0, "reprovadas": 0, "erros": 0, "cache": 0}

    def _chave(self, motivo: Motivo, estagio: str, humor: float | None) -> str:
        faixa = None if humor is None else (2 if humor >= .66 else 1 if humor >= .33 else 0)
        return json.dumps([motivo.para_dict(), estagio, faixa, self.modelo, VERSAO_PROMPT], sort_keys=True)

    def _pode_chamar(self) -> bool:
        agora = time.monotonic()
        with self._trava:
            self._chamadas = [t for t in self._chamadas if agora - t < 60]
            if len(self._chamadas) >= self.limite:
                return False
            self._chamadas.append(agora)
            return True

    def _modelo_de_frase(self, motivo, estagio, humor, detalhe) -> Resultado:
        self.estatisticas["template"] += 1
        return Resultado(template(motivo, estagio, humor), "template", detalhe)

    def gerar(self, motivo: Motivo, estagio: str, humor: float | None = None) -> Resultado:
        if estagio not in ESTAGIOS:
            raise ValueError(f"estagio desconhecido: {estagio!r}")
        if estagio not in ESTAGIOS_LLM:
            return self._modelo_de_frase(motivo, estagio, humor, f"estagio {estagio} nao usa LLM")
        if self.cliente is None:
            return self._modelo_de_frase(motivo, estagio, humor, "servidor sem credencial da API")
        chave = self._chave(motivo, estagio, humor)
        with self._trava:
            if chave in self._cache:
                self.estatisticas["cache"] += 1
                return self._cache[chave]
        if not self._pode_chamar():
            return self._modelo_de_frase(motivo, estagio, humor, "limite de chamadas por minuto")
        try:
            pedido = dict(
                model=self.modelo,
                max_tokens=1024,
                system=SISTEMA,
                messages=[{"role": "user", "content": montar_pedido(motivo, estagio, humor)}],
            )
            if self.modelo in MODELOS_COM_FALLBACK:
                # Opus 5 / Fable 5.1: esforco baixo e fallback de recusa do servidor da API
                resposta = self.cliente.beta.messages.create(
                    **pedido,
                    output_config={"effort": "low", "format": {"type": "json_schema", "schema": ESQUEMA}},
                    betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default",
                )
            else:
                # Haiku 4.5 (padrao): sem `effort` (o modelo rejeita); recusa cai no template
                resposta = self.cliente.messages.create(
                    **pedido,
                    output_config={"format": {"type": "json_schema", "schema": ESQUEMA}},
                )
        except Exception as err:  # rede, credencial, limite: a fala e so exibicao, cai no template
            self.estatisticas["erros"] += 1
            return self._modelo_de_frase(motivo, estagio, humor, f"erro na API: {type(err).__name__}")
        if resposta.stop_reason != "end_turn":
            self.estatisticas["erros"] += 1
            return self._modelo_de_frase(motivo, estagio, humor, f"resposta interrompida: {resposta.stop_reason}")
        try:
            texto_json = next(b.text for b in resposta.content if b.type == "text")
            dados = json.loads(texto_json)
            validar(dados["texto"], dados["fatores_citados"], motivo, estagio)
        except (FalaReprovada, KeyError, StopIteration, json.JSONDecodeError) as err:
            self.estatisticas["reprovadas"] += 1
            return self._modelo_de_frase(motivo, estagio, humor, f"reprovada: {err}")
        r = Resultado(dados["texto"].strip(), "llm", getattr(resposta, "model", self.modelo))
        self.estatisticas["llm"] += 1
        with self._trava:
            self._cache[chave] = r
        return r


def criar_cliente():
    """Cliente do Claude se houver credencial no ambiente; senao None (so template)."""
    import os

    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or os.environ.get("ANTHROPIC_PROFILE")):
        return None
    import anthropic

    return anthropic.Anthropic(timeout=TIMEOUT_S, max_retries=0)
