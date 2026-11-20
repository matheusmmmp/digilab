"""Gabarito das vidas de hoje que o G0 da genetica vai tocar (docs/TAREFA_V3_GENOMA_G0.md, secao 3.2, etapa E0: "o gabarito antes").
Gravado com o codigo da main (fa5fd6a) ANTES de qualquer mudanca no pacote, num commit proprio. Com a `ConfigGenoma` desligada (E1/E2), estas
vidas tem de sair iguais, byte a byte; com ela ligada e o genoma vazio, a trajetoria tem de sair igual (o log ganha o evento `genoma`).

Os tres caminhos que o G0 toca (o replay do mundo e a bancada que o monta), com as sementes dos testes (101 a 505) e poucos dias:
- `A`: o mundo fisico com o corpo quimico e o cerebro A (os lobos), nos dois layouts, perto e longe (`gabarito_dois_pets.vida_direta`);
- `REL`: o mundo com o DigiBrain modular, o braco REL da C4 (o M3* do conserto com a `memoria_autobio`), no `longe_fixo` e no comedouro,
  com o dono atencioso (`run_v2_memoria_autobio.viver`);
- `PAL`: o mundo do J5 com o paladar ligado e a fruta ao lado (a bancada do pet que pensa, `gabarito_pqp_ao_lado.config`).

De cada vida: o sha256 do log (o JSONL do motor) e o da trajetoria, que e feita de tres partes: as decisoes do pet (`acoes_recentes`), o
estado do motor depois de cada `avancar` (um por passo do dono; o gabarito instrumenta o `Motor.avancar` so enquanto gera, sem tocar no
pacote) e o resumo da vida (o estado final, as rngs e o registro do mundo; e a politica interna, o corpo e as medidas, quando ha). O
arquivo grava tambem o sha de cada parte, para o diagnostico apontar a que divergiu.

    python tests/gabarito_genoma_g0.py      # grava tests/gabaritos/genoma_g0_vidas_de_hoje.json (so com o codigo de antes da mudanca)
"""
from __future__ import annotations

import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_habito_intencao as hi  # noqa: E402
import gabarito_pqp_ao_lado as gal  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as rma  # noqa: E402

import bancada_v2 as bv  # noqa: E402
from digilab import engine as _engine  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "genoma_g0_vidas_de_hoje.json"
SEMENTES = (101, 202, 303, 404, 505)                     # so as dos testes
DIAS_A = 2
DIAS_REL = 3
LAYOUTS_A = ("padrao", "afastado")
LUGARES_A = ("perto", "longe")
LUGARES_REL = ("longe_fixo", "comedouro")
VIDAS_PAL = (("P1", "T1"), ("P1-plan", "T2"))


def _sha(obj) -> str:
    texto = obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True, default=repr)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


class _Passos:
    """le os estados por passo guardados no proprio motor (nao por id: o id de um motor liberado volta a ser usado)"""

    @staticmethod
    def get(motor, padrao=None):
        return motor.__dict__.get("_passos_g0", padrao)


@contextmanager
def _estados_por_passo():
    """instrumenta o `Motor.avancar` so enquanto gera: guarda o sha do `estado()` depois de cada chamada, por motor (id). So le."""
    original = _engine.Motor.avancar
    registro = _Passos()

    def avancar(self, ticks):
        saida = original(self, ticks)
        self.__dict__.setdefault("_passos_g0", []).append(_sha(self.estado()))
        return saida

    _engine.Motor.avancar = avancar
    try:
        yield registro
    finally:
        _engine.Motor.avancar = original


def impressao(motor, passos: list[str], extra: dict | None = None) -> dict:
    """o log, e a trajetoria: as decisoes, o estado por passo e o resumo da vida (cada parte com o seu sha)"""
    rngs = [motor._rng_politica.getstate(), motor._rng_ambiente.getstate()]
    for nome in ("_rng_fruta", "_rng_obediencia"):
        r = getattr(motor, nome, None)
        rngs.append(None if r is None else r.getstate())
    corpo = getattr(motor, "corpo", None)
    fisico = motor.resumo_mundo_fisico() if hasattr(motor, "resumo_mundo_fisico") else None
    resumo = {"motor": type(motor).__name__, "estado": repr(motor._estado), "estado_motor": motor.estado(), "rngs": repr(rngs),
              "fisico": fisico, "corpo": None if corpo is None else corpo.para_dict(),
              "politica": json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr), "extra": extra}
    partes = {"decisoes": _sha(repr(motor.acoes_recentes(10**9))), "estados": _sha(passos), "resumo": _sha(resumo)}
    return {"log": _sha(motor.log.para_jsonl()), "trajetoria": _sha(partes), "partes": partes, "passos": len(passos)}


def vidas_a(registro) -> dict:
    out = {}
    for layout in LAYOUTS_A:
        for lugar in LUGARES_A:
            for s in SEMENTES:
                fp, fm = gdp.fabricas_diretas(layout, "quimica", "lobos")
                dono = gdp.DonoComBolaPerto(gdp.DonoComLugar(gdp.criar_dono("atencioso"), lugar, s, "atencioso", gdp.LAYOUTS[layout]))
                v = gdp.simular_vida_mundo("atencioso", dono, fp(gdp.CONFIG_PADRAO), s, DIAS_A, 16 * DIAS_A, fm, rotulo_dono="atencioso")
                out[f"A|{layout}|quimica|lobos|{lugar}|{s}"] = {**impressao(v.motor, registro.get(v.motor, []),
                                                                        {"interacoes": v.interacoes})}
    return out


def vidas_rel(registro) -> dict:
    out = {}
    for lugar in LUGARES_REL:
        for s in SEMENTES:
            motor, reg, _, _ = rma.viver("REL", "atencioso", lugar, s, DIAS_REL, orq.ORCAMENTO_POR_DIA)
            medidas = hi.impressao(motor, reg, "REL")
            out[f"REL|atencioso|{lugar}|{s}"] = impressao(motor, registro.get(motor, []), medidas)
    return out


def vidas_pal(registro) -> dict:
    bp = bv.bancada_pqp_da_config(gal.config())
    out = {}
    for braco, protocolo in VIDAS_PAL:
        for s in SEMENTES:
            v = bp.vida(bv.EspecPQP(braco, protocolo, s))
            m = bp.medir(v)
            del m["custo"]                                # o relogio
            out[f"PAL|{braco}|{protocolo}|{s}"] = impressao(v.motor, registro.get(v.motor, []), {"medidas": m})
    return out


def gerar() -> dict:
    with _estados_por_passo() as registro:
        out = {**vidas_a(registro), **vidas_rel(registro), **vidas_pal(registro)}
    return out


def serializar(g: dict) -> str:
    return json.dumps(g, sort_keys=True, indent=1) + "\n"


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(serializar(g), encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas, {ARQUIVO.stat().st_size} bytes")
