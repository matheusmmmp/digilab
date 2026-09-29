"""Almanaque do Digimundo (DESIGN_VOZ_PROPRIA, secao 10): o Digimundo e um reflexo da internet.

`almanaque.json` e versionado e revisado a mao (texto proprio; sem memes ofensivos, politicos ou de odio). O sha256
dele vai para o registro de cada fala. Uma entrada vira o fato [W1] ("coisa que ouvi no Digimundo"), que sustenta
afirmacoes sobre a internet e o mundo, NUNCA sobre a vida do pet ou do dono (verificador).

Na fala espontanea entra com chance CHANCE_ESPONTANEA, sorteada na rng da fala; na Conversar, quando o jogador puxa
o assunto (a apresentacao escolhe o id).
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

ARQUIVO = Path(__file__).with_name("almanaque.json")
CHANCE_ESPONTANEA = 0.15          # PROPOSTO (DESIGN_VOZ_PROPRIA, secao 10)
TEMAS = ("internet", "games", "meme_global", "meme_br")
MAX_TEXTO = 80
_PROIBIDOS = set("[]{}\n\r")


class AlmanaqueInvalido(ValueError):
    """Arquivo fora do formato ou id desconhecido: falha alto."""


def carregar(caminho: Path = ARQUIVO) -> tuple[list[dict], str]:
    """(entradas, sha256 do arquivo). Confere o formato de cada entrada."""
    bruto = caminho.read_bytes()
    d = json.loads(bruto.decode("utf-8"))
    if set(d) != {"versao", "descricao", "entradas"}:
        raise AlmanaqueInvalido(f"chaves do almanaque: {sorted(d)}")
    ids = set()
    for e in d["entradas"]:
        if set(e) != {"id", "tema", "epoca", "nomes", "texto"}:
            raise AlmanaqueInvalido(f"entrada com chaves {sorted(e)}")
        if e["id"] in ids:
            raise AlmanaqueInvalido(f"id repetido: {e['id']}")
        ids.add(e["id"])
        if e["tema"] not in TEMAS or not isinstance(e["nomes"], list):
            raise AlmanaqueInvalido(f"{e['id']}: tema ou nomes invalidos")
        t = e["texto"]
        if not isinstance(t, str) or not t.strip() or len(t) > MAX_TEXTO or _PROIBIDOS & set(t):
            raise AlmanaqueInvalido(f"{e['id']}: texto fora do formato")
    return d["entradas"], hashlib.sha256(bruto).hexdigest()


_CACHE: dict[str, dict] | None = None


def entrada(id_: str) -> dict:
    global _CACHE
    if _CACHE is None:
        _CACHE = {e["id"]: e for e in carregar()[0]}
    if id_ not in _CACHE:
        raise AlmanaqueInvalido(f"id do almanaque desconhecido: {id_!r}")
    return _CACHE[id_]


def sortear(rng: random.Random, chance: float = CHANCE_ESPONTANEA) -> str | None:
    """id de uma entrada com a chance dada, ou None. Consome sempre dois sorteios (numeros comuns)."""
    u, k = rng.random(), rng.random()
    if u >= chance:
        return None
    ids = sorted(e["id"] for e in carregar()[0])
    return ids[int(k * len(ids))]
