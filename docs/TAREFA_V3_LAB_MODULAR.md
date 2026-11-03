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
- **Teste:** `tests/test_gabarito_digibrain_modular_web.py` (8 testes): o Gravador não muda a vida (log, ações, rngs, motivos, estado interno, `episodio_autobio` restaurado), o exportador sai igual em duas execuções e o gravado bate com uma
  execução nova (comparando o texto, não o gzip), o sha256 e o limite de 10 MB, as constantes efetivas, a cobertura.
- **Achado, não resolvido (LAB-3):** a "próxima versão livre (hoje a v15)" já está em uso: o PR #525 (aberto, `v3-habitat-objetos`) usa pet
  v15. A LM4 decide o número depois de conferir a `main`.

## 10. Resumo da etapa LM1 (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm1`)

Os espelhos TS de `_comum`, M-SENS, M-AFETO e M-IMPULSO estão em `web/app/motor/digibrain/` (`_comum.ts`, `sens.ts`, `afeto.ts`, `impulso.ts`,
mais `constantes.ts`), com o G-PAR de cada módulo passando. Nada do jogo os usa ainda: nenhuma tela, laço ou chave; o `digibrain.ts` do A v11, o
`digilab/engine.py` e o pacote `digilab/digibrain/` não mudaram, e os três gabaritos da LM0 não foram regravados.

- **Nomes:** as classes (`Sens`, `Afeto`, `Impulso`) e as funções seguem o Python em camelCase, como o resto do motor TS (`div_arred` →
  `divArred`, `sinal_corpo` → `sinalCorpo`); os campos dos dados (`falta`, `g_apr`, `termos`…) ficam em snake_case, como no gabarito.
- **Constantes:** `constantes.ts` copia a `ConfigDigibrainInatos` e a `ConfigDigibrain` do braço REL do `digibrain_modular_constantes.json`;
  `test/digibrain_modular_constantes.test.ts` confere cada folha. O gabarito da LM0 não traz os números do `Config` e da `ConfigMundo` que o
  M-SENS lê (passo de 15 ticks, noite 1320–420, `sub` 16, raio 6, 8 vistos): ficam em `CONFIG_MODULAR_MUNDO` e o teste os confere contra
  `constantes_python.json` e a `CMU` do motor.
- **Aritmética:** só inteira, com o `divArred` do jogo (`mundo.ts`); o único float é o `vetor_estado[7]` (a hora), que vira o minuto pelo
  `round` do Python (meio para o par), como no Python. Sem rng nestes módulos. As funções do A (`faltaReceptor`, `leituraReceptor`,
  `contribuicoesCorpo`, `sinalCorpo`) vêm do `lobos.ts`, com os pesos `w_d` todos 1, como o Python sem `pesos_drives`.
- **O que o gabarito da LM0 não bastava:** o `Impulso.unidades` recebe o M-PLAST (`<plasticidade>` no gabarito), e o incentivo não se reconstrói
  dos termos (`mul(incentivo, prox)` perde o incentivo). Pedi uma leitura nova ao exportador, num commit próprio: `--leituras-plast` grava
  `digibrain_modular_leituras_plast.json.gz` (as chamadas `plast.habito` e `plast.incentivo` de dentro do impulso, 8 vidas × 384 decisões), sem
  tocar os três arquivos da LM0. O teste do impulso usa um M-PLAST de mentira que devolve o que o Python devolveu e confere a entrada de cada
  pergunta. O `casa` (`<fn>`, do M-MEM) é refeito no teste (a LM3 porta o oficial). A persistência chega por `{textoDaChave(chave): h}`.
- **Fora do laboratório:** `facetas_mem` (LAB-1). O `Impulso` falha alto se ligada ou se vierem `facetas`; o ramo das facetas do Python não foi portado.
- **G-PAR (conferidas, nas 8 vidas):** `sens.codificar` 3 072; `afeto.ler` 3 072, `afeto.drives` 3 072, `afeto.consequencia` 3 064;
  `impulso.unidades` 3 072 (com lembrança, lugar lembrado, incentivo, hábito e persistência cada um em pelo menos uma decisão). Cada teste falha se a conta for zero.

## 11. Resumo da etapa LM5a (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm5a`)

As pranchas estão em `docs/pranchas/lab/` (só papel; nenhum código em `web/app/`): Ajustes › Laboratório, a tela Pet com o selo
"experimental" e o painel do DigiBrain modular, cada uma em 390 e 1280 px, nas peles Vidro e Militar (12 capturas PNG, `gerar.py`,
`capturar.sh`, `lab.css`). O `LEIA.md` da pasta tem o quadro de onde vem cada barra e cada texto (o campo do motivo de `adapt.py`) e as
decisões LM5-1 a LM5-6.

- **O painel:** as barras são a parte de cada termo da unidade escolhida (`termos.inato`, `prox`+`nov`, `incentivo` P1, `habito` P2,
  `memoria`, `lembranca`, `persistencia`; a faceta fica desligada), a lembrança da vez (`alvo`, `lembranca`), a intenção em curso
  (`estado.I`, `C`, `F`, `n_sp`), as chances (`unidades[].w`), o que mudaria a escolha (as `sondas`) e as últimas ações.
- **Decisões para o Matheus:** LM5-1 (painel no celular: folha), LM5-2 (barras: só as não nulas), LM5-3 (barra negativa: divergente),
  LM5-4 (o lugar lembrado em coordenadas, não em região), LM5-5 (uma prancha a mais para o pet de teste já nascido, com descarte), LM5-6
  (mostrar compromisso e frustração). Cada uma com a recomendação e o custo de errar no `LEIA.md`.
- **O que depende de leitura fora do motivo:** o "desde a decisão N" (`estado_interno().modulos.estado.I.inicio`) e a região do episódio.
- A LM5b só começa com as pranchas aprovadas (LAB-4) e depois da B3 (LAB-5).

## 12. Resumo da etapa LM2 (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm2`)

Os espelhos TS do M-ESTADO, do M-ARB e do M-PLAST (P1 e P2) estão em `web/app/motor/digibrain/` (`estado.ts`, `arb.ts`, `plast.ts`), com um G-PAR
por módulo em `web/app/test/` passando. Nada do jogo os usa ainda; `digilab/engine.py`, `digilab/digibrain/` e `web/app/motor/digibrain.ts` não
mudaram, nenhum gabarito foi regravado e o exportador não precisou de leitura nova.

- **Fora do laboratório (LAB-1):** o `EstadoDinamico` levanta erro se `credito_corrida`, `intencao_suspensa` ou `redecidir_evento` vierem ligadas
  (e `cuidarSuspensa`, `eventos` e `registrarRedecisao` levantam erro); a `Arbitragem` levanta erro com `facetas_mem` ou com `segurar`.
  `modula_g_apr` e os controles já estavam fora na LM1.
- **A rng do M-ARB:** o gabarito guarda só o sha256 do estado da rng. O TS a refaz com o `RandomPy` do jogo semeado com `semente + 1_000_003`
  (a `_rng_politica` do `engine.py`) e confere, a cada `arb.escolher`, o sha256 do `getstate()` antes e depois contra `rng_antes` e `rng_depois`.
- **O estado:** o gabarito não grava o estado por chamada, só a assinatura ao fim de cada decisão. Cada G-PAR refaz a vida inteira num módulo
  novo, na ordem das chamadas, e confere a assinatura dele (`estado`, `arb`, `plast`) ao fim das 3 072 decisões; a saída é conferida em toda chamada.
- **O M-PLAST:** o `habito` e o `incentivo` chamados pelo impulso vêm do `leituras_plast` da LM1, refeitos no ponto do `impulso.unidades`, com o estado
  de agora do M-PLAST.
- **G-PAR (conferidas, nas 8 vidas):** estado 9 208 (contexto 3 072, escolhida 3 072, consequência 3 064) e 3 072 assinaturas; arb 6 144 (reflexo
  3 072, escolher 3 072: 2 505 sorteios, 567 sem sorteio, 522 reflexos); plast 28 772 (montar 3 072, consequencia_p1 166 com 91 consumos, creditar
  3 042, habito 21 504, incentivo 988). Cada teste falha se a conta for zero.
- **Cobertura que o gabarito não tem:** os fins `sumiu` e `desistiu` do M-ESTADO não aparecem nas 8 vidas (só `meta`, `trocou`, `achou`, `unica`);
  o ramo `sumiu`/`desistiu` está portado linha a linha, mas sem G-PAR. Pedir outras vidas ao exportador é decisão da LM4.

## 13. Resumo da etapa LM3 (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm3`)

O espelho TS do M-MEM está em `web/app/motor/digibrain/mem.ts`, com o G-PAR em `web/app/test/digibrain_modular_mem.test.ts` passando. Nada do jogo o usa ainda;
`digilab/engine.py`, `digilab/digibrain/` e `web/app/motor/digibrain.ts` não mudaram, nenhum gabarito foi regravado e o exportador não precisou de leitura nova.

- **O que entrou:** o lugar lembrado (`codificar`, `recuperar`, o `casa` oficial, que o teste do impulso passou a usar) e a `memoria_autobio` REL: o episódio completo
  (`episodioAutobio`), o tick (`relogio`), as faixas do corpo, a lembrança (`lembrar`), o lugar pela soma, a consolidação (duradoura e central), o termo
  `L = mul(w_lem, sigma)` (`termoLembranca`) e o `estadoInterno`.
- **Fora do laboratório (LAB-1):** `facetas_mem` e os bracos de pesquisa do `controle_mem` (sem, rec, emb, rel_sem_neg) falham no construtor; `evidenciaFaceta` e
  `classesComPositivo` falham alto; os ganchos do M-PERS não existem no TS. Sem rng, aritmética só inteira.
- **O gabarito:** o `adapt.episodio_autobio` do fechamento da decisão `k-1` está na lista da `k-1` e o `$ref` dele na da `k` (o gravador conta `adapt.*` como `k - 1`); o G-PAR resolve isso (ver o registro).
- **G-PAR (conferidas, nas 8 vidas, 18 797 chamadas):** `mem.relogio` 3 072; `mem.consolidar` 3 072 (24 registros não nulos); `mem.lembrar` 3 072 (2 097 lembranças, nas três memórias);
  `mem.termo_lembranca` 3 072; `mem.recuperar` 3 072 (471 lugares recuperados); `mem.codificar` 154; `mem.codificar_autobio` 219; `adapt.episodio_autobio` 3 064 (219 episódios de
  origem consumo, evento e visita; 2 845 sem episódio). Mais as sondas: o `impulso.unidades` e o `arb.escolher` refeitos com o termo e o `casa` do `mem.ts` nas 3 072 decisões
  (`sem_lembranca` presente nas 3 072, `lembranca_decidiu` em 81, unidade com termo `L` em 1 514 decisões) e a assinatura do `mem` igual ao fim de cada decisão. O teste falha se uma conta for zero.

## 14. Resumo da etapa LM4 (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm4`)

O M-ADAPT está em `web/app/motor/digibrain/adapt.ts` (a classe `DigiBrain`: `agir`, `observar`, `estadoInterno`, `escolherAlvo`, `consequenciaMundo`,
`consequenciaCorpo`, `receberAcaoDono`, o fechamento com o `episodioAutobio`), o laço pergunta ao modular quando a chave do laboratório está ligada, e o pet de teste
(v16) nasce só pela fábrica `petDeTeste` (`motor/pet_lab.ts`). `digilab/engine.py`, `digilab/digibrain/`, `motor/digibrain.ts` e `web/app/src/` não mudaram; nenhum
gabarito existente foi regravado. Os desvios estão no registro (2026-11, LM4).

- **A versão (LAB-3):** a v15 está tomada pelo PR #525 (aberto), então o pet de teste é a **v16** (`VERSAO_PET_LAB`). Herda a v14 (regras de luta `CV21E_TR14`, mundo do
  produto, corpo) menos o cérebro. `VERSAO_PET` segue 14 e `VERSOES_PET` segue `[13, 14]`; a v16 entra por exceção explícita. O `bracoV11` fica na v16 só para o desejo e o
  caráter, sem decidir nem aprender.
- **O laço:** a chave `digibrain` de `OpcoesLacoMundo` (a "chave da v13") é a do laboratório: ligada, o laço dá `obs.mundo` ao cérebro, pergunta o alvo e chama o
  `consequenciaMundo` depois do `observar`. Desligada, o laço é o de hoje (G2).
- **As leituras novas do exportador (commits próprios):** `--logs` (`digibrain_modular_logs.json.gz`, o log do motor das 8 vidas) e `--fins`
  (`digibrain_modular_fins.json.gz`, 6 vidas com `sumiu` e `desistiu` do M-ESTADO; o `desistiu` só aparece com `n_desiste_cheiro = 2`, valor do próprio arquivo).
- **Os gates:** G-PAR-VIDA (`test/digibrain_modular_vida.test.ts`): 3 072 decisões das 8 vidas da LM0 e 2 304 das 6 dos fins (5 376 no total), iguais ao Python em ação, motivo
  e assinatura dos seis módulos, mais o sha256 do estado interno inteiro no fim de cada vida. G1 (`test/pet_lab.test.ts`): o replay do pet de teste, evento a evento, por
  replay e por save. G2: a suíte inteira (contagens no PR).
- **Cobertura que falta:** os ramos `sumiu`/`desistiu` das intenções com alvo (`comer/comida`, `brincar/bola`, `explorar/ponto`) não ocorreram em nenhuma vida achada;
  seguem portados sem G-PAR-VIDA.

## 15. Resumo da etapa LM5a2 (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm5a2`)

A prancha extra da LM5-5, aprovada pelo Matheus em 2026-11-03: **Ajustes › Laboratório com o pet de teste já nascido** (nome, forma, idade, Abrir e Descartar) e a **confirmação
do Descartar** (o save do pet de teste é apagado e não volta; os pets de hoje não são tocados), em `docs/pranchas/lab/` (`ajustes_vivo_*`, `ajustes_descartar_*`), 390 e 1280 px,
Vidro e Militar, 8 capturas. Papel só: nenhum código em `web/app/`. A fonte de cada campo está no `LEIA.md`. O pet de teste é a v16 (a v15 é do #525). Decisões novas
LM5-7 (o que o Abrir faz), LM5-8 (força da confirmação) e LM5-9 (baixar o log antes), cada uma com recomendação e custo de errar no `LEIA.md`. A LM5b espera a B3.

## 16. Resumo da etapa LM5b (2026-11-03, worker Claude Code, Sonnet 5.5, worktree `v3-lab-modular-lm5b`)

A tela do laboratório está no jogo web, atrás da chave desligada: **Ajustes › Laboratório** (a explicação, a chave, o ovo de teste v16 e a lista com Abrir e Descartar), o selo "experimental" na plaquinha do topo, o **painel
DigiBrain do modular** (a folha no celular, a coluna no desktop) e o import e o export dos saves v16. A LM5b veio **antes da B3**, a pedido do Matheus em 2026-11-03 (o desvio está no registro); a B3 parte desta tela.
O pet de hoje, o painel do A v11 e os saves antigos abrem iguais; `digibrain/adapt.ts`, o laço e os gabaritos não mudaram.

- **Ajustes › Laboratório** (`src/telas/config/Laboratorio.tsx`, `src/lab.ts`): a chave `CHAVE-lab-ligado` (desligada); o pet de teste em `CHAVE-lab`, um por vez; **Abrir** (LM5-7) mostra o pet na tela Pet sem trocar o pet ativo
  (`jogo.ts`: `abrirLab`, `sairDoLab`; o botão "voltar ao meu pet" na plaquinha); **Descartar** (LM5-8) abre a confirmação sem digitar, com o foco em Cancelar, e apaga só `CHAVE-lab`. Sem baixar o log (LM5-9).
- **O painel** (`src/componentes/DigiBrainLab.tsx`, `Motor.leituraLab()` em `motor/digibrain/leitura.ts`): Agora, Lembrança da vez (o lugar em coordenadas, LM5-4), o peso de cada módulo (só as barras não nulas, divergentes, com o "−", LM5-2 e LM5-3;
  a linha "Sem contribuição agora"), Intenção em curso com C, F e n_sp e uma linha de explicação (LM5-6), as opções e a chance de cada uma, o que mudaria a escolha (as sondas) e as últimas ações. Todo número vem do motivo do motor.
- **Os saves v16** (`src/importar.ts`): o arquivo v16 abre pelo replay e vai para o Laboratório; nunca vira pet ativo nem guardado.
- **Fora:** a fala de memória (a conferência `falaMemoria.ts` não foi ligada; ver o registro).
- **Testes:** `test/lab_leitura.test.ts` (a leitura), `test/lab_tela.test.ts` (o espaço do save, o Abrir, o descarte que só apaga o save do teste, o importar e exportar v16), `e2e/lab_modular.spec.ts` (chocar, abrir, o painel mostra o motivo, descartar com
  confirmação) e `e2e_capturas/lab.spec.ts` (as capturas, só com `DIGILAB_CAPTURAS_LAB=<pasta>`). As contagens estão no PR.
- **Capturas** (390 e 1280 px, Vidro e Militar, claro e escuro, 40 PNG): `docs/pranchas/lab-tela/capturas/`.
