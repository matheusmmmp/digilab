# TAREFA V3 — INDICE_DESVIOS (2026-11-06)

Coordenador: a sessão Claude Code da INFRA_AGENTES. Worker: Claude Code (sessão própria). Worktree e branch: `v3-indice-desvios`. Status: EM ANDAMENTO (proposta PROPOSTO; o código espera o ok do Matheus).

Categoria: arquitetura. Origem: Claude Code, 2026-11-06: o índice de desvios conflita em todo PR; propor o índice gerado ou merge=union, sem perder o G-CONCAT.

## 1. Pergunta

Como tirar o conflito de merge do índice `docs/REGISTRO_DESVIOS.md`, que hoje aparece em todo PR que entra depois de outro, sem perder o
G-CONCAT (`tools/conferir_saude.py`, rodada de saúde, etapa 2: `docs/TAREFA_V2_SAUDE.md`)? É infraestrutura do trabalho em paralelo; não
vem de uma hipótese do plano de pesquisa.

**Status: PROPOSTO.** Este documento só propõe. Nenhum código muda antes do ok do Matheus (seção 8).

### 1.1 O problema, medido

- O índice tem 485 linhas (`origin/main` `93395f93`). Cada frente acrescenta uma no fim; os arquivos do mês (`docs/registro/AAAA-MM.md`)
  também crescem no fim, mas têm `merge=union` no `.gitattributes` desde 2026-10-14 e não conflitam.
- Metade dos merges da `main` é local (95 dos últimos 200, de "Matheus de Medeiros Pereira": o worker traz a `main` para o branch dele)
  e metade é o botão do GitHub (105). Nos merges locais o índice conflita e é resolvido à mão; os títulos dizem "registro na ordem"
  (por exemplo `377f1a40`, `035048d9`, `ada18071`, `6034cd70`). Em 2026-11-06 foram umas oito vezes só nos PRs da INFRA_AGENTES (#601 a #629).
- Resolver à mão já moveu seções de outras frentes por engano.

### 1.2 O que o G-CONCAT confere hoje (`conferir_registro`, `tools/conferir_saude.py`)

1. a concatenação dos arquivos do mês começa pelo registro do commit de base, byte a byte (sha256 em `docs/historico/registro_lotes.json`),
   e pela cópia da etapa 0;
2. **o índice lista as seções dos arquivos do mês, na ordem dos arquivos** (os meses em ordem, as seções na ordem em que estão no
   arquivo), sem seção datada e sem linha estranha;
3. cada seção está no arquivo do mês da data dela; nenhuma seção repetida; a pasta só tem `AAAA-MM.md`;
4. as seções dos lotes absorvidos são iguais às do commit do lote.

O ponto 2 é o único que olha o índice. E o índice é **função pura** dos arquivos do mês: `CABECALHO_INDICE` mais uma
`linha_indice(título)` por seção, na ordem de `arquivos_do_mes` × `partir` (as três já estão em `tools/registro_por_mes.py`). Nada no
índice é informação nova; ele é redundância conferida.

### 1.3 O `merge=union` no índice já foi tentado

Em 2026-10-14 o índice entrou no `merge=union` junto com os arquivos do mês (`1341c5bf`) e saiu no mesmo dia (`1df1afed`): "um PR no
formato antigo colou o registro inteiro no índice sem conflito; a conferência pegou". O comentário está no `.gitattributes`.

## 2. Depende de

Nada na `main` além do que já está lá. Depende das decisões D-ID1 a D-ID4 (seção 8).

## 3. Mudança mínima

### 3.1 As duas saídas

**(a) O índice gerado.** Uma ferramenta, `tools/gerar_indice_desvios.py`, escreve o índice a partir dos títulos `## ` dos arquivos do
mês (com as funções que já existem em `tools/registro_por_mes.py`); `--conferir` sai com 1 se o índice do disco não é o gerado. **O
worker para de editar o índice.** Quem regenera é o Matheus ou o coordenador, depois dos merges (D-ID2). Como o índice da `main` passa a
poder ficar atrás dos arquivos do mês entre uma regeneração e outra, o ponto 2 do G-CONCAT vira, no PR, "o índice é uma
subsequência, na ordem, das seções dos arquivos do mês, e toda linha dele tem a seção" (a falta das linhas novas vira aviso); a
igualdade inteira fica no `--conferir` (D-ID3). Os pontos 1, 3 e 4 não mudam.

**(b) `docs/REGISTRO_DESVIOS.md merge=union`** no `.gitattributes`, com o worker seguindo a regra de hoje (linha no fim do índice).

### 3.2 O que cada uma faz com a ordem (ensaio)

Ensaio num repositório de rascunho com os dois arquivos em `merge=union` (o script está no apêndice, seção 9; roda com `bash` numa pasta
de rascunho, fora do repositório). Os merges como os workers fazem hoje:

| caso | o que acontece | arquivo do mês | índice com union | G-CONCAT |
|---|---|---|---|---|
| T1: PR B sai da base, A entra na `main`, B traz a `main` (merge local) | union põe o "nosso" (B) antes do "deles" (A) nos dois | s0 B A | s0 B A | passa |
| T2: merge direto do PR na `main` | o mesmo, com os lados trocados | … C | … C | passa |
| T3: virada do mês: a `main` já tem uma seção de 2026-12; um PR aberto em novembro entra depois | a seção vai para o fim de `2026-11.md`, a linha vai para o fim do índice | … D E | … E D | **falha** |
| T4: um PR corrige o título de uma seção antiga nos dois arquivos | junta sem conflito | s0b … | s0b … | passa |

Leitura:
- **O union mantém a ordem do G-CONCAT enquanto os dois lados escrevem no mesmo mês** (T1, T2, T4): os dois arquivos conflitam no mesmo
  trecho e o union resolve os dois do mesmo jeito.
- **Na virada do mês ele quebra** (T3): o arquivo do mês não conflita (cada lado escreveu num arquivo), o índice conflita, e o union põe a
  linha de novembro depois da de dezembro. O G-CONCAT reprova e alguém reordena à mão: é o conflito de hoje, uma vez por mês por PR
  que atravessa a virada. Com o índice gerado, T3 sai certo sem ninguém tocar (a ordem vem dos arquivos).
- **O union não pega erro, só junta** (1.3): um PR que cole lixo no índice entra sem conflito. Hoje o G-CONCAT pega no CI do PR seguinte
  (o `ler_indice` falha com seção datada no índice), não no merge.
- Não conferido: se o botão de merge do GitHub aplica o `merge=union`. Nos merges locais o git aplica (ensaio acima); o botão só junta
  sem conflito, e um PR que conflite ali fica parado até o worker trazer a `main`, o que já é o caminho de hoje.

### 3.3 Recomendação: (a)

O índice é derivado; o que é derivado se gera, não se junta. A (a) tira o conflito de todos os casos (inclusive T3), deixa o G-CONCAT
com os pontos 1, 3 e 4 intactos e o ponto 2 conferido contra uma fonte só, e a resolução de qualquer bagunça vira um comando. A (b) é uma
linha no `.gitattributes`, mas devolve o risco que já fez o índice sair do union em 2026-10-14 e falha na virada do mês.

| | (a) gerado | (b) union |
|---|---|---|
| custo de fazer | ferramenta (~60 linhas, reusa `registro_por_mes`), testes, troca do ponto 2 do G-CONCAT, 4 textos de instrução | 1 linha no `.gitattributes` |
| conflito que sobra | nenhum no índice (só o Matheus/coordenador escreve nele) | na virada do mês (T3), e por PR que edite linhas antigas do índice |
| **custo de errar** | um bug no gerador escreve um índice errado; o `--conferir` e o ponto 2 do G-CONCAT apontam, e se conserta rodando de novo. Nenhum byte das seções está em jogo: o gerador só lê os arquivos do mês | um merge junta lixo ou ordem errada **sem conflito**; só o CI do PR seguinte pega, e alguém resolve à mão, que é o que move seções por engano |
| índice da `main` | pode ficar atrás até a regeneração (o `ESTADO_ATUAL` também fica, D-ID2) | sempre em dia |

Plano B dentro da (a), se o Matheus preferir o índice sempre em dia (D-ID2): o worker roda o gerador no próprio PR. O conflito volta a
aparecer, mas a resolução é `git checkout --theirs docs/REGISTRO_DESVIOS.md` e rodar o gerador de novo, sem decidir ordem à mão.

### 3.4 O que muda, se for (a)

- **Novo:** `tools/gerar_indice_desvios.py` (escreve o índice; `--conferir` só confere). Reusa `CABECALHO_INDICE`, `linha_indice`,
  `partir` e `arquivos_do_mes` de `tools/registro_por_mes.py`; nenhuma regra de formato duplicada.
- **Novo:** `tests/test_infra_indice_desvios.py` (entra sozinho no CI, que roda os `tests/test_infra_*.py`): o gerado é o índice da
  `main` de hoje byte a byte; os casos T1 e T3 da tabela; um índice atrasado passa no PR e falha no `--conferir`; uma linha sem seção falha.
- **Alterado:** `tools/conferir_saude.py`, o ponto 2 do G-CONCAT (subsequência no PR, igualdade no `--conferir`; D-ID3).
- **Alterado:** `tools/registro_por_mes.py`: o texto de `CABECALHO_INDICE` (a regra de onde escrever) e o `absorver`, que passa a
  regenerar o índice em vez de acrescentar a linha.
- **Alterado:** `tools/gerar_estado_atual.py` lê as últimas seções dos arquivos do mês, não do índice (senão o `ESTADO_ATUAL` herda o
  atraso do índice).
- **Alterado:** `.github/workflows/verificar-pr.yml`: um passo "Índice de desvios em dia (só aviso)", igual ao do `ESTADO_ATUAL`.
- **O que NÃO muda:** nenhum byte dos arquivos do mês, o `merge=union` deles, o `registro_lotes.json`, os pontos 1, 3 e 4 do G-CONCAT, o
  caminho `docs/REGISTRO_DESVIOS.md` (o código e os artefatos que o citam seguem achando). Nada em `digilab/`, `experiments/`, `web/app/`.

### 3.5 O que muda nas instruções dos workers

| arquivo | hoje | proposto |
|---|---|---|
| `docs/modelos/TAREFA_V3_MODELO.md`, seção 5 | "Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md` (rodada de saúde, etapa 2)." | "Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve rodando o gerador, nunca à mão." |
| `CLAUDE.md`, "Trabalho em paralelo" (só com o ok do Matheus, D-ID4) | "…e com uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`." | "…; o índice `docs/REGISTRO_DESVIOS.md` é gerado (`tools/gerar_indice_desvios.py`), e o worker não o edita." A linha da tabela "Onde está o quê" não muda. |
| `docs/V2_TRABALHO_PARALELO.md` (a regra do desvio, linha 57) | "…e uma linha no fim do índice…" | o mesmo texto do modelo |
| o próprio índice (`CABECALHO_INDICE`) | "Onde o worker escreve o desvio novo: 1. a seção…; 2. uma linha no fim deste índice…" | "1. a seção…, no fim do arquivo do mês. Este índice é gerado por `python tools/gerar_indice_desvios.py`; não o edite." |

O `docs/modelos/TAREFA_V2_MODELO.md` fica como está (a V2 está congelada); se o Matheus quiser, recebe o mesmo texto.

Se for (b): só o `.gitattributes` muda; as instruções seguem iguais, mais uma frase no modelo: "na virada do mês, se o G-CONCAT reprovar
a ordem do índice, ponha a linha da seção do mês anterior antes das do mês novo".

## 4. Experimento e gate (se houver run)

Sem run. O critério do código, depois do ok: `python tools/conferir_saude.py` passa na `main` de hoje com o índice gerado igual ao
atual, byte a byte, e os testes da seção 3.4 passam.

## 5. Entrega

- Esta etapa: este documento e o PR, na categoria arquitetura, com o relato no modelo de `.github/pull_request_template.md`.
- Sem seção no registro: a proposta não tem desvio, e uma seção nova no índice seria mais um conflito deste mesmo tipo.
- O código (seção 3.4) fica para depois do ok do Matheus, num PR seguinte.

## 6. Fora desta tarefa

- A ordem das seções dentro do arquivo do mês: o `merge=union` põe a seção do branch antes da que já estava na `main` (T1), então um
  merge local da `main` no branch muda a ordem da `main`. O G-CONCAT não exige ordem por data e nada se perde, mas o diff do PR mostra
  seções de outras frentes "movidas". Fica como questão aberta.
- Qualquer mudança nos textos das seções, no `registro_lotes.json` ou nos arquivos de `docs/historico/`.

## 7. Critérios de aceitação

- Este arquivo existe na `main` com o status PROPOSTO e as decisões D-ID1 a D-ID4.
- O PR passa no `tools/verificar_relato.py` (categoria arquitetura) e não muda nada em `digilab/`, `experiments/` ou `web/app/src/`.

## 8. Precisa do Matheus

- **D-ID1, qual saída.** Recomendação: (a), o índice gerado. Custo de errar: escolher (a) sem precisar custa uma ferramenta pequena e a
  regeneração depois dos merges; escolher (b) e errar devolve o merge que junta lixo sem conflito (o de 2026-10-14) e deixa o conflito da
  virada do mês.
- **D-ID2, quem regenera e quando.** Recomendação: quem faz o merge (o Matheus, ou o coordenador num PR só do índice), depois de cada
  leva de merges; o CI avisa quando o índice está atrás. Custo de errar: o índice da `main` fica algumas seções atrás por um tempo (as
  seções estão inteiras nos arquivos do mês). A alternativa é o worker regenerar no PR (plano B da 3.3), com o conflito resolvido por
  comando.
- **D-ID3, o ponto 2 do G-CONCAT no PR.** Recomendação: aceitar o índice atrasado (subsequência na ordem, toda linha com a seção) e
  manter a igualdade no `--conferir`. Custo de errar: uma seção pode ficar sem linha no índice até a regeneração; nenhuma linha errada ou
  fora de ordem passa.
- **D-ID4, as duas frases do `CLAUDE.md`.** Recomendação: trocar a regra do desvio na seção "Trabalho em paralelo" pelo texto da 3.5,
  no mesmo PR do código. Custo de errar: se o `CLAUDE.md` não mudar, o worker segue a regra antiga e volta a editar o índice.

## 9. Apêndice: o ensaio do `merge=union`

`bash ensaio.sh <pasta de rascunho>` cria um repositório novo em `<pasta>/repo_union` e imprime a ordem do arquivo do mês e do índice
em cada caso. Saída em 2026-11-06 (git do Windows): a tabela da seção 3.2.

```bash
set -e
R="$1/repo_union"; rm -rf "$R"; mkdir -p "$R/docs/registro"; cd "$R"; git init -q; git config user.email t@t; git config user.name t; git config core.autocrlf false
printf 'docs/registro/*.md merge=union\ndocs/REGISTRO_DESVIOS.md merge=union\n' > .gitattributes
printf '## 2026-11-01 — BASE: s0\ntexto 0\n\n' > docs/registro/2026-11.md
printf '# Indice\n\n## Índice\n\n- [2026-11-01 — BASE: s0](registro/2026-11.md)\n' > docs/REGISTRO_DESVIOS.md
git add -A; git commit -qm base; git branch -M main
add(){ printf "## $1 — $2\ntexto $2\n\n" >> docs/registro/$3.md; printf -- "- [$1 — $2](registro/$3.md)\n" >> docs/REGISTRO_DESVIOS.md; git add -A; git commit -qm "$2"; }
ordem(){ echo "  arquivo: $(grep -h '^## ' docs/registro/*.md | sed 's/.*— //' | tr '\n' ' ')"; echo "  índice : $(grep '^- ' docs/REGISTRO_DESVIOS.md | sed 's/.*— //;s/\].*//' | tr '\n' ' ')"; }
echo "T1: PR-B sai da base, A entra na main; B faz merge da main (local, como os workers)"
git checkout -qb B; add 2026-11-05 B 2026-11; git checkout -q main; add 2026-11-04 A 2026-11
git checkout -q B; git merge -q --no-edit main; ordem; git checkout -q main; git merge -q --no-edit B; echo " main depois do PR B:"; ordem
echo "T2: o mesmo, mas o merge direto do PR na main (main=ours)"
git checkout -qb C main~2 2>/dev/null || git checkout -qb C HEAD~3; add 2026-11-06 C 2026-11; git checkout -q main; git merge -q --no-edit C; ordem
echo "T3: virada do mês: main já tem 2026-12; PR D (aberto em novembro) entra depois"
git checkout -qb D; add 2026-11-30 D 2026-11; git checkout -q main; add 2026-12-01 E 2026-12; git merge -q --no-edit D; ordem
echo "T4: PR F corrige um título existente (s0 -> s0b) nos dois arquivos; main acrescenta G"
git checkout -qb F; sed -i 's/BASE: s0/BASE: s0b/' docs/registro/2026-11.md docs/REGISTRO_DESVIOS.md; git commit -qam F; git checkout -q main; add 2026-12-02 G 2026-12; git merge -q --no-edit F; ordem
```
