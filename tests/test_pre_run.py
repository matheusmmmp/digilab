"""INFRA_AGENTES E3 (docs/TAREFA_V3_INFRA_AGENTES.md, seção 3.3): o tools/pre_run.py recusa a run sem plano na main, com base fora das
faixas reservadas ou numa queimada, com outra run em andamento ou com mais de 4 processos. Cada caso monta um repositório pequeno, com um
origin/main local, e troca a lista de processos da máquina pela DIGILAB_PRE_RUN_PROCESSOS.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import pre_run  # noqa: E402

ORQ = "experiments/run_v3_teste.py"
FAIXAS = ('FAIXAS_QUEIMADAS = ((15101, 15505, "a validacao antiga"),)\n'
          'FAIXAS_RESERVADAS = (\n    (101, 1010, "testes"),\n    (15101, 15505, "queimada, segue reservada"),\n'
          '    (78101, 78505, "AN4"),\n)\n')


def git(p: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    p = tmp_path / "repo"
    (p / "experiments" / "bancada").mkdir(parents=True)
    (p / "experiments" / "configs").mkdir()
    (p / "docs").mkdir()
    (p / "experiments" / "bancada" / "faixas.py").write_text(FAIXAS, encoding="utf-8")
    (p / "experiments" / "run_v3_teste.py").write_text("# orquestrador de teste\n", encoding="utf-8")
    (p / "docs" / "PLANO_ANALISE_V3_TESTE.md").write_text("# plano APROVADO\n", encoding="utf-8")
    git(p, "init", "-q", "-b", "main")
    git(p, "add", "-A")
    git(p, "commit", "-q", "-m", "inicio")
    git(p, "update-ref", "refs/remotes/origin/main", "HEAD")
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", "[]")
    return p


def config(p: Path, nome: str = "c.json", **campos) -> str:
    cfg = {"plano": "docs/PLANO_ANALISE_V3_TESTE.md", "unidades": {"bases": [78101, 78202], "k": 1}, **campos}
    (p / "experiments" / "configs" / nome).write_text(json.dumps(cfg), encoding="utf-8")
    return f"experiments/configs/{nome}"


def motivos(p: Path, cfg: str, processos: int = 4) -> list[str]:
    return pre_run.conferir(ORQ, cfg, processos, p)


def test_passa_com_a_faixa_reservada_e_com_as_sementes_de_teste(repo):
    assert motivos(repo, config(repo)) == []
    assert motivos(repo, config(repo, "v.json", unidades={"bases": [101, 202, 303, 404, 505], "k": 1})) == []


def test_plano_fora_do_git(repo):
    (repo / "docs" / "PLANO_ANALISE_V3_NOVO.md").write_text("# novo\n", encoding="utf-8")
    m = motivos(repo, config(repo, plano="docs/PLANO_ANALISE_V3_NOVO.md"))
    assert len(m) == 1 and "não está no git" in m[0]


def test_plano_sujo(repo):
    (repo / "docs" / "PLANO_ANALISE_V3_TESTE.md").write_text("# plano mudado depois\n", encoding="utf-8")
    assert any("não commitada" in x for x in motivos(repo, config(repo)))


def test_plano_que_nao_chegou_na_main(repo):
    (repo / "docs" / "PLANO_ANALISE_V3_TESTE.md").write_text("# plano com adendo\n", encoding="utf-8")
    git(repo, "commit", "-q", "-am", "adendo so no branch")
    assert any("não é o do origin/main" in x for x in motivos(repo, config(repo)))
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    assert any("git fetch" in x for x in motivos(repo, config(repo)))


@pytest.mark.parametrize("base,texto", [(15202, "faixa queimada"), (99101, "nenhuma faixa de FAIXAS_RESERVADAS")])
def test_base_queimada_ou_fora_das_reservadas(repo, base, texto):
    m = motivos(repo, config(repo, unidades={"bases": [78101, base], "k": 1}))
    assert len(m) == 1 and texto in m[0] and str(base) in m[0]


def test_outra_run_em_andamento(repo, monkeypatch):
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", json.dumps([
        "python -m pytest tests/test_x.py",
        r"C:\Python313\python.exe experiments\run_v2_memoria_autobio.py --config x.json --processos 4"]))
    m = motivos(repo, config(repo))
    assert len(m) == 1 and "outra run" in m[0] and "run_v2_memoria_autobio" in m[0]


def test_cinco_processos(repo):
    m = motivos(repo, config(repo), processos=5)
    assert len(m) == 1 and "no máximo 4" in m[0]


def test_config_sem_plano_e_sem_bases(repo):
    (repo / "experiments" / "configs" / "v2.json").write_text(json.dumps({"descricao": "da V2", "saida": "x"}), encoding="utf-8")
    m = motivos(repo, "experiments/configs/v2.json")
    assert any("`plano`" in x for x in m) and any("`unidades.bases`" in x for x in m)


def test_orquestrador_que_nao_e_run(repo):
    assert any("não é um orquestrador" in x for x in pre_run.conferir("tools/outra_coisa.py", config(repo), 1, repo))


def test_exigir_levanta(repo):
    with pytest.raises(pre_run.Recusa, match="no máximo 4"):
        pre_run.exigir(ORQ, config(repo), 5, repo)


def test_pela_linha_de_comando_no_repositorio_de_verdade(monkeypatch):
    """O critério da seção 3.3: a varredura da AN4 (as sementes dos testes) passa com 4 processos e é recusada com 5. O plano dela está na
    main desde a AN3; num checkout sem o origin/main, o teste pula."""
    if subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--verify", "--quiet", "origin/main"], capture_output=True).returncode:
        pytest.skip("sem origin/main neste checkout")
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", "[]")
    base = [sys.executable, str(RAIZ / "tools" / "pre_run.py"), "experiments/run_v3_acoes_novas.py",
            "--config", "experiments/configs/v3_acoes_novas/varredura.json"]
    r = subprocess.run(base + ["--processos", "4"], capture_output=True, cwd=RAIZ)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    r = subprocess.run(base + ["--processos", "5"], capture_output=True, cwd=RAIZ)
    assert r.returncode == 2 and "no máximo 4" in r.stderr.decode("utf-8")


def test_a_lista_de_processos_da_maquina_responde(monkeypatch):
    """Sem a lista falsa, o pre_run consegue listar os processos Python da máquina (este pytest entre eles)."""
    monkeypatch.delenv("DIGILAB_PRE_RUN_PROCESSOS", raising=False)
    linhas = pre_run.linhas_de_comando()
    assert any("pytest" in c for _, c in linhas)


# ------------------------------------------------------------------ E7: as medições do combate (seção 14 da tarefa; V3-D8)

MEDIR = "web/app/scripts/equilibrio_tr/medir_tudo.py"


def test_medicao_passa_sozinha_e_espera_outra_run(monkeypatch):
    assert pre_run.conferir_medicao(MEDIR) == []
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", json.dumps(["python experiments/run_v3_x.py --config c.json"]))
    m = pre_run.conferir_medicao("scripts/equilibrio_tr/fase2_formas.ts")
    assert len(m) == 1 and "outra run" in m[0]


def test_medicao_em_andamento_barra_a_run_de_pesquisa(repo, monkeypatch):
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", json.dumps([
        r"C:\Program Files\nodejs\node.exe C:\x\tsx\cli.mjs scripts/equilibrio_tr/fase4_progressao.ts --faixa calibracao2 --parte g1"]))
    m = motivos(repo, config(repo))
    assert len(m) == 1 and "outra run" in m[0] and "fase4_progressao" in m[0]


def test_medicao_da_luta_em_tempo_real(monkeypatch):
    """LUTA_POC LP5-0: a bancada nova (scripts/equilibrio_poc) tambem e medicao, e uma em andamento barra a outra."""
    assert pre_run.conferir_medicao("web/app/scripts/equilibrio_poc/medir_tudo.ts") == []
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", json.dumps(["node scripts/equilibrio_poc/bancada.ts --grupo formas"]))
    m = pre_run.conferir_medicao("scripts/equilibrio_poc/medir_tudo.ts")
    assert len(m) == 1 and "outra run" in m[0] and "bancada.ts" in m[0]


def test_script_que_nao_e_medicao():
    assert "não é uma medição" in pre_run.conferir_medicao("scripts/outra/coisa.ts")[0]


def test_medicao_pela_linha_de_comando(monkeypatch):
    monkeypatch.setenv("DIGILAB_PRE_RUN_PROCESSOS", "[]")
    r = subprocess.run([sys.executable, str(RAIZ / "tools" / "pre_run.py"), MEDIR, "--medicao"], capture_output=True, cwd=RAIZ)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    r = subprocess.run([sys.executable, str(RAIZ / "tools" / "pre_run.py"), "experiments/run_v3_x.py"], capture_output=True, cwd=RAIZ)
    assert r.returncode == 2 and "--config" in r.stderr.decode("utf-8")
