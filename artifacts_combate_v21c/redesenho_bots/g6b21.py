import json, sys
sys.path.insert(0, r"D:\Trab\digilab\v1"); sys.path.insert(0, r"D:\Trab\digilab\v1\experiments")
from avaliar_v21c import regras, taxa
from digilab.combate_v2.v21.bots import ADULTOS, lutador_adulto, PREP, _d, _ga, _gb, PERTO, MEDIO, LONGE
from digilab.combate_v2.v21.catalogo import Forma, LINHA_DA_FORMA, carater_canonico, perfil
from digilab.combate_v2.v21.gambits import Condicao as C, ListaGambits, regra, se
from digilab.combate_v2.v21.partida import Lutador
from digilab.combate_v2.v21.regras import Acao as A
from digilab.config import CONFIG_CATALOGO

r = regras({"hp_por_vigor": 2.5, "hp_base": 75.0, "marca_fragil": True})
ESP = list(CONFIG_CATALOGO.especies_ativas)
F = lambda a: C("oponente_frequente", (a,))
HP = lambda f=0.5: C("hp_proprio_abaixo", (f,))


def g6b(forma, gl, n=20):
    vals = []
    for e in ESP:
        b = lutador_adulto(forma, e, r.v21)
        fo = Forma(e, "adulto", "sereno", LINHA_DA_FORMA[forma], forma)
        fav = Lutador(f"{forma}#f", perfil(fo, None, carater_canonico(forma), 1.05, r.v21), gl, b.epsilon)
        des = Lutador(f"{forma}#d", perfil(fo, None, carater_canonico(forma), 0.95, r.v21), gl, b.epsilon)
        vals.append(taxa(fav, des, "g6b", n, r))
    return round(sum(vals) / len(vals), 3)


def troca(forma, pos, nova):
    """Substitui a regra na posicao `pos` (a lista tem 8) por `nova`, ou insere no topo tirando a ultima."""
    g = ADULTOS[forma]
    regras_ = list(g.regras)
    if pos == "topo":
        regras_ = [nova] + regras_[:-1]
    else:
        regras_[pos] = nova
    return ListaGambits(tuple(regras_), g.final, g.estagio)


CAND = {
    "duelista": [("topo", regra(se(HP(), F(A.GOLPE_RAPIDO)), A.DEFENDER)), ("topo", regra(se(HP(), F(A.INVESTIDA)), A.DEFENDER)),
                 ("topo", regra(se(HP(), F(A.PREPARAR_PESADO)), A.GOLPE_RAPIDO))],
    "furioso": [("topo", regra(se(HP(), F(A.PREPARAR_PESADO)), A.GOLPE_RAPIDO)), ("topo", regra(se(HP(), F(A.GOLPE_RAPIDO)), A.ESQUIVAR)),
                ("topo", regra(se(HP(), F(A.INVESTIDA)), A.RECUAR))],
    "espelho": [("topo", regra(se(HP(), F(A.CONTRA_GOLPE)), A.PREPARAR_PESADO)), ("topo", regra(se(HP(), F(A.CONTRA_GOLPE)), A.CARREGAR)),
                ("topo", regra(se(HP(), F(A.CONTRA_GOLPE)), A.RECUAR))],
    "muralha": [("topo", regra(se(HP(), F(A.CONTRA_GOLPE)), A.PREPARAR_PESADO)), ("topo", regra(se(HP(), F(A.DEFENDER)), A.PREPARAR_PESADO)),
                ("topo", regra(se(HP(), F(A.CONTRA_GOLPE)), A.RECUAR))],
    "sentinela": [("topo", regra(se(HP(), F(A.MARCAR)), A.ESQUIVAR)), ("topo", regra(se(HP(), F(A.DISPARO)), A.AVANCAR)),
                  ("topo", regra(se(HP(), F(A.DISPARO)), A.DEFENDER))],
    "emboscador": [("topo", regra(se(HP(), F(A.MARCAR)), A.ESQUIVAR)), ("topo", regra(se(HP(), F(A.DISPARO)), A.AVANCAR)),
                   ("topo", regra(se(HP(), F(A.DISPARO)), A.DEFENDER))],
    "vigia": [("topo", regra(se(HP(), F(A.PELE_DURA)), A.RECUAR)), ("topo", regra(se(HP(), F(A.PREPARAR_PESADO)), A.ESQUIVAR)),
              ("topo", regra(se(HP(), F(A.PELE_DURA)), A.CARREGAR))],
    "tita": [("topo", regra(se(HP(), F(A.PELE_DURA)), A.RECUAR)), ("topo", regra(se(HP(), F(A.PREPARAR_PESADO)), A.GOLPE_RAPIDO)),
             ("topo", regra(se(HP(), F(A.PELE_DURA)), A.CARREGAR))],
}
formas = sys.argv[1:] or list(CAND)
for f in formas:
    res = {"original": g6b(f, ADULTOS[f])}
    for i, (pos, rg) in enumerate(CAND[f]):
        try:
            res[f"c{i}:{rg.acao.value}<-{rg.condicoes[1].params[0].value}"] = g6b(f, troca(f, pos, rg))
        except Exception as e:
            res[f"c{i}"] = f"invalida: {e}"
    print(f, json.dumps(res, ensure_ascii=False), flush=True)
