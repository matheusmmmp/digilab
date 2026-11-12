# Gera o ESBOCO B da pagina de entrada (2026-11-12): o Matheus mandou mais uma imagem de referencia (uma pagina de jogo escura, com o
# personagem grande no meio do nome, os ladrilhos coloridos da colecao e o celular com fichas flutuando) e pediu: "Gere tambem um esboco
# usando como referencia essa imagem". E uma segunda opcao, ao lado da pagina clara (gerar.py); as duas dizem as mesmas coisas.
# So desenho; nenhum codigo do jogo. Uso (da raiz): python docs/pranchas/ux-pagina-inicial/gerar_b.py   (escreve inicial_b.html)
#
# O QUE VEM DA REFERENCIA: a moldura fina com a aba em cima; o palco escuro com o nome gigante e o personagem por cima das letras; o
# rabisco inclinado; a faixa de riscas; a ficha do canto com os dois ladrilhos e o botao redondo; a fileira de ladrilhos de cor, de
# tamanhos diferentes; o horizonte; o texto ao lado de um celular com fichas flutuando.
# O QUE NAO VEM: "tap to earn", NFT, moeda trocada por dinheiro e contagem regressiva. O jogo nao tem nada disso (CN-11: sem gacha e
# sem venda de vantagem; o guia, principio 5: sem contagem para prender).
# As afirmacoes da pagina sao as mesmas do gerar.py (a origem de cada uma esta no cabecalho de la).
# EXEMPLO DE LAYOUT, NUNCA DADO: "explorar 48 %, comer 31 %, dormir 21 %", a ficha "Agumon · Rookie" e os codigos dos ladrilhos.
import importlib.util
from pathlib import Path

# o gerar.py ao lado (o pet, os icones, a pasta), carregado com outro nome: ele mesmo importa o "gerar" da prancha dos lugares
_esp = importlib.util.spec_from_file_location("gerar_pagina", Path(__file__).parent / "gerar.py")
P = importlib.util.module_from_spec(_esp)
_esp.loader.exec_module(P)

G, AQUI, pet, ic = P.G, P.AQUI, P.pet, P.ic


def nota(txt: str, estilo: str, w: int = 280) -> str:
    return f'<span class="nota" style="{estilo};max-width:{w}px">{txt}</span>'


def ladrilho(nome: str, k: float, cor: str, cls: str = "", extra: str = "") -> str:
    return f'<span class="ladrilho {cor} {cls}">{pet(nome, k)}{extra}</span>'


def rotulo(nome: str, nivel: str) -> str:
    return f'<span class="rotulo lcd"><b>{nome}</b>{nivel}</span>'


def pagina() -> str:
    garantias = "".join(f"<li>{G.svg('check')} {t}</li>" for t in ["No navegador", "Sem conta", "Sem instalar"])
    ops = "".join(f'<span class="op"><span>{o}</span><i><b style="width:{p}%"></b></i><span>{p} %</span></span>'
                  for o, p in [("explorar", 48), ("comer", 31), ("dormir", 21)])
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DigiLab · a página de entrada (prancha, esboço B)</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Barlow:wght@400;500;600;700&family=DotGothic16&family=Saira+Condensed:wght@600;700&display=swap">
<link rel="stylesheet" href="inicial_b.css">
<script>if(new URLSearchParams(location.search).has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body>
<div class="moldura"><span class="aba lcd" aria-hidden="true">[ DigiLab ]</span>

<header class="palco" aria-labelledby="h1">
  <a class="logo" href="#topo" aria-label="DigiLab"><i aria-hidden="true"></i>DIGILAB</a>
  <nav class="menu" aria-label="Nesta página"><a href="#dia">Primeiro dia</a><a href="#pets">Os Digimon</a><a href="#cerebro">DigiBrain</a></nav>
  <div class="topo-dir"><a class="bt fantasma" href="#/config/conta">Entrar</a><a class="bt" href="#/pet">{ic("play")}Jogar agora</a></div>
  <span class="rabisco" aria-hidden="true">pet com cérebro</span>
  <h1 class="nome" id="h1"><span>Digi</span><span>Lab</span></h1>
  <span class="heroi-pet">{pet("Agumon", 6)}</span>
  <div class="riscas" aria-hidden="true"></div>
  <p class="frase">Crie um Digimon<br>que <em>decide</em><br>sozinho</p>
  <a class="redondo" href="#/pet" aria-label="Começar agora">{ic("play")}</a>
  <div class="selo"><span><span class="n">4</span><br><span class="lcd">brasões<br>para o ovo</span></span>
    {ladrilho("Koromon", .9, "c-destaque")}{ladrilho("Tsunomon", .9, "c-sombria")}</div>
  <div class="lado" aria-hidden="true"><span>{G.svg("pet")}</span><span>{G.svg("treinar")}</span><span>{G.svg("lutar")}</span></div>
  {nota("B1 · o palco da referência: o nome gigante e o pet por cima das letras, o rabisco, as riscas, a frase embaixo. 'Jogar agora' no canto e o botão redondo levam direto ao jogo (CN-1)", "left:420px;top:74px", 320)}
  {nota("no lugar do '10K NFTs': os quatro brasões do ovo. Sem contagem regressiva (guia, princípio 5)", "right:24px;bottom:150px", 260)}
</header>

<section class="sec" id="dia" aria-labelledby="t1">
  <span class="solto s1">{pet("Botamon", 2.6)}</span><span class="solto s2">{pet("Koromon", 1.1)}</span><span class="solto s3">{pet("Tokomon", 2.4)}</span>
  <div class="dia"><span></span>
    <div class="txt"><span class="rabisco" aria-hidden="true">primeiro dia</span><h2 id="t1">O ovo é seu</h2>
      <p>Você escolhe um brasão e recebe um ovo. Ele choca num <b>In-Training</b>, que cresce com o que vive. Abre no navegador, sem conta.</p></div></div>
  {nota("B2 · os bebês soltos pelos lados, no lugar das pedras flutuando", "left:30px;top:20px", 240)}
</section>

<section id="pets" aria-label="Alguns Digimon do jogo">
  <div class="fileira">
    {ladrilho("Palmon", 2.2, "c-ok", "gg")}
    {rotulo("Biyomon", "Rookie")}
    {ladrilho("Gomamon", 1.3, "c-destaque")}
    {ladrilho("Agumon", 2.6, "c-acao", "gg", '<span class="cod">ROOKIE</span>')}
    {rotulo("Patamon", "Rookie")}
    {ladrilho("Koromon", 1.1, "c-navy")}
    {ladrilho("Biyomon", 1.5, "c-sombria")}
    {rotulo("Gomamon", "Rookie")}
    {ladrilho("Patamon", 1.4, "c-nec")}
    {rotulo("Koromon", "In-Training")}
  </div>
  <div class="horizonte" role="img" aria-label="A ilha do jogo, ao longe"></div>
</section>

<section class="sec" id="cerebro" aria-labelledby="t2">
  <div class="cerebro">
    <div class="txt"><span class="rabisco" aria-hidden="true">DigiBrain</span><h2 id="t2">Veja o que<br>ele pensa</h2>
      <p>Cada pet tem uma rede própria, que muda com a vida dele. O jogo mostra a <b>escolha de agora</b> e a chance de cada opção, sem texto inventado.</p>
      <div class="recurso"><header><span class="lcd">O que tem no jogo</span><span class="lcd">01 / 03</span></header>
        <b>Cuidar e ensinar</b><small>Ponha a comida na ilha, brinque, elogie ou corrija. Ele lembra.</small>
        <div class="setas" aria-hidden="true"><span>{G.svg("seta")}</span><span>{G.svg("seta")}</span></div></div>
    </div>
    <div class="aparelho">
      <div class="fone"><span class="cab lcd">{G.svg("digibrain")}DigiBrain</span>
        <img src="../digibrain-lab/scan_lab_mapa_1280.png" alt="O DigiBrain aberto no jogo: a rede do pet e a escolha de agora">
        <span class="cena">{pet("Agumon", 2.4)}</span></div>
      <div class="flut fl1"><span class="lcd">Espécime</span><b>Agumon</b><span class="lcd">Rookie · Coragem</span></div>
      <div class="flut fl2"><span class="lcd">Escolha de agora</span>{ops}</div>
      <div class="flut fl3"><span class="etq-apr">aprendido com você</span></div>
    </div>
  </div>
  {nota("B3 · o texto ao lado do celular com fichas flutuando. Dentro dele, a captura real do DigiBrain. As porcentagens são EXEMPLO. A ficha '01 / 03' passaria por cuidar, treinar e lutar", "right:30px;top:40px", 300)}
  {nota("as cores dos ladrilhos são emprestadas de tokens que têm sentido fixo no jogo (PI-5)", "left:30px;top:20px", 260)}
</section>

<section class="fim" aria-labelledby="t3">
  <h2 id="t3">O ovo está esperando</h2>
  <a class="bt grande" href="#/pet">{ic("play")}Começar agora</a>
  <ul class="garantias lcd" aria-label="Para começar">{garantias}</ul>
</section>
<footer class="rodape">
  <nav aria-label="Rodapé"><a href="#termos">Termos</a><a href="#privacidade">Privacidade</a><a href="#creditos">Créditos</a></nav>
  <span>Sprites, ícones e fundos: Digimon UP (Bandai). DigiLab é um projeto pessoal.</span>
</footer>
</div>
<div class="fixo"><a class="bt" href="#/pet">{ic("play")}Começar agora</a></div>
</body></html>
'''


if __name__ == "__main__":
    (AQUI / "inicial_b.html").write_text(pagina(), encoding="utf-8", newline="\n")
    print("inicial_b.html")
