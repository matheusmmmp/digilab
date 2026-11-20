"""SOCIAL_PAR MD: a medida do M1 e do M2 (docs/PLANO_ANALISE_V3_SOCIAL_PAR_MD.md, APROVADO pelo Matheus em 2026-11-19, "Aprovado").

O instrumento da S3 sem mudanca (o `run_v3_social_par_s.py`: as cinco vidas por par, o d0 = 5, o T*c, a delta_A = 4, o G-DET, o G-INSTR e o
G1), com os pets dos mecanismos no lugar do pet de hoje. Os dois pets do par recebem a mesma config (secao 2):
- M1: a `unidades_sociais`;
- M1-inc0: a `unidades_sociais` com a `incentivo_social_zero` (o controle do D-SP-63);
- M1+M2: a `unidades_sociais` e a `ConfigCompanhia` ligada;
- M1-inc0+M2: o controle do M1+M2 (o MD-2).
O HOJE (o pet da S3, sem mecanismo) so entra na fumaca, para o G-S3-IGUAL (secao 8). Os substratos sao o B1 e o C (o MD-4).

O que muda no par, contra a S3 (D-SP-74):
- o C leva F pela `IntervencaoT0` (no lugar da perturbacao de tupla, que faz o mesmo), para o retrato do t0 sair do mesmo gancho do B1;
- o retrato do t0: o desfecho social de cada pet com o DigiBrain, lido no gancho, antes do levar (a PM-1 e os descritivos);
- a VIVO de P vai embrulhada pelo `Gravador` (que nao muda a politica), para a frequencia das unidades sociais na janela.
O G-S3-IGUAL (um teste) confere que, com o HOJE, as vidas saem com o sha256 das da S3.

As travas: o plano APROVADO, a faixa reservada, as bases e o K do plano, os quatro mecanismos e os dois substratos, no maximo 4
processos, nada por cima, e o `pre_run` no `main()` fora da fumaca.

    python experiments/run_v3_social_par_md.py --config experiments/configs/v3_social_par_md/fumaca.json --saida <pasta> --processos 2
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import pre_run  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_social_par_a0 as a0  # noqa: E402
import run_v3_social_par_s as s  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS, SementeSemPlano, unidades_derivadas  # noqa: E402
from bancada.rodar import _dump, _gravar, _sha  # noqa: E402
from digilab.config import CONFIG_COMPANHIA_LIGADA, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, TIPOS_ALVO_SOCIAIS  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.grupo import RegistroGrupo, reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.mundo import deslocar  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_SOCIAL_PAR_MD.md"
FASE = "social_par_md"
CM, CCO, CI, DONO = s.CM, s.CCO, s.CI, s.DONO
D0, DELTA_A = s.D0, s.DELTA_A
M1 = {"unidades_sociais": True}
INC0 = {"unidades_sociais": True, "incentivo_social_zero": True}
COMP = {"cfg_companhia": CONFIG_COMPANHIA_LIGADA}
MECANISMOS = {"M1": (M1, None), "M1-inc0": (INC0, None), "M1+M2": (M1, COMP), "M1-inc0+M2": (INC0, COMP)}   # 2 (MD-2)
SO_FUMACA = {"HOJE": (None, None)}                                                                          # o G-S3-IGUAL (8)
COM_M2 = ("M1+M2", "M1-inc0+M2")
BRACOS = ("B1", "C")                                                                                        # 2 (MD-4)
PREFIXO = {"run": "social_par_md", "det": "social_par_md_det"}                                              # 4
BASES_RUN = tuple(range(105001, 105201))                                                                    # 4 (MD-5): 200 bases, k = 1
BASES_DET = tuple(range(105301, 105351))                                                                    # 4: o G-DET, 50 bases
BASES_TESTE = s.BASES_TESTE
K = 1
FAIXA = (105001, 105400)                                                                                    # 4 (MD-5)
PM1_MIN = 0.5                                                                                               # 5 (MD-6), SEM FONTE
MAX_PROCESSOS = 4                                                                                           # 9 (V3-D8)
ORQUESTRADOR = "experiments/run_v3_social_par_md.py"
SAIDA = "artifacts_v3_social_par_md/run"


# ================================================================== as travas
def exigir_plano_aprovado() -> None:
    if "- **Status:** APROVADO pelo Matheus" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho")


def exigir_faixa_reservada() -> None:
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (4)")


def modo_da_config(cfg: dict) -> str:
    """confere a config contra o plano: a fumaca so com as bases dos testes (e o HOJE so nela); a run com as bases e o K da secao 4, os
    quatro mecanismos e os dois substratos"""
    modo, bracos, mecs = cfg.get("modo"), cfg.get("bracos"), cfg.get("mecanismos")
    validos = {**MECANISMOS, **SO_FUMACA} if modo == "fumaca" else MECANISMOS
    if (modo not in ("fumaca", "run") or not isinstance(bracos, list) or not bracos or any(b not in BRACOS for b in bracos)
            or not isinstance(mecs, list) or not mecs or any(m not in validos for m in mecs) or len(set(mecs)) != len(mecs)):
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
        raise SementeSemPlano("as bases da run sao 105001...105200 e as do G-DET 105301...105350 (4)")
    if tuple(bracos) != BRACOS or tuple(mecs) != tuple(MECANISMOS):
        raise ValueError(f"a run tem os substratos {BRACOS} e os mecanismos {tuple(MECANISMOS)}: {bracos}, {mecs}")
    return modo


# ================================================================== os pets de cada mecanismo
def fabricas(mec: str, semente_pet: int):
    """(a fabrica do cerebro, a do motor) do pet do mecanismo: o pet do jogo da S (`a0.fabricas_do_jogo`) com a ConfigDigibrain do
    mecanismo e, nos bracos com o M2, a ConfigCompanhia no motor. O HOJE e o `a0.fabricas_do_jogo` sem mudanca"""
    if mec in SO_FUMACA:
        return a0.fabricas_do_jogo(DONO, semente_pet, CCO)
    cd_extra, motor_extra = MECANISMOS[mec]
    _, fm0 = a0.fabricas_do_jogo(DONO, semente_pet, CCO)
    cd = replace(orq.config_do_braco(a0.e6.BRACO, conserto=True), **cd_extra)
    mk = dict(motor_extra or {})

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cd, a0.e6.CM, semente=semente_pet, cfg_cooperacao=CCO)

    def fm(pol, cfg, sm, **kw):
        return fm0(pol, cfg, sm, **kw, **mk)
    return fp, fm


def _vivo(mec: str, ident: str, ss: dict, gravar: bool = False) -> pc.Membro:
    fp, fm = fabricas(mec, ss[ident])
    return pc.Membro(ident, "vivo", fm, fp, a0._dono(ss[ident]), DONO, "digibrain", gravar=gravar)


def _passivo(mec: str, ident: str, ss: dict) -> pc.Membro:
    _, fm = fabricas(mec, ss[ident])
    return pc.Membro(ident, "vivo", fm, lambda c: pc.Passivo(c), a0._dono(ss[ident]), DONO, "passivo")


def _gravado(mec: str, ident: str, ss: dict, gravacao: list, eventos: list) -> pc.Membro:
    _, fm = fabricas(mec, ss[ident])
    return pc.Membro(ident, "gravado", fm, gravacao=gravacao, eventos_dono=eventos, rotulo_dono=DONO, rotulo_cerebro="gravada")


def _seguidor(mec: str, ident: str, ss: dict, gravar: bool = False) -> pc.Membro:
    """o controle positivo do G-DET (3): o `SeguidorPuro` no lugar de P, com o motor do mecanismo (o corpo sente a companhia)"""
    _, fm = fabricas(mec, ss[ident])
    return pc.Membro(ident, "vivo", fm, lambda c: pc.SeguidorPuro(c), a0._dono(ss[ident]), DONO, "seguidor_puro", gravar=gravar)


def _fabricas_replay(mec: str, ss: dict, det: bool) -> dict:
    out = {i: fabricas(mec, ss[i]) for i in ("A", "B")}
    if det:
        out["B"] = (lambda c: pc.SeguidorPuro(c), out["B"][1])
    return out


# ================================================================== o t0 (2 e D-SP-74)
def retrato_social(g) -> dict:
    """o desfecho social de cada pet com o DigiBrain (o P1 das classes `seguir` e `onde_comeu`, por receptor) e a solidao do corpo, no
    gancho do t0, antes do levar; um pet sem P1 social (o HOJE, o seguidor) fica de fora"""
    out = {}
    for i, m in sorted(g.motores.items()):
        pl = getattr(getattr(getattr(m.politica, "m", None), "plast", None), "desfecho", None)
        if pl is None or not all(c in pl for c in TIPOS_ALVO_SOCIAIS):
            continue
        plast = m.politica.m.plast
        out[i] = {"receptores": list(plast.receptores), "desfecho": {c: list(plast.desfecho[c]) for c in TIPOS_ALVO_SOCIAIS},
                  "solidao": m.corpo.q.get("solidao") if getattr(m, "corpo", None) is not None else None}
    return out


def _intervencao(ctx: dict, base: bool, retrato: dict) -> dict:
    """os argumentos do `viver_par`: o C pela `IntervencaoT0` (o mesmo levar da perturbacao de tupla da S: F acordado, a D0 de P na
    direcao), o B1 o da S; nos dois, o retrato do t0 antes do levar"""
    braco, t0, direcao = ctx["braco"], ctx["t0"], ctx["direcao"]
    if braco == "C":
        if base:
            return {}

        def c(g):
            retrato.update(retrato_social(g))
            px, py = g.motores["B"].pet
            x, y = deslocar(px, py, direcao, D0 * CM.sub, CM)
            g.levar_pet("A", x, y)
        return {"intervencao": pc.IntervencaoT0(t0, ("A",), c, "A")}
    if braco == "B1":
        orig = s._intervencao(ctx, base)["intervencao"]

        def b1(g, _f=orig.aplicar):
            retrato.update(retrato_social(g))
            _f(g)
        return {"intervencao": pc.IntervencaoT0(orig.t0, orig.acordados, b1, orig.levado)}
    raise ValueError(f"braco desconhecido: {braco!r}")


def viver(sm: int, membros: list, ctx: dict, base: bool, retrato: dict | None = None) -> pc.VidaPar:
    return pc.viver_par(CM, sm, membros, s.DIAS, cfg_intervencao=CI, cfg_cooperacao=CCO,
                        **_intervencao(ctx, base, {} if retrato is None else retrato))


def frequencia_social(decisoes: list, de: int, ate: int) -> dict:
    """as decisoes de P com um alvo social (o tipo do alvo resolvido), entre os indices [de, ate)"""
    dd = [d for d in decisoes if de <= d.indice < ate]
    n = sum(1 for d in dd if d.alvo is not None and d.alvo.tipo in TIPOS_ALVO_SOCIAIS)
    return {"decisoes": len(dd), "sociais": n, "fracao": None if not dd else n / len(dd)}


# ================================================================== um par (o trabalho de um processo)
def g1(sm: int, ss: dict, ctx: dict, mec: str, det: bool, vivo: pc.VidaPar, condicoes: dict, arquivo: Path) -> None:
    """o G1 da S: a VIVO pelo `reproduzir_grupo`, e a GRAV e a OUTRA refeitas da gravacao lida do disco"""
    import gzip
    lido = RegistroGrupo.de_jsonl(vivo.grupo.registro.para_jsonl())
    r = reproduzir_grupo(lido, _fabricas_replay(mec, ss, det), CM, cfg_cooperacao=CCO, cfg_intervencao=CI)
    if r.registro != vivo.grupo.registro or [tuple(r.motores[i].pet) for i in "AB"] != [tuple(vivo.grupo.motores[i].pet) for i in "AB"]:
        raise RuntimeError(f"G1: a VIVO do par {sm} ({mec}, {ctx['braco']}) nao se refaz pelo replay")
    with gzip.open(arquivo, "rt", encoding="utf-8") as f:
        disco = json.load(f)
    if disco["contexto"] != ctx:
        raise RuntimeError(f"G1: o contexto do disco do par {sm} nao e o da vida")
    for nome, chave in (("GRAV", "base"), ("OUTRA", "base_outra")):
        if nome not in condicoes:
            continue
        gravacao, eventos = a0._gravacao_do_disco(disco["gravacoes"][chave])
        w = viver(sm, [_vivo(mec, "A", ss), _gravado(mec, "B", ss, gravacao, eventos)], ctx, base=False)
        if a0._sha_vida(w) != a0._sha_vida(condicoes[nome]) or a0._sha_vida(w) != disco["sha256"][nome]:
            raise RuntimeError(f"G1: a {nome} do par {sm} ({mec}, {ctx['braco']}) nao se refaz da gravacao do disco")


def vidas(u: dict) -> dict:
    """as vidas de um par (cinco; tres no G-DET), sem gravar nada: o que o `par` grava e o G-S3-IGUAL compara"""
    sm, braco, det, mec = u["semente"], u["braco"], u["det"], u["mecanismo"]
    ss = sementes_do_grupo(sm, CONFIG_GRUPO_LIGADA.ids)
    ctx = s.contexto(braco, sm)
    p = (lambda i, x, gravar=False: _seguidor(mec, i, x, gravar)) if det else (lambda i, x, gravar=False: _vivo(mec, i, x, gravar))
    base = viver(sm, [_vivo(mec, "A", ss), p("B", ss, gravar=True)], ctx, base=True)
    retrato: dict = {}
    vivo = viver(sm, [_vivo(mec, "A", ss), p("B", ss, gravar=not det)], ctx, base=False, retrato=retrato)
    grav = viver(sm, [_vivo(mec, "A", ss), _gravado(mec, "B", ss, base.gravacoes["B"], pc.eventos_do_dono(base.grupo, "B"))], ctx,
                 base=False)
    condicoes = {"VIVO": vivo, "GRAV": grav}
    gravacoes = {"base": a0._gravacao_em_disco(base)}
    if not det:
        base_outra = viver(sm, [_passivo(mec, "A", ss), _vivo(mec, "B", ss, gravar=True)], ctx, base=True)
        condicoes["OUTRA"] = viver(sm, [_vivo(mec, "A", ss), _gravado(mec, "B", ss, base_outra.gravacoes["B"],
                                                                     pc.eventos_do_dono(base_outra.grupo, "B"))], ctx, base=False)
        gravacoes["base_outra"] = a0._gravacao_em_disco(base_outra)
    return {"ss": ss, "ctx": ctx, "base": base, "condicoes": condicoes, "gravacoes": gravacoes, "retrato": retrato}


def par(u: dict, pasta: str) -> dict:
    """as vidas de um par de uma celula, o G-INSTR, o G1, as medidas da S e as da secao 5 (a PM-1 e os descritivos)"""
    sm, braco, det, mec = u["semente"], u["braco"], u["det"], u["mecanismo"]
    v = vidas(u)
    vivo, grav, ctx = v["condicoes"]["VIVO"], v["condicoes"]["GRAV"], v["ctx"]
    a0.g_instr(vivo, grav)
    nome = f"{'DET-' if det else ''}{mec}-{braco}-{u['base']}-{u['k']:04d}"
    disco = {"par": nome, "semente": sm, "mecanismo": mec, "contexto": ctx, "gravacoes": v["gravacoes"],
             "sha256": {c: a0._sha_vida(w) for c, w in v["condicoes"].items()}}
    arquivo = Path(pasta) / "vidas" / f"{nome}.json.gz"
    s._gravar_disco(arquivo, disco)
    g1(sm, v["ss"], ctx, mec, det, vivo, v["condicoes"], arquivo)
    out = {"par": nome, "mecanismo": mec, "braco": braco, "det": det, "base": u["base"], "k": u["k"], "semente": sm, "contexto": ctx,
           "condicoes": {c: s._janela(w) for c, w in v["condicoes"].items()}, "no_t0": vivo.no_t0, "retrato_t0": v["retrato"],
           "g_instr": True, "g1": True, "arquivo_sha256": _sha(arquivo)}
    if not det:
        k = pc.indice_do_passo(vivo, vivo.t0)
        out["frequencia_social_P"] = {"antes_do_t0": frequencia_social(v["base"].gravacoes["B"], 0, k),
                                      "janela_VIVO": frequencia_social(vivo.gravacoes["B"], k, k + s.JANELA)}
        out["riqueza"] = s.s0.observar_vida(vivo, nome)
    return out


def _executar(trabalhos_: list[dict], pasta: str, processos: int) -> list[dict]:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8 e secao 9)")
    if processos <= 1:
        return [par(u, pasta) for u in trabalhos_]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        return [f.result() for f in [pool.submit(par, u, pasta) for u in trabalhos_]]


def trabalhos(cfg: dict) -> list[dict]:
    """as unidades de cada celula: as mesmas sementes nas oito (4), e as do G-DET"""
    run = unidades_derivadas(cfg["unidades"]["bases"], K, PREFIXO["run"])
    det = unidades_derivadas(cfg["det"]["bases"], K, PREFIXO["det"])
    return [{**u, "mecanismo": m, "braco": b, "det": d} for d, uu in ((False, run), (True, det))
            for m in cfg["mecanismos"] for b in cfg["bracos"] for u in uu]


# ================================================================== a analise (5 e 7)
def pm1(registros: list[dict]) -> dict:
    """5 (MD-6): a fracao dos pares em que o P (o B) tem, no t0, o desfecho do `seguir` no receptor da solidao < 0"""
    vals = []
    for r in registros:
        p = r["retrato_t0"].get("B")
        if p is None:
            raise RuntimeError(f"PM-1: o par {r['par']} sem o retrato do t0 de P")
        vals.append(p["desfecho"]["seguir"][p["receptores"].index("solidao")])
    n = sum(1 for x in vals if x < 0)
    f = None if not vals else n / len(vals)
    return {"n_pares": len(vals), "n_negativo": n, "fracao": f, "minimo": PM1_MIN, "passa": f is not None and f >= PM1_MIN,
            "media": None if not vals else sum(vals) / len(vals)}


LEITURA_A = {"cego": "o substrato nao deixa ver: a celula nao diz nada sobre o mecanismo",
             "pm1": "inconclusivo por premissa: o P1 nao aprendeu o valor do outro antes do t0",
             "premissa": "inconclusivo por premissa (PA): registrado como esta",
             "≈ 0": "nulo com um instrumento que ve: o mecanismo nao faz P responder a F neste substrato",
             "< 0": "o parceiro responde: aproxima o contato",
             "> 0": "o parceiro responde: afasta o contato",
             "indeterminado": "registrado como esta; nada se decide"}


def leitura_celula(mec: str, prem: dict, prim: dict, gdet: dict, p1: dict | None) -> dict:
    """7: o G-DET primeiro, depois as premissas da S, depois a PM-1 (so nos braços com o M2, e so diante de um ≈ 0)"""
    classe = prim["classe"]
    if not gdet["passa"]:
        chave = "cego"
    elif not prem["A_conclusivo"]:
        chave = "premissa"
    elif mec in COM_M2 and classe == "≈ 0" and not p1["passa"]:
        chave = "pm1"
    else:
        chave = classe
    return {"classe": {"pm1": "inconclusivo por premissa (PM-1)", "premissa": "inconclusivo por premissa"}.get(chave, chave),
            "texto": LEITURA_A[chave]}


def contraste(registros: list[dict], braco: str, com: str, sem: str) -> dict:
    """5: D_A(com) - D_A(sem), pareado pela base, nos pares elegiveis nas duas celulas"""
    por = {m: {(r["base"], r["k"]): r for r in registros if r["mecanismo"] == m and r["braco"] == braco and not r["det"]} for m in (com, sem)}
    chaves = sorted(set(por[com]) & set(por[sem]))
    dd = [s.d_a(por[com][c]) - s.d_a(por[sem][c]) for c in chaves if s.elegivel_a(por[com][c]) and s.elegivel_a(por[sem][c])]
    return {"medida": f"D_A({com}) - D_A({sem}), pareado pela base", "pares": len(chaves), **a0._contraste(dd, DELTA_A)}


def leitura_conjunto(celulas: dict, contrastes: dict) -> dict:
    """7, o conjunto, no B1"""
    b1 = celulas.get("M1+M2|B1")
    if b1 is None:
        return {"texto": "sem a celula M1+M2|B1: nenhuma linha do conjunto se aplica"}
    cl, apr = b1["leitura"]["classe"], contrastes.get("C-APR|B1", {}).get("classe")
    if cl in ("< 0", "> 0") and apr == "< 0":
        texto = "os mecanismos fazem aparecer um social aprendido: descrever o caminho e levar M1-4 e M2-6 ao Matheus"
    elif cl in ("< 0", "> 0") and apr == "≈ 0":
        texto = "a resposta vem das unidades a mais ou da companhia no corpo, nao do aprendizado (o D-SP-62)"
    elif cl == "≈ 0":
        texto = "o valor da solidao nao basta para P responder: um plano novo, com outro alivio ou outro mecanismo (M3 ou M4)"
    elif cl == "inconclusivo por premissa (PM-1)":
        texto = "o P1 nao chega a aprender antes do t0: olhar a frequencia do `seguir` antes do t0, num plano novo"
    else:
        texto = "nenhuma das linhas da secao 7 se aplica: registrado como esta"
    return {"M1+M2|B1": cl, "C-APR|B1": apr, "texto": texto}


def _media(xs: list):
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def descritivos(rr: list[dict]) -> dict:
    """5, os descritivos (nao decidem nada)"""
    def desf(classe: str, receptor: str, pet: str):
        vals = []
        for r in rr:
            p = r["retrato_t0"].get(pet)
            if p is not None:
                vals.append(p["desfecho"][classe][p["receptores"].index(receptor)])
        return _media(vals)
    receptores = next((r["retrato_t0"]["B"]["receptores"] for r in rr if "B" in r["retrato_t0"]), [])
    return {"frequencia_social_P": {q: _media([r["frequencia_social_P"][q]["fracao"] for r in rr]) for q in ("antes_do_t0", "janela_VIVO")},
            "desfecho_t0": {pet: {c: {rc: desf(c, rc, pet) for rc in receptores} for c in TIPOS_ALVO_SOCIAIS} for pet in ("A", "B")},
            "solidao_P_no_t0": _media([r["retrato_t0"].get("B", {}).get("solidao") for r in rr])}


def analisar(registros: list[dict]) -> dict:
    if not all(r["g_instr"] and r["g1"] for r in registros):
        raise RuntimeError("um par sem o G-INSTR ou o G1: a run nao se le (8)")
    celulas = {}
    for mec in [m for m in (*MECANISMOS, *SO_FUMACA) if any(r["mecanismo"] == m for r in registros)]:
        for b in BRACOS:
            rr = [r for r in registros if r["mecanismo"] == mec and r["braco"] == b and not r["det"]]
            dd = [r for r in registros if r["mecanismo"] == mec and r["braco"] == b and r["det"]]
            if not rr:
                continue
            prem, prims, gd = s.premissas(rr), s.primarios(rr), s.g_det(dd)
            p1 = pm1(rr) if mec in COM_M2 else None
            celulas[f"{mec}|{b}"] = {"pares": len(rr), "premissas": prem, "primario": prims["A"], "secundarios": s.secundarios(rr),
                                     "g_det": gd, "pm1": p1, "leitura": leitura_celula(mec, prem, prims["A"], gd, p1),
                                     "substrato": s.substrato(rr), "riqueza": s.riqueza(rr),
                                     "descritivos": descritivos(rr) if mec not in SO_FUMACA else None}
    contrastes = {}
    mecs, bracos = {r["mecanismo"] for r in registros}, {r["braco"] for r in registros}
    for nome, (com, sem) in (("C-APR", ("M1+M2", "M1-inc0+M2")), ("C-APR1", ("M1", "M1-inc0"))):
        if {com, sem} <= mecs:
            for b in [x for x in BRACOS if x in bracos]:
                contrastes[f"{nome}|{b}"] = contraste(registros, b, com, sem)
    return {"celulas": celulas, "contrastes": contrastes, "conjunto": leitura_conjunto(celulas, contrastes)}


# ================================================================== a run
def meta_inicial(cfg: dict, modo: str, tt: list[dict], processos: int, caminho_config: Path | None) -> dict:
    m = s.meta_inicial(cfg, modo, tt, processos, caminho_config)
    m.update({"fase": FASE, "plano": PLANO, "plano_sha256": _sha(RAIZ / PLANO), "orquestrador_sha256": _sha(Path(__file__)),
              "orquestrador_s_sha256": _sha(Path(s.__file__)), "comando": " ".join(["python"] + sys.argv)})
    m["sha256"].update({n: _sha(RAIZ / "digilab" / n) for n in ("corpo.py", "corpo_grafo.py", "motor_corpo.py")})
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
    print(json.dumps({"conjunto": r["conjunto"], "celulas": {c: {"leitura": x["leitura"], "g_det": {k: x["g_det"][k] for k in ("ic95", "passa")}}
                                                             for c, x in r["celulas"].items()},
                      "contrastes": {c: {k: x[k] for k in ("media", "ic95", "classe")} for c, x in r["contrastes"].items()}},
                     indent=1, ensure_ascii=True, default=str))


if __name__ == "__main__":
    main()
