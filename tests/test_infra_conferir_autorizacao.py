"""A conferência da autorização de implementação (tools/conferir_autorizacao.py): só o Matheus, fora de app, sem edição, no SHA atual."""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import conferir_autorizacao as ca  # noqa: E402

TAREFA = "docs/TAREFA_V2_X.md"
SHA = "3b18e512dba79e4c8300dd08aeb37f8e728b8dad"


def comentario(corpo=None, login="matheusmmmp", tipo="User", app=None, editado=False):
    corpo = corpo if corpo is not None else f"AUTORIZO IMPLEMENTAÇÃO: {TAREFA}\nblob SHA: {SHA[:12]}\nEscopo: seção 3 dessa tarefa\n"
    return {
        "id": 1, "body": corpo, "user": {"login": login, "type": tipo},
        "performed_via_github_app": app,
        "created_at": "2026-10-19T10:00:00Z", "updated_at": "2026-10-19T10:05:00Z" if editado else "2026-10-19T10:00:00Z",
    }


def um(c):
    vs = ca.conferir([c], TAREFA, SHA, "matheusmmmp")
    assert len(vs) == 1
    return vs[0]


def test_autorizacao_do_matheus_vale():
    v = um(comentario())
    assert v.valido and v.motivos == []


def test_comentario_que_nao_e_autorizacao_e_ignorado():
    assert ca.conferir([comentario("Tarefa formalizada no PR #337.")], TAREFA, SHA, "matheusmmmp") == []


def test_escrita_pelo_chatgpt_work_nao_vale():
    """O caso real do passo 6: autor matheusmmmp, mas via o app do conector."""
    v = um(comentario(app={"name": "ChatGPT Codex Connector"}))
    assert not v.valido and "ChatGPT Codex Connector" in v.motivos[0]


def test_outro_autor_ou_bot_nao_vale():
    assert not um(comentario(login="outra-pessoa")).valido
    assert not um(comentario(tipo="Bot")).valido


def test_comentario_editado_nao_vale():
    assert "editado" in um(comentario(editado=True)).motivos[0]


def test_sha_diferente_ou_ausente_nao_vale():
    outro = comentario(f"AUTORIZO IMPLEMENTAÇÃO: {TAREFA}\nblob SHA: deadbeef1234\n")
    assert "não é o da tarefa hoje" in um(outro).motivos[0]
    sem = comentario(f"AUTORIZO IMPLEMENTAÇÃO: {TAREFA}\n")
    assert um(sem).motivos == ["sem linha 'blob SHA:'"]


def test_outra_tarefa_nao_vale():
    c = comentario(f"AUTORIZO IMPLEMENTAÇÃO: docs/TAREFA_V2_Y.md\nblob SHA: {SHA[:12]}\n")
    assert "não 'docs/TAREFA_V2_X.md'" in um(c).motivos[0]


def test_todos_os_motivos_aparecem_juntos():
    v = um(comentario(f"AUTORIZO IMPLEMENTAÇÃO: {TAREFA}\nblob SHA: deadbeef\n", app={"name": "X"}, editado=True))
    assert len(v.motivos) == 3


def test_sha_do_blob_bate_com_o_git(tmp_path):
    def g(*a):
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)
    g("init", "-q")
    (tmp_path / "docs").mkdir()
    (tmp_path / TAREFA).write_text("# tarefa\n", encoding="utf-8")
    g("add", "-A")
    g("commit", "-q", "-m", "t")
    sha = ca.sha_do_blob(tmp_path, "HEAD", TAREFA)
    esperado = subprocess.run(["git", "-C", str(tmp_path), "hash-object", TAREFA], capture_output=True, text=True).stdout.strip()
    assert sha == esperado
