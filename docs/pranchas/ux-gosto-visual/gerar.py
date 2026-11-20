# Gera a prancha "o pet assistindo TV" (docs/PLANO_UX_GOSTO_VISUAL.md; UX-GV-1 a 10 aprovadas pelo Matheus em 2026-11-11: "Sim, segue a
# prancha"). So desenho; nenhum codigo do jogo. Usa os ajudantes da prancha dos lugares (../ux-lugares-menus/gerar.py: os icones, o pet, a
# amostra do fundo, a nota) e os tokens de la (lugares.css); o que e novo esta em tv.css.
# A pele vem de ?pele=vidro|xcom no endereco, e ?sem tira as notas amarelas.
# Uso (da raiz): python docs/pranchas/ux-gosto-visual/desenhar_tv.py   (as imagens da TV, em img/; so quando o tv.py muda)
#                python docs/pranchas/ux-gosto-visual/gerar.py         (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# O FUNDO e o da prancha dos lugares (img/cena_sem_pet.jpg: uma captura do jogo de 2026-11-06, de dia, sem HUD). O cantinho de verdade
# fica perto da barraca do Tamer (#814 e #820); aqui ele esta sobre outro trecho de grama, so para o enquadramento. O tapete e as
# almofadas sao amostras do proprio fundo (sem cor nova); no jogo, as cores sao as do cantinhoTv.ts.
# A TV e o modelo do #814 (docs/objetos3d/cartoon/tv.py), desenhado pelo desenhar_tv.py na inclinacao da camera.
# O PET e o Agumon (Rookie), o sprite de Assets/arena_up (fora do git). As poses das reacoes sao o mesmo quadro deslocado ou virado:
# no jogo, sao as do cantinhoTv.ts (#820).
#
# DE ONDE VEM CADA TEXTO E NUMERO:
#   as seis reacoes ................. web/app/src/gostoVisual/gosto.ts (Reacao) e estadoTv.ts (BALAO); as frases em palavras sao do plano (5.1)
#   "Gosta mais de" ................. gosto.ts, gostaMaisDe e PALAVRAS ("cores vivas", "som constante", ...); os extremos dos trilhos tambem
#   os sete componentes ............. gosto.ts, COMPONENTES e NOME_COMPONENTE (cor, brilho, movimento, detalhe, volume, ritmo, timbre)
#   de nascenca / de tanto ver / do carinho ... gosto.ts: Inato.otimo, EstadoGosto.exposicao e EstadoGosto.carinho (ja separados no P0)
#   o que esta passando ............. estadoTv.ts (origem, programa) e tvDoJogo.ts (PROGRAMAS: "desenho colorido e agitado", ...)
#   o tempo junto ................... gosto.ts, tempoJunto(EstadoGosto.segundosJuntos)
#   a frase da privacidade .......... o plano, 3.2 (a regra e a da ideia, docs/futuro/gosto_visual_pet.md, secoes 7 e 14)
# EXEMPLO DE LAYOUT, NUNCA DADO: as posicoes das marcas nos trilhos, "2 h 10 min", "D3 07:42", o pet e o programa escolhidos.
# Nenhum numero de jogo novo. Os tamanhos e os tempos de interface sao PROPOSTO, SEM FONTE.
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "ux-lugares-menus"))
import gerar as G  # noqa: E402

IC = {
    "tv": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 2l4 5 4-5"/>',
    "parar": '<rect x="6" y="6" width="12" height="12" rx="1"/>',
    "coracao": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "interrog": '<path d="M9 9a3 3 0 1 1 4.5 2.6c-1 .6-1.5 1.2-1.5 2.4"/><path d="M12 18v.5"/>',
    "bocejo": '<circle cx="6" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="18" cy="12" r="1"/>',
    "janela": '<rect x="3" y="4" width="18" height="16" rx="1"/><rect x="12" y="11" width="7" height="7"/>',
    "tela": '<rect x="3" y="4" width="18" height="12" rx="1"/><path d="M8 20h8M12 16v4"/>',
    "som_off": '<path d="M4 9v6h4l5 4V5L8 9z"/><path d="M17 9l4 6M21 9l-4 6"/>',
}


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else G.svg(n, cls)


def cab(titulo: str, w: int, h: int) -> str:
    return f'''<!doctype html><html lang="pt-BR" style="width:{w}px;height:{h}px"><head><meta charset="utf-8"><meta name="viewport" content="width={w}">
<title>O pet assistindo TV · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600;700;800;900&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="../ux-lugares-menus/lugares.css">
<link rel="stylesheet" href="tv.css">
<style>:root{{--assets-spr:url("{G.A}/sprites/Agumon.png")}}</style>
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.pele=q.get("pele")==="xcom"?"xcom":"vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body style="width:{w}px;height:{h}px">'''


FIM = "</body></html>\n"

# ---------------------------------------------------------------------------------------------------- a cena: o cantinho da TV
# o centro do cantinho no fundo (as coordenadas da captura de 1920 x 931)
CX, CY = 640, 440
SINAL = {"adorando": "coracao", "curioso": "interrog", "enjoou": "bocejo", "nao_gosta": "x"}   # "olhando" e "distraido" nao tem sinal
# o sprite do Agumon olha para a esquerda; "virado" o poe olhando para a TV (a direita). No "enjoou" e no "nao curti" ele desvira
POSE = {"adorando": "virado pulo", "curioso": "virado inclina", "enjoou": "", "nao_gosta": "", "distraido": "longe", "olhando": "virado"}
PALAVRA = {"adorando": "Está adorando", "olhando": "Está assistindo", "curioso": "Ficou curioso", "enjoou": "Enjoou disso",
           "nao_gosta": "Não curtiu", "distraido": "Não está prestando atenção"}


def cantinho(tv: str = "tv_34_ligada", reacao: str | None = "adorando", sentado: bool = True, sinal: bool = True) -> str:
    """o tapete, as duas almofadas, a TV e o pet (com a pose e o sinal da reacao), nas coordenadas do fundo"""
    o = G.sombra_chao(CX - 175, CY + 6, 350, 96, .22)
    o += G.parte("vermelho", CX - 165, CY, 330, 86, extra="border-radius:50%;z-index:2;opacity:.9")
    o += G.parte("areia", CX - 132, CY + 8, 264, 68, extra="border-radius:50%;z-index:2;opacity:.55")
    o += G.parte("pedra", CX - 118, CY + 16, 92, 36, extra="border-radius:50%;z-index:3")      # a almofada do pet
    o += G.parte("faixa", CX - 40, CY + 44, 84, 32, extra="border-radius:50%;z-index:3")       # a almofada do dono, vazia
    o += f'<img class="tv-img" src="img/{tv}.png" alt="" style="left:{CX + 40}px;top:{CY - 150}px;width:210px;height:210px">'
    if sentado:
        cls = POSE.get(reacao or "olhando", "")
        o += G.pet(CX - 72, CY + 36, "parado", 1.25, nome="Agumon").replace('class="pet', f'class="pet {cls}' if cls else 'class="pet')
        if sinal and reacao in SINAL:
            o += f'<span class="sinal" style="left:{CX - 91}px;top:{CY - 104}px">{ic(SINAL[reacao])}</span>'
    return o


def mundo(cam: tuple, dentro: str) -> str:
    s, ox, oy = cam
    return (f'<div class="mundo" style="--s:{s};--ox:{ox};--oy:{oy}" role="img" aria-label="A ilha, com o cantinho da TV (o fundo é uma captura real '
            f'do jogo; o cantinho é desenho)">{dentro}</div>')


def cam(s: float, cx_tela: float, cy_tela: float) -> tuple:
    """a camera que poe o centro do cantinho no ponto (cx, cy) da tela"""
    return (s, round(CX * s - cx_tela), round((CY - 20) * s - cy_tela))


# ---------------------------------------------------------------------------------------------------- a HUD de contexto
def topo(w: int) -> str:
    return (f'<div class="caixa t-topo">{G.svg("pet")}<span>Agumon</span><small>Rookie</small></div>'
            f'<div class="caixa t-relogio" style="right:14px" aria-hidden="true">D3 07:42</div>')


def trilho() -> str:
    its = "".join(f'<span class="{"at" if n == "pet" else ""}">{G.svg(n)}</span>' for n in ("pet", "crescer", "lutar", "diario", "conversar", "ajustes"))
    return f'<nav class="caixa t-trilho" aria-label="Navegação (a de hoje, sem item novo)">{its}</nav>'


def dock(carinho: bool = False) -> str:
    its = "".join(f'<span class="{"dest" if (carinho and n == "Carinho") else ""}">{n}</span>'
                  for n in ("Alimentar", "Brincar", "Limpar", "Carinho", "Tapa", "Tratar", "Mais"))
    return f'<div class="caixa t-dock" role="toolbar" aria-label="Ações (as de hoje)">{its}</div>'


def selo(x_css: str, texto: str = "Vendo a sua tela", extra: str = "") -> str:
    return (f'<div class="caixa cap-selo" style="{x_css}{extra}" role="status"><i aria-hidden="true"></i><span>{texto}</span>'
            f'<button type="button" class="tb p">{ic("parar")}Parar</button></div>')


def pilha(tv_aberta: bool = False) -> str:
    return (f'<div class="t-pilha"><div class="caixa">{G.svg("estado")}Estado atual</div><div class="caixa">{G.svg("evolucao")}Evolução</div>'
            f'<div class="caixa">{G.svg("acoes")}Últimas ações</div><button type="button" class="caixa tv-bt">{ic("tv")}TV</button></div>')


# ---------------------------------------------------------------------------------------------------- o painel da TV
# (nome, extremo esquerdo, extremo direito, nascenca, de tanto ver, do carinho, agora), de 0 a 100; exemplo de layout
LINHAS_IMG = [("Cor", "cores suaves", "cores vivas", 30, 24, 13, 82), ("Brilho", "imagens escuras", "imagens claras", 55, 6, 0, 70),
              ("Movimento", "cenas calmas", "muito movimento", 64, -10, 0, 78), ("Detalhe", "cenas simples", "cheias de detalhe", 48, 3, 0, 60)]
LINHAS_SOM = [("Volume", "som baixinho", "som alto", 40, 5, 0, 68), ("Ritmo", "som constante", "ritmo agitado", 18, 4, 0, 72),
              ("Timbre", "sons graves", "sons agudos", 52, -4, 6, 58)]


def linha(l: tuple, agora: bool = False) -> str:
    nome, esq, dir_, nasc, ver, car, ag = l
    hoje = nasc + ver + car
    partes = [f'<i class="m-nasc" style="left:{nasc}%"></i>']
    if ver:
        a, b = sorted((nasc, nasc + ver))
        partes.append(f'<i class="m-ver {"dir" if ver > 0 else "esq"}" style="left:{a}%;width:{b - a}%"></i>')
    if car:
        a, b = sorted((nasc + ver, hoje))
        partes.append(f'<i class="m-car" style="left:{a}%;width:{b - a}%"></i>')
    partes.append(f'<i class="m-agora" style="left:{ag}%"></i>' if agora else f'<i class="m-hoje" style="left:{hoje}%"></i>')
    de = [f"de nascença, {nasc} de 100"] + ([f"mudou {abs(ver)} de tanto ver"] if ver else []) + ([f"mudou {abs(car)} com o carinho"] if car else [])
    rot = f"{nome}: agora, {ag} de 100" if agora else f"{nome}: {'; '.join(de)}; hoje, {hoje} de 100"
    so = "".join(partes) if not agora else partes[-1]
    return (f'<div class="gl" role="img" aria-label="{rot} (de {esq} a {dir_})"><b>{nome}</b><div class="gl-trilho">{so}</div>'
            f'<div class="gl-ext"><span>{esq}</span><span>{dir_}</span></div></div>')


LEGENDA = ('<p class="leg"><span><i><i class="m-nasc"></i></i>de nascença</span><span><i><i class="m-ver dir"></i></i>de tanto ver</span>'
           '<span><i><i class="m-car"></i></i>do carinho</span><span><i><i class="m-hoje"></i></i>hoje</span></p>')
PRIV = (f'<p class="priv">{G.svg("cadeado")}<span>Ele só sente cores, brilho, movimento e som: sete números por segundo. Nenhuma imagem é guardada e '
        f'nada sai deste computador.</span></p>')


def sec_agora(origem: str, reacao: str, motivo: str, janela: bool = True) -> str:
    j = f'<button type="button" class="tb">{ic("janela")}Janela pequena</button>' if janela else ""
    return (f'<div class="tvp-sec"><p class="fraco">Passando: {origem}</p>'
            f'<p class="forte-txt" role="status">{PALAVRA[reacao]}{": " + motivo if motivo else "."}</p>'
            f'<div class="linha-bts"><button type="button" class="tb">{ic("parar")}Parar</button>{j}</div></div>')


def sec_ligar(com_tela: bool = True) -> str:
    t = f'<button type="button" class="tb cheio">{ic("tela")}Mostrar minha tela</button>' if com_tela else ""
    return (f'<div class="tvp-sec"><button type="button" class="tb forte cheio">{ic("tv")}Ligar a TV</button>{t}{PRIV if com_tela else ""}</div>')


def sec_gosto(porque: str = "", passando: str = "", nasc: bool = True) -> str:
    n = '<p class="fraco">De nascença, preferia cores suaves.</p>' if nasc else ""
    p = (f'<button type="button" class="abre {"aberto" if porque else ""}" aria-expanded="{"true" if porque else "false"}">{G.svg("seta")}Por quê</button>{porque}')
    a = (f'<button type="button" class="abre {"aberto" if passando else ""}" aria-expanded="{"true" if passando else "false"}">{G.svg("seta")}O que está passando</button>{passando}'
         if passando is not None else "")
    return (f'<div class="tvp-sec"><h3>Do que o Agumon gosta</h3><p class="forte-txt">Gosta mais de: cores vivas e som constante.</p>{n}{p}{a}</div>')


def sec_rodape(priv: bool = True) -> str:
    return f'<div class="tvp-sec"><p class="fraco">Assistiram juntos: 2 h 10 min</p>{PRIV if priv else ""}</div>'


def painel(x: str, y: int, w: int, corpo: str, h: str = "") -> str:
    return (f'<section class="caixa tvp" style="{x};top:{y}px;width:{w}px;{h}" aria-labelledby="tvp-tit">'
            f'<div class="tvp-cab">{ic("tv")}<span><b id="tvp-tit">TV</b><small>Cantinho da TV</small></span>'
            f'<button type="button" class="fecha" aria-label="Fechar o painel (a TV continua ligada)" aria-keyshortcuts="Escape">{G.svg("x")}</button></div>'
            f'{corpo}</section>')


PORQUE_CURTO = "".join(linha(l) for l in (LINHAS_IMG[0], LINHAS_SOM[1])) + LEGENDA + '<button type="button" class="tb p">Ver todos</button>'
PORQUE_TODOS = ('<p class="grupo">Imagem</p>' + "".join(linha(l) for l in LINHAS_IMG) + '<p class="grupo">Som</p>' + "".join(linha(l) for l in LINHAS_SOM) + LEGENDA)
PASSANDO = "".join(linha(l, agora=True) for l in (LINHAS_IMG[0], LINHAS_IMG[2], LINHAS_SOM[1]))


# ---------------------------------------------------------------------------------------------------- as telas a 1440 x 900
W, H, PW = 1440, 900, 420
CAM_P = cam(1.6, (W - PW - 16 + 70) / 2, 430)   # o cantinho no meio da parte livre, a esquerda do painel
CAM_L = cam(1.6, W / 2, 440)


def base_1440(cena: str, hud: str, titulo: str, camx: tuple = CAM_P) -> str:
    return cab(titulo, W, H) + mundo(camx, cena) + topo(W) + trilho() + hud + FIM


def desligada_1440() -> str:
    return base_1440(cantinho("tv_34", None, sentado=False), dock()
                     + painel("right:16px", 60, PW, sec_ligar() + sec_gosto(nasc=True, passando=None) + sec_rodape(priv=False))
                     + G.nota("1 · o toque na TV (ou o botão TV da pilha) traz a câmera ao cantinho e abre o painel. A TV está desligada: o pet fica onde o motor diz", 96, 120, 300)
                     + G.nota("UX-GV-6 · a TV do jogo é o botão principal; a tela do dono é o segundo, com a frase fixa da privacidade antes do seletor do Chrome", 700, 150, 290)
                     + G.nota("UX-GV-3 · a TV em três quartos (40°, PROPOSTO): a tela aparece e o pet vai ficar de perfil", 560, 560, 280)
                     + G.nota("o gosto se lê mesmo com a TV desligada; a origem \"de nascença\" vem primeiro", 700, 360, 280), "TV desligada")


def ligada_1440() -> str:
    return base_1440(cantinho(), dock(carinho=True) + selo("left:50%;translate:-50% 0;", extra="margin-left:-218px")
                     + painel("right:16px", 60, PW, sec_agora("a sua tela", "adorando", "tem as cores de que ele gosta.")
                              + sec_gosto(porque=PORQUE_CURTO, passando="") + sec_rodape())
                     + G.nota("UX-GV-1 · o cantinho é a vista; o painel é o controle e a leitura. O cartão do canto sai, e o pet aparece uma vez só", 96, 120, 300)
                     + G.nota("UX-GV-10 · um ícone no lugar do balão de texto, no lugar dos emotes de hoje; a pose (o pulinho) é o sinal principal", 200, 250, 280)
                     + G.nota("UX-GV-6 · o selo da captura, com o Parar, fica fixo nas três vistas", 330, 62, 300)
                     + G.nota("UX-GV-7 · um carinho só: o Carinho do dock (ou o toque no pet)", 470, 800, 280)
                     + G.nota("UX-GV-4 e 5 · a frase primeiro; no porquê, só os componentes marcados. Três origens com forma própria; \"do carinho\" usa a malha ciano tracejada do aprendido com o dono", 700, 470, 300), "TV ligada, a tela do dono")


def porque_1440() -> str:
    return base_1440(cantinho(reacao="curioso"), dock() + painel("right:16px", 60, PW,
                     sec_agora("a TV do jogo, show de música", "curioso", "o som é novo para ele.") + sec_gosto(porque=PORQUE_TODOS, passando="", nasc=False))
                     + G.nota("\"Ver todos\": os sete componentes, em Imagem e Som. Cada linha é uma frase para o leitor de tela", 700, 250, 280)
                     + G.nota("com a TV do jogo não há selo de captura: nada do computador é lido", 330, 62, 300)
                     + G.nota("\"curioso\" inclina a cabeça e mostra a interrogação", 200, 250, 240), "o porquê aberto, a TV do jogo")


def passando_1440() -> str:
    return base_1440(cantinho(reacao="enjoou"), dock() + painel("right:16px", 60, PW,
                     sec_agora("a TV do jogo, planilha", "enjoou", "já viu muito disso.") + sec_gosto(porque="", passando=PASSANDO + '<p class="fraco">O círculo é o que a TV mostra agora.</p>')
                     + sec_rodape(priv=False))
                     + G.nota("\"O que está passando\" fica separado do gosto: em cima é o pet, embaixo é a tela. O leitor de tela não o anuncia a cada segundo", 700, 520, 290)
                     + G.nota("\"enjoou\": o pet vira para o outro lado, com as reticências. A frase diz o porquê em palavras de jogo", 200, 250, 280), "o que está passando")


def fechado_1440() -> str:
    return base_1440(cantinho(reacao="nao_gosta"), dock(carinho=True) + pilha() + selo("left:50%;translate:-50% 0;"),
                     "painel fechado, a TV ligada", CAM_L).replace(FIM, G.nota("fechar o painel (× ou Esc) não desliga a TV: o pet continua assistindo, e o selo com o Parar fica na tela", 500, 62, 320)
                     + G.nota("UX-GV-2 · o botão TV na pilha: o caminho do teclado, e de quem não achou a TV na ilha (só com a chave ligada)", 900, 260, 250)
                     + G.nota("\"não curtiu\": o pet vira para o outro lado, com o x. Sem o painel, a diferença para \"enjoou\" está só no ícone", 330, 520, 280) + FIM)


# ---------------------------------------------------------------------------------------------------- a 900 x 700
def ligada_900() -> str:
    w, h, pw = 900, 700, 340
    return (cab("TV ligada, a 900 px", w, h) + mundo(cam(1.25, (w - pw - 16 + 70) / 2, 340), cantinho()) + topo(w) + trilho()
            + selo("left:210px;") + painel("right:12px", 56, pw, sec_agora("a sua tela", "adorando", "tem as cores de que ele gosta.", janela=True)
                                           + sec_gosto(porque="", passando="") + sec_rodape(priv=False))
            + G.nota("a 900 px o painel é o mesmo, mais estreito; o porquê abre uma linha por componente", 90, 440, 250)
            + G.nota("o dock fica sob o painel quando não cabe: o carinho também é o toque no pet", 90, 600, 250) + FIM)


# ---------------------------------------------------------------------------------------------------- a 390 x 844 (a folha, UX-GV-8)
def cel(titulo: str, cena: str, folha: str, notas: str, selo_: bool = True, cy: float = 250) -> str:
    dk = "".join(f'<span class="{"dest" if n == "Carinho" else ""}">{n}</span>' for n in ("Alimentar", "Brincar", "Limpar", "Carinho", "Mais"))
    s = selo("left:62px;", "Vendo a tela") if selo_ else ""
    return (cab(titulo, 390, 844) + mundo(cam(1.05, 195, cy), cena)
            + f'<div class="caixa t-topo" style="left:8px;top:10px;padding:6px 10px">{G.svg("pet")}</div>{s}'
            + folha + f'<div class="caixa cel-dock" role="toolbar" aria-label="Ações">{dk}</div>' + notas + FIM)


def folha(corpo: str, top: int) -> str:
    return (f'<section class="caixa tvp folha-tv" style="top:{top}px;bottom:64px" role="dialog" aria-labelledby="fo-tit"><span class="alca" aria-hidden="true"></span>'
            f'<div class="tvp-cab" style="padding:6px 14px">{ic("tv")}<span><b id="fo-tit">TV</b></span>'
            f'<button type="button" class="fecha" aria-label="Fechar a folha (a TV continua ligada)">{G.svg("x")}</button></div>{corpo}</section>')


def recolhida_390() -> str:
    corpo = ('<div class="tvp-sec"><p class="forte-txt" role="status">Está adorando: tem as cores de que ele gosta.</p>'
             '<p>Gosta mais de: cores vivas e som constante.</p>'
             f'<button type="button" class="abre" aria-expanded="false">{G.svg("seta")}Mais</button></div>')
    return cel("a folha recolhida", cantinho(), folha(corpo, 568),
               G.nota("UX-GV-8 · uma folha baixa em vez do modal: o pet é o assunto e fica à vista. Recolhida: a reação e o gosto", 12, 470, 250)
               + G.nota("a área de toque do carinho é a almofada inteira (44 px ou mais)", 12, 380, 220)
               + G.nota("sem Janela pequena e sem Mostrar minha tela no celular: o navegador não tem", 150, 60, 230), cy=230)


def aberta_390() -> str:
    corpo = (sec_agora("a TV do jogo, desenho colorido e agitado", "adorando", "tem as cores de que ele gosta.", janela=False)
             + sec_gosto(porque=PORQUE_CURTO, passando=None))
    return cel("a folha esticada", cantinho(), folha(corpo, 330),
               G.nota("\"Mais\" estica a folha até cerca de meia tela (PROPOSTO, SEM FONTE); a câmera sobe o cantinho", 12, 250, 240), selo_=False, cy=170)


def desligada_390() -> str:
    corpo = sec_ligar(com_tela=False) + '<div class="tvp-sec"><p>Gosta mais de: cores vivas e som constante.</p></div>'
    return cel("a TV desligada no celular", cantinho("tv_34", None, sentado=False), folha(corpo, 600),
               G.nota("no celular só a TV do jogo: nenhum botão que falha ao tocar", 12, 500, 230), selo_=False, cy=240)


# ---------------------------------------------------------------------------------------------------- a janela pequena (360 x 620)
def janela() -> str:
    return (cab("a janela pequena", 360, 620) + '<div class="jp">' + selo("", extra="")
            + f'<div class="jp-palco"><span class="caixa jp-balao" role="status">Está adorando</span>{G.pet(0, 0, "parado", 1.9, nome="Agumon").replace("left:", "x:").replace("top:", "y:")}</div>'
            + '<p>Gosta mais de: cores vivas e som constante.</p>'
            + f'<div class="linha-bts"><button type="button" class="tb forte">{G.svg("mao")}Carinho</button><button type="button" class="tb">{ic("parar")}Parar</button></div></div>'
            + FIM)


# ---------------------------------------------------------------------------------------------------- as reacoes e o giro
def quadro(cena: str, rot: str, sub: str, camx: tuple, selo_q: str = "", veu: bool = False) -> str:
    sq = f'<span class="caixa selo-q">{selo_q}</span>' if selo_q else ""
    return f'<div class="quadro">{mundo(camx, cena)}{"<i class=veu></i>" if veu else ""}{sq}<div class="rot"><b>{rot}</b><small>{sub}</small></div></div>'


def reacoes() -> str:
    c = cam(1.25, 225, 200)
    sub = {"adorando": "pula de leve · um coração", "olhando": "sentado, de frente para a TV · sem sinal", "curioso": "inclina a cabeça · uma interrogação",
           "enjoou": "vira para o outro lado · reticências", "nao_gosta": "vira para o outro lado · um x", "distraido": "olha em volta · sem sinal"}
    qs = "".join(quadro(cantinho(reacao=r), PALAVRA[r], sub[r], c) for r in ("adorando", "olhando", "curioso", "enjoou", "nao_gosta", "distraido"))
    return (cab("as seis reações", W, H) + '<p class="titulo-p">As seis reações: a pose, o sinal e as palavras<small>UX-GV-10 · a pose é o sinal principal; '
            'o ícone fica no lugar dos emotes de hoje; as palavras ficam no painel e no leitor de tela. A fila: chamado, fala do jogo, emote do jogo, sinal da TV. '
            'O sinal só muda quando a reação muda, e dura pelo menos 3 s (PROPOSTO, SEM FONTE)</small></p>'
            + f'<div class="quadros" style="top:110px;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr)">{qs}</div>'
            + G.nota("as poses aqui são o mesmo quadro do sprite, deslocado ou virado; no jogo são as do cantinho (#820)", 980, 60, 300) + FIM)


def giro() -> str:
    c = cam(1.5, 225, 300)
    qs = (quadro(cantinho("tv_lado_ligada", "olhando"), "Hoje: a TV de lado", "a tela olha para o oeste e a câmera olha do sul: a imagem não aparece", c, "hoje")
          + quadro(cantinho("tv_frente_ligada", "olhando"), "(a) A TV de frente", "a imagem aparece, mas o pet teria de ficar de costas: o sprite não tem costas, e a reação some", c, "descartada", veu=True)
          + quadro(cantinho("tv_34_ligada", "adorando"), "(c) A TV em três quartos", "40° para o sul (PROPOSTO): a imagem aparece e o pet continua de perfil, olhando para ela", c, "UX-GV-3 · aprovada"))
    return (cab("o giro da TV", W, H) + '<p class="titulo-p">O giro da TV e o enquadramento<small>UX-GV-3 · o giro vale sempre, com ou sem a chave; '
            'a almofada e o tapete giram junto. Ao abrir o lugar, a câmera só anda até o cantinho e aproxima</small></p>'
            + f'<div class="quadros" style="top:90px;grid-template-columns:repeat(3,1fr)">{qs}</div>' + FIM)


TELAS = {
    "desligada_1440": desligada_1440, "ligada_1440": ligada_1440, "porque_1440": porque_1440, "passando_1440": passando_1440, "fechado_1440": fechado_1440,
    "ligada_900": ligada_900, "recolhida_390": recolhida_390, "aberta_390": aberta_390, "desligada_390": desligada_390,
    "janela_360": janela, "reacoes_1440": reacoes, "giro_1440": giro,
}

if __name__ == "__main__":
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")
