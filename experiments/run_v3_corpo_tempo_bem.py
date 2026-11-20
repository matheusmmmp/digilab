"""CORPO: o replay de conferencia do "Tempo bem" sobre as vidas ja gravadas da C3 (sem vida nova, sem faixa nova).

O Matheus decidiu em 2026-11-20 a primaria de bem-estar: a fracao das decisoes sem privacao e sem exaustao, nos dias 1 a 14
(`digilab.metrics.tempo_bem_nas_decisoes`). "Antes de valer: um replay sobre as vidas da C3 confere que a fracao e calculavel." Este
script faz esse replay e mais nada:
  - refaz cada vida do CTRL e do DTB da C3 com o codigo da run (`run_v3_corpo_c3.viver`) e confere, antes de ler qualquer coisa, que o log
    refeito tem o `log_sha256` gravado no `medidas.json.gz` da C3; se uma vida nao bate, para;
  - confere que a privacao e a exaustao dos dias 8 a 14 recalculadas aqui sao as do `medidas.json.gz`, ate o ultimo float;
  - calcula o "Tempo bem" de cada vida (dias 1 a 14, e tambem 8 a 14) e resume DTB - CTRL por lugar, nas 12 celulas e nas 11 distintas.
O estado de cada decisao nao esta no `medidas.json` (o event sourcing): por isso a vida e refeita. Nada aqui muda a leitura da C3, e o
numero do DTB aqui nao e a validacao (a C3 escolheu o braco): ele so da o nivel e o desvio-padrao para o plano da C4.

    python experiments/run_v3_corpo_tempo_bem.py --config experiments/configs/v3_corpo_c3/run.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_corpo_c3 as c3  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.metrics import (JANELA_8_14, exaustao_nas_decisoes, janela_dias, privacao_nas_decisoes,  # noqa: E402
                             tempo_bem_nas_decisoes)

FONTE = RAIZ / "artifacts_v3_corpo" / "c3"
SAIDA = RAIZ / "artifacts_v3_corpo" / "c3_tempo_bem"
BRACOS = ("CTRL", "DTB")                         # os dois bracos da C4; a D e o DTL nao sao refeitos
MAX_PROCESSOS = c3.MAX_PROCESSOS
TEMPO_BEM = lambda r: r["tempo_bem"]             # noqa: E731
LUGARES = ("comedouro", "longe", "longe_fixo")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def medidas_da_vida(estados, passo: int, dias: int) -> dict:
    """o "Tempo bem" de uma vida, pelo Estado de cada decisao (`Registro.estados`: fome, higiene, energia, ...; a decisao k no tick k x
    passo): dias 1 a 14 (a primaria) e dias 8 a 14 (a janela das guardas de hoje), com a privacao e a exaustao das mesmas decisoes"""
    dec = [(k * passo, e[0], e[1], e[2]) for k, e in enumerate(estados)]
    vida = tempo_bem_nas_decisoes(dec, janela_dias(1, dias), orq.LIMIAR_PRIVACAO, orq.LIMIAR_EXAUSTAO)
    janela = tempo_bem_nas_decisoes(dec, JANELA_8_14 if dias >= 14 else janela_dias(1, dias), orq.LIMIAR_PRIVACAO, orq.LIMIAR_EXAUSTAO)
    return {"tempo_bem": vida["frac"], "privacao_vida": vida["frac_privacao"], "exaustao_vida": vida["frac_exaustao"],
            "decisoes": vida["n"], "tempo_bem_8_14": janela["frac"]}


def uma_vida(item: tuple) -> dict:
    braco, dono, lugar, base, semente, log_sha, privacao, exaustao, dias, orcamento = item
    motor, registro, _fab, _cat, _baixas = c3.viver(braco, dono, lugar, semente, dias, orcamento)
    rotulo = f"{braco}|{dono}|{lugar}|{semente}"
    if hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest() != log_sha:
        raise RuntimeError(f"TEMPO_BEM: a vida {rotulo} nao se refaz com o log_sha256 da C3")
    passo, es = CONFIG_PADRAO.intervalo_decisao_ticks, registro.estados
    ticks = [k * passo for k in range(len(es))]
    janela = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    p = privacao_nas_decisoes([(t, e[0], e[1], e[2], e[3]) for t, e in zip(ticks, es) if janela[0] <= t < janela[1]],
                              orq.LIMIAR_PRIVACAO)["fracao_privacao"]
    x = exaustao_nas_decisoes([(t, e[2]) for t, e in zip(ticks, es)], janela, orq.LIMIAR_EXAUSTAO)["frac"]
    if p != privacao or x != exaustao:
        raise RuntimeError(f"TEMPO_BEM: a privacao ou a exaustao da vida {rotulo} nao e a do medidas.json da C3")
    return {"vida": rotulo, "braco": braco, "dono": dono, "lugar": lugar, "base": base, "semente": semente, "k": 0,
            "privacao_8_14": p, "exaustao_8_14": x, **medidas_da_vida(es, passo, dias)}


def _contraste(linhas: list[dict], medida, celulas, nome: str) -> dict:
    e = c3.ma.estimativa(orq.por_unidade(linhas, "DTB", "CTRL", medida, celulas), c3.MARGEM)
    niveis = {b: sum(medida(r) for r in linhas if r["braco"] == b and (r["dono"], r["lugar"]) in celulas)
              / max(1, sum(1 for r in linhas if r["braco"] == b and (r["dono"], r["lugar"]) in celulas)) for b in BRACOS}
    return {**e, "contraste": "DTB - CTRL", "lugar": nome, "niveis": niveis}


def resumir(linhas: list[dict]) -> dict:
    """DTB - CTRL, pareado por unidade, com a classe da A6.6 (delta = 0,032), por lugar, nas 12 celulas, nas 11 distintas e em cada
    celula; para o "Tempo bem" dos dias 1 a 14 (a primaria) e, ao lado, o dos dias 8 a 14"""
    grupos = [(lugar, c3._celulas(lugar)) for lugar in LUGARES] + [("as 12 celulas", c3.CELULAS), ("as 11 celulas", c3.CELULAS_DISTINTAS)]
    out = {"tempo_bem": {n: _contraste(linhas, TEMPO_BEM, cs, n) for n, cs in grupos},
           "tempo_bem_8_14": {n: _contraste(linhas, lambda r: r["tempo_bem_8_14"], cs, n) for n, cs in grupos},
           "por_celula": {f"{d}|{lugar}": _contraste(linhas, TEMPO_BEM, ((d, lugar),), f"{d}|{lugar}") for d, lugar in c3.CELULAS}}
    out["vidas"] = len(linhas)
    out["vidas_no_piso_ou_teto"] = {"tempo_bem_0": sum(1 for r in linhas if r["tempo_bem"] == 0.0),
                                    "tempo_bem_1": sum(1 for r in linhas if r["tempo_bem"] == 1.0)}
    return out


def rodar(config: Path, fonte: Path, saida: Path, processos: int) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe: o replay se recusa a gravar por cima")
    cfg = json.loads(config.read_text(encoding="utf-8"))
    if c3.modo_da_config(cfg) != c3.FASE:
        raise ValueError("o replay so le a run da C3 (a config da run, nao a da fumaca)")
    medidas = json.loads(gzip.decompress((fonte / "medidas.json.gz").read_bytes()).decode("utf-8"))
    itens = [(r["braco"], r["dono"], r["lugar"], r["base"], r["semente"], r["log_sha256"], r["privacao"], r["exaustao"], cfg["dias"],
              cfg["orcamento_por_dia"]) for r in medidas if r["braco"] in BRACOS]
    if len(itens) != len(BRACOS) * len(c3.CELULAS) * len(cfg["unidades"]["bases"]):
        raise RuntimeError(f"{len(itens)} vidas na fonte: esperava os {len(BRACOS)} bracos x 12 celulas x as unidades")
    saida.mkdir(parents=True)
    inicio, t0 = time.time(), time.perf_counter()
    with ProcessPoolExecutor(max_workers=processos) as ex:
        linhas = sorted(ex.map(uma_vida, itens, chunksize=8), key=lambda r: r["vida"])
    resumo = resumir(linhas)
    bv._gravar(saida / "tempo_bem.json", bv._dump(linhas))
    bv._gravar(saida / "resumo.json", bv._dump(resumo))
    rc = orq.rc
    meta = {"o_que_e": "replay de conferencia do Tempo bem sobre as vidas da C3 (sem vida nova)", "fonte": rc._relativo(fonte),
            "fonte_sha256": {n: _sha(fonte / n) for n in ("medidas.json.gz", "meta.json")}, "bracos": list(BRACOS),
            "config_arquivo": rc._relativo(config), "config_sha256": _sha(config), "vidas": len(linhas), "processos": processos,
            "limiar_privacao": orq.LIMIAR_PRIVACAO, "limiar_exaustao": orq.LIMIAR_EXAUSTAO, "margem": c3.MARGEM,
            "comando": " ".join(["python", *sys.argv]), "python": platform.python_version(),
            "git_head": rc._git("rev-parse", "HEAD"), "script_sha256": _sha(Path(__file__)),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py"), "orquestrador_c3_sha256": _sha(Path(c3.__file__)),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio)), "duracao_s": time.perf_counter() - t0,
            "artefatos_sha256": {n: _sha(saida / n) for n in ("tempo_bem.json", "resumo.json")}}
    bv._gravar(saida / "meta.json", bv._dump(meta))
    return resumo


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--fonte", default=str(FONTE))
    ap.add_argument("--saida", default=str(SAIDA))
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    pre_run.exigir(__file__, a.config, a.processos)
    r = rodar(Path(a.config), Path(a.fonte), Path(a.saida), a.processos)
    print(json.dumps({k: {n: {c: v[c] for c in ("media", "ic95", "niveis")} for n, v in r[k].items()} for k in ("tempo_bem",)}, indent=1))


if __name__ == "__main__":
    main()
