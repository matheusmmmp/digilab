"""Os conceitos que a voz recebe (CONVERSA_PET, DC2; formato fixo da secao 2 de docs/research/ESPEC_DECODIFICADOR_FALA.md).

    {"versao": "dec-v1", "k": 123, "intencao": "fome",
     "conceitos": [{"nome": "fome", "valor": 870, "confianca": 610, "alvo": "racao"}, ...]}

O decodificador (DC1) produz isto a partir do cerebro modular. Aqui so se VALIDA (a entrada da pagina nao e confiavel) e se
decide quais conceitos entram na fala. A voz nunca ve estado, log nem fato: so isto, o estagio, o estilo da especie, a fala do
dono e os fatos [J] "o dono me disse".

Os limiares abaixo sao PROPOSTOS, SEM FONTE: a espec (secao 2) diz que existem dois e que sao PROPOSTOS, sem dar o numero. Estes
valem ate a calibracao da DC1/DC4; o Matheus decide.
"""

from __future__ import annotations

from dataclasses import dataclass

VERSAO_DEC = "dec-v1"
S = 1024                                  # escala inteira do modular (digilab/digibrain): valor e confianca em [0, S]
NOMES = ("fome", "sono", "bem_estar", "mal_estar", "agitacao", "aversao", "frustracao", "determinacao", "indecisao",
         "lembranca", "solidao", "curiosidade")                              # catalogo fechado (espec, secao 2)
CLASSES_OBJETO = ("racao", "a", "b", "c", "podre", "bola")                   # = digilab/digibrain/sens.py CLASSES_OBJETO
PREFIXO_EPISODIO = "ep"                                                      # alvo de lembranca: id do episodio, ex. "ep42"
MAX_DIGITOS_EPISODIO = 6
MAX_CONCEITOS = 2 * len(NOMES)            # um nome pode vir com alvos diferentes (aversao a racao e a bola); par (nome, alvo) unico
LIMIAR_VALOR = S // 4                     # PROPOSTO, SEM FONTE: abaixo disto o conceito nao entra na fala
LIMIAR_CONFIANCA = S // 2                 # PROPOSTO, SEM FONTE: abaixo disto o conceito entra como hesitacao
FORTE = S * 3 // 4                        # PROPOSTO, SEM FONTE: so para o prompt dizer "forte" ou "fraco"

# o que cada conceito quer dizer, para a voz (nao e fato do pet: e o significado do nome)
SIGNIFICADO = {
    "fome": "quer comer, está com fome", "sono": "está com sono ou cansado", "bem_estar": "se sente bem, contente",
    "mal_estar": "se sente mal, incomodado", "agitacao": "está agitado, alerta ou assustado",
    "aversao": "não quer ou evita aquilo (o alvo)", "frustracao": "está frustrado, desistiu de algo",
    "determinacao": "está decidido, firme no que quer", "indecisao": "está em dúvida entre querer coisas diferentes",
    "lembranca": "lembra de algo (o alvo)", "solidao": "se sente sozinho, quer atenção ou cuidado",
    "curiosidade": "está curioso, quer explorar",
}
assert set(SIGNIFICADO) == set(NOMES)


class ConceitosInvalidos(ValueError):
    """Conceitos fora do formato fixo: o servidor responde 400."""


@dataclass(frozen=True)
class Conceito:
    nome: str
    valor: int
    confianca: int
    alvo: str | None = None

    @property
    def hesitante(self) -> bool:
        return self.confianca < LIMIAR_CONFIANCA

    def para_dict(self) -> dict:
        return {"nome": self.nome, "valor": self.valor, "confianca": self.confianca,
                **({"alvo": self.alvo} if self.alvo is not None else {})}


@dataclass(frozen=True)
class Conceitos:
    k: int
    intencao: str
    conceitos: tuple[Conceito, ...]

    def ativos(self) -> tuple[Conceito, ...]:
        """Os que entram na fala: valor >= LIMIAR_VALOR, do maior valor para o menor (empate: a ordem do catalogo)."""
        ok = [c for c in self.conceitos if c.valor >= LIMIAR_VALOR]
        return tuple(sorted(ok, key=lambda c: (-c.valor, NOMES.index(c.nome), c.alvo or "")))

    def para_dict(self) -> dict:
        return {"versao": VERSAO_DEC, "k": self.k, "intencao": self.intencao,
                "conceitos": [c.para_dict() for c in self.conceitos]}


def _inteiro(v, rotulo: str, lo: int, hi: int) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
        raise ConceitosInvalidos(f"conceitos: {rotulo} precisa ser inteiro em [{lo}, {hi}]")
    return v


def alvo_valido(alvo, rivais=frozenset()) -> bool:
    """Alvo so de catalogo: uma classe de objeto, o id de um episodio ("ep" + digitos) ou um rival (nome do corpus)."""
    if not isinstance(alvo, str):
        return False
    if alvo in CLASSES_OBJETO or alvo in rivais:
        return True
    n = alvo[len(PREFIXO_EPISODIO):]
    return alvo.startswith(PREFIXO_EPISODIO) and n.isascii() and n.isdigit() and 0 < len(n) <= MAX_DIGITOS_EPISODIO


def validar(d, rivais=frozenset()) -> Conceitos:
    """O objeto da pagina -> Conceitos, ou ConceitosInvalidos. Chave a mais ou a menos, nome fora do catalogo, numero fora de
    [0, S], booleano no lugar de inteiro, alvo fora do catalogo e (nome, alvo) repetido: tudo e erro."""
    if not isinstance(d, dict) or set(d) != {"versao", "k", "intencao", "conceitos"}:
        raise ConceitosInvalidos("conceitos: chaves erradas (versao, k, intencao, conceitos)")
    if d["versao"] != VERSAO_DEC:
        raise ConceitosInvalidos(f"conceitos: versao precisa ser {VERSAO_DEC!r}")
    k = _inteiro(d["k"], "k", 0, 2**31 - 1)
    if d["intencao"] not in NOMES:                      # `in` numa tupla de str: tipo errado (lista, dict) nao casa
        raise ConceitosInvalidos("conceitos: intencao fora do catalogo")
    lista = d["conceitos"]
    if not isinstance(lista, list) or len(lista) > MAX_CONCEITOS:
        raise ConceitosInvalidos("conceitos: lista invalida")
    out, vistos = [], set()
    for c in lista:
        if not isinstance(c, dict) or not {"nome", "valor", "confianca"} <= set(c) or set(c) - {"nome", "valor", "confianca", "alvo"}:
            raise ConceitosInvalidos("conceitos: cada conceito e {nome, valor, confianca, alvo?}")
        if c["nome"] not in NOMES:
            raise ConceitosInvalidos("conceitos: nome fora do catalogo")
        alvo = c.get("alvo")
        if "alvo" in c and not alvo_valido(alvo, rivais):
            raise ConceitosInvalidos("conceitos: alvo fora do catalogo")
        chave = (c["nome"], alvo)
        if chave in vistos:
            raise ConceitosInvalidos("conceitos: conceito repetido")
        vistos.add(chave)
        out.append(Conceito(c["nome"], _inteiro(c["valor"], "valor", 0, S), _inteiro(c["confianca"], "confianca", 0, S), alvo))
    return Conceitos(k, d["intencao"], tuple(out))
