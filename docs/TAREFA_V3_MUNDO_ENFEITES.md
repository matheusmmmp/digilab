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
