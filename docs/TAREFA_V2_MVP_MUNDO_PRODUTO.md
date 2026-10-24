# TAREFA V2 — MVP_MUNDO_PRODUTO: o mundo físico no jogo, com a comida posta pelo jogador (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: a definir (o A, dono da web, é o candidato natural). Worktree e branch: `v2-mvp-mundo-<etapa>`.
Status: **ABERTA, só papel.** Nenhum código. As decisões MV-1 a MV-6 (seção 8) estão abertas.

Categoria: implementacao. Origem: Matheus, 2026-10-24, o PROMPT MESTRE (seção 7): o primeiro produto jogável, com o mundo físico
integrado ao jogo. **Esta tarefa absorve o #399** (`docs/futuro/comida_arrastar.md`, que não foi mergeado). O conteúdo dele está
reescrito aqui, **sem a dependência da P4.**

## 0. Os cinco pontos (`docs/PRODUTO_VISAO.md`, seção 2)

| ponto | resposta |
|---|---|
| a capacidade | o pet do jogo percebe uma comida posta pelo jogador num lugar, decide, navega, come, e o corpo muda |
| o marco que desbloqueia | o MVP (`docs/PRODUTO_VISAO.md`, seção 3) e o lugar onde o cérebro modular entra no jogo (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`) |
| a evidência | testes de paridade com o Python, o replay, os testes de unidade e o e2e de integração (pôr a comida, o pet anda e come, o corpo muda), com e sem WebGL. **Não é experimento:** nenhuma run de pesquisa |
| as dependências reais | o `Mundo` TS com o contrato (já na `main`, com o G-PAR-CONTRATO); o corpo do v11 (na `main`); o evento `deixar_comida` (no motor do mundo, Python e TS). **Não depende da P4 nem do cérebro modular** |
| se o gate falhar | o gate é de engenharia: a paridade, o replay ou o e2e falhando param a entrega até o conserto. Se o cérebro do momento (o A v11) não for à comida com frequência, isso é registrado como comportamento do cérebro, e não bloqueia o MVP: o critério é a cadeia funcionar, e a troca do cérebro é de outra tarefa |

## 1. Pergunta

O jogador consegue pôr a comida num lugar escolhido do cenário, e o pet do jogo perceber, ir, comer e sentir no corpo, com tudo no log e
no replay?

## 2. Depende de

**Na `main`:**
- o `Mundo` TS (`web/app/motor/mundo.ts`), com a percepção, os alvos, o andar, o comer e o `deixarComida` (`mundo.ts:758`), e as chaves do
  contrato da P4 (etapas 1 e 2; `test/contrato.test.ts`);
- o corpo do v11 (`MotorCorpo` em TS);
- a cena 3D da Tela Pet (`src/telas/pet/cena3d.ts`) e a reserva (`CenarioPet.tsx`).

**Decisões:** as MV-1 a MV-6.

## 3. Mudança mínima (PROPOSTA)

1. **Uma versão de pet nova** (MV-1), o v11 com o mundo:
   - o laço do pet do jogo passa a ter o `Mundo`;
   - o v11 continua igual, byte a byte.
2. **O evento de comida com lugar no log do jogo:**
   - `deixar_comida(tipo, x, y)`, com o replay;
   - o motor valida (dentro do mapa, sem obstáculo) e falha alto se não valer.
3. **O cérebro do momento no mundo** (MV-2):
   - o A v11 escolhe a ação (comer, explorar);
   - o alvo é o padrão do motor (a comida boa mais perto ou o cheiro), como no J1 sem o alvo aprendido;
   - o A do TS não ganha as chaves do mundo nesta tarefa.
4. **A consequência no corpo:**
   - comer no mundo chega ao corpo do v11 pelo estímulo de consumo, como no Python (`estimulo_consumo_mundo`);
   - a etapa 1 confere o que o TS já tem e porta o que falta, com G-PAR.
5. **A tela:**
   - **o gesto:** arrastar a comida e soltar no chão da cena 3D (o ponto da vista vira a célula do motor);
   - **o caminho acessível:** escolher a comida e depois o lugar por toque ou teclado (MV-4);
   - **o botão "Alimentar"** continua como reserva temporária, pondo a comida no comedouro (o lugar padrão do `DonoComLugar`).
6. **A cena segue o motor:**
   - a cena 3D e a reserva desenham o pet e os objetos nas posições do motor, interpoladas;
   - a vista só lê;
   - a câmera e a interpolação ficam fora do log.

**O que NÃO muda:** o `engine.py`; o cérebro A; os pets v1 a v11; o Python de pesquisa, salvo os gabaritos novos.

## 4. Experimento e gate

**Não há run.** Os gates são de engenharia:

| gate | o que confere |
|---|---|
| G2 | o v11 sem o mundo sai como hoje (a assinatura do replay contra um gabarito gravado antes) |
| G1 | a vida com a versão nova se refaz do log, bit a bit |
| G-PAR | o laço do pet com o mundo (comer, andar, o corpo) contra um gabarito do Python, decisão a decisão |
| G-EVENTO | o `deixar_comida` inválido falha alto; o evento desconhecido falha alto |
| E2E-COMIDA | pôr a comida, o pet anda até ela, come, e a fome cai, com e sem WebGL |
| E2E-CENA | a posição desenhada segue a do motor |

## 5. Entrega

- **Os testes:**
  - em `web/app`: `npm test`, `npm run tipos`, `npm run e2e`;
  - no Python: os testes dos gabaritos novos;
  - a contagem vai no corpo do PR.
- **As capturas:** de 390, 360 e 1280 px, com o sprite de reserva.
- **O registro:** em `docs/registro/AAAA-MM.md` e no índice. O resumo vai na seção 9 desta tarefa.

## 6. Fora desta tarefa

- o cérebro modular e as chaves do mundo no A do TS (alvo aprendido, planejador);
- as frutas do paladar no jogo (a CA-1 do #399, aqui a MV-3);
- objetos além da comida (a bola, brinquedos);
- dois pets e qualquer coisa online;
- o lugar da comida como pergunta de pesquisa (a CA-2 do #399: a pergunta do dono está encerrada).

## 7. Critérios de aceitação

- O jogador põe a comida num lugar pelo gesto e pelo caminho acessível. O evento entra no log, e recarregar a página refaz a vida.
- No e2e, o pet percebe a comida, anda até ela e come, e o receptor da fome cai, com a cena 3D e com a reserva.
- O v11 sem a versão nova sai igual ao gabarito.
- O G-PAR do laço com o mundo passa.
- **O botão "Alimentar" sem lugar** fica descrito na tela e na tarefa como reserva temporária, e não como a interação planejada.

## 8. Precisa do Matheus

Todas PROPOSTAS, com a recomendação primeiro.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **MV-1** | a versão de pet do mundo | **uma versão nova (a próxima livre, v12)**, com o v11 intacto; o cérebro modular fica com a seguinte | pôr o mundo no v11: os saves dos v11 quebram |
| **MV-2** | o cérebro no MVP | **o A v11 do jogo, com o alvo padrão do motor;** a troca pelo modular vem pela tarefa de integração | esperar o modular: o MVP espera a pesquisa de novo. Portar as chaves do mundo do A: trabalho num cérebro que deixa de ser o alvo |
| **MV-3** | quais comidas se arrastam (CA-1) | **só a ração no MVP;** as frutas depois, com o paladar no TS | as frutas já: o paladar no TS (a etapa 5 do corpo) entra no caminho do MVP |
| **MV-4** | o caminho acessível | **escolher a comida e tocar no chão, ou escolher um lugar nomeado (o comedouro, perto, longe) por teclado** | só o arrastar: o celular e o teclado ficam sem caminho |
| **MV-5** | os limites (CA-3) | **os do motor do mundo de hoje** (quantas no chão, amadurecer, apodrecer); nada novo | inventar limites agora: número novo sem fonte |
| **MV-6** | os textos de "uso pessoal" na tela (`TelaConfig.tsx:184-185`) e nos comentários do atlas | **trocar pelo crédito e pela procedência** (a regra de `docs/UI_GUIDELINES.md`, seção 5.1), junto com a primeira etapa de tela | manter: a tela contradiz a decisão do Matheus sobre os sprites |

## 9. Resumo da etapa

### Etapa 0, os gabaritos (worker D, 2026-10-24)

- **Num commit próprio, antes de qualquer mudança de código,** e sem mecânica nem chave nova. As MV-1 a MV-6 continuam com o Matheus.
- **No TS** (`web/app/test/mvp_etapa0.test.ts` → `web/app/test/gabaritos/mvp_etapa0_ts.json`), o G2 do MVP:
  - **as vidas do jogo:** três pets v11 de hoje (as sementes 101, 202 e 303), com o dono de roteiro do `pet_v11.test.ts` e um dono mais
    calmo. Cada uma tem o log inteiro e, num replay incremental, a assinatura (sha256) a cada 25 eventos e no fim, com o estado interno do
    cérebro A;
  - **as vidas do `lobos_v11.test.ts` e as do laço:** o sha256 dos gabaritos do Python que o G-PAR do v11, do mundo, do contrato e do MVP
    leem (8 arquivos).
- **No Python** (`experiments/exportar_gabarito_mvp_mundo.py` → `web/app/test/gabaritos/mvp_mundo_python.json`, conferido por
  `tests/test_gabarito_mvp_mundo_web.py`), o gabarito do laço para o G-PAR da etapa 1:
  - quatro vidas de 3 dias do pet com o corpo do v11 no mundo físico de hoje, com o dono com lugar: três com o cérebro A do v11 (sem as
    chaves do mundo, o alvo padrão do motor, como a MV-2 recomenda) e uma com o instinto do mundo no mesmo corpo;
  - decisão a decisão, o traço do mundo (a percepção, os candidatos, o alvo, o ocorrido, o estado) e o corpo antes e depois (os
    químicos, os receptores e os estímulos: o andar, a comida, a novidade), mais o log, o resumo e o corpo no fim.
- **Os testes:** o do Python confere o arquivo byte a byte, a cobertura do laço e que gravar não muda a vida; o do TS confere as vidas
  ponto a ponto e os arquivos pinados.
- **Interpretações e achados** em `docs/registro/2026-10.md`.

### Etapa 1, o pet v12 com o mundo (worker D, 2026-10-24)

- **O motor TS e a paridade; a tela é da etapa 2.** O `VERSAO_PET` passa a 12 (MV-1): o laço do corpo do v11 ganha o `Mundo`
  (`web/app/motor/motor_corpo_mundo.ts`, o porte do `com_corpo(MotorMundo)`), e o v11 e os anteriores ficam iguais.
- **O evento `"dc"`** (`deixar_comida`, só a ração, MV-3): com o replay e a validação (fora do mapa, não inteiro, tipo que não é ração,
  malformado e num pet anterior ao v12 falham alto). O botão Alimentar dos v12 põe a ração no comedouro, como reserva temporária;
  nenhum texto de tela mudou. A MV-6 foi decidida no #402 (usar os sprites de Digimon do projeto); a troca dos textos de "uso
  pessoal" pelo crédito e pela procedência é da etapa 2.
- **O laço:** o pet percebe antes de decidir, o comer não dá fome por si (MF-2), e a consequência do mundo vem antes do cérebro. O andar, a
  comida do mapa (com o efeito do alimentar, sem digestão, MV-9), a novidade e a atividade viram estímulos no corpo, com a curiosidade
  (MV-8). O carinho e o tapa ficam fora do mundo (MV-7). O cérebro é o A do v11, com o alvo padrão do motor e sem as chaves do mundo (MV-2).
- **O mundo do produto** (a opção 1 do Matheus, 2026-10-24): o v12 roda o layout padrão sem árvores, só com a ração do jogador
  (`CONFIG_MUNDO_MVP` no `digilab/config.py`, `CMU_MVP` no `motor/constantes.ts`; PROPOSTOS, SEM FONTE). Só o produto o usa: a bancada e a
  pesquisa seguem com o layout padrão, e um teste confere que ele não vaza. O gabarito dele (`mvp_produto_python.json`) entrou num commit
  próprio, antes do código.
- **Os gates:** o G2 (`mvp_etapa0_ts.json` intacto e o teste passando, com o v11 fixado), o G1 (o replay do v12 bit a bit, incremental,
  pelo `Motor.reproduzir` e pelo JSON do save), o G-PAR e o G-EVENTO. O G-PAR é decisão a decisão, com o corpo inteiro e sem campo
  mascarado, em dois cenários: o do produto (`mvp_produto_python.json`, o mesmo cenário nos dois lados) e o da pesquisa
  (`mvp_mundo_python.json`, o gabarito da etapa 0).
- **O achado da fruta:** no Python, o A do v11 quebra quando come uma fruta caída das árvores. A opção 1 tira as árvores do mundo do
  produto, e o A não mudou. Se o layout fica depois do MVP, reavalia-se quando o cérebro modular e as frutas forem especificados
  (nota do Matheus, 2026-10-24).
- **Interpretações e achados** em `docs/registro/2026-10.md`.
