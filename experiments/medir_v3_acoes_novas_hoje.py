"""AN0 da ACOES_NOVAS (docs/TAREFA_V3_ACOES_NOVAS.md, secao 3.6): o descritivo de HOJE, sem vida nova.

Le so as vidas ja gravadas do DigiBrain modular (braco REL da C4, sementes dos testes), em `web/app/test/gabaritos/`:
  - `digibrain_modular_comedouro.json.gz` e `digibrain_modular_longe_fixo.json.gz` (LM0): por decisao, as chamadas dos modulos e o motivo;
    daqui saem a posicao do pet (a entrada do `adapt.agir`) e, portanto, o deslocamento;
  - `digibrain_modular_fins.json.gz` (LM4): o motivo por decisao de 6 vidas (sem a posicao).
Nenhum motor roda, nenhuma semente nova, nenhuma faixa. **Nenhum numero vira resultado: e descritivo** (a AN0 so diz de onde a AN-2 parte).

Medidas (por fonte, lugar e dono, e o total):
  1. a fracao de decisoes `explorar/vagar`, e a mistura das escolhas;
  2. as corridas de vagar seguidas (numero, comprimento medio e maximo, histograma);
  3. o deslocamento por decisao (unidades de posicao do mundo, distancia euclidiana, entre a posicao da decisao k e a da k+1), por classe
     da escolha (vagar, outro explorar, nao explorar), a fracao de decisoes sem sair do lugar, e o zigue-zague do vagar seguido (a [HIPOTESE]
     da secao 2.1: a fracao dos pares de vagar seguidos cujo passo inverte o anterior; a razao deslocamento liquido / caminho da corrida);
  4. a urgencia maxima nas decisoes de vagar (`afeto.urgencias`; fome, higiene, energia e saude, o conjunto da AN-4, e todas), contra o
     `urgencia_lambda` de hoje;
  5. a conferencia da 3.3: o gesto do dono entra no r? Quais gestos as vidas gravadas trazem, e o r da opcao que os recebeu; e, pela
     configuracao, quais canais fazem o r (`fora_do_r`).

    python experiments/medir_v3_acoes_novas_hoje.py            # grava artifacts_v3_acoes_novas/hoje.json
    python experiments/medir_v3_acoes_novas_hoje.py --conferir # gera de novo e compara com o gravado (o gate: sai igual)
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN  # noqa: E402

PASTA_GAB = RAIZ / "web" / "app" / "test" / "gabaritos"
SAIDA = RAIZ / "artifacts_v3_acoes_novas" / "hoje.json"
FONTES = (
    ("lm0", "digibrain_modular_comedouro.json.gz"),
    ("lm0", "digibrain_modular_longe_fixo.json.gz"),
    ("lm4_fins", "digibrain_modular_fins.json.gz"),
)
VAGAR = ["explorar", "vagar"]
GUARDA_AN4 = ("fome", "higiene", "energia", "saude")     # AN-4: as necessidades da guarda
CASAS = 6


def _r(x: float) -> float:
    return round(x, CASAS)


def _media(xs: list) -> float | None:
    return _r(sum(xs) / len(xs)) if xs else None


def _classe(escolha: list) -> str:
    if escolha[:2] == VAGAR:
        return "vagar"
    return "outro_explorar" if escolha[0] == "explorar" else "nao_explorar"


def _posicao(dec: dict) -> tuple | None:
    """a posicao do pet na entrada do `adapt.agir` (so nos gabaritos da LM0, que trazem as chamadas)"""
    if "chamadas" not in dec:
        return None
    for c in dec["chamadas"]:
        if c["m"] == "adapt.agir":
            mundo = c["e"][0]["mundo"]
            if mundo is None:
                raise ValueError(f"decisao {dec['k']}: sem mundo na entrada do adapt.agir")
            return (mundo["x"], mundo["y"])
    raise ValueError(f"decisao {dec['k']}: sem adapt.agir")


def _corridas(flags: list) -> list:
    """(inicio, comprimento) de cada sequencia de decisoes de vagar seguidas"""
    out, ini = [], None
    for i, f in enumerate(flags + [False]):
        if f and ini is None:
            ini = i
        elif not f and ini is not None:
            out.append((ini, i - ini))
            ini = None
    return out


def _vida(v: dict) -> dict:
    """as contas de uma vida, em somas e listas (somadas depois por grupo)"""
    decs = sorted(v["decisoes"], key=lambda d: d["k"])
    ks = [d["k"] for d in decs]
    if ks != list(range(len(ks))):
        raise ValueError("decisoes fora de ordem ou com buraco")
    motivos = [d["motivo"] for d in decs]
    escolhas = [m["escolha"] for m in motivos]
    flags = [e[:2] == VAGAR for e in escolhas]
    pos = [_posicao(d) for d in decs]
    tem_pos = all(p is not None for p in pos)

    mistura: dict = {}
    for e in escolhas:
        chave = "/".join(str(x) for x in e if x is not None)
        mistura[chave] = mistura.get(chave, 0) + 1

    desloc = {"vagar": [], "outro_explorar": [], "nao_explorar": []}
    passos = []                                  # o vetor de cada decisao com k+1
    if tem_pos:
        for k in range(len(decs) - 1):
            dx, dy = pos[k + 1][0] - pos[k][0], pos[k + 1][1] - pos[k][1]
            passos.append((dx, dy))
            desloc[_classe(escolhas[k])].append(math.hypot(dx, dy))

    corridas = _corridas(flags)
    pares = inverte = 0
    liquido = caminho = 0.0
    if tem_pos:
        for k in range(len(passos) - 1):
            if flags[k] and flags[k + 1]:
                a, b = passos[k], passos[k + 1]
                if (a != (0, 0)) and (b != (0, 0)):
                    pares += 1
                    inverte += (a[0] * b[0] + a[1] * b[1]) < 0
        for ini, n in corridas:
            if n >= 2 and ini + n < len(pos):
                liquido += math.hypot(pos[ini + n][0] - pos[ini][0], pos[ini + n][1] - pos[ini][1])
                caminho += sum(math.hypot(*passos[k]) for k in range(ini, ini + n))

    urg_guarda, urg_todas = [], []
    for m, f in zip(motivos, flags):
        if f:
            u = m["afeto"]["urgencias"]
            urg_guarda.append(max(u[n] for n in GUARDA_AN4))
            urg_todas.append(max(u.values()))

    gestos = {}                                  # tipo -> [n, n com r != 0, soma do r]; o gesto de k+1 e do intervalo da opcao k
    sem_gesto = [0, 0]
    for k in range(len(decs) - 1):
        r = motivos[k]["consequencia"]["r"]
        tipos = [g[0] for g in motivos[k + 1]["gestos"]]
        if not tipos:
            sem_gesto[0] += 1
            sem_gesto[1] += r != 0
        for t in tipos:
            g = gestos.setdefault(t, [0, 0, 0])
            g[0] += 1
            g[1] += r != 0
            g[2] += r
    return {"n": len(decs), "n_vagar": sum(flags), "mistura": mistura, "tem_pos": tem_pos, "desloc": desloc,
            "corridas": [n for _, n in corridas], "pares": pares, "inverte": inverte, "liquido": liquido, "caminho": caminho,
            "urg_guarda": urg_guarda, "urg_todas": urg_todas, "gestos": gestos, "sem_gesto": sem_gesto}


def _somar(vidas: list) -> dict:
    n = sum(v["n"] for v in vidas)
    n_vagar = sum(v["n_vagar"] for v in vidas)
    mistura: dict = {}
    for v in vidas:
        for k, x in v["mistura"].items():
            mistura[k] = mistura.get(k, 0) + x
    corridas = [c for v in vidas for c in v["corridas"]]
    hist: dict = {}
    for c in corridas:
        faixa = str(c) if c < 5 else "5+"
        hist[faixa] = hist.get(faixa, 0) + 1
    out = {"vidas": len(vidas), "decisoes": n, "decisoes_vagar": n_vagar, "fracao_vagar": _r(n_vagar / n) if n else None,
           "mistura_das_escolhas": dict(sorted(mistura.items())),
           "corridas_de_vagar": {"n": len(corridas), "comprimento_medio": _media(corridas), "comprimento_maximo": max(corridas, default=0),
                                 "histograma": dict(sorted(hist.items())),
                                 "decisoes_em_corridas_de_2_ou_mais": sum(c for c in corridas if c >= 2)}}
    com_pos = [v for v in vidas if v["tem_pos"]]
    if com_pos:
        desloc = {}
        for cl in ("vagar", "outro_explorar", "nao_explorar"):
            xs = [d for v in com_pos for d in v["desloc"][cl]]
            desloc[cl] = {"n": len(xs), "media": _media(xs), "maximo": _r(max(xs)) if xs else None,
                          "fracao_sem_sair_do_lugar": _r(sum(1 for d in xs if d == 0) / len(xs)) if xs else None}
        pares = sum(v["pares"] for v in com_pos)
        caminho = sum(v["caminho"] for v in com_pos)
        out["deslocamento_por_decisao"] = desloc
        out["zigue_zague_do_vagar"] = {
            "pares_de_vagar_seguidos_com_passo": pares, "pares_que_invertem": sum(v["inverte"] for v in com_pos),
            "fracao_que_inverte": _r(sum(v["inverte"] for v in com_pos) / pares) if pares else None,
            "razao_liquido_sobre_caminho_nas_corridas_de_2_ou_mais": _r(sum(v["liquido"] for v in com_pos) / caminho) if caminho else None}
    else:
        out["deslocamento_por_decisao"] = None          # a fonte nao grava a posicao
        out["zigue_zague_do_vagar"] = None
    lam = CONFIG_DIGIBRAIN_INATOS.urgencia_lambda
    ug = [u for v in vidas for u in v["urg_guarda"]]
    ut = [u for v in vidas for u in v["urg_todas"]]
    out["urgencia_nas_decisoes_de_vagar"] = {
        "urgencia_lambda_de_hoje": lam,
        "guarda_an4": {"n": len(ug), "media": _media(ug), "maximo": max(ug, default=None),
                       "acima_do_lambda": sum(1 for u in ug if u > lam),
                       "fracao_acima_do_lambda": _r(sum(1 for u in ug if u > lam) / len(ug)) if ug else None},
        "todas_as_necessidades": {"media": _media(ut), "maximo": max(ut, default=None)}}
    gestos: dict = {}
    for v in vidas:
        for t, (a, b, c) in v["gestos"].items():
            g = gestos.setdefault(t, [0, 0, 0])
            g[0] += a
            g[1] += b
            g[2] += c
    out["gestos_do_dono"] = {
        "por_tipo": {t: {"opcoes": a, "com_r_diferente_de_0": b, "soma_do_r": c} for t, (a, b, c) in sorted(gestos.items())},
        "opcoes_sem_gesto": {"opcoes": sum(v["sem_gesto"][0] for v in vidas), "com_r_diferente_de_0": sum(v["sem_gesto"][1] for v in vidas)}}
    return out


def gerar() -> dict:
    grupos: dict = {}
    for fonte, nome in FONTES:
        with gzip.open(PASTA_GAB / nome, "rt", encoding="utf-8") as f:
            dados = json.load(f)
        for v in dados["vidas"]:
            lugar = v["lugar"]
            conta = _vida(v)
            for chave in (f"{fonte}|{lugar}|{v['dono']}", f"{fonte}|{lugar}|todos", f"{fonte}|todos|todos", "total"):
                grupos.setdefault(chave, []).append(conta)
    receptores_r = [r for r in RECEPTORES_DIGIBRAIN if r not in CONFIG_DIGIBRAIN_INATOS.fora_do_r]
    return {
        "nota": "AN0, descritivo de HOJE: so vidas ja gravadas (sementes dos testes); nenhum numero e resultado",
        "fontes": [f"web/app/test/gabaritos/{n}" for _, n in FONTES],
        "braco": "REL",
        "posicao": "unidades de posicao do mundo (x, y do Observacao.mundo); distancia euclidiana entre decisoes seguidas",
        "urgencia": "escala S = 1024 (afeto.urgencias)",
        "grupos": {k: _somar(vs) for k, vs in sorted(grupos.items())},
        "conferencia_3_3": {
            "fora_do_r": list(CONFIG_DIGIBRAIN_INATOS.fora_do_r),
            "canais_do_r": receptores_r,
            "solidao_e_estresse_no_r": ("solidao" in receptores_r) and ("estresse" in receptores_r),
            "gestos_de_carinho_ou_tapa_nas_vidas_gravadas": sorted(
                {t for g in grupos["total"] for t in g["gestos"] if t in ("acariciar", "elogiar", "repreender")}),
            "leitura": "o carinho baixa solidao e estresse no corpo (digilab/corpo.py, `ACARICIAR`), e os dois fazem o r (so o susto fica "
                       "fora); logo o canal existe pela configuracao. As vidas gravadas NAO trazem carinho nem tapa (so alimentar, limpar "
                       "e brincar), entao o efeito do carinho no r do vagar nao e observavel aqui sem vida nova: fica para o teste da AN2.",
        },
    }


def _texto(d: dict) -> str:
    return json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conferir", action="store_true", help="gera de novo e compara com o artefato gravado")
    args = ap.parse_args()
    texto = _texto(gerar())
    sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    if args.conferir:
        gravado = SAIDA.read_bytes().decode("utf-8")
        if gravado != texto:
            raise SystemExit(f"DIVERGE: gerado {sha}, gravado {hashlib.sha256(gravado.encode('utf-8')).hexdigest()}")
        print(f"igual ao gravado: sha256 {sha}")
        return
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    print(f"{SAIDA.relative_to(RAIZ)}  sha256 {sha}")


if __name__ == "__main__":
    main()
