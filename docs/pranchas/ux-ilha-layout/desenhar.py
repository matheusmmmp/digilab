"""Planta da ilha vista de cima: a de hoje (do jogo, ilha_mvp.json) e as propostas A, B e C. So desenho."""
import json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon
import random

AQUI = Path(__file__).parent
# ilha_mvp.json: a ilhaDe(CMU_MVP) de web/app/src/telas/pet/ilha/grade.ts (celulas, objetos, enfeites e lugares), tirada em 2026-11-08 de cdc9e522
D = json.load(open(AQUI / "ilha_mvp.json", encoding="utf-8"))
X0, Z0, LARG, PROF = D["x0"], D["z0"], D["larg"], D["prof"]
W, H = D["area"]["w"], D["area"]["h"]

COR = {"agua": "#7ec8e3", "areia": "#ecd9a0", "g0": "#a6d77a", "g1": "#8fc463", "g2": "#78ad4f", "caminho": "#d7b98a",
       "arv": "#2f7d32", "pinho": "#1f5e2a", "arbusto": "#4f9a3a", "pedra": "#8b8f96", "poste": "#f2c94c", "enfeite": "#c0392b",
       "lugar": "#1d4e89", "lar": "#d35400", "praca": "#f5e6c8", "texto": "#1b1b1b"}

def fundo(ax, cel=True):
    """o terreno de hoje (o mesmo nas propostas: a moldura nao muda)"""
    for j in range(PROF):
        for i in range(LARG):
            t, n = D["celulas"][j * LARG + i]
            c = {"gr": COR[f"g{max(0, min(n, 2))}"], "ca": COR["caminho"], "ar": COR["areia"], "ag": COR["agua"]}[t]
            ax.add_patch(Rectangle((X0 + i, Z0 + j), 1, 1, color=c, lw=0))
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, ec="#333", lw=1.2, ls="--"))

def arvore(ax, x, z, r=1.3, cor=None, fruta=False):
    ax.add_patch(Circle((x, z), r, color=cor or COR["arv"], ec="#123", lw=0.4, zorder=5))
    if fruta: ax.add_patch(Circle((x, z), r * 0.35, color="#e74c3c", zorder=6))

def marca(ax, x, z, txt, cor, forma="s", tam=1.6, dz=-1.9):
    if forma == "s":
        ax.add_patch(FancyBboxPatch((x - tam / 2, z - tam / 2), tam, tam, boxstyle="round,pad=0.15", fc=cor, ec="white", lw=1, zorder=8))
    else:
        ax.add_patch(Circle((x, z), tam / 2, fc=cor, ec="white", lw=1, zorder=8))
    ax.text(x, z + dz, txt, ha="center", va="center", fontsize=6.5, weight="bold", color=COR["texto"], zorder=9,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))

def poste(ax, x, z):
    ax.add_patch(Circle((x, z), 0.45, fc=COR["poste"], ec="#7a5a00", lw=0.6, zorder=7))

def caminho(ax, pts, larg=1.6):
    xs, zs = zip(*pts)
    ax.plot(xs, zs, color=COR["caminho"], lw=larg * 4.2, solid_capstyle="round", zorder=2)

def eixos(ax, titulo):
    ax.set_xlim(X0, X0 + LARG); ax.set_ylim(Z0 + PROF, Z0); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(titulo, fontsize=10, weight="bold", loc="left")
    ax.annotate("câmera (o jogador olha para o norte)", xy=(W / 2, H + 9), ha="center", fontsize=6.5, color="#333")
    ax.annotate("N ↑", xy=(X0 + 2, Z0 + 2.5), fontsize=8, weight="bold")

# ------------------------------------------------------------------ hoje
def hoje(ax):
    fundo(ax)
    for m, x, z, e in D["objetos"]:
        if m in ("pinheiro", "arvore_redonda"): arvore(ax, x, z, 1.1 * e, COR["pinho"] if m == "pinheiro" else COR["arv"])
        elif m == "arbusto": ax.add_patch(Circle((x, z), 0.6, color=COR["arbusto"], zorder=4))
        elif m == "pedra": ax.add_patch(Circle((x, z), 0.5, color=COR["pedra"], zorder=4))
    for e in D["enfeites"]:
        if e["nome"] == "poste": poste(ax, e["x"], e["z"])
        else: marca(ax, e["x"], e["z"], e["nome"], COR["enfeite"], tam=1.2, dz=1.6)
    for l in D["lugares"]:
        marca(ax, l["x"], l["z"], {"barraca": "barraca (Diário)", "portao": "portão (Lutar)", "cais": "cais"}[l["nome"]], COR["lugar"], tam=2.2, dz=2.3)
    L = D["layout"]
    nx, nz = L["ninho"]; cx, cz = L["comedouro"]; bx, bz = L["bola_inicio"]
    marca(ax, nx, nz, "ninho", COR["lar"], "o", 1.8); marca(ax, cx, cz, "tigela", COR["lar"], "o", 1.2)
    marca(ax, bx, bz, "bola", COR["lar"], "o", 1.0)
    marca(ax, nx + 3, nz - 4, "saco (Crescer)", COR["lugar"], tam=1.4, dz=-1.8)
    eixos(ax, "Hoje (CMU_MVP): tudo enfileirado na faixa de cima, nenhuma árvore na área do pet")

# ------------------------------------------------------------------ as propostas (pontos em células do mundo; PROPOSTO, SEM FONTE)
def bosque(ax, cx, cz, n, raio, semente, cor=None):
    r = random.Random(semente)
    for _ in range(n):
        a, d = r.uniform(0, 2 * math.pi), raio * math.sqrt(r.random())
        arvore(ax, cx + d * math.cos(a), cz + d * math.sin(a), r.uniform(1.0, 1.5), cor or (COR["pinho"] if r.random() < .5 else COR["arv"]))
    for _ in range(n // 2):
        a, d = r.uniform(0, 2 * math.pi), raio * 1.15
        ax.add_patch(Circle((cx + d * math.cos(a), cz + d * math.sin(a)), 0.6, color=COR["arbusto"], zorder=4))

def praca(ax, x, z, r):
    ax.add_patch(Circle((x, z), r, fc=COR["praca"], ec="#b89b6a", lw=1, zorder=2))

def cinturao(ax, vao, semente):
    """a mata de fundo da moldura: densa e continua no norte e no leste do rio, com um vao em frente ao marco (o portao) para ele se ver"""
    r = random.Random(semente)
    for x in range(X0 + 1, 64, 2):
        if abs(x - vao) < 5: continue
        for z in (-9.5, -7, -4.8):
            if r.random() < .85: arvore(ax, x + r.uniform(-.6, .6), z + r.uniform(-.6, .6), r.uniform(1.0, 1.4), COR["pinho"] if r.random() < .6 else COR["arv"])
    for z in range(-10, 31, 2):
        for x in (69.5, 72.5, 75.5):
            if r.random() < .8: arvore(ax, x + r.uniform(-.6, .6), z + r.uniform(-.6, .6), r.uniform(1.0, 1.4), COR["pinho"])
    for z in range(-2, 24, 3):
        if r.random() < .7: arvore(ax, -6 + r.uniform(-1, 1), z, 1.2, COR["arv"])

def proposta(ax, P, titulo):
    fundo(ax)
    cinturao(ax, P["lugares"]["portão (Lutar)"][0], 7)
    for c in P["caminhos"]: caminho(ax, c)
    for p in P.get("pracas", []): praca(ax, *p)
    for b in P["bosques"]: bosque(ax, *b)
    for x, z, fr in P["frutiferas"]: arvore(ax, x, z, 1.5, COR["arv"], fruta=True)
    for x, z in P["postes"]: poste(ax, x, z)
    for x, z, t in P["pedras"]: ax.add_patch(Circle((x, z), t, color=COR["pedra"], zorder=4))
    for nome, (x, z) in P["enfeites"].items(): marca(ax, x, z, nome, COR["enfeite"], tam=1.2, dz=1.6)
    for nome, (x, z) in P["lugares"].items(): marca(ax, x, z, nome, COR["lugar"], tam=2.2, dz=2.3)
    for nome, (x, z, t) in P["lar"].items(): marca(ax, x, z, nome, COR["lar"], "o", t)
    for x, z, txt in P.get("notas", []):
        ax.text(x, z, txt, fontsize=6, style="italic", color="#3b3b3b", ha="center", zorder=10)
    eixos(ax, titulo)

A = {  # o lar no bosque + a praca: a recomendada
    "caminhos": [[(14, 16), (22, 16), (31, 16)], [(31, 16), (31, 6), (31, -1)], [(31, 16), (36, 24), (38, 31)], [(31, 16), (40, 13), (47, 10)]],
    "pracas": [(31, 16, 4.2)],
    "bosques": [(7, 6, 6, 3.5, 1), (2, 13, 4, 2.5, 2), (54, 8, 10, 6, 3), (58, 22, 8, 5, 4), (20, 26, 4, 2.5, 5), (44, 26, 3, 2.2, 6)],
    "frutiferas": [(9, 9, "a"), (14, 7, "b"), (6, 14, "c")],
    "postes": [(27.5, 13), (34.5, 13), (27.5, 19.5), (34.5, 19.5), (33.5, 26), (37, 30)],
    "pedras": [(60, -2, 0.9), (62, -1, 0.7), (57.5, -3, 0.6), (49, 12, 0.6), (11, 22, 0.6)],
    "enfeites": {"carro": (59, -3), "geladeira": (62.5, -3.5), "trilho": (55.5, -4.5)},
    "lugares": {"portão (Lutar)": (31, -2.5), "barraca (Diário)": (48.5, 8.5), "cais": (38, 33), "saco (Crescer)": (22, 9)},
    "lar": {"ninho": (11, 13, 1.9), "tigela": (16, 15.5, 1.2), "bola": (21, 19, 1.0)},
    "notas": [(11, 19.5, "o lar: bosque atrás, quintal aberto na frente"), (31, 22.4, "praça: o nó"), (56, 15.5, "a mata (borda leste)"), (59, 1.3, "ferro-velho")],
}
B = {  # a vila em roda: o pet no centro e tudo em volta
    "caminhos": [[(32, 15), (32, -1)], [(32, 15), (14, 12)], [(32, 15), (50, 11)], [(32, 15), (30, 32)], [(32, 15), (44, 20)]],
    "pracas": [(32, 15, 6.5)],
    "bosques": [(25, 8, 5, 2.4, 11), (39, 8, 5, 2.4, 12), (5, 6, 8, 4.5, 13), (58, 8, 9, 5, 14), (8, 25, 5, 3, 15), (58, 24, 6, 4, 16)],
    "frutiferas": [(28, 10.5, "a"), (36, 10.5, "b"), (24, 17, "c")],
    "postes": [(26, 15), (38, 15), (31, 21), (33, 21), (30.5, 27)],
    "pedras": [(3, -1, 0.9), (5, -2, 0.7), (45, 22, 0.6)],
    "enfeites": {"carro": (3, -3), "geladeira": (6.5, -3.5), "trilho": (9, -4.5)},
    "lugares": {"portão (Lutar)": (32, -2.5), "barraca (Diário)": (13, 11), "cais": (30, 33), "saco (Crescer)": (45, 20)},
    "lar": {"ninho": (32, 13, 1.9), "tigela": (35, 16.5, 1.2), "bola": (29, 17.5, 1.0)},
    "notas": [(32, 24.5, "o ninho no centro da roda"), (6, 1.5, "ferro-velho")],
}
C = {  # a trilha: do lar a oeste ate a mata a leste, um destino por zona
    "caminhos": [[(8, 15), (16, 13), (24, 17), (32, 14), (40, 18), (48, 15), (56, 16)], [(32, 14), (32, -1)], [(24, 17), (22, 32)]],
    "pracas": [(32, 14, 3.2)],
    "bosques": [(3, 8, 6, 3.2, 21), (12, 4, 4, 2.5, 22), (40, 6, 5, 3, 23), (55, 6, 9, 5, 24), (56, 25, 7, 4, 25), (12, 25, 4, 2.6, 26)],
    "frutiferas": [(5, 12, "a"), (9, 9, "b"), (4, 18, "c")],
    "postes": [(16, 15.2), (24, 19), (32, 16.8), (40, 20), (48, 17.2)],
    "pedras": [(44, -2, 0.9), (46.5, -2.6, 0.7), (63, 12, 0.6)],
    "enfeites": {"carro": (44, -3.5), "geladeira": (47.5, -3.8), "trilho": (41, -4.5)},
    "lugares": {"portão (Lutar)": (32, -2.5), "barraca (Diário)": (49, 11.5), "cais": (22, 33), "saco (Crescer)": (24, 12)},
    "lar": {"ninho": (8, 14, 1.9), "tigela": (12, 16.5, 1.2), "bola": (17, 19, 1.0)},
    "notas": [(8, 21, "o lar"), (40, 23.5, "a trilha liga as zonas"), (45, 1.2, "ferro-velho")],
}

def salvar(nome, fn, *a):
    fig, ax = plt.subplots(figsize=(11, 6.6), dpi=150)
    fn(ax, *a)
    fig.tight_layout(); fig.savefig(AQUI / f"{nome}.png"); plt.close(fig)

salvar("planta_hoje", hoje)
salvar("planta_A", proposta, A, "A · O lar no bosque e a praça (recomendada)")
salvar("planta_B", proposta, B, "B · A vila em roda, com o pet no centro")
salvar("planta_C", proposta, C, "C · A trilha, uma zona depois da outra")
json.dump({"A": A, "B": B, "C": C}, open(AQUI / "propostas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
