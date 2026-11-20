# Gera a prancha "a conta: entrar e primeiro acesso" (docs/PLANO_UX_CONTA.md). So desenho; nenhum codigo do jogo.
# As telas sao a 1 (Entrar), a 2 (Primeiro acesso) e a parte da CN2 da 4 (Perfil e conta) do docs/PLANO_V3_CONTA.md, secao 3.
# Usa os ajudantes da prancha dos lugares (../ux-lugares-menus/gerar.py e gerar_movel.py: os icones, a ilha, a HUD, a nota) e os tokens
# de la (lugares.css, movel.css); o que e novo esta em conta.css. A pele vem de ?pele=vidro|xcom; no desktop ?sem tira as notas, e no
# celular as notas so aparecem com ?notas.
# Uso (da raiz): python docs/pranchas/ux-conta/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# DE ONDE VEM CADA TEXTO E CADA REGRA (docs/PLANO_V3_CONTA.md, CN-1 a CN-10 DECIDIDAS pelo Matheus em 2026-11-11):
#   a conta e escolha, o jogo abre sem ela ............ CN-1 (secao 2): "o jogo primeiro, a conta depois"
#   Google e GitHub, sem senha ........................ CN-2 (secao 2); nao ha formulario de e-mail e senha, nem "esqueci a senha"
#   a entrada por Ajustes ("Conta") ................... secao 2; o cais fica para o MMO (lugaresIlha.ts: LUGAR_ABERTO.cais = false)
#   o que vai e o que nao vai para o servidor ......... secao 9: vao o apelido, os pets e o Tamer; nao vao o nome, o e-mail e a fala
#   o apelido: um nome de Digimon e um numero ......... secao 3, tela 2 (e o plano MMO); a troca por uma lista fechada
#   a pergunta da idade, so adultos convidados ........ CN-10 (secao 9) e CN-6
#   o aceite com a versao ............................. secao 3, tela 2; a tabela `consentimentos` (secao 4)
#   os aparelhos, baixar os dados, apagar, sair ....... secao 3, tela 4; "some com tudo em ate 30 dias" e da CN-5 (secao 9)
# EXEMPLO DE LAYOUT, NUNCA DADO: "Agumon#4821", as datas, as horas, os nomes dos aparelhos, a lista de oito Digimon, "versao 2026-11".
# Nenhum numero de jogo novo. Os tamanhos de interface sao PROPOSTO, SEM FONTE.
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "ux-lugares-menus"))
import gerar as G  # noqa: E402
import gerar_movel as M  # noqa: E402

IC = {
    "conta": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    # a marca de cada provedor em uma cor so (a do texto). O G e um desenho simples; o do GitHub e o do lucide, que o app ja usa
    "google": '<path d="M20 12h-8"/><path d="M19 7.5A8.5 8.5 0 1 0 20.5 12"/>',
    "github": ('<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2'
               'c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>'),
    "baixar": '<path d="M12 3v12M7 10l5 5 5-5M4 20h16"/>',
    "sair": '<path d="M9 21H5V3h4M16 17l5-5-5-5M21 12H9"/>',
    "lixo": '<path d="M3 6h18M8 6V4h8v2M6 6l1 15h10l1-15M10 11v6M14 11v6"/>',
    "pc": '<rect x="3" y="4" width="18" height="12" rx="1"/><path d="M8 20h8M12 16v4"/>',
    "celular": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "nuvem": '<path d="M17.5 19H7a5 5 0 1 1 1.6-9.7A6 6 0 0 1 20 11.5 3.8 3.8 0 0 1 17.5 19z"/>',
    "papel": '<path d="M6 2h9l4 4v16H6z"/><path d="M14 2v5h5M9 13h6M9 17h6"/>',
    "sem_fala": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1.2-4.4A8 8 0 1 1 21 12z"/><path d="M4 4l16 16"/>',
    "dado": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h.01M15 15h.01M15 9h.01M9 15h.01"/>',
}


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else G.svg(n, cls)


def _css(h: str) -> str:
    h = h.replace("<title>Lugares da ilha · ", "<title>A conta · ")
    h = h.replace('href="lugares.css"', 'href="../ux-lugares-menus/lugares.css"').replace('href="movel.css"', 'href="../ux-lugares-menus/movel.css"')
    h = h.replace(f'url("{G.A}/', f'url("../{G.A}/' if False else f'url("{G.A}/')
    return h.replace("</head>", '<link rel="stylesheet" href="conta.css">\n</head>')


def cab(titulo: str) -> str:
    return _css(G.cab(titulo))


def cab_cel(titulo: str, topo: int, c360: bool = False) -> str:
    h = _css(M.cab(titulo, c360))
    return h.replace("</head>", f"<style>:root{{--folha-top:{topo}px}}</style></head>")


FIM = G.FIM
APELIDO = ("Agumon", "4821")   # exemplo de layout


# ---------------------------------------------------------------------------------------------------- as caixas: o painel (1920) e a folha (390)
def _cab_parte(titulo: str, icone: str, sub: str, tid: str, voltar: str) -> str:
    v = (f'<button type="button" class="bt-ic ct-voltar" aria-label="{voltar}">{G.svg("seta")}</button>' if voltar else "")
    return (f'<div class="lp-cab ct-cab">{v}{ic(icone)}<span class="lp-tit"><b id="{tid}">{titulo}</b><small>{sub}</small></span>'
            f'<button type="button" class="bt-ic" aria-label="Fechar e voltar ao Pet" aria-keyshortcuts="Escape">{G.svg("x")}</button></div>')


def painel(titulo: str, corpo: str, icone: str = "conta", sub: str = "Ajustes", voltar: str = "Voltar aos Ajustes", x: int = 100, y: int = 128,
           w: int = 460, cls: str = "") -> str:
    """a parte "Conta" dos Ajustes: a mesma caixa dos Ajustes de hoje (TelaConfig.tsx), com o voltar, como Visual, Fala e Registro"""
    return (f'<section class="caixa lp painel-lugar {cls}" style="left:{x}px;top:{y}px;width:{w}px" aria-labelledby="ct-tit">'
            f'{_cab_parte(titulo, icone, sub, "ct-tit", voltar)}<div class="lp-corpo ct-corpo">{corpo}</div></section>')


def folha(titulo: str, corpo: str, icone: str = "conta", sub: str = "Ajustes", voltar: str = "Voltar aos Ajustes") -> str:
    return (f'<section class="caixa folha ct-folha painel-lugar" role="dialog" aria-modal="true" aria-labelledby="ct-tit">'
            f'<span class="alca" aria-hidden="true"></span>{_cab_parte(titulo, icone, sub, "ct-tit", voltar)}'
            f'<div class="lp-corpo ct-corpo">{corpo}</div></section>')


def tela(titulo: str, caixa: str, notas: str = "", leque: bool = True) -> str:
    """o desktop: a ilha viva, a HUD de sempre e a caixa no lugar dos Ajustes (a camera nao se mexe: a conta nao e lugar)"""
    return (cab(titulo) + G.mundo("ilha", G.pet(1160, 400, "parado")) + G.topo(leque=leque) + G.trilho("pet") + G.pilha() + G.dock() + G.minimapa()
            + caixa + notas + FIM)


def tela_cel(titulo: str, caixa: str, topo: int, notas: str = "", c360: bool = False) -> str:
    return (cab_cel(titulo, topo, c360) + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna() + caixa + notas + FIM)


def aceite(marcado: bool, txt: str, sub: str = "") -> str:
    s = f"<small>{sub}</small>" if sub else ""
    return (f'<button type="button" class="ct-aceite" role="checkbox" aria-checked="{"true" if marcado else "false"}">'
            f'<span class="ct-caixa" aria-hidden="true">{G.svg("check")}</span><span>{txt}{s}</span></button>')


# ---------------------------------------------------------------------------------------------------- os corpos
def corpo_ajustes(com_conta: bool = False) -> str:
    """os Ajustes de hoje (a lista de TelaConfig.tsx, encurtada) com a linha nova no topo"""
    def aj(i: str, tit: str, res: str, dir_: str = "", cls: str = "") -> str:
        d = dir_ or G.svg("seta")
        return f'<button type="button" class="aj {cls}" aria-label="{tit}: {res}">{ic(i)}<span><b>{tit}</b></span>{d}{G.b(res)}</button>'
    sw = lambda on: f'<span class="interruptor{" on" if on else ""}" role="switch" aria-checked="{"true" if on else "false"}"></span>'
    if com_conta:
        conta = (f'<button type="button" class="aj foco" aria-label="Conta: {APELIDO[0]}#{APELIDO[1]}, 2 aparelhos">{ic("conta")}'
                 f'<span><b>Conta</b><small>{APELIDO[0]}#{APELIDO[1]}</small></span>{G.svg("seta")}</button>')
    else:
        conta = (f'<button type="button" class="aj novo foco" aria-label="Conta: sem conta, o pet fica neste aparelho">{ic("conta")}'
                 f'<span><b>Conta</b><small>sem conta</small></span>{G.svg("seta")}</button>')
    return f'''
{conta}
{aj("olho", "Visual", "pele, tema do habitat, mapa e câmera")}
{aj("dica", "Dicas", "o Professor Agumon explica cada coisa nova, uma vez", sw(False))}
{aj("estado", "Detalhes do pet", "os painéis Estado atual, Evolução e Últimas ações", sw(True))}
{aj("conversar", "Fala", "modo frases prontas")}
{aj("som", "Som", "a luta, o treino, os menus e a música", sw(True))}
{aj("registro", "Registro", "semente, eventos, verificar replay, exportar")}
{aj("info", "Sobre", "versão, créditos e procedência")}'''


def corpo_entrar() -> str:
    return f'''
<p class="ct-chamada">O mesmo pet em outro aparelho</p>
<div>
  <span class="rot">O que vai para o servidor</span>
  <ul class="ct-vai" style="margin-top:6px">
    <li>{ic("pet")}Os pets e o Tamer<span class="etq ok">vai</span></li>
    <li>{ic("conta")}Um apelido<span class="etq ok">vai</span></li>
    <li class="nao">{ic("sem_fala")}Nome, e-mail e conversa<span class="etq">não vão</span></li>
  </ul>
</div>
<div class="ct-prov" role="group" aria-label="Entrar">
  <button type="button" class="bt">{ic("google")}Entrar com Google{G.svg("seta", "ic seta")}</button>
  <button type="button" class="bt">{ic("github")}Entrar com GitHub{G.svg("seta", "ic seta")}</button>
</div>
<div class="ct-rodape">
  <button type="button" class="bt">Agora não{G.b("Sem conta, nada muda: o pet fica neste aparelho.")}</button>
  <button type="button" class="ct-link">Termos</button><button type="button" class="ct-link">Privacidade</button>
</div>
<p class="sec linha">{ic("info", "ic ic-p")}Sem senha. Por enquanto, só convidados com 18 anos ou mais.</p>'''


def passos(agora: int) -> str:
    nomes = ["Jogo", "Google", "Conta"]
    li = "".join(f'<li class="{"feito" if i < agora else "agora" if i == agora else ""}"'
                 f'{" aria-current=step" if i == agora else ""}>{n}</li>' for i, n in enumerate(nomes))
    return f'<ol class="ct-passos" aria-label="Passo {agora + 1} de 3">{li}</ol>'


def corpo_indo() -> str:
    return f'''
{passos(1)}
<p class="ct-chamada" role="status">Abrindo o Google</p>
<p class="sec">Escolha a conta na página do Google. O jogo espera aqui.</p>
<div class="ct-bts"><button type="button" class="bt">Cancelar</button></div>'''


def corpo_voltando() -> str:
    return f'''
{passos(2)}
<p class="ct-chamada" role="status">Conferindo a conta</p>
<p class="sec">Você volta para onde estava.</p>
<div class="ct-bts"><button type="button" class="bt" disabled>Cancelar</button></div>'''


def corpo_falhou() -> str:
    return f'''
<div class="destaque perigo" role="alert"><span class="rot">Não entrou</span><b class="grande">Não deu para entrar</b>
  <p>O jogo continua neste aparelho.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Tentar de novo</button><button type="button" class="bt">Agora não</button></div>'''


def corpo_fora() -> str:
    return f'''
<div class="destaque" role="alert"><span class="rot">Só convidados</span><b class="grande">Esta conta não está na lista</b>
  <p>Nada foi guardado. O jogo continua neste aparelho.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Usar outra conta</button><button type="button" class="bt">Agora não</button></div>'''


def corpo_menor() -> str:
    return f'''
<div class="destaque" role="alert"><span class="rot">Idade</span><b class="grande">A conta ainda é só para adultos</b>
  <p>Nada foi guardado. O jogo continua neste aparelho, sem conta.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Voltar ao pet</button></div>'''


def cartao_apelido(botao: str, sub: str) -> str:
    return (f'<div class="cartao ct-apelido"><span class="palquinho">{G.spr(APELIDO[0], .8)}</span>'
            f'<span><b>{APELIDO[0]}<i>#{APELIDO[1]}</i></b><small>{sub}</small></span>{botao}</div>')


def corpo_primeiro(pronto: bool = True) -> str:
    dis = "" if pronto else " disabled"
    return f'''
<div><span class="rot">Apelido</span>
  <div style="margin-top:6px">{cartao_apelido(f'<button type="button" class="bt">{ic("replay")}Trocar</button>', "É como os outros veem você.")}</div></div>
<div><span class="rot" id="ct-idade">Idade</span>
  <div class="ct-idade" role="radiogroup" aria-labelledby="ct-idade" style="margin-top:6px">
    <button type="button" class="rival" role="radio" aria-checked="{"true" if pronto else "false"}"><span class="radio"></span><b>18 anos ou mais</b></button>
    <button type="button" class="rival" role="radio" aria-checked="false"><span class="radio"></span><b>Menos de 18</b></button>
  </div></div>
{aceite(pronto, "Li e aceito os <u>Termos</u> e a <u>Privacidade</u>", "versão 2026-11")}
<div class="ct-bts"><button type="button" class="bt acao grande"{dis}>Criar a conta</button><button type="button" class="bt">Cancelar</button></div>'''


NOMES = ["Agumon", "Gabumon", "Biyomon", "Tentomon", "Palmon", "Gomamon", "Patamon", "Guilmon"]   # exemplo: a lista fechada e a UX-CN-4


def corpo_apelido() -> str:
    chips = "".join(f'<button type="button" class="filtro" role="radio" aria-checked="{"true" if n == APELIDO[0] else "false"}" '
                    f'aria-pressed="{"true" if n == APELIDO[0] else "false"}">{n}</button>' for n in NOMES)
    return f'''
{cartao_apelido(f'<button type="button" class="bt" aria-label="Sortear outro número">{ic("dado")}Número</button>', "O número é sorteado.")}
<div><span class="rot" id="ct-nomes">O Digimon do apelido</span>
  <div class="ct-nomes" role="radiogroup" aria-labelledby="ct-nomes" style="margin-top:6px">{chips}</div></div>
<div class="ct-bts"><button type="button" class="bt acao">Usar este</button><button type="button" class="bt">Voltar</button></div>'''


def corpo_perfil() -> str:
    return f'''
{cartao_apelido(f'<button type="button" class="bt">{ic("replay")}Trocar</button>', "Google · desde 12/11/2026")}
<div><span class="rot">Aparelhos</span>
  <ul class="ct-ap" style="margin-top:6px">
    <li class="med-li">{ic("pc")}<span><b>Este PC</b><small>agora</small></span><span class="etq aqui">aqui</span></li>
    <li class="med-li">{ic("celular")}<span><b>Celular</b><small>ontem, 21:10</small></span><button type="button" class="bt">Desconectar</button></li>
  </ul></div>
<div style="display:flex;flex-direction:column;gap:4px"><span class="rot" style="margin-bottom:2px">Seus dados</span>
  <button type="button" class="fechado">{ic("baixar")}<span>Baixar meus dados</span>{G.svg("seta")}</button>
  <button type="button" class="fechado">{ic("papel")}<span>Termos e Privacidade</span><span class="sec">aceitos em 12/11</span>{G.svg("seta")}</button>
</div>
<div class="ct-bts"><button type="button" class="bt">{ic("sair")}Sair</button>
  <button type="button" class="bt perigo" style="margin-left:auto">{ic("lixo")}Apagar a conta</button></div>'''


def corpo_apagar(marcado: bool = False) -> str:
    dis = "" if marcado else " disabled"
    return f'''
<div class="destaque perigo"><span class="rot">Sem volta</span><b class="grande">Apagar {APELIDO[0]}#{APELIDO[1]}</b>
  <ul class="ct-some">
    <li>{G.svg("x")}Somem do servidor o apelido, os pets e os aparelhos.</li>
    <li>{ic("relogio")}Tudo é apagado em até 30 dias.</li>
    <li class="fica">{G.svg("check")}O pet deste aparelho continua aqui.</li>
  </ul></div>
<button type="button" class="fechado">{ic("baixar")}<span>Baixar meus dados antes</span>{G.svg("seta")}</button>
{aceite(marcado, "Entendi que não volta")}
<div class="ct-bts"><button type="button" class="bt acao">Manter a conta</button>
  <button type="button" class="bt perigo"{dis}>{ic("lixo")}Apagar para sempre</button></div>'''


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def ajustes_conta_1920() -> str:
    pn = (f'<section class="caixa lp painel-lugar" style="left:100px;top:128px;width:460px" aria-labelledby="aj-tit">'
          f'<div class="lp-cab" style="padding-bottom:8px">{G.svg("ajustes")}<span class="lp-tit"><b id="aj-tit">Ajustes</b></span>'
          f'<button type="button" class="bt-ic" aria-label="Fechar os Ajustes" aria-keyshortcuts="Escape">{G.svg("x")}</button></div>'
          f'<div class="lp-corpo" style="gap:6px;border-top:1px solid var(--hx-borda)">{corpo_ajustes()}</div></section>')
    return tela("Ajustes com a linha Conta", pn,
                G.nota("1 · a porta da conta: uma linha nova no topo dos Ajustes (CN-1: o jogo abre direto na ilha, a conta é escolha)", 580, 190, 300)
                + G.nota("sem conta: tracejada, como toda linha nova, e diz 'sem conta'. Nada pisca nem insiste", 580, 250, 280)
                + G.nota("o cais continua trancado (é do MMO, do nível 10). Quando abrir, leva a esta mesma tela (UX-CN-2)", 580, 310, 280)
                + G.nota("a lista dos Ajustes está encurtada aqui; a de verdade é a do TelaConfig.tsx", 580, 520, 260))


def entrar_1920() -> str:
    return tela("Entrar", painel("Conta", corpo_entrar()),
                G.nota("2 · Entrar (tela 1 do plano). A conta é uma parte dos Ajustes: a mesma caixa, com o voltar", 580, 136, 300)
                + G.nota("o que vai para o servidor, em três linhas, ANTES dos botões (plano, seção 9). Cada linha diz 'vai' ou 'não vão' em texto, não só em cor", 580, 215, 300)
                + G.nota("os dois provedores com o mesmo peso (CN-2). Sem campo de e-mail, sem senha, sem 'esqueci a senha'. A marca em uma cor só: a regra de marca do Google não foi conferida (UX-CN-3)", 580, 345, 300)
                + G.nota("'Agora não' fecha e não pergunta de novo. Sem culpa e sem contagem (guia, princípio 5)", 580, 470, 280)
                + G.nota("só convidados adultos, dito aqui, antes de sair para o Google (CN-6 e CN-10)", 580, 530, 280)
                + G.contagem(420, 106))


def estados_1920() -> str:
    def est(i: int, rot: str, titulo: str, corpo: str) -> str:
        x = 40 + i * 374
        return (G.nota(rot, x, 122, 340)
                + painel(titulo, corpo, voltar="", x=x, y=150, w=350, cls="ct-estado"))
    return (cab("Entrar: os estados") + G.mundo("ilha", "") + '<div class="veu"></div>'
            + f'<span class="caixa titulo-pr" style="position:absolute;left:40px;top:40px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">Entrar: os estados</span>'
            + est(0, "3a · saiu para o Google (o jogo fica na aba; a ida é na mesma aba ou numa janela: decisão da CN2)", "Conta", corpo_indo())
            + est(1, "3b · voltou do Google: o servidor confere e devolve o jogador ao lugar em que estava (plano, seção 3: as rotas)", "Conta", corpo_voltando())
            + est(2, "3c · a ida falhou, foi cancelada ou o servidor está fora", "Conta", corpo_falhou())
            + est(3, "3d · a conta do provedor não está na lista de convidados (CN-6)", "Conta", corpo_fora())
            + est(4, "3e · respondeu 'Menos de 18' no primeiro acesso (CN-10)", "Conta", corpo_menor())
            + G.nota("os passos são três pontos parados; nada gira nem pisca (guia, seção 11). O estado é dito em texto, com role=status ou alert", 40, 470, 340)
            + G.nota("em todo erro: o que aconteceu, que nada foi guardado e que o jogo continua. Um botão principal por caixa", 788, 470, 340)
            + G.nota("no celular, cada estado é a mesma folha da tela Entrar", 1536, 470, 300)
            + FIM)


def primeiro_1920() -> str:
    return tela("Primeiro acesso", painel("Primeiro acesso", corpo_primeiro(), sub="Conta", voltar=""),
                G.nota("4 · Primeiro acesso (tela 2): é o cadastro inteiro. Três coisas numa caixa só: o apelido, a idade e o aceite", 580, 136, 300)
                + G.nota("o apelido já vem pronto: um nome de Digimon e um número (plano MMO). 'Trocar' abre a lista fechada (quadro 5). Ninguém digita nome: sem nome real e sem ofensa", 580, 205, 300)
                + G.nota("a idade é uma pergunta de duas respostas, sem data de nascimento (o mínimo de dado: CN-10)", 580, 330, 280)
                + G.nota("o aceite mostra a versão dos termos (a tabela consentimentos). 'Criar a conta' fica apagado até a idade e o aceite", 580, 400, 300)
                + G.nota("'Cancelar' sai sem criar nada: o servidor não guarda a conta pela metade", 580, 480, 280)
                + G.contagem(420, 106))


def apelido_1920() -> str:
    return tela("Trocar o apelido", painel("Apelido", corpo_apelido(), sub="Primeiro acesso", voltar="Voltar ao primeiro acesso"),
                G.nota("5 · a troca do apelido: o Digimon por uma lista fechada, o número por sorteio", 580, 136, 300)
                + G.nota("os oito nomes são EXEMPLO. Qual lista usar é a UX-CN-4 (recomendo os Rookies do Catálogo, iguais para todos)", 580, 280, 300)
                + G.nota("os nomes são os do Digimon na tela, como em todo o jogo", 580, 360, 260))


def perfil_1920() -> str:
    return tela("Conta: o perfil", painel("Conta", corpo_perfil()),
                G.nota("6 · Conta, já com a conta (tela 4, a parte da CN2): o apelido, os aparelhos, os dados, sair e apagar", 580, 136, 300)
                + G.nota("o provedor aparece só pelo nome ('Google'); o e-mail não é guardado e não aparece (plano, seção 9)", 580, 200, 280)
                + G.nota("cada aparelho: um nome e a última vez. O daqui diz 'aqui' e não tem Desconectar", 580, 290, 280)
                + G.nota("baixar os dados e apagar a conta ficam aqui, sem pedido por e-mail (plano, seção 9)", 580, 400, 280)
                + G.nota("'Apagar a conta' é tracejado e na cor do perigo, longe do 'Sair'", 580, 500, 260)
                + G.nota("as cópias do save, o ícone de sincronização e 'levar o pet para a conta' são da CN3 e não estão nesta prancha", 580, 560, 300)
                + G.contagem(420, 106))


def apagar_1920() -> str:
    return tela("Apagar a conta", painel("Apagar a conta", corpo_apagar(), icone="lixo", sub="Conta", voltar="Voltar à conta"),
                G.nota("7 · Apagar a conta: o que some, em quanto tempo e o que fica (CN-5: até 30 dias, com as cópias)", 580, 136, 300)
                + G.nota("o botão principal é 'Manter a conta'. 'Apagar para sempre' fica apagado até marcar 'Entendi que não volta'", 580, 420, 300)
                + G.nota("'Baixar meus dados antes' no caminho, sem obrigar", 580, 345, 260))


# ---------------------------------------------------------------------------------------------------- as telas a 390 (e uma a 360)
def ajustes_conta_390() -> str:
    return tela_cel("Ajustes com a linha Conta · 390", G.folha("ajustes", "", corpo_ajustes()).replace('class="caixa folha', 'class="caixa folha ct-folha'), 300,
                    M.nota("a linha Conta no topo da folha dos Ajustes (o leque do retrato › Configurações)", 14, 250))


def entrar_390() -> str:
    return tela_cel("Entrar · 390", folha("Conta", corpo_entrar()), 318,
                    M.nota("a mesma folha dos Ajustes, mais alta; a ilha e o pet continuam em cima", 14, 240))


def falhou_390() -> str:
    return tela_cel("Entrar: não deu · 390", folha("Conta", corpo_falhou(), voltar=""), 560,
                    M.nota("os estados usam a folha baixa: o pet fica à vista", 14, 480))


def primeiro_390(c360: bool = False) -> str:
    return tela_cel("Primeiro acesso · " + ("360" if c360 else "390"), folha("Primeiro acesso", corpo_primeiro(), sub="Conta", voltar=""),
                    430 if not c360 else 390, M.nota("o cadastro inteiro numa folha, sem rolar", 14, 330), c360)


def apelido_390() -> str:
    return tela_cel("Trocar o apelido · 390", folha("Apelido", corpo_apelido(), sub="Primeiro acesso", voltar="Voltar ao primeiro acesso"), 420)


def perfil_390() -> str:
    return tela_cel("Conta: o perfil · 390", folha("Conta", corpo_perfil()), 370)


def apagar_390() -> str:
    return tela_cel("Apagar a conta · 390", folha("Apagar a conta", corpo_apagar(True), icone="lixo", sub="Conta", voltar="Voltar à conta"), 430,
                    M.nota("aqui com o 'Entendi' marcado: o Apagar acende", 14, 350))


TELAS = {
    "ajustes_conta_1920": ajustes_conta_1920, "entrar_1920": entrar_1920, "estados_1920": estados_1920, "primeiro_1920": primeiro_1920,
    "apelido_1920": apelido_1920, "perfil_1920": perfil_1920, "apagar_1920": apagar_1920,
    "ajustes_conta_390": ajustes_conta_390, "entrar_390": entrar_390, "falhou_390": falhou_390, "primeiro_390": primeiro_390,
    "primeiro_360": lambda: primeiro_390(True), "apelido_390": apelido_390, "perfil_390": perfil_390, "apagar_390": apagar_390,
}


def escrever() -> None:
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")


if __name__ == "__main__":
    escrever()
