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


def rodar(script: str, evento: dict, projeto: Path, **extra: str) -> subprocess.CompletedProcess:
    env = {**__import__("os").environ, "CLAUDE_PROJECT_DIR": str(projeto), **extra}
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


def test_proposta_e_os_hooks_ligados():
    """A configuração proposta existe e aponta os scripts que existem. Ligados no projeto, os que o Matheus escolheu: o H1, o H1b e o
    H3 (2026-10-14, religados no #590); o H4, o H6 e o H9 (D-IA-7, 2026-11-06). O H2 fica desligado até a medida do Stop."""
    proposta = json.loads((RAIZ / "docs" / "propostas" / "hooks_settings.json").read_text(encoding="utf-8"))
    comandos = [h["command"] for evento in proposta["hooks"].values() for grupo in evento for h in grupo["hooks"]]
    assert sorted({Path(c.split("/.claude/hooks/")[1].rstrip('"')).name for c in comandos}) == \
        ["h1_engine.py", "h1b_engine_sha.py", "h2_testes.py", "h3_main.py", "h4_autorizo.py", "h6_capturas.py", "h9_faixas.py"]
    assert all((HOOKS / Path(c.split("/.claude/hooks/")[1].rstrip('"')).name).exists() for c in comandos)
    ativo = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
    ligados = [h["command"] for evento in ativo["hooks"].values() for grupo in evento for h in grupo["hooks"]]
    assert sorted({Path(c.split("/.claude/hooks/")[1].rstrip('"')).name for c in ligados}) == \
        ["h1_engine.py", "h1b_engine_sha.py", "h3_main.py", "h4_autorizo.py", "h6_capturas.py", "h9_faixas.py"]
    assert set(ligados) <= set(comandos)


# ------------------------------------------------------------------ INFRA_AGENTES E1 (docs/TAREFA_V3_INFRA_AGENTES.md, seção 3.1)

FAIXAS_TEXTO = (
    'FAIXAS_QUEIMADAS = ((15101, 15505, "a validacao antiga"),)\n'
    'FAIXAS_RESERVADAS = (\n    (77101, 77505, "C4"),\n)\n')


def commitar(projeto: Path, mensagem: str) -> None:
    git(projeto, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    git(projeto, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", mensagem)


@pytest.fixture
def com_faixas(projeto):
    """O projeto com um experiments/bancada/faixas.py pequeno, commitado, e o origin/main apontando para esse commit."""
    (projeto / "experiments" / "bancada").mkdir(parents=True)
    (projeto / "experiments" / "bancada" / "faixas.py").write_text(FAIXAS_TEXTO, encoding="utf-8")
    commitar(projeto, "faixas")
    git(projeto, "update-ref", "refs/remotes/origin/main", "HEAD")
    return projeto


def test_h1b_faixas_queimadas_contra_o_origin_main(com_faixas):
    p = com_faixas
    faixas = p / "experiments" / "bancada" / "faixas.py"
    assert rodar("h1b_engine_sha.py", stop(p), p).returncode == 0
    faixas.write_text(FAIXAS_TEXTO.replace('"a validacao antiga"', '"outro texto"'), encoding="utf-8")
    assert rodar("h1b_engine_sha.py", stop(p), p).returncode == 2          # a entrada antiga mudou
    faixas.write_text(FAIXAS_TEXTO.replace('"a validacao antiga"),)', '"a validacao antiga"), (16101, 16505, "nova"),)'),
                      encoding="utf-8")
    assert rodar("h1b_engine_sha.py", stop(p), p).returncode == 0          # só entrou uma no fim
    faixas.write_text(FAIXAS_TEXTO.replace('(15101, 15505, "a validacao antiga"),', ''), encoding="utf-8")
    r = rodar("h1b_engine_sha.py", stop(p), p)                             # sumiu, como faria um sed
    assert r.returncode == 2 and b"FAIXAS_QUEIMADAS" in r.stderr


def test_h1b_sem_origin_main_falha_alto(com_faixas):
    git(com_faixas, "update-ref", "-d", "refs/remotes/origin/main")
    r = rodar("h1b_engine_sha.py", stop(com_faixas), com_faixas)
    assert r.returncode == 2 and b"git fetch" in r.stderr


def test_h2_replay_so_com_mudanca_em_digilab_ou_bancada(projeto):
    (projeto / "tests" / "test_engine.py").write_text("def test_replay():\n    assert False\n", encoding="utf-8")
    commitar(projeto, "replay")
    conta = projeto / "tests" / "test_conta.py"
    conta.write_text(conta.read_text(encoding="utf-8") + "\n# so o teste mudou\n", encoding="utf-8")
    r = rodar("h2_testes.py", stop(projeto), projeto)                      # só tests/ mudou: o replay não entra
    assert r.returncode == 0, r.stderr
    (projeto / "digilab" / "conta.py").write_text("def dobro(x):\n    return x + x\n", encoding="utf-8")
    r = rodar("h2_testes.py", stop(projeto), projeto)
    assert r.returncode == 2 and b"tests/test_engine.py" in r.stderr


def test_h2_testes_da_frente_pelo_branch(projeto):
    (projeto / "tests" / "test_conta_frente.py").write_text("def test_frente():\n    assert False\n", encoding="utf-8")
    commitar(projeto, "frente")
    git(projeto, "checkout", "-q", "-b", "v3-conta-frente-e1")             # o prefixo mais longo que acha: conta_frente
    conta = projeto / "tests" / "test_conta.py"
    conta.write_text(conta.read_text(encoding="utf-8") + "\n# mudado\n", encoding="utf-8")
    r = rodar("h2_testes.py", stop(projeto), projeto)
    assert r.returncode == 2 and b"tests/test_conta_frente.py" in r.stderr


def test_h2_estouro_do_limite_bloqueia_uma_vez(projeto):
    (projeto / "tests" / "test_conta.py").write_text("import time\n\n\ndef test_lento():\n    time.sleep(30)\n", encoding="utf-8")
    sessao = f"teste-{uuid.uuid4().hex}"
    r = rodar("h2_testes.py", stop(projeto, sessao=sessao), projeto, DIGILAB_H2_LIMITE_S="2")
    assert r.returncode == 2 and b"passaram de 2 s" in r.stderr
    assert rodar("h2_testes.py", stop(projeto, sessao=sessao), projeto, DIGILAB_H2_LIMITE_S="2").returncode == 0


@pytest.mark.parametrize("caminho", [
    "web/app/e2e/jogo.spec.ts-snapshots/pet-390.png",
    "web/app/test/algo-snapshots/x.png",
    "CAPTURAS",
])
def test_h6_nega_editar_referencia(projeto, caminho):
    capturas = projeto.parent / "capturas_fora"
    alvo = str(capturas / "telas" / "pet.png") if caminho == "CAPTURAS" else caminho
    for tool in ("Edit", "Write"):
        r = rodar("h6_capturas.py", pre_tool(tool, {"file_path": alvo}, projeto), projeto, DIGILAB_CAPTURAS=str(capturas))
        assert r.returncode == 2 and b"H6" in r.stderr


def test_h6_pasta_padrao_das_capturas(projeto):
    alvo = projeto / "artifacts_v2_front_react" / "capturas" / "pet.png"
    r = rodar("h6_capturas.py", pre_tool("Write", {"file_path": str(alvo)}, projeto), projeto, DIGILAB_CAPTURAS="")
    assert r.returncode == 2


@pytest.mark.parametrize("comando", [
    "rm -rf web/app/e2e/jogo.spec.ts-snapshots",
    "cd web/app && mv novo.png e2e/jogo.spec.ts-snapshots/pet.png",
    "Remove-Item -Recurse web\\app\\e2e\\jogo.spec.ts-snapshots",
    "echo x > web/app/e2e/a-snapshots/b.png",
    "git checkout -- web/app/e2e/jogo.spec.ts-snapshots/pet.png",
])
def test_h6_nega_o_shell_que_escreve(projeto, comando):
    for tool in ("Bash", "PowerShell"):
        r = rodar("h6_capturas.py", pre_tool(tool, {"command": comando}, projeto), projeto)
        assert r.returncode == 2 and b"H6" in r.stderr, comando


@pytest.mark.parametrize("comando", [
    "npx playwright test -u",
    "cd web/app && npx playwright test e2e/jogo.spec.ts --update-snapshots",
    "npm run e2e -- -u",
    "npm run capturas -- --update-snapshots=all",
])
def test_h6_pergunta_no_update_snapshots(projeto, comando):
    assert decisao(rodar("h6_capturas.py", pre_tool("Bash", {"command": comando}, projeto), projeto)) == "ask"


@pytest.mark.parametrize("comando", [
    "git push -u origin v3-x",
    "npm run e2e",
    "npx playwright test e2e/jogo.spec.ts",
    "ls web/app/e2e/jogo.spec.ts-snapshots",
    "git diff -- web/app/e2e/jogo.spec.ts-snapshots",
    "rm web/app/test-results/x.png",
])
def test_h6_deixa_o_resto(projeto, comando):
    assert decisao(rodar("h6_capturas.py", pre_tool("Bash", {"command": comando}, projeto), projeto)) is None


def test_h6_deixa_editar_codigo(projeto):
    r = rodar("h6_capturas.py", pre_tool("Edit", {"file_path": "web/app/src/App.tsx"}, projeto), projeto)
    assert r.returncode == 0 and r.stdout == b"" and r.stderr == b""


def editar_faixas(projeto: Path, velho: str, novo: str) -> dict:
    return pre_tool("Edit", {"file_path": "experiments/bancada/faixas.py", "old_string": velho, "new_string": novo}, projeto)


@pytest.mark.parametrize("velho,novo", [
    ('(15101, 15505, "a validacao antiga"),', ''),
    ('(15101, 15505, ', '(15101, 15500, '),
    ('FAIXAS_QUEIMADAS = (', 'FAIXAS_QUEIMADAS_ANTIGAS = ('),
])
def test_h9_remover_ou_mudar_queimada_nega(com_faixas, velho, novo):
    r = rodar("h9_faixas.py", editar_faixas(com_faixas, velho, novo), com_faixas)
    assert r.returncode == 2 and b"H9" in r.stderr


def test_h9_queimar_faixa_nova_pergunta(com_faixas):
    r = rodar("h9_faixas.py", editar_faixas(com_faixas, '"a validacao antiga"),)', '"a validacao antiga"), (16101, 16505, "caiu"),)'),
              com_faixas)
    assert decisao(r) == "ask" and "16101...16505" in json.loads(r.stdout)["hookSpecificOutput"]["permissionDecisionReason"]


def test_h9_reservada_passa_e_outros_arquivos_tambem(com_faixas):
    p = com_faixas
    nova = '(77101, 77505, "C4"),\n    (79101, 79505, "nova"),'
    assert decisao(rodar("h9_faixas.py", editar_faixas(p, '(77101, 77505, "C4"),', nova), p)) is None
    outro = pre_tool("Edit", {"file_path": "digilab/conta.py", "old_string": "2", "new_string": "3"}, p)
    assert decisao(rodar("h9_faixas.py", outro, p)) is None


def test_h9_write_e_multiedit(com_faixas):
    p = com_faixas
    caminho = str(p / "experiments" / "bancada" / "faixas.py")
    r = rodar("h9_faixas.py", pre_tool("Write", {"file_path": caminho, "content": "FAIXAS_QUEIMADAS = ()\n"}, p), p)
    assert r.returncode == 2
    pares = [{"old_string": '"C4"', "new_string": '"C4 da V3"'}, {"old_string": '"a validacao antiga"', "new_string": '"outra"'}]
    r = rodar("h9_faixas.py", pre_tool("MultiEdit", {"file_path": caminho, "edits": pares}, p), p)
    assert r.returncode == 2
    r = rodar("h9_faixas.py", pre_tool("Write", {"file_path": caminho, "content": "FAIXAS_QUEIMADAS = (\n"}, p), p)
    assert r.returncode == 2 and b"consigo ler" in r.stderr
