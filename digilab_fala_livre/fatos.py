"""Bloco de FATOS com identificadores (TAREFA_FALA_LIVRE, secao 1).

Entrada: um dicionario com o estado do pet (montado pela web ou, na avaliacao, a partir de um log do Python).
Como a web e entrada NAO confiavel, `fatos_de_estado` so aceita chaves e valores conhecidos, com limites de
tamanho, e falha alto (FatosInvalidos) em qualquer outra coisa. Cada fato ganha um identificador curto:

    I identidade   T temperamento   C carater   E estado   M memoria   D desejo   R motivo   V vinculo
    G gatilho (o evento que disparou a fala espontanea)

Temperamento e carater entram so nos eixos extremos (|valor| >= LIMIAR_EXTREMO); o vinculo so em faixa.
"""

from __future__ import annotations

from dataclasses import dataclass

LIMIAR_EXTREMO = 0.2
ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")
EIXOS_TEMPERAMENTO = ("curiosidade", "teimosia", "sensibilidade", "rancor")      # digilab/temperamento.EIXOS
EIXOS_CARATER = ("impetuoso", "paciente", "atento", "resistente")
NECESSIDADES = ("fome", "higiene", "energia", "humor", "saude")
ESPACOS = ("curto", "longo")
TIPOS_DESEJO = ("necessidade", "vontade")
MAX_TEXTO = 80
MAX_MEMORIAS = 8
MAX_MOTIVOS = 3
MAX_FATORES = 4


class FatosInvalidos(ValueError):
    """Estado do pet fora do formato: a fala nao e gerada."""


@dataclass(frozen=True)
class Fato:
    id: str
    tipo: str          # identidade, temperamento, carater, estado, memoria, desejo, motivo, vinculo, gatilho
    texto: str

    def linha(self) -> str:
        return f"[{self.id}] {self.tipo}: {self.texto}"


def _txt(v, rotulo: str) -> str:
    if not isinstance(v, str) or not v.strip() or len(v) > MAX_TEXTO:
        raise FatosInvalidos(f"{rotulo}: texto invalido")
    if any(c in v for c in "[]{}\n\r"):
        raise FatosInvalidos(f"{rotulo}: caractere proibido")
    return v.strip()


def _num(v, rotulo: str, lo: float, hi: float) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
        raise FatosInvalidos(f"{rotulo}: numero fora de [{lo}, {hi}]")
    return float(v)


def _nivel(v: float) -> str:
    return "baixo" if v < 0.34 else "medio" if v < 0.67 else "alto"


def _minutos(v: int) -> str:
    v = int(v)
    if v < 60:
        return f"ha {v} min"
    if v < 24 * 60:
        return f"ha {v // 60} h"
    return f"ha {v // (24 * 60)} dia(s)"


def faixa_vinculo(v: float) -> str:
    return "baixo" if v < 0.4 else "medio" if v < 0.7 else "alto"


def fatos_de_estado(e: dict) -> list[Fato]:
    """Estado do pet (dict) -> lista de fatos com identificadores. Falha alto em qualquer campo invalido."""
    if not isinstance(e, dict):
        raise FatosInvalidos("estado precisa ser um objeto")
    desconhecidas = set(e) - {"identidade", "temperamento", "carater", "estado", "memorias", "desejo", "motivos",
                              "vinculo", "gatilho"}
    if desconhecidas:
        raise FatosInvalidos(f"chaves desconhecidas: {sorted(desconhecidas)}")
    fatos: list[Fato] = []

    ident = e.get("identidade")
    if not isinstance(ident, dict) or ident.get("estagio") not in ESTAGIOS:
        raise FatosInvalidos("identidade com estagio invalido")
    partes = [f"estagio {ident['estagio']}"]
    for k in ("especie", "forma", "linha"):
        if ident.get(k) is not None:
            partes.insert(len(partes) - 1, f"{k} {_txt(ident[k], k)}")
    fatos.append(Fato("I1", "identidade", ", ".join(partes)))

    for chave, eixos, letra, tipo in (("temperamento", EIXOS_TEMPERAMENTO, "T", "temperamento marcante"),
                                     ("carater", EIXOS_CARATER, "C", "carater marcante")):
        d = e.get(chave) or {}
        if not isinstance(d, dict) or set(d) - set(eixos):
            raise FatosInvalidos(f"{chave}: eixos invalidos")
        extremos = [(k, _num(v, k, -1, 1)) for k, v in d.items() if abs(_num(v, k, -1, 1)) >= LIMIAR_EXTREMO]
        for i, (k, v) in enumerate(sorted(extremos, key=lambda kv: -abs(kv[1])), 1):
            fatos.append(Fato(f"{letra}{i}", tipo, f"{k} {v:+.1f}".replace(".", ",")))

    est = e.get("estado") or {}
    if not isinstance(est, dict):
        raise FatosInvalidos("estado invalido")
    necs = [f"{k} {_nivel(_num(est[k], k, 0, 1))}" for k in NECESSIDADES if k in est]
    if necs:
        fatos.append(Fato("E1", "estado", ", ".join(necs)))
    extra = []
    if "emocao" in est:
        extra.append(f"emocao {_txt(est['emocao'], 'emocao')}")
    if "fadiga" in est:
        extra.append(f"fadiga {int(_num(est['fadiga'], 'fadiga', 0, 100))} de 100")
    if "sobrecarga" in est and _num(est["sobrecarga"], "sobrecarga", 0, 100) > 0:
        extra.append(f"sobrecarga de treino {int(est['sobrecarga'])} de 100")
    if est.get("sujo") is True:
        extra.append("sujo (coco por perto)")
    if est.get("peso") in ("magro", "gordo"):
        extra.append(f"peso fora da faixa ({est['peso']})")
    if extra:
        fatos.append(Fato("E2", "estado", ", ".join(extra)))

    mems = e.get("memorias") or []
    if not isinstance(mems, list) or len(mems) > MAX_MEMORIAS:
        raise FatosInvalidos("memorias invalidas")
    for i, m in enumerate(mems, 1):
        if not isinstance(m, dict) or m.get("espaco") not in ESPACOS:
            raise FatosInvalidos("memoria invalida")
        quando = _minutos(_num(m.get("ha_min", 0), "ha_min", 0, 10**6))
        fatos.append(Fato(f"M{i}", "memoria", f"({m['espaco']} prazo, {_txt(m['categoria'], 'categoria')}) "
                                              f"{_txt(m['evento'], 'evento')}, {quando}"))

    des = e.get("desejo")
    if des is not None:
        if not isinstance(des, dict) or des.get("tipo") not in TIPOS_DESEJO:
            raise FatosInvalidos("desejo invalido")
        fatos.append(Fato("D1", "desejo atual", f"{des['tipo']} de {_txt(des['alvo'], 'alvo')}"))

    mots = e.get("motivos") or []
    if not isinstance(mots, list) or len(mots) > MAX_MOTIVOS:
        raise FatosInvalidos("motivos invalidos")
    for i, m in enumerate(mots, 1):
        if not isinstance(m, dict):
            raise FatosInvalidos("motivo invalido")
        fat = m.get("fatores") or []
        if not isinstance(fat, list) or len(fat) > MAX_FATORES:
            raise FatosInvalidos("fatores invalidos")
        causa = ", ".join(_txt(f, "fator") for f in fat) if fat else "sem causa registrada"
        ref = f" (evento: {_txt(m['evento_ref'], 'evento_ref')})" if m.get("evento_ref") else ""
        fatos.append(Fato(f"R{i}", "motivo de decisao", f"{_txt(m['acao'], 'acao')} por causa de: {causa}{ref}"))

    if e.get("vinculo") is not None:
        fatos.append(Fato("V1", "vinculo", faixa_vinculo(_num(e["vinculo"], "vinculo", 0, 1))))

    g = e.get("gatilho")
    if g is not None:
        fatos.append(Fato("G1", "evento agora", _txt(g, "gatilho")))
    return fatos


def bloco(fatos: list[Fato]) -> str:
    return "FATOS\n" + "\n".join(f.linha() for f in fatos)


def estagio_de(fatos: list[Fato]) -> str:
    ident = next(f for f in fatos if f.id == "I1").texto
    return next(s for s in ESTAGIOS if f"estagio {s}" in ident)
