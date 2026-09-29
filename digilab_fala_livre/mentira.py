"""Moldes de distorcao da mentira (DESIGN_VOZ_PROPRIA, secao 9).

A mentira e decidida pelo MOTOR (digilab/educacao.py, ConfigMentira): ele diz se a fala mente e sobre qual tema
(estado ou historia). Aqui so se escolhe o fato verdadeiro e se aplica um molde fixo. A LLM recebe a versao falsa
como fato [F1] e a instrucao de afirma-la; o registro guarda a verdade ao lado (Fato.meta). Nada e sorteado:
mesmo estado e mesmos fatos dao a mesma mentira.

  estado    a necessidade mais baixa (abaixo de LIMIAR) e negada ("estou cheio, nem quero comer"); se todas estao
            em dia, o pet finge uma necessidade ("estou morrendo de fome"), como o chamado falso
  historia  o primeiro fato (na ordem da selecao) de uma regra que admite distorcao; sem nenhum, cai no estado
"""

from __future__ import annotations

from digilab.historia import CUIDADO_DONO, PET_EU, PET_INF, TEXTO_PERIODO, _rival_padrao

LIMIAR = 0.35             # = ConfigEducacao.limiar_necessidade_real (necessidade abaixo disto e real)
NEGA = {"fome": "estou cheio, nem quero comer", "higiene": "estou limpinho", "energia": "estou cheio de energia",
        "humor": "estou muito feliz", "saude": "estou ótimo, nada dói"}
FINGE = {"fome": "estou morrendo de fome", "humor": "estou muito triste", "higiene": "estou todo sujo",
         "energia": "estou morto de cansaço", "saude": "estou doente"}
_ORDEM = ("fome", "humor", "higiene", "energia", "saude")


def _nivel(v: float) -> str:
    return "baixo" if v < 0.34 else "medio" if v < 0.67 else "alto"


def _estado(est: dict) -> tuple[str, str, str]:
    necs = {k: float(est[k]) for k in _ORDEM if k in est}
    if not necs:
        return "estado não informado", FINGE["fome"], "estado:finge:fome"
    k = min(_ORDEM, key=lambda n: (necs.get(n, 2.0), _ORDEM.index(n)))
    if necs[k] < LIMIAR:
        return f"{k} {_nivel(necs[k])}", NEGA[k], f"estado:nega:{k}"
    k = next(n for n in _ORDEM if n in necs)
    return f"{k} {_nivel(necs[k])}", FINGE[k], f"estado:finge:{k}"


def _historia(regra: str, d: dict) -> str | None:
    """molde por regra (None: a regra nao admite distorcao)"""
    if regra == "demora":
        return "você nunca me atende" if d.get("rapido") else "você sempre me atende na hora"
    if regra == "periodo_dono" and d.get("periodo") in TEXTO_PERIODO:
        return f"você nunca aparece {TEXTO_PERIODO[d['periodo']]}"
    if regra == "cuidado_dono" and d.get("acao") in CUIDADO_DONO:
        return f"você nunca quer {CUIDADO_DONO[d['acao']]}"
    if regra == "cede_manha":
        return "você nunca cede quando faço manha"
    if regra == "gosto" and d.get("acao") in PET_INF:
        return f"odeio {PET_INF[d['acao']]}"
    if regra == "desgosto" and d.get("acao") in PET_INF:
        return f"adoro {PET_INF[d['acao']]}"
    if regra == "treino_favorito" and d.get("exercicio"):
        return f"odeio treinar {str(d['exercicio']).replace('_', ' ')}"
    if regra in ("revanche", "venceu_depois", "primeira_derrota") and d.get("rival"):
        return f"eu venci {_rival_padrao(str(d['rival']))} fácil"
    if regra == "primeira_vitoria":
        return "nunca venci uma luta"
    if regra == "lesao":
        return "me machuquei e ninguém me tratou" if d.get("tratada") else "nunca me machuquei"
    if regra == "ausencia":
        return "você nunca some"
    if regra == "sombria":
        return "nunca virei sombrio"
    if regra == "sequencia" and d.get("a") in PET_INF and d.get("b") in PET_EU:
        return f"nunca {PET_EU[d['b']]} depois de {PET_INF[d['a']]}"
    if regra == "periodo" and d.get("acao") in PET_EU and d.get("periodo") in TEXTO_PERIODO:
        return f"{TEXTO_PERIODO[d['periodo']]} eu quase não {PET_EU[d['acao']]}"
    return None                         # evolucao, cruzamento: nada a distorcer


def distorcer(tema: str, est: dict, fatos: list) -> tuple[str, str, str]:
    """(texto verdadeiro, texto falso, molde). `fatos`: os Fato ja montados (a historia traz regra e dados)."""
    if tema not in ("estado", "historia"):
        raise ValueError(f"tema de mentira desconhecido: {tema!r}")
    if tema == "historia":
        for f in fatos:
            meta = dict(f.meta)
            if "regra" not in meta:
                continue
            falsa = _historia(meta["regra"], meta.get("dados") or {})
            if falsa is not None:
                return f.texto, falsa, f"historia:{meta['regra']}"
    return _estado(est)
