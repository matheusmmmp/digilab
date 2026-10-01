"""TAREFA_ANALISE_PODER, Etapa 1: piloto (ovos pareados, 5 bracos, condicao neutra e real).

    python experiments/run_poder.py --processos 8
    python experiments/run_poder.py --ovos 50001 --partidas 4 --replicas 2 --painel 2 --saida <pasta>   # fumaca

Config: experiments/configs/poder_pesquisa.json (arena V21C normalizada, sementes de piloto, M0, N0).

1. Vidas: cada ovo de piloto gera um pet em cada braco (run_treino: personalidade completa + treino, 14 dias,
   orcamento igual). Log gravado e rejogado DO DISCO; evolucao ate adulto.
2. Para cada variante de condicao (neutra, real), com os MESMOS pets e as MESMAS sementes de partida:
   A  confronto direto: os 10 pares de bracos de cada ovo, M partidas por par (lados trocados na metade);
      o par principal (atencioso x aleatorio) repetido em R replicas com sorteios de partida diferentes
      (pets fixos) -> variancia devida so as partidas;
   B  painel fixo: cada pet contra os 8 bots adultos canonicos x 4 especies (bateria V21C), P partidas por
      bot, sementes que so dependem do ovo, do bot e de k (as mesmas para os 5 bracos do ovo).
Guarda o resultado de CADA partida (pontos) para a Etapa 2 estimar variancias sem aproximacao, e os tempos
de cada fase (8 processos) para o modelo de custo da Etapa 4.

Saida em artifacts_poder/piloto/ (um arquivo por variante + pets + tempos).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.bots import FORMAS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.combate_v2.v21.regras import Regras  # noqa: E402
from digilab.config import (CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, ConfigArenaPesquisa,  # noqa: E402
                            ConfigCombateV2C, ConfigCombateV21C, ConfigCombateV21D)
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import evoluir, ovo  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, derivar_semente, sha256_engine  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.treino_vida import BRACOS_TREINO, fabricas_treino, orcamento_treino, simular_vida_treino  # noqa: E402
from run_treino import lutador_pet  # noqa: E402

CFG_PADRAO = RAIZ / "experiments" / "configs" / "poder_pesquisa.json"
PRINCIPAL = ("atencioso", "aleatorio")


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def regras_de(cfg: dict) -> Regras:
    """Regras da config. Com alguma chave da ConfigCombateV21D em `regras_v21` (docs/PLANO_ANALISE_V21D.md) a V2.1 e a
    V21D; sem nenhuma, a V21C de sempre (as runs antigas nao mudam)."""
    from dataclasses import asdict as _a, fields as _f
    c = cfg["combate"]
    chaves_v21d = {x.name for x in _f(ConfigCombateV21D)} - {x.name for x in _f(ConfigCombateV21C)}
    cls = ConfigCombateV21D if set(c["regras_v21"]) & chaves_v21d else ConfigCombateV21C
    return Regras(base=ConfigCombateV2C(**{**_a(CONFIG_COMBATE_V2), **c["regras_base"]}),
                  v21=cls(**{**_a(CONFIG_COMBATE_V21), **c["regras_v21"]}))


# ------------------------------------------------------------------ 1. vidas
def _vida(args):
    """Uma vida (braco, ovo): simula, grava, rejoga do disco, evolui. Roda num processo do pool."""
    b, s, dias, saida = args
    t0 = time.perf_counter()
    esp, _ = ovo(s)
    tmp = sortear(s)
    v = simular_vida_treino(b, s, dias, esp, tmp)
    m = v.motor
    orc, _ = orcamento_treino(dias)
    if v.interacoes != orc:
        raise RuntimeError(f"{b}@{s}: {v.interacoes} interacoes, esperado {orc}")
    arq = Path(saida) / "vidas" / f"{b}@{s}.jsonl"
    _gravar(arq, m.log.para_jsonl())
    fp, fm = fabricas_treino(s, esp, tmp)
    r = reproduzir_com_feedback(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), fp, semente=s, fabrica_motor=fm)
    if r.resumo_treino() != m.resumo_treino() or r.estado() != m.estado() or r.vinculo.serie != m.vinculo.serie:
        raise RuntimeError(f"replay de {b}@{s} divergiu")
    sondas = (PROTOCOLO_ARENA_V1.v("estados_sonda"), PROTOCOLO_ARENA_V1.v("amostras_por_estado"),
              PROTOCOLO_ARENA_V1.v("semente_sonda"))
    ev = evoluir(m.log, fp, s, *sondas, m.estado()["saude"], fabrica_motor=fm, sombria=bool(m.sombria))
    dados = {"braco": b, "ovo": s, "especie": esp, "forma": ev.para_dict()["forma"], "sombria": bool(m.sombria),
             "condicao": ev.condicao, "saude_final": m.estado()["saude"], "treino_total": m.treino.pontos and
             sum(m.treino.pontos.values()), "vinculo_final": m.vinculo.valor}
    return (b, s), ev, dict(m.treino.pontos), dados, time.perf_counter() - t0


# ------------------------------------------------------------------ 2. partidas
def _pontos(a, b, rotulo, n, r) -> list[float]:
    """Pontos de `a` em n partidas contra b, lados trocados na metade (mesma convencao do run_treino)."""
    out = []
    for k in range(n):
        sp = derivar_semente(rotulo, a.nome, b.nome, k)
        out.append(jogar(a, b, sp, r).pontos_a if k < n // 2 else 1.0 - jogar(b, a, sp, r).pontos_a)
    return out


def _partidas_do_ovo(args):
    """Todas as partidas de um ovo numa variante: pares A, replicas do par principal e o painel B."""
    s, pets, cfg, neutra, m_a, reps, m_b, rotulo = args
    t0 = time.perf_counter()
    r = regras_de(cfg)
    carena = ConfigArenaPesquisa(condicao_neutra=neutra)
    lut = {b: lutador_pet(f"{b}@{s}", ev, pontos, False, carena, r.v21) for b, (ev, pontos) in pets.items()}
    bracos = [b for b in BRACOS_TREINO if b in lut]
    a_pares, n_part = {}, 0
    for i, x in enumerate(bracos):
        for y in bracos[i + 1:]:
            a_pares[f"{x}|{y}"] = _pontos(lut[x], lut[y], f"{rotulo}|A|{s}", m_a, r)
            n_part += m_a
    x, y = PRINCIPAL
    replicas = [_pontos(lut[x], lut[y], f"{rotulo}|A-rep{k}|{s}", m_a, r) for k in range(reps)]
    n_part += reps * m_a
    painel = {}
    for esp in CONFIG_CATALOGO.especies_ativas:
        for f in FORMAS:
            bot = lutador_adulto(f, esp, r.v21, nome=f"painel:{f}@{esp}")
            for b in bracos:
                # a semente depende do ovo, do bot e de k, nao do braco: os 5 bracos enfrentam as mesmas partidas
                pts = []
                for k in range(m_b):
                    sp = derivar_semente(f"{rotulo}|B|{s}", bot.nome, k)
                    pts.append(jogar(lut[b], bot, sp, r).pontos_a if k < m_b // 2 else 1.0 - jogar(bot, lut[b], sp, r).pontos_a)
                painel.setdefault(b, {})[bot.nome] = pts
                n_part += m_b
    return s, {"A": a_pares, "A_replicas_principal": replicas, "B": painel}, n_part, time.perf_counter() - t0


def executar(cfg: dict, saida: Path, ovos: list[int], m_a: int, reps: int, m_b: int, processos: int | None,
             rotulo: str | None = None) -> dict:
    """rotulo: rotulo das sementes de partida (padrao: o do piloto; a confirmatoria usa o proprio)."""
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    if m_a % 2 or m_b % 2:
        raise ValueError("partidas precisa ser par (lados trocados na metade)")
    saida.mkdir(parents=True, exist_ok=True)
    rotulo = rotulo or cfg["rotulo_partidas_piloto"]
    bracos = list(cfg["bracos_principais"]) + list(cfg["bracos_secundarios"])
    if sorted(bracos) != sorted(BRACOS_TREINO):
        raise ValueError(f"bracos do config {bracos} != BRACOS_TREINO")
    tempos = {"processos": processos}
    with ProcessPoolExecutor(processos) as pool:
        t0 = time.perf_counter()
        vidas = list(pool.map(_vida, [(b, s, cfg["dias"], str(saida)) for s in ovos for b in BRACOS_TREINO]))
        tempos["vidas_s"] = time.perf_counter() - t0
        tempos["vida_media_s_por_processo"] = sum(v[4] for v in vidas) / len(vidas)
        pets = {k: (ev, pontos) for k, ev, pontos, _, _ in vidas}
        dados = {f"{b}@{s}": d for (b, s), _, _, d, _ in vidas}
        _gravar(saida / "pets.json", _dump(dados))
        print(f"  {len(vidas)} vidas em {tempos['vidas_s']:.0f} s", flush=True)
        resultados = {}
        for nome, neutra in sorted(cfg["variantes_condicao"].items()):
            t1 = time.perf_counter()
            por_ovo = {}
            n_total = 0
            for s, res, n_part, _ in pool.map(_partidas_do_ovo, [
                    (s, {b: pets[(b, s)] for b in BRACOS_TREINO}, cfg, neutra, m_a, reps, m_b, rotulo) for s in ovos]):
                por_ovo[str(s)] = res
                n_total += n_part
            dt = time.perf_counter() - t1
            tempos[f"partidas_{nome}_s"] = dt
            tempos[f"partidas_{nome}_n"] = n_total
            tempos[f"segundos_por_partida_{nome}"] = dt / n_total
            resultados[nome] = por_ovo
            _gravar(saida / f"partidas_{nome}.json", _dump({"variante": nome, "condicao_neutra": neutra, "por_ovo": por_ovo}))
            print(f"  variante {nome}: {n_total} partidas em {dt:.0f} s", flush=True)
    meta = {"descricao": __doc__.strip().splitlines()[0], "config": cfg, "ovos": ovos, "M_A": m_a, "replicas_principal": reps,
            "M_B_por_bot": m_b, "painel": [f"{f}@{e}" for e in CONFIG_CATALOGO.especies_ativas for f in FORMAS],
            "tempos": tempos,
            "fontes_sha256": hashlib.sha256(b"".join((RAIZ / p).read_bytes().replace(b"\r\n", b"\n") for p in (
                "experiments/run_poder.py", "experiments/run_treino.py", "digilab/evolucao.py", "digilab/config.py",
                "digilab/combate_v2/v21/catalogo.py", "digilab/combate_v2/v21/regras.py"))).hexdigest(),
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()}}
    _gravar(saida / "meta.json", _dump(meta))
    return {"meta": meta, "resultados": resultados, "pets": dados}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=str(CFG_PADRAO))
    ap.add_argument("--saida", default=str(RAIZ / "artifacts_poder" / "piloto"))
    ap.add_argument("--ovos", type=int, nargs="*", help="padrao: sementes_piloto do config")
    ap.add_argument("--partidas", type=int, help="M por par no desenho A (padrao: M0 do config)")
    ap.add_argument("--replicas", type=int, default=10, help="replicas do par principal (sorteio de partida)")
    ap.add_argument("--painel", type=int, default=20, help="partidas por bot do painel (desenho B)")
    ap.add_argument("--processos", type=int, default=None)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    ovos = a.ovos or cfg["sementes_piloto"]
    antigas = set(cfg["sementes_antigas"]) | set(cfg["sementes_confirmatorias"])
    if set(ovos) & antigas:
        raise ValueError(f"ovos do piloto colidem com sementes antigas/confirmatorias: {sorted(set(ovos) & antigas)}")
    executar(cfg, Path(a.saida), ovos, a.partidas or cfg["M0_partidas_por_par"], a.replicas, a.painel,
             a.processos or cfg["processos"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
