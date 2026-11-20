"""Gabarito do SOCIAL_PAR M2 (docs/ESPEC_SOCIAL_PAR_M2.md, secoes 5 e 6): as vidas de hoje do pet do jogo da S, sozinho, no par da S3 e num
grupo em que o B entra no dia 1, gravadas com o codigo de ANTES da `ConfigCompanhia`, num commit proprio. Com a companhia desligada, estas
vidas tem de sair iguais, byte a byte (o G2); com ela ligada, o pet sozinho tambem (o G2b).

As vidas (so as sementes dos testes):
  - `sozinho|<semente>`: o pet sozinho no mundo do laboratorio, com o dono `atencioso` no comedouro, 3 dias;
  - `par|<braco>|<semente>`: a vida VIVO do par da S3 (C ou B1), 5 dias;
  - `entrada|<semente>`: o grupo de dois pets do jogo da S, o A no tick 0 e o B no dia 1, 2 dias.
Os cerebros sao os do pet de hoje (o M1 desligado). De cada vida: o sha256 do log (ou do registro do grupo), do estado de cada motor (com
o corpo), do estado interno de cada cerebro e as contagens.

    python tests/gabarito_social_m2.py     # grava tests/gabaritos/social_m2_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_social_par_a0 as a0  # noqa: E402
import run_v3_social_par_s as s  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "social_m2_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS_SOZINHO = 3
DIAS_ENTRADA = 2
BRACOS = ("C", "B1")
ENTRADA_B = 96 * 15                                     # o B entra no dia 1


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def fabricas(semente_pet: int, cd_extra: dict | None = None, motor_extra: dict | None = None):
    """(a fabrica do cerebro, a do motor) do pet do jogo da S. `cd_extra` vai a ConfigDigibrain (o M1) e `motor_extra` ao motor (a
    ConfigCompanhia, pelo teste); o gabarito usa os dois vazios"""
    _, fm0 = a0.fabricas_do_jogo(a0.DONO, semente_pet, a0.CCO)
    cd = replace(orq.config_do_braco(a0.e6.BRACO, conserto=True), **(cd_extra or {}))
    mk = dict(motor_extra or {})

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cd, a0.e6.CM, semente=semente_pet, cfg_cooperacao=a0.CCO)

    def fm(pol, cfg, sm, **kw):
        return fm0(pol, cfg, sm, **kw, **mk)
    return fp, fm


def vida_sozinho(semente: int, cd_extra: dict | None = None, motor_extra: dict | None = None):
    fp, fm = fabricas(semente, cd_extra, motor_extra)
    cerebro = fp()
    motor, _ = simular_vida_fisico(a0._dono(semente), cerebro, semente, DIAS_SOZINHO, orq.ORCAMENTO_POR_DIA * DIAS_SOZINHO, a0.DONO,
                                   lambda p, cfg, sm: fm(p, cfg, sm))
    return motor, cerebro


def vida_par(braco: str, semente: int, cd_extra: dict | None = None, motor_extra: dict | None = None) -> pc.VidaPar:
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    membros = []
    for i in ("A", "B"):
        fp, fm = fabricas(ss[i], cd_extra, motor_extra)
        membros.append(pc.Membro(i, "vivo", fm, fp, a0._dono(ss[i]), a0.DONO, "digibrain"))
    return s.viver(semente, membros, s.contexto(braco, semente), base=False)


def vida_entrada(semente: int, cd_extra: dict | None = None, motor_extra: dict | None = None):
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, entrada in (("A", 0), ("B", ENTRADA_B)):
        fp, fm = fabricas(ss[ident], cd_extra, motor_extra)
        pets.append(PetDoGrupo(ident, entrada, fp, fm, a0._dono(ss[ident]), a0.DONO, "digibrain"))
    return simular_grupo(a0.CM, semente, pets, DIAS_ENTRADA, cfg_cooperacao=a0.CCO)


def impressao_sozinho(semente: int, cd_extra: dict | None = None, motor_extra: dict | None = None) -> dict:
    motor, cerebro = vida_sozinho(semente, cd_extra, motor_extra)
    return {"log": _sha(_texto([ev.para_dict() for ev in motor.log])), "estado": _sha(_texto(motor.estado())),
            "cerebro": _sha(_texto(cerebro.estado_interno())), "decisoes": cerebro.k}


def impressao_grupo(g) -> dict:
    return {"registro": _sha(g.registro.para_jsonl()), "tick": g.tick,
            "estados": {i: _sha(_texto(m.estado())) for i, m in sorted(g.motores.items())},
            "logs": {i: _sha(m.log.para_jsonl()) for i, m in sorted(g.motores.items())},
            "cerebros": {i: _sha(_texto(m.politica.estado_interno())) for i, m in sorted(g.motores.items())},
            "decisoes": {i: m.politica.k for i, m in sorted(g.motores.items())}}


def gerar() -> dict:
    out = {f"sozinho|{sm}": impressao_sozinho(sm) for sm in SEMENTES}
    out.update({f"par|{b}|{sm}": {**impressao_grupo(vida_par(b, sm).grupo)} for b in BRACOS for sm in SEMENTES})
    out.update({f"entrada|{sm}": impressao_grupo(vida_entrada(sm)) for sm in SEMENTES})
    return out


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da companhia")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
