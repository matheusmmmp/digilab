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
- **O `dec-v4`** (a fala do assistir, docs/futuro/fala_do_assistir.md, FA-2 a FA-4, DECIDIDAS pelo Matheus em 2026-11-12): o `olhar` no
  catalogo de comportamentos e o bloco `assistir` (`gostei`, `susto`, `chato`, `o_que_e`), lido do campo `olhar` do motivo (com o enjoo) e da
  decisao anterior; os limiares na `ConfigFalaAssistir`, calibrados nas vidas gravadas da GV3 e da GV3b
  (`artifacts_v3_gosto_visual/fala_limiares/`). O espelho e o `decodificarV4` do TS, conferido contra
  `web/app/test/gabaritos/decodificador_v4_python.json.gz`. O dec-v1 e o dec-v2 nao mudam.
"""
from __future__ import annotations

from ..config import CONFIG_DECODIFICADOR, CONFIG_DIGIBRAIN_INATOS, CONFIG_FALA_ASSISTIR, ConfigDecodificador, ConfigFalaAssistir
from ..policies.lobos import div_arred
from ._comum import clamp, mul

VERSAO = "dec-v1"
VERSAO_V2 = "dec-v2"
CATALOGO = ("fome", "sono", "bem_estar", "mal_estar", "agitacao", "aversao", "frustracao", "determinacao", "indecisao", "lembranca",
            "solidao", "curiosidade")
RECEPTORES = ("fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto")
COMPORTAMENTOS = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")
# dec-v2 (DC2b): o conceito `lembranca` ganha `episodio` = {acao, classe, desfecho}, de catalogo fechado, decodificado do episodio recuperado
CLASSES_EPISODIO = ("racao", "a", "b", "c", "podre", "nao_havia", "bola", "sem_alvo")     # = mem.CLASSES_AUTOBIO
DESFECHOS = ("bom", "ruim", "neutro")
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


def _validar(m: dict, comportamentos: tuple[str, ...] = COMPORTAMENTOS) -> None:
    """falha alto em receptor, comportamento ou sonda desconhecidos (`comportamentos`: o catalogo da versao; o dec-v4 soma o `olhar`)"""
    for r in m["afeto"]["urgencias"]:
        if r not in RECEPTORES:
            raise ValueError(f"receptor desconhecido no motivo: {r!r}")
    for u in m["unidades"]:
        if u["chave"][0] not in comportamentos:
            raise ValueError(f"comportamento desconhecido no motivo: {u['chave'][0]!r}")
    for s in m["sondas"]:
        if s.endswith("_decidiu") and s not in SONDAS_DECIDIU:
            raise ValueError(f"sonda desconhecida no motivo: {s!r}")
    for s in SONDAS_DECIDIU:
        if s not in m["sondas"]:
            raise ValueError(f"o motivo nao tem a sonda {s!r}")


def decodificar(motivo: dict, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR, S: int = CONFIG_DIGIBRAIN_INATOS.escala) -> dict:
    """{versao, k, intencao, conceitos: [{nome, valor, confianca, alvo?}]} (a espec, secao 2), os 12 conceitos na ordem do catalogo"""
    return _decodificar(motivo, cfg, S, COMPORTAMENTOS)


def _decodificar(motivo: dict, cfg: ConfigDecodificador, S: int, comportamentos: tuple[str, ...]) -> dict:
    """o dec-v1 sobre o catalogo de comportamentos dado (o do dec-v1, ou o do dec-v4 com o `olhar`); as contas nao mudam"""
    m = motivo
    _validar(m, comportamentos)
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


def desfecho_do_episodio(ep: dict, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR) -> str:
    """PROPOSTA (DC2b, SEM FONTE): o desfecho e o sinal da significancia `sigma` do episodio (o r_n da consequencia, ou o do corpo
    que a visita vazia nao alcancou), com margem `limiar_desfecho`: bom se sigma >= limiar, ruim se sigma <= -limiar, senao neutro"""
    if ep["sigma"] >= cfg.limiar_desfecho:
        return "bom"
    return "ruim" if ep["sigma"] <= -cfg.limiar_desfecho else "neutro"


def episodio_dec(ep: dict, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR) -> dict | None:
    """{acao, classe, desfecho} do episodio autobiografico (`mem.py`), de catalogo fechado, ou None para o episodio de luta (a acao dele
    nao e um dos 7 comportamentos: a lembranca de luta fica fora desta versao, DC-C). Texto livre do episodio nao entra. Falha alto fora do catalogo"""
    if ep["origem"] == "luta":
        return None
    acao = ep["acao"][0]
    if acao not in COMPORTAMENTOS:
        raise ValueError(f"episodio com comportamento desconhecido: {acao!r}")
    if ep["classe"] not in CLASSES_EPISODIO:
        raise ValueError(f"episodio com classe desconhecida: {ep['classe']!r}")
    return {"acao": acao, "classe": ep["classe"], "desfecho": desfecho_do_episodio(ep, cfg)}


def decodificar_v2(motivo: dict, episodio: dict | None, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR,
                   S: int = CONFIG_DIGIBRAIN_INATOS.escala) -> dict:
    """O `dec-v2`: o `dec-v1` com a versao trocada e, no conceito `lembranca`, o campo `episodio` {acao, classe, desfecho}. `episodio` e o
    episodio autobiografico recuperado na decisao (o de id `motivo["lembranca"]["recuperado"]`), ou None (sem lembranca, episodio que saiu da
    memoria ou episodio de luta): sem ele o conceito fica como no v1. Os outros conceitos e a intencao nao mudam (o decodificador so le)"""
    r = decodificar(motivo, cfg, S)
    r["versao"] = VERSAO_V2
    if episodio is None:
        return r
    rec = motivo["lembranca"]["recuperado"]
    if rec is None or episodio.get("id") != rec:
        raise ValueError(f"o episodio {episodio.get('id')!r} nao e o recuperado na decisao ({rec!r})")
    dec = episodio_dec(episodio, cfg)
    if dec is not None:
        for c in r["conceitos"]:
            if c["nome"] == "lembranca":
                c["episodio"] = dec
    return r


# ====================================================================== o dec-v4: a fala do assistir (FA-2 a FA-4)
VERSAO_V4 = "dec-v4"                                   # nome PROPOSTO (FA-2)
COMPORTAMENTOS_V4 = COMPORTAMENTOS + ("olhar",)        # = config.COMPORTAMENTO_OLHAR: o olhar entra no catalogo (FA-2)
# os conceitos do assistir da primeira versao (FA-3: sem o `de_novo`), na ordem do catalogo (o desempate da intencao)
CATALOGO_ASSISTIR = ("gostei", "susto", "chato", "o_que_e")
CAMPOS_OLHAR_V4 = ("telas", "olhava", "agrado", "agrado_inato", "gosto", "enjoo", "agrado_efetivo", "olha")


def _escala(x: int, limiar: int, h: int, S: int) -> int:
    """o sinal x em [0, S] levado a [0, S] por duas retas: 0 -> 0, `limiar` -> h, S -> S (o sinal no limiar vale o limiar de ativo)"""
    x = clamp(x, 0, S)
    return div_arred(x * h, limiar) if x < limiar else h + div_arred((x - limiar) * (S - h), S - limiar)


def _confianca_assistir(valor: int, h: int, S: int) -> int:
    """a distancia do valor ao limiar de ativo h, em [0, S]: 0 no limiar e S nas pontas (o ativo de pouco e o conceito em duvida)"""
    return div_arred((valor - h) * S, S - h) if valor >= h else div_arred((h - valor) * S, h)


def _validar_olhar(o: dict) -> None:
    """o campo `olhar` do motivo com o enjoo (o cerebro do jogo v35+ e da GV3b, D-GV-ENJOO-CER); falha alto sem ele ou com campo a menos"""
    falta = [c for c in CAMPOS_OLHAR_V4 if c not in o]
    if falta:
        raise ValueError(f"o dec-v4 pede o olhar com o enjoo no motivo; faltam {falta}")
    if o["olhava"] is not None and any(o[c] is None for c in ("agrado", "agrado_efetivo", "enjoo")):
        raise ValueError("o dec-v4: o pet olhava e o motivo nao tem o agrado, o agrado efetivo ou o enjoo")


def conceitos_assistir(motivo: dict, anterior: dict | None, cfg: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR,
                       S: int = CONFIG_DIGIBRAIN_INATOS.escala) -> dict | None:
    """os conceitos do assistir da decisao (FA-2 a FA-4), ou None se o pet nao olhava uma TV no intervalo que acabou (`olhar.olhava`; "so
    enquanto o pet olha", FA-5). PROPOSTO, SEM FONTE nos limiares (ConfigFalaAssistir, calibrados nas vidas gravadas da GV3 e da GV3b):
    - `gostei`: o agrado efetivo do que o pet olhava (o agrado com o enjoo, o que o cerebro usa no termo `gosto`), alto;
    - `susto`: a subida da urgencia do susto desde a decisao anterior (o salto de volume do corpo, GV-17; FA-4: so o volume), zerada quando
      houve tapa nos gestos do intervalo (o tapa e o outro emissor do susto no corpo; o susto do assistir e so o da tela);
    - `chato`: o enjoo da TV (a habituacao do cerebro, D-GV-ENJOO-CER) e o tedio, os dois altos (o menor dos dois valores);
    - `o_que_e`: o agrado sem o enjoo baixo (o nivel longe do alvo aprendido: longe do esperado) e o enjoo baixo (o pet ainda nao cansou
      daquela TV: a novidade que o motivo mostra; o `novidade_tela` do corpo nao esta no motivo); o menor dos dois.
    A intencao do assistir: o `susto`, quando ativo (FA-2); senao o ativo de maior valor (empate: a ordem do catalogo); nenhum ativo: None.
    `anterior` e o motivo da decisao k - 1 (None so na primeira decisao)."""
    o = motivo["olhar"]
    _validar_olhar(o)
    if anterior is None:
        if motivo["k"] != 0:
            raise ValueError(f"o dec-v4 pede o motivo anterior a decisao {motivo['k']}")
        susto_antes = 0
    else:
        if anterior["k"] != motivo["k"] - 1:
            raise ValueError(f"o motivo anterior e o da decisao {anterior['k']}, nao o da {motivo['k'] - 1}")
        susto_antes = anterior["afeto"]["urgencias"]["susto"]
    if o["olhava"] is None:
        return None
    h = cfg.limiar_ativo
    urg = motivo["afeto"]["urgencias"]
    tapa = any(g[0] == "tapa" for g in motivo["gestos"])
    subida = 0 if tapa else max(0, urg["susto"] - susto_antes)
    ae, enjoo = o["agrado_efetivo"], o["enjoo"]
    valores = {
        "gostei": _escala(ae, cfg.gostei_agrado, h, S),
        "susto": _escala(subida, cfg.susto_subida, h, S),
        "chato": min(_escala(enjoo, cfg.chato_enjoo, h, S), _escala(urg["tedio"], cfg.chato_tedio, h, S)),
        "o_que_e": min(_escala(S - o["agrado"], S - cfg.o_que_e_agrado, h, S), _escala(S - enjoo, S - cfg.o_que_e_enjoo, h, S)),
    }
    cs = [{"nome": n, "valor": valores[n], "confianca": _confianca_assistir(valores[n], h, S)} for n in CATALOGO_ASSISTIR]
    ativos = [c for c in cs if c["valor"] >= h]
    if any(c["nome"] == "susto" for c in ativos):
        intencao = "susto"
    elif ativos:
        intencao = max(ativos, key=lambda c: (c["valor"], -CATALOGO_ASSISTIR.index(c["nome"])))["nome"]
    else:
        intencao = None
    return {"olhava": o["olhava"], "intencao": intencao, "conceitos": cs}


def decodificar_v4(motivo: dict, anterior: dict | None, cfg: ConfigDecodificador = CONFIG_DECODIFICADOR,
                   cfg_assistir: ConfigFalaAssistir = CONFIG_FALA_ASSISTIR, S: int = CONFIG_DIGIBRAIN_INATOS.escala) -> dict:
    """O `dec-v4` (FA-2): os 12 conceitos do dec-v1 com o `olhar` no catalogo de comportamentos (as contas sao as do dec-v1) e o bloco
    `assistir` (`conceitos_assistir`, ou None quando o pet nao olhava). Falha alto num motivo sem o olhar com o enjoo. O dec-v1 e o dec-v2
    nao mudam. So le: nada muda o cerebro nem a vida"""
    if "olhar" not in motivo:
        raise ValueError("o dec-v4 pede o motivo com o olhar (a subchave `olhar` do modular)")
    r = _decodificar(motivo, cfg, S, COMPORTAMENTOS_V4)
    r["versao"] = VERSAO_V4
    r["assistir"] = conceitos_assistir(motivo, anterior, cfg_assistir, S)
    return r
