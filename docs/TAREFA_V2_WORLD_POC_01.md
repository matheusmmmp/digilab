# TAREFA V2 — WORLD_POC_01 (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-world-poc-01`. Status: EM ANDAMENTO.

Categoria: implementacao. Origem: Matheus, 2026-10-19: o WORLD-POC-01a da investigação WORLD-POC-001 (docs/futuro/mundo_3d.md), aprovado em 2026-10-19 para avançar em paralelo ao Gate C.

## 1. Pergunta

**O WORLD-POC-01a responde:** a arquitetura decidida para o mundo 3D funciona no navegador? É a do `docs/futuro/mundo_3d.md`:
- W-1: a física no motor, em inteiros (o arranjo V);
- W-2: o Three.js imperativo só como vista;
- o contrato sensório-motor da seção 4, sem o DigiBrain conhecer a engine.

**É um protótipo técnico, não pesquisa.** Ele não vem de hipótese do `docs/PLANO_V2_PESQUISA.md`, não tem run nem semente reservada e
fecha o **Gate A** (a viabilidade técnica; `docs/futuro/mundo_3d.md`, seção 7). É a fase P3 da especificação, que **avança em paralelo**
ao Gate C (a W-5, como o Matheus esclareceu em 2026-10-19, trata do cérebro de verdade no mundo novo, a P4, e não da P3).

A especificação inteira (o escopo, os componentes, os testes, as métricas e a estimativa) está em `docs/futuro/mundo_3d/poc_01.md`.
Esta tarefa a põe em etapas com gates e diz o que não entra.

## 2. Depende de

- **Na `main`:** a investigação (#340: `docs/futuro/mundo_3d.md` e os anexos em `docs/futuro/mundo_3d/`).
- **Decisões do Matheus que já existem:**
  - W-1 a W-7 (2026-10-18, pela recomendação; `docs/futuro/mundo_3d.md`, seção 8);
  - a liberação do POC em paralelo ao Gate C (2026-10-19).
- **Nenhuma frente de código precisa entrar antes:** o POC não usa o `motor/` do jogo, o `lobos.ts` nem o `corpo.ts`.

## 3. Mudança mínima

**O que muda** (todos os caminhos PROPOSTOS; o worker pode ajustar nomes, sem mudar as fronteiras):

| arquivo | papel | conhece o Three.js? |
|---|---|---|
| `web/app/poc/mundo3d/mundo.ts` | o estado inteiro da sala (o piso de 16 × 12 células de 16 subunidades, as paredes, os obstáculos, a bola, a comida e o pet) e o `passo()` de um tick | não |
| `web/app/poc/mundo3d/fisica.ts` | a física inteira: o círculo contra o retângulo, o deslize, a bola (atrito, reflexão na parede com restituição em fração inteira, o empurrão) e os sub-passos | não |
| `web/app/poc/mundo3d/controlador.ts` | o A* inteiro na grade e a execução da Intenção até chegar, bloquear, o alvo sumir ou dar a hora | não |
| `web/app/poc/mundo3d/sensores.ts` | a Observação do contrato (`mundo_3d.md`, 4.2): o cone com raio na grade e oclusão (o obstáculo alto tapa, o baixo não), os bigodes em 8 setores e o contato. Nenhuma posição absoluta de objeto na Observação | não |
| `web/app/poc/mundo3d/cerebro.ts` | o cérebro de teste: um decisor de regras (a fome leva à comida, o tédio leva à bola) que lê só a Observação e devolve só a Intenção (`mundo_3d.md`, 4.3). **Não é o cérebro A** | não, e um teste confere |
| `web/app/poc/mundo3d/registro.ts` | o registro por decisão: a Observação, a Intenção, a ação executada e o resultado físico (`mundo_3d.md`, 4.1), exportável em JSON | não |
| `web/app/poc/mundo3d/vista.ts` | o Three.js: a câmera ortográfica inclinada (M-2), as caixas do piso e das paredes, o pet como `THREE.Sprite` com filtro nearest e escala inteira, a sombra como disco, a parede da frente semitransparente quando cobre o pet e a interpolação entre ticks | **sim, e só ele** |
| `web/app/poc/mundo3d.html` e `web/app/poc/vite.config.ts` | a página e uma config do Vite própria, **fora do build do app** (o `npm run build` do jogo sai igual) | — |
| `web/app/test/poc_mundo3d*.test.ts` | os testes da seção 7 | — |
| `web/app/package.json` | a dependência `three` em versão exata (a 0.186.1 foi a conferida em 2026-10-18, `docs/futuro/mundo_3d/tecnologias.md`), mais um script `poc` para abrir a página | — |

**O sprite (W-6):** o pet usa um quadro do atlas do Digimon UP, **só local e sem versionar**, carregado como o `src/atlas.ts` faz. Sem
o atlas, entra um sprite de reserva desenhado à mão, que vai no repositório.

**O que NÃO muda:**
- o jogo: `web/app/src/` e o `npm run build` do app;
- o motor do jogo (`web/app/motor/`) e as versões de pet;
- o motor da pesquisa (`digilab/`, inclusive `mundo.py` e o `engine.py`, congelado);
- o cérebro A (`digilab/policies/lobos.py`, `web/app/motor/lobos.ts`);
- os gabaritos, os experimentos e as runs.

O POC não importa nada de `web/app/motor/` nem de `src/`, e nada de lá o importa.

## 4. Experimento e gate (se houver run)

Não há run de pesquisa nem plano de análise: é um protótipo técnico, sem semente reservada. Os gates são técnicos, por etapa:

| etapa | o quê | gate (o teste ou a medida) | PR |
|---|---|---|---|
| **E0** | a página, a config própria do Vite, a dependência `three` e o sprite de reserva | **G-FRONTEIRA:** um teste lê o fonte; só o `vista.ts` importa `three`; nada de `poc/` importa `motor/` ou `src/`, e o contrário também não; o `npm run build` do app não muda de conteúdo | PR 1 |
| **E1** | a física inteira e o controlador | **G-COLISAO:** o círculo não atravessa a parede nem o canto, desliza, e a bola rápida não atravessa com os sub-passos. **G-BOLA:** o empurrão dá velocidade na direção do contato, o atrito para a bola e a reflexão troca a componente normal. **G-NAVEGA (M4):** o pet chega ao alvo em todos os cenários com os dois obstáculos | PR 1 |
| **E2** | os sensores, o contrato, o cérebro de teste e o registro | **G-SENSOR:** o obstáculo alto tapa e o baixo não; nada fora do cone aparece; a Observação não traz posição absoluta de objeto. **G-CONTRATO:** o `cerebro.ts` só importa os tipos do contrato. **G-DET (a primeira metade da M5):** a mesma semente e o mesmo log dão o mesmo hash do estado, duas vezes no Node | PR 1 |
| **E3** | a vista | **M1:** a página abre e o WebGL desenha (o screenshot do e2e não é vazio). **M2:** os pixels do sprite na tela batem com os do quadro na escala inteira, sem borrar, nos quatro cantos da sala | PR 2 |
| **E4** | as medições e o relato | **M3:** os quadros por segundo e o tempo de quadro, no desktop e num celular real (PROPOSTO: 30 quadros por segundo no celular; a emulação do Playwright não vale). **M5:** o mesmo hash no Node e no Chrome (o e2e), e o tempo do replay de 1 dia de sala, só descritivo. **M6:** o bundle da página em gzip, só descritivo. Os números vão para `artifacts_v2_world_poc/` | PR 2 |

Se um gate falhar, o worker registra o resultado como está e não ajusta o critério olhando para ele.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V2_*.md` da run ou o `TAREFA_V2_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.
- **Dois PRs, na ordem:**
  - o PR 1, com as etapas E0 a E2, é o mundo do POC sem a vista: tudo testável no Node;
  - o PR 2, com as etapas E3 e E4, traz a vista, as medições e a seção do resultado no fim deste documento.

## 6. Fora desta tarefa

- **O POC-01b** (o Rapier, `@dimforge/rapier3d-deterministic-compat`): fica opcional e separado, com tarefa própria, e só se o Matheus
  quiser medir antes de rever a W-1.
- **O Python e a paridade:** o POC é só TS. A física inteira só vai para `mundo.py` e `mundo.ts` com paridade na P4, com tarefa própria,
  atrás de chave desligada (W-4).
- **O cérebro A no mundo novo** (a P4): espera o Gate C (W-5).
- **O jogo:** nenhuma tela, versão de pet, save ou prancha nova.
- **O corpo químico:** o cérebro de teste usa uma fome e um tédio de brinquedo, sem os receptores.
- **Dois pets, o som, o cheiro e a curiosidade.**
- **Sprites direcionais:** o POC usa um quadro de frente, espelhado para os lados; se o atlas tem outras direções, isso fica Não
  verificado e anotado.

## 7. Critérios de aceitação

| critério da especificação (seção 8) | o que confere |
|---|---|
| o navegador renderiza o ambiente adequadamente | M1 no e2e e M3 com o artefato em `artifacts_v2_world_poc/` |
| o sprite permanece visualmente correto | M2, teste do e2e; a oclusão vista no screenshot do artefato |
| o corpo físico colide com objetos | G-COLISAO e G-BOLA, testes em `web/app/test/` |
| o pet consegue navegar até um alvo | G-NAVEGA (M4), teste |
| a física produz resultados observáveis | G-BOLA e o registro exportado: a bola empurrada se move, e o registro mostra quanto |
| o DigiBrain recebe observações sem depender da engine | G-FRONTEIRA e G-CONTRATO, testes que leem o fonte |
| a arquitetura atual continua funcionando | `npm test`, `npm run tipos`, `npm run e2e` e `python -m pytest tests/ -q` passam, com a contagem no PR; o build do app sai igual (G-FRONTEIRA) |

**A estimativa** (`docs/futuro/mundo_3d/poc_01.md`, seção 7; PROPOSTA, sem histórico para calibrar): de 5,5 a 8,5 dias de sessão para o
POC-01a, com estas hipóteses:
- um worker;
- o atlas na máquina;
- sem Python;
- um celular real para a M3.

## 8. Precisa do Matheus

**As três DECIDIDAS em 2026-10-19, pela recomendação** (o Matheus, pelo coordenador):

- **O celular da M3: DECIDIDO.** O Matheus faz a M3 abrindo a página num celular real. A página mostra os quadros por segundo na tela e
  os copia em JSON. O worker deixa as instruções prontas no PR 2. Sem a medida, a M3 fica Não verificada e o Gate A, parcial.
- **O limite da M3: DECIDIDO.** Os 30 quadros por segundo no celular são **referência, não gate duro**. O número segue sem fonte.
- **A dependência `three`: DECIDIDO.** Ela entra no `package.json` do app, **com a versão exata e sem faixa**: a `0.186.1`, publicada
  em 2026-09-24 (o registro do npm, `docs/futuro/mundo_3d/tecnologias.md`). A G-FRONTEIRA garante que o app não a importa.

## 9. Execução

As etapas entregues entram aqui, cada uma numa seção no fim deste documento.
