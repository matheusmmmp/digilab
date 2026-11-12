"""O orquestrador da GV3 do GOSTO_VISUAL: a run descritiva genoma x dono com a sonda das duas TVs (docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md;
docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 7 e 9, a linha P1e).

Cada unidade (base, k) tem uma semente (o mundo, a grade da TV e a politica) e um genoma da visao, derivados por `derivar_semente`
("gosto-visual" e "gosto-visual-genoma", a regra E3 sem prefixo novo na bancada). A unidade vive seis vidas: o genoma proprio e o vazio
(o controle) x os tres donos (`nenhum`, `calmo`, `agitado`; secao 2.3 do plano). A vida e a do laboratorio com o olhar (o REL da C4 com a
subchave `olhar`, o mesmo do gabarito da P1f), o corpo do v11 com a tela, a TV do jogo, 14 dias. Os 7 primeiros dias sao a
familiarizacao (secao 2.2); a sonda das duas TVs (experiments/sonda_duas_tvs.py) roda nos dias 7 a 13, 3 replicas por dia. Toda vida e
gravada, rejogada do disco (G1) e conferida; a sonda confere o G2. As medidas saem de `metrics.medidas_duas_tvs` e
`metrics.familiarizacao_tv`; a analise e a da secao 5 do plano, descritiva (nao ha gate).

A GV3b (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md): a mesma run com o enjoo da imagem ligado no corpo e no cerebro
(`CONFIG_ENJOO_TELA_LIGADA`, D-GV-ENJOO-CER), escolhida pela fase da config (`gosto_visual_enjoo`), com a faixa 90101...90505 e as pastas
`piloto_enjoo` e `gosto_visual_enjoo`. Tudo o mais e o da GV3. Com as configs antigas (fase `gosto_visual`), o orquestrador faz o que fazia.

O adendo 2 da GV3b (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md): a GV3b de novo, depois que a run do adendo 1 parou porque as duas TVs
nao couberam (D-GV-GV3B-12). A fase `gosto_visual_enjoo2` escolhe a regra "sem_sonda" da sonda (a replica sem lugar fica sem sonda e e
contada, com o teto TETO_SEM_LUGAR), a faixa 91101...91505 e as pastas `piloto_enjoo2` e `gosto_visual_enjoo2`; a run so roda com a pasta
do piloto no git, o piloto aprovado na conferencia e o git limpo. As fases antigas seguem com a regra "falha", e os artefatos delas saem
os de antes. A faixa 90101...90505 esta queimada: as configs do adendo 1 nao passam mais na trava.

A trava (secao 9 do plano): o piloto e a run so rodam com o cabecalho do plano "APROVADO pelo Matheus", a faixa 89101...89505 em
FAIXAS_RESERVADAS, a secao do registro da run no plano, as bases e o K do plano, no maximo 4 processos e nada por cima de uma pasta que ja
existe. A fumaca (as sementes dos testes, 101...505) roda sem a faixa e sem o registro, com 2 a 14 dias (a sonda so no ultimo dia).

    python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/piloto.json --processos 4
    python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/gosto_visual.json --processos 4
    python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/piloto_enjoo.json --processos 4
    python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/gosto_visual_enjoo.json --processos 4
    python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/piloto_enjoo2.json --processos 4
    python experiments/run_v3_gosto_visual.py --config experiments/configs/v3_gosto_visual/gosto_visual_enjoo2.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import time
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gosto_visual as X  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402
from bancada.faixas import FAIXAS_QUEIMADAS, FAIXAS_RESERVADAS  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.config import CONFIG_ENJOO_TELA_LIGADA, CONFIG_PADRAO, CONFIG_TV_LIGADA  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.genoma_visao import genoma_visao, genoma_visao_vazio  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, centro_da_celula  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md"
MARCA_APROVADO = "**Status: APROVADO pelo Matheus"
TITULO_REGISTRO = "## 11. O registro da run"
FASE = "gosto_visual"
FAIXA = (89101, 89505)                                       # confirmada pelo coordenador, 2026-11-11
BASES_PILOTO = (89101, 89202)                                # secao 6 do plano
BASES_RUN = (89303, 89404, 89505)
K_PILOTO, K_RUN = 2, 12                                      # PROPOSTOS, SEM FONTE (secao 6)
FLUXO_UNIDADE = "gosto-visual"
GENOMAS = ("proprio", "vazio")                               # secao 2.1
DONOS = ("nenhum", "calmo", "agitado")                       # secao 2.3
DIAS = 14                                                    # PROPOSTO, SEM FONTE (secao 2.2)
DIAS_FAMILIARIZACAO = 7                                      # PROPOSTO, SEM FONTE (secao 2.2)
TOLERANCIA_FAMILIARIZACAO = 0.05                             # PROPOSTO, SEM FONTE: ~2 erros-padrao binomiais da diferenca (secao 2.2)
REPLICAS = sd.REPLICAS
HORA = 60
TROCA_DONO_HORAS = 1                                         # PROPOSTO, SEM FONTE: o dono poe o programa dele a cada hora (secao 2.3)
FRACAO_MINIMA_OLHOU = 0.25                                   # PROPOSTO, SEM FONTE: a conferencia do piloto (secao 6)
MAX_PROCESSOS = 4                                            # V3-D8
BOOTSTRAP = 2000
SAIDA = "artifacts_v3_gosto_visual"
CHAVES_CONFIG = {"descricao", "fase", "plano", "unidades", "dias"}
PERFIL_DO_DONO = {"calmo": sd.PERFIL_A, "agitado": sd.PERFIL_B}
# a GV3b (o adendo 1): o enjoo ligado; o resto e o da GV3
FASE_ENJOO = "gosto_visual_enjoo"
PLANO_ENJOO = "docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md"
TITULO_REGISTRO_ENJOO = "## 9. O registro da run"
FAIXA_ENJOO = (90101, 90505)                                 # confirmada pelo coordenador, 2026-11-12
BASES_PILOTO_ENJOO = (90101, 90202)                          # secao 6 do adendo (o molde da 89xxx)
BASES_RUN_ENJOO = (90303, 90404, 90505)
# o adendo 2 da GV3b: a regra "sem_sonda" para as duas TVs sem lugar, a faixa nova e o piloto no git antes da run
FASE_ENJOO2 = "gosto_visual_enjoo2"
PLANO_ENJOO2 = "docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md"
TITULO_REGISTRO_ENJOO2 = "## 8. O registro da run"
FAIXA_ENJOO2 = (91101, 91505)                                # confirmada pelo coordenador, 2026-11-12
BASES_PILOTO_ENJOO2 = (91101, 91202)                         # secao 6 do adendo 2 (o molde da 89xxx e da 90xxx)
BASES_RUN_ENJOO2 = (91303, 91404, 91505)
TETO_SEM_LUGAR = 0.05                                        # PROPOSTO, SEM FONTE: o adendo 2, secao 2 (D-GV-GV3B2-2)
# por fase: o plano, o titulo do registro, a faixa, as bases do piloto e da run, os nomes dos modos (as pastas), o enjoo, a regra da sonda
# para as duas TVs sem lugar e os planos por baixo (que tambem tem de estar aprovados)
FASES = {FASE: {"plano": PLANO, "registro": TITULO_REGISTRO, "faixa": FAIXA, "piloto": BASES_PILOTO, "run": BASES_RUN,
                "modos": ("piloto", FASE), "enjoo": False, "sem_lugar": "falha", "base": ()},
         FASE_ENJOO: {"plano": PLANO_ENJOO, "registro": TITULO_REGISTRO_ENJOO, "faixa": FAIXA_ENJOO, "piloto": BASES_PILOTO_ENJOO,
                      "run": BASES_RUN_ENJOO, "modos": ("piloto_enjoo", FASE_ENJOO), "enjoo": True, "sem_lugar": "falha",
                      "base": ((PLANO, TITULO_REGISTRO),)},
         FASE_ENJOO2: {"plano": PLANO_ENJOO2, "registro": TITULO_REGISTRO_ENJOO2, "faixa": FAIXA_ENJOO2, "piloto": BASES_PILOTO_ENJOO2,
                       "run": BASES_RUN_ENJOO2, "modos": ("piloto_enjoo2", FASE_ENJOO2), "enjoo": True, "sem_lugar": "sem_sonda",
                       "base": ((PLANO, TITULO_REGISTRO), (PLANO_ENJOO, TITULO_REGISTRO_ENJOO))}}


# ================================================================== a trava
def _plano(plano: str = PLANO) -> str:
    return (RAIZ / plano).read_text(encoding="utf-8")


def exigir_plano_aprovado(texto: str, titulo_registro: str = TITULO_REGISTRO) -> None:
    linhas = texto.splitlines()
    status = next((x for x in linhas[1:12] if x.startswith("**Status:")), None)
    if status is None or not status.startswith(MARCA_APROVADO):
        raise RuntimeError("o plano do GOSTO_VISUAL sem o status APROVADO pelo Matheus no cabecalho: nenhuma vida da faixa")
    if sum(1 for x in linhas if x.startswith(titulo_registro)) != 1:
        raise RuntimeError(f"o plano sem a secao {titulo_registro!r} (o registro da run): nenhuma vida da faixa")


def exigir_faixa_reservada(faixa: tuple = FAIXA) -> None:
    if not any((lo, hi) == faixa for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {faixa[0]}...{faixa[1]} nao esta em FAIXAS_RESERVADAS")
    if any(lo <= faixa[1] and faixa[0] <= hi for lo, hi, _ in FAIXAS_QUEIMADAS):
        raise bv.SementeSemPlano(f"a faixa {faixa} cruza uma faixa queimada")


def modo_da_config(cfg: dict, texto_plano: str | None = None) -> str:
    """'fumaca' (as sementes dos testes), 'piloto' ou 'gosto_visual' (o plano a letra; a trava); na fase da GV3b, 'fumaca',
    'piloto_enjoo' ou 'gosto_visual_enjoo' (o adendo 1 a letra, com o plano da GV3 tambem aprovado); o resto falha alto"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] not in FASES:
        raise ValueError(f"fase {cfg['fase']!r}: so {sorted(FASES)}")
    f = FASES[cfg["fase"]]
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if type(u.get("k")) is not int or u["k"] < 1 or set(u) != {"bases", "k"}:
        raise ValueError(f"unidades {u!r}: so as bases e o K >= 1")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 2 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 2 a {DIAS}")
        return "fumaca"
    if bases == f["piloto"]:
        modo, k = f["modos"][0], K_PILOTO
    elif bases == f["run"]:
        modo, k = f["modos"][1], K_RUN
    else:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca), {list(f['piloto'])} ou {list(f['run'])}")
    exigir_faixa_reservada(f["faixa"])
    exigir_plano_aprovado(_plano(f["plano"]) if texto_plano is None else texto_plano, f["registro"])
    for plano_base, titulo in f["base"]:                     # o adendo vale sobre o plano da GV3 (e o 2 sobre o 1): aprovados tambem
        exigir_plano_aprovado(_plano(plano_base), titulo)
    erros = [f"dias {cfg['dias']}"] if cfg["dias"] != DIAS else []
    erros += [f"K {u['k']}"] if u["k"] != k else []
    erros += [f"plano {cfg.get('plano')!r}"] if cfg.get("plano") != f["plano"] else []
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return modo


def unidades(bases, k: int) -> list[dict]:
    """a regra E3 (secao 6 do plano): a semente derivar_semente("gosto-visual", b, k) e o genoma derivar_semente("gosto-visual-genoma",
    b, k); falha alto com base repetida, colisao ou um valor numa faixa reservada"""
    bases = list(bases)
    if len(set(bases)) != len(bases):
        raise ValueError(f"base repetida: {bases}")
    out = [{"base": b, "k": j, "semente": derivar_semente(FLUXO_UNIDADE, b, j), "genoma": derivar_semente(f"{FLUXO_UNIDADE}-genoma", b, j)}
           for b in bases for j in range(k)]
    valores = [x["semente"] for x in out] + [x["genoma"] for x in out]
    if len(set(valores)) != len(valores):
        raise ValueError("colisao entre sementes e genomas derivados")
    if any(bv.na_faixa_reservada(v) for v in valores):
        raise ValueError("uma semente derivada caiu numa faixa reservada")
    return out


def dias_da_sonda(dias: int) -> tuple[int, ...]:
    """os dias 7 a 13 na run; na fumaca, so o ultimo"""
    return tuple(range(DIAS_FAMILIARIZACAO, DIAS)) if dias == DIAS else (dias - 1,)


# ================================================================== a vida
_CORPO = None


def _cc():
    global _CORPO
    if _CORPO is None:
        _CORPO = X._cc()
    return _CORPO


def fabricas(semente: int, genoma, enjoo: bool = False) -> tuple:
    """(fabrica da politica, fabrica do motor) da vida, reusadas no replay e na copia da sonda. `enjoo` (a GV3b): a
    CONFIG_ENJOO_TELA_LIGADA no cerebro e no corpo; desligado, o caminho de antes, sem o argumento"""
    cv, co = X.config_vida(), X.config_olhar("grade")
    kw = {"cfg_enjoo_tela": CONFIG_ENJOO_TELA_LIGADA} if enjoo else {}

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cv, orq.CM, semente=semente, cfg_olhar=co, genoma_visao_ovo=genoma, **kw)

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=_cc(),
                                     cfg_tela=X.TELA, cfg_tv=CONFIG_TV_LIGADA, **kw)
    return fp, fm


def programa_do_dono(dono: str, programas: tuple) -> int | None:
    """o programa da grade que o dono poe (secao 2.3): o mais perto (L1) do perfil do dono, o menor indice no empate; `nenhum`: None"""
    if dono not in DONOS:
        raise ValueError(f"dono desconhecido: {dono!r}")
    if dono == "nenhum":
        return None
    alvo = PERFIL_DO_DONO[dono]
    return min(range(len(programas)), key=lambda i: (sum(abs(a - b) for a, b in zip(programas[i], alvo)), i))


def viver(genoma_tipo: str, dono: str, unidade: dict, dias: int, fim_do_dia=None, enjoo: bool = False):
    """a vida (secao 2): devolve (motor, fabricas, o programa do dono). `fim_do_dia(dia, motor, fabricas)`, se dado, e chamado no fim de
    cada dia (so o teste do G2 o usa, para pr a sonda no meio da vida). `enjoo`: a GV3b (o enjoo ligado)"""
    if genoma_tipo not in GENOMAS:
        raise ValueError(f"genoma desconhecido: {genoma_tipo!r}")
    semente = unidade["semente"]
    g = genoma_visao(unidade["genoma"]) if genoma_tipo == "proprio" else genoma_visao_vazio()
    fab = fabricas(semente, g, enjoo)
    fp, fm = fab
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)
    prog = programa_do_dono(dono, m.mundo.tv.programas)
    x, y = centro_da_celula(orq.CM.layout.comedouro, orq.CM)
    for h in range(dias * 24):
        if prog is not None and h % TROCA_DONO_HORAS == 0 and m.estado()["tv"]["programa"] != prog:
            m.trocar_canal(prog)
        m.avancar(HORA)
        if h % 3 == 0:
            m.deixar_comida("racao", x, y)
        if h % 5 == 2 and not m.estado()["dormindo"]:
            m.observar(AcaoUsuario.ACARICIAR)
        if fim_do_dia is not None and h % 24 == 23:
            fim_do_dia(h // 24, m, fab)
    return m, fab, prog


def fracoes_olhando(motor, dias: int) -> list[float]:
    """por dia, a fracao das decisoes acordadas em que o cerebro escolheu olhar a TV da vida (secao 2.2)"""
    c = sd.cerebro_da_copia(motor)
    por_dia = 1440 // CONFIG_PADRAO.intervalo_decisao_ticks
    if len(c.motivos) != dias * por_dia:
        raise RuntimeError(f"{len(c.motivos)} decisoes em {dias} dias: eram {dias * por_dia}")
    out = []
    for d in range(dias):
        ms = c.motivos[d * por_dia:(d + 1) * por_dia]
        acordadas = [x for x in ms if x["acao"] != "dormir"]
        out.append(0.0 if not acordadas else sum(1 for x in acordadas if x["olhar"]["olha"] is not None) / len(acordadas))
    return out


def _vida(cfg: dict, genoma_tipo: str, dono: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    semente, dias = unidade["semente"], cfg["dias"]
    fase = FASES[cfg["fase"]]
    motor, fab, prog = viver(genoma_tipo, dono, unidade, dias, enjoo=fase["enjoo"])
    nome = f"{genoma_tipo}_{dono}_{semente}"
    arquivo = Path(pasta) / "vidas" / f"{nome}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, semente, arquivo.read_text(encoding="utf-8"))
    fr = fracoes_olhando(motor, dias)
    familiar = fr[:min(DIAS_FAMILIARIZACAO, dias - 1)]
    crit = M.familiarizacao_tv(familiar, TOLERANCIA_FAMILIARIZACAO) if len(familiar) >= 4 else None
    s = sd.sonda(motor, fab, semente, dias_da_sonda(dias), REPLICAS, fase["sem_lugar"])
    bv._gravar(Path(pasta) / "vidas" / f"{nome}_sonda.json", bv._dump(s))
    medidas = [{"dia": d["dia"], "replica": r["replica"], **M.medidas_duas_tvs(r, sd.JANELA_TICKS),
                "agrado_inato": r["agrado"]["A"]["inato"] - r["agrado"]["B"]["inato"],
                "agrado_agora": r["agrado"]["A"]["agora"] - r["agrado"]["B"]["agora"]}
               for d in s["por_dia"] for r in d["replicas"] if "sem_lugar" not in r]
    sem_lugar = [{"dia": d["dia"], **r} for d in s["por_dia"] for r in d["replicas"] if "sem_lugar" in r]
    extra = {} if fase["sem_lugar"] == "falha" else {"replicas_sem_lugar": sem_lugar}   # o adendo 2; as fases antigas, o de antes
    return {"vida": f"{genoma_tipo}|{dono}|{semente}", "genoma_tipo": genoma_tipo, "dono": dono, "semente": semente,
            "base": unidade["base"], "k": unidade["k"], "programa_do_dono": prog, "fracoes_olhando": fr, "familiarizacao": crit,
            "dias_sem_sonda": sum(1 for d in s["por_dia"] if d["tick"] is None), "medidas": medidas,
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}, **extra}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, g, d, unidade, pasta) for g in GENOMAS for d in DONOS]


# ================================================================== a analise (secao 5 do plano; descritiva)
def _media(v: list[float]) -> float | None:
    return sum(v) / len(v) if v else None


def por_pet(r: dict) -> dict:
    """as medias do pet (secao 4.2): cada medida sobre as replicas validas de todos os dias da sonda"""
    def med(campo: str) -> float | None:
        return _media([x[campo] for x in r["medidas"] if x[campo] is not None])
    inatos = {x["agrado_inato"] for x in r["medidas"]}
    if len(inatos) > 1:
        raise RuntimeError(f"{r['vida']}: o agrado inato mudou na vida: {sorted(inatos)}")
    return {"escolha": med("escolha"), "tempo_relativo": med("tempo_relativo"), "tempo_total": med("tempo_total"),
            "agrado_inato": inatos.pop() if inatos else None, "agrado_agora": med("agrado_agora"),
            "validas": sum(1 for x in r["medidas"] if x["escolha"] is not None), "replicas": len(r["medidas"])}


def _spearman_seguro(xs: list, ys: list) -> float | None:
    try:
        return M.spearman(xs, ys)
    except ValueError:
        return None


def _boot(unids: list, estat, rotulo: tuple, boot: int) -> dict:
    """o ponto e o IC95 percentil do bootstrap que reamostra unidades inteiras (a unidade leva as seis vidas); reamostras indefinidas
    ficam fora dos percentis e sao contadas"""
    ponto = estat(unids)
    rng = random.Random(derivar_semente("gosto-visual-boot", *rotulo))
    reams, indef = [], 0
    for _ in range(boot):
        v = estat([unids[rng.randrange(len(unids))] for _ in unids]) if unids else None
        if v is None:
            indef += 1
        else:
            reams.append(v)
    return {"ponto": ponto, "ic95": M.ic_percentil(reams) if len(reams) >= 2 else None, "indefinidas": indef, "unidades": len(unids)}


def _sem_variancia(valores: list) -> bool:
    return len(valores) >= 1 and len(set(valores)) == 1


def analisar(registros: list[dict], boot: int = BOOTSTRAP, so_estaveis: bool = False) -> dict:
    """secao 5: por celula genoma x dono, a escolha, o tempo relativo e o tempo total (as medias dos pets); a parte do genoma (o Spearman
    do agrado inato com cada medida, nos genomas proprios, dentro do dono); a parte do dono (as diferencas entre os donos dentro da
    unidade, em cada genoma) e a interacao; a divergencia; a repetibilidade; a regra das medidas sem variancia (secao 5.6)."""
    pets = {}
    for r in registros:
        chave = (r["base"], r["k"], r["genoma_tipo"], r["dono"])
        if chave in pets:
            raise RuntimeError(f"vida repetida: {chave}")
        estavel = r["familiarizacao"] is None or r["familiarizacao"]["estavel"]
        if so_estaveis and not estavel:
            continue
        pets[chave] = {**por_pet(r), "registro": r}
    unids = sorted({(b, k) for b, k, _, _ in pets})
    medidas = ("escolha", "tempo_relativo", "tempo_total")
    out = {"pets": len(pets), "unidades": len(unids), "celulas": {}, "genoma": {}, "dono": {}, "interacao": {}, "repetibilidade": {}}
    for g in GENOMAS:
        for d in DONOS:
            ps = [p for (b, k, gg, dd), p in pets.items() if gg == g and dd == d]
            cel = {"pets": len(ps), "sem_sonda_valida": sum(1 for p in ps if p["escolha"] is None)}
            for med in medidas:
                v = [p[med] for p in ps if p[med] is not None]
                cel[med] = {"media": _media(v), "n": len(v), "sem_variancia": _sem_variancia(v)}
            out["celulas"][f"{g}|{d}"] = cel
    for d in DONOS:                                          # a parte do genoma (5.2)
        for med in ("escolha", "tempo_relativo"):
            def estat(us, d=d, med=med):
                xs, ys = [], []
                for u in us:
                    p = pets.get((*u, "proprio", d))
                    if p is not None and p[med] is not None:
                        xs.append(p["agrado_inato"])
                        ys.append(p[med])
                return _spearman_seguro(xs, ys)
            out["genoma"][f"{d}|{med}"] = _boot(unids, estat, ("genoma", d, med), boot)
    pares = (("calmo", "agitado"), ("calmo", "nenhum"), ("agitado", "nenhum"))
    for g in GENOMAS:                                        # a parte do dono (5.3)
        for a, b in pares:
            for med in ("escolha", "tempo_relativo"):
                def estat(us, g=g, a=a, b=b, med=med):
                    dif = [pets[(*u, g, a)][med] - pets[(*u, g, b)][med] for u in us
                           if (*u, g, a) in pets and (*u, g, b) in pets and pets[(*u, g, a)][med] is not None
                           and pets[(*u, g, b)][med] is not None]
                    return _media(dif)
                out["dono"][f"{g}|{a}-{b}|{med}"] = _boot(unids, estat, ("dono", g, a, b, med), boot)
    for med in ("escolha", "tempo_relativo"):                # a interacao (5.4): o efeito calmo - agitado no proprio menos no vazio
        def estat(us, med=med):
            dif = []
            for u in us:
                ks = [(*u, g, d) for g in GENOMAS for d in ("calmo", "agitado")]
                if all(x in pets and pets[x][med] is not None for x in ks):
                    p = [pets[x][med] for x in ks]
                    dif.append((p[0] - p[1]) - (p[2] - p[3]))
            return _media(dif)
        out["interacao"][med] = _boot(unids, estat, ("interacao", med), boot)
    ambos = [p for p in pets.values() if p["escolha"] is not None and p["tempo_relativo"] is not None]
    out["divergencia"] = {"pets": len(ambos),                # 5.5: a divergencia e dado
                          "sinais_opostos": sum(1 for p in ambos if (p["escolha"] - 0.5) * (p["tempo_relativo"] - 0.5) < 0),
                          "spearman_escolha_tempo": _spearman_seguro([p["escolha"] for p in ambos], [p["tempo_relativo"] for p in ambos])}
    for g in GENOMAS:                                        # 5.7: a repetibilidade, R_pet entre os dias, nas medias do dia
        for med in ("escolha", "tempo_relativo"):
            estat_pets = []
            for (b, k, gg, d), p in pets.items():
                if gg != g:
                    continue
                dias: dict[int, list[float]] = {}
                for x in p["registro"]["medidas"]:
                    if x[med] is not None:
                        dias.setdefault(x["dia"], []).append(x[med])
                if dias:
                    estat_pets.append(M.estatisticas_grupo([_media(v) for v in dias.values()]))
            try:
                out["repetibilidade"][f"{g}|{med}"] = M.icc1_estatisticas(estat_pets)["r"]
            except ValueError:
                out["repetibilidade"][f"{g}|{med}"] = None
    return out


def familiarizacao(registros: list[dict]) -> dict:
    """secao 2.2: quantos pets ficaram estaveis, por celula"""
    out = {}
    for g in GENOMAS:
        for d in DONOS:
            rs = [r for r in registros if r["genoma_tipo"] == g and r["dono"] == d]
            cs = [r["familiarizacao"] for r in rs if r["familiarizacao"] is not None]
            out[f"{g}|{d}"] = {"vidas": len(rs), "com_criterio": len(cs), "estaveis": sum(1 for c in cs if c["estavel"]),
                               "fracao_media_olhando": _media([f for r in rs for f in r["fracoes_olhando"]])}
    cs = [r["familiarizacao"] for r in registros if r["familiarizacao"] is not None]
    est = sum(1 for c in cs if c["estavel"])
    # secao 2.2: com menos da metade das vidas estaveis, o resultado registra que a familiarizacao nao estabilizou em 7 dias
    out["total"] = {"com_criterio": len(cs), "estaveis": est, "nao_estabilizou": bool(cs) and 2 * est < len(cs)}
    return out


def contar_sem_lugar(registros: list[dict], teto: float = TETO_SEM_LUGAR) -> dict:
    """o adendo 2, secao 2: as replicas sem sonda porque as duas TVs nao couberam, no total e por celula genoma x dono, contra o teto.
    A fracao e sobre todas as replicas tentadas (as medidas mais as sem lugar). Passar do teto no total ou numa celula e escrito na leitura
    e, no piloto, segura a run"""
    def conta(rs):
        n_sem = sum(len(r["replicas_sem_lugar"]) for r in rs)
        n = n_sem + sum(len(r["medidas"]) for r in rs)
        return {"tentadas": n, "sem_lugar": n_sem, "fracao": n_sem / n if n else 0.0}
    out = {"teto": teto, "total": conta(registros), "celulas": {}}
    for g in GENOMAS:
        for d in DONOS:
            out["celulas"][f"{g}|{d}"] = conta([r for r in registros if r["genoma_tipo"] == g and r["dono"] == d])
    acima = [k for k, c in out["celulas"].items() if c["fracao"] > teto]
    out["celulas_acima_do_teto"] = acima
    out["passou_do_teto"] = out["total"]["fracao"] > teto or bool(acima)
    return out


def exigir_piloto_no_git(fase: dict) -> None:
    """o adendo 2, secao 7: a run so roda com a pasta do piloto commitada (o `git_limpo` da run sai verdadeiro; o segundo problema da
    D-GV-GV3B-12), o git limpo e o piloto aprovado na conferencia; senao, falha alto antes de qualquer vida"""
    rc = orq.rc
    rel = f"{SAIDA}/{fase['modos'][0]}"
    for n in ("meta.json", "medidas.json", "analise.json", "custo.json", "vidas.tar.gz"):
        if rc._git("ls-files", f"{rel}/{n}") != f"{rel}/{n}":
            raise RuntimeError(f"o piloto fora do git: {rel}/{n} (o adendo 2, secao 7): nenhuma vida da run")
    if rc._git("status", "--porcelain") != "":
        raise RuntimeError("o git nao esta limpo (o adendo 2, secao 7): nenhuma vida da run")
    analise = json.loads((RAIZ / rel / "analise.json").read_text(encoding="utf-8"))
    if analise["conferencia"]["a_run_pode_rodar"] is not True:
        raise RuntimeError("o piloto nao passou na conferencia (a GVP-7 ou o teto das replicas sem lugar): a run nao roda")


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None, boot: int = BOOTSTRAP) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima")
    us = unidades(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]))
    fase = FASES[cfg["fase"]]
    if fase["sem_lugar"] == "sem_sonda" and modo == fase["modos"][1]:
        exigir_piloto_no_git(fase)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": cfg["fase"], "plano": fase["plano"], "plano_sha256": rc._sha_arquivo(RAIZ / fase["plano"]), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "sonda_sha256": rc._sha_arquivo(Path(sd.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": us, "genomas": list(GENOMAS), "donos": list(DONOS), "replicas": REPLICAS, "bootstrap": boot,
            "dias_sonda": list(dias_da_sonda(cfg["dias"])),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "tv.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    if fase["enjoo"]:                                        # a GV3b: o plano da GV3 por baixo do adendo, a config do enjoo e o corpo
        meta["plano_base"] = PLANO
        meta["plano_base_sha256"] = rc._sha_arquivo(RAIZ / PLANO)
        meta["enjoo_tela"] = asdict(CONFIG_ENJOO_TELA_LIGADA)
        meta["sha256"] |= {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("corpo.py", "motor_corpo.py")}
    if fase["sem_lugar"] != "falha":                         # o adendo 2: a regra, o teto e o adendo 1 por baixo
        meta["sem_lugar"] = {"regra": fase["sem_lugar"], "teto": TETO_SEM_LUGAR}
        meta["plano_adendo1"] = PLANO_ENJOO
        meta["plano_adendo1_sha256"] = rc._sha_arquivo(RAIZ / PLANO_ENJOO)
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in us], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(us) * len(GENOMAS) * len(DONOS):
        raise RuntimeError(f"{len(registros)} vidas, eram {len(us) * len(GENOMAS) * len(DONOS)}")
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    lidos = list(json.loads((pasta / "medidas.json").read_text(encoding="utf-8")).values())   # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": cfg["fase"], "plano": fase["plano"], "vidas": len(lidos), "familiarizacao": familiarizacao(lidos),
                 "principal": analisar(lidos, boot, so_estaveis=False), "so_estaveis": analisar(lidos, boot, so_estaveis=True)}
    reps = [x for r in lidos for x in r["medidas"]]
    olhou = sum(1 for x in reps if x["escolha"] is not None) / len(reps) if reps else 0.0
    # secao 6 do plano: o piloto so confere que o pet olha; abaixo de 1 replica em 4, a run nao roda e o caso volta ao Matheus
    resultado["conferencia"] = {"replicas": len(reps), "fracao_olhou": olhou, "minimo": FRACAO_MINIMA_OLHOU,
                                "a_run_pode_rodar": olhou >= FRACAO_MINIMA_OLHOU}
    if fase["sem_lugar"] != "falha":                         # o adendo 2: a contagem das sem lugar e o teto; no piloto, o teto segura a run
        resultado["sem_lugar"] = contar_sem_lugar(lidos)
        resultado["conferencia"]["sem_lugar_passou_do_teto"] = resultado["sem_lugar"]["passou_do_teto"]
        resultado["conferencia"]["a_run_pode_rodar"] = olhou >= FRACAO_MINIMA_OLHOU and not resultado["sem_lugar"]["passou_do_teto"]
    bv._gravar(pasta / "analise.json", bv._dump(resultado))
    custos = [r["custo"]["vida_parede"] for r in registros]
    bv._gravar(pasta / "custo.json", bv._dump({"vidas": len(custos), "parede_media_s": _media(custos), "parede_max_s": max(custos),
                                               "total_parede_s": meta["vidas_parede_s"]}))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "analise.json", "custo.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA}/)")
    pasta = Path(a.saida) if a.saida else RAIZ / SAIDA / modo
    r = rodar(cfg, pasta, a.processos, caminho)["resultado"]
    print(json.dumps({"modo": r["modo"], "vidas": r["vidas"], "familiarizacao": r["familiarizacao"]}, indent=1, ensure_ascii=True,
                     default=str)[:3000])


if __name__ == "__main__":
    main()
