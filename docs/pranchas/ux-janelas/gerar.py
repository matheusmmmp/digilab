# Gera a prancha "as janelas do pet: arrastar, esconder e arrumar" (docs/PLANO_UX_JANELAS.md). So desenho; nenhum codigo do jogo.
# O pedido do Matheus (2026-11-12): os menus "serem todos modulares, eles serem drag and drop", "deixar a aba de DigiBrain no meio da
# tela", "arrastar a aba de ultimas [acoes] para baixo, ou tirar ela", e em Ajustes "o exibir dedicado a cada janela".
# Usa os ajudantes da prancha dos lugares (a ilha, o topo, o trilho, o dock, o minimapa, a nota) e a caixa da prancha da conta.
# A pele vem de ?pele=vidro|xcom; ?sem tira as notas amarelas (no celular elas so aparecem com ?notas).
# Uso (da raiz): python docs/pranchas/ux-janelas/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# O QUE JA EXISTE NO JOGO (web/app/src, lido em 2026-11-12) E ESTA PRANCHA REUSA:
#   os paineis Estado atual, Evolucao, Ultimas acoes e a linha DigiBrain .... telas/pet/TelaPet.tsx (PainelHud, LinhaDigiBrain)
#   abrir e fechar cada painel, guardado no navegador ....................... TelaPet.tsx (useAbertosHud, a chave "-hud")
#   arrastar pelo cabecalho, com a posicao guardada ......................... hudPet.ts (useArrastavelPorAlca, a chave "-hud-arraste")
#   "Exibir detalhes do pet" e "Voltar os paineis ao lugar" ................. hudPet.ts e telas/config/TelaConfig.tsx
#   o scan do DigiBrain ..................................................... componentes/ScanDigiBrain.tsx (hoje um dialogo modal)
# EXEMPLO DE LAYOUT, NUNCA DADO: os valores dos medidores, as horas, as ultimas acoes, "Ultimate · 15h 15min" e as posicoes das janelas.
# Nenhum numero de jogo novo. Os tamanhos e as distancias de encaixe sao PROPOSTO, SEM FONTE.
import importlib.util
from pathlib import Path

AQUI = Path(__file__).parent
_esp = importlib.util.spec_from_file_location("gerar_conta", AQUI.parent / "ux-conta" / "gerar.py")
C = importlib.util.module_from_spec(_esp)
_esp.loader.exec_module(C)
G, M = C.G, C.M

C.IC.update({
    "alca": '<circle cx="9" cy="6" r="1.2"/><circle cx="15" cy="6" r="1.2"/><circle cx="9" cy="12" r="1.2"/><circle cx="15" cy="12" r="1.2"/><circle cx="9" cy="18" r="1.2"/><circle cx="15" cy="18" r="1.2"/>',
    "mais": '<circle cx="12" cy="5" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="12" cy="19" r="1.4"/>',
    "mover": '<path d="M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M12 21l-3-3M12 21l3-3M3 12l3-3M3 12l3 3M21 12l-3-3M21 12l-3 3"/>',
    "esconder": '<path d="M3 3l18 18M10.6 5.2A9.8 9.8 0 0 1 12 5c6 0 10 7 10 7a17 17 0 0 1-3.2 3.9M6.5 6.6A17 17 0 0 0 2 12s4 7 10 7a9.7 9.7 0 0 0 4-.9"/>',
    "voltar_lugar": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
    "grade": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    "mapa": '<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>',
})
ic = C.ic


def _css(h: str) -> str:
    h = h.replace('href="conta.css"', 'href="../ux-conta/conta.css">\n<link rel="stylesheet" href="janelas.css"')
    return h.replace("<title>A conta · ", "<title>As janelas do pet · ")


# ---------------------------------------------------------------------------------------------------- as janelas
def vital(rot: str, v: int) -> str:
    return f'<span class="vital"><span>{rot}</span><span class="barra" role="img" aria-label="{rot} {v} de 100"><i style="width:{v}%"></i></span><b>{v}</b></span>'


CORPO = {
    "estado": "".join(vital(r, v) for r, v in [("Comida", 64), ("Energia", 81), ("Higiene", 40), ("Humor", 72), ("Saúde", 95)]),
    "evolucao": '<span class="sec">Próxima forma em 15h 15min.</span>',
    "acoes": "".join(f'<span class="acao-l"><b>{h}</b><span>{a}</span></span>' for h, a in [("07:40", "carinho"), ("07:31", "treino: corrida"), ("07:12", "comeu a ração")]),
    "digibrain": '<img src="../digibrain-lab/scan_lab_mapa_1280.png" alt="O DigiBrain: a rede do pet e a escolha de agora">',
}
JAN = {   # id: (icone, titulo, resumo com a janela fechada)
    "estado": ("estado", "Estado atual", "comida 64 % · higiene 40 %"),
    "evolucao": ("evolucao", "Evolução", "Ultimate · 15h 15min"),
    "acoes": ("acoes", "Últimas ações", "07:40 · carinho"),
    "digibrain": ("digibrain", "DigiBrain", "o porquê das escolhas"),
}


def janela(jid: str, aberta: bool = False, x: float = None, y: float = None, w: int = 300, cls: str = "", menu: bool = False, extra: str = "") -> str:
    """um painel da pilha de hoje, solto: a alca, o icone, o titulo, o menu dos tres pontos e o abrir/fechar"""
    i, tit, res = JAN[jid]
    pos = "" if x is None else f' style="left:{x}px;top:{y}px;width:{w}px"'
    resumo = "" if aberta else f'<span class="resumo">{res}</span>'
    corpo = f'<div class="jn-corpo">{CORPO[jid]}</div>' if aberta else ""
    return (f'<section class="caixa jn {cls}" aria-label="{tit}"{pos}><header class="jn-cab"><span class="jn-alca" aria-hidden="true">{ic("alca")}</span>{G.svg(i)}'
            f'<span class="tit">{tit}{resumo}</span>'
            f'<button type="button" class="jn-bt" aria-label="Opções de {tit}" aria-haspopup="menu" aria-expanded="{"true" if menu else "false"}">{ic("mais")}</button>'
            f'<button type="button" class="jn-bt{" aberto" if aberta else ""}" aria-label="{"Recolher" if aberta else "Abrir"} {tit}" aria-expanded="{"true" if aberta else "false"}">{G.svg("seta")}</button>'
            f'</header>{corpo}{extra}</section>')


def cena(titulo: str, miolo: str, notas: str = "", dock: bool = True, mini: bool = True, cls: str = "") -> str:
    h = _css(C.cab(titulo))
    if cls:
        h = h.replace("<body>", f'<body class="{cls}">')
    return (h + G.mundo("ilha", G.pet(1160, 400, "parado")) + G.topo() + G.trilho("pet") + (G.dock() if dock else "") + (G.minimapa() if mini else "")
            + miolo + notas + C.FIM)


CURSOR = '<svg class="cursor" style="left:{x}px;top:{y}px" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 2l17 9-7 2-3 7z"/></svg>'


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def padrao_1920() -> str:
    col = f'<aside class="jn-col" aria-label="Janelas do pet">{janela("estado", True)}{janela("evolucao")}{janela("acoes")}{janela("digibrain")}</aside>'
    return cena("O arranjo padrão", col,
                G.nota("1 · o arranjo padrão é a pilha de hoje, no mesmo lugar. A diferença: cada painel é uma janela solta, com a alça (os seis pontos) e o menu (os três pontos)", 1270, 76, 320)
                + G.nota("quem não mexer em nada vê o jogo de hoje. Nenhuma janela nova aparece sozinha", 1270, 180, 300)
                + G.nota("abrir e fechar continua na seta, como hoje. O arraste é pelo cabeçalho inteiro; a alça só mostra que dá para arrastar", 1270, 250, 320)
                + G.nota("o DigiBrain deixa de ser só uma linha que abre um modal: é uma janela como as outras (UX-JN-3)", 1270, 420, 320))


def arrastando_1920() -> str:
    col = f'<aside class="jn-col" aria-label="Janelas do pet">{janela("estado", True)}{janela("evolucao")}<span style="height:48px"></span>{janela("digibrain")}</aside>'
    miolo = (col
             + '<span class="jn-fantasma" style="left:1608px;top:336px;width:300px;height:48px"></span>'
             + '<span class="jn-encaixe" style="left:100px;top:752px;width:300px;height:182px"></span>'
             + '<span class="jn-guia v" style="left:100px;top:86px;height:848px"></span><span class="jn-guia h" style="left:100px;top:934px;width:1500px"></span>'
             + janela("acoes", True, 126, 734, cls="na-mao")
             + CURSOR.format(x=250, y=752)
             + f'<span class="caixa jn-dica" style="left:440px;top:760px">Solte para encaixar no canto<kbd>Esc</kbd>cancela</span>')
    return cena("Arrastando uma janela", miolo,
                G.nota("2 · 'Últimas ações' na mão, indo para o canto de baixo. O lugar de onde saiu fica tracejado até soltar", 1270, 330, 320)
                + G.nota("perto de uma borda ou de outra janela, aparecem as guias e a sombra de onde ela vai encaixar (a 16 px: PROPOSTO). Longe de tudo, ela fica onde for solta", 440, 640, 340)
                + G.nota("a janela nunca sai da tela nem fica debaixo do topo, do trilho ou das ações de baixo: o encaixe as respeita", 440, 820, 340)
                + G.nota("Esc cancela e devolve a janela. Um arraste nunca vira clique (já é assim no hudPet.ts)", 800, 760, 300),
                dock=False)


def arranjo_1920() -> str:
    miolo = (janela("digibrain", True, 560, 150, 360)
             + janela("acoes", True, 100, 752)
             + f'<aside class="jn-col" aria-label="Janelas do pet">{janela("estado", True)}</aside>')
    return cena("Um arranjo do jogador", miolo,
                G.nota("3 · um arranjo de laboratório: o DigiBrain aberto no meio, ao lado do pet; 'Últimas ações' embaixo; o Estado à direita; a Evolução escondida", 940, 150, 320)
                + G.nota("o DigiBrain fica na tela enquanto você joga: não é mais modal, não trava o resto e o minimapa não some (UX-JN-3). É a etapa mais cara", 940, 250, 320)
                + G.nota("a posição de cada janela fica no navegador, fora do save, e não sobe para a nuvem (a CN0 fechou: os ajustes de tela ficam no aparelho)", 420, 800, 340)
                + G.nota("se a janela do navegador encolher, cada janela guarda o canto mais próximo e a distância até ele; nenhuma fica para fora", 940, 380, 320))


def menu_1920() -> str:
    menu = (f'<div class="caixa jn-menu" role="menu" aria-label="Opções de Últimas ações" style="left:1370px;top:320px">'
            f'<button type="button" role="menuitem">{G.svg("seta")}Recolher</button>'
            f'<button type="button" role="menuitem" class="foco">{ic("mover")}Mover<kbd>setas</kbd></button>'
            f'<button type="button" role="menuitem">{ic("esconder")}Esconder</button>'
            f'<button type="button" role="menuitem">{ic("voltar_lugar")}Voltar ao lugar</button></div>')
    col = f'<aside class="jn-col" aria-label="Janelas do pet">{janela("estado", True)}{janela("evolucao")}{janela("acoes", menu=True)}{janela("digibrain")}</aside>'
    miolo = (col + menu + janela("digibrain", True, 240, 200, 360, cls="movendo")
             + '<span class="caixa jn-dica" style="left:240px;top:150px"><kbd>← ↑ ↓ →</kbd>move<kbd>Enter</kbd>fixa<kbd>Esc</kbd>cancela</span>')
    return cena("O menu da janela e o teclado", miolo,
                G.nota("4 · o menu dos três pontos: tudo o que o arraste faz tem um caminho sem arrastar (guia, seção 13: nada importante só no gesto)", 1040, 330, 310)
                + G.nota("'Mover' passa a janela para as setas do teclado, de 16 em 16 px (PROPOSTO), com o encaixe; Enter fixa e Esc cancela. À esquerda, o DigiBrain sendo movido assim", 620, 200, 330)
                + G.nota("'Esconder' tira a janela da tela. Ela volta por Ajustes › Exibir, nunca some de vez", 1040, 430, 310)
                + G.nota("o leitor de tela ouve a posição nova ao fixar ('DigiBrain, à esquerda, no alto'), uma vez", 620, 320, 330))


def exibir_1920() -> str:
    sw = lambda on: f'<span class="interruptor{" on" if on else ""}" role="switch" aria-checked="{"true" if on else "false"}"></span>'

    def linha(i: str, tit: str, on: bool, sub: str = "") -> str:
        s = f"<small>{sub}</small>" if sub else ""
        return f'<button type="button" class="aj" aria-label="Exibir {tit}">{ic(i)}<span><b>{tit}</b>{s}</span>{sw(on)}</button>'
    corpo = f'''
<div class="ex-lista" role="group" aria-label="Janelas da tela do pet">
  {linha("estado", "Estado atual", True)}
  {linha("evolucao", "Evolução", False, "escondida")}
  {linha("acoes", "Últimas ações", True)}
  {linha("digibrain", "DigiBrain", True)}
  {linha("relogio", "Agora", True, "a linha do alto")}
  {linha("mapa", "Minimapa", True)}
</div>
<div><span class="rot" id="ex-arr">Arranjo</span>
  <div class="ex-arranjos" role="radiogroup" aria-labelledby="ex-arr" style="margin-top:6px">
    <button type="button" class="filtro" role="radio" aria-checked="false" aria-pressed="false">Padrão</button>
    <button type="button" class="filtro" role="radio" aria-checked="true" aria-pressed="true">Meu</button>
    <button type="button" class="filtro" role="radio" aria-checked="false" aria-pressed="false">Limpo</button>
  </div></div>
<div class="ct-bts"><button type="button" class="bt acao">{ic("grade")}Arrumar as janelas</button><button type="button" class="bt">{ic("voltar_lugar")}Voltar ao lugar</button></div>'''
    pn = C.painel("Exibir", corpo, icone="olho", sub="Ajustes", voltar="Voltar aos Ajustes")
    miolo = pn + janela("digibrain", True, 1000, 150, 360) + f'<aside class="jn-col" aria-label="Janelas do pet">{janela("estado", True)}{janela("acoes")}</aside>'
    return cena("Ajustes: Exibir", miolo,
                G.nota("5 · Ajustes › Exibir: uma chave por janela, no lugar da chave única 'Exibir detalhes do pet' de hoje. A tela atrás muda na hora", 580, 136, 300)
                + G.nota("a lista sai do mesmo cadastro que a tela usa: uma janela nova entra aqui sem mexer nos Ajustes", 580, 230, 300)
                + G.nota("três arranjos: 'Padrão' (o de hoje), 'Meu' (o que o jogador montou) e 'Limpo' (só o pet e as ações). Os nomes são PROPOSTOS (UX-JN-5)", 580, 470, 300)
                + G.nota("'Voltar ao lugar' já existe hoje (Ajustes › Visual › Painéis) e vem para cá", 580, 580, 300)
                + G.contagem(420, 106), mini=True)


def arrumar_1920() -> str:
    canto = '<span class="jn-canto" aria-hidden="true"></span>'
    miolo = ('<div class="veu"></div><div class="grade" aria-hidden="true"></div>'
             + f'<div class="caixa faixa-arrumar" role="status">{ic("grade")}Arrumando as janelas<button type="button" class="bt acao">Pronto</button><button type="button" class="bt">Cancelar</button></div>'
             + janela("digibrain", True, 560, 150, 360, extra=canto)
             + janela("acoes", True, 100, 752, extra=canto)
             + janela("estado", True, 1608, 86, extra=canto)
             + f'<div class="caixa bandeja"><span class="rot">Escondidas</span><button type="button" class="bt">{G.svg("evolucao")}Evolução</button></div>')
    return cena("O modo arrumar", miolo,
                G.nota("6 · o modo arrumar (a etapa 4, opcional): o jogo fica por baixo, sem receber toques; aparecem a grade, o contorno de cada janela e o canto de redimensionar", 940, 150, 320)
                + G.nota("embaixo, as janelas escondidas: arrastar uma para a tela a traz de volta. 'Pronto' guarda; 'Cancelar' desfaz tudo", 800, 800, 320)
                + G.nota("fora deste modo já dá para arrastar (quadro 2). O modo existe para arrumar várias de uma vez sem tocar no pet sem querer", 940, 290, 320)
                + G.nota("o tempo do jogo não para aqui: é só tela (UX-JN-6)", 940, 400, 280),
                dock=False, mini=False, cls="arrumando")


# ---------------------------------------------------------------------------------------------------- o celular: so a lista
def exibir_390() -> str:
    sw = lambda on: f'<span class="interruptor{" on" if on else ""}" role="switch" aria-checked="{"true" if on else "false"}"></span>'
    linhas = "".join(f'<button type="button" class="aj" aria-label="Exibir {t}">{ic(i)}<span><b>{t}</b></span>{sw(on)}</button>'
                     for i, t, on in [("estado", "Estado atual", True), ("evolucao", "Evolução", False), ("acoes", "Últimas ações", True), ("digibrain", "DigiBrain", True)])
    corpo = f'<div class="ex-lista" role="group" aria-label="O que o retrato mostra">{linhas}</div><p class="sec">No celular as janelas não se arrastam: elas abrem pelo retrato.</p>'
    h = _css(C.cab_cel("Ajustes: Exibir · 390", 440))
    return (h + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna() + C.folha("Exibir", corpo, icone="olho")
            + M.nota("no celular só as chaves: cada uma tira ou põe o botão no leque do retrato", 14, 360) + C.FIM)


TELAS = {"padrao_1920": padrao_1920, "arrastando_1920": arrastando_1920, "arranjo_1920": arranjo_1920, "menu_1920": menu_1920,
         "exibir_1920": exibir_1920, "arrumar_1920": arrumar_1920, "exibir_390": exibir_390}

if __name__ == "__main__":
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")
