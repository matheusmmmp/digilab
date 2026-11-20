# O celular da prancha "Lugares da ilha: menus" (rodada 3): cada tela do desktop a 390 x 844, e Itens tambem a 360 x 800. So desenho.
# Usa os ajudantes do gerar.py (os icones, a ilha e a camera, os objetos novos, os corpos dos paineis, a trilha de niveis) e o movel.css.
# Uso: python docs/pranchas/ux-lugares-menus/gerar.py   (escreve o desktop e chama este); ou este sozinho.
# ?pele=vidro|xcom troca a pele; as notas so aparecem com ?notas (a tela do celular e pequena; o capturar.sh tira as duas).
#
# Do mobile minimo aprovado (#619, docs/pranchas/ux-mobile/ na worktree v3-ux-mobile): o retrato e a hora no canto de cima a esquerda, a
# coluna Conversar, Crescer, Lutar e Diario no canto de cima a direita, as acoes do pet embaixo, o leque no retrato, nenhuma barra de abas.
# Os lugares no celular: tocar no icone da coluna leva a camera ao lugar (a mesma viagem do desktop; corte seco com reduzir movimento), e o
# painel vira a folha que sobe da base e cobre so a parte de baixo (gerar.folha). O minimapa (a L1 e so do desktop) vira um botao "Mapa"
# no leque do retrato, que abre o mapa por cima (nada de circulo fixo).
from pathlib import Path

import gerar as g

# as cameras do celular: o plano da ilha (1920 x 931) num visor de 390 x 844, com o lugar no terco de cima (a folha cobre de y 400 para
# baixo). Abaixo da imagem fica o fundo escuro, sob a folha. Enquadramentos de layout, nao de jogo.
g.CAM.update({
    "m_ilha": (0.906, 780, 0),       # a ilha normal (931 x 0,906 = 844): o saco e o pet
    "m_viagem": (0.95, 795, 45),     # o meio do caminho ate o saco
    "m_saco": (1.0, 805, 90),        # Crescer
    "m_portao": (1.0, 1400, 370),    # Lutar
    "m_barraca": (0.85, 70, 215),    # Diario
    "m_barraca_ilha": (0.906, 60, 0),  # a barraca vista da ilha (o destrave)
})


def cab(titulo: str, c360: bool = False) -> str:
    h = g.cab(titulo, cel=True).replace('href="lugares.css">', 'href="lugares.css">\n<link rel="stylesheet" href="movel.css">')
    h = h.replace('if(q.has("sem"))', 'if(!q.has("notas"))')   # no celular as notas so com ?notas
    if c360:
        h = h.replace('class="cel"', 'class="cel c360"').replace('content="width=390"', 'content="width=360"')
        h = h.replace("</head>", "<style>:root{--folha-top:380px}</style></head>")
    return h


# ---- a HUD do mobile minimo
TECLA_ROT = {"conversar": "Conversar", "crescer": "Crescer", "lutar": "Lutar", "diario": "Diário"}


def topo(nome: str = "Growlmon", aberto: bool = False) -> str:
    i = g.retrato_i(nome)
    return (f'<button type="button" class="caixa m-retrato" aria-label="Retrato: o nível do Tamer, os vitais e os painéis" aria-haspopup="menu" '
            f'aria-expanded="{"true" if aberto else "false"}">{i}</button>'
            f'<span class="caixa m-relogio" role="group" aria-label="07:42, dia 3"><small aria-hidden="true">D3</small><b aria-hidden="true">07:42</b></span>')


def coluna(atual: str = "", trancados: tuple = (), novo: str = "", toque: str = "") -> str:
    out = []
    for n, r in TECLA_ROT.items():
        tr = n in trancados
        cls = "caixa bt48" + (" trancado" if tr else "") + (" toque" if n == toque else "")
        cur = ' aria-current="page"' if n == atual else ""
        lab = f"{r}, trancado, Nv {g.NIVEL[n][0]}: {g.NIVEL[n][1]}" if tr else (f"{r}, novo" if n == novo else r)
        dis = ' aria-disabled="true"' if tr else ""
        nv = f'<span class="nv" aria-hidden="true">{g.svg("cadeado", "ic ic-p")}Nv {g.NIVEL[n][0]}</span>' if tr else ""
        nvo = '<i class="novo-selo" aria-hidden="true"></i>' if n == novo else ""
        out.append(f'<div class="m-item">{nv}<button type="button" class="{cls}" aria-label="{lab}"{cur}{dis}>{g.svg(n)}</button>{nvo}</div>')
    return f'<nav class="m-coluna" aria-label="Destinos">{"".join(out)}</nav>'


def dock(cls: str = "") -> str:
    bs = "".join(f'<button type="button" aria-label="{r}">{g.svg(i)}</button>'
                 for i, r in [("drumstick", "Alimentar"), ("music", "Brincar"), ("droplet", "Limpar"), ("ellipsis", "Mais")])
    return f'<div class="m-dock {cls}" role="group" aria-label="Cuidar e ensinar">{bs}</div>'


def agora(x: float, y: float) -> str:
    return (f'<button type="button" class="caixa m-agora" style="left:{x:.0f}px;top:{y:.0f}px" aria-label="Agora: explorando. Porquê no DigiBrain.">'
            f'{g.svg("exploracao")}</button>')


def nota(txt: str, x: float, y: float, w: int = 250) -> str:
    return g.nota(txt, x, y, w)


def pagina(titulo: str, corpo: str, c360: bool = False) -> str:
    return cab(titulo, c360) + corpo + g.FIM


# ---- os lugares: a ilha em cima e a folha embaixo
def _lugar(cam: str, pet: str, dest: str, ativa: str, corpo: str, titulo: str, notas: str = "", c360: bool = False, foco: str = "",
           dica: str = "", extra: str = "") -> str:
    return pagina(titulo, g.mundo(cam, pet) + topo() + coluna(dest) + g.folha(dest, ativa, corpo, foco, dica) + extra + notas, c360)


def crescer(ativa: str, corpo: str, titulo: str, notas: str = "", pose: str = "parado", c360: bool = False, extra: str = "") -> str:
    return _lugar("m_saco", g.pet(880, 480, pose, k=1.4), "crescer", ativa, corpo, titulo, notas, c360, extra=extra)


def lutar(ativa: str, corpo: str, titulo: str, notas: str = "", foco: str = "", dica: str = "") -> str:
    return _lugar("m_portao", g.pet(1480, 760, "parado", k=1.3), "lutar", ativa, corpo, titulo, notas, foco=foco, dica=dica)


def diario(ativa: str, corpo: str, titulo: str, notas: str = "") -> str:
    return _lugar("m_barraca", g.pet(470, 712, "parado", k=1.3, virado=True), "diario", ativa, corpo, titulo, notas)


# ---- as telas
def transicao_1() -> str:
    x, y = g.tela(1160, 400 - 77 * 1.3, "m_ilha")
    return pagina("abrir um lugar a 390, quadro 1",
                  g.mundo("m_ilha", g.pet(1160, 400, "parado", k=1.3)) + topo() + coluna(toque="crescer") + agora(x, y - 60) + dock()
                  + nota("1 · o mobile mínimo de hoje (#619). O toque em Crescer, na coluna, leva a câmera ao saco", 14, 470))


def transicao_2() -> str:
    return pagina("abrir um lugar a 390, quadro 2",
                  g.mundo("m_viagem", g.pet(1000, 470, "andando", k=1.35, virado=True)) + topo() + coluna("crescer") + dock("saindo")
                  + g.folha("crescer", "treinar", "").replace('class="caixa folha', 'class="caixa folha subindo', 1)
                  + nota("2 · a câmera a caminho (700 ms, PROPOSTO, SEM FONTE, como no desktop), o pet anda, as ações saem e a folha sobe da base. "
                         "Reduzir movimento: corte seco ao quadro 3", 14, 470))


def transicao_3() -> str:
    return crescer("treinar", g.corpo_treinar(), "abrir um lugar a 390, quadro 3", pose="treino",
                   notas=nota("3 · chegou: a folha cobre só a parte de baixo (top 400 px, PROPOSTO, SEM FONTE); o saco e o pet ficam em cima", 14, 300))


def crescer_treinar() -> str:
    return crescer("treinar", g.corpo_treinar(), "Crescer · Treinar · 390", pose="treino",
                   notas=nota("o corpo é o do desktop, com a regra do texto; o Forçar trancado (Nv 6, o save está no Nv 5)", 14, 300))


def crescer_itens(c360: bool = False) -> str:
    return crescer("itens", g.corpo_itens(), f"Crescer · Itens · {360 if c360 else 390}", c360=c360,
                   notas=nota("a folha de baixo substitui a faixa no topo da rodada 2; o resto da folha rola", 14, 300))


def crescer_evolucao() -> str:
    return crescer("evolucao", g.corpo_evolucao(), "Crescer · Evolução · 390",
                   notas=nota("a folha de baixo substitui a faixa no topo da rodada 2; o resto da folha rola", 14, 300))


def lutar_arena() -> str:
    return lutar("arena", g.corpo_arena(), "Lutar · Arena · 390",
                 notas=nota("a Fronteira trancada (Nv 8, 'Abre com 6 medalhas'); as Regras trancadas (Nv 6)", 14, 300))


def lutar_medalhas() -> str:
    return lutar("medalhas", g.corpo_medalhas(), "Lutar · Medalhas · 390")


def diario_registro() -> str:
    return diario("registro", g.corpo_registro(), "Diário · Registro · 390")


def diario_catalogo() -> str:
    return diario("catalogo", g.corpo_catalogo(), "Diário · Catálogo · 390")


def ajustes() -> str:
    """Ajustes nao e lugar: a folha sobe sobre a ilha de sempre (o leque se fecha quando ela abre)"""
    return pagina("Ajustes · 390", g.mundo("m_ilha", g.pet(1160, 400, "parado", k=1.3)) + topo() + coluna()
                  + g.folha("ajustes", "", g.corpo_ajustes())
                  + nota("Ajustes abre do leque do retrato (Configurações); a câmera não se mexe", 14, 300))


def leque(nivel: int, mapa: bool = False) -> str:
    """o leque do retrato (M1): o Tamer Nv N (P-8), os cinco vitais (o Estado atual) e os paineis; o Mapa e novo (a proposta do minimapa)"""
    vit = "".join(f'<span class="vit">{g.svg(i)}{v}</span>' for i, v in [("drumstick", 64), ("zap", 81), ("droplet", 40), ("smile", 72), ("saude", 95)])
    sim = ' aria-pressed="true"'
    pai = "".join(f'<button type="button" class="caixa bt48" aria-label="{r}"{sim if (r == "Mapa" and mapa) else ""}>{g.svg(i)}</button>'
                  for i, r in [("evolucao", "Evolução"), ("historico", "Últimas ações"), ("digibrain", "DigiBrain"), ("exploracao", "Mapa"),
                               ("ajustes", "Configurações"), ("users", "Meus pets")])
    return (f'<div id="leque" role="group" aria-label="Retrato">'
            f'<span class="tamer-nv m-tamer caixa" role="img" aria-label="Tamer, nível {nivel}">Tamer Nv {nivel}</span>'
            f'<button type="button" class="caixa m-vitais" aria-label="Estado atual: comida 64 %, energia 81 %, higiene 40 %, humor 72 %, saúde 95 %">{vit}</button>'
            f'<div class="m-paineis">{pai}</div></div>')


def mapa() -> str:
    """o minimapa no celular (proposta): o botao Mapa no leque abre o mapa por cima; tocar num lugar abre o menu dele (a camera vai la)"""
    esc = 280 / 216
    px, py = g.PET_MINI["ilha"]
    cx = (f'<section class="caixa m-mapa" role="dialog" aria-label="Mapa da ilha"><div class="m-mapa-cab"><b class="rot">Mapa</b>'
          f'<button type="button" class="bt-ic" aria-label="Fechar o mapa">{g.svg("x")}</button></div>'
          f'<div class="disco">{g.mapa_svg(px, py)}{g.mini_bts(esc=esc)}</div></section>')
    return pagina("o mapa a 390", g.mundo("m_ilha", g.pet(1160, 400, "parado", k=1.3)) + topo(aberto=True) + coluna() + dock()
                  + leque(g.NIVEL_SAVE, mapa=True) + cx
                  + nota(f"o leque do retrato: Tamer Nv {g.NIVEL_SAVE} (P-8; a conta de marcos do save, gerar.py NIVEL_SAVE) e o botão novo Mapa", 14, 760)
                  + nota("o minimapa no celular: um botão no leque abre o mapa por cima; sem círculo fixo. A Fronteira trancada (Nv 8)", 150, 560))


def lugar_trancado() -> str:
    cx, cy = g.tela(*g.CADEADO["crescer"], "m_ilha")
    n, motivo = g.NIVEL["crescer"]
    return pagina("lugar trancado · 390",
                  g.mundo("m_ilha", g.pet_koromon(1160, 400), trancados=("crescer", "lutar", "diario")) + topo("Koromon")
                  + coluna(trancados=g.TRANC_NV1) + dock() + g.cadeados("m_ilha", ("crescer",))
                  + g.balao_aberto(f"<b>Nv {n}</b> · {motivo}", cx - 40, cy + 40, 220)
                  + nota("Tamer Nv 1: o Koromon. Na coluna, os ícones iguais, apagados, com o cadeado e o nível (plano 3.4); na ilha, o saco apagado "
                         "com 'Nv 3' (a barraca e o portão estão fora do quadro, apagados também). O balão: o toque no saco", 14, 470))


def lugar_destravado() -> str:
    return pagina("lugar destravado · 390",
                  g.mundo("m_barraca_ilha", g.pet_koromon(420, 760), trancados=("crescer", "lutar"), extra=g.brilho(118, 448, 292, 270))
                  + topo("Koromon") + coluna(trancados=g.TRANC_NV2, novo="diario") + dock()
                  + g.cadeados("m_barraca_ilha", (), aberto="diario")
                  + g.cartao_destrave("left:20px;right:20px;top:110px")
                  + nota("Tamer Nv 2: a barraca abre (o cadeado aberto, o brilho uma vez); o cartão de destrave (plano 4.1 e 4.2, linha do Nv 2). "
                         "Ir leva a câmera à barraca", 14, 290))


TELAS = {
    "transicao_1_390": transicao_1, "transicao_2_390": transicao_2, "transicao_3_390": transicao_3,
    "crescer_treinar_390": crescer_treinar, "crescer_itens_390": crescer_itens, "crescer_evolucao_390": crescer_evolucao,
    "lutar_arena_390": lutar_arena, "lutar_medalhas_390": lutar_medalhas,
    "diario_registro_390": diario_registro, "diario_catalogo_390": diario_catalogo,
    "ajustes_390": ajustes, "mapa_390": mapa, "lugar_trancado_390": lugar_trancado, "lugar_destravado_390": lugar_destravado,
    "crescer_itens_360": lambda: crescer_itens(c360=True),
}


def escrever() -> None:
    d = Path(__file__).parent
    for nome, f in TELAS.items():
        (d / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    escrever()
