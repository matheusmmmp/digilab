# Espec do P1: o gosto visual dentro do cérebro e do corpo químico

Status (2026-11-11): **PROPOSTO**. É a espec da integração pedida pelo Matheus depois de ver o P0 rodando: "quero que ele acesse o
cérebro para ter esses feedbacks e isso afetar de forma biológica e química". Só documento. **Nenhum código do P1 antes de o Matheus
revisar esta espec**, e nenhuma run antes do plano de análise. As decisões GV-15 a GV-23 (seção 10) são dele. A frente é a
`docs/TAREFA_V3_GOSTO_VISUAL.md`; a proposta, `docs/futuro/gosto_visual_pet.md`; o P0, o PR do `web/app/src/gostoVisual/`.

**Regras desta espec:**
- referências só as da nota do vault `BUSCA_GOSTO_VISUAL_2026-11-10.md` (as citadas na proposta) e as do projeto; todo o resto é **SEM
  FONTE**. Nenhuma referência sustenta um mapa do agrado visual em substâncias: **todo o mapa químico da seção 4 é desenho, SEM FONTE**;
- todo número novo é PROPOSTO e vai para o `digilab/config.py` com o status e a fonte (ou SEM FONTE);
- nenhuma alegação de novidade;
- vocabulário de estímulo, de receptor, de escolha e de medida: nada aqui diz que o pet sente prazer (F2, `docs/DEFINICOES_FRUTAS_V2.md`, 2.2);
- **a vida de hoje sai byte a byte igual com a chave desligada**, e o gabarito dela é gravado num commit próprio, antes da mudança (P1a);
- `digilab/engine.py` não muda; só biblioteca padrão no `digilab/`.

## 0. Em uma página

| peça | onde entra | o que já existe e serve de molde | o que é novo |
|---|---|---|---|
| **o estímulo** | o mundo: um objeto TV, com programas | os objetos do `MotorMundo`; o `estimulo_gosto` do paladar | a TV e os programas; o evento `sentido_tela` (só no modo livre) |
| **o sentido** | o corpo: um órgão da tela, com adaptação | o órgão da Audição (`ConfigOuvido`, DP-14: receptor por canal, adaptação que é a habituação) | sete canais (4 da visão, 3 do som) e os químicos de adaptação deles |
| **a química** | o corpo: emissores sobre químicos que já existem | o tédio, a curiosidade, o estresse, o susto e a tristeza (`corpo.py`, etapa 6) | só os emissores; nenhum químico de prazer (como a PL-1) |
| **a percepção** | o M-SENS | a habituação por classe (PE-11) e as linhas de objeto | a classe `tela` e a leitura dos receptores da tela |
| **o gosto inato** | o genoma | o `GenomaPaladar` (rng própria, fixo na vida, nunca aprendido) | o `GenomaVisao`: o ponto ótimo e a largura por canal |
| **o olhar** | o M-IMPULSO, o M-ARB e o M-PLAST | as unidades (b, o) e o sorteio; o P1 (o desfecho) e o P2 (o hábito) | o comportamento `olhar`, com uma unidade por TV vista |
| **a medida** | as sondas | a bateria da INDIVIDUALIDADE (cópia, rng própria, G2) | a sonda das duas TVs (GV-11) |

## 1. O estímulo: a TV do jogo e a tela real

### 1.1 Na pesquisa: só a TV do jogo

- **A TV é um objeto do mundo**, com posição, como o comedouro. Ela passa **programas**: cada um é um perfil de sete inteiros em [0, C]
  (cor, brilho, movimento, complexidade, volume, variação, timbre) e uma variação pequena dentro dele. É o análogo do perfil de gosto de
  cada tipo de comida (`docs/futuro/paladar.md`, 3.1).
- **A grade de programas é sorteada** por uma rng própria do mundo, `tv-programas`, derivada por `derivar_semente`. Trocar de política não
  muda a grade (RNG de ambiente e de política separadas).
- **Quem troca o canal** é o dono (um gesto novo `trocar_canal`, com o programa escolhido) ou a grade sozinha. As personas sintéticas da
  INDIVIDUALIDADE usam o gesto para mostrar coisas diferentes (seção 7).
- **A tela real nunca entra em resultado** (GV-20): ela é acaso real, e o `CLAUDE.md` só aceita o modo determinístico para resultado,
  protocolo com hash e paridade.

### 1.2 No jogo: a tela real pelo modo livre gravado

O conteúdo da tela é acaso real. Ele entra no log como evento, e o replay lê o evento (a exceção do modo livre gravado do `CLAUDE.md`,
como a `decisao_externa` de `digilab/events.py`, que hoje só leva um booleano).

- **O evento novo:** `sentido_tela`, com a fonte (`tela` ou `tv`) e os sete níveis. O motor usa, em cada tick, o último `sentido_tela` até
  aquele tick; sem nenhum, a TV está desligada. Um `sentido_tela` mal formado, ou num motor sem a chave, levanta erro.
- **O formato** (PROPOSTO): o valor em texto, `fonte|n1|…|n7`, com cada nível em 0 a 15 (16 níveis; o corpo multiplica por C/15). Um
  evento ocupa cerca de 74 bytes numa linha do `para_jsonl` (conferido com o `json.dumps` do formato, sem artefato).
- **A frequência** (GV-15): o P0 calcula um vetor por segundo real, mas o tempo do jogo anda, por padrão, a 10 minutos de jogo por segundo
  (`web/app/src/tempo.ts`), e a 1x um tick é um minuto real. Um evento por tick ou por segundo pesa demais no save do navegador:

| regra | eventos por hora real de tela | tamanho por hora (74 B por evento) |
|---|---|---|
| um por segundo real | 3 600 | ~266 KB |
| um por tick, a 1x | 60 | ~4,4 KB |
| um por tick, a 10 min/s | 36 000 | ~2,7 MB |
| **a média de 10 s reais, só quando algum nível muda** (a recomendação) | até 360; perto de 0 numa tela parada | **até ~27 KB** |

  O teto de 27 KB por hora deixa cerca de 185 horas de tela em 5 MB (o limite usual do `localStorage`), contra cerca de 19 horas com um
  evento por segundo. A conta do limite do navegador é de ordem de grandeza, SEM FONTE.
- **O P0 vira a fonte do evento:** ele já tem a captura, o vetor e o descarte do quadro (seção 14 da proposta). Só o que muda é que os
  sete níveis resumidos passam a entrar no log, e a tela do P0 mostra isso ao dono.

## 2. O sentido: um órgão da tela, com a habituação no corpo

O molde é o órgão da Audição (`ConfigOuvido`, DP-14, desligado hoje, e o Olfato): um receptor por canal, um químico de adaptação por
receptor, a adaptação andando para a intensidade com uma meia-vida, e a leitura `e = max(0, I − a − limiar)`, `r = div_arred(S e, e +
meia_saturacao)`. A habituação da literatura (Fantz 1964, `10.1126/science.146.3644.668`; Raz et al. 2025, `10.7554/elife.102713`) fica
assim dentro do corpo: **o interesse que se gasta e volta é a adaptação**.

- **A sub-chave nova:** `ConfigCorpo.tela` (só com o mundo físico), com uma `ConfigTela` própria, no molde da `ConfigOuvido`:
  `limiar`, `meia_saturacao`, `meia_vida_adaptacao`, `k_adaptacao`, `teto_intensidade`. Todos PROPOSTOS, SEM FONTE, no `config.py`.
- **Dois receptores por canal** (GV-18):
  - `tela_<canal>`, **o nível**: lê a intensidade I sem adaptação, como o `paladar_q` lê a concentração do sabor. É o que o gosto inato
    compara com o ponto ótimo (seção 5);
  - `novidade_tela`, **um receptor só**, com a soma das partes adaptadas `e` dos sete canais: alto quando a tela muda, perto de 0 quando o
    pet já se acostumou. É o que gasta o interesse.
- **O estímulo do tick:** o mundo entrega a intensidade de cada canal por `sentir`, só quando o pet está olhando (seção 6) e só a TV que ele
  olha. Sem olhar, I = 0 e a adaptação decai (o interesse volta). Como no Ouvido, o tick exige um `sentir` desde o tick anterior (falha
  alto).
- **Os químicos novos:** os sete `adaptacao_tela_<canal>` (concentração em [0, teto_intensidade]) e os sete níveis. Não há químico de
  prazer nem de gosto.

## 3. Por que o corpo e não só o cérebro

O P0 guarda o gosto todo num módulo do navegador. O pedido do Matheus é que o que o pet assiste **mude o corpo**, e que o corpo mude o
que o pet faz. No Digilab o cérebro só lê receptores (a G-RECEPTOR do M-SENS), e o aprendizado vem da consequência no corpo (o
`sinal_corpo`, o r_n). Por isso o caminho é: a tela mexe em químicos, os químicos mudam os receptores, e o M-AFETO e o M-PLAST aprendem
com essa mudança, como já aprendem com a comida e a bola.

## 4. A química: o que olhar a tela mexe no corpo

**Só químicos que já existem** (`digilab/corpo.py`, etapa 6, e a tristeza do Sistema neuroquímico). O que é novo são os emissores, cada um
atrás da sub-chave `tela` e com o seu número PROPOSTO, SEM FONTE. **Nenhuma fonte da nota sustenta este mapa:** é desenho.

| o que acontece | o químico que já existe | o emissor novo (PROPOSTO, SEM FONTE) | o molde no código de hoje | decisão |
|---|---|---|---|---|
| olhar a tela | o **tédio** cai | `atividade("assistir")`, com a redução pela variedade recente (DS-4) | o `atividade(nome)` da bola, do brincar e do explorar | GV-21 |
| a tela traz algo novo | a **curiosidade** cai | `estimulo_novidade(n)` quando o `novidade_tela` passa de um corte, até o teto de hoje (2) | o `estimulo_novidade` do mundo físico | GV-23 |
| o pet olha algo perto do ponto ótimo dele (o agrado alto) | a **tristeza** cai (o humor sobe) | um ganho de humor proporcional ao agrado, como o `estimulo_bola(ganho_humor)` | o humor da bola e da fruta | GV-16 |
| som alto ou movimento demais por muito tempo | o **estresse** sobe | acima de um corte alto de `volume` ou de `movimento`, por tick olhando | o estresse dos drives (etapa 6) | GV-17 |
| um salto brusco de volume (um estouro) | o **susto** sobe | quando o `volume` sobe mais que um salto entre dois ticks | o susto do tapa (meia-vida 30) | GV-17 |
| o enjoo (o pet já se acostumou) | nada sobe | o `novidade_tela` cai pela adaptação, e o tédio volta a subir porque a redução pela variedade some | a variedade do tédio (DS-4) | — |
| assistir junto com o dono | a **solidão** cairia | **fora da primeira versão** | o carinho na solidão | GV-22 |

- **O agrado na tristeza difere do paladar.** No paladar, a PL-1 decidiu que não há químico de prazer e que o gosto entra só no sinal do
  cérebro. Aqui a recomendação mantém "nenhum químico novo de prazer", mas usa o humor que a bola e a fruta já movem (GV-16). Isso é uma
  escolha do Matheus: se ele preferir a forma do paladar, o agrado vai só para o sinal (seção 5.2) e a tristeza fica de fora.
- **O estresse e o susto entram na excitação** do M-AFETO (`EXCITANTES = dor, susto, estresse`). Assim um programa barulhento demais
  aumenta a excitação e o `g_apr` sem nenhuma peça nova no cérebro.
- **A tela não mexe na fome, na energia, na higiene nem na saúde.** O gasto basal continua o de hoje (olhar é parado; o metabolismo trata
  como ocioso).

## 5. O gosto: inato no genoma, aprendido pela exposição e pela consequência

### 5.1 O inato: o `GenomaVisao`

No molde do `digilab/genoma_paladar.py`:
- **por canal k**, o ponto ótimo `o_k` em [0, C] e a largura `l_k`, sorteados por pet, uniformes e independentes, com a rng própria
  `visao-ovo`, derivada da semente do ovo. Ela não toca o temperamento, o `GenomaFrutas` nem o `GenomaPaladar`;
- **o agrado inato** do nível de agora é um pico em inteiros: `A = Σ_k pico(n_k − o_k, l_k) / 7`, com o `pico` em degraus inteiros (a
  forma exata na implementação, PROPOSTA). O apoio para o pico: Yanagisawa 2021 (`10.3389/fncom.2021.698252`) e Kidd et al. 2012
  (`10.1371/journal.pone.0036399`); a cautela: Van Geert e Wagemans 2020 (`10.1037/aca0000224`);
- **fixo na vida, nunca aprendido, nunca herdado o aprendido** (DEFINICOES_FRUTAS_V2, 2.4). Com a herança do genoma da linhagem, o
  `GenomaVisao` segue a regra das outras seções. O genoma vazio (todos os pets com o mesmo ótimo no meio) é o controle.

### 5.2 Onde o agrado entra

- **No sinal do cérebro**, como o canal `gosto` do paladar: um termo `gosto_visual` no `sinal_corpo` do M-AFETO, com o agrado do que o
  pet olhou na opção. Ele dá o r_n e, por ele, o P2 aprende o hábito de olhar.
- **No corpo**, só se a GV-16 decidir: o ganho de humor da seção 4.

### 5.3 O aprendido: três partes, separadas

| parte | onde fica | como anda | o que se lê no painel |
|---|---|---|---|
| **a exposição** (Zajonc 1968, `10.1037/h0025848`) | um estado novo do M-SENS: o alvo aprendido por canal, que anda devagar para o nível visto | só olhando; com um teto, como no P0 | o deslocamento do alvo |
| **a consequência** (Provenza 1995, `10.2307/4002498`; Yearsley et al. 2006, `10.2307/3844777`) | o P1 do M-PLAST: o desfecho `d[tela, r]`, o quanto olhar muda cada receptor | o `Delta_r` de cada opção de olhar, como o comer | o "olhar me faz bem" (o incentivo G da classe `tela`) |
| **o hábito** | o P2 do M-PLAST: a linha `H[olhar, j]` | o r_n das opções de olhar (o crédito por opção, PE-3) | quando ele costuma olhar |

O carinho do dono durante a exibição, que no P0 puxava o gosto, aqui é a consequência de verdade: o carinho mexe na solidão, no estresse e
no conforto (`corpo.py`), e o P1 credita essa mudança à classe `tela` se o pet estava olhando. **SEM FONTE** para a mesma associação com
imagens num agente.

## 6. O olhar: um comportamento que o M-ARB escolhe e o M-PLAST reforça

- **O comportamento novo `olhar`** (GV-19), atrás da sub-chave `olhar` da `ConfigDigibrain`: entra em `COMPORTAMENTOS_DIGIBRAIN` só com
  ela, no fim da lista, para a ordem das unidades de hoje não mudar. É uma ação nova do pet no mundo (`AcaoPet`), como as da
  `docs/TAREFA_V3_ACOES_NOVAS.md`, e o `MotorMundo` a executa: o pet vai até perto da TV e fica.
- **As unidades:** uma por TV vista (a classe `tela` nos `vistos` do M-SENS), com a proximidade e a novidade da linha de objeto. O inato do
  `olhar` (`W0`) lê a urgência do tédio e da curiosidade e a novidade da linha; o incentivo é o G da classe `tela` (P1); o hábito é o
  `H[olhar, j]` (P2).
- **O sorteio** é o do M-ARB de hoje, com a mesma rng de política. As sondas "quem decidiu" valem para o `olhar` sem mudança.
- **O fim da opção:** o pet para de olhar quando o sorteio da decisão seguinte escolhe outra coisa. Com o `novidade_tela` caindo, a
  curiosidade e o tédio sobem, e a ativação do `olhar` cai: é o enjoo, sem regra nova.
- **A M-SENS hoje falha alto com um receptor de órgão presente.** O P1d abre essa porta só para os receptores da tela, com a chave.

## 7. O gosto como traço: as sondas da INDIVIDUALIDADE

- **A sonda das duas TVs** (GV-11: sonda própria desta frente, com a maquinaria das de `experiments/sondas_individualidade.py`): numa
  cópia do pet num tick, duas TVs com dois programas que o dono **nunca** mostrou, a posição sorteada por rng própria. Lê-se a **escolha**
  (qual o pet olha primeiro) e o **tempo relativo olhando**, em separado (GV-5; Gustafsson et al. 2021, `10.3758/s13420-021-00484-3`;
  Pfefferle et al. 2025, `10.3758/s13428-025-02668-5`).
- **Só depois da familiarização** (GV-6; Hirskyj-Douglas e Webber 2021, `10.1145/3493842.3493893`).
- **O desenho genoma × dono:** clones com donos que mostram programas diferentes dão a parte do dono (a exposição e a consequência);
  genomas diferentes com o mesmo dono dão a parte do genoma; o genoma vazio é o controle (`docs/futuro/individualidade_pet.md`, seção 4).

## 8. As regras de mudança e os gabaritos

- **Cada peça atrás da sua chave, todas desligadas:** `ConfigCorpo.tela`, a `ConfigTela`, `ConfigMundo.tv`, `ConfigDigibrain.olhar`, o
  `GenomaVisao` (vazio quando desligado). Desligadas, a vida de hoje sai byte a byte, no Python e no web.
- **O gabarito das vidas de hoje** num commit próprio, antes de qualquer mudança (P1a): as vidas do modular e do A nas sementes dos testes
  (101…505), com o log e o estado final, e um teste que as confere.
- **O evento novo** (`sentido_tela`) num replay sem a chave levanta erro, e um evento de tipo desconhecido continua levantando erro.
- **A paridade com o web** (P1f): os gabaritos saem de um exportador `experiments/exportar_gosto_visual.py`, com a TV do jogo; o motor TS
  confere bit a bit no Node. A tela real entra no web só pelo evento, que é o mesmo nos dois.

## 9. As etapas

| etapa | o quê | depende de | entrega |
|---|---|---|---|
| **P1a** | o gabarito das vidas de hoje, num commit próprio, e o teste que o confere | esta espec revisada | PR próprio |
| **P1b** | o corpo: a `ConfigTela`, o órgão da tela (os receptores e a adaptação) e os emissores da seção 4, atrás de `ConfigCorpo.tela`; o G-HOJE byte a byte | P1a | código e testes |
| **P1c** | o mundo: a TV, a grade de programas (`tv-programas`), o gesto `trocar_canal` e o evento `sentido_tela` | P1b | código e testes |
| **P1d** | o cérebro: o M-SENS (a classe `tela`, os receptores, o alvo aprendido), o `GenomaVisao`, o comportamento `olhar` (M-IMPULSO, M-ARB, M-PLAST) e o canal `gosto_visual` | P1c | código e testes |
| **P1e** | a sonda das duas TVs (só leitura, G2 byte a byte), o `docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md` commitado antes da primeira vida, a faixa pedida ao coordenador; depois, a run descritiva genoma × dono e o `RESULTADO_V3_GOSTO_VISUAL.md` | P1d | plano, run, resultado |
| **P1f** | o web: o motor TS com paridade; o P0 passa a gravar o `sentido_tela` (o modo livre) e o painel lê o cérebro em vez do módulo próprio | P1d (a paridade); P1e não bloqueia | código e testes |

Na ordem da proposta: o P1a a P1d são o GV1; o P1e, o GV2 e o GV3; o P1f, o GV4 e o GV5. **O plano de análise vem antes de qualquer
vida**, com a familiarização, os perfis dos programas da sonda e a regra para uma sonda sem variância escritos nele.

## 10. As decisões do Matheus (todas PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GV-15** | Com que frequência o vetor da tela real entra no log. | **A média de 10 s reais, em 16 níveis por canal, só quando algum nível muda**: até ~27 KB por hora de tela. | Um evento por segundo enche o save do navegador em cerca de 19 horas de tela; um por tick, a 10 min/s, em menos de duas. Resumir demais (um por minuto) deixa o pet cego aos cortes de cena e aos estouros de som. |
| **GV-16** | Se o agrado mexe no corpo (a tristeza) ou só no sinal do cérebro. | **Os dois, cada um atrás da sua sub-chave**: o canal `gosto_visual` no sinal (como o paladar) e um ganho pequeno de humor (o caminho da bola e da fruta). Nenhum químico novo de prazer. | Só no sinal, a tela não "afeta o corpo", que é o pedido. Só no corpo, o agrado se mistura com o humor que a comida e a bola movem e fica difícil separar na medida. As sub-chaves deixam testar um sem o outro. |
| **GV-17** | O som alto e o movimento demais como estressores. | **Sim: o estresse por tick acima de um corte alto, e o susto só num salto brusco de volume.** | Sem isso, o pet "gosta" de qualquer barulho que estiver perto do ponto ótimo dele. Com cortes baixos demais, qualquer clipe estressa o pet e a TV vira castigo. SEM FONTE para os cortes. |
| **GV-18** | Onde fica a habituação: no corpo (um órgão com adaptação) ou no M-SENS. | **No corpo, no molde do Ouvido**, com o nível por canal e um receptor `novidade_tela`; o M-SENS só lê. | Na M-SENS, a habituação não vira química e o "efeito biológico" pedido fica só no cérebro. No corpo, são 14 químicos novos (os 7 níveis e as 7 adaptações) e o custo do tick sobe. |
| **GV-19** | O olhar como comportamento novo ou como unidade dentro do `explorar`. | **Comportamento novo `olhar`, no fim da lista, atrás da sub-chave.** | Dentro do `explorar`, o hábito de olhar se mistura com o de vagar e o P2 não separa os dois. Como comportamento novo, as tabelas do modular (W0, H) ganham uma linha, e o web precisa de paridade nela. |
| **GV-20** | O que o pet vê na pesquisa. | **Só a TV do jogo.** A tela real só no jogo, pelo modo livre gravado, e nunca em resultado. | Com a tela real numa run, o resultado não é reproduzível, e o `CLAUDE.md` não o aceita. |
| **GV-21** | Olhar a tela tira tédio. | **Sim, como uma atividade (`assistir`), com a redução pela variedade de hoje (DS-4).** | Sem isso, o tédio não puxa o pet para a TV e o enjoo não tem efeito no corpo. Com uma redução forte, a TV vira a melhor atividade e o pet para de brincar e explorar. |
| **GV-22** | Assistir junto com o dono tira solidão. | **Fora da primeira versão.** | Com ela, a parte do dono no traço mistura a companhia com a exposição, e o desenho genoma × dono perde a leitura. Sem ela, "passar tempo com o usuário" fica só no P0. |
| **GV-23** | A novidade da tela tira curiosidade. | **Sim, pelo `estimulo_novidade` de hoje, com o mesmo teto.** | Sem isso, a curiosidade não liga a tela ao corpo. Com um corte baixo, todo corte de cena conta como novidade, e a curiosidade nunca sobe. |

As GV-1 a GV-14 da proposta seguem valendo. Esta espec segue as recomendações delas (a TV do jogo primeiro, o gosto do pet, a parte inata
no genoma numa seção própria, a medida em duas partes, a familiarização, o pico, a consequência pelo canal do corpo e a sonda própria).

## 11. Riscos

- **O mapa químico é desenho, não ciência.** Mitigação: todo emissor é SEM FONTE, atrás de sub-chave, e a run descritiva mostra o que cada
  um faz antes de qualquer leitura.
- **A TV virar o melhor lugar do mundo.** Mitigação: a adaptação, a variedade do tédio e o estresse do excesso; a run mede o tempo total
  olhando como efeito colateral.
- **O save do navegador encher.** Mitigação: a GV-15.
- **O custo do tick e do replay.** Mitigação: o P1b mede o custo do órgão antes do plano.
- **A paridade em uma ação nova.** Mitigação: o P1f só depois do P1d estável, com os gabaritos do exportador.
