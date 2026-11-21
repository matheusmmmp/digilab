# Gera a prancha "peles de rua: tres modelos base" (docs/PLANO_UX_PELES_RUA.md). So desenho; nenhum codigo do jogo.
# O pedido do Matheus (2026-11-20), com 15 imagens de referencia: "olhe as pranchas que temos referente aos novos modelos de layout, que e
# o vidro e o militar [...]. E dai projete uma nova UI pensando numa estetica mais com esse traco de desenho, com retas, cores fortes,
# colagem e street art, algo moderno", e "Gere 3 modelos bases diferentes".
#
# COMO UMA PELE E FEITA NO JOGO (lido em web/app/src/estilo, 2026-11-20): um bloco de tokens --hx-* e --hud-* por pele em tokens.css
# (o Militar em :root, o Vidro em :root[data-pele="vidro"]) e um arquivo de forma por pele (pele-xcom.css, 56 linhas; pele-vidro.css,
# 188). O DOM nao muda. Esta prancha segue o mesmo corte: base.css e o esqueleto (igual nos tres), o bloco de tokens de cada modelo sai
# do dicionario MODELOS abaixo, e a forma de cada um esta em estencil.css, zine.css e arcade.css.
#
# Uso (da raiz): python docs/pranchas/ux-peles-rua/gerar.py   (escreve os HTML ao lado e recorta os sprites em _spr/, fora do git)
# Precisa do Pillow e de D:\Trab\digilab\Assets (o atlas de clipes, fora do git). ?sem tira as notas amarelas.
#
# O QUE E REAL E O QUE E EXEMPLO:
#   as telas e as pecas ............. as da tela do pet de hoje (TelaPet.tsx: o topo, o trilho, as janelas, o aviso, o dock, o minimapa)
#                                      e o lugar Crescer > Treinar (TelaTreinar.tsx: os seis exercicios e os ganhos de cada um)
#   os nomes ........................ os do jogo: Agumon, Rookie, Coragem; Elogiar e Repreender (#912); os seis exercicios
#   a semantica das cores ........... a do UI_GUIDELINES, secao 3: necessidade (rosa), aprendido (ciano), alerta, perigo, ok
#   o pet ........................... o primeiro quadro do clipe Idle do atlas de clipes (digilab_atlas_up_clipes), o que o jogo usa
#   o fundo ......................... uma captura do jogo de 2026-11-20, sem a HUD (img/cena_1920.jpg)
#   EXEMPLO DE LAYOUT, NUNCA DADO ... os valores dos medidores, as horas, os Bits, "Tamer Nv 4", a fala do pet, o porque do agora
# Nenhum numero de jogo novo. AS CORES E AS DUAS FONTES NOVAS SAO PROPOSTAS: uma pele nova pede valores novos para os tokens.
import importlib.util
import json
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).parent
ASSETS = AQUI.parents[3] / "Assets"
_esp = importlib.util.spec_from_file_location("gerar_lugares", AQUI.parent / "ux-lugares-menus" / "gerar.py")
G = importlib.util.module_from_spec(_esp)
_esp.loader.exec_module(G)   # so os icones (G.svg)
svg = G.svg

FONTES = ("https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@500;600;700&family=Saira+Stencil+One&family=Barlow:wght@500;600;700;800"
          "&family=Rubik:ital,wght@0,500;0,700;0,800;0,900;1,700;1,800;1,900&family=DotGothic16&family=Bungee&display=swap")

# ---------------------------------------------------------------------------------------------------- os tres modelos: os tokens
# cada token: (valor, o papel na folha do modelo ou None). Os nomes sao os de tokens.css; os NOVOS estao marcados no plano (secao 4).
MODELOS = {
    "estencil": dict(
        n=1, nome="Estêncil", curto="cartaz de rua",
        frase="Cartaz de rua: tinta, osso e vermelhão, cortes em 45° e letra vazada. É o Militar que virou pôster.",
        letras="Saira Stencil One (nova) nos títulos; Saira Condensed nos rótulos e nos números; Barlow no texto.",
        tracos=["a caixa escura com contorno de osso e os cantos cortados em 45°", "a sombra dura, preta, de 5 px",
                "botões e abas em paralelogramo", "o índice em vermelhão e as riscas de sinalização"],
        tokens={
            "--chao": ("#0E0F12", None), "--hx-chao-ink": ("#F0EADB", None),
            "--hx-miolo": ("#17191F", "tinta: o fundo das caixas"), "--hx-miolo-2": ("#262933", "tinta clara: teclas e cartões"),
            "--hx-borda": ("#F0EADB", "osso: o contorno e o texto"),
            "--hx-texto": ("#F0EADB", None), "--hx-texto-2": ("#DAD4C4", None), "--hx-sec": ("#B3AD9E", "o texto secundário"),
            "--hx-rotulo": ("#F0EADB", None), "--hx-escolhido": ("#F0EADB", None), "--hx-escolhido-ink": ("#17191F", None),
            "--hx-btn-bg": ("#FF4B2B", "vermelhão: a ação e o índice"), "--hx-btn-ink": ("#17191F", None),
            "--hx-medidor": ("#F0EADB", None), "--hx-medidor-trilho": ("rgba(240,234,219,.2)", None), "--hx-medidor-alt": ("12px", None),
            "--hx-sombra-cor": ("#000000", "a sombra dura"),
            "--hx-alerta": ("#FFB020", None), "--hx-perigo": ("#E07C7C", None), "--hx-ok": ("#4BE07E", None),
            "--hx-necessidade": ("#FF7FC0", None), "--hx-aprendido": ("#6FE3FF", None), "--hx-sombrio": ("#D3B6FA", None),
            "--hx-foco": ("#FFFFFF", None),
            "--hx-f": ('"Saira Condensed","Barlow",system-ui,sans-serif', None),
            "--hx-f-tit": ('"Saira Stencil One","Saira Condensed",system-ui,sans-serif', None),
            "--hx-f-num": ('"Saira Condensed",system-ui,sans-serif', None),
        }),
    "zine": dict(
        n=2, nome="Zine", curto="colagem de papel",
        frase="Colagem: papel creme, traço preto grosso, fita amarela e retícula. Cada caixa é um recorte colado, um pouco torto.",
        letras="Rubik 900 itálico nos títulos e nos números; Barlow no texto. As duas já estão no guia.",
        tracos=["o papel creme com traço preto de 3 px, meio tremido, e a sombra dura preta", "as caixas giradas até 1 grau, como recortes",
                "a fita amarela, a retícula e as tiras pretas de título", "a cor de sentido sempre como fundo, com texto preto"],
        tokens={
            "--chao": ("#E6DCC3", None), "--hx-chao-ink": ("#131313", None),
            "--hx-miolo": ("#F6F0E0", "papel: o fundo das caixas"), "--hx-miolo-2": ("#EBE2CB", "papel escuro: teclas e trilhos"),
            "--hx-borda": ("#131313", "tinta: o traço e o texto"),
            "--hx-texto": ("#131313", None), "--hx-texto-2": ("#2B2924", None), "--hx-sec": ("#5A5446", "o texto secundário"),
            "--hx-rotulo": ("#131313", None), "--hx-escolhido": ("#2B50FF", "anil: o escolhido e os medidores"), "--hx-escolhido-ink": ("#FFFFFF", None),
            "--hx-btn-bg": ("#FFD60A", "amarelo-fita: a ação"), "--hx-btn-ink": ("#131313", None),
            "--hx-medidor": ("#2B50FF", None), "--hx-medidor-trilho": ("#DCD2B8", None), "--hx-medidor-alt": ("15px", None),
            "--hx-sombra-cor": ("#131313", None),
            "--hx-alerta": ("#FF9F1C", None), "--hx-perigo": ("#F0483E", None), "--hx-ok": ("#3DCB6C", None),
            "--hx-necessidade": ("#FF6FB5", None), "--hx-aprendido": ("#4FD8F0", None), "--hx-sombrio": ("#B58CF2", None),
            "--hx-foco": ("#2B50FF", None),
            "--hx-f": ('"Barlow",system-ui,sans-serif', None),
            "--hx-f-tit": ('"Rubik","Barlow",system-ui,sans-serif', None),
            "--hx-f-num": ('"Rubik",system-ui,sans-serif', None),
        }),
    "arcade": dict(
        n=3, nome="Arcade", curto="adesivo e pixel",
        frase="Adesivo de fliperama: azul-cobalto, contorno marinho, lima e canto em degrau de pixel. É o Vidro que virou sticker.",
        letras="Bungee (nova) nos títulos e nos números grandes; DotGothic16 (a do visor, do guia) nos números pequenos; Barlow no texto, nos rótulos e nas etiquetas.",
        tracos=["a caixa azul-cobalto com contorno marinho e os cantos em degrau", "a sombra dura marinho de 5 px",
                "o adesivo: uma borda branca recortada em volta do que é solto", "os medidores em blocos e a retícula no título"],
        tokens={
            "--chao": ("#080C33", None), "--hx-chao-ink": ("#FFFFFF", None),
            "--hx-miolo": ("#2247F0", "cobalto: o fundo das caixas"), "--hx-miolo-2": ("#1936C6", "cobalto escuro: teclas e cartões"),
            "--hx-borda": ("#0A1040", "marinho: o contorno e a sombra"),
            "--hx-texto": ("#FFFFFF", "branco: o texto e o adesivo"), "--hx-texto-2": ("#E6ECFF", None), "--hx-sec": ("#D3DDFF", None),
            "--hx-rotulo": ("#FFFFFF", None), "--hx-escolhido": ("#FFFFFF", None), "--hx-escolhido-ink": ("#0A1040", None),
            "--hx-btn-bg": ("#C8F53B", "lima: a ação e os medidores"), "--hx-btn-ink": ("#0A1040", None),
            "--hx-medidor": ("#C8F53B", None), "--hx-medidor-trilho": ("rgba(10,16,64,.5)", None), "--hx-medidor-alt": ("14px", None),
            "--hx-sombra-cor": ("#0A1040", None),
            "--hx-alerta": ("#FFC933", None), "--hx-perigo": ("#FF9C8F", None), "--hx-ok": ("#7CF2A4", None),
            "--hx-necessidade": ("#FF9AD0", None), "--hx-aprendido": ("#8DEBFF", None), "--hx-sombrio": ("#D9C2FF", None),
            "--hx-foco": ("#FFFFFF", None),
            "--hx-f": ('"Barlow",system-ui,sans-serif', None),
            "--hx-f-tit": ('"Bungee","Barlow",system-ui,sans-serif', None),
            "--hx-f-num": ('"DotGothic16",ui-monospace,monospace', None),
        }),
}

# os pares de contraste conferidos por conta (WCAG 2.x), impressos ao gerar e copiados para o LEIA.md
PARES = [("o texto na caixa", "--hx-texto", "--hx-miolo"), ("o secundário na caixa", "--hx-sec", "--hx-miolo"),
         ("o texto na tecla", "--hx-texto", "--hx-miolo-2"), ("a ação", "--hx-btn-ink", "--hx-btn-bg"), ("o escolhido", "--hx-escolhido-ink", "--hx-escolhido")]


def _lum(h: str) -> float:
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a: str, b: str) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------------------------------------------- os sprites (fora do git)
FORMA = {"Agumon": "brasa_crianca_sereno", "Koromon": "brasa_bebe", "Greymon": "brasa_adolescente_brigao"}
_ATLAS = None


def spr(nome: str, k: float) -> str:
    """o primeiro quadro do clipe Idle da forma, recortado do atlas de clipes para _spr/ (fora do git: UI_GUIDELINES 5.1)"""
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = json.loads((ASSETS / "digilab_atlas_up_clipes.json").read_text(encoding="utf-8"))
    x, y, w, h = _ATLAS["sprites"][FORMA[nome]]["clipes"]["Idle"]["quadros"][0][:4]
    d = AQUI / "_spr"
    d.mkdir(exist_ok=True)
    (d / ".gitignore").write_text("*\n", encoding="utf-8")
    arq = d / f"{nome}.png"
    if not arq.exists():
        Image.open(ASSETS / _ATLAS["atlas"]).crop((x, y, x + w, y + h)).save(arq)
    return (f'<i class="spr" role="img" aria-label="{nome}" style="width:{w * k:.0f}px;height:{h * k:.0f}px;'
            f'background-image:url(_spr/{nome}.png)"></i>')


# ---------------------------------------------------------------------------------------------------- o esqueleto: as pecas
FILTROS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="rabisco" x="-4%" y="-8%" width="108%" height="116%">'
           '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="11" result="r"/>'
           '<feDisplacementMap in="SourceGraphic" in2="r" scale="4" xChannelSelector="R" yChannelSelector="G"/></filter></svg>')


def cab(modelo: str, titulo: str, corpo_cls: str = "") -> str:
    m = MODELOS[modelo]
    toks = ";".join(f"{k}:{v}" for k, (v, _) in m["tokens"].items())
    return f'''<!doctype html><html lang="pt-BR" data-modelo="{modelo}"><head><meta charset="utf-8"><meta name="viewport" content="width=1920">
<title>Peles de rua · {m["nome"]} · {titulo}</title>
<link rel="stylesheet" href="{FONTES}">
<style>:root{{{toks}}}</style>
<link rel="stylesheet" href="base.css">
<link rel="stylesheet" href="{modelo}.css">
<script>if(new URLSearchParams(location.search).has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body class="{corpo_cls}">{FILTROS}'''


FIM = "</body></html>\n"


def nota(txt: str, x: float, y: float, w: int = 290) -> str:
    return f'<span class="nota" style="left:{x}px;top:{y}px;max-width:{w}px">{txt}</span>'


def etq(txt: str, cls: str, icone: str = "") -> str:
    return f'<span class="etq {cls}">{svg(icone) if icone else ""}{txt}</span>'


def topo() -> str:
    return f'''<header class="topo">
  <div class="cx cartao-pet"><i class="fita"></i><span class="retrato">{spr("Agumon", 1)}</span>
    <span class="t"><b>Agumon</b><small>Rookie · Coragem</small></span>{etq("Tamer Nv 4", "nv")}</div>
  <div class="cx p agora"><span class="rot">Agora</span><b>explorando</b><span class="porque">nada urgente</span>{svg("seta")}</div>
  <div class="logo" role="img" aria-label="DigiLab"><i class="enf"></i><b>DIGILAB</b><i class="enf"></i></div>
  <span class="vao"></span>
  <div class="cx relogio"><span class="d"><span class="dia">Dia 3</span><b class="hora">07:42</b></span><span class="salvo">salvo</span></div>
  <div class="cx p bits">{svg("chip")}<b>170</b></div>
</header>'''


NAV = [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário"), ("conversar", "Conversar"), ("ajustes", "Ajustes")]


def trilho(atual: str = "pet", so: tuple = ()) -> str:
    bts = "".join(f'<button type="button" class="nav"{" aria-current=page" if i == atual else ""}>{svg(i)}<span>{r}</span></button>'
                  for i, r in NAV if not so or i in so)
    return f'<nav class="cx trilho" aria-label="Destinos">{bts}</nav>'


VITAIS = [("drumstick", "Comida", 38, "baixa"), ("zap", "Energia", 63, ""), ("droplet", "Higiene", 70, ""), ("smile", "Humor", 91, ""),
          ("saude", "Saúde", 100, "ok")]


def vitais() -> str:
    return "".join(f'<div class="vital {c}">{svg(i)}<span class="r">{r}</span><span class="barra" role="img" aria-label="{r} {v} de 100">'
                   f'<i style="width:{v}%"></i></span><b class="n">{v}</b></div>' for i, r, v, c in VITAIS)


def janela(n: int, icone: str, tit: str, res: str, corpo: str = "") -> str:
    ab = bool(corpo)
    resumo = "" if ab else f"<small>{res}</small>"
    c = f'<div class="jan-corpo">{corpo}</div>' if ab else ""
    fita = '<i class="fita"></i>' if ab else ""
    return (f'<section class="cx jan{" aberta" if ab else ""}" aria-label="{tit}">{fita}<header class="jan-cab"><span class="num">0{n}</span>{svg(icone)}'
            f'<span class="tit"><b>{tit}</b>{resumo}</span><span class="risca" aria-hidden="true"></span>'
            f'<button type="button" class="seta" aria-label="{"Recolher" if ab else "Abrir"} {tit}" aria-expanded="{"true" if ab else "false"}">{svg("seta")}</button>'
            f'</header>{c}</section>')


def pilha() -> str:
    return (f'<aside class="pilha" aria-label="Janelas do pet">{janela(1, "estado", "Estado atual", "", vitais())}'
            f'{janela(2, "evolucao", "Evolução", "próxima forma em 7h 26min")}{janela(3, "acoes", "Últimas ações", "07:40 · elogio")}'
            f'{janela(4, "digibrain", "DigiBrain", "o porquê das escolhas")}{janela(5, "olho", "TV", "o cantinho da TV")}</aside>')


def aviso(extra: str = "") -> str:
    return (f'<div class="cx p aviso" role="status" style="{extra}">{svg("drumstick")}<b>Fome</b>'
            f'<button type="button">Estado{svg("seta")}</button></div>')


def balao(x: float, y: float) -> str:
    return f'<div class="cx p balao" style="left:{x}px;top:{y}px">Tô com fome.<i class="rabo" aria-hidden="true"></i></div>'


DOCK = [("drumstick", "Alimentar"), ("music", "Brincar"), ("droplet", "Limpar"), ("mao", "Elogiar"), ("alerta", "Repreender"), ("saude", "Tratar"),
        ("ellipsis", "Mais")]


def dock(so: int = 0) -> str:
    bts = "".join(f'<button type="button" class="tecla">{svg(i)}<span>{r}</span></button>' for i, r in (DOCK[:so] if so else DOCK))
    return f'<nav class="cx dock" aria-label="Cuidar e ensinar">{bts}</nav>'


def mini() -> str:
    return '''<div class="cx mini" role="img" aria-label="Minimapa da ilha"><i class="fita"></i><svg viewBox="0 0 200 200" aria-hidden="true">
  <rect class="m-agua" width="200" height="200"/>
  <polygon class="m-areia" points="22,96 40,48 86,24 140,26 178,58 186,108 168,156 120,180 66,172 30,140"/>
  <polygon class="m-ilha" points="36,98 50,60 88,40 136,42 164,68 170,106 156,144 118,164 72,158 44,132"/>
  <path class="m-trilha" d="M69 117 L112 104 L128 132 L150 81"/>
  <rect class="m-lugar" x="62" y="110" width="14" height="14"/><rect class="m-lugar" x="121" y="125" width="14" height="14"/>
  <rect class="m-lugar" x="143" y="74" width="14" height="14"/>
  <rect class="m-pet" x="97" y="85" width="14" height="14"/>
</svg></div>'''


# os seis exercicios e os ganhos sao os do jogo (TelaTreinar.tsx, CTR.exercicios); a estrela e a aptidao (exemplo: dois deles)
EXS = [("levantar_pedra", "Levantar pedra", "+2 força +1 vigor", False), ("corrida", "Corrida", "+2 fôlego +1 recuperação", True),
       ("alvo", "Alvo", "+2 mira +1 fôlego", False), ("esquiva", "Esquiva", "+2 guarda +1 vigor", False),
       ("meditar", "Meditar", "+2 recuperação +1 guarda", True), ("resistencia", "Resistência", "+2 vigor +1 força", False)]


def exercicios() -> str:
    return '<div class="exs" role="group" aria-label="Exercícios">' + "".join(
        f'<button type="button" class="ex">{svg(i)}<b>{n}</b><small>{g}</small>'
        f'{etq("", "apt alerta", "estrela") if apt else ""}</button>' for i, n, g, apt in EXS) + "</div>"


def medidor(rot: str, v: int, marcas: tuple, cls: str = "") -> str:
    ms = "".join(f'<span class="marca" style="left:{x}%"></span>' for x in marcas)
    return (f'<div class="med {cls}"><span class="rot">{rot}</span><span class="barra" role="img" aria-label="{rot} {v} de 100">'
            f'<i style="width:{v}%"></i>{ms}</span><b class="n">{v}</b></div>')


ABAS = [("treinar", "Treinar"), ("aprend", "Aprendizado"), ("evolucao", "Evolução"), ("itens", "Itens")]


def abas() -> str:
    return '<div class="abas" role="tablist" aria-label="Abas de Crescer">' + "".join(
        f'<button type="button" role="tab" class="aba" aria-selected="{"true" if i == 0 else "false"}" aria-label="{r}">{svg(ic)}<span>{r}</span></button>'
        for i, (ic, r) in enumerate(ABAS)) + "</div>"


def cab_lugar() -> str:
    return (f'<div class="lg-cab">{svg("crescer")}<span class="tit"><b id="lg-tit">Crescer</b><small>saco de pancada</small></span>'
            f'<button type="button" class="fechar" aria-label="Voltar à ilha">{svg("x")}</button></div>')


def destaque() -> str:
    return (f'<div class="destaque"><span class="g"><span class="rot">Treino</span><b class="grande">Pronto</b></span>'
            f'<span class="sec">último: Corrida · 07:31</span></div>')


def lugar() -> str:
    return f'''<section class="cx lugar" aria-labelledby="lg-tit"><i class="fita"></i>{cab_lugar()}{abas()}
  <div class="lg-corpo" role="tabpanel">{destaque()}{exercicios()}
    {medidor("Fadiga", 24, (40, 60))}{medidor("Sobrecarga", 8, (30, 60), "baixa")}
    <div class="linha"><button type="button" class="bt trancado" aria-disabled="true">{svg("zap")}Forçar{etq("Nv 6", "nv", "cadeado")}</button>
      <span class="sec" style="margin-left:auto">estágio <b class="n">0/10</b></span></div>
    <button type="button" class="como">{svg("info")}<span>Como funciona</span>{svg("seta", "ic seta")}</button>
  </div></section>'''


def cena(px: int = 690, py: int = 720, k: float = 3, fundo: str = "") -> str:
    f = f' style="background-position:{fundo}"' if fundo else ""
    return f'<div class="cena"{f}></div><div class="pet-chao" style="left:{px}px;top:{py}px"><i class="sombra"></i>{spr("Agumon", k)}</div>'


# ---------------------------------------------------------------------------------------------------- as quatro telas de cada modelo
def tela_pet(mo: str) -> str:
    m = MODELOS[mo]
    return (cab(mo, "a tela do pet") + cena() + topo() + trilho() + pilha() + aviso() + balao(760, 508) + dock() + mini()
            + nota(f'{m["n"]} · {m["nome"]}: a tela do pet com as mesmas peças de hoje, nos mesmos lugares. Só a pele muda', 130, 100, 300)
            + nota("o aviso da necessidade continua rosa e o que é aprendido continua ciano: o sentido das cores é o do guia (seção 3)", 760, 150, 330)
            + nota("o habitat e o pet não são da pele: o fundo é uma captura do jogo de hoje (2026-11-20), e o Agumon é o sprite do jogo", 1130, 560, 300)
            + FIM)


def tela_lugar(mo: str) -> str:
    return (cab(mo, "um lugar aberto") + cena(1360, 668) + topo() + trilho("crescer") + lugar() + dock() + mini()
            + nota("Crescer › Treinar, o painel mais cheio do jogo: o cabeçalho, as abas, o destaque, os seis exercícios, dois medidores, um botão trancado e a ajuda", 740, 110, 320)
            + nota("os nomes e os ganhos dos exercícios são os do jogo; a estrela é a aptidão (dois de exemplo)", 740, 330, 300)
            + nota("Fadiga 24, Sobrecarga 8, 07:31 e 0/10 são EXEMPLO. No jogo a câmera vai ao saco de pancada; aqui o fundo é o mesmo da outra tela", 740, 560, 300)
            + FIM)


MDOCK = [("drumstick", "Alimentar"), ("music", "Brincar"), ("droplet", "Limpar"), ("ellipsis", "Mais")]
MCOL = [("conversar", "Conversar"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário")]


def fone(x: int, miolo: str) -> str:
    return f'<div class="fone" style="left:{x}px">{miolo}</div>'


def m_hud(atual: str = "") -> str:
    col = "".join(f'<button type="button" class="cx p bt48" aria-label="{r}"{" aria-current=page" if i == atual else ""}>{svg(i)}</button>' for i, r in MCOL)
    return (f'<button type="button" class="cx p m-retrato" aria-label="Retrato">{spr("Agumon", 1.2)}</button>'
            f'<span class="cx p m-relogio"><small>D3</small><b class="hora">07:42</b></span>'
            f'<nav class="m-coluna" aria-label="Destinos">{col}</nav>')


def tela_celular(mo: str) -> str:
    m = MODELOS[mo]
    a = (f'<div class="cena" style="background-position:30% 50%"></div><div class="pet-chao" style="left:190px;top:560px"><i class="sombra"></i>{spr("Agumon", 2.6)}</div>'
         + m_hud() + aviso() + balao(214, 372)
         + '<div class="m-dock" role="group" aria-label="Cuidar e ensinar">'
         + "".join(f'<button type="button" class="cx p m-tecla" aria-label="{r}">{svg(i)}</button>' for i, r in MDOCK) + "</div>")
    corpo = f'<div class="lg-corpo" role="tabpanel">{destaque()}{exercicios()}</div>'
    b = (f'<div class="cena" style="background-position:51% 50%"></div><div class="pet-chao" style="left:150px;top:350px"><i class="sombra"></i>{spr("Agumon", 2.2)}</div>'
         + m_hud("crescer")
         + f'<section class="cx folha" role="dialog" aria-labelledby="lg-tit"><span class="alca" aria-hidden="true"></span>{cab_lugar()}{abas()}{corpo}</section>')
    leg = (f'<div class="legenda-cel" style="left:1220px"><span class="rot">Modelo {m["n"]} de 3 · celular</span><h1 style="color:var(--hx-chao-ink)">{m["nome"]}</h1>'
           f'<p class="esp-txt">À esquerda, a tela do pet a 390 × 844: o retrato, a hora, a coluna dos destinos e as ações redondas de hoje viram as peças do modelo.</p>'
           f'<p class="esp-txt">À direita, um lugar aberto: a folha sobe da base, com o mesmo cabeçalho, as abas e os exercícios em duas colunas.</p></div>')
    return cab(mo, "o celular") + '<div class="palco-cel"></div>' + fone(280, a) + fone(750, b) + leg + FIM


def tela_folha(mo: str) -> str:
    m = MODELOS[mo]
    t = m["tokens"]
    am = "".join(f'<li class="amostra"><i style="background:{v}"></i><span><b>{papel.split(":")[0]}</b><small>{v}</small></span></li>'
                 for k, (v, papel) in t.items() if papel)
    sem = "".join(f'<div class="sem-linha">{etq(rot, cls, ic)}<span>{txt}</span></div>' for rot, cls, ic, txt in [
        ("necessidade", "nec", "drumstick", "o que o pet precisa agora"), ("aprendido", "apr", "aprend", "o que veio do que você ensinou"),
        ("alerta", "alerta", "alerta", "o destaque e o trancado"), ("perigo", "perigo", "x", "o que não tem volta"), ("ok", "ok", "check", "o que está bem")])
    tracos = "".join(f"<li>{x}</li>" for x in m["tracos"])
    return cab(mo, "a folha do modelo") + f'''<div class="esp">
<div class="esp-col">
  <div class="esp-nome"><span class="rot" style="color:inherit">Modelo {m["n"]} de 3 · {m["curto"]}</span><h1>{m["nome"]}</h1><p>{m["frase"]}</p></div>
  <h2>A paleta</h2><ul class="amostras">{am}</ul>
  <h2>O sentido das cores (o do guia)</h2>{sem}
</div>
<div class="esp-col">
  <h2>As letras</h2>
  <div class="cx caixa-demo"><span class="t-display">Digimon</span><span class="rot">Rótulo · Fadiga · Sobrecarga</span>
    <span>Ponha a comida na ilha, brinque, elogie ou repreenda. Ele lembra.</span><span class="t-num">07:42 · 170 · 63 %</span></div>
  <p class="esp-txt">{m["letras"]}</p>
  <h2>O traço</h2><ul class="esp-txt">{tracos}</ul>
  <h2>Uma janela</h2>{janela(1, "estado", "Estado atual", "", vitais())}{janela(2, "evolucao", "Evolução", "próxima forma em 7h 26min")}
</div>
<div class="esp-col">
  <h2>Os botões</h2>
  <div class="pecas"><button type="button" class="bt acao">{svg("check")}Treinar agora</button><button type="button" class="bt">Agora não</button>
    <button type="button" class="bt perigo">{svg("x")}Apagar</button><button type="button" class="bt" disabled>Desligado</button>
    <button type="button" class="bt trancado" aria-disabled="true">{svg("zap")}Forçar{etq("Nv 6", "nv", "cadeado")}</button></div>
  <h2>As etiquetas e as chaves</h2>
  <div class="pecas">{etq("Tamer Nv 4", "nv")}{etq("aprendido", "apr", "aprend")}{etq("ok", "ok", "check")}{etq("teste", "alerta")}{etq("Fome", "nec", "drumstick")}
    <span class="inter on" role="switch" aria-checked="true"></span><span class="inter" role="switch" aria-checked="false"></span></div>
  <h2>As abas</h2>{abas()}
  <h2>Os medidores</h2>{medidor("Energia", 63, ())}{medidor("Comida", 38, (), "baixa")}{medidor("Saúde", 100, (), "ok")}
  <h2>O trilho e as ações</h2>{trilho("crescer", ("pet", "crescer", "lutar", "conversar"))}{dock(4)}
</div>
<div class="esp-col">
  <h2>O destaque e os cartões</h2>
  <div class="cx caixa-demo" style="padding:14px">{destaque()}<div class="exs" style="grid-template-columns:1fr 1fr">{
    "".join(f'<button type="button" class="ex">{svg(i)}<b>{n}</b><small>{g}</small>{etq("", "apt alerta", "estrela") if a else ""}</button>' for i, n, g, a in EXS[:2])}</div></div>
  <h2>O aviso, a fala e a placa</h2>{aviso()}
  <div class="cx p balao">Tô com fome.<i class="rabo" aria-hidden="true"></i></div>
  <span class="cx p placa" style="position:relative;align-self:flex-start">{svg("saco")}Saco de pancada</span>
  <h2>A marca</h2><div class="logo" style="position:relative;left:auto;transform:none;align-self:flex-start"><i class="enf"></i><b>DIGILAB</b><i class="enf"></i></div>
</div></div>''' + FIM


def comparacao() -> str:
    """as duas peles de hoje (capturas do jogo de 2026-11-20) e os tres modelos (as capturas desta prancha), no mesmo recorte"""
    def q(src: str, rot: str, sub: str, novo: bool = False) -> str:
        return (f'<figure class="cmp{" novo" if novo else ""}"><span class="recorte"><img src="{src}" alt=""></span>'
                f'<figcaption><b>{rot}</b><span>{sub}</span></figcaption></figure>')
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=1920">
<title>Peles de rua · as cinco lado a lado</title>
<link rel="stylesheet" href="{FONTES}">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1920px;height:950px}}
/* a prancha de comparacao nao e de modelo nenhum: preto, branco e cinza, sem cor de pele */
body{{background:#111;color:#fff;font:500 15px/1.3 "Barlow",system-ui,sans-serif;padding:26px 30px;display:flex;flex-direction:column;gap:14px}}
h1{{font:800 26px/1 "Barlow",sans-serif;letter-spacing:.02em}}
h1 small{{font:500 16px/1 "Barlow",sans-serif;color:#bbb;margin-left:14px}}
.grade{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;flex:1;min-height:0}}
.cmp{{display:flex;flex-direction:column;gap:8px;min-width:0}}
.recorte{{position:relative;flex:1;min-height:0;overflow:hidden;background:#000;outline:2px solid #555}}
.cmp.novo .recorte{{outline-color:#fff}}
.recorte img{{position:absolute;right:0;top:0;height:108%;width:auto}}
figcaption b{{display:block;font:800 19px/1.1 "Barlow",sans-serif}}
figcaption span{{display:block;color:#bbb;font-size:14px}}
.baixo{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;height:140px}}
.baixo .recorte img{{right:auto;left:0;top:0;height:680%}}
</style></head><body>
<h1>As peles lado a lado<small>o mesmo canto da tela do pet (o relógio e as janelas) e, embaixo, o cartão do pet e a linha do agora</small></h1>
<div class="grade">{q("img/hoje_vidro.jpg", "Vidro (hoje)", "a pele padrão do jogo")}{q("img/hoje_militar.jpg", "Militar (hoje)", "a outra pele do jogo")}
{q("capturas/estencil_pet_limpa.jpg", "1 · Estêncil", "cartaz de rua", True)}{q("capturas/zine_pet_limpa.jpg", "2 · Zine", "colagem de papel", True)}
{q("capturas/arcade_pet_limpa.jpg", "3 · Arcade", "adesivo e pixel", True)}</div>
<div class="baixo">{"".join(f'<span class="recorte"><img src="{s}" alt=""></span>' for s in ["img/hoje_vidro.jpg", "img/hoje_militar.jpg", "capturas/estencil_pet_limpa.jpg", "capturas/zine_pet_limpa.jpg", "capturas/arcade_pet_limpa.jpg"])}</div>
</body></html>
'''


TELAS = {"pet": tela_pet, "lugar": tela_lugar, "celular": tela_celular, "folha": tela_folha}


def escrever() -> None:
    for mo, m in MODELOS.items():
        for nome, f in TELAS.items():
            (AQUI / f"{mo}_{nome}.html").write_text(f(mo), encoding="utf-8", newline="\n")
        t = m["tokens"]
        linha = " · ".join(f"{rot} {contraste(t[a][0], t[b][0]):.1f}" for rot, a, b in PARES)
        print(f'{m["nome"]}: {linha}'.encode("ascii", "replace").decode())
    (AQUI / "comparacao.html").write_text(comparacao(), encoding="utf-8", newline="\n")
    print(len(MODELOS) * len(TELAS), "telas")


if __name__ == "__main__":
    escrever()
