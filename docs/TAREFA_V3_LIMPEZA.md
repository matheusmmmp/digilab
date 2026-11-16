# TAREFA V3 — LIMPEZA (2026-11-16)

Coordenador: sessão do Matheus (Claude Code). Worker: Claude Code, worktree `v3-limpeza`. Worktree e branch: `v3-limpeza`. Status: EM ANDAMENTO
(a LZ0 e a LZ1; as decisões D-LZ-1 a D-LZ-3 DECIDIDAS pelo Matheus em 2026-11-16, pela recomendação: "Aceito").

Categoria: arquitetura. Origem: Matheus, 2026-11-16: "vamos tentar enxugar o projeto [...] separar o que era do Bandit, que não está
sendo mais usado, do Cérebro A, que também não está sendo mais usado", com as escolhas (nesta sessão):
- **o A sai de tudo:** do jogo (a escolha em Ajustes e o fallback) e da pesquisa; as peças que o modular usa vão para um módulo neutro do
  modular. Isso muda a decisão de 2026-10-24 ("o A é a linha de base, o controle e o fallback condicionado"), e o `CLAUDE.md` muda na LZ5;
- **o escopo:** o bandit, o A e a v1; também o cérebro B, o C e a camada única da V2, e os experimentos da v1 que só eles usam. O combate
  fica;
- **o backup:** uma tag no commit de antes da limpeza; os arquivos saem do git e vão copiados, com os mesmos caminhos, para
  `D:\Trab\digilab\backup_limpeza_2026-11`, fora do repositório. O Matheus move essa pasta depois, e nenhuma sessão a lê como contexto.

## 1. Pergunta

Não há pergunta de pesquisa. O objetivo é que o código e os documentos vivos digam só o que o jogo e a pesquisa da V3 usam: o motor, o
DigiBrain modular, o mundo, o corpo, o grupo, a bancada e o combate.

## 2. O que o inventário mostrou (LZ0)

O inventário é gerado por `tools/inventario_limpeza.py` (só lê o código pela AST) em `docs/limpeza/inventario_python.json`. Ele classifica
cada arquivo Python em SAI, REFAZ, FICA ou REVER (a docstring do script define as classes). Na `main` de 2026-11-16 (`58a22928`):

| área | SAI | REFAZ | FICA | REVER |
|---|---|---|---|---|
| `digilab/` | 13 | 15 | 53 | 2 |
| `experiments/` | 130 | 9 | 42 | 10 |
| `tests/` | 19 | 81 | 236 | 16 |
| `tools/` | 0 | 1 | 26 | 0 |
| `servidor/` | 0 | 0 | 6 | 0 |

**O limite do inventário:** ele lê imports, não o que a vida roda. A bancada é uma raiz viva e ainda monta os braços do A (o A11, o
J5, o pet que pensa), então os testes e gabaritos das vidas do A que passam pela bancada saem como FICA ou REFAZ. Eles viram SAI na LZ2,
quando a bancada perde esses braços, e a lista da LZ1 separa um caso do outro.

**Os cérebros não saem só movendo arquivos.** Três amarras:

1. **O modular importa peças do A.** Sete arquivos de `digilab/digibrain/` tiram do `lobos.py` as funções `div_arred`, `leitura_receptor`,
   `falta_receptor`, `sinal_corpo`, `contribuicoes_corpo` e `valor_previsto`; o `motivo.py` e o `painel_digibrain.py` tiram as tabelas
   `ENTRADAS`, `ENTRADAS_MUNDO`, `REGRAS`, `REGRAS_MUNDO`, `FATORES_PLANO` e a função `sortear`. No web é igual: o `ObservacaoLobos`
   e o `TransicaoLobos` de `motor/lobos.ts` são os tipos da observação de todo pet, e o `digibrain.ts` e o `carater.ts` importam de lá.
2. **A cadeia de motores das vidas de hoje passa pela v1.** O `motor_corpo.MotorCorpo` herda do `educacao.MotorEducacao`, que herda do
   `obediencia.MotorPersonalidade` (o arquivo da política do bandit com personalidade). Toda vida do modular passa por essas classes com
   a educação e a obediência desligadas, e o índice dos eventos que o replay confere conta os eventos delas
   (`motor_corpo.py:371`). O `protocol.py` importa os `FATORES_*` do `memoria.py` e do `memoria_espacos.py`, e por ele quase todo o
   pacote alcança os arquivos do bandit.
3. **No web, todo pet tem um `Bandit`.** O `Motor` cria um `Bandit` em toda vida (`motor/motor.ts:277` e `:541`) e chama o `observar`,
   o `receberAcaoDono` e o `assinatura`, nunca o `agir`. A assinatura dele entra na conferência das vidas salvas, então as 15 versões de
   pet de hoje (`VERSOES_PET`, v21 a v37) dependem dele. 68 arquivos de `web/app` citam o bandit ou o A, 34 deles testes.

## 3. As etapas

Cada etapa é um PR. Nenhuma muda o `engine.py`.

- **LZ0 (este PR):** o inventário, o script e esta tarefa. Nenhum código muda.
- **LZ1, os gabaritos:** num commit próprio, antes de qualquer mudança: as vidas do modular em todos os mundos e braços da bancada
  (comedouro, perto, longe, `longe_fixo`, `longe_ancora`; os braços M0 a M3\*, REL e PAD; os quatro donos), byte a byte, e a lista dos
  gabaritos do web que a LZ2 e a LZ3 não podem mudar.
- **LZ2, o Python neutro:**
  - as funções e tabelas da amarra 1 vão para `digilab/digibrain/base.py`, sem mudar uma linha da conta;
  - os `FATORES_*` vão para o `protocol.py`, com os mesmos valores;
  - a cadeia de motores da amarra 2 vira uma só, com o comportamento de hoje com a educação, as lesões e a obediência desligadas, e o
    mesmo índice de eventos;
  - a bancada perde os braços do A, do B e do C;
  - aceita só com os gabaritos da LZ1 iguais e o inventário sem nenhum REFAZ no `digilab/` e na bancada.
- **LZ3, o web:**
  - os tipos e funções do `lobos.ts` que o modular usa vão para `motor/digibrain/base.ts`;
  - o A sai de Ajustes e do fallback (`src/cerebro.ts`, `CEREBROS`, `pet_v11.ts`), e o `Bandit` sai do `Motor`;
  - a saída do `Bandit` muda a assinatura, então pede uma versão nova de pet e decide o que acontece com as de hoje (D-LZ-1);
  - depende do #931 (v38 e v39), que mexe nas mesmas versões.
- **LZ4, a saída:**
  - a tag `antes-limpeza` no commit da `main` de antes da saída;
  - os arquivos SAI, com os testes, os experimentos, as configs, os artefatos das runs e os documentos dessas frentes (D-LZ-3), saem do git e
    vão copiados para `D:\Trab\digilab\backup_limpeza_2026-11`, com os mesmos caminhos e uma lista com o sha256 de cada um;
  - os REVER são decididos um a um na tabela do PR;
  - a suíte inteira, o `npm test`, o `npm run tipos` e o `npm run e2e` passam.
- **LZ5, os documentos:** o `CLAUDE.md` (a decisão do A e a seção Arquitetura), o `docs/MAPA_REPOSITORIO.md`, o `docs/PAINEL_V3.md`, um índice
  de uma página do que saiu (`docs/historico/LIMPEZA_2026-11.md`, com a tag) e a memória das sessões, que nunca lê a pasta do backup.

## 3.1 A LZ1: o que guarda cada gabarito de hoje

Cada gerador `tests/gabarito_*.py` foi rodado com as classes do bandit, do A, do B, do C e da camada única armadas para parar na primeira
instância (`tools/cerebro_do_gabarito.py`). O resultado:

- **Guardam o modular (10), e são a guarda da LZ2 em diante:**
  - o `limpeza_lg` (novo, LZ1);
  - o `digibrain_conserto`, o `digibrain_modular` e o `memoria_autobio`;
  - o `sono_segura`, o `redecidir_evento`, o `habito_intencao` e o `conversa_dc3`;
  - o `gosto_visual_enjoo` e o `orgao_visao`.
  - Fora dos `tests/gabarito_*.py`, os gabaritos do CO6 e do CO7 (`experiments/exportar_gabarito_co6.py` e `co7`) usam o modular.
- **Rodam o A (38), e saem na LZ2 com os braços do A:**
  - pelo script (34): `arvore_sacode`, `bancada_k4`, `bancada_liga`, `bancada_montagem`, `banheiro`, `banheiro_ligado`, `banheiro_perto`,
    `corpo`, `corpo_mundo`, `digibrain`, `dois_pets`, `fruta_ao_lado`, `genoma_g0`, `gosto_visual`, `lance_dono`, `lugar_estilos`,
    `lugar_estilos_lg`, `metabolismo`, `metabolismo_ligado`, `mundo`, `orgao_sem_direcao`, `orgaos`, `p2d_p3i`, `p2d_p3i_bancada`, `p4`,
    `paladar`, `paladar_mundo`, `pet_que_pensa`, `pet_que_pensa_plano`, `pqp_adendo7`, `pqp_ao_lado`, `pqp_mundo`, `rede_de_si` e
    `tv_jogo`;
  - pela leitura do código (4): o `canais_reforco`, o `cerebro_n6_n7` e o `competicao` importam o `lobos.py`, e o `credito_canal` é da
    V3-9 da V2. Os quatro recusam regravar, e o script não os rodou.

**O achado:** várias mecânicas que o jogo usa só têm gabarito com o A: a árvore que sacode, a TV do jogo, o lance do dono, o banheiro, o
metabolismo ligado, os órgãos, a fruta ao lado e os dois pets. Quando o A sair, elas ficariam sem guarda byte a byte no Python. A paridade do web
(os gabaritos `*_python.json`) continua guardando o lado TS.

**A LZ1 parte 2 (feita, aprovada pelo Matheus: "Sim, grave"):** o `tests/gabarito_limpeza_mecanicas.py`
(`tests/gabaritos/limpeza_mecanicas_de_hoje.json`, 60 vidas, num commit próprio) grava as mecânicas com os cérebros que ficam: o modular
do jogo (o REL) e o instinto do mundo.
- **As mecânicas:**
  - a árvore que sacode, só com a chave e com o roteiro do dono que sacode (18 sacudidas por vida, na ilha);
  - o banheiro, o metabolismo e o corpo da etapa 6;
  - a fruta ao lado e o lance do dono.
- **As recusas de hoje ficam gravadas:** o modular recusa o corpo do banheiro (os receptores `vontade` e `conforto`, fora do protótipo).
- **Onde a guarda vem de outros gabaritos:**
  - os dois pets e o lance com o modular: as entradas do REL do `lance_dono`;
  - o modular com a TV: o `gosto_visual_enjoo` e o `orgao_visao`.
- **O que segue sem guarda Python com o modular:** a TV do jogo (`cfg_tv_jogo`, só no modo livre gravado) e a ilha com água (exige o
  controlador do contrato). As entradas do instinto nos gabaritos do A (a árvore, o banheiro, os dois pets) continuam valendo e ficam na
  LZ2, sem as do A.

## 4. Experimento e gate

Não há run. O gate de cada etapa é o byte a byte dos gabaritos da LZ1 e a suíte.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (a LZ3 e a LZ4).
- Registro: seção própria no fim de `docs/registro/2026-11.md` em cada etapa que decidir algo.
- PR contra a `main` com o relato no corpo; merge só pelo Matheus.

## 6. Fora desta tarefa

- O combate (`digilab/combate_v2/`, a luta da POC) fica, inclusive o que a educação usa dele.
- A LONGE_GEOMETRIA: a run roda do checkout `v3-longe-geometria-run`, parado no `58a22928`, e não é afetada. A análise e o
  `RESULTADO_V3_LONGE_GEOMETRIA.md` saem antes de a LZ2 entrar na `main` (D-LZ-2).
- Mudar o comportamento de qualquer pet ou vida de pesquisa: a limpeza só tira o que não roda.

## 7. Critérios de aceitação

- `python tools/inventario_limpeza.py` sem nenhum arquivo SAI nem REFAZ no repositório depois da LZ4.
- Os gabaritos da LZ1 iguais byte a byte depois da LZ2, da LZ3 e da LZ4.
- A tag `antes-limpeza` existe na origem, e a lista com o sha256 de cada arquivo do backup confere com o conteúdo dele nessa tag.
- A suíte inteira e os testes do web passam na LZ4.

## 8. Precisa do Matheus

**DECIDIDAS em 2026-11-16** pela recomendação ("Aceito", nesta sessão): a versão nova sem o `Bandit` e sem o A, com as de hoje
fechando com aviso (D-LZ-1); a LZ0 e a LZ1 já, a LZ2 em diante depois do resultado da LONGE_GEOMETRIA (D-LZ-2); os documentos e os
artefatos das frentes que saem vão para o backup (D-LZ-3).

- **D-LZ-1, os pets de hoje no web (antes da LZ3).** Tirar o `Bandit` do `Motor` muda a assinatura de toda vida salva.
  - **Recomendação:** uma versão nova sem o `Bandit` e sem o A; as versões de hoje deixam de abrir, com aviso, como as v13 a v19 na LP-6. Não
    há saves de terceiros.
  - **Alternativa:** manter uma cópia congelada do `bandit.ts`, usada só para abrir os saves velhos. A limpeza fica pela metade no web.
  - **Custo de errar:** com a recomendação, você perde os seus pets atuais; com a alternativa, o bandit continua no código do jogo.
- **D-LZ-2, a ordem com a LONGE_GEOMETRIA.**
  - **Recomendação:** a LZ0 e a LZ1 entram já; a LZ2 em diante só depois do resultado da LONGE_GEOMETRIA, porque a análise roda pelo
    código da `main`.
  - **Custo de errar:** se a LZ2 entrar antes, a análise pode quebrar ou mudar o hash do protocolo no meio da frente.
- **D-LZ-3, os documentos e os artefatos das frentes que saem.**
  - **Recomendação:** os `TAREFA`, `PLANO_ANALISE` e `RESULTADO` das frentes do bandit, do A, do B, do C e da v1, com as pastas
    `artifacts_*` delas, vão para o backup. No repositório ficam o `docs/LEITURA_CONSOLIDADA_DONO.md`, o `docs/FECHAMENTO_V2.md` e o
    índice da LZ5.
  - **Custo de errar:** um resultado antigo citado num documento vivo fica sem o artefato no repositório. Ele continua na tag e no backup.

## 9. Depois da limpeza

As fases L0 a L6 da complexidade acidental (versões, chaves, constantes duplicadas, `core/` sem DOM, CI) começam da `main` depois da LZ5
("Limpeza antes", Matheus, 2026-11-16). O pedido e as adaptações dele estão em `docs/futuro/complexidade_acidental_l0_l6.md`. A principal
adaptação é que, pela D-LZ-1, a garantia de replay dos saves vale da versão da LZ3 em diante.

