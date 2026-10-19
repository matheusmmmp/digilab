"""A leitura do painel DigiBrain dos pets v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 4 e etapa 5).

O jogo web mostra o cerebro A ao lado do pet, e a tela nao calcula nada: as contas do painel ficam aqui, com o espelho em
web/app/motor/digibrain.ts e paridade bit a bit pelo gabarito (experiments/exportar_gabarito_painel_digibrain.py). Sao leituras puras
do motivo de uma decisao (`PoliticaLobos.motivos`) e do desvio aprendido (`PoliticaLobos.desvio_aprendido`): nao mudam peso, motivo,
memoria nem rng, e nenhum numero novo entra no cerebro.

- **As barras por lobo** (`leitura_decisao`): a contribuicao de cada lobo na acao escolhida, dividida pelo peso efetivo dela (as barras
  somam 1, a menos do arredondamento). O lobo de decisao vem em duas partes: o aprendido nas entradas de sempre (w - w0, a soma dos
  `aprendido`) e o das entradas do corpo (a soma dos `aprendido_corpo`, prior 0). As duas somadas sao a `decisao` do motivo, bit a bit
  (conferido: falha alto se nao forem). O aprendido e o corpo podem ser negativos.
- **A percepcao** (PW-5, lista e nao barra): as entradas de maior |w.x| na acao escolhida, w o peso efetivo da entrada, (w0 / S) x mais
  o termo aprendido. O vies fica de fora (nao e algo que o pet le); termos zero tambem.
- **As chances**: o peso efetivo / a soma dos pesos efetivos dos candidatos, na ordem do sorteio.
- **"Quem decidiu"** (a sonda contrafactual da auditoria E0, V3-1, `docs/futuro/digibrain_v3_e0.md`): o sorteio so com os impulsos e o
  mesmo `u`. Se a acao sai outra, o aprendido mudou esta decisao. Nao e o `lobo_decisivo`, que mede so o tamanho da contribuicao.
- **"O que aprendeu"** (`leitura_aprendido`): as acoes de maior |desvio aprendido| sobre o prior, a mesma base da vontade (PW-3).
"""
from __future__ import annotations

from .events import ACOES_PET_HOJE
from .policies.lobos import ENTRADAS, sortear

N_PERCEPCAO = 3        # quantas entradas a percepcao lista: "as duas ou tres" da tarefa (secao 4); SEM FONTE, so apresentacao
N_APRENDIDO = 3        # quantas acoes o "o que aprendeu" lista; SEM FONTE, so apresentacao
LOBOS_BARRAS = ("impulsos", "decisao", "corpo", "memoria_emocao", "piso")


def _soma(valores) -> float:
    """Da esquerda para a direita a partir de 0.0, como `ativacao` (sem somatorio compensado)."""
    acumulado = 0.0
    for v in valores:
        acumulado = acumulado + v
    return acumulado


def leitura_decisao(motivo: dict, prior_linha: list[int], S: int, receptores: list[str],
                    n_percepcao: int = N_PERCEPCAO) -> dict:
    """A leitura de uma decisao para o painel. `motivo` e um item de `PoliticaLobos.motivos` (com as chaves em texto, como no
    gabarito); `prior_linha` e a linha do prior da regra e da acao escolhida (inteiros na escala S, na ordem de ENTRADAS); `receptores`
    sao os receptores novos do cerebro, na ordem de `aprendido_corpo` (vazio sem o corpo)."""
    a, cand, c = motivo["acao"], motivo["candidatos"], motivo["contribuicoes"]
    if a not in cand:
        raise ValueError(f"acao {a} fora dos candidatos {cand}")
    if len(prior_linha) != len(ENTRADAS):
        raise ValueError(f"linha do prior com {len(prior_linha)} pesos, esperados {len(ENTRADAS)}")
    efetivo = motivo["pesos"][a]
    if not efetivo > 0.0:
        raise ValueError(f"peso efetivo nao positivo na acao escolhida: {efetivo}")
    aprendido = motivo["aprendido"]
    aprendido_corpo = motivo.get("aprendido_corpo")
    if aprendido is None:
        if aprendido_corpo is not None:
            raise ValueError("aprendido do corpo sem o aprendido")
        decisao, corpo = c["decisao"][a], 0.0
    else:
        decisao = _soma(aprendido[a])
        corpo = 0.0 if aprendido_corpo is None else _soma(aprendido_corpo[a])
        if decisao + corpo != c["decisao"][a]:
            raise ValueError(f"a decisao do motivo ({c['decisao'][a]!r}) nao e o aprendido ({decisao!r}) mais o corpo ({corpo!r})")
    partes = {"impulsos": c["impulsos"][a], "decisao": decisao, "corpo": corpo, "memoria_emocao": c["memoria_emocao"][a],
              "piso": c["piso"][a]}
    barras = {lobo: partes[lobo] / efetivo for lobo in LOBOS_BARRAS}

    total = _soma(motivo["pesos"][x] for x in cand)
    chances = [{"acao": x, "chance": motivo["pesos"][x] / total} for x in cand]

    u = motivo["u"]
    if u is None:
        if len(cand) != 1:
            raise ValueError(f"decisao sem u com {len(cand)} candidatos")
        quem = {"escolha": False, "acao_instinto": a, "mudou": False}
    else:
        so_impulsos = cand[sortear([c["impulsos"][x] for x in cand], u)]
        quem = {"escolha": True, "acao_instinto": so_impulsos, "mudou": so_impulsos != a}

    x = motivo["percepcao"]
    entradas = []
    for j, e in enumerate(ENTRADAS):
        if e == "vies":
            continue
        termo = (prior_linha[j] / S) * x[e]
        if aprendido is not None:
            termo = termo + aprendido[a][j]
        entradas.append((e, x[e], termo))
    if aprendido_corpo is not None:
        xc = motivo["percepcao_corpo"]
        if len(receptores) != len(aprendido_corpo[a]):
            raise ValueError(f"{len(receptores)} receptores para {len(aprendido_corpo[a])} termos do corpo")
        for i, r in enumerate(receptores):
            entradas.append((r, xc[r], aprendido_corpo[a][i]))
    ordem = sorted((k for k in range(len(entradas)) if entradas[k][2] != 0.0), key=lambda k: (-abs(entradas[k][2]), k))
    percepcao = [{"entrada": entradas[k][0], "x": entradas[k][1], "termo": entradas[k][2]} for k in ordem[:n_percepcao]]

    return {"n": motivo["n"], "regra": motivo["regra"], "acao": a, "barras": barras, "chances": chances, "quem_decidiu": quem,
            "percepcao": percepcao}


def leitura_aprendido(desvio: dict[str, float], n: int = N_APRENDIDO) -> list[dict]:
    """As acoes de maior |desvio aprendido| (o `desvio_aprendido`, com as chaves em texto), sem as de desvio zero; no empate, a ordem
    de ACOES_PET_HOJE."""
    ordem = [a.value for a in ACOES_PET_HOJE]
    fora = [a for a in desvio if a not in ordem]
    if fora:
        raise ValueError(f"acoes fora de ACOES_PET_HOJE: {fora}")
    acoes = sorted((a for a in desvio if desvio[a] != 0.0), key=lambda a: (-abs(desvio[a]), ordem.index(a)))
    return [{"acao": a, "desvio": desvio[a]} for a in acoes[:n]]
