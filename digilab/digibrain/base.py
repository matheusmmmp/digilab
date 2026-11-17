"""A base neutra do DigiBrain modular (docs/TAREFA_V3_LIMPEZA.md, a LZ2): as contas inteiras e a interface do corpo que o pacote usa, e as
tabelas de nomes que o motivo e o painel leem. Vieram do cerebro A (`digilab/policies/lobos.py`) sem mudar uma linha da conta, e o
lobos.py passa a importa-las daqui ate sair (a LZ4). So inteiros (o G-INT do pacote): o `sortear`, que usa float, fica em
`digilab/policy.py`.

- `div_arred(n, d)`: n / d em inteiros, arredondado ao mais proximo, meio longe do zero;
- `leitura_receptor`, `falta_receptor`, `contribuicoes_corpo`, `sinal_corpo` e `valor_previsto`: a leitura dos receptores da
  PercepcaoCorpo e o sinal homeostatico do corpo (secao 9 do corpo), na escala S;
- as tabelas: as regras do instinto, as entradas da percepcao, as do mundo, os fatores do plano e os receptores.
"""
from __future__ import annotations

from dataclasses import replace

FATORES_PLANO = ("plano_arvore", "plano_comida", "plano_evita")   # os fatores do motivo quando o plano decide (motivo.py, expressao.py)
# as regras do instinto, na ordem em que ele as testa (policy.py: ultima_regra)
REGRAS = ("sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono",
          "fome_moderada", "tempo_livre")
# entradas da percepcao: vies + Estado.vetor (ordem congelada em state.py) + tempo sem cuidado
ENTRADAS = ("vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora",
            "ticks_sem_cuidado")
# as regras do instinto do mundo (ambiente.REGRA_BOLA, frutas.REGRA_FRUTA) e as entradas que o motor injeta
REGRAS_MUNDO = ("bola_no_cenario", "fruta_no_cenario")
ENTRADAS_MUNDO = ("bola", "fruta")

RECEPTORES_HOJE = ("fome", "higiene", "energia", "humor", "saude")          # leitura = S - falta, na ordem de Estado.vetor
RECEPTORES_NOVOS = ("tedio", "curiosidade", "solidao", "estresse", "dor", "susto",   # leitura = a falta (dor e susto: a concentracao)
                    "vontade", "conforto")                                         # banheiro: a concentracao (a vontade, o conforto)
# BN-6: o receptor do conforto le a concentracao; a falta do drive e a falta de conforto, S - leitura (o carinho a reduz)
RECEPTORES_FALTA_INVERTIDA = ("conforto",)


def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def leitura_receptor(pc, nome: str, S: int) -> int:
    """A leitura do receptor `nome` da PercepcaoCorpo (inteiro em [0, S]); um receptor que nao existe (None) ou fora da escala falha
    alto."""
    v = getattr(pc, nome)
    if v is None:
        raise RuntimeError(f"corpo: o receptor {nome!r} nao existe nesta Observacao.corpo")
    if type(v) is not int or not 0 <= v <= S:
        raise ValueError(f"corpo: receptor {nome!r} fora de inteiros em [0, {S}]: {v!r}")
    return v


def falta_receptor(pc, nome: str, S: int) -> int:
    """A falta na escala S: S - leitura nos drives de hoje (o receptor le o drive), a propria leitura nos novos (o receptor le a falta,
    ou a concentracao na dor, no susto e na vontade), e S - leitura no conforto (BN-6: o receptor le o conforto; a falta e a de
    conforto)."""
    v = leitura_receptor(pc, nome, S)
    if nome in RECEPTORES_HOJE or nome in RECEPTORES_FALTA_INVERTIDA:
        return S - v
    if nome in RECEPTORES_NOVOS:
        return v
    raise KeyError(f"receptor desconhecido: {nome!r}")


def contribuicoes_corpo(antes, depois, drives: tuple, S: int, pesos_drives: dict | None = None,
                        pesos_janela: dict | None = None) -> dict[str, int]:
    """c_d = w_d * delta_d por drive, delta_d = falta_d(antes)**2 - falta_d(depois)**2 sobre os receptores (secao 9). Com `pesos_janela`
    (A2.4, na escala S), delta_d e ponderado como em `delta_ponderado`: div_arred(w * delta, S) quando w != S. `pesos_drives` sao os
    inteiros w_d (ConfigConsequencia.pesos_drives_corpo); sem eles, todos 1. Um drive sem peso falha alto."""
    c = {}
    for d in drives:
        fa, fd = falta_receptor(antes, d, S), falta_receptor(depois, d, S)
        delta = fa * fa - fd * fd
        if pesos_janela is not None:
            w = pesos_janela[d]
            if type(w) is not int or not 0 <= w <= S:
                raise ValueError(f"peso da janela do drive {d!r} fora de inteiros em [0, {S}]: {w!r}")
            if w != S:
                delta = div_arred(w * delta, S)
        wd = 1 if pesos_drives is None else pesos_drives[d]
        if type(wd) is not int or wd < 0:
            raise ValueError(f"w_d do drive {d!r} precisa ser inteiro >= 0: {wd!r}")
        c[d] = wd * delta
    return c


def valor_previsto(pc, delta: dict, drives: tuple, ganho: int, S: int, pesos_drives: dict | None = None) -> int:
    """O pet que pensa (a tarefa, secao 2.2): o `sinal_corpo` dos receptores de agora (`pc`) para os previstos, a leitura de agora mais
    `delta` (receptor -> mudanca, na escala S), cortada em [0, S]. Os receptores sem mudanca ficam como estao. Inteiro."""
    novos = {}
    for r, v in delta.items():
        if v != 0:
            novos[r] = max(0, min(S, leitura_receptor(pc, r, S) + v))
    if not novos:
        return 0
    return sinal_corpo(pc, replace(pc, **novos), drives, ganho, S, pesos_drives)


def sinal_corpo(antes, depois, drives: tuple, ganho: int, S: int, pesos_drives: dict | None = None,
                pesos_janela: dict | None = None) -> int:
    """V2, corpo (secao 9): f_S = div_arred(ganho * (D(antes) - D(depois)), S), com D = soma_d w_d * falta_d**2 sobre os receptores
    (`antes` e `depois` sao PercepcaoCorpo). Com os drives de hoje e w_d = 1, o numero do N3 (`sinal_homeostatico`) sobre o mesmo
    estado: o receptor e S - div_arred(q * S, C), e S - arred(h * S) do drive lido da o mesmo inteiro. Inteiro."""
    if type(ganho) is not int or ganho < 0:
        raise ValueError(f"ganho precisa ser inteiro >= 0: {ganho!r}")
    total = 0
    for c in contribuicoes_corpo(antes, depois, drives, S, pesos_drives, pesos_janela).values():
        total += c
    return div_arred(ganho * total, S)
