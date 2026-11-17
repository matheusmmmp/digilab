"""O resumo descritivo da medida da espera da voz no jogo (CONVERSA_PET, F2; docs/PLANO_ANALISE_V3_CONVERSA_ESPERA.md, secoes 1 e 2).

Le `turnos.jsonl` (gravado por web/app/e2e/medir_espera.spec.ts) e sai com, por medida (T1 a T4), o n, o p50, o p95 (com os valores vizinhos,
porque o p95 de 120 e instavel) e a fracao acima de 2, 5, 8 e 15 s (com o IC de Wilson), e com a fracao de espontaneas descartadas (T5). A
primeira conversa (fria) vai separada das outras (quente). Descritivo: sem gate, e nada daqui compara com outro braco.

    python experiments/resumo_espera_f2.py --pasta artifacts_v3_conversa_espera/G

So biblioteca padrao. Os quantis e o IC vem de `digilab/metrics.py` (`quantis`, `ic_wilson`). Campo faltando levanta erro.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.metrics import ic_wilson, quantis  # noqa: E402

# D-ES-1, DECIDIDO, SEM FONTE: o limite L = 8 s (o prazo do PacaPet, so como referencia de contagem, nao um alvo de UX) e a curva de 2, 5, 8 e 15 s
LIMITE_L_S = 8.0
CURVA_S = (2.0, 5.0, 8.0, 15.0)
MEDIDAS = ("T1", "T2", "T3", "T4")
CAMPOS = ("situacao", "t_envio", "t_chamada", "t_primeira", "t_balao", "t_verif", "descartada", "modelo", "erro", "latencia_s",
          "conversa", "turno", "fria")


def ler_turnos(caminho: Path) -> list[dict]:
    """as linhas do turnos.jsonl; JSON ruim, campo faltando ou arquivo sem linha levanta erro"""
    linhas = []
    for i, txt in enumerate(caminho.read_text(encoding="utf-8").split("\n"), 1):
        if not txt.strip():
            continue
        try:
            reg = json.loads(txt)
        except json.JSONDecodeError as e:
            raise ValueError(f"{caminho}: linha {i} nao e JSON: {e}") from e
        faltam = [c for c in CAMPOS if c not in reg]
        if faltam:
            raise ValueError(f"{caminho}: linha {i} sem os campos {faltam}")
        if reg["situacao"] not in ("conversa", "espontanea"):
            raise ValueError(f"{caminho}: linha {i} com situacao {reg['situacao']!r}")
        if not isinstance(reg["descartada"], bool):
            raise ValueError(f"{caminho}: linha {i} com `descartada` que nao e booleano")
        linhas.append(reg)
    if not linhas:
        raise ValueError(f"{caminho}: sem nenhuma linha")
    return linhas


def _dif_s(reg: dict, fim: str, ini: str) -> float | None:
    """(fim - ini) em segundos; None se o fim e None (a medida nao aconteceu); ini None com fim presente e erro"""
    if reg[fim] is None:
        return None
    if reg[ini] is None:
        raise ValueError(f"registro com {fim} mas sem {ini}: {reg}")
    d = (reg[fim] - reg[ini]) / 1000.0
    if d < 0:
        raise ValueError(f"tempo negativo ({fim} - {ini} = {d:.3f} s): {reg}")
    return d


def valores_da_medida(regs: list[dict], medida: str) -> list[float]:
    """os valores (s) de T1..T4 sobre as CONVERSAS (T5, a espontanea, tem a funcao propria). Registro sem o tempo (erro, sem verificacao) fica fora."""
    if medida not in MEDIDAS:
        raise ValueError(f"medida desconhecida: {medida}")
    campos = {"T1": ("t_balao", "t_envio"), "T2": ("t_primeira", "t_envio"), "T3": ("t_verif", "t_balao"), "T4": ("t_chamada", "t_envio")}[medida]
    saida = []
    for r in regs:
        if r["situacao"] != "conversa":
            continue
        v = _dif_s(r, *campos)
        if v is not None:
            saida.append(v)
    return saida


def resumo_de(valores: list[float]) -> dict:
    """n, p50, p95 (o posto mais proximo), os vizinhos do p95 e, por limite da curva, a fracao acima com o IC de Wilson"""
    n = len(valores)
    if not n:
        return {"n": 0}
    xs = sorted(valores)
    p50, p95 = quantis(xs, [0.5, 0.95])
    posto = next(i for i, x in enumerate(xs) if x == p95)       # o primeiro posto com o valor do p95
    out = {"n": n, "p50": p50, "p95": p95, "p95_vizinhos": [xs[max(0, posto - 1)], xs[min(n - 1, posto + 1)]], "max": xs[-1], "acima": {}}
    for lim in CURVA_S:
        k = sum(1 for x in xs if x > lim)
        out["acima"][f"{lim:g}"] = {"k": k, "n": n, "fracao": k / n, "ic95": ic_wilson(k, n)}
    out["acima_L"] = out["acima"][f"{LIMITE_L_S:g}"]
    return out


def espontaneas(regs: list[dict]) -> dict:
    """T5: as descartadas / as disparadas (com o IC de Wilson) e o pedido -> balao (s) das que sairam"""
    esp = [r for r in regs if r["situacao"] == "espontanea"]
    if not esp:
        return {"disparadas": 0}
    k = sum(1 for r in esp if r["descartada"])
    saidas = [_dif_s(r, "t_balao", "t_envio") for r in esp if not r["descartada"]]
    saidas = [v for v in saidas if v is not None]
    return {"disparadas": len(esp), "descartadas": k, "fracao_descartada": k / len(esp), "ic95": ic_wilson(k, len(esp)),
            "pedido_balao_s": resumo_de(saidas)}


def resumir(regs: list[dict]) -> dict:
    """o resumo inteiro: frio (a conversa 1) e quente (as outras), por medida; as espontaneas ficam num bloco so (nao tem conversa)"""
    conv = [r for r in regs if r["situacao"] == "conversa"]
    for r in conv:
        if r["conversa"] is None or r["fria"] is None:
            raise ValueError(f"conversa sem numero de conversa ou sem `fria`: {r}")
    fria = [r for r in conv if r["fria"]]
    quente = [r for r in conv if not r["fria"]]
    return {
        "limite_L_s": LIMITE_L_S, "curva_s": list(CURVA_S),
        "n_conversas_turnos": len(conv), "n_erros": sum(1 for r in conv if r["erro"] is not None),
        "quente": {m: resumo_de(valores_da_medida(quente, m)) for m in MEDIDAS},
        "fria": {m: resumo_de(valores_da_medida(fria, m)) for m in MEDIDAS},
        "espontaneas": espontaneas(regs),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pasta", required=True, type=Path, help="a pasta do braco, com turnos.jsonl")
    a = ap.parse_args()
    res = resumir(ler_turnos(a.pasta / "turnos.jsonl"))
    (a.pasta / "resumo.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"turnos de conversa: {res['n_conversas_turnos']} (erros: {res['n_erros']}); limite L = {LIMITE_L_S:g} s")
    for grupo in ("quente", "fria"):
        for m in MEDIDAS:
            r = res[grupo][m]
            if not r["n"]:
                print(f"{grupo:6s} {m}: sem valores")
                continue
            curva = "  ".join(f">{k} s: {v['fracao']:.2f}" for k, v in r["acima"].items())
            print(f"{grupo:6s} {m}: n={r['n']} p50={r['p50']:.2f} p95={r['p95']:.2f} (vizinhos {r['p95_vizinhos'][0]:.2f}..{r['p95_vizinhos'][1]:.2f})  {curva}")
    e = res["espontaneas"]
    if e["disparadas"]:
        print(f"espontaneas: {e['descartadas']}/{e['disparadas']} descartadas ({e['fracao_descartada']:.2f}; IC95 {e['ic95'][0]:.2f}..{e['ic95'][1]:.2f})")
    else:
        print("espontaneas: nenhuma disparada")


if __name__ == "__main__":
    main()
