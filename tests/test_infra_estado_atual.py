"""O índice derivado (tools/gerar_estado_atual.py): só copia o que as fontes declaram, e regenerar sem mudança dá o mesmo arquivo."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import gerar_estado_atual as ge  # noqa: E402


def fontes(tmp: Path) -> Path:
    d = tmp / "docs"
    d.mkdir()
    (d / "PAINEL_V2.md").write_text("# Painel\n\n**Atualizado em 2026-10-13** (`main` `ec09483`).\n", encoding="utf-8")
    (d / "TAREFA_V2_A.md").write_text("# TAREFA V2 — A\n\nWorker: x. Status: **ABERTA.** Mais texto.\n", encoding="utf-8")
    (d / "TAREFA_V2_B.md").write_text("# TAREFA V2 — B\n\nsem linha de status\n", encoding="utf-8")
    (d / "PLANO_ANALISE_V2_A.md").write_text("# Plano A\n", encoding="utf-8")
    (d / "RESULTADO_V2_A.md").write_text("# Resultado A\n\nPlano: `docs/PLANO_ANALISE_V2_A.md`. Tarefa: `docs/TAREFA_V2_A.md`.\n",
                                         encoding="utf-8")
    (d / "REGISTRO_DESVIOS.md").write_text("# Registro\n\n## Índice\n\n" + "".join(f"- [2026-10-{i:02d} — R{i}](registro/2026-10.md)\n"
                                                                                for i in range(1, 13)), encoding="utf-8")
    return tmp


def test_copia_o_declarado_e_cita_a_fonte(tmp_path):
    texto = ge.gerar(fontes(tmp_path))
    assert "atualizado em 2026-10-13 (`main` `ec09483`). É o coordenador" in texto
    assert "| [TAREFA_V2_A](TAREFA_V2_A.md) | TAREFA V2 — A | ABERTA | [RESULTADO_V2_A](RESULTADO_V2_A.md) |" in texto
    assert "| [TAREFA_V2_B](TAREFA_V2_B.md) | TAREFA V2 — B | sem status declarado | nenhum |" in texto
    assert "| [PLANO_ANALISE_V2_A](PLANO_ANALISE_V2_A.md) | Plano A | [RESULTADO_V2_A](RESULTADO_V2_A.md) |" in texto
    assert "Não é fonte de verdade" in texto


def test_so_os_ultimos_registros(tmp_path):
    texto = ge.gerar(fontes(tmp_path))
    assert "R12" in texto and "R3]" in texto and "R2]" not in texto and "(12 entradas)" in texto


def test_conferir(tmp_path):
    raiz = fontes(tmp_path)
    assert ge.principal(["--raiz", str(raiz), "--conferir"]) == 1
    assert ge.principal(["--raiz", str(raiz)]) == 0
    assert ge.principal(["--raiz", str(raiz), "--conferir"]) == 0
    (raiz / "docs" / "TAREFA_V2_C.md").write_text("# C\n", encoding="utf-8")
    assert ge.principal(["--raiz", str(raiz), "--conferir"]) == 1


def test_o_repositorio_gera_sem_erro():
    texto = ge.gerar(RAIZ)
    assert "TAREFA_V2_SAUDE" in texto


def test_lista_tambem_os_arquivos_v3(tmp_path):
    raiz = fontes(tmp_path)
    d = raiz / "docs"
    (d / "TAREFA_V3_Z.md").write_text("# TAREFA V3 — Z\n\nStatus: ABERTA.\n", encoding="utf-8")
    (d / "PLANO_ANALISE_V3_Z.md").write_text("# Plano Z\n", encoding="utf-8")
    texto = ge.gerar(raiz)
    assert "| [TAREFA_V3_Z](TAREFA_V3_Z.md) | TAREFA V3 — Z | ABERTA | nenhum |" in texto
    assert "| [PLANO_ANALISE_V3_Z](PLANO_ANALISE_V3_Z.md) | Plano Z | nenhum |" in texto


def test_sem_arquivo_v3_os_titulos_ficam_como_eram(tmp_path):
    texto = ge.gerar(fontes(tmp_path))
    assert "## 1. Tarefas (`docs/TAREFA_V2_*.md`)" + "\n" in texto and "V3" not in texto
