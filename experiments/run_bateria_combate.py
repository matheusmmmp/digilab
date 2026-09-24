"""Bateria de bots do combate V2: o portao do combate.

    python experiments/run_bateria_combate.py --config experiments/configs/bateria_canonico.json

Round-robin completo entre os bots (inclui espelhos), N partidas por par por
semente, lados trocados na metade. Gates G1-G7 (limiares em
ConfigBateriaCombate, todos PROPOSTOS). Codigo de saida: 0 APROVADA,
2 REPROVADA; motivo por gate em gates.json.

Calibracao sem overfitting: o JSON fixa sementes de calibracao e de
validacao disjuntas; `conjunto` escolhe qual usar. Numeros so se ajustam
olhando calibracao; a run canonica usa so validacao.

Saida: matriz.json, equilibrio.json, gates.json, partidas.csv,
amostra_replay.jsonl (partidas rejogadas do disco no G3).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import statistics
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.bots import ADAPTATIVO, FIXOS, ORACULO, TODOS, bot, permutar  # noqa: E402
from digilab.combate_v2.gambits import PESADO_AUTOMATICO  # noqa: E402
from digilab.combate_v2.lutador import CondicaoFisica, Estilo, Lutador  # noqa: E402
from digilab.combate_v2.partida import jogar, reproduzir  # noqa: E402
from digilab.combate_v2.regras import ACOES_ESCOLHIVEIS  # noqa: E402
from digilab.config import CONFIG_BATERIA_COMBATE, CONFIG_COMBATE_V2  # noqa: E402
from digilab.metrics import bootstrap_ic, equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402
from run_arena import _imports_externos  # noqa: E402

CHAVES = {"descricao", "saida", "sementes_calibracao", "sementes_validacao", "conjunto",
          "partidas_por_par_por_semente", "registro_calibracao"}
BOOT_REAMOSTRAGENS, BOOT_SEMENTE, BOOT_NIVEL = 10000, 4242, 0.95


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(caminho: Path, texto: str) -> None:
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def carregar(caminho: Path) -> dict:
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    extras = set(cfg) - CHAVES
    if extras:
        raise KeyError(f"chaves desconhecidas no config da bateria: {sorted(extras)}")
    for k in ("saida", "sementes_calibracao", "sementes_validacao", "conjunto", "partidas_por_par_por_semente"):
        if k not in cfg:
            raise KeyError(f"config da bateria sem {k!r}")
    cal, val = cfg["sementes_calibracao"], cfg["sementes_validacao"]
    if set(cal) & set(val):
        raise ValueError(f"sementes de calibracao e validacao se sobrepoem: {sorted(set(cal) & set(val))}")
    if cfg["conjunto"] not in ("calibracao", "validacao"):
        raise ValueError(f"conjunto invalido: {cfg['conjunto']!r}")
    if cfg["partidas_por_par_por_semente"] % 2:
        raise ValueError("partidas por par precisa ser par (lados trocados na metade)")
    return cfg


def hashes(cfg_json: dict) -> dict:
    fontes = sorted((RAIZ / "digilab" / "combate_v2").glob("*.py"))
    h_regras = hashlib.sha256()
    for f in fontes:
        h_regras.update(f.name.encode() + b"\0" + f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    # saida e descricao nao mudam o experimento: ficam fora do hash
    semantico = {k: v for k, v in cfg_json.items() if k not in ("saida", "descricao")}
    carga = {"combate": asdict(CONFIG_COMBATE_V2), "bateria": asdict(CONFIG_BATERIA_COMBATE), "json": semantico}
    h_cfg = hashlib.sha256(json.dumps(carga, sort_keys=True, default=list).encode()).hexdigest()
    return {"regras_sha256": h_regras.hexdigest(), "config_sha256": h_cfg,
            "arquivos_regras": [f.name for f in fontes]}


def _partidas_par(a: Lutador, b: Lutador, rotulo: str, sementes: list[int], n: int):
    """N partidas por semente; na segunda metade os lados trocam. Pontos sempre do ponto de vista de `a`."""
    for s in sementes:
        for k in range(n):
            sp = derivar_semente("bateria", rotulo, s, a.nome, b.nome, k)
            if k < n // 2:
                p = jogar(a, b, sp)
                yield s, k, p, p.pontos_a, 0
            else:
                p = jogar(b, a, sp)
                yield s, k, p, 1.0 - p.pontos_a, 1


def executar(caminho_cfg: Path) -> int:
    cfg = carregar(caminho_cfg)
    cb = CONFIG_BATERIA_COMBATE
    saida = Path(cfg["saida"])
    if not saida.is_absolute():
        saida = RAIZ / saida
    saida.mkdir(parents=True, exist_ok=True)

    externos = sorted(_imports_externos(RAIZ / "digilab"))
    if externos:
        raise RuntimeError(f"digilab usa imports fora da stdlib: {externos}")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")

    sementes = list(cfg["sementes_" + cfg["conjunto"]])
    n = cfg["partidas_por_par_por_semente"]
    bots = {nome: bot(nome) for nome in TODOS}

    # ------------------------------------------------ round-robin
    linhas, confrontos, amostra = [], [], []
    por_semente: dict[tuple[str, str, int], list[float]] = {}
    turnos, fins = [], {"ko": 0, "limite": 0}
    decisoes = {nome: {a.value: 0 for a in ACOES_ESCOLHIVEIS} for nome in TODOS}
    espelho_lado0 = {nome: [] for nome in TODOS}
    passo_amostra = None
    nomes = list(TODOS)
    total_previsto = len(nomes) * (len(nomes) + 1) // 2 * n * len(sementes)
    passo_amostra = max(1, total_previsto // cb.partidas_replay_amostra)
    contador = 0
    for i, na in enumerate(nomes):
        for nb in nomes[i:]:
            for s, k, p, pts, trocado in _partidas_par(bots[na], bots[nb], "rr", sementes, n):
                confrontos.append((na, nb, pts))
                por_semente.setdefault((na, nb, s), []).append(pts)
                turnos.append(p.turnos)
                fins[p.motivo_fim] += 1
                if na == nb:
                    espelho_lado0[na].append(p.pontos_a)
                for ev in p.log:
                    if ev["tipo"] != "turno":
                        continue
                    for lado, (acao, motivo) in ((0, (ev["a"], ev["ma"])), (1, (ev["b"], ev["mb"]))):
                        if motivo == PESADO_AUTOMATICO:
                            continue
                        dono = p.nome_a if lado == 0 else p.nome_b
                        decisoes[dono][acao] += 1
                u = p.estado_final.lados
                linhas.append([s, k, p.nome_a, p.nome_b, p.semente, p.pontos_a, p.motivo_fim, p.turnos,
                               repr(u[0].hp), repr(u[1].hp)])
                if contador % passo_amostra == 0 and len(amostra) < cb.partidas_replay_amostra:
                    amostra.append(p)
                contador += 1

    with (saida / "partidas.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["semente_conjunto", "k", "lado_a", "lado_b", "semente_partida", "pontos_a", "fim", "turnos", "hp_a", "hp_b"])
        w.writerows(linhas)
    _gravar(saida / "amostra_replay.jsonl", "".join(p.para_jsonl() for p in amostra))

    taxa = matriz_taxas(confrontos)
    taxa_semente = {
        f"{a}|{b}|{s}": sum(v) / len(v) for (a, b, s), v in sorted(por_semente.items())
    }
    _gravar(saida / "matriz.json", _dump({
        "unidade": "pontos medios da linha contra a coluna (empate = 0.5), lados trocados na metade",
        "conjunto": cfg["conjunto"], "sementes": sementes, "partidas_por_par_por_semente": n,
        "taxa": taxa, "taxa_por_semente": taxa_semente, "n_partidas": len(confrontos),
    }))

    # ------------------------------------------------ equilibrio
    eq_fixos = equilibrio_simetrico(taxa, list(FIXOS), cb.iteracoes_fictitious_play)
    eq_todos = equilibrio_simetrico(taxa, [x for x in TODOS if x != ORACULO], cb.iteracoes_fictitious_play)
    sup = suporte(eq_fixos["estrategia"], cb.peso_minimo_suporte)
    _gravar(saida / "equilibrio.json", _dump({
        "bots_fixos": {**eq_fixos, "suporte": sup, "peso_minimo_suporte": cb.peso_minimo_suporte},
        "fixos_mais_adaptativo_informativo": {**eq_todos, "suporte": suporte(eq_todos["estrategia"], cb.peso_minimo_suporte)},
    }))

    gates = []

    def gate(nome, ok, msg, valores):
        gates.append({"gate": nome, "ok": bool(ok), "mensagem": msg, "valores": valores})

    # G1
    dominantes = [x for x in FIXOS if all(taxa[x][y] > 0.5 for y in FIXOS if y != x)]
    g1 = not dominantes and len(sup) >= cb.suporte_minimo
    gate("G1_sem_estrategia_dominante", g1,
         (f"nenhum fixo vence todos os outros; suporte do equilibrio {sup} (>= {cb.suporte_minimo})" if g1 else
          f"FALHOU: dominantes {dominantes}; suporte {sup} (precisa >= {cb.suporte_minimo})"),
         {"dominantes": dominantes, "suporte": sup, "estrategia": eq_fixos["estrategia"]})

    # G2
    ad_al = [taxa_semente[f"{ADAPTATIVO}|aleatorio|{s}"] if f"{ADAPTATIVO}|aleatorio|{s}" in taxa_semente
             else 1.0 - taxa_semente[f"aleatorio|{ADAPTATIVO}|{s}"] for s in sementes]
    ic = bootstrap_ic(ad_al, BOOT_REAMOSTRAGENS, BOOT_SEMENTE, BOOT_NIVEL)
    media_vs_fixos = {x: sum(taxa[x][y] for y in FIXOS) / len(FIXOS) for x in (ADAPTATIVO, ORACULO)}
    g2a = taxa[ADAPTATIVO]["aleatorio"] >= cb.taxa_min_adaptativo_vs_aleatorio and ic["ic_inferior"] > 0.5
    g2b = media_vs_fixos[ORACULO] >= media_vs_fixos[ADAPTATIVO]
    gate("G2_existe_habilidade", g2a and g2b,
         f"adaptativo x aleatorio {taxa[ADAPTATIVO]['aleatorio']:.3f} (>= {cb.taxa_min_adaptativo_vs_aleatorio}), "
         f"IC95 [{ic['ic_inferior']:.3f}, {ic['ic_superior']:.3f}] (inferior > 0.5: {ic['ic_inferior'] > 0.5}); "
         f"media contra fixos: oraculo {media_vs_fixos[ORACULO]:.3f} x adaptativo {media_vs_fixos[ADAPTATIVO]:.3f} "
         f"(oraculo >= adaptativo: {g2b})",
         {"adaptativo_vs_aleatorio": taxa[ADAPTATIVO]["aleatorio"], "ic95_por_semente": ic,
          "media_contra_fixos": media_vs_fixos})

    # G3
    vies = {x: sum(v) / len(v) for x, v in espelho_lado0.items()}
    fora = {x: v for x, v in vies.items() if abs(v - 0.5) > cb.tolerancia_espelho}
    arquivo = (saida / "amostra_replay.jsonl").read_text(encoding="utf-8").splitlines()
    logs, atual = [], []
    for linha in arquivo:
        ev = json.loads(linha)
        if ev["tipo"] == "cabecalho" and atual:
            logs.append(atual)
            atual = []
        atual.append(ev)
    if atual:
        logs.append(atual)
    for log in logs:
        reproduzir(log, bots[log[0]["a"]], bots[log[0]["b"]])  # diverge -> ReplayCombateDivergiu
    g3 = not fora and len(logs) == len(amostra)
    gate("G3_sanidade", g3,
         f"pontos do lado 0 nos espelhos (vies de posicao) dentro de 0.5 +- {cb.tolerancia_espelho}: "
         f"{'sim' if not fora else 'NAO ' + str(fora)}; {len(logs)} partidas rejogadas do disco bit a bit",
         {"pontos_lado0_espelho": vies, "replay_partidas": len(logs)})

    # G4
    med = statistics.median(turnos)
    frac_lim = fins["limite"] / len(turnos)
    g4 = cb.mediana_turnos_min <= med <= cb.mediana_turnos_max and frac_lim < cb.fracao_max_limite_turnos
    gate("G4_ritmo", g4,
         f"mediana de turnos {med} (entre {cb.mediana_turnos_min} e {cb.mediana_turnos_max}); "
         f"{frac_lim:.3f} das partidas no limite de turnos (< {cb.fracao_max_limite_turnos})",
         {"mediana_turnos": med, "fracao_limite": frac_lim, "fins": fins})

    # G5
    cont = {a.value: sum(decisoes[x][a.value] for x in sup) for a in ACOES_ESCOLHIVEIS}
    tot = sum(cont.values())
    frac = {a: c / tot for a, c in cont.items()} if tot else {}
    mortas = sorted(a for a, f in frac.items() if f < cb.fracao_min_acao)
    gate("G5_sem_acao_morta", tot > 0 and not mortas,
         f"fracao de cada acao nas decisoes dos bots do suporte {sup}; abaixo de {cb.fracao_min_acao}: {mortas or 'nenhuma'}",
         {"fracao_por_acao": frac, "decisoes_por_bot": decisoes})

    # G6
    neutra = CondicaoFisica.neutra()
    variantes = {"neutra": neutra}
    for dh in (-1, 1):
        for dg in (-1, 1):
            variantes[f"hp{'+' if dh > 0 else '-'}_guts{'+' if dg > 0 else '-'}"] = CondicaoFisica(
                neutra.hp_max * (1 + dh * cb.variacao_hp), neutra.guts_inicial + dg * cb.variacao_guts_inicial,
                neutra.regen_guts)
    taxa_cond: dict[str, dict[str, float]] = {}
    for estilo_nome in FIXOS:
        taxa_cond[estilo_nome] = {}
        for vnome, cond in variantes.items():
            eu = Lutador(estilo_nome, cond, bots[estilo_nome].estilo)
            pts = [pt for op in FIXOS
                   for _, _, _, pt, _ in _partidas_par(eu, Lutador(op + "#op", neutra, bots[op].estilo),
                                                        f"g6|{vnome}", sementes, cb.partidas_g6_por_semente)]
            taxa_cond[estilo_nome][vnome] = sum(pts) / len(pts)
    efeito_cond = {x: max(v.values()) - min(v.values()) for x, v in taxa_cond.items()}
    neutras = {x: v["neutra"] for x, v in taxa_cond.items()}
    efeito_estilo = max(neutras.values()) - min(neutras.values())
    g6 = max(efeito_cond.values()) < efeito_estilo
    gate("G6_condicao_nao_domina_estilo", g6,
         f"maior efeito da condicao (mesmo estilo) {max(efeito_cond.values()):.3f} "
         f"({max(efeito_cond, key=efeito_cond.get)}) vs efeito do estilo (condicao neutra, melhor - pior) {efeito_estilo:.3f}",
         {"efeito_condicao_por_estilo": efeito_cond, "efeito_estilo": efeito_estilo,
          "taxa_contra_fixos": taxa_cond, "variantes": {k: v.para_dict() for k, v in variantes.items()}})

    # G7
    perms = permutar(ADAPTATIVO, cb.semente_permutacoes_g7, cb.permutacoes_g7)
    orig = bots[ADAPTATIVO]
    por_perm = {}
    for ordem, gl in perms:
        emb = Lutador(f"{ADAPTATIVO}#perm{''.join(map(str, ordem))}", neutra, Estilo(gl, orig.estilo.epsilon))
        pts = [pt for _, _, _, pt, _ in _partidas_par(orig, emb, "g7", sementes, cb.partidas_g7_por_semente)]
        por_perm["".join(map(str, ordem))] = sum(pts) / len(pts)
    media_g7 = sum(por_perm.values()) / len(por_perm)
    gate("G7_ordem_dos_gambits_importa", media_g7 >= cb.taxa_min_g7,
         f"adaptativo original contra {len(perms)} permutacoes da ordem: media {media_g7:.3f} (>= {cb.taxa_min_g7})",
         {"por_permutacao": por_perm, "media": media_g7})

    aprovada = all(g["ok"] for g in gates)
    registro = None
    if cfg.get("registro_calibracao"):
        registro = json.loads((RAIZ / cfg["registro_calibracao"]).read_text(encoding="utf-8"))
    resumo = {
        "status": "APROVADA" if aprovada else "REPROVADA",
        "falharam": [g["gate"] for g in gates if not g["ok"]],
        "gates": gates,
        "conjunto": cfg["conjunto"],
        "sementes": sementes,
        "sementes_calibracao": cfg["sementes_calibracao"],
        "sementes_validacao": cfg["sementes_validacao"],
        "partidas_por_par_por_semente": n,
        "hashes": hashes(cfg),
        "config_combate_v2": asdict(CONFIG_COMBATE_V2),
        "config_bateria": asdict(CONFIG_BATERIA_COMBATE),
        "registro_calibracao": registro,
        "avisos": ["todos os numeros de ConfigCombateV2 e ConfigBateriaCombate sao PROPOSTOS"]
                  + ([] if cfg["conjunto"] == "validacao" else ["conjunto de CALIBRACAO: nao e a run canonica"]),
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    arquivos = ["matriz.json", "equilibrio.json", "partidas.csv", "amostra_replay.jsonl"]
    resumo["artefatos_sha256"] = {a: hashlib.sha256((saida / a).read_bytes()).hexdigest() for a in arquivos}
    _gravar(saida / "gates.json", _dump(resumo))

    print(f"bateria {resumo['status']}  conjunto {cfg['conjunto']}  saida {saida}")
    for g in gates:
        print(f"  [{'ok' if g['ok'] else 'REPROVA'}] {g['gate']}: {g['mensagem']}")
    return 0 if aprovada else 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Bateria de bots do combate V2")
    ap.add_argument("--config", required=True, type=Path)
    return executar(ap.parse_args(argv).config)


if __name__ == "__main__":
    sys.exit(main())
