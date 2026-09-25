"""Orquestrador da arena (Etapa 6).

    python experiments/run_arena.py --config experiments/configs/canonico.json

Fluxo:
  1. preflight   - ambiente, engine intocado, protocolo valido, replay v0
  2. vidas       - cada braco x cada semente, politica do braco (protocolo), orcamento imposto
  3. replay      - toda vida e reconstruida DO DISCO e comparada bit a bit
  4. torneio     - round-robin entre todos os pets
  5. replay      - toda partida e rejogada com os pets reconstruidos
  6. metricas    - so via digilab.metrics
  7. gate        - pode REPROVAR a run; motivo gravado

Divergencia de replay nao e aviso: levanta erro e para tudo.

O protocolo sai do campo `protocolo` do config (padrao arena-v1). Em arena-v1
todo braco usa bandit e o rotulo do braco e o nome do dono. Em
arena-v1-ablacao os bracos sao dono x politica (ex.: atencioso-instinto) e a
politica de cada braco vem do protocolo, nunca de codigo fixo aqui.

Saida (em `saida` do config): metrics.json, divergence.json, matches.csv,
partidas.jsonl, vidas/*.jsonl, vidas/*.politica.json, preflight.json.
Codigo de saida: 0 APROVADA, 2 REPROVADA, excecao em falha de execucao.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import LogDeEventos, Motor, reproduzir  # noqa: E402
from digilab.arena import Lutador, ResultadoPartida, lutar, stats_de_tracos  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import (  # noqa: E402
    bootstrap_ic,
    bradley_terry,
    divergencia_politicas,
    efeito_do_treino,
    estados_sonda,
    finais,
    taxa_vitoria,
)
from digilab.memoria import PoliticaBanditMemoria  # noqa: E402
from digilab.memoria_espacos import PoliticaBanditEspacos  # noqa: E402
from digilab.policies import PoliticaBandit  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import (  # noqa: E402
    ENGINE_SHA256_V0,
    PROTOCOLO_ARENA_V1,
    PROTOCOLOS,
    Protocolo,
    ProtocoloAblacao,
    ProtocoloMemoria,
    ProtocoloMemoriaEspacos,
    bracos_do_protocolo,
    configs_congelados,
    derivar_semente,
    sha256_engine,
)
from digilab.tracos import tracos_de_acoes  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

CHAVES_CONFIG = {"saida", "protocolo_substituicoes", "descricao", "protocolo"}

# politica de comportamento por nome de protocolo -> fabrica(cfg)
FABRICAS_POLITICA = {
    "bandit": lambda cfg=None: PoliticaBandit(cfg),
    "instinto": lambda cfg=None: PoliticaInstinto(cfg),
    "bandit_memoria": lambda cfg=None: PoliticaBanditMemoria(cfg),
    "bandit_espacos": lambda cfg=None: PoliticaBanditEspacos(cfg),
}
# politicas que aprendem: o gate de divergencia so olha pares delas
APRENDIZES = {"bandit", "bandit_memoria", "bandit_espacos"}


class PreflightFalhou(RuntimeError):
    pass


class ReplayDivergiu(RuntimeError):
    pass


class OrcamentoDesigual(RuntimeError):
    pass


class DivergenciaInstintoNaoNula(RuntimeError):
    """Pets com PoliticaInstinto nao aprendem: a sonda (numeros aleatorios
    comuns) tem que dar JSD exatamente zero entre eles. Qualquer outro valor
    e bug no orquestrador, na sonda ou na politica."""


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


# ------------------------------------------------------------------ config


def carregar_config(caminho: Path) -> tuple[Protocolo, Path, dict]:
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    desconhecidas = set(bruto) - CHAVES_CONFIG
    if desconhecidas:
        raise KeyError(f"chaves desconhecidas no config: {sorted(desconhecidas)}")
    if "saida" not in bruto:
        raise KeyError("config sem 'saida'")
    nome = bruto.get("protocolo", PROTOCOLO_ARENA_V1.versao)
    if nome not in PROTOCOLOS:
        raise KeyError(f"protocolo desconhecido no config: {nome!r}; validos: {sorted(PROTOCOLOS)}")
    base = PROTOCOLOS[nome]
    subs = bruto.get("protocolo_substituicoes", {})
    protocolo = base.com_substituicoes(subs) if subs else base
    saida = Path(bruto["saida"])
    if not saida.is_absolute():
        saida = RAIZ / saida
    return protocolo, saida, bruto


# ------------------------------------------------------------------ preflight


def _imports_externos(pacote: Path) -> set[str]:
    """Imports absolutos do pacote que nao sao stdlib nem o proprio pacote."""
    import ast

    fora: set[str] = set()
    for arq in pacote.rglob("*.py"):
        for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8"))):
            if isinstance(no, ast.Import):
                raizes = [a.name.split(".")[0] for a in no.names]
            elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
                raizes = [no.module.split(".")[0]]
            else:
                continue
            for r in raizes:
                if r not in sys.stdlib_module_names and r != "digilab":
                    fora.add(f"{arq.name}:{r}")
    return fora


def preflight(protocolo: Protocolo, saida: Path) -> dict:
    checagens: list[dict] = []

    def checar(nome: str, ok: bool, detalhe: str) -> None:
        checagens.append({"checagem": nome, "ok": bool(ok), "detalhe": detalhe})

    checar("python>=3.10", sys.version_info >= (3, 10), platform.python_version())

    externos = sorted(_imports_externos(RAIZ / "digilab"))
    checar("digilab so usa stdlib", len(externos) == 0, f"imports fora da stdlib: {externos}")

    h = sha256_engine()
    checar("engine.py intocado", h == ENGINE_SHA256_V0, h)

    try:
        protocolo.validar()
        checar("protocolo valido", True, protocolo.versao)
    except Exception as e:  # registra e reprova o preflight, nao engole
        checar("protocolo valido", False, repr(e))

    try:
        saida.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=saida, delete=True):
            pass
        checar("saida gravavel", True, str(saida))
    except OSError as e:
        checar("saida gravavel", False, repr(e))

    m = Motor(semente=1)
    for _ in range(24):
        m.avancar(60)
    checar("replay v0 bit a bit", reproduzir(m.log, semente=1).estado() == m.estado(), "motor v0, 1 dia")

    resultado = {"ok": all(c["ok"] for c in checagens), "checagens": checagens}
    if saida.exists():
        (saida / "preflight.json").write_text(_dump(resultado), encoding="utf-8", newline="\n")
    if not resultado["ok"]:
        falhas = [c for c in checagens if not c["ok"]]
        raise PreflightFalhou(f"preflight reprovado: {falhas}")
    return resultado


# ------------------------------------------------------------------ execucao


def executar(protocolo: Protocolo, saida: Path) -> int:
    pre = preflight(protocolo, saida)
    dir_vidas = saida / "vidas"
    dir_vidas.mkdir(parents=True, exist_ok=True)

    sementes = list(protocolo.v("sementes_coorte"))
    bracos_exec = bracos_do_protocolo(protocolo)
    bracos = [rotulo for rotulo, _, _ in bracos_exec]
    dono_de_braco = {rotulo: dono for rotulo, dono, _ in bracos_exec}
    politica_de_braco = {rotulo: pol for rotulo, _, pol in bracos_exec}
    for pol in politica_de_braco.values():
        if pol not in FABRICAS_POLITICA:
            raise KeyError(f"politica sem fabrica no orquestrador: {pol!r}")
    dias = protocolo.v("dias_simulados")
    orcamento = protocolo.v("orcamento_interacoes")

    # ---------------------------------------------------------- 2. vidas
    vidas = {}
    for s in sementes:
        for b in bracos:
            dono = dono_de_braco[b]
            politica = FABRICAS_POLITICA[politica_de_braco[b]]()
            v = simular_vida(b, criar_dono(dono), politica, s, dias, orcamento, rotulo_dono=dono)
            vidas[v.nome] = v
            (dir_vidas / f"{v.nome}.jsonl").write_text(v.motor.log.para_jsonl(), encoding="utf-8", newline="\n")
            (dir_vidas / f"{v.nome}.politica.json").write_text(
                json.dumps(v.motor.politica.estado_interno(), sort_keys=True), encoding="utf-8", newline="\n"
            )

    interacoes = {
        n: sum(1 for e in v.motor.log if e.tipo == "acao_usuario") for n, v in sorted(vidas.items())
    }
    if set(interacoes.values()) != {orcamento}:
        raise OrcamentoDesigual(f"interacoes por pet diferem do orcamento {orcamento}: {interacoes}")

    # ---------------------------------------------------------- 3. replay das vidas, do disco
    reconstruidos = {}
    for nome, v in sorted(vidas.items()):
        log = LogDeEventos.de_jsonl((dir_vidas / f"{nome}.jsonl").read_text(encoding="utf-8"))
        r = reproduzir_com_feedback(log, FABRICAS_POLITICA[politica_de_braco[v.braco]], semente=v.semente_coorte)
        salvo = json.loads((dir_vidas / f"{nome}.politica.json").read_text(encoding="utf-8"))
        if r.estado() != v.motor.estado():
            raise ReplayDivergiu(f"{nome}: estado final diverge no replay")
        if r.acoes_recentes(10**9) != v.motor.acoes_recentes(10**9):
            raise ReplayDivergiu(f"{nome}: sequencia de acoes diverge no replay")
        if json.loads(json.dumps(r.politica.estado_interno(), sort_keys=True)) != salvo:
            raise ReplayDivergiu(f"{nome}: parametros da politica divergem no replay")
        reconstruidos[nome] = r

    # ---------------------------------------------------------- 4. torneio
    def lutador(nome: str, motor) -> Lutador:
        acoes = [a for _, a in motor.acoes_recentes(10**9)]
        return Lutador(nome, motor.politica, stats_de_tracos(tracos_de_acoes(acoes)))

    lutadores = {n: lutador(n, v.motor) for n, v in vidas.items()}
    lutadores_replay = {n: lutador(n, r) for n, r in reconstruidos.items()}
    nomes = sorted(lutadores)
    partidas = []
    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:
            for k in range(protocolo.v("partidas_por_par")):
                semente = derivar_semente("partida", protocolo.v("semente_torneio"), a, b, k)
                partidas.append(lutar(lutadores[a], lutadores[b], semente))

    with (saida / "partidas.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for p in partidas:
            f.write(json.dumps(p.para_dict(), sort_keys=True) + "\n")
    with (saida / "matches.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["semente", "pet_a", "braco_a", "pet_b", "braco_b", "vencedor", "pontos_a", "turnos", "hp_a", "hp_b"])
        for p in partidas:
            u = p.turnos[-1]
            w.writerow([
                p.semente, p.nome_a, vidas[p.nome_a].braco, p.nome_b, vidas[p.nome_b].braco,
                p.vencedor, p.pontos_a, len(p.turnos), repr(u.hp_a), repr(u.hp_b),
            ])

    # ---------------------------------------------------------- 5. replay das partidas, do disco
    with (saida / "partidas.jsonl").open(encoding="utf-8") as f:
        gravadas = [json.loads(linha) for linha in f]
    if len(gravadas) != len(partidas):
        raise ReplayDivergiu("numero de partidas gravadas difere do executado")
    for g in gravadas:
        r = lutar(lutadores_replay[g["nome_a"]], lutadores_replay[g["nome_b"]], g["semente"])
        if json.loads(json.dumps(r.para_dict(), sort_keys=True)) != g:
            raise ReplayDivergiu(f"partida {g['nome_a']} x {g['nome_b']} semente {g['semente']} diverge no replay")

    # ---------------------------------------------------------- 6. metricas
    braco_de = {n: v.braco for n, v in vidas.items()}
    tv = taxa_vitoria(partidas)
    bt_pets = bradley_terry(partidas)

    partidas_braco = [
        ResultadoPartida(p.semente, braco_de[p.nome_a], braco_de[p.nome_b], p.vencedor, ())
        for p in partidas
        if braco_de[p.nome_a] != braco_de[p.nome_b]
    ]
    bt_bracos = bradley_terry(partidas_braco)

    politicas = {n: v.motor.politica for n, v in vidas.items()}
    politicas["instinto"] = PoliticaInstinto()
    estados = estados_sonda(protocolo.v("estados_sonda"), protocolo.v("semente_sonda"))
    div, dists = divergencia_politicas(politicas, estados, protocolo.v("amostras_por_estado"), protocolo.v("semente_sonda"))
    grupo = dict(braco_de, instinto="instinto")
    pares_pets = {k: v for k, v in div.pares.items() if "instinto" not in k}
    # O gate mede divergencia so entre pets que APRENDEM (bandit). Em arena-v1
    # todo pet e bandit, entao isto e exatamente o calculo de sempre.
    pol_de_pet = {n: politica_de_braco[braco_de[n]] for n in vidas}

    def ambos(a: str, b: str, pol: str) -> bool:
        return pol_de_pet[a] == pol and pol_de_pet[b] == pol

    def aprendem(a: str, b: str) -> bool:
        return pol_de_pet[a] in APRENDIZES and pol_de_pet[b] in APRENDIZES

    jsd_inter = [v for (a, b), v in pares_pets.items() if grupo[a] != grupo[b] and aprendem(a, b)]
    jsd_intra = [v for (a, b), v in pares_pets.items() if grupo[a] == grupo[b] and aprendem(a, b)]
    jsd_inter_instinto = {
        f"{a} | {b}": v for (a, b), v in pares_pets.items() if grupo[a] != grupo[b] and ambos(a, b, "instinto")
    }
    if "instinto" in politica_de_braco.values():
        nao_nulos = {k: v for k, v in jsd_inter_instinto.items() if v != 0.0}
        if not jsd_inter_instinto:
            raise DivergenciaInstintoNaoNula("nenhum par instinto x instinto de bracos diferentes para conferir")
        if nao_nulos:
            raise DivergenciaInstintoNaoNula(
                f"BUG: {len(nao_nulos)} par(es) de bracos instinto com JSD != 0: {dict(list(nao_nulos.items())[:5])}"
            )
    jsd_vs_instinto = {n: div.pares[tuple(sorted((n, "instinto")))] for n in vidas}
    piso = [div.piso_ruido[n] for n in vidas]
    media = lambda xs: sum(xs) / len(xs)  # noqa: E731
    jsd_inter_media = media(jsd_inter)
    piso_max = max(piso)
    # por par de bracos (inclui o par critico)
    jsd_por_par_braco: dict[str, list[float]] = {}
    for (a, b), v in pares_pets.items():
        if grupo[a] != grupo[b]:
            chave = " x ".join(sorted((grupo[a], grupo[b])))
            jsd_por_par_braco.setdefault(chave, []).append(v)

    # resultado central: atencioso vs aleatorio, pareado por semente, para
    # cada politica do protocolo (arena-v1 so tem bandit, rotulo = dono)
    def rotulo(dono: str, pol: str) -> str:
        achados = [r for r, d, p in bracos_exec if d == dono and p == pol]
        if len(achados) != 1:
            raise KeyError(f"braco {dono} x {pol} ausente ou duplicado no protocolo")
        return achados[0]

    def confronto_central(pol: str) -> dict:
        ra, rb = rotulo("atencioso", pol), rotulo("aleatorio", pol)
        pareado = []
        for s in sementes:
            a, b = f"{ra}@{s}", f"{rb}@{s}"
            pts = [p.pontos_a if p.nome_a == a else 1.0 - p.pontos_a for p in partidas if {p.nome_a, p.nome_b} == {a, b}]
            if len(pts) != protocolo.v("partidas_por_par"):
                raise RuntimeError(f"confronto {a} x {b} com {len(pts)} partidas")
            pareado.append(sum(pts) / len(pts))
        ic = bootstrap_ic(pareado, protocolo.v("bootstrap_reamostragens"), protocolo.v("bootstrap_semente"), protocolo.v("nivel_confianca"))
        if ic["ic_inferior"] > 0.5:
            veredito = "ATENCIOSO_VENCE"
        elif ic["ic_superior"] < 0.5:
            veredito = "ATENCIOSO_PERDE"
        else:
            veredito = "INCONCLUSIVO"
        # todos os confrontos atencioso x aleatorio, qualquer semente (secundario)
        todos = [
            p.pontos_a if braco_de[p.nome_a] == ra else 1.0 - p.pontos_a
            for p in partidas
            if {braco_de[p.nome_a], braco_de[p.nome_b]} == {ra, rb}
        ]
        return {
            "pergunta": "pet treinado por dono atencioso vence pet treinado por dono aleatorio com o mesmo orcamento?",
            "unidade": "pontos medios do atencioso no confronto direto, por semente de coorte (empate = 0.5)",
            "por_semente": dict(zip(map(str, sementes), pareado)),
            **ic,
            "veredito": veredito,
            "secundario_todos_confrontos": {"pontos_medios": media(todos), "n_partidas": len(todos)},
        }

    politicas_protocolo = list(dict.fromkeys(pol for _, _, pol in bracos_exec))
    central_por_politica = {pol: confronto_central(pol) for pol in politicas_protocolo}

    fin = finais({n: v.motor.estado() for n, v in vidas.items()})
    finais_braco = {}
    for b in bracos:
        for campo in ("saude", "humor"):
            vals = [fin[f"{b}@{s}"][campo] for s in sementes]
            finais_braco.setdefault(b, {})[campo] = bootstrap_ic(
                vals, protocolo.v("bootstrap_reamostragens"), protocolo.v("bootstrap_semente"), protocolo.v("nivel_confianca")
            )
    taxa_braco = {}
    for b in bracos:
        vals = [tv[f"{b}@{s}"]["taxa"] for s in sementes]
        taxa_braco[b] = bootstrap_ic(
            vals, protocolo.v("bootstrap_reamostragens"), protocolo.v("bootstrap_semente"), protocolo.v("nivel_confianca")
        )

    # ---------------------------------------------------------- 7. gate
    limiar = protocolo.v("limiar_divergencia_jsd_bits")
    gate = []

    def regra(nome, ok, msg):
        gate.append({"regra": nome, "ok": bool(ok), "mensagem": msg})

    regra("orcamento_igual_entre_bracos", True, f"todos os {len(interacoes)} pets com {orcamento} interacoes (verificado)")
    regra("replay_vidas_bit_a_bit", True, f"{len(vidas)} vidas reconstruidas do disco sem divergencia")
    regra("replay_partidas_bit_a_bit", True, f"{len(partidas)} partidas rejogadas sem divergencia")
    regra("sementes_suficientes", len(sementes) >= 5, f"{len(sementes)} sementes")
    regra(
        "sonda_com_resolucao",
        piso_max < limiar,
        f"piso de ruido Monte Carlo maximo {piso_max:.6f} bits vs limiar {limiar} bits"
        + ("" if piso_max < limiar else " -- a sonda nao consegue medir diferencas do tamanho do limiar"),
    )
    quem = "pets bandit de bracos diferentes" if isinstance(protocolo, ProtocoloAblacao) else "pets de bracos diferentes"
    regra(
        "divergencia_entre_politicas",
        jsd_inter_media >= limiar,
        (
            f"JSD media entre {quem} = {jsd_inter_media:.6f} bits, limiar {limiar} bits"
            if jsd_inter_media >= limiar
            else f"CONVERGENCIA: JSD media entre {quem} = {jsd_inter_media:.6f} bits, "
            f"abaixo do limiar {limiar} bits. O AMBIENTE NAO TEM PROFUNDIDADE SUFICIENTE: donos "
            f"diferentes produzem politicas praticamente iguais, entao o torneio nao mede treino."
        ),
    )
    if isinstance(protocolo, ProtocoloAblacao):
        regra(
            "divergencia_instinto_zero",
            True,
            f"{len(jsd_inter_instinto)} pares instinto x instinto de bracos diferentes, todos com JSD exatamente 0.0 "
            f"(verificado; valor nao nulo levanta DivergenciaInstintoNaoNula)",
        )
    aprovada = all(r["ok"] for r in gate)

    avisos = []
    propostos = protocolo.campos_propostos()
    if propostos:
        avisos.append(f"run com {len(propostos)} parametro(s) PROPOSTO(s), nao referendados: {propostos}")
    base_canonica = PROTOCOLOS[protocolo.versao.split("+")[0]]
    if protocolo.hash() != base_canonica.hash():
        avisos.append("protocolo NAO CANONICO (substituicoes via --config): resultado nao e o do portao")

    # ---------------------------------------------------------- artefatos
    divergence = {
        "unidade": "bits (Jensen-Shannon, log2)",
        "limiar": limiar,
        "jsd_media_entre_bracos": jsd_inter_media,
        "jsd_media_dentro_do_braco": media(jsd_intra) if jsd_intra else None,
        "jsd_por_par_de_bracos": {k: {"media": media(v), "n_pares": len(v)} for k, v in sorted(jsd_por_par_braco.items())},
        "jsd_vs_instinto": jsd_vs_instinto,
        "piso_ruido_por_politica": div.piso_ruido,
        "piso_ruido_maximo": piso_max,
        "pares": {f"{a} | {b}": v for (a, b), v in sorted(div.pares.items())},
        "estados_sonda": [
            {"vetor_estado": list(o.vetor_estado), "ticks_desde_cuidado": o.ticks_desde_cuidado} for o in estados
        ],
        "distribuicoes": dists,
    }
    if isinstance(protocolo, ProtocoloAblacao):
        divergence["gate_usa"] = "pares bandit x bandit de bracos (donos) diferentes"
        divergence["jsd_entre_bracos_instinto"] = {
            "media": media(list(jsd_inter_instinto.values())),
            "maximo": max(jsd_inter_instinto.values()),
            "n_pares": len(jsd_inter_instinto),
            "esperado": 0.0,
        }
    (saida / "divergence.json").write_text(_dump(divergence), encoding="utf-8", newline="\n")

    metrics = {
        "status_run": "APROVADA" if aprovada else "REPROVADA",
        "motivos_reprovacao": [r["mensagem"] for r in gate if not r["ok"]],
        "gate": gate,
        "avisos": avisos,
        "protocolo_hash": protocolo.hash(),
        "protocolo_canonico_hash": base_canonica.hash(),
        "protocolo": protocolo.para_dict(),
        "configs": configs_congelados(),
        "engine_sha256": sha256_engine(),
        "sementes_coorte": sementes,
        "bracos": bracos,
        "interacoes_por_pet": interacoes,
        "resultado_central": central_por_politica["bandit" if "bandit" in central_por_politica else politicas_protocolo[0]],
        "taxa_vitoria_por_pet": tv,
        "taxa_vitoria_por_braco": taxa_braco,
        "bradley_terry_por_pet": bt_pets,
        "bradley_terry_por_braco_sem_confronto_interno": bt_bracos,
        "divergencia_resumo": {
            "jsd_media_entre_bracos": jsd_inter_media,
            "jsd_media_dentro_do_braco": divergence["jsd_media_dentro_do_braco"],
            "jsd_por_par_de_bracos": divergence["jsd_por_par_de_bracos"],
            "piso_ruido_maximo": piso_max,
            "limiar": limiar,
        },
        "finais_por_pet": fin,
        "finais_por_braco": finais_braco,
        "n_partidas": len(partidas),
        "preflight": pre,
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    if isinstance(protocolo, ProtocoloMemoria):
        # resultado principal desta run: divergencia com memoria x sem memoria
        ref = {}
        for fonte, chave in (("artifacts/metrics.json", "jsd_media_entre_bracos"),
                             ("artifacts_ablacao/metrics.json", "jsd_media_entre_bracos")):
            caminho = RAIZ / fonte
            if not caminho.exists():
                raise FileNotFoundError(f"referencia sem memoria ausente: {fonte}")
            ref[fonte] = json.loads(caminho.read_text(encoding="utf-8"))["divergencia_resumo"][chave]
        metrics["divergencia_com_x_sem_memoria"] = {
            "com_memoria": jsd_inter_media,
            "sem_memoria": ref,
            "nota": "sem memoria = bracos bandit da run canonica (Linux/3.11) e da ablacao (mesmas vidas); "
                    "mesmas sementes, orcamento, duracao e donos",
        }
        if isinstance(protocolo, ProtocoloMemoriaEspacos):
            b1 = RAIZ / "artifacts_v1_memoria" / "metrics.json"
            if not b1.exists():
                raise FileNotFoundError("referencia da memoria B1 ausente: artifacts_v1_memoria/metrics.json")
            metrics["divergencia_com_x_sem_memoria"]["memoria_b1_features"] = json.loads(
                b1.read_text(encoding="utf-8"))["divergencia_resumo"]["jsd_media_entre_bracos"]
    if isinstance(protocolo, ProtocoloAblacao):
        metrics["bracos_dono_politica"] = {r: {"dono": d, "politica": pol} for r, d, pol in bracos_exec}
        metrics["divergencia_resumo"]["gate_usa"] = divergence["gate_usa"]
        metrics["divergencia_resumo"]["jsd_entre_bracos_instinto"] = divergence["jsd_entre_bracos_instinto"]
        metrics["atencioso_vs_aleatorio_por_politica"] = central_por_politica
        ef = efeito_do_treino(
            central_por_politica["bandit"]["por_semente"],
            central_por_politica["instinto"]["por_semente"],
            protocolo.v("bootstrap_reamostragens"),
            protocolo.v("bootstrap_semente"),
            protocolo.v("nivel_confianca"),
        )
        e = ef["efeito"]
        if e["ic_inferior"] > 0.0:
            ef["veredito"] = "TREINO_AUMENTA_A_VANTAGEM"
        elif e["ic_superior"] < 0.0:
            ef["veredito"] = "TREINO_REDUZ_A_VANTAGEM"
        else:
            ef["veredito"] = "INDISTINGUIVEL_DE_ZERO"
        vi = ef["vantagem_instinto"]
        ef["cuidado_sozinho"] = (
            "ATENCIOSO_COM_INSTINTO_VENCE" if vi["ic_inferior"] > 0.0
            else "ATENCIOSO_COM_INSTINTO_PERDE" if vi["ic_superior"] < 0.0
            else "INCONCLUSIVO"
        )
        metrics["efeito_do_treino"] = ef
    arquivos = ["divergence.json", "matches.csv", "partidas.jsonl", "preflight.json"]
    metrics["artefatos_sha256"] = {a: _sha(saida / a) for a in arquivos}
    metrics["artefatos_sha256"].update(
        {f"vidas/{p.name}": _sha(p) for p in sorted(dir_vidas.iterdir())}
    )
    (saida / "metrics.json").write_text(_dump(metrics), encoding="utf-8", newline="\n")

    print(f"run {metrics['status_run']}  protocolo {metrics['protocolo_hash'][:12]}  saida {saida}")
    for r in gate:
        print(f"  [{'ok' if r['ok'] else 'REPROVA'}] {r['regra']}: {r['mensagem']}")
    for a in avisos:
        print(f"  AVISO: {a}")
    if "efeito_do_treino" in metrics:
        ef = metrics["efeito_do_treino"]
        e = ef["efeito"]
        print(f"  efeito do treino: {ef['veredito']}  media {e['media']:.4f}  IC{int(e['nivel']*100)} [{e['ic_inferior']:.4f}, {e['ic_superior']:.4f}]  n={e['n']}  (cuidado sozinho: {ef['cuidado_sozinho']})")
    for pol, rc in central_por_politica.items():
        rotulo_pol = "central" if len(central_por_politica) == 1 else f"atencioso x aleatorio ({pol})"
        print(f"  {rotulo_pol}: {rc['veredito']}  media {rc['media']:.4f}  IC{int(rc['nivel']*100)} [{rc['ic_inferior']:.4f}, {rc['ic_superior']:.4f}]  n={rc['n']}")
    return 0 if aprovada else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Simulador de arena com bracos de controle")
    ap.add_argument("--config", required=True, type=Path)
    args = ap.parse_args(argv)
    protocolo, saida, _ = carregar_config(args.config)
    return executar(protocolo, saida)


if __name__ == "__main__":
    sys.exit(main())
