# TAREFA V3 — ITENS_3D (2026-11-05)

Coordenador: o Gerente da frente ITENS_3D (Claude Code, Opus 5.5, nesta sessão). Worker: a definir, depois das decisões da seção 8.
Worktree e branch: `v3-itens-3d`. Status: ABERTA; D-I1 a D-I6 DECIDIDAS (2026-11-05); nada foi instalado, gerado ou pago.

Categoria: arquitetura. Origem: Matheus, 2026-11-05: um pipeline para gerar itens próprios da ilha em glTF (bola, cocô, frutas, saco, kit
médico) com o MCP for Blender e um gerador de malha, entrando na ilha com procedência própria.

Lido para esta tarefa: `CLAUDE.md`, `web/app/CLAUDE.md`, `docs/PAINEL_V3.md`, `docs/TAREFA_V3_HABITAT_OBJETOS.md` (HO-1 a HO-3 valem e
não são reabertas), `docs/TAREFA_V3_HABITAT_ILHA_3D.md`, `web/app/src/telas/pet/ilha/modelos.ts`, `itens.ts`, `cocos.ts`, `cena.ts`
(o carregador), `test/ilha_modelos.test.ts`, as licenças em `web/app/public/kits3d/*/License*.txt`, `docs/UI_GUIDELINES.md` §5.1 e, no
vault, `40 Produção e divulgação/05_ARQUITETURAS_ORQUESTRACAO.md` (seção 4 e "Padrões que se repetem").

## 1. Pergunta

Um item gerado (bola, cocô, fruta, saco, kit médico) entra na ilha pela mesma tabela de modelos dos kits CC0 com a mesma qualidade visual
e o mesmo custo de render dos kits?

- Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é produto (trilha L, a ilha da L4). Não há run nem semente.
- "Mesma qualidade visual" é julgada por um revisor que não fez o item e pelo Matheus (seção 7). "Mesmo custo de render" é medido:
  triângulos, texturas, bytes e draw calls (seção 4.2) e o fps da M3 (seção 7).

## 2. Depende de

- **A ilha na `main`:** a L4, H0 a H5 (#488 a #494) e os mapas trocáveis (#520). O carregador dos kits (`carregarVariante`, `cena.ts`)
  é o que os itens reusam.
- **O cocô 3D na `main`:** o #567 (`15ce588b`), que trouxe `ilha/cocos.ts` e o `CENA.cocoNoChao`. O cocô gerado troca só o desenho
  (o `criar(i)` que o `Itens` passa ao `Cocos`); o lugar, o pulinho e a sincronização com a sujeira ficam como estão.
- **A bola física na `main`:** o pet v15 com a `bolaNoGolpe` (HABITAT_OBJETOS, HO-1). O item só troca o desenho; a posição continua a
  do motor.
- **As decisões da seção 8**, antes de qualquer gasto ou instalação.
- **A referência visual:** as capturas da ilha da H5 (`D:\Trab\digilab\capturas_ilha_h5\`, 390 e 1280; claro, escuro e noite). Elas
  ainda esperam a aprovação do Matheus (PAINEL, seção 2). Por isso a referência de cada item é a mesma cena com o item procedural de
  hoje, lado a lado (seção 7).

## 3. Mudança mínima

**O que entra (por item):**
- Os arquivos do item em `web/app/public/itens/<item>/`: o `.gltf`, o `.bin`, uma textura de cor e um `License.txt` de procedência
  própria (o gerador, o plano e a data, os termos de uso do gerador na data, o prompt e as imagens de entrada, quem aprovou; UI_GUIDELINES
  §5.1).
- A linha do item na tabela de modelos (`web/app/src/telas/pet/ilha/modelos.ts`), no mesmo formato `Modelo` (arquivos, altura em
  células, vento 0, sombra, baixo).
- O teste que confere os itens (seção 4.2), em `web/app/test/`.
- Os artefatos do pipeline fora de `public/`: `docs/itens3d/<item>/` com o concept aprovado, as vistas, o relatório do validador, as
  medidas e as capturas.

**O que NÃO muda:** nada do motor (`web/app/motor/`, `digilab/`), nenhum evento, log, save, versão de pet ou gabarito; os kits CC0 em
`public/kits3d/` e o orçamento de 8 MB deles (H-1); o `engine.py`.

**Dois achados que a mudança mínima pedida não cobre (para o Matheus decidir, seção 8):**
1. **Uma linha nova em `MODELOS` quebra os tipos de outros três arquivos.** `cassette.ts`, `floresta.ts` e `voxel.ts` declaram
   `Record<NomeModelo, ...>`, então cada chave nova de `MODELOS` exige uma peça em cada um dos três estilos do habitat, e o teste "o
   script copia a mesma lista da tabela" (`ilha_modelos.test.ts`) falha, porque o `kits3d_copiar.py` não conhece os itens. `MODELOS` é
   hoje a tabela da decoração da grade; os itens não são decoração sorteada. A recomendação (D-I4) é uma tabela irmã, `ITENS_MODELOS`, no
   mesmo `modelos.ts` e com o mesmo tipo `Modelo`.
2. **Para o item aparecer na ilha, a vista precisa carregá-lo.** Hoje a bola, a fruta, o cocô, o saco e o kit médico são desenhos
   procedurais em `itens.ts`; nenhum lê a tabela. Sem uma troca pequena em `itens.ts` (a função do item passa a usar o `carregarVariante`
   de `cena.ts`, que já normaliza a caixa para a altura da tabela), não há captura nem fps a medir. É código da vista, não do motor. A
   recomendação é incluir essa troca, só para o item da etapa, no mesmo PR (D-I4).

## 4. Pipeline, gates e gerador (sem run de pesquisa)

Sem plano de análise, sem sementes, sem GPU de pesquisa: nada aqui é vida do pet.

### 4.1 O pipeline e os papéis

Cada etapa só começa quando a anterior passou o gate dela (padrão 2 do vault: o número antes do olho).

| # | etapa | quem faz | o que sai | gate para seguir |
|---|---|---|---|---|
| 0 | **Orçamento** | Gerente | a cotação do item em créditos e reais (seção 4.3) | dentro do teto que o Matheus aprovou |
| 1 | **Concept 2D** | produtor (worker), com um modelo de imagem | 3 a 4 concepts do item numa imagem, com **uma referência de estilo tirada da própria ilha** (um recorte de `capturas_ilha_h5/ilha_1280_claro.png` com os kits e o item procedural de hoje) | o Matheus escolhe um (o quadro-mestre, padrão 3) |
| 2 | **Multivista** | produtor | frente, lado e costas do concept escolhido, fundo liso | as vistas batem com o concept (o produtor confere; o revisor vê na etapa 8) |
| 3 | **Malha** | o gerador (seção 4.3), chamado pelo produtor | malha texturizada em GLB, do multi-image-to-3D | o arquivo abre |
| 4 | **Remesh** | produtor, no gerador (remesh com alvo) ou no Blender (Decimate) | a malha no teto de triângulos da categoria | gate G1 |
| 5 | **Escala** | produtor | a altura da linha da tabela (células); o carregador normaliza a caixa para ela e põe a base em y = 0 | gate G2 |
| 6 | **Cor (o "PBR")** | produtor, no Blender | uma textura de cor só, até 1024 px; o resto do PBR sai | gates G3, G4, G5 |
| 7 | **Exportação glTF** | produtor | `.gltf` + `.bin` + `.png`, sem Draco e sem extensão | gate G6 (o validador) e G7 (bytes) |
| 8 | **Render na ilha** | produtor | capturas da ilha com o item, pelo próprio jogo (Playwright, o portão de capturas da ilha) — o render no Blender pelo MCP serve só de rascunho, porque não tem o material toon nem a dobra da ilha | as capturas existem nas mesmas posições da referência |
| 9 | **Revisão** | **revisor novo**: uma sessão que não fez o item e não vê os prompts nem os gates, só o concept escolhido, a captura de referência e a captura com o item | aprova ou devolve com o defeito apontado na imagem | aprovado pelo revisor; depois o Matheus (seção 7) |

**Por que o "PBR" vira só cor:** o carregador da ilha (`carregarVariante`, `cena.ts:299`) troca todo material por `MeshToonMaterial`
e aproveita só o `map`, a `color` e as cores de vértice. Normal, metálico, rugosidade e emissivo do gerador seriam bytes que nunca chegam
à tela (a H-1 já tirou o mapa normal dos kits pelo mesmo motivo). O gerador pode texturizar em PBR; o produtor guarda só a cor base, sem a
luz assada (o toon da ilha dá a sombra). O carregador também levanta erro com mais de um material por malha.

**O Blender:** não está instalado nesta máquina (procurado em `Program Files`, no `PATH`, no registro de programas e nos pacotes da
Store, 2026-11-05). As etapas 4 a 7 precisam dele ou de uma ferramenta de linha de comando para glTF; o MCP for Blender (vault 4.1) usa um
socket local sem autenticação. Instalar é decisão do Matheus (D-I5).

### 4.2 Os gates numéricos por item (PROPOSTOS)

Medidos nos 28 modelos da tabela `MODELOS` de hoje (o script está na seção 9, com a saída; os números são da `main` `389f3893`):

| categoria dos kits | modelos | triângulos (mín – mediana – máx) | texturas |
|---|---|---|---|
| baixos (`baixo: true`: flor, trevo, grama, grama alta, samambaia, cogumelo) | 12 | 155 – **554,5** – 3 216 | 512 a 1024 px |
| altos (árvore, pinheiro, arbusto, pedra) | 16 | 12 – **2 414** – 6 265 | 1024 px |
| todos | 28 | 12 – 817,5 – 6 265 | 1 008 × 981 a 1024 × 1024; nenhuma acima de 1024 |

Em todos os 28, cada primitiva tem textura de cor (`baseColorTexture`), há um material por malha e não há mapa normal, metálico ou emissivo.

| gate | o que confere | valor PROPOSTO | onde |
|---|---|---|---|
| G1 triângulos | abaixo do teto da categoria do item | itens pequenos (bola, cocô, fruta, kit médico, altura ≤ 0,8 célula): **≤ 554**, a mediana dos baixos; o saco (≈ 2,5 células, com o poste): **≤ 2 414**, a mediana dos altos | teste |
| G2 caixa | a altura da linha da tabela é a do item procedural de hoje, para o tamanho na tela não mudar: bola **0,72** (2 × `R_BOLA` 0,36), fruta ≈ 0,45, cocô e kit médico medidos no procedural na etapa | a caixa do glTF tem altura > 0 e proporção (largura/altura) dentro de ±25 % da do concept | teste e carregador |
| G3 texturas | tamanho de cada imagem | PNG ou JPG, lado ≤ **1024 px**, potência de 2 | teste |
| G4 material | nenhuma primitiva sem textura de cor; um material por malha | 0 sem textura | teste |
| G5 mapas inúteis | nada de normal, metálico/rugosidade, oclusão ou emissivo | 0 | teste |
| G6 validador | o Khronos glTF-Validator, rodado no pipeline por `npx gltf-validator` (sem dependência nova no `package.json`) | 0 erros, 0 avisos; o relatório JSON em `docs/itens3d/<item>/` | artefato, conferido pelo teste (o relatório existe e tem 0 erros) |
| G7 bytes | `.gltf` + `.bin` + imagens por item; a pasta `public/itens/` inteira | ≤ **300 KB** por item; ≤ **2 MB** a pasta (fora dos 8 MB dos kits) | teste |
| G8 procedência | o `License.txt` ao lado de cada item, com gerador, data, termos e aprovação | existe e cita o gerador | teste |
| G9 draw calls | o item gerado não desenha mais que o procedural que ele troca (a bola de hoje: a esfera e a sombra) | `draw_calls` da M3 com o item ≤ o de antes | M3, na captura |

### 4.3 A escolha do gerador e o custo

**A máquina (medida em 2026-11-05):** NVIDIA GeForce RTX 2060 com **6 GB** de VRAM (`nvidia-smi`: 6 144 MiB, 2 121 MiB em uso com a
área de trabalho aberta), 32 GB de RAM, 149 GB livres em C: e 74 GB em D:. Blender: não instalado.

| gerador | onde roda | cabe? | custo por tentativa (multivista + textura + remesh) | custo dos 5 itens (até 3 tentativas cada) |
|---|---|---|---|---|
| **Meshy** (API, MCP oficial) | nuvem | sim | 30 créditos (multi-image + textura 2K) + 5 (remesh) = 35 créditos ≈ **R$ 3,78** | ≈ 525 créditos + retexturas: cabe nos 1 000 créditos de **um mês do Pro, R$ 107,90** (o mínimo para ter a API) |
| **Tripo** (API) | nuvem | sim | 40 a 100 créditos a US$ 0,01 = US$ 0,40 a 1,00 ≈ **R$ 2,15 a 5,38** | ≈ **R$ 32 a 81**; o mínimo de compra não foi conferido |
| **TRELLIS.2** | local | **não**: pede 24 GB de VRAM e Linux | — | — |
| **Hunyuan3D-2.1** | local | **não**: 10 a 29 GB | — | — |
| TripoSR (via Meshwire) | local | sim (4 GB), com qualidade menor (vault 4.4 e 4.7) | R$ 0 | R$ 0, mais a instalação |

- Fontes dos preços (lidas em 2026-11-05): a tabela de créditos da API da Meshy (`docs.meshy.ai/en/api/pricing`), os planos da Meshy em
  reais (`meshy.ai/pricing`: Pro R$ 107,90 com 1 000 créditos por mês; a API só a partir do Pro) e a página da API da Tripo
  (`developers.tripo3d.ai`: 1 crédito = US$ 0,01; multivista 20–30, textura 10–30, retopologia 10–40). O dólar: R$ 5,20 (a mediana
  do Focus para o fim de 2026) mais 3,5 % de IOF no cartão ≈ R$ 5,38; a cotação do dia não foi encontrada.
- O concept (etapa 1) tem custo à parte: a imagem da Tripo custa 5 créditos (≈ R$ 0,27); um modelo de imagem que o Matheus já assina sai
  sem custo marginal.
- **Os termos de uso** de cada gerador (de quem é a malha, se o plano grátis impõe licença) não foram conferidos nesta sessão; o worker
  confere e cita no `License.txt` antes da primeira chamada paga (G8).
- **Recomendação: Meshy, um mês do Pro.** Teto conhecido de R$ 107,90 pelos cinco itens; o remesh com alvo de triângulos e o
  multi-image-to-3D na mesma API; MCP oficial; e é o caso documentado com o MCP for Blender (vault 4.2: um cenário inteiro por cerca de
  US$ 5). A Tripo sai mais barata por item, mas sem MCP oficial e com o mínimo de compra a conferir. Local não cabe na RTX 2060, salvo o
  TripoSR, mais fraco.

## 5. Entrega

- Testes: em `web/app`: `npm test`, `npm run tipos` e `npm run e2e` (a frente toca a web). O Python não muda.
- Registro: seção própria no fim de `docs/registro/2026-11.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`. O resumo da
  etapa vai no corpo do PR e numa seção no fim deste documento, nunca no `CLAUDE.md`.
- **Um PR por item**, contra a `main`, com resumo e números (cada um com o artefato em `docs/itens3d/<item>/`). Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da
  categoria (implementacao, nas etapas dos itens).
- O registro do gasto: o saldo de créditos antes e depois de cada item, no corpo do PR (padrão 4 do vault).

## 6. Fora desta tarefa

- Rig e animação de itens; personagens e Digimon em 3D (o pet continua em papel).
- A cama, a comida, a carne e a luz dos kits CC0 baixados (HO-3: ficam para quando a ilha os usar).
- Qualquer mudança no motor, no log ou na física da bola; o lugar do cocô (continua só na vista, #567).
- Os outros estilos do habitat (cassette, floresta, voxel), se a D-I4 for a tabela irmã: eles seguem com os desenhos de hoje.
- Trocar os kits CC0 existentes por itens gerados.

## 7. Critérios de aceitação (por item)

- `web/app/test/ilha_modelos.test.ts` passa com os itens novos, e os gates G1 a G8 estão num teste que roda no `npm test`.
- `npm run tipos` passa.
- A captura da ilha com o item (1280 e 390; claro, escuro e noite; o mesmo save e a mesma câmera da referência) tem a referência
  aprovada: o revisor novo aprova, e depois o Matheus aprova o par lado a lado (o procedural de hoje e o gerado).
- O fps da ilha não cai: a M3 (`?medir3d=1`, `CenarioPet.tsx`) antes e depois, no mesmo mapa e câmera, com `draw_calls` igual ou menor
  (G9) e `fps_media` dentro de 5 % (PROPOSTO). O navegador do app limita a 30 Hz (H5, seção 10), então a medida de fps é do Matheus no
  Chrome do desktop; o `draw_calls` sai também no e2e.
- O `License.txt` e os artefatos de `docs/itens3d/<item>/` existem; o crédito do gerador entra em Ajustes › Sobre, como o dos kits.

## 8. Precisa do Matheus

**D-I1 a D-I6 DECIDIDAS pelo Matheus em 2026-11-05, pela recomendação** ("Sim, as seis", no chat desta sessão): a bola primeiro, a Meshy
com um mês do Pro, o teto pela mediana por categoria (554 e 2 414), a tabela irmã `ITENS_MODELOS` com a troca em `itens.ts`, instalar o
Blender LTS e o MCP for Blender (socket só em localhost, modo seguro) e o teto de gasto de R$ 120. A instalação, a assinatura e a primeira
geração ficam para a etapa da bola, num PR de implementação; esta tarefa não instala nem gasta. Os 300 KB por item, os 2 MB da pasta e os
5 % de fps (seção 4.2 e 7) continuam PROPOSTOS.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| D-I1 | qual item primeiro | **a bola**: a física já está no motor (HO-1), o lugar e o giro vêm do motor, e é o item que mais aparece | a bola é a forma mais fácil para o gerador (uma esfera com faixas): ela prova bem a integração (escala, giro em volta do centro, sombra, draw calls) e mal o gerador. Se ela passar e o kit médico falhar, a resposta à pergunta da seção 1 sai otimista; o custo é um item a mais (≈ R$ 4 a 12) para testar uma forma difícil. Errar para o lado do saco primeiro gasta mais tentativas no item mais caro (G1 de 2 414) |
| D-I2 | o gerador | **Meshy, um mês do Pro (R$ 107,90, 1 000 créditos)** | a Tripo custaria ≈ R$ 32 a 81 pelos cinco: escolher a Meshy paga até ≈ R$ 75 a mais pela previsibilidade e pelo MCP oficial. Escolher local não roda nesta GPU (só o TripoSR, com qualidade menor e um dia de instalação) |
| D-I3 | o teto de triângulos | **a mediana por categoria**: ≤ 554 para os itens pequenos, ≤ 2 414 para o saco | teto alto demais (a mediana geral, 817, ou o máximo, 6 265) deixa um item pequeno pesar mais que uma flor; baixo demais (o mínimo dos kits) força um remesh que estraga a silhueta. Como o custo da ilha é dominado pelas instâncias da grama e das árvores, um erro aqui custa pouco fps e muito retrabalho |
| D-I4 | a tabela e a vista | **uma tabela irmã `ITENS_MODELOS` em `modelos.ts`**, mais a troca do desenho do item em `itens.ts` no mesmo PR | entrar em `MODELOS` obriga a desenhar o item nos estilos cassette, floresta e voxel e a mudar o teste do `kits3d_copiar.py`; sem a troca em `itens.ts`, o item não aparece e a pergunta não se responde |
| D-I5 | instalar o Blender e o MCP for Blender | **sim**, a versão LTS do Blender e o MCP for Blender, com o socket só em `localhost` e o modo seguro ligado | sem eles, as etapas 4 a 7 dependem só do remesh do gerador e de uma ferramenta de linha de comando, sem o olho do produtor no meio; com eles, o risco é o socket sem autenticação aberto enquanto o Blender roda |
| D-I6 | o teto de gasto | **R$ 120** para os cinco itens (o Pro mais a folga do concept), com o saldo no corpo de cada PR | sem teto, as tentativas não têm fim; um teto curto demais para no meio de um item |

## 9. A medida dos kits (como refazer)

O script `docs/itens3d/medir_kits.mjs` lê a tabela `MODELOS`, abre cada `.gltf` de `public/kits3d/` e conta os triângulos pelos índices
de cada primitiva, os materiais, as texturas de cor e o tamanho de cada PNG pelo cabeçalho. A saída é `docs/itens3d/kits_cc0_medidas.json`
(refazer, da raiz: `node docs/itens3d/medir_kits.mjs web/app > docs/itens3d/kits_cc0_medidas.json`; só Node, sem dependência). Na
primeira etapa de item o mesmo cálculo entra no teste da G1 a G5. Os números da seção 4.2 são da `main` `389f3893`, 28 arquivos:

```
baixos (12): 155 285 288 326 379 494 615 642 755 880 1690 3216    -> mediana 554,5
altos  (16): 12 44 48 72 84 900 1368 1646 3182 3505 3648 3947 4066 4964 5648 6265 -> mediana 2414
```

## 10. Antes da bola: os termos da Meshy e a referência (2026-11-05, Gerente, Claude Code, Opus 5.5, worktree `v3-itens-3d-bola`)

**Os termos de uso da Meshy** (`meshy.ai/terms-of-use`, atualizados em 2026-09-19, lidos em 2026-11-05). Servem para a ilha, com dois cuidados:
- **De quem é a malha:** no plano pago, do cliente ("customers on a paid Meshy plan own their Customer Output", §3.2). No plano grátis, a
  Meshy é a dona e libera em CC BY 4.0 com crédito; por isso nada se gera no plano grátis para o jogo. Postar na comunidade da Meshy põe o
  item em CC0 (§3.3): não postar.
- **Uso no jogo:** os termos não falam de jogo nem de uso comercial; a posse no plano pago cobre publicar. A Meshy não garante que o item
  seja único (§7.2): o revisor confere se ele não copia um item conhecido.
- **Cuidado 1, a marca de IA:** é proibido tirar ou alterar "AI identifiers such as metadata or watermarks" (§2.4). O remesh e a exportação
  no Blender podem apagar os metadados do GLB; o pipeline copia o `asset` e os `extras` de origem do GLB da Meshy para o `.gltf` final, e
  o `License.txt` diz que o item foi gerado pela Meshy (G8 passa a conferir os dois).
- **Cuidado 2, o treino:** a Meshy pode usar as entradas e as saídas de clientes fora do Enterprise (o Pro incluído) para treinar (§2.9),
  salvo pedido de exclusão a support@meshy.ai. Recomendação: o Matheus pede a exclusão ao assinar (o concept e a referência da ilha vão
  como entrada). Custo de não pedir: o concept e a malha podem entrar no treino da Meshy; nada no jogo muda.
- Também vale: o cliente revisa a saída antes de usar (§2.4) e não usa as saídas para treinar um gerador concorrente (§2.6).

**A referência da bola de hoje** (a bola procedural, para o par lado a lado; seção 7). Roteiro: `web/app/e2e_capturas/itens_bola_referencia.spec.ts`
(com `DIGILAB_CAPTURAS_ITENS=1`); saves: `web/app/e2e_capturas/saves_bola.json`, de `gerar_saves_bola.mjs` (semente 4242, pet v17
Gomamon, a bola 2 células a leste do pet, 13:00 e 22:30, o relógio parado). As 12 imagens (tela inteira e recorte em volta da bola, 390 e
1280, claro, escuro e noite) ficam fora do git, em `D:\Trab\digilab\capturas_itens3d\bola\referencia\`, porque o pet é sprite do UP; os
sha256 e a M3 de cada uma estão em `docs/itens3d/bola/referencia.json`, e as M3 inteiras em `docs/itens3d/bola/*_m3.json`.

| tela | draw calls (claro / escuro / noite) |
|---|---|
| 1280 × 800 | 89 / 89 / 109 |
| 390 × 844 | 82 / 82 / 98 |

O G9 da bola gerada é ter o mesmo número ou menos em cada uma das seis. O `fps_media` dessas medidas (60) é do Chrome sem janela do
Playwright e não é o fps do jogo: a medida de fps continua com o Matheus (seção 7).

## 11. A bola na ilha (2026-11-06, Gerente, Claude Code, Opus 5.5, worktree `v3-itens-3d-bola`)

A primeira etapa (D-I1). Em ordem, com o que cada passo deixou em `docs/itens3d/bola/`:

| etapa | o que saiu | créditos (saldo) |
|---|---|---|
| 1 concept | quatro concepts pelo Image to Image (nano-banana-2) com dois recortes da ilha sem o pet; o Matheus escolheu o 2, gomos (`concept/`) | 24 (1 100 → 1 076) |
| 2 multivista | três vistas coerentes do concept 2 (`vistas/`) | 6 (→ 1 070) |
| 3 malha | Multi-Image to 3D com remesh para 500: 524 triângulos, um material, textura de 2048 px; **facetada, amassada, gomos borrados e sombra embutida** (`malha/`) | 30 (→ 1 040) |
| 4–6 conserto (decisão do Matheus: no Blender, sem gerar de novo) | uma esfera UV limpa de 440 triângulos recebe a cor da Meshy por bake; a cor é chapada em três tons (`conserto/`, `consertar_bola.py`, `achatar_cores.py`) | 0 |
| 7 exportação | `web/app/public/itens/bola/` (glTF separado, 1024 px, a marca de IA no `asset.extras`, o `License.txt`) | 0 |
| 8 render na ilha | seis capturas lado a lado com a bola de hoje, a M3 de cada uma | 0 |
| 9 revisão | o revisor novo (uma sessão que só viu o concept e as capturas): **aprovado com ressalva**, cores lavadas e o amarelo some à noite; a paleta foi saturada (rodada 2) e as capturas refeitas | 0 |

Gasto total: 60 créditos, ≈ R$ 6,50 (o Pro a R$ 0,108 o crédito), dentro do teto de R$ 120 (D-I6).

**Os gates** (o teste `web/app/test/ilha_itens3d.test.ts` confere G1 a G8):
- G1 440 triângulos (teto 554); G2 a caixa igual nos três eixos, normalizada para 0,72 célula (o diâmetro da bola de antes);
- G3 PNG de 1024 px; G4 um material com textura; G5 nenhum mapa extra;
- G6 o glTF-Validator 2.0.0-dev.3.10 com 0 erros e 0 avisos (`validacao.json`); G7 os arquivos do item somam cerca de 26 KB;
- G8 o `License.txt` e o `asset.extras` com a Meshy e as três tarefas;
- G9 os draw calls iguais aos da bola de antes nas seis cenas: 89, 89 e 109 em 1280; 82, 82 e 98 em 390 (`referencia.json`, `gerada.json`).

**A resposta à pergunta da seção 1, para a bola:** a malha do gerador **não** entrou com a qualidade dos kits; entrou depois do conserto no
Blender, em que só a cor do gerador sobreviveu (a forma é uma esfera do Blender, as cores são a paleta do concept). Com o conserto, o custo
de render é o mesmo da bola de antes. O risco da D-I1 se confirmou: a esfera é a forma mais fácil de fazer sem gerador, então a bola diz
pouco sobre os itens de forma livre (o saco, o kit médico, o cocô).

**O código da vista** (D-I4): `ITENS_MODELOS` em `modelos.ts`; em `itens.ts`, a bola procedural sai e o glTF entra pelo
`carregarVariante` dos kits, com o pivô no centro para o giro; o `vista.ts` carrega os itens junto dos kits (falha alto do mesmo jeito) e
marca `data-objetos` quando terminam; o crédito em Ajustes › Sobre. A bola nova vale em todos os mapas do habitat, porque os itens são
os mesmos em todos. O motor, o log e o save não mudam.

**Fora:** o fps de verdade (a M3 no Chrome do desktop, com o Matheus); a aprovação das capturas pelo Matheus.

## 12. O saco de pancada na ilha (2026-11-06, Gerente, Claude Code, Opus 5.5, worktree `v3-itens-3d-saco`)

O segundo item, de forma livre, escolhido pelo Matheus depois da bola. Em ordem, com o que cada passo deixou em `docs/itens3d/saco/`:

| etapa | o que saiu | créditos (saldo) |
|---|---|---|
| 1 concept | quatro concepts com dois recortes da ilha sem o pet (o saco procedural e os kits); o Matheus escolheu o 2, bambu (`concept/`) | 24 (1 040 → 1 016) |
| 2 multivista | três vistas do concept 2; duas quase iguais, todas fiéis ao concept (`vistas/`) | 6 (→ 1 010) |
| 3 malha | Multi-Image to 3D com remesh para 2 000: **2 082 triângulos, uma peça só, com a forma do concept** (bambu, amarras, corrente, saco de lona, pedra com musgo); textura de 2048 px com sombra embutida (`malha/`) | 30 (→ 980) |
| 4 corte | no Blender, por script (`consertar_saco.py`): a malha da Meshy fica e é cortada em duas peças pelo vão entre o poste e o saco | 0 |
| 5 cor | a textura chapada em sete cores do concept (`paleta.json`, `achatar_cores.py`), 1024 px; depois do revisor, a lona e a corda que caíam na pedra viram musgo, só nos triângulos de UV da pedra (`uv_base.py`, `pintar_base.py`) | 0 |
| 6 exportação | `web/app/public/itens/saco/` (glTF separado com os nós `suporte` e `saco`, a marca de IA, o `License.txt`) | 0 |
| 7 render na ilha | o saco parado e a M3 (claro e escuro), e uma rajada de capturas do treino, antes e depois (`e2e_capturas/itens_saco.spec.ts`) | 0 |
| 8 revisão | o revisor visual (um subagente Sonnet que só viu o concept, as prévias e as capturas): **aprovado com ressalva**; conferir o saco contra o poste no fim do balanço (conferido em quadros ampliados: não toca), as manchas marrons e rosadas na pedra (tiradas, etapa 5) e o saco um pouco pequeno perto do pet (levado ao Matheus) | 0 |

Gasto do saco: 60 créditos; com a bola, 120 créditos, ≈ R$ 13, dentro do teto de R$ 120 (D-I6).

**O corte.** As fatias da malha por altura (no glb da Meshy, z para cima, de −0,95 a 0,95) mostram: a pedra da base até z ≈ −0,76; o
poste em x de 0,14 a 0,26; o saco em x de −0,52 a −0,08 e z de −0,48 a 0,38; a corrente em x ≈ −0,3 até o braço (z ≈ 0,66). Há um vão
entre o poste e o saco em toda a altura do saco. O `saco` são as faces com o centro em x < 0,05 e −0,7 < z < 0,63 (1 031 triângulos); o
`suporte`, o resto (1 051). Um primeiro corte sem o limite de baixo levava um pedaço da pedra junto com o saco; as capturas mostraram, e o
limite entrou. A malha gira 180° para o poste ficar do lado −x, como o saco procedural.

**Os gates:** G1 2 082 triângulos (teto 2 414); G2 os nós sem transformação, mais alto que largo, com os dois nós; G3 PNG de 1024 px;
G4 um material com textura; G5 nenhum mapa extra, `doubleSided` falso (a malha é fechada); G6 o glTF-Validator com 0 erros e 0 avisos
(`validacao.json`); G7 cerca de 200 KB; G8 o `License.txt` e o `asset.extras`; G9 os draw calls caem de 86 para 80 com o saco na tela
(as oito peças do saco procedural viram duas), nas duas cenas (`D:\Trab\digilab\capturas_itens3d\saco\`, fora do git, com o pet). O
fps do Chrome sem janela (60 e 53,8/59,3) não é o do jogo.

**A animação do golpe** (pedido do Matheus, 2026-11-06), só vista, como o resto do `itens.ts`: o saco já balançava para longe de quem
bateu (`SACO_BALANCO`). Agora também gira um pouco na corrente (`SACO_GIRO`, o sentido pelo lado do braço de onde o pet bate) e amassa na
direção do golpe, achatando nela e alargando nas outras, máximo no instante do golpe e voltando como lona cheia (`SACO_AMASSO`). Como o
pet fica do lado oposto ao do poste, o balanço vai para o poste; o vão é curto, então o balanço para esse lado para em
`SACO_FOLGA_POSTE` (0,14 rad), antes de tocar o bambu. Com movimento reduzido, o saco fica parado. Os números são PROPOSTOS, SEM FONTE,
para ajustar jogando. O treino no `vista.ts` não muda: o saco fica pendurado no mesmo ponto do procedural (`SACO_PENDURADO`).

**A resposta à pergunta da seção 1, para o saco:** desta vez **sim**: a malha do gerador entrou na ilha com a forma do concept e abaixo do
teto, e o pipeline só cortou, girou e chapou a cor. O que o gerador não deu, e o Blender deu: as duas peças para a animação e a cor sem a
sombra embutida. Com o saco, o gerador responde melhor nos itens de forma livre do que na esfera.

**Fora:** o fps de verdade (a M3 no Chrome do desktop, com o Matheus); a aprovação das capturas pelo Matheus; a referência do treino teve
poucos quadros na rajada (o Chrome demorou mais nas capturas da referência), mas o balanço de antes é o mesmo código e está nos quadros.
