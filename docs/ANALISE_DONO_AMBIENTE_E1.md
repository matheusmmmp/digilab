# Análise exploratória — de onde vem a interação dono × ambiente do E1

Status: **EXECUTADA, exploratória e pós hoc**, sem gate (2026-09-29). Lê só o que o E1 já gravou; nenhuma vida nem partida nova.

- **Script:** `experiments/analisar_dono_ambiente.py --entrada D:/Trab/digilab/arquivo/artifacts_linhagem_E1_vidas/natureza_criacao`
- **Artefato:** `artifacts_linhagem/dono_ambiente/resultado.json` (todo número abaixo vem dele)
- **Pergunta:** o E1 achou que a interação dono × ambiente explica 22% da variância da taxa no painel (`CLAUDE.md`, seção do E1). Isso é efeito do dono sobre o pet, ou é a soma de regras que o simulador já fixa?

## Resultado em três frases

1. **As mortes são todas "lesão sem tratar"** (40 na rodada de espécie fixa, 42 na balanceada) e vêm de duas regras que nós escrevemos: o **sorteio de lesão**, que depende da semente do ambiente, e a **regra do dono**. O aleatório nunca entra na rotina de responder a lesão (`donos_educacao.py`, `_resposta`), e o relapso só trata na visita.
2. **Sem as mortes, a interação continua, por outro caminho:** o ambiente muda a **forma** em que o pet termina, e **a forma final explica 96% da variância da taxa** (93% só entre os donos que nunca perdem pets).
3. **Dentro da mesma forma sobra 4%**, e aí a interação some (2%). O dono explica 22% desse resto: na mesma forma, o pet do atencioso vai um pouco melhor (+0,027 acima da média da forma), pelo ε da disciplina.

## Os números (rodada principal: espécie fixa, brasa)

**Exposição e morte.** A exposição a lesões é do ambiente (soma das lesões dos 4 donos):

| ambiente | 82001 | 82002 | 82003 | 82004 |
|---|---|---|---|---|
| lesões | 1 | 31 | 98 | 10 |

Pets com pelo menos uma lesão, e quantos deles morreram:

| dono | lesionados | mortos | regra de tratar lesão |
|---|---|---|---|
| aleatório | 42 | 32 | nenhuma (só se sortear o botão) |
| relapso | 21 | 8 | só na visita |
| atencioso | 26 | 0 | sempre que presente |
| permissivo | 6 | 0 | sempre que presente |

Nenhum pet morreu sem lesão.

**Decomposição da variância** (fração de cada componente; G genoma, D dono, R ambiente):

| resposta | G | D | R | D×R | resíduo |
|---|---|---|---|---|---|
| taxa no painel | 0,049 | 0,050 | 0,020 | **0,223** | 0,657 |
| morte (0/1) | 0,001 | 0,112 | 0,001 | 0,103 | 0,757 |
| lesões | 0,034 | 0,054 | **0,186** | 0,094 | 0,632 |
| saúde final | 0,012 | **0,630** | 0,000 | 0,021 | 0,308 |
| taxa, só atencioso e permissivo | 0,045 | 0,000 | 0,000 | **0,470** | 0,405 |
| taxa menos a média da forma | 0,077 | **0,219** | 0,021 | 0,024 | 0,650 |

**A forma decide a taxa.** Taxa média no painel por forma final (todos os donos):

| forma | pets | taxa |
|---|---|---|
| furioso | 17 | 0,710 |
| duelista | 57 | 0,627 |
| emboscador | 94 | 0,567 |
| adolescente brigão | 72 | 0,468 |
| espelho | 158 | 0,406 |
| muralha | 128 | 0,279 |
| titã | 16 | 0,189 |
| adolescente guardião | 27 | 0,182 |
| morto | 40 | 0,000 |

(Formas com menos de 15 pets estão no artefato.)

**Como o ambiente chega à forma** (descritivo): no ambiente 82003, 25 dos 40 pets do atencioso ficaram presos como **adolescente guardião**. Perderam o sparring contra o guardião da própria linha e não se qualificaram (só 15 de 40 viraram adultos, contra 31–40 nos outros ambientes). O permissivo termina quase sempre em espelho ou emboscador, dois arquétipos do meio para cima, e por isso é o dono que menos varia entre ambientes (desvio 0,023 contra 0,135 do atencioso).

**A rodada balanceada repete o quadro:** forma com R² 0,92, mortes todas por lesão sem tratar, e o dono explica 15% do resíduo dentro da forma. A diferença é que a espécie entra: o genoma explica 20% desse resíduo.

## O que isso muda

**Para a pesquisa.** Tudo o que medimos de efeito do dono (a confirmatória, a V3, a V3c e o E1) passa pelo mesmo gargalo:

    dono → (morte, por regra do dono) + (loteria de formas) + (ε da disciplina) → taxa no painel

- **O painel B mede quase só o arquétipo.** E os arquétipos são desiguais: de 0,71 (furioso) a 0,19 (titã). É o desequilíbrio que a bateria V21C aceitou como exceção (E1, E4).
- **A V4 que propus no direcionamento não deve rodar:** "o cuidado coerente reduz a variância entre ambientes" testaria duas regras que nós mesmos escrevemos (quem trata lesão, e a qualificação no sparring), e o resultado estaria decidido antes da run.
- **O que ainda seria informativo:**
  1. Medir o dono pela **distribuição de formas** que ele produz, e não pela taxa. A pesquisa V2.1 já mostrou que as formas diferem por dono.
  2. Ou **equilibrar os arquétipos antes**: enquanto a forma decidir 96% do resultado, qualquer efeito de dono, genoma ou ambiente passa pela loteria de formas.

**Para o jogo.** A sensação "meu pet é bom" depende quase só de qual forma ele virou. Duas consequências:
- **O equilíbrio entre arquétipos vira prioridade de desenho**, à frente de M2–M4. É o E1/E4 do combate, que ficaram como exceção aceita.
- **A qualificação pelo sparring pune linhas inteiras:** perder o sparring contra o espelho da própria linha prende o pet no adolescente, e isso depende do ambiente, não do dono.

## Limites

- Exploratória e pós hoc: olhamos esses dados sabendo o resultado do E1. Nada aqui é confirmatório.
- Só 4 ambientes. Os ICs do desvio entre ambientes são largos (no artefato).
- O R² da forma conta "morto" como forma (taxa 0). Sem as mortes (só atencioso e permissivo), ele é 0,93.
- O painel B usa a condição neutra: a saúde não entra na luta. Por isso a saúde final (explicada 63% pelo dono) quase não aparece na taxa.
