"""Expressao do motivo por estagio (Parte A). Funcao pura, so templates.

| estagio     | canal     | pode revelar                                         |
|-------------|-----------|------------------------------------------------------|
| bebe        | emote     | so humor (vida) ou reacao (combate); NUNCA a causa   |
| crianca     | icones    | acao + icone do PRIMEIRO fator                       |
| adolescente | fragmento | palavras soltas do PRIMEIRO fator                    |
| adulto      | frase     | frase com ate 2 fatores e o evento referenciado      |

A fala nunca inventa causa: so cita fatores do motivo; sem fator (ou
exploracao) o adulto diz "nao sei, so quis". Cada fator tem um MARCADOR que
aparece em todo texto que o cita e em nenhum outro lugar; a carga verifica
cobertura e unicidade (falta ou colisao levanta TabelaIncompleta). Isso e o
que torna a honestidade testavel.

Arte: placeholders em texto/ASCII, sem asset externo.
"""

from __future__ import annotations

from dataclasses import dataclass

from .combate_v2.gambits import CATALOGO
from .config import CONFIG_EXPRESSAO, ConfigExpressao
from .events import AcaoPet
from .motivo import FATORES_VIDA, Motivo, nome_base

ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")
CANAL = {"bebe": "emote", "crianca": "icones", "adolescente": "fragmento", "adulto": "frase"}
GENERICO_ADULTO = "Não sei, só quis."


class TabelaIncompleta(ValueError):
    pass


# ------------------------------------------------------------------ fatores
# bebe: sempre "" (bebe nunca cita causa). adulto do combate aceita {p0}, {p1}.

FATORES: dict[str, dict[str, str]] = {
    # vida
    "habito": {"marcador": "costume", "bebe": "", "crianca": "[:costume:]", "adolescente": "costume...",
               "adulto": "por costume"},
    "fome": {"marcador": "fome", "bebe": "", "crianca": "[:fome:]", "adolescente": "fome...",
             "adulto": "por causa da fome"},
    "higiene": {"marcador": "higiene", "bebe": "", "crianca": "[:higiene:]", "adolescente": "higiene...",
                "adulto": "por causa da higiene"},
    "energia": {"marcador": "cansaço", "bebe": "", "crianca": "[:cansaço:]", "adolescente": "cansaço...",
                "adulto": "por causa do cansaço"},
    "humor": {"marcador": "humor", "bebe": "", "crianca": "[:humor:]", "adolescente": "humor...",
              "adulto": "por causa do meu humor"},
    "saude": {"marcador": "saúde", "bebe": "", "crianca": "[:saúde:]", "adolescente": "saúde...",
              "adulto": "por causa da saúde"},
    "sujeira": {"marcador": "sujeira", "bebe": "", "crianca": "[:sujeira:]", "adolescente": "sujeira...",
                "adulto": "por causa da sujeira"},
    "dormindo": {"marcador": "sono", "bebe": "", "crianca": "[:sono:]", "adolescente": "sono...",
                 "adulto": "porque eu estava com sono"},
    "hora": {"marcador": "hora do dia", "bebe": "", "crianca": "[:hora do dia:]", "adolescente": "hora do dia...",
             "adulto": "por causa da hora do dia"},
    "tempo_sem_cuidado": {"marcador": "sem cuidado", "bebe": "", "crianca": "[:sem cuidado:]",
                          "adolescente": "sem cuidado...", "adulto": "porque fiquei muito tempo sem cuidado"},
    # combate (catalogo de gambits)
    "sempre": {"marcador": "sempre faço", "bebe": "", "crianca": "[:sempre faço:]",
               "adolescente": "sempre faço...", "adulto": "porque sempre faço isso"},
    "distancia_eh": {"marcador": "distância", "bebe": "", "crianca": "[:distância:]",
                     "adolescente": "distância...", "adulto": "porque a distância era {p0}"},
    "hp_proprio_abaixo": {"marcador": "machucado", "bebe": "", "crianca": "[:machucado:]",
                          "adolescente": "machucado...",
                          "adulto": "porque eu estava machucado (menos de {p0} da vida)"},
    "guts_proprio_abaixo": {"marcador": "exausto", "bebe": "", "crianca": "[:exausto:]",
                            "adolescente": "exausto...", "adulto": "porque eu estava exausto (guts abaixo de {p0})"},
    "guts_proprio_acima": {"marcador": "folga de guts", "bebe": "", "crianca": "[:folga de guts:]",
                           "adolescente": "folga de guts...",
                           "adulto": "porque eu tinha folga de guts ({p0} ou mais)"},
    "oponente_preparando": {"marcador": "você ia usar o golpe pesado", "bebe": "",
                            "crianca": "[:você ia usar o golpe pesado:]",
                            "adolescente": "você ia usar o golpe pesado...",
                            "adulto": "porque você ia usar o golpe pesado"},
    "oponente_hp_abaixo": {"marcador": "você estava fraco", "bebe": "", "crianca": "[:você estava fraco:]",
                           "adolescente": "você estava fraco...",
                           "adulto": "porque você estava fraco (menos de {p0} da vida)"},
    "oponente_guts_abaixo": {"marcador": "você estava sem guts", "bebe": "", "crianca": "[:você estava sem guts:]",
                             "adolescente": "você estava sem guts...",
                             "adulto": "porque você estava sem guts (abaixo de {p0})"},
    "oponente_repete": {"marcador": "você repetiu", "bebe": "", "crianca": "[:você repetiu:]",
                        "adolescente": "você repetiu...", "adulto": "porque você repetiu '{p0}' {p1} vezes"},
    "oponente_frequente": {"marcador": "você insiste", "bebe": "", "crianca": "[:você insiste:]",
                           "adolescente": "você insiste...", "adulto": "porque você insiste em '{p0}'"},
}

# ------------------------------------------------------------------ acoes

ACOES_VIDA = {
    "ocioso": ("[à toa]", "à toa", "Fiquei à toa"),
    "dormir": ("[dormir]", "dormir", "Dormi"),
    "comer": ("[comer]", "comer", "Comi"),
    "brincar": ("[brincar]", "brincar", "Brinquei"),
    "chamar_atencao": ("[chamar]", "chamar", "Chamei você"),
    "explorar": ("[explorar]", "explorar", "Explorei"),
    "emburrar": ("[emburrar]", "emburrar", "Emburrei"),
}
ACOES_COMBATE = {
    "avancar": ("[avançar]", "avançar", "Avancei"),
    "recuar": ("[recuar]", "recuar", "Recuei"),
    "golpe_rapido": ("[golpe]", "golpe", "Dei um golpe rápido"),
    "preparar_pesado": ("[preparar]", "preparar", "Preparei o pesado"),
    "disparo": ("[disparo]", "disparo", "Disparei"),
    "defender": ("[defender]", "defender", "Defendi"),
    "esquivar": ("[esquivar]", "esquivar", "Esquivei"),
    "carregar": ("[carregar]", "carregar", "Carreguei guts"),
    "pesado": ("[pesado!]", "pesado!", "Soltei o pesado que eu tinha preparado"),
}
# bebe no combate: reacao pela natureza da acao, nunca a causa
REACAO_BEBE = {
    "avancar": "(o_o)>", "recuar": "<(o_o)", "golpe_rapido": "(>_<)!", "preparar_pesado": "(ò_ó)...",
    "disparo": "(>_<)~", "defender": "(-_-)#", "esquivar": "(^o^)~", "carregar": "(ò_ó)*", "pesado": "(ò_ó)!!",
}
EMOTE_HUMOR = ("(T_T)", "(-_-)", "(^_^)")


def validar_tabelas(fatores_obrigatorios=None) -> None:
    obrig = set(fatores_obrigatorios if fatores_obrigatorios is not None
                else set(FATORES_VIDA) | set(CATALOGO) | set(_fatores_extra()))
    faltando = sorted(obrig - set(FATORES))
    if faltando:
        raise TabelaIncompleta(f"fatores sem entrada na tabela: {faltando}")
    for nome, e in FATORES.items():
        for chave in ("marcador",) + ESTAGIOS:
            if chave not in e:
                raise TabelaIncompleta(f"fator {nome!r} sem entrada para {chave!r}")
        if e["bebe"] != "":
            raise TabelaIncompleta(f"fator {nome!r}: bebe nao pode citar causa")
        for est in ("crianca", "adolescente", "adulto"):
            if e["marcador"] not in e[est]:
                raise TabelaIncompleta(f"fator {nome!r}/{est}: texto sem o marcador {e['marcador']!r}")
    marcadores = {n: e["marcador"] for n, e in FATORES.items()}
    for n1, m1 in marcadores.items():
        for n2, e2 in FATORES.items():
            if n1 != n2 and any(m1 in e2[est] for est in ("crianca", "adolescente", "adulto")):
                raise TabelaIncompleta(f"marcador de {n1!r} aparece no texto de {n2!r}")
    faltam_vida = sorted(set(a.value for a in AcaoPet) - set(ACOES_VIDA))
    from .combate_v2.regras import Acao

    faltam_comb = sorted(set(a.value for a in Acao) - set(ACOES_COMBATE))
    faltam_reacao = sorted(set(a.value for a in Acao) - set(REACAO_BEBE))
    if faltam_vida or faltam_comb or faltam_reacao:
        raise TabelaIncompleta(f"acoes sem texto: vida {faltam_vida}, combate {faltam_comb}, reacao {faltam_reacao}")
    fixos = [t for trio in list(ACOES_VIDA.values()) + list(ACOES_COMBATE.values()) for t in trio]
    fixos += [GENERICO_ADULTO] + list(REACAO_BEBE.values()) + list(EMOTE_HUMOR)
    for n, m in marcadores.items():
        for t in fixos:
            if m in t:
                raise TabelaIncompleta(f"marcador de {n!r} ({m!r}) aparece em texto fixo {t!r}")


def _fatores_extra() -> tuple[str, ...]:
    """Fatores alem da vida e do catalogo (memoria, Parte B), se o modulo existir."""
    try:
        from .memoria import FATORES_MEMORIA
    except ImportError:
        return ()
    return FATORES_MEMORIA


@dataclass(frozen=True)
class Expressao:
    canal: str
    conteudo: str
    motivo_ref: tuple  # (origem, tick) ou (origem, turno)


def estagio_por_idade(dias: float, cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> str:
    """PROVISORIO: idade em dias simulados -> estagio. Vira derivado da evolucao quando ela existir."""
    if dias < 0:
        raise ValueError(f"idade negativa: {dias}")
    if dias < cfg.dias_fim_bebe:
        return "bebe"
    if dias < cfg.dias_fim_crianca:
        return "crianca"
    if dias < cfg.dias_fim_adolescente:
        return "adolescente"
    return "adulto"


def _params(fator: str) -> list[str]:
    if "(" not in fator:
        return []
    corpo = fator[fator.index("(") + 1:-1]
    saida = []
    for p in corpo.split(","):
        try:
            f = float(p)
            saida.append(f"{f:.0%}" if 0 < f < 1 else p)
        except ValueError:
            saida.append(p.replace("_", " "))
    return saida


def _texto_fator(fator: str, estagio: str) -> str:
    base = nome_base(fator)
    if base not in FATORES:
        raise TabelaIncompleta(f"fator sem entrada: {base!r}")
    t = FATORES[base][estagio]
    ps = _params(fator)
    return t.format(**{f"p{i}": v for i, v in enumerate(ps)}) if "{" in t else t


def _refs(motivo: Motivo) -> str:
    if not motivo.evento_ref:
        return ""
    if motivo.origem == "vida":
        return " (lembro do evento #" + ", #".join(str(r) for r in motivo.evento_ref) + ")"
    return " (turno " + ", ".join(str(r) for r in motivo.evento_ref) + ")"


def expressar(motivo: Motivo, estagio: str, humor: float | None = None,
              cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> Expressao:
    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    ref = (motivo.origem, motivo.tick if motivo.origem == "vida" else motivo.turno)
    acoes = ACOES_VIDA if motivo.origem == "vida" else ACOES_COMBATE
    if motivo.acao not in acoes:
        raise TabelaIncompleta(f"acao sem texto: {motivo.acao!r}")
    icone, palavra, frase = acoes[motivo.acao]
    fatores = () if motivo.exploracao else motivo.fatores

    if estagio == "bebe":
        if motivo.origem == "vida":
            if humor is None:
                raise ValueError("bebe na vida precisa do humor")
            i = 2 if humor >= cfg.humor_alegre else 1 if humor >= cfg.humor_neutro else 0
            return Expressao("emote", EMOTE_HUMOR[i], ref)
        return Expressao("emote", REACAO_BEBE[motivo.acao], ref)
    if estagio == "crianca":
        partes = [icone] + ([_texto_fator(fatores[0], "crianca")] if fatores else [])
        return Expressao("icones", " ".join(partes), ref)
    if estagio == "adolescente":
        return Expressao("fragmento", f"{palavra}... " + (_texto_fator(fatores[0], "adolescente") if fatores else ""), ref)
    if not fatores:
        return Expressao("frase", f"{frase}. {GENERICO_ADULTO}", ref)
    causas = " e ".join(_texto_fator(f, "adulto") for f in fatores[:2])
    return Expressao("frase", f"{frase} {causas}{_refs(motivo)}.", ref)


def marcadores_citados(conteudo: str) -> set[str]:
    """Fatores (nome base) cujo marcador aparece no conteudo."""
    return {n for n, e in FATORES.items() if e["marcador"] in conteudo}


validar_tabelas()
