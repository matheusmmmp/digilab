# Vínculo: por que premia o dono aleatório, e o que o corrigiria (V2, fase 0)

Status: **PROPOSTO** (2026-10-01). Tarefa `docs/TAREFA_V2_F0_VINCULO.md` (fase 0, item 3 do `docs/PLANO_V2_PESQUISA.md`).
**Nenhum código do motor muda nesta tarefa**: é diagnóstico e proposta. Todo número vem de um artefato em disco, citado na
tabela ou na frase; a conta nova está em `artifacts_v2_vinculo/resultado.json` (`python experiments/analisar_vinculo.py`; uma
linha por vida em `por_pet.json`), sobre vidas já gravadas, sem semente nova.

## Resumo em três frases

1. **O vínculo premia o dono aleatório porque dois dos três componentes só geram amostra quando o pet está em falta.** O
   pedido (atendimento) só abre com fome ou higiene abaixo de 0,5 e a vontade (desejo) só é atendida por quem age sem olhar a
   necessidade; o dono que evita a falta nunca é medido (0,5 pedidos por vida no atencioso contra 540 no aleatório, nas 40 vidas
   da personalidade), e o aleatório recebe centenas de amostras acima de 0,5.
2. **O único componente que mede o dono, a coerência, mede sinal constante por ação e pune quem muda o sinal com o contexto**,
   que é o que o dono coerente faz (elogia brincar descansado, repreende brincar cansado): a amostra média dele é 0,62, a do
   incoerente 0,51. Agrupando por (ação, situação do pet), a do atencioso sobe para 0,74 e a do incoerente fica em 0,50.
3. **Recomendação:** trocar o vínculo por **previsibilidade**: só a coerência, por ação **e situação do pet**; atendimento e
   desejo saem. Recalculada sobre as vidas gravadas, inverte o sinal nos dois conjuntos: atencioso − aleatório vai de −0,069 para
   **+0,223** nas 40 vidas da personalidade e de −0,176 para **+0,209** nas 640 do E1. Nenhum termo de cuidado entra.

## 1. Como o vínculo é calculado hoje

### 1.1 Fórmula

`digilab/vinculo.py` (espelho: `web/app/motor/vinculo.ts`). Valor `v` em [0, 1], inicial 0,5, média móvel a cada amostra:

    v ← v + α · peso_c · (amostra − v),  α = 0,1   (ConfigVinculo / CVI)

Uma amostra puxa `v` 10% (peso 1) ou 5% (peso 0,5) do caminho até ela. O que decide o vínculo final é **quantas amostras cada
componente dá e com que valor médio**; a ordem importa pouco além das últimas dezenas.

### 1.2 Os três componentes

| componente | peso | quando gera amostra | amostra | janela |
|---|---|---|---|---|
| **atendimento** | 1,0 | o pet decide `chamar_atencao` com `min(fome, higiene) < 0,5` (`ConfigMemoriaEspacos.limiar_necessidade_pedido`): abre um pedido. O **primeiro cuidado** do dono (alimentar, limpar, brincar, acariciar, petisco, banheiro, tratar lesão) fecha **todos** os pedidos abertos, um por um | `1 − latência/240` por pedido fechado; **0** por pedido que passa de 240 ticks sem cuidado | 240 ticks (4 h) |
| **coerência** | 1,0 | a cada elogiar/repreender, se há feedback anterior sobre a **mesma ação do pet** nas últimas 24 h (o feedback entra no histórico depois) | fração desses feedbacks anteriores com o **mesmo sinal** | 1440 ticks |
| **desejo** | 0,5 | o pet passa a ter vontade de comer / brincar / chamar atenção (só quando o desejo muda): abre uma vontade. A ação do dono que a atende (alimentar / brincar / acariciar) em até 60 ticks fecha | **1** por vontade fechada; **0** por vontade que expira | 60 ticks |

Fora da média móvel, no mesmo valor: **ajustes diretos** (forçar treino com fadiga alta −0,05, `ConfigTreino.vinculo_forcar`;
bronca num chamado real −0,05, `ConfigEducacao.vinculo_bronca_sem_motivo`, pets v4+), a **pausa de treino** (amostra 1 com peso 1
quando a pausa acaba sem treino, 0 quando o dono treina por cima) e o **teto 0,6** da forma sombria (`ConfigSombrio.teto_vinculo`).

### 1.3 Onde o valor é usado

- **Obediência** (`obediencia.py`, `termos_obediencia`; web `termosObediencia`): `p = logística(1 + 2·vínculo − teimosia − 2·conflito)`.
  Vínculo 0,5 contra 0,6 muda `p` em cerca de 0,02; o que decide a obediência é o conflito (CLAUDE.md, seção da personalidade).
- **Mega** (só web, pets v5+): Ultimate → Mega pede vínculo ≥ 0,4 na hora da evolução (`CMG.vinculo`, `Motor.requisitosMega`).
- **Fala**: fator `vinculo_baixo` ("não confio") no motivo da recusa. O Lago (arena "do vínculo") usa a palavra, não o valor.
- **Pesquisa**: só descritivo (portador "imposto" na Etapa A; `vinculo_final` nos `pets.json`). Nunca entra em combate (teste por AST).

### 1.4 Python × web: batem no valor

Conferência por leitura, linha a linha, de `vinculo.py` contra `vinculo.ts` e dos pontos de chamada:

| ponto | Python | web | igual? |
|---|---|---|---|
| fórmula, inicial, α, pesos, janelas | `ConfigVinculo` | `CVI` (conferida por `constantes.test.mjs`) | sim |
| limiar do pedido | `CONFIG_MEMORIA_ESPACOS.limiar_necessidade_pedido` 0,5 | `CME.limiarPedido` 0,5 | sim |
| cuidados que fecham pedido | `CUIDADOS_QUE_ATENDEM` (7 ações) | `CUIDADOS` (as mesmas 7) | sim |
| vontade → ação do dono | `ATENDE_VONTADE` | `ATENDE_VONTADE` | sim |
| desejo só quando muda | `_decisao_observada` (`d if mudou else None`) | `_desejo` (`mudou ? d : null`) | sim |
| ação do pet no feedback | `_acao_pet_atual` (última decisão) | `this.acao` | sim |
| recusa ainda alimenta o vínculo | `_depois_do_dono` na recusa | `_desobedeceu` chama `acaoDono` | sim |
| forçar, bronca sem motivo, pausa, teto | `ajustar` / `_amostra` / `limitar` | idem (`CTR.vincForcar`, `CED.vincBroncaSemMotivo`, `CTR.pesoPausa`, `CSO.tetoVinc`) | sim |
| versões | sempre (motores da personalidade em diante) | só pets v2+ | por desenho |
| **contador** | `limitar` acrescenta à série quando corta; `atualizacoes = len(serie)` | `limitar` não incrementa `n` | **não** (só o contador) |

A única diferença é de contagem, não de valor: um pet sombrio cortado para 0,6 tem `atualizacoes` uma unidade acima de `n`. Nenhum
valor, decisão ou tela depende disso; registrado em `docs/REGISTRO_DESVIOS.md` (2026-10-01), sem correção nesta tarefa. Não existe
gabarito de paridade do vínculo entre os dois motores (os RNGs diferem, logo as vidas diferem); a conferência é do código.

## 2. O defeito, com números

| artefato | medida | atencioso | aleatório | outros | atencioso − aleatório |
|---|---|---|---|---|---|
| `artifacts_v1_personalidade/completa/metrics.json` (`personalidade.por_braco.*.vinculo_final`; 10 ovos, 14 dias, 224 interações) | vínculo final médio | 0,539 [0,454; 0,628] | 0,607 [0,524; 0,689] | relapso 0,500; incoerente 0,419 | −0,069 [−0,206; +0,074] |
| idem (`obediencia`) | obediência | 0,918 | 0,771 | | +0,147 [+0,092; +0,205]: a obediência separa; o vínculo não |
| `artifacts_linhagem/sinal_dono/resultado.json` (`portadores.vinculo_final`; 640 vidas do E1: 40 genomas × 4 donos × 4 ambientes) | vínculo final médio | 0,424 [0,349; 0,501] | 0,600 [0,537; 0,659] | permissivo 0,729; relapso 0,469 | **−0,176 [−0,291; −0,061]** |
| idem (`fracao`) | de onde vem a variância | | | dono 0,393; dono × ambiente 0,188; resíduo 0,369; genoma 0,004 | o vínculo é quase só dono, e aponta para o lado errado |
| `artifacts_treino/resumo.json` (`por_braco.*.vinculo_final`; 10 ovos) | vínculo final médio | 0,563 | 0,605 | exigente **0,216**; relapso 0,476; incoerente 0,472 | o exigente é o único que o vínculo separa, pelo ajuste direto do forçar (−0,05) |
| `artifacts_campanha/mega/limiar_vinculo.json` (web, pets v5; 6 vidas de 3 dias, 16/dia) | Megas em 6 vidas, limiar 0,4 | **3** | **5** | incoerente 3; relapso 4 | em **todo** limiar da varredura (0,7 a 0,3) o aleatório chega em ≥ 4 e o atencioso em ≤ 3 |
| `artifacts_campanha/mega/vinculo_donos.json` (`vinculo_max_no_ultimate`) | maior vínculo no Ultimate | 0,232 a 0,495 | 0,655 a 0,751 (5 vidas; a 6ª parou no adolescente) | | o atencioso só passa de 0,4 em 3 vidas, por pouco (0,451; 0,475; 0,495) |

O limiar do Mega foi baixado de 0,7 para 0,4 (`docs/DESIGN_EVOLUCAO_CANONICA.md`) porque, com 0,7, nenhum dono coerente chegava
e o aleatório chegava. A varredura mostra que **nenhum limiar inverte a ordem**: o problema está na medida, não no corte.

## 3. A causa, com a conta

Conta sobre as vidas gravadas (`experiments/analisar_vinculo.py`): o `Vinculo` de cada replay é trocado por uma subclasse que só
anota as atualizações (componente, amostra, peso, se o pedido foi atendido ou perdeu) e o estado do pet **antes** de cada ação do
dono. Conferência: o vínculo final de cada replay é igual ao do artefato (40 de 40 na personalidade, 640 de 640 no E1, e o
`hash_parametros_educacao` do E1; falha alto se diferir). Replay: 3 s e 346 s. Números em `artifacts_v2_vinculo/resultado.json`.
"Empurrão" é a soma dos deslocamentos do vínculo causados pelo componente ao longo da vida (positivo sobe, negativo desce).

### 3.1 As 40 vidas da personalidade (`artifacts_v1_personalidade/completa`, protocolo `arena-v1-personalidade`)

| dono | n vidas | vínculo final | cuidados/vida | feedbacks/vida | fração dos avanços com necessidade baixa | cuidados com necessidade baixa (estrita / ampla) |
|---|---|---|---|---|---|---|
| aleatorio | 10 | 0,607 | 146,4 | 77,6 | 0,815 | 0,81 / 0,84 |
| atencioso | 10 | 0,539 | 87,2 | 136,8 | 0,041 | 0,64 / 0,65 |
| incoerente | 10 | 0,419 | 93,5 | 130,5 | 0,043 | 0,61 / 0,63 |
| relapso | 10 | 0,500 | 183,8 | 40,2 | 0,611 | 0,51 / 0,55 |

| dono | atendimento: n/vida (atendidos) · amostra média · empurrão | coerência: n/vida · amostra média · empurrão | desejo: n/vida (atendidos) · amostra média · empurrão |
|---|---|---|---|
| aleatorio | 539,5 (456,1) · 0,518 · **+0,733** | 55,2 · 0,524 · −0,316 | 12,5 (1,3) · 0,106 · −0,309 |
| atencioso | 0,5 (0,5) · 0,938 · +0,021 | 123,7 · 0,623 · +0,868 | 31,8 (0,0) · 0,000 · **−0,851** |
| incoerente | 0,4 (0,4) · 0,938 · +0,019 | 106,9 · 0,511 · +0,579 | 31,9 (0,5) · 0,012 · −0,679 |
| relapso | 426,2 (231,6) · 0,289 · +0,086 | 24,0 · 0,652 · +0,351 | 20,6 (1,5) · 0,088 · −0,437 |

(Necessidade baixa = `min(fome, higiene) < 0,5`, o critério do pedido; "ampla" inclui o humor. Sem pausa de treino nem ajustes
nestas vidas: os donos da v1 não treinam.)

### 3.2 Três mecanismos, todos a favor de quem age sem olhar

1. **Atendimento mede oportunidade, não resposta.** O pedido só abre quando fome ou higiene já está abaixo de 0,5, e o atencioso
   cuida exatamente nesse limiar a cada 15 minutos (`ConfigDonos.limiar_alimentar`/`limiar_limpar` 0,50): o pet dele passa
   **4% dos avanços** com necessidade baixa e abre **0,5 pedido por vida**. O pet do aleatório passa **81%** do tempo abaixo do
   limiar e abre **540 pedidos**; como o aleatório faz 146 cuidados em 14 dias (um a cada 2,3 h, dentro da janela de 4 h) e
   **um cuidado fecha todos os pedidos abertos**, 456 dos 540 são "atendidos", com amostra média 0,518 > 0,5. Empurrão:
   **+0,73** no aleatório, +0,02 no atencioso. O relapso (3 visitas por dia) abre 426 pedidos e perde metade: amostra 0,289, o
   único que o atendimento não sobe. **O componente premia o dono que deixa o pet pedir e cuida com frequência**, e não vê o dono
   que não deixa chegar ao pedido.
2. **Desejo mede coincidência.** A vontade dura 60 ticks e só é fechada pela ação exata. O atencioso age por necessidade, não por
   vontade: **32 vontades por vida, 0 atendidas**, 32 amostras 0 (empurrão **−0,85**, o maior da vida dele). O aleatório, que
   acerta por acaso, atende 1,3 de 12,5 (amostra 0,106, empurrão −0,31). O desejo derruba todos, e derruba mais quem é coerente.
3. **Coerência mede sinal constante por ação, e o dono coerente muda o sinal com o contexto.** `julgar_acao` dá +1 a brincar
   descansado e −1 a brincar cansado, +1 a dormir à noite e −1 de dia, +1 a chamar atenção com necessidade e −1 sem: para o
   vínculo, que agrupa só pela ação do pet, isso é incoerência. Amostra média: atencioso **0,623**, relapso 0,652 (feedback em
   rajada, poucas amostras), aleatório 0,524, incoerente 0,511. É o único componente que favorece o atencioso, e favorece pouco
   (contrafactual "só coerência": +0,065). Agrupando por (ação, situação do pet), a amostra do atencioso sobe para **0,740**, a do
   incoerente fica em 0,502 e a do aleatório em 0,527 (tabela abaixo).

| dono | coerência de hoje (por ação): amostras/vida · média | coerência por situação (ação × necessidade baixa × cansado × noite): amostras/vida · média |
|---|---|---|
| aleatorio | 55,2 · 0,524 | 35,5 · 0,527 |
| atencioso | 123,7 · 0,623 | 102,9 · 0,740 |
| incoerente | 106,9 · 0,511 | 79,9 · 0,502 |
| relapso | 24,0 · 0,652 | 8,4 · 0,806 |

Somando: o atencioso recebe 124 amostras de coerência em torno de 0,6 e 32 de desejo em 0; o aleatório recebe 540 de atendimento
em torno de 0,52, que dominam tudo. O vínculo final é, em essência, **a frequência com que o dono age em janelas curtas depois de
o pet entrar em falta**.

### 3.3 Contrafactuais sobre o fluxo gravado (personalidade)

Recalculados com a mesma fórmula sobre as mesmas amostras, mantendo ajustes e teto, com os eventos da vida fixos (na vida real
um vínculo diferente mudaria a obediência e, com ela, um pouco da vida: é conta, não run). A linha "hoje" reproduz o replay.
"Coerência contextual" = a regra de hoje com o histórico por (ação, situação do pet). "Atendimento por resposta" = cada cuidado
do dono vira amostra 1 com necessidade baixa no estado que ele viu e 0 sem; o pedido sai.

| variante | aleatório | atencioso | incoerente | relapso | atencioso − aleatório |
|---|---|---|---|---|---|
| hoje (conferência: igual ao replay) | 0,607 | 0,539 | 0,419 | 0,500 | −0,069 |
| só atendimento | 0,648 | 0,521 | 0,517 | 0,509 | −0,127 |
| só coerência | 0,547 | 0,612 | 0,507 | 0,653 | +0,065 |
| só desejo | 0,326 | 0,124 | 0,135 | 0,253 | −0,202 |
| sem atendimento | 0,490 | 0,535 | 0,416 | 0,476 | +0,045 |
| normalizado pela média do aleatório (controle embutido) | 0,604 | 0,572 | 0,472 | 0,510 | −0,032 |
| coerência contextual no lugar da coerência | 0,603 | 0,642 | 0,398 | 0,491 | +0,038 |
| coerência contextual, sem atendimento | 0,452 | 0,638 | 0,394 | 0,431 | +0,186 |
| **só coerência contextual** | 0,529 | **0,752** | 0,505 | 0,673 | **+0,223** |
| atendimento por resposta (estrita) | 0,712 | 0,520 | 0,457 | 0,516 | −0,192 |
| atendimento por resposta (ampla, com humor) | 0,729 | 0,520 | 0,457 | 0,564 | −0,209 |
| atendimento por resposta ampla + coerência contextual | 0,723 | 0,589 | 0,445 | 0,570 | −0,134 |

Leitura: tirar o atendimento já inverte o sinal (+0,045), mas deixa todo mundo perto de 0,5 (o desejo derruba os quatro);
normalizar pela média do aleatório **não corrige** (−0,032), porque o atencioso continua sem amostra de atendimento e com 32 zeros
de desejo; "atendimento por resposta" **piora** (−0,19 a −0,21): 81% dos cuidados do aleatório caem com o pet em falta, porque o
pet dele vive em falta, contra 64% do atencioso, que também brinca por humor e acaricia sem necessidade. **Toda medida que amostra
"o dono respondeu à falta" premia quem cria a falta.** O que separa é a coerência por situação: sozinha, +0,223; com o desejo, +0,186.

### 3.4 A mesma conta no E1 (640 vidas, educação-v1 ligada)

Vidas de 14 dias com travessuras, lesões, sparring e treino (`artifacts_linhagem/natureza_criacao/especie_fixa`; logs em
`D:/Trab/digilab/arquivo/artifacts_linhagem_E1_vidas/`); donos atencioso, aleatório, permissivo e relapso (o incoerente não está
no E1). Aqui o atencioso **cuida muito e fala pouco**: 219 cuidados por vida (104 idas ao banheiro pelos avisos, 53 limpezas,
40 refeições) e só 27 feedbacks; o aleatório faz 144 cuidados e 43 feedbacks.

| dono | n vidas | vínculo final | cuidados/vida | feedbacks/vida | fração dos avanços com necessidade baixa | cuidados com necessidade baixa (estrita / ampla) |
|---|---|---|---|---|---|---|
| aleatorio | 160 | 0,600 | 144,0 | 43,2 | 0,815 | 0,83 / 0,84 |
| atencioso | 160 | 0,424 | 218,5 | 27,1 | 0,048 | 0,27 / 0,28 |
| permissivo | 160 | 0,729 | 224,3 | 23,6 | 0,027 | 0,18 / 0,18 |
| relapso | 160 | 0,469 | 188,8 | 39,1 | 0,646 | 0,56 / 0,61 |

| dono | atendimento: n/vida (atendidos) · amostra média · empurrão | coerência: n/vida · amostra média · empurrão | desejo: n/vida (atendidos) · amostra média · empurrão | pausa: n/vida · amostra média | ajustes/vida |
|---|---|---|---|---|---|
| aleatorio | 563,7 (489,3) · 0,561 · **+0,976** | 29,1 · 0,453 · −0,372 | 7,0 (0,5) · 0,066 · −0,183 | 9,6 · 0,462 | bronca sem motivo 0,52; forçar 1,53 |
| atencioso | 2,7 (0,7) · 0,798 · +0,015 | 12,4 · 0,567 · +0,080 | 39,3 (1,0) · 0,023 · **−0,872** | 14,2 · 1,000 | — |
| permissivo | 0,1 (0,1) · 0,875 · +0,003 | 10,6 · 1,000 · +0,330 | 21,2 (0,5) · 0,031 · −0,610 | 14,5 · 1,000 | — |
| relapso | 455,1 (250,6) · 0,296 · −0,258 | 23,8 · 0,585 · +0,204 | 20,7 (2,2) · 0,108 · −0,445 | 10,3 · 1,000 | — |

| dono | coerência de hoje: amostras/vida · média | coerência por situação: amostras/vida · média |
|---|---|---|
| aleatorio | 29,1 · 0,453 | 19,5 · 0,463 |
| atencioso | 12,4 · 0,567 | 7,2 · 0,764 |
| permissivo | 10,6 · 1,000 | 7,8 · 1,000 |
| relapso | 23,8 · 0,585 | 9,1 · 0,786 |

| variante | aleatório | atencioso | permissivo | relapso | atencioso − aleatório |
|---|---|---|---|---|---|
| hoje (conferência: igual ao replay) | 0,600 | 0,424 | 0,729 | 0,469 | −0,176 |
| só atendimento | 0,627 | 0,499 | 0,504 | 0,470 | −0,128 |
| só coerência | 0,438 | 0,560 | 0,811 | 0,601 | +0,122 |
| só desejo | 0,295 | 0,118 | 0,226 | 0,270 | −0,176 |
| sem atendimento | 0,410 | 0,431 | 0,729 | 0,529 | +0,021 |
| normalizado pela média do aleatório | 0,571 | 0,617 | 0,839 | 0,449 | +0,046 |
| coerência contextual no lugar da coerência | 0,604 | 0,446 | 0,704 | 0,470 | −0,158 |
| coerência contextual, sem atendimento | 0,402 | 0,453 | 0,703 | 0,573 | +0,051 |
| **só coerência contextual** | 0,434 | **0,644** | 0,761 | 0,676 | **+0,209** |
| atendimento por resposta (estrita) | 0,734 | 0,317 | 0,276 | 0,626 | −0,417 |
| atendimento por resposta (ampla) | 0,749 | 0,319 | 0,276 | 0,661 | −0,430 |
| atendimento por resposta ampla + coerência contextual | 0,769 | 0,321 | 0,260 | 0,671 | −0,447 |

Leitura do E1: os mesmos três mecanismos, mais fortes. O aleatório ganha **+0,98** de atendimento (564 pedidos, 489 "atendidos");
o atencioso perde **−0,87** no desejo (39 vontades, 1 atendida) e quase não tem coerência (12 feedbacks por vida), então termina em
0,42 apesar das 14 pausas respeitadas. O permissivo (cuida como o atencioso e cede com petisco) fica em 0,73 porque o feedback dele
é todo positivo (coerência 1,0) e tem menos vontades expiradas. Com o desejo mantido, a correção quase some (+0,051): o atencioso
do E1 tem poucas amostras de feedback para compensar 39 zeros. **Só a coerência por situação separa nos dois conjuntos** (+0,223 e
+0,209), com o relapso e o permissivo acima do aleatório (os dois dão feedback coerente; o que lhes falta é cuidado, e cuidado já é
medido pela saúde e pelas mortes).

### 3.5 Por que o Mega vai para o aleatório

Nas vidas da web do artefato do Mega (3 dias, 48 interações, pets v5), os mesmos componentes rodam em `vinculo.ts`. Com 48
interações cada amostra pesa mais, e o atencioso termina entre 0,00 e 0,30 (seção 2). A decomposição por componente dessas vidas
**não foi feita nesta tarefa** (exigiria um script em `web/app/test/`; a tarefa pede `experiments/`); fica como conferência para a
frente que implementar o vínculo novo. O mecanismo é o mesmo porque o código é espelho (seção 1.4).

## 4. Alternativas de desenho

Em comum: ficam na média móvel em [0, 1] (obediência, Mega, fala e saves não mudam de escala); valem só para uma **versão de pet
nova** na web (o coordenador reserva o número) e, no Python, para uma `ConfigVinculo` com **chaves desligadas por padrão**, para que
os protocolos com hash e os artefatos continuem reproduzindo. Os números de "efeito esperado" são os contrafactuais da seção 3
(conta sobre vidas gravadas, não run): o efeito numa vida nova difere um pouco porque o vínculo entra na obediência.

### 4.1 A — Previsibilidade: só a coerência, por ação e situação do pet (recomendada)

- **O que mede:** se o dono é **previsível para o pet**: o feedback sobre a mesma ação, **na mesma situação do pet**, tem o mesmo
  sinal. A situação é discretizada com limiares que o próprio pet já usa, nenhum do dono: necessidade baixa (`min(fome, higiene)
  < 0,5`, o limiar do pedido), cansado (`energia < 0,25`, a regra do instinto) e noite (`ConfigPadrao.e_noite`): 8 situações × ação.
  Sem histórico na situação, sem amostra (como hoje). Atendimento e desejo saem do vínculo (o atendimento continua onde já estava:
  na memória, como `demora`, e na latência do bandit; o desejo continua nas métricas de cumprimento). Ajustes diretos, pausa e teto
  da sombria ficam como estão.
- **Efeito esperado (`so_coerencia_contextual`):** personalidade atencioso 0,752, relapso 0,673, aleatório 0,529, incoerente 0,505
  (**+0,223**); E1 atencioso 0,644, permissivo 0,761, relapso 0,676, aleatório 0,434 (**+0,209**). O aleatório e o incoerente ficam
  em ~0,5 (feedback ao acaso = indiferente); quem dá feedback coerente sobe, cuide muito (permissivo) ou pouco (relapso).
- **Risco de virar canal de cuidado:** nenhum. Nenhum termo lê necessidade, saúde, latência ou frequência de cuidado. Vira um canal
  de **feedback**: o dono mudo fica em 0,5 e só se move pelos ajustes (forçar, bronca sem motivo) e pela pausa.
- **Riscos próprios:** (i) **tautologia parcial**: a situação "necessidade baixa" usa o mesmo número (0,5) que o atencioso usa para
  cuidar, mas o critério do feedback dele é outro (0,35 e 0,40, `ConfigDonos`); as situações do pet não reproduzem a regra do dono, e
  a amostra do atencioso fica em 0,74–0,76, não em 1. Um dono humano coerente com outros limiares também sobe, porque o que conta é
  repetir o sinal na mesma situação. (ii) **Pouca amostra**: 103 por vida no atencioso da personalidade, mas 7 a 9 no atencioso, no
  permissivo e no relapso do E1: alta variância por vida, e o vínculo anda devagar em quem fala pouco. (iii) Ninguém cai abaixo de
  0,5 sem ajuste direto; o Mega (≥ 0,4) ficaria aberto a quase todo mundo e precisa de limiar novo. (iv) O relapso em 0,67 é correto
  pelo que a medida diz (ele é coerente quando fala), mas pode surpreender quem espera que vínculo = cuidado.
- **O que muda:** `vinculo.py` (chave do histórico passa a (ação, situação); `ConfigVinculo` ganha `coerencia_por_situacao: bool` e os
  limiares da situação, `peso_atendimento` e `peso_desejo` 0 na variante nova; `acao_dono` recebe a observação do pet antes da
  ação); `vinculo.ts` + `CVI` (espelho), `constantes.test.mjs`/`exportar_constantes_web.py`; `VERSAO_PET` nova; `medir_vinculo_mega.mjs`
  roda de novo para o limiar do Mega (0,4 foi calibrado no vínculo velho); gabaritos e assinaturas v1–v9 intactos;
  `test_personalidade.py` ganha o caso da variante; a fala ganha as frases "sei o que esperar de você" / "você me confunde".

### 4.2 B — Previsibilidade com o desejo: coerência por situação, atendimento fora, desejo fica

- **O que mede:** o mesmo que A, mais "o dono atende o que eu queria" (o desejo de hoje).
- **Efeito esperado (`coerencia_contextual_sem_atendimento`):** personalidade atencioso 0,638, aleatório 0,452, incoerente 0,394,
  relapso 0,431 (**+0,186**); E1 atencioso 0,453, aleatório 0,402, permissivo 0,703, relapso 0,573 (**+0,051**).
- **Risco de virar canal de cuidado:** baixo, mas o desejo continua medindo coincidência: quem faz muito cuidado ao acaso acerta
  mais vontades.
- **Riscos próprios:** no E1 a correção quase some, porque o atencioso de lá dá pouco feedback e expira 39 vontades por vida; o
  resultado depende de quanto o dono fala. Vantagem: quem dá feedback ao acaso cai abaixo de 0,5 (incoerente 0,39), o que dá uma
  frase clara na fala.
- **O que muda:** o de A, com `peso_desejo` mantido em 0,5.

### 4.3 C — Cuidado a tempo pelo estado (não recomendada; registrada porque é a correção óbvia)

- **O que mede:** em vez do pedido, o **tempo que cada necessidade passa abaixo do limiar** até o cuidado que a atende:
  amostra `1 − tempo/janela` quando o dono atende, 0 quando passa da janela. Lido do estado a cada decisão do pet, não do
  `chamar_atencao`.
- **Efeito esperado (proxy, `fracao_avancos_necessidade_baixa`):** o atencioso passa 4–5% dos avanços em falta, o incoerente 4%,
  o permissivo 3%, o relapso 61–65%, o aleatório 81%. A ordem inverte, com margem.
- **Risco de virar canal de cuidado:** **é** o canal de cuidado. Mede o mesmo que a saúde e as mortes já medem
  (`docs/LEITURA_CONSOLIDADA_DONO.md`: "o dono pesa pelo cuidado"), e não distingue atencioso de incoerente (4% × 4%): o vínculo
  deixaria de dizer qualquer coisa sobre coerência, que é o que o cânone do Mega pede ("ligação com o parceiro").
- **O que muda:** `vinculo.py`/`vinculo.ts` passam a ler o estado a cada decisão; o resto como em A.

### 4.4 Testadas na conta e descartadas

| ideia | personalidade | E1 | por quê |
|---|---|---|---|
| normalizar cada amostra pela média do aleatório (controle embutido) | −0,032 | +0,046 | o atencioso continua sem amostra de atendimento e com dezenas de zeros de desejo |
| atendimento por resposta (cuidado com necessidade baixa = 1, sem = 0) | −0,192 / −0,209 | −0,417 / −0,430 | o pet do aleatório vive em falta: 81–83% dos cuidados dele caem com necessidade baixa |
| só tirar o atendimento, resto igual | +0,045 | +0,021 | o desejo derruba todos para ~0,4–0,5 |
| só a coerência de hoje (por ação) | +0,065 | +0,122 | pune o dono que muda o sinal com a situação |
| coerência por situação, mas com o atendimento | +0,038 | −0,158 | o atendimento domina |
| mexer no limiar do Mega | varredura 0,7 → 0,3: aleatório ≥ 4 de 6, atencioso ≤ 3 em todos (`limiar_vinculo.json`) | | o corte não inverte a ordem; a medida é que está errada |

## 5. Recomendação e pergunta ao Matheus

**Adotar a alternativa A** (previsibilidade: só a coerência do feedback, por ação e situação do pet; atendimento e desejo saem),
numa versão de pet nova e com chave desligada por padrão no Python, e recalibrar o limiar do Mega com `medir_vinculo_mega.mjs`
depois, não antes. **B** mantém o desejo e fica frágil quando o dono fala pouco (+0,051 no E1); **C** inverte a ordem, mas vira
saúde com outro nome.

**Pergunta:** o Matheus aprova a **A** (só previsibilidade), prefere a **B** (previsibilidade com o desejo) ou quer outra
combinação (por exemplo, A com um teto de amostras por dia, para o dono que fala muito não dominar)? Com a resposta, a
implementação vira frente própria (fora desta tarefa), com o número da versão de pet reservado pelo coordenador.

## 6. O que fica fora e o que fica aberto

- Implementar o vínculo novo, o limiar do Mega e a obediência: fora (tarefa, seção 6).
- A decomposição por componente das vidas da web do artefato do Mega (seção 3.5): não feita; conferência para a frente que implementar.
- Os contrafactuais são sobre eventos fixos; a frente que implementar deve medir em vidas novas (sementes de calibração), com o
  plano de análise registrado antes, e só então validar. Os limiares da situação (0,5; 0,25; noite) são PROPOSTOS.
