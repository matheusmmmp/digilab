"""O que os hooks do Digilab dividem (rodada de saúde, etapa 4; docs/TAREFA_V2_SAUDE.md). Só a biblioteca padrão.

Cada hook lê do stdin o JSON do evento (o formato da documentação do Claude Code) e responde pelo código de saída e pelo stdout/stderr:
- código 0 sem saída: deixa seguir;
- código 2 com o motivo no stderr: bloqueia (no PreToolUse, a ferramenta não roda; no Stop, o Claude continua o turno com o motivo);
- código 0 com um JSON no stdout: a decisão estruturada (o "ask" do H3).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def ler_evento() -> dict:
    texto = sys.stdin.read()
    if not texto.strip():
        raise SystemExit("hook sem entrada no stdin")
    return json.loads(texto)


def raiz_do_projeto(evento: dict) -> Path:
    """O diretório do projeto: o CLAUDE_PROJECT_DIR do Claude Code, senão o `cwd` do evento, senão o deste arquivo."""
    for candidato in (os.environ.get("CLAUDE_PROJECT_DIR"), evento.get("cwd")):
        if candidato:
            return Path(candidato).resolve()
    return Path(__file__).resolve().parents[2]


def git(raiz: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8", "replace")


def sha_do_engine(raiz: Path) -> tuple[str, str]:
    """(o sha256 do digilab/engine.py no disco, o ENGINE_SHA256_V0 do digilab/protocol.py), lido como texto, sem importar o pacote."""
    atual = hashlib.sha256((raiz / "digilab" / "engine.py").read_bytes()).hexdigest()
    m = re.search(r'^ENGINE_SHA256_V0\s*=\s*"([0-9a-f]{64})"', (raiz / "digilab" / "protocol.py").read_text(encoding="utf-8"), re.M)
    if m is None:
        raise RuntimeError("não achei ENGINE_SHA256_V0 em digilab/protocol.py")
    return atual, m.group(1)


def bloquear(motivo: str) -> None:
    """Código 2 com o motivo no stderr, em UTF-8 (o console do Windows usaria outra codificação)."""
    sys.stderr.flush()
    sys.stderr.buffer.write((motivo.rstrip() + "\n").encode("utf-8"))
    sys.stderr.buffer.flush()
    raise SystemExit(2)


def perguntar(motivo: str) -> None:
    """A decisão "ask" do PreToolUse, em JSON no stdout (só ASCII: os acentos vão escapados): o Claude Code pergunta ao usuário."""
    sys.stdout.buffer.write((json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                                                "permissionDecisionReason": motivo}}) + "\n").encode("ascii"))
    sys.stdout.buffer.flush()
    raise SystemExit(0)
