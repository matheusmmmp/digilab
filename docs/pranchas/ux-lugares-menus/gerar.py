# Gera a prancha "Lugares da ilha: menus" (L2/L3), rodada 2: cada menu e um lugar da ilha, e A REGRA DO TEXTO (a vista so tem icone,
# numero e um rotulo de 1 a 3 palavras; frase so no "como funciona" fechado ou no balao do foco/hover). So desenho; nenhum codigo do jogo.
# A pele vem de ?pele=vidro|xcom no endereco, e ?sem tira as notas amarelas.
# Uso: python docs/pranchas/ux-lugares-menus/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim).
# O fundo img/cena_sem_pet.jpg e uma captura do jogo de 2026-11-06 (a ilha de dia, sem HUD, a 1920 x 931), com o pet embutido
# e o "Zz" apagados por remendo de grama da propria captura; o pet e o objeto novo vem por cima, nesta prancha.
# O "antes" (img/antes/*.jpg, antes_palavras.json) sao capturas e contagens do jogo de hoje (medir_antes.mjs; o save "champion").
#
# O ESTADO DESENHADO e o mesmo do antes: Growlmon, Champion, brasao Coragem; o Tamer sem medalha, 0 chips, 0 cartas; "15h 15min ate virar
# Ultimate" e exemplo de layout. As outras telas seguem o mesmo pet.
#
# DE ONDE VEM CADA TEXTO E NUMERO (a tabela completa esta em docs/PROPOSTAS_V3_UX_TELA_PET.md, secao "Lugares da ilha: menus (L2/L3)"):
#   nomes das formas e niveis ....... web/app/motor/nomes.ts (DIGIMON_DA_FORMA: o Coragem e Koromon, Agumon/Guilmon, Greymon, Kyubimon,
#                                     Birdramon, Growlmon, ...), NOME_EST, NOME_ARQ, NOME_ESP, NOME_STAT, NOME_EXERCICIO, NOME_PET
#   treino .......................... constantes.ts CTR (ganhoPri 2, ganhoSec 1, tetoEstagio.adolescente 12, limiarPausa 40, limiteForcar 60,
#                                     intervalo 10), CSO (aviso 30, sombrio 60), APTIDAO.brasa (forca 1,2, guarda 1,1); TelaTreinar.tsx
#   evolucao ........................ CMD.adulto 3 (o Ultimate pede 3 medalhas), CAT.sparring 10, CLE.limiarTaxa .8; TelaEvolucao.tsx;
#                                     src/tamer.ts medalhasQueFaltam (as 3 primeiras que o Tamer nao tem: Campina, Torre de pedra, Floresta)
#   itens ........................... motor/itens.ts (ITENS: nome e efeito; ITEM_DA_MEDALHA; CARTA_DA_REVANCHE), CIT (vagas [1,1] [3,2] [5,3],
#                                     gutsFolego 20, curaAbaixo .3, curaFracao .2); src/telas/crescer/TelaItens.tsx (deOnde, comoGanhar, o
#                                     "pede um Champion"); "treino 10/11" e o porqueItensNaoValem do save (texto do antes)
#   arena e medalhas ................ src/luta.ts, src/nomesRivais.ts (DIGIMON_BOT), motor/bots.ts (NOME_BOT, os NPCs), motor/medalhas.ts,
#                                     motor/arenas.ts, src/tamer.ts (comoGanhar), motor/liga.ts (MEDALHAS_LIGA); sparringTexto (luta.ts)
#   registro, catalogo, ajustes ..... motor.ts (_hist), TelaRegistro.tsx, TelaCatalogo.tsx (formasDoBrasao: 19), TelaConfig.tsx
# EXEMPLO DE LAYOUT, NUNCA DADO: Dia 3, 07:42, 07:31, 15h 15min, fadiga 20, estagio 10/12, semente 7000, 76 eventos, as horas do registro,
#   o rival escolhido. Os niveis da trava vem do plano de progressao DECIDIDO (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.3, 3.4, 4.1 e 4.2;
#   NIVEL, abaixo). Nenhum numero de jogo novo.
from pathlib import Path
from urllib.parse import quote

A = "../../../../Assets/arena_up"  # fora do git (UI_GUIDELINES 5.1); so as capturas precisam dele

# ---------------------------------------------------------------------------------------------------- icones (traco, estilo lucide)
IC = {
    "pet": '<circle cx="12" cy="13" r="6"/><circle cx="7" cy="5" r="1.6"/><circle cx="17" cy="5" r="1.6"/>',
    "crescer": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "lutar": '<path d="M5 19L19 5"/><path d="M14 5h5v5"/><path d="M5 14l5 5"/>',
    "diario": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 8h6M9 12h6"/>',
    "conversar": '<path d="M4 5h16v11H9l-5 4z"/>',
    "ajustes": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
    "digibrain": '<path d="M12 4c-4 0-7 3-7 7 0 4 3 8 7 8s7-4 7-8c0-4-3-7-7-7z"/><path d="M12 4v15"/>',
    "estado": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "acoes": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "treinar": '<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>',
    "aprend": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    "evolucao": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-12 7"/>',
    "itens": '<rect x="7" y="7" width="10" height="10" rx="1"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    "arena": '<path d="M5 19L19 5"/><path d="M14 5h5v5"/><path d="M5 14l5 5"/>',
    "exploracao": '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    "fronteira": '<path d="M5 21V4"/><path d="M5 4h12l-2.5 4L17 12H5"/>',
    "medalhas": '<circle cx="12" cy="15" r="5"/><path d="M8 3l4 7 4-7"/>',
    "registro": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "catalogo": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    "geracoes": '<circle cx="12" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/><path d="M12 7v5M6 17v-3h12v3"/>',
    "cenarios": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 15l5-5 4 4 3-3 6 6"/>',
    # exercicios (os mesmos do ICONE_RESERVA de TelaTreinar.tsx: Dumbbell, Footprints, Crosshair, Wind, Flower2, Shield)
    "levantar_pedra": '<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>',
    "corrida": '<path d="M7 4c2 0 3 2 3 5s-1 4-3 4-3-1-3-4 1-5 3-5zM17 10c2 0 3 2 3 5s-1 4-3 4-3-1-3-4 1-5 3-5z"/>',
    "alvo": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>',
    "esquiva": '<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h7"/>',
    "meditar": '<circle cx="12" cy="9" r="3"/><path d="M12 12v9M7 16c3 0 5 1 5 5M17 16c-3 0-5 1-5 5"/>',
    "resistencia": '<path d="M12 3l8 3v6c0 5-4 8-8 9-4-1-8-4-8-9V6z"/>',
    # itens
    "chip": '<rect x="7" y="7" width="10" height="10" rx="1"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    "chip_stat": '<rect x="7" y="7" width="10" height="10" rx="1"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4M12 10v4M10 12h4"/>',
    "chip_regra": '<rect x="7" y="7" width="10" height="10" rx="1"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4M10 12h4l-1.5-1.5M14 12l-1.5 1.5"/>',
    "carta": '<rect x="6" y="3" width="12" height="18" rx="1.5"/><path d="M12 8l1.5 3 3 .5-2.2 2 .6 3-2.9-1.5-2.9 1.5.6-3-2.2-2 3-.5z"/>',
    "alerta": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/>',
    "coberto": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "estrela": '<path d="M12 3l2.6 5.6 6 .6-4.5 4 1.3 6L12 16.3 6.6 19.2l1.3-6-4.5-4 6-.6z"/>',
    "relogio": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "historico": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
    "lua": '<path d="M20 14A8 8 0 1 1 10 4a6 6 0 0 0 10 10z"/>',
    "mao": '<path d="M8 13V5a1.5 1.5 0 0 1 3 0v6M11 10V4a1.5 1.5 0 0 1 3 0v7M14 10V5a1.5 1.5 0 0 1 3 0v8c0 4-3 7-6 7s-5-2-6-4l-2-4a1.5 1.5 0 0 1 2.6-1.5L8 13"/>',
    # o lucide "tent" do cartao de destrave do Diario (plano 4.2) e os do mobile minimo (M1: as acoes e os vitais)
    "tent": '<path d="M3.5 21 14 3"/><path d="M20.5 21 10 3"/><path d="M15.5 21 12 15l-3.5 6"/><path d="M2 21h20"/>',
    "drumstick": '<path d="M15.4 15.6a5 5 0 1 0-7-7c-1.6 1.6-1.7 3.4-1.4 5l-2.8 2.8a2 2 0 1 0 2.4 2.4l2.8-2.8c1.6.3 3.4.2 5-1.4z"/>',
    "music": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "droplet": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "ellipsis": '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    "zap": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "smile": '<circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
    "saude": '<path d="M20 9c0 5-8 11-8 11S4 14 4 9a4 4 0 0 1 8-1 4 4 0 0 1 8 1z"/><path d="M3 12h5l2-3 3 6 2-3h6"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14c2 .8 3 2.8 3 6"/>',
    # controles
    "x":'<path d="M6 6l12 12M18 6L6 18"/>',
    "seta": '<path d="M9 6l6 6-6 6"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v.5"/>',
    "cadeado": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "aberto": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 7.5-2"/>',
    "replay": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
    "copiar": '<rect x="8" y="8" width="12" height="12" rx="1"/><path d="M4 16V4h12"/>',
    "olho": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "dica": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    "frasco": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/>',
    "som": '<path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M17 9a4 4 0 0 1 0 6"/>',
    "camera": '<path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="4"/>',
    "brasao": '<path d="M12 3l7 4v6c0 4-3 7-7 8-4-1-7-4-7-8V7z"/>',
    "saco": '<path d="M12 2v3"/><rect x="8" y="5" width="8" height="15" rx="4"/><path d="M8 10h8M8 15h8"/>',
    "portao": '<path d="M4 21V8M20 21V8M2 8h20M3 5h18"/><path d="M10 8v6h4V8"/>',
    "barraca": '<path d="M12 3L2 21h20z"/><path d="M12 3v18M9 21l3-6 3 6"/>',
}


def svg(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>'


def mascara(n: str) -> str:
    """o icone como mascara (o simbolo pintado com a amostra do fundo); o #000 e so o alfa da mascara, como o --hx-mascara"""
    s = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='#000' stroke-width='2.6' "
         f"stroke-linecap='round' stroke-linejoin='round'>{IC[n]}</svg>")
    # aspas simples no url(), porque vai dentro do style="..."; as do proprio SVG viram %27
    return "url('data:image/svg+xml," + quote(s, safe="/:= ") + "')"


def b(txt: str) -> str:
    """o balao do foco/hover: fica no HTML com hidden (o innerText nao conta); no jogo, aria-describedby e o tooltip"""
    return f'<span class="caixa balao" role="tooltip" hidden>{txt}</span>'


def balao_aberto(txt: str, x: float, y: float, w: int = 300) -> str:
    """o balao aberto de demonstracao (o foco ou o hover num quadro), FORA do painel, para nao entrar na contagem"""
    return f'<span class="caixa balao" role="tooltip" style="left:{x}px;top:{y}px;max-width:{w}px">{txt}</span>'


# ---------------------------------------------------------------------------------------------------- a camera
# (escala, ox, oy): o plano da ilha (1920 x 931) escalado e deslocado. Os enquadramentos sao de layout, nao de jogo.
CAM = {
    "ilha": (1.0205, 20, 0),        # a ilha normal (931 x 1,0205 = 950)
    "viagem": (1.18, 330, 40),      # o meio do caminho ate o saco (quadro b)
    "saco": (1.35, 650, 83),        # Crescer
    "saco_ad": (1.35, 247, 83),     # Crescer, no antes x depois (o saco mais a direita, ao lado do painel)
    "portao": (1.30, 576, 201),     # Lutar
    "barraca": (1.35, 0, 145),      # Diario
}


def tela(x: float, y: float, cam: str) -> tuple[float, float]:
    s, ox, oy = CAM[cam]
    return x * s - ox, y * s - oy


# ---------------------------------------------------------------------------------------------------- os sprites
# (quadro w, h, folha sw, sh, passo x, y), de Assets/arena_up/dados/atlas.json; so o Growlmon usa outros quadros (o passo)
SPR = {
    "Growlmon": (105, 77, 741, 467, 106, 78),
    "Agumon": (94, 68, 664, 482, 95, 69),
    "Koromon": (113, 92, 797, 557, 114, 93),
}
POSE = {"parado": (0, 0), "andando": (2, 5), "treino": (3, 0)}   # quadros da folha do Growlmon (coluna, linha)


def pet(cx: float, base: float, pose: str, k: float = 1.8, virado: bool = False, nome: str = "Growlmon") -> str:
    """o pet na ilha (coordenadas do plano), com a base em `base`: o Growlmon (o save do antes) ou o Koromon (as telas da trava)"""
    w, h, sw, sh, px, py = SPR[nome]
    c, r = POSE[pose] if nome == "Growlmon" else (0, 0)
    v = " virado" if virado else ""
    img = "" if nome == "Growlmon" else f"background-image:url('{A}/sprites/{nome}.png');"
    return (f'<div class="pet{v}" role="img" aria-label="{nome}" style="{img}left:{cx - w * k / 2:.1f}px;top:{base - h * k:.1f}px;width:{w * k:.1f}px;'
            f'height:{h * k:.1f}px;background-size:{sw * k:.1f}px {sh * k:.1f}px;background-position:{-c * px * k:.1f}px {-r * py * k:.1f}px"></div>')


# ---- a trilha de niveis do Tamer (DECIDIDA: docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, branch v3-progressao, PR #634, P-1 a P-11; secao 3.3).
# O nivel e do Tamer e e a quantidade de marcos (3.2). Lugar trancado (3.4, P-11): visivel desde o Nv 1, apagado, cadeado e "Nv N"; a dica
# (foco/hover e aria-label) diz o marco. Os textos do marco sao da prancha, montados do "marco (gatilho)" da tabela 3.3 e do exemplo da 3.4.
NIVEL = {
    "diario": (2, "Abre com 3 chamados atendidos"),        # 3.3, linha 2: atendeu 3 chamados do In-Training
    "crescer": (3, "Abre quando ele virar Rookie"),         # 3.3, linha 3 (o texto e o exemplo da 3.4)
    "conversar": (3, "Abre quando ele virar Rookie"),       # 3.3, linha 3
    "lutar": (4, "Abre com o primeiro treino"),             # 3.3, linha 4
    "itens": (5, "Abre com a primeira medalha"),            # 3.3, linha 5
    "regras": (6, "Abre quando ele virar Champion"),        # 3.3, linha 6 (P-4: so esconde o editor e o cartao; o motor nao muda)
    "fronteira": (8, "Abre com 6 medalhas"),                # 3.3, linha 8 (a trava de hoje, MEDALHAS_LIGA)
}
# o nivel do save do antes (Growlmon Champion, o Tamer sem medalha), pela contagem de marcos (3.2): chocou (1), atendeu 3 chamados (2:
# "virou Agumon (cuidado 100%)" no historico do antes), virou Rookie (3), o primeiro treino (4: o save tem treino, "o seu pet tem 10"),
# virou Champion (5). A primeira medalha falta (o Tamer tem 0). = 5 marcos = Nv 5. Pergunta: a ordem dos marcos nesse save (ver a secao).
NIVEL_SAVE = 5


def nv(chave: str) -> str:
    """'Nv N' com o cadeado, e o marco no aria-label"""
    n, motivo = NIVEL[chave]
    return f'<span class="nv" role="img" aria-label="trancado: {motivo}">{svg("cadeado", "ic ic-p")}Nv {n}</span>'


def spr(nome: str, k: float, pose: str = "parado") -> str:
    """um sprite dentro de um painel (palco, no da arvore, tile): o quadro 0,0 da folha, ou a pose do Growlmon"""
    w, h, sw, sh, px, py = SPR[nome]
    c, r = POSE[pose] if nome == "Growlmon" else (0, 0)
    return (f'<span class="spr" style="width:{w * k:.1f}px;height:{h * k:.1f}px;background-image:url(\'{A}/sprites/{nome}.png\');'
            f'background-size:{sw * k:.1f}px {sh * k:.1f}px;background-position:{-c * px * k:.1f}px {-r * py * k:.1f}px"></span>')


# ---------------------------------------------------------------------------------------------------- os objetos novos
# (aprovados pelo Matheus em 2026-11-06: entram na ilha 3D como objetos low-poly CC0 do mesmo kit; aqui, o desenho provisorio)
# material = (ax, ay, largura, altura) de um trecho liso do proprio fundo: a parte e esse trecho ampliado (lugares.css, .amostra)
MAT = {
    "pedra": (928, 469, 26, 17),      # a base cinza do saco de pancada
    "madeira": (961, 262, 11, 190),   # o poste do saco (vertical)
    "viga": (980, 236, 55, 8),        # a trave do poste (horizontal)
    "vermelho": (1018, 350, 30, 28),  # o saco, entre as faixas brancas
    "areia": (1190, 660, 110, 38),    # o caminho de terra
    "faixa": (1250, 244, 300, 56),    # as faixas do barranco do fundo (tabuas)
}


def parte(m: str, x: float, y: float, w: float, h: float, clip: str = "", faceta: str = "", op: float = .3, extra: str = "") -> str:
    ax, ay, rw, rh = MAT[m]
    z = max(w / rw, h / rh) * 1.02
    cp = f"clip-path:polygon({clip});" if clip else ""
    fc = f'<i class="faceta" style="clip-path:polygon({faceta});opacity:{op}"></i>' if faceta else ""
    return (f'<div class="amostra objeto" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--ax:{ax};--ay:{ay};--z:{z:.2f};{cp}{extra}">{fc}</div>')


def sombra_chao(x: float, y: float, w: float, h: float, op: float = .5) -> str:
    return f'<div class="sombra" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;opacity:{op};z-index:2"></div>'


def simbolo(m: str, n: str, x: float, y: float, w: float) -> str:
    ax, ay, rw, rh = MAT[m]
    z = max(w / rw, w / rh) * 1.02
    return (f'<div class="amostra objeto simbolo" style="left:{x}px;top:{y}px;width:{w}px;height:{w}px;--ax:{ax};--ay:{ay};--z:{z:.2f};'
            f'--msk:{mascara(n)};z-index:4"></div>')


def apagar(partes: str, sim: bool) -> str:
    """o lugar trancado: o mesmo desenho, apagado (filter, nao e cor)"""
    return f'<div class="apagado" style="left:0;top:0;width:1920px;height:931px">{partes}</div>' if sim else partes


def saco_apagado() -> str:
    """o saco de pancada trancado: ele esta no fundo, entao um recorte do proprio fundo, no mesmo lugar, vai por cima, apagado"""
    # o poste (x 952-975), a trave (y 232-248), o saco (x 1003-1065, y 285-420) e a base (x 918-1018, y 455-495), no recorte de 160 x 272
    # o contorno em px do recorte: a trave, a corda, o saco, o poste e a base (o mesmo desenho do fundo, sem o retangulo de grama)
    clip = ("37px 4px,132px 4px,132px 22px,118px 22px,118px 54px,153px 54px,153px 200px,85px 200px,85px 54px,112px 54px,112px 22px,"
            "60px 22px,60px 229px,103px 229px,103px 271px,3px 271px,3px 229px,37px 229px")
    return (f'<div class="amostra objeto apagado" style="left:915px;top:226px;width:160px;height:272px;--ax:915;--ay:226;--z:1;'
            f'clip-path:polygon({clip})"></div>')


def portao(apagado: bool = False) -> str:
    """o portao da arena (objeto novo): no fim do caminho de terra, a direita, atravessado na trilha; base em y 765"""
    return apagar(_portao(), apagado)


def _portao() -> str:
    return "".join([
        sombra_chao(1462, 748, 276, 34, .45),
        parte("pedra", 1495, 548, 58, 220, "10% 0,90% 0,100% 100%,0 100%", "55% 0,90% 0,100% 100%,58% 100%", .35),
        parte("pedra", 1647, 548, 58, 220, "10% 0,90% 0,100% 100%,0 100%", "55% 0,90% 0,100% 100%,58% 100%", .35),
        parte("pedra", 1489, 536, 70, 16, "0 100%,8% 0,92% 0,100% 100%"),
        parte("pedra", 1641, 536, 70, 16, "0 100%,8% 0,92% 0,100% 100%"),
        parte("viga", 1472, 514, 256, 30, "0 30%,4% 0,96% 0,100% 30%,98% 100%,2% 100%", "2% 62%,98% 62%,98% 100%,2% 100%", .3),
        parte("vermelho", 1482, 482, 236, 34, "6% 100%,0 72%,50% 0,100% 72%,94% 100%", "50% 0,100% 72%,94% 100%,50% 100%", .3),
        parte("vermelho", 1572, 544, 56, 94, "0 0,100% 0,100% 100%,50% 84%,0 100%", "50% 0,100% 0,100% 100%,50% 84%", .25),
        simbolo("areia", "lutar", 1584, 566, 32),
    ])


def barraca(apagada: bool = False) -> str:
    """a barraca do Tamer (objeto novo): a esquerda, encostada no barranco; base em y 700. Apagada = trancada (a trava de progresso)"""
    partes = "".join([
        sombra_chao(92, 682, 380, 36, .45),
        parte("areia", 140, 470, 250, 230, "50% 0,100% 100%,0 100%", "50% 0,100% 100%,50% 100%", .3),
        parte("vermelho", 136, 680, 258, 20, "3% 0,97% 0,100% 100%,0 100%"),
        '<div class="sombra objeto" style="left:232px;top:588px;width:66px;height:94px;border-radius:0;clip-path:polygon(50% 0,100% 100%,0 100%);opacity:.9"></div>',
        parte("madeira", 261, 428, 8, 48),
        parte("vermelho", 269, 430, 50, 28, "0 0,100% 50%,0 100%", "0 50%,100% 50%,0 100%", .25),
        parte("faixa", 404, 640, 62, 58, "", "62% 0,100% 0,100% 100%,62% 100%", .3),
        parte("madeira", 112, 600, 8, 100),
        parte("faixa", 82, 572, 68, 44, "4% 0,96% 0,100% 100%,0 100%", "0 78%,100% 78%,100% 100%,0 100%", .3),
        simbolo("vermelho", "diario", 102, 578, 30),
    ])
    return apagar(partes, apagada)


def brilho(x: float, y: float, w: float, h: float) -> str:
    """o lugar que acabou de abrir brilha uma vez em --hx-alerta (plano 3.4); com reduzir movimento, sem brilho"""
    return f'<div class="brilho" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'


def mundo(cam: str, pets: str, barraca_apagada: bool = False, trancados: tuple = (), extra: str = "") -> str:
    """trancados: os lugares apagados na ilha ("diario" a barraca, "crescer" o saco, "lutar" o portao)"""
    s, ox, oy = CAM[cam]
    tr = set(trancados) | ({"diario"} if barraca_apagada else set())
    return (f'<div class="mundo" style="--s:{s};--ox:{ox};--oy:{oy}" role="img" aria-label="A ilha (o fundo e uma captura real do jogo, de dia)">'
            f'{saco_apagado() if "crescer" in tr else ""}{portao("lutar" in tr)}{barraca("diario" in tr)}{extra}{pets}</div>')


# onde fica o cadeado de cada lugar, nas coordenadas da ilha (o centro do objeto)
CADEADO = {"diario": (265, 560), "crescer": (1035, 340), "lutar": (1600, 620)}


def cadeados(cam: str, quais: tuple, aberto: str = "") -> str:
    out = []
    for q in quais:
        x, y = tela(*CADEADO[q], cam)
        n, motivo = NIVEL[q]
        out.append(f'<span class="caixa cadeado-ilha" style="left:{x:.0f}px;top:{y:.0f}px" tabindex="0" role="img" aria-label="trancado, Nv {n}: {motivo}">'
                   f'{svg("cadeado")}<b>Nv {n}</b></span>')
    if aberto:
        x, y = tela(*CADEADO[aberto], cam)
        out.append(f'<span class="caixa cadeado-ilha aberto" style="left:{x:.0f}px;top:{y:.0f}px" role="img" aria-label="aberto">{svg("aberto")}</span>')
    return "".join(out)


# ---------------------------------------------------------------------------------------------------- a pagina, a HUD e a contagem
# a contagem de palavras: a mesma regra do medir_antes.mjs (o innerText do painel inteiro e a regex abaixo)
CONTA_JS = r'''<script>
addEventListener("load", () => {
  const re = /[\p{L}\p{N}]+(?:[-'’][\p{L}\p{N}]+)*/gu, n = el => (el.innerText.match(re) || []).length;
  document.querySelectorAll("[data-conta]").forEach(e => { const a = document.querySelector(e.dataset.conta);
    e.querySelector("b").textContent = a ? n(a) : "ERRO: sem " + e.dataset.conta; });
  document.querySelectorAll("iframe[data-conta-em]").forEach(f => { const go = () => { const d = f.contentDocument, a = d && d.querySelector(".painel-lugar");
      document.querySelector(f.dataset.contaEm).querySelector("b").textContent = a ? n(a) : "ERRO: o iframe não abriu"; };
    if (f.contentDocument && f.contentDocument.readyState === "complete") go(); else f.addEventListener("load", go); });
});
</script>'''


def cab(titulo: str, cel: bool = False) -> str:
    h = ' class="cel"' if cel else ""
    return f'''<!doctype html><html lang="pt-BR"{h}><head><meta charset="utf-8"><meta name="viewport" content="width={390 if cel else 1920}">
<title>Lugares da ilha · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600;700;800;900&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="lugares.css">
<style>:root{{--assets-spr:url("{A}/sprites/Growlmon.png")}}</style>
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.pele=q.get("pele")==="xcom"?"xcom":"vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
{CONTA_JS}
</head><body{h}>'''


FIM = "</body></html>\n"


def contagem(x: float, y: float, alvo: str = ".painel-lugar", txt: str = "palavras no painel") -> str:
    return f'<span class="contagem so-nota" style="left:{x}px;top:{y}px" data-conta="{alvo}"><b>…</b> {txt}</span>'


def retrato_i(nome: str) -> str:
    """o recorte do retrato: o do lugares.css e o do Growlmon; o Koromon troca a folha e o tamanho"""
    if nome == "Growlmon":
        return "<i></i>"
    w, h, sw, sh, _, _ = SPR[nome]
    return f'<i style="width:{w}px;height:{h}px;background-image:url(\'{A}/sprites/{nome}.png\');background-size:{sw}px {sh}px"></i>'


def topo(leque: bool = False, agora: bool = True, nome: str = "Growlmon", nivel: str = "Champion · Coragem") -> str:
    ag = ('<button type="button" class="caixa agora" aria-label="Agora: explorando. Tempo livre: o instinto faria o mesmo. Abrir o porquê no DigiBrain">'
          '<span class="rot">agora</span><span class="acao">explorando</span></button>') if agora else ""
    exp = "true" if leque else "false"
    return f'''<header class="topo">
  <div class="caixa topo-pet"><button type="button" class="retrato" aria-label="Retrato: Meus pets, DigiBrain, Ajustes e o nível do Tamer" aria-haspopup="menu" aria-expanded="{exp}">{retrato_i(nome)}</button>
    <span class="topo-pet-txt"><b>{nome}</b><small>{nivel}</small></span></div>
  {ag}
  <span class="logo">DIGILAB</span>
  <div class="caixa relogio"><span class="hora"><small>Dia 3</small><b>07:42</b></span><span class="salvo">● salvo</span></div>
</header>'''


# o trilho: Pet volta a ilha (Esc); C, L, D abrem o lugar com corte seco (o atalho direto, PROPOSTO)
TECLA = {"crescer": "C", "lutar": "L", "diario": "D"}


def trilho(atual: str = "pet", clicado: str = "", trancados: tuple = (), novo: str = "") -> str:
    """trancados: o icone fica igual, so apagado (plano 3.4); o nome acessivel diz o marco; a tecla abre o cartao do motivo"""
    bts = []
    for n, r in [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário"), ("conversar", "Conversar")]:
        tr = n in trancados
        cur = ' aria-current="page"' if n == atual else ""
        cl = (" clicado" if n == clicado else "") + (" trancado" if tr else "")
        k = f'<kbd aria-hidden="true">{TECLA[n]}</kbd>' if n in TECLA else ""
        nvo = '<i class="novo-selo" style="left:6px;top:6px" aria-hidden="true"></i>' if n == novo else ""
        lab = (f' aria-disabled="true" aria-label="{r}, trancado, Nv {NIVEL[n][0]}: {NIVEL[n][1]}"' if tr
               else (f' aria-label="{r}, novo"' if n == novo else ""))
        ks = f' aria-keyshortcuts="{TECLA[n]}"' if n in TECLA else (' aria-keyshortcuts="Escape"' if n == "pet" else "")
        bts.append(f'<button type="button" class="nav-bt{cl}"{cur}{ks}{lab}>{nvo}{svg(n)}{r}{k}</button>')
    return f'<nav class="caixa trilho" aria-label="Navegação">{"".join(bts)}</nav>'


def pilha(cls: str = "", evo: str = "Ultimate · 15h 15min") -> str:
    def p(ic: str, tit: str, res: str) -> str:
        return (f'<section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false">{svg(ic)}'
                f'<span class="tit">{tit}<span class="resumo">{res}</span></span><span class="risca"></span></button></section>')
    return (f'<aside class="pilha {cls}" aria-label="Painéis do pet">{p("estado", "Estado atual", "comida 64 % · higiene 40 %")}'
            f'{p("evolucao", "Evolução", evo)}{p("acoes", "Últimas ações", "07:40 · carinho")}</aside>')


def dock(cls: str = "") -> str:
    bs = "".join(f'<button type="button">{a}</button>' for a in ["Alimentar", "Brincar", "Limpar", "Carinho", "Tapa", "Tratar", "Mais"])
    return f'<nav class="caixa dock {cls}" aria-label="Ações">{bs}</nav>'


# ---- o minimapa (contexto): coordenadas do circulo de 216 px
MINI = {"crescer": (111, 83), "lutar": (146, 146), "diario": (47, 113), "fronteira": (180, 96)}
PET_MINI = {"ilha": (125, 63), "saco": (96, 96), "portao": (146, 179), "barraca": (70, 132), "viagem": (112, 78)}


def mapa_svg(px: float, py: float) -> str:
    return f'''<svg class="mapa" viewBox="0 0 216 216" aria-hidden="true">
  <polygon class="ilha" points="30,62 62,30 108,20 160,32 192,64 200,110 188,160 150,194 100,202 56,186 24,150 16,104"/>
  <path class="arv" d="M54 46l7-13 7 13zM84 36l7-13 7 13zM120 34l7-13 7 13zM156 44l7-13 7 13z"/>
  <path class="barranco" d="M20 122 Q36 74 92 56"/>
  <path class="trilha" d="M74 130 L130 120 L146 146 L170 150 Q192 138 182 112"/>
  <ellipse class="coisa" cx="74" cy="130" rx="11" ry="6"/><circle class="coisa" cx="130" cy="118" r="5"/>
  <circle class="pet-ponto" cx="{px}" cy="{py}" r="6"/>
</svg>'''


def mini_bts(atual: str = "", trancados: tuple = (), novo: str = "", esc: float = 1) -> str:
    """os lugares do minimapa (botoes de 44 px); trancado: apagado, tracejado, cadeado e "Nv N"; a Fronteira no Nv 8 (plano 3.3)"""
    def bt(n: str, ic: str, rot: str) -> str:
        x, y = MINI[n]
        x, y = x * esc, y * esc
        if n in trancados or n == "fronteira":
            k = n
            return (f'<button type="button" class="mini-bt trancado" style="left:{x:.0f}px;top:{y:.0f}px" aria-disabled="true" '
                    f'aria-label="{rot}, trancado, Nv {NIVEL[k][0]}: {NIVEL[k][1]}">{svg(ic)}<span class="mini-nv">Nv {NIVEL[k][0]}</span></button>')
        cur = ' aria-current="true"' if n == atual else ""
        nvo = '<i class="novo-selo" style="right:-2px;top:-2px" aria-hidden="true"></i>' if n == novo else ""
        return f'<button type="button" class="mini-bt" style="left:{x:.0f}px;top:{y:.0f}px" aria-label="{rot}"{cur}>{svg(ic)}{nvo}</button>'
    return (bt("crescer", "saco", "Saco de pancada: Crescer") + bt("lutar", "portao", "Portão da arena: Lutar")
            + bt("diario", "barraca", "Barraca do Tamer: Diário") + bt("fronteira", "fronteira", "Fronteira"))


def minimapa(atual: str = "", pet_em: str = "ilha", trancados: tuple = (), novo: str = "") -> str:
    px, py = PET_MINI[pet_em]
    return (f'<nav class="mini" aria-label="Minimapa: clicar num lugar abre o menu dele">{mapa_svg(px, py)}'
            f'{mini_bts(atual, trancados, novo)}<span class="mini-rot">ilha</span></nav>')


def nota(txt: str, x: float, y: float, w: int = 300) -> str:
    return f'<span class="nota" style="left:{x}px;top:{y}px;max-width:{w}px">{txt}</span>'


def placa(ic: str, nome: str, x: float, y: float, cls: str = "", extra: str = "") -> str:
    return f'<span class="caixa placa-lugar {cls}" style="left:{x}px;top:{y}px">{svg(ic)}{nome}{extra}</span>'


def conector(d: str, cx: float, cy: float) -> str:
    return f'<svg class="conector" viewBox="0 0 1920 950" aria-hidden="true"><path d="{d}"/><circle cx="{cx}" cy="{cy}" r="4"/></svg>'


# ---------------------------------------------------------------------------------------------------- o painel do lugar (1920) e a folha (390)
ABAS = {
    "crescer": [("treinar", "Treinar"), ("aprend", "Aprendizado"), ("evolucao", "Evolução"), ("itens", "Itens")],
    "lutar": [("arena", "Arena"), ("exploracao", "Exploração"), ("fronteira", "Fronteira"), ("medalhas", "Medalhas")],
    "diario": [("registro", "Registro"), ("catalogo", "Catálogo"), ("geracoes", "Gerações"), ("cenarios", "Cenários")],
}
NOME_DEST = {"crescer": "Crescer", "lutar": "Lutar", "diario": "Diário"}
LUGAR = {"crescer": "saco de pancada", "lutar": "portão da arena", "diario": "barraca do Tamer"}


def abas(dest: str, ativa: str, foco: str = "", marcas: tuple = (), dica_foco: str = "") -> str:
    out = []
    for i, (n, rot) in enumerate(ABAS[dest], 1):
        sel = n == ativa
        tranc = dest == "lutar" and n == "fronteira"
        cls = "aba" + (" trancada" if tranc else "") + (" foco" if n == foco else "")
        lab = f"{rot}, trancada, Nv {NIVEL['fronteira'][0]}: {NIVEL['fronteira'][1]}" if tranc else rot
        conteudo = svg(n) + (rot if sel else "")
        if n in marcas:
            conteudo += '<i class="marca" aria-hidden="true"></i>'
        if tranc:
            conteudo += f'<span class="aba-nv" aria-hidden="true">Nv {NIVEL["fronteira"][0]}</span>'
        if n == foco:
            sub = f"<small>{dica_foco}</small>" if dica_foco else ""
            conteudo += f'<span class="caixa dica" role="tooltip">{rot}{sub}</span>'
        dis = ' aria-disabled="true"' if tranc else ""
        out.append(f'<button type="button" role="tab" class="{cls}" aria-selected="{"true" if sel else "false"}" aria-label="{lab}" '
                   f'aria-keyshortcuts="{i}" title="{lab}"{dis}>{conteudo}</button>')
    return f'<div class="abas" role="tablist" aria-label="Abas de {NOME_DEST[dest]}">{"".join(out)}</div>'


def painel(dest: str, ativa: str, corpo: str, x: float, y: float, w: float, foco: str = "", marcas: tuple = (), dica_foco: str = "") -> str:
    return f'''<section class="caixa lp painel-lugar" style="left:{x}px;top:{y}px;width:{w}px" aria-labelledby="lp-tit">
  <div class="lp-cab">{svg(dest)}<span class="lp-tit"><b id="lp-tit">{NOME_DEST[dest]}</b><small>{LUGAR[dest]}</small></span>
    <button type="button" class="bt-ic" aria-label="Voltar à ilha" aria-keyshortcuts="Escape">{svg("x")}</button></div>
  {abas(dest, ativa, foco, marcas, dica_foco)}
  <div class="lp-corpo" role="tabpanel">{corpo}</div>
</section>'''


def folha(dest: str, ativa: str, corpo: str, foco: str = "", dica: str = "") -> str:
    """a folha do celular (rodada 3): sobe da base e cobre so a parte de baixo; em cima ficam o lugar e o pet. Volta pelo x ("Fechar e
    voltar ao Pet"), pelo Esc ou pelo toque fora (M1). Substitui a faixa no topo da rodada 2. A altura (top 400 a 390 x 844) e PROPOSTA,
    SEM FONTE. Com dest="ajustes" nao ha abas."""
    nome = NOME_DEST.get(dest, "Ajustes")
    lugar = f"<small>{LUGAR[dest]}</small>" if dest in LUGAR else ""
    ab = abas(dest, ativa, foco, (), dica) if dest in ABAS else ""
    return f'''<section class="caixa folha painel-lugar" role="dialog" aria-modal="true" aria-labelledby="fo-tit">
  <span class="alca" aria-hidden="true"></span>
  <div class="lp-cab">{svg(dest)}<span class="lp-tit"><b id="fo-tit">{nome}</b>{lugar}</span>
    <button type="button" class="bt-ic" aria-label="Fechar e voltar ao Pet" aria-keyshortcuts="Escape">{svg("x")}</button></div>
  {ab}
  <div class="lp-corpo" role="tabpanel">{corpo}</div>
</section>'''


def como(txt: str, aberto: bool = False) -> str:
    a = " open" if aberto else ""
    return f'<details class="como"{a}><summary>{svg("info")}Como funciona{svg("seta")}</summary><p>{txt}</p></details>'


def fechado(ic: str, tit: str, balao: str = "") -> str:
    return f'<button type="button" class="fechado" aria-expanded="false">{svg(ic)}<span>{tit}</span>{svg("seta")}{b(balao) if balao else ""}</button>'


def med(rot: str, v: float, marcas: list) -> str:
    lim = "".join(f'<span class="lim" style="left:{m}%"></span>' for m, _ in marcas)
    mk = "".join(f'<span style="left:{m}%">{m}</span>' for m, _ in marcas)
    al = "; ".join(f"{m}: {t}" for m, t in marcas)
    return (f'<div class="med"><span class="rot">{rot}</span><span class="barra" role="img" aria-label="{rot} {v:.0f} de 100; marcas {al}">'
            f'<i style="--v:{v}%"></i>{lim}</span><em>{v:.0f}</em><span class="marcas" aria-hidden="true">{mk}</span></div>')


def selo(n: int, cls: str, rot: str, balao: str) -> str:
    return f'<span class="selo {cls}" tabindex="0" role="img" aria-label="{rot}"><i>{n}</i>{b(balao)}</span>'


# ---------------------------------------------------------------------------------------------------- Crescer · Itens (NOVA)
# os 6 chips e as 3 cartas de motor/itens.ts, com o efeito encurtado (o inteiro vai para o balao) e o lugar de onde vem (TelaItens.tsx
# deOnde e comoGanhar); o nivel do chip de regra e o "pede um Champion/Ultimate" do antes (estagioMinimo). O Tamer sem medalha (o save do
# antes): 0 chips, 0 cartas e as 3 vagas trancadas (CIT.vagas: 1 vaga com 1 medalha, 2 com 3, 3 com 5).
CHIPS = [
    ("chip_stat", "Força", "Chip de Força", "+1 força +1 vigor", "",
     "+1 de força e +1 de vigor, como treino: só ocupa o espaço de treino que ainda falta no estágio.", "vença o Gazimon na Campina", False),
    ("chip_stat", "Guarda", "Chip de Guarda", "+1 guarda +1 recuperação", "",
     "+1 de guarda e +1 de recuperação, como treino: só ocupa o espaço de treino que ainda falta no estágio.", "vença o Myotismon três vezes seguidas na Cidadela", False),
    ("chip_regra", "Recuo", "Chip Recuo", "pesado → recuar", "Champion",
     "Regra nova: quando o rival prepara o golpe pesado, recuar (o pesado erra de longe, sem gastar guts).", "vença o Guardromon na Torre de pedra", True),
    ("chip_regra", "Oportunista", "Chip Oportunista", "guts &lt; 20 → pesado", "Champion",
     "Regra nova: de perto, com o rival sem fôlego (guts &lt; 20), preparar o golpe pesado.", "vença o Youkomon na Floresta", False),
    ("chip_regra", "Perseguidor", "Chip Perseguidor", "disparo → avançar", "Ultimate",
     "Regra nova: contra quem insiste em atirar de longe, avançar.", "vença o MarinBullmon no Lago", False),
    ("chip_regra", "Aparo", "Chip Aparo", "golpe rápido → defender", "Ultimate",
     "Regra nova: contra quem insiste no golpe rápido, defender (o aparo devolve dano).", "vença o Piedmon na Montanha Espiral", False),
]
CARTAS = [
    ("Fôlego", "Carta de Fôlego", "+20 guts", "+20 de guts no começo da luta (até o máximo).", "o Gazimon na Campina ou o Youkomon na Floresta"),
    ("Cura", "Carta de Cura", "&lt; 30% → +20%", "Na primeira vez que a vida cai abaixo de 30%, cura 20% da vida máxima.", "o Myotismon na Cidadela ou o Piedmon na Montanha Espiral"),
    ("Foco", "Carta de Foco", "não se distrai", "O pet não se distrai: segue as próprias regras a luta inteira.", "o Guardromon na Torre de pedra ou o MarinBullmon no Lago"),
]


def corpo_itens() -> str:
    slots = "".join(f'<span class="slot trancada" role="img" aria-label="vaga {i}: abre com {m} medalha{"s" if m > 1 else ""}">{svg("cadeado")}<small>{m}</small></span>'
                    for i, m in [(1, 1), (2, 3), (3, 5)])
    topo_ = f'''<div class="itens-topo">
  <span class="conta-ic" role="img" aria-label="0 chips">{svg("chip")}<b class="num-g">0</b><small>chips</small></span>
  <span class="conta-ic" role="img" aria-label="0 cartas">{svg("carta")}<b class="num-g">0</b><small>cartas</small></span>
  <span class="aviso-it" tabindex="0" aria-label="Os itens ainda não fazem efeito: pedem treino">{svg("alerta")}treino <b>10/11</b>{b("Agora os itens não fazem efeito: os itens pedem treino: pelo menos 11 pontos neste nível (o seu pet tem 10).")}</span>
  <span class="vagas" role="group" aria-label="Vagas de chip do Growlmon: nenhuma aberta">{slots}<small>vagas</small></span></div>'''
    chips = []
    for i, (tipo, curto, nome, ef, nivel, frase, onde, coberto) in enumerate(CHIPS):
        canto = (f'<span class="etq">{nivel}</span>' if nivel else "") + (svg("coberto") if coberto else "") + svg("cadeado")
        prox = " proximo" if i == 0 else ""
        cob = " Este chip fica coberto: a regra “se oponente preparando pesado → esquivar” do pet vale sempre que ele valeria e vem antes." if coberto else ""
        chips.append(f'<button type="button" class="item falta{prox}" aria-label="{nome}, ainda não é seu">{svg(tipo)}<b>{curto}</b><small>{ef}</small>'
                     f'<span class="canto">{canto}</span>{b(f"<b>{nome}</b>: {frase}{cob} Ainda não é seu: {onde}.")}</button>')
    cartas = "".join(
        f'<button type="button" class="item falta" aria-label="{nome}, nenhuma">{svg("carta")}<b>{curto}</b><small>{ef}</small>'
        f'<span class="canto"><span class="qtd">×0</span></span>{b(f"<b>{nome}</b>: {frase} Vem da revanche vencida contra {de}.")}</button>'
        for curto, nome, ef, frase, de in CARTAS)
    return f'''{topo_}
<span class="rot">Chips</span>
<div class="item-grade" role="list">{"".join(chips)}</div>
<span class="rot">Cartas</span>
<div class="item-grade" role="list">{cartas}</div>
{como("Os itens são seus, como as medalhas: o líder de cada arena dá um item na primeira vitória, e a revanche vencida dá uma carta. O chip não se gasta; a carta vale uma luta só. Vagas de chip: 1 com 1 medalha, 2 com 3 e 3 com 5. Os itens pedem treino: com menos da metade do treino típico do nível, não fazem efeito. O chip de regra entra no fim da lista de combate; a carta só vale na Exploração.")}'''


# ---------------------------------------------------------------------------------------------------- Crescer · Evolucao (REFEITA)
# o que importa: a forma atual, o tempo, o que o nivel pede (CMD.adulto = 3 medalhas, as 3 que o Tamer ainda nao tem pela ordem de
# MEDALHAS: Campina, Torre de pedra, Floresta; e as 10 lutas de treino, CAT.sparring, com 80% de vitorias, CLE.limiarTaxa) e a arvore.
MED_FALTA = [(1, "Medalha da Campina", "vença o Gazimon na Campina"), (2, "Medalha da Torre de pedra", "vença o Guardromon na Torre de pedra"),
             (3, "Medalha da Floresta", "vença o Youkomon na Floresta")]


def no_spr(nome: str, cls: str, k: float, rot: str) -> str:
    v = svg("check", "ic v") if cls == "ok" else ""
    return f'<button type="button" class="n {cls}" aria-label="{rot}">{spr(nome, k)}{v}</button>'


def no_q(cls: str, rot: str, balao: str = "") -> str:
    return f'<button type="button" class="n {cls}" aria-label="{rot}">?{b(balao) if balao else ""}</button>'


def corpo_evolucao() -> str:
    selos = "".join(selo(n, "falta", f"{nm}, falta", f"<b>{nm}</b>: {onde}.") for n, nm, onde in MED_FALTA)
    fila = lambda rot, nos: f'<div class="fila"><span class="rot">{rot}</span><div class="nos">{nos}</div></div>'
    return f'''
<div class="evo-topo">
  <div class="palco" aria-hidden="true"><span class="disco"></span><span style="position:absolute;left:50%;bottom:4px;transform:translateX(-50%)">{spr("Growlmon", 1.15)}</span></div>
  <div class="evo-nome"><b class="nome">Growlmon</b><div class="linha"><span class="etq">Champion</span><span class="linha" style="gap:4px">{svg("brasao", "ic ic-p")}Coragem</span></div></div>
  <div class="prazo2"><span class="linha">{svg("relogio")}<b class="num-g">15h 15min</b></span><small class="sec">até Ultimate</small></div>
</div>
<div class="destaque reqs" role="group" aria-label="O que a evolução para Ultimate pede">
  <span class="req"><span class="selos">{selos}</span><small>medalhas</small><b class="num-g" style="font-size:18px">0/3</b></span>
  <span class="req" tabindex="0" aria-label="lutas de treino: 0 de 10">{svg("lutar")}<b class="num-g" style="font-size:18px">0/10</b><small>lutas</small>{b("Lutas de treino na Arena: 10 para virar Ultimate, com 80% ou mais de vitórias.")}</span>
</div>
<div class="arv2" role="group" aria-label="Árvore de Coragem">
  {fila("In-Training", no_spr("Koromon", "ok", .42, "Koromon, percorrido"))}
  {fila("Rookie", no_spr("Agumon", "ok", .48, "Agumon, percorrido") + no_q("fechado", "forma não decidida, fechada"))}
  {fila("Champion", no_q("fechado", "fechada") + no_q("fechado", "fechada") + no_q("fechado", "fechada") + no_spr("Growlmon", "agora", .44, "Growlmon, agora"))}
  {fila("Ultimate", no_q("possivel", "Ultimate, arquétipo Vigia, possível", "<b>Vigia</b>: um dos dois arquétipos do Ultimate da linha; o eixo complementar decide.")
        + no_q("possivel", "Ultimate, arquétipo Titã, possível", "<b>Titã</b>: o outro arquétipo do Ultimate da linha.")
        + no_q("sombria", "forma sombria da linha", "<b>Sombria</b>: sobrecarga alta na virada para Ultimate."))}
  {fila("Mega", no_q("possivel", "Mega, possível"))}
</div>
<div class="bts-linha">{fechado("historico", "Histórico", "nasceu Koromon; virou Agumon; virou Growlmon")}{fechado("info", "Porquê", "decidido pelo caráter resistente, o eixo mais alto ao fim do Rookie")}</div>
{como("Cada evolução é decidida pelo que o pet viveu: cuidado, caráter e lutas de treino. Champion → Ultimate: o tempo do Champion, 10 lutas de treino com 80% ou mais de vitórias e 3 medalhas do Tamer. Na árvore: o verde é o caminho, o claro é agora, o tracejado é possível, o pontilhado é fechado e o listrado é a sombria.")}'''


# ---- as pecas do Nv 6 (plano 3.3, linha 6; P-4: so esconder o editor e o cartao ate o Nv 6, sem tocar no motor). O save do antes esta no
# Nv 5 pela conta de marcos (NIVEL_SAVE), entao o Forcar e o cartao das regras aparecem trancados, com "Nv 6"
def trancado_bt(ic: str, rot: str, chave: str) -> str:
    n, motivo = NIVEL[chave]
    return (f'<button type="button" class="fechado trancado" aria-disabled="true" aria-label="{rot}, trancado, Nv {n}: {motivo}">{svg(ic)}<span>{rot}</span>'
            f'<span class="nv">{svg("cadeado", "ic ic-p")}Nv {n}</span>{b(motivo + ".")}</button>')


def forcar() -> str:
    if NIVEL_SAVE >= NIVEL["regras"][0]:
        return (f'<button type="button" class="bt forcar" disabled aria-label="Forçar: abre com fadiga 60">Forçar</button>'
                f'{b("Abre com fadiga 60: rende mais, mas gera sobrecarga.")}')
    return f'<span style="width:180px">{trancado_bt("treinar", "Forçar", "regras")}</span>'


def regras_bt() -> str:
    if NIVEL_SAVE >= NIVEL["regras"][0]:
        return fechado("digibrain", "Regras", "As regras de combate do seu pet: ele as aprende lutando; você pode travar ou vetar.")
    return trancado_bt("digibrain", "Regras", "regras")


# ---------------------------------------------------------------------------------------------------- Crescer · Treinar
def corpo_treinar() -> str:
    # CTR.exercicios (pri, sec), ganhoPri 2, ganhoSec 1; a aptidao do Coragem (APTIDAO.brasa: forca 1,2, guarda 1,1): a estrela em Levantar
    # pedra (forca) e Esquiva (guarda), como o selo de TelaTreinar.tsx (apt[pri] > 1)
    ex = [("levantar_pedra", "Levantar pedra", "força", "vigor", True), ("corrida", "Corrida", "fôlego", "recuperação", False),
          ("alvo", "Alvo", "mira", "fôlego", False), ("esquiva", "Esquiva", "guarda", "vigor", True),
          ("meditar", "Meditar", "recuperação", "guarda", False), ("resistencia", "Resistência", "vigor", "força", False)]
    grade = "".join(
        f'<button type="button" class="ex" aria-label="Treinar {n}{": aptidão" if apt else ""}">{svg(k)}<b>{n}</b><small>+2 {p} +1 {s}</small>'
        + (f'<span class="etq alerta" style="padding:1px 3px">{svg("estrela", "ic ic-p")}</span>' if apt else "") + "</button>" for k, n, p, s, apt in ex)
    return f'''
<div class="destaque linha" role="status">{svg("check")}<b class="grande" style="margin:0">Pronto</b>
  <span class="sec linha" style="margin-left:auto;gap:6px" tabindex="0">{svg("replay", "ic ic-p")}Corrida 07:31{b("Um treino por vez, com 10 min de intervalo.")}</span></div>
<div class="ex-grade" role="group" aria-label="Exercícios">{grade}</div>
<div class="cartao" style="display:flex;flex-direction:column;gap:6px">
  {med("Fadiga", 20, [(40, "pede pausa"), (60, "só forçar")])}
  {med("Sobrecarga", 0, [(30, "aviso"), (60, "sombria")])}</div>
<div class="linha">{forcar()}
  <span class="sec" style="margin-left:auto">estágio <b class="num" style="--n:15px">10/12</b></span></div>
{como("Um toque por sessão, com pelo menos 10 min entre elas. Cada exercício sobe um stat principal e um secundário; a estrela é a aptidão do brasão (Coragem rende 1,2× em força e 1,1× em guarda). Com fadiga 40 ele pede pausa; com 60 o botão vira Forçar: rende mais, mas gera sobrecarga.")}'''


# ---------------------------------------------------------------------------------------------------- Lutar
def corpo_arena() -> str:
    # os bots (luta.ts RIVAIS_CLASSICOS; nomesRivais.ts DIGIMON_BOT; NOME_BOT; o oraculo e "referência"); o escolhido e exemplo.
    # "5 regras": o Champion tem 5 (o "Como funciona" da Arena); "lutas 0/10": sparringTexto (luta.ts), CAT.sparring
    bots = [("Kuramon", "aleatório"), ("Monochromon", "agressivo"), ("Golemon", "tartaruga"), ("Tankmon", "atirador"),
            ("Leomon", "contragolpe"), ("Devimon", "adaptativo"), ("Jijimon", "referência")]
    riv = "".join(f'<button type="button" class="rival" role="radio" aria-checked="{"true" if n == "Monochromon" else "false"}"><span class="radio" aria-hidden="true"></span>'
                  f'<span><b>{n}</b><small>{e}</small></span></button>' for n, e in bots)
    return f'''
<div class="linha"><span class="palco" style="width:76px;height:60px" aria-hidden="true"><span style="position:absolute;left:50%;bottom:0;transform:translateX(-50%)">{spr("Growlmon", .72)}</span></span>
  <b style="font:700 18px/1.1 var(--hx-f)">Growlmon</b><span class="etq">Champion</span>
  <span class="chip-apr" style="margin-left:auto">{svg("digibrain", "ic ic-p")}5 regras</span></div>
<div class="destaque linha" role="status" tabindex="0">{svg("lutar")}<b class="num-g">0/10</b><span>lutas de treino</span><span class="etq" style="margin-left:auto">Ultimate</span>
  {b("As lutas de treino da Arena contam para virar Ultimate: 10, com 80% ou mais de vitórias.")}</div>
<div class="rivais" role="radiogroup" aria-label="Rival">{riv}<button type="button" class="rival" aria-expanded="false" aria-label="Mostrar as 8 formas adultas"><span class="radio" style="border-style:dashed" aria-hidden="true"></span><span><b>+8</b><small>adultos</small></span></button></div>
<div class="lutar-linha"><button type="button" class="bt acao grande">{svg("lutar")}Lutar</button><button type="button" class="bt">Melhor de 10</button></div>
<div class="bts-linha">{regras_bt()}
  <button type="button" class="fechado" aria-label="Medalha da Campina: vença o Gazimon na Campina, na Exploração">{svg("medalhas")}<span>Campina</span>{svg("seta")}</button></div>
{como("Lute contra um rival. Seu pet decide por regras de combate que ele mesmo aprende lutando; você pode travar ou vetar regras. A campanha contra os NPCs, com as medalhas, fica na aba Exploração.")}'''


def corpo_medalhas() -> str:
    # MEDALHAS (medalhas.ts), os lideres (bots.ts), a regra (arenas.ts), o item e a carta (itens.ts), o que libera (CMD; TelaMedalhas.tsx
    # libera(): a 6a, a Fronteira). O Tamer com 0 medalhas (o save do antes).
    outras = [(2, "Torre de pedra", "Guardromon", ""), (3, "Floresta", "Youkomon", "Ultimate"), (4, "Cidadela", "Myotismon, três vezes seguidas", ""),
              (5, "Lago", "MarinBullmon", "Mega"), (6, "Montanha Espiral", "Piedmon", "Fronteira")]
    li = "".join(f'<button type="button" class="med-li" aria-label="Medalha {"do" if lugar == "Lago" else "da"} {lugar}: vença o {lider}">'
                 f'<span class="selo falta" aria-hidden="true"><i>{n}</i></span><span><b>{lugar}</b></span>'
                 + (f'<span class="etq">{lib}</span>' if lib else "<span></span>") + "</button>" for n, lugar, lider, lib in outras)
    return f'''
<div class="med-cab"><span><span class="num">0/6</span></span>
  <ul class="libera" aria-label="O que as medalhas liberam"><li><b>1</b>Champion</li><li><b>3</b>Ultimate</li><li><b>5</b>Mega</li></ul></div>
<div class="destaque" role="status">
  <div class="lider">
    <span class="lider-spr" role="img" aria-label="Gazimon, líder da Campina"><i></i></span>
    <span><span class="linha"><span class="selo proxima" aria-hidden="true"><i>1</i></span><b class="grande" style="margin:0">Campina</b></span>
      <span class="linha" style="margin-top:8px;gap:6px;flex-wrap:wrap"><span class="etq">{svg("chip_stat", "ic ic-p")}Força</span><span class="etq">{svg("carta", "ic ic-p")}Fôlego</span></span>
      <span class="linha" style="margin-top:8px"><button type="button" class="bt acao">{svg("exploracao")}Exploração</button></span></span></div>
  {b("Vença o Gazimon na Campina. O básico: sem regra especial, vence o pet bem cuidado e treinado. Dá o Chip de Força; a revanche dá a Carta de Fôlego.")}</div>
<div class="med-lista" aria-label="As outras medalhas">{li}</div>
<div class="med-li" style="cursor:default" aria-label="Medalha de ouro: com as 6 medalhas, vença a Liga dos Líderes na Fronteira"><span class="selo ouro" aria-hidden="true" style="opacity:.6"><i>★</i></span>
  <span><b>Liga</b></span><span class="sec">{svg("cadeado")}</span></div>
{como("As medalhas são suas, não do pet: ficam quando ele é guardado ou morre, e valem para todos os pets seguintes. Vença o líder de cada lugar da campanha para ganhar a dele, com um item. Com as 6, a Liga dos Líderes abre na Fronteira.")}'''


# ---------------------------------------------------------------------------------------------------- Diario
def corpo_registro() -> str:
    # as linhas: o _hist do motor (motor.ts) e NOME_PET; o tipo (TelaRegistro.tsx TIPO_REG) vira icone, com o nome no aria-label;
    # "regras" e o aprendido (tracejado ciano). Horas, semente e eventos: exemplo.
    tipos = {"você": "mao", "treino": "treinar", "pet": "pet", "regras": "digibrain"}
    linhas = [("D3 07:40", "você", "carinho"), ("D3 07:31", "treino", "treinou corrida"), ("D3 07:24", "pet", "brincando"),
              ("D3 07:18", "regras", "travou uma regra"), ("D3 07:15", "você", "alimentar"), ("D3 07:02", "pet", "explorando"),
              ("D2 22:10", "pet", "dormindo")]
    ls = "".join(f'<button type="button" class="reg-l" style="grid-template-columns:86px 28px 1fr 20px"><span class="t">{t}</span>'
                 f'<span class="{"chip-apr" if e == "regras" else ""}" role="img" aria-label="{e}" style="{"padding:2px" if e == "regras" else ""}">{svg(tipos[e], "ic ic-p")}</span>'
                 f'<span>{x}</span>{svg("seta", "ic seta")}</button>' for t, e, x in linhas)
    filtros = "".join(f'<button type="button" class="filtro" aria-pressed="{"true" if f == "tudo" else "false"}">{f}</button>'
                      for f in ["tudo", "você", "pet", "lutas", "recusas", "treino"])
    return f'''
<div class="destaque reg-topo"><span class="par"><span class="rot">semente</span><span class="num">7000</span></span>
  <span class="par"><span class="rot">eventos</span><span class="num">76</span></span>
  <span class="linha" style="margin-left:auto"><button type="button" class="bt acao" aria-label="Verificar replay">{svg("replay")}Verificar</button>
    <button type="button" class="bt" aria-label="Copiar registro">{svg("copiar")}Copiar</button></span></div>
<div class="filtros" role="group" aria-label="Filtrar o registro">{filtros}</div>
<div class="reg" aria-label="O registro, do mais novo ao mais velho">{ls}</div>
{como("O estado do pet nunca é salvo. Só este registro, e a vida é reconstruída a partir dele. Verificar refaz o pet a partir dos eventos e confere se sai o mesmo, até o último decimal.", aberto=True)}
{fechado("x", "Novo ovo", "Um ovo novo apaga este pet e o registro dele. Não dá para desfazer.")}'''


def corpo_catalogo() -> str:
    # formasDoBrasao (TelaCatalogo.tsx): 19 formas; o Coragem em nomes.ts. Vistas = o caminho deste pet: Koromon, Agumon e Growlmon = 3 de 19.
    # As nao vistas: so a silhueta (no jogo, a do atlas); o nome vai para o aria-label e o balao.
    def t(nome: str, sub: str = "", visto: str = "", meu: bool = False) -> str:
        cls = "tile" + (" visto" if visto else " nao-visto") + (" meu" if meu else "")
        cx = spr(visto, .42 if visto != "Koromon" else .36) if visto else '<span class="sil" aria-hidden="true"></span>'
        lab = nome + (f" · {sub}" if sub else "") + ("" if visto else ", ainda não vista") + (", seu pet" if meu else "")
        nm = f'<span class="nm">{nome}</span>' if visto else ""
        return f'<button type="button" role="option" class="{cls}" aria-label="{lab}"><span class="cx">{cx}</span>{nm}</button>'

    def nivel(rot: str, tiles: str) -> str:
        return f'<div class="cat-nivel"><span class="rot">{rot}</span><div class="cat-grade">{tiles}</div></div>'
    ult = "".join(t(n, a) for n, a in [("MetalGreymon", "Duelista"), ("MetalGreymon", "Furioso"), ("Taomon", "Espelho"), ("Taomon", "Muralha"),
                                       ("Garudamon", "Sentinela"), ("Garudamon", "Emboscador"), ("WarGrowlmon", "Vigia"), ("WarGrowlmon", "Titã")])
    brs = "".join(f'<button type="button" class="brasao" aria-pressed="{"true" if x == "Coragem" else "false"}">{svg("brasao")}{x}</button>'
                  for x in ["Coragem", "Amizade", "Conhecimento", "Sinceridade"])
    return f'''
<div class="brasoes" role="group" aria-label="Brasão">{brs}</div>
<div class="destaque linha" role="status"><span class="num">3/19</span><span>vistas</span></div>
<div role="listbox" aria-label="Formas do brasão" style="display:flex;flex-direction:column;gap:8px">
{nivel("In-Training · Rookie", t("Koromon", visto="Koromon") + t("Agumon", visto="Agumon") + t("Guilmon"))}
{nivel("Champion", t("Greymon") + t("Kyubimon") + t("Birdramon") + t("Growlmon", visto="Growlmon", meu=True))}
{nivel("Ultimate", ult)}
{nivel("Mega", "".join(t(n) for n in ["WarGreymon", "Sakuyamon", "Phoenixmon", "Gallantmon"]))}
</div>
{fechado("lutar", "Técnicas", "As 4 técnicas (Champion) e as 8 passivas (Ultimate e Mega).")}
{como("Vista = forma por onde este pet passou. Cada brasão percorre a mesma árvore: 1 In-Training, 2 Rookies, 4 Champions, 4 Ultimates e 4 Megas. Toque numa forma para ver a ficha: os 6 stats, vida, guts, técnica e passiva.")}'''


# ---------------------------------------------------------------------------------------------------- Ajustes (nao e lugar)
def corpo_ajustes() -> str:
    def aj(ic: str, tit: str, res: str, dir_: str = "", cls: str = "") -> str:
        d = dir_ or svg("seta")
        return f'<button type="button" class="aj {cls}" aria-label="{tit}: {res}">{svg(ic)}<span><b>{tit}</b></span>{d}{b(res)}</button>'
    sw = lambda on: f'<span class="interruptor{" on" if on else ""}" role="switch" aria-checked="{"true" if on else "false"}"></span>'
    return f'''
{aj("olho", "Visual", "pele, tema do habitat, mapa e câmera")}
{aj("dica", "Dicas", "o Professor Agumon explica cada coisa nova, uma vez", sw(False))}
{aj("estado", "Detalhes do pet", "os painéis Estado atual, Evolução e Últimas ações", sw(True))}
{aj("camera", "Viagem da câmera", "NOVO: desligada, os lugares abrem num corte seco", sw(True), "novo")}
{aj("conversar", "Fala", "modo frases prontas")}
{aj("som", "Som", "golpes, impactos e o efeito da evolução", sw(False))}
{aj("registro", "Registro", "semente, eventos, verificar replay, exportar")}
{aj("acoes", "Tempo", "acelera o relógio do pet", '<span class="etq alerta">teste</span>')}
{aj("frasco", "Laboratório", "o pet de teste com o DigiBrain modular", '<span class="etq alerta">experimental</span>')}
{aj("info", "Sobre", "versão, créditos e procedência")}'''


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def transicao_1() -> str:
    """quadro a: a ilha normal, com a HUD, e o clique em Crescer (ou no lugar do minimapa)"""
    return (cab("abrir um lugar, quadro 1") + mundo("ilha", pet(1160, 400, "parado")) + topo() + trilho("pet", "crescer") + pilha() + dock() + minimapa()
            + '<svg class="cursor" style="left:62px;top:182px" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 2l17 9-7 2-3 7z"/></svg>'
            + nota("1 · a ilha de hoje. Clique em Crescer (ou tecla C, ou o saco no minimapa): a câmera vai ao saco", 100, 166, 260)
            + nota("portão da arena e barraca do Tamer: aprovados para a ilha 3D (kit CC0); aqui, desenho provisório", 1340, 420, 300)
            + nota("o minimapa (de outra sessão; aqui só contexto) no lugar do botão DigiBrain, que vai ao leque do retrato", 1440, 650, 230)
            + nota("a Fronteira trancada: apagada, tracejada, cadeado (abre com as 6 medalhas, MapaExploracao.tsx)", 1380, 836, 290)
            + nota("Ajustes sai do trilho: vai ao leque do retrato", 100, 392, 220)
            + FIM)


def transicao_2() -> str:
    """quadro b: a camera a caminho, o pet andando, a HUD recolhendo"""
    x, y = tela(1000, 270, "viagem")
    return (cab("abrir um lugar, quadro 2") + mundo("viagem", pet(1135, 470, "andando", virado=True)) + topo() + trilho("crescer")
            + pilha("saindo-dir") + dock("saindo-baixo") + minimapa("crescer", "viagem")
            + placa("saco", "Saco de pancada", x, y - 70, "chegando")
            + f'<span class="caixa pular" role="status" aria-label="Indo ao saco de pancada. Esc ou clique para pular">{svg("seta")}<kbd>Esc</kbd></span>'
            + nota("2 · a câmera a caminho: 700 ms (PROPOSTO, SEM FONTE); o pet anda até o saco (só vista, nada entra no registro). Esc ou clique pulam", 100, 410, 300)
            + nota("a pilha e o dock recolhem; o topo, o trilho e o minimapa ficam", 1500, 330, 260)
            + nota("reduzir movimento: corte seco para o quadro 3 (UI_GUIDELINES 11)", 640, 820, 320)
            + FIM)


def _crescer(ativa: str, corpo: str, notas: str, titulo: str, pose: str = "parado", foco: str = "", dica: str = "", extra: str = "") -> str:
    px, py = tela(1035, 285, "saco")
    return (cab(titulo) + mundo("saco", pet(860, 505, pose)) + topo(agora=False) + trilho("crescer") + minimapa("crescer", "saco")
            + placa("saco", "Saco de pancada", px - 30, py - 112)
            + conector("M792 392 L836 392 L880 330", 792, 392)
            + painel("crescer", ativa, corpo, 880, 84, 600, foco, ("treinar",) if ativa != "treinar" else (), dica)
            + contagem(1330, 62) + extra + notas + FIM)


def transicao_3() -> str:
    return _crescer("treinar", corpo_treinar(),
                    nota("3 · chegou: o painel entra ao lado do saco (180 ms, ease-out: o 'card entrando' do guia, seção 11)", 1500, 96, 300)
                    + nota("a ilha continua viva em volta: o painel tem 600 px e não escurece a cena", 1500, 150, 300),
                    "abrir um lugar, quadro 3", pose="treino")


def crescer_treinar() -> str:
    return _crescer("treinar", corpo_treinar(),
                    nota("o treino pronto em destaque, numa palavra; o 'um treino por vez, 10 min' foi para o balão", 1490, 120, 260)
                    + nota("+2/+1: CTR; a estrela da aptidão em Levantar pedra e Esquiva: APTIDAO.brasa (força 1,2, guarda 1,1)", 1490, 220, 260)
                    + nota("marcas 40/60 e 30/60 só em número (CTR, CSO); o rótulo delas vai no aria-label. Fadiga 20, 07:31 e 10/12: EXEMPLO", 1490, 470, 260)
                    + nota("o pet treinando no saco (o CENA.treino de hoje já põe o pet ali: só vista)", 380, 820, 300),
                    "Crescer · Treinar", pose="treino")


def crescer_itens() -> str:
    return _crescer("itens", corpo_itens(),
                    nota("NOVA. Cada chip e carta: ícone, nome curto, efeito em 2 a 4 palavras; o tracejado = ainda não é seu (cadeado no canto)", 1490, 120, 270)
                    + nota("as vagas: 3 encaixes trancados, com o nº de medalhas que abre cada um (CIT.vagas); o Tamer do save tem 0", 1490, 196, 270)
                    + nota("'treino 10/11': os itens ainda não fazem efeito (porqueItensNaoValem do save); a frase vai para o balão", 1490, 274, 270)
                    + nota("o balão aberto: o hover ou o foco no Chip de Força (fora da contagem)", 1490, 520, 270)
                    + nota("o 'próximo' (borda amarela): o primeiro que o Tamer pode ganhar, pela ordem das medalhas", 1490, 600, 270),
                    "Crescer · Itens",
                    extra=balao_aberto("<b>Chip de Força</b>: +1 de força e +1 de vigor, como treino: só ocupa o espaço de treino que ainda falta no "
                                       "estágio. Ainda não é seu: vença o Gazimon na Campina.", 896, 392, 290))


def crescer_evolucao() -> str:
    return _crescer("evolucao", corpo_evolucao(),
                    nota("REFEITA: a forma, o tempo, o que o nível pede e a árvore. Nenhuma frase à vista", 1490, 120, 270)
                    + nota("as medalhas: CMD.adulto = 3; as 3 que o Tamer não tem (Campina, Torre de pedra, Floresta), apagadas; o lugar de cada uma no balão", 1490, 200, 270)
                    + nota("o save mistura duas contas: o pet sabe de 1 medalha (evento 'u'), o Tamer tem 0; o jogo de hoje mostra '1 de 3' e 'Faltam 3'. Aqui, só a do Tamer (pergunta)", 1490, 296, 270)
                    + nota("'0/10 lutas': CAT.sparring, com 80% (CLE.limiarTaxa) no balão; é requisito do Ultimate, então ficou (pergunta)", 1490, 420, 270)
                    + nota("a árvore só da linha do pet: as outras linhas viram nós pontilhados pequenos, sem texto; 15h 15min: EXEMPLO", 1490, 520, 270),
                    "Crescer · Evolução",
                    extra=balao_aberto("<b>Medalha da Campina</b>: vença o Gazimon na Campina.", 912, 392, 260))


def _lutar(ativa: str, corpo: str, notas: str, titulo: str, foco: str = "", dica: str = "") -> str:
    px, py = tela(1600, 482, "portao")
    return (cab(titulo) + mundo("portao", pet(1600, 792, "parado")) + topo(agora=False) + trilho("lutar") + minimapa("lutar", "portao")
            + placa("portao", "Portão da arena", px, py - 62)
            + conector("M1362 560 L1330 520 L1300 520", 1362, 560)
            + painel("lutar", ativa, corpo, 690, 84, 610, foco, (), dica)
            + contagem(1140, 62) + notas + FIM)


def lutar_arena() -> str:
    return _lutar("arena", corpo_arena(),
                  nota("o destaque da Arena: as lutas de treino (0/10, sparringTexto), que levam ao Ultimate; a medalha vira um botão 'Campina'", 1316, 210, 280)
                  + nota("os rivais: nome e estilo (luta.ts, nomesRivais.ts, NOME_BOT). Monochromon escolhido: EXEMPLO. Sem luta, a linha da última luta some", 1316, 330, 280)
                  + nota("a aba Fronteira trancada; o motivo na dica (foco) e no aria-label", 1316, 150, 280)
                  + nota("PORTÃO DA ARENA: aprovado para a ilha 3D; desenho provisório", 1620, 296, 230),
                  "Lutar · Arena", foco="fronteira", dica=f"Nv {NIVEL['fronteira'][0]} · {NIVEL['fronteira'][1]}")


def lutar_medalhas() -> str:
    return _lutar("medalhas", corpo_medalhas(),
                  nota("a próxima em destaque: o líder, o selo, o que ela dá (ícone e nome) e o botão; as frases no balão (medalhas.ts, arenas.ts, itens.ts)", 1316, 230, 280)
                  + nota("as outras: o nº e o lugar; só as que liberam um nível dizem qual (TelaMedalhas.tsx, libera)", 1316, 420, 280)
                  + nota("0/6: o Tamer do save", 1316, 140, 280),
                  "Lutar · Medalhas")


def _diario(ativa: str, corpo: str, notas: str, titulo: str) -> str:
    px, py = tela(269, 430, "barraca")
    return (cab(titulo) + mundo("barraca", pet(515, 712, "parado", virado=True)) + topo(agora=False) + trilho("diario") + minimapa("diario", "barraca")
            + placa("barraca", "Barraca do Tamer", px, py - 70)
            + conector("M430 456 L600 330 L800 330", 430, 456)
            + painel("diario", ativa, corpo, 800, 84, 620)
            + contagem(1260, 62) + notas + FIM)


def diario_registro() -> str:
    return _diario("registro", corpo_registro(),
                   nota("o 'como funciona' aberto (o único quadro em que ele aparece aberto; a contagem inclui ele)", 1436, 640, 250)
                   + nota("o tipo de cada linha vira ícone (o nome no aria-label); 'regras' é aprendido: tracejado ciano (motor.ts _hist, TIPO_REG). Horas, 7000 e 76: EXEMPLO", 1436, 330, 260)
                   + nota("BARRACA DO TAMER: aprovada para a ilha 3D; desenho provisório", 100, 850, 240),
                   "Diário · Registro")


def diario_catalogo() -> str:
    return _diario("catalogo", corpo_catalogo(),
                   nota("19 formas do Coragem (formasDoBrasao, nomes.ts); vistas = o caminho deste pet: 3/19", 1436, 200, 260)
                   + nota("só as vistas têm nome à vista; as outras, a silhueta (no jogo, a do atlas), com o nome no aria-label e no balão", 1436, 380, 260)
                   + nota("a ficha (stats, vida, guts) abre por toque numa forma, como hoje (Folha)", 1436, 560, 260),
                   "Diário · Catálogo")


def ajustes() -> str:
    # o "Tamer Nv N" no leque (P-8); o N do save do antes e a conta de marcos (NIVEL_SAVE, no topo deste arquivo)
    lq = (f'<div class="caixa leque" role="menu" aria-label="Retrato"><span class="tamer-nv" role="img" aria-label="Tamer, nível {NIVEL_SAVE}">Tamer Nv {NIVEL_SAVE}</span>'
          f'<button type="button" role="menuitem">{svg("pet")}Meus pets</button>'
          f'<button type="button" role="menuitem">{svg("digibrain")}DigiBrain</button>'
          f'<button type="button" role="menuitem" aria-expanded="true">{svg("ajustes")}Ajustes</button></div>')
    pn = f'''<section class="caixa lp painel-lugar" style="left:100px;top:128px;width:460px" aria-labelledby="aj-tit">
  <div class="lp-cab" style="padding-bottom:8px">{svg("ajustes")}<span class="lp-tit"><b id="aj-tit">Ajustes</b></span>
    <button type="button" class="bt-ic" aria-label="Fechar os Ajustes" aria-keyshortcuts="Escape">{svg("x")}</button></div>
  <div class="lp-corpo" style="gap:6px;border-top:1px solid var(--hx-borda)">{corpo_ajustes()}</div></section>'''
    return (cab("Ajustes") + mundo("ilha", pet(1160, 400, "parado")) + topo(leque=True) + trilho("pet") + pilha() + dock() + minimapa()
            + lq + pn + contagem(580, 132)
            + nota("o retrato abre um leque: o nível do Tamer (P-8), Meus pets, DigiBrain e Ajustes", 640, 40, 300)
            + nota(f"Tamer Nv {NIVEL_SAVE}: os marcos do save do antes (plano 3.2: o nível é a quantidade de marcos): chocou, 3 chamados, "
                   "Rookie, o primeiro treino e Champion; a primeira medalha falta (o Tamer tem 0)", 580, 520, 300)
            + nota("Ajustes não é lugar: a câmera não se mexe. Cada linha: ícone e nome; o resumo de hoje vai para o balão", 580, 300, 260)
            + nota("a lista é a de TelaConfig.tsx; 'Viagem da câmera' é NOVA (preferência de tela, não de jogo)", 580, 420, 260)
            + FIM)


# ---- a trava de progresso (Matheus, 2026-11-06: "pode ter trava de progresso"; a regra e os numeros ficam para o plano de progressao)
# o estado coerente com a trilha (pedido da rodada 3): o Koromon (In-Training); Tamer Nv 1 (so chocou) e Nv 2 (atendeu 3 chamados)
TRANC_NV1 = ("diario", "crescer", "lutar", "conversar")
TRANC_NV2 = ("crescer", "lutar", "conversar")


def pet_koromon(x: float = 1160, y: float = 400) -> str:
    return pet(x, y, "parado", k=1.25, nome="Koromon")


def cartao_destrave(estilo: str) -> str:
    """o cartao de destrave (plano 4.1, tipo A): o icone do lugar, o titulo de ate 3 palavras, a frase de ate 8 (plano 4.2, linha do Nv 2:
    tent, "Diário", "Veja o que ele fez e por quê."), Ir (a camera vai ao lugar) e Depois. Uma vez por nivel."""
    return (f'<section class="caixa cartao-destrave" role="dialog" aria-labelledby="cd-tit" style="{estilo}">'
            f'<span class="cd-ic">{svg("tent")}</span><span class="cd-txt"><b id="cd-tit">Diário</b><span>Veja o que ele fez e por quê.</span>'
            f'<span class="cd-bts"><button type="button" class="bt acao">{svg("seta")}Ir</button><button type="button" class="bt">Depois</button></span></span></section>')


def lugar_trancado() -> str:
    cx, cy = tela(*CADEADO["crescer"], "ilha")
    return (cab("lugar trancado") + mundo("ilha", pet_koromon(), trancados=("diario", "crescer", "lutar"))
            + topo(nome="Koromon", nivel="In-Training · Coragem") + trilho("pet", trancados=TRANC_NV1)
            + pilha(evo="próxima: Rookie") + dock() + minimapa(trancados=("diario", "crescer", "lutar"))
            + cadeados("ilha", ("diario", "crescer", "lutar"))
            + balao_aberto(f'<b>Nv {NIVEL["crescer"][0]}</b> · {NIVEL["crescer"][1]}', cx - 20, cy + 36, 260)
            + nota("Tamer Nv 1 (só chocou): o Koromon, In-Training. A barraca (Nv 2), o saco (Nv 3) e o portão (Nv 4) apagados, com o cadeado e o nível "
                   "(plano 3.3 e 3.4, P-11: visíveis desde o Nv 1)", 330, 450, 300)
            + nota("o trilho: os ícones iguais, só apagados (Diário, Crescer, Lutar e Conversar); o nível e o marco no aria-label. A tecla ou a rota de "
                   "um lugar trancado abre o cartão do motivo, não o painel (3.4)", 330, 560, 300)
            + nota("o balão aberto: o foco ou o hover no saco. O texto do marco é da prancha, da tabela 3.3 (a linha 3: 'virou Rookie')", 330, 680, 300)
            + FIM)


def lugar_destravado() -> str:
    bx, by = tela(140, 470, "ilha")
    return (cab("lugar destravado")
            + mundo("ilha", pet_koromon(), trancados=("crescer", "lutar"), extra=brilho(118, 448, 292, 270))
            + topo(nome="Koromon", nivel="In-Training · Coragem") + trilho("pet", trancados=TRANC_NV2, novo="diario")
            + pilha(evo="próxima: Rookie") + dock() + minimapa(trancados=("crescer", "lutar"), novo="diario")
            + cadeados("ilha", ("crescer", "lutar"), aberto="diario")
            + cartao_destrave(f"left:{bx + 370:.0f}px;top:{by - 30:.0f}px")
            + nota("Tamer Nv 2: o Koromon atendeu 3 chamados (plano 3.3, linha 2). A barraca abre: o cadeado aberto e o brilho uma vez em --hx-alerta "
                   "(3.4); o saco e o portão continuam trancados", 480, 650, 320)
            + nota("o cartão de destrave (4.1, tipo A): ícone tent, 'Diário' e 'Veja o que ele fez e por quê.' (4.2, linha do Nv 2); Ir leva a câmera "
                   "à barraca, Depois fecha. Com reduzir movimento, sem brilho: só o cartão", 480, 750, 320)
            + FIM)


# ---------------------------------------------------------------------------------------------------- antes x depois
ANTES = {"itens": 455, "evolucao": 235}   # antes_palavras.json (medir_antes.mjs): o painel inteiro, inclusive o que so aparece rolando


def antes_depois(aba: str) -> str:
    nome = {"itens": "Itens", "evolucao": "Evolução"}[aba]
    corpo = corpo_itens() if aba == "itens" else corpo_evolucao()
    antes = (f'<div class="antes-cx" role="img" aria-label="O jogo de hoje: Crescer · {nome}">'
             f'<i class="so-militar" style="background-image:url(\'img/antes/antes_{aba}_1920_militar.jpg\')"></i>'
             f'<i class="so-vidro" style="background-image:url(\'img/antes/antes_{aba}_1920_vidro.jpg\')"></i></div>')
    return (cab(f"antes x depois · {nome}") + mundo("saco_ad", pet(905, 505, "parado", k=1.7)) + antes
            + painel("crescer", aba, corpo, 1240, 60, 600)
            + f'<span class="titulo-pr">Crescer · {nome}: antes (o jogo de hoje) × depois (a regra do texto)</span>'
            + f'<span class="contagem" style="left:40px;top:874px"><b>{ANTES[aba]}</b> palavras no painel, antes · antes_palavras.json (medir_antes.mjs), com o que só aparece rolando</span>'
            + f'<span class="contagem" style="left:1240px;top:874px" data-conta=".painel-lugar"><b>…</b> palavras no painel, depois · innerText de .painel-lugar nesta página, a mesma regex</span>'
            + FIM)


def antes_depois_390(aba: str) -> str:
    nome = {"itens": "Itens", "evolucao": "Evolução"}[aba]
    antes = (f'<div class="cel-cx" style="left:500px" role="img" aria-label="O jogo de hoje a 390: Crescer · {nome}">'
             f'<i class="so-militar" style="position:absolute;inset:0;background:url(\'img/antes/antes_{aba}_390_militar.jpg\') 0 0/390px auto no-repeat"></i>'
             f'<i class="so-vidro" style="position:absolute;inset:0;background:url(\'img/antes/antes_{aba}_390_vidro.jpg\') 0 0/390px auto no-repeat"></i></div>')
    # o depois: a propria pagina de 390 num iframe, com a mesma pele e sem notas
    ifr = (f'<iframe class="cel-cx" style="left:1030px" id="ifr" data-conta-em="#conta-depois" title="O depois a 390: Crescer · {nome}"></iframe>'
           f'<script>document.getElementById("ifr").src="crescer_{aba}_390.html?sem&pele="+(new URLSearchParams(location.search).get("pele")||"vidro");</script>')
    return (cab(f"antes x depois a 390 · {nome}") + f'<div class="cena-cel" style="opacity:.25" aria-hidden="true"></div>' + antes + ifr
            + f'<span class="titulo-pr">Crescer · {nome} a 390: antes (a M1 do mobile) × depois (a M2, a regra do texto)</span>'
            + f'<span class="contagem" style="left:500px;top:894px;white-space:normal;width:390px"><b>{ANTES[aba]}</b> palavras na folha, antes · antes_palavras.json (medir_antes.mjs)</span>'
            + f'<span class="contagem" id="conta-depois" style="left:1030px;top:894px;white-space:normal;width:390px"><b>…</b> palavras na folha, depois · innerText de .painel-lugar no iframe</span>'
            + FIM)


TELAS = {
    "transicao_1_1920": transicao_1, "transicao_2_1920": transicao_2, "transicao_3_1920": transicao_3,
    "crescer_treinar_1920": crescer_treinar, "crescer_itens_1920": crescer_itens, "crescer_evolucao_1920": crescer_evolucao,
    "lutar_arena_1920": lutar_arena, "lutar_medalhas_1920": lutar_medalhas,
    "diario_registro_1920": diario_registro, "diario_catalogo_1920": diario_catalogo,
    "ajustes_1920": ajustes, "lugar_trancado_1920": lugar_trancado, "lugar_destravado_1920": lugar_destravado,
    "antes_depois_itens_1920": lambda: antes_depois("itens"), "antes_depois_evolucao_1920": lambda: antes_depois("evolucao"),
    "antes_depois_itens_390": lambda: antes_depois_390("itens"), "antes_depois_evolucao_390": lambda: antes_depois_390("evolucao"),
}

def escrever() -> None:
    d = Path(__file__).parent
    for nome, f in TELAS.items():
        (d / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    escrever()
    # o celular (390 e 360) fica no gerar_movel.py, com os mesmos ajudantes; rodar este escreve as duas larguras
    import gerar_movel
    gerar_movel.escrever()
