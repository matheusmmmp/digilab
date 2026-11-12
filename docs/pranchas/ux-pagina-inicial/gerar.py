# Gera a prancha "a pagina de entrada" (a tela 6 do docs/PLANO_V3_CONTA.md, secao 3: "uma pagina inicial curta"; etapa CN6).
# RODADA 2 (2026-11-12), pelo pedido do Matheus com quatro referencias: "esse design mais clean, cyber futurismo, um laboratorio de ia
# mesmo misturado com game e estetica dos pets sendo fofos, uma pagina seguindo um pouco a ideia do 'Explore 14k'".
# RODADA 3 (2026-11-12), sobre a captura da rodada 2: "corrija tentando deixar um pouco com as formas retas da pagina do valorant".
# Entraram os cortes retos em degrau entre as faixas, os titulos em caixa alta alinhados a um lado, a moldura de oito lados no
# lugar do anel, os botoes com a moldura deslocada e os quadradinhos na margem. As cores e os textos nao mudaram.
# So desenho; nenhum codigo do jogo. Uma pagina so, que rola, com a quebra a 900 px. ?sem tira as notas amarelas.
# Uso (da raiz): python docs/pranchas/ux-pagina-inicial/gerar.py   (escreve inicial.html ao lado; precisa do Pillow e dos sprites em
#                D:\Trab\digilab\Assets, fora do git, para achar o primeiro quadro de cada folha)
#
# O QUE VEM DE CADA REFERENCIA:
#   "Explore 14K" ............ a estrutura: a imagem grande com o titulo e um botao; as secoes numeradas com o losango e o titulo no meio;
#                              a imagem em moldura no centro; a faixa larga; o texto ao lado de uma ficha; a faixa azul com tres colunas
#   o anel com circuitos ..... o especime: o pet dentro do anel, com as trilhas saindo para cima e para baixo
#   a malha com o "00" ....... a malha fina no fundo, as riscas diagonais, os numeros grandes, os cantos cortados
#   "Design Futures" ......... o claro quase branco com uma cor so de destaque e os rotulos pequenos espacados
#
# DE ONDE VEM CADA AFIRMACAO DA PAGINA (nada do que ela diz e novo):
#   "abre no navegador, sem conta e sem instalar" ..... docs/PLANO_V3_CONTA.md, CN-1
#   a linha do Agumon na regua do heroi ............... web/app/motor/nomes.ts (DIGIMON_DA_FORMA: Koromon, Agumon, Greymon) e
#                                                       motor/arena/formas.ts (MetalGreymon, Ultimate; WarGreymon, Mega)
#   o brasao, o ovo, o primeiro cuidado ............... a jornada do jogo; os brasoes e os niveis: UI_GUIDELINES, secao 12
#   as acoes Alimentar, Brincar, Limpar, Carinho ...... o dock da tela Pet
#   o pet decide sozinho; o DigiBrain mostra a escolha  docs/PRODUTO_VISAO.md, secao 1; o scan do DigiBrain (ScanDigiBrain.tsx)
#   "aprendido" ....................................... UI_GUIDELINES, principio 2
#   seis exercicios, seis medalhas ate a Liga ......... Crescer › Treinar (TelaTreinar.tsx) e MapaExploracao.tsx
#   sem gacha, os Bits so jogando ..................... CN-11 e docs/PLANO_V3_MOEDA.md (M-2)
#   sem culpa e sem contagem .......................... UI_GUIDELINES, principio 5
#   o credito do Digimon UP (Bandai) no rodape ........ UI_GUIDELINES, secao 5.1
# A pagina NAO diz "sem anuncios": a CN-12 preve o video pedido pelo jogador para a voz.
# EXEMPLO DE LAYOUT, NUNCA DADO: "explorar 48 %", "comer 31 %", "dormir 21 %" e a ficha "Agumon · Rookie · Coragem".
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "ux-lugares-menus"))
import gerar as G  # noqa: E402  (so os icones)

ASSETS = AQUI.parents[3] / "Assets" / "arena_up" / "sprites"
IC = {"play": '<path d="M7 4l13 8-13 8z"/>', "conta": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>'}


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else G.svg(n, cls)


# o primeiro quadro do Greymon esta de olho fechado (o Matheus viu, 2026-11-12): a folha tem 7 x 7 quadros de 622/7 x 552/7 px, e o
# escolhido e o da coluna 5, linha 5 (parado, de olho aberto)
REGIAO = {"Greymon": (355, 315, 444, 394)}


def _primeira_faixa(ocupado: list) -> tuple[int, int]:
    """a primeira faixa ocupada com 8 px ou mais (algumas folhas tem um pixel solto antes do primeiro quadro)"""
    i = 0
    while True:
        a = next(j for j in range(i, len(ocupado)) if ocupado[j])
        b = next((j for j in range(a, len(ocupado)) if not ocupado[j]), len(ocupado))
        if b - a >= 8:
            return a, b
        i = b


def pet(nome: str, k: float, vira: bool = False, arq: str = "") -> str:
    """o primeiro quadro da folha do Digimon (parado), achado pelo alfa: a primeira coluna de quadros e, nela, a primeira linha"""
    arq = arq or nome   # a folha, quando o primeiro quadro da folha do nome nao e o parado (o WarGreymon)
    im = Image.open(ASSETS / f"{arq}.png").convert("RGBA")
    al = im.getchannel("A")
    W, H = im.size
    if nome in REGIAO:   # um quadro escolhido a mao, pela regiao dele na folha
        x0, y0, x1, y1 = REGIAO[nome]
    else:
        x0, x1 = _primeira_faixa([al.crop((x, 0, x + 1, H)).getbbox() is not None for x in range(W)])
        y0, y1 = _primeira_faixa([al.crop((x0, y, x1, y + 1)).getbbox() is not None for y in range(H)])
    bx = al.crop((x0, y0, x1, y1)).getbbox()
    x0, x1, y0, y1 = x0 + bx[0], x0 + bx[2], y0 + bx[1], y0 + bx[3]
    return (f'<span class="pet{" vira" if vira else ""}" role="img" aria-label="{nome}" style="width:{(x1 - x0) * k:.0f}px;height:{(y1 - y0) * k:.0f}px;'
            f"background-image:url('{G.A}/sprites/{arq}.png');background-size:{W * k:.0f}px {H * k:.0f}px;"
            f'background-position:{-x0 * k:.0f}px {-y0 * k:.0f}px"></span>')


def nota(txt: str, estilo: str, w: int = 280) -> str:
    return f'<span class="nota" style="{estilo};max-width:{w}px">{txt}</span>'


def marca(n: str, rot: str, titulo: str, tid: str) -> str:
    return (f'<div class="marca-sec"><span class="losango" aria-hidden="true"><span>{n}</span></span><span class="lcd">{rot}</span>'
            f'<h2 id="{tid}">{titulo}</h2></div>')


GARANTIAS = "".join(f"<li>{G.svg('check')}{t}</li>" for t in ["No navegador", "Sem conta", "Sem instalar"])

# as trilhas de circuito do especime (1080 x 560): linhas, nos, pilhas de tracos e setas, saindo do anel para cima e para baixo
TRILHAS = '''<svg class="trilhas" viewBox="0 0 1080 560" aria-hidden="true">
<path d="M470 60V0M540 26V0M610 60V20l40-20M410 110V40L360 0M670 110V70l60-40V0"/>
<path d="M470 500v60M540 534v26M610 500v40l-40 20M410 450v70l50 40M670 450v50l70 40v20"/>
<path d="M300 280H170l-40-40H0M780 280h130l40 40h130M335 200l-60-40H190M745 360l60 40h85"/>
<circle class="no" cx="470" cy="60" r="5"/><circle class="no" cx="610" cy="60" r="5"/><circle class="no" cx="540" cy="26" r="5"/>
<circle class="no" cx="470" cy="500" r="5"/><circle class="no" cx="610" cy="500" r="5"/><circle class="no" cx="540" cy="534" r="5"/>
<circle class="cheio" cx="410" cy="110" r="4"/><circle class="cheio" cx="670" cy="110" r="4"/><circle class="cheio" cx="410" cy="450" r="4"/><circle class="cheio" cx="670" cy="450" r="4"/>
<circle class="cheio" cx="300" cy="280" r="4"/><circle class="cheio" cx="780" cy="280" r="4"/><circle class="no" cx="190" cy="160" r="5"/><circle class="no" cx="890" cy="400" r="5"/>
<g class="cheio"><rect x="500" y="6" width="14" height="3"/><rect x="500" y="12" width="14" height="3"/><rect x="500" y="18" width="14" height="3"/>
<rect x="566" y="538" width="14" height="3"/><rect x="566" y="544" width="14" height="3"/><rect x="566" y="550" width="14" height="3"/>
<path d="M636 34l5 8h-10zM636 22l5 8h-10zM444 524l5 8h-10zM444 536l5 8h-10zM60 232l8 5-8 5zM1010 312l8 5-8 5z"/></g>
</svg>'''


ARQ = {"WarGreymon": "WarGreymon_Adventure"}   # a folha em que o primeiro quadro e o WarGreymon parado, sem a poeira do golpe


def pagina() -> str:
    jogar = f'<a class="bt acao jogar" href="#/pet">{ic("play")}Começar agora</a>'
    fila = "".join(f'<figure>{pet(n, k, v, ARQ.get(n, ""))}<figcaption class="lcd"><b>{n}</b><span class="nv"> · {nv}</span></figcaption></figure>'
                   for n, k, v, nv in [("Koromon", 1.2, True, "In-Training"), ("Agumon", 1.5, True, "Rookie"), ("Greymon", 2.0, True, "Champion"),
                                       ("MetalGreymon", 1.4, True, "Ultimate"), ("WarGreymon", 2.2, True, "Mega")])
    brasoes = "".join(f'<span class="chip">{b}</span>' for b in ["Coragem", "Amizade", "Conhecimento", "Sinceridade"])
    ops = "".join(f'<span class="barra-op"><span>{o}</span><i><b style="width:{p}%"></b></i><span>{p} %</span></span>'
                  for o, p in [("explorar", 48), ("comer", 31), ("dormir", 21)])
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DigiLab · a página de entrada (prancha, rodada 2)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Barlow:wght@400;500;600;700&family=DotGothic16&family=Saira+Condensed:wght@600;700&display=swap">
<link rel="stylesheet" href="inicial.css">
<script>if(new URLSearchParams(location.search).has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body><div class="pi">

<header class="barra">
  <a class="marca" href="#topo" aria-label="DigiLab"><i aria-hidden="true"></i>DIGILAB</a>
  <nav aria-label="Nesta página"><a href="#lab">O laboratório</a><a href="#dia">Primeiro dia</a><a href="#jogo">O jogo</a></nav>
  <a class="bt" href="#/config/conta">{ic("conta")}Entrar</a>
  <a class="bt acao" href="#/pet">{ic("play")}Jogar</a>
</header>

<main id="topo">
<section class="heroi" aria-labelledby="h1">
  <span class="lcd olho">Laboratório de pets com IA</span>
  <h1 id="h1">Crie um Digimon<em>que decide sozinho</em></h1>
  <p class="sub">Você cuida, ensina e treina. Ele escolhe o que fazer, e o jogo mostra o porquê.</p>
  <div class="cta">
    <a class="bt claro jogar" href="#/pet">{ic("play")}Começar agora</a>
    <ul class="garantias" aria-label="Para começar">{GARANTIAS}</ul>
    <a class="ja" href="#/config/conta">Já tenho conta: entrar</a>
  </div>
  <span class="corte" aria-hidden="true"></span>
  <div class="fila" aria-label="A linha do Agumon, do In-Training ao Mega">{fila}</div>
  <span class="regua" aria-hidden="true"></span>
  {nota("1 · a ideia do 'Explore 14K': a imagem grande (a ilha de verdade, de uma captura do jogo), o título em caixa alta e UM botão. Ele leva direto ao jogo (CN-1: sem conta)", "right:20px;top:90px", 320)}
  {nota("embaixo a imagem acaba num corte reto, em degrau (as formas do Valorant), e os pets ficam na borda, sobre uma régua de laboratório. É a linha do Agumon no jogo (nomes.ts e formas.ts), do In-Training ao Mega; é uma das linhas possíveis, não a única", "right:20px;bottom:150px", 300)}
</section>

<section class="sec" id="lab" aria-labelledby="t1">
  {marca("01", "Laboratório aberto", "Um cérebro que você pode ver", "t1")}
  <div class="duas">
    <p>Cada pet nasce com uma rede própria. Ela muda com o que ele vive: a comida que achou, o elogio, a bronca.</p>
    <p>Abra o DigiBrain a qualquer hora e veja a escolha de agora e a chance de cada opção. Nada ali é texto inventado.</p>
  </div>
  <div class="especime">
    {TRILHAS}
    <div class="anel"><i class="miolo" aria-hidden="true"></i><span class="sombra" aria-hidden="true"></span>{pet("Agumon", 3)}</div>
    <div class="ficha f1"><span class="lcd">Espécime</span><b>Agumon</b><span class="lcd">Rookie · Coragem</span></div>
    <figure class="ficha f2"><img src="../digibrain-lab/scan_lab_mapa_1280.png" alt="O DigiBrain aberto no jogo: a rede do pet e a escolha de agora"><figcaption class="lcd">O DigiBrain, no jogo</figcaption></figure>
    <div class="ficha f3"><span class="lcd">Escolha de agora</span>{ops}<span class="etq-apr">aprendido com você</span></div>
  </div>
  {nota("2 · as seções numeradas com o losango e o título no meio (o 'Explore 14K'); no lugar da foto em losango, o pet numa moldura de oito lados, em camadas, com trilhas de circuito", "left:20px;top:30px", 300)}
  {nota("as três fichas: quem é o pet, a captura real do DigiBrain e a escolha de agora. As porcentagens são EXEMPLO", "right:20px;top:330px", 260)}
</section>

<div class="panorama" role="img" aria-label="O jogo: a ilha, um Gomamon ao lado do saco de pancada e o menu de treino"><span class="lcd">Captura do jogo · a ilha e o treino</span></div>

<section class="sec" id="dia" aria-labelledby="t2">
  <div class="lado-a-lado">
    <div>
      {marca("02", "Primeiro dia", "Do ovo ao primeiro cuidado", "t2")}
      <p>Você escolhe um brasão e recebe um ovo. Ele choca num In-Training, que cresce com o que vive. Como ele vai evoluir depende de como foi criado.</p>
      <div class="chips" aria-label="Os brasões">{brasoes}</div>
    </div>
    <div class="agenda">
      <header><span class="lcd">Em um minuto</span><span class="lcd">3 passos</span></header>
      <ol>
        <li><span class="n" aria-hidden="true">1</span><span><b>Escolha um brasão</b><small>Ele define o ovo.</small></span>{G.svg("brasao")}</li>
        <li><span class="n" aria-hidden="true">2</span><span><b>O ovo choca</b><small>Nasce um In-Training.</small></span>{pet("Koromon", .45)}</li>
        <li><span class="n" aria-hidden="true">3</span><span><b>Cuide e ensine</b><small>Comida, brincadeira, elogio.</small></span>{G.svg("drumstick")}</li>
      </ol>
    </div>
  </div>
  {nota("3 · o texto ao lado de uma ficha com cabeçalho escuro (a agenda do 'Explore 14K'), com os três primeiros minutos do jogo", "right:20px;top:36px", 280)}
</section>

<section class="azul" id="jogo" aria-labelledby="t3">
  {marca("03", "O jogo", "O ovo está esperando", "t3")}
  <ul class="tres">
    <li><span class="palco">{pet("Tokomon", 1.3)}</span><h3>Cuidar</h3><p>Alimentar, brincar, limpar e dar carinho. Ele sente e responde.</p></li>
    <li><span class="palco">{pet("Agumon", 1.5)}</span><h3>Treinar</h3><p>Seis exercícios no saco de pancada. O treino muda os golpes.</p></li>
    <li><span class="palco">{pet("Greymon", 1.1)}</span><h3>Lutar</h3><p>Ele luta sozinho na arena. Seis medalhas até a Liga.</p></li>
  </ul>
  <div class="fecho"><a class="bt claro jogar" href="#/pet">{ic("play")}Começar agora</a><ul class="garantias" aria-label="Para começar">{GARANTIAS}</ul></div>
  {nota("4 · a faixa azul do fim, com a borda em degraus de circuito no lugar do papel rasgado, três colunas e o botão de novo", "left:20px;top:80px", 300)}
</section>

<section class="sec" aria-labelledby="t4" style="padding-bottom:40px">
  <div class="marca-sec"><span class="lcd">Sem pegadinha</span><h2 id="t4">O que o jogo não faz</h2></div>
  <ul class="nao">
    <li><b>Sem gacha</b><span>Nada de caixa de prêmio nem sorteio pago.</span></li>
    <li><b>Sem vantagem à venda</b><span>Os Bits só se ganham jogando.</span></li>
    <li><b>Sem culpa</b><span>Nenhuma contagem nem aviso insistente.</span></li>
    <li><b>Conta opcional</b><span>Entrar é escolha, e você pode apagar tudo.</span></li>
  </ul>
</section>
</main>

<footer class="rodape">
  <nav aria-label="Rodapé"><a href="#termos">Termos</a><a href="#privacidade">Privacidade</a><a href="#creditos">Créditos</a></nav>
  <span>Sprites, ícones e fundos: Digimon UP (Bandai). DigiLab é um projeto pessoal.</span>
</footer>

<div class="fixo"><a class="bt acao" href="#/pet">{ic("play")}Começar agora</a></div>
</div></body></html>
'''


def escrever() -> None:
    (AQUI / "inicial.html").write_text(pagina(), encoding="utf-8", newline="\n")
    print("inicial.html")


if __name__ == "__main__":
    escrever()
