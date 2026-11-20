# Gera a RODADA 2 da prancha "peles de rua": as outras telas nos dois modelos escolhidos pelo Matheus em 2026-11-20 ("Zine e Estêncil").
# So desenho; nenhum codigo do jogo. Usa o gerar.py ao lado (o cabecalho, os tokens, o topo, o trilho, o dock, o minimapa, o sprite) e
# acrescenta r2.css (o esqueleto das pecas novas, igual nos dois modelos) e estencil_r2.css e zine_r2.css (a forma delas).
# Uso (da raiz): python docs/pranchas/ux-peles-rua/gerar_r2.py   (escreve <modelo>_<tela>.html ao lado; ?sem tira as notas)
#
# AS TELAS E DE ONDE VEM O CONTEUDO (capturas do jogo de 2026-11-20, na pele Vidro, lidas antes de desenhar):
#   ajustes .... a lista de Ajustes (Visual, Dicas, Rever o tutorial, Exibir, Mitologia, Viagem da camera, Fala, Som e os tres volumes) e
#                a parte Exibir, com as seis chaves da JN1 (janelasPet.ts). No jogo a parte abre no lugar da lista; aqui, lado a lado
#   lutar ...... Lutar > Arena: a frase, o pet, os oito rivais, os oito mapas e o Lutar; as abas com a Fronteira trancada (Nv 8)
#   diario ..... Diario > Registro: a semente, os eventos, Verificar e Copiar, o Codice das lendas, os seis filtros e as linhas
#   scan ....... o DigiBrain aberto (o scan) e um chamado com "Atender". O desenho da rede e uma captura do jogo (img/scan_rede.jpg)
#   estados .... cada peca parada nos estados: normal, com o mouse, pressionada, com o foco, desligada, escolhida, trancada
# EXEMPLO DE LAYOUT, NUNCA DADO: o rival e o mapa escolhidos, as horas e as linhas do registro, "4242" e "10", os volumes.
# Os tempos e as distancias dos estados sao PROPOSTO, SEM FONTE (o guia, secao 11, da 80 ms para o botao pressionado).
import importlib.util
import json
from pathlib import Path

AQUI = Path(__file__).parent
_esp = importlib.util.spec_from_file_location("gerar_peles", AQUI / "gerar.py")
P = importlib.util.module_from_spec(_esp)
_esp.loader.exec_module(P)
svg, spr, etq, nota, FIM = P.svg, P.spr, P.etq, P.nota, P.FIM

ESCOLHIDOS = ("zine", "estencil")
P.G.IC.update({
    "grade": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    "montanha": '<path d="M3 20l6-12 4 7 2-3 6 8z"/>',
    "lista": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "mapa": '<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "volume": '<path d="M4 9v6h4l5 4V5L8 9z"/><path d="M17 9a4 4 0 0 1 0 6"/>',
})
# os oito rivais da Arena de hoje: a forma de cada um no atlas de clipes, pelo nome do Digimon
RIVAIS = ["Agumon", "Guilmon", "Patamon", "Gabumon", "Armadillomon", "Veemon", "Palmon", "Gomamon"]
_at = json.loads((P.ASSETS / "digilab_atlas_up_clipes.json").read_text(encoding="utf-8"))["sprites"]
for _n in RIVAIS:
    P.FORMA.setdefault(_n, next(k for k, v in _at.items() if v["digimon"] == _n))


def cab(mo: str, titulo: str) -> str:
    h = P.cab(mo, titulo).replace('<link rel="stylesheet" href="base.css">', '<link rel="stylesheet" href="base.css">\n<link rel="stylesheet" href="r2.css">')
    return h.replace(f'<link rel="stylesheet" href="{mo}.css">', f'<link rel="stylesheet" href="{mo}.css">\n<link rel="stylesheet" href="{mo}_r2.css">')


# ---------------------------------------------------------------------------------------------------- o painel de um lugar, generico
def abas(itens: list, nome: str) -> str:
    """itens: (icone, rotulo, estado) com estado "" | "sel" | "Nv N" (trancada)"""
    out = []
    for ic, r, e in itens:
        tr = e.startswith("Nv")
        extra = etq(e, "nv", "cadeado") if tr else ""
        out.append(f'<button type="button" role="tab" class="aba{" trancada" if tr else ""}" aria-selected="{"true" if e == "sel" else "false"}" '
                   f'aria-label="{r}{", trancada, " + e if tr else ""}"{" aria-disabled=true" if tr else ""}>{svg(ic)}<span>{r}</span>{extra}</button>')
    return f'<div class="abas" role="tablist" aria-label="Abas de {nome}">{"".join(out)}</div>'


def painel(icone: str, titulo: str, sub: str, corpo: str, tabs: str = "", x: int = 122, w: int = 600, fechar: str = "Voltar à ilha") -> str:
    s = f"<small>{sub}</small>" if sub else ""
    return (f'<section class="cx lugar" style="left:{x}px;width:{w}px" aria-label="{titulo}"><i class="fita"></i>'
            f'<div class="lg-cab">{svg(icone)}<span class="tit"><b>{titulo}</b>{s}</span>'
            f'<button type="button" class="fechar" aria-label="{fechar}">{svg("x")}</button></div>{tabs}'
            f'<div class="lg-corpo">{corpo}</div></section>')


def inter(on: bool, cls: str = "") -> str:
    return f'<span class="inter{" on" if on else ""} {cls}" role="switch" aria-checked="{"true" if on else "false"}"></span>'


# ---------------------------------------------------------------------------------------------------- Ajustes
def aj(icone: str, nome: str, dir_: str = "", cls: str = "") -> str:
    return f'<button type="button" class="aj {cls}">{svg(icone)}<b>{nome}</b>{dir_ or svg("seta", "ic seta")}</button>'


def vol(nome: str, v: int) -> str:
    return (f'<div class="vol">{svg("volume")}<b>{nome}</b><span class="trilha" role="slider" aria-label="Volume: {nome}" aria-valuenow="{v}" aria-valuemin="0" '
            f'aria-valuemax="100"><i style="width:{v}%"></i><b style="left:{v}%"></b></span><span class="n">{v} %</span></div>')


def corpo_ajustes() -> str:
    return f'''<div class="aj-lista">
{aj("olho", "Visual")}{aj("dica", "Dicas", inter(False))}{aj("replay", "Rever o tutorial")}{aj("grade", "Exibir", cls="novo")}
{aj("montanha", "Mitologia", inter(True), "novo")}{aj("camera", "Viagem da câmera", inter(True), "novo")}{aj("conversar", "Fala")}{aj("som", "Som", inter(True))}
{vol("Geral", 60)}{vol("Música", 50)}{vol("Efeitos", 100)}</div>'''


EXIBIR = [("estado", "Estado atual", True), ("evolucao", "Evolução", True), ("acoes", "Últimas ações", False), ("digibrain", "DigiBrain", True),
          ("relogio", "Agora", True), ("mapa", "Minimapa", True)]


def corpo_exibir() -> str:
    linhas = "".join(aj(i, n, inter(on)) for i, n, on in EXIBIR)
    return (f'<div class="parte-cab"><button type="button" class="bt voltar">{svg("seta")}Ajustes</button><b class="parte-tit">Exibir</b></div>'
            f'<div class="aj-lista" role="group" aria-label="Janelas da tela do pet">{linhas}</div>')


def tela_ajustes(mo: str) -> str:
    return (cab(mo, "Ajustes") + P.cena(1320, 690) + P.topo() + P.trilho("ajustes")
            + painel("ajustes", "Ajustes", "", corpo_ajustes(), w=440, fechar="Fechar os Ajustes")
            + painel("ajustes", "Ajustes", "", corpo_exibir(), x=590, w=440, fechar="Fechar os Ajustes") + P.dock() + P.mini()
            + nota("5 · Ajustes: uma linha por ajuste, com a seta (abre uma parte) ou a chave. As linhas novas ('Exibir', 'Mitologia', 'Viagem da câmera') levam a marca de novo", 1050, 110, 300)
            + nota("a parte 'Exibir' (uma chave por janela, a JN1). No jogo ela abre no lugar da lista; aqui as duas estão lado a lado", 1050, 200, 300)
            + nota("os volumes: o trilho, o cursor e o número. 60, 50 e 100 são EXEMPLO; a lista continua para baixo", 1050, 290, 280)
            + FIM)


# ---------------------------------------------------------------------------------------------------- Lutar > Arena
MAPAS = [("Campo de treino", "Sem regras: só os dois lutadores e o chão."), ("Coliseu", "A arena fecha."), ("Floresta Green Shade", "Árvores e moitas."),
         ("Praia Shellfish", "Maré."), ("Deserto Endless", "Areia movediça e tempestade."), ("Castelo Midnight", "Pilares e runa."),
         ("Caverna Blackheart", "Lava e erupções."), ("Ringue D-1 Grand Prix", "Sem cerca.")]


def op(miolo: str, sel: bool, cls: str = "") -> str:
    return f'<button type="button" class="op {cls}" role="radio" aria-checked="{"true" if sel else "false"}">{miolo}</button>'


def corpo_arena() -> str:
    riv = "".join(op(f'<span class="q">{spr(n, .7)}</span><b>{n}</b>', n == "Gabumon") for n in RIVAIS)
    mapas = "".join(op(f"<b>{n}</b><small>{d}</small>", i == 0, "mapa") for i, (n, d) in enumerate(MAPAS))
    return f'''<p class="frase">Seu pet luta sozinho, em tempo real. Escolha o rival e o mapa e assista.</p>
<div class="linha"><span class="q grande">{spr("Agumon", .9)}</span><b class="nome-pet">Agumon</b>{etq("Rookie", "")}</div>
<div><span class="rot" id="r-rival">Rival</span><div class="ops r3" role="radiogroup" aria-labelledby="r-rival">{riv}</div></div>
<div><span class="rot" id="r-mapa">Mapa</span><div class="ops r2" role="radiogroup" aria-labelledby="r-mapa">{mapas}</div></div>
<button type="button" class="bt acao cheio">{svg("lutar")}Lutar</button>'''


def tela_lutar(mo: str) -> str:
    tabs = abas([("arena", "Arena", "sel"), ("exploracao", "Exploração", ""), ("fronteira", "Fronteira", "Nv 8"), ("medalhas", "Medalhas", "")], "Lutar")
    return (cab(mo, "Lutar › Arena") + P.cena(1360, 690) + P.topo() + P.trilho("lutar")
            + painel("lutar", "Lutar", "portão da arena", corpo_arena(), tabs, w=680) + P.mini()
            + nota("6 · Lutar › Arena: duas escolhas de uma só (o rival e o mapa) e um botão principal. O escolhido tem de saltar sem depender só da cor", 830, 110, 300)
            + nota("os oito rivais e os oito mapas são os do jogo de hoje; a frase de cada mapa é a primeira da descrição dele. O rival e o mapa marcados são EXEMPLO", 830, 330, 300)
            + nota("a aba Fronteira está trancada (Nv 8): apagada, com o cadeado e o nível", 830, 215, 280)
            + nota("com um lugar aberto, as ações de baixo e as janelas da direita recolhem, como hoje", 830, 760, 280)
            + FIM)


# ---------------------------------------------------------------------------------------------------- Diario > Registro
LINHAS = [("D1 16:45", "pet", "chamando você"), ("D1 16:30", "pet", "comendo"), ("D1 14:00", "pet", "dormindo"), ("D1 14:00", "mao", "alimentar"),
          ("D1 13:45", "pet", "brincando"), ("D1 13:30", "pet", "à toa"), ("D1 13:15", "pet", "brincando"), ("D1 13:00", "pet", "à toa")]


def corpo_registro() -> str:
    filtros = "".join(f'<button type="button" class="filtro" aria-pressed="{"true" if f == "tudo" else "false"}">{f}</button>'
                      for f in ["tudo", "você", "pet", "lutas", "recusas", "treino"])
    linhas = "".join(f'<button type="button" class="reg-l{" voce" if i == "mao" else ""}"><span class="t">{t}</span>{svg(i)}<span>{x}</span>{svg("seta", "ic seta")}</button>'
                     for t, i, x in LINHAS)
    return f'''<div class="destaque reg-topo"><span class="par"><span class="rot">Semente</span><b class="n">4242</b></span>
  <span class="par"><span class="rot">Eventos</span><b class="n">10</b></span>
  <span class="linha" style="margin-left:auto"><button type="button" class="bt acao">{svg("replay")}Verificar</button><button type="button" class="bt">{svg("copiar")}Copiar</button></span></div>
<button type="button" class="banner"><b>Códice das lendas</b><small>o que vocês dois já viveram, e o que ainda falta</small></button>
<div class="filtros" role="group" aria-label="Filtrar o registro">{filtros}</div>
<div class="reg" aria-label="O registro, do mais novo ao mais velho">{linhas}</div>'''


def tela_diario(mo: str) -> str:
    tabs = abas([("registro", "Registro", "sel"), ("catalogo", "Catálogo", ""), ("geracoes", "Gerações", ""), ("cenarios", "Cenários", "")], "Diário")
    return (cab(mo, "Diário › Registro") + P.cena(1320, 690) + P.topo() + P.trilho("diario")
            + painel("diario", "Diário", "barraca do Tamer", corpo_registro(), tabs) + P.mini()
            + nota("7 · Diário › Registro: a tela de mais texto corrido. É o teste de leitura da pele: linhas finas, hora, ícone e uma seta", 750, 110, 300)
            + nota("a linha do que VOCÊ fez tem uma marca própria; as do pet não", 750, 560, 280)
            + nota("'4242', '10', as horas e as linhas são EXEMPLO (as de uma captura do jogo de hoje)", 750, 330, 280)
            + FIM)


# ---------------------------------------------------------------------------------------------------- o scan do DigiBrain e um chamado
def scan() -> str:
    onda = '<svg class="onda" viewBox="0 0 220 30" aria-hidden="true"><path d="M2 24h14l6-20 6 20h190"/></svg>'
    return f'''<section class="cx scan" aria-label="DigiBrain"><i class="fita"></i>
  <div class="scan-cab">{svg("digibrain")}<b>DigiBrain</b><i class="vivo" role="img" aria-label="ligado"></i>
    <button type="button" class="fechar" aria-label="Como ler">{svg("info")}</button><button type="button" class="fechar" aria-label="O mapa em texto">{svg("lista")}</button>
    <button type="button" class="fechar" aria-label="Fechar DigiBrain">{svg("x")}</button></div>
  <span class="scan-tela"><img src="img/scan_rede.jpg" alt="A rede do pet, viva"></span>
  <div class="scan-faixa">{onda}<span class="par"><span class="rot">Estado atual</span><b class="estado">{svg("smile")}Sem cuidado</b></span></div>
</section>'''


def chamado() -> str:
    return (f'<div class="cx chamado" role="status"><div class="ch-t">{svg("alerta")}<span class="tit"><b>Chamando você</b><small>um elogio atende</small></span></div>'
            f'<button type="button" class="bt acao cheio">Atender</button></div>')


def tela_scan(mo: str) -> str:
    return (cab(mo, "o DigiBrain e um chamado") + P.cena() + P.topo() + P.trilho() + chamado() + scan() + P.dock()
            + nota("8 · o DigiBrain aberto. O desenho da rede é conteúdo, como o habitat: fica escuro e igual nas duas peles (é uma captura do jogo). A pele faz a moldura, o cabeçalho e a faixa de baixo", 1150, 560, 320)
            + nota("o chamado: um cartão na cor da necessidade, com um botão só. É a peça mais urgente da tela e não pisca (guia, seção 11)", 1150, 110, 300)
            + nota("'Sem cuidado' e 'um elogio atende' são os textos do jogo de hoje", 1150, 690, 280)
            + FIM)


# ---------------------------------------------------------------------------------------------------- os estados
def linha(rot: str, miolo: str) -> str:
    return f'<div class="est-linha"><span>{rot}</span><span class="est-peca">{miolo}</span></div>'


def tela_estados(mo: str) -> str:
    m = P.MODELOS[mo]

    def bt(cls: str, txt: str = "Treinar agora", dis: str = "") -> str:
        return f'<button type="button" class="bt acao {cls}"{dis}>{svg("check")}{txt}</button>'

    def bt2(cls: str) -> str:
        return f'<button type="button" class="bt {cls}">Agora não</button>'

    def caixa(miolo: str, cls: str = "") -> str:
        return f'<span class="cx p est-cx {cls}">{miolo}</span>'

    def nav(cls: str, atual: bool = False, extra: str = "") -> str:
        return caixa(f'<button type="button" class="nav {cls}"{" aria-current=page" if atual else ""}>{svg("crescer")}<span>Crescer</span>{extra}</button>')

    def tecla(cls: str) -> str:
        return caixa(f'<button type="button" class="tecla {cls}">{svg("mao")}<span>Elogiar</span></button>')

    def aba(cls: str, sel: bool = False, tr: bool = False) -> str:
        e = etq("Nv 8", "nv", "cadeado") if tr else ""
        return (f'<span class="abas est-abas"><button type="button" role="tab" class="aba {cls}{" trancada" if tr else ""}" aria-selected="{"true" if sel else "false"}">'
                f'{svg("arena")}<span>Arena</span>{e}</button></span>')

    def opc(cls: str, sel: bool = False) -> str:
        return op(f'<span class="q">{spr("Gabumon", .7)}</span><b>Gabumon</b>', sel, cls)

    def linha_aj(cls: str, on: bool = True) -> str:
        return aj("grade", "Exibir", inter(on), cls)

    blocos = [
        ("O botão principal", [("normal", bt("")), ("com o mouse", bt("s-mouse")), ("pressionado", bt("s-press")), ("com o foco", bt("s-foco")),
                               ("desligado", bt("", dis=" disabled"))]),
        ("O botão comum", [("normal", bt2("")), ("com o mouse", bt2("s-mouse")), ("pressionado", bt2("s-press")), ("com o foco", bt2("s-foco"))]),
        ("A opção (rival, mapa)", [("normal", opc("")), ("com o mouse", opc("s-mouse")), ("escolhida", opc("", True)), ("escolhida, com o foco", opc("s-foco", True))]),
        ("A linha de Ajustes", [("normal", linha_aj("")), ("com o mouse", linha_aj("s-mouse")), ("com o foco", linha_aj("s-foco")), ("a chave desligada", linha_aj("", False))]),
        ("A aba", [("normal", aba("")), ("com o mouse", aba("s-mouse")), ("escolhida", aba("", True)), ("com o foco", aba("s-foco")), ("trancada", aba("", tr=True))]),
        ("O destino do trilho", [("normal", nav("")), ("com o mouse", nav("s-mouse")), ("atual", nav("", True)), ("com o foco", nav("s-foco"))]),
        ("A ação de baixo", [("normal", tecla("")), ("com o mouse", tecla("s-mouse")), ("pressionada", tecla("s-press")), ("com o foco", tecla("s-foco"))]),
    ]
    cols = "".join(f'<section class="est-bloco"><h2>{t}</h2>{"".join(linha(r, x) for r, x in ls)}</section>' for t, ls in blocos)
    regra = {"zine": "Com o mouse, o recorte sobe 2 px e a sombra cresce; pressionado, ele encosta no papel e a sombra some. O foco é um contorno anil de 3 px, por fora.",
             "estencil": "Com o mouse, o fundo clareia e entra um traço de osso; pressionado, o botão afunda 2 px. O foco é um contorno branco de 3 px: por fora nas peças retas, por dentro onde o canto é cortado, e duas barras na aba, que é inclinada."}[mo]
    return (cab(mo, "os estados") + f'<div class="est"><header class="est-cab"><span class="rot">Modelo {m["n"]} · {m["nome"]} · os estados</span>'
            f'<p>{regra} Nada pisca nem gira; a troca leva 80 ms e vira corte com o movimento reduzido.</p></header>{cols}</div>' + FIM)


TELAS = {"ajustes": tela_ajustes, "lutar": tela_lutar, "diario": tela_diario, "scan": tela_scan, "estados": tela_estados}

if __name__ == "__main__":
    for mo in ESCOLHIDOS:
        for nome, f in TELAS.items():
            (AQUI / f"{mo}_{nome}.html").write_text(f(mo), encoding="utf-8", newline="\n")
    print(len(ESCOLHIDOS) * len(TELAS), "telas da rodada 2")
