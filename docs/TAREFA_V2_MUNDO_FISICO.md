# Tarefa — V2: o mundo físico mínimo (W-TAREFA-MUNDO, rodada 16)

Status (2026-10-07): **PROPOSTO**. **MF-1 a MF-4 DECIDIDAS pelo Matheus em 2026-10-07, todas pela recomendação** (seção 11). Só papel. Esta tarefa não autoriza run; o plano de análise é `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`,
commitado junto, antes de qualquer run.

Parte de `docs/futuro/mundo_fisico.md`:
- as decisões M-1 (mapa 2D contínuo), M-2 (vista inclinada) e M-3 (arrastar e soltar a comida);
- a seção 6, item 1 (o mundo físico mínimo);
- a seção 7 (consequências para a pesquisa);
- as decisões de 2026-10-07 que já valem: **M-4** (quatro regiões: casa, jardim, campo e mata) e **M-5** (a ordem da seção 6).

Lê também:
- `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md` (PR #203), seção 5: no mundo de hoje a consequência ensina o pet a ficar parado;
- `docs/RESULTADO_V2_N3.md`: o G-P1 falhou no mundo `padrao` (+0,0008 [−0,0067; +0,0077]).

**Não amarra o mundo a nenhum cérebro.** O mundo expõe percepção e consequência por uma interface que qualquer cérebro pode usar: o
instinto, o A, o B, o C ou um cérebro que planeja. O porte do v11 está pausado (`docs/V2_RODADA_16.md`, seção 6), e esta tarefa vale para
a pesquisa no Python. O porte para a web cobre só o motor e a paridade (seção 8); a tela fica para depois da prancha W-PRANCHA-MAPA.

## 1. O que entra e o que fica fora

**Entra (item 1 da seção 6):**
- o mapa 2D contínuo com as quatro regiões;
- a comida deixada pelo dono num ponto do mapa (`deixar_comida`) e a bola deixada num ponto (`deixar_bola`);
- as árvores que derrubam frutas, a recarga, a comida que apodrece e a bola que rola;
- o deslocamento até um alvo, com gasto de energia pela distância;
- a visão por raio e o cheiro;
- a fome urgente indo à comida mais próxima vista ou cheirada.

**Fica fora:**
- tédio, curiosidade e solidão (item 2, a W-TAREFA-CORPO do chat B);
- a podre que tenta o instinto, e a praga (item 3);
- o dispensador (item 4);
- o ninho com conforto, a casa e a saudade (item 5): dormir continua igual em qualquer ponto;
- o cultivo e as palavras (item 6);
- o carinho e o tapa no corpo;
- a tela do mapa.

## 2. A chave e o motor

- **Chave:** `ConfigMundo.ligada` (em `digilab/config.py`), desligada por padrão.
- **Motor:** `MotorMundo`, num arquivo novo `digilab/mundo.py`. É subclasse da cadeia de hoje (`MotorAmbiente` → `MotorFrutas`), como as
  frutas (N4) e a bola (A1) entraram. **`engine.py` não muda** (sha256 conferido no teste), e `ambiente.py` e `frutas.py` também não.
- **Com a chave desligada:** nenhuma rng nova, nenhum registro novo, nenhuma chave nova em `estado()`. É o `MotorFrutas` byte a byte.
- **Com a chave ligada**, o mundo substitui o cenário do N4 e do A1:
  - frutas, ração e bola passam a ser objetos com posição;
  - `ConfigFrutas.ligada` e `ConfigBola.ligada` junto com o mundo levantam erro;
  - os gestos de hoje (`alimentar`, `oferecer_fruta_<f>`, `por_bola`, `tirar_bola`) no log de uma vida com o mundo levantam erro: o gesto
    é o `deixar_*` (seção 4).
- **`AcaoPet` não ganha membro.** Explorar, comer e brincar ganham sub-decisões de alvo (seção 5). `AcaoUsuario` também não ganha membro: os
  eventos novos são tipos novos do log, como a `luta` da educação.

## 3. O mapa e as posições (inteiros)

**Unidades:**
- o mapa é uma grade de **64 × 30 células**, e cada célula tem **16 subunidades**;
- uma posição é `(x, y)` em subunidades, inteiros, com `0 ≤ x < 1024` e `0 ≤ y < 480`;
- a distância é `d = isqrt(dx² + dy²)`, a raiz inteira (`math.isqrt` no Python; a mesma conta em inteiros no TypeScript, sobre `BigInt` ou
  com prova de que não passa de 2⁵³).

**As quatro regiões (M-4)** são faixas de `x`, sem parede, nas mesmas proporções do protótipo `mundo_fisico_vistas.html`:

| região | células em x | o que tem |
|---|---|---|
| casa | 0 a 15 | o ninho (4, 15) e o comedouro (10, 15) |
| jardim | 16 a 33 | 3 árvores |
| campo | 34 a 47 | espaço aberto; a bola começa em (40, 15) |
| mata | 48 a 63 | 6 árvores |

- **O pet nasce no ninho.**
- **A disposição é fixa** e fica em `ConfigMundo.layout`. Árvores, ninho, comedouro e o ponto inicial da bola são os mesmos em toda vida,
  no Python e na web.
- Os números desta seção e das seções 6 e 7 são **PROPOSTOS, sem fonte**. Os que o plano marca como calibráveis saem da calibração do
  mundo (plano, seção 6); o resto fica como está.

## 4. O que o dono faz: os eventos novos no log

- **`deixar_comida(tipo, x, y)`:** `Evento(tick, tipo="deixar_comida", valor="<tipo>|<x>|<y>")`, com `tipo` em `racao`, `a`, `b` ou `c`.
- **`deixar_bola(x, y)`:** `Evento(tick, tipo="deixar_bola", valor="<x>|<y>")`. Põe a bola num ponto, ou a muda de lugar. Há uma bola só.

**A posição já entra arredondada para a grade:** inteiros em subunidades, dentro do mapa. Na web, o ponto da tela vira o ponto do chão e é
arredondado (meio longe do zero, como `div_arred`) antes de gerar o evento. Posição fora do mapa, não inteira ou tipo desconhecido
levantam erro. O arrasto na tela não entra no log.

**Só o `reproduzir_mundo` entende os eventos novos.** O `reproduzir` de hoje levanta erro com eles, como já faz com qualquer tipo
desconhecido.

**Cuidado e orçamento:**
- o `deixar_comida` conta como contato, como o `alimentar` de hoje: zera o tempo sem cuidado, soma um cuidado e gasta uma interação do
  orçamento do dono. A fome **só sobe quando o pet come**;
- o `deixar_bola` segue a regra do `por_bola`: gasta orçamento e não é contato.

**Onde soltar é uma variável do cuidado** (`mundo_fisico.md`, seção 2.3). O embrulho `DonoComLugar` (no `mundo.py`) troca o `alimentar` do
dono sintético por `deixar_comida("racao", x, y)`, com o lugar dado pelo estilo:
- **comedouro:** o ponto do comedouro;
- **perto:** a posição do pet, mais um desvio de até 2 células;
- **longe:** um ponto entre 20 e 30 células do pet, numa direção sorteada, cortado para dentro do mapa.

Os sorteios do lugar saem de uma rng própria, `derivar_semente("dono-lugar", semente, rotulo_dono)`. **O braço não entra na semente:** P0 e
P1 sorteiam os mesmos desvios (números comuns).

## 5. O que o pet faz: a sub-decisão de alvo

**O cérebro escolhe o alvo; o motor anda** (`mundo_fisico.md`, seção 2.1).

**O deslocamento numa decisão:**
- **velocidade fixa:** `v` subunidades por tick. O alcance de uma decisão é `v × intervalo_decisao_ticks`;
- **o passo:** do ponto `p` ao alvo `t`, com `d = dist(p, t)`. Se `d ≤ alcance`, o pet chega em `t`. Senão, anda
  `p + (div_arred(dx × alcance, d), div_arred(dy × alcance, d))`, cortado para dentro do mapa;
- **o deslocamento é feito de uma vez, na decisão.** É o mesmo que andar `intervalo` ticks à velocidade `v`; a web interpola só para
  desenhar;
- **o gasto de energia:** `custo_energia_por_subunidade × deslocamento`. Soma-se ao efeito de sempre da ação (o `−0,015` do explorar, o
  `−0,02` do brincar);
- **o alvo pendente:** se o pet não chegou e a próxima decisão é a mesma ação, o alvo antigo vira o candidato `continuar`.

**As sub-decisões.** A cada decisão de explorar, comer ou brincar, o motor monta os candidatos e chama o gancho opcional do cérebro, no
mesmo padrão do `escolher_fruta` (LOBOS-MUNDO):

```
escolher_alvo(acao, candidatos, percepcao, u) -> Alvo | None
```

- **`u`:** um inteiro em [0, 2¹⁶) da rng própria `derivar_semente("alvo", semente)`. É sorteado **sempre** em explorar, comer e brincar,
  haja candidato ou não (números comuns, como a `rng_fruta`).
- **`None`:** vale o padrão do motor.
- **Um alvo fora dos candidatos** levanta erro. A exceção é o `ponto(x, y)` no explorar (um lugar lembrado), que só precisa estar dentro do
  mapa.

| ação | candidatos | padrão do motor (o que o instinto usa) |
|---|---|---|
| **comer** | cada comida vista (ração, madura ou podre); `cheiro` (1 célula × 8 na direção do cheiro), se há direção; `continuar` | a comida boa vista mais próxima (empate: `d`, depois o tipo, depois o id); sem ela, `cheiro`; sem cheiro, fica parado |
| **explorar** | `cheiro`; `vagar` (direção entre 16 e distância de 4 a 12 células, as duas tiradas do `u`); `casa` (o comedouro); `continuar`; `ponto(x, y)` vindo do cérebro | `continuar`, se há alvo pendente; senão `cheiro`, se o cheiro passa de `limiar_cheiro_explorar`; senão `vagar` |
| **brincar** | a bola, se vista; `continuar` | a bola vista; sem ela, brinca parado (o efeito de sempre, sem o bônus da bola) |

**O padrão nunca escolhe comida podre.** Só um cérebro pode escolher a podre pelo gancho. O que tenta o instinto fica para o item 3.

**O que acontece ao chegar** (raio de pegar: 1 célula):
- **comer:** come a comida do alvo;
- **explorar:** se a fome está abaixo de `fome_max_comer_achado` e há comida boa no raio de pegar, come a mais próxima, o "achou e comeu"
  (**decisão MF-1**);
- **brincar:** brinca com a bola. O humor sobe `ganho_humor_bola`, como na A1, e a bola rola (seção 6).

**O que cada comida faz:**

| comida | fome | humor | outro |
|---|---|---|---|
| ração | `+ganho_alimentar` (0,45, o de hoje) | — | a chance de sujeira de hoje (0,35), sorteada na rng do mundo |
| fruta madura | `+nutricao_fruta` (0,15: os 0,05 do comer mais os 0,10 do N4) | o efeito da fruta (o genoma do N4; no mundo "iguais", 0) | — |
| fruta ou ração podre | 0 | `efeito_podre` (−0,10, igual ao `efeito_humor_ruim`) | só por escolha de um cérebro |

**O comer de sempre:** fora do mundo, `comer` sobe a fome `+0,05` em qualquer lugar (`efeito_da_acao_do_pet`, `policy.py`). Isso já cobre
quatro vezes o decaimento da fome numa decisão (1/1200 × 15). Com a chave, **comer sem comida no alcance não dá fome**: o mundo desfaz o
`+0,05` antes de qualquer cérebro observar a transição (**decisão MF-2**).
- Sem isso, ficar parado comendo do nada vence qualquer busca, e o mundo não testa nada.
- **Se o A não conseguir desfazer sem tocar o `engine.py`, para e relata.** O `engine.py` não muda.

## 6. O que o mundo faz (a rng do mundo)

**Árvores.** O mundo avança em cada decisão:
- a cada passo de 15 min, cada árvore fora da recarga sorteia uma queda com probabilidade `p_queda` (jardim 1/96, mata 2/96: perto de uma e
  duas quedas por dia);
- uma queda derruba de 1 a 3 frutas, em pontos a até 2 células do tronco;
- cada árvore tem um tipo de fruta fixo no layout;
- o chão guarda no máximo 4 frutas por árvore; o excesso não cai, mas os sorteios acontecem do mesmo jeito;
- depois de uma queda, a árvore entra em recarga por `recarga_min` (720).

**Apodrecer.** Toda comida fica madura por um prazo (fruta 720 min, ração 1440 min), depois fica podre por `prazo_podre` (720) e então
some. A podre não tem cheiro de comida.

**A bola rola** depois de cada brincadeira:
- a direção é uma entre 16;
- a distância começa entre 3 e 10 células (no campo, o dobro) e perde `atrito` subunidades por tick até parar;
- o ponto final é cortado para dentro do mapa.

No mínimo, a bola não some nem reaparece; isso fica para depois.

**As rngs** (**decisão MF-4**). Todo sorteio do mundo vem do lado do ambiente, nunca da rng do pet, em fluxos próprios por
`derivar_semente`:
- `"mundo-arvores"`: as quedas e os pontos das frutas. Não depende do pet, então P0 e P1 veem as mesmas quedas;
- `"mundo-bola"`: as rolagens;
- `"mundo-sujeira"`: a sujeira da ração.

**O `_rng_ambiente` do engine não é tocado.** Sortear nele faria o comportamento do cérebro mudar o clima, e os braços deixariam de ser
comparáveis (o comentário do `engine.py` sobre as duas rngs).

## 7. O que o pet percebe, sem acesso privilegiado

Antes de cada decisão, o motor injeta a percepção num campo novo e opcional da `Observacao`, como fez com `bola` e `fruta`:
`mundo: PercepcaoMundo | None = None`. A `de_estado`, o bandit e as sondas não o leem.

| campo | o que é |
|---|---|
| `x`, `y` | a própria posição (**decisão MF-3**) |
| `regiao` | 0 casa, 1 jardim, 2 campo, 3 mata |
| `vistos` | os objetos a até `raio_visao` (6 células): `(id, tipo, dx, dy, d)` com a posição relativa, em ordem de `d`, tipo e id, no máximo 8 |
| `cheiro` | a soma, em inteiros, do cheiro de cada comida boa: `A_tipo × (R − d) // R` com `d < R` (ração `A` = 64, fruta 32; `R` = 24 células) |
| `direcao_cheiro` | 0 sem gradiente; 1 a 8 é a direção (L, NE, N, NO, O, SO, S, SE) em que o cheiro, medido a 1 célula, passa do centro. O maior vence; no empate, a ordem fixa |
| `alvo_pendente` | o tipo do alvo da decisão anterior que ficou sem chegar, ou nada |

- **O pet não recebe a lista de tudo** nem o que está fora do raio, a não ser como cheiro.
- **A soma direta é exata e barata** com poucos objetos (`mundo_fisico.md`, seção 2.5).
- **A podre não entra no cheiro,** mas aparece em `vistos`.

**Os campos de hoje.** Com o mundo, `bola`, `fruta`, `frutas_cenario`, `info_frutas` e `pedido_frutas` ficam no padrão. Os bônus da A1 e do
N4 no instinto não disparam; o instinto do mundo usa a percepção nova (seção 9). O cérebro que quiser ver o mundo lê `obs.mundo`.

## 8. A consequência chega a qualquer cérebro

A consequência de andar, comer e brincar é aplicada pelo motor depois da transição do engine, como o comer da fruta no N4. Para qualquer
cérebro ver o estado depois disso, o motor chama, uma vez por decisão de explorar, comer ou brincar, o gancho opcional:

```
consequencia_mundo(acao, ocorrido, obs_depois)
```

- **`ocorrido`:** o deslocamento, o alvo, se chegou, o que comeu e se brincou com a bola;
- **`obs_depois`:** a observação do estado depois de andar, comer e brincar;
- **quem não tem o gancho não vê nada de novo.**

O `fruta_comida` da E2 continua sendo chamado quando o pet come uma fruta, para os cérebros que já o usam.

**Critério (teste do mundo):** numa decisão em que o pet andou e comeu, o `obs_depois` tem a energia já descontada e a fome já somada.
Nenhum cérebro vê o `+0,05` desfeito (MF-2).

**O que o B ajusta nos cérebros** (seção 9): a checagem da E2 ("comer com fruta da decisão anterior ficou sem `fruta_comida`") assume que
comer com fruta no cenário sempre come. No mundo, comer pode só andar. Com a chave, o sinal da consequência dos cérebros que aprendem por ela
passa a esperar o `consequencia_mundo`.

## 9. Quem faz o quê (donos de arquivo)

| etapa | dono | arquivos | entrega |
|---|---|---|---|
| 1. gabaritos de hoje | **A** | `tests/gabaritos/mundo_vidas_de_hoje.json` | vidas de hoje (P0, P1, P3, nos mundos `padrao`, `bola`, `descasado`, `iguais_frutas`) gravadas **antes** de qualquer mudança, para o G2 |
| 2. o mundo | **A** | `digilab/mundo.py`, `ConfigMundo` em `config.py`, os eventos em `events.py` (só funções novas), o campo `mundo` da `Observacao` em `policy.py` (só o campo novo, com padrão), `tests/test_mundo.py` | seções 2 a 8; o `DonoComLugar`; o `reproduzir_mundo` |
| 3. o instinto e os cérebros | **B** | `PoliticaInstintoMundo` (subclasse do instinto, num arquivo do B), os ganchos nos cérebros, `tests/test_mundo_cerebros.py` | a regra da fome urgente; os pesos do tempo livre com o que vê; o modo `sem_explorar` do P0z (plano); o `consequencia_mundo` no A (e no B e no C, se forem para a bancada) |
| 4. a bancada | **D** | `experiments/bancada_v2.py`, `experiments/configs/v2_mundo/` | o mundo `fisico`; os braços e o acoplado do plano; as medidas do plano; o prefixo de unidades `"mundo"`; as faixas novas em `FAIXAS_RESERVADAS` |
| 5. a web (motor) | **A** | `web/app/src/motor/mundo.ts`, a paridade em `web/app/src/motor/__tests__/` | o motor do mundo em TS e a paridade; nenhuma tela |

**Ordem:** 1 → 2 → 3 e 5 em paralelo → 4. Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**

**O instinto do mundo (etapa 3, B):**
- **a fome urgente (`pedido_necessidade`):** com a chave, se a fome está abaixo de 0,25 e há comida boa vista ou cheiro (`cheiro > 0`), o
  pet escolhe **comer**. O padrão do motor o leva à comida vista mais próxima ou segue o cheiro. Sem nada disso, chama, como hoje. A
  higiene abaixo de 0,25 continua chamando;
- **a fome moderada:** igual a hoje (50/50 entre comer e chamar, a mesma chamada de rng);
- **o tempo livre:**
  - `comer` ganha `w_fruta × 1` com comida boa vista;
  - `brincar` ganha `w_bola × 1` com a bola vista;
  - os mesmos `w` calibrados do N4 e da A1, e a mesma chamada de `rng.choices`;
- **o modo `sem_explorar`:** o peso de `explorar` no tempo livre vai para `ocioso`. É o braço de controle do plano (P0z), não um pet do
  jogo.

**A regra que liga a percepção às entradas do cérebro A** é do B. O mundo não sabe que o A existe.

## 10. Gates

| gate | o que confere | onde |
|---|---|---|
| **G1** | toda vida com o mundo, rejogada do log, dá o mesmo estado, as mesmas posições e os mesmos objetos, bit a bit | `tests/test_mundo.py` e a bancada (toda vida) |
| **G2** | chave desligada = as vidas de hoje byte a byte, contra os gabaritos da etapa 1 | `tests/test_mundo.py` |
| **G-V1-V10** | os pets v1 a v10 iguais (os testes de reprodução da web e do Python que já existem passam sem mudança) | a suíte de sempre |
| **G-ENGINE** | `engine.py` com o sha256 de antes, sempre; `ambiente.py` e `frutas.py` sem mudança na etapa 2. Os cérebros (`lobos.py`, `cerebro_b.py`, `cerebro_c.py`) só mudam na etapa 3, atrás da chave, com o G2 | `tests/test_mundo.py` |
| **G-PAR** | paridade Python × TS: o deslocamento, a distância, o cheiro e a direção, os sorteios das árvores e da bola, e o `deixar_comida` e o `deixar_bola` no log dão os mesmos números em uma grade de casos e em 3 vidas inteiras gravadas | `web/app/src/motor/__tests__/mundo.test.ts` e o gabarito do Python |
| **G-MEC** | testes de mecanismo: comer sem comida não dá fome (MF-2); andar desconta a energia pela distância; o "achou e comeu" (MF-1); a fruta cai, apodrece e some nos prazos; a bola rola e para dentro do mapa; o `obs_depois` do `consequencia_mundo` já tem tudo aplicado; nenhuma rng do mundo toca o `_rng_ambiente` nem a rng do pet | `tests/test_mundo.py` |
| **G-NUMS** | P0 e P1 da mesma unidade veem as mesmas quedas de fruta (o fluxo `mundo-arvores` não depende do pet) | `tests/test_mundo.py` |

**Nenhuma run de pesquisa nesta tarefa.** Os testes usam só as sementes dos testes (101…505). As runs são do plano.

## 11. Decisões do Matheus

**DECIDIDAS em 2026-10-07: MF-1 a MF-4, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| MF-1 | No explorar, o pet come a comida que acha ao chegar ("achou e comeu")? | **sim**, com a fome abaixo de `fome_max_comer_achado` (0,85). Sem isso, com a janela imediata, o ganho de achar comida vai para o comer da decisão seguinte, e o explorar só registra o gasto | sem: o P1 não tem como ligar explorar à comida, e o teste mede o crédito, não o mundo. Com: comer e explorar se sobrepõem um pouco |
| MF-2 | Com o mundo, comer sem comida no alcance deixa de dar o `+0,05` de fome? | **sim**, desfeito pelo mundo antes de qualquer cérebro observar | sem: comer parado cobre 4 vezes a fome que se perde, e nenhuma busca compensa |
| MF-3 | O pet sabe a própria posição? | **sim:** sem ela, nenhum cérebro guarda "onde achei comida" nem volta para casa. Os objetos fora do raio continuam escondidos | sem: o explorar só pode seguir o cheiro ou vagar, e "um lugar que lembra" some da seção 2.2 |
| MF-4 | Os sorteios do mundo saem de fluxos próprios do lado do ambiente, e não do `_rng_ambiente` do engine? | **sim** (seção 6) | no `_rng_ambiente`: o comportamento do cérebro mudaria o clima, e P0 e P1 deixariam de ser comparáveis |

As decisões do plano (PMF-1 a PMF-7) estão no fim do plano.
