# TAREFA_FRONT_TS — jogo web em TypeScript, com motor separado e teste de paridade

Tirar o jogo web do arquivo único `web/digilab_sprites.html` (≈4.400 linhas: motor, combate,
fala e interface misturados) e levar para um projeto **Vite + TypeScript**, com o **motor puro
separado da interface** e **testes automáticos** que garantem que nada do jogo mudou.

É uma **exceção de escopo** ao `CLAUDE.md` ("não aumentar escopo"), autorizada pelo Matheus em
2026-09-28. Registrar a exceção no `CLAUDE.md` junto das outras.

## 1. Por que, em uma frase

Hoje toda mudança de jogo é espelhada à mão no HTML (`CV`, `CV21`, `CSO`, `CTR`, `CAMPANHA`…),
sem nenhum teste do lado web, e estado de uma tela vaza em outra (ver
`docs/REVISAO_INTERFACE_UP.md`, item 1). A migração troca "espelhar e torcer" por tipos e testes.

## 2. Decisões já tomadas

- **Vite + TypeScript, aplicação estática.** Nada de Next.js: não há renderização no servidor,
  rota de API nem SEO; o motor, o registro e o replay rodam no aparelho, e o
  `servidor/servidor_local.py` continua servindo os arquivos e a rota `/api/fala`.
- **Interface:** Preact (ou Svelte, escolha justificada no plano). **Atualização de 2026-10-19 (decisão do Matheus):** o Preact
  sai e entra o React, com Tailwind, shadcn e lucide, mantendo o Vite e o TypeScript e sem Next.js
  (`docs/TAREFA_V2_FRONT_REACT.md`). Componentes seguem
  `docs/UI_GUIDELINES.md` e o canvas https://claude.ai/artifact/2XHKuofCpCfZeA1N6iVy9g.
- **Testes:** Vitest para unidade e paridade; Playwright só para o teste de fumaça da Etapa 5.
- **Pasta:** `web/app/` (código), saída do build em `web/dist/` (não versionada).
- **O arquivo atual continua funcionando** até a Etapa 6. Durante a migração, os dois convivem.

## 3. Regras (não negociáveis)

1. **Determinismo.** Mesma semente + mesmo registro = mesmo estado, até o último float, no
   motor novo e no atual. O gerador aleatório do web é o **mulberry32** (linha ~1058 do HTML):
   portar exatamente, com a mesma ordem de consumo. Qualquer divergência na paridade para tudo.
2. **Motor sem DOM.** `web/app/motor/` não importa nada de interface, `window`, `document`,
   `localStorage` nem `fetch`. Verificado por teste (lint de imports ou script).
3. **O registro é a verdade.** O estado nunca é salvo; só `{semente, log, versao}` na chave
   `digilab-web-v21-sprites` (e as chaves `-aba`, `-fala-llm`, `-anterior`). Mesmo formato,
   mesma chave: **um save de hoje abre igual no app novo.**
4. **A fala nunca decide nada** (barreiras da `TAREFA_FALA_LIVRE.md` continuam valendo).
5. **Nada de Python muda** além de um exportador de constantes (Etapa 1) em `experiments/` ou
   `tests/`. `digilab/engine.py` continua congelado; o pacote `digilab/` continua só com
   biblioteca padrão.
6. **Sprites de terceiros continuam fora do repositório.** O app carrega o atlas de
   `D:\Trab\digilab\Assets\` pelo mesmo caminho relativo de hoje; o crédito fica no rodapé
   (nota de 2026-10-24: o "uso pessoal" saiu; vale `docs/UI_GUIDELINES.md`, seção 5.1).
7. **Falhar alto.** Evento desconhecido no registro, sprite sem mapa, constante divergente:
   erro visível, nunca valor padrão silencioso.
8. Português nos comentários, sem acento em identificadores (igual ao Python).

## 4. Etapas (parar e mostrar ao fim de cada uma)

### Etapa 0 · Pré-condições e plano (sem código)

- Conferir que o HTML atual roda sem erro e que `motor.assinatura()` existe e cobre o estado
  inteiro (estado, ação, traços, política, evoluções, forma, chamados, sparring, treino…).
- Listar os blocos do HTML e para onde cada um vai (tabela: bloco → módulo TS).
- Listar todos os `localStorage` usados e o formato de cada um.
- Mostrar o plano e a escolha Preact × Svelte. **Parar e esperar aprovação.**

### Etapa 1 · Gabaritos de paridade (antes de portar qualquer coisa)

- **Gabarito do web atual:** um script Node que carrega só o motor do HTML atual (extraído
  por marcação, sem DOM) e, para N sementes × registros sintéticos (todas as ações do dono,
  treino, forçar, lutas de arena e campanha, evoluções até adulto e sombria, pets versão 1,
  2 e 3), grava `assinatura()` em pontos fixos do replay. Saída em
  `web/app/test/gabaritos/*.json`, versionada. Mínimo: 50 sementes, todos os estágios.
- **Constantes do Python:** um exportador grava em JSON os parâmetros de `digilab/config.py`
  que o web espelha. Um teste compara com as constantes do TS e falha em qualquer diferença.
  (Paridade bit a bit com o Python **não** é objetivo: o gerador aleatório é outro. O que se
  garante é que os parâmetros são os mesmos.)
- Parar e mostrar: quantos gabaritos, o que cobrem, e o teste de constantes passando contra o
  próprio HTML atual.

### Etapa 2 · Motor em TypeScript

- Portar para `web/app/motor/`: RNG, estado e necessidades, política (bandit), traços,
  memória por espaços, desejo e obediência, chamados, treino/fadiga/sobrecarga, evolução e
  sombria, combate V2.1 (distância, guts, pesado anunciado, técnicas, passivas, regras de
  combate), campanha, rivais, registro e replay.
- Tipos para eventos do registro (união discriminada), formas, estágios, espécies.
- **Critério de aceite:** 100% dos gabaritos da Etapa 1 iguais; teste de constantes verde;
  teste de "motor sem DOM" verde. Nada de interface ainda.

### Etapa 3 · Esqueleto do app

- Vite, tokens `--dl-*` do guia, fontes, tema claro/escuro, barra de 4 destinos, roteamento
  por destino e sub-aba, leitura e gravação do save (mesma chave), carga do atlas.
- Estado da interface derivado do motor (nenhuma tela guarda cópia própria do estado do pet;
  isso elimina a classe de bug do item 1 da revisão).
- `servidor_local.py`: servir `web/dist/` e incluir as rotas novas em `ROTAS_REMOTAS`, sem
  abrir o resto da pasta no modo remoto.
- Parar e mostrar: app abrindo um save antigo, nos dois temas, em 360 e 1280 px.

### Etapa 4 · Telas

Uma tela por vez, na ordem: Pet → Treinar → Crescer (Aprendizado, Evolução) → Lutar (Arena,
Campanha, palco) → Diário (Registro, Catálogo, Lab) → Meus pets → Primeira vez. Cada uma segue
a prancha correspondente do canvas e o guia, **resolvendo junto os itens da
`docs/REVISAO_INTERFACE_UP.md`** daquela tela. Elementos do desenho sem dado no motor ficam
de fora e vão para a lista de lacunas. Parar ao fim de cada destino com screenshots.

### Etapa 5 · Verificação ponta a ponta

- Playwright: abrir com um save de cada versão (1, 2, 3), navegar pelos 4 destinos, cuidar,
  treinar, forçar, lutar uma vez na arena e uma na campanha; conferir que a assinatura final
  bate com a do HTML atual rodando o mesmo registro.
- Checklist da seção 14 do guia em todas as telas; sem erro no console; sem rolagem lateral
  em 360 px.

### Etapa 6 · Troca

- O `digilab_sprites.html` passa a redirecionar para o app novo (ou vira "versão antiga"
  acessível por link). A regra "sempre aplicar na web" passa a valer para `web/app/`.
- Atualizar `CLAUDE.md` (mapa do repositório, comandos de build e teste) e a memória do
  projeto.

## 5. Relatório final

1. O que foi feito por etapa, arquivos criados e removidos.
2. Paridade: quantos gabaritos, cobertura por estágio e tipo de evento, e confirmação de 100%.
3. Itens da `REVISAO_INTERFACE_UP.md` resolvidos e os que ficaram.
4. Lacunas (elementos do desenho sem dado no motor).
5. Como rodar: `npm run dev`, `npm test`, `npm run build`, e como o servidor local serve o
   build no modo remoto.
