"""O corpo do Creatures 3 por baixo dos drives (V2, W-CORPO-QUIMICA e W-CORPO-DIGESTAO; docs/TAREFA_V2_CORPO_DRIVES.md, secao 14).

Etapa 1: a quimica dos drives de hoje, sem orgao (secao 4). Cinco quimicos guardam a FALTA de cada drive, em inteiros de [0, C]:

    fome         -> fome      (o drive lido e (C - q) / C)
    desconforto  -> higiene
    cansaco      -> energia
    tristeza     -> humor
    dano         -> saude

Os numeros sao os de hoje, convertidos para a escala C = 450000 (CD-1): o mmc dos denominadores das taxas de hoje, entao toda taxa e
todo efeito de hoje viram inteiros exatos. A conversao confere isso ao montar as taxas e falha alto se um numero sair da grade.

Etapa 3, o orgao 1 (secao 5, sub-chave `digestao`): a comida (a racao, o comer, a nutricao da fruta) entra como o quimico `alimento`, e
a reacao da digestao tira `alimento` e a mesma quantidade de `fome`, ate `taxa_digestao` por tick. Na taxa C (CD-3) tudo passa no mesmo
tick, e a fome lida e a de hoje. O que sobra no estomago quando a fome chega a 0 e descartado: e o corte de hoje (a fome nao passa de 1).
O corpo expoe quanto digeriu em cada tick (a vontade do banheiro, docs/TAREFA_V2_BANHEIRO.md, secao 3, sobe com ele).

Etapa 4, o orgao 2 (secao 6, sub-chave `vida`): o quimico `vida` comeca em C ao nascer e decai `vida_decaimento` por tick. Receptores sobre
a Vida mudam o estagio nos limiares C - v x tick_do_estagio, com os ticks de estagio de hoje (as duracoes da ConfigEvolucaoPesquisa, as
mesmas de treino_stats.estagio_no_tick): o estagio pela Vida e o de hoje, tick a tick. A Vida nao mata nesta etapa (em 0, fica em 0) e
nao tem receptor para o cerebro.

Os estimulos do mundo fisico (digilab/mundo.py; para o A ligar o MotorMundo no MotorCorpo): o andar (`estimulo_andar`, o custo de hoje,
1/6000 de energia por subunidade, e 75 em C), as comidas do mapa (`estimulo_consumo_mundo`: a racao deixada, a fruta madura e a podre,
com os numeros da ConfigMundo) e a MF-2 (`acao_pet(..., com_mundo=True)`: no mundo, comer nao da fome por si; a comida vem do mapa). A
sujeira depois da racao continua sorteada pelo mundo (o fluxo `mundo-sujeira`), no Estado.

Etapa 6 (secoes 7, 8 e 17), os drives novos e os gestos:
  - `drives_novos`: o tedio (+450 por tick acordado; a reducao pela variedade recente, DS-4: `atividade(nome)` com "bola", "brincar",
    "explorar", e o "dono_brinca" dentro do `acao_dono(BRINCAR)`), a curiosidade (so com o mundo fisico, `com_mundo`, CD-8: +300 por
    tick acordado, `estimulo_novidade(n)` tira 90000 por novidade, ate 2), a solidao (+225 por tick acordado; o carinho tira 180000) e o
    estresse (por tick, div_arred(soma de max(0, q_d - 337500), 256) sobre os drives; meia-vida 1440; o carinho tira 90000);
  - `gestos`: o tapa (`acao_dono` com o valor "tapa": dor +90000, susto +180000, estresse +45000), a dor (meia-vida 60) e o susto
    (meia-vida 30), e o medo da mao (CD-5): o carinho na solidao e no estresse vezes (C - medo_da_mao x q_susto) / C.
Os receptores novos leem a falta (a concentracao na dor e no susto), div_arred(q S, C). Nenhum drive do Estado muda por eles.

O banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 3 e BN-6; sub-chave `banheiro`, que exige os gestos):
  - a `vontade` (de fazer as necessidades): +150 por tick acordado; a digestao poe nela 1/3 do alimento digerido (o resto da divisao
    fica guardado, entao nada se perde no arredondamento); `estimulo_aliviar` a zera; acima de 0,75 o desconforto sobe +150 por tick
    (fase 2, o gatilho `acima`). O receptor le a concentracao, como a dor;
  - a necessidade no chao (o objeto e do motor, etapa 3): `estimulo_necessidade` da o "cheiro" imediato (+22500 de desconforto) e o
    `passo(..., necessidades=n)` soma +100 de desconforto por tick por necessidade na regiao do pet, ate 3 (o motor conta);
  - o `conforto` (BN-6): o carinho o sobe (+45000, com o medo da mao, como a solidao e o estresse) e ele cai com meia-vida 60. O receptor
    le a concentracao; o cerebro le a falta de conforto (S - leitura), entao o carinho da sinal mesmo com a solidao baixa.

O metabolismo energetico (docs/TAREFA_V2_METABOLISMO.md, secao 3; ME-1 a ME-7 pela recomendacao; sub-chave `metabolismo`, que exige a
digestao): dois quimicos sem receptor (ME-2), guardados como concentracao, o `combustivel` (C/2 ao nascer) e a `reserva` (C/4):
  - a conversao: a digestao poe no combustivel conversao_num/conversao_den do que digeriu, com o resto guardado (como a vontade); o que
    passa do teto e descartado (e contado);
  - o gasto basal: 375 por tick acordado e 187 dormindo (fase 1); as atividades (o brincar do pet e o do dono, o explorar e o andar) tiram
    do combustivel o mesmo numero que somam ao cansaco, que nao muda;
  - o armazenamento (acima de 3C/4, ate 375 por tick, combustivel -> reserva) e a mobilizacao (abaixo de C/2, ate 375, reserva ->
    combustivel): transferencias 1 por 1 com limiar, depois da fase 1 e antes da fase 2;
  - a falta: abaixo de C/4 o cansaco sobe 500 por tick (fase 2, o gatilho `abaixo`). E a unica ponte entre o combustivel e o pet (ME-1):
    com o combustivel acima de C/4, todo quimico de antes e o de sem o metabolismo, tick a tick.
A fome nao le o combustivel (ME-5) e o excedente do estomago com a fome em 0 segue descartado (ME-4). `contas_metabolismo` guarda, em
totais, o que entrou e saiu do combustivel e da reserva (a contabilidade fecha a cada tick).

O grafo (secao 18): `grafo_do_corpo` monta a tabela unica dos quimicos, reacoes, emissores, receptores, meias-vidas e tetos
(digilab/corpo_grafo.py), e o `Corpo` a usa (a lista dos quimicos, os receptores, as meias-vidas, os emissores do tick por fase e as
quantidades dos estimulos novos) e a confere na carga (`corpo_grafo.checar`, que falha alto).

Componente puro: nao e motor, nao sorteia (nenhuma rng), nao le o cerebro. A sujeira e o sono continuam estados do `Estado` (o motor
sorteia a sujeira como hoje); o corpo so os le. Quem liga o corpo ao motor e o A (etapa 2, `MotorCorpo`).

Por que a vida com o corpo nao sai byte a byte igual a de hoje (secao 3): os limiares de hoje caem sobre a grade inteira. A fome que
parte de 0,80 chega a 0,25 exato no tick 660 em inteiros, e o float de hoje passa um pouco abaixo. Por isso o G-HOJE e, aqui, em malha
aberta (as mesmas acoes forcadas, tick a tick), e a malha fechada fica com o plano.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import CONFIG_EVOLUCAO_PESQUISA, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigCorpo, ConfigEvolucaoPesquisa, ConfigMundo
from .corpo_grafo import Emissor, Grafo, Leitura, Quimico, Reacao, checar
from .events import ACOES_PET_BANHEIRO, ACOES_PET_HOJE, FRUTAS, TIPOS_COMIDA_MUNDO, AcaoPet, AcaoUsuario
from .state import Estado

QUIMICOS = ("fome", "desconforto", "cansaco", "tristeza", "dano")
DRIVE_DO_QUIMICO = {"fome": "fome", "desconforto": "higiene", "cansaco": "energia", "tristeza": "humor", "dano": "saude"}
QUIMICOS_DA_PRIVACAO = ("fome", "desconforto", "cansaco")       # Estado.em_privacao: fome, higiene e energia (humor nao conta)
ORGAO_DIGESTAO = ("alimento",)                                    # sem receptor para o cerebro (secao 5)
ORGAO_VIDA = ("vida",)                                            # sem receptor para o cerebro (secao 6)
ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")           # os de treino_stats.estagio_no_tick, na ordem
NOVOS = ("tedio", "curiosidade", "solidao", "estresse")           # etapa 6, drives_novos (a curiosidade so com o mundo fisico)
GESTOS = ("dor", "susto")                                         # etapa 6, gestos
BANHEIRO = ("vontade", "conforto")                                # o banheiro (TAREFA_V2_BANHEIRO, secao 3 e BN-6)
METABOLISMO = ("combustivel", "reserva")                          # o metabolismo (TAREFA_V2_METABOLISMO, secao 3); sem receptor (ME-2)
CONTAS_METABOLISMO = ("convertido", "descartado_teto", "mobilizado", "gasto_basal", "gasto_atividade", "armazenado")
DRIVES_DO_ESTRESSE = ("fome", "desconforto", "cansaco", "tedio", "curiosidade", "solidao", "dor")   # secao 7, os que o estresse le
ATIVIDADES = ("bola", "brincar", "explorar", "dono_brinca")       # DS-4: as atividades que reduzem o tedio e entram na janela
VALOR_TAPA = "tapa"                                               # AcaoUsuario.TAPA (o enum e do A, etapa 6): o corpo o le pelo valor


def quimicos_de(cc: ConfigCorpo, com_mundo: bool = False) -> tuple[str, ...]:
    """Os quimicos que o corpo tem com estas chaves: os cinco de hoje, os de cada orgao ligado e os da etapa 6 (a curiosidade so com o
    mundo fisico)."""
    novos = tuple(n for n in NOVOS if n != "curiosidade" or com_mundo) if cc.drives_novos else ()
    return (QUIMICOS + (ORGAO_DIGESTAO if cc.digestao else ()) + (ORGAO_VIDA if cc.vida else ()) + novos
            + (GESTOS if cc.gestos else ()) + (BANHEIRO if cc.banheiro else ()) + (METABOLISMO if cc.metabolismo else ()))


TOLERANCIA_GRADE = 1e-6                                           # quanto um numero de hoje x C pode fugir de um inteiro (so erro de float)

# Status dos campos da ConfigCorpo (conferido por teste). Todos PROPOSTOS, nenhum referendado.
PARAMETROS_CORPO: dict[str, tuple[str, str]] = {
    "ligada": ("PROPOSTO", "TAREFA_V2_CORPO_DRIVES, secao 2: a quimica dos drives de hoje (etapa 1)"),
    "digestao": ("PROPOSTO", "secao 5, etapa 3 (orgao 1, W-CORPO-DIGESTAO)"),
    "vida": ("PROPOSTO", "secao 6, etapa 4 (orgao 2, W-CORPO-DIGESTAO)"),
    "drives_novos": ("PROPOSTO", "secao 7, etapa 6 (CORPO-DRIVES)"),
    "gestos": ("PROPOSTO", "secao 8, etapa 6 (CORPO-DRIVES)"),
    "escala": ("DECIDIDO", "CD-1: C = 450000, o mmc dos denominadores das taxas de hoje (#210)"),
    "escala_receptor": ("PROPOSTO", "= S do cerebro A (2**ConfigLobos.bits_ponto_fixo), secao 3"),
    "bits_meia_vida": ("PROPOSTO", "secao 3: k_h na escala 2**16"),
    "pet_brincar_cansaco": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (energia -0,02) x C"),
    "pet_explorar_cansaco": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (energia -0,015) x C"),
    "pet_explorar_tristeza": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (humor +0,01) x C"),
    "pet_comer_fome": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (fome +0,05) x C"),
    "pet_emburrar_tristeza": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (humor -0,01) x C"),
    "k_meia_vida_susto": ("PROPOSTO", "secao 8: meia-vida 30, sem fonte; k pela regra da secao 3"),
    "k_meia_vida_dor": ("PROPOSTO", "secao 8: meia-vida 60, sem fonte; k pela regra da secao 3"),
    "k_meia_vida_estresse": ("PROPOSTO", "secao 7: meia-vida 1440, sem fonte; k pela regra da secao 3"),
    "taxa_digestao": ("DECIDIDO", "CD-3: C, tudo no mesmo tick (a fome de hoje); a digestao lenta so com o plano (#210)"),
    "vida_decaimento": ("PROPOSTO", "secao 6: C // (28 dias x 1440), a vida mais longa da pesquisa (o bloco de duracoes do adendo 3)"),
    "tedio_sobe": ("PROPOSTO", "secao 7: +450 por tick acordado, sem fonte; o plano calibra (m_sobe)"),
    "curiosidade_sobe": ("PROPOSTO", "secao 7: +300 por tick acordado, sem fonte"),
    "solidao_sobe": ("PROPOSTO", "secao 7: +225 por tick acordado, sem fonte; o plano calibra (m_sobe)"),
    "estresse_limiar": ("PROPOSTO", "secao 7: 0,75 de falta, sem fonte; fixo no plano (6.1)"),
    "estresse_divisor": ("PROPOSTO", "secao 7: 256, sem fonte; o plano calibra (m_sobe)"),
    "janela_tedio": ("PROPOSTO", "secao 17 (DS-4): 8, sem fonte; fixa pelo adendo 1 do plano (A1.2)"),
    "tedio_bola": ("PROPOSTO", "secao 17: -135000, sem fonte; o plano calibra (m_reduz)"),
    "tedio_brincar": ("PROPOSTO", "secao 17: -45000, sem fonte; o plano calibra (m_reduz)"),
    "tedio_explorar": ("PROPOSTO", "secao 17: -90000, sem fonte; o plano calibra (m_reduz)"),
    "tedio_dono": ("PROPOSTO", "secao 17: -90000, sem fonte; o plano calibra (m_reduz)"),
    "curiosidade_novidade": ("PROPOSTO", "secao 7: -90000 por novidade, sem fonte"),
    "curiosidade_max_novidades": ("PROPOSTO", "secao 7: ate 2 por decisao, sem fonte"),
    "janela_novidade": ("PROPOSTO", "secao 7: 1440 ticks, sem fonte (o registro do que o pet viu e do motor)"),
    "carinho_solidao": ("PROPOSTO", "secao 8: -180000, sem fonte; o plano calibra (m_reduz)"),
    "carinho_estresse": ("PROPOSTO", "secao 8: -90000, sem fonte; o plano calibra (m_reduz)"),
    "tapa_dor": ("PROPOSTO", "secao 8: +90000, sem fonte; fixo no plano (6.1)"),
    "tapa_susto": ("PROPOSTO", "secao 8: +180000, sem fonte; fixo no plano (6.1)"),
    "tapa_estresse": ("PROPOSTO", "secao 8: +45000, sem fonte; fixo no plano (6.1)"),
    "medo_da_mao": ("DECIDIDO", "CD-5: o susto corta o carinho; 0 e a variante sem medo"),
    "banheiro": ("DECIDIDO", "BN-1 a BN-6 (TAREFA_V2_BANHEIRO, secao 10): a vontade e o conforto no corpo (etapa 2, do B)"),
    "vontade_sobe": ("PROPOSTO", "TAREFA_V2_BANHEIRO, secao 3: +150 por tick acordado, sem fonte; o plano calibra (m_v)"),
    "vontade_digestao_num": ("PROPOSTO", "secao 3: 1/3 do alimento digerido, sem fonte; o plano calibra (m_v)"),
    "vontade_digestao_den": ("PROPOSTO", "secao 3: 1/3 do alimento digerido, sem fonte; o plano calibra (m_v)"),
    "vontade_limiar": ("PROPOSTO", "secao 3: 0,75, sem fonte"),
    "vontade_desconforto": ("PROPOSTO", "secao 3: +150 por tick acima do limiar, sem fonte; o plano calibra (m_d)"),
    "necessidade_desconforto": ("PROPOSTO", "secao 3: +22500, o cheiro imediato, sem fonte"),
    "necessidade_regiao": ("PROPOSTO", "secao 3: +100 por tick por necessidade na regiao, sem fonte"),
    "necessidade_max_regiao": ("PROPOSTO", "secao 3: ate 3 necessidades, sem fonte"),
    "conforto_carinho": ("PROPOSTO", "BN-6: o menor da grade 6.1 do plano (45000) que passa o G-CAR; a calibracao do plano escolhe"),
    "k_meia_vida_conforto": ("PROPOSTO", "BN-6: meia-vida 60 (a menor da grade 6.1 do plano); k pela regra da secao 3"),
    "metabolismo": ("DECIDIDO", "ME-1 a ME-7 pela recomendacao (TAREFA_V2_METABOLISMO, secao 9; Matheus, 2026-10-11)"),
    "combustivel_inicial": ("PROPOSTO", "TAREFA_V2_METABOLISMO, secao 3: C/2, sem fonte"),
    "reserva_inicial": ("PROPOSTO", "secao 3: C/4, sem fonte"),
    "conversao_num": ("PROPOSTO", "secao 3: 1/1, sem fonte; com o gasto basal igual a subida da fome, comer o que a fome pede o mantem"),
    "conversao_den": ("PROPOSTO", "secao 3: 1/1, sem fonte"),
    "gasto_basal_acordado": ("PROPOSTO", "secao 3: 375 = a subida da fome, sem fonte; o passo 0 da calibracao escala (ME-7)"),
    "gasto_basal_dormindo": ("PROPOSTO", "secao 3: 187, a metade, sem fonte; o passo 0 da calibracao escala (ME-7)"),
    "armazenar_limiar": ("PROPOSTO", "secao 3: 3C/4, sem fonte"),
    "armazenar_taxa": ("PROPOSTO", "secao 3: 375 por tick, sem fonte"),
    "mobilizar_limiar": ("PROPOSTO", "secao 3: C/2, sem fonte"),
    "mobilizar_taxa": ("PROPOSTO", "secao 3: 375 por tick, sem fonte"),
    "falta_limiar": ("PROPOSTO", "secao 3: C/4, sem fonte"),
    "falta_cansaco": ("PROPOSTO", "secao 3: +500 por tick, o cansaco de um tick acordado de dia, sem fonte (ME-1)"),
    "gasto_atividades_num": ("PROPOSTO", "ME-3 e ME-7: 1/1, o mesmo numero do cansaco; o passo 0 da calibracao escala (no gasto_atividades)"),
    "gasto_atividades_den": ("PROPOSTO", "ME-3 e ME-7: 1/1, o mesmo numero do cansaco; o passo 0 da calibracao escala (no gasto_atividades)"),
}


# ------------------------------------------------------------------ inteiros

def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0. A mesma conta de lobos.div_arred (conferido por teste);
    copiada para o corpo nao depender de um cerebro."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def na_grade(x: float, escala: int, nome: str) -> int:
    """x * escala como inteiro exato. Um numero de hoje fora da grade falha alto (a CD-1 diz que nenhum fica fora)."""
    v = x * escala
    r = int(round(v))
    if abs(v - r) > TOLERANCIA_GRADE:
        raise ValueError(f"{nome} = {x!r} nao cai na grade de {escala}: {v!r}")
    return r


def k_meia_vida(h: int, bits: int = 16) -> int:
    """A constante da meia-vida h (secao 3): arred(2**bits * (1 - 2**(-1/h))). So para derivar e conferir as constantes da ConfigCorpo;
    o tick nunca a chama (nenhuma funcao transcendental no tick)."""
    if h <= 0:
        raise ValueError(f"meia-vida nao positiva: {h}")
    return int((2 ** bits) * (1.0 - 2.0 ** (-1.0 / h)) + 0.5)


def passo_meia_vida(q: int, k: int, bits: int = 16) -> int:
    """Um tick de decaimento (secao 3): q - max(1, div_arred(q * k, 2**bits)) enquanto q > 0. O minimo de 1 impede que uma concentracao
    pequena fique presa."""
    if q <= 0:
        return 0
    return max(0, q - max(1, div_arred(q * k, 2 ** bits)))


# ------------------------------------------------------------------ taxas

@dataclass(frozen=True)
class TaxasCorpo:
    """Os numeros de hoje na escala C, com o sinal da falta (positivo = o drive piora). Montados de Config e ConfigCorpo por taxas_de."""

    fome_por_tick: int
    desconforto_por_tick: int
    desconforto_por_sujeira: int
    tristeza_por_tick: int
    cansaco_acordado: int
    cansaco_noite: int
    cansaco_dormindo: int                    # negativo: dormir descansa
    dano_privacao: int
    dano_cura: int                           # negativo
    limiar_privacao: int                     # privacao: algum quimico da privacao acima disto (o 0,15 de hoje)
    dono: dict                               # AcaoUsuario -> {quimico: delta}
    pet: dict                                # AcaoPet -> {quimico: delta}


def gasto_da_atividade(cc: ConfigCorpo, cansaco: int) -> int:
    """O que uma atividade tira do combustivel: div_arred(o que ela soma ao cansaco x gasto_atividades_num, gasto_atividades_den). Com o
    fator 1/1, o mesmo numero (ME-3). Um gasto que arredonda a zero falha alto: a atividade deixaria de custar combustivel."""
    if cansaco <= 0:
        raise ValueError(f"atividade sem cansaco: {cansaco}")
    g = div_arred(cansaco * cc.gasto_atividades_num, cc.gasto_atividades_den)
    if g <= 0:
        raise ValueError(f"o fator do gasto das atividades zera o gasto de {cansaco}: "
                         f"{cc.gasto_atividades_num}/{cc.gasto_atividades_den}")
    return g


def taxas_de(cfg: Config, cc: ConfigCorpo) -> TaxasCorpo:
    C = cc.escala
    g = lambda x, nome: na_grade(x, C, nome)  # noqa: E731
    dono = {
        AcaoUsuario.ALIMENTAR: {"fome": -g(cfg.ganho_alimentar, "ganho_alimentar")},
        AcaoUsuario.LIMPAR: {"desconforto": -g(cfg.ganho_limpar, "ganho_limpar")},
        AcaoUsuario.BRINCAR: {"tristeza": -g(cfg.ganho_brincar_humor, "ganho_brincar_humor"),
                              "cansaco": g(cfg.custo_brincar_energia, "custo_brincar_energia"),
                              "fome": g(cfg.custo_brincar_fome, "custo_brincar_fome")},
        AcaoUsuario.ACARICIAR: {"tristeza": -g(cfg.ganho_elogiar * 0.6, "ganho_elogiar * 0.6")},
        AcaoUsuario.ELOGIAR: {"tristeza": -g(cfg.ganho_elogiar, "ganho_elogiar")},
        AcaoUsuario.REPREENDER: {"tristeza": g(cfg.custo_repreender, "custo_repreender")},
    }
    pet = {
        AcaoPet.OCIOSO: {}, AcaoPet.DORMIR: {}, AcaoPet.CHAMAR_ATENCAO: {},
        AcaoPet.BRINCAR: {"tristeza": -g(cfg.humor_por_tick_brincando * cfg.intervalo_decisao_ticks, "humor do brincar"),
                          "cansaco": cc.pet_brincar_cansaco},
        AcaoPet.EXPLORAR: {"cansaco": cc.pet_explorar_cansaco, "tristeza": cc.pet_explorar_tristeza},
        AcaoPet.COMER: {"fome": cc.pet_comer_fome},
        AcaoPet.EMBURRAR: {"tristeza": cc.pet_emburrar_tristeza},
    }
    if cc.banheiro:
        pet[AcaoPet.ALIVIAR] = {}               # o aliviar e o estimulo `estimulo_aliviar` (a vontade a zero), do motor com o banheiro
    if cc.metabolismo:
        # ME-3: as atividades tiram do combustivel o que somam ao cansaco vezes o fator do gasto (1/1: o mesmo numero); o cansaco de hoje
        # nao muda
        for efeitos in (pet[AcaoPet.BRINCAR], pet[AcaoPet.EXPLORAR], dono[AcaoUsuario.BRINCAR]):
            efeitos["combustivel"] = -gasto_da_atividade(cc, efeitos["cansaco"])
    esperadas = set(ACOES_PET_HOJE) | (set(ACOES_PET_BANHEIRO) if cc.banheiro else set())
    if set(pet) != esperadas:
        raise ValueError(f"acoes do pet sem efeito no corpo: {sorted(a.value for a in esperadas - set(pet))}")
    return TaxasCorpo(
        fome_por_tick=g(cfg.decaimento_fome, "decaimento_fome"),
        desconforto_por_tick=g(cfg.decaimento_higiene, "decaimento_higiene"),
        desconforto_por_sujeira=g(cfg.decaimento_higiene * cfg.penalidade_higiene_por_sujeira, "penalidade_higiene_por_sujeira"),
        tristeza_por_tick=g(cfg.decaimento_humor, "decaimento_humor"),
        cansaco_acordado=g(cfg.decaimento_energia, "decaimento_energia"),
        cansaco_noite=g(cfg.decaimento_energia * cfg.multiplicador_noturno, "decaimento_energia * multiplicador_noturno"),
        cansaco_dormindo=-g(cfg.energia_por_tick_dormindo, "energia_por_tick_dormindo"),
        dano_privacao=g(cfg.dano_saude_por_tick, "dano_saude_por_tick"),
        dano_cura=-g(cfg.cura_saude_por_tick, "cura_saude_por_tick"),
        limiar_privacao=C - g(cfg.limiar_privacao, "limiar_privacao"),
        dono=dono,
        pet=pet,
    )


# ------------------------------------------------------------------ o grafo (secao 18)

MEIAS_VIDAS = {"estresse": ("k_meia_vida_estresse", 1440), "dor": ("k_meia_vida_dor", 60), "susto": ("k_meia_vida_susto", 30),
               "conforto": ("k_meia_vida_conforto", 60)}
RECEPTOR_DE = {**DRIVE_DO_QUIMICO, **{n: n for n in NOVOS + GESTOS + BANHEIRO}}     # o nome do receptor (o campo da PercepcaoCorpo)


def grafo_do_corpo(cfg: Config, cc: ConfigCorpo, t: TaxasCorpo, com_mundo: bool = False) -> Grafo:
    """A tabela unica do corpo com estas chaves (secao 18). Os numeros de hoje vem das taxas (`t`) e os da etapa 6 da ConfigCorpo; os
    estimulos que vem de fora com quantidade variavel (a bola, a fruta, o andar, a comida podre) guardam so o sinal. Com a digestao, a
    comida (a racao, o comer, a fruta) entra no estomago (`alimento`) e a reacao da digestao a tira, junto com a fome."""
    C = cc.escala
    nomes = quimicos_de(cc, com_mundo)
    quimicos = []
    for n in nomes:
        receptor = RECEPTOR_DE.get(n)
        leitura = None if receptor is None else ("drive" if n in QUIMICOS else "falta")
        h = MEIAS_VIDAS.get(n)
        quimicos.append(Quimico(n, C, True, receptor, leitura, None if h is None else h[1],
                                None if h is None else getattr(cc, h[0])))
    # a digestao tira o alimento e a fome; com o banheiro, poe na vontade uma fracao do que digeriu; com o metabolismo, no combustivel
    fracoes = ((("vontade", cc.vontade_digestao_num, cc.vontade_digestao_den),) if cc.banheiro else ()) + (
        (("combustivel", cc.conversao_num, cc.conversao_den),) if cc.metabolismo else ())
    reacoes = ((Reacao("digestao", ("alimento", "fome"), tuple(q for q, _, _ in fracoes), cc.taxa_digestao, fracoes),)
               if cc.digestao else ())
    if cc.metabolismo:
        # as transferencias com limiar: o excedente vai a reserva, e a reserva volta quando o combustivel cai
        reacoes += (Reacao("armazenamento", ("combustivel",), ("reserva",), cc.armazenar_taxa, le="combustivel", lado="acima",
                           limiar=cc.armazenar_limiar),
                    Reacao("mobilizacao", ("reserva",), ("combustivel",), cc.mobilizar_taxa, le="combustivel", lado="abaixo",
                           limiar=cc.mobilizar_limiar))

    def comida(efeitos: dict) -> tuple:
        if cc.digestao and efeitos.get("fome", 0) < 0:
            efeitos = {**{k: v for k, v in efeitos.items() if k != "fome"}, "alimento": -efeitos["fome"]}
        return tuple(efeitos.items())

    em: list[Emissor] = [
        Emissor("fome_tick", "tick", 1, (("fome", t.fome_por_tick),)),
        Emissor("desconforto_tick", "tick", 1, (("desconforto", t.desconforto_por_tick),)),
        Emissor("desconforto_sujeira", "sujeira", 1, (("desconforto", t.desconforto_por_sujeira),)),
        Emissor("tristeza_tick", "tick", 1, (("tristeza", t.tristeza_por_tick),)),
        Emissor("cansaco_dormindo", "dormindo", 1, (("cansaco", t.cansaco_dormindo),)),
        Emissor("cansaco_noite", "noite_acordado", 1, (("cansaco", t.cansaco_noite),)),
        Emissor("cansaco_dia", "dia_acordado", 1, (("cansaco", t.cansaco_acordado),)),
    ]
    if cc.vida:
        em.append(Emissor("vida_tick", "tick", 1, (("vida", -cc.vida_decaimento),)))
    sobe = {"tedio": cc.tedio_sobe, "curiosidade": cc.curiosidade_sobe, "solidao": cc.solidao_sobe}
    em += [Emissor(f"{n}_sobe", "acordado", 1, ((n, sobe[n]),)) for n in NOVOS if n in sobe and n in nomes]
    if cc.banheiro:
        em += [Emissor("vontade_sobe", "acordado", 1, (("vontade", cc.vontade_sobe),)),
               Emissor("necessidade_regiao", "necessidades", 1, (("desconforto", cc.necessidade_regiao),))]
    if cc.metabolismo:
        em += [Emissor("gasto_basal_acordado", "acordado", 1, (("combustivel", -cc.gasto_basal_acordado),)),
               Emissor("gasto_basal_dormindo", "dormindo", 1, (("combustivel", -cc.gasto_basal_dormindo),))]
    degrau = tuple(Leitura(n, 1, 1) for n in QUIMICOS_DA_PRIVACAO)     # um degrau: conta como ganho 1 se entrar num laco
    em += [Emissor("dano_privacao", "privacao", 2, (("dano", t.dano_privacao),), degrau),
           Emissor("dano_cura", "sem_privacao", 2, (("dano", t.dano_cura),))]
    if "estresse" in nomes:
        le = tuple(Leitura(n, 1, cc.estresse_divisor) for n in DRIVES_DO_ESTRESSE if n in nomes)
        em.append(Emissor("estresse_drives", "limiar", 2, (("estresse", 1),), le, cc.estresse_limiar, cc.estresse_divisor, True))
    if cc.banheiro:
        # a vontade acima de 0,75 sobe o desconforto (o que faz o pet querer aliviar); um degrau, como o dano pela privacao
        em.append(Emissor("vontade_desconforto", "acima", 2, (("desconforto", cc.vontade_desconforto),), (Leitura("vontade", 1, 1),),
                          cc.vontade_limiar))
    if cc.metabolismo:
        # a falta de combustivel sobe o cansaco (ME-1, a unica ponte); um degrau, como o dano pela privacao
        em.append(Emissor("falta_combustivel", "abaixo", 2, (("cansaco", cc.falta_cansaco),), (Leitura("combustivel", 1, 1, -1),),
                          cc.falta_limiar))
    # os estimulos (fase 0): os de hoje pelas taxas, os do mundo e os da etapa 6
    for acao, efeitos in t.dono.items():
        em.append(Emissor(f"dono:{acao.value}", "estimulo", 0, comida(efeitos) if acao is AcaoUsuario.ALIMENTAR else tuple(efeitos.items())))
    for acao, efeitos in t.pet.items():
        if efeitos:
            em.append(Emissor(f"pet:{acao.value}", "estimulo", 0, comida(efeitos) if acao is AcaoPet.COMER else tuple(efeitos.items())))
    em += [Emissor("bola", "estimulo", 0, (("tristeza", -1),), variavel=True),
           Emissor("fruta", "estimulo", 0, comida({"fome": -1, "tristeza": -1}), variavel=True),
           Emissor("fruta_ruim", "estimulo", 0, (("tristeza", 1),), variavel=True),
           Emissor("andar", "estimulo", 0, (("cansaco", 1),) + ((("combustivel", -1),) if cc.metabolismo else ()), variavel=True),
           Emissor("comida_podre", "estimulo", 0, (("tristeza", 1),), variavel=True)]
    if cc.drives_novos:
        bases = {"bola": cc.tedio_bola, "brincar": cc.tedio_brincar, "explorar": cc.tedio_explorar, "dono_brinca": cc.tedio_dono}
        em += [Emissor(f"atividade:{a}", "estimulo", 0, (("tedio", -bases[a]),)) for a in ATIVIDADES]
        if "curiosidade" in nomes:
            em.append(Emissor("novidade", "estimulo", 0, (("curiosidade", -cc.curiosidade_novidade),)))
        medo = (Leitura("susto", cc.carinho_solidao * cc.medo_da_mao, C, -1),) if cc.gestos else ()
        em.append(Emissor("carinho_solidao", "estimulo", 0, (("solidao", -cc.carinho_solidao),), medo))
        medo = (Leitura("susto", cc.carinho_estresse * cc.medo_da_mao, C, -1),) if cc.gestos else ()
        em.append(Emissor("carinho_estresse", "estimulo", 0, (("estresse", -cc.carinho_estresse),), medo))
    if cc.gestos:
        em.append(Emissor("tapa", "estimulo", 0, (("dor", cc.tapa_dor), ("susto", cc.tapa_susto), ("estresse", cc.tapa_estresse))))
    if cc.banheiro:
        medo = (Leitura("susto", cc.conforto_carinho * cc.medo_da_mao, C, -1),)
        em += [Emissor("carinho_conforto", "estimulo", 0, (("conforto", cc.conforto_carinho),), medo),
               Emissor("aliviar", "estimulo", 0, (("vontade", -1),), variavel=True),           # a vontade a zero
               Emissor("necessidade", "estimulo", 0, (("desconforto", cc.necessidade_desconforto),))]
    return Grafo(tuple(quimicos), reacoes, tuple(em))


# ------------------------------------------------------------------ orgao 2: os limiares da Vida

def ticks_de_estagio(cfg_evo: ConfigEvolucaoPesquisa) -> tuple[int, int, int]:
    """Os ticks em que o estagio de hoje muda (treino_stats.estagio_no_tick): fim do bebe, da crianca e do adolescente."""
    t1 = cfg_evo.dur_bebe_min
    t2 = t1 + cfg_evo.dur_crianca_min
    return t1, t2, t2 + cfg_evo.dur_adolescente_min


def limiares_estagio(cc: ConfigCorpo, cfg_evo: ConfigEvolucaoPesquisa) -> tuple[int, ...]:
    """Os limiares dos receptores de estagio: C - v x T para cada tick de estagio T. Um limiar que nao fica acima de 0 falha alto: a Vida
    acabaria antes do estagio e o receptor nunca o veria."""
    lim = tuple(cc.escala - cc.vida_decaimento * t for t in ticks_de_estagio(cfg_evo))
    if any(x <= 0 for x in lim):
        raise ValueError(f"a Vida acaba antes de um estagio: limiares {lim} (v = {cc.vida_decaimento}, ticks {ticks_de_estagio(cfg_evo)})")
    return lim


# ------------------------------------------------------------------ o corpo

class Corpo:
    """A quimica dos drives de hoje e os orgaos ligados. `q` guarda cada quimico em [0, C] (a falta, nos de hoje). Nao sorteia; a sujeira
    e o sono vem do Estado."""

    def __init__(self, q: dict[str, int], cfg: Config | None = None, cc: ConfigCorpo | None = None,
                 cfg_evo: ConfigEvolucaoPesquisa | None = None, com_mundo: bool = False) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cfg_evo = cfg_evo or CONFIG_EVOLUCAO_PESQUISA
        self.cc = cc or ConfigCorpo(ligada=True)
        if not self.cc.ligada:
            raise ValueError("Corpo com ConfigCorpo desligada: com a chave desligada o corpo nao existe")
        self.com_mundo = com_mundo
        self.C = self.cc.escala
        self.S = self.cc.escala_receptor
        self.t = taxas_de(self.cfg, self.cc)
        # secao 18: a tabela unica, conferida na carga (falha alto); a lista e a ordem dos quimicos saem dela
        self.grafo = grafo_do_corpo(self.cfg, self.cc, self.t, com_mundo)
        self.relato_grafo = checar(self.grafo)
        self.quimicos = self.grafo.nomes
        if self.quimicos != quimicos_de(self.cc, com_mundo):            # pragma: no cover - o grafo e montado de quimicos_de
            raise RuntimeError("o grafo e a lista de quimicos divergem")
        if set(q) != set(self.quimicos):
            raise ValueError(f"quimicos do corpo: esperava {self.quimicos}, veio {sorted(q)}")
        for nome, v in q.items():
            teto = self.grafo.quimico(nome).teto
            if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= teto:
                raise ValueError(f"concentracao de {nome} fora de [0, {teto}] ou nao inteira: {v!r}")
        self.q = {nome: q[nome] for nome in self.quimicos}
        self.janela_tedio: list[str] = []                 # DS-4: as ultimas atividades (so com drives_novos)
        # orgao 1: o que passou do estomago para a fome (no tick corrente, no ultimo tick fechado e no total) e o que se descartou
        self.digerido_tick = 0
        self.digerido_no_tick = 0
        self.digerido_total = 0
        self.descartado_total = 0
        # banheiro: o resto da divisao da fracao do digerido que vai para a vontade (em [0, vontade_digestao_den))
        self.resto_vontade = 0
        # metabolismo: o resto da conversao (em [0, conversao_den)), as transferencias com limiar e a contabilidade do combustivel e da
        # reserva, em totais (CONTAS_METABOLISMO)
        self.resto_combustivel = 0
        self._fracoes = next((r.fracoes for r in self.grafo.reacoes if r.nome == "digestao"), ())
        self._transferencias = tuple(r for r in self.grafo.reacoes if r.le is not None)
        self.contas_metabolismo = {k: 0 for k in CONTAS_METABOLISMO} if self.cc.metabolismo else None
        # orgao 2: os limiares dos receptores de estagio sobre a Vida
        self.limiares_estagio = limiares_estagio(self.cc, self.cfg_evo) if self.cc.vida else ()

    @classmethod
    def de_estado(cls, estado: Estado, cfg: Config | None = None, cc: ConfigCorpo | None = None,
                  cfg_evo: ConfigEvolucaoPesquisa | None = None, com_mundo: bool = False) -> Corpo:
        """O corpo de um Estado de hoje (o do nascimento, por exemplo). Cada drive tem de cair na grade de C. A Vida e a do tick do
        Estado (C no nascimento). Os quimicos da etapa 6 comecam em 0 (`com_mundo`: a curiosidade existe)."""
        cc = cc or ConfigCorpo(ligada=True)
        C = cc.escala
        q = {nome: na_grade(1.0 - getattr(estado, drive), C, f"Estado.{drive}") for nome, drive in DRIVE_DO_QUIMICO.items()}
        if cc.digestao:
            q["alimento"] = 0                    # o Estado de hoje nao tem estomago: comeca vazio
        if cc.vida:
            q["vida"] = max(0, C - cc.vida_decaimento * estado.tick)
        if cc.metabolismo:
            q["combustivel"] = cc.combustivel_inicial
            q["reserva"] = cc.reserva_inicial
        for nome in quimicos_de(cc, com_mundo):
            q.setdefault(nome, 0)                          # os drives novos e os gestos: zero no nascimento
        return cls(q, cfg, cc, cfg_evo, com_mundo)

    # ---------------------------------------------------------- estimulos

    def _somar(self, deltas: dict[str, int], rubrica: str = "gasto_atividade") -> None:
        """Soma os deltas, cortados em [0, C]. Com o metabolismo, o que sai do combustivel por aqui e gasto (`rubrica`: o basal no tick,
        as atividades nos estimulos) e entra na contabilidade pelo que de fato saiu; combustivel subindo por aqui falha alto (a conversao
        e a mobilizacao tem caminho proprio)."""
        antes = self.q["combustivel"] if "combustivel" in deltas else None
        for nome, d in deltas.items():
            self.q[nome] = min(self.C, max(0, self.q[nome] + d))
        if antes is not None:
            if deltas["combustivel"] > 0:
                raise RuntimeError(f"combustivel subindo fora da conversao e da mobilizacao: {deltas['combustivel']}")
            self.contas_metabolismo[rubrica] += antes - self.q["combustivel"]

    def _efeito(self, deltas: dict[str, int], comida: bool) -> None:
        """Os deltas de uma acao; com a digestao, o que a comida tira da fome vai para o estomago."""
        if comida and self.cc.digestao:
            self._somar({k: v for k, v in deltas.items() if k != "fome"})
            self._ingerir(-deltas["fome"])
        else:
            self._somar(deltas)

    def acao_dono(self, acao: AcaoUsuario) -> None:
        """O efeito de state.aplicar_acao_usuario nos drives. A sujeira (limpar, e o sorteio do alimentar) e o sono (o brincar acorda)
        continuam no Estado, com o motor. Acao fora das seis de hoje (e do tapa) falha alto: as outras sao estimulos proprios ou de outra
        etapa. A racao (alimentar) e comida; o custo de fome do brincar do dono nao.

        Etapa 6: com `drives_novos`, o dono brincar e a atividade "dono_brinca" do tedio (DS-4) e o acariciar e o carinho (secao 8: a
        solidao e o estresse, vezes o medo da mao com `gestos`). O tapa (o valor "tapa", AcaoUsuario.TAPA do A) so com `gestos`: dor,
        susto e estresse; nenhum drive de hoje muda."""
        if acao.value == VALOR_TAPA:
            if not self.cc.gestos:
                raise ValueError("tapa sem a sub-chave gestos (secao 8): so o MotorCorpo com gestos aceita")
            self._estimulo("tapa")
            return
        if acao not in self.t.dono:
            raise ValueError(f"acao do dono sem estimulo no corpo nesta etapa: {acao.value}")
        self._efeito(self.t.dono[acao], acao is AcaoUsuario.ALIMENTAR)
        if self.cc.drives_novos:
            if acao is AcaoUsuario.BRINCAR:
                self.atividade("dono_brinca")
            elif acao is AcaoUsuario.ACARICIAR:
                self._carinho()

    # ---------------------------------------------------------- etapa 6: os drives novos e os gestos

    def _estimulo(self, nome: str) -> None:
        """Um estimulo de quantidade fixa da tabela (o tapa)."""
        self._somar(dict(self.grafo.emissor(nome).efeitos))

    def _carinho(self) -> None:
        """Secao 8: o carinho na solidao e no estresse, vezes (C - medo_da_mao x q_susto) / C com `gestos` (o medo da mao, CD-5); sem
        `gestos`, inteiro. A tristeza (o 0,06 de hoje) ja veio no acao_dono. Com o banheiro (BN-6), tambem o conforto, com o mesmo
        fator."""
        fator = self.C - self.cc.medo_da_mao * self.q["susto"] if self.cc.gestos else self.C
        for nome in ("carinho_solidao", "carinho_estresse") + (("carinho_conforto",) if self.cc.banheiro else ()):
            self._somar({q: div_arred(d * fator, self.C) for q, d in self.grafo.emissor(nome).efeitos})

    def atividade(self, nome: str) -> None:
        """DS-4 (secao 17): a reducao do tedio pela atividade `nome` e div_arred(base x (J - r), J), com r as vezes que ela aparece na
        janela das ultimas J atividades antes desta; depois ela entra na janela e a mais antiga sai. "bola", "brincar" e "explorar" vem do
        motor, uma vez por decisao; "dono_brinca", do acao_dono(BRINCAR). So com `drives_novos`."""
        if not self.cc.drives_novos:
            raise ValueError("atividade do tedio sem a sub-chave drives_novos")
        if nome not in ATIVIDADES:
            raise ValueError(f"atividade desconhecida: {nome!r} (so {ATIVIDADES})")
        base = -dict(self.grafo.emissor(f"atividade:{nome}").efeitos)["tedio"]
        J = self.cc.janela_tedio
        r = self.janela_tedio.count(nome)
        self._somar({"tedio": -div_arred(base * (J - r), J)})
        self.janela_tedio.append(nome)
        del self.janela_tedio[:-J]

    def estimulo_novidade(self, n: int) -> None:
        """Secao 7: explorar e achar `n` objetos novos (os `vistos_novos` do motor) tira 90000 da curiosidade por novidade, ate 2. A
        curiosidade so existe com o mundo fisico (CD-8): sem ela, falha alto."""
        if "curiosidade" not in self.q:
            raise ValueError("novidade sem a curiosidade: ela exige drives_novos e o mundo fisico (CD-8)")
        if type(n) is not int or n < 0:
            raise ValueError(f"numero de novidades precisa ser inteiro >= 0: {n!r}")
        k = min(n, self.cc.curiosidade_max_novidades)
        if k:
            self._somar({q: d * k for q, d in self.grafo.emissor("novidade").efeitos})

    def acao_pet(self, acao: AcaoPet, com_mundo: bool = False) -> None:
        """O efeito de policy.efeito_da_acao_do_pet nos drives, na decisao, antes do tick. O sono (dormir) fica no Estado. O comer e
        comida. Com o mundo fisico (MF-2): comer nao da fome por si (o mundo desfaz o +0,05 antes de qualquer cerebro ver); a comida vem do
        mapa, pelo `estimulo_consumo_mundo`."""
        if com_mundo and acao is AcaoPet.COMER:
            return
        self._efeito(self.t.pet[acao], acao is AcaoPet.COMER)

    def estimulo_bola(self, ganho_humor: float) -> None:
        """Brincar com a bola no cenario (MotorAmbiente, A1): humor + ganho_humor_bola."""
        self._somar({"tristeza": -na_grade(ganho_humor, self.C, "ganho_humor_bola")})

    def estimulo_fruta(self, nutricao: float, efeito_humor: float) -> None:
        """Comer uma fruta (MotorFrutas, N4): fome + nutricao e humor + o efeito da fruta (E2). Sem a digestao (etapa 3), direto na fome."""
        self._efeito({"fome": -na_grade(nutricao, self.C, "nutricao"),
                      "tristeza": -na_grade(efeito_humor, self.C, "efeito_humor")}, True)

    # ---------------------------------------------------------- o banheiro (TAREFA_V2_BANHEIRO, secao 3)

    def _exigir_banheiro(self) -> None:
        if not self.cc.banheiro:
            raise ValueError("estimulo do banheiro sem a sub-chave banheiro (ConfigCorpo.banheiro)")

    def estimulo_aliviar(self) -> None:
        """O pet fez as necessidades (`aliviar`, em qualquer lugar): a vontade cai a 0. A necessidade no chao e o `estimulo_necessidade`,
        que o motor chama quando ela fica (sem o limpador, ou fora do banheiro)."""
        self._exigir_banheiro()
        self.q["vontade"] = 0

    def estimulo_necessidade(self) -> None:
        """A necessidade deixada no chao: o "cheiro" imediato, desconforto + necessidade_desconforto."""
        self._exigir_banheiro()
        self._estimulo("necessidade")

    # ---------------------------------------------------------- o mundo fisico
    def estimulo_andar(self, deslocamento: int, custo_por_subunidade: float) -> None:
        """O andar do mundo fisico (mundo.MotorMundo._consequencia): energia - custo x deslocamento, alem do efeito da acao. O custo de hoje
        (1/6000 por subunidade) e 75 em C; um custo fora da grade falha alto. `deslocamento` em subunidades, inteiro >= 0."""
        if type(deslocamento) is not int or deslocamento < 0:
            raise ValueError(f"deslocamento precisa ser inteiro >= 0: {deslocamento!r}")
        k = na_grade(custo_por_subunidade, self.C, "custo_energia_por_subunidade")
        if deslocamento:
            # com o metabolismo, a tabela tira do combustivel o que soma ao cansaco vezes o fator do gasto (ME-3), sobre o andar inteiro
            # desta decisao (o arredondamento e um so)
            cansaco = k * deslocamento
            self._somar({q: d * (cansaco if q == "cansaco" else gasto_da_atividade(self.cc, cansaco))
                         for q, d in self.grafo.emissor("andar").efeitos})

    def estimulo_consumo_mundo(self, tipo: str, situacao: str, cfg_mundo: ConfigMundo, efeito_fruta: float = 0.0) -> None:
        """Comer uma comida do mapa (mundo.MotorMundo._comer_mundo), pelo `comer` ou pelo "achou e comeu" do explorar:
        - racao madura: fome + ganho_alimentar (a mesma racao do alimentar de hoje; comida, com a digestao);
        - fruta madura: fome + nutricao_fruta e humor + o efeito da fruta (`efeito_fruta`, o do mundo; 0 nas frutas iguais);
        - podre (racao ou fruta): humor + efeito_podre, sem fome.
        Tipo ou situacao fora disso falha alto."""
        if tipo not in TIPOS_COMIDA_MUNDO:
            raise ValueError(f"comida do mundo desconhecida: {tipo!r}")
        if situacao == "podre":
            self._somar({"tristeza": -na_grade(cfg_mundo.efeito_podre, self.C, "efeito_podre")})
        elif situacao != "madura":
            raise ValueError(f"situacao da comida desconhecida: {situacao!r}")
        elif tipo == "racao":
            self._efeito(self.t.dono[AcaoUsuario.ALIMENTAR], True)
        elif tipo in FRUTAS:
            self.estimulo_fruta(cfg_mundo.nutricao_fruta, efeito_fruta)
        else:                                                      # pragma: no cover - TIPOS_COMIDA_MUNDO = racao + FRUTAS
            raise ValueError(f"comida sem estimulo: {tipo!r}")

    # ---------------------------------------------------------- orgao 1: a digestao

    def _ingerir(self, quantidade: int) -> None:
        """A comida vai ao estomago (cortado em C) e a digestao anda na hora, com o que resta da taxa do tick."""
        if quantidade < 0:
            raise ValueError(f"comida negativa: {quantidade}")
        self.q["alimento"] = min(self.C, self.q["alimento"] + quantidade)
        self._digerir()

    def _digerir(self) -> None:
        """A reacao da secao 5: t = min(alimento, fome, o que resta de taxa_digestao no tick); tira t do alimento e da fome. Com a fome em
        0 e comida no estomago, o resto e descartado (o corte de hoje: a fome nao passa de 1)."""
        t = min(self.q["alimento"], self.q["fome"], self.cc.taxa_digestao - self.digerido_tick)
        if t > 0:
            self.q["alimento"] -= t
            self.q["fome"] -= t
            self.digerido_tick += t
            self.digerido_total += t
            # o que a digestao produz, pela tabela: a vontade (banheiro) e o combustivel (metabolismo) sobem com o que se digeriu,
            # num/den, com o resto guardado (a soma ao longo da vida e exata)
            for nome, num, den in self._fracoes:
                resto = getattr(self, f"resto_{nome}") + t * num
                v, resto = divmod(resto, den)
                setattr(self, f"resto_{nome}", resto)
                novo = self.q[nome] + v
                self.q[nome] = min(self.C, novo)
                if nome == "combustivel":
                    self.contas_metabolismo["convertido"] += v
                    self.contas_metabolismo["descartado_teto"] += novo - self.q[nome]
        if self.q["fome"] == 0 and self.q["alimento"] > 0:
            self.descartado_total += self.q["alimento"]
            self.q["alimento"] = 0

    # ---------------------------------------------------------- o tick

    def em_privacao(self) -> bool:
        """O receptor de privacao: algum de fome, desconforto e cansaco acima de C - 0,15 C (Estado.em_privacao de hoje)."""
        return any(self.q[nome] > self.t.limiar_privacao for nome in QUIMICOS_DA_PRIVACAO)

    def _dispara(self, e: Emissor, antes: Estado, noite: bool) -> bool:
        g = e.gatilho
        if g in ("tick", "sujeira", "necessidades"):
            return True
        if g == "acordado":
            return not antes.dormindo
        if g == "dormindo":
            return bool(antes.dormindo)
        if g == "noite_acordado":
            return not antes.dormindo and noite
        if g == "dia_acordado":
            return not antes.dormindo and not noite
        raise ValueError(f"gatilho {g!r} fora da fase 1")      # pragma: no cover - checado na tabela

    def passo(self, antes: Estado, necessidades: int = 0) -> None:
        """Um tick, na ordem de state.avancar_um_tick, pelos emissores da tabela (secao 18). `antes` e o Estado no comeco do tick: a
        sujeira, o sono e a hora vem dele. 0) a digestao; 1) a fase 1: fome, desconforto (o tick e a sujeira), tristeza, cansaco (dormindo,
        noite ou dia), a Vida e as subidas dos drives novos, somados por quimico e cortados uma vez; 2) a fase 2, sobre os valores depois da
        fase 1: o dano pelo receptor de privacao e o estresse pelos drives acima do limiar; 3) as meias-vidas. O motor sorteia a sujeira
        (fora daqui). Com o banheiro, `necessidades` e quantas necessidades estao na regiao do pet neste tick (o motor conta; ate
        necessidade_max_regiao), e a vontade acima do limiar sobe o desconforto (fase 2). Sem o banheiro, `necessidades` tem de ser 0.
        Com o metabolismo: a conversao vai na digestao, o gasto basal na fase 1, as transferencias com limiar (o armazenamento e a
        mobilizacao) entre a fase 1 e a 2, e a falta de combustivel na fase 2."""
        if type(necessidades) is not int or necessidades < 0:
            raise ValueError(f"necessidades na regiao precisa ser inteiro >= 0: {necessidades!r}")
        if necessidades and not self.cc.banheiro:
            raise ValueError("necessidades na regiao sem a sub-chave banheiro")
        if self.cc.digestao:
            self._digerir()                       # o que ficou no estomago, com o que resta da taxa deste tick
        noite = self.cfg.e_noite(antes.tick % TICKS_POR_DIA)
        deltas: dict[str, int] = {}
        for e in self.grafo.da_fase(1):
            if self._dispara(e, antes, noite):
                if e.gatilho == "sujeira":
                    n = antes.sujeira
                elif e.gatilho == "necessidades":
                    n = min(necessidades, self.cc.necessidade_max_regiao)
                else:
                    n = 1
                for q, d in e.efeitos:
                    deltas[q] = deltas.get(q, 0) + d * n
        self._somar(deltas, "gasto_basal")
        # metabolismo: as transferencias com limiar, sobre os valores depois da fase 1 (antes da fase 2: a falta ve o que a reserva
        # devolveu neste tick)
        for r in self._transferencias:
            self._transferir(r)
        privacao = self.em_privacao()
        deltas = {}
        for e in self.grafo.da_fase(2):
            if e.gatilho == "limiar":
                soma = 0
                for le in e.le:
                    soma += max(0, self.q[le.quimico] - e.limiar)
                v = div_arred(soma, e.divisor)
            elif e.gatilho in ("privacao", "sem_privacao"):
                v = 1 if privacao == (e.gatilho == "privacao") else 0
            elif e.gatilho == "acima":
                v = 1 if self.q[e.le[0].quimico] > e.limiar else 0
            elif e.gatilho == "abaixo":
                v = 1 if self.q[e.le[0].quimico] < e.limiar else 0
            else:                                                     # pragma: no cover - checado na tabela
                raise ValueError(f"gatilho {e.gatilho!r} fora da fase 2")
            if v:
                for q, d in e.efeitos:
                    deltas[q] = deltas.get(q, 0) + d * v
        self._somar(deltas)
        bits = self.cc.bits_meia_vida
        for qm in self.grafo.quimicos:
            if qm.k_meia_vida is not None:
                self.q[qm.nome] = passo_meia_vida(self.q[qm.nome], qm.k_meia_vida, bits)
        if self.cc.digestao:
            self.digerido_no_tick = self.digerido_tick          # o tick fechou: a taxa volta inteira no proximo
            self.digerido_tick = 0

    def _transferir(self, r: Reacao) -> None:
        """Uma transferencia com limiar (o metabolismo): com o quimico lido do lado certo do limiar, passa 1 por 1 do consumido ao
        produzido ate min(taxa, a distancia ao limiar, o que ha, o que cabe): nada se perde e nada passa do teto."""
        de, para = r.consome[0], r.produz[0]
        distancia = self.q[r.le] - r.limiar if r.lado == "acima" else r.limiar - self.q[r.le]
        t = min(r.taxa, distancia, self.q[de], self.grafo.quimico(para).teto - self.q[para])
        if t > 0:
            self.q[de] -= t
            self.q[para] += t
            self.contas_metabolismo["armazenado" if para == "reserva" else "mobilizado"] += t

    # ---------------------------------------------------------- leituras

    def drives(self) -> dict[str, float]:
        """Os drives de hoje lidos da quimica: (C - q) / C (a divisao IEEE e exata, igual no Python e no TS)."""
        return {DRIVE_DO_QUIMICO[nome]: (self.C - self.q[nome]) / self.C for nome in QUIMICOS}

    def no_estado(self, estado: Estado) -> Estado:
        """O Estado com os cinco drives trocados pela leitura da quimica (o que o MotorCorpo vai fazer a cada tick, etapa 2)."""
        return replace(estado, **self.drives())

    def falta(self, nome: str) -> int:
        """A falta de um quimico na escala S do cerebro: div_arred(q * S, C)."""
        return div_arred(self.q[nome] * self.S, self.C)

    def receptores(self) -> dict[str, int]:
        """O que o pet sente, na escala S, pelos receptores da tabela (secao 10): os drives de hoje leem o drive, S - falta; os drives
        novos leem a falta, e a dor e o susto a concentracao (a mesma conta, div_arred(q S, C)). Pelo nome do receptor."""
        return {qm.receptor: (self.S - self.falta(qm.nome) if qm.leitura == "drive" else self.falta(qm.nome))
                for qm in self.grafo.receptores()}

    def estagio(self) -> str:
        """Os receptores de estagio sobre a Vida (so com o orgao 2): o estagio e o numero de limiares que a Vida ja cruzou. Com a Vida
        em C - v x tick, cruzar C - v x T e o mesmo que tick >= T: o estagio de hoje, exato. Nao vai ao cerebro."""
        if not self.cc.vida:
            raise ValueError("estagio pela Vida sem o orgao 2 (ConfigCorpo.vida desligada)")
        return ESTAGIOS[sum(1 for limiar in self.limiares_estagio if self.q["vida"] <= limiar)]

    def para_dict(self) -> dict:
        d = {"q": dict(self.q)}
        if self.cc.digestao:
            d["digestao"] = {"digerido_no_tick": self.digerido_no_tick, "digerido_total": self.digerido_total,
                             "descartado_total": self.descartado_total}
        if self.cc.vida:
            d["estagio"] = self.estagio()
        if self.cc.drives_novos:
            d["janela_tedio"] = list(self.janela_tedio)
        if self.cc.banheiro:
            d["resto_vontade"] = self.resto_vontade
        if self.cc.metabolismo:
            d["metabolismo"] = {"resto_combustivel": self.resto_combustivel, "contas": dict(self.contas_metabolismo)}
        return d
