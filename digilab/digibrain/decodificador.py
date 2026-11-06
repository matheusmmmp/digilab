"""O decodificador de conceitos `dec-v1` (docs/research/ESPEC_DECODIFICADOR_FALA.md, DC1): do `motivo` de uma decisao do modular aos 12 conceitos
nomeados da fala, cada um com valor e confianca em [0, S], mais a intencao (regra I-a, DC-B).

- **Funcao pura:** so le o `motivo` (inteiros na escala S, sem rng, sem float); nada muda o cerebro nem a vida. O espelho em TS e
  `web/app/motor/digibrain/decodificador.ts`, conferido bit a bit contra `web/app/test/gabaritos/decodificador_python.json`.
- **Sem o `consequencia` do motivo:** ele so aparece na decisao seguinte (o motivo da vida inteira o tem, o do painel na hora da decisao nao), e o
  decodificador tem de dar a mesma saida nos dois. O `estadoInterno()` tambem nao e preciso: tudo o que os conceitos pedem esta no `motivo`.
- **Falha alto:** receptor, comportamento ou sonda desconhecidos levantam erro (sem valor padrao).
- **Pesos e limiares:** `ConfigDecodificador` (`digilab/config.py`), PROPOSTOS, SEM FONTE.
- **Intencao (I-a):** `lembranca` quando a sonda `lembranca_decidiu` e verdadeira; senao o conceito de maior valor (empate: a ordem do catalogo),
  sem contar a `lembranca`.
"""
from __future__ import annotations

from ..config import CONFIG_DECODIFICADOR, CONFIG_DIGIBRAIN_INATOS, ConfigDecodificador
from ..policies.lobos import div_arred
from ._comum import clamp, mul

VERSAO = "dec-v1"
CATALOGO = ("fome", "sono", "bem_estar", "mal_estar", "agitacao", "aversao", "frustracao", "determinacao", "indecisao", "lembranca",
            "solidao", "curiosidade")
RECEPTORES = ("fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto")
COMPORTAMENTOS = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")
SONDAS_DECIDIU = ("afeto_decidiu", "aprendido_decidiu", "habito_decidiu", "incentivo_decidiu", "lembranca_decidiu", "memoria_decidiu",
                  "persistencia_decidiu")


def _media(pares: list[tuple[int, int]]) -> int:
    """a media ponderada dos sinais: div_arred(soma(peso x sinal), soma(peso)); sem peso nenhum, 0"""
    soma = sum(p for p, _ in pares)
    return 0 if soma == 0 else div_arred(sum(p * s for p, s in pares), soma)


def _fracao(m: dict, comportamentos: tuple[str, ...], S: int) -> int:
    """a fracao dos pesos w das opcoes dos comportamentos, em [0, S]; sem peso nenhum, 0"""
    total = sum(u["w"] for u in m["unidades"])
    if total <= 0:
        return 0
    return div_arred(sum(u["w"] for u in m["unidades"] if u["chave"][0] in comportamentos) * S, total)


def _escolhida(m: dict) -> dict:
    esc = [u for u in m["unidades"] if list(u["chave"]) == list(m["escolha"])]
    if len(esc) != 1:
        raise ValueError(f"o motivo nao tem a unidade escolhida: {m['escolha']!r}")
    return esc[0]


def _confianca_escolhida(m: dict, S: int) -> int:
    """a fracao da escolhida; no reflexo (sem sorteio) a escolha e certa: S"""
    esc = _escolhida(m)
    if m["reflexo"]:
        return S
    total = sum(u["w"] for u in m["unidades"])
    return 0 if total <= 0 else div_arred(esc["w"] * S, total)


def _validar(m: dict) -> None:
    """falha alto em receptor, comportamento ou sonda desconhecidos"""
    for r in m["afeto"]["urgencias"]:
        if r not in RECEPTORES:
            raise ValueError(f"receptor desconhecido no motivo: {r!r}")
    for u in m["unidades"]:
        if u["chave"][0] not in COMPORTAMENTOS:
            raise ValueError(f"comportamento desconhecido no motivo: {u['chave'][0]!r}")
    for s in m["sondas"]:
        if s.endswith("_decidiu") and s not in SONDAS_DECIDIU:
            raise ValueError(f"sonda desconhecida no motivo: {s!r}")
    for s in SONDAS_DECIDIU:
        if s not in m["sondas"]:
            raise ValueError(f"o motivo nao tem a sonda {s!r}")


def decodificar(motivo: dict, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR, S: int = CONFIG_DIGIBRAIN_INATOS.escala) -> dict:
    """{versao, k, intencao, conceitos: [{nome, valor, confianca, alvo?}]} (a espec, secao 2), os 12 conceitos na ordem do catalogo"""
    m = motivo
    _validar(m)
    urg = m["afeto"]["urgencias"]
    est = m["estado"]
    escolha = m["escolha"]
    esc_conf = _confianca_escolhida(m, S)
    sondas = m["sondas"]
    I = est["I"]
    cs: dict[str, dict] = {}

    def conceito(nome: str, valor: int, confianca: int, alvo: str | None = None) -> None:
        d = {"nome": nome, "valor": clamp(valor, 0, S), "confianca": clamp(confianca, 0, S)}
        if alvo is not None:
            d["alvo"] = alvo
        cs[nome] = d

    # fome
    alvo_comida = escolha[1] if escolha[0] == "comer" and escolha[1] is not None else None
    conceito("fome", _media([(cfg.p_fome_urgencia, urg["fome"]), (cfg.p_fome_fracao, _fracao(m, ("comer",), S)),
                             (cfg.p_fome_intencao, S if I is not None and I[0] == "comer" else 0),
                             (cfg.p_fome_pista, S if m["memoria"]["pista"] else 0)]), esc_conf, alvo_comida)
    # sono
    conceito("sono", _media([(cfg.p_sono_urgencia, urg["energia"]), (cfg.p_sono_fracao, _fracao(m, ("dormir",), S)),
                             (cfg.p_sono_reflexo, S if m["reflexo"] else 0),
                             (cfg.p_sono_noite, S if m["contexto"]["noite"] else 0)]), esc_conf)
    # bem-estar e mal-estar: o sinal e o modulo de V
    V = m["afeto"]["V"]
    conceito("bem_estar", cfg.ganho_v * max(0, V), min(S, abs(V)))
    conceito("mal_estar", cfg.ganho_v * max(0, -V), min(S, abs(V)))
    # agitacao
    E = m["afeto"]["E"]
    conceito("agitacao", _media([(cfg.p_agitacao_e, E), (cfg.p_agitacao_urgencia, max(urg["dor"], urg["susto"], urg["estresse"]))]), E)
    # aversao aprendida (a lembranca com sigma < 0)
    lem = m["lembranca"]
    ep = None if lem["recuperado"] is None else f"ep{lem['recuperado']}"
    if lem["recuperado"] is not None and lem["sigma"] < 0:
        conceito("aversao", mul(lem["sim"], clamp(cfg.ganho_sigma * -lem["sigma"], 0, S), S), lem["sim"], ep)
    else:
        conceito("aversao", 0, 0)
    # frustracao
    frustrado = any(f["motivo"] in cfg.fins_frustrantes for f in m["fins"])
    conceito("frustracao", _media([(cfg.p_frustracao_f, est["F"]), (cfg.p_frustracao_fim, S if frustrado else 0),
                                   (cfg.p_frustracao_n_sp, min(S, div_arred(est["n_sp"] * S, cfg.n_sp_teto)))]), est["F"])
    # determinacao: a intencao em curso, o compromisso C e a persistencia; a sonda da persistencia que decidiu leva ao piso
    if I is None:
        det = 0
    else:
        det = _media([(cfg.p_determinacao_c, est["C"]),
                      (cfg.p_determinacao_persistencia, clamp(_escolhida(m)["termos"]["persistencia"], 0, S))])
    if sondas["persistencia_decidiu"]:
        det = max(det, cfg.piso_sonda)
    conceito("determinacao", det, est["C"] if I is not None else 0)
    # indecisao: a margem entre os dois maiores pesos e as sondas que decidiram
    ws = sorted((u["w"] for u in m["unidades"] if u["w"] > 0), reverse=True)
    margem = S if m["reflexo"] or len(ws) < 2 else div_arred((ws[0] - ws[1]) * S, sum(ws))
    n_dec = sum(1 for s in SONDAS_DECIDIU if sondas[s])
    conceito("indecisao", _media([(cfg.p_indecisao_margem, S - margem), (cfg.p_indecisao_sondas, div_arred(n_dec * S, len(SONDAS_DECIDIU)))]),
             S - margem)
    # lembranca ativa: a semelhanca; a sonda da lembranca que decidiu leva ao piso
    val_lem = 0 if lem["recuperado"] is None else lem["sim"]
    if sondas["lembranca_decidiu"]:
        val_lem = max(val_lem, cfg.piso_sonda)
    conceito("lembranca", val_lem, 0 if lem["recuperado"] is None else lem["sim"], ep)
    # solidao
    conceito("solidao", _media([(cfg.p_solidao_urgencia, urg["solidao"]), (cfg.p_solidao_fracao, _fracao(m, ("chamar_atencao", "emburrar"), S))]),
             urg["solidao"])
    # curiosidade
    gx = m["afeto"]["g_exp"]
    conceito("curiosidade", _media([(cfg.p_curiosidade_urgencia, urg["curiosidade"]), (cfg.p_curiosidade_tedio, urg["tedio"]),
                                    (cfg.p_curiosidade_g_exp, gx), (cfg.p_curiosidade_fracao, _fracao(m, ("explorar",), S))]), gx)
    # a intencao (I-a)
    if sondas["lembranca_decidiu"]:
        intencao = "lembranca"
    else:
        intencao = max((n for n in CATALOGO if n != "lembranca"), key=lambda n: (cs[n]["valor"], -CATALOGO.index(n)))
    return {"versao": VERSAO, "k": m["k"], "intencao": intencao, "conceitos": [cs[n] for n in CATALOGO]}
