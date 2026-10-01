"""Diagnostico do vinculo (docs/TAREFA_V2_F0_VINCULO.md, fase 0 da V2): por que o vinculo premia o dono aleatorio?

    python experiments/analisar_vinculo.py [--e1 <pasta de vidas do E1>] [--processos N] [--so-personalidade]

Nenhuma vida nova, nenhuma semente nova, nenhuma mecanica nova e nada muda em digilab/. O script reproduz vidas ja
gravadas e so observa o vinculo:
  - as 40 vidas de artifacts_v1_personalidade/completa/vidas (10 ovos x 4 donos, 14 dias, 224 interacoes; protocolo
    arena-v1-personalidade), conferidas contra o vinculo_final do .personalidade.json de cada uma;
  - as 640 vidas arquivadas do E1 (rodada especie_fixa: 40 genomas x 4 donos x 4 ambientes, educacao-v1 ligada),
    conferidas contra o pets.json do E1 (as mesmas que experiments/sinal_dono.py reproduz).
Replay que nao bate com o artefato levanta erro.

Em cada vida o Vinculo e trocado por uma subclasse que anota cada atualizacao (componente, amostra, peso, se foi um
pedido atendido ou perdido) sem mudar o valor, e o motor ganha um gancho de leitura do estado depois de cada avanco. Com
isso saem, por dono: quantas amostras cada componente deu, a amostra media, o empurrao liquido de cada componente, as
acoes do dono por tipo, e contrafactuais recalculados sobre o MESMO fluxo de amostras (so atendimento, so coerencia,
sem atendimento, normalizado pela media do aleatorio, coerencia por contexto). Os contrafactuais fixam os eventos da
vida: na vida real o vinculo entra na obediencia, entao um vinculo diferente mudaria um pouco a vida. Sao uma conta
sobre o que foi gravado, nao uma run.

Saida: artifacts_v2_vinculo/resultado.json (agregados) e artifacts_v2_vinculo/por_pet.json (uma linha por vida).
Descritivo: nenhum gate, nenhum IC novo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import CONFIG_MEMORIA_ESPACOS, CONFIG_PADRAO, CONFIG_VINCULO  # noqa: E402
from digilab.educacao import reproduzir_educacao  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLOS, hash_parametros_educacao, sha256_engine  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.vinculo import Vinculo  # noqa: E402
from run_arena import fabricas_vida  # noqa: E402
from run_educacao import _fabricas  # noqa: E402
from run_natureza_criacao import chave, genoma  # noqa: E402

PERSONALIDADE = RAIZ / "artifacts_v1_personalidade" / "completa"
E1 = RAIZ / "artifacts_linhagem" / "natureza_criacao" / "especie_fixa"
VIDAS_E1 = Path("D:/Trab/digilab/arquivo/artifacts_linhagem_E1_vidas/natureza_criacao/especie_fixa/vidas")
CFG_E1 = RAIZ / "experiments" / "configs" / "linhagem" / "natureza_criacao.json"
SAIDA = RAIZ / "artifacts_v2_vinculo"

CUIDADOS = ("alimentar", "limpar", "brincar", "acariciar", "petisco", "levar_ao_banheiro", "tratar_lesao")
FEEDBACK = ("elogiar", "repreender")
COMPONENTES = ("atendimento", "coerencia", "desejo", "pausa")
# contexto do pet para a coerencia contextual (contrafactual): so limiares que o PROPRIO pet ja usa, nenhum do dono.
# necessidade baixa = o limiar do pedido (ConfigMemoriaEspacos.limiar_necessidade_pedido); cansado = a regra do instinto
# "energia < 0,25 -> dormir" (PoliticaInstinto); noite = o ciclo circadiano do motor (ConfigPadrao.e_noite)
LIMIAR_CANSADO_INSTINTO = 0.25
JANELA_COERENCIA = CONFIG_VINCULO.janela_coerencia_ticks


class VinculoRegistrado(Vinculo):
    """O Vinculo de sempre, anotando cada atualizacao. O valor e identico (conferido contra o artefato)."""

    def __init__(self, cfg=None) -> None:
        super().__init__(cfg)
        self.registro: list[dict] = []        # cada atualizacao: componente, tipo, amostra/delta, peso, atendido
        self.feedbacks_ctx: list[dict] = []   # cada feedback do dono: acao do pet, sinal, contexto do pet
        self.motor = None                     # posto pela fabrica; so leitura do estado

    def _amostra(self, tick, componente, amostra, peso, ref):
        antes = self.valor
        super()._amostra(tick, componente, amostra, peso, ref)
        self.registro.append({"t": tick, "c": componente, "tipo": "amostra", "a": amostra, "p": peso,
                              "atendido": ref is not None if componente in ("atendimento", "desejo") else amostra >= 0.5,
                              "antes": antes, "depois": self.valor})

    def ajustar(self, tick, componente, delta, ref):
        antes = self.valor
        super().ajustar(tick, componente, delta, ref)
        self.registro.append({"t": tick, "c": componente, "tipo": "ajuste", "a": delta, "p": 1.0, "atendido": None,
                              "antes": antes, "depois": self.valor})

    def limitar(self, tick, teto, componente):
        antes = self.valor
        super().limitar(tick, teto, componente)
        self.registro.append({"t": tick, "c": componente, "tipo": "teto", "a": teto, "p": 1.0, "atendido": None,
                              "antes": antes, "depois": self.valor})

    def acao_dono(self, acao, tick, acao_pet, ref):
        if self.motor is not None and self.motor._pre_vetor is None:
            raise RuntimeError("acao do dono sem o estado anterior registrado (gancho do motor nao rodou)")
        if acao.value in CUIDADOS and self.motor is not None:
            v = self.motor._pre_vetor
            lim = CONFIG_MEMORIA_ESPACOS.limiar_necessidade_pedido
            # cuidado com necessidade baixa no estado que o dono viu: estrita = fome ou higiene (o criterio do pedido do pet);
            # ampla = fome, higiene ou humor (as tres necessidades que um cuidado do dono atende)
            self.registro.append({"t": tick, "c": "cuidado", "tipo": "cuidado", "a": None, "p": self.cfg.peso_atendimento,
                                  "nec_baixa": min(v[0], v[1]) < lim, "nec_baixa_ampla": min(v[0], v[1], v[3]) < lim,
                                  "pedido_pendente": bool(self.pedidos), "atendido": None, "antes": self.valor, "depois": self.valor})
        if acao in (AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER) and acao_pet is not None and self.motor is not None:
            v = self.motor._pre_vetor
            fome, higiene, energia = v[0], v[1], v[2]
            ctx = (min(fome, higiene) < CONFIG_MEMORIA_ESPACOS.limiar_necessidade_pedido,
                   energia < LIMIAR_CANSADO_INSTINTO, CONFIG_PADRAO.e_noite(self.motor._pre_tick_do_dia))
            self.feedbacks_ctx.append({"t": tick, "acao": acao_pet.value, "sinal": 1 if acao is AcaoUsuario.ELOGIAR else -1,
                                       "ctx": "".join("1" if x else "0" for x in ctx)})
        super().acao_dono(acao, tick, acao_pet, ref)


def instrumentar(motor):
    """troca o vinculo do motor pela versao anotada e le o estado depois de cada avanco (nada do motor muda)"""
    v = VinculoRegistrado(motor.vinculo.cfg)
    v.motor = motor
    motor.vinculo = v
    motor._amostras_estado = []
    avancar = motor._avancar

    def _avancar_lendo(ticks):
        r = avancar(ticks)
        vet = motor._estado.vetor()
        motor._amostras_estado.append(min(vet[0], vet[1]))
        return r
    motor._avancar = _avancar_lendo
    aplicar = motor._aplicar_acao_usuario
    motor._pre_vetor = None

    def _aplicar_lendo(acao):
        motor._pre_vetor = motor._estado.vetor()          # o estado que o dono viu, antes do efeito da acao
        motor._pre_tick_do_dia = motor._estado.tick_do_dia
        return aplicar(acao)
    motor._aplicar_acao_usuario = _aplicar_lendo
    return motor


def coerencia_contextual(feedbacks: list[dict]) -> list[tuple[float | None, float | None]]:
    """por feedback do dono: (amostra da regra de hoje, amostra por contexto). A regra de hoje: fracao dos feedbacks
    anteriores na janela sobre a MESMA acao do pet com o mesmo sinal; a contextual: a mesma fracao, mas por (acao do pet,
    contexto do pet). None quando nao ha historico (hoje tambem nao gera amostra; a contextual, idem)."""
    hist_a: dict[str, list[tuple[int, int]]] = {}
    hist_c: dict[tuple, list[tuple[int, int]]] = {}
    out = []
    for f in feedbacks:
        ka, kc = f["acao"], (f["acao"], f["ctx"])
        ha = [(t, s) for t, s in hist_a.get(ka, []) if f["t"] - t <= JANELA_COERENCIA]
        hc = [(t, s) for t, s in hist_c.get(kc, []) if f["t"] - t <= JANELA_COERENCIA]
        out.append((sum(s == f["sinal"] for _, s in ha) / len(ha) if ha else None,
                    sum(s == f["sinal"] for _, s in hc) / len(hc) if hc else None))
        hist_a[ka] = ha + [(f["t"], f["sinal"])]
        hist_c[kc] = hc + [(f["t"], f["sinal"])]
    return out


def recalcular(registro: list[dict], cfg, manter, transformar=None) -> float:
    """o vinculo final se so as atualizacoes aceitas por `manter` tivessem acontecido (ajustes e teto sempre entram);
    `transformar(entrada) -> amostra` troca a amostra. Mesma formula do Vinculo, sobre o fluxo gravado."""
    v, teto = cfg.inicial, 1.0
    for e in registro:
        if e["tipo"] == "ajuste":
            v = min(teto, max(0.0, v + e["a"]))
        elif e["tipo"] == "teto":
            teto = e["a"]
            v = min(v, teto)
        elif e["tipo"] == "cuidado":
            if not (transformar is not None and manter(e)):
                continue                       # na regra de hoje o cuidado em si nao e amostra
            a = transformar(e)
            if a is None:
                continue
            v = min(teto, max(0.0, v + cfg.alfa * e["p"] * (a - v)))
        elif manter(e):
            a = e["a"] if transformar is None else transformar(e)
            if a is None:                      # sem amostra neste evento (contrafactual): nada acontece
                continue
            v = min(teto, max(0.0, v + cfg.alfa * e["p"] * (a - v)))
    return v


def resumo_vida(nome: str, dono: str, motor, log: LogDeEventos, vinculo_ref: float) -> dict:
    v: VinculoRegistrado = motor.vinculo
    if v.valor != vinculo_ref:
        raise RuntimeError(f"{nome}: vinculo do replay {v.valor!r} != artefato {vinculo_ref!r}")
    acoes = Counter(e.valor for e in log if e.tipo == "acao_usuario")
    por_c: dict = {}
    for c in COMPONENTES:
        xs = [e for e in v.registro if e["tipo"] == "amostra" and e["c"] == c]
        por_c[c] = {"n": len(xs), "n_atendido": sum(bool(e["atendido"]) for e in xs),
                    "amostra_media": (sum(e["a"] for e in xs) / len(xs)) if xs else None,
                    "empurrao": sum(e["depois"] - e["antes"] for e in xs)}
    ajustes = Counter(e["c"] for e in v.registro if e["tipo"] == "ajuste")
    pares = coerencia_contextual(v.feedbacks_ctx)
    coer_hoje = [e["a"] for e in v.registro if e["tipo"] == "amostra" and e["c"] == "coerencia"]
    hoje_recalc = [h for h, _ in pares if h is not None]
    if hoje_recalc != coer_hoje:
        raise RuntimeError(f"{nome}: a coerencia recalculada por feedback nao bate com as amostras do vinculo "
                           f"({len(hoje_recalc)} x {len(coer_hoje)})")
    # alinhada com as amostras de coerencia de hoje: a contextual no mesmo evento, ou None (sem historico no contexto)
    ctx_alinhada = [c for h, c in pares if h is not None]
    com_hist = [c for c in ctx_alinhada if c is not None]
    estados = motor._amostras_estado
    cuid = [e for e in v.registro if e["tipo"] == "cuidado"]
    return {"nome": nome, "dono": dono, "vinculo_final": v.valor, "atualizacoes": len(v.registro) - len(cuid),
            "cuidados_com_necessidade_baixa": sum(e["nec_baixa"] for e in cuid),
            "cuidados_com_necessidade_baixa_ampla": sum(e["nec_baixa_ampla"] for e in cuid),
            "cuidados_com_pedido_pendente": sum(e["pedido_pendente"] for e in cuid),
            "acoes_do_dono": dict(acoes), "cuidados": sum(acoes[a] for a in CUIDADOS), "feedbacks_do_dono": sum(acoes[a] for a in FEEDBACK),
            "componentes": por_c, "ajustes": dict(ajustes), "teto": v.teto,
            "coerencia_hoje_media": (sum(coer_hoje) / len(coer_hoje)) if coer_hoje else None,
            "coerencia_contextual_media": (sum(com_hist) / len(com_hist)) if com_hist else None,
            "feedbacks": len(v.feedbacks_ctx), "amostras_coerencia_hoje": len(coer_hoje), "amostras_coerencia_contextual": len(com_hist),
            "fracao_avancos_necessidade_baixa": sum(x < CONFIG_MEMORIA_ESPACOS.limiar_necessidade_pedido for x in estados) / len(estados),
            "necessidade_minima_media": sum(estados) / len(estados),
            # fluxo compacto para os contrafactuais (agregados no processo principal)
            "_registro": [(e["c"], e["tipo"], e["a"], e["p"], e.get("nec_baixa"), e.get("nec_baixa_ampla")) for e in v.registro],
            "_coerencia_ctx": ctx_alinhada}


def medir_personalidade(args) -> dict:
    nome, dono, semente = args
    pasta = PERSONALIDADE / "vidas"
    log = LogDeEventos.de_jsonl((pasta / f"{nome}.jsonl").read_text(encoding="utf-8"))
    ref = json.loads((pasta / f"{nome}.personalidade.json").read_text(encoding="utf-8"))
    fab_pol, fab_motor = fabricas_vida(PROTOCOLOS["arena-v1-personalidade"], "bandit_personalidade", semente)
    fm = lambda politica, cfg, s: instrumentar(fab_motor(politica, cfg, s))  # noqa: E731
    m = reproduzir_com_feedback(log, fab_pol, semente=semente, fabrica_motor=fm)
    return resumo_vida(nome, dono, m, log, ref["vinculo_final"])


def medir_e1(args) -> dict:
    b, g, r, esp_regra, pasta, ref = args
    esp, temp_ovo, tmp = genoma(g, esp_regra)
    nome = chave(b, g, r)
    log = LogDeEventos.de_jsonl((Path(pasta) / f"{nome}.jsonl").read_text(encoding="utf-8"))
    fp, _, fm, _ = _fabricas(b, r, esp, tmp, temp_ovo)
    fmi = lambda politica, cfg, s: instrumentar(fm(politica, cfg, s))  # noqa: E731
    m = reproduzir_educacao(log, fp, semente=r, fabrica_motor=fmi)
    return resumo_vida(nome, b, m, log, ref)


def media(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def agregar(vidas: list[dict], cfg) -> dict:
    donos = sorted({v["dono"] for v in vidas})
    por_dono = {}
    for d in donos:
        vs = [v for v in vidas if v["dono"] == d]
        acoes = Counter()
        for v in vs:
            acoes.update(v["acoes_do_dono"])
        comp = {}
        for c in COMPONENTES:
            comp[c] = {"n_medio_por_vida": media([v["componentes"][c]["n"] for v in vs]),
                       "n_atendido_medio_por_vida": media([v["componentes"][c]["n_atendido"] for v in vs]),
                       "amostra_media": media([v["componentes"][c]["amostra_media"] for v in vs]),
                       "vidas_com_amostra": sum(v["componentes"][c]["n"] > 0 for v in vs),
                       "empurrao_medio": media([v["componentes"][c]["empurrao"] for v in vs])}
        ajustes = Counter()
        for v in vs:
            ajustes.update(v["ajustes"])
        por_dono[d] = {"n_vidas": len(vs), "vinculo_final_medio": media([v["vinculo_final"] for v in vs]),
                       "vinculo_final_min_max": [min(v["vinculo_final"] for v in vs), max(v["vinculo_final"] for v in vs)],
                       "acoes_do_dono_por_vida": {a: n / len(vs) for a, n in sorted(acoes.items())},
                       "cuidados_por_vida": media([v["cuidados"] for v in vs]), "feedbacks_por_vida": media([v["feedbacks_do_dono"] for v in vs]),
                       "amostras_coerencia_hoje_por_vida": media([v["amostras_coerencia_hoje"] for v in vs]),
                       "amostras_coerencia_contextual_por_vida": media([v["amostras_coerencia_contextual"] for v in vs]),
                       "componentes": comp, "ajustes_por_vida": {a: n / len(vs) for a, n in sorted(ajustes.items())},
                       "fracao_cuidados_com_necessidade_baixa": media([v["cuidados_com_necessidade_baixa"] / v["cuidados"] for v in vs if v["cuidados"]]),
                       "fracao_cuidados_com_necessidade_baixa_ampla": media([v["cuidados_com_necessidade_baixa_ampla"] / v["cuidados"] for v in vs if v["cuidados"]]),
                       "fracao_cuidados_com_pedido_pendente": media([v["cuidados_com_pedido_pendente"] / v["cuidados"] for v in vs if v["cuidados"]]),
                       "coerencia_hoje_media": media([v["coerencia_hoje_media"] for v in vs]),
                       "coerencia_contextual_media": media([v["coerencia_contextual_media"] for v in vs]),
                       "fracao_avancos_necessidade_baixa": media([v["fracao_avancos_necessidade_baixa"] for v in vs]),
                       "necessidade_minima_media": media([v["necessidade_minima_media"] for v in vs])}
    # contrafactuais sobre o fluxo gravado
    base = {c: por_dono["aleatorio"]["componentes"][c]["amostra_media"] for c in COMPONENTES}

    def normalizar(e):
        b = base.get(e[0])
        return None if b is None else min(1.0, max(0.0, cfg.inicial + (e[2] - b)))

    def resposta(e):
        """atendimento por resposta: cada cuidado do dono vira amostra 1 com necessidade baixa (fome ou higiene) e 0 sem"""
        return (1.0 if e[4] else 0.0) if e[1] == "cuidado" else e[2]

    def resposta_ampla(e):
        """idem, com humor entre as necessidades"""
        return (1.0 if e[5] else 0.0) if e[1] == "cuidado" else e[2]

    def variante(nome_v, manter, transformar=None, troca_coerencia=False):
        finais = {}
        for v in vidas:
            reg = [{"c": c, "tipo": t, "a": a, "p": p, "nec_baixa": nb, "nec_baixa_ampla": nba} for c, t, a, p, nb, nba in v["_registro"]]
            if troca_coerencia:
                it = iter(v["_coerencia_ctx"])
                for e in reg:
                    if e["tipo"] == "amostra" and e["c"] == "coerencia":
                        e["a"] = next(it)
            tr = (lambda e: transformar((e["c"], e["tipo"], e["a"], e["p"], e["nec_baixa"], e["nec_baixa_ampla"]))) if transformar else None
            finais.setdefault(v["dono"], []).append(recalcular(reg, cfg, manter, tr))
        med = {d: media(xs) for d, xs in finais.items()}
        med["atencioso-aleatorio"] = med["atencioso"] - med["aleatorio"]
        return med
    contrafactuais = {
        "hoje (conferencia: igual ao replay)": variante("hoje", lambda e: True),
        "so_atendimento": variante("so_atendimento", lambda e: e["c"] == "atendimento"),
        "so_coerencia": variante("so_coerencia", lambda e: e["c"] == "coerencia"),
        "so_desejo": variante("so_desejo", lambda e: e["c"] == "desejo"),
        "sem_atendimento": variante("sem_atendimento", lambda e: e["c"] != "atendimento"),
        "normalizado_pela_media_do_aleatorio": variante("normalizado", lambda e: True, normalizar),
        "coerencia_contextual_no_lugar_da_coerencia": variante("ctx", lambda e: True, troca_coerencia=True),
        "coerencia_contextual_sem_atendimento": variante("ctx_sem_atend", lambda e: e["c"] != "atendimento", troca_coerencia=True),
        "so_coerencia_contextual": variante("so_ctx", lambda e: e["c"] == "coerencia", troca_coerencia=True),
        "atendimento_por_resposta": variante("resposta", lambda e: e["c"] != "atendimento", resposta),
        "atendimento_por_resposta_ampla": variante("resposta_ampla", lambda e: e["c"] != "atendimento", resposta_ampla),
        "atendimento_por_resposta_ampla_e_coerencia_contextual": variante("resposta_ctx", lambda e: e["c"] != "atendimento",
                                                                         resposta_ampla, troca_coerencia=True),
    }
    hoje = contrafactuais["hoje (conferencia: igual ao replay)"]
    for d in donos:
        if abs(hoje[d] - por_dono[d]["vinculo_final_medio"]) > 1e-12:
            raise RuntimeError(f"recalculo do fluxo gravado difere do replay no dono {d}: {hoje[d]} != {por_dono[d]['vinculo_final_medio']}")
    return {"donos": donos, "n_vidas": len(vidas), "por_dono": por_dono, "baseline_aleatorio_por_componente": base,
            "contrafactuais": contrafactuais}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--e1", default=str(VIDAS_E1), help="pasta com as 640 vidas .jsonl do E1 (especie_fixa)")
    ap.add_argument("--processos", type=int, default=8)
    ap.add_argument("--so-personalidade", action="store_true")
    a = ap.parse_args(argv)
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    t0 = time.perf_counter()
    met = json.loads((PERSONALIDADE / "metrics.json").read_text(encoding="utf-8"))
    tarefas = [(f"{b}@{s}", b, s) for b in met["bracos"] for s in met["sementes_coorte"]]
    with ProcessPoolExecutor(a.processos) as pool:
        vidas_p = list(pool.map(medir_personalidade, tarefas))
    t_p = time.perf_counter() - t0
    print(f"  personalidade: {len(vidas_p)} replays conferidos em {t_p:.0f} s", flush=True)
    out = {"tarefa": "docs/TAREFA_V2_F0_VINCULO.md",
           "config_vinculo": {k: getattr(CONFIG_VINCULO, k) for k in ("inicial", "alfa", "peso_atendimento", "peso_coerencia",
                                                                       "peso_desejo", "janela_latencia_ticks",
                                                                       "janela_coerencia_ticks", "janela_desejo_ticks")},
           "contexto_coerencia_contextual": {"necessidade_baixa": f"min(fome, higiene) < {CONFIG_MEMORIA_ESPACOS.limiar_necessidade_pedido} (limiar do pedido)",
                                             "cansado": f"energia < {LIMIAR_CANSADO_INSTINTO} (regra do instinto)",
                                             "noite": "ConfigPadrao.e_noite"},
           "personalidade": {"artefato": "artifacts_v1_personalidade/completa", "protocolo": "arena-v1-personalidade",
                             "conferencia": {"replays_iguais_ao_personalidade_json": len(vidas_p)}, **agregar(vidas_p, CONFIG_VINCULO)}}
    por_pet = [{k: v for k, v in x.items() if not k.startswith("_")} for x in vidas_p]
    if not a.so_personalidade:
        cfg = json.loads(CFG_E1.read_text(encoding="utf-8"))
        rc = cfg["rodadas"]["especie_fixa"]
        pets_e1 = json.loads((E1 / "pets.json").read_text(encoding="utf-8"))
        meta_e1 = json.loads((E1 / "meta.json").read_text(encoding="utf-8"))
        if hash_parametros_educacao() != meta_e1["hash_parametros_educacao"]:
            raise RuntimeError("hash_parametros_educacao difere do E1")
        t1 = time.perf_counter()
        tarefas = [(b, g, r, rc["especie"], a.e1, pets_e1[chave(b, g, r)]["vinculo_final"])
                   for g in rc["genomas"] for r in rc["ambientes"] for b in sorted(cfg["donos"])]
        with ProcessPoolExecutor(a.processos) as pool:
            vidas_e = list(pool.map(medir_e1, tarefas))
        t_e = time.perf_counter() - t1
        print(f"  E1: {len(vidas_e)} replays conferidos em {t_e:.0f} s", flush=True)
        out["e1"] = {"artefato": "artifacts_linhagem/natureza_criacao/especie_fixa (vidas em arquivo/)", "vidas": a.e1,
                     "conferencia": {"replays_iguais_ao_pets_json_do_e1": len(vidas_e), "hash_parametros_educacao_igual": True},
                     **agregar(vidas_e, CONFIG_VINCULO)}
        por_pet += [{k: v for k, v in x.items() if not k.startswith("_")} for x in vidas_e]
    out["meta"] = {"tempo_s": time.perf_counter() - t0, "processos": a.processos,
                   "fontes_sha256": hashlib.sha256(b"".join((RAIZ / p).read_bytes().replace(b"\r\n", b"\n") for p in (
                       "experiments/analisar_vinculo.py", "digilab/vinculo.py", "digilab/obediencia.py", "digilab/educacao.py",
                       "digilab/treino_vida.py", "digilab/config.py"))).hexdigest(),
                   "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()}}
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                          encoding="utf-8", newline="\n")
    (SAIDA / "por_pet.json").write_text(json.dumps(por_pet, ensure_ascii=False, indent=0, sort_keys=True) + "\n",
                                        encoding="utf-8", newline="\n")
    for bloco in ("personalidade", "e1"):
        if bloco not in out:
            continue
        print(f"{bloco}:")
        for d, x in out[bloco]["por_dono"].items():
            cs = "  ".join(f"{c}: n {x['componentes'][c]['n_medio_por_vida']:.1f} a {x['componentes'][c]['amostra_media'] if x['componentes'][c]['amostra_media'] is None else round(x['componentes'][c]['amostra_media'], 3)}"
                           for c in COMPONENTES)
            print(f"  {d:<10} vinculo {x['vinculo_final_medio']:.3f}  cuidados {x['cuidados_por_vida']:.1f} feedbacks {x['feedbacks_por_vida']:.1f}  {cs}")
        for n, v in out[bloco]["contrafactuais"].items():
            print(f"  {n}: " + "  ".join(f"{d} {x:.3f}" for d, x in v.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
