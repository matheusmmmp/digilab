# Plano de análise V3: a ablação do aprendizado no jogo (EVIDENCIA A2)

**Status: APROVADO pelo Matheus em 2026-11-16,** com as AB-1 a AB-7 DECIDIDAS pela recomendação ("Aprovo, pode rodar") e a AB-2b ("Mapear para acariciar/tapa"), nesta sessão. Escrito em 2026-11-16 (Claude Code, Opus 5.5, branch `v3-evidencia-a2`), na fase A2 do pedido de
2026-11-16 (`docs/TAREFA_V3_EVIDENCIA.md`), depois do CHECKPOINT A2 ("Aceitar e seguir A2", D-EV-A1-7).

## 0. A trava e o que já foi visto

**Nenhuma vida da run roda antes de três coisas:**
1. este plano commitado, com "APROVADO pelo Matheus" no cabeçalho (o orquestrador confere e recusa sem);
2. as decisões AB-1 a AB-7 (seção 9) DECIDIDAS;
3. a faixa da seção 2.3 em `FAIXAS_RESERVADAS` (o orquestrador confere).

O plano entrou PROPOSTO num commit só dele (`2481e33e`). O código (o harness, o orquestrador, as configs e os testes) entra **no commit
da aprovação**, antes de qualquer vida da run, e fica no branch até o merge do Matheus.

**O que já foi visto antes deste plano:** uma vida de 3 dias do ovo do jogo (v38, montado como na seção 2.1), semente 101 (dos testes,
fora da faixa), dono atencioso, braço A, só para medir o tempo: 0,28 s e 288 decisões. Nenhuma medida de ação ou de motivo foi lida.
Depois da aprovação, a fumaça do harness (semente 101, os 3 donos, os 2 braços) mostrou só o que o código precisava: o B sem unidade com
aprendido e o A com; a unidade escolhida achada pela chave em lista; e o dono incoerente com o mesmo log do atencioso, porque o retorno dele
(`elogiar`, `repreender`) não é ação do dono no jogo e o laço o descartava. Daí a AB-2b. Nenhuma fração de ação ou de motivo foi lida.

**O que este plano não afirma:** que o aprendizado é bom ou ruim para o pet; nada sobre o Python (a C4 já mediu lá); nenhuma alegação de
novidade.

## 1. A pergunta, a hipótese e a previsão, escritas antes

**A pergunta (a do pedido):** o P1 e o P2 do M-PLAST (`web/app/motor/digibrain/plast.ts`) mudam o comportamento do pet **no jogo**, e não
só no Python?

**A hipótese (H):** com o P1 e o P2 ligados (o braço A), a distribuição das ações e a do motivo diferem das do mesmo pet com o estado
aprendido zerado a cada decisão (o braço B). A previsão é "difere"; o sinal de cada categoria é SEM FONTE, e nenhum é previsto.

**O que refutaria H (a regra do pedido):** as distribuições iguais, com o IC95 de toda diferença A − B incluindo o 0 (seção 5.3).

## 2. O cenário e o desenho

### 2.1 O pet e a vida

- **O pet:** o ovo do jogo de hoje (`VERSAO_PET`, a v38), montado como o jogo e o `scripts/equilibrio_cuidado/e0.ts` montam: `new
  Motor(semente, VERSAO_PET)`, `ligarProduto` com as três chaves, `trocarCerebro("modular")` e `ligarPonteLuta(true)` (AB-3). O orquestrador
  falha alto se `cerebroAtual` não for o modular ou se o `p1` e o `p2` da config do M-PLAST não estiverem ligados.
- **O dono:** os donos sintéticos do motor (`motor/donos.ts`, `criarDono`, o espelho do `donos.py` da C4), no laço do
  `test/evolucao_canonica.test.ts`: um passo de `CD.passo` minutos, o orçamento de 16 ações por dia, só as `ACOES_DONO_JOGO_V11`, a rng do
  dono `hashSemente("dono", semente, tipo)`. Sem luta (AB-4).
- **O retorno do dono (AB-2b):** o `elogiar` vira `acariciar` e o `repreender` vira `tapa`, a correspondência da tela do jogo (Elogiar =
  acariciar, Repreender = tapa), antes do filtro das `ACOES_DONO_JOGO_V11`. Uma ação que o motor recusa (o `observar` levanta, sem ser a
  morte) é contada e a vida segue, como no `test/dc3d_hoje.ts`; o número de recusas vai no descritivo.
- **As "3 vidas" do pedido:** os três donos `atencioso`, `relapso` e `incoerente`, cada um uma vida de **3 dias** (AB-2).
- **A morte:** a vida para em `m.morte`; as medidas usam as decisões até ali, e o número de mortes por braço vai no resultado.

### 2.2 Os braços (o mesmo código)

- **A:** o pet como o jogo o choca (o P1 e o P2 ligados).
- **B:** o mesmo pet, a mesma semente, o mesmo dono e o mesmo código. A única diferença é um invólucro instalado na instância, de fora, no
  `m.lab.impulso.unidades` (a leitura do incentivo e do hábito em cada decisão, `adapt.ts`): antes de cada chamada, ele zera **no lugar**
  o `H`, o `desfecho` e o `andar` do `m.lab.plast`, e então chama o método original. O P1 e o P2 continuam rodando (o desfecho e o H andam
  entre as decisões), mas nenhuma decisão os lê com valor diferente de 0. Os contadores (`consumos`, `amostras_andar`, `creditos`) não são
  tocados. Nenhum arquivo do motor muda.
- **A conferência da manipulação (falha alto):** em B, os termos `incentivo` e `habito` de toda unidade de toda decisão são 0; em A, ao
  menos uma decisão da run tem um deles diferente de 0.
- **O pareamento:** A e B começam iguais; depois da primeira decisão diferente, a vida diverge (o dono reage ao pet). A comparação é da
  distribuição na vida inteira, não decisão a decisão.

### 2.3 As sementes e o N (AB-1, AB-5)

- **A faixa:** 98101…98505, nova, conferida livre na `origin/main` e em todos os branches remotos em 2026-11-16 (a 96xxx e a 97xxx são da
  A1; a 96xxx colide com a LONGE_GEOMETRIA, D-EV-A1-8).
- **O N:** K = 200 sementes, 98101…98300, uma por unidade. Cada semente dá 3 vidas (os 3 donos) em cada braço: 1 200 vidas.
- **A unidade:** a semente, com a média das 3 vidas dela (os donos pesam igual).

## 3. As medidas (por vida)

Lidas de `m.lab.motivos` (um registro por decisão, `adapt.ts`), na vida inteira:
- **As ações:** a fração das decisões em cada um dos 7 `COMPORTAMENTOS_DIGIBRAIN` (`ocioso`, `dormir`, `comer`, `brincar`,
  `chamar_atencao`, `explorar`, `emburrar`), pelo `acao` do registro.
- **O motivo:** não há um campo "motivo" único; o registro guarda a unidade escolhida. As frações das decisões:
  - pelo `tipo_escolha`, agrupado em `comida` (as classes `racao`, `a`, `b`, `c`, `podre`), `cheiro`, `bola`, `vagar`, `ponto` e
    `sem_objeto` (o null); um tipo fora destes falha alto;
  - com o `reflexo` verdadeiro; com o `nada_a_fazer` verdadeiro.
- **Ao lado (descritivo):** o número de decisões, a morte, a média dos termos `incentivo` e `habito` da unidade escolhida em A, e a
  distância de variação total entre as distribuições médias de ação de A e de B.

## 4. O determinismo

Cada vida roda duas vezes, e o sha256 dos `acao` e `tipo_escolha` em ordem tem de sair igual (falha alto). Em A, a vida também é refeita por
`Motor.reproduzir(semente, log, VERSAO_PET)`, e os `acao` têm de sair iguais (falha alto). Em B, o replay do jogo não instala o invólucro;
vale a dupla execução.

## 5. A análise (uma vez)

### 5.1 O teste

- Para cada uma das **15 medidas** (7 de ação, 8 de motivo), a diferença A − B por unidade, o IC95 pelo t (gl 199) e o p bilateral, com
  o `ic_t` e o `t_unilateral` de `digilab/metrics.py` (os mesmos do `contraste_t` da C4, que dá só o p unilateral).
- **Uma família de 15, com Holm** sobre os p bilaterais, α = 0,05.
- Ao lado, sem mudar a decisão: a margem efetiva de cada medida (o menor efeito com poder 0,8 pelo dp observado).

### 5.2 Por que sem margem

O pedido define a refutação pelo IC que inclui o 0, sem margem de equivalência; este plano não inventa uma. A margem efetiva vai ao lado,
para que um "nula" com IC largo não seja lido como "igual".

### 5.3 A regra de leitura, escrita antes

| o que sai | condição | a leitura |
|---|---|---|
| **muda** | ao menos uma das 15 medidas rejeitada pelo Holm (`metrics.holm`, α = 0,05) | o P1 e o P2 mudam o comportamento no jogo. **H confirmada** |
| **nula** | o IC95 (sem ajuste) de **todas** as 15 inclui o 0 | as distribuições iguais. **H refutada** |
| **indeterminado** | algum IC95 sem ajuste exclui o 0, mas nenhum passa no Holm | **H não confirmada nem refutada** |

**O que o CHECKPOINT A3 faz com a leitura:** a classe vai ao Matheus como saiu. Pelo pedido, se a ablação der nula, o "aprendizado em
vida" é política fixa + estado + memória para efeito de produto, e a A1 ganha peso. Esta run não decide isso.

## 6. Uma vez, e o que fica no git

- **A run roda uma vez,** com um comando só: `python experiments/run_v3_ablacao_aprendizado.py --config
  experiments/configs/v3_ablacao_aprendizado/run.json`. Ele chama o harness Node (`node web/app/scripts/ablacao_aprendizado.ts`), que grava
  as medidas por vida, e faz a análise da seção 5. O orquestrador recusa gravar por cima de uma pasta que existe.
- **Em `artifacts_v3_ablacao_aprendizado/run/`:** o `meta.json`, o `medidas.json` (o `.gz` só acima de 100 MB) e o `resultado.json`.
- **O meta grava:** o commit e o `git_limpo`; o comando exato e o do Node; as versões do Python e do Node; o sha256 do plano, da config, do
  orquestrador, do harness, do `plast.ts`, do `adapt.ts` e do `impulso.ts`; o sha256 de cada artefato; e, por vida, o sha256 do log e da
  sequência das decisões.
- **O resultado** vai em `docs/RESULTADO_V3_ABLACAO_APRENDIZADO.md`, com a leitura pela seção 5.3.

## 7. Se algo falhar

Uma falha alta (a manipulação, o determinismo, o replay, um tipo desconhecido) **para a run, que volta ao Matheus** com o comando, a saída e
a lacuna. Nada se conserta para o número sair.

## 8. O custo esperado

1 200 vidas × 2 execuções × ~0,3 s, mais o replay de A: ~15 min num processo Node.

## 9. As decisões para o Matheus

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| AB-1 | o N | **K = 200 sementes** (600 vidas por braço). O pedido diz "mesma semente, mesmas 3 vidas": com 1 semente, o IC95 teria n = 3 (gl 2) e um "nula" não diria nada. Cada vida custa 0,3 s | com o literal, uma nula com IC enorme mudaria a proposta comercial no CHECKPOINT A3 sem base |
| AB-2 | as 3 vidas | os 3 donos `atencioso`, `relapso` e `incoerente` por semente; o `aleatorio` fica fora (age sem olhar o pet) | com outros donos, o resultado vale para outro cuidado |
| AB-3 | o pet | o ovo do jogo (v38, o modular de hoje), não o pet de teste v16 do laboratório | o v16 responde pelo laboratório, não pelo jogo |
| AB-4 | a luta | sem luta e sem arena | a luta mexe no corpo e no humor; fica para outra pergunta |
| AB-5 | a faixa | 98101…98505 | — |
| AB-6 | o braço B | o zerar no lugar antes de cada leitura do `impulso.unidades` (seção 2.2), não antes do `agir` (que deixaria o P1 da decisão anterior entrar na de agora) | zerar antes do `agir` deixa um resto do aprendizado em B |
| AB-2b | o retorno do dono | `elogiar` → `acariciar`, `repreender` → `tapa` (decidida depois da fumaça; seção 2.1) | sem o mapa, o incoerente é o atencioso de novo |
| AB-7 | a regra | a da seção 5.3: uma família de 15 com Holm; "nula" só com todos os IC incluindo o 0 | uma regra mais frouxa daria "muda" por acaso; uma mais dura, "indeterminado" demais |

## 10. Referências

Nenhuma: o desenho é o do pedido, com o teste da C4. SEM FONTE para o tamanho esperado do efeito.
