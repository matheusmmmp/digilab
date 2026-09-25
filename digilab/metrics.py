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
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .arena import ResultadoPartida
from .config import CONFIG_METRICAS, ConfigMetricas
from .events import AcaoPet
from .policy import Observacao, Politica
from .protocol import derivar_semente

ACOES = tuple(AcaoPet)


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
