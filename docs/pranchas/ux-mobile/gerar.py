# Gera as pranchas da M1 do mobile "Digivice" (UX_TELA_PET): a tela Pet e a barra de abas abaixo de 900 px, um HTML por estado.
# Uso: python docs/pranchas/ux-mobile/gerar.py   (escreve pet_<estado>.html ao lado). So desenho; nenhum codigo do jogo.
# No endereco: ?tema=claro|escuro (os --dl-* mudam com o tema; a pele vidro|xcom nao muda nada no Digivice), ?aba=amarela (a aba ativa
# da direcao, pergunta M1-1), ?pulsa (o pulso do vital baixo, pergunta M1-2) e ?sem (tira as notas amarelas).
# A mesma pagina serve a 390 x 844 e a 360 x 800 (o capturar.sh poe num iframe de cada largura).
# Os textos sao os do jogo (cada um com a fonte na nota da secao "Mobile Digivice (M1, 2026-11-06)" do PROPOSTAS_V3_UX_TELA_PET.md);
# os numeros (64 %, D3 07:42) sao exemplo de layout, nunca dado.
from pathlib import Path

A = "../../../../Assets/arena_up"  # fora do git (UI_GUIDELINES 5.1); so as capturas precisam dele

# icones simples (traco), so para a prancha; no jogo sao os lucide e as pecas do atlas de hoje
IC = {
    "comida": '<path d="M15 4a5 5 0 0 1 0 8l-2 2-4-4 2-2a5 5 0 0 1 4-4z"/><path d="M9 10l-5 5 2 1 1 2 5-5"/>',
    "energia": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "higiene": '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/>',
    "humor": '<circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    "saude": '<path d="M20 8.5C20 5.5 17.5 4 15.5 4 13.8 4 12.7 5 12 6c-.7-1-1.8-2-3.5-2C6.5 4 4 5.5 4 8.5 4 13 12 20 12 20s8-7 8-11.5z"/><path d="M5 12h4l1.5-3 2 6 1.5-3H19"/>',
    "alimentar": '<path d="M4 13h16a8 8 0 0 1-16 0z"/><path d="M12 5v4M9 6v3M15 6v3"/>',
    "brincar": '<path d="M9 18V6l10-2v12"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="16" r="2"/>',
    "limpar": '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/><path d="M9 14a3 3 0 0 0 3 3"/>',
    "acariciar": '<path d="M20 8.5C20 5.5 17.5 4 15.5 4 13.8 4 12.7 5 12 6c-.7-1-1.8-2-3.5-2C6.5 4 4 5.5 4 8.5 4 13 12 20 12 20s8-7 8-11.5z"/>',
    "mais": '<circle cx="5" cy="12" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="19" cy="12" r="1.4"/>',
    "pet": '<circle cx="12" cy="14" r="5"/><circle cx="6" cy="8" r="1.8"/><circle cx="18" cy="8" r="1.8"/><circle cx="10" cy="5" r="1.6"/><circle cx="14" cy="5" r="1.6"/>',
    "crescer": '<path d="M12 21v-9"/><path d="M12 12c0-4 3-6 7-6 0 4-3 6-7 6z"/><path d="M12 14c0-3-2-5-6-5 0 3 2 5 6 5z"/>',
    "lutar": '<path d="M5 19L19 5"/><path d="M14 5h5v5"/><path d="M5 14l5 5"/><path d="M19 19L9 9"/>',
    "diario": '<path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M8 7h6"/>',
    "conversar": '<path d="M4 5h16v11H9l-5 4z"/>',
    "ajustes": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
    "estado": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "evolucao": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "acoes": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>',
    "digibrain": '<path d="M12 4c-4 0-7 3-7 7 0 4 3 8 7 8s7-4 7-8c0-4-3-7-7-7z"/><path d="M12 4v15M8 9h2M14 9h2M8 14h2M14 14h2"/>',
    "seta": '<path d="M9 6l6 6-6 6"/>',
}


def svg(n: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>'


# ---- os estados (um HTML cada). vit: comida, energia, higiene, humor, saude em % (Math.round(m.e[k] * 100), TelaPet.tsx:216-217);
# nec: os que estao abaixo de LIMIAR_NEC (TelaPet.tsx:279); agora: (NOME_PET[m.acao], caso da LinhaAgora); sug: resumoAgora(...).acao
ESTADOS = {
    "normal": dict(vit=[64, 81, 70, 72, 95], nec=[], agora=("brincando", "aprendido", "à toa"), sug="brincar", alerta=None,
                   sono=False, emote=False, hora=("D3", "07:42"), dia=3,
                   notas=[("left:10px;top:330px", "a sugerida vem do desejo aprendido \"quer brincar\" (resumoAgora, ACAO_DESEJO)"),
                          ("left:10px;top:156px", "os 5 vitais sempre visíveis: hoje só no painel Estado")]),
    "vital": dict(vit=[35, 81, 70, 72, 95], nec=["comida"], agora=("comendo", "instinto", None), sug="alimentar", alerta="resumo",
                  sono=False, emote=True, hora=("D3", "09:15"), dia=3,
                  notas=[("left:10px;top:244px", "o resumo de 15 s sem o \"agora: …\" (o balão já diz o que ele faz)"),
                         ("left:10px;top:156px", "comida abaixo de 50 % (LIMIAR_NEC): rosa sólido; o pulso só com ?pulsa (M1-2)")]),
    "dormindo": dict(vit=[58, 18, 66, 70, 95], nec=["energia"], agora=("dormindo", "uma", None), sug=None, alerta=None,
                     sono=True, emote=False, hora=("D3", "14:10"), dia=3,
                     notas=[("left:10px;top:330px", "dormindo: o pet achatado, mais apagado, com o zz (sono.ts); a energia não tem ação, nada amarelo"),
                            ("left:10px;top:156px", "energia baixa: rosa sólido")]),
    "chamado": dict(vit=[12, 74, 62, 55, 90], nec=["comida"], agora=("chamando você", "uma", None), sug="alimentar", alerta="pedido",
                    sono=False, emote=True, hora=("D3", "11:40"), dia=3,
                    notas=[("left:10px;top:244px", "o cartão de hoje (Chamados, temPedido), sem \"AGORA\": o balão do pet diz o que ele faz"),
                           ("left:10px;top:330px", "achado M1-10: o cartão diz carinho, o dock sugere Alimentar (a necessidade mais baixa)")]),
}
ROT_VIT = [("comida", "comida"), ("energia", "energia"), ("higiene", "higiene"), ("humor", "humor"), ("saude", "saúde")]


def vitais(e: dict) -> str:
    itens = []
    for (ic, rot), v in zip(ROT_VIT, e["vit"]):
        nec = ic in e["nec"]
        baixo = ", baixa" if nec else ""
        itens.append(f'<li class="vit{" nec" if nec else ""}" aria-label="{rot} {v} %{baixo}">{svg(ic)}'
                     f'<b aria-hidden="true">{v}<small>%</small></b><span class="rot" aria-hidden="true">{rot}</span></li>')
    return f'<ul class="vitais" aria-label="Necessidades">{"".join(itens)}</ul>'


def agora(e: dict) -> str:
    acao, caso, sem_ele = e["agora"]
    # rotuloAgora(v, true) (LinhaAgora.tsx:44-51); a forma curta do meio (agora-curto, pet_hud.css:165-166)
    if caso == "aprendido":
        meio, porque = '<span class="chip aprendido">aprendido</span>', f"Aprendido: sem ele, {sem_ele}."
    elif caso == "instinto":
        meio, porque = '<span class="neutro">instinto</span>', "Com fome: o instinto faria o mesmo."
    elif caso == "uma":
        regra = "Exausto" if acao == "dormindo" else "Precisando de você"
        meio, porque = '<span class="neutro">uma opção</span>', f"{regra}: só havia uma opção."
    elif caso == "sem":
        meio, porque = '<span class="chip sem"><b>?</b>sem motivo registrado</span>', "Sem motivo registrado."
    else:
        raise ValueError("caso desconhecido: " + caso)
    rot = f"Agora: {acao}. {porque} Porquê no DigiBrain."
    seta = svg("seta").replace("<svg ", '<svg class="seta" ', 1)
    return (f'<button type="button" class="agora" aria-label="{rot}" aria-expanded="false" aria-controls="pet-painel">'
            f'<span class="acao" aria-hidden="true">{acao}</span><span class="ponto" aria-hidden="true">·</span>'
            f'<span aria-hidden="true" style="display:contents">{meio}</span>{seta}</button>')


def alerta(e: dict) -> str:
    if e["alerta"] is None:
        return ""
    if e["alerta"] == "resumo":
        # Resumo (TelaPet.tsx:313-321): o texto de resumoAgora (desejo de necessidade: "precisa " + ALVOS_DESEJO.comer[1]); abre o Estado
        return ('<button type="button" class="alerta"><span class="ic" aria-hidden="true">' + svg("comida") + '</span>'
                '<span class="txt"><b>precisa comer</b></span><span class="ver">Estado' + svg("seta") + '</span></button>')
    # Chamados, o pedido sem chamado aberto (TelaPet.tsx:236-242): o pet em chamar_atencao
    return ('<div class="alerta" role="group" aria-label="Chamando você"><span class="ic" aria-hidden="true">!</span>'
            '<span class="txt"><b>Chamando você</b><small>um carinho atende</small></span>'
            '<button type="button" class="prim">Atender</button></div>')


def corpo(nome: str, e: dict) -> str:
    sug = e["sug"]
    # o dock do celular: as quatro primeiras de ORDEM_DOCK e o Mais (TelaPet.tsx:327, :357); rotulos de ROTULO_DONO (acoes.ts:11)
    acoes = [("alimentar", "Alimentar"), ("brincar", "Brincar"), ("limpar", "Limpar"), ("acariciar", "Carinho")]
    bts = []
    for a, r in acoes:
        cls = "ac" + (" sug" if a == sug else "")
        if a == "alimentar":
            # pets com mundo (v12+): o Alimentar e a reserva (TelaPet.tsx:370-373)
            bts.append(f'<button type="button" class="{cls}" aria-label="Alimentar (reserva: põe a ração no comedouro)">{svg(a)}<span>{r}</span>'
                       '<small aria-hidden="true">reserva</small></button>')
        else:
            bts.append(f'<button type="button" class="{cls}">{svg(a)}<span>{r}</span></button>')
    bts.append(f'<button type="button" class="ac mais" aria-expanded="false" aria-controls="acoes-mais" aria-haspopup="true">{svg("mais")}<span>Mais</span></button>')
    lado = "".join(f'<button type="button" class="bt" aria-pressed="false" aria-controls="pet-painel" aria-label="{r}" title="{r}">{svg(n)}</button>'
                   for n, r in [("estado", "Estado atual"), ("evolucao", "Evolução"), ("acoes", "Últimas ações"), ("digibrain", "DigiBrain")])
    lado += f'<button type="button" class="bt cfg" aria-label="Configurações">{svg("ajustes")}</button>'
    atual = ' aria-current="page"'
    abas = "".join(f'<button type="button" class="aba"{atual if n == "pet" else ""}><span class="circ">{svg(n)}</span>{r}</button>'
                   for n, r in [("pet", "Pet"), ("crescer", "Crescer"), ("lutar", "Lutar"), ("diario", "Diário")])
    pet = '<div class="pet dorme"></div><div class="zz" aria-hidden="true">z<i>z</i></div>' if e["sono"] else '<div class="pet"></div>'
    emote = f'<div class="emote" aria-hidden="true">{svg("comida")}</div>' if e["emote"] else ""
    notas = "".join(f'<span class="nota" style="{p}">{t}</span>' for p, t in e["notas"])
    d, h = e["hora"]
    return f'''
<div class="cena" role="img" aria-label="Fundo neutro no lugar da ilha 3D, com o Gabumon{" dormindo" if e["sono"] else ""}"><div class="sombra"></div>{pet}{emote}</div>
<header class="topo">
  <div class="placa"><button type="button" class="retrato" aria-haspopup="dialog" aria-label="Meus pets"><i></i></button>
    <span class="placa-txt"><b>Gabumon</b><span class="estagio">Rookie</span></span></div>
  <span class="lcd" role="group" aria-label="{h}, dia {e["dia"]}"><small>{d}</small>{h}</span>
  <button type="button" class="bt" aria-label="Conversar">{svg("conversar")}</button>
</header>
{vitais(e)}
{alerta(e)}
<nav class="lado" aria-label="Painéis do pet">{lado}</nav>
{agora(e)}
<div class="dock" role="group" aria-label="Cuidar e ensinar">{"".join(bts)}</div>
<nav class="abas dl-nav" aria-label="Destinos">{abas}</nav>
{notas}
</body></html>
'''


def cab(nome: str) -> str:
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UX Pet M1 Digivice · {nome}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rubik:ital,wght@1,900&family=M+PLUS+Rounded+1c:wght@700;800;900&family=DotGothic16&display=swap">
<link rel="stylesheet" href="mobile.css">
<style>:root{{--assets-spr:url("{A}/sprites/Gabumon.png")}}</style>
<script>const q=new URLSearchParams(location.search);document.documentElement.dataset.tema=q.get("tema")==="escuro"?"escuro":"claro";
addEventListener("DOMContentLoaded",()=>{{const b=document.body.classList;if(q.has("sem"))b.add("sem-notas");if(q.get("aba")==="amarela")b.add("aba-amarela");if(q.has("pulsa"))b.add("pulsa");}});</script>
</head><body>'''


d = Path(__file__).parent
for nome, e in ESTADOS.items():
    (d / f"pet_{nome}.html").write_text(cab(nome) + corpo(nome, e), encoding="utf-8", newline="\n")
