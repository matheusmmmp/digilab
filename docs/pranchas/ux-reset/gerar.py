# Gera a prancha "o reset e as duas pontuacoes" (docs/PLANO_UX_RESET.md; a etapa MMO8 do docs/PLANO_V3_MMO.md). So desenho; nenhum codigo
# do jogo. Duas partes: (A) o reset: aposentar o Digimon em Geracoes, o bonus (Respeito e Bits) e o ovo novo; (B) o perfil com as duas
# pontuacoes: os pontos do Digimon e o Respeito do Tamer, com os dois rankings.
# Usa os ajudantes da prancha dos lugares (../ux-lugares-menus/gerar.py e gerar_movel.py) e os da conta (../ux-conta/gerar.py: o painel, a
# folha, o aceite e os icones); o que e novo esta em reset.css. A pele vem de ?pele=vidro|xcom; no desktop ?sem tira as notas, e no celular
# as notas so aparecem com ?notas.
# Uso (da raiz): python docs/pranchas/ux-reset/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# DE ONDE VEM CADA TEXTO E CADA REGRA (docs/PLANO_V3_MMO.md, secoes 8 e 9; MMO-15 a MMO-19 APROVADAS em 2026-11-11):
#   o reset e do pet, nao do Tamer; aposenta em Geracoes ............ MMO-17; src/heranca.ts (CHAVE_GERACOES, Aposentado)
#   o ovo novo pela escolha do brasao ............................... MMO-17; src/jornada.ts (chocarDoBrasao)
#   o que zera e o que fica ......................................... a tabela da secao 9 do plano
#   os niveis do reset: Ultimate, Mega, Mega com a Liga ............. MMO-18; secao 9 (300/600/1000 de Respeito; 150/400/800 Bits; PROPOSTO)
#   sem heranca de stats ............................................ MMO-18 (a revisao CR-7/CR-8 do PLANO_V3_CICLO e outra etapa)
#   o Respeito do reset pede 200 pontos do Digimon conferidos ....... MMO-18 (PROPOSTO)
#   um reset pago em Bits por semana de relogio ..................... MMO-18 (PROPOSTO); MMO-19 (os Bits do reset, linha nova da M-2)
#   o cruzamento tambem conta como reset ............................ MMO-17
#   as duas pontuacoes e os dois rankings ........................... MMO-15; secao 8
#   o recorde sem teto; "Tamer Lendario" a partir de 10 000 ......... MMO-16 (PROPOSTO)
#   de onde vem o Respeito: 100 por lider, 500 a Liga, o reset,
#     100 por titulo da semana, 20 por selo ......................... a tabela da secao 8 (PROPOSTO); 100 e 20 ja no servidor (MMO7)
#   o nivel do Tamer do 11 em diante: 1 a cada 1 000 de Respeito .... MMO-15 (PROPOSTO)
#   o ranking conta so o que o servidor viu ......................... secao 8, "O que o servidor confere"
#   as rotas: GET /premios (o Respeito conferido), GET /tamers e
#     GET /digimons (os dois rankings) .............................. servidor_web/src/premios/ (MMO7 e MMO8, PR do codigo)
#   o apelido: um nome de Digimon e um numero ....................... CN2
# EXEMPLO DE LAYOUT, NUNCA DADO: os apelidos, os pontos, o Respeito, as posicoes, os dias, as horas, "Dia 41", "2a geracao".
# Os tamanhos de interface sao PROPOSTO, SEM FONTE.
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "ux-lugares-menus"))
import importlib.util  # noqa: E402
import gerar as G  # noqa: E402
import gerar_movel as M  # noqa: E402

_spec = importlib.util.spec_from_file_location("gerar_conta", AQUI.parent / "ux-conta" / "gerar.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

# o Ultimate e o Mega do exemplo (o brasao Coragem): quadros de Assets/arena_up/dados/atlas.json (w, h, sw, sh, passo x, passo y)
G.SPR["Wargrowlmon"] = (139, 108, 1119, 871, 140, 109)
G.SPR["Gallantmon"] = (189, 144, 1329, 1014, 190, 145)

IC = {
    "ancora": '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M8 11h8M4 14a8 8 0 0 0 16 0"/>',
    "ovo": '<path d="M12 3c-4 0-7 6-7 11a7 7 0 0 0 14 0c0-5-3-11-7-11z"/>',
    "coroa": '<path d="M3 8l4 4 5-7 5 7 4-4-2 11H5z"/>',
    "moeda": '<circle cx="12" cy="12" r="8"/><path d="M9 9h4.5a2 2 0 0 1 0 4H9h5a2 2 0 0 1 0 4H9V7"/>',
    "trofeu": '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3"/>',
    "caixa": '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
}
C.IC.update(IC)


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else C.ic(n, cls)


def _css(h: str) -> str:
    return (h.replace("<title>A conta · ", "<title>O reset · ").replace("<title>Lugares da ilha · ", "<title>O reset · ")
            .replace('href="conta.css"', 'href="../ux-conta/conta.css"')
            .replace("</head>", '<link rel="stylesheet" href="../ux-cais/cais.css">\n<link rel="stylesheet" href="reset.css">\n</head>'))


def cab(titulo: str) -> str:
    return _css(C.cab(titulo))


def cab_cel(titulo: str, topo: int, c360: bool = False) -> str:
    return _css(C.cab_cel(titulo, topo, c360))


FIM = G.FIM


def tela(titulo: str, caixa: str, notas: str = "", leque: bool = True, ultimate: bool = True) -> str:
    """o desktop: o molde da conta (C.tela) com o cabecalho desta prancha; o pet da ilha e o do exemplo (WarGrowlmon, Ultimate)"""
    pet = G.pet(1420, 600, "parado", k=1.1, nome="Wargrowlmon") if ultimate else G.pet(1160, 400, "parado")
    topo = G.topo(leque=leque, nome="Wargrowlmon", nivel="Ultimate · Coragem").replace("<b>Wargrowlmon</b>", "<b>WarGrowlmon</b>") if ultimate else G.topo(leque=leque)
    return (cab(titulo) + G.mundo("ilha", pet) + topo + G.trilho("pet") + G.pilha() + G.dock() + G.minimapa()
            + caixa + notas + FIM)


VOCE = "Agumon 4821"
# (pet, forma, estagio, dia da vida, geracao): o pet ativo do exemplo. EXEMPLO DE LAYOUT
ATIVO = ("Wargrowlmon", "WarGrowlmon", "Ultimate", 41, 2)
# os niveis do reset (PROPOSTOS, SEM FONTE; MMO-18): (nivel, o que o pet chegou a, Respeito, Bits)
NIVEIS = [(1, "Ultimate", 300, 150), (2, "Mega", 600, 400), (3, "Mega e o título da Liga", 1000, 800)]
LENDARIO = 10000


def num(n: int) -> str:
    return f"{n:,}".replace(",", " ")


# ---------------------------------------------------------------------------------------------------- A. as pecas do reset
def cartao_pet(nome: str = ATIVO[1], spr: str = ATIVO[0], est: str = ATIVO[2], dia: int = ATIVO[3], ger: int = ATIVO[4],
               extra: str = "") -> str:
    return (f'<div class="cartao rs-pet"><span class="palquinho">{G.spr(spr, .44 if spr != "Growlmon" else .58)}</span>'
            f'<span><b>{nome}</b><small>{est} · Coragem · Dia {dia} · {ger}ª geração</small>{extra}</span></div>')


def escada(atual: int) -> str:
    """os tres niveis do reset, com o do pet marcado em texto; o antes do Ultimate e 'sem bonus'"""
    def um(n: int, chegou: str, resp: int, bits: int) -> str:
        eu = n == atual
        cls = " rs-eu" if eu else (" rs-feito" if n < atual else "")
        etq = '<span class="etq aqui">este pet</span>' if eu else ""
        return (f'<li class="rs-nv{cls}"{" aria-current=&quot;true&quot;" if eu else ""}><span class="rs-nv-n">{n}</span>'
                f'<span><b>{chegou}</b>{etq}</span><span class="rs-nv-v"><b>+{num(resp)}</b><small>Respeito</small></span>'
                f'<span class="rs-nv-v"><b>+{bits}</b><small>Bits</small></span></li>')
    return (f'<ol class="rs-escada" aria-label="Os níveis do reset">{"".join(um(*x) for x in NIVEIS)}</ol>')


def bonus(resp_ok: bool = True, bits_ok: bool = True, nivel: int = 1, pontos: int = 240) -> str:
    """o que este reset da, em texto: o Respeito (com a trava dos 200 pontos conferidos) e os Bits (com a trava de um por semana)"""
    _, chegou, resp, bits = NIVEIS[nivel - 1]
    r_sub = (f"entra no ranking: ele tem {pontos} pontos conferidos (o mínimo é 200)" if resp_ok
             else f"fica só no seu perfil: ele tem {pontos} pontos conferidos, e o ranking pede 200")
    b_sub = ("o reset pago desta semana" if bits_ok else "o reset desta semana já foi pago: o próximo, na segunda")
    return f'''
<ul class="rs-bonus" aria-label="O bônus deste reset">
  <li class="{"" if resp_ok else "rs-parcial"}">{ic("coroa")}<span><b>+{num(resp)} Respeito</b><small>{r_sub}</small></span></li>
  <li class="{"" if bits_ok else "rs-parcial"}">{ic("moeda")}<span><b>{"+" + str(bits) if bits_ok else "0"} Bits</b><small>{b_sub}</small></span></li>
</ul>'''


def fica_sai() -> str:
    return f'''
<div class="rs-duas">
  <div><span class="rot">Vai para Gerações</span>
    <ul class="rs-lista">
      <li>{ic("geracoes")}{ATIVO[1]}, com a vida inteira, só para ver</li>
      <li>{ic("trofeu")}os pontos dele ficam no ranking dos Digimon</li>
      <li>{ic("chip")}os chips equipados voltam ao inventário</li>
    </ul></div>
  <div><span class="rot">Fica com você</span>
    <ul class="rs-lista fica">
      <li>{G.svg("check")}as medalhas, os itens e o título</li>
      <li>{G.svg("check")}os Bits, o portão e as melhorias</li>
      <li>{G.svg("check")}o nível, o Respeito, os selos</li>
      <li>{G.svg("check")}os pets guardados</li>
    </ul></div>
</div>'''


COMO_RESET = ("O reset é do pet, não do Tamer: o Digimon se aposenta e um ovo novo choca. O bônus vem do ponto a que ele chegou. "
              "O ovo novo começa do zero, sem os stats do anterior. O cruzamento também conta como reset do pai que se aposenta.")


def corpo_reset() -> str:
    return f'''
{cartao_pet()}
<div><span class="rot">O nível do reset</span>{escada(1)}</div>
{bonus()}
{fica_sai()}
{G.como(COMO_RESET).replace("Como funciona", "Como o reset funciona")}
<div class="ct-bts"><button type="button" class="bt">Agora não</button>
  <button type="button" class="bt perigo" style="margin-left:auto">{ic("ovo")}Aposentar e chocar um ovo</button></div>'''


def corpo_confirmar(marcado: bool = True) -> str:
    dis = "" if marcado else " disabled"
    return f'''
<div class="destaque perigo"><span class="rot">Sem volta</span><b class="grande">Aposentar {ATIVO[1]}</b>
  <ul class="ct-some">
    <li>{ic("geracoes")}Ele vai para Gerações e não volta a ser o ativo.</li>
    <li>{ic("ovo")}Você escolhe o brasão do ovo novo em seguida.</li>
    <li class="fica">{G.svg("check")}+300 Respeito e +150 Bits.</li>
  </ul></div>
{C.aceite(marcado, "Entendi que não volta")}
<div class="ct-bts"><button type="button" class="bt acao">Manter {ATIVO[1]}</button>
  <button type="button" class="bt perigo"{dis}>{ic("ovo")}Aposentar</button></div>'''


def corpo_feito() -> str:
    return f'''
<div class="destaque ok" role="status"><span class="rot">Reset feito</span><b class="grande">{ATIVO[1]} foi para Gerações</b>
  <p>Nível 1 do reset: o Ultimate.</p></div>
<ul class="rs-bonus" aria-label="O que entrou">
  <li>{ic("coroa")}<span><b>+300 Respeito</b><small>agora 2 640 · conferido quando o servidor vir o registro dele</small></span></li>
  <li>{ic("moeda")}<span><b>+150 Bits</b><small>saldo 1 230</small></span></li>
</ul>
<div class="ct-bts"><button type="button" class="bt acao">{ic("ovo")}Escolher o brasão</button></div>'''


# ---- os estados do reset (a caixa pequena)
def est_sem_bonus() -> str:
    return f'''
{cartao_pet("Growlmon", "Growlmon", "Champion", 18, 1)}
<div class="destaque" role="status"><span class="rot">Sem bônus</span><b class="grande">O bônus começa no Ultimate</b>
  <p>Aposentar agora é o recomeço de sempre: o pet vai para Gerações e nada entra.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Continuar com ele</button><button type="button" class="bt">Aposentar assim</button></div>'''


def est_mega() -> str:
    return f'''
{cartao_pet("Gallantmon", "Gallantmon", "Mega", 63, 2)}
{escada(2)}
{bonus(nivel=2, pontos=610)}'''


def est_liga() -> str:
    return f'''
{cartao_pet("Gallantmon", "Gallantmon", "Mega", 77, 2, '<span class="etq ok">título da Liga</span>')}
{escada(3)}
{bonus(nivel=3, pontos=940)}'''


def est_sem_pontos() -> str:
    return f'''
{cartao_pet()}
{bonus(resp_ok=False, pontos=80)}
<p class="ca-parcial">{ic("info", "ic ic-p")}<span>Os pontos vêm das lutas ranqueadas. Depois do reset, ele não luta mais.</span></p>'''


def est_bits_pagos() -> str:
    return f'''
{cartao_pet()}
{bonus(bits_ok=False)}
<p class="ca-parcial">{ic("info", "ic ic-p")}<span>O Respeito entra igual. Os Bits pagam um reset por semana.</span></p>'''


def est_sem_conta() -> str:
    return f'''
{cartao_pet()}
<ul class="rs-bonus"><li>{ic("coroa")}<span><b>+300 Respeito</b><small>no seu perfil; o ranking pede a conta</small></span></li>
  <li>{ic("moeda")}<span><b>+150 Bits</b><small>os Bits são do jogo, com ou sem conta</small></span></li></ul>
<div class="ct-bts"><button type="button" class="bt">{ic("conta")}Entrar</button><button type="button" class="bt perigo" style="margin-left:auto">{ic("ovo")}Aposentar</button></div>'''


def est_cruzar() -> str:
    return f'''
<div class="destaque" role="status"><span class="rot">Nova geração</span><b class="grande">O pai ativo se aposenta</b>
  <p>O cruzamento conta como reset: {ATIVO[1]} leva o bônus do nível dele.</p></div>
{bonus()}'''


# ---------------------------------------------------------------------------------------------------- B. o perfil e os rankings
# (feito, quantas, Respeito): a tabela da secao 8 (os valores PROPOSTOS); as contagens sao EXEMPLO
ORIGENS = [("medalhas", "1ª medalha de cada líder", "6 de 6", 600), ("coroa", "título da Liga", "1", 500),
           ("ovo", "resets", "nível 1 e nível 2", 900), ("trofeu", "títulos da semana", "2", 200), ("estrela", "selos Top do dia", "7", 140)]
CONFERIDO = 2340
LOCAL = 2640


def nivel_tamer(r: int) -> int:
    return 10 + r // 1000   # o 10 e o primeiro Mega; do 11 em diante, 1 a cada 1 000 (MMO-15, PROPOSTO)


def cartoes_pontuacao(curto: bool = False) -> str:
    pct = CONFERIDO / LENDARIO * 100
    prox = (nivel_tamer(CONFERIDO) + 1 - 10) * 1000
    return f'''
<div class="rs-pont">
  <section class="cartao rs-pc" aria-labelledby="rs-r"><span class="rot" id="rs-r">{ic("coroa")}Respeito do Tamer</span>
    <b class="rs-grande">{num(CONFERIDO)}</b>
    <small>conferido · {num(LOCAL)} no jogo</small>
    <span class="rs-linha"><span class="etq">Nv {nivel_tamer(CONFERIDO)}</span><small>Nv {nivel_tamer(CONFERIDO) + 1} em {num(prox)}</small></span>
    <span class="barra rs-barra" role="img" aria-label="{num(CONFERIDO)} de {num(LENDARIO)} até Tamer Lendário"><i style="--v:{pct:.0f}%"></i></span>
    <small>Tamer Lendário em {num(LENDARIO)} · a conta não para</small></section>
  <section class="cartao rs-pc" aria-labelledby="rs-d"><span class="rot" id="rs-d">{ic("trofeu")}Pontos do Digimon</span>
    <span class="rs-dg"><span class="palquinho">{G.spr("Wargrowlmon", .42)}</span><span><b class="rs-grande">1 120</b><small>WarGrowlmon · aposentado</small></span></span>
    <span class="rs-linha"><span class="etq ok">3º</span><small>no ranking dos Digimon</small></span>
    {"" if curto else '<small>O ativo, Agumon, tem 60. Cada pet começa do zero.</small>'}</section>
</div>'''


def origens(aberto: bool = True) -> str:
    lis = "".join(f'<li class="med-li">{ic(i)}<span><b>{t}</b><small>{q}</small></span><span class="rs-v">+{num(v)}</span></li>' for i, t, q, v in ORIGENS)
    a = " open" if aberto else ""
    return (f'<details class="rs-de"{a}><summary>{G.svg("info")}De onde vem o Respeito{G.svg("seta")}</summary>'
            f'<ul class="med-lista">{lis}</ul>'
            f'<p class="ca-txt sec">O ranking conta só o que o servidor viu nos registros enviados. Um reset que o servidor ainda não viu fica só no jogo (+300).</p></details>')


def corpo_perfil(curto: bool = False) -> str:
    return f'''
{C.cartao_apelido(f'<button type="button" class="bt">{G.svg("replay")}Trocar</button>', "Google · desde 12/11/2026")}
{cartoes_pontuacao(curto)}
{origens(not curto)}
<div class="ct-bts"><button type="button" class="bt acao">{ic("ancora")}Ver os rankings no cais</button></div>
<button type="button" class="fechado">{ic("pc")}<span>Aparelhos, dados e a conta</span>{G.svg("seta")}</button>'''


# os rankings: (posicao, apelido, Respeito) e (posicao, Digimon, Tamer, pontos, aposentado). EXEMPLO DE LAYOUT
TAMERS = [(1, "Gabumon 0317", 11240, True), (2, "Palmon 7740", 8320, False), (3, "Tentomon 1206", 6100, False), (4, "Patamon 5589", 4780, False),
          (5, "Biyomon 9034", 3900, False), (6, "Gomamon 2251", 3120, False), (7, "Guilmon 6612", 2980, False), (8, "Gabumon 4408", 2600, False),
          (14, VOCE, CONFERIDO, False)]
DIGIMONS = [(1, "Gallantmon", "Palmon 7740", 2310, False), (2, "MetalGarurumon", "Gabumon 0317", 1940, True), (3, "WarGrowlmon", VOCE, 1120, True),
            (4, "Angewomon", "Patamon 5589", 1080, False), (5, "MegaKabuterimon", "Tentomon 1206", 960, True), (6, "Garudamon", "Biyomon 9034", 900, False),
            (7, "WereGarurumon", "Gabumon 4408", 760, True), (8, "Zudomon", "Gomamon 2251", 720, False)]


def abas(atual: str) -> str:
    def a(n: str) -> str:
        s = "true" if n == atual else "false"
        return f'<button type="button" role="tab" class="filtro" aria-selected="{s}" aria-pressed="{s}">{n}</button>'
    return f'<div class="ca-est rs-abas" role="tablist" aria-label="Rankings do cais">{"".join(a(n) for n in ["Semana", "Tamers", "Digimon", "Mural"])}</div>'


def tab_tamers(n: int = 8) -> str:
    def li(p: int, nome: str, r: int, lend: bool) -> str:
        eu = nome == VOCE
        e = '<span class="etq aqui">você</span>' if eu else ""
        t = '<span class="etq alerta">Lendário</span>' if lend else ""
        return (f'<tr class="{"ca-eu" if eu else ""}"><td class="ca-pos">{p}º</td><th scope="row"><span>{nome}</span>{e}{t}</th>'
                f'<td class="ca-pts">{num(r)}</td><td>Nv {nivel_tamer(r)}</td></tr>')
    top = [x for x in TAMERS if x[0] <= n]
    eu = [x for x in TAMERS if x[1] == VOCE and x[0] > n]
    corpo = "".join(li(*x) for x in top) + ("".join('<tr class="ca-salto" aria-hidden="true"><td colspan="4">· · ·</td></tr>' + li(*x) for x in eu))
    return (f'<table class="ca-tab"><caption class="so-leitor">Ranking dos Tamers pelo Respeito conferido</caption><thead><tr><th scope="col">#</th>'
            f'<th scope="col">Tamer</th><th scope="col">Respeito</th><th scope="col">Nível</th></tr></thead><tbody>{corpo}</tbody></table>')


def tab_digimons(n: int = 8, curto: bool = False) -> str:
    def li(p: int, forma: str, tamer: str, pts: int, apos: bool) -> str:
        eu = tamer == VOCE
        e = '<span class="etq aqui">seu</span>' if eu else ""
        a = '<span class="etq">aposentado</span>' if apos else ""
        t = "" if curto else f'<td class="rs-tamer">{tamer}</td>'
        return (f'<tr class="{"ca-eu" if eu else ""}"><td class="ca-pos">{p}º</td><th scope="row"><span>{forma}</span>{e}{a}</th>{t}'
                f'<td class="ca-pts">{num(pts)}</td></tr>')
    corpo = "".join(li(*x) for x in DIGIMONS[:n])
    tc = "" if curto else '<th scope="col">Tamer</th>'
    return (f'<table class="ca-tab"><caption class="so-leitor">Ranking dos Digimon: o total da vida de cada pet</caption><thead><tr><th scope="col">#</th>'
            f'<th scope="col">Digimon</th>{tc}<th scope="col">Pontos</th></tr></thead><tbody>{corpo}</tbody></table>')


def corpo_tamers() -> str:
    return f'''
{abas("Tamers")}
{tab_tamers()}
<p class="ca-parcial">{ic("info", "ic ic-p")}<span>O Respeito só sobe. "Lendário" a partir de {num(LENDARIO)}; a conta não para.</span></p>
{G.como("O Respeito vem dos feitos do Tamer e dos resets, só os que o servidor conferiu. No empate, fica na frente quem chegou antes.").replace("Como funciona", "Como a tabela conta")}'''


def corpo_digimons(curto: bool = False) -> str:
    return f'''
{abas("Digimon")}
{tab_digimons(6 if curto else 8, curto)}
<p class="ca-parcial">{ic("info", "ic ic-p")}<span>Uma linha por pet, pelo total da vida. O aposentado fica com o que tinha.</span></p>'''


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def reset_1920() -> str:
    return tela("o reset", C.painel("Aposentar", corpo_reset(), icone="users", sub="Meus pets", voltar="Voltar a Meus pets", x=100, y=110, w=520),
                  G.nota("1 · 'Aposentar' entra em Meus pets, no cartão do ativo, ao lado de 'Novo ovo' e 'Nova geração' (UX-RS-1)", 640, 120, 300)
                  + G.nota("o nível do reset em texto e em escada: 1 Ultimate, 2 Mega, 3 Mega com a Liga. O deste pet diz 'este pet' (MMO-18)", 640, 210, 300)
                  + G.nota("o bônus em duas linhas, cada uma com a trava dela em texto: os 200 pontos conferidos (Respeito) e um reset pago por semana (Bits)", 640, 320, 300)
                  + G.nota("o que vai e o que fica, a tabela da seção 9 do plano em 7 linhas. Sem herança de stats: está no 'Como o reset funciona'", 640, 440, 300)
                  + G.nota("o botão é tracejado, na cor do perigo, à direita e longe de 'Agora não': não se desfaz", 640, 560, 300)
                  + G.nota("o pet, os dias, a geração e os pontos são EXEMPLO; os 300/150, 200 e 'um por semana' são PROPOSTOS do plano", 640, 650, 300)
                  + G.contagem(480, 92))


def confirmar_1920() -> str:
    return tela("o reset: confirmar", C.painel("Aposentar", corpo_confirmar(), icone="users", sub="Meus pets", voltar="Voltar", x=100, y=150, w=460)
                  + C.painel("Aposentar", corpo_feito(), icone="users", sub="Meus pets", voltar="", x=620, y=150, w=460, cls="rs-segundo"),
                  G.nota("2 · a confirmação: o molde de 'Apagar a conta' (a caixa de perigo, o aceite, o botão que só acende com ele). O principal é manter (UX-RS-2)", 1110, 160, 320)
                  + G.nota("3 · feito: o que entrou, em texto, e um caminho só, 'Escolher o brasão', a tela do ovo de hoje (jornada.ts)", 1110, 300, 320)
                  + G.nota("o Respeito diz 'conferido quando o servidor vir o registro dele': o jogo manda o registro do aposentado sozinho, com a conta (UX-RS-4)", 1110, 400, 320)
                  + G.nota("os dois painéis lado a lado são só da prancha: no jogo, o segundo troca o corpo do primeiro", 1110, 520, 320), leque=False)


def _grade(titulo: str, itens: list, w: int = 500, passo_y: int = 480) -> str:
    def est(i: int, rot: str, corpo: str) -> str:
        x = 40 + (i % 3) * 620
        y = 96 + (i // 3) * passo_y
        return G.nota(rot, x, y, 560) + C.painel("Aposentar", corpo, icone="users", sub="Meus pets", voltar="", x=x, y=y + 44, w=w, cls="ct-estado rs-estado")
    return (cab(titulo) + G.mundo("ilha", "") + '<div class="veu"></div>'
            + f'<span class="caixa titulo-pr" style="position:absolute;left:40px;top:36px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">{titulo}</span>'
            + "".join(est(i, r, c) for i, (r, c) in enumerate(itens)))


def estados_1920() -> str:
    return (_grade("O reset: os níveis e os estados", [
        ("4a · antes do Ultimate: sem bônus, dito em texto. O principal é continuar; aposentar assim é o recomeço de hoje", est_sem_bonus()),
        ("4b · nível 2, o Mega: a escada marca o 1 como passado e o 2 como 'este pet'", est_mega()),
        ("4c · nível 3, o Mega com o título da Liga deste pet: a etiqueta do título no cartão", est_liga()),
        ("4d · sem os 200 pontos conferidos: o Respeito entra só no perfil, e a linha diz por quê", est_sem_pontos()),
        ("4e · os Bits desta semana já pagos: a linha dos Bits diz 0 e quando volta", est_bits_pagos()),
        ("4f · sem conta: o Respeito fica no perfil local; os Bits entram igual. 'Entrar' é secundário (CN-1)", est_sem_conta()),
    ]) + G.nota("o cruzamento (Nova geração) mostra a linha do bônus do pai que se aposenta, acima do 'Cruzar' de hoje (MMO-17)", 1300, 36, 560) + FIM)


def perfil_1920() -> str:
    return tela("o perfil: as duas pontuações", C.painel("Conta", corpo_perfil(), x=100, y=72, w=540),
                  G.nota("5 · o perfil abre pelas duas pontuações, lado a lado: a do Tamer e a do Digimon. Cada uma com o seu ranking (MMO-15)", 660, 106, 310)
                  + G.nota("o Respeito grande é o conferido, o do ranking; o do jogo vem menor ao lado (seção 8: 'a tela pode mostrar um local maior')", 660, 210, 310)
                  + G.nota("o nível do Tamer passa do 10 pelo Respeito, um a cada 1 000 (PROPOSTO). A barra vai até 'Lendário' (10 000) e a frase diz que a conta não para (MMO-16)", 660, 320, 310)
                  + G.nota("os pontos do Digimon: o melhor pet do Tamer, com a posição. O ativo vem embaixo, em texto: cada pet começa do zero", 660, 450, 310)
                  + G.nota("'De onde vem o Respeito': os cinco feitos da seção 8, cada um com a soma. Aberto aqui; no jogo, fechado", 660, 560, 310)
                  + G.nota("os aparelhos, os dados e apagar descem para uma linha (a prancha da conta, UX-CN). Os números são EXEMPLO", 660, 680, 310)
                  + G.contagem(500, 54))


def rankings_1920() -> str:
    px, py = G.tela(260, 330, "ilha")
    return (cab("os rankings no cais") + G.mundo("ilha", G.pet(1500, 640, "parado")) + G.topo(agora=False) + G.trilho("pet") + G.minimapa()
            + f'<span class="caixa placa-lugar" style="left:{px - 40:.0f}px;top:{py - 62:.0f}px">{ic("ancora")}Cais</span>'
            + C.painel("Cais", corpo_tamers(), icone="ancora", sub="ranking dos Tamers", voltar="", x=360, y=84, w=520, cls="ca-painel")
            + C.painel("Cais", corpo_digimons(), icone="ancora", sub="ranking dos Digimon", voltar="", x=910, y=84, w=560, cls="ca-painel rs-segundo")
            + G.nota("6 · o cais ganha duas abas, 'Tamers' e 'Digimon', ao lado de 'Semana' e 'Mural' (UX-RS-3). O mesmo molde da tabela da semana", 1500, 96, 300)
            + G.nota("Tamers: pelo Respeito conferido. 'Lendário' em texto, sem parar a conta; o nível ao lado. A sua linha vem sempre", 1500, 220, 300)
            + G.nota("Digimon: o máximo histórico, uma linha por pet, pelo total da vida. 'aposentado' em texto: ele fica com o que tinha", 1500, 340, 300)
            + G.nota("os dois rankings não têm semana: não zeram (seção 8). As abas lado a lado são só da prancha", 1500, 460, 300)
            + G.nota("os apelidos, os pontos e o Respeito são EXEMPLO", 1500, 560, 300)
            + FIM)


def estados_perfil_1920() -> str:
    sem_conta = f'''
<div class="rs-pont"><section class="cartao rs-pc"><span class="rot">{ic("coroa")}Respeito do Tamer</span><b class="rs-grande">{num(LOCAL)}</b>
  <small>no jogo · o ranking pede a conta</small></section>
  <section class="cartao rs-pc"><span class="rot">{ic("trofeu")}Pontos do Digimon</span><b class="rs-grande">—</b><small>as lutas ranqueadas pedem a conta</small></section></div>
<div class="ct-bts"><button type="button" class="bt acao">{ic("conta")}Entrar</button><button type="button" class="bt">Agora não</button></div>'''
    sem_rede = f'''
<div class="destaque" role="alert"><span class="rot">Sem resposta</span><b class="grande">O conferido não veio</b>
  <p>O Respeito do jogo continua aqui: {num(LOCAL)}.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Tentar de novo</button></div>'''
    zero = f'''
<div class="rs-pont"><section class="cartao rs-pc"><span class="rot">{ic("coroa")}Respeito do Tamer</span><b class="rs-grande">0</b>
  <small>a 1ª medalha de cada líder vale 100</small></section>
  <section class="cartao rs-pc"><span class="rot">{ic("trofeu")}Pontos do Digimon</span><b class="rs-grande">0</b><small>a luta ranqueada abre no Nv 10</small></section></div>'''
    vazia = f'''
{abas("Digimon")}
<div class="ca-vazia" role="status"><b>Nenhum Digimon pontuou ainda</b><span>A tabela nasce com a primeira vitória ranqueada conferida.</span></div>'''
    return (cab("o perfil: os estados") + G.mundo("ilha", "") + '<div class="veu"></div>'
            + '<span class="caixa titulo-pr" style="position:absolute;left:40px;top:36px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">O perfil e os rankings: os estados</span>'
            + G.nota("7a · sem conta: o Respeito do jogo aparece igual; o ranking e os pontos pedem a conta", 40, 96, 560)
            + C.painel("Conta", sem_conta, x=40, y=140, w=520, cls="ct-estado")
            + G.nota("7b · o servidor não respondeu: o número do jogo fica, e o conferido espera", 660, 96, 560)
            + C.painel("Conta", sem_rede, x=660, y=140, w=520, cls="ct-estado")
            + G.nota("7c · o Tamer novo: os zeros com o primeiro passo de cada um, em texto", 1280, 96, 560)
            + C.painel("Conta", zero, x=1280, y=140, w=520, cls="ct-estado")
            + G.nota("7d · o ranking dos Digimon sem ninguém: uma frase, sem tabela vazia", 40, 520, 560)
            + C.painel("Cais", vazia, icone="ancora", sub="ranking dos Digimon", voltar="", x=40, y=564, w=520, cls="ct-estado")
            + FIM)


# ---------------------------------------------------------------------------------------------------- as telas a 390
def _cel(titulo: str, caixa_titulo: str, corpo: str, topo: int, nota: str = "", icone: str = "users", sub: str = "Meus pets",
         voltar: str = "Voltar a Meus pets", c360: bool = False) -> str:
    return (cab_cel(titulo, topo, c360) + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna()
            + C.folha(caixa_titulo, corpo, icone=icone, sub=sub, voltar=voltar).replace('class="caixa folha', 'class="caixa folha rs-folha')
            + (M.nota(nota, 14, topo - 80) if nota else "") + FIM)


def reset_390() -> str:
    corpo = f'''
{cartao_pet()}
{escada(1)}
{bonus()}
{G.como(COMO_RESET).replace("Como funciona", "Como o reset funciona")}
<div class="ct-bts"><button type="button" class="bt">Agora não</button><button type="button" class="bt perigo">{ic("ovo")}Aposentar</button></div>'''
    return _cel("o reset · 390", "Aposentar", corpo, 120, "a folha alta: o pet, a escada, o bônus. 'O que vai e o que fica' entra no 'Como o reset funciona'")


def confirmar_390() -> str:
    return _cel("o reset: confirmar · 390", "Aposentar", corpo_confirmar(), 380)


def perfil_390() -> str:
    return _cel("o perfil · 390", "Conta", corpo_perfil(curto=True), 96, icone="conta", sub="Ajustes", voltar="Voltar aos Ajustes")


def rankings_390() -> str:
    return _cel("os rankings · 390", "Cais", corpo_digimons(curto=True), 230, icone="ancora", sub="ranking dos Digimon", voltar="")


TELAS = {
    "reset_1920": reset_1920, "confirmar_1920": confirmar_1920, "estados_1920": estados_1920,
    "perfil_1920": perfil_1920, "rankings_1920": rankings_1920, "estados_perfil_1920": estados_perfil_1920,
    "reset_390": reset_390, "confirmar_390": confirmar_390, "perfil_390": perfil_390, "rankings_390": rankings_390,
}


def escrever() -> None:
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")


if __name__ == "__main__":
    escrever()
