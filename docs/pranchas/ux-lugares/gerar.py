# Gera as tres pranchas da L1 de "Lugares da ilha" (docs/PROPOSTAS_V3_UX_TELA_PET.md, secao "Lugares da ilha (L1)"), a 1920 x 950:
#   lugares_normal.html  a camera seguindo o pet, com o minimapa no canto e o DigiBrain na pilha;
#   lugares_longe.html   a camera solta, longe do pet, com o pet chamando: o aviso na borda e o "seguir o pet";
#   lugares_mapa.html    o minimapa ampliado num quadro da prancha (nao e tela), com a legenda e a fonte de cada marca.
# A pele vem de ?pele=vidro|xcom e ?sem tira as notas amarelas. So desenho; nenhum codigo do jogo.
# O fundo e uma captura real da ilha (o Gomamon dormindo) e o mapa e a grade de verdade (ilha_json.mts e ilha_png.py), fora do git, em
# D:\Trab\digilab\capturas_ux_lugares_aprovar\fundo\. As posicoes das marcas sao as do layout do motor (LAYOUT_MUNDO_PADRAO,
# web/app/motor/constantes.ts:403-410) e as da vista (o saco: ninho + SACO_DESDE_NINHO, ilha/constantes.ts:56); a do pet, a da bola e a
# da fruta no chao sao exemplo de layout, como os numeros da pilha (49 %, 14:10), nunca dado.
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ux-pet"))
D = Path(__file__).parent
FUNDO = "../../../../capturas_ux_lugares_aprovar/fundo"  # servido de D:\Trab\digilab (capturar.sh)
ILHA = json.loads((Path(r"D:/Trab/digilab/capturas_ux_lugares_aprovar/fundo/ilha.json")).read_text(encoding="utf-8"))
X0, Z0, LARG, PROF = ILHA["x0"], ILHA["z0"], ILHA["larg"], ILHA["prof"]
L = {"ninho": ILHA["ninho"], "comedouro": ILHA["comedouro"], "arvores": ILHA["arvores"]}
SACO = (L["ninho"][0] + 0.5 + 3, L["ninho"][1] + 0.5 - 4)  # itens.ts:217, SACO_DESDE_NINHO = [3, -4]
COR_FRUTA = {"a": "#e8533f", "b": "#f2b134", "c": "#8a5bd6"}  # ilha/itens.ts:24 (cores que a cena ja pinta)

# icones de traco (os lucide do jogo: Bed, Utensils, Dumbbell, Volleyball, LocateFixed, Brain, ChevronLeft/Right)
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
    "cama": '<path d="M2 18V6M2 14h20v4M22 18v-6a3 3 0 0 0-3-3h-9v5"/><circle cx="6" cy="11" r="2"/>',
    "comedouro": '<path d="M3 2v7c0 1 1 2 2 2h2a2 2 0 0 0 2-2V2M6 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1 1 2 2 2h3zm0 0v7"/>',
    "saco": '<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>',
    "bola": '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 0 0 18M3.5 9.5c5 2 12 2 17 0M5 17c4-3 10-3 14 0"/>',
    "seguir": '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
    "dir": '<path d="M9 5l7 7-7 7"/>',
}


def svg(n: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>'


def cab(titulo: str, fundo: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lugares L1 · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600;700;800;900&family=Rajdhani:wght@700&display=swap">
<link rel="stylesheet" href="../ux-pet/pet.css"><link rel="stylesheet" href="lugares.css">
<style>:root{{--fundo-mapa:url("{FUNDO}/ilha_cima.png");{fundo}}}.retrato i{{background:url("{FUNDO}/retrato.png") center/contain no-repeat;width:40px;height:40px;transform:translate(-50%,-50%)}}</style>
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.pele=q.get("pele")==="xcom"?"xcom":"vidro";if(q.has("sem"))addEventListener("DOMContentLoaded",()=>document.body.classList.add("sem-notas"));</script>
</head><body class="d">'''


# ---- o minimapa: D px de diametro, k px por celula, centrado na celula `centro`
def minimapa(D: int, k: float, centro, foco, pet, chama=False, bola=(40.5, 15.5), fruta=(29.0, 22.0, "b"), giro=0, rotulo=True, solto=False) -> str:
    cx, cz = centro
    px = lambda x, z: (D / 2 + (x - cx) * k, D / 2 + (z - cz) * k)
    dentro = lambda x, z: (px(x, z)[0] - D / 2) ** 2 + (px(x, z)[1] - D / 2) ** 2 < (D / 2 - 6) ** 2
    bg = f"--mx:{D / 2 - (cx - X0) * k:.1f}px;--mz:{D / 2 - (cz - Z0) * k:.1f}px;--mw:{LARG * k:.1f}px;--mh:{PROF * k:.1f}px;--mm:{D}px"
    m = []

    def marca(cls, x, z, inner="", extra=""):
        if dentro(x, z):
            a, b = px(x, z)
            m.append(f'<span class="mm {cls}" style="left:{a:.1f}px;top:{b:.1f}px;{extra}">{inner}</span>')

    for _id, x, z, _f in L["arvores"]:
        marca("arv", x + 0.5, z + 0.5)
    marca("comida", fruta[0], fruta[1], extra=f"--c:{COR_FRUTA[fruta[2]]}")
    marca("ic", L["ninho"][0] + 0.5, L["ninho"][1] + 0.5, svg("cama"))
    marca("ic", SACO[0], SACO[1], svg("saco"))
    marca("ic", L["comedouro"][0] + 0.5, L["comedouro"][1] + 0.5, svg("comedouro"))
    marca("ic", bola[0], bola[1], svg("bola"))
    # o cone: o ponto da camera no chao (5 celulas atras do foco, a camera "atras" olha para o norte) abrindo 11 celulas para cada lado ate
    # 13 adiante; so desenho, a forma certa sai do FOV no codigo
    fx, fz = foco
    w, h = 22 * k, 18 * k
    a, b = px(fx, fz + 5)
    m.append(f'<span class="cone" style="left:{a - w / 2:.1f}px;top:{b - h:.1f}px;width:{w:.1f}px;height:{h:.1f}px;transform:rotate({giro}deg)"></span>')
    if solto:
        a, b = px(fx, fz)
        m.append(f'<span class="alvo" style="left:{a:.1f}px;top:{b:.1f}px"></span>')
    marca("pet" + (" chama" if chama else ""), pet[0], pet[1])
    n = '<span class="n">N</span>' if rotulo else ""
    return (f'<button type="button" class="minimapa" style="{bg}" aria-label="Minimapa da ilha: clique para levar a câmera; '
            f'o pet está {"longe da câmera" if solto else "no centro da vista"}">{n}{"".join(m)}</button>')


def nav_bt(n: str, r: str) -> str:
    atual = ' aria-current="page"' if n == "pet" else ""
    return f'<button type="button" class="nav-bt"{atual}>{svg(n)}{r}</button>'


def hud(pilha_aberta: bool = True) -> str:
    nav = "".join(nav_bt(n, r) for n, r in [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário"),
                                              ("conversar", "Conversar"), ("ajustes", "Ajustes")])
    med = lambda r, v, t="": f'<div class="med {t}"><span class="rot">{r}</span><span class="tri" role="img" aria-label="{r} {v} de 100"><i style="--v:{v}%"></i></span><em>{v} %</em></div>'
    dock = "".join(f'<button type="button">{a}</button>' for a in ["Alimentar", "Brincar", "Limpar", "Carinho", "Tapa", "Tratar", "Mais"])
    corpo = (f'<div class="painel-corpo">{med("comida", 49, "alerta")}{med("energia", 29, "alerta")}{med("higiene", 75)}{med("humor", 96)}{med("saúde", 100, "ok")}'
             '<button type="button" class="detalhes" aria-expanded="false">Detalhes ›</button></div>') if pilha_aberta else ""
    return f'''
<header class="topo">
  <div class="caixa topo-pet"><button type="button" class="retrato" aria-label="Meus pets; com a câmera solta, volta ao pet"><i></i></button><span class="topo-pet-txt"><b>Gomamon</b><small>Rookie</small></span></div>
  <button type="button" class="caixa agora" aria-expanded="false" aria-controls="pet-painel" aria-label="Agora: dormindo. Exausto: só havia uma opção. Abrir o porquê no DigiBrain">
    <span class="rot">agora</span><span class="acao">dormindo</span><span class="ponto" aria-hidden="true">·</span><span class="neutro">Exausto · só havia uma opção</span><span class="seta" aria-hidden="true">›</span></button>
  <span class="logo">DIGILAB</span>
  <div class="caixa relogio"><span class="hora"><small>Dia 1</small><b>14:10</b></span><span class="salvo">● salvo</span></div>
</header>
<nav class="caixa trilho" aria-label="Navegação">{nav}</nav>
<aside class="pilha" aria-label="Painéis do pet">
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="{str(pilha_aberta).lower()}">{svg("estado")}<span class="tit">Estado atual</span><span class="risca"></span></button>{corpo}</section>
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false">{svg("evolucao")}<span class="tit">Evolução<span class="resumo">próxima forma em 8h 50min</span></span><span class="risca"></span></button></section>
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false">{svg("acoes")}<span class="tit">Últimas ações<span class="resumo">14:00 · dormindo</span></span><span class="risca"></span></button></section>
  <section class="caixa painel"><button type="button" class="painel-cab" aria-expanded="false" aria-controls="pet-painel">{svg("digibrain")}<span class="tit">DigiBrain<span class="resumo">o porquê das escolhas</span></span><span class="risca"></span></button></section>
</aside>
<nav class="caixa dock" aria-label="Ações">{dock}</nav>'''


PET = (7.6, 16.0)  # entre o ninho e o comedouro, como na captura do fundo
CENTRO = (32.0, 15.0)  # o meio da area andavel (64 x 30)
K, MM = 3.3, 232  # PROPOSTO, SEM FONTE


def normal() -> str:
    return cab("normal", '--fundo-cena:url("' + FUNDO + '/cena_limpa.jpg")') + f'''
<div class="cena" role="img" aria-label="A ilha 3D, captura real, com o Gomamon dormindo"></div>
{hud()}
{minimapa(MM, K, CENTRO, PET, PET)}
<span class="nota" style="right:262px;bottom:200px">NOVO: o minimapa, no lugar da etiqueta do DigiBrain. A ilha inteira, norte para cima (L1-1); o pet rosa (L1-2) e o cone da vista</span>
<span class="nota" style="right:328px;top:392px">NOVA: a etiqueta do DigiBrain vira a 4ª linha da pilha (L1-6)</span>
<span class="nota" style="left:104px;bottom:110px">WASD / setas / arrasto direito ou do meio: a câmera anda. Roda, Shift + roda e arrasto esquerdo: como hoje</span>
<span class="nota" style="left:50%;top:76px;transform:translateX(-50%)">o cartão do chamado continua aqui, no alto ao centro (não desenhado)</span>
</body></html>
'''


def longe() -> str:
    # o fundo: o recorte do oeste da mesma captura (x 0-900, y 0-445: árvores e penhasco, sem o pet); a vista real sai no codigo
    foco, pet = (22.0, 9.0), (57.0, 21.0)
    fundo = f'--fundo-cena:url("{FUNDO}/cena_limpa.jpg");--fundo-tam:4096px auto;--fundo-pos:0 0'
    return cab("longe", fundo) + f'''
<div class="cena" role="img" aria-label="A ilha 3D com a câmera solta no jardim, sem o pet na tela (recorte da captura real)"></div>
{hud(pilha_aberta=False)}
<button type="button" class="caixa borda" style="right:16px;top:470px" aria-label="Gomamon está chamando, a leste. Seguir o pet (F)">
  <span class="exc" aria-hidden="true">!</span><span class="retrato" aria-hidden="true"><i></i></span><span class="seta">{svg("dir")}</span></button>
<button type="button" class="caixa seguir" aria-label="Seguir o pet (F)">{svg("seguir")}<kbd>F</kbd></button>
{minimapa(MM, K, CENTRO, foco, pet, chama=True, solto=True)}
<span class="nota" style="right:16px;top:430px">aviso na borda: o pet chama e está fora da tela, do lado em que ele está; clicar = F</span>
<span class="nota" style="right:110px;bottom:272px">"seguir o pet": só o ícone e a tecla, quando o ponto olhado passa de 6 células do pet (L1-7)</span>
<span class="nota" style="right:262px;bottom:120px">o losango é o ponto olhado (a câmera solta); o anel no pet rosa: ele está chamando</span>
<span class="nota" style="left:104px;bottom:110px">fundo: um recorte da mesma captura (sem o pet), só para a prancha; a vista real sai no código</span>
</body></html>
'''


def mapa() -> str:
    def leg(marca: str, txt: str, fonte: str) -> str:
        return f'<span>{marca}</span><span>{txt}<small>{fonte}</small></span>'
    ic = lambda n: f'<span class="mm ic">{svg(n)}</span>'
    legenda = "".join([
        leg('<span class="mm pet"></span>', "o pet (o desenhado, a posição do motor interpolada)", "Mundo.pet, motor/mundo.ts; Seguidor, vista.ts"),
        leg('<span class="mm pet chama"></span>', "o pet chamando (o mesmo caso do cartão do chamado)", "chamadosVisiveis, hudPet.ts; acao chamar_atencao, TelaPet.tsx:301"),
        leg('<span class="mm alvo" style="position:static;transform:rotate(45deg)"></span>', "o ponto olhado, só com a câmera solta", "só da vista (ORBITA, orbita.ts)"),
        leg(ic("cama"), "o ninho", "LayoutMundo.ninho [4, 15], motor/constantes.ts:406"),
        leg(ic("comedouro"), "o comedouro", "Mundo.comedouro; LayoutMundo.comedouro [10, 15], motor/constantes.ts:406"),
        leg(ic("saco"), "o saco de pancada (o lugar da L2)", "só da vista: ninho + SACO_DESDE_NINHO, ilha/itens.ts:217, ilha/constantes.ts:56"),
        leg(ic("bola"), "a bola", "Mundo.bola, motor/mundo.ts; Itens.bolaDesenhada"),
        leg('<span class="mm arv"></span>', "as árvores de fruta do layout (J1–J3, M1–M6)", "Mundo.arvores; LayoutMundo.arvores, motor/constantes.ts:407-409"),
        leg(f'<span class="mm comida" style="--c:{COR_FRUTA["b"]}"></span>', "fruta ou ração no chão, na cor da cena", "Mundo.comidas; COR_FRUTA e COR_RACAO, ilha/itens.ts:22-24"),
        leg('<span class="cone" style="position:static;display:block;width:22px;height:18px"></span>', "o cone da vista", "a câmera do habitat e a ORBITA (CAMERAS, ilha/constantes.ts)"),
        leg("—", "fora: o cocô, o kit médico, a arena e o diário", "enfeites da vista (L1-4); a arena e o diário só na L3"),
    ])
    return cab("mapa", '--fundo-cena:url("' + FUNDO + '/cena_limpa.jpg")') + f'''
<div class="cena" role="img" aria-label="A ilha 3D, captura real, com o Gomamon dormindo"></div>
{hud()}
{minimapa(MM, K, CENTRO, PET, PET)}
<section class="caixa quadro mapa" aria-label="Quadro da prancha: o minimapa ampliado e a legenda">
  <div class="col"><span class="titulo">A · a ilha inteira (recomendado)</span>
    <div class="grande">{minimapa(340, K * 340 / MM, CENTRO, PET, PET)}</div>
    <span class="apoio">o mesmo minimapa do canto, ampliado 1,5×; o fundo é a grade da ilha nas cores da cena (ilhaDe, grade.ts:230; PALETA_ILHA, cena.ts:83-86)</span>
</div>
  <div class="col"><span class="titulo">B · a janela em volta da câmera (L1-1)</span>
    <div class="grande">{minimapa(340, 9.0, PET, PET, PET)}</div>
    <span class="apoio">~27 por 27 células em volta do ponto olhado, a 9 px por célula: a casa fica legível, mas o mapa não mostra o que está longe</span></div>
  <div class="col"><span class="titulo">as marcas e de onde vêm</span><div class="legenda">{legenda}</div></div>
</section>
<span class="nota" style="left:104px;top:560px">quadro só da prancha: o minimapa ampliado, as duas escalas e a legenda</span>
</body></html>
'''


for nome, f in [("normal", normal), ("longe", longe), ("mapa", mapa)]:
    (D / f"lugares_{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
