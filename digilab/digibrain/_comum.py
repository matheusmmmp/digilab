"""As contas comuns do DigiBrain modular (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 1): a aritmetica inteira na escala S (DM-2), sem
float, sem `/` e sem `math` (o G-INT confere pela AST).

- `mul(a, b, S) = div_arred(a x b, S)`, com o `div_arred` do A (meio longe do zero; o divisor positivo), importado do lobos.py, que nao
  muda (secao 8.1, "o reaproveitamento e por importacao");
- `phi(v) = clamp(v, 0, A_max)`, a ativacao linear por partes;
- o integrador com vazamento da forma I (secao 3): `y <- y + mul(k, u - y)`, com `k = div_arred(S x Delta, tau)`.

As chaves das unidades (comportamento, alvo) ficam aqui tambem: `chave_unidade` e `chave_json`, as mesmas em todo modulo."""
from __future__ import annotations

from ..policies.lobos import div_arred


def mul(a: int, b: int, S: int) -> int:
    """o produto na escala S: div_arred(a x b, S)"""
    return div_arred(a * b, S)


def clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else (hi if v > hi else v)


def phi(v: int, a_max: int) -> int:
    """a ativacao: clamp(v, 0, A_max)"""
    return clamp(v, 0, a_max)


def ganho_de_tau(tau: int, delta: int, S: int) -> int:
    """o ganho por decisao de uma constante de tempo tau (ticks), com tau >= Delta: div_arred(S x Delta, tau)"""
    if type(tau) is not int or tau < delta:
        raise ValueError(f"constante de tempo {tau!r} abaixo do passo do cerebro ({delta} ticks)")
    return div_arred(S * delta, tau)


def integrar(y: int, u: int, k: int, S: int) -> int:
    """um passo do integrador com vazamento (forma I): y + mul(k, u - y)"""
    return y + mul(k, u - y, S)


def chave_unidade(acao: str, tipo: str | None = None, ident=None) -> tuple:
    """a chave de uma unidade (b, o): o comportamento (o valor da AcaoPet), o tipo do alvo (None nos sem alvo) e a identidade do alvo (o id
    da comida, 0 da bola, (x, y) do lugar lembrado; None no cheiro, no vagar e nos sem alvo)"""
    return (acao, tipo, ident)


def chave_json(chave: tuple | None):
    """a chave em listas, para o registro (derivado) e o estado interno"""
    if chave is None:
        return None
    acao, tipo, ident = chave
    return [acao, tipo, list(ident) if isinstance(ident, tuple) else ident]


def sem_equacao(modulo: str, metodo: str) -> NotImplementedError:
    """o gancho vazio (M-PERS, M-GEN, M-EXPR no que a etapa 1 nao cobre)"""
    return NotImplementedError(f"{modulo}.{metodo}: gancho vazio no prototipo (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.9)")
