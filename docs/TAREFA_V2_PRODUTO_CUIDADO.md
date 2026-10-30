# TAREFA V2 — PRODUTO-CUIDADO (2026-10-30)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Gerente (Claude Code). Worker: A (Claude Code, Opus 5.5). Worktree e branch: `v2-produto-cuidado`. Status: ENTREGUE.

Categoria: implementacao. Origem: o seguimento do PR #450 (`docs/TAREFA_V2_PRODUTO_FOME.md`), pedido pelo Gerente e autorizado pelo
Matheus em 2026-10-29: a comida passa a contar no cuidado do bebê, e os chamados de higiene e de carinho passam a seguir o corpo, como
o de fome.

## 1. Pergunta

Com o chamado de fome pela fome do corpo (o #450, limiar 0,45), o bebê quase não chama mais por fome. O cuidado da evolução fica só na
higiene e no carinho, que seguem pelo relógio, e um dono que nunca alimenta cria um bebê sereno. Como fazer a comida contar, e os outros
dois chamados seguirem o corpo? Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é um conserto do produto jogável.

## 2. Depende de

O PR #450 na `main` (31e3d7e).

## 3. Mudança mínima

- **O achado que parou o código** (a seção 8): no bebê v13, o corpo quase não precisa de cuidado no estágio. Com limiares parecidos com o
  0,45, os chamados pelo corpo quase não abrem, e sem chamados o cuidado dá 1: até o bebê de quem não faz nada sairia sereno.
- **A opção (C), a escolhida pelo Matheus em 2026-10-30:**
  - os três chamados do bebê abrem pelo corpo, com limiares do bebê, relativos à faixa do corpo dele: a fome abaixo de 0,7, a higiene
    abaixo de 0,9 e o humor abaixo de 0,8, este no chamado de carinho. Os três são PROPOSTOS, SEM FONTE;
  - os intervalos de 30/60/45 min e a janela de 15 ficam como hoje;
  - o alimentar ou a ração posta atendem o chamado de fome.
- **As fronteiras:** uma chave nova, que chega pelo evento `"p"` só nos ovos novos. Os saves de antes ficam iguais, e o corpo, o cérebro e
  o Python não mudam.

## 4. Experimento e gate (se houver run)

Nenhuma run. A medição do efeito no bebê é de testes, nas sementes 101, 202 e 303.

## 5. Entrega

- **A medição:** o efeito com os mesmos seis donos do #450. Quem não faz nada deve sair arisco, e quem atende tudo, sereno.
- **O relato:** no PR, com tipos, vitest, e2e, `conferir_saude` e `verificar_relato`.
- **O desvio:** no bebê, o 0,7 toma o lugar do 0,45.

## 6. Fora desta tarefa

- O corpo do bebê, o instinto e o cérebro (o 0,45 do `fome_moderada`).
- O `digilab/evolucao.py`: é o cronograma da pesquisa, e fica como está.
- O `test_arvore_fala`, que falha na `main` desde o R2b: é da frente do COMBATE-TR.

## 7. Critérios de aceitação

- `web/app/test/produto_cuidado.test.ts` passa. `web/app/test/produto_fome.test.ts` também, e com ele o `test/efeito_chamado_fome.json`
  igual byte a byte.
- O gabarito das vidas v13 (`test/vidas_v13.test.ts`) passa sem mudar.
- Nada muda no Python, no corpo nem no cérebro.

## 8. Precisa do Matheus

- **A opção (C): DECIDIDA** (Matheus, 2026-10-30, pelo Gerente). Os três limiares (0,7, 0,9 e 0,8) são PROPOSTOS.
- **O achado que levou à escolha** (medido na sessão, sementes 101 e 202, com as chaves do #450):

  | no bebê sem cuidado | rápido (180 min) | clássico (360 min) |
  |---|---|---|
  | fome | 0,80 → 0,65 | 0,80 → 0,50 |
  | higiene | 1 → 0,88 | 1 → 0,76 |
  | sujeira | 0 | 0 |
  | humor | 0,68–0,78 no começo, sobe sozinho a ~0,97 | igual |

- **A ração que o bebê não come:** um achado novo, com uma pergunta para o Matheus (seção 9).

## 9. Resumo da entrega (worker A, 2026-10-30)

- **A chave:** `chamadosPeloCorpo`, a terceira chave do evento `"p"` (`ChavesProduto`, `motor/tipos.ts`).
  - O jogo a grava ligada nos ovos novos (`src/produto.ts`, `CHAMADOS_PELO_CORPO`).
  - O evento das duas chaves de 2026-10-29 (os ovos do #450) segue válido e a deixa desligada. Os saves sem o evento seguem com as três
    desligadas.
- **Os chamados pelo corpo** (`Motor._chamadoCorpo`, com os limiares em `CHAMADO_BEBE_CORPO`, `motor/constantes.ts`):
  - **abrem** quando a variável do corpo fica abaixo do limiar do bebê (a fome, a higiene e o humor), no máximo um a cada intervalo
    (30, 60 e 45 min), e não pelo relógio;
  - **fecham como atendidos** com a ação do dono, como hoje: o alimentar ou a ração posta no de fome, o limpar no de higiene, o carinho
    ou o brincar no de carinho. O de fome fecha também quando a fome volta ao limiar, como no #450;
  - **fecham como perdidos** quando a janela de 15 min passa, como hoje. O humor sobe sozinho, mas isso não fecha o chamado de carinho;
  - **no bebê, o 0,7 da fome toma o lugar do 0,45** do #450. O chamado de fome só existe no bebê, então com a chave o 0,45 deixa de valer.
- **O código:** o `_chamadoFome` do #450 virou o caso da fome de `_chamadoCorpo`, e o intervalo de cada tipo fica em `ultimoChamado`.
  Com as duas chaves de 2026-10-29, a vida sai igual: o `test/efeito_chamado_fome.json` foi regravado e saiu idêntico, byte a byte.
- **A chave só mexe nos chamados:** o estado, o mundo e o cérebro saem iguais aos de sem ela (`test/produto_cuidado.test.ts`).
- **O efeito no bebê** (`web/app/test/efeito_chamados_bebe.json`, de `web/app/test/medir_chamados_bebe.ts`):
  - **as vidas:** as sementes 101, 202 e 303, nos dois ritmos, com os seis donos de roteiro do #450 (SEM FONTE);
  - **três estados das chaves:** "hoje" (sem o evento, os chamados pelo relógio), "#450" (as duas chaves de 2026-10-29) e "corpo" (as
    três);
  - **a fração de cuidado e o ramo** (sereno com 0,8 ou mais), conferidos pelo `test/produto_cuidado.test.ts`. Onde as sementes diferem,
    vai a faixa:

| ritmo | dono | hoje | #450 | corpo |
|---|---|---|---|---|
| rápido (180 min) | nada | 0 (arisco) | 0 (arisco) | 0 (arisco) |
| rápido | atende tudo na hora, ou 10 min depois | 1 (sereno) | 1 (sereno) | 1 (sereno) |
| rápido | brinca na 1ª hora e atende tudo | 1 (sereno) | 1 (sereno) | 1 (sereno) |
| rápido | só alimenta | 0,5 (arisco) | 0 (arisco) | 0,4–0,5 (arisco) |
| rápido | atende tudo, menos a fome | 0,5 (arisco) | **1 (sereno)** | 0,5–0,6 (arisco) |
| clássico (360 min) | nada | 0 (arisco) | 0 (arisco) | 0 (arisco) |
| clássico | atende tudo na hora, ou 10 min depois | 1 (sereno) | 1 (sereno) | 1 (sereno) |
| clássico | brinca na 1ª hora e atende tudo | 1 (sereno) | 1 (sereno) | 1 (sereno) |
| clássico | só alimenta | 0,478 (arisco) | 0 (arisco) | 0,533–0,615 (arisco) |
| clássico | atende tudo, menos a fome | 0,522 (arisco) | **1 (sereno)** | 0,273–0,333 (arisco) |

  - **Quem não faz nada sai arisco, e quem atende tudo sai sereno,** nos dois ritmos e nas três sementes, como o Gerente pediu.
  - **A comida conta:** quem nunca alimenta já não sai sereno (com o #450, saía). Quem só alimenta já não cai a 0.
  - **Os chamados que abrem, para o dono que não faz nada** (fome, higiene, carinho):
    - no rápido: hoje 5, 2 e 3; com a chave, 2, 1 e 1–2;
    - no clássico: hoje 11, 5 e 7; com a chave, 8, 4 e 1–3.
- **Um achado novo: o bebê não come a ração do dono.**
  - O pet só come com a fome abaixo de 0,45 (o instinto, `lobos.ts`, `agirInstinto`), e a fome do bebê fica acima disso no estágio.
  - Com a chave, o dono que atende cada chamado de fome deixa uma ração no comedouro por chamado, e elas ficam no mundo: são 2 no fim do
    rápido e 8 no do clássico, e a fome do bebê não sobe nenhuma vez. O teste está no `test/produto_cuidado.test.ts`.
  - O cuidado conta o gesto do dono, como a (C) previa. A ração que se acumula fica para o Matheus decidir (o PR, "Questões abertas").
- **Interpretações e achados** em `docs/registro/2026-10.md` (PRODUTO-CUIDADO).
