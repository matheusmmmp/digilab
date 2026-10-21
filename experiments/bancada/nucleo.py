"""A bancada da V2, módulo `nucleo`.

A classe Bancada, inteira (SA-4: partir em mixins é outra passada).

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, replace

from digilab.ambiente import DonoComBola, MotorAmbiente, PoliticaInstintoBola, reproduzir_ambiente
from digilab.config import (CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA,
                            CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, CONFIG_PEDIDO_LIGADA, TICKS_POR_DIA, ConfigBola,
                            ConfigConsequencia, ConfigFrutas, ConfigInformacao, ConfigLobos, ConfigMundo, ConfigPedido)
from digilab.config import ConfigCompeticao, ConfigCorpo
from digilab.config import CONFIG_TROCA_DIGESTAO, ConfigTrocaDigestao
from digilab.config import CONFIG_GRUPO_LIGADA, ConfigGrupo
from digilab.grupo import Grupo, PetDoGrupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo
from digilab.gestos import CanalComGestos, DonoComGestos, simular_vida_gestos
from digilab.motor_corpo import com_corpo
from digilab.donos import criar_dono
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario, LogDeEventos
from digilab.evolucao import politica_no_tick
from digilab.instinto_mundo import PoliticaInstintoMundo
from digilab.instinto_banheiro import PoliticaInstintoBanheiro
from digilab.config import CONFIG_BANHEIRO_LIGADA, ConfigBanheiro
from digilab.frutas import DonoPedinte, JulgadorFruta, PoliticaInstintoFrutas, genoma_frutas
from digilab.metrics import (acerto_na_tarefa, custo_da_plasticidade, desempenho_no_ambiente, consumos_ate_metade, distribuicoes_de_acao,
                             estados_sonda, jsd_media, multiconjunto_informacoes, privacao_nas_decisoes, resposta_a_bola, taxa_fruta_ruim,
                             ZONAS_CONFLITO, deferencia_ao_pedido, dia_cruza_zero, fracao_da_fruta, memoria_nas_subdecisoes,
                             ocupacao_espacos_frutas)
from digilab.metrics import (cuidado_preservado, deficit_fome_energia, inclinacao_permanencia, janela_dias, permanencia_media,
                             taxa_no_abandono, visitas_manchas)
from digilab.metrics import contribuicao_drives, dominancia_decisoes
from digilab.metrics import drives_novos as medir_drives_novos, tempo_livre_be
from digilab.metrics import REGRAS_TEMPO_LIVRE, efeitos_do_tapa, metabolismo_da_vida, tempo_comer_brincar, vez_no_grupo
from digilab.mundo import DonoCarinhoBanheiro
from digilab.mundo import ESTILOS_LUGAR, DonoComLugar, MotorMundo, centro_da_celula, reproduzir_mundo
from digilab.obediencia import MotorPersonalidade
from digilab.policies import PoliticaLobos
from digilab.policies.lobos import (DRIVES_NOVOS_SINAL, RECEPTOR_DO_INDICE, RECEPTORES_NOVOS, contribuicoes_corpo, sinal_corpo,
                                    sinal_corpo_canais)
from digilab.policies.lobos import CANAL_DO_DRIVE, INDICE_HUMOR, arred, sinal_por_canal
from digilab.config import ConfigRedeDeSi
from digilab.rede_de_si import ACOES as ACOES_REDE, CONTEXTO as CONTEXTO_REDE, RedeDeSi
from digilab.policies.lobos import REGRAS_PEDIDO
from digilab.metrics import brier_skill, brier_skill_multiclasse, mae_previsao, media_historica, previsao_persistencia
from digilab.policy import PoliticaInstinto
from digilab.protocol import derivar_semente
from digilab.temperamento import NEUTRO
from digilab.temperamento import sortear as sortear_temperamento
from digilab.treino import CanalDeInteracao, MotorComFeedback, reproduzir_com_feedback, simular_vida

from .mundos import CONFIG_CORPO_QUIMICA
from .bracos import MONTAGEM_PADRAO


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
    cfg_mundo: ConfigMundo = CONFIG_MUNDO_LIGADA         # W-BANCADA-MUNDO: o mundo fisico (o layout afastado vem do mundo)
    cfg_corpo: ConfigCorpo = CONFIG_CORPO_QUIMICA        # W-BANCADA-CORPO: o corpo do regime "quimica" (o "corpo" liga por cima)
    cfg_rede: ConfigRedeDeSi | None = None               # W-BANCADA-REDE: a rede de si observando toda vida (None: sem a rede)
    cfg_troca_digestao: ConfigTrocaDigestao = CONFIG_TROCA_DIGESTAO   # rede de si, 2b: a taxa lenta do P1-c-lenta (RS-3)
    metabolismo: bool = True                             # adendo 3 (A3.1): False tira o metabolismo dos bracos do corpo, so para
                                                         # refazer as vidas de antes dele (os gabaritos do G2); fora da config
    cfg_competicao: ConfigCompeticao | None = None       # V3-3/V3-4 (TAREFA_V2_V3_COMPETICAO): a competicao entre as regras urgentes
                                                         # em todo cerebro A da bancada (o R1 e, com o aprendizado desligado, o
                                                         # R1-congelado); None ou desligada: a vida de hoje

    def __post_init__(self) -> None:
        if self.dias <= 0 or self.orcamento <= 0:
            raise ValueError("dias e orcamento precisam ser positivos")
        if not self.cfg_lobos.aprendizado_ligado:
            raise ValueError("cfg_lobos e a do aprendiz (aprendizado ligado); o P0 desliga por conta propria")
        if not self.cfg_bola.ligada:
            raise ValueError("cfg_bola e a dos mundos da bola: ligada (o mundo padrao nao usa bola)")
        if not self.cfg_frutas.ligada:
            raise ValueError("cfg_frutas e a dos mundos das frutas: ligada")
        if not (self.cfg_corpo.ligada and self.cfg_corpo.digestao and self.cfg_corpo.vida) or self.cfg_corpo.drives_novos \
                or self.cfg_corpo.gestos or self.cfg_corpo.metabolismo:
            raise ValueError("cfg_corpo e a da quimica (ligada, digestao e Vida, sem drives novos, gestos nem metabolismo); o regime e o "
                             "braco ligam o resto")
        if not self.cfg_informacao.ligada:
            raise ValueError("cfg_informacao e a dos mundos das frutas: ligada (sem informante, nada muda na vida)")
        if not self.cfg_pedido.ligada:
            raise ValueError("cfg_pedido e a dos bracos com pedido: ligada")
        if self.montagem not in MONTAGENS:
            raise ValueError(f"montagem {self.montagem!r}: so {MONTAGENS}")
        if not self.cfg_mundo.ligada:
            raise ValueError("cfg_mundo e a do mundo fisico: ligada")

    def cfg_mundo_de(self, mundo: Mundo) -> ConfigMundo:
        """A ConfigMundo de um mundo fisico: a da bancada, com o layout afastado no `fisico_afastado` (A1.8; nada mais muda)."""
        if mundo.fisico is None:
            raise ValueError(f"mundo {mundo.nome!r} nao e o fisico")
        layout = LAYOUTS_FISICO[mundo.fisico]
        return self.cfg_mundo if layout is None else replace(self.cfg_mundo, layout=layout)

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

    def politica(self, espec: EspecVida, cfg=None):
        """O cerebro do braco (a `PoliticaDoBraco`); com a chave `rede_de_si`, embrulhado pela rede de si, que so observa (RS-5,
        `PoliticaComRede`: a vida e a de sem a rede, G-OBS). A rede le os receptores do corpo: braco sem corpo falha alto."""
        p = self.politica_do_braco(espec, cfg)
        return p if self.cfg_rede is None else PoliticaComRedeSemOrgaos(p, self.cfg_rede)

    def politica_do_braco(self, espec: EspecVida, cfg=None) -> PoliticaDoBraco:
        if espec.cerebro not in CEREBROS:
            raise KeyError(f"cerebro {espec.cerebro!r}: so {CEREBROS} (outros cerebros sao a comparacao do N11)")
        b = braco_de(espec.braco)
        mundo = mundo_de(espec.mundo)
        if b.fonte == "informacao" and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a informacao e sobre as frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        if (b.memoria is not None or b.pedido) and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a memoria e o pedido sao das frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        if b.instinto_mundo is not None and mundo.fisico is None:
            raise ValueError(f"braco {b.rotulo}: o instinto do mundo e do mundo fisico, nao {espec.mundo!r}")
        if mundo.fisico is not None and (espec.cerebro == "instinto" or b.instinto_mundo is not None):
            # o instinto que ve o mundo (instinto_mundo, #232), com os pesos w_bola e w_fruta da bancada (as chaves de hoje desligadas: o
            # mundo substitui o cenario do N4 e da A1). O P0z e ele no modo sem_explorar, em qualquer cerebro: os lobos nao tem o modo
            if b.fonte != "nenhuma" or b.memoria is not None or b.pedido:
                raise ValueError(f"o instinto do mundo so no P0 e no P0z (nao aprende, nao lembra, nao le o pedido): braco {b.rotulo}")
            if b.instinto_mundo not in (None, "sem_explorar"):
                raise ValueError(f"braco {b.rotulo}: modo do instinto do mundo {b.instinto_mundo!r}")
            cb, cf = self.pesos_do_mundo()
            if b.banheiro is not None:          # banheiro: o instinto do alivio, sobre o do mundo (o P0 do 2 x 2 com o cerebro instinto)
                return PoliticaDoBraco(PoliticaInstintoBanheiro(cfg, self.cfg_banheiro_de(espec), self.cfg_corpo_de(espec), cb, cf), b)
            return PoliticaDoBraco(PoliticaInstintoMundo(cfg, cb, cf, sem_explorar=b.instinto_mundo == "sem_explorar"), b)
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
        if b.alvo:                          # P1-alvo (PLANO_ANALISE_V2_MUNDO_ALVO, secao 3): o alvo aprendido, so no mundo fisico
            if mundo.fisico is None:
                raise ValueError(f"braco {b.rotulo}: o alvo aprendido e do mundo fisico, nao {espec.mundo!r}")
            cl = replace(cl, alvo_aprendido=True)
        # LOBOS-MUNDO (#141): os lobos veem o mundo em que vivem; no padrao, nenhuma chave (as formas de antes). No mundo fisico, a
        # chave dele (MUNDO-CEREBROS, #232), com os pesos da bancada nas chaves de hoje desligadas
        cb = self.cfg_bola if mundo.bola is not None else None
        cf = self.cfg_frutas if mundo.frutas else None
        cm = None
        if mundo.fisico is not None:
            (cb, cf), cm = self.pesos_do_mundo(), self.cfg_mundo_de(mundo)
        # canais (#169): o braco que os fixa (as ablacoes da K-7) manda; os outros seguem a config
        cc = self.cfg_consequencia if b.canais is None else replace(self.cfg_consequencia, canais_ligados=b.canais)
        if b.pesos_janela:                  # P1-cw (A2.4, #236): o peso de cada drive pela falta recente; o resto do P1 igual
            cc = replace(cc, pesos_janela=True)
        return PoliticaDoBraco(PoliticaLobos(cfg, cl, cfg_bola=cb, cfg_frutas=cf, cfg_mundo=cm, cfg_corpo=self.cfg_corpo_de(espec),
                                             cfg_banheiro=self.cfg_banheiro_de(espec), cfg_competicao=self.cfg_competicao), b, cc)

    def cfg_corpo_de(self, espec: EspecVida) -> ConfigCorpo | None:
        """A ConfigCorpo da vida pelo regime do braco: None em "hoje" (e nos bracos sem regime: a vida de antes); a da bancada em
        "quimica"; a da bancada com `drives_novos` e `gestos` em "corpo" (a etapa 6). Vale tambem no mundo fisico (o arranjo do #247)."""
        regime = braco_de(espec.braco).regime
        if regime in (None, "hoje"):
            return None
        if regime == "quimica":
            return replace(self.cfg_corpo, drives_novos=False, gestos=False, metabolismo=self.metabolismo_de(espec))
        # banheiro: o corpo com os gestos e a sub-chave banheiro (a vontade e o conforto, TAREFA_V2_BANHEIRO, secao 3 e BN-6)
        return replace(self.cfg_corpo, drives_novos=True, gestos=True, banheiro=braco_de(espec.braco).banheiro is not None,
                       metabolismo=self.metabolismo_de(espec))

    def metabolismo_de(self, espec: EspecVida) -> bool:
        """o metabolismo da vida: o do braco (A3.1), salvo na bancada com `metabolismo=False` (as vidas de antes, so para o G2)"""
        return self.metabolismo and braco_de(espec.braco).metabolismo

    def cfg_banheiro_de(self, espec: EspecVida) -> ConfigBanheiro | None:
        """A ConfigBanheiro da vida: None fora dos bracos do banheiro; nos quatro do 2 x 2, a ligada, com o limpador do braco (BL0 e BLC).
        O carinho depois do banheiro e do dono (o DonoCarinhoBanheiro), nao da chave."""
        b = braco_de(espec.braco)
        if b.banheiro is None:
            return None
        if mundo_de(espec.mundo).fisico is None:
            raise ValueError(f"braco {b.rotulo}: o banheiro e do mundo fisico, nao {espec.mundo!r}")
        return replace(CONFIG_BANHEIRO_LIGADA, limpador=BRACOS_BANHEIRO[b.banheiro][0])

    def pesos_do_mundo(self) -> tuple[ConfigBola, ConfigFrutas]:
        """A ConfigBola e a ConfigFrutas da bancada com a chave desligada: no mundo fisico elas so dao os pesos w_bola e w_fruta ao instinto
        do mundo e ao prior dos lobos (o MotorMundo exige as duas desligadas)."""
        return replace(self.cfg_bola, ligada=False), replace(self.cfg_frutas, ligada=False)

    def fabrica_politica(self, espec: EspecVida):
        return lambda cfg=None: self.politica(espec, cfg)

    def fabrica_motor(self, espec: EspecVida):
        mundo = mundo_de(espec.mundo)
        # corpo (W-BANCADA-CORPO): o com_corpo(...) do motor do mundo, com a ConfigCorpo do regime; sem regime, o motor de antes
        corpo = self.cfg_corpo_de(espec)
        classe = (lambda base: base) if corpo is None else com_corpo  # noqa: E731
        kc = {} if corpo is None else {"cfg_corpo": corpo}
        if braco_de(espec.braco).digestao_lenta:
            # rede de si, etapa 2b (RS-3): a taxa_digestao passa a lenta no fim do dia 7 (o tick da troca do mutavel), no MotorCorpo
            kc["troca_digestao"] = (self.tick_troca_digestao, self.cfg_troca_digestao.taxa_lenta)
        banheiro = self.cfg_banheiro_de(espec)       # o banheiro (#265): a chave no MotorMundo, com o corpo com a sub-chave na frente
        if banheiro is not None:
            kc["cfg_banheiro"] = banheiro
        if mundo.fisico is not None:
            # o desenho do plano do mundo (secao 2): MotorMundo, obediencia, educacao, lesoes, frutas e bola de hoje desligadas, especie
            # brasa; o mundo "iguais" (PMF-7): as tres frutas com o efeito neutro no humor
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cm = self.cfg_mundo_de(mundo)
            efeito = efeitos_da_condicao(None, self.cfg_frutas, mundo.condicao)
            return lambda politica, cfg, semente: classe(MotorMundo)(politica, cfg, semente, temperamento, "brasa",
                                                                     obediencia_desligada=True, semente_genoma=espec.genoma,
                                                                     cfg_mundo=cm, efeito_frutas=efeito, **kc)
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
            # P1-c-tapaX (A1.1): o DonoTapaFruta le os consumos pelo mesmo estado()["consumos_frutas"] (a chave so os expoe)
            if braco_de(espec.braco).gestos == "tapa_fruta":
                cj = CONFIG_JULGAMENTO_FORA
            return lambda politica, cfg, semente: classe(MotorFrutasMundo)(
                politica, cfg, semente, temperamento, "brasa", obediencia_desligada=True, cfg_bola=CONFIG_BOLA, cfg_frutas=cf,
                semente_genoma=espec.genoma, condicao=condicao, tick_troca=troca, cfg_informacao=ci, cfg_pedido=cp,
                cfg_julgamento=cj, **kc)
        if mundo.bola is not None:
            # o desenho da A1 (plano, secao 3): MotorAmbiente, obediencia, educacao e lesoes desligadas, especie brasa
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cb = self.cfg_bola
            return lambda politica, cfg, semente: classe(MotorAmbiente)(politica, cfg, semente, temperamento, "brasa",
                                                                        obediencia_desligada=True, cfg_bola=cb, **kc)
        if espec.genoma is None:
            return lambda politica, cfg, semente: classe(MotorComFeedback)(politica=politica, cfg=cfg, semente=semente, **kc)
        temperamento = sortear_temperamento(espec.genoma)
        if braco_de(espec.braco).regime is not None:
            # corpo (W-BANCADA-CORPO): nos bracos do plano do corpo, hoje e quimica, a obediencia fica desligada no padrao com genoma,
            # como nos mundos da bola e das frutas (o corpo a exige, secao 2): o par G-HOJE difere so na quimica
            return lambda politica, cfg, semente: classe(MotorPersonalidade)(politica, cfg, semente, temperamento,
                                                                             obediencia_desligada=True, **kc)
        return lambda politica, cfg, semente: MotorPersonalidade(politica, cfg, semente, temperamento)

    # ------------------------------------------------------------- vidas

    def vida(self, espec: EspecVida) -> VidaBancada:
        mundo = mundo_de(espec.mundo)
        if (espec.lugar is not None) != (mundo.fisico is not None):
            raise ValueError(f"{espec.nome}: o lugar do dono existe so no mundo fisico, e la e obrigatorio")
        b = braco_de(espec.braco)
        if b.gestos is not None and (mundo.fisico is not None or mundo.bola == "a1"):
            raise ValueError(f"{espec.nome}: os gestos do dono (DonoComGestos) ficam fora do mundo fisico e do bola_a1 (o plano do corpo "
                             "nao os usa la; o mundo fisico tem o dono so com o cuidado, PMF-3)")
        if b.gestos == "tapa_fruta" and not mundo.frutas:
            raise ValueError(f"{espec.nome}: o tapa na fruta X precisa de um mundo das frutas")
        fm = self.fabrica_motor(espec)
        rotulo = f"{espec.dono}-{espec.braco}"
        dono_ = self.dono(espec)
        canal = CanalComGestos if b.gestos is not None else CanalDeInteracao   # o SemGesto gasta o orcamento sem ir ao motor
        broncas = 0                              # N7: as broncas do pedido (so no P3+ped), que vem pelo canal do mundo
        julgamentos = 0                          # K4: os julgamentos da fruta, tambem pelo canal do mundo
        retirados = 0                            # mundo fisico: os sinais que o filtro sem_ensino ao vivo nao deixou chegar (PMF-3)
        carinhos = 0                             # banheiro: os carinhos depois do banheiro, pelo canal do mundo (fora do orcamento)
        if mundo.fisico is not None:
            if espec.lugar not in ESTILOS_LUGAR:
                raise ValueError(f"lugar {espec.lugar!r}: so {ESTILOS_LUGAR}")
            # o dono da v1 com o alimentar no lugar do estilo (a rng dono-lugar sem o braco) e so com o cuidado
            dono = DonoComLugar(criar_dono(espec.dono), espec.lugar, espec.semente, espec.dono, self.cfg_mundo_de(mundo))
            # banheiro (#265): nos bracos com carinho (B0C, BLC), o DonoCarinhoBanheiro, fora do orcamento (BN-2)
            carinho = DonoCarinhoBanheiro() if b.banheiro is not None and BRACOS_BANHEIRO[b.banheiro][1] else None
            motor, retirados = simular_vida_fisico(dono, self.politica(espec, CONFIG_PADRAO), espec.semente, self.dias,
                                                   self.orcamento, espec.dono, fm, carinho=carinho)
            carinhos = 0 if carinho is None else carinho.feitos
        elif mundo.bola == "a1":
            # como a A1 rodou: o dono embrulhado poe a bola DENTRO do orcamento; o aleatorio sorteia por_bola
            v = simular_vida(rotulo, DonoComBola(espec.dono, self.cfg_bola), self.politica(espec, CONFIG_PADRAO),
                             espec.semente, self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm)
            motor = v.motor
        elif mundo.bola == "b1b2":
            motor = simular_vida_mundo(dono_, RegraBola(espec.dono, self.cfg_bola),
                                       self.politica(espec, CONFIG_PADRAO), espec.semente, self.dias, self.orcamento,
                                       espec.dono, fm, canal_classe=canal)
        elif mundo.frutas:
            regra = CalendarioFrutas(espec.semente, self.cfg_frutas)
            julga = RegraFrutasComJulgador(regra, self.julgador(espec)) if self.julga_fruta(espec) else None
            regra = julga or regra
            if b.fonte == "informacao" and b.informacao != "depois":     # o P2d nao tem o informante da oferta: o julgador e o dele
                regra = RegraFrutasComInformante(regra, self.informante(espec))
            if b.pedido:
                regra = RegraFrutasComPedinte(regra, self.pedinte(espec))
            motor = simular_vida_mundo(dono_, regra, self.politica(espec, CONFIG_PADRAO), espec.semente,
                                       self.dias, self.orcamento, espec.dono, fm, canal_classe=canal)
            broncas = len(regra.pedinte.broncas) if b.pedido else 0
            # so o julgamento como feedback (elogiar/repreender) e julgamento; como informacao, conta em `informacoes` (o log)
            julgamentos = julga.feitos if julga is not None and julga.julgador.saida == "feedback" else 0
        else:
            # com os gestos, o treino.simular_vida com o CanalComGestos (a mesma rng do dono)
            simular = simular_vida_gestos if b.gestos is not None else simular_vida
            motor = simular(rotulo, dono_, self.politica(espec, CONFIG_PADRAO), espec.semente,
                            self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm).motor
        gestos = None
        if b.gestos is not None:
            gestos = dict(dono_.trocas)
            retirados = gestos["sem_gesto"]      # a bronca do modo sem tapa gasta o orcamento e nao chega ao log
            if isinstance(dono_, DonoTapaFruta):
                gestos.update({"fruta_x": dono_.fruta, "tapas_fruta": len(dono_.tapas), "descartados": len(dono_.descartados)})
        dono, eventos_mundo = contar_acoes(motor.log)
        dono += contar_gestos_mundo(motor.log)   # o deixar_comida e o deixar_bola do mundo fisico gastam o orcamento (0 nos outros)
        dono -= broncas + julgamentos + carinhos    # a bronca do pedido, o julgamento e o carinho do banheiro estao no log, mas vieram
        #                                           pelo mundo
        orcamento_gasto = dono + (eventos_mundo if mundo.bola == "a1" else 0) + retirados
        if orcamento_gasto != self.orcamento:
            raise RuntimeError(f"{espec.nome}: {orcamento_gasto} interacoes no orcamento, orcamento {self.orcamento}")
        vida = VidaBancada(espec, motor, dono, broncas=broncas, julgamentos=julgamentos, retirados=retirados, gestos=gestos,
                           carinhos=carinhos)
        self.conferir_replay(vida)
        return vida

    def dono(self, espec: EspecVida):
        """O dono da vida: o da v1 (criar_dono); nos bracos com gestos, dentro do DonoComGestos (o modo "tapa" no bloco do tapa; o "sem
        tapa" nos outros) e, no P1-c-tapaX, ainda dentro do DonoTapaFruta. A rng e a de sempre: o mesmo dono nos dois modos."""
        base = criar_dono(espec.dono)
        g = braco_de(espec.braco).gestos
        if g is None:
            return base
        base = DonoComGestos(base, "tapa" if g == "tapa" else "sem_tapa")
        return DonoTapaFruta(base, fruta_tapa(espec.semente)) if g == "tapa_fruta" else base

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
        if mundo_de(espec.mundo).fisico is not None:
            return reproduzir_mundo(log, fp, semente=espec.semente, fabrica_motor=fm)
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
        vida = VidaBancada(espec, m, contar_acoes(log)[0] + contar_gestos_mundo(log) - broncas - julgamentos, origem=origem.nome,
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
        if self.cfg_rede is not None and _estado_rede(r) != _estado_rede(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o estado da rede de si diverge no replay (G1-REDE)")

    # ------------------------------------------------------------- medidas

    def medir(self, vida: VidaBancada, sonda: dict, piso: float | None = None, taxa_p0: float | None = None) -> dict:
        """Desempenho no ambiente, acerto na tarefa e custo da plasticidade de uma vida. `piso` = acerto total do P0 na mesma
        celula (o prior herdado); sem ele, o da propria vida. O replay de medicao e conferido bit a bit contra a vida."""
        regs = []

        motores: list = []
        quimicos: list = []       # rede de si: os quimicos do corpo em cada decisao, so para o oraculo (nunca entregues a rede)

        def fab(cfg=None):
            reg = _Registro(self.politica(vida.espec, cfg))
            regs.append(reg)
            if self.cfg_rede is not None:
                sondar_quimicos(rede_de(reg).rede, motores, quimicos)
            return reg

        fisico = mundo_de(vida.espec.mundo).fisico is not None
        repro = reproduzir_mundo if fisico else reproduzir_com_feedback     # o mundo fisico tem eventos proprios no log
        fm_base = self.fabrica_motor(vida.espec)
        sonda_metab: list = []

        def fm(*a, **kw):
            """o motor de sempre; com o metabolismo, uma sonda so de leitura no passo do corpo (a medida descritiva, A3.3)"""
            motor = fm_base(*a, **kw)
            motores.append(motor)
            corpo = getattr(motor, "corpo", None)
            if corpo is not None and corpo.cc.metabolismo:
                sondar_metabolismo(corpo, sonda_metab)
            return motor

        m = repro(LogDeEventos.de_jsonl(vida.motor.log.para_jsonl()), fab, semente=vida.espec.semente, fabrica_motor=fm)
        if resumo_motor(m) != resumo_motor(vida.motor) or _interno(m) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou a vida")
        if self.cfg_rede is not None and _estado_rede(m) != _estado_rede(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: a sonda dos quimicos mudou a rede de si (G1-REDE)")
        reg = regs[0]
        reg.metabolismo = sonda_metab
        bola = None
        if isinstance(m, MotorAmbiente) and not fisico:
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
        extra_mundo = ({"lugar": vida.espec.lugar, "retirados": vida.retirados, "mundo_fisico": self.medidas_mundo(vida, m, reg)}
                       if fisico else {})
        dominancia = self.medidas_dominancia(vida, reg)
        corpo = self.medidas_corpo(vida, m, reg)
        if corpo is not None and m.cc.metabolismo:
            corpo["metabolismo"] = self.medidas_metabolismo(vida, m, reg)
        if corpo is not None and m.cc.gestos:
            corpo["tapa"] = self.medidas_tapa(vida, m, reg)
        comportamento = self.medidas_comportamento(reg)
        banheiro = self.medidas_banheiro(vida, m, reg) if braco_de(vida.espec.braco).banheiro is not None else None
        rede = None
        if self.cfg_rede is not None:
            tick_troca = self.tick_troca_digestao if braco_de(vida.espec.braco).digestao_lenta else None
            self.conferir_troca_digestao(vida, m, tick_troca)
            rede = self.medidas_rede(rede_de(reg).rede, quimicos, do_braco(reg.interna).cerebro.motivos, m.log, tick_troca)
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
                "deriva_final": custo["deriva_final"], "custo_da_plasticidade": custo, "dominancia": dominancia, "corpo": corpo, "banheiro": banheiro,
                "comportamento": comportamento, "rede_de_si": rede,
                **extra_mundo}

    # ------------------------------------------------------------- rede de si (PLANO_ANALISE_V2_REDE_DE_SI, secao 4; W-BANCADA-REDE)
    def conferir_troca_digestao(self, vida, m, tick_troca: int | None) -> None:
        """A troca da digestao da vida (etapa 2b) foi a pedida: no P1-c-lenta, no tick da bancada e para a taxa lenta; nos outros, nenhuma.
        Uma troca fora disso falha alto."""
        feita = getattr(m, "troca_digestao", None)
        if tick_troca is None:
            if feita is not None:
                raise RuntimeError(f"{vida.nome}: troca da digestao num braco sem a digestao lenta: {feita}")
            return
        if feita is None or feita["tick"] != tick_troca or feita["para"] != self.cfg_troca_digestao.taxa_lenta:
            raise RuntimeError(f"{vida.nome}: a troca da digestao nao foi a pedida (tick {tick_troca}, taxa "
                               f"{self.cfg_troca_digestao.taxa_lenta}): {feita}")

    @property
    def tick_troca_digestao(self) -> int:
        """O tick da troca da digestao do P1-c-lenta: o fim do dia 7 (RS-3), o mesmo corte do mutavel (`tick_troca`)."""
        return self.tick_troca

    def medidas_rede(self, rede: RedeDeSi, quimicos: list, motivos: list, log, tick_troca: int | None = None) -> dict:
        """As medidas da secao 4 de uma vida com a rede observando, do replay de medicao: a rede, as linhas de base (persistencia e media
        historica) e o oraculo (o mesmo LMS com os quimicos do corpo como entrada, so aqui), por horizonte, na janela dos ultimos sete
        dias (os dias 8 a 14 numa vida de 14); D_SI e D_MEDIA; a adaptacao (com `tick_troca`: a mesma rede congelada no tick, so na fome,
        nos ultimos quatro dias); a autoria do pedido e ao nascer (o Brier skill contra as sondas do cerebro, lidas do motivo e nunca
        entregues a rede); os descritivos (por receptor, a curva por dia, os pesos no fim de cada dia, a surpresa por hora).

        Gate da reproducao: a rede refeita aqui, so das leituras, das acoes e do contexto que ela registrou, tem de dar as mesmas previsoes
        (as duas cabecas) e os mesmos pesos no fim; senao falha alto (o oraculo e a congelada sao essa mesma conta)."""
        regs = rede.registros
        if not regs:
            raise RuntimeError("rede de si sem registros: a vida nao teve decisao")
        if len(quimicos) != len(regs) or len(motivos) != len(regs):
            raise RuntimeError(f"rede de si: {len(regs)} decisoes na rede, {len(quimicos)} retratos dos quimicos, {len(motivos)} motivos")
        receptores = list(rede.receptores)
        hz = rede.horizontes
        intervalo = CONFIG_PADRAO.intervalo_decisao_ticks
        por_dia = TICKS_POR_DIA // intervalo
        leituras = [r["leituras"] for r in regs]
        K = len(regs)
        dias = -(-K // por_dia)

        refeita = rede_offline(rede.cfg, regs, receptores)
        for n in hz:
            if refeita["corpo"][str(n)] != [r["corpo"][str(n)] for r in regs]:
                raise ReplayDivergiu(f"rede de si refeita das leituras: as previsoes de n = {n} divergem da rede")
        if refeita["autoria"] != [r["autoria"] for r in regs] or refeita["pesos_corpo"] != rede.pesos_corpo \
                or refeita["pesos_autoria"] != rede.pesos_autoria:
            raise ReplayDivergiu("rede de si refeita das leituras: a autoria ou os pesos divergem da rede")
        oraculo = rede_offline(rede.cfg, regs, receptores, extra=quimicos, autoria=False)

        janela = range(max(0, K - 7 * por_dia), K)          # os ultimos sete dias (8 a 14 numa vida de 14)
        pers, media = previsao_persistencia(leituras), media_historica(leituras)
        previsores = {"rede": refeita["corpo"], "oraculo": oraculo["corpo"]}
        maes = {}
        for n in hz:
            linha = {"rede": mae_previsao(leituras, previsores["rede"][str(n)], n, janela, receptores),
                     "persistencia": mae_previsao(leituras, pers, n, janela, receptores),
                     "media": mae_previsao(leituras, media, n, janela, receptores),
                     "oraculo": mae_previsao(leituras, previsores["oraculo"][str(n)], n, janela, receptores)}
            mr, mp, mm = linha["rede"]["mae"], linha["persistencia"]["mae"], linha["media"]["mae"]
            linha["d_si"] = None if mr is None else mp - mr
            linha["d_media"] = None if mr is None else mm - mr
            linha["rede_menos_persistencia_por_receptor"] = {
                r: (None if linha["rede"]["por_receptor"][r] is None else
                    linha["rede"]["por_receptor"][r] - linha["persistencia"]["por_receptor"][r]) for r in receptores}
            maes[str(n)] = linha
        n_pri = 4 if 4 in hz else hz[len(hz) // 2]
        curva = []
        for d in range(dias):
            ks = range(d * por_dia, min(K, (d + 1) * por_dia))
            curva.append({"dia": d + 1, "rede": mae_previsao(leituras, previsores["rede"][str(n_pri)], n_pri, ks, receptores)["mae"],
                          "persistencia": mae_previsao(leituras, pers, n_pri, ks, receptores)["mae"]})

        adapta = None
        if tick_troca is not None:
            k_troca = -(-tick_troca // intervalo)               # a primeira decisao no tick da troca ou depois
            cong = rede_offline(rede.cfg, regs, receptores, congelar_k=k_troca, autoria=False)
            fim4 = range(max(0, K - 4 * por_dia), K)            # os ultimos quatro dias (11 a 14 numa vida de 14)
            mr = mae_previsao(leituras, refeita["corpo"][str(n_pri)], n_pri, fim4, receptores, so=("fome",))
            mc = mae_previsao(leituras, cong["corpo"][str(n_pri)], n_pri, fim4, receptores, so=("fome",))
            mo = mae_previsao(leituras, oraculo["corpo"][str(n_pri)], n_pri, fim4, receptores, so=("fome",))
            adapta = {"tick_troca": tick_troca, "k_troca": k_troca, "rede": mr["mae"], "congelada": mc["mae"], "oraculo": mo["mae"],
                      "n": mr["n"], "d_adapta": None if mr["mae"] is None else mc["mae"] - mr["mae"],
                      "curva_fome": [{"dia": d + 1, **{nome: mae_previsao(leituras, prev["corpo"][str(n_pri)], n_pri,
                                                                          range(d * por_dia, min(K, (d + 1) * por_dia)),
                                                                          receptores, so=("fome",))["mae"]
                                                       for nome, prev in (("rede", refeita), ("congelada", cong))}}
                                     for d in range(dias)]}

        # a autoria: as sondas do cerebro (lidas do motivo, nunca entregues a rede)
        S = rede.S
        ped, ped_zona = [], {z: [] for z in REGRAS_PEDIDO}
        nasc = []
        for k in janela:
            r, m = regs[k], motivos[k]
            if r["acao"] != m["acao"]:
                raise RuntimeError(f"decisao {k}: a rede viu {r['acao']!r}, o cerebro decidiu {m['acao']!r}")
            cands = m["candidatos"]
            pesos_nasc = {a.value: q for a, q in zip(ACOES_REDE, r["autoria_ao_nascer"])}
            nasc.append((cands, pesos_nasc, sonda_ao_nascer(m)))
            if r["contexto"][CONTEXTO_REDE.index("pedido")] == S and m["regra"] in REGRAS_PEDIDO and "comer" in cands:
                sem = m["pedido"]["acao_sem_pedido"] if "pedido" in m else m["acao"]    # sem a sonda, o pedido nao pesou: a propria
                pesos_sem = {a.value: q for a, q in zip(ACOES_REDE, r["autoria_sem_pedido"])}
                linha = (_normalizar_cands(pesos_sem, cands)["comer"], int(sem == "comer"))
                ped.append(linha)
                ped_zona[m["regra"]].append(linha)
        bss_ped = brier_skill([p for p, _ in ped], [e for _, e in ped])
        autoria = {"bss_ped": bss_ped,
                   "bss_ped_por_zona": {z: {**brier_skill([p for p, _ in v], [e for _, e in v]),
                                            "frequencia_evento": (sum(e for _, e in v) / len(v)) if v else None}
                                        for z, v in ped_zona.items()},
                   "bss_nasc": brier_skill_multiclasse(nasc)}

        # os descritivos: os pesos no fim de cada dia e a surpresa por hora (em torno da troca e de cada tapa)
        horas = -(-K // 4)
        surpresa_hora = []
        for h in range(horas):
            vals = [v for r in regs[4 * h:4 * h + 4] for v in r["surpresa"].get(str(hz[0]), [])]
            surpresa_hora.append(sum(vals) / len(vals) if vals else None)
        ticks_tapa = sorted(int(e["tick"]) for e in (json.loads(x) for x in log.para_jsonl().splitlines())
                            if e.get("valor") == AcaoUsuario.TAPA.value)
        hora_de = lambda t: (-(-t // intervalo)) // 4      # noqa: E731  a hora da primeira decisao no tick ou depois
        horas_tapa = {hora_de(t) for t in ticks_tapa}
        hora_troca = None if tick_troca is None else hora_de(tick_troca)
        marcadas = horas_tapa | ({hora_troca} if hora_troca is not None else set())
        com = [surpresa_hora[h] for h in sorted(horas_tapa) if h < horas and surpresa_hora[h] is not None]
        sem = [v for h, v in enumerate(surpresa_hora) if h not in marcadas and v is not None]
        surpresa = {"horizonte": hz[0], "por_hora": surpresa_hora, "tapas": len(ticks_tapa),
                    "media_horas_com_tapa": (sum(com) / len(com)) if com else None,
                    "media_horas_sem_nada": (sum(sem) / len(sem)) if sem else None,
                    "hora_da_troca": hora_troca,
                    "troca": None if hora_troca is None or hora_troca >= horas else surpresa_hora[hora_troca]}
        return {"receptores": receptores, "horizontes": list(hz), "decisoes": K, "janela_k": [janela.start, janela.stop],
                "horizonte_primario": n_pri, "mae": maes, "d_si": maes[str(n_pri)]["d_si"], "d_media": maes[str(n_pri)]["d_media"],
                "curva": curva, "adaptacao": adapta, "autoria": autoria, "pesos_por_dia": refeita["pesos_por_dia"],
                "surpresa": surpresa, "cortes": rede.cortes, "n_pesos": rede.n_pesos(),
                "quimicos_do_oraculo": len(quimicos[0])}

    def medidas_corpo(self, vida: VidaBancada, motor, reg: "_Registro") -> dict | None:
        """As medidas do PLANO_ANALISE_V2_CORPO_DRIVES (secao 5), todas de metrics.py, nas vidas com o corpo ligado (None nas outras). A
        janela e a dos ultimos sete dias (os dias 8 a 14 numa vida de 14), e a vida toda sai ao lado na `BE`:
          - `BE` e `OC` (5.1): (tick, regra do instinto, acao) de cada decisao do replay de medicao;
          - o cuidado preservado (5.2): (tick, em privacao, saude, fome) de cada decisao, a privacao pela Estado.em_privacao;
          - os drives novos (5.3): a falta lida pelo receptor, na escala 0-1, de cada decisao, quando o corpo tem receptores novos;
            sem eles (o regime "quimica"), sai indisponivel, com o no."""
        cc = getattr(motor, "cc", None)
        if cc is None or not cc.ligada:
            return None
        if len(reg.corpo) != len(reg.decisoes) or any(pc is None for pc in reg.corpo):
            raise RuntimeError(f"{vida.nome}: o corpo ligado e decisao sem os receptores (Observacao.corpo)")
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        fim = self.dias * TICKS_POR_DIA
        ticks = [t for t, _, _ in reg.decisoes]
        decs = [(t, regra, a) for (t, _, a), (_, regra, _) in zip(reg.decisoes, reg.bola)]
        cuidado = [(t, p, sau, v[1]) for t, (p, sau), v in zip(ticks, reg.amostras, reg.vetores)]
        S = self.cfg_lobos.escala
        novos = [r for r in RECEPTORES_NOVOS if r in DRIVES_NOVOS_SINAL and getattr(reg.corpo[0], r) is not None]
        if novos:
            amostras = [(t, a, {r: getattr(pc, r) / S for r in novos}) for t, a, pc in zip(ticks, reg.acordado, reg.corpo)]
            drives = {"disponivel": True, "janela": medir_drives_novos(amostras, janela),
                      "vida_toda": medir_drives_novos(amostras, (0, fim))}
        else:
            drives = {"disponivel": False, "motivo": "o corpo sem receptores novos (o regime quimica, sem drives_novos)"}
        return {"regime": braco_de(vida.espec.braco).regime, "janela": list(janela), "gestos": vida.gestos,
                "be": tempo_livre_be(decs, janela), "be_vida": tempo_livre_be(decs, (0, fim)),
                "cuidado": cuidado_preservado(cuidado, janela), "drives_novos": drives,
                "corpo_final": motor.corpo.para_dict()}

    def medidas_comportamento(self, reg: "_Registro") -> dict:
        """A `BE` e o cuidado preservado (PLANO_ANALISE_V2_CORPO_DRIVES, 5.1 e 5.2) em TODA vida, com ou sem o corpo, pelas mesmas contas do
        bloco do corpo: o G-HOJE (b) compara a quimica com o "hoje", que nao tem o bloco. Janela: os ultimos sete dias."""
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        ticks = [t for t, _, _ in reg.decisoes]
        decs = [(t, regra, a) for (t, _, a), (_, regra, _) in zip(reg.decisoes, reg.bola)]
        cuidado = [(t, p, sau, v[1]) for t, (p, sau), v in zip(ticks, reg.amostras, reg.vetores)]
        return {"janela": list(janela), "be": tempo_livre_be(decs, janela), "cuidado": cuidado_preservado(cuidado, janela)}

    def medidas_tapa(self, vida: VidaBancada, motor, reg: "_Registro") -> dict:
        """Os efeitos do tapa (PLANO_ANALISE_V2_CORPO_DRIVES, secao 5.4; so descritivos), nas vidas com os gestos, pela
        `metrics.efeitos_do_tapa`: os tapas do registro, os carinhos do replay de medicao (a reducao da solidao lida pelo receptor e o sinal
        pelo corpo, a conta do cerebro, como no banheiro), as acoes e o estresse de cada decisao. Janela: os ultimos sete dias."""
        S = self.cfg_lobos.escala
        cc = getattr(reg.interna, "cfg_consequencia", self.cfg_consequencia)
        pd = dict(cc.pesos_drives_corpo)
        drives = lambda r: tuple(RECEPTOR_DO_INDICE[i] for i in cc.drives) + tuple(  # noqa: E731
            x for x in RECEPTORES_NOVOS if x in DRIVES_NOVOS_SINAL and getattr(r, x) is not None)
        tapas = [e.tick for e in motor.log if e.tipo == "acao_usuario" and str(e.valor) == AcaoUsuario.TAPA.value]
        carinhos = [(t, (antes.solidao - depois.solidao) / S, sinal_corpo(antes, depois, drives(antes), cc.ganho, S, pd))
                    for t, antes, depois in reg.carinhos]
        decs = [(t, a) for t, _, a in reg.decisoes]
        estresse = [(t, pc.estresse / S) for (t, _, _), pc in zip(reg.decisoes, reg.corpo)]
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        return efeitos_do_tapa(tapas, carinhos, decs, estresse, janela, ticks_por_dia=TICKS_POR_DIA)

    def medidas_metabolismo(self, vida: VidaBancada, motor, reg: "_Registro") -> dict:
        """A medida descritiva do metabolismo (PLANO_ANALISE_V2_CORPO_DRIVES, A3.3; TAREFA_V2_METABOLISMO, secao 6), por vida, so relato:
          - a fracao do tempo acordado com a falta de combustivel (abaixo de `falta_limiar`, C/4) e as vezes que a falta disparou, tick a
            tick, pela sonda do passo do corpo no replay de medicao (`sondar_metabolismo`);
          - o combustivel e a reserva no fim de cada dia;
          - o tempo entre comer e brincar (as decisoes do replay; o plano o pede no P1-c, e sai em toda vida com o metabolismo).
        A conta do corpo no fim (`contas_metabolismo`) sai ao lado; a sonda tem de ter um tick por tick vivido (falha alto)."""
        sonda = getattr(reg, "metabolismo", None)
        fim = self.dias * TICKS_POR_DIA
        if not sonda or len(sonda) != motor._estado.tick or [t for t, *_ in sonda] != list(range(motor._estado.tick)):
            raise RuntimeError(f"{vida.nome}: a sonda do metabolismo nao cobre a vida tick a tick")
        decs = [(t, a) for t, _, a in reg.decisoes]
        return {**metabolismo_da_vida(sonda, motor.cc.falta_limiar, TICKS_POR_DIA), "tempo_comer_brincar": tempo_comer_brincar(decs),
                "contas": dict(motor.corpo.contas_metabolismo), "fim": fim}

    def medidas_dominancia(self, vida: VidaBancada, reg: "_Registro") -> dict:
        """Adendo 2 do plano do corpo (A2.2), numa vida: por decisao observada, c_d = falta_d,antes^2 - falta_d,depois^2 por drive do
        sinal (os de ConfigConsequencia.drives; na decisao que comeu fruta, mais o humor com a E2, e o depois e o estado logo depois de
        comer), com as faltas na escala S do sinal (S - arred(h * S)) e w_d = 1 (D-4). Nos bracos que aprendem pela consequencia, e o
        sinal deles ("sinal"); nos outros, a mesma conta como sonda ("sonda"). Com os canais ligados e o aprendizado ligado, a soma por
        canal dos sinais recalculados daqui (lobos.sinal_por_canal, a mesma ordem dos drives) tem de ser o total que o cerebro guardou:
        se nao for, falha alto. A janela e a dos ultimos sete dias (os dias 8 a 14 numa vida de 14), e a vida toda sai ao lado."""
        b = self.braco(vida.espec)
        cerebro = reg.interna.cerebro
        cc = getattr(reg.interna, "cfg_consequencia", self.cfg_consequencia)
        S = self.cfg_lobos.escala
        if reg.passos_sinal and reg.passos_sinal[0]["antes_corpo"] is not None:
            return self._dominancia_pelo_corpo(vida, reg, b, cerebro, cc, S)
        acao_drives = tuple(cc.drives)
        fruta_drives = acao_drives + ((INDICE_HUMOR,) if cc.humor_na_fruta and INDICE_HUMOR not in acao_drives else ())
        falta = lambda v, ds: {NOMES_DRIVES[i]: S - arred(v[i] * S) for i in ds}  # noqa: E731
        janela = cc.pesos_janela and getattr(cerebro, "_aprende", False)
        indice_do_canal = {c: i for i, c in CANAL_DO_DRIVE.items()}
        decisoes, por_canal = [], {}
        for p in reg.passos_sinal:
            ds = fruta_drives if comeu_fruta_e2(p) else acao_drives
            pesos = None
            if janela:                  # P1-cw (A2.4): os pesos que o cerebro usou nesta decisao, o mesmo no antes e no depois
                anotados = cerebro.motivos[p["k"]].get("pesos_janela")
                if anotados is None:
                    raise RuntimeError(f"{vida.nome}: decisao {p['k']} sem os pesos da janela no motivo")
                pesos = {indice_do_canal[c]: w for c, w in anotados.items()}
                if not set(ds) <= set(pesos):      # o cerebro pesa os drives da E2 em toda decisao; a acao so usa os do N3
                    raise RuntimeError(f"{vida.nome}: os pesos da janela {sorted(pesos)} nao cobrem os drives do sinal {sorted(ds)}")
                pesos = {i: pesos[i] for i in ds}
            w_d = None if pesos is None else {NOMES_DRIVES[i]: w for i, w in pesos.items()}
            decisoes.append((p["tick"], p["regra"],
                             contribuicao_drives(falta(p["antes"], ds), falta(p["depois"], ds), w_d, escala=S)))
            for canal, f in sinal_por_canal(p["antes"], p["depois"], ds, cc.ganho, S, pesos).items():
                por_canal[canal] = por_canal.get(canal, 0) + f
        canais = getattr(cerebro, "_canais", None)
        conferido = False
        if b.fonte in APRENDE_PELA_CONSEQUENCIA and cc.canais_ligados and getattr(cerebro, "_aprende", False):
            if canais is None or canais["creditos"] != len(reg.passos_sinal):
                raise RuntimeError(f"{vida.nome}: o cerebro creditou {None if canais is None else canais['creditos']} decisoes, "
                                   f"a medida viu {len(reg.passos_sinal)}")
            if any(canais["por_canal"].get(c, 0) != v for c, v in por_canal.items()):
                raise RuntimeError(f"{vida.nome}: o sinal por drive da medida e o dos canais do cerebro divergem")
            conferido = True
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        return {"origem": "sinal" if b.fonte in APRENDE_PELA_CONSEQUENCIA else "sonda", "conferido_com_canais": conferido,
                "janela": list(janela), "na_janela": dominancia_decisoes(decisoes, janela),
                "vida_toda": dominancia_decisoes(decisoes, (0, self.dias * TICKS_POR_DIA))}

    def _dominancia_pelo_corpo(self, vida: VidaBancada, reg: "_Registro", b: Braco, cerebro, cc: ConfigConsequencia, S: int) -> dict:
        """A dominancia (A2.2) com o corpo ligado: a conta do sinal pelo corpo (`lobos.contribuicoes_corpo`, secao 9 da tarefa), sobre
        os receptores da decisao e os de depois dos estimulos da propria acao (o gancho `consequencia_corpo`), com os w_d inteiros da
        `ConfigConsequencia.pesos_drives_corpo` e, com a `pesos_janela`, o peso da janela do motivo. Os drives: os do N3, o humor so no
        comer de fruta (E2) e os novos que o corpo tiver (o susto fora), pelos nomes do corpo. Nos bracos que aprendem pela consequencia,
        a contribuicao de cada decisao tem de ser a que o cerebro gravou no motivo (`sinal_corpo`) e, com os canais, a soma por canal a dos
        canais dele: se nao for, falha alto."""
        nomes = {"fome": "fome", "higiene": "desconforto", "energia": "cansaco", "humor": "tristeza"}
        pd = dict(cc.pesos_drives_corpo)
        aprende = (b.fonte in APRENDE_PELA_CONSEQUENCIA and getattr(cerebro, "_aprende", False)
                   and getattr(cerebro, "_corpo", None) is not None)
        decisoes, por_canal = [], {}
        for p in reg.passos_sinal:
            antes, depois = p["antes_corpo"], p["depois_corpo"]
            if antes is None or depois is None:
                raise RuntimeError(f"{vida.nome}: decisao {p['k']} sem os receptores de antes ou de depois (o gancho do corpo)")
            drives = tuple(RECEPTOR_DO_INDICE[i] for i in cc.drives)
            if comeu_fruta_e2(p) and cc.humor_na_fruta and "humor" not in drives:
                drives = drives + ("humor",)
            drives = drives + tuple(r for r in RECEPTORES_NOVOS if r in DRIVES_NOVOS_SINAL and getattr(antes, r) is not None)
            pesos = None
            motivo = cerebro.motivos[p["k"]] if aprende else None
            if aprende and cc.pesos_janela:
                anotados = motivo.get("pesos_janela")
                if anotados is None or not set(drives) <= set(anotados):
                    raise RuntimeError(f"{vida.nome}: decisao {p['k']} sem os pesos da janela dos drives {drives} no motivo")
                pesos = {d: anotados[d] for d in drives}
            c = contribuicoes_corpo(antes, depois, drives, S, pd, pesos)
            if aprende and motivo.get("sinal_corpo", {}).get("drives") != c:
                raise RuntimeError(f"{vida.nome}: decisao {p['k']}: a contribuicao da medida e a do cerebro divergem")
            decisoes.append((p["tick"], p["regra"], {nomes.get(d, d): v for d, v in c.items()}))
            for canal, f in sinal_corpo_canais(antes, depois, drives, cc.ganho, S, pd, pesos).items():
                por_canal[canal] = por_canal.get(canal, 0) + f
        canais = getattr(cerebro, "_canais", None)
        conferido = False
        if aprende and cc.canais_ligados:
            if canais is None or canais["creditos"] != len(reg.passos_sinal):
                raise RuntimeError(f"{vida.nome}: o cerebro creditou {None if canais is None else canais['creditos']} decisoes, "
                                   f"a medida viu {len(reg.passos_sinal)}")
            if any(canais["por_canal"].get(c, 0) != v for c, v in por_canal.items()):
                raise RuntimeError(f"{vida.nome}: o sinal por drive da medida e o dos canais do cerebro divergem")
            conferido = True
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        # o passo 3 da 6.2 (o w_novos): por decisao de tempo livre com sinal na janela, a soma |c_d| dos drives novos (NOVOS_W) e a dos
        # outros, com os pesos desta vida; o orquestrador da calibracao escala os novos por w e tira a mediana da parcela
        novos_livres = []
        for t, regra, c in decisoes:
            if janela[0] <= t < janela[1] and regra in REGRAS_TEMPO_LIVRE and sum(c.values()) != 0:
                a = sum(abs(v) for d, v in c.items() if d in NOVOS_W)
                novos_livres.append([a, sum(abs(v) for v in c.values()) - a])
        return {"origem": "sinal" if b.fonte in APRENDE_PELA_CONSEQUENCIA else "sonda", "conferido_com_canais": conferido,
                "conferido_com_motivo": bool(aprende), "pelo_corpo": True, "janela": list(janela),
                "na_janela": dominancia_decisoes(decisoes, janela),
                "vida_toda": dominancia_decisoes(decisoes, (0, self.dias * TICKS_POR_DIA)),
                "novos_livres": novos_livres}

    def medidas_banheiro(self, vida: VidaBancada, motor, reg: "_Registro") -> dict:
        """As medidas do PLANO_ANALISE_V2_BANHEIRO (secoes 4 e 8) numa vida do 2 x 2, pela `medidas_banheiro_de`. Le:
          - do motor (o contrato da etapa 3 do A, conferido aqui): `motor.alivios`, um dict por `aliviar`, com `tick` (o da decisao),
            `dentro` (terminou dentro do banheiro), `urgente` (a regra urgente, o acidente), `alvo` ("banheiro" ou "aqui"),
            `distancia` (do pet ao banheiro na decisao, em subunidades) e `recolhido` (o limpador recolheu a necessidade);
          - do replay de medicao (_Registro): os carinhos (`mudanca_no_corpo`: o tick, a solidao antes e o sinal pelo corpo, a conta do
            cerebro) e a transicao de cada decisao (o sinal do alivio recolhido pelo limpador, a mesma conta) e o cuidado de cada decisao;
          - do cerebro no fim de cada dia (o replay do mundo cortado no dia): os pesos do alvo `banheiro` e `aqui`."""
        alivios = getattr(motor, "alivios", None)
        if alivios is None:
            raise NotImplementedError(f"{vida.nome}: o motor sem os alivios ({NOS_PENDENTES.get('banheiro', 'a etapa 3 do banheiro')})")
        chaves = {"tick", "dentro", "urgente", "alvo", "distancia", "recolhido"}
        if any(set(a) != chaves for a in alivios):
            raise RuntimeError(f"{vida.nome}: alivio fora do contrato {sorted(chaves)}")
        cc = getattr(reg.interna, "cfg_consequencia", self.cfg_consequencia)
        S = self.cfg_lobos.escala
        pd = dict(cc.pesos_drives_corpo)
        # os drives do sinal pelo corpo, como na dominancia: os do N3 e os novos que o corpo tem (o susto fora); a conta do cerebro
        drives = lambda r: tuple(RECEPTOR_DO_INDICE[i] for i in cc.drives) + tuple(  # noqa: E731
            x for x in RECEPTORES_NOVOS if x in DRIVES_NOVOS_SINAL and getattr(r, x) is not None)
        sinal = lambda antes, depois: sinal_corpo(antes, depois, drives(antes), cc.ganho, S, pd)  # noqa: E731
        carinhos = [(t, antes.solidao / S, sinal(antes, depois)) for t, antes, depois in reg.carinhos]
        por_tick = {p["tick"]: p for p in reg.passos_sinal}
        limpador = []
        for a in alivios:
            if a["recolhido"]:
                p = por_tick.get(a["tick"])
                if p is None or p["antes_corpo"] is None or p["depois_corpo"] is None:
                    raise RuntimeError(f"{vida.nome}: alivio recolhido no tick {a['tick']} sem a decisao e os receptores dela")
                limpador.append((a["tick"], sinal(p["antes_corpo"], p["depois_corpo"])))
        ticks = [t for t, _, _ in reg.decisoes]
        cuidado = [(t, p, sau, v[1]) for t, (p, sau), v in zip(ticks, reg.amostras, reg.vetores)]
        fab, fm, T = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec), TICKS_POR_DIA
        pesos = None                             # o instinto do alivio nao aprende o alvo (o herdado, sem pesos)
        if vida.espec.cerebro == "lobos":
            pesos = [do_braco(reproduzir_mundo(vida.motor.log, fab, semente=vida.espec.semente, fabrica_motor=fm, ate_tick=d * T)
                              .politica).cerebro.estado_interno()["pesos_alvo"] for d in range(1, self.dias + 1)]
        return medidas_banheiro_de([(a["tick"], a["dentro"], a["urgente"]) for a in alivios], self.dias, carinhos, limpador, pesos,
                                   cuidado, [(a["tick"], a["alvo"], a["dentro"], a["distancia"]) for a in alivios if not a["urgente"]])

    def medidas_mundo(self, vida: VidaBancada, motor: MotorMundo, reg: "_Registro") -> dict:
        """As medidas do PLANO_ANALISE_V2_MUNDO_FISICO (secao 5 e adendo 1, A1.8), todas de digilab/metrics.py, numa vida do mundo fisico.
        A janela e a dos ultimos sete dias (os dias 8 a 14 numa vida de 14; a vida toda se ela for mais curta), e a vida toda sai ao lado
        no D_FE. Do motor (os registros do MotorMundo): a posicao depois de cada decisao (`decisoes_mundo`, a trajetoria), os troncos, as
        quedas (o fluxo mundo-arvores: as `sorteadas`, que nao dependem do pet) e os consumos (a fome ganha); do replay de medicao
        (_Registro): o estado em cada decisao e se o pet estava acordado. As visitas recontadas pela metrica sao conferidas contra as que
        o motor registrou (`visitas`): uma diferenca falha alto."""
        fim = self.dias * TICKS_POR_DIA
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        decs = motor.decisoes_mundo
        if len(decs) != len(reg.vetores):
            raise RuntimeError(f"{vida.nome}: {len(decs)} decisoes no mundo e {len(reg.vetores)} no replay de medicao")
        ticks = [d["tick"] for d in decs]
        fe = [(t, v[1], v[3]) for t, v in zip(ticks, reg.vetores)]                    # (tick, fome, energia) da decisao
        cuidado = [(t, p, s, v[1]) for t, (p, s), v in zip(ticks, reg.amostras, reg.vetores)]
        traj = [(d["tick"], d["x"], d["y"]) for d in decs]
        if not traj or traj[0][0] > 0:                                                # o nascimento, no ninho
            traj = [(0, *centro_da_celula(motor.cmf.layout.ninho, motor.cmf))] + traj
        arvores = {a["id"]: (a["x"], a["y"]) for a in motor.arvores}
        quedas = [q["tick"] for q in motor.quedas for _ in range(q["sorteadas"])]
        todas = visitas_manchas(traj, arvores, fim, (0, fim), quedas=quedas, raio_celulas=motor.cmf.raio_mancha_celulas)
        recontadas = sorted((v["arvore"], v["inicio"], v["fim"], v["decisoes_dentro"]) for v in todas if not v["censurada"])
        if recontadas != sorted((v["arvore"], v["chegada"], v["saida"], v["decisoes"]) for v in motor.visitas):
            raise RuntimeError(f"{vida.nome}: as visitas da metrica e as do motor divergem")
        visitas = [v for v in todas if janela[0] <= v["inicio"] < janela[1]]
        ganhos = [(c["tick"], c["fome_depois"] - c["fome_antes"]) for c in motor.consumos_mundo]
        horas = sum(reg.acordado) * CONFIG_PADRAO.intervalo_decisao_ticks / 60.0
        return {"janela": list(janela), "d_fe": deficit_fome_energia(fe, janela), "d_fe_vida": deficit_fome_energia(fe, (0, fim)),
                "cuidado": cuidado_preservado(cuidado, janela), "visitas": visitas,
                "permanencia_custo": inclinacao_permanencia(visitas, "custo_viagem"),
                "permanencia_taxa": inclinacao_permanencia(visitas, "taxa_recente"),
                "taxa_no_abandono": taxa_no_abandono(visitas, ganhos, horas), "permanencia_media": permanencia_media(visitas),
                "horas_acordado": horas, "deixadas": len(motor.deixadas), "consumos": len(motor.consumos_mundo),
                "quedas": len(motor.quedas)}

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
        # corpo: o prior e o P0 do mesmo regime, e as sondas ganham os receptores do proprio estado (o cerebro com o corpo os exige)
        regime = braco_de(vida.espec.braco).regime
        p0 = {"quimica": "P0-quimica", "corpo": "P0-c"}.get(regime, "P0")
        corpo = self.cfg_corpo_de(vida.espec)
        if corpo is not None:
            # os receptores novos de cada estado sorteados pela rng propria da sonda (sonda-corpo), na ordem dos estados
            rng = random.Random(derivar_semente("sonda-corpo", sonda["semente"]))
            com_mundo = mundo_de(vida.espec.mundo).fisico is not None
            estados = [replace(o, corpo=percepcao_da_sonda(o, corpo, rng, com_mundo)) for o in estados]
        prior = do_braco(self.politica(replace(vida.espec, braco=p0), CONFIG_PADRAO))   # sem a rede: a sonda nao a alimenta
        d_prior = distribuicoes_de_acao(prior, estados, sonda["amostras"], sonda["semente"])
        fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
        log = vida.motor.log
        serie = []
        fisico = mundo_de(vida.espec.mundo).fisico is not None
        for d in range(1, self.dias + 1):
            # a sonda le o cerebro do braco direto: o embrulho da bola mexeria no motor e poria a bola nos estados da sonda. O mundo
            # fisico tem eventos proprios no log: o replay dele, com o mesmo corte no tick
            if fisico:
                pol = do_braco(reproduzir_mundo(log, fab, semente=vida.espec.semente, fabrica_motor=fm,
                                                ate_tick=d * TICKS_POR_DIA).politica)
            else:
                pol = do_braco(politica_no_tick(log, fab, vida.espec.semente, d * TICKS_POR_DIA, fm))
            serie.append(jsd_media(distribuicoes_de_acao(pol, estados, sonda["amostras"], sonda["semente"]), d_prior))
        return serie

    # ------------------------------------------------------------- dois pets: o grupo (TAREFA_V2_DOIS_PETS, etapa 5)


    def bancada_grupo(self) -> "Bancada":
        """O cerebro A do plano (secao 2): o do ponto e da montagem da bancada, com o que a etapa 4 acrescenta: o alvo aprendido (#255; o
        P0 com o aprendizado desligado fica no alvo padrao do motor), as entradas sociais (prior 0) e o modelo dos outros (so registrado;
        #266). No prior, o P0 e o instinto do mundo byte a byte, tambem com o outro a vista (o gate do #266). E a rota do canal do humor no
        mundo fisico (#269, `presenca_fruta_mundo`: a decisao de comer le a fruta madura a vista, prior 0), sem a qual os canais da montagem
        completa falham alto ao comer a fruta que mexe no humor."""
        return replace(self, cfg_lobos=replace(self.cfg_lobos, alvo_aprendido=True, entradas_sociais=True, modelo_outros=True,
                                               presenca_fruta_mundo=True))

    def canais_no_pet(self, espec: EspecVida) -> bool:
        """Os canais da consequencia chegam ao cerebro deste pet? So nas fontes que aprendem pela consequencia, com os canais do braco
        montado (a montagem completa os liga no P1) ou, sem eles fixos, os da config."""
        b = self.braco(espec)
        if b.fonte not in APRENDE_PELA_CONSEQUENCIA:
            return False
        return self.cfg_consequencia.canais_ligados if b.canais is None else b.canais

    def orcamento_por_dia(self) -> int:
        if self.orcamento % self.dias:
            raise ValueError(f"o grupo tem orcamento por dia vivido: {self.orcamento} interacoes em {self.dias} dias nao divide")
        return self.orcamento // self.dias


    def dias_do_grupo(self, eg: EspecGrupo) -> int:
        """O grupo vive K + `dias` (o B vive os `dias` da bancada depois do dia K); o "A-so", os `dias`."""
        return eg.k + self.dias if BRACOS_GRUPO[eg.braco].b else self.dias


    def espec_do_pet(self, eg: EspecGrupo, ident: str) -> EspecVida:
        braco = dict((i, b) for i, b, _ in _entradas(eg))[ident]
        semente = sementes_do_grupo(eg.semente, CONFIG_GRUPO_LIGADA.ids)[ident]
        return EspecVida(eg.dono, braco, semente, None, eg.mundo, lugar=eg.lugar)


    def efeitos_do_grupo(self, eg: EspecGrupo) -> dict:
        """O efeito verdadeiro (o tipo ruim da unidade) e, no A embaralhado, o desarranjado dos K dias."""
        ruim = tipo_ruim(eg.semente)
        out = {"ruim": ruim, "verdadeiro": efeito_dois_pets(ruim, self.cfg_frutas)}
        if BRACOS_GRUPO[eg.braco].companheiro == "embaralhado":
            pi = desarranjo_dois_pets(eg.semente)
            out.update({"pi": pi, "ruim_embaralhado": pi[ruim], "embaralhado": efeito_dois_pets(pi[ruim], self.cfg_frutas)})
        return out


    def fabrica_motor_do_grupo(self, eg: EspecGrupo, ident: str):
        """A fabrica do motor de um pet do grupo, no formato do Grupo.entrar (`mundo=`, `entrada_mundo=`): o MotorMundo do plano do mundo
        (obediencia, educacao, lesoes, frutas e bola de hoje desligadas, especie brasa, temperamento neutro), com o efeito das frutas da unidade;
        o A embaralhado, o MotorMundoTroca. Sem `mundo`, o MotorMundo dono do proprio Mundo (a vida de hoje, para o gate do pet sozinho)."""
        cm = self.cfg_mundo_de(mundo_de(eg.mundo))
        ef = self.efeitos_do_grupo(eg)
        embaralha = ident == "A" and BRACOS_GRUPO[eg.braco].companheiro == "embaralhado"
        tick_troca = eg.k * TICKS_POR_DIA

        def fabrica(politica, cfg, semente, mundo=None, entrada_mundo=0):
            kw = dict(obediencia_desligada=True, semente_genoma=None, cfg_mundo=cm, mundo=mundo, entrada_mundo=entrada_mundo)
            if embaralha:
                return MotorMundoTroca(politica, cfg, semente, NEUTRO, "brasa", efeito_frutas=ef["embaralhado"], tick_troca=tick_troca,
                                       efeito_depois=ef["verdadeiro"], **kw)
            return MotorMundo(politica, cfg, semente, NEUTRO, "brasa", efeito_frutas=ef["verdadeiro"], **kw)
        return fabrica


    def pets_do_grupo(self, eg: EspecGrupo, envolver=None) -> list[PetDoGrupo]:
        """Os PetDoGrupo do `simular_grupo`: a politica do braco de cada pet pela bancada (o cerebro A com o alvo aprendido), a fabrica do
        motor e o dono, um por pet (o DonoComLugar sobre o dono da v1, com a semente do pet: as rngs `dono` e `dono-lugar` sao dele).
        `envolver(ident, politica)` embrulha a politica (o _RegistroGrupo do replay de medicao)."""
        _validar_espec_grupo(eg)
        bg_ = self.bancada_grupo()
        cm = self.cfg_mundo_de(mundo_de(eg.mundo))
        pets = []
        for ident, braco, entrada in _entradas(eg):
            espec = self.espec_do_pet(eg, ident)

            def fp(cfg=None, e=espec, i=ident):
                p = bg_.politica(e, cfg)
                return p if envolver is None else envolver(i, p)
            dono = DonoComLugar(criar_dono(eg.dono), eg.lugar, espec.semente, eg.dono, cm)
            pets.append(PetDoGrupo(ident, entrada, fp, self.fabrica_motor_do_grupo(eg, ident), dono, eg.dono,
                                   cerebro=f"{espec.cerebro}/{braco}"))
        return pets


    def cfg_grupo(self) -> ConfigGrupo:
        return replace(CONFIG_GRUPO_LIGADA, orcamento_por_dia=self.orcamento_por_dia())


    def grupo(self, eg: EspecGrupo) -> VidaGrupo:
        """O grupo da celula (DP-7, a validacao inicial), pelo `simular_grupo`: um dono para todos, decidindo por pet, com o orcamento por dia
        vivido de cada um e so com o cuidado (o CanalSemEnsino ao vivo, PMF-3). O G1 do grupo e conferido antes de devolver."""
        _validar_espec_grupo(eg)
        canais: list = []

        class _Canal(CanalSemEnsino):
            def __init__(s, *a, **kw) -> None:
                super().__init__(*a, **kw)
                canais.append(s)

        g = simular_grupo(self.cfg_mundo_de(mundo_de(eg.mundo)), eg.semente, self.pets_do_grupo(eg), self.dias_do_grupo(eg),
                          cfg_grupo=self.cfg_grupo(), cfg=CONFIG_PADRAO, canal_classe=_Canal)
        retirados = {c.motor.ident: c.retirados for c in canais}
        if set(retirados) != set(g.motores):
            raise RuntimeError(f"{eg.nome}: canais {sorted(retirados)} para os pets {sorted(g.motores)}")
        vida = VidaGrupo(eg, g, dict(g.interacoes), retirados)
        self.conferir_replay_grupo(vida)
        return vida


    def rejogar_grupo(self, registro: RegistroGrupo, eg: EspecGrupo, envolver=None) -> Grupo:
        fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in self.pets_do_grupo(eg, envolver)}
        return reproduzir_grupo(registro, fabricas, self.cfg_mundo_de(mundo_de(eg.mundo)), self.cfg_grupo(), CONFIG_PADRAO)


    def conferir_replay_grupo(self, vida: VidaGrupo, texto: str | None = None) -> None:
        """G1 do grupo: rejoga o registro do grupo a partir do texto (do disco, se vier) e compara tudo bit a bit (o mundo, as vezes
        sorteadas, a rng da ordem e cada pet: log, estado, acoes, rngs, registros do mundo fisico, estado interno da politica)."""
        proprio = vida.grupo.registro.para_jsonl()
        texto = proprio if texto is None else texto
        if texto != proprio:
            raise ReplayDivergiu(f"{vida.nome}: o registro do disco nao e o do grupo")
        r = self.rejogar_grupo(RegistroGrupo.de_jsonl(texto), vida.espec)
        if _resumo_grupo(r) != _resumo_grupo(vida.grupo):
            raise ReplayDivergiu(f"{vida.nome}: o grupo diverge no replay")


    def chao_na_entrada(self, vida: VidaGrupo, ident: str = "B") -> dict:
        """O chao do mundo quando o pet `ident` entra (R-3, so descritivo; o B no dia K): o registro do grupo rejogado ate logo antes da entrada
        dele, com o mundo atualizado ate o tick (a atualizacao e idempotente e so le o tick e o fluxo das arvores). Conta as comidas por tipo e
        situacao."""
        reg = vida.grupo.registro
        idx = [k for k, e in enumerate(reg.eventos) if e.tipo == "entrada" and e.valor == ident]
        if len(idx) != 1:
            raise ValueError(f"{vida.nome}: o pet {ident!r} nao entrou uma vez no registro")
        antes = reg.eventos[:idx[0]]
        entrados = [e.valor for e in antes if e.tipo == "entrada"]
        cab = {**reg.cabecalho, "pets": {i: dict(reg.cabecalho["pets"][i]) for i in entrados}}
        fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in self.pets_do_grupo(vida.espec) if p.ident in entrados}
        g = reproduzir_grupo(RegistroGrupo(cab, list(antes)), fabricas, self.cfg_mundo_de(mundo_de(vida.espec.mundo)), self.cfg_grupo(),
                             CONFIG_PADRAO)
        g.mundo.atualizar(g.tick)
        contagem: dict = {}
        for c in g.mundo.comidas.values():
            chave = f"{c['tipo']}/{g.mundo.situacao(c, g.tick)}"
            contagem[chave] = contagem.get(chave, 0) + 1
        return {"tick": g.tick, "comidas": dict(sorted(contagem.items()))}


    def medidas_sociais(self, vida: VidaGrupo) -> dict:
        """Os descritivos da secao 4 que vem dos sentidos (etapa 3 do A, #263), por pet, dos registros do grupo e de cada motor:
          - o uso dos candidatos sociais: por dia vivido, as decisoes de explorar e quantas foram ao `seguir` e ao `onde_comeu` (o alvo de
            `decisoes_mundo`; a fracao None sem explorar no dia);
          - o que o pet viu: os consumos do outro que ele viu (`vistos_comer`), por tipo e situacao (o consumo do outro no mesmo tick; um
            consumo visto sem consumo do outro falha alto), e quantos do tipo ruim maduros;
          - a disputa (`Grupo.disputas`): quantas, quantas o pet ganhou e, em cada uma, a distancia dele e a do outro a comida;
          - o toque (`Grupo.contatos`): os contatos por tipo (disputa, encostar, esbarrar), por dia vivido;
          - o tempo a vista (`a_vista`), as idas a `onde_comeu` (chegou, comeu) e as decisoes no grupo.
        O modelo dos outros sai em `modelo_dos_outros`."""
        g = vida.grupo
        ruim = self.efeitos_do_grupo(vida.espec)["ruim"]
        fim = g.tick
        out = {}
        for ident, m in g.motores.items():
            entrada = m.entrada_mundo
            dias = (fim - entrada) // TICKS_POR_DIA
            dia = lambda t, e=entrada: (t - e) // TICKS_POR_DIA  # noqa: E731
            uso = [{"dia": d + 1, "explorar": 0, "seguir": 0, "onde_comeu": 0} for d in range(dias)]
            for dec in m.decisoes_mundo:
                if dec["acao"] == "explorar":
                    u = uso[dia(dec["tick"])]
                    u["explorar"] += 1
                    if dec["alvo"] in ("seguir", "onde_comeu"):
                        u[dec["alvo"]] += 1
            for u in uso:
                for c in ("seguir", "onde_comeu"):
                    u[f"fracao_{c}"] = u[c] / u["explorar"] if u["explorar"] else None
            vistos: dict = {}
            vistos_ruins = 0
            for vc in m.vistos_comer:
                comidos = [c for c in g.motores[vc["outro"]].consumos_mundo if c["tick"] == vc["tick"]]
                if len(comidos) != 1:
                    raise RuntimeError(f"{vida.nome}/{ident}: consumo visto no tick {vc['tick']} sem um consumo do {vc['outro']}")
                c = comidos[0]
                chave = f"{c['tipo']}/{c['situacao']}"
                vistos[chave] = vistos.get(chave, 0) + 1
                vistos_ruins += c["tipo"] == ruim and c["situacao"] == "madura"
            disputas = []
            for d in g.disputas:
                if ident in (d["vencedor"], d["perdedor"]):
                    ganhou = d["vencedor"] == ident
                    primeiro = None if d["vencedor_primeiro"] is None else d["vencedor_primeiro"] == ganhou
                    disputas.append({"tick": d["tick"], "tipo": d["tipo"], "ganhou": ganhou, "veio_primeiro": primeiro,
                                     "d_eu": d["d_vencedor" if ganhou else "d_perdedor"],
                                     "d_outro": d["d_perdedor" if ganhou else "d_vencedor"], "contato": d["contato"]})
            toque = [{"dia": d + 1} for d in range(dias)]
            for c in g.contatos:
                if ident in c["pets"]:
                    t = toque[dia(c["tick"])]
                    t[c["tipos"][ident]] = t.get(c["tipos"][ident], 0) + 1
            rs = m.resumo_social()
            idas = rs["idas_onde_comeu"]
            out[ident] = {"uso_candidatos": uso,
                          "vistos_comer": {"n": len(m.vistos_comer), "por_tipo": dict(sorted(vistos.items())), "ruins_maduros": vistos_ruins},
                          "disputas": {"n": len(disputas), "ganhou": sum(x["ganhou"] for x in disputas), "lista": disputas},
                          "toque_por_dia": toque, "a_vista": dict(rs["a_vista"]), "decisoes_no_grupo": rs["decisoes_no_grupo"],
                          "idas_onde_comeu": {"n": len(idas), "chegou": sum(1 for i in idas if i["chegou"]),
                                              "comeu": sum(1 for i in idas if i["comeu"] is not None)}}
        return out

    def modelo_dos_outros(self, vida: VidaGrupo) -> dict:
        """O modelo dos outros no fim da vida (plano, secao 4: a familiaridade, a confianca por atividade e a afinidade de cada pet sobre o
        outro; so registradas, DP-8), por pet, como o cerebro o serializa (`estado_interno()["modelo_outros"]["outros"]`). O cerebro do
        grupo sempre o tem (`bancada_grupo`): um cerebro sem ele falha alto. O por dia sai do replay de medicao (`medir_grupo`)."""
        out = {}
        for ident, m in vida.grupo.motores.items():
            interno = m.politica.estado_interno()
            if "modelo_outros" not in interno:
                raise RuntimeError(f"{vida.nome}/{ident}: o cerebro sem o modelo dos outros (a chave modelo_outros)")
            out[ident] = interno["modelo_outros"]["outros"]
        return out

    def medir_grupo(self, vida: VidaGrupo) -> dict:
        """As medidas da secao 4 que ja tem dado no registro do grupo, do replay de medicao (conferido bit a bit contra o grupo):
          - a R de cada pet (`metrics.taxa_fruta_ruim` sobre os consumos de fruta madura, com o efeito vigente do tipo no tick): no B, os 7
            primeiros dias (a primaria, PDP-2), a vida toda e um por dia; no A, um por dia, ate o dia K e depois (o A embaralhado pelo efeito
            de cada lado da troca);
          - o custo de ter companhia: o D_FE e a privacao (`deficit_fome_energia`, `cuidado_preservado`) nos 7 primeiros dias e na vida toda;
          - o alvo aprendido: os pesos por classe no fim de cada dia (o "o que o B aprendeu", com as classes `seguir` e `onde_comeu`);
          - a sorte da ordem (R-5, `vez_no_grupo`) e o chao no dia K (R-3);
          - os consumos por tipo, situacao e como (achou ou foi comer), o gasto do dono e os sinais retirados (PMF-3).
        As medidas sociais (`medidas_sociais`, da etapa 3) e o modelo dos outros (`modelo_dos_outros`, no fim, e por dia em cada pet) saem
    ao lado."""
        eg = vida.espec
        regs: dict = {}

        def envolver(ident, politica):
            regs[ident] = _RegistroGrupo(politica)
            return regs[ident]

        r = self.rejogar_grupo(vida.grupo.registro, eg, envolver)
        if _resumo_grupo(r) != _resumo_grupo(vida.grupo):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou o grupo")
        ef = self.efeitos_do_grupo(eg)
        fim_grupo = self.dias_do_grupo(eg) * TICKS_POR_DIA
        dia_k = eg.k * TICKS_POR_DIA
        pets = {}
        for ident, m in r.motores.items():
            reg = regs[ident]
            reg.fim()
            decs = m.decisoes_mundo
            if len(decs) != len(reg.vetores):
                raise RuntimeError(f"{vida.nome}/{ident}: {len(decs)} decisoes no mundo e {len(reg.vetores)} no replay de medicao")
            intervalo = CONFIG_PADRAO.intervalo_decisao_ticks
            ticks = [d["tick"] for d in decs]
            if ticks != [m.entrada_mundo + k * intervalo for k in range(len(ticks))]:
                raise RuntimeError(f"{vida.nome}/{ident}: decisoes fora da grade do pet")
            entrada = m.entrada_mundo
            dias_vividos = (fim_grupo - entrada) // TICKS_POR_DIA
            efeito_no_tick = m.efeito_no_tick if isinstance(m, MotorMundoTroca) else (lambda t: ef["verdadeiro"])  # noqa: E731
            frutas = [(c["tick"], efeito_no_tick(c["tick"])[c["tipo"]]) for c in m.consumos_mundo
                      if c["tipo"] in FRUTAS and c["situacao"] == "madura"]
            vida_j = (entrada, fim_grupo)
            primeiros = (entrada, entrada + min(JANELA_PRIMARIA_DIAS, dias_vividos) * TICKS_POR_DIA)
            janelas = {"vida": vida_j, "primeiros_7": primeiros}
            if entrada < dia_k:                                   # o A que vive os K dias antes do B
                janelas.update({"ate_k": (entrada, dia_k), "depois_k": (dia_k, fim_grupo)})
            for d in range(dias_vividos):
                janelas[f"dia_{d + 1}"] = (entrada + d * TICKS_POR_DIA, entrada + (d + 1) * TICKS_POR_DIA)
            fe = [(t, v[1], v[3]) for t, v in zip(ticks, reg.vetores)]
            cuidado = [(t, p, s, v[1]) for t, (p, s), v in zip(ticks, reg.amostras, reg.vetores)]
            consumos: dict = {}
            for c in m.consumos_mundo:
                chave = f"{c['tipo']}/{c['situacao']}/{c['como']}"
                consumos[chave] = consumos.get(chave, 0) + 1
            pets[ident] = {"braco": dict((i, b) for i, b, _ in _entradas(eg))[ident], "semente": m.semente, "entrada": entrada,
                           "dias_vividos": dias_vividos, "taxa_fruta_ruim": taxa_fruta_ruim(frutas, janelas),
                           "d_fe": {"primeiros_7": deficit_fome_energia(fe, primeiros), "vida": deficit_fome_energia(fe, vida_j)},
                           "cuidado": {"primeiros_7": cuidado_preservado(cuidado, primeiros), "vida": cuidado_preservado(cuidado, vida_j)},
                           "pesos_alvo_por_dia": reg.pesos_alvo_dia, "modelo_outros_por_dia": reg.modelo_dia,
                       "vez": vez_no_grupo(r.ordens, ident),
                           "consumos": dict(sorted(consumos.items())), "consumos_fruta_madura": len(frutas),
                           "interacoes": vida.interacoes.get(ident), "retirados": vida.retirados.get(ident),
                           "troca": getattr(m, "troca", None)}
        b = BRACOS_GRUPO[eg.braco]
        return {"grupo": vida.nome, "braco": eg.braco, "companheiro": b.companheiro, "semente": eg.semente, "k": eg.k, "dono": eg.dono,
                "lugar": eg.lugar, "mundo": eg.mundo, "ruim": ef["ruim"], "ruim_embaralhado": ef.get("ruim_embaralhado"),
                "ordens": len(r.ordens), "pets": pets, "chao_no_dia_k": self.chao_na_entrada(vida) if b.b else None,
                "sociais": self.medidas_sociais(vida), "modelo_dos_outros": self.modelo_dos_outros(vida)}


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .mundos import (CalendarioFrutas, CONFIG_JULGAMENTO_FORA, efeitos_da_condicao, JULGAMENTOS, LAYOUTS_FISICO,  # noqa: E402
                     MotorFrutasMundo, Mundo, mundo_de)
from .bracos import (ACOES, APRENDE_PELA_CONSEQUENCIA, Braco, braco_de, braco_montado, BRACOS, BRACOS_BANHEIRO, CEREBROS,  # noqa: E402
                     cfg_lobos_do_braco, filtro_de, MONTAGENS, NOMES_DRIVES, NOS_PENDENTES, NOVOS_W, PoliticaDoBraco)
from .vida import (contar_acoes, contar_gestos_mundo, EspecVida, filtrar_log, _interno, ReplayDivergiu, resumo_motor,  # noqa: E402
                   VidaBancada)
from .regras_mundo import (CanalSemEnsino, comeu_fruta_e2, DonoTapaFruta, fruta_tapa, InformanteAcoplado, InformanteDoMundo,  # noqa: E402
                           _julgar, _Registro, RegraBola, RegraFrutasComInformante, RegraFrutasComJulgador,
                           RegraFrutasComPedinte, simular_vida_fisico, simular_vida_mundo, sondar_metabolismo)
from .medidas import (do_braco, _estado_rede, medidas_banheiro_de, _normalizar_cands, percepcao_da_sonda,  # noqa: E402
                      PoliticaComRedeSemOrgaos, rede_de, rede_offline, sonda_ao_nascer, sondar_quimicos)
from .grupo import (BRACOS_GRUPO, desarranjo_dois_pets, efeito_dois_pets, _entradas, EspecGrupo, JANELA_PRIMARIA_DIAS,  # noqa: E402
                    MotorMundoTroca, _RegistroGrupo, _resumo_grupo, tipo_ruim, _validar_espec_grupo, VidaGrupo)
