# Gera as duas pranchas da P1 da UX_TELA_PET (a proposta B refinada: a linha do agora e o chip de causa), a 390 e a 1920 px.
# A pele vem de ?pele=vidro|xcom no endereco, e ?sem tira as notas amarelas.
# Uso: python docs/pranchas/ux-pet/gerar.py   (escreve pet_390.html e pet_1920.html ao lado). So desenho; nenhum codigo do jogo.
# Os textos da tela sao os do jogo (DigiBrain.tsx: REGRA_TXT, ACAO_CURTA e as frases do "Agora"; nomes.ts: NOME_PET; expressao.ts:
# ACOES_VIDA_TXT e FATORES_TXT); os numeros (64 %, 07:42, Dia 3) sao exemplo de layout, nunca dado.
from pathlib import Path

A = "../../../../Assets/arena_up"  # fora do git (UI_GUIDELINES 5.1); so as capturas precisam dele

# icones simples (traco), so para a prancha; no jogo sao os lucide de hoje
IC = {
    "pet": '<circle cx="12" cy="13" r="6"/><circle cx="7" cy="5" r="1.6"/><circle cx="17" cy="5" r="1.6"/>',
    "crescer": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "lutar": '<path d="M5 19L19 5"/><path d="M14 5h5v5"/><path d="M5 14l5 5"/>',
    "diario": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 8h6M9 12h6"/>',
    "conversar": '<path d="M4 5h16v11H9l-5 4z"/>',
    "ajustes": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>',
    "estado": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "evolucao": '<path d="M3 17l6-6 4 4 8-8"/>',
    "acoes": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "digibrain": '<path d="M12 4c-4 0-7 3-7 7 0 4 3 8 7 8s7-4 7-8c0-4-3-7-7-7z"/><path d="M12 4v15"/>',
}


def svg(n: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>'


def nav_bt(n: str, rotulo: str) -> str:
    atual = ' aria-current="page"' if n == "pet" else ""
    return f'<button type="button" class="nav-bt"{atual}>{svg(n)}{rotulo}</button>'


def cab(titulo: str, cls: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UX Pet P1 · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600;700;800;900&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="pet.css">
<style>:root{{--assets-spr:url("{A}/sprites/Gabumon.png")}}</style>
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.pele=q.get("pele")==="xcom"?"xcom":"vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body class="{cls}">'''


# ---- a linha do agora: os cinco casos da tabela "Sempre visivel" do plano
def agora(caso: str, curta: bool = False, fixa: bool = True) -> str:
    seta = '<span class="seta" aria-hidden="true">›</span>'
    if caso == "aprendido":
        acao, rot = "brincando", "Agora: brincando. Aprendido: sem ele, à toa. Abrir o porquê no DigiBrain"
        meio = ('<span class="chip aprendido"><b>aprendido</b></span>' if curta
                else '<span class="chip aprendido"><b>aprendido</b> · sem ele: à toa</span>')
    elif caso == "instinto":
        acao, rot = "explorando", "Agora: explorando. Tempo livre: o instinto faria o mesmo. Abrir o porquê no DigiBrain"
        meio = '<span class="neutro">instinto</span>' if curta else '<span class="neutro">Tempo livre · o instinto faria o mesmo</span>'
    elif caso == "uma":
        acao, rot = "dormindo", "Agora: dormindo. Exausto: só havia uma opção. Abrir o porquê no DigiBrain"
        meio = '<span class="neutro">uma opção</span>' if curta else '<span class="neutro">Exausto · só havia uma opção</span>'
    elif caso == "sem":
        acao, rot = "à toa", "Agora: à toa. Sem motivo registrado. Abrir o DigiBrain"
        meio = '<span class="chip sem"><span class="q">?</span>sem motivo registrado</span>'
    elif caso == "modular":
        acao, rot = "brincando", "Agora: brincando. Cérebro modular. Abrir o porquê no DigiBrain"
        meio = '<span class="neutro">cérebro modular</span>'
    else:
        raise ValueError("caso desconhecido: " + caso)
    pressionado = ' aria-pressed="false" aria-controls="pet-painel"' if fixa else ' tabindex="-1"'
    return (f'<button type="button" class="caixa agora"{pressionado} aria-label="{rot}">'
            f'<span class="rot">agora</span><span class="acao">{acao}</span><span class="ponto" aria-hidden="true">·</span>{meio}{seta}</button>')


def balao() -> str:
    # o motivo do treino com pausa no Rookie: ACOES_VIDA_TXT.treinar_cansado "[sem pausa]" + o marcador de fadiga_treino
    return '''<button type="button" class="caixa balao" aria-haspopup="dialog" title="Toque para ver o porquê">
  <span class="fala">[sem pausa] <span class="marca">treino puxado</span></span>
  <span class="chip corpo"><b>vem do corpo</b> · treino puxado</span>
  <small>toque para ver o porquê</small></button>
<svg class="rabicho" viewBox="0 0 24 14" aria-hidden="true"><path class="f" d="M0 0L12 14L24 0z"/><path class="l" d="M0 0L12 14L24 0"/></svg>'''


def retrato() -> str:
    return '<button type="button" class="retrato" aria-label="Meus pets"><i></i></button>'


def corpo_1920() -> str:
    nav = "".join(nav_bt(n, r) for n, r in [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário"),
                                              ("conversar", "Conversar"), ("ajustes", "Ajustes")])
    med = lambda r, v, t="": f'<div class="med {t}"><span class="rot">{r}</span><span class="tri" role="img" aria-label="{r} {v} de 100"><i style="--v:{v}%"></i></span><em>{v} %</em></div>'
    dock = "".join(f'<button type="button">{a}</button>' for a in ["Alimentar", "Brincar", "Limpar", "Carinho", "Tapa", "Tratar", "Mais"])
    quadro = f'''<section class="caixa quadro" aria-label="Quadro da prancha: os estados da linha do agora e do chip">
  <h2>Quadro da prancha · os estados</h2>
  <div class="caso"><small>o aprendido mudou a escolha (quem_decidiu.mudou)</small>{agora("aprendido", fixa=False)}</div>
  <div class="caso"><small>o instinto bastava (escolha, sem mudar)</small>{agora("instinto", fixa=False)}</div>
  <div class="caso"><small>uma opção só (sem escolha)</small>{agora("uma", fixa=False)}</div>
  <div class="caso"><small>antes da 1ª decisão (decisao null)</small>{agora("sem", fixa=False)}</div>
  <div class="caso"><small>o modular decide (Motor.lab)</small>{agora("modular", fixa=False)}</div>
  <div class="sep"></div>
  <div class="caso"><small>balão: treino com pausa (fadiga_treino)</small><span><span class="chip corpo"><b>vem do corpo</b> · treino puxado</span></span></div>
  <div class="caso"><small>balão: outro fator, só o marcador (hoje não ocorre)</small><span><span class="chip neutro">costume</span></span></div>
  <div class="caso"><small>balão: sem fator ou exploração</small><span><span class="chip sem"><span class="q">?</span>sem motivo registrado</span></span></div>
</section>'''
    return f'''
<div class="cena" role="img" aria-label="Fundo neutro no lugar da ilha 3D, com o Gabumon"><div class="sombra"></div><div class="pet"></div></div>
<header class="topo">
  <div class="caixa topo-pet">{retrato()}<span class="topo-pet-txt"><b>Gabumon</b><small>Rookie</small></span></div>
  {agora("aprendido")}
  <span class="logo">DIGILAB</span>
  <div class="caixa relogio"><span class="hora"><small>Dia 3</small><b>07:42</b></span><span class="salvo">● salvo</span></div>
</header>
<nav class="caixa trilho" aria-label="Navegação">{nav}</nav>
{balao()}
<aside class="pilha" aria-label="Painéis do pet">
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="true">{svg("estado")}<span class="tit">Estado atual</span><span class="risca"></span></button>
    <div class="painel-corpo">{med("comida", 64)}{med("energia", 81)}{med("higiene", 40, "alerta")}{med("humor", 72)}{med("saúde", 95, "ok")}
      <button type="button" class="detalhes" aria-expanded="false">Detalhes ›</button></div></section>
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false">{svg("evolucao")}<span class="tit">Evolução<span class="resumo">próxima forma em 2 h</span></span><span class="risca"></span></button></section>
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false">{svg("acoes")}<span class="tit">Últimas ações<span class="resumo">07:40 · carinho</span></span><span class="risca"></span></button></section>
</aside>
<button type="button" class="caixa p etiqueta-db" aria-pressed="false" aria-controls="pet-painel">{svg("digibrain")}DigiBrain</button>
<nav class="caixa dock" aria-label="Ações">{dock}</nav>
{quadro}
<span class="nota" style="left:180px;top:66px">NOVA: a linha do agora, sempre visível; abre o DigiBrain (P1-3)</span>
<span class="nota" style="left:calc(50% + 180px);top:470px">balão de hoje (15 s) sobre o pet + o chip embaixo da fala (P1-1)</span>
<span class="nota" style="left:50%;top:76px;transform:translateX(-50%)">o cartão do chamado continua aqui, no alto ao centro (não desenhado)</span>
<span class="nota" style="right:16px;top:440px">pilha, trilho, dock e etiqueta: sem mudança</span>
<span class="nota" style="left:104px;top:424px">quadro só da prancha: os estados lado a lado</span>
</body></html>
'''


def corpo_390() -> str:
    lado = "".join(f'<button type="button" aria-label="{r}" aria-pressed="false" aria-controls="pet-painel">{svg(n)}</button>'
                   for n, r in [("estado", "Estado atual"), ("evolucao", "Evolução"), ("acoes", "Últimas ações"), ("digibrain", "DigiBrain")])
    dock = "".join(f'<button type="button">{a}</button>' for a in ["Alimentar", "Brincar", "Limpar", "Carinho"]) + '<button type="button" class="mais" aria-label="Mais ações">…</button>'
    barra = "".join(nav_bt(n, r) for n, r in [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário")])
    return f'''
<div class="cena" role="img" aria-label="Fundo neutro no lugar da ilha 3D, com o Gabumon"><div class="sombra"></div><div class="pet"></div></div>
<header class="topo">
  <div class="caixa topo-pet">{retrato()}<span class="topo-pet-txt"><b>Gabumon</b><small>Rookie</small></span></div>
  <div class="caixa relogio"><span class="hora"><small>Dia 3</small><b>07:42</b></span><span class="salvo">● salvo</span></div>
  <button type="button" class="topo-bt" aria-label="Conversar">{svg("conversar")}</button>
  <button type="button" class="topo-bt" aria-label="Ajustes">{svg("ajustes")}</button>
</header>
{agora("sem")}
<div class="caixa alerta-pos" aria-hidden="true">lugar do chamado / resumo (15 s), 50 px abaixo de hoje</div>
<nav class="lado" aria-label="Painéis do pet">{lado}</nav>
{balao()}
<nav class="caixa dock" aria-label="Ações">{dock}</nav>
<nav class="barra" aria-label="Navegação">{barra}</nav>
<span class="nota" style="left:10px;top:176px">NOVA: a linha do agora, acima (o caso mais largo, o "?")</span>
<span class="nota" style="left:10px;top:200px">o cartão do chamado desce de 70 para 120 px</span>
<span class="nota" style="left:10px;top:340px">balão sobre o pet + chip (P1-1)</span>
</body></html>
'''


d = Path(__file__).parent
(d / "pet_390.html").write_text(cab("pet 390 px", "m") + corpo_390(), encoding="utf-8", newline="\n")
(d / "pet_1920.html").write_text(cab("pet 1920 px", "d") + corpo_1920(), encoding="utf-8", newline="\n")
