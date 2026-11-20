"""O gerador do índice de desvios (tools/gerar_indice_desvios.py; docs/TAREFA_V3_INDICE_DESVIOS.md, D-ID1 a D-ID4).

O índice é função dos arquivos do mês: a ordem dos meses e, dentro do mês, a do arquivo. O G-CONCAT com o índice atrasado, fora de ordem
e na virada do mês fica em tests/test_conferir_saude.py, que já monta o registro de verdade num diretório à parte.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import gerar_indice_desvios as gid  # noqa: E402
import registro_por_mes as rpm  # noqa: E402


def _meses(tmp: Path, meses: dict[str, list[str]]) -> Path:
    for m, titulos in meses.items():
        rpm.escrever(tmp / rpm.PASTA / f"{m}.md", "\n".join(f"## {t}\n\ntexto de {t[-1]}\n" for t in titulos))
    return tmp


def test_a_ordem_e_a_dos_arquivos_nao_a_das_datas(tmp_path):
    # T1 da tarefa: o merge=union pôs B (dia 5) antes de A (dia 4); o índice segue o arquivo
    raiz = _meses(tmp_path, {"2026-12": ["2026-12-01 — E"], "2026-11": ["2026-11-05 — B", "2026-11-04 — A"]})
    assert [t for t, _ in gid.entradas(raiz)] == ["2026-11-05 — B", "2026-11-04 — A", "2026-12-01 — E"]
    assert gid.entradas(raiz)[2][1] == "docs/registro/2026-12.md"
    texto = gid.gerar(raiz)
    assert texto.startswith(rpm.CABECALHO_INDICE)
    assert texto[len(rpm.CABECALHO_INDICE):] == ("- [2026-11-05 — B](registro/2026-11.md)\n- [2026-11-04 — A](registro/2026-11.md)\n"
                                                  "- [2026-12-01 — E](registro/2026-12.md)\n")
    assert rpm.ler_indice(texto) == gid.entradas(raiz)


def test_escreve_confere_e_so_le_os_arquivos_do_mes(tmp_path):
    raiz = _meses(tmp_path, {"2026-11": ["2026-11-01 — A"]})
    mes = rpm.ler(raiz / rpm.PASTA / "2026-11.md")
    assert gid.principal(["--raiz", str(raiz), "--conferir"]) == 1          # sem índice
    assert gid.principal(["--raiz", str(raiz)]) == 0
    assert gid.principal(["--raiz", str(raiz), "--conferir"]) == 0
    assert gid.principal(["--raiz", str(raiz)]) == 0 and gid.principal(["--raiz", str(raiz), "--conferir"]) == 0  # idempotente
    assert rpm.ler(raiz / rpm.PASTA / "2026-11.md") == mes
    rpm.escrever(raiz / rpm.PASTA / "2026-11.md", mes + "\n## 2026-11-02 — B\n\ntexto\n")
    assert gid.atrasadas(raiz) == ["2026-11-02 — B"]
    assert gid.principal(["--raiz", str(raiz), "--conferir"]) == 1


def test_uma_linha_em_branco_a_mais_nao_e_o_gerado(tmp_path):
    raiz = _meses(tmp_path, {"2026-11": ["2026-11-01 — A", "2026-11-02 — B"]})
    gid.principal(["--raiz", str(raiz)])
    destino = raiz / rpm.REGISTRO
    rpm.escrever(destino, rpm.ler(destino).replace("\n- [2026-11-02", "\n\n- [2026-11-02"))
    assert gid.atrasadas(raiz) == [] and gid.principal(["--raiz", str(raiz), "--conferir"]) == 1


def test_falha_alto_sem_arquivo_do_mes_ou_com_secao_sem_data(tmp_path):
    with pytest.raises(ValueError, match="não tem arquivo"):
        gid.gerar(tmp_path)
    rpm.escrever(tmp_path / rpm.PASTA / "2026-11.md", "## sem data\n\ntexto\n")
    with pytest.raises(ValueError, match="sem data"):
        gid.gerar(tmp_path)


def test_o_repositorio_gera_as_mesmas_entradas_do_indice_na_ordem():
    # o índice da main pode estar atrasado (D-ID3), mas o que ele lista está no gerado, na mesma ordem
    listadas = rpm.ler_indice(rpm.ler(RAIZ / rpm.REGISTRO))
    geradas = gid.entradas(RAIZ)
    assert len(geradas) >= len(listadas) >= 486
    assert [e for e in geradas if e in set(listadas)] == listadas
