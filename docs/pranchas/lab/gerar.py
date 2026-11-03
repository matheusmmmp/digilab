# Gera as pranchas da LM5a (docs/TAREFA_V3_LAB_MODULAR.md, secao 4): Ajustes > Laboratorio, a tela Pet com o pet de teste e o painel do
# DigiBrain modular, cada uma em 390 e 1280 px. A pele vem de ?pele=vidro|xcom no endereco; ?sem tira as notas amarelas e as linhas de fonte.
# Uso: python docs/pranchas/lab/gerar.py   (escreve <tela>_390.html e <tela>_1280.html ao lado). So desenho; nenhum codigo do jogo.
# Os numeros dos exemplos sao inventados para o desenho (um motivo coerente com a conta do digilab/digibrain/); a origem de cada campo
# esta no LEIA.md.
from pathlib import Path

A = "../../../../Assets"  # fora do git (UI_GUIDELINES 5.1); so as capturas precisam dele


def cab(titulo: str, cls: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LM5a · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;600;700&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="lab.css">
<style>:root{{--assets-fundo:url("{A}/arena_up/mapas/floresta_fundo.png");--assets-piso:url("{A}/arena_up/mapas/floresta_piso.jpg");--assets-spr:url("{A}/arena_up/sprites/Agumon.png");--assets-ovo:url("{A}/eggs/egg_1.png")}}</style>
<script>const q=new URLSearchParams(location.search);if((q.get("pele")||"vidro")==="vidro")document.documentElement.dataset.pele="vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body class="{cls}">'''


FIM = "\n</body></html>\n"
RET = '<span class="ret"><i></i></span>'


def nota(txt: str, estilo: str) -> str:
    return f'<span class="nota" style="{estilo}">{txt}</span>'


# ---------------------------------------------------------------- 1. Ajustes > Laboratorio
def ajustes(m: bool) -> str:
    pos = "left:10px;right:10px;top:34px" if m else "right:16px;top:16px;bottom:16px;width:500px"
    notas = (nota("modal centralizado, como as outras telas no celular", "left:10px;top:8px") if m else
             nota("painel à direita (≥ 900 px), como Ajustes de hoje", "right:530px;top:24px"))
    return f'''
<div class="cena escura"><div class="fundo"></div><div class="piso"></div></div>
<section class="caixa painel-aj" style="{pos}" aria-label="Ajustes · Laboratório">
  <header><h1>Ajustes</h1><button class="bt" style="min-height:40px;padding:0 12px" aria-label="Fechar">×</button></header>
  <div class="abas"><span>Geral</span><span>Som</span><span>Fala</span><span class="on">Laboratório</span></div>
  <div class="sec" style="border:0;padding:0">
    <h2>O que é o laboratório</h2>
    <p>Um pet de teste com o <b>DigiBrain modular</b>: cada decisão dele mostra qual módulo pesou. Os pets de hoje seguem com o cérebro A v11 e não mudam.</p>
    <small>É para ver o modular jogando. Nada que acontece aqui vira medida de pesquisa.</small>
  </div>
  <div class="sec">
    <div class="chave on" role="switch" aria-checked="true" aria-label="Modo laboratório"><span class="tr"><i></i></span><b>Modo laboratório · ligado</b></div>
    <small>Desligado, o botão de chocar some e o jogo fica como está. O pet de teste, se existir, fica guardado.</small>
  </div>
  <div class="sec">
    <h2>Pet de teste</h2>
    <div class="pt-lista">{RET.replace("ret", "ret ovo")}<span style="display:grid;gap:2px"><b>Nenhum pet de teste ainda</b><small>O ovo nasce aqui, não em Meus pets.</small></span></div>
    <button class="bt prim" style="width:100%">Chocar o ovo de teste</button>
  </div>
  <div class="aviso"><b>Experimental</b><span>O pet de teste fica num espaço próprio do save, ao lado dos seus pets, e não troca o cérebro de nenhum deles. Ele leva o selo “experimental” na tela do Pet.</span></div>
</section>
{notas}
  {nota("seção só existe com a chave de laboratório (LAB-2); a chave nasce desligada", "left:10px;bottom:8px" if m else "right:530px;bottom:20px")}'''


# ---------------------------------------------------------------- 2. tela Pet com o pet de teste
def tela_pet(m: bool) -> str:
    necs = "".join(f'<div class="nec"><span>{n}</span><span class="bar"><i style="--v:{v}%;--c:{c}"></i></span></div>'
                   for n, v, c in (("Comida", 72, "var(--hx-ok)"), ("Energia", 58, "var(--hx-ok)"), ("Higiene", 86, "var(--hx-ok)"), ("Humor", 40, "var(--hx-alerta)")))
    nav = "".join(f'<span class="ic{" on" if i == 0 else ""}">{t}</span>' for i, t in enumerate(("Pet", "Crescer", "Lutar", "Diário")))
    rail = '<span class="ic">Chat</span><span class="ic">Cérebro</span><span class="ic">Ajustes</span>'
    if m:
        lay = f'''
<div class="pet" style="left:calc(50% - 95px);bottom:23%"></div><div class="sombra" style="left:calc(50% - 60px);bottom:calc(23% - 6px);width:120px;height:24px"></div>
<div class="caixa plaq" style="left:10px;top:10px;right:112px">{RET}<span class="col"><span class="nm">Agumon</span><span><span class="selo">experimental</span></span></span></div>
<div class="caixa rel" style="right:10px;top:10px;min-width:92px"><small>HORA</small><b>14:32</b></div>
<div class="caixa trilho-ic" style="right:10px;top:76px;grid-auto-flow:column">{rail}</div>
<div class="caixa balao" style="left:20px;top:196px">Cheguei perto do lugar de antes.</div>
<div class="caixa pilha" style="left:10px;right:10px;bottom:84px">{necs}</div>
<nav class="caixa nav" style="left:10px;right:10px;bottom:10px;justify-content:space-between">{nav}</nav>'''
        notas = (nota("selo na plaquinha; o resto do HUD é o de hoje", "left:12px;top:70px") +
                 nota("o botão Cérebro abre o painel do modular (folha)", "right:10px;top:124px"))
    else:
        lay = f'''
<div class="pet" style="left:calc(50% - 142px);bottom:21%"></div><div class="sombra" style="left:calc(50% - 90px);bottom:calc(21% - 8px);width:180px;height:34px"></div>
<div class="caixa plaq" style="left:16px;top:16px;min-width:300px">{RET}<span class="col"><span class="nm">Agumon</span><span><span class="selo">experimental</span></span></span></div>
<div class="caixa rel" style="left:50%;transform:translateX(-50%);top:16px;min-width:110px"><small>HORA</small><b>14:32</b></div>
<div class="caixa trilho-ic" style="left:16px;top:96px">{rail}</div>
<div class="caixa balao" style="left:calc(50% + 70px);top:240px">Cheguei perto do lugar de antes.</div>
<div class="caixa pilha" style="right:16px;top:16px;width:240px">{necs}</div>
<nav class="caixa nav" style="left:50%;transform:translateX(-50%);bottom:16px">{nav}</nav>'''
        notas = (nota("selo na plaquinha; o resto do HUD é o de hoje", "left:330px;top:24px") +
                 nota("o botão Cérebro abre o painel do modular", "left:84px;top:150px"))
    return '\n<div class="cena"><div class="fundo"></div><div class="piso"></div></div>' + lay + notas


# ---------------------------------------------------------------- 3. o painel do DigiBrain modular
def barra(nome: str, v: float, fonte: str) -> str:
    cl = "neg" if v < 0 else "pos"
    w = min(50.0, abs(v) * 50)  # a barra vai do centro (0) a cada ponta (+-100% da soma da unidade escolhida)
    sinal = "+" if v > 0 else "−" if v < 0 else ""
    return (f'<li><span>{nome}</span><span class="tr"><b class="{cl}" style="--w:{w:.1f}%"></b></span>'
            f'<em>{sinal}{abs(v) * 100:.0f}%</em><span class="fonte" style="grid-column:1/-1;margin-top:-3px">{fonte}</span></li>')


def chance(nome: str, p: int, esc: bool = False) -> str:
    return (f'<li class="{"esc" if esc else ""}"><span>{nome}{" · escolhida" if esc else ""}</span>'
            f'<span class="tr"><b style="--w:{p}%"></b></span><em>{p}%</em></li>')


def painel(m: bool) -> str:
    pos = "left:0;right:0;top:120px" if m else "right:0;top:0;bottom:0;width:480px"
    barras = "".join([
        barra("Lugar lembrado", 240 / 540, "unidades[escolha].termos.memoria ÷ .soma"),
        barra("Inato", 200 / 540, "termos.inato ÷ soma"),
        barra("Lembrança", 90 / 540, "termos.lembranca ÷ soma"),
        barra("Persistência", 70 / 540, "termos.persistencia ÷ soma"),
        barra("Hábito (P2)", -60 / 540, "termos.habito ÷ soma"),
    ])
    ult = "".join(f'<li><span class="h">{h}</span>{a}</li>' for h, a in (("14:30", "explorar"), ("14:12", "explorar"), ("13:58", "ocioso"), ("13:40", "chamar você"), ("13:21", "dormir")))
    corpo = f'''
<aside class="caixa db" style="{pos}" aria-label="DigiBrain modular">
  <div class="topo"><h1>DigiBrain</h1><span style="display:flex;gap:8px;align-items:center"><span class="selo">modular · experimental</span><button class="bt" style="min-height:40px;padding:0 12px" aria-label="Fechar">×</button></span></div>
  <section class="agora"><h2>Agora</h2><b>Explorar o lugar lembrado</b>
    <small>Sem o lugar lembrado, teria explorado pelo cheiro.</small>
    <span class="fonte">motivo.acao, motivo.escolha · motivo.sondas.sem_memoria, .memoria_decidiu</span></section>
  <section><h2>Lembrança da vez</h2>
    <div class="lembr"><b>Lembrou do lugar (14, 9)</b>
      <small>de um episódio guardado na memória duradoura · semelhança 72% · peso na escolha +17%</small></div>
    <span class="fonte">motivo.alvo {{tipo "ponto", x, y, do_mem}} · motivo.lembranca {{recuperado, memoria, sim, sigma, L}}</span>
    <small>Sem lembrança, o bloco diz “Nada lembrado nesta decisão.”</small></section>
  <section><h2>O peso de cada módulo nesta escolha</h2>
    <ul class="barras" role="list">{barras}</ul>
    <small>Sem contribuição agora: incentivo (P1), objeto à vista.</small>
    <small>Cada barra é a parte da soma da unidade escolhida; para a esquerda da linha, o módulo puxou contra.</small></section>
  <section><h2>Intenção em curso</h2>
    <div class="kv"><span>Explorar → lugar (14, 9)</span><em>desde a decisão 41</em><span>Compromisso</span><em>62%</em><span>Frustração</span><em>12%</em><span>Passos sem avançar</span><em>2</em></div>
    <span class="fonte">motivo.estado {{I, C, n_sp, F}} · estado_interno().modulos.estado.I.inicio</span></section>
  <section><h2>As opções e a chance de cada uma</h2>
    <ul class="chances" role="list">{chance("explorar · lugar (14, 9)", 55, True)}{chance("explorar · cheiro", 25)}{chance("ocioso", 12)}{chance("chamar você", 8)}</ul>
    <span class="fonte">motivo.unidades[i].w ÷ soma dos w (com o reflexo do sono não há sorteio: uma opção só)</span></section>
  <section><h2>O que mudaria a escolha</h2>
    <div class="chips"><span class="sim">sem o lugar lembrado: sim</span><span>sem a lembrança: não</span><span>sem o hábito: não</span><span>sem o incentivo: não</span><span>sem a persistência: não</span><span>só o inato: sim</span></div>
    <span class="fonte">motivo.sondas.{{sem_memoria, sem_lembranca, sem_habito, sem_incentivo, sem_persistencia, so_inato}} e os campos *_decidiu</span></section>
  <section><h2>Últimas ações</h2><ol class="ult" role="list" style="list-style:none;padding:0;display:grid;gap:6px">{ult}</ol>
    <span class="fonte">Motor.historico (quem = pet), como o painel do A v11</span></section>
</aside>'''
    notas = (nota("folha que sobe de baixo, até 85% da altura, com rolagem", "left:12px;top:10px") if m else
             nota("coluna à direita, como o painel do A v11", "right:490px;top:12px"))
    return ('\n<div class="cena"><div class="fundo"></div><div class="piso"></div></div>'
            '\n<div class="pet" style="left:calc(50% - 95px);bottom:60%;opacity:.9;transform:scale(.5);transform-origin:bottom"></div>' + corpo + notas)


d = Path(__file__).parent
for nome, f, rot in (("ajustes", ajustes, "Ajustes › Laboratório"), ("pet", tela_pet, "tela Pet com o pet de teste"), ("painel", painel, "painel DigiBrain modular")):
    (d / f"{nome}_390.html").write_text(cab(f"{rot} 390 px", "m") + f(True) + FIM, encoding="utf-8", newline="\n")
    (d / f"{nome}_1280.html").write_text(cab(f"{rot} 1280 px", "d") + f(False) + FIM, encoding="utf-8", newline="\n")
