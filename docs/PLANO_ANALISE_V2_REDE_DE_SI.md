# Plano de análise — V2: a rede de si em observação (etapa 2 do ego)

Status (2026-10-08): **PROPOSTO**, registrado **antes de qualquer run**. É a etapa 4 de `docs/TAREFA_V2_REDE_DE_SI.md`. As decisões da
tarefa (RS-1 a RS-7) foram **DECIDIDAS pelo Matheus em 2026-10-08, todas pela recomendação**. As deste plano (PRS-1 a PRS-5,
seção 12) foram **DECIDIDAS em 2026-10-11, todas pela recomendação**.

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- A calibração não lê o primário, e a validação roda uma vez só. Nada se ajusta olhando a validação.
- Nenhuma alegação de novidade: modelos de previsão do próprio corpo e da própria ação já estão publicados (`docs/futuro/ego_existencia.md`,
  seção 3). Este plano só mede se a rede deste pet faz o que a tarefa pede.

## 1. A pergunta

**A rede de si aprende o próprio pet, só olhando?** Três partes:
- **O corpo:** a rede prevê as leituras dos receptores a n decisões melhor que as duas linhas de base obrigatórias (D-7): a
  **persistência** (o depois é como agora) e a **média histórica** (o depois é a média do que já viu).
- **A mudança:** quando o corpo muda no meio da vida, a rede volta a prever melhor que a mesma rede congelada no momento da mudança.
- **A autoria:** a estimativa da própria escolha em situação alterada é calibrada contra a sonda do cérebro, que o pet não vê.

**A predição** (sentido fixado agora): a rede bate a persistência a 4 decisões (1 h) nos dias 8 a 14.

**O que não se pergunta aqui:** se a rede ajuda o pet (a etapa 3 do ego), as perguntas (a etapa 4) e a fala.

## 2. O pet, os mundos e o dono

- **O cérebro:** o A, no ponto da K2 (`artifacts_v2_calibracao_conjunta/escolha.json`), na montagem completa. Não se calibra (M10).
- **O corpo:** o regime "corpo" da bancada (a química, os drives novos e os gestos; `docs/TAREFA_V2_CORPO_DRIVES.md`, etapa 8).
- **Os mundos** (RS-4):
  - **`bola`**, para a cabeça do corpo e a adaptação;
  - **`iguais_frutas` com o pedido do N7**, para a autoria. É onde a sonda "quem decidiu" do pedido existe. As frutas iguais tiram o efeito da
    fruta ruim da conta.
- **O dono:** o atencioso, com os gestos (`DonoComGestos`). Os outros donos ficam fora (PROPOSTO): a pergunta é sobre a rede, não sobre o dono.
- **A duração:** 14 dias, uma decisão a cada 15 ticks (96 por dia).
- **A rede:** a da tarefa, seção 2, na mesma vida. **Ela não muda a vida** (G-OBS): cada braço abaixo é uma vida só, com a rede observando.

## 3. Os braços

A rede é uma chave da bancada (`rede_de_si`), e não um braço: ela observa a vida de um braço sem mudá-la. Os braços são da bancada; os novos
estão marcados.

| braço | mundo | o que é | para quê |
|---|---|---|---|
| **P1-c** | `bola` | o P1 com o corpo (já existe) | **primário** (a cabeça do corpo) |
| P0-c | `bola` | o P0 com o corpo (já existe) | descritivo: a rede num pet que não aprende |
| **P1-c-lenta** (novo) | `bola` | o P1-c com a digestão lenta a partir do fim do dia 7 (RS-3) | G-ADAPTA |
| P1-c-tapa | `bola` | o P1-c com o tapa no lugar da bronca (já existe) | descritivo: a surpresa depois do tapa |
| **P1+ped-c** (novo) | `iguais_frutas` | o P1+ped com o corpo | a autoria (G-AUT-PED, G-AUT-NASC) |

**A digestão lenta do P1-c-lenta** é uma troca da `ConfigCorpo.taxa_digestao` num tick, gravada no registro como a troca do mutável:
- **antes do fim do dia 7:** C (a de hoje);
- **a partir dele:** a taxa lenta, PROPOSTA = C // 8 (a escolha fica no adendo 1, seção 6, pela regra "o receptor da fome muda"; nunca pelo
  primário).

A troca muda a vida (é uma mudança do mundo), igual com a rede ligada ou desligada.

**Por que não a troca de estágio:** hoje ela não muda o corpo (o estágio só é lido; seção 7 da tarefa). Uma rede que "se adapta" a ela não
teria o que adaptar.

## 4. As medidas

**A janela primária:** os dias 8 a 14 (os ticks [10080, 20160), `metrics.JANELA_8_14`). A rede aprende desde o tick 0. Os dias 1 a 7 são
descritivos.

**Os erros da cabeça do corpo.** Em cada decisão k da janela, para cada receptor r e horizonte n:

| previsor | previsão de `l_r(k + n)` | quem guarda |
|---|---|---|
| a rede | `p_r,n(k)`, a da tarefa, feita na decisão k | a rede, no estado dela |
| **persistência** | `l_r(k)` | a bancada |
| **média histórica** | `div_arred(Σ_{j ≤ k} l_r(j), k + 1)`: só o passado, em inteiros | a bancada |

O erro é `|previsão − l_r(k + n)|`, na escala S. Uma decisão sem k + n dentro da vida sai da conta.

**`MAE_X(n)`** é a média do erro absoluto do previsor X no horizonte n, sobre os receptores e as decisões da janela, por vida.
- **Os receptores:** todos os que o corpo expõe no regime "corpo" (`PercepcaoCorpo`), com o mesmo peso.
- **O que não entra:** o susto. Ele é zero quase sempre, e a persistência acerta por construção. Sai à parte.

**A primária (PRS-1):** `D_SI = MAE_pers(4) − MAE_rede(4)`, por unidade. Maior é melhor.

**Os secundários (dentro do Holm, seção 7):**
- **`D_MEDIA = MAE_media(4) − MAE_rede(4)`,** no P1-c.
- **`D_ADAPTA`,** no P1-c-lenta. É `MAE_cong(4) − MAE_rede(4)` só no receptor da fome, nos dias 11 a 14.
  - **`cong`:** a mesma rede com os pesos congelados no tick da troca. É a bancada que a refaz por replay, sem ser outra vida.
  - **O que mede:** se a rede que continua aprendendo prevê melhor o corpo novo que a rede que parou.
- **`BSS_PED`, a autoria do pedido,** no P1+ped-c, nas decisões com pedido vigente e `comer` entre os candidatos (`fome_moderada`,
  `fruta_no_cenario`).
  - **O evento:** "sem o pedido, a ação seria comer", lido da sonda N7 do motivo (`pedido`: a ação com o mesmo u e sem o termo).
  - **A previsão:** a probabilidade de `comer` que a rede dá com o pedido zerado.
  - **A medida:** o **Brier skill** contra a frequência do evento nas mesmas decisões da mesma vida: `BSS = 1 − Brier_rede / Brier_base`.
- **`BSS_NASC`, a autoria "ao nascer",** no P1+ped-c, em todas as decisões dos dias 8 a 14.
  - **O evento:** a ação da sonda do aprendido (`motivo["sonda"]`: a ação com o aprendido zerado e o mesmo u). Ela é o que o pet herdou,
    o pet "ao nascer".
  - **A previsão:** a distribuição da rede com a idade na primeira faixa.
  - **A medida:** o Brier de várias classes (a soma sobre as ações candidatas), em skill contra a distribuição das ações da sonda na mesma
    vida.

**Os descritivos (sem gate):**

| medida | definição |
|---|---|
| os outros horizontes | `D_SI` e `D_MEDIA` em n = 1 e n = 16 |
| por receptor | `MAE_rede − MAE_pers` de cada receptor, o susto incluído |
| a curva | `MAE_rede(4)` e `MAE_pers(4)` por dia, dos dias 1 a 14 |
| o oráculo | o mesmo LMS em inteiros, com os químicos do corpo como entrada (acesso privilegiado). Só a bancada o roda, e ele nunca existe no pet. É o teto de referência da margem (seção 6) |
| o P0-c | `D_SI` e `D_MEDIA` num pet que não aprende |
| a adaptação, a curva | o erro da fome por dia no P1-c-lenta, da rede e da congelada |
| a surpresa (E-11) | a surpresa da tarefa por hora, em torno da troca da digestão e de cada tapa (P1-c-tapa), contra as horas sem nada |
| os pesos | os pesos das duas cabeças no fim de cada dia, e quantos no teto |
| a autoria por zona | `BSS_PED` em `fome_moderada` e em `fruta_no_cenario`, e a frequência do evento |

## 5. A calibração (só a rede, sem o primário)

**O que se calibra:** só o `passo` do LMS da rede. O cérebro, o corpo e o mundo não se calibram aqui.

**A grade:** `passo` ∈ {S/64, S/16, S/4} (PROPOSTO).

**A regra:**
- **O que roda:** o P1-c, nas sementes de calibração (seção 8). A rede é uma chave que observa, então uma vida só serve à grade inteira (cada
  `passo` rejoga a mesma vida).
- **O que fica:** o `passo` com o menor `MAE_rede(1)` nos **dias 1 a 7**. É o erro da própria rede, num horizonte e numa janela fora do
  primário.
- **O que a calibração não lê:** a persistência, a média histórica e nenhum contraste.
- **O teto:** se a rede prende pesos no teto em mais da metade das vidas, o `passo` sai da grade. Se nenhum sobrar, fica o menor.
- **A taxa lenta da digestão** (seção 3) se escolhe nas mesmas sementes, pelo P1-c-lenta: a maior taxa da grade {C // 2, C // 4, C // 8}
  em que o receptor da fome, na média dos dias 8 a 10, difere do P1-c por mais de S/16 (PROPOSTO). É uma regra sobre o corpo, não sobre a
  rede.

## 6. O piloto, a margem e o N

**O piloto:** no `passo` escolhido, os cinco braços, nas mesmas 20 unidades da calibração. Serve só para a margem, o N e o custo; os números
dele não entram como evidência.

**A margem `Δ_SI`, na escala da medida** (a convenção de "metade" da regra 6.3 do experimento maior), PRS-4:

`Δ_SI = ½ × [MAE_pers(4) − MAE_oraculo(4)]`, no P1-c, nos dias 8 a 14.

É o ganho de uma rede que chegasse à metade do caminho entre não saber nada (a persistência) e saber o químico (o oráculo). **Se essa
distância no piloto for ≤ S/128** (PROPOSTO), a persistência já é quase o teto, e não há o que aprender a 4 decisões: a validação não roda,
e o plano volta ao Matheus.

**As margens dos secundários,** pela mesma regra:
- `Δ_MEDIA` = `Δ_SI`;
- `Δ_ADAPTA` = ½ × a distância entre a congelada e o oráculo na fome, nos dias 11 a 14;
- `Δ_BSS` = 0,1 (PROPOSTO, SEM FONTE).

**O N:** o menor K_u (unidades por base) de 4 a 10 com poder simulado ≥ 0,8 para detectar `Δ_SI` no primário.
- **O método:** um bootstrap das diferenças por unidade do piloto, deslocadas para `Δ_SI`, com 2.000 réplicas por K_u.
- **Os secundários:** o poder de cada um sai só como relato. Abaixo de 0,5, o gate é lido como subpotenciado.
- **Se nem K_u = 10 chega a 0,8,** a validação roda com 10 e o poder sai declarado.

**O adendo 1:** o `passo`, a taxa lenta, as margens, o K_u, o poder e o custo entram num commit antes da validação.

## 7. Gates e regra de decisão

**Os gates de mecanismo** (da tarefa) vêm antes de qualquer run e não são estatística:
- **G-OBS:** a vida com a rede é byte a byte a vida sem ela, em todo braço;
- **G1-REDE:** o estado da rede é refeito pelo replay;
- **G-RECEPTOR;**
- **G-INT;**
- **G-PESOS.**

Se um falha, nada roda.

**O bootstrap:** sobre as unidades, com 10.000 reamostragens, semente 4242 e IC95; o IC90 só na equivalência.

| gate | medida (por unidade) | regra | papel |
|---|---|---|---|
| **G-SI** | `D_SI` no P1-c | as categorias abaixo | **primário** |
| G-MEDIA | `D_MEDIA` no P1-c | limite inferior do IC95 > 0, Holm | secundário |
| G-ADAPTA | `D_ADAPTA` no P1-c-lenta | limite inferior do IC95 > 0, Holm | secundário |
| G-AUT-PED | `BSS_PED` no P1+ped-c | limite inferior do IC95 > 0, Holm | secundário |
| G-AUT-NASC | `BSS_NASC` no P1+ped-c | limite inferior do IC95 > 0, Holm | secundário |

**As categorias do G-SI** são exclusivas e lidas nesta ordem (a ordem do PR #196):
1. **a rede sabe de si:** o limite inferior do IC95 > 0. Se o limite superior do IC90 < `Δ_SI`, leva o rótulo **"abaixo de Δ"**;
2. **a rede prevê pior que copiar o presente:** o limite superior do IC95 < 0;
3. **equivalente à persistência:** o IC90 dentro de ±`Δ_SI`;
4. **inconclusivo:** o resto.

**O Holm** cobre {G-MEDIA, G-ADAPTA, G-AUT-PED, G-AUT-NASC}, com α = 0,05. O G-SI é único e não entra.

**A leitura:**
- **A rede sabe de si e passa o G-MEDIA:** a etapa 2 do ego está cumprida no corpo. Os descritivos por horizonte e por receptor dizem onde.
  Isso libera o desenho da etapa 3 (a rede na decisão), com plano próprio.
- **A rede sabe de si e não passa o G-MEDIA:** a rede bate o presente, mas não a média. Ela aprendeu o nível de cada receptor, e não a
  dinâmica. Registrado; a etapa 3 espera uma decisão.
- **Equivalente ou inconclusivo:** pelo D-7, "um automodelo que não bate a persistência não sabe de si". Os descritivos (o oráculo, os pesos
  no teto, a curva) dizem se faltou entrada, passo ou capacidade.
- **Pior que a persistência:** a rede tem um defeito. O prior é a persistência (RS-2), então ela desaprendeu.
- **Os secundários não mudam a categoria do primário:**
  - **G-ADAPTA** diz se a rede acompanha a mudança do corpo;
  - **G-AUT-PED e G-AUT-NASC** dizem se a autoria é calibrada.
  - Uma autoria sem skill, com o corpo bem previsto, é lida como "a rede sabe do corpo, não de si como quem decide".

## 8. Sementes

| uso | faixa | bases |
|---|---|---|
| calibração e piloto | **43101…43505** | 43101, 43202, 43303, 43404, 43505 (K_u = 4) |
| validação | **44101…44505** | 44101, 44202, 44303, 44404, 44505 (K_u do adendo) |

- **O prefixo de unidades:** `"rede_de_si"`.
- **Conferências em 2026-10-08,** no `origin/main` (`4bb2edf`):
  - as duas faixas estão fora de `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS`;
  - elas também ficam fora das faixas que os planos já propuseram e o D ainda não registrou: 35101…36505 (transferência) e 39101…42505
    (dois pets);
  - `git grep -w` das bases não acha uso fora dos gabaritos e dos artefatos.
- **O D registra** as faixas e o prefixo, com a fonte deste plano (tarefa, etapa 3).

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **A persistência é forte demais a 4 decisões:** os receptores andam devagar | a margem vem do oráculo (seção 6); se a distância é pequena, a validação não roda. Os horizontes 16 e 1 saem descritos |
| R-2 | **A média histórica injusta:** ela vê a vida até agora, e a rede também | as duas só usam o passado. A média é a mais simples que o D-7 pede |
| R-3 | **O G-OBS escondido:** o embrulho chama algo que mexe na rng ou no estado | o G-OBS compara o estado interno do cérebro e as rngs, byte a byte, em todo braço, antes de qualquer run |
| R-4 | **A rede aprende o dono, não o corpo:** o dono atencioso é regular | é parte do corpo como o pet o vive. O P0-c e o P1-c-tapa saem descritos. Outros donos ficam para depois |
| R-5 | **A autoria com poucos eventos:** o pedido só vale nos dias 1 a 10 | o `BSS_PED` usa todas as decisões com pedido vigente, e a contagem sai junto. Com menos de 20 eventos numa vida, ela sai da conta e é contada |
| R-6 | **A sonda "ao nascer" mede o herdado,** não o pet novo | é a definição deste plano: o pet ao nascer é o herdado (o prior do A), e a sonda o dá com o mesmo u |
| R-7 | **A digestão lenta muda mais que a fome:** o tédio e a energia mudam junto | o G-ADAPTA é só da fome. Os outros receptores saem descritos |
| R-8 | **O P1+ped-c não monta:** o corpo e o pedido ainda não andaram juntos na bancada | é um gate da etapa 3 da tarefa (o D). Se não monta, a autoria espera, e o primário roda sem ela |
| R-9 | **Os rótulos** ("sabe de si", "autoria") | só valem pelas medidas e regras desta seção. A leitura não usa consciência nem intenção |

## 10. A exposição para a etapa 4 (E-11)

Este plano não testa a pergunta interna. Ele só confere que a **surpresa existe e é legível**:
- a rede expõe, por receptor e horizonte, o erro recente e a surpresa (a tarefa, seção 2);
- a bancada a grava por decisão;
- os descritivos da seção 4 a mostram em torno da troca da digestão e dos tapas.

Nenhum limiar de "surpresa demais" é fixado aqui: é da etapa 4, com plano próprio.

## 11. Artefatos e reprodução

- **As pastas:**
  - `artifacts_v2_rede_de_si/calibracao/`, com `escolha.json` e o `piloto/`;
  - `artifacts_v2_rede_de_si/validacao/`.

  Cada uma traz `meta.json` (o sha256 de `rede_de_si.py`, `lobos.py`, `corpo.py`, `config.py` e `engine.py`) e os registros das vidas. O
  estado da rede sai do replay.
- **As configs:** `experiments/configs/v2_rede_de_si/{calibracao,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe.

## 12. Decisões do Matheus

**DECIDIDAS em 2026-10-11: PRS-1 a PRS-5, todas como recomendado.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PRS-1 | A medida primária | **`D_SI` a 4 decisões, a média sobre os receptores, nos dias 8 a 14** | n = 1: quase toda rede bate ou empata com a persistência, e o teste fica fraco. n = 16: o dono pesa mais que o corpo |
| PRS-2 | O braço primário | **o P1-c** (o pet que aprende, com o corpo inteiro) | o P0-c: mais fácil (a política não muda), mas não é o pet do ego |
| PRS-3 | Os secundários do Holm | **média histórica, adaptação, autoria do pedido e autoria ao nascer** | sem a média: a rede pode bater o presente só aprendendo o nível. Sem a autoria: metade da rede de si fica sem medida |
| PRS-4 | A margem | **metade da distância entre a persistência e o oráculo** | uma margem fixa sem dado pode ser larga ou estreita demais. Sem o oráculo, não há teto para a "metade" |
| PRS-5 | O dono | **só o atencioso, com os gestos** | os quatro donos: a vida custa 4 vezes, e a pergunta é sobre a rede |

## Adendo 1 — os números da calibração e do piloto (2026-10-14)

A calibração foi autorizada pelo Matheus em 2026-10-13 e rodou uma vez nas bases 43101…43505 (K_u = 4, 20 unidades), pelo commit `8294d74`
com a árvore limpa. Os números vêm de `artifacts_v2_rede_de_si/calibracao/` (`escolha.json`, `resultado.json`, `grade/grade.json`,
`piloto/medidas.json`, `meta.json`; as vidas ficam fora do git). O relatório é `docs/RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md`. Nada foi
ajustado olhando o piloto.

### A1.1 O `passo`: S/16 (64)

| `passo` | MAE_rede(1), dias 1 a 7 | vidas com peso no teto |
|---|---|---|
| S/64 (16) | 18,17 | 0 de 20 |
| **S/16 (64)** | **10,42** | 0 de 20 |
| S/4 (256) | 13,89 | 6 de 20 |

Nenhum ponto saiu pelo teto, e a regra fechou no 64.

### A1.2 A taxa lenta: C // 8 (56250), "não fechou"

O receptor da fome do P1-c nos dias 8 a 10 tem média 738,1. Pelo P1-c-lenta:

| taxa | média da fome | diferença do P1-c |
|---|---|---|
| C // 2 (225000) | 738,1 | 0,0 |
| C // 4 (112500) | 731,8 | 6,3 |
| C // 8 (56250) | 727,9 | 10,2 |

Nenhuma taxa passa o limiar S/16 (64). Pela reserva registrada antes da run, fica a menor taxa (C // 8, a que mais muda o corpo), com o
"não fechou".

### A1.3 A margem: negativa. A validação não roda

- **A distância** MAE_pers(4) − MAE_oráculo(4) no P1-c, dias 8 a 14, tem média **−24,5**, negativa nas 20 unidades: o oráculo prevê pior
  que a persistência. `Δ_SI` = −12,3.
- **A distância do G-ADAPTA** (congelada − oráculo, fome, dias 11 a 14, P1-c-lenta) tem média −18,5; `Δ_ADAPTA` = −9,3.
- **Pela seção 6** (distância ≤ S/128), **a validação não roda e o plano volta ao Matheus.** O N e o poder não foram calculados.
- **A causa não é a da leitura da seção 6** ("a persistência já é quase o teto"): o oráculo, com os químicos a mais na entrada e o mesmo
  `passo` da rede, deixa de ser um teto. É o risco descrito no fim de `docs/TAREFA_V2_REDE_DE_SI.md` antes da run.

### A1.4 O custo

- A grade custa 5,1 s de CPU por vida.
- O piloto custa por vida, em CPU, com o replay e a medição:

  | braço | CPU por vida |
  |---|---|
  | P0-c | 18,2 s |
  | P1-c | 19,7 s |
  | P1-c-lenta | 20,4 s |
  | P1-c-tapa | 21,3 s |
  | P1+ped-c | 33,4 s |

- A run inteira levou 7,6 min com 8 processos.
