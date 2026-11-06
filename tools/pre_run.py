"""O gate antes de uma run de pesquisa (INFRA_AGENTES E3, `docs/TAREFA_V3_INFRA_AGENTES.md`, seção 3.3). Só biblioteca padrão.

    python tools/pre_run.py <orquestrador> --config <json> [--processos N]

Sai com código 0 (pode rodar) ou 2 (recusa, com todos os motivos no stderr). Não roda nada da run. Recusa quando:
1. a config não tem `plano` ou `unidades.bases` (falha alto: as configs da V2 congelada não têm, e elas não rodam mais);
2. o plano não está no git, tem mudança não commitada, ou o texto dele no disco não é o do `origin/main` (D-IA-6: o plano que vale é o
   que está na `main`); sem `origin/main`, pede `git fetch`;
3. alguma base cai fora de toda faixa de `FAIXAS_RESERVADAS` ou dentro de uma de `FAIXAS_QUEIMADAS` (lidas pela AST de
   `experiments/bancada/faixas.py`, sem importar a bancada; as sementes dos testes, 101…505, estão na reservada 101…1010);
4. há outra run em andamento: um processo Python com `experiments/run_v[23]_*.py` na linha de comando (fora este processo e o pai, para
   quando o próprio orquestrador chama o gate);
5. passam de 4 processos (V3-D8).

Quem chama: o hook H10 (`.claude/hooks/h10_pre_run.py`), antes do comando da run, e, daqui para a frente, os `run_v3_*` novos no começo
do `main()` (D-IA-2), por `conferir(...)`. Os `run_v2_*` da V2 congelada não mudam.

`DIGILAB_PRE_RUN_PROCESSOS`, se definida, é uma lista JSON de linhas de comando que substitui a lista do sistema (só para os testes, que
não podem depender do que a máquina está rodando).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FAIXAS = Path("experiments") / "bancada" / "faixas.py"
MAX_PROCESSOS = 4                                          # V3-D8 (docs/PLANO_V3.md, seção 7)
RUN = re.compile(r"experiments[\\/]+run_v[23]_[A-Za-z0-9_]+\.py")


class Recusa(Exception):
    pass


def git(raiz: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def tupla_de(texto: str, nome: str) -> tuple:
    for no in ast.parse(texto).body:
        alvos = no.targets if isinstance(no, ast.Assign) else [no.target] if isinstance(no, ast.AnnAssign) else []
        if any(isinstance(a, ast.Name) and a.id == nome for a in alvos) and no.value is not None:
            return tuple(ast.literal_eval(no.value))
    raise ValueError(f"não achei {nome} em {FAIXAS.as_posix()}")


def motivos_da_config(cfg: dict) -> tuple[list[str], str | None, list[int]]:
    motivos = []
    plano = cfg.get("plano")
    bases = (cfg.get("unidades") or {}).get("bases")
    if not isinstance(plano, str) or not plano:
        motivos.append("a config não tem `plano` (o caminho do plano de análise)")
        plano = None
    if not isinstance(bases, list) or not bases or not all(isinstance(b, int) and not isinstance(b, bool) for b in bases):
        motivos.append("a config não tem `unidades.bases` (uma lista de inteiros)")
        bases = []
    return motivos, plano, bases


def motivos_do_plano(raiz: Path, plano: str) -> list[str]:
    if git(raiz, "ls-files", "--error-unmatch", "--", plano)[0] != 0:
        return [f"o plano {plano} não está no git"]
    if git(raiz, "status", "--porcelain", "--", plano)[1].strip():
        return [f"o plano {plano} tem mudança não commitada"]
    if git(raiz, "rev-parse", "--verify", "--quiet", "origin/main")[0] != 0:
        return ["não achei o origin/main para conferir o plano; rode git fetch origin"]
    cod, na_main = git(raiz, "rev-parse", f"origin/main:{plano}")
    if cod != 0:
        return [f"o plano {plano} não está no origin/main (D-IA-6: o plano vale quando está na main); se já entrou, rode git fetch origin"]
    if git(raiz, "rev-parse", f"HEAD:{plano}")[1].strip() != na_main.strip():
        return [f"o plano {plano} daqui não é o do origin/main (D-IA-6); traga a main ou rode git fetch origin"]
    return []


def motivos_das_bases(raiz: Path, bases: list[int]) -> list[str]:
    texto = (raiz / FAIXAS).read_text(encoding="utf-8")
    reservadas, queimadas = tupla_de(texto, "FAIXAS_RESERVADAS"), tupla_de(texto, "FAIXAS_QUEIMADAS")
    motivos = []
    for b in bases:
        queimada = next((f for f in queimadas if f[0] <= b <= f[1]), None)
        if queimada is not None:
            motivos.append(f"a base {b} está na faixa queimada {queimada[0]}...{queimada[1]} ({queimada[2]}); faixa queimada não volta")
        elif not any(f[0] <= b <= f[1] for f in reservadas):
            motivos.append(f"a base {b} não está em nenhuma faixa de FAIXAS_RESERVADAS; peça a faixa ao coordenador antes da run")
    return motivos


def linhas_de_comando() -> list[tuple[int, str]]:
    """(pid, linha de comando) de cada processo Python da máquina."""
    falsa = os.environ.get("DIGILAB_PRE_RUN_PROCESSOS")
    if falsa is not None:
        return [(0, c) for c in json.loads(falsa)]
    if os.name == "nt":
        script = ("Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
                  "ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }")
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, timeout=60)
    else:
        r = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError("não consegui listar os processos: " + r.stderr.decode("utf-8", "replace").strip())
    saida = []
    for linha in r.stdout.decode("utf-8", "replace").splitlines():
        pid, _, comando = linha.strip().replace("\t", " ", 1).partition(" ")
        if pid.isdigit() and ("python" in comando.lower() or os.name == "nt"):
            saida.append((int(pid), comando))
    return saida


def motivos_de_outra_run() -> list[str]:
    meus = {os.getpid(), os.getppid()}
    outras = [c for pid, c in linhas_de_comando() if pid not in meus and RUN.search(c)]
    if outras:
        return ["há outra run em andamento (uma run de pesquisa por vez, V3-D8): " + " | ".join(o[:160] for o in outras)]
    return []


def conferir(orquestrador: str, config: str, processos: int = 1, raiz: Path = RAIZ) -> list[str]:
    """Os motivos da recusa; lista vazia se a run pode rodar."""
    motivos = []
    if not RUN.search(orquestrador.replace("\\", "/")):
        motivos.append(f"{orquestrador} não é um orquestrador experiments/run_v[23]_*.py")
    if processos > MAX_PROCESSOS:
        motivos.append(f"{processos} processos: no máximo {MAX_PROCESSOS} por run (V3-D8)")
    caminho = Path(config) if Path(config).is_absolute() else raiz / config
    if not caminho.is_file():
        return motivos + [f"a config {config} não existe"]
    m, plano, bases = motivos_da_config(json.loads(caminho.read_text(encoding="utf-8")))
    motivos += m
    if plano:
        motivos += motivos_do_plano(raiz, plano)
    motivos += motivos_das_bases(raiz, bases)
    motivos += motivos_de_outra_run()
    return motivos


def exigir(orquestrador: str, config: str, processos: int = 1, raiz: Path = RAIZ) -> None:
    """Para os orquestradores novos: levanta `Recusa` com os motivos, em vez de deixar a run começar."""
    motivos = conferir(orquestrador, config, processos, raiz)
    if motivos:
        raise Recusa("pre_run recusou a run:\n- " + "\n- ".join(motivos))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="o gate antes de uma run de pesquisa (INFRA_AGENTES E3)")
    ap.add_argument("orquestrador")
    ap.add_argument("--config", required=True)
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--raiz", default=str(RAIZ))
    a = ap.parse_args(argv)
    motivos = conferir(a.orquestrador, a.config, a.processos, Path(a.raiz).resolve())
    if motivos:
        sys.stderr.buffer.write(("pre_run recusou a run:\n- " + "\n- ".join(motivos) + "\n").encode("utf-8"))
        return 2
    print("pre_run: pode rodar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
