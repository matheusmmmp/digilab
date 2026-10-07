# Tarefa — V2: o banheiro, a necessidade no lugar certo e o limpador (W-TAREFA-BANHEIRO)

Status: **PROPOSTO**, escrito pelo coordenador em 2026-10-07 a pedido do Matheus. **Só papel.** O código vem em etapas depois do mundo
físico e do corpo (seção 9). Os números são **PROPOSTOS, sem fonte**.

**O pedido do Matheus (2026-10-07):**
- O pet faz as necessidades numa área do mapa, o **banheiro**.
- Quando ele faz no lugar certo e o jogador faz um **carinho**, medimos **quanto tempo ele demora para aprender** a fazer no banheiro.
- **Não há botão de elogiar.** "Elogio" no pedido quer dizer o carinho (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md` continua valendo).
- O jogador pode comprar um **limpador** que recolhe as necessidades, e ele **só funciona no banheiro**.

**A pergunta (para o plano):** com o carinho depois do banheiro, com o limpador, ou com os dois, em quantos dias o pet passa a fazer as
necessidades no banheiro? E quanto ele aprende sem nenhum dos dois?

**Por que o limpador importa para a pesquisa.** O limpador cria uma **consequência no corpo**, sem ninguém ensinar:
- no banheiro, a necessidade some na hora e o desconforto não sobe;
- fora do banheiro, ela fica no chão e o desconforto sobe.

Isso é o caminho que a decisão do produto escolheu: o pet aprende pela consequência. O carinho é o gesto do dono, e chega ao cérebro
pelo corpo (CD-4).

## 1. O que entra e o que fica fora

**Entra:**
- a região **banheiro** no mapa;
- o químico **`vontade`** (a vontade de fazer as necessidades), no corpo;
- a ação **`aliviar`** do pet, com a sub-decisão de onde (seção 4);
- a **necessidade** como objeto do mapa, com o desconforto de estar perto dela;
- o **limpador** do banheiro, como chave do mundo;
- o **dono que acaricia** depois de uma necessidade no banheiro;
- as medidas e os gates.

**Fica fora:**
- a loja, a moeda e a compra do limpador: no produto, quando a loja existir (como a aura do herói). Na pesquisa, o limpador é ligado ou
  desligado pela config;
- o "levar ao banheiro" e o aviso antes de sujar da educação-v1 (`educacao.py`). Eles continuam iguais nos pets e mundos de hoje e não
  se misturam com este banheiro (seção 2);
- a tela;
- uma versão de pet nova.

## 2. A chave e o lugar

- **A chave:** `ConfigBanheiro` no fim de `config.py`, desligada por padrão. Exige o mundo físico (`ConfigMundo.ligada`) e o corpo com os
  gestos (`ConfigCorpo.gestos`); sem eles, falha alto.
- **Com educação, lesões ou o aviso de higiene da educação-v1 ligados:** falha alto. O banheiro da educação-v1 é outra mecânica.
- **Chave desligada:** é a vida de hoje (do mundo e do corpo) byte a byte. Nenhuma rng nova, nenhum campo novo, nenhuma chave nova em
  `estado()`.
- **O motor:** a subclasse do `MotorCorpo`, ou o próprio `MotorMundo` com a chave, como o A decidir. `engine.py` não muda.

## 3. O banheiro, a vontade e a necessidade

**O banheiro.** Um retângulo dentro da casa, em `ConfigMundo.layout` (PROPOSTO: células x 0 a 3, y 0 a 5, longe do ninho e do comedouro).
É uma área, sem parede.

**A vontade** (químico novo, em C = 450000, na escala da `TAREFA_V2_CORPO_DRIVES.md`):
- **sobe** +150 por tick acordado (PROPOSTO: cheia em ~50 h sem comer);
- **e sobe com a comida:** a digestão (órgão 1) põe em `vontade` uma fração do `alimento` digerido (PROPOSTO: 1/3);
- **cai a 0** quando o pet faz as necessidades (`aliviar`);
- **dormindo**, não sobe;
- **receptor para o cérebro:** sim, na escala S, como os outros drives novos.

**O desconforto da vontade:** com a `vontade` acima de 0,75, o `desconforto` (o químico da higiene) sobe +150 por tick a mais (PROPOSTO).
É o que faz o pet querer aliviar.

**A necessidade no mapa.** Cada `aliviar` deixa um objeto `necessidade` na posição do pet, salvo quando o limpador o recolhe (abaixo).
- **Enquanto houver uma necessidade na mesma região do pet**, o `desconforto` sobe +100 por tick a mais por objeto, até 3 objetos
  (PROPOSTO).
- **Ao ser deixada**, a necessidade dá um aumento imediato de +22500 no `desconforto` (PROPOSTO: o "cheiro"). É a consequência imediata que
  a janela do sinal (seção 9 da tarefa do corpo) enxerga.
- **O dono limpa** com o `limpar` de hoje, que passa a recolher as necessidades da região do pet (com a chave). Sem limpar, ela fica.

**O limpador** (`ConfigBanheiro.limpador`, PROPOSTO desligado):
- recolhe **na hora** a necessidade deixada dentro do banheiro;
- **sem limpador**, a necessidade no banheiro fica no chão como qualquer outra;
- **fora do banheiro**, o limpador não faz nada.

**A consequência imediata de cada caso:**

| onde | sem limpador | com limpador |
|---|---|---|
| no banheiro | a vontade cai; +22500 de desconforto (o objeto fica) | a vontade cai; **sem** desconforto |
| fora | a vontade cai; +22500 de desconforto | a vontade cai; +22500 de desconforto |

Sem limpador, o lugar não muda a consequência imediata. A diferença que sobra é atrasada: o pet passa menos tempo no banheiro que na
casa. **Com limpador, o banheiro é melhor já na hora.**

## 4. O que o pet faz: `aliviar` e onde

**A ação.** `AcaoPet.ALIVIAR`, **no fim do enum**, só com a chave.
- Contraria a regra da tarefa do mundo ("`AcaoPet` não ganha membro"); é a decisão BN-1 (seção 10).
- A alternativa da BN-1 é o alívio involuntário, sem ação: o pet faz onde estiver quando a vontade passa de um limiar. Mas aí não há o que
  aprender sobre o lugar, a não ser por onde ele anda.

**A sub-decisão de onde**, como as sub-decisões de alvo do mundo:
- **alvo `banheiro`:** o motor leva o pet ao ponto mais próximo do banheiro, com o custo de energia da distância, e ele alivia lá. Se o
  banheiro estiver além do alcance de uma decisão, ele anda o que der e alivia **onde parou**: chegou tarde;
- **alvo `aqui`:** alivia onde está.

**O instinto** (`PoliticaInstintoBanheiro`, subclasse; dono: o B):
- **urgente:** com a `vontade` acima de 0,90, ele alivia, com o alvo sempre `aqui` (o acidente). É a regra urgente, que o pet não
  aprende;
- **moderada:** com a `vontade` acima de 0,50, `aliviar` entra no tempo livre com peso `w_vontade × vontade` (PROPOSTO, calibrável), na
  mesma chamada de `rng.choices`;
- **o alvo herdado:** `banheiro` com peso `w_banheiro_0` e `aqui` com peso S (PROPOSTO: `w_banheiro_0` = S/4, ou seja, o pet nasce
  preferindo `aqui` 4 a 1);
- **dormindo:** não alivia.

**O que se aprende.** Os pesos do alvo (`banheiro`, `aqui`) e o peso de `aliviar` no tempo livre, pela regra de cada cérebro. No cérebro A,
a regra da L1 com o sinal da consequência (P1) e, com os gestos, a mudança no corpo depois do carinho (CD-4).

## 5. O dono que acaricia

**`DonoCarinhoBanheiro`** (embrulho do A, sobre o `DonoComGestos` da tarefa do corpo):
- depois de cada `aliviar` **dentro do banheiro**, faz um `acariciar` no **primeiro passo do dono** depois do alívio (o momento do K4);
- **fora do orçamento**, pelo canal do mundo (como o julgamento do K4 fora do orçamento): os braços com e sem carinho têm o mesmo
  orçamento de cuidado;
- **o crédito:** o carinho chega ao cérebro só pelo corpo (CD-4), creditado à última decisão pela janela da v1. Com uma decisão a cada 15
  ticks, a última decisão antes do carinho é o `aliviar`. Um teste confere, como no K4;
- **fora do banheiro**, o dono não faz nada. Não há bronca nem tapa neste teste.

**O risco do carinho.** Pela tarefa do corpo, o carinho reduz a `solidao` e o `estresse`. Com a solidão baixa, ele quase não dá sinal: o
efeito depende do estado do pet. O plano mede a solidão no momento de cada carinho (seção 7).

## 6. O desenho do teste (para o plano)

**Quatro braços, 2 × 2**, todos com o mesmo dono de cuidado (o atencioso, com o `DonoComLugar` do mundo) e o cérebro A no ponto da K2, fonte
consequência (P1, montagem completa):

| braço | limpador | carinho depois do banheiro |
|---|---|---|
| B00 | não | não |
| B0C | não | sim |
| BL0 | sim | não |
| BLC | sim | sim |

- **O instinto:** o P0, com o aprendizado desligado, nos quatro braços (a referência de quanto o pet acerta sem aprender).
- **Contraste do carinho:** B0C − B00. **Contraste do limpador:** BL0 − B00. **A soma:** BLC contra os outros.
- **O tempo das vidas:** pelo menos 14 dias. A duração exata é do plano, pelo poder.

## 7. As medidas

- **A fração no banheiro:** dos alívios do dia, a fração dentro do banheiro, por dia.
- **O dia até o critério:** o primeiro dia em que a fração passa de 0,80 e fica acima nos 2 dias seguintes (PROPOSTO). Quem não chega
  fica censurado no fim da vida.
- **Os alívios até o critério**, além dos dias.
- **Os acidentes:** os alívios urgentes, por dia.
- **O cuidado preservado:** a privação e a saúde (como nos planos do corpo e do mundo).
- **O carinho:** quantos houve, e a solidão no momento de cada um.
- **O peso aprendido:** o do alvo `banheiro` contra o de `aqui`, no fim de cada dia.

## 8. Gates

| gate | o que confere |
|---|---|
| **G1** | toda vida com o banheiro, rejogada do log, bit a bit |
| **G2** | chave desligada = a vida do mundo e do corpo de hoje, byte a byte, contra gabaritos gravados antes |
| **G-MEC** | a vontade sobe e cai como a seção 3; o limpador recolhe só no banheiro; o objeto dá o desconforto da região; o `limpar` recolhe; o urgente alivia `aqui`; o alvo `banheiro` leva o pet até lá ou alivia onde parou |
| **G-CRED** | o carinho do `DonoCarinhoBanheiro` é creditado à decisão de `aliviar`, como no K4 |
| **G-CONS** | com limpador, o sinal imediato do `aliviar` no banheiro é maior que fora; sem limpador, igual |
| **G-PAR** | paridade Python × TS da vontade, do objeto, do limpador e do alvo |
| **G-ENGINE** | `engine.py` com o sha256 de antes |

**Nenhuma run de pesquisa nesta tarefa.** Os testes usam as sementes 101…505. As runs são do plano, com faixas novas.

## 9. Etapas e donos

| etapa | dono | o quê | depende de |
|---|---|---|---|
| 0 | **C** | `docs/PLANO_ANALISE_V2_BANHEIRO.md`, commitado antes de qualquer run | esta tarefa |
| 1 | **A** | gabaritos (o mundo e o corpo com a chave desligada) | o mundo (etapa 2) e o corpo (etapa 6) na main |
| 2 | **B** | a `vontade` no `corpo.py`; `AcaoPet.ALIVIAR`; o instinto; o alvo nos cérebros | a etapa 1 |
| 3 | **A** | o banheiro, o objeto, o limpador e o `limpar` no `MotorMundo`; o `DonoCarinhoBanheiro` | a etapa 2 |
| 4 | **A** | a web (motor) e o G-PAR | a etapa 3 |
| 5 | **D** | os braços B00 a BLC e as medidas na bancada | a etapa 3 |

Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**

## 10. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| BN-1 | `aliviar` como ação nova do pet (no fim do enum, só com a chave) | **sim**: sem a ação, o pet não decide onde, e não há o que aprender sobre o lugar | involuntário: o "aprender o banheiro" vira aprender por onde andar, com crédito muito atrasado |
| BN-2 | O carinho fora do orçamento do dono | **sim**, como o K4 | dentro: o braço com carinho tira cuidado do pet e mistura os dois efeitos |
| BN-3 | O desenho 2 × 2 (carinho × limpador) | **sim** | só o carinho: não se sabe se a consequência no corpo bastaria |
| BN-4 | O critério de "aprendeu": 0,80 por 3 dias seguidos | **sim**, PROPOSTO; o plano pode ajustar antes da run | critério frouxo: aprende por acaso; rígido: quase todos censurados |
| BN-5 | O limpador no produto como compra na loja, quando a loja existir | **sim**, registrado como IDEIA para o produto | — |
