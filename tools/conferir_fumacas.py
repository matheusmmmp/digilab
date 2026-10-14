"""G-FUMACAS da rodada de saúde, etapa 3 (docs/TAREFA_V2_SAUDE.md): toda fumaça de `experiments/configs/` roda antes e depois da
bancada em módulos, e os arquivos de saída têm de sair iguais (sha256).

  python tools/conferir_fumacas.py rodar --raiz <worktree> --saida <pasta>     # roda todas as fumaças daquela árvore
  python tools/conferir_fumacas.py comparar <pasta antes> <pasta depois>         # compara arquivo a arquivo

Cada fumaça roda pelo orquestrador dela, com `--saida` dentro de <pasta>/<nome>. A do cérebro B grava onde a config manda: ela roda de uma
cópia da config com a saída trocada por um caminho absoluto. Na comparação, os `meta*.json` saem à parte: trazem tempo de parede e o
sha256 dos fontes, que mudam por construção. Todo o resto (medidas, tabelas, resultados, as vidas) tem de ser igual.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# fora: as fumaças da arena v1 (run_arena.py) não importam a bancada e gravam onde a config manda
FORA = {"experiments/configs/fumaca.json", "experiments/configs/ablacao_fumaca.json", "experiments/configs/memoria_fumaca.json"}
# config -> (orquestrador, argumentos a mais)
FUMACAS = {
    "experiments/configs/bancada/fumaca.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_frutas.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_k4_canais.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_montagem.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_n5.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_n6.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_n7.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/bancada/fumaca_p2d_p3i.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_corpo/fumaca.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_corpo/fumaca_passo0.json": ("experiments/bancada_v2.py", ["--passo0"]),
    "experiments/configs/v2_corpo/fumaca_calibracao.json": ("experiments/run_v2_calibracao_corpo.py", []),
    "experiments/configs/v2_mundo/fumaca.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_mundo/fumaca_calibracao.json": ("experiments/run_v2_calibracao_mundo.py", []),
    "experiments/configs/v2_mundo/fumaca_validacao.json": ("experiments/run_v2_validacao_mundo.py", []),
    "experiments/configs/v2_mundo_alvo/fumaca_piloto.json": ("experiments/run_v2_mundo_alvo.py", []),
    "experiments/configs/v2_mundo_alvo/fumaca_validacao.json": ("experiments/run_v2_mundo_alvo.py", []),
    "experiments/configs/v2_dois_pets/fumaca.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_dois_pets/fumaca_calibracao.json": ("experiments/run_v2_calibracao_dois_pets.py", []),
    "experiments/configs/v2_rede_de_si/fumaca.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_rede_de_si/fumaca_autoria.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_rede_de_si/fumaca_calibracao.json": ("experiments/run_v2_calibracao_rede_de_si.py", []),   # o #303
    "experiments/configs/v2_pet_que_pensa/fumaca.json": ("experiments/bancada_v2.py", []),
    "experiments/configs/v2_pet_que_pensa/fumaca_calibracao.json": ("experiments/run_v2_calibracao_pet_que_pensa.py", []),
    "experiments/configs/v2_experimento_maior/fumaca.json": ("experiments/run_v2_experimento_maior.py", []),
    "experiments/configs/v2_calibracao_conjunta/fumaca.json": ("experiments/run_v2_calibracao_conjunta.py", []),
    "experiments/configs/v2_calibracao_cerebro_c/fumaca.json": ("experiments/run_v2_calibracao_cerebro_c.py", []),
    "experiments/configs/v2_comparacao_cerebros/fumaca_ac.json": ("experiments/run_v2_comparacao_cerebros.py", []),
    "experiments/configs/v2_comparacao_cerebros/fumaca_B.json": ("experiments/run_v2_calibracao_cerebro_b.py", ["SAIDA_NA_CONFIG"]),
}


def nome_de(config: str) -> str:
    return config.removeprefix("experiments/configs/").removesuffix(".json").replace("/", "__")


def rodar(raiz: Path, saida: Path, so: list[str]) -> dict:
    achadas = sorted(p.relative_to(raiz).as_posix() for p in (raiz / "experiments/configs").rglob("*fumaca*.json"))
    faltam = sorted(set(achadas) - set(FUMACAS) - FORA)
    if faltam:
        raise SystemExit(f"fumaças sem orquestrador na tabela: {faltam}")
    saida.mkdir(parents=True, exist_ok=False)
    relato = {}
    for config, (script, extra) in FUMACAS.items():
        if so and nome_de(config) not in so:
            continue
        if not (raiz / config).exists():          # uma fumaça de um PR que ainda não está nesta árvore
            relato[config] = {"rc": None, "segundos": 0.0, "ausente": True}
            print(f"{nome_de(config)}: ausente nesta árvore", flush=True)
            continue
        destino = saida / nome_de(config)
        if extra == ["SAIDA_NA_CONFIG"]:
            cfg = json.loads((raiz / config).read_text(encoding="utf-8"))
            cfg["saida"] = str(destino.resolve())
            copia = saida / f"{nome_de(config)}.config.json"
            copia.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            cmd = [sys.executable, script, "--config", str(copia.resolve())]
        else:
            cmd = [sys.executable, script, "--config", config, "--saida", str(destino.resolve()), *extra]
        t0 = time.time()
        r = subprocess.run(cmd, cwd=raiz, capture_output=True)
        relato[config] = {"rc": r.returncode, "segundos": round(time.time() - t0, 1)}
        (saida / f"{nome_de(config)}.log").write_bytes(r.stdout + b"\n--- stderr ---\n" + r.stderr)
        print(f"{nome_de(config)}: rc {r.returncode}, {relato[config]['segundos']} s", flush=True)
    (saida / "relato.json").write_text(json.dumps(relato, indent=2), encoding="utf-8")
    return relato


def hashes(pasta: Path) -> dict[str, str]:
    return {p.relative_to(pasta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(pasta.rglob("*")) if p.is_file() and not p.name.endswith((".log", ".config.json")) and p.name != "relato.json"}


def comparar(antes: Path, depois: Path) -> int:
    a, d = hashes(antes), hashes(depois)
    ra = {c: r for c, r in json.loads((antes / "relato.json").read_text(encoding="utf-8")).items() if c not in FORA}
    rd = {c: r for c, r in json.loads((depois / "relato.json").read_text(encoding="utf-8")).items() if c not in FORA}
    falhas = [f"rc diferente: {c} ({ra[c]['rc']} x {rd.get(c, {}).get('rc')})" for c in ra if ra[c]["rc"] != rd.get(c, {}).get("rc")]
    falhas += [f"rc não zero: {c}" for c in rd if rd[c]["rc"] not in (0, None)]
    so_a, so_d = sorted(set(a) - set(d)), sorted(set(d) - set(a))
    falhas += [f"só antes: {x}" for x in so_a] + [f"só depois: {x}" for x in so_d]
    metas = [x for x in a if x in d and Path(x).name.startswith("meta")]
    iguais = [x for x in a if x in d and a[x] == d[x] and x not in metas]
    difs = [x for x in a if x in d and a[x] != d[x] and x not in metas]
    falhas += [f"diferente: {x}" for x in difs]
    medidas = [x for x in iguais if Path(x).name == "medidas.json"]
    print(f"{len(iguais)} arquivos iguais (sha256), {len(medidas)} deles medidas.json; {len(metas)} meta*.json à parte; "
          f"{len(ra)} fumaças")
    for f in falhas:
        print("  FALHA", f)
    print("G-FUMACAS", "passa" if not falhas else f"FALHA ({len(falhas)})")
    return 1 if falhas else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("rodar")
    r.add_argument("--raiz", default=".")
    r.add_argument("--saida", required=True)
    r.add_argument("--so", nargs="*", default=[])
    c = sub.add_parser("comparar")
    c.add_argument("antes")
    c.add_argument("depois")
    args = ap.parse_args()
    if args.comando == "rodar":
        rodar(Path(args.raiz).resolve(), Path(args.saida).resolve(), args.so)
    else:
        raise SystemExit(comparar(Path(args.antes), Path(args.depois)))
