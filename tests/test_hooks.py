"""G-HOOKS (rodada de saúde, etapa 4; docs/TAREFA_V2_SAUDE.md): cada hook de .claude/hooks/ recebe no stdin o JSON do evento, no formato
da documentação do Claude Code, e o teste confere o código de saída e o texto.

Os hooks estão DESLIGADOS (a configuração proposta fica em docs/propostas/hooks_settings.json; SA-5). Estes testes rodam os scripts
direto, como o Claude Code rodaria.
"""
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
HOOKS = RAIZ / ".claude" / "hooks"


def rodar(script: str, evento: dict, projeto: Path) -> subprocess.CompletedProcess:
    env = {**__import__("os").environ, "CLAUDE_PROJECT_DIR": str(projeto)}
    return subprocess.run([sys.executable, str(HOOKS / script)], input=json.dumps(evento).encode("utf-8"), capture_output=True,
                          env=env, cwd=projeto, timeout=600)


def git(projeto: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(projeto), *args], check=True, capture_output=True)


@pytest.fixture
def projeto(tmp_path):
    """Um repositório pequeno: o engine.py e o protocol.py de verdade, um módulo e o teste dele, no branch main."""
    p = tmp_path / "projeto"
    (p / "digilab").mkdir(parents=True)
    (p / "tests").mkdir()
    for nome in ("engine.py", "protocol.py"):
        shutil.copyfile(RAIZ / "digilab" / nome, p / "digilab" / nome)
    (p / "digilab" / "conta.py").write_text("def dobro(x):\n    return 2 * x\n", encoding="utf-8")
    (p / "tests" / "test_conta.py").write_text(
        "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))\nfrom digilab.conta import dobro\n\n\n"
        "def test_dobro():\n    assert dobro(2) == 4\n", encoding="utf-8")
    (p / "digilab" / "__init__.py").write_text("", encoding="utf-8")
    git(p, "init", "-q", "-b", "main")
    git(p, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    git(p, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "inicio")
    return p


def pre_tool(tool: str, entrada: dict, projeto: Path) -> dict:
    return {"session_id": "teste", "cwd": str(projeto), "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": entrada}


def stop(projeto: Path, ativo: bool = False, sessao: str | None = None) -> dict:
    return {"session_id": sessao or f"teste-{uuid.uuid4().hex}", "cwd": str(projeto), "hook_event_name": "Stop",
            "stop_hook_active": ativo}


# ------------------------------------------------------------------ H1 e H1b: o engine.py


@pytest.mark.parametrize("caminho", ["digilab/engine.py", "ABSOLUTO", "digilab/../digilab/engine.py"])
def test_h1_nega_o_engine(projeto, caminho):
    alvo = str(projeto / "digilab" / "engine.py") if caminho == "ABSOLUTO" else caminho
    for tool in ("Edit", "Write"):
        r = rodar("h1_engine.py", pre_tool(tool, {"file_path": alvo}, projeto), projeto)
        assert r.returncode == 2 and b"engine.py" in r.stderr


@pytest.mark.parametrize("caminho", ["digilab/config.py", "digilab/engine_novo.py", "tests/test_engine.py"])
def test_h1_deixa_os_outros(projeto, caminho):
    r = rodar("h1_engine.py", pre_tool("Edit", {"file_path": caminho}, projeto), projeto)
    assert r.returncode == 0 and r.stdout == b"" and r.stderr == b""


def test_h1_fora_do_projeto_e_sem_caminho(projeto, tmp_path):
    fora = tmp_path / "outro" / "digilab" / "engine.py"
    assert rodar("h1_engine.py", pre_tool("Write", {"file_path": str(fora)}, projeto), projeto).returncode == 0
    assert rodar("h1_engine.py", pre_tool("Write", {}, projeto), projeto).returncode == 0


def test_h1b_sha_do_engine(projeto):
    assert rodar("h1b_engine_sha.py", stop(projeto), projeto).returncode == 0
    alvo = projeto / "digilab" / "engine.py"
    alvo.write_bytes(alvo.read_bytes() + b"\n# mudado por comando de shell\n")
    r = rodar("h1b_engine_sha.py", stop(projeto), projeto)
    assert r.returncode == 2 and b"engine.py mudou" in r.stderr
    assert rodar("h1b_engine_sha.py", stop(projeto, ativo=True), projeto).returncode == 0   # não bloqueia duas vezes seguidas


def test_h1b_no_repositorio_de_verdade():
    assert rodar("h1b_engine_sha.py", stop(RAIZ), RAIZ).returncode == 0


# ------------------------------------------------------------------ H2: os testes rápidos no fim do turno


def test_h2_sem_mudanca_nao_roda(projeto):
    r = rodar("h2_testes.py", stop(projeto), projeto)
    assert r.returncode == 0 and r.stderr == b""


def test_h2_roda_o_teste_do_modulo_mudado_e_nao_bloqueia_duas_vezes(projeto):
    (projeto / "digilab" / "conta.py").write_text("def dobro(x):\n    return 3 * x\n", encoding="utf-8")
    sessao = f"teste-{uuid.uuid4().hex}"
    r = rodar("h2_testes.py", stop(projeto, sessao=sessao), projeto)
    assert r.returncode == 2 and b"tests/test_conta.py" in r.stderr
    assert rodar("h2_testes.py", stop(projeto, ativo=True, sessao=sessao), projeto).returncode == 0   # stop_hook_active
    assert rodar("h2_testes.py", stop(projeto, sessao=sessao), projeto).returncode == 0              # o mesmo motivo
    (projeto / "digilab" / "conta.py").write_text("def dobro(x):\n    return 2 * x\n", encoding="utf-8")
    assert rodar("h2_testes.py", stop(projeto, sessao=sessao), projeto).returncode == 0              # passou


def test_h2_teste_mudado_e_gabarito_tocado(projeto):
    (projeto / "tests" / "gabaritos").mkdir()
    (projeto / "tests" / "gabaritos" / "conta.json").write_text("{}", encoding="utf-8")
    (projeto / "tests" / "test_gabarito.py").write_text(
        "from pathlib import Path\n\n\ndef test_gabarito():\n    assert (Path(__file__).parent / 'gabaritos' / 'conta.json').read_text() == '{}'\n",
        encoding="utf-8")
    git(projeto, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    git(projeto, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "gabarito")
    (projeto / "tests" / "gabaritos" / "conta.json").write_text("{\"x\": 1}", encoding="utf-8")
    r = rodar("h2_testes.py", stop(projeto), projeto)
    assert r.returncode == 2 and b"tests/test_gabarito.py" in r.stderr


def test_h2_mudanca_fora_das_pastas_nao_roda(projeto):
    (projeto / "LEIA.md").write_text("x\n", encoding="utf-8")
    assert rodar("h2_testes.py", stop(projeto), projeto).returncode == 0


# ------------------------------------------------------------------ H3: o merge e o push na main


def decisao(r: subprocess.CompletedProcess) -> str | None:
    assert r.returncode == 0, r.stderr
    if not r.stdout.strip():
        return None
    return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]


@pytest.mark.parametrize("comando", [
    "gh pr merge 312 --merge",
    "git push origin main",
    "git push origin HEAD:main",
    "git push --force origin +v2-x:main",
    "git push origin refs/heads/main",
    "git push --all origin",
    "git -C D:/Trab/digilab/v2 push origin main",
    "cd /d/Trab && git push origin main",
    "git status; git push origin main",
])
def test_h3_pergunta(projeto, comando):
    for tool in ("Bash", "PowerShell"):
        assert decisao(rodar("h3_main.py", pre_tool(tool, {"command": comando}, projeto), projeto)) == "ask"


@pytest.mark.parametrize("comando", [
    "git merge origin/main",
    "git merge --no-commit origin/main",
    "git push origin v2-saude-etapa4",
    "git push -u origin v2-saude-etapa4",
    "git fetch origin main",
    "gh pr view 312",
    "gh pr create --base main --head v2-x",
    "git log --oneline origin/main",
])
def test_h3_nao_pergunta(projeto, comando):
    git(projeto, "checkout", "-q", "-b", "v2-x")
    assert decisao(rodar("h3_main.py", pre_tool("Bash", {"command": comando}, projeto), projeto)) is None


def test_h3_push_sem_refspec_depende_do_branch(projeto):
    assert decisao(rodar("h3_main.py", pre_tool("Bash", {"command": "git push"}, projeto), projeto)) == "ask"
    git(projeto, "checkout", "-q", "-b", "v2-x")
    assert decisao(rodar("h3_main.py", pre_tool("Bash", {"command": "git push"}, projeto), projeto)) is None


def test_proposta_desligada_e_valida():
    """A configuração proposta existe, aponta os scripts que existem, e o projeto não tem hook ligado."""
    proposta = json.loads((RAIZ / "docs" / "propostas" / "hooks_settings.json").read_text(encoding="utf-8"))
    comandos = [h["command"] for evento in proposta["hooks"].values() for grupo in evento for h in grupo["hooks"]]
    assert sorted(Path(c.split("/.claude/hooks/")[1].rstrip('"')).name for c in comandos) == \
        ["h1_engine.py", "h1b_engine_sha.py", "h2_testes.py", "h3_main.py"]
    assert all((HOOKS / Path(c.split("/.claude/hooks/")[1].rstrip('"')).name).exists() for c in comandos)
    ativo = RAIZ / ".claude" / "settings.json"
    assert not ativo.exists() or "hooks" not in json.loads(ativo.read_text(encoding="utf-8"))
