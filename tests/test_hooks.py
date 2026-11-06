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
    H3 (2026-10-14, religados no #590); o H4, o H6 e o H9 (D-IA-7, 2026-11-06); o H2, depois da medida do Stop, e o H10 (E3), os dois em
    2026-11-06. A
    proposta e o projeto ficam iguais."""
    proposta = json.loads((RAIZ / "docs" / "propostas" / "hooks_settings.json").read_text(encoding="utf-8"))
    comandos = [h["command"] for evento in proposta["hooks"].values() for grupo in evento for h in grupo["hooks"]]
    assert sorted({Path(c.split("/.claude/hooks/")[1].rstrip('"')).name for c in comandos}) == \
        ["h10_pre_run.py", "h1_engine.py", "h1b_engine_sha.py", "h2_testes.py", "h3_main.py", "h4_autorizo.py", "h6_capturas.py",
         "h9_faixas.py"]
    assert all((HOOKS / Path(c.split("/.claude/hooks/")[1].rstrip('"')).name).exists() for c in comandos)
    ativo = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
    ligados = [h["command"] for evento in ativo["hooks"].values() for grupo in evento for h in grupo["hooks"]]
    assert sorted({Path(c.split("/.claude/hooks/")[1].rstrip('"')).name for c in ligados}) == \
        ["h10_pre_run.py", "h1_engine.py", "h1b_engine_sha.py", "h2_testes.py", "h3_main.py", "h4_autorizo.py", "h6_capturas.py",
         "h9_faixas.py"]
    assert ativo == proposta


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
def test_h6_nega_editar_referencia_infra(projeto, caminho):
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
def test_h6_pergunta_no_update_snapshots_infra(projeto, comando):
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


# ------------------------------------------------------------------ H10: o pre_run antes da run (INFRA_AGENTES E3, seção 3.3)


@pytest.fixture
def com_pre_run(com_faixas):
    """O projeto com as faixas, o tools/pre_run.py de verdade, um plano na main e uma config com a faixa reservada 77101...77505."""
    p = com_faixas
    (p / "tools").mkdir()
    shutil.copyfile(RAIZ / "tools" / "pre_run.py", p / "tools" / "pre_run.py")
    (p / "docs").mkdir()
    (p / "docs" / "PLANO_ANALISE_V3_X.md").write_text("# plano\n", encoding="utf-8")
    (p / "experiments" / "configs").mkdir()
    (p / "experiments" / "configs" / "x.json").write_text(
        json.dumps({"plano": "docs/PLANO_ANALISE_V3_X.md", "unidades": {"bases": [77101], "k": 1}}), encoding="utf-8")
    (p / "experiments" / "configs" / "queimada.json").write_text(
        json.dumps({"plano": "docs/PLANO_ANALISE_V3_X.md", "unidades": {"bases": [15101], "k": 1}}), encoding="utf-8")
    commitar(p, "plano e configs")
    git(p, "update-ref", "refs/remotes/origin/main", "HEAD")
    return p


def h10(p: Path, comando: str, tool: str = "Bash", processos: str = "[]") -> subprocess.CompletedProcess:
    return rodar("h10_pre_run.py", pre_tool(tool, {"command": comando}, p), p, DIGILAB_PRE_RUN_PROCESSOS=processos)


@pytest.mark.parametrize("comando", [
    "python experiments/run_v3_x.py --config experiments/configs/x.json --processos 4",
    "cd D:/Trab && python experiments/run_v2_y.py --config=experiments/configs/x.json",
    "python experiments/run_v3_x.py --help",
    "python -m pytest tests/test_run_v2_y.py -q",
    "git log -- experiments/run_v2_y.py",
])
def test_h10_deixa_passar(com_pre_run, comando):
    for tool in ("Bash", "PowerShell"):
        r = h10(com_pre_run, comando, tool)
        assert r.returncode == 0, r.stderr.decode("utf-8", "replace")


@pytest.mark.parametrize("comando,texto", [
    ("python experiments/run_v3_x.py --config experiments/configs/x.json --processos 5", "no máximo 4"),
    (r"python experiments\run_v3_x.py --config experiments/configs/queimada.json", "faixa queimada"),
    (".venv/Scripts/python.exe experiments/run_v2_y.py --config experiments/configs/nao_existe.json", "não existe"),
    ("python experiments/run_v3_x.py --processos 2", "sem --config"),
])
def test_h10_recusa(com_pre_run, comando, texto):
    r = h10(com_pre_run, comando)
    assert r.returncode == 2 and texto in r.stderr.decode("utf-8")


def test_h10_outra_run_em_andamento(com_pre_run):
    r = h10(com_pre_run, "python experiments/run_v3_x.py --config experiments/configs/x.json",
            processos=json.dumps(["python experiments/run_v3_outra.py --config c.json"]))
    assert r.returncode == 2 and "outra run" in r.stderr.decode("utf-8")


# ------------------------------------------------------------------ A1 da UX_TELA_PET (docs/TAREFA_V3_UX_TELA_PET.md, seção 3.3)
# H5, H6 e H8 estão DESLIGADOS: a proposta fica em docs/propostas/hooks_ux_settings.json (SA-5; UX-5).


def rodar_com(script: str, evento: dict, projeto: Path, *args: str, **env_extra: str) -> subprocess.CompletedProcess:
    env = {**__import__("os").environ, "CLAUDE_PROJECT_DIR": str(projeto), **env_extra}
    return subprocess.run([sys.executable, str(HOOKS / script), *args], input=json.dumps(evento).encode("utf-8"), capture_output=True,
                          env=env, cwd=projeto, timeout=600)


@pytest.fixture
def projeto_web(projeto):
    """O projeto pequeno com um web/app mínimo, num branch de worker saído da main."""
    for pasta in ("web/app/src", "web/app/test", "web/app/motor"):
        (projeto / pasta).mkdir(parents=True)
    (projeto / "web" / "app" / "src" / "tela.ts").write_text("export const x = 1;\n", encoding="utf-8")
    git(projeto, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    git(projeto, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "web")
    git(projeto, "checkout", "-q", "-b", "v3-x")
    return projeto


def passos_falsos(passa: bool, marca: str = "x") -> str:
    """Os passos do H5 trocados por um Python que passa ou falha com uma linha FAIL (DIGILAB_H5_PASSOS)."""
    codigo = "print('ok')" if passa else f"import sys; print(' FAIL  test/tela.test.ts > {marca}'); sys.exit(1)"
    return json.dumps([["vitest", [sys.executable, "-c", codigo]]])


def test_h5_sem_mudanca_no_web_nao_roda(projeto_web):
    (projeto_web / "LEIA.md").write_text("x\n", encoding="utf-8")
    r = rodar_com("h5_web.py", stop(projeto_web), projeto_web, DIGILAB_H5_BASE="main", DIGILAB_H5_PASSOS=passos_falsos(False))
    assert r.returncode == 0 and r.stderr == b""


@pytest.mark.parametrize("como", ["nao_commitado", "commitado", "novo"])
def test_h5_roda_com_mudanca_no_web_e_nao_bloqueia_duas_vezes(projeto_web, como):
    tela = projeto_web / "web" / "app" / ("src/nova.ts" if como == "novo" else "src/tela.ts")
    tela.write_text("export const x = 2;\n", encoding="utf-8")
    if como == "commitado":
        git(projeto_web, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qam", "mudou")
    sessao = f"teste-{uuid.uuid4().hex}"
    falha = {"DIGILAB_H5_BASE": "main", "DIGILAB_H5_PASSOS": passos_falsos(False)}
    r = rodar_com("h5_web.py", stop(projeto_web, sessao=sessao), projeto_web, **falha)
    assert r.returncode == 2 and b"vitest" in r.stderr and b"FAIL" in r.stderr
    assert rodar_com("h5_web.py", stop(projeto_web, ativo=True, sessao=sessao), projeto_web, **falha).returncode == 0  # stop_hook_active
    assert rodar_com("h5_web.py", stop(projeto_web, sessao=sessao), projeto_web, **falha).returncode == 0              # o mesmo motivo
    outra = {**falha, "DIGILAB_H5_PASSOS": passos_falsos(False, "outro")}
    assert rodar_com("h5_web.py", stop(projeto_web, sessao=sessao), projeto_web, **outra).returncode == 2              # motivo novo
    ok = {**falha, "DIGILAB_H5_PASSOS": passos_falsos(True)}
    assert rodar_com("h5_web.py", stop(projeto_web, sessao=sessao), projeto_web, **ok).returncode == 0


def test_h5_para_no_primeiro_passo_que_falha(projeto_web):
    (projeto_web / "web" / "app" / "motor" / "m.ts").write_text("x\n", encoding="utf-8")
    passos = json.dumps([["tipos", [sys.executable, "-c", "import sys; print('error TS2322: x'); sys.exit(1)"]],
                         ["e2e", [sys.executable, "-c", "raise SystemExit('nao devia rodar')"]]])
    r = rodar_com("h5_web.py", stop(projeto_web), projeto_web, DIGILAB_H5_BASE="main", DIGILAB_H5_PASSOS=passos)
    assert r.returncode == 2 and b"'tipos'" in r.stderr and b"error TS2322" in r.stderr and b"nao devia" not in r.stderr


def test_h5_passo_longo_demais_nao_bloqueia(projeto_web):
    (projeto_web / "web" / "app" / "src" / "tela.ts").write_text("export const x = 3;\n", encoding="utf-8")
    passos = json.dumps([["e2e", [sys.executable, "-c", "import time; time.sleep(5)"]]])
    r = rodar_com("h5_web.py", stop(projeto_web), projeto_web, DIGILAB_H5_BASE="main", DIGILAB_H5_PASSOS=passos, DIGILAB_H5_LIMITE_S="1")
    assert r.returncode == 0


@pytest.mark.parametrize("alvo", ["web/app/e2e/jogo.spec.ts-snapshots/tela-gpu.png", "web/app/e2e_capturas/x-snapshots/a.png",
                                  "artifacts_v2_front_react/capturas/pet_390.png", "CAPTURAS_ABS"])
def test_h6_nega_editar_referencia(projeto, alvo):
    if alvo == "CAPTURAS_ABS":
        alvo = str(projeto / "artifacts_v2_front_react" / "capturas" / "sub" / "x.png")
    for tool in ("Edit", "Write"):
        r = rodar_com("h6_capturas.py", pre_tool(tool, {"file_path": alvo}, projeto), projeto)
        assert r.returncode == 2 and b"H6" in r.stderr


def test_h6_respeita_digilab_capturas(projeto, tmp_path):
    fora = tmp_path / "refs"
    r = rodar_com("h6_capturas.py", pre_tool("Write", {"file_path": str(fora / "a.png")}, projeto), projeto, DIGILAB_CAPTURAS=str(fora))
    assert r.returncode == 2
    padrao = "artifacts_v2_front_react/capturas/a.png"   # com outra pasta definida, a padrão deixa de ser referência
    assert rodar_com("h6_capturas.py", pre_tool("Write", {"file_path": padrao}, projeto), projeto, DIGILAB_CAPTURAS=str(fora)).returncode == 0


@pytest.mark.parametrize("alvo", ["web/app/src/telas/pet/TelaPet.tsx", "docs/pranchas/ux-pet/a.png", "web/app/e2e/jogo.spec.ts",
                                  "capturas_ux_pet_aprovar/pet.png"])
def test_h6_deixa_os_outros(projeto, alvo):
    r = rodar_com("h6_capturas.py", pre_tool("Write", {"file_path": alvo}, projeto), projeto)
    assert r.returncode == 0 and r.stdout == b"" and r.stderr == b""


@pytest.mark.parametrize("comando", [
    "npx playwright test -u",
    "npx playwright test e2e/jogo.spec.ts --update-snapshots",
    "npx playwright test --update-snapshots=changed",
    "npm run e2e -- -u",
    "cd web/app && npm run capturas -- --update-snapshots",
])
def test_h6_pergunta_no_update_snapshots(projeto, comando):
    for tool in ("Bash", "PowerShell"):
        assert decisao(rodar_com("h6_capturas.py", pre_tool(tool, {"command": comando}, projeto), projeto)) == "ask"


@pytest.mark.parametrize("comando", [
    "rm web/app/e2e/jogo.spec.ts-snapshots/tela-gpu.png",
    "cp nova.png web/app/e2e/jogo.spec.ts-snapshots/tela-gpu.png",
    "Remove-Item -Recurse artifacts_v2_front_react/capturas",
    "echo x > artifacts_v2_front_react/capturas/a.png",
    "git checkout -- web/app/e2e/jogo.spec.ts-snapshots/",
])
def test_h6_nega_escrever_pelo_shell(projeto, comando):
    r = rodar_com("h6_capturas.py", pre_tool("Bash", {"command": comando}, projeto), projeto)
    assert r.returncode == 2 and b"H6" in r.stderr


@pytest.mark.parametrize("comando", [
    "npx playwright test",
    "npm run e2e",
    "git push -u origin v3-x",
    "ls web/app/e2e/jogo.spec.ts-snapshots/",
    "git diff -- web/app/e2e/jogo.spec.ts-snapshots/",
    "npm run capturas 2>&1 | tail -5",
])
def test_h6_deixa_os_outros_comandos(projeto, comando):
    r = rodar_com("h6_capturas.py", pre_tool("Bash", {"command": comando}, projeto), projeto)
    assert r.returncode == 0 and r.stdout == b"" and r.stderr == b""


@pytest.mark.parametrize("papel,tool,alvo,passa", [
    ("designer", "Write", "docs/pranchas/ux-pet/b/prancha.html", True),
    ("designer", "Edit", "docs/PROPOSTAS_V3_UX_TELA_PET.md", True),
    ("designer", "Write", "web/app/src/telas/pet/TelaPet.tsx", False),
    ("designer", "Write", "docs/pranchas/b3/x.html", False),
    ("implementador", "Edit", "web/app/src/telas/pet/TelaPet.tsx", True),
    ("implementador", "Write", "web/app/src/estilo/pet_hud.css", True),
    ("implementador", "Edit", "web/app/motor/motor.ts", False),
    ("implementador", "Edit", "web/app/test/gabaritos/vida.json", False),
    ("implementador", "Edit", "web/app/src/save.ts", False),
    ("implementador", "Edit", "web/app/src/rotas.ts", False),
    ("implementador", "Edit", "digilab/config.py", False),
    ("implementador", "Write", "experiments/run_x.py", False),
    ("implementador", "Write", "servidor/servidor_local.py", False),
    ("implementador", "Write", "web/app/e2e/jogo.spec.ts-snapshots/a.png", False),
    ("implementador", "Write", "FORA", False),
    ("testador", "Write", "docs/qualquer.md", False),
    ("testador", "Edit", "web/app/src/telas/pet/TelaPet.tsx", False),
])
def test_h8_escrita_por_papel(projeto, tmp_path, papel, tool, alvo, passa):
    if alvo == "FORA":
        alvo = str(tmp_path / "outro" / "a.ts")
    r = rodar_com("h8_escopo.py", pre_tool(tool, {"file_path": alvo}, projeto), projeto, papel)
    assert (r.returncode == 0) == passa, r.stderr.decode("utf-8")
    if not passa:
        assert b"H8" in r.stderr


@pytest.mark.parametrize("comando,passa", [
    ("npm run build", True),
    ("npm run e2e", True),
    ("npm run e2e -- e2e/jogo.spec.ts", True),
    ("npm run tipos", True),                    # INFRA_AGENTES E4 (seção 3.4)
    ("npm test", True),
    ("cd web/app && npm run test", True),
    ("npm test -- --update", False),
    ("DIGILAB_CAPTURAS_LARGURAS=390,1920 npm run capturas", True),
    ("cd web/app && npx playwright test e2e/jogo.spec.ts --project=gpu", True),
    ("git diff --stat", True),
    ("ls test-results", True),
    ("npx playwright test -u", False),
    ("npm run capturas -- --update-snapshots", False),
    ("npm install", False),
    ("npm run dev", False),
    ("rm -rf test-results", False),
    ("cat a.txt > b.txt", False),
    ("python -c \"open('x','w')\"", False),
    ("git checkout main", False),
    ("find . -delete", False),
])
def test_h8_shell_do_testador(projeto, comando, passa):
    for tool in ("Bash", "PowerShell"):
        r = rodar_com("h8_escopo.py", pre_tool(tool, {"command": comando}, projeto), projeto, "testador")
        assert (r.returncode == 0) == passa, (comando, r.stderr.decode("utf-8"))


@pytest.mark.parametrize("comando,passa", [
    ("sha256sum artifacts_v3_acoes_novas/run/run.log", True),       # INFRA_AGENTES E6: o hash e o tamanho dos artefatos
    ("stat -c %s artifacts_v3_acoes_novas/run/medidas.json", True),
    ("Get-FileHash artifacts_v3_acoes_novas/run/run.log", True),
    ("du -b artifacts_v3_acoes_novas/run/vidas.tar.gz", True),
    ("cat docs/RESULTADO_V3_ACOES_NOVAS.md", True),
    ("python -c \"print(1)\"", False),
    ("rm artifacts_v3_acoes_novas/run/run.log", False),
    ("sha256sum x > y.txt", False),
    ("find . -name x -delete", False),
    ("npm test", False),
])
def test_h8_shell_do_auditor(projeto, comando, passa):
    for tool in ("Bash", "PowerShell"):
        r = rodar_com("h8_escopo.py", pre_tool(tool, {"command": comando}, projeto), projeto, "auditor")
        assert (r.returncode == 0) == passa, (comando, r.stderr.decode("utf-8"))


def test_h8_auditor_nao_escreve(projeto):
    for tool in ("Edit", "Write"):
        r = rodar_com("h8_escopo.py", pre_tool(tool, {"file_path": "docs/RESULTADO_V3_X.md"}, projeto), projeto, "auditor")
        assert r.returncode == 2 and "auditor" in r.stderr.decode("utf-8")


def test_h8_designer_sem_shell_implementador_com_shell(projeto):
    assert rodar_com("h8_escopo.py", pre_tool("Bash", {"command": "ls"}, projeto), projeto, "designer").returncode == 2
    assert rodar_com("h8_escopo.py", pre_tool("Bash", {"command": "npm test"}, projeto), projeto, "implementador").returncode == 0


@pytest.mark.parametrize("args", [(), ("gerente",), ("designer", "extra")])
def test_h8_papel_desconhecido_bloqueia(projeto, args):
    r = rodar_com("h8_escopo.py", pre_tool("Write", {"file_path": "docs/pranchas/ux-pet/a.html"}, projeto), projeto, *args)
    assert r.returncode == 2 and b"papel desconhecido" in r.stderr


def test_proposta_ux_aponta_scripts_que_existem_e_nada_ligado():
    """A proposta da A1 existe e aponta os scripts que existem. Do settings.json, o H5 e o H8 ficam de fora (SA-5); o H6 está ligado
    desde a INFRA_AGENTES E1 (D-IA-5 e D-IA-7, o mesmo arquivo nas duas frentes; docs/TAREFA_V3_INFRA_AGENTES.md, seção 12)."""
    proposta = json.loads((RAIZ / "docs" / "propostas" / "hooks_ux_settings.json").read_text(encoding="utf-8"))
    comandos = [h["command"] for evento in proposta["hooks"].values() for grupo in evento for h in grupo["hooks"]]
    comandos += [a["command"] for a in proposta["agentes_h8"].values()]
    nomes = {c.split("/.claude/hooks/")[1].split('"')[0] for c in comandos}
    assert nomes == {"h5_web.py", "h6_capturas.py", "h8_escopo.py"}
    assert all((HOOKS / n).exists() for n in nomes)
    assert sorted(proposta["agentes_h8"]) == ["designer", "implementador", "testador"]
    ativo = (RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8")
    assert not any(n in ativo for n in nomes - {"h6_capturas.py"})
    assert "h6_capturas.py" in ativo
