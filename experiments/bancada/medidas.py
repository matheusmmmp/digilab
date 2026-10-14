"""A bancada da V2, módulo `medidas`.

As medidas que não são métodos da Bancada: o banheiro, a rede de si, as sondas e as tabelas.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import json
import random

from digilab.ambiente import _PoliticaComBola
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA
from digilab.config import ConfigCorpo
from digilab.corpo import Corpo, div_arred as div_arred_corpo
from digilab.motor_corpo import PercepcaoCorpo
from digilab.frutas import _PoliticaComFrutas
from digilab.metrics import tabela_braco_condicao, tabela_braco_condicao_parcial
from digilab.metrics import cuidado_preservado
from digilab.metrics import leitura_dominancia
from digilab.metrics import alivios_ate_criterio, alivios_por_dia, curva_sobrevivencia, dia_do_criterio
from digilab.mundo import _PoliticaComMundo
from digilab.obediencia import _PoliticaObservada
from digilab.policies.lobos import RECEPTORES_NOVOS
from digilab.policies.lobos import arred
from digilab.config import ConfigRedeDeSi
from digilab.rede_de_si import ACOES as ACOES_REDE, CONTEXTO as CONTEXTO_REDE, PoliticaComRede, RedeDeSi
from digilab.rede_de_si import div_arred
from digilab.corpo import todos_receptores_orgaos
from digilab.policies.lobos import sortear
from digilab.state import Estado


MEDIDAS_TABELA = ("fracao_fora_de_privacao", "saude_media", "humor_medio", "acerto_total", "deriva_final")


def receptores_novos_de(cc: ConfigCorpo, com_mundo: bool = False) -> tuple[str, ...]:
    """Os receptores novos que o corpo desta ConfigCorpo tem (os da tabela do grafo, `Corpo.receptores`), na ordem de RECEPTORES_NOVOS:
    nenhum na quimica; tedio, solidao e estresse com `drives_novos`; dor e susto com `gestos`; a curiosidade so com o mundo fisico (CD-8)."""
    nomes = set(Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo).receptores())
    return tuple(r for r in RECEPTORES_NOVOS if r in nomes)


def medidas_banheiro_de(alivios, dias: int, carinhos=(), limpador=(), pesos_alvo=None, cuidado=(), escolhas=()) -> dict:
    """As medidas do PLANO_ANALISE_V2_BANHEIRO numa vida, das funcoes do #224 (`metrics`). As entradas, sem o motor:
      - `alivios`: (tick, dentro do banheiro, urgente) por `aliviar`;
      - `carinhos`: (tick, solidao antes na escala 0-1, sinal pelo corpo) por carinho depois do banheiro;
      - `limpador`: (tick, sinal pelo corpo) por alivio recolhido pelo limpador;
      - `pesos_alvo`: os pesos do alvo no fim de cada dia, {"banheiro": w, "aqui": w} (um por dia, ou None);
      - `cuidado`: (tick, em privacao, saude, fome) por decisao;
      - `escolhas`: (tick, alvo, terminou dentro, distancia) por `aliviar` decidido (sem o urgente), para o "chegou tarde" (R-2).
    Sai: a fracao diaria e os acidentes (`alivios_por_dia`); o dia do criterio com a censura e T* (`dia_do_criterio`, BN-4: 0,80 em tres
    dias seguidos); os alivios ate o criterio; os acidentes na vida; o cuidado preservado na vida (`cuidado_preservado`); o carinho e o
    limpador por dia (quantos, a solidao media no carinho, o sinal medio: R-3); o peso do alvo por dia (banheiro - aqui); o chegou tarde
    (a fracao das escolhas de `banheiro` que terminam fora, e a distancia media delas)."""
    T = TICKS_POR_DIA
    por_dia = alivios_por_dia(alivios, dias)
    criterio = dia_do_criterio([o["fracao"] for o in por_dia])
    n = sum(o["n"] for o in por_dia)
    urgentes = sum(o["urgentes"] for o in por_dia)

    def diario(itens, campos):
        out = [{"dia": d + 1, "n": 0, **{c: None for c in campos}} for d in range(dias)]
        soma = [[0.0] * len(campos) for _ in range(dias)]
        for item in itens:
            d = item[0] // T
            if not 0 <= d < dias:
                raise ValueError(f"tick {item[0]} fora dos {dias} dias")
            out[d]["n"] += 1
            for i, v in enumerate(item[1:]):
                soma[d][i] += v
        for o, s in zip(out, soma):
            if o["n"]:
                o.update({c: v / o["n"] for c, v in zip(campos, s)})
        return out

    if pesos_alvo is not None and len(pesos_alvo) != dias:
        raise ValueError(f"pesos do alvo: {len(pesos_alvo)} dias, a vida tem {dias}")
    banheiro_escolhido = [(t, dentro, dist) for t, alvo, dentro, dist in escolhas if alvo == "banheiro"]
    tarde = [x for x in banheiro_escolhido if not x[1]]
    return {"por_dia": por_dia, "criterio": criterio, "alivios_ate_criterio": alivios_ate_criterio(por_dia, criterio["dia"]),
            "alivios": n, "acidentes": {"n": urgentes, "fracao": urgentes / n if n else None},
            "cuidado": cuidado_preservado(cuidado, (0, dias * T)) if cuidado else None,
            "carinho": {"n": len(carinhos), "por_dia": diario(carinhos, ("solidao_media", "sinal_medio"))},
            "limpador": {"n": len(limpador), "por_dia": diario(limpador, ("sinal_medio",))},
            "peso_alvo_por_dia": None if pesos_alvo is None else [
                {"banheiro": p["banheiro"], "aqui": p["aqui"], "banheiro_menos_aqui": p["banheiro"] - p["aqui"]} for p in pesos_alvo],
            "chegou_tarde": {"escolhas_banheiro": len(banheiro_escolhido), "fora": len(tarde),
                             "fracao": len(tarde) / len(banheiro_escolhido) if banheiro_escolhido else None,
                             "distancia_media": (sum(d for _, _, d in banheiro_escolhido) / len(banheiro_escolhido)
                                                 if banheiro_escolhido else None)}}


def tabela_banheiro(medidas: dict) -> dict:
    """Por braco do 2 x 2 (o rotulo, P0 ou P1), o descritivo da secao 4: a curva de Kaplan-Meier do dia do criterio (`curva_sobrevivencia`:
    a mediana quando existe, a fracao censurada e a RMST, a media de T*), sobre as vidas daquele braco. Os contrastes pareados (G-CARINHO,
    G-LIMPADOR) sao do orquestrador do plano."""
    por_braco: dict = {}
    for m in medidas.values():
        if m.get("banheiro") is not None and m["origem"] is None:
            por_braco.setdefault(m["braco"], []).append(m["banheiro"]["criterio"])
    return {b: curva_sobrevivencia(cs) for b, cs in sorted(por_braco.items())}


def percepcao_da_sonda(obs, cc: ConfigCorpo, rng: random.Random | None = None, com_mundo: bool = False) -> PercepcaoCorpo:
    """Os receptores de um estado sintetico da sonda (a deriva), com a conta do corpo: cada drive h vira o quimico q = arred((1 - h) C),
    o ponto da grade de C mais perto, e o receptor e S - div_arred(q S, C), como o `Corpo.receptores`. Os receptores novos (a leitura e a
    falta, ou a concentracao na dor e no susto) nao tem drive no vetor da sonda: cada um sai uniforme na grade [0, S] da `rng` (a da sonda,
    derivar_semente("sonda-corpo", semente), um sorteio por receptor na ordem de RECEPTORES_NOVOS), como as outras entradas da sonda saem
    uniformes. Sem `rng`, so a quimica (sem receptores novos); com eles e sem `rng`, falha alto."""
    C, S = cc.escala, cc.escala_receptor
    v = obs.vetor_estado
    leituras = {}
    for i, nome in enumerate(("fome", "higiene", "energia", "humor", "saude")):
        q = arred((1.0 - v[i]) * C)
        leituras[nome] = S - div_arred_corpo(q * S, C)
    novos = receptores_novos_de(cc, com_mundo)
    if novos and rng is None:
        raise ValueError(f"a sonda do corpo com os receptores novos {novos} precisa da rng da sonda")
    for r in novos:
        leituras[r] = rng.randrange(S + 1)
    return PercepcaoCorpo(**leituras)


def do_braco(politica) -> PoliticaDoBraco:
    """A PoliticaDoBraco dentro dos embrulhos dos motores (bola, personalidade)."""
    p = politica
    while not isinstance(p, PoliticaDoBraco):
        if isinstance(p, _Espiao):
            p = p.interna
        elif isinstance(p, _PoliticaComMundo):
            p = p._pm
        elif isinstance(p, _PoliticaComFrutas):
            p = p._pf
        elif isinstance(p, _PoliticaComBola):
            p = p._pb
        elif isinstance(p, _PoliticaObservada):
            p = p._p
        elif isinstance(p, PoliticaComRede):
            p = p._interna
        else:
            raise TypeError(f"politica sem PoliticaDoBraco dentro: {type(p).__name__}")
    return p


class PoliticaComRedeSemOrgaos(PoliticaComRede):
    """A rede da bancada do Digicorpo: a `PoliticaComRede`, que recusa os orgaos do Olfato e da Audicao (#299). Com eles ligados, a rede
    le os receptores de cada narina e ouvido e passa do teto dela (`experiments/custo_orgaos.py`); a bancada do Digicorpo roda sem eles e
    falha alto na primeira decisao que os traz, antes de a rede ver a observacao."""

    def agir(self, obs, rng):
        pc = getattr(obs, "corpo", None)
        ligados = [] if pc is None else [r for r in todos_receptores_orgaos() if getattr(pc, r, None) is not None]
        if ligados:
            raise RuntimeError(f"rede de si com os orgaos ligados ({ligados}): a rede passa do teto; a bancada do Digicorpo roda sem eles")
        return super().agir(obs, rng)


def sondar_quimicos(rede: RedeDeSi, motores: list, saida: list) -> None:
    """Uma sonda so de leitura: antes de cada `observar` da rede, o retrato dos quimicos do corpo do motor (cada um na escala S do teto
    dele, `div_arred(q x S, teto)`, na ordem de `corpo.quimicos`), para o oraculo da bancada. A rede nao ve o retrato (G-RECEPTOR)."""
    observar = rede.observar

    def observar_com_retrato(obs, acao):
        corpo = motores[-1].corpo
        S = rede.S
        saida.append([div_arred(corpo.q[n] * S, corpo.grafo.quimico(n).teto) for n in corpo.quimicos])
        return observar(obs, acao)
    rede.observar = observar_com_retrato


def sonda_ao_nascer(m: dict) -> str:
    """A acao da sonda "ao nascer" do cerebro A (BSS_NASC, R-6): a escolha com os pesos do prior (o lobo de impulsos) e o mesmo u; com um
    candidato so, ele (o legibilidade_a da comparacao dos cerebros)."""
    cands = m["candidatos"]
    if m["u"] is None:
        return cands[0]
    return cands[sortear([m["contribuicoes"]["impulsos"][a] for a in cands], m["u"])]


def _normalizar_cands(pesos: dict, cands: list) -> dict:
    tot = sum(pesos[a] for a in cands)
    return {a: (pesos[a] / tot if tot > 0 else 1.0 / len(cands)) for a in cands}


def rede_offline(cfg: ConfigRedeDeSi, registros: list, receptores: list, extra: list | None = None, congelar_k: int | None = None,
                 autoria: bool = True) -> dict:
    """A rede de si refeita so dos registros dela (as leituras, a acao, o contexto e a faixa de cada decisao), com as mesmas contas
    (`RedeDeSi._saida` e `_lms`) na mesma ordem: em cada decisao k, as previsoes de k - n aprendem com a leitura de k, e a cabeca preve
    k + n. `extra[k]`: entradas a mais em cada decisao, logo depois das leituras (o oraculo: os quimicos na escala S); o prior continua a
    persistencia. `congelar_k`: de k em diante, nada aprende (a rede congelada do G-ADAPTA). So a bancada usa: nunca existe no pet."""
    contas = RedeDeSi(cfg)
    S, hz = contas.S, contas.horizontes
    R = len(registros[0]["leituras"])
    E = len(extra[0]) if extra else 0
    jc = R + E + len(ACOES_REDE) + len(CONTEXTO_REDE) + 1
    prior = {str(n): [[S if j == i else 0 for j in range(jc)] for i in range(R)] for n in hz}
    pesos = {n: [list(w) for w in t] for n, t in prior.items()}
    F = len(cfg.faixas_idade) + 1
    vies = div_arred(S, len(ACOES_REDE))
    prior_a = {a.value: [0] * (R + len(CONTEXTO_REDE) + F) + [vies] for a in ACOES_REDE}
    pesos_a = {a: list(w) for a, w in prior_a.items()}
    pend: dict = {str(n): [] for n in hz}
    prev: dict = {str(n): [] for n in hz}
    q_out, por_dia = [], []
    passo_dia = TICKS_POR_DIA // CONFIG_PADRAO.intervalo_decisao_ticks
    for k, reg in enumerate(registros):
        ls, ctx = reg["leituras"], reg["contexto"]
        aprende = congelar_k is None or k < congelar_k
        for n in hz:
            if k - n >= 0:
                x, p = pend[str(n)][k - n]
                if aprende:
                    for i in range(R):
                        contas._lms(pesos[str(n)][i], prior[str(n)][i], x, ls[i] - p[i])
        if autoria:
            y = ls + ctx + [S if f == reg["faixa"] else 0 for f in range(F)] + [S]
            q = [contas._saida(pesos_a[a.value], y) for a in ACOES_REDE]
            q_out.append(q)
            if aprende:
                for a, qa in zip(ACOES_REDE, q):
                    contas._lms(pesos_a[a.value], prior_a[a.value], y, (S if a.value == reg["acao"] else 0) - qa)
        x = ls + (list(extra[k]) if extra else []) + [S if a.value == reg["acao"] else 0 for a in ACOES_REDE] + ctx + [S]
        for n in hz:
            p = [contas._saida(pesos[str(n)][i], x) for i in range(R)]
            pend[str(n)].append((x, p))
            prev[str(n)].append(p)
        if (k + 1) % passo_dia == 0 or k == len(registros) - 1:
            por_dia.append({"k": k, "corpo": _resumo_pesos([w for t in pesos.values() for w in t],
                                                           [w for t in prior.values() for w in t], cfg.teto),
                            "autoria": _resumo_pesos(list(pesos_a.values()), list(prior_a.values()), cfg.teto) if autoria else None})
    return {"corpo": prev, "autoria": q_out if autoria else None,
            "pesos_corpo": {n: dict(zip(receptores, t)) for n, t in pesos.items()} if not E else None,
            "pesos_autoria": pesos_a if autoria else None, "pesos_por_dia": por_dia}



def _resumo_pesos(pesos: list, prior: list, teto: int) -> dict:
    """Os pesos de uma cabeca num momento: quantos no teto (|w - w0| = teto) e o desvio medio |w - w0|."""
    desv = [abs(w - w0) for linha, linha0 in zip(pesos, prior) for w, w0 in zip(linha, linha0)]
    return {"no_teto": sum(1 for d in desv if d >= teto), "desvio_medio": sum(desv) / len(desv), "pesos": len(desv)}


def rede_de(politica) -> PoliticaComRede:
    """O embrulho da rede de si dentro dos embrulhos dos motores e do registro de medicao (falha alto sem ela)."""
    p = politica
    while not isinstance(p, PoliticaComRede):
        if isinstance(p, (_Espiao, _Registro)):
            p = p.interna
        elif isinstance(p, _PoliticaComMundo):
            p = p._pm
        elif isinstance(p, _PoliticaComFrutas):
            p = p._pf
        elif isinstance(p, _PoliticaComBola):
            p = p._pb
        elif isinstance(p, _PoliticaObservada):
            p = p._p
        else:
            raise TypeError(f"politica sem a rede de si dentro: {type(p).__name__}")
    return p


def _estado_rede(motor) -> str:
    return json.dumps(rede_de(motor.politica).rede.estado(), sort_keys=True)


def tabelas_braco_condicao(medidas: dict, boot: dict) -> dict:
    """Por dono e medida: tabela braco x condicao, unidade = vida (semente x genoma). A coluna e "condicao/mundo"
    ("casado/padrao", "casado/casado_frutas", "descasado/descasado", "mutavel/mutavel"...): dois mundos da mesma condicao nunca se
    misturam numa celula. Nos mundos das frutas, tambem as medidas do N5 (MEDIDAS_FRUTAS: a taxa da fruta ruim no inicio e no final
    e os consumos ate a metade do caminho), pela tabela parcial, que conta as vidas sem valor em vez de sumir com elas."""
    out = {}
    for dono in sorted({m["dono"] for m in medidas.values()}):
        out[dono] = {}
        for medida in MEDIDAS_TABELA:
            valores: dict[tuple[str, str], list[float]] = {}
            for m in medidas.values():
                if m["dono"] == dono:
                    valores.setdefault((m["braco"], _coluna(m)), []).append(m[medida])
            out[dono][medida] = tabela_braco_condicao(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
        # as medidas do N5 (plano, secao 5), so nos mundos das frutas: podem faltar numa vida (janela sem consumo, P0 sem consumo)
        frutas = [m for m in medidas.values() if m["dono"] == dono and m["frutas"] is not None]
        if frutas:
            for medida, f in MEDIDAS_FRUTAS.items():
                valores = {}
                for m in frutas:
                    valores.setdefault((m["braco"], _coluna(m)), []).append(f(m["frutas"]))
                out[dono][medida] = tabela_braco_condicao_parcial(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
        # as medidas do mundo fisico (PLANO_ANALISE_V2_MUNDO_FISICO, secao 5), com a coluna por lugar
        fisicas = [m for m in medidas.values() if m["dono"] == dono and m.get("mundo_fisico") is not None]
        if fisicas:
            for medida, f in MEDIDAS_MUNDO.items():
                valores = {}
                for m in fisicas:
                    valores.setdefault((m["braco"], _coluna(m)), []).append(f(m["mundo_fisico"]))
                out[dono][medida] = tabela_braco_condicao_parcial(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
    return out


def tabela_dominancia(medidas: dict) -> dict:
    """Adendo 2 do plano do corpo (A2.2, A2.3, A2.6), na janela: por braco x condicao/mundo x tipo de decisao (tempo livre e o resto),
    f_d por unidade (as celulas da unidade somadas: os donos e, no mundo fisico, os lugares; f_d = lideradas / decisoes com sinal), a
    leitura (metrics.leitura_dominancia: o IC95 de f_d por bootstrap sobre as unidades, 10.000 reamostragens, semente 4242; "domina"
    com o limite inferior acima de 0,50), a parcela agregada soma|c_d| / soma soma|c| e a contribuicao com sinal. Regra de leitura,
    fora do Holm. `origem`: "sinal" nos bracos que aprendem pela consequencia, "sonda" nos outros (o P0)."""
    grupos: dict = {}
    for m in medidas.values():
        dom = m.get("dominancia")
        if dom is None:
            continue
        g = grupos.setdefault((m["braco"], f"{m['condicao']}/{m['mundo']}"), {"origem": dom["origem"], "unidades": {}})
        if g["origem"] != dom["origem"]:
            raise RuntimeError(f"{m['vida']}: origem da dominancia diferente no mesmo braco")
        u = g["unidades"].setdefault((m["genoma"], m["semente"]), {})
        for tipo, r in dom["na_janela"].items():
            t = u.setdefault(tipo, {"n": 0, "lideradas": {}, "soma_abs": {}, "contribuicao": {}})
            t["n"] += r["n"]
            for chave in ("lideradas", "soma_abs", "contribuicao"):
                for d, v in r[chave].items():
                    t[chave][d] = t[chave].get(d, 0) + v
    out: dict = {}
    for (braco, coluna), g in sorted(grupos.items()):
        cel = out.setdefault(braco, {}).setdefault(coluna, {"origem": g["origem"], "unidades": len(g["unidades"])})
        for tipo in ("tempo_livre", "resto"):
            us = [u[tipo] for _, u in sorted(g["unidades"].items(), key=lambda x: (str(x[0][0]), x[0][1])) if tipo in u]
            drives = sorted({d for u in us for d in u["lideradas"]})
            f = {d: [(u["lideradas"].get(d, 0) / u["n"]) if u["n"] else None for u in us] for d in drives}
            soma = {d: sum(u["soma_abs"].get(d, 0) for u in us) for d in drives}
            total = sum(soma.values())
            cel[tipo] = {"decisoes": sum(u["n"] for u in us), "f_por_unidade": f, "leitura": leitura_dominancia(f),
                         "parcela": {d: (soma[d] / total) if total else None for d in drives},
                         "contribuicao": {d: sum(u["contribuicao"].get(d, 0) for u in us) for d in drives}}
    return out


def _coluna(m: dict) -> str:
    """A coluna da tabela: "condicao/mundo", e no mundo fisico "condicao/mundo/lugar" (o lugar e parte da celula, PMF-4)."""
    base = f"{m['condicao']}/{m['mundo']}"
    return base if m.get("lugar") is None else f"{base}/{m['lugar']}"


MEDIDAS_FRUTAS = {
    "taxa_fruta_ruim_inicio": lambda f: f["taxa_fruta_ruim"]["inicio"]["taxa"],
    "taxa_fruta_ruim_final": lambda f: f["taxa_fruta_ruim"]["final"]["taxa"],
    "consumos_ate_metade": lambda f: f["consumos_ate_metade"]["consumos"],
}
MEDIDAS_MUNDO = {
    "d_fe": lambda f: f["d_fe"]["d_fe"],
    "privacao_janela": lambda f: f["cuidado"]["privacao"],
    "permanencia_media": lambda f: f["permanencia_media"],
}


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .bracos import PoliticaDoBraco  # noqa: E402
from .regras_mundo import _Espiao, _Registro  # noqa: E402
