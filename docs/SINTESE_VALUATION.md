# SÍNTESE — VALUATION (2026-11-17, Claude Code, Opus 5.5)

**A frente está encerrada com o diagnóstico, sem conserto.** O Matheus escolheu, no CHECKPOINT V3, em 2026-11-17: "Encerrar, ir à V5"
(D-VAL-23). A tarefa é a [TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md).

## 1. A pergunta

Por que o DigiBrain modular (o REL da C4) fecha menos episódios de fome que a baseline trivial da A1 no `longe_fixo`? A A1 (PR #943) mediu
REL − TRIV = −0,083 [−0,128; −0,038] na taxa por episódio. Qual elo, do drive à escolha, falha?

## 2. A resposta, em três frases

1. **O elo que falha é o reflexo do sono, não o valor da comida.** Desligado, o reflexo fecha +0,129 a mais de episódios, 1,55 vez o gap da
   A1. As outras cinco hipóteses saem refutadas: B (exploração), E (o viés do comer), F (V e E no z), C (a memória) e G (o sorteio).
2. **Comer e descansar competem no mesmo intervalo.** No REL, 63 % das decisões com a energia abaixo de S/4 acontecem com a fome urgente.
   Tirar o reflexo nessas horas fecha mais episódios, mas deixa o pet exausto.
3. **O conserto testado não passa.** A guarda do reflexo pela fome urgente fecha +0,106 a mais, mas sobe a exaustão em +0,195 (de 0,23 para
   0,42). A regra escrita antes reprova pela G2, e a fase parou.

## 3. As fases

| fase | o que entregou | PR | leitura |
|---|---|---|---|
| V0 | o [MAPA_VALUATION.md](MAPA_VALUATION.md): o fluxo de uma decisão, do M-SENS ao M-ARB, no Python e no TS | #945 | o REL come mais ração (2,96 por dia contra 1,49); o que falha é fechar o episódio dentro da janela (39 % vencem, contra 9 %) |
| V1 | o [PLANO_ANALISE_V3_VALUATION.md](PLANO_ANALISE_V3_VALUATION.md), com o adendo 1 (o braço A fora) | #946 | aprovado |
| V2 | a ablação, 5 600 vidas na 99xxx, uma vez: [RESULTADO_V3_VALUATION.md](RESULTADO_V3_VALUATION.md) | #949 | **só a R confirmada** (+0,129 [+0,117; +0,141]), marcada como "piora o bem-estar" (privação +0,084, exaustão +0,276) |
| V3 | o [PLANO_ANALISE_V3_VALUATION_CONSERTO.md](PLANO_ANALISE_V3_VALUATION_CONSERTO.md) e o conserto, 4 800 vidas na 73xxx, uma vez: [RESULTADO_V3_VALUATION_CONSERTO.md](RESULTADO_V3_VALUATION_CONSERTO.md) | #969 | **falha** pela G2 (a exaustão +0,195 no `longe_fixo`, +0,174 nas 12 células); a P, a G1 e a G3 passam |
| V4 | não rodou: o conserto não passou da V3 | — | — |
| V5 | esta síntese | este PR | — |

## 4. O que fica

- **A causa, localizada e medida:** o reflexo do sono (`Arbitragem.reflexo`, energia abaixo de `lambda_sono` = S/4) troca o `comer` por
  `dormir` dentro do episódio. São 13,2 intenções de comer trocadas por vida no `longe_fixo`.
- **O achado do regime:** a energia baixa e a fome urgente andam juntas em 63 % das decisões. Nesse regime, o pet não tem como comer e
  descansar ao mesmo tempo. Qualquer conserto no reflexo troca episódios fechados por exaustão.
- **O que não é a causa:** o valor da comida (E e F), a exploração (B), a memória do lugar (C: ela ajuda, −0,058 sem ela) e o sorteio do
  M-ARB (G: ele protege, −0,290 sem ele).
- **No código:**
  - as chaves de ablação da V2 (`ConfigAblacaoValuation`) e a do conserto (`ConfigConsertoValuation.guarda_fome_reflexo`) ficam
    desligadas, só de pesquisa;
  - desligadas, as vidas de hoje saem byte a byte (os gabaritos `valuation_de_hoje.json` e `valuation_conserto_de_hoje.json`);
  - nenhum pet, save ou arquivo do `web/app` mudou.
- **Os artefatos:** `artifacts_v3_valuation/ablacao/` e `artifacts_v3_valuation/conserto/`, cada um com o `meta.json` e os sha256.
- **As faixas queimadas pela frente:** a 99101…99505 (a V2) e a 73101…73505 (a V3).

## 5. O que a frente não demonstra

- nada contra a TRIV depois do conserto, porque a V4 não rodou;
- nada sobre o jogo web, porque as runs são do Python;
- nada sobre outro limiar além do `lambda_sono` e do `urgencia_lambda` de hoje;
- nada com o sono que segura ligado;
- nada fora dos 14 dias e do mundo do MVP;
- nada sobre uma guarda mais estreita, como a fome urgente **com** a comida à vista. Ela ficou como a opção (b) do CHECKPOINT V3 e não
  foi escolhida.

## 6. Em aberto, para o Matheus

- **A chave `guarda_fome_reflexo` no código:** ela pode ficar como registro do teste, desligada, ou sair num PR de limpeza. Fica como
  está até a decisão.
- **Os merges dos PRs empilhados** (#945, #946, #949, #969 e o desta V5) são do Matheus, na ordem.
- **Uma frente nova sobre o regime de energia e fome** só com pergunta nova. Esta frente não propõe nenhuma.

## 7. A linha do PAINEL (proposta ao coordenador)

> **VALUATION** · por que o modular fecha menos episódios de fome que a TRIV no `longe_fixo` · **encerrada com o diagnóstico**
> (2026-11-17): a causa é o reflexo do sono (a R, +0,129, a única confirmada na ablação); o conserto pela fome urgente fecha +0,106, mas
> reprova pela exaustão (+0,195), e a V4 não rodou · `docs/SINTESE_VALUATION.md`
