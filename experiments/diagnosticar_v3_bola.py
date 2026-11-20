"""BOLA_DIAGNOSTICO (o replay R-b): em que elo o `brincar` deixa de virar chute, sobre vidas ja gravadas (sem vida nova, sem faixa).

As vidas nao se guardam inteiras (o event sourcing). Este script refaz cada vida com o codigo da run e confere que ela e a da run antes de
ler qualquer coisa dela; se uma nao bate, para:
  - `a0`: a VIVO dos 210 pares da SOCIAL_PAR A0 (as vidas do S0), pelo sha256 do registro e das posicoes no `.json.gz` do par;
  - `c3_par`: os pares do bloco II da CORPO C3, pelo registro do grupo igual, byte a byte, ao `.jsonl.gz` do `pares.tar.gz`;
  - `c3_vida`: uma amostra fixa das vidas de um pet da CORPO C3 (o braco CTRL, as primeiras bases, as 12 celulas), pelo `log_sha256` do
    `medidas.json.gz`.
So leitura: nenhuma medida de run muda e nada aqui e teste. A cadeia contada, por decisao `brincar` (docs/RESULTADO_V3_BOLA_DIAGNOSTICO.md):
  brincar -> a bola no raio da visao -> um alvo (a tentativa) -> chegou (o chute).

    python experiments/diagnosticar_v3_bola.py --c3 <pasta artifacts_v3_corpo/c3> --processos 2
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import platform
import subprocess
import sys
import tarfile
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import run_v3_corpo_c3 as c3  # noqa: E402
import run_v3_social_par_a0 as a0  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA  # noqa: E402
from digilab.grupo import sementes_do_grupo  # noqa: E402
from digilab.mundo import distancia, div_arred, regiao_de  # noqa: E402

A0_VIDAS = RAIZ / "artifacts_v3_social_par_a0" / "run" / "vidas"
SAIDA = RAIZ / "artifacts_v3_bola_diagnostico"
MAX_PROCESSOS = 4
BRACO_VIDAS = "CTRL"                        # as vidas de um pet lidas: so o braco de controle da C3 (o corpo de hoje)
FAIXAS_D = ("ate_pegar", "ate_um_passo", "ate_visao", "ate_2_visoes", "ate_4_visoes", "alem")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _bola_em(cm, b: dict, tick: int) -> tuple[int, int]:
    """a conta do `Mundo.bola_em`, sobre um estado guardado da bola"""
    if b["d"] == 0 or tick >= b["t0"] + -(-b["d"] // cm.atrito):
        return b["x1"], b["y1"]
    andou = cm.atrito * (tick - b["t0"])
    return b["x0"] + div_arred((b["x1"] - b["x0"]) * andou, b["d"]), b["y0"] + div_arred((b["y1"] - b["y0"]) * andou, b["d"])


def _estados_da_bola(mundo, cm) -> list[dict]:
    """os estados da bola na vida, em ordem: o do comeco e um por rolagem. Qualquer outra mudanca da bola (deixada, lancada, troca de
    ilha) falha alto: este diagnostico nao a refaz"""
    if mundo.bolas_deixadas or getattr(mundo, "lances", None) or getattr(mundo, "troca_ilha", None):
        raise RuntimeError("BOLA: a bola mudou de lugar por um caminho que o diagnostico nao refaz (deixada, lance ou troca de ilha)")
    bx, by = (c * cm.sub + cm.sub // 2 for c in cm.layout.bola_inicio)
    estados = [{"x0": bx, "y0": by, "x1": bx, "y1": by, "t0": 0, "d": 0}]
    for r in mundo.rolagens:
        (x0, y0), (x1, y1) = r["de"], r["para"]
        estados.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "t0": r["tick"], "d": distancia(x1 - x0, y1 - y0)})
    return estados


def cadeia_do_pet(motor, mundo, rotulos: dict) -> dict:
    """a cadeia do `brincar` de um pet numa vida ja vivida: decisao a decisao, a distancia do pet (no comeco da decisao) a bola, e o que o
    registro do motor (`decisoes_mundo`) diz do alvo e da chegada. A bola no tick da decisao e a de antes das rolagens desse tick"""
    cm = motor.cmf
    estados = _estados_da_bola(mundo, cm)
    visao, pegar, alcance = motor._raio_visao, motor._raio_pegar, motor._alcance
    cortes = (pegar, pegar + alcance, visao, 2 * visao, 4 * visao)
    nomes = [r[0] for r in cm.layout.regioes]
    c = Counter()
    por_regiao, dec_regiao, faixas, alvos, acoes_vista, depois = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    d_min = None
    dec = motor.decisoes_mundo
    for k, d in enumerate(dec):
        b = [e for e in estados if e["t0"] < d["tick"]] or estados[:1]
        bx, by = _bola_em(cm, b[-1], d["tick"])
        x0, y0 = d["antes"]
        dist = distancia(bx - x0, by - y0)
        d_min = dist if d_min is None else min(d_min, dist)
        regiao = nomes[regiao_de(x0, cm)]
        dec_regiao[regiao] += 1
        c["decisoes"] += 1
        a_vista = dist <= visao
        if a_vista:
            c["decisoes_bola_no_raio"] += 1
            acoes_vista[d["acao"]] += 1
        if d["brincou_com_bola"] and d["acao"] != "brincar":
            raise RuntimeError("BOLA: um chute fora do brincar")
        if d["acao"] != "brincar":
            continue
        c["brincar"] += 1
        por_regiao[regiao] += 1
        faixas[FAIXAS_D[next((i for i, lim in enumerate(cortes) if dist <= lim), len(cortes))]] += 1
        c["brincar_bola_no_raio"] += a_vista
        com_alvo = d["alvo"] is not None
        c["brincar_com_alvo"] += com_alvo
        alvos[str(d["alvo"])] += 1
        c["no_raio_sem_alvo"] += a_vista and not com_alvo
        c["fora_do_raio_com_alvo"] += com_alvo and not a_vista
        c["chutes"] += bool(d["brincou_com_bola"])
        if d["brincou_com_bola"] and not d["chegou"]:
            raise RuntimeError("BOLA: um chute sem a chegada")
        if com_alvo and not d["brincou_com_bola"]:
            c["tentativa_sem_chute"] += 1
            depois[dec[k + 1]["acao"] if k + 1 < len(dec) else "fim_da_vida"] += 1
    if c["chutes"] != sum(1 for d in dec if d["brincou_com_bola"]):
        raise RuntimeError("BOLA: a contagem dos chutes nao fecha")
    return {**rotulos, **{k: c[k] for k in ("decisoes", "decisoes_bola_no_raio", "brincar", "brincar_bola_no_raio", "brincar_com_alvo",
                                           "chutes", "no_raio_sem_alvo", "fora_do_raio_com_alvo", "tentativa_sem_chute")},
            "brincar_por_regiao": dict(por_regiao), "decisoes_por_regiao": dict(dec_regiao), "brincar_por_distancia": dict(faixas),
            "alvo_do_brincar": dict(alvos), "acoes_com_bola_no_raio": dict(acoes_vista), "depois_da_tentativa_sem_chute": dict(depois),
            "d_min_celulas": d_min / cm.sub, "rolagens_do_mundo": len(mundo.rolagens),
            "raios": {"visao": visao, "pegar": pegar, "alcance": alcance, "sub": cm.sub}}


# ================================================================== as tres fontes
def do_a0(arquivo: str) -> list[dict]:
    with gzip.open(arquivo, "rt", encoding="utf-8") as f:
        disco = json.load(f)
    s, pert = disco["semente"], tuple(disco["perturbacao"])
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    v = a0._viver(s, [a0._vivo("A", ss), a0._vivo("B", ss)], pert)
    if a0._sha_vida(v) != disco["sha256"]["VIVO"]:
        raise RuntimeError(f"BOLA: a VIVO do par {disco['par']} do A0 nao se refaz com o sha256 da run")
    return [cadeia_do_pet(v.grupo.motores[i], v.grupo.mundo,
                          {"fonte": "a0", "vida": disco["par"], "pet": i, "braco": "VIVO", "dono": a0.DONO, "lugar": "comedouro"})
            for i in "AB"]


def do_c3_par(item: tuple) -> list[dict]:
    braco, base, k, semente, gravado_sha = item
    v, _ss, _pert = c3.viver_par(braco, semente, c3_dias_pares())
    texto = v.grupo.registro.para_jsonl().encode("utf-8")
    if hashlib.sha256(texto).hexdigest() != gravado_sha:
        raise RuntimeError(f"BOLA: o par {braco}|{base}-{k:04d} da C3 nao se refaz com o registro gravado")
    return [cadeia_do_pet(v.grupo.motores[i], v.grupo.mundo,
                          {"fonte": "c3_par", "vida": f"{braco}|{base}-{k:04d}", "pet": i, "braco": braco, "dono": a0.DONO,
                           "lugar": "comedouro"}) for i in "AB"]


def do_c3_vida(item: tuple) -> list[dict]:
    dono, lugar, semente, log_sha, dias, orcamento = item
    motor, _registro, _fab, _cat, _baixas = c3.viver(BRACO_VIDAS, dono, lugar, semente, dias, orcamento)
    if hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest() != log_sha:
        raise RuntimeError(f"BOLA: a vida {BRACO_VIDAS}|{dono}|{lugar}|{semente} da C3 nao se refaz com o log_sha256 da run")
    return [cadeia_do_pet(motor, motor.mundo, {"fonte": "c3_vida", "vida": f"{BRACO_VIDAS}|{dono}|{lugar}|{semente}", "pet": "unico",
                                               "braco": BRACO_VIDAS, "dono": dono, "lugar": lugar})]


def c3_dias_pares() -> int:
    return json.loads((RAIZ / "experiments" / "configs" / "v3_corpo_c3" / "run.json").read_text(encoding="utf-8"))["pares"]["dias"]


def _fazer(tarefa: tuple) -> tuple:
    tipo, item = tarefa
    t = time.perf_counter()
    linhas = {"a0": do_a0, "c3_par": do_c3_par, "c3_vida": do_c3_vida}[tipo](item)
    return tipo, linhas, time.perf_counter() - t


# ================================================================== o resumo
CAMPOS = ("decisoes", "decisoes_bola_no_raio", "brincar", "brincar_bola_no_raio", "brincar_com_alvo", "chutes", "no_raio_sem_alvo",
          "fora_do_raio_com_alvo", "tentativa_sem_chute")
DICS = ("brincar_por_regiao", "decisoes_por_regiao", "brincar_por_distancia", "alvo_do_brincar", "acoes_com_bola_no_raio",
        "depois_da_tentativa_sem_chute")


def somar(linhas: list[dict]) -> dict:
    """a soma de um grupo de vidas de pet, com as medias por vida e as vidas em que cada elo aconteceu ao menos uma vez"""
    n = len(linhas)
    out: dict = {"vidas_de_pet": n}
    for campo in CAMPOS:
        out[campo] = sum(x[campo] for x in linhas)
        out[campo + "_vidas_com"] = sum(1 for x in linhas if x[campo] > 0)
    for campo in DICS:
        soma = Counter()
        for x in linhas:
            soma.update(x[campo])
        out[campo] = dict(sorted(soma.items()))
    out["brincar_por_vida"] = out["brincar"] / n
    out["d_min_celulas_mediana"] = sorted(x["d_min_celulas"] for x in linhas)[n // 2]
    out["d_min_celulas_menor"] = min(x["d_min_celulas"] for x in linhas)
    out["vidas_que_nunca_viram_a_bola"] = sum(1 for x in linhas if x["decisoes_bola_no_raio"] == 0)
    out["vidas_em_mundo_com_rolagem"] = sum(1 for x in linhas if x["rolagens_do_mundo"] > 0)
    return out


def resumir(linhas: list[dict]) -> dict:
    def grupos(chave) -> dict:
        nomes = sorted({chave(x) for x in linhas})
        return {nome: somar([x for x in linhas if chave(x) == nome]) for nome in nomes}
    return {"por_fonte": grupos(lambda x: x["fonte"]),
            "por_fonte_e_pet": grupos(lambda x: f"{x['fonte']}|{x['pet']}"),
            "por_fonte_e_braco": grupos(lambda x: f"{x['fonte']}|{x['braco']}"),
            "c3_vida_por_dono": somar_por(linhas, "dono"), "c3_vida_por_lugar": somar_por(linhas, "lugar"),
            "c3_vida_por_dono_e_lugar": {f"{d}|{lg}": somar([x for x in linhas if x["fonte"] == "c3_vida" and x["dono"] == d
                                                           and x["lugar"] == lg])
                                         for d, lg in sorted({(x["dono"], x["lugar"]) for x in linhas if x["fonte"] == "c3_vida"})},
            "raios": linhas[0]["raios"]}


def somar_por(linhas: list[dict], campo: str) -> dict:
    vidas = [x for x in linhas if x["fonte"] == "c3_vida"]
    return {nome: somar([x for x in vidas if x[campo] == nome]) for nome in sorted({x[campo] for x in vidas})}


def brincar_das_medidas(medidas: list[dict]) -> dict:
    """o `brincar` por vida em TODAS as vidas de um pet da C3, direto das medidas gravadas (sem replay): por braco, dono e lugar"""
    out = {}
    for chave in sorted({(m["braco"], m["dono"], m["lugar"]) for m in medidas}):
        vs = [m["acoes"].get("brincar", 0) for m in medidas if (m["braco"], m["dono"], m["lugar"]) == chave]
        out["|".join(chave)] = {"vidas": len(vs), "brincar": sum(vs), "brincar_por_vida": sum(vs) / len(vs)}
    return out


# ================================================================== a porta
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--c3", required=True, help="a pasta artifacts_v3_corpo/c3 da run da CORPO C3 (pares.json, pares.tar.gz, medidas.json.gz)")
    ap.add_argument("--processos", type=int, default=2)
    ap.add_argument("--bases-vidas", type=int, default=10, help="quantas bases (as primeiras) das vidas de um pet da C3 se refazem")
    ap.add_argument("--bracos-pares", default="CTRL,D,DTL,DTB")
    ap.add_argument("--limite", type=int, default=None, help="so para a fumaca: no maximo N tarefas de cada fonte (nao grava o resultado)")
    args = ap.parse_args()
    if not 1 <= args.processos <= MAX_PROCESSOS:
        raise SystemExit(f"--processos de 1 a {MAX_PROCESSOS} (V3-D8)")
    pasta_c3 = Path(args.c3)
    t0, inicio = time.perf_counter(), time.strftime("%Y-%m-%dT%H:%M:%S")

    tarefas: list[tuple] = [("a0", str(p)) for p in sorted(A0_VIDAS.glob("*.json.gz"))]
    n_a0 = len(tarefas)
    bracos = args.bracos_pares.split(",")
    pares = json.loads((pasta_c3 / "pares.json").read_text(encoding="utf-8"))
    with tarfile.open(pasta_c3 / "pares.tar.gz") as tar:
        gravados = {m.name: hashlib.sha256(gzip.GzipFile(fileobj=io.BytesIO(tar.extractfile(m).read())).read()).hexdigest()
                    for m in tar.getmembers() if m.isfile()}
    t_pares = [("c3_par", (p["braco"], p["base"], p["k"], p["semente"], gravados[f"pares/{p['braco']}/{p['base']}-{p['k']:04d}.jsonl.gz"]))
               for p in pares if p["braco"] in bracos]
    with gzip.open(pasta_c3 / "medidas.json.gz", "rt", encoding="utf-8") as f:
        medidas = json.load(f)
    cfg_c3 = json.loads((RAIZ / "experiments" / "configs" / "v3_corpo_c3" / "run.json").read_text(encoding="utf-8"))
    bases = sorted({m["base"] for m in medidas})[:args.bases_vidas]
    t_vidas = [("c3_vida", (m["dono"], m["lugar"], m["semente"], m["log_sha256"], cfg_c3["dias"], cfg_c3["orcamento_por_dia"]))
               for m in medidas if m["braco"] == BRACO_VIDAS and m["base"] in bases]
    if args.limite is not None:
        tarefas, t_pares, t_vidas = tarefas[:args.limite], t_pares[:args.limite], t_vidas[:args.limite]
    tarefas += t_pares + t_vidas

    linhas, custo = [], Counter()
    with ProcessPoolExecutor(max_workers=args.processos) as ex:
        for tipo, ls, dt in ex.map(_fazer, tarefas, chunksize=1):
            linhas += ls
            custo[tipo] += dt
    resumo = resumir(linhas)
    resumo["c3_brincar_das_medidas"] = brincar_das_medidas(medidas)
    if args.limite is not None:
        print(json.dumps({k: {c: v[c] for c in ("vidas_de_pet", "brincar", "brincar_bola_no_raio", "brincar_com_alvo", "chutes")}
                          for k, v in resumo["por_fonte"].items()}, indent=1), dict(custo))
        return
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "contagens.json").write_text(json.dumps(linhas, sort_keys=True, indent=0) + "\n", encoding="utf-8", newline="\n")
    (SAIDA / "resumo.json").write_text(json.dumps(resumo, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    meta = {"fase": "bola_diagnostico", "comando": "python experiments/diagnosticar_v3_bola.py " + " ".join(sys.argv[1:]),
            "inicio": inicio, "fim": time.strftime("%Y-%m-%dT%H:%M:%S"), "parede_s": time.perf_counter() - t0,
            "cpu_por_fonte_s": dict(custo), "processos": args.processos, "python": platform.python_version(),
            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip(),
            "git_limpo": subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=RAIZ, capture_output=True,
                                        text=True, check=True).stdout.strip() == "",
            "script_sha256": _sha(Path(__file__)),
            "fonte": {"a0_pares": n_a0, "c3_pares": len(t_pares), "c3_pares_bracos": bracos, "c3_vidas": len(t_vidas),
                      "c3_vidas_bases": bases, "c3_vidas_braco": BRACO_VIDAS,
                      "c3_pares_json_sha256": _sha(pasta_c3 / "pares.json"), "c3_pares_tar_sha256": _sha(pasta_c3 / "pares.tar.gz"),
                      "c3_medidas_gz_sha256": _sha(pasta_c3 / "medidas.json.gz"),
                      "a0_meta_sha256": _sha(A0_VIDAS.parent / "meta.json")},
            "artefatos_sha256": {n: _sha(SAIDA / n) for n in ("contagens.json", "resumo.json")}}
    (SAIDA / "meta.json").write_text(json.dumps(meta, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"BOLA_DIAGNOSTICO: {len(linhas)} vidas de pet em {meta['parede_s']:.0f} s; {SAIDA}")


if __name__ == "__main__":
    main()
