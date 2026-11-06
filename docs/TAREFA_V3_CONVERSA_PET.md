# TAREFA V3 — CONVERSA_PET (2026-11-06)

Coordenador: Gerente da frente CONVERSA_PET (Claude Code, Opus 5.5). Worker: um por missão (seção 3). Worktree e branch: `v3-conversa-<missao>`,
criados de `origin/main` (enquanto o PR #618 não entra na `main`, de `origin/v3-conversa-diagnostico`, para a tarefa existir no branch).
Status: ABERTA. **D1 a D7 DECIDIDAS pelo Matheus em 2026-11-06, todas pela recomendação** (seção 8). Ordem das missões: leva 1 = M1, M3, M5;
leva 2 = M2, M4 (depois de M1 e M3); leva 3 = M6 (depois do prompt, D4).

Categoria: arquitetura. Origem: Matheus, 2026-11-06: "o chat não está dialogando de uma maneira... não parece real, parece um diálogo de verdade."

## 1. Pergunta

Como fazer a conversa com o pet parecer um diálogo de verdade (voz estável da espécie e do estágio, memória da conversa, reação ao que o
dono diz, iniciativa, ritmo) sem afrouxar a trava de que a fala só alega causa, memória e estado que o registro sustenta?

Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é frente de produto (`docs/PRODUTO_VISAO.md`), sobre a fala por LLM, que fica
fora do pacote do pet (`servidor/CLAUDE.md`).

**O diagnóstico** está em [docs/research/DIAGNOSTICO_CONVERSA_PET.md](research/DIAGNOSTICO_CONVERSA_PET.md), com as trocas gravadas no jogo
de verdade (`artifacts_conversa_pet/diagnostico/`). As causas, por peso:

1. **C1, regressão da R2b (`665fe9e`):** a página parou de mandar `voz: true`; a conversa voltou ao prompt `livre-v2` e perdeu o comando
   pelo chat (que a tela ainda promete) e o estilo da espécie.
2. **C2, o prompt pede pouco:** "frases curtas" para todo estágio, as regras de verdade dominando, nenhum pedido de reagir, perguntar ou
   manter o assunto. O adulto respondeu entre 5 e 59 caracteres de 320.
3. **C3, a conversa não é fonte de fato:** o pet não pode citar o que o dono disse um turno antes (o nome).
4. **C4, histórico sem fronteira:** as 10 trocas atravessam sessões e estágios; o "nhã" do bebê contaminou a criança.
5. **C5, o pet de hoje não chega ao prompt:** a memória autobiográfica (C4), as lutas e o corpo do modular ficam fora.
6. **C6, formato e ritmo:** JSON forçado na fala, duas chamadas por turno, p50 5,0 s e picos de 42 s, sem streaming.

**As referências** (30 verificadas, mais 4 de produto) estão em [docs/research/REFERENCIAS_CONVERSA_PET.md](research/REFERENCIAS_CONVERSA_PET.md).
Ainda não entraram em `docs/referencias/referencias_verificadas.csv`; isso fica para o PR de literatura da frente, se o Matheus quiser.

## 2. Depende de

- As decisões D1 a D7 do Matheus (seção 8).
- Nada de outra frente: a fala livre, o servidor e a tela Conversar estão na `main`. A M6 (abaixo) usa a C4 e a PONTE_LUTA, já na `main`.

## 3. Mudança mínima

PROPOSTA, depende das decisões. Uma missão por PR, cada uma num worktree próprio, Sonnet para o código.

| missão | o que muda | arquivos | depende de |
|---|---|---|---|
| M1 | religar o comando e o estilo da espécie na conversa (sem a mentira nem a voz espontânea dos v7–v10) | `servidor/fala_livre.py`, `web/app/src/falaLivre.ts` | D1 |
| M2 | histórico com fronteira: só a sessão e o estágio atuais, trocas marcadas | `web/app/src/falaLivre.ts`, `digilab_fala_livre/prompt.py` | D2 |
| M3 | prompt `conversa-v1`: regras enxutas no fim, tamanho por estágio, exemplos de diálogo, reação e iniciativa | `digilab_fala_livre/prompt.py`, testes | D2 |
| M4 | a conversa como fonte de fato rotulada ("o dono me disse"), com teste de injeção | `digilab_fala_livre/fatos.py`, `verificador.py`, `falaLivre.ts` | D3 |
| M5 | cliente Claude para a fala livre, com chave e teto como na moldura; preços dos modelos 5.5 na tabela | `servidor/`, `tools/estimar_custo_llm.py` | D5 |
| M6 | a C4, as lutas e o corpo do modular nos fatos da conversa | `web/app/src/falaLivre.ts`, `digilab_fala_livre/fatos.py` | D4 |

O que NÃO muda: o registro do pet (a fala nunca entra nele, salvo o comando pelo catálogo fechado e o evento de sempre), `digilab/engine.py`,
`digilab/`, as versões de pet, os gabaritos e a paridade. Toda mecânica nova fica atrás de chave desligada; desligada, a conversa de hoje sai
igual. O `livre-v2` e o `livre-v8` continuam no pacote e reproduzem.

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_CONVERSA_PET.md`, commitado antes de qualquer rodada com número.
- Sementes reservadas: calibração e validação pedidas ao coordenador da V3 e postas em `experiments/bancada/faixas.py` antes da rodada.
- Métrica e gate (PROPOSTOS): a preferência do Matheus em pares cegos de conversas inteiras (ACUTE-Eval) e a taxa de falas com alegação sem
  fato (verificador + amostra marcada à mão), que não pode subir em relação ao `livre-v2`.
- GPU: sim, o `gemma2:9b` na RTX 2060, uma rodada por vez, no máximo 4 processos.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a missão toca a web).
- Registro: seção própria no fim de `docs/registro/2026-11.md` e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`. O resumo da etapa
  vai no corpo do PR e numa seção no fim deste arquivo.
- PR contra a `main` com resumo e números (cada um com o artefato), relato conferido por
  `python tools/verificar_relato.py --arquivo <corpo> --base origin/main`. Merge só pelo Matheus.

## 6. Fora desta tarefa

- A memória da conversa entre sessões ligada à memória autobiográfica (O11 do diagnóstico), salvo decisão contrária em D6.
- A voz com mentira e a fala espontânea com janela dos pets v7–v10 (saíram na R2b, decisão D-9).
- Modelo local maior que o `gemma2:9b` e ajuste fino (O10), até a comparação da D5.
- Qualquer efeito do texto do jogador no aprendizado do pet: só o catálogo fechado do comando.

## 7. Critérios de aceitação

- O diagnóstico e as referências existem e os links resolvem (este PR).
- Cada missão: os testes da missão passam; com a chave desligada, a conversa de hoje sai igual (teste); o relato passa no
  `verificar_relato.py`.
- M1: "vai comer" na tela Conversar de um pet v17 vira a ação pelo mesmo caminho do botão (teste e e2e).
- A avaliação: o plano está na `main` antes da primeira rodada; a validação roda uma vez.

## 8. Precisa do Matheus

**Decididas pelo Matheus em 2026-11-06 ("Aceito todas"), cada uma pela recomendação abaixo.** O detalhe e o custo de errar estão em
[docs/research/DIAGNOSTICO_CONVERSA_PET.md](research/DIAGNOSTICO_CONVERSA_PET.md), seção 8. Em uma linha cada:

- **D1** consertar o comando agora (M1): recomendo sim, primeiro. Custo de errar: religar algo que a R2b tirou de propósito.
- **D2** prompt `conversa-v1` com histórico de fronteira, exemplos e iniciativa (M2, M3): recomendo sim. Custo: fala mais longa, mais
  chance de alegar sem fato (o verificador fica).
- **D3** a conversa como fonte de fato rotulada (M4): recomendo sim, com limites. Custo: primeira porta do texto do jogador no prompt
  como fato; risco de injeção.
- **D4** a C4, as lutas e o corpo na fala (M6): recomendo sim, depois do prompt. Custo: paridade antes de saber se o prompt convence.
- **D5** comparar às cegas o `gemma2:9b`, o `claude-haiku-5-5` e o `claude-sonnet-5-5` (M5): recomendo sim, ~200 turnos, menos de
  US$ 1,50 estimados, teto separado. Custo: escolher a API traz rede e gasto ao jogo.
- **D6** memória da conversa entre sessões nesta frente: recomendo não agora. Custo: o pet não lembra de um dia para o outro.
- **D7** avaliação cega pareada pelo Matheus, juiz LLM só como triagem: recomendo sim. Custo: sem o Matheus, a frente otimiza o gosto do juiz.

## M1 — o comando e o estilo da espécie religados (2026-11-06, worker Claude Code Sonnet 5.5, branch `v3-conversa-m1-comando`)

- **Feito:** `livre-v9` em `digilab_fala_livre/prompt.py`; o campo `comando: true` do pedido da conversa em `servidor/fala_livre.py`; a
  conversa (e só ela) manda `comando: true` em `web/app/src/falaLivre.ts`. Mentira, história H/O/P/L, almanaque W e voz espontânea continuam fora.
- **Testes:** `tests/test_conversa_m1.py` (novo) e `tests/test_comando_chat.py` (ajustado: o `livre-v9` entra em `VERSOES_COMANDO`, 5 pastas de
  rodada); `web/app/test/comando_chat.test.ts` (pedido com `comando: true`); `web/app/e2e/conversa_comando.spec.ts` (novo: "vai comer" na Conversar
  grava o evento do botão).
- **Avaliação do comando (G4):** `artifacts_fala_livre/comando/rodada4_v9/` — falsos positivos 3,3 % (passa), imperativos 78,3 % (**falha**, limite 80 %).
  Detalhe e a decisão aberta em `docs/registro/2026-11.md` (D-M1-4).
## 9. Decisões depois das missões

- **DM1-1 (2026-11-06, Matheus): o `livre-v9` da M1 fica como está**, com o gate do comando falho por 1,7 ponto (imperativos 78,3 %
  contra o mínimo de 80 %; falsos positivos 3,3 %, passa; `artifacts_fala_livre/comando/rodada4_v9/`, PR #626). Recomendação do worker e
  do Gerente: os erros vão para o lado seguro (comando nulo). O reforço da regra do comando (v9b) fica para depois da M3, em faixa nova.
