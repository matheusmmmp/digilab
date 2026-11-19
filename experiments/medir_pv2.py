"""A medicao do PR do codigo do PV-2 (docs/PLANO_ANALISE_V3_PET_VIVO_PV2.md, secao 4 e PV2-9): so nas sementes dos testes, sem faixa e sem
run. Duas partes, gravadas em artifacts_v3_pet_vivo/pv2/medicao_codigo.json:

1. **Os numeros do mecanismo (PV2-9), pelas regras abaixo, PROPOSTAS e SEM FONTE, escritas antes de rodar:**
   - a queda do cheiro: o |dC| das decisoes do executor com dC < 0, nas vidas do OLF-0 (a tropotaxia, sem pirueta) com o `w0_dc` = 0
     (o dC fora do inato, para a medida nao depender do proprio numero que ela propoe; D-PV2C-10), nos 3 lugares, nas sementes 101 a
     505, com o dono `atencioso`;
   - `l_pirueta` = 2 x a mediana dessas quedas (a pirueta pede a queda de umas duas decisoes, nao uma so);
   - `w0_dc` = div_arred(S x S, 8 x a mediana): uma queda tipica tira S/8 do inato da unidade comer/cheiro;
   - `n_varredura` = 1, sem medida (o plano nao da como medir); fica PROPOSTO;
   - `taxa_placebo` = arred(256 x piruetas / decisoes do executor fora da varredura), nas vidas do OLF-DCV com o `l_pirueta` e o
     `w0_dc` acima (a taxa da hora sorteada e a da pirueta);
   - a saturacao do OLF-G (a INT-4): nas mesmas vidas do OLF-DCV, para cada decisao com cheiro (c > 0), o nivel com o ganho
     `clamp(div_arred(c x (G0 + u_fome), G0), 0, S)` para G0 em 64, 128, 256, 512 e 1024, pela conta (sem vida nova); a fracao no teto S.
     O corte da INT-4: mais de metade no teto pede um adendo com outro G0.
2. **O custo:** o tempo de parede de 2 vidas de 14 dias por braco (sementes 101 e 202, `longe`), com o G1 do replay conferido, e a projecao
   da run (14 400 vidas, o plano, secao 4) com 4 processos. O contrafactual da SE-C (1 440 vidas) nao entra: e a conta da 0b, medida la
   (artifacts_v3_pet_vivo/auditoria/tempo_a4.json).

    python experiments/medir_pv2.py
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import pv2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.config import CONFIG_PV2  # noqa: E402
from digilab.digibrain.base import div_arred  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v3_pet_vivo" / "pv2" / "medicao_codigo.json"
SEMENTES = (101, 202, 303, 404, 505)
LUGARES = ("comedouro", "longe_fixo", "longe")
DONO = "atencioso"
DIAS = 14
VIDAS_DA_RUN = 14400
PROCESSOS = 4
CODIGO = ("digilab/digibrain/sens.py", "digilab/digibrain/impulso.py", "digilab/digibrain/adapt.py", "digilab/digibrain/plast.py",
          "digilab/config.py", "digilab/metrics.py", "experiments/pv2.py", "experiments/medir_pv2.py")


def _motivos(braco: str, lugar: str, semente: int, base=None) -> list[dict]:
    _, registro, _ = pv2.viver(braco, DONO, lugar, semente, DIAS, base=base)
    return orq.cerebro_de(registro).motivos


def quedas_olf0() -> list[int]:
    out = []
    for lugar in LUGARES:
        for s in SEMENTES:
            out += [-m["pv2"]["dC"] for m in _motivos("OLF-0", lugar, s, replace(CONFIG_PV2, w0_dc=0)) if "pv2" in m and m["pv2"]["dC"] < 0]
    return out


G0S = (64, 128, 256, 512, 1024)


def taxa_da_pirueta(base) -> dict:
    piruetas = fora = execs = 0
    pares = []
    for lugar in LUGARES:
        for s in SEMENTES:
            ms = _motivos("OLF-DCV", lugar, s, base)
            exe = [m["pv2"] for m in ms if "pv2" in m]
            execs += len(exe)
            fora += sum(1 for e in exe if e["fase"] != "varredura")
            piruetas += sum(1 for e in exe if e["fase"] == "pirueta")
            pares += [(m["olfato"]["c"], m["afeto"]["urgencias"].get("fome", 0)) for m in ms if m["olfato"]["c"] > 0]
    S = orq.CONFIG_DIGIBRAIN_INATOS.escala
    saturacao = {g: sum(1 for c, u in pares if min(S, max(0, div_arred(c * (g + u), g))) >= S) / len(pares) for g in G0S} if pares else None
    cs = [c for c, _ in pares]
    return {"executor": execs, "fora_da_varredura": fora, "piruetas": piruetas,
            "taxa_placebo": round(256 * piruetas / fora) if fora else None,
            "nivel_c": None if not cs else {"n": len(cs), "mediana": statistics.median(cs), "maximo": max(cs)},
            "saturacao_olf_g": saturacao}


def custo() -> dict:
    tempos = {}
    for braco in pv2.BRACOS:
        ts = []
        for s in (101, 202):
            t = time.perf_counter()
            pv2.medir(braco, DONO, "longe", s, DIAS)
            ts.append(time.perf_counter() - t)
        tempos[braco] = ts
    media = statistics.mean(t for ts in tempos.values() for t in ts)
    return {"segundos_por_vida": tempos, "media_s": media,
            "projecao_run_h": VIDAS_DA_RUN * media / PROCESSOS / 3600, "vidas": VIDAS_DA_RUN, "processos": PROCESSOS,
            "nota": "com o G1 do replay em cada vida (a run tambem confere); sem o contrafactual da SE-C"}


def medir() -> dict:
    S = orq.CONFIG_DIGIBRAIN_INATOS.escala
    quedas = quedas_olf0()
    if not quedas:
        raise RuntimeError("nenhuma queda do cheiro nas vidas do OLF-0")
    med = int(statistics.median(quedas))
    l_pirueta = max(1, 2 * med)
    w0_dc = div_arred(S * S, 8 * max(1, med))
    base = replace(CONFIG_PV2, l_pirueta=l_pirueta, w0_dc=w0_dc, n_varredura=1)
    taxa = taxa_da_pirueta(base)
    return {"descricao": __doc__.strip().splitlines()[0],
            "quedas": {"n": len(quedas), "mediana": med, "p25": statistics.quantiles(quedas, n=4)[0],
                       "p75": statistics.quantiles(quedas, n=4)[2], "maxima": max(quedas)},
            "propostos": {"l_pirueta": l_pirueta, "w0_dc": w0_dc, "n_varredura": 1, "taxa_placebo": taxa["taxa_placebo"]},
            "pirueta": taxa, "custo": custo(), "sementes": SEMENTES, "lugares": LUGARES, "dono": DONO, "dias": DIAS,
            "codigo": {c: hashlib.sha256((RAIZ / c).read_bytes()).hexdigest() for c in CODIGO}}


if __name__ == "__main__":
    d = medir()
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: d[k] for k in ("quedas", "propostos", "pirueta")}, ensure_ascii=False))
    print("custo:", round(d["custo"]["media_s"], 2), "s por vida; projecao", round(d["custo"]["projecao_run_h"], 2), "h")
