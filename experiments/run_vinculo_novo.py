"""Run do vinculo B em vidas novas (docs/PLANO_ANALISE_V2_VINCULO.md, secoes 3 e 4; tarefa docs/TAREFA_V2_F0_VINCULO_NOVO.md).

    python experiments/run_vinculo_novo.py --conjunto calibracao|validacao [--dias 14] [--processos 8]

Vidas novas pelo pipeline do treino (digilab.treino_vida.simular_vida_treino, o mesmo de run_treino.py): 5 bracos
(atencioso, relapso, aleatorio, incoerente, exigente), 14 dias, orcamento igual em todos; especie e temperamento do ovo
pela semente. Pareado por semente: cada (braco, semente) roda com o vinculo de hoje ("hoje", ConfigVinculoSituacao
desligada) e com a variante B ("b", ligada). Cada vida e gravada e rejogada DO DISCO (serie do vinculo, estado e treino
conferidos). Sementes: calibracao 3101..3505; validacao 5101..5505 (uma vez, depois do plano e do codigo commitados).

Metricas (bootstrap sobre sementes com os parametros do PROTOCOLO_ARENA_V1, como no run_treino):
  primaria (gate PROPOSTO): vinculo final atencioso - aleatorio por semente, nas vidas B; passa se o IC95 ficar acima de 0;
  secundarias: vinculo por braco (B e hoje), a mesma diferenca nas vidas de hoje, exigente - atencioso, obediencia por
  braco, amostras e empurrao por componente do vinculo. Sem GPU. Saida: artifacts_v2_vinculo_novo/<conjunto>/.
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
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_VINCULO, CONFIG_VINCULO_B_LIGADA, CONFIG_VINCULO_SITUACAO  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.metrics import bootstrap_ic  # noqa: E402
from digilab.protocol import (ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, PROTOCOLO_ARENA_V1_PERSONALIDADE, hash_protocolo,  # noqa: E402
                              sha256_engine, validar_parametros_vinculo_b)
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.treino_vida import BRACOS_TREINO, fabricas_treino, orcamento_treino, simular_vida_treino  # noqa: E402

SAIDA = RAIZ / "artifacts_v2_vinculo_novo"
SEMENTES = {"calibracao": (3101, 3202, 3303, 3404, 3505), "validacao": (5101, 5202, 5303, 5404, 5505)}
MODOS = {"hoje": None, "b": CONFIG_VINCULO_B_LIGADA}
BOOT = (PROTOCOLO_ARENA_V1.v("bootstrap_reamostragens"), PROTOCOLO_ARENA_V1.v("bootstrap_semente"),
        PROTOCOLO_ARENA_V1.v("nivel_confianca"))
HASH_PERSONALIDADE = "d986ff1b9308"


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=1, sort_keys=True, default=list) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def vida(args) -> dict:
    """uma vida (braco, semente, modo): simula, grava, rejoga do disco e confere; devolve o resumo"""
    b, s, modo, dias, pasta = args
    esp, _ = ovo(s)
    t = sortear(s)
    cfg_b = MODOS[modo]
    orc, _ = orcamento_treino(dias)
    v = simular_vida_treino(b, s, dias, esp, t, cfg_vinculo_situacao=cfg_b)
    m = v.motor
    if v.interacoes != orc:
        raise RuntimeError(f"{b}@{s}.{modo}: {v.interacoes} interacoes, esperado {orc}")
    arq = Path(pasta) / "vidas" / f"{b}@{s}.{modo}.jsonl"
    _gravar(arq, m.log.para_jsonl())
    fp, fm = fabricas_treino(s, esp, t, cfg_vinculo_situacao=cfg_b)
    r = reproduzir_com_feedback(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), fp, semente=s, fabrica_motor=fm)
    if (r.resumo_treino() != m.resumo_treino() or r.estado() != m.estado() or r.vinculo.serie != m.vinculo.serie
            or r.vinculo.para_dict() != m.vinculo.para_dict()):
        raise RuntimeError(f"replay de {b}@{s}.{modo} divergiu")
    if (modo == "b") != bool(m.vinculo.cs.ligada):
        raise RuntimeError(f"{b}@{s}.{modo}: variante do vinculo errada no motor")
    if modo == "b" and m.vinculo.pedidos:
        raise RuntimeError(f"{b}@{s}.b: a variante B abriu pedido")
    serie = m.vinculo.serie
    n_comp = Counter(c for _, _, c, _ in serie)
    empurrao: dict[str, float] = {}
    antes = m.vinculo.cfg.inicial
    for _, valor, c, _ in serie:
        empurrao[c] = empurrao.get(c, 0.0) + (valor - antes)
        antes = valor
    if modo == "b" and n_comp.get("atendimento", 0):
        raise RuntimeError(f"{b}@{s}.b: amostra de atendimento na variante B")
    acoes = Counter(e.valor for e in m.log if e.tipo == "acao_usuario")
    res = m.resumo_treino()
    dados = {"braco": b, "semente": s, "modo": modo, "especie": esp, "vinculo_final": m.vinculo.valor,
             "vinculo": m.vinculo.para_dict(), "n_amostras_por_componente": dict(n_comp), "empurrao_por_componente": empurrao,
             "chaves_feedback": sorted(m.vinculo.feedbacks) if modo == "b" else len(m.vinculo.feedbacks),
             "pedidos_obediencia": m.pedidos_obediencia, "recusas": len(m.recusas),
             "obediencia_cuidado": 1.0 - len(m.recusas) / m.pedidos_obediencia if m.pedidos_obediencia else 1.0,
             "acoes_do_dono": dict(acoes), "sombria": bool(m.sombria), "sobrecarga_adulto": res["transicoes"]["adulto"]["sobrecarga"],
             "sessoes": len(m.treino.sessoes), "enroladas": m.enroladas, "dono": dict(v.dono.contagem), "interacoes": v.interacoes}
    _gravar(Path(pasta) / "vidas" / f"{b}@{s}.{modo}.treino.json", _dump(dados))
    return dados


def ic(valores) -> dict:
    return bootstrap_ic(list(valores), *BOOT)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conjunto", choices=sorted(SEMENTES), required=True)
    ap.add_argument("--dias", type=int, default=14)
    ap.add_argument("--processos", type=int, default=8)
    a = ap.parse_args(argv)
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    if not hash_protocolo(PROTOCOLO_ARENA_V1_PERSONALIDADE).startswith(HASH_PERSONALIDADE):
        raise RuntimeError("o hash do protocolo da personalidade mudou: a ConfigVinculo nao pode mudar")
    validar_parametros_vinculo_b()
    if CONFIG_VINCULO_SITUACAO.ligada:
        raise RuntimeError("a ConfigVinculoSituacao padrao precisa estar desligada")
    sementes = SEMENTES[a.conjunto]
    pasta = SAIDA / a.conjunto
    t0 = time.perf_counter()
    tarefas = [(b, s, modo, a.dias, str(pasta)) for s in sementes for b in BRACOS_TREINO for modo in MODOS]
    with ProcessPoolExecutor(a.processos) as pool:
        vidas = list(pool.map(vida, tarefas))
    t_vidas = time.perf_counter() - t0
    por = {(d["braco"], d["semente"], d["modo"]): d for d in vidas}
    if len(por) != len(tarefas):
        raise RuntimeError("vidas repetidas")

    def medias(modo: str, campo: str) -> dict:
        return {b: ic([por[(b, s, modo)][campo] for s in sementes]) for b in BRACOS_TREINO}

    def contraste(modo: str, x: str, y: str, campo: str = "vinculo_final") -> dict:
        por_semente = {s: por[(x, s, modo)][campo] - por[(y, s, modo)][campo] for s in sementes}
        return {**ic(por_semente.values()), "por_semente": por_semente}

    primaria = contraste("b", "atencioso", "aleatorio")
    gate = {"criterio": "vinculo final atencioso - aleatorio nas vidas B: limite inferior do IC95 (bootstrap sobre sementes) > 0",
            "conjunto": a.conjunto, "vale_como_gate": a.conjunto == "validacao",
            "resultado": "PASSA" if primaria["ic_inferior"] > 0 else "FALHA"}
    componentes = {}
    for modo in MODOS:
        componentes[modo] = {}
        for b in BRACOS_TREINO:
            vs = [por[(b, s, modo)] for s in sementes]
            comps = sorted({c for v in vs for c in v["n_amostras_por_componente"]})
            componentes[modo][b] = {c: {"n_medio_por_vida": sum(v["n_amostras_por_componente"].get(c, 0) for v in vs) / len(vs),
                                        "empurrao_medio": sum(v["empurrao_por_componente"].get(c, 0.0) for v in vs) / len(vs)} for c in comps}
    fontes = ("experiments/run_vinculo_novo.py", "digilab/vinculo.py", "digilab/obediencia.py", "digilab/treino_vida.py",
              "digilab/config.py", "digilab/donos.py", "digilab/metrics.py")
    out = {"descricao": __doc__.splitlines()[0], "plano": "docs/PLANO_ANALISE_V2_VINCULO.md", "conjunto": a.conjunto,
           "sementes": sementes, "bracos": BRACOS_TREINO, "dias": a.dias, "orcamento_por_vida": orcamento_treino(a.dias)[0],
           "modos": {"hoje": "ConfigVinculoSituacao desligada (o vinculo de hoje)", "b": "ConfigVinculoSituacao ligada (variante B)"},
           "config": {"vinculo": asdict(CONFIG_VINCULO), "situacao_b": asdict(CONFIG_VINCULO_B_LIGADA)},
           "bootstrap": {"reamostragens": BOOT[0], "semente": BOOT[1], "nivel": BOOT[2]},
           "gate": gate,
           "primaria": {"atencioso_menos_aleatorio_b": primaria},
           "secundarias": {
               "vinculo_final_por_braco": {modo: medias(modo, "vinculo_final") for modo in MODOS},
               "atencioso_menos_aleatorio_hoje": contraste("hoje", "atencioso", "aleatorio"),
               "exigente_menos_atencioso": {modo: contraste(modo, "exigente", "atencioso") for modo in MODOS},
               "incoerente_menos_aleatorio": {modo: contraste(modo, "incoerente", "aleatorio") for modo in MODOS},
               "obediencia_cuidado_por_braco": {modo: medias(modo, "obediencia_cuidado") for modo in MODOS},
               "componentes_do_vinculo": componentes,
               "sombrias": {modo: {b: sum(por[(b, s, modo)]["sombria"] for s in sementes) for b in BRACOS_TREINO} for modo in MODOS},
           },
           "conferencias": {"replays_do_disco_iguais": len(vidas), "engine_sha256_congelado": True,
                            "hash_personalidade_intacto": HASH_PERSONALIDADE, "variante_b_sem_pedido_nem_atendimento": True,
                            "orcamento_igual_em_todas": all(d["interacoes"] == orcamento_treino(a.dias)[0] for d in vidas)},
           "meta": {"tempo_vidas_s": t_vidas, "processos": a.processos,
                    "fontes_sha256": hashlib.sha256(b"".join((RAIZ / p).read_bytes().replace(b"\r\n", b"\n") for p in fontes)).hexdigest(),
                    "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()}}}
    _gravar(pasta / "resumo.json", _dump(out))
    print(f"{a.conjunto}: {len(vidas)} vidas em {t_vidas:.0f} s")
    for modo in MODOS:
        print(f"  [{modo}] vinculo final: " + "  ".join(f"{b} {out['secundarias']['vinculo_final_por_braco'][modo][b]['media']:.3f}" for b in BRACOS_TREINO))
    p = primaria
    print(f"  atencioso - aleatorio (B): {p['media']:+.3f} [{p['ic_inferior']:+.3f}; {p['ic_superior']:+.3f}]  por semente "
          + " ".join(f"{v:+.3f}" for v in p["por_semente"].values()))
    h = out["secundarias"]["atencioso_menos_aleatorio_hoje"]
    print(f"  atencioso - aleatorio (hoje): {h['media']:+.3f} [{h['ic_inferior']:+.3f}; {h['ic_superior']:+.3f}]")
    print(f"GATE ({a.conjunto}{'' if gate['vale_como_gate'] else ', nao vale como gate'}): {gate['resultado']}")
    return 0 if gate["resultado"] == "PASSA" else 2


if __name__ == "__main__":
    raise SystemExit(main())
