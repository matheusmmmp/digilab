# TAREFA V3 — LITERATURA, a missão C0 (2026-10-30)

Coordenador: o Gerente da V3 (sessão do Claude Code que abriu a trilha C). Worker: Claude Code (Opus 5.5). Worktree e branch:
`v3-literatura-c0`, criada de `origin/main` em `b3643bb`. Status: ENTREGUE.

Categoria: literatura. Origem: Matheus, 2026-10-30: a V3-D6 do `docs/PLANO_V3.md` põe a C0 antes de tudo na trilha C, porque a C1, a C2
e a C4 vão citar fontes da triagem de literatura de 2026-10-30, e nada se cita sem verificação.

## 1. Pergunta

Quais das fontes que a triagem de 2026-10-30 aponta para a trilha C (`docs/PLANO_V3.md`, seção 2.1) existem como registradas, e o que
cada uma autoriza afirmar? É o nó C0 da trilha C, a partir da recomendação R6 da triagem.

## 2. Depende de

Nada. O CI só aceita uma `TAREFA_V3_*` depois do merge do PR de infraestrutura do prefixo V3 (branch `v3-infra-prefixo`, V3-D1); o PR
desta tarefa só abre depois disso.

## 3. Mudança mínima

Só `docs/`:
- `docs/referencias/v3c0_referencias_verificadas.csv`, `v3c0_verificacao_crossref.json` e `v3c0_referencias.bib`: a verificação, no
  formato das tabelas que já existem;
- `docs/referencias/V3C0_SINTESE_TRIAGEM_2026-10-30.md`: a síntese da triagem (conclusões, L1–L11, R1–R7, a busca da R6), sem PDFs e
  sem texto copiado dos artigos;
- `docs/referencias/v3c0_buscas_r6.json`: o registro das quatro buscas da R6;
- `docs/referencias/REGRAS_CITACAO_DIGILAB.md` (a regra 9) e `docs/referencias/revisao_alife_linhagem.md` (a afirmação sem suporte 9):
  a alegação proibida nova da seção 2.2 do plano;
- este arquivo, o registro do mês e o índice.

Não muda: código, testes, configs, runs. A skill `literatura-digilab` fica fora do repositório; o texto proposto para ela vai no corpo do
PR, e o Matheus decide.

## 4. Experimento e gate (se houver run)

Não há run. As buscas da R6 são consultas a APIs públicas (OpenAlex, Semantic Scholar, arXiv), registradas com a data e as contagens.

## 5. Entrega

- Testes: nenhum código muda; `python tools/conferir_saude.py` antes do commit.
- Registro: a seção no fim de `docs/registro/2026-10.md` e a linha no fim de `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main`, com a seção Literatura; `python tools/verificar_relato.py --arquivo <corpo> --base origin/main` antes. Merge só
  pelo Matheus.

## 6. Fora desta tarefa

- Ler os artigos publicados no lugar das versões-irmãs (Gadanho 2001 e Ho 2008 continuam lidos pela tese).
- Verificar as pistas novas que a busca da R6 trouxe (ficam como SEM FONTE na síntese, seção 5).
- Zamin, Rity, Fujita, Lim, PEPA, Burke e Blumberg, o Cobot: citados pela triagem, não pedidos aqui; continuam SEM FONTE.
- Editar a skill `literatura-digilab`.
- Rever a `docs/ESPEC_DIGIBRAIN_MODULAR.md` (o fim da trilha C).

## 7. Critérios de aceitação

- Cada fonte da seção 2.1 do plano tem uma linha em `docs/referencias/v3c0_referencias_verificadas.csv`, com status do vocabulário do
  projeto e a ressalva de leitura em `o_que_sustenta`; todo DOI da tabela está em `v3c0_verificacao_crossref.json` com o status da API.
- A síntese cita só fontes dessa tabela ou das tabelas antigas; o resto aparece como pista, SEM FONTE.
- `REGRAS_CITACAO_DIGILAB.md` tem a regra 9, e a seção "Afirmações sem suporte" da revisão tem o item 9.
- `v3c0_buscas_r6.json` tem as quatro strings, as três bases e as contagens que a síntese cita.
- `python tools/conferir_saude.py` passa; o corpo do PR passa em `tools/verificar_relato.py`.

## 8. Precisa do Matheus

- **O texto da regra para a skill `literatura-digilab`** (no corpo do PR). Recomendação: acrescentar como regra 9, igual à do
  repositório. Custo de errar: a skill sem a regra deixa uma sessão futura escrever a alegação proibida, e o CI do repositório não confere
  texto fora dele.
- **A tese de Ho com DOI do DataCite (`10.18745/th.14271`) marcada VERIFICADA.** O vocabulário diz "DOI resolve no Crossref (ou API do
  arXiv)"; aqui o DOI resolve no DataCite. Recomendação: aceitar, como já se aceita o arXiv. Custo de errar: baixo, o registro está na
  API do DataCite e no repositório da universidade.

## 9. O resultado da etapa (2026-10-30)

- **22 linhas na tabela:** 21 VERIFICADAS (4 delas sem DOI) e 1 NÃO LOCALIZADA (o DOI da reimpressão de 2011 do PEPE dá 404; cita-se o
  capítulo de 2009). Nenhuma com `update-to` nem `updated-by`.
- **Das fontes pedidas, todas confirmadas.** Entraram também o IVA 2003 de Ho (o primeiro artigo da linha, achado na mesma busca) e o
  IAS-8 2004, e os dois artigos de Yoon de 2000 (AGENTS e AAAI), porque a triagem leu os dois.
- **Duas leituras continuam por versão-irmã:** Gadanho e Hallam 2001 (pela tese de 1999) e Ho 2008 (pela tese de 2005). O AISB 2006 de
  Ho tem só a existência confirmada e entra como cinza (o repositório o marca como não arbitrado).
- **A busca da R6** confirma a lacuna: "autobiographic agent" traz a linha de Ho inteira no topo. Os achados novos ficam como pistas na
  síntese, seção 5.
