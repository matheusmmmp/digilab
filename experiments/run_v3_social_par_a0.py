"""SOCIAL_PAR, A0 e B0: o parceiro que responde no pet de hoje (docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md, APROVADO pelo Matheus em
2026-11-17, "Aprovo todas").

Cada par (a semente do grupo) vive cinco vidas na mesma semente (o plano, 3.2): a base e a base-OUTRA (as gravacoes de P), e a VIVO, a GRAV e
a OUTRA com a mesma perturbacao (F, o pet A, levado a 12 celulas de P, o pet B, no t0 sorteado nos dias 1 a 3 de uma vida de 5). Os dois
pets sao o modular com a CO7 (A0-1), com o dono atencioso no `comedouro` (A0-2).

Em cada par: o G-INSTR (as posicoes da VIVO e da GRAV iguais ate o passo da perturbacao; se falha, a run para) e o G1 (a VIVO rejogada pelo
`reproduzir_grupo`, e a GRAV e a OUTRA refeitas da gravacao lida do disco, com o mesmo registro e as mesmas posicoes). As medidas sao as de
`digilab/metrics.py`; a analise (as premissas, os primarios, os secundarios com o Holm, a leitura da secao 7 e o descritivo da secao 8) sai do
`medidas.json` gravado.

Os modos (a config): `fumaca` (as bases dos testes, 101...505, numa pasta fora de artifacts_v3_social_par_a0/), `piloto` (so pelo
`experiments/piloto_social_par_a0.py`, que nao grava nenhuma media) e `run` (a faixa 101101...101505, com o K decidido pelo Matheus depois do
piloto, secao 6). A run se recusa a rodar sem o plano APROVADO, sem a faixa em FAIXAS_RESERVADAS, com mais de 4 processos ou por cima de uma
pasta que ja existe.

    python experiments/run_v3_social_par_a0.py --config experiments/configs/v3_social_par_a0/fumaca.json --saida <pasta> --processos 2
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS, SementeSemPlano, unidades_derivadas  # noqa: E402
from bancada.rodar import _dump, _gravar, _sha  # noqa: E402
from digilab import metrics as mt  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.config import (CONFIG_COOPERACAO_CO7, CONFIG_GRUPO_LIGADA, CONFIG_INTERVENCAO_SOCIAL_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            TICKS_POR_DIA)
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import EventoGrupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md"
FASE = "social_par_a0"
CM = e6.CM
CCO = CONFIG_COOPERACAO_CO7                                   # 3.1, A0-1: a CO7 nos dois, no grupo e no cerebro
CI = CONFIG_INTERVENCAO_SOCIAL_LIGADA
DONO, LUGAR = "atencioso", "comedouro"                        # 3.1, A0-2
DIAS = 5                                                      # 3.1, A0-3
PASSO = 15                                                    # o passo do dono, em ticks (uma decisao)
T0_MIN, T0_MAX = TICKS_POR_DIA, 3 * TICKS_POR_DIA             # 3.3, A0-3: o t0 num passo do dono nos dias 1 a 3
D0 = 12                                                       # 3.3, A0-4, SEM FONTE
RAIO_PERTO, RAIO_CONTATO = CI.raio_perto_celulas, CI.raio_contato_celulas     # 6 e 1 (5.2, A0-4)
JANELA = CI.janela_reencontro                                 # 96 decisoes, um dia (5)
JANELA_TICKS = JANELA * PASSO
JANELA_CHUTE = 60                                             # 5.2, A0-6: em ticks, SEM FONTE
DESLOCAMENTOS = tuple(PASSO * j for j in range(8, 89))        # 5.2: 81 substitutos, a mais de 8 decisoes do original
MIN_CHUTES = 2                                                # 5.1, PB-1
DELTA_A, DELTA_B = 4.0, 0.05                                  # 6, A0-5 e A0-6, SEM FONTE
PA1_MIN, PA2_FRACAO, PA2_N, PA3_MIN, PB1_N = 0.95, 0.80, 100, 0.20, 100        # 5.1
ALFA_SECUNDARIOS = 0.05                                       # 5.4: bilateral, o Holm na familia dos tres
MAX_PROCESSOS = 4                                             # 9 (V3-D8)
PREFIXO = {"fumaca": "social_par", "piloto": "social_par_piloto", "run": "social_par"}
BASES = {"piloto": (102101, 102202, 102303, 102404, 102505), "run": (101101, 101202, 101303, 101404, 101505)}     # 3.4, A0-8
FAIXA = {"piloto": (102101, 102505), "run": (101101, 101505)}
K_PILOTO = 20                                                 # 3.4, A0-7
K_RUN = None                                                  # 6: o Matheus decide depois do piloto; None recusa a run
SAIDA = "artifacts_v3_social_par_a0/run"
CONDICOES = pc.CONDICOES


# ================================================================== as travas
def exigir_plano_aprovado() -> None:
    """a trava do cabecalho do plano: a linha do status comeca com "APROVADO pelo Matheus" """
    status = [x for x in (RAIZ / PLANO).read_text(encoding="utf-8").splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho: {status[:1] or 'sem a linha do status'}")


def exigir_faixa_reservada(modo: str) -> None:
    if not any((lo, hi) == FAIXA[modo] for lo, hi, _ in FAIXAS_RESERVADAS):
        raise SementeSemPlano(f"a faixa {FAIXA[modo][0]}...{FAIXA[modo][1]} nao esta em FAIXAS_RESERVADAS (3.4)")


def modo_da_config(cfg: dict) -> str:
    """confere a config contra o plano: a fumaca so com as bases dos testes; o piloto e a run so com as bases da faixa; o K do piloto e o
    do plano, e o da run tem de vir na config (o Matheus o decide depois do piloto)"""
    modo = cfg.get("modo")
    bases, k = cfg.get("unidades", {}).get("bases"), cfg.get("unidades", {}).get("k")
    if modo not in PREFIXO or not isinstance(bases, list) or type(k) is not int or k < 1:
        raise ValueError(f"config invalida: {cfg}")
    if modo == "fumaca":
        if not all(b in (101, 202, 303, 404, 505) for b in bases):
            raise SementeSemPlano(f"a fumaca so usa as bases dos testes (101...505): {bases}")
        return modo
    exigir_plano_aprovado()
    exigir_faixa_reservada(modo)
    if tuple(bases) != BASES[modo]:
        raise SementeSemPlano(f"as bases do {modo} sao {BASES[modo]} (3.4): {bases}")
    if modo == "piloto" and k != K_PILOTO:
        raise ValueError(f"o piloto tem K = {K_PILOTO} por base (3.4, A0-7): {k}")
    if modo == "run" and (K_RUN is None or k != K_RUN):
        raise ValueError(f"o K da run e o decidido pelo Matheus depois do piloto (secao 6), K_RUN = {K_RUN}: {k}")
    return modo


# ================================================================== o pet de hoje (3.1, A0-1)
def fabricas_do_jogo(dono: str, semente_pet: int, cfg_cooperacao=None):
    """(a fabrica do cerebro, a do motor) do pet de hoje: o modular do `exportar_gabarito_co6.fabricas` com a CO7 no cerebro, como o
    `exportar_gabarito_co7_par.grupo` e o jogo v39 (web/app/motor/grupo_jogo.ts:75). A `cfg_cooperacao` padrao e a CONFIG_COOPERACAO_CO7;
    o grupo recebe a mesma, no `viver_par`. Mora aqui, e nao na bancada (o plano dizia `parceiro.py`): so os orquestradores montam o
    DigiBrain (tests/test_digibrain_vidas.py, o T.3; D-SP-29)."""
    cco = cfg_cooperacao or CONFIG_COOPERACAO_CO7
    if not (cco.ligada and cco.co6 and cco.co7):
        raise ValueError(f"o pet de hoje tem a CO7 ligada (A0-1): {cco}")
    cd = orq.config_do_braco(e6.BRACO, conserto=True)
    _, fm = e6.fabricas(dono, semente_pet)

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cd, e6.CM, semente=semente_pet, cfg_cooperacao=cco)
    return fp, fm


# ================================================================== as cinco vidas de um par
def _dono(semente_pet: int) -> DonoComLugar:
    return DonoComLugar(criar_dono(DONO), LUGAR, semente_pet, DONO, CM)


def _vivo(ident: str, ss: dict, gravar: bool = False) -> pc.Membro:
    fp, fm = fabricas_do_jogo(DONO, ss[ident], CCO)
    return pc.Membro(ident, "vivo", fm, fp, _dono(ss[ident]), DONO, "digibrain", gravar=gravar)


def _passivo(ident: str, ss: dict) -> pc.Membro:
    _, fm = fabricas_do_jogo(DONO, ss[ident], CCO)
    return pc.Membro(ident, "vivo", fm, lambda c: pc.Passivo(c), _dono(ss[ident]), DONO, "passivo")


def _gravado(ident: str, ss: dict, gravacao: list, eventos: list) -> pc.Membro:
    _, fm = fabricas_do_jogo(DONO, ss[ident], CCO)
    return pc.Membro(ident, "gravado", fm, gravacao=gravacao, eventos_dono=eventos, rotulo_dono=DONO, rotulo_cerebro="gravada")


def _viver(s: int, membros: list, perturbacao=None) -> pc.VidaPar:
    return pc.viver_par(CM, s, membros, DIAS, perturbacao=perturbacao, cfg_intervencao=CI, cfg_cooperacao=CCO)


def _sha_vida(v: pc.VidaPar) -> dict:
    return {"registro": hashlib.sha256(v.grupo.registro.para_jsonl().encode("utf-8")).hexdigest(),
            "posicoes": hashlib.sha256(json.dumps(v.posicoes, sort_keys=True).encode("utf-8")).hexdigest()}


def g_instr(vivo: pc.VidaPar, grav: pc.VidaPar) -> None:
    """5.3: as posicoes de F e de P na VIVO e na GRAV sao iguais em todos os passos ate o da perturbacao (inclusive); um par que falha e um
    erro do codigo, e a run para"""
    if vivo.t0 is None or grav.t0 != vivo.t0:
        raise RuntimeError(f"G-INSTR: o t0 da VIVO ({vivo.t0}) e o da GRAV ({grav.t0}) diferem")
    k = pc.indice_do_passo(vivo, vivo.t0)
    for i in ("A", "B"):
        if vivo.posicoes[i][:k + 1] != grav.posicoes[i][:k + 1]:
            primeiro = next(j for j, (a, b) in enumerate(zip(vivo.posicoes[i], grav.posicoes[i])) if a != b)
            raise RuntimeError(f"G-INSTR: o pet {i} difere entre a VIVO e a GRAV no passo {primeiro}, antes da perturbacao (passo {k})")


def _gravacao_em_disco(base: pc.VidaPar) -> dict:
    return {"decisoes": [d.para_dict() for d in base.gravacoes["B"]], "eventos_dono": [e.para_dict() for e in pc.eventos_do_dono(base.grupo, "B")]}


def _gravacao_do_disco(d: dict) -> tuple[list, list]:
    return [pc.DecisaoGravada.de_dict(x) for x in d["decisoes"]], [EventoGrupo.de_dict(x) for x in d["eventos_dono"]]


def g1(s: int, ss: dict, vivo: pc.VidaPar, condicoes: dict, arquivo: Path) -> None:
    """o G1: a VIVO pelo `reproduzir_grupo` (as causas de fora: o dono e o levar), bit a bit; a GRAV e a OUTRA refeitas da gravacao lida
    do arquivo gravado, com o mesmo registro e as mesmas posicoes"""
    fabricas = {i: fabricas_do_jogo(DONO, ss[i], CCO) for i in ("A", "B")}
    lido = RegistroGrupo.de_jsonl(vivo.grupo.registro.para_jsonl())
    r = reproduzir_grupo(lido, fabricas, CM, cfg_cooperacao=CCO, cfg_intervencao=CI)
    if r.registro != vivo.grupo.registro or [tuple(r.motores[i].pet) for i in "AB"] != [tuple(vivo.grupo.motores[i].pet) for i in "AB"]:
        raise RuntimeError(f"G1: a VIVO do par {s} nao se refaz pelo replay")
    with gzip.open(arquivo, "rt", encoding="utf-8") as f:
        disco = json.load(f)
    pert = tuple(disco["perturbacao"])
    for nome, chave in (("GRAV", "base"), ("OUTRA", "base_outra")):
        gravacao, eventos = _gravacao_do_disco(disco["gravacoes"][chave])
        w = _viver(s, [_vivo("A", ss), _gravado("B", ss, gravacao, eventos)], pert)
        if _sha_vida(w) != _sha_vida(condicoes[nome]) or _sha_vida(w) != disco["sha256"][nome]:
            raise RuntimeError(f"G1: a {nome} do par {s} nao se refaz da gravacao do disco")


def _janela(v: pc.VidaPar) -> dict:
    """as medidas de uma condicao na janela de 96 decisoes depois do passo da perturbacao (5.2, 5.4 e 8)"""
    d = pc.distancias_celulas(v, "A", "B")
    if v.t0 is None:
        return {"cabe": False, "t0": None}
    k = pc.indice_do_passo(v, v.t0)
    if k + JANELA >= len(d):
        return {"cabe": False, "t0": v.t0, "passo": k}
    w = slice(k, k + JANELA + 1)
    t_perto, cens_perto = mt.tempo_ate_raio(d, RAIO_PERTO, k, JANELA)
    t_contato, cens_contato = mt.tempo_ate_raio(d, RAIO_CONTATO, k, JANELA)
    inicio, fim = v.passos[k], v.passos[k + JANELA]
    if fim - inicio != JANELA_TICKS:
        raise RuntimeError(f"a janela tem {fim - inicio} ticks, eram {JANELA_TICKS}")
    chutes = {i: [t - inicio - 1 for t in pc.chutes(v, i) if inicio < t <= fim] for i in ("A", "B")}
    alt = {}
    for de, para in (("A", "B"), ("B", "A")):
        obs = mt.alternancia(chutes[de], chutes[para], JANELA_CHUTE)
        subs = [x for x in mt.alternancia_substituta(chutes[de], chutes[para], JANELA_CHUTE, DESLOCAMENTOS, JANELA_TICKS) if x is not None]
        alt[f"{de}{para}"] = {"observada": obs, "substitutos": None if not subs else sum(subs) / len(subs),
                              "excesso": None if obs is None or not subs else obs - sum(subs) / len(subs)}
    eps = mt.episodios_em_raio(d[k + 1:k + JANELA + 1], RAIO_PERTO)
    pol = v.grupo.motores["A"].politica
    motivos = getattr(pol, "motivos", None)
    co7 = None
    if motivos is not None and len(motivos) == len(v.passos):
        janela_m = motivos[k + 1:k + JANELA + 1]
        co7 = {"com_dever": sum(1 for m in janela_m if m.get("dever") is not None),
               "escudo_removeu": sum(1 for m in janela_m if m.get("dever") and m["dever"].get("removidas"))}
    return {"cabe": True, "t0": v.t0, "passo": k, "distancia_no_t0": d[k],
            "t_perto": mt.tempo_restrito(d, RAIO_PERTO, k, JANELA), "censurado_perto": cens_perto,
            "t_contato": mt.tempo_restrito(d, RAIO_CONTATO, k, JANELA), "censurado_contato": cens_contato,
            "fracao_perto": mt.fracao_em_raio(d[k + 1:k + JANELA + 1], RAIO_PERTO),
            "episodios_perto": {"n": len(eps), "media": None if not eps else sum(eps) / len(eps)},
            "contingencia_FP": mt.contingencia(v.posicoes["A"][w], v.posicoes["B"][w]),
            "contingencia_PF": mt.contingencia(v.posicoes["B"][w], v.posicoes["A"][w]),
            "chutes": {i: len(c) for i, c in chutes.items()}, "alternancia": alt,
            "desvios_P": _contar(v.desvios.get("B", [])), "desvios_P_janela": _contar([x for x in v.desvios.get("B", []) if k < x[0] <= k + JANELA]),
            "co7_F": co7}


def _contar(desvios: list) -> dict:
    out: dict = {}
    for _, tipo in desvios:
        out[tipo] = out.get(tipo, 0) + 1
    return out


def par(u: dict, pasta: str | None) -> dict:
    """as cinco vidas de um par, o G-INSTR, o G1 e as medidas (o trabalho de um processo)"""
    s = u["semente"]
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    t0, direcao = pc.sortear_perturbacao(s, T0_MIN, T0_MAX, PASSO)
    pert = ("A", "B", t0, direcao, D0)
    base = _viver(s, [_vivo("A", ss), _vivo("B", ss, gravar=True)])
    base_outra = _viver(s, [_passivo("A", ss), _vivo("B", ss, gravar=True)])
    vivo = _viver(s, [_vivo("A", ss), _vivo("B", ss)], pert)
    grav = _viver(s, [_vivo("A", ss), _gravado("B", ss, base.gravacoes["B"], pc.eventos_do_dono(base.grupo, "B"))], pert)
    outra = _viver(s, [_vivo("A", ss), _gravado("B", ss, base_outra.gravacoes["B"], pc.eventos_do_dono(base_outra.grupo, "B"))], pert)
    condicoes = {"VIVO": vivo, "GRAV": grav, "OUTRA": outra}
    g_instr(vivo, grav)
    nome = f"{u['base']}-{u['k']:04d}"
    disco = {"par": nome, "semente": s, "perturbacao": list(pert),
             "gravacoes": {"base": _gravacao_em_disco(base), "base_outra": _gravacao_em_disco(base_outra)},
             "sha256": {c: _sha_vida(v) for c, v in condicoes.items()}}
    if pasta is None:
        raise ValueError("o par precisa de uma pasta para as gravacoes (o G1 le do disco)")
    arquivo = Path(pasta) / "vidas" / f"{nome}.json.gz"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(arquivo, "wt", encoding="utf-8", compresslevel=6) as f:
        json.dump(disco, f, sort_keys=True)
    g1(s, ss, vivo, condicoes, arquivo)
    return {"par": nome, "base": u["base"], "k": u["k"], "semente": s, "t0_sorteado": t0, "direcao": direcao,
            "condicoes": {c: _janela(v) for c, v in condicoes.items()}, "no_t0": vivo.no_t0,
            "chutes_P_base_outra_por_dia": len(pc.chutes(base_outra, "B")) / DIAS, "g_instr": True, "g1": True,
            "arquivo_sha256": _sha(arquivo)}


def _executar(unidades: list[dict], pasta: str, processos: int) -> list[dict]:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8 e secao 9)")
    if processos <= 1:
        return [par(u, pasta) for u in unidades]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        return [f.result() for f in [pool.submit(par, u, pasta) for u in unidades]]


# ================================================================== a analise (5, 7 e 8)
def _cabe(r: dict) -> bool:
    return r["condicoes"]["VIVO"]["cabe"] and r["condicoes"]["GRAV"]["cabe"]


def elegivel_a(r: dict) -> bool:
    return _cabe(r) and r["condicoes"]["VIVO"]["distancia_no_t0"] > RAIO_PERTO


def elegivel_b(r: dict) -> bool:
    return _cabe(r) and all(r["condicoes"][c]["chutes"][i] >= MIN_CHUTES for c in ("VIVO", "GRAV") for i in ("A", "B"))


def d_a(r: dict) -> float:
    return float(r["condicoes"]["VIVO"]["t_perto"] - r["condicoes"]["GRAV"]["t_perto"])


def d_b(r: dict) -> float | None:
    v, g = (r["condicoes"][c]["alternancia"]["AB"]["excesso"] for c in ("VIVO", "GRAV"))
    return None if v is None or g is None else v - g


def premissas(registros: list[dict]) -> dict:
    """5.1: as quatro premissas, com as contagens"""
    n = len(registros)
    cabe = [r for r in registros if _cabe(r)]
    ea = [r for r in cabe if elegivel_a(r)]
    espaco = [r for r in ea if not (r["condicoes"]["VIVO"]["censurado_perto"] and r["condicoes"]["GRAV"]["censurado_perto"])]
    eb = [r for r in cabe if elegivel_b(r) and d_b(r) is not None]
    f = lambda a, b: None if not b else len(a) / len(b)  # noqa: E731
    pa1 = {"n_pares": n, "n_cabe": len(cabe), "fracao": f(cabe, registros), "minimo": PA1_MIN}
    pa2 = {"n_elegiveis": len(ea), "fracao": f(ea, cabe), "minimo_fracao": PA2_FRACAO, "minimo_n": PA2_N}
    pa3 = {"n_com_reencontro": len(espaco), "fracao": f(espaco, ea), "minimo": PA3_MIN}
    pb1 = {"n_elegiveis": len(eb), "fracao": f(eb, cabe), "minimo_n": PB1_N}
    pa1["passa"] = pa1["fracao"] is not None and pa1["fracao"] >= PA1_MIN
    pa2["passa"] = pa2["fracao"] is not None and pa2["fracao"] >= PA2_FRACAO and len(ea) >= PA2_N
    pa3["passa"] = pa3["fracao"] is not None and pa3["fracao"] >= PA3_MIN
    pb1["passa"] = len(eb) >= PB1_N
    return {"PA-1": pa1, "PA-2": pa2, "PA-3": pa3, "PB-1": pb1,
            "A_conclusivo": pa1["passa"] and pa2["passa"] and pa3["passa"], "B_conclusivo": pa1["passa"] and pb1["passa"]}


def _contraste(valores: list[float], margem: float | None) -> dict:
    """o IC95 pelo t sobre os pares (`metrics.ic_t`), o p bilateral pelo t e, com margem, a classe da secao 7 (a da A6.6, `lr.classe`)"""
    ic = mt.ic_t(valores)
    p = None
    if ic["motivo"] is None and ic["dp"] > 0:
        t = ic["media"] / (ic["dp"] / math.sqrt(ic["n"]))
        p = min(1.0, 2.0 * mt.t_unilateral(abs(t), ic["n"] - 1))
    out = {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": [ic["ic_inferior"], ic["ic_superior"]], "p_bilateral": p,
           "motivo": ic["motivo"]}
    if margem is not None:
        out["margem"] = margem
        out["classe"] = lr.classe(ic, margem)["classe"]
    else:
        lo, hi = ic["ic_inferior"], ic["ic_superior"]
        out["classe"] = "indeterminado" if lo is None else ("> 0" if lo > 0 else "< 0" if hi < 0 else "inclui 0")
    return out


def primarios(registros: list[dict]) -> dict:
    ea = [r for r in registros if elegivel_a(r)]
    eb = [r for r in registros if elegivel_b(r) and d_b(r) is not None]
    return {"A0": {"medida": "D_A = T*_VIVO - T*_GRAV (decisoes; negativo = F volta mais depressa com P que responde)",
                   **_contraste([d_a(r) for r in ea], DELTA_A)},
            "B0": {"medida": "D_B = E_VIVO - E_GRAV (o excesso de alternancia de F para P sobre os substitutos)",
                   **_contraste([d_b(r) for r in eb], DELTA_B)}}


def secundarios(registros: list[dict]) -> dict:
    """5.4: S1, S2 e S3, com o Holm na familia dos tres (alfa 0,05, bilateral)"""
    ea = [r for r in registros if elegivel_a(r)]
    c = lambda r, n: r["condicoes"][n]  # noqa: E731
    s1 = [float(c(r, "GRAV")["t_perto"] - c(r, "OUTRA")["t_perto"]) for r in ea if c(r, "OUTRA")["cabe"]]
    s2 = [c(r, "VIVO")["fracao_perto"] - c(r, "GRAV")["fracao_perto"] for r in ea]
    s3_pares = [r for r in ea if c(r, "VIVO")["contingencia_FP"] is not None and c(r, "GRAV")["contingencia_FP"] is not None]
    s3 = [c(r, "VIVO")["contingencia_FP"] - c(r, "GRAV")["contingencia_FP"] for r in s3_pares]
    out = {"S1_GRAV_menos_OUTRA": {**_contraste(s1, None), "fora": len(ea) - len(s1)},
           "S2_fracao_perto": {**_contraste(s2, None), "fora": 0},
           "S3_contingencia_FP": {**_contraste(s3, None), "fora": len(ea) - len(s3)}}
    h = mt.holm({k: v["p_bilateral"] for k, v in out.items()}, ALFA_SECUNDARIOS)
    for k in out:
        out[k]["holm"] = h[k]
    return out


LEITURA_A = {"≈ 0": "o previsto: no pet de hoje, o parceiro que responde nao muda o reencontro em mais de uma hora de jogo (nenhuma "
                    "diferenca acima da delta; nao quer dizer que o pet ignora o outro)",
             "< 0": "um caminho social ja existe no pet de hoje: F volta mais depressa quando P responde (a CO7 ou o mundo comum; o "
                    "descritivo aponta, um adendo separa)",
             "> 0": "P que responde afasta o reencontro (por exemplo, disputando a comida); o mesmo caminho do < 0",
             "indeterminado": "registrado como esta; nada se decide com ele"}
LEITURA_B = {"≈ 0": "o previsto: P nao chuta depois de F mais do que a gravacao e a taxa de cada um explicam",
             "> 0": "P responde aos chutes de F: o primeiro sinal de coordenacao pela bola no pet de hoje (o E_GRAV e a direcao de P para "
                    "F, no descritivo, dizem se e resposta ou geometria)",
             "< 0": "P chuta menos depois de F quando responde: registrado como esta",
             "indeterminado": "registrado como esta"}


def leitura(prims: dict, prem: dict) -> dict:
    """a secao 7, escrita antes"""
    out = {}
    for nome, tabela, conclusivo in (("A0", LEITURA_A, prem["A_conclusivo"]), ("B0", LEITURA_B, prem["B_conclusivo"])):
        classe = prims[nome]["classe"]
        out[nome] = ({"classe": "inconclusivo por premissa", "texto": "registrado como esta; nada se decide com ele"} if not conclusivo
                     else {"classe": classe, "texto": tabela[classe]})
    return out


def _media(xs: list) -> float | None:
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def descritivo(registros: list[dict]) -> dict:
    """a secao 8 (sem gate; nada aqui muda a secao 7)"""
    ea = [r for r in registros if elegivel_a(r)]
    out: dict = {}
    desv = {c: {} for c in ("GRAV", "OUTRA")}
    for r in registros:
        for c in desv:
            for tipo, n in r["condicoes"][c].get("desvios_P_janela", {}).items():
                desv[c][tipo] = desv[c].get(tipo, 0) + n
    out["1_desvios_P_na_janela"] = desv

    def estrato(chave):
        g: dict = {}
        for r in ea:
            g.setdefault(chave(r), []).append(d_a(r))
        return {str(k): {"n": len(v), "media_D_A": _media(v)} for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}
    p_no_t0 = lambda r: ("dormindo" if r["no_t0"]["pets"]["B"]["dormindo"] else "comendo" if r["no_t0"]["pets"]["B"]["comeu"]  # noqa: E731
                         else "livre")
    out["2_P_no_t0"] = estrato(p_no_t0)
    out["3_comida_no_t0"] = estrato(lambda r: "com comida" if r["no_t0"]["comidas"] else "sem comida")
    out["4_idade"] = estrato(lambda r: f"dia {r['condicoes']['VIVO']['t0'] // TICKS_POR_DIA}")
    out["5_contato_e_episodios"] = {c: {"t_contato": _media([r["condicoes"][c]["t_contato"] for r in ea]),
                                        "censurado_contato": _media([float(r["condicoes"][c]["censurado_contato"]) for r in ea]),
                                        "episodios_perto_n": _media([r["condicoes"][c]["episodios_perto"]["n"] for r in ea]),
                                        "episodios_perto_duracao": _media([r["condicoes"][c]["episodios_perto"]["media"] for r in ea]),
                                        "t_perto": _media([r["condicoes"][c]["t_perto"] for r in ea]),
                                        "censurado_perto": _media([float(r["condicoes"][c]["censurado_perto"]) for r in ea])}
                                    for c in CONDICOES if all(r["condicoes"][c]["cabe"] for r in ea)}
    out["6_conferencias"] = {"contingencia_PF_na_GRAV": _contraste([r["condicoes"]["GRAV"]["contingencia_PF"] for r in ea
                                                                    if r["condicoes"]["GRAV"]["contingencia_PF"] is not None], None),
                             "excesso_PF": {c: _media([r["condicoes"][c]["alternancia"]["BA"]["excesso"] for r in registros
                                                       if r["condicoes"][c]["cabe"]]) for c in CONDICOES},
                             "excesso_FP": {c: _media([r["condicoes"][c]["alternancia"]["AB"]["excesso"] for r in registros
                                                       if r["condicoes"][c]["cabe"]]) for c in CONDICOES}}
    out["7_chutes_P_com_F_passivo_por_dia"] = _media([r["chutes_P_base_outra_por_dia"] for r in registros])
    out["8_co7_F_na_janela"] = {c: {k: _media([r["condicoes"][c]["co7_F"][k] for r in ea if r["condicoes"][c]["co7_F"] is not None])
                                    for k in ("com_dever", "escudo_removeu")} for c in CONDICOES}
    return out


def analisar(registros: list[dict]) -> dict:
    if not all(r["g_instr"] and r["g1"] for r in registros):
        raise RuntimeError("um par sem o G-INSTR ou o G1: a run nao se le (5.3)")
    prem = premissas(registros)
    prims = primarios(registros)
    return {"premissas": prem, "primarios": prims, "secundarios": secundarios(registros), "leitura": leitura(prims, prem),
            "descritivo": descritivo(registros)}


# ================================================================== a run
def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def meta_inicial(cfg: dict, modo: str, unidades: list[dict], processos: int, caminho_config: Path | None) -> dict:
    return {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": _sha(RAIZ / PLANO), "config": cfg,
            "config_sha256": None if caminho_config is None else _sha(caminho_config),
            "orquestrador_sha256": _sha(Path(__file__)), "parceiro_sha256": _sha(Path(pc.__file__)),
            "git_head": _git("rev-parse", "HEAD"), "git_limpo": _git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "dias": DIAS, "d0": D0, "janela": JANELA, "janela_chute": JANELA_CHUTE, "t0": [T0_MIN, T0_MAX],
            "sha256": {n: _sha(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "grupo.py")}
            | {f"digibrain/{p.name}": _sha(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "python": platform.python_version(), "inicio": time.strftime("%Y-%m-%dT%H:%M:%S")}


def coletar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> tuple[dict, list[dict]]:
    """as vidas de todos os pares (o piloto e a run): grava o meta.json e devolve os registros, sem analise"""
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 7)")
    unidades = unidades_derivadas(cfg["unidades"]["bases"], cfg["unidades"]["k"], PREFIXO[modo])
    pasta.mkdir(parents=True)
    meta = meta_inicial(cfg, modo, unidades, processos, caminho_config)
    _gravar(pasta / "meta.json", _dump(meta))
    t = time.perf_counter()
    registros = _executar(unidades, str(pasta), processos)
    meta["vidas_parede_s"] = time.perf_counter() - t
    meta["vidas"] = 5 * len(registros)
    if len(registros) != len(unidades):
        raise RuntimeError(f"{len(registros)} pares, eram {len(unidades)}")
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _gravar(pasta / "meta.json", _dump(meta))
    return meta, registros


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if cfg.get("modo") == "piloto":
        raise ValueError("o piloto roda so pelo experiments/piloto_social_par_a0.py, que nao grava nenhuma media (secao 6)")
    meta, registros = coletar(cfg, pasta, processos, caminho_config)
    _gravar(pasta / "medidas.json", _dump({r["par"]: r for r in sorted(registros, key=lambda r: r["par"])}))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": meta["modo"], "fase": FASE, "plano": PLANO, "pares": len(lidos), **analisar(list(lidos.values()))}
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
    if cfg.get("modo") == "fumaca" and a.saida is None:
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v3_social_par_a0/)")
    r = rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]
    print(json.dumps({k: r[k] for k in ("modo", "pares", "premissas", "primarios", "leitura")}, indent=1, ensure_ascii=True,
                     default=str)[:4000])


if __name__ == "__main__":
    main()
