import sys
sys.path.insert(0, r"D:\Trab\digilab\v1"); sys.path.insert(0, r"D:\Trab\digilab\v1\experiments")
import digilab.combate_v2.v21.gambits as G
from avaliar_v21c import regras, taxa
from digilab.combate_v2.v21.bots import ADOLESCENTES, ADULTOS_V21C, lutador_adulto
from digilab.combate_v2.v21.catalogo import Forma, LINHA_DA_FORMA, carater_canonico, perfil
from digilab.combate_v2.v21.gambits import ListaGambits, CONDICOES_POR_ESTAGIO
from digilab.combate_v2.v21.partida import Lutador
from digilab.config import CONFIG_CATALOGO, CONFIG_COMBATE_V2
cap = int(sys.argv[1])
orig = G.max_regras
G.max_regras = lambda e: cap if e == "adolescente" else orig(e)
r = regras({"hp_por_vigor": 2.5, "hp_base": 75.0, "marca_fragil": True, "bots_v21c": True})
ok_c = set(CONDICOES_POR_ESTAGIO["adolescente"])
def adol(linha, forma):
    base = list(ADOLESCENTES[linha].regras)
    extra = [rg for rg in ADULTOS_V21C[forma].regras if all(c.nome in ok_c for c in rg.condicoes) and rg not in base]
    return ListaGambits(tuple((base + extra)[:cap]), ADOLESCENTES[linha].final, "adolescente")
res = {}
for f in ADULTOS_V21C:
    linha = LINHA_DA_FORMA[f]; vals = []
    for e in CONFIG_CATALOGO.especies_ativas:
        ad = lutador_adulto(f, e, r.v21)
        fo = Forma(e, "adolescente", "sereno", linha)
        ado = Lutador(f"adol-{linha}@{e}", perfil(fo, None, carater_canonico(f), 1.0, r.v21), adol(linha, f) if cap > 5 else ADOLESCENTES[linha], CONFIG_COMBATE_V2.epsilon_bots)
        vals.append(taxa(ad, ado, "e4", 10, r))
    res[f] = round(sum(vals) / len(vals), 3)
print("cap", cap, res)
