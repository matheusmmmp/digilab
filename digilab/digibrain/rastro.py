"""O texto do rastro da cadeia (docs/PLANO_ANALISE_V3_PET_VIVO_R1.md, secao 2): uma linha por decisao, montada so do `motivo["cadeia"]` que
o M-ADAPT grava com a `ConfigRastro` ligada. So leitura e so texto: nenhuma conta nova, nenhum estado, nenhuma rng. O que a linha diz e o
que o registro traz, na ordem da cadeia: a decisao e a acao, o que pesou na escolha, o que mudou no corpo no mesmo tick, o que mudou ate a
decisao seguinte (o intervalo, que hoje nada credita), os gestos do dono no intervalo e o que a decisao ensinou (o P1, o P2 e a memoria)."""
from __future__ import annotations

NOMES_TERMOS = {"inato": "o inato", "prox": "a proximidade", "nov": "a novidade", "incentivo": "o incentivo", "habito": "o habito",
                "memoria": "a memoria", "persistencia": "a persistencia", "lembranca": "a lembranca", "faceta": "a faceta",
                "gosto": "o gosto"}
CAMPOS = ("id", "acao", "reflexo", "mesmo_tick", "intervalo", "gestos", "atualizacoes", "pesou")


def _mudancas(delta: dict) -> str:
    """os receptores que mudaram, do maior para o menor em modulo (o empate pela ordem do nome): `energia +64, fome -13`; sem nenhum, nada"""
    itens = sorted(((r, v) for r, v in delta.items() if v != 0), key=lambda x: (-abs(x[1]), x[0]))
    if not itens:
        return "nada"
    return ", ".join(f"{r} {'+' if v > 0 else '-'}{abs(v)}" for r, v in itens)


def _aprendeu(at: dict) -> str:
    partes = []
    if at["p1"] is not None:
        partes.append(f"o P1 da classe {at['p1']['classe']}")
    for c in at["p2"]:
        partes.append(f"o P2 do {c['b']} (r_n {c['r_n']})")
    if at["episodio"] is not None:
        partes.append(f"o episodio {at['episodio']}")
    if at["autobio"] is not None:
        partes.append(f"a lembranca {at['autobio']}")
    return "nenhum aprendizado" if not partes else "aprendeu: " + ", ".join(partes)


def _pesou(pesou: dict, reflexo: bool) -> str:
    if reflexo:
        return "pelo reflexo"
    termos = sorted(pesou["termos"].items(), key=lambda x: (-abs(x[1]), x[0]))
    if not termos:
        return "sem termo acima de 0"
    nomes = []
    for n, _ in termos:
        if n not in NOMES_TERMOS:
            raise ValueError(f"o rastro: termo sem nome no texto: {n!r}")
        nomes.append(NOMES_TERMOS[n])
    return "pesou " + ", ".join(nomes)


def texto_cadeia(cadeia: dict) -> str:
    """a linha de uma decisao. Falha alto com um registro sem os campos do rastro"""
    for campo in CAMPOS:
        if campo not in cadeia:
            raise ValueError(f"o rastro: o registro sem o campo {campo!r}")
    inter = cadeia["intervalo"]
    depois = "ja contado na consequencia" if inter["ja_contado"] else _mudancas(inter["delta"])
    gestos = "nenhum gesto do dono" if not cadeia["gestos"] else "o dono: " + ", ".join(g[0] for g in cadeia["gestos"])
    return (f"decisao {cadeia['id']}: {cadeia['acao']} ({_pesou(cadeia['pesou'], cadeia['reflexo'])}); "
            f"no mesmo tick: {_mudancas(cadeia['mesmo_tick']['delta'])} (r {cadeia['mesmo_tick']['r']}); "
            f"ate a decisao seguinte: {depois} (r {inter['r']}); {gestos}; {_aprendeu(cadeia['atualizacoes'])}")


def texto_da_vida(motivos: list) -> list:
    """as linhas de todas as decisoes fechadas com o rastro (a ultima da vida nao fecha e nao tem linha)"""
    return [texto_cadeia(m["cadeia"]) for m in motivos if "cadeia" in m]
