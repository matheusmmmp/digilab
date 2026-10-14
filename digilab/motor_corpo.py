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
O banheiro (docs/TAREFA_V2_BANHEIRO.md, secoes 2 a 4, etapa 3): com a ConfigBanheiro ligada no MotorMundo, o corpo tem de ter a
sub-chave `banheiro` (e vice-versa: a vontade sem o banheiro no mapa nao teria como cair; falha alto). O `aliviar` do mundo vira o
`Corpo.estimulo_aliviar` (a vontade a zero) e, quando a necessidade fica no chao, o `Corpo.estimulo_necessidade` (o cheiro), depois do
andar; a cada tick, `Corpo.passo(..., necessidades=n)` com as necessidades na zona do pet (`MotorMundo.necessidades_na_zona`).
Com educacao, lesoes, obediencia ou uma acao de treino, falha alto (secao 2): lesao como dano de orgao e da etapa 1b. O corpo nao sorteia
nada e o cerebro nao recebe o objeto do corpo: so os receptores (G-RECEPTOR).
Os orgaos do Olfato e da Audicao (docs/TAREFA_V2_DOIS_PETS.md, etapa 8b; docs/futuro/dois_pets.md, secao 5.6): com a `cfg_olfato` ou a
`cfg_ouvido` ligada (so com o corpo e o mundo fisico; falha alto sem eles), o corpo nasce com os orgaos e o motor entrega a ele o
estimulo de cada receptor (`Corpo.sentir`) antes de cada tick e antes de cada percepcao. O estimulo vem do gancho do lado do mundo
`_intensidades_do_orgao()` (do A: a intensidade no ponto de cada narina e de cada ouvido, um inteiro por nome de receptor, sem direcao);
o motor sem o gancho falha alto na construcao. Os receptores vao a `PercepcaoCorpo` pelos nomes de `corpo.todos_receptores_orgaos`.
A troca da digestao (rede de si, etapa 2b; RS-3): com `troca_digestao=(tick, taxa)`, no comeco do primeiro tick em ou depois de `tick`
(antes da decisao e do passo daquele tick) a `taxa_digestao` do corpo passa a `taxa`; o grafo do corpo e refeito com ela e conferido de
novo (as quatro checagens). A troca fica em `troca_digestao` (registro derivado, como a troca do mutavel: o tick, o pedido, a taxa antes e
depois) e no `estado()`; o replay a refaz pela mesma fabrica. Sem ela pedida, nada muda.
O Paladar (docs/futuro/paladar.md, secao 3.2; ConfigCorpo.paladar, so com o mundo fisico): cada comida madura comida no mapa (o comer, o
"achou e comeu") e a fruta na mao levam ao corpo o perfil do tipo (um inteiro em [0, C] por qualidade), do lado do mundo (o A, etapa 1):
no mapa, o `ocorrido["comeu"]["perfil"]`; na mao, a `ConfigPaladar` do MotorMundo (`cpal.perfis`). O corpo com o paladar exige o mundo com
o paladar (`cpal.ligada`; falha alto na construcao). A podre nao tem perfil. Os receptores `paladar_<q>` vao a `PercepcaoCorpo`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import CONFIG_CORPO, CONFIG_OLFATO, CONFIG_OUVIDO, ConfigCorpo, ConfigOlfato, ConfigOuvido
from .corpo import DRIVE_DO_QUIMICO, Corpo, grafo_do_corpo, taxas_de
from .corpo_grafo import checar
from .educacao import MotorEducacao
from .engine import Motor
from .events import ACOES_CORPO, ACOES_MAO, ACOES_TREINO, ACOES_TROCA_ARVORES, AcaoPet, AcaoUsuario
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
    vontade: int | None = None            # o banheiro (TAREFA_V2_BANHEIRO, secao 3): a concentracao
    conforto: int | None = None           # BN-6: a concentracao (o cerebro le a falta de conforto, S - leitura)
    # os orgaos do Olfato e da Audicao (dois pets, secao 5.6): r = div_arred(S e, e + K), e = max(0, I - a - limiar); uma narina (um
    # ouvido) usa o nome sem lado, duas usam _esq e _dir (corpo.todos_receptores_orgaos, conferido por teste). Desligados, None
    olfato_comida: int | None = None
    olfato_comida_esq: int | None = None
    olfato_comida_dir: int | None = None
    olfato_outro: int | None = None
    olfato_outro_esq: int | None = None
    olfato_outro_dir: int | None = None
    ouvido_comendo: int | None = None
    ouvido_comendo_esq: int | None = None
    ouvido_comendo_dir: int | None = None
    ouvido_bola: int | None = None
    ouvido_bola_esq: int | None = None
    ouvido_bola_dir: int | None = None
    ouvido_chamado: int | None = None
    ouvido_chamado_esq: int | None = None
    ouvido_chamado_dir: int | None = None
    ouvido_emburrado: int | None = None
    ouvido_emburrado_esq: int | None = None
    ouvido_emburrado_dir: int | None = None
    # o Paladar (docs/futuro/paladar.md, secao 3.2): o sabor de cada qualidade (a concentracao, div_arred(q S, C)). Desligado, None
    paladar_doce: int | None = None
    paladar_azedo: int | None = None
    paladar_amargo: int | None = None
    paladar_salgado: int | None = None


class MotorCorpo:
    """Mixin: vai na frente de um motor de hoje (use `com_corpo`). `cfg_corpo` liga o corpo."""

    def __init__(self, *a, cfg_corpo: ConfigCorpo | None = None, cfg_olfato: ConfigOlfato | None = None,
                 cfg_ouvido: ConfigOuvido | None = None, troca_digestao: tuple[int, int] | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        self.cc = cfg_corpo or CONFIG_CORPO
        self.co = cfg_olfato or CONFIG_OLFATO
        self.cv = cfg_ouvido or CONFIG_OUVIDO
        # rede de si, etapa 2b: a troca da digestao pedida (tick, taxa) e a feita (o registro derivado; None ate o tick)
        self._troca_pedida = self._conferir_troca(troca_digestao)
        self.troca_digestao: dict | None = None
        self._conferir_orgaos()
        banheiro = self._banheiro_ligado()
        if banheiro != (self.cc.ligada and self.cc.banheiro):
            raise ValueError("o banheiro no mapa (ConfigBanheiro.ligada) e a vontade no corpo (ConfigCorpo.banheiro) vao juntos "
                             f"(TAREFA_V2_BANHEIRO, secao 2): mapa {banheiro}, corpo {self.cc.ligada and self.cc.banheiro}")
        if not self.cc.ligada:
            return                                   # desligado: o motor de baixo, byte a byte
        self._recusar_o_que_o_corpo_nao_cobre()
        treino = getattr(self, "treino", None)
        self._cfg_evo = treino.cfg_evo if treino is not None else None
        if self._orgaos_ligados():                    # os orgaos: so com o mundo fisico (conferido acima)
            self.corpo = Corpo.de_estado(self._estado, self.cfg, self.cc, self._cfg_evo, com_mundo=True, cfg_olfato=self.co,
                                         cfg_ouvido=self.cv)
        elif self.cc.drives_novos or self.cc.paladar:  # etapa 6: a curiosidade so existe com o mundo fisico (CD-8); o paladar exige o mundo
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

    def _conferir_paladar(self) -> None:
        """O Paladar so com o mundo fisico e com o paladar do mundo ligado (a ConfigPaladar do MotorMundo, `cpal`, do A)."""
        if not (self.cc.ligada and self.cc.paladar):
            return
        if not self._mundo_ligado():
            raise ValueError("o Paladar le o perfil da comida do mapa: exige o mundo fisico (paladar, secao 3.1)")
        cpal = getattr(self, "cpal", None)
        if cpal is None or not cpal.ligada:
            raise ValueError("o corpo com o paladar exige o mundo com o paladar (ConfigPaladar.ligada no MotorMundo; paladar, secao 4)")

    def _perfil(self, comeu: dict) -> dict[str, int] | None:
        """O perfil do que o pet comeu no mapa: o `perfil` do `ocorrido["comeu"]` (o mundo o poe so com a ConfigPaladar ligada; None na
        podre). Com o corpo sem o paladar, nada (o corpo recusa um perfil sem a sub-chave)."""
        if not self.cc.paladar:
            return None
        if "perfil" not in comeu:
            raise RuntimeError(f"o corpo com o paladar e o consumo sem perfil do mundo: {comeu!r}")
        return comeu["perfil"]

    def _conferir_orgaos(self) -> None:
        """Os orgaos (secao 5.6 dos dois pets) so com o corpo e o mundo fisico, e com o gancho do lado do mundo que entrega o estimulo."""
        self._conferir_paladar()
        if not self._orgaos_ligados():
            return
        if not self.cc.ligada:
            raise ValueError("os orgaos do Olfato e da Audicao sao do corpo: ConfigCorpo.ligada desligada")
        if not self._mundo_ligado():
            raise ValueError("os orgaos do Olfato e da Audicao leem a intensidade num ponto do mapa: exigem o mundo fisico")
        if not callable(getattr(self, "_intensidades_do_orgao", None)):
            raise NotImplementedError("o motor nao tem `_intensidades_do_orgao`: o lado do mundo do orgao (a intensidade no ponto de "
                                      "cada narina e de cada ouvido) e do A, etapa 8b")

    def _conferir_troca(self, troca) -> tuple[int, int] | None:
        """A troca da digestao so com o corpo e a digestao ligados, um tick positivo e uma taxa inteira positiva diferente da de hoje."""
        if troca is None:
            return None
        tick, taxa = troca
        if not (self.cc.ligada and self.cc.digestao):
            raise ValueError("a troca da digestao exige o corpo com a digestao (ConfigCorpo.digestao)")
        if type(tick) is not int or tick <= 0 or type(taxa) is not int or taxa <= 0:
            raise ValueError(f"troca da digestao: tick e taxa inteiros positivos, veio {troca!r}")
        if taxa == self.cc.taxa_digestao:
            raise ValueError(f"troca da digestao para a mesma taxa ({taxa}): nao e troca")
        return tick, taxa

    def _trocar_digestao(self) -> None:
        """A troca no tick (RS-3): a ConfigCorpo do motor e do corpo com a taxa nova, o grafo refeito com ela e conferido de novo."""
        tick_pedido, nova = self._troca_pedida
        antiga = self.cc.taxa_digestao
        cc = replace(self.cc, taxa_digestao=nova)
        corpo = self.corpo
        grafo = grafo_do_corpo(corpo.cfg, cc, taxas_de(corpo.cfg, cc), corpo.com_mundo, corpo.co, corpo.cv)
        if grafo.nomes != corpo.quimicos:             # pragma: no cover - a taxa nao muda os quimicos
            raise RuntimeError("a troca da digestao mudou os quimicos do corpo")
        corpo.cc, corpo.t, corpo.grafo, corpo.relato_grafo = cc, taxas_de(corpo.cfg, cc), grafo, checar(grafo)
        self.cc = cc
        self.troca_digestao = {"tick": self._estado.tick, "tick_pedido": tick_pedido, "de": antiga, "para": nova}

    def _orgaos_ligados(self) -> bool:
        return self.co.ligada or self.cv.ligada

    def _sentir(self) -> None:
        """O estimulo de cada receptor de orgao, do lado do mundo, entregue ao corpo (antes de cada tick e de cada percepcao)."""
        if self.cc.ligada and self._orgaos_ligados():
            self.corpo.sentir(self._intensidades_do_orgao())

    # ------------------------------------------------------------ leituras
    def _ligado(self) -> bool:
        return self.cc.ligada

    def _mundo_ligado(self) -> bool:
        cmf = getattr(self, "cmf", None)
        return cmf is not None and cmf.ligada

    def _banheiro_ligado(self) -> bool:
        cbh = getattr(self, "cbh", None)
        return self._mundo_ligado() and cbh is not None and cbh.ligada

    def percepcao_corpo(self) -> PercepcaoCorpo:
        self._sentir()                                # os orgaos: o estimulo de agora, no lugar de agora
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

    def _um_tick(self) -> None:
        """Um tick do laco, para o grupo (digilab/grupo.py) intercalar os pets; o `_abrir_avanco` e o `_fechar_avanco` do MotorMundo
        fazem o resto do `_avancar` acima (o indice do evento e a morte)."""
        if not self._ligado():
            super()._um_tick()
            return
        self._laco(1)

    def _laco(self, ticks: int) -> list[tuple[int, AcaoPet]]:
        produzidas: list[tuple[int, AcaoPet]] = []
        intervalo = self.cfg.intervalo_decisao_ticks
        for _ in range(ticks):
            self._conferir_sincronia("tick")
            if self._troca_pedida is not None and self.troca_digestao is None and self._estado.tick >= self._troca_pedida[0]:
                self._trocar_digestao()               # rede de si, etapa 2b: antes da decisao e do passo do tick
            if self._estado.tick >= self._proxima_decisao:
                self._decidir(intervalo, produzidas)
            antes = self._estado
            self._sentir()                            # os orgaos: o estimulo deste tick (a adaptacao anda para ele no passo)
            if self.cc.banheiro:
                self.corpo.passo(antes, necessidades=self.necessidades_na_zona())   # o banheiro: as necessidades na zona do pet
            else:
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
            self.corpo.estimulo_consumo_mundo(tipo, comeu["situacao"], cmf, self.efeito_frutas.get(tipo, 0.0),
                                              perfil=self._perfil(comeu))
            self._estimulos.append(("comida", tipo, comeu["situacao"]))
        if bola:
            self.corpo.estimulo_bola(cmf.ganho_humor_bola)
            self._estimulos.append(("bola",))
        alivio = ocorrido.get("alivio")
        if alivio is not None:
            # o banheiro (secao 3): a vontade a zero e, se a necessidade ficou no chao (sem o limpador, ou fora do banheiro), o cheiro
            self.corpo.estimulo_aliviar()
            self._estimulos.append(("aliviar", alivio["dentro"]))
            if not alivio["recolhido"]:
                self.corpo.estimulo_necessidade()
                self._estimulos.append(("necessidade",))
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
        if acao in ACOES_MAO or acao in ACOES_TROCA_ARVORES:
            # o J5 (TAREFA_V2_PET_QUE_PENSA, secao 2.3): a fruta na mao vira o estimulo da fruta madura (`_estimulo_mao`), e a troca de
            # tipo nao toca o corpo. Os dois sao do MotorMundo, que confere a chave
            self._conferir_sincronia(f"antes de {acao.value}")
            super()._aplicar_acao_usuario(acao)
            self._conferir_sincronia(f"depois de {acao.value}")
            return
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
        # os drives que a acao de hoje muda (o combustivel do metabolismo nao e drive: so o corpo o tem)
        self._conferir_estimulo(acao.value, {DRIVE_DO_QUIMICO[q] for q in deltas if q in DRIVE_DO_QUIMICO})
        if deltas:
            self.corpo.acao_dono(acao)
        self._sincronizar()

    def _estimulo_mao(self, f: str) -> None:
        """O J5: a fruta na mao escreve fome e humor em float (a conta da fruta madura do mundo): vira o estimulo da fruta madura do mapa,
        antes de o motor montar a observacao de depois para o gancho `fruta_na_mao`."""
        if not self._ligado():
            return super()._estimulo_mao(f)
        self._conferir_estimulo("fruta na mao", {"fome", "humor"})
        perfil = dict(self.cpal.perfis[f]) if self.cc.paladar else None      # a mao: o perfil do tipo, da ConfigPaladar do mundo
        self.corpo.estimulo_consumo_mundo(f, "madura", self.cmf, self.efeito_frutas[f], perfil=perfil)
        self._sincronizar()

    # ------------------------------------------------------------ etapa 6: os gestos (secao 8)
    def _observacao_gesto(self) -> Observacao:
        obs = self._observacao()
        return replace(obs, mundo=self._perceber(self._estado.tick), social=self.percepcao_social()) if self._mundo_ligado() else obs

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
        if self._troca_pedida is not None:
            d["troca_digestao"] = None if self.troca_digestao is None else dict(self.troca_digestao)
        return d


_CLASSES: dict[type, type] = {}


def com_corpo(base: type) -> type:
    """A classe do motor `base` com o corpo na frente (`MotorCorpo` primeiro na MRO). Uma por base."""
    if not issubclass(base, Motor):
        raise TypeError(f"{base.__name__} nao e um motor")
    if base not in _CLASSES:
        _CLASSES[base] = type(f"{base.__name__}Corpo", (MotorCorpo, base), {"__module__": __name__})
    return _CLASSES[base]
