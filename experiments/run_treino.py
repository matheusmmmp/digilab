"""Runs da TAREFA_TREINO_SOMBRIO (secoes 5, 6 e 8).

    python experiments/run_treino.py

1. Vidas com treino: 5 bracos (atencioso, relapso, aleatorio, incoerente, exigente) x os 10 ovos
   da personalidade (mesmo ovo = mesma especie e temperamento em todos os bracos), 14 dias,
   MESMO orcamento em todos (cuidado 16/dia + sessoes-alvo do estagio). Logs em
   artifacts_treino/vidas/; cada vida e rejogada DO DISCO e conferida (treino, vinculo, estado).
2. Evolucao (digilab/evolucao.py) com o MotorTreino no replay; sobrecarga >= 60 no inicio do
   adulto -> forma sombria da linha.
3. Arena V2.1 entre os 5 bracos, por ovo, stats treinados NORMALIZADOS ao orcamento da especie
   (barreira 1); gambits canonicos da forma (as sombrias: bots.SOMBRIOS), epsilon minimo 0,2 nas
   sombrias.
4. Campanha: cada pet (stats treinados ABSOLUTOS) contra os 3 NPCs -> artifacts_campanha/treino.json.
   A campanha e o S2 lutam com as regras da campanha (V21C, campanha.REGRAS_CAMPANHA); a arena segue a V2.1.
5. Gate S2 (bots, sem vida): por linha, forma sombria x cada forma normal da linha, com treino
   uniforme 0..36: (a) treino minimo para vencer o tier 1 (taxa >= 0,5) da sombria <= o da normal;
   (b) taxa media contra o tier 2 da sombria <= a da normal + TOLERANCIA_S2 (0,02: ruido da instabilidade
   das sombrias, decisao do Matheus). Tier 2 = a Torre, com 3 rivais a escolha: vale o MELHOR rival
   (o jogador escolhe contra quem lutar).
Saida em artifacts_treino/. Codigo de saida 0 se S2 passa, 2 se falha (o resto e descritivo).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.campanha import REGRAS_CAMPANHA, npc  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, SOMBRIOS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHAS, SOMBRIA_DA_LINHA, perfil  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar  # noqa: E402
from digilab.combate_v2.v21.regras import REGRAS_PADRAO, Regras  # noqa: E402
from digilab.config import (CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_EVOLUCAO_PESQUISA,  # noqa: E402
                            CONFIG_SOMBRIO, CONFIG_TREINO, STATS_V21)
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import evoluir, ovo  # noqa: E402
from digilab.metrics import bootstrap_ic  # noqa: E402
from digilab.protocol import (ENGINE_SHA256_V0, OVOS_PERSONALIDADE, PROTOCOLO_ARENA_V1, derivar_semente,  # noqa: E402
                              sha256_engine)
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.treino_vida import BRACOS_TREINO, fabricas_treino, orcamento_treino, simular_vida_treino  # noqa: E402

SAIDA = RAIZ / "artifacts_treino"
DIAS = 14
BOOT = (PROTOCOLO_ARENA_V1.v("bootstrap_reamostragens"), PROTOCOLO_ARENA_V1.v("bootstrap_semente"),
        PROTOCOLO_ARENA_V1.v("nivel_confianca"))
NIVEIS_S2 = (0, 6, 12, 18, 24, 30, 36)
TOLERANCIA_S2 = 0.02


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def lutador_pet(nome: str, ev, pontos: dict, absoluto: bool) -> Lutador:
    """absoluto = campanha: stats sem normalizar e vida pela formula da V21C."""
    cfg = REGRAS_CAMPANHA.v21 if absoluto else None
    p = perfil(ev.forma, ev.temperamento, ev.carater_adulto, ev.condicao, cfg, treino=pontos,
               normalizar_treino=not absoluto)
    sombria = ev.forma.adulta in SOMBRIOS
    g = SOMBRIOS[ev.forma.adulta] if sombria else ADULTOS[ev.forma.adulta]
    eps = CONFIG_COMBATE_V2.epsilon_bots
    if sombria:
        eps = max(eps, CONFIG_SOMBRIO.epsilon_minimo)
    return Lutador(nome, p, g, eps)


def taxa(a: Lutador, b: Lutador, rotulo: str, n: int, r: Regras = REGRAS_PADRAO) -> float:
    pts = []
    for k in range(n):
        sp = derivar_semente("treino", rotulo, a.nome, b.nome, k)
        pts.append(jogar(a, b, sp, r).pontos_a if k < n // 2 else 1.0 - jogar(b, a, sp, r).pontos_a)
    return sum(pts) / len(pts)


def gate_s2(n: int) -> dict:
    """Bots canonicos com treino uniforme (nivel/6 em cada stat), stats absolutos (campanha)."""
    especies = list(CONFIG_CATALOGO.especies_ativas)
    lugar = lambda n: [k for k, d in CONFIG_CAMPANHA.npcs.items() if d["lugar"] == n]  # noqa: E731
    t1, t2s = [npc(k) for k in lugar(1)], [npc(k) for k in lugar(2)]
    res, ok = {}, True
    for linha in LINHAS:
        sombria = SOMBRIA_DA_LINHA[linha]
        normais = list(CONFIG_CATALOGO.arquetipos_adulto[linha]["formas"])
        curva = {}
        for forma in [sombria] + normais:
            por_nivel = {}
            for nivel in NIVEIS_S2:
                tr = {k: nivel / len(STATS_V21) for k in STATS_V21}
                v1, v2 = [], []
                for esp in especies:
                    cfg = REGRAS_CAMPANHA.v21
                    base = lutador_adulto(forma, esp, cfg)
                    p = perfil(_forma(forma, esp), None, _car(forma, cfg), 1.0, cfg, treino=tr if nivel else None,
                               normalizar_treino=False)
                    lut = Lutador(f"{forma}+{nivel}@{esp}", p, base.gambits, base.epsilon)
                    v1.append(max(taxa(lut, r, "s2-t1", n, REGRAS_CAMPANHA) for r in t1))
                    v2.append(max(taxa(lut, r, "s2-t2", n, REGRAS_CAMPANHA) for r in t2s))
                por_nivel[nivel] = {"tier1": sum(v1) / len(v1), "tier2": sum(v2) / len(v2)}
            minimo = next((nv for nv in NIVEIS_S2 if por_nivel[nv]["tier1"] >= 0.5), None)
            curva[forma] = {"por_nivel": por_nivel, "treino_minimo_tier1": minimo,
                            "tier2_media": sum(x["tier2"] for x in por_nivel.values()) / len(NIVEIS_S2)}
        comp = {}
        for nf in normais:
            ms, mn = curva[sombria]["treino_minimo_tier1"], curva[nf]["treino_minimo_tier1"]
            mais_cedo = (ms if ms is not None else 999) <= (mn if mn is not None else 999)
            nao_maior = curva[sombria]["tier2_media"] <= curva[nf]["tier2_media"] + TOLERANCIA_S2
            comp[nf] = {"tier1_mais_cedo_ou_igual": mais_cedo, "tier2_nao_maior": nao_maior}
            ok = ok and mais_cedo and nao_maior
        res[linha] = {"sombria": sombria, "curvas": curva, "comparacao": comp}
    return {"ok": ok, "por_linha": res, "niveis": NIVEIS_S2, "partidas_por_par": n, "especies": especies,
            "treino": "uniforme (nivel/6 em cada stat), stats absolutos"}


def _forma(nome, esp):
    from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, Forma
    return Forma(esp, "adulto", "sereno", LINHA_DA_FORMA[nome], nome)


def _car(nome, cfg=None):
    from digilab.combate_v2.v21.catalogo import carater_canonico
    return carater_canonico(nome, cfg)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--partidas", type=int, default=100, help="por par (par; lados trocados)")
    ap.add_argument("--partidas-s2", type=int, default=40)
    a = ap.parse_args(argv)
    if a.partidas % 2 or a.partidas_s2 % 2:
        raise ValueError("partidas precisa ser par")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    orc, alvo = orcamento_treino(DIAS)
    sondas = (PROTOCOLO_ARENA_V1.v("estados_sonda"), PROTOCOLO_ARENA_V1.v("amostras_por_estado"),
              PROTOCOLO_ARENA_V1.v("semente_sonda"))

    # 1-2. vidas, replay do disco e evolucao
    pets = {}
    for s in OVOS_PERSONALIDADE:
        esp, _ = ovo(s)
        t = sortear(s)
        for b in BRACOS_TREINO:
            v = simular_vida_treino(b, s, DIAS, esp, t)
            m = v.motor
            if v.interacoes != orc:
                raise RuntimeError(f"{b}@{s}: {v.interacoes} interacoes, esperado {orc}")
            arq = SAIDA / "vidas" / f"{b}@{s}.jsonl"
            _gravar(arq, m.log.para_jsonl())
            fp, fm = fabricas_treino(s, esp, t)
            r = reproduzir_com_feedback(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), fp, semente=s,
                                        fabrica_motor=fm)
            if (r.resumo_treino() != m.resumo_treino() or r.estado() != m.estado()
                    or r.vinculo.serie != m.vinculo.serie):
                raise RuntimeError(f"replay de {b}@{s} divergiu")
            ev = evoluir(m.log, fp, s, *sondas, m.estado()["saude"], fabrica_motor=fm, sombria=bool(m.sombria))
            res = m.resumo_treino()
            dados = {"braco": b, "ovo": s, "especie": esp, "forma": ev.para_dict()["forma"], "sombria": bool(m.sombria),
                     "fala_fria": bool(m.fala_fria), "treino": res, "vinculo_final": m.vinculo.valor,
                     "obediencia_cuidado": 1.0 - len(m.recusas) / m.pedidos_obediencia if m.pedidos_obediencia else 1.0,
                     "sessoes": len(m.treino.sessoes), "enroladas": m.enroladas,
                     "dono": dict(v.dono.contagem), "carater_adulto": ev.carater_adulto, "condicao": ev.condicao}
            _gravar(SAIDA / "vidas" / f"{b}@{s}.treino.json", _dump(dados))
            pets[(b, s)] = (ev, m.treino.pontos, dados)
            print(f"  {b:10s} {s:5d} {ev.forma.rotulo:40s} sombria={m.sombria} sobre@adulto="
                  f"{res['transicoes']['adulto']['sobrecarga']:.1f} vinc={m.vinculo.valor:.3f}", flush=True)

    # 3. arena (normalizada)
    print("arena ...", flush=True)
    arena = {}
    for s in OVOS_PERSONALIDADE:
        lut = {b: lutador_pet(f"{b}@{s}", pets[(b, s)][0], pets[(b, s)][1], False) for b in BRACOS_TREINO}
        for i, x in enumerate(BRACOS_TREINO):
            for y in BRACOS_TREINO[i + 1:]:
                arena[(s, x, y)] = taxa(lut[x], lut[y], f"arena|{s}", a.partidas)

    def pts_braco(b):
        vals = []
        for s in OVOS_PERSONALIDADE:
            vs = [arena[(s, x, y)] if x == b else 1 - arena[(s, x, y)] for (ss, x, y) in arena if ss == s and b in (x, y)]
            vals.append(sum(vs) / len(vs))
        return vals

    # 4. campanha (absoluta)
    print("campanha ...", flush=True)
    camp = {}
    for (b, s), (ev, pontos, _) in pets.items():
        lut = lutador_pet(f"{b}@{s}", ev, pontos, True)
        camp[(b, s)] = {tier: taxa(lut, npc(tier), f"campanha|{s}", CONFIG_CAMPANHA.partidas_por_par, REGRAS_CAMPANHA)
                        for tier in CONFIG_CAMPANHA.npcs}

    # 5. S2
    print("S2 ...", flush=True)
    s2 = gate_s2(a.partidas_s2)

    # resumo
    por_braco = {}
    for b in BRACOS_TREINO:
        ds = [pets[(b, s)][2] for s in OVOS_PERSONALIDADE]
        por_braco[b] = {
            "fracao_sombria": sum(d["sombria"] for d in ds) / len(ds),
            "fracao_fala_fria": sum(d["fala_fria"] for d in ds) / len(ds),
            "vinculo_final": bootstrap_ic([d["vinculo_final"] for d in ds], *BOOT),
            "obediencia_cuidado": bootstrap_ic([d["obediencia_cuidado"] for d in ds], *BOOT),
            "enroladas_por_sessao": sum(d["enroladas"] for d in ds) / max(1, sum(d["sessoes"] for d in ds)),
            "treino_total": bootstrap_ic([d["treino"]["total"] for d in ds], *BOOT),
            "forcadas_media": sum(d["treino"]["forcadas"] for d in ds) / len(ds),
            "pausas_ignoradas_media": sum(d["treino"]["pausas"]["ignoradas"] for d in ds) / len(ds),
            "sobrecarga_no_adulto": [d["treino"]["transicoes"]["adulto"]["sobrecarga"] for d in ds],
            "formas_adultas": dict(Counter(d["forma"]["adulta"] for d in ds)),
            "linhas": dict(Counter(d["forma"]["linha"] for d in ds)),
            "arena_media_contra_os_outros": bootstrap_ic(pts_braco(b), *BOOT),
            "campanha": {tier: bootstrap_ic([camp[(b, s)][tier] for s in OVOS_PERSONALIDADE], *BOOT)
                         for tier in CONFIG_CAMPANHA.npcs},
        }
    par = lambda x, y, s: arena[(s, x, y)] if (s, x, y) in arena else 1 - arena[(s, y, x)]  # noqa: E731
    ex_at = {
        "arena_exigente_contra_atencioso": bootstrap_ic([par("exigente", "atencioso", s) for s in OVOS_PERSONALIDADE], *BOOT),
        "vinculo_exigente_menos_atencioso": bootstrap_ic(
            [pets[("exigente", s)][2]["vinculo_final"] - pets[("atencioso", s)][2]["vinculo_final"] for s in OVOS_PERSONALIDADE], *BOOT),
        "campanha_exigente_menos_atencioso": {tier: bootstrap_ic(
            [camp[("exigente", s)][tier] - camp[("atencioso", s)][tier] for s in OVOS_PERSONALIDADE], *BOOT)
            for tier in CONFIG_CAMPANHA.npcs},
        "atencioso_contra_aleatorio": bootstrap_ic([par("atencioso", "aleatorio", s) for s in OVOS_PERSONALIDADE], *BOOT),
    }
    fontes = [RAIZ / "digilab" / f for f in ("treino_stats.py", "treino_vida.py", "evolucao.py", "obediencia.py")]
    fontes += sorted((RAIZ / "digilab" / "combate_v2" / "v21").glob("*.py"))
    h = hashlib.sha256()
    for f in fontes:
        h.update(f.name.encode() + b"\0" + f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    resumo = {
        "descricao": __doc__.splitlines()[0], "ovos": OVOS_PERSONALIDADE, "dias": DIAS,
        "orcamento_por_vida": orc, "slots_alvo": alvo, "partidas_por_par": a.partidas,
        "por_braco": por_braco, "exigente_x_atencioso": ex_at, "S2": s2,
        "replay_vidas_do_disco": len(pets),
        "config_treino": asdict(CONFIG_TREINO), "config_sombrio": asdict(CONFIG_SOMBRIO),
        "config_evolucao": asdict(CONFIG_EVOLUCAO_PESQUISA), "fontes_sha256": h.hexdigest(),
        "avisos": ["todos os numeros sao PROPOSTOS; sobrecarga_forcar calibrada 15 -> 25 (calibracao_treino.json)",
                   "bateria V2.1 REPROVADA (pre-condicao dispensada pelo Matheus)",
                   "interpretacoes em docs/REGISTRO_DESVIOS.md"],
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    _gravar(SAIDA / "resumo.json", _dump(resumo))
    _gravar(RAIZ / "artifacts_campanha" / "treino.json", _dump({
        "descricao": "campanha dos 5 bracos com treino (stats absolutos) contra os 3 NPCs; ver artifacts_treino/resumo.json",
        "por_pet": {f"{b}@{s}": v for (b, s), v in camp.items()},
        "por_braco": {b: por_braco[b]["campanha"] for b in BRACOS_TREINO},
        "partidas_por_par": CONFIG_CAMPANHA.partidas_por_par}))
    for b in BRACOS_TREINO:
        d = por_braco[b]
        print(f"  {b:10s} sombria={d['fracao_sombria']:.1f} vinc={d['vinculo_final']['media']:.3f} "
              f"arena={d['arena_media_contra_os_outros']['media']:.3f} "
              f"camp={[round(d['campanha'][t]['media'], 2) for t in CONFIG_CAMPANHA.npcs]}")
    print("  exigente x atencioso (arena):", ex_at["arena_exigente_contra_atencioso"])
    print(f"  [{'ok' if s2['ok'] else 'REPROVA'}] S2")
    return 0 if s2["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
