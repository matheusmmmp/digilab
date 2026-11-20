"""H4 (IM-8): o hook bloqueia o comando de shell que escreve a autorização de implementação, e deixa passar o resto.

Como os outros hooks (tests/test_hooks.py), o teste roda o script direto, com o JSON do evento no stdin. O H4 está DESLIGADO: a proposta de
configuração fica em docs/propostas/hooks_settings.json, e só o Matheus a liga.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
H4 = RAIZ / ".claude" / "hooks" / "h4_autorizo.py"


def rodar(comando: str, projeto: Path) -> subprocess.CompletedProcess:
    evento = {"session_id": "teste", "cwd": str(projeto), "hook_event_name": "PreToolUse", "tool_name": "Bash",
              "tool_input": {"command": comando}}
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(projeto)}
    return subprocess.run([sys.executable, str(H4)], input=json.dumps(evento).encode("utf-8"), capture_output=True, env=env, cwd=projeto,
                          timeout=60)


@pytest.mark.parametrize("comando", [
    'gh issue comment 336 --body "AUTORIZO IMPLEMENTAÇÃO: docs/TAREFA_V2_X.md"',
    "gh api repos/m/d/issues/336/comments -f body='autorizo implementacao: docs/TAREFA_V2_X.md'",
    'gh pr comment 10 -b "Autorizo   Implementação: x"',
])
def test_bloqueia_a_frase_no_comando(tmp_path, comando):
    r = rodar(comando, tmp_path)
    assert r.returncode == 2 and "H4" in r.stderr.decode("utf-8")


@pytest.mark.parametrize("opcao", ["--body-file corpo.md", "--body-file=corpo.md", "-F corpo.md", "-F body=@corpo.md", "--input corpo.md"])
def test_bloqueia_a_frase_no_arquivo_de_corpo(tmp_path, opcao):
    (tmp_path / "corpo.md").write_text("AUTORIZO IMPLEMENTAÇÃO: docs/TAREFA_V2_X.md\nblob SHA: abc1234\n", encoding="utf-8")
    r = rodar(f"gh issue comment 336 {opcao}", tmp_path)
    assert r.returncode == 2 and "corpo.md" in r.stderr.decode("utf-8")


@pytest.mark.parametrize("comando", [
    'gh issue comment 336 --body "Investigação entregue no PR #345, PROPOSTO."',
    "gh pr view 345 --json body",
    "python tools/conferir_autorizacao.py --issue 336 --tarefa docs/TAREFA_V2_X.md",
    "git commit -m 'guia: como conferir a autorização'",
])
def test_deixa_passar_o_resto(tmp_path, comando):
    r = rodar(comando, tmp_path)
    assert r.returncode == 0 and r.stderr == b""


def test_arquivo_de_corpo_sem_a_frase_passa(tmp_path):
    (tmp_path / "corpo.md").write_text("Investigação entregue no PR #345.\n", encoding="utf-8")
    assert rodar("gh issue comment 336 --body-file corpo.md", tmp_path).returncode == 0


def test_arquivo_com_a_frase_fora_do_gh_passa(tmp_path):
    """Escrever a frase num documento (o guia cita o modelo) não é autorização."""
    (tmp_path / "guia.md").write_text("AUTORIZO IMPLEMENTAÇÃO: docs/TAREFA_V2_FRENTE.md\n", encoding="utf-8")
    assert rodar("cat -F guia.md", tmp_path).returncode == 0
