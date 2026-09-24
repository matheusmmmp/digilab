"""Motivo unificado de decisao, para vida e combate (Parte A).

Somente leitura: calcular um motivo nao consome rng, nao muda estado de
politica nem decisao nenhuma. O motivo e registro estruturado produzido pela
propria decisao; a expressao (expressao.py) so pode mostrar menos do que ele.

Vida
  - PoliticaBandit: usa os pesos AMOSTRADOS que decidiram (ultima_decisao).
    contribuicao_i = x_i * (theta~_escolhida_i - media dos theta~_i das outras).
    So vira fator uma contribuicao POSITIVA (a favor da acao escolhida) e
    >= limiar_motivo, e so se o termo de valor MUDOU a escolha: se sem ele o
    argmax de log(prior) + Gumbel ja daria a mesma acao, quem decidiu foi o
    prior/ruido e o motivo fica sem fator (ver docs/REGISTRO_DESVIOS.md).
  - PoliticaInstinto: a regra que disparou (ultima_regra).
  Captura: PoliticaComMotivo embrulha a politica e le o registro depois de
  cada agir(); delega tudo o mais sem alterar nada.

Combate
  Adaptador do motivo que o combate V2 ja grava no log (indice da regra,
  "exploracao", "pesado_automatico", "oraculo"). Nao altera combate_v2/.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Sequence

from .config import CONFIG_EXPRESSAO, ConfigExpressao
from .events import AcaoPet, AcaoUsuario, LogDeEventos
from .policy import Observacao, Politica, PoliticaInstinto, Transicao

ORIGENS = ("vida", "combate")

# nome do fator por indice de feature do bandit (policies/bandit.features)
FATOR_DA_FEATURE = (
    "habito", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo",
    "hora", "hora", "tempo_sem_cuidado",
)
FATORES_VIDA = tuple(dict.fromkeys(FATOR_DA_FEATURE))

# regra do instinto -> fatores (variaveis da condicao que disparou)
_FATORES_INSTINTO = {
    "sono_exaustao": ("energia",),
    "sono_continuar": ("dormindo", "energia"),
    "sono_noite": ("hora", "energia"),
    "fome_moderada": ("fome",),
    "tempo_livre": (),          # sorteio ponderado sem condicao: nao ha causa a citar
}


@dataclass(frozen=True)
class Motivo:
    origem: str
    acao: str
    fatores: tuple[str, ...]
    evento_ref: tuple[int, ...]
    intensidade: float | None
    exploracao: bool
    tick: int | None = None      # vida
    turno: int | None = None     # combate

    def __post_init__(self) -> None:
        if self.origem not in ORIGENS:
            raise ValueError(f"origem invalida: {self.origem!r}")
        if len(self.fatores) > 2:
            raise ValueError(f"no maximo 2 fatores, veio {self.fatores}")
        if (self.tick is None) == (self.turno is None):
            raise ValueError("motivo precisa de tick (vida) OU turno (combate)")
        if self.origem == "vida":
            if self.tick is None or self.intensidade is None or not 0.0 <= self.intensidade <= 1.0:
                raise ValueError(f"motivo de vida precisa de tick e intensidade em [0,1]: {self}")
        else:
            if self.turno is None or self.intensidade is not None:
                raise ValueError(f"motivo de combate precisa de turno e intensidade None: {self}")
        if self.exploracao and self.fatores:
            raise ValueError("exploracao nao tem fator")

    def para_dict(self) -> dict:
        return {
            "origem": self.origem, "tick": self.tick, "turno": self.turno, "acao": self.acao,
            "fatores": list(self.fatores), "evento_ref": list(self.evento_ref),
            "intensidade": self.intensidade, "exploracao": self.exploracao,
        }


# ================================================================ vida


def motivo_bandit(decisao: dict, tick: int, ref_ultimo_cuidado: int | None,
                  cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> tuple[Motivo, dict]:
    """(Motivo, diagnostico). Funcao pura do registro da decisao."""
    x, escolhida = decisao["x"], decisao["acao"]
    amostras = decisao["amostras"]
    outras = [a for a in amostras if a is not escolhida]
    contrib: dict[str, float] = {}
    for i, xi in enumerate(x):
        media = sum(amostras[a][i] for a in outras) / len(outras)
        nome = FATOR_DA_FEATURE[i]
        contrib[nome] = contrib.get(nome, 0.0) + xi * (amostras[escolhida][i] - media)

    sem_valor = {a: decisao["log_prior"][a] + decisao["gumbel"][a] for a in amostras}
    argmax_sem_valor = max(sem_valor, key=lambda a: (sem_valor[a], -list(amostras).index(a)))
    valor_decidiu = argmax_sem_valor is not escolhida

    positivos = sorted(((c, n) for n, c in contrib.items() if c >= cfg.limiar_motivo), reverse=True)
    maior_abs = max(contrib.items(), key=lambda kv: abs(kv[1]))
    fatores = tuple(n for _, n in positivos[:2]) if valor_decidiu else ()
    soma_pos = sum(c for c in contrib.values() if c > 0)
    intensidade = (positivos[0][0] / soma_pos) if fatores and soma_pos > 0 else 0.0
    refs = (ref_ultimo_cuidado,) if "tempo_sem_cuidado" in fatores and ref_ultimo_cuidado is not None else ()
    diag = {
        "valor_decidiu": valor_decidiu,
        # formula literal da tarefa (maior |contribuicao| >= limiar), sem as checagens de honestidade
        "fator_formula_literal": maior_abs[0] if abs(maior_abs[1]) >= cfg.limiar_motivo else None,
    }
    return Motivo("vida", escolhida.value, fatores, refs, min(1.0, intensidade), False, tick=tick), diag


def motivo_instinto(regra: str, obs: Observacao, acao: AcaoPet, tick: int, ref_ultimo_cuidado: int | None,
                    cfg_instinto=None) -> Motivo:
    fome, higiene, energia, humor, *_ = obs.vetor_estado
    if regra == "pedido_necessidade":
        fatores = tuple(n for n, v in (("fome", fome), ("higiene", higiene)) if v < 0.25)
        intensidade = 1.0
    elif regra == "abandono":
        fatores = ("tempo_sem_cuidado", "humor") if acao is AcaoPet.EMBURRAR else ("tempo_sem_cuidado",)
        intensidade = 1.0
    elif regra == "fome_moderada":
        fatores, intensidade = _FATORES_INSTINTO[regra], 0.5
    elif regra == "tempo_livre":
        pesos = {AcaoPet.OCIOSO: 3.0, AcaoPet.EXPLORAR: 2.0 + 2.0 * energia,
                 AcaoPet.BRINCAR: 1.0 + 3.0 * humor, AcaoPet.CHAMAR_ATENCAO: 1.0}
        fatores, intensidade = (), pesos[acao] / sum(pesos.values())
    elif regra in _FATORES_INSTINTO:
        fatores, intensidade = _FATORES_INSTINTO[regra], 1.0
    else:
        raise ValueError(f"regra do instinto desconhecida: {regra!r}")
    refs = (ref_ultimo_cuidado,) if "tempo_sem_cuidado" in fatores and ref_ultimo_cuidado is not None else ()
    return Motivo("vida", acao.value, fatores, refs, intensidade, False, tick=tick)


class PoliticaComMotivo:
    """Embrulha uma politica de vida e registra o motivo de cada decisao.

    Delega agir/observar/estado_interno/receber_acao_dono sem alterar nada: as
    mesmas chamadas, na mesma ordem, com a mesma rng. `indices_dono[k]` = indice
    no log do k-esimo evento de acao do dono (para evento_ref); opcional.
    """

    def __init__(self, interna: Politica, indices_dono: Sequence[int] | None = None,
                 cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> None:
        self.interna = interna
        self.nome = interna.nome
        self.cfg = cfg
        self._indices_dono = list(indices_dono) if indices_dono is not None else None
        self._n_dono = 0
        self._tick_ultimo_cuidado = 0
        self.motivos: list[Motivo] = []
        self.diagnosticos: list[dict] = []
        self.humores: list[float] = []   # humor observado em cada decisao (emote do bebe)

    def _ref_cuidado(self) -> int | None:
        if self._indices_dono is None or self._n_dono == 0:
            return None
        return self._indices_dono[self._n_dono - 1]

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        acao = self.interna.agir(obs, rng)
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        if isinstance(self.interna, PoliticaInstinto):
            m = motivo_instinto(self.interna.ultima_regra, obs, acao, tick, self._ref_cuidado())
            diag = {"valor_decidiu": None, "fator_formula_literal": None}
        elif hasattr(self.interna, "ultima_decisao"):
            dec = self.interna.ultima_decisao
            if dec is None or dec["acao"] is not acao:
                raise RuntimeError("registro da decisao do bandit nao corresponde a acao devolvida")
            m, diag = motivo_bandit(dec, tick, self._ref_cuidado(), self.cfg)
        else:
            raise TypeError(f"politica sem registro de decisao: {type(self.interna).__name__}")
        self.motivos.append(m)
        self.diagnosticos.append(diag)
        self.humores.append(obs.vetor_estado[3])
        return acao

    def observar(self, transicao: Transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self._tick_ultimo_cuidado = tick
        self._n_dono += 1
        f = getattr(self.interna, "receber_acao_dono", None)
        if f is not None:
            f(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()


def indices_eventos_dono(log: LogDeEventos) -> list[int]:
    return [i for i, e in enumerate(log) if e.tipo == "acao_usuario"]


def motivos_de_vida(log: LogDeEventos, fabrica: Callable, semente: int, cfg: ConfigExpressao = CONFIG_EXPRESSAO):
    """Reproduz a vida do log com o embrulho; devolve (motor, PoliticaComMotivo)."""
    from .treino import reproduzir_com_feedback

    indices = indices_eventos_dono(log)
    embrulho: list[PoliticaComMotivo] = []

    def fab(c):
        p = PoliticaComMotivo(fabrica(c), indices, cfg)
        embrulho.append(p)
        return p

    motor = reproduzir_com_feedback(log, fab, semente=semente)
    return motor, embrulho[0]


# ================================================================ combate


def nome_condicao(c) -> str:
    """'nome' ou 'nome(p1,p2)' com distancia/acao pelo rotulo."""
    if not c.params:
        return c.nome
    partes = []
    for p in c.params:
        partes.append(getattr(p, "rotulo", None) or getattr(p, "value", p))
    return f"{c.nome}({','.join(str(x) for x in partes)})"


def nome_base(fator: str) -> str:
    return fator.split("(", 1)[0]


def _refs_condicao(c, turno: int, historico_op: tuple) -> tuple[int, ...]:
    """Turnos do log (1-based, campo 't') que sustentam a condicao na decisao do turno `turno`."""
    n = c.nome
    if n == "sempre":
        return ()
    if n == "oponente_preparando":
        return (turno - 1,)
    if n == "oponente_repete":
        _, k = c.params
        return tuple(range(turno - k, turno))
    if n == "oponente_frequente":
        janela = 5
        ini = max(1, turno - janela)
        return tuple(t for t in range(ini, turno) if historico_op[t - 1] is c.params[0])
    return (turno,)  # condicao de estado (hp, guts, distancia): turno corrente


def regra_do_motivo(estilo, motivo_log):
    """Regra de gambits indicada por um motivo inteiro do log (ou None)."""
    if not isinstance(motivo_log, int):
        return None
    g = estilo.gambits
    return g.regras[motivo_log] if motivo_log < len(g.regras) else g.final


def motivos_de_partida(log: list[dict], lutadores, cfg=None) -> list[tuple[int, int, Motivo, object]]:
    """[(turno, lado, Motivo, estado_antes_da_decisao)] reproduzindo a partida pelo log.

    `lutadores` = (Lutador_a, Lutador_b) do combate V2. Evento desconhecido levanta erro.
    """
    from .combate_v2.regras import Acao, estado_inicial, resolver

    a, b = lutadores
    estado = estado_inicial((a.condicao.hp_max, b.condicao.hp_max),
                            (a.condicao.guts_inicial, b.condicao.guts_inicial),
                            (a.condicao.regen_guts, b.condicao.regen_guts))
    saida = []
    for ev in log:
        tipo = ev.get("tipo")
        if tipo in ("cabecalho", "fim"):
            continue
        if tipo != "turno":
            raise ValueError(f"evento desconhecido no log de combate: {tipo!r}")
        t = ev["t"]
        for lado, (acao, m) in enumerate(((ev["a"], ev["ma"]), (ev["b"], ev["mb"]))):
            estilo = (a, b)[lado].estilo
            hist_op = estado.oponente(lado).historico
            if m == "exploracao":
                mot = Motivo("combate", acao, (), (), None, True, turno=t)
            elif m == "pesado_automatico":
                mot = Motivo("combate", acao, (), (t - 1,), None, False, turno=t)
            elif m == "oraculo":
                mot = Motivo("combate", acao, (), (), None, False, turno=t)
            elif isinstance(m, int):
                regra = regra_do_motivo(estilo, m)
                conds = [c for c in regra.condicoes if c.nome != "sempre"]
                refs = sorted({r for c in conds for r in _refs_condicao(c, t, hist_op)})
                mot = Motivo("combate", acao, tuple(nome_condicao(c) for c in conds), tuple(refs),
                             None, False, turno=t)
            else:
                raise ValueError(f"motivo de combate desconhecido: {m!r}")
            saida.append((t, lado, mot, estado))
        estado, _ = resolver(estado, Acao(ev["a"]), Acao(ev["b"]), cfg)
    return saida
