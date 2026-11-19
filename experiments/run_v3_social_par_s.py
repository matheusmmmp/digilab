"""SOCIAL_PAR S: o substrato que deixa o social aparecer (docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md, APROVADO pelo Matheus em 2026-11-18,
"Aprovado", com o adendo 1, "Aprovo o adendo 1").

Tres bracos, que mudam so o que acontece no t0 (o resto e a vida do A0: o modular com a CO7 nos dois, o dono atencioso no comedouro,
5 dias, o t0 sorteado nos dias 1 a 3, a janela de 96 decisoes):
- C: F levado a D0 = 5 celulas de P (o adendo 1, A1-1), pela perturbacao de tupla da E1 e do A0;
- B1: P levado a um ponto Q do campo ou da mata, e F a D0 de Q, fora da casa; os dois acordados (o `levar_pet` recusa quem dorme); as
  vidas base tambem levam P a Q, para a gravacao de P comecar la;
- B2: F levado como no C, e a bola posta parada na posicao de P (o `deixar_bola_intervencao`); as vidas base tambem recebem a bola.

Cada par vive a base e a base-OUTRA (as gravacoes de P) e a VIVO, a GRAV e a OUTRA. O G-DET de cada braco troca P pelo `SeguidorPuro` da
E1 (base, VIVO e GRAV). Em todo par: o G-INSTR (a VIVO e a GRAV iguais ate o t0) e o G1 (a VIVO pelo `reproduzir_grupo`; a GRAV e a OUTRA
refeitas da gravacao lida do disco). O primario do A e o tempo ate o contato (o adendo 1, A1-2); o do B e o do A0.

As travas: o plano e o adendo APROVADOS, a faixa reservada, as bases e o K do plano, no maximo 4 processos, nada por cima, e o `pre_run`
no `main()` fora da fumaca.

    python experiments/run_v3_social_par_s.py --config experiments/configs/v3_social_par_s/fumaca.json --saida <pasta> --processos 2
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import observar_v3_social_par_s0 as s0  # noqa: E402
import pre_run  # noqa: E402
import resumir_v3_social_par_s0 as rs0  # noqa: E402
import run_v3_social_par_a0 as a0  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS, SementeSemPlano, unidades_derivadas  # noqa: E402
from bancada.rodar import _dump, _gravar, _sha  # noqa: E402
from digilab import metrics as mt  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA  # noqa: E402
from digilab.grupo import RegistroGrupo, reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.mundo import celula_de, centro_da_celula, deslocar, distancia  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md"
FASE = "social_par_s"
CM, CCO, CI = a0.CM, a0.CCO, a0.CI
DONO = a0.DONO
DIAS, PASSO, T0_MIN, T0_MAX = a0.DIAS, a0.PASSO, a0.T0_MIN, a0.T0_MAX
D0 = 5                                                        # o adendo 1, A1-1: dentro das 6 celulas da visao
JANELA = a0.JANELA                                            # 96 decisoes
RAIO_PERTO, RAIO_CONTATO = a0.RAIO_PERTO, a0.RAIO_CONTATO     # 6 e 1
DELTA_A, DELTA_B = a0.DELTA_A, a0.DELTA_B                     # 6 do plano: as do A0
MIN_CHUTES = a0.MIN_CHUTES
PA1_MIN, PA2_FRACAO, PA2_N, PA3_MIN, PB1_N = a0.PA1_MIN, a0.PA2_FRACAO, a0.PA2_N, a0.PA3_MIN, a0.PB1_N
CASA_X_MAX = CM.layout.regioes[0][2]                          # a casa vai da celula 0 a 15 em x (o layout mvp)
Q_X = (34, 60)                                                # 2: Q no campo ou na mata, em celulas
BRACOS = ("C", "B1", "B2")
PREFIXO = {"run": "social_par_s", "det": "social_par_s_det"}  # 4
BASES_RUN = tuple(range(103001, 103201))                      # 4, S-4: 200 bases, k = 1
BASES_DET = tuple(range(103301, 103351))                      # 4: o G-DET, 50 bases
BASES_TESTE = (101, 202, 303, 404, 505)
K = 1
FAIXA = (103001, 103400)                                      # 4, S-5
MAX_PROCESSOS = 4                                             # 9 (V3-D8)
ORQUESTRADOR = "experiments/run_v3_social_par_s.py"
SAIDA = "artifacts_v3_social_par_s/run"
CONDICOES = pc.CONDICOES


# ================================================================== as travas
def exigir_plano_aprovado() -> None:
    texto = (RAIZ / PLANO).read_text(encoding="utf-8")
    if "- **Status:** APROVADO pelo Matheus" not in texto:
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho")
    if "## 11. Adendo 1 (APROVADO pelo Matheus" not in texto:
        raise RuntimeError(f"o adendo 1 do plano {PLANO} nao esta APROVADO (d0 = 5 e o primario pelo contato)")


def exigir_faixa_reservada() -> None:
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (4)")


def modo_da_config(cfg: dict) -> str:
    """confere a config contra o plano: a fumaca so com as bases dos testes; a run com as bases e o K da secao 4 e os tres bracos"""
    modo = cfg.get("modo")
    bracos = cfg.get("bracos")
    if modo not in ("fumaca", "run") or not isinstance(bracos, list) or not bracos or any(b not in BRACOS for b in bracos):
        raise ValueError(f"config invalida: {cfg}")
    for chave in ("unidades", "det"):
        u = cfg.get(chave, {})
        if not isinstance(u.get("bases"), list) or u.get("k") != K:
            raise ValueError(f"config invalida em {chave!r} (as bases e k = {K}): {u}")
    if modo == "fumaca":
        todas = cfg["unidades"]["bases"] + cfg["det"]["bases"]
        if not all(b in BASES_TESTE for b in todas):
            raise SementeSemPlano(f"a fumaca so usa as bases dos testes (101...505): {todas}")
        return modo
    exigir_plano_aprovado()
    exigir_faixa_reservada()
    if tuple(cfg["unidades"]["bases"]) != BASES_RUN or tuple(cfg["det"]["bases"]) != BASES_DET:
        raise SementeSemPlano("as bases da run sao 103001...103200 e as do G-DET 103301...103350 (4)")
    if tuple(bracos) != BRACOS:
        raise ValueError(f"a run tem os tres bracos {BRACOS}: {bracos}")
    return modo


# ================================================================== os membros
def _seguidor(ident: str, ss: dict, gravar: bool = False) -> pc.Membro:
    """o controle positivo do G-DET (3): o `SeguidorPuro` da E1 no lugar do pet de hoje, com o mesmo dono e o mesmo motor"""
    _, fm = a0.fabricas_do_jogo(DONO, ss[ident], CCO)
    return pc.Membro(ident, "vivo", fm, lambda c: pc.SeguidorPuro(c), a0._dono(ss[ident]), DONO, "seguidor_puro", gravar=gravar)


def _fabricas(ss: dict, det: bool) -> dict:
    out = {i: a0.fabricas_do_jogo(DONO, ss[i], CCO) for i in ("A", "B")}
    if det:
        out["B"] = (lambda c: pc.SeguidorPuro(c), out["B"][1])
    return out


# ================================================================== a intervencao de cada braco (2 e o adendo 1)
def _cabe(x: int, y: int, direcao: int, r: int) -> bool:
    """o ponto a r subunidades na direcao cai no mapa sem corte e fora da casa"""
    px, py = deslocar(x, y, direcao, r, CM)
    return distancia(px - x, py - y) >= r - 1 and celula_de(px, py, CM)[0] > CASA_X_MAX


def sortear_q(semente: int) -> tuple[tuple[int, int], int]:
    """o B1: Q (o centro de uma celula com x em 34..60) e a direcao de F a partir de Q, de uma rng propria do braco; a direcao e uma das
    16 em que F cai a D0 de Q sem corte e fora da casa"""
    rng = random.Random(derivar_semente("social-par-s-q", semente))
    q = centro_da_celula((rng.randint(*Q_X), rng.randrange(CM.celulas_y)), CM)
    viaveis = [d for d in range(16) if _cabe(*q, d, D0 * CM.sub)]
    if not viaveis:
        raise RuntimeError(f"B1: nenhuma direcao cabe a {D0} celulas de {q}")
    return q, rng.choice(viaveis)


def contexto(braco: str, semente: int) -> dict:
    """o que o t0 do par precisa, sorteado antes da vida (o t0 e a direcao do A0; Q e a direcao de F no B1)"""
    t0, direcao = pc.sortear_perturbacao(semente, T0_MIN, T0_MAX, PASSO)
    ctx = {"braco": braco, "t0": t0, "direcao": direcao, "q": None}
    if braco == "B1":
        q, ctx["direcao"] = sortear_q(semente)
        ctx["q"] = list(q)
    return ctx


def _intervencao(ctx: dict, base: bool) -> dict:
    """os argumentos do `viver_par` para a vida (a perturbacao de tupla no C; a IntervencaoT0 no B1 e no B2)"""
    braco, t0, direcao = ctx["braco"], ctx["t0"], ctx["direcao"]
    if braco == "C":
        return {} if base else {"perturbacao": ("A", "B", t0, direcao, D0)}
    if braco == "B1":
        qx, qy = ctx["q"]
        fx, fy = deslocar(qx, qy, direcao, D0 * CM.sub, CM)

        def b1(g, _base=base):
            g.levar_pet("B", qx, qy)
            if not _base:
                g.levar_pet("A", fx, fy)
        return {"intervencao": pc.IntervencaoT0(t0, ("A", "B"), b1, None if base else "A")}
    if braco == "B2":
        def b2(g, _base=base):
            px, py = g.motores["B"].pet
            if not _base:
                x, y = deslocar(px, py, direcao, D0 * CM.sub, CM)
                g.levar_pet("A", x, y)
            g.deixar_bola_intervencao("B", px, py)
        return {"intervencao": pc.IntervencaoT0(t0, ("A",), b2, None if base else "A")}
    raise ValueError(f"braco desconhecido: {braco!r}")


def viver(s: int, membros: list, ctx: dict, base: bool) -> pc.VidaPar:
    return pc.viver_par(CM, s, membros, DIAS, cfg_intervencao=CI, cfg_cooperacao=CCO, **_intervencao(ctx, base))


# ================================================================== as medidas de uma condicao (5 e o adendo 1)
def _janela(v: pc.VidaPar) -> dict:
    """as medidas do A0 na janela, mais o tempo ate o contato como o T*c do adendo (o `tempo_restrito` com o raio 1), onde o contato
    aconteceu (fora da casa?) e os chutes por dia na vida inteira"""
    j = a0._janela(v)
    j["chutes_por_dia"] = {i: len(pc.chutes(v, i)) / DIAS for i in ("A", "B")}
    if not j["cabe"]:
        return j
    k = j["passo"]
    j["t_contato_c"] = j["t_contato"]
    if not j["censurado_contato"]:
        kk = k + j["t_contato"]
        j["contato_fora_da_casa"] = all(celula_de(*v.posicoes[i][kk], CM)[0] > CASA_X_MAX for i in ("A", "B"))
    else:
        j["contato_fora_da_casa"] = None
    return j


# ================================================================== um par (o trabalho de um processo)
def _gravar_disco(arquivo: Path, disco: dict) -> None:
    """o .json.gz com o cabecalho do gzip sem hora nem nome (mtime = 0): o mesmo par da o mesmo arquivo, byte a byte"""
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo, "wb") as bruto, gzip.GzipFile(filename="", mode="wb", compresslevel=6, fileobj=bruto, mtime=0) as gz:
        gz.write(json.dumps(disco, sort_keys=True).encode("utf-8"))


def g1(s: int, ss: dict, ctx: dict, det: bool, vivo: pc.VidaPar, condicoes: dict, arquivo: Path) -> None:
    """o G1: a VIVO pelo `reproduzir_grupo` (as causas de fora: o dono e a intervencao), e as outras condicoes refeitas da gravacao lida
    do disco, com o mesmo registro e as mesmas posicoes"""
    lido = RegistroGrupo.de_jsonl(vivo.grupo.registro.para_jsonl())
    r = reproduzir_grupo(lido, _fabricas(ss, det), CM, cfg_cooperacao=CCO, cfg_intervencao=CI)
    if r.registro != vivo.grupo.registro or [tuple(r.motores[i].pet) for i in "AB"] != [tuple(vivo.grupo.motores[i].pet) for i in "AB"]:
        raise RuntimeError(f"G1: a VIVO do par {s} ({ctx['braco']}) nao se refaz pelo replay")
    with gzip.open(arquivo, "rt", encoding="utf-8") as f:
        disco = json.load(f)
    if disco["contexto"] != ctx:
        raise RuntimeError(f"G1: o contexto do disco do par {s} nao e o da vida")
    for nome, chave in (("GRAV", "base"), ("OUTRA", "base_outra")):
        if nome not in condicoes:
            continue
        gravacao, eventos = a0._gravacao_do_disco(disco["gravacoes"][chave])
        w = viver(s, [a0._vivo("A", ss), a0._gravado("B", ss, gravacao, eventos)], ctx, base=False)
        if a0._sha_vida(w) != a0._sha_vida(condicoes[nome]) or a0._sha_vida(w) != disco["sha256"][nome]:
            raise RuntimeError(f"G1: a {nome} do par {s} ({ctx['braco']}) nao se refaz da gravacao do disco")


def par(u: dict, pasta: str) -> dict:
    """as vidas de um par de um braco (cinco; tres no G-DET), o G-INSTR, o G1 e as medidas"""
    s, braco, det = u["semente"], u["braco"], u["det"]
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    ctx = contexto(braco, s)
    p = _seguidor if det else a0._vivo
    base = viver(s, [a0._vivo("A", ss), p("B", ss, gravar=True)], ctx, base=True)
    vivo = viver(s, [a0._vivo("A", ss), p("B", ss)], ctx, base=False)
    grav = viver(s, [a0._vivo("A", ss), a0._gravado("B", ss, base.gravacoes["B"], pc.eventos_do_dono(base.grupo, "B"))], ctx, base=False)
    condicoes = {"VIVO": vivo, "GRAV": grav}
    gravacoes = {"base": a0._gravacao_em_disco(base)}
    if not det:
        base_outra = viver(s, [a0._passivo("A", ss), a0._vivo("B", ss, gravar=True)], ctx, base=True)
        condicoes["OUTRA"] = viver(s, [a0._vivo("A", ss), a0._gravado("B", ss, base_outra.gravacoes["B"],
                                                                     pc.eventos_do_dono(base_outra.grupo, "B"))], ctx, base=False)
        gravacoes["base_outra"] = a0._gravacao_em_disco(base_outra)
    a0.g_instr(vivo, grav)
    nome = f"{'DET-' if det else ''}{braco}-{u['base']}-{u['k']:04d}"
    disco = {"par": nome, "semente": s, "contexto": ctx, "gravacoes": gravacoes,
             "sha256": {c: a0._sha_vida(v) for c, v in condicoes.items()}}
    arquivo = Path(pasta) / "vidas" / f"{nome}.json.gz"
    _gravar_disco(arquivo, disco)
    g1(s, ss, ctx, det, vivo, condicoes, arquivo)
    out = {"par": nome, "braco": braco, "det": det, "base": u["base"], "k": u["k"], "semente": s, "contexto": ctx,
           "condicoes": {c: _janela(v) for c, v in condicoes.items()}, "no_t0": vivo.no_t0, "g_instr": True, "g1": True,
           "arquivo_sha256": _sha(arquivo)}
    if not det:
        out["riqueza"] = s0.observar_vida(vivo, nome)
    return out


def _executar(trabalhos: list[dict], pasta: str, processos: int) -> list[dict]:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8 e secao 9)")
    if processos <= 1:
        return [par(u, pasta) for u in trabalhos]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        return [f.result() for f in [pool.submit(par, u, pasta) for u in trabalhos]]


def trabalhos(cfg: dict) -> list[dict]:
    """as unidades de cada braco: as mesmas sementes nos tres (4, S-4), e as do G-DET"""
    run = unidades_derivadas(cfg["unidades"]["bases"], K, PREFIXO["run"])
    det = unidades_derivadas(cfg["det"]["bases"], K, PREFIXO["det"])
    return ([{**u, "braco": b, "det": False} for b in cfg["bracos"] for u in run]
            + [{**u, "braco": b, "det": True} for b in cfg["bracos"] for u in det])


# ================================================================== a analise (5, 7 e o adendo 1)
def elegivel_a(r: dict) -> bool:
    v, g = r["condicoes"]["VIVO"], r["condicoes"]["GRAV"]
    return v["cabe"] and g["cabe"] and v["distancia_no_t0"] > RAIO_CONTATO


def d_a(r: dict) -> float:
    return float(r["condicoes"]["VIVO"]["t_contato_c"] - r["condicoes"]["GRAV"]["t_contato_c"])


def premissas(registros: list[dict]) -> dict:
    """5.1 com o adendo 1: a PA-2 pela distancia > 1 no t0, a PA-3 pelo contato na janela; a PB-1 a do A0"""
    n = len(registros)
    cabe = [r for r in registros if a0._cabe(r)]
    ea = [r for r in cabe if elegivel_a(r)]
    espaco = [r for r in ea if not (r["condicoes"]["VIVO"]["censurado_contato"] and r["condicoes"]["GRAV"]["censurado_contato"])]
    eb = [r for r in cabe if a0.elegivel_b(r) and a0.d_b(r) is not None]
    f = lambda a, b: None if not b else len(a) / len(b)  # noqa: E731
    pa1 = {"n_pares": n, "n_cabe": len(cabe), "fracao": f(cabe, registros), "minimo": PA1_MIN}
    pa2 = {"n_elegiveis": len(ea), "fracao": f(ea, cabe), "minimo_fracao": PA2_FRACAO, "minimo_n": PA2_N}
    pa3 = {"n_com_contato": len(espaco), "fracao": f(espaco, ea), "minimo": PA3_MIN}
    pb1 = {"n_elegiveis": len(eb), "fracao": f(eb, cabe), "minimo_n": PB1_N}
    pa1["passa"] = pa1["fracao"] is not None and pa1["fracao"] >= PA1_MIN
    pa2["passa"] = pa2["fracao"] is not None and pa2["fracao"] >= PA2_FRACAO and len(ea) >= PA2_N
    pa3["passa"] = pa3["fracao"] is not None and pa3["fracao"] >= PA3_MIN
    pb1["passa"] = len(eb) >= PB1_N
    return {"PA-1": pa1, "PA-2": pa2, "PA-3": pa3, "PB-1": pb1,
            "A_conclusivo": pa1["passa"] and pa2["passa"] and pa3["passa"], "B_conclusivo": pa1["passa"] and pb1["passa"]}


def primarios(registros: list[dict]) -> dict:
    ea = [r for r in registros if elegivel_a(r)]
    eb = [r for r in registros if a0.elegivel_b(r) and a0.d_b(r) is not None]
    return {"A": {"medida": "D_A = T*c_VIVO - T*c_GRAV (o tempo ate o contato, em decisoes; negativo = F e P se tocam mais depressa "
                            "com P que responde)", **a0._contraste([d_a(r) for r in ea], DELTA_A)},
            "B": {"medida": "D_B = E_VIVO - E_GRAV (o excesso de alternancia de F para P sobre os substitutos)",
                  **a0._contraste([a0.d_b(r) for r in eb], DELTA_B)}}


def secundarios(registros: list[dict]) -> dict:
    """5 com o adendo 1: o S1 sobre o T*c (GRAV - OUTRA), o S2 e o S3 os do A0; o Holm na familia dos tres"""
    ea = [r for r in registros if elegivel_a(r)]
    c = lambda r, n: r["condicoes"][n]  # noqa: E731
    s1 = [float(c(r, "GRAV")["t_contato_c"] - c(r, "OUTRA")["t_contato_c"]) for r in ea if c(r, "OUTRA")["cabe"]]
    s2 = [c(r, "VIVO")["fracao_perto"] - c(r, "GRAV")["fracao_perto"] for r in ea]
    s3p = [r for r in ea if c(r, "VIVO")["contingencia_FP"] is not None and c(r, "GRAV")["contingencia_FP"] is not None]
    s3 = [c(r, "VIVO")["contingencia_FP"] - c(r, "GRAV")["contingencia_FP"] for r in s3p]
    out = {"S1_GRAV_menos_OUTRA": {**a0._contraste(s1, None), "fora": len(ea) - len(s1)},
           "S2_fracao_perto": {**a0._contraste(s2, None), "fora": 0},
           "S3_contingencia_FP": {**a0._contraste(s3, None), "fora": len(ea) - len(s3)}}
    h = mt.holm({k: v["p_bilateral"] for k, v in out.items()}, a0.ALFA_SECUNDARIOS)
    for k in out:
        out[k]["holm"] = h[k]
    return out


def g_det(det: list[dict]) -> dict:
    """3: o controle positivo passa com o IC95 do D_A todo abaixo de -delta_A"""
    ea = [r for r in det if elegivel_a(r)]
    c = a0._contraste([d_a(r) for r in ea], DELTA_A)
    hi = c["ic95"][1]
    return {**c, "n_pares": len(det), "limiar": -DELTA_A, "passa": hi is not None and hi < -DELTA_A}


LEITURA_A = {"cego": "o substrato nao deixa ver: o braco nao diz nada sobre o pet de hoje",
             "≈ 0": "nulo com um instrumento que ve: o pet de hoje nao responde ao parceiro neste substrato",
             "< 0": "o social aparece: o parceiro que responde aproxima o contato",
             "> 0": "o social aparece: o parceiro que responde afasta o contato",
             "indeterminado": "registrado como esta; nada se decide"}


def leitura_braco(prem: dict, prims: dict, gdet: dict) -> dict:
    """7: o G-DET primeiro, depois a premissa e a classe"""
    if not gdet["passa"]:
        a = {"classe": "cego", "texto": LEITURA_A["cego"]}
    elif not prem["A_conclusivo"]:
        a = {"classe": "inconclusivo por premissa", "texto": "registrado como esta; nada se decide com ele"}
    else:
        a = {"classe": prims["A"]["classe"], "texto": LEITURA_A[prims["A"]["classe"]]}
    b = ({"classe": "inconclusivo por premissa", "texto": "a PB-1 falha: o braco nao deu substrato para a bola"} if not prem["B_conclusivo"]
         else {"classe": prims["B"]["classe"], "texto": "a classe do D_B pela margem, sem G-DET (3)"})
    return {"A": a, "B": b}


def leitura_conjunto(por_braco: dict) -> dict:
    """7, o conjunto"""
    la = {b: x["leitura"]["A"]["classe"] for b, x in por_braco.items()}
    if "B1" in la and la["B1"] == "≈ 0":
        texto = "o social nao existe no pet de hoje, mesmo num substrato que o deixa ver: o proximo passo e mecanismo (M1-M4)"
    elif any(c in ("< 0", "> 0") for c in la.values()):
        texto = "o substrato resolveu: o proximo passo e descrever esse caminho antes do M1"
    elif la.get("B1") == "cego" and la.get("C") == "cego":
        texto = "o substrato ainda nao deixa ver: a S2 precisa de mais bracos, numa rodada nova com plano novo"
    else:
        texto = "nenhuma das tres linhas da secao 7 se aplica: registrado como esta"
    return {"classes_A": la, "texto": texto}


def _media(xs: list):
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def substrato(registros: list[dict]) -> dict:
    """5, as medidas do substrato (descritivas, sem gate)"""
    ea = [r for r in registros if elegivel_a(r)]
    c = lambda r, n: r["condicoes"][n]  # noqa: E731
    return {"t_contato_GRAV_media": _media([c(r, "GRAV")["t_contato_c"] for r in ea]),
            "t_contato_VIVO_media": _media([c(r, "VIVO")["t_contato_c"] for r in ea]),
            "t_perto_GRAV_media": _media([c(r, "GRAV")["t_perto"] for r in ea]),
            "distancia_no_t0_media": _media([c(r, "VIVO")["distancia_no_t0"] for r in ea]),
            "contato_fora_da_casa_VIVO": _media([None if c(r, "VIVO")["contato_fora_da_casa"] is None
                                                 else float(c(r, "VIVO")["contato_fora_da_casa"]) for r in ea]),
            "chutes_por_dia_VIVO": {i: _media([c(r, "VIVO")["chutes_por_dia"][i] for r in registros]) for i in ("A", "B")},
            "chutes_na_janela_VIVO": {i: _media([c(r, "VIVO")["chutes"][i] for r in registros if c(r, "VIVO")["cabe"]]) for i in "AB"},
            "desvios_P_janela_GRAV": _media([c(r, "GRAV")["desvios_P_janela"].get("alvo_fora", 0) for r in registros])}


def riqueza(registros: list[dict]) -> dict:
    """5, o que os dois fazem juntos (as medidas da S0, nas VIVO do braco); o "quem fecha a distancia" e None quando nenhum par comeca
    fora do raio perto (o d0 = 5 do adendo 1 ja comeca dentro)"""
    obs = [r["riqueza"] for r in registros]
    return {"presenca": {"F": rs0.presenca(obs, "A"), "P": rs0.presenca(obs, "B")}, "juntos": rs0.juntos(obs),
            "fecha_a_distancia": (rs0.fecha(obs) if sum(o["fecha_a_distancia"].get("passos", 0) for o in obs) else None),
            "mundo": rs0.mundo(obs), "distancia": rs0.distancia(obs)}


def analisar(registros: list[dict]) -> dict:
    if not all(r["g_instr"] and r["g1"] for r in registros):
        raise RuntimeError("um par sem o G-INSTR ou o G1: a run nao se le (8)")
    por_braco = {}
    for b in BRACOS:
        rr = [r for r in registros if r["braco"] == b and not r["det"]]
        dd = [r for r in registros if r["braco"] == b and r["det"]]
        if not rr:
            continue
        prem, prims, gd = premissas(rr), primarios(rr), g_det(dd)
        por_braco[b] = {"pares": len(rr), "premissas": prem, "primarios": prims, "secundarios": secundarios(rr), "g_det": gd,
                        "leitura": leitura_braco(prem, prims, gd), "substrato": substrato(rr), "riqueza": riqueza(rr)}
    return {"bracos": por_braco, "conjunto": leitura_conjunto(por_braco)}


# ================================================================== a run
def meta_inicial(cfg: dict, modo: str, tt: list[dict], processos: int, caminho_config: Path | None) -> dict:
    m = a0.meta_inicial(cfg, modo, tt, processos, caminho_config)
    m.update({"fase": FASE, "plano": PLANO, "plano_sha256": _sha(RAIZ / PLANO), "orquestrador_sha256": _sha(Path(__file__)),
              "orquestrador_a0_sha256": _sha(Path(a0.__file__)), "observar_s0_sha256": _sha(Path(s0.__file__)), "d0": D0,
              "comando": " ".join(["python"] + sys.argv)})
    return m


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez)")
    tt = trabalhos(cfg)
    pasta.mkdir(parents=True)
    meta = meta_inicial(cfg, modo, tt, processos, caminho_config)
    _gravar(pasta / "meta.json", _dump(meta))
    t = time.perf_counter()
    registros = _executar(tt, str(pasta), processos)
    meta["vidas_parede_s"] = time.perf_counter() - t
    meta["vidas"] = sum(3 if r["det"] else 5 for r in registros)
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if len(registros) != len(tt):
        raise RuntimeError(f"{len(registros)} pares, eram {len(tt)}")
    _gravar(pasta / "medidas.json", _dump({r["par"]: r for r in sorted(registros, key=lambda r: r["par"])}))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "pares": len(lidos), **analisar(list(lidos.values()))}
    _gravar(pasta / "resultado.json", _dump(resultado))
    meta["artefatos_sha256"] = {n: _sha(pasta / n) for n in ("medidas.json", "resultado.json")}
    _gravar(pasta / "meta.json", _dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if cfg.get("modo") == "fumaca":
        if a.saida is None:
            raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    else:
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)          # o H10 (D-IA-6: o plano na origin/main) e a V3-D8, antes de tudo
    r = rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]
    print(json.dumps({"conjunto": r["conjunto"], **{b: {"leitura": x["leitura"], "g_det": {k: x["g_det"][k] for k in ("ic95", "passa")}}
                                                     for b, x in r["bracos"].items()}}, indent=1, ensure_ascii=True, default=str))


if __name__ == "__main__":
    main()
