# TAREFA V2 — UP-ATLAS: o atlas com os clipes oficiais do Digimon UP (2026-10-29)

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: a definir. Worktree e branch: `v2-up-atlas`. Status: ABERTA (liberada pelo Matheus em
2026-10-29, com a D3 decidida).

Categoria: implementacao. Origem: Matheus, 2026-10-29: o levantamento `D:\Trab\digilab\remaster\LEVANTAMENTO_INTEGRACAO.md` (fora do
repositório), seção 3, e o prompt de integração da seção 8 dele.

## 1. Pergunta

O jogo web pode tocar os clipes oficiais do Digimon UP (`Idle`, `Run`, `Attack_1`, `Stun`, `Die`, `Evol`), com a duração real de cada
quadro, no lugar do idle recortado a 120 ms fixos, sem mudar nada do motor nem do save? Nó do produto: a apresentação do pet
(`docs/PRODUTO_VISAO.md`, seção 3, "o pet e a cena no navegador, com animação"); não vem de hipótese do `PLANO_V2_PESQUISA.md`.

## 2. Depende de

- Nenhuma frente de código. Decisão D3 do Matheus (procedência dos assets novos) antes de gerar o atlas.
- É a base da UP-EVOLUCAO (o clipe `Evol`) e da UP-ARENA (os clipes da luta).

## 3. Mudança mínima

**A pilha do jogo não muda (Matheus, 2026-10-29):** tudo o que o DigiLab já usa de tecnologia fica como está (Vite 8.3.1, TypeScript
7.0.2, React 19.3.0, Tailwind 4.3.3, three 0.186.1, o Node do `engines` e as demais dependências de `web/app/package.json`, nas mesmas
versões; o Python e a biblioteca padrão no pacote `digilab/`). Nenhuma versão sobe ou desce e nenhuma ferramenta é trocada; as mudanças
desta tarefa são implementadas dentro dessa pilha. O `package.json` e o `package-lock.json` saem iguais, a não ser por dependência nova
aprovada pelo Matheus antes (seção 8).

**Fonte (fora do git), conferida em 2026-10-29:** `D:\Trab\digilab\remaster\export\<Nome>.png/.json`, 280 pares; todo quadro tem
`duration` (33 a 667 ms no Agumon); as tags `Idle`, `Run`, `Attack_1`, `Stun`, `Die` existem nos 280, `Evol` em 90. Há tags que o
levantamento não cita (`Jump` 3, `Fall` 3, `Slide` 3, `Run_Fever` 2): ficam fora. As 60 formas de `Assets/catalogo_sprites_up.json` têm
todas o nome exato de um export; 57 têm `Evol`. O bot `oraculo` (Jijimon) não tem export: segue no atlas atual.

1. **Gerador novo** `D:\Trab\digilab\Assets\gerar_atlas_up_clipes.py` (fora do git, como o `gerar_atlas_up.py`; biblioteca padrão +
   Pillow): lê o catálogo e os exports, empacota por forma, NPC e bot os seis clipes com a duração de cada quadro, e grava
   `Assets/digilab_atlas_up_clipes.png/.json`. Falha alto em forma sem export ou sem `Idle`. As peças de interface continuam vindo do
   atlas atual (não duplicar).
2. **Formato do JSON** (proposta, o worker pode ajustar com registro): `sprites[nome].clipes[clipe] = { quadros: Quadro[], ms: number[],
   loop: boolean }`, mais a `caixa` comum por sprite e a âncora nos pés (UI_GUIDELINES, seção 5).
3. **`web/app/src/atlas.ts`:** `quadroAgora(a, nome, clipe = "Idle")` pela soma das durações; `desenharSprite(..., clipe)`. Chave nova
   desligada `CLIPES_UP` (constante do app, não do motor): desligada, o app carrega `digilab_atlas_up.json` e desenha igual a hoje;
   ligada, carrega o atlas de clipes e usa `Idle` onde hoje é idle. Atlas de clipes ausente com a chave ligada → aviso visível (o mesmo
   caminho de erro de hoje) e nada de cair calado no atlas antigo.
4. **Servir os arquivos novos:** a lista do `web/app/vite.config.ts` e a `ROTAS_REMOTAS` do `servidor/servidor_local.py` (os dois só
   servem arquivos listados; o resto responde 404).
5. **Escala:** as caixas dos exports vão de 75×65 a 225×127 px (personagem + sombra), maiores que o idle atual (até 148×103). Seguir a
   regra de escala inteira: escolher a escala menor que cabe, nunca redimensionar. Conferir o palco de 390 px.
6. **Proposta, sem código:** onde `Run`, `Attack_1`, `Stun` e `Die` entrariam nas telas que já existem (o pet andando na cena do Pet,
   `cena3d.ts` e `PalcoPet.tsx`; a luta, `PalcoLuta.tsx`; a derrota). Vai como tabela no relato, para o Matheus escolher.

**Não muda:** o motor (`web/app/motor/`), o `engine.py`, o pacote `digilab/`, o save, o log, `VERSAO_PET`, a ordem de RNG, o atlas atual
e o gerador atual. Nenhum asset entra no git.

## 4. Experimento e gate

Não há run.

## 5. Entrega

- Testes: `npm test`, `npm run tipos`, `npm run e2e` em `web/app` (o e2e roda com o sprite de reserva; nada dele depende do atlas novo).
  Teste novo de unidade em `atlas.ts`: o quadro certo para um tempo dado, com um JSON de clipes sintético versionado em `test/`
  (sem PNG da Bandai).
- O gabarito "antes": capturas do palco do Pet, da Revelação e da luta com a chave desligada, feitas antes da mudança, e as mesmas
  depois, iguais.
- Registro, relato no PR e seção no fim deste documento, como o modelo manda.

## 6. Fora desta tarefa

Tela nova; ligar `Run`/`Attack_1`/`Stun`/`Die` nas telas (só a proposta); a skin `Invision`; o "respirar" (escala ~4 %, não está nos
quadros); trocar o mapa forma → Digimon; a forma sombria (continua o véu roxo sobre o quadro); remover o atlas antigo.

## 7. Critérios de aceitação

1. `Assets/digilab_atlas_up_clipes.json` tem as 60 formas, os NPCs e os bots com export, cada um com os 5 clipes comuns, e `Evol` nas
   57 formas que o têm; o gerador sai com erro se uma forma do catálogo não tiver export.
2. Com `CLIPES_UP` desligada, as capturas antes e depois são iguais pixel a pixel.
3. Com a chave ligada, o idle de uma forma toca com as durações do JSON (teste de unidade) e o palco de 390 px não corta o sprite.
4. Com a chave ligada e o atlas ausente, a tela mostra o aviso de atlas que não carregou.
5. `docs/UI_GUIDELINES.md`, seção 5 ("idle a 120 ms por quadro"), ganha a nota de que, com a chave ligada, vale a duração do clipe.
6. A tabela de onde entram `Run`, `Attack_1`, `Stun` e `Die` está no relato.

## 8. Precisa do Matheus

- D3 (a procedência dos assets novos), antes de começar.
- Depois da entrega: onde ligar `Run`, `Attack_1`, `Stun` e `Die` (pela tabela), e quando ligar `CLIPES_UP` por padrão. Recomendação:
  ligar o `Idle` por padrão depois de ver as capturas; o custo de errar é baixo (é só apresentação, volta com a chave).

## 9. Decisões tomadas

- **D3 DECIDIDA pelo Matheus (2026-10-29, no chat da coordenação):** os assets novos do Digimon UP (os clipes, as cenas, os sons, as
  músicas e a arte das arenas) seguem a mesma regra dos sprites: `docs/UI_GUIDELINES.md`, seção 5.1, com a procedência registrada, fora do
  git, com o crédito, e o e2e sem eles.
- **A pilha não muda** (Matheus, 2026-10-29): seção 3.

## 10. O que foi feito (2026-10-29, worker Claude Code, Sonnet 5.5)

- **Gerador** `Assets/gerar_atlas_up_clipes.py` (fora do git) → `Assets/digilab_atlas_up_clipes.png/.json`: 76 sprites (as 60 formas, os NPCs, os
  bots e o `guia` com export), 76 Digimon, 57 formas com `Evol`, 3.380 quadros únicos de 3.858. Sai com erro se forma, NPC ou bot não
  tiver export ou `Idle` (exceções listadas: `bot_oraculo` e `guia`, que seguem no atlas atual). PNG de 2048×13777 (22 MB).
- **`atlas.ts`:** `CLIPES_UP = false`; `quadroDoClipe` (pela soma das durações), `quadroAgora(a, nome, parado, clipe, t0)`,
  `desenharSprite(..., { clipe })`, `juntarClipes`. Desligada, o app não pede o atlas de clipes e desenha como antes. Ligada, atlas de clipes
  ausente ou inválido vira `erro` e o aviso "Atlas de sprites não carregou." (e2e novo, sem assets). `vite.config.ts` e `ROTAS_REMOTAS`
  ganharam só as duas entradas novas.
- **Testes:** `test/atlas_clipes.test.ts` com `test/atlas_clipes_sintetico.json` (sem PNG da Bandai).
- **Critérios:** (1) o gerador cumpre; (2) 42 capturas antes/depois iguais com a chave desligada, `lutar-medalhas` em 1280 só na segunda
  tentativa (registro); (3) teste de unidade, e o palco de 390 px do Pet e a Revelação não cortam o sprite com `?clipes_up=1`; (4) e2e novo; (5) nota
  na `UI_GUIDELINES.md`; (6) a tabela abaixo.
- **Limites vistos com a chave ligada** (ver o registro): as caixas chegam a 298×210, o pet do palco do Pet sai menor (a escala é pela
  altura da caixa) e as silhuetas da árvore de evolução saem pequenas na caixa. Não há capturas da luta: não existe captura estática dela.

### Proposta: onde entram `Run`, `Attack_1`, `Stun` e `Die` (sem código)

| clipe | onde | como | custo |
|---|---|---|---|
| `Run` (loop) | o pet andando na cena do Pet (`cena3d.ts`, `PalcoPet.tsx`), quando ele vai ao comedouro ou ao brinquedo | trocar `Idle` por `Run` enquanto a posição muda; espelhar pelo sentido | baixo; só apresentação |
| `Run` | a luta (`PalcoLuta.tsx`), na aproximação | entre o `q` de início e o primeiro golpe | médio: pede tempo de cena que a luta não tem |
| `Attack_1` (uma vez) | a luta, no golpe de cada lutador | tocar no tick do ataque do log; voltar ao `Idle` | médio: ligar ao evento do log sem mudá-lo |
| `Attack_1` | o brincar e o treino no Pet | uma vez ao acertar o treino | baixo |
| `Stun` (uma vez) | a luta, quando o lutador leva dano | no evento de dano | médio, igual ao ataque |
| `Die` (uma vez, segura o último) | a luta, no KO; o `ModalResultado` da derrota | tocar e parar no último quadro | baixo |
| `Die` | a morte de um pet no Pet, se a mecânica existir | — | não recomendo agora: depende de mecânica |

**Recomendação:** `Run` na cena do Pet e `Die` na derrota primeiro (só apresentação, sem tocar no log); `Attack_1` e `Stun` na luta junto
com a UP-ARENA. **O custo de errar é baixo** (volta com a chave). Decisões do Matheus: onde ligar cada clipe e quando ligar `CLIPES_UP` por
padrão (recomendo o `Idle`, depois de ver as capturas com a chave ligada).
