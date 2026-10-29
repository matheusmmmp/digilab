# TAREFA V2 — UP-EVOLUCAO: a cena oficial de digievolução na Revelação (2026-10-29)

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: Claude Code (Opus 5.5). Worktree e branch: `v2-up-evolucao`. Status: A TELA ENTREGUE, à espera do Matheus (a etapa 0 na seção 10, decidida na seção 9; a tela na seção 11; liberada em 2026-10-29)
(D3 e D4 decididas; a UP-ATLAS na `main`, #441).

Categoria: implementacao. Origem: Matheus, 2026-10-29: `D:\Trab\digilab\remaster\LEVANTAMENTO_INTEGRACAO.md`, seção 5, e o protótipo em
`D:\Trab\digilab\remaster\fonte\evo\` (publicado em https://claude.ai/artifact/ULZ6H5m8YJFWigyrJTNWm3).

## 1. Pergunta

A Revelação (`web/app/src/componentes/Revelacao.tsx`) pode tocar a cena oficial de digievolução do UP, com o pet da forma nova, sem mudar
a regra de evolução nem o que a tela mostra do motor? Nó do produto: a evolução (`docs/PRODUTO_VISAO.md`, seção 3, "treino, crescimento,
batalha e evolução").

## 2. Depende de

- UP-ATLAS na `main` (o clipe `Evol` e o atlas de clipes, para a reserva sem cena).
- D3 (procedência) e D4 (as linhas oficiais só como referência visual).
- UP-SOM é independente: a música e o efeito sonoro desta etapa entram só pelo sistema de áudio dela. Se a UP-SOM não estiver na `main`,
  esta etapa vai sem som e deixa o gancho.

## 3. Mudança mínima

**A pilha do jogo não muda (Matheus, 2026-10-29):** tudo o que o DigiLab já usa de tecnologia fica como está (Vite 8.3.1, TypeScript
7.0.2, React 19.3.0, Tailwind 4.3.3, three 0.186.1, o Node do `engines` e as demais dependências de `web/app/package.json`, nas mesmas
versões; o Python e a biblioteca padrão no pacote `digilab/`). Nenhuma versão sobe ou desce e nenhuma ferramenta é trocada; as mudanças
desta tarefa são implementadas dentro dessa pilha. O `package.json` e o `package-lock.json` saem iguais, a não ser por dependência nova
aprovada pelo Matheus antes (seção 8).

**Fonte conferida em 2026-10-29:** `remaster/fonte/evo/` tem `index.html`, `linhas.json` (15 linhas), `cenas/` (6: adventure, zero2,
tamers, tamers_mega, jogress, dramon; 6 MB), `digimon/` (90 esqueletos; 18 MB), `musica/` (6 MP3), `musica_wav/` (5). O protótipo usa
`spine-webgl@4.2.120` (iife). Das 60 formas do DigiLab, 57 estão nas linhas oficiais e têm `Evol`.

1. **Etapa 0, as cenas em quadros (antes de código de tela):** pela regra da pilha, o caminho padrão é **converter as cenas em quadros**
   com `spine_quadros.py` (fora do git) e tocá-las com o canvas 2D que o app já usa; o runtime Spine (`@esotericsoftware/spine-webgl`)
   seria dependência nova e só entra se o Matheus aprovar antes. Medir e trazer: o peso em disco das cenas em quadros, o tempo de carregar
   e tocar uma cena no celular de referência dos Gates A e B, e a fidelidade contra o protótipo (as cenas usam mistura e alfa direto; os
   Digimon são pré-multiplicados; o que a conversão perder, listado com captura lado a lado). Se a fidelidade não servir, a etapa para e
   leva ao Matheus a alternativa do runtime, com o peso e a licença dele (a Spine Runtimes License pede licença do editor). **Parar e
   mostrar.**
2. **Assets (fora do git):** copiar para `D:\Trab\digilab\Assets\evolucao_up\` as cenas, os esqueletos das formas do DigiLab (não os 90 se
   só 57 servem) e um mapa `forma → (cena, esqueleto)`. Servir pela lista do `vite.config.ts` e do `servidor_local.py`.
3. **Escolha da cena:** pela `EvolutionAction` da linha oficial do Digimon da forma nova (`linhas.json`): Adventure/Adventure02 →
   adventure/zero2, Tamers → tamers, TamersMega → tamers_mega, Jogress → jogress, Dramon → dramon. Forma sem linha (3) ou sem cena →
   o clipe `Evol` do atlas de clipes com o efeito `Levelup_0_Partner`; sem `Evol` → a Revelação de hoje.
4. **Na Revelação:** a cena toca antes do cartão, puxável ("Pular") e com `prefers-reduced-motion` respeitado (vai direto para a
   Revelação de hoje). Notas técnicas do levantamento: as cenas com `premultipliedAlpha=false`, os Digimon pré-multiplicados; o pet
   preso ao osso `AAA_Digimon` (Jogress: `AAA_DigimonL`/`R`, e aqui só há um pet: usar o `L` e registrar); cenas sem Flash usam o
   Flash/Loop da Adventure; a sombra (slot `Shadow`) não é desenhada.
5. **Chave desligada** `CENA_EVOLUCAO_UP` no app: desligada, a Revelação de hoje, igual.
6. A forma sombria: a cena com o véu roxo do atlas no pet, ou a Revelação de hoje; proposta do worker, decisão do Matheus.

**Não muda:** `digilab/evolucao.py`, as regras de evolução do motor TS, o log, o save, `VERSAO_PET`, o "O que decidiu" da Revelação
(continua vindo do motor). A evolução do UP (nível, pontos, linhas) não entra como regra.

## 4. Experimento e gate

Não há run. A etapa 0 é medida de engenharia, com o roteiro de medição no relato.

## 5. Entrega

`npm test`, `npm run tipos`, `npm run e2e` (o e2e com a chave desligada e sem os assets, como hoje; um teste de unidade para o mapa forma
→ cena com dados sintéticos). Capturas antes e depois com a chave desligada, iguais. Um vídeo curto ou capturas da cena com a chave
ligada, no celular e no desktop. Registro e relato como o modelo manda.

## 6. Fora desta tarefa

Mudar a regra de evolução; a evolução por Jogress com dois pets; a skin `Invision`; o resto de `timeline_assets_all`; a tela de árvore de
evolução (`TelaEvolucao.tsx`) além do "rever" que já abre a Revelação; o som se a UP-SOM não estiver pronta.

## 7. Critérios de aceitação

1. A etapa 0 traz as cenas em quadros com o peso, o tempo e a comparação lado a lado com o protótipo; o `package.json` não muda.
2. Com a chave desligada, a Revelação é igual à de hoje (capturas e e2e).
3. Com a chave ligada, cada uma das 6 cenas toca com pelo menos uma forma do DigiLab, e a forma sem linha cai na reserva `Evol`.
4. Asset ausente com a chave ligada → aviso visível e a Revelação de hoje, não tela preta.
5. Movimento reduzido e "Pular" levam direto ao cartão.

## 8. Precisa do Matheus

- Depois da etapa 0: se os quadros servem. Só se não servirem, a dependência nova do runtime Spine (com o peso e a licença), que a regra
  da pilha não deixa entrar sem o sim do Matheus. O custo de errar é retrabalho da tela (a escolha da cena serve aos dois).
- A forma sombria na cena (item 6).

## 9. Decisões tomadas

- **D3 DECIDIDA (Matheus, 2026-10-29):** os assets novos seguem a regra dos sprites (`docs/UI_GUIDELINES.md`, seção 5.1).
- **D4 DECIDIDA (Matheus, 2026-10-29, "siga as recomendações"):** as linhas oficiais do UP ficam só como referência visual (escolher a
  cena e a música); as regras de evolução do DigiLab não mudam.
- **A pilha não muda** (Matheus, 2026-10-29): seção 3.
- **As quatro da etapa 0 DECIDIDAS (Matheus, 2026-10-29, no chat da coordenação, "aceitou as quatro recomendações"; relatadas pelo
  coordenador):**
  1. os quadros servem, com a frente separada por trecho da ordem de desenho;
  2. o formato: 650×500, 30 quadros/s, WebP q80;
  3. o Digimon segue o osso fora da escala inteira só durante a cena, com vizinho mais próximo; o cartão continua a 4×. É exceção à seção 5
     do `docs/UI_GUIDELINES.md`, com a nota lá;
  4. a medida no celular de referência vai junto com o e2e da tela.

## 10. Relato da etapa 0 (2026-10-29, worker UP-EVOLUCAO, Claude Code, Opus 5.5, worktree `v2-up-evolucao`)

Sem código de tela. Tudo o que a etapa produziu está fora do git, em `D:\Trab\digilab\Assets\evolucao_up\etapa0\` (procedência:
UI_GUIDELINES 5.1, D3). Os números abaixo saem de `analise/resumo.json`, `analise/por_quadro.json`, `analise/trechos.json`,
`analise/trechos_peso.txt`, `analise/peso_total_q80.txt`, `analise/bancada_desktop.json` e `analise/runtime_spine.txt`, nessa pasta; as
ferramentas que os produzem estão em `ferramentas/`.

**O `spine_quadros.py` não serve para as cenas.** Ele foi feito para os Digimon (pixel art em `region`, vizinho mais próximo, ignora
rotação abaixo de 1° e escala a menos de 10%, sem mistura). As cenas têm malhas (`mesh`, até 120 por cena), recorte (`clipping`),
restrições de caminho e de transformação, mistura aditiva (de 23 a 279 slots por esqueleto), tinta de duas cores e textura com filtro
linear. Rodado só no fundo da Tamers: 268 quadros numa caixa de 3844×2710, 357 cels por quadro, 75.316 PNGs, 409 MB, e o recorte
ignorado (`spine_quadros_tamers_back/`). Como formato de entrega, não serve.

**A conversão que serve: os quadros rasterizados pelo próprio runtime, fora do jogo.** Uma página de captura
(`ferramentas/captura.html`, com o `spine-webgl` 4.2.120 do CDN, como o protótipo) repete a sequência e o encaixe do protótipo a passo
fixo de 1/30 s e grava, por quadro, três camadas: o fundo (`back`, opaco), a frente só com os slots normais (RGBA, por fosqueamento
preto/branco) e a frente só com os aditivos (sobre preto, para somar com o `lighter` do canvas 2D). O Digimon fica fora das camadas: no
jogo ele é o sprite do app, entre o fundo e a frente, na posição do osso `AAA_Digimon`, que a captura grava por quadro (`meta.json`).
Cada cena tem a Summon (12,33 s; 15,03 s na Adventure) e a revelação, o Flash e 5 s do Loop da Adventure (10 s). Resolução 650×500
(metade da câmera de 1300×1000 do protótipo), 30 quadros/s, WebP com perda.

| cena | quadros | peso q80 (MB) | peso q60 (MB) | fundo no q80 (MB) | PSNR q80 mediana / mín. (dB) | quadros com erro de ordem* |
|---|---|---|---|---|---|---|
| adventure | 752 | 12,05 | 9,62 | 7,42 | 40,23 / 27,91 | 1/151 |
| zero2 | 671 | 9,34 | 7,18 | 6,55 | 39,78 / 27,02 | 9/135 |
| tamers | 671 | 10,94 | 8,25 | 8,06 | 39,59 / 27,30 | 22/135 |
| tamers_mega | 671 | 9,42 | 6,96 | 8,04 | 40,43 / 33,78 | 1/135 |
| jogress | 671 | 7,32 | 5,61 | 5,62 | 41,14 / 35,40 | 0/135 |
| dramon | 671 | 8,36 | 6,56 | 5,93 | 41,14 / 27,77 | 9/135 |

\* quadros amostrados (1 em 5) com mais de 1% dos pixels a mais de 32 níveis do runtime, com as camadas sem perda.

- **Peso:** de 7,3 a 12,1 MB por cena no q80. O trecho da revelação sai byte a byte igual nas cinco cenas que passam para a Adventure
  (e quase igual na própria Adventure): guardado uma vez, as seis cenas somam 35,7 MB no q80. Uma evolução baixa só a cena dela. O fundo
  é de 62% a 85% do peso.
- **Fidelidade:** a galeria `analise/galeria_lado_a_lado.png` põe o protótipo e os quadros q80 lado a lado, um quadro por cena antes e
  outro na revelação, e não há diferença visível; as capturas `analise/lado_*_q80_*.png` trazem também a diferença ×4. Duas perdas:
  - **a ordem da frente.** Ela alterna normal e aditivo de 5 a 11 vezes na ordem de desenho, e com três camadas o aditivo de baixo sai
    por cima do normal (o casulo de dados da Tamers aos 8–12 s, os rastros da Zero2 e da Dramon aos 0–3 s; `analise/pior_dramon_0035.png`).
    **Separar a frente por trecho da ordem de desenho resolve:** nos recortes recapturados, PSNR mínimo de 61,7 dB e nenhum pixel a mais
    de 32 níveis, com a frente de 0% a 21% mais pesada e até 4 camadas de frente não vazias por quadro;
  - **a compressão:** o q80 fica em ~40 dB de mediana, e o q60 em ~38–40 dB.
  - Duas camadas só (o fundo e a frente inteira somada) não servem: o clarão branco do Flash cobre até 100% dos pixels errados.
- **Carregar e tocar (desktop, não o celular):** a bancada do `analise/tocador.html` decodifica e compõe a cena inteira, 4 quadros em
  voo, e sustentou de 64 a 160 quadros/s (30 pedidos), com 2–7 ms de decodificação por imagem na mediana e o primeiro lote em 7–15 ms
  (servidor local, com as análises rodando ao mesmo tempo). O protótipo, com o runtime, carregou a cena e os dois Digimon em 93–834 ms
  no mesmo desktop. **O celular de referência dos Gates A e B não foi medido:** o worker não tem um (como na M3). Roteiro para o Matheus:
  na pasta `analise`, rodar `python -m http.server 8767 --bind 0.0.0.0`, abrir `http://<ip do PC>:8767/tocador.html` no celular, tocar
  cada cena a 30 quadros/s e 3 camadas e anotar `carga_primeiro_quadro_ms`, `desenhados` e `atrasados` (atrasado = quadro que não ficou
  pronto a tempo). Com a rede, a cena pede ~0,5 MB/s enquanto toca (10,9 MB em 22,4 s na Tamers); por isso o app deve baixar a cena antes.
- **O Digimon na cena não fica em escala inteira.** O osso escala o pet: de 1,2 a 1,39 sobre o 4,2 do protótipo (≈5,0× a 5,8×) em cinco
  cenas, e de 0 a 4 na Tamers Mega (o pet cresce do nada). A regra da seção 5 do UI_GUIDELINES pede escala inteira, 4× na revelação.
- **A alternativa do runtime (não instalada):** `@esotericsoftware/spine-webgl` 4.2.120, 221.638 bytes minificado (67.009 com gzip),
  depende do `spine-core` 4.2.120; as cenas ficam em 6 MB (os seis `back`/`front`/atlas/PNG). A licença é a Spine Runtimes License: integrar
  o runtime pede licença do editor Spine (a seção 2 da licença do editor, ou "cada usuário do produto obtém a própria licença do editor"),
  e a redistribuição leva o aviso. A fidelidade é a do protótipo (é a referência).
- **Uma nota de licença também nos quadros:** a ferramenta de captura usa o mesmo runtime, fora do jogo, como o protótipo já usa. Se
  isso entra na licença da Spine, não sei (SEM FONTE); o jogo não levaria o runtime.

**Recomendação do worker:** os quadros servem. Com a frente por trecho, a fidelidade é a do runtime (fora a compressão), a pilha não
muda e o desktop sobra. O custo é o peso: cerca de 10 MB por evolução e ~36 MB no servidor, e o celular ainda sem medida. **Decisões
pedidas ao Matheus** (todas PROPOSTAS; o custo de errar é refazer a conversão, que roda sozinha em cerca de 1 h de captura para as seis cenas):
1. **Os quadros servem?** Recomendação: sim, com a frente por trecho. Errar aqui custa retrabalho da tela (a escolha da cena serve aos dois).
2. **Formato:** 650×500, 30 quadros/s, WebP q80 (PROPOSTOS, SEM FONTE). O q60 tira de 20% a 25% do peso com 1,3 a 1,5 dB a menos; 15 quadros/s tiram
   metade, mas os efeitos ficam aos saltos.
3. **O Digimon segue o osso fora da escala inteira** (vizinho mais próximo, sem suavizar) durante a cena, ou arredonda para a escala
   inteira mais próxima e perde o crescimento contínuo da Tamers Mega. Recomendação: seguir o osso só durante a cena, como desvio
   registrado da seção 5; o cartão da Revelação continua a 4×.
4. **A medida no celular de referência** (roteiro acima), antes da etapa de tela, ou junto com o e2e dela.

## 11. Relato da tela (2026-10-29, worker UP-EVOLUCAO, Claude Code, Opus 5.5, worktree `v2-up-evolucao`)

**O que entrou (seção 3, itens 2 a 6):**
- `web/app/src/evolucaoUp.ts` (novo): a chave `CENA_EVOLUCAO_UP`, desligada; a escolha da cena pela forma nova (`escolherCena`); a
  sequência Summon + revelação (`sequencia`); o quadro do pet no clipe (`quadroDigimon`: o `Evol` não repete e segue no `Idle`, e sem o
  atlas de clipes vale o `Idle` do atlas atual); o centro do corpo e o lugar do pet no osso (`centroDoCorpo`, `lugarDigimon`); e a carga
  do mapa e dos quadros, que falha alto.
- `web/app/src/componentes/CenaEvolucao.tsx` (novo): a cena no canvas 2D. Baixa os dois pacotes da cena (a Summon e a revelação) antes de
  tocar, com "carregando a cena… N%", e decodifica numa janela de 20 quadros. Espera o atlas, se a Revelação abrir antes de ele chegar. Desenha o fundo, depois o pet do app no osso (com vizinho mais próximo, fora da
  escala inteira: decisão 3), depois a frente por trecho: o aditivo com `lighter` e o normal por cima. O relógio só anda com o quadro
  pronto. Toca a música da linha e o `sfx_evolution_sfx` com a queda na revelação, pelo `src/som.ts`. Tem o "Pular".
- `Revelacao.tsx`: com a chave ligada e sem movimento reduzido, a cena abre antes do cartão. No fim, no "Pular" ou com o erro, vem o
  cartão de hoje. Asset ausente dá um aviso visível ("A cena da evolução não tocou: …") e cai no cartão. Com a chave desligada, o código
  segue o caminho de hoje.
- `atlas.ts`: o véu da forma sombria (`quadroSombrio`) passa a ser exportado, para a cena usar o mesmo.
- O servidor: o `vite.config.ts` e o `servidor_local.py`, também no modo remoto, servem só `/Assets/evolucao_up/mapa.json` e
  `/Assets/evolucao_up/pacotes/<nome simples>.bin` (`tests/test_servidor_remoto.py`).
- Fora do git, em `D:\Trab\digilab\Assets\`:
  - o que o jogo serve: `evolucao_up/pacotes/` (7 pacotes, 34,5 MB: os WebP dos quadros, um atrás do outro) e `evolucao_up/mapa.json`
    (264 KB), gerados por `gerar_evolucao_up.py`;
  - o que fica para refazer: `evolucao_up/mestres/` (os PNG sem perda, 654 MB), `evolucao_up/quadros/` (os 5.852 WebP soltos, 47 MB em
    disco) e `evolucao_up/cenas_meta/`;
  - as ferramentas em `evolucao_up/ferramentas/`: `converter.html`, `servidor_conversao.py` e `webp.py` (a conversão) e
    `verificar_chave_ligada.mjs` (a verificação).
  - Procedência: UI_GUIDELINES 5.1 (D3).

**Interpretações do worker:**
- **A revelação é uma só para as seis cenas:** o Flash e 5 s do Loop da Adventure, com esqueletos novos, como o protótipo faz nas cinco
  cenas sem Flash. Na própria Adventure, o protótipo segue no mesmo esqueleto; na etapa 0, isso diferiu em 3 dos 39 quadros conferidos.
- **Os esqueletos não foram copiados** (item 2): com os quadros, o pet é o sprite do atlas do app, e o mapa leva só a cena e a música.
- **A sombra do pet aparece na cena:** os quadros do atlas de clipes já vêm com a sombra achatada, e o protótipo a esconde. O centro do
  corpo é o do primeiro quadro do `Idle` com a sombra. Para tirar a sombra, seria preciso gerar outro atlas pelos cels; fica proposto.
- **A reserva `Evol` vai sem o efeito `Levelup_0_Partner`:** das 60 formas do pet, 57 têm linha oficial; as 3 sem linha (Seadramon,
  MegaSeadramon e MetalSeadramon) também não têm `Evol` e caem na Revelação de hoje. Nenhuma forma chega à reserva, então o efeito não
  foi convertido. A reserva toca o `Evol` a 4× e segue no cartão.
- **A forma sombria (item 6), proposta:** a cena toca com o véu roxo do atlas no pet novo. A alternativa é a Revelação de hoje. A decisão
  fica com o Matheus.
- **A música** começa com a cena e para quando a Revelação fecha. Sem a cena (chave desligada, forma sem cena ou erro), o efeito toca no
  cartão, como hoje.
- **Um pacote por cena, em vez de um arquivo por quadro:** com 1.700 WebP soltos, o servidor local levou de 31 a 42 s para entregar uma
  cena de ~11 MB, porque atende um pedido por vez. Com um pacote, o mesmo levou menos de 1 s (a verificação abaixo).
- **Números PROPOSTOS, SEM FONTE:** a janela de 20 quadros.

**A conversão:** 6 Summons (451 quadros na Adventure, 370 nas outras) e a revelação (301 quadros), com até 5 imagens por quadro (o fundo e
até 4 trechos de frente). São 34,5 MB no total; uma evolução baixa de 6,6 MB (Jogress) a 11,6 MB (Adventure). As 57 formas com linha se
dividem assim: Adventure 32, Zero2 9, Tamers 7, Jogress 4, Tamers Mega 3, Dramon 2. Todas as cenas têm forma do DigiLab.

**A verificação com a chave ligada** (`ferramentas/verificar_chave_ligada.mjs`, num build local com a chave ligada só para isso; a fonte
voltou a `false`; Chrome headless, servidor local; saída em `evolucao_up/verificacao_chave_ligada/`, com o `relato.txt`):
- o momento do save do e2e (Agumon → Greymon, cena Adventure), em 390 e 1280 px: a cena carregou em menos de 1 s e o cartão veio 25,5 s
  a 26 s depois de abrir (15 s de Summon e 10 s de revelação), sem erro na página. As fotos de 1 a 22 s substituem o vídeo, porque gravar
  vídeo pedia baixar o ffmpeg do Playwright, e não baixei;
- as seis cenas: o mapa servido troca a cena do Greymon, e cada uma tocou até o cartão (22,6 s a 23,3 s; a Adventure, 25,5 s), sem erro
  (`seis_cenas_8s.png`, `tira_adventure_1280.png`, `tira_390.png`);
- o "Pular" leva ao cartão; com movimento reduzido, a cena nem monta;
- sem o `mapa.json` ou sem o pacote da cena: o aviso visível ("A cena da evolução não tocou: HTTP 404 em …") e o cartão
  (`aviso_*_390.png`);
- a verificação achou e corrigiu três problemas: a Revelação abria antes de o atlas chegar, e a cena desistia; o carimbo do
  `requestAnimationFrame` e o `performance.now` estavam em bases diferentes sob o relógio do Playwright, e o relógio da cena pulava; e o
  texto do aviso estourava a largura em 390 px.

**O celular de referência (decisão 4): NÃO VERIFICADO.** O worker não tem o aparelho, e a emulação não vale (POC-01, M3). Roteiro para o
Matheus: trocar a chave para `true` em `web/app/src/evolucaoUp.ts`, rodar `npm run build` e abrir pelo túnel do
`servidor/servidor_local.py --remoto` uma evolução (ou o "Ver a revelação de novo" de Crescer · Evolução). Anotar quanto tempo leva o
"carregando a cena", se a cena anda sem soluço e se o cartão chega no fim; depois voltar a chave para `false`.

**Os testes, com a chave desligada** (logs em `D:\Trab\digilab\Assets\evolucao_up\verificacao_chave_desligada\`):
- `npm run tipos` limpo; `npm test` → 653 passados (58 arquivos), com `web/app/test/evolucaoUp.test.ts` (9 novos);
  `python -m pytest tests/test_servidor_remoto.py -q` → 15 passados; `python tools/conferir_saude.py` passa.
- `npm run e2e` → 97 passados e 1 falha: o "Forçar" do treino, por tempo (o relógio do app anda 10 min/s e a fadiga cai antes do clique,
  com 3 workers em paralelo). Sozinho, o mesmo teste passou 3 de 3 no branch e 3 de 3 na `main` pura (`e7e6c3c`).
- **As capturas da chave desligada:**
  - a referência foi gravada com o build da `main` atual (`e7e6c3c`) numa worktree temporária. A primeira referência, de antes do código,
    ficou velha quando a `main` andou;
  - o branch e a própria `main` foram comparados com ela, com 1 worker. Os dois falham nas mesmas 3 capturas: Diário · Cenários em
    390 px e Crescer · Evolução v6 em 390 e 1280 px. Elas mudam entre duas rodadas da própria `main`, então não são deste PR;
  - no branch, outras 3 deram diferença na primeira tentativa e passaram na segunda;
  - **o momento da evolução (`evolucao-momento`), a tela que este PR toca, sai igual em 390 e 1280 px.**

