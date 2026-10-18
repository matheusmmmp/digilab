"""A escala e o deslocamento proprios do carater do v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, PW-4 opcao (b); o metodo e o criterio estao na
secao 15 da tarefa, registrados antes desta medida). Descritiva, com as sementes dos testes; sem run de pesquisa.

Parte do artefato da medida da PW-4 (`artifacts_v2_w_porte/carater_v11.json`, de experiments/medir_carater_v11.py): o desvio bruto por eixo
de cada pet, no fim da crianca e no fim do adolescente, nos 20 pets v10 e nos 20 pets v11. Nada e simulado aqui de novo.
  - a escala do v11: CCP.escala x a razao das medianas de |bruto| (v11 / v10), arredondada a tres casas;
  - o deslocamento do adolescente: um por eixo que leve as 4 linhas para perto de 25% (o leilao abaixo);
  - o deslocamento do adulto: em cada linha, menos a mediana do eixo complementar dos pets da linha, com a escala nova
    (o metodo de 2026-09-25, docs/registro/2026-09.md);
  - os deslocamentos sao arredondados a quatro casas, como os de hoje, e o criterio e conferido com os numeros arredondados.

    python experiments/calibrar_carater_v11.py      # grava artifacts_v2_w_porte/carater_v11_calibracao.json
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.v21.catalogo import LINHAS, forma_adulta, linha_do_adolescente  # noqa: E402
from digilab.config import CONFIG_CATALOGO, CONFIG_EVOLUCAO_PESQUISA  # noqa: E402

MEDIDA = RAIZ / "artifacts_v2_w_porte" / "carater_v11.json"
ARQUIVO = RAIZ / "artifacts_v2_w_porte" / "carater_v11_calibracao.json"
EIXOS = ("atento", "impetuoso", "paciente", "resistente")
EIXO_DA_LINHA = {l: CONFIG_CATALOGO.arquetipos_adolescente[l]["eixo"] for l in LINHAS}
COMP_DA_LINHA = {l: CONFIG_CATALOGO.arquetipos_adulto[l]["eixo_complementar"] for l in LINHAS}
SPARRING = CONFIG_EVOLUCAO_PESQUISA.sparring_simulado
PASSO_LEILAO = 0.005               # o quanto o eixo da linha cheia desce alem da menor margem (o epsilon do leilao; bem acima do arredondamento a 4 casas)
MAX_RODADAS = 10_000
FOLGA_LEILAO = 1                    # o leilao para com toda linha a um pet de 1/4 (4 a 6 de 20): o 5/5/5/5 exato cicla nestes pets
# o criterio da secao 15
LINHA_MIN, LINHA_MAX = 0.15, 0.35
CIMA_MIN, CIMA_MAX = 0.35, 0.65
RAZAO_MIN, RAZAO_MAX = 0.5, 2.0
CORTE_FOLGA = 0.10


def corta(x: float) -> float:
    return max(-1.0, min(1.0, x))


def carater(bruto: dict, escala: float, desloc: dict) -> dict:
    return {e: corta(bruto[e] / escala + desloc[e]) for e in EIXOS}


def sem_corte(bruto: dict, escala: float, desloc: dict) -> dict:
    """o carater sem o corte em [-1, 1]: o leilao anda nele, porque com o corte os eixos empatam em -1 e a linha fica presa na ordem fixa.
    O criterio confere a linha com o corte."""
    return {e: bruto[e] / escala + desloc[e] for e in EIXOS}


def dominante(car: dict) -> str:
    """a linha do eixo dominante, com o desempate da ordem fixa (a regra de linha_do_adolescente, sem a conferencia da faixa)"""
    return max(LINHAS, key=lambda l: (car[EIXO_DA_LINHA[l]], -LINHAS.index(l)))


def leilao_adolescente(pets: list[dict], escala: float) -> tuple[dict, int]:
    """O deslocamento do adolescente (um leilao): enquanto a linha mais cheia passa de 1/4 dos pets, o eixo dela desce ate o pet de menor
    margem passar para outra linha. Para quando toda linha fica a FOLGA_LEILAO pets de 1/4, ou falha alto."""
    alvo = len(pets) / len(LINHAS)
    d = {e: 0.0 for e in EIXOS}
    for rodada in range(MAX_RODADAS):
        linhas = [dominante(sem_corte(p["bruto_adolescente"], escala, d)) for p in pets]
        cont = {l: linhas.count(l) for l in LINHAS}
        cheia = max(LINHAS, key=lambda l: (cont[l], -LINHAS.index(l)))
        if max(cont.values()) <= alvo + FOLGA_LEILAO and min(cont.values()) >= alvo - FOLGA_LEILAO:
            return d, rodada
        eixo = EIXO_DA_LINHA[cheia]
        margens = []
        for p, l in zip(pets, linhas):
            if l != cheia:
                continue
            car = sem_corte(p["bruto_adolescente"], escala, d)
            margens.append(car[eixo] - max(car[EIXO_DA_LINHA[o]] for o in LINHAS if o != cheia))
        d[eixo] -= min(margens) + PASSO_LEILAO
    raise RuntimeError(f"o leilao do adolescente nao fechou em {MAX_RODADAS} rodadas")


def calibrar() -> dict:
    medida = json.loads(MEDIDA.read_text(encoding="utf-8"))
    ccp = medida["constantes_web"]["CCP"]
    v10 = [p for p in medida["pets"] if p["versao"] == "v10"]
    v11 = [p for p in medida["pets"] if p["versao"] == "v11"]
    if len(v10) != 20 or len(v11) != 20:
        raise ValueError(f"a medida da PW-4 deveria ter 20 pets por versao: {len(v10)}, {len(v11)}")
    razao = medida["criterio"]["escala"]["razao"]
    escala = round(ccp["escala"] * razao, 3)

    d_adol_bruto, rodadas = leilao_adolescente(v11, escala)
    media = sum(d_adol_bruto.values()) / len(EIXOS)          # somar uma constante a todos os eixos nao muda a linha
    d_adol = {e: round(d_adol_bruto[e] - media, 4) for e in EIXOS}
    linhas = [linha_do_adolescente(carater(p["bruto_adolescente"], escala, d_adol)) for p in v11]

    d_adul = {}
    for l in LINHAS:
        comp = COMP_DA_LINHA[l]
        zs = [p["bruto_adulto"][comp] / escala for p, li in zip(v11, linhas) if li == l]
        if not zs:
            raise ValueError(f"nenhum pet v11 na linha {l}: a mediana do complementar nao existe")
        d_adul[comp] = round(-statistics.median(zs), 4) + 0.0          # + 0.0: sem o -0.0

    pets = []
    for p, l in zip(v11, linhas):
        car_adul = carater(p["bruto_adulto"], escala, d_adul)
        pets.append({"dono": p["dono"], "semente": p["semente"], "linha": l, "forma": forma_adulta(l, car_adul, SPARRING),
                     "carater_adolescente": carater(p["bruto_adolescente"], escala, d_adol), "carater_adulto": car_adul})

    n = len(pets)
    dist_linha = {l: sum(p["linha"] == l for p in pets) / n for l in LINHAS}
    formas_cima = {l: next(f for f, x in CONFIG_CATALOGO.arquetipos_adulto[l]["formas"].items() if x["sinal"] == ">=0") for l in LINHAS}
    cima = sum(p["forma"] == formas_cima[p["linha"]] for p in pets) / n
    formas = tuple(f for l in LINHAS for f in CONFIG_CATALOGO.arquetipos_adulto[l]["formas"])
    dist_forma = {f: sum(p["forma"] == f for p in pets) / n for f in formas}

    m10 = statistics.median(abs(x) / ccp["escala"] for p in v10 for est in ("bruto_adolescente", "bruto_adulto") for x in p[est].values())
    m11 = statistics.median(abs(x) / escala for p in v11 for est in ("bruto_adolescente", "bruto_adulto") for x in p[est].values())
    cortados_v10 = medida["criterio"]["escala"]["cortados"]["v10"]
    vs = [abs(x) for p in pets for est in ("carater_adolescente", "carater_adulto") for x in p[est].values()]
    cortados_v11 = sum(v >= 1.0 for v in vs) / len(vs)

    c_linhas = all(LINHA_MIN <= x <= LINHA_MAX for x in dist_linha.values())
    c_formas = CIMA_MIN <= cima <= CIMA_MAX
    c_escala = RAZAO_MIN <= m11 / m10 <= RAZAO_MAX and cortados_v11 <= cortados_v10 + CORTE_FOLGA
    return {"descricao": "PW-4 (b): a escala e o deslocamento proprios do carater do v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 15)",
            "medida": {"arquivo": str(MEDIDA.relative_to(RAIZ)).replace("\\", "/"),
                       "sha256": hashlib.sha256(MEDIDA.read_bytes()).hexdigest()},
            "escala_v10": ccp["escala"], "razao_medianas": razao, "escala_v11": escala,
            "desloc_v11": {"adolescente": d_adol, "adulto": d_adul}, "rodadas_leilao": rodadas,
            "distribuicoes": {"linha": dist_linha, "forma": dist_forma, "forma_de_cima": cima},
            "criterio": {"linhas": {"ok": c_linhas, "faixa": [LINHA_MIN, LINHA_MAX]},
                         "formas": {"ok": c_formas, "forma_de_cima": cima, "faixa": [CIMA_MIN, CIMA_MAX]},
                         "escala": {"ok": c_escala, "mediana_v10": m10, "mediana_v11": m11, "razao": m11 / m10,
                                    "cortados": {"v10": cortados_v10, "v11": cortados_v11}},
                         "fecha": c_linhas and c_formas and c_escala},
            "pets": pets,
            "codigo": {c: hashlib.sha256((RAIZ / c).read_bytes()).hexdigest() for c in ("experiments/calibrar_carater_v11.py",)}}


if __name__ == "__main__":
    r = calibrar()
    ARQUIVO.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: r[k] for k in ("escala_v11", "desloc_v11", "rodadas_leilao", "distribuicoes", "criterio")}, indent=1,
                     ensure_ascii=False))
