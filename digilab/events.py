"""Eventos.

O log de eventos e a unica fonte de verdade. O estado do pet nunca e
salvo: ele e sempre reconstruido rodando o log de novo a partir do
nascimento, com a mesma semente. Se o replay divergir, e bug, e o teste
quebra.

So dois tipos de evento entram no log:

  AcaoUsuario  - o que a pessoa fez, e quando
  Avanco       - quanto tempo passou desde o evento anterior

As acoes do pet NAO entram no log. Elas sao derivadas: sao exatamente o
que a politica produz ao reprocessar o log. E por isso que o log e um
dado de pesquisa e nao so um save file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Sequence


class AcaoUsuario(str, Enum):
    ALIMENTAR = "alimentar"
    LIMPAR = "limpar"
    BRINCAR = "brincar"
    ACARICIAR = "acariciar"
    ELOGIAR = "elogiar"
    REPREENDER = "repreender"
    # treino (TAREFA_TREINO_SOMBRIO): um botao por exercicio. So o MotorTreino sabe aplicar;
    # no motor da v1 (state.aplicar_acao_usuario) elas levantam erro. Donos da v1 usam ACOES_V1.
    TREINAR_LEVANTAR_PEDRA = "treinar_levantar_pedra"
    TREINAR_CORRIDA = "treinar_corrida"
    TREINAR_ALVO = "treinar_alvo"
    TREINAR_ESQUIVA = "treinar_esquiva"
    TREINAR_MEDITAR = "treinar_meditar"
    TREINAR_RESISTENCIA = "treinar_resistencia"
    # educacao-v1 (docs/DESIGN_EDUCACAO_HERANCA_LESOES.md): so o MotorEducacao sabe aplicar; nos motores
    # anteriores levantam erro. Ficam no fim do enum para nao mexer em nada que dependa da ordem.
    PETISCO = "petisco"
    LEVAR_AO_BANHEIRO = "levar_ao_banheiro"
    TRATAR_LESAO = "tratar_lesao"
    # V2, A1 (docs/V2_A1_BOLA_DESENHO.md): a bola no cenario. So o MotorAmbiente (digilab/ambiente.py) sabe aplicar; nos
    # motores anteriores levantam erro. No fim do enum, como as de educacao: nada que dependa da ordem muda.
    POR_BOLA = "por_bola"
    TIRAR_BOLA = "tirar_bola"
    # V2, N4 (docs/DEFINICOES_FRUTAS_V2.md, F3): o dono oferece uma fruta (um botao por fruta). So o MotorFrutas
    # (digilab/frutas.py) sabe aplicar; nos motores anteriores levantam erro. No fim do enum, como a bola.
    OFERECER_FRUTA_A = "oferecer_fruta_a"
    OFERECER_FRUTA_B = "oferecer_fruta_b"
    OFERECER_FRUTA_C = "oferecer_fruta_c"
    # V2, N5 (docs/TAREFA_V2_N5_MUNDO.md; nomes definidos no docs/PLANO_ANALISE_V2_N5.md, PR #142): o dono INFORMA sobre uma fruta ("faz bem" ou
    # "faz mal"). O conteudo e o que o dono diz; se esta certo ou errado e decidido pelo braco (P2, P2e), nao pelo evento. Nao e cuidado
    # nem reforco: so o MotorFrutas com ConfigInformacao.ligada aceita; nos motores anteriores levantam erro. No fim do enum.
    INFORMAR_FRUTA_A_BEM = "informar_fruta_a_bem"
    INFORMAR_FRUTA_A_MAL = "informar_fruta_a_mal"
    INFORMAR_FRUTA_B_BEM = "informar_fruta_b_bem"
    INFORMAR_FRUTA_B_MAL = "informar_fruta_b_mal"
    INFORMAR_FRUTA_C_BEM = "informar_fruta_c_bem"
    INFORMAR_FRUTA_C_MAL = "informar_fruta_c_mal"
    # V2, N7 (docs/PLANO_ANALISE_V2_N7.md, decisao N7-1): o dono PEDE "deixe a fruta X". E a vontade do dono, sem valor de verdade, e nao
    # a informacao do N5. Nao e cuidado nem reforco: so o MotorFrutas com ConfigPedido.ligada aceita; nos motores anteriores levantam
    # erro. No fim do enum.
    PEDIR_DEIXAR_FRUTA_A = "pedir_deixar_fruta_a"
    PEDIR_DEIXAR_FRUTA_B = "pedir_deixar_fruta_b"
    PEDIR_DEIXAR_FRUTA_C = "pedir_deixar_fruta_c"
    # V2, corpo, etapa 6 (docs/TAREFA_V2_CORPO_DRIVES.md, secao 8): o tapa, a desaprovacao com corpo (dor, susto, estresse) e o sinal da
    # bronca. So o MotorCorpo com ConfigCorpo.gestos aceita; nos motores de hoje (e no reproduzir de hoje) levanta erro. No fim do enum.
    TAPA = "tapa"
    # V2, o pet que pensa (J5; docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.3, etapa 3): o dono da a fruta NA MAO (o teste 1, a revalorizacao;
    # PQ-4) e a troca de tipo entre duas classes de arvore (o teste 2). Os dois ficam fora do orcamento, pelo canal do mundo, e so o
    # MotorMundo com ConfigPetQuePensaMundo.ligada aceita; nos motores de hoje levantam erro. No fim do enum.
    DAR_FRUTA_A = "dar_fruta_a"
    DAR_FRUTA_B = "dar_fruta_b"
    DAR_FRUTA_C = "dar_fruta_c"
    TROCAR_ARVORES_A_B = "trocar_arvores_a_b"
    TROCAR_ARVORES_A_C = "trocar_arvores_a_c"
    TROCAR_ARVORES_B_C = "trocar_arvores_b_c"


# as 6 acoes da v1, na ordem original: donos sorteiam daqui (list(AcaoUsuario) mudaria a
# canonica, que sorteia entre todas)
ACOES_V1 = (AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR,
            AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER)
ACOES_TREINO = tuple(a for a in AcaoUsuario if a.value.startswith("treinar_"))
ACOES_EDUCACAO = (AcaoUsuario.PETISCO, AcaoUsuario.LEVAR_AO_BANHEIRO, AcaoUsuario.TRATAR_LESAO)
ACOES_BOLA = (AcaoUsuario.POR_BOLA, AcaoUsuario.TIRAR_BOLA)
ACOES_FRUTAS = (AcaoUsuario.OFERECER_FRUTA_A, AcaoUsuario.OFERECER_FRUTA_B, AcaoUsuario.OFERECER_FRUTA_C)
ACOES_CORPO = (AcaoUsuario.TAPA,)
FRUTAS = ("a", "b", "c")


def fruta_de(acao: AcaoUsuario) -> str:
    if acao not in ACOES_FRUTAS:
        raise ValueError(f"acao nao e oferta de fruta: {acao}")
    return acao.value[len("oferecer_fruta_"):]


CONTEUDOS_INFORMACAO = ("bem", "mal")
ACOES_INFORMACAO = tuple(AcaoUsuario(f"informar_fruta_{f}_{c}") for f in FRUTAS for c in CONTEUDOS_INFORMACAO)


def informacao_de(acao: AcaoUsuario) -> tuple[str, str]:
    """(fruta, conteudo) de uma acao de informar; conteudo em CONTEUDOS_INFORMACAO"""
    if acao not in ACOES_INFORMACAO:
        raise ValueError(f"acao nao e informacao: {acao}")
    _, _, fruta, conteudo = acao.value.split("_")
    return fruta, conteudo


def informar(fruta: str, conteudo: str) -> AcaoUsuario:
    if fruta not in FRUTAS or conteudo not in CONTEUDOS_INFORMACAO:
        raise ValueError(f"informacao invalida: {fruta!r}, {conteudo!r}")
    return AcaoUsuario(f"informar_fruta_{fruta}_{conteudo}")


ACOES_PEDIDO = tuple(AcaoUsuario(f"pedir_deixar_fruta_{f}") for f in FRUTAS)


def pedido_de(acao: AcaoUsuario) -> str:
    """a fruta de um pedido \"deixe a fruta X\" (N7)"""
    if acao not in ACOES_PEDIDO:
        raise ValueError(f"acao nao e pedido: {acao}")
    return acao.value[len("pedir_deixar_fruta_"):]


def pedir_deixar(fruta: str) -> AcaoUsuario:
    if fruta not in FRUTAS:
        raise ValueError(f"fruta desconhecida: {fruta!r}")
    return AcaoUsuario(f"pedir_deixar_fruta_{fruta}")


ACOES_MAO = tuple(AcaoUsuario(f"dar_fruta_{f}") for f in FRUTAS)
PARES_TROCA = (("a", "b"), ("a", "c"), ("b", "c"))
ACOES_TROCA_ARVORES = tuple(AcaoUsuario(f"trocar_arvores_{x}_{y}") for x, y in PARES_TROCA)


def fruta_dada(acao: AcaoUsuario) -> str:
    """a fruta que o dono da na mao (J5)"""
    if acao not in ACOES_MAO:
        raise ValueError(f"acao nao e fruta na mao: {acao}")
    return acao.value[len("dar_fruta_"):]


def dar_fruta(fruta: str) -> AcaoUsuario:
    if fruta not in FRUTAS:
        raise ValueError(f"fruta desconhecida: {fruta!r}")
    return AcaoUsuario(f"dar_fruta_{fruta}")


def par_da_troca(acao: AcaoUsuario) -> tuple[str, str]:
    """(x, y) da troca de tipo por arvore (J5), em ordem"""
    if acao not in ACOES_TROCA_ARVORES:
        raise ValueError(f"acao nao e troca de tipo: {acao}")
    _, _, x, y = acao.value.split("_")
    return x, y


def trocar_arvores(x: str, y: str) -> AcaoUsuario:
    par = tuple(sorted((x, y)))
    if par not in PARES_TROCA:
        raise ValueError(f"troca invalida: {x!r}, {y!r}")
    return AcaoUsuario(f"trocar_arvores_{par[0]}_{par[1]}")


def oferta_de(fruta: str) -> AcaoUsuario:
    if fruta not in FRUTAS:
        raise ValueError(f"fruta desconhecida: {fruta!r}")
    return AcaoUsuario(f"oferecer_fruta_{fruta}")


def exercicio_de(acao: AcaoUsuario) -> str:
    if acao not in ACOES_TREINO:
        raise ValueError(f"acao nao e de treino: {acao}")
    return acao.value[len("treinar_"):]


class AcaoPet(str, Enum):
    OCIOSO = "ocioso"
    DORMIR = "dormir"
    COMER = "comer"
    BRINCAR = "brincar"
    CHAMAR_ATENCAO = "chamar_atencao"
    EXPLORAR = "explorar"
    EMBURRAR = "emburrar"
    # V2, banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 4; BN-1): fazer as necessidades, no fim do enum e so com a chave do banheiro. As
    # iteracoes de hoje (bandit, metricas, tracos, arena, desejo, lobos sem banheiro) usam ACOES_PET_HOJE, as sete de sempre
    ALIVIAR = "aliviar"


# as sete acoes do pet de sempre, na ordem do enum: quem itera sobre as acoes do pet (bandit, metricas, tracos, arena, desejo, o cerebro A
# sem o banheiro) usa esta tupla, e a vida de hoje nao muda com o membro novo
ACOES_PET_HOJE = (AcaoPet.OCIOSO, AcaoPet.DORMIR, AcaoPet.COMER, AcaoPet.BRINCAR, AcaoPet.CHAMAR_ATENCAO, AcaoPet.EXPLORAR,
                  AcaoPet.EMBURRAR)
ACOES_PET_BANHEIRO = (AcaoPet.ALIVIAR,)
if ACOES_PET_HOJE + ACOES_PET_BANHEIRO != tuple(AcaoPet):      # pragma: no cover - conferido na carga
    raise RuntimeError("AcaoPet mudou: ACOES_PET_HOJE e ACOES_PET_BANHEIRO tem de cobrir o enum, na ordem")


@dataclass(frozen=True)
class Evento:
    """Um evento no log. `tick` e o tempo absoluto desde o nascimento."""

    tick: int
    tipo: str  # "avanco" | "acao_usuario"
    valor: str | int

    def para_dict(self) -> dict:
        return {"tick": self.tick, "tipo": self.tipo, "valor": self.valor}

    @staticmethod
    def de_dict(d: dict) -> "Evento":
        return Evento(tick=int(d["tick"]), tipo=str(d["tipo"]), valor=d["valor"])


def avanco(tick: int, ticks: int) -> Evento:
    if ticks <= 0:
        raise ValueError(f"avanco precisa ser positivo, recebeu {ticks}")
    return Evento(tick=tick, tipo="avanco", valor=int(ticks))


def acao_usuario(tick: int, acao: AcaoUsuario) -> Evento:
    return Evento(tick=tick, tipo="acao_usuario", valor=acao.value)


def luta(tick: int, rival: str, semente: int) -> Evento:
    """educacao-v1: luta fora da arena de pesquisa. So rival e semente: o resultado e a lesao saem do
    replay da partida. So o reproduzir_educacao entende; os replays antigos levantam erro."""
    if "|" in rival:
        raise ValueError(f"nome de rival com '|': {rival!r}")
    return Evento(tick=tick, tipo="luta", valor=f"{rival}|{int(semente)}")


def decisao_externa(tick: int, ponto: str, valor: bool, fonte: str, versao: str) -> Evento:
    """Modo livre gravado: decisao de LLM ou de acaso real. O replay le daqui e nao chama ninguem."""
    return Evento(tick=tick, tipo="decisao_externa",
                  valor=json.dumps({"ponto": ponto, "valor": valor, "fonte": fonte, "versao": versao},
                                   sort_keys=True, ensure_ascii=False))


def ler_decisao(evento: Evento) -> dict:
    if evento.tipo != "decisao_externa":
        raise ValueError(f"evento nao e decisao_externa: {evento.tipo!r}")
    d = json.loads(str(evento.valor))
    if set(d) != {"ponto", "valor", "fonte", "versao"} or not isinstance(d["valor"], bool):
        raise ValueError(f"decisao_externa malformada: {d!r}")
    return {**d, "tick": evento.tick}


def fala(tick: int, gatilho: str) -> Evento:
    """DESIGN_VOZ_PROPRIA (secao 9): fala espontanea disparada de fora (reencontro, marco...). So o gatilho vai
    para o log; se ela e mentira sai da rng_mentira do motor (o replay sorteia de novo, igual)."""
    if not gatilho or not gatilho.replace("_", "").isalnum():
        raise ValueError(f"gatilho de fala invalido: {gatilho!r}")
    return Evento(tick=tick, tipo="fala", valor=gatilho)


# V2, mundo fisico (docs/TAREFA_V2_MUNDO_FISICO.md, secao 4): o dono deixa a comida ou a bola num ponto do mapa. Tipos novos do log,
# como a `luta`: so o `reproduzir_mundo` (digilab/mundo.py) os entende; os replays de antes levantam erro. A posicao ja vem na grade
# (inteiros em subunidades, dentro do mapa: 0 <= x < 1024, 0 <= y < 480); fora disso, nao inteira ou tipo desconhecido levanta erro.
TIPOS_COMIDA_MUNDO = ("racao", "a", "b", "c")
LARGURA_MUNDO = 1024
ALTURA_MUNDO = 480


def _posicao_mundo(x, y) -> tuple[int, int]:
    if type(x) is not int or type(y) is not int:
        raise ValueError(f"posicao do mundo nao inteira: ({x!r}, {y!r})")
    if not (0 <= x < LARGURA_MUNDO and 0 <= y < ALTURA_MUNDO):
        raise ValueError(f"posicao fora do mapa: ({x}, {y})")
    return x, y


def deixar_comida(tick: int, tipo: str, x: int, y: int) -> Evento:
    if tipo not in TIPOS_COMIDA_MUNDO:
        raise ValueError(f"tipo de comida desconhecido: {tipo!r}")
    x, y = _posicao_mundo(x, y)
    return Evento(tick=tick, tipo="deixar_comida", valor=f"{tipo}|{x}|{y}")


def deixar_bola(tick: int, x: int, y: int) -> Evento:
    x, y = _posicao_mundo(x, y)
    return Evento(tick=tick, tipo="deixar_bola", valor=f"{x}|{y}")


def _inteiro_do_log(texto: str) -> int:
    if not texto.isdigit():
        raise ValueError(f"inteiro malformado no log: {texto!r}")
    return int(texto)


def ler_deixar_comida(evento: Evento) -> tuple[str, int, int]:
    if evento.tipo != "deixar_comida":
        raise ValueError(f"evento nao e deixar_comida: {evento.tipo!r}")
    partes = str(evento.valor).split("|")
    if len(partes) != 3 or partes[0] not in TIPOS_COMIDA_MUNDO:
        raise ValueError(f"deixar_comida malformado: {evento.valor!r}")
    return (partes[0],) + _posicao_mundo(_inteiro_do_log(partes[1]), _inteiro_do_log(partes[2]))


def ler_deixar_bola(evento: Evento) -> tuple[int, int]:
    if evento.tipo != "deixar_bola":
        raise ValueError(f"evento nao e deixar_bola: {evento.tipo!r}")
    partes = str(evento.valor).split("|")
    if len(partes) != 2:
        raise ValueError(f"deixar_bola malformado: {evento.valor!r}")
    return _posicao_mundo(_inteiro_do_log(partes[0]), _inteiro_do_log(partes[1]))


def ler_luta(evento: Evento) -> tuple[str, int]:
    if evento.tipo != "luta":
        raise ValueError(f"evento nao e luta: {evento.tipo!r}")
    rival, semente = str(evento.valor).rsplit("|", 1)
    return rival, int(semente)


class LogDeEventos:
    """Lista append-only de eventos, serializavel como JSONL."""

    def __init__(self, eventos: Sequence[Evento] | None = None) -> None:
        self._eventos: list[Evento] = list(eventos or [])

    def anexar(self, evento: Evento) -> None:
        if self._eventos and evento.tick < self._eventos[-1].tick:
            raise ValueError(
                f"evento fora de ordem: tick {evento.tick} vem depois de "
                f"{self._eventos[-1].tick}"
            )
        self._eventos.append(evento)

    def __iter__(self) -> Iterator[Evento]:
        return iter(self._eventos)

    def __len__(self) -> int:
        return len(self._eventos)

    def __getitem__(self, i: int) -> Evento:
        return self._eventos[i]

    def para_jsonl(self) -> str:
        return "\n".join(json.dumps(e.para_dict(), ensure_ascii=False) for e in self._eventos)

    @staticmethod
    def de_jsonl(texto: str) -> "LogDeEventos":
        eventos = [
            Evento.de_dict(json.loads(linha))
            for linha in texto.splitlines()
            if linha.strip()
        ]
        return LogDeEventos(eventos)
