"""M-ADAPT, o adaptador cerebro-corpo-motor (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.1 e 7): o DigiBrain modular sob o `Protocol`
`Politica` (digilab/policy.py), com os ganchos que o motor procura no cerebro (`escolher_alvo`, `consequencia_mundo`,
`consequencia_corpo`, `receber_acao_dono`). Nenhuma conta propria: encaminha a Observacao aos modulos, a rng de politica so ao M-ARB, e a
consequencia ao M-AFETO, ao M-PLAST, ao M-ESTADO e ao M-MEM.

**A decisao** (`agir`): M-SENS -> M-AFETO -> M-ESTADO (o contexto) -> M-MEM (a recuperacao, com a subchave) -> M-IMPULSO (as unidades,
com o incentivo e o habito do M-PLAST) -> M-ARB (a escolha, o u e as sondas) -> M-ESTADO (a intencao escolhida; a opcao trocada vai ao
P2). A unidade escolhida e o par (comportamento, alvo): o `agir` devolve a acao, e o `escolher_alvo` o alvo dela. O reflexo do sono e uma
conta so (`Arbitragem.reflexo`), feita depois do M-AFETO e passada ao M-ESTADO e ao M-ARB. Com a subchave `intencao_suspensa` (a parte (b)
da L-2, docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 2.3), o M-ESTADO cuida da intencao suspensa antes do contexto
(`cuidar_suspensa`); as que acabam ali vao ao P2 e ao registro com as do `escolhida`, e o motivo ganha a `suspensa`. Com a subchave
`redecidir_evento` (a C3, docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md, secao 2.3), o M-ESTADO confere os eventos antes do contexto
(`eventos`, com o gesto do dono desde a decisao anterior), o M-ARB segura o candidato sem sorteio quando nao ha evento, e o motivo ganha
`segurada` e `evento`. Com a `ConfigSonoSegura` ligada (`cfg_sono`, docs/TAREFA_V3_SONO_SEGURA.md), o reflexo do sono tambem segura o
pet que esta dormindo ate a energia passar de `lambda_acordar`, salvo a fome urgente (`Arbitragem.reflexo`). Com a subchave `memoria_autobio` (a C4, M0 e M1, docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secao
3), a decisao guarda o tick do relogio do pet e o afeto de antes, e o fechamento monta o episodio completo e o entrega ao M-MEM
(`episodio_autobio`, `codificar_autobio`), com o id em `consequencia["autobio"]`; nenhuma decisao o le ainda (a M4 e etapa posterior). Na M2 e na M3, antes do `recuperar` a decisao roda o relogio, a consolidacao do dia
novo (`consolidar`) e a lembranca (`lembrar`), e o motivo ganha `lembranca` e `consolidacao`; a lembranca ainda nao entra na escolha, e o
lugar lembrado passa a valer pela soma dos sigma (MA-2). Com a `facetas_mem` (a C4, M5, secao 6.2), a consolidacao do dia novo faz as tres
facetas andarem um passo (`_mudar_facetas`, M-PERS), o M-IMPULSO soma o termo `faceta` e o motivo ganha `faceta` (os valores e as mudancas
com os ids dos episodios).

Com a subchave `passeio` (docs/TAREFA_V3_ACOES_NOVAS.md, secoes 3.1 a 3.4), o M-ESTADO cuida do passeio antes do contexto (`cuidar_passeio`, com
as urgencias, o reflexo e o gesto do dono desde a decisao anterior); o `explorar/vagar` escolhido sem urgencia vira o passeio no
`escolher_alvo` (o ponto que o motor sorteou), e nas decisoes seguintes o passeio e entregue como `Alvo.ponto`. O motivo ganha `do_passeio`
no alvo, e o fim do passeio sem credito pelo gesto traz `credito: "gesto"`. Desligada, nenhum campo novo.

Com a subchave `fala_unidades` (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1), o M-IMPULSO divide o `chamar_atencao` nas tres unidades de
fala (o conteudo so na chave da escolha, `[chamar_atencao, c, None]`); a acao entregue ao motor e o chamar de hoje, e a opcao de fala credita
a linha de H do conteudo. A consequencia da opcao de fala (o r_n que o P2 credita, o V e o E, o episodio) le o corpo de depois na
decisao seguinte, antes da acao seguinte (o adendo 1 do plano, A1.1: o intervalo contem o cuidado do dono); o mundo de depois e o de
hoje. Desligada, nenhum campo novo; ligada, nenhum campo novo no motivo (o conteudo esta na `escolha`).

**O alvo** (`escolher_alvo`): o candidato do motor do tipo (e do id) da unidade escolhida; o `u` do motor e ignorado. **A excecao unica**
(a PE-14 revista): em EXPLORAR, o lugar lembrado do M-MEM e entregue como `Alvo.ponto(x, y)`, fora da lista do motor, que o valida por
conta propria (`MotorMundo._validar_alvo`: so em EXPLORAR, coordenadas inteiras dentro do mapa). Brincar sem bola a vista nao tem alvo
(devolve None, e o padrao do motor sem bola e nenhum).

**A consequencia:** a ordem dos ganchos no motor com o mundo e o corpo e `agir`, `escolher_alvo`, `observar`, `consequencia_mundo` (so
nas acoes com alvo) e `consequencia_corpo`. A decisao guarda tudo numa pendencia e so a fecha no comeco da decisao seguinte.

**As falhas altas** (secao 4.1, o padrao do A em lobos.py:2318-2330):
  - a Observacao chega sem `corpo` ou sem `mundo`;
  - uma decisao fica sem o gancho de consequencia (o corpo e o `observar`; o do mundo nas acoes com alvo), ou o motor nao pediu o alvo
    numa acao com alvo;
  - o alvo da unidade nao esta entre os candidatos (salvo o `ponto`, so em EXPLORAR), ou o gancho chega para outra acao;
  - uma subchave desligada e o termo do modulo diferente de 0 numa decisao (ou o estado dele fora de 0).

**Os gestos do dono** (`receber_acao_dono`): o motor os entrega (o MotorComFeedback e o tapa do corpo); o M-ADAPT so os registra na
decisao seguinte. Nenhum modulo os recebe como sinal: o corpo os sente pelos receptores e o dono pesa pela consequencia no mundo, nunca
como recompensa direta (a D-B do PLANO_V2_PESQUISA, secao 3; escolha PROPOSTA da etapa 1a).

**A luta** (`receber_luta`, a ponte da luta, PE2, docs/TAREFA_V3_PONTE_LUTA.md, secoes 3.1 e 3.2; so com a `ConfigLutaMemoria` ligada e a
`memoria_autobio`): irma do `receber_acao_dono`, guarda o resumo pronto (rival, resultado, vida perdida em S, tick); na decisao seguinte o
M-SENS o entrega na Observacao (`sens["lutas"]`) e, depois da consolidacao e da lembranca, o M-MEM o guarda como episodio de origem `luta`
(rival em `outro`), se a regra de hoje o aceita. Nenhum modulo o recebe como recompensa: o V, o E, o g_apr e o M-PLAST nao andam; a
variacao do corpo (o corpo da consequencia anterior contra o da Observacao) e quem da o sigma. Desligada, nenhum campo, estado nem gancho.

**O olhar** (GOSTO_VISUAL, P1d; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 5 e 6; a subchave `olhar`, com a `ConfigOlhar` e o `GenomaVisao` do
ovo, `genoma_visao(semente)`, rng propria `visao-ovo`, ou o dado, como o genoma vazio do controle). Tres ganchos novos, que o motor com a TV
procura no cerebro (nenhum le a chave fora do pacote):
  - `ver_tela(linhas)`: o motor, antes de cada decisao, entrega as TVs a vista (id, dx, dy, d); o M-SENS faz delas as linhas da classe
    `tela` (sem o gancho na decisao, nenhuma);
  - `olhando_tela()`: o id da TV da unidade de olhar escolhida na ultima decisao, ou None. O motor so entrega o que a TV passa ao corpo
    quando o pet olha a TV desse id (e esta acordado, parado e com ela no raio da visao);
  - `agrado_tela(leituras)`: com a `agrado_no_corpo` (GV-16), o agrado do nivel lido agora (o motor chama o `estimulo_agrado_tela` do
    corpo, depois do assistir); sem ela, None.
A unidade de olhar e entregue ao motor como o OCIOSO (o pet fica parado; o metabolismo e o do ocioso, secao 4 da espec), sem alvo. Na
decisao, o termo `gosto` da unidade da TV que o pet ja olhava e mul(w_gosto, agrado - S/2), com o agrado do nivel da percepcao de agora
(0 nas outras e se ele nao olhava). Na consequencia da opcao de olhar: o canal `gosto_visual` = mul(ganho_gosto_visual, agrado - S/2) no
r (M-AFETO), com o agrado do nivel de depois contra o alvo de antes; depois a exposicao (`Sens.expor`) e o P1 da classe `tela`. O motivo
ganha `olhar` (o agrado, o inato, o gosto e as TVs a vista). Desligada, nenhum campo, estado nem gancho que funcione (os tres falham alto).

**O registro** (secao 7): cada decisao guarda o seu motivo em `motivos` (derivado, nunca no log): as unidades com os termos, os pesos, o
u, a escolha, o afeto, o estado, a memoria, as sondas e, no fechamento, a consequencia."""
from __future__ import annotations

import random
from dataclasses import dataclass

from ..config import (COMPORTAMENTO_OLHAR, CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_LUTA_MEMORIA, CONFIG_MUNDO_LIGADA, CONFIG_OLHAR,
                      CONFIG_PADRAO, CONTEUDOS_FALA, VERSAO_PET_DIGIBRAIN, Config, ConfigDigibrain, ConfigDigibrainInatos,
                      ConfigFalaUnidades, ConfigLutaMemoria, ConfigMundo, ConfigOlhar, ConfigSonoSegura)
from ..events import AcaoPet, AcaoUsuario, LutaSemChave, resumo_luta
from ..genoma_visao import GenomaVisao, genoma_visao
from ..modelo_mundo import raiz_inteira
from ..mundo import ACOES_COM_ALVO, Alvo
from ..policies.lobos import leitura_receptor
from ..policy import Observacao, Transicao
from ..protocol import derivar_semente
from ._comum import chave_json, mul
from .afeto import Afeto
from .arb import Arbitragem
from .estado import GESTOS_DO_DONO, EstadoDinamico
from .impulso import Impulso
from .mem import Memoria, episodio_autobio, episodio_luta
from .pers import FACETAS, SENTIDO, Personalidade
from .plast import Plasticidade
from .sens import COMIDAS_BOAS, Sens, classe_do_tipo


class DigibrainDesligado(RuntimeError):
    """o DigiBrain modular montado com a ConfigDigibrain desligada"""


@dataclass(frozen=True)
class Intencao:
    """a escolha do M-ARB vista pelo motor: a acao e, nas acoes com alvo, o tipo do candidato do motor, o id dele (a comida, a bola) e,
    no lugar lembrado, o ponto"""

    acao: AcaoPet
    tipo_alvo: str | None = None
    id_alvo: int | None = None
    ponto: tuple | None = None
    passeio: bool = False


@dataclass
class Modulos:
    """os modulos da DM-3, um por arquivo"""

    sens: Sens
    afeto: Afeto
    estado: EstadoDinamico
    impulso: Impulso
    mem: Memoria
    arb: Arbitragem
    plast: Plasticidade
    pers: Personalidade | None = None             # o M-PERS (a C4, M5): so com a `facetas_mem`

    def itens(self) -> tuple:
        out = (("sens", self.sens), ("afeto", self.afeto), ("estado", self.estado), ("impulso", self.impulso), ("mem", self.mem),
               ("arb", self.arb), ("plast", self.plast))
        return out if self.pers is None else out + (("pers", self.pers),)


def montar_modulos(cfg: Config, cd: ConfigDigibrain, cm: ConfigMundo, inatos: ConfigDigibrainInatos,
                   serie_e_doadora: tuple | None, semente: int | None = None, luta: bool = False,
                   cfg_fala: ConfigFalaUnidades | None = None, cfg_olhar: ConfigOlhar | None = None,
                   genoma: GenomaVisao | None = None, cfg_sono: ConfigSonoSegura | None = None) -> Modulos:
    return Modulos(sens=Sens(cfg, cm, inatos, cfg_olhar, genoma), afeto=Afeto(cfg, cd, inatos, serie_e_doadora),
                   estado=EstadoDinamico(cfg, cd, inatos), impulso=Impulso(inatos, cd, cfg_fala, cfg_olhar), mem=Memoria(cm, inatos, cd.memoria_autobio, cd.controle_mem,
                                 None if semente is None else random.Random(derivar_semente(semente, "mem_emb")),
                                 luta), arb=Arbitragem(inatos, cd.memoria_autobio, cd.facetas_mem, cfg_sono), plast=Plasticidade(cd, inatos),
                   pers=Personalidade(inatos.eta_faceta, inatos.teto_faceta, True) if cd.facetas_mem else None)


def intencao_da_unidade(unidade: dict) -> Intencao:
    acao, tipo, ident = unidade["chave"]
    if acao == COMPORTAMENTO_OLHAR:                   # o olhar (P1d): o motor o executa como o ocioso, parado e sem alvo (D-GV-P1d-1)
        return Intencao(AcaoPet.OCIOSO)
    a = AcaoPet(acao)
    if tipo == "ponto":
        return Intencao(a, "ponto", None, tuple(ident))
    if tipo == "passeio":                             # o passeio (AN-2): o ponto fixo, entregue ao motor como o lugar lembrado
        return Intencao(a, "ponto", None, tuple(ident), True)
    if a is AcaoPet.CHAMAR_ATENCAO:                   # a unidade de fala (DC3, 3.1): o conteudo fica so na chave; o mundo e o do chamar
        return Intencao(a, None, None)
    return Intencao(a, tipo, ident if tipo in ("comida", "bola") else None)


class DigiBrain:
    """o cerebro modular (a v13, DM-5), so com a ConfigDigibrain ligada"""

    nome = "digibrain"
    versao_pet = VERSAO_PET_DIGIBRAIN

    def alcance_da_memoria(self, d_max: int) -> None:
        """o alcance da memoria de lugar do M-MEM passa a ser `d_max` (a ilha grande, IG6); os `inatos` do cerebro acompanham"""
        self.m.mem.alcance(d_max)
        self.inatos = self.m.mem.p

    def mundo_deslocado(self, dx: int, dy: int, ajustar, regiao_de) -> int:
        """o gancho da ida para a ilha maior (MotorMundo._aplicar_mudar_ilha, IG4): os lugares que o M-MEM lembra andam com o mundo"""
        return self.m.mem.deslocar(dx, dy, ajustar, regiao_de)

    def __init__(self, cfg: Config | None = None, cfg_digibrain: ConfigDigibrain | None = None, cfg_mundo: ConfigMundo | None = None,
                 inatos: ConfigDigibrainInatos | None = None, serie_e_doadora: tuple | None = None,
                 semente: int | None = None, cfg_luta_memoria: ConfigLutaMemoria | None = None,
                 cfg_fala: ConfigFalaUnidades | None = None, cfg_olhar: ConfigOlhar | None = None,
                 genoma_visao_ovo: GenomaVisao | None = None, cfg_sono: ConfigSonoSegura | None = None) -> None:
        self.cd = cfg_digibrain or CONFIG_DIGIBRAIN
        if not self.cd.ligada:
            raise DigibrainDesligado("o DigiBrain modular so existe com a ConfigDigibrain ligada")
        self.cfg = cfg or CONFIG_PADRAO
        self.cm = cfg_mundo or CONFIG_MUNDO_LIGADA      # so a geometria (o raio da visao, a celula): a mesma no layout do MVP
        self.inatos = inatos or CONFIG_DIGIBRAIN_INATOS
        self.S = self.inatos.escala
        self.luta_memoria = (cfg_luta_memoria or CONFIG_LUTA_MEMORIA).ligada     # a ponte da luta (PE2)
        if self.luta_memoria and not self.cd.memoria_autobio:
            raise ValueError("luta_memoria so com a memoria_autobio (docs/TAREFA_V3_PONTE_LUTA.md, 3.2)")
        # o olhar (P1d): a ConfigOlhar e o genoma da visao do ovo (o dado, ou o da semente, rng propria `visao-ovo`), so com a subchave
        self.co: ConfigOlhar | None = None
        self.genoma_visao: GenomaVisao | None = None
        if self.cd.olhar:
            self.co = cfg_olhar or CONFIG_OLHAR
            if genoma_visao_ovo is None:
                if semente is None:
                    raise ValueError("o olhar (P1d) pede o genoma da visao: a semente do ovo ou o genoma_visao_ovo")
                genoma_visao_ovo = genoma_visao(semente, self.co)
            self.genoma_visao = genoma_visao_ovo
        elif cfg_olhar is not None or genoma_visao_ovo is not None:
            raise ValueError("a ConfigOlhar e o genoma da visao so com a subchave olhar")
        self.m = montar_modulos(self.cfg, self.cd, self.cm, self.inatos, serie_e_doadora, semente, self.luta_memoria, cfg_fala,
                                self.co, self.genoma_visao, cfg_sono=cfg_sono)
        self._telas: list | None = None               # o olhar (P1d): as TVs a vista entregues pelo motor para a decisao seguinte
        self._olhando = None                          # o id da TV da unidade de olhar da ultima decisao (None: nao olha)
        self._lutas: list[dict] = []                  # os resumos desde a decisao anterior (so com a luta_memoria)
        self._pc_antes_luta = None                    # o corpo da ultima consequencia fechada (so com a luta_memoria)
        self.k = 0
        self.motivos: list[dict] = []
        self._pendencia: dict | None = None
        self._gestos: list = []
        self.gestos = {}

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    # ------------------------------------------------------------ a decisao
    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if obs.corpo is None or obs.mundo is None:
            raise ValueError("o DigiBrain modular decide com o corpo e o mundo na Observacao (obs.corpo e obs.mundo)")
        if self._pendencia is not None:
            self._fechar(self._pendencia, obs)
            self._pendencia = None
        m, cd = self.m, self.cd
        k = self.k
        lutas, self._lutas = (self._lutas, []) if self.luta_memoria else (None, [])
        if cd.olhar:                                  # o olhar (P1d): as TVs a vista, do gancho `ver_tela` (sem ele, nenhuma)
            telas, self._telas = (self._telas or []), None
            sens = m.sens.codificar(obs, lutas if self.luta_memoria else None, telas)
        else:
            sens = m.sens.codificar(obs, lutas) if self.luta_memoria else m.sens.codificar(obs)
        receptores = m.sens.receptores
        m.plast.montar(receptores)
        afeto = m.afeto.ler(sens)
        # uma conta so, ao M-ESTADO e ao M-ARB (a L-2, secao 2.3); o sono que segura le tambem a urgencia da fome (desligado, a chamada de hoje)
        reflexo = m.arb.reflexo(sens, afeto["urgencias"]) if m.arb.sono.ligada else m.arb.reflexo(sens)
        retomadas = m.estado.retomadas
        fins_susp = m.estado.cuidar_suspensa(sens, afeto, reflexo) if cd.intencao_suspensa else []
        fins_passeio = m.estado.cuidar_passeio(afeto["urgencias"], reflexo, any(g[0] in GESTOS_DO_DONO for g in self._gestos)) if cd.passeio else []
        evento, segurar = m.estado.eventos(sens, afeto, reflexo, bool(self._gestos)) if cd.redecidir_evento else ([], None)
        ctx = m.estado.contexto(afeto["urgencias"]) if cd.passeio else m.estado.contexto()
        if cd.memoria_autobio:                        # a C4, M2 e M3: o relogio, a consolidacao do dia novo e a lembranca da decisao
            tick = m.mem.relogio(sens["minuto"])
            consolidacao = m.mem.consolidar(k)
            mudancas = self._mudar_facetas(consolidacao) if cd.facetas_mem and consolidacao is not None else []
            lembranca = m.mem.lembrar(sens)
            termo_lem = m.mem.termo_lembranca(lembranca)
            episodios_luta = self._episodios_luta(sens, afeto, tick) if self.luta_memoria else None
        memoria = m.mem.recuperar(sens, afeto) if cd.m_mem else None
        gosto, olhar = None, None
        if cd.olhar:                                  # o olhar (P1d): o agrado do que o pet ja olhava, no termo `gosto` da unidade dela
            gosto, olhar = self._gosto_da_decisao(sens)
        unidades, z = m.impulso.unidades(
            sens, afeto, ctx, m.plast, memoria, m.afeto.drives(receptores),
            None if not cd.memoria_autobio or termo_lem is None else (termo_lem, m.mem.casa),
            (dict(m.pers.valores), m.mem.classes_com_positivo()) if cd.facetas_mem else None, **({} if gosto is None else {"gosto": gosto}))
        esc = m.arb.escolher(unidades, afeto, sens, rng, reflexo, segurar)  # a rng de politica vai so ao M-ARB
        self._conferir_desligadas(unidades)
        unidade = esc["unidade"]
        fins = fins_susp + fins_passeio + m.estado.escolhida(unidade, z, afeto["g_apr"], k, reflexo)
        if cd.redecidir_evento:                       # a C3: o candidato fora da lista (ou com peso 0) e o E-FIM (RE-2)
            evento = evento + (["E-FIM"] if esc["fora"] else [])
            m.estado.registrar_redecisao(unidade["chave"], esc["segurada"], reflexo, evento)
        creditos = _creditar(m.plast, fins, cd)
        if cd.credito_corrida:                        # a C2: a corrida que a troca de comportamento fechou, ao P2 uma vez so
            fechadas = m.estado.corridas_fechadas
            corridas = [{"b": c["b"], "inicio": c["inicio"], "n": c["n"], "r": c["r"]} for c in fechadas]
            creditos += [x for x in (m.plast.creditar(c) for c in fechadas) if x is not None]
        intencao = intencao_da_unidade(unidade)
        urg = afeto["urgencias"]
        self.motivos.append({
            "k": k, "acao": intencao.acao.value, "escolha": chave_json(unidade["chave"]), "tipo_escolha": unidade["tipo"],
            "reflexo": esc["reflexo"],
            "nada_a_fazer": esc["nada_a_fazer"], "u": esc["u"],
            "unidades": [{"chave": chave_json(x["chave"]), "termos": x["termos"], "a": x["a"], "w": w}
                         for x, w in zip(unidades, esc["pesos"])],
            "afeto": {"urgencias": urg, "V": afeto["V"], "E": afeto["E"], "e_usada": afeto["e_usada"], "g_apr": afeto["g_apr"],
                      "g_exp": afeto["g_exp"]},
            "estado": {"I": chave_json(ctx["I"]), "C": ctx["C"], "n_sp": ctx["n_sp"], "F": ctx["F"]},
            "memoria": None if memoria is None else {"pista": memoria["pista"], "recuperado": memoria["recuperado"],
                                                     "lugar": memoria["lugar"], "valor": memoria["valor"]},
            "sondas": esc["sondas"],
            "falta_fome": sens["falta"].get("fome"),
            "contexto": {"drive": max(sorted(urg), key=lambda r: urg[r]) if urg else None,
                         "comida_vista": sens["conjuncoes"]["comida_vista"] > 0, "noite": sens["contexto"]["noite"] > 0},
            "fins": _registrados(fins), "creditos": creditos, "gestos": self._gestos,
            "consequencia": None})
        entregue = [_fim(f) for f in fins if not f.get("registro", True)]
        if entregue:                                  # a busca guardada (DX-4), entregue sem a opcao composta: so com a subchave
            self.motivos[-1]["busca_entregue"] = entregue
        if cd.memoria_autobio:                        # a C4, M2 e M3: desligada, nenhum campo novo
            self.motivos[-1]["lembranca"] = {**lembranca, "L": None if termo_lem is None else termo_lem["L"],
                                             "unidades": [] if termo_lem is None else
                                             [chave_json(x["chave"]) for x in unidades if m.mem.casa(termo_lem, x)]}
            self.motivos[-1]["consolidacao"] = consolidacao
        if self.luta_memoria:                         # a ponte da luta (PE2): desligada, nenhum campo novo
            self.motivos[-1]["lutas"] = episodios_luta
        if cd.facetas_mem:                            # a C4, M5: desligada, nenhum campo novo
            self.motivos[-1]["faceta"] = {"valores": dict(m.pers.valores), "mudancas": mudancas}
        if cd.credito_corrida:                        # a C2: desligada, nenhum campo novo
            self.motivos[-1]["corridas"] = corridas
        if cd.intencao_suspensa:                      # a L-2: a suspensa ao fim da decisao e a retomada (desligada, nenhum campo novo)
            self.motivos[-1]["suspensa"] = m.estado.suspensa_resumo()
            self.motivos[-1]["retomou"] = m.estado.retomadas > retomadas
        if cd.redecidir_evento:                       # a C3: desligada, nenhum campo novo
            self.motivos[-1]["segurada"] = esc["segurada"]
            self.motivos[-1]["evento"] = evento
        if cd.olhar:                                  # o olhar (P1d): desligada, nenhum campo novo
            self._olhando = unidade["chave"][2] if unidade["chave"][0] == COMPORTAMENTO_OLHAR else None
            self.motivos[-1]["olhar"] = {**olhar, "olha": self._olhando}
        self._pendencia = {"k": k, "intencao": intencao, "unidade": unidade, "sens": sens, "g_apr": afeto["g_apr"], "pediu": False,
                           "alvo": None, "corpo": None, "transicao": None, "mundo": None}
        if cd.memoria_autobio:                        # a C4: o que o episodio completo le no fechamento
            self._pendencia.update({"tick": tick, "afeto": {"V": afeto["V"], "E": afeto["E"]},
                                    "gestos": self._gestos})
        self._gestos = []
        self.k += 1
        return intencao.acao

    # ------------------------------------------------------------ o olhar (P1d, so com a subchave `olhar`)
    def _gosto_da_decisao(self, sens: dict) -> tuple[dict, dict]:
        """o termo `gosto` da unidade da TV que o pet olhava na decisao anterior (se ela ainda esta a vista e o corpo le a tela): mul(w_gosto,
        agrado - S/2), com o agrado do nivel da percepcao de agora; e o resumo para o motivo"""
        S = self.S
        niveis = sens["tela_niveis"]
        a = a_inato = None
        gosto = {}
        visivel = any(o["id"] == self._olhando for o in sens["telas"])
        if self._olhando is not None and visivel and niveis is not None:
            a, a_inato = self.m.sens.agrado(niveis), self.m.sens.agrado_inato(niveis)
            gosto[self._olhando] = mul(self.co.w_gosto, a - S // 2, S)
        return gosto, {"telas": [o["id"] for o in sens["telas"]], "olhava": self._olhando, "agrado": a, "agrado_inato": a_inato,
                       "gosto": gosto.get(self._olhando)}

    def _exigir_olhar(self, gancho: str) -> ConfigOlhar:
        if not self.cd.olhar:
            raise RuntimeError(f"{gancho}: a TV com o DigiBrain modular exige a subchave olhar (GOSTO_VISUAL, P1d)")
        return self.co

    def ver_tela(self, linhas: list) -> None:
        """o motor, antes da decisao: as TVs a vista, (id, dx, dy, d) inteiros (validadas no M-SENS). Duas vezes sem decisao falha alto"""
        self._exigir_olhar("ver_tela")
        if self._telas is not None:
            raise RuntimeError("ver_tela duas vezes antes da mesma decisao")
        if type(linhas) is not list:
            raise TypeError(f"ver_tela recebe a lista das TVs a vista: {linhas!r}")
        self._telas = [tuple(x) for x in linhas]

    def olhando_tela(self):
        """o id da TV que o pet olha (a unidade de olhar da ultima decisao), ou None"""
        self._exigir_olhar("olhando_tela")
        return self._olhando

    def agrado_tela(self, leituras: dict) -> int | None:
        """GV-16, com a `agrado_no_corpo`: o agrado do nivel lido agora (os receptores da tela, `tela_<canal>`, na escala S), quando o pet
        olha; sem ela, ou sem olhar, None"""
        co = self._exigir_olhar("agrado_tela")
        if not co.agrado_no_corpo or self._olhando is None:
            return None
        return self.m.sens.agrado({c: leituras[f"tela_{c}"] for c in self.m.sens.otimo})

    def _episodios_luta(self, sens: dict, afeto: dict, tick: int) -> list[dict]:
        """a ponte da luta (PE2): cada resumo da Observacao vira, se a regra de hoje o aceita, um episodio de origem `luta`. O corpo de antes
        e o da ultima consequencia fechada (sem ela, a luta nao tem antes e o corpo de depois e o de antes); o V e o E nao andam. Devolve
        os resumos com o id do episodio (ou None)"""
        m, out = self.m, []
        for resumo in sens["lutas"]:
            recs = m.sens.receptores
            antes = self._pc_antes_luta if self._pc_antes_luta is not None else sens["pc"]
            cons = m.afeto.sigma_luta(antes, sens["pc"], recs)
            l0 = [leitura_receptor(antes, r, self.S) for r in recs]
            l1 = [sens["leitura"][r] for r in recs]
            ep = episodio_luta(sens, recs, l0, l1, {"V": afeto["V"], "E": afeto["E"]}, cons, resumo, self.k, tick, self.inatos)
            out.append({**resumo, "episodio": None if ep is None else m.mem.codificar_autobio(ep)})
        return out

    def _mudar_facetas(self, consolidacao: dict) -> list[dict]:
        """a M5 (6.2): na consolidacao diaria, cada faceta anda um passo `eta_faceta` no sentido da soma dos sigma da evidencia (zero se a
        soma for 0), com os ids dos episodios; devolve as mudancas registradas"""
        m = self.m
        out = []
        for nome in FACETAS:
            evidencia = m.mem.evidencia_faceta(nome)
            soma = sum(s for _, s in evidencia)
            passo = SENTIDO[nome] * ((soma > 0) - (soma < 0)) * self.inatos.eta_faceta
            reg = m.pers.mudar_faceta(nome, passo, [i for i, _ in evidencia], consolidacao["dia"]) if passo else None
            if reg is not None:
                out.append({**reg, "soma": soma})
        return out

    def escolher_alvo(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        p = self._pendente(acao, "escolher_alvo")
        if p["pediu"]:
            raise RuntimeError(f"escolher_alvo duas vezes na mesma decisao ({acao.value})")
        p["pediu"] = True
        it = p["intencao"]
        if it.tipo_alvo is None:
            if acao is AcaoPet.BRINCAR and not any(c.tipo == "bola" for c in candidatos):
                return None                                         # brincar sem bola a vista: sem alvo
            raise ValueError(f"a intencao de {acao.value} chegou sem objeto, e o motor pede um alvo")
        if it.tipo_alvo == "ponto":
            if acao is not AcaoPet.EXPLORAR:                        # pragma: no cover - so o explorar tem a unidade do lugar
                raise ValueError(f"o lugar lembrado (Alvo.ponto) so em EXPLORAR, nao em {acao.value}")
            alvo = Alvo.ponto(*it.ponto)
            self.motivos[-1]["alvo"] = {**alvo.para_dict(), "do_mem": not it.passeio}
            if self.cd.passeio:
                self.motivos[-1]["alvo"]["do_passeio"] = it.passeio
            p["alvo"] = alvo
            return alvo
        alvo = next((c for c in candidatos if c.tipo == it.tipo_alvo and (it.id_alvo is None or c.id == it.id_alvo)), None)
        if alvo is None:
            raise ValueError(f"o alvo da intencao ({it.tipo_alvo}, {it.id_alvo}) nao esta entre os candidatos do motor: "
                             f"{[(c.tipo, c.id) for c in candidatos]}")
        self.motivos[-1]["alvo"] = {**alvo.para_dict(), "do_mem": False}
        if self.cd.passeio:                           # o vagar escolhido sem urgencia vira o passeio, com o ponto que o motor sorteou
            nova = None
            if p["unidade"]["chave"][:2] == ("explorar", "vagar"):
                x, y = p["sens"]["pos"]
                d = raiz_inteira((alvo.x - x) * (alvo.x - x) + (alvo.y - y) * (alvo.y - y))
                nova = self.m.estado.abrir_passeio((alvo.x, alvo.y), d)
                if nova is not None:
                    p["unidade"] = {**p["unidade"], "chave": nova, "d": d}
            self.motivos[-1]["alvo"]["do_passeio"] = nova is not None
        p["alvo"] = alvo
        return alvo

    # ------------------------------------------------------------ a consequencia (guardada; vai aos modulos na decisao seguinte)
    def consequencia_corpo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        p = self._pendente(acao, "consequencia_corpo")
        if p["corpo"] is not None:
            raise RuntimeError("consequencia_corpo duas vezes na mesma decisao")
        p["corpo"] = (ocorrido, obs_depois)

    def observar(self, transicao: Transicao) -> None:
        p = self._pendente(transicao.acao, "observar")
        if p["transicao"] is not None:
            raise RuntimeError("observar duas vezes na mesma decisao")
        p["transicao"] = transicao

    def consequencia_mundo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        p = self._pendente(acao, "consequencia_mundo")
        if p["mundo"] is not None:
            raise RuntimeError("consequencia_mundo duas vezes na mesma decisao")
        p["mundo"] = (ocorrido, obs_depois)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """o gesto do dono, so registrado (a docstring do modulo)"""
        self._gestos.append([acao.value, tick])
        self.gestos[acao.value] = self.gestos.get(acao.value, 0) + 1

    def receber_luta(self, rival: str, resultado: int, vida_perdida_s: int, tick: int) -> None:
        """o resumo pronto da luta (ponte da luta, PE2), so guardado ate a decisao seguinte (a docstring do modulo). Sem a chave, falha alto"""
        if not self.luta_memoria:
            raise LutaSemChave("receber_luta exige a ConfigLutaMemoria ligada (luta_memoria; ponte da luta, PE2)")
        resumo_luta(tick, rival, resultado, vida_perdida_s)       # a validacao do evento (rival, resultado, vida perdida)
        self._lutas.append({"rival": rival, "resultado": resultado, "vida_perdida_s": vida_perdida_s, "tick": tick})

    def estado_interno(self) -> dict:
        out = {"nome": self.nome, "versao_pet": self.versao_pet, "k": self.k, "pendente": self._pendencia is not None,
               "gestos": dict(sorted(self.gestos.items())), "modulos": {nome: mod.estado_interno() for nome, mod in self.m.itens()
                                                                         if hasattr(mod, "estado_interno")},
               "motivos": self.motivos}
        if self.cd.olhar:                             # o olhar (P1d): desligada, o estado e o de hoje, byte a byte
            out["olhar"] = {"olhando": self._olhando, "genoma_visao": self.genoma_visao.para_dict()}
        return out

    # ------------------------------------------------------------ a pendencia
    def _pendente(self, acao: AcaoPet, gancho: str) -> dict:
        p = self._pendencia
        if p is None:
            raise RuntimeError(f"{gancho} sem decisao pendente")
        if p["intencao"].acao is not acao:
            raise RuntimeError(f"{gancho} de {acao.value} na decisao de {p['intencao'].acao.value}")
        return p

    def _conferir_desligadas(self, unidades: list[dict]) -> None:
        """com uma subchave desligada, o termo do modulo e 0 em toda unidade e o estado dele fica em 0 (falha alto)"""
        cd, m = self.cd, self.m
        for termo, ligada in (("incentivo", cd.p1), ("habito", cd.p2), ("memoria", cd.m_mem), ("persistencia", cd.persistencia)):
            if not ligada and any(x["termos"][termo] != 0 for x in unidades):
                raise RuntimeError(f"a subchave do termo {termo!r} esta desligada e o termo nao e 0")
        if not cd.p1 and not m.plast.desfecho_zero():
            raise RuntimeError("sem o P1, o desfecho e o andar ficam em 0")
        if not cd.p2 and not m.plast.habito_zero():
            raise RuntimeError("sem o P2, o habito fica em 0")
        if not cd.m_mem and m.mem.episodios:
            raise RuntimeError("sem o M-MEM, a memoria fica vazia")
        if not cd.memoria_autobio and m.mem.autobio:
            raise RuntimeError("sem a memoria_autobio, o M-MEM nao tem a recente")
        if not cd.passeio and (m.estado.passeios or any(x["chave"][1] == "passeio" for x in unidades)):
            raise RuntimeError("sem o passeio, o M-ESTADO nao abre passeio")
        if not cd.olhar and any(x["acao"] == COMPORTAMENTO_OLHAR or "gosto" in x["termos"] for x in unidades):
            raise RuntimeError("sem a subchave olhar, nenhuma unidade de olhar nem termo gosto")
        fala = [x["chave"][1] for x in unidades if x["acao"] == "chamar_atencao"]
        if fala != (list(CONTEUDOS_FALA) if cd.fala_unidades else [None]):
            raise RuntimeError(f"as unidades do chamar {fala} nao sao as da fala_unidades {'ligada' if cd.fala_unidades else 'desligada'}")

    def _fechar(self, p: dict, obs_seguinte: Observacao) -> None:
        """a consequencia da decisao anterior aos modulos. Com a `fala_unidades` (o adendo 1 do plano da DC3, A1.1), a opcao de fala (as
        tres unidades do chamar) le o corpo de depois na percepcao da decisao seguinte (`obs_seguinte`, antes da acao seguinte): o
        intervalo contem o passo inteiro, com o cuidado do dono. As outras opcoes, e o chamar desligada a subchave, leem o corpo do tick
        da acao, como hoje. A ultima decisao da vida nao tem decisao seguinte e fica sem fechar, como toda ultima decisao de hoje."""
        it, m, S = p["intencao"], self.m, self.S
        acao = it.acao
        if p["corpo"] is None or p["transicao"] is None:
            raise RuntimeError(f"a decisao de {acao.value} ficou sem o gancho de consequencia (o corpo e o observar)")
        com_alvo = acao in ACOES_COM_ALVO
        if com_alvo and not p["pediu"]:
            raise RuntimeError(f"a decisao de {acao.value} tinha alvo, e o motor nao pediu o alvo")
        if com_alvo and p["mundo"] is None:
            raise RuntimeError(f"a decisao de {acao.value} ficou sem o consequencia_mundo")
        pc0 = p["sens"]["pc"]
        pc1 = p["corpo"][1].corpo
        if self.cd.fala_unidades and acao is AcaoPet.CHAMAR_ATENCAO:     # A1.1: a fala ate a decisao seguinte
            if p["unidade"]["chave"][1] not in CONTEUDOS_FALA:
                raise RuntimeError(f"a fala da decisao {p['k']} sem conteudo com a fala_unidades ligada")
            pc1 = obs_seguinte.corpo
        pm1 = p["transicao"].observacao_seguinte.mundo
        if pc1 is None or pm1 is None:
            raise RuntimeError("a consequencia sem o corpo ou sem o mundo de depois")
        ocorrido = p["mundo"][0] if p["mundo"] is not None else None
        recs = m.sens.receptores
        olhou = self.cd.olhar and p["unidade"]["chave"][0] == COMPORTAMENTO_OLHAR
        gv = olhar = None
        if olhou:                                     # o olhar (P1d): o agrado do nivel de depois, contra o alvo de antes da exposicao
            niveis = m.sens.niveis_tela(pc1)
            if niveis is not None:
                a = m.sens.agrado(niveis)
                gv = mul(self.co.ganho_gosto_visual, a - S // 2, S)
                olhar = {"agrado": a, "gosto_visual": gv}
        cons = m.afeto.consequencia(pc0, pc1, recs, gv) if gv is not None else m.afeto.consequencia(pc0, pc1, recs)
        l0 = [leitura_receptor(pc0, r, S) for r in recs]
        l1 = [leitura_receptor(pc1, r, S) for r in recs]
        if olhar is not None:
            m.sens.expor(niveis)                      # a exposicao, so quando o pet olhou (o alvo anda para o nivel visto)
            olhar["desloc"] = dict(m.sens.desloc)
        pos0, pos1 = p["sens"]["pos"], (pm1.x, pm1.y)
        comeu = None if ocorrido is None else ocorrido["comeu"]
        classe_comida = None if comeu is None else ("podre" if comeu["situacao"] == "podre" else comeu["tipo"])
        p1 = None
        if acao is AcaoPet.COMER:
            p1 = m.plast.consequencia_p1("comer", classe_comida if comeu is not None and comeu["como"] == "comer" else None, l0, l1,
                                         pos0, pos1, p["g_apr"])
        elif acao is AcaoPet.BRINCAR:
            p1 = m.plast.consequencia_p1("brincar", "bola" if ocorrido["brincou_com_bola"] else None, l0, l1, pos0, pos1, p["g_apr"])
        elif olhou:                                   # o olhar (P1d): o desfecho da classe `tela` (o quanto olhar muda cada receptor)
            p1 = m.plast.consequencia_olhar(l0, l1, p["g_apr"])
        chave = p["unidade"]["chave"]
        visto, d = True, None
        if chave[1] in ("comida", "bola"):
            alvo = next((v for v in pm1.vistos if v[0] == chave[2]), None)
            visto, d = alvo is not None, None if alvo is None else alvo[4]
        elif chave[1] in ("ponto", "passeio"):
            px, py = chave[2]
            d = raiz_inteira((px - pos1[0]) * (px - pos1[0]) + (py - pos1[1]) * (py - pos1[1]))
        fins = m.estado.consequencia(cons["r_n"], ocorrido, {
            "visto": visto, "d": d, "ha_cheiro": pm1.direcao_cheiro != 0,
            "comida_boa_vista": any(classe_do_tipo(v[1]) in COMIDAS_BOAS for v in pm1.vistos)})
        creditos = _creditar(m.plast, fins, self.cd)
        episodio = None
        if self.cd.m_mem:
            base = {"decisao": p["k"], "regiao": pm1.regiao, "delta": dict(zip(recs, [b - a for a, b in zip(l0, l1)])), "r": cons["r"],
                    "r_n": cons["r_n"], "hora": p["sens"]["minuto"], "fome_antes": p["sens"]["falta"].get("fome")}
            if comeu is not None:
                episodio = m.mem.codificar({**base, "ponto": pos1, "classe": classe_comida, "origem": "consumo"})
            elif chave[1] == "ponto" and ocorrido["chegou"]:
                episodio = m.mem.codificar({**base, "ponto": chave[2], "classe": "nao_havia", "origem": "visita", "r": 0,
                                                 "r_n": 0})
        if self.luta_memoria:                         # o corpo de antes da proxima luta (nenhum efeito nos modulos)
            self._pc_antes_luta = pc1
        autobio = None
        if self.cd.memoria_autobio:                   # a C4, M0 e M1: o episodio completo, que nenhuma decisao le ainda
            ida = next((f["r"] for f in fins if f["chave"] == chave), None) if chave[1] == "ponto" else None
            desfecho = {"comeu": classe_comida, "chegou": ocorrido is not None and ocorrido["chegou"], "r_ida": ida}
            ep = episodio_autobio(p["sens"], pm1, recs, l0, l1, p["afeto"], cons, p["gestos"], p["unidade"], desfecho, p["k"],
                                  p["tick"], self.inatos)
            autobio = None if ep is None else m.mem.codificar_autobio(ep)
        motivo = self.motivos[p["k"]]
        motivo["consequencia"] = {"r": cons["r"], "r_n": cons["r_n"], "canais": cons["canais"],
                                  "comeu": None if comeu is None else {"id": comeu["id"], "tipo": comeu["tipo"],
                                                                       "situacao": comeu["situacao"], "como": comeu["como"]},
                                  "chegou": None if ocorrido is None else ocorrido["chegou"], "p1": p1, "creditos": creditos,
                                  "episodio": episodio}
        if self.cd.memoria_autobio:                   # desligada, nenhum campo novo
            motivo["consequencia"]["autobio"] = autobio
        if self.cd.olhar:                             # o olhar (P1d): desligada, nenhum campo novo
            motivo["consequencia"]["olhar"] = olhar
        motivo["fins"] = motivo["fins"] + _registrados(fins)


def _creditar(plast: Plasticidade, fins: list[dict], cd: ConfigDigibrain | None = None) -> list[dict]:
    """as opcoes que acabaram ao P2, salvo a busca guardada no "achou" (DX-4: o credito dela segue pela opcao composta). Com a
    `credito_corrida` (C2) nenhuma opcao vai ao P2: o credito e o da corrida do comportamento, entregue pelo `agir`"""
    if cd is not None and cd.credito_corrida:
        return []
    return [c for c in (plast.creditar(f) for f in fins if f.get("credito", True)) if c is not None]


def _registrados(fins: list[dict]) -> list[dict]:
    """os fins para o registro: sem as opcoes de uma decisao e sem a busca entregue depois do "achou" (ja registrada nele)"""
    return [_fim(f) for f in fins if f["motivo"] != "unica" and f.get("registro", True)]


def _fim(f: dict) -> dict:
    """o resumo de uma opcao que acabou, para o registro (a opcao composta da DX-4 marcada)"""
    out = {"chave": chave_json(f["chave"]), "inicio": f["inicio"], "n": f["n"], "motivo": f["motivo"], "meta": f["meta"], "r": f["r"]}
    if f.get("composta"):
        out["composta"] = True
    if f.get("credito_descartado"):                   # o passeio (AN-6): so com a subchave, o gesto do dono no intervalo
        out["credito"] = f["credito_descartado"]
    if "n_susp" in f:                                 # a L-2: a intencao que ja foi suspensa (so com a subchave), para as S-1 e S-2
        out["n_susp"] = f["n_susp"]
    return out
