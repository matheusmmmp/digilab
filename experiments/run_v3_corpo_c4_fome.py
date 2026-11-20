"""CORPO C4: o replay da fome sobre as vidas ja gravadas da run da C4 (sem vida nova, sem faixa nova, sem teste).

Um descritivo ACRESCENTADO DEPOIS da aprovacao do plano (sugestao da Gerencia, aceita pelo Matheus em 2026-11-20 como "Replay
depois"): a fome media e a fracao do tempo com a fome acima de 0,5 (o teto C/2 do braco DTB), por lugar e por celula. Nao entra na
leitura da secao 6 do plano, nao tem classe nem p, e nao muda regra nenhuma: o orquestrador da run (`run_v3_corpo_c4.py`) fica intacto.
Este script:
  - refaz cada vida do bloco I com o codigo da run (`run_v3_corpo_c3.viver`) e confere, antes de ler qualquer coisa, que o log refeito
    tem o `log_sha256` gravado no `medidas.json` da C4; se uma vida nao bate, para;
  - confere que o "Tempo bem" recalculado aqui e o do `medidas.json`, ate o ultimo float;
  - calcula a fome de cada vida nas decisoes dos dias 1 a 14 (`digilab.metrics.fome_nas_decisoes`) e resume os niveis dos dois bracos e
    DTB - CTRL (a media, o dp e o IC95 pelas unidades) por lugar, nas 12 celulas, nas 11 distintas e em cada celula.
O estado de cada decisao nao esta no `medidas.json` (o event sourcing): por isso a vida e refeita.

    python experiments/run_v3_corpo_c4_fome.py --config experiments/configs/v3_corpo_c4/run.json --processos 4
"""
from __future__ import annotations

import argparse
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
import run_v3_corpo_c4 as c4  # noqa: E402
import run_v3_corpo_tempo_bem as tb  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.metrics import fome_nas_decisoes, janela_dias  # noqa: E402

FONTE = RAIZ / "artifacts_v3_corpo" / "c4"
SAIDA = RAIZ / "artifacts_v3_corpo" / "c4_fome"
LIMIAR_FOME = 0.5                                # a fome no teto do DTB (C/2); o corte e do pedido, SEM FONTE
CONFERIDAS = ("tempo_bem", "privacao_vida", "exaustao_vida", "decisoes", "tempo_bem_8_14")
MEDIDAS = {"fome_media": lambda r: r["fome_media"], "fome_acima_do_teto": lambda r: r["fome_acima_do_teto"]}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fome_da_vida(estados, passo: int, dias: int) -> dict:
    """a fome de uma vida pelo Estado de cada decisao (`Registro.estados`: fome, ...; a decisao k no tick k x passo), dias 1 a `dias`"""
    f = fome_nas_decisoes([(k * passo, e[0]) for k, e in enumerate(estados)], janela_dias(1, dias), LIMIAR_FOME)
    return {"fome_media": f["media"], "fome_acima_do_teto": f["frac_acima"], "decisoes_fome": f["n"]}


def uma_vida(item: tuple) -> dict:
    braco, dono, lugar, base, semente, k, log_sha, gravadas, dias, orcamento = item
    motor, registro, _fab, _cat, _baixas = c3.viver(braco, dono, lugar, semente, dias, orcamento)
    rotulo = f"{braco}|{dono}|{lugar}|{semente}"
    if hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest() != log_sha:
        raise RuntimeError(f"FOME: a vida {rotulo} nao se refaz com o log_sha256 da C4")
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    refeitas = tb.medidas_da_vida(registro.estados, passo, dias)
    if tuple(refeitas[c] for c in CONFERIDAS) != tuple(gravadas):
        raise RuntimeError(f"FOME: o Tempo bem da vida {rotulo} nao e o do medidas.json da C4")
    return {"vida": rotulo, "braco": braco, "dono": dono, "lugar": lugar, "base": base, "semente": semente, "k": k,
            "tempo_bem": refeitas["tempo_bem"], **fome_da_vida(registro.estados, passo, dias)}


def resumir(linhas: list[dict]) -> dict:
    """os niveis dos dois bracos e DTB - CTRL, pareado por unidade (a media, o dp e o IC95, sem classe e sem p: so descritivo), por
    lugar, nas 12 celulas, nas 11 distintas e em cada celula"""
    grupos = [(lugar, c3._celulas(lugar)) for lugar in c4.LUGARES] + [("as 12 celulas", c4.CELULAS), ("as 11 celulas", c4.CELULAS_DISTINTAS)]
    out = {nome: {"por_lugar": {n: c4._descr(linhas, medida, cs) for n, cs in grupos},
                  "por_celula": {f"{d}|{lugar}": c4._descr(linhas, medida, ((d, lugar),)) for d, lugar in c4.CELULAS}}
           for nome, medida in MEDIDAS.items()}
    out["vidas"] = len(linhas)
    out["limiar_fome"] = LIMIAR_FOME
    return out


def rodar(config: Path, fonte: Path, saida: Path, processos: int) -> dict:
    if processos > c4.MAX_PROCESSOS:
        raise ValueError(f"no maximo {c4.MAX_PROCESSOS} processos (V3-D8)")
    if saida.exists():
        raise FileExistsError(f"{saida} ja existe: o replay se recusa a gravar por cima")
    cfg = json.loads(config.read_text(encoding="utf-8"))
    if c4.modo_da_config(cfg) != c4.FASE:
        raise ValueError("o replay so le a run da C4 (a config da run, nao a da fumaca)")
    meta_fonte = json.loads((fonte / "meta.json").read_text(encoding="utf-8"))
    if _sha(fonte / "medidas.json") != meta_fonte["artefatos_sha256"]["medidas.json"]:
        raise RuntimeError("o medidas.json da fonte nao tem o sha256 do meta.json da run")
    medidas = json.loads((fonte / "medidas.json").read_text(encoding="utf-8"))
    itens = [(r["braco"], r["dono"], r["lugar"], r["base"], r["semente"], r["k"], r["log_sha256"], tuple(r[c] for c in CONFERIDAS),
              cfg["dias"], cfg["orcamento_por_dia"]) for r in medidas]
    if len(itens) != len(c4.BRACOS) * len(c4.CELULAS) * len(cfg["unidades"]["bases"]):
        raise RuntimeError(f"{len(itens)} vidas na fonte: esperava os {len(c4.BRACOS)} bracos x 12 celulas x as unidades")
    saida.mkdir(parents=True)
    inicio, t0 = time.time(), time.perf_counter()
    with ProcessPoolExecutor(max_workers=processos) as ex:
        linhas = sorted(ex.map(uma_vida, itens, chunksize=8), key=lambda r: r["vida"])
    resumo = resumir(linhas)
    bv._gravar(saida / "fome.json", bv._dump(linhas))
    bv._gravar(saida / "resumo.json", bv._dump(resumo))
    rc = orq.rc
    meta = {"o_que_e": "replay da fome sobre as vidas da C4 (sem vida nova); descritivo acrescentado depois da aprovacao do plano",
            "fonte": rc._relativo(fonte), "fonte_sha256": {n: _sha(fonte / n) for n in ("medidas.json", "meta.json")},
            "bracos": list(c4.BRACOS), "config_arquivo": rc._relativo(config), "config_sha256": _sha(config), "vidas": len(linhas),
            "processos": processos, "limiar_fome": LIMIAR_FOME, "comando": " ".join(["python", *sys.argv]),
            "python": platform.python_version(), "git_head": rc._git("rev-parse", "HEAD"), "script_sha256": _sha(Path(__file__)),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py"), "orquestrador_c3_sha256": _sha(Path(c3.__file__)),
            "orquestrador_c4_sha256": _sha(Path(c4.__file__)),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio)), "duracao_s": time.perf_counter() - t0,
            "artefatos_sha256": {n: _sha(saida / n) for n in ("fome.json", "resumo.json")}}
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
    print(json.dumps({m: {n: {"niveis": v["niveis"], "DTB - CTRL": {c: v["DTB - CTRL"][c] for c in ("media", "ic95")}}
                          for n, v in r[m]["por_lugar"].items()} for m in MEDIDAS}, indent=1))


if __name__ == "__main__":
    main()
