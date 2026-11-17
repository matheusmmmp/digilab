"""Personalidade no motor: temperamento na politica, vinculo, obediencia e desejo.

Desde a LZ2b da LIMPEZA (docs/TAREFA_V3_LIMPEZA.md, 3.3), aqui ficam so a `PoliticaBanditPersonalidade` (D-LZ-8) e as fabricas de vida da
v1 que a usam por padrao (`fabricas_treino`, `simular_vida_treino`, `fabricas_educacao`, `fabricas_filho`; D-LZ-10); o motor foi para o
`digilab/personalidade.py`, reexportado aqui. Este arquivo sai na LZ4. O resto deste texto e o de antes.

docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secoes 1-3. Nada aqui altera engine.py:
  - PoliticaBanditPersonalidade: a politica da memoria por espacos com as ESCALAS do
    temperamento (variancia da amostra, peso de elogio e repreensao, decaimento das
    memorias de demora e bronca). Temperamento neutro = configs identicas = mesma politica.
  - MotorPersonalidade: subclasse do MotorComFeedback. Sobrescreve so
    _aplicar_acao_usuario (recusa) e embrulha a politica para ver cada decisao
    (desejo e vinculo). O log e o mesmo: o replay reconstroi tudo.

Obediencia (so para acoes de cuidado; feedback sempre chega):
    p = logistica(b0 + b_vinculo*vinculo - b_teimosia*teimosia - b_conflito*conflito)
sorteada na stream propria `rng_obediencia` (derivada da semente do motor). Na
desobediencia: `recusar` (a acao do dono nao tem efeito) ou `fazer_outra` (o pet
segue a propria acao atual por um tick). Em ambos:
  - a acao consome orcamento igual (o canal ja contou antes de chegar aqui);
  - a funcao de efeito do dono roda sobre um estado DESCARTADO, so para consumir a
    rng de ambiente como uma acao aceita: recusar nao desalinha o clima entre bracos;
  - a tentativa conta como contato (tempo sem cuidado zera), sem efeito nas necessidades;
  - a politica recebe a acao do dono normalmente (recusa nao corta aprendizado).
Com `obediencia_desligada`, p = 1 e a rng_obediencia nunca e usada.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Callable

from .config import (CONFIG_BANDIT, CONFIG_DONOS, CONFIG_HABITUACAO, CONFIG_PADRAO, CONFIG_TEMPERAMENTO, CONFIG_TREINO, TICKS_POR_DIA,
                     Config, ConfigConfianca, ConfigDonos, ConfigEducacao, ConfigLesoes, ConfigMentira, ConfigTreino)
from .donos import Visao
from .educacao import MotorEducacao, rival_padrao
from .heranca import Origem
from .memoria_espacos import PoliticaBanditEspacos
# o motor de personalidade foi para o `personalidade.py` (a LZ2b, D-LZ-8); os nomes ficam reexportados aqui ate a LZ4
from .personalidade import (ATENDE, MotorPersonalidade, Recusa, _IDX, _PoliticaObservada, conflito, logistica,  # noqa: F401
                            termos_obediencia)
from .protocol import derivar_semente
from .temperamento import NEUTRO, Temperamento
from .treino import CanalDeInteracao, Vida
from .treino_vida import DonoComTreino, MotorTreino, orcamento_treino


class PoliticaBanditPersonalidade(PoliticaBanditEspacos):
    """Memoria por espacos + temperamento. Com o temperamento neutro, os configs
    derivados sao IGUAIS aos padrao e a politica e identica a PoliticaBanditEspacos."""

    def __init__(self, cfg=None, temperamento: Temperamento = NEUTRO, cfg_bandit=None, cfg_memoria=None,
                 cfg_temperamento=None, habituacao_ligada: bool = False, cfg_habituacao=None) -> None:
        ct = cfg_temperamento or CONFIG_TEMPERAMENTO
        cb = cfg_bandit or CONFIG_BANDIT
        self.temperamento = temperamento
        if not temperamento.neutro:
            cb = replace(cb, variancia_amostra=cb.variancia_amostra * temperamento.fator_variancia(ct),
                         recompensa_elogio=cb.recompensa_elogio * temperamento.peso_elogio(ct),
                         recompensa_repreensao=cb.recompensa_repreensao * temperamento.peso_repreensao(ct))
            fator = {c: temperamento.fator_tau_rancor(ct) for c in ct.categorias_rancor}
        else:
            fator = None
        # habituacao (adendo DF 2.3): desligada = memoria e recompensa identicas as de antes
        self.habituacao_ligada = habituacao_ligada
        hab = (cfg_habituacao or CONFIG_HABITUACAO) if habituacao_ligada else None
        super().__init__(cfg, cb, cfg_memoria, fator, hab, temperamento)


# ------------------------------------------------------------------ as fabricas de vida da v1, com o bandit por padrao
# vieram do treino_vida.py e do educacao.py sem mudar uma linha (a LZ2b da LIMPEZA, D-LZ-10): saem com este arquivo na LZ4

def fabricas_treino(semente: int, especie: str, temperamento: Temperamento, obediencia_desligada: bool = False,
                    ct: ConfigTreino | None = None, cfg_vinculo_situacao=None):
    """(fabrica da politica, fabrica do motor) de uma vida com treino; reusadas no replay.
    cfg_vinculo_situacao: a variante B do vinculo (docs/PLANO_ANALISE_V2_VINCULO.md); None = o vinculo de sempre."""
    fp = lambda cfg=None: PoliticaBanditPersonalidade(cfg, temperamento)  # noqa: E731
    fm = (lambda politica, cfg, s: MotorTreino(politica, cfg, s, temperamento, especie,  # noqa: E731
                                               obediencia_desligada=obediencia_desligada, cfg_treino=ct,
                                               cfg_vinculo_situacao=cfg_vinculo_situacao))
    return fp, fm


def simular_vida_treino(braco: str, semente: int, dias: int, especie: str, temperamento: Temperamento,
                        cfg: Config | None = None, cfg_donos: ConfigDonos | None = None,
                        ct: ConfigTreino | None = None, cfg_vinculo_situacao=None) -> Vida:
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    ct = ct or CONFIG_TREINO
    total = dias * TICKS_POR_DIA
    passos = total // cfg_donos.passo_ticks
    orc, _ = orcamento_treino(dias, cfg_donos, ct)
    fp, fm = fabricas_treino(semente, especie, temperamento, ct=ct, cfg_vinculo_situacao=cfg_vinculo_situacao)
    motor = fm(fp(cfg), cfg, semente)
    dono = DonoComTreino(braco, dias, cfg_donos, ct)
    # rng do dono: propria de cada braco (derivada da semente e do braco), como na v1
    rng_dono = random.Random(derivar_semente("dono", semente, braco))
    canal = CanalDeInteracao(motor, orc, cfg_donos.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orc, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
    canal.fechar()
    v = Vida(braco=braco, semente_coorte=semente, motor=motor, interacoes=canal.gasto)
    v.dono = dono          # contagens do dono (treino x carinho no slot), para o relatorio
    return v


def fabricas_filho(origem: Origem, **kw):
    """fabricas_educacao com a especie e o temperamento herdados (a semente do motor vem de quem chama)."""
    return fabricas_educacao(0, origem.especie, origem.temperamento, **kw)


def fabricas_educacao(semente: int, especie: str, temperamento: Temperamento, obediencia_desligada: bool = False,
                      ct=None, ce: ConfigEducacao | None = None, cl: ConfigLesoes | None = None,
                      lutador_do_pet: Callable | None = None, rival_por_nome: Callable = rival_padrao,
                      cfg_evo=None, decisor_externo=None, cm: ConfigMentira | None = None,
                      honestidade_especie: float = 1.0, cc: ConfigConfianca | None = None,
                      politica_fabrica: Callable | None = None):
    """(fabrica da politica, fabrica do motor) de uma vida com educacao; reusadas no replay (sem o decisor).
    politica_fabrica (V2, L1): troca a politica do pet (padrao: o bandit da personalidade, bit a bit como antes)."""
    fp = politica_fabrica or (lambda cfg=None: PoliticaBanditPersonalidade(cfg, temperamento))  # noqa: E731
    fm = (lambda politica, cfg, s: MotorEducacao(politica, cfg, s, temperamento, especie,  # noqa: E731
                                                 obediencia_desligada=obediencia_desligada, cfg_treino=ct,
                                                 cfg_educacao=ce, cfg_lesoes=cl, lutador_do_pet=lutador_do_pet,
                                                 rival_por_nome=rival_por_nome, cfg_evo=cfg_evo,
                                                 decisor_externo=decisor_externo, cfg_mentira=cm,
                                                 honestidade_especie=honestidade_especie, cfg_confianca=cc))
    return fp, fm
