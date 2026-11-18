# Gera a prancha "o cais e a semana" (docs/PLANO_UX_CAIS.md; a etapa MMO5 do docs/PLANO_V3_MMO.md). So desenho; nenhum codigo do jogo.
# Usa os ajudantes da prancha dos lugares (../ux-lugares-menus/gerar.py e gerar_movel.py) e os da conta (../ux-conta/gerar.py: o painel, a
# folha e os icones); o que e novo esta em cais.css. A pele vem de ?pele=vidro|xcom; no desktop ?sem tira as notas, e no celular as notas
# so aparecem com ?notas.
# Uso (da raiz): python docs/pranchas/ux-cais/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# DE ONDE VEM CADA TEXTO E CADA REGRA:
#   uma tabela por estagio (Rookie, Champion, Ultimate, Mega) ...... MMO-9; ESTAGIOS (servidor_web/src/envio/semanas.ts)
#   a linha: posicao, apelido, pontos, rivais vencidos, lutas ...... GET /semanas/:semana/tabelas (semanas.ts)
#   o desempate: pontos, rivais vencidos, menos lutas, quem antes .. MMO-9; web/app/src/ranking/pontos.ts
#   a semana: de segunda a domingo, horario de Brasilia ............ MMO-9; GET /semanas (atual, fecha_em, congela_em, fechadas)
#   a tabela congela 1 h depois do fim da semana ................... FOLGA_DO_FECHAMENTO_MS (PROPOSTA, D-CONTA-118)
#   a resposta leva ate 100 linhas, e a de quem pede vem sempre .... LINHAS_DA_TABELA (PROPOSTO); o campo "voce"
#   as tabelas pedem a sessao; o segredo publicado, nao ............ o 401 de /tabelas; GET /semanas/:semana/segredo (D-CONTA-120)
#   o segredo sai quando a semana congela, e como conferir ......... MMO-14; o campo "como" de /segredo
#   as 12 ultimas semanas fechadas ................................. SEMANAS_LISTADAS (PROPOSTO)
#   o cais abre no nivel 10, o primeiro Mega (no beta, 3 medalhas) . MMO-13; BT0-1; DIGILAB_MARCO_RANQUEADA
#   o apelido: um nome de Digimon e um numero ...................... CN2 (docs/TAREFA_V3_CONTA.md)
#   o cais trancado e o cartao de destrave ......................... a prancha dos lugares (lugar_trancado, cartao_destrave; plano 3.4 e 4.1)
# EXEMPLO DE LAYOUT, NUNCA DADO: os apelidos, os pontos, as posicoes, "14 Tamers", as datas, as horas e o segredo.
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

IC = {
    "ancora": '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M8 11h8M4 14a8 8 0 0 0 16 0"/>',
    "trofeu": '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3"/>',
    "sem_rede": '<path d="M2 8.5a15 15 0 0 1 20 0M5.5 12a10 10 0 0 1 13 0M9 15.5a5 5 0 0 1 6 0M12 19h.01"/><path d="M3 3l18 18"/>',
    "chave": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M14 9l2 2"/>',
    "esq": '<path d="M15 5l-7 7 7 7"/>',
    "dir": '<path d="M9 5l7 7-7 7"/>',
}
C.IC.update(IC)   # o painel e a folha da conta desenham o icone do cabecalho pelo ic() de la


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else C.ic(n, cls)


def _css(h: str) -> str:
    return (h.replace("<title>A conta · ", "<title>O cais · ").replace("<title>Lugares da ilha · ", "<title>O cais · ")
            .replace('href="conta.css"', 'href="../ux-conta/conta.css"')
            .replace("</head>", '<link rel="stylesheet" href="cais.css">\n</head>'))


def cab(titulo: str) -> str:
    return _css(C.cab(titulo))


def cab_cel(titulo: str, topo: int, c360: bool = False) -> str:
    return _css(C.cab_cel(titulo, topo, c360))


FIM = G.FIM
VOCE = "Agumon 4821"
# (posicao, apelido, pontos, rivais vencidos, lutas usadas). EXEMPLO DE LAYOUT, NUNCA DADO.
CHAMPION = [(1, "Gabumon 0317", 260, 8, 31), (2, "Palmon 7740", 240, 8, 28), (3, "Tentomon 1206", 240, 7, 35), (4, "Patamon 5589", 205, 7, 40),
            (5, "Biyomon 9034", 180, 6, 22), (6, "Gomamon 2251", 180, 6, 27), (7, "Guilmon 6612", 150, 5, 19), (8, "Gabumon 4408", 140, 5, 30),
            (9, "Palmon 0093", 120, 4, 18), (10, "Tentomon 8875", 100, 4, 16), (11, "Biyomon 3320", 90, 3, 12), (12, VOCE, 80, 4, 23),
            (13, "Patamon 1177", 40, 2, 9), (14, "Gomamon 6046", 20, 1, 4)]
FECHADA = [(1, "Palmon 7740", 310, 8, 44), (2, "Gabumon 0317", 290, 8, 39), (3, "Tentomon 1206", 250, 7, 41), (4, VOCE, 140, 5, 33),
           (5, "Guilmon 6612", 130, 5, 21), (6, "Biyomon 9034", 120, 4, 26), (7, "Patamon 5589", 80, 3, 30), (8, "Gomamon 2251", 60, 3, 11),
           (9, "Gabumon 4408", 20, 1, 6)]
ESTAGIOS = [("Rookie", 6), ("Champion", 14), ("Ultimate", 3), ("Mega", 0)]   # o total de cada tabela (o campo "total")
ESTAGIOS_FECHADA = [("Rookie", 4), ("Champion", 9), ("Ultimate", 2), ("Mega", 0)]
ESTAGIOS_FORA = [("Rookie", 3), ("Champion", 14), ("Ultimate", 3), ("Mega", 0)]
SEGREDO = "9f2c41d07ab35e186c0d74f2a1b98e5530c7d6124fa08b93e1d5a7c60b2f4e81"   # exemplo: 32 bytes em hexadecimal


# ---------------------------------------------------------------------------------------------------- as pecas
def semana(texto: str = "16 a 22 de novembro", estado: str = "aberta", sub: str = "Fecha domingo, 23:59 · faltam 2 d 4 h", proxima: bool = False) -> str:
    """o cabecalho da semana: as datas, o estado em texto e as setas para as semanas fechadas (ate 12). A seta da direita apaga na atual"""
    cls = {"aberta": "", "fechando": " alerta", "fechada": " ok"}[estado]
    dis = "" if proxima else " disabled"
    return (f'<div class="ca-sem" role="group" aria-label="Semana de {texto}, {estado}">'
            f'<button type="button" class="bt-ic" aria-label="Semana anterior">{ic("esq")}</button>'
            f'<span class="ca-sem-txt"><b>{texto}</b><span class="etq{cls}">{estado}</span><small>{sub}</small></span>'
            f'<button type="button" class="bt-ic" aria-label="Semana seguinte"{dis}>{ic("dir")}</button></div>')


def estagios(atual: str = "Champion", seu: str = "Champion", curto: bool = False, totais: list | None = None) -> str:
    """uma tabela por estagio (MMO-9). A do pet de agora leva "seu pet" em texto; a contagem e o campo "total" da resposta"""
    def um(n: str, t: int) -> str:
        sel = "true" if n == atual else "false"
        meu = ", o estágio do seu pet" if n == seu else ""
        marca = '<i class="ca-meu" aria-hidden="true"></i>' if n == seu else ""
        return (f'<button type="button" class="filtro" role="radio" aria-checked="{sel}" aria-pressed="{sel}" aria-label="{n}, {t} Tamers{meu}">'
                f'{marca}{n}<small>{t}</small></button>')
    leg = "" if curto else f'<span class="ca-leg"><i class="ca-meu" aria-hidden="true"></i>o estágio do seu pet</span>'
    return f'<div class="ca-est" role="radiogroup" aria-label="Estágio da tabela">{"".join(um(*e) for e in (totais or ESTAGIOS))}</div>{leg}'


def linha(l: tuple, curto: bool = False) -> str:
    p, nome, pts, riv, lut = l
    eu = nome == VOCE
    etq = '<span class="etq aqui">você</span>' if eu else ""
    return (f'<tr class="{"ca-eu" if eu else ""}"{" aria-current=&quot;true&quot;" if eu else ""}><td class="ca-pos">{p}º</td>'
            f'<th scope="row"><span>{nome}</span>{etq}</th><td class="ca-pts">{pts}</td><td>{riv}</td>' + ("" if curto else f'<td>{lut}</td>') + '</tr>')


def tabela(linhas: list, n: int = 8, total: int = 14, estagio: str = "Champion", curto: bool = False, fechada: bool = False) -> str:
    """as n primeiras e, se quem pede esta abaixo delas, a linha dele presa no fim (o campo "voce"). "Ver todas" abre as outras (ate 100)"""
    topo = linhas[:n]
    corpo = "".join(linha(l, curto) for l in topo)
    eu = next((l for l in linhas if l[1] == VOCE), None)
    cols = 4 if curto else 5
    if eu and eu not in topo:
        corpo += f'<tr class="ca-salto" aria-hidden="true"><td colspan="{cols}">· · ·</td></tr>' + linha(eu, curto)
    cab_l = "" if curto else '<th scope="col" title="Lutas usadas">Lutas</th>'
    resto = (f'<button type="button" class="bt ca-mais" aria-expanded="false">Ver todas as {total}</button>' if total > n else "")
    return (f'<table class="ca-tab"><caption class="so-leitor">Tabela {estagio}, {"final" if fechada else "parcial"}: {total} Tamers</caption>'
            f'<thead><tr><th scope="col">#</th><th scope="col">Tamer</th><th scope="col">Pontos</th>'
            f'<th scope="col" title="Rivais diferentes vencidos">Rivais</th>{cab_l}</tr></thead><tbody>{corpo}</tbody></table>{resto}')


COMO = ("Só a vitória ranqueada conferida pelo servidor conta. No empate de pontos, fica na frente quem venceu mais rivais diferentes; "
        "depois, quem usou menos lutas; depois, quem chegou antes aos pontos.")


def como(aberto: bool = False) -> str:
    return G.como(COMO, aberto).replace("Como funciona", "Como a tabela conta")


def corpo_semana(curto: bool = False) -> str:
    return f'''
{semana()}
{estagios(curto=curto)}
{tabela(CHAMPION, 6 if curto else 8, curto=curto)}
<p class="ca-parcial">{ic("info", "ic ic-p")}<span>Parcial: entram só as lutas que o servidor já conferiu.</span></p>
{"" if curto else como()}
<div class="ct-bts"><button type="button" class="bt acao">{G.svg("lutar")}Ir para a Arena</button><button type="button" class="bt">{ic("replay")}Atualizar</button></div>'''


def corpo_fechada(curto: bool = False) -> str:
    return f'''
{semana("9 a 15 de novembro", "fechada", "Fechou em 16/11, à 1h", proxima=True)}
<div class="destaque ca-final" role="status"><span class="rot">O seu resultado · Champion</span><b class="grande">4º lugar <small>de 9</small></b>
  <p>140 pontos · 5 rivais vencidos · 33 lutas</p></div>
{estagios(curto=True, totais=ESTAGIOS_FECHADA)}
{tabela(FECHADA, 5 if curto else 6, total=9, curto=curto, fechada=True)}
<button type="button" class="fechado" aria-expanded="false">{ic("chave")}<span>Conferir a semana</span><span class="sec">segredo publicado</span>{G.svg("seta")}</button>'''


def corpo_segredo() -> str:
    return f'''
{semana("9 a 15 de novembro", "fechada", "Fechou em 16/11, à 1h", proxima=True)}
<div><span class="rot">O segredo da semana</span>
  <div class="ca-seg"><code>{SEGREDO}</code><button type="button" class="bt" aria-label="Copiar o segredo">{G.svg("copiar")}Copiar</button></div></div>
<p class="sec ca-txt">Com ele, qualquer pessoa refaz a semente de cada luta e confere que o servidor não escolheu a sorte de ninguém.</p>
<div><span class="rot">Como conferir</span>
  <p class="ca-txt">A semente da luta são os 4 primeiros bytes de HMAC-SHA256 do segredo com "conta|número da luta".</p></div>
<p class="sec ca-txt">O segredo só sai depois que a semana congela. O da semana aberta fica no servidor.</p>
<div class="ct-bts"><button type="button" class="bt">Voltar à tabela</button></div>'''


# ---- os estados (a caixa pequena, como os estados da conta)
def est_buscando() -> str:
    return f'''
{semana()}
<p class="ct-chamada" role="status">Buscando a tabela</p>
<p class="sec">A semana e os estágios aparecem assim que a resposta chegar.</p>'''


def est_sem_rede() -> str:
    return f'''
<div class="destaque" role="alert"><span class="rot">Sem resposta</span><b class="grande">A tabela não veio</b>
  <p>Os seus pontos continuam guardados no servidor.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Tentar de novo</button><button type="button" class="bt">Voltar à ilha</button></div>'''


def est_sem_conta() -> str:
    return f'''
<div class="destaque" role="status"><span class="rot">Só com a conta</span><b class="grande">As tabelas pedem a conta</b>
  <p>Elas mostram só os apelidos. Sem conta, nada muda no jogo.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">{ic("conta")}Entrar</button><button type="button" class="bt">Agora não</button></div>'''


def est_vazia() -> str:
    return f'''
{semana()}
{estagios("Mega", curto=True)}
<div class="ca-vazia" role="status"><b>Ninguém pontuou em Mega nesta semana</b><span>A tabela nasce com a primeira vitória conferida.</span></div>'''


def est_fora() -> str:
    return f'''
{semana()}
{estagios("Rookie", curto=True, totais=ESTAGIOS_FORA)}
{tabela([(1, "Guilmon 6612", 30, 3, 9), (2, "Palmon 0093", 20, 2, 5), (3, "Biyomon 3320", 10, 1, 2)], 3, total=3, estagio="Rookie")}
<p class="ca-parcial">{ic("info", "ic ic-p")}<span>Você não lutou com um Rookie nesta semana.</span></p>'''


def est_fechando() -> str:
    return f'''
{semana("16 a 22 de novembro", "fechando", "A tabela congela à 1h de segunda")}
<div class="destaque" role="status"><span class="rot">A semana acabou</span><b class="grande">Conferindo as últimas lutas</b>
  <p>A luta feita até 23:59 e ainda não enviada pode chegar até a 1h. Depois disso, vale como derrota.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Ver a tabela parcial</button></div>'''


# ---------------------------------------------------------------------------------------------------- as telas a 1920
CAIS_XY = (260, 330)   # onde o cais fica no fundo: so de layout (a captura do fundo e de antes do cais 3D)


def painel_cais(corpo: str, x: int = 660, y: int = 84, w: int = 560, sub: str = "ranking da semana", cls: str = "") -> str:
    return C.painel("Cais", corpo, icone="ancora", sub=sub, voltar="", x=x, y=y, w=w, cls="ca-painel " + cls)


def cais_1920() -> str:
    px, py = G.tela(*CAIS_XY, "ilha")
    return (cab("Cais · a semana") + G.mundo("ilha", G.pet(1500, 640, "parado")) + G.topo(agora=False) + G.trilho("pet") + G.minimapa()
            + f'<span class="caixa placa-lugar" style="left:{px - 40:.0f}px;top:{py - 62:.0f}px">{ic("ancora")}Cais</span>'
            + painel_cais(corpo_semana())
            + G.contagem(1232, 62)
            + G.nota("1 · o cais abre a semana: as datas, o estado em texto ('aberta') e quanto falta. As setas levam às semanas já fechadas (até 12)", 1300, 96, 300)
            + G.nota("uma tabela por estágio (MMO-9). A do pet de agora abre primeiro e leva a marca; o número é quantos Tamers pontuaram", 1300, 196, 300)
            + G.nota("as 8 primeiras e a sua linha, sempre: se você está abaixo, ela fica presa no fim, com 'você' em texto (UX-CA-3)", 1300, 300, 300)
            + G.nota("as colunas são as do desempate, na ordem: pontos, rivais diferentes vencidos, lutas usadas", 1300, 400, 300)
            + G.nota("'parcial' em texto: a luta ainda não conferida não aparece. A prévia do jogo nunca entra aqui (UX-LR-3)", 1300, 490, 300)
            + G.nota("um botão principal: 'Ir para a Arena'. O cais não tem botão de luta (UX-LR-1)", 1300, 590, 300)
            + G.nota("os apelidos, os pontos e as datas são EXEMPLO. O fundo é de antes do cais 3D: o lugar na ilha é só de layout", 1300, 670, 300)
            + FIM)


def _grade(titulo: str, itens: list, w: int = 460, passo_y: int = 420) -> str:
    def est(i: int, rot: str, corpo: str) -> str:
        x = 40 + (i % 3) * 620
        y = 96 + (i // 3) * passo_y
        return G.nota(rot, x, y, 560) + painel_cais(corpo, x, y + 44, w, cls="ct-estado ca-estado")
    return (cab(titulo) + G.mundo("ilha", "") + '<div class="veu"></div>'
            + f'<span class="caixa titulo-pr" style="position:absolute;left:40px;top:36px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">{titulo}</span>'
            + "".join(est(i, r, c) for i, (r, c) in enumerate(itens)))


def estados_1920() -> str:
    return (_grade("O cais: os estados", [
        ("2a · abriu o cais: a semana aparece na hora (o jogo sabe a data) e a tabela chega depois. Nada gira", est_buscando()),
        ("2b · o servidor não respondeu: diz o que houve e que os pontos não se perdem", est_sem_rede()),
        ("2c · sem conta (401): as tabelas pedem a sessão. Leva à tela Entrar; 'Agora não' fecha e não insiste (UX-CA-4)", est_sem_conta()),
        ("2d · a tabela sem ninguém: uma frase, sem tabela vazia desenhada", est_vazia()),
        ("2e · a tabela de um estágio em que você não lutou: as linhas dos outros e uma frase no lugar da sua", est_fora()),
        ("2f · entre domingo 23:59 e segunda 1h: a semana acabou, mas a tabela ainda aceita a luta já feita (a folga de 1 h, PROPOSTA)", est_fechando()),
    ]) + G.nota("em todo estado: o que houve e um caminho. Um botão principal por caixa. No celular, cada estado é a folha baixa", 1300, 36, 560) + FIM)


def fechada_1920() -> str:
    px, py = G.tela(*CAIS_XY, "ilha")
    return (cab("Cais · a semana fechada") + G.mundo("ilha", G.pet(1500, 700, "parado")) + G.topo(agora=False) + G.trilho("pet") + G.minimapa()
            + painel_cais(corpo_fechada(), 330, 84, 540)
            + painel_cais(corpo_segredo(), 900, 84, 460, sub="conferir a semana", cls="ca-segredo")
            + G.nota("3 · a semana fechada: a etiqueta 'fechada', a hora em que fechou e o seu resultado em destaque, em texto", 1400, 96, 300)
            + G.nota("a tabela final é a que o servidor gravou no fechamento; não muda mais. A seta da direita volta à semana aberta", 1400, 196, 300)
            + G.nota("'Conferir a semana' fica fechado, no fim: é para quem quer auditar, não para todo mundo (UX-CA-5)", 1400, 300, 300)
            + G.nota("4 · aberto: o segredo para copiar e a regra em uma frase. O jogo não confere sozinho; a conta é de quem copia", 1400, 400, 300)
            + G.nota("os dois painéis lado a lado são só da prancha: no jogo, o segundo troca o corpo do primeiro", 1400, 500, 300)
            + FIM)


def lugar_1920(aberto: bool) -> str:
    """o cais trancado (antes do nivel 10) e o cartao de destrave: os moldes da prancha dos lugares (lugar_trancado e cartao_destrave)"""
    cx, cy = G.tela(*CAIS_XY, "ilha")
    base = (cab("o cais destravado" if aberto else "o cais trancado") + G.mundo("ilha", G.pet(1160, 400, "parado"))
            + G.topo() + G.trilho("pet") + G.pilha() + G.dock() + G.minimapa())
    if not aberto:
        return (base + f'<span class="caixa cadeado-ilha" style="left:{cx:.0f}px;top:{cy:.0f}px" tabindex="0" role="img" '
                f'aria-label="Cais, trancado, Nv 10: abre com o primeiro Mega">{G.svg("cadeado")}<b>Nv 10</b></span>'
                + G.balao_aberto("<b>Nv 10</b> · Abre com o primeiro Mega", cx - 20, cy + 46, 260)
                + G.nota("5 · antes do nível 10: o cais aparece na ilha, apagado, com o cadeado e o nível, como os outros lugares (plano dos lugares, 3.4)", 540, 250, 300)
                + G.nota("o balão aberto: o foco ou o toque no cais. O marco é o primeiro Mega (MMO-13); no beta, 3 medalhas (BT0-1)", 540, 370, 300)
                + G.nota("o cais não ganha ícone no trilho nem no celular: entra-se pelo lugar, pelo minimapa e por 'Ver a semana' na Arena (UX-CA-2)", 540, 470, 300)
                + G.nota("o fundo é de antes do cais 3D: a posição do cadeado é só de layout", 540, 590, 300)
                + FIM)
    cartao = (f'<section class="caixa cartao-destrave" role="dialog" aria-labelledby="cd-tit" style="left:{cx + 150:.0f}px;top:{cy - 40:.0f}px">'
              f'<span class="cd-ic">{ic("ancora")}</span><span class="cd-txt"><b id="cd-tit">Cais</b><span>Veja o ranking da semana.</span>'
              f'<span class="cd-bts"><button type="button" class="bt acao">{G.svg("seta")}Ir</button><button type="button" class="bt">Depois</button></span></span></section>')
    return (base + f'<span class="caixa cadeado-ilha aberto" style="left:{cx:.0f}px;top:{cy:.0f}px" role="img" aria-label="aberto">{G.svg("aberto")}</span>'
            + cartao
            + G.nota("6 · o nível 10 confirmado: o cartão de destrave do cais, no molde dos outros lugares (4.1): o ícone, 'Cais' e uma frase de até 8 palavras", 620, 470, 320)
            + G.nota("'Ir' leva a câmera ao cais e abre a semana; 'Depois' fecha. Uma vez só. Hoje o marco 10 conta em silêncio (seção 12 da tarefa)", 620, 580, 320)
            + G.nota("sem conta, o cais abre igual e mostra o estado 2c: a conta continua sendo escolha (CN-1)", 620, 690, 320)
            + FIM)


# ---------------------------------------------------------------------------------------------------- as telas a 390 (e uma a 360)
def _cel(titulo: str, corpo: str, topo: int, nota: str = "", sub: str = "ranking da semana", c360: bool = False) -> str:
    return (cab_cel(titulo, topo, c360) + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna()
            + C.folha("Cais", corpo, icone="ancora", sub=sub, voltar="").replace('class="caixa folha', 'class="caixa folha ca-folha')
            + (M.nota(nota, 14, topo - 80) if nota else "") + FIM)


def cais_390(c360: bool = False) -> str:
    return _cel("Cais · a semana · " + ("360" if c360 else "390"), corpo_semana(curto=True), 150 if c360 else 190,
                "a folha alta: a semana, os estágios, 6 linhas e a sua. A coluna 'Lutas' sai; continua em 'Ver todas'", c360=c360)


def fechada_390() -> str:
    return _cel("Cais · a semana fechada · 390", corpo_fechada(curto=True), 230)


def sem_conta_390() -> str:
    return _cel("Cais · sem conta · 390", est_sem_conta(), 560, "os estados usam a folha baixa: a ilha e o pet ficam à vista")


def segredo_390() -> str:
    return _cel("Cais · conferir a semana · 390", corpo_segredo(), 300, sub="conferir a semana")


TELAS = {
    "cais_1920": cais_1920, "estados_1920": estados_1920, "fechada_1920": fechada_1920,
    "trancado_1920": lambda: lugar_1920(False), "destravado_1920": lambda: lugar_1920(True),
    "cais_390": cais_390, "cais_360": lambda: cais_390(True), "fechada_390": fechada_390, "sem_conta_390": sem_conta_390,
    "segredo_390": segredo_390,
}


def escrever() -> None:
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")


if __name__ == "__main__":
    escrever()
