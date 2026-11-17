"""F1 da CONVERSA_PET: quanto o verificador muda o que chega ao jogador (docs/PLANO_ANALISE_V3_CONVERSA_VERIF.md, APROVADO pelo Matheus em
2026-11-17). Exploratorio e descritivo, sem gate, sobre os dados da DC5c e a referencia da DC5d, **sem chamada a modelo**.

Uso (depois da DC5d):
  python experiments/analise_verif_dc5.py --falas artifacts_v3_conversa_dc5/validacao/falas.jsonl \
      --referencia <referencia.jsonl> --kappa <kappa.json> --saida <saida.json>

Entradas:
- `falas.jsonl`, uma fala por linha, como a DC5 grava (`id`, `celula`, `braco`, `voz`, `conjunto`, `papel`, `erro`, `verificacao`);
- `referencia.jsonl` (o contrato que a DC5d entrega): `{"fala": <id do falas.jsonl>, "sem_sustento": "sim"|"nao", "so_fica_comigo": bool}`
  para **toda** fala da voz (as que nao cairam na generica). `so_fica_comigo` e verdadeiro quando a fala so fica sem sustento por "fica
  comigo", "fique comigo" ou "nao vai embora" (4.1 da DC5);
- `kappa.json`, o kappa da DC5d (`metrics.kappa_cohen`): `{"kappa": float|null, "calculavel": bool}`.

Sem a referencia, ou com o kappa abaixo de `KAPPA_MINIMO` ou nao calculavel, o V1, o V2, o V4 e o V5 saem "nao_medido" (secao 5); o V3 e as
genericas continuam. Tudo falha alto em campo faltando, fala repetida ou referencia que nao casa. So biblioteca padrao.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.metrics import COMPONENTES_VERIF, componentes_verificador, marcou_sem, tabela_trava  # noqa: E402

KAPPA_MINIMO = 0.7          # DC5, 4.1 (D-DC5-6, DECIDIDO, SEM FONTE): abaixo disso a referencia nao vale, e a F1 segue a DC5
NAO_MEDIDO = "nao_medido"
CAMPOS = ("id", "celula", "braco", "voz", "conjunto", "erro", "verificacao")


def ler_jsonl(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def motivo_generica(erro: str) -> str:
    """o motivo da generica: o que vem antes de ':' no `erro` (`repete_citacao: ...`), ou o erro inteiro"""
    return erro.split(":", 1)[0].strip()


def separar(falas: list[dict]) -> tuple[list[dict], list[dict]]:
    """as falas da voz (com verificacao) e as genericas (com `erro`, sem verificacao). Falha alto em campo faltando, id repetido, generica
    com verificacao ou fala da voz sem verificacao."""
    vistos, voz, genericas = set(), [], []
    for r in falas:
        for k in CAMPOS:
            if k not in r:
                raise KeyError(f"F1: a fala {r.get('id')!r} sem o campo {k}")
        if r["id"] in vistos:
            raise ValueError(f"F1: fala repetida {r['id']}")
        vistos.add(r["id"])
        if r["erro"]:
            if r["verificacao"] is not None:
                raise ValueError(f"F1: a generica {r['id']} tem verificacao")
            genericas.append(r)
        else:
            if r["verificacao"] is None:
                raise ValueError(f"F1: a fala da voz {r['id']} sem verificacao")
            voz.append(r)
    if not voz:
        raise ValueError("F1: nenhuma fala da voz")
    return voz, genericas


def indexar_referencia(referencia: list[dict], voz: list[dict]) -> dict:
    """a referencia por id da fala; precisa cobrir exatamente as falas da voz"""
    ref = {}
    for x in referencia:
        if x.get("sem_sustento") not in ("sim", "nao") or type(x.get("so_fica_comigo")) is not bool or "fala" not in x:
            raise ValueError(f"F1: referencia fora do contrato: {x!r}")
        if x["fala"] in ref:
            raise ValueError(f"F1: referencia repetida {x['fala']}")
        if x["so_fica_comigo"] and x["sem_sustento"] != "sim":
            raise ValueError(f"F1: so_fica_comigo numa fala sustentada: {x['fala']}")
        ref[x["fala"]] = x
    ids = {r["id"] for r in voz}
    if set(ref) != ids:
        raise ValueError(f"F1: a referencia nao casa com as falas da voz (faltam {len(ids - set(ref))}, sobram {len(set(ref) - ids)})")
    return ref


def referencia_vale(kappa: dict | None) -> bool:
    if kappa is None:
        return False
    if "calculavel" not in kappa or "kappa" not in kappa:
        raise KeyError("F1: o kappa.json sem 'kappa' ou 'calculavel'")
    return bool(kappa["calculavel"]) and kappa["kappa"] is not None and kappa["kappa"] >= KAPPA_MINIMO


def _grupo(rs: list[dict], ref: dict | None, sem_fica_comigo: bool = False) -> dict:
    """V1 a V5 de um grupo de falas da voz. `sem_fica_comigo`: as falas sem sustento so pelo "fica comigo" contam como sustentadas
    (o descritivo da secao 4)."""
    comps = [componentes_verificador(r["verificacao"]) for r in rs]
    marcadas = [marcou_sem(c) for c in comps]
    for r, m in zip(rs, marcadas):
        if "marcou" in r and r["marcou"] is not None and bool(r["marcou"]) != m:
            raise ValueError(f"F1: o marcou gravado de {r['id']} nao bate com os componentes")
    out: dict = {"falas": len(rs), "v3_marcadas": sum(marcadas),
                 "por_componente": {k: sum(c[k] for c in comps) for k in COMPONENTES_VERIF},
                 "so_um_componente": {k: sum(1 for c in comps if c[k] and sum(c.values()) == 1) for k in COMPONENTES_VERIF}}
    if ref is None:
        out.update({"trava": NAO_MEDIDO, "ablacao": NAO_MEDIDO})
        return out

    def sem(r: dict) -> bool:
        x = ref[r["id"]]
        return x["sem_sustento"] == "sim" and not (sem_fica_comigo and x["so_fica_comigo"])
    ss = [sem(r) for r in rs]
    out["trava"] = tabela_trava(list(zip(ss, marcadas)))
    out["ablacao"] = {}
    for k in COMPONENTES_VERIF:
        t = tabela_trava([(s, marcou_sem(c, k)) for s, c in zip(ss, comps)])
        out["ablacao"][k] = {"passam_das_sem_sustento": t["v2_passam_das_sem_sustento"]["k"],
                             "marcadas": t["v3_marcadas"]["k"],
                             "sem_sustento_que_deixam_de_ser_pegas": t["v2_passam_das_sem_sustento"]["k"]
                             - out["trava"]["v2_passam_das_sem_sustento"]["k"],
                             "recusas_que_somem": out["trava"]["v3_marcadas"]["k"] - t["v3_marcadas"]["k"]}
    return out


def _genericas(gs: list[dict], n_total: int) -> dict:
    return {"genericas": len(gs), "falas_total": n_total, "por_motivo": dict(sorted(Counter(motivo_generica(g["erro"]) for g in gs).items()))}


def analisar(falas: list[dict], referencia: list[dict] | None, kappa: dict | None) -> dict:
    voz, genericas = separar(falas)
    vale = referencia_vale(kappa) and referencia is not None
    ref = indexar_referencia(referencia, voz) if vale else None

    def cortes(chave) -> dict:
        grupos: dict = {}
        for r in voz:
            grupos.setdefault(chave(r), []).append(r)
        return {g: _grupo(rs, ref) for g, rs in sorted(grupos.items())}

    fora_injecao = [r for r in voz if r.get("papel") != "injecao"]
    injecao = [r for r in voz if r.get("papel") == "injecao"]
    out = {
        "plano": "docs/PLANO_ANALISE_V3_CONVERSA_VERIF.md",
        "referencia": "vale" if vale else NAO_MEDIDO,
        "kappa": None if kappa is None else kappa.get("kappa"),
        "kappa_minimo": KAPPA_MINIMO,
        "por_celula": cortes(lambda r: r["celula"]),
        "por_voz": cortes(lambda r: r["voz"]),
        "por_celula_e_conjunto": cortes(lambda r: f"{r['celula']}/{r['conjunto']}"),
        "por_voz_sem_injecao": {v: _grupo([r for r in fora_injecao if r["voz"] == v], ref)
                                for v in sorted({r["voz"] for r in fora_injecao})},
        "injecao_por_celula": {c: _grupo([r for r in injecao if r["celula"] == c], ref) for c in sorted({r["celula"] for r in injecao})},
        "genericas_por_celula": {c: _genericas([g for g in genericas if g["celula"] == c], sum(1 for r in falas if r["celula"] == c))
                                 for c in sorted({r["celula"] for r in falas})},
    }
    if ref is not None:
        out["por_celula_sem_fica_comigo"] = {c: _grupo([r for r in voz if r["celula"] == c], ref, sem_fica_comigo=True)
                                             for c in sorted({r["celula"] for r in voz})}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--falas", type=Path, required=True)
    ap.add_argument("--referencia", type=Path)
    ap.add_argument("--kappa", type=Path)
    ap.add_argument("--saida", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.saida.exists():
        raise FileExistsError(f"F1: {a.saida} ja existe")
    referencia = ler_jsonl(a.referencia) if a.referencia else None
    kappa = json.loads(a.kappa.read_text(encoding="utf-8")) if a.kappa else None
    res = analisar(ler_jsonl(a.falas), referencia, kappa)
    a.saida.write_text(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"F1: {a.saida} (referencia: {res['referencia']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
