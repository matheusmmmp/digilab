import json, sys
exec(open(r"C:/Users/mathe/AppData/Local/Temp/claude/D--Trab-digilab/b4af1f72-98e8-4e1a-8d2e-e438b6adceea/scratchpad/g6b21b.py", encoding="utf-8").read().split("CAND2 = {")[0])
CAND3 = {
 "muralha": [("hp75_perto_recua", troca("muralha", "topo", regra(se(HP(0.75), _d(PERTO)), A.RECUAR))),
             ("hp75_medio_disparo", troca("muralha", "topo", regra(se(HP(0.75), _d(MEDIO)), A.DISPARO))),
             ("recua+dispara", topo2("muralha", regra(se(HP(0.75), _d(PERTO)), A.RECUAR), regra(se(HP(0.75), _d(MEDIO)), A.DISPARO))),
             ("hp75_golpe_contra", troca("muralha", "topo", regra(se(HP(0.75), F(A.CONTRA_GOLPE)), A.GOLPE_RAPIDO)))],
 "sentinela": [("hp75_avanca_disparo", troca("sentinela", "topo", regra(se(HP(0.75), F(A.DISPARO)), A.AVANCAR))),
               ("hp75_def_disparo", troca("sentinela", "topo", regra(se(HP(0.75), F(A.DISPARO)), A.DEFENDER))),
               ("esq75+avanca75", topo2("sentinela", regra(se(HP(0.75), F(A.MARCAR)), A.ESQUIVAR), regra(se(HP(0.75), F(A.DISPARO)), A.AVANCAR))),
               ("hp90_avanca", troca("sentinela", "topo", regra(se(HP(0.75), C("oponente_hp_abaixo", (0.75,))), A.AVANCAR)))],
}
for f in (sys.argv[1:] or list(CAND3)):
    print(f, json.dumps({n: g6b(f, g) for n, g in CAND3[f]}), flush=True)
