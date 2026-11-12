# Gera a prancha "a pagina de entrada" (a tela 6 do docs/PLANO_V3_CONTA.md, secao 3: "uma pagina inicial curta"; etapa CN6).
# So desenho; nenhum codigo do jogo. Uma pagina so, que rola, com a quebra a 900 px (o corte do app). A pele vem de ?pele=vidro|xcom,
# e ?sem tira as notas amarelas (no celular elas nunca aparecem).
# Uso (da raiz): python docs/pranchas/ux-pagina-inicial/gerar.py   (escreve inicial.html ao lado)
#
# DE ONDE VEM CADA AFIRMACAO DA PAGINA (nada do que ela diz e novo):
#   "abre no navegador, sem conta e sem instalar" ..... docs/PLANO_V3_CONTA.md, CN-1: o jogo abre direto na ilha; a conta e escolha
#   o save fica no aparelho ........................... idem, secao 1 (web/app/src/save.ts, localStorage)
#   o brasao, o ovo, o primeiro cuidado ............... a jornada do jogo (o brasao, o ovo, a ilha); os brasoes: UI_GUIDELINES, secao 12
#   os niveis Digi-Egg a Mega ......................... UI_GUIDELINES, secao 12
#   as acoes Alimentar, Brincar, Limpar, Carinho ...... o dock da tela Pet
#   o pet decide sozinho; o DigiBrain mostra a escolha  docs/PRODUTO_VISAO.md, secao 1; o scan do DigiBrain (ScanDigiBrain.tsx)
#   "o que voce ensina" ............................... UI_GUIDELINES, principio 2 e a marca do aprendido (--hx-aprendido)
#   treinar, lutar, as 6 medalhas, evoluir ............ Crescer e Lutar (as telas de hoje); "as 6 medalhas": MapaExploracao.tsx
#   sem gacha, os Bits so jogando ..................... CN-11 e docs/PLANO_V3_MOEDA.md (M-2)
#   sem culpa e sem contagem .......................... UI_GUIDELINES, principio 5
#   o credito do Digimon UP (Bandai) no rodape ........ UI_GUIDELINES, secao 5.1
# A pagina NAO diz "sem anuncios": a CN-12 preve o video pedido pelo jogador para a voz.
# AS CAPTURAS sao do jogo e ja estavam no repositorio: ../ilha-grande/saco_em_terra_1440.jpg (2026-11-11),
# ../digibrain-lab/scan_lab_mapa_1280.png, ../b3/capturas_codigo/luta_1280_vidro.png e o fundo ../ux-lugares-menus/img/cena_sem_pet.jpg.
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "ux-lugares-menus"))
import gerar as G  # noqa: E402

IC = {
    "play": '<path d="M7 4l13 8-13 8z"/>',
    "ovo": '<path d="M12 3c-4 0-7 6-7 10a7 7 0 0 0 14 0c0-4-3-10-7-10z"/>',
    "coracao": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "conta": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
}


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else G.svg(n, cls)


def nota(txt: str, estilo: str, w: int = 280) -> str:
    return f'<span class="nota" style="{estilo};max-width:{w}px">{txt}</span>'


def tela(src: str, alt: str, legenda: str, cls: str = "") -> str:
    return (f'<figure class="caixa pi-tela {cls}"><img src="{src}" alt="{alt}" loading="lazy">'
            f'<figcaption>{legenda}</figcaption></figure>')


GARANTIAS = "".join(f"<li>{G.svg('check')}{t}</li>" for t in ["No navegador", "Sem conta", "Sem instalar"])
JOGAR = f'<a class="bt acao jogar" href="#/pet">{ic("play")}Começar agora</a>'


def pagina() -> str:
    brasoes = "".join(f'<span class="etq">{b}</span>' for b in ["Coragem", "Amizade", "Conhecimento", "Sinceridade"])
    acoes = "".join(f'<span class="etq">{a}</span>' for a in ["Alimentar", "Brincar", "Limpar", "Carinho"])
    evo = (f'{G.spr("Koromon", .5)}{G.svg("seta")}{G.spr("Agumon", .8)}{G.svg("seta")}'
           f'<span class="q" role="img" aria-label="Champion: ainda não se sabe">?</span>')
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DigiLab · a página de entrada (prancha)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700;800&family=Barlow:wght@400;500;600;700;800;900&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="../ux-lugares-menus/lugares.css">
<link rel="stylesheet" href="inicial.css">
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.pele=q.get("pele")==="xcom"?"xcom":"vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body><div class="pi">

<header class="pi-barra">
  <a class="pi-marca" href="#topo" aria-label="DigiLab"><i aria-hidden="true">//</i>DIGILAB</a>
  <nav class="pi-nav" aria-label="Nesta página"><a href="#comeca">Como começa</a><a href="#jogo">O jogo</a><a href="#regras">Sem pegadinha</a></nav>
  <a class="bt" href="#/config/conta">{ic("conta")}Entrar</a>
  <a class="bt acao" href="#/pet">{ic("play")}Jogar</a>
</header>

<main id="topo">
<section class="pi-heroi" aria-labelledby="pi-h1">
  <div class="txt">
    <span class="rot">Pet virtual com cérebro próprio</span>
    <h1 id="pi-h1">Crie um Digimon que decide sozinho</h1>
    <p class="sub">Você cuida, ensina e treina. Ele escolhe o que fazer, e o jogo mostra o porquê.</p>
    <div class="pi-cta">
      {JOGAR}
      <ul class="pi-garantias" aria-label="Para começar">{GARANTIAS}</ul>
      <a class="pi-ja" href="#/config/conta">Já tenho conta: entrar</a>
    </div>
  </div>
  {tela("../ilha-grande/saco_em_terra_1440.jpg", "O jogo: um Gomamon ao lado do saco de pancada, na ilha, com o menu de treino aberto",
        "O jogo de hoje: a ilha, o pet e o treino.")}
  {nota("1 · o botão principal está na primeira dobra e leva direto ao jogo (#/pet): a CN-1 diz que o jogo abre sem conta. Nenhum formulário antes", "left:20px;top:16px", 330)}
  {nota("a imagem é uma captura real do jogo (2026-11-11), não uma ilustração", "right:20px;top:16px", 260)}
  {nota("'Entrar' é discreto, para quem já tem conta; leva a Ajustes › Conta (a prancha ux-conta)", "left:20px;bottom:14px", 300)}
</section>

<section class="pi-sec" id="comeca" aria-labelledby="pi-comeca">
  <span class="rot">Em um minuto</span>
  <h2 id="pi-comeca">Como começa</h2>
  <ol class="pi-passos">
    <li class="caixa pi-passo"><span class="n" aria-hidden="true">1</span><h3>Escolha um brasão</h3><p>Ele define o ovo que você recebe.</p><div class="pi-brasoes">{brasoes}</div></li>
    <li class="caixa pi-passo"><span class="n" aria-hidden="true">2</span><h3>O ovo choca</h3><p>Nasce um In-Training. Daí em diante ele cresce com o que vive.</p><div class="pi-linha-evo">{evo}</div></li>
    <li class="caixa pi-passo"><span class="n" aria-hidden="true">3</span><h3>Cuide e ensine</h3><p>Ponha a comida na ilha, brinque, elogie ou corrija. Ele lembra.</p><div class="pi-acoes">{acoes}</div></li>
  </ol>
  {nota("2 · os três primeiros minutos do jogo, na ordem em que acontecem. Os nomes são os do jogo (brasões, níveis, ações)", "right:20px;top:20px", 300)}
  {nota("o Champion é um '?': a página não promete uma forma que depende de como o pet foi criado", "left:38%;bottom:8px", 300)}
</section>

<div id="jogo">
<section class="pi-faixa" aria-labelledby="pi-f1">
  <div class="txt"><span class="rot">DigiBrain</span><h2 id="pi-f1">Veja o que ele pensa</h2>
    <p>Cada escolha do pet sai de uma rede que muda com a vida dele. Abra o DigiBrain e veja a escolha de agora e a chance de cada opção.</p>
    <ul class="pts"><li>{G.svg("digibrain")}<span>O motivo de cada ação, sem texto inventado.</span></li>
      <li>{G.svg("aprend")}<span>O que veio de você aparece marcado: <span class="etq apr">aprendido</span></span></li></ul></div>
  {tela("../digibrain-lab/scan_lab_mapa_1280.png", "O DigiBrain: a rede do pet e a escolha de agora, explorar, 48 %", "O DigiBrain aberto no jogo.", "estreita")}
  {nota("3 · três faixas, uma por coisa que o jogo tem hoje. Cada afirmação tem origem (o cabeçalho do gerar.py)", "left:20px;top:10px", 300)}
</section>
<section class="pi-faixa inv" aria-labelledby="pi-f2">
  <div class="txt"><span class="rot">Crescer e lutar</span><h2 id="pi-f2">Treine, lute e evolua</h2>
    <p>Do Digi-Egg ao Mega. O treino muda os golpes, a luta rende medalhas, e a evolução depende de como ele foi criado.</p>
    <ul class="pts"><li>{G.svg("treinar")}<span>Seis exercícios no saco de pancada.</span></li>
      <li>{G.svg("medalhas")}<span>Seis medalhas até a Liga.</span></li>
      <li>{G.svg("evolucao")}<span>Mais de uma forma possível em cada nível.</span></li></ul></div>
  {tela("../b3/capturas_codigo/luta_1280_vidro.png", "A luta: Gabumon contra Monochromon na arena", "A arena: o pet luta sozinho, e o jogo diz a regra que ele usou.")}
</section>
<section class="pi-faixa" aria-labelledby="pi-f3">
  <div class="txt"><span class="rot">Seu aparelho, seu pet</span><h2 id="pi-f3">Comece agora, guarde depois</h2>
    <p>O pet fica salvo neste navegador. Se quiser levá-lo para outro aparelho, crie uma conta depois, com Google ou GitHub.</p>
    {JOGAR}</div>
  {tela("../ux-conta/capturas/entrar_390_vidro.jpg", "A tela Entrar no celular: o que vai para o servidor e os botões do Google e do GitHub", "A conta é opcional e fica nos Ajustes.", "fina")}
  {nota("o botão se repete aqui, no fim e, no celular, numa barra fixa embaixo", "left:20px;bottom:10px", 260)}
</section>
</div>

<section class="pi-sec" id="regras" aria-labelledby="pi-regras" style="border-top:1px solid var(--hx-borda)">
  <span class="rot">Sem pegadinha</span>
  <h2 id="pi-regras">O que o jogo não faz</h2>
  <ul class="pi-nao">
    <li><b>Sem gacha</b><span>Nada de caixa de prêmio nem sorteio pago.</span></li>
    <li><b>Sem vantagem à venda</b><span>Os Bits só se ganham jogando.</span></li>
    <li><b>Sem culpa</b><span>Nenhuma contagem nem aviso insistente para você voltar.</span></li>
    <li><b>Sem conta obrigatória</b><span>Entrar é escolha, e você pode apagar tudo.</span></li>
  </ul>
  {nota("4 · só o que já está decidido (CN-11, M-2, o princípio 5 do guia, CN-1). Não diz 'sem anúncios': a CN-12 prevê o vídeo pedido para a voz", "right:20px;top:20px", 320)}
</section>

<section class="pi-fim" aria-labelledby="pi-fim">
  <h2 id="pi-fim">O ovo está esperando</h2>
  {JOGAR}
  <ul class="pi-garantias" aria-label="Para começar">{GARANTIAS}</ul>
</section>
</main>

<footer class="pi-rodape">
  <nav aria-label="Rodapé"><a href="#termos">Termos</a><a href="#privacidade">Privacidade</a><a href="#creditos">Créditos</a></nav>
  <span>Sprites, ícones e fundos: Digimon UP (Bandai).</span>
  <span>DigiLab é um projeto pessoal.</span>
</footer>

<div class="pi-fixo"><a class="bt acao" href="#/pet">{ic("play")}Começar agora</a></div>
</div></body></html>
'''


def escrever() -> None:
    (AQUI / "inicial.html").write_text(pagina(), encoding="utf-8", newline="\n")
    print("inicial.html")


if __name__ == "__main__":
    escrever()
