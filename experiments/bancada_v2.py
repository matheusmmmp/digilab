"""V2, BANCADA (docs/TAREFA_V2_BANCADA.md): um orquestrador unico para os bracos da pergunta maior.

    python experiments/bancada_v2.py --config experiments/configs/bancada/fumaca.json --saida <pasta>   # fumaca, NAO canonica

A pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6) compara fontes de plasticidade no MESMO aprendiz (validacao
V1 do docs/ROADMAP_V2.md: a L1 separa de onde vem o sinal da regra de atualizacao). A bancada fixa isso em codigo:

  vida = (genoma, mundo, dono, braco, semente)
    genoma   None = sem genoma (temperamento neutro); um inteiro g = temperamento sorteado de g (a semente do genoma separada
             da do ambiente, como no E1 da linhagem). No mundo padrao: MotorComFeedback sem genoma (como a L1) e
             MotorPersonalidade com genoma; nos mundos da bola, sempre o MotorAmbiente da A1 (obediencia desligada).
    mundo    padrao   o motor de sempre, sem objeto nenhum.
             bola     a bola da A1 (MotorAmbiente, ConfigBola ligada) com as decisoes B1 e B2 de 2026-10-01: os donos sao os
                      da v1 (o aleatorio NAO sorteia por_bola) e a bola entra por uma regra do mundo FORA do orcamento
                      (RegraBola: a regra dos coerentes do DonoComBola sem o limite do passo; o relapso so nas visitas, B3).
             bola_a1  a bola exatamente como a A1 rodou (DonoComBola: o aleatorio sorteia por_bola e a bola gasta orcamento);
                      so para reproduzir a A1 (gate), nao para runs novas.
             casado_frutas, descasado, mutavel   os mundos das frutas (N4, MotorFrutas; docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md,
                      secao 2, E1): as mesmas ofertas nos tres, por um calendario que sai da semente (CalendarioFrutas: horarios
                      fixos, a rotacao do N4 com o inicio derivado da semente, sem olhar o estado do pet nem o braco), fora do
                      orcamento e fora do sorteio do dono aleatorio (B1, B2). Muda so o efeito no humor (F6), pelo genoma das frutas:
                      no casado a fruta de maior preferencia inata faz bem e a de menor faz mal; no descasado, o contrario; a do
                      meio e neutra nos dois (efeitos_da_condicao: o descasado e o casado com o sinal trocado). O mutavel comeca
                      casado e troca para o descasado na metade da vida (tick_troca); a troca fica no registro derivado do motor
                      (MotorFrutasMundo.troca) e o replay a refaz.
             Cada mundo realiza uma CONDICAO da pergunta maior (CONDICOES): casado (padrao, bola, bola_a1, casado_frutas),
             descasado e mutavel.
    dono     um dono sintetico; a rng do dono deriva de (semente, nome do dono), igual em todos os bracos e mundos.
    braco    P0..P3: o MESMO cerebro (PoliticaLobos, mesmo prior, mesma ConfigLobos); so a FONTE do sinal muda.
    semente  a do motor: rng de ambiente = semente, rng de politica = semente + 1_000_003 (engine.py, intocado).

  fontes (o campo `fonte` do braco):
    nenhuma       P0   so a predisposicao herdada: o aprendiz com o aprendizado DESLIGADO (o prior fixo). Nada do dono chega
                       a ele. Entregar "sinal nenhum" a um aprendiz ligado nao e P0: o credito do chamado expira por dentro
                       (Aprendiz._expirar) e vira sinal negativo do dono ausente.
    consequencia  P1   (N3, docs/PLANO_ANALISE_V2_N3.md) a consequencia da propria acao: em `observar`, o sinal
                       `lobos.sinal_homeostatico` da transicao (reducao do deficit de fome, higiene e energia, janela
                       imediata) entra na mesma regra de atualizacao da L1 (`Aprendiz.observar_consequencia`). Nada do
                       dono chega ao aprendiz (nem o credito do chamado).
    informacao    P2   (certa), P2e (errada) e P2a (acoplada): o aprendiz do P1 (a consequencia da propria acao, com a E2, e o
                       UNICO reforco) num mundo das frutas em que um informante diz se cada fruta faz bem ou mal
                       (docs/PLANO_ANALISE_V2_N5.md). A informacao entra pela percepcao (o MotorFrutas injeta `info_frutas`), nunca
                       pelo `receber_acao_dono`: nada do dono chega ao aprendiz. P2 = DonoInformante `certo` logo depois de cada
                       oferta do CalendarioFrutas; P2e = `errado`, nos mesmos ticks; P2a = o mesmo multiconjunto (fruta, conteudo
                       verdadeiro) do P2 em ticks sorteados pela rng derivar_semente("informacao-acoplada", semente) (plano,
                       secao 4.2; InformanteAcoplado). Informar e evento do log fora do orcamento, pelo canal do mundo.
    dono          P3   o feedback explicito (COACH): toda acao do dono chega ao aprendiz pelo gancho receber_acao_dono,
                       exatamente como na L1 (a vida e byte a byte a da L1: teste).

  modo acoplado (malha aberta; generaliza log_so_cuidado/vidas_acopladas de run_v2_l1.py): o registro de eventos de uma vida,
  com um filtro (nenhum, sem_sinais, sem_sinais_sem_carinho), e rejogado com o cerebro de outro braco, no MESMO mundo. O motor
  acoplado guarda o log filtrado: o registro dele e o da origem com os eventos retirados, evento a evento. Os eventos do mundo
  (por/tirar a bola; as ofertas de fruta do N4) nunca saem: nenhum filtro pode retira-los (o "so cuidado" da A1, que tirava a
  bola, e outra coisa e fica em run_v2_a1.py).

  cerebros: lobos (o aprendiz, todos os bracos) e instinto (a referencia herdada, so no P0: PoliticaInstintoBola na bola,
  PoliticaInstintoFrutas nas frutas). Desde a BANCADA-N5 os lobos veem o mundo (LOBOS-MUNDO, #141): a bancada passa cfg_bola nos
  mundos da bola e cfg_frutas nos das frutas, e o P0 com lobos e o instinto que ve a bola e as frutas, byte a byte. No mundo padrao,
  nada muda.

  medidas (todas de digilab/metrics.py; nenhuma conta aqui): desempenho no proprio ambiente (tempo fora de privacao e saude
  media, amostrados em cada decisao; humor medio, `privacao_nas_decisoes`; acerto na tarefa do dono, `acerto_na_tarefa`), custo
  da plasticidade (deriva ao prior por dia e tempo ate a metade do caminho, `custo_da_plasticidade`), nos mundos das frutas a
  `taxa_fruta_ruim` por janela (inicio, final, antes e depois da troca, e por dia) e a tabela braco x condicao.

  unidades derivadas (E3 do plano do experimento maior, secao 8.1): de cada semente reservada (base b) saem K unidades,
  semente = derivar_semente("experimento-maior", b, k) e genoma = derivar_semente("experimento-maior-genoma", b, k)
  (unidades_derivadas; o campo "unidades" da config). FAIXAS_RESERVADAS lista as faixas reservadas ou usadas; o teste confere
  que nenhuma unidade cai nelas.

  N6 e N7 (BANCADA-N6-N7; docs/PLANO_ANALISE_V2_N6.md e docs/PLANO_ANALISE_V2_N7.md): o mundo iguais_frutas (condicao "iguais": as
  tres frutas com o efeito neutro, N7-5), os bracos de memoria M0, MR, MT, ME (N6) e os do pedido P0+ped, P1+ped, P3+ped (N7), o
  desarranjo do ME por rng propria (desarranjo_n6, N6-6) e as unidades derivadas com prefixo ("n6", "n7"; o padrao continua
  "experimento-maior"). Desde a BANCADA-LIGA-N6-N7 os bracos rodam: a memoria e o pedido do cerebro (CEREBRO-N6-N7) por cima do ponto,
  o DonoPedinte (N7-MUNDO) pelo canal do mundo, os pedidos e as broncas do pedido fora do orcamento, o "so cuidado" sem eles, e as
  medidas dos dois planos lidas das sondas que o cerebro grava no motivo.

  K4 e canais (BANCADA-K4-CANAIS; decisao do Matheus de 2026-10-05 e K-7 do plano da calibracao conjunta): com "julgamento_fruta" na
  config, o dono dos bracos com fonte dono (o P3) julga cada consumo de fruta pelo efeito real vigente (JulgadorFruta, #170), pela
  regra do mundo, FORA do orcamento (o atencioso decide com o orcamento inteiro); os julgamentos sao elogiar/repreender contados a parte
  (VidaBancada.julgamentos) e saem com o sem_ensino. Os canais (#169) seguem a chave "consequencia" da config, e um braco pode fixa-los
  (Braco.canais): as ablacoes da K-7 sao o P1c (P1 completo: memoria e canais), o P1c-mem (sem memoria, g = 0) e o P1c-can (escalar).

  montagem (BANCADA-MONTAGEM; decisao do Matheus de 2026-10-05, opcao 1; PLANO_CALIBRACAO_CONJUNTA_V2, secao 1): a chave "montagem" da
  config. "simples" (o padrao, e sem a chave) e a bancada de antes, byte a byte. "completa" monta o cerebro A da secao 1 em cada braco,
  pela fonte (MONTAGEM_COMPLETA): o P0 sem nada; P1, P2, P2e, P2a e P3 com a memoria relevante (ganho g da config, so nos mundos das
  frutas); canais ligados nos que aprendem pela consequencia (P1, P2*) e desligados no P3; w0_info da config so nos P2*; w0_pedido da
  config so nos bracos com pedido. O que o braco fixa (a memoria do N6 e das ablacoes, os canais das ablacoes) vence a montagem, entao o
  P1c e o P1 completo e o P1c-mem e o P1c-can sao o P1 completo menos uma peca.

  P2d e P3i (P2D-P3I, parte D; adendo 3, secao 3.3, do plano do experimento maior): o P2d e o P2 com a informacao depois do consumo (o
  JulgadorFruta da parte A com saida="informacao", no primeiro passo do dono depois de cada consumo, no lugar do informante da oferta);
  o P3i e o P3 com o julgamento do K4 saindo como informacao (a mesma saida), e na montagem completa com o w0_info da config. O
  conhecimento e o mesmo do P2 e do K4 (os efeitos reais da bancada, com a troca do mutavel); as informacoes ficam fora do orcamento,
  contam em `informacoes` e saem no sem_ensino; o multiconjunto (fruta, conteudo) vai por vida nas medidas.

  ponto do aprendiz (BANCADA-EXPERIMENTO; decisao R1 de 2026-10-05, docs/RESULTADO_V2_REVISAO_APRENDIZ.md): o campo "ponto" da config
  escolhe um ponto nomeado de PONTOS_APRENDIZ, e a chave "lobos" troca campos por cima dele. Sem "ponto", o "L1" (o
  CONFIG_LOBOS_APRENDIZ: passo 512, teto 1024), entao as runs antigas nao mudam. O "T3" (teto 16*S = 16384, o resto igual: sem traco)
  e o ponto de partida do N5 e do experimento maior (PONTO_N5_EXPERIMENTO).

Toda vida e rejogada do disco e comparada bit a bit (G1): divergencia levanta erro e para tudo. engine.py e lobos.py nao
mudam. Sementes: so as dos testes (101...505) sem plano; qualquer outra exige o plano de analise registrado (campo "plano").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.ambiente import (DonoComBola, MotorAmbiente, PoliticaInstintoBola, _PoliticaComBola,  # noqa: E402
                              reproduzir_ambiente)
from digilab.config import (CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_DONOS, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, CONFIG_PEDIDO_LIGADA, TICKS_POR_DIA,
                            ConfigBola, ConfigConsequencia, ConfigFrutas, ConfigInformacao, ConfigJulgamentoFruta, ConfigLobos,
                            ConfigPedido)
from digilab.donos import Visao, criar_dono, cuidados_necessarios, julgar_acao  # noqa: E402
from digilab.events import (ACOES_BOLA, ACOES_FRUTAS, ACOES_INFORMACAO, ACOES_PEDIDO, FRUTAS, AcaoPet, AcaoUsuario,  # noqa: E402
                            LogDeEventos, fruta_de, informar, oferta_de)
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.frutas import (DonoInformante, DonoPedinte, JulgadorFruta, MotorFrutas, PoliticaInstintoFrutas,  # noqa: E402
                            _PoliticaComFrutas, genoma_frutas)
from digilab.metrics import (acerto_na_tarefa, custo_da_plasticidade, desempenho_no_ambiente,  # noqa: E402
                             consumos_ate_metade, distribuicoes_de_acao, estados_sonda, jsd_media, multiconjunto_informacoes, privacao_nas_decisoes,
                             resposta_a_bola, tabela_braco_condicao, tabela_braco_condicao_parcial, taxa_fruta_ruim,
                             ZONAS_CONFLITO, deferencia_ao_pedido, dia_cruza_zero, fracao_da_fruta, memoria_nas_subdecisoes,
                             ocupacao_espacos_frutas)
from digilab.obediencia import MotorPersonalidade, _PoliticaObservada  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import desarranjo_n6 as desarranjo_dos_lobos  # noqa: E402
from digilab.policies.lobos import sinal_homeostatico  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import CanalDeInteracao, MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402

ACOES = tuple(a.value for a in AcaoPet)
SINAIS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})
SEMENTES_TESTE = frozenset({101, 202, 303, 404, 505})
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
FILTROS = {"nenhum": frozenset(), "sem_sinais": SINAIS,
           "sem_sinais_sem_carinho": SINAIS | {AcaoUsuario.ACARICIAR.value},
           # N5 (plano, secao 4): o "so cuidado" do P2 tira os sinais de ensino E a informacao; as ofertas ficam. N7 (plano, secao 4.2):
           # o "so cuidado" do P3+ped tira tambem os pedidos; as broncas do pedido sao `repreender` e saem com os sinais
           "sem_informacao": INFORMACOES, "sem_ensino": SINAIS | INFORMACOES | PEDIDOS,
           "sem_ensino_sem_carinho": SINAIS | INFORMACOES | PEDIDOS | {AcaoUsuario.ACARICIAR.value},
           # N7: o controle do P0+ped (o P0 no registro dele sem os pedidos; os sinais do dono ficam) e o nome do plano para o so cuidado
           "sem_pedido": PEDIDOS, "sem_ensino_sem_pedido": SINAIS | INFORMACOES | PEDIDOS}
# os eventos do MUNDO no log: acoes do dono que poem coisas no cenario. O acoplado nunca os tira (as ofertas de fruta do N4 entram
# aqui quando existirem). Os filtros so tiram o que o dono ENSINA ou o carinho.
EVENTOS_DO_MUNDO = frozenset(a.value for a in ACOES_BOLA + ACOES_FRUTAS)
# o que entra pelo canal do mundo, fora do orcamento do dono: os eventos do mundo e a informacao do dono (B2; plano do N5, secao 2).
# A informacao NAO e evento do mundo: o "so cuidado" a tira (FILTROS); o mundo (bola, ofertas) nunca sai.
FORA_DO_ORCAMENTO = EVENTOS_DO_MUNDO | INFORMACOES | PEDIDOS     # N7: os pedidos tambem (B2); as broncas do pedido, pela regra
assert not any(f & EVENTOS_DO_MUNDO for f in FILTROS.values()), "um filtro nao pode tirar eventos do mundo"


@dataclass(frozen=True)
class Condicao:
    """Uma condicao da pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6, item 2): a relacao entre o mundo e a
    predisposicao herdada. `precisa` = o que falta (e de qual no) para a condicao existir; vazio quando ja existe."""

    nome: str
    descricao: str
    precisa: str = ""
    no: str = ""


CONDICOES = {
    "casado": Condicao("casado", "o mundo e aquele para o qual o prior foi feito: nada nele contradiz a predisposicao herdada"),
    "descasado": Condicao(
        "descasado", "o mundo contradiz o prior: a fruta preferida de nascenca faz mal (e a menos preferida faz bem)"),
    "mutavel": Condicao(
        "mutavel", "o mundo muda no meio da vida: comeca casado e o efeito das frutas troca na metade (a boa vira ruim e "
        "vice-versa); a troca fica no registro derivado e o replay a refaz"),
    # N7-5 (docs/PLANO_ANALISE_V2_N7.md, secao 4.3): fora da pergunta maior, o mundo da arbitragem
    "iguais": Condicao(
        "iguais", "as tres frutas com o mesmo efeito (neutro no humor) e a mesma nutricao: escolher uma fruta nao tem consequencia "
        "propria, so a da fome (o mundo \"iguais\" do N4 na bancada)"),
}


@dataclass(frozen=True)
class Mundo:
    nome: str
    condicao: str                    # a condicao da pergunta maior que este mundo realiza
    bola: str | None = None          # None: sem bola; "b1b2": a bola das decisoes B1/B2; "a1": a bola como a A1 rodou
    frutas: bool = False             # os mundos das frutas (MotorFrutasMundo); o efeito sai da condicao

    @property
    def ambiente(self) -> bool:
        """roda no MotorAmbiente (bola) ou numa subclasse dele (frutas)"""
        return self.bola is not None or self.frutas


MUNDOS = {
    "padrao": Mundo("padrao", "casado"),
    "bola": Mundo("bola", "casado", "b1b2"),
    "bola_a1": Mundo("bola_a1", "casado", "a1"),
    "casado_frutas": Mundo("casado_frutas", "casado", frutas=True),
    "descasado": Mundo("descasado", "descasado", frutas=True),
    "mutavel": Mundo("mutavel", "mutavel", frutas=True),
    "iguais_frutas": Mundo("iguais_frutas", "iguais", frutas=True),
}


def mundo_de(nome: str) -> Mundo:
    if nome in CONDICOES and CONDICOES[nome].precisa:
        c = CONDICOES[nome]
        raise NotImplementedError(f"condicao {nome!r} ({c.descricao}): precisa {c.precisa}")
    if nome not in MUNDOS:
        raise NotImplementedError(f"mundo {nome!r}: so {sorted(MUNDOS)}")
    m = MUNDOS[nome]
    if CONDICOES[m.condicao].precisa:          # pragma: no cover - um mundo registrado so realiza condicao que ja existe
        raise NotImplementedError(m.condicao)
    return m
MEDIDAS_TABELA = ("fracao_fora_de_privacao", "saude_media", "humor_medio", "acerto_total", "deriva_final")
CHAVES_CONFIG = {"descricao", "plano", "bracos", "donos", "sementes", "unidades", "genomas", "mundos", "dias", "orcamento",
                 "sonda", "bootstrap", "acoplados", "consequencia", "lobos", "frutas", "ponto", "julgamento_fruta", "montagem"}
# K4 fora do orcamento (decisao do Matheus, 2026-10-05): a chave liga o motor e a regra do mundo; o julgamento usa elogiar/repreender
CONFIG_JULGAMENTO_FORA = ConfigJulgamentoFruta(ligada=True, no_orcamento=False)
JULGAMENTOS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})


# ------------------------------------------------------------------ as frutas na bancada


def efeitos_da_condicao(genoma, cf: ConfigFrutas, condicao: str) -> dict:
    """O efeito no humor de cada fruta (F6: o ruim no humor, fora de em_privacao). Casado: a de maior preferencia inata faz bem
    (-efeito_humor_ruim) e a de menor faz mal (efeito_humor_ruim); descasado: o mesmo com o sinal trocado; a do meio fica com o
    efeito neutro nos dois. Assim casado e descasado diferem SO no sinal, e os dois tem uma fruta boa e uma ruim."""
    if condicao == "iguais":                       # N7-5: todas com o efeito neutro, como o mundo "iguais" do N4
        return {f: cf.efeito_humor_neutro for f in FRUTAS}
    if cf.efeito_humor_ruim >= 0.0:
        raise ValueError("efeito_humor_ruim precisa ser negativo")
    pref = genoma.preferencia_inata
    maior = genoma.fruta_preferida()
    menor = min(FRUTAS, key=lambda f: (pref[f], FRUTAS.index(f)))
    if maior == menor:
        raise ValueError("preferencias inatas iguais: sem fruta preferida nem rejeitada")
    ruim, bom = cf.efeito_humor_ruim, -cf.efeito_humor_ruim
    if condicao == "casado":
        alto, baixo = bom, ruim
    elif condicao == "descasado":
        alto, baixo = ruim, bom
    else:
        raise ValueError(f"efeitos so de casado, descasado ou iguais, nao {condicao!r}")
    return {f: (alto if f == maior else baixo if f == menor else cf.efeito_humor_neutro) for f in FRUTAS}


class MotorFrutasMundo(MotorFrutas):
    """O MotorFrutas (digilab/frutas.py, que nao muda) com o efeito de cada fruta dado pela CONDICAO do mundo da bancada, no
    lugar do `ConfigFrutas.mundo` do N4. No mutavel o efeito comeca casado e troca para o descasado na primeira decisao em ou
    depois de `tick_troca` (as decisoes caem a cada 15 ticks, entao com tick_troca multiplo de 15 a troca e no tick exato); a
    troca fica em `self.troca` (registro derivado: tick e os efeitos antes e depois) e em cada consumo (o efeito aplicado).
    Nenhuma rng a mais; o replay pelo log refaz tudo."""

    def __init__(self, *a, condicao: str, tick_troca: int | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        if not self.cf.ligada:
            raise ValueError("os mundos das frutas pedem ConfigFrutas.ligada")
        if condicao == "mutavel":
            if tick_troca is None or tick_troca <= 0:
                raise ValueError("o mutavel precisa de tick_troca > 0")
            inicial = "casado"
        elif condicao in ("casado", "descasado", "iguais"):
            if tick_troca is not None:
                raise ValueError(f"so o mutavel troca, nao {condicao!r}")
            inicial = condicao
        else:
            raise ValueError(f"condicao das frutas desconhecida: {condicao!r}")
        self.condicao = condicao
        self.tick_troca = tick_troca
        conds = ("iguais",) if condicao == "iguais" else ("casado", "descasado")
        self._efeitos = {c: efeitos_da_condicao(self.genoma, self.cf, c) for c in conds}
        self.efeito_vigente = inicial
        self.efeito_humor = dict(self._efeitos[inicial])
        self.troca: dict | None = None

    def _frutas_na_proxima_decisao(self) -> float:
        t = self._estado.tick
        if self.condicao == "mutavel" and self.troca is None and t >= self.tick_troca:
            antes = dict(self.efeito_humor)
            self.efeito_vigente = "descasado"
            self.efeito_humor = dict(self._efeitos["descasado"])
            self.troca = {"tick": t, "tick_troca": self.tick_troca, "de": "casado", "para": "descasado",
                          "efeito_antes": antes, "efeito_depois": dict(self.efeito_humor)}
        return super()._frutas_na_proxima_decisao()

    def resumo_mundo(self) -> dict:
        return {"condicao": self.condicao, "tick_troca": self.tick_troca, "efeito_vigente": self.efeito_vigente,
                "efeitos": {c: dict(e) for c, e in self._efeitos.items()}, "troca": self.troca}


class CalendarioFrutas:
    """As ofertas de fruta do experimento maior (plano, secao 2; K5): saem da SEMENTE, nao do estado do pet nem do braco, entao o
    mesmo pet ve as mesmas frutas nos mesmos ticks em qualquer braco e condicao. Nos horarios fixos do N4
    (`ConfigFrutas.horarios_oferta`), todo dia, o proximo conjunto da `rotacao_ofertas`, comecando no indice
    derivar_semente("calendario-frutas", semente) % len(rotacao). Diferente do OfertasFrutas do N4, oferece com o pet dormindo
    tambem (a fruta fica no cenario ate o prazo): olhar o sono faria a oferta depender do estado. Regra do mundo da bancada:
    fora do orcamento e fora do sorteio do dono aleatorio (B1, B2), igual para todo dono."""

    def __init__(self, semente: int, cf: ConfigFrutas) -> None:
        self.cf = cf
        self.k = derivar_semente("calendario-frutas", semente) % len(cf.rotacao_ofertas)

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        if visao.estado["tick"] % TICKS_POR_DIA not in self.cf.horarios_oferta:
            return []
        conjunto = self.cf.rotacao_ofertas[self.k % len(self.cf.rotacao_ofertas)]
        self.k += 1
        return [oferta_de(f) for f in conjunto]


# ------------------------------------------------------------------ unidades derivadas (E3)

BASES_EXPERIMENTO_MAIOR = {"calibracao": (14101, 14202, 14303, 14404, 14505),
                           "validacao": (15101, 15202, 15303, 15404, 15505)}
BASES_N6 = {"calibracao": (19101, 19202, 19303, 19404, 19505), "validacao": (20101, 20202, 20303, 20404, 20505)}
BASES_N7 = {"calibracao": (21101, 21202, 21303, 21404, 21505), "validacao": (22101, 22202, 22303, 22404, 22505)}
BASES_COMPARACAO = {"calibracao": (28101, 28202, 28303, 28404, 28505), "validacao": (29101, 29202, 29303, 29404, 29505)}
# o prefixo das unidades derivadas de cada plano (regra E3): semente derivar_semente(prefixo, b, k), genoma
# derivar_semente(prefixo + "-genoma", b, k) (plano do N6, secao 12.2; plano do N7, secao 12.2; o da comparacao dos cerebros,
# PLANO_ANALISE_V2_COMPARACAO_CEREBROS, secao 6.2)
PREFIXOS_UNIDADES = ("experimento-maior", "n6", "n7", "comparacao-cerebros")
# faixas reservadas ou ja usadas no repositorio (fonte ao lado); o teste tambem varre experiments/configs/. Intervalos fechados.
FAIXAS_RESERVADAS = (
    (101, 1010, "testes (101...505) e ovos da personalidade (101...1010)"),
    (1101, 1505, "baterias do combate V2 (configs bateria_*)"),
    (2101, 2505, "validacao do combate V2"),
    (3101, 3505, "calibracao: V2.1, L1, vinculo B"),
    (4101, 4505, "validacao: V2.1, V21D, equilibrio, L1"),
    (5101, 5505, "validacao do vinculo B"),
    (6101, 6505, "A1, calibracao"), (7101, 7505, "A1, validacao"),
    (8101, 8505, "N3, calibracao"), (9101, 9505, "N3, validacao"),
    (10101, 10505, "N4, calibracao"), (11101, 11505, "N4, validacao"),
    (12101, 12505, "N5, calibracao (reservada)"), (13101, 13505, "N5, validacao (reservada)"),
    (14101, 14505, "experimento maior, bases da calibracao"), (15101, 15505, "experimento maior, bases da validacao"),
    (16101, 16505, "N11 cerebros, calibracao (ROADMAP_V2, secao 6; substituida pela C-8, nao usar)"),
    (17101, 17505, "N11 cerebros, validacao (ROADMAP_V2, secao 6; substituida pela C-8, nao usar)"),
    (18101, 18505, "revisao do aprendiz, so calibracao (V2_RODADA_5)"),
    (19101, 19505, "N6, calibracao (PLANO_ANALISE_V2_N6, N6-9)"), (20101, 20505, "N6, validacao (PLANO_ANALISE_V2_N6, N6-9)"),
    (21101, 21505, "N7, calibracao (PLANO_ANALISE_V2_N7, secao 12.1)"), (22101, 22505, "N7, validacao (PLANO_ANALISE_V2_N7, secao 12.1)"),
    (28101, 28505, "comparacao dos cerebros: calibracao de B e C e piloto (PLANO_ANALISE_V2_COMPARACAO_CEREBROS, C-8)"),
    (29101, 29505, "comparacao dos cerebros: validacao de A, B e C (PLANO_ANALISE_V2_COMPARACAO_CEREBROS, C-8)"),
    (50001, 50020, "analise de poder, piloto"), (60001, 60160, "confirmatoria"), (69001, 69001, "M1, gate G1"),
    (80001, 82004, "linhagem E1 (piloto, genomas e ambientes)"),
    (20260900, 20261800, "fala, voz, comando e bootstraps (sementes de 2026-09/10 e semente + i)"),
)


def unidades_derivadas(bases, k_por_base: int, prefixo: str = "experimento-maior") -> list[dict]:
    """E3 (plano do experimento maior, secao 8.1): a unidade k da base b tem semente derivar_semente(prefixo, b, k) e genoma
    derivar_semente(prefixo + "-genoma", b, k), k = 0..K-1; o prefixo e o do plano (PREFIXOS_UNIDADES: "experimento-maior", o
    padrao; "n6"; "n7"). Falha alto com K < 1, base repetida, prefixo desconhecido ou colisao."""
    if prefixo not in PREFIXOS_UNIDADES:
        raise ValueError(f"prefixo das unidades {prefixo!r}: so {PREFIXOS_UNIDADES}")
    if k_por_base < 1:
        raise ValueError("K precisa ser >= 1")
    bases = list(bases)
    if len(set(bases)) != len(bases):
        raise ValueError(f"base repetida: {bases}")
    out = [{"base": b, "k": k, "semente": derivar_semente(prefixo, b, k),
            "genoma": derivar_semente(f"{prefixo}-genoma", b, k)} for b in bases for k in range(k_por_base)]
    valores = [u["semente"] for u in out] + [u["genoma"] for u in out]
    if len(set(valores)) != len(valores):
        raise ValueError("colisao entre sementes e genomas derivados")
    return out


def na_faixa_reservada(valor: int) -> str | None:
    for lo, hi, fonte in FAIXAS_RESERVADAS:
        if lo <= valor <= hi:
            return fonte
    return None


class ReplayDivergiu(RuntimeError):
    pass


class SementeSemPlano(RuntimeError):
    pass


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
}
FONTES_IMPLEMENTADAS = ("nenhuma", "dono", "consequencia", "informacao")
# o que os bracos do N6 e do N7 esperam de outros chats; um braco que depende de uma peca daqui falha alto com o no. A entrada sai
# daqui quando a peca estiver na main (e os testes de tests/test_bancada_n6_n7.py dizem o que conferir entao).
# Vazio desde a BANCADA-LIGA-N6-N7: a memoria (CEREBRO-N6-N7, #167) e o pedido (N7-MUNDO, #166) estao na main. Fica a tabela para a
# proxima peca de outro chat (o K4 e os canais, rodada 10).
NOS_PENDENTES: dict = {}
# filtros do acoplado que dependem de eventos que ainda nao existem (nenhum hoje)
FILTROS_PENDENTES: dict = {}
# a memoria de cada braco do N6 no cerebro: o M0 guarda e nao age (ganho 0, N6-2/N6-3); o ME com o desarranjo da vida (N6-6)
MODO_MEMORIA = {"nenhuma": "relevante", "relevante": "relevante", "recencia": "recencia", "embaralhada": "embaralhada"}
CONFIG_LOBOS_PADRAO = ConfigLobos()
APRENDE_PELA_CONSEQUENCIA = ("consequencia", "informacao")   # o P2 e o P1 com a informacao na percepcao (plano do N5, secao 3)


def braco_de(rotulo: str) -> Braco:
    if rotulo not in BRACOS:
        raise KeyError(f"braco desconhecido {rotulo!r}: {sorted(BRACOS)}")
    b = BRACOS[rotulo]
    if b.fonte not in FONTES_IMPLEMENTADAS:
        raise NotImplementedError(f"braco {b.rotulo}: a fonte {b.fonte!r} chega no {b.no} (docs/ROADMAP_V2.md)")
    for peca, presente in (("memoria", b.memoria is not None), ("pedido", b.pedido)):
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
    nada: a vida do P3 e byte a byte a da L1 e a do P0 a do instinto (testes)."""

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
            self.sinais_entregues += acao.value in SINAIS
            self.cerebro.receber_acao_dono(acao, tick)
        elif self.braco.fonte not in ("nenhuma",) + APRENDE_PELA_CONSEQUENCIA:   # pragma: no cover - braco_de ja barra
            raise NotImplementedError(self.braco.fonte)
        # informacao: nada do dono chega ao aprendiz por aqui (o MotorFrutas nem chama o gancho para informar; plano do N5, secao 3)

    def estado_interno(self) -> dict:
        return {**self.cerebro.estado_interno(), "bancada": {"braco": self.braco.rotulo, "fonte": self.braco.fonte}}

    def __getattr__(self, nome):
        cerebro = self.__dict__.get("cerebro")
        if cerebro is None:
            raise AttributeError(nome)
        return getattr(cerebro, nome)


# ------------------------------------------------------------------ a vida


@dataclass(frozen=True)
class EspecVida:
    dono: str
    braco: str
    semente: int
    genoma: int | None = None
    mundo: str = "padrao"
    cerebro: str = "lobos"

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "padrao" else f"~{self.mundo}"
        g = "" if self.genoma is None else f"~g{self.genoma}"
        c = "" if self.cerebro == "lobos" else f"~{self.cerebro}"
        return f"{self.dono}-{self.braco}{c}{m}{g}@{self.semente}"

    @property
    def celula(self) -> tuple:
        """O que define o par de vidas que se comparam entre bracos: tudo menos o braco."""
        return (self.dono, self.semente, self.genoma, self.mundo, self.cerebro)

    @property
    def condicao(self) -> str:
        return mundo_de(self.mundo).condicao


@dataclass
class VidaBancada:
    espec: EspecVida
    motor: MotorComFeedback
    interacoes: int                  # acoes do dono no log, fora os eventos do mundo
    origem: str | None = None        # so no modo acoplado: o nome da vida de origem, o braco dela e o filtro
    origem_braco: str | None = None
    filtro: str | None = None
    broncas: int = 0                 # N7: as broncas do pedido no registro (repreender pelo canal do mundo, fora do orcamento)
    julgamentos: int = 0             # K4: os julgamentos da fruta no registro (elogiar/repreender pelo canal do mundo)

    @property
    def rotulo_braco(self) -> str:
        """O braco na tabela: "P3", ou "P0<P3:sem_sinais" para o P0 acoplado ao registro do P3 sem os sinais."""
        b = self.espec.braco if self.espec.cerebro == "lobos" else f"{self.espec.braco}~{self.espec.cerebro}"
        if self.origem is None:
            return b
        return f"{b}<{self.origem_braco}:{self.filtro}"

    @property
    def eventos_mundo(self) -> int:
        return contar_acoes(self.motor.log)[1]

    @property
    def informacoes(self) -> int:
        return contar_informacoes(self.motor.log)

    @property
    def pedidos(self) -> int:
        return contar_pedidos(self.motor.log)

    @property
    def nome(self) -> str:
        if self.origem is None:
            return self.espec.nome
        e = self.espec
        return replace(e, braco=f"{e.braco}~de-{self.origem_braco}-{self.filtro}").nome


def filtrar_log(log: LogDeEventos, retirar: frozenset) -> LogDeEventos:
    """O mesmo log sem as acoes do dono em `retirar` (valores de AcaoUsuario); avancos, eventos do mundo e as outras acoes nos
    mesmos ticks. Tirar um evento do mundo falha alto: o acoplado reproduz o mundo da origem."""
    if retirar & EVENTOS_DO_MUNDO:
        raise ValueError(f"o filtro tiraria eventos do mundo: {sorted(retirar & EVENTOS_DO_MUNDO)}")
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in retirar)])


def contar_acoes(log: LogDeEventos) -> tuple[int, int]:
    """(acoes do dono no orcamento, eventos do mundo). As informacoes (fora do orcamento, sem ser mundo) nao entram em nenhuma das
    duas: contar_informacoes."""
    dono = mundo = 0
    for e in log:
        if e.tipo == "acao_usuario":
            if str(e.valor) in EVENTOS_DO_MUNDO:
                mundo += 1
            elif str(e.valor) not in INFORMACOES and str(e.valor) not in PEDIDOS:
                dono += 1
    return dono, mundo


def contar_pedidos(log: LogDeEventos) -> int:
    return sum(1 for e in log if e.tipo == "acao_usuario" and str(e.valor) in PEDIDOS)


def contar_informacoes(log: LogDeEventos) -> int:
    return sum(1 for e in log if e.tipo == "acao_usuario" and str(e.valor) in INFORMACOES)


def resumo_motor(motor) -> tuple:
    """Tudo que uma vida produz: log, estado final, acoes do pet, as rngs e, no motor de personalidade, obediencia, recusas,
    desejos e vinculo."""
    extra = ()
    if isinstance(motor, MotorPersonalidade):
        extra = (motor._rng_obediencia.getstate(), [r.para_dict() for r in motor.recusas],
                 [d.para_dict() for d in motor.desejos], motor.vinculo.para_dict())
    if isinstance(motor, MotorAmbiente):
        bola = motor.resumo_bola() if motor.cb.ligada else {"ligada": False, "contagem": dict(motor.contagem_bola)}
        extra = extra + (bola, dict(motor.contagem), motor.morte)
    if isinstance(motor, MotorFrutas):
        extra = extra + (motor.resumo_frutas(),)
    if isinstance(motor, MotorFrutasMundo):
        extra = extra + (motor.resumo_mundo(),)
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), *extra)


def _interno(motor) -> str:
    return json.dumps(motor.politica.estado_interno(), sort_keys=True)


@dataclass(frozen=True)
class Bancada:
    dias: int
    orcamento: int
    cfg_lobos: ConfigLobos = CONFIG_LOBOS_APRENDIZ    # o aprendiz de todos os bracos (o P0 o usa com o aprendizado desligado)
    cfg_bola: ConfigBola = CONFIG_BOLA_LIGADA          # a bola dos mundos da bola (padroes calibrados na A1)
    cfg_consequencia: ConfigConsequencia = CONFIG_CONSEQUENCIA    # o sinal do P1 (N3)
    cfg_frutas: ConfigFrutas = CONFIG_FRUTAS_LIGADA    # as frutas dos mundos das frutas (padroes calibrados no N4)
    cfg_informacao: ConfigInformacao = CONFIG_INFORMACAO_LIGADA   # o canal da informacao, ligado em todo mundo das frutas (N5)
    cfg_pedido: ConfigPedido = CONFIG_PEDIDO_LIGADA      # N7: o pedido, ligado so no motor dos bracos com pedido
    julgamento_fruta: bool = False                       # K4: o dono dos bracos com fonte dono julga a fruta, fora do orcamento
    montagem: str = MONTAGEM_PADRAO                      # BANCADA-MONTAGEM: "simples" (a de antes) ou "completa" (o cerebro A da secao 1)

    def __post_init__(self) -> None:
        if self.dias <= 0 or self.orcamento <= 0:
            raise ValueError("dias e orcamento precisam ser positivos")
        if not self.cfg_lobos.aprendizado_ligado:
            raise ValueError("cfg_lobos e a do aprendiz (aprendizado ligado); o P0 desliga por conta propria")
        if not self.cfg_bola.ligada:
            raise ValueError("cfg_bola e a dos mundos da bola: ligada (o mundo padrao nao usa bola)")
        if not self.cfg_frutas.ligada:
            raise ValueError("cfg_frutas e a dos mundos das frutas: ligada")
        if not self.cfg_informacao.ligada:
            raise ValueError("cfg_informacao e a dos mundos das frutas: ligada (sem informante, nada muda na vida)")
        if not self.cfg_pedido.ligada:
            raise ValueError("cfg_pedido e a dos bracos com pedido: ligada")
        if self.montagem not in MONTAGENS:
            raise ValueError(f"montagem {self.montagem!r}: so {MONTAGENS}")

    def braco(self, espec: EspecVida) -> Braco:
        """O braco da vida com as pecas da montagem da bancada (braco_montado)."""
        return braco_montado(braco_de(espec.braco), self.montagem, mundo_de(espec.mundo).frutas)

    @property
    def tick_troca(self) -> int:
        """o mutavel troca na metade da vida (no fim do dia dias // 2: dia 7 numa vida de 14; plano, secao 4.3)"""
        if self.dias < 2:
            raise ValueError("o mutavel precisa de pelo menos 2 dias")
        return (self.dias // 2) * TICKS_POR_DIA

    def janelas_frutas(self, condicao: str) -> dict:
        """as janelas da taxa_fruta_ruim (plano, secao 4.3): inicio e final (as duas metades da vida), antes e depois da troca no
        mutavel, e uma por dia (a curva)"""
        metade, fim = (self.dias // 2) * TICKS_POR_DIA, self.dias * TICKS_POR_DIA
        j = {"total": (0, fim), "inicio": (0, metade), "final": (metade, fim)}
        if condicao == "mutavel":
            j["antes_da_troca"] = (0, self.tick_troca)
            j["depois_da_troca"] = (self.tick_troca, fim)
        for d in range(self.dias):
            j[f"dia_{d + 1}"] = (d * TICKS_POR_DIA, (d + 1) * TICKS_POR_DIA)
        return j

    # ------------------------------------------------------------- fabricas

    def politica(self, espec: EspecVida, cfg=None) -> PoliticaDoBraco:
        if espec.cerebro not in CEREBROS:
            raise KeyError(f"cerebro {espec.cerebro!r}: so {CEREBROS} (outros cerebros sao a comparacao do N11)")
        b = braco_de(espec.braco)
        mundo = mundo_de(espec.mundo)
        if b.fonte == "informacao" and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a informacao e sobre as frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        if (b.memoria is not None or b.pedido) and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a memoria e o pedido sao das frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        if espec.cerebro == "instinto":
            if b.fonte != "nenhuma" or b.memoria is not None or b.pedido:
                raise ValueError(f"cerebro instinto so no P0 (nao aprende, nao lembra, nao le o pedido): braco {b.rotulo}")
            if mundo.frutas:
                return PoliticaDoBraco(PoliticaInstintoFrutas(cfg, CONFIG_BOLA, self.cfg_frutas), b)
            if mundo.bola is not None:
                return PoliticaDoBraco(PoliticaInstintoBola(cfg, self.cfg_bola), b)
            return PoliticaDoBraco(PoliticaInstinto(cfg), b)
        b = self.braco(espec)       # a montagem (BANCADA-MONTAGEM); na simples, o proprio braco
        cl = self.cfg_lobos if b.fonte != "nenhuma" else replace(self.cfg_lobos, aprendizado_ligado=False)
        cl = cfg_lobos_do_braco(cl, b, espec.semente, self.montagem)
        # LOBOS-MUNDO (#141): os lobos veem o mundo em que vivem; no padrao, nenhuma chave (as formas de antes)
        cb = self.cfg_bola if mundo.bola is not None else None
        cf = self.cfg_frutas if mundo.frutas else None
        # canais (#169): o braco que os fixa (as ablacoes da K-7) manda; os outros seguem a config
        cc = self.cfg_consequencia if b.canais is None else replace(self.cfg_consequencia, canais_ligados=b.canais)
        return PoliticaDoBraco(PoliticaLobos(cfg, cl, cfg_bola=cb, cfg_frutas=cf), b, cc)

    def fabrica_politica(self, espec: EspecVida):
        return lambda cfg=None: self.politica(espec, cfg)

    def fabrica_motor(self, espec: EspecVida):
        mundo = mundo_de(espec.mundo)
        if mundo.frutas:
            # o desenho do N4 (plano, secao 3): MotorFrutas, obediencia, educacao, lesoes e bola desligadas, especie brasa; o genoma
            # das frutas (preferencia inata, neofobia) sai do genoma da vida, ou da semente sem genoma (o padrao do MotorFrutas)
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cf, ci, condicao = self.cfg_frutas, self.cfg_informacao, mundo.condicao
            troca = self.tick_troca if condicao == "mutavel" else None
            # N7: a chave do pedido so no motor dos bracos com pedido (com ela o estado() ganha pedido e desobediencias; nos outros, o
            # motor de hoje, e um pedido no registro falha alto)
            cp = self.cfg_pedido if braco_de(espec.braco).pedido else None
            # K4: com o julgamento, o motor dos bracos com fonte dono expoe os consumos (estado()["consumos_frutas"]) para o julgador
            cj = CONFIG_JULGAMENTO_FORA if self.julga_fruta(espec) else None
            return lambda politica, cfg, semente: MotorFrutasMundo(
                politica, cfg, semente, temperamento, "brasa", obediencia_desligada=True, cfg_bola=CONFIG_BOLA, cfg_frutas=cf,
                semente_genoma=espec.genoma, condicao=condicao, tick_troca=troca, cfg_informacao=ci, cfg_pedido=cp,
                cfg_julgamento=cj)
        if mundo.bola is not None:
            # o desenho da A1 (plano, secao 3): MotorAmbiente, obediencia, educacao e lesoes desligadas, especie brasa
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cb = self.cfg_bola
            return lambda politica, cfg, semente: MotorAmbiente(politica, cfg, semente, temperamento, "brasa",
                                                                obediencia_desligada=True, cfg_bola=cb)
        if espec.genoma is None:
            return lambda politica, cfg, semente: MotorComFeedback(politica=politica, cfg=cfg, semente=semente)
        temperamento = sortear_temperamento(espec.genoma)
        return lambda politica, cfg, semente: MotorPersonalidade(politica, cfg, semente, temperamento)

    # ------------------------------------------------------------- vidas

    def vida(self, espec: EspecVida) -> VidaBancada:
        mundo = mundo_de(espec.mundo)
        fm = self.fabrica_motor(espec)
        rotulo = f"{espec.dono}-{espec.braco}"
        broncas = 0                              # N7: as broncas do pedido (so no P3+ped), que vem pelo canal do mundo
        julgamentos = 0                          # K4: os julgamentos da fruta, tambem pelo canal do mundo
        if mundo.bola == "a1":
            # como a A1 rodou: o dono embrulhado poe a bola DENTRO do orcamento; o aleatorio sorteia por_bola
            v = simular_vida(rotulo, DonoComBola(espec.dono, self.cfg_bola), self.politica(espec, CONFIG_PADRAO),
                             espec.semente, self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm)
            motor = v.motor
        elif mundo.bola == "b1b2":
            motor = simular_vida_mundo(criar_dono(espec.dono), RegraBola(espec.dono, self.cfg_bola),
                                       self.politica(espec, CONFIG_PADRAO), espec.semente, self.dias, self.orcamento,
                                       espec.dono, fm)
        elif mundo.frutas:
            regra = CalendarioFrutas(espec.semente, self.cfg_frutas)
            b = braco_de(espec.braco)
            julga = RegraFrutasComJulgador(regra, self.julgador(espec)) if self.julga_fruta(espec) else None
            regra = julga or regra
            if b.fonte == "informacao" and b.informacao != "depois":     # o P2d nao tem o informante da oferta: o julgador e o dele
                regra = RegraFrutasComInformante(regra, self.informante(espec))
            if b.pedido:
                regra = RegraFrutasComPedinte(regra, self.pedinte(espec))
            motor = simular_vida_mundo(criar_dono(espec.dono), regra, self.politica(espec, CONFIG_PADRAO), espec.semente,
                                       self.dias, self.orcamento, espec.dono, fm)
            broncas = len(regra.pedinte.broncas) if b.pedido else 0
            # so o julgamento como feedback (elogiar/repreender) e julgamento; como informacao, conta em `informacoes` (o log)
            julgamentos = julga.feitos if julga is not None and julga.julgador.saida == "feedback" else 0
        else:
            motor = simular_vida(rotulo, criar_dono(espec.dono), self.politica(espec, CONFIG_PADRAO), espec.semente,
                                 self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm).motor
        dono, eventos_mundo = contar_acoes(motor.log)
        dono -= broncas + julgamentos            # a bronca do pedido e o julgamento sao feedback no log, mas vieram pelo mundo
        orcamento_gasto = dono + (eventos_mundo if mundo.bola == "a1" else 0)
        if orcamento_gasto != self.orcamento:
            raise RuntimeError(f"{espec.nome}: {orcamento_gasto} interacoes no orcamento, orcamento {self.orcamento}")
        vida = VidaBancada(espec, motor, dono, broncas=broncas, julgamentos=julgamentos)
        self.conferir_replay(vida)
        return vida

    def efeitos_reais(self, espec: EspecVida) -> dict:
        """o efeito real de cada fruta no mundo da vida (E7: o que o dono informante sabe): {"antes": ..., "depois": ...}; "depois"
        so no mutavel (o descasado, a partir de tick_troca)"""
        mundo = mundo_de(espec.mundo)
        if not mundo.frutas:
            raise ValueError(f"sem frutas no mundo {espec.mundo!r}")
        g = genoma_frutas(espec.semente if espec.genoma is None else espec.genoma, self.cfg_frutas)
        if mundo.condicao == "mutavel":
            return {"antes": efeitos_da_condicao(g, self.cfg_frutas, "casado"),
                    "depois": efeitos_da_condicao(g, self.cfg_frutas, "descasado")}
        return {"antes": efeitos_da_condicao(g, self.cfg_frutas, mundo.condicao), "depois": None}

    def informante(self, espec: EspecVida):
        """o informante do braco: P2 `certo`, P2e `errado` (DonoInformante de frutas.py, com o efeito real do mundo da bancada) e P2a
        acoplado (InformanteAcoplado: o multiconjunto do P2 em ticks sorteados)"""
        b = braco_de(espec.braco)
        if b.fonte != "informacao":
            raise ValueError(f"braco {b.rotulo} nao tem informante")
        ef = self.efeitos_reais(espec)
        troca = self.tick_troca if ef["depois"] is not None else None
        if b.informacao == "acoplada":
            return InformanteAcoplado(espec.semente, self.dias, self.cfg_frutas, ef, troca)
        if b.informacao == "depois":
            raise ValueError(f"braco {b.rotulo}: a informacao dele e o julgador com saida informacao (Bancada.julgador), nao um informante")
        modo = {"certa": "certo", "errada": "errado"}[b.informacao]
        return InformanteDoMundo(modo, ef, troca)

    def julga_fruta(self, espec: EspecVida) -> bool:
        """K4: o dono desta vida julga a fruta? Nos mundos das frutas: os bracos com fonte dono (o P3, o P3i, o P3+ped) com a chave
        julgamento_fruta; o P2d sempre (o julgador com saida "informacao" e o informante dele, P2D-P3I)."""
        if not mundo_de(espec.mundo).frutas:
            return False
        b = braco_de(espec.braco)
        return b.informacao == "depois" or (self.julgamento_fruta and b.fonte == "dono")

    def saida_julgamento(self, espec: EspecVida) -> str:
        """A saida do JulgadorFruta da vida: "informacao" no P2d e no P3i (P2D-P3I, parte A), "feedback" (o K4) nos outros."""
        b = braco_de(espec.braco)
        return "informacao" if (b.informacao == "depois" or b.julgamento == "informacao") else "feedback"

    def julgador(self, espec: EspecVida) -> JulgadorFruta:
        """K4 (contrato K4, E7): o conhecimento do dono do P3 sao os efeitos reais da bancada, os mesmos que o informante do P2 recebe
        (e a troca do mutavel); o julgamento sai fora do orcamento (CONFIG_JULGAMENTO_FORA)."""
        if not self.julga_fruta(espec):
            raise ValueError(f"{espec.nome}: sem julgamento da fruta (chave julgamento_fruta, mundo das frutas, braco com fonte dono "
                             "ou o P2d)")
        ef = self.efeitos_reais(espec)
        troca = self.tick_troca if ef["depois"] is not None else None
        return JulgadorFruta(ef["antes"], ef["depois"], troca, CONFIG_JULGAMENTO_FORA, saida=self.saida_julgamento(espec))

    def pedinte(self, espec: EspecVida) -> DonoPedinte:
        """N7: o dono que pede da unidade (a fruta X pela semente, N7-6), com a bronca da desobediencia so no P3+ped (fonte dono, N7-8)."""
        b = braco_de(espec.braco)
        if not b.pedido:
            raise ValueError(f"braco {b.rotulo} nao tem pedido")
        return DonoPedinte.da_semente(espec.semente, self.cfg_pedido, bronca=b.fonte == "dono")

    def rejogar(self, log: LogDeEventos, espec: EspecVida):
        fp, fm = self.fabrica_politica(espec), self.fabrica_motor(espec)
        if mundo_de(espec.mundo).ambiente:
            return reproduzir_ambiente(log, fp, semente=espec.semente, fabrica_motor=fm)
        return reproduzir_com_feedback(log, fp, semente=espec.semente, fabrica_motor=fm)

    def acoplar(self, origem: VidaBancada, braco: str, filtro: str) -> VidaBancada:
        """Modo acoplado (malha aberta): o registro da vida de origem, sem as acoes do filtro, rejogado com o cerebro de outro
        braco (ou do mesmo). Os eventos sao os da origem nos mesmos ticks; so o cerebro (e o que ele faz deles) muda."""
        retirar = filtro_de(filtro)
        if origem.origem is not None:
            raise ValueError("acoplar uma vida ja acoplada nao e suportado: acople a partir da vida de origem")
        log = filtrar_log(origem.motor.log, retirar)
        espec = replace(origem.espec, braco=braco)
        m = self.rejogar(log, espec)
        # as broncas do pedido e os julgamentos da fruta (feedback pelo canal do mundo) ficam no registro so se o filtro nao tira os
        # sinais; um filtro que tirasse so um dos dois deixaria a conta sem como separar o que veio do dono
        if (origem.broncas or origem.julgamentos) and len(JULGAMENTOS & retirar) == 1:
            raise ValueError(f"filtro {filtro!r} tira so parte dos sinais: as broncas e os julgamentos da origem nao se separam")
        fica = not (JULGAMENTOS & retirar)
        broncas, julgamentos = (origem.broncas, origem.julgamentos) if fica else (0, 0)
        vida = VidaBancada(espec, m, contar_acoes(log)[0] - broncas - julgamentos, origem=origem.nome,
                           origem_braco=origem.rotulo_braco, filtro=filtro, broncas=broncas, julgamentos=julgamentos)
        self.conferir_replay(vida)
        return vida

    def conferir_replay(self, vida: VidaBancada, texto_log: str | None = None) -> None:
        """G1: rejoga a vida a partir do log serializado (do disco, se vier o texto) e compara tudo bit a bit."""
        texto = vida.motor.log.para_jsonl() if texto_log is None else texto_log
        if texto != vida.motor.log.para_jsonl():
            raise ReplayDivergiu(f"{vida.nome}: o log do disco nao e o da vida")
        r = self.rejogar(LogDeEventos.de_jsonl(texto), vida.espec)
        if resumo_motor(r) != resumo_motor(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: log, estado, acoes ou rngs divergem no replay")
        if _interno(r) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: estado interno da politica diverge no replay")

    # ------------------------------------------------------------- medidas

    def medir(self, vida: VidaBancada, sonda: dict, piso: float | None = None, taxa_p0: float | None = None) -> dict:
        """Desempenho no ambiente, acerto na tarefa e custo da plasticidade de uma vida. `piso` = acerto total do P0 na mesma
        celula (o prior herdado); sem ele, o da propria vida. O replay de medicao e conferido bit a bit contra a vida."""
        regs = []

        def fab(cfg=None):
            reg = _Registro(self.politica(vida.espec, cfg))
            regs.append(reg)
            return reg

        m = reproduzir_com_feedback(LogDeEventos.de_jsonl(vida.motor.log.para_jsonl()), fab, semente=vida.espec.semente,
                                    fabrica_motor=self.fabrica_motor(vida.espec))
        if resumo_motor(m) != resumo_motor(vida.motor) or _interno(m) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou a vida")
        reg = regs[0]
        bola = None
        if isinstance(m, MotorAmbiente):
            tick = CONFIG_PADRAO.intervalo_decisao_ticks
            bola = {"resposta": resposta_a_bola([(k * tick, b, r, a) for k, (b, r, a) in enumerate(reg.bola)]),
                    "contagem": dict(m.contagem_bola)}
        frutas = None
        if isinstance(m, MotorFrutasMundo):
            consumos = [(c["tick"], c["efeito_humor"]) for c in m.consumos]
            taxas = taxa_fruta_ruim(consumos, self.janelas_frutas(m.condicao))
            dias = [taxas[f"dia_{d + 1}"] for d in range(self.dias)]
            if taxa_p0 is None and vida.espec.braco == "P0" and vida.origem is None:
                taxa_p0 = taxas["total"]["taxa"]                    # o P0 e a propria referencia
            if m.condicao == "iguais":
                taxa_p0 = None                                      # sem fruta ruim, sem caminho ate a metade (sem_referencia)
            frutas = {"taxa_fruta_ruim": taxas, "consumos": len(consumos), "contagem": dict(m.contagem_frutas),
                      "mundo": m.resumo_mundo(), "genoma": m.genoma.para_dict(),
                      "consumos_ate_metade": consumos_ate_metade([x["taxa"] for x in dias], [x["n"] for x in dias], taxa_p0),
                      "informacoes": [dict(i) for i in m.informacoes],
                      "multiconjunto_informacoes": multiconjunto_informacoes(m.informacoes),
                      "decisoes_com_informacao": m.decisoes_com_informacao}
        n6 = self.medidas_n6(vida, m, reg) if isinstance(m, MotorFrutasMundo) else None
        n7 = self.medidas_n7(vida, m, reg) if isinstance(m, MotorFrutasMundo) else None
        desempenho = desempenho_no_ambiente(reg.amostras)
        humor = privacao_nas_decisoes(reg.vetores, CONFIG_PADRAO.limiar_privacao)["humor_medio"]
        tarefa = acerto_na_tarefa(reg.decisoes, _julgar, ACOES, TICKS_POR_DIA)
        sinais = []
        for d in tarefa["dias"]:
            ate = [s for (t, _, _), s in zip(reg.decisoes, reg.sinais_na_decisao) if t < (d + 1) * TICKS_POR_DIA]
            sinais.append(ate[-1] if ate else 0)
        deriva = self.deriva(vida, sonda)
        custo = custo_da_plasticidade(deriva, tarefa["acerto"], sinais,
                                      tarefa["acerto_total"] if piso is None else piso)
        return {"vida": vida.nome, "braco": vida.rotulo_braco, "fonte": braco_de(vida.espec.braco).fonte,
                "cerebro": vida.espec.cerebro, "dono": vida.espec.dono, "semente": vida.espec.semente,
                "genoma": vida.espec.genoma, "mundo": vida.espec.mundo, "condicao": vida.espec.condicao,
                "origem": vida.origem, "filtro": vida.filtro, "interacoes": vida.interacoes,
                "eventos_mundo": vida.eventos_mundo, "informacoes": vida.informacoes, "bola": bola, "frutas": frutas,
                "pedidos": vida.pedidos, "broncas": vida.broncas, "julgamentos": vida.julgamentos, "n6": n6, "n7": n7,
                "humor_medio": humor,
                **desempenho, "acerto_total": tarefa["acerto_total"], "acerto_por_dia": tarefa["acerto"],
                "teto_total": tarefa["teto_total"], "sinais_total": reg.sinais, "sinais_do_dono": reg.sinais_do_dono,
                "sinais_acumulados": sinais,
                "deriva_final": custo["deriva_final"], "custo_da_plasticidade": custo}

    def medidas_n6(self, vida: VidaBancada, motor, reg: "_Registro") -> dict | None:
        """N6 (plano, secoes 6 e 7), nos bracos de memoria: as sub-decisoes da fruta com a sonda contrafactual que o cerebro grava no
        motivo (`fruta.sonda_memoria`: a escolha com m = 0 e o mesmo u), a fracao decidida pela memoria (G-CITA), a cobertura, a
        ocupacao dos espacos por decisao e as verificacoes exatas dos marcos 1 e 2 (todo consumo virou um episodio da mesma fruta, na
        mesma ordem). Fora dos bracos de memoria, None."""
        if self.braco(vida.espec).memoria is None:      # na montagem completa, tambem P1 a P3 nos mundos das frutas
            return None
        cerebro = reg.interna.cerebro
        interno = cerebro.estado_interno()
        subs = []
        for mot in cerebro.motivos:
            fr = mot.get("fruta")
            if fr is None:
                continue
            mem = fr.get("memoria_emocao")
            if mem is None:
                raise RuntimeError(f"{vida.nome}: sub-decisao sem o registro da memoria com a memoria ligada")
            sonda = fr.get("sonda_memoria")
            if (sonda is None) != (len(fr["presentes"]) < 2):
                raise RuntimeError(f"{vida.nome}: a sonda da memoria tem de existir so com duas frutas ou mais")
            recuperados = sum(1 for v in mem.values() if v["episodio"] is not None)
            subs.append((len(fr["presentes"]), fr["escolhida"], sonda["escolha_sem_memoria"] if sonda else fr["escolhida"],
                         recuperados))
        r = memoria_nas_subdecisoes(subs, len(cerebro.motivos))
        contagem = interno["memoria"]["sondas"]
        if (r["subdecisoes_2_mais"], r["mudou"]) != (contagem["subdecisoes_2mais"], contagem["mudou"]):
            raise RuntimeError(f"{vida.nome}: as sondas do motivo e as contagens do cerebro divergem")
        episodios = interno["memoria"]["episodios"]
        consumos = motor.consumos
        return {**r, "modo": interno["memoria"]["modo"], "ganho": interno["memoria"]["ganho"],
                "ocupacao": ocupacao_espacos_frutas(reg.espacos, FRUTAS),
                "marcos": {"consumos": len(consumos), "episodios": len(episodios),
                           "episodio_por_consumo": [e["fruta"] for e in episodios] == [c["fruta"] for c in consumos],
                           "contagem": dict(interno["memoria"]["contagem"])}}

    def medidas_n7(self, vida: VidaBancada, motor, reg: "_Registro") -> dict | None:
        """N7 (plano, secao 6), nos bracos com pedido e nos acoplados a um deles: a fruta X da unidade, as decisoes de conflito com a sonda
        "quem decidiu" que o cerebro grava no motivo (`pedido.acao_sem_pedido`: a acao com o mesmo u e sem o termo), a deferencia por zona
        e janela (dias 1..metade e metade..dias_pedido do pedido; a extincao depois), as violacoes das regras urgentes (G-URG), a fracao
        de X nas ofertas com X e outra fruta, as desobediencias, e a trajetoria diaria de w_pedido com o dia em que cruza o zero. A decisao
        k cai no tick k x intervalo_decisao_ticks. Fora disso, None."""
        de_pedido = braco_de(vida.espec.braco).pedido or (vida.origem_braco is not None and
                                                          BRACOS.get(vida.origem_braco.split("<")[0], BRACOS["P0"]).pedido)
        if not de_pedido:
            return None
        cerebro = reg.interna.cerebro
        passo = CONFIG_PADRAO.intervalo_decisao_ticks
        T, cp = TICKS_POR_DIA, self.cfg_pedido
        fim, fim_pedidos = self.dias * T, min(cp.dias_pedido, self.dias) * T
        metade = min(cp.dias_pedido // 2, self.dias) * T
        janelas = {"inicial": (0, metade), "final": (metade, fim_pedidos), "extincao": (fim_pedidos, fim)}
        decisoes, consumos = [], []
        for k, mot in enumerate(cerebro.motivos):
            ped = mot.get("pedido")
            if ped is not None:
                decisoes.append((k * passo, mot["regra"], mot["regra"] in ZONAS_CONFLITO and ped["p"] == -1.0,
                                 mot["acao"] == AcaoPet.COMER.value, ped["acao_sem_pedido"] == AcaoPet.COMER.value))
            fr = mot.get("fruta")
            if fr is not None:
                consumos.append((k * passo, fr["escolhida"], fr["presentes"]))
        x = DonoPedinte.sortear_fruta(vida.espec.semente)
        estado = motor.estado()
        serie = None
        interno = cerebro.estado_interno()
        if "peso_pedido" in interno:
            if interno["aprendizado_ligado"]:
                fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
                serie = [do_braco(politica_no_tick(vida.motor.log, fab, vida.espec.semente, d * T, fm)).cerebro
                         .estado_interno()["peso_pedido"] for d in range(1, self.dias + 1)]
            else:
                serie = [interno["peso_pedido"]] * self.dias
        return {"fruta_x": x, "janelas": janelas, "deferencia": deferencia_ao_pedido(decisoes, janelas),
                "fracao_x": fracao_da_fruta(consumos, x, janelas), "desobediencias": estado.get("desobediencias"),
                "pedidos": vida.pedidos, "broncas": vida.broncas, "w_pedido_por_dia": serie,
                "dia_w_pedido_cruza_zero": dia_cruza_zero(serie) if serie else None}

    def deriva(self, vida: VidaBancada, sonda: dict) -> list[float]:
        """JSD (bits) entre a politica no fim de cada dia e a do prior herdado (o P0 da mesma vida), nas mesmas sondas."""
        estados = estados_sonda(sonda["estados"], sonda["semente"])
        prior = self.politica(replace(vida.espec, braco="P0"), CONFIG_PADRAO)
        d_prior = distribuicoes_de_acao(prior, estados, sonda["amostras"], sonda["semente"])
        fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
        log = vida.motor.log
        serie = []
        for d in range(1, self.dias + 1):
            # a sonda le o cerebro do braco direto: o embrulho da bola mexeria no motor e poria a bola nos estados da sonda
            pol = do_braco(politica_no_tick(log, fab, vida.espec.semente, d * TICKS_POR_DIA, fm))
            serie.append(jsd_media(distribuicoes_de_acao(pol, estados, sonda["amostras"], sonda["semente"]), d_prior))
        return serie


def do_braco(politica) -> PoliticaDoBraco:
    """A PoliticaDoBraco dentro dos embrulhos dos motores (bola, personalidade)."""
    p = politica
    while not isinstance(p, PoliticaDoBraco):
        if isinstance(p, _Espiao):
            p = p.interna
        elif isinstance(p, _PoliticaComFrutas):
            p = p._pf
        elif isinstance(p, _PoliticaComBola):
            p = p._pb
        elif isinstance(p, _PoliticaObservada):
            p = p._p
        else:
            raise TypeError(f"politica sem PoliticaDoBraco dentro: {type(p).__name__}")
    return p


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
                       fabrica_motor):
    """treino.simular_vida com um canal do MUNDO fora do orcamento (B2): a cada passo o dono age pelo CanalDeInteracao (o
    orcamento exato de sempre) e depois a regra do mundo poe o que pos, direto no motor (entra no log, nao no canal). O dono
    nao ve os eventos do mundo no gasto do orcamento. Mesma rng do dono que simular_vida (derivada de semente e rotulo_dono)."""
    cfg, cd = CONFIG_PADRAO, CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cd.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cd.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono))
    canal = CanalDeInteracao(motor, orcamento, cd.max_interacoes_por_passo)
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
        mem = getattr(self.interna.cerebro, "_memoria", None)   # N6, so le: a memoria dos lobos depois de promover (o que a decisao viu)
        if mem is not None:
            self.espacos.append((tuple(e["fruta"] for e in mem.curto), tuple(e["fruta"] for e in mem.longo)))
        return acao

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self._tick_ultimo_cuidado = tick          # toda acao do dono zera o relogio de cuidado (state.aplicar_acao_usuario)
        self.sinais_do_dono += acao.value in SINAIS
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _julgar(estado: dict, acao: str) -> int:
    return julgar_acao({**estado, "acao_atual": acao}, CONFIG_DONOS)


# ------------------------------------------------------------------ orquestrador


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def validar_config(cfg: dict) -> dict:
    faltam = {"bracos", "donos", "dias", "orcamento", "sonda", "bootstrap"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config: ou 'sementes' (x 'genomas') ou 'unidades' (bases x K derivadas), um dos dois")
    if "unidades" in cfg:
        u = cfg["unidades"]
        if not {"bases", "k"} <= set(u) <= {"bases", "k", "prefixo"} or "genomas" in cfg:
            raise ValueError(f"unidades fora do formato {{'bases': [...], 'k': K, 'prefixo'?}} (sem 'genomas'): {u}")
        unidades_derivadas(u["bases"], int(u["k"]), u.get("prefixo", "experimento-maior"))
        fora = sorted(set(u["bases"]) - SEMENTES_TESTE)
        if fora:
            plano = cfg.get("plano")
            if not plano or not (RAIZ / plano).is_file():
                raise SementeSemPlano(f"bases {fora} fora das dos testes: precisa do plano de analise registrado (campo 'plano')")
    if "ponto" in cfg and cfg["ponto"] not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {cfg['ponto']!r}: so {sorted(PONTOS_APRENDIZ)}")
    if "montagem" in cfg and cfg["montagem"] not in MONTAGENS:
        raise ValueError(f"montagem {cfg['montagem']!r}: so {MONTAGENS}")
    for b in cfg["bracos"]:
        braco_de(b)
    for m in cfg.get("mundos", ["padrao"]):
        mundo_de(m)
    for a in cfg.get("acoplados", []):
        if set(a) != {"origem", "destino", "filtro"}:
            raise ValueError(f"acoplado fora do formato: {a}")
        try:
            filtro_de(a["filtro"])
        except KeyError as e:
            raise ValueError(f"acoplado fora do formato: {a}") from e
        braco_de(a["destino"])
        if a["origem"] not in cfg["bracos"]:
            raise ValueError(f"acoplado de um braco que nao roda: {a['origem']}")
    genomas = [g for g in cfg.get("genomas", [None]) if g is not None]
    fora = sorted((set(cfg.get("sementes", [])) | set(genomas)) - SEMENTES_TESTE)
    if fora:
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes {fora} fora das dos testes {sorted(SEMENTES_TESTE)}: precisa do plano de analise "
                                  "registrado (campo 'plano', arquivo no repositorio)")
    return cfg


def cfg_lobos_do_ponto(ponto: str = PONTO_PADRAO, troca: dict | None = None) -> ConfigLobos:
    """O aprendiz de um ponto nomeado (PONTOS_APRENDIZ), com os campos de `troca` por cima. Ponto desconhecido falha alto."""
    if ponto not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {ponto!r}: so {sorted(PONTOS_APRENDIZ)}")
    base = replace(CONFIG_LOBOS_APRENDIZ, **PONTOS_APRENDIZ[ponto])
    return replace(base, **troca) if troca else base


def bancada_da_config(cfg: dict) -> Bancada:
    """A Bancada da config: os padroes, e o que as chaves "consequencia", "ponto" e "lobos" (o ponto nomeado, e por cima dele os campos
    da chave "lobos"; sem "ponto", o L1 = CONFIG_LOBOS_APRENDIZ) e "frutas" (sobre o CONFIG_FRUTAS_LIGADA; listas do JSON viram tuplas)
    trocam. Sem essas chaves, a bancada de sempre (REVISAO-APRENDIZ)."""
    cc = CONFIG_CONSEQUENCIA if "consequencia" not in cfg else replace(CONFIG_CONSEQUENCIA, **cfg["consequencia"])
    kw = {"cfg_consequencia": cc}
    if "lobos" in cfg or "ponto" in cfg:
        kw["cfg_lobos"] = cfg_lobos_do_ponto(cfg.get("ponto", PONTO_PADRAO), cfg.get("lobos"))
    if cfg.get("julgamento_fruta"):
        kw["julgamento_fruta"] = True
    if "montagem" in cfg:
        kw["montagem"] = cfg["montagem"]
    if "frutas" in cfg:
        tupla = lambda v: tuple(tupla(x) for x in v) if isinstance(v, list) else v  # noqa: E731
        kw["cfg_frutas"] = replace(CONFIG_FRUTAS_LIGADA, **{k: tupla(v) for k, v in cfg["frutas"].items()})
    return Bancada(int(cfg["dias"]), int(cfg["orcamento"]), **kw)


def rodar(cfg: dict, pasta: Path) -> dict:
    """Vidas de todos os bracos x donos x sementes (x genomas x mundos), gravadas e rejogadas do disco; os acoplados; as
    medidas por vida e as tabelas braco x condicao por dono e medida."""
    validar_config(cfg)
    bancada = bancada_da_config(cfg)
    dir_vidas = pasta / "vidas"
    vidas: dict[str, VidaBancada] = {}

    def guardar(v: VidaBancada) -> None:
        _gravar(dir_vidas / f"{v.nome}.jsonl", v.motor.log.para_jsonl())
        _gravar(dir_vidas / f"{v.nome}.politica.json", _interno(v.motor))
        bancada.conferir_replay(v, (dir_vidas / f"{v.nome}.jsonl").read_text(encoding="utf-8"))
        vidas[v.nome] = v

    if "unidades" in cfg:
        unidades = unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]),
                                      cfg["unidades"].get("prefixo", "experimento-maior"))
        pares = [(u["genoma"], u["semente"]) for u in unidades]
    else:
        unidades = []
        pares = [(g, int(s)) for g in cfg.get("genomas", [None]) for s in cfg["sementes"]]
    da_unidade = {(u["genoma"], u["semente"]): {"base": u["base"], "k": u["k"]} for u in unidades}
    for (g, s), mundo, dono, braco in product(pares, cfg.get("mundos", ["padrao"]), cfg["donos"], cfg["bracos"]):
        guardar(bancada.vida(EspecVida(dono, braco, s, g, mundo)))
    origens = list(vidas.values())
    for a in cfg.get("acoplados", []):
        for v in origens:
            if v.espec.braco == a["origem"]:
                guardar(bancada.acoplar(v, a["destino"], a["filtro"]))
    # o piso do tempo ate aprender e o acerto do P0 na mesma celula (o prior herdado); sem P0 na config, o da propria vida
    medidas, piso, taxa_p0 = {}, {}, {}
    for nome, v in sorted(vidas.items()):
        if v.espec.braco == "P0" and v.origem is None:
            medidas[nome] = bancada.medir(v, cfg["sonda"])
            piso[v.espec.celula] = medidas[nome]["acerto_total"]
            if medidas[nome]["frutas"] is not None:
                taxa_p0[v.espec.celula] = medidas[nome]["frutas"]["taxa_fruta_ruim"]["total"]["taxa"]
    for nome, v in sorted(vidas.items()):
        if nome not in medidas:
            medidas[nome] = bancada.medir(v, cfg["sonda"], piso.get(v.espec.celula), taxa_p0.get(v.espec.celula))
    for nome, v in vidas.items():
        medidas[nome]["unidade"] = da_unidade.get((v.espec.genoma, v.espec.semente))
    tabelas = tabelas_braco_condicao(medidas, cfg["bootstrap"])
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "tabelas.json", _dump(tabelas))
    _gravar(pasta / "meta.json", _dump(meta(cfg)))
    return {"vidas": vidas, "medidas": medidas, "tabelas": tabelas}


def tabelas_braco_condicao(medidas: dict, boot: dict) -> dict:
    """Por dono e medida: tabela braco x condicao, unidade = vida (semente x genoma). A coluna e "condicao/mundo"
    ("casado/padrao", "casado/casado_frutas", "descasado/descasado", "mutavel/mutavel"...): dois mundos da mesma condicao nunca se
    misturam numa celula. Nos mundos das frutas, tambem as medidas do N5 (MEDIDAS_FRUTAS: a taxa da fruta ruim no inicio e no final
    e os consumos ate a metade do caminho), pela tabela parcial, que conta as vidas sem valor em vez de sumir com elas."""
    out = {}
    for dono in sorted({m["dono"] for m in medidas.values()}):
        out[dono] = {}
        for medida in MEDIDAS_TABELA:
            valores: dict[tuple[str, str], list[float]] = {}
            for m in medidas.values():
                if m["dono"] == dono:
                    valores.setdefault((m["braco"], f"{m['condicao']}/{m['mundo']}"), []).append(m[medida])
            out[dono][medida] = tabela_braco_condicao(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
        # as medidas do N5 (plano, secao 5), so nos mundos das frutas: podem faltar numa vida (janela sem consumo, P0 sem consumo)
        frutas = [m for m in medidas.values() if m["dono"] == dono and m["frutas"] is not None]
        if frutas:
            for medida, f in MEDIDAS_FRUTAS.items():
                valores = {}
                for m in frutas:
                    valores.setdefault((m["braco"], f"{m['condicao']}/{m['mundo']}"), []).append(f(m["frutas"]))
                out[dono][medida] = tabela_braco_condicao_parcial(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
    return out


MEDIDAS_FRUTAS = {
    "taxa_fruta_ruim_inicio": lambda f: f["taxa_fruta_ruim"]["inicio"]["taxa"],
    "taxa_fruta_ruim_final": lambda f: f["taxa_fruta_ruim"]["final"]["taxa"],
    "consumos_ate_metade": lambda f: f["consumos_ate_metade"]["consumos"],
}


def meta(cfg: dict) -> dict:
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    return {"config": cfg, "ponto": cfg.get("ponto", PONTO_PADRAO),
            "cfg_lobos": cfg_lobos_do_ponto(cfg.get("ponto", PONTO_PADRAO), cfg.get("lobos")).__dict__,
            "python": platform.python_version(), "plataforma": platform.platform(),
            "engine_sha256": sha256_engine(), "lobos_sha256": _sha(RAIZ / "digilab" / "policies" / "lobos.py"),
            "config_sha256": _sha(RAIZ / "digilab" / "config.py"), "bancada_sha256": _sha(Path(__file__)),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bancada da V2: bracos P0-P3 sobre o mesmo aprendiz (docs/TAREFA_V2_BANCADA.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True, help="pasta de saida (vidas/, medidas.json, tabelas.json, meta.json)")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida))
    print(f"{len(r['vidas'])} vidas rejogadas do disco bit a bit; medidas e tabelas em {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
