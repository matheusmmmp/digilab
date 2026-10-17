"""Protótipo: o cérebro A desenhado como um connectome (docs/futuro/connectome_cerebro_a.md, status PROPOSTO).

Não é uma rede de neurônios. É a tabela de pesos inteiros w[regra][acao][entrada] da PoliticaLobos (digilab/policies/lobos.py), com as
tabelas vizinhas (o alvo aprendido por classe, a presença da fruta, as entradas sociais e as do corpo), desenhada como grafo: os nós são
as entradas da percepção, as regras do lobo impulsos, as ações candidatas e as classes de alvo; cada aresta é um peso. A atividade de
cada decisão vem do motivo dela (`estado_interno()["motivos"]`).

O que o script faz:
  1. vive uma vida de TESTE (semente 101, 202, 303, 404 ou 505; nunca uma faixa de pesquisa) pela bancada, que já confere o replay;
  2. grava o log no disco e o rejoga do texto do disco, com um gravador que lê os pesos do cérebro antes de cada decisão (só lê: não
     consome rng nem muda estado; a vida rejogada é conferida bit a bit contra a vida);
  3. confere os pesos gravados contra o motivo de cada decisão (o termo aprendido do motivo tem de ser o (w - w0) x / S gravado) e contra
     o estado interno final;
  4. escreve `dados.json`, `contagem.json` (o tamanho real do grafo) e `connectome.html` (d3 de CDN, versão fixa).

Uso:
    python tools/connectome_cerebro_a.py --vida pqp --semente 101 --saida artifacts_connectome/pqp-101
    python tools/connectome_cerebro_a.py --vida dois_pets --semente 101 --saida artifacts_connectome/dois_pets-101

Fora do pacote digilab/ e só biblioteca padrão. Não muda engine.py, a política nem o jogo web.
"""
from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.events import FRUTAS, LogDeEventos  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import ENTRADAS_SOCIAIS, LOBO_PLANEJAMENTO, LOBOS_TODOS  # noqa: E402

SEMENTES_TESTE = (101, 202, 303, 404, 505)
VIDAS = ("pqp", "dois_pets")
CONFIG_PQP = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca_calibracao_paladar.json"
CONFIG_DOIS_PETS = RAIZ / "experiments" / "configs" / "v2_dois_pets" / "calibracao.json"
# a vida do J5 de exemplo: os números calibrados do adendo 3 (docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md: ganho_gosto S/2,
# g_plano S), o braço com o planejador para o lobo planejamento aparecer, o T1 com os dias do plano (D_a 7, janela 3)
PQP_PADRAO = {"braco": "P1-plan", "protocolo": "T1", "d_a": 7, "janela": 3, "g_plano": 1024, "ganho_gosto": 512}
# a vida dos dois pets de exemplo: o B com o A informativo, o B entra no dia K = 2 e a vida tem 4 dias
DOIS_PETS_PADRAO = {"braco": "B+Ainf", "k_dias": 2, "dias": 4, "pet": "B"}
D3_CDN = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"
# os nomes dos estágios na tela (lobos.LOBOS_TODOS na ordem); o rótulo é só de tela
ROTULO_LOBO = {"percepcao": "percepção", "memoria_emocao": "memória/emoção", "impulsos": "impulsos", "decisao": "decisão",
               "planejamento": "planejamento"}
RECEPTORES_DE_HOJE = ("fome", "higiene", "energia", "humor", "saude")


# ------------------------------------------------------------------ o gravador dos pesos


def achatar_pesos(c: PoliticaLobos) -> dict[str, int]:
    """Todo peso do cérebro, numa chave por aresta. Tipos: t (a tabela da decisão, regra|acao|entrada), c (as entradas novas do corpo),
    s (as entradas sociais), m (o alvo aprendido, regra:acao|classe), f (a presença da fruta em comer). Uma tabela que o protótipo não
    desenha falha alto, para nenhum peso ficar fora do grafo em silêncio."""
    if c._pesos_fruta or c._peso_info is not None or c._peso_pedido is not None or c._pesos_alvo or c._memoria is not None:
        raise NotImplementedError("o protótipo não desenha a sub-decisão da fruta, a informação, o pedido, o alvo do banheiro nem a N6")
    d: dict[str, int] = {}
    for r, acoes in c._pesos.items():
        for a, ws in acoes.items():
            for e, w in zip(c.entradas, ws):
                d[f"t|{r}|{a.value}|{e}"] = w
    for r, acoes in c._pesos_corpo.items():
        for a, ws in acoes.items():
            for e, w in zip(c._receptores_novos, ws):
                d[f"c|{r}|{a.value}|{e}"] = w
    for r, acoes in c._pesos_social.items():
        for a, ws in acoes.items():
            for e, w in zip(ENTRADAS_SOCIAIS, ws):
                d[f"s|{r}|{a.value}|{e}"] = w
    for k, tabela in c._pesos_alvo_mundo.items():
        for cl, w in tabela.items():
            d[f"m|{k}|{cl}"] = w
    for f, w in c._pesos_comer_fruta.items():
        d[f"f|{f}"] = w
    if len(d) != c.n_pesos():
        raise RuntimeError(f"achatei {len(d)} pesos, o cérebro tem {c.n_pesos()}")
    return d


def achatar_prior(c: PoliticaLobos) -> dict[str, int]:
    """O mesmo achatamento sobre o prior (w0). O prior das entradas do corpo só existe com o banheiro; sem ele é 0 (lobos.py)."""
    salvo = (c._pesos, c._pesos_corpo, c._pesos_social, c._pesos_alvo_mundo, c._pesos_comer_fruta)
    try:
        c._pesos = c._prior
        c._pesos_corpo = c._prior_corpo
        c._pesos_social = c._prior_social
        c._pesos_alvo_mundo = c._prior_alvo_mundo
        c._pesos_comer_fruta = c._prior_comer_fruta
        return achatar_pesos(c)
    finally:
        c._pesos, c._pesos_corpo, c._pesos_social, c._pesos_alvo_mundo, c._pesos_comer_fruta = salvo


class Gravador:
    """Os pesos de um cérebro antes de cada decisão, em mudanças esparsas, e o que o motivo não guarda (a presença da fruta e a hora)."""

    def __init__(self, c: PoliticaLobos) -> None:
        self.cerebro = c
        self.prior = achatar_prior(c)
        self.inicial = achatar_pesos(c)
        self._ultimo = dict(self.inicial)
        self.mudancas: list[list] = []     # por decisão: [[chave, w], ...] desde a decisão anterior
        self.extras: list[dict] = []       # por decisão: presença da fruta, hora do dia, dia

    def antes(self) -> None:
        agora = achatar_pesos(self.cerebro)
        self.mudancas.append([[k, w] for k, w in agora.items() if self._ultimo[k] != w])
        self._ultimo = agora

    def depois(self, obs) -> None:
        hora = obs.vetor_estado[7]
        dia = 0
        if self.extras:
            anterior = self.extras[-1]
            dia = anterior["dia"] + (1 if hora < anterior["hora"] else 0)
        self.extras.append({"hora": hora, "dia": dia, "presenca": list(self.cerebro._presenca_na_decisao or ())})


@contextmanager
def gravando():
    """Embrulha PoliticaLobos.agir enquanto dura o bloco: um Gravador por instância que decide. Só lê."""
    gravadores: list[Gravador] = []
    por_id: dict[int, Gravador] = {}
    original = PoliticaLobos.agir

    def agir(self, obs, rng):
        g = por_id.get(id(self))
        if g is None:
            g = por_id[id(self)] = Gravador(self)
            gravadores.append(g)
        g.antes()
        acao = original(self, obs, rng)
        g.depois(obs)
        return acao

    PoliticaLobos.agir = agir
    try:
        yield gravadores
    finally:
        PoliticaLobos.agir = original


def cerebro_de(politica) -> PoliticaLobos:
    """A PoliticaLobos dentro dos embrulhos do motor e da bancada."""
    from experiments.bancada.medidas import do_braco
    c = do_braco(politica).cerebro
    while not isinstance(c, PoliticaLobos):
        c = c._interna
    return c


# ------------------------------------------------------------------ as vidas de teste


def _conferir_semente(semente: int) -> None:
    from experiments.bancada.faixas import na_faixa_reservada
    if semente not in SEMENTES_TESTE:
        raise ValueError(f"semente {semente}: o protótipo só usa as sementes dos testes {SEMENTES_TESTE}")
    faixa = na_faixa_reservada(semente)
    if faixa is None or not faixa.startswith("testes"):
        raise ValueError(f"semente {semente}: a tabela das faixas não a dá como dos testes ({faixa})")


def vida_pqp(semente: int, pasta: Path) -> tuple[PoliticaLobos, Gravador, dict]:
    from experiments import bancada_v2 as bv
    from experiments.bancada.vida import _interno, resumo_motor
    p = PQP_PADRAO
    cfg = json.loads(CONFIG_PQP.read_text(encoding="utf-8"))
    for k in ("calibracao_ganho_gosto", "calibracao_g_plano"):
        cfg.pop(k)
    cfg.update({"bracos": [p["braco"]], "protocolos": [p["protocolo"]], "d_a": p["d_a"], "janela": p["janela"], "g_plano": p["g_plano"],
                "sementes": [semente]})
    cfg["consequencia"] = {**cfg["consequencia"], "ganho_gosto": p["ganho_gosto"]}
    bp = bv.bancada_pqp_da_config(cfg)
    espec = bv.EspecPQP(p["braco"], p["protocolo"], semente)
    vida = bp.vida(espec)                                   # já confere o replay (G1)
    arquivo = pasta / "log.jsonl"
    arquivo.write_text(vida.motor.log.para_jsonl(), encoding="utf-8")
    with gravando() as gravadores:
        motor = bp.rejogar(LogDeEventos.de_jsonl(arquivo.read_text(encoding="utf-8")), espec)
    if resumo_motor(motor) != resumo_motor(vida.motor) or _interno(motor) != _interno(vida.motor):
        raise RuntimeError(f"{espec.nome}: o replay gravado diverge da vida")
    c = cerebro_de(motor.politica)
    g = _gravador_de(gravadores, c)
    meta = {"vida": "pqp", "semente": semente, "nome": espec.nome, "dias": p["d_a"] + p["janela"], "config": str(CONFIG_PQP.relative_to(RAIZ)),
            "troca": {k: v for k, v in p.items()}, "x": vida.x, "tick_mudanca": vida.tick_mudanca, "pet": "A",
            "corpo": contar_corpo(motor.corpo.grafo)}
    return c, g, meta


def vida_dois_pets(semente: int, pasta: Path) -> tuple[PoliticaLobos, Gravador, dict]:
    from experiments.bancada.config import bancada_da_config
    from experiments.bancada.grupo import EspecGrupo, _resumo_grupo, validar_config_grupo
    from digilab.grupo import RegistroGrupo
    p = DOIS_PETS_PADRAO
    cfg = json.loads(CONFIG_DOIS_PETS.read_text(encoding="utf-8"))
    for k in ("calibracao_k", "piloto", "taxa", "margem", "poder", "unidades", "plano", "adendo_janelas", "bootstrap"):
        cfg.pop(k, None)
    cfg.update({"tipo": "grupo", "bracos": [p["braco"]], "sementes": [semente], "k_dias": p["k_dias"], "dias": p["dias"]})
    validar_config_grupo(cfg)
    chaves = {k: v for k, v in cfg.items() if k in ("consequencia", "lobos", "ponto", "montagem", "mundo", "teto_pesos")}
    bancada = bancada_da_config({**chaves, "dias": p["dias"], "orcamento": int(cfg["orcamento_por_dia"]) * p["dias"]})
    eg = EspecGrupo(p["braco"], semente, p["k_dias"], cfg["dono"], cfg["lugar"])
    vida = bancada.grupo(eg)                                # já confere o replay do grupo (G1)
    arquivo = pasta / "registro.jsonl"
    arquivo.write_text(vida.grupo.registro.para_jsonl(), encoding="utf-8")
    with gravando() as gravadores:
        g_rej = bancada.rejogar_grupo(RegistroGrupo.de_jsonl(arquivo.read_text(encoding="utf-8")), eg)
    if _resumo_grupo(g_rej) != _resumo_grupo(vida.grupo):
        raise RuntimeError(f"{eg.nome}: o replay gravado diverge do grupo")
    c = cerebro_de(g_rej.motores[p["pet"]].politica)
    g = _gravador_de(gravadores, c)
    meta = {"vida": "dois_pets", "semente": semente, "nome": eg.nome, "dias": p["dias"], "config": str(CONFIG_DOIS_PETS.relative_to(RAIZ)),
            "troca": dict(p), "pet": p["pet"]}
    return c, g, meta


def _gravador_de(gravadores: list[Gravador], c: PoliticaLobos) -> Gravador:
    achados = [g for g in gravadores if g.cerebro is c]
    if len(achados) != 1:
        raise RuntimeError(f"{len(achados)} gravadores para o cérebro do pet (esperado 1)")
    g = achados[0]
    if len(g.mudancas) != len(c.motivos):
        raise RuntimeError(f"{len(g.mudancas)} decisões gravadas, {len(c.motivos)} motivos")
    return g


# ------------------------------------------------------------------ conferências e dados


def pesos_por_decisao(g: Gravador):
    """Os pesos no momento de cada decisão (antes dela), um dicionário por decisão, em ordem (gerador)."""
    w = dict(g.inicial)
    for mud in g.mudancas:
        for k, v in mud:
            w[k] = v
        yield w


def conferir(c: PoliticaLobos, g: Gravador) -> None:
    """Falha alto se o gravado não fecha com o cérebro: o fim com o estado interno, e o termo aprendido de cada motivo com (w - w0) x / S."""
    S = c._escala
    # o fim: o crédito da última decisão chega depois dela, então o fim é o cérebro de agora, achatado, contra o estado interno público
    agora = achatar_pesos(c)
    ei = c.estado_interno()
    for r, acoes in ei["pesos"].items():
        for a, ws in acoes.items():
            for e, w in zip(ei["entradas"], ws):
                if agora[f"t|{r}|{a}|{e}"] != w:
                    raise RuntimeError(f"peso {r}|{a}|{e}: achatado {agora[f't|{r}|{a}|{e}']}, estado interno {w}")
    for k, t in ei.get("pesos_alvo_mundo", {}).items():
        for cl, w in t.items():
            if agora[f"m|{k}|{cl}"] != w:
                raise RuntimeError(f"alvo {k}|{cl}: achatado {agora[f'm|{k}|{cl}']}, estado interno {w}")
    for n, (w, m) in enumerate(zip(pesos_por_decisao(g), c.motivos)):
        if m["aprendido"] is None:
            continue
        x = [m["percepcao"][e] for e in c.entradas]
        for a, termos in m["aprendido"].items():
            for e, xj, t in zip(c.entradas, x, termos):
                k = f"t|{m['regra']}|{a}|{e}"
                if (w[k] - g.prior[k]) / S * xj != t:
                    raise RuntimeError(f"decisão {n}: o termo aprendido de {k} no motivo ({t}) não é (w - w0) x / S gravado")


def montar_dados(c: PoliticaLobos, g: Gravador, meta: dict) -> dict:
    S = c._escala
    ei = c.estado_interno()
    final = achatar_pesos(c)
    chaves = sorted(final)
    indice = {k: i for i, k in enumerate(chaves)}
    # nós
    nos: list[dict] = []

    def no(ident, rotulo, grupo, lobo, sub=""):
        nos.append({"id": ident, "rotulo": rotulo, "grupo": grupo, "lobo": lobo, "sub": sub})

    for e in c.entradas:
        sub = "receptor" if e in RECEPTORES_DE_HOJE else ("mundo" if e in ("bola", "fruta") else "estado")
        no(f"e:{e}", e, "entrada", "percepcao", sub)
    for e in c._receptores_novos:
        no(f"e:{e}", e, "entrada", "percepcao", "corpo")
    if c._pesos_social:
        for e in ENTRADAS_SOCIAIS:
            no(f"e:{e}", e, "entrada", "percepcao", "social")
    if c._pesos_comer_fruta:
        for f in FRUTAS:
            no(f"e:presenca_{f}", f"fruta {f} à vista", "entrada", "percepcao", "presenca")
    for r in c._pesos:
        no(f"r:{r}", r, "regra", "impulsos")
    acoes = []
    for acoes_r in c._pesos.values():
        for a in acoes_r:
            if a.value not in acoes:
                acoes.append(a.value)
    for a in acoes:
        no(f"a:{a}", a, "acao", "decisao")
    classes = []
    for t in c._pesos_alvo_mundo.values():
        for cl in t:
            if cl not in classes:
                classes.append(cl)
    for cl in classes:
        no(f"k:{cl}", cl, "classe", "decisao")
    no("l:memoria_emocao", "memória/emoção", "lobo", "memoria_emocao")
    tem_plano = c._modelo_mundo is not None
    if tem_plano:
        no("l:planejamento", "plano (modelos do mundo)", "lobo", "planejamento")
    # arestas (uma por peso)
    arestas = []
    for k in chaves:
        partes = k.split("|")
        tipo = partes[0]
        if tipo in ("t", "c", "s"):
            _, r, a, e = partes
            arestas.append({"k": k, "tipo": tipo, "de": f"e:{e}", "via": f"r:{r}", "para": f"a:{a}", "regra": r, "acao": a, "entrada": e})
        elif tipo == "m":
            _, chave, cl = partes
            r, a = chave.split(":")
            arestas.append({"k": k, "tipo": tipo, "de": f"a:{a}", "via": None, "para": f"k:{cl}", "regra": r, "acao": a, "classe": cl})
        elif tipo == "f":
            arestas.append({"k": k, "tipo": tipo, "de": f"e:presenca_{partes[1]}", "via": None, "para": "a:comer", "fruta": partes[1]})
        else:
            raise RuntimeError(f"tipo de aresta {tipo!r}")
        arestas[-1]["w0"] = g.prior[k]
        arestas[-1]["w0_ini"] = g.inicial[k]
    # decisões (o motivo, enxuto) e as mudanças de peso por índice
    decisoes = []
    for m, mud, ex in zip(c.motivos, g.mudancas, g.extras):
        d = {"n": m["n"], "regra": m["regra"], "cands": m["candidatos"], "acao": m["acao"], "decisivo": m["lobo_decisivo"],
             "contrib": m["contribuicoes"], "pesos": m["pesos"], "u": m["u"],
             "x": [m["percepcao"][e] for e in c.entradas], "dia": ex["dia"], "hora": ex["hora"], "pres": ex["presenca"],
             "mud": [[indice[k], w] for k, w in mud]}
        if "percepcao_corpo" in m:
            d["xc"] = [m["percepcao_corpo"][e] for e in c._receptores_novos]
        if "percepcao_social" in m:
            d["xs"] = [m["percepcao_social"][e] for e in ENTRADAS_SOCIAIS]
        if "alvo_aprendido" in m:
            d["alvo"] = m["alvo_aprendido"]
        if "alvo_plano" in m:
            d["alvo_plano"] = {"alvo": m["alvo_plano"]["alvo"], "termos": m["alvo_plano"]["termos"],
                               "decidiu": m["alvo_plano"]["plano_decidiu"]}
        if "plano" in m:
            d["plano"] = {"V": m["plano"]["V"], "decidiu": m["plano"]["plano_decidiu"]}
        if "sinal_corpo" in m:
            d["sinal"] = m["sinal_corpo"]["f"]
        decisoes.append(d)
    contagem = contar(c, g, nos, arestas)
    return {"meta": {**meta, "escala": S, "teto": c.cl.teto, "g_plano": c.cl.g_plano, "lobos": list(LOBOS_TODOS if tem_plano else LOBOS_TODOS[:4]),
                     "rotulo_lobo": ROTULO_LOBO, "entradas": list(c.entradas), "receptores_novos": list(c._receptores_novos),
                     "sociais": list(ENTRADAS_SOCIAIS) if c._pesos_social else [], "n_decisoes": len(decisoes)},
            "nos": nos, "arestas": arestas, "final": [final[k] for k in chaves], "decisoes": decisoes, "contagem": contagem}


def contar(c: PoliticaLobos, g: Gravador, nos: list, arestas: list) -> dict:
    """O tamanho real do grafo: nós por grupo; pesos (arestas possíveis), não nulos no prior, no fim e em algum momento da vida; pesos que
    o aprendizado mexeu; arestas que acenderam (termo != 0) em alguma decisão."""
    final = achatar_pesos(c)
    algum = {k for k, w in g.inicial.items() if w != 0}
    for mud in g.mudancas:
        algum.update(k for k, w in mud if w != 0)
    algum.update(k for k, w in final.items() if w != 0)
    por_tipo: dict = {}
    for a in arestas:
        t = por_tipo.setdefault(a["tipo"], {"pesos": 0, "nao_nulos_prior": 0, "nao_nulos_fim": 0, "nao_nulos_na_vida": 0, "aprendidos_fim": 0})
        k = a["k"]
        t["pesos"] += 1
        t["nao_nulos_prior"] += g.prior[k] != 0
        t["nao_nulos_fim"] += final[k] != 0
        t["nao_nulos_na_vida"] += k in algum
        t["aprendidos_fim"] += final[k] != g.prior[k]
    total = {campo: sum(t[campo] for t in por_tipo.values()) for campo in next(iter(por_tipo.values()))}
    # acesas: termo w x / S != 0 numa decisão, nas arestas da tabela da decisão da regra que disparou, entre os candidatos
    acesas = set()
    pos = {e: j for j, e in enumerate(c.entradas)}
    for w, m in zip(pesos_por_decisao(g), c.motivos):
        for a in m["candidatos"]:
            for e, j in pos.items():
                k = f"t|{m['regra']}|{a}|{e}"
                if w[k] != 0 and m["percepcao"][e] != 0:
                    acesas.add(k)
    grupos: dict = {}
    for n in nos:
        chave = n["grupo"] + (f":{n['sub']}" if n["sub"] else "")
        grupos[chave] = grupos.get(chave, 0) + 1
    return {"nos": len(nos), "nos_por_grupo": grupos, "pesos_por_tipo": por_tipo, "pesos_total": total,
            "n_pesos_do_cerebro": c.n_pesos(), "arestas_t_acesas_na_vida": len(acesas), "decisoes": len(c.motivos),
            "comparacao_flywire": {"neuronios": "cerca de 139 mil", "sinapses": "54,5 milhões",
                                   "fonte": "Dorkenwald et al. 2024, 10.1038/s41586-024-07558-y (CORPUS; docs/research/digibrain/sources/drosophila.md)"}}


def contar_corpo(grafo) -> dict:
    """O tamanho do grafo do corpo químico da vida (corpo_grafo.Grafo, o do motor): nós (químicos, reações, emissores, órgãos) e arestas
    (efeito emissor -> químico, leitura químico -> emissor, consumo e produção das reações, receptor químico -> cérebro)."""
    return {"quimicos": len(grafo.quimicos), "quimicos_com_receptor": sum(q.receptor is not None for q in grafo.quimicos),
            "receptores": sorted(q.receptor for q in grafo.quimicos if q.receptor is not None),
            "reacoes": len(grafo.reacoes), "emissores": len(grafo.emissores), "orgaos": len(grafo.orgaos),
            "arestas_efeito": sum(len(e.efeitos) for e in grafo.emissores if e.destino == "corpo"),
            "arestas_leitura": sum(len(e.le) for e in grafo.emissores),
            "arestas_reacao": sum(len(r.consome) + len(r.produz) for r in grafo.reacoes)}


# ------------------------------------------------------------------ o HTML


def escrever_html(dados: dict, destino: Path) -> None:
    modelo = (Path(__file__).with_name("connectome_cerebro_a.html")).read_text(encoding="utf-8")
    js = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = modelo.replace("__D3_CDN__", D3_CDN).replace("__DADOS__", js)
    if "__DADOS__" in html or "__D3_CDN__" in html:
        raise RuntimeError("o modelo do HTML ficou com marcador")
    destino.write_text(html, encoding="utf-8")


def principal(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vida", choices=VIDAS, default="pqp")
    ap.add_argument("--semente", type=int, default=101)
    ap.add_argument("--saida", type=Path, default=None)
    args = ap.parse_args(argv)
    _conferir_semente(args.semente)
    pasta = args.saida or RAIZ / "artifacts_connectome" / f"{args.vida}-{args.semente}"
    pasta.mkdir(parents=True, exist_ok=True)
    c, g, meta = (vida_pqp if args.vida == "pqp" else vida_dois_pets)(args.semente, pasta)
    conferir(c, g)
    dados = montar_dados(c, g, meta)
    (pasta / "dados.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    (pasta / "contagem.json").write_text(json.dumps({"meta": dados["meta"] | {"rotulo_lobo": None}, **dados["contagem"]}, ensure_ascii=False,
                                                    indent=2), encoding="utf-8")
    escrever_html(dados, pasta / "connectome.html")
    print(f"{meta['nome']}: {dados['contagem']['nos']} nós, {dados['contagem']['pesos_total']['nao_nulos_fim']} pesos não nulos no fim "
          f"(de {dados['contagem']['n_pesos_do_cerebro']}), {len(dados['decisoes'])} decisões -> {pasta / 'connectome.html'}")
    return dados


if __name__ == "__main__":
    principal()
