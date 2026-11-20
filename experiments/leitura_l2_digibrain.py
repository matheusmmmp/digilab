"""A leitura da avaliacao da L-2 (adendo 5), so descritiva e so das partes gravadas: nenhuma vida roda, e nenhum criterio novo.

  - confere que o resultado.json da avaliacao se refaz igual das 12 partes relidas (pelo indice, com o sha256 de cada uma);
  - soma, por braco e lugar, as S-1 a S-6 da A5.3 na forma que o relato le:
      S-1: as suspensoes que acabaram, a media do n_susp (as decisoes de reflexo somadas) e a fracao em "expirou";
      S-2: a fracao em meta ou achou das buscas suspensas e das nunca suspensas, e os fins de todas as buscas e idas pelo motivo;
      S-3, S-4 e S-6: as fracoes das somas do resultado (o andado liquido medio, o andado ate 0, o reflexo em 2, a persistencia);
      S-5: a media por vida da exaustao e da privacao;
  - e as trocas da busca pela vencedora, somadas por braco e lugar.

    python experiments/leitura_l2_digibrain.py
grava artifacts_v2_digibrain_prototipo/l2/avaliacao_leitura.json
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402

AVALIACAO = RAIZ / l2.SAIDA["l2_avaliacao"]
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "l2" / "avaliacao_leitura.json"


def _fracao(a: float, b: float) -> float | None:
    return a / b if b else None


def _somar(dicts) -> dict:
    c: Counter = Counter()
    for d in dicts:
        c.update(d)
    return dict(sorted(c.items()))


def por_braco_e_lugar(registros: list[dict]) -> dict:
    out = {}
    for b in l2.BRACOS:
        for lu in l2.orq.LUGARES:
            vs = [r for r in registros if r["braco"] == b and r["lugar"] == lu]
            if not vs:
                continue
            x = [r["l2"] for r in vs]
            susp = sum(v["s1"]["suspensas"] for v in x)
            s2 = {k: sum(v["s2"][k] for v in x) for k in x[0]["s2"]}
            s3 = {k: sum(v["s3"][k] for v in x) for k in x[0]["s3"]}
            s4 = {k: sum(v["s4"][k] for v in x) for k in x[0]["s4"]}
            s6 = {k: sum(v["s6"][k] for v in x) for k in x[0]["s6"]}
            out[f"{b}|{lu}"] = {
                "vidas": len(vs),
                "s1": {"suspensas": susp, "n_susp_medio": _fracao(sum(v["s1"]["n_susp_soma"] for v in x), susp),
                       "frac_expirou": _fracao(sum(v["s1"]["expiradas"] for v in x), susp)},
                "s2": {**s2,
                       "frac_meta_ou_achou_suspensas": _fracao(s2["buscas_suspensas_meta_ou_achou"], s2["buscas_suspensas"]),
                       "frac_meta_ou_achou_nunca_suspensas": _fracao(s2["buscas_nunca_suspensas_meta_ou_achou"],
                                                                     s2["buscas_nunca_suspensas"]),
                       "fins_busca": _somar(v["fins"].get("busca", {}) for v in x),
                       "fins_ida": _somar(v["fins"].get("ida", {}) for v in x)},
                "s3": {**s3, "andado_liquido_medio": _fracao(s3["andado_liquido_soma"], s3["retomadas_com_alvo"]),
                       "frac_ate_zero": _fracao(s3["andado_liquido_ate_zero"], s3["retomadas_com_alvo"])},
                "s4": {**s4, "frac_reflexo_em_2": _fracao(s4["reflexo_em_2"], s4["retomadas"])},
                "s5": {"exaustao_media": statistics.fmean(r["exaustao"] for r in vs),
                       "privacao_media": statistics.fmean(r["privacao"] for r in vs)},
                "s6": {**s6, "frac_persistencia_decidiu": _fracao(s6["persistencia_decidiu"], s6["retomadas"])},
                "trocas_da_busca_por_vencedora": _somar(v["trocas"]["busca"]["por_vencedora"] for v in x)}
    return out


def calcular() -> dict:
    registros = list(l2.ler_medidas(AVALIACAO).values())
    resultado = json.loads((AVALIACAO / "resultado.json").read_text(encoding="utf-8"))
    refeito = {"fase": "l2_avaliacao", "modo": "l2_avaliacao", "plano": resultado["plano"],
               **l2.analisar(registros, "l2_avaliacao")}
    if bv._dump(refeito) != bv._dump(resultado):
        raise RuntimeError("o resultado.json nao se refaz igual das partes relidas")
    return {"rotulo": "a leitura da avaliacao da L-2: as S-1 a S-6 por braco e lugar, so das partes gravadas; descritiva, sem criterio",
            "fontes": {l2.orq.rc._relativo(AVALIACAO / n): bv._sha(AVALIACAO / n)
                       for n in ("meta.json", "resultado.json", l2.INDICE)},
            "script": {"arquivo": l2.orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "resultado_refeito_das_partes": True,
            "vidas": len(registros),
            "por_braco_e_lugar": por_braco_e_lugar(registros)}


if __name__ == "__main__":
    d = calcular()
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {l2.orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)}), {d['vidas']} vidas")
