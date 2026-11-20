# Resultado — Etapa B: o canal contínuo do caráter até a luta

Status: **EXECUTADO** (2026-09-30), uma run por nível, pelo plano e pelo adendo B registrados antes
(`docs/PLANO_ANALISE_CANAL_DONO.md`; commits `c3ed8ca`, `3023a31` e `ffff038`).

- **Desvio, antes da run:** a dose alta passou de k = 9 para k = 8. Com k = 9, a renormalização dos stats não tinha
  solução para 3 dos 600 pets vivos. A regra da troca não olha resultado (`docs/REGISTRO_DESVIOS.md`).
- **Implementação trocada, antes da leitura:** o k saiu da `ConfigCatalogo` e do `catalogo.py`, que entram nos
  hashes gravados das validações, e foi para o catálogo do painel (`run_natureza_criacao.catalogo_do_painel`,
  commit `a3080f2`).
  - k = 8: os stats dos 600 pets vivos saem idênticos nas duas implementações, e a run vale como está;
  - k = 3: 108 pets diferiam no último bit, e a run foi refeita;
  - os números da análise ficaram iguais até a 4ª casa (`docs/REGISTRO_DESVIOS.md`).
- **Fonte dos números:** `artifacts_linhagem/natureza_criacao_canal/analise_plano.json` (`experiments/analisar_canal.py`).
  k = 1 é o E1; k = 3 e k = 8 estão em `…/natureza_criacao_canal/k3/` e `k8/`.

## Resultado em três frases

1. **Gate B: CANAL NÃO ABERTO**, por margem mínima. Com k = 8 o r² da forma sobre os vivos cai de 0,938 para 0,899:
   Δ −0,039, IC95 [−0,081; **+0,0008**]. O limite superior passa de zero por 0,0008. Pelo plano o canal não abriu, e o
   passo 2 (Δfrac_D) não se lê como gate.
2. **Mesmo descritivamente, o dono não ganha peso: perde.**
   - frac_D da taxa: 0,050 (k = 1) → 0,039 (k = 3) → **0,028 (k = 8)**; Δ(k = 8) −0,022 [−0,098; +0,046];
   - atencioso − aleatório quase não muda: +0,123 → +0,130, Δ +0,007 [−0,018; +0,029];
   - a transmissão (frac_D da taxa ÷ 0,208 do eixo resistente) cai de 0,24 para 0,14.
3. **A variância que o canal acrescenta não é do dono.**
   - O caráter está correlacionado com a forma (ele decide a linha e a forma). Amplificá-lo **afasta as formas** entre
     si: emboscador 0,567 → 0,606, espelho 0,406 → 0,380, titã 0,189 → 0,167.
   - O pouco que muda dentro da forma vai para dono × ambiente (frac_DR 0,223 → 0,250) e resíduo, não para o dono.
   - Com k = 8, 30% dos stats ficam presos no limite (5% com k = 1). O canal satura antes de levar sinal.

## Conferências: todas passaram

| conferência | k = 3 | k = 8 |
|---|---|---|
| 640 vidas iguais, byte a byte, às do E1 arquivadas | 640 | 640 |
| `pets.json` igual ao do E1 | igual | igual |
| `hash_parametros_educacao` igual | igual | igual |
| config igual ao E1 fora de `catalogo_painel` | igual | igual |

Testes do canal (`tests/test_canal_dono.py`): com o padrão 1,0 os stats não mudam; o peso maior afasta os stats do
neutro; o orçamento renormalizado não muda.

## Primário (4 donos, 640 células, morto = 0)

ICs: IC95 pigeonhole pareado, 10 000 reamostras, semente 20260930.

| estimando | k = 1 | k = 3 | k = 8 | Δ(k = 8 − k = 1) |
|---|---|---|---|---|
| **r² da forma, vivos (13)** | 0,938 | 0,930 | 0,899 | **−0,039 [−0,081; +0,001]** |
| **frac_D** | 0,050 | 0,039 | 0,028 | **−0,022 [−0,098; +0,046]** |
| frac_G | 0,049 | — | 0,047 | −0,002 [−0,020; +0,027] |
| frac_DR | 0,223 | 0,237 | 0,250 | +0,026 [−0,029; +0,053] |
| frac_e | 0,657 | 0,666 | 0,660 | +0,003 [−0,063; +0,031] |
| r² com morto (14) | 0,959 | — | 0,928 | −0,030 [−0,063; −0,004] |
| r² só as 8 formas adultas | 0,935 | — | 0,890 | −0,045 [−0,101; +0,006] |
| atencioso − aleatório | +0,123 | +0,124 | +0,130 | +0,007 [−0,018; +0,029] |

- Reamostrando só os genomas (secundário), o Δr²_vivos de k = 8 fica em [−0,057; −0,022]. A incerteza que deixa o
  gate de fora vem dos 4 ambientes.
- O r² com morto cai com IC fora de zero, mas o plano define a manipulação sobre os vivos.
- k = 3 move pouco tudo: Δr²_vivos −0,008 [−0,022; +0,006], Δfrac_D −0,012 [−0,045; +0,014].

## Secundário (atencioso + permissivo, sem mortes)

| estimando | k = 1 | k = 8 | Δ |
|---|---|---|---|
| r²_forma | 0,929 | 0,900 | −0,029 [−0,078; +0,027] |
| frac_D | 0,000 | 0,000 | 0,000 [−0,084; +0,076] |
| frac_DR | 0,470 | 0,411 | −0,059 [−0,103; +0,016] |
| atencioso − permissivo | +0,005 | +0,024 | +0,019 [−0,002; +0,040] |

## Taxa média por forma (os 640 pets)

| forma | n | k = 1 | k = 3 | k = 8 |
|---|---|---|---|---|
| furioso | 17 | 0,710 | 0,716 | 0,724 |
| duelista | 57 | 0,627 | 0,625 | 0,621 |
| emboscador | 94 | 0,567 | 0,589 | 0,606 |
| sentinela | 5 | 0,523 | 0,524 | 0,540 |
| adolescente brigão | 72 | 0,468 | 0,468 | 0,463 |
| espelho | 158 | 0,406 | 0,397 | 0,380 |
| muralha | 128 | 0,279 | 0,279 | 0,275 |
| bastião rachado | 15 | 0,213 | 0,199 | 0,178 |
| titã | 16 | 0,189 | 0,182 | 0,167 |
| adolescente guardião | 27 | 0,182 | 0,178 | 0,183 |

Stats presos em `stat_min`/`stat_max` (6 por pet vivo): k = 1 5,3%, k = 3 10,6%, k = 8 30,1%.

## Leitura

- **O caminho da arquitetura, como testado, fecha negativo.**
  - Etapa A: o dono deixa sinal no caráter, num eixo só, e não o da coerência.
  - Etapa B: levar o caráter direto à luta não dá peso ao dono. O caráter carrega mais forma e ambiente do que dono,
    e amplificá-lo amplifica sobretudo isso.
- **O gargalo não é só a forma: é o que o pet aprende.** No eixo que passou no gate A, o dono explica 20,8%, contra
  27,2% do ambiente e da interação dono × ambiente juntos (frac R 0,030 + frac DR 0,242). Nos outros três eixos, a
  interação sozinha fica entre 31% e 48% (`docs/RESULTADO_SINAL_DONO.md`). Um canal fiel ao caráter transmite essa
  proporção.
- **A comparação com o V21D:**
  - comprimir as formas (V21D) não comprimiu o canal;
  - abrir um canal contínuo (aqui) não deu peso ao dono;
  - nas duas, a fração do dono não subiu.
- **Limites:**
  - 4 ambientes;
  - espécie fixa;
  - o canal é um só (o peso do caráter nos stats) e satura com k alto;
  - os donos são quatro regras sintéticas.

## Decisões em aberto (para o Matheus)

- Se a pesquisa segue nessa pergunta, o próximo nível é **o aprendiz**, não o mapa até a luta. A política e o caráter
  precisam carregar mais dono do que ambiente: mais orçamento de interação, aprendizado mais forte, ou um sinal do dono
  que o ambiente não sorteie.
- A alternativa é encerrar a pergunta do mapa com este resultado e registrar a leitura consolidada: neste motor, o
  dono pesa pelo cuidado (mortes, saúde), não pelo ensino.
