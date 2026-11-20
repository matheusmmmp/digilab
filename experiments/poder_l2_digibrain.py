"""O poder da avaliacao da L-2 (docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 7; o adendo 5 do plano): so le o medidas.json do piloto do
conserto (as 72 vidas do M3* nas bases 65303 a 65505, K = 2; no git), nenhuma vida. A 66xxx nao entra nesta conta (a espec, secao 7.1).

Para cada medida dos criterios C-L2-2 e C-L2-3, por lugar: a media e o desvio-padrao entre as unidades (a unidade e a media das celulas
do lugar, uma vida por dono), e o poder do criterio pela aproximacao normal do t nao central, com o quantil t de metrics.quantil_t:
  - o desvio da diferenca pareada sai do da unidade pela correlacao rho entre as duas vidas do par: sigma_d = sigma x raiz(2 (1 - rho)).
    O rho nao esta medido em artefato nenhum; a tabela da rho = 0, 0,5 e 0,8;
  - C-L2-2 (o longe por episodio, o limite inferior do IC95 acima de 0): o poder para um efeito delta na grade;
  - C-L2-3 (nao piorar, com o efeito verdadeiro 0): por episodio e por racao no comedouro e no perto, o limite inferior acima de -0,03;
    a exaustao e a privacao nos tres lugares, o limite superior abaixo de +0,02.
A aproximacao normal e um pouco otimista com poucas unidades. Os numeros sao PROPOSTOS para o plano; nenhum e gate.

    python experiments/poder_l2_digibrain.py
grava artifacts_v2_digibrain_prototipo/l2/poder.json
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import quantil_t  # noqa: E402

ENTRADA = RAIZ / "artifacts_v2_digibrain_prototipo" / "conserto" / "piloto" / "medidas.json"
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "l2" / "poder.json"
KS = (10, 20, 30, 50, 100, 200)
RHOS = (0.0, 0.5, 0.8)
DELTAS = (0.03, 0.05, 0.10)            # o efeito no longe por episodio (C-L2-2): uma grade, sem fonte
MARGEM_EP = -0.03                      # C-L2-3, as taxas (PROPOSTA, SEM FONTE; a espec, secao 7.3)
MARGEM_CORPO = 0.02                    # C-L2-3, a exaustao e a privacao
MEDIDAS = {"episodio": lambda v: v["episodios_fome"]["taxa"], "racao": lambda v: v["cadeia"]["taxa"],
           "exaustao": lambda v: v["exaustao"], "privacao": lambda v: v["privacao"]}


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def poder(ncp_por_raiz_k: float, k: int) -> float:
    """P(T > t_crit) com T ~ normal(ncp, 1), ncp = (distancia ao limite / sigma_d) x raiz(K); t_crit unilateral do IC95"""
    return 1.0 - _phi(quantil_t(k - 1, 0.95) - ncp_por_raiz_k * math.sqrt(k))


def unidades(medidas: dict, lugar: str, f) -> list[float]:
    por: dict = {}
    for v in medidas.values():
        if v["braco"] == "M3" and v["lugar"] == lugar:
            x = f(v)
            if x is None:
                raise RuntimeError(f"{v['vida']}: a medida sem valor")
            por.setdefault((v["base"], v["k"]), []).append(x)
    if any(len(xs) != len(orq.DONOS) for xs in por.values()):
        raise RuntimeError("uma unidade sem as quatro vidas do lugar")
    return [statistics.fmean(xs) for _, xs in sorted(por.items())]


def calcular(medidas: dict) -> dict:
    dispersao = {}
    for nome, f in MEDIDAS.items():
        for lu in orq.LUGARES:
            u = unidades(medidas, lu, f)
            dispersao[f"{nome}|{lu}"] = {"unidades": len(u), "media": statistics.fmean(u), "dp": statistics.stdev(u)}

    def tabela(dp: float, distancia: float) -> dict:
        return {f"rho={rho}": {f"K={k}": poder(distancia / (dp * math.sqrt(2 * (1 - rho))), k) for k in KS} for rho in RHOS}

    c2 = {f"delta={d}": tabela(dispersao["episodio|longe"]["dp"], d) for d in DELTAS}
    c3 = {}
    for nome in ("episodio", "racao"):
        for lu in ("comedouro", "perto"):
            c3[f"{nome}|{lu}"] = tabela(dispersao[f"{nome}|{lu}"]["dp"], -MARGEM_EP)
    for nome in ("exaustao", "privacao"):
        for lu in orq.LUGARES:
            c3[f"{nome}|{lu}"] = tabela(dispersao[f"{nome}|{lu}"]["dp"], MARGEM_CORPO)
    # a conjuncao do C-L2-3, pelo produto (as comparacoes tratadas como independentes: uma aproximacao, nao um limite)
    conj = {f"rho={rho}": {f"K={k}": math.prod(c3[c][f"rho={rho}"][f"K={k}"] for c in c3) for k in KS} for rho in RHOS}
    return {"rotulo": "o poder da avaliacao da L-2, PROPOSTO para o adendo 5; aproximacao normal do t nao central; sem gate",
            "fonte": {orq.rc._relativo(ENTRADA): bv._sha(ENTRADA)},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 vidas do lugar (uma por dono) de uma unidade (base, k) do piloto do conserto, o M3*",
            "margens": {"taxas": MARGEM_EP, "corpo": MARGEM_CORPO}, "deltas_C-L2-2": list(DELTAS), "rhos": list(RHOS), "ks": list(KS),
            "dispersao": dispersao, "C-L2-2": c2, "C-L2-3": c3, "C-L2-3_conjuncao_aprox": conj}


if __name__ == "__main__":
    d = calcular(json.loads(ENTRADA.read_text(encoding="utf-8")))
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
