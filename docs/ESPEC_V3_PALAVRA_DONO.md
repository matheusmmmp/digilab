# Espec: o dono inventa uma palavra e o pet aprende (F4, 2026-11-17)

**Status:** **APROVADO pelo Matheus em 2026-11-17**, no chat da sessão F4. D-PD-1 a D-PD-4 (os conflitos de partida, seção 2) e D-PD-5 a
D-PD-9 (a prancha, a espec e o teste, seção 8) foram todas decididas pela recomendação. O código começa pela PD1, depois da LZ2a e da etapa 2 do
`TAREFA_V3_ELOGIO`. Todos os números são **PROPOSTOS, SEM FONTE**. Eles se acertam na rodada de equilíbrio do fim, e esta frente não calibra
nada.

**Origem:** a frente F4 do prompt das cinco frentes (vault, `30 Decisões e protocolo/PROMPT_CINCO_FRENTES_2026-11-16.md`), que nasceu do
PacaPet (Karati e Kluver 2026, WOCHAT, `10.21437/WoChat.2026-2`, lido em texto completo; vault, `CONFERENCIA_REFS_FALA_LLM_2026-11-16.md`).

**A prancha:** [`docs/pranchas/ux-palavra-dono/`](pranchas/ux-palavra-dono/LEIA.md).

## 0. Em uma página

- **O que o dono faz:** no arco do pet, escolhe **Dizer…**, digita uma palavra ("zorp") e confirma. A palavra vira um evento no registro
  (`pl`), com o tick e o texto normalizado.
- **O que o pet percebe:** uma característica nova do contexto z, a "palavra ouvida", ligada por uma janela curta depois do evento. Ela
  entra em todos os comportamentos pelo hábito `H[b, j]`, como a "noite" ou a "fome sem comida". O inato não conhece palavra nenhuma: o
  `W⁰` dela é 0, e o pet nasce sem ligar palavra a nada.
- **Como ele aprende:** pela regra P2 do M-PLAST, **sem mudança**. Se o pet fez b com a palavra no ar e o corpo melhorou, `H[b, palavra]`
  sobe. O elogio pesa só pela mudança que faz no corpo, pela rota da D-EL-2. Não há sinal novo (D-PD-1).
- **O corpo vence:** com alguma urgência crua acima do limiar (`alguma_urgencia_critica`, o predicado da F3), a palavra fica fora daquela
  decisão. Ela não puxa e não ganha elegibilidade.
- **O que o pet mostra:** quando uma ligação passa de um limiar, um cartão diz uma vez "Growlmon liga 'zorp' a brincar", e o painel de
  hábitos (WD-1, só leitura) lista as palavras com a força de cada ligação. **Nunca "entende"** (D-PD-2).
- **Onde nasce:** no Python, atrás de uma subchave desligada, com paridade no TS (D-PD-4). A voz vem depois e gera o mesmo evento (D-PD-3).
- **O teste:** um dono coerente contra um dono inconsistente, com o mesmo número de palavras e de carinhos. A medida é uma sonda
  contrafactual sem rng nova: a chance do comportamento com a palavra contra sem ela, no mesmo estado (seção 6).

## 1. O que existe hoje (conferido na `main` em 2026-11-17, `a794c3ae`)

| peça | onde | o que pesa aqui |
|---|---|---|
| o contexto z, com ~20 características que entram em todos os comportamentos | `digilab/config.py` (`CARACTERISTICAS_DIGIBRAIN`); `digilab/digibrain/impulso.py` (`contexto_z`) | a palavra é mais uma entrada de z, e só com a subchave (outra tupla, como a `COMPORTAMENTOS_DIGIBRAIN_OLHAR`) |
| o hábito P2: `H[b*,j] ← clamp(H[b*,j] + g_apr·η_h·r_n·e_j, ±H_max)`, com a elegibilidade da decisão que começou a opção | `digilab/digibrain/plast.py`; espec do modular, seção 2.4 | a regra que liga a palavra, sem mudança |
| a urgência convexa, `u = a·falta + b·max(0, falta − λ)`, com λ por receptor | `digilab/digibrain/afeto.py:97` | o joelho λ é a porta "o corpo vence" |
| o crédito do carinho pelo corpo, logo depois da ação | `docs/TAREFA_V3_ELOGIO.md` (D-EL-1 a D-EL-8 DECIDIDAS em 2026-11-16; o código vem depois da LZ2a) | a única rota do elogio até a palavra |
| o arco de comandos fixo e o pedido como percepção | `docs/PLANO_V3_INTERACAO.md` (EN-1, EN-4, EN-5, EN-9; WD-4) | o "Dizer…" mora no arco, ao lado dos pedidos |
| o painel de hábitos, só leitura | `docs/PLANO_V3_INTERACAO.md`, WD-1 | as palavras aprendidas entram nele |
| "não afirma que o pet entende o que o dono diz" | `docs/PLANO_ANALISE_V3_CONVERSA_DC5.md`, cabeçalho | continua valendo (D-PD-2) |
| o arco do pet no jogo | ainda não existe: é a IT3 (vista) | a vista desta frente depende da IT3 |

**Do PacaPet (texto completo; o que a fonte afirma):** a frase livre do usuário só vira gatilho depois de aparecer várias vezes no mesmo
contexto, com confiança e uma checagem de compatibilidade. Um estado crítico do corpo vence a dica, e com ensino contraditório só 2 de 7
dicas disparam. **Leitura do DigiLab:** o PacaPet guarda isso numa memória de dicas à parte. Aqui a mesma ideia passa pela rede do pet
(seção 3.7).

## 2. As decisões de partida (DECIDIDAS pelo Matheus, 2026-11-17, no chat da sessão F4)

As perguntas foram levadas com a recomendação e o custo de errar. As respostas estão literais (a opção escolhida, que é a recomendada em
todas).

| # | a pergunta | a resposta do Matheus | o que fica |
|---|---|---|---|
| D-PD-1 | "D-PD-1: qual sinal ensina a palavra ao pet?" (a regra: o gesto do dono não treina o pet) | **"Corpo pelo hábito (Recomendado)"** | a palavra é uma característica de z e aprende pelo H do P2 com o r do corpo; o elogio só pela rota da D-EL |
| D-PD-2 | "D-PD-2: como fica a frase da DC5 'não afirma que o pet entende o dono'?" | **"Mantém, só associação (Recomendado)"** | a mecânica afirma só uma associação medida; a tela diz "liga 'zorp' a cavar"; a voz não diz que entendeu |
| D-PD-3 | "D-PD-3: de onde vem a palavra?" | **"Texto agora, voz depois (Recomendado)"** | texto normalizado vira evento; a voz, numa etapa futura, gera o mesmo evento pela transcrição gravada |
| D-PD-4 | "D-PD-4: onde a mecânica nasce?" (um conflito que a sessão achou: a EN-4 põe o pedido só no TS) | **"Python + paridade TS (Recomendado)"** | nasce em `digilab/`, com o teste na bancada e o espelho TS bit a bit; a IT6, o pedido fixo, continua só TS |

**Os custos que foram ao Matheus, para o registro:**
- **D-PD-1:** um elogio como sinal direto quebraria a regra e reabriria a pergunta do dono, que está encerrada. Só pelo corpo, a palavra
  pode aprender devagar, e isso se mede (seção 6), sem calibrar.
- **D-PD-2:** escrever "entende" na tela prometeria uma compreensão que a rede não tem e contradiria a DC5.
- **D-PD-3:** com a voz já no começo, o ditado erra ("patch" por pet) e uma mesma palavra vira duas. O dono passa a parecer inconsistente
  e o teste fica sujo.
- **D-PD-4:** só no TS, não haveria teste com braço de controle.

## 3. O desenho

### 3.1 O evento `pl` (a palavra dita)

- **A forma no registro:** `{"t": "pl", "k": <tick>, "p": "<texto normalizado>"}`. O nome `pl` está PROPOSTO. Se estiver tomado no registro
  do jogo, troca na etapa de código, e o nome final vai ao Matheus junto do gabarito.
- **A normalização é determinística e fica na tela, antes de gravar:**
  1. NFKD, sem os diacríticos;
  2. minúsculas;
  3. só `a-z`, `0-9` e o espaço;
  4. espaços colapsados e cortados nas pontas;
  5. de 1 a 24 caracteres (PROPOSTO).
- **No replay, falhar alto:** um `p` fora da norma levanta erro, e não se normaliza de novo. O motor confia só no que está gravado.
- **Um por vez (EN-5):** uma palavra nova substitui a que estava no ar e não se empilha.

### 3.2 O vocabulário: K vagas

- **K = 4 vagas por pet** (PROPOSTO, SEM FONTE; D-PD-7). A vaga é dada na ordem em que a palavra aparece pela primeira vez no registro, e por
  isso o replay a refaz.
- **Com as vagas cheias,** a tela não aceita uma palavra nova e diz: "Ele já guarda 4 palavras." Esquecer uma palavra (decaimento do H)
  fica fora: é a PE-10 do modular, ainda aberta.
- **Por que vagas fixas:** o z tem tamanho fixo, e a ordem das características não muda dentro de uma versão. Com vagas, `H` cresce de
  7 × 20 para 7 × 24, e o resto do cérebro não muda.

### 3.3 A percepção (M-SENS)

- **A população nova "palavra ouvida"** (só com a subchave): `ouvida_k = S` durante `W_p` ticks depois do evento `pl` da vaga k, e 0 fora
  dessa janela. `W_p` é a janela do pedido (EN-5, PROPOSTO: alguns minutos de pet), e a forma é um degrau, sem queda gradual (PROPOSTO).
- **No z:** `CARACTERISTICAS_DIGIBRAIN_PALAVRA = CARACTERISTICAS_DIGIBRAIN + ("pal_0", …, "pal_{K−1}")`, no fim. Com isso a ordem das
  características de hoje não muda.
- **O inato:** `W⁰[b, pal_k] = 0` para todo b. Uma palavra nunca puxa nada por nascença.

### 3.4 A porta "o corpo vence"

- **A regra:** se `alguma_urgencia_critica(urgencias)` é verdadeira, então `pal_k = 0` em z naquela decisão, para todo k. É o predicado da
  F3 (`docs/ESPEC_V3_URGENCIAS.md`, seção 6.2, PR #958): `urgencias[r] > urgencia_lambda` sobre as urgências **cruas** do M-AFETO. É o
  mesmo teste das guardas de hoje (`arb.py`, `estado.py:142`, `adapt.py:345`). A guarda compara a **urgência** com o limiar, e não a falta:
  com os inatos padrão, a urgência passa do limiar com a falta acima de 640, e na v38 e na v39, acima de 800 (números da F3).
- **Efeito no aprendizado:** como a elegibilidade é `e_j = z_j`, a palavra também não ganha crédito numa decisão dessas. O pet com fome
  crítica não aprende "zorp" comendo.
- **Ligação com a F3:** a D-UR-8 da F3 (decidida pelo Matheus no chat da F3 em 2026-11-17) diz que a palavra não passa pela prioridade da
  F3, e que o "corpo vence" é uma guarda própria sobre esse predicado. A primeira versão desta espec dizia "falta acima de λ". A correção
  para a urgência acima do limiar segue o texto da tarefa ("urgência acima de λ ignora a palavra") e as guardas de hoje. Está registrada no
  registro do mês. **A palavra não é um impulso:**
  não entra na urgência nem no sinal do corpo, e por isso a F4 não depende de uma decisão da F3.

### 3.5 O aprendizado (D-PD-1): a P2 sem mudança

`H[b*, pal_k] ← clamp(H[b*, pal_k] + mul(mul(g_apr, η_h), mul(r_n, e_pal_k)), −H_max, H_max)`

- É a linha da P2 de hoje, só com as colunas novas. O `r_n` é o sinal homeostático da opção. Com a D-EL ligada, o carinho dentro da janela
  soma a ele pela rota da D-EL-2.
- **O que isso ensina:** a palavra se liga ao que melhorou o corpo quando ela estava no ar.
  - Um dono que diz "zorp" quando o pet está entediado com a bola perto, e faz carinho quando ele brinca, liga "zorp" a brincar.
  - Um dono que diz "zorp" para o pet comer sem fome não liga nada. A comida não alivia o corpo, e nada credita.
- **O que isso não ensina (o custo assumido da D-PD-1):** uma palavra para uma ação sem efeito no corpo ("Senta", quando existir) só se
  liga pelo carinho, pela D-EL. Sem a D-EL, ela não se liga. Isso é o mecanismo, não um defeito a calibrar.
- **Dizer muitas vezes não é funcionar.** O GARP mostra o risco de a repetição pesar demais (quatro notas quase iguais venceram uma
  diferente; vault, `LEITURA_GARP_2026-11-17.md`). Aqui ele não aparece por três razões:
  - a palavra só muda o H quando o corpo responde (`r_n ≠ 0`), e dizer sem consequência não soma nada;
  - repetir dentro da janela `W_p` não empilha (EN-5): é uma elegibilidade por opção, e não uma por vez que o dono disse;
  - o braço S do teste (6.1) separa a exposição da contingência.

  O que conta é quantas vezes a palavra esteve no ar quando o corpo melhorou.
- **A sutileza que o teste mede:** a P2 não tem competição entre as colunas, como teria uma regra delta. A palavra e o contexto ganham
  crédito juntos. Um dono que diz "zorp" sempre no mesmo contexto ensina "zorp" e ensina o contexto. Só a sonda fora desse contexto
  (seção 6.3) separa os dois.

### 3.6 O alvo: (comportamento, alvo)

O H é por comportamento: "zorp" puxa brincar, e não brincar com aquela bola. O alvo continua escolhido pelos termos de hoje (a proximidade,
o incentivo G).

**Para a palavra puxar o alvo (atrás de uma segunda subchave, desligada; D-PD-6):**
- uma tabela `Hα[k, t]`, de K × |TIPOS_ALVO_DIGIBRAIN| (4 × 9);
- ela aprende pela mesma regra de três fatores, na consequência: `Hα[k, tipo(o*)] += g_apr·η_h·r_n·e_pal_k`, só no tipo do alvo escolhido;
- ela entra na ativação de toda unidade com alvo do tipo t como o termo `palavra_alvo = Σ_k mul(Hα[k, t], pal_k)`, guardado à parte para
  a sonda.

**RECOMENDAÇÃO:** começar só com o comportamento. O alvo multiplica os parâmetros por 9, e testá-lo pede um mundo com dois alvos do mesmo
comportamento ("zorp" é a fruta a e não a b). Esse é um segundo teste, depois do primeiro.

### 3.7 Por que a rede e não a tabela de contagem do PacaPet

A tarefa pede para dizer por que, ou mostrar que a tabela basta.

1. **A tabela não pesa o corpo.** Ela aprende o ensino ruim tanto quanto o bom, e isso contraria a D-PD-1.
2. **A tabela dispara como uma regra que corta.** Quando "zorp" passa do limiar, o pet faz X. Isso é o que o modular tirou do A ("nenhuma
   regra decide quais ações concorrem", seção 8.2 da espec do modular). Aqui a palavra só soma à ativação, e a fome, o sono e a bola
   continuam concorrendo.
3. **A checagem de compatibilidade do PacaPet vem de graça.** Brincar sem bola continua sendo a unidade "brincar sem alvo", e uma ação
   impossível não existe como unidade. O mundo decide o que dá para fazer, e a palavra não precisa de um filtro à parte.
4. **O "quem decidiu" já existe.** A soma da ativação é guardada termo a termo (seção 7 da espec do modular). O termo da palavra é
   `Σ_k H[b, pal_k]·pal_k`, separado do resto do hábito, e o DigiBrain e o painel o mostram sem mecanismo novo.

**Quando a tabela bastaria:** se o objetivo fosse um apelido determinístico de um comando ("zorp" = Brinca). Isso é o arco fixo com outro
nome, não aprendizado. A IT6 já cobre isso.

### 3.8 O que o pet mostra (a tela; detalhe na prancha)

- **A força** de cada ligação é `H[b, pal_k]`, só leitura. **"Liga"** quando `H[b, pal_k] ≥ θ_liga` e b é o maior da coluna da palavra, com
  uma folga `θ_folga` sobre o segundo (os dois PROPOSTOS: `H_max / 4` e `H_max / 16`).
- **O cartão** aparece uma vez, na primeira vez que uma ligação passa o limiar: "Growlmon liga 'zorp' a brincar." É derivado do estado e
  refeito pelo replay. Não é evento.
- **O painel de hábitos** (WD-1) ganha a seção "Palavras": cada palavra com o comportamento que ela mais puxa e uma barra de força.
  "Ainda nada" quando não passa o limiar.
- **Os textos, pela D-PD-2:** "liga", "puxa" e "costuma" estão liberados. "Entende", "sabe o que quer dizer" e "obedece" estão proibidos.
  Isso vale para a tela, as dicas do Professor Agumon e a fala.
- **A fala:** uma palavra aprendida não é um conceito da fala. A voz não a cita como compreendida, e o verificador recusa uma frase que diga
  que o pet entendeu o dono. Se a frase pode citar a palavra (o pet repete "zorp") é uma pergunta futura, fora desta espec.

### 3.8b De quem vale a palavra

Nesta espec, só a do dono do pet, pelo arco daquele pet: o evento `pl` vai ao registro de um pet só. O GARP lembra que a palavra de primeira
mão vale mais que a de segunda (vault, `LEITURA_GARP_2026-11-17.md`). Três casos ficam **fora** e voltam como pergunta própria, se um dia
fizerem sentido:
- uma palavra dita por outro dono (o MMO);
- uma palavra ouvida de outro pet;
- uma palavra passada do pet ao gêmeo dele.

### 3.9 O registro e o replay

- **O evento `pl`** fica no registro do pet, como toda entrada do dono. O replay o lê e não normaliza de novo.
- **O registro da decisão** ganha os `pal_k` de z e o termo `habito_palavra`, separado do `habito`. A soma não muda, e a sonda lê os dois.
- **Cada atualização da P2** já é registrada (a regra, o índice, o antes, o depois e o r). As colunas novas entram no mesmo registro.
- **Com a subchave desligada,** a vida de hoje sai byte a byte, e o gabarito é gravado num commit próprio antes do código.
- **Com a subchave ligada e sem nenhum evento `pl`,** a vida também sai byte a byte (todos os `pal_k` = 0, e `W⁰` e H começam em 0). Um teste
  confere.

### 3.10 Python e web (D-PD-4)

- **No Python,** atrás de `ConfigDigibrain.palavra` (PROPOSTO), desligada:
  - a população no M-SENS;
  - as características `pal_k` no z, com a outra tupla;
  - a porta do 3.4;
  - as colunas da P2;
  - o termo `habito_palavra` no registro.
- **A entrada da palavra na bancada:** um gancho da política, `ouvir_palavra(p, tick)`, chamado por uma camada de motor atrás de chave,
  como as outras camadas. O `engine.py` não muda. O desenho exato da camada é da etapa de código.
- **No TS:**
  - o espelho do cérebro, com paridade bit a bit no Node (os gabaritos de `experiments/exportar_*.py`);
  - o evento `pl` no `Motor.aplicarEvento`;
  - uma `VERSAO_PET` nova.

  Os pets das versões antigas não mudam.
- **A IT6 (o pedido fixo) continua só no TS (EN-4).** A palavra e o pedido convivem no arco. O pedido é percepção sem aprendizado, e a
  palavra é percepção com o P2.

### 3.11 A voz, depois (D-PD-3)

Numa etapa própria, a transcrição do ditado passa pela mesma normalização e vira o mesmo evento `pl`, no modo livre gravado: o replay lê o
evento, e não o áudio. As correções conhecidas do ditado (a memória do projeto, por exemplo "patch" por pet) ficam como pista do risco.
Que a transcrição precise de confirmação na tela antes de gravar (PROPOSTO: sim) se decide nessa etapa.

## 4. A ordem, passo a passo

1. O dono abre o arco do pet (o segurar parado, a IT3) e escolhe **Dizer…**. Abre o campo com as palavras já ditas como atalho.
2. O dono digita e confirma. A tela normaliza e grava `pl` com o tick. O balão do dono mostra a palavra sobre o pet.
3. Na próxima decisão dentro de `W_p`, `pal_k = S` em z, salvo pela porta do 3.4. A ativação de cada comportamento soma `H[b, pal_k]·S`.
4. O pet faz o que o M-ARB sortear, que pode ser outra coisa ou nada de novo. A tela não promete nada.
5. Na consequência da opção, a P2 atualiza `H[b*, pal_k]` com o r do corpo. Um carinho dentro da janela soma pela D-EL.
6. Se uma ligação passar o limiar pela primeira vez, aparece o cartão (3.8).

## 5. O que não muda

- O `engine.py`, os pets antigos e a vida com a chave desligada.
- O inato: nenhuma palavra puxa nada ao nascer.
- A regra "o gesto do dono não treina o pet": a palavra aprende pelo corpo, como todo hábito.
- A DC5: não se afirma que o pet entende.
- A luta: sem botão, e a palavra não entra nela.

## 6. O teste falsificável (T-PALAVRA)

**A hipótese, escrita antes:** a ligação vem da **coerência** do ensino, não de quantas vezes a palavra é dita. Um dono coerente deixa a
palavra puxando o comportamento ensinado mais do que um dono inconsistente com o mesmo número de palavras e de carinhos.

**A fonte da restrição:** Thomaz e Breazeal (`10.1016/j.artint.2007.09.009`, VERIFICADA) documentam que pessoas reais dão recompensa
antecipada e são inconsistentes, e o PacaPet mostra o mesmo limite (2 de 7 dicas disparam com ensino contraditório). Isso é a razão do
braço, não um número a reproduzir.

### 6.1 Os braços

Todos usam:
- o modular com a subchave da palavra ligada;
- o corpo com `gestos`;
- o mundo com bola e frutas;
- a D-EL ligada;
- o mesmo orçamento de contatos;
- a palavra "zorp" e o comportamento-alvo **brincar**, porque brincar alivia o tédio pelo corpo (premissa P1).

| braço | o dono |
|---|---|
| **C, coerente** | diz "zorp" sempre no mesmo tipo de momento (tédio acima de um limiar e bola à vista) e faz um carinho no primeiro passo depois de o pet brincar dentro da janela |
| **I, inconsistente** | o mesmo número de "zorp" e de carinhos da unidade C pareada. Metade dos "zorp" em momentos sorteados (rng própria, `derivar_semente("palavra-dono", semente)`), e os carinhos depois de um comportamento sorteado entre os que vieram depois da palavra, uma fração deles antes de o pet agir (o retorno antecipado de Thomaz e Breazeal). A fração está PROPOSTA |
| **S, sorteado** (secundário) | o mesmo número de "zorp" em momentos sorteados e o mesmo número de carinhos em passos sorteados, sem olhar o pet. Separa a exposição da contingência |
| **0, sem palavra** | só para as premissas; com a chave ligada e sem `pl`, sai byte a byte da chave desligada (3.9) |

### 6.2 As premissas (antes do contraste)

- **P0, técnica:** no braço C, `H[brincar, pal_zorp]` sai de 0, e o registro mostra as atualizações.
- **P1, do corpo:** neste mundo, brincar dá `r_n > 0` com tédio alto. Sem isso, a D-PD-1 não tem o que ligar, e o teste para aí,
  registrado.
- **P2, a porta:** com `alguma_urgencia_critica` verdadeira, `pal_k = 0` e a elegibilidade da palavra é 0. É conferência de mecanismo, por um teste
  unitário, e não uma hipótese.

### 6.3 A medida: a sonda contrafactual

Em pontos de sonda fixos no plano (PROPOSTO: as decisões de um dia de pet depois do dia N), o estado é congelado, e calcula-se:

`Δ_b = π(b | pal_zorp = S) − π(b | pal_zorp = 0)`

- **As regras da conta:** é a mesma conta do M-ARB sobre as mesmas ativações, com o mesmo `u` e **sem rng nova**, como nas sondas do
  M-ARB. A vida não muda: a sonda só lê.
- **A medida principal:** `Δ_brincar` nos pontos **fora do contexto de ensino** (tédio abaixo do limiar do braço C). Isso separa "zorp" do
  contexto em que foi dito (3.5).
- **As secundárias:**
  - o `Δ_brincar` dentro do contexto;
  - o `Δ` dos outros comportamentos (a especificidade: "zorp" não puxa comer);
  - a fração das vidas em que a ligação passa o limiar do 3.8, que é o equivalente descritivo do "2 de 7" do PacaPet;
  - a guarda: o bem-estar e a nutrição não pioram no braço C.

### 6.4 O contraste e a previsão

- **H1 (o gate da frente):** `Δ_brincar(C) − Δ_brincar(I) > 0`, pareado pela unidade (o mesmo genoma, o mesmo mundo e a mesma semente),
  com o IC 95 % por bootstrap acima de 0.
- **H1 cai** se o IC incluir 0 ou ficar abaixo dele. Nesse caso, a palavra não separa o ensino coerente do inconsistente, e o resultado
  negativo é registrado como está.
- **Secundário, descritivo:** `C − S` (contingência contra exposição) e `I − S`.
- **O que a previsão não diz:** não diz quanto, porque os números são da rodada de equilíbrio. Não diz que o pet entende. Não diz nada
  sobre donos humanos: os donos aqui são scripts.

### 6.5 O que vem antes da run

- o plano de análise `docs/PLANO_ANALISE_V3_PALAVRA_DONO.md`, commitado antes da primeira vida, com a faixa reservada pedida ao
  coordenador, o N de unidades, os pontos de sonda e o sha256 no meta;
- a validação roda **uma vez**, no máximo com 4 processos (V3-D8);
- os limiares do braço C e a fração do I entram no plano, PROPOSTOS, e não se ajustam olhando para a validação.

## 7. As etapas (um PR por etapa, cada uma com o sim do Matheus)

| etapa | o que entrega | depende de |
|---|---|---|
| **PD0, o papel (este PR)** | a espec, a prancha e o teste; D-PD-1 a D-PD-4 decididas | — |
| **PD1, o Python** | o gabarito antes; a subchave; o M-SENS, o z, a porta e a P2; o gancho e a camada da bancada; os testes (byte a byte desligada, byte a byte sem `pl`, a porta, a vaga pela ordem do registro) | a LZ2a (o modular na base nova) e o código da D-EL (etapa 2 do `TAREFA_V3_ELOGIO`) |
| **PD2, o plano e a run** | o plano de análise, a faixa e a validação uma vez; o `RESULTADO_V3_PALAVRA_DONO.md` | PD1 |
| **PD3, o jogo web** | o espelho TS com paridade; o evento `pl`; a `VERSAO_PET` nova; a vista da prancha (o Dizer… no arco, o balão, o cartão, a seção no painel de hábitos) | PD1; a IT3 (o arco) e o painel de hábitos (WD-1) |
| **PD4, a voz** | a transcrição gravada como `pl`, com confirmação na tela | PD3; a decisão da etapa |
| **PD5, o alvo** (se D-PD-6 abrir) | a tabela `Hα` atrás da segunda subchave e o teste com dois alvos | PD2 |

## 8. As decisões da prancha, da espec e do teste (DECIDIDAS pelo Matheus, 2026-11-17, no chat da sessão F4)

As perguntas foram levadas com a recomendação e o custo de errar, e as respostas estão literais (a opção escolhida).

| # | a pergunta curta | recomendação | custo de errar |
|---|---|---|---|
| D-PD-5 | Aprova a prancha (o Dizer… no arco, o balão do dono, o cartão "liga" e a seção Palavras no painel de hábitos)? | sim | uma prancha errada vira código errado na PD3; refazer a prancha é barato agora |
| D-PD-6 | A palavra puxa só o comportamento primeiro, com o alvo numa segunda subchave depois? | sim, só o comportamento | com o alvo junto, o teste precisa de dois alvos e o H cresce 9 vezes antes de saber se a ideia funciona |
| D-PD-7 | 4 vagas de palavra por pet, sem esquecer? | sim (PROPOSTO, se acerta no equilíbrio) | poucas vagas frustram o jogador; muitas engordam o z. Esquecer depende da PE-10 |
| D-PD-8 | Aprova a espec e o T-PALAVRA (C × I pela sonda, H1 como gate), para a PD1 começar depois da LZ2a e da D-EL? | sim | sem o teste, a mecânica vai ao jogo sem prova de que ensina alguma coisa |
| D-PD-9 | Se a H1 cair, a palavra fica fora do jogo até um desenho novo? | sim | pôr no jogo uma palavra que não separa o dono coerente do inconsistente promete ao jogador um ensino que o pet não faz |

**As respostas do Matheus (literais):**
- **D-PD-5:** "Aprovo (Recomendado)".
- **D-PD-6:** "Só comportamento (Recomendado)".
- **D-PD-7:** "4 vagas, sem esquecer (Recomendado)".
- **D-PD-8:** "Aprovo (Recomendado)".
- **D-PD-9:** "Fica fora (Recomendado)".

## 9. A literatura usada

- **PacaPet:** Karati e Kluver (2026), WOCHAT, `10.21437/WoChat.2026-2`. VERIFICADA, pelo texto completo (vault,
  `CONFERENCIA_REFS_FALA_LLM_2026-11-16.md`). É a origem da ideia e do limite do ensino contraditório.
- **Thomaz e Breazeal**, `10.1016/j.artint.2007.09.009`. VERIFICADA (a skill `literatura-digilab`). O dono real é antecipado e
  inconsistente, e é a razão do braço I.
- **A P2 e o sustento dela** (Cliff e Grand 1999; Frémaux e Gerstner 2016; Gerstner et al. 2018; Keramati e Gutkin 2014): os da espec do
  modular, seção 2.4, sem nada novo.
- **O sinal do corpo como terceiro fator continua SEM FONTE** (espec do modular, seção 2.4), e a palavra herda isso.
- **Dreyfus (2002)**, `10.1023/A:1021351606209`, VERIFICADA pelo texto completo (a skill; o PR #954). A fonte afirma que uma das
  restrições do corpo é medir o sucesso pela satisfação do próprio agente, e não pelo critério do pesquisador. **Leitura do DigiLab:** é um
  enquadramento a favor da D-PD-1 (o desfecho no corpo, e não o elogio), e não evidência de que ela funciona. A outra restrição dele, a
  ordem das experiências, conversa com o braço C × I.
- **"Nunca escrever que o pet entende"** (a skill, a rodada Dreyfus de 2026-11-16, Searle 1980 e Harnad 1990, VERIFICADAS): é enquadramento, e a D-PD-2 o segue.
- **Nenhuma alegação de novidade.** A palavra livre que vira gatilho está publicada (PacaPet), e o comportamento ensinado também (a regra 3
  da skill). O que resta é o teste com braço de controle, e ele também não é contribuição sem uma busca dirigida.
