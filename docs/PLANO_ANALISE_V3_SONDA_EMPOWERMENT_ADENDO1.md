# PLANO DE ANÁLISE V3 — SONDA_EMPOWERMENT, adendo 1: a opção (b) da D-F5-2 (2026-11-17, sessão da F5, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus (2026-11-17), com a (b2).** À pergunta "Aprova a D-F5-11 com as vidas novas no mundo com árvores, a
(b2)?", ele respondeu "Aprovo a (b2)". Este cabeçalho foi commitado antes do gabarito e do primeiro artefato (D-F5-8).

**De onde vem:** a primeira medida (`docs/RESULTADO_V3_SONDA_EMPOWERMENT.md`) deu "plano pelas entradas". O Matheus aceitou as duas
recomendações da seção 6 dela em 2026-11-17 ("Aprovo as duas"):
- **D-F5-2 (b):** rejogar uma run já feita, com mais classes ao alcance, depois de conferir o replay;
- **D-F5-10:** o "igual ao CONT" vazio não encerra a F5.

O plano original (`docs/PLANO_ANALISE_V3_SONDA_EMPOWERMENT.md`) continua valendo: as medidas, as conferências e a leitura. Este adendo
só troca as vidas, e diz por que a troca pedida não existe como foi pensada.

## 1. O que a opção (b) precisava

Uma run já feita, com o DigiBrain modular (a sonda lê o M-PLAST e o M-MEM) e com **mais classes ao alcance** do que a ração e a bola.

## 2. O que existe (conferido em 2026-11-17, sem rodar a sonda)

**FATO VERIFICADO:**
- **As runs gravadas com o modular usam o mesmo mundo.** As quatro que conferi gravam as vidas inteiras, e todas usam o `orq.CM`, que
  é o `CONFIG_MUNDO_MVP`:
  - a `artifacts_v3_longe_geometria/run/vidas.tar.gz`, com 12.800 vidas de 14 dias;
  - a `acoes_novas`;
  - a `individualidade`;
  - a `gosto_visual`.
- **Esse mundo não tem árvores** (`LAYOUT_MUNDO_MVP`, `arvores=()`, `digilab/config.py:1870`). Sem árvores, as classes que o pet pode
  comer são a ração, a ração podre e a bola, entre as seis de `CLASSES_DESFECHO` (`digilab/digibrain/plast.py:34`). As frutas `a`, `b`
  e `c` não aparecem.
- **Numa vida da LONGE_GEOMETRIA** (`PAD/atencioso_longe_10046074008288200363.jsonl`), o log só tem o tempo, as ações do dono e as
  rações postas (165).
- **O mundo com as três frutíferas existe**, o `CONFIG_MUNDO_ILHA` (`digilab/config.py:1873-1880`). Ele é do jogo (os pets v20) e só
  roda com o sacudir ligado. O único gabarito com árvores, o `tests/gabarito_arvore_sacode.py`, é do cérebro A e do instinto, que a
  sonda não lê.
- **O mapa tem 64 × 30 células de 16 subunidades**, ou seja, 1.024 × 480 subunidades. O alcance da memória é `d_max = 1024`
  (`digilab/config.py:2982`). Isso explica o `CONT` sem variação da primeira medida (o D-F5-A): de quase todo lugar, o pet alcança
  tudo o que lembra.

**NÃO CONFIRMADO:**
- se as outras runs da `individualidade` (I5, I7) usam outro mundo;
- se a ilha grande (128 × 60, com o `d_max` na proporção do mapa, IG-6) deixa o `CONT` variar.

## 3. O que isso muda

- **Rejogar a LONGE_GEOMETRIA não traz mais classes.** As vidas são mais longas e os lugares da ração mudam mais, mas o alcance continua
  sendo de ração e bola. A leitura esperada seria de novo "plano pelas entradas". Isto é HIPÓTESE, e não foi medido.
- **A M-S2 provavelmente não lê em nenhum mapa de hoje.** Com o `d_max` do tamanho do mapa, o `CONT` quase não varia entre os lugares de
  uma decisão. Pela D-F5-10, isso fica como "não leu", e a leitura passa a depender da M-S1.

## 4. As vidas propostas para a (b) (D-F5-11)

| opção | as vidas | o que dá | o que custa |
|---|---|---|---|
| **(b1)** | rejogar uma amostra da LONGE_GEOMETRIA: as 200 vidas do PAD no `longe`, depois de conferir o replay delas no código de hoje | segue a D-F5-2 (b) à letra | provavelmente a mesma resposta, porque as entradas são as mesmas |
| **(b2)** | vidas novas e curtas no `CONFIG_MUNDO_ILHA`, com o modular de hoje e o sacudir ligado, as sementes dos testes (101…505, como na opção (a)), os 2 donos da AN0 e 4 dias | as frutas `a`, `b` e `c` ao alcance: o `E` pode chegar a mais de 5 | sai da letra da D-F5-2 (é vida nova, não run feita). Precisa de um pequeno código em `experiments/` e de um gabarito próprio antes da medida. Leva menos de um minuto com 4 processos (0,4 s por vida na SE2) |
| **(b3)** | nenhuma: a F5 para com "plano pelas entradas", e a H-EMP-1 fica registrada esperando uma run de pesquisa num mundo com árvores | nada roda | a pergunta fica sem resposta até essa run existir |

**Recomendação: (b2).** É a única das três em que o `E` tem como variar além de ração e bola, e custa pouco. As sementes são as dos
testes, não uma faixa de pesquisa, como na opção (a). As medidas, as conferências e a leitura são as do plano, com a D-F5-10 para a M-S2.

**O custo de errar:**
- com a (b1), gasta-se uma etapa de replay para repetir as entradas estreitas;
- com a (b3), a F5 acaba sem ter visto o `E` num mundo em que ele pode variar;
- com a (b2), se o Matheus quisesse só vidas já feitas, a medida sai de um mundo que nenhuma run de pesquisa usou. Por isso o resultado
  dela não pode ser lido como o do pet da pesquisa.

## 5. Se a (b2) for aprovada, o que este adendo fixa antes

- **As vidas:** o `CONFIG_MUNDO_ILHA` com o sacudir ligado e o modular de hoje. Os donos são `atencioso` e `relapso`, os lugares
  `comedouro` e `longe_fixo`, as sementes 101 e 202, e são 4 dias: as oito células da AN0, no mundo com árvores.
- **O gabarito:** o sha256 do log de cada vida, gravado num commit próprio antes da medida. O G-S0 confere contra ele, e o G-S1 fica
  como está.
- **As medidas e a leitura:** as do plano, seções 2 e 4. A M-S2 que não ler fica como "não leu" (D-F5-10).
- **A conferência das entradas, antes da leitura:** as classes consumidas por vida. Se nenhuma fruta for comida, o relato diz isso, e a
  leitura continua sendo a do plano.
- **Os artefatos:** `artifacts_v3_f5_sonda/b2/`, com o mesmo formato. A medida roda uma vez.
- **As limitações:** as do plano, mais uma. É um mundo do jogo, sem run de pesquisa, então o resultado não fala do pet da pesquisa.

## 6. A decisão do Matheus

| id | pergunta | recomendação | custo de errar |
|---|---|---|---|
| **D-F5-11** | quais vidas para a (b): rejogar a LONGE_GEOMETRIA (b1), vidas curtas novas no mundo com árvores (b2), ou parar (b3)? | (b2) | seção 4 |

Decisão: a (b2), em 2026-11-17 ("Aprovo a (b2)").
