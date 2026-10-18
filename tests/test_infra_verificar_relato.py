"""O verificador do relato de volta (tools/verificar_relato.py): cada categoria com o caso que passa e o que reprova, e a separação entre
o que o agente declara e o que a ferramenta confere."""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import verificar_relato as vr  # noqa: E402

DOI_BOM = "10.1162/artl_a_00319"
DOI_RUIM = "10.1234/nao.verificado"


def corpo(categoria: str, extra: str = "", evidencias: str = "- Testes rodados: nenhum, só documentação.", decisoes: str = "nenhuma",
          tarefa: str = "`docs/TAREFA_V2_X.md`") -> str:
    return f"""Tarefa: {tarefa}
Categoria: {categoria}
Executor: Claude Code (sessão de teste)
Branch: `v2-x`. Commit base: `abc1234`

<!-- comentário do modelo, que some -->

## O que é

Uma mudança pequena.

## Arquivos

- **Novo:** `docs/x.md`.

## Evidências declaradas

{evidencias}

## Desvios

nenhum

## Decisões do Matheus

{decisoes}

## Questões abertas

nenhuma

## Próximos passos

nenhum
{extra}"""


def raiz_minima(tmp: Path) -> Path:
    (tmp / "docs" / "referencias").mkdir(parents=True)
    (tmp / "tests").mkdir()
    (tmp / "docs" / "TAREFA_V2_X.md").write_text("# TAREFA V2 — X\n", encoding="utf-8")
    (tmp / "docs" / "referencias" / "v9_referencias_verificadas.csv").write_text(
        f"referencia,verificada,doi_ou_id\nLehman 2020,VERIFICADA,{DOI_BOM}\nOutro,NÃO VERIFICADA,{DOI_RUIM}\n", encoding="utf-8")
    (tmp / "docs" / "referencias" / "v9_referencias.bib").write_text(f"@article{{x, doi = {{{DOI_RUIM}}}}}\n", encoding="utf-8")
    return tmp


def falhas(itens):
    return [i for i in itens if not i.ok and not i.alerta]


def test_o_template_do_repo_sem_preencher_reprova():
    modelo = (RAIZ / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
    itens = vr.verificar(modelo, [], RAIZ)
    assert falhas(itens)
    assert any(i.regra == "categoria válida" for i in falhas(itens))


def test_campo_faltando_reprova(tmp_path):
    raiz = raiz_minima(tmp_path)
    c = corpo("documentacao").replace("Executor: Claude Code (sessão de teste)\n", "")
    assert [i.regra for i in falhas(vr.verificar(c, ["docs/x.md"], raiz))] == ["campo Executor"]


def test_placeholder_do_modelo_conta_como_vazio(tmp_path):
    raiz = raiz_minima(tmp_path)
    c = corpo("documentacao", decisoes="<Cada uma com a recomendação e o custo de errar, ou \"nenhuma\".>")
    assert [i.regra for i in falhas(vr.verificar(c, [], raiz))] == ["seção Decisões do Matheus"]


def test_sinal_de_menor_e_maior_dentro_de_codigo_nao_e_placeholder(tmp_path):
    """Achado da INFRA-POC (#331): um comando citado com argumento genérico não pode virar seção vazia."""
    raiz = raiz_minima(tmp_path)
    c = corpo("documentacao", decisoes="nenhuma; o guia cita `python tools/verificar_relato.py --pr <N>`\n\n```bash\nx --arquivo <corpo.md>\n```")
    assert falhas(vr.verificar(c, [], raiz)) == []


def test_tarefa_que_nao_existe_reprova(tmp_path):
    raiz = raiz_minima(tmp_path)
    c = corpo("documentacao", tarefa="`docs/TAREFA_V2_NAO_HA.md`")
    assert [i.regra for i in falhas(vr.verificar(c, [], raiz))] == ["a tarefa existe"]


def test_documentacao_passa_com_links_bons_e_reprova_com_link_quebrado(tmp_path):
    raiz = raiz_minima(tmp_path)
    (raiz / "docs" / "x.md").write_text("[ok](TAREFA_V2_X.md) [fora](https://x.org) [ancora](#a)\n", encoding="utf-8")
    assert falhas(vr.verificar(corpo("documentacao"), ["docs/x.md"], raiz)) == []
    (raiz / "docs" / "x.md").write_text("[quebrado](NAO_HA.md)\n", encoding="utf-8")
    assert [i.regra for i in falhas(vr.verificar(corpo("documentacao"), ["docs/x.md"], raiz))] == ["os links resolvem"]


def test_documentacao_reprova_se_codigo_mudou(tmp_path):
    raiz = raiz_minima(tmp_path)
    assert [i.regra for i in falhas(vr.verificar(corpo("documentacao"), ["digilab/x.py"], raiz))] == ["só documentos mudaram"]


def test_implementacao_exige_teste(tmp_path):
    raiz = raiz_minima(tmp_path)
    assert [i.regra for i in falhas(vr.verificar(corpo("implementacao"), ["tools/x.py"], raiz))] == ["há teste no PR"]
    assert falhas(vr.verificar(corpo("implementacao"), ["tools/x.py", "tests/test_x.py"], raiz)) == []


def test_implementacao_teste_citado_que_nao_existe_reprova(tmp_path):
    raiz = raiz_minima(tmp_path)
    c = corpo("implementacao", evidencias="- Testes rodados: `python -m pytest tests/test_nao_ha.py -q` → 3 passed.")
    assert [i.regra for i in falhas(vr.verificar(c, ["tools/x.py"], raiz))] == ["o teste citado existe"]


def test_saida_de_teste_colada_e_so_declarada(tmp_path):
    """Uma saída de teste colada no corpo não vira prova: sai como alerta DECLARADA e não satisfaz a regra da categoria."""
    raiz = raiz_minima(tmp_path)
    c = corpo("implementacao", evidencias="- Testes rodados: todos os testes passam.\n```\n12 passed in 3.1s\n```")
    itens = vr.verificar(c, ["tools/x.py"], raiz)
    alertas = [i for i in itens if i.alerta]
    assert alertas and all(i.coluna == "DECLARADA" for i in alertas)
    assert [i.regra for i in falhas(itens)] == ["há teste no PR"]


def literatura(origem="Claude Science, 2026-10-18, revisão do P7", dois=DOI_BOM, limitacoes="só metadados e resumo"):
    return f"""
## Literatura

Origem: {origem}
DOIs: {dois}
Resultados: a síntese em `docs/referencias/X_SINTESE.md`.
Limitações: {limitacoes}
"""


def test_literatura_passa_com_doi_verificado(tmp_path):
    raiz = raiz_minima(tmp_path)
    assert falhas(vr.verificar(corpo("literatura", literatura()), ["docs/referencias/X_SINTESE.md"], raiz)) == []


def test_literatura_doi_fora_da_tabela_reprova(tmp_path):
    raiz = raiz_minima(tmp_path)
    itens = vr.verificar(corpo("literatura", literatura(dois="10.9999/inventado.1")), [], raiz)
    assert [i.regra for i in falhas(itens)] == ["o DOI está em docs/referencias"]


def test_literatura_sem_limitacoes_e_com_codigo_reprova(tmp_path):
    raiz = raiz_minima(tmp_path)
    itens = vr.verificar(corpo("literatura", literatura(limitacoes="")), ["digilab/x.py"], raiz)
    assert sorted(i.regra for i in falhas(itens)) == ["literatura: Limitações", "só docs/ mudou"]


def test_literatura_doi_marcado_nao_verificado_reprova_mesmo_no_bib(tmp_path):
    raiz = raiz_minima(tmp_path)
    itens = vr.verificar(corpo("literatura", literatura(dois=DOI_RUIM)), [], raiz)
    assert [i.regra for i in falhas(itens)] == ["o DOI está em docs/referencias"]
    assert "NÃO VERIFICADA" in falhas(itens)[0].detalhe


def test_os_dois_do_repo_sao_lidos():
    """O Lehman 2020 foi conferido depois da revisão: está no .bib e não na tabela (skill literatura-digilab)."""
    conhecidos = vr.dois_conhecidos(RAIZ)
    assert conhecidos[DOI_BOM][0] and conhecidos[DOI_BOM][1] == "referencias.bib"
    assert any(fonte.endswith(": VERIFICADA") for _, fonte in conhecidos.values())  # o status da tabela é lido


def test_arquitetura(tmp_path):
    raiz = raiz_minima(tmp_path)
    bom = corpo("arquitetura", "\nStatus: PROPOSTO.\n", decisoes="- **D-1:** recomendo A; errar custa uma rodada.")
    assert falhas(vr.verificar(bom, ["docs/x.md"], raiz)) == []
    sem_decisao = corpo("arquitetura", "\nStatus: PROPOSTO.\n", decisoes="nenhuma")
    assert [i.regra for i in falhas(vr.verificar(sem_decisao, [], raiz))] == ["decisões do Matheus listadas"]
    com_codigo = vr.verificar(bom, ["experiments/run_x.py"], raiz)
    assert [i.regra for i in falhas(com_codigo)] == ["nenhum código mudou"]


def _git(raiz: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(raiz), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True)


def _repo_experimento(tmp: Path, plano_primeiro: bool) -> Path:
    raiz = raiz_minima(tmp)
    _git(raiz, "init", "-q")
    plano = raiz / "docs" / "PLANO_ANALISE_V2_X.md"
    artefato = raiz / "artifacts_v2_x" / "metrics.json"
    artefato.parent.mkdir()
    ordem = [(plano, "# plano\n"), (artefato, "{}\n")] if plano_primeiro else [(artefato, "{}\n"), (plano, "# plano\n")]
    for arq, texto in ordem:
        arq.write_text(texto, encoding="utf-8")
        _git(raiz, "add", "-A")
        _git(raiz, "commit", "-q", "-m", arq.name)
    return raiz


EXP = "\nPlano: `docs/PLANO_ANALISE_V2_X.md`. Número: 0,31 em `artifacts_v2_x/metrics.json`.\n"


def test_experimento_plano_antes_do_artefato_passa(tmp_path):
    raiz = _repo_experimento(tmp_path, plano_primeiro=True)
    assert falhas(vr.verificar(corpo("experimento", EXP), ["artifacts_v2_x/metrics.json"], raiz)) == []


def test_experimento_plano_depois_do_artefato_reprova(tmp_path):
    raiz = _repo_experimento(tmp_path, plano_primeiro=False)
    itens = vr.verificar(corpo("experimento", EXP), ["artifacts_v2_x/metrics.json"], raiz)
    assert [i.regra for i in falhas(itens)] == ["plano commitado antes do artefato"]


def test_experimento_artefato_citado_que_nao_existe_reprova(tmp_path):
    raiz = _repo_experimento(tmp_path, plano_primeiro=True)
    c = corpo("experimento", EXP + "Outro: `artifacts_v2_x/nao_ha.json`.\n")
    assert [i.regra for i in falhas(vr.verificar(c, [], raiz))] == ["o artefato citado existe"]


def test_saida_do_pytest_colada_vira_alerta(tmp_path):
    raiz = raiz_minima(tmp_path)
    c = corpo("implementacao", evidencias="- `python -m pytest tests/test_x.py -q` → 53 passed.")
    (raiz / "tests" / "test_x.py").write_text("", encoding="utf-8")
    itens = vr.verificar(c, ["tests/test_x.py"], raiz)
    assert falhas(itens) == [] and [i.coluna for i in itens if i.alerta] == ["DECLARADA"]


def test_tabela_separa_declarada_de_verificada(tmp_path):
    raiz = raiz_minima(tmp_path)
    saida = vr.tabela(vr.verificar(corpo("documentacao"), [], raiz))
    assert "| DECLARADA |" in saida and "| VERIFICADA |" in saida and "não é prova" in saida
