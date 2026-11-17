"""As vidas do ELOGIO (docs/TAREFA_V3_ELOGIO.md, secoes 4 e 9; etapa 2, so a montagem): o DigiBrain modular do braco REL, o corpo da etapa 6
com os gestos, o mundo com as arvores e a condicao `casado` (D-EL-9: o efeito de cada fruta no humor pela preferencia inata do genoma das
frutas da semente), o dono atencioso com o lugar `comedouro` e o carinho do `DonoElogioFruta` pelo gancho `carinho` do
`simular_vida_fisico`, fora do orcamento e como contato (D-EL-10).

Os bracos (secao 4):
  - `E0`: so a consequencia natural (nenhum carinho);
  - `E-imed`: um carinho no primeiro passo do dono depois de cada consumo da fruta X;
  - `E-atraso`: o mesmo carinho, com o atraso sorteado entre 1, 3 e 6 passos do dono (D-EL-5; 1 e o do E-imed);
  - `E-sorteado`: o controle principal, os passos dados de fora (o mesmo numero de carinhos do E-imed da mesma unidade, sorteados por
    `passos_sorteados`, rng propria), sem olhar o consumo;
  - `E-incons`: o E-imed com 20 % dos carinhos levados ao consumo seguinte de outra fruta e 10 % levados ao passo seguinte em que o pet vai
    comer X e ainda nao comeu (o elogio antecipado; D-EL-6).
O carinho contingente vai so na primeira metade da vida (D-EL-7: a M3, a retencao, le a segunda); o do sorteado tambem.

A fruta X sai por vida de `derivar_semente("elogio-fruta", semente)`, uniforme entre as tres (secao 4). Cada fluxo novo tem a sua rng
(`elogio-atraso`, `elogio-incons`, `elogio-sorteado`), e nenhuma toca o mundo nem o cerebro. O dono ve o pet comer pelos consumos do motor
(`consumos_mundo`) e ve aonde ele vai pelo alvo pendente do motor: so le.

Sem metricas aqui: as medidas M1 a M4 entram no `digilab/metrics.py` com o plano de analise (etapa 3)."""
from __future__ import annotations

import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.mundos import efeitos_da_condicao  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_DONOS, CONFIG_ELOGIO, CONFIG_FRUTAS, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            TICKS_POR_DIA, ConfigElogio)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.frutas import genoma_frutas  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

BRACOS = ("E0", "E-imed", "E-atraso", "E-sorteado", "E-incons")
ATRASOS = (1, 3, 6)                                     # D-EL-5, em passos do dono (1 = o primeiro passo depois do consumo)
FRACAO_OUTRA, FRACAO_ANTES = 0.2, 0.1                   # D-EL-6
DONO, LUGAR = "atencioso", "comedouro"
CM = CONFIG_MUNDO_LIGADA
CONDICAO = "casado"                                     # D-EL-9


def fruta_elogio(semente: int) -> str:
    """a fruta X da vida (secao 4): uniforme entre as tres, rng propria, sem olhar a preferencia"""
    rng = random.Random(derivar_semente("elogio-fruta", semente))
    return FRUTAS[rng.randrange(len(FRUTAS))]


def passos_da_vida(dias: int) -> int:
    total = dias * TICKS_POR_DIA
    if total % CONFIG_DONOS.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    return total // CONFIG_DONOS.passo_ticks


def passos_sorteados(n: int, ate_passo: int, semente: int) -> list[int]:
    """o E-sorteado: `n` passos (com repeticao) sorteados uniformes em [0, ate_passo), rng propria, sem olhar o consumo"""
    if n < 0 or ate_passo < 1:
        raise ValueError(f"n {n} e ate_passo {ate_passo}")
    rng = random.Random(derivar_semente("elogio-sorteado", semente))
    return sorted(rng.randrange(ate_passo) for _ in range(n))


class DonoElogioFruta:
    """O carinho dos bracos (a docstring do modulo), pelo gancho `carinho` do simular_vida_fisico: `acoes(estado)` uma vez por passo,
    depois das acoes do dono. O motor chega pela fabrica (`motor`), so para ler os consumos e o alvo pendente. `carinhos` guarda
    (passo, o porque: imed, atraso, outra, antes ou sorteado)."""

    def __init__(self, braco: str, fruta: str, semente: int, ate_passo: int, sorteados: list[int] | None = None) -> None:
        if braco not in BRACOS:
            raise ValueError(f"braco {braco!r}: so {BRACOS}")
        if fruta not in FRUTAS:
            raise ValueError(f"fruta {fruta!r}: so {FRUTAS}")
        if (braco == "E-sorteado") != (sorteados is not None):
            raise ValueError("os passos sorteados existem so no E-sorteado, e la sao obrigatorios")
        self.braco = braco
        self.fruta = fruta
        self.ate_passo = ate_passo
        self.motor = None
        self.passo = -1
        self._vistos = 0
        self._agenda: dict[int, list[str]] = {}       # passo -> os porques dos carinhos marcados para ele
        for p in sorteados or ():
            self._agenda.setdefault(p, []).append("sorteado")
        self._outra = 0                               # E-incons: carinhos esperando o consumo de outra fruta
        self._antes = 0                               # E-incons: carinhos esperando o pet ir comer X
        self.rng_atraso = random.Random(derivar_semente("elogio-atraso", semente))
        self.rng_incons = random.Random(derivar_semente("elogio-incons", semente))
        self.carinhos: list[tuple[int, str]] = []
        self.consumos_x = 0

    def _indo_comer_x(self) -> bool:
        pend = self.motor._pendente
        if pend is None or pend["acao"] is not AcaoPet.COMER or pend["alvo"].objeto() != "comida":
            return False
        c = self.motor.mundo.comidas.get(pend["alvo"].id)
        return c is not None and c["tipo"] == self.fruta

    def acoes(self, estado: dict) -> list:
        if self.motor is None:
            raise RuntimeError("o DonoElogioFruta sem o motor (a fabrica o entrega)")
        self.passo += 1
        consumos = self.motor.consumos_mundo
        if len(consumos) < self._vistos:
            raise RuntimeError(f"consumos voltaram atras: {self._vistos} -> {len(consumos)}")
        novos, self._vistos = consumos[self._vistos:], len(consumos)
        de_x = sum(1 for c in novos if c["tipo"] == self.fruta)
        de_outra = sum(1 for c in novos if c["tipo"] in FRUTAS and c["tipo"] != self.fruta)
        self.consumos_x += de_x
        agora = list(self._agenda.pop(self.passo, []))
        contingente = self.passo < self.ate_passo
        if contingente and self.braco in ("E-imed", "E-atraso", "E-incons"):
            for _ in range(de_x):
                if self.braco == "E-imed":
                    agora.append("imed")
                elif self.braco == "E-atraso":
                    d = ATRASOS[self.rng_atraso.randrange(len(ATRASOS))]
                    if d == 1:
                        agora.append("atraso")
                    else:
                        self._agenda.setdefault(self.passo + d - 1, []).append("atraso")
                else:
                    u = self.rng_incons.random()
                    if u < FRACAO_OUTRA:
                        self._outra += 1
                    elif u < FRACAO_OUTRA + FRACAO_ANTES:
                        self._antes += 1
                    else:
                        agora.append("imed")
        if self.braco == "E-incons" and contingente:
            if self._outra and de_outra:
                agora.extend(["outra"] * self._outra)
                self._outra = 0
            if self._antes and self._indo_comer_x():
                agora.extend(["antes"] * self._antes)
                self._antes = 0
        if not contingente and self.braco != "E-sorteado":
            agora = [x for x in agora if x == "sorteado"]   # o contingente para na metade: o atraso marcado para depois cai
        self.carinhos.extend((self.passo, x) for x in agora)
        return [AcaoUsuario.ACARICIAR] * len(agora)


def fabricas(semente: int, cfg_elogio: ConfigElogio, dono: DonoElogioFruta | None):
    """(a fabrica do cerebro, a do motor) da vida; a do motor entrega o motor ao dono do carinho"""
    efeito = efeitos_da_condicao(genoma_frutas(semente, CONFIG_FRUTAS), CONFIG_FRUTAS, CONDICAO)
    cd = orq.config_do_braco("REL", None, True)

    def fp(cfg=None):
        return orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, CM, semente=semente, cfg_elogio=cfg_elogio), orq.CONFIG_DIGIBRAIN_INATOS.escala)

    def fm(politica, cfg, s):
        motor = com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CM,
                                      cfg_corpo=CONFIG_CORPO_DRIVES, efeito_frutas=efeito)
        if dono is not None and dono.motor is None:   # so a vida; o replay monta outro motor e nao o entrega
            dono.motor = motor
        return motor

    return fp, fm


def viver(braco: str, semente: int, dias: int, cfg_elogio: ConfigElogio = CONFIG_ELOGIO, sorteados: list[int] | None = None):
    """uma vida do braco: (o motor, o cerebro, o dono do carinho ou None no E0, as fabricas)"""
    passos = passos_da_vida(dias)
    dono = None if braco == "E0" else DonoElogioFruta(braco, fruta_elogio(semente), semente, passos // 2, sorteados)
    fp, fm = fabricas(semente, cfg_elogio, dono)
    registro = fp(CONFIG_PADRAO)
    motor, _ = simular_vida_fisico(DonoComLugar(criar_dono(DONO), LUGAR, semente, DONO, CM), registro, semente, dias,
                                   orq.ORCAMENTO_POR_DIA * dias, DONO, fm, carinho=dono)
    return motor, orq.cerebro_de(registro), dono, (fp, fm)


def viver_par(semente: int, dias: int, cfg_elogio: ConfigElogio = CONFIG_ELOGIO):
    """o E-imed e o E-sorteado da mesma unidade: o sorteado com o mesmo numero de carinhos, nos passos de `passos_sorteados`"""
    imed = viver("E-imed", semente, dias, cfg_elogio)
    n = len(imed[2].carinhos)
    sorteado = viver("E-sorteado", semente, dias, cfg_elogio, passos_sorteados(n, passos_da_vida(dias) // 2, semente))
    return imed, sorteado
