"""A bancada da V2, módulo `mundos`.

As condições, os mundos, os eventos do mundo, o corpo por regime, os efeitos das frutas e o calendário.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

from dataclasses import dataclass

from digilab.config import LAYOUT_MUNDO_AFASTADO, TICKS_POR_DIA, ConfigFrutas, ConfigJulgamentoFruta
from digilab.config import ConfigCorpo
from digilab.donos import Visao
from digilab.events import ACOES_BOLA, ACOES_FRUTAS, FRUTAS, AcaoUsuario, oferta_de
from digilab.frutas import MotorFrutas
from digilab.protocol import derivar_semente


# os eventos do MUNDO no log: acoes do dono que poem coisas no cenario. O acoplado nunca os tira (as ofertas de fruta do N4 entram
# aqui quando existirem). Os filtros so tiram o que o dono ENSINA ou o carinho.
EVENTOS_DO_MUNDO = frozenset(a.value for a in ACOES_BOLA + ACOES_FRUTAS)


@dataclass(frozen=True)
class Condicao:
    """Uma condicao da pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6, item 2): a relacao entre o mundo e a
    predisposicao herdada. `precisa` = o que falta (e de qual no) para a condicao existir; vazio quando ja existe."""

    nome: str
    descricao: str
    precisa: str = ""
    no: str = ""


CONDICOES = {
    "casado": Condicao("casado", "o mundo e aquele para o qual o prior foi feito: nada nele contradiz a predisposicao herdada"),
    "descasado": Condicao(
        "descasado", "o mundo contradiz o prior: a fruta preferida de nascenca faz mal (e a menos preferida faz bem)"),
    "mutavel": Condicao(
        "mutavel", "o mundo muda no meio da vida: comeca casado e o efeito das frutas troca na metade (a boa vira ruim e "
        "vice-versa); a troca fica no registro derivado e o replay a refaz"),
    # N7-5 (docs/PLANO_ANALISE_V2_N7.md, secao 4.3): fora da pergunta maior, o mundo da arbitragem
    "iguais": Condicao(
        "iguais", "as tres frutas com o mesmo efeito (neutro no humor) e a mesma nutricao: escolher uma fruta nao tem consequencia "
        "propria, so a da fome (o mundo \"iguais\" do N4 na bancada)"),
}


@dataclass(frozen=True)
class Mundo:
    nome: str
    condicao: str                    # a condicao da pergunta maior que este mundo realiza
    bola: str | None = None          # None: sem bola; "b1b2": a bola das decisoes B1/B2; "a1": a bola como a A1 rodou
    frutas: bool = False             # os mundos das frutas (MotorFrutasMundo); o efeito sai da condicao
    fisico: str | None = None        # o mundo fisico (MotorMundo): o layout, "padrao" ou "afastado" (A1.8)

    @property
    def ambiente(self) -> bool:
        """roda no MotorAmbiente (bola) ou numa subclasse dele (frutas, mundo fisico)"""
        return self.bola is not None or self.frutas or self.fisico is not None


MUNDOS = {
    "padrao": Mundo("padrao", "casado"),
    "bola": Mundo("bola", "casado", "b1b2"),
    "bola_a1": Mundo("bola_a1", "casado", "a1"),
    "casado_frutas": Mundo("casado_frutas", "casado", frutas=True),
    "descasado": Mundo("descasado", "descasado", frutas=True),
    "mutavel": Mundo("mutavel", "mutavel", frutas=True),
    "iguais_frutas": Mundo("iguais_frutas", "iguais", frutas=True),
    # o mundo fisico (PLANO_ANALISE_V2_MUNDO_FISICO, secao 2; PMF-7: o mundo "iguais") e o layout afastado do G-DIST (A1.8)
    "fisico": Mundo("fisico", "iguais", fisico="padrao"),
    "fisico_afastado": Mundo("fisico_afastado", "iguais", fisico="afastado"),
}
LAYOUTS_FISICO = {"padrao": None, "afastado": LAYOUT_MUNDO_AFASTADO}     # None: o layout da ConfigMundo da bancada


def mundo_de(nome: str) -> Mundo:
    if nome in CONDICOES and CONDICOES[nome].precisa:
        c = CONDICOES[nome]
        raise NotImplementedError(f"condicao {nome!r} ({c.descricao}): precisa {c.precisa}")
    if nome not in MUNDOS:
        raise NotImplementedError(f"mundo {nome!r}: so {sorted(MUNDOS)}")
    m = MUNDOS[nome]
    if CONDICOES[m.condicao].precisa:          # pragma: no cover - um mundo registrado so realiza condicao que ja existe
        raise NotImplementedError(m.condicao)
    return m
# corpo (W-BANCADA-CORPO): a quimica da pergunta do plano (secao 1: "a quimica de hoje", CD-3): o corpo com a digestao na taxa C e a
# Vida, sem os drives novos. O regime "corpo" liga por cima os drives novos e os gestos (etapa 6). A chave "corpo" da config troca os
# numeros, nunca as sub-chaves
CONFIG_CORPO_QUIMICA = ConfigCorpo(ligada=True, digestao=True, vida=True)
REGIMES_CORPO = ("hoje", "quimica", "corpo")
SUBCHAVES_CORPO = ("ligada", "digestao", "vida", "drives_novos", "gestos", "metabolismo")
# K4 fora do orcamento (decisao do Matheus, 2026-10-05): a chave liga o motor e a regra do mundo; o julgamento usa elogiar/repreender
CONFIG_JULGAMENTO_FORA = ConfigJulgamentoFruta(ligada=True, no_orcamento=False)
JULGAMENTOS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})


# ------------------------------------------------------------------ as frutas na bancada


def efeitos_da_condicao(genoma, cf: ConfigFrutas, condicao: str) -> dict:
    """O efeito no humor de cada fruta (F6: o ruim no humor, fora de em_privacao). Casado: a de maior preferencia inata faz bem
    (-efeito_humor_ruim) e a de menor faz mal (efeito_humor_ruim); descasado: o mesmo com o sinal trocado; a do meio fica com o
    efeito neutro nos dois. Assim casado e descasado diferem SO no sinal, e os dois tem uma fruta boa e uma ruim."""
    if condicao == "iguais":                       # N7-5: todas com o efeito neutro, como o mundo "iguais" do N4
        return {f: cf.efeito_humor_neutro for f in FRUTAS}
    if cf.efeito_humor_ruim >= 0.0:
        raise ValueError("efeito_humor_ruim precisa ser negativo")
    pref = genoma.preferencia_inata
    maior = genoma.fruta_preferida()
    menor = min(FRUTAS, key=lambda f: (pref[f], FRUTAS.index(f)))
    if maior == menor:
        raise ValueError("preferencias inatas iguais: sem fruta preferida nem rejeitada")
    ruim, bom = cf.efeito_humor_ruim, -cf.efeito_humor_ruim
    if condicao == "casado":
        alto, baixo = bom, ruim
    elif condicao == "descasado":
        alto, baixo = ruim, bom
    else:
        raise ValueError(f"efeitos so de casado, descasado ou iguais, nao {condicao!r}")
    return {f: (alto if f == maior else baixo if f == menor else cf.efeito_humor_neutro) for f in FRUTAS}


class MotorFrutasMundo(MotorFrutas):
    """O MotorFrutas (digilab/frutas.py, que nao muda) com o efeito de cada fruta dado pela CONDICAO do mundo da bancada, no
    lugar do `ConfigFrutas.mundo` do N4. No mutavel o efeito comeca casado e troca para o descasado na primeira decisao em ou
    depois de `tick_troca` (as decisoes caem a cada 15 ticks, entao com tick_troca multiplo de 15 a troca e no tick exato); a
    troca fica em `self.troca` (registro derivado: tick e os efeitos antes e depois) e em cada consumo (o efeito aplicado).
    Nenhuma rng a mais; o replay pelo log refaz tudo."""

    def __init__(self, *a, condicao: str, tick_troca: int | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        if not self.cf.ligada:
            raise ValueError("os mundos das frutas pedem ConfigFrutas.ligada")
        if condicao == "mutavel":
            if tick_troca is None or tick_troca <= 0:
                raise ValueError("o mutavel precisa de tick_troca > 0")
            inicial = "casado"
        elif condicao in ("casado", "descasado", "iguais"):
            if tick_troca is not None:
                raise ValueError(f"so o mutavel troca, nao {condicao!r}")
            inicial = condicao
        else:
            raise ValueError(f"condicao das frutas desconhecida: {condicao!r}")
        self.condicao = condicao
        self.tick_troca = tick_troca
        conds = ("iguais",) if condicao == "iguais" else ("casado", "descasado")
        self._efeitos = {c: efeitos_da_condicao(self.genoma, self.cf, c) for c in conds}
        self.efeito_vigente = inicial
        self.efeito_humor = dict(self._efeitos[inicial])
        self.troca: dict | None = None

    def _frutas_na_proxima_decisao(self) -> float:
        t = self._estado.tick
        if self.condicao == "mutavel" and self.troca is None and t >= self.tick_troca:
            antes = dict(self.efeito_humor)
            self.efeito_vigente = "descasado"
            self.efeito_humor = dict(self._efeitos["descasado"])
            self.troca = {"tick": t, "tick_troca": self.tick_troca, "de": "casado", "para": "descasado",
                          "efeito_antes": antes, "efeito_depois": dict(self.efeito_humor)}
        return super()._frutas_na_proxima_decisao()

    def resumo_mundo(self) -> dict:
        return {"condicao": self.condicao, "tick_troca": self.tick_troca, "efeito_vigente": self.efeito_vigente,
                "efeitos": {c: dict(e) for c, e in self._efeitos.items()}, "troca": self.troca}


class CalendarioFrutas:
    """As ofertas de fruta do experimento maior (plano, secao 2; K5): saem da SEMENTE, nao do estado do pet nem do braco, entao o
    mesmo pet ve as mesmas frutas nos mesmos ticks em qualquer braco e condicao. Nos horarios fixos do N4
    (`ConfigFrutas.horarios_oferta`), todo dia, o proximo conjunto da `rotacao_ofertas`, comecando no indice
    derivar_semente("calendario-frutas", semente) % len(rotacao). Diferente do OfertasFrutas do N4, oferece com o pet dormindo
    tambem (a fruta fica no cenario ate o prazo): olhar o sono faria a oferta depender do estado. Regra do mundo da bancada:
    fora do orcamento e fora do sorteio do dono aleatorio (B1, B2), igual para todo dono."""

    def __init__(self, semente: int, cf: ConfigFrutas) -> None:
        self.cf = cf
        self.k = derivar_semente("calendario-frutas", semente) % len(cf.rotacao_ofertas)

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        if visao.estado["tick"] % TICKS_POR_DIA not in self.cf.horarios_oferta:
            return []
        conjunto = self.cf.rotacao_ofertas[self.k % len(self.cf.rotacao_ofertas)]
        self.k += 1
        return [oferta_de(f) for f in conjunto]
