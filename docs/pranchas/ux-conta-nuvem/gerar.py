# Gera a prancha "o save na nuvem: levar o pet e os estados" (as telas 3 e 5 do docs/PLANO_V3_CONTA.md, secao 3; etapa CN3; a parte
# da frente UX na F0 do docs/ROADMAP_V3_CONTA.md). So desenho; nenhum codigo do jogo.
# Usa o molde da prancha da conta (../ux-conta/gerar.py: a caixa, a folha, o aceite, os icones) e os ajudantes da prancha dos lugares.
# A pele vem de ?pele=vidro|xcom; no desktop ?sem tira as notas, e no celular as notas so aparecem com ?notas.
# Uso (da raiz): python docs/pranchas/ux-conta-nuvem/gerar.py   (escreve os HTML ao lado; a lista esta em TELAS, no fim)
#
# DE ONDE VEM CADA REGRA (docs/PLANO_V3_CONTA.md, CN-1 a CN-18 DECIDIDAS; docs/RESULTADO_V3_CONTA_CN0.md):
#   o que sobe: o pet ativo, os guardados, Geracoes, o Tamer ....... plano 5.4 (CN-4) e a tabela fechada na CN0 (secao 2)
#   a conversa e o laboratorio nunca sobem ......................... plano 5.4; CN0, "nao sai"
#   "ficar com os deste aparelho / os da nuvem / guardar os dois" ... plano, secao 3, tela 3
#   a vez por pet; "jogar aqui" toma a vez; os outros so veem ...... plano 5.2 (CN-3)
#   a escolha da historia; a outra vai para Geracoes, so para ver .. plano 5.3 (CN-3)
#   "atualize o jogo" antes de sincronizar ......................... plano 5.5 (a MMO-14)
#   o servidor fora do ar: o jogo continua neste aparelho .......... plano 5.1 (o localStorage continua sendo a fonte do aparelho)
#   as copias: uma por dia, 30 dias; restaurar nao apaga a de agora  plano 5.6 (CN-5)
#   o pet nao envelhece com o jogo fechado ......................... CN0, secao 3
# EXEMPLO DE LAYOUT, NUNCA DADO: os nomes dos pets e dos aparelhos, "dia 3 · 07:42", as horas, as contagens de eventos, as datas.
# Nenhum numero de jogo novo. Os tamanhos de interface sao PROPOSTO, SEM FONTE.
import importlib.util
from pathlib import Path

AQUI = Path(__file__).parent
# o gerar.py da prancha da conta, carregado com outro nome (ele mesmo importa o "gerar" da prancha dos lugares)
_esp = importlib.util.spec_from_file_location("gerar_conta", AQUI.parent / "ux-conta" / "gerar.py")
C = importlib.util.module_from_spec(_esp)
_esp.loader.exec_module(C)
G, M = C.G, C.M

IC = {
    "nuvem_ok": '<path d="M17.5 19H7a5 5 0 1 1 1.6-9.7A6 6 0 0 1 20 11.5 3.8 3.8 0 0 1 17.5 19z"/><path d="M9 14l2 2 4-4"/>',
    "enviando": '<path d="M17.5 19H7a5 5 0 1 1 1.6-9.7A6 6 0 0 1 20 11.5 3.8 3.8 0 0 1 17.5 19z"/><path d="M12 17v-6M9.5 13.5L12 11l2.5 2.5"/>',
    "sem_nuvem": '<path d="M17.5 19H7a5 5 0 1 1 1.6-9.7A6 6 0 0 1 20 11.5 3.8 3.8 0 0 1 17.5 19z"/><path d="M4 4l16 16"/>',
    "restaurar": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
}

C.IC.update(IC)   # a caixa e a folha da prancha da conta desenham o icone do cabecalho pelo ic() de la


def ic(n: str, cls: str = "ic") -> str:
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>' if n in IC else C.ic(n, cls)


def _css(h: str) -> str:
    h = h.replace('href="conta.css"', 'href="../ux-conta/conta.css">\n<link rel="stylesheet" href="nuvem.css"')
    return h.replace("<title>A conta · ", "<title>O save na nuvem · ")


def tela(titulo: str, caixa: str, notas: str = "", extra: str = "", so_ver: bool = False) -> str:
    dock = G.dock("nv-so-ver") if so_ver else G.dock()
    return (_css(C.cab(titulo)) + G.mundo("ilha", G.pet(1160, 400, "parado")) + G.topo() + G.trilho("pet") + G.pilha() + dock + G.minimapa()
            + caixa + extra + notas + C.FIM)


def tela_cel(titulo: str, caixa: str, topo: int, notas: str = "") -> str:
    return (_css(C.cab_cel(titulo, topo)) + G.mundo("m_ilha", G.pet(1160, 400, "parado", k=1.3)) + M.topo() + M.coluna() + caixa + notas + C.FIM)


def aviso(titulo: str, corpo: str, icone: str = "nuvem", x: int = 720, y: int = 250, w: int = 480, cls: str = "") -> str:
    """um aviso sobre a tela do pet: a mesma caixa da conta, no meio, sem o voltar (nao e parte dos Ajustes)"""
    return C.painel(titulo, corpo, icone=icone, sub="Conta", voltar="", x=x, y=y, w=w, cls="nv-aviso " + cls)


# ---------------------------------------------------------------------------------------------------- a tela 3: levar o pet para a conta
def corpo_levar() -> str:
    return f'''
<p class="ct-chamada">Levar os pets para a conta</p>
<div><span class="rot">Neste aparelho</span>
  <ul class="ct-ap nv-lista" style="margin-top:6px">
    <li class="med-li">{G.svg("pet")}<span><b>Growlmon</b><small>Champion · dia 3</small></span><span class="etq ok">ativo</span></li>
    <li class="med-li">{G.svg("users")}<span><b>2 guardados</b><small>Koromon e Gabumon</small></span></li>
    <li class="med-li">{G.svg("geracoes")}<span><b>Gerações</b><small>3 vidas</small></span></li>
    <li class="med-li">{G.svg("medalhas")}<span><b>O Tamer</b><small>medalhas, Bits e itens</small></span></li>
  </ul></div>
<p class="sec linha">{ic("sem_fala", "ic ic-p")}A conversa e o laboratório não sobem.</p>
<div class="ct-bts"><button type="button" class="bt acao">{ic("enviando")}Levar para a conta</button><button type="button" class="bt">Agora não</button></div>
<p class="sec">Eles continuam também neste aparelho.</p>'''


def lado(titulo: str, pet: str, quando: str, resto: str, icone: str, marcado=None) -> str:
    if marcado is None:
        return (f'<div class="nv-lado"><span class="linha rot">{ic(icone)}{titulo}</span><b>{pet}</b><small>{quando}</small><small>{resto}</small></div>')
    return (f'<button type="button" class="nv-lado" role="radio" aria-checked="{"true" if marcado else "false"}">'
            f'<span class="linha rot"><span class="radio"></span>{ic(icone)}{titulo}</span><b>{pet}</b><small>{quando}</small><small>{resto}</small></button>')


def corpo_escolher() -> str:
    def op(marcado: bool, tit: str, sub: str) -> str:
        return (f'<button type="button" class="rival" role="radio" aria-checked="{"true" if marcado else "false"}"><span class="radio"></span>'
                f'<span><b>{tit}</b><small>{sub}</small></span></button>')
    return f'''
<p class="ct-chamada">A conta já tem pets</p>
<div class="nv-lados">
  {lado("Neste aparelho", "Growlmon", "Champion · dia 3, 07:42", "2 guardados", "pc")}
  {lado("Na nuvem", "Agumon", "Rookie · dia 1, 19:20", "1 guardado · do Celular", "nuvem")}
</div>
<div><span class="rot" id="nv-qual">O que fica</span>
  <div class="nv-opcoes" role="radiogroup" aria-labelledby="nv-qual" style="margin-top:6px">
    {op(True, "Guardar os dois", "O Growlmon segue ativo. O Agumon entra nos guardados.")}
    {op(False, "Ficar com os deste aparelho", "Os da nuvem vão para as cópias, por 30 dias.")}
    {op(False, "Ficar com os da nuvem", "Os deste aparelho vão para as cópias, por 30 dias.")}
  </div></div>
<div class="ct-bts"><button type="button" class="bt acao">Continuar</button><button type="button" class="bt">Agora não</button></div>'''


# ---------------------------------------------------------------------------------------------------- a tela 5: os estados
def chip(icone: str, txt: str, cls: str = "", hora: str = "") -> str:
    h = f"<small>{hora}</small>" if hora else ""
    return f'<span class="caixa p nv-chip {cls}">{ic(icone)}{txt}{h}</span>'


def col(c: str, balao: str, nota: str) -> str:
    return (f'<div class="nv-col">{c}<span class="caixa balao" role="tooltip">{balao}</span>'
            f'<span class="nota fixa">{nota}</span></div>')


def hud_1920() -> str:
    fileira = ('<div class="nv-fileira">'
               + col(chip("nuvem_ok", "Na nuvem", "ok"), "Sincronizado agora há pouco, às <b>07:40</b>.", "a · sincronizado: o estado de quase sempre. Discreto: o ícone e duas palavras")
               + col(chip("enviando", "Enviando"), "Mandando o que você fez desde as <b>07:40</b>.", "b · enviando: sem girar nem piscar (guia, seção 11); some sozinho")
               + col(chip("sem_nuvem", "Offline", "alerta", "07:40"), "Sem conexão. O jogo continua aqui e envia quando voltar.", "c · offline: com a hora da última sincronização. É aviso, não erro")
               + col(chip("olho", "Só ver", "alerta"), "Este pet está aberto no <b>Celular</b>. Toque para jogar aqui.", "d · outro aparelho tem a vez (plano 5.2). O toque abre o aviso do quadro 4")
               + col(chip("aberto", "Salvo"), "Sem conta: o pet fica só neste aparelho.", "e · sem conta: o 'salvo' de hoje, sem mudança")
               + "</div>")
    return (_css(C.cab("O estado da nuvem no HUD")) + G.mundo("ilha", G.pet(1160, 400, "parado")) + '<div class="veu"></div>' + G.topo()
            + fileira
            + G.nota("3 · o estado da nuvem fica onde hoje está o '● salvo', dentro da caixa do relógio (canto de cima, à direita). Nenhuma peça nova no HUD (UX-NV-3)", 1380, 86, 300)
            + G.nota("aqui os cinco estados estão ampliados e lado a lado, cada um com o balão do foco aberto. No jogo aparece um por vez, no tamanho do 'salvo'", 150, 190, 420)
            + G.nota("o estado nunca é só cor: há o ícone e a palavra. No leitor de tela, uma região de status diz a mudança uma vez", 150, 560, 420)
            + G.nota("no celular: o mesmo ícone, sem a palavra, ao lado da hora; o toque abre o balão", 150, 610, 420)
            + C.FIM)


def corpo_outro() -> str:
    return f'''
<p class="ct-chamada">Este pet está aberto no Celular</p>
<p class="sec">Desde as 07:31. Aqui ele fica só para ver.</p>
<div class="ct-bts"><button type="button" class="bt acao">{ic("pc")}Jogar aqui</button><button type="button" class="bt">Só ver</button></div>
<p class="sec linha">{ic("info", "ic ic-p")}Jogar aqui fecha a vez do Celular. O que ele já enviou fica.</p>'''


def corpo_divergiu(marcado: int = -1) -> str:
    dis = "" if marcado >= 0 else " disabled"
    return f'''
<div class="destaque"><span class="rot">Duas histórias</span><b class="grande">O Growlmon seguiu por dois caminhos</b>
  <p>Os dois aparelhos jogaram sem se falar. Escolha qual história fica.</p></div>
<div class="nv-lados" role="radiogroup" aria-label="Qual história fica">
  {lado("Este PC", "dia 3, 07:42", "38 eventos novos", "o último: carinho", "pc", marcado == 0)}
  {lado("Celular", "dia 3, 06:10", "12 eventos novos", "o último: treino", "celular", marcado == 1)}
</div>
<p class="sec linha">{G.svg("geracoes", "ic ic-p")}A outra vai para Gerações, só para ver. Nada é apagado.</p>
<div class="ct-bts"><button type="button" class="bt acao"{dis}>Ficar com esta</button><button type="button" class="bt">Decidir depois</button></div>'''


def corpo_atualize() -> str:
    return f'''
<div class="destaque"><span class="rot">Versão antiga</span><b class="grande">Atualize o jogo</b>
  <p>A sincronização volta depois de atualizar. O pet continua neste aparelho.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Atualizar agora</button><button type="button" class="bt">Depois</button></div>'''


def corpo_fora() -> str:
    return f'''
<div class="destaque"><span class="rot">Nuvem</span><b class="grande">O servidor não respondeu</b>
  <p>O jogo continua neste aparelho e envia quando o servidor voltar.</p></div>
<p class="sec">Última sincronização: hoje, 07:40.</p>
<div class="ct-bts"><button type="button" class="bt acao">Continuar jogando</button></div>'''


def corpo_sessao() -> str:
    return f'''
<div class="destaque"><span class="rot">Conta</span><b class="grande">Entre de novo</b>
  <p>A sessão acabou. O pet continua neste aparelho; entre para voltar a sincronizar.</p></div>
<div class="ct-bts"><button type="button" class="bt acao">Entrar</button><button type="button" class="bt">Agora não</button></div>'''


COPIAS = [("Hoje, 03:00", "Growlmon · dia 3"), ("Ontem, 03:00", "Growlmon · dia 2"), ("10/11, 03:00", "Agumon · dia 1"),
          ("09/11, 03:00", "Koromon · dia 1")]


def corpo_copias() -> str:
    li = "".join(f'<li><span><b>{q}</b><small>{o}</small></span><button type="button" class="bt">{ic("restaurar")}Restaurar</button></li>'
                 for q, o in COPIAS)
    return f'''
<p class="sec">Uma cópia por dia, guardada por 30 dias.</p>
<ul class="nv-copias">{li}</ul>
<p class="sec linha">{ic("info", "ic ic-p")}As histórias que você não escolheu também ficam aqui.</p>'''


def corpo_restaurar() -> str:
    return f'''
<div class="destaque"><span class="rot">Restaurar</span><b class="grande">Voltar à cópia de ontem</b>
  <ul class="ct-some">
    <li class="fica">{G.svg("check")}O Growlmon volta ao dia 2.</li>
    <li class="fica">{G.svg("check")}O de agora vira uma cópia. Nada se perde.</li>
    <li class="neutro">{ic("celular")}Vale para todos os aparelhos da conta.</li>
  </ul></div>
<div class="ct-bts"><button type="button" class="bt acao">Restaurar</button><button type="button" class="bt">Cancelar</button></div>'''


# ---------------------------------------------------------------------------------------------------- as telas a 1920
def levar_1920() -> str:
    return tela("Levar os pets para a conta", C.painel("Conta", corpo_levar()),
                G.nota("1 · Levar o pet para a conta (tela 3), logo depois do primeiro acesso. A lista é o que a CN0 fechou: o pet ativo, os guardados, Gerações e o Tamer", 580, 136, 300)
                + G.nota("o que não sobe é dito na mesma tela: a conversa e o laboratório (plano 5.4)", 580, 400, 280)
                + G.nota("'Agora não' deixa tudo como está; a oferta fica em Ajustes › Conta, sem insistir", 580, 460, 280)
                + G.contagem(420, 106))


def escolher_1920() -> str:
    return tela("A conta já tem pets", C.painel("Conta", corpo_escolher()),
                G.nota("2 · a conta já tem pets (entrou num segundo aparelho). Os dois lados aparecem antes da pergunta: o pet, o nível, o dia do jogo e de onde veio", 580, 136, 300)
                + G.nota("as três respostas do plano, cada uma com a consequência escrita. 'Guardar os dois' vem marcada, porque é a que não tira nada de lugar (UX-NV-1)", 580, 330, 300)
                + G.nota("o que não foi escolhido vai para as cópias por 30 dias: o plano não diz o destino, e esta é a proposta (UX-NV-2)", 580, 440, 300)
                + G.contagem(420, 106))


def outro_1920() -> str:
    return tela("O pet aberto em outro aparelho", aviso("Outro aparelho", corpo_outro(), icone="celular"),
                G.nota("4 · 'este pet está aberto em outro aparelho' (plano 5.2). É um aviso sobre a tela do pet, não uma parte dos Ajustes", 1220, 256, 300)
                + G.nota("só ver: o pet e a ilha aparecem, e as ações ficam apagadas até 'Jogar aqui'. O estado do HUD mostra 'Só ver'", 720, 500, 320)
                + G.nota("a hora é a do relógio de verdade. O pet não envelhece com o jogo fechado (CN0, seção 3)", 1220, 340, 280),
                so_ver=True)


def divergiu_1920() -> str:
    return tela("Duas histórias", aviso("Duas histórias", corpo_divergiu(), icone="geracoes", y=200, w=520),
                G.nota("5 · a escolha da história (plano 5.3). Nenhuma vem marcada: aqui o jogo não escolhe por você. 'Ficar com esta' acende ao marcar", 1260, 206, 300)
                + G.nota("cada lado diz o dia do jogo, quantos eventos tem a mais e o último. São dados do registro, não um resumo inventado", 1260, 330, 300)
                + G.nota("a outra história vai para Gerações, só para ver: dito antes do botão. 'Decidir depois' deixa o pet só para ver (UX-NV-4)", 1260, 420, 300),
                so_ver=True)


def avisos_1920() -> str:
    def est(i: int, rot: str, titulo: str, corpo: str, icone: str) -> str:
        x = 150 + i * 560
        return G.nota(rot, x, 222, 480) + aviso(titulo, corpo, icone=icone, x=x, y=250, w=500)
    return (_css(C.cab("Os avisos da nuvem")) + G.mundo("ilha", "") + '<div class="veu"></div>'
            + '<span class="caixa titulo-pr" style="position:absolute;left:150px;top:120px;padding:10px 16px;font:700 18px/1.1 var(--hx-f);letter-spacing:.08em;text-transform:uppercase">A nuvem: os avisos</span>'
            + est(0, "6a · o aparelho está com o jogo desatualizado (plano 5.5)", "Atualizar", corpo_atualize(), "alerta")
            + est(1, "6b · o servidor fora do ar (aparece uma vez; depois, só o ícone 'Offline')", "Nuvem", corpo_fora(), "sem_nuvem")
            + est(2, "6c · a sessão expirou", "Conta", corpo_sessao(), "conta")
            + G.nota("os três dizem a mesma coisa antes de tudo: o pet continua neste aparelho. Nenhum trava o jogo", 150, 520, 420)
            + G.nota("um botão principal por caixa; sem contagem e sem texto de culpa (guia, princípio 5)", 710, 520, 420)
            + C.FIM)


def copias_1920() -> str:
    return tela("Conta: as cópias", C.painel("Cópias", corpo_copias(), icone="restaurar", sub="Conta", voltar="Voltar à conta"),
                G.nota("7 · as cópias do save (a parte da tela 4 que a prancha da conta deixou fora). Entra por uma linha nova em Conta › Seus dados: 'Cópias do save'", 580, 136, 300)
                + G.nota("uma por dia, por 30 dias (plano 5.6). Cada linha: o dia, o pet e o dia do jogo. 'Hoje, 03:00' é EXEMPLO", 580, 240, 280)
                + G.nota("as histórias não escolhidas (quadros 2 e 5) também caem aqui (UX-NV-2)", 580, 440, 280))


def restaurar_1920() -> str:
    return tela("Restaurar uma cópia", C.painel("Restaurar", corpo_restaurar(), icone="restaurar", sub="Cópias", voltar="Voltar às cópias"),
                G.nota("8 · restaurar: o que volta e o que acontece com o de agora (vira uma cópia: plano 5.6). Vale para todos os aparelhos", 580, 136, 300))


# ---------------------------------------------------------------------------------------------------- as telas a 390
def levar_390() -> str:
    return tela_cel("Levar os pets · 390", C.folha("Conta", corpo_levar()), 380)


def escolher_390() -> str:
    return tela_cel("A conta já tem pets · 390", C.folha("Conta", corpo_escolher()), 300)


def outro_390() -> str:
    return tela_cel("Outro aparelho · 390", C.folha("Outro aparelho", corpo_outro(), icone="celular", sub="Conta", voltar=""), 560,
                    M.nota("os avisos usam a folha baixa: o pet fica à vista", 14, 470))


def divergiu_390() -> str:
    return tela_cel("Duas histórias · 390", C.folha("Duas histórias", corpo_divergiu(0), icone="geracoes", sub="Conta", voltar=""), 380,
                    M.nota("aqui com 'Este PC' marcado: o botão acende", 14, 300))


def restaurar_390() -> str:
    return tela_cel("Restaurar · 390", C.folha("Restaurar", corpo_restaurar(), icone="restaurar", sub="Cópias", voltar="Voltar às cópias"), 480)


TELAS = {
    "levar_1920": levar_1920, "escolher_1920": escolher_1920, "hud_1920": hud_1920, "outro_1920": outro_1920, "divergiu_1920": divergiu_1920,
    "avisos_1920": avisos_1920, "copias_1920": copias_1920, "restaurar_1920": restaurar_1920,
    "levar_390": levar_390, "escolher_390": escolher_390, "outro_390": outro_390, "divergiu_390": divergiu_390, "restaurar_390": restaurar_390,
}


if __name__ == "__main__":
    for nome, f in TELAS.items():
        (AQUI / f"{nome}.html").write_text(f(), encoding="utf-8", newline="\n")
    print(len(TELAS), "telas")
