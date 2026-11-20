"""As vidas do teste de recompensa (docs/PLANO_ANALISE_V3_PET_VIVO_RECOMPENSA.md, APROVADO; secao 3): o pet do v38 (`pv2.fabricas`
com `v38=True`), os donos e os lugares da C4, e um carinho a mais do dono pelo gancho `carinho` do `simular_vida_fisico`, fora do
orcamento, como no ELOGIO (D-EL-10). Nada muda no cerebro, no corpo nem no motor.

Os bracos (RC-4):
  - `R0`: nenhum carinho a mais, a ConfigElogio desligada (o pet de hoje);
  - `R-CORPO`: um carinho no passo do dono seguinte a cada decisao de comer ou de brincar, a ConfigElogio desligada (so o corpo);
  - `R-CB`: o mesmo carinho, a ConfigElogio ligada com g = 2S e W = 1 (RC-3);
  - `R-SORT`: o mesmo numero de carinhos do R-CB da mesma unidade e celula, em passos sorteados (rng propria,
    `recompensa-sorteado`), a ConfigElogio ligada.

O dono do carinho so le o que o pet decidiu (`motivos` do cerebro, entregue pela fabrica). O passo do dono e o da decisao sao iguais:
no passo p ele ve a decisao p, e o carinho dele credita essa decisao com W = 1 (a C-HORA do orquestrador confere). O rastro
(`ConfigRastro`, so leitura) fica ligado em todo braco, para as medidas do caminho do sono; a vida sai igual com ele ou sem.

Sem metricas aqui: as medidas ficam no `digilab/metrics.py`."""
from __future__ import annotations

import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import pv2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_DONOS, CONFIG_PADRAO, CONFIG_RASTRO_LIGADA, TICKS_POR_DIA, ConfigElogio  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

BRACOS = ("R0", "R-CORPO", "R-CB", "R-SORT")
COM_CREDITO = ("R-CB", "R-SORT")                         # os bracos com a ConfigElogio ligada
NA_HORA = ("R-CORPO", "R-CB")                            # os bracos com o carinho depois do comer e do brincar
ALVOS = ("comer", "brincar")                             # a pergunta do plano (RC-1)
GANHO = 2 * CONFIG_DIGIBRAIN_INATOS.escala               # RC-3: g = 2S, o topo da grade do ELOGIO (D-EL-8); PROPOSTO, SEM FONTE
JANELA = 1                                               # RC-3: W = 1, a decisao recompensada e a ultima
ELOGIO = ConfigElogio(ligada=True, ganho=GANHO, janela=JANELA)
RASTRO = {"cfg_rastro": CONFIG_RASTRO_LIGADA}


def passos_da_vida(dias: int) -> int:
    total = dias * TICKS_POR_DIA
    if total % CONFIG_DONOS.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    if CONFIG_DONOS.passo_ticks != CONFIG_PADRAO.intervalo_decisao_ticks:
        raise RuntimeError("o passo do dono e o da decisao diferem: o carinho no passo seguinte nao e o da decisao (secao 1 do plano)")
    return total // CONFIG_DONOS.passo_ticks


def passos_sorteados(n: int, passos: int, semente: int) -> list[int]:
    """o R-SORT: `n` passos (com repeticao) sorteados uniformes em [0, passos), rng propria, sem olhar o pet"""
    if n < 0 or passos < 1:
        raise ValueError(f"n {n} e passos {passos}")
    rng = random.Random(derivar_semente("recompensa-sorteado", semente))
    return sorted(rng.randrange(passos) for _ in range(n))


class DonoRecompensa:
    """O carinho a mais (a docstring do modulo), pelo gancho `carinho`: `acoes(estado)` uma vez por passo, depois das acoes do dono.
    O cerebro chega pela fabrica (`cerebro`), so para ler as decisoes. `carinhos` guarda (passo, a decisao recompensada ou None no
    R-SORT)."""

    def __init__(self, braco: str, sorteados: list[int] | None = None) -> None:
        if braco not in BRACOS or braco == "R0":
            raise ValueError(f"braco {braco!r}: o carinho a mais so em {BRACOS[1:]}")
        if (braco == "R-SORT") != (sorteados is not None):
            raise ValueError("os passos sorteados existem so no R-SORT, e la sao obrigatorios")
        self.braco = braco
        self.cerebro = None
        self.passo = -1
        self._vistos = 0
        self._agenda: dict[int, int] = {}
        for p in sorteados or ():
            self._agenda[p] = self._agenda.get(p, 0) + 1
        self.carinhos: list[tuple[int, int | None]] = []

    def acoes(self, estado: dict) -> list:
        if self.cerebro is None:
            raise RuntimeError("o DonoRecompensa sem o cerebro (a fabrica o entrega)")
        self.passo += 1
        motivos = self.cerebro.motivos
        if len(motivos) < self._vistos:
            raise RuntimeError(f"as decisoes voltaram atras: {self._vistos} -> {len(motivos)}")
        novas = list(range(self._vistos, len(motivos)))
        self._vistos = len(motivos)
        if self.braco == "R-SORT":
            agora = [None] * self._agenda.pop(self.passo, 0)
        else:
            agora = [k for k in novas if motivos[k]["escolha"][0] in ALVOS]
        self.carinhos.extend((self.passo, k) for k in agora)
        return [AcaoUsuario.ACARICIAR] * len(agora)


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int = orq.ORCAMENTO_POR_DIA):
    """(a fabrica do cerebro, a do motor) do braco: o v38 do PV-2, com o rastro e, nos bracos com credito, a ConfigElogio do plano"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    extra = dict(RASTRO)
    if braco in COM_CREDITO:
        extra["cfg_elogio"] = ELOGIO
    return pv2.fabricas("HOJE", dono, semente, dias, orcamento_por_dia, None, True, extra_cerebro=extra)


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int = orq.ORCAMENTO_POR_DIA,
          sorteados: list[int] | None = None) -> dict:
    """uma vida do braco: o motor, o registro, o cerebro, o dono do carinho (None no R0) e as fabricas"""
    passos_da_vida(dias)
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia)
    registro = fp(CONFIG_PADRAO)
    cerebro = orq.cerebro_de(registro)
    carinho = None
    if braco != "R0":
        carinho = DonoRecompensa(braco, sorteados)
        carinho.cerebro = cerebro
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm, carinho=carinho)
    return {"motor": motor, "registro": registro, "cerebro": cerebro, "dono": carinho, "fabricas": (fp, fm)}


def viver_celula(dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int = orq.ORCAMENTO_POR_DIA) -> dict:
    """os quatro bracos da unidade na celula, na ordem: o R-SORT vem depois do R-CB, com o mesmo numero de carinhos a mais"""
    out = {b: viver(b, dono, lugar, semente, dias, orcamento_por_dia) for b in ("R0", "R-CORPO", "R-CB")}
    sorteados = passos_sorteados(len(out["R-CB"]["dono"].carinhos), passos_da_vida(dias), semente)
    out["R-SORT"] = viver("R-SORT", dono, lugar, semente, dias, orcamento_por_dia, sorteados)
    return out
