import sys, json
sys.path.insert(0, r"D:\Trab\digilab\v1"); sys.path.insert(0, r"D:\Trab\digilab\v1\experiments")
from avaliar_v21c import avaliar, regras
from digilab.combate_v2.v21.bots import RESPOSTAS_V21C
bots = sys.argv[1] == "1"
r = regras({"hp_por_vigor": 2.5, "hp_base": 75.0, "marca_fragil": True, "bots_v21c": bots})
o = avaliar(r, None, 10, resposta_marcar=RESPOSTAS_V21C["marcar"])
print("bots_v21c", bots, json.dumps({k: (v if k != "E2" else v[:2]) for k, v in o.items()}, ensure_ascii=False))
