# TAREFA V3 — CADEIA (2026-11-11)

Coordenador e worker: sessão do Gerente da V3 (Claude Code, Opus 5.5). Worktree e branch: `v3-cadeia-f1`. Status: ETAPA 1 ENTREGUE (PR
aberto).

Categoria: implementacao. Origem: Matheus, 2026-11-11.
- Ele colou um contexto sobre o Wobbledogs e pediu uma auditoria "para diagnosticarmos mais funcionalidades".
- A auditoria está no vault: `20 Temas/Auditoria — cadeia órgão-cérebro-mundo (Wobbledogs).md`.
- Ele aprovou as D1 a D8 pela recomendação: "Aprovo as oito".

## 1. Pergunta

A cadeia estado interno → percepção → decisão → ação → mundo → corpo → aprendizado acontece no jogo de hoje? Ela é provada por teste e
visível para o jogador? Nó do produto: o pet vivo (`docs/PRODUTO_VISAO.md`); a frente de pesquisa é o PET_VIVO.

## 2. Depende de

As D1 a D8 da auditoria, DECIDIDAS em 2026-11-11.

## 3. Mudança mínima (a Fase 1, D1: sem mecanismo novo no cérebro)

| Etapa | O que entra | PR da auditoria |
|---|---|---|
| **1 (este PR)** | o teste de cenário do lugar lembrado; a D2 no `CLAUDE.md`; a D4 e a D5 no registro | PR-A e PR-F |
| **2** | a vista não mastiga sem comida (D3); o lugar vazio visível com o rosto que o atlas já tem (D6) | PR-B e PR-D |
| **3** | o painel do DigiBrain mostra o resultado e o que mudou | PR-C |

Fica fora da Fase 1: o plano da Fase 2, que entra no PET_VIVO como etapa ou adendo (D7, PR-E). A normalização do sorteio (PR-G) segue na fila
da PV2-10.

Não mudam o motor, o log, o save, o replay nem a vida de nenhum pet.

## 4. Experimento e gate

Não há run. A etapa 1 é um teste determinístico (`web/app/test/cenario_lugar_lembrado.test.ts`).

## 5. Entrega

Um PR por etapa, com `npm run tipos`, `npx vitest run` e o relato no corpo.

## 6. Fora desta tarefa

- A Fase 2 (o A/B no Python, D7).
- A lesão como dor no corpo (D4: depois, com "dor × evasão").
- Mais classes de comida (D8: com a ARVORE_SACODE).

## 7. Critérios de aceitação (etapa 1)

1. O teste passa nas 5 sementes:
   - T1: o modular vai ao lugar lembrado, e a memória decide;
   - T2: o A não vai sem ver a comida;
   - T3: a visita vazia é gravada;
   - T4: o replay dá a mesma assinatura.
2. O `CLAUDE.md` diz que os ovos novos nascem com o modular.
3. O registro tem a D4, a D5 e os achados da etapa.

## 8. Precisa do Matheus

O merge.

## 9. Etapa 1 (2026-11-11): o cenário do lugar lembrado

O teste `test/cenario_lugar_lembrado.test.ts`:
- **O roteiro:** dois dias de ração no mesmo lugar e depois 50 h sem comida.
- **O modular:** nas 5 sementes (101 a 105), escolhe o lugar lembrado, a sonda `sem_memoria` mostra que a memória decidiu, chega perto e
  grava as visitas vazias.
- **O A:** com o mesmo log, só chama o dono.

Os achados estão no registro (D-CADEIA-2 e D-CADEIA-3):
- o lugar vazio não perde valor nesta janela;
- o A nem come a ração do treino em 4 das 5 sementes.

## 10. Etapa 2 (2026-11-11): a cena só mastiga com o que comer e o lugar vazio no rosto

Branch `v3-cadeia-f2`, sobre a etapa 1. Só vista.

- **D3:**
  - `comidaPerto` (`src/telas/pet/cenaAcao.ts`): a comida a até uma célula do pet;
  - `escolherComer`, `gestoAgora` e `desenharEfeitos` só desenham o comer com ela;
  - a ilha (`ilha/papel.ts`), o palco 2D (`PalcoPet.tsx`) e a reserva (`MundoReserva.tsx`) passam a informação.
- **D6:** `ultimoVazio` e o rosto Triste por 2 s quando a memória grava uma visita vazia nova (`src/telas/pet/momentos.ts`).
- **Testes:**
  - `test/ilha_comer_clipe.test.ts`: o comer sem nada perto e `comidaPerto`;
  - `test/momentos.test.ts`: o lugar vazio;
  - os e2e do comer e da cena seguem passando.
- **Desvios:** D-CADEIA-5 e 6.

## 11. Etapa 3 (2026-11-11): o painel mostra o resultado da decisão anterior

Branch `v3-cadeia-f3`, sobre a etapa 2. Só leitura.

- **`resultadoAnterior`** (`motor/digibrain/leitura.ts`): o `consequencia` do motivo anterior.
- **`textoResultado`** (`src/componentes/DigiBrainLab.tsx`): uma linha, por exemplo "Explorar o lugar lembrado (183, 249); chegou e não havia
  comida; a visita vazia ficou na memória".
- **Onde aparece:** sob o mapa do scan do modular e na seção "O que aconteceu antes" do mapa em texto.
- **Testes:**
  - `test/resultado_lab.test.ts` (3): o consumo e a visita vazia no cenário do lugar lembrado, o texto de cada caso e "só leitura";
  - o e2e do laboratório confere a seção.
- **Desvios:** D-CADEIA-7 a 9.

