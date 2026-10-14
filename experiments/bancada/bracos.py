"""A bancada da V2, módulo `bracos`.

Os sinais e filtros, os pontos do aprendiz, os braços, os nós pendentes, a montagem e a PoliticaDoBraco.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, replace

from digilab.config import CONFIG_CONSEQUENCIA, CONFIG_LOBOS_APRENDIZ, ConfigConsequencia, ConfigLobos
from digilab.events import ACOES_PET_HOJE, ACOES_INFORMACAO, ACOES_PEDIDO, FRUTAS, AcaoUsuario
from digilab.policies.lobos import desarranjo_n6 as desarranjo_dos_lobos
from digilab.policies.lobos import sinal_homeostatico
from digilab.policies.lobos import INDICE_HUMOR
from digilab.protocol import derivar_semente

from .mundos import EVENTOS_DO_MUNDO


ACOES = tuple(a.value for a in ACOES_PET_HOJE)
SINAIS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})
# pontos nomeados do aprendiz: campos trocados sobre o CONFIG_LOBOS_APRENDIZ (decisao R1, 2026-10-05). Um ponto novo entra aqui, com a
# fonte; os de antes nao mudam.
PONTOS_APRENDIZ = {
    "L1": {},                                   # passo 512, teto 1024 = 1*S: o ponto calibrado da L1 (o padrao de sempre)
    "T3": {"teto": 16 * 2 ** CONFIG_LOBOS_APRENDIZ.bits_ponto_fixo},   # R1: teto 16*S, sem traco (REVISAO_APRENDIZ, secao 3)
}
PONTO_PADRAO = "L1"                             # sem o campo "ponto": as runs antigas, byte a byte
PONTO_N5_EXPERIMENTO = "T3"                     # o ponto de partida do N5 e do experimento maior (R1)
CEREBROS = ("lobos", "instinto")
INFORMACOES = frozenset(a.value for a in ACOES_INFORMACAO)
PEDIDOS = frozenset(a.value for a in ACOES_PEDIDO)        # N7: "deixe a fruta X" (o pedido do dono, N7-MUNDO)
# corpo (etapa 6): os gestos do dono no registro, o tapa e o carinho (o que o DonoComGestos poe no lugar da bronca e do elogio)
GESTOS = frozenset({AcaoUsuario.TAPA.value, AcaoUsuario.ACARICIAR.value})
SINAIS_DO_DONO = SINAIS | {AcaoUsuario.TAPA.value}       # o que o dono manda direto ao aprendiz: o elogio, a bronca e o tapa
FILTROS = {"nenhum": frozenset(), "sem_sinais": SINAIS,
           "sem_sinais_sem_carinho": SINAIS | {AcaoUsuario.ACARICIAR.value},
           # N5 (plano, secao 4): o "so cuidado" do P2 tira os sinais de ensino E a informacao; as ofertas ficam. N7 (plano, secao 4.2):
           # o "so cuidado" do P3+ped tira tambem os pedidos; as broncas do pedido sao `repreender` e saem com os sinais
           "sem_informacao": INFORMACOES, "sem_ensino": SINAIS | INFORMACOES | PEDIDOS,
           "sem_ensino_sem_carinho": SINAIS | INFORMACOES | PEDIDOS | {AcaoUsuario.ACARICIAR.value},
           # N7: o controle do P0+ped (o P0 no registro dele sem os pedidos; os sinais do dono ficam) e o nome do plano para o so cuidado
           "sem_pedido": PEDIDOS, "sem_ensino_sem_pedido": SINAIS | INFORMACOES | PEDIDOS,
           # corpo (TAREFA_V2_CORPO_DRIVES, secao 14, etapa 8): o acoplado sem os gestos do dono, o tapa e o carinho; o resto fica
           "sem_gestos": GESTOS}
# o que entra pelo canal do mundo, fora do orcamento do dono: os eventos do mundo e a informacao do dono (B2; plano do N5, secao 2).
# A informacao NAO e evento do mundo: o "so cuidado" a tira (FILTROS); o mundo (bola, ofertas) nunca sai.
FORA_DO_ORCAMENTO = EVENTOS_DO_MUNDO | INFORMACOES | PEDIDOS     # N7: os pedidos tambem (B2); as broncas do pedido, pela regra
assert not any(f & EVENTOS_DO_MUNDO for f in FILTROS.values()), "um filtro nao pode tirar eventos do mundo"
GESTOS_DONO = ("sem_tapa", "tapa", "tapa_fruta")


# ------------------------------------------------------------------ bracos e fonte do sinal


@dataclass(frozen=True)
class Braco:
    rotulo: str
    fonte: str                       # nenhuma | consequencia | informacao | dono
    no: str                          # o no do roadmap que liga a fonte
    informacao: str | None = None    # P2: "certa"; P2e: "errada"
    memoria: str | None = None       # N6: nenhuma | relevante | recencia | embaralhada (o lobo memoria_emocao, chat B)
    pedido: bool = False             # N7: o dono pede "deixe a fruta X" (o mundo do chat A e a entrada `pedido` do chat B)
    canais: bool | None = None       # canais da consequencia (#169): None segue a config; True/False fixa (as ablacoes da K-7)
    julgamento: str | None = None    # P3i: "informacao" = o julgamento do K4 sai como informacao (JulgadorFruta saida="informacao")
    instinto_mundo: str | None = None   # P0z: o instinto do mundo num modo (PoliticaInstintoMundo, etapa 3 do B: "sem_explorar")
    pesos_janela: bool = False       # P1-cw: o peso de cada drive pela falta recente (adendo 2 do plano do corpo, A2.4; chave do B)
    regime: str | None = None        # corpo: None = "hoje" (sem corpo), "quimica" ou "corpo" (PLANO_ANALISE_V2_CORPO_DRIVES, secao 1)
    gestos: str | None = None        # corpo: o DonoComGestos (etapa 6 do A): "sem_tapa", "tapa" ou "tapa_fruta" (o tapa na fruta X, A1.1)
    banheiro: str | None = None      # banheiro: o braco do 2 x 2 (limpador x carinho depois do banheiro): "B00", "B0C", "BL0" ou "BLC"
    metabolismo: bool = False        # corpo, adendo 3 (A3.1, ME-6): o combustivel e a reserva no bloco do corpo, do tapa e nos acoplados
    alvo: bool = False               # mundo com o alvo aprendido (PLANO_ANALISE_V2_MUNDO_ALVO, secao 3): o P1 com ConfigLobos.alvo_aprendido
    digestao_lenta: bool = False     # rede de si (PLANO_ANALISE_V2_REDE_DE_SI, secao 3, RS-3): a taxa_digestao trocada no fim do dia 7


BRACOS = {
    "P0": Braco("P0", "nenhuma", "N0"),
    "P1": Braco("P1", "consequencia", "N3"),
    "P2": Braco("P2", "informacao", "N5", "certa"),
    "P2e": Braco("P2e", "informacao", "N5", "errada"),
    "P2a": Braco("P2a", "informacao", "N5", "acoplada"),
    "P3": Braco("P3", "dono", "N1"),
    # N6 (docs/PLANO_ANALISE_V2_N6.md, secao 4.1): o aprendizado do lobo de decisao desligado (N6-2), a memoria e a unica plasticidade
    "M0": Braco("M0", "nenhuma", "N6", memoria="nenhuma"),
    "MR": Braco("MR", "nenhuma", "N6", memoria="relevante"),
    "MT": Braco("MT", "nenhuma", "N6", memoria="recencia"),
    "ME": Braco("ME", "nenhuma", "N6", memoria="embaralhada"),
    # N7 (docs/PLANO_ANALISE_V2_N7.md, secao 4.1): o pedido "deixe X"; o P3+ped com a bronca da desobediencia (N7-8)
    "P0+ped": Braco("P0+ped", "nenhuma", "N7", pedido=True),
    "P1+ped": Braco("P1+ped", "consequencia", "N7", pedido=True),
    "P3+ped": Braco("P3+ped", "dono", "N7", pedido=True),
    # K-7 (PLANO_CALIBRACAO_CONJUNTA_V2, secoes 1 e 4.1): o P1 completo (memoria com o ganho da config e canais) e as duas ablacoes
    "P1c": Braco("P1c", "consequencia", "K-7", memoria="relevante", canais=True),
    "P1c-mem": Braco("P1c-mem", "consequencia", "K-7", memoria="nenhuma", canais=True),     # sem memoria: g = 0
    "P1c-can": Braco("P1c-can", "consequencia", "K-7", memoria="relevante", canais=False),  # escalar: sem canais
    # adendo 3, secao 3.3, do plano do experimento maior (P2D-P3I): o momento (P2 x P2d) e a interpretacao (P3 x P3i)
    "P2d": Braco("P2d", "informacao", "adendo-3", "depois"),          # a informacao depois do consumo, no lugar da da oferta
    "P3i": Braco("P3i", "dono", "adendo-3", julgamento="informacao"),  # o julgamento do K4 como informacao
    # mundo fisico (PLANO_ANALISE_V2_MUNDO_FISICO, secao 3 e adendo 1): o controle da premissa e a fonte dos acoplados P0^ac e P1^ac
    "P0z": Braco("P0z", "nenhuma", "mundo-fisico", instinto_mundo="sem_explorar"),
    # o mundo com o alvo aprendido (PLANO_ANALISE_V2_MUNDO_ALVO, secao 3): o mesmo P1, com a chave do alvo aprendido (#255) e o w0_alvo
    # padrao; so no mundo fisico. Os acoplados P1-alvo^ac saem do registro do P0z (a config os pede)
    "P1-alvo": Braco("P1-alvo", "consequencia", "mundo-alvo", alvo=True),
    # corpo (PLANO_ANALISE_V2_CORPO_DRIVES, secao 3): o bloco G-HOJE (a quimica contra hoje, malha fechada, os donos de sempre)
    "P0-hoje": Braco("P0-hoje", "nenhuma", "corpo-3.1", regime="hoje"),
    "P1-hoje": Braco("P1-hoje", "consequencia", "corpo-3.1", regime="hoje"),
    "P3-hoje": Braco("P3-hoje", "dono", "corpo-3.1", regime="hoje"),
    "P0-quimica": Braco("P0-quimica", "nenhuma", "corpo-3.1", regime="quimica"),
    "P1-quimica": Braco("P1-quimica", "consequencia", "corpo-3.1", regime="quimica"),
    "P3-quimica": Braco("P3-quimica", "dono", "corpo-3.1", regime="quimica"),
    # o bloco do corpo (3.2), com o DonoComGestos sem tapa; os acoplados P1-q^ac e P1-c^ac saem do registro do P0-q (a config os pede).
    # Desde o adendo 3 (A3.1, ME-6), o bloco do corpo, o do tapa e o G ganham o metabolismo em todos os bracos; o G-HOJE (3.1) fica sem
    "P0-q": Braco("P0-q", "nenhuma", "corpo-3.2", regime="quimica", gestos="sem_tapa", metabolismo=True),
    "P1-q": Braco("P1-q", "consequencia", "corpo-3.2", regime="quimica", gestos="sem_tapa", metabolismo=True),
    "P0-c": Braco("P0-c", "nenhuma", "corpo-3.2", regime="corpo", gestos="sem_tapa", metabolismo=True),
    "P1-c": Braco("P1-c", "consequencia", "corpo-3.2", regime="corpo", gestos="sem_tapa", metabolismo=True),
    # o bloco do tapa (3.3, so no mundo bola)
    "P0-c-tapa": Braco("P0-c-tapa", "nenhuma", "corpo-3.3", regime="corpo", gestos="tapa", metabolismo=True),
    "P1-c-tapa": Braco("P1-c-tapa", "consequencia", "corpo-3.3", regime="corpo", gestos="tapa", metabolismo=True),
    # o bloco G, a generalizacao do tapa (adendo 1, A1.1, no iguais_frutas)
    "P1-c-tapaX": Braco("P1-c-tapaX", "consequencia", "corpo-A1.1", regime="corpo", gestos="tapa_fruta", metabolismo=True),
    "P1-c-frutas": Braco("P1-c-frutas", "consequencia", "corpo-A1.1", regime="corpo", gestos="sem_tapa", metabolismo=True),
    # corpo, adendo 2 (PLANO_ANALISE_V2_CORPO_DRIVES, A2.4 e A2.5): o P1-c com o peso de cada drive pela janela recente
    "P1-cw": Braco("P1-cw", "consequencia", "corpo-A2.4", pesos_janela=True, regime="corpo", gestos="sem_tapa", metabolismo=True),
    # rede de si (PLANO_ANALISE_V2_REDE_DE_SI, secao 3): o P1-c com a digestao lenta a partir do fim do dia 7 (G-ADAPTA; a troca e da
    # etapa 2b, do A: espera o no) e o P1+ped com o corpo, no iguais_frutas (a autoria do pedido)
    "P1-c-lenta": Braco("P1-c-lenta", "consequencia", "rede-de-si", regime="corpo", gestos="sem_tapa", metabolismo=True,
                        digestao_lenta=True),
    "P1+ped-c": Braco("P1+ped-c", "consequencia", "rede-de-si", pedido=True, regime="corpo", gestos="sem_tapa", metabolismo=True),
    # banheiro (PLANO_ANALISE_V2_BANHEIRO, secoes 1 a 3): os quatro bracos do 2 x 2 (limpador x carinho depois do banheiro), com o cerebro A
    # no P1 (o aprendiz, fonte consequencia) e no P0 (o instinto, a referencia), no corpo com os gestos e o banheiro; o mundo fisico
    **{f"{c}-{b}": Braco(f"{c}-{b}", fonte, "banheiro", regime="corpo", banheiro=b)
       for c, fonte in (("P0", "nenhuma"), ("P1", "consequencia")) for b in ("B00", "B0C", "BL0", "BLC")},
}
# o 2 x 2 do banheiro: o braco -> (limpador, carinho depois do banheiro)
BRACOS_BANHEIRO = {"B00": (False, False), "B0C": (False, True), "BL0": (True, False), "BLC": (True, True)}
FONTES_IMPLEMENTADAS = ("nenhuma", "dono", "consequencia", "informacao")
# o que os bracos do N6 e do N7 esperam de outros chats; um braco que depende de uma peca daqui falha alto com o no. A entrada sai
# daqui quando a peca estiver na main (e os testes de tests/test_bancada_n6_n7.py dizem o que conferir entao).
# Vazio desde a BANCADA-LIGA-N6-N7: a memoria (CEREBRO-N6-N7, #167) e o pedido (N7-MUNDO, #166) estao na main. Fica a tabela para a
# proxima peca de outro chat (o K4 e os canais, rodada 10).
NOS_PENDENTES: dict = {
    # o "instinto_mundo" (W-BANCADA-MUNDO) saiu na W-LIGA-MUNDO: a PoliticaInstintoMundo e os ganchos dos cerebros estao na main (#232)
    # o "pesos_janela" (W-DOMINANCIA) saiu na W-LIGA-PESOS-JANELA: a chave da ConfigConsequencia esta na main (#236)
    # o "corpo", o "dono_gestos" e o "tapa" (W-BANCADA-CORPO) sairam na W-LIGA-GESTOS: a etapa 6 do corpo esta na main (o motor e o
    # DonoComGestos do A, #245; a quimica dos drives novos e dos gestos e o cerebro do B, #247). O "corpo_mundo" saiu junto: o #247 passou
    # o cerebro ao arranjo do MotorCorpo no mundo fisico (o consequencia_mundo credita, o consequencia_corpo fecha a decisao), com o G1
    # o "banheiro" (W-BANCADA-BANHEIRO) saiu na W-BANCADA-DOIS-PETS: a etapa 3 do banheiro esta na main (#265: o banheiro no MotorMundo,
    # a necessidade, o limpador, o limpar, o aliviar com alvo e o DonoCarinhoBanheiro)
    # dois pets (TAREFA_V2_DOIS_PETS, etapa 5, do D): o "sentidos_grupo" saiu com o #263 (a visao, o toque e a disputa) e o
    # "cerebro_social" com o #266 (as entradas sociais e o modelo dos outros no cerebro A, ligados nos bracos do grupo)
    # o "canais_fruta_mundo" (W-BANCADA-DOIS-PETS) saiu na W-BANCADA-METABOLISMO: a rota do canal do humor no mundo fisico entrou (#269,
    # ConfigLobos.presenca_fruta_mundo), ligada no cerebro do grupo
    # o "gasto_atividades" (W-BANCADA-METABOLISMO) saiu na W-BANCADA-PASSO0: o fator do gasto das atividades sobre o combustivel entrou
    # na ConfigCorpo (#275, `gasto_atividades_num/den`), e o passo 0 o escala junto com o basal (PCD-9)
    # o "planejador" (W-BANCADA-PQP) saiu na W-BANCADA-PQP-PLANO: o planejador de um alvo e o lobo `planejamento` estao na main (#294,
    # ConfigLobos.g_plano), ligados nos bracos P1-plan, P1-plan-desfecho e P1-plan-cong
    # a "digestao_lenta" (W-BANCADA-REDE) saiu com a etapa 2b da rede de si (do A): a troca da digestao no MotorCorpo
    # (`troca_digestao`), com o tick da bancada e a taxa lenta da ConfigTrocaDigestao (chave "digestao_lenta" da config)
}
# filtros do acoplado que dependem de eventos que ainda nao existem: o no do NOS_PENDENTES de cada um. O "sem_gestos" saiu na
# W-LIGA-GESTOS (o tapa na main)
FILTROS_PENDENTES: dict = {}
# a memoria de cada braco do N6 no cerebro: o M0 guarda e nao age (ganho 0, N6-2/N6-3); o ME com o desarranjo da vida (N6-6)
MODO_MEMORIA = {"nenhuma": "relevante", "relevante": "relevante", "recencia": "recencia", "embaralhada": "embaralhada"}
CONFIG_LOBOS_PADRAO = ConfigLobos()
# os drives do sinal pelos nomes do corpo (PLANO_ANALISE_V2_CORPO_DRIVES, A2.2), pelos indices de Estado.vetor (os canais de
# lobos.CANAL_DO_DRIVE: fome, higiene, energia, humor)
NOMES_DRIVES = {0: "fome", 1: "desconforto", 2: "cansaco", INDICE_HUMOR: "tristeza"}
# os drives novos do sinal pelo corpo (a etapa 6, tarefa do corpo secao 9), os que o w_novos da 6.2 do plano do corpo pesa
NOVOS_W = ("tedio", "curiosidade", "solidao", "estresse", "dor")
APRENDE_PELA_CONSEQUENCIA = ("consequencia", "informacao")   # o P2 e o P1 com a informacao na percepcao (plano do N5, secao 3)


def braco_de(rotulo: str) -> Braco:
    if rotulo not in BRACOS:
        raise KeyError(f"braco desconhecido {rotulo!r}: {sorted(BRACOS)}")
    b = BRACOS[rotulo]
    if b.fonte not in FONTES_IMPLEMENTADAS:
        raise NotImplementedError(f"braco {b.rotulo}: a fonte {b.fonte!r} chega no {b.no} (docs/ROADMAP_V2.md)")
    if b.regime is not None and b.regime not in REGIMES_CORPO:
        raise ValueError(f"braco {b.rotulo}: regime {b.regime!r}, so {REGIMES_CORPO}")
    if b.gestos is not None and (b.gestos not in GESTOS_DONO or b.regime in (None, "hoje")):
        raise ValueError(f"braco {b.rotulo}: gestos {b.gestos!r} (so {GESTOS_DONO}, e so com o corpo)")
    if b.banheiro is not None and (b.banheiro not in BRACOS_BANHEIRO or b.regime != "corpo" or b.gestos is not None
                                   or b.fonte not in ("nenhuma", "consequencia")):
        raise ValueError(f"braco {b.rotulo}: banheiro {b.banheiro!r} (so {sorted(BRACOS_BANHEIRO)}, no corpo, sem os gestos de dono e "
                         "so no P0 ou no P1)")
    if b.digestao_lenta and b.regime != "corpo":
        raise ValueError(f"braco {b.rotulo}: a digestao lenta e do corpo (regime \"corpo\"), nao {b.regime!r}")
    if b.metabolismo and b.regime not in ("quimica", "corpo"):
        raise ValueError(f"braco {b.rotulo}: o metabolismo so existe com o corpo (regime quimica ou corpo), nao {b.regime!r}")
    if b.gestos in ("tapa", "tapa_fruta") and b.regime != "corpo":
        raise ValueError(f"braco {b.rotulo}: o tapa so existe com `gestos` no corpo (regime \"corpo\"), nao {b.regime!r}")
    for peca, presente in (("memoria", b.memoria is not None), ("pedido", b.pedido), ("instinto_mundo", b.instinto_mundo is not None),
                           ("pesos_janela", b.pesos_janela), ("corpo", b.regime == "corpo"),
                           ("dono_gestos", b.gestos is not None), ("tapa", b.gestos in ("tapa", "tapa_fruta")),
                           ("banheiro", b.banheiro is not None), ("digestao_lenta", b.digestao_lenta)):
        if presente and peca in NOS_PENDENTES:
            raise NotImplementedError(f"braco {b.rotulo}: {NOS_PENDENTES[peca]}")
    return b


def filtro_de(nome: str) -> frozenset:
    """O conjunto de acoes que o filtro do acoplado tira; um filtro que depende de evento que ainda nao existe falha alto com o no."""
    if nome in FILTROS_PENDENTES and FILTROS_PENDENTES[nome] in NOS_PENDENTES:
        raise NotImplementedError(f"filtro {nome!r}: {NOS_PENDENTES[FILTROS_PENDENTES[nome]]}")
    if nome not in FILTROS:
        raise KeyError(f"filtro desconhecido {nome!r}: {sorted(FILTROS)}")
    return FILTROS[nome]


def desarranjo_n6(semente: int) -> dict:
    """N6-6 (plano do N6, secao 4.1): a permutacao pi do ME, um desarranjo de FRUTAS (nenhuma fruta em si mesma), sorteado uma vez por
    vida pela rng propria derivar_semente("n6-embaralha", semente). Com tres frutas ha dois, um por sentido do ciclo. Nao toca outra rng."""
    rng = random.Random(derivar_semente("n6-embaralha", semente))
    passo = 1 + rng.randrange(len(FRUTAS) - 1) if len(FRUTAS) == 3 else None
    if passo is None:                       # pragma: no cover - o mundo das frutas tem tres frutas (FRUTAS)
        raise ValueError("desarranjo_n6 escrito para tres frutas")
    pi = {f: FRUTAS[(i + passo) % len(FRUTAS)] for i, f in enumerate(FRUTAS)}
    if tuple(pi[f] for f in FRUTAS) != desarranjo_dos_lobos(semente):     # o mesmo pi que os lobos usam (CEREBRO-N6-N7)
        raise RuntimeError("desarranjo_n6 da bancada difere do dos lobos")
    return pi


# BANCADA-MONTAGEM: as pecas do cerebro A montado que cada fonte liga (PLANO_CALIBRACAO_CONJUNTA_V2, secao 1). memoria: o modo
# (com o ganho g da config); canais: os da consequencia; info: o w0_info da config. O pedido segue o braco (so onde ha pedido).
MONTAGENS = ("simples", "completa")
MONTAGEM_PADRAO = "simples"
MONTAGEM_COMPLETA = {
    "nenhuma": {"memoria": None, "canais": False, "info": False},           # P0 (K-1): o instinto, nada ligado
    "consequencia": {"memoria": "relevante", "canais": True, "info": False},  # P1
    "informacao": {"memoria": "relevante", "canais": True, "info": True},     # P2, P2e, P2a
    "dono": {"memoria": "relevante", "canais": False, "info": False},         # P3: o sinal e o dono, sem canais
}


def recebe_informacao(b: Braco) -> bool:
    """O braco recebe informacao do dono? Os de fonte informacao (P2, P2e, P2a, P2d) e o P3i (o julgamento como informacao): na
    montagem completa so eles ficam com o w0_info da config."""
    return MONTAGEM_COMPLETA[b.fonte]["info"] or b.julgamento == "informacao"


def braco_montado(b: Braco, montagem: str, frutas: bool) -> Braco:
    """O braco com as pecas da montagem. "simples": o proprio braco. "completa": a memoria e os canais da fonte (MONTAGEM_COMPLETA)
    onde o braco nao os fixa; a memoria so nos mundos das frutas (fora deles o cerebro nao a tem). O que o braco fixa vence: o N6 (M0 a
    ME) e as ablacoes da K-7 (P1c-mem sem memoria, P1c-can sem canais) ficam o que sao, por cima da montagem."""
    if montagem not in MONTAGENS:
        raise ValueError(f"montagem {montagem!r}: so {MONTAGENS}")
    if montagem == "simples":
        return b
    pecas = MONTAGEM_COMPLETA[b.fonte]
    memoria = b.memoria if b.memoria is not None else (pecas["memoria"] if frutas else None)
    canais = b.canais if b.canais is not None else pecas["canais"]
    return replace(b, memoria=memoria, canais=canais)


def cfg_lobos_do_braco(cl: ConfigLobos, b: Braco, semente: int, montagem: str = MONTAGEM_PADRAO) -> ConfigLobos:
    """As chaves do N6 e do N7 que o braco liga por cima do aprendiz do ponto (CEREBRO-N6-N7): memoria so nos bracos de memoria (o M0
    com ganho 0; o MT na recencia; o ME com o desarranjo da vida), o pedido so nos bracos com pedido (w0_pedido da config). Nos outros
    bracos as chaves voltam ao padrao (desligadas): a vida de hoje, byte a byte, seja qual for a config. Na montagem completa o braco
    chega ja montado (braco_montado) e o w0_info da config fica so nos bracos com fonte informacao (os P2)."""
    if montagem not in MONTAGENS:
        raise ValueError(f"montagem {montagem!r}: so {MONTAGENS}")
    if montagem == "completa" and not recebe_informacao(b):
        cl = replace(cl, w0_info=0)
    if b.memoria is None:
        cl = replace(cl, memoria_ligada=False, memoria_ganho=0, memoria_modo=CONFIG_LOBOS_PADRAO.memoria_modo, memoria_permutacao=())
    else:
        modo = MODO_MEMORIA[b.memoria]
        cl = replace(cl, memoria_ligada=True, memoria_modo=modo, memoria_ganho=0 if b.memoria == "nenhuma" else cl.memoria_ganho,
                     memoria_permutacao=desarranjo_dos_lobos(semente) if modo == "embaralhada" else ())
    if not b.pedido:
        cl = replace(cl, w0_pedido=0)
    return cl


class PoliticaDoBraco:
    """O cerebro do braco com a fonte do sinal na frente dele. Decide, observa e serializa pelo cerebro; o que muda entre os
    bracos e so de onde vem o sinal: na fonte "dono" tudo o que passa por `receber_acao_dono`, na "nenhuma" nada, na
    "consequencia" so o sinal da propria acao, calculado em `observar` (o dono nao chega). Nao consome rng nem muda a ordem de
    nada: a vida do P3 e byte a byte a da L1 e a do P0 a do instinto (testes).

    Os gestos do corpo (etapa 6; TAREFA_V2_CORPO_DRIVES, secao 8): o tapa e o sinal direto (CD-10) e chega ao cerebro em toda fonte que
    aprende (dono, consequencia, informacao); o carinho chega so pelo corpo, no `mudanca_no_corpo` (CD-4), nas mesmas fontes. No P0
    (fonte "nenhuma", o aprendizado desligado) nenhum dos dois chega, como nada do dono."""

    def __init__(self, cerebro, braco: Braco, cfg_consequencia: ConfigConsequencia | None = None) -> None:
        self.cerebro = cerebro
        self.braco = braco
        self.nome = cerebro.nome
        self.cfg_consequencia = cfg_consequencia or CONFIG_CONSEQUENCIA
        self.sinais_entregues = 0        # elogios e broncas que chegaram ao aprendiz (a eficiencia amostral conta estes)
        self.consequencias = 0           # P1: decisoes com sinal de consequencia != 0

    def agir(self, obs, rng):
        return self.cerebro.agir(obs, rng)

    def observar(self, transicao) -> None:
        if self.braco.fonte in APRENDE_PELA_CONSEQUENCIA:
            f_S = sinal_homeostatico(transicao, self.cerebro.cl.escala, self.cfg_consequencia)
            self.consequencias += f_S != 0
            self.cerebro.observar_consequencia(transicao, f_S, self.cfg_consequencia)   # o mesmo ganho no sinal da fruta (E2)
        else:
            self.cerebro.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if self.braco.fonte == "dono":
            self.sinais_entregues += acao.value in SINAIS_DO_DONO
            self.cerebro.receber_acao_dono(acao, tick)
        elif acao is AcaoUsuario.TAPA and self.braco.fonte in APRENDE_PELA_CONSEQUENCIA:
            # o tapa e o sinal direto em toda fonte que aprende (CD-10): o cerebro o credita a ultima decisao; o resto do dono nao chega
            self.sinais_entregues += 1
            self.cerebro.receber_acao_dono(acao, tick)
        elif self.braco.fonte not in ("nenhuma",) + APRENDE_PELA_CONSEQUENCIA:   # pragma: no cover - braco_de ja barra
            raise NotImplementedError(self.braco.fonte)
        # informacao: nada do dono chega ao aprendiz por aqui (o MotorFrutas nem chama o gancho para informar; plano do N5, secao 3)

    def mudanca_no_corpo(self, obs_antes, obs_depois) -> None:
        """O carinho pelo corpo (CD-4; o MotorCorpo com `gestos` chama este gancho, sem dizer que gesto foi): chega ao cerebro nas fontes
        que aprendem, como o tapa; no P0, nada. Explicito, para o __getattr__ nao o repassar ao P0."""
        if self.braco.fonte == "nenhuma":
            return
        self.cerebro.mudanca_no_corpo(obs_antes, obs_depois)

    def consequencia_mundo(self, acao, ocorrido: dict, obs_depois) -> None:
        """O gancho do MotorMundo (explorar, comer e brincar, com tudo aplicado), repassado ao cerebro EM TODA FONTE: o cerebro anota o
        que aconteceu no motivo, o modelo dos outros (`modelo_outros`, dois pets, #266) conta as idas a `onde_comeu` e o que o pet comeu,
        e so na fonte consequencia ha sinal pendente para creditar (o cerebro decide; no P0, nada e creditado). Explicito, para nao
        depender do __getattr__; o cerebro sem o gancho (o instinto) nao recebe nada, como antes."""
        gancho = getattr(self.cerebro, "consequencia_mundo", None)
        if gancho is not None:
            gancho(acao, ocorrido, obs_depois)

    def estado_interno(self) -> dict:
        return {**self.cerebro.estado_interno(), "bancada": {"braco": self.braco.rotulo, "fonte": self.braco.fonte}}

    def __getattr__(self, nome):
        cerebro = self.__dict__.get("cerebro")
        if cerebro is None:
            raise AttributeError(nome)
        return getattr(cerebro, nome)


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .mundos import REGIMES_CORPO  # noqa: E402
