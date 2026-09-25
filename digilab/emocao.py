"""Emocao filtrada pelo temperamento (docs/ADENDO_MEMORIA_EMOCAO_DF.md, secao 2.1).

Todo evento que gera memoria (MemoriaEspacos.eventos) gera tambem uma emocao, e ela
depende do temperamento: o mesmo atraso irrita o rancoroso e entristece o sensivel.
Tabela declarativa categoria x temperamento -> (emocao, valencia em [-1, 1]):
  - cada regra e (eixo, polo, emocao, valencia); vale se polo * eixo > limiar_eixo;
  - se varias valem, vence o eixo de maior modulo (empate: a primeira da tabela);
  - nenhuma vale: a emocao padrao da categoria.
Toda categoria ativa da memoria tem padrao, entao toda combinacao de temperamento tem
emocao (cobertura verificada na carga).

Somente leitura: funcao pura dos eventos da memoria + temperamento, sem rng, sem efeito
em stats, combate ou aprendizado. "A valencia multiplica a intensidade da memoria" fica
atras de ConfigEmocao.modula_memoria (desligada; ver docs/REGISTRO_DESVIOS.md).
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import CONFIG_EMOCAO, CONFIG_MEMORIA_ESPACOS, ConfigEmocao

# categoria -> {"regras": ((eixo, polo, emocao, valencia), ...), "padrao": (emocao, valencia)}. PROPOSTO.
EMOCOES: dict[str, dict] = {
    "demora": {"regras": (("rancor", "+", "raiva", -0.9), ("sensibilidade", "+", "tristeza", -0.7)),
               "padrao": ("incomodo", -0.4)},
    "bronca": {"regras": (("rancor", "+", "raiva", -0.8), ("sensibilidade", "-", "ferido", -0.9),
                          ("teimosia", "+", "desdem", -0.2)),
               "padrao": ("vergonha", -0.5)},
    "elogio": {"regras": (("sensibilidade", "+", "euforia", 0.9), ("teimosia", "+", "indiferenca", 0.1)),
               "padrao": ("orgulho", 0.6)},
    "carinho": {"regras": (("sensibilidade", "+", "ternura", 0.8), ("curiosidade", "-", "timidez", 0.3)),
                "padrao": ("alegria", 0.5)},
}


class TabelaEmocaoIncompleta(ValueError):
    pass


@dataclass(frozen=True)
class Emocao:
    tick: int
    categoria: str
    nome: str
    valencia: float
    eixo: str | None          # eixo do temperamento que escolheu a emocao (None: padrao)
    ref: int | None           # ordinal da acao do dono que gerou o evento (None: pedido perdido)

    def para_dict(self) -> dict:
        return {"tick": self.tick, "categoria": self.categoria, "nome": self.nome, "valencia": self.valencia,
                "eixo": self.eixo, "ref": self.ref}


def nomes_de_emocao() -> set[str]:
    return {r[2] for e in EMOCOES.values() for r in e["regras"]} | {e["padrao"][0] for e in EMOCOES.values()}


def validar_emocoes(tabela: dict | None = None, ativas=None) -> None:
    from .temperamento import EIXOS

    tabela = EMOCOES if tabela is None else tabela
    ativas = CONFIG_MEMORIA_ESPACOS.ativas if ativas is None else ativas
    faltam = sorted(set(ativas) - set(tabela))
    if faltam:
        raise TabelaEmocaoIncompleta(f"categorias ativas sem emocao: {faltam}")
    for cat, e in tabela.items():
        if cat not in CONFIG_MEMORIA_ESPACOS.categorias:
            raise TabelaEmocaoIncompleta(f"emocao para categoria desconhecida: {cat!r}")
        if "padrao" not in e or "regras" not in e:
            raise TabelaEmocaoIncompleta(f"categoria {cat!r} sem padrao ou sem regras")
        for eixo, polo, nome, val in e["regras"]:
            if eixo not in EIXOS or polo not in "+-" or not nome:
                raise TabelaEmocaoIncompleta(f"regra invalida em {cat!r}: {(eixo, polo, nome)}")
            if not -1.0 <= val <= 1.0:
                raise TabelaEmocaoIncompleta(f"valencia fora de [-1, 1] em {cat!r}/{nome}: {val}")
        if not -1.0 <= e["padrao"][1] <= 1.0:
            raise TabelaEmocaoIncompleta(f"valencia padrao fora de [-1, 1] em {cat!r}")


def emocao_de(categoria: str, temperamento, tick: int = 0, ref: int | None = None,
              cfg: ConfigEmocao | None = None) -> Emocao:
    cfg = cfg or CONFIG_EMOCAO
    if categoria not in EMOCOES:
        raise TabelaEmocaoIncompleta(f"categoria sem emocao: {categoria!r}")
    melhor = None
    for i, (eixo, polo, nome, val) in enumerate(EMOCOES[categoria]["regras"]):
        v = getattr(temperamento, eixo)
        if (v if polo == "+" else -v) > cfg.limiar_eixo:
            chave = (abs(v), -i)
            if melhor is None or chave > melhor[0]:
                melhor = (chave, eixo, nome, val)
    if melhor is None:
        nome, val = EMOCOES[categoria]["padrao"]
        return Emocao(tick, categoria, nome, val, None, ref)
    _, eixo, nome, val = melhor
    return Emocao(tick, categoria, nome, val, eixo, ref)


def emocoes_da_memoria(memoria, temperamento, cfg: ConfigEmocao | None = None) -> list[Emocao]:
    """Uma emocao por evento que gerou memoria (MemoriaEspacos.eventos), em ordem."""
    return [emocao_de(c, temperamento, t, ref, cfg) for t, c, _, ref in memoria.eventos]


validar_emocoes()
