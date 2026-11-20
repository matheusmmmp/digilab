# Gera as duas pranchas da B3 (390 e 1280 px); a pele vem de ?pele=vidro|xcom no endereco, e ?sem tira as notas amarelas.
# Uso: python docs/pranchas/b3/gerar.py   (escreve luta_390.html e luta_1280.html ao lado). So desenho; nenhum codigo do jogo.
from pathlib import Path

A = "../../../../Assets/arena_up"  # fora do git (UI_GUIDELINES 5.1); so as capturas precisam dele
PAUSA = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 3h3v10H4zM9 3h3v10H9z"/></svg>'


def cab(titulo: str, cls: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>B3 · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;600;700&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="luta.css">
<style>:root{{--assets-fundo:url("{A}/mapas/ringue_fundo.jpg");--assets-piso:url("{A}/mapas/ringue_piso.jpg");--assets-sprA:url("{A}/sprites/Gabumon.png");--assets-sprB:url("{A}/sprites/Monochromon.png")}}</style>
<script>const q=new URLSearchParams(location.search);if((q.get("pele")||"vidro")==="vidro")document.documentElement.dataset.pele="vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body class="{cls}">'''


def corpo(celular: bool) -> str:
    def ret(s: str) -> str:
        return f'<span class="ret"><i style="background-image:var(--assets-spr{s})"></i></span>'
    if celular:
        notas = '''<span class="nota" style="left:10px;top:118px">HUD no sistema da tela Pet</span>
<span class="nota" style="left:10px;bottom:146px">regra em uso, faixa embaixo (B3-3)</span>
<span class="nota" style="left:50%;bottom:74px;transform:translateX(-50%)">dock da luta (B3-4)</span>'''
    else:
        notas = '''<span class="nota" style="left:50%;top:128px;transform:translateX(-50%)">cena a tela inteira (B3-2); sem trilho (B3-1)</span>
<span class="nota" style="right:16px;top:72px">regra em uso, à direita (B3-3)</span>
<span class="nota" style="left:50%;bottom:78px;transform:translateX(-50%)">dock da luta (B3-4)</span>'''
    return f'''
<div class="palco" role="img" aria-label="Palco da luta: Gabumon contra Monochromon">
  <div class="fundo"></div><div class="piso"></div>
  <div class="sombra" style="left:calc(var(--lut-a) + 12px)"></div><div class="lut a"></div>
  <div class="sombra" style="left:calc(var(--lut-b) + 12px)"></div><div class="lut b"></div>
  <span class="num dano" style="left:calc(var(--lut-b) + 90px);bottom:calc(var(--lut-y) + 190px)">-12,4</span>
</div>
<header class="hud">
  <div class="caixa plaq a">{ret("A")}<span class="txt"><span class="nome">Gabumon</span><span class="bar vida" role="img" aria-label="vida do seu pet"><i style="--v:78%"></i></span><span class="bar guts" role="img" aria-label="guts do seu pet"><i style="--v:34%"></i></span></span></div>
  <div class="caixa rel" aria-label="tempo da luta"><small>TEMPO</small><b>0:03</b><em>até 1:20</em></div>
  <div class="caixa plaq b">{ret("B")}<span class="txt"><span class="nome">Monochromon</span><span class="bar vida" role="img" aria-label="vida do rival"><i style="--v:56%"></i></span><span class="bar guts" role="img" aria-label="guts do rival"><i style="--v:81%"></i></span></span></div>
</header>
<div class="caixa modo">Arena · treino</div>
<section class="caixa regra" aria-live="polite"><h2>Regra em uso</h2><div class="corpo"><small>O que Gabumon faz</small><span>se distância é perto e meu guts ≥ 20 → golpe rápido</span></div></section>
<nav class="caixa dock" aria-label="Controles da luta">
  <button class="bt" aria-label="Pausar a animação" aria-pressed="false">{PAUSA}</button>
  <button class="bt" aria-label="Velocidade dobrada" aria-pressed="true">×2</button>
  <span class="sep"></span>
  <button class="bt perigo">Desistir</button>
</nav>
{notas}
</body></html>
'''


d = Path(__file__).parent
(d / "luta_390.html").write_text(cab("luta 390 px", "m") + corpo(True), encoding="utf-8", newline="\n")
(d / "luta_1280.html").write_text(cab("luta 1280 px", "d") + corpo(False), encoding="utf-8", newline="\n")
