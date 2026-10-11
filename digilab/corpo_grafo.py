"""O grafo de reacoes do corpo, validado antes da run (V2; docs/TAREFA_V2_CORPO_DRIVES.md, secao 18; decisao D-3).

O grafo do corpo e declarado como dado, numa tabela unica: os quimicos (com o receptor, a meia-vida e o teto com descarte), as reacoes
(o que consomem e o que produzem), os emissores (o que os dispara, o que leem e o que emitem). O `Corpo` (digilab/corpo.py) monta a
tabela uma vez (`corpo.grafo_do_corpo`) e a usa: a lista e a ordem dos quimicos, os receptores, as meias-vidas, os emissores do tick em
cada fase e as quantidades dos estimulos novos. A checagem le a mesma tabela, entao nao existem duas listas que podem divergir.

As checagens estaticas (`checar`), que rodam em teste e na carga do `Corpo` e falham alto (`GrafoInvalido`):
  1. fechado: nenhuma reacao, emissor ou leitura cita quimico fora da tabela;
  2. sumidouro: todo quimico tem pelo menos um caminho de consumo (uma reacao que o gasta, um emissor que o reduz, uma meia-vida ou um
     teto com descarte);
  3. automantido: nenhum quimico consumido fica sem reposicao (um emissor que o sobe, uma reacao que o produz) ou sem teto declarado;
  4. laco de ganho: no grafo receptor -> emissor, nenhum ciclo tem produto de ganhos >= 1, contado em inteiros (produto dos numeradores
     >= produto dos denominadores). Uma aresta e uma influencia positiva: o quimico lido aumenta o que o emissor produz do quimico
     alvo (ou corta o que ele consome dele, como o susto no carinho). As reacoes com limiar (o metabolismo) tambem leem um quimico e
     entram aqui com o mesmo sentido: "acima" aumenta o que produzem, "abaixo" corta o que consomem.
Desde o metabolismo (docs/TAREFA_V2_METABOLISMO.md, secao 3), duas checagens a mais, que so mordem nas reacoes:
  2b. sumidouro real das transferencias: as reacoes com limiar so passam um quimico a outro (1 por 1); todo quimico que elas tocam
      tem de chegar, por elas, a um quimico com sumidouro de verdade (um emissor que o reduz, uma meia-vida, uma reacao que o consome
      sem ser transferencia). O teto nao conta: um estoque que so sai pelo teto nao gasta nada (o combustivel sem gasto falha);
  3b. reposicao do que as transferencias consomem: todo quimico que uma reacao com limiar consome tem uma fonte (um emissor que o sobe,
      uma reacao que o produz). Aqui o teto nao desculpa (a reserva sem armazenamento falha). Nas reacoes sem limiar (a digestao) vale a
      checagem 3 de sempre, em que o teto desculpa.
O relato (sem recusar): os pares acoplados com meias-vidas na mesma ordem (a maior < 10 vezes a menor), o risco de oscilacao; e os
quimicos cujo unico sumidouro e o teto.

O criterio "fechado e automantido" e desenho nosso; a literatura citada para ele ainda nao foi lida (D-1). So biblioteca padrao; nao
importa o corpo nem o cerebro.
"""

from __future__ import annotations

from dataclasses import dataclass

GATILHOS_TICK = ("tick", "acordado", "dormindo", "noite_acordado", "dia_acordado", "sujeira", "privacao", "sem_privacao", "limiar",
                 "necessidades", "acima",      # banheiro: por necessidade na regiao (fase 1); um quimico acima do limiar (fase 2)
                 "abaixo")                     # metabolismo: um quimico abaixo do limiar (fase 2), o espelho do "acima"
LADOS_REACAO = ("acima", "abaixo")           # o lado do limiar de uma reacao com limiar (a transferencia do metabolismo)
GATILHOS = GATILHOS_TICK + ("estimulo",)
LEITURAS_RECEPTOR = ("drive", "falta")       # drive: S - div_arred(q S, C) (os drives de hoje); falta: div_arred(q S, C)
ORDEM_MEIA_VIDA = 10                         # "na mesma ordem": a maior meia-vida do par e menor que 10 vezes a menor


class GrafoInvalido(ValueError):
    """Uma checagem estatica do grafo do corpo falhou (secao 18)."""


@dataclass(frozen=True)
class Quimico:
    nome: str
    teto: int                                # o corte de cima (C)
    descarte: bool = True                    # o que passa do teto e descartado
    receptor: str | None = None              # o nome do receptor para o cerebro (o campo da PercepcaoCorpo); None = sem receptor
    leitura: str | None = None               # "drive" ou "falta" (LEITURAS_RECEPTOR); so com receptor
    meia_vida: int | None = None             # h, em ticks (relato e conferencia da k)
    k_meia_vida: int | None = None           # a constante inteira do passo da meia-vida (secao 3)


@dataclass(frozen=True)
class Reacao:
    """Uma reacao do tick. Sem limiar (`le` None): a digestao, que tira `taxa` no maximo de cada quimico consumido; o que ela produz sai
    da fracao num/den do consumido (`fracoes`), com o resto guardado. Com limiar (o metabolismo): uma transferencia 1 por 1 de um
    quimico a outro, que so anda com `le` acima (ou abaixo) de `limiar`, ate min(taxa, a distancia ao limiar, o que ha, o que cabe)."""

    nome: str
    consome: tuple[str, ...]
    produz: tuple[str, ...]
    taxa: int                                # o maximo por tick
    fracoes: tuple[tuple[str, int, int], ...] = ()   # (quimico produzido, num, den): a parte do consumido que vira ele
    le: str | None = None                    # o quimico do limiar (so nas transferencias)
    lado: str | None = None                  # "acima" ou "abaixo" (LADOS_REACAO)
    limiar: int = 0


@dataclass(frozen=True)
class Leitura:
    """Uma aresta receptor -> emissor: o emissor le `quimico`, com ganho num/den por unidade. `sinal` +1: mais do quimico lido, mais
    efeito; -1: mais do quimico lido, menos efeito (o susto corta o carinho)."""

    quimico: str
    num: int
    den: int
    sinal: int = 1


@dataclass(frozen=True)
class Emissor:
    nome: str
    gatilho: str                             # GATILHOS
    fase: int                                # 1 ou 2 no tick; 0 nos estimulos
    efeitos: tuple[tuple[str, int], ...]     # (quimico, delta por disparo; o sinal e o da falta/concentracao)
    le: tuple[Leitura, ...] = ()
    limiar: int = 0                          # so no gatilho "limiar": soma de max(0, q - limiar) dos quimicos lidos
    divisor: int = 1                         # so no gatilho "limiar": div_arred(soma, divisor)
    variavel: bool = False                   # a quantidade vem de fora (a bola, a fruta, o andar): o delta guarda so o sinal


@dataclass(frozen=True)
class Grafo:
    quimicos: tuple[Quimico, ...]
    reacoes: tuple[Reacao, ...]
    emissores: tuple[Emissor, ...]

    @property
    def nomes(self) -> tuple[str, ...]:
        return tuple(q.nome for q in self.quimicos)

    def quimico(self, nome: str) -> Quimico:
        for q in self.quimicos:
            if q.nome == nome:
                return q
        raise KeyError(f"quimico fora do grafo: {nome!r}")

    def emissor(self, nome: str) -> Emissor:
        for e in self.emissores:
            if e.nome == nome:
                return e
        raise KeyError(f"emissor fora do grafo: {nome!r}")

    def tem_emissor(self, nome: str) -> bool:
        return any(e.nome == nome for e in self.emissores)

    def da_fase(self, fase: int) -> tuple[Emissor, ...]:
        return tuple(e for e in self.emissores if e.fase == fase and e.gatilho != "estimulo")

    def receptores(self) -> tuple[Quimico, ...]:
        return tuple(q for q in self.quimicos if q.receptor is not None)


# ------------------------------------------------------------------ as checagens

def _forma(g: Grafo) -> None:
    """A forma da tabela: nomes unicos, gatilhos e leituras conhecidos, meia-vida e k juntas, deltas inteiros nao nulos."""
    nomes = g.nomes
    if len(set(nomes)) != len(nomes):
        raise GrafoInvalido(f"quimico repetido: {nomes}")
    receptores = [q.receptor for q in g.quimicos if q.receptor is not None]
    if len(set(receptores)) != len(receptores):
        raise GrafoInvalido(f"receptor repetido: {receptores}")
    for q in g.quimicos:
        if type(q.teto) is not int or q.teto < 0:
            raise GrafoInvalido(f"{q.nome}: teto {q.teto!r}")
        if (q.receptor is None) != (q.leitura is None) or (q.leitura is not None and q.leitura not in LEITURAS_RECEPTOR):
            raise GrafoInvalido(f"{q.nome}: receptor {q.receptor!r} com leitura {q.leitura!r}")
        if (q.meia_vida is None) != (q.k_meia_vida is None):
            raise GrafoInvalido(f"{q.nome}: meia-vida e k so juntas")
        if q.k_meia_vida is not None and (type(q.k_meia_vida) is not int or q.k_meia_vida <= 0 or q.meia_vida <= 0):
            raise GrafoInvalido(f"{q.nome}: meia-vida {q.meia_vida!r}, k {q.k_meia_vida!r}")
    for nome in [e.nome for e in g.emissores] + [r.nome for r in g.reacoes]:
        if [e.nome for e in g.emissores].count(nome) + [r.nome for r in g.reacoes].count(nome) != 1:
            raise GrafoInvalido(f"emissor ou reacao repetido: {nome!r}")
    for e in g.emissores:
        if e.gatilho not in GATILHOS:
            raise GrafoInvalido(f"{e.nome}: gatilho {e.gatilho!r}")
        if (e.gatilho == "estimulo") != (e.fase == 0) or e.fase not in (0, 1, 2):
            raise GrafoInvalido(f"{e.nome}: fase {e.fase} com o gatilho {e.gatilho!r}")
        if not e.efeitos or any(type(d) is not int or d == 0 for _, d in e.efeitos):
            raise GrafoInvalido(f"{e.nome}: efeitos {e.efeitos!r}")
        if e.gatilho == "limiar" and not (e.le and e.divisor > 1):
            raise GrafoInvalido(f"{e.nome}: o gatilho limiar precisa de leituras e de divisor > 1")
        if e.gatilho == "acima" and not (len(e.le) == 1 and e.divisor == 1 and e.fase == 2):
            raise GrafoInvalido(f"{e.nome}: o gatilho acima le um quimico so, sem divisor, na fase 2")
        for le in e.le:
            if type(le.num) is not int or type(le.den) is not int or le.num < 0 or le.den <= 0 or le.sinal not in (1, -1):
                raise GrafoInvalido(f"{e.nome}: leitura {le!r}")
        if e.gatilho == "abaixo" and not (len(e.le) == 1 and e.le[0].sinal == -1 and e.divisor == 1 and e.fase == 2):
            raise GrafoInvalido(f"{e.nome}: o gatilho abaixo le um quimico so, com sinal -1 (menos dele, mais efeito), sem divisor, "
                                "na fase 2")
    for r in g.reacoes:
        if not r.consome or type(r.taxa) is not int or r.taxa <= 0:
            raise GrafoInvalido(f"{r.nome}: reacao {r!r}")
        for q, num, den in r.fracoes:
            if q not in r.produz or type(num) is not int or type(den) is not int or num <= 0 or den <= 0:
                raise GrafoInvalido(f"{r.nome}: fracao {(q, num, den)!r}")
        if len({q for q, _, _ in r.fracoes}) != len(r.fracoes):
            raise GrafoInvalido(f"{r.nome}: fracao repetida {r.fracoes!r}")
        if (r.le is None) != (r.lado is None):
            raise GrafoInvalido(f"{r.nome}: o limiar de uma reacao pede o quimico lido e o lado juntos")
        if r.le is not None:
            if (r.lado not in LADOS_REACAO or len(r.consome) != 1 or len(r.produz) != 1 or r.consome == r.produz or r.fracoes
                    or type(r.limiar) is not int or r.limiar < 0):
                raise GrafoInvalido(f"{r.nome}: a reacao com limiar e uma transferencia 1 por 1 de um quimico a outro, com o lado "
                                    f"{LADOS_REACAO} e limiar inteiro: {r!r}")
        elif r.limiar != 0:
            raise GrafoInvalido(f"{r.nome}: limiar sem o quimico lido")


def _fechado(g: Grafo) -> None:
    conhecidos = set(g.nomes)
    citados = []
    for r in g.reacoes:
        citados += [(r.nome, q) for q in r.consome + r.produz + ((r.le,) if r.le is not None else ())]
    for e in g.emissores:
        citados += [(e.nome, q) for q, _ in e.efeitos] + [(e.nome, le.quimico) for le in e.le]
    fora = sorted({(onde, q) for onde, q in citados if q not in conhecidos})
    if fora:
        raise GrafoInvalido(f"grafo nao fechado: quimicos fora da tabela {fora}")


def _caminhos(g: Grafo) -> tuple[dict, dict]:
    """(sumidouros, fontes) por quimico, com o que os faz."""
    sumidouros = {q: [] for q in g.nomes}
    fontes = {q: [] for q in g.nomes}
    for r in g.reacoes:
        for q in r.consome:
            sumidouros[q].append(f"reacao:{r.nome}")
        for q in r.produz:
            fontes[q].append(f"reacao:{r.nome}")
    for e in g.emissores:
        for q, d in e.efeitos:
            (sumidouros if d < 0 else fontes)[q].append(f"emissor:{e.nome}")
    for q in g.quimicos:
        if q.k_meia_vida is not None:
            sumidouros[q.nome].append("meia_vida")
        if q.teto > 0 and q.descarte:
            sumidouros[q.nome].append("teto")
    return sumidouros, fontes


def _arestas(g: Grafo) -> dict[tuple[str, str], tuple[int, int]]:
    """As arestas de influencia positiva receptor -> emissor -> quimico, com o maior ganho (num, den) entre os emissores."""
    arestas: dict[tuple[str, str], tuple[int, int]] = {}
    for e in g.emissores:
        for le in e.le:
            for alvo, d in e.efeitos:
                if (d > 0) == (le.sinal > 0):          # mais do lido, mais do alvo
                    chave = (le.quimico, alvo)
                    atual = arestas.get(chave)
                    if atual is None or le.num * atual[1] > atual[0] * le.den:
                        arestas[chave] = (le.num, le.den)
    # as transferencias com limiar: andam 1 por 1, entao o ganho local e 1. "acima": mais do lido, mais do produzido (e mais consumo);
    # "abaixo": mais do lido, menos consumo (mais do consumido). As retroalimentacoes do metabolismo sao negativas e nao viram aresta
    for r in g.reacoes:
        if r.le is None:
            continue
        for alvo in (r.produz if r.lado == "acima" else r.consome):
            arestas.setdefault((r.le, alvo), (1, 1))
    return arestas


def ciclos(arestas: dict) -> list[tuple[str, ...]]:
    """Os ciclos simples do grafo dirigido (cada um uma vez, comecando pelo menor no)."""
    vizinhos: dict[str, list[str]] = {}
    for a, b in arestas:
        vizinhos.setdefault(a, []).append(b)
    achados = []

    def busca(inicio: str, atual: str, caminho: list[str]) -> None:
        for prox in sorted(vizinhos.get(atual, ())):
            if prox == inicio:
                achados.append(tuple(caminho))
            elif prox > inicio and prox not in caminho:
                busca(inicio, prox, caminho + [prox])

    for no in sorted(vizinhos):
        busca(no, no, [no])
    return achados


def checar(g: Grafo) -> dict:
    """As quatro checagens da secao 18 (falham alto) e o relato. Devolve o relato."""
    _forma(g)
    _fechado(g)
    sumidouros, fontes = _caminhos(g)
    sem_sumidouro = [q for q, s in sumidouros.items() if not s]
    if sem_sumidouro:
        raise GrafoInvalido(f"quimicos sem sumidouro: {sem_sumidouro}")
    teto = {q.nome: q.teto > 0 for q in g.quimicos}
    sem_reposicao = [q for q, s in sumidouros.items() if any(x != "teto" for x in s) and not fontes[q] and not teto[q]]
    if sem_reposicao:
        raise GrafoInvalido(f"quimicos consumidos sem reposicao nem teto (nao automantido): {sem_reposicao}")
    _transferencias(g, sumidouros, fontes)
    arestas = _arestas(g)
    lacos = []
    for c in ciclos(arestas):
        num = den = 1
        for a, b in zip(c, c[1:] + c[:1]):
            n, d = arestas[(a, b)]
            num, den = num * n, den * d
        lacos.append({"ciclo": list(c), "ganho": [num, den]})
        if num >= den:
            raise GrafoInvalido(f"laco receptor -> emissor com ganho >= 1: {c} ({num}/{den})")
    return {"pares_meia_vida_mesma_ordem": pares_mesma_ordem(g, arestas), "so_pelo_teto": sorted(
        q for q, s in sumidouros.items() if s == ["teto"]), "lacos": lacos,
        "sumidouros": {q: list(s) for q, s in sumidouros.items()}, "fontes": {q: list(s) for q, s in fontes.items()}}


def _transferencias(g: Grafo, sumidouros: dict, fontes: dict) -> None:
    """As checagens 2b e 3b (falham alto): o que as transferencias consomem tem fonte, e o que elas tocam chega a um sumidouro de verdade
    (nem o teto nem outra transferencia)."""
    transfere = {r.nome for r in g.reacoes if r.le is not None}
    if not transfere:
        return
    consumidos = sorted({q for r in g.reacoes if r.le is not None for q in r.consome})
    sem_fonte = [q for q in consumidos if not fontes[q]]
    if sem_fonte:
        raise GrafoInvalido(f"quimicos que uma transferencia consome sem fonte (o teto nao repoe; nao automantido): {sem_fonte}")
    real = {q for q, s in sumidouros.items()
            if any(x != "teto" and not (x.startswith("reacao:") and x[len("reacao:"):] in transfere) for x in s)}
    passa: dict[str, set[str]] = {}                    # quimico -> para onde as transferencias o levam
    for r in g.reacoes:
        if r.le is not None:
            passa.setdefault(r.consome[0], set()).add(r.produz[0])
    tocados = sorted({q for r in g.reacoes if r.le is not None for q in r.consome + r.produz})
    presos = []
    for q in tocados:
        vistos, pilha = set(), [q]
        while pilha:
            x = pilha.pop()
            if x not in vistos:
                vistos.add(x)
                pilha.extend(passa.get(x, ()))
        if not vistos & real:
            presos.append(q)
    if presos:
        raise GrafoInvalido(f"estoques que so saem pelo teto (sem sumidouro de verdade pelas transferencias): {presos}")


def pares_mesma_ordem(g: Grafo, arestas: dict | None = None) -> list[list[str]]:
    """Os pares acoplados (uma aresta entre eles, em qualquer sentido, ou o mesmo emissor/reacao mexendo nos dois) com meias-vidas na
    mesma ordem. So relato."""
    arestas = _arestas(g) if arestas is None else arestas
    acoplados = {frozenset(par) for par in arestas if par[0] != par[1]}
    for e in g.emissores:
        alvos = [q for q, _ in e.efeitos] + [le.quimico for le in e.le]
        acoplados |= {frozenset((a, b)) for a in alvos for b in alvos if a != b}
    for r in g.reacoes:
        alvos = list(r.consome + r.produz)
        acoplados |= {frozenset((a, b)) for a in alvos for b in alvos if a != b}
    h = {q.nome: q.meia_vida for q in g.quimicos if q.meia_vida is not None}
    pares = []
    for par in acoplados:
        a, b = sorted(par)
        if a in h and b in h and max(h[a], h[b]) < ORDEM_MEIA_VIDA * min(h[a], h[b]):
            pares.append([a, b])
    return sorted(pares)
