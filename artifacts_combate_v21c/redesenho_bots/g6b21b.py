import json, sys
exec(open(r"C:/Users/mathe/AppData/Local/Temp/claude/D--Trab-digilab/b4af1f72-98e8-4e1a-8d2e-e438b6adceea/scratchpad/g6b21.py", encoding="utf-8").read().split("CAND = {")[0])
def topo2(forma, r1, r2):
    g = ADULTOS[forma]; rr_ = [r1, r2] + list(g.regras)[:-2]
    return ListaGambits(tuple(rr_), g.final, g.estagio)
CAND2 = {
 "furioso": [("hp_perto_pesado", troca("furioso", "topo", regra(se(HP(), _d(PERTO)), A.PREPARAR_PESADO))),
             ("hp_perto_recua", troca("furioso", "topo", regra(se(HP(), _d(PERTO)), A.RECUAR))),
             ("esq+pesado", topo2("furioso", regra(se(HP(), F(A.GOLPE_RAPIDO)), A.ESQUIVAR), regra(se(HP(), _d(PERTO)), A.PREPARAR_PESADO))),
             ("hp75_esq", troca("furioso", "topo", regra(se(HP(0.75), F(A.GOLPE_RAPIDO)), A.ESQUIVAR)))],
 "muralha": [("hp_perto_pesado", troca("muralha", "topo", regra(se(HP(), _d(PERTO)), A.PREPARAR_PESADO))),
             ("hp_medio_disparo", troca("muralha", "topo", regra(se(HP(), _d(MEDIO)), A.DISPARO))),
             ("hp_carrega", troca("muralha", "topo", regra(se(HP(), F(A.DEFENDER)), A.CARREGAR))),
             ("hp75_pesado", troca("muralha", "topo", regra(se(HP(0.75), _d(PERTO)), A.PREPARAR_PESADO)))],
 "sentinela": [("esq+avanca", topo2("sentinela", regra(se(HP(), F(A.MARCAR)), A.ESQUIVAR), regra(se(HP(), F(A.DISPARO)), A.AVANCAR))),
               ("hp75_esq_marcar", troca("sentinela", "topo", regra(se(HP(0.75), F(A.MARCAR)), A.ESQUIVAR))),
               ("hp_marca", troca("sentinela", "topo", regra(se(HP(), _ga(20)), A.MARCAR)))],
 "emboscador": [("esq+avanca", topo2("emboscador", regra(se(HP(), F(A.MARCAR)), A.ESQUIVAR), regra(se(HP(), F(A.DISPARO)), A.AVANCAR))),
                ("hp75_avanca", troca("emboscador", "topo", regra(se(HP(0.75), F(A.DISPARO)), A.AVANCAR)))],
 "vigia": [("hp_golpe_prep", troca("vigia", "topo", regra(se(HP(), F(A.PREPARAR_PESADO)), A.GOLPE_RAPIDO))),
           ("hp_perto_pesado", troca("vigia", 7, regra(se(HP(), _d(PERTO)), A.PREPARAR_PESADO))),
           ("hp_def_golpe", troca("vigia", 7, regra(se(HP(), F(A.GOLPE_RAPIDO)), A.DEFENDER)))],
}
for f in (sys.argv[1:] or list(CAND2)):
    print(f, json.dumps({n: g6b(f, g) for n, g in CAND2[f]}), flush=True)
