"""Os conceitos que a voz recebe (CONVERSA_PET, DC2; formato fixo da secao 2 de docs/research/ESPEC_DECODIFICADOR_FALA.md).

    {"versao": "dec-v1", "k": 123, "intencao": "fome",
     "conceitos": [{"nome": "fome", "valor": 870, "confianca": 610, "alvo": "racao"}, ...]}

O decodificador (DC1) produz isto a partir do cerebro modular. Aqui so se VALIDA (a entrada da pagina nao e confiavel) e se
decide quais conceitos entram na fala. A voz nunca ve estado, log nem fato: so isto, o estagio, o estilo da especie, a fala do
dono e os fatos [J] "o dono me disse".

Os limiares (valor e confianca) sao PROPOSTOS, SEM FONTE, e vivem num lugar so: `ConfigDecodificador` (digilab/config.py, DC1); as
constantes daqui sao leituras dela (DC2b, D-CP-DC2b-1), e um teste falha se divergirem. O Matheus decide.

Formatos: `dec-v1` (DC1/DC2) e `dec-v2` (DC2b): o v2 so acrescenta ao conceito `lembranca` o campo `episodio` = {acao, classe, desfecho}, tudo
de catalogo fechado (acao: os 7 comportamentos; classe: as 8 classes de episodio; desfecho: bom, ruim ou neutro), decodificado do episodio
recuperado. Nenhum texto livre do episodio chega aqui, e o `episodio` fora do catalogo e erro (400 no servidor).
`dec-v3` (DC3d): os conceitos do dec-v2, com a `intencao` vinda da unidade de fala que o modular escolheu (a subchave `fala_unidades`): so um dos
tres conteudos de INTENCOES_FALA (fome, higiene, solidao), que sao os CONTEUDOS_FALA de digilab/config.py. No dec-v3 a intencao fora deles, ou
um nome do catalogo que nao e conteudo de fala, e erro (400). A intencao e um PEDIDO ao dono (PEDIDO_DITO), e liga a voz-v3 e a verif-v9.
"""

from __future__ import annotations

from dataclasses import dataclass

from digilab.config import CONFIG_DECODIFICADOR, CONTEUDOS_FALA

VERSAO_DEC = "dec-v1"
VERSAO_DEC_V2 = "dec-v2"
VERSAO_DEC_V3 = "dec-v3"
VERSOES_DEC = (VERSAO_DEC, VERSAO_DEC_V2, VERSAO_DEC_V3)
INTENCOES_FALA = CONTEUDOS_FALA                    # a intencao do dec-v3: o conteudo da unidade de fala (catalogo fechado)
S = 1024                                  # escala inteira do modular (digilab/digibrain): valor e confianca em [0, S]
NOMES = ("fome", "sono", "bem_estar", "mal_estar", "agitacao", "aversao", "frustracao", "determinacao", "indecisao",
         "lembranca", "solidao", "curiosidade")                              # catalogo fechado (espec, secao 2)
CLASSES_OBJETO = ("racao", "a", "b", "c", "podre", "bola")                   # = digilab/digibrain/sens.py CLASSES_OBJETO
PREFIXO_EPISODIO = "ep"                                                      # alvo de lembranca: id do episodio, ex. "ep42"
MAX_DIGITOS_EPISODIO = 6
MAX_CONCEITOS = 2 * len(NOMES)            # um nome pode vir com alvos diferentes (aversao a racao e a bola); par (nome, alvo) unico
LIMIAR_VALOR = CONFIG_DECODIFICADOR.limiar_valor            # PROPOSTO, SEM FONTE: abaixo disto o conceito nao entra na fala (a fonte e a config da DC1)
LIMIAR_CONFIANCA = CONFIG_DECODIFICADOR.limiar_confianca    # PROPOSTO, SEM FONTE: abaixo disto o conceito entra como hesitacao (idem)
ACOES_EPISODIO = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")   # os 7 comportamentos (= decodificador.COMPORTAMENTOS)
CLASSES_EPISODIO = ("racao", "a", "b", "c", "podre", "nao_havia", "bola", "sem_alvo")                  # = decodificador.CLASSES_EPISODIO
DESFECHOS = ("bom", "ruim", "neutro")
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
# como a voz-v2 diz o episodio (so palavras de catalogo; o texto livre do episodio nunca chega)
ACAO_DITA = {"ocioso": "ficar parado", "dormir": "dormir", "comer": "comer", "brincar": "brincar", "chamar_atencao": "chamar a atenção do dono",
             "explorar": "explorar", "emburrar": "ficar emburrado"}
CLASSE_DITA = {"racao": "ração", "a": "uma fruta (A)", "b": "uma fruta (B)", "c": "uma fruta (C)", "podre": "comida podre",
               "nao_havia": "um lugar onde não havia comida", "bola": "a bola", "sem_alvo": "nada em especial"}
DESFECHO_DITO = {"bom": "foi bom", "ruim": "foi ruim", "neutro": "não foi nem bom nem ruim"}
assert set(ACAO_DITA) == set(ACOES_EPISODIO) and set(CLASSE_DITA) == set(CLASSES_EPISODIO) and set(DESFECHO_DITO) == set(DESFECHOS)
# como a voz-v3 diz o pedido do dec-v3 (o que a rede escolheu pedir ao dono; so palavras de catalogo)
PEDIDO_DITO = {"fome": "pedir comida ao dono", "higiene": "pedir ao dono para te limpar", "solidao": "pedir a companhia do dono"}
assert tuple(PEDIDO_DITO) == INTENCOES_FALA == ("fome", "higiene", "solidao")


class ConceitosInvalidos(ValueError):
    """Conceitos fora do formato fixo: o servidor responde 400."""


@dataclass(frozen=True)
class Conceito:
    nome: str
    valor: int
    confianca: int
    alvo: str | None = None
    episodio: tuple | None = None            # (acao, classe, desfecho), so no conceito `lembranca` do dec-v2 e do dec-v3

    @property
    def hesitante(self) -> bool:
        return self.confianca < LIMIAR_CONFIANCA

    def para_dict(self) -> dict:
        return {"nome": self.nome, "valor": self.valor, "confianca": self.confianca,
                **({"alvo": self.alvo} if self.alvo is not None else {}),
                **({"episodio": dict(zip(("acao", "classe", "desfecho"), self.episodio))} if self.episodio is not None else {})}


@dataclass(frozen=True)
class Conceitos:
    k: int
    intencao: str
    conceitos: tuple[Conceito, ...]
    versao: str = VERSAO_DEC

    @property
    def pedido(self) -> str | None:
        """O pedido do dec-v3 (o conteudo da unidade de fala que a rede escolheu); None nos outros formatos."""
        return self.intencao if self.versao == VERSAO_DEC_V3 else None

    def ativos(self) -> tuple[Conceito, ...]:
        """Os que entram na fala: valor >= LIMIAR_VALOR, do maior valor para o menor (empate: a ordem do catalogo)."""
        ok = [c for c in self.conceitos if c.valor >= LIMIAR_VALOR]
        return tuple(sorted(ok, key=lambda c: (-c.valor, NOMES.index(c.nome), c.alvo or "")))

    def para_dict(self) -> dict:
        return {"versao": self.versao, "k": self.k, "intencao": self.intencao,
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


def _episodio(c: dict, versao: str) -> tuple:
    """O `episodio` do conceito `lembranca` do dec-v2: exatamente {acao, classe, desfecho}, cada um de catalogo (valor de tipo errado,
    inclusive lista ou dict, nunca casa); so no dec-v2, so na `lembranca` e so com alvo de episodio (`ep<N>`)."""
    e = c["episodio"]
    if versao not in (VERSAO_DEC_V2, VERSAO_DEC_V3) or c["nome"] != "lembranca":
        raise ConceitosInvalidos("conceitos: episodio so existe na lembranca do dec-v2")
    alvo = c.get("alvo")
    if not isinstance(alvo, str) or not alvo.startswith(PREFIXO_EPISODIO) or alvo in CLASSES_OBJETO:
        raise ConceitosInvalidos("conceitos: episodio so com alvo de episodio (ep<N>)")
    if not isinstance(e, dict) or set(e) != {"acao", "classe", "desfecho"}:
        raise ConceitosInvalidos("conceitos: episodio e {acao, classe, desfecho}")
    if not (isinstance(e["acao"], str) and e["acao"] in ACOES_EPISODIO and isinstance(e["classe"], str) and e["classe"] in CLASSES_EPISODIO
            and isinstance(e["desfecho"], str) and e["desfecho"] in DESFECHOS):
        raise ConceitosInvalidos("conceitos: episodio fora do catalogo")
    return (e["acao"], e["classe"], e["desfecho"])


def validar(d, rivais=frozenset()) -> Conceitos:
    """O objeto da pagina -> Conceitos, ou ConceitosInvalidos. Chave a mais ou a menos, nome fora do catalogo, numero fora de
    [0, S], booleano no lugar de inteiro, alvo fora do catalogo e (nome, alvo) repetido: tudo e erro."""
    if not isinstance(d, dict) or set(d) != {"versao", "k", "intencao", "conceitos"}:
        raise ConceitosInvalidos("conceitos: chaves erradas (versao, k, intencao, conceitos)")
    if d["versao"] not in VERSOES_DEC:                  # `in` numa tupla de str: tipo errado (lista, dict) nao casa
        raise ConceitosInvalidos(f"conceitos: versao precisa ser uma de {VERSOES_DEC!r}")
    versao = d["versao"]
    k = _inteiro(d["k"], "k", 0, 2**31 - 1)
    if d["intencao"] not in (INTENCOES_FALA if versao == VERSAO_DEC_V3 else NOMES):   # `in` numa tupla de str: tipo errado nao casa
        raise ConceitosInvalidos("conceitos: intencao fora do catalogo")
    lista = d["conceitos"]
    if not isinstance(lista, list) or len(lista) > MAX_CONCEITOS:
        raise ConceitosInvalidos("conceitos: lista invalida")
    out, vistos = [], set()
    for c in lista:
        if not isinstance(c, dict) or not {"nome", "valor", "confianca"} <= set(c) or set(c) - {"nome", "valor", "confianca", "alvo", "episodio"}:
            raise ConceitosInvalidos("conceitos: cada conceito e {nome, valor, confianca, alvo?, episodio?}")
        if c["nome"] not in NOMES:
            raise ConceitosInvalidos("conceitos: nome fora do catalogo")
        alvo = c.get("alvo")
        if "alvo" in c and not alvo_valido(alvo, rivais):
            raise ConceitosInvalidos("conceitos: alvo fora do catalogo")
        episodio = _episodio(c, versao) if "episodio" in c else None
        chave = (c["nome"], alvo)
        if chave in vistos:
            raise ConceitosInvalidos("conceitos: conceito repetido")
        vistos.add(chave)
        out.append(Conceito(c["nome"], _inteiro(c["valor"], "valor", 0, S), _inteiro(c["confianca"], "confianca", 0, S), alvo, episodio))
    return Conceitos(k, d["intencao"], tuple(out), versao)
