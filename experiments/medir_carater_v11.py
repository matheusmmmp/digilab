"""A escala do carater no v11 contra o v10: as linhas e as formas adultas (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, PW-4; a medida e o criterio
de "perto" estao na secao 11 da tarefa, registrados antes desta medida). Descritiva, com as sementes dos testes; sem run de pesquisa.

O carater e o da web (`web/app/motor/carater.ts`, `caraterPolitica`): o desvio da politica sobre a mesma politica recem-nascida, em 32
sondas x 100 amostras com a semente 9001, a media dos tracos de cada eixo, / 0,05, mais o `DESLOC_CARATER` do estagio, cortado em [-1, 1].
As constantes sao lidas de `web/app/motor/constantes.ts` (CCP e DESLOC_CARATER), para a medida usar exatamente as do jogo.
  - o v10: o bandit do Python (`PoliticaBandit`) com os donos de sempre, com elogio e bronca (`simular_vida`);
  - o v11: a vida do gabarito da web (`experiments/exportar_gabarito_lobos.py`: P1-c-tapa, o corpo, o carinho, o tapa e a consequencia).
    As sondas ganham os receptores do corpo pela rng `sonda-corpo` da mesma semente (como a deriva da bancada).
A linha sai do carater no fim da crianca (900 min) e a forma adulta do carater no fim do adolescente (1980 min).

    python experiments/medir_carater_v11.py      # grava artifacts_v2_w_porte/carater_v11.json
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import statistics
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as eg  # noqa: E402

from digilab.combate_v2.v21.catalogo import LINHAS, forma_adulta, linha_do_adolescente, ramo_da_crianca  # noqa: E402
from digilab.config import CONFIG_ARENA, CONFIG_CATALOGO, CONFIG_EVOLUCAO_PESQUISA, CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.evolucao import fracao_cuidado_bebe, politica_no_tick  # noqa: E402
from digilab.metrics import distribuicoes_de_acao, estados_sonda  # noqa: E402
from digilab.policies.bandit import PoliticaBandit  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v2_w_porte" / "carater_v11.json"
CONSTANTES_TS = RAIZ / "web" / "app" / "motor" / "constantes.ts"
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303, 404, 505)                  # as dos testes
DIAS = 2
ORCAMENTO = 16 * DIAS
PERMUTACOES = 10_000
CFG_EVO = CONFIG_EVOLUCAO_PESQUISA
T_ADOL = CFG_EVO.dur_bebe_min + CFG_EVO.dur_crianca_min
T_ADUL = T_ADOL + CFG_EVO.dur_adolescente_min


def constantes_web() -> tuple[dict, dict]:
    """CCP e DESLOC_CARATER de web/app/motor/constantes.ts (falha alto se o formato mudar)."""
    texto = CONSTANTES_TS.read_text(encoding="utf-8")
    m = re.search(r"export const CCP = \{ nEstados: (\d+), amostras: (\d+), semente: (\d+), escala: ([\d.]+) \};", texto)
    if m is None:
        raise ValueError("CCP nao encontrado em constantes.ts")
    ccp = {"estados": int(m.group(1)), "amostras": int(m.group(2)), "semente": int(m.group(3)), "escala": float(m.group(4))}
    desloc = {}
    for estagio in ("adolescente", "adulto"):
        d = re.search(estagio + r": \{ atento: ([-\d.]+), impetuoso: ([-\d.]+), paciente: ([-\d.]+), resistente: ([-\d.]+) \}", texto)
        if d is None:
            raise ValueError(f"DESLOC_CARATER.{estagio} nao encontrado em constantes.ts")
        desloc[estagio] = dict(zip(("atento", "impetuoso", "paciente", "resistente"), map(float, d.groups())))
    return ccp, desloc


def carater(pol, base, estados: list, ccp: dict, desloc: dict) -> tuple[dict, dict]:
    """(carater por eixo, desvio bruto por eixo): o metodo de caraterPolitica (a web), com as sondas dadas."""
    dp = distribuicoes_de_acao(pol, estados, ccp["amostras"], ccp["semente"])
    db = distribuicoes_de_acao(base, estados, ccp["amostras"], ccp["semente"])
    por_traco: dict[str, float] = {}
    for a, traco in dict(CONFIG_ARENA.mapa_pet_combate).items():
        por_traco[traco] = por_traco.get(traco, 0.0) + sum(p[a] - q[a] for p, q in zip(dp, db)) / len(estados)
    bruto = {e: sum(por_traco[t] for t in ts) / len(ts) for e, ts in CFG_EVO.eixo_traco.items()}
    return {e: max(-1.0, min(1.0, v / ccp["escala"] + desloc[e])) for e, v in bruto.items()}, bruto


def evoluir(log, fab, semente: int, fm, base, estados: list, ccp: dict, desloc: dict) -> dict:
    """o ramo, os dois carateres, a linha e a forma adulta de uma vida"""
    frac, _, _ = fracao_cuidado_bebe(log, CFG_EVO)
    car_adol, bruto_adol = carater(bv.do_braco(politica_no_tick(log, fab, semente, T_ADOL, fm)) if fm else
                                   politica_no_tick(log, fab, semente, T_ADOL), base, estados, ccp, desloc["adolescente"])
    car_adul, bruto_adul = carater(bv.do_braco(politica_no_tick(log, fab, semente, T_ADUL, fm)) if fm else
                                   politica_no_tick(log, fab, semente, T_ADUL), base, estados, ccp, desloc["adulto"])
    linha = linha_do_adolescente(car_adol)
    return {"ramo": ramo_da_crianca(frac), "carater_adolescente": car_adol, "bruto_adolescente": bruto_adol,
            "carater_adulto": car_adul, "bruto_adulto": bruto_adul, "linha": linha,
            "forma": forma_adulta(linha, car_adul, CFG_EVO.sparring_simulado)}


def pets_v10(ccp: dict, desloc: dict) -> list[dict]:
    estados = estados_sonda(ccp["estados"], ccp["semente"])
    fab = lambda cfg=None: PoliticaBandit(cfg or CONFIG_PADRAO)  # noqa: E731
    out = []
    for d in DONOS:
        for s in SEMENTES:
            v = simular_vida(f"{d}-v10", criar_dono(d), fab(CONFIG_PADRAO), s, DIAS, ORCAMENTO, rotulo_dono=d)
            out.append({"versao": "v10", "dono": d, "semente": s,
                        **evoluir(v.motor.log, fab, s, None, fab(CONFIG_PADRAO), estados, ccp, desloc)})
    return out


def pets_v11(ccp: dict, desloc: dict) -> list[dict]:
    b = eg.bancada_v11(DIAS, ORCAMENTO)
    out = []
    for d in DONOS:
        for s in SEMENTES:
            espec = bv.EspecVida(d, eg.BRACO_V11, s)
            v = b.vida(espec)
            cc = b.cfg_corpo_de(espec)
            rng = random.Random(derivar_semente("sonda-corpo", ccp["semente"]))
            estados = [replace(o, corpo=bv.percepcao_da_sonda(o, cc, rng)) for o in estados_sonda(ccp["estados"], ccp["semente"])]
            base = bv.do_braco(b.politica(espec, CONFIG_PADRAO))           # o A recem-nascido: o instinto
            out.append({"versao": "v11", "dono": d, "semente": s,
                        **evoluir(v.motor.log, b.fabrica_politica(espec), s, b.fabrica_motor(espec), base, estados, ccp, desloc)})
    return out


def distribuicao(pets: list[dict], chave: str, valores: tuple) -> dict:
    return {x: sum(p[chave] == x for p in pets) / len(pets) for x in valores}


def tvd(a: dict, b: dict) -> float:
    return sum(abs(a[k] - b[k]) for k in a) / 2


def permutacao(v10: list[dict], v11: list[dict], chave: str, valores: tuple) -> dict:
    """a TVD observada e o 95o percentil da TVD com os rotulos de versao permutados (rng propria)"""
    obs = tvd(distribuicao(v10, chave, valores), distribuicao(v11, chave, valores))
    rng = random.Random(derivar_semente("pw4-permutacao", chave))
    todos = v10 + v11
    nulos = []
    for _ in range(PERMUTACOES):
        rng.shuffle(todos)
        nulos.append(tvd(distribuicao(todos[:len(v10)], chave, valores), distribuicao(todos[len(v10):], chave, valores)))
    nulos.sort()
    p95 = nulos[int(0.95 * PERMUTACOES) - 1]
    p = sum(n >= obs for n in nulos) / PERMUTACOES
    return {"tvd": obs, "p95_nulo": p95, "p": p, "perto": obs <= p95}


def escala(v10: list[dict], v11: list[dict], ccp: dict) -> dict:
    def brutos(pets):
        return [abs(x) for p in pets for est in ("bruto_adolescente", "bruto_adulto") for x in p[est].values()]

    def cortados(pets):
        vs = [abs(x) for p in pets for est in ("carater_adolescente", "carater_adulto") for x in p[est].values()]
        return sum(v >= 1.0 for v in vs) / len(vs)
    m10, m11 = statistics.median(brutos(v10)), statistics.median(brutos(v11))
    c10, c11 = cortados(v10), cortados(v11)
    razao = m11 / m10
    return {"mediana_abs_bruto": {"v10": m10, "v11": m11}, "razao": razao, "cortados": {"v10": c10, "v11": c11},
            "perto": 0.5 <= razao <= 2.0 and c11 <= c10 + 0.10}


def so_desloc(pets: list[dict], ccp: dict, desloc: dict) -> dict:
    """Descritivo, fora do criterio: a linha e a forma que o pet teria com o desvio zerado (so o DESLOC_CARATER da web), e a fracao dos
    pets em que a linha e a forma medidas sao essas. Mostra o quanto o aprendido decide a linha e a forma."""
    car0_adol = {e: max(-1.0, min(1.0, desloc["adolescente"][e])) for e in desloc["adolescente"]}
    car0_adul = {e: max(-1.0, min(1.0, desloc["adulto"][e])) for e in desloc["adulto"]}
    linha0 = linha_do_adolescente(car0_adol)
    iguais_linha = sum(p["linha"] == linha0 for p in pets) / len(pets)
    iguais_forma = sum(p["forma"] == forma_adulta(p["linha"], car0_adul, CFG_EVO.sparring_simulado) for p in pets) / len(pets)
    return {"linha_sem_desvio": linha0, "fracao_linha_sem_desvio": iguais_linha, "fracao_forma_sem_desvio": iguais_forma}


def medir() -> dict:
    ccp, desloc = constantes_web()
    v10, v11 = pets_v10(ccp, desloc), pets_v11(ccp, desloc)
    formas = tuple(f for l in LINHAS for f in CONFIG_CATALOGO.arquetipos_adulto[l]["formas"])
    linhas = permutacao(v10, v11, "linha", LINHAS)
    formas_r = permutacao(v10, v11, "forma", formas)
    esc = escala(v10, v11, ccp)
    perto = linhas["perto"] and formas_r["perto"] and esc["perto"]
    return {"descricao": "PW-4: o carater do v11 contra o v10, pelo metodo da web (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 11)",
            "constantes_web": {"CCP": ccp, "DESLOC_CARATER": desloc}, "donos": list(DONOS), "sementes": list(SEMENTES),
            "dias": DIAS, "orcamento": ORCAMENTO, "permutacoes": PERMUTACOES,
            "distribuicoes": {v: {"linha": distribuicao(p, "linha", LINHAS), "forma": distribuicao(p, "forma", formas),
                                  "ramo": distribuicao(p, "ramo", ("sereno", "arisco"))} for v, p in (("v10", v10), ("v11", v11))},
            "criterio": {"linhas": linhas, "formas": formas_r, "escala": esc, "perto": perto},
            "descritivo_so_desloc": {"v10": so_desloc(v10, ccp, desloc), "v11": so_desloc(v11, ccp, desloc)},
            "pets": v10 + v11,
            "codigo": {c: hashlib.sha256((RAIZ / c).read_bytes()).hexdigest() for c in
                       ("experiments/medir_carater_v11.py", "digilab/policies/lobos.py", "digilab/policies/bandit.py",
                        "web/app/motor/constantes.ts")}}


if __name__ == "__main__":
    r = medir()
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: r[k] for k in ("criterio", "descritivo_so_desloc")}, indent=1, ensure_ascii=False))
