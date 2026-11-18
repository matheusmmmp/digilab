# RESULTADO V3 — ELOGIO: a calibração e a validação (2026-11-18)

Worker: Claude Code, Opus 5.5, worktree `v3-elogio`. Plano: [PLANO_ANALISE_V3_ELOGIO.md](PLANO_ANALISE_V3_ELOGIO.md) (APROVADO em
2026-11-18, sha256 `0ad2f78b823b…` nas duas `meta.json`). Código: `main` em `424c269e` (#985). A validação rodou uma vez ("Sim, rode",
Matheus, 2026-11-18), na célula que a regra da calibração escolheu.

Os artefatos ficam em `resultados/v3_elogio/<fase>/`: `meta.json`, `resultado.json` e `vidas.jsonl` (as medidas por vida, não os logs; as
vidas são regeneráveis da config e do código). Todo número abaixo sai de um `resultado.json` ou de um `vidas.jsonl`.

## 1. A resposta curta

**O G-EL1 confirma:** E-imed − E-sorteado em M2 = **+0,073 [+0,042; +0,104]** (n 196), sem piora da M4. Mas **o E-imed não fica acima do
E0** (−0,003 [−0,027; +0,022]): o contraste vem do E-sorteado, que baixa a fração de X (−0,076 contra o E0). Com o g e o W da validação, o
carinho logo depois de X não leva o pet a comer mais X do que sem carinho nenhum. O que se mede é que o carinho fora de hora o afasta de X.

A P0 falha por um carinho com sinal zero (seção 4), e a P1 falha como a sonda previa (D-EL-20).

## 2. A calibração (sementes 25101 a 25200, 100 unidades, 2 500 vidas, 15 min com 4 processos)

E-imed − E-sorteado por célula. Na privação e na exaustão está o limite superior do IC95, que precisa ficar abaixo de +0,032.

| g | W | M2, média [IC95] | privação | exaustão | passa |
|---|---|---|---|---|---|
| 256 | 1 | +0,033 [−0,009; 0,076] | 0,021 | 0,004 | não |
| **256** | **2** | **+0,042 [+0,0008; 0,084]** | 0,013 | 0,002 | **sim, a escolhida** |
| 256 | 4 | +0,041 [−0,001; 0,085] | 0,025 | 0,005 | não |
| 512 | 1 | +0,048 [+0,003; 0,090] | 0,036 | 0,006 | não (M4) |
| 512 | 2 | +0,070 [+0,027; 0,119] | 0,040 | 0,008 | não (M4) |
| 512 | 4 | +0,048 [−0,004; 0,105] | 0,042 | 0,007 | não |
| 1024 | 1 | +0,054 [+0,007; 0,100] | 0,030 | 0,005 | sim |
| 1024 | 2 | +0,070 [+0,023; 0,118] | 0,052 | 0,009 | não (M4) |
| 1024 | 4 | +0,071 [+0,023; 0,118] | 0,037 | 0,005 | não (M4) |
| 2048 | 1 | +0,063 [+0,017; 0,107] | 0,032 | 0,007 | sim |
| 2048 | 2 | +0,088 [+0,046; 0,135] | 0,028 | 0,006 | sim |
| 2048 | 4 | +0,058 [+0,017; 0,104] | 0,028 | 0,006 | sim |

A regra (D-EL-21) pega o menor g e, nele, o menor W: **g = S/4 = 256, W = 2** (S = 1024), que passa por pouco. A P1 no E0 da calibração:
+0,033 [−0,030; +0,097] (n 99).

## 3. A validação (sementes 25301 a 25500, 200 unidades, 1 200 vidas, 6 min com 4 processos)

**O G-EL1, classe "confirma":**
- M2, E-imed − E-sorteado: +0,073 [+0,042; +0,104], n 196 (4 unidades sem consumo elegível);
- privação: −0,008 [−0,028; +0,011]; exaustão: −0,001 [−0,005; +0,003]. Os dois limites superiores estão abaixo de +0,032.

**Os secundários (descritivos):**

| contraste | M2, média [IC95] | n |
|---|---|---|
| E-imed − E0 | −0,003 [−0,027; +0,022] | 198 |
| E-atraso − E-imed | −0,009 [−0,029; +0,012] | 198 |
| E-incons − E-imed | −0,013 [−0,034; +0,008] | 198 |
| E-imed − E-sorteado em M3 (retenção) | +0,019 [−0,012; +0,049] | 199 |
| E-imed − E-sorteado, X = preferida | +0,074 [+0,019; +0,128] | 60 |
| E-imed − E-sorteado, X ≠ preferida | +0,073 [+0,039; +0,114] | 136 |

Os atrasos sorteados no E-atraso foram: 1 passo em 182 carinhos, 3 em 217 e 6 em 220.

**As médias de M2 por braço** (do `vidas.jsonl`, descritivas): E0 0,320, E-imed 0,318, E-atraso 0,309, E-incons 0,305, E-sorteado 0,243.
O E-sorteado contra o E0 dá −0,076 em média (n 196). Os quatro braços com carinho têm a mediana de 2 carinhos por vida.

## 4. As premissas

- **P0, falha.** O E0-off e o E0 dão o mesmo log em todas as 200 unidades. Mas 1 dos 2 342 carinhos dos braços com carinho teve sinal 0:
  na unidade 25425, no E-atraso, entre 10 carinhos. A premissa exige todos diferentes de 0. Pela regra do projeto, a falha fica registrada
  e não para o contraste. Ela é do E-atraso, e o G-EL1 compara o E-imed com o E-sorteado. A causa não foi investigada.
- **P1, falha, como previsto.** No E0, a fração da preferida na 2ª metade menos a da 1ª: +0,020 [−0,028; +0,068] (n 198). Sem ela, a
  leitura "o elogio acelera a natural" cai (D-EL-20).
- **P1b.** No fim da vida do E0, o humor do desfecho da classe preferida menos o da rejeitada: +134,8 [+129,5; +140,0] (n 200). O modular
  aprende o desfecho, mas a escolha não segue.

## 5. A leitura

1. **O gate, como escrito, passa.** O plano pôs o controle no E-sorteado, e contra ele o efeito é claro e não piora a M4. Isso vale para
   X = preferida e para X ≠ preferida.
2. **O "ensina X" não se sustenta contra o E0.** O E-imed fica igual ao E0, e o efeito inteiro está no E-sorteado, abaixo dos dois. O
   carinho sorteado cai na janela de decisões que não são comer X na maior parte das vezes (duas das três frutas não são X, e muitas decisões
   nem são comer). Uma hipótese, não medida: ele credita outras classes e as torna mais atraentes do que X. O carinho logo depois de X
   credita X, mas X já ganha o crédito do próprio desfecho, e a escolha pesa pouco o humor (a seção 2 do plano). Testar isso exigiria uma medida nova
   (o desfecho por classe no fim da 1ª metade, por braço), fora deste plano.
3. **O atraso e a inconsistência não mudam a M2 contra o E-imed** com g = 256 e W = 2. Isso combina com o E-imed não se separar do E0: não
   há efeito a degradar.
4. **A célula escolhida é a de menor g.** Na calibração, o efeito contra o E-sorteado cresce com o g (até +0,088 em 2S, W = 2). Com o g
   escolhido, a validação deu um efeito maior que o da calibração (+0,073 contra +0,042). Esta validação não diz se um g maior tiraria o
   E-imed de cima do E0; responder isso pede um plano novo.

## 6. O que não muda

Nada vai para a web (a etapa 6 esperava a validação). A chave do ELOGIO continua desligada por padrão, e o jogo não muda.

## 7. A decisão do Matheus (2026-11-18)

"Sim, registre assim": o ELOGIO fica registrado com esta leitura. O G-EL1 confirma contra o E-sorteado, e o carinho na hora não ensina X
além do E0. A etapa 6 (a web) não começa, e a chave continua desligada. Um g maior só volta com um plano novo.
