"""V2, experimento maior: o orquestrador (docs/TAREFA_V2_BANCADA_EXPERIMENTO.md, docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md).

Monta, pela bancada (experiments/bancada_v2.py), os bracos P0, P1, P2, P2e e P3 nos mundos casado_frutas, descasado e mutavel, com o
dono principal (atencioso) e o "so cuidado" acoplado de cada braco com dono (P2, P2e e P3 no proprio registro sem os sinais e sem a
informacao: filtro `sem_ensino`, as ofertas ficam; secao 1). Do `medidas.json` da bancada tira:

  - os seis contrastes primarios unilaterais (secao 6.2), pareados por unidade, orientados para a predicao (positivo = o que ela diz),
    com o bootstrap reamostrando as SEMENTES (a unidade de ambiente) e Holm sobre a familia (E8);
  - a equivalencia da predicao 5 (P3 - P0, IC de 90% dentro de (-delta, +delta)), fora da familia;
  - as leituras por predicao (confirma, refuta, inconclusivo, inconclusivo por duracao; confirma parcialmente na predicao 2) pelas
    regras da secao 5, e a separacao do cuidado da secao 5.1 nos contrastes com P2, P2e e P3;
  - as curvas por dia, a margem delta (secao 6.3), sigma_d e o N por contraste (secao 7.2).

Grava: <saida>/frutas/ (a run da bancada: vidas, medidas, tabelas braco x condicao, meta), <saida>/padrao/ (a referencia do mundo
padrao, P0, P1 e P3, so descritiva; E1), contrastes.json, curvas.json, resumo.json e meta.json. Toda vida e rejogada do disco bit a bit
pela bancada (G1).

Modos, pelas sementes: "fumaca" (so as sementes dos testes, 101...505; nao canonica), "calibracao" (bases 14101...14505; delta medido
na propria run) e "validacao" (bases 15101...15505; delta do adendo, obrigatorio). Os dois ultimos pedem o campo "plano" com este
plano, as unidades derivadas e a vida de 14 dias (E5). Nesta tarefa so a fumaca roda.

Uso:  python experiments/run_v2_experimento_maior.py --config experiments/configs/v2_experimento_maior/fumaca.json --saida <pasta>
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402
from digilab.metrics import (contraste_pareado, dentro_da_margem, holm, inclinacao_mmq,  # noqa: E402
                             tamanho_amostra)
from digilab.protocol import PROTOCOLO_ARENA_V1  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md"
BRACOS = ("P0", "P1", "P2", "P2e", "P3")
MUNDOS = ("casado_frutas", "descasado", "mutavel")
DONO_PRINCIPAL = "atencioso"
COM_DONO = ("P2", "P2e", "P3")                      # os bracos com o "so cuidado" acoplado (secao 1)
FILTRO_SO_CUIDADO = "sem_ensino"                    # sem sinais e sem a informacao; as ofertas e o cuidado ficam (F7)
BRACOS_PADRAO = ("P0", "P1", "P3")                  # a referencia do mundo padrao (sem frutas, sem informacao)
DIAS_PLANO = 14                                     # E5
DIAS_INCLINACAO = 4                                 # "dias 11 a 14" numa vida de 14: os 4 ultimos dias (predicao 2)
CHAVES = {"descricao", "plano", "unidades", "sementes", "genomas", "dias", "orcamento", "ponto", "lobos", "consequencia",
          "frutas", "sonda", "bootstrap", "delta", "alfa", "poder", "donos", "referencia_padrao"}
BOOTSTRAP_PADRAO = {"reamostragens": PROTOCOLO_ARENA_V1.bootstrap_reamostragens.valor,
                    "semente": PROTOCOLO_ARENA_V1.bootstrap_semente.valor, "nivel": PROTOCOLO_ARENA_V1.nivel_confianca.valor}
# Contrato K4 (secao 1, E7): o dono do P3 julga a escolha de fruta pelo efeito real (JulgadorFruta, #170), ligado na bancada pela
# BANCADA-K4-CANAIS (chave "julgamento_fruta", fora do orcamento, decisao do Matheus de 2026-10-05). Com False, a predicao 5 sairia com o
# aviso de que mede so que o P3 nao sabe das frutas.
K4_DONO_JULGA_FRUTA = True
# BANCADA-MONTAGEM (decisao do Matheus de 2026-10-05, opcao 1): o cerebro A montado da secao 1 do PLANO_CALIBRACAO_CONJUNTA_V2 em cada
# braco (chave "montagem" da bancada): memoria em P1 a P3, canais em P1 e P2, w0_info so nos P2, o P0 o instinto. Vale na K2 e na validacao.
MONTAGEM = "completa"


@dataclass(frozen=True)
class Contraste:
    nome: str
    predicao: int
    mundo: str
    medida: str          # janela da taxa_fruta_ruim ("inicio", "final", "depois_da_troca") ou "consumos_ate_metade"
    mais: str            # d = mais - menos; positivo = o que a predicao diz
    menos: str


PRIMARIOS = (
    Contraste("p1_casado", 1, "casado_frutas", "final", "P1", "P0"),
    Contraste("p2_descasado", 2, "descasado", "final", "P0", "P1"),
    Contraste("p2_mutavel", 2, "mutavel", "depois_da_troca", "P0", "P1"),
    Contraste("p3_consumos", 3, "descasado", "consumos_ate_metade", "P1", "P2"),
    Contraste("p4a_piora", 4, "descasado", "inicio", "P2e", "P1"),
    Contraste("p4b_recupera", 4, "descasado", "final", "P0", "P2e"),
)
EQUIVALENCIA = Contraste("p5_equivalencia", 5, "descasado", "final", "P3", "P0")
SECUNDARIOS = (                                     # descritivos (secao 6.2): a predicao 1 com os outros bracos
    Contraste("p1_casado_P2", 1, "casado_frutas", "final", "P2", "P0"),
    Contraste("p1_casado_P3", 1, "casado_frutas", "final", "P3", "P0"),
)


# ------------------------------------------------------------------ config e modo


def modo_e_unidades(cfg: dict) -> tuple[str, list[dict]]:
    """O modo pela origem das sementes, e as unidades (genoma, semente, base, k). Mistura de faixas, faixa de outro experimento ou
    validacao/calibracao fora das regras do plano falham alto."""
    sobram = set(cfg) - CHAVES
    if sobram:
        raise ValueError(f"config: chaves desconhecidas {sorted(sobram)}")
    for k in ("dias", "orcamento", "sonda"):
        if k not in cfg:
            raise ValueError(f"config: falta {k!r}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config: ou 'sementes' (so na fumaca) ou 'unidades' (bases x K derivadas)")
    if "unidades" in cfg:
        bases = set(cfg["unidades"]["bases"])
        unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]))
    else:
        bases = set(cfg["sementes"]) | {g for g in cfg.get("genomas", []) if g is not None}
        unidades = [{"genoma": g, "semente": int(s), "base": None, "k": None}
                    for g in cfg.get("genomas", [None]) for s in cfg["sementes"]]
    cal, val = set(bv.BASES_EXPERIMENTO_MAIOR["calibracao"]), set(bv.BASES_EXPERIMENTO_MAIOR["validacao"])
    if bases <= bv.SEMENTES_TESTE:
        modo = "fumaca"
    elif bases <= cal:
        modo = "calibracao"
    elif bases <= val:
        modo = "validacao"
    else:
        raise bv.SementeSemPlano(f"sementes {sorted(bases)}: so as dos testes, ou as bases de UMA faixa do experimento maior "
                                 f"(calibracao {sorted(cal)} ou validacao {sorted(val)}), sem misturar")
    if modo != "fumaca":
        if cfg.get("plano") != PLANO or not (RAIZ / PLANO).is_file():
            raise bv.SementeSemPlano(f"{modo}: precisa do campo 'plano' = {PLANO!r}")
        if "unidades" not in cfg:
            raise ValueError(f"{modo}: so com as unidades derivadas (E3)")
        if int(cfg["dias"]) != DIAS_PLANO:
            raise ValueError(f"{modo}: a vida e de {DIAS_PLANO} dias (E5), nao {cfg['dias']}")
        if modo == "validacao" and not isinstance(cfg.get("delta"), (int, float)):
            raise ValueError("validacao: o delta vem do adendo (secao 7.3), numero obrigatorio")
        if modo == "calibracao" and cfg.get("delta") is not None:
            raise ValueError("calibracao: o delta e medido na propria calibracao (secao 6.3), nao dado")
    donos = cfg.get("donos", [DONO_PRINCIPAL])
    if DONO_PRINCIPAL not in donos:
        raise ValueError(f"o dono principal ({DONO_PRINCIPAL}) tem de rodar")
    return modo, unidades


def config_da_bancada(cfg: dict, bracos, mundos, acoplados) -> dict:
    out = {k: cfg[k] for k in ("plano", "unidades", "sementes", "genomas", "dias", "orcamento", "lobos", "consequencia", "frutas",
                               "sonda") if k in cfg}
    out.update({"descricao": f"experimento maior: {cfg.get('descricao', '')}", "bracos": list(bracos), "mundos": list(mundos),
                "donos": cfg.get("donos", [DONO_PRINCIPAL]), "acoplados": acoplados, "ponto": cfg.get("ponto", bv.PONTO_N5_EXPERIMENTO),
                "bootstrap": cfg.get("bootstrap", BOOTSTRAP_PADRAO), "julgamento_fruta": K4_DONO_JULGA_FRUTA,
                "montagem": MONTAGEM})
    return out


# ------------------------------------------------------------------ valores por unidade


def _chave_unidade(m: dict) -> tuple:
    return (m["genoma"], m["semente"])


def valor(m: dict, medida: str):
    """A medida de uma vida: a taxa da fruta ruim numa janela, ou os consumos ate a metade (None sem referencia ou sem consumo)."""
    f = m["frutas"]
    if f is None:
        raise ValueError(f"{m['vida']}: sem frutas")
    if medida == "consumos_ate_metade":
        return f["consumos_ate_metade"]["consumos"]
    return f["taxa_fruta_ruim"][medida]["taxa"]


def indice(medidas: dict, dono: str = DONO_PRINCIPAL) -> dict:
    """(rotulo do braco, mundo, unidade) -> medidas da vida, so do dono dado. O rotulo do acoplado e o da bancada ("P2<P2:sem_ensino")."""
    idx = {}
    for m in medidas.values():
        if m["dono"] == dono:
            chave = (m["braco"], m["mundo"], _chave_unidade(m))
            if chave in idx:
                raise ValueError(f"vida repetida: {chave}")
            idx[chave] = m
    return idx


def rotulo_so_cuidado(braco: str) -> str:
    return f"{braco}<{braco}:{FILTRO_SO_CUIDADO}"


def diferencas(idx: dict, unidades: list[dict], mundo: str, medida: str, mais: str, menos: str, sinal: float = 1.0) -> dict:
    """{semente: [sinal * (mais - menos) por unidade]} e as unidades sem valor (contadas, nunca somem)."""
    grupos, faltam = {}, []
    for u in unidades:
        ku = (u["genoma"], u["semente"])
        a, b = (valor(idx[(r, mundo, ku)], medida) for r in (mais, menos))
        if a is None or b is None:
            faltam.append({"genoma": u["genoma"], "semente": u["semente"], mais: a, menos: b})
            continue
        grupos.setdefault(u["semente"], []).append(sinal * (a - b))
    return {"grupos": grupos, "sem_valor": faltam}


def calcular_contraste(idx, unidades, c: Contraste, boot: dict) -> dict:
    d = diferencas(idx, unidades, c.mundo, c.medida, c.mais, c.menos)
    r = contraste_pareado(d["grupos"], boot["reamostragens"], boot["semente"])
    return {"nome": c.nome, "predicao": c.predicao, "mundo": c.mundo, "medida": c.medida, "d": f"{c.mais} - {c.menos}",
            **r, "sem_valor": d["sem_valor"], "valores": {str(k): v for k, v in d["grupos"].items()}}


# ------------------------------------------------------------------ margem, curvas e duracao


def delta_da_regra(idx, unidades) -> dict:
    """Secao 6.3: delta = metade da distancia entre a taxa_fruta_ruim do P0 no descasado (janela final, a das predicoes) e 0."""
    taxas = [valor(idx[("P0", "descasado", (u["genoma"], u["semente"]))], "final") for u in unidades]
    com = [t for t in taxas if t is not None]
    if not com:
        return {"delta": None, "taxa_p0": None, "n": 0, "sem_valor": len(taxas)}
    media = sum(com) / len(com)
    return {"delta": media / 2.0, "taxa_p0": media, "n": len(com), "sem_valor": len(taxas) - len(com)}


def curvas(idx, unidades, dias: int) -> dict:
    """Media por dia da taxa da fruta ruim, por braco e mundo (dias sem consumo nao entram; n por dia)."""
    out = {}
    for b in BRACOS:
        for mundo in MUNDOS:
            serie = []
            for d in range(1, dias + 1):
                vs = [valor(idx[(b, mundo, (u["genoma"], u["semente"]))], f"dia_{d}") for u in unidades]
                com = [v for v in vs if v is not None]
                serie.append({"dia": d, "media": (sum(com) / len(com)) if com else None, "n": len(com)})
            out[f"{b}/{mundo}"] = serie
    return out


def dia_do_cruzamento(acima: list[dict], abaixo: list[dict]) -> int | None:
    """O primeiro dia em que a curva `acima` (P2e) fica <= a `abaixo` (P0), depois de um dia em que esteve acima (predicao 4)."""
    esteve_acima = False
    for a, b in zip(acima, abaixo):
        if a["media"] is None or b["media"] is None:
            continue
        if a["media"] > b["media"]:
            esteve_acima = True
        elif esteve_acima:
            return a["dia"]
    return None


def inclinacao_final(idx, unidades, mundo: str, dias: int, boot: dict) -> dict:
    """Predicao 2, "se a vida for longa": a inclinacao de P0 - P1 (taxa por dia) nos ultimos DIAS_INCLINACAO dias, por unidade, com
    o IC do bootstrap sobre as sementes. `cresce` = IC 95% inteiro acima de 0."""
    if dias < DIAS_INCLINACAO:
        return {"dias": None, "cresce": False, "motivo": f"vida com menos de {DIAS_INCLINACAO} dias"}
    janela = list(range(dias - DIAS_INCLINACAO + 1, dias + 1))
    grupos, sem = {}, 0
    for u in unidades:
        ku = (u["genoma"], u["semente"])
        pts = []
        for d in janela:
            a = valor(idx[("P0", mundo, ku)], f"dia_{d}")
            b = valor(idx[("P1", mundo, ku)], f"dia_{d}")
            if a is not None and b is not None:
                pts.append((d, a - b))
        if len({x for x, _ in pts}) < 2:
            sem += 1
            continue
        grupos.setdefault(u["semente"], []).append(inclinacao_mmq([x for x, _ in pts], [y for _, y in pts]))
    r = contraste_pareado(grupos, boot["reamostragens"], boot["semente"])
    cresce = r["ic95"] is not None and r["ic95"]["ic_inferior"] > 0.0
    return {"dias": janela, **r, "sem_valor": sem, "cresce": cresce}


def tamanhos(contrastes: dict, delta: float | None, alfa: float, poder: float) -> dict:
    """Secao 7.2: sigma_d e N por contraste primario (alfa / 6, o passo mais exigente de Holm), e o N da validacao = o maior, ao
    multiplo de 5. Sem delta > 0 ou sem 2 unidades, None com o motivo. A conferencia por simulacao fica para o adendo."""
    out, ns = {}, []
    for nome, c in contrastes.items():
        vs = [x for g in c["valores"].values() for x in g]
        if len(vs) < 2 or not delta:
            out[nome] = {"sigma_d": None, "n": None, "motivo": "menos de 2 unidades com valor ou delta <= 0"}
            continue
        m = sum(vs) / len(vs)
        sigma = math.sqrt(sum((x - m) ** 2 for x in vs) / (len(vs) - 1))
        n = tamanho_amostra(sigma, delta, alfa / len(contrastes), poder, 5)
        out[nome] = {"sigma_d": sigma, "n": n}
        ns.append(n)
    return {"por_contraste": out, "n_validacao": max(ns) if ns else None, "alfa_passo": alfa / len(contrastes), "poder": poder}


# ------------------------------------------------------------------ leituras (secao 5)


def _ic95_abaixo_de_zero(c: dict) -> bool:
    return c["ic95"] is not None and c["ic95"]["ic_superior"] < 0.0


def leitura_positiva(c: dict, h: dict, delta: float | None, refuta_por_equivalencia: bool = True) -> str:
    """Confirma = rejeitado por Holm na direcao predita; refuta = IC 95% inteiro abaixo de 0 ou (quando a predicao diz) IC 90% inteiro
    dentro de (-delta, +delta); o resto, inconclusivo."""
    if h["rejeita"]:
        return "confirma"
    if _ic95_abaixo_de_zero(c) or (refuta_por_equivalencia and dentro_da_margem(c["ic90"], delta)):
        return "refuta"
    return "inconclusivo"


def leitura_p2(lds: dict, cresce: dict, k2: bool) -> str:
    """Predicao 2: as duas condicoes confirmam = confirma; so uma = confirma parcialmente; qualquer uma refuta = refuta; senao
    inconclusivo. Sem confirmar, se a diferenca ainda cresce no fim numa condicao que nao confirmou: inconclusivo por duracao. Sem o
    K2 (o humor da fruta no sinal do P1, E2): nao testavel."""
    if not k2:
        return "nao_testavel"
    vs = list(lds.values())
    if all(v == "confirma" for v in vs):
        return "confirma"
    if any(v == "refuta" for v in vs):
        base = "refuta"
    elif any(v == "confirma" for v in vs):
        return "confirma_parcialmente"
    else:
        base = "inconclusivo"
    if any(cresce[m] and lds[m] != "confirma" for m in lds):
        return "inconclusivo_por_duracao"
    return base


def leitura_p4(ca: dict, ha: dict, cb: dict, hb: dict, delta: float | None) -> str:
    """Predicao 4: (a) e (b) rejeitados por Holm = confirma; (a) vale e (b) tem IC 95% abaixo de 0 ou IC 90% dentro da margem =
    refuta (a recuperacao); o resto, inconclusivo."""
    if ha["rejeita"] and hb["rejeita"]:
        return "confirma"
    if ha["rejeita"] and (_ic95_abaixo_de_zero(cb) or dentro_da_margem(cb["ic90"], delta)):
        return "refuta"
    return "inconclusivo"


def leitura_equivalencia(c: dict, delta: float | None) -> str:
    """Predicao 5: IC 90% dentro de (-delta, +delta) = confirma; IC 95% inteiro fora da margem = refuta; o resto, inconclusivo."""
    if delta is None:
        return "inconclusivo"
    if dentro_da_margem(c["ic90"], delta):
        return "confirma"
    ic = c["ic95"]
    if ic is not None and (ic["ic_inferior"] > delta or ic["ic_superior"] < -delta):
        return "refuta"
    return "inconclusivo"


def separacao_do_cuidado(idx, unidades, c: Contraste, boot: dict) -> dict:
    """Secao 5.1, para cada braco com dono no contraste: (a) o braco difere do proprio "so cuidado" acoplado na direcao do contraste
    (IC 95% acima de 0); (b) sem diferenca de saude media e de tempo fora de privacao entre o braco e o acoplado (IC 95% contendo 0;
    nos mundos das frutas nao ha morte: lesoes desligadas). Leitura: ensino (a e b), ensino misturado com cuidado (so a), sem efeito
    acima do so cuidado (sem a)."""
    out = {}
    for braco, sinal in ((c.mais, 1.0), (c.menos, -1.0)):
        if braco not in COM_DONO:
            continue
        aco = rotulo_so_cuidado(braco)
        a = contraste_pareado(diferencas(idx, unidades, c.mundo, c.medida, braco, aco, sinal)["grupos"], boot["reamostragens"],
                              boot["semente"])
        cuidado = {}
        for med in ("saude_media", "fracao_fora_de_privacao"):
            grupos = {}
            for u in unidades:
                ku = (u["genoma"], u["semente"])
                grupos.setdefault(u["semente"], []).append(idx[(braco, c.mundo, ku)][med] - idx[(aco, c.mundo, ku)][med])
            r = contraste_pareado(grupos, boot["reamostragens"], boot["semente"])
            ic = r["ic95"]
            cuidado[med] = {**r, "igual": ic is None or (ic["ic_inferior"] <= 0.0 <= ic["ic_superior"])}
        va = a["ic95"] is not None and a["ic95"]["ic_inferior"] > 0.0
        vb = all(x["igual"] for x in cuidado.values())
        leitura = "ensino" if va and vb else "ensino_misturado_com_cuidado" if va else "sem_efeito_acima_do_so_cuidado"
        out[braco] = {"so_cuidado": aco, "a_acima_do_so_cuidado": a, "b_cuidado": cuidado, "leitura": leitura}
    return out


# ------------------------------------------------------------------ analise


def analisar(medidas: dict, unidades: list[dict], cfg: dict, modo: str, k2: bool) -> dict:
    """A analise inteira a partir das medidas da bancada (a funcao que os testes alimentam com dados sinteticos)."""
    boot = cfg.get("bootstrap", BOOTSTRAP_PADRAO)
    alfa, poder, dias = float(cfg.get("alfa", 0.05)), float(cfg.get("poder", 0.8)), int(cfg["dias"])
    idx = indice(medidas)
    if cfg.get("delta") is not None:
        regra = {"delta": float(cfg["delta"]), "origem": "adendo (secao 7.3)"}
    else:
        regra = {**delta_da_regra(idx, unidades), "origem": "regra da secao 6.3 medida nesta run"}
    delta = regra["delta"]
    primarios = {c.nome: calcular_contraste(idx, unidades, c, boot) for c in PRIMARIOS}
    h = holm({n: c["p_unilateral"] for n, c in primarios.items()}, alfa)
    for n in primarios:
        primarios[n]["holm"] = h[n]
    eq = calcular_contraste(idx, unidades, EQUIVALENCIA, boot)
    secundarios = {c.nome: calcular_contraste(idx, unidades, c, boot) for c in SECUNDARIOS}
    cv = curvas(idx, unidades, dias)
    cresce = {m: inclinacao_final(idx, unidades, m, dias, boot) for m in ("descasado", "mutavel")}
    cuidado = {c.nome: separacao_do_cuidado(idx, unidades, c, boot) for c in PRIMARIOS + (EQUIVALENCIA,)
               if c.mais in COM_DONO or c.menos in COM_DONO}

    ld = {n: leitura_positiva(primarios[n], h[n], delta) for n in ("p1_casado", "p2_descasado", "p2_mutavel")}
    censura = {}
    for b in ("P1", "P2"):
        cs = [idx[(b, "descasado", (u["genoma"], u["semente"]))]["frutas"]["consumos_ate_metade"] for u in unidades]
        censura[b] = {"censuradas": sum(1 for x in cs if x["censurado"]), "sem_referencia": sum(1 for x in cs if x["sem_referencia"]),
                      "n": len(cs)}
    predicoes = {
        "1": {"leitura": ld["p1_casado"], "contrastes": ["p1_casado"], "secundarios": list(secundarios)},
        "2": {"leitura": leitura_p2({"descasado": ld["p2_descasado"], "mutavel": ld["p2_mutavel"]},
                                    {m: cresce[m]["cresce"] for m in cresce}, k2),
              "por_condicao": {"descasado": ld["p2_descasado"], "mutavel": ld["p2_mutavel"]},
              "contrastes": ["p2_descasado", "p2_mutavel"], "k2": k2,
              "inclinacao_final": {m: {k: cresce[m][k] for k in ("dias", "media", "ic95", "n", "sem_valor", "cresce")}
                                   for m in cresce}},
        "3": {"leitura": leitura_positiva(primarios["p3_consumos"], h["p3_consumos"], delta, refuta_por_equivalencia=False),
              "contrastes": ["p3_consumos"], "censura": censura},
        "4": {"leitura": leitura_p4(primarios["p4a_piora"], h["p4a_piora"], primarios["p4b_recupera"], h["p4b_recupera"], delta),
              "contrastes": ["p4a_piora", "p4b_recupera"],
              "dia_do_cruzamento_P2e_P0": dia_do_cruzamento(cv["P2e/descasado"], cv["P0/descasado"])},
        "5": {"leitura": leitura_equivalencia(eq, delta), "contrastes": ["p5_equivalencia"], "k4": K4_DONO_JULGA_FRUTA,
              **({} if K4_DONO_JULGA_FRUTA else {"aviso": "K4 fora da main: o dono do P3 nao julga a fruta; a predicao 5 mede so que "
                                                           "o P3 nao sabe das frutas (E7)"})},
    }
    for p in predicoes.values():
        p["cuidado"] = {n: {b: x["leitura"] for b, x in cuidado[n].items()} for n in p["contrastes"] if n in cuidado}
    return {"modo": modo, "status": "resultado" if modo == "validacao" else "piloto, nao resultado",
            "delta": regra, "alfa": alfa, "primarios": primarios, "equivalencia": eq, "secundarios": secundarios,
            "separacao_do_cuidado": cuidado, "curvas": cv, "predicoes": predicoes,
            "tamanho_amostra": tamanhos(primarios, delta, alfa, poder)}


def rodar(cfg: dict, pasta: Path) -> dict:
    modo, unidades = modo_e_unidades(cfg)
    acoplados = [{"origem": b, "destino": b, "filtro": FILTRO_SO_CUIDADO} for b in COM_DONO]
    cb = config_da_bancada(cfg, BRACOS, MUNDOS, acoplados)
    r = bv.rodar(cb, pasta / "frutas")
    padrao = None
    if cfg.get("referencia_padrao", True):
        padrao = bv.rodar(config_da_bancada(cfg, BRACOS_PADRAO, ("padrao",), []), pasta / "padrao")
    k2 = bv.bancada_da_config(cb).cfg_consequencia.humor_na_fruta
    a = analisar(r["medidas"], unidades, cfg, modo, k2)
    resumo = {"modo": a["modo"], "status": a["status"], "delta": a["delta"], "alfa": a["alfa"],
              "predicoes": a["predicoes"], "tamanho_amostra": a["tamanho_amostra"],
              "contratos": {"K2_humor_da_fruta_no_P1": k2, "K4_dono_julga_fruta": K4_DONO_JULGA_FRUTA,
                            "montagem": MONTAGEM},
              "vidas": {"frutas": len(r["vidas"]), "padrao": len(padrao["vidas"]) if padrao else 0},
              "unidades": len(unidades)}
    contrastes = {k: a[k] for k in ("primarios", "equivalencia", "secundarios", "separacao_do_cuidado")}
    bv._gravar(pasta / "contrastes.json", bv._dump(contrastes))
    bv._gravar(pasta / "curvas.json", bv._dump(a["curvas"]))
    bv._gravar(pasta / "resumo.json", bv._dump(resumo))
    bv._gravar(pasta / "meta.json", bv._dump({"config": cfg, "modo": modo, "plano": PLANO, "plano_sha256": bv._sha(RAIZ / PLANO),
                                               "orquestrador_sha256": bv._sha(Path(__file__)), "python": platform.python_version()}))
    return {"modo": modo, "unidades": unidades, "frutas": r, "padrao": padrao, "analise": a, "resumo": resumo}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="experimento maior da V2 (docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida))
    print(f"{r['modo']}: {r['resumo']['vidas']} vidas rejogadas do disco bit a bit; "
          + "; ".join(f"predicao {k}: {v['leitura']}" for k, v in r["resumo"]["predicoes"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
