import json, sys
sys.path.insert(0, r"D:\Trab\digilab\v1"); sys.path.insert(0, r"D:\Trab\digilab\v1\experiments")
from avaliar_v21c import regras, taxa
from digilab.combate_v2.v21.bots import ADULTOS, ADOLESCENTES, lutador_adulto, lutador_adolescente, _d, PERTO, MEDIO, LONGE, _ga
from digilab.combate_v2.v21.catalogo import Forma, LINHA_DA_FORMA, carater_canonico, perfil
from digilab.combate_v2.v21.gambits import Condicao as C, ListaGambits, regra, se
from digilab.combate_v2.v21.partida import Lutador
from digilab.combate_v2.v21.regras import Acao as A
from digilab.config import CONFIG_CATALOGO, CONFIG_COMBATE_V21
r = regras({"hp_por_vigor": 2.5, "hp_base": 75.0, "marca_fragil": True})
ESP = list(CONFIG_CATALOGO.especies_ativas); FORMAS = list(ADULTOS)
TEC = {"brigao": A.INVESTIDA, "guardiao": A.CONTRA_GOLPE, "cacador": A.MARCAR, "colosso": A.PELE_DURA}
HP = lambda f: C("hp_proprio_abaixo", (f,)); F = lambda a: C("oponente_frequente", (a,))
def com_topo(f, *n):
    g = ADULTOS[f]; return ListaGambits((tuple(n) + g.regras)[:CONFIG_COMBATE_V21.max_regras_adulto], g.final, g.estagio)
def medir(f, gl, n=8):
    vals6, vo, va = [], [], []
    for e in ESP:
        b = lutador_adulto(f, e, r.v21); fo = Forma(e, "adulto", "sereno", LINHA_DA_FORMA[f], f)
        fav = Lutador(f"{f}#f", perfil(fo, None, carater_canonico(f), 1.05, r.v21), gl, b.epsilon)
        des = Lutador(f"{f}#d", perfil(fo, None, carater_canonico(f), 0.95, r.v21), gl, b.epsilon)
        vals6.append(taxa(fav, des, "g6b", n, r))
        eu = Lutador(f"{f}@{e}", b.perfil, gl, b.epsilon)
        for o in FORMAS:
            if o != f: vo.append(taxa(eu, lutador_adulto(o, e, r.v21), "vs", n, r))
        va.append(taxa(eu, lutador_adolescente(LINHA_DA_FORMA[f], e, carater_canonico(f), r.v21), "e4", n, r))
    m = lambda v: round(sum(v) / len(v), 3)
    return {"g6b": m(vals6), "vs_outros": m(vo), "vs_adol": m(va)}
acoes = [A.GOLPE_RAPIDO, A.ESQUIVAR, A.DEFENDER, A.CARREGAR, A.RECUAR, A.AVANCAR, A.DISPARO, A.PREPARAR_PESADO]
for f in sys.argv[1:]:
    tec = TEC[LINHA_DA_FORMA[f]]
    out = {"original": medir(f, ADULTOS[f])}
    for lim in (0.5, 0.75):
        for a in acoes:
            try:
                gl = com_topo(f, regra(se(HP(lim), F(tec)), a))
                out[f"{lim}:{a.value}"] = medir(f, gl)
            except Exception as ex:
                pass
    print(f, json.dumps(out), flush=True)
