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

## 13. A entrada pelos lugares (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-lugares-entrada`)

**Por que aqui:** depois do #678 o Matheus pediu para seguir com as recomendações. A entrada pelos lugares não depende do nível do Tamer,
porque o portão e a barraca já estão abertos (D-LG-18). O nível do Tamer fica para a tarefa de código dele (o item 3 da seção 9 do
`docs/PLANO_V3_PROGRESSAO_TUTORIAL.md`).

**O que entrou:**
- `web/app/src/telas/pet/ToqueLugar.tsx`, ligado no `Habitat.tsx` com o `irDestino` do `App.tsx`:
  - o toque no portão abre o Lutar, e o toque na barraca abre o Diário;
  - o cais, trancado, não faz nada;
  - com o mouse, o cursor vira a mão sobre um lugar que abre (D-LG-19).
- **Na vista:**
  - `lugares.ts` devolve a caixa de cada lugar (`caixas`, no `Objetos.lugares`);
  - `vista.ts` ganha `lugarEm` e o põe no `CENA.mundo`;
  - `lugarNoPonto`, em `curva.ts`, projeta a caixa com a dobra (D-LG-20).
- **As tabelas:** `LUGAR_ABERTO`, `LUGAR_DESTINO` e o tipo `NomeLugar` ficam em `web/app/src/telas/pet/lugaresIlha.ts`, fora da `ilha/` e
  sem three (a fronteira da ilha).
- **O teste:** o LG-G6 em `web/app/test/ilha_lugares.test.ts` confere o retângulo, os destinos e o gesto.

**Fica para depois:** o nível do Tamer, que traz o cadeado e o "Nv" no lugar trancado, o toque no lugar trancado e o brilho de quando o
lugar abre.


## 14. O portão retrabalhado com a textura pintada (2026-11-07, worker, Claude Code, Opus 5.5, branch `v3-objeto-portao`)

**Por que aqui:** o Matheus achou os objetos 3D feios e "sem textura" e pediu que cada um fosse refeito numa sessão própria, o mais perto
possível do esboço escolhido (`docs/objetos3d/REFERENCIAS.md`, seção 5). O portão segue o esboço 1, o arco de blocos de pedra
(`docs/objetos3d/portao/esbocos/esboco_1_pedra_blocos.png`).

**O que entrou:**
- **A malha nova pela Meshy:** a multivista a partir da tarefa do esboço (6 créditos) e a malha (30), uma tentativa só, dentro do teto de 36. Os
  arquivos e os JSON das tarefas estão em `docs/objetos3d/portao/vistas/` e `malha/`, e o gasto em `docs/objetos3d/portao/saldo.json`.
- **O acabamento** (`docs/objetos3d/portao/acabar_portao.py`, no Blender 4.5 pela linha de comando):
  - a malha 1,5 vez mais funda, como o D-LG-4, e os vértices repetidos soldados;
  - a folha do portal aplainada, com a normal do plano (D-OBJ-PO-2);
  - a ilha única de UV do portal (D-OBJ-PO-3);
  - as normais ponderadas, com as quinas acima de 60° vivas;
  - 2 012 triângulos (teto 2 414), a frente em +z e a base no chão.
- **A textura** (`textura_portao.py`): a pintada da Meshy fica, sem achatar. Só as manchas brancas saem, e entram os retoques do revisor:
  o dourado e o vermelho dos estandartes mais vivos e um realce leve das juntas. O portal vem da vista de frente da multivista, com a grade
  e a espiral. A textura vai a 512 px numa paleta de 240 cores com pontilhado, para caber nos 300 KB (D-OBJ-PO-1). A máscara do portal
  (`portao_luz.png`, 512 px) sai dos triângulos de UV do portal, então fica alinhada com os UVs novos por construção.
- **A publicação** (`publicar_portao.py`): a marca de IA no `asset.extras`, os arquivos em `web/app/public/lugares/portao/` (268 449 bytes)
  e o glTF-Validator (`validar_gltf.cjs`; 0 erros, 0 avisos em `docs/lugares3d/portao/validacao.json`). A altura (5 células), a grade e
  as posições não mudam.
- **Os testes:** o LG-G5 (a paleta da Ilha) deixa de valer para o portão e continua valendo para os outros lugares. O LG-G5b, novo, confere
  a textura pintada: a cor é um PNG quadrado de 512 a 1 024 px com mais de 64 cores, e a máscara de luz cai no ciano da textura. Os dois
  estão em `web/app/test/ilha_lugares.test.ts`, lista `TEXTURA_PINTADA` (D-OBJ-PO-1). Os gates G1 a G8 de `web/app/test/lugares3d.test.ts`
  ficam como estavam e passam.

**As capturas** ficam fora do git, em `D:\Trab\digilab\capturas_objetos3d\portao\`:
- a prancha `prancha_portao.png`: o esboço, o antes e o depois na vitrine, e o antes e o depois no jogo nos mapas Digital e Ilha;
- as imagens soltas `vitrine_*`, `antes_*` e `depois_*` (`*_cena` é a cena sem o menu; `*_lugar` é a viagem ao portão, com o Lutar aberto).

Para o estilo Digital, a vitrine e o jogo rodaram numa worktree só de captura, montada do branch do #692 (`v3-mapa-digital-d5`).

**O revisor** (um subagente que não fez o trabalho) deu três pareceres:
1. **APROVA COM RESSALVA:** o portal manchado e apagado, o dourado sumindo e as juntas fracas.
2. **APROVA COM RESSALVA:** o portal ficou liso e o ciano vazou para as ilhas vizinhas, os dois efeitos do primeiro conserto.
3. **APROVA,** depois da ilha única do portal.

Ficam como estão:
- o estandarte esquerdo meio torto, a proporção mais atarracada que no esboço e a barra que, de lado, parece uma lança. São da malha e
  pediriam outra geração;
- uma névoa clara na emenda esquerda do portal, que quase não aparece no jogo.

**Fica para depois:** o portal no jogo é um ciano mais apagado que na vitrine. A força da luz é `LUGAR_LUZ.forca`, em `constantes.ts`,
fora deste trabalho. A grade do esboço é pintada e parada, não gira.

## 15. O retrabalho da barraca (2026-11-08, worker, Claude Code, Opus 5.5, branch `v3-objeto-barraca`)

**O pedido:** refazer a barraca o mais perto possível do esboço 1 do retrabalho (`docs/objetos3d/barraca/esbocos/esboco_1_domo_costuras.png`,
o domo turquesa com costuras e remendos, a entrada enrolada, as cordas laranja, a lona, a antena e o banquinho com livros), com a regra
nova da textura (`docs/objetos3d/REFERENCIAS.md`, seção 5: não achatar, normais suavizadas) e a entrada lendo como vão de verdade.

**O que entrou:**
- `web/app/public/lugares/barraca/`: o glTF novo (1 847 triângulos, 1 nó, 1 material só de cor), a textura pintada em 512 px com 256
  cores e o `License.txt`; 223 KB no total. A marca de IA e as tarefas da Meshy no `asset.extras`.
- `LUGARES_MODELOS.barraca` em `modelos.ts`: altura 3,6 e sombra 2,2 (PROPOSTO; D-LG-OB-4).
- `web/app/test/ilha_lugares.test.ts`: a lista `TEXTURA_PINTADA` tira a barraca do LG-G5, e o LG-G5b confere o detalhe guardado e o chão
  de dentro escuro (D-LG-OB-1).
- `docs/objetos3d/barraca/`: a multivista e a malha da Meshy (`vistas/`, `malha/`), o `saldo.json` e os scripts, na ordem do
  `publicar_barraca.py`: `faces.py` e `interior.py` (Blender, as faces e as de dentro), `textura_barraca.py` (o escuro de dentro, as cordas
  laranja e o chão), `acabar_barraca.py` (Blender: os vértices fundidos, as normais a 60°, o pivô na base, a frente em +z, o chão e o forro)
  e `publicar_barraca.py` (a redução da textura e a marca de IA). O validador em `docs/lugares3d/barraca/validacao.json` (0 erros, 0 avisos).

**Os números e os achados:** D-LG-OB-1 a D-LG-OB-6 no `docs/registro/2026-11.md`. O principal: a lona nova, mais funda, entra no degrau do
barranco atrás do ponto da barraca; o forro de dentro esconde as pedras, e a altura desceu de 4 para 3,6.

**A prancha e as capturas** (fora do git): `D:\Trab\digilab\capturas_objetos3d\barraca\` — `prancha_barraca.png` (o esboço, o antes e o
depois na vitrine, o antes e o depois no jogo, nos mapas Ilha e Digital), `vitrine_antes_*.png`, `vitrine_depois_*.png`,
`visao_ilha.png`, `visao_digital.png`.

**O revisor:** APROVA COM RESSALVA (a porta lê como abertura escura nos dois mapas; as cordas só leem laranja no mapa Ilha, por causa do
traço). O que fica sem conserto está no D-LG-OB-6.

**A Meshy:** 36 créditos (multivista 6 + malha 30), no teto da sessão.

**Ao mesclar com o portão (seção 14, Gerente, 2026-11-08):** os dois trouxeram um LG-G5b. Em `web/app/test/ilha_lugares.test.ts` fica o do portão (512 a 1024 px, quadrado, mais de 64 cores, a máscara de luz no mesmo UV) para os dois, com a barraca em `TEXTURA_PINTADA`, e o chão escuro da barraca vira um teste próprio no mesmo bloco.

## 16. O cais retrabalhado com a textura pintada (2026-11-08, worker, Claude Code, Opus 5.5, branch `v3-objeto-cais`)

**Por que aqui:** o Matheus achou os objetos 3D feios e "sem textura" e pediu que cada um fosse refeito numa sessão própria, o mais perto
possível do esboço escolhido (`docs/objetos3d/REFERENCIAS.md`, seção 5). O cais segue o esboço 1: o píer curto de tábuas com os postes
enrolados em corda e o barquinho de pesca azul e amarelo com a cabine (`docs/objetos3d/cais/esbocos/esboco_1_pier_barco.png`).

**O que entrou:**
- **A malha nova pela Meshy:** a multivista a partir da tarefa do esboço (6 créditos) e a malha (30), uma tentativa só, no teto de 36. O
  prompt da multivista tira a água do esboço (o mar é o da ilha). Os arquivos e os JSON das tarefas estão em `docs/objetos3d/cais/vistas/` e
  `malha/`, e o gasto em `docs/objetos3d/cais/saldo.json` (86 → 80 → 50).
- **O acabamento** (`docs/objetos3d/cais/acabar_cais.py`, no Blender 4.5 pela linha de comando): a malha como a Meshy deu, com a frente em
  +z como o cais de antes (o píer ao longo de x, o barco atrás, do lado do mar); a base no chão e o centro no meio; os vértices repetidos
  soldados e as faces degeneradas tiradas; tudo liso com normais ponderadas e as quinas acima de 60° vivas. São 2 159 triângulos (teto 2 414).
- **A textura** (`textura_cais.py`, o mesmo caminho do vagão, #710): a pintada da Meshy fica, sem achatar. O azul, o amarelo e o musgo ganham
  um pouco de saturação, e a madeira vai para o brilho medido no esboço (D-OBJ-CAIS-2). Fica em 512 px, numa paleta de 192 cores com
  pontilhado, para caber nos 300 KB.
- **A publicação** (`publicar_cais.py`): a marca de IA no `asset.extras`, os arquivos em `web/app/public/lugares/cais/` (291 797 bytes) e o
  glTF-Validator (`docs/itens3d/validar.cjs`; 0 erros, 0 avisos em `docs/lugares3d/cais/validacao.json`). A máscara `cais_luz.png` sai
  (D-OBJ-CAIS-3). A altura em `LUGARES_MODELOS.cais` vai de 2,4 para 1,8 (D-OBJ-CAIS-1). A grade e as posições não mudam.
- **Os testes:** o cais sai do LG-G5 (a paleta da Ilha) e entra no LG-G5b (a textura pintada: PNG quadrado de 512 a 1 024 px com mais de
  64 cores), pela lista `TEXTURA_PINTADA` de `web/app/test/ilha_lugares.test.ts`, a mesma do portão (#713). Os gates G1 a G8 de
  `web/app/test/lugares3d.test.ts` ficam como estavam e passam.

**As capturas** ficam fora do git, em `D:\Trab\digilab\capturas_objetos3d\cais\`: a prancha `prancha_cais_final.png` (o esboço, as prévias do
Blender, o antes e o depois no jogo nos mapas Digital e Ilha; o depois do Digital já com o traço de nanquim do #692, mesclado na `main`
durante o trabalho) e as imagens soltas `antes_*`, `depois_*` (antes da mescla) e `depois_d5_*` (depois dela). Uma cópia da prancha está
em `docs/objetos3d/cais/conserto/prancha.jpg`. As capturas no jogo usam a câmera de desenvolvimento (`?cameradev=1`, `__camera.ir("cais")`)
num Vite próprio.

**O revisor** (um subagente que não fez o trabalho) deu dois pareceres:
1. **APROVA COM RESSALVA:** a madeira escura e lisa demais, a corda sem o bege, a corda de amarração como fita, o píer na areia sem água,
   o barco grande e a silhueta mais longa e fina que a do esboço.
2. **APROVA COM RESSALVA,** depois do brilho da madeira: sem problema novo; ficam as ressalvas da malha.

**Ficam como estão:** a corda de amarração em fita, a silhueta longa, o tamanho do barco e o musgo que a Meshy não pintou (só uma malha nova
resolve, e o teto era de uma tentativa); a água sob o píer (o modelo não leva água, e a posição não muda).

## 17. O cais em voxel (2026-11-08, worker, Claude Code, Opus 5.5, branch `v3-objeto-cais-voxel`)

**Por que aqui:** com o cais da seção 16 pronto (#729), o Matheus pediu referências para deixar o barco "mais digital, mais pixelado". Três
caminhos foram mostrados: voxel, textura em pixel grande e detalhes digitais em ciano. Um teste local mostrou que a textura em pixel grande
não funciona no atlas picotado da Meshy, e que o voxel funciona. O Matheus escolheu o voxel.

**O que entrou:**
- **O voxel** (`docs/objetos3d/cais/voxel_cais.py`, no Blender 4.5 pela linha de comando). Nenhum crédito da Meshy: a forma e a cor vêm da
  malha e da textura pintada da seção 16. Os passos:
  - a grade tem 48 blocos no comprido (48 × 22 × 12);
  - o bloco é cheio quando a superfície passa a menos de 0,6 lado de bloco do centro dele;
  - a cor do bloco é a média da textura em 7 pontos da malha (o centro e 6 em volta);
  - as faces que dão para um bloco vazio são juntadas em retângulos por plano, e cada retângulo leva 2 × 2 texels por face de bloco num
    atlas de 512 px, com 1 texel de borda repetida;
  - as normais são as dos planos (cubo de verdade).

  São 2 156 triângulos (teto 2 414): com 64 blocos no comprido seriam 3 408. A textura do realce sai do `textura_cais.py` com `cores 0`,
  que tira a paleta.
- **A publicação** (`publicar_cais.py ... voxel`): o sampler NEAREST nos dois filtros, para o pixel duro sem mipmap (o mipmap misturaria
  os blocos vizinhos do atlas). São 174 953 bytes, e o glTF-Validator deu 0 erros e 0 avisos.
- **A altura** vai de 1,8 para 1,9, para manter os ~7,6 células de comprimento (o voxel é um pouco mais alto que a malha).
- **Os testes:** o cais fica no LG-G5b, na lista `TEXTURA_PINTADA` de `web/app/test/ilha_lugares.test.ts`, como pediu o Gerente: o atlas
  é um PNG quadrado de 512 px com mais de 64 cores. O sampler NEAREST não tem teste próprio (D-OBJ-CAIS-V4).

**As capturas** ficam fora do git, em `D:\Trab\digilab\capturas_objetos3d\cais\`: a prancha `prancha_voxel.png`, com o esboço, as prévias,
o cais pintado do #729 e o voxel no jogo, e as imagens soltas `voxel_*`. O teste dos três caminhos fica em `teste_digital\`. Uma cópia da
prancha está em `docs/objetos3d/cais/voxel/prancha.jpg`.

**O revisor** (um subagente que não fez o trabalho) deu APROVA COM RESSALVA: lê-se como voxel de verdade, e o barco é reconhecível. Ficam de
fora os anéis de corda nos postes, a janela da cabine e os tons por tábua, que seriam pintura nova (D-OBJ-CAIS-V8).

## 18. O cais feito à mão por script (2026-11-10, Gerente, Claude Code, Fable 5.2, branch `v3-objeto-cais-mao`)

**O pedido:** depois do carro e da geladeira feitos por script (`docs/TAREFA_V3_MUNDO_ENFEITES.md`, seções 15 e 16), o Matheus pediu:
"agora eu quero que você faça a mesma coisa com o cais". O cais em voxel da seção 17 sai do jogo.

**O cais (`docs/objetos3d/cais/mao/`):**
- `cais_mao.py`: segue o esboço 1 (o píer de tábuas, as estacas amarradas de corda, o musgo e o barquinho azul e amarelo com a cabine),
  mas nada vem da Meshy. O píer agora sai da areia para o mar: uma rampa, a passarela e a ponta mais larga (um L), com o barco atracado ao
  lado. As peças são sólidos simples: 11 tábuas de quinas vivas, cada uma com o tamanho e o giro um pouco diferentes (uma quebrada), 4
  vigas, 7 estacas, 4 voltas de corda, o casco por seções, a cabine com o teto de lona, 2 cabos de amarrar, o barril, o caixote, a boia, o
  musgo, as flores e o capim. A pintura é uma função da posição no espaço, só com cores chapadas. Os sólidos, o atlas e a escrita do glTF
  são os do `carro_mao.py`;
- `publicar_mao.py`: a procedência no `asset.extras`, a troca em `web/app/public/lugares/cais/` e o validador (0 erros, 0 avisos).

**No jogo:** 1 704 triângulos (teto 2 414), 198 kB com o `License.txt` (teto 300 kB), um nó, uma malha, uma textura de 1024 px.
- **As medidas do script estão em células da ilha**, e a altura da tabela (1,96) é a do modelo: a escala é 1.
- **O pé do modelo fica no fundo do mar** (`FUNDO_AGUA`), não mais na areia: as estacas e o casco do barco entram na água.
- **O meio do modelo fica 0,9 célula mar adentro** (`PLANTA_ILHA.lugares.cais.mar`). A vista centra o modelo pela caixa dele; sem isso, a
  metade do píer ficava em cima da grama. Com isso a rampa começa na borda da areia, onde o caminho de terra chega.
- O `web/app/test/lugares3d.test.ts` aceita as duas procedências (a marca de IA da Meshy ou o script do feito à mão, como nos enfeites) e
  ganha o teste do cais: a procedência, a escala 1, o pé no fundo do mar e o avanço.

**Não feito:** não houve revisor separado nem prancha de capturas no git; a conferência foi na vitrine e no jogo, no estilo da Ilha, de dia
e de noite. O estilo Digital dentro do jogo, o celular e o e2e não foram conferidos. O toque no cais usa a caixa do modelo, que mudou de
forma; o cais segue trancado. Os desvios estão em `docs/registro/2026-11.md`, D-OBJ-CAIS-M1 a M4.

## 19. O portão e a barraca em cartoon, feitos à mão por script (2026-11-10, Gerente, Claude Code, Fable 5.2, branch `v3-objetos-cartoon`)

**O pedido do Matheus (2026-11-10):** "então faz tudo em estilo cartoon pra ver como fica", depois do levantamento do padrão dos objetos.
É um teste para ele olhar: a decisão entre o cartoon e o voxel continua dele.

**O que mudou:**

- **O portão** (`docs/objetos3d/cartoon/portao.py`) troca o da Meshy. Segue o esboço 1: dois pilares de quatro blocos de pedra, um arco
  de sete pedras em cunha com a chave maior, o portal ciano (a grade e o redemoinho pintados num plano), duas flâmulas vermelhas na
  frente e o musgo. 457 triângulos. A máscara `portao_luz.png` acende o portal quando o lugar abre, como antes.
- **A barraca** (`docs/objetos3d/cartoon/barraca.py`) troca a da Meshy. Segue o esboço 1: o domo turquesa de base quadrada arredondada,
  as costuras nas quatro varetas, os remendos, o rolo da porta, a antena no alto, os quatro estais com as estacas e o banquinho com os
  livros. A porta é pintada no domo (a entrada sem vão, como antes). 743 triângulos.
- A altura, a sombra e o ponto de cada lugar não mudam. O motor, o log e o save não mudam.
- A base comum e o script que publica estão em `docs/objetos3d/cartoon/` (o `docs/TAREFA_V3_MUNDO_ENFEITES.md`, seção 18).
- **O conserto do cais (D-OBJ-CAIS-M5):** ao fazer o vagão, a caixa de quinas vivas do `cais_mao.py` mostrou duas das cinco faces de
  costas. O conserto entrou no branch do cais (#752), e o cais foi regerado.

**Os testes:** o `web/app/test/lugares3d.test.ts` confere a procedência dos dois; o `web/app/test/ilha_lugares.test.ts` troca o teste do
chão de dentro da barraca (ele lia um ponto da textura da Meshy) por um que confere o escuro pintado da porta.

**Não feito:** não houve revisor separado nem prancha de capturas no git. No jogo, o portão e a barraca aparecem apagados porque estão
trancados no save de teste (o nível do Tamer); as cores foram conferidas na vitrine. O lugar aberto (o portal aceso), o estilo Digital,
o celular e o e2e não foram conferidos. Os arquivos da Meshy ficam em `docs/objetos3d/portao/` e `docs/objetos3d/barraca/` como
histórico. Os desvios estão em `docs/registro/2026-11.md`, D-CARTOON-1 a 5.
