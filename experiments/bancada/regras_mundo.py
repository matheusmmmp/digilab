"""A bancada da V2, módulo `regras_mundo`.

O tapa na fruta X, as regras e os informantes do mundo, as vidas pelo mundo e o registro da medição.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import random
from dataclasses import replace

from digilab.config import CONFIG_DONOS, CONFIG_PADRAO, TICKS_POR_DIA, ConfigBola, ConfigFrutas
from digilab.gestos import DonoComGestos
from digilab.donos import Visao, cuidados_necessarios, julgar_acao
from digilab.events import ACOES_FRUTAS, FRUTAS, AcaoPet, AcaoUsuario, fruta_de, informar
from digilab.frutas import DonoInformante, DonoPedinte, JulgadorFruta
from digilab.mundo import CanalMundo, DeixarBola, DeixarComida, MotorMundo
from digilab.protocol import derivar_semente
from digilab.state import Estado
from digilab.treino import CanalDeInteracao, OrcamentoExcedido, OrcamentoNaoConsumido


# ------------------------------------------------------------------ o tapa na fruta X (corpo, adendo 1, A1.1)


def fruta_tapa(semente: int) -> str:
    """A fruta X do P1-c-tapaX (A1.1): sorteada uma vez por vida por derivar_semente("tapa-fruta", semente), uniforme entre as tres, sem
    olhar a preferencia inata. E a regra do N7-6 (DonoPedinte.sortear_fruta) com outra rng; nao toca outra."""
    rng = random.Random(derivar_semente("tapa-fruta", semente))
    return FRUTAS[rng.randrange(len(FRUTAS))]


class DonoTapaFruta:
    """O dono do P1-c-tapaX (adendo 1 do plano do corpo, A1.1): o DonoComGestos sem tapa (`base`) mais o tapa na fruta X. Em cada passo,
    um `tapa` por consumo novo de X (lidos em estado()["consumos_frutas"], que o motor expoe com a ConfigJulgamentoFruta ligada) vem
    PRIMEIRO, ate o maximo do passo: e o primeiro passo do dono depois do consumo, dentro do orcamento e como contato (CD-6). O dono
    embrulhado decide com a `Visao` do que sobra (gasto + n, minimo e maximo - n; a regra do DonoJulgaFruta), entao o canal fecha o mesmo
    orcamento. O que nao coube no passo fica em `descartados` (o tick do consumo; nao volta depois). `tapas` guarda (tick do consumo, tick
    do tapa)."""

    def __init__(self, base, fruta: str) -> None:
        if fruta not in FRUTAS:
            raise ValueError(f"fruta {fruta!r}: so {FRUTAS}")
        if not isinstance(base, DonoComGestos) or base.modo != "sem_tapa":
            raise ValueError("o tapa na fruta X vai por cima do DonoComGestos sem tapa (A1.1)")
        self.base = base
        self.fruta = fruta
        self.nome = base.nome
        self.tapas: list[tuple[int, int]] = []
        self.descartados: list[int] = []
        self._vistos = 0

    @property
    def trocas(self) -> dict:
        return self.base.trocas

    def decidir(self, visao: Visao, rng: random.Random) -> list:
        consumos = visao.estado["consumos_frutas"]
        if len(consumos) < self._vistos:
            raise RuntimeError(f"consumos voltaram atras: {self._vistos} -> {len(consumos)}")
        novos, self._vistos = consumos[self._vistos:], len(consumos)
        de_x = [t for t, f in novos if f == self.fruta]
        n = min(len(de_x), visao.maximo_permitido)
        self.descartados.extend(de_x[n:])
        self.tapas.extend((t, visao.estado["tick"]) for t in de_x[:n])
        resto = replace(visao, gasto=visao.gasto + n, minimo_obrigatorio=max(0, visao.minimo_obrigatorio - n),
                        maximo_permitido=visao.maximo_permitido - n)
        return [AcaoUsuario.TAPA] * n + self.base.decidir(resto, rng)


# ------------------------------------------------------------------ o mundo da bola com B1 e B2


class RegraBola:
    """Decisoes B1 e B2 (2026-10-01, docs/RESULTADO_V2_A1.md): quem poe a bola e uma regra do MUNDO, fora do orcamento do dono.
    A regra dos coerentes da A1 (DonoComBola), sem a condicao do limite do passo (a bola nao gasta orcamento): atencioso e
    incoerente poem com o pet acordado, fora da noite, sem cuidado pendente, sem bola no cenario e no maximo `bolas_por_dia`
    por dia; o relapso so nos passos em que ele mesmo agiu (as visitas; B3: aceito como e). O aleatorio NAO poe bola (B1: o
    `por_bola` sai do sorteio dele, e ele nao tem outra regra). Le a visao de ANTES das acoes do dono do passo, como a A1."""

    def __init__(self, dono: str, cfg_bola: ConfigBola, cfg_donos=None, cfg=None) -> None:
        self.dono = dono
        self.cb = cfg_bola
        self.cd = cfg_donos or CONFIG_DONOS
        self.cfg = cfg or CONFIG_PADRAO
        self._dia = -1
        self._bolas_hoje = 0

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        if self.dono == "aleatorio":
            return []
        e = visao.estado
        dia = e["tick"] // TICKS_POR_DIA
        if dia != self._dia:
            self._dia, self._bolas_hoje = dia, 0
        if self.dono == "relapso" and not acoes_do_dono:
            return []
        if (self._bolas_hoje < self.cb.bolas_por_dia and not e["dormindo"] and not self.cfg.e_noite(e["tick_do_dia"])
                and e.get("bola") is None and not cuidados_necessarios(e, self.cd)):
            self._bolas_hoje += 1
            return [AcaoUsuario.POR_BOLA]
        return []


class InformanteDoMundo:
    """O DonoInformante (frutas.py, que nao muda) com o efeito REAL do mundo da bancada (E7; `efeitos_da_condicao`), sobre cada fruta
    oferecida, logo depois da oferta. No mutavel o efeito real troca em `tick_troca`: antes, o dono sabe o do casado; dali em diante,
    o do descasado (dois DonoInformante, escolhidos pelo tick)."""

    def __init__(self, modo: str, efeitos: dict, tick_troca: int | None) -> None:
        self.modo = modo
        self.antes = DonoInformante(modo, efeitos["antes"])
        self.depois = DonoInformante(modo, efeitos["depois"]) if efeitos["depois"] is not None else None
        if (self.depois is None) != (tick_troca is None):
            raise ValueError("so o mutavel troca o efeito, e ele precisa do tick_troca")
        self.tick_troca = tick_troca

    def acoes(self, tick: int, ofertadas: list[str]) -> list[AcaoUsuario]:
        d = self.depois if self.depois is not None and tick >= self.tick_troca else self.antes
        return d.acoes(tick, ofertadas)

    @property
    def feitas(self) -> list[tuple[int, str, str]]:
        return sorted(self.antes.feitas + (self.depois.feitas if self.depois else []))


class InformanteAcoplado:
    """P2a (plano do N5, secao 4.2; decisao N5-4): o MESMO multiconjunto de (fruta, conteudo verdadeiro) que o P2 da unidade recebe,
    em ticks sorteados uniformemente ao longo da vida, pela rng derivar_semente("informacao-acoplada", semente). O multiconjunto sai do
    CalendarioFrutas (que nao depende do pet), passo a passo, com o conteudo do `certo` no tick original; cada item ganha um passo do
    dono sorteado (rng.randrange sobre os passos, na ordem do calendario) e vai ao motor nesse passo, pela ordem original. Fora de
    hora: a informacao muitas vezes fala de uma fruta que nao esta no cenario. No mutavel o conteudo e o verdadeiro NO TICK ORIGINAL
    (e o mesmo multiconjunto do P2), entao um item levado para o outro lado da troca deixa de ser verdadeiro. O modo `acoplado` do
    DonoInformante (docs/TAREFA_V2_N5_ACOPLADO.md, chat A) tem de dar os mesmos eventos; ate ele entrar, a bancada usa este."""

    def __init__(self, semente: int, dias: int, cf: ConfigFrutas, efeitos: dict, tick_troca: int | None) -> None:
        cd = CONFIG_DONOS
        passos = dias * TICKS_POR_DIA // cd.passo_ticks
        verdade = InformanteDoMundo("certo", efeitos, tick_troca)
        calendario = CalendarioFrutas(semente, cf)
        itens: list[tuple[int, str, str]] = []                       # (tick original, fruta, conteudo)
        for passo in range(passos):
            tick = (passo + 1) * cd.passo_ticks                       # o tick da visao do dono em simular_vida_mundo
            ofertas = calendario.decidir(Visao(estado={"tick": tick}, passo=passo, passos_totais=passos, orcamento=0, gasto=0,
                                                minimo_obrigatorio=0, maximo_permitido=0), [])
            for a in verdade.acoes(tick, [fruta_de(o) for o in ofertas]):
                f, c = a.value.split("_")[2:]
                itens.append((tick, f, c))
        rng = random.Random(derivar_semente("informacao-acoplada", semente))
        self.agenda: dict[int, list[tuple[str, str]]] = {}
        self.itens = itens
        for _, f, c in itens:
            tick = (rng.randrange(passos) + 1) * cd.passo_ticks
            self.agenda.setdefault(tick, []).append((f, c))
        self.feitas: list[tuple[int, str, str]] = []

    def acoes(self, tick: int, ofertadas: list[str]) -> list[AcaoUsuario]:
        out = []
        for f, c in self.agenda.get(tick, []):
            self.feitas.append((tick, f, c))
            out.append(informar(f, c))
        return out


class RegraFrutasComJulgador:
    """K4 fora do orcamento (decisao do Matheus, 2026-10-05): o julgamento da fruta (JulgadorFruta, #170) primeiro, como no
    simular_vida_frutas (logo depois das acoes do dono do passo, com o estado do passo), e depois o que a regra de dentro poe (as
    ofertas). Os julgamentos sao elogiar/repreender, os unicos extras que esta regra poe fora do orcamento; `feitos` os conta."""

    def __init__(self, regra, julgador: JulgadorFruta) -> None:
        if julgador.cj.no_orcamento:
            raise ValueError("a regra do mundo so leva o julgamento fora do orcamento")
        self.regra = regra
        self.julgador = julgador
        self.feitos = 0
        # o feedback (elogiar/repreender) so entra fora do orcamento por esta regra; a informacao ja e FORA_DO_ORCAMENTO (P2d, P3i)
        proprios = JULGAMENTOS if julgador.saida == "feedback" else frozenset()
        self.extras_fora_do_orcamento = proprios | getattr(regra, "extras_fora_do_orcamento", frozenset())

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        julg = self.julgador.acoes(visao.estado)
        self.feitos += len(julg)
        return julg + self.regra.decidir(visao, acoes_do_dono)


class RegraFrutasComInformante:
    """O canal do mundo das frutas com um informante: as ofertas do calendario e, logo depois, o que o informante diz (fora do
    orcamento, B2). O informante recebe as frutas oferecidas no passo (o acoplado as ignora)."""

    def __init__(self, calendario: CalendarioFrutas, informante) -> None:
        self.calendario = calendario
        self.informante = informante
        self.extras_fora_do_orcamento = getattr(calendario, "extras_fora_do_orcamento", frozenset())

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        ofertas = self.calendario.decidir(visao, acoes_do_dono)
        return ofertas + self.informante.acoes(visao.estado["tick"], [fruta_de(o) for o in ofertas])


class RegraFrutasComPedinte:
    """N7: o canal do mundo das frutas com o dono que pede (DonoPedinte, N7-MUNDO): o que a regra de dentro poe (as ofertas e, no P2, a
    informacao) e, logo depois, as acoes do pedinte com o estado do passo e as frutas oferecidas: a bronca da desobediencia (so no P3+ped)
    e o pedido "deixe X". Tudo fora do orcamento (B2), como no simular_vida_frutas."""

    def __init__(self, regra, pedinte: DonoPedinte) -> None:
        self.regra = regra
        self.pedinte = pedinte
        proprios = frozenset({AcaoUsuario.REPREENDER.value}) if pedinte.bronca else frozenset()
        self.extras_fora_do_orcamento = proprios | getattr(regra, "extras_fora_do_orcamento", frozenset())

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        eventos = self.regra.decidir(visao, acoes_do_dono)
        ofertadas = [fruta_de(e) for e in eventos if e in ACOES_FRUTAS]
        return eventos + self.pedinte.acoes(visao.estado, ofertadas)


class _Espiao:
    """So nos testes: embrulha a politica do braco e anota tudo o que chega por `receber_acao_dono` (o gate "a informacao nunca chega
    ao aprendiz como sinal")."""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.nome = interna.nome
        self.recebidas: list[tuple[str, int]] = []

    def agir(self, obs, rng):
        return self.interna.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self.recebidas.append((acao.value, tick))
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def simular_vida_mundo(dono, regra_mundo, politica, semente: int, dias: int, orcamento: int, rotulo_dono: str,
                       fabrica_motor, canal_classe=CanalDeInteracao):
    """treino.simular_vida com um canal do MUNDO fora do orcamento (B2): a cada passo o dono age pelo CanalDeInteracao (o
    orcamento exato de sempre) e depois a regra do mundo poe o que pos, direto no motor (entra no log, nao no canal). O dono
    nao ve os eventos do mundo no gasto do orcamento. Mesma rng do dono que simular_vida (derivada de semente e rotulo_dono).
    `canal_classe`: o CanalComGestos nos bracos com os gestos do corpo (o SemGesto gasta o orcamento sem ir ao motor)."""
    cfg, cd = CONFIG_PADRAO, CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cd.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cd.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono))
    canal = canal_classe(motor, orcamento, cd.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cd.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        acoes = dono.decidir(visao, rng_dono)
        canal.aplicar(acoes, passo, passos)
        permitidos = FORA_DO_ORCAMENTO | getattr(regra_mundo, "extras_fora_do_orcamento", frozenset())
        for evento in regra_mundo.decidir(visao, acoes):
            if evento.value not in permitidos:
                raise ValueError(f"a regra do mundo so poe eventos do mundo, informacao ou pedido, nao {evento.value!r}")
            motor.observar(evento)
    canal.fechar()
    return motor


class CanalSemEnsino(CanalMundo):
    """PMF-3 (PLANO_ANALISE_V2_MUNDO_FISICO, secao 2): os donos so com o cuidado, pelo filtro sem_ensino de hoje aplicado AO VIVO. O dono
    decide como sempre (o mesmo dono sintetico, no mesmo ritmo do orcamento); o elogio e a bronca contam no orcamento dele, mas nao chegam
    ao motor nem ao log (`retirados`). O resto vai como no CanalMundo (o deixar_comida e o deixar_bola gastam o orcamento)."""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.retirados = 0

    def aplicar(self, acoes: list, passo: int, passos_totais: int) -> None:
        minimo, maximo = self.limites(passo, passos_totais)
        if len(acoes) > maximo:
            raise OrcamentoExcedido(f"passo {passo}: dono pediu {len(acoes)} interacoes, maximo {maximo}")
        if len(acoes) < minimo:
            raise OrcamentoNaoConsumido(f"passo {passo}: dono fez {len(acoes)} interacoes, minimo {minimo}")
        for acao in acoes:
            if isinstance(acao, AcaoUsuario) and acao.value in SINAIS:
                self.retirados += 1                        # o sem_ensino: gasta o orcamento do dono, nao chega ao pet
            elif isinstance(acao, DeixarComida):
                self.motor.deixar_comida(acao.tipo, acao.x, acao.y)
            elif isinstance(acao, DeixarBola):
                self.motor.deixar_bola(acao.x, acao.y)
            elif isinstance(acao, AcaoUsuario):
                aceita = getattr(self.motor, "aceita", None)
                if aceita is not None and not aceita(acao):
                    self.rejeitados += 1
                    continue
                self.motor.observar(acao)
            else:
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            self.gasto += 1


def simular_vida_fisico(dono, politica, semente: int, dias: int, orcamento: int, rotulo_dono: str, fabrica_motor, carinho=None,
                        mudanca=None):
    """O mundo.simular_vida_mundo com o CanalSemEnsino (PMF-3): o dono (embrulhado pelo DonoComLugar) cuida pelos gestos do mundo, que
    gastam o orcamento, e o elogio e a bronca dele ficam fora. A rng do dono e a de sempre (`dono`, semente, rotulo do dono: igual em todo
    braco). `mudanca` (o J5, `RegraMudancaPQP`): os eventos da mudanca do teste depois das acoes do dono do passo (e do carinho), fora do
    orcamento. Devolve (motor, sinais retirados)."""
    cfg, cd = CONFIG_PADRAO, CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cd.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cd.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    if not isinstance(motor, MotorMundo) or not motor.cmf.ligada:
        raise ValueError("simular_vida_fisico precisa do MotorMundo com o mundo ligado")
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono))
    canal = CanalSemEnsino(motor, orcamento, cd.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cd.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
        if carinho is not None:                  # banheiro (#265): o carinho depois das acoes do dono do passo, fora do orcamento
            for acao in carinho.acoes(motor.estado()):
                motor.observar(acao)
        if mudanca is not None:                  # o J5: a mudanca do teste (a fruta na mao ou a troca de tipo), fora do orcamento
            for acao in mudanca.acoes(motor.estado()):
                motor.observar(acao)
    canal.fechar()
    return motor, canal.retirados


def sondar_metabolismo(corpo, destino: list) -> None:
    """A sonda do metabolismo no replay de medicao, so de leitura: embrulha o `passo` do corpo e anota, a cada tick, (tick do pet no
    comeco do tick, dormindo, combustivel e reserva no fim do tick). Nao muda nada do corpo (o replay de medicao e conferido bit a bit)."""
    original = corpo.passo

    def passo(antes, *a, **kw):
        r = original(antes, *a, **kw)
        destino.append((antes.tick, bool(antes.dormindo), corpo.q["combustivel"], corpo.q["reserva"]))
        return r
    corpo.passo = passo


def comeu_fruta_e2(passo: dict) -> bool:
    """A decisao tem o sinal da E2 (o humor nos drives): a fruta comida e a acao foi COMER, a regra do cerebro (lobos.consequencia_mundo
    e o _creditar_corpo). No mundo fisico o motor avisa `fruta_comida` tambem no "achou e comeu" do explorar, e o cerebro credita esse
    explorar com o sinal do N3, sem o humor (MUNDO-CALIBRACAO, 2026-10-12); fora do mundo fisico, so o comer come fruta."""
    return passo["fruta"] is not None and passo["acao"] == AcaoPet.COMER.value


class _Registro:
    """Embrulha a politica do braco no replay de medicao: anota cada decisao (tick, estado como o dono o julga, acao), a
    amostra de estado (em privacao, saude), os sinais do dono que chegaram ao aprendiz ate ali e os que o dono deu. So le;
    repassa tudo."""

    def __init__(self, interna: PoliticaDoBraco) -> None:
        self.interna = interna
        self.nome = interna.nome
        self._tick_ultimo_cuidado = 0
        self.decisoes: list[tuple[int, dict, str]] = []
        self.amostras: list[tuple[bool, float]] = []
        self.sinais_na_decisao: list[int] = []
        self.sinais_do_dono = 0
        self.bola: list[tuple[bool, str, str]] = []      # (bola no cenario, regra do instinto/impulso, acao), por decisao
        self.vetores: list[tuple] = []                     # (indice, fome, higiene, energia, humor), por decisao
        self.espacos: list[tuple] = []                     # N6: (frutas no curto, frutas no longo prazo) depois de cada decisao
        self.acordado: list[bool] = []                     # mundo fisico: o pet acordado na decisao (as horas acordado da taxa media)
        # adendo 2 do corpo: por decisao observada, o tick, a regra e o estado antes e depois da propria acao (na fruta, o depois e o
        # estado logo depois de comer, o mesmo da E2)
        self.passos_sinal: list[dict] = []
        self.corpo: list = []                              # corpo: a PercepcaoCorpo de cada decisao (None sem o corpo)
        self.carinhos: list = []                           # gestos: (tick, PercepcaoCorpo antes, depois) de cada carinho pelo corpo
        self._decisao: tuple | None = None

    @property
    def sinais(self) -> int:
        return self.interna.sinais_entregues

    def agir(self, obs, rng):
        acao = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        estado = {"fome": v[0], "higiene": v[1], "energia": v[2], "tick_do_dia": int(round(v[7] * TICKS_POR_DIA))}
        self.decisoes.append((obs.ticks_desde_cuidado + self._tick_ultimo_cuidado, estado, acao.value))
        self.amostras.append((Estado(fome=v[0], higiene=v[1], energia=v[2]).em_privacao(CONFIG_PADRAO), v[4]))
        self.sinais_na_decisao.append(self.interna.sinais_entregues)
        self.bola.append((obs.bola > 0.0, self.interna.ultima_regra, acao.value))
        self.vetores.append((len(self.vetores), v[0], v[1], v[2], v[3]))
        self.acordado.append(v[6] == 0.0)
        self.corpo.append(obs.corpo)                       # corpo: os receptores da decisao (None sem o corpo)
        self._decisao = (self.decisoes[-1][0], self.interna.ultima_regra)
        mem = getattr(self.interna.cerebro, "_memoria", None)   # N6, so le: a memoria dos lobos depois de promover (o que a decisao viu)
        if mem is not None:
            self.espacos.append((tuple(e["fruta"] for e in mem.curto), tuple(e["fruta"] for e in mem.longo)))
        return acao

    def observar(self, transicao) -> None:
        tick, regra = self._decisao
        self.passos_sinal.append({"tick": tick, "regra": regra, "k": len(self.decisoes) - 1, "acao": transicao.acao.value,
                                  "antes": transicao.observacao.vetor_estado,
                                  "depois": transicao.observacao_seguinte.vetor_estado, "fruta": None,
                                  "antes_corpo": transicao.observacao.corpo, "depois_corpo": None})
        self.interna.observar(transicao)

    def consequencia_corpo(self, acao, ocorrido: dict, obs_depois) -> None:
        """O gancho do MotorCorpo (uma chamada por decisao, logo depois dos estimulos da propria acao): so anota os receptores de
        depois na decisao observada e repassa (o cerebro sem o gancho, como o instinto, nao recebe nada)."""
        if not self.passos_sinal or self.passos_sinal[-1]["depois_corpo"] is not None:
            raise RuntimeError("corpo: gancho de consequencia sem decisao observada (ou o segundo na mesma decisao)")
        self.passos_sinal[-1]["depois_corpo"] = obs_depois.corpo
        gancho = getattr(self.interna, "consequencia_corpo", None)
        if gancho is not None:
            gancho(acao, ocorrido, obs_depois)

    def fruta_comida(self, fruta: str, obs_depois) -> None:
        """O gancho da E2: a decisao de comer a fruta tem o sinal do estado logo depois de comer. So anota e repassa (o cerebro sem o
        gancho, como o instinto, nao recebe nada, como antes)."""
        ultimo = self.passos_sinal[-1]
        if ultimo["fruta"] is not None:
            raise RuntimeError("duas frutas comidas na mesma decisao")
        ultimo["depois"], ultimo["fruta"] = obs_depois.vetor_estado, fruta
        aviso = getattr(self.interna, "fruta_comida", None)
        if aviso is not None:
            aviso(fruta, obs_depois)

    def receber_acao_dono(self, acao, tick) -> None:
        self._tick_ultimo_cuidado = tick          # toda acao do dono zera o relogio de cuidado (state.aplicar_acao_usuario)
        self.sinais_do_dono += acao.value in SINAIS_DO_DONO
        self.interna.receber_acao_dono(acao, tick)

    def mudanca_no_corpo(self, obs_antes, obs_depois) -> None:
        """O carinho com `gestos` (o MotorCorpo nao o passa por `receber_acao_dono`): e contato e zera o relogio de cuidado no instante
        dele, o `ticks_desde_cuidado` do `obs_antes` (a conta do cerebro). So acerta o relogio, anota os receptores (as medidas do carinho
        do banheiro) e repassa."""
        self._tick_ultimo_cuidado += obs_antes.ticks_desde_cuidado
        self.carinhos.append((self._tick_ultimo_cuidado, obs_antes.corpo, obs_depois.corpo))
        self.interna.mudanca_no_corpo(obs_antes, obs_depois)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _julgar(estado: dict, acao: str) -> int:
    return julgar_acao({**estado, "acao_atual": acao}, CONFIG_DONOS)


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .mundos import CalendarioFrutas, JULGAMENTOS  # noqa: E402
from .bracos import FORA_DO_ORCAMENTO, PoliticaDoBraco, SINAIS, SINAIS_DO_DONO  # noqa: E402
