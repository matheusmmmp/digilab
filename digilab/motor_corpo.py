"""O corpo por baixo dos drives, no motor (V2; docs/TAREFA_V2_CORPO_DRIVES.md, etapa 2 da secao 14; CD-1 a CD-10 decididas).

`MotorCorpo` e um mixin que vai na frente de um motor de hoje, por subclasse: `com_corpo(MotorComFeedback)` (mundo `padrao`),
`com_corpo(MotorAmbiente)` (`bola`), `com_corpo(MotorFrutasMundo)` (os mundos das frutas da bancada). engine.py nao muda; nenhum arquivo
das classes do meio muda.

Desligado (ConfigCorpo.ligada False, o padrao): tudo passa ao motor de baixo. Nenhum corpo, nenhuma chave nova em estado(), nenhum
campo preenchido, nenhuma rng a mais: a vida de hoje byte a byte (G2).

Ligado (secao 2), os cinco drives do Estado (fome, higiene, energia, humor, saude) passam a ser a LEITURA da quimica do `Corpo`
(digilab/corpo.py, do B), a cada tick e depois de cada estimulo:
  - o laco do tick e refeito aqui (o corpo de engine.Motor._avancar), com o `Corpo.passo` no lugar da dinamica float dos drives. O
    `state.avancar_um_tick` continua sendo chamado para o que nao e drive (o tick e o sorteio da sujeira, na mesma rng e na mesma ordem
    de hoje); os drives que ele calcula em float sao trocados pela leitura. Os efeitos por avanco das classes do meio ficam: o contador
    de eventos do MotorPersonalidade e a morte conferida do MotorEducacao;
  - cada escritor de drive da auditoria vira estimulo no corpo:
      a acao do dono (state.aplicar_acao_usuario)            -> Corpo.acao_dono, nas seis acoes de hoje
      a acao do pet (policy.efeito_da_acao_do_pet)           -> Corpo.acao_pet (o efeito float so deixa o dormindo)
      a bola do MotorAmbiente (brincar com a bola)           -> Corpo.estimulo_bola
      a fruta do MotorFrutas (nutricao e o efeito no humor)  -> Corpo.estimulo_fruta, antes do gancho `fruta_comida`
      a consequencia do mundo fisico (MotorMundo._consequencia), nesta ordem:
        o comer sem comida (MF-2)                            -> Corpo.acao_pet(acao, com_mundo=True), na decisao
        o andar                                              -> Corpo.estimulo_andar(deslocamento, custo por subunidade)
        a comida do mapa (comer ou achar)                    -> Corpo.estimulo_consumo_mundo(tipo, situacao, ConfigMundo, efeito)
        a bola do mundo                                      -> Corpo.estimulo_bola(ganho_humor_bola)
      e so depois o mundo chama `consequencia_mundo(acao, ocorrido, obs_depois)`, com o `obs.corpo` (secao 9);
  - G-BYPASS: um drive mudado por fora do corpo falha alto. Entre os passos, o Estado tem de ser a leitura; num estimulo, so os drives
    que ele mexe podem mudar no float de baixo;
  - a percepcao: antes de cada decisao, `Observacao.corpo` = `PercepcaoCorpo`, os receptores na escala S (secao 10);
  - o gancho `consequencia_corpo(acao, ocorrido, obs_depois)` (secao 9): uma chamada por decisao, sempre, logo depois dos estimulos da
    propria acao (o pet, a bola, a fruta e, com o mundo fisico, o andar e a comida do mapa) e antes do tempo e do dono; quem nao tem o
    gancho vive como hoje. Com o mundo fisico, o `consequencia_mundo` (so nas decisoes de explorar, comer e brincar, como hoje) vem antes
    dele, ja com os estimulos aplicados e o `obs.corpo`;
  - com o orgao 2 (a Vida), o estagio pelos receptores da Vida e conferido contra o de hoje (treino_stats.estagio_no_tick) a cada tick.
Etapa 6, a parte do motor (secoes 7 e 8; o contrato dos ganchos combinado com o B, dono da quimica nova):
  - `gestos`: o tapa (`AcaoUsuario.TAPA`) e o carinho viram so o estimulo do corpo (`Corpo.acao_dono`), contam como contato e gastam o
    orcamento (CD-6). O tapa vai ao cerebro por `receber_acao_dono` (o sinal direto) e nao chama o `mudanca_no_corpo` (CD-9); o
    carinho nao e repassado, e o cerebro o ve so pelo `mudanca_no_corpo(obs_antes, obs_depois)`. Sem `gestos`, o tapa falha alto
    (GestoSemChave) e o carinho e o de hoje;
  - `drives_novos`: `Corpo.atividade(nome)` (o tedio pela variedade, secao 17) uma vez por decisao de brincar ("bola" ou "brincar") ou
    explorar, depois dos estimulos da acao; com o mundo fisico, o registro do que o pet viu e quando, os `vistos_novos` no `ocorrido`
    do mundo e `Corpo.estimulo_novidade(n)` no explorar (a curiosidade, CD-8; o corpo nasce com `com_mundo`).
Com educacao, lesoes, obediencia ou uma acao de treino, falha alto (secao 2): lesao como dano de orgao e da etapa 1b. O corpo nao sorteia
nada e o cerebro nao recebe o objeto do corpo: so os receptores (G-RECEPTOR).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import CONFIG_CORPO, ConfigCorpo
from .corpo import DRIVE_DO_QUIMICO, Corpo
from .educacao import MotorEducacao
from .engine import Motor
from .events import ACOES_CORPO, ACOES_TREINO, AcaoPet, AcaoUsuario
from .obediencia import MotorPersonalidade
from .policy import Observacao, Transicao, efeito_da_acao_do_pet
from .state import avancar_um_tick
from .treino import PoliticaTreinavel
from .treino_stats import estagio_no_tick

DRIVES = ("fome", "higiene", "energia", "humor", "saude")


class ForaDoCorpo(RuntimeError):
    """G-BYPASS: com o corpo ligado, um drive do Estado mudou por fora da quimica."""


class GestoSemChave(ValueError):
    """O tapa (secao 8) num MotorCorpo sem ConfigCorpo.gestos."""


@dataclass(frozen=True)
class PercepcaoCorpo:
    """O que o pet sente do corpo (secao 10), na escala S do cerebro A. Os drives de hoje: S - div_arred(q * S, C). Os campos dos
    drives novos e dos gestos (etapa 6) ficam None ate existirem. `alimento` e `vida` nao tem receptor."""

    fome: int
    higiene: int
    energia: int
    humor: int
    saude: int
    tedio: int | None = None
    curiosidade: int | None = None
    solidao: int | None = None
    estresse: int | None = None
    dor: int | None = None
    susto: int | None = None


class MotorCorpo:
    """Mixin: vai na frente de um motor de hoje (use `com_corpo`). `cfg_corpo` liga o corpo."""

    def __init__(self, *a, cfg_corpo: ConfigCorpo | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        self.cc = cfg_corpo or CONFIG_CORPO
        if not self.cc.ligada:
            return                                   # desligado: o motor de baixo, byte a byte
        self._recusar_o_que_o_corpo_nao_cobre()
        treino = getattr(self, "treino", None)
        self._cfg_evo = treino.cfg_evo if treino is not None else None
        if self.cc.drives_novos:                      # etapa 6: a curiosidade so existe com o mundo fisico (CD-8)
            self.corpo = Corpo.de_estado(self._estado, self.cfg, self.cc, self._cfg_evo, com_mundo=self._mundo_ligado())
        else:
            self.corpo = Corpo.de_estado(self._estado, self.cfg, self.cc, self._cfg_evo)
        self._estado = self.corpo.no_estado(self._estado)
        self._estimulos: list[tuple] = []             # os estimulos da decisao em curso (para o `ocorrido`)
        self.consequencias = 0                        # quantas vezes o gancho `consequencia_corpo` foi chamado
        self.mudancas = 0                             # quantas vezes o gancho `mudanca_no_corpo` foi chamado (o carinho, com `gestos`)
        # etapa 6, secao 7: o registro do que o pet viu e quando (o id do objeto -> o ultimo tick em que o viu), so com os drives novos
        # e o mundo fisico; derivado (o replay o refaz)
        self._vistos_em: dict[int, int] | None = {} if (self.cc.drives_novos and self._mundo_ligado()) else None

    def _recusar_o_que_o_corpo_nao_cobre(self) -> None:
        """Secao 2: o corpo vale nos motores dos mundos da pesquisa, sem educacao, lesoes nem obediencia. As classes do meio so podem
        mexer no avanco nos dois pontos que o laco daqui refaz."""
        if isinstance(self, MotorPersonalidade) and not self.obediencia_desligada:
            raise ValueError("o corpo exige a obediencia desligada (secao 2)")
        if isinstance(self, MotorEducacao) and (self.ce.ligada or self.cl.ligada):
            raise ValueError("o corpo exige educacao e lesoes desligadas (secao 2; lesao como dano de orgao e da etapa 1b)")
        conhecidos = {MotorCorpo, MotorEducacao, MotorPersonalidade, Motor}
        estranhos = [c.__name__ for c in type(self).__mro__ if "_avancar" in vars(c) and c not in conhecidos]
        if estranhos:
            raise TypeError(f"classes que mexem no avanco e que o laco do corpo nao refaz: {estranhos}")

    # ------------------------------------------------------------ leituras
    def _ligado(self) -> bool:
        return self.cc.ligada

    def _mundo_ligado(self) -> bool:
        cmf = getattr(self, "cmf", None)
        return cmf is not None and cmf.ligada

    def percepcao_corpo(self) -> PercepcaoCorpo:
        return PercepcaoCorpo(**self.corpo.receptores())

    def _observacao(self) -> Observacao:
        return replace(Observacao.de_estado(self._estado), corpo=self.percepcao_corpo())

    def _drives(self) -> dict[str, float]:
        e = self._estado
        return {d: getattr(e, d) for d in DRIVES}

    def _conferir_sincronia(self, onde: str) -> None:
        """G-BYPASS: entre os passos, o Estado e a leitura da quimica."""
        leitura = self.corpo.drives()
        fora = {d: (v, leitura[d]) for d, v in self._drives().items() if v != leitura[d]}
        if fora:
            raise ForaDoCorpo(f"{onde}, tick {self._estado.tick}: drive mudado por fora do corpo {fora}")

    def _conferir_estimulo(self, onde: str, permitidos: set[str]) -> None:
        """Depois de um escritor de hoje: so os drives do estimulo podem ter mudado no float de baixo."""
        leitura = self.corpo.drives()
        fora = {d: (v, leitura[d]) for d, v in self._drives().items() if d not in permitidos and v != leitura[d]}
        if fora:
            raise ForaDoCorpo(f"{onde}, tick {self._estado.tick}: drive mudado por fora do estimulo {fora}")

    def _sincronizar(self) -> None:
        self._estado = self.corpo.no_estado(self._estado)

    # ------------------------------------------------------------ o laco do tick (o corpo de engine.Motor._avancar)
    def _avancar(self, ticks: int):
        if not self._ligado():
            return super()._avancar(ticks)
        if isinstance(self, MotorPersonalidade):
            self._n_eventos += 1                      # o MotorPersonalidade._avancar: o evento de avanco no indice dos refs
        produzidas = self._laco(ticks)
        if isinstance(self, MotorEducacao):
            self._conferir_morte(self._estado.tick)    # o MotorEducacao._avancar: a morte conferida no fim do avanco
        return produzidas

    def _laco(self, ticks: int) -> list[tuple[int, AcaoPet]]:
        produzidas: list[tuple[int, AcaoPet]] = []
        intervalo = self.cfg.intervalo_decisao_ticks
        for _ in range(ticks):
            self._conferir_sincronia("tick")
            if self._estado.tick >= self._proxima_decisao:
                self._decidir(intervalo, produzidas)
            antes = self._estado
            self.corpo.passo(antes)
            # o tick e a sujeira de hoje (a mesma rng, na mesma ordem); os drives float dele sao trocados pela leitura
            self._estado = self.corpo.no_estado(avancar_um_tick(antes, self.cfg, self._rng_ambiente))
            if self.cc.vida and self._cfg_evo is not None:
                hoje = estagio_no_tick(self._estado.tick, self._cfg_evo)
                if self.corpo.estagio() != hoje:
                    raise ForaDoCorpo(f"tick {self._estado.tick}: estagio pela Vida {self.corpo.estagio()} != o de hoje {hoje}")
        return produzidas

    def _decidir(self, intervalo: int, produzidas: list) -> None:
        obs = self._observacao()
        acao = self.politica.agir(obs, self._rng_politica)
        self._acao_atual = acao
        # o float de hoje so deixa o dormindo; os drives vem do corpo
        e = efeito_da_acao_do_pet(self._estado, acao, self.cfg, intervalo)
        self.corpo.acao_pet(acao, com_mundo=self._mundo_ligado())      # MF-2: com o mundo, o comer so da fome com comida do mapa
        self._estado = self.corpo.no_estado(e)
        self._estimulos = [("pet", acao.value)]
        self._acoes_pet.append((self._estado.tick, acao))
        produzidas.append((self._estado.tick, acao))
        self._proxima_decisao = self._estado.tick + intervalo
        usadas = self._bolas_usadas()
        self.politica.observar(Transicao(observacao=obs, acao=acao, observacao_seguinte=self._observacao(), recompensa=None))
        # a bola do MotorAmbiente escreve o humor direto, dentro do observar: vira o estimulo da bola. A conferencia vem antes do
        # estimulo: depois dele o float de baixo e a leitura podem diferir no ultimo bit, e a leitura e o que vale
        bola = self._bolas_usadas() > usadas
        self._conferir_estimulo("decisao", {"humor"} if bola else set())
        if bola:
            self.corpo.estimulo_bola(self.cb.ganho_humor_bola)
            self._estimulos.append(("bola",))
        self._sincronizar()
        if self.cc.drives_novos and not self._mundo_ligado():      # com o mundo, a atividade vem na consequencia dele
            self._atividade(acao, bola)
        gancho = getattr(self.politica, "consequencia_corpo", None)
        if gancho is not None:
            ocorrido = {"acao": acao.value, "estimulos": list(self._estimulos)}
            gancho(acao, ocorrido, self._observacao())
            self.consequencias += 1

    # ------------------------------------------------------------ o mundo fisico (MotorMundo), como estimulo
    def _consequencia(self, acao: AcaoPet):
        """A consequencia do MotorMundo escreve energia (o andar), fome e humor (a comida do mapa) e humor (a bola) em float: vira os
        estimulos do mundo, antes de o mundo montar o `obs_depois` e chamar o cerebro e o `consequencia_mundo` (secao 9). O MF-2 ja
        veio na decisao (o `acao_pet` com o mundo nao da fome ao comer; o float de baixo volta a fome de antes, o mesmo numero)."""
        if not self._ligado():
            return super()._consequencia(acao)
        self._conferir_sincronia("antes da consequencia do mundo")
        ocorrido = super()._consequencia(acao)
        if ocorrido is None:
            self._conferir_estimulo("mundo, acao sem alvo", set())
            return None
        comeu, bola = ocorrido["comeu"], ocorrido["brincou_com_bola"]
        permitidos = {"energia"} | ({"fome", "humor"} if comeu is not None else set()) | ({"humor"} if bola else set())
        self._conferir_estimulo("mundo", permitidos)
        cmf = self.cmf
        self.corpo.estimulo_andar(ocorrido["deslocamento"], cmf.custo_energia_por_subunidade)
        self._estimulos.append(("andar", ocorrido["deslocamento"]))
        if comeu is not None:
            tipo = comeu["tipo"]
            self.corpo.estimulo_consumo_mundo(tipo, comeu["situacao"], cmf, self.efeito_frutas.get(tipo, 0.0))
            self._estimulos.append(("comida", tipo, comeu["situacao"]))
        if bola:
            self.corpo.estimulo_bola(cmf.ganho_humor_bola)
            self._estimulos.append(("bola",))
        if self._vistos_em is not None:
            self._novidade(acao, ocorrido)
        if self.cc.drives_novos:
            self._atividade(acao, bola)
        self._sincronizar()
        return ocorrido

    # ------------------------------------------------------------ etapa 6: os drives novos (secao 7)
    def _atividade(self, acao: AcaoPet, bola: bool) -> None:
        """O tedio pela variedade (secao 17, DS-4): avisa ao corpo a atividade da propria acao, depois dos estimulos dela. O dono
        brincar o corpo ja sabe pelo `acao_dono(BRINCAR)`."""
        if acao is AcaoPet.BRINCAR:
            nome = "bola" if bola else "brincar"
        elif acao is AcaoPet.EXPLORAR:
            nome = "explorar"
        else:
            return
        self.corpo.atividade(nome)
        self._estimulos.append(("atividade", nome))

    def _registrar_vistos(self, vistos, tick: int) -> None:
        for v in vistos:
            self._vistos_em[v[0]] = tick

    def _novidade(self, acao: AcaoPet, ocorrido: dict) -> None:
        """Secao 7: uma novidade e um objeto dos `vistos` (comida ou bola: o resto e cenario) que o pet nao viu nas ultimas
        `janela_novidade` ticks, achado numa decisao de explorar (na percepcao depois de andar). O que ele ja via ao decidir nao conta.
        `ocorrido["vistos_novos"]` = [[id, tipo], ...] em toda decisao com alvo (vazio fora do explorar); o corpo recebe a contagem."""
        tick = self._estado.tick
        vistos = self._perceber(tick).vistos
        novos = []
        if acao is AcaoPet.EXPLORAR:
            janela = self.cc.janela_novidade
            novos = [[v[0], v[1]] for v in vistos if v[0] not in self._vistos_em or tick - self._vistos_em[v[0]] >= janela]
            self.corpo.estimulo_novidade(len(novos))
            self._estimulos.append(("novidade", len(novos)))
        ocorrido["vistos_novos"] = novos
        self._registrar_vistos(vistos, tick)

    def _antes_da_decisao(self):
        """o MotorMundo, antes de cada decisao: o que o pet ve ao decidir entra no registro de novidade"""
        p = super()._antes_da_decisao()
        if self._ligado() and self._vistos_em is not None:
            self._registrar_vistos(p.vistos, self._estado.tick)
        return p

    def _observacao_depois_mundo(self) -> Observacao:
        """o `obs_depois` do mundo com o `obs.corpo` (os receptores ja com os estimulos da propria acao)"""
        obs = super()._observacao_depois_mundo()
        return replace(obs, corpo=self.percepcao_corpo()) if self._ligado() else obs

    def _bolas_usadas(self) -> int:
        contagem = getattr(self, "contagem_bola", None)
        return 0 if contagem is None else contagem["usadas"]

    # ------------------------------------------------------------ os escritores de hoje, como estimulo
    def _comer(self, f: str, tick: int) -> None:
        """O MotorFrutas._comer escreve fome e humor em float: vira o estimulo da fruta, antes do gancho `fruta_comida` (E2)."""
        if not self._ligado():
            return super()._comer(f, tick)
        self._conferir_sincronia("antes da fruta")
        super()._comer(f, tick)
        self._conferir_estimulo("fruta", {"fome", "humor"})
        self.corpo.estimulo_fruta(self.cf.nutricao, self.efeito_humor[f])
        self._sincronizar()
        self._estimulos.append(("fruta", f))

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if not self._ligado():
            return super()._aplicar_acao_usuario(acao)
        if acao in ACOES_TREINO:
            raise ValueError(f"{acao.value} com o corpo: o treino nao tem estimulo no corpo (secao 2)")
        if acao in ACOES_CORPO and not self.cc.gestos:
            raise GestoSemChave(f"{acao.value} sem ConfigCorpo.gestos (secao 8)")
        if acao in ACOES_CORPO or (acao is AcaoUsuario.ACARICIAR and self.cc.gestos):
            self._gesto(acao)
            return
        self._conferir_sincronia(f"antes de {acao.value}")
        super()._aplicar_acao_usuario(acao)
        deltas = self.corpo.t.dono.get(acao, {})
        self._conferir_estimulo(acao.value, {DRIVE_DO_QUIMICO[q] for q in deltas})
        if deltas:
            self.corpo.acao_dono(acao)
        self._sincronizar()

    # ------------------------------------------------------------ etapa 6: os gestos (secao 8)
    def _observacao_gesto(self) -> Observacao:
        obs = self._observacao()
        return replace(obs, mundo=self._perceber(self._estado.tick)) if self._mundo_ligado() else obs

    def _gesto(self, acao: AcaoUsuario) -> None:
        """O tapa e, com `gestos`, o carinho (secao 8). Os dois contam como contato e gastam o orcamento (CD-6), como toda acao do dono;
        o efeito e so o do corpo (`acao_dono`), e o Estado e a leitura. O tapa e repassado ao cerebro por `receber_acao_dono` (o sinal
        direto) e nao chama o `mudanca_no_corpo` (CD-9). O carinho NAO e repassado: o cerebro o ve so pelo corpo, no
        `mudanca_no_corpo(obs_antes, obs_depois)`, que nao diz que gesto foi. Os efeitos das classes do meio, na ordem delas: a janela
        da educacao (desligada: so expira), o indice do evento e o vinculo do MotorPersonalidade."""
        tick = self._estado.tick
        self._conferir_sincronia(f"antes de {acao.value}")
        if isinstance(self, MotorEducacao):
            self._expirar(tick)
        ref = None
        if isinstance(self, MotorPersonalidade):
            ref = self._n_eventos
            self._n_eventos += 1
        antes = self._observacao_gesto() if acao is AcaoUsuario.ACARICIAR else None
        self._estado = replace(self._estado, tick_ultimo_cuidado=tick, total_cuidados=self._estado.total_cuidados + 1)
        self.corpo.acao_dono(acao)
        self._sincronizar()
        if acao is AcaoUsuario.TAPA and isinstance(self.politica, PoliticaTreinavel):
            self.politica.receber_acao_dono(acao, tick)
        if isinstance(self, MotorPersonalidade):
            self._depois_do_dono(acao, tick, ref)
        if acao is AcaoUsuario.ACARICIAR:
            gancho = getattr(self.politica, "mudanca_no_corpo", None)
            if gancho is not None:
                gancho(antes, self._observacao_gesto())
                self.mudancas += 1

    def estado(self) -> dict:
        d = super().estado()
        if self._ligado():
            d["corpo"] = self.corpo.para_dict()       # so com a chave: desligado, o estado() de baixo
        return d


_CLASSES: dict[type, type] = {}


def com_corpo(base: type) -> type:
    """A classe do motor `base` com o corpo na frente (`MotorCorpo` primeiro na MRO). Uma por base."""
    if not issubclass(base, Motor):
        raise TypeError(f"{base.__name__} nao e um motor")
    if base not in _CLASSES:
        _CLASSES[base] = type(f"{base.__name__}Corpo", (MotorCorpo, base), {"__module__": __name__})
    return _CLASSES[base]
