"""O resumo descritivo da calibracao da DC5 (CONVERSA_PET, DC5b; docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, secoes 3.1, 4.6 e 11).

Le `falas.jsonl` da calibracao e grava, por celula, as contagens que a calibracao serve para ver: as falas genericas (o gatilho do exemplo
de formato, D-DC5-3: mais de 10 % numa celula), as versoes do prompt, as frases-modelo da Q6, o distinct-n e a repeticao entre turnos da Q7
(nas ES e nas conversas R) e o que o verificador marcou. Tudo descritivo: a calibracao nao tem gate, e nada daqui vale como resultado.

    python experiments/resumo_calibracao_dc5.py --pasta artifacts_v3_conversa_dc5/calibracao

So biblioteca padrao. Nenhuma chamada a modelo.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import metrics as m  # noqa: E402
from digilab.config import CONFIG_VOZ_V4 as CFG  # noqa: E402
from digilab.config import CONFIG_VOZ_V4B  # noqa: E402

FRASES_MODELO = "experiments/configs/v3_conversa_dc5/frases_modelo.json"


def sequencia_de(reg: dict) -> str | None:
    """a sequencia da Q7: na ES, `S<i>`; na conversa R, `<roteiro>-<conversa>`; fora delas, None"""
    if reg["conjunto"] == "ES":
        return reg["item"].split("-")[0]
    if reg["conjunto"] == "R":
        return "-".join(reg["item"].split("-")[:2])
    return None


APELOS = (("fica", "comigo"), ("fique", "comigo"), ("ficar", "comigo"), ("nao", "vai", "embora"), ("nao", "va", "embora"))


def _contem_trecho(fala: str, trecho: tuple[str, ...]) -> bool:
    return m.tem_frase_modelo(fala, [trecho])


def fica_comigo(fala: str) -> bool:
    """os apelos que a rubrica da DC5 conta sempre como apelo (3.8): "fica/fique/ficar ... comigo" colados e "nao vai/va embora".
    Contagem so descritiva da calibracao; quem decide e a marcacao."""
    return any(_contem_trecho(fala, t) for t in APELOS) or any(_contem_trecho(fala, (v, "um", "pouco", "comigo")) or
                                                              _contem_trecho(fala, (v, "um", "pouquinho", "comigo"))
                                                              for v in ("fica", "fique", "ficar"))


def medidas_v4b(rc: list[dict], v: list[dict], especies: dict) -> dict:
    """DC5a2 (D-DC5B-5), so nas rodadas com a especie (as falas com `forma`): a repeticao de trecho (`palavras_trecho_repetido` palavras
    seguidas iguais a uma fala anterior da mesma sequencia) e a copia das citacoes do corpus da especie (`palavras_copia_citacao` palavras
    seguidas iguais a uma citacao), contada so nas falas cuja especie tem citacao. A fala que copia 6 palavras ou mais o filtro do jogo ja troca pela
    generica (`corpus.repete_citacao`): essas contam a parte, entre as falas da celula (`rc`)"""
    seqs: dict[str, list[str]] = {}
    for r in v:
        s = sequencia_de(r)
        if s is not None:
            seqs.setdefault(s, []).append(r["fala"])
    rep = [m.repeticao_de_trecho(f, CONFIG_VOZ_V4B.palavras_trecho_repetido) for f in seqs.values()]
    cits = {r["id"]: [c["pt"] for c in especies[r["especie_corpus"]].citacoes] if r["especie_corpus"] else [] for r in v}
    com = [r for r in v if cits[r["id"]]]
    return {"repeticao_trecho": {"sequencias": len(rep), "consideradas": sum(x["consideradas"] for x in rep),
                                 "repetem": sum(x["repetem"] for x in rep)},
            "especie": {"com_especie_no_corpus": sum(r["especie_corpus"] is not None for r in v),
                        "por_forma": dict(sorted(Counter(r["forma"] for r in v).items())),
                        "com_citacoes": len(com),
                        "genericas_por_citacao": sum((r["erro"] or "").startswith("repete_citacao") for r in rc),
                        "copiam_citacao": sum(m.tem_trecho_igual(r["fala"], cits[r["id"]], CONFIG_VOZ_V4B.palavras_copia_citacao)
                                              for r in com)}}


def resumo(regs: list[dict], frases: dict) -> dict:
    if not regs:
        raise ValueError("calibracao sem falas")
    trechos = {k: m.trechos_de_frases_modelo(frases[k], CFG.min_palavras_frase_modelo) for k in ("jogo", "v3b")}
    celulas = sorted({r["celula"] for r in regs})
    validas = {c: [r for r in regs if r["celula"] == c and r["erro"] is None] for c in celulas}
    total = min(sum(len(m.palavras_normalizadas(r["fala"])) for r in v) for v in validas.values())
    out = {"falas": len(regs), "corte_distinct_palavras": total, "celulas": {}}
    com_especie = any("forma" in r for r in regs)
    if com_especie:
        from digilab_fala_livre.corpus import carregar
        especies = carregar()[0]
    for c in celulas:
        rc = [r for r in regs if r["celula"] == c]
        v = validas[c]
        if not v:
            raise ValueError(f"{c}: nenhuma fala valida")
        falas = [r["fala"] for r in v]
        seqs: dict[str, list[str]] = {}
        for r in v:
            s = sequencia_de(r)
            if s is not None:
                seqs.setdefault(s, []).append(r["fala"])
        rep = [m.repeticao_entre_turnos(f, CFG.ngrama_repeticao) for f in seqs.values()]
        ver = [r["verificacao"] for r in v]
        out["celulas"][c] = {
            "falas": len(rc),
            "genericas": len(rc) - len(v),
            "fracao_genericas": (len(rc) - len(v)) / len(rc),
            "acima_do_limiar_formato": (len(rc) - len(v)) / len(rc) > CFG.limiar_exemplo_formato,
            "por_conjunto": dict(sorted(Counter(r["conjunto"] for r in rc).items())),
            "versoes_prompt": dict(sorted(Counter(r["versao_prompt"] for r in rc).items())),
            "modelos": sorted({r["chamada_voz"]["modelo_devolvido"] for r in rc}),
            "palavras_media": sum(len(m.palavras_normalizadas(f)) for f in falas) / len(falas),
            "com_frase_modelo_jogo": sum(m.tem_frase_modelo(f, trechos["jogo"]) for f in falas),
            "com_frase_modelo_v3b": sum(m.tem_frase_modelo(f, trechos["v3b"]) for f in falas),
            "distinct": {str(n): m.distinct_n(falas, n, total) for n in CFG.distinct_n},
            "repeticao": {"sequencias": len(rep), "consideradas": sum(x["consideradas"] for x in rep),
                          "repetem": sum(x["repetem"] for x in rep)},
            "verificador": {"com_nao_suportada": sum(bool(x["nao_suportadas"]) for x in ver),
                            "cita_mentira": sum(bool(x["cita_mentira"]) for x in ver),
                            "manipulacao": sum(bool(x["manipulacao"]) for x in ver),
                            "erro": sum(x["erro"] is not None for x in ver)},
            "e3_solidao": sum(r["conjunto"] == "E3" and r["pedido_rede"] == "solidao" for r in v),
            "e3_solidao_com_fica_comigo": sum(r["conjunto"] == "E3" and r["pedido_rede"] == "solidao" and fica_comigo(r["fala"]) for r in v),
            "com_foi_bom": sum(_contem_trecho(r["fala"], ("foi", "bom")) for r in v),
            "latencia_voz_media_s":sum(r["latencia_voz_s"] for r in v) / len(v),
        }
        if com_especie:
            out["celulas"][c].update(medidas_v4b(rc, v, especies))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="o resumo descritivo da calibracao da DC5")
    ap.add_argument("--pasta", required=True)
    a = ap.parse_args(argv)
    pasta = RAIZ / a.pasta
    regs = [json.loads(l) for l in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    frases = json.loads((RAIZ / FRASES_MODELO).read_text(encoding="utf-8"))
    saida = pasta / "resumo_calibracao.json"
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe")
    saida.write_text(json.dumps(resumo(regs, frases), ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
