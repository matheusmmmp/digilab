# TAREFA V2 — WORLD_POC_02 (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-world-poc-02`. Status: ENTREGUE (E0 a E3; a E4, o Android mais simples, fica para quando houver o aparelho).

Categoria: implementacao. Origem: Matheus, 2026-10-19: o Gate B do mundo 3D (organismo corporificado, ainda com o cérebro de teste), depois do Gate A aprovado em 2026-10-19.

## 1. Pergunta

**O WORLD-POC-02 responde:** o organismo do POC-01a fecha o laço inteiro do contrato sensório-motor (`docs/futuro/mundo_3d.md`, seção
4) com um corpo de verdade? Um laço é:
- o pet percebe;
- decide (o cérebro de teste);
- navega;
- age sobre o mundo físico;
- sente a consequência pelo **corpo químico** (o `corpo.ts`, com fome, digestão e metabolismo).

É o **Gate B** da especificação ("organismo corporificado": percepção, decisão, navegação e consequências físicas e fisiológicas), ainda
**sem o cérebro A**. É um protótipo técnico, não pesquisa: não vem de hipótese do `docs/PLANO_V2_PESQUISA.md` e não tem run nem semente
reservada.

**Depois do Gate A**, aprovado pelo Matheus em 2026-10-19 (`docs/TAREFA_V2_WORLD_POC_01.md`), com duas ressalvas:
- só um celular, recente, foi medido;
- o cérebro de verdade no mundo novo (a P4) espera o Gate C.

## 2. Depende de

- **Na `main`:**
  - o POC-01a (#355, #358), com o mundo inteiro, a vista e o contrato;
  - o `corpo.ts` com o metabolismo (#333);
  - a `CCO_V11`, a config do corpo do v11 em `web/app/motor/constantes.ts`.
- **Decisões que já existem:** W-1 a W-7 (`docs/futuro/mundo_3d.md`, seção 8); o Gate A (2026-10-19).
- **Decisões que esta tarefa pede ao Matheus:** seção 8 (CP-1 a CP-7).

## 3. Mudança mínima

**A ideia:** o corpo de brinquedo do POC-01a (a fome e o tédio que só sobem) dá lugar ao **`Corpo` do `corpo.ts`, como ele está**.
- As consequências do mundo físico do POC viram os **estímulos que o corpo já tem**.
- O corpo anda um passo por tick.
- O cérebro de teste passa a ler os receptores.
- Nenhum químico, emissor ou estímulo novo entra no corpo.

| o que muda | onde | como |
|---|---|---|
| o corpo do pet | `web/app/poc/mundo3d/mundo.ts` (ou um `corpo_poc.ts` ao lado) | o `Corpo` do `corpo.ts` com a `CCO_V11`, nascido pelo `Corpo.deEstado` de um estado inicial fixo. O tick do POC passa a ser 1 minuto de jogo (CP-3) |
| o passo do corpo | o passo do mundo | `corpo.passo({ tick, dormindo, sujeira })` a cada tick, no estado do começo do tick, como o `MotorCorpo` do jogo (`web/app/motor/motor_corpo.ts`). A sujeira fica em 0, porque o POC não tem sujeira (CP-4) |
| comer a comida do mundo | quando o pet come | `corpo.estimuloConsumoMundo("racao", "madura", CMU)`: a comida vai ao estômago, e a digestão a passa para a fome |
| andar | o fim de cada decisão | `corpo.estimuloAndar(deslocamento, CMU.custo_energia_por_subunidade)`, com o deslocamento inteiro da decisão. Um arredondamento só, como no mundo físico do Python. Com o metabolismo, sai também do combustível |
| a bola | o empurrão | `corpo.estimuloBola(CMU.ganho_humor_bola)` e `corpo.atividade("bola")` (o tédio). No máximo uma vez por decisão (CP-5) |
| descansar | a Intenção `descansar` | `dormindo` verdadeiro nos ticks dela, e o sono do corpo (o basal dormindo, o cansaço caindo) faz o resto (CP-2) |
| o contato | a colisão | **nenhum efeito no corpo**, só registro (CP-1) |
| a Observação | `sensores.ts`, `tipos.ts` | o campo `corpo` passa a ser `Corpo.receptores()`, os inteiros na escala S, no lugar da fome e do tédio de brinquedo. Só os receptores; o cérebro nunca lê a química |
| o cérebro de teste | `cerebro.ts` | as mesmas regras sobre os receptores: a falta de fome acima de um limiar leva à comida, a de tédio à bola e a de energia ao descanso. Os limiares são PROPOSTOS, sem fonte |
| o registro | `registro.ts`, `simulacao.ts` | a consequência fisiológica (a 4 do contrato) passa a ser real: os receptores antes e depois de cada decisão e a contribuição de cada drive, com a mesma conta do `contribuicoesCorpo` do `lobos.ts` |
| a fronteira | `web/app/test/poc_mundo3d.test.ts` | a G-FRONTEIRA passa a permitir que o POC importe **o `corpo.ts` e o que ele importa**, e nada mais de `motor/` (CP-6). O motor e o jogo continuam sem importar o POC |
| a chave | `Simulacao` | `corpo: false` (o padrão) dá o POC-01a byte a byte, com os hashes do `artifacts_v2_world_poc/e2e.json`; `corpo: true` liga o corpo |
| a vista | `vista.ts`, `pagina.ts` | um painel com os receptores do corpo, só desenho, e a página com o corpo ligado |

**O que NÃO muda:**
- o jogo (`web/app/src/`, o `npm run build` do app sai idêntico);
- o motor do jogo (`web/app/motor/`, inclusive o `corpo.ts`: só é importado, sem mudança);
- o motor da pesquisa (`digilab/`) e o `engine.py`;
- o cérebro A (`lobos.py`, `lobos.ts`);
- os gabaritos;
- a física inteira e o contrato do POC-01a (a Observação continua relativa, sem posição absoluta).

## 4. Experimento e gate (se houver run)

Não há run de pesquisa nem plano de análise: é um protótipo técnico, sem semente reservada. Os gates são técnicos, por etapa:

| etapa | o quê | gate | PR |
|---|---|---|---|
| **E0** | a chave `corpo` e o POC-01a guardado | **G-POC01-IGUAL:** com `corpo: false`, os hashes das sementes 101, 202 e 303 são os do `artifacts_v2_world_poc/e2e.json`, e os 31 testes do POC-01a passam sem mudança. Este teste entra num commit **antes** do corpo | PR 1 |
| **E1** | o corpo no mundo do POC | **G-CORPO-IGUAL:** o corpo dentro do POC é o `corpo.ts` sem cópia. Uma vida do POC grava a sequência de chamadas ao corpo (os passos e os estímulos); essa sequência, aplicada a um `Corpo` solto, dá a mesma química no fim. **G-CONSEQUENCIA:** comer a comida do mundo põe alimento no estômago e, com a digestão, tira a falta de fome; andar sobe o cansaço e, com o metabolismo, tira do combustível na proporção do deslocamento; o empurrão na bola tira do tédio e da tristeza; o contato não muda nenhum químico | PR 1 |
| **E2** | os receptores na Observação, o cérebro de teste sobre eles e o registro fisiológico | **G-CONTRATO-CORPO:** a Observação traz só os receptores, sem química nem posição absoluta, e o `cerebro.ts` continua importando só o `tipos.ts`. **G-LACO (o Gate B):** numa vida com a semente fixa, o registro mostra a cadeia completa ao menos uma vez em cada ramo (a comida e a bola): a falta alta no receptor, a Observação com o objeto visto, a Intenção, a ação executada até chegar, o resultado físico, os receptores antes e depois, e a falta menor depois. **G-DET:** a mesma semente dá o mesmo estado, o replay refaz a vida, e o hash é o mesmo no Node e no Chrome (o e2e) | PR 1 |
| **E3** | a vista do corpo | **M-CORPO:** o painel dos receptores aparece na página e acompanha o corpo (o e2e confere o texto do painel contra os receptores do estado). **G-APP-IGUAL:** o build do app sai idêntico (o sha256 do `web/dist/`) | PR 2 |
| **E4** (opcional, ressalva do Gate A) | o Android mais simples | a M3 do POC-01a num Android de entrada, se o Matheus tiver um à mão; sem ele, fica registrado como não medido | PR 2 |

Se um gate falhar, o worker registra o resultado como está e não ajusta o critério olhando para ele.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V2_*.md` da run ou o `TAREFA_V2_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.
- **Também:** o e2e da página do POC (`npm run poc:e2e`) e as medidas em `artifacts_v2_world_poc/`, num arquivo novo para o POC-02. Os do
  POC-01a não mudam.
- **Dois PRs:** o PR 1 com E0 a E2 (o organismo, testável no Node); o PR 2 com E3 e E4.

## 6. Fora desta tarefa

- **O cérebro A** (`lobos.ts`) no mundo novo: é a P4, que espera o Gate C (W-5).
- **O jogo:** nenhuma tela, versão de pet, save ou prancha.
- **O Python e a paridade:** o POC segue só em TS. O corpo é o `corpo.ts`, que já tem paridade com o `corpo.py`, mas o mundo do POC não
  tem gêmeo no Python. O porte do mundo do POC para o `mundo.py`, com paridade e atrás de chave (W-4), é da P4.
- **Química nova:**
  - a dor por batida;
  - a curiosidade pela novidade (CP-1, CP-6);
  - a sujeira e o banheiro;
  - o paladar (a fruta com gosto).
- **Dois pets, o dono e os gestos** (o carinho e o tapa precisam de um dono no POC, que não há).
- **O POC-01b** (o Rapier), que segue opcional.

## 7. Critérios de aceitação

| critério (o Gate B da especificação) | o que confere |
|---|---|
| percepção | a Observação com os receptores e os objetos vistos, sem acesso privilegiado: G-CONTRATO-CORPO |
| decisão | o cérebro de teste decide sobre os receptores: G-LACO |
| navegação | o pet chega à comida e à bola, como no POC-01a: G-NAVEGA continua passando, e G-LACO |
| consequências físicas | a comida some, a bola anda e o contato fica no registro: G-CONSEQUENCIA |
| consequências fisiológicas | o corpo muda pelos estímulos certos, com o mesmo resultado de um `Corpo` solto: G-CORPO-IGUAL e G-CONSEQUENCIA |
| a cadeia rastreável | o registro com as cinco coisas do contrato, com a consequência no corpo real: G-LACO |
| a arquitetura de hoje continua | o POC-01a igual (G-POC01-IGUAL), o app igual (G-APP-IGUAL) e as quatro suítes passando, com a contagem no PR |

**A estimativa**: de **3 a 5 dias de sessão**, PROPOSTA e SEM FONTE. A base é o POC-01a, que levou 1 dia de sessão para os dois PRs,
mas com o mundo novo; aqui o mundo existe e o corpo já tem paridade. As hipóteses:
- um worker;
- o `corpo.ts` sem mudança;
- sem o Python.

## 8. Precisa do Matheus

**As sete DECIDIDAS em 2026-10-19, pela recomendação** (o Matheus, pelo coordenador), inclusive a CP-7: o Gate B fecha no POC, em TS, e a
paridade do mundo com o Python fica para a entrada da P4.

| # | decisão | DECIDIDO (a recomendação) | o custo de errar |
|---|---|---|---|
| CP-1 | o contato (bater na parede, no obstáculo, na bola) tem efeito no corpo? | **não**: só registro. Uma dor por batida seria química nova e SEM FONTE; ela é do Sistema nociceptivo (J10, adiado) ou do proprioceptivo, que ainda é ideia (`docs/DEFINICOES_CORPO_V2.md`, 8.1) | baixo: o registro já guarda o contato, e o efeito entra depois, atrás de chave |
| CP-2 | o `descansar` é dormir? | **sim**: `dormindo` nos ticks da Intenção, em qualquer lugar da sala. O POC não tem ninho; o conforto do ninho (`mundo_fisico.md`, 2.2) fica para depois | médio: sem dormir, o cansaço só sobe e o pet de teste se esgota; com o sono em qualquer lugar, o descanso fica fácil demais |
| CP-3 | o tick do POC vira 1 minuto de jogo? | **sim**: as taxas do corpo são por minuto. A página do POC-01a anda 10 ticks por segundo, então 1 segundo de tela é 10 minutos de corpo, e um dia passa em 2,4 minutos de tela | baixo: é um protótipo; a velocidade da página é um número só |
| CP-4 | a sujeira e a higiene | **ficam paradas** (a sujeira em 0): o POC não tem sujeira nem banheiro. **A premissa estava errada (corrigida em 2026-10-19):** a sujeira fica em 0, mas a higiene cai pelo próprio corpo, mesmo sem sujeira, e o POC não tem como limpar. O Matheus decidiu, pela recomendação (a), deixar como está: a queda entra como dado (o pet sem dono piora), sem um limpar do dono (seção 10) | baixo: a higiene não muda e não entra em nenhuma consequência |
| CP-5 | o empurrão na bola conta como brincar no corpo uma vez por decisão ou por empurrão? | **uma vez por decisão** com empurrão, como o `brincou_com_bola` do `ocorrido` do mundo físico do Python | baixo: empurrões seguidos não viram vários brincares |
| CP-6 | o POC pode importar o `corpo.ts` do `motor/` | **sim**: só o `corpo.ts` e o que ele importa, sem cópia, para o corpo do POC ser o do jogo e da pesquisa. A G-FRONTEIRA confere a lista, e o motor e o jogo continuam sem importar o POC | baixo: copiar duplicaria o corpo e quebraria a paridade com o `corpo.py` sem ninguém ver |
| CP-7 | o Gate B se fecha no POC (em TS) ou só com o mundo também no Python? | **no POC**: a demonstração técnica do organismo corporificado. A paridade do mundo com o Python (a seção 7 do `mundo_3d.md` pedia "no motor, Python e TS") fica como critério de entrada da P4, junto com o Gate C | médio: se o Gate B exigir o Python, a P4 começa antes do Gate C, o que a W-5 não quer |

## 9. Execução

As etapas entregues entram aqui, cada uma numa seção no fim deste documento.

## 10. Etapas E0 a E2, entregues (2026-10-19, PR 1)

**E0, a chave e o POC-01a guardado:**
- a `Simulacao` ganhou a opção `corpo` (desligada por padrão);
- o **G-POC01-IGUAL** (`web/app/test/poc_mundo3d_corpo.test.ts`) entrou num commit antes do corpo. Com a chave desligada, os hashes das
  sementes 101, 202 e 303 são os do `artifacts_v2_world_poc/e2e.json`, e os registros saem iguais.

**E1, o corpo no mundo do POC** (`web/app/poc/mundo3d/corpo_poc.ts`, o único ponto do POC que importa o motor, CP-6):
- **o corpo:** o `Corpo` do `corpo.ts` com a `CCO_V11`, nascido do estado inicial `ESTADO_INICIAL_POC` (PROPOSTO);
- **por tick, depois do passo do mundo:**
  - comer chama o `estimuloConsumoMundo("racao", "madura")`;
  - o primeiro empurrão da decisão chama o `estimuloBola` e a `atividade("bola")` (CP-5);
  - o corpo anda o `passo`, no estado do começo do tick: `dormindo` no `descansar` (CP-2) e sem sujeira (CP-4);
- **no fim de cada decisão:** o `estimuloAndar` com o caminho andado;
- **o contato não chama o corpo** (CP-1);
- **o registro:** cada chamada fica gravada (`chamadasCorpo`). O estado ganha o `corpo.paraDict()` só com a chave.

**E2, o contrato com o corpo:**
- **a Observação:** o campo `corpo` passa a ser `Corpo.receptores()` com a chave ligada, e o corpo de brinquedo com ela desligada;
- **o cérebro:** o `cerebroDeTesteCorpo` (`cerebro.ts`, que continua importando só o `tipos.ts`) decide sobre as faltas dos receptores,
  com os limiares PROPOSTOS `LIMIARES_CORPO` (exausto 700, fome 350, tédio 300, na escala 1024);
- **o registro:** cada decisão leva os receptores antes e depois e a `consequencia` por drive, a conta do `contribuicoesCorpo` do
  `lobos.ts` com todos os pesos 1 (o teste confere contra ele).

**Os gates** (`web/app/test/poc_mundo3d_corpo.test.ts`, 17 testes; os 31 do POC-01a seguem passando):
- **G-POC01-IGUAL:** passa (3 sementes, os hashes do POC-01a).
- **G-CORPO-IGUAL:** as 3.150 chamadas de uma vida de 3.000 ticks, refeitas num `Corpo` solto com a conta escrita de novo no teste, dão
  o mesmo `paraDict()`. Sem uma das comidas, sai outro (o controle negativo).
- **G-CONSEQUENCIA:**
  - comer passa pela digestão (o `digerido_total` sobe) e tira a falta de fome, e toda decisão que comeu termina com a consequência da
    fome positiva;
  - andar 240 sobe o cansaço o dobro de andar 120, e o combustível com diferença de no máximo 1;
  - a bola tira do tédio e da tristeza, uma vez por decisão;
  - o contato não chama o corpo: só os quatro estímulos, e há contato no registro.
- **G-CONTRATO-CORPO:** a Observação traz exatamente as chaves de `Corpo.receptores()`, sem química e sem posição absoluta.
- **G-LACO, o Gate B:** a vida da semente 101 fecha as duas cadeias:
  - **a comida**, na decisão 34: a falta de fome em 691 (acima de 350), a comida vista, `consumir` com o `ref` dela, `chegou` em 2
    ticks, comeu, e a falta de fome caiu para 243;
  - **a bola**, na decisão 27: o tédio em 553 (acima de 300), a bola vista, `empurrar`, 52 subunidades andadas, 2 empurrões, a bola
    de (152, 56) a (185, 78), e o tédio caiu para 276.
- **G-DET:** no Node, a mesma semente dá a mesma vida, e o replay pelo log a refaz, com o corpo. No Chrome
  (`web/app/e2e_poc/corpo.spec.ts`), os hashes das sementes 101, 202 e 303 com o corpo são os do Node
  (`artifacts_v2_world_poc/poc02_e2e.json`).
- **A G-FRONTEIRA**, mudada pela CP-6: o POC só importa a si mesmo, o `three` (só na vista) e, do motor, o fecho do `corpo.ts`
  (`corpo.ts`, `constantes.ts`, `estado.ts`, `mundo.ts`...), calculado pelo próprio teste a partir dos imports.

**A vida de demonstração** (`npm run poc:medir02` → `artifacts_v2_world_poc/poc02_laco.json`; só descritiva):
- a semente 101, 3.000 ticks, 199 decisões fechadas;
- os resultados das Intenções: 68 descansos, 52 explorações, 6 `consumir` (3 comeram), 73 `empurrar` (57 pararam bloqueados contra
  uma parede ou um obstáculo);
- **o achado:** no fim, a fome e a higiene estão em 0 e a saúde caiu de 1024 para 148. Também ficaram no máximo o tédio, a solidão e o
  estresse. O pet do POC, sem dono e com o cérebro de teste, piora em dois dias de jogo. Duas coisas pesam:
  - **a higiene cai pelo próprio corpo:** a premissa da CP-4 ("a higiene não muda") estava errada; sem sujeira, ela cai mesmo assim,
    e o POC não tem como limpar;
  - a comida é uma só na sala, e o cérebro de teste a acha pouco (só no cone da visão).

  Isso não fere o Gate B, que é a cadeia, mas mostra que um organismo no mundo novo precisa de mais do que o laço: um dono, ou um
  cérebro que procure.

## 11. Etapa E3, entregue (2026-10-19, PR 2), e a premissa da CP-4 corrigida

**O painel do corpo** (`web/app/poc/mundo3d/pagina.ts`, `poc/mundo3d.html`):
- **a página roda com o corpo ligado por padrão** (o POC-02); `?corpo=0` volta ao POC-01a, e o e2e do POC-01a usa essa forma;
- **o painel:** abaixo da sala, um painel mostra os dez receptores do corpo (fome, higiene, energia, humor, saúde, tédio, solidão,
  estresse, dor, susto), cada um com a leitura de 0 a 1024 e uma barra. É só desenho: ele lê `Corpo.receptores()` a cada quadro, e o
  motor nunca lê a tela;
- **o título** diz qual POC está rodando.

**Os gates:**
- **M-CORPO** (`web/app/e2e_poc/corpo.spec.ts`): com a página rodando e depois pausada, os valores do painel são exatamente os
  receptores do estado, nas mesmas chaves, e o painel aparece (`artifacts_v2_world_poc/poc02_e2e.json`, M_CORPO;
  `poc02_painel.png`). Com `?corpo=0`, não há corpo nem painel;
- **G-APP-IGUAL:** o build do app sai idêntico ao da `main`, o mesmo sha256 dos arquivos de `web/dist/`;
- o e2e da página passa com 10 testes: os 7 do POC-01a, agora com `?corpo=0`, e os 3 do POC-02.

**A premissa da CP-4, corrigida:**
- a tarefa dizia que a higiene não mudava sem sujeira. Ela cai pelo próprio corpo, e o POC não tem como limpar;
- na vida de demonstração (`artifacts_v2_world_poc/poc02_laco.json`), a higiene e a fome chegam a 0 e a saúde cai de 1024 para 148
  em 3.000 ticks;
- **o Matheus decidiu, pela recomendação (a), deixar como está:** é um dado (o pet sem dono piora), e não entra um limpar do dono.

**A E4** (um Android mais simples, a ressalva 1 do Gate A) fica para quando houver o aparelho, pelas instruções da M3 do POC-01a
(`docs/TAREFA_V2_WORLD_POC_01.md`, seção 11).
