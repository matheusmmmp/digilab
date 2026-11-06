# Gera a prancha "Lugares da ilha: menus" (L2/L3), a 1920 x 950: cada menu e um lugar da ilha. So desenho; nenhum codigo do jogo.
# A pele vem de ?pele=vidro|xcom no endereco, e ?sem tira as notas amarelas.
# Uso: python docs/pranchas/ux-lugares-menus/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim).
# O fundo img/cena_sem_pet.jpg e uma captura do jogo de 2026-11-06 (a ilha de dia, sem HUD, a 1920 x 931), com o pet embutido
# e o "Zz" apagados por remendo de grama da propria captura; o pet e o objeto novo vem por cima, nesta prancha.
#
# DE ONDE VEM CADA TEXTO E NUMERO (a tabela completa esta em docs/PROPOSTAS_V3_UX_TELA_PET.md, secao "Lugares da ilha: menus (L2/L3)"):
#   nomes das formas e niveis ....... web/app/motor/nomes.ts (DIGIMON_DA_FORMA, NOME_EST, NOME_ARQ, NOME_ESP, NOME_STAT, NOME_EXERCICIO, NOME_PET)
#   treino .......................... motor/constantes.ts CTR (ganhoPri 2, ganhoSec 1, tetoStat 10, tetoEstagio.crianca 10, tetoVida 36,
#                                     limiarPausa 40, limiteForcar 60, intervalo 10), CSO (aviso 30, sombrio 60), APTIDAO.cirro;
#                                     textos de src/telas/crescer/TelaTreinar.tsx ("pronto para treinar", a legenda da aptidao)
#   evolucao ........................ CMD (adolescente 1, adulto 3, mega 5), CAT.adolescente (eixos), CAT.limiarCuidado .8;
#                                     src/telas/crescer/TelaEvolucao.tsx (requisito, fmtCar "todos os eixos na faixa comum")
#   arena e medalhas ................ src/luta.ts (RIVAIS_CLASSICOS, RIVAIS_ADULTOS), src/nomesRivais.ts (DIGIMON_BOT), motor/bots.ts
#                                     (NOME_BOT, os NPCs), motor/medalhas.ts (MEDALHAS), motor/arenas.ts (titulo, frase), motor/itens.ts
#                                     (ITEM_DA_MEDALHA, CARTA_DA_REVANCHE), src/tamer.ts (comoGanhar, textoFalta), motor/liga.ts (MEDALHAS_LIGA)
#   registro ........................ motor/motor.ts (_hist: "alimentar", "carinho", "treinou corrida"), NOME_PET; src/telas/diario/TelaRegistro.tsx
#   catalogo ........................ src/telas/diario/TelaCatalogo.tsx (formasDoBrasao: 19 formas; "N de 19 vistas")
#   ajustes ......................... src/telas/config/TelaConfig.tsx (a lista e os resumos); src/pele.ts (NOME_PELE)
# EXEMPLO DE LAYOUT, NUNCA DADO: Dia 3, 07:42, semente 7000, 76 eventos (os dois da captura de hoje), fadiga 20, os pontos treinados,
#   o prazo da evolucao, as horas do registro. Nenhum numero de jogo novo; as duracoes da viagem sao PROPOSTAS, SEM FONTE.
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
    # abas de Crescer
    "treinar": '<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>',
    "aprend": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    "evolucao": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-12 7"/>',
    "itens": '<rect x="7" y="7" width="10" height="10" rx="1"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
    # abas de Lutar
    "arena": '<path d="M5 19L19 5"/><path d="M14 5h5v5"/><path d="M5 14l5 5"/>',
    "exploracao": '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    "fronteira": '<path d="M5 21V4"/><path d="M5 4h12l-2.5 4L17 12H5"/>',
    "medalhas": '<circle cx="12" cy="15" r="5"/><path d="M8 3l4 7 4-7"/>',
    # abas do Diario
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
    # controles
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "seta": '<path d="M9 6l6 6-6 6"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v.5"/>',
    "cadeado": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
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


# ---------------------------------------------------------------------------------------------------- a camera
# (escala, ox, oy): o plano da ilha (1920 x 931) escalado e deslocado. Os enquadramentos sao de layout, nao de jogo.
CAM = {
    "ilha": (1.0205, 20, 0),        # a ilha normal (931 x 1,0205 = 950)
    "viagem": (1.18, 330, 40),      # o meio do caminho ate o saco (quadro b)
    "saco": (1.35, 650, 83),        # Crescer
    "portao": (1.30, 576, 201),     # Lutar
    "barraca": (1.35, 0, 145),      # Diario
}


def tela(x: float, y: float, cam: str) -> tuple[float, float]:
    s, ox, oy = CAM[cam]
    return x * s - ox, y * s - oy


# ---------------------------------------------------------------------------------------------------- o pet (o Gabumon)
# A folha Gabumon.png e 791 x 538, 8 x 7 quadros de 98,875 x 76,857 (o recorte do pet.css da ux-pet: 0, -307,6 = linha 4).
QW, QH = 791 / 8, 538 / 7
POSE = {"parado": (0, 4), "andando": (4, 5), "treino": (4, 3)}


def pet(cx: float, base: float, pose: str, k: float = 2, virado: bool = False) -> str:
    c, r = POSE[pose]
    w, h = QW * k, QH * k
    v = " virado" if virado else ""
    return (f'<div class="pet{v}" role="img" aria-label="Gabumon" style="left:{cx - w / 2:.1f}px;top:{base - h:.1f}px;width:{w:.1f}px;height:{h:.1f}px;'
            f'background-size:{791 * k:.1f}px {538 * k:.1f}px;background-position:{-c * QW * k:.1f}px {-r * QH * k:.1f}px"></div>')


def spr(pose: str, k: float) -> str:
    """o Gabumon dentro de um painel (palco, tile)"""
    c, r = POSE[pose]
    return (f'<span class="spr" style="width:{QW * k:.1f}px;height:{QH * k:.1f}px;background-size:{791 * k:.1f}px {538 * k:.1f}px;'
            f'background-position:{-c * QW * k:.1f}px {-r * QH * k:.1f}px"></span>')


# ---------------------------------------------------------------------------------------------------- os objetos novos (desenho provisorio)
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


def portao() -> str:
    """o portao da arena (OBJETO NOVO): no fim do caminho de terra, a direita, atravessado na trilha; base em y 765"""
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


def barraca() -> str:
    """a barraca do Tamer (OBJETO NOVO): a esquerda, encostada no barranco; base em y 700"""
    return "".join([
        sombra_chao(92, 682, 380, 36, .45),
        parte("areia", 140, 470, 250, 230, "50% 0,100% 100%,0 100%", "50% 0,100% 100%,50% 100%", .3),
        parte("vermelho", 136, 680, 258, 20, "3% 0,97% 0,100% 100%,0 100%"),
        f'<div class="sombra objeto" style="left:232px;top:588px;width:66px;height:94px;border-radius:0;clip-path:polygon(50% 0,100% 100%,0 100%);opacity:.9"></div>',
        parte("madeira", 261, 428, 8, 48),
        parte("vermelho", 269, 430, 50, 28, "0 0,100% 50%,0 100%", "0 50%,100% 50%,0 100%", .25),
        parte("faixa", 404, 640, 62, 58, "", "62% 0,100% 0,100% 100%,62% 100%", .3),
        parte("madeira", 112, 600, 8, 100),
        parte("faixa", 82, 572, 68, 44, "4% 0,96% 0,100% 100%,0 100%", "0 78%,100% 78%,100% 100%,0 100%", .3),
        simbolo("vermelho", "diario", 102, 578, 30),
    ])


def mundo(cam: str, pets: str) -> str:
    s, ox, oy = CAM[cam]
    return (f'<div class="mundo" style="--s:{s};--ox:{ox};--oy:{oy}" role="img" aria-label="A ilha (o fundo e uma captura real do jogo, de dia)">'
            f'{portao()}{barraca()}{pets}</div>')


# ---------------------------------------------------------------------------------------------------- a HUD que fica
def cab(titulo: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=1920">
<title>Lugares da ilha · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600;700;800;900&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="lugares.css">
<style>:root{{--assets-spr:url("{A}/sprites/Gabumon.png")}}</style>
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.pele=q.get("pele")==="xcom"?"xcom":"vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body>'''


def topo(leque: bool = False, agora: bool = True) -> str:
    ag = ('<button type="button" class="caixa agora" aria-label="Agora: explorando. Tempo livre: o instinto faria o mesmo. Abrir o porquê no DigiBrain">'
          '<span class="rot">agora</span><span class="acao">explorando</span><span class="neutro">· Tempo livre · o instinto faria o mesmo</span></button>') if agora else ""
    exp = "true" if leque else "false"
    return f'''<header class="topo">
  <div class="caixa topo-pet"><button type="button" class="retrato" aria-label="Retrato: Meus pets, DigiBrain e Ajustes" aria-haspopup="menu" aria-expanded="{exp}"><i></i></button>
    <span class="topo-pet-txt"><b>Gabumon</b><small>Rookie · Amizade</small></span></div>
  {ag}
  <span class="logo">DIGILAB</span>
  <div class="caixa relogio"><span class="hora"><small>Dia 3</small><b>07:42</b></span><span class="salvo">● salvo</span></div>
</header>'''


# o trilho: Pet volta a ilha (Esc); C, L, D abrem o lugar com corte seco (o atalho direto, PROPOSTO)
TECLA = {"crescer": "C", "lutar": "L", "diario": "D"}


def trilho(atual: str = "pet", clicado: str = "") -> str:
    bts = []
    for n, r in [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário"), ("conversar", "Conversar")]:
        cur = ' aria-current="page"' if n == atual else ""
        cl = " clicado" if n == clicado else ""
        k = f'<kbd aria-hidden="true">{TECLA[n]}</kbd>' if n in TECLA else ""
        ks = f' aria-keyshortcuts="{TECLA[n]}"' if n in TECLA else (' aria-keyshortcuts="Escape"' if n == "pet" else "")
        bts.append(f'<button type="button" class="nav-bt{cl}"{cur}{ks}>{svg(n)}{r}{k}</button>')
    return f'<nav class="caixa trilho" aria-label="Navegação">{"".join(bts)}</nav>'


def pilha(cls: str = "") -> str:
    def p(ic: str, tit: str, res: str) -> str:
        return (f'<section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false">{svg(ic)}'
                f'<span class="tit">{tit}<span class="resumo">{res}</span></span><span class="risca"></span></button></section>')
    return (f'<aside class="pilha {cls}" aria-label="Painéis do pet">{p("estado", "Estado atual", "comida 64 % · higiene 40 %")}'
            f'{p("evolucao", "Evolução", "Champion: falta 1 medalha")}{p("acoes", "Últimas ações", "07:40 · carinho")}</aside>')


def dock(cls: str = "") -> str:
    b = "".join(f'<button type="button">{a}</button>' for a in ["Alimentar", "Brincar", "Limpar", "Carinho", "Tapa", "Tratar", "Mais"])
    return f'<nav class="caixa dock {cls}" aria-label="Ações">{b}</nav>'


# ---- o minimapa (contexto): coordenadas do circulo de 216 px
MINI = {"crescer": (111, 83), "lutar": (146, 146), "diario": (47, 113), "fronteira": (180, 96)}
PET_MINI = {"ilha": (125, 63), "saco": (96, 96), "portao": (146, 179), "barraca": (70, 132), "viagem": (112, 78)}


def minimapa(atual: str = "", pet_em: str = "ilha") -> str:
    px, py = PET_MINI[pet_em]
    mapa = f'''<svg class="mapa" viewBox="0 0 216 216" aria-hidden="true">
  <polygon class="ilha" points="30,62 62,30 108,20 160,32 192,64 200,110 188,160 150,194 100,202 56,186 24,150 16,104"/>
  <path class="arv" d="M54 46l7-13 7 13zM84 36l7-13 7 13zM120 34l7-13 7 13zM156 44l7-13 7 13z"/>
  <path class="barranco" d="M20 122 Q36 74 92 56"/>
  <path class="trilha" d="M74 130 L130 120 L146 146 L170 150 Q192 138 182 112"/>
  <ellipse class="coisa" cx="74" cy="130" rx="11" ry="6"/><circle class="coisa" cx="130" cy="118" r="5"/>
  <circle class="pet-ponto" cx="{px}" cy="{py}" r="6"/>
</svg>'''

    def bt(n: str, ic: str, rot: str) -> str:
        x, y = MINI[n]
        cur = ' aria-current="true"' if n == atual else ""
        return f'<button type="button" class="mini-bt" style="left:{x}px;top:{y}px" aria-label="{rot}"{cur}>{svg(ic)}</button>'
    fx, fy = MINI["fronteira"]
    # a Fronteira: trancada ate as 6 medalhas (MapaExploracao.tsx: "abre com as 6 medalhas (0 de 6)"; MEDALHAS_LIGA = MEDALHAS.length)
    fr = (f'<button type="button" class="mini-bt trancado" style="left:{fx}px;top:{fy}px" aria-disabled="true" '
          f'aria-label="Fronteira, trancada: abre com as 6 medalhas (0 de 6)">{svg("fronteira")}<span class="cad">{svg("cadeado")}</span></button>')
    return (f'<nav class="mini" aria-label="Minimapa: clicar num lugar abre o menu dele">{mapa}'
            f'{bt("crescer", "saco", "Saco de pancada: Crescer")}{bt("lutar", "portao", "Portão da arena: Lutar")}{bt("diario", "barraca", "Barraca do Tamer: Diário")}'
            f'{fr}<span class="mini-rot">ilha</span></nav>')


def nota(txt: str, x: float, y: float, w: int = 300) -> str:
    return f'<span class="nota" style="left:{x}px;top:{y}px;max-width:{w}px">{txt}</span>'


def placa(ic: str, nome: str, x: float, y: float, cls: str = "") -> str:
    return f'<span class="caixa placa-lugar {cls}" style="left:{x}px;top:{y}px">{svg(ic)}{nome}</span>'


def conector(d: str, cx: float, cy: float) -> str:
    return f'<svg class="conector" viewBox="0 0 1920 950" aria-hidden="true"><path d="{d}"/><circle cx="{cx}" cy="{cy}" r="4"/></svg>'


# ---------------------------------------------------------------------------------------------------- o painel do lugar
ABAS = {
    "crescer": [("treinar", "Treinar"), ("aprend", "Aprendizado"), ("evolucao", "Evolução"), ("itens", "Itens")],
    "lutar": [("arena", "Arena"), ("exploracao", "Exploração"), ("fronteira", "Fronteira"), ("medalhas", "Medalhas")],
    "diario": [("registro", "Registro"), ("catalogo", "Catálogo"), ("geracoes", "Gerações"), ("cenarios", "Cenários")],
}
NOME_DEST = {"crescer": "Crescer", "lutar": "Lutar", "diario": "Diário"}
LUGAR = {"crescer": "no saco de pancada", "lutar": "no portão da arena", "diario": "na barraca do Tamer"}


def abas(dest: str, ativa: str, foco: str = "", marcas: tuple = (), dica_foco: str = "") -> str:
    out = []
    for i, (n, rot) in enumerate(ABAS[dest], 1):
        sel = n == ativa
        tranc = dest == "lutar" and n == "fronteira"
        cls = "aba" + (" trancada" if tranc else "") + (" foco" if n == foco else "")
        lab = f"{rot}, trancada: abre com as 6 medalhas (0 de 6)" if tranc else rot
        conteudo = svg(n) + (rot if sel else "")
        if n in marcas:
            conteudo += '<i class="marca" aria-hidden="true"></i>'
        if tranc:
            conteudo += f'<span class="cad" aria-hidden="true">{svg("cadeado")}</span>'
        if n == foco:
            sub = f"<small>{dica_foco}</small>" if dica_foco else ""
            conteudo += f'<span class="caixa dica" role="tooltip">{rot}{sub}</span>'
        dis = ' aria-disabled="true"' if tranc else ""
        out.append(f'<button type="button" role="tab" class="{cls}" aria-selected="{"true" if sel else "false"}" aria-label="{lab}" '
                   f'aria-keyshortcuts="{i}" title="{lab}"{dis}>{conteudo}</button>')
    return f'<div class="abas" role="tablist" aria-label="Abas de {NOME_DEST[dest]}">{"".join(out)}</div>'


def painel(dest: str, ativa: str, corpo: str, x: float, y: float, w: float, foco: str = "", marcas: tuple = (), dica_foco: str = "") -> str:
    return f'''<section class="caixa lp" style="left:{x}px;top:{y}px;width:{w}px" aria-labelledby="lp-tit">
  <div class="lp-cab">{svg(dest)}<span class="lp-tit"><b id="lp-tit">{NOME_DEST[dest]}</b><small>{LUGAR[dest]}</small></span>
    <button type="button" class="bt-ic bt-fechar" aria-label="Voltar à ilha" aria-keyshortcuts="Escape">{svg("x")}<kbd aria-hidden="true">Esc</kbd></button></div>
  {abas(dest, ativa, foco, marcas, dica_foco)}
  <div class="lp-corpo" role="tabpanel">{corpo}</div>
</section>'''


def como(txt: str, aberto: bool = False, titulo: str = "Como funciona") -> str:
    a = " open" if aberto else ""
    return f'<details class="como"{a}><summary>{svg("info")}{titulo}{svg("seta")}</summary><p>{txt}</p></details>'


def fechado(ic: str, tit: str, res: str, cls: str = "") -> str:
    return f'<button type="button" class="fechado {cls}" aria-expanded="false">{svg(ic)}<span>{tit}</span><span class="sec">{res}</span>{svg("seta")}</button>'


def med(rot: str, v: float, marcas: list, cls: str = "") -> str:
    lim = "".join(f'<span class="lim" style="left:{m}%"></span>' for m, _ in marcas)
    mk = "".join(f'<span style="left:{m}%">{m} · {t}</span>' for m, t in marcas)
    return (f'<div class="med {cls}"><span class="rot">{rot}</span><span class="barra" role="img" aria-label="{rot} {v:.0f} de 100">'
            f'<i style="--v:{v}%"></i>{lim}</span><em>{v:.0f} / 100</em><span class="marcas" aria-hidden="true">{mk}</span></div>')


# ---------------------------------------------------------------------------------------------------- Crescer
def corpo_treinar() -> str:
    # CTR.exercicios (pri, sec), CTR.ganhoPri 2 e ganhoSec 1; NOME_EXERCICIO e NOME_STAT; aptidao do Amizade (APTIDAO.cirro: mira 1,2,
    # recuperacao 1,1): o selo vai em Alvo (mira) e Meditar (recuperacao), como em TelaTreinar.tsx (apt[pri] > 1)
    ex = [("levantar_pedra", "Levantar pedra", "força", "vigor", False), ("corrida", "Corrida", "fôlego", "recuperação", False),
          ("alvo", "Alvo", "mira", "fôlego", True), ("esquiva", "Esquiva", "guarda", "vigor", False),
          ("meditar", "Meditar", "recuperação", "guarda", True), ("resistencia", "Resistência", "vigor", "força", False)]
    grade = "".join(
        f'<button type="button" class="ex" aria-label="Treinar {n}">{svg(k)}<b>{n}</b><small>+2 {p} · +1 {s}</small>'
        + ('<span class="etq alerta">aptidão</span>' if apt else "") + "</button>" for k, n, p, s, apt in ex)
    return f'''
<div class="destaque" role="status"><span class="rot">agora</span><b class="grande">Pronto para treinar</b>
  <span class="sec">último: Corrida · 07:31 · um treino por vez, 10 min de intervalo</span></div>
<div class="ex-grade" role="group" aria-label="Exercícios">{grade}</div>
<p class="sec"><span class="etq alerta">aptidão</span> Amizade rende 1,2× em mira e 1,1× em recuperação.</p>
<div class="cartao" style="display:flex;flex-direction:column;gap:6px"><span class="rot">Cansaço</span>
  {med("Fadiga", 20, [(40, "pede pausa"), (60, "só forçar")])}
  {med("Sobrecarga", 0, [(30, "aviso"), (60, "sombria")])}</div>
<div class="linha"><button type="button" class="bt forcar" disabled>Forçar treino</button><span class="sec">abre com fadiga 60</span>
  <span class="sec" style="margin-left:auto">na vida <b class="num" style="--n:15px">+3,1</b> de 36</span></div>
{fechado("treinar", "Treinado na vida, stat a stat", "6 stats · de 0 a 10")}
{como("Um toque por sessão, com pelo menos 10 min entre elas. Cada exercício sobe um stat principal e um secundário. Com fadiga 40 ele pede pausa; com 60 o botão vira Forçar: rende mais, mas gera sobrecarga.")}'''


def corpo_evolucao() -> str:
    # a arvore do Amizade (nomes.ts): Tsunomon; Patamon (sereno) e Gabumon (arisco); os 4 Champions sao "?" (a forma futura ainda nao
    # decidida pelo motor aparece sem nome, TelaEvolucao.tsx e guia 5), com o eixo da linha (CAT.adolescente: impetuoso, paciente, atento,
    # resistente). CMD.adolescente = 1 medalha. O prazo e exemplo de layout (m.dur e o relogio do pet).
    champs = "".join(f'<button type="button" class="no possivel" aria-label="forma ainda não decidida, Champion, {e}, possível"><span class="q">?</span><small>{e}</small></button>'
                     for e in ["impetuoso", "paciente", "atento", "resistente"])
    return f'''
<div class="heroi">
  <div class="palco" aria-hidden="true"><span class="disco"></span><span class="spr-pos" style="position:absolute;left:50%;bottom:2px;transform:translateX(-50%)">{spr("parado", 1.4)}</span></div>
  <div><span class="rot">forma atual</span><div class="nome">Gabumon</div><span class="sec">Rookie · brasão Amizade</span></div>
  <div class="prazo"><span class="num">1d 4h</span><span class="sec">até virar Champion</span></div>
</div>
<div class="destaque" role="status"><span class="rot">o que falta</span>
  <div class="linha" style="margin-top:4px"><span class="selos"><span class="selo proxima" aria-hidden="true"><i>1</i></span></span>
    <span><b style="font:700 17px/1.2 var(--hx-f)">0 de 1 medalha do Tamer</b><br><span class="sec">Falta a Medalha da Campina: vença o Gazimon na Campina.</span></span></div>
  <div class="linha" style="margin-top:8px"><button type="button" class="bt acao">{svg("exploracao")}Ir à Exploração</button><span class="sec">a câmera vai ao portão</span></div></div>
<div class="cartao" style="display:flex;flex-direction:column;gap:2px"><span class="rot">se evoluísse agora</span>
  <span>caráter: todos os eixos na faixa comum <span class="sec">→ ?</span></span></div>
<div class="arv" role="group" aria-label="Árvore de Amizade">
  <div class="arv-nivel"><span class="rot">In-Training</span><div class="arv-nos"><button type="button" class="no percorrido" aria-label="Tsunomon, percorrido">{svg("check", "ic ok")}<span>Tsunomon</span></button></div></div>
  <div class="arv-nivel"><span class="rot">Rookie</span><div class="arv-nos">
    <button type="button" class="no agora" aria-label="Gabumon, agora"><span>Gabumon<small>agora · cuidado &lt; 80%</small></span></button>
    <button type="button" class="no fechado" aria-label="Patamon, fechado"><span>Patamon<small>cuidado ≥ 80%</small></span></button></div></div>
  <div class="arv-nivel"><span class="rot">Champion</span><div class="arv-nos">{champs}</div></div>
</div>
{fechado("evolucao", "Ultimate e Mega", "8 + 4 formas · no Catálogo")}
{fechado("acoes", "Histórico", "nasceu Tsunomon · virou Gabumon")}
{como("Cada evolução é decidida pelo que o pet viveu: cuidado, caráter e lutas de treino. Depois do Rookie, cada evolução pede medalhas do Tamer: 1 para Champion, 3 para Ultimate e 5 para Mega.")}'''


# ---------------------------------------------------------------------------------------------------- Lutar
def corpo_arena() -> str:
    # os bots (luta.ts RIVAIS_CLASSICOS; nome: nomesRivais.ts DIGIMON_BOT; estilo: bots.ts NOME_BOT; o oraculo e "referência",
    # TelaArena.tsx). O escolhido (Monochromon) e exemplo. RIVAIS_ADULTOS tem 8. "3 regras de combate": o Rookie tem 3 (o "Como
    # funciona" da Arena); no jogo e m.gp.ativas.length.
    bots = [("Kuramon", "aleatório"), ("Monochromon", "agressivo"), ("Golemon", "tartaruga"), ("Tankmon", "atirador"),
            ("Leomon", "contragolpe"), ("Devimon", "adaptativo"), ("Jijimon", "referência")]
    riv = "".join(f'<button type="button" class="rival" role="radio" aria-checked="{"true" if n == "Monochromon" else "false"}"><span class="radio" aria-hidden="true"></span>'
                  f'<span><b>{n}</b><small>{e}</small></span></button>' for n, e in bots)
    return f'''
<div class="linha"><span class="palco" style="width:76px;height:60px" aria-hidden="true"><span style="position:absolute;left:50%;bottom:0;transform:translateX(-50%)">{spr("parado", .75)}</span></span>
  <span><b style="font:700 18px/1.1 var(--hx-f)">Gabumon</b><br><span class="sec">Rookie</span></span>
  <span class="chip-apr" style="margin-left:auto">{svg("digibrain")}3 regras de combate</span></div>
<div class="destaque" role="status"><span class="rot">a luta que libera medalha</span><b class="grande">Gazimon, na Campina</b>
  <span class="sec">Medalha da Campina · libera Rookie → Champion</span>
  <div class="linha" style="margin-top:8px"><button type="button" class="bt acao">{svg("exploracao")}Ir à Exploração</button><span class="sec">a campanha fica na Exploração</span></div></div>
<span class="rot">Rival de treino</span>
<div class="rivais" role="radiogroup" aria-label="Rival">{riv}<button type="button" class="rival" aria-expanded="false"><span class="radio" style="border-style:dashed" aria-hidden="true"></span><span><b>+ 8 formas adultas</b><small>mostrar</small></span></button></div>
<div class="lutar-linha"><button type="button" class="bt acao grande">{svg("lutar")}Lutar</button><button type="button" class="bt">Melhor de 10</button></div>
<p class="sec">Nenhuma luta ainda. A primeira aparece aqui.</p>
{fechado("digibrain", "Regras de combate do seu pet", "3 regras · travar ou vetar", "")}
{como("Lute contra um rival. Seu pet decide por regras de combate que ele mesmo aprende lutando; você pode travar ou vetar regras. A campanha contra os NPCs fica na aba Exploração.")}'''


def corpo_medalhas() -> str:
    # MEDALHAS (medalhas.ts), os lideres (bots.ts), a regra (arenas.ts), o item e a carta (itens.ts), o que libera (CMD e
    # TelaMedalhas.tsx libera()); a 6a: "a coleção completa e a Fronteira (a Liga dos Líderes)". O Tamer com 0 medalhas e exemplo.
    outras = [(2, "Medalha da Torre de pedra", "vença o Guardromon na Torre de pedra", ""),
              (3, "Medalha da Floresta", "vença o Youkomon na Floresta", "Champion → Ultimate"),
              (4, "Medalha da Cidadela", "vença o Myotismon três vezes seguidas na Cidadela", ""),
              (5, "Medalha do Lago", "vença o MarinBullmon no Lago", "Ultimate → Mega"),
              (6, "Medalha da Montanha Espiral", "vença o Piedmon na Montanha Espiral", "a Fronteira")]
    li = "".join(f'<button type="button" class="med-li" aria-expanded="false"><span class="selo" aria-hidden="true"><i>{n}</i></span>'
                 f'<span><b>{nm}</b><small>{onde}</small></span>' + (f'<span class="etq">libera {lib}</span>' if lib else '<span class="sec">ainda não</span>')
                 + "</button>" for n, nm, onde, lib in outras)
    return f'''
<div class="med-cab"><span><span class="rot">medalhas do Tamer</span><br><span class="num">0</span> <span class="sec">de 6</span></span>
  <ul class="libera" aria-label="O que as medalhas liberam"><li><b>1</b>Rookie → Champion</li><li><b>3</b>Champion → Ultimate</li><li><b>5</b>Ultimate → Mega</li></ul></div>
<div class="destaque" role="status"><span class="rot">a próxima</span>
  <div class="lider" style="margin-top:6px">
    <span class="lider-spr" role="img" aria-label="Gazimon, líder da Campina"><i></i><small>líder</small></span>
    <span><span class="linha"><span class="selo proxima" aria-hidden="true"><i>1</i></span><b class="grande" style="margin:0">Medalha da Campina</b></span>
      <span class="sec" style="display:block;margin-top:4px">vença o Gazimon na Campina · <b>O básico:</b> sem regra especial, vence o pet bem cuidado e treinado.</span>
      <span class="linha" style="margin-top:6px;flex-wrap:wrap;gap:6px"><span class="etq alerta">libera Rookie → Champion</span><span class="etq">dá Chip de Força</span><span class="etq">revanche: Carta de Fôlego</span></span></span></div>
  <div class="linha" style="margin-top:10px"><button type="button" class="bt acao">{svg("exploracao")}Ir à Campina</button><span class="sec">abre a Exploração</span></div></div>
<div class="med-lista" aria-label="As outras medalhas">{li}</div>
<div class="med-li" style="cursor:default"><span class="selo ouro" aria-hidden="true" style="opacity:.6"><i>★</i></span>
  <span><b>Medalha de ouro e recordes da Fronteira</b><small>com as 6 medalhas, vença a Liga dos Líderes na Fronteira; os recordes abrem depois do título</small></span><span class="sec">{svg("cadeado")}</span></div>
{como("As medalhas são suas, não do pet: ficam quando ele é guardado ou morre, e valem para todos os pets seguintes. Vença o líder de cada lugar da campanha para ganhar a dele, com um item.")}'''


# ---------------------------------------------------------------------------------------------------- Diario
def corpo_registro() -> str:
    # as linhas: o _hist do motor (motor.ts: dono -> a acao, "alimentar", "carinho"; treino -> "treinou corrida"; pet -> NOME_PET) e as
    # etiquetas de TelaRegistro.tsx (TIPO_REG: você, pet, treino, regras...). "regras" e o aprendido (malha/tracejado ciano). Horas: exemplo.
    linhas = [("D3 07:40", "você", "carinho", ""), ("D3 07:31", "treino", "treinou corrida", ""), ("D3 07:24", "pet", "brincando", ""),
              ("D3 07:18", "regras", "regras de combate: travou uma regra", "apr"), ("D3 07:15", "você", "alimentar", ""),
              ("D3 07:02", "pet", "explorando", ""), ("D2 22:10", "pet", "dormindo", "")]
    ls = "".join(f'<button type="button" class="reg-l"><span class="t">{t}</span><span class="etq {c}">{e}</span><span>{x}</span>{svg("seta", "ic seta")}</button>'
                 for t, e, x, c in linhas)
    filtros = "".join(f'<button type="button" class="filtro" aria-pressed="{"true" if f == "tudo" else "false"}">{f}</button>'
                      for f in ["tudo", "você", "pet", "lutas", "recusas", "treino"])
    return f'''
<div class="destaque reg-topo"><span class="par"><span class="rot">semente</span><span class="num">7000</span></span>
  <span class="par"><span class="rot">eventos</span><span class="num">76</span></span>
  <span class="linha" style="margin-left:auto"><button type="button" class="bt acao">{svg("replay")}Verificar replay</button>
    <button type="button" class="bt">{svg("copiar")}Copiar registro</button></span></div>
<div class="filtros" role="group" aria-label="Filtrar o registro">{filtros}</div>
<div class="reg" aria-label="O registro, do mais novo ao mais velho">{ls}</div>
<p class="sec">Linhas reconstruídas do registro: 76.</p>
{como("O estado do pet nunca é salvo. Só este registro, e a vida é reconstruída a partir dele. Verificar replay refaz o pet a partir dos eventos e confere se sai o mesmo, até o último decimal.", aberto=True)}
{fechado("x", "Novo ovo (apaga este pet)", "área de risco")}'''


def corpo_catalogo() -> str:
    # formasDoBrasao (TelaCatalogo.tsx): 1 In-Training, 2 Rookies, 4 Champions, 8 Ultimates (2 arquetipos por linha), 4 Megas = 19;
    # os nomes do Amizade em nomes.ts (DIGIMON_DA_FORMA). Vistas: Tsunomon e Gabumon (o caminho deste pet) = 2 de 19.
    def t(nome: str, sub: str = "", visto: bool = False, meu: bool = False) -> str:
        cls = "tile" + (" visto" if visto else " nao-visto") + (" meu" if meu else "")
        cx = spr("parado", .46) if meu else '<span class="sil" aria-hidden="true"></span>'
        lab = nome + (f" · {sub}" if sub else "") + ("" if visto else ", ainda não vista") + (", seu pet" if meu else "")
        etq = '<span class="etq alerta">seu pet</span>' if meu else ""
        sm = f"<small>{sub}</small>" if sub else ""
        return f'<button type="button" role="option" class="{cls}" aria-label="{lab}">{etq}<span class="cx">{cx}</span><span class="nm">{nome}{sm}</span></button>'

    def nivel(rot: str, tiles: str) -> str:
        return f'<div class="cat-nivel"><span class="rot">{rot}</span><div class="cat-grade">{tiles}</div></div>'
    ult = "".join(t(n, a) for n, a in [("WereGarurumon", "Duelista"), ("WereGarurumon", "Furioso"), ("MagnaAngemon", "Espelho"), ("MagnaAngemon", "Muralha"),
                                       ("Silphymon", "Sentinela"), ("Silphymon", "Emboscador"), ("Angewomon", "Vigia"), ("Angewomon", "Titã")])
    brs = "".join(f'<button type="button" class="brasao" aria-pressed="{"true" if b == "Amizade" else "false"}">{svg("brasao")}{b}</button>'
                  for b in ["Coragem", "Amizade", "Conhecimento", "Sinceridade"])
    return f'''
<div class="brasoes" role="group" aria-label="Brasão">{brs}</div>
<div class="destaque linha" role="status"><span class="num">2</span><span>de 19 formas vistas <span class="sec">· vista = por onde este pet passou</span></span></div>
<div role="listbox" aria-label="Formas do brasão" style="display:flex;flex-direction:column;gap:10px">
{nivel("In-Training · Rookie", t("Tsunomon", visto=True) + t("Patamon") + t("Gabumon", visto=True, meu=True))}
{nivel("Champion", "".join(t(n) for n in ["Garurumon", "Angemon", "Aquilamon", "Gatomon"]))}
{nivel("Ultimate", ult)}
{nivel("Mega", "".join(t(n) for n in ["MetalGarurumon", "Seraphimon", "Valkyrimon", "Magnadramon"]))}
</div>
{fechado("lutar", "Técnicas e passivas", "4 técnicas · 8 passivas")}
{como("Cada brasão percorre a mesma árvore: 1 In-Training, 2 Rookies, 4 Champions, 4 Ultimates e 4 Megas. Toque numa forma para ver a ficha: os 6 stats, vida, guts, técnica e passiva.")}'''


# ---------------------------------------------------------------------------------------------------- Ajustes (nao e lugar)
def corpo_ajustes() -> str:
    def aj(ic: str, tit: str, res: str, dir_: str = "", cls: str = "") -> str:
        d = dir_ or svg("seta")
        return f'<button type="button" class="aj {cls}">{svg(ic)}<span><b>{tit}</b><small>{res}</small></span>{d}</button>'
    sw = lambda on: f'<span class="interruptor{" on" if on else ""}" role="switch" aria-checked="{"true" if on else "false"}"></span>'
    vis = '<span class="so-militar">pele Militar</span><span class="so-vidro">pele Sci-fi</span> · tema do sistema · mapa ilha · Normal'
    return f'''
<span class="rot aj-sec">Jogo</span>
{aj("olho", "Visual", vis)}
{aj("dica", "Mostrar dicas", "o Professor Agumon explica cada coisa nova, uma vez", sw(False))}
{aj("estado", "Exibir detalhes do pet", "os painéis Estado atual, Evolução e Últimas ações", sw(True))}
{aj("camera", "Viagem da câmera", "NOVO · desligada, os lugares abrem num corte seco", sw(True), "novo")}
<span class="rot aj-sec">Fala e som</span>
{aj("conversar", "Fala do pet", "modo frases prontas")}
{aj("som", "Som do jogo", "golpes, impactos e o efeito da evolução", sw(False))}
<span class="rot aj-sec">Dados</span>
{aj("registro", "Registro e replay", "semente 7000 · 76 eventos · exportar")}
{aj("acoes", "Tempo", "velocidade 10 min/s", '<span class="etq alerta">teste</span>')}
<span class="rot aj-sec">Laboratório e sobre</span>
{aj("frasco", "Laboratório", "desligado · o jogo é o de hoje", '<span class="etq alerta">experimental</span>')}
{aj("info", "Sobre o Digilab", "versão, créditos e procedência")}'''


# ---------------------------------------------------------------------------------------------------- as telas
def transicao_1() -> str:
    """quadro a: a ilha normal, com a HUD, e o clique em Crescer (ou no lugar do minimapa)"""
    return (cab("abrir um lugar, quadro 1") + mundo("ilha", pet(1160, 400, "parado")) + topo() + trilho("pet", "crescer") + pilha() + dock() + minimapa()
            + '<svg class="cursor" style="left:62px;top:182px" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 2l17 9-7 2-3 7z"/></svg>'
            + nota("1 · a ilha de hoje. O clique em Crescer (ou tecla C, ou o saco no minimapa) leva a câmera ao saco", 100, 166, 260)
            + nota("o portão da arena e a barraca do Tamer: OBJETOS NOVOS, desenho provisório (as cores são amostras do próprio fundo)", 1340, 420, 300)
            + nota("o minimapa (de outra sessão; aqui só contexto) no lugar do botão DigiBrain, que vai ao leque do retrato", 1440, 650, 230)
            + nota("lugar trancado: a Fronteira, apagada, tracejada e com cadeado. Abre com as 6 medalhas (MapaExploracao.tsx, liga.ts)", 1380, 836, 290)
            + nota("Ajustes sai do trilho: vai ao leque do retrato (tela ajustes)", 100, 392, 220)
            + "</body></html>\n")


def transicao_2() -> str:
    """quadro b: a camera a caminho, o pet andando, a HUD recolhendo"""
    x, y = tela(1000, 270, "viagem")
    return (cab("abrir um lugar, quadro 2") + mundo("viagem", pet(1130, 470, "andando", virado=True)) + topo() + trilho("crescer")
            + pilha("saindo-dir") + dock("saindo-baixo") + minimapa("crescer", "viagem")
            + placa("saco", "Saco de pancada", x, y - 70, "chegando")
            + '<span class="caixa pular" role="status">indo ao saco de pancada · <kbd>Esc</kbd> ou clique para pular</span>'
            + nota("2 · a câmera a caminho: 700 ms (PROPOSTO, SEM FONTE), ease-out; o pet anda até o saco (só vista, nada entra no registro)", 100, 410, 300)
            + nota("a pilha e o dock recolhem junto com a câmera; o topo, o trilho e o minimapa ficam", 1500, 330, 260)
            + nota("reduzir movimento: sem viagem e sem o pet andando; corte seco para o quadro 3 (UI_GUIDELINES 11)", 640, 820, 320)
            + "</body></html>\n")


def _crescer(ativa: str, corpo: str, notas: str, foco: str = "", dica: str = "", titulo: str = "") -> str:
    px, py = tela(1035, 285, "saco")
    return (cab(titulo) + mundo("saco", pet(870, 505, "treino") if ativa == "treinar" else mundo_pet_saco()) + topo(agora=False) + trilho("crescer") + minimapa("crescer", "saco")
            + placa("saco", "Saco de pancada", px - 30, py - 112)
            + conector("M792 392 L836 392 L880 330", 792, 392)
            + painel("crescer", ativa, corpo, 880, 84, 600, foco, ("treinar",) if ativa != "treinar" else (), dica)
            + notas + "</body></html>\n")


def mundo_pet_saco() -> str:
    return pet(870, 505, "parado")


def transicao_3() -> str:
    return _crescer("treinar", corpo_treinar(),
                    nota("3 · chegou: o painel entra ao lado do saco (180 ms, ease-out: o 'card entrando' do guia, seção 11)", 1500, 96, 300)
                    + nota("a ilha continua viva em volta: o painel tem 600 px, um terço da tela, e não escurece a cena", 1500, 150, 300),
                    titulo="abrir um lugar, quadro 3")


def crescer_treinar() -> str:
    return _crescer("treinar", corpo_treinar(),
                    nota("o treino pronto em destaque (o único amarelo da tela); textos de TelaTreinar.tsx", 1490, 168, 260)
                    + nota("+2/+1, o selo da aptidão em Alvo e Meditar e a legenda: CTR, APTIDAO.cirro (constantes.ts)", 1490, 300, 260)
                    + nota("marcas 40/60 e 30/60: CTR.limiarPausa, CTR.limiteForcar, CSO.aviso, CSO.sombrio. Fadiga 20, 07:31 e +3,1: EXEMPLO", 1490, 520, 260)
                    + nota("as abas em ícones; só a ativa tem rótulo. 1-4 trocam de aba; Esc volta à ilha", 1490, 120, 260)
                    + nota("o pet treinando no saco (o CENA.treino de hoje já põe o pet ali: só vista)", 380, 820, 300),
                    titulo="Crescer · Treinar")


def crescer_evolucao() -> str:
    return _crescer("evolucao", corpo_evolucao(),
                    nota("o que falta em destaque: a medalha (CMD.adolescente = 1; o texto é o textoFalta de tamer.ts), com o atalho para a luta", 1490, 236, 270)
                    + nota("os Champions sem nome e com '?': a forma futura não decidida pelo motor (TelaEvolucao.tsx, guia 5); o eixo de CAT.adolescente", 1490, 500, 270)
                    + nota("o foco do teclado na aba Itens: o rótulo aparece na dica. O losango amarelo em Treinar = o treino está pronto", 1490, 112, 270)
                    + nota("1d 4h: EXEMPLO (m.dur e o relógio do pet)", 1490, 190, 270),
                    foco="itens", dica="chips e cartas", titulo="Crescer · Evolução")


def _lutar(ativa: str, corpo: str, notas: str, titulo: str, foco: str = "", dica: str = "") -> str:
    px, py = tela(1600, 482, "portao")
    return (cab(titulo) + mundo("portao", pet(1600, 792, "parado")) + topo(agora=False) + trilho("lutar") + minimapa("lutar", "portao")
            + placa("portao", "Portão da arena", px, py - 62)
            + conector("M1362 560 L1330 520 L1300 520", 1362, 560)
            + painel("lutar", ativa, corpo, 690, 84, 610, foco, (), dica)
            + notas + "</body></html>\n")


def lutar_arena() -> str:
    return _lutar("arena", corpo_arena(),
                  nota("a luta que libera medalha em destaque: a 1ª medalha (Campina, Gazimon) libera o Champion (medalhas.ts, CMD, tamer.ts)", 1316, 210, 280)
                  + nota("os rivais: luta.ts, nomesRivais.ts, bots.ts (NOME_BOT). Monochromon escolhido: EXEMPLO", 1316, 400, 280)
                  + nota("a aba Fronteira trancada: apagada, tracejada, cadeado; o motivo na dica (foco) e no aria-label", 1316, 150, 280)
                  + nota("PORTÃO DA ARENA: objeto novo, desenho provisório, no fim do caminho de terra", 1620, 296, 230),
                  "Lutar · Arena", foco="fronteira", dica="abre com as 6 medalhas (0 de 6)")


def lutar_medalhas() -> str:
    return _lutar("medalhas", corpo_medalhas(),
                  nota("a próxima medalha em destaque, com o líder, a regra da arena e o que ela dá (medalhas.ts, arenas.ts, itens.ts)", 1316, 230, 280)
                  + nota("as outras recuam: uma linha cada; só as que liberam um nível dizem o quê (TelaMedalhas.tsx, libera)", 1316, 470, 280)
                  + nota("0 de 6: EXEMPLO (o registro do Tamer)", 1316, 140, 280)
                  + nota("o Gazimon: o quadro 0,0 da folha dele (6 x 6), sem px conhecidos; conferir na captura", 1316, 330, 280),
                  "Lutar · Medalhas")


def _diario(ativa: str, corpo: str, notas: str, titulo: str) -> str:
    px, py = tela(269, 430, "barraca")
    return (cab(titulo) + mundo("barraca", pet(515, 712, "parado", virado=True)) + topo(agora=False) + trilho("diario") + minimapa("diario", "barraca")
            + placa("barraca", "Barraca do Tamer", px, py - 70)
            + conector("M430 456 L600 330 L800 330", 430, 456)
            + painel("diario", ativa, corpo, 800, 84, 620)
            + notas + "</body></html>\n")


def diario_registro() -> str:
    return _diario("registro", corpo_registro(),
                   nota("o 'como funciona' aberto (o único quadro em que ele aparece aberto)", 1436, 640, 250)
                   + nota("as linhas são as do _hist do motor (motor.ts) e NOME_PET; 'regras' é aprendido: tracejado ciano. Horas, semente 7000 e 76 eventos: EXEMPLO", 1436, 330, 260)
                   + nota("BARRACA DO TAMER: objeto novo, desenho provisório, junto ao barranco", 100, 850, 240),
                   "Diário · Registro")


def diario_catalogo() -> str:
    return _diario("catalogo", corpo_catalogo(),
                   nota("19 formas do Amizade (formasDoBrasao, nomes.ts); vistas = o caminho deste pet: 2 de 19", 1436, 200, 260)
                   + nota("seu pet em destaque; as não vistas: no jogo, a silhueta do atlas (aqui só o lugar dela)", 1436, 380, 260)
                   + nota("a ficha (stats, vida, guts) abre por toque numa forma, como hoje (Folha)", 1436, 560, 260),
                   "Diário · Catálogo")


def ajustes() -> str:
    lq = (f'<div class="caixa leque" role="menu" aria-label="Retrato"><button type="button" role="menuitem">{svg("pet")}Meus pets</button>'
          f'<button type="button" role="menuitem">{svg("digibrain")}DigiBrain</button>'
          f'<button type="button" role="menuitem" aria-expanded="true">{svg("ajustes")}Ajustes</button></div>')
    corpo = corpo_ajustes()
    pn = f'''<section class="caixa lp" style="left:100px;top:128px;width:540px" aria-labelledby="aj-tit">
  <div class="lp-cab" style="padding-bottom:8px">{svg("ajustes")}<span class="lp-tit"><b id="aj-tit">Ajustes</b><small>pelo retrato; não é um lugar da ilha</small></span>
    <button type="button" class="bt-ic bt-fechar" aria-label="Fechar os Ajustes" aria-keyshortcuts="Escape">{svg("x")}<kbd aria-hidden="true">Esc</kbd></button></div>
  <div class="lp-corpo" style="gap:6px;border-top:1px solid var(--hx-borda)">{corpo}</div></section>'''
    return (cab("Ajustes") + mundo("ilha", pet(1160, 400, "parado")) + topo(leque=True) + trilho("pet") + pilha() + dock() + minimapa()
            + lq + pn
            + nota("o retrato abre um leque: Meus pets (o de hoje), DigiBrain (sai do canto, por causa do minimapa) e Ajustes", 470, 74, 300)
            + nota("Ajustes não é lugar: a câmera não se mexe, o painel desce do retrato e a ilha fica como está", 660, 300, 260)
            + nota("a lista e os resumos são os de TelaConfig.tsx; 'Viagem da câmera' é NOVA (preferência de tela, não de jogo)", 660, 420, 260)
            + nota("Visual, semente 7000, 76 eventos e 10 min/s: EXEMPLO da captura de hoje", 660, 560, 260)
            + "</body></html>\n")


TELAS = {
    "transicao_1": transicao_1, "transicao_2": transicao_2, "transicao_3": transicao_3,
    "crescer_treinar": crescer_treinar, "crescer_evolucao": crescer_evolucao,
    "lutar_arena": lutar_arena, "lutar_medalhas": lutar_medalhas,
    "diario_registro": diario_registro, "diario_catalogo": diario_catalogo,
    "ajustes": ajustes,
}

if __name__ == "__main__":
    d = Path(__file__).parent
    for nome, f in TELAS.items():
        (d / f"{nome}_1920.html").write_text(f(), encoding="utf-8", newline="\n")
