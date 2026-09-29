"""A historia do pet: fatos de habito, gosto e marco tirados do registro (DESIGN_VOZ_PROPRIA, secao 2).

Funcao pura do registro: o mesmo `RegistroVida` da sempre os mesmos fatos, na mesma ordem (teste). O extrator
nao escreve texto livre: cada fato sai de um molde fixo por regra, com os dados estruturados ao lado.

Tipos (o id do fato na fala e a letra + a posicao na lista):
  H  habito meu      sequencia A -> B entre as acoes do pet; acao mais frequente num periodo do dia
  O  habito do dono  periodo em que ele aparece; o cuidado que mais faz; cede a manha com petisco; demora nos chamados
  P  gosto           acao que o aprendizado mais puxou para cima / para baixo (sonda do carater); treino favorito;
                     revanche (o ultimo rival que o venceu e ainda nao foi vencido depois)
  L  marco           evolucoes, primeira vitoria e derrota, "perdi N vezes antes de vencer", lesoes, ausencias do
                     dono, a forma sombria, filho de um cruzamento

`registro_de_motor` monta o registro a partir de um MotorEducacao ja rejogado; as acoes do pet nao estao no log
e vem de `fabrica_com_captura`, que anota cada decisao durante o replay. Os limiares ficam em ConfigHistoria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from typing import Callable, Sequence

from .config import CONFIG_HISTORIA, TICKS_POR_DIA, ConfigHistoria
from .events import AcaoUsuario, LogDeEventos

PERIODOS = (("madrugada", 0, 6), ("manha", 6, 12), ("tarde", 12, 18), ("noite", 18, 24))
TEXTO_PERIODO = {"madrugada": "de madrugada", "manha": "de manhã", "tarde": "à tarde", "noite": "à noite"}
# acao do pet: 1a pessoa ("eu ...") e infinitivo ("depois de ...")
PET_EU = {"dormir": "durmo", "comer": "como", "brincar": "brinco", "chamar_atencao": "chamo você",
          "explorar": "exploro", "emburrar": "emburro"}
PET_INF = {"dormir": "dormir", "comer": "comer", "brincar": "brincar", "chamar_atencao": "chamar você",
           "explorar": "explorar", "emburrar": "emburrar"}
CUIDADO_DONO = {AcaoUsuario.ALIMENTAR.value: "me dar comida", AcaoUsuario.LIMPAR.value: "me limpar",
                AcaoUsuario.BRINCAR.value: "brincar comigo", AcaoUsuario.ACARICIAR.value: "me dar carinho",
                AcaoUsuario.PETISCO.value: "me dar petisco"}
# nivel na tela (nomes Digimon; ids internos nao mudam)
NIVEL = {"bebe": "In-Training", "crianca": "Rookie", "adolescente": "Champion", "adulto": "Ultimate"}
TIPOS = ("H", "O", "P", "L")
MAX_TEXTO = 80
_PROIBIDOS = set("[]{}\n\r")


class HistoriaInvalida(ValueError):
    """Registro malformado ou fato que nao cabe no molde."""


@dataclass(frozen=True)
class FatoHistoria:
    tipo: str            # H, O, P ou L
    regra: str           # nome da regra (ex.: "sequencia", "ausencia")
    chave: str           # identidade estavel do fato (para nao repetir o mesmo assunto)
    texto: str           # molde preenchido, 1a pessoa do pet
    tick: int            # quando aconteceu (marco) ou o fim da janela observada (habito, gosto)
    dados: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS:
            raise HistoriaInvalida(f"tipo de fato desconhecido: {self.tipo!r}")
        if not self.texto or len(self.texto) > MAX_TEXTO or _PROIBIDOS & set(self.texto):
            raise HistoriaInvalida(f"texto fora do molde: {self.texto!r}")

    def para_dict(self) -> dict:
        return {"tipo": self.tipo, "regra": self.regra, "chave": self.chave, "texto": self.texto, "tick": self.tick,
                "dados": dict(self.dados)}


@dataclass(frozen=True)
class RegistroVida:
    """Tudo o que o extrator le. Listas ordenadas por tick; so dados (nada de motor)."""

    tick_final: int
    acoes_dono: tuple = ()          # (tick, acao do dono: AcaoUsuario.value)
    acoes_pet: tuple = ()           # (tick, AcaoPet.value), uma por decisao
    janelas: tuple = ()             # historico_janelas do MotorEducacao (dicts)
    sessoes_treino: tuple = ()      # (tick, exercicio)
    lutas: tuple = ()               # historico_lutas (dicts com tick, rival, resultado, lesao)
    evolucoes: tuple = ()           # (tick, estagio), em ordem
    sombria_tick: int | None = None
    filho_de_cruzamento: bool = False
    desvio_por_acao: tuple = ()     # (acao do pet, desvio da politica sobre o bandit recem-nascido), sonda do carater

    def ate(self, tick: int) -> "RegistroVida":
        """o registro como era antes de `tick` (para saber quando um fato apareceu)"""
        def corte(xs, t=lambda x: x[0]):
            return tuple(x for x in xs if t(x) < tick)
        return RegistroVida(
            tick_final=min(self.tick_final, tick), acoes_dono=corte(self.acoes_dono), acoes_pet=corte(self.acoes_pet),
            janelas=tuple(j for j in self.janelas if j["fim"] < tick), sessoes_treino=corte(self.sessoes_treino),
            lutas=tuple(x for x in self.lutas if x["tick"] < tick), evolucoes=corte(self.evolucoes),
            sombria_tick=self.sombria_tick if self.sombria_tick is not None and self.sombria_tick < tick else None,
            filho_de_cruzamento=self.filho_de_cruzamento, desvio_por_acao=self.desvio_por_acao)


def periodo_do_tick(tick: int) -> str:
    hora = (tick % TICKS_POR_DIA) // 60
    for nome, a, b in PERIODOS:
        if a <= hora < b:
            return nome
    raise HistoriaInvalida(f"hora fora do dia: {hora}")


def dia_do_tick(tick: int) -> int:
    return tick // TICKS_POR_DIA + 1


def _episodios(acoes_pet: Sequence) -> list[tuple[int, str]]:
    """inicio de cada trecho de uma mesma acao (fora ocioso): a acao repetida decisao a decisao conta uma vez"""
    out, anterior = [], None
    for tick, a in acoes_pet:
        if a != anterior and a != "ocioso":
            out.append((tick, a))
        anterior = a
    return out


# ------------------------------------------------------------ H: habitos do pet
def _sequencias(ep: list, c: ConfigHistoria, fim: int) -> list[FatoHistoria]:
    if not ep:
        return []
    seguintes = []                         # por episodio: acoes que comecam em (t, t + janela]
    j = 0
    for i, (t, _) in enumerate(ep):
        j = max(j, i + 1)
        while j < len(ep) and ep[j][0] <= t:
            j += 1
        k, s = j, set()
        while k < len(ep) and ep[k][0] <= t + c.janela_seq_min:
            s.add(ep[k][1])
            k += 1
        seguintes.append(s)
    n = len(ep)
    acoes = sorted({a for _, a in ep})
    base = {b: sum(b in s for s in seguintes) / n for b in acoes}
    fatos = []
    for a in acoes:
        idx = [i for i, (_, x) in enumerate(ep) if x == a]
        if len(idx) < c.min_ocorrencias_seq:
            continue
        for b in acoes:
            if b == a or base[b] == 0:
                continue
            p = sum(b in seguintes[i] for i in idx) / len(idx)
            lift = p / base[b]
            if p >= c.prob_seq_min and lift >= c.lift_min:
                fatos.append(FatoHistoria("H", "sequencia", f"H:seq:{a}:{b}",
                                          f"quase sempre {PET_EU[b]} depois de {PET_INF[a]}", fim,
                                          {"a": a, "b": b, "prob": p, "lift": lift, "ocorrencias": len(idx)}))
    return fatos


def _periodos_pet(ep: list, c: ConfigHistoria, fim: int) -> list[FatoHistoria]:
    fatos = []
    for a in sorted({x for _, x in ep}):
        ts = [t for t, x in ep if x == a]
        media = len(ts) / len(PERIODOS)                 # periodos de 6 h: a media do dia por periodo
        for nome, _, _ in PERIODOS:
            k = sum(periodo_do_tick(t) == nome for t in ts)
            if k >= c.min_ocorrencias_periodo and k >= c.fator_periodo * media:
                fatos.append(FatoHistoria("H", "periodo", f"H:per:{a}:{nome}",
                                          f"{TEXTO_PERIODO[nome]} eu {PET_EU[a]} mais", fim,
                                          {"acao": a, "periodo": nome, "ocorrencias": k, "media": media}))
    return fatos


# ------------------------------------------------------------ O: habitos do dono
def _dono(r: RegistroVida, c: ConfigHistoria) -> list[FatoHistoria]:
    fatos, fim, acoes = [], r.tick_final, r.acoes_dono
    if acoes:
        n = len(acoes)
        for nome, _, _ in PERIODOS:
            ts = [t for t, _ in acoes if periodo_do_tick(t) == nome]
            dias = len({dia_do_tick(t) for t in ts})
            if len(ts) / n >= c.fracao_periodo_dono and dias >= c.dias_periodo_dono:
                fatos.append(FatoHistoria("O", "periodo_dono", f"O:per:{nome}",
                                          f"você costuma aparecer {TEXTO_PERIODO[nome]}", fim,
                                          {"periodo": nome, "fracao": len(ts) / n, "dias": dias}))
        cont = {a: sum(x == a for _, x in acoes) for a in CUIDADO_DONO}
        melhor = max(sorted(cont), key=lambda a: cont[a])
        if cont[melhor] / n >= c.fracao_cuidado_dono:
            fatos.append(FatoHistoria("O", "cuidado_dono", f"O:cui:{melhor}",
                                      f"o que você mais faz é {CUIDADO_DONO[melhor]}", fim,
                                      {"acao": melhor, "fracao": cont[melhor] / n}))
    manhas = [j for j in r.janelas if j["tipo"] == "chamado" and j["falso"] and j["desfecho"] in ("cedido", "corrigido")]
    if len(manhas) >= c.min_manhas:
        cede = sum(j["desfecho"] == "cedido" for j in manhas) / len(manhas)
        if cede >= c.fracao_cede_manha:
            fatos.append(FatoHistoria("O", "cede_manha", "O:manha", "quando faço manha, você cede com petisco", fim,
                                      {"fracao": cede, "manhas": len(manhas)}))
    chamados = [j for j in r.janelas if (j["tipo"] == "aviso" or (j["tipo"] == "chamado" and not j["falso"]))]
    if len(chamados) >= c.min_chamados_demora:
        med = median(j["fim"] - j["inicio"] for j in chamados)
        if med <= c.demora_rapida_min:
            fatos.append(FatoHistoria("O", "demora", "O:demora", "você atende meus chamados rápido", fim,
                                      {"mediana_min": med, "chamados": len(chamados), "rapido": True}))
        elif med >= c.demora_lenta_min:
            fatos.append(FatoHistoria("O", "demora", "O:demora", "você demora para atender meus chamados", fim,
                                      {"mediana_min": med, "chamados": len(chamados), "rapido": False}))
    return fatos


# ------------------------------------------------------------ P: gostos
def _gostos(r: RegistroVida, c: ConfigHistoria, nome_rival: Callable[[str], str]) -> list[FatoHistoria]:
    fatos, fim = [], r.tick_final
    desvio = dict(r.desvio_por_acao)
    desvio.pop("ocioso", None)
    if desvio:
        ordem = sorted(desvio)
        alto = max(ordem, key=lambda a: desvio[a])
        baixo = min(ordem, key=lambda a: desvio[a])
        if desvio[alto] >= c.limiar_gosto:
            fatos.append(FatoHistoria("P", "gosto", f"P:gosto:{alto}", f"gosto de {PET_INF[alto]}", fim,
                                      {"acao": alto, "desvio": desvio[alto]}))
        if desvio[baixo] <= -c.limiar_gosto:
            fatos.append(FatoHistoria("P", "desgosto", f"P:desgosto:{baixo}", f"não curto {PET_INF[baixo]}", fim,
                                      {"acao": baixo, "desvio": desvio[baixo]}))
    if len(r.sessoes_treino) >= c.min_sessoes_treino:
        cont: dict[str, int] = {}
        for _, e in r.sessoes_treino:
            cont[e] = cont.get(e, 0) + 1
        fav = max(sorted(cont), key=lambda e: cont[e])
        if cont[fav] / len(r.sessoes_treino) >= c.fracao_treino_favorito:
            fatos.append(FatoHistoria("P", "treino_favorito", f"P:treino:{fav}",
                                      f"meu treino favorito é {fav.replace('_', ' ')}", fim,
                                      {"exercicio": fav, "fracao": cont[fav] / len(r.sessoes_treino)}))
    ultimo_que_venceu = None
    for x in r.lutas:
        if x["resultado"] == "derrota":
            ultimo_que_venceu = x
        elif x["resultado"] == "vitoria" and ultimo_que_venceu is not None and x["rival"] == ultimo_que_venceu["rival"]:
            ultimo_que_venceu = None
    if ultimo_que_venceu is not None:
        rv = ultimo_que_venceu["rival"]
        fatos.append(FatoHistoria("P", "revanche", f"P:revanche:{rv}", f"quero revanche contra {nome_rival(rv)}",
                                  ultimo_que_venceu["tick"], {"rival": rv}))
    return fatos


# ------------------------------------------------------------ L: marcos
def _marcos(r: RegistroVida, c: ConfigHistoria, nome_rival: Callable[[str], str]) -> list[FatoHistoria]:
    fatos = []
    for t, est in r.evolucoes:
        fatos.append(FatoHistoria("L", "evolucao", f"L:evo:{est}", f"virei {NIVEL[est]} no dia {dia_do_tick(t)}", t,
                                  {"estagio": est}))
    primeira = {}
    derrotas_antes: dict[str, int] = {}
    for x in r.lutas:
        res, rv, t = x["resultado"], x["rival"], x["tick"]
        if res in ("vitoria", "derrota") and res not in primeira:
            primeira[res] = x
            txt = "venci minha primeira luta" if res == "vitoria" else "perdi minha primeira luta"
            fatos.append(FatoHistoria("L", f"primeira_{res}", f"L:primeira:{res}", f"{txt} no dia {dia_do_tick(t)}",
                                      t, {"rival": rv}))
        if res == "derrota":
            derrotas_antes[rv] = derrotas_antes.get(rv, 0) + 1
        elif res == "vitoria" and rv in derrotas_antes:
            n = derrotas_antes.pop(rv)
            if n >= 2:
                fatos.append(FatoHistoria("L", "venceu_depois", f"L:depois:{rv}:{t}",
                                          f"perdi para {nome_rival(rv)} {n} vezes antes de vencer", t,
                                          {"rival": rv, "derrotas": n}))
        if x.get("lesao"):
            tratou = any(a == AcaoUsuario.TRATAR_LESAO.value and t <= td for td, a in r.acoes_dono)
            txt = "e você me tratou" if tratou else "e ninguém me tratou"
            fatos.append(FatoHistoria("L", "lesao", f"L:lesao:{t}", f"me machuquei no dia {dia_do_tick(t)} {txt}", t,
                                      {"tratada": tratou}))
    ticks = [t for t, _ in r.acoes_dono]
    for a, b in zip([0] + ticks, ticks + [r.tick_final]):
        if b - a >= c.ausencia_min:
            h = (b - a) // 60
            fatos.append(FatoHistoria("L", "ausencia", f"L:ausencia:{a}", f"você sumiu por {h} h no dia {dia_do_tick(a)}",
                                      b, {"inicio": a, "fim": b, "horas": h}))
    if r.sombria_tick is not None:
        fatos.append(FatoHistoria("L", "sombria", "L:sombria", "virei uma forma sombria", r.sombria_tick, {}))
    if r.filho_de_cruzamento:
        fatos.append(FatoHistoria("L", "cruzamento", "L:cruzamento", "nasci de um cruzamento de dois pets", 0, {}))
    return fatos


def _rival_padrao(nome: str) -> str:
    """'sparring:brigao@brasa' -> 'o brigão'; 'npc:tier1_brutamontes' -> 'o brutamontes'"""
    _, _, resto = nome.partition(":")
    base = resto.split("@")[0].split("_")[-1]
    return f"o {base}"


def extrair(r: RegistroVida, c: ConfigHistoria | None = None,
            nome_rival: Callable[[str], str] = _rival_padrao) -> list[FatoHistoria]:
    """Todos os fatos do registro, em ordem fixa: L (por tick), H, P, O. Funcao pura."""
    c = c or CONFIG_HISTORIA
    ep = _episodios(r.acoes_pet)
    fim = r.tick_final
    marcos = sorted(_marcos(r, c, nome_rival), key=lambda f: (f.tick, f.chave))
    habitos = _sequencias(ep, c, fim) + _periodos_pet(ep, c, fim)
    return marcos + habitos + _gostos(r, c, nome_rival) + _dono(r, c)


def selecionar(fatos: Sequence[FatoHistoria], citados_recentes: Sequence[Sequence[str]] = (),
               c: ConfigHistoria | None = None) -> list[FatoHistoria]:
    """Ate max_fatos para uma fala: marcos recentes primeiro, depois habitos, gostos e habitos do dono. Um fato
    citado (pela chave) nas ultimas `falas_recentes` falas vai para o fim, para o pet nao repetir o assunto; no
    maximo `max_por_regra` fatos de cada regra (os mais recentes)."""
    c = c or CONFIG_HISTORIA
    recentes = {k for fala in list(citados_recentes)[-c.falas_recentes:] for k in fala}
    ordem = {"L": 0, "H": 1, "P": 2, "O": 3}
    chave = lambda f: (f.chave in recentes, ordem[f.tipo], -f.tick if f.tipo == "L" else 0, f.chave)  # noqa: E731
    out, por_regra = [], {}
    for f in sorted(fatos, key=chave):
        if por_regra.get(f.regra, 0) < c.max_por_regra:
            por_regra[f.regra] = por_regra.get(f.regra, 0) + 1
            out.append(f)
    return out[:c.max_fatos]


def ids(fatos: Sequence[FatoHistoria]) -> list[tuple[str, FatoHistoria]]:
    """id de cada fato na fala: letra do tipo + posicao entre os do mesmo tipo (H1, H2, O1...)"""
    cont: dict[str, int] = {}
    out = []
    for f in fatos:
        cont[f.tipo] = cont.get(f.tipo, 0) + 1
        out.append((f"{f.tipo}{cont[f.tipo]}", f))
    return out


# ------------------------------------------------------------ registro a partir do motor
def fabrica_com_captura(fabrica_motor: Callable, destino: list) -> Callable:
    """Embrulha a fabrica do motor: cada decisao do pet vai para `destino` como (tick, acao). So observa: o motor
    faz exatamente o mesmo (teste)."""
    def fabrica(politica, cfg, semente):
        m = fabrica_motor(politica, cfg, semente)
        original = m._decisao_observada

        def observada(transicao):
            destino.append((m._estado.tick, transicao.acao.value))
            original(transicao)
        m._decisao_observada = observada
        return m
    return fabrica


def registro_de_motor(motor, acoes_pet: Sequence, log: LogDeEventos | None = None,
                      desvio_por_acao: dict | None = None) -> RegistroVida:
    """RegistroVida de um MotorEducacao (ao vivo ou rejogado). As acoes do pet vem de fabrica_com_captura."""
    log = log if log is not None else motor.log
    acoes_dono = tuple((e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario")
    evolucoes = tuple(sorted((v["tick"], est) for est, v in motor.transicoes.items()))
    sombria_tick = motor.transicoes["adulto"]["tick"] if motor.sombria else None
    return RegistroVida(
        tick_final=motor.estado()["tick"], acoes_dono=acoes_dono, acoes_pet=tuple(acoes_pet),
        janelas=tuple(dict(j) for j in motor.historico_janelas),
        sessoes_treino=tuple((s.tick, s.exercicio) for s in motor.treino.sessoes if not s.enrolou),
        lutas=tuple(dict(x) for x in motor.historico_lutas), evolucoes=evolucoes, sombria_tick=sombria_tick,
        filho_de_cruzamento=motor.origem is not None,
        desvio_por_acao=tuple(sorted((desvio_por_acao or {}).items())))


def desvio_por_acao(politica, base, n_estados: int, amostras: int, semente_sonda: int) -> dict:
    """desvio medio da politica sobre `base` (o bandit recem-nascido), por acao, na sonda do carater (mesmos
    estados e numeros aleatorios comuns de evolucao.carater)"""
    from .metrics import distribuicoes_de_acao, estados_sonda
    estados = estados_sonda(n_estados, semente_sonda)
    dp = distribuicoes_de_acao(politica, estados, amostras, semente_sonda)
    di = distribuicoes_de_acao(base, estados, amostras, semente_sonda)
    return {a: sum(p[a] - q[a] for p, q in zip(dp, di)) / len(estados) for a in dp[0]}
