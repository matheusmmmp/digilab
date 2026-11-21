"""PLASTICIDADE_EVOLUIDA, o C0: a triagem do critico, antes do E0 (docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, secao 9.1; PE-8 a PE-11,
APROVADAS pelo Matheus em 2026-11-21). E uma triagem, sem gate: nada confirmatorio sai daqui.

Pergunta: com um critico (o erro de diferenca temporal no lugar da recompensa crua no P2), aprender passa a valer mais para o pet?

Os tres bracos, no pet v38 do E0 (`run_v3_plasticidade_e0.viver`, a config de hoje), nas mesmas 6 celulas e 10 unidades do E0 (as bases
110001...110010), 14 dias: 3 x 6 x 10 = 180 vidas (a secao 9.1 da tarefa fala em 360; a conta dos tres bracos da 180, D-PE-C0-5).
  - HOJE: o pet v38 de hoje (o APRENDE do E0), byte a byte o `pv2.viver("HOJE", ..., v38=True)`;
  - CRITICO: o mesmo pet com a `ConfigCritico` ligada (`digilab/digibrain/plast.py`);
  - CONGELADO: o mesmo pet com o `p1` e o `p2` desligados, como no E0.

As medidas (secao 9.1), pelo `digilab/metrics.py`: o "Tempo bem" (dias 1 a 14); o valor do aprendizado sem o critico (HOJE - CONGELADO)
e com ele (CRITICO - CONGELADO), pareados por unidade, e o contraste entre os dois, com o IC95 pelo t (`sensibilidade_um_por_vez`); a
fracao `aprendido_decidiu`; a parte do credito do habito que vai a linha do dormir (`credito_do_habito_por_linha`); a entropia do
sorteio (PE-10, `entropia_do_sorteio`); ao lado, a saude e a exaustao dos dias 8 a 14.

A leitura (secao 9.1, escrita antes), descritiva: "o critico aumenta o valor do aprendizado" (o IC95 do contraste todo acima de 0) ou
"nada muda" (o IC95 contem o 0). O IC95 todo abaixo de 0 nao esta na tabela e volta ao Matheus. O corte para uma confirmacao e o da
PQ3-9 do pet que pensa (o IC95 acima de 0 e a media em 0,032 ou mais), so informado.

As conferencias de cada vida, que falham alto: o replay pelo log (G1), o T-CENARIO-1, as do E0 (`conferir_vida`: o pet, o braco e o
critico so onde a vida o pediu), a C-HOJE no braco HOJE e, no CRITICO, a contabilidade do credito (cada opcao guardada foi fechada uma
vez, ou ficou pendente no fim da vida).

A trava: sem o "APROVADO pelo Matheus" na tarefa, sem a faixa em FAIXAS_RESERVADAS, fora das 10 bases, com a pasta de saida existente,
sem o `tools/pre_run.py` e sem disco, a run se recusa. A fumaca (as sementes dos testes) so serve ao custo.

  python experiments/run_v3_plasticidade_c0.py --config experiments/configs/v3_plasticidade_c0/run.json --processos 4
  python experiments/run_v3_plasticidade_c0.py --config experiments/configs/v3_plasticidade_c0/fumaca.json --saida <pasta>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import pv2  # noqa: E402
import run_v3_plasticidade_e0 as E0  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_CRITICO_LIGADA  # noqa: E402

orq, C4, V, ra = E0.orq, E0.C4, E0.V, E0.ra
PLANO = E0.PLANO                                              # a leitura escrita antes esta na secao 9.1 da tarefa
ORQUESTRADOR = "experiments/run_v3_plasticidade_c0.py"
FASE = "plasticidade_c0"
SAIDA = "artifacts_v3_plasticidade/c0"
PREFIXO, DIAS, MAX_PROCESSOS, NIVEL = E0.PREFIXO, E0.DIAS, E0.MAX_PROCESSOS, E0.NIVEL
CELULAS, N_BASES, K_POR_BASE = E0.CELULAS, E0.N_BASES, E0.K_POR_BASE
HOJE, CRITICO, CONGELADO = "HOJE", "CRITICO", "CONGELADO"
BRACOS = (HOJE, CRITICO, CONGELADO)
CRITICO_DO_C0 = CONFIG_CRITICO_LIGADA                         # PE-9: o eta_v e o gamma da config, PROPOSTOS, SEM FONTE
# o braco -> (o braco do E0, a ConfigCritico)
MONTAGEM = {HOJE: (E0.APRENDE, None), CRITICO: (E0.APRENDE, CRITICO_DO_C0), CONGELADO: (E0.CONGELADO, None)}
N_VIDAS = len(BRACOS) * len(CELULAS) * N_BASES * K_POR_BASE   # 180
MEDIDA = "tempo_bem"
AO_LADO = ("aprendido_decidiu", "credito_dormir", "credito_dormir_n", "entropia_bits", "entropia_frac_baixa", "saude_8_14", "exaustao_8_14",
           "habito_abs")
DELTA_PQ3_9 = 0.032                                           # o corte da PQ3-9 do pet que pensa (o delta da C4); so informado
L_AUMENTA = "o critico aumenta o valor do aprendizado"
L_NADA = "nada muda"
L_FORA = "o critico diminui o valor do aprendizado: fora da leitura da secao 9.1, volta ao Matheus como esta"
L_SEM_IC = "sem leitura: falta o IC do contraste"
SEGUE = {L_AUMENTA: "o E0 roda com o critico ligado nos dois bracos, e o eta_v entra entre os genes",
         L_NADA: "o E0 roda como esta, e a leitura 'estrutural' ganha forca",
         L_FORA: "nenhum passo previsto: o caso vai ao Matheus",
         L_SEM_IC: "nenhum passo: o resultado nao tem o que a regra le"}
NAO_DIZ = ["nada confirmatorio: e uma triagem, com 10 unidades",
           "nada sobre outros valores do eta_v e do gamma: o C0 testa um ponto so",
           "nada sobre donos e lugares fora das seis celulas",
           "nada sobre o jogo: a chave fica desligada nele, e o pet e o v38 do Python"]


class C0Divergiu(RuntimeError):
    """uma conferencia de uma vida falhou, ou a analise ficou sem o que a regra le"""


# ================================================================== as vidas
def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int = E0.ORCAMENTO_POR_DIA) -> tuple:
    """uma vida do braco: (o motor, o registro, as fabricas)"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    e0, critico = MONTAGEM[braco]
    return E0.viver(E0.HOJE, e0, dono, lugar, semente, dias, orcamento_por_dia, critico)


def conferir_critico(nome: str, registro) -> dict:
    """a contabilidade do credito no braco CRITICO (falha alto): cada opcao guardada pelo `creditar` foi fechada uma vez pelo
    `fechar_pendentes`, ou esta pendente no fim da vida; a soma dos |delta H| dos registros e a do habito. Devolve o que o V aprendeu"""
    c = orq.cerebro_de(registro)
    plast = c.m.plast
    guardadas = sum(1 for m in c.motivos for cr in m["creditos"] + (m["consequencia"] or {}).get("creditos", []) if cr.get("pendente"))
    fechadas = [f for m in c.motivos for f in m["critico"]["fechados"] + [cr for cr in m["creditos"] if not cr.get("pendente")]]
    if any(f["regra"] != "P2-critico" for f in fechadas):
        raise C0Divergiu(f"{nome}: um credito do P2 sem o critico numa vida com ele")
    if guardadas != len(fechadas) + len(plast.pendentes) or plast.creditos != len(fechadas):
        raise C0Divergiu(f"{nome}: {guardadas} opcoes guardadas, {len(fechadas)} fechadas e {len(plast.pendentes)} pendentes")
    return {"v_abs": sum(abs(v) for v in plast.V), "fechadas": len(fechadas), "pendentes_no_fim": len(plast.pendentes),
            "delta_abs_medio": None if not fechadas else sum(abs(f["delta"]) for f in fechadas) / len(fechadas),
            "r_abs_medio": None if not fechadas else sum(abs(f["r_n"]) for f in fechadas) / len(fechadas),
            "creditos_que_movem": sum(1 for f in fechadas if f["abs"] > 0)}


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    nome = f"{braco}|{dono}|{lugar}|{semente}"
    e0, critico = MONTAGEM[braco]
    motor, registro, fab = viver(braco, dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"])
    texto = motor.log.para_jsonl()
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{semente}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, semente, arquivo.read_text(encoding="utf-8"))          # G1
    orq.conferir_cenario(motor, registro)
    E0.conferir_vida(E0.HOJE, e0, motor, registro, critico)
    if braco == HOJE:                                                                      # C-HOJE
        hoje, registro_hoje, _ = pv2.viver("HOJE", dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"], v38=True)
        if hoje.log.para_jsonl() != texto or E0.assinatura_da_vida(hoje, registro_hoje) != E0.assinatura_da_vida(motor, registro):
            raise C0Divergiu(f"C-HOJE, {nome}: o braco HOJE nao e o pet v38 de hoje")
    out = {"vida": nome, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"], "k": unidade["k"],
           **E0.medir(cfg["dias"], motor, registro), "critico": conferir_critico(nome, registro) if braco == CRITICO else None,
           "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(), "vida_sha256": E0.assinatura_da_vida(motor, registro)}
    out["custo"] = {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}
    return json.loads(json.dumps(out))


def tarefa(cfg: dict, unidade: dict, dono: str, lugar: str, pasta: str) -> list[dict]:
    """uma celula numa unidade: os tres bracos"""
    return [_vida(cfg, braco, dono, lugar, unidade, pasta) for braco in BRACOS]


# ================================================================== a analise (secao 9.1 da tarefa, escrita antes)
def por_unidade(registros: list[dict], medida: str, com_none: bool = False) -> dict:
    """braco -> semente -> a media da medida nas seis celulas; falha alto com vida repetida ou faltando. `com_none` (so nos descritivos
    ao lado): a celula sem valor fica fora da media, e a unidade sem nenhuma fica None"""
    idx: dict = {}
    for r in registros:
        chave = (r["braco"], r["semente"], r["dono"], r["lugar"])
        if chave in idx:
            raise C0Divergiu(f"vida repetida: {chave}")
        idx[chave] = r[medida]
    sementes = sorted({r["semente"] for r in registros})
    if len(idx) != len(BRACOS) * len(sementes) * len(CELULAS):
        raise C0Divergiu(f"{len(idx)} vidas: sao {len(BRACOS)} bracos x {len(sementes)} unidades x {len(CELULAS)} celulas")
    return {b: {s: E0._media_das_celulas([idx[(b, s, d, lugar)] for d, lugar in CELULAS], com_none) for s in sementes} for b in BRACOS}


def ler(resumo: dict) -> dict:
    """a leitura da secao 9.1, pelo IC95 do contraste do valor do aprendizado (com o critico menos sem ele), pareado por unidade"""
    c = resumo["configs"]["critico"]["contraste_valor"]
    if c["ic_inferior"] is None:
        return {"leitura": L_SEM_IC, "segue": SEGUE[L_SEM_IC], "corte_pq3_9": None}
    leitura = L_AUMENTA if c["ic_inferior"] > 0.0 else L_FORA if c["ic_superior"] < 0.0 else L_NADA
    return {"leitura": leitura, "segue": SEGUE[leitura],
            "corte_pq3_9": {"delta": DELTA_PQ3_9, "passa": c["ic_inferior"] > 0.0 and c["media"] >= DELTA_PQ3_9,
                            "texto": "o corte para uma confirmacao (PQ3-9 do pet que pensa): o IC95 acima de 0 e a media em delta ou mais; "
                                     "so informado, o C0 e triagem"}}


def analisar(registros: list[dict]) -> dict:
    pu = por_unidade(registros, MEDIDA)
    # as duas "configs" do resumo: o aprendiz sem o critico e com ele, contra o mesmo CONGELADO; a referencia e o de hoje
    resumo = met.sensibilidade_um_por_vez({"hoje": {"APRENDE": pu[HOJE], "CONGELADO": pu[CONGELADO]},
                                           "critico": {"APRENDE": pu[CRITICO], "CONGELADO": pu[CONGELADO]}}, "hoje", nivel=NIVEL)
    ao_lado = {}
    for m in AO_LADO:
        por = por_unidade(registros, m, com_none=True)
        ao_lado[m] = {b: E0._media_das_celulas(list(v.values()), True) for b, v in por.items()}
    crit = [r["critico"] for r in registros if r["braco"] == CRITICO]
    idx = {(r["braco"], r["semente"], r["dono"], r["lugar"]): r["vida_sha256"] for r in registros}
    iguais = sum(1 for (b, *resto), sha in idx.items() if b == CRITICO and sha == idx[(HOJE, *resto)])
    r = resumo["configs"]
    return {"medida": MEDIDA, "unidades": resumo["unidades"], "celulas": [list(c) for c in CELULAS], "critico": asdict(CRITICO_DO_C0),
            "tempo_bem": {HOJE: r["hoje"]["aprende"], CRITICO: r["critico"]["aprende"], CONGELADO: r["hoje"]["congelado"]},
            "valor_do_aprendizado": {"sem_o_critico": r["hoje"]["valor"], "com_o_critico": r["critico"]["valor"],
                                     "contraste": r["critico"]["contraste_valor"]},
            "ao_lado": ao_lado, "entropia": {"limiar_bits": met.LIMIAR_ENTROPIA_BAIXA},
            "o_critico_nas_vidas": {"vidas": len(crit), "vidas_iguais_as_de_hoje": iguais,
                                    "v_abs_medio": sum(c["v_abs"] for c in crit) / len(crit),
                                    "creditos_que_movem": sum(c["creditos_que_movem"] for c in crit),
                                    "fechadas": sum(c["fechadas"] for c in crit), "pendentes_no_fim": sum(c["pendentes_no_fim"] for c in crit)},
            "leitura": ler(resumo), "nao_diz": NAO_DIZ}


# ================================================================== a trava e a run
def modo_da_config(cfg: dict) -> str:
    """a trava do E0 (`E0.modo_da_config`: as chaves, a faixa reservada, as 10 bases, o plano APROVADO, os 14 dias), com a fase do C0 e
    sem o subconjunto de configs"""
    if "configs" in cfg:
        raise ValueError("o C0 nao tem configs: sao os tres bracos na config de hoje")
    return E0.modo_da_config(cfg, FASE)


def projecao_h(custos: dict, processos: int = MAX_PROCESSOS) -> float:
    por_vida = sum(c["vida_parede"] for c in custos.values()) / len(custos)
    return N_VIDAS * por_vida / processos / 3600


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez)")
    livre = ra.exigir_disco(RAIZ)
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "e0_sha256": rc._sha_arquivo(Path(E0.__file__)),
            "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {"config_digibrain": vars(E0.config_digibrain(e0)), "critico": None if cr is None else asdict(cr)}
                       for b, (e0, cr) in MONTAGEM.items()},
            "faixa": cfg["faixa"], "nivel": NIVEL, "delta_pq3_9": DELTA_PQ3_9, "limiar_entropia_bits": met.LIMIAR_ENTROPIA_BAIXA,
            "disco_livre_gb": livre,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "corpo.py",
                                                                         "motor_corpo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    tarefas = [(tarefa, (cfg, u, dono, lugar, str(pasta))) for u in unidades for dono, lugar in CELULAS]
    registros = [r for s in rc._executar(tarefas, processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    registros.sort(key=lambda r: r["vida"])
    custos = {r["vida"]: r.pop("custo") for r in registros}            # o relogio fora do medidas.json
    bv._gravar(pasta / "medidas.json", bv._dump(registros))
    bv._gravar(pasta / "custos.json", bv._dump(custos))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    if modo == "fumaca":                                      # a fumaca so serve ao custo: nenhuma medida dela e lida
        resultado = {"modo": modo, "fase": FASE, "vidas": len(lidos), "bracos": list(BRACOS), "conferencias": "passam"}
    else:
        resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    meta["pasta_crua_apagada"] = {"vidas": C4.conferir_e_apagar(pasta / "vidas", pasta / "vidas.tar.gz")}
    meta["custo"] = {"vida_parede_media_s": sum(c["vida_parede"] for c in custos.values()) / len(custos),
                     "vida_cpu_media_s": sum(c["vida_cpu"] for c in custos.values()) / len(custos),
                     "projecao_parede_h_4_processos": projecao_h(custos), "vidas_da_run": N_VIDAS}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "custos.json", "resultado.json", "vidas.tar.gz")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    res = r["resultado"]
    if res["modo"] == "fumaca":
        return json.dumps({**res, "custo": r["meta"]["custo"]}, indent=1, ensure_ascii=True, default=str)
    return json.dumps({"vidas": res["vidas"], "leitura": res["leitura"], "valor_do_aprendizado": res["valor_do_aprendizado"]},
                      indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", required=True)
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--processos", type=int, default=1)
    a = ap_.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)       # tambem na fumaca: ela vive vidas, e a maquina leva uma carga por vez
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)))


if __name__ == "__main__":
    main()
