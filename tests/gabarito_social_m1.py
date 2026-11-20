"""Gabarito do SOCIAL_PAR M1 (docs/ESPEC_SOCIAL_PAR_M1.md, secoes 5 e 6): as vidas de hoje do DigiBrain modular, do pet sozinho e do par,
gravadas com o codigo de ANTES da subchave `unidades_sociais`, num commit proprio. Com a subchave desligada, estas vidas tem de sair iguais,
byte a byte (o G2); com ela ligada, o pet sozinho tambem (o G2b).

As vidas (so as sementes dos testes):
  - `sozinho|<semente>`: o pet do jogo da S (o `run_v3_social_par_a0.fabricas_do_jogo`: o modular REL do laboratorio com a CO7), sozinho
    no mundo do laboratorio, com o dono `atencioso` no comedouro, 3 dias;
  - `par|<braco>|<semente>`: o par da S3 (dois pets do jogo), a vida VIVO do braco (C ou B1), os 5 dias da S, com a intervencao no t0.
De cada vida: o sha256 do log (ou do registro do grupo), das posicoes, do estado interno de cada cerebro (com os motivos) e as contagens.

    python tests/gabarito_social_m1.py     # grava tests/gabaritos/social_m1_de_hoje.json (so com o codigo de antes)
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
from digilab.grupo import sementes_do_grupo  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "social_m1_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS_SOZINHO = 3
BRACOS = ("C", "B1")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def fabricas(semente_pet: int, extra: dict | None = None):
    """(a fabrica do cerebro, a do motor) do pet do jogo da S, com `extra` na ConfigDigibrain (o teste liga a subchave por aqui; o
    gabarito usa {})"""
    _, fm = a0.fabricas_do_jogo(a0.DONO, semente_pet, a0.CCO)
    cd = replace(orq.config_do_braco(a0.e6.BRACO, conserto=True), **(extra or {}))

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cd, a0.e6.CM, semente=semente_pet, cfg_cooperacao=a0.CCO)
    return fp, fm


def vida_sozinho(semente: int, extra: dict | None = None):
    fp, fm = fabricas(semente, extra)
    cerebro = fp()
    motor, _ = simular_vida_fisico(a0._dono(semente), cerebro, semente, DIAS_SOZINHO, orq.ORCAMENTO_POR_DIA * DIAS_SOZINHO, a0.DONO,
                                   lambda p, cfg, sm: fm(p, cfg, sm))
    return motor, cerebro


def vida_par(braco: str, semente: int, extra: dict | None = None) -> pc.VidaPar:
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    membros = []
    for i in ("A", "B"):
        fp, fm = fabricas(ss[i], extra)
        membros.append(pc.Membro(i, "vivo", fm, fp, a0._dono(ss[i]), a0.DONO, "digibrain"))
    return s.viver(semente, membros, s.contexto(braco, semente), base=False)


def impressao_sozinho(semente: int, extra: dict | None = None) -> dict:
    motor, cerebro = vida_sozinho(semente, extra)
    return {"log": _sha(_texto([ev.para_dict() for ev in motor.log])), "estado": _sha(_texto(motor.estado())),
            "cerebro": _sha(_texto(cerebro.estado_interno())), "decisoes": cerebro.k}


def impressao_par(braco: str, semente: int, extra: dict | None = None) -> dict:
    v = vida_par(braco, semente, extra)
    g = v.grupo
    return {**a0._sha_vida(v), "tick": g.tick, "t0": v.t0,
            "cerebros": {i: _sha(_texto(m.politica.estado_interno())) for i, m in sorted(g.motores.items())},
            "decisoes": {i: m.politica.k for i, m in sorted(g.motores.items())}}


def gerar() -> dict:
    out = {f"sozinho|{sm}": impressao_sozinho(sm) for sm in SEMENTES}
    out.update({f"par|{b}|{sm}": impressao_par(b, sm) for b in BRACOS for sm in SEMENTES})
    return out


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da subchave")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
