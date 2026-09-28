"""Calibracao PvE: lutadores com stats do catalogo contra NPCs de stats maiores."""
import random, combate
from combate import *
from bots import bots
combate.C.update(MOV_V2=True, PARRY=5, FINTA=True, MORTE_SUBITA=25)

def params(st):
    v,f,r,F,m,g = (st[k] for k in ('vigor','folego','recuperacao','forca','mira','guarda'))
    return dict(hp=70+3*v, g0=30+2*f, gmax=80+2*f, regen=4+0.4*r,
                mp=0.7+0.03*F, md=0.7+0.03*m, mg=1.3-0.03*g)

def resolver_p(a,b,acts,dist,turno,P):
    A=[a,b]; X=list(acts)
    guts=[A[i].guts-(0 if X[i] in ('executar','fintar') else C['CUSTO'][X[i]]) for i in range(2)]
    dano=[0.0,0.0]; interr=[False,False]
    for i in range(2):
        j=1-i; me,op=X[i],X[j]; base=0; tipo=None
        if me=='rapido': base,tipo=C['D_RAPIDO'],'rapido'
        elif me=='executar' and dist==PERTO: base,tipo=C['D_PESADO'],'pesado'
        elif me=='disparo': base,tipo=C['D_DISPARO'],'disparo'
        elif me=='fintar' and dist==PERTO: base,tipo=C['D_RAPIDO'],'rapido'
        if me=='rapido' and op=='preparar': interr[j]=True
        if tipo:
            base*= P[i]['md'] if tipo=='disparo' else P[i]['mp']
            mm=1.0
            if op=='defender': mm=(C['DEF_PES'] if tipo=='pesado' else C['DEF_MULT'])*P[j]['mg']
            elif op=='esquivar' and tipo in ('pesado','disparo'): mm=0
            elif op=='carregar': mm=C['CARR_MULT']
            if turno>=C['MORTE_SUBITA']: mm*=C['MS_MULT']
            dano[j]+=base*mm
            if tipo=='rapido' and op=='defender': dano[i]+=C['PARRY']
    av=[x=='avancar' for x in X]; rc=[x=='recuar' for x in X]
    mov=-sum(av)+sum(1 for i in range(2) if rc[i] and not av[1-i])
    d2=max(PERTO,min(LONGE,dist+mov)); out=[]
    for i in range(2):
        g=guts[i]+P[i]['regen']+(C['DEF_REGEN'] if X[i]=='defender' else 0)+(C['CARR_GANHO'] if X[i]=='carregar' else 0)
        out.append(L(A[i].hp-dano[i],min(P[i]['gmax'],g),X[i]=='preparar' and not interr[i],A[i].hist+[X[i]]))
    return out[0],out[1],d2

def partida_p(pa,pb,Sa,Sb,seed):
    rng=random.Random(seed); P=[params(Sa),params(Sb)]
    a=L(P[0]['hp'],P[0]['g0']); b=L(P[1]['hp'],P[1]['g0']); d=MEDIO; ct=[{k:0 for k in range(12)}]*2
    for t in range(C['TMAX']):
        xa,_=pa.decidir(a,b,d,rng,ct[0]); xb,_=pb.decidir(b,a,d,rng,ct[1])
        a,b,d=resolver_p(a,b,(xa,xb),d,t,P)
        if a.hp<=0 or b.hp<=0: return 0.5 if a.hp<=0 and b.hp<=0 else (1.0 if b.hp<=0 else 0.0)
    fa,fb=a.hp/P[0]['hp'],b.hp/P[1]['hp']; return 0.5 if fa==fb else float(fa>fb)

def uniforme(total):
    return {k:total/6 for k in ('vigor','folego','recuperacao','forca','mira','guarda')}

def taxa(pa,pb,Sa,Sb,N=150):
    return sum(partida_p(pa,pb,Sa,Sb,k) for k in range(N))/N
