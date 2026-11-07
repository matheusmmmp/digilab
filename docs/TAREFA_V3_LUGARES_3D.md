# TAREFA V3 — LUGARES_3D (2026-11-07)

Coordenador: Matheus. Worker: Claude Code (Gerente das frentes ITENS_3D, MUNDO_ENFEITES e MAPA_DIGITAL, Opus 5.5). Worktree:
`v3-mundo-enfeites`; um branch por lugar (`v3-lugares-3d-portao`, `-barraca`, `-cais`). Status: ABERTA.

Categoria: implementacao. Origem: Matheus, 2026-11-07: os modelos 3D dos lugares da ilha (o portao da arena, a barraca do Tamer e o cais), pedidos pelo Matheus em 2026-11-06 e pela frente UX_TELA_PET para a L3.

## 1. Pergunta

Não é pesquisa: são os três objetos 3D dos "Lugares da ilha" (`docs/PLANO_V3_PROGRESSAO_TUTORIAL.md`, P-11): o portão da arena (Lutar), a
barraca do Tamer (Diário) e o cais (o multiplayer, futuro). O Matheus pediu em 2026-11-06 "faz sketches… e daí depois a gente realmente
projeta". A frente UX_TELA_PET (a L3 dos lugares) põe os modelos na cena por um módulo próprio (`ilha/lugares.ts`); esta tarefa entrega os
arquivos.

## 2. Depende de

- Os esboços: 9 concepts da Meshy (3 por lugar), em `docs/lugares3d/<lugar>/concept/` e na prancha `docs/lugares3d/prancha_esbocos.png`.
- **A escolha do Matheus (2026-11-07, nesta sessão): "barraca 2, portal 1 e cais 3"**: o domo digital com a antena, o arco de pedra
  com o portal ciano e o píer com a balsa e a boia de dados. (Uma escolha repassada antes por outra sessão, "barraca 3", não vale: a dele, aqui,
  é a de cima.)
- O pipeline dos itens e dos enfeites (`docs/TAREFA_V3_ITENS_3D.md`, `docs/TAREFA_V3_MUNDO_ENFEITES.md`): concept, multivista e malha pela Meshy,
  o conserto no Blender por script, o glTF-Validator, o `License.txt` com a marca de IA.

## 3. Mudança mínima

- **Os arquivos**, um lugar por PR, na ordem portão, barraca e cais: `web/app/public/lugares/<lugar>/<lugar>.gltf`, `.bin`,
  `<lugar>_cor.png` e `License.txt`; o portão leva também `portao_luz.png`, a máscara emissiva do portal (acende com o lugar aberto).
- **A forma combinada com a L3:** glTF separado, 1 nó, 1 material só de cor, textura de até 1024 px, teto de 2 414 triângulos (o dos
  marcos), até 300 KB; pivô no centro da base; frente no +z do glTF; a altura pela tabela `LUGARES_MODELOS` (`web/app/src/telas/pet/ilha/
  modelos.ts`), lida pelo `carregarVariante` de `cena.ts` (PROPOSTO: portão 5 células, barraca 4, cais a definir). Trancado e aberto são o
  mesmo modelo: o trancado é a vista (apagado, com o cadeado), da L3.
- **Os scripts e a procedência** em `docs/lugares3d/<lugar>/`.
- **Um teste** dos gates G1 a G8 (`web/app/test/lugares3d.test.ts`), como o `test/ilha_enfeites.test.ts`.

**O que NÃO muda:** o motor, o log, o save, a grade (`grade.ts`) e a cena (`ilha/lugares.ts` é da L3); os outros estilos; as versões de pet.

## 4. Experimento e gate (se houver run)

Não há run. Os gates de cada lugar são os G1 a G8 dos itens (`docs/TAREFA_V3_ITENS_3D.md`), com o teto de 2 414 triângulos, num teste; e a
prévia lida por um revisor que não fez a etapa.

## 5. Entrega

- Testes: em `web/app`: `npm test`, `npm run tipos`, `npm run e2e`.
- Registro: seção própria no fim de `docs/registro/AAAA-MM.md`; o índice `docs/REGISTRO_DESVIOS.md` é gerado
  (`python tools/gerar_indice_desvios.py`). O resumo de cada lugar vai no corpo do PR e numa seção no fim deste arquivo.
- PR contra a `main` por lugar, no modelo de relato. Merge só pelo Matheus.

## 6. Fora desta tarefa

- Pôr os lugares na cena, o ponto e o giro de cada um, o estado trancado e o cadeado na tela: é da L3 (frente UX_TELA_PET).
- O cadeado como modelo 3D: só se a L3 pedir.
- O cais na ilha: o multiplayer é futuro; o modelo entra, a cena não.

## 7. Critérios de aceitação

- Cada lugar com o teste dos gates passando e o validador sem erro nem aviso (`docs/lugares3d/<lugar>/validacao.json`).
- A prévia de cada lugar no PR, com o parecer do revisor, e a aprovação do Matheus.
- O gasto da Meshy nos `saldo.json` e nos JSON das tarefas.

## 8. Precisa do Matheus

- **A altura de cada lugar** (PROPOSTA: portão 5 células, barraca 4; o pet tem ~1, a geladeira 3, o pinheiro 7). Recomendação: aceitar e ajustar
  na L3 jogando. Custo de errar: só vista; o número está numa tabela.
- **O gasto.** Recomendação: ~36 créditos por lugar (multivista e malha), ~108 no total, além dos 54 dos esboços (saldo 482 em 2026-11-06).
  Custo de errar: créditos de um mês de plano.

## 9. O portão da arena (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-lugares-3d-portao`)

**O que entrou:** `web/app/public/lugares/portao/` (o glTF com 1 576 triângulos, a cor chapada, a máscara do portal `portao_luz.png` e o
`License.txt`), a tabela `LUGARES_MODELOS` e `LUGARES_LUZ` em `modelos.ts` (altura 5, PROPOSTO) e o teste `test/lugares3d.test.ts` (G1 a G8,
teto 2 414). Os passos e os scripts em `docs/lugares3d/portao/` (`consertar_portao.py`, `mascara_portal.py`, `paleta.json`, `validacao.json`).
O conserto e os números: D-LG-3 a D-LG-5 (a profundidade 1,5 vez maior, pela ressalva do revisor). Gasto: 36 créditos no portão, mais os 54 dos esboços (saldo 446).

**A prévia:** `D:\Trab\digilab\capturas_lugares3d\portao\previa_portao.png` (aberto, de lado, trancado e de costas, renderizados no Blender).
O revisor: no corpo do PR.

**Para a L3:** carregar `LUGARES_MODELOS.portao` pelo `carregarVariante`, com a frente +z para a área; a máscara `LUGARES_LUZ.portao` como
`emissiveMap` (sem virar a imagem, `flipY = false`, como o poste em `enfeites.ts`), com a intensidade 0 trancado e a cor do portal aberto.

## 10. A barraca do Tamer (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-lugares-3d-barraca`)

**O que entrou:** `web/app/public/lugares/barraca/` (o glTF com 2 037 triângulos, a cor chapada e o `License.txt`) e a linha
`LUGARES_MODELOS.barraca` em `modelos.ts` (altura 4, sombra 2,4, PROPOSTO); o teste `test/lugares3d.test.ts` já percorre a tabela inteira.
Os passos e os scripts em `docs/lugares3d/barraca/` (`consertar_barraca.py`, `achatar_barraca.py`, `paleta.json`, `conserto/uv_faces.json`,
`validacao.json`). O conserto
e os números: D-LG-6 a D-LG-9 (a cor pelo matiz, porque a sombra embutida levava a listra branca ao cinza, e uma cor por face; sem máscara de
luz, porque a tela não sobreviveu à malha; a entrada não lê, porque a malha não tem vão). Gasto: 36 créditos (saldo 410).

**A prévia:** `D:\Trab\digilab\capturas_lugares3d\barraca\previa_barraca.png` (frente, direita, costas e esquerda, no Blender) e
`docs/lugares3d/barraca/conserto/previa.png` (3/4). O revisor: no corpo do PR.

**Para a L3:** carregar `LUGARES_MODELOS.barraca` pelo `carregarVariante`, com a frente +z (a porta aberta) para a área. Não há
`LUGARES_LUZ.barraca`.

## 11. O cais (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-lugares-3d-cais`)

**O que entrou:** `web/app/public/lugares/cais/` (o glTF com 2 019 triângulos, a cor chapada, a máscara do ciano `cais_luz.png` e o
`License.txt`), as linhas `LUGARES_MODELOS.cais` (altura 2,4, sombra 0, PROPOSTO) e `LUGARES_LUZ.cais` em `modelos.ts`, e o teste da máscara
em `test/lugares3d.test.ts`, agora para todo `LUGARES_LUZ`. Os passos e os scripts em `docs/lugares3d/cais/` (`consertar_cais.py`,
`mascara_cais.py`, `faces_tabuas.py`, `pintar_tabuas.py`, `paleta.json`, `validacao.json`). O conserto e os números: D-LG-10 a D-LG-13. Gasto: 36 créditos (saldo 374).

**A prévia:** `D:\Trab\digilab\capturas_lugares3d\cais\previa_cais.png` (quatro lados, no Blender, câmera ortográfica) e
`docs/lugares3d/cais/conserto/previa.png`. O revisor: no corpo do PR.

**Para a L3:** carregar `LUGARES_MODELOS.cais` pelo `carregarVariante`, com o comprido do píer ao longo da beira; a máscara
`LUGARES_LUZ.cais` como `emissiveMap` (`flipY = false`), como a do portão. O cais na ilha é futuro (o multiplayer): o modelo entra, a cena não.

Com o cais, os três lugares da tarefa estão entregues.

## 12. Os lugares na ilha e no estilo dela (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-lugares-na-ilha`)

**Por que aqui:** a sessão da L3 ("Lugares da ilha") não existe mais, e o Matheus pediu que eu pusesse os três na cena e melhorasse as
texturas, para os modelos se encaixarem no estilo do mapa e ficarem mais bonitos (D-LG-14).

**O que entrou:**
- `web/app/src/telas/pet/ilha/lugares.ts`: carrega os três pelo `carregarVariante`, com a sombra redonda, e acende a máscara do lugar
  aberto. Ainda não há o nível do Tamer, então `LUGAR_ABERTO` diz o estado: o portão e a barraca abertos, o cais trancado (D-LG-16).
  Entra nos mapas Ilha e Digital, como os enfeites (`estilos.ts`).
- `grade.ts`, `porLugares`: depois dos enfeites, com a rng própria. O portão e a barraca ficam ao norte da área, no ponto que cabe mais perto
  de um alvo ao lado do ninho; o cais fica na última linha de areia antes do mar. Cada lugar abre uma clareira: a vista não desenha a
  decoração ali (`Ilha.escondidos`), e a lista `objetos` não muda (o E-G0 passa). Os números estão em `LUGARES_GRADE` e `LUGAR_LUZ`, em
  `constantes.ts` (D-LG-15).
- **O estilo da Ilha nas texturas:** `docs/lugares3d/estilo_ilha.py` troca cada cor chapada pela versão da Ilha, mais escura e mais saturada,
  perto dos kits. As cores novas ficam na `paleta_ilha` de cada `paleta.json`, e a textura de antes fica em `conserto/cor_antes_ilha.png`.
  A saída é um PNG de paleta, sem perda e uns 35 % mais leve (D-LG-17).
- `web/app/test/ilha_lugares.test.ts`: LG-G1 a LG-G5 (onde ficam, a frente para a área, a clareira e a paleta publicada).

**As capturas** (fora do git): `D:\Trab\digilab\capturas_lugares3d\ilha\`.
- Depois: `visao_ilha.jpg`, `visao_digital.jpg`, `barraca_ilha.jpg`, `portao_ilha.jpg` e `cais_ilha.jpg`.
- Antes: `antes_cais_pastel.jpg`, `antes_portao_arvores.jpg` e `antes_barraca_oeste.jpg`.

**Fica para depois:**
- o nível do Tamer: o cadeado e o "Nv" no lugar trancado, o brilho de quando o lugar abre e a entrada pelo lugar, que hoje não se clica;
- o cais é visto da água pela câmera de trás.

A entrada da barraca lê na ilha (o vão escuro sob o arco), então refazer a malha (D-LG-9) não é necessário.
