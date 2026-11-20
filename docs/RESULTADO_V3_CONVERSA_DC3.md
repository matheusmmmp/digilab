# RESULTADO V3 — CONVERSA_PET, DC3: a rede escolhendo falar (2026-11-07, Gerente da CONVERSA_PET, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_CONVERSA_DC3.md](PLANO_ANALISE_V3_CONVERSA_DC3.md), APROVADO em 2026-11-07. O adendo 1 (o crédito da fala
até a decisão seguinte e o gate condicionado à necessidade) também foi APROVADO no mesmo dia, e o registro da run está na seção 13.

**A run:** única, na `main` 9e16832 (árvore limpa). Bases 79101…79505, K = 40 por base: 200 unidades e 3 200 vidas de 14 dias, só no
comedouro. Rodou em 4 processos, com 42 min de parede.

**Os artefatos** ficam em `artifacts_v3_conversa_dc3/run/`: `meta.json`, `medidas.json`, `resultado.json` e `vidas.tar.gz`.
- Todo número deste documento sai do `resultado.json`. O que é conta minha sobre ele está marcado como "conta sobre o artefato".
- A análise foi refeita a partir do `medidas.json` e saiu igual byte a byte. Os sha256 do `meta.json` batem.

## 1. A leitura, uma linha só (7.4)

| premissas | G-ESCUTA | guarda | a linha |
|---|---|---|---|
| as quatro passam | **"> 0"** | **"≈ 0"** | **2: a rede aprende a falar pela consequência sem cuidar pior de si.** O que segue é a DC3d (o porte ao jogo, atrás de chave) |

- **G-ESCUTA:** é a diferença atende − ignora na P(fala pertinente | necessidade), no LAB+F, nos dias 8 a 14, média das 4 células.
  - A média é **+0,0212**, com IC95 [+0,0125; +0,0300], n = 200 unidades, nenhuma fora; t = 4,79.
  - O dp entre as unidades é 0,063. O efeito detectável com poder 0,8 era 0,0125.
- **G-COMEDOURO-DC3:** é a diferença LAB+F − LAB na taxa por episódio de fome, com o dono que ignora.
  - A média é −0,0062, com IC95 [−0,0160; +0,0035], dentro da margem δ = 0,018: **"≈ 0"**.
  - A margem efetiva pelo dp observado foi 0,0139.
- **As premissas:**

| premissa | o valor |
|---|---|
| P-FALA | 20,7 % das decisões fora do dormir são fala (IC95 [20,5; 20,9] %) |
| P-ATENDE | 4,64 atendimentos por dia nos dias 1–3 (IC95 [4,55; 4,72]) |
| G-ELEGIVEL-EP | passa nos dois braços |
| P-NECESSIDADE | 100 % das unidades com o gate definido |

- **A conferência do crédito (4.4, A1.3):** 51 076 de 51 076 atendimentos do LAB+F caem dentro do intervalo da fala que os provocou. No LAB
  são 0 de 39 047, como deve ser, porque o LAB é o controle.

## 2. O que acompanha o gate (descritivo, sem gate; seção 8 e A1.3)

**A1. O contraste se inverte com o tempo.** A tabela dá a P(fala pertinente | necessidade) no LAB+F:

| janela | atende | ignora |
|---|---|---|
| dias 1–3 | 0,125 | 0,241 |
| dias 8–14 | 0,188 | 0,163 |

- No começo, quem é atendido fala menos do que precisa, porque as necessidades dele são mais baixas.
- Ao longo da vida, a fala pertinente sobe com quem atende e cai com quem ignora. O gate pega o fim dessa inversão.
- A extinção também aparece. A EXT (a fala por dia nos dias 8–14 menos a dos dias 1–3, com o dono que ignora) dá −5,26 falas por dia,
  IC95 [−5,60; −4,92]: **"< 0"**, como previsto.

**A2. Quase todo o efeito vem do dono atencioso, contado duas vezes.**
- Esta é uma conta sobre o artefato, por célula, a partir das médias de `descritivo.necessidade`, dias 8–14. A diferença atende − ignora é:

| dono | atende − ignora |
|---|---|
| atencioso | **+0,082** |
| incoerente | +0,082 (a célula é idêntica à do atencioso no comedouro, a `CELULA_DUPLICADA`) |
| aleatório | **−0,044** |
| relapso | **−0,022** |

- O plano manteve a célula repetida, como na C4 e na AN4, e o gate é a média das 4. **Sem a repetição, a média das três células
  distintas fica em torno de +0,005.** Isso é uma conta sobre as médias, não um gate nem um IC: o gate é o registrado, e passou. Mas o
  efeito é do dono atencioso. Com o relapso e com o aleatório, atender não aumentou a fala pertinente.
- **Um resto do confundidor (A1.2):** com o atencioso que ignora, a urgência média nas decisões com necessidade fica no teto (1 024 = S).
  Com o que atende, ela fica em 722. O condicionamento tira o "o dono já resolveu", mas não iguala a intensidade.

**A3. A fala aprende por conteúdo, e só a de companhia sobe.** As linhas de H do LAB+F, a soma dos pesos no fim do dia 14:

| unidade | atende | ignora |
|---|---|---|
| fome | −233 | −523 |
| higiene | −45 | −197 |
| solidão | **+393** | −252 |

- O r_n médio creditado à fala de companhia com o dono que atende vai de +154 a +610, conforme o dono.
- **O pedido de comida nunca compensa,** nem com quem atende: o r_n da fala de fome fica entre −185 e −239.
- **Por quê, pela mecânica:** o dono que atende põe a ração no comedouro, e o pet ainda precisa andar até ela. Na decisão seguinte a fome
  ainda não caiu, e a do passo subiu. Já o carinho mexe na solidão no mesmo passo.
- **Então o que a rede aprende é "pedir companhia a quem dá companhia",** não "pedir o que precisa".

**A4. O corpo:** com o dono que atende, a fração do tempo fora da faixa nos dias 8–14 é pior no LAB+F do que no LAB, por +0,026 (IC95
[+0,020; +0,032]). Com o que ignora, a diferença é "≈ 0". O atendimento gasta o orçamento do dono com a fala, no mesmo orçamento de 16
por dia (DC3-3).

**A5. O decodificador:** o conteúdo da fala coincide com a intenção do `dec-v2` em menos de 5 % das falas: 4,4 % na de companhia com o
dono que atende, perto de 0 na de fome, e 0 na de higiene, que não é conceito do catálogo. A fala antes da ação (I-b) e a explicada
depois (I-a) dizem coisas diferentes.

## 3. O que este resultado não afirma

Ele não afirma:
- que o pet "quer se comunicar" ou entende linguagem;
- que a fala parece viva ao jogador (SEM FONTE; isso é do Matheus, jogando);
- que o modular supera o A;
- um tamanho de efeito fora das condições da run;
- nenhuma novidade.

**Em particular:** ele não mostra que a rede aprende a pedir comida, nem que aprende com donos que não são atenciosos (A2, A3).

## 4. O que segue

- **Pela 7.4 (linha 2): a DC3d,** o porte ao jogo atrás de chave: o espelho TS da `fala_unidades`, a paridade e a unidade escolhida como
  intenção da voz.
- **Para o porte, pelo descritivo:** no jogo, o jogador faz o papel do dono que atende. A3 diz o que esperar: um pet que pede carinho e
  deixa de pedir comida.
- **A pergunta do pedido de comida fica para depois,** sem gate: por que ele não compensa e se o crédito deveria ir até o pet comer. Ela
  vai para a DC4 ou para um adendo novo, se o Matheus quiser.
