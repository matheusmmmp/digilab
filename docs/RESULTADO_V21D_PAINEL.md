# Resultado — o painel do E1 com a V21D (força do canal de forma)

Status: **EXECUTADO** (2026-09-30), uma run, pelo plano registrado antes (`docs/PLANO_ANALISE_V21D.md`, commits
`23ecedf` e `da9c1ee`). Nenhum número, chave, semente ou critério mudou depois da run. Nenhum desvio.

Todo número abaixo vem de `artifacts_linhagem/natureza_criacao_v21d/especie_fixa/analise_plano.json`
(`experiments/analisar_v21d.py`), salvo quando outro arquivo é citado.

## Resultado em três frases

1. **Gate: COMPRESSÃO NÃO VERIFICADA.** Nos pets do painel a V21D não comprimiu o canal de forma. O r² da forma
   final ficou em 0,929 → 0,939, Δ +0,010, IC95 [−0,042; +0,040]. **Pelo plano, o experimento não testa H, e nada
   se conclui sobre o dono.** O passo 2 (Δfrac_D) não se aplica.
2. **Por quê:** a V21D aproxima as formas entre si, mas **troca a ordem** das duas mais comuns em vez de encolher a
   distância entre elas.
   - A amplitude entre as formas adultas caiu de 0,521 para 0,387.
   - Só que 286 dos 600 pets vivos são espelho ou muralha. O espelho caiu de 0,406 para 0,301 e a muralha subiu de
     0,279 para 0,351: continuam separados, agora em ordem trocada.
   - Pesada pela frequência das formas, a variância entre formas não diminuiu.
3. **O que ficou de pé:** o "canal comprimido" da validação (7 formas em [0,40; 0,60]) é uma propriedade dos **bots
   com pesos iguais**. Na população que a vida produz, com as formas desiguais em número e os pets com caráter,
   treino e disciplina, ele não aparece.

## Conferências (seção 9 do plano): todas passaram

| conferência | resultado |
|---|---|
| as 640 vidas da V21D iguais, byte a byte, às do E1 arquivadas | 640 de 640 |
| `pets.json` igual ao do E1 | igual |
| `hash_parametros_educacao` igual ao do E1 | `6a9037ad…` nos dois |
| config igual ao E1 fora das quatro chaves (sementes, rótulo, partidas, bootstrap) | igual |
| mortes no subconjunto primário (atencioso e permissivo) | 0 |
| antes da run, o piloto V21C refeito com o código novo | `taxa_por_celula`, estimativas e `pets.json` iguais aos do E1 |
| `r2_por_categoria` (movida para o `metrics.py`) | `analisar_dono_ambiente.py` reproduz o artefato byte a byte (0,9585 e 0,9290) |

Run: vidas 985 s, painel 129 s (960 000 partidas: 600 pets vivos × 32 bots × 50), análise 10 s
(`…/natureza_criacao_v21d/especie_fixa/meta.json`).

## Estimandos primários (atencioso + permissivo, 320 células)

Os ICs são IC95 pigeonhole pareados, com 10 000 reamostras e semente 20260930.

| estimando | V21C | V21D | Δ (V21D − V21C) |
|---|---|---|---|
| **r²_forma** | 0,9290 [0,9008; 0,9499] | 0,9388 [0,8928; 0,9630] | **+0,0098 [−0,0417; +0,0395]** |
| **frac_D** | 0,000 [0,000; 0,391] | 0,000 [0,000; 0,534] | +0,000 [−0,146; +0,297] (não entra no gate) |
| frac_G | 0,045 [0,000; 0,461] | 0,014 [0,000; 0,371] | −0,031 [−0,144; +0,025] |
| frac_DR | 0,470 [0,019; 0,624] | 0,592 [0,022; 0,692] | +0,123 [−0,158; +0,285] |
| frac_e | 0,405 [0,116; 0,521] | 0,282 [0,073; 0,355] | −0,123 [−0,256; +0,025] |
| r² só nas 8 formas adultas | 0,908 [0,833; 0,945] | 0,920 [0,857; 0,956] | +0,012 [−0,062; +0,084] |
| atencioso − permissivo | +0,005 [−0,127; +0,142] | +0,042 [−0,111; +0,184] | +0,037 [+0,005; +0,073] |

- σ²_D sem truncar: −0,0031 com a V21C e −0,0028 com a V21D. Nas duas condições o dono não aparece como componente.
- O Δ atencioso − permissivo tem o IC fora de 0: +0,037 [+0,005; +0,073]. É **secundário, sem gate**, e chegou
  depois de um passo 1 que falhou; relatado, não interpretado como efeito do dono.

## Análise completa (4 donos, morto = 0; secundária)

| estimando | V21C | V21D | Δ |
|---|---|---|---|
| r² com morto (14 categorias) | 0,9585 | 0,9543 | −0,004 [−0,024; +0,013] |
| r² só vivos (13 categorias) | 0,9378 | 0,9261 | −0,012 [−0,068; +0,020] |
| r² só as 8 formas adultas | 0,9348 | 0,9149 | −0,020 [−0,093; +0,022] |
| frac_D | 0,050 [0,000; 0,324] | 0,000 [0,000; 0,315] | −0,050 [−0,095; +0,064] |
| frac_G | 0,049 [0,000; 0,101] | 0,009 [0,000; 0,053] | −0,040 [−0,080; 0,000] |
| frac_DR | 0,223 | 0,317 | +0,094 [−0,041; +0,149] |
| frac_e | 0,657 | 0,645 | −0,013 [−0,126; +0,116] |
| atencioso − aleatório | +0,123 [+0,016; +0,204] | +0,108 [−0,009; +0,193] | −0,015 [−0,039; +0,012] |

Com os 4 donos, o r² também não cai com IC fora de 0. As frações de dono e de genoma não sobem: a estimativa de cada
uma desce.

## Taxa média por forma final (os 640 pets)

| forma | n | V21C | V21D | Δ |
|---|---|---|---|---|
| furioso | 17 | 0,710 | 0,688 | −0,022 |
| duelista | 57 | 0,627 | 0,588 | −0,039 |
| emboscador | 94 | 0,567 | 0,514 | −0,053 |
| sentinela | 5 | 0,523 | 0,450 | −0,073 |
| predador | 2 | 0,500 | 0,531 | +0,032 |
| adolescente brigão | 72 | 0,468 | 0,412 | −0,056 |
| **espelho** | **158** | 0,406 | **0,301** | **−0,104** |
| vigia | 6 | 0,286 | 0,476 | +0,190 |
| **muralha** | **128** | 0,279 | **0,351** | +0,073 |
| bastião rachado | 15 | 0,213 | 0,268 | +0,055 |
| titã | 16 | 0,189 | 0,445 | +0,256 |
| adolescente guardião | 27 | 0,182 | 0,160 | −0,022 |
| adolescente colosso | 3 | 0,023 | 0,036 | +0,013 |
| morto | 40 | 0 | 0 | 0 |

**Comparação com a validação** (bots, pesos iguais, `artifacts_combate_v21c/validacao_v21d/criterios.json`,
painel B):
- os colossos sobem nos pets, como nos bots: titã 0,233 → 0,436 nos bots e 0,189 → 0,445 nos pets;
- o **espelho** cai muito mais nos pets (0,406 → 0,301) do que nos bots (0,614 → 0,434), e fica abaixo da faixa;
- os adolescentes não mudam de lista e perdem para o painel novo.

## Distribuição de formas (QD; seção 8, descritivo)

Por dono, 160 pets. A cobertura e o κ vêm só das formas, iguais nas duas condições (conferido).

| dono | cobertura (8 nichos) | κ de Fleiss da forma entre ambientes | concordância entre pares | QD-score V21C → V21D | ICC da taxa entre ambientes V21C / V21D |
|---|---|---|---|---|---|
| aleatório | 1,00 | −0,028 | 0,129 | 3,517 → 3,733 | −0,081 / −0,027 |
| atencioso | 0,75 | −0,058 | 0,121 | 2,961 → 3,139 | −0,182 / −0,249 |
| permissivo | 0,50 | **0,269** | 0,521 | 1,830 → 1,699 | 0,493 / 0,482 |
| relapso | 0,875 | −0,017 | 0,163 | 2,847 → 3,086 | 0,014 / −0,090 |

- **O mesmo genoma com o mesmo dono chega a formas diferentes em cada ambiente.** O κ fica perto de 0 (o acaso) em
  três donos; só o permissivo tem alguma concordância (0,27). A forma é decidida mais pelo ambiente que pelo dono ou
  pelo genoma. Isso repete, por outra medida, a leitura da análise dono × ambiente.
- Os ICs de κ, da concordância e da ICC (no artefato) têm o limite superior inflado pelo bootstrap pigeonhole: um
  ambiente sorteado duas vezes conta como dois avaliadores que concordam. Vale a estimativa pontual; os ICs não servem
  para essas três medidas.
- O QD-score sobe nos donos que cobrem mais nichos, porque os colossos (titã, vigia) sobem, e cai no permissivo, que
  vive no espelho.

## Leitura

- **Para a pergunta adotada** (que propriedade do mapa dá efeito ao dono): este teste não chegou a comprimir o canal
  nos pets, então **não informa** se comprimir daria peso ao dono. Não é o resultado "arquitetura" nem o "calibração".
- **O que ele mostra:** a força do canal de forma, medida nos pets, depende de **quantos pets caem em cada forma**, não
  só da faixa das formas. A distribuição que a vida produz (espelho 158, muralha 128; sentinela 5, vigia 6) decide.
  Um reequilíbrio que só olha os bots com pesos iguais pode reordenar as formas sem comprimir.
- **Limites:**
  - R = 4 ambientes: ICs largos;
  - espécie fixa (brasa);
  - a V21D só no painel, com a vida em V21C;
  - uma run, sem poder calculado.

## Decisões em aberto (para o Matheus)

1. Se a pergunta do mapa continua, um segundo nível de canal comprimido **nos pets** precisa de um critério de
   compressão ponderado pela distribuição de formas da vida, e não pela faixa dos bots. Isso é calibração nova, com
   plano próprio.
2. A alternativa é **aceitar que o canal de forma não se comprime por reequilíbrio de listas** e ir para a
   arquitetura: por exemplo, uma resposta do dono que não passe pela forma.
