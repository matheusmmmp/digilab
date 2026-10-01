# Leitura consolidada — o que o dono faz ao pet neste motor (pergunta encerrada)

Status: **pergunta ENCERRADA** por decisão do Matheus (2026-10-01). Nenhuma run nova; este documento junta o que já foi
medido. Todo número aponta o artefato que o produz; confira lá, não aqui.

**A pergunta encerrada:** que propriedade do mapa até o desempenho é necessária para que o dono (ou o genoma) tenha
efeito mensurável no comportamento do pet? É a forma reescrita da hipótese central original ("treino por um dono
coerente produz um pet melhor que feedback aleatório com o mesmo volume de interação").

## 1. A leitura, em uma frase

**Neste motor, o dono pesa pelo cuidado, não pelo ensino.** O que separa os donos é quem deixa o pet morrer ou adoecer.
O feedback deixa pouca marca no que o pet aprende, essa marca depende mais do ambiente que do dono, e nenhum dos dois
canais testados até a luta (comprimir as formas, levar o caráter direto aos stats) deu peso ao dono.

## 2. A cadeia de evidência

| # | resultado | número | artefato |
|---|---|---|---|
| 1 | **A hipótese central foi refutada** (desenho B, condição neutra, 160 ovos) | atencioso − aleatório −0,034 [−0,072; +0,006] | `artifacts_confirmatoria/resultado.json` |
| 2 | Com educação, lesões e morte, o atencioso vence; metade vem das mortes do aleatório | +0,121 [+0,066; +0,175]; sem mortes (pós hoc) +0,058 | `artifacts_educacao/` (`PLANO_ANALISE_V3.md`) |
| 3 | Entre 24 personas de dono, só o **limiar de cuidado** tem efeito | +0,065 [+0,008; +0,115] por 1,0 | `artifacts_educacao_v3c/` |
| 4 | O genoma pesa pouco; dono × ambiente pesa mais que o dono | σ²_G IC95 [−0,0007; +0,0032] (4,9%); frac DR 0,223; frac D 0,050 | `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json` |
| 5 | As mortes vêm todas de lesão sem tratar, uma regra que nós escrevemos para cada dono; a saúde final é quase toda do dono | 40 de 40 mortes; frac D da saúde final 0,630 | `artifacts_linhagem/dono_ambiente/resultado.json` |
| 6 | **A forma final decide a taxa** no painel | r² 0,9585 (14 categorias); dentro da forma sobra pouco | idem → `forma_final` |
| 7 | O mesmo genoma com o mesmo dono chega a formas diferentes em cada ambiente | κ de Fleiss da forma −0,058 a −0,017 em 3 donos; permissivo 0,269 | `artifacts_linhagem/natureza_criacao_v21d/especie_fixa/analise_plano.json` |
| 8 | Reequilibrar as listas (V21D) **não comprime** o canal de forma nos pets: troca a ordem de espelho e muralha | Δr² +0,010 [−0,042; +0,040] | idem → `gate`; `docs/RESULTADO_V21D_PAINEL.md` |
| 9 | O dono deixa sinal no caráter aprendido, **num eixo só**, e não é o da coerência | resistente: σ²_D IC 98,75% [+0,0009; +0,0121], frac D 0,208; atencioso − aleatório +0,012 [−0,091; +0,115] | `artifacts_linhagem/sinal_dono/resultado.json`; `docs/RESULTADO_SINAL_DONO.md` |
| 10 | O ambiente move o que o pet aprende, antes de existir a forma | dono × ambiente 24% a 48% por eixo; κ da linha perto de 0 (salvo o permissivo, 0,41) | idem |
| 11 | Levar o caráter direto aos stats (k = 8) **não abre o canal**, e o dono perde peso | Δr² vivos −0,039 [−0,081; +0,0008]; frac D 0,050 → 0,028 | `artifacts_linhagem/natureza_criacao_canal/analise_plano.json`; `docs/RESULTADO_CANAL_DONO.md` |

Já sabíamos antes, e a cadeia confirma: o aprendizado mexe pouco no comportamento. A JSD entre braços ficou em 0,0204
bit, contra o limiar de 0,02 (`artifacts/divergence.json`).

## 3. Como ler

- **O que diferencia os donos é o cuidado.** As mortes (2, 5), a saúde (5) e o limiar de cuidado (3) carregam o
  efeito. Os três vêm de regras dos donos sintéticos, então o "efeito do cuidado" mede essas regras. É um resultado
  sobre o desenho, não uma descoberta sobre donos.
- **O ensino não chega à luta** por nenhum dos caminhos testados:
  - pela forma, o ambiente decide (6, 7) e reequilibrar as formas não ajudou (8);
  - por fora da forma, o sinal no aprendiz é fraco e não é o da coerência (9, 10), e um canal direto não o transmitiu
    (11).
- **O gargalo é o aprendiz, antes do combate.** O feedback do dono move pouco a política, e o pouco que move o
  ambiente também move. Mexer no mapa até a luta não resolve isso.

## 4. O que esta leitura não diz

- Não diz nada sobre jogadores humanos: só donos sintéticos, quatro regras escritas por nós.
- Não generaliza para fora deste motor:
  - bandit Thompson linear;
  - 14 dias;
  - orçamento fixo de interações;
  - 4 ambientes;
  - espécie fixa na rodada principal.
- Não diz que o ensino é impossível. Diz que, **com este aprendiz**, ele não aparece. Um aprendizado mais forte, ou um
  sinal do dono que o ambiente não sorteie, poderia mudar isso. Seria uma pergunta nova, com plano próprio.

## 5. O que fica fechado

- As perguntas "o dono coerente produz pet melhor" e "que mapa dá efeito ao dono" estão encerradas neste motor.
  - Não rodar de novo variações de calibração das formas ou de peso do caráter atrás de efeito do dono.
  - Não rodar a "V4" (cuidado reduz a variância entre ambientes): ela testaria regras nossas
    (`docs/ANALISE_DONO_AMBIENTE_E1.md`).
- O código das runs fica, com as chaves desligadas por padrão:
  - `ConfigCombateV21D` no Python;
  - `catalogo_painel` só por config;
  - `experiments/sinal_dono.py`, `analisar_v21d.py` e `analisar_canal.py`.
- Nada disso muda a pesquisa antiga nem o jogo.

## 6. Para o jogo

- **A sensação "meu pet é bom" depende quase só da forma**, e a forma depende muito de onde o pet vive. Se o jogo
  quiser que o jogador sinta autoria, o desenho tem de tornar visível e controlável o que hoje é sorteado pelo
  ambiente (a linha, a forma).
- **O cuidado já é o que separa os donos.** Lesão, saúde e morte são a alavanca legível que o jogo tem.
- O vínculo segue com o defeito conhecido: o aleatório termina com vínculo maior que o atencioso (−0,176 em
  atencioso − aleatório, `artifacts_linhagem/sinal_dono/resultado.json`).

## 7. Reabrir

Só com uma **pergunta nova sobre o aprendiz**, em plano registrado antes da run: por exemplo, um aprendizado em que o
dono responda por uma fração da política maior que a do ambiente. Não reabrir mexendo no mapa até a luta.
