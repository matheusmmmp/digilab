# Gera a prancha "a luta ranqueada" (docs/PLANO_UX_LUTA_RANQUEADA.md; a etapa MMO4 do docs/PLANO_V3_MMO.md). So desenho; nenhum codigo do jogo.
# Usa os ajudantes da prancha dos lugares (../ux-lugares-menus/gerar.py e gerar_movel.py) e os da conta (../ux-conta/gerar.py: o painel, a
# folha e os icones); o que e novo esta em ranqueada.css. A pele vem de ?pele=vidro|xcom; no desktop ?sem tira as notas, e no celular as
# notas so aparecem com ?notas.
# Uso (da raiz): python docs/pranchas/ux-luta-ranqueada/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# DE ONDE VEM CADA TEXTO E CADA REGRA:
#   so a vitoria ranqueada vale ponto, pela faixa do rival ....... MMO-7; web/app/src/ranking/pontos.ts (PONTOS_FAIXA: Champion 20)
#   o mesmo rival na semana vale a metade ........................ MMO-7; pontos.ts
#   10 lutas ranqueadas por dia, pelo relogio do servidor ........ MMO-8; LUTAS_POR_DIA; o 429 limite_do_dia com reabre_em (sementes.ts)
#   a semente vem do servidor e a pedida conta como luta ......... MMO-6; POST /sementes (servidor_web/src/envio/sementes.ts)
#   a luta sem envio vale como derrota ........................... pontos.ts (nao_enviada, pendente); fecha no fim da semana (MMO5)
#   o servidor manda na pontuacao; o cliente mostra a previa ..... MMO-5; POST /envios devolve as lutas e os pontos
#   abre no nivel 10, o primeiro Mega (no beta, 3 medalhas) ...... MMO-13; BT0-1; o 403 nivel_insuficiente
#   so com a conta ............................................... CN-1; o 401
#   o cliente de outra versao nao envia .......................... MMO-14; o 422 versao_*_desconhecida
#   a semana: de segunda a domingo, horario de Brasilia .......... MMO-9
#   o rival e o mapa: os da Arena de hoje ........................ TelaLugaresPoc.tsx (rivaisArenaPoc, os 8 mapas de motor/arena/cenas.ts)
# EXEMPLO DE LAYOUT, NUNCA DADO: os rivais, "7 de 10", "60 pontos", "3 rivais", as horas. Os pontos por faixa e o limite sao PROPOSTOS, SEM
# FONTE (plano MMO). Os tamanhos de interface sao PROPOSTO, SEM FONTE.
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "ux-lugares-menus"))
import importlib.util  # noqa: E402
import gerar as G  # noqa: E402
import gerar_movel as M  # noqa: E402

# o gerar.py da conta tem o mesmo nome do dos lugares: entra por caminho, com outro nome (ele importa o dos lugares como "gerar")
_spec = importlib.util.spec_from_file_location("gerar_conta", AQUI.parent / "ux-conta" / "gerar.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

IC = {
    "trofeu": '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3"/>',
    "servidor": '<rect x="3" y="4" width="18" height="7" rx="1"/><rect x="3" y="13" width="18" height="7" rx="1"/><path d="M7 7.5h.01M7 16.5h.01"/>',
    "sem_rede": '<path d="M2 8.5a15 15 0 0 1 20 0M5.5 12a10 10 0 0 1 13 0M9 15.5a5 5 0 0 1 6 0M12 19h.01"/><path d="M3 3l18 18"/>',
    "mapa": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2zM9 4v14M15 6v14"/>',
    "enviar": '<path d="M12 19V5M6 11l6-6 6 6"/><path d="M4 21h16"/>',
}


C.IC.update(IC)   # o painel e a folha da conta desenham o icone do cabecalho pelo ic() de la


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else C.ic(n, cls)


def _css(h: str) -> str:
    return (h.replace("<title>A conta · ", "<title>A luta ranqueada · ").replace("<title>Lugares da ilha · ", "<title>A luta ranqueada · ")
            .replace('href="conta.css"', 'href="../ux-conta/conta.css"')
            .replace("</head>", '<link rel="stylesheet" href="ranqueada.css">\n</head>'))


def cab(titulo: str) -> str:
    return _css(C.cab(titulo))


def cab_cel(titulo: str, topo: int, c360: bool = False) -> str:
    return _css(C.cab_cel(titulo, topo, c360))


FIM = G.FIM
PET = "Growlmon"
# os rivais da Arena de um Champion (EXEMPLO: a lista de verdade e a do rivaisArenaPoc); todos na faixa Champion, 20 pontos
RIVAIS = [("Greymon", 20, ""), ("Garurumon", 20, ""), ("Birdramon", 10, "vencido 1×"), ("Kabuterimon", 20, ""),
          ("Togemon", 5, "vencido 2×"), ("Ikkakumon", 20, ""), ("Angemon", 20, ""), ("Leomon", 20, "")]
ESCOLHIDO = "Garurumon"
MAPAS = ["Campo de treino", "Coliseu", "Floresta Green Shade", "Praia Shellfish"]   # 4 dos 8 de motor/arena/cenas.ts


# ---------------------------------------------------------------------------------------------------- as pecas
def modo(ranqueada: bool = True, trancada: str = "") -> str:
    """a escolha no topo da aba Arena: Treino (a luta de hoje) ou Ranqueada. Trancada: com o motivo no rotulo, e a aba continua tocavel"""
    t, r = ("false", "true") if ranqueada else ("true", "false")
    cad = f'{G.svg("cadeado", "ic ic-p")}' if trancada else ""
    return (f'<div class="lr-modo" role="radiogroup" aria-label="Tipo de luta">'
            f'<button type="button" class="filtro" role="radio" aria-checked="{t}" aria-pressed="{t}">{G.svg("lutar", "ic ic-p")}Treino</button>'
            f'<button type="button" class="filtro" role="radio" aria-checked="{r}" aria-pressed="{r}"'
            f'{f" aria-label=&quot;Ranqueada, trancada: {trancada}&quot;" if trancada else ""}>{ic("trofeu", "ic ic-p")}Ranqueada{cad}</button></div>')


def placar(hoje: int = 7, pontos: int = 60, rivais: int = 3, curto: bool = False) -> str:
    """a semana e o dia, sempre a vista: quantas lutas de hoje ja foram e os pontos da semana (os confirmados pelo servidor)"""
    pinos = "".join(f'<i class="{"usada" if i < hoje else ""}"></i>' for i in range(10))
    return (f'<div class="lr-placar" role="group" aria-label="Luta ranqueada: {hoje} de 10 lutas de hoje usadas; {pontos} pontos na semana">'
            f'<div class="lr-dia"><span class="rot">Hoje</span><b class="num-g">{hoje}<small>/10</small></b>'
            f'<span class="lr-pinos" aria-hidden="true">{pinos}</span></div>'
            f'<div class="lr-sem"><span class="rot">Semana</span><b class="num-g">{pontos}<small> pontos</small></b>'
            + ("" if curto else f'<span class="sec">{rivais} rivais vencidos · fecha domingo</span>') + '</div></div>')


def rivais(curto: bool = False) -> str:
    """curto (o celular): 'vencido 1× · metade' numa linha so; o rotulo inteiro continua no aria-label"""
    def um(n: str, p: int, obs: str) -> str:
        sel = n == ESCOLHIDO
        meio = f"<small>{obs} · {'metade' if curto else 'vale a metade'}</small>" if obs else "<small>Champion</small>"
        return (f'<button type="button" class="rival lr-rival" role="radio" aria-checked="{"true" if sel else "false"}" '
                f'aria-label="{n}, vale {p} pontos{", " + obs + ", vale a metade" if obs else ""}"><span class="radio" aria-hidden="true"></span>'
                f'<span><b>{n}</b>{meio}</span><span class="lr-vale{" meio" if obs else ""}"><b>{p}</b></span></button>')
    return f'<div class="rivais" role="radiogroup" aria-label="Rival">{"".join(um(*r) for r in RIVAIS)}</div>'


def mapas(n: int = 4) -> str:
    chips = "".join(f'<button type="button" class="filtro" role="radio" aria-checked="{"true" if i == 1 else "false"}" '
                    f'aria-pressed="{"true" if i == 1 else "false"}">{m}</button>' for i, m in enumerate(MAPAS[:n]))
    return (f'<div class="lr-mapas" role="radiogroup" aria-label="Mapa">{chips}'
            f'<button type="button" class="filtro" aria-expanded="false" aria-label="Mostrar os outros {8 - n} mapas">+{8 - n}</button></div>')


AVISO = (f'<p class="lr-aviso">{ic("info", "ic ic-p")}<span>Ao pedir, a luta <b>já conta</b> nas 10 de hoje. '
         f'Se ela não chegar ao servidor, vale como derrota.</span></p>')


AVISO_CURTO = (f'<p class="lr-aviso">{ic("info", "ic ic-p")}<span>Ao pedir, a luta <b>já conta</b>. Sem envio, vale como derrota.</span></p>')


def corpo_arena() -> str:
    return f'''
{modo()}
{placar()}
<div><span class="rot">Rival · quanto vale a vitória</span><div style="margin-top:6px">{rivais()}</div></div>
<div><span class="rot">Mapa</span><div style="margin-top:6px">{mapas()}</div></div>
{AVISO}
<div class="lutar-linha"><button type="button" class="bt acao grande">{ic("trofeu")}Lutar valendo 20</button></div>'''


def corpo_arena_cel() -> str:
    return f'''
{modo()}
{placar(curto=True)}
<div><span class="rot">Rival · quanto vale a vitória</span><div style="margin-top:6px">{rivais(curto=True)}</div></div>
{AVISO_CURTO}
<div class="lutar-linha"><button type="button" class="bt acao grande">{ic("trofeu")}Lutar valendo 20</button>
  <button type="button" class="bt" aria-label="Mapa: Coliseu. Trocar">{ic("mapa")}Coliseu</button></div>'''


def linha_luta(rival: str = ESCOLHIDO, mapa: str = "Coliseu") -> str:
    return (f'<div class="lr-luta"><span class="palquinho">{G.spr(PET, .6)}</span><span class="lr-x" aria-hidden="true">×</span>'
            f'<span><b>{rival}</b><small>{mapa} · luta 8 de 10 de hoje</small></span></div>')


# ---- os estados do pedido (a caixa pequena, como os estados da conta)
def est_pedindo() -> str:
    return f'''
{C.passos(1).replace("Jogo", "Escolha").replace("Google", "Servidor").replace("Conta", "Luta")}
<p class="ct-chamada" role="status">Pedindo a luta ao servidor</p>
<p class="sec">A luta começa assim que a resposta chegar.</p>
<div class="ct-bts"><button type="button" class="bt" disabled>Cancelar</button></div>'''


def est_sem_rede() -> str:
    return f'''
<div class="destaque" role="alert"><span class="rot">Sem resposta</span><b class="grande">A luta não foi pedida</b>
  <p>Nada foi gasto: continuam 7 de 10 hoje.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Tentar de novo</button><button type="button" class="bt">Lutar de treino</button></div>'''


def est_limite() -> str:
    return f'''
<div class="destaque" role="status"><span class="rot">Limite de hoje</span><b class="grande">10 de 10 lutas feitas</b>
  <p>Volta à meia-noite, no horário de Brasília. Faltam 3 h 12 min.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Lutar de treino</button><button type="button" class="bt">Ver a semana</button></div>'''


def est_nivel() -> str:
    return f'''
<div class="destaque" role="status"><span class="rot">Trancada · Nv 10</span><b class="grande">Abre com o primeiro Mega</b>
  <p>Leve um pet ao Mega e envie o registro. A luta de treino continua aberta.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Lutar de treino</button></div>'''


def est_sem_conta() -> str:
    return f'''
<div class="destaque" role="status"><span class="rot">Só com a conta</span><b class="grande">A luta ranqueada pede a conta</b>
  <p>O servidor confere cada luta. Sem conta, nada muda no jogo.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">{ic("conta")}Entrar</button><button type="button" class="bt">Agora não</button></div>'''


def est_versao() -> str:
    return f'''
<div class="destaque" role="alert"><span class="rot">Versão antiga</span><b class="grande">Atualize o jogo</b>
  <p>O servidor confere com a versão nova. Nada foi gasto.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">{ic("replay")}Recarregar</button><button type="button" class="bt">Lutar de treino</button></div>'''


# ---- o resultado: a previa do jogo e a palavra do servidor
def res(estado: str) -> str:
    """depois do palco. previa: o que o jogo viu; conferindo: o envio saiu; confirmado: o servidor concorda; divergiu: o servidor contou outra
    coisa, e a dele vale (MMO-5); pendente: o envio nao saiu, e a luta espera"""
    topo = linha_luta()
    if estado == "conferindo":
        return f'''{topo}
<div class="lr-res" role="status"><span class="etq">prévia</span><b class="lr-grande">Vitória</b><b class="lr-pts">+20</b></div>
<p class="lr-serv" role="status">{ic("servidor", "ic ic-p")}<span>O servidor está conferindo a luta.</span><span class="lr-pontos3" aria-hidden="true"><i></i><i></i><i></i></span></p>
<div class="ct-bts"><button type="button" class="bt acao">Outra luta</button><button type="button" class="bt">Ver a luta de novo</button></div>'''
    if estado == "confirmado":
        return f'''{topo}
<div class="lr-res ok" role="status"><span class="etq ok">{G.svg("check", "ic ic-p")}conferido</span><b class="lr-grande">Vitória</b><b class="lr-pts">+20</b></div>
<p class="lr-serv">{ic("servidor", "ic ic-p")}<span>Semana: <b>80 pontos</b> · 4 rivais vencidos · 8 de 10 hoje</span></p>
<div class="ct-bts"><button type="button" class="bt acao">Outra luta</button><button type="button" class="bt">Ver a luta de novo</button></div>'''
    if estado == "derrota":
        return f'''{topo}
<div class="lr-res" role="status"><span class="etq ok">{G.svg("check", "ic ic-p")}conferido</span><b class="lr-grande">Derrota</b><b class="lr-pts zero">0</b></div>
<p class="lr-serv">{ic("servidor", "ic ic-p")}<span>Semana: <b>60 pontos</b> · 3 rivais vencidos · 8 de 10 hoje</span></p>
<div class="ct-bts"><button type="button" class="bt acao">Outra luta</button><button type="button" class="bt">Ver a luta de novo</button></div>'''
    if estado == "divergiu":
        return f'''{topo}
<div class="lr-res alerta" role="alert"><span class="etq alerta">o servidor</span><b class="lr-grande">Derrota</b><b class="lr-pts zero">0</b></div>
<div class="destaque"><span class="rot">O servidor viu outra luta</span>
  <p>Aqui deu vitória; no servidor, derrota. Vale a conta do servidor. Isso é raro e fica registrado.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Outra luta</button><button type="button" class="bt">Ver a luta do servidor</button></div>'''
    return f'''{topo}
<div class="lr-res" role="status"><span class="etq">prévia</span><b class="lr-grande">Vitória</b><b class="lr-pts">+20</b></div>
<div class="destaque" role="alert"><span class="rot">Ainda não enviada</span>
  <p>Sem conexão. O jogo envia sozinho quando ela voltar. Se não chegar até domingo, vale como derrota.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">{ic("enviar")}Enviar agora</button><button type="button" class="bt">Lutar de treino</button></div>'''


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def _lutar(corpo: str, notas: str, titulo: str, w: int = 610) -> str:
    px, py = G.tela(1600, 482, "portao")
    return (cab(titulo) + G.mundo("portao", G.pet(1600, 792, "parado")) + G.topo(agora=False) + G.trilho("lutar") + G.minimapa("lutar", "portao")
            + G.placa("portao", "Portão da arena", px, py - 62)
            + G.painel("lutar", "arena", corpo, 690, 84, w)
            + G.contagem(1140, 62) + notas + FIM)


def arena_1920() -> str:
    return _lutar(corpo_arena(),
                  G.nota("1 · a luta ranqueada mora na aba Arena do portão: a mesma tela da luta de treino, com uma escolha no topo (UX-LR-1). O cais fica para as tabelas (MMO5)", 1316, 96, 300)
                  + G.nota("sempre à vista: as lutas de hoje (7 de 10, em texto e em pinos) e os pontos da semana, os já conferidos pelo servidor (MMO-8, MMO-9)", 1316, 196, 300)
                  + G.nota("cada rival diz quanto vale a vitória. O já vencido na semana vale a metade e diz por quê em texto, não só em cor (MMO-7)", 1316, 300, 300)
                  + G.nota("o rival e o mapa são escolha do jogador, como no treino (UX-LR-5: o plano, na seção 3, fala em rival do servidor)", 1316, 420, 300)
                  + G.nota("o aviso fica ACIMA do botão, e o botão diz o que está em jogo. Não há segunda tela de confirmação (UX-LR-2)", 1316, 520, 300)
                  + G.nota("os rivais, '7 de 10' e '60 pontos' são EXEMPLO. Os pontos por faixa e o limite são PROPOSTOS (plano MMO)", 1316, 610, 300),
                  "Lutar · Arena · Ranqueada")


def estados_1920() -> str:
    def est(i: int, rot: str, corpo: str) -> str:
        x = 40 + (i % 3) * 620
        y = 96 + (i // 3) * 400
        return (G.nota(rot, x, y, 560)
                + C.painel("Luta ranqueada", corpo, icone="trofeu", sub="Arena", voltar="", x=x, y=y + 44, w=420, cls="ct-estado lr-estado").replace(
                    'class="ic"', 'class="ic"', 1))
    return (cab("Luta ranqueada: os estados do pedido") + G.mundo("portao", "") + '<div class="veu"></div>'
            + '<span class="caixa titulo-pr" style="position:absolute;left:40px;top:36px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">Luta ranqueada: os estados do pedido</span>'
            + est(0, "2a · tocou em 'Lutar valendo': o jogo manda o registro até ali e espera a semente. Três pontos parados; nada gira (guia, seção 11)", est_pedindo())
            + est(1, "2b · o servidor não respondeu: a semente NÃO saiu, então nada foi gasto. A tela diz isso com o número", est_sem_rede())
            + est(2, "2c · a 11ª do dia (429): quando volta, em texto. A luta de treino é o botão principal", est_limite())
            + est(3, "2d · a conta ainda não abriu a luta ranqueada (403). A escolha 'Ranqueada' mostra o cadeado e continua tocável, para ler o motivo", est_nivel())
            + est(4, "2e · sem conta (401): leva à tela Entrar da prancha da conta. 'Agora não' fecha e não insiste", est_sem_conta())
            + est(5, "2f · o jogo aberto é de outra versão (422, MMO-14): recarregar. Nada foi gasto", est_versao())
            + G.nota("em todo estado: o que houve, se a luta foi gasta ou não, e um caminho. Um botão principal por caixa. No celular, cada estado é a folha baixa", 1300, 36, 560)
            + FIM)


def resultado_1920() -> str:
    def est(i: int, rot: str, corpo: str) -> str:
        x = 40 + (i % 3) * 620
        y = 96 + (i // 3) * 420
        return (G.nota(rot, x, y, 560)
                + C.painel("Luta ranqueada", corpo, icone="trofeu", sub="Arena · resultado", voltar="", x=x, y=y + 44, w=460, cls="ct-estado lr-estado lr-resultado"))
    return (cab("Luta ranqueada: o resultado") + G.mundo("portao", "") + '<div class="veu"></div>'
            + '<span class="caixa titulo-pr" style="position:absolute;left:40px;top:36px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">Luta ranqueada: o resultado</span>'
            + est(0, "3a · o palco fechou. O jogo mostra o que viu, com a etiqueta 'prévia', e já envia. O jogador não fica parado esperando (UX-LR-3)", res("conferindo"))
            + est(1, "3b · o servidor concordou: a etiqueta vira 'conferido' (texto e ícone) e a linha traz a semana atualizada", res("confirmado"))
            + est(2, "3c · a derrota conferida: 0, sem drama e sem vermelho. A luta foi usada", res("derrota"))
            + est(3, "3d · o servidor contou outra coisa (raro; a MMO0 não achou nenhum em 4 561 lutas). Vale a dele, com o aviso (MMO-5)", res("divergiu"))
            + est(4, "3e · o envio não saiu. O jogo reenvia sozinho quando a conexão volta; o botão é para quem quer agora (UX-LR-4)", res("pendente"))
            + G.nota("o resultado troca o corpo da aba Arena depois do palco. 'Outra luta' volta à escolha (quadro 1), com o placar novo", 1280, 516, 560)
            + G.nota("os pontos entram na semana só quando o servidor confere. A prévia nunca soma no placar", 1280, 600, 560)
            + FIM)


# ---------------------------------------------------------------------------------------------------- as telas a 390 (e uma a 360)
def arena_390(c360: bool = False) -> str:
    topo = 190 if c360 else 215
    return (cab_cel("Lutar · Arena · Ranqueada · " + ("360" if c360 else "390"), topo, c360)
            + G.mundo("m_portao", G.pet(1480, 760, "parado", k=1.3)) + M.topo() + M.coluna("lutar")
            + G.folha("lutar", "arena", corpo_arena_cel()).replace('class="caixa folha', 'class="caixa folha ct-folha lr-folha')
            + M.nota("a mesma folha da Arena; o mapa vira um botão ao lado do Lutar, e os textos encurtam para caber sem rolar", 14, topo - 70) + FIM)


def _cel(titulo: str, corpo: str, topo: int, nota: str = "", sub: str = "Arena") -> str:
    return (cab_cel(titulo, topo) + G.mundo("m_portao", G.pet(1480, 760, "parado", k=1.3)) + M.topo() + M.coluna("lutar")
            + C.folha("Luta ranqueada", corpo, icone="trofeu", sub=sub, voltar="").replace('class="caixa folha', 'class="caixa folha lr-folha')
            + (M.nota(nota, 14, topo - 80) if nota else "") + FIM)


def limite_390() -> str:
    return _cel("Luta ranqueada: limite de hoje · 390", est_limite(), 560, "os estados usam a folha baixa: o portão e o pet ficam à vista")


def resultado_390() -> str:
    return _cel("Luta ranqueada: conferido · 390", res("confirmado"), 500, "o resultado na folha baixa, logo depois do palco", sub="Arena · resultado")


def pendente_390() -> str:
    return _cel("Luta ranqueada: ainda não enviada · 390", res("pendente"), 470, sub="Arena · resultado")


TELAS = {
    "arena_1920": arena_1920, "estados_1920": estados_1920, "resultado_1920": resultado_1920,
    "arena_390": arena_390, "arena_360": lambda: arena_390(True), "limite_390": limite_390, "resultado_390": resultado_390,
    "pendente_390": pendente_390,
}


def escrever() -> None:
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")


if __name__ == "__main__":
    escrever()
