"""O grupo: N pets de verdade no mesmo mundo fisico (V2; docs/TAREFA_V2_DOIS_PETS.md, etapa 2; desenho docs/futuro/dois_pets.md, secoes 2
a 4; DP-1 a DP-3 e DP-7 decididas pelo Matheus em 2026-10-07).

Cada pet continua com o proprio motor (o `MotorMundo`, com o `MotorCorpo` por cima quando ligado), o proprio `Estado`, as proprias rngs de
ambiente e de politica (engine.py nao muda) e o proprio cerebro. Os motores apontam para o mesmo `Mundo` (digilab/mundo.py). O `Grupo` so
avanca os motores no mesmo relogio, um tick por vez, e grava o registro do grupo; nao decide nada.

A vez no tick (DP-2): em cada tick em que dois ou mais pets decidem, o fluxo `mundo-ordem` (`derivar_semente("mundo-ordem", s)`) sorteia a
ordem; o primeiro age inteiro (decide, anda, come) e o segundo percebe o mundo como ficou. Os pets ficam numa lista ordenada pelo
identificador, e o sorteio escolhe dessa lista (nunca a ordem do codigo). Com um pet so, nao ha sorteio, e o fluxo nem e criado. O
embaralhamento e o do `random.shuffle` do CPython, escrito com `randrange` (Fisher-Yates), para o TS repetir os mesmos numeros.

As sementes (secao 2): a semente do mundo e a do grupo, s; o primeiro pet usa s (sozinho no mapa, e a vida de hoje de semente s); o segundo
usa `derivar_semente("segundo-pet", s)`. Os fluxos do pet (`alvo`, `mundo-sujeira`, e os do dono, `dono` e `dono-lugar`) saem da semente
dele.

O relogio: o do mundo (o do grupo) e o de cada pet. O pet entra num inicio de dia do mundo (ConfigGrupo; o experiente da secao 11 vive K
dias antes do outro chegar, e o mundo pode passar dias sem pet nenhum); o relogio dele (o Estado, o log, o corpo, a Vida) comeca em 0 na
entrada, e a hora do dia e a mesma nos dois. O Mundo e os registros do mundo fisico usam o relogio do mundo.

O registro do grupo (DP-3): o cabecalho (a semente, os pets com a semente, a entrada, o rotulo do cerebro e do dono, o layout) e os eventos,
no relogio do mundo, cada um com o destino (`grupo`: o avanco e a entrada; `mundo`: deixar a comida e a bola; `pet:<id>`: o limpar, o
acariciar, o tapa...), o pet (o do orcamento do dono, que recebe o contato) e a origem (`dono`; com dois donos, na etapa 7, `dono:<id>`). O
avanco e um so, do grupo. A projecao de um pet (`RegistroGrupo.projecao`) e o log de hoje dele, evento a evento, no relogio dele; o log do
proprio motor e essa projecao (conferido no G1). Nao entra no registro o que um pet faz, ve ou come: isso sai do replay.

O replay (`reproduzir_grupo`) refaz o grupo do cabecalho e rejoga os eventos no mesmo relogio, com a mesma ordem sorteada, e falha alto se o
registro refeito diferir do lido.

O dono (DP-7, a validacao inicial): um dono sintetico para todos, com o orcamento por pet (ConfigGrupo.orcamento_por_dia por dia vivido) e
as rngs de cada pet; ele decide o cuidado de cada pet so pelo que ve daquele pet (`simular_grupo`, `PetNoGrupo`).

Os sentidos sobre o outro (etapa 3; desenho, secao 5; DP-11, degrau 1): a visao e o toque. O grupo monta a `PercepcaoSocial` de cada
pet so com o que e fisico (a posicao dos outros, a acao que se ve de fora, o consumo visto, o contato) e a poe no `obs.social`; nunca o
estado interno do outro. O toque e uma conta do grupo no fim de cada tick com decisao, depois de os pets agirem na vez sorteada: ha contato
com as celulas a ate `ConfigGrupo.raio_toque_celulas` em Chebyshev, e o tipo (disputa, encostar, esbarrar) sai do que aconteceu no tick. A
disputa e a comida que um comeu e o outro tinha como alvo (neste tick, ou o alvo que ele trazia da decisao anterior): o primeiro na vez
come, o segundo nao acha (MF-2). Os registros (`contatos`, `disputas` e, em cada motor, os consumos vistos, as idas a `onde_comeu` e o
tempo a vista) sao derivados: nada disso entra no registro do grupo, o replay refaz. O toque nao mexe no corpo (degrau 3).

O cheiro proprio, o rastro e o som (etapa 8; desenho, secoes 5.3, 5.4 e 5.6; DP-11, degrau 1b), atras da ConfigSentidos (desligada: o
grupo de hoje, byte a byte), e so com dois pets presentes (sozinho, nada e guardado). O rastro mora no Mundo: cada pet deixa uma marca por
decisao, na posicao da decisao. O som e um evento do grupo: quando um pet come, brinca com a bola, chama ou emburra, cada outro presente a
menos de R_som o ouve (a linha reta, OA-3) e guarda na caixa dele, com a direcao e a distancia e a intensidade no centro e no ponto de cada
ouvido (pela direcao do ultimo passo de quem ouve); a caixa vai para a percepcao da decisao seguinte e se esvazia. A percepcao de cada pet
(`PercepcaoSentidos` em `obs.social.sentidos`) tem o cheiro de cada outro (o cheiro dele e o rastro dele, a conta inteira do cheiro da
comida num canal separado, OA-1), a direcao pronta do mundo (OA-2) e a intensidade no ponto de cada narina, para o orgao do corpo (DP-13). Os
sons emitidos (`sons`) sao derivados; a ConfigSentidos vai no cabecalho do registro (so ligada), e o replay a confere.

So biblioteca padrao.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from typing import Callable

from .config import CONFIG_DONOS, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, CONFIG_SENTIDOS, TICKS_POR_DIA, Config, ConfigDonos, ConfigGrupo
from .config import ConfigMundo, ConfigSentidos
from .donos import Visao
from .events import AcaoUsuario, Evento, LogDeEventos, avanco, ler_deixar_bola, ler_deixar_comida
from .events import deixar_bola as evento_deixar_bola
from .events import deixar_comida as evento_deixar_comida
from .mundo import (CANDIDATOS_SOCIAIS, PASSO_INICIAL, SONS, CanalMundo, MotorMundo, Mundo, PercepcaoSentidos, PercepcaoSocial, celula_de,
                    cheiro_do_pet, direcao_vizinha, distancia, em_contato, fontes_do_pet, perceber_social, som_ouvido, tipos_do_contato)
from .protocol import derivar_semente

ROTULO_ORDEM = "mundo-ordem"                 # o fluxo da vez no tick (DP-2)
ROTULO_SEGUNDO_PET = "segundo-pet"           # a semente do segundo pet (secao 2)
VERSAO_REGISTRO = 1
DESTINO_GRUPO = "grupo"
DESTINO_MUNDO = "mundo"
ORIGEM_DONO = "dono"                         # um dono para todos (DP-7, a validacao inicial); dois donos: `dono:<id>` (etapa 7)


class GrupoSemChave(RuntimeError):
    """O grupo com ConfigGrupo.ligada = False."""


class RegistroDivergente(ValueError):
    """O replay refez um registro diferente do lido."""


def sementes_do_grupo(semente: int, ids: tuple) -> dict[str, int]:
    """O primeiro pet usa a semente do grupo; o segundo, `derivar_semente("segundo-pet", s)` (secao 2)."""
    if len(ids) > 2:
        raise ValueError("so dois pets nesta etapa")
    out = {ids[0]: semente}
    if len(ids) == 2:
        out[ids[1]] = derivar_semente(ROTULO_SEGUNDO_PET, semente)
    return out


def destino_do_pet(ident: str) -> str:
    return f"pet:{ident}"


# ================================================================== o registro do grupo
@dataclass(frozen=True)
class EventoGrupo:
    """Um evento do registro do grupo, no relogio do mundo."""

    tick: int
    tipo: str                # entrada | avanco | acao_usuario | deixar_comida | deixar_bola
    valor: str | int         # o valor do evento de hoje (o avanco em ticks; a acao; "tipo|x|y"; "x|y"); na entrada, o id do pet
    destino: str             # grupo | mundo | pet:<id>
    pet: str | None = None   # o pet do evento (a entrada; o do orcamento do dono)
    origem: str | None = None    # quem causou (o dono); o avanco e a entrada nao tem origem

    def para_dict(self) -> dict:
        return {"tick": self.tick, "tipo": self.tipo, "valor": self.valor, "destino": self.destino, "pet": self.pet,
                "origem": self.origem}

    @staticmethod
    def de_dict(d: dict) -> "EventoGrupo":
        if set(d) != {"tick", "tipo", "valor", "destino", "pet", "origem"}:
            raise ValueError(f"evento do grupo com campos errados: {sorted(d)}")
        return EventoGrupo(int(d["tick"]), str(d["tipo"]), d["valor"], str(d["destino"]), d["pet"], d["origem"])


class RegistroGrupo:
    """O cabecalho e os eventos do grupo (DP-3). JSONL: a primeira linha e o cabecalho, as outras os eventos."""

    def __init__(self, cabecalho: dict, eventos: list[EventoGrupo] | None = None) -> None:
        self.cabecalho = cabecalho
        self.eventos: list[EventoGrupo] = list(eventos or [])

    def anexar(self, evento: EventoGrupo) -> None:
        self.eventos.append(evento)

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, RegistroGrupo) and self.para_jsonl() == outro.para_jsonl()

    def para_jsonl(self) -> str:
        linhas = [json.dumps({"cabecalho": self.cabecalho}, sort_keys=True, separators=(",", ":"))]
        linhas += [json.dumps(e.para_dict(), sort_keys=True, separators=(",", ":")) for e in self.eventos]
        return "\n".join(linhas) + "\n"

    @staticmethod
    def de_jsonl(texto: str) -> "RegistroGrupo":
        linhas = [l for l in texto.splitlines() if l.strip()]
        if not linhas:
            raise ValueError("registro do grupo vazio")
        primeira = json.loads(linhas[0])
        if set(primeira) != {"cabecalho"}:
            raise ValueError("a primeira linha do registro do grupo tem de ser o cabecalho")
        return RegistroGrupo(primeira["cabecalho"], [EventoGrupo.de_dict(json.loads(l)) for l in linhas[1:]])

    def projecao(self, ident: str) -> LogDeEventos:
        """O log de hoje do pet `ident`, no relogio dele: os avancos depois da entrada e os eventos do dono dele, sem o destino."""
        pet = self.cabecalho["pets"].get(ident)
        if pet is None:
            raise KeyError(f"pet fora do grupo: {ident!r}")
        entrada = pet["entrada"]
        eventos = []
        dentro = False
        for e in self.eventos:
            if e.tipo == "entrada":
                dentro = dentro or e.valor == ident
            elif e.tipo == "avanco":
                if dentro:
                    eventos.append(Evento(e.tick - entrada, "avanco", e.valor))
            elif e.pet == ident:
                eventos.append(Evento(e.tick - entrada, e.tipo, e.valor))
        return LogDeEventos(eventos)


# ================================================================== o grupo
class Grupo:
    """N motores sobre um `Mundo`, no mesmo relogio. Nao decide nada: so chama cada motor na vez sorteada e grava o registro."""

    def __init__(self, cfg_mundo: ConfigMundo, semente: int, cfg_grupo: ConfigGrupo | None = None, cfg: Config | None = None,
                 cfg_sentidos: ConfigSentidos | None = None) -> None:
        self.cg = cfg_grupo or CONFIG_GRUPO_LIGADA
        if not self.cg.ligada:
            raise GrupoSemChave("o grupo so existe com ConfigGrupo.ligada (sem ela, o MotorMundo de um pet e dono do proprio Mundo)")
        self.cfg = cfg or CONFIG_PADRAO
        self.cs = cfg_sentidos or CONFIG_SENTIDOS        # o degrau 1b (etapa 8): desligada, o grupo de hoje
        self.semente = semente
        self.mundo = Mundo(cfg_mundo, semente)
        self.sementes = sementes_do_grupo(semente, self.cg.ids)
        self.tick = 0                            # o relogio do mundo
        self.motores: dict[str, MotorMundo] = {}
        self._rng_ordem: random.Random | None = None     # so com dois pets decidindo no mesmo tick
        self.interacoes: dict[str, int] = {}     # o gasto do dono de cada pet (simular_grupo)
        self.ordens: list[dict] = []             # {tick, decidem, ordem}: as vezes sorteadas (derivadas; o replay refaz)
        self.contatos: list[dict] = []           # o toque (secao 5.2): um por par e por tick com decisao, com o tipo de cada um
        self.disputas: list[dict] = []           # a comida que um comeu e o outro tinha como alvo: quem ganhou, a vez, as distancias
        self.registro = RegistroGrupo({"versao": VERSAO_REGISTRO, "semente": semente, "ids": list(self.cg.ids),
                                       "layout": cfg_mundo.layout.nome, "pets": {}})
        if self.cs.ligada:
            self.mundo.ligar_marcas()
            self.sons: list[dict] = []               # os sons emitidos (derivados): tick, quem, o som, onde, quem ouviu
            self.registro.cabecalho["sentidos"] = asdict(self.cs)

    # ------------------------------------------------------------ a entrada
    def entrar(self, ident: str, politica, fabrica_motor: Callable, cerebro: str, dono: str) -> MotorMundo:
        """O pet `ident` entra agora (um inicio de dia do mundo), com a semente dele. `fabrica_motor(politica, cfg, semente, mundo=,
        entrada_mundo=)` monta o motor sobre o mundo do grupo. `cerebro` e `dono` sao os rotulos do cabecalho."""
        if ident not in self.cg.ids:
            raise ValueError(f"pet fora do grupo: {ident!r} (ids {self.cg.ids})")
        if ident in self.motores:
            raise ValueError(f"o pet {ident!r} ja entrou")
        if self.tick % TICKS_POR_DIA:
            raise ValueError(f"o pet entra num inicio de dia do mundo: tick {self.tick}")
        motor = fabrica_motor(politica, self.cfg, self.sementes[ident], mundo=self.mundo, entrada_mundo=self.tick)
        if not isinstance(motor, MotorMundo) or not motor.cmf.ligada or motor.mundo is not self.mundo:
            raise ValueError("a fabrica do grupo tem de devolver um MotorMundo ligado sobre o mundo do grupo")
        if motor.semente != self.sementes[ident] or motor.entrada_mundo != self.tick:
            raise ValueError("a fabrica do grupo tem de passar a semente e a entrada que recebe")
        for outro in self.motores.values():      # o efeito de cada fruta e do mundo: o mesmo para todos
            if outro.efeito_frutas != motor.efeito_frutas:
                raise ValueError(f"efeito_frutas diferente entre os pets: {outro.efeito_frutas} x {motor.efeito_frutas}")
        if motor._estado.tick != 0 or len(motor.log):
            raise ValueError("o pet entra recem-nascido (tick 0, log vazio)")
        self._conferir_orgaos(motor)
        motor._grupo, motor.ident = self, ident
        if self.cs.ligada and motor._passo is None:
            motor._passo = PASSO_INICIAL             # a direcao do ultimo passo antes do primeiro passo
        self.motores[ident] = motor
        self.registro.cabecalho["pets"][ident] = {"semente": self.sementes[ident], "entrada": self.tick, "cerebro": cerebro, "dono": dono}
        self.registro.anexar(EventoGrupo(self.tick, "entrada", ident, DESTINO_GRUPO, ident))
        return motor

    def ids_presentes(self) -> list[str]:
        return [i for i in self.cg.ids if i in self.motores]

    def pet(self, ident: str) -> "PetNoGrupo":
        if ident not in self.motores:
            raise KeyError(f"o pet {ident!r} nao entrou")
        return PetNoGrupo(self, ident)

    # ------------------------------------------------------------ o tempo
    def avancar(self, ticks: int) -> None:
        """Um avanco do grupo (um evento so): cada pet presente ganha o avanco no proprio log, e os ticks andam intercalados."""
        ev = avanco(self.tick, ticks)            # valida (positivo)
        self.registro.anexar(EventoGrupo(self.tick, "avanco", ev.valor, DESTINO_GRUPO))
        for i in self.ids_presentes():
            m = self.motores[i]
            m.log.anexar(avanco(m._estado.tick, ticks))
        self._avancar(ticks)

    def _avancar(self, ticks: int) -> None:
        presentes = self.ids_presentes()
        for i in presentes:
            self.motores[i]._abrir_avanco()
        for _ in range(ticks):
            decidem = [i for i in presentes if self.motores[i]._estado.tick >= self.motores[i]._proxima_decisao]
            ordem = self._sortear(decidem) if len(decidem) >= 2 else decidem
            for i in ordem + [i for i in presentes if i not in decidem]:
                self.motores[i]._um_tick()
            if decidem and len(presentes) >= 2:
                self._toque_e_disputa(presentes, ordem)
            self.tick += 1
        for i in presentes:
            m = self.motores[i]
            m._fechar_avanco()
            if m._estado.tick + m.entrada_mundo != self.tick:     # o relogio do pet anda com o do mundo
                raise RuntimeError(f"o relogio do pet {i} saiu do relogio do mundo")

    def _sortear(self, decidem: list[str]) -> list[str]:
        """DP-2: um sorteio por tick com dois ou mais pets decidindo, no fluxo `mundo-ordem`, sobre a lista ordenada pelo id (o
        random.shuffle do CPython, escrito com randrange)."""
        if self._rng_ordem is None:
            self._rng_ordem = random.Random(derivar_semente(ROTULO_ORDEM, self.semente))
        ordem = list(decidem)
        for k in range(len(ordem) - 1, 0, -1):
            j = self._rng_ordem.randrange(k + 1)
            ordem[k], ordem[j] = ordem[j], ordem[k]
        self.ordens.append({"tick": self.tick, "decidem": list(decidem), "ordem": list(ordem)})
        return ordem

    # ------------------------------------------------------------ os sentidos sobre o outro (etapa 3)
    def perceber_social(self, ident: str) -> PercepcaoSocial | None:
        """A visao e o toque do pet `ident` agora (secoes 5.1 e 5.2), so do que e fisico: a posicao e a acao visivel de cada outro presente
        e a memoria do proprio pet (o consumo visto, o ultimo contato). None com o pet sozinho no grupo."""
        outros = [i for i in self.ids_presentes() if i != ident]
        if not outros:
            return None
        m = self.motores[ident]
        fisico = [(i, *self.motores[i].pet, self.motores[i]._acao_atual.value) for i in outros]
        sentidos = self.perceber_sentidos(ident, outros) if self.cs.ligada else None
        return perceber_social(*m.pet, self.tick, fisico, m._viu_comer, m._toques, m._raio_visao, sentidos)

    # ------------------------------------------------------------ o cheiro proprio, o rastro e o som (etapa 8; degrau 1b)
    MUNDO_OLFATO = ("afastamento_narinas", "cheiro_pet", "cheiro_marca", "raio_celulas", "idade_marca", "max_marcas")
    MUNDO_OUVIDO = ("afastamento_ouvidos", "som", "raio_som_celulas")

    def _conferir_orgaos(self, motor: MotorMundo) -> None:
        """O orgao do corpo de um pet do grupo le o mundo do grupo: o Olfato social e a Audicao exigem a ConfigSentidos ligada, e os
        numeros do mundo do orgao (o afastamento, o rastro, o raio, o som) tem de ser os do grupo (uma config so; falha alto)."""
        co, cv = getattr(motor, "co", None), getattr(motor, "cv", None)
        corpo = getattr(motor, "cc", None)
        if corpo is None or not corpo.ligada:
            return
        if co is not None and co.ligada:
            if co.outro_pet and not self.cs.ligada:
                raise ValueError("o Olfato social (ConfigOlfato.outro_pet) no grupo exige a ConfigSentidos ligada (o rastro e do mundo)")
            difs = [c for c in self.MUNDO_OLFATO if getattr(co, c) != getattr(self.cs.olfato, c)]
            if difs:
                raise ValueError(f"os numeros do mundo do olfato do pet nao sao os do grupo: {difs}")
        if cv is not None and cv.ligada:
            if not self.cs.ligada:
                raise ValueError("a Audicao (ConfigOuvido) no grupo exige a ConfigSentidos ligada (o som e do mundo)")
            difs = [c for c in self.MUNDO_OUVIDO if getattr(cv, c) != getattr(self.cs.ouvido, c)]
            if difs:
                raise ValueError(f"os numeros do mundo do ouvido do pet nao sao os do grupo: {difs}")

    def sentidos_ativos(self) -> bool:
        """o degrau 1b guarda e emite so com a chave e com dois pets presentes (desenho, secao 5: sozinho, nada e guardado)"""
        return self.cs.ligada and len(self.motores) >= 2

    def perceber_sentidos(self, ident: str, outros: list[str]) -> PercepcaoSentidos:
        """o que o pet `ident` sente dos `outros` agora (secoes 5.3, 5.4 e 5.6), so do que e fisico: o canal de cada outro (o cheiro na
        posicao dele e o rastro que ele deixou no mundo) e a caixa dos sons que o proprio pet ouviu desde a decisao anterior"""
        m, sub = self.motores[ident], self.mundo.cmf.sub
        cheiro = []
        for i in outros:
            fontes = fontes_do_pet(*self.motores[i].pet, self.mundo.marcas_de(i), self.tick, self.cs.olfato)
            cheiro.append((i, *cheiro_do_pet(*m.pet, m._passo, fontes, self.cs.olfato, sub)))
        sons = tuple((*s[:7], self.tick - s[7]) for s in m._sons_ouvidos)
        return PercepcaoSentidos(m._passo, tuple(cheiro), sons)

    def emitir_som(self, quem: str, som: str) -> None:
        """secao 5.4: o pet `quem` fez o som agora, onde esta. Cada outro presente a menos de R_som o ouve, em linha reta, e guarda na caixa
        (quem, o som, a direcao, a distancia, a intensidade no centro e nos dois ouvidos, o tick). Sem os sentidos ativos, nada."""
        if not self.sentidos_ativos():
            return
        if som not in SONS:
            raise ValueError(f"som desconhecido: {som!r}")
        sx, sy = self.motores[quem].pet
        ouvintes, onde = [], {}
        for i in self.ids_presentes():
            if i == quem:
                continue
            m = self.motores[i]
            onde[i] = [*m.pet, m._passo]               # onde estava e para onde olhava cada outro (a auditoria e as medidas)
            ouvido = som_ouvido(*m.pet, m._passo, sx, sy, self.cs.ouvido, self.mundo.cmf.sub)
            if ouvido is None:
                continue
            m._sons_ouvidos.append((quem, som, *ouvido, self.tick))
            # o orgao do ouvido (DP-14): o som entra no passo do tick do mundo em que o ouvinte esta (o deste tick, se ele ainda nao andou
            # o tick; o seguinte, se ja andou)
            if getattr(m, "cv", None) is not None and m.cv.ligada and m.cc.ligada:
                m._sons_orgao.append((m._tm(m._estado.tick), som, *ouvido[2:]))
            ouvintes.append(i)
        self.sons.append({"tick": self.tick, "emissor": quem, "som": som, "x": sx, "y": sy, "ouvintes": ouvintes, "outros": onde})

    def viu_comer(self, quem: str, x: int, y: int) -> None:
        """o pet `quem` comeu a comida de (x, y) agora: cada outro que o tem a vista (dentro do raio, neste momento) guarda o ponto"""
        mq = self.motores[quem]
        for i in self.ids_presentes():
            if i == quem:
                continue
            m = self.motores[i]
            d = distancia(mq.pet[0] - m.pet[0], mq.pet[1] - m.pet[1])
            if d <= m._raio_visao:
                m._viu_comer[quem] = (x, y, self.tick)
                m.vistos_comer.append({"tick": self.tick, "outro": quem, "x": x, "y": y, "d": d})

    def _no_tick(self, m: MotorMundo) -> dict | None:
        ts = m._tick_social
        return ts if ts is not None and ts["tick"] == self.tick else None

    def _toque_e_disputa(self, presentes: list[str], ordem: list[str]) -> None:
        """o fim de um tick com decisao (secao 5.2): por par, a disputa (registrada com ou sem contato) e o contato com o tipo de cada um"""
        cmf = self.mundo.cmf
        for k, a in enumerate(presentes):
            for b in presentes[k + 1:]:
                ma, mb = self.motores[a], self.motores[b]
                disputa = self._disputa(a, b) or self._disputa(b, a)
                contato = em_contato(ma.pet, mb.pet, cmf, self.cg.raio_toque_celulas)
                if disputa is not None:
                    disputa["contato"] = contato
                    self.disputas.append(disputa)
                if not contato:
                    continue
                seguiu = {i: self._seguiu(self.motores[i]) for i in (a, b)}
                tipos = tipos_do_contato(a, b, disputa, seguiu)
                (ax, ay), (bx, by) = celula_de(*ma.pet, cmf), celula_de(*mb.pet, cmf)
                sinal = lambda v: (v > 0) - (v < 0)  # noqa: E731
                direcoes = {a: direcao_vizinha(sinal(bx - ax), sinal(by - ay)), b: direcao_vizinha(sinal(ax - bx), sinal(ay - by))}
                for eu, outro in ((a, b), (b, a)):
                    self.motores[eu]._toques[outro] = (tipos[eu], direcoes[eu], self.tick)
                self.contatos.append({"tick": self.tick, "pets": [a, b], "tipos": tipos, "direcoes": direcoes,
                                      "celulas": {a: [ax, ay], b: [bx, by]}, "decidem": list(ordem)})

    def _seguiu(self, m: MotorMundo) -> str | None:
        """o id do pet que `m` seguiu neste tick (o candidato `seguir`, ou o continuar dele), ou None"""
        ts = self._no_tick(m)
        if ts is None or ts["alvo"] is None:
            return None
        alvo = ts["alvo"]
        classe = alvo.de if alvo.tipo == "continuar" else alvo.tipo
        return ts["social"] if classe == "seguir" else None

    def _disputa(self, vencedor: str, perdedor: str) -> dict | None:
        """o `vencedor` comeu neste tick a comida que o `perdedor` tinha como alvo neste tick, ou trazia como alvo pendente"""
        mv, mp = self.motores[vencedor], self.motores[perdedor]
        tv = self._no_tick(mv)
        if tv is None or tv["comeu"] is None:
            return None
        c = tv["comeu"]
        tp = self._no_tick(mp)
        alvos = []
        if tp is not None:
            alvos += [tp["alvo"]] + ([tp["pendente_antes"]["alvo"]] if tp["pendente_antes"] is not None else [])
        elif mp._pendente is not None:
            alvos.append(mp._pendente["alvo"])
        if not any(a is not None and a.objeto() == "comida" and a.id == c["id"] for a in alvos):
            return None
        de_v = tv["de"]
        de_p = tp["de"] if tp is not None else mp.pet
        vez = self.ordens[-1]["ordem"] if self.ordens and self.ordens[-1]["tick"] == self.tick else None
        return {"tick": self.tick, "comida": c["id"], "tipo": c["tipo"], "situacao": c["situacao"], "vencedor": vencedor,
                "perdedor": perdedor, "vencedor_primeiro": None if vez is None else vez.index(vencedor) < vez.index(perdedor),
                "d_vencedor": distancia(c["x"] - de_v[0], c["y"] - de_v[1]), "d_perdedor": distancia(c["x"] - de_p[0], c["y"] - de_p[1]),
                "perdedor_decidiu": tp is not None}

    # ------------------------------------------------------------ o dono (DP-7: o orcamento e o contato sao de um pet)
    def acao_dono(self, ident: str, acao: AcaoUsuario) -> None:
        m = self.motores[ident]
        self.registro.anexar(EventoGrupo(self.tick, "acao_usuario", acao.value, destino_do_pet(ident), ident, ORIGEM_DONO))
        m.observar(acao)

    def deixar_comida(self, ident: str, tipo: str, x: int, y: int) -> None:
        m = self.motores[ident]
        ev = evento_deixar_comida(self.tick, tipo, x, y)        # valida antes do registro
        self.registro.anexar(EventoGrupo(self.tick, ev.tipo, ev.valor, DESTINO_MUNDO, ident, ORIGEM_DONO))
        m.deixar_comida(tipo, x, y)

    def deixar_bola(self, ident: str, x: int, y: int) -> None:
        m = self.motores[ident]
        ev = evento_deixar_bola(self.tick, x, y)
        self.registro.anexar(EventoGrupo(self.tick, ev.tipo, ev.valor, DESTINO_MUNDO, ident, ORIGEM_DONO))
        m.deixar_bola(x, y)

    # ------------------------------------------------------------ leitura
    def resumo(self) -> dict:
        """o mundo, as vezes sorteadas e o que cada pet guarda (o G1 do grupo compara isto bit a bit)"""
        r = {"tick": self.tick, "mundo": self.mundo.resumo(), "ordens": self.ordens,
             "rng_ordem": None if self._rng_ordem is None else self._rng_ordem.getstate(),
             "contatos": self.contatos, "disputas": self.disputas,
             "pets": {i: _resumo_do_pet(m) for i, m in self.motores.items()}}
        if self.cs.ligada:
            r["sentidos"] = {"sons": self.sons, "pets": {i: {"passo": m._passo, "sons_ouvidos": [list(s) for s in m._sons_ouvidos],
                                                             "sons_orgao": [list(s) for s in m._sons_orgao]}
                                                         for i, m in self.motores.items()}}
        return r


def _resumo_do_pet(m: MotorMundo) -> dict:
    return {"estado": repr(m._estado), "estado_motor": m.estado(), "acoes": m.acoes_recentes(10 ** 9),
            "rngs": [m._rng_politica.getstate(), m._rng_ambiente.getstate()], "fisico": m.resumo_mundo_fisico(),
            "politica": m.politica.estado_interno(), "log": m.log.para_jsonl(), "entrada": m.entrada_mundo,
            "social": m.resumo_social()}


class PetNoGrupo:
    """A porta do dono para um pet do grupo: o que o CanalMundo chama no motor, gravado no registro do grupo com o destino e a origem."""

    def __init__(self, grupo: Grupo, ident: str) -> None:
        self.grupo = grupo
        self.ident = ident
        self.motor = grupo.motores[ident]

    def observar(self, acao: AcaoUsuario) -> None:
        self.grupo.acao_dono(self.ident, acao)

    def deixar_comida(self, tipo: str, x: int, y: int) -> None:
        self.grupo.deixar_comida(self.ident, tipo, x, y)

    def deixar_bola(self, x: int, y: int) -> None:
        self.grupo.deixar_bola(self.ident, x, y)

    def estado(self) -> dict:
        return self.motor.estado()

    def __getattr__(self, nome: str):
        if nome == "aceita":                     # o CanalMundo pergunta se o motor tem `aceita`
            return getattr(self.motor, nome)
        raise AttributeError(nome)


# ================================================================== o replay
def reproduzir_grupo(registro: RegistroGrupo, fabricas: dict[str, tuple[Callable, Callable]], cfg_mundo: ConfigMundo,
                     cfg_grupo: ConfigGrupo | None = None, cfg: Config | None = None, cfg_sentidos: ConfigSentidos | None = None) -> Grupo:
    """Refaz o grupo do cabecalho e rejoga os eventos no mesmo relogio. `fabricas[id] = (fabrica da politica, fabrica do motor)`. O
    registro refeito tem de ser o lido (falha alto); evento desconhecido, fora do tick ou de pet que nao entrou tambem."""
    cab = registro.cabecalho
    cg = cfg_grupo or CONFIG_GRUPO_LIGADA
    if cab.get("versao") != VERSAO_REGISTRO:
        raise ValueError(f"versao do registro do grupo desconhecida: {cab.get('versao')!r}")
    if list(cab["ids"]) != list(cg.ids) or cab["layout"] != cfg_mundo.layout.nome:
        raise ValueError("o cabecalho do registro nao e o desta ConfigGrupo/ConfigMundo")
    cs = cfg_sentidos or CONFIG_SENTIDOS
    if cab.get("sentidos") != (asdict(cs) if cs.ligada else None):
        raise ValueError(f"o cabecalho do registro nao e o desta ConfigSentidos: {cab.get('sentidos')!r}")
    if set(fabricas) != set(cab["pets"]):
        raise ValueError(f"fabricas {sorted(fabricas)} para os pets {sorted(cab['pets'])}")
    cfg = cfg or CONFIG_PADRAO
    g = Grupo(cfg_mundo, cab["semente"], cg, cfg, cs)
    for e in registro.eventos:
        if e.tick != g.tick:
            raise ValueError(f"evento no tick {e.tick} com o grupo no tick {g.tick}: {e}")
        if e.tipo == "entrada":
            pet = cab["pets"][e.valor]
            fp, fm = fabricas[e.valor]
            g.entrar(e.valor, fp(cfg), fm, pet["cerebro"], pet["dono"])
        elif e.tipo == "avanco":
            g.avancar(int(e.valor))
        elif e.tipo == "acao_usuario":
            g.acao_dono(e.pet, AcaoUsuario(e.valor))
        elif e.tipo == "deixar_comida":
            g.deixar_comida(e.pet, *ler_deixar_comida(Evento(e.tick, e.tipo, e.valor)))
        elif e.tipo == "deixar_bola":
            g.deixar_bola(e.pet, *ler_deixar_bola(Evento(e.tick, e.tipo, e.valor)))
        else:
            raise ValueError(f"tipo de evento desconhecido no registro do grupo: {e.tipo!r}")
    if g.registro != registro:
        raise RegistroDivergente("o replay refez um registro do grupo diferente do lido")
    return g


# ================================================================== a vida do grupo com o dono
@dataclass(frozen=True)
class PetDoGrupo:
    """Um pet da simulacao do grupo: quando entra (tick do mundo, inicio de dia), o cerebro, o motor e o dono dele."""

    ident: str
    entrada: int
    politica_fabrica: Callable
    fabrica_motor: Callable
    dono: object                             # o dono sintetico (o DonoComLugar), um por pet, com as rngs do pet; None: sem dono
    rotulo_dono: str
    cerebro: str = ""


def simular_grupo(cfg_mundo: ConfigMundo, semente: int, pets: list[PetDoGrupo], dias: int, cfg_grupo: ConfigGrupo | None = None,
                  cfg: Config | None = None, cfg_donos: ConfigDonos | None = None, canal_classe: type | None = None,
                  cfg_sentidos: ConfigSentidos | None = None) -> Grupo:
    """O `simular_vida_mundo` do grupo (DP-7, a validacao inicial): a cada passo do dono o grupo anda o passo e, para cada pet presente
    (na ordem dos ids), o dono decide o cuidado dele pelo que ve dele, com o orcamento dele (`orcamento_por_dia` por dia vivido) e a rng
    `dono` dele (`derivar_semente("dono", semente do pet, rotulo do dono)`). Um pet so, entrando no tick 0, e o `simular_vida_mundo` de
    hoje com a semente do grupo, byte a byte."""
    cg = cfg_grupo or CONFIG_GRUPO_LIGADA
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    total = dias * TICKS_POR_DIA
    passo = cfg_donos.passo_ticks
    if total % passo or TICKS_POR_DIA % passo:
        raise ValueError("duracao ou dia nao e multiplo do passo do dono")
    if len({p.ident for p in pets}) != len(pets):
        raise ValueError("pet repetido na simulacao do grupo")
    for p in pets:
        if not 0 <= p.entrada < total:
            raise ValueError(f"o pet {p.ident} entra fora da vida do grupo: {p.entrada}")
        if type(p.entrada) is not int or p.entrada % TICKS_POR_DIA:
            # sem isto o pet nunca entrava, em silencio (o laco so o poe num passo do dono): a entrada e um tick do mundo, num inicio de dia
            raise ValueError(f"o pet {p.ident} entra num inicio de dia do mundo (multiplo de {TICKS_POR_DIA}): {p.entrada!r}")
    g = Grupo(cfg_mundo, semente, cg, cfg, cfg_sentidos)
    por_id = sorted(pets, key=lambda p: p.ident)           # G-ORDEM: a ordem da lista nao importa
    canais: dict[str, CanalMundo] = {}
    rngs: dict[str, random.Random] = {}
    passos_pet: dict[str, int] = {}
    for k in range(total // passo):
        t = k * passo
        for p in por_id:
            if p.entrada == t:
                g.entrar(p.ident, p.politica_fabrica(cfg), p.fabrica_motor, p.cerebro, p.rotulo_dono)
                if p.dono is None:                  # pet sem dono (um parceiro passivo nos testes): sem canal e sem orcamento
                    continue
                vividos = total - p.entrada
                passos_pet[p.ident] = vividos // passo
                orcamento = cg.orcamento_por_dia * vividos // TICKS_POR_DIA
                canais[p.ident] = (canal_classe or CanalMundo)(g.pet(p.ident), orcamento, cfg_donos.max_interacoes_por_passo)
                rngs[p.ident] = random.Random(derivar_semente("dono", g.sementes[p.ident], p.rotulo_dono))
        g.avancar(passo)
        for p in por_id:
            if p.ident not in canais:
                continue
            canal = canais[p.ident]
            n = (t - p.entrada) // passo
            minimo, maximo = canal.limites(n, passos_pet[p.ident])
            visao = Visao(estado=g.motores[p.ident].estado(), passo=n, passos_totais=passos_pet[p.ident], orcamento=canal.orcamento,
                          gasto=canal.gasto, minimo_obrigatorio=minimo, maximo_permitido=maximo)
            canal.aplicar(p.dono.decidir(visao, rngs[p.ident]), n, passos_pet[p.ident])
    for i, canal in canais.items():
        canal.fechar()
        g.interacoes[i] = canal.gasto
    return g
