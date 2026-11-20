"""H10 (PreToolUse, Bash|PowerShell): nenhuma run de pesquisa começa sem passar pelo `tools/pre_run.py` (INFRA_AGENTES E3,
`docs/TAREFA_V3_INFRA_AGENTES.md`, seção 3.3).

Acha no comando um `python … experiments/run_v[23]_*.py` (o pedido dizia `run_v2_*`; o `run_v3_acoes_novas.py` já existe), tira o
`--config` e o `--processos` (as duas formas, `--x valor` e `--x=valor`) e chama o `pre_run.py` com eles. Se ele recusa, código 2 com os
motivos. Um `--help` passa. Sem `--config`, código 2: o orquestrador também exige, e o gate não tem o que conferir.

**As medições do combate** (`python … scripts/equilibrio_tr/*.py` e `npx tsx … scripts/equilibrio_tr/*.ts`, em `web/app`; desde a LUTA_POC
LP5-0 também `node … scripts/equilibrio_poc/*.ts`, a bancada da luta em tempo real) passam pelo
`pre_run.py --medicao`: só a regra de uma carga por vez, que a V3-D8 aplica a elas (INFRA_AGENTES E7).

Como o H3, o hook lê o texto do comando: uma run lançada por um script que chama o orquestrador por dentro não passa por aqui (os
`run_v3_*` novos chamam o `pre_run.exigir` no começo, D-IA-2).
"""
from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, raiz_do_projeto  # noqa: E402

SEPARADORES = re.compile(r"&&|\|\||;|\||\n")
RUN = re.compile(r"(^|[\\/])experiments[\\/]+run_v[23]_[A-Za-z0-9_]+\.py$")
MEDICAO = re.compile(r"(^|[\\/])scripts[\\/]+equilibrio_(?:tr|poc)[\\/]+[A-Za-z0-9_]+\.(py|ts)$")


def tokens_de(pedaco: str) -> list[str]:
    try:
        return shlex.split(pedaco, posix=True)
    except ValueError:
        return pedaco.split()


def opcao(tokens: list[str], nome: str) -> str | None:
    for i, t in enumerate(tokens):
        if t == nome and i + 1 < len(tokens):
            return tokens[i + 1]
        if t.startswith(nome + "="):
            return t.split("=", 1)[1]
    return None


def runs_do_comando(comando: str) -> list[list[str]]:
    """Os pedaços do comando que rodam um orquestrador pelo Python (os tokens a partir do nome do script)."""
    saida = []
    for pedaco in SEPARADORES.split(comando.replace("\\", "/")):
        tokens = tokens_de(pedaco.strip())
        if not any(Path(t).stem.lower().startswith(("python", "py")) for t in tokens[:3]):
            continue
        for i, t in enumerate(tokens):
            if RUN.search(t):
                saida.append(tokens[i:])
                break
    return saida


def medicoes_do_comando(comando: str) -> list[str]:
    """Os scripts de medição do combate que o comando roda, pelo Python (o `.py`) ou pelo Node (`npx tsx`, `node`, o `.ts`)."""
    saida = []
    for pedaco in SEPARADORES.split(comando.replace("\\", "/")):
        tokens = tokens_de(pedaco.strip())
        nomes = [Path(t).stem.lower() for t in tokens[:3]]
        roda = any(n.startswith("python") or n in ("py", "npx", "node", "tsx") for n in nomes)
        alvo = next((t for t in tokens if MEDICAO.search(t)), None)
        if roda and alvo and "-h" not in tokens and "--help" not in tokens:
            saida.append(alvo)
    return saida


def main() -> None:
    evento = ler_evento()
    comando = (evento.get("tool_input") or {}).get("command") or ""
    raiz = raiz_do_projeto(evento)
    for script in medicoes_do_comando(comando):
        r = subprocess.run([sys.executable, str(raiz / "tools" / "pre_run.py"), script, "--medicao", "--raiz", str(raiz)],
                           capture_output=True, timeout=120)
        if r.returncode != 0:
            bloquear("H10: " + (r.stderr.decode("utf-8", "replace").strip() or f"pre_run saiu com {r.returncode}"))
    for tokens in runs_do_comando(comando):
        if "-h" in tokens or "--help" in tokens:
            continue
        config = opcao(tokens, "--config")
        if config is None:
            bloquear(f"H10: {tokens[0]} sem --config; o pre_run não tem o plano nem as bases para conferir.")
        processos = opcao(tokens, "--processos") or "1"
        r = subprocess.run([sys.executable, str(raiz / "tools" / "pre_run.py"), tokens[0], "--config", config, "--processos", processos,
                            "--raiz", str(raiz)], capture_output=True, timeout=120)
        if r.returncode != 0:
            bloquear("H10: " + (r.stderr.decode("utf-8", "replace").strip() or f"pre_run saiu com {r.returncode}"))


if __name__ == "__main__":
    main()
