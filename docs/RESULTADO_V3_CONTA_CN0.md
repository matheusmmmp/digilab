# RESULTADO V3 — CONTA, CN0: a medida do save, as chaves do navegador e o tempo fechado (2026-11-12, Claude Code, Opus 5.5)

**A etapa:** a CN0 do [PLANO_V3_CONTA.md](PLANO_V3_CONTA.md) (seção 10), a primeira da F0 do [ROADMAP_V3_CONTA.md](ROADMAP_V3_CONTA.md).
É uma medida de engenharia, sem servidor e sem tela. Não usa faixa de sementes reservada: as sementes saem de `hashSemente("cn0", ...)`.
O motor (`web/app/motor/`), o formato do save e as versões de pet não mudam. Os perfis do jogador são **PROPOSTOS, SEM FONTE**, porque não
há medida de como as pessoas jogam. Os bytes são medidos, não estimados. O desvio está no `docs/registro/2026-11.md`, seção "CONTA: a CN0"
(D-CONTA-34 a D-CONTA-38).

**Para refazer:**

```bash
cd web/app && node scripts/medir_cn0_save.ts
```

O comando grava `web/app/scripts/medicoes/cn0_save.json` (versão da medida 1). O teste fica em `web/app/test/medir_cn0_save.test.ts`.

## 1. O tamanho do save por dia de jogo

**Como foi medido.** O script `web/app/scripts/medir_cn0_save.ts` grava as vidas no Node:
- **o pet de um só** é o `Motor` da versão dos ovos novos (v35), com o `ligarProduto` do jogo;
- **o grupo dos dois pets** é o `GrupoDoJogo` da `VERSAO_GRUPO` (v36), como o `chocarDoisOvos`;
- **o dono** é o dos Cenários (`criarDono`), com as ações do dono dos v11 em diante. Trata a lesão, treina, luta na arena e tenta um líder
  por dia;
- **a TV** são eventos `"st"`, pela mesma porta do `cerebroTv.ts` (`sentidoTela`);
- **no fim de cada dia**, o Tamer confere o que o pet fez com as funções do jogo (`conferirMedalhas`, `conferirBits`...) e o pet recebe
  as medalhas (`sincronizarPet`).

O texto medido é o que o jogo grava no `localStorage` (`textoSave` e `textoSaveGrupo`), em bytes UTF-8, cru, gzip (nível 9) e brotli
(qualidade 11). Os saves reabrem pelo `lerSave` no fim (o script falha se não reabrirem).

São 18 vidas: 3 perfis, um pet só e o grupo, 3 vidas de 21 dias de jogo cada. Nenhuma morreu. Em 21 dias, os pets chegam ao Rookie, ao
Champion ou ao Ultimate; as medalhas dos líderes seguram o resto. O JSON foi gravado em 713 s numa máquina com outra run rodando. O `commit` do JSON
(`0e577625`) é a base da `main`, com o script ainda fora do commit.

**Os perfis** (D-CONTA-37, PROPOSTOS, SEM FONTE):

| perfil | o dono | por dia |
|---|---|---|
| **dedicado** | o atencioso, a cada passo de 15 min | 3 treinos, 4 lutas, 30 min de TV |
| **casual** | o relapso, 3 visitas por dia | 1 treino, 1 luta, sem TV |
| **TV longa** | o atencioso | 3 treinos, 4 lutas, 2 h de TV (o pior caso) |

**O save no fim de cada semana** (a média das 3 vidas; `resumo[].porDia` do JSON):

| perfil | dia | eventos | cru | gzip | brotli |
|---|---|---|---|---|---|
| dedicado, um pet | 7 | 1 256 | 35,5 kB | 4,7 kB | 3,5 kB |
| | 14 | 2 507 | 72,8 kB | 9,0 kB | 6,5 kB |
| | 21 | 3 770 | 111,0 kB | 13,1 kB | 9,3 kB |
| dedicado, grupo | 21 | 4 257 | 147,5 kB | 15,8 kB | 11,4 kB |
| casual, um pet | 21 | 495 | 12,9 kB | 2,2 kB | 1,7 kB |
| casual, grupo | 21 | 941 | 29,0 kB | 3,8 kB | 2,9 kB |
| TV longa, um pet | 21 | 13 536 | 399,7 kB | 41,8 kB | 27,4 kB |
| TV longa, grupo | 21 | 14 080 | 490,3 kB | 45,0 kB | 30,0 kB |

**Por dia** (`eventosNovosPorDia` e `bytesNovosPorDiaCru`), o que a sincronização da CN3 mandaria:

| perfil | eventos novos por dia (média; máximo) | bytes novos por dia, cru (média; máximo) | o trecho do dia 21 comprimido sozinho (gzip; brotli) |
|---|---|---|---|
| dedicado, um pet | 179; 252 | 5,3 kB; 7,1 kB | 0,85 kB; 0,68 kB |
| dedicado, grupo | 202; 340 | 7,0 kB; 10,9 kB | 0,98 kB; 0,79 kB |
| casual, um pet | 23; 45 | 0,6 kB; 1,1 kB | 0,24 kB; 0,22 kB |
| casual, grupo | 45; 88 | 1,4 kB; 2,6 kB | 0,36 kB; 0,32 kB |
| TV longa, um pet | 644; 1 159 | 19,0 kB; 35,6 kB | 2,0 kB; 1,4 kB |
| TV longa, grupo | 670; 1 201 | 23,3 kB; 41,7 kB | 2,3 kB; 1,6 kB |

**O que pesa no log** (`vidas[].porTipo`, a vida 0 de cada perfil):
- **o dedicado**, 111 kB: a TV (`"st"`) é 69 % dos bytes, com 2 266 eventos de 34 B. Depois vêm o tempo (`"t"`, 1 018 eventos, 13 kB),
  a comida no chão (`"dc"`), as lutas (`"l"`, 84 eventos de 71 B) e as ações do dono (`"d"`, 194);
- **o casual:** os 277 cuidados (`"d"`) são o que mais pesa, e o tempo quase não pesa (110 eventos). Os avanços seguidos do relógio se
  juntam num `"t"` só, até a próxima ação;
- **a TV longa:** o `"st"` é 82 % dos bytes, com 9 998 eventos.

O evento custa de 26 a 35 B cru (`bytesPorEventoCru`). O brotli fica entre 6 % e 13 % do cru, e o gzip entre 9 % e 17 %; a TV comprime
melhor, porque se repete.

**O Tamer** (`-tamer`, `tamer` por dia) chega a 7 a 19 kB cru num pet de 21 dias, e a 11 a 36 kB no grupo. Quase tudo são os eventos
`"bits"`: o dedicado tem 163 eventos, 159 deles de Bits, mais 3 medalhas e 1 item. Comprime a uns 6 %.

**O pacote da conta** (`pacotes`): o que a primeira sincronização (a tela 3 da CN3) subiria de um jogador de cada perfil:
- o save ativo (a vida 0 de um pet só);
- os guardados (as outras 5 vidas do perfil, 2 de um pet só e 3 grupos);
- Gerações (a vida 0 aposentada);
- o Tamer.

| perfil | save | guardados | Gerações | Tamer | tudo, cru | tudo, gzip | tudo, brotli |
|---|---|---|---|---|---|---|---|
| dedicado | 112 kB | 663 kB | 112 kB | 18 kB | 905 kB | 100 kB | 57 kB |
| casual | 13 kB | 113 kB | 13 kB | 7 kB | 146 kB | 18 kB | 11 kB |
| TV longa | 400 kB | 2 270 kB | 400 kB | 17 kB | 3 088 kB | 304 kB | 167 kB |

**O que isso diz para a CN3** (leitura, não meta):
- **a sincronização por eventos é pequena:** um dia de jogo manda de 0,6 a 23 kB cru (de 0,2 a 1,6 kB em brotli). A CN3 pode mandar o
  trecho novo sem comprimir e comprimir só o armazenado;
- **o armazenado cresce com a TV.** Um jogador com 6 pets de 21 dias e 2 h de TV por dia guarda 3 MB cru no navegador, e 167 kB em brotli
  na nuvem. O `localStorage` tem um limite por origem (da ordem de 5 MB nos navegadores, SEM FONTE neste documento). O pior caso chega
  perto dele antes da conta existir, e essa é uma questão aberta (no relato do PR);
- **o grupo custa de 1,2 a 2,2 vezes o pet de um só,** e não 2 vezes fixo: a TV é do mundo comum (um `"st"` serve aos dois pets), e cada
  evento do grupo leva o id do pet.

## 2. As chaves do navegador, uma a uma

São 37 chaves `CHAVE + "-..."` em `web/app/src/`, mais três fora desse padrão. `CHAVE` é `digilab-web-v21-sprites`, o save do pet ativo,
que vai para a nuvem (é o que a CN3 sincroniza). Na coluna "destino":
- **nuvem**: vai para a nuvem;
- **aparelho**: fica no aparelho;
- **não sai**: nunca deixa o aparelho, nem a pedido.

A coluna "plano" diz o que a tabela 5.4 do plano propunha. "—" quer dizer que o plano não citava a chave.

| # | chave | o que guarda (onde) | plano | destino | por quê |
|---|---|---|---|---|---|
| 1 | `-guardados` | os pets em espera, cada um `{semente, log, versao}` (e `grupo`, `foco` no par); `pets.ts` | nuvem | **nuvem** | são pets do jogador; é a maior parte dos bytes (seção 1) |
| 2 | `-geracoes` | os pais aposentados (`Aposentado`: o save, `ger`, `filho`, `quando`); `heranca.ts` | nuvem | **nuvem** | é a história do jogador |
| 3 | `-tamer` | o registro do Tamer `{versao, log}`: medalhas, itens, título, recordes, Fábrica, Salão, Bits; `tamer.ts` | nuvem | **nuvem** | sem ele o pet perde as medalhas que liberam a evolução (o evento "u") |
| 4 | `-nivel` | os marcos e os cartões vistos do nível do Tamer, em JSON; `nivelTela.ts` | nuvem | **nuvem** | o nível destrava os lugares da ilha. Sem a chave, o aparelho novo entra no piso 4 (P-6), e quem já estava acima perde lugares |
| 5 | `-conclusao-liga` | as sementes dos pets que já viram a conclusão da Liga; `jornada.ts` | nuvem | **nuvem** | é por pet: sem ela, a conclusão toca de novo |
| 6 | `-mitologia` | a chave liga/desliga da mitologia (`"0"`/`"1"`, Ajustes); `mitologia.ts` | nuvem | **aparelho** | é uma preferência de Ajustes como o som e o tema, não um conteúdo. Muda a tabela 5.4 (D-CONTA-35) |
| 7 | `-mitologia-ouvidas` | por pet, o que o oráculo já contou e o enigma decifrado; `mitologia.ts` | nuvem | **nuvem** | o enigma decifrado é progresso do jogo; fica fora do log (D-E1-4) |
| 8 | `-descartados` | os saves que o descarte 6 tirou, até o jogador baixar ou dispensar; `tamer.ts` | nuvem | **nuvem** | são pets do jogador, ainda que antigos |
| 9 | `-descarte` | o marcador da versão do descarte já feito (`"8"`); `tamer.ts` | nuvem | **nuvem**, junto do `-tamer` | um aparelho novo com o Tamer e sem o marcador refaz o descarte (`feito` vira 1) |
| 10 | `-anterior` | o pet do jogador guardado quando ele abre um pet dos Cenários (Diário); `TelaCenarios.tsx`, `MeusPets.tsx` | aberto | **nuvem, como o pet do jogador** | é o pet de verdade enquanto o ativo (`CHAVE`) é um pet de teste. A CN3 sobe o `-anterior` no lugar do ativo e não sobe o pet dos Cenários, como o do laboratório (D-CONTA-34) |
| 11 | `-habitat` | o mapa, a câmera, o controle e o visual da ilha; `habitat.ts` | aberto | **aparelho** | é só vista (o motor não lê). Os mapas Floresta e Cassette só existem no modo dev, e o celular pede outra câmera (D-CONTA-34) |
| 12 | `-viagem` | a "Viagem da câmera" ligada ou desligada; `viagem.ts` | aberto | **aparelho** | é preferência de movimento, como o "reduzir movimento" do sistema (D-CONTA-34) |
| 13 | `-aba` | a última aba aberta (`"destino/aba"`); `save.ts` | aparelho | **aparelho** | estado da tela |
| 14 | `-boas-vindas` | `"1"` depois da primeira visita (o slogan); `App.tsx` | — | **aparelho** | estado da tela |
| 15 | `-abertura` | o pedido da câmera do primeiro dia, uma vez por pet (`{semente, tocada}`); `abertura.ts` | — | **aparelho** | só toca quando o ovo choca; no aparelho novo o ovo já chocou |
| 16 | `-dicas` | os ids das dicas já vistas; `dicas.ts` | aparelho | **aparelho** | a tabela 5.4 já dizia; repetir uma dica é barato |
| 17 | `-dicas-ligadas` | as dicas ligadas ou desligadas; `dicas.ts` | aparelho | **aparelho** | preferência |
| 18 | `-diario-visto` | o tick do último Diário lido (o brilho de novidade), por pet; `objetosIlha.ts` | — | **aparelho** | o pior caso é um brilho a mais |
| 19 | `-tema` | sistema, claro ou escuro; `tema.ts` | aparelho | **aparelho** | preferência de tela |
| 20 | `-pele` | Vidro ou XCOM; `pele.ts` | aparelho | **aparelho** | preferência de tela |
| 21 | `-som` | o som ligado ou desligado; `som.ts` | aparelho | **aparelho** | preferência do aparelho |
| 22 | `-som-volume` | o volume geral; `som.ts` | aparelho | **aparelho** | idem |
| 23 | `-som-vol-musica` | o volume da música; `som.ts` | aparelho | **aparelho** | idem |
| 24 | `-som-vol-efeitos` | o volume dos efeitos; `som.ts` | aparelho | **aparelho** | idem |
| 25 | `-hud` | os painéis abertos na pilha (Estado, Evolução, Ações, Detalhes); `TelaPet.tsx` | aparelho | **aparelho** | o celular e o PC pedem outro arranjo |
| 26 | `-hud-arraste` | o deslocamento do HUD arrastado; `hudPet.ts` | aparelho | **aparelho** | depende do tamanho da tela |
| 27 | `-detalhes-pet` | "Exibir detalhes do pet" (Ajustes); `hudPet.ts` | — | **aparelho** | preferência |
| 28 | `-aviso-v6` | o aviso pendente do descarte dos v1 a v6; `tamer.ts` | aparelho | **aparelho** | um aviso já lido não volta; um pendente aparece só onde o descarte rodou |
| 29 | `-aviso-tr` | o aviso pendente do descarte 6 (`{pets, fabrica}`); `tamer.ts` | aparelho | **aparelho** | idem |
| 30 | `-aviso-poc` | o aviso pendente dos descartes 7 e 8; `tamer.ts` | aparelho | **aparelho** | idem |
| 31 | `-fala-llm` | a voz pela LLM ligada ou desligada; `fala.ts` | não sai | **não sai** | a fala nunca entra no registro do pet (`servidor/CLAUDE.md`) |
| 32 | `-modo-fala` | o modo da fala livre (template, moldura...); `falaLivre.ts` | não sai | **não sai** | idem |
| 33 | `-conversa-nova` | a conversa nova ligada; `falaLivre.ts` | não sai | **não sai** | idem |
| 34 | `-fala-rede` | a fala pela rede ligada; `falaLivre.ts` | não sai | **não sai** | idem |
| 35 | `-lab` | o pet de teste do laboratório `{semente, log, versao}`; `lab.ts` | não sai | **não sai** | o pet de teste nunca se mistura com os do jogador (LAB-2) |
| 36 | `-lab-ligado` | o laboratório ligado; `lab.ts` | não sai | **não sai** | preferência do laboratório |
| 37 | `-lab-fala` | "Fala com conteúdo (teste)"; `lab.ts` | não sai | **não sai** | idem |

**As três fora do padrão `CHAVE + "-"`** (a contagem de 37 do plano não as pegava):

| chave | o que guarda | destino | por quê |
|---|---|---|---|
| `digilab-web-v21-sprites-cerebro` (`cerebro.ts`, escrita por extenso) | o cérebro dos ovos novos (modular ou A) | **aparelho** | é preferência: o ovo grava a escolha no registro ao nascer, e o replay lê o registro |
| `digilab-web-v21-sprites.fala.jsonl` (`falaLivre.ts`, com ponto) | o log de apresentação das falas e da conversa | **não sai** | é o dado mais pessoal do jogo (seção 5.4 do plano) |
| `digilab-gosto-visual-p0:<semente>` (`gostoVisual/gosto.ts`), uma por pet | o gosto aprendido do P0 (a TV), por pet: só o aprendido, sem imagem nem som | **nuvem, junto do pet** | é memória do pet fora do log. Nos pets sem a TV no cérebro (de antes da v32), a reação à TV sai só daqui; sem a chave, o pet "esquece" o gosto ao trocar de aparelho (D-CONTA-36) |

**A tabela 5.4 fica assim:**
- **nuvem:** o save, `-guardados`, `-geracoes`, `-tamer`, `-descarte`, `-nivel`, `-conclusao-liga`, `-mitologia-ouvidas`, `-descartados`,
  o `-anterior` (como o pet do jogador) e o gosto da TV por pet;
- **aparelho:** a tela, o som e o HUD, `-mitologia`, `-habitat`, `-viagem`, `-cerebro`, as dicas, os avisos e as marcas de "já visto";
- **não sai:** a fala e o laboratório.

As duas listas do jogo continuam fora da sincronização: o `-lab` (e o pet dos Cenários, que ocupa a `CHAVE` enquanto há `-anterior`).

## 3. O tempo entre fechar num aparelho e abrir no outro

**O código** (`web/app/src/tempo.ts`, `iniciarTempo`) tem um laço de `setInterval` de 100 ms. A cada passo, ele mede
`dt = min(3600, o tempo real desde o passo anterior)` pelo `performance.now()` e anda `velocidade × dt` minutos de jogo. O primeiro passo
mede desde a hora em que o laço começou. O save `{semente, log, versao}` não tem hora de parede, e nada no app recupera o tempo
fechado (procurei hora de fechar, `visibilitychange`, `pagehide` e recuperação na abertura: não há). A velocidade também não é guardada:
toda abertura começa em 10 min/s.

**A resposta: o pet não envelhece pelo tempo fechado.** Fechar num aparelho e abrir no outro, uma hora ou uma semana depois, devolve o
pet no tick em que ele foi fechado. Só a aba aberta faz o tempo andar, inclusive em segundo plano, porque o `dt` é o relógio real.

**A medida que confirma:**
- **o teste** `web/app/test/medir_cn0_save.test.ts`, "fechado, o pet não envelhece", roda o laço do `tempo.ts` com o relógio na mão:
  3 s abertos (o pet anda), 8 h fechados, o mesmo texto do save aberto noutro armazenamento. O pet abre no mesmo tick e, no primeiro passo
  de 0,1 s, anda no máximo 1 min de jogo;
- **o JSON** (`tempo`): o save reaberto pelo `lerSave` tem o mesmo tick de quando foi fechado e só os campos `semente`, `log` e `versao`
  (`temHoraDeParede: false`).

**O salto de 1 h real só vale com a aba aberta.** Quando o PC dorme com o jogo aberto, o primeiro passo depois do sono anda no máximo 1 h
real na velocidade da hora. O teste "aberto com o PC dormindo 8 h" confere: a 1x, o pet anda 60 min de jogo, não 480. Nas outras
velocidades o salto é grande (o `tempo.saltoPorPasso` do JSON). A 10 min/s, a velocidade com que o jogo abre, o salto é de 36 000 min,
**25 dias de jogo**. O bebê anda minuto a minuto e para no primeiro chamado; do In-Training em diante, o pet anda os 25 dias de uma vez.
Isso não é desta etapa: vai como questão aberta para a CN3 (D-CONTA-38).

**O que muda para a CN3:**
- a nuvem não precisa reconciliar o relógio. O log é a história inteira, e o tick do último evento é a idade do pet;
- se o Matheus quiser que o pet envelheça fechado, isso é mecânica nova, com versão de pet nova, e não é deste plano.
