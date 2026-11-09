# TAREFA V3 — MUNDO_ENFEITES (2026-11-06)

Coordenador: o Gerente da frente MUNDO_ENFEITES (Claude Code, Opus 5.5, nesta sessão; o mesmo da ITENS_3D). Worker: a definir por etapa.
Worktree e branch: `v3-mundo-enfeites`. Status: ABERTA; D-E1 a D-E4 DECIDIDAS (2026-11-06); nada foi baixado, gerado ou pago.

Categoria: arquitetura. Origem: Matheus, 2026-11-06: deixar o mundo menos vazio com objetos do nosso mundo largados no meio da natureza
(uma geladeira, trilhos de trem, um carro abandonado, postes de luz dispostos ao acaso), num estilo cartunesco e fofo, para criança.

Lido para esta tarefa: `CLAUDE.md`, `web/app/CLAUDE.md`, `docs/PAINEL_V3.md`, `docs/TAREFA_V3_ITENS_3D.md` (o pipeline, os gates G1 a G9 e
o que os quatro itens ensinaram, seções 11 a 13), `docs/TAREFA_V3_HABITAT_ILHA_3D.md`, `web/app/src/telas/pet/ilha/grade.ts` (a grade, a
área andável, a moldura e `porObjetos`), `estilos.ts`, `modelos.ts`, `cena.ts` (`objetos`, `carregarVariante`), `itens.ts` (a luz do ninho)
e `docs/itens3d/kits_cc0_medidas.json`.

## 1. Pergunta

Dá para encher a moldura da ilha com enfeites do mundo humano, alguns repetidos (postes) e alguns marcos únicos (um carro, uma geladeira, um
trilho), no estilo da ilha, sem tocar o motor, sem mudar o mapa de hoje e sem perder fps? Não vem de uma hipótese do `PLANO_V2_PESQUISA.md`:
é produto (`docs/PRODUTO_VISAO.md`), como a L4 e a ITENS_3D.

## 2. Depende de

- A L4 (a ilha 3D) e a ITENS_3D (o pipeline Meshy + Blender, os scripts em `docs/itens3d/`), na `main`.
- As decisões D-E1 a D-E4 (seção 8), já tomadas.
- Para cada download de kit CC0 (seção 4.2): o ok do Matheus no chat, com o nome, a origem e o tamanho.

## 3. Mudança mínima

**O que muda (só a vista):**
- `web/app/src/telas/pet/ilha/grade.ts`: uma lista nova, `Ilha.enfeites`, ao lado de `objetos`, sorteada por uma rng **própria**
  (`rng(semente ^ SAL_ENFEITES)`), depois de `porObjetos`. Os `objetos` de hoje saem iguais, item a item (gate E-G0, seção 4.3).
- `web/app/src/telas/pet/ilha/modelos.ts`: uma tabela irmã, `ENFEITES_MODELOS` (como a `ITENS_MODELOS` da D-I4), com os arquivos, a altura,
  a sombra e a categoria (`repetido` ou `marco`).
- `web/app/src/telas/pet/ilha/enfeites.ts` (novo): carrega os modelos e põe os enfeites como `InstancedMesh` (um por peça, como os kits),
  e o brilho dos postes à noite, um `InstancedMesh` só (como a luz do ninho: aditivo no chão, não ilumina nada).
- `web/app/src/telas/pet/ilha/vista.ts` e `estilos.ts`: só o estilo **ilha** recebe os enfeites nesta frente; os outros (voxel, floresta,
  cassette) ficam como estão.
- `web/app/public/enfeites/<nome>/`: os arquivos, cada um com o `License.txt` (CC0 com a origem, ou Meshy com a marca de IA, como na D-I4).
- O crédito em Ajustes › Sobre.

**O que NÃO muda:** o motor, o log, o save, a área andável e o caminho do pet; os `objetos` de hoje da grade; os outros estilos de mapa;
as versões de pet. Nenhum enfeite dentro da área andável (a regra 5 da L4 vale: dentro dela só entram objetos baixos, e enfeite não é baixo).

## 4. Desenho

### 4.1 A lista (D-E1) e a linguagem visual

| enfeite | categoria | quantos por mapa (PROPOSTO) | de onde (D-E2) |
|---|---|---|---|
| poste de luz | repetido | 8 | kit CC0 |
| carro abandonado | marco | 1 | Meshy |
| geladeira | marco | 1 | Meshy |
| pedaço de trilho com um vagãozinho | marco | 1 | Meshy (o trilho pode vir de kit CC0) |

Depois, se der certo, a lista da conversa de 2026-11-06 (fora desta tarefa até o Matheus pedir): semáforo torto, placa de rua, orelhão,
TV de tubo, máquina de refrigerante, caixa de correio, banco de praça, ponto de ônibus.

**A linguagem visual (vale para o prompt do concept e para o revisor):**
- formas gordinhas e cantos arredondados, cores pastel saturadas, o toon de três tons da ilha, sem contorno;
- abandonado com carinho: musgo, flores e trepadeiras crescendo nos objetos, um passarinho ou ninho em cima de um poste ou do carro;
- **nada** de ferrugem suja, vidro quebrado, fio solto, pichação, sangue, lixo ou cara de perigo;
- nenhuma marca, logotipo ou placa legível de empresa real (o carro sem marca, a geladeira sem logo).

### 4.2 De onde vêm os modelos

- **Os repetidos, de kit CC0.** Candidatos: os kits da Kenney de cidade, carros e trem (CC0, conforme a página da Kenney; a licença é
  conferida no arquivo baixado antes de qualquer uso). Cada download só com o ok do Matheus no chat (nome, origem, tamanho). Se o poste do kit
  não combinar com a ilha, ele vai pela Meshy como um marco.
- **Os marcos, pela Meshy** (o pipeline da ITENS_3D, seção 4.1 dela): concept com a referência de estilo da própria ilha (o recorte do saco
  gerado e dos kits, sem o pet), o Matheus escolhe, multivista, malha, conserto no Blender por script (a cor chapada; os detalhes que a malha
  perder, como a cruz do kit, voltam no Blender), exportação, captura e revisor.
- **O custo:** cerca de 66 créditos por marco (concept 24, vistas 6, malha 30, uma folga de 6). O teto da frente é a D-E3.

### 4.3 Onde ficam (a grade)

Tudo por semente, como a grama: o mesmo mapa sai sempre igual, e cada mapa do motor (o layout) tem o seu conjunto.
- **Os postes "ao acaso":** na moldura, em grama plana, a uma distância da área andável entre 1,5 e 4 células (nada alto rente à área,
  como as árvores hoje, e perto o bastante para a câmera ver), a pelo menos 4 células um do outro e a 2 de qualquer árvore. PROPOSTO.
- **Os marcos:** um em cada canto que a câmera vê da tela Pet, a 2 a 5 células da área, em grama plana com folga de 1 célula, a 3 de
  qualquer árvore e a 6 um do outro. O trilho fica paralelo à borda mais próxima. PROPOSTO.
- **Longe do que já é da cena:** nunca na água, na areia ou no rio; os objetos de hoje ficam onde estão, e um enfeite que cair perto
  demais de um deles é sorteado de novo (até um número de tentativas; se faltar lugar, falha alto, como a decoração de hoje).
- **A luz dos postes à noite:** o brilho no chão de cada poste, com o raio e a cor da luz do ninho (`LUZ_NINHO`), só quando é noite.

### 4.4 Gates (por enfeite e por mapa)

| gate | o quê | como |
|---|---|---|
| E-G0 | os `objetos` de hoje da grade não mudam | um teste grava a lista de hoje (gabarito num commit próprio, antes da mudança) e confere item a item |
| E-G1 a E-G8 | os G1 a G8 da ITENS_3D, por arquivo | o teto de triângulos é a mediana dos kits por categoria (D-I3): 554 para os repetidos (o poste se repete), 2 414 para os marcos |
| E-G9 | os draw calls: os postes entram instanciados (um `InstancedMesh` por peça do modelo), então 8 postes custam o de 1 | a M3 (`?medir3d=1`) antes e depois, no mesmo save |
| E-G10 | nenhum enfeite na área andável, na água ou na areia; as distâncias da seção 4.3 | teste de unidade da grade, em todos os layouts do motor |
| E-G11 | nada cobre o pet nem o HUD | as capturas de 390 e 1280 (claro, escuro e noite), lidas pelo revisor |
| E-G12 | o fps de verdade | a M3 no Chrome do desktop e num celular, pelo Matheus |

## 5. Entrega e etapas

Um PR por etapa, com o relato no corpo; o merge só pelo Matheus.

| etapa | o quê | gasto |
|---|---|---|
| E0 | esta tarefa (PR de arquitetura) | 0 |
| E1 | a grade dos enfeites (E-G0, E-G10), a tabela, o `enfeites.ts` e **os postes** com a luz à noite; o kit CC0 baixado com o ok | 0 créditos |
| E2 | o primeiro marco (o carro), para testar uma peça grande pela Meshy | ~66 créditos |
| E3 | a geladeira e o trilho, num PR só | ~132 créditos |

Em cada etapa: `npm run tipos`, `npm test`, `npm run e2e` em `web/app`; o registro numa seção no fim de `docs/registro/AAAA-MM.md`, com a
linha no índice; o resumo numa seção no fim deste arquivo; as capturas com o pet fora do git (`D:\Trab\digilab\capturas_enfeites\`).

## 6. Fora desta tarefa

- O pet interagir com os enfeites (cheirar a geladeira, dormir no carro, subir no trilho): é cérebro e motor, outra frente. A ideia fica em
  `docs/futuro/enfeites_interacao.md` (D-E4).
- Os estilos voxel, floresta e cassette.
- A segunda leva de enfeites (seção 4.1), até o Matheus pedir.
- Mexer na grama, nas árvores e nas pedras de hoje.

## 7. Critérios de aceitação

- E-G0 e E-G10 num teste de unidade (`web/app/test/`), passando em todos os layouts do motor.
- Cada enfeite com o `License.txt` e os gates E-G1 a E-G8 num teste, como o `ilha_itens3d.test.ts`.
- As M3 antes e depois de cada etapa (E-G9), com os arquivos citados no PR.
- As capturas lidas por um revisor que não fez a peça (E-G11), e aprovadas pelo Matheus.
- O gasto da Meshy de cada etapa nos `saldo.json`, dentro do teto da D-E3.

## 8. Precisa do Matheus

**Decididas (2026-11-06, Matheus: "Eu concordo", sobre a proposta da conversa):**
- **D-E1, a lista inicial:** postes de luz, o carro, a geladeira e o trilho (seção 4.1).
- **D-E2, a origem:** kit CC0 para os repetidos; a Meshy para os marcos únicos.
- **D-E3, o teto de gasto da frente:** R$ 60 (cerca de 550 créditos da Meshy, no preço do Pro da D-I2), separado do teto da ITENS_3D.
- **D-E4, só vista:** a interação do pet com os enfeites fica para outra frente, registrada em `docs/futuro/`.

**Abertas, cada uma na etapa em que aparece:**
- **O download de cada kit CC0** (E1). Recomendação: baixar só o kit de onde sai o poste. Custo de errar: um kit inteiro no disco sem uso.
- **Os concepts de cada marco** (E2, E3): o Matheus escolhe um, como na ITENS_3D.
- **As quantidades e as distâncias** da seção 4.3, PROPOSTAS. Recomendação: aceitar e ajustar jogando. Custo de errar: só vista.
- **O plano da Meshy:** o Pro de um mês da D-I2 tem 860 créditos de saldo (2026-11-06). Recomendação: usar o saldo nas E2 e E3 enquanto o
  plano está ativo; renovar ou não é do Matheus. Custo de errar: perder o saldo que vence, ou pagar um mês a mais sem uso.

## 9. E1: os postes na ilha (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mundo-enfeites-e1`)

**O gabarito primeiro (E-G0):** os `objetos` de hoje da grade, nos dois layouts do motor (mvp: 630; padrão: 634), gravados em
`web/app/test/gabaritos/ilha_objetos.json` num commit próprio, antes dos enfeites (`scripts/gabarito_ilha_objetos.ts`). O teste
`test/ilha_enfeites.test.ts` confere item a item; passa com os enfeites.

**A grade:** `Ilha.enfeites`, sorteada por `rng(semente ^ ENFEITES_GRADE.sal)` depois de `porObjetos` (D-EN-2), com 14 postes por mapa
(`ENFEITES_GRADE`, PROPOSTO; eram 8, e só 1 aparecia na tela), entre 1,5 e 4 células da área, a 4 um do outro e a 2 das coisas altas;
o giro vira a lanterna para a área. E-G10 num teste, nos dois layouts.

**O poste, primeiro do kit (D-E2) e depois pela Meshy:**
- o kit `kenney_cityKitRoads` (City Kit Roads 2.2, CC0, 2,8 MB, baixado com o ok do Matheus; fora do git, em
  `D:\Trab\digilab\Assets\kits3d\kenney_city_roads\`) tem o `light-curved`: 92 triângulos, cinza, fino, de rodovia. Na ilha, saiu
  sem nada do estilo dela (captura em `D:\Trab\digilab\capturas_enfeites\poste_kenney\`); o Matheus escolheu a Meshy;
- pela Meshy: quatro concepts (24 créditos), o Matheus escolheu o 1, lampião; vistas (6) e malha (30): 455 triângulos (teto 554), fiel ao
  concept, mesmo com as vistas achatadas. Saldo 860 → 800 (`docs/enfeites/poste/`);
- o conserto (`consertar_poste.py`): a malha fica; a cor chapada em quatro cores (`paleta.json`), uma por face, sem a troca pelos
  vizinhos (`limpar_faces.py` com 0 rodadas: os vizinhos apagavam os vidros, de 8 faces).

**A luz à noite:** os vidros acendem pelo `emissiveMap` (a máscara `poste_luz.png`, de `mascara_luz.py`, fora do glTF por causa do G5), um
halo em cascas aditivas em volta da lanterna (`ENFEITE_HALO`; um ponto do three e uma esfera só não serviram: o ponto não apareceu e a
esfera parecia uma bolha) e o brilho no chão de `LUZ_NINHO`. Nada disso ilumina a cena.

**Os gates:** E-G0 e E-G10 passam; E-G1 a E-G8 num teste (455 triângulos, 1024 px, 0 erros e 0 avisos no validador, cerca de 87 KB com a
máscara, `License.txt` e `asset.extras`); E-G9, os draw calls, com o save da bola: de dia, 76 → 78 (390) e 83 → 85 (1280), os postes e a
sombra; à noite, 94 → 100 e 100 → 106, mais o brilho e as três cascas do halo (`D:\Trab\digilab\capturas_enfeites\`, fora do git,
com o pet). E-G11: o revisor (um subagente Sonnet que só viu o concept e as capturas) **aprovou com ressalva**: os postes ficam no fundo
(a moldura é a borda do mapa), e o da direita, em 1280, fica parcialmente atrás do painel Estado. E-G12, o fps de verdade, com o Matheus.

**Fora:** os marcos (E2 e E3); o fps no desktop e no celular.

## 10. E2: o carro abandonado (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mundo-enfeites-e2`)

**O carro, pela Meshy:** quatro concepts (24 créditos); o Matheus escolheu o 3, a caminhonete azul-céu com um jardim na caçamba (a van
lembrava demais um modelo real). Vistas (6) e malha (30): 1 946 triângulos (teto 2 414 dos marcos), a forma do concept; as flores da
caçamba viraram pétalas pontudas, que ainda se leem como jardim. Saldo 800 → 740 (`docs/enfeites/carro/`). O conserto
(`consertar_carro.py`): a malha fica; a cor chapada em oito cores (`paleta.json`), uma por face, com uma rodada pelos vizinhos.

**O lugar dos marcos (a grade):** `ENFEITES_GRADE` passou a ter os números por enfeite; os postes vêm primeiro e saem iguais aos da E1.
O carro fica só ao norte da área (o lado que a câmera da tela Pet vê), a até 12 células do ninho em x (onde a câmera mais fica), entre 1,5
e 3 células da área, em chão plano com folga de 1 célula, a 2 das coisas altas e a 3 dos postes (a distância é a de quem chega; com 6, os
postes do norte não deixavam lugar). Os marcos do norte são sorteados só na faixa (pela grade inteira, quase nenhum sorteio caía nela), com
até 4 000 tentativas. Os do motor: mvp (10,4; −1,8) e padrão (4,5; −1,5). Os enfeites sem luz não usam a lanterna para o giro: a frente do
glTF (+z) vira para a área, e a caminhonete mostra o lado com o jardim.

**O caminho até o lugar:** primeiro, sorteado na moldura inteira, o carro caiu em x = 33, longe da casa; depois, a 2 a 5 células da área,
ficou no platô atrás do barranco e de um tronco, pálido pela névoa; a 1,5 a 3 células, aparece inteiro na beira do platô.

**Os gates:** E-G0 e E-G10 passam (com o norte e a casa no teste); E-G1 a E-G8 num teste (1 946 triângulos, 1024 px, 0 erros e 0 avisos no
validador, cerca de 180 KB); E-G9: um draw call a mais, de dia e de noite (78 → 79 e 100 → 101 em 390; 85 → 86 e 106 → 107 em 1280;
`D:\Trab\digilab\capturas_enfeites\referencia_e2\` e `\carro\`). E-G11: o revisor (um subagente Sonnet que só viu o concept e as
capturas) **aprovou com ressalva**: pequeno e distante demais em 390 e à noite, o azul pouco saturado; o conserto foi o dele, a altura de
1,3 para 1,9 e a paleta mais saturada (rodada 2), e as capturas refeitas. À noite ele escurece com a cena, como o resto da moldura.

## 11. E3: a geladeira e o trilho, com traços de nanquim (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mundo-enfeites-e3`)

**Os dois, pela Meshy:** quatro concepts de cada (48 créditos); o Matheus escolheu a geladeira 1 (menta, com o vaso de flores) e o
trilho 1 (o vagão vermelho de janelas redondas). Vistas (12) e malhas (60): a geladeira com 2 062 triângulos e o trilho com 1 760 (teto
2 414 dos marcos), as duas com a forma do concept. Saldo 740 → 620 (`docs/enfeites/geladeira/`, `docs/enfeites/trilho/`).

**Os traços de nanquim (pedido do Matheus, 2026-11-06: "mais cartunesco, traços firmes, fortes, na textura mesmo", no jeito de
Borderlands):** sobre a textura chapada (seis cores por item, uma por face), `docs/enfeites/arestas_uv.py` lista as arestas da malha no
espaço da textura (as faces dos dois lados, o ângulo, o comprimento e o segmento de UV em cada face), e `docs/enfeites/tracar_linhas.py`
desenha um traço quase preto (`TINTA`) de 5 px em cada divisa de cor e em cada quina grande (mais de 70° e com pelo menos 0,12 de
comprimento). Na primeira rodada (38°, sem o comprimento, 7 px), as facetas da Meshy davam riscos soltos e sujos; o revisor apontou, e o
limiar subiu. Os traços ficam só na textura: nenhum shader novo.

**O lugar:** os dois ficam ao norte, como o carro, numa faixa de x a partir do ninho (`faixa`: −12 a 14 para a geladeira, −9 a 9 para o
trilho), com 3 células dos outros enfeites; os do motor: mvp, geladeira (2,8; −2,6) e trilho (6,1; −1,6); padrão, geladeira (−1,3; −1,6) e
trilho (7,4; −3,9). Na primeira rodada, o trilho foi parar em x = 20 no mvp, atrás do painel Estado.

**Os gates:** E-G0 e E-G10 passam; E-G1 a E-G8 num teste (2 062 e 1 760 triângulos, 1024 px, 0 erros e 0 avisos, cerca de 210 KB cada);
E-G9: dois draw calls a mais, de dia e de noite (80 → 81 e 101 → 103 em 390; 86 → 88 e 107 → 109 em 1280;
`D:\Trab\digilab\capturas_enfeites\referencia_e3\` e `\e3\`). E-G11: o revisor reprovou o trilho e aprovou a geladeira com ressalva na
rodada 1 (traços sujos, o trilho atrás do HUD); a rodada 2 está no corpo do PR. Os postes e o carro ficam sem traços nesta etapa.


## 12. O trem refeito no retrabalho dos objetos (2026-11-07, worker, Claude Code, Opus 5.5, branch `v3-objeto-trem`)

**O pedido:** o Matheus achou o trilho da E3 "muito feio, com o cel shading esquisito". As causas estão em `docs/objetos3d/REFERENCIAS.md`
(seções 1 e 5): a textura achatada em 7 cores e as normais facetadas, que fazem o toon de dois tons manchar cada face.

**A malha:** pela Meshy, a partir do esboço 1 (o vagão de madeira vermelho, o teto creme curvo, as escotilhas de latão, as rodas de ferro e o
trilho com dormentes e grama): a multivista (6 créditos) e a malha (30), uma tentativa, dentro do teto de 36 da sessão
(`docs/objetos3d/trem/saldo.json`). A malha tem 2 157 triângulos (teto 2 414 dos marcos).

**O acabamento** (`docs/objetos3d/trem/acabar_trem.py`, Blender 4.5 pela linha de comando, e `textura_trem.py`):
- a textura pintada da Meshy fica: as tábuas, a tinta descascada, a ferrugem, o latão, o musgo e a grama; só um realce leve de saturação no
  latão, no vidro, nos verdes e no metal (D-OB-TREM-3);
- as normais vêm de uma cópia suavizada da malha, sem quinas duras (D-OB-TREM-1): é o que tira as manchas do toon;
- a textura fica em 512 px com 256 cores, para caber nos 300 KB do teste (D-OB-TREM-2); o enfeite tem ~294 KB.

**No jogo:** os três arquivos de `web/app/public/enfeites/trilho/` trocados; a altura fica em 2,0 e a sombra cai para 1,6 (D-OB-TREM-4). A
grade e as posições não mudam: o E-G0 e o E-G10 passam, e o E-G1 a E-G8 também, sem trocar teste nenhum.

**A revisão:** um revisor que não fez o trabalho comparou a prancha (o esboço, o antes, o depois e o vagão no jogo nos mapas Digital e
Ilha; `D:\Trab\digilab\capturas_objetos3d\trem\prancha_trem.png`) e deu APROVA COM RESSALVA nas duas rodadas. Na primeira, apontou o latão
desbotado, o musgo e a grama apagados, o vidro escuro e o teto facetado de frente; a rodada 2 consertou os quatro pela textura e pelas
normais. Ficam como ressalva o que pede malha nova: os para-choques e o engate, o chassi de frente, os degraus na borda do teto e os
trilhos pintados de marrom.

## 13. O carro retrabalhado (2026-11-08, worker, Claude Code, Opus 5.5, branch `v3-objeto-carro`)

**O pedido:** o Matheus achou os objetos feios e "sem textura", e o carro "completamente sem detalhe" (a caminhonete da E2, achatada em 7
cores). O retrabalho segue `docs/objetos3d/REFERENCIAS.md` (seção 5) e o esboço `docs/objetos3d/carro/esbocos/esboco_1_hatch_retro.png`: o
hatch retrô azul com ferrugem, as rodas grandes, as janelas, os faróis, o jardim no teto e o musgo no capô.

**Pela Meshy:** a multivista a partir do esboço (6 créditos) e a malha (30): 2 175 triângulos (teto 2 414 dos marcos). Saldo 122 → 86
(`docs/objetos3d/carro/`, `saldo.json`).

**O acabamento, por script (`docs/objetos3d/carro/`):**
- `acabar_carro.py` (Blender 4.5 pela linha de comando): a malha girada 90°, com a frente em +z do glTF; os vértices repetidos soldados; as
  normais suavizadas e ponderadas; a base no y = 0;
- `textura_carro.py`: a textura pintada da Meshy sem achatar, 512 px em paleta de 256 cores, com um retoque leve nas máscaras do
  `mascaras_carro.py`: os verdes mais vivos, flores rosa no teto e os faróis amarelos;
- `publicar_carro.py`: a marca de IA no `asset.extras`, a troca em `web/app/public/enfeites/carro/` e o validador (0 erros, 0 avisos).

**No jogo:** a altura vai de 3,4 para 4,8 (`ENFEITES_MODELOS`); a grade e as posições não mudam. São 297 010 bytes, de um teto de 307 200.

**O revisor** (um subagente Sonnet que não fez o trabalho e viu só o esboço e as capturas) deu **APROVA COM RESSALVA** nas duas rodadas. Na
rodada 1, pediu o teto, o musgo, os faróis e a escala; a rodada 2 fez o retoque e a altura. Ficam, porque só uma malha nova resolve:
- as rodas encaixadas no corpo, com o pneu liso;
- a boca escura do teto e o tufo estreito; as flores só leem na vitrine.

As capturas (a prancha, a vitrine no D5, a Ilha e o Digital, antes e depois) estão fora do git, em `D:\Trab\digilab\capturas_objetos3d\carro\`.
Os desvios estão em `docs/registro/2026-11.md`, D-OBJ-CARRO-1 a 6.

### 13.1. A rodada 3: o carro em cartoon limpo (2026-11-08 e 09, worker, Claude Code, Opus 5.5, branch `v3-objeto-carro-cartoon`)

**O pedido:** com o #715 no jogo, o Matheus achou o carro "um cartoon bem no feio": a malha está boa, mas a pintura da Meshy é quase foto
(a ferrugem em degradê, o vidro sujo com o banco por dentro, o musgo de esponja) num mundo de cores chapadas com toon de dois tons. A
textura cartoon foi aprovada pelo Matheus, pelo Gerente, depois da prancha. A malha, a altura e a grade não mudam; não houve Meshy.

**O que mudou (`docs/objetos3d/carro/`):**
- `oclusao_carro.py` (Blender pela linha de comando): a oclusão ambiente assada da própria malha na UV (`conserto/oclusao.png`), para as
  caixas de roda, as frestas e as molduras escurecerem;
- `mascaras_carro.py`: a máscara opcional da faixa das janelas (`conserto/janelas.png`), pela altura dos triângulos;
- `estilizar_carro.py`: a textura redesenhada por região. O mean shift junta o ruído pintado em manchas; cada pixel cai numa classe pelo
  matiz (a tinta azul, a ferrugem, o musgo, o pneu, o metal, o farol, a lanterna, o vidro na faixa das janelas, as lascas cinza pequenas)
  e recebe uma cor de uma paleta fixa por faixa de brilho; a mediana tira os pontinhos; a oclusão escurece; as flores rosa voltam no
  teto. O farol cresce sobre a ferrugem pintada em volta da lente;
- `textura_carro.py` (sem as máscaras) reduz a 512 px em paleta de 256 cores, e o `publicar_carro.py` troca a textura e roda o validador
  (0 erros, 0 avisos). São 261 002 bytes, de um teto de 307 200.

**Ficam:** as rodas encaixadas no corpo (da malha) e alguns pontos amarelos no para-choque, onde a ferrugem encosta no farol. As capturas
(`prancha_carro_r3.png`, `r3_ilha_carro_1280.png`, `r3_digital_carro_1280.png`) estão em `D:\Trab\digilab\capturas_objetos3d\carro\`.
Os desvios estão em `docs/registro/2026-11.md`, D-OBJ-CARRO-7 a 9.

## 14. O poste em blocos (2026-11-08, worker, Claude Code, Opus 5.5, branch `v3-objeto-poste`)

**O pedido:** o Matheus achou os objetos feios e "sem textura"; o poste da E1 era o lampião achatado em quatro cores. O retrabalho parte do
esboço `docs/objetos3d/poste/esbocos/esboco_1_ferro_hera.png`: o poste antigo de ferro fundido verde, a lanterna de vidro amarelo quente, a
hera subindo e a base de pedra com musgo.

**Tentativa 1, pela Meshy (fora do jogo):** a multivista e a malha (36 créditos, saldo 50 → 14), 460 triângulos, a textura pintada sem
achatar com retoques no espaço 3D da malha, e três rodadas do revisor (APROVA COM RESSALVA). O Matheus achou o poste "ainda feio" e pediu
"um pouco mais fino", "uma estética mais pixelada", "mais digitais". Os arquivos dela ficam em `docs/objetos3d/poste/` como histórico.

**A direção C, escolhida pelo Matheus:** depois de uma prancha de referências (postes de voxel, o esboço 2 "ferro digital", uma maquete em
blocos e testes de pixel no poste da Meshy; fora do git, em `D:\Trab\digilab\capturas_objetos3d\poste\referencias_pixel\`), um poste em
blocos, feito à mão, com textura de pixel. O pixel sobre a malha da Meshy virava ruído (o atlas dela vem em ilhas pequenas).

**O poste em blocos (`docs/objetos3d/poste/blocos/`):**
- `poste_blocos.py`: 39 caixas (a base e o degrau de pedra, o pé com o alargado, o fuste de 2 blocos com dois anéis, os braços curtos, o
  colar de latão, a lanterna com as quinas, o teto em degraus com as pontas, o pináculo, os tufos de musgo e as folhas da hera) e a pintura
  em pixel art de cada material, pela posição de cada texel no mundo (a pedra, o ferro, a hera e o musgo continuam de uma face para a
  outra); 4 texels por bloco, o atlas de 256 px ampliado sem filtro a 1 024 px, o "nearest" no sampler do glTF; a máscara da luz âmbar no
  miolo dos vidros. Sem IA, sem Blender, determinístico;
- `previa_blocos.py`: as prévias no Blender; `publicar_blocos.py`: a procedência, a troca em `web/app/public/enfeites/poste/` e o
  validador (0 erros, 0 avisos).

**No jogo:** 390 triângulos (teto 554), 39 942 bytes (de 307 200); a altura fica 4,5 e a grade e as posições não mudam (E-G0, E-G10). O
halo (`ENFEITE_HALO`) vai para o meio dos vidros novos (0,86 → 0,77) e fica mais fraco (0,08 → 0,06). O `web/app/test/ilha_enfeites.test.ts`
passa a aceitar a procedência "feito à mão por script" ao lado da da Meshy (D-OBJ-POSTE-5). Os fios do Digital, a 0,93 da altura, caem no
pináculo.

**O revisor** (um subagente Sonnet novo, que não fez o trabalho nem viu a tentativa 1): **APROVA COM RESSALVA** nas duas rodadas. A rodada 1 pediu o vidro âmbar à noite, o fuste mais claro, menos peso em cima, os braços curtos (compridos pareciam placa) e a hera mais limpa; a rodada 2 deu tudo por resolvido, menos o contraste do fuste e da hera à noite no Digital (ainda escuros), que não bloqueia. A prancha está em
`docs/objetos3d/poste/blocos/prancha_poste_blocos.jpg`; as capturas (antes e blocos, Ilha e Digital, dia e noite) estão fora do git, em
`D:\Trab\digilab\capturas_objetos3d\poste\blocos\`. Os desvios estão em `docs/registro/2026-11.md`, D-OBJ-POSTE-1 a 9.

## 15. O carro feito à mão por script (2026-11-09, Gerente, Claude Code, Fable 5.2, branch `v3-objeto-carro-mao`)

**O pedido:** com o carro em cartoon (#739) no jogo, o Matheus achou que ele continuava "muito feio" e pediu uma revisão dos modelos 3D,
a começar por ele. O defeito era da malha, não da pintura: a malha da Meshy é amassada e facetada, e a textura dela vem em ilhas
pequenas, que viram cacos triangulares quando a cor é chapada. O carro foi refeito do zero, como o poste da seção 14.

**O carro (`docs/objetos3d/carro/mao/`):**
- `carro_mao.py`: a carroceria é uma superfície por seções (23 estações, 19 pontos cada: a soleira, a lateral, o ombro, a coluna e o
  teto), com a linha de cima do esboço 1 (o capô, o para-brisa, o teto, o vidro de trás); as peças são sólidos simples (quatro rodas,
  as molduras das caixas de roda, dois para-choques, dois faróis, os retrovisores, seis tufos de musgo, doze folhas de capim e quatro
  flores). A pintura é uma função da posição no espaço: os vidros com a moldura e os riscos de brilho, a porta, a maçaneta, o corte do
  capô, a grade, os piscas, as lanternas, a placa, a ferrugem (a barra de baixo, as manchas que escorrem, a volta das rodas), o musgo e o
  buraco do teto com a terra. Só cores chapadas, sem degradê. O atlas é pintado a 2 048 px e reduzido a 1 024 px, em 128 cores. Sem IA,
  sem Blender, determinístico;
- `publicar_mao.py`: a procedência no `asset.extras`, a troca em `web/app/public/enfeites/carro/` e o validador (0 erros, 0 avisos).

**No jogo:** 2 166 triângulos (teto 2 414), 177 821 bytes com o `License.txt` (teto 307 200), um nó, uma malha, uma textura. A altura
(4,8), a sombra, a grade e o lugar do carro não mudam (E-G0, E-G10). O `web/app/test/ilha_enfeites.test.ts` ganha o teste da
procedência. Os scripts do carro da Meshy ficam em `docs/objetos3d/carro/` como histórico.

**Não feito:** não houve revisor separado nem prancha de capturas no git; a conferência foi na vitrine (`poc/vitrine.html`) e no jogo, no
estilo da Ilha. O estilo Digital e o celular não foram conferidos. Os desvios estão em `docs/registro/2026-11.md`, D-OBJ-CARRO-10 a 12.

## 16. A geladeira feita à mão por script (2026-11-09, Gerente, Claude Code, Fable 5.2, branch `v3-objeto-geladeira-mao`)

**O pedido:** depois do carro da seção 15, o Matheus pediu: "agora arrume essa geladeira também". A geladeira da Meshy tinha o mesmo
defeito do carro (a malha amassada) e esperava créditos para ser refeita; pelo script ela não gasta crédito.

**A geladeira (`docs/objetos3d/geladeira/mao/`):**
- `geladeira_mao.py`: o corpo e as duas portas são seções de cantos redondos, como no esboço 1 (a geladeira retrô verde-menta); as peças
  são sólidos simples (dois puxadores cromados, quatro dobradiças, o vaso de barro com o broto, as folhas da hera e cinco tufos de musgo
  no pé). A pintura é uma função da posição no espaço, só com cores chapadas: os reflexos na diagonal, o emblema, as lascas de tinta com
  ferrugem que escorre, a ferrugem do pé, a grade do motor atrás e os ramos da hera. A geladeira fica tombada 3,5 graus para o lado. Os
  sólidos, o atlas e a escrita do glTF são os do `carro_mao.py`, que ganhou a função `exportar` (o carro sai byte a byte igual);
- `publicar_mao.py`: a procedência no `asset.extras`, a troca em `web/app/public/enfeites/geladeira/` e o validador (0 erros, 0 avisos).

**No jogo:** 1 880 triângulos (teto 2 414), 158 352 bytes com o `License.txt` (teto 307 200), um nó, uma malha, uma textura. A altura
(3,0), a sombra, a grade e o lugar não mudam (E-G0, E-G10). O jogo vira a frente dos marcos para a área, então na praia do sul o jogador
vê a geladeira de costas; por isso a hera também sobe por trás, ao lado da grade do motor. O `web/app/test/ilha_enfeites.test.ts` ganha o
teste da procedência. Os arquivos da geladeira da Meshy ficam em `docs/enfeites/geladeira/` como histórico.

**Não feito:** não houve revisor separado nem prancha de capturas no git; a conferência foi na vitrine e no jogo, no estilo da Ilha. O
estilo Digital dentro do jogo e o celular não foram conferidos. Os desvios estão em `docs/registro/2026-11.md`, D-OBJ-GEL-1 a 3.
