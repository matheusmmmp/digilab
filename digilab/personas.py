"""Personas de dono (educacao-v1, sistema E; docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, secao 6).

Uma persona e um JSON com os parametros de um dono sintetico. Pode ser escrita a mao ou gerada por LLM
(tools/gerar_personas.py, FORA do pacote). Aqui so o esquema, a validacao (falha alto em campo
desconhecido, faltando ou fora da faixa) e a leitura de um lote com o sha256 do arquivo. O dono que joga
a persona (donos_educacao.DonoComEducacao com persona) e deterministico: a LLM nunca e chamada de novo.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

# campo -> (tipo, faixa ou valores, descricao para o gerador)
ESQUEMA_PERSONA = {
    "nome": (str, r"^[a-z0-9_-]{1,40}$", "identificador curto, minusculas, sem espaco"),
    "descricao": (str, 300, "uma ou duas frases sobre a rotina e o jeito dessa pessoa com o pet"),
    "horarios": (list, None, "faixas de hora em que a pessoa olha o pet: lista de [inicio, fim], horas inteiras 0-24; "
                             "inicio maior que fim = atravessa a meia-noite (ex.: [22, 2])"),
    "prob_atender_janela": (float, (0.0, 1.0), "chance de responder quando o pet chama ou avisa, estando presente"),
    "prob_ceder_petisco": (float, (0.0, 1.0), "quando o chamado parece manha (necessidade em dia): chance de dar petisco em vez de bronca"),
    "prob_feedback_coerente": (float, (0.0, 1.0), "chance de o elogio ou a bronca combinar com o que o pet fez"),
    "limiar_cuidado": (float, (0.1, 0.9), "abaixo de quanto (0-1) de fome, higiene ou humor a pessoa cuida"),
    "perfil_treino": (str, ("atencioso", "exigente"), "quantas sessoes de treino por dia: o alvo (atencioso) ou o teto (exigente)"),
}


class PersonaInvalida(ValueError):
    pass


@dataclass(frozen=True)
class Persona:
    nome: str
    descricao: str
    horarios: tuple
    prob_atender_janela: float
    prob_ceder_petisco: float
    prob_feedback_coerente: float
    limiar_cuidado: float
    perfil_treino: str

    def presente(self, hora: int) -> bool:
        return any((ini <= hora < fim) if ini < fim else (hora >= ini or hora < fim) for ini, fim in self.horarios)

    def para_dict(self) -> dict:
        d = {k: getattr(self, k) for k in ESQUEMA_PERSONA}
        d["horarios"] = [list(h) for h in self.horarios]
        return d


def validar_persona(d: dict) -> Persona:
    if not isinstance(d, dict):
        raise PersonaInvalida(f"persona nao e objeto: {type(d).__name__}")
    faltam, sobram = set(ESQUEMA_PERSONA) - set(d), set(d) - set(ESQUEMA_PERSONA)
    if faltam or sobram:
        raise PersonaInvalida(f"campos faltando {sorted(faltam)}, desconhecidos {sorted(sobram)}")
    for k, (tipo, regra, _) in ESQUEMA_PERSONA.items():
        v = d[k]
        if tipo is float:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not regra[0] <= v <= regra[1]:
                raise PersonaInvalida(f"{k}: {v!r} fora de {regra}")
        elif not isinstance(v, tipo):
            raise PersonaInvalida(f"{k}: esperava {tipo.__name__}, veio {type(v).__name__}")
        elif k == "nome" and not re.match(regra, v):
            raise PersonaInvalida(f"nome invalido: {v!r}")
        elif k == "descricao" and not 0 < len(v) <= regra:
            raise PersonaInvalida("descricao vazia ou longa demais")
        elif k == "perfil_treino" and v not in regra:
            raise PersonaInvalida(f"perfil_treino: {v!r} nao e {regra}")
    hs = d["horarios"]
    if not hs:
        raise PersonaInvalida("horarios vazio")
    for h in hs:
        if (not isinstance(h, list) or len(h) != 2 or not all(isinstance(x, int) and not isinstance(x, bool) for x in h)
                or not (0 <= h[0] <= 24 and 0 <= h[1] <= 24) or h[0] == h[1]):
            raise PersonaInvalida(f"faixa de horario invalida: {h!r}")
    return Persona(d["nome"], d["descricao"], tuple(tuple(h) for h in hs),
                   *(float(d[k]) for k in ("prob_atender_janela", "prob_ceder_petisco", "prob_feedback_coerente",
                                           "limiar_cuidado")), d["perfil_treino"])


def carregar_lote(caminho: Path) -> tuple[list[Persona], str]:
    """(personas, sha256 do arquivo com finais de linha normalizados). Nomes repetidos levantam erro."""
    bruto = Path(caminho).read_bytes().replace(b"\r\n", b"\n")
    d = json.loads(bruto.decode("utf-8"))
    if set(d) != {"meta", "personas"}:
        raise PersonaInvalida(f"lote precisa de 'meta' e 'personas', tem {sorted(d)}")
    ps = [validar_persona(p) for p in d["personas"]]
    nomes = [p.nome for p in ps]
    if len(set(nomes)) != len(nomes):
        raise PersonaInvalida("nomes de persona repetidos no lote")
    return ps, hashlib.sha256(bruto).hexdigest()
