# Gera a prancha da M1 do mobile "minimo" da UX_TELA_PET (docs/PROPOSTAS_V3_UX_TELA_PET.md, "Mobile minimo"): a tela Pet abaixo de 900 px,
# nas peles de hoje (Vidro e Militar), sobre a cena 3D de verdade. Cada HTML e o proprio celular; o capturar.sh o abre num iframe.
# Uso: python docs/pranchas/ux-mobile/gerar.py   (escreve pet_<estado>.html ao lado). So desenho; nenhum codigo do jogo.
# Parametros: ?pele=vidro|xcom (Militar e o id xcom, como no app); ?notas mostra as notas de fonte por cima do desenho.
# O fundo sao capturas reais do jogo, fora do git, em D:\Trab\digilab\capturas_ux_mobile_aprovar\minimo\_fundo\ (servidas pelo
# python -m http.server 8765 com raiz em D:\Trab\digilab; a prancha fica em /v3-ux-mobile/docs/pranchas/ux-mobile/).
# Os textos e os nomes acessiveis sao os do jogo (citados em cada funcao); os numeros (12 %, 64, 07:42, D3) sao exemplo de layout, nunca dado.
from pathlib import Path

AQUI = Path(__file__).resolve().parent
F = "../../../../capturas_ux_mobile_aprovar/minimo/_fundo"  # fora do git; relativo a docs/pranchas/ux-mobile/
DIA, NOITE, RETRATO = F + "/cena_dia.png", F + "/cena_noite.png", F + "/retrato.png"
LUCIDE = "https://unpkg.com/lucide@0.441.0/dist/umd/lucide.min.js"  # o app usa o lucide-react; a prancha, o mesmo desenho dos icones


def ic(nome: str) -> str:
    return f'<i data-lucide="{nome}" aria-hidden="true"></i>'


def nota(txt: str, pos: str) -> str:
    return f'<span class="nota" style="{pos}">{txt}</span>'


# ---- canto de cima a esquerda. O retrato: Retrato (TelaPet.tsx:50) no .topo-retrato (Topo.tsx:18). No celular ele passa a abrir os
# vitais e os paineis; o nome "Paineis do pet" e o da nav da borda que ele substitui (TelaPet.tsx:566), pergunta M1-1.
def retrato(ponto: bool = False, aberto: bool = False) -> str:
    p = '<span class="ponto-nec" aria-hidden="true"></span>' if ponto else ""
    return (f'<button type="button" class="cx forma topo-retrato" aria-label="Painéis do pet" aria-expanded="{str(aberto).lower()}" '
            f'aria-controls="leque"><img src="{RETRATO}" alt="" width="52" height="52">{p}</button>')


# a hora: diaDe e hhmm de m.e.tick (TelaPet.tsx:46-47), o grupo e o nome de Topo.tsx:29
def relogio(dia: int, hora: str) -> str:
    return (f'<span class="cx pilula topo-relogio" role="group" aria-label="{hora}, dia {dia}">'
            f'<small aria-hidden="true">D{dia}</small><b aria-hidden="true">{hora}</b></span>')


# ---- canto de cima a direita: Conversar (o .topo-bt de Topo.tsx:35, o nome que o e2e procura) e os destinos da Nav (Nav.tsx:14-20,
# icones de Nav.tsx:9, nomes de NOME_DESTINO em rotas.ts:12). Sem Pet: a tela Pet e a casa.
def coluna() -> str:
    dest = "".join(f'<button type="button" class="cx forma bt48 ic hx-nav__bt">{ic(i)}<span class="sr-only hx-nav__rot">{n}</span></button>'
                   for i, n in [("sprout", "Crescer"), ("swords", "Lutar"), ("book-open", "Diário")])
    return (f'<div class="coluna"><button type="button" class="cx forma bt48 ic topo-bt" aria-label="Conversar">{ic("message-circle")}</button>'
            f'<nav class="dl-nav hx-nav" aria-label="Destinos">{dest}</nav></div>')


# ---- sobre o pet: a linha do agora so em icone. O nome acessivel e o rotuloAgora(v, true) de LinhaAgora.tsx:44-51; o caso e o vistaAgora
# (LinhaAgora.tsx:30-38). O icone de cada acao do motor (NOME_PET, motor/nomes.ts:18) e PROPOSTO (pergunta M1-5)
ICONE_AGORA = {"ocioso": "coffee", "dormir": "moon", "comer": "drumstick", "brincar": "music", "chamar_atencao": "megaphone",
               "explorar": "compass", "emburrar": "angry"}


def agora(acao: str, caso: str, rotulo: str) -> str:
    if acao not in ICONE_AGORA:
        raise ValueError("acao do pet desconhecida: " + acao)
    if caso not in ("aprendido", "instinto", "uma", "sem", "modular"):
        raise ValueError("caso desconhecido: " + caso)
    return (f'<button type="button" class="cx forma ic pet-agora" data-caso="{caso}" aria-label="{rotulo}" aria-expanded="false" '
            f'aria-controls="pet-painel">{ic(ICONE_AGORA[acao])}</button>')


# ---- embaixo, so as acoes. Os nomes: ROTULO_DONO (acoes.ts:11-14) no texto do botao (TelaPet.tsx:371-373), que fica so para o leitor de
# tela; o Alimentar dos pets com mundo leva o aria-label e o title da reserva (TelaPet.tsx:372); o Mais, o "Mais" de TelaPet.tsx:377-378.
# As fixas no celular passam de 4 para 3 (o Carinho vai para o Mais, a direcao do Matheus; pergunta M1-2)
FIXAS = [("alimentar", "Alimentar", "drumstick"), ("brincar", "Brincar", "music"), ("limpar", "Limpar", "droplet")]
RESERVA = ' aria-label="Alimentar (reserva: põe a ração no comedouro)" title="Reserva temporária: põe a ração no comedouro"'


def acoes(sugerida: str | None = None, mais: bool = False, segurar: str | None = None) -> str:
    ids = [a for a, _, _ in FIXAS]
    if sugerida is not None and sugerida not in ids:
        raise ValueError("a sugerida tem de ser uma acao fixa: " + sugerida)
    if segurar is not None and segurar not in ids:
        raise ValueError("so se segura uma acao fixa: " + segurar)
    bts = []
    for a, rot, i in FIXAS:
        cls = "hx-btn dock-bt acao-destaque" + (" acao-destaque--sugerida" if a == sugerida else "") + (" dedo" if a == segurar else "")
        extra = RESERVA if a == "alimentar" else ""
        balao = f'<span class="cx rotulo-segurar" role="tooltip">{rot}</span>' if a == segurar else ""
        bts.append(f'<button type="button" class="{cls}"{extra}>{ic(i)}<span class="sr-only">{rot}</span>{balao}</button>')
    bts.append(f'<button type="button" class="hx-btn dock-bt acao-mais" aria-expanded="{str(mais).lower()}" aria-controls="acoes-mais" '
               f'aria-haspopup="true">{ic("x" if mais else "ellipsis")}<span class="sr-only">Mais</span></button>')
    menu = mais_menu() if mais else ""
    return f'<div class="pet-dock">{menu}<div class="acoes-pet dock" role="group" aria-label="Cuidar e ensinar">{"".join(bts)}</div></div>'


# o menu do Mais: Carinho, Tapa e Tratar (ROTULO_DONO; ORDEM_DOCK em TelaPet.tsx:327) e as duas barras dos pets com mundo, com os nomes
# de PorRacao.tsx:83 e PorBola.tsx:132 (pergunta M1-3: o Por racao fica)
def mais_menu() -> str:
    ex = "".join(f'<button type="button" class="hx-btn dock-bt acao-extra">{ic(i)}<span class="sr-only">{r}</span></button>'
                 for i, r in [("heart", "Carinho"), ("hand", "Tapa"), ("cross", "Tratar")])
    racao = ('<button type="button" class="hx-btn dock-bt racao-bt" aria-label="Pôr ração: arraste até o chão da cena, ou toque e escolha o lugar" '
             f'aria-pressed="false">{ic("bean")}</button>')
    bola = ('<button type="button" class="hx-btn dock-bt racao-bt bola-bt" aria-label="Pôr a bola: arraste até o chão da cena, ou toque para pôr '
            f'perto do pet">{ic("circle-dot")}</button>')
    return f'<div class="acoes-mais dock-mais" id="acoes-mais" role="group" aria-label="Mais ações">{ex}{racao}{bola}</div>'


# ---- so quando existe: o aviso. E o Resumo de hoje (TelaPet.tsx:313-321), o botao que abre o Estado: o nome continua o texto de ROTULO_BAIXO
# (TelaPet.tsx:274) e o "Estado"; a vista e so o icone de ICONE_NEC (TelaPet.tsx:209) e o % (Math.round(m.e[k] * 100), TelaPet.tsx:216)
ICONE_NEC = {"fome": "drumstick", "energia": "zap", "higiene": "droplet", "humor": "smile"}
ROTULO_BAIXO = {"fome": "está com fome", "energia": "energia baixa", "higiene": "higiene baixa", "humor": "humor baixo"}


def aviso(k: str, pct: int) -> str:
    return (f'<button type="button" class="pilula aviso-nec pet-prioridade">{ic(ICONE_NEC[k])}<span aria-hidden="true">{pct} %</span>'
            f'<span class="sr-only">{ROTULO_BAIXO[k]}</span><span class="sr-only">Estado</span></button>')


# ---- o chamado urgente, como hoje: o "Chamando voce" de Chamados (TelaPet.tsx:236-241), que aparece com temPedido (TelaPet.tsx:299-302).
# No jogo o icone e o emote do UP (emoji_exclam); na prancha, um icone de traco no lugar dele
def chamado() -> str:
    return ('<div class="pet-alerta"><div class="cx chamado dl-card"><span class="ic chamado-ic">' + ic("circle-alert") + '</span>'
            '<span class="chamado-txt"><b>Chamando você</b><span class="dl-apoio">um carinho atende</span></span>'
            '<button type="button" class="hx-continuar">Atender</button></div></div>')


# ---- por gesto: o toque no retrato. Os 5 vitais (NEC_PET e a saude, TelaPet.tsx:205 e :217; icones de ICONE_NEC e HeartPulse) sao um botao
# so, o "Estado atual" de hoje (TITULO_PAINEL, TelaPet.tsx:441), que abre o painel com os Detalhes; depois os outros paineis com os nomes de
# TITULO_PAINEL e ICONE_PAINEL (TelaPet.tsx:441-442), o Configuracoes (Topo.tsx:36) e o Meus pets (Topo.tsx:18; pergunta M1-1)
def leque(vit: dict[str, int]) -> str:
    nomes = [("fome", "comida", "drumstick"), ("energia", "energia", "zap"), ("higiene", "higiene", "droplet"), ("humor", "humor", "smile"),
             ("saude", "saúde", "heart-pulse")]
    if set(vit) != {k for k, _, _ in nomes}:
        raise ValueError("os cinco vitais do motor, nem mais nem menos")
    itens, desc = [], []
    for k, rot, i in nomes:
        v = vit[k]
        # o rosa abaixo de LIMIAR_NEC (0,5, TelaPet.tsx:279) nas quatro; a saude so muda abaixo de 0,3 (TelaPet.tsx:217), em --hx-perigo
        baixa = v < 50 if k != "saude" else False
        if k == "saude" and v < 30:
            raise ValueError("a saude critica nao esta desenhada nesta prancha")
        itens.append(f'<span class="vit{" baixa" if baixa else ""}" aria-hidden="true">{ic(i)}<b>{v}</b></span>')
        desc.append(f'{rot} {v} %' + (", baixa" if baixa else ""))
    vitais = (f'<button type="button" class="cx pilula leque-vitais" aria-label="Estado atual" aria-describedby="vit-desc" aria-pressed="false" '
              f'aria-controls="pet-painel">{"".join(itens)}<span class="sr-only" id="vit-desc">{"; ".join(desc)}</span></button>')
    paineis = "".join(f'<button type="button" class="cx forma bt48 ic" aria-label="{n}" aria-pressed="false" aria-controls="pet-painel">{ic(i)}</button>'
                      for i, n in [("trending-up", "Evolução"), ("history", "Últimas ações"), ("brain", "DigiBrain")])
    paineis += f'<button type="button" class="cx forma bt48 ic" aria-label="Configurações">{ic("settings")}</button>'
    paineis += f'<button type="button" class="cx forma bt48 ic" aria-label="Meus pets" aria-haspopup="dialog">{ic("users")}</button>'
    return f'<div id="leque" role="group" aria-label="Painéis do pet">{vitais}<div class="leque-paineis">{paineis}</div></div>'


# ---- os estados. Cada um: (titulo, fundo, corpo)
NORMAL_AGORA = agora("brincar", "aprendido", "Agora: brincando. Aprendido: sem ele, à toa. Porquê no DigiBrain.")


def normal() -> str:
    return (retrato() + relogio(3, "07:42") + coluna() + NORMAL_AGORA + acoes()
            + nota("sempre na tela: retrato, hora, a coluna, o ícone do agora (ciano tracejado: o aprendido mudou a escolha, "
                   "vistaAgora) e as 3 ações + Mais. Nenhum texto nem número fixo", "left:14px;top:250px")
            + nota("o fundo é a captura do jogo (cena_dia.png), cortada pelo cover: os 2 botões do HUD de hoje ficam fora", "right:14px;top:250px"))


def fome() -> str:
    return (retrato(ponto=True) + relogio(3, "07:42") + coluna()
            + aviso("fome", 12)
            + agora("explorar", "instinto", "Agora: explorando. Com fome: o instinto faria o mesmo. Porquê no DigiBrain.")
            + acoes(sugerida="alimentar")
            + nota("fome 12 % < FOME_FALA 0,15 (hudPet.ts:14): o aviso fica fixo enquanto valer (useAviso, TelaPet.tsx:308); o ponto rosa e o "
                   "Alimentar rosa e maior vêm de resumoAgora().acao (TelaPet.tsx:284-295, :356)", "left:14px;top:84px"))


def com_retrato() -> str:
    vit = {"fome": 64, "energia": 41, "higiene": 70, "humor": 72, "saude": 95}
    return (retrato(ponto=True, aberto=True) + relogio(3, "07:42") + coluna() + leque(vit) + NORMAL_AGORA + acoes()
            + nota("energia 41 < LIMIAR_NEC 0,5: o vital rosa e o ponto; ACAO_NEC.energia é null (TelaPet.tsx:276), nenhuma ação cresce. "
                   "Os vitais são o botão Estado atual", "left:80px;top:156px"))


def com_mais() -> str:
    return (retrato() + relogio(3, "07:42") + coluna() + NORMAL_AGORA + acoes(mais=True)
            + nota("o Mais aberto: Carinho, Tapa, Tratar, Pôr ração e Pôr a bola (as duas só nos pets com mundo); Esc, o toque fora "
                   "ou o × fecham, como hoje (TelaPet.tsx:359-366)", "left:14px;top:250px"))


def dormindo() -> str:
    return (retrato() + relogio(4, "01:25") + coluna()
            + agora("dormir", "uma", "Agora: dormindo. De noite: só havia uma opção. Porquê no DigiBrain.") + acoes()
            + nota("cena_noite.png é outra captura (outro pet, acordado); no jogo o pet dorme achatado com o zz (sono.ts). Sem aviso de "
                   "energia dormindo: pergunta M1-8", "left:14px;top:250px"))


def com_chamado() -> str:
    return (retrato() + relogio(3, "07:42") + coluna() + chamado()
            + agora("chamar_atencao", "instinto", "Agora: chamando você. Precisando de você: o instinto faria o mesmo. Porquê no DigiBrain.")
            + acoes()
            + nota("o chamado urgente como hoje: o cartão com texto e o Atender (temPedido, TelaPet.tsx:299-302); é a única caixa com texto "
                   "na tela", "left:14px;top:250px"))


def segurar() -> str:
    return (retrato() + relogio(3, "07:42") + coluna() + NORMAL_AGORA + acoes(segurar="brincar")
            + nota("segurar o dedo mostra o nome acessível de hoje num balão (o mesmo aparece no foco do teclado); o tempo do toque longo é "
                   "pergunta M1-9", "left:14px;top:250px"))


ESTADOS = {
    "normal": ("normal", DIA, normal),
    "fome": ("com fome", DIA, fome),
    "retrato": ("com o retrato aberto", DIA, com_retrato),
    "mais": ("com o Mais aberto", DIA, com_mais),
    "dormindo": ("dormindo", NOITE, dormindo),
    "chamado": ("com o chamado urgente", DIA, com_chamado),
    "segurar": ("segurando o dedo em Brincar", DIA, segurar),
}


def pagina(titulo: str, fundo: str, corpo: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UX Pet M1 · mobile mínimo · {titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@500;600;700&family=Rajdhani:wght@600;700&family=Saira+Condensed:wght@500;600;700&display=swap">
<link rel="stylesheet" href="minimo.css">
<script>
const q = new URLSearchParams(location.search), pele = q.get("pele") ?? "vidro";
if (pele !== "vidro" && pele !== "xcom") throw new Error("pele desconhecida: " + pele + " (vidro ou xcom)");
document.documentElement.dataset.pele = pele;
if (q.has("notas")) addEventListener("DOMContentLoaded", () => document.body.classList.add("notas"));
</script>
</head><body>
<div class="cena" style="background-image:url('{fundo}')" role="img" aria-label="A cena 3D do jogo (captura, fundo da prancha)"></div>
<section class="tela pet-tela" aria-label="Tela do pet">
{corpo}
</section>
<script src="{LUCIDE}"></script>
<script>
/* falhar alto: sem o lucide a prancha nao tem icone nenhum */
if (!window.lucide) document.body.insertAdjacentHTML("beforeend", '<p class="erro-prancha">os ícones (lucide) não carregaram</p>');
else lucide.createIcons();
</script>
</body></html>
'''


def main() -> None:
    for nome, (titulo, fundo, corpo) in ESTADOS.items():
        (AQUI / f"pet_{nome}.html").write_text(pagina(titulo, fundo, corpo()), encoding="utf-8", newline="\n")
    print(f"{len(ESTADOS)} paginas em {AQUI}")


if __name__ == "__main__":
    main()
