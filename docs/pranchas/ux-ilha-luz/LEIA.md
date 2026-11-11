# Prancha: a hierarquia de luz da ilha (2026-11-09)

Esta prancha cuida da regra 1 de "guiar o olhar sem texto" (a prancha do layout, `docs/pranchas/ux-ilha-layout/`). O pedido do Matheus, em
2026-11-08, foi: "regras de game design para instruir o player a observar o mundo [...] Tem que ser algo mais natural". A regra diz que a luz
dá a prioridade:
- os destinos com luz quente;
- os caminhos claros;
- a decoração mais escura e menos saturada.

A fonte é o Level Design Book, "Lighting", no levantamento `20 Temas/Ensinar a olhar.md` do Obsidian. O Matheus disse "Sim, a prancha" em
2026-11-09.

**Como foi feito:** as imagens saem do jogo de verdade, com um protótipo atrás de `?luz=a|b|c`. Sem o parâmetro, nenhum shader muda. Isso
vale também na main depois do merge, até a etapa de código.

## Como a luz funciona (o protótipo)

- **Nenhuma luz nova.** O mundo curvo já passa todo material da ilha pelo `curvar` (`web/app/src/telas/pet/ilha/cena.ts`). O protótipo
  acrescenta ali um termo no fragmento, pela posição no chão.
- **Os focos:** o lar (o ninho e o comedouro), a praça, o portão, a barraca e o cais, cada um com o seu raio, e os caminhos da planta A, como
  focos pequenos a cada 3 células (`luzConta.ts`, `listaDeFocos`).
- **Perto de um foco,** a cor fica inteira e puxa um pouco para a cor da luz do ninho (`LUZ_NINHO`). Nenhuma cor nova entra.
- **Longe dos focos,** a cor escurece e perde saturação.
- **O chão pesa 0,3.** Na primeira versão, a grama longe dos focos ficava cinza-barro e os focos viravam discos visíveis. Agora o chão, as
  flores e os tufos recebem 0,3 do efeito, e quem muda é o que fica de pé: as árvores, as pedras, os enfeites e a lata do Digital. A borda de
  cada foco esfuma de 20 % do raio até o raio.
- **Ficam de fora:** o pet (que não passa pelo `curvar`), as sombras, os halos, as partículas e os fios. Também fica de fora a noite, que já
  tem os lampiões e os halos.
- **Os números** estão em `LUZ_HIERARQUIA` (`constantes.ts`) e são PROPOSTO, SEM FONTE.

## As propostas

| | longe dos focos | perto dos focos | como fica |
|---|---|---|---|
| **A, forte** | escuro 0,78, dessatura 0,45 | quente 0,14 | as árvores do fundo ficam cinzentas e pesadas, e o portão salta. Lê como efeito. |
| **B, suave** | escuro 0,90, dessatura 0,25 | quente 0,08 | as árvores ficam um pouco mais quietas, e o portão, os postes e a barraca sobressaem sem parecer efeito. |
| **C, só quente** | nada muda | quente 0,12 | quase igual a hoje: os destinos ficam levemente mais quentes. |

## Os arquivos

Cada grade tem quatro quadros: em cima, hoje e A; embaixo, B e C. Todos estão na pele Vidro a 1920 × 950, com o mesmo save e o relógio
parado às 13:00.
- `cmp_ilha_9_longe.jpg`, `cmp_ilha_8_alto.jpg` e `cmp_ilha_2_praca.jpg`: o mapa Ilha (o padrão).
- `cmp_digital_9_longe.jpg` e `cmp_digital_8_alto.jpg`: o mapa Digital.
- `faixa_ilha.jpg` e `faixa_digital.jpg`: a faixa do fundo (as árvores e o portão) em tamanho real, de cima para baixo: hoje, A, B e C. Aqui
  a diferença aparece melhor.
- `celular_hoje_b.jpg`: o celular a 390 × 844, com hoje e B no Vidro (Ilha) e hoje e B no Militar (Digital).
- `fonte/capturar.spec.ts`: refaz as capturas. Copie o arquivo para `web/app/e2e_capturas/luz.spec.ts`, rode `npx vite build` e depois
  `CAP_ROTULO=b CAP_MAPA=ilha CAP_LUZ=b npx playwright test -c playwright.capturas.config.ts e2e_capturas/luz.spec.ts --project gpu`.
  Apague a cópia depois.

## As decisões (APROVADAS em 2026-11-09)

O Matheus respondeu "B com tudo" (2026-11-09): a B e as recomendações de LZ-2 a LZ-5, como estão abaixo. A etapa de código está na
seção 28 de `docs/TAREFA_V3_UX_TELA_PET.md`.


- **LZ-1, a proposta.** Recomendação: **B, suave**. O Matheus pediu algo natural, e B guia sem aparecer. A lê como filtro, e C quase não
  muda nada. Custo de errar: baixo, porque é só trocar três números em `LUZ_HIERARQUIA`.
- **LZ-2, quem acende.** Recomendação: o lar, a praça, o portão, a barraca e os caminhos, **sem o cais enquanto ele estiver trancado**. O cais
  é do multiplayer futuro (`LUGAR_ABERTO`), e acender um lugar que não abre ensina errado; a regra do sinal único (Norman) vale também para a
  luz. Na etapa de código, o cais trancado saiu dos focos. Custo de errar: baixo, porque o foco do cais liga quando ele abrir.
- **LZ-3, a noite.** Recomendação: **sem o efeito à noite.** A noite já tem a hierarquia dela (os lampiões e os halos dos enfeites e dos
  lugares). Custo de errar: baixo.
- **LZ-4, o chão.** Recomendação: **o chão com peso 0,3.** Com peso 1, a grama fica cinza e os focos viram manchas (a primeira versão). Custo
  de errar: médio, porque é o que separa "natural" de "efeito".
- **LZ-5, em quais mapas.** Recomendação: **em todos que passam pelo `curvar`** (Ilha, Digital e Voxel; os mapas de dev também). Custo de
  errar: baixo.

## Depois da aprovação (a etapa de código)

- Tirar o `?luz=` e ligar a proposta escolhida como padrão, com as decisões LZ-2 a LZ-5.
- Medir o custo no celular: hoje são até 48 focos num laço do fragmento, e talvez seja preciso juntar os focos dos caminhos.
- Recapturar com este script e rodar o e2e inteiro: com a luz ligada, as capturas de tela do e2e mudam, e o `--update-snapshots` só roda
  com o ok do Matheus.
