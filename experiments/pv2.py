"""As vidas do PV-2 (docs/PLANO_ANALISE_V3_PET_VIVO_PV2.md, secoes 3 e 4; docs/futuro/integracao_cadeia_digibrain.md, secao 8): o REL das
fases do conserto (o cerebro dos ovos, como na C4), o corpo do v11 da bancada, o mundo do MVP e os lugares da C4, com o braco:
  - HOJE: o REL de hoje, com o oraculo do mundo (a referencia descritiva);
  - OLF-0, OLF-DC, OLF-DCV, OLF-PLA, OLF-G: o orgao do Olfato da comida ligado no corpo (duas narinas, DP-13; o mundo deixa de mandar a
    direcao) e a ConfigPV2 ligada no cerebro, com o braco.

So montagem das vidas, o replay (G1) e as medidas de uma vida. Nenhuma run: a run do PV-2 pede o adendo e a faixa (o plano, secao 4).
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (BRACOS_PV2, CONFIG_LANCE_DONO_LIGADA, CONFIG_PADRAO, CONFIG_PV2, CONFIG_SONO_SEGURA_LIGADA,  # noqa: E402
                            ConfigEquilibrioCuidado, ConfigOlfato, ConfigPV2, inatos_e1)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import medidas_pv2  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

BRACOS = ("HOJE",) + BRACOS_PV2
OLFATO = ConfigOlfato(ligada=True, comida=True, narinas=2)     # o orgao do DP-13, com os valores da config
# a checagem do v38 (INT-8; o adendo 2 do plano, A2.3): o que o Python tem do pet do jogo, como no gabarito do EQUILIBRIO_CUIDADO
# (exportar_gabarito_digibrain_modular.equilibrio_cuidado): os inatos do E1, o sono que segura, o lance do dono, as duas regras do E1 e o
# bebe nas primeiras K_BEBE decisoes. O olhar (o orgao da visao) fica de fora.
EQUILIBRIO_V38 = ConfigEquilibrioCuidado(guarda_fome_brincar=True, comer_bebe=True)
K_BEBE = 96                                                     # o 1o dia, como o K_BEBE do gabarito do E1


def bebe_pelas_decisoes(cerebro) -> None:
    """o embrulho do `agir` do v38: o gancho `estagio_bebe` com o pet bebe nas primeiras K_BEBE decisoes (o do gabarito do E1)"""
    agir = cerebro.agir

    def com_estagio(obs, rng):
        cerebro.estagio_bebe(cerebro.k < K_BEBE)
        return agir(obs, rng)
    cerebro.agir = com_estagio


def config_pv2(braco: str, base: ConfigPV2 | None = None) -> ConfigPV2 | None:
    """a ConfigPV2 do braco (None no HOJE): a `base` (os numeros do mecanismo; a de hoje, CONFIG_PV2) ligada, com o braco"""
    if braco == "HOJE":
        return None
    if braco not in BRACOS_PV2:
        raise ValueError(f"braco do PV-2 {braco!r}: so {BRACOS}")
    return replace(base or CONFIG_PV2, ligada=True, braco=braco)


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, base: ConfigPV2 | None = None, v38: bool = False):
    """(a fabrica do cerebro, a do motor) da vida, como `orq.fabricas` do REL, com o orgao e a ConfigPV2 nos bracos OLF-*; com `v38`, as
    chaves do pet do jogo que o Python tem (EQUILIBRIO_V38 e vizinhos), no cerebro e, o lance, no motor"""
    b = orq.bancada(dias, orcamento_por_dia)
    cc = b.cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))
    cd = orq.config_do_braco("REL", None, True)
    cp = config_pv2(braco, base)
    kw_motor = {} if cp is None else {"cfg_olfato": OLFATO}
    kw_cerebro = {} if cp is None else {"cfg_pv2": cp, "cfg_olfato": OLFATO}
    if v38:
        kw_motor["cfg_lance_dono"] = CONFIG_LANCE_DONO_LIGADA
        kw_cerebro.update(inatos=inatos_e1(), cfg_sono=CONFIG_SONO_SEGURA_LIGADA, cfg_lance=CONFIG_LANCE_DONO_LIGADA,
                          cfg_equilibrio=EQUILIBRIO_V38)

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc,
                                     **kw_motor)

    def fp(cfg=None):
        registro = orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, orq.CM, semente=semente, **kw_cerebro), orq.CONFIG_DIGIBRAIN_INATOS.escala)
        if v38:                                   # na fabrica, para o replay do G1 ter o mesmo bebe
            bebe_pelas_decisoes(orq.cerebro_de(registro))
        return registro

    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int = orq.ORCAMENTO_POR_DIA,
          base: ConfigPV2 | None = None, v38: bool = False, ao_montar=None):
    """uma vida: (o motor, o registro, as fabricas). `ao_montar(cerebro)` roda antes da vida (o leitor da SE-C)"""
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia, base, v38)
    registro = fp(CONFIG_PADRAO)
    if ao_montar is not None:
        ao_montar(orq.cerebro_de(registro))
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm)


def medir(braco: str, dono: str, lugar: str, semente: int, dias: int, base: ConfigPV2 | None = None, replay: bool = True) -> dict:
    """as medidas de uma vida (o `medidas_pv2` do metrics.py), com o G1 do replay conferido antes (falha alto)"""
    motor, registro, fab = viver(braco, dono, lugar, semente, dias, base=base)
    if replay:
        orq.conferir_replay(motor, fab, semente, motor.log.para_jsonl())
    cerebro = orq.cerebro_de(registro)
    return {"braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "dias": dias,
            **medidas_pv2(cerebro.motivos, motor.consumos_mundo, braco != "HOJE", cerebro.S)}
