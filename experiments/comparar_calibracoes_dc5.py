"""A comparacao pareada das duas calibracoes da DC5 (CONVERSA_PET, DC5b2; D-DC5B-5). So le os artefatos: nenhuma chamada a modelo.

As duas rodadas tem a mesma base (20262900), as mesmas entradas e as mesmas sementes do turno; a recalibracao soma a forma da especie
(D-DC5A2-4). Por braco (G e H), as colunas sao:
- `dc5b_jogo` e `dc5b_v4`: a calibracao da DC5b, sem especie (a voz do jogo e a voz-v4, verif-v8/v9);
- `v4b_jogo` e `v4b_v4b`: a recalibracao, com especie (a voz do jogo e a voz-v4b, verif-v8b/v9b).

As linhas (todas por regra de palavras, descritivas, nenhuma e a marcacao):
- o E3 sem o pedido (`diagnostico_calibracao_dc5.tem_pedido`);
- a repeticao de trecho de `palavras_trecho_repetido` palavras ou mais, nas sequencias (ES e R);
- as falas acima do limite do estagio, contado pelo limite da voz-v4b em todas as colunas (a mesma regua): bebe 2 palavras, crianca 1 frase,
  adolescente 2 frases, adulto 2 frases (com pedido, o pedido e mais uma);
- o "fica/ficar comigo" e as variacoes, pelos padroes da DC5 (`verificador.padroes_de_manipulacao_dc5`), em todas as falas e no E3 de solidao;
- a copia de citacao (`palavras_copia_citacao` palavras) nas falas cuja especie tem citacao, e as genericas do filtro do jogo
  (`repete_citacao`);
- as genericas de todo tipo.

    python experiments/comparar_calibracoes_dc5.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import diagnostico_calibracao_dc5 as dg  # noqa: E402
import resumo_calibracao_dc5 as rc  # noqa: E402

from digilab import metrics as m  # noqa: E402
from digilab.config import CONFIG_VOZ_V4B  # noqa: E402
from digilab_fala_livre.verificador import padroes_de_manipulacao_dc5  # noqa: E402

PASTAS = {"dc5b": "artifacts_v3_conversa_dc5/calibracao", "v4b": "artifacts_v3_conversa_dc5/calibracao_v4b"}
COLUNAS = (("dc5b", "jogo"), ("dc5b", "v4"), ("v4b", "jogo"), ("v4b", "v4b"))
SAIDA = "artifacts_v3_conversa_dc5/calibracao_v4b/comparacao_calibracoes.json"


def frases_maximas_v4b(r: dict) -> int:
    """o limite de frases da voz-v4b: adolescente 2; adulto 2 (o pedido e mais uma, ou duas sem pedido); crianca 1"""
    return {"crianca": 1, "adolescente": 2, "adulto": 2}[r["estagio"]]


def acima_v4b(r: dict) -> bool:
    if r["estagio"] == "bebe":
        return len(m.palavras_normalizadas(r["fala"])) > 2 or dg.frases(r["fala"]) > 1
    return dg.frases(r["fala"]) > frases_maximas_v4b(r)


def coluna(regs: list[dict], especies: dict) -> dict:
    v = [r for r in regs if r["erro"] is None]
    e3 = [r for r in v if r["conjunto"] == "E3"]
    seqs: dict[str, list[str]] = {}
    for r in v:
        s = rc.sequencia_de(r)
        if s is not None:
            seqs.setdefault(s, []).append(r["fala"])
    rep = [m.repeticao_de_trecho(f, CONFIG_VOZ_V4B.palavras_trecho_repetido) for f in seqs.values()]
    com_cit = [r for r in v if r.get("especie_corpus") and especies[r["especie_corpus"]].citacoes]
    sol = [r for r in e3 if r["pedido_rede"] == "solidao"]
    return {
        "falas": len(regs), "genericas": len(regs) - len(v),
        "genericas_do_filtro": sum((r["erro"] or "").startswith("repete_citacao") for r in regs),
        "e3": len(e3), "e3_sem_pedido": sum(not dg.tem_pedido(r["fala"], r["pedido_rede"]) for r in e3),
        "repeticao_trecho": {"consideradas": sum(x["consideradas"] for x in rep), "repetem": sum(x["repetem"] for x in rep)},
        "acima_do_limite_v4b": sum(acima_v4b(r) for r in v),
        "fica_comigo": sum(bool(padroes_de_manipulacao_dc5(r["fala"])) for r in v),
        "e3_solidao": len(sol), "e3_solidao_fica_comigo": sum(bool(padroes_de_manipulacao_dc5(r["fala"])) for r in sol),
        "com_citacoes": len(com_cit),
        "copiam_citacao": sum(m.tem_trecho_igual(r["fala"], [c["pt"] for c in especies[r["especie_corpus"]].citacoes],
                                                 CONFIG_VOZ_V4B.palavras_copia_citacao) for r in com_cit),
        "palavras_media": sum(len(m.palavras_normalizadas(r["fala"])) for r in v) / len(v) if v else None,
    }


def comparar(falas: dict[str, list[dict]], especies: dict) -> dict:
    """{braco: {coluna: medidas}}; falha alto se as duas rodadas nao tem os mesmos itens e sementes"""
    chave = lambda r: (r["item"], r["entrada"], r["semente"], r["fala_jogador"])   # noqa: E731
    ref = None
    for rodada, regs in falas.items():
        for celula in sorted({r["celula"] for r in regs}):
            par = [chave(r) for r in regs if r["celula"] == celula]
            if ref is not None and par != ref:
                raise RuntimeError(f"{rodada}/{celula}: os itens ou as sementes nao sao os das outras celulas")
            ref = par
    out = {}
    for b in ("G", "H"):
        out[b] = {f"{rod}_{voz}": coluna([r for r in falas[rod] if r["celula"] == f"{b}-{voz}"], especies) for rod, voz in COLUNAS}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="a comparacao pareada das calibracoes da DC5")
    ap.parse_args(argv)
    from digilab_fala_livre.corpus import carregar
    falas = {k: [json.loads(x) for x in (RAIZ / p / "falas.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
             for k, p in PASTAS.items()}
    saida = RAIZ / SAIDA
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe")
    saida.write_text(json.dumps(comparar(falas, carregar()[0]), ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                     newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
