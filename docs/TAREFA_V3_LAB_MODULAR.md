# TAREFA V3 — LAB-MODULAR: o DigiBrain modular inteiro no jogo, em modo laboratório (2026-11-01)

Coordenador: Gerente da V3 (Claude Code, Opus 5.5). Worker: um por etapa, numa worktree `v3-lab-modular-<etapa>` com o branch do mesmo
nome, cortado da `origin/main`. Status: **ABERTA**, com as LAB-1 a LAB-5 DECIDIDAS pelo Matheus em 2026-11-01, pela recomendação ("Aprova"). Nenhum código foi
escrito para esta tarefa.

Categoria: implementacao. Origem: Matheus, 2026-11-01. Ele perguntou se dava para levar o cérebro modular inteiro ao jogo web para
testar já. O Gerente recomendou esperar o resultado da C4 e então levar o modular inteiro, num **modo laboratório** atrás de uma chave
desligada, com o A v11 seguindo como padrão. A resposta do Matheus foi "Siga sua recomendação".

**Esta tarefa substitui a L3 do `docs/PLANO_V3.md`** ("uma peça do modular no jogo; proposta: o lugar lembrado do M-MEM") e é o "plano
próprio do porte" que a D-C4-1 do PR #541 pede antes de a `memoria_autobio` ir ao jogo. A `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`
continua valendo para o passo seguinte, o modular como cérebro padrão do ovo, que esta tarefa **não** faz.

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | um pet de teste, nascido só pelo laboratório, decide no jogo com o DigiBrain modular inteiro, com o mesmo replay e o painel por módulo |
| o marco que desbloqueia | o Matheus joga com o modular e vê, no painel, qual módulo pesou em cada decisão |
| a evidência | o G-PAR de cada módulo e o G-PAR-VIDA (vidas inteiras decisão a decisão iguais ao Python); o G2 (a chave desligada deixa o jogo byte a byte); o e2e do laboratório |
| as dependências reais | o #541 na `main` com a D-C4-1 decidida; as LAB-1 a LAB-5 (seção 8) |
| se o gate falhar | o módulo que falha não entra, e a etapa para; o jogo segue com o A v11, que o laboratório nunca troca |

## 1. Pergunta

O DigiBrain modular, na configuração que a pesquisa validou, roda no jogo web com o mesmo comportamento do Python, decisão a decisão, sem
mudar nada para quem não liga o laboratório?

Não é run de pesquisa e não mede se o modular é melhor. O laboratório serve para ver o pet jogando; **nenhum número do jogo vira resultado.**

## 2. Depende de
- **Na `main`, já:** o pacote `digilab/digibrain/` com a C4 inteira (#530 a #539); o mundo, o corpo e o A v11 em TS (`web/app/motor/`); a
  conferência da fala de memória (`web/app/src/falaMemoria.ts`, #536).
- **O PR #541** (a run da C4) na `main`, com a D-C4-1 decidida: sem ela, a `memoria_autobio` sai da seção 3 e a LM3 porta só o lugar
  lembrado.
- **As LAB-1 a LAB-5** (seção 8), DECIDIDAS em 2026-11-01.

## 3. Mudança mínima: o que entra (a recomendação da LAB-1)

O Python de referência é o pacote `digilab/digibrain/` da `main` (12 arquivos, cerca de 2 050 linhas), atrás da `ConfigDigibrain`.

| peça | no laboratório | por quê |
|---|---|---|
| `ligada`, M-SENS, M-AFETO, M-IMPULSO, M-ARB, M-PLAST (P1 e P2), M-ESTADO com a persistência, M-ADAPT | **sim** | é o cérebro modular; os valores de partida são os de `ConfigDigibrainInatos`, PROPOSTOS, como estão |
| `cheiro_inato` e `intencao_cheiro` (a DX-3 e a DX-4; o M3\*) | **sim** | é o braço que a C1 validou no `longe_fixo` (#510) |
| `memoria_autobio`, braço REL (`controle_mem = "rel"`), com os negativos | **sim, se a D-C4-1 seguir a recomendação** | a C4 passou na linha 3 de A9.7 (#541): o Holm rejeita os três contrastes do primário, e a guarda não falha. O REL é o braço validado (D-C4-3) |
| a fala de memória (M6) | **sim**, pela conferência que já está na web (`web/app/src/falaMemoria.ts`) | a fala só alega o que o registro sustenta; a LLM continua fora do motor |
| `facetas_mem` | **não** | as facetas saíram `≈ 0` (D-C4-3) |
| `redecidir_evento` | **não** | a C3 saiu indeterminada (#527) |
| `credito_corrida` | **não** | a C2 saiu negativa (#517) |
| `intencao_suspensa` (a L-2) | **não** | a L-2 fechou como negativa (#454, #455) |
| `modula_g_apr` e os controles (`controle_g_apr`, os outros braços do `controle_mem`) | **não** | são controles de pesquisa, não peças do pet |
| a genética, dois pets, o modular como ovo padrão | **não** | fora desta tarefa (seção 6) |

**Nenhum número nasce na web.** Todo valor vem da `ConfigDigibrain` e da `ConfigDigibrainInatos` do Python, pelo gabarito das constantes.

### 3.1 As regras do porte

- **A aritmética é só inteira,** como no Python (a DM-2 e o G-INT). O espelho TS usa os mesmos arredondamentos (`div_arred`, `mul`) e o
  mesmo sorteio; nenhum `float` entra na decisão.
- **Um arquivo TS por módulo,** em `web/app/motor/digibrain/`, com o nome do Python (`sens.ts`, `afeto.ts`, …). O `digibrain.ts` de hoje
  é o painel do A v11 (#347) e **não muda**.
- **Os gabaritos vêm antes do TS** em cada etapa, gravados pelo Python em `web/app/test/gabaritos/` e saindo iguais em duas execuções.
  As sementes são as dos testes (101…505); não são vidas de pesquisa, e nenhuma faixa é reservada.
- **Nenhum gabarito existente é regravado.** Se um teste de replay ou de paridade que já passa quebrar, o worker para e avisa o Gerente.
- **O `digilab/engine.py` e o pacote `digilab/digibrain/` não mudam.** O que faltar no Python para exportar o gabarito (uma leitura nova,
  por exemplo) entra fora do pacote, num exportador em `experiments/`.
- **A chave desligada é o jogo de hoje byte a byte:** os pets v1 a v14 e os saves antigos abrem iguais (o G2 da etapa 4).

## 4. Experimento e gate: as etapas, na ordem (não há run)

| etapa | o quê | onde | gate | modelo |
|---|---|---|---|---|
| **LM0** | o exportador do Python: com a configuração da seção 3, vidas curtas do mundo (`longe_fixo` e comedouro) gravando, por decisão, a entrada de cada módulo, a saída, o motivo e a assinatura do estado; e as constantes do modular | `experiments/exportar_gabarito_digibrain_modular.py`, `web/app/test/gabaritos/digibrain_modular_*.json` | o gabarito sai igual em duas execuções; o tamanho cabe no repositório (abaixo de 10 MB por arquivo, ou o `.gz` da D-C4-4) | Sonnet |
| **LM1** | `_comum`, M-SENS, M-AFETO e M-IMPULSO em TS | `web/app/motor/digibrain/` | **G-PAR** de cada módulo: entrada a entrada igual ao gabarito | Sonnet |
| **LM2** | M-ESTADO (a intenção, o compromisso, a frustração, a DX-4), M-ARB e M-PLAST (P1 e P2, o crédito por opção) | idem | G-PAR de cada módulo | Sonnet |
| **LM3** | M-MEM: o lugar lembrado e a `memoria_autobio` REL (o episódio, a consolidação, a lembrança, o termo `L` e as sondas); os ganchos do M-PERS ficam vazios | idem | G-PAR do M-MEM; as sondas `sem_lembranca` iguais ao Python | Sonnet |
| **LM4** | o M-ADAPT montado e o laço: `motor_corpo_mundo.ts` passa a perguntar ao modular quando a chave do laboratório está ligada (a chave da v13 do comentário de hoje vira a do laboratório; a LAB-3 decide o nome da versão) | `web/app/motor/digibrain/adapt.ts`, `web/app/motor/motor_corpo_mundo.ts` | **G-PAR-VIDA:** vidas inteiras do gabarito decisão a decisão iguais; **G1:** o replay bit a bit; **G2:** chave desligada, todos os gabaritos de hoje passam sem regravar | Sonnet; Opus se o G-PAR-VIDA divergir sem causa clara |
| **LM5a** | as pranchas do laboratório e do painel por módulo (390 e 1280 px, nas duas peles), com só o que o motor tem | `docs/pranchas/lab/` | o Matheus aprova as pranchas (LAB-4 e LAB-5) | Sonnet |
| **LM5b** | a tela: o laboratório em Ajustes, o ovo de teste, o selo "experimental", o painel com a contribuição de cada módulo a partir do motivo, a fala de memória pela conferência | `web/app/src/` | o e2e: o pet de teste nasce, come a comida posta, lembra o lugar e o painel mostra o motivo; os testes do `web/app` passam | Sonnet |

As etapas LM0 a LM4 só tocam o motor e os testes. A LM5b é a única que toca a tela (`web/app/src/`).

## 5. Entrega e os arquivos disputados

- **`web/app/motor/motor_corpo_mundo.ts`** (LM4): só esta tarefa mexe nele enquanto ela estiver aberta.
- **`web/app/src/`** (LM5b): a B3 (código) e a L4 (a M3) também tocam a tela. A LM5b espera a B3 ser mergeada, ou o Gerente alterna as
  duas, uma missão por vez em `App.tsx`, `tokens.css`, `pet.css` e `Nav.tsx` (`docs/PLANO_V3.md`, seção 5).
- **`digilab/digibrain/`:** esta tarefa só lê. Se uma pesquisa nova da trilha C mexer no pacote, o gabarito da LM0 é refeito antes da
  etapa seguinte.

## 6. Fora desta tarefa

- o modular como cérebro do ovo padrão, e o que fazer com os pets v11 (a `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`, seção 8);
- as peças da seção 3 marcadas "não";
- qualquer medida de desempenho do modular no jogo como resultado de pesquisa;
- a calibração dos valores PROPOSTOS (fica para a rodada de equilíbrio, no fim);
- a D-C1-3 (de onde vem o ganho do M3\*). Ela segue aberta como descritivo com plano próprio, antes de o modular virar o padrão, e não
  antes do laboratório.

## 7. Critérios de aceitação

- Com o laboratório desligado, nada muda: todos os gabaritos e e2e de hoje passam sem regravar.
- Com o laboratório ligado, o pet de teste decide como o Python, decisão a decisão, nas vidas do gabarito.
- O replay é bit a bit.
- O painel mostra o motivo por módulo e a lembrança, sem rótulo que prometa mais do que o cérebro faz.
- Cada etapa num PR próprio, com o relato conferido por `tools/verificar_relato.py`, e o painel da V3 atualizado.
## 8. Precisa do Matheus

**DECIDIDAS em 2026-11-01:** as cinco, pela recomendação ("Aprova", no chat com o Gerente da V3).

Cada uma com a recomendação e o custo de errar.

- **LAB-1, o que entra:** a tabela da seção 3.
  - Recomendação: o M3\* mais a `memoria_autobio` REL, sem as facetas, sem a C2, a C3 e a L-2.
  - Custo de errar: com menos peças, o laboratório não mostra a memória que a C4 validou. Com as peças negativas, o pet de teste carrega
    mecanismos sem efeito medido.
- **LAB-2, como o pet de teste nasce:** em Ajustes › Laboratório, um ovo de teste num espaço próprio do save, ao lado dos pets de hoje.
  - Recomendação: assim, com o selo "experimental" na tela do pet.
  - Custo de errar: com o modular no ovo padrão, um pet de verdade nasce com um cérebro que não é o padrão e não volta atrás. Sem espaço
    próprio, o pet de teste mistura o save.
- **LAB-3, o nome da versão:** a DM-5 chamou o modular de "v13", mas no jogo a v13 e a v14 já são pets da luta (`CV21E_TR`, a B2).
  - Recomendação: a próxima versão livre (hoje a v15), com tudo da v14 menos o cérebro, que passa a ser o modular. A LM4 confere a base
    antes do código.
  - Custo de errar: reaproveitar a v13 quebra os saves dos pets v13 que lutam hoje.
- **LAB-4, o painel por módulo:** a contribuição de cada módulo na ação escolhida (impulso, plasticidade, memória, persistência), como as
  barras do A v11, mais a lembrança da vez ("lembrou do lugar X").
  - Recomendação: as pranchas da LM5a antes de qualquer código de tela.
  - Custo de errar: sem prancha, a tela é refeita depois de pronta.
- **LAB-5, o lugar na fila:** as LM0 a LM4 começam já, porque só tocam o motor. A LM5b espera a B3.
  - Recomendação: assim.
  - Custo de errar: com a LM5b antes da B3, as duas disputam a tela e uma refaz a outra.


## 9. Resumo da etapa LM0 (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm0`)

O exportador do gabarito está pronto: `experiments/exportar_gabarito_digibrain_modular.py`. Nenhum código TS, nenhum parâmetro novo;
`digilab/engine.py` e `digilab/digibrain/` não mudaram, e nenhum gabarito existente foi regravado.

- **A configuração:** o braço REL da C4 (`run_v2_digibrain_prototipo.SUBCHAVES_C4["REL"]`, com `conserto=True`): `ligada`, `p1`, `p2`, `m_mem`,
  `persistencia`, `cheiro_inato`, `intencao_cheiro`, `memoria_autobio` e `controle_mem = "rel"`; desligadas `facetas_mem`,
  `redecidir_evento`, `credito_corrida`, `intencao_suspensa` e `modula_g_apr`. As constantes efetivas (`ConfigDigibrain` e
  `ConfigDigibrainInatos`) estão em `digibrain_modular_constantes.json`.
- **As vidas:** o mundo do MVP (`CONFIG_MUNDO_MVP`), `longe_fixo` e comedouro × donos atencioso e relapso × sementes 101 e 202 × 4 dias
  (384 decisões) = 8 vidas. Por que essas: com 4 dias há 3 consolidações do dia (a lembrança vem da duradoura e da central); o relapso deixa de
  cuidar e provoca a busca e o lugar lembrado; o atencioso cobre a comida posta. A soma das 8 vidas cobre, pelo `cobertura` das constantes:
  o P2 (hábito ≠ 0 em 2 361 das 3 072 decisões), o P1, a persistência, a busca guardada (DX-4, 16 decisões com `busca_entregue`), os fins
  `achou`, `meta` e `trocou`, a memória recuperada, a lembrança com termo `L` e sem ele (as sondas `sem_lembranca` em toda decisão), o
  lugar lembrado como alvo (`Alvo.ponto`, 104 decisões), as consolidações, os episódios autobiográficos e os gestos do dono. A vida
  atencioso/`longe_fixo`/101 não come (só explora e dorme): fica pelo caso sem episódios.
- **O tamanho:** cada lugar tem ~27 MiB de texto (4 vidas × ~6,8 MiB; ~17,8 KiB por decisão), acima dos 10 MB. Os arquivos vão em
  `.json.gz` (mtime 0, nível 9: 1,2 e 1,3 MiB) e o sha256 do texto original fica em `arquivos` nas constantes. Mais vidas ou dias
  custariam repositório sem ganho de cobertura; a LM4 pode pedir outras vidas pelo mesmo exportador.
- **O formato:** o docstring do exportador. Por decisão: as chamadas em ordem (`adapt.*` e os métodos dos módulos que o M-ADAPT chama direto,
  com `e`, `s` e `$ref` para o objeto que repete uma saída da decisão), o `motivo` final e a `assinatura` (sha256 de 16 hex do
  `estado_interno` de sens, afeto, estado, mem, arb e plast); por vida, o sha256 do log e do estado interno. A rng de política vira o
  sha256 do estado antes e depois.
- **Teste:** `tests/test_gabarito_digibrain_modular_web.py` (6 testes): o exportador sai igual em duas execuções e o gravado bate com uma
  execução nova (comparando o texto, não o gzip), o sha256 e o limite de 10 MB, as constantes efetivas, a cobertura.
- **Achado, não resolvido (LAB-3):** a "próxima versão livre (hoje a v15)" já está em uso: o PR #525 (aberto, `v3-habitat-objetos`) usa pet
  v15. A LM4 decide o número depois de conferir a `main`.
