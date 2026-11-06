# TAREFA V3 — MAPA_DIGITAL (2026-11-06)

Coordenador: o Gerente da frente MAPA_DIGITAL (Claude Code, Opus 5.5, nesta sessão; o mesmo da MUNDO_ENFEITES). Worker: a definir por
etapa. Worktree e branch: `v3-mapa-digital` (na worktree `v3-mundo-enfeites`). Status: ABERTA; a direção B escolhida pelo Matheus
(2026-11-06); D-MD1 a D-MD5 DECIDIDAS pela recomendação (2026-11-06, seção 8); nada foi feito no jogo.

Categoria: arquitetura. Origem: Matheus, 2026-11-06: o chão, as texturas e os objetos da ilha estão genéricos ("bem o que veio do kit");
pediu uma estética "mais na pegada do anime, com as cores mais chapadas" e um mapa mais temático. Mostrou como referência de clima
imagens de animes e jogos de monstros digitais, entre eles o Next Order. Entre as três maquetes (A, fundo de anime; B, mundo digital;
C, cidade engolida), escolheu a **B**.

Lido para esta tarefa: `CLAUDE.md`, `web/app/CLAUDE.md`, `docs/TAREFA_V3_MUNDO_ENFEITES.md` (os enfeites e os traços de nanquim, seção
11), `docs/TAREFA_V3_HABITAT_ILHA_3D.md` (a ilha, a regra 5, H-6), `web/app/src/telas/pet/ilha/cena.ts` (`toon`, o `GRADIENTE`, o
`terreno`, o `ceu`, as `nuvens`, `montarCena`, `aplicarNoite`), `estilos.ts`, `grade.ts`, `modelos.ts`, `web/app/src/habitat.ts` (os mapas
de Ajustes).

## 1. Pergunta

A ilha fica com a cara da maquete B — fundo de anime (céu pintado com nuvens enormes, grama saturada e chapada com florzinhas, barranco
de pedra cinza com musgo, cel shading de dois tons, traços de nanquim) e o toque digital (partículas de dados, uma grade fraca no céu,
fios entre os postes, um objeto humano gigante como marco) — sem tocar o motor, sem mudar onde as coisas ficam e sem perder fps?

**A linha da inspiração:** a referência é o clima (cores, céu, o digital, objetos humanos na natureza). Nada é copiado: nenhum mapa,
modelo, textura, logotipo ou nome desses jogos; as imagens de terceiros não vão para gerador nenhum (só a descrição do estilo).

## 2. Depende de

- A MUNDO_ENFEITES na `main` (a E3 entrou no PR #631): os postes, o carro, a geladeira, o trilho e o `tracar_linhas.py`.
- As decisões D-MD1 a D-MD5 (seção 8), tomadas.

## 3. Mudança mínima

**O que muda (só a vista):**
- um estilo de mapa novo, `digital` (D-MD1), em `estilos.ts`, sobre a **mesma grade** (`grade.ts`): a área andável, a moldura, os objetos e
  os enfeites ficam onde estão;
- `cena.ts`: uma paleta de terreno nova (grama em dois verdes saturados, a pedra cinza com faixas de musgo no barranco, o caminho), uma
  textura de chão com florzinhas, o céu pintado (D-MD2), o `GRADIENTE` do toon em dois tons com a sombra azulada;
- os modelos dos kits (árvores, arbustos, pedras, flores) recoloridos para a paleta chapada e com os traços de nanquim (o pipeline da
  E3: `achatar_cores.py`, `limpar_faces.py`, `arestas_uv.py`, `tracar_linhas.py`), numa pasta própria do estilo; os postes e o carro
  ganham os traços também;
- o digital: as partículas de dados (pontinhos ciano que flutuam, mais fortes à noite), a grade fraca no céu, os fios entre os postes
  (curvas penduradas entre postes vizinhos) e um objeto gigante como marco (D-MD3);
- Ajustes › Mapa: o "Digital" na lista (D-MD1).

**O que NÃO muda:** o motor, o log, o save, a área andável e o caminho do pet; a grade e os objetos de hoje (o gate D-G0, como o E-G0);
os outros estilos (ilha, voxel, floresta, cassette); as versões de pet.

## 4. Etapas e gates

| etapa | o quê | gasto |
|---|---|---|
| D0 | esta tarefa (PR de arquitetura) | 0 |
| D1 | o estilo `digital` na lista, a paleta do chão com as flores, o barranco de pedra, o toon de dois tons e o céu pintado | 0 a 6 créditos (D-MD2) |
| D2 | os kits recoloridos e com traços, e os traços nos postes e no carro | 0 |
| D3 | o digital: as partículas, a grade no céu, os fios dos postes | 0 |
| D4 | o objeto gigante (o marco) | ~66 créditos (D-MD3) |

**Gates (cada etapa, contra a mesma captura da ilha de hoje):**
- D-G0: os objetos e os enfeites da grade não mudam (o gabarito de `test/gabaritos/ilha_objetos.json` e as posições dos enfeites);
- D-G1: os draw calls da M3 (`?medir3d=1`) no máximo 10 % acima do estilo ilha; as partículas num desenho só;
- D-G2: os arquivos novos com os gates G1 a G8 da ITENS_3D (os kits recoloridos com a licença CC0 de origem ao lado);
- D-G3: nada cobre o pet nem o HUD; o pet (o sprite) continua legível sobre o chão novo (contraste);
- D-G4: as capturas lado a lado com a maquete B (`D:\Trab\digilab\capturas_enfeites\maquetes\`), lidas por um revisor que não fez a etapa,
  e aprovadas pelo Matheus;
- D-G5: o fps de verdade, no desktop e num celular, pelo Matheus.

Em cada etapa: `npm run tipos`, `npm test`, `npm run e2e`; o registro em `docs/registro/AAAA-MM.md` com a linha no índice; o resumo numa
seção no fim deste arquivo; as capturas com o pet fora do git (`D:\Trab\digilab\capturas_mapa_digital\`).

## 5. Fora desta tarefa

- O pet interagir com o digital (as partículas, o marco): é cérebro e motor (a ideia de `docs/futuro/enfeites_interacao.md`).
- Mudar a grade, a área andável ou o layout do motor.
- Os outros estilos de mapa.
- A cidade engolida (a maquete C) e mais objetos gigantes além de um.

## 6. Critérios de aceitação

- D-G0 num teste; D-G1 nas M3 citadas no PR; D-G2 num teste como o `ilha_enfeites.test.ts`.
- As capturas de cada etapa ao lado da maquete B, com o parecer do revisor no PR e a aprovação do Matheus.
- O gasto da Meshy nos `saldo.json`, dentro do teto da D-MD4.

## 7. Riscos

- **O sprite do pet sobre a grama saturada:** o pet é um sprite em papel; um chão muito saturado pode apagá-lo. O D-G3 confere e, se
  precisar, a grama perto do pet fica um tom mais clara.
- **Os traços nos kits:** os kits CC0 são facetados como as malhas da Meshy; o limiar da E3 (70°, comprimento mínimo) vale de partida.
- **A maquete é pintura, o jogo é 3D:** o alvo é a direção (cor, céu, chão, o digital), não a imagem igual.

## 8. Precisa do Matheus

**DECIDIDAS em 2026-11-06:** o Matheus aceitou as cinco recomendações abaixo ("Sim, mescle os dois", à pergunta "Aceito as cinco
recomendações e mesclo o #631 e o #632?").

- **D-MD1, o digital como estilo novo ou no lugar da ilha.** Recomendação: um estilo novo, "Digital", em Ajustes › Mapa, e ele vira o
  padrão quando as capturas forem aprovadas; a ilha de hoje fica selecionável. Custo de errar: trocar o padrão sem aprovação muda a cara
  do jogo de todo mundo de uma vez.
- **D-MD2, o céu pintado.** Recomendação: uma panorâmica de céu gerada pela Meshy (Image to Image, 6 créditos, a partir de uma descrição,
  sem imagem de terceiros) e ajustada à mão; a alternativa é desenhar as nuvens no código, como as de hoje, maiores. Custo de errar: 6
  créditos, ou um céu que não fica pintado o bastante.
- **D-MD3, o objeto gigante.** Recomendação: uma lata de refrigerante sem marca (a da maquete), pela Meshy, longe no fundo; outras ideias:
  uma cabine telefônica ou um hidrante gigantes. Custo de errar: ~66 créditos num marco que não combina.
- **D-MD4, o teto de gasto da frente.** Recomendação: R$ 20 (~185 créditos; o saldo do Pro é 602 em 2026-11-06). Custo de errar: gastar
  além do previsto num mês de plano.
- **D-MD5, os números PROPOSTOS** (a paleta, a densidade das partículas, a transparência da grade, a curva dos fios). Recomendação: aceitar
  e ajustar jogando. Custo de errar: só vista.
