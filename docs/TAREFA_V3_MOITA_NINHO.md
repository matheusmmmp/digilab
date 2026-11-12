# TAREFA V3 — MOITA_NINHO: o que tapa o pet fica transparente

**Status:** feita no branch `v3-moita-ninho` (2026-11-12), à espera do PR e do merge do Matheus.

## O pedido

O Matheus pediu para resolver "a questão da moita": o ovo do brasão choca no ninho da ilha grande, e a câmera de sempre olha por trás de
uma árvore grande e de uma moita, que tapam o ovo e o pet no meio da tela. Essas árvores são células fechadas do mapa do motor; tirá-las
mudaria o mundo e as vidas. O conserto é só na vista.

## O conserto

- `web/app/src/telas/pet/ilha/tapar.ts` (sem three): `quemTapa` decide, pela linha da câmera a três pontos de um cilindro curto do pet,
  quais objetos (cilindros de pé) a cruzam antes do pet; `opacidadeAgora` anda a opacidade.
- `web/app/src/telas/pet/ilha/transparente.ts`: `Esmaecer` troca a instância que tapa por um clone de uma instância, com o material
  próprio e transparente, que vai a 0,3 e volta a 1 (o `alphaTest` desce junto); com "reduzir movimento", na hora.
- `cena.ts` (`objetos`) junta as peças de cada árvore, pinheiro e arbusto; `vista.ts` chama o `Esmaecer` a cada quadro com o pet em foco.
- Os números em `TAPAR_PET` (`ilha/constantes.ts`), PROPOSTO, SEM FONTE. A leitura `__digilab.tapando()` diz quantos estão transparentes.
- O motor, o save e a `VERSAO_PET` não mudam.

## O resultado

- A árvore e a moita na frente do ninho ficam transparentes logo depois de chocar: `docs/capturas_moita_ninho/antes_1280x800.png` e
  `depois_1280x800.png`.
- Os testes: `test/ilha_tapar.test.ts` (8) e o e2e `e2e/moita_ninho.spec.ts` ("a árvore na frente do ninho fica transparente").
  `npm run tipos` limpo; Vitest 176 arquivos, 1 798 passaram e 3 pulados (o `hx_pele` falhou na primeira rodada pelos fins de linha
  CRLF que a edição deixou no `main.tsx`; voltaram a LF, e ele passa, 29 de 29); e2e inteiro 140 de 140.
- Os desvios D-MN-1 a D-MN-6 estão em `docs/registro/2026-11.md`.
