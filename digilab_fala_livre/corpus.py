"""Corpus de personalidade Digimon (DESIGN_VOZ_PROPRIA, secao 11): o JEITO da especie, nunca fatos da vida do pet.

`corpus_especies.json` e versionado (o sha256 vai para o registro de cada fala). O carregador aplica o filtro
das marcas da auditoria, e falha alto em marca desconhecida:
  - entram [VERIFICADO] e [VERIFICADO EM OUTRA FONTE], so de jogos com veredito APTO ou APTO COM RESSALVAS;
  - [PARCIAL] entra so se a parte com suporte foi reescrita na auditoria (`"reescrito": true`);
  - [OUTRA MIDIA] (anime) so com `meta.liberar_outra_midia` e marcada como anime;
  - [INFERENCIA], [DIVERGENTE], [SEM FONTE] e [FONTE INVALIDA] ficam de fora.
Traco e jeito de falar vao para o bloco de ESTILO do prompt: guiam o tom e nao sustentam afirmacao nenhuma.
Citacoes sao so referencia de tom (ate 3 por especie, 1-2 frases); o filtro `repete_citacao` reprova a fala que
copia 6 ou mais palavras seguidas de uma citacao. Interacoes entram quando o outro Digimon esta em cena (rival de
luta, NPC da campanha), como rixa da especie, nunca como algo que aconteceu com o pet.
honestidade_especie: HONESTIDADE_ENGANADOR se algum traco que entrou for de enganador (`"enganador": true`), senao 1.

Filtro do alfabeto (2026-09-30): traco, jeito de falar e interacao cujo TEXTO tem letra fora do alfabeto latino (o corpus
descreve o registro japones das especies: pronomes como おいら, finais como 〜だぜ) ficam FORA do bloco de estilo e contam
em `descartados["NAO LATINO"]`. Com esses itens no pedido o gemma2:9b respondia com trechos em japones, e `saida.ler`
rejeita a fala inteira (vira a generica). O arquivo do corpus nao muda (o sha256 continua o mesmo); as citacoes `pt` sao
latinas por construcao. `carregar(..., so_latino=False)` desliga o filtro (so para medir o antes e o depois).
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

ARQUIVO = Path(__file__).with_name("corpus_especies.json")
HONESTIDADE_ENGANADOR = 0.7        # = digilab.config.ConfigMentira.honestidade_enganador (teste confere)
MARCAS_OK = ("VERIFICADO", "VERIFICADO EM OUTRA FONTE")
MARCAS_FORA = ("INFERENCIA", "DIVERGENTE", "SEM FONTE", "FONTE INVALIDA")
MARCAS = MARCAS_OK + MARCAS_FORA + ("PARCIAL", "OUTRA MIDIA")
VEREDITOS_OK = ("APTO", "APTO COM RESSALVAS")
MAX_CITACOES = 3
PALAVRAS_REPETIDAS = 6
MAX_TRACOS_ESTILO = 8               # o bloco de estilo nao incha o prompt (a ordem do arquivo decide)
MAX_FALA_ESTILO = 5


class CorpusInvalido(ValueError):
    """Arquivo fora do formato, marca desconhecida ou citacao acima do limite."""


@dataclass(frozen=True)
class Especie:
    especie: str
    jogos: tuple
    tracos: tuple            # textos que passaram no filtro
    fala: tuple
    interacoes: tuple        # (com, texto, midia)
    citacoes: tuple          # dicts {pt, original, fonte, fan_translation}
    honestidade_especie: float
    descartados: dict = field(default_factory=dict)      # marca -> quantos itens ficaram de fora


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def latino(t: str) -> bool:
    """True se toda letra do texto e do alfabeto latino (a mesma regra de saida.ler)."""
    return all(unicodedata.name(c, "").startswith("LATIN") for c in t if c.isalpha())


def _marca(item: dict, rotulo: str) -> str:
    m = item.get("marca")
    m = _sem_acento(m).strip("[]").upper() if isinstance(m, str) else m
    if m not in MARCAS:
        raise CorpusInvalido(f"{rotulo}: marca desconhecida {m!r}")
    return m


def _entra(item: dict, rotulo: str, meta: dict, vereditos: dict) -> bool:
    m = _marca(item, rotulo)
    jogo = item.get("jogo")
    if jogo is not None and vereditos.get(jogo) not in VEREDITOS_OK:
        return False
    if m in MARCAS_OK:
        return True
    if m == "PARCIAL":
        return item.get("reescrito") is True
    if m == "OUTRA MIDIA":
        return bool(meta.get("liberar_outra_midia")) and item.get("midia") == "anime"
    return False


def _frases(t: str) -> int:
    return len([p for p in re.split(r"[.!?。！？]+", t) if p.strip()])


def _especie(e: dict, meta: dict, so_latino: bool = True) -> Especie | None:
    vereditos = meta["vereditos"]
    if set(e) != {"especie", "jogos", "tracos", "fala", "interacoes", "citacoes", "honestidade_especie"}:
        raise CorpusInvalido(f"especie com chaves {sorted(e)}")
    if e["honestidade_especie"] is not None:
        raise CorpusInvalido(f"{e['especie']}: honestidade_especie e calculada pelo carregador (deixe null)")
    jogos = tuple(j for j in e["jogos"] if vereditos.get(j) in VEREDITOS_OK)
    if not jogos:
        return None
    fora: dict[str, int] = {}

    def filtra(itens, rotulo, campo="texto"):
        out = []
        for it in itens:
            if not _entra(it, f"{e['especie']}.{rotulo}", meta, vereditos):
                m = _marca(it, rotulo)
                fora[m] = fora.get(m, 0) + 1
            elif so_latino and not latino(it[campo]):
                fora["NAO LATINO"] = fora.get("NAO LATINO", 0) + 1
            else:
                out.append(it)
        return out
    tracos = filtra(e["tracos"], "tracos")
    fala = filtra(e["fala"], "fala")
    inter = filtra(e["interacoes"], "interacoes")
    cits = filtra(e["citacoes"], "citacoes", "pt")
    if len(cits) > MAX_CITACOES:
        raise CorpusInvalido(f"{e['especie']}: {len(cits)} citacoes (maximo {MAX_CITACOES})")
    for c in cits:
        if set(c) - {"pt", "original", "fonte", "fan_translation", "marca", "jogo", "midia", "nota_marca_original"} or _frases(c["pt"]) > 2:
            raise CorpusInvalido(f"{e['especie']}: citacao fora do formato ou com mais de 2 frases")
    enganador = any(t.get("enganador") is True for t in tracos)
    return Especie(e["especie"], jogos, tuple(t["texto"] for t in tracos), tuple(f["texto"] for f in fala),
                   tuple((i["com"], i["texto"], i.get("midia", "jogo")) for i in inter),
                   tuple({k: c[k] for k in ("pt", "original", "fonte", "fan_translation")} for c in cits),
                   HONESTIDADE_ENGANADOR if enganador else 1.0, fora)


def carregar(caminho: Path = ARQUIVO, so_latino: bool = True) -> tuple[dict[str, Especie], dict, str]:
    """(especie -> Especie, meta, sha256 do arquivo). so_latino=False desliga o filtro do alfabeto (so para medir)."""
    bruto = caminho.read_bytes()
    d = json.loads(bruto.decode("utf-8"))
    if set(d) != {"meta", "especies"}:
        raise CorpusInvalido(f"chaves do corpus: {sorted(d)}")
    meta = d["meta"]
    if not isinstance(meta.get("vereditos"), dict) or "exemplo" not in meta:
        raise CorpusInvalido("meta sem vereditos ou sem a marca de exemplo")
    out = {}
    for e in d["especies"]:
        esp = _especie(e, meta, so_latino)
        if esp is not None:
            if esp.especie in out:
                raise CorpusInvalido(f"especie repetida: {esp.especie}")
            out[esp.especie] = esp
    return out, meta, hashlib.sha256(bruto).hexdigest()


def bloco_estilo(esp: Especie, rival: str | None = None) -> str:
    """Bloco de ESTILO do prompt. Nao e fato: nao tem identificador e nao sustenta afirmacao."""
    linhas = [f"ESTILO DA ESPÉCIE (só tom; não é fato, não sustenta nada e não se cita)",
              f"Você é um {esp.especie}."]
    if esp.tracos:
        linhas.append("Jeito de ser: " + "; ".join(esp.tracos[:MAX_TRACOS_ESTILO]) + ".")
    if esp.fala:
        linhas.append("Jeito de falar: " + "; ".join(esp.fala[:MAX_FALA_ESTILO]) + ".")
    if esp.citacoes:
        linhas.append("Exemplos de tom (NÃO repita as palavras): " + " | ".join(f'"{c["pt"]}"' for c in esp.citacoes))
    for com, texto, midia in esp.interacoes:
        if rival is not None and com == rival:
            linhas.append(f"Com {com} em cena: {texto} (rixa da espécie, não algo que aconteceu com você).")
    return "\n".join(linhas)


def _palavras(t: str) -> list[str]:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"\w+", t)


def repete_citacao(fala: str, citacoes, n: int = PALAVRAS_REPETIDAS) -> str | None:
    """A primeira citacao de que a fala copia n ou mais palavras seguidas (sem acento e caixa), ou None."""
    pf = _palavras(fala)
    grams = {tuple(pf[i:i + n]) for i in range(len(pf) - n + 1)}
    for c in citacoes:
        pc = _palavras(c["pt"])
        if any(tuple(pc[i:i + n]) in grams for i in range(len(pc) - n + 1)):
            return c["pt"]
    return None
