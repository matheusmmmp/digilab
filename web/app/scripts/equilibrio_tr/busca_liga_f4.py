"""Fase 4 da rodada de equilibrio do tempo real (G-3, a Liga): a busca por coordenadas dos fatores dos 6 lideres da Liga, lider a lider,
na grade 0,1 a 2,5, ate 3 passadas (as 3 rodadas da fase), com 4 processos. Ordem registrada antes de rodar: 1) mais formas na faixa
[0,25; 0,85]; 2) a menor soma do que falta ate a faixa; 3) a menor mudanca de fator (a soma de |fator - hoje|). Cada ponto e uma
rodada da bancada (fase4_progressao.ts --parte g3 --fatores-hoje --fatores), gravada em medicoes/equilibrio_tr/fase4/liga/.
uso (em web/app): python scripts/equilibrio_tr/busca_liga_f4.py"""
import json,subprocess,os,sys
from concurrent.futures import ThreadPoolExecutor
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
G="scripts/medicoes/equilibrio_tr/fase4/liga"
HOJE={'campina': 0.4, 'torre': 0.3, 'floresta': 0.1, 'cidadela': 1, 'lago': 1.7, 'espiral': 0.9}
GRADE=[round(.1*i,1) for i in range(1,26)]
cache={}
def nome(f): return "_".join(f"{k}{f[k]}" for k in HOJE)
def mede(f):
    key=nome(f)
    if key in cache: return cache[key]
    os.makedirs(G,exist_ok=True); p=f"{G}/{key}.json"
    if not os.path.exists(p):
        subprocess.run(["npx.cmd","tsx","scripts/equilibrio_tr/fase4_progressao.ts","--faixa","calibracao","--parte","g3","--fatores-hoje","--fatores",json.dumps({"liga":f}),"--saida",p],check=True,capture_output=True)
    t=[v["titulos"] for v in json.load(open(p))["metas"]["G-3"]["formas"].values()]
    dentro=sum(.25<=x<=.85 for x in t); falta=sum(max(.25-x,0,x-.85) for x in t); mud=sum(abs(f[k]-HOJE[k]) for k in HOJE)
    cache[key]=(-dentro,round(falta,4),round(mud,4)); return cache[key]
f=dict(HOJE); atual=mede(f); print("inicio",f,atual,flush=True)
for passada in range(3):
    mudou=False
    for k in HOJE:
        cands=[{**f,k:v} for v in GRADE]
        with ThreadPoolExecutor(4) as ex: rs=list(ex.map(mede,cands))
        best=min(zip(rs,cands),key=lambda t:t[0])
        if best[0]<atual: f,atual,mudou=best[1],best[0],True
        print("passada",passada+1,k,f[k],atual,flush=True)
    if not mudou: break
print("FIM",json.dumps(f),atual)
