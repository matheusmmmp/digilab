"""Expressao do motivo por estagio (Parte A). Funcao pura, so templates.

| estagio     | canal     | pode revelar                                         |
|-------------|-----------|------------------------------------------------------|
| bebe        | emote     | so humor (vida) ou reacao (combate); NUNCA a causa   |
| crianca     | icones    | acao + icone do PRIMEIRO fator                       |
| adolescente | fragmento | palavras soltas do PRIMEIRO fator                    |
| adulto      | frase     | frase com ate 2 fatores e o evento referenciado      |

A fala nunca inventa causa: so cita fatores do motivo. Sem fator: na vida (sem exploracao) quem decidiu foi o
prior do instinto, e o adulto diz "foi instinto" (decisao do Matheus, 2026-09-29: o "nao sei" em >80% das
decisoes do adulto escondia essa causa verdadeira); na exploracao e no combate, "nao sei, so quis". Cada fator tem um MARCADOR que
aparece em todo texto que o cita e em nenhum outro lugar; a carga verifica
cobertura e unicidade (falta ou colisao levanta TabelaIncompleta). Isso e o
que torna a honestidade testavel.

Arte: placeholders em texto/ASCII, sem asset externo.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .combate_v2.gambits import CATALOGO
from .config import CONFIG_EXPRESSAO, ConfigExpressao
from .events import ACOES_PET_HOJE
from .motivo import FATORES_VIDA, Motivo, nome_base

ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")
CANAL = {"bebe": "emote", "crianca": "icones", "adolescente": "fragmento", "adulto": "frase"}
GENERICO_ADULTO = "Não sei, só quis."
GENERICO_INSTINTO = "Foi instinto: é o meu jeito."


class TabelaIncompleta(ValueError):
    pass


# ------------------------------------------------------------------ fatores
# bebe: sempre "" (bebe nunca cita causa). adulto do combate aceita {p0}, {p1}.

FATORES: dict[str, dict[str, str]] = {
    # vida
    "habito": {"marcador": "costume", "bebe": "", "crianca": "[:costume:]", "adolescente": "costume...",
               "adulto": "por costume"},
    "fome": {"marcador": "fome", "bebe": "", "crianca": "[:fome:]", "adolescente": "fome...",
             "adulto": "por causa da fome"},
    "higiene": {"marcador": "higiene", "bebe": "", "crianca": "[:higiene:]", "adolescente": "higiene...",
                "adulto": "por causa da higiene"},
    "energia": {"marcador": "cansaço", "bebe": "", "crianca": "[:cansaço:]", "adolescente": "cansaço...",
                "adulto": "por causa do cansaço"},
    "humor": {"marcador": "humor", "bebe": "", "crianca": "[:humor:]", "adolescente": "humor...",
              "adulto": "por causa do meu humor"},
    "saude": {"marcador": "saúde", "bebe": "", "crianca": "[:saúde:]", "adolescente": "saúde...",
              "adulto": "por causa da saúde"},
    "sujeira": {"marcador": "sujeira", "bebe": "", "crianca": "[:sujeira:]", "adolescente": "sujeira...",
                "adulto": "por causa da sujeira"},
    "dormindo": {"marcador": "sono", "bebe": "", "crianca": "[:sono:]", "adolescente": "sono...",
                 "adulto": "porque eu estava com sono"},
    "hora": {"marcador": "hora do dia", "bebe": "", "crianca": "[:hora do dia:]", "adolescente": "hora do dia...",
             "adulto": "por causa da hora do dia"},
    "tempo_sem_cuidado": {"marcador": "sem cuidado", "bebe": "", "crianca": "[:sem cuidado:]",
                          "adolescente": "sem cuidado...", "adulto": "porque fiquei muito tempo sem cuidado"},
    # mundo (V2, N5-ACOPLADO): as regras da bola e da fruta e a sub-decisao da fruta. So conduta, nunca sensacao (F2 das frutas)
    "bola": {"marcador": "bola", "bebe": "", "crianca": "[:bola:]", "adolescente": "bola...",
             "adulto": "porque a bola estava ali"},
    "fruta": {"marcador": "fruta à vista", "bebe": "", "crianca": "[:fruta à vista:]", "adolescente": "fruta à vista...",
              "adulto": "porque havia fruta à vista"},
    "incentivo_fruta": {"marcador": "a que eu mais procuro", "bebe": "", "crianca": "[:a que eu mais procuro:]",
                        "adolescente": "a que eu mais procuro...", "adulto": "porque é a que eu mais procuro"},
    "escolha_aprendida_fruta": {"marcador": "aprendi a escolher", "bebe": "", "crianca": "[:aprendi a escolher:]",
                                "adolescente": "aprendi a escolher...", "adulto": "porque aprendi a escolher essa"},
    # memoria (Parte B)
    # o pet que pensa, etapa 2 (TAREFA_V2_PET_QUE_PENSA, secao 2.2): o plano decidiu. So nomeia o que os modelos tem: o lugar e o tipo
    # que mais pesou (p0, p1), a comida que o pet via (p0) ou o tipo que pesou contra a outra escolha (p0)
    "plano_arvore": {"marcador": "lá cai", "bebe": "", "crianca": "[:lá cai:]", "adolescente": "lá cai...",
                     "adulto": "porque no {p0} lá cai {p1}, que me faz bem"},
    "plano_comida": {"marcador": "vi ali", "bebe": "", "crianca": "[:vi ali:]", "adolescente": "vi ali...",
                     "adulto": "porque vi ali {p0}, que me faz bem"},
    "plano_evita": {"marcador": "me faz mal", "bebe": "", "crianca": "[:me faz mal:]", "adolescente": "me faz mal...",
                    "adulto": "porque {p0} me faz mal"},
    "latencia_fome": {"marcador": "demorou com a comida", "bebe": "", "crianca": "[:demorou com a comida:]",
                      "adolescente": "demorou com a comida...",
                      "adulto": "porque você demorou com a comida da última vez"},
    "latencia_higiene": {"marcador": "demorou para me limpar", "bebe": "", "crianca": "[:demorou para me limpar:]",
                         "adolescente": "demorou para me limpar...",
                         "adulto": "porque você demorou para me limpar da última vez"},
    "repreensoes": {"marcador": "bronca", "bebe": "", "crianca": "[:bronca:]", "adolescente": "bronca...",
                    "adulto": "por causa das broncas recentes"},
    "elogios": {"marcador": "elogio", "bebe": "", "crianca": "[:elogio:]", "adolescente": "elogio...",
                "adulto": "por causa dos elogios recentes"},
    # combate (catalogo de gambits)
    "sempre": {"marcador": "sempre faço", "bebe": "", "crianca": "[:sempre faço:]",
               "adolescente": "sempre faço...", "adulto": "porque sempre faço isso"},
    "distancia_eh": {"marcador": "distância", "bebe": "", "crianca": "[:distância:]",
                     "adolescente": "distância...", "adulto": "porque a distância era {p0}"},
    "hp_proprio_abaixo": {"marcador": "machucado", "bebe": "", "crianca": "[:machucado:]",
                          "adolescente": "machucado...",
                          "adulto": "porque eu estava machucado (menos de {p0} da vida)"},
    "guts_proprio_abaixo": {"marcador": "exausto", "bebe": "", "crianca": "[:exausto:]",
                            "adolescente": "exausto...", "adulto": "porque eu estava exausto (guts abaixo de {p0})"},
    "guts_proprio_acima": {"marcador": "folga de guts", "bebe": "", "crianca": "[:folga de guts:]",
                           "adolescente": "folga de guts...",
                           "adulto": "porque eu tinha folga de guts ({p0} ou mais)"},
    "oponente_preparando": {"marcador": "você ia usar o golpe pesado", "bebe": "",
                            "crianca": "[:você ia usar o golpe pesado:]",
                            "adolescente": "você ia usar o golpe pesado...",
                            "adulto": "porque você ia usar o golpe pesado"},
    "oponente_hp_abaixo": {"marcador": "você estava fraco", "bebe": "", "crianca": "[:você estava fraco:]",
                           "adolescente": "você estava fraco...",
                           "adulto": "porque você estava fraco (menos de {p0} da vida)"},
    "oponente_guts_abaixo": {"marcador": "você estava sem guts", "bebe": "", "crianca": "[:você estava sem guts:]",
                             "adolescente": "você estava sem guts...",
                             "adulto": "porque você estava sem guts (abaixo de {p0})"},
    "oponente_repete": {"marcador": "você repetiu", "bebe": "", "crianca": "[:você repetiu:]",
                        "adolescente": "você repetiu...", "adulto": "porque você repetiu '{p0}' {p1} vezes"},
    "oponente_frequente": {"marcador": "você insiste", "bebe": "", "crianca": "[:você insiste:]",
                           "adolescente": "você insiste...", "adulto": "porque você insiste em '{p0}'"},
    # desobediencia: termos da logistica da obediencia (so o de maior contribuicao negativa)
    "vinculo_baixo": {"marcador": "não confio", "bebe": "", "crianca": "[:não confio:]",
                      "adolescente": "não confio...", "adulto": "porque ainda não confio em você"},
    "teimosia": {"marcador": "teimoso", "bebe": "", "crianca": "[:teimoso:]",
                 "adolescente": "teimoso...", "adulto": "porque eu sou teimoso"},
    "necessidade_fome": {"marcador": "barriga vazia", "bebe": "", "crianca": "[:barriga vazia:]",
                         "adolescente": "barriga vazia...", "adulto": "porque eu estava de barriga vazia"},
    "necessidade_higiene": {"marcador": "todo sujo", "bebe": "", "crianca": "[:todo sujo:]",
                            "adolescente": "todo sujo...", "adulto": "porque eu estava todo sujo"},
    "necessidade_energia": {"marcador": "sem forças", "bebe": "", "crianca": "[:sem forças:]",
                            "adolescente": "sem forças...", "adulto": "porque eu estava sem forças"},
    "necessidade_humor": {"marcador": "chateado", "bebe": "", "crianca": "[:chateado:]",
                          "adolescente": "chateado...", "adulto": "porque eu estava chateado"},
    # treino (TAREFA_TREINO_SOMBRIO): fadiga do treino (forcar, pausa ignorada, pedido de pausa)
    "fadiga_treino": {"marcador": "treino puxado", "bebe": "", "crianca": "[:treino puxado:]",
                      "adolescente": "treino puxado...", "adulto": "por causa do treino puxado"},
    # memoria por espacos (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1)
    "demora": {"marcador": "me deixou esperando", "bebe": "", "crianca": "[:me deixou esperando:]",
               "adolescente": "me deixou esperando...", "adulto": "porque lembro que você me deixou esperando"},
    "bronca": {"marcador": "repreensão", "bebe": "", "crianca": "[:repreensão:]",
               "adolescente": "repreensão...", "adulto": "porque lembro da sua repreensão"},
    "elogio": {"marcador": "parabéns", "bebe": "", "crianca": "[:parabéns:]",
               "adolescente": "parabéns...", "adulto": "porque lembro dos seus parabéns"},
    "carinho": {"marcador": "carinho", "bebe": "", "crianca": "[:carinho:]",
                "adolescente": "carinho...", "adulto": "porque lembro do seu carinho"},
    # V2C (C1): turno de execucao do pesado (fintar ou executar)
    "executando_pesado": {"marcador": "hora do pesado", "bebe": "", "crianca": "[:hora do pesado:]",
                          "adolescente": "hora do pesado...", "adulto": "porque era a hora do pesado"},
    # condicoes do combate V2.1 (combate_v2/v21/gambits.py)
    "turno_execucao": {"marcador": "luta longa", "bebe": "", "crianca": "[:luta longa:]",
                       "adolescente": "luta longa...", "adulto": "porque já era uma luta longa (turno {p0} ou mais)"},
    "oponente_vai_preparar": {"marcador": "vi o pesado vindo", "bebe": "", "crianca": "[:vi o pesado vindo:]",
                              "adolescente": "vi o pesado vindo...",
                              "adulto": "porque vi o pesado vindo antes de você preparar"},
}

# ------------------------------------------------------------------ acoes

ACOES_VIDA = {
    "ocioso": ("[à toa]", "à toa", "Fiquei à toa"),
    "dormir": ("[dormir]", "dormir", "Dormi"),
    "comer": ("[comer]", "comer", "Comi"),
    "brincar": ("[brincar]", "brincar", "Brinquei"),
    "chamar_atencao": ("[chamar]", "chamar", "Chamei você"),
    "explorar": ("[explorar]", "explorar", "Explorei"),
    "emburrar": ("[emburrar]", "emburrar", "Emburrei"),
    # desobediencia (TAREFA_PERSONALIDADE_OBEDIENCIA): o "pedido" e a acao do dono
    "recusar": ("[não!]", "não quero", "Não quis fazer o que você pediu"),
    "fazer_outra": ("[outra coisa]", "outra coisa", "Fiz outra coisa em vez do que você pediu"),
    # treino (TAREFA_TREINO_SOMBRIO): o "pedido" e a sessao do dono
    "forcar_treino": ("[forçado]", "forçado", "Treinei além do meu limite"),
    "treinar_cansado": ("[sem pausa]", "sem pausa", "Treinei mesmo pedindo para parar"),
    "enrolar": ("[enrolei]", "enrolei", "Enrolei no treino"),
}
ACOES_COMBATE = {
    "avancar": ("[avançar]", "avançar", "Avancei"),
    "recuar": ("[recuar]", "recuar", "Recuei"),
    "golpe_rapido": ("[golpe]", "golpe", "Dei um golpe rápido"),
    "preparar_pesado": ("[preparar]", "preparar", "Preparei o pesado"),
    "disparo": ("[disparo]", "disparo", "Disparei"),
    "defender": ("[defender]", "defender", "Defendi"),
    "esquivar": ("[esquivar]", "esquivar", "Esquivei"),
    "carregar": ("[carregar]", "carregar", "Carreguei guts"),
    "pesado": ("[pesado!]", "pesado!", "Soltei o pesado que eu tinha preparado"),
    "fintar": ("[finta]", "finta", "Fintei em vez de soltar o pesado"),
    # tecnicas do combate V2.1
    "investida": ("[investida]", "investida", "Investi"),
    "contra_golpe": ("[contra]", "contra-golpe", "Fiz o contra-golpe"),
    "marcar": ("[marcar]", "marcar", "Marquei você"),
    "pele_dura": ("[pele dura]", "pele dura", "Endureci a pele"),
}
# bebe no combate: reacao pela natureza da acao, nunca a causa
REACAO_BEBE = {
    "avancar": "(o_o)>", "recuar": "<(o_o)", "golpe_rapido": "(>_<)!", "preparar_pesado": "(ò_ó)...",
    "disparo": "(>_<)~", "defender": "(-_-)#", "esquivar": "(^o^)~", "carregar": "(ò_ó)*", "pesado": "(ò_ó)!!",
    "fintar": "(¬‿¬)!",
    "investida": "(ò_ó)>>", "contra_golpe": "(ò_ó)|", "marcar": "(o_o)+", "pele_dura": "(-_-)[]",
}
EMOTE_HUMOR = ("(T_T)", "(-_-)", "(^_^)")

# ------------------------------------------------------------------ temperamento (1.3)
# tom por eixo e polo; o bebe ja mostra por emote (temperamento e inato, nao e causa de
# decisao). So entram eixos com |valor| >= limiar_extremo, do mais forte ao mais
# fraco; mesmo esquema de marcador unico dos fatores (honestidade testavel).
TOM_TEMPERAMENTO: dict[tuple[str, str], dict[str, str]] = {
    ("curiosidade", "+"): {"marcador": "fuçador", "bebe": "(o.o)?", "crianca": "[:fuçador:]",
                           "adolescente": "fuçador...", "adulto": "Nasci fuçador, sempre atrás de novidade."},
    ("curiosidade", "-"): {"marcador": "cauteloso", "bebe": "(._.)", "crianca": "[:cauteloso:]",
                           "adolescente": "cauteloso...", "adulto": "Nasci cauteloso com o que não conheço."},
    ("teimosia", "+"): {"marcador": "cabeça-dura", "bebe": "(¬_¬)", "crianca": "[:cabeça-dura:]",
                        "adolescente": "cabeça-dura...", "adulto": "Nasci cabeça-dura."},
    ("teimosia", "-"): {"marcador": "dócil", "bebe": "(u_u)", "crianca": "[:dócil:]",
                        "adolescente": "dócil...", "adulto": "Nasci dócil, fácil de convencer."},
    ("sensibilidade", "+"): {"marcador": "derretido", "bebe": "(*^_^*)", "crianca": "[:derretido:]",
                             "adolescente": "derretido...", "adulto": "Nasci derretido com qualquer agrado."},
    ("sensibilidade", "-"): {"marcador": "melindroso", "bebe": "(;_;)", "crianca": "[:melindroso:]",
                             "adolescente": "melindroso...", "adulto": "Nasci melindroso com qualquer reclamação."},
    ("rancor", "+"): {"marcador": "guardo mágoa", "bebe": "(ò_ó)", "crianca": "[:guardo mágoa:]",
                      "adolescente": "guardo mágoa...", "adulto": "Nasci assim: guardo mágoa por muito tempo."},
    ("rancor", "-"): {"marcador": "esqueço rápido", "bebe": "(^o^)", "crianca": "[:esqueço rápido:]",
                      "adolescente": "esqueço rápido...", "adulto": "Nasci assim: esqueço rápido o que passou."},
}
TEMPERAMENTO_NEUTRO = {"bebe": "(o_o)", "crianca": "[~]", "adolescente": "...", "adulto": "Nasci sem nada que se destaque."}

# ------------------------------------------------------------------ emocao (adendo DF 2.1)
# emote no bebe, icone na crianca, palavra no adolescente, frase no adulto. O marcador e a
# palavra da emocao; a causa e o evento que gerou a memoria (texto sem marcador de fator).
def _em(marcador: str, bebe: str, adulto: str) -> dict[str, str]:
    return {"marcador": marcador, "bebe": bebe, "crianca": f"[{marcador}]", "adolescente": f"{marcador}...",
            "adulto": adulto}


EMOCAO_TXT: dict[str, dict[str, str]] = {
    "raiva": _em("raiva", "(>_<)#", "Senti raiva"),
    "tristeza": _em("tristeza", "(T.T)", "Senti tristeza"),
    "incomodo": _em("incômodo", "(-_-;)", "Senti incômodo"),
    "ferido": _em("ferido", "(;_;)!", "Fiquei ferido"),
    "desdem": _em("desdém", "(-.-)z", "Senti desdém"),
    "vergonha": _em("vergonha", "(>///<)", "Senti vergonha"),
    "euforia": _em("euforia", "(^o^)//", "Senti euforia"),
    "indiferenca": _em("indiferença", "(._.)~", "Senti indiferença"),
    "orgulho": _em("orgulho", "(^_^)v", "Senti orgulho"),
    "ternura": _em("ternura", "(^3^)", "Senti ternura"),
    "timidez": _em("timidez", "(//_//)", "Senti timidez"),
    "alegria": _em("alegria", "(^v^)", "Senti alegria"),
}
CAUSA_EMOCAO = {"demora": "quando você demorou", "bronca": "quando você brigou comigo",
                "elogio": "quando você falou bem de mim", "carinho": "quando você me deu atenção"}

# ------------------------------------------------------------------ carater (adendo DF 2.2)
# o carater e aprendido (medido do adolescente em diante); so eixos com |valor| >= limiar_extremo
TOM_CARATER: dict[tuple[str, str], dict[str, str]] = {
    ("impetuoso", "+"): {"marcador": "esquentado", "adolescente": "esquentado...", "adulto": "Virei esquentado."},
    ("impetuoso", "-"): {"marcador": "contido", "adolescente": "contido...", "adulto": "Virei contido."},
    ("paciente", "+"): {"marcador": "sei esperar", "adolescente": "sei esperar...",
                        "adulto": "Virei alguém que sei esperar."},
    ("paciente", "-"): {"marcador": "afobado", "adolescente": "afobado...", "adulto": "Virei afobado."},
    ("atento", "+"): {"marcador": "ligado em tudo", "adolescente": "ligado em tudo...",
                      "adulto": "Virei ligado em tudo."},
    ("atento", "-"): {"marcador": "distraído", "adolescente": "distraído...", "adulto": "Virei distraído."},
    ("resistente", "+"): {"marcador": "casca-grossa", "adolescente": "casca-grossa...",
                          "adulto": "Virei casca-grossa."},
    ("resistente", "-"): {"marcador": "frágil", "adolescente": "frágil...", "adulto": "Virei frágil."},
}
CARATER_NEUTRO = {"adolescente": "...", "adulto": "Não virei nada de marcante."}

# ------------------------------------------------------------------ desejo (3.2)
# o jogador distingue necessidade de vontade a partir da crianca (marcador do tipo).
# Necessidade cita a necessidade que passou do limiar (o unico fator do calculo);
# vontade cita so que e a acao de maior media aprendida. O bebe nao distingue.
DESEJO_TIPO = {
    "necessidade": {"marcador": "preciso", "crianca": "[preciso!]", "adolescente": "preciso", "adulto": "Eu preciso"},
    "vontade": {"marcador": "queria", "crianca": "[queria?]", "adolescente": "queria", "adulto": "Eu queria"},
}
DESEJO_BEBE = "(>o<)"
VONTADE_ADULTO = "é o que mais deu certo até agora"
# alvo -> (icone, infinitivo); cobre os alvos de necessidade e todas as acoes do pet
ALVOS_DESEJO = {
    "comer": ("[comer]", "comer"), "limpar": ("[banho]", "tomar banho"), "dormir": ("[dormir]", "dormir"),
    "brincar": ("[brincar]", "brincar"), "ocioso": ("[à toa]", "ficar à toa"),
    "chamar_atencao": ("[chamar]", "chamar você"), "explorar": ("[explorar]", "explorar"),
    "emburrar": ("[emburrar]", "emburrar"), "descansar": ("[descanso]", "descansar"),
}


# ------------------------------------------------------------------ confianca de combate (M1, 2.5)
# estado derivado das lutas (digilab/confianca.py), nao e causa de decisao: o bebe mostra so um emote, a crianca a
# versao curta, o adolescente o fragmento e o adulto a frase. Mesmo esquema de marcador unico. "neutro" nao tem
# frase (expressar_confianca devolve None). O "porque" e a lista de lutas do registro em ConfiancaCombate.estado.
CONFIANCA_TXT: dict[str, dict[str, str]] = {
    "confiante": {"marcador": "confiante", "bebe": "(^o^)b", "crianca": "[:confiante:] Ganhei!",
                  "adolescente": "confiante... ganhei as últimas", "adulto": "Tô confiante: ganhei as últimas."},
    "inseguro": {"marcador": "inseguro", "bebe": "(;_;)?", "crianca": "[:inseguro:] Perdi de novo…",
                 "adolescente": "inseguro... depois daquelas derrotas", "adulto": "Ando inseguro depois daquelas derrotas."},
    "entediado": {"marcador": "sei tudo dele", "bebe": "(-.-)~", "crianca": "[:sei tudo dele:] De novo?",
                  "adolescente": "de novo esse aí... sei tudo dele", "adulto": "De novo esse aí? Já sei tudo dele."},
}


def expressar_confianca(estado: dict, estagio: str) -> Expressao | None:
    """Frase de estado da confianca (M1): `estado` e o dict de ConfiancaCombate.estado(tick). Neutro: None."""
    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    nome = estado["estado"]
    if nome == "neutro":
        return None
    if nome not in CONFIANCA_TXT:
        raise TabelaIncompleta(f"estado de confianca sem texto: {nome!r}")
    return Expressao(CANAL[estagio], CONFIANCA_TXT[nome][estagio], ("confianca", tuple(estado["lutas"])))


def confiancas_citadas(conteudo: str) -> set[str]:
    return {k for k, e in CONFIANCA_TXT.items() if e["marcador"] in conteudo}


def validar_tabelas(fatores_obrigatorios=None) -> None:
    from .combate_v2.v21.gambits import CATALOGO as CATALOGO_V21

    obrig = set(fatores_obrigatorios if fatores_obrigatorios is not None
                else set(FATORES_VIDA) | set(CATALOGO) | set(CATALOGO_V21) | set(_fatores_extra()))
    faltando = sorted(obrig - set(FATORES))
    if faltando:
        raise TabelaIncompleta(f"fatores sem entrada na tabela: {faltando}")
    for nome, e in FATORES.items():
        for chave in ("marcador",) + ESTAGIOS:
            if chave not in e:
                raise TabelaIncompleta(f"fator {nome!r} sem entrada para {chave!r}")
        if e["bebe"] != "":
            raise TabelaIncompleta(f"fator {nome!r}: bebe nao pode citar causa")
        for est in ("crianca", "adolescente", "adulto"):
            if e["marcador"] not in e[est]:
                raise TabelaIncompleta(f"fator {nome!r}/{est}: texto sem o marcador {e['marcador']!r}")
    marcadores = {n: e["marcador"] for n, e in FATORES.items()}
    for n1, m1 in marcadores.items():
        for n2, e2 in FATORES.items():
            if n1 != n2 and any(m1 in e2[est] for est in ("crianca", "adolescente", "adulto")):
                raise TabelaIncompleta(f"marcador de {n1!r} aparece no texto de {n2!r}")
    faltam_vida = sorted(set(a.value for a in ACOES_PET_HOJE) - set(ACOES_VIDA))
    from .combate_v2.regras import Acao
    from .combate_v2.v21.regras import Acao as AcaoV21

    todas = set(a.value for a in Acao) | set(a.value for a in AcaoV21)
    faltam_comb = sorted(todas - set(ACOES_COMBATE))
    faltam_reacao = sorted(todas - set(REACAO_BEBE))
    if faltam_vida or faltam_comb or faltam_reacao:
        raise TabelaIncompleta(f"acoes sem texto: vida {faltam_vida}, combate {faltam_comb}, reacao {faltam_reacao}")
    fixos = [t for trio in list(ACOES_VIDA.values()) + list(ACOES_COMBATE.values()) for t in trio]
    fixos += [GENERICO_ADULTO] + list(REACAO_BEBE.values()) + list(EMOTE_HUMOR)
    for n, m in marcadores.items():
        for t in fixos:
            if m in t:
                raise TabelaIncompleta(f"marcador de {n!r} ({m!r}) aparece em texto fixo {t!r}")


def _fatores_extra() -> tuple[str, ...]:
    """Fatores alem da vida e do catalogo (memoria, Parte B), se o modulo existir."""
    try:
        from .memoria import FATORES_MEMORIA
        from .memoria_espacos import FATORES_ESPACOS
    except ImportError:
        return ()
    return FATORES_MEMORIA + FATORES_ESPACOS


@dataclass(frozen=True)
class Expressao:
    canal: str
    conteudo: str
    motivo_ref: tuple  # (origem, tick) ou (origem, turno)


def estagio_por_idade(dias: float, cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> str:
    """PROVISORIO: idade em dias simulados -> estagio. Vira derivado da evolucao quando ela existir."""
    if dias < 0:
        raise ValueError(f"idade negativa: {dias}")
    if dias < cfg.dias_fim_bebe:
        return "bebe"
    if dias < cfg.dias_fim_crianca:
        return "crianca"
    if dias < cfg.dias_fim_adolescente:
        return "adolescente"
    return "adulto"


def _params(fator: str) -> list[str]:
    if "(" not in fator:
        return []
    corpo = fator[fator.index("(") + 1:-1]
    saida = []
    for p in corpo.split(","):
        try:
            f = float(p)
            saida.append(f"{f:.0%}" if 0 < f < 1 else p)
        except ValueError:
            saida.append(p.replace("_", " "))
    return saida


def _texto_fator(fator: str, estagio: str) -> str:
    base = nome_base(fator)
    if base not in FATORES:
        raise TabelaIncompleta(f"fator sem entrada: {base!r}")
    t = FATORES[base][estagio]
    ps = _params(fator)
    return t.format(**{f"p{i}": v for i, v in enumerate(ps)}) if "{" in t else t


def _refs(motivo: Motivo) -> str:
    if not motivo.evento_ref:
        return ""
    if motivo.origem == "vida":
        return " (lembro do evento #" + ", #".join(str(r) for r in motivo.evento_ref) + ")"
    return " (turno " + ", ".join(str(r) for r in motivo.evento_ref) + ")"


def expressar(motivo: Motivo, estagio: str, humor: float | None = None,
              cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> Expressao:
    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    ref = (motivo.origem, motivo.tick if motivo.origem == "vida" else motivo.turno)
    acoes = ACOES_VIDA if motivo.origem == "vida" else ACOES_COMBATE
    if motivo.acao not in acoes:
        raise TabelaIncompleta(f"acao sem texto: {motivo.acao!r}")
    icone, palavra, frase = acoes[motivo.acao]
    fatores = () if motivo.exploracao else motivo.fatores

    if estagio == "bebe":
        if motivo.origem == "vida":
            if humor is None:
                raise ValueError("bebe na vida precisa do humor")
            i = 2 if humor >= cfg.humor_alegre else 1 if humor >= cfg.humor_neutro else 0
            return Expressao("emote", EMOTE_HUMOR[i], ref)
        return Expressao("emote", REACAO_BEBE[motivo.acao], ref)
    if estagio == "crianca":
        partes = [icone] + ([_texto_fator(fatores[0], "crianca")] if fatores else [])
        return Expressao("icones", " ".join(partes), ref)
    if estagio == "adolescente":
        return Expressao("fragmento", f"{palavra}... " + (_texto_fator(fatores[0], "adolescente") if fatores else ""), ref)
    if not fatores:
        geral = GENERICO_INSTINTO if motivo.origem == "vida" and not motivo.exploracao else GENERICO_ADULTO
        return Expressao("frase", f"{frase}. {geral}", ref)
    causas = " e ".join(_texto_fator(f, "adulto") for f in fatores[:2])
    return Expressao("frase", f"{frase} {causas}{_refs(motivo)}.", ref)


def eixos_marcantes(temperamento, cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> list[tuple[str, str]]:
    """(eixo, polo) com |valor| >= limiar, do mais forte ao mais fraco (empate: ordem de EIXOS)."""
    from .temperamento import EIXOS

    return eixos_extremos(temperamento.para_dict(), EIXOS, cfg)


def expressar_temperamento(temperamento, estagio: str, cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> Expressao:
    """Tom do temperamento inato (1.3): bebe emote do eixo mais forte; crianca e adolescente
    o mais forte; adulto ate 2. Sem eixo marcante: texto neutro, sem marcador."""
    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    marcantes = eixos_marcantes(temperamento, cfg)
    ref = ("temperamento", 0)
    if not marcantes:
        return Expressao(CANAL[estagio], TEMPERAMENTO_NEUTRO[estagio], ref)
    if estagio == "adulto":
        frases = [TOM_TEMPERAMENTO[k]["adulto"] for k in marcantes[:2]]
        return Expressao("frase", " ".join(frases[:1] + ["E n" + f[1:] for f in frases[1:]]), ref)
    return Expressao(CANAL[estagio], TOM_TEMPERAMENTO[marcantes[0]][estagio], ref)


def expressar_emocao(emocao, estagio: str) -> Expressao:
    """Emocao de um evento de memoria (adendo 2.1): so a emocao e o evento que a gerou."""
    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    if emocao.nome not in EMOCAO_TXT:
        raise TabelaIncompleta(f"emocao sem texto: {emocao.nome!r}")
    if emocao.categoria not in CAUSA_EMOCAO:
        raise TabelaIncompleta(f"categoria sem causa de emocao: {emocao.categoria!r}")
    t = EMOCAO_TXT[emocao.nome]
    ref = ("emocao", emocao.tick)
    if estagio == "adulto":
        r = f" (lembro do evento #{emocao.ref})" if emocao.ref is not None else ""
        return Expressao("frase", f"{t['adulto']} {CAUSA_EMOCAO[emocao.categoria]}{r}.", ref)
    return Expressao(CANAL[estagio], t[estagio], ref)


def eixos_extremos(valores: dict, ordem, cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> list[tuple[str, str]]:
    """(eixo, polo) com |valor| >= limiar_extremo, do mais forte ao mais fraco (empate: `ordem`)."""
    vals = [(abs(valores[e]), -i, e) for i, e in enumerate(ordem)]
    return [(e, "+" if valores[e] > 0 else "-") for v, _, e in sorted(vals, reverse=True) if v >= cfg.limiar_extremo]


EIXOS_CARATER = ("impetuoso", "paciente", "atento", "resistente")


def expressar_carater(carater: dict, estagio: str, cfg: ConfigExpressao = CONFIG_EXPRESSAO) -> Expressao:
    """Carater aprendido (medido do adolescente em diante): mesma regra de extremos do temperamento."""
    if estagio not in ("adolescente", "adulto"):
        raise ValueError(f"carater so existe do adolescente em diante, nao em {estagio!r}")
    if set(carater) != set(EIXOS_CARATER):
        raise TabelaIncompleta(f"eixos de carater diferentes da tabela: {sorted(carater)}")
    ext = eixos_extremos(carater, EIXOS_CARATER, cfg)
    ref = ("carater", 0)
    if not ext:
        return Expressao(CANAL[estagio], CARATER_NEUTRO[estagio], ref)
    if estagio == "adulto":
        frases = [TOM_CARATER[k]["adulto"] for k in ext[:2]]
        return Expressao("frase", " ".join(frases[:1] + ["E v" + f[1:] for f in frases[1:]]), ref)
    return Expressao("fragmento", TOM_CARATER[ext[0]]["adolescente"], ref)


def expressar_desejo(desejo, estagio: str) -> Expressao:
    """Desejo (3.2): bebe nao distingue; da crianca em diante o marcador do tipo aparece."""
    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    if desejo.alvo not in ALVOS_DESEJO:
        raise TabelaIncompleta(f"alvo de desejo sem texto: {desejo.alvo!r}")
    ref = ("desejo", desejo.tick)
    if estagio == "bebe":
        return Expressao("emote", DESEJO_BEBE, ref)
    icone, verbo = ALVOS_DESEJO[desejo.alvo]
    t = DESEJO_TIPO[desejo.tipo]
    if estagio == "crianca":
        return Expressao("icones", f"{t['crianca']} {icone}", ref)
    if desejo.tipo == "necessidade":
        from .desejo import NECESSIDADE_DO_ALVO

        causa = NECESSIDADE_DO_ALVO[desejo.alvo]
        if estagio == "adolescente":
            return Expressao("fragmento", f"{t['adolescente']} {verbo}... {_texto_fator(causa, 'adolescente')}", ref)
        return Expressao("frase", f"{t['adulto']} {verbo} {_texto_fator(causa, 'adulto')}.", ref)
    if estagio == "adolescente":
        return Expressao("fragmento", f"{t['adolescente']} {verbo}...", ref)
    return Expressao("frase", f"{t['adulto']} {verbo}: {VONTADE_ADULTO}.", ref)


def validar_tabelas_personalidade() -> None:
    """Cobertura e unicidade das tabelas de temperamento e desejo (mesmas regras de FATORES)."""
    from .desejo import NECESSIDADES, TIPOS
    from .temperamento import EIXOS

    faltam = sorted(f"{e}{p}" for e in EIXOS for p in "+-" if (e, p) not in TOM_TEMPERAMENTO)
    if faltam:
        raise TabelaIncompleta(f"eixos de temperamento sem tom: {faltam}")
    for k, e in TOM_TEMPERAMENTO.items():
        for chave in ("marcador",) + ESTAGIOS:
            if chave not in e:
                raise TabelaIncompleta(f"tom {k} sem entrada para {chave!r}")
        for est in ("crianca", "adolescente", "adulto"):
            if e["marcador"] not in e[est]:
                raise TabelaIncompleta(f"tom {k}/{est}: texto sem o marcador {e['marcador']!r}")
        if not e["adulto"].startswith("Nasci "):
            raise TabelaIncompleta(f"tom {k}/adulto deve comecar com 'Nasci '")
    if len({e["bebe"] for e in TOM_TEMPERAMENTO.values()}) != len(TOM_TEMPERAMENTO):
        raise TabelaIncompleta("emotes de temperamento repetidos")
    if sorted(DESEJO_TIPO) != sorted(TIPOS):
        raise TabelaIncompleta(f"tipos de desejo sem texto: {sorted(set(TIPOS) - set(DESEJO_TIPO))}")
    for tipo, e in DESEJO_TIPO.items():
        if any(e["marcador"] not in e[est] for est in ("crianca", "adolescente", "adulto")):
            raise TabelaIncompleta(f"desejo {tipo!r}: texto sem o marcador")
    alvos = {a.value for a in ACOES_PET_HOJE} | {alvo for _, alvo in NECESSIDADES.values()}
    if alvos - set(ALVOS_DESEJO):
        raise TabelaIncompleta(f"alvos de desejo sem texto: {sorted(alvos - set(ALVOS_DESEJO))}")
    # nenhum marcador (fator, tom ou tipo de desejo) pode aparecer em texto que nao o cita
    marc = {("fator", n): e["marcador"] for n, e in FATORES.items()}
    marc.update({("tom", k): e["marcador"] for k, e in TOM_TEMPERAMENTO.items()})
    marc.update({("desejo", k): e["marcador"] for k, e in DESEJO_TIPO.items()})
    marc.update({("emocao", k): e["marcador"] for k, e in EMOCAO_TXT.items()})
    marc.update({("carater", k): e["marcador"] for k, e in TOM_CARATER.items()})
    marc.update({("confianca", k): e["marcador"] for k, e in CONFIANCA_TXT.items()})
    textos = {("tom", k): [e[s] for s in ("crianca", "adolescente", "adulto")] for k, e in TOM_TEMPERAMENTO.items()}
    textos.update({("desejo", k): [e[s] for s in ("crianca", "adolescente", "adulto")] for k, e in DESEJO_TIPO.items()})
    textos.update({("emocao", k): [e[s] for s in ("crianca", "adolescente", "adulto")] for k, e in EMOCAO_TXT.items()})
    textos.update({("carater", k): [e[s] for s in ("adolescente", "adulto")] for k, e in TOM_CARATER.items()})
    textos.update({("confianca", k): [e[s] for s in ("crianca", "adolescente", "adulto")] for k, e in CONFIANCA_TXT.items()})
    # confianca (M1): os tres estados com frase tem texto em todo estagio, com o marcador nos falados; emotes distintos
    from .confianca import ESTADOS

    if set(ESTADOS) - {"neutro"} != set(CONFIANCA_TXT):
        raise TabelaIncompleta(f"estados de confianca sem texto: {sorted(set(ESTADOS) - {'neutro'} - set(CONFIANCA_TXT))}")
    for k, e in CONFIANCA_TXT.items():
        for chave in ("marcador",) + ESTAGIOS:
            if chave not in e or not e[chave]:
                raise TabelaIncompleta(f"confianca {k!r} sem entrada para {chave!r}")
        if any(e["marcador"] not in e[st] for st in ("crianca", "adolescente", "adulto")):
            raise TabelaIncompleta(f"confianca {k!r}: texto sem o marcador")
    if len({e["bebe"] for e in CONFIANCA_TXT.values()}) != len(CONFIANCA_TXT):
        raise TabelaIncompleta("emotes de confianca repetidos")
    fixos = list(TEMPERAMENTO_NEUTRO.values()) + [DESEJO_BEBE, VONTADE_ADULTO] + [t for par in ALVOS_DESEJO.values() for t in par]
    fixos += list(CAUSA_EMOCAO.values()) + list(CARATER_NEUTRO.values())
    # emocao: toda emocao da tabela de digilab/emocao.py tem texto, com marcador em cada estagio falado
    from .emocao import EMOCOES, nomes_de_emocao

    if nomes_de_emocao() - set(EMOCAO_TXT):
        raise TabelaIncompleta(f"emocoes sem texto: {sorted(nomes_de_emocao() - set(EMOCAO_TXT))}")
    if set(EMOCOES) - set(CAUSA_EMOCAO):
        raise TabelaIncompleta(f"categorias sem causa de emocao: {sorted(set(EMOCOES) - set(CAUSA_EMOCAO))}")
    for k, e in EMOCAO_TXT.items():
        if any(e["marcador"] not in e[st] for st in ("crianca", "adolescente", "adulto")):
            raise TabelaIncompleta(f"emocao {k!r}: texto sem o marcador")
    if len({e["bebe"] for e in EMOCAO_TXT.values()}) != len(EMOCAO_TXT):
        raise TabelaIncompleta("emotes de emocao repetidos")
    for k, e in TOM_CARATER.items():
        if any(e["marcador"] not in e[st] for st in ("adolescente", "adulto")):
            raise TabelaIncompleta(f"carater {k}: texto sem o marcador")
        if not e["adulto"].startswith("Virei "):
            raise TabelaIncompleta(f"carater {k}/adulto deve comecar com 'Virei '")
    faltam_car = sorted(f"{e}{p}" for e in EIXOS_CARATER for p in "+-" if (e, p) not in TOM_CARATER)
    if faltam_car:
        raise TabelaIncompleta(f"eixos de carater sem tom: {faltam_car}")
    for dono, m in marc.items():
        for outro, ts in textos.items():
            if outro != dono and any(m in t for t in ts):
                raise TabelaIncompleta(f"marcador {m!r} de {dono} aparece no texto de {outro}")
        for t in fixos:
            if m in t:
                raise TabelaIncompleta(f"marcador {m!r} de {dono} aparece em texto fixo {t!r}")
        if dono[0] != "fator":
            for n, e in FATORES.items():
                if any(m in e[s] for s in ("crianca", "adolescente", "adulto")):
                    raise TabelaIncompleta(f"marcador {m!r} de {dono} aparece no fator {n!r}")


# fala fria (TAREFA_TREINO_SOMBRIO): sobrecarga no aviso (crianca -> adolescente) ou forma sombria.
# So o tom muda (emote apagado, abertura seca); o conteudo e os fatores citados sao os mesmos.
EMOTE_FRIO = "(-_-)"
ABERTURA_FRIA = "Hm."


def esfriar(expr: Expressao) -> Expressao:
    if expr.canal == "emote":
        return replace(expr, conteudo=EMOTE_FRIO)
    if expr.canal == "frase":
        return replace(expr, conteudo=f"{ABERTURA_FRIA} {expr.conteudo}")
    return replace(expr, conteudo=f"... {expr.conteudo}")


def marcadores_citados(conteudo: str) -> set[str]:
    """Fatores (nome base) cujo marcador aparece no conteudo."""
    return {n for n, e in FATORES.items() if e["marcador"] in conteudo}


def emocoes_citadas(conteudo: str) -> set[str]:
    return {k for k, e in EMOCAO_TXT.items() if e["marcador"] in conteudo}


def carateres_citados(conteudo: str) -> set[tuple[str, str]]:
    return {k for k, e in TOM_CARATER.items() if e["marcador"] in conteudo}


def tons_citados(conteudo: str) -> set[tuple[str, str]]:
    """(eixo, polo) do temperamento cujo marcador aparece no conteudo."""
    return {k for k, e in TOM_TEMPERAMENTO.items() if e["marcador"] in conteudo}


validar_tabelas()
validar_tabelas_personalidade()
