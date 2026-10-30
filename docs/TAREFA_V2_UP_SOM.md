# TAREFA V2 — UP-SOM: o sistema de áudio do jogo web (2026-10-29)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: a definir. Worktree e branch: `v2-up-som`. Status: ABERTA (liberada pelo Matheus em
2026-10-29, com a D3 decidida).

Categoria: implementacao. Origem: Matheus, 2026-10-29: `D:\Trab\digilab\remaster\LEVANTAMENTO_INTEGRACAO.md`, seções 5 e 6, e o bloco
"sons do jogo" de `remaster/fonte/site/arena.html` (linha ~482).

## 1. Pergunta

O jogo web pode tocar os sons do Digimon UP (golpe, impacto, evolução) sem mudar o motor, desligado por padrão, com volume e liga/desliga
na Configuração? Nó do produto: a experiência básica (`docs/PRODUTO_VISAO.md`, seção 3).

## 2. Depende de

- D3 (procedência dos sons). Nenhuma frente de código: corre em paralelo com a UP-ATLAS.
- A UP-EVOLUCAO e a UP-ARENA usam este sistema; não o contrário.

## 3. Mudança mínima

**A pilha do jogo não muda (Matheus, 2026-10-29):** tudo o que o DigiLab já usa de tecnologia fica como está (Vite 8.3.1, TypeScript
7.0.2, React 19.3.0, Tailwind 4.3.3, three 0.186.1, o Node do `engines` e as demais dependências de `web/app/package.json`, nas mesmas
versões; o Python e a biblioteca padrão no pacote `digilab/`). Nenhuma versão sobe ou desce e nenhuma ferramenta é trocada; as mudanças
desta tarefa são implementadas dentro dessa pilha. O `package.json` e o `package-lock.json` saem iguais, a não ser por dependência nova
aprovada pelo Matheus antes (seção 8).

**Fonte conferida em 2026-10-29:** `remaster/export/sons/` com 734 MP3 (~12 MB; o levantamento diz 13), a planilha
`sons_digimon_up.xlsx` (905 eventos), o mapa por Digimon `remaster/fonte/scripts_sons/sons_arena.json` (265 dos 280 com som; 15 mudos,
lista na seção 6 do levantamento) e as músicas `remaster/fonte/evo/musica/` (5 BGM + `sfx_evolution_sfx`), com início e loop na
constante `MUSICAS` de `evo/index.html`.

1. **Assets (fora do git):** copiar para `D:\Trab\digilab\Assets\sons\` só os MP3 que o mapa usa para as formas, NPCs e bots do DigiLab,
   mais as 5 músicas e `sfx_evolution_sfx`; gerar `Assets/sons/mapa.json` (forma → eventos) por um script fora do git a partir de
   `sons_arena.json` e do catálogo de sprites. Servir pela lista do `vite.config.ts` e do `servidor_local.py`.
2. **`web/app/src/som.ts`** (novo; sem DOM no motor, então fica em `src/`): Web Audio, carregamento preguiçoso, `tocar(evento, forma)`,
   variação como tom (±variação/3, como a arena; o levantamento não sabe se é tom ou volume: registrar como PROPOSTO), música com
   `LoopStart`/`LoopEnd` em amostras a 44,1 kHz. **A aleatoriedade da variação usa `Math.random` do app, nunca a RNG do motor**, e
   nada do som entra no log.
3. **Liga/desliga e volume em `TelaConfig.tsx`:** troca a linha "o jogo ainda não tem som" por um interruptor e um controle de volume,
   lembrados no `localStorage` do app (não no save do pet). Padrão: desligado. O navegador só toca depois de um gesto: ligar o som é o
   gesto.
4. **Onde toca nesta etapa:** só onde o app já tem o instante: a luta atual (`PalcoLuta.tsx`; golpe e acerto pelo que a tela já desenha)
   e a Revelação (`sfx_evolution_sfx`; a música por tipo fica com a UP-EVOLUCAO). Proposta de outros pontos no relato, sem código.
5. Arquivo de som ausente com o som ligado → um aviso visível uma vez e a tela segue; não falha calado.

**Não muda:** o motor TS, o `engine.py`, o log, o save, o replay, a ordem de RNG do motor. O combate não muda de regra nem de tempo.

## 4. Experimento e gate

Não há run.

## 5. Entrega

`npm test` (teste de unidade de `som.ts` com um `AudioContext` falso: o evento certo, a variação dentro da faixa, nada toca desligado),
`npm run tipos`, `npm run e2e` (som desligado; nenhuma requisição de MP3 com o som desligado). Um teste de replay existente continua
passando sem mudança. Registro e relato como o modelo manda.

## 6. Fora desta tarefa

As outras 56 faixas do `soundbgm`; os 194 sons sem instante conhecido (interface, gacha); a música por tipo de evolução (vai com a
UP-EVOLUCAO); som na arena em tempo real (vai com a UP-ARENA); reaproveitar o código colado da arena (reaproveita-se a lógica).

## 7. Critérios de aceitação

1. Com o som desligado (padrão), nenhuma requisição de áudio sai (e2e) e a vida refeita pelo log é igual (o teste de replay).
2. Ligado, um golpe da luta atual toca o som do mapa daquela forma (teste de unidade com o mapa sintético).
3. O volume e o liga/desliga sobrevivem a recarregar a página e não aparecem no save exportado.
4. Os 15 Digimon mudos e as formas sem som ficam listados no relato; tocar evento sem som não levanta erro (é silêncio esperado).
5. Arquivo ausente com o som ligado mostra o aviso.

## 8. Precisa do Matheus

- D3, antes de começar.
- A variação como tom ou volume: recomendação, tom, como a arena (o custo de errar é só de ouvido).

## 9. Decisões tomadas

- **D3 DECIDIDA pelo Matheus (2026-10-29, no chat da coordenação):** os assets novos do Digimon UP (os clipes, as cenas, os sons, as
  músicas e a arte das arenas) seguem a mesma regra dos sprites: `docs/UI_GUIDELINES.md`, seção 5.1, com a procedência registrada, fora do
  git, com o crédito, e o e2e sem eles.
- **A pilha não muda** (Matheus, 2026-10-29): seção 3.

## 10. Relato da etapa (2026-10-29, worker UP-SOM, Claude Code, Sonnet 5.5, worktree `v2-up-som`)

**O que entrou:**
- `web/app/src/som.ts` (novo): Web Audio sem biblioteca, `criarSom(dep)` com dependências injetáveis e a instância `SOM`; `tocar(evento, forma,
  habilidade)`, `tocarEvolucao`, `tocarMusica` (início e laço em amostras a 44,1 kHz, `ATRASO_MP3` 1105), carregamento preguiçoso do `mapa.json` e dos
  MP3, aviso uma vez (`AvisoSom`) quando falta arquivo. Desligado, não cria contexto nem pede arquivo.
- Configuração: a seção SOM (interruptor e volume) troca a linha "o jogo ainda não tem som". Lembrados em `localStorage`
  (`digilab-web-v21-sprites-som` e `-som-volume`), fora do save.
- Luta (`luta.ts`, `somDoTurno`): quem fez `golpe_rapido`, `disparo` ou `pesado` toca o golpe da forma dele; quem causou dano toca o acerto e o fim.
  Disparo e pesado usam o conjunto de habilidade; o golpe rápido, o de ataque. Pular a animação não toca.
- Revelação: `tocarEvolucao(0)` (a queda do `sfx_evolution_sfx`, a partir de 15,45 s: a Revelação do app abre já no instante da virada).
- Servidor: `vite.config.ts` e `servidor_local.py` servem `/Assets/sons/mapa.json` e `/Assets/sons/<nome>.mp3` (nome simples, sem caminho), também no modo remoto.
- Fora do git: `D:\Trab\digilab\Assets\gerar_sons_up.py` gera `Assets/sons/` (150 MP3 de golpe + 5 músicas + `sfx_evolution_sfx`, 8,9 MB) e o `mapa.json`.
  Procedência: UI_GUIDELINES 5.1 (D3).

**Não mudou:** motor, `engine.py`, save, log, RNG do motor, `package.json` e lockfile (`npm ci` só instalou).

**Cobertura do mapa (critério 4):** 75 chaves de sprite com som. Sem som: `brasa_adulto_vigia` (Wargrowlmon), `oraculo` (Jijimon) e `guia` (Agu).
Dos 15 Digimon mudos do levantamento (seção 6), só o Wargrowlmon está no catálogo de sprites do DigiLab (`brasa_adulto_vigia`); `oraculo` (Jijimon) e `guia` (Agu)
não estão no mapa de sons do protótipo. Os outros 14 mudos não aparecem em nenhuma forma, NPC ou bot do DigiLab (conferido contra `catalogo_sprites_up.json`).
Tocar forma sem som é silêncio, sem erro (teste de unidade).

**Testes:** `npm test` 621 passados (53 arquivos; `som.test.ts` com 9 novos); `npm run tipos` limpo; `tests/test_servidor_remoto.py` 13 passados;
`npm run e2e` 93 passados (2 novos de som).

**PROPOSTOS (SEM FONTE):** volume padrão 0,6 ao ligar; variação como tom de ±variação/3 (como a arena; o custo de errar é só de ouvido);
disparar `fim` junto do acerto.

**Propostas de outros pontos, sem código:** estalo ao comer e ao receber o carinho (efeitos de interface, hoje sem instante mapeado); fanfarra na
medalha; música de fundo por estágio na Pet; os 194 sons de interface/gacha quando houver o instante.
