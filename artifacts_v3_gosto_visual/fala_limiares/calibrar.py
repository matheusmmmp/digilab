"""A calibracao dos limiares do `dec-v4` (docs/futuro/fala_do_assistir.md, FA-2; a ConfigFalaAssistir de digilab/config.py).

Le so o `sinais.json.gz` desta pasta (de `extrair_sinais.py`, as vidas GRAVADAS da GV3 e da GV3b do adendo 2, rejogadas e conferidas) e grava
o `limiares.json`. Nenhuma vida nova; nada aqui e resultado de pesquisa nem entra numa medida. A regra (PROPOSTA, SEM FONTE; D-GV-FALA-4):

- **A base da calibracao e a GV3b, so o genoma proprio:** e a configuracao do jogo v35+ (o olhar com o enjoo ligado, D-GV-TVJOGO), e o dec-v4
  pede o enjoo. O genoma vazio (o controle) e a GV3 (sem o enjoo) ficam como descritivo: as mesmas distribuicoes, lado a lado.
- **A unidade e a decisao em que o pet olhava** uma TV no intervalo que acabou (`olhar.olhava` nao nulo).
- **O quantil** e o de posto mais perto, em inteiros: o valor de posto ceil(p n) da lista ordenada (n o tamanho da lista).
- **Os limiares:**
  - `gostei_agrado`: o quantil 0,90 do agrado efetivo (o pet diz "gostei" nos 10% de agrado mais alto do que ele olha);
  - `o_que_e_agrado`: o quantil 0,10 do agrado SEM o enjoo (o `agrado` do motivo: a distancia do nivel ao alvo aprendido, o "longe do
    esperado"); `o_que_e_enjoo`: a mediana do enjoo (o pet ainda nao cansou daquela TV). O agrado efetivo nao serve aqui: ele cai com o
    enjoo, e o agrado efetivo baixo e quase sempre o pet enjoado, o `chato` (o primeiro ensaio, com o efetivo e o quantil 0,25 do enjoo,
    deixou o `o_que_e` ativo em 0,7% das decisoes; D-GV-FALA-4);
  - `chato_enjoo` e `chato_tedio`: o quantil 0,75 do enjoo e do tedio;
  - `susto_subida`: o quantil 0,10 das subidas positivas da urgencia do susto de uma decisao para a seguinte, sem tapa (o susto do corpo so
    sobe por um estimulo: sem tapa, so o salto de volume da tela, GV-17; quase todo salto vira o susto, e o limite de 1 min da FA-5 segura a
    frequencia).
- **O descritivo:** por run, genoma e dono, quantas decisoes olhando e, na GV3b, a fracao em que cada conceito do dec-v4 fica ativo e a
  distribuicao da intencao, com os limiares calibrados (pela funcao `conceitos_assistir` do decodificador, sobre os sinais).

    python artifacts_v3_gosto_visual/fala_limiares/calibrar.py      # grava limiares.json nesta pasta
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_FALA_ASSISTIR  # noqa: E402
from digilab.digibrain.decodificador import CATALOGO_ASSISTIR, conceitos_assistir  # noqa: E402

PASTA = Path(__file__).resolve().parent
ENTRADA = PASTA / "sinais.json.gz"
SAIDA = PASTA / "limiares.json"
BASE = ("gv3b", "proprio")
REGRA = {"gostei_agrado": ("agrado_efetivo", 0.90), "o_que_e_agrado": ("agrado", 0.10), "o_que_e_enjoo": ("enjoo", 0.50),
         "chato_enjoo": ("enjoo", 0.75), "chato_tedio": ("tedio", 0.75), "susto_subida": ("subida_susto", 0.10)}
QUANTIS_DESCRITIVOS = (0.10, 0.25, 0.50, 0.75, 0.90)


def quantil(xs: list[int], p: float) -> int:
    """o de posto mais perto: o elemento de posto ceil(p n) (1-indexado) da lista ordenada; lista vazia levanta erro"""
    if not xs:
        raise ValueError("quantil de uma lista vazia")
    v = sorted(xs)
    return v[max(1, math.ceil(p * len(v))) - 1]


def _subida(l: dict) -> int | None:
    """a subida do susto desde a decisao anterior, sem tapa; None sem a anterior ou com tapa"""
    if l["susto_anterior"] is None or l["tapa"]:
        return None
    return l["susto"] - l["susto_anterior"]


def _sinais(linhas: list[dict]) -> dict[str, list[int]]:
    out = {"agrado": [l["agrado"] for l in linhas], "tedio": [l["tedio"] for l in linhas],
           "subida_susto": [s for s in (_subida(l) for l in linhas) if s is not None and s > 0]}
    if linhas and linhas[0]["enjoo"] is not None:
        out["agrado_efetivo"] = [l["agrado_efetivo"] for l in linhas]
        out["enjoo"] = [l["enjoo"] for l in linhas]
    return out


def _descreve(xs: list[int]) -> dict:
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "min": min(xs), "max": max(xs), **{f"q{int(p * 100):02d}": quantil(xs, p) for p in QUANTIS_DESCRITIVOS}}


def _mini_motivo(l: dict) -> tuple[dict, dict]:
    """o motivo e o anterior minimos que `conceitos_assistir` le, montados dos sinais gravados (o resto do motivo nao entra na conta)"""
    olhar = {"telas": [], "olhava": 1, "agrado": l["agrado"], "agrado_inato": None, "gosto": None, "enjoo": l["enjoo"],
             "agrado_efetivo": l["agrado_efetivo"], "olha": None}
    m = {"k": l["k"], "olhar": olhar, "afeto": {"urgencias": {"tedio": l["tedio"], "susto": l["susto"]}},
         "gestos": [["tapa", 0]] if l["tapa"] else []}
    ant = {"k": l["k"] - 1, "afeto": {"urgencias": {"susto": l["susto_anterior"] if l["susto_anterior"] is not None else l["susto"]}}}
    return m, ant


def main() -> None:
    dados = json.loads(gzip.decompress(ENTRADA.read_bytes()).decode("utf-8"))
    grupos: dict[tuple, list[dict]] = {}
    vidas: Counter = Counter()
    for v in dados["vidas"]:
        grupos.setdefault((v["run"], v["genoma_tipo"]), []).extend(v["olhava"])
        grupos.setdefault((v["run"], v["genoma_tipo"], v["dono"]), []).extend(v["olhava"])
        vidas[(v["run"], v["genoma_tipo"], v["dono"])] += 1
    base = _sinais(grupos[BASE])
    limiares = {nome: quantil(base[sinal], p) for nome, (sinal, p) in REGRA.items()}
    cfg = replace(CONFIG_FALA_ASSISTIR, **limiares)
    descritivo = {}
    for chave in sorted(grupos):
        linhas = grupos[chave]
        d = {"decisoes_olhando": len(linhas), "sinais": {n: _descreve(xs) for n, xs in sorted(_sinais(linhas).items())}}
        if len(chave) == 3:
            d["vidas"] = vidas[chave]
        if chave[0] == "gv3b":
            ativos, intencao = Counter(), Counter()
            for l in linhas:
                m, ant = _mini_motivo(l)
                a = conceitos_assistir(m, ant, cfg)
                for c in a["conceitos"]:
                    if c["valor"] >= cfg.limiar_ativo:
                        ativos[c["nome"]] += 1
                intencao[str(a["intencao"])] += 1
            d["fracao_ativo"] = {n: ativos[n] / len(linhas) for n in CATALOGO_ASSISTIR}
            d["intencao"] = dict(sorted(intencao.items()))
        descritivo["|".join(chave)] = d
    out = {"entrada": ENTRADA.name, "entrada_sha256": hashlib.sha256(ENTRADA.read_bytes()).hexdigest(), "base": "|".join(BASE),
           "regra": {n: {"sinal": s, "quantil": p} for n, (s, p) in REGRA.items()}, "limiares": limiares,
           "config_fala_assistir": asdict(cfg), "config_em_digilab_igual": asdict(cfg) == asdict(CONFIG_FALA_ASSISTIR),
           "descritivo": descritivo}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(limiares), "| a config de digilab/config.py e a calibrada:", out["config_em_digilab_igual"])


if __name__ == "__main__":
    main()
