"""V2, A1: a bola, sem aprendizado (docs/PLANO_ANALISE_V2_A1.md, registrado antes da run; desenho docs/V2_A1_BOLA_DESENHO.md).

    python experiments/run_v2_a1.py --config experiments/configs/v2_a1/calibracao.json   # grade, sementes 6101...6505
    python experiments/run_v2_a1.py --config experiments/configs/v2_a1/validacao.json    # UMA vez, 7101...7505

Fluxo por ponto (duracao_min, ganho_humor_bola, w_bola):
  1. vidas    - arena v1 (4 donos, 224 interacoes, 14 dias), MotorAmbiente com obediencia, educacao e lesoes desligadas,
                temperamento neutro, especie brasa; o mesmo dono com a mesma rng em todos os bracos (rotulo_dono). Bracos:
                bola (dono poe, o instinto ve), bolacega (dono poe, w_bola = 0: o instinto nao ve) e sembola (dono da v1;
                nao depende do ponto, roda uma vez).
  2. replay   - toda vida e reconstruida do log gravado e comparada bit a bit (estado, acoes, rngs, contadores da bola) (G1).
  3. medidas  - um gravador no replay anota cada decisao (bola presente, regra do instinto, acao, necessidades);
                metrics.resposta_a_bola (1a-pet) e metrics.privacao_nas_decisoes (cuidado controlado).
  4. escolha  - calibracao: a regra do plano (secao 4). So no ponto escolhido (e na validacao): o "so cuidado" acoplado
                (D4) e a sensibilidade de bolas_por_dia {2, 8}.
Divergencia de replay levanta erro e para tudo. Nenhuma metrica fora de digilab/metrics.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.ambiente import DonoComBola, PoliticaInstintoBola, fabricas_ambiente, reproduzir_ambiente  # noqa: E402
from digilab.config import CONFIG_BOLA_LIGADA, CONFIG_PADRAO, ConfigBola  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_BOLA, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.metrics import bootstrap_ic, privacao_nas_decisoes, resposta_a_bola  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, sha256_engine  # noqa: E402
from digilab.treino import Vida, simular_vida  # noqa: E402

SEMENTES_CALIBRACAO = (6101, 6202, 6303, 6404, 6505)
SEMENTES_VALIDACAO = (7101, 7202, 7303, 7404, 7505)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
DIAS = PROTOCOLO_ARENA_V1.dias_simulados.valor
ORCAMENTO = PROTOCOLO_ARENA_V1.orcamento_interacoes.valor
BOOT = {"reamostragens": 10_000, "semente": 20261001, "nivel": 0.95}
FAIXA_P_BOLA = (0.30, 0.80)                    # plano, secao 4: uma decisao, nem reflexo nem indiferenca
SINAIS = (AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value)


class ReplayDivergiu(RuntimeError):
    pass


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def ic(xs) -> dict:
    return bootstrap_ic(list(xs), BOOT["reamostragens"], BOOT["semente"], BOOT["nivel"])


def media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


def nome_ponto(p: dict) -> str:
    return f"d{p['duracao_min']}_g{p['ganho_humor_bola']}_w{p['w_bola']}"


def cfg_bola(p: dict, bolas_por_dia: int | None = None) -> ConfigBola:
    return replace(CONFIG_BOLA_LIGADA, duracao_min=p["duracao_min"], ganho_humor_bola=p["ganho_humor_bola"], w_bola=p["w_bola"],
                   bolas_por_dia=bolas_por_dia if bolas_por_dia is not None else CONFIG_BOLA_LIGADA.bolas_por_dia)


# ------------------------------------------------------------------ gravador de decisoes (so no replay)


class _Gravadora:
    """Embrulha a politica no replay e anota cada decisao: (indice, bola presente, regra, acao, fome, higiene, energia, humor).
    So repassa: nenhuma rng a mais, nenhum estado mudado."""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.nome = interna.nome
        self.decisoes: list[tuple] = []

    def agir(self, obs, rng):
        a = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        self.decisoes.append((len(self.decisoes), obs.bola > 0.0, self.interna.ultima_regra, a.value, v[0], v[1], v[2], v[3]))
        return a

    def observar(self, transicao):
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick):
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self):
        return self.interna.estado_interno()


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate())


# ------------------------------------------------------------------ 1-3. vidas, replay e medidas


def _fabricas(braco: str, cb: ConfigBola):
    """(fabrica da politica, fabrica do motor) do braco. bolacega: o motor tem a bola, a politica nao a ve (w_bola = 0)."""
    if braco == "bolacega":
        cega = replace(cb, w_bola=0.0)
        return fabricas_ambiente(cfg_bola=cb, politica_fabrica=lambda cfg=None: PoliticaInstintoBola(cfg, cega))
    return fabricas_ambiente(cfg_bola=cb)


def _dono(braco: str, dono: str, cb: ConfigBola):
    return criar_dono(dono) if braco == "sembola" else DonoComBola(dono, cb)


def medir(v_motor, log: LogDeEventos, fp, fm, semente: int, nome: str) -> dict:
    """Rejoga do log com o gravador, confere bit a bit contra o motor vivo (G1) e mede."""
    grav = []

    def fab(cfg=None):
        g = _Gravadora(fp(cfg))
        grav.append(g)
        return g

    r = reproduzir_ambiente(log, fab, semente=semente, fabrica_motor=fm)
    if _nucleo(r) != _nucleo(v_motor) or r.resumo_bola() != v_motor.resumo_bola() or r.estado() != v_motor.estado():
        raise ReplayDivergiu(f"{nome}: o replay do log diverge da vida")
    dec = grav[0].decisoes
    tick = CONFIG_PADRAO.intervalo_decisao_ticks
    resp = resposta_a_bola([(k * tick, b, regra, a) for k, b, regra, a, *_ in dec])
    priv = privacao_nas_decisoes([(k * tick, f, h, e, hu) for k, _, _, _, f, h, e, hu in dec], CONFIG_PADRAO.limiar_privacao)
    n_acoes = {}
    for e in log:
        if e.tipo == "acao_usuario":
            n_acoes[str(e.valor)] = n_acoes.get(str(e.valor), 0) + 1
    return {"resposta": resp, "privacao": priv, "bola": v_motor.contagem_bola, "acoes_dono": n_acoes,
            "saude_final": v_motor._estado.saude, "humor_final": v_motor._estado.humor, "morte": v_motor.morte,
            "interacoes": sum(n_acoes.values())}


def vidas_braco(braco: str, cb: ConfigBola, sementes, pasta: Path | None) -> dict:
    """Vidas de um braco nos 4 donos x sementes, gravadas (se ha pasta), rejogadas do log e medidas. nome -> medidas."""
    fp, fm = _fabricas(braco, cb)
    saida = {}
    for s in sementes:
        for dono in DONOS:
            nome = f"{dono}-{braco}@{s}"
            v = simular_vida(f"{dono}-{braco}", _dono(braco, dono, cb), fp(), s, DIAS, ORCAMENTO, rotulo_dono=dono, fabrica_motor=fm)
            texto = v.motor.log.para_jsonl()
            if pasta is not None:
                _gravar(pasta / "vidas" / f"{nome}.jsonl", texto)
                texto = (pasta / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")
            m = medir(v.motor, LogDeEventos.de_jsonl(texto), fp, fm, s, nome)
            if m["interacoes"] != ORCAMENTO:
                raise RuntimeError(f"{nome}: {m['interacoes']} interacoes, orcamento {ORCAMENTO}")
            saida[nome] = m
    return saida


# ------------------------------------------------------------------ resumos


def _por_semente(medidas: dict, braco: str, sementes, f) -> list[float]:
    """por semente, a media sobre os donos de f(medida) (None fica de fora; conta quantos entraram)."""
    out = []
    for s in sementes:
        vals = [f(medidas[f"{d}-{braco}@{s}"]) for d in DONOS]
        vals = [x for x in vals if x is not None]
        if not vals:
            raise ValueError(f"{braco}@{s}: nenhum dono com a medida definida")
        out.append(media(vals))
    return out


def resumo_ponto(bola: dict, cega: dict, sem: dict, sementes) -> dict:
    s = list(sementes)
    dp = _por_semente(bola, "bola", s, lambda m: m["resposta"]["delta"])
    dp_cega = _por_semente(cega, "bolacega", s, lambda m: m["resposta"]["delta"])
    p_com = _por_semente(bola, "bola", s, lambda m: m["resposta"]["p_com_bola"])
    priv_b = _por_semente(bola, "bola", s, lambda m: m["privacao"]["fracao_privacao"])
    priv_s = _por_semente(sem, "sembola", s, lambda m: m["privacao"]["fracao_privacao"])
    hum_b = _por_semente(bola, "bola", s, lambda m: m["privacao"]["humor_medio"])
    hum_s = _por_semente(sem, "sembola", s, lambda m: m["privacao"]["humor_medio"])
    dif_priv = [a - b for a, b in zip(priv_b, priv_s)]
    dif_hum = [a - b for a, b in zip(hum_b, hum_s)]
    sem_delta = {n: m["resposta"] for n, m in bola.items() if m["resposta"]["delta"] is None}
    mortes = sum(m["morte"] is not None for d in (bola, cega, sem) for m in d.values())
    por_dono = {}
    for d in DONOS:
        ms = [bola[f"{d}-bola@{x}"] for x in s]
        por_dono[d] = {"bolas_postas": media(m["bola"]["postas"] for m in ms), "usadas": media(m["bola"]["usadas"] for m in ms),
                       "expiradas": media(m["bola"]["expiradas"] for m in ms),
                       "decisoes_com_bola": media(m["bola"]["decisoes_com_bola"] for m in ms),
                       "p_com_bola": [m["resposta"]["p_com_bola"] for m in ms], "delta": [m["resposta"]["delta"] for m in ms],
                       "fracao_privacao": media(m["privacao"]["fracao_privacao"] for m in ms),
                       "fracao_privacao_sembola": media(sem[f"{d}-sembola@{x}"]["privacao"]["fracao_privacao"] for x in s),
                       "humor_medio": media(m["privacao"]["humor_medio"] for m in ms),
                       "humor_medio_sembola": media(sem[f"{d}-sembola@{x}"]["privacao"]["humor_medio"] for x in s)}
    return {"delta_p": {"por_semente": dp, **ic(dp)}, "delta_p_bolacega": {"por_semente": dp_cega, **ic(dp_cega)},
            "p_com_bola": {"por_semente": p_com, **ic(p_com)},
            "privacao_bola_menos_sembola": {"por_semente": dif_priv, **ic(dif_priv)},
            "humor_bola_menos_sembola": {"por_semente": dif_hum, **ic(dif_hum)},
            "mortes": mortes, "vidas_sem_delta": sem_delta, "por_dono": por_dono}


def gates(r: dict) -> dict:
    pet = {"definicao": "Delta p = p(brincar | bola) - p(brincar | sem bola) no tempo livre, braco bola, media dos donos por semente",
           "ic_inferior": r["delta_p"]["ic_inferior"], "passa": r["delta_p"]["ic_inferior"] > 0}
    priv = r["privacao_bola_menos_sembola"]
    cuidado = {"mortes": r["mortes"], "privacao_ic": [priv["ic_inferior"], priv["ic_superior"]],
               "passa": r["mortes"] == 0 and priv["ic_inferior"] <= 0 <= priv["ic_superior"]}
    return {"1a_pet": pet, "cuidado_controlado": cuidado,
            "1a_dono": "nao testada: sem apoio na literatura (D6) e exige o aprendiz (A1 + L1, chat B)",
            "G1": "replay do log bit a bit em toda vida (o orquestrador para se divergir)",
            "G2": "tests/test_ambiente.py (a, b, c)"}


def escolher(varredura: list[dict]) -> dict:
    """Plano, secao 4: entre os pontos com p(brincar | bola) medio na faixa e o IC da privacao contendo 0, o de maior limite
    inferior do Delta p; empate: menor ganho, depois menor w_bola, depois menor duracao."""
    def ok(v):
        r = v["resumo"]
        p = r["p_com_bola"]["media"]
        priv = r["privacao_bola_menos_sembola"]
        return FAIXA_P_BOLA[0] <= p <= FAIXA_P_BOLA[1] and priv["ic_inferior"] <= 0 <= priv["ic_superior"]

    chave = lambda v: (-v["resumo"]["delta_p"]["ic_inferior"], v["ponto"]["ganho_humor_bola"], v["ponto"]["w_bola"],  # noqa: E731
                       v["ponto"]["duracao_min"])
    candidatos = [v for v in varredura if ok(v)]
    fechou = bool(candidatos)
    v = min(candidatos if fechou else varredura, key=chave)
    return {"ponto": v["ponto"], "fechou": fechou, "candidatos": [nome_ponto(c["ponto"]) for c in candidatos],
            "regra": "plano, secao 4", "faixa_p_com_bola": FAIXA_P_BOLA}


# ------------------------------------------------------------------ acoplado e sensibilidade (ponto escolhido e validacao)


def log_so_cuidado(log: LogDeEventos, sem_carinho: bool = False) -> LogDeEventos:
    """D4: o mesmo log sem elogio, bronca e as acoes da bola (e, na variante, sem acariciar): o cuidado nos mesmos ticks."""
    fora = set(SINAIS) | {a.value for a in ACOES_BOLA} | ({AcaoUsuario.ACARICIAR.value} if sem_carinho else set())
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in fora)])


def acoplados(cb: ConfigBola, sementes, pasta: Path, bola: dict, sem: dict) -> dict:
    fp, fm = _fabricas("bola", cb)
    out = {}
    for variante, sem_carinho in (("cuidado", False), ("cuidado-semcarinho", True)):
        por_semente = {}
        for s in sementes:
            origem = LogDeEventos.de_jsonl((pasta / "vidas" / f"atencioso-bola@{s}.jsonl").read_text(encoding="utf-8"))
            log = log_so_cuidado(origem, sem_carinho)
            nome = f"atencioso-{variante}@{s}"
            _gravar(pasta / "acoplado" / "vidas" / f"{nome}.jsonl", log.para_jsonl())
            m_vivo = reproduzir_ambiente(log, fp, semente=s, fabrica_motor=fm)
            m = medir(m_vivo, LogDeEventos.de_jsonl((pasta / "acoplado" / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")),
                      fp, fm, s, nome)
            por_semente[str(s)] = {**m, "interacoes_origem": bola[f"atencioso-bola@{s}"]["interacoes"]}
        ss = [str(s) for s in sementes]
        priv = [por_semente[x]["privacao"]["fracao_privacao"] for x in ss]
        priv_b = [bola[f"atencioso-bola@{x}"]["privacao"]["fracao_privacao"] for x in ss]
        priv_s = [sem[f"atencioso-sembola@{x}"]["privacao"]["fracao_privacao"] for x in ss]
        hum = [por_semente[x]["privacao"]["humor_medio"] for x in ss]
        hum_b = [bola[f"atencioso-bola@{x}"]["privacao"]["humor_medio"] for x in ss]
        out[variante] = {"por_semente": por_semente,
                         "interacoes": [por_semente[x]["interacoes"] for x in ss],
                         "privacao": ic(priv), "privacao_bola_menos_acoplado": ic([a - b for a, b in zip(priv_b, priv)]),
                         "privacao_sembola_menos_acoplado": ic([a - b for a, b in zip(priv_s, priv)]),
                         "humor": ic(hum), "humor_bola_menos_acoplado": ic([a - b for a, b in zip(hum_b, hum)]),
                         "mortes": sum(por_semente[x]["morte"] is not None for x in ss)}
    return out


def sensibilidade(p: dict, sementes, sem: dict) -> dict:
    out = {}
    for n in (2, 8):
        cb = cfg_bola(p, n)
        bola = vidas_braco("bola", cb, sementes, None)
        cega = vidas_braco("bolacega", cb, sementes, None)
        r = resumo_ponto(bola, cega, sem, sementes)
        out[str(n)] = {k: r[k] for k in ("delta_p", "p_com_bola", "privacao_bola_menos_sembola", "humor_bola_menos_sembola", "mortes")}
    return out


# ------------------------------------------------------------------ principal


def meta(cfg: dict, t0: float, cb: ConfigBola | None) -> dict:
    arquivos = ["digilab/ambiente.py", "digilab/policy.py", "digilab/config.py", "digilab/metrics.py", "digilab/engine.py",
                "digilab/events.py", "experiments/run_v2_a1.py"]
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    return {"config": cfg, "sha256": {a: _sha(RAIZ / a) for a in arquivos}, "python": sys.version, "plataforma": platform.platform(),
            "segundos": round(time.perf_counter() - t0, 1), "config_bola": asdict(cb) if cb else None,
            "dias": DIAS, "orcamento": ORCAMENTO, "bootstrap": BOOT}


def rodar_ponto(p: dict, sementes, pasta: Path | None, sem: dict) -> tuple[dict, dict, dict]:
    cb = cfg_bola(p)
    bola = vidas_braco("bola", cb, sementes, pasta)
    cega = vidas_braco("bolacega", cb, sementes, pasta)
    return bola, cega, resumo_ponto(bola, cega, sem, sementes)


def principal(cfg: dict) -> int:
    t0 = time.perf_counter()
    sementes = tuple(cfg["sementes"])
    esperadas = SEMENTES_CALIBRACAO if cfg["conjunto"] == "calibracao" else SEMENTES_VALIDACAO
    if sementes != esperadas:
        raise ValueError(f"conjunto {cfg['conjunto']} com sementes {sementes}; o plano diz {esperadas}")
    saida = RAIZ / cfg["saida"]
    if cfg["conjunto"] == "validacao" and (saida / "resultado.json").exists():
        raise RuntimeError("a validacao roda uma vez: resultado.json ja existe")
    sem = vidas_braco("sembola", CONFIG_BOLA_LIGADA, sementes, saida / "sembola")
    if cfg["conjunto"] == "calibracao":
        varredura = []
        for d in cfg["grade"]["duracao_min"]:
            for g in cfg["grade"]["ganho_humor_bola"]:
                for w in cfg["grade"]["w_bola"]:
                    p = {"duracao_min": d, "ganho_humor_bola": g, "w_bola": w}
                    _, _, r = rodar_ponto(p, sementes, saida / "grade" / nome_ponto(p), sem)
                    linha = {"ponto": p, "resumo": r, "gates": gates(r)}
                    varredura.append(linha)
                    print(f"{nome_ponto(p)}: dp {r['delta_p']['media']:+.3f} [{r['delta_p']['ic_inferior']:+.3f}] "
                          f"p_bola {r['p_com_bola']['media']:.3f} priv {r['privacao_bola_menos_sembola']['media']:+.4f}", flush=True)
        _gravar(saida / "varredura.jsonl", "".join(json.dumps(v, sort_keys=True, ensure_ascii=False) + "\n" for v in varredura))
        escolha = escolher(varredura)
        p = escolha["ponto"]
    else:
        escolha = {"ponto": cfg["ponto"], "fechou": None, "regra": "validacao: o ponto do config, commitado antes"}
        p = cfg["ponto"]
    pasta = saida / "ponto"
    bola, cega, r = rodar_ponto(p, sementes, pasta, sem)
    g = gates(r)
    acop = acoplados(cfg_bola(p), sementes, pasta, bola, sem)
    sens = sensibilidade(p, sementes, sem)
    resultado = {"conjunto": cfg["conjunto"], "sementes": list(sementes), "escolha": escolha, "ponto": p, "resumo": r, "gates": g,
                 "acoplado": {k: {kk: vv for kk, vv in v.items() if kk != "por_semente"} for k, v in acop.items()},
                 "sensibilidade_bolas_por_dia": sens}
    _gravar(saida / "pet.json", _dump({"bola": bola, "bolacega": cega}))
    _gravar(saida / "sembola.json", _dump(sem))
    _gravar(saida / "so_cuidado.json", _dump(acop))
    _gravar(saida / "resultado.json", _dump(resultado))
    _gravar(saida / "meta.json", _dump(meta(cfg, t0, cfg_bola(p))))
    print(f"ponto {nome_ponto(p)} (fechou: {escolha['fechou']}); 1a-pet {'PASSA' if g['1a_pet']['passa'] else 'FALHA'} "
          f"dp {r['delta_p']['media']:+.3f} [{r['delta_p']['ic_inferior']:+.3f}; {r['delta_p']['ic_superior']:+.3f}]; "
          f"cuidado {'PASSA' if g['cuidado_controlado']['passa'] else 'FALHA'} (mortes {r['mortes']}, privacao "
          f"{r['privacao_bola_menos_sembola']['media']:+.4f}); {time.perf_counter() - t0:.0f} s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    return principal(json.loads((RAIZ / a.config).read_text(encoding="utf-8")))


if __name__ == "__main__":
    raise SystemExit(main())
