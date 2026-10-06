"""V2, V1-ADENDO3: o custo da validacao unica com o bloco de duracoes e os bracos P2d e P3i, e a escolha da duracao maior (adendo 3,
secao 3.1, do docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md).

A conta, registrada antes da run:
- o tempo por vida de 14 dias e o da calibracao conjunta (artifacts_v2_calibracao_conjunta/D/resultado.json, "segundos_por_vida": o
  piloto de 880 vidas, a mesma composicao de 44 por unidade da validacao);
- o bloco de duracoes tem vidas de 7 e de D dias; o tempo delas sai do de 14 pela razao t(d) / t(14) medida aqui, so nas sementes dos
  testes (bases 101 e 202, K = 1), com os mesmos bracos (P0 e P1), mundos (descasado e mutavel), ponto e montagem da validacao, pela
  bancada inteira (vida, replay do disco e medidas);
- os bracos P2d e P3i (2 x 2 mundos por unidade, 14 dias) contam o tempo por vida da calibracao conjunta;
- D = 28 se a validacao inteira cabe no teto de 12 h (K-10); senao 21; senao nenhuma, e o Matheus decide.

Uso:  python experiments/custo_adendo3.py --saida artifacts_v2_v1_adendo3
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402

TETO_HORAS = 12.0                                  # K-10 do plano da calibracao conjunta
DURACOES_MAIORES = (28, 21)                        # adendo 3: a maior entre 28 e 21 que couber
DURACAO_MENOR = 7
DURACOES_MEDIDAS = (7, 14, 21, 28)
BASES_MEDIDA = [101, 202]                          # so as sementes dos testes


def vidas_por_unidade_principal() -> dict:
    """As vidas por unidade da validacao do #183: o bloco principal (bracos x mundos + o so cuidado), a referencia do padrao e os blocos
    da secao 4 do plano da calibracao conjunta."""
    principal = len(em.BRACOS) * len(em.MUNDOS) + len(em.COM_DONO) * len(em.MUNDOS)
    padrao = len(em.BRACOS_PADRAO)
    blocos = {n: len(b) * len(m) + len(a) * len(m) for n, (b, m, a) in em.BLOCOS.items() if n != "duracoes"}
    return {"principal": principal, "padrao": padrao, "blocos": blocos,
            "total": principal + padrao + sum(blocos.values())}


def medir_razoes(cfg_val: dict) -> dict:
    """Tempo por vida de P0 e P1 no descasado e no mutavel em cada duracao, pela bancada, nas sementes dos testes."""
    tempos = {}
    pasta = Path(tempfile.mkdtemp(prefix="custo_adendo3_"))
    try:
        for d in DURACOES_MEDIDAS:
            cfg = {k: v for k, v in cfg_val.items() if k != "plano"}
            cfg.update({"unidades": {"bases": BASES_MEDIDA, "k": 1}, **em.dias_e_orcamento(cfg_val, d)})
            cb = em.config_da_bancada(cfg, em.BLOCO_DURACOES[0], em.BLOCO_DURACOES[1], [])
            t0 = time.perf_counter()
            r = bv.rodar(cb, pasta / f"d{d}")
            seg = time.perf_counter() - t0
            tempos[d] = {"vidas": len(r["vidas"]), "segundos": seg, "segundos_por_vida": seg / len(r["vidas"])}
    finally:
        shutil.rmtree(pasta, ignore_errors=True)
    base = tempos[14]["segundos_por_vida"]
    for d, t in tempos.items():
        t["razao_a_14"] = t["segundos_por_vida"] / base
    return tempos


def custo(cfg_val: dict, k2: dict, tempos: dict, n_unidades: int) -> dict:
    spv = float(k2["segundos_por_vida"])
    vpu = vidas_por_unidade_principal()
    p2d_p3i = len(em.BLOCO_P2D_P3I[0]) * len(em.BLOCO_P2D_P3I[1])
    dur_vidas = len(em.BLOCO_DURACOES[0]) * len(em.BLOCO_DURACOES[1])
    base_s = n_unidades * (vpu["total"] + p2d_p3i) * spv
    opcoes = {}
    for dmax in DURACOES_MAIORES:
        bloco_s = n_unidades * dur_vidas * spv * (tempos[DURACAO_MENOR]["razao_a_14"] + tempos[dmax]["razao_a_14"])
        total_h = (base_s + bloco_s) / 3600.0
        opcoes[dmax] = {"bloco_duracoes_horas": bloco_s / 3600.0, "total_horas": total_h, "cabe": total_h <= TETO_HORAS}
    escolhida = next((d for d in DURACOES_MAIORES if opcoes[d]["cabe"]), None)
    return {"segundos_por_vida_k2": spv, "fonte_k2": "artifacts_v2_calibracao_conjunta/D/resultado.json",
            "unidades": n_unidades, "vidas_por_unidade_sem_o_adendo3": vpu, "vidas_por_unidade_p2d_p3i": p2d_p3i,
            "vidas_por_unidade_bloco_duracoes": {"7": dur_vidas, "D": dur_vidas},
            "horas_sem_o_bloco_de_duracoes": base_s / 3600.0, "opcoes": {str(k): v for k, v in opcoes.items()},
            "teto_horas": TETO_HORAS, "duracao_maior": escolhida,
            "decisao": ("cabe: a maior entre 28 e 21 dias" if escolhida else
                        "nem 21 dias cabe no teto: o Matheus decide (adendo 3, secao 3.1)")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="custo da validacao unica com o adendo 3")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    cfg_val = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/validacao.json").read_text(encoding="utf-8"))
    k2 = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta/D/resultado.json").read_text(encoding="utf-8"))
    unidades = bv.unidades_derivadas(cfg_val["unidades"]["bases"], int(cfg_val["unidades"]["k"]))   # a conta vem antes da config
    tempos = medir_razoes(cfg_val)
    r = custo(cfg_val, k2, tempos, len(unidades))
    r.update({"medida_da_razao": {"bases": BASES_MEDIDA, "k": 1, "bracos": list(em.BLOCO_DURACOES[0]),
                                  "mundos": list(em.BLOCO_DURACOES[1]), "por_duracao": {str(k): v for k, v in tempos.items()}},
              "python": platform.python_version(), "maquina": platform.platform()})
    out = RAIZ / a.saida
    out.mkdir(parents=True, exist_ok=True)
    bv._gravar(out / "custo.json", bv._dump(r))
    print(json.dumps({k: r[k] for k in ("horas_sem_o_bloco_de_duracoes", "opcoes", "duracao_maior", "decisao")}, indent=1))
    return 0 if r["duracao_maior"] else 2


if __name__ == "__main__":
    sys.exit(main())
