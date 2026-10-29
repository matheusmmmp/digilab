# TAREFA V2 — UP-EVOLUCAO: a cena oficial de digievolução na Revelação (2026-10-29)

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: a definir. Worktree e branch: `v2-up-evolucao`. Status: ABERTA (liberada pelo Matheus em 2026-10-29)
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
