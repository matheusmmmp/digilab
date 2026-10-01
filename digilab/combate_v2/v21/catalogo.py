"""Catalogo de pets V2.1: especie + caminho de arquetipos -> stats -> perfil de combate.

stat = especie + temperamento + carater + arquetipo_crianca + arquetipo_adolescente
       + arquetipo_adulto; depois estagio e condicao.

Todo modificador soma zero, entao a soma dos stats fica no orcamento da especie.
Nos extremos, em vez de cortar (clamp, que quebraria a soma zero), a
RENORMALIZACAO prende o stat no limite e devolve a diferenca, em partes iguais,
aos stats ainda livres, ate nenhum sair da faixa. O total volta ao orcamento.

Transicoes (arvore_evolucao.json), cada uma com uma moeda:
  bebe -> crianca        cuidado (fracao de janelas atendidas) >= limiar: sereno; senao arisco
  crianca -> adolescente eixo de carater dominante -> linha
  adolescente -> adulto  sinal do eixo complementar da linha (exige sparring minimo)

O carater (desvio da politica aprendida em relacao ao instinto em
contextos-sonda) vem da TAREFA_PERSONALIDADE_OBEDIENCIA, que ainda nao existe:
aqui ele e ENTRADA (dict eixo -> [-1, 1]). Ver docs/REGISTRO_DESVIOS.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

from ...config import (CONFIG_CATALOGO, CONFIG_COMBATE_V21, CONFIG_SOMBRIO, CONFIG_TREINO, ESTAGIOS_V21, STATS_V21, ConfigCatalogo,
                       ConfigCombateV21, ConfigEscala)

LINHAS = ("brigao", "guardiao", "cacador", "colosso")
RAMOS_CRIANCA = ("sereno", "arisco")
FORMAS_ADULTAS = ("duelista", "furioso", "espelho", "muralha", "sentinela", "emboscador", "vigia", "tita")
# formas sombrias (TAREFA_TREINO_SOMBRIO, arvore_evolucao.json > ramos_sombrios): uma por linha,
# substitui as 2 formas adultas quando a sobrecarga passa do limiar na evolucao
SOMBRIA_DA_LINHA = {l: CONFIG_SOMBRIO.formas[l]["nome"] for l in LINHAS}
FORMAS_SOMBRIAS = tuple(SOMBRIA_DA_LINHA[l] for l in LINHAS)
LINHA_DA_FORMA = {f: l for l in LINHAS for f in CONFIG_CATALOGO.arquetipos_adulto[l]["formas"]} | \
    {f: l for l, f in SOMBRIA_DA_LINHA.items()}


class CatalogoInvalido(ValueError):
    pass


def _eixos(vetor: dict | None, nomes, rotulo: str) -> dict:
    vetor = dict(vetor or {})
    extras = set(vetor) - set(nomes)
    if extras:
        raise CatalogoInvalido(f"{rotulo}: eixos desconhecidos {sorted(extras)}")
    for k, v in vetor.items():
        if not -1.0 <= v <= 1.0:
            raise CatalogoInvalido(f"{rotulo}.{k} fora de [-1, 1]: {v}")
    return {k: float(vetor.get(k, 0.0)) for k in nomes}


@dataclass(frozen=True)
class Forma:
    """Especie + caminho. Campos do caminho ficam None ate o estagio chegar la."""

    especie: str
    estagio: str
    ramo: str | None = None          # crianca: sereno / arisco
    linha: str | None = None         # adolescente: brigao / guardiao / cacador / colosso
    adulta: str | None = None        # adulto: uma das 8 formas

    def __post_init__(self) -> None:
        cat = CONFIG_CATALOGO
        if self.especie not in cat.especies:
            raise CatalogoInvalido(f"especie desconhecida: {self.especie!r}")
        if self.estagio not in ESTAGIOS_V21:
            raise CatalogoInvalido(f"estagio desconhecido: {self.estagio!r}")
        nivel = ESTAGIOS_V21.index(self.estagio)
        esperado = (nivel >= 1, nivel >= 2, nivel >= 3)
        tem = (self.ramo is not None, self.linha is not None, self.adulta is not None)
        if tem != esperado:
            raise CatalogoInvalido(f"caminho incompleto ou sobrando para {self.estagio}: {self}")
        if self.ramo is not None and self.ramo not in RAMOS_CRIANCA:
            raise CatalogoInvalido(f"ramo desconhecido: {self.ramo!r}")
        if self.linha is not None and self.linha not in LINHAS:
            raise CatalogoInvalido(f"linha desconhecida: {self.linha!r}")
        if self.adulta is not None and LINHA_DA_FORMA.get(self.adulta) != self.linha:
            raise CatalogoInvalido(f"forma adulta {self.adulta!r} nao pertence a linha {self.linha!r}")

    @property
    def tecnica(self) -> str | None:
        return CONFIG_CATALOGO.arquetipos_adolescente[self.linha]["tecnica"] if self.linha else None

    @property
    def passiva(self) -> str | None:
        return self.adulta

    @property
    def sombria(self) -> bool:
        return self.adulta in FORMAS_SOMBRIAS

    @property
    def rotulo(self) -> str:
        return "/".join(x for x in (self.especie, self.ramo, self.linha, self.adulta) if x)


def renormalizar(brutos: dict, total: float, minimo: float, maximo: float) -> dict:
    """Prende no limite quem saiu da faixa e devolve a diferenca aos livres.

    Deterministico; termina porque cada rodada prende pelo menos um stat.
    """
    if not len(brutos) * minimo <= total <= len(brutos) * maximo:
        raise CatalogoInvalido(f"orcamento {total} impossivel na faixa [{minimo}, {maximo}]")
    valores = dict(brutos)
    presos: dict = {}
    while True:
        livres = [k for k in STATS_V21 if k in valores and k not in presos]
        fora = [k for k in livres if valores[k] < minimo or valores[k] > maximo]
        if not fora:
            return {k: (presos[k] if k in presos else valores[k]) for k in STATS_V21 if k in brutos}
        for k in fora:
            presos[k] = minimo if valores[k] < minimo else maximo
        livres = [k for k in livres if k not in presos]
        if not livres:
            raise CatalogoInvalido("renormalizacao sem stats livres")
        sobra = total - sum(presos.values()) - sum(valores[k] for k in livres)
        for k in livres:
            valores[k] += sobra / len(livres)


def stats(forma: Forma, temperamento: dict | None = None, carater: dict | None = None,
          cat: ConfigCatalogo | None = None) -> dict:
    cat = cat or CONFIG_CATALOGO
    temp = _eixos(temperamento, cat.temperamento, "temperamento")
    car = _eixos(carater, cat.carater, "carater")
    brutos = {k: float(cat.especies[forma.especie][k]) for k in STATS_V21}

    def somar(mods: dict, peso: float = 1.0) -> None:
        for k, v in mods.items():
            brutos[k] += peso * v

    for eixo, v in temp.items():
        somar(cat.temperamento[eixo], v)
    for eixo, v in car.items():
        somar(cat.carater[eixo], v)
    if forma.ramo:
        somar(cat.arquetipos_crianca[forma.ramo])
    if forma.linha:
        somar(cat.arquetipos_adolescente[forma.linha]["stats"])
    if forma.adulta in FORMAS_SOMBRIAS:
        somar(CONFIG_SOMBRIO.formas[forma.linha]["stats"])
    elif forma.adulta:
        somar(cat.arquetipos_adulto[forma.linha]["formas"][forma.adulta]["stats"])
    total = float(sum(cat.especies[forma.especie].values()))
    return renormalizar(brutos, total, cat.stat_min, cat.stat_max)


def com_treino(base: dict, treino: dict, normalizar: bool, total: float | None = None,
               cat: ConfigCatalogo | None = None) -> dict:
    """Stats da forma + pontos treinados (treino_stats.py).

    normalizar=True (arena e pesquisa, barreira 1 da TAREFA_TREINO_SOMBRIO): o total volta ao
    orcamento `total` mantendo as PROPORCOES treinadas (escala e depois renormalizacao na faixa).
    normalizar=False (campanha): ganho absoluto, sem teto de stat.
    """
    cat = cat or CONFIG_CATALOGO
    extras = set(treino) - set(STATS_V21)
    if extras:
        raise CatalogoInvalido(f"treino com stats desconhecidos: {sorted(extras)}")
    if any(v < 0 for v in treino.values()):
        raise CatalogoInvalido("pontos de treino negativos")
    # cada ponto treinado vale peso_ponto_combate pontos de stat (decisao do Matheus: treino mais forte)
    brutos = {k: base[k] + CONFIG_TREINO.peso_ponto_combate * treino.get(k, 0.0) for k in STATS_V21}
    if not normalizar:
        return brutos
    total = float(sum(base.values())) if total is None else total
    soma = sum(brutos.values())
    return renormalizar({k: v * total / soma for k, v in brutos.items()}, total, cat.stat_min, cat.stat_max)


@dataclass(frozen=True)
class Perfil:
    """Tudo que o combate V2.1 precisa de um lutador; fixo na partida."""

    rotulo: str
    estagio: str
    tecnica: str | None
    passiva: str | None
    hp_max: float
    guts_inicial: float
    guts_max: float
    regen: float
    mult_perto: float
    mult_disparo: float
    mult_guarda: float          # multiplica os redutores de defender
    stats: dict = field(default_factory=dict)
    # escala (ConfigEscala, Parte C da TAREFA_PLANILHA_PROGRESSAO): None = desligada (o combate de sempre).
    # Fracao exata: a razao E_A / E_B do dano nao depende de um fator comum aos dois lados.
    escala: Fraction | None = None

    def para_dict(self) -> dict:
        d = {k: getattr(self, k) for k in (
            "rotulo", "estagio", "tecnica", "passiva", "hp_max", "guts_inicial", "guts_max", "regen",
            "mult_perto", "mult_disparo", "mult_guarda")} | {"stats": dict(self.stats)}
        if self.escala is not None:          # so aparece com a escala ligada: os logs antigos nao mudam
            d["escala"] = str(self.escala)
        return d


def escala_de(estagio: str, pontos_treino: float, esc: ConfigEscala) -> Fraction:
    """E = vida_por_estagio x (1 + beta x pontos treinados), como fracao exata."""
    return Fraction(esc.vida_por_estagio[estagio]) * (1 + Fraction(str(esc.beta_treino)) * Fraction(pontos_treino))


def perfil(forma: Forma, temperamento: dict | None = None, carater: dict | None = None,
           condicao: float = 1.0, cfg: ConfigCombateV21 | None = None, cat: ConfigCatalogo | None = None,
           treino: dict | None = None, normalizar_treino: bool = True, escala: ConfigEscala | None = None) -> Perfil:
    """Stats -> numeros de combate. `condicao` (do cuidado) multiplica hp_max e guts_inicial.
    `treino`: pontos treinados somados aos stats (normalizados ao orcamento na arena; absolutos na campanha).
    `escala` ligada: o treino e sempre normalizado (o tamanho vai para a escala E), a vida perde o multiplicador de
    estagio (a razao E_A/E_B faz esse papel) e o guts continua com ele (ritmo)."""
    cfg = cfg or CONFIG_COMBATE_V21
    cat = cat or CONFIG_CATALOGO
    esc = escala if escala is not None and escala.ligada else None
    if esc is not None:
        normalizar_treino = True
    if forma.estagio == "bebe":
        raise CatalogoInvalido("bebe nao luta")
    if not cat.condicao_mult_min <= condicao <= cat.condicao_mult_max:
        raise CatalogoInvalido(f"condicao {condicao} fora de [{cat.condicao_mult_min}, {cat.condicao_mult_max}]")
    s = stats(forma, temperamento, carater, cat)
    if treino:
        s = com_treino(s, treino, normalizar_treino, cat=cat)
    est = cat.mult_estagio[forma.estagio]
    guts_max = (cfg.guts_max_base + cfg.guts_max_por_folego * s["folego"]) * est
    est_vida = est if esc is None else 1.0
    return Perfil(
        rotulo=forma.rotulo, estagio=forma.estagio, tecnica=forma.tecnica, passiva=forma.passiva,
        hp_max=(cfg.hp_base + cfg.hp_por_vigor * s["vigor"]) * est_vida * condicao,
        guts_inicial=min(guts_max, (cfg.guts_inicial_base + cfg.guts_inicial_por_folego * s["folego"]) * est * condicao),
        guts_max=guts_max,
        regen=cfg.regen_base + cfg.regen_por_recuperacao * s["recuperacao"],
        mult_perto=cfg.mult_base + cfg.mult_por_ponto * s["forca"],
        mult_disparo=cfg.mult_base + cfg.mult_por_ponto * s["mira"],
        mult_guarda=cfg.guarda_base - cfg.guarda_por_ponto * s["guarda"],
        stats=s,
        escala=None if esc is None else escala_de(forma.estagio, sum((treino or {}).values()), esc),
    )


# ------------------------------------------------------------ transicoes

def ramo_da_crianca(fracao_cuidado: float, cat: ConfigCatalogo | None = None) -> str:
    cat = cat or CONFIG_CATALOGO
    if not 0.0 <= fracao_cuidado <= 1.0:
        raise CatalogoInvalido(f"fracao de cuidado fora de [0, 1]: {fracao_cuidado}")
    return "sereno" if fracao_cuidado >= cat.limiar_cuidado_sereno else "arisco"


def linha_do_adolescente(carater: dict, cat: ConfigCatalogo | None = None) -> str:
    """Eixo dominante (maior valor; empate: ordem fixa das linhas)."""
    cat = cat or CONFIG_CATALOGO
    car = _eixos(carater, cat.carater, "carater")
    eixo_da_linha = {l: cat.arquetipos_adolescente[l]["eixo"] for l in LINHAS}
    return max(LINHAS, key=lambda l: (car[eixo_da_linha[l]], -LINHAS.index(l)))


def forma_adulta(linha: str, carater: dict, sparring: int, cat: ConfigCatalogo | None = None) -> str | None:
    """None se ainda nao tem o sparring minimo (continua adolescente)."""
    cat = cat or CONFIG_CATALOGO
    if sparring < cat.sparring_minimo_adulto:
        return None
    car = _eixos(carater, cat.carater, "carater")
    arq = cat.arquetipos_adulto[linha]
    positivo = car[arq["eixo_complementar"]] >= 0.0
    for nome, f in arq["formas"].items():
        if (f["sinal"] == ">=0") == positivo:
            return nome
    raise CatalogoInvalido(f"linha {linha!r} sem forma para o sinal")


def carater_canonico(adulta: str, cfg: ConfigCombateV21 | None = None) -> dict:
    """Carater dos bots da bateria: eixo da linha +x, complementar com o sinal da forma.
    Forma sombria (substitui as duas da linha): so o eixo da linha."""
    cfg = cfg or CONFIG_COMBATE_V21
    cat = CONFIG_CATALOGO
    linha = LINHA_DA_FORMA[adulta]
    if adulta in FORMAS_SOMBRIAS:
        return {cat.arquetipos_adolescente[linha]["eixo"]: cfg.carater_bot_linha}
    arq = cat.arquetipos_adulto[linha]
    sinal = 1.0 if arq["formas"][adulta]["sinal"] == ">=0" else -1.0
    return {cat.arquetipos_adolescente[linha]["eixo"]: cfg.carater_bot_linha,
            arq["eixo_complementar"]: sinal * cfg.carater_bot_complementar}


def formas_da_especie(especie: str) -> list[Forma]:
    """As 15 formas visiveis de uma especie (1 bebe, 2 criancas, 4 adolescentes, 8 adultos).

    Visual: o ramo da crianca nao muda o sprite do adolescente/adulto (o caminho
    completo tem 16 variantes de stats por especie, mas 15 sprites).
    """
    saida = [Forma(especie, "bebe")]
    saida += [Forma(especie, "crianca", r) for r in RAMOS_CRIANCA]
    saida += [Forma(especie, "adolescente", "sereno", l) for l in LINHAS]
    saida += [Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[f], f) for f in FORMAS_ADULTAS]
    return saida
