"""A bancada da V2, módulo `config`.

A validação da config, o teto de pesos, a rede da config e a bancada da config.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

from dataclasses import replace

from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, ConfigLobos,
                            LIMITE_TETO_PESOS_PLANO)
from digilab.config import CONFIG_TROCA_DIGESTAO
from digilab.mundo import ESTILOS_LUGAR
from digilab.config import CONFIG_REDE_DE_SI_LIGADA, ConfigRedeDeSi

from . import RAIZ
from .bracos import PONTO_PADRAO


CHAVES_CONFIG = {"descricao", "plano", "bracos", "donos", "sementes", "unidades", "genomas", "mundos", "dias", "orcamento",
                 "sonda", "bootstrap", "acoplados", "consequencia", "lobos", "frutas", "ponto", "julgamento_fruta", "montagem",
                 "lugares", "mundo", "corpo", "teto_pesos", "rede_de_si", "digestao_lenta"}


def validar_config(cfg: dict) -> dict:
    faltam = {"bracos", "donos", "dias", "orcamento", "sonda", "bootstrap"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config: ou 'sementes' (x 'genomas') ou 'unidades' (bases x K derivadas), um dos dois")
    if "unidades" in cfg:
        u = cfg["unidades"]
        if not {"bases", "k"} <= set(u) <= {"bases", "k", "prefixo"} or "genomas" in cfg:
            raise ValueError(f"unidades fora do formato {{'bases': [...], 'k': K, 'prefixo'?}} (sem 'genomas'): {u}")
        unidades_derivadas(u["bases"], int(u["k"]), u.get("prefixo", "experimento-maior"))
        fora = sorted(set(u["bases"]) - SEMENTES_TESTE)
        if fora:
            plano = cfg.get("plano")
            if not plano or not (RAIZ / plano).is_file():
                raise SementeSemPlano(f"bases {fora} fora das dos testes: precisa do plano de analise registrado (campo 'plano')")
    if "ponto" in cfg and cfg["ponto"] not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {cfg['ponto']!r}: so {sorted(PONTOS_APRENDIZ)}")
    if "montagem" in cfg and cfg["montagem"] not in MONTAGENS:
        raise ValueError(f"montagem {cfg['montagem']!r}: so {MONTAGENS}")
    validar_teto_pesos(cfg)
    for b in cfg["bracos"]:
        braco_de(b)
    for m in cfg.get("mundos", ["padrao"]):
        mundo_de(m)
    if "rede_de_si" in cfg:
        cfg_rede_da_config(cfg)
        sem_corpo = sorted({b for b in cfg["bracos"] if braco_de(b).regime not in ("quimica", "corpo")}
                           | {a["braco"] for a in cfg.get("acoplados", []) if braco_de(a["braco"]).regime not in ("quimica", "corpo")})
        if sem_corpo:
            raise ValueError(f"a rede de si le os receptores do corpo: os bracos {sem_corpo} nao tem corpo (regime quimica ou corpo)")
    fisicos = [m for m in cfg.get("mundos", ["padrao"]) if mundo_de(m).fisico is not None]
    com_corpo_ = [b for b in cfg["bracos"] if BRACOS[b].regime in ("quimica", "corpo")]     # os bracos ja passaram pelo braco_de
    com_gestos = [b for b in cfg["bracos"] if BRACOS[b].gestos is not None]
    sem_gestos_ = [m for m in cfg.get("mundos", ["padrao"]) if mundo_de(m).fisico is not None or mundo_de(m).bola == "a1"]
    if com_gestos and sem_gestos_:
        raise ValueError(f"bracos com os gestos do dono {com_gestos} nos mundos {sem_gestos_}: os gestos ficam fora do mundo fisico e do "
                         "bola_a1")
    banheiro = [b for b in cfg["bracos"] if BRACOS[b].banheiro is not None]
    if banheiro and any(mundo_de(m).fisico is None for m in cfg.get("mundos", ["padrao"])):
        raise ValueError(f"bracos {banheiro}: o banheiro so no mundo fisico")
    tapa_x = [b for b in cfg["bracos"] if BRACOS[b].gestos == "tapa_fruta"]
    if tapa_x and any(not mundo_de(m).frutas for m in cfg.get("mundos", ["padrao"])):
        raise ValueError(f"bracos {tapa_x}: o tapa na fruta X so nos mundos das frutas")
    if "corpo" in cfg:
        if set(cfg["corpo"]) & set(SUBCHAVES_CORPO):
            raise ValueError(f"'corpo' troca os numeros da ConfigCorpo, nao as sub-chaves {SUBCHAVES_CORPO}: o regime e do braco")
        if not com_corpo_:
            raise ValueError("'corpo' sem braco com corpo (regime quimica ou corpo)")
    if fisicos:
        lugares = cfg.get("lugares")
        if not lugares or len(set(lugares)) != len(lugares) or any(lg not in ESTILOS_LUGAR for lg in lugares):
            raise ValueError(f"o mundo fisico pede 'lugares', sem repetir, de {ESTILOS_LUGAR}: {lugares}")
    elif "lugares" in cfg:
        raise ValueError("'lugares' so existe com o mundo fisico")
    if "mundo" in cfg:
        if not fisicos:
            raise ValueError("'mundo' (a ConfigMundo) so existe com o mundo fisico")
        replace(CONFIG_MUNDO_LIGADA, **cfg["mundo"])
    for a in cfg.get("acoplados", []):
        if set(a) != {"origem", "destino", "filtro"}:
            raise ValueError(f"acoplado fora do formato: {a}")
        try:
            filtro_de(a["filtro"])
        except KeyError as e:
            raise ValueError(f"acoplado fora do formato: {a}") from e
        braco_de(a["destino"])
        if a["origem"] not in cfg["bracos"]:
            raise ValueError(f"acoplado de um braco que nao roda: {a['origem']}")
    genomas = [g for g in cfg.get("genomas", [None]) if g is not None]
    usadas = set(cfg.get("sementes", [])) | set(genomas) | set(cfg.get("unidades", {}).get("bases", []))
    for ini, fim, motivo in FAIXAS_QUEIMADAS:
        queimadas = sorted(x for x in usadas if ini <= x <= fim)
        if queimadas:
            raise SementeSemPlano(f"sementes/bases {queimadas} na faixa queimada {ini}...{fim} ({motivo}): nao usar para nada")
    fora = sorted((set(cfg.get("sementes", [])) | set(genomas)) - SEMENTES_TESTE)
    if fora:
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes {fora} fora das dos testes {sorted(SEMENTES_TESTE)}: precisa do plano de analise "
                                  "registrado (campo 'plano', arquivo no repositorio)")
    return cfg


def cfg_lobos_do_ponto(ponto: str = PONTO_PADRAO, troca: dict | None = None) -> ConfigLobos:
    """O aprendiz de um ponto nomeado (PONTOS_APRENDIZ), com os campos de `troca` por cima. Ponto desconhecido falha alto."""
    if ponto not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {ponto!r}: so {sorted(PONTOS_APRENDIZ)}")
    base = replace(CONFIG_LOBOS_APRENDIZ, **PONTOS_APRENDIZ[ponto])
    return replace(base, **troca) if troca else base


def validar_teto_pesos(cfg: dict) -> int | None:
    """O teto de pesos declarado pelo plano (TP-1 e TP-2, docs/DECISAO_V2_TETO_PESOS.md). Sem a chave "teto_pesos", None: o padrao da
    ConfigLobos (1000) e a bancada de hoje, byte a byte. Com ela, {"maximo": N, "pesos": n}:
      - N inteiro acima do padrao e ate LIMITE_TETO_PESOS_PLANO (2000);
      - n os pesos do maior cerebro A dos bracos da config, de N - 1 para baixo e do padrao para cima (um cerebro que cabe no padrao nao
        precisa de teto proprio). A run confere n contra o cerebro montado (`conferir_teto_pesos`);
      - o `plano` da config, um arquivo do repositorio: e o texto que diz por que.
    O teto so entra por aqui: "maximo_pesos" na chave "lobos" falha alto."""
    if "maximo_pesos" in (cfg.get("lobos") or {}):
        raise ValueError("o teto de pesos so entra pela chave 'teto_pesos' (o plano declara o teto e os pesos), nao por 'lobos'")
    t = cfg.get("teto_pesos")
    if t is None:
        return None
    if not isinstance(t, dict) or set(t) != {"maximo", "pesos"}:
        raise ValueError(f"teto_pesos: {{'maximo': N, 'pesos': n}}, nao {t!r}")
    padrao = ConfigLobos().maximo_pesos
    maximo, pesos = t["maximo"], t["pesos"]
    if type(maximo) is not int or not padrao < maximo <= LIMITE_TETO_PESOS_PLANO:
        raise ValueError(f"teto_pesos.maximo {maximo!r}: inteiro acima do padrao ({padrao}) e ate o limite ({LIMITE_TETO_PESOS_PLANO}, "
                         "TP-2; acima pede decisao nova)")
    if type(pesos) is not int or not padrao <= pesos < maximo:
        raise ValueError(f"teto_pesos.pesos {pesos!r}: inteiro de {padrao} (abaixo, o cerebro cabe no padrao) a {maximo - 1}")
    plano = cfg.get("plano")
    if not plano or not (RAIZ / plano).is_file():
        raise SementeSemPlano("teto_pesos: o teto proprio e de um plano (TP-1): precisa do campo 'plano' com o arquivo que diz por que")
    return maximo


def conferir_teto_pesos(cfg: dict, cerebros) -> dict | None:
    """Com o teto declarado, os pesos do maior cerebro A dos bracos (`cerebros`: nome -> cerebro montado pela bancada) tem de ser os
    declarados em teto_pesos.pesos: falha alto se nao forem. Sem teto declarado, None (nada e conferido: a bancada de hoje)."""
    if validar_teto_pesos(cfg) is None:
        return None
    pesos = {nome: c.n_pesos() for nome, c in cerebros.items() if hasattr(c, "n_pesos")}
    if not pesos:
        raise RuntimeError("teto_pesos declarado sem nenhum cerebro A nos bracos da config")
    maior = max(pesos.values())
    if maior != cfg["teto_pesos"]["pesos"]:
        raise RuntimeError(f"teto_pesos.pesos {cfg['teto_pesos']['pesos']}: o maior cerebro dos bracos tem {maior} ({pesos})")
    return {"maximo": cfg["teto_pesos"]["maximo"], "pesos": maior, "por_cerebro": pesos}


def cfg_rede_da_config(cfg: dict) -> ConfigRedeDeSi:
    """A chave `rede_de_si` da config: campos da ConfigRedeDeSi por cima da ligada (`{}` = os padroes). Desligar por ela falha alto."""
    troca = cfg["rede_de_si"]
    if not isinstance(troca, dict) or troca.get("ligada", True) is not True:
        raise ValueError(f"rede_de_si: um dict com campos da ConfigRedeDeSi, sempre ligada (sem a chave, sem a rede), nao {troca!r}")
    tupla = lambda v: tuple(v) if isinstance(v, list) else v  # noqa: E731
    return replace(CONFIG_REDE_DE_SI_LIGADA, **{k: tupla(v) for k, v in troca.items()})


def bancada_da_config(cfg: dict) -> Bancada:
    """A Bancada da config: os padroes, e o que as chaves "consequencia", "ponto" e "lobos" (o ponto nomeado, e por cima dele os campos
    da chave "lobos"; sem "ponto", o L1 = CONFIG_LOBOS_APRENDIZ) e "frutas" (sobre o CONFIG_FRUTAS_LIGADA; listas do JSON viram tuplas)
    trocam. Sem essas chaves, a bancada de sempre (REVISAO-APRENDIZ)."""
    cc = CONFIG_CONSEQUENCIA if "consequencia" not in cfg else replace(CONFIG_CONSEQUENCIA, **cfg["consequencia"])
    kw = {"cfg_consequencia": cc}
    teto = validar_teto_pesos(cfg)
    if "lobos" in cfg or "ponto" in cfg or teto is not None:
        troca = dict(cfg.get("lobos") or {})
        if teto is not None:                      # o teto declarado pelo plano (TP-1); sem ele, o padrao da ConfigLobos
            troca["maximo_pesos"] = teto
        kw["cfg_lobos"] = cfg_lobos_do_ponto(cfg.get("ponto", PONTO_PADRAO), troca or None)
    if cfg.get("julgamento_fruta"):
        kw["julgamento_fruta"] = True
    if "montagem" in cfg:
        kw["montagem"] = cfg["montagem"]
    tupla = lambda v: tuple(tupla(x) for x in v) if isinstance(v, list) else v  # noqa: E731
    if "frutas" in cfg:
        kw["cfg_frutas"] = replace(CONFIG_FRUTAS_LIGADA, **{k: tupla(v) for k, v in cfg["frutas"].items()})
    if "mundo" in cfg:
        kw["cfg_mundo"] = replace(CONFIG_MUNDO_LIGADA, **{k: tupla(v) for k, v in cfg["mundo"].items()})
    if "corpo" in cfg:
        kw["cfg_corpo"] = replace(CONFIG_CORPO_QUIMICA, **{k: tupla(v) for k, v in cfg["corpo"].items()})
    if "rede_de_si" in cfg:
        kw["cfg_rede"] = cfg_rede_da_config(cfg)
    if "digestao_lenta" in cfg:
        kw["cfg_troca_digestao"] = replace(CONFIG_TROCA_DIGESTAO, **cfg["digestao_lenta"])
    return Bancada(int(cfg["dias"]), int(cfg["orcamento"]), **kw)


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .faixas import FAIXAS_QUEIMADAS, SEMENTES_TESTE, SementeSemPlano, unidades_derivadas  # noqa: E402
from .mundos import CONFIG_CORPO_QUIMICA, mundo_de, SUBCHAVES_CORPO  # noqa: E402
from .bracos import braco_de, BRACOS, filtro_de, MONTAGENS, PONTOS_APRENDIZ  # noqa: E402
from .nucleo import Bancada  # noqa: E402
