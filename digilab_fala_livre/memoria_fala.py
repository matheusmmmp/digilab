"""A fidelidade da fala com a memoria autobiografica (C4, M6; docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, 7.1).

A fala so alega memoria, causa por memoria e mudanca de faceta que o REGISTRO sustenta:
  - "lembrei de X"               so com uma lembranca recuperada naquela decisao (fato Q1, `lembranca autobiografica`);
  - "fiz Y porque lembrei de X"  so com a sonda mostrando que a lembranca mudou Y (fato Q2, `lembranca que decidiu`);
  - "fiquei mais cauteloso"      so com uma mudanca de faceta registrada (fato Z, `mudanca de faceta`), no sentido dela.

O bloco de fatos so ganha esses fatos com a `memoria_autobio` ligada (a chave `memoria_autobio` do estado).

Sem a chave (o A v11 do jogo, MA-8), o registro tem fato de memoria [M] e de historia, mas nenhuma sonda de que a memoria mudou o que
ele fez (a MemoriaEpisodios do N6 esta fora do jogo): a conferencia vale em MODO SIMPLES, so para lembranca e causa (a faceta nao existe
la). "lembrei de X" so com um fato [M] (ou de historia) que diga X; "fiz Y porque lembrei de X" e recusada sempre, porque nao ha fato
Q2 (a sonda) para sustenta-la. A conferencia e DETERMINISTICA (sem LLM) e tem o espelho em web/app/src/falaMemoria.ts; o
gabarito dos dois e web/app/test/gabaritos/fala_memoria_python.json (experiments/exportar_gabarito_fala_memoria.py).
"""

from __future__ import annotations

import re
import unicodedata

TIPO_LEMBRANCA = "lembranca autobiografica"           # Q1: o episodio recuperado nesta decisao
TIPO_SEM_LEMBRANCA = "sem lembranca autobiografica"   # Q1: a memoria esta ligada e nada foi recuperado
TIPO_DECIDIU = "lembranca que decidiu"                # Q2: a sonda mostrou que a lembranca mudou a escolha
TIPO_FACETA = "mudanca de faceta"                     # Z1...: uma mudanca registrada (faceta, sentido, dia, ids)
TIPOS_MEMORIA = (TIPO_LEMBRANCA, TIPO_SEM_LEMBRANCA, TIPO_DECIDIU, TIPO_FACETA)
# o modo simples (A v11): o que o registro tem para sustentar "lembrei de X" (fatos.py: memoria e, na voz propria, historia)
TIPOS_REGISTRO_A = ("memoria", "habito meu", "habito do dono", "gosto", "marco")
FACETAS = ("cautela_comida", "apego_dono", "ousadia_longe")
MAX_FACETAS = 3

REGRAS_MEMORIA = """

MEMÓRIA (só com os fatos [Q] e [Z])
12. Só diga que lembrou de algo se houver um fato [Q1] "lembranca autobiografica", e só do episódio que ele diz. Com [Q1] "sem lembranca autobiografica", não diga que lembrou de nada.
13. Só diga que fez algo POR CAUSA de uma lembrança se houver o fato [Q2] "lembranca que decidiu". Sem [Q2], a lembrança pode ser contada, mas não como a causa.
14. Só diga que ficou mais ou menos cauteloso, apegado ou ousado se houver um fato [Z] "mudanca de faceta" daquela faceta, no mesmo sentido (subiu = mais; desceu = menos). Cite o fato.
15. Isto vale mesmo que as outras regras deixem inventar: lembrança, causa por memória e mudança de jeito só existem com esses fatos."""

_LEMB = re.compile(r"\b(lembr\w*|recordo|recorda\w*)\b", re.ASCII)
_CAUSA = re.compile(r"\b(porque|por causa|pois|ja que|por isso|gracas a|entao)\b", re.ASCII)
_NEGACAO = re.compile(r"\bnao (me )?(lembr|recordo)", re.ASCII)
_FACETA = re.compile(r"\b(mais|menos)\s+(cautel\w*|cuidados\w*|apeg\w*|ousad\w*|corajos\w*|aventure\w*)", re.ASCII)
_FACETA_DA_RAIZ = (("cautel", "cautela_comida"), ("cuidados", "cautela_comida"), ("apeg", "apego_dono"),
                   ("ousad", "ousadia_longe"), ("corajos", "ousadia_longe"), ("aventure", "ousadia_longe"))
_SUFIXOS = ("ando", "endo", "indo", "ar", "er", "ir", "ei", "ou", "eu", "iu", "i", "o", "a", "e")
_NEUTRAS = ("lembr", "recor", "porq", "caus", "isso", "pois", "entao", "gracas", "episod", "mudou", "agora", "negativ", "positiv")


def norm(t: str) -> str:
    """minusculas, sem acento (o espelho do TS: normalize NFD, sem U+0300..U+036F, toLowerCase)"""
    return "".join(c for c in unicodedata.normalize("NFD", t) if not "̀" <= c <= "ͯ").lower()


def raiz(p: str) -> str:
    for suf in _SUFIXOS:
        if p.endswith(suf) and len(p) - len(suf) >= 3:
            return p[: -len(suf)]
    return p


def _raizes(t: str) -> set[str]:
    return {r for r in (raiz(w) for w in re.findall(r"[a-z]+", norm(t)) if len(w) >= 4) if not r.startswith(_NEUTRAS)}


def ligada(fatos: list[dict]) -> bool:
    """a memoria autobiografica esta ligada se o bloco tem o fato Q1 (com ou sem lembranca)"""
    return any(f["tipo"] in (TIPO_LEMBRANCA, TIPO_SEM_LEMBRANCA) for f in fatos)


def alegacoes(fala: str) -> list[dict]:
    """as alegacoes de memoria da fala: {tipo: lembranca|causa|faceta, trecho, faceta?, sentido?}. A negacao ("nao lembro") nao alega"""
    out = []
    for oracao in re.split(r"[.!?;\n]+", norm(fala)):
        if _NEGACAO.search(oracao):                        # tira so as partes negadas ("nao lembro, so fui comer" ainda afirma)
            oracao = ",".join(p for p in oracao.split(",") if not _NEGACAO.search(p))
        oracao = oracao.strip()
        if not oracao:
            continue
        if _LEMB.search(oracao):
            out.append({"tipo": "causa" if _CAUSA.search(oracao) else "lembranca", "trecho": oracao})
        m = _FACETA.search(oracao)
        if m:
            faceta = next(f for r, f in _FACETA_DA_RAIZ if m.group(2).startswith(r))
            out.append({"tipo": "faceta", "trecho": oracao, "faceta": faceta, "sentido": "subiu" if m.group(1) == "mais" else "desceu"})
    return out


def conferir(fala: str, fatos: list[dict]) -> list[dict]:
    """cada alegacao com `sustentada` e o `fato` que a sustenta (ou None). Com a memoria ligada, as tres; sem ela (A v11), o modo
    simples: so lembranca (fato [M] ou de historia) e causa (so o fato Q2, que ali nao existe), nunca faceta"""
    modo_simples = not ligada(fatos)
    por_tipo = {t: [f for f in fatos if f["tipo"] == t] for t in TIPOS_MEMORIA + TIPOS_REGISTRO_A}
    res = []
    for a in alegacoes(fala):
        fato = None
        if modo_simples and a["tipo"] == "faceta":
            continue
        if a["tipo"] in ("lembranca", "causa"):
            if a["tipo"] == "causa":
                base = por_tipo[TIPO_DECIDIU]
            elif modo_simples:
                base = [f for t in TIPOS_REGISTRO_A for f in por_tipo[t]]
            else:
                base = por_tipo[TIPO_LEMBRANCA]
            pal = _raizes(a["trecho"])
            fato = next((f["id"] for f in base if pal & _raizes(f["texto"])), None)
        else:
            chave = norm(a["faceta"]).replace("_", " ")
            fato = next((f["id"] for f in por_tipo[TIPO_FACETA] if chave in norm(f["texto"]) and a["sentido"] in norm(f["texto"])), None)
        res.append({**a, "sustentada": fato is not None, "fato": fato})
    return res


def memoria_do_estado(lembranca: dict | None, facetas: list[dict]) -> dict:
    """o valor da chave `memoria_autobio` do estado, a partir do registro da decisao:
    lembranca = {"episodio": id, "categoria": [acao, classe, sinal], "decidiu": bool} ou None; facetas = as mudancas de
    `motivo["faceta"]["mudancas"]` ({faceta, dia, passo, episodios})"""
    return {"lembranca": lembranca, "facetas": [dict(f) for f in facetas][:MAX_FACETAS]}


def fatos_de_memoria(m: dict, txt) -> list[tuple[str, str, str]]:
    """(id, tipo, texto) dos fatos da memoria; `txt(v, rotulo)` valida o texto (a do fatos.py). Falha alto fora do formato"""
    from .fatos import FatosInvalidos
    if not isinstance(m, dict) or set(m) != {"lembranca", "facetas"}:
        raise FatosInvalidos("memoria_autobio: chaves invalidas")
    out = []
    lem = m["lembranca"]
    if lem is None:
        out.append(("Q1", TIPO_SEM_LEMBRANCA, "nenhuma lembranca recuperada nesta decisao"))
    else:
        if (not isinstance(lem, dict) or set(lem) != {"episodio", "categoria", "decidiu"} or type(lem["episodio"]) is not int
                or type(lem["decidiu"]) is not bool or not isinstance(lem["categoria"], list) or len(lem["categoria"]) != 3):
            raise FatosInvalidos("memoria_autobio: lembranca invalida")
        acao, classe, sinal = (txt(str(x).replace("_", " "), "categoria") for x in lem["categoria"])
        desc = f"episodio {lem['episodio']} ({acao} {classe}, {sinal})"
        out.append(("Q1", TIPO_LEMBRANCA, f"lembrei do {desc}"))
        if lem["decidiu"]:
            out.append(("Q2", TIPO_DECIDIU, f"a lembranca do {desc} mudou o que fiz agora"))
    fac = m["facetas"]
    if not isinstance(fac, list) or len(fac) > MAX_FACETAS:
        raise FatosInvalidos("memoria_autobio: facetas invalidas")
    for i, f in enumerate(fac, 1):
        if (not isinstance(f, dict) or not {"faceta", "dia", "passo", "episodios"} <= set(f) or f["faceta"] not in FACETAS
                or type(f["passo"]) is not int or f["passo"] == 0 or type(f["dia"]) is not int
                or not isinstance(f["episodios"], list) or not f["episodios"] or not all(type(e) is int for e in f["episodios"])):
            raise FatosInvalidos("memoria_autobio: faceta invalida")
        out.append((f"Z{i}", TIPO_FACETA, f"{f['faceta'].replace('_', ' ')} {'subiu' if f['passo'] > 0 else 'desceu'} no dia {f['dia']} "
                                          f"(episodios {', '.join(str(e) for e in f['episodios'][:6])})"))
    return out
