# Gera a prancha "o dono inventa uma palavra e o pet aprende" (docs/ESPEC_V3_PALAVRA_DONO.md, F4). So desenho; nenhum codigo do jogo.
# As decisoes de partida (Matheus, 2026-11-17, chat da sessao F4): D-PD-1 a palavra aprende pelo habito com o r do corpo; D-PD-2 a tela
# diz "liga", nunca "entende"; D-PD-3 texto agora, voz depois; D-PD-4 Python com paridade no TS.
# Usa os ajudantes da prancha das janelas (../ux-janelas/gerar.py: a cena, a janela solta), que usa os da conta e dos lugares. O que e
# novo esta em palavra.css. A pele vem de ?pele=vidro|xcom; no desktop ?sem tira as notas, e no celular as notas so aparecem com ?notas.
# Uso (da raiz): python docs/pranchas/ux-palavra-dono/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# O QUE JA EXISTE E O QUE NAO EXISTE (web/app/src e docs, lido em 2026-11-17 na main a794c3ae):
#   o arco do pet ................................ NAO existe: e a IT3 do docs/PLANO_V3_INTERACAO.md (o segurar parado, do Rookie em diante)
#   os comandos Come, Dorme, Brinca, Cava ......... EN-9 (DECIDIDA); nenhum existe no motor ainda (IT6, IT8)
#   Elogiar e Repreender no arco do desktop ....... EN-6 (DECIDIDA); os gestos existem hoje (ToquePet.tsx, o dock)
#   o painel de habitos, so leitura ............... WD-1 (DECIDIDA); NAO existe ainda
#   a janela solta e o painel dos Ajustes ......... as pranchas ux-janelas (UX-JN, APROVADA) e ux-conta
# EXEMPLO DE LAYOUT, NUNCA DADO: "zorp", "nana", "vem", as forcas das barras, as horas e o Growlmon.
# Nenhum numero de jogo novo. As 4 vagas sao PROPOSTO, SEM FONTE (D-PD-7); os tamanhos de interface tambem.
import importlib.util
from pathlib import Path

AQUI = Path(__file__).parent
_esp = importlib.util.spec_from_file_location("gerar_janelas", AQUI.parent / "ux-janelas" / "gerar.py")
J = importlib.util.module_from_spec(_esp)
_esp.loader.exec_module(J)
C, G, M = J.C, J.G, J.M

C.IC.update({
    "dizer": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1.2-4.4A8 8 0 1 1 21 12z"/><path d="M9 11.5h6M9 8.5h4"/>',
    "come": '<path d="M7 3v8a2 2 0 0 0 4 0V3M9 13v8M16 3c-1.5 2-2 4-2 7h3v11"/>',
    "dorme": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "brinca": '<circle cx="12" cy="12" r="8"/><path d="M4.5 9.5c5 1 10 1 15 0M4.5 14.5c5-1 10-1 15 0"/>',
    "cava": '<path d="M14 4l6 6M17 7l-9 9M8 16l-4 4M5 13l6 6"/>',
    "elogiar": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "repreender": '<path d="M12 3v10M12 17v.01"/><circle cx="12" cy="12" r="10"/>',
    "habitos": '<path d="M4 19V9M10 19V5M16 19v-7M22 19H2"/>',
    "orelha": '<path d="M7 9a5 5 0 0 1 10 0c0 3-3 4-3 7a3 3 0 0 1-6 0"/><path d="M10 9a2 2 0 0 1 4 0"/>',
})
ic = C.ic

VERBO = {"come": "comer", "dorme": "dormir", "brinca": "brincar", "cava": "cavar"}
CMD = [("come", "Come"), ("dorme", "Dorme"), ("brinca", "Brinca"), ("cava", "Cava")]
PET_D = (1164, 408)   # o pet no desktop: G.tela(1160, 400, "ilha") (o centro e a base)
PET_C = (271, 362)    # o pet no celular: a camera m_ilha de gerar_movel.py (0,906; 780; 0)


def _css(h: str) -> str:
    h = h.replace('href="janelas.css"', 'href="../ux-janelas/janelas.css">\n<link rel="stylesheet" href="palavra.css"')
    h = h.replace('href="conta.css"', 'href="../ux-conta/conta.css">\n<link rel="stylesheet" href="palavra.css"') if "palavra.css" not in h else h
    return h.replace("<title>As janelas do pet · ", "<title>A palavra do dono · ").replace("<title>A conta · ", "<title>A palavra do dono · ")


# ---------------------------------------------------------------------------------------------------- as pecas
def arco(cx: float, cy: float, r: int, itens: list, foco: str = "", cel: bool = False) -> str:
    """o arco do pet (a IT3), em volta do pet: um botao por item, num semicirculo de cima; `foco` e o item em foco"""
    import math
    n = len(itens)
    out = []
    for i, (k, rot) in enumerate(itens):
        a = math.pi * (1.0 - (i + 0.5) / n)          # da esquerda para a direita, por cima
        x, y = cx + r * math.cos(a), cy - r * math.sin(a)
        cls = "arco-bt" + (" foco" if k == foco else "") + (" dizer" if k == "dizer" else "")
        out.append(f'<button type="button" class="caixa {cls}" style="left:{x:.0f}px;top:{y:.0f}px" aria-label="{rot}">{ic(k)}<span>{rot}</span></button>')
    tam = "cel" if cel else ""
    return f'<nav class="arco {tam}" role="menu" aria-label="O arco do pet">{"".join(out)}</nav>'


def campo(valor: str = "zorp", vagas: tuple = ("zorp", "nana"), k: int = 4, cel: bool = False) -> str:
    chips = "".join(f'<button type="button" class="filtro pl-chip" aria-label="Dizer {p} de novo">{p}</button>' for p in vagas)
    livres = k - len(vagas)
    return f'''
<label class="rot" for="pl-campo">A palavra</label>
<div class="pl-linha"><input id="pl-campo" class="pl-campo" type="text" value="{valor}" maxlength="24" autocomplete="off" spellcheck="false" aria-describedby="pl-ajuda">
<button type="button" class="bt acao">{ic("dizer")}Dizer</button></div>
<p class="sec" id="pl-ajuda">Ele ouve a palavra por um tempo curto. O que fizer depois é com ele.</p>
<div><span class="rot">Já ditas · {len(vagas)} de {k}</span><div class="pl-chips" role="group" aria-label="Palavras já ditas">{chips}{''.join('<span class="pl-vaga" aria-hidden="true"></span>' for _ in range(livres))}</div></div>'''


def forca(p: str, comp: str, v: int, liga: bool) -> str:
    if not liga:
        return (f'<div class="pl-forca nada"><b class="pl-p">{p}</b><span class="pl-alvo">ainda nada</span>'
                f'<span class="barra" role="img" aria-label="{p}: ainda não liga a nada"><i style="width:{v}%"></i><u style="left:25%" aria-hidden="true"></u></span></div>')
    return (f'<div class="pl-forca"><b class="pl-p">{p}</b><span class="pl-alvo">{ic(comp)}liga a {VERBO[comp]}</span>'
            f'<span class="barra" role="img" aria-label="{p} liga a {comp}: força {v} de 100"><i style="width:{v}%"></i><u style="left:25%" aria-hidden="true"></u></span></div>')


def habitos_corpo() -> str:
    acoes = "".join(f'<span class="hb-l"><span>{a}</span><span class="barra"><i style="width:{v}%"></i></span></span>'
                    for a, v in [("Brincar", 62), ("Explorar", 41), ("Dormir", 33)])
    return (f'<span class="rot">O que ele passou a fazer</span>{acoes}'
            f'<span class="rot" style="margin-top:8px">Palavras · 3 de 4</span>'
            + forca("zorp", "brinca", 71, True) + forca("nana", "dorme", 38, True) + forca("vem", "", 12, False)
            + '<p class="sec">A barra mostra o quanto a palavra puxa o que ele faz. O traço é onde ela passa a ligar. Só leitura.</p>')


def cartao(cel: bool = False) -> str:
    c = " cel" if cel else ""
    return (f'<div class="caixa pl-cartao{c}" role="status">{ic("orelha")}<span><b>Growlmon liga “zorp” a brincar</b>'
            f'<small>Quando você diz “zorp”, ele costuma ir brincar.</small></span>'
            f'<button type="button" class="bt">Ver hábitos</button></div>')


def balao_dono(x: float, y: float, p: str = "zorp", apagado: str = "") -> str:
    cls = " apagado" if apagado else ""
    sub = f'<span class="pl-motivo">{apagado}</span>' if apagado else ""
    return f'<div class="caixa pl-balao{cls}" style="left:{x:.0f}px;top:{y:.0f}px" role="status" aria-label="Você disse {p}"><span class="pl-dita">“{p}”</span>{sub}</div>'


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def cena(titulo: str, miolo: str, notas: str = "", **kw) -> str:
    return _css(J.cena(titulo, miolo, notas, **kw))


def dizer_1920() -> str:
    cx, cy = PET_D
    itens = CMD[:2] + [("dizer", "Dizer…")] + CMD[2:] + [("elogiar", "Elogiar"), ("repreender", "Repreender")]
    pn = C.painel("Dizer uma palavra", campo(), icone="dizer", sub="Growlmon", voltar="Voltar ao arco", x=1400, y=150, w=420)
    miolo = arco(cx, cy - 70, 190, itens, foco="dizer") + pn
    return cena("Dizer uma palavra", miolo,
                G.nota("1 · o arco do pet (a IT3, ainda não existe): segurar parado no pet. Ao lado dos pedidos fixos (EN-9) e do Elogiar e Repreender (EN-6), o item novo Dizer…", 640, 120, 330)
                + G.nota("o campo aceita uma palavra ou expressão curta (até 24 letras). Antes de gravar, a tela tira acento e maiúscula: “Zórp” e “zorp” são a mesma palavra", 1400, 560, 400)
                + G.nota("as palavras já ditas viram atalho: um toque diz de novo. Ele guarda 4 (PROPOSTO, D-PD-7); com as 4 cheias, uma palavra nova não entra", 1400, 680, 400)
                + G.nota("só texto nesta etapa (D-PD-3). Nenhum microfone aqui: a voz vem numa etapa própria e grava a mesma palavra", 1400, 800, 400)
                + G.nota("nada diz que ele vai obedecer ou entender (D-PD-2). A frase de ajuda é neutra, como a da primeira recusa (EN-8)", 640, 640, 330),
                dock=False)


def ouviu_1920() -> str:
    cx, cy = PET_D
    inset = (f'<section class="caixa pl-inset" aria-label="Quando o corpo vence"><span class="rot">Quando o corpo vence</span>'
             f'<div class="pl-inset-cena">{balao_dono(24, 34, "zorp", "com muita fome, não ouviu")}</div></section>')
    miolo = balao_dono(cx - 40, cy - 250) + inset
    return cena("Ele ouviu", miolo,
                G.nota("2 · a palavra dita aparece num balão do dono sobre o pet (tracejado, para não se confundir com a fala dele). Some quando acaba a janela em que ele ouve", 1230, 120, 330)
                + G.nota("o pet faz o que decidir: brincar, outra coisa, nada novo. A tela não marca acerto nem erro. O Elogiar e o Repreender são os de sempre e contam só pelo corpo (D-EL)", 1230, 260, 330)
                + G.nota("no canto: com uma falta acima de λ (fome, sono…), o corpo vence. O balão sai apagado, com o motivo, e a palavra não entra na decisão nem no aprendizado", 120, 330, 330)
                + G.nota("nenhum número na tela: a força só aparece no painel de hábitos", 1230, 420, 330))


def liga_1920() -> str:
    jan = (f'<section class="caixa jn" aria-label="Hábitos" style="left:1590px;top:86px;width:318px">'
           f'<header class="jn-cab"><span class="jn-alca" aria-hidden="true">{ic("alca")}</span>{ic("habitos")}<span class="tit">Hábitos</span>'
           f'<button type="button" class="jn-bt aberto" aria-label="Recolher Hábitos" aria-expanded="true">{G.svg("seta")}</button></header>'
           f'<div class="jn-corpo">{habitos_corpo()}</div></section>')
    miolo = cartao() + jan
    return cena("Ele liga a palavra", miolo,
                G.nota("3 · na primeira vez que uma palavra passa o traço, um cartão, uma vez só: “liga” e “costuma”, nunca “entende” nem “obedece” (D-PD-2)", 620, 200, 340)
                + G.nota("o painel de hábitos (WD-1, só leitura) ganha a seção Palavras: cada uma com o que ela mais puxa e a barra de força. Nunca uma barra que o jogador enche", 1240, 420, 330)
                + G.nota("“vem” ainda não passou o traço: “ainda nada”. Uma palavra dita fora de hora, ou para algo que não faz bem ao corpo, pode ficar assim para sempre (D-PD-1)", 1240, 560, 330)
                + G.nota("a barra é H[b, palavra] lido do cérebro; o traço é o limiar PROPOSTO (H_max/4). O DigiBrain mostra o mesmo termo na soma da escolha", 1240, 700, 330),
                dock=True)


# ---------------------------------------------------------------------------------------------------- o celular
def dizer_390() -> str:
    cx, cy = PET_C
    itens = CMD[:2] + [("dizer", "Dizer…")] + CMD[2:]
    h = _css(C.cab_cel("Dizer uma palavra · 390", 470))
    return (h + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna()
            + arco(cx - 45, cy - 50, 110, itens, foco="dizer", cel=True)
            + C.folha("Dizer uma palavra", campo(cel=True), icone="dizer", sub="Growlmon", voltar="Voltar ao arco")
            + M.nota("no celular o arco junta os pedidos e o Dizer… (EN-6); o Elogiar e o Repreender ficam no dock. O campo abre na folha, com o teclado do aparelho", 14, 300)
            + C.FIM)


def habitos_390() -> str:
    h = _css(C.cab_cel("Hábitos · 390", 300))
    return (h + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna() + cartao(cel=True)
            + C.folha("Hábitos", habitos_corpo(), icone="habitos", sub="Growlmon", voltar="")
            + M.nota("o cartão aparece uma vez, no alto; “Ver hábitos” abre esta folha. O painel é só leitura", 14, 200)
            + C.FIM)


TELAS = {"dizer_1920": dizer_1920, "ouviu_1920": ouviu_1920, "liga_1920": liga_1920, "dizer_390": dizer_390, "habitos_390": habitos_390}

if __name__ == "__main__":
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")
