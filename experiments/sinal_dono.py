"""Etapa A do plano do canal do dono (docs/PLANO_ANALISE_CANAL_DONO.md): o sinal do dono chega ao que o pet aprende?

    python experiments/sinal_dono.py [--vidas <pasta>] [--processos N]

Nenhuma vida nova e nenhuma mecanica nova: reproduz as 640 vidas arquivadas da rodada especie_fixa do E1, confere
cada replay contra o pets.json do E1, mede os portadores do sinal (carater em T_ADOL e T_ADUL, disciplina, saude,
vinculo e treino) e decompoe cada um em genoma x dono x ambiente (metrics.componentes_cruzados), com o bootstrap
pigeonhole do E1. Gate A: em algum eixo do carater em T_ADOL, o limite inferior do IC 98,75% (Bonferroni pelos 4
eixos) de sigma2_D acima de 0. Saida: artifacts_linhagem/sinal_dono/resultado.json.
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

from digilab.combate_v2.v21.catalogo import SOMBRIA_DA_LINHA, forma_adulta, linha_do_adolescente  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.educacao import politica_no_tick_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import carater  # noqa: E402
from digilab.metrics import bootstrap_cruzado, componentes_cruzados, ic_percentil, kappa_fleiss  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, hash_parametros_educacao, sha256_engine  # noqa: E402
from run_educacao import SONDAS, T_ADOL, T_ADUL, _fabricas  # noqa: E402
from run_natureza_criacao import chave, genoma  # noqa: E402

E1 = RAIZ / "artifacts_linhagem" / "natureza_criacao" / "especie_fixa"
VIDAS_E1 = Path("D:/Trab/digilab/arquivo/artifacts_linhagem_E1_vidas/natureza_criacao/especie_fixa/vidas")
SAIDA = RAIZ / "artifacts_linhagem" / "sinal_dono"
CFG_E1 = RAIZ / "experiments" / "configs" / "linhagem" / "natureza_criacao.json"

# fixados no plano (secao 3)
REAMOSTRAS, SEMENTE = 10000, 20260930
NIVEL_GATE = 1 - 0.05 / 4          # Bonferroni pelos 4 eixos
COMPONENTES = ("G", "D", "R", "GD", "GR", "DR", "e")
CAMPOS_CONFERIDOS = ("especie", "morta", "morte", "sparring", "adulto_liberado", "disciplina_final", "saude_final",
                     "vinculo_final", "sombria", "treino_total", "forma")


def medir(args) -> tuple:
    """replay de uma vida arquivada: (chave, dados como no pets.json do E1, portadores)"""
    b, g, r, esp_regra, pasta = args
    esp, temp_ovo, tmp = genoma(g, esp_regra)
    nome = chave(b, g, r)
    log = LogDeEventos.de_jsonl((Path(pasta) / f"{nome}.jsonl").read_text(encoding="utf-8"))
    fp, fm_base, fm, pet = _fabricas(b, r, esp, tmp, temp_ovo)
    m = reproduzir_educacao(log, fp, semente=r, fabrica_motor=fm)
    lutas = m.historico_lutas
    dados = {"dono": b, "genoma": g, "ambiente": r, "especie": esp, "morta": m.morte is not None, "morte": m.morte,
             "sparring": {"lutas": len(lutas), "vitorias": sum(x["resultado"] == "vitoria" for x in lutas),
                          "lesoes": sum(x["lesao"] for x in lutas)},
             "adulto_liberado": m.adulto_liberado, "disciplina_final": m.disciplina,
             "saude_final": m.estado()["saude"], "vinculo_final": m.vinculo.valor, "sombria": bool(m.sombria),
             "treino_total": sum(m.treino.pontos.values())}
    if m.morte is not None and m.morte["tick"] <= T_ADOL:
        raise RuntimeError(f"{nome}: morte no tick {m.morte['tick']}, antes de T_ADOL ({T_ADOL})")
    pol_adol = politica_no_tick_educacao(log, fp, r, T_ADOL, fm_base)
    car_adol, bruto_adol = carater(pol_adol, fp(CONFIG_PADRAO), *SONDAS)
    linha = linha_do_adolescente(car_adol)
    port = {"carater_adol": car_adol, "bruto_adol": bruto_adol, "linha": linha,
            "treino": dict(m.treino.pontos), "carater_adul": None}
    vivo_em_adul = m.morte is None or m.morte["tick"] > T_ADUL
    if vivo_em_adul:
        pol_adul = politica_no_tick_educacao(log, fp, r, T_ADUL, fm_base)
        car_adul, _ = carater(pol_adul, fp(CONFIG_PADRAO), *SONDAS)
        port["carater_adul"] = car_adul
    if m.morte is None:
        _, linha_pet, ramo = pet._adolescente(m)
        if linha_pet != linha:
            raise RuntimeError(f"{nome}: linha do replay {linha_pet} != a do carater em T_ADOL {linha}")
        car_adul = port["carater_adul"]
        if m.adulto_liberado:
            adulta = SOMBRIA_DA_LINHA[linha] if m.sombria else forma_adulta(linha, car_adul, len(lutas))
            dados["forma"] = {"estagio": "adulto", "ramo": ramo, "linha": linha, "adulta": adulta}
        else:
            dados["forma"] = {"estagio": "adolescente", "ramo": ramo, "linha": linha, "adulta": None}
    return nome, dados, port


def conferir(nome: str, dados: dict, ref: dict) -> None:
    for k in CAMPOS_CONFERIDOS:
        if dados.get(k) != ref.get(k):
            raise RuntimeError(f"{nome}: replay difere do pets.json do E1 em {k}: {dados.get(k)!r} != {ref.get(k)!r}")


def estatistica(nomes: list[str], donos: list[str]):
    """y[g][d][r] = tupla de portadores -> componentes, fracoes e medias por dono de cada um, e o contraste
    atencioso - aleatorio (secao 3 do plano)"""
    ja, jl = donos.index("atencioso"), donos.index("aleatorio")

    def f(y) -> dict:
        out = {}
        for i, n in enumerate(nomes):
            vals = [yg[ja][k][i] - yg[jl][k][i] for yg in y for k in range(len(yg[0]))]
            out[f"{n}|atencioso-aleatorio"] = sum(vals) / len(vals)
            c = componentes_cruzados([[[cel[i] for cel in yd] for yd in yg] for yg in y])
            for k in COMPONENTES:
                out[f"{n}|var_{k}"] = c["componentes"][k]
                out[f"{n}|frac_{k}"] = c["fracao"][k]
            for j, d in enumerate(c["media_por_dono"]):
                out[f"{n}|media_dono_{j}"] = d
        return out
    return f


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vidas", default=str(VIDAS_E1))
    ap.add_argument("--processos", type=int, default=16)
    a = ap.parse_args(argv)
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    cfg = json.loads(CFG_E1.read_text(encoding="utf-8"))
    rc = cfg["rodadas"]["especie_fixa"]
    gs, rs, ds = list(rc["genomas"]), list(rc["ambientes"]), sorted(cfg["donos"])
    pets_e1 = json.loads((E1 / "pets.json").read_text(encoding="utf-8"))
    meta_e1 = json.loads((E1 / "meta.json").read_text(encoding="utf-8"))
    if hash_parametros_educacao() != meta_e1["hash_parametros_educacao"]:
        raise RuntimeError("hash_parametros_educacao difere do E1")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(a.processos) as pool:
        medidos = list(pool.map(medir, [(b, g, r, rc["especie"], a.vidas) for g in gs for r in rs for b in ds]))
    t_replay = time.perf_counter() - t0
    port = {}
    for nome, dados, p in medidos:
        conferir(nome, dados, pets_e1[nome])
        port[nome] = p
    print(f"  {len(medidos)} replays conferidos em {t_replay:.0f} s", flush=True)

    eixos = sorted(port[chave(ds[0], gs[0], rs[0])]["carater_adol"])
    stats_treino = sorted({k for p in port.values() for k in p["treino"]})
    nomes, valor = [], {}
    for e in eixos:
        nomes.append(f"carater_adol:{e}")
    for e in eixos:
        nomes.append(f"bruto_adol:{e}")
    nomes += ["disciplina_final", "saude_final", "vinculo_final"] + [f"treino_fracao:{s}" for s in stats_treino]

    def valores(nome: str) -> tuple:
        p, d = port[nome], pets_e1[nome]
        tot = sum(p["treino"].values())
        return (tuple(p["carater_adol"][e] for e in eixos) + tuple(p["bruto_adol"][e] for e in eixos)
                + (float(d["disciplina_final"]), float(d["saude_final"]), float(d["vinculo_final"]))
                + tuple((p["treino"].get(s, 0.0) / tot) if tot > 0 else 0.0 for s in stats_treino))
    y = [[[valores(chave(d, g, r)) for r in rs] for d in ds] for g in gs]
    f = estatistica(nomes, ds)
    t1 = time.perf_counter()
    pontual = f(y)
    boots = bootstrap_cruzado(y, f, REAMOSTRAS, SEMENTE, reamostrar="GR")
    ic95 = {k: ic_percentil([b[k] for b in boots]) for k in pontual}
    ic_gate = {k: ic_percentil([b[k] for b in boots], NIVEL_GATE) for k in pontual if k.endswith("|var_D")}
    t_boot = time.perf_counter() - t1

    portadores = {}
    for n in nomes:
        portadores[n] = {
            "grupo": "aprendido" if n.startswith(("carater", "bruto")) else "imposto",
            "componentes": {k: {"estimativa": pontual[f"{n}|var_{k}"], "ic95": ic95[f"{n}|var_{k}"]} for k in COMPONENTES},
            "fracao": {k: {"estimativa": pontual[f"{n}|frac_{k}"], "ic95": ic95[f"{n}|frac_{k}"]} for k in COMPONENTES},
            "media_por_dono": {d: {"estimativa": pontual[f"{n}|media_dono_{j}"], "ic95": ic95[f"{n}|media_dono_{j}"]}
                               for j, d in enumerate(ds)},
            "atencioso-aleatorio": {"estimativa": pontual[f"{n}|atencioso-aleatorio"], "ic95": ic95[f"{n}|atencioso-aleatorio"]}}
    gate_eixos = {e: {"var_D": pontual[f"carater_adol:{e}|var_D"], f"ic{NIVEL_GATE:.4f}": ic_gate[f"carater_adol:{e}|var_D"],
                      "passa": ic_gate[f"carater_adol:{e}|var_D"][0] > 0} for e in eixos}
    gate = {"criterio": f"em algum eixo do carater em T_ADOL, limite inferior do IC {NIVEL_GATE:.4f} (Bonferroni, 4 eixos) "
                        "pigeonhole de sigma2_D > 0",
            "eixos": gate_eixos, "resultado": "SINAL PRESENTE" if any(v["passa"] for v in gate_eixos.values()) else "SINAL AUSENTE"}

    # descritivos: linha (o gargalo), concordancia da linha entre ambientes, carater em T_ADUL nos vivos
    linha_segue = sum(port[n]["linha"] == linha_do_adolescente(port[n]["carater_adol"]) for n in port) / len(port)
    linhas = {d: {} for d in ds}
    for n, p in port.items():
        d = pets_e1[n]["dono"]
        linhas[d][p["linha"]] = linhas[d].get(p["linha"], 0) + 1
    kappa_linha = {d: kappa_fleiss([[port[chave(d, g, r)]["linha"] for r in rs] for g in gs]) for d in ds}
    adul = {}
    for d in ds:
        xs = [port[chave(d, g, r)]["carater_adul"] for g in gs for r in rs if port[chave(d, g, r)]["carater_adul"]]
        adul[d] = {"n": len(xs), "media": {e: sum(x[e] for x in xs) / len(xs) for e in eixos}}

    out = {"plano": "docs/PLANO_ANALISE_CANAL_DONO.md", "etapa": "A",
           "bootstrap": {"reamostragens": REAMOSTRAS, "semente": SEMENTE, "tipo": "pigeonhole GR", "nivel_gate": NIVEL_GATE},
           "donos": ds, "eixos": eixos, "n_pets": len(port),
           "conferencias": {"replays_iguais_ao_pets_json_do_e1": len(medidos), "mortes_antes_de_T_ADOL": 0,
                            "hash_parametros_educacao_igual": True, "linha_segue_o_carater_em_T_ADOL": linha_segue},
           "gate": gate, "portadores": portadores,
           "linha": {"contagem_por_dono": linhas, "kappa_fleiss_entre_ambientes": kappa_linha},
           "carater_adul_vivos": adul,
           "meta": {"T_ADOL": T_ADOL, "T_ADUL": T_ADUL, "vidas": a.vidas, "tempos": {"replay_s": t_replay, "bootstrap_s": t_boot},
                    "hash_parametros_educacao": hash_parametros_educacao(),
                    "fontes_sha256": hashlib.sha256(b"".join((RAIZ / p).read_bytes().replace(b"\r\n", b"\n") for p in (
                        "experiments/sinal_dono.py", "experiments/run_educacao.py", "experiments/run_natureza_criacao.py",
                        "digilab/metrics.py", "digilab/educacao.py", "digilab/evolucao.py", "digilab/config.py"))).hexdigest(),
                    "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()}}}
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "portadores_por_pet.json").write_text(json.dumps(port, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                                   encoding="utf-8", newline="\n")
    (SAIDA / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                          encoding="utf-8", newline="\n")
    for e, v in gate_eixos.items():
        fr = portadores[f"carater_adol:{e}"]["fracao"]
        print(f"  {e}: sigma2_D {v['var_D']:+.6f} IC98,75 {[round(x, 6) for x in v[f'ic{NIVEL_GATE:.4f}']]}  "
              f"frac G {fr['G']['estimativa']:.3f} D {fr['D']['estimativa']:.3f} R {fr['R']['estimativa']:.3f} "
              f"DR {fr['DR']['estimativa']:.3f} e {fr['e']['estimativa']:.3f}")
    print(f"GATE A: {gate['resultado']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
