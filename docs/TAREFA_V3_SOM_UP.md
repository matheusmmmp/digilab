# TAREFA V3 — SOM_UP (2026-11-10)

Coordenador e worker: sessão do Gerente da V3 (Claude Code, Opus 5.5). Worktree e branch: `v3-som-up`, sobre o `v3-evolucao-cena`
(PR #770) com a `main` de hoje. Status: ENTREGUE (PR aberto, merge do Matheus).

Categoria: implementacao. Origem: Matheus, 2026-11-10: "implementa o que tem do Digimon Up, segue as suas recomendações ali e depois a
gente planeja o que a gente faz com o Digimon no habitat". A análise e as recomendações SD-1 a SD-8 estão no vault (`20 Temas/Sound design
do jogo.md`).

## 1. Pergunta

O jogo toca o que o acervo do Digimon UP tem de som nos momentos que já existem? São a luta, o treino, o comer, os menus, o nível, a medalha
e a música por lugar. Nó do produto: a experiência básica (`docs/PRODUTO_VISAO.md`, seção 3).

## 2. Depende de

- O PR #770 (o som ligado por padrão e a retomada no primeiro gesto). Este branch sai dele; depois do merge do #770 o PR fica só com o
  SOM_UP.
- A D3 (2026-10-29): os sons e as músicas do Digimon UP seguem a regra dos sprites (`docs/UI_GUIDELINES.md`, 5.1), fora do git e com crédito.

## 3. Mudança mínima

**Fora do git:**

- `Assets/gerar_sons_up.py` ganha duas coisas:
  - os 17 efeitos (`sfx_ui_*`, já em MP3 no remaster);
  - as 14 músicas por lugar, convertidas do WAV do `AudioClip` pelo mesmo `lameenc` a 128 kbps da extração, para o atraso do codificador ser
    o `ATRASO_MP3` de sempre. O início e o laço de cada música vêm da tabela `BGM` do GameData (`Resource`, `Start`, `LoopStart`,
    `LoopEnd`).
- O `mapa.json` passa à versão 2, com `efeitos` e `lugares`. As formas e as 5 músicas da evolução saem iguais.
- `Assets/sons` passa a 189 arquivos, 22 MB.

**No jogo (`web/app/src`):**

- `som.ts` ganha estas peças:
  - os barramentos da música e dos efeitos, por baixo do volume geral;
  - o teto de 4 cópias do mesmo arquivo tocando juntas;
  - `efeito(nome)`;
  - `pedirMusica(fonte, alvo)`: a música é a do pedido mais forte, na ordem evolução > luta > treino = nascimento = jornada > ilha;
  - os volumes da música e dos efeitos;
  - o aviso do mapa antigo.
- `somEventos.ts` (novo): quem sabe do instante emite, e só a casca toca. Os módulos de cena e de regra não importam o áudio.
- `somJogo.ts` (novo): liga os instantes ao `SOM` e pede duas músicas.
  - **A música da ilha** (SD-6) toca só de dia, com o pet nascido, vivo e acordado, num ciclo de 240 s tocando e 90 s em silêncio.
  - **A música do nascimento** toca com o ovo chocando.
- `somLuta.ts` (novo): os sons de cada passo da luta. O projétil que nasce toca o golpe de quem atirou; a habilidade, o golpe dela; o dano, o
  acerto e o fim de quem bateu. Volta o mapa por Digimon, que a LP4 deixou sem chamador.
- Onde cada som entra:

| Onde | Som |
|---|---|
| `lutaPocTela.ts` | os sons do passo; a música do mapa (a de chefe na Liga); o começo; a vitória ou a derrota no fim. O pular não toca o começo de cada luta. |
| `cenaAcao.ts` | o comer, no "comeu a ração" e no começo do laço do comer |
| `TelaTreinar.tsx` | o aparelho de cada exercício e a música do treino |
| `nivelTela.ts` | o nível novo |
| `jogo.ts` | a medalha nova |
| `PainelTela.tsx`, `PainelLugar.tsx` | abrir a cada destino novo e fechar ao sair |
| `Jornada.tsx` | a música do nascimento na escolha do brasão |
| `CenaEvolucao.tsx`, `Revelacao.tsx` | a música da evolução passa pelo pedido com prioridade |

- `TelaConfig.tsx`: os volumes geral, da música e dos efeitos (SD-5), e o resumo do Som corrigido.

**Não muda:** o motor, o log, o save, o replay e a RNG do motor. Nada do som entra no registro, e a variação usa o `Math.random` do app.

## 4. Experimento e gate

Não há run.

## 5. Entrega

`npm run tipos`, `npx vitest run`, os e2e (Playwright), a prévia, e o relato no corpo do PR.

## 6. Fora desta tarefa

O que o Digimon UP não tem:

- o carinho, a bronca, o cocô e o limpar;
- o pegar e o soltar, a bola e o sono;
- o chamado do bebê (o bipe da SD-8);
- a voz por espécie (S7);
- o ambiente da ilha (S5).

Isso fica para o plano do "Digimon no habitat" que o Matheus pediu. Também ficam de fora os Bits e a loja (S6, depois da MO2) e as músicas do
`soundbgm` que não têm lugar no jogo.

## 7. Critérios de aceitação

1. Com o som desligado, nenhuma requisição de áudio sai (o e2e do som, que já existia).
2. Com o mapa da versão 2, três telas pedem o som certo (e2e novo, pulado sem `Assets/sons`):
   - o painel pede `sfx_ui_window_open`;
   - o treino pede `SFX_BGM_training_others`;
   - a luta pede a música do mapa, os `sfx_dm_*` e o `pvp_*`.
3. A ordem das músicas, o teto de cópias, os volumes, o mapa antigo, o ciclo da ilha e os sons do passo da luta têm teste de unidade
   (`test/som_up.test.ts`).
4. O resumo do Som em Ajustes não fala mais de algo que o jogo não faz.

## 8. Precisa do Matheus

- **O merge**, depois do #770.
- **Os números PROPOSTOS** (SEM FONTE):

| Número | Valor |
|---|---|
| volume da música | 0,5 |
| volume dos efeitos | 1 |
| cópias do mesmo arquivo tocando juntas | no máximo 4 |
| ciclo da ilha | 240 s tocando, 90 s em silêncio |

- **Qual arquivo toca em cada evento e qual faixa em cada lugar** (escolha pelo nome do arquivo, sem ouvir). A recomendação é ouvir no jogo e
  trocar o que não servir no `Assets/gerar_sons_up.py`. Errar custa só de ouvido.
