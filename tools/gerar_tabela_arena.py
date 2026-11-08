"""Gera web/app/motor/arena/formas.ts: a tabela de numeros da luta da POC para as 60 formas do jogo (LUTA_POC, LP1; a LP-2 de
docs/TAREFA_V3_LUTA_POC.md). O replay nao pode depender da pasta Assets/ (fora do git): a simulacao le so esta tabela.

Entrada (fora do git): D:/Trab/digilab/Assets/arena_up/dados/{golpes,atributos,atlas}.json, gerados por Assets/gerar_arena_up.py a
partir do prototipo remaster/fonte/site (Digimon UP, Bandai; com o credito, docs/UI_GUIDELINES.md, secao 5.1). As formas do jogo vem do
DIGIMON_DA_FORMA de web/app/motor/nomes.ts.

Saida, por forma: o Digimon no atlas da arena, o atributo, o golpe e a habilidade (a animacao, o instante do golpe `t` em s, o projetil
com o prefab, o tipo e a velocidade, os impactos), a duracao (ms) dos clipes do golpe e da habilidade (a soma dos quadros da tag, com o
recuo do prototipo quando a tag nao existe) e o fator de ritmo `fr` ja calculado (EQ.kGolpe = 0,06 e EQ.kProj = 0,05 da POC; a
simulacao so pode usar sqrt, min, max, floor, ceil, round e abs, por isso a potencia sai daqui). Os status do Digimon UP NAO entram
(LP-3): os numeros do lutador vem dos stats do pet. Os desenhos (pranchas e efeitos) continuam fora do git.

Uso (na raiz do repositorio): python tools/gerar_tabela_arena.py [--dados <pasta>] [--conferir]
--conferir: nao escreve; falha se o arquivo do git for diferente do que sairia agora. Falha alto se faltar arquivo, forma ou campo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS_PADRAO = Path("D:/Trab/digilab/Assets/arena_up/dados")
NOMES_TS = RAIZ / "web" / "app" / "motor" / "nomes.ts"
SAIDA = RAIZ / "web" / "app" / "motor" / "arena" / "formas.ts"

# constantes da POC (web/app/motor/arena/constantes.ts, EQ; remaster/arena_equilibrio.md). Um teste confere que batem com o EQ do TS.
K_GOLPE = 0.06
K_PROJ = 0.05
# o golpe de quem nao tem script de ataque no jogo: a regra do prototipo (GOLPE_GENERICO), PROPOSTO, PROTOTIPO
GOLPE_GENERICO = {"anim": "Attack_1", "t": 0.4, "proj": None, "hits": [], "skill": None}
# nomes do catalogo do DigiLab que o atlas da arena escreve de outro jeito (alem de espaco e caixa): o APELIDO_ATLAS do #448
APELIDO_ATLAS = {"Ankylomon": "Ankiromon"}
ATRIBUTOS = ("Vaccine", "Virus", "Data", "Free", "None", "Unknown")


def falha(msg: str) -> None:
    raise SystemExit(f"gerar_tabela_arena: {msg}")


def norma(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def ler_formas() -> dict[str, list[str]]:
    txt = NOMES_TS.read_text(encoding="utf-8")
    m = re.search(r"export const DIGIMON_DA_FORMA: Record<string, \[string, string\]> = (\{.*?\});", txt)
    if not m:
        falha(f"DIGIMON_DA_FORMA nao encontrado em {NOMES_TS}")
    formas = json.loads(m.group(1))
    if len(formas) != 60:
        falha(f"esperava 60 formas no DIGIMON_DA_FORMA, achei {len(formas)}")
    return formas


def tag_de(A: dict, nome: str) -> list:
    """o tagDe da POC: a de mesmo nome; senao a que comeca com as 4 primeiras letras; senao a primeira do atlas"""
    for t in A["t"]:
        if t[0] == nome:
            return t
    for t in A["t"]:
        if t[0].lower().startswith(nome.lower()[:4]):
            return t
    return A["t"][0]


def duracao(A: dict, nome: str) -> tuple[int, str]:
    tg = tag_de(A, nome)
    ms = 0
    for f in A["f"][tg[1]:tg[2] + 1]:
        if not isinstance(f[2], (int, float)):
            falha(f"duracao de quadro nao numerica ({nome})")
        ms += f[2]
    return ms, tg[0]


def fator_ritmo(g: dict) -> float:
    """o fatorRitmo da POC: golpe mais demorado e projetil mais lento batem mais forte"""
    f = (max(0.2, g["t"]) / 0.5) ** K_GOLPE
    if g["proj"]:
        f *= (30 / (g["proj"]["vel"] or 30)) ** K_PROJ
    return f


def golpe_base(g: dict, onde: str) -> dict:
    for k in ("anim", "t", "proj", "hits"):
        if k not in g:
            falha(f"{onde}: falta {k}")
    if not isinstance(g["t"], (int, float)):
        falha(f"{onde}: instante do golpe nao numerico")
    proj = None
    if g["proj"]:
        p = g["proj"]
        if not isinstance(p.get("vel"), (int, float)):
            falha(f"{onde}: velocidade do projetil")
        proj = {"prefab": p.get("prefab"), "vel": p["vel"], "tipo": p.get("tipo")}
    hits = [{"prefab": h["prefab"], "atraso": h["atraso"]} for h in g["hits"]]
    return {"anim": g["anim"], "t": g["t"], "proj": proj, "hits": hits, "fr": fator_ritmo(g)}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gerar(dados: Path) -> str:
    arqs = {n: dados / f"{n}.json" for n in ("golpes", "atributos", "atlas")}
    for p in arqs.values():
        if not p.is_file():
            falha(f"falta {p}")
    golpes = json.loads(arqs["golpes"].read_text(encoding="utf-8"))
    atributos = json.loads(arqs["atributos"].read_text(encoding="utf-8"))
    atlas = json.loads(arqs["atlas"].read_text(encoding="utf-8"))["d"]
    idx = {norma(n): n for n in atlas}
    linhas = []
    recuos = []
    for chave, (nome, estagio) in ler_formas().items():
        dig = idx.get(norma(APELIDO_ATLAS.get(nome, nome)))
        if not dig:
            falha(f"{chave} ({nome}) nao esta no atlas da arena")
        A = atlas[dig]
        atr = atributos.get(dig)
        if atr not in ATRIBUTOS:
            falha(f"{dig}: sem atributo ({atr})")
        bruto = golpes.get(dig)
        generico = bruto is None
        if generico:
            bruto = GOLPE_GENERICO
            recuos.append(f"{dig}: sem script de ataque no jogo, golpe generico")
        g = golpe_base(bruto, f"{dig}.golpe")
        sk = golpe_base(bruto["skill"], f"{dig}.habilidade") if bruto.get("skill") else None
        ms_atk, tag_atk = duracao(A, g["anim"])
        ms_sk, tag_sk = duracao(A, (sk or g)["anim"])
        if tag_atk != g["anim"]:
            recuos.append(f"{dig}: o golpe {g['anim']} usa a tag {tag_atk}")
        if sk and tag_sk != sk["anim"]:
            recuos.append(f"{dig}: a habilidade {sk['anim']} usa a tag {tag_sk}")
        item = {"digimon": dig, "nome": nome, "estagio": estagio, "atributo": atr, "generico": generico,
                "golpe": g, "habilidade": sk, "msGolpe": ms_atk, "msHabilidade": ms_sk}
        linhas.append(f"  {json.dumps(chave)}: {json.dumps(item, ensure_ascii=False)},")
    shas = "\n".join(f"   - {n}.json sha256 {sha(p)}" for n, p in arqs.items())
    rec = "\n".join(f"   - {r}" for r in recuos) or "   - nenhum"
    return f"""/* GERADO por tools/gerar_tabela_arena.py; nao editar a mao (python tools/gerar_tabela_arena.py --conferir confere).
   A tabela de numeros da luta da POC para as 60 formas do jogo (LUTA_POC, LP1; a LP-2 de docs/TAREFA_V3_LUTA_POC.md).
   Procedencia: os dados de jogo do Digimon UP (Bandai; com o credito, docs/UI_GUIDELINES.md, secao 5.1), copiados do prototipo
   remaster/fonte/site por Assets/gerar_arena_up.py para D:/Trab/digilab/Assets/arena_up/dados (fora do git):
{shas}
   As formas: o DIGIMON_DA_FORMA de web/app/motor/nomes.ts. So numeros e nomes: os desenhos ficam fora do git. Os status do Digimon UP nao
   entram (LP-3). `fr` e o fatorRitmo da POC ja calculado (kGolpe = {K_GOLPE}, kProj = {K_PROJ}); msGolpe e msHabilidade sao a duracao (ms) dos
   clipes no atlas. Os recuos do prototipo (explicitos, como a P4 da UP-ARENA):
{rec}
   Os numeros sao do jogo; o uso deles na luta e PROPOSTO ate a LP5. */
import type {{ DadosForma }} from "./tipos.ts";

export const FORMAS_ARENA: Readonly<Record<string, DadosForma>> = {{
{chr(10).join(linhas)}
}};
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", type=Path, default=DADOS_PADRAO)
    ap.add_argument("--conferir", action="store_true")
    a = ap.parse_args()
    txt = gerar(a.dados)
    if a.conferir:
        if SAIDA.read_text(encoding="utf-8") != txt:
            falha(f"{SAIDA} difere do que o gerador produz agora")
        print("formas.ts confere")
        return
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(txt, encoding="utf-8", newline="\n")
    print(f"escrito {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    sys.exit(main())
