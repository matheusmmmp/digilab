"""Metricas (Etapa 5). Existem uma vez so e servem a todos os bracos.

  taxa_vitoria             pontos / jogos em round-robin (empate = 0.5)
  bradley_terry            forca log por pet, com erro padrao (Hessiana)
  divergencia_politicas    JSD (bits) entre distribuicoes de acao
                           condicionadas ao estado, sobre estados de sonda
  finais                   saude e humor ao fim da vida
  bootstrap_ic             intervalo percentil sobre unidades (sementes)
  efeito_do_treino         ablacao: vantagem do atencioso com bandit menos a
                           mesma vantagem com instinto, pareada por semente
"""

from __future__ import annotations

import math
import random
from bisect import bisect_left
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .arena import ResultadoPartida
from .config import CONFIG_METRICAS, TICKS_POR_DIA, ConfigMetricas
from .events import ACOES_PET_HOJE
from .policy import Observacao, Politica
from .protocol import derivar_semente

ACOES = ACOES_PET_HOJE


# ------------------------------------------------------------ vitoria


def pontos_por_confronto(partidas: Iterable[ResultadoPartida]) -> dict[tuple[str, str], list[float]]:
    """(i, j) -> lista de pontos de i contra j. Guarda os dois sentidos."""
    tabela: dict[tuple[str, str], list[float]] = {}
    for p in partidas:
        tabela.setdefault((p.nome_a, p.nome_b), []).append(p.pontos_a)
        tabela.setdefault((p.nome_b, p.nome_a), []).append(1.0 - p.pontos_a)
    return tabela


def taxa_vitoria(partidas: Iterable[ResultadoPartida]) -> dict[str, dict]:
    soma: dict[str, float] = {}
    jogos: dict[str, int] = {}
    empates: dict[str, int] = {}
    for p in partidas:
        for nome, pts in ((p.nome_a, p.pontos_a), (p.nome_b, 1.0 - p.pontos_a)):
            soma[nome] = soma.get(nome, 0.0) + pts
            jogos[nome] = jogos.get(nome, 0) + 1
            empates[nome] = empates.get(nome, 0) + (p.vencedor == "empate")
    return {n: {"taxa": soma[n] / jogos[n], "jogos": jogos[n], "empates": empates[n]} for n in sorted(soma)}


# ------------------------------------------------------------ Bradley-Terry


def _resolver(M: list[list[float]], v: list[float]) -> list[float]:
    """Eliminacao gaussiana com pivotamento parcial."""
    n = len(v)
    A = [list(M[i]) + [v[i]] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c]))
        if abs(A[piv][c]) < 1e-14:
            raise ArithmeticError("sistema singular no Bradley-Terry")
        A[c], A[piv] = A[piv], A[c]
        for r in range(c + 1, n):
            f = A[r][c] / A[c][c]
            for k in range(c, n + 1):
                A[r][k] -= f * A[c][k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (A[r][n] - sum(A[r][k] * x[k] for k in range(r + 1, n))) / A[r][r]
    return x


def _inversa(M: list[list[float]]) -> list[list[float]]:
    n = len(M)
    colunas = [_resolver(M, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[colunas[j][i] for j in range(n)] for i in range(n)]


def bradley_terry(
    partidas: Sequence[ResultadoPartida], cfg: ConfigMetricas | None = None
) -> dict[str, dict]:
    """MLE penalizada (ridge) das forcas log; empate conta 0.5 para cada lado.

    Erro padrao = raiz da diagonal da inversa da Hessiana negativa. O ridge
    fixa a translacao (forcas somam ~0) e evita divergencia com placar perfeito.
    """
    cfg = cfg or CONFIG_METRICAS
    nomes = sorted({p.nome_a for p in partidas} | {p.nome_b for p in partidas})
    if len(nomes) < 2:
        raise ValueError("Bradley-Terry precisa de pelo menos 2 competidores")
    idx = {n: i for i, n in enumerate(nomes)}
    obs = [(idx[p.nome_a], idx[p.nome_b], p.pontos_a) for p in partidas]
    n = len(nomes)
    beta = [0.0] * n

    def grad_hess(beta):
        g = [-cfg.ridge_bradley_terry * b for b in beta]
        H = [[(-cfg.ridge_bradley_terry if i == j else 0.0) for j in range(n)] for i in range(n)]
        for i, j, y in obs:
            p = 1.0 / (1.0 + math.exp(-(beta[i] - beta[j])))
            g[i] += y - p
            g[j] -= y - p
            w = p * (1.0 - p)
            H[i][i] -= w
            H[j][j] -= w
            H[i][j] += w
            H[j][i] += w
        return g, H

    for _ in range(cfg.max_iter_bradley_terry):
        g, H = grad_hess(beta)
        passo = _resolver([[-h for h in linha] for linha in H], g)
        beta = [b + s for b, s in zip(beta, passo)]
        if max(abs(s) for s in passo) < cfg.tolerancia_bradley_terry:
            break
    else:
        raise ArithmeticError("Bradley-Terry nao convergiu")

    _, H = grad_hess(beta)
    cov = _inversa([[-h for h in linha] for linha in H])
    # So contrastes sao identificaveis: projeta na restricao soma-zero
    # (P = I - 11^T/n). Sem isso o erro padrao mede a translacao livre,
    # que so o ridge segura, e nao a incerteza das forcas relativas.
    P = [[(1.0 if i == j else 0.0) - 1.0 / n for j in range(n)] for i in range(n)]
    PC = [[sum(P[i][k] * cov[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    cov_c = [[sum(PC[i][k] * P[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    media = sum(beta) / n
    return {
        nome: {"forca_log": beta[i] - media, "erro_padrao": math.sqrt(max(0.0, cov_c[i][i]))}
        for nome, i in idx.items()
    }


# ------------------------------------------------------------ divergencia


def estados_sonda(n: int, semente: int) -> list[Observacao]:
    """Estados sorteados uniformemente. Congelados pelo protocolo (n, semente)."""
    rng = random.Random(derivar_semente("sonda", semente))
    estados = []
    for _ in range(n):
        vetor = (
            rng.random(), rng.random(), rng.random(), rng.random(), rng.random(),
            rng.randrange(6) / 5.0, float(rng.random() < 0.3), rng.random(),
        )
        estados.append(Observacao(vetor_estado=vetor, ticks_desde_cuidado=rng.randrange(0, 481), total_cuidados=0))
    return estados


def distribuicoes_de_acao(
    politica: Politica, estados: Sequence[Observacao], amostras: int, semente: int
) -> list[dict[str, float]]:
    """Frequencia empirica de acoes por estado.

    Numeros aleatorios comuns: o estado k usa a MESMA sequencia de rng para
    toda politica, entao politicas identicas dao distribuicoes identicas.
    """
    saida = []
    for k, obs in enumerate(estados):
        rng = random.Random(derivar_semente("dist", semente, k))
        cont = {a.value: 0 for a in ACOES}
        for _ in range(amostras):
            cont[politica.agir(obs, rng).value] += 1
        saida.append({a: c / amostras for a, c in cont.items()})
    return saida


def jsd_bits(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    if set(p) != set(q):
        raise ValueError("distribuicoes com suportes declarados diferentes")
    js = 0.0
    for a in p:
        m = 0.5 * (p[a] + q[a])
        if p[a] > 0:
            js += 0.5 * p[a] * math.log2(p[a] / m)
        if q[a] > 0:
            js += 0.5 * q[a] * math.log2(q[a] / m)
    return max(0.0, js)


def jsd_media(dp: Sequence[Mapping[str, float]], dq: Sequence[Mapping[str, float]]) -> float:
    if len(dp) != len(dq) or not dp:
        raise ValueError("listas de distribuicoes incompativeis")
    return sum(jsd_bits(p, q) for p, q in zip(dp, dq)) / len(dp)


@dataclass(frozen=True)
class Divergencia:
    pares: dict[tuple[str, str], float]      # JSD media entre cada par de politicas
    piso_ruido: dict[str, float]             # JSD entre a politica e ela mesma com rng independente

    def media_entre(self, grupo_de: Mapping[str, str], mesmo_grupo: bool) -> float:
        vals = [v for (a, b), v in self.pares.items() if (grupo_de[a] == grupo_de[b]) == mesmo_grupo]
        if not vals:
            raise ValueError("nenhum par na selecao pedida")
        return sum(vals) / len(vals)


def divergencia_politicas(
    politicas: Mapping[str, Politica], estados: Sequence[Observacao], amostras: int, semente: int
) -> tuple[Divergencia, dict[str, list[dict[str, float]]]]:
    dists = {n: distribuicoes_de_acao(p, estados, amostras, semente) for n, p in politicas.items()}
    nomes = sorted(politicas)
    pares = {(a, b): jsd_media(dists[a], dists[b]) for i, a in enumerate(nomes) for b in nomes[i + 1:]}
    piso = {
        n: jsd_media(dists[n], distribuicoes_de_acao(politicas[n], estados, amostras, semente + 1))
        for n in nomes
    }
    return Divergencia(pares=pares, piso_ruido=piso), dists


# ------------------------------------------------------------ finais e IC


def finais(estados: Mapping[str, dict]) -> dict[str, dict]:
    return {n: {"saude": e["saude"], "humor": e["humor"]} for n, e in sorted(estados.items())}


def bootstrap_ic(valores: Sequence[float], reamostragens: int, semente: int, nivel: float) -> dict:
    if len(valores) < 2:
        raise ValueError("bootstrap precisa de pelo menos 2 unidades")
    rng = random.Random(derivar_semente("bootstrap", semente))
    n = len(valores)
    medias = sorted(sum(valores[rng.randrange(n)] for _ in range(n)) / n for _ in range(reamostragens))
    alfa = (1.0 - nivel) / 2.0
    lo = medias[int(math.floor(alfa * (reamostragens - 1)))]
    hi = medias[int(math.ceil((1.0 - alfa) * (reamostragens - 1)))]
    return {"media": sum(valores) / n, "ic_inferior": lo, "ic_superior": hi, "nivel": nivel, "n": n}


# ------------------------------------------------------------ ablacao treino x cuidado


def vantagem_em_pontos(pontos_atencioso: float) -> float:
    """Pontos do atencioso menos pontos do aleatorio no confronto direto.

    Cada partida distribui 1 ponto (empate = 0.5 para cada), entao a
    vantagem e p - (1 - p) = 2p - 1, em [-1, 1]; 0 = equilibrio.
    """
    if not (0.0 <= pontos_atencioso <= 1.0):
        raise ValueError(f"pontos fora de [0, 1]: {pontos_atencioso}")
    return 2.0 * pontos_atencioso - 1.0


def efeito_do_treino(
    pontos_bandit: Mapping[str, float],
    pontos_instinto: Mapping[str, float],
    reamostragens: int,
    semente: int,
    nivel: float,
) -> dict:
    """Efeito do treino = vantagem(atencioso x aleatorio | bandit)
                        - vantagem(atencioso x aleatorio | instinto),
    pareado por semente de coorte.

    `pontos_*`: semente -> pontos medios do atencioso contra o aleatorio da
    MESMA semente. Com instinto nao ha aprendizado; a vantagem que sobra vem
    do cuidado (estado de vida -> tracos -> stats). O que o bandit acrescenta
    por cima disso e o efeito do treino. IC: bootstrap percentil sobre
    sementes (bootstrap_ic); as tres estimativas usam a mesma semente de
    bootstrap, entao reamostram as mesmas sementes.
    """
    if set(pontos_bandit) != set(pontos_instinto):
        raise ValueError(
            f"sementes diferentes entre politicas: {sorted(pontos_bandit)} x {sorted(pontos_instinto)}"
        )
    sementes = sorted(pontos_bandit)
    vb = [vantagem_em_pontos(pontos_bandit[s]) for s in sementes]
    vi = [vantagem_em_pontos(pontos_instinto[s]) for s in sementes]
    ef = [b - i for b, i in zip(vb, vi)]
    ic = lambda xs: bootstrap_ic(xs, reamostragens, semente, nivel)  # noqa: E731
    return {
        "definicao": "(pontos atencioso - pontos aleatorio | bandit) - (mesma diferenca | instinto), "
        "por semente; pontos = media do confronto direto, empate = 0.5",
        "por_semente": {
            s: {"vantagem_bandit": b, "vantagem_instinto": i, "efeito": e}
            for s, b, i, e in zip(sementes, vb, vi, ef)
        },
        "vantagem_bandit": ic(vb),
        "vantagem_instinto": ic(vi),
        "efeito": ic(ef),
    }


# ------------------------------------------------------------ combate V2: matriz e equilibrio


def matriz_taxas(confrontos: Iterable[tuple[str, str, float]]) -> dict[str, dict[str, float]]:
    """(a, b, pontos de a) -> taxa[a][b] = pontos medios de a contra b.

    Guarda os dois sentidos; no espelho (a == b) as duas posicoes contam.
    """
    soma: dict[tuple[str, str], float] = {}
    n: dict[tuple[str, str], int] = {}
    for a, b, pa in confrontos:
        for x, y, p in ((a, b, pa), (b, a, 1.0 - pa)):
            soma[(x, y)] = soma.get((x, y), 0.0) + p
            n[(x, y)] = n.get((x, y), 0) + 1
    nomes = sorted({x for x, _ in soma})
    return {x: {y: soma[(x, y)] / n[(x, y)] for y in nomes if (x, y) in soma} for x in nomes}


def equilibrio_simetrico(taxa: Mapping[str, Mapping[str, float]], nomes: Sequence[str], iteracoes: int) -> dict:
    """Fictitious play deterministico no jogo simetrico de soma zero u(i,j) = taxa[i][j] - 0.5.

    Parte de contagem zero; a cada iteracao soma 1 a melhor resposta contra a
    frequencia acumulada (empate: menor indice em `nomes`). Retorna a
    frequencia empirica (aproxima o equilibrio), o valor do melhor desvio
    contra ela (explorabilidade; 0 = equilibrio exato) e a trajetoria final.
    """
    faltando = [(i, j) for i in nomes for j in nomes if j not in taxa.get(i, {})]
    if faltando:
        raise ValueError(f"matriz incompleta: faltam {faltando[:5]}")
    k = len(nomes)
    u = [[taxa[nomes[i]][nomes[j]] - 0.5 for j in range(k)] for i in range(k)]
    cont = [0] * k
    ganho = [0.0] * k  # ganho[i] = soma_j u[i][j] * cont[j]
    for _ in range(iteracoes):
        br = max(range(k), key=lambda i: (ganho[i], -i))
        cont[br] += 1
        for i in range(k):
            ganho[i] += u[i][br]
    freq = [c / iteracoes for c in cont]
    desvio = max(sum(u[i][j] * freq[j] for j in range(k)) for i in range(k))
    return {
        "estrategia": dict(zip(nomes, freq)),
        "explorabilidade": desvio,
        "iteracoes": iteracoes,
        "metodo": "fictitious play deterministico, u = taxa - 0.5, empate pelo menor indice",
    }


def suporte(estrategia: Mapping[str, float], peso_minimo: float) -> list[str]:
    return sorted(n for n, p in estrategia.items() if p >= peso_minimo)


# ================================================================ personalidade
# (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md)


def cumprimento_desejo(desejos, acoes_pet, k_ticks: int) -> dict:
    """Fracao dos desejos `vontade` com alvo X em que o pet escolhe X nos proximos
    `k_ticks`. Toda acao do pet e possivel a qualquer momento nesta simulacao, entao
    toda vontade conta como oportunidade. Baixo = a fala promete o que o pet nao faz."""
    vontades = [d for d in desejos if d.tipo == "vontade" and d.intensidade > 0]
    cumpridos = sum(any(d.tick <= t <= d.tick + k_ticks and a.value == d.alvo for t, a in acoes_pet)
                    for d in vontades)
    return {"vontades": len(vontades), "cumpridas": cumpridos,
            "cumprimento": cumpridos / len(vontades) if vontades else None}


def fracao_tempo_vontade(desejos, tick_fim: int) -> float:
    """Fracao do tempo de vida com um desejo `vontade` ativo (legibilidade do aprendizado)."""
    total, t_ant, ativo = 0, 0, False
    for d in desejos:
        if ativo:
            total += d.tick - t_ant
        t_ant, ativo = d.tick, d.tipo == "vontade" and d.intensidade > 0
    if ativo:
        total += tick_fim - t_ant
    return total / tick_fim if tick_fim else 0.0


def decomposicao_ovo_braco(valor: Mapping[tuple[str, str], float]) -> dict:
    """ANOVA de dois fatores sem interacao, uma observacao por (ovo, braco):
    fracao da soma de quadrados explicada pelo ovo, pelo braco e o residuo."""
    ovos = sorted({o for o, _ in valor})
    bracos = sorted({b for _, b in valor})
    if len(valor) != len(ovos) * len(bracos):
        raise ValueError("decomposicao exige a tabela completa ovo x braco")
    gm = sum(valor.values()) / len(valor)
    m_ovo = {o: sum(valor[(o, b)] for b in bracos) / len(bracos) for o in ovos}
    m_br = {b: sum(valor[(o, b)] for o in ovos) / len(ovos) for b in bracos}
    ss_tot = sum((v - gm) ** 2 for v in valor.values())
    ss_ovo = len(bracos) * sum((m - gm) ** 2 for m in m_ovo.values())
    ss_br = len(ovos) * sum((m - gm) ** 2 for m in m_br.values())
    frac = (lambda x: x / ss_tot) if ss_tot > 0 else (lambda x: 0.0)
    return {"fracao_ovo": frac(ss_ovo), "fracao_braco": frac(ss_br), "fracao_residuo": frac(ss_tot - ss_ovo - ss_br),
            "ss_total": ss_tot, "n_ovos": len(ovos), "n_bracos": len(bracos),
            "media_por_braco": m_br}


# ------------------------------------------------------------ natureza x criacao (PLANO_ANALISE_LINHAGEM)

COMPONENTES_CRUZADOS = ("G", "D", "R", "GD", "GR", "DR", "e")


def tabela_cruzada(valor: Mapping[tuple, float]) -> tuple[list, list, list, list[list[list[float]]]]:
    """(genomas, donos, ambientes, y[g][d][r]) a partir de {(genoma, dono, ambiente): valor}; exige a tabela completa."""
    gs = sorted({k[0] for k in valor})
    ds = sorted({k[1] for k in valor})
    rs = sorted({k[2] for k in valor})
    if len(valor) != len(gs) * len(ds) * len(rs):
        raise ValueError("decomposicao cruzada exige a tabela completa genoma x dono x ambiente")
    return gs, ds, rs, [[[float(valor[(g, d, r)]) for r in rs] for d in ds] for g in gs]


def componentes_cruzados(y: Sequence[Sequence[Sequence[float]]]) -> dict:
    """ANOVA de 3 fatores cruzados (genoma G, dono D, ambiente R), uma observacao por celula. Componentes de
    variancia pelo metodo dos momentos, esperancas do modelo ALEATORIO SEM RESTRICAO (a interacao tripla fica no
    residuo). Estimadores sem truncar (podem sair negativos); `fracao` trunca em 0."""
    a, b, c = len(y), len(y[0]), len(y[0][0])
    if a < 2 or b < 2 or c < 2:
        raise ValueError("cada fator precisa de pelo menos 2 niveis")
    n = a * b * c
    gm = sum(v for yg in y for yd in yg for v in yd) / n
    mg = [sum(v for yd in yg for v in yd) / (b * c) for yg in y]
    md = [sum(y[i][j][k] for i in range(a) for k in range(c)) / (a * c) for j in range(b)]
    mr = [sum(y[i][j][k] for i in range(a) for j in range(b)) / (a * b) for k in range(c)]
    mgd = [[sum(y[i][j]) / c for j in range(b)] for i in range(a)]
    mgr = [[sum(y[i][j][k] for j in range(b)) / b for k in range(c)] for i in range(a)]
    mdr = [[sum(y[i][j][k] for i in range(a)) / a for k in range(c)] for j in range(b)]
    ss = {"G": b * c * sum((m - gm) ** 2 for m in mg), "D": a * c * sum((m - gm) ** 2 for m in md),
          "R": a * b * sum((m - gm) ** 2 for m in mr),
          "GD": c * sum((mgd[i][j] - mg[i] - md[j] + gm) ** 2 for i in range(a) for j in range(b)),
          "GR": b * sum((mgr[i][k] - mg[i] - mr[k] + gm) ** 2 for i in range(a) for k in range(c)),
          "DR": a * sum((mdr[j][k] - md[j] - mr[k] + gm) ** 2 for j in range(b) for k in range(c))}
    ss_tot = sum((v - gm) ** 2 for yg in y for yd in yg for v in yd)
    ss["e"] = ss_tot - sum(ss.values())
    gl = {"G": a - 1, "D": b - 1, "R": c - 1, "GD": (a - 1) * (b - 1), "GR": (a - 1) * (c - 1),
          "DR": (b - 1) * (c - 1), "e": (a - 1) * (b - 1) * (c - 1)}
    qm = {k: ss[k] / gl[k] for k in ss}
    e = qm["e"]
    var = {"G": (qm["G"] - qm["GD"] - qm["GR"] + e) / (b * c), "D": (qm["D"] - qm["GD"] - qm["DR"] + e) / (a * c),
           "R": (qm["R"] - qm["GR"] - qm["DR"] + e) / (a * b), "GD": (qm["GD"] - e) / c, "GR": (qm["GR"] - e) / b,
           "DR": (qm["DR"] - e) / a, "e": e}
    pos = {k: max(0.0, v) for k, v in var.items()}
    tot = sum(pos.values())
    return {"componentes": var, "fracao": {k: (v / tot if tot > 0 else 0.0) for k, v in pos.items()},
            "ss": ss, "gl": gl, "qm": qm, "ss_total": ss_tot, "media_geral": gm,
            "media_por_dono": md, "niveis": {"G": a, "D": b, "R": c}}


def decomposicao_cruzada(valor: Mapping[tuple, float]) -> dict:
    """Extensao da decomposicao_ovo_braco para genoma x dono x ambiente (cruzados, uma observacao por celula)."""
    gs, ds, rs, y = tabela_cruzada(valor)
    out = componentes_cruzados(y)
    out["media_por_dono"] = dict(zip(ds, out["media_por_dono"]))
    out["rotulos"] = {"G": gs, "D": ds, "R": rs}
    return out


def bootstrap_cruzado(y: Sequence[Sequence[Sequence[float]]], estatistica, reamostragens: int, semente: int,
                      reamostrar: str = "GR") -> list:
    """Bootstrap 'pigeonhole' (McCullagh, 2000) para fatores cruzados: reamostra com reposicao, de forma
    independente, os genomas (G) e/ou os ambientes (R); os donos ficam fixos. Um nivel sorteado duas vezes conta
    como dois niveis. Devolve a `estatistica(y_reamostrado)` de cada reamostra."""
    if not set(reamostrar) <= {"G", "R"} or not reamostrar:
        raise ValueError(f"reamostrar deve ser 'G', 'R' ou 'GR', veio {reamostrar!r}")
    rng = random.Random(derivar_semente("bootstrap-cruzado", semente))
    a, c = len(y), len(y[0][0])
    out = []
    for _ in range(reamostragens):
        ig = [rng.randrange(a) for _ in range(a)] if "G" in reamostrar else list(range(a))
        ir = [rng.randrange(c) for _ in range(c)] if "R" in reamostrar else list(range(c))
        out.append(estatistica([[[y[i][j][k] for k in ir] for j in range(len(y[i]))] for i in ig]))
    return out


def ic_percentil(valores: Sequence[float], nivel: float = 0.95) -> list[float]:
    v = sorted(valores)
    if not v:
        raise ValueError("ic_percentil sem valores")
    lo = (1.0 - nivel) / 2
    return [v[int(lo * len(v))], v[int((1.0 - lo) * len(v)) - 1]]


# ------------------------------------------------------------ forma final e diversidade (docs/PLANO_ANALISE_V21D.md)


def r2_por_categoria(valores: Sequence[float], categorias: Sequence[str]) -> dict:
    """Fracao da soma de quadrados de `valores` entre as `categorias` (r2 de um fator so). Mesma conta, na mesma
    ordem, do r2 da forma final de experiments/analisar_dono_ambiente.py."""
    if len(valores) != len(categorias) or not valores:
        raise ValueError("r2_por_categoria: valores e categorias vazios ou de tamanhos diferentes")
    m = sum(valores) / len(valores)
    grupos: dict[str, list[float]] = {}
    for v, c in zip(valores, categorias):
        grupos.setdefault(c, []).append(v)
    ss_tot = sum((v - m) ** 2 for v in valores)
    ss_ent = sum(len(v) * (sum(v) / len(v) - m) ** 2 for v in grupos.values())
    return {"r2": ss_ent / ss_tot if ss_tot > 0 else 0.0, "n_categorias": len(grupos),
            "media_por_categoria": {c: {"n": len(v), "media": sum(v) / len(v)} for c, v in sorted(grupos.items())}}


def kappa_fleiss(itens: Sequence[Sequence[str]]) -> dict:
    """Concordancia categorica: cada item e classificado pelo mesmo numero de avaliadores (aqui: a forma final de um
    genoma nos ambientes). Devolve o kappa de Fleiss e a concordancia media entre pares (P barra). Falha alto quando o
    kappa nao e definido (todos na mesma categoria) ou quando os itens tem numero diferente de avaliadores."""
    if not itens:
        raise ValueError("kappa_fleiss sem itens")
    n = len(itens[0])
    if n < 2 or any(len(x) != n for x in itens):
        raise ValueError("kappa_fleiss: todo item precisa do mesmo numero (>= 2) de avaliadores")
    total: dict[str, int] = {}
    p_itens = []
    for x in itens:
        cont: dict[str, int] = {}
        for c in x:
            cont[c] = cont.get(c, 0) + 1
            total[c] = total.get(c, 0) + 1
        p_itens.append((sum(k * k for k in cont.values()) - n) / (n * (n - 1)))
    p_barra = sum(p_itens) / len(p_itens)
    p_e = sum((k / (len(itens) * n)) ** 2 for k in total.values())
    if p_e >= 1.0:
        raise ValueError("kappa_fleiss indefinido: todas as classificacoes na mesma categoria")
    return {"kappa": (p_barra - p_e) / (1.0 - p_e), "concordancia_pares": p_barra, "acaso": p_e}


def qualidade_diversidade(valores: Sequence[float], categorias: Sequence[str], nichos: Sequence[str]) -> dict:
    """Cobertura (nichos com pelo menos um valor / numero de nichos) e QD-score (soma, nos nichos alcancados, da media
    dos valores do nicho). Categorias fora de `nichos` nao contam."""
    if len(valores) != len(categorias) or not nichos:
        raise ValueError("qualidade_diversidade: entradas invalidas")
    alvo = set(nichos)
    por: dict[str, list[float]] = {}
    for v, c in zip(valores, categorias):
        if c in alvo:
            por.setdefault(c, []).append(v)
    medias = {c: sum(v) / len(v) for c, v in sorted(por.items())}
    return {"cobertura": len(por) / len(alvo), "qd_score": sum(medias.values()), "media_por_nicho": medias,
            "n_por_nicho": {c: len(v) for c, v in sorted(por.items())}}


def icc_um_fator(tabela: Sequence[Sequence[float]]) -> float:
    """ICC(1) de um fator: linhas = sujeitos (genomas), colunas = avaliacoes (ambientes). (QM_entre - QM_dentro) /
    (QM_entre + (k - 1) QM_dentro). Pode sair negativa. Falha alto sem variancia."""
    n, k = len(tabela), len(tabela[0]) if tabela else 0
    if n < 2 or k < 2 or any(len(x) != k for x in tabela):
        raise ValueError("icc_um_fator: tabela precisa de >= 2 linhas e >= 2 colunas, todas do mesmo tamanho")
    gm = sum(v for x in tabela for v in x) / (n * k)
    medias = [sum(x) / k for x in tabela]
    qm_entre = k * sum((m - gm) ** 2 for m in medias) / (n - 1)
    qm_dentro = sum((v - medias[i]) ** 2 for i, x in enumerate(tabela) for v in x) / (n * (k - 1))
    den = qm_entre + (k - 1) * qm_dentro
    if den <= 0:
        raise ValueError("icc_um_fator indefinida: sem variancia")
    return (qm_entre - qm_dentro) / den


# ------------------------------------------------------------ V2, L1: tarefa ensinada (G3-T) e norma de reacao
# docs/PLANO_ANALISE_V2_L1.md, secoes 3.2 e 4.2; docs/DEFINICOES_V2.md, D1 e D4. Biblioteca padrao, uma vez so.


def acerto_na_tarefa(decisoes: Sequence[tuple[int, Mapping, str]], julgar, acoes: Sequence[str],
                     ticks_por_dia: int) -> dict:
    """G3-T. `decisoes` = [(tick, estado, acao)] de uma vida; `julgar(estado, acao) -> int` e a tarefa do dono
    (+1 elogia, -1 repreende, 0 nada a dizer; donos.julgar_acao). Por dia: n, acerto = fracao com +1 (o 0 conta
    como nao elogiado) e teto = fracao das decisoes em que ALGUMA das `acoes` teria +1 nos mesmos estados (a
    politica otima do dono, avaliada nos estados que o pet visitou)."""
    if ticks_por_dia <= 0:
        raise ValueError("ticks_por_dia precisa ser positivo")
    por_dia: dict[int, list[tuple[bool, bool]]] = {}
    for tick, estado, acao in decisoes:
        certo = julgar(estado, acao) == 1
        teto = any(julgar(estado, a) == 1 for a in acoes)
        por_dia.setdefault(tick // ticks_por_dia, []).append((certo, teto))
    if not por_dia:
        raise ValueError("vida sem decisoes")
    dias = sorted(por_dia)
    n = [len(por_dia[d]) for d in dias]
    acerto = [sum(c for c, _ in por_dia[d]) / len(por_dia[d]) for d in dias]
    teto = [sum(t for _, t in por_dia[d]) / len(por_dia[d]) for d in dias]
    total = sum(n)
    return {"dias": dias, "n": n, "acerto": acerto, "teto": teto,
            "acerto_total": sum(c for d in dias for c, _ in por_dia[d]) / total,
            "teto_total": sum(t for d in dias for _, t in por_dia[d]) / total}


def eficiencia_amostral(acerto_por_dia: Sequence[float], sinais_acumulados_por_dia: Sequence[int], piso: float,
                        maximo: float | None = None) -> dict:
    """Quantos sinais do dono (acumulados ate o fim do dia) ate o primeiro dia com acerto >= (piso + maximo) / 2.
    `maximo` = o maximo da curva, se nao vier. dia = None quando a curva nunca chega la."""
    if len(acerto_por_dia) != len(sinais_acumulados_por_dia) or not acerto_por_dia:
        raise ValueError("curva de acerto e sinais acumulados com tamanhos diferentes ou vazios")
    maximo = max(acerto_por_dia) if maximo is None else maximo
    alvo = 0.5 * (piso + maximo)
    for d, (a, s) in enumerate(zip(acerto_por_dia, sinais_acumulados_por_dia)):
        if a >= alvo:
            return {"alvo": alvo, "piso": piso, "maximo": maximo, "dia": d, "sinais": s}
    return {"alvo": alvo, "piso": piso, "maximo": maximo, "dia": None, "sinais": None}


def norma_de_reacao(y: Mapping[str, Mapping[str, Mapping[str, float]]], condicao_a: str, condicao_b: str) -> dict:
    """Regressao conjunta (Finlay-Wilkinson) para ovo x ambiente x condicao, y[condicao][ovo][ambiente].

    Indice do ambiente z_r = media de y de todos os pets (todas as condicoes e ovos) no ambiente r, centrada.
    Por (condicao, ovo): y = alpha + beta * z por minimos quadrados sobre os ambientes (alpha = nivel, beta =
    sensibilidade ao ambiente; com z centrado, alpha = media de y do pet). Devolve z, alpha e beta por celula,
    as medias por condicao e, por ovo, as diferencas alpha_a - alpha_b e beta_a - beta_b (para bootstrap fora)."""
    condicoes = list(y)
    if condicao_a not in y or condicao_b not in y:
        raise KeyError(f"condicoes {condicao_a!r} e {condicao_b!r} precisam estar em {condicoes}")
    ovos = sorted(y[condicao_a])
    ambientes = sorted(y[condicao_a][ovos[0]])
    if len(ambientes) < 2 or len(ovos) < 1:
        raise ValueError("precisa de pelo menos 2 ambientes e 1 ovo")
    for c in condicoes:
        if sorted(y[c]) != ovos or any(sorted(y[c][g]) != ambientes for g in ovos):
            raise ValueError(f"condicao {c!r} com ovos ou ambientes diferentes")
    z_bruto = {r: sum(y[c][g][r] for c in condicoes for g in ovos) / (len(condicoes) * len(ovos)) for r in ambientes}
    z_medio = sum(z_bruto.values()) / len(ambientes)
    z = {r: z_bruto[r] - z_medio for r in ambientes}
    szz = sum(v * v for v in z.values())
    if szz <= 0.0:
        raise ValueError("ambientes sem variacao: o indice do ambiente e constante")
    celulas: dict[str, dict[str, dict]] = {}
    for c in condicoes:
        celulas[c] = {}
        for g in ovos:
            ym = sum(y[c][g][r] for r in ambientes) / len(ambientes)
            beta = sum(z[r] * (y[c][g][r] - ym) for r in ambientes) / szz
            celulas[c][g] = {"alpha": ym, "beta": beta}
    medias = {c: {"alpha": sum(celulas[c][g]["alpha"] for g in ovos) / len(ovos),
                  "beta": sum(celulas[c][g]["beta"] for g in ovos) / len(ovos)} for c in condicoes}
    dif = {g: {"alpha": celulas[condicao_a][g]["alpha"] - celulas[condicao_b][g]["alpha"],
               "beta": celulas[condicao_a][g]["beta"] - celulas[condicao_b][g]["beta"]} for g in ovos}
    return {"ambientes": ambientes, "ovos": ovos, "z": z, "celulas": celulas, "medias": medias,
            "diferenca_por_ovo": dif, "condicoes": [condicao_a, condicao_b]}


# ------------------------------------------------------------ V2, bancada: a pergunta maior
# docs/TAREFA_V2_BANCADA.md, docs/ARQUITETURA_V2_VALIDACAO.md (secao 6): "vantagem adaptativa" = desempenho no proprio
# ambiente (nunca a forca na arena); a plasticidade tem custo (deriva ao prior, tempo ate aprender). Biblioteca padrao.


def desempenho_no_ambiente(amostras: Sequence[tuple[bool, float]]) -> dict:
    """Desempenho no proprio ambiente a partir de amostras do estado do pet em instantes igualmente espacados (a bancada
    amostra em cada decisao, a cada `Config.intervalo_decisao_ticks`). Cada amostra = (em_privacao, saude), com
    `em_privacao` dado por `Estado.em_privacao` (a regra mora no estado, nao aqui). Devolve a fracao do tempo FORA de
    privacao e a saude media."""
    if not amostras:
        raise ValueError("vida sem amostras de estado")
    n = len(amostras)
    fora = 0
    saude = 0.0
    for em_privacao, s in amostras:
        if type(em_privacao) is not bool:
            raise TypeError(f"em_privacao precisa ser bool: {em_privacao!r}")
        if not 0.0 <= s <= 1.0:
            raise ValueError(f"saude fora de [0, 1]: {s!r}")
        fora += not em_privacao
        saude = saude + s
    return {"n": n, "fracao_fora_de_privacao": fora / n, "saude_media": saude / n}


def custo_da_plasticidade(deriva_por_dia: Sequence[float], acerto_por_dia: Sequence[float],
                          sinais_acumulados_por_dia: Sequence[int], piso: float) -> dict:
    """Custo da plasticidade de uma vida. `deriva_por_dia[d]` = JSD (bits) entre a politica no fim do dia d + 1 e a do
    prior herdado, nas mesmas sondas; o tempo ate aprender e o dia (e os sinais) em que o acerto na tarefa chega a metade
    do caminho entre `piso` (o acerto do prior na mesma vida) e o maximo da curva, pela `eficiencia_amostral`."""
    if not deriva_por_dia:
        raise ValueError("serie de deriva vazia")
    if any(d < 0.0 for d in deriva_por_dia):
        raise ValueError("deriva negativa: JSD e >= 0")
    return {"deriva_por_dia": list(deriva_por_dia), "deriva_final": deriva_por_dia[-1], "deriva_maxima": max(deriva_por_dia),
            "tempo_ate_metade": eficiencia_amostral(acerto_por_dia, sinais_acumulados_por_dia, piso)}


def tabela_braco_condicao(valores: Mapping[tuple[str, str], Sequence[float]], reamostragens: int, semente: int,
                          nivel: float) -> dict:
    """Tabela braco x condicao de uma medida: `valores[(braco, condicao)]` = um valor por unidade (vida). Por celula: n,
    media e IC percentil por bootstrap sobre as unidades (`bootstrap_ic`). A grade precisa ser completa (todo braco em
    toda condicao) e toda celula precisa de pelo menos 2 unidades: falha alto, nunca deixa celula vazia."""
    if not valores:
        raise ValueError("tabela sem celulas")
    bracos = sorted({b for b, _ in valores})
    condicoes = sorted({c for _, c in valores})
    faltam = [(b, c) for b in bracos for c in condicoes if (b, c) not in valores]
    if faltam:
        raise ValueError(f"grade braco x condicao incompleta: faltam {faltam}")
    celulas = {b: {c: bootstrap_ic([float(v) for v in valores[(b, c)]], reamostragens, semente, nivel) for c in condicoes}
               for b in bracos}
    return {"bracos": bracos, "condicoes": condicoes, "celulas": celulas}

# ------------------------------------------------------------ V2, A1: a bola (docs/PLANO_ANALISE_V2_A1.md, secao 2)


def resposta_a_bola(decisoes: Sequence[tuple[int, bool, str, str]], acao: str = "brincar",
                    regras: Sequence[str] = ("tempo_livre", "bola_no_cenario")) -> dict:
    """1a-pet: `decisoes` = (tick, bola presente, regra do instinto, acao do pet). Nas decisoes de tempo livre (as unicas em
    que a bola pode pesar), p(acao | bola presente) e p(acao | bola ausente), e a diferenca. None quando um lado nao tem decisao."""
    com = [a for _, b, r, a in decisoes if b and r in regras]
    sem = [a for _, b, r, a in decisoes if not b and r in regras]
    p_com = sum(a == acao for a in com) / len(com) if com else None
    p_sem = sum(a == acao for a in sem) / len(sem) if sem else None
    return {"n_decisoes": len(decisoes), "n_com_bola": sum(1 for _, b, _, _ in decisoes if b),
            "n_livre_com_bola": len(com), "n_livre_sem_bola": len(sem), "p_com_bola": p_com, "p_sem_bola": p_sem,
            "delta": (p_com - p_sem) if p_com is not None and p_sem is not None else None}


def privacao_nas_decisoes(decisoes: Sequence[tuple[int, float, float, float, float]], limiar: float) -> dict:
    """Cuidado controlado (G5 descritivo): `decisoes` = (tick, fome, higiene, energia, humor) no tick de cada decisao.
    Fracao das decisoes em privacao (min(fome, higiene, energia) < limiar), humor e energia medios."""
    if not decisoes:
        raise ValueError("sem decisoes")
    n = len(decisoes)
    return {"n_decisoes": n,
            "fracao_privacao": sum(1 for _, f, h, e, _ in decisoes if min(f, h, e) < limiar) / n,
            "humor_medio": sum(hu for *_, hu in decisoes) / n,
            "energia_media": sum(e for _, _, _, e, _ in decisoes) / n}


# ------------------------------------------------------------ V2, N4: as frutas (docs/PLANO_ANALISE_V2_N4.md, secao 2)


def comer_por_incentivo(decisoes: Sequence[tuple[str, bool, float, str]],
                        regras: Sequence[str] = ("tempo_livre", "fruta_no_cenario")) -> dict:
    """G-SEP (i): `decisoes` = (regra do instinto, ha fruta no cenario, maior incentivo visto, acao). Nas decisoes de tempo livre com
    fruta, p(comer | incentivo >= mediana) - p(comer | incentivo < mediana). A mediana e a da propria lista. None se um lado vazio."""
    xs = [(x, a == "comer") for r, presente, x, a in decisoes if presente and r in regras]
    if not xs:
        return {"n": 0, "mediana": None, "p_alto": None, "p_baixo": None, "delta": None, "p_comer": None}
    ordenados = sorted(x for x, _ in xs)
    n = len(ordenados)
    mediana = ordenados[n // 2] if n % 2 else 0.5 * (ordenados[n // 2 - 1] + ordenados[n // 2])
    alto = [c for x, c in xs if x >= mediana]
    baixo = [c for x, c in xs if x < mediana]
    p_alto = sum(alto) / len(alto) if alto else None
    p_baixo = sum(baixo) / len(baixo) if baixo else None
    return {"n": n, "mediana": mediana, "p_alto": p_alto, "p_baixo": p_baixo, "p_comer": sum(c for _, c in xs) / n,
            "delta": (p_alto - p_baixo) if p_alto is not None and p_baixo is not None else None}


def escolha_por_incentivo(ofertas: Sequence[tuple[Sequence[str], Mapping[str, float], str | None]]) -> dict:
    """G-SEP (ii): `ofertas` = (frutas no cenario, incentivo de cada uma antes da escolha, fruta escolhida ou None). Nas escolhas com
    pelo menos duas frutas, a fracao em que a escolhida e uma das de maior incentivo, menos a esperada sem incentivo (media de 1/n)."""
    casos = [(list(p), inc, e) for p, inc, e in ofertas if e is not None and len(p) >= 2]
    if not casos:
        return {"n": 0, "acerto": None, "acaso": None, "delta": None}
    acertos = 0
    acaso = 0.0
    for p, inc, e in casos:
        if e not in p:
            raise ValueError(f"fruta escolhida {e!r} fora do cenario {p}")
        topo = max(inc[f] for f in p)
        acertos += inc[e] == topo
        acaso += 1.0 / len(p)
    n = len(casos)
    return {"n": n, "acerto": acertos / n, "acaso": acaso / n, "delta": acertos / n - acaso / n}


def saciedade_especifica(consumos: Sequence[tuple[float, float, float]]) -> dict:
    """G-SSE: `consumos` = (avaliacao registrada, consumo recente daquela fruta antes, fome antes). Minimos quadrados de
    avaliacao ~ 1 + recente + fome. Falha alto com menos de 4 consumos ou sistema singular."""
    if len(consumos) < 4:
        raise ValueError(f"saciedade_especifica precisa de pelo menos 4 consumos, recebeu {len(consumos)}")
    X = [(1.0, r, f) for _, r, f in consumos]
    y = [a for a, _, _ in consumos]
    XtX = [[sum(x[i] * x[j] for x in X) for j in range(3)] for i in range(3)]
    Xty = [sum(x[i] * yi for x, yi in zip(X, y)) for i in range(3)]
    b = _resolver(XtX, Xty)
    return {"n": len(consumos), "intercepto": b[0], "beta_recente": b[1], "beta_fome": b[2]}


# ------------------------------------------------------------ V2, bancada das frutas: a predicao do experimento maior
# docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md, secao 4.1 e 4.3: a medida primaria e a fracao dos consumos de fruta em que o pet
# comeu a fruta que, NAQUELE momento, tinha o efeito ruim (no mutavel a fruta ruim troca no meio da vida).


def taxa_fruta_ruim(consumos: Sequence[tuple[int, float]], janelas: Mapping[str, tuple[int, int]]) -> dict:
    """`consumos` = (tick, efeito no humor aplicado naquele consumo); ruim = efeito < 0 (o efeito vigente no consumo, entao a troca
    do mutavel ja esta dentro dele). `janelas` = nome -> [inicio, fim) em ticks. Por janela: n consumos, quantos ruins e a taxa;
    taxa None quando a janela nao tem consumo (o pet nao comeu fruta ali: nao e zero)."""
    for nome, (ini, fim) in janelas.items():
        if not (isinstance(ini, int) and isinstance(fim, int)) or ini < 0 or fim <= ini:
            raise ValueError(f"janela {nome!r} invalida: [{ini}, {fim})")
    out = {}
    for nome, (ini, fim) in janelas.items():
        sel = [e for t, e in consumos if ini <= t < fim]
        ruins = sum(e < 0.0 for e in sel)
        out[nome] = {"inicio": ini, "fim": fim, "n": len(sel), "ruins": ruins, "taxa": ruins / len(sel) if sel else None}
    return out


def saciedade_especifica_n1(consumos: Sequence[tuple[float, float, float, float]]) -> dict:
    """N1 (decisao do Matheus, rodada 4; docs/RESULTADO_V2_N4.md): a saciedade sensorio-especifica COM o termo da preferencia inata.
    `consumos` = (avaliacao registrada, preferencia inata daquela fruta, consumo recente dela antes, fome antes). Minimos quadrados de
    avaliacao ~ 1 + preferencia + recente + fome. A queda especifica e beta_recente (< 0); beta_fome ~ 0 se a fome nao entra; beta_pref
    ~ 1 se a avaliacao parte da preferencia. Sem o termo da preferencia (saciedade_especifica), a diferenca de preferencia entre frutas
    vaza para os outros coeficientes. Ao lado, a queda media por unidade de consumo recente, (preferencia - avaliacao) / recente, nos
    consumos com recente > 0. Falha alto com menos de 5 consumos ou sistema singular."""
    if len(consumos) < 5:
        raise ValueError(f"saciedade_especifica_n1 precisa de pelo menos 5 consumos, recebeu {len(consumos)}")
    X = [(1.0, p, r, f) for _, p, r, f in consumos]
    y = [a for a, _, _, _ in consumos]
    XtX = [[sum(x[i] * x[j] for x in X) for j in range(4)] for i in range(4)]
    Xty = [sum(x[i] * yi for x, yi in zip(X, y)) for i in range(4)]
    b = _resolver(XtX, Xty)
    quedas = [(p - a) / r for a, p, r, _ in consumos if r > 0.0]
    return {"n": len(consumos), "intercepto": b[0], "beta_pref": b[1], "beta_recente": b[2], "beta_fome": b[3],
            "queda_por_unidade": (sum(quedas) / len(quedas)) if quedas else None, "n_com_recente": len(quedas)}


# ------------------------------------------------------------ V2, bancada do N5: eficiencia sobre a taxa da fruta ruim
# docs/PLANO_ANALISE_V2_N5.md, secao 5 (e o experimento maior, predicao 3): consumos ate a metade do caminho, com censura a direita.


def consumos_ate_metade(taxa_por_dia: Sequence[float | None], consumos_por_dia: Sequence[int], taxa_p0: float | None) -> dict:
    """Consumos de fruta ate o fim do primeiro dia em que a `taxa_fruta_ruim` DO DIA chega a metade do caminho entre a do P0 da mesma
    unidade (`taxa_p0`) e 0, pela `eficiencia_amostral` (acerto = 1 - taxa, piso = 1 - taxa_p0, maximo = 1). Dia sem consumo (taxa None)
    nunca chega. Se nunca chega, conta o total de consumos da vida e marca `censurado` (censura a direita, plano do N5). Sem taxa do
    P0 (o P0 nao comeu fruta) nao ha caminho: devolve `sem_referencia`."""
    if len(taxa_por_dia) != len(consumos_por_dia) or not taxa_por_dia:
        raise ValueError("taxa por dia e consumos por dia com tamanhos diferentes ou vazios")
    if any(c < 0 for c in consumos_por_dia):
        raise ValueError("consumo negativo")
    total = sum(consumos_por_dia)
    if taxa_p0 is None:
        return {"sem_referencia": True, "alvo": None, "dia": None, "consumos": None, "censurado": None, "total": total}
    if not 0.0 <= taxa_p0 <= 1.0:
        raise ValueError(f"taxa do P0 fora de [0, 1]: {taxa_p0!r}")
    acerto = [float("-inf") if t is None else 1.0 - t for t in taxa_por_dia]
    acumulados, soma = [], 0
    for c in consumos_por_dia:
        soma += c
        acumulados.append(soma)
    e = eficiencia_amostral(acerto, acumulados, 1.0 - taxa_p0, maximo=1.0)
    chegou = e["dia"] is not None
    return {"sem_referencia": False, "alvo": 1.0 - e["alvo"], "dia": e["dia"], "consumos": e["sinais"] if chegou else total,
            "censurado": not chegou, "total": total}


def tabela_braco_condicao_parcial(valores: Mapping[tuple[str, str], Sequence[float | None]], reamostragens: int, semente: int,
                                  nivel: float) -> dict:
    """A `tabela_braco_condicao` para medidas que podem faltar numa vida (None: a taxa de uma janela sem consumo). A grade tem de ser
    completa; por celula: quantas vidas tem valor e quantas nao, e o IC por bootstrap so com 2 ou mais valores (senao a media, se houver
    uma, e `ic` None com o motivo). Nada some sem ser contado."""
    if not valores:
        raise ValueError("tabela sem celulas")
    bracos = sorted({b for b, _ in valores})
    condicoes = sorted({c for _, c in valores})
    faltam = [(b, c) for b in bracos for c in condicoes if (b, c) not in valores]
    if faltam:
        raise ValueError(f"grade braco x condicao incompleta: faltam {faltam}")
    celulas: dict[str, dict] = {}
    for b in bracos:
        celulas[b] = {}
        for c in condicoes:
            todos = list(valores[(b, c)])
            com = [float(v) for v in todos if v is not None]
            cel = {"n": len(com), "sem_valor": len(todos) - len(com)}
            if len(com) >= 2:
                cel["ic"] = bootstrap_ic(com, reamostragens, semente, nivel)
            else:
                cel["ic"] = None
                cel["media"] = com[0] if com else None
                cel["motivo"] = "menos de 2 vidas com valor"
            celulas[b][c] = cel
    return {"bracos": bracos, "condicoes": condicoes, "celulas": celulas}


# ------------------------------------------------------------ V2, experimento maior: contrastes pareados, Holm, equivalencia
# docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md, secoes 5, 6 e 7. O contraste e orientado por quem chama: positivo = o que a predicao diz.


def _medias_bootstrap_agrupadas(grupos: Sequence[Sequence[float]], reamostragens: int, semente: int) -> list[float]:
    """Medias reamostradas, sorteando os GRUPOS (a unidade de ambiente, a semente) com reposicao e todos os valores de cada grupo
    juntos (secao 6.2). Com um valor por grupo, sao as mesmas medias do `bootstrap_ic` (mesma rng, mesma ordem de soma)."""
    rng = random.Random(derivar_semente("bootstrap", semente))
    k = len(grupos)
    medias = []
    for _ in range(reamostragens):
        vals: list[float] = []
        for _ in range(k):
            vals.extend(grupos[rng.randrange(k)])
        medias.append(sum(vals) / len(vals))
    return sorted(medias)


def _percentis(medias_ordenadas: Sequence[float], nivel: float) -> tuple[float, float]:
    r = len(medias_ordenadas)
    alfa = (1.0 - nivel) / 2.0
    return (medias_ordenadas[int(math.floor(alfa * (r - 1)))], medias_ordenadas[int(math.ceil((1.0 - alfa) * (r - 1)))])


def _beta_cf(a: float, b: float, x: float) -> float:
    """Fracao continuada da beta incompleta (Lentz modificado)."""
    pequeno = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > pequeno else pequeno)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        for num in (m * (b - m) * x / ((a + m2 - 1.0) * (a + m2)), -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1.0))):
            d = 1.0 + num * d
            d = 1.0 / (d if abs(d) > pequeno else pequeno)
            c = 1.0 + num / c
            c = c if abs(c) > pequeno else pequeno
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            return h
    raise ArithmeticError("beta incompleta nao convergiu")


def beta_incompleta(a: float, b: float, x: float) -> float:
    """I_x(a, b), a beta incompleta regularizada."""
    if not 0.0 <= x <= 1.0:
        raise ValueError(f"x fora de [0, 1]: {x!r}")
    if x in (0.0, 1.0):
        return x
    ln = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(ln) * _beta_cf(a, b, x) / a
    return 1.0 - math.exp(ln) * _beta_cf(b, a, 1.0 - x) / b


def t_unilateral(t: float, gl: int) -> float:
    """P(T >= t) para a t de Student com gl graus de liberdade."""
    if gl < 1:
        raise ValueError("gl < 1")
    cauda = 0.5 * beta_incompleta(gl / 2.0, 0.5, gl / (gl + t * t))
    return cauda if t >= 0 else 1.0 - cauda


def contraste_pareado(grupos: Mapping[object, Sequence[float]], reamostragens: int, semente: int) -> dict:
    """Contraste pareado por unidade (secao 6), ja orientado: positivo = a direcao predita. `grupos` = {semente: [diferencas das
    unidades daquela semente]}. Devolve a media, os ICs percentis de 95% e 90% (a mesma reamostragem), o p unilateral do bootstrap
    (a fracao das medias reamostradas <= 0, o lado oposto) e, como conferencia, o teste t pareado unilateral sobre as unidades.
    Com menos de 2 grupos nao ha bootstrap: os ICs e o p ficam None, com o motivo."""
    gs = [list(map(float, v)) for _, v in sorted(grupos.items(), key=lambda kv: repr(kv[0])) if len(v)]
    valores = [x for g in gs for x in g]
    out: dict = {"n": len(valores), "n_grupos": len(gs), "media": (sum(valores) / len(valores)) if valores else None,
                 "ic95": None, "ic90": None, "p_unilateral": None, "t_pareado": None, "motivo": None}
    if len(gs) < 2:
        out["motivo"] = "menos de 2 grupos com valor"
        return out
    medias = _medias_bootstrap_agrupadas(gs, reamostragens, semente)
    for chave, nivel in (("ic95", 0.95), ("ic90", 0.90)):
        lo, hi = _percentis(medias, nivel)
        out[chave] = {"ic_inferior": lo, "ic_superior": hi, "nivel": nivel}
    out["p_unilateral"] = sum(1 for m in medias if m <= 0.0) / reamostragens
    n = len(valores)
    media = out["media"]
    var = sum((x - media) ** 2 for x in valores) / (n - 1)
    if var > 0.0:
        t = media / math.sqrt(var / n)
        out["t_pareado"] = {"t": t, "gl": n - 1, "p_unilateral": t_unilateral(t, n - 1)}
    return out


def holm(p: Mapping[str, float | None], alfa: float) -> dict:
    """Correcao de Holm (passo a passo descendente) sobre a familia inteira. p None (o contraste nao teve teste) conta como 1: a
    familia nao encolhe. Por hipotese: o p, a ordem, o limiar alfa/(m - i), se rejeita e o p ajustado."""
    if not p:
        raise ValueError("familia vazia")
    if not 0.0 < alfa < 1.0:
        raise ValueError(f"alfa fora de (0, 1): {alfa!r}")
    m = len(p)
    ordem = sorted(p, key=lambda k: (1.0 if p[k] is None else p[k], k))
    out, parou, ajustado = {}, False, 0.0
    for i, k in enumerate(ordem):
        pk = 1.0 if p[k] is None else float(p[k])
        limiar = alfa / (m - i)
        rejeita = not parou and pk <= limiar
        parou = parou or not rejeita
        ajustado = max(ajustado, min(1.0, (m - i) * pk))
        out[k] = {"p": p[k], "ordem": i + 1, "limiar": limiar, "rejeita": rejeita, "p_ajustado": ajustado}
    return out


def dentro_da_margem(ic: Mapping[str, float] | None, delta: float | None) -> bool:
    """O IC inteiro dentro de (-delta, +delta) (equivalencia por dois testes unilaterais, pelo IC de 90%)."""
    if ic is None or delta is None:
        return False
    return -delta < ic["ic_inferior"] and ic["ic_superior"] < delta


def inclinacao_mmq(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Inclinacao de minimos quadrados de y em x (pelo menos 2 x distintos)."""
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("inclinacao precisa de 2 pontos ou mais")
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0.0:
        raise ValueError("x todos iguais")
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def tamanho_amostra(desvio_d: float, delta: float, alfa: float, poder: float, multiplo: int = 1) -> int:
    """N = ((z_{1-alfa} + z_poder) * sigma_d / delta)^2, unilateral (secao 7.2), arredondado para cima ao multiplo."""
    if delta <= 0.0 or desvio_d < 0.0 or not 0.0 < alfa < 1.0 or not 0.0 < poder < 1.0 or multiplo < 1:
        raise ValueError("tamanho_amostra: delta > 0, desvio >= 0, alfa e poder em (0, 1), multiplo >= 1")
    from statistics import NormalDist
    z = NormalDist().inv_cdf
    n = math.ceil(((z(1.0 - alfa) + z(poder)) * desvio_d / delta) ** 2)
    return max(multiplo, -(-n // multiplo) * multiplo)


# ------------------------------------------------------------ V2, N6: a memoria de episodios (docs/PLANO_ANALISE_V2_N6.md, secoes 6 e 8)


def memoria_nas_subdecisoes(subdecisoes: Sequence[tuple[int, str, str, int]], total_decisoes: int) -> dict:
    """A memoria na escolha da fruta. `subdecisoes` = uma por sub-decisao da fruta: (frutas no cenario, escolha, escolha da sonda
    contrafactual com m_f = 0 e o mesmo u, episodios recuperados). Sobre as sub-decisoes com 2 frutas ou mais (as unicas em que a
    memoria pode agir; N6-7): a fracao decidida pela memoria (escolha diferente da sonda; G-CITA) e a cobertura (com pelo menos um
    episodio recuperado). Sobre TODAS as decisoes do pet (`total_decisoes`, o denominador da v1): a fracao de motivos que citam a
    memoria (so descritiva: por construcao fica abaixo da da v1, secao 8). E os episodios decisivos (H-MEM-02): das sub-decisoes com
    recuperacao, quantas mudaram. Fracao None sem denominador."""
    if total_decisoes < 0:
        raise ValueError("total de decisoes negativo")
    duas = [s for s in subdecisoes if s[0] >= 2]
    for n, escolha, sem, rec in subdecisoes:
        if n < 1 or rec < 0 or not escolha or not sem:
            raise ValueError(f"sub-decisao invalida: {(n, escolha, sem, rec)}")
        if n == 1 and escolha != sem:
            raise ValueError("com uma fruta so a memoria nao muda a escolha")
    mudou = sum(1 for _, e, s, _ in duas if e != s)
    com_rec = [x for x in duas if x[3] > 0]
    if mudou > total_decisoes:
        raise ValueError("mais escolhas mudadas que decisoes")
    frac = lambda a, b: (a / b) if b else None  # noqa: E731
    return {"subdecisoes": len(subdecisoes), "subdecisoes_2_mais": len(duas), "mudou": mudou,
            "fracao_decidida": frac(mudou, len(duas)), "com_recuperacao": len(com_rec),
            "cobertura": frac(len(com_rec), len(duas)),
            "decisivas_entre_recuperadas": frac(sum(1 for _, e, s, _ in com_rec if e != s), len(com_rec)),
            "total_decisoes": total_decisoes, "fracao_motivos_total": frac(mudou, total_decisoes)}


def ocupacao_espacos_frutas(instantes: Sequence[tuple[Sequence[str], Sequence[str]]], frutas: Sequence[str]) -> dict:
    """Ocupacao dos espacos da memoria (como experiments/memoria_espacos.py): `instantes` = (frutas no curto prazo, frutas no longo
    prazo) a cada decisao. Media de espacos ocupados em cada prazo, e por fruta a fracao do tempo na memoria (qualquer prazo) e no
    longo prazo (risco 2 do plano: a fruta ruim no longo prazo)."""
    if not instantes:
        raise ValueError("ocupacao sem instantes")
    n = len(instantes)
    for curto, longo in instantes:
        if any(f not in frutas for f in list(curto) + list(longo)):
            raise ValueError(f"fruta fora de {list(frutas)}")
        if len(set(curto)) != len(curto) or len(set(longo)) != len(longo):
            raise ValueError("no maximo um episodio por fruta em cada prazo")
    return {"curto_medio": sum(len(c) for c, _ in instantes) / n, "longo_medio": sum(len(l) for _, l in instantes) / n,
            "na_memoria": {f: sum(1 for c, l in instantes if f in c or f in l) / n for f in frutas},
            "no_longo": {f: sum(1 for _, l in instantes if f in l) / n for f in frutas}, "instantes": n}


# ------------------------------------------------------------ V2, N7: a arbitragem (docs/PLANO_ANALISE_V2_N7.md, secao 6)

ZONAS_CONFLITO = ("fome_moderada", "fruta_no_cenario")       # onde `comer` e candidato e a necessidade nao e urgente (secao 3)


def quem_decidiu_conflito(comeu: bool, comeria_sem_pedido: bool) -> str:
    """Numa decisao de conflito: "pedido" quando o pet nao comeu e, com o mesmo u e o termo do pedido zerado, teria comido;
    "necessidade" quando comeu (a necessidade ou o gosto venceu); "ninguem" quando nao comeria de qualquer jeito."""
    if comeu:
        return "necessidade"
    return "pedido" if comeria_sem_pedido else "ninguem"


def deferencia_ao_pedido(decisoes: Sequence[tuple[int, str, bool, bool, bool]], janelas: Mapping[str, tuple[int, int]]) -> dict:
    """`decisoes` = (tick, regra, conflito, comeu, comeria_sem_pedido) por decisao do pet. Conflito = regra numa ZONAS_CONFLITO com
    toda fruta do cenario com pedido vigente. Por zona e janela ([inicio, fim) em ticks): conflitos, quantos o pedido decidiu e a
    deferencia (fracao; None sem conflito), mais o total por janela. G-URG: as decisoes FORA das zonas (as regras urgentes: sono,
    pedido_necessidade, abandono) em que o pedido mudou a decisao contam como violacao (tem de ser 0)."""
    out: dict = {"por_janela": {}, "violacoes_urgentes": 0, "conflitos": 0}
    for tick, regra, conflito, comeu, sem in decisoes:
        if conflito and regra not in ZONAS_CONFLITO:
            raise ValueError(f"conflito fora das zonas {ZONAS_CONFLITO}: {regra!r}")
        if regra not in ZONAS_CONFLITO and not comeu and sem:
            out["violacoes_urgentes"] += 1
    for nome, (ini, fim) in janelas.items():
        cel = {}
        for zona in ZONAS_CONFLITO + ("total",):
            sel = [d for d in decisoes if d[2] and ini <= d[0] < fim and (zona == "total" or d[1] == zona)]
            pelo_pedido = sum(1 for d in sel if quem_decidiu_conflito(d[3], d[4]) == "pedido")
            cel[zona] = {"conflitos": len(sel), "pelo_pedido": pelo_pedido,
                         "pela_necessidade": sum(1 for d in sel if d[3]), "deferencia": (pelo_pedido / len(sel)) if sel else None}
        out["por_janela"][nome] = cel
    out["conflitos"] = sum(1 for d in decisoes if d[2])
    return out


def fracao_da_fruta(consumos: Sequence[tuple[int, str, Sequence[str]]], fruta: str, janelas: Mapping[str, tuple[int, int]]) -> dict:
    """A fracao de X (secao 6): `consumos` = (tick, fruta comida, frutas no cenario). Por janela, entre os consumos em ofertas com
    `fruta` E outra fruta no cenario, a fracao em que o pet comeu `fruta`; n e taxa None sem consumo (a unidade fica fora daquele
    contraste, com o numero reportado)."""
    for _, f, presentes in consumos:
        if f not in presentes:
            raise ValueError(f"comeu {f!r} fora do cenario {list(presentes)}")
    out = {}
    for nome, (ini, fim) in janelas.items():
        sel = [f for t, f, p in consumos if ini <= t < fim and fruta in p and len(set(p)) >= 2]
        x = sum(1 for f in sel if f == fruta)
        out[nome] = {"inicio": ini, "fim": fim, "n": len(sel), "de_x": x, "taxa": (x / len(sel)) if sel else None}
    return out


def dia_cruza_zero(serie_por_dia: Sequence[float]) -> int | None:
    """O primeiro dia (1, 2, ...) em que a serie (w_pedido no fim de cada dia, que parte de w0 > 0) fica <= 0; None se nunca."""
    for d, v in enumerate(serie_por_dia):
        if v <= 0:
            return d + 1
    return None


def multiconjunto_informacoes(informacoes: Sequence[Mapping]) -> dict[str, int]:
    """P2D-P3I (adendo 3, secao 3.3): o multiconjunto (fruta, conteudo) das informacoes de uma vida, {"<fruta>/<conteudo>": n}, em ordem.
    Le o registro do motor das frutas (`MotorFrutas.informacoes`: dicts com "fruta" e "conteudo")."""
    cont: dict[str, int] = {}
    for i in informacoes:
        k = f"{i['fruta']}/{i['conteudo']}"
        cont[k] = cont.get(k, 0) + 1
    return dict(sorted(cont.items()))


# ------------------------------------------------------------ V2, rodada 17: as medidas do mundo fisico, do corpo e do banheiro
# (W-MEDIDAS-R17, docs/V2_RODADA_17.md). Funcoes puras sobre listas simples de eventos. O motor do mundo e o corpo novo ainda nao estao
# na main: cada docstring diz o que o motor precisa fornecer. Posicoes em subunidades, 16 por celula (docs/TAREFA_V2_MUNDO_FISICO.md,
# secao 3); 1 tick = 1 minuto.

SUBUNIDADES_POR_CELULA = 16
REGRAS_TEMPO_LIVRE = ("tempo_livre", "bola_no_cenario")
ATIVIDADES_TEDIO = ("bola", "brincar", "explorar", "dono_brinca")     # as que o corpo guarda na janela do tedio (corpo, adendo 1, A1.2)


def janela_dias(primeiro: int, ultimo: int) -> tuple[int, int]:
    """Os dias `primeiro` a `ultimo` (1 = o dia do nascimento; os dois entram) como [inicio, fim) em ticks."""
    if primeiro < 1 or ultimo < primeiro:
        raise ValueError(f"dias invalidos: {primeiro} a {ultimo}")
    return (primeiro - 1) * TICKS_POR_DIA, ultimo * TICKS_POR_DIA


JANELA_8_14 = janela_dias(8, 14)          # a janela das medidas dos tres planos


def _checar_janela(janela: tuple[int, int]) -> tuple[int, int]:
    ini, fim = janela
    if not (isinstance(ini, int) and isinstance(fim, int)) or ini < 0 or fim <= ini:
        raise ValueError(f"janela invalida: [{ini}, {fim})")
    return ini, fim


def _escala01(nome: str, v: float) -> float:
    if not 0.0 <= v <= 1.0:
        raise ValueError(f"{nome} fora de [0, 1]: {v!r}")
    return v


# --- o mundo fisico (docs/PLANO_ANALISE_V2_MUNDO_FISICO.md)


def deficit_fome_energia(decisoes: Sequence[tuple[int, float, float]], janela: tuple[int, int] = JANELA_8_14) -> dict:
    """D_FE, a primaria (secao 5.1; no adendo 1, P0 - P1 em malha fechada): a media, nas decisoes da janela, de
    ((1 - fome) + (1 - energia)) / 2. O motor fornece, por decisao do pet, (tick, fome, energia) no estado em que ele decide (o da
    `Observacao`), na escala 0-1. A vida toda (o descritivo) e a mesma conta com `janela_dias(1, 14)`. Falha alto sem decisao na
    janela."""
    ini, fim = _checar_janela(janela)
    sel = [(_escala01("fome", f), _escala01("energia", e)) for t, f, e in decisoes if ini <= t < fim]
    if not sel:
        raise ValueError("D_FE sem decisao na janela")
    return {"n": len(sel), "d_fe": sum((2.0 - f - e) / 2.0 for f, e in sel) / len(sel)}


def custo_viagem(arvores: Mapping[str, tuple[int, int]]) -> dict[str, float]:
    """A1.8: o custo de viagem de cada arvore, a distancia do tronco dela ao tronco da arvore mais proxima, em celulas:
    isqrt(dx^2 + dy^2) em subunidades, dividido por 16. `arvores` = id -> (x, y) do tronco em subunidades, do layout da `ConfigMundo`
    (convertido de celulas como o motor converte). E fixo pelo layout."""
    if len(arvores) < 2:
        raise ValueError("custo de viagem precisa de 2 arvores ou mais")
    out = {}
    for a, (xa, ya) in arvores.items():
        d = min(math.isqrt((xa - xb) ** 2 + (ya - yb) ** 2) for b, (xb, yb) in arvores.items() if b != a)
        out[a] = d / SUBUNIDADES_POR_CELULA
    return out


def taxa_recente(quedas: Sequence[int], tick: int, horas: int = 24) -> float | None:
    """As frutas caidas por hora nas `horas` antes de `tick`, [tick - horas*60, tick). `quedas` = o tick de cada queda de fruta, de todas
    as arvores (o fluxo `mundo-arvores`, que nao depende do pet). None quando a janela comeca antes do nascimento."""
    if tick - horas * 60 < 0:
        return None
    return sum(1 for q in quedas if tick - horas * 60 <= q < tick) / horas


def visitas_manchas(trajetoria: Sequence[tuple[int, int, int]], arvores: Mapping[str, tuple[int, int]], tick_fim: int,
                    janela: tuple[int, int] = JANELA_8_14, quedas: Sequence[int] | None = None, raio_celulas: int = 3) -> list[dict]:
    """As visitas as manchas (A1.8). O motor fornece:
    - `trajetoria`: (tick, x, y), uma entrada por decisao do pet, mesmo sem deslocamento, em ordem de tick: a posicao depois do
      deslocamento daquela decisao, que vale de `tick` ate a entrada seguinte (o motor anda de uma vez, na decisao; tarefa, secao 5).
      A primeira e o nascimento, no ninho;
    - `arvores`: id -> (x, y) do tronco, em subunidades; `tick_fim`: o fim da vida;
    - `quedas` (opcional): os ticks das quedas de fruta, para a `taxa_recente` de cada visita.

    Mancha = a ate `raio_celulas` do tronco, isqrt(dx^2 + dy^2) <= raio_celulas * 16. Cada arvore tem as suas visitas, e manchas que se
    sobrepoem contam uma visita em cada. Visita = de `inicio` (o tick da primeira entrada dentro) ate `fim` (o da primeira entrada fora
    depois dela); `permanencia` = fim - inicio, em minutos. `decisoes_dentro` = as entradas da visita depois da primeira, mais a de
    saida: todas foram tomadas com o pet na mancha. Contam as visitas com `inicio` na janela e ao menos uma decisao dentro. A que nao
    termina ate `tick_fim` sai `censurada`, com fim = tick_fim, e fica fora das inclinacoes (contada)."""
    ini, fim_j = _checar_janela(janela)
    ticks = [t for t, _, _ in trajetoria]
    if any(b <= a for a, b in zip(ticks, ticks[1:])):
        raise ValueError("trajetoria fora de ordem ou com tick repetido")
    if ticks and tick_fim < ticks[-1]:
        raise ValueError("tick_fim antes da ultima entrada da trajetoria")
    raio = raio_celulas * SUBUNIDADES_POR_CELULA
    custo = custo_viagem(arvores) if len(arvores) >= 2 else {a: None for a in arvores}
    out = []
    for a, (xa, ya) in sorted(arvores.items()):
        dentro = [math.isqrt((x - xa) ** 2 + (y - ya) ** 2) <= raio for _, x, y in trajetoria]
        i = 0
        while i < len(trajetoria):
            if not dentro[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(trajetoria) and dentro[j + 1]:
                j += 1
            saiu = j + 1 < len(trajetoria)
            inicio = trajetoria[i][0]
            fim = trajetoria[j + 1][0] if saiu else tick_fim
            n_dentro = (j - i) + (1 if saiu else 0)
            if ini <= inicio < fim_j and n_dentro >= 1:
                v = {"arvore": a, "inicio": inicio, "fim": fim, "permanencia": fim - inicio, "censurada": not saiu,
                     "decisoes_dentro": n_dentro, "custo_viagem": custo[a]}
                if quedas is not None:
                    v["taxa_recente"] = taxa_recente(quedas, inicio)
                out.append(v)
            i = j + 1
    out.sort(key=lambda v: (v["inicio"], v["arvore"]))
    return out


def inclinacao_permanencia(visitas: Sequence[Mapping], sobre: str) -> dict:
    """A inclinacao (minimos quadrados) da permanencia sobre `sobre`, nas visitas nao censuradas com valor:
    - "custo_viagem": a medida 1 (G-PERM, inclinacao do P1 - a do P0);
    - "taxa_recente": a medida 3 (G-OPORT; quem aprende o custo de oportunidade sai antes depois de dias ricos: inclinacao < 0).
    As visitas da unidade (as 12 celulas de um braco) entram juntas: e so concatenar as listas. `inclinacao` None, com o motivo, sem 2
    valores distintos de x. Nada some sem ser contado."""
    if sobre not in ("custo_viagem", "taxa_recente"):
        raise ValueError(f"inclinacao sobre {sobre!r}")
    usadas = [(v[sobre], v["permanencia"]) for v in visitas if not v["censurada"] and v.get(sobre) is not None]
    base = {"n": len(usadas), "censuradas": sum(1 for v in visitas if v["censurada"]),
            "sem_valor": sum(1 for v in visitas if not v["censurada"] and v.get(sobre) is None)}
    if len({x for x, _ in usadas}) < 2:
        return {**base, "inclinacao": None, "motivo": "menos de 2 valores distintos"}
    return {**base, "inclinacao": inclinacao_mmq([x for x, _ in usadas], [y for _, y in usadas]), "motivo": None}


def taxa_no_abandono(visitas: Sequence[Mapping], ganhos: Sequence[tuple[int, float]], horas_acordado: float,
                     minutos: int = 30) -> dict:
    """Medida 2 (A1.8, so descritiva): por visita nao censurada, a taxa de ganho nos `minutos` antes de sair, [fim - minutos, fim), por
    hora, dividida pela taxa media da vida (a soma dos ganhos por hora acordado). O motor fornece `ganhos` = (tick, fome ganha) por
    consumo, o aumento da fome pelo que o pet comeu, na escala 0-1, e as horas acordado da vida. Por vida (a media e a da vida); para
    a unidade, concatenar as `razoes`. `media_vida` None (e nenhuma razao) sem ganho na vida."""
    if horas_acordado <= 0.0:
        raise ValueError("horas acordado <= 0")
    total = sum(g for _, g in ganhos)
    media = total / horas_acordado if total > 0.0 else None
    validas = [v for v in visitas if not v["censurada"]]
    razoes = [] if media is None else [
        (sum(g for t, g in ganhos if v["fim"] - minutos <= t < v["fim"]) / (minutos / 60.0)) / media for v in validas]
    return {"n": len(razoes), "media_vida": media, "razoes": razoes,
            "razao_media": (sum(razoes) / len(razoes)) if razoes else None}


def permanencia_media(visitas: Sequence[Mapping]) -> float | None:
    """A permanencia media (minutos) das visitas nao censuradas; None sem visita."""
    p = [v["permanencia"] for v in visitas if not v["censurada"]]
    return (sum(p) / len(p)) if p else None


def contraste_distancia(p1_afastado: float | None, p1_padrao: float | None, p0_afastado: float | None,
                        p0_padrao: float | None) -> float | None:
    """G-DIST (A1.8), por unidade: [P1(afastado) - P1(padrao)] - [P0(afastado) - P0(padrao)] na permanencia media. None se falta um."""
    if None in (p1_afastado, p1_padrao, p0_afastado, p0_padrao):
        return None
    return (p1_afastado - p1_padrao) - (p0_afastado - p0_padrao)


# --- o corpo e os drives (docs/PLANO_ANALISE_V2_CORPO_DRIVES.md)


def tempo_livre_be(decisoes: Sequence[tuple[int, str, str]], janela: tuple[int, int] = JANELA_8_14) -> dict:
    """`BE`, a primaria (secao 5.1), e `OC` ao lado. O motor fornece (tick, regra do instinto, acao) por decisao. Nas decisoes de tempo
    livre da janela (regras `tempo_livre` e `bola_no_cenario`): BE = fracao em brincar ou explorar; OC = em ocioso ou chamar_atencao; e
    a fracao de cada acao (descritivo). None sem decisao de tempo livre."""
    ini, fim = _checar_janela(janela)
    sel = [a for t, r, a in decisoes if ini <= t < fim and r in REGRAS_TEMPO_LIVRE]
    if not sel:
        return {"n": 0, "be": None, "oc": None, "por_acao": {}}
    n = len(sel)
    cont: dict[str, int] = {}
    for a in sel:
        cont[a] = cont.get(a, 0) + 1
    return {"n": n, "be": (cont.get("brincar", 0) + cont.get("explorar", 0)) / n,
            "oc": (cont.get("ocioso", 0) + cont.get("chamar_atencao", 0)) / n,
            "por_acao": {a: c / n for a, c in sorted(cont.items())}}


def cuidado_preservado(decisoes: Sequence[tuple[int, bool, float, float]], janela: tuple[int, int] = JANELA_8_14) -> dict:
    """O cuidado preservado (secao 5.2). O motor fornece (tick, em privacao, saude, fome) por decisao: a privacao e a
    `Estado.em_privacao` (a definicao do N3), avaliada no motor. Privacao = a fracao das decisoes da janela em privacao
    (1 - fracao_fora_de_privacao); saude e fome medias (a fome, so descritiva). Falha alto sem decisao na janela."""
    ini, fim = _checar_janela(janela)
    sel = [(p, _escala01("saude", s), _escala01("fome", f)) for t, p, s, f in decisoes if ini <= t < fim]
    if not sel:
        raise ValueError("cuidado sem decisao na janela")
    n = len(sel)
    return {"n": n, "privacao": sum(1 for p, _, _ in sel if p) / n, "saude_media": sum(s for _, s, _ in sel) / n,
            "fome_media": sum(f for _, _, f in sel) / n}


def drives_novos(amostras: Sequence[tuple[int, bool, Mapping[str, float]]], janela: tuple[int, int] = JANELA_8_14,
                 limiar: float = 0.75) -> dict:
    """Os drives novos (secao 5.3; o tedio medio e a PR-5). O motor fornece, por decisao, (tick, acordado, {drive: falta}) com a falta
    lida pelo receptor, na escala 0-1 (tedio, solidao, estresse). Por drive: a media nas decisoes da janela e a fracao das decisoes
    acordado com a falta >= `limiar` (o ">= 0,75" do adendo 1). A fracao e None sem decisao acordado."""
    ini, fim = _checar_janela(janela)
    sel = [(a, d) for t, a, d in amostras if ini <= t < fim]
    if not sel:
        raise ValueError("drives sem decisao na janela")
    nomes = sorted({k for _, d in sel for k in d})
    if any(set(d) != set(nomes) for _, d in sel):
        raise ValueError("os drives mudam entre as amostras")
    acordado = [d for a, d in sel if a]
    out = {}
    for k in nomes:
        out[k] = {"media": sum(_escala01(k, d[k]) for _, d in sel) / len(sel),
                  "fracao_acima": (sum(1 for d in acordado if d[k] >= limiar) / len(acordado)) if acordado else None}
    return {"n": len(sel), "n_acordado": len(acordado), "drives": out}


def variedade_recente(atividades: Sequence[tuple[int, str]], ticks_decisao: Sequence[int], janela_tedio: int = 8,
                      janela: tuple[int, int] = JANELA_8_14) -> dict:
    """A variedade (adendo 1, A1.2, descritivo): em cada decisao de tempo livre da janela, quantas atividades distintas ha entre as
    ultimas `janela_tedio` antes dela; a media. O motor fornece `atividades` = (tick, atividade), as que o corpo guarda na janela do
    tedio (bola, brincar, explorar, dono_brinca), na ordem em que entram, e os ticks das decisoes de tempo livre. "Antes" e estrito:
    a atividade da propria decisao nao conta. Com menos de `janela_tedio` atividades ate ali, contam as que houver. None sem decisao."""
    if janela_tedio < 1:
        raise ValueError("janela do tedio < 1")
    ini, fim = _checar_janela(janela)
    if any(a not in ATIVIDADES_TEDIO for _, a in atividades):
        raise ValueError(f"atividade fora de {ATIVIDADES_TEDIO}")
    ts = [t for t, _ in atividades]
    if any(b < a for a, b in zip(ts, ts[1:])):
        raise ValueError("atividades fora de ordem")
    valores = []
    for td in ticks_decisao:
        if ini <= td < fim:
            antes = [a for t, a in atividades if t < td][-janela_tedio:]
            valores.append(len(set(antes)))
    return {"n": len(valores), "media": (sum(valores) / len(valores)) if valores else None}


def p_comer_so_fruta(decisoes: Sequence[tuple[int, Sequence[str], bool]], frutas: Sequence[str],
                     janela: tuple[int, int] = JANELA_8_14) -> dict:
    """A1.1: por fruta f, p(comer | so f no cenario), nas decisoes da janela com exatamente a fruta f no cenario. O motor fornece
    (tick, frutas no cenario, comeu) por decisao. `p` None sem decisao com so f."""
    ini, fim = _checar_janela(janela)
    out = {}
    for f in frutas:
        sel = [c for t, p, c in decisoes if ini <= t < fim and set(p) == {f}]
        out[f] = {"n": len(sel), "p": (sum(sel) / len(sel)) if sel else None}
    return out


def inclinacao_generalizacao(sem_tapa: Mapping[str, float | None], com_tapa: Mapping[str, float | None], punida: str) -> dict:
    """A inclinacao da generalizacao do tapa (adendo 1, A1.1, so descritiva), numa unidade. A queda de f = sem_tapa[f] - com_tapa[f]
    (o P1-c-frutas menos o P1-c-tapaX), em p(comer | so f) ou no peso aprendido da escolha de f no fim da vida. Inclinacao = (queda
    media nas nao punidas) / (queda na punida): 0 e especifico; 1 generaliza tudo. Sai `indefinida` quando a queda na punida nao e
    positiva ou falta: o tapa nao pegou nem na fruta punida, e a unidade e contada a parte. Fruta nao punida sem valor num dos lados
    fica fora da media, contada em `faltam`."""
    if punida not in sem_tapa or set(sem_tapa) != set(com_tapa):
        raise ValueError("as frutas dos dois lados diferem ou a punida nao esta nelas")
    queda = {f: (None if sem_tapa[f] is None or com_tapa[f] is None else sem_tapa[f] - com_tapa[f]) for f in sorted(sem_tapa)}
    outras = [q for f, q in queda.items() if f != punida and q is not None]
    faltam = sum(1 for f, q in queda.items() if f != punida and q is None)
    qp = queda[punida]
    if qp is None or qp <= 0.0 or not outras:
        motivo = ("falta a punida" if qp is None else "queda na punida nao positiva" if qp <= 0.0 else "nenhuma nao punida com valor")
        return {"queda": queda, "faltam": faltam, "indefinida": True, "motivo": motivo, "inclinacao": None}
    return {"queda": queda, "faltam": faltam, "indefinida": False, "motivo": None, "inclinacao": (sum(outras) / len(outras)) / qp}


# --- o banheiro (docs/PLANO_ANALISE_V2_BANHEIRO.md)


def alivios_por_dia(alivios: Sequence[tuple[int, bool, bool]], dias: int) -> list[dict]:
    """A fracao diaria no banheiro e os acidentes (secao 8). O motor fornece (tick, dentro do banheiro, urgente) por `aliviar`: urgente =
    pela regra urgente (a vontade acima de 0,90, alvo `aqui`), o acidente. Por dia 1..dias: n, quantos no banheiro, a fracao (None sem
    alivio), os urgentes e a fracao deles. Falha alto com alivio depois do ultimo dia."""
    if dias < 1:
        raise ValueError("dias < 1")
    out = [{"dia": d + 1, "n": 0, "no_banheiro": 0, "urgentes": 0} for d in range(dias)]
    for t, dentro, urgente in alivios:
        d = t // TICKS_POR_DIA
        if t < 0 or d >= dias:
            raise ValueError(f"alivio no tick {t} fora dos {dias} dias")
        out[d]["n"] += 1
        out[d]["no_banheiro"] += bool(dentro)
        out[d]["urgentes"] += bool(urgente)
    for o in out:
        o["fracao"] = (o["no_banheiro"] / o["n"]) if o["n"] else None
        o["fracao_urgentes"] = (o["urgentes"] / o["n"]) if o["n"] else None
    return out


def dia_do_criterio(fracoes: Sequence[float | None], limiar: float = 0.80, seguidos: int = 3) -> dict:
    """A primaria (secao 4, BN-4): o primeiro dia d (1, 2, ...) em que a fracao no banheiro e >= `limiar` em d e nos `seguidos` - 1 dias
    seguintes. Dia sem alivio (None) nao e acerto nem erro: quebra a sequencia. `fracoes` = a fracao de cada dia da vida (D dias,
    `alivios_por_dia`). Censurado quando nenhum d <= D - seguidos + 1 chega. O horizonte tau = D - seguidos + 2 (com 3 seguidos, o
    D - 1 do plano) e T* = min(T, tau): T, ou tau se censurado (a media restrita, RMST, e a media de T*)."""
    if seguidos < 1 or len(fracoes) < seguidos:
        raise ValueError("vida mais curta que a sequencia do criterio")
    D = len(fracoes)
    ok = [f is not None and f >= limiar for f in fracoes]
    tau = D - seguidos + 2
    for d in range(D - seguidos + 1):
        if all(ok[d:d + seguidos]):
            return {"dia": d + 1, "censurado": False, "tau": tau, "t_estrela": d + 1}
    return {"dia": None, "censurado": True, "tau": tau, "t_estrela": tau}


def alivios_ate_criterio(por_dia: Sequence[Mapping], dia: int | None) -> int:
    """Os alivios do nascimento ate o fim do dia do criterio (secao 8); censurado (`dia` None), o total da vida. `por_dia` e o
    `alivios_por_dia`."""
    if dia is not None and not 1 <= dia <= len(por_dia):
        raise ValueError(f"dia do criterio fora da vida: {dia}")
    return sum(o["n"] for o in (por_dia if dia is None else por_dia[:dia]))


def curva_sobrevivencia(criterios: Sequence[Mapping]) -> dict:
    """O descritivo da secao 4, num braco: a curva de Kaplan-Meier dos `dia_do_criterio` das vidas (o mesmo horizonte). Com a censura so
    administrativa, no fim, igual em todas, a curva e a fracao que ainda nao chegou: S(t) = P(T > t), t = 0..tau. A mediana e o menor
    t com S(t) <= 0,5 (None se mais da metade e censurada); a RMST = soma de S(t) para t < tau = a media de T*."""
    if not criterios:
        raise ValueError("curva sem vidas")
    taus = {c["tau"] for c in criterios}
    if len(taus) != 1:
        raise ValueError("horizontes diferentes")
    tau = taus.pop()
    n = len(criterios)
    s = [sum(1 for c in criterios if c["censurado"] or c["dia"] > t) / n for t in range(tau + 1)]
    mediana = next((t for t, v in enumerate(s) if v <= 0.5), None)
    return {"n": n, "tau": tau, "s": s, "mediana": mediana, "fracao_censurada": sum(1 for c in criterios if c["censurado"]) / n,
            "rmst": sum(s[:tau])}


# ------------------------------------------------------------ V2, adendo 2 do plano do corpo: a dominancia de um drive no sinal
# (PLANO_ANALISE_V2_CORPO_DRIVES, A2.2 e A2.3; decisao D-4). So descritiva: fora do Holm e sem gate; o "domina" e regra de leitura.

LIMIAR_LIDERA = 0.80             # A2.3: o drive lidera a decisao com p_d >= 0,80 (os outros juntos dao no maximo um quarto do que ele da)
LIMIAR_DOMINA = 0.50             # A2.3: domina com o limite inferior do IC95 de f_d acima de 0,50


def contribuicao_drives(faltas_antes: Mapping[str, int], faltas_depois: Mapping[str, int], pesos: Mapping[str, int] | None = None,
                        escala: int = 1024) -> dict[str, int]:
    """A2.2: c_d = w_d * (falta_d,antes^2 - falta_d,depois^2) por drive, em inteiros. As faltas sao inteiros na escala S (a mesma conta
    do sinal e dos canais: falta = S - arred(h * S)); `pesos` e o w_d na escala S (S = peso 1, o de hoje; sem `pesos`, todos 1), e
    c_d = div_arred(w_d * delta_d, S). Os mesmos drives nos dois lados, ou falha alto."""
    if set(faltas_antes) != set(faltas_depois):
        raise ValueError(f"drives diferentes antes e depois: {sorted(faltas_antes)} x {sorted(faltas_depois)}")
    pesos = pesos or {}
    out = {}
    for d, a in faltas_antes.items():
        b = faltas_depois[d]
        if not (type(a) is int and type(b) is int) or not (0 <= a <= escala and 0 <= b <= escala):
            raise ValueError(f"falta de {d!r} fora de inteiros em [0, {escala}]: {a!r}, {b!r}")
        w = pesos.get(d, escala)
        if type(w) is not int or w < 0:
            raise ValueError(f"peso de {d!r} precisa ser inteiro >= 0: {w!r}")
        delta = a * a - b * b
        out[d] = delta if w == escala else _div_arred(w * delta, escala)
    return out


def _div_arred(n: int, d: int) -> int:
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def parcelas_drives(c: Mapping[str, int]) -> dict[str, float] | None:
    """A2.2: p_d = |c_d| / soma_e |c_e| (entre 0 e 1, soma 1). None quando nenhum drive mexeu (soma dos |c| = 0)."""
    total = sum(abs(v) for v in c.values())
    if total == 0:
        return None
    return {d: abs(v) / total for d, v in c.items()}


def dominancia_decisoes(decisoes: Sequence[tuple[int, str, Mapping[str, int]]], janela: tuple[int, int] = JANELA_8_14,
                        limiar: float = LIMIAR_LIDERA, regras_livres: Sequence[str] = REGRAS_TEMPO_LIVRE) -> dict:
    """A2.2 e A2.3, numa vida: `decisoes` = (tick, regra do instinto, {drive: c_d}) por decisao, as contribuicoes com sinal. Contam as
    decisoes da janela COM SINAL (D_antes != D_depois: soma dos c_d != 0), separadas em tempo livre (regras tempo_livre e
    bola_no_cenario) e o resto. Por tipo: quantas, quantas cada drive lidera (p_d >= limiar), a fracao f_d = lideradas / n (None sem
    decisao), as sem lider, a parcela agregada soma|c_d| / soma soma|c| e a contribuicao com sinal soma c_d. As contagens vao juntas
    para a unidade somar as celulas (f_d da unidade = soma das lideradas / soma de n)."""
    if limiar <= 0.5:
        raise ValueError("o limiar de liderar precisa passar de 0,5 (um lider por decisao)")
    ini, fim = _checar_janela(janela)
    drives = sorted({d for _, _, c in decisoes for d in c})
    tipos = {"tempo_livre": [], "resto": []}
    for t, regra, c in decisoes:
        if ini <= t < fim and sum(c.values()) != 0:
            tipos["tempo_livre" if regra in regras_livres else "resto"].append(c)
    out = {}
    for tipo, cs in tipos.items():
        lideradas = {d: 0 for d in drives}
        abs_d = {d: 0 for d in drives}
        sinal_d = {d: 0 for d in drives}
        sem_lider = 0
        for c in cs:
            p = parcelas_drives(c)
            lider = [d for d, v in p.items() if v >= limiar]
            if lider:
                lideradas[lider[0]] += 1           # com limiar > 0,5 so um drive pode liderar
            else:
                sem_lider += 1
            for d, v in c.items():
                abs_d[d] += abs(v)
                sinal_d[d] += v
        total = sum(abs_d.values())
        n = len(cs)
        out[tipo] = {"n": n, "lideradas": lideradas, "sem_lider": sem_lider,
                     "f": {d: (lideradas[d] / n) if n else None for d in drives},
                     "parcela": {d: (abs_d[d] / total) if total else None for d in drives},
                     "soma_abs": abs_d, "contribuicao": sinal_d}
    return out


def leitura_dominancia(f_por_unidade: Mapping[str, Sequence[float | None]], reamostragens: int = 10_000, semente: int = 4242,
                       nivel: float = 0.95, limiar: float = LIMIAR_DOMINA) -> dict:
    """A2.3, a regra de leitura (fora do Holm): por drive, o IC (bootstrap sobre as unidades) de f_d, e "domina" se o limite inferior
    passa de `limiar`. Unidade sem decisao de tempo livre com sinal (f None) fica fora, contada em `sem_valor`. Com menos de 2 unidades
    com valor, sem IC e `domina` None, com o motivo. Nada some sem ser contado."""
    out = {}
    for d, fs in sorted(f_por_unidade.items()):
        vals = [float(f) for f in fs if f is not None]
        base = {"n": len(vals), "sem_valor": sum(1 for f in fs if f is None)}
        if len(vals) < 2:
            out[d] = {**base, "media": (vals[0] if vals else None), "ic": None, "domina": None, "motivo": "menos de 2 unidades com valor"}
            continue
        ic = bootstrap_ic(vals, reamostragens, semente, nivel)
        out[d] = {**base, "media": ic["media"], "ic": ic, "domina": ic["ic_inferior"] > limiar, "motivo": None}
    return out


# ================================================================== dois pets (PLANO_ANALISE_V2_DOIS_PETS, secoes 4 e 9)
def vez_no_grupo(ordens: Sequence[Mapping], ident: str, janela: tuple[int, int] | None = None) -> dict:
    """A sorte da ordem no tick (R-5, so descritiva): das vezes sorteadas do grupo (`Grupo.ordens`: {tick, decidem, ordem}, um item por
    tick com dois pets ou mais decidindo), em quantas o pet `ident` decidiu junto e em quantas foi o primeiro. `janela` = [inicio, fim)
    em ticks do mundo (None: todas). Fracao None sem tick junto (nao e zero)."""
    if janela is not None:
        _checar_janela(janela)
    sel = [o for o in ordens if ident in o["decidem"] and (janela is None or janela[0] <= o["tick"] < janela[1])]
    for o in sel:
        if sorted(o["ordem"]) != sorted(o["decidem"]):
            raise ValueError(f"ordem que nao e uma permutacao de quem decide: {o}")
    primeiro = sum(1 for o in sel if o["ordem"][0] == ident)
    return {"juntos": len(sel), "primeiro": primeiro, "fracao_primeiro": primeiro / len(sel) if sel else None}


# ================================================================== metabolismo (PLANO_ANALISE_V2_CORPO_DRIVES, adendo 3, A3.3)
def metabolismo_da_vida(sonda: Sequence[tuple[int, bool, int, int]], falta_limiar: int, ticks_por_dia: int) -> dict:
    """A medida descritiva do metabolismo numa vida, so relato. `sonda` = (tick, dormindo, combustivel, reserva) de cada tick, em ordem e
    sem buraco (tick 0, 1, ...), com o combustivel e a reserva no fim do tick; a vida tem dias inteiros. A falta e o combustivel abaixo de
    `falta_limiar` (estritamente, como o gatilho `abaixo` do grafo). Sai:
      - `acordado`, `acordado_com_falta` e a `fracao` (None sem tick acordado);
      - `disparos`: as vezes que a falta comecou (o tick com falta cujo anterior nao tinha; o primeiro tick conta se ja tem falta);
      - `por_dia`: o combustivel e a reserva no ultimo tick de cada dia.
    Tick fora de ordem ou vida sem dias inteiros falha alto."""
    if ticks_por_dia <= 0 or not sonda or len(sonda) % ticks_por_dia:
        raise ValueError(f"metabolismo: a vida tem de ter dias inteiros ({len(sonda)} ticks, {ticks_por_dia} por dia)")
    acordado = com_falta = disparos = 0
    antes = False
    por_dia = []
    for i, (t, dormindo, comb, reserva) in enumerate(sonda):
        if t != i:
            raise ValueError(f"metabolismo: tick {t} na posicao {i}")
        falta = comb < falta_limiar
        if not dormindo:
            acordado += 1
            com_falta += falta
        disparos += falta and not antes
        antes = falta
        if (t + 1) % ticks_por_dia == 0:
            por_dia.append({"dia": (t + 1) // ticks_por_dia, "combustivel": comb, "reserva": reserva})
    return {"acordado": acordado, "acordado_com_falta": com_falta, "fracao": com_falta / acordado if acordado else None,
            "disparos": disparos, "ticks_com_falta": sum(1 for _, _, c, _ in sonda if c < falta_limiar), "por_dia": por_dia}


def tempo_comer_brincar(decisoes: Sequence[tuple[int, str]]) -> dict:
    """O tempo entre comer e brincar (A3.3, no P1-c), so relato: para cada decisao `brincar` depois de algum `comer`, os ticks desde o
    ultimo `comer`. Sai quantas, a media e a mediana (None sem nenhuma). `decisoes` = (tick, acao) em ordem; fora de ordem falha alto."""
    ultimo = None
    gaps = []
    anterior = None
    for t, a in decisoes:
        if anterior is not None and t < anterior:
            raise ValueError(f"tempo_comer_brincar: decisoes fora de ordem ({t} depois de {anterior})")
        anterior = t
        if a == "comer":
            ultimo = t
        elif a == "brincar" and ultimo is not None:
            gaps.append(t - ultimo)
    if not gaps:
        return {"n": 0, "media": None, "mediana": None}
    ordenados = sorted(gaps)
    meio = len(ordenados) // 2
    mediana = ordenados[meio] if len(ordenados) % 2 else (ordenados[meio - 1] + ordenados[meio]) / 2
    return {"n": len(gaps), "media": sum(gaps) / len(gaps), "mediana": mediana}


# ================================================================== dois pets: a taxa agregada sobre as unidades (PLANO_ANALISE_V2_DOIS_PETS)
MODOS_TAXA_AGREGADA = ("razao_das_somas", "media_das_unidades")


def taxa_agregada(contagens: Sequence[tuple[int, int]], modo: str) -> dict:
    """A taxa de fruta ruim de um grupo de unidades numa janela, com `contagens` = (n consumos, quantos ruins) por unidade (uma unidade
    sem consumo na janela entra com n = 0: o pet nao comeu fruta ali, nao e taxa zero).
      - `razao_das_somas`: soma dos ruins / soma dos n (cada consumo pesa igual; a unidade sem consumo nao pesa);
      - `media_das_unidades`: a media das taxas das unidades com n > 0 (cada unidade pesa igual).
    Sai a taxa (None sem nenhum consumo), o n somado e quantas unidades tem valor."""
    if modo not in MODOS_TAXA_AGREGADA:
        raise ValueError(f"modo da taxa agregada {modo!r}: so {MODOS_TAXA_AGREGADA}")
    for n, r in contagens:
        if type(n) is not int or type(r) is not int or n < 0 or not 0 <= r <= n:
            raise ValueError(f"contagem invalida (n, ruins) = ({n!r}, {r!r})")
    com = [(n, r) for n, r in contagens if n]
    n_total = sum(n for n, _ in com)
    if not com:
        taxa = None
    elif modo == "razao_das_somas":
        taxa = sum(r for _, r in com) / n_total
    else:
        taxa = sum(r / n for n, r in com) / len(com)
    return {"taxa": taxa, "n": n_total, "unidades": len(contagens), "unidades_com_valor": len(com), "modo": modo}


def bootstrap_taxa_agregada(contagens: Sequence[tuple[int, int]], modo: str, reamostragens: int, semente: int,
                            nivel: float = 0.95) -> dict:
    """O IC percentil da `taxa_agregada` reamostrando as UNIDADES com reposicao (a unidade inteira, com o n e os ruins dela; secao 7 do
    plano dos dois pets: bootstrap sobre as unidades). Uma reamostra sem nenhum consumo nao tem taxa: com alguma assim, o IC fica None,
    com o motivo e a contagem (nao se descarta reamostra em silencio)."""
    ponto = taxa_agregada(contagens, modo)
    out = {**ponto, "ic": None, "nivel": nivel, "reamostragens": reamostragens, "reamostras_sem_valor": 0, "motivo": None}
    k = len(contagens)
    if k < 2 or ponto["taxa"] is None:
        out["motivo"] = "menos de 2 unidades ou nenhum consumo"
        return out
    rng = random.Random(derivar_semente("bootstrap-taxa-agregada", semente))
    taxas, sem = [], 0
    for _ in range(reamostragens):
        t = taxa_agregada([contagens[rng.randrange(k)] for _ in range(k)], modo)["taxa"]
        if t is None:
            sem += 1
        else:
            taxas.append(t)
    out["reamostras_sem_valor"] = sem
    if sem:
        out["motivo"] = f"{sem} reamostras sem nenhum consumo na janela"
        return out
    lo, hi = _percentis(sorted(taxas), nivel)
    out["ic"] = {"ic_inferior": lo, "ic_superior": hi, "nivel": nivel}
    return out


def efeitos_do_tapa(tapas: Sequence[int], carinhos: Sequence[tuple[int, float, int]], decisoes: Sequence[tuple[int, str]],
                    estresse: Sequence[tuple[int, float]], janela: tuple[int, int] = JANELA_8_14, horas_depois: int = 6 * 60,
                    ticks_por_dia: int = 1440, limiar: float = 0.75) -> dict:
    """Os efeitos do tapa (PLANO_ANALISE_V2_CORPO_DRIVES, secao 5.4), so descritivos, nas decisoes e carinhos da janela. O motor fornece:
    `tapas` (os ticks dos tapas da vida), `carinhos` = (tick, reducao da solidao na escala 0-1, sinal pelo corpo) por carinho,
    `decisoes` = (tick, acao) e `estresse` = (tick, falta do estresse na escala 0-1) por decisao. "Depois de um tapa" = algum tapa em
    [t - horas_depois, t), estritamente antes (o tapa e o carinho do mesmo passo nao se ordenam); o resto e o "sem tapa" (a comparacao
    com as horas anteriores sem tapa). Sai: o medo da mao (a reducao media da solidao por carinho, depois e sem), a fracao de
    chamar_atencao nas decisoes depois de um tapa e nas outras, o sinal medio do carinho depois e sem (o R-3), o estresse da ultima
    decisao de cada dia e a fracao das decisoes com o estresse >= limiar. Medias de grupo vazio sao None. O vinculo nao esta disponivel
    (S-4). Fora de ordem falha alto."""
    ini, fim = _checar_janela(janela)
    ts = sorted(tapas)
    for seq, nome in ((carinhos, "carinhos"), (decisoes, "decisoes"), (estresse, "estresse")):
        ticks = [x[0] for x in seq]
        if ticks != sorted(ticks):
            raise ValueError(f"efeitos_do_tapa: {nome} fora de ordem")

    def depois(t: int) -> bool:
        i = bisect_left(ts, t)                    # o primeiro tapa >= t; o anterior a ele e o ultimo estritamente antes
        return i > 0 and t - ts[i - 1] <= horas_depois

    def media(xs):
        return sum(xs) / len(xs) if xs else None
    car = [(depois(t), r, s) for t, r, s in carinhos if ini <= t < fim]
    dec = [(depois(t), a) for t, a in decisoes if ini <= t < fim]
    chamar = {g: [a == "chamar_atencao" for d, a in dec if d is g] for g in (True, False)}
    est = [(t, e) for t, e in estresse if ini <= t < fim]
    fim_dia: dict[int, float] = {}
    for t, e in est:
        fim_dia[t // ticks_por_dia + 1] = e     # o ultimo da janela em cada dia
    return {"tapas": sum(1 for t in ts if ini <= t < fim), "tapas_vida": len(ts), "horas_depois": horas_depois,
            "medo_da_mao": {"depois_tapa": {"n": sum(1 for d, _, _ in car if d), "reducao_solidao": media([r for d, r, _ in car if d])},
                            "sem_tapa": {"n": sum(1 for d, _, _ in car if not d), "reducao_solidao": media([r for d, r, _ in car if not d])}},
            "chamar_atencao": {"depois_tapa": {"n": len(chamar[True]), "fracao": media(chamar[True])},
                               "sem_tapa": {"n": len(chamar[False]), "fracao": media(chamar[False])}},
            "carinho_sinal": {"depois_tapa": media([s for d, _, s in car if d]), "sem_tapa": media([s for d, _, s in car if not d])},
            "estresse_fim_do_dia": [{"dia": d, "estresse": e} for d, e in sorted(fim_dia.items())],
            "estresse_acima": {"n": len(est), "fracao": media([e >= limiar for _, e in est])},
            "vinculo": "nao disponivel (a base nova do vinculo, S-4)"}


# --- o mundo com o alvo aprendido (docs/PLANO_ANALISE_V2_MUNDO_ALVO.md, secao 5)


def uso_do_alvo(decisoes: Sequence[tuple[int, str, str]], janela: tuple[int, int] = JANELA_8_14) -> dict:
    """G-USO (secao 5): a fracao das decisoes com alvo, na janela, em que o alvo escolhido difere do que a tabela do prior daria com o
    mesmo u. Entrada: (tick, a classe escolhida, a classe do prior com o mesmo u), uma por decisao com alvo (quem chama faz o sorteio do
    prior: todas as classes em w0_alvo, mais 1 na do padrao). Sem decisao na janela, a fracao e None. Fora de ordem falha alto."""
    ini, fim = _checar_janela(janela)
    ticks = [d[0] for d in decisoes]
    if ticks != sorted(ticks):
        raise ValueError("uso_do_alvo: decisoes fora de ordem")
    dentro = [(e, p) for t, e, p in decisoes if ini <= t < fim]
    difere = sum(1 for e, p in dentro if e != p)
    return {"decisoes": len(dentro), "difere": difere, "fracao": difere / len(dentro) if dentro else None}


def classes_por_dia(decisoes: Sequence[tuple[int, str, str]], ticks_por_dia: int = TICKS_POR_DIA) -> dict:
    """Descritivo da secao 5: por acao e por dia (1 = o do nascimento), a contagem e a fracao de cada classe escolhida. Entrada: (tick,
    a acao, a classe), uma por decisao com alvo."""
    cont: dict = {}
    for t, acao, classe in decisoes:
        dia = t // ticks_por_dia + 1
        c = cont.setdefault(acao, {}).setdefault(dia, {})
        c[classe] = c.get(classe, 0) + 1
    return {a: {str(d): {"n": sum(cs.values()), "fracao": {c: v / sum(cs.values()) for c, v in sorted(cs.items())}}
                for d, cs in sorted(por.items())} for a, por in sorted(cont.items())}


# --- o pet que pensa, J5 (docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secao 4)
# Funcoes puras sobre o que a bancada tira da percepcao do pet e do registro do motor, por decisao. Nenhuma le os modelos do mundo.
#   fome      o receptor da fome na decisao (inteiro em [0, S]); a oportunidade pede fome <= fome_max (S/2)
#   maduros   os tipos das comidas maduras a vista ("racao", "a", "b", "c"); a podre nao entra
#   troncos   {id: o tipo que a arvore da agora} dos troncos que o pet ja viu
#   alvo      None (acao sem alvo) ou {"tipo", "fruta" (o tipo da comida alvo, ou None), "arvore" (o id da arvore alvo, ou None)}


def oportunidade_revalorizacao(fome: int, maduros: Sequence[str], troncos: Mapping[str, str], alvo: Mapping | None, x: str,
                               fome_max: int) -> tuple[bool, bool]:
    """O T1 (secao 4): (e oportunidade, o pet escolheu x). Oportunidade: fome <= fome_max, um alvo de x disponivel (a x a vista, ou uma
    arvore do tipo x entre os troncos ja vistos) e ao menos um alvo que nao e de x (outra comida madura a vista, ou um tronco ja visto de
    outro tipo). Escolher x: a acao tem alvo e ele e uma comida x ou uma arvore que da x agora. Fora da oportunidade, nao escolheu."""
    disponivel = x in maduros or x in troncos.values()
    alternativa = any(t != x for t in maduros) or any(t != x for t in troncos.values())
    if not (fome <= fome_max and disponivel and alternativa):
        return False, False
    if alvo is None:
        return True, False
    return True, alvo.get("fruta") == x or (alvo.get("arvore") is not None and troncos.get(alvo["arvore"]) == x)


def busca_transicao(fome: int, maduros: Sequence[str], alvo: Mapping | None, x: str, velhas: set, novas: set,
                    fome_max: int) -> tuple[bool, bool]:
    """O T2 (secao 4): (e busca, vai as novas). Busca: fome <= fome_max, sem a x a vista, e o alvo e uma arvore do tipo x de antes da troca
    (as velhas) ou de depois (as novas: as da y no layout). Antes da mudanca a definicao e a mesma, com as novas ainda dando y."""
    if velhas & novas:
        raise ValueError(f"velhas e novas se cruzam: {sorted(velhas & novas)}")
    arv = None if alvo is None else alvo.get("arvore")
    if fome > fome_max or x in maduros or arv is None or arv not in velhas | novas:
        return False, False
    return True, arv in novas


def exposto_transicao(px: int, py: int, vistos: Sequence[tuple], novas: Sequence[tuple[int, int]], x: str, raio: int) -> bool:
    """A exposicao do T2 (secao 4): uma x madura nos `vistos` (id, tipo, dx, dy, d) do pet em (px, py) a ate `raio` (subunidades) de uma
    arvore nova (as posicoes em subunidades)."""
    for _i, tipo, dx, dy, *_ in vistos:
        if tipo != x:
            continue
        cx, cy = px + dx, py + dy
        if any((cx - ax) ** 2 + (cy - ay) ** 2 <= raio * raio for ax, ay in novas):
            return True
    return False


def mudanca_de_escolha(linhas: Sequence[Mapping], n: int, tick_mudanca: int | None) -> dict:
    """A primaria da secao 4 (PP-7, a mudanca dentro da unidade), por unidade e braco. `linhas`, uma por decisao, em ordem: {"tick",
    "depois" (veio depois da mudanca), "conta" (e oportunidade, ou busca ja contavel), "sucesso" (escolheu x, ou foi as novas),
    "reexperiencia" (consumiu x no mapa)}.
      - antes: as `n` ultimas que contam antes da mudanca;
      - depois: as `n` primeiras que contam depois dela, ate o primeiro consumo de x no mapa (o corte da reexperiencia: a decisao que leva
        a ele conta, as seguintes nao);
      - f = a fracao de sucesso; com menos de `n`, as que houver; sem nenhuma antes ou depois, a unidade sai "sem oportunidade" (R-2).
    Sai a queda (f_antes - f_depois, o q do T1) e a subida (f_depois - f_antes, o m do T2), o nivel (f_depois), as oportunidades depois ate
    o corte e a latencia (ticks da mudanca ate a primeira oportunidade depois)."""
    if n < 1:
        raise ValueError(f"n {n!r}: pelo menos 1")
    depois_visto = False
    ultimo = None
    for ln in linhas:
        if ultimo is not None and ln["tick"] < ultimo:
            raise ValueError("as linhas nao estao em ordem de tick")
        ultimo = ln["tick"]
        if ln["depois"]:
            depois_visto = True
        elif depois_visto:
            raise ValueError("uma linha de antes depois de uma de depois")
    antes = [ln for ln in linhas if not ln["depois"] and ln["conta"]][-n:]
    depois_ate_corte, corte = [], None
    for ln in linhas:
        if not ln["depois"]:
            continue
        if ln["conta"]:
            depois_ate_corte.append(ln)
        if ln["reexperiencia"]:
            corte = ln["tick"]
            break
    depois = depois_ate_corte[:n]
    frac = lambda ls: None if not ls else sum(1 for ln in ls if ln["sucesso"]) / len(ls)  # noqa: E731
    f_antes, f_depois = frac(antes), frac(depois)
    sem = f_antes is None or f_depois is None
    return {"n_antes": len(antes), "n_depois": len(depois), "oportunidades_depois_ate_corte": len(depois_ate_corte),
            "f_antes": f_antes, "f_depois": f_depois, "nivel": f_depois,
            "queda": None if sem else f_antes - f_depois, "subida": None if sem else f_depois - f_antes,
            "sem_oportunidade": sem, "corte_reexperiencia": corte,
            "latencia": None if not depois_ate_corte or tick_mudanca is None else depois_ate_corte[0]["tick"] - tick_mudanca}
