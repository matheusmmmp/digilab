# Especificação: a fala que nasce da rede (decodificador de conceitos, LLM só como voz)

Gerente da frente CONVERSA_PET (Claude Code, Opus 5.5), 2026-11-06. Status: **DC-A a DC-E DECIDIDAS pelo Matheus em 2026-11-06, todas
pela recomendação ("Aceito todas")**; os números (pesos, limiares) seguem PROPOSTOS até a calibração. Decisão de partida do Matheus (2026-11-06): a fala do
pet nasce das redes neurais dele; a LLM só põe em palavras, sem ver logs nem fatos ("LLM só como voz"). Ideia de origem: o
`docs/futuro/decodificador_conceitos.md` (Matheus, 2026-10-04). Mapa do estado interno: levantamento de 2026-11-06 sobre `origin/main`
(resumo na seção 1; arquivo:linha no levantamento, guardado com esta espec).

## 0. O que muda

```
hoje:     página monta FATOS (estado do jogo, memória do Bandit, desejo do A) → LLM escreve → verificador confere contra os FATOS
proposta: passo do modular → leitura dos sinais nomeados → conceitos C_t (valor + confiança) → intenção da fala
          → LLM-voz recebe SÓ {intenção, conceitos acima do limiar, estágio, estilo da espécie, mensagem do dono}
          → verificador confere a frase contra os conceitos
```

A LLM não vê estado, log nem fato: só o que a rede "quer dizer" naquele instante. Conceito incerto vira hesitação ("acho que..."), nunca
afirmação. O texto continua fora do registro do pet; o comando pelo catálogo fechado continua sendo a única ponte de volta.

## 1. O que a rede tem hoje (pets v17, modular `CONFIG_DIGIBRAIN_LAB`)

- **Legível e recalculável:** tudo é inteiro na escala S = 1024, com nome, e o `motivo` de cada decisão (`web/app/motor/digibrain/adapt.ts`
  ~143–166; `digilab/digibrain/adapt.py` ~210–246) carrega as urgências dos 11 receptores, o drive dominante, V e E (afeto), F (frustração),
  a intenção em curso I* e o compromisso C, todas as opções com os termos de cada módulo (inato, incentivo, hábito, memória, persistência,
  lembrança), os pesos e a escolhida, as sondas contrafactuais ("a escolha mudaria sem o hábito?"), a lembrança ativa (episódio, semelhança,
  sigma), "sei onde tem comida", a consolidação do dia, as lutas e a consequência (r, r_n, canais). O replay refaz tudo bit a bit.
- **O painel já lê isso:** `digibrain/leitura.ts` calcula as partes por termo e as chances; o decodificador começa dali.
- **O que a fala usa hoje: nada disso.** `estadoDoPet` lê `m.motivos` (só motivos do treino desde o v11), a memória do Bandit e o desejo e o
  caráter do cérebro A parado. A fala de hoje pode contradizer o cérebro que decide.
- **Lacunas da rede:** não há afeto pelo dono (os gestos só viram corpo), nem intenção de comunicar (`chamar_atencao` não tem conteúdo),
  nem emoção com nome (só V e E), e a lembrança de luta é registrada mas nunca muda uma escolha.

## 2. Os conceitos v1 (CBM manual: sinais nomeados → conceito, sem treino)

Cada conceito tem valor em [0, S] e confiança em [0, S], calculados por uma função declarada dos sinais do `motivo` (inteiros, sem rng),
com o mesmo código em Python e em TS e um gabarito de paridade. Os pesos das funções são PROPOSTOS, SEM FONTE, até a calibração.

| conceito | sinais | confiança |
|---|---|---|
| fome / querer comer | urgência da fome, fração dos pesos das opções de comer, I* = comer, pista de comida lembrada | fração da escolhida |
| cansaço / sono | urgência da energia, reflexo do sono, noite, peso de dormir | idem |
| bem-estar ou mal-estar | sinal e módulo de V; r_n da última consequência e o canal que mais pesou | módulo de V |
| agitação / alarme | E; urgências de dor, susto e estresse | E |
| aversão aprendida a X | lembrança com sigma < 0 casando com uma opção; desfecho aprendido negativo da classe; sonda da lembrança decidindo | sim da lembrança |
| frustração | F; fins desistiu, sumiu ou trocou; decisões sem progresso | F |
| determinação | I*, C, parte da persistência, sonda da persistência decidindo | C |
| indecisão / conflito | margem pequena entre os dois maiores pesos; termos opostos na escolhida; sondas que mudariam a escolha | 1 − margem |
| lembrança ativa | episódio recuperado, semelhança, tipo de memória (recente, duradoura, central), sigma | sim |
| solidão / falta de cuidado | urgência da solidão, tempo sem cuidado, peso de chamar atenção e de emburrar, gestos recentes | urgência |
| curiosidade | urgências de curiosidade e tédio, novidade dos objetos, g_exp | g_exp |

Um conceito só entra na fala acima de um limiar de valor; com confiança abaixo de outro limiar, entra como hesitação. Ambos PROPOSTOS.

**O formato (fixo, para a DC1 e a DC2 andarem em paralelo):** a saída do decodificador, por decisão do modular, é

```json
{"versao": "dec-v1", "k": 123, "intencao": "fome",
 "conceitos": [{"nome": "fome", "valor": 870, "confianca": 610, "alvo": "racao"}, ...]}
```

com `nome` num catálogo fechado (os da tabela, com bem-estar e mal-estar separados; ids sem acento: `fome`, `sono`, `bem_estar`, `mal_estar`, `agitacao`, `aversao`,
`frustracao`, `determinacao`, `indecisao`, `lembranca`, `solidao`, `curiosidade`), `valor` e `confianca` inteiros em [0, 1024] e `alvo`
opcional (uma classe de objeto, um episódio de memória pelo id ou um rival, sempre de um catálogo). A intenção, na I-a, é um nome do mesmo
catálogo. O servidor recebe isso da página, valida contra o catálogo (entrada não confiável) e só isso vai à voz.

## 3. A intenção da fala (o "o que dizer")

- **I-a, por regra sobre os conceitos (post-hoc).** A intenção é o conceito dominante, ou a lembrança quando ela decidiu a escolha. Não muda o
  cérebro nem a vida; sai já na primeira versão.
- **I-b, a rede escolhe falar (ante-hoc).** O modular ganha unidades de fala (pedir comida, reclamar, contar uma lembrança, chamar o dono),
  que competem com as outras opções e aprendem pelas consequências no corpo (o dono atende, a fome cai). A rede passa a decidir o que dizer
  como decide o que fazer. Mecânica nova atrás de chave desligada, pesquisa no Python antes, paridade depois.

## 4. A conversa

O modular não tem entrada de linguagem. Quando o dono escreve, o conteúdo da resposta é o estado atual da rede (conceitos + intenção); a
mensagem do dono vai só à voz, para a frase responder a ela, e os fatos "o dono me disse" (M4) continuam valendo para citar o que ele disse.
O texto do dono não entra na rede (nada de "texto ensina"), salvo o comando pelo catálogo fechado.

## 5. Como medir se a fala é da rede (do `decodificador_conceitos.md`, seção 4)

- **Fidelidade causal:** as sondas contrafactuais já existem; um conceito que diz "foi a lembrança" tem de coincidir com a sonda da lembrança
  decidindo.
- **Completude:** quanto da escolha se prevê pelos conceitos contra pelos sinais inteiros.
- **Calibração:** conceito declarado incerto erra mais que o declarado certo.
- **Fala fiel aos conceitos:** o verificador confere que a frase só afirma conceitos acima do limiar e não acrescenta estado.
- **Humanos:** o Matheus compara às cegas, em pares, a fala pelo decodificador contra o `conversa-v1` de hoje (o plano de análise é
  reescrito para esses braços antes de qualquer rodada).

## 6. Missões (depois das decisões)

| missão | o que | onde |
|---|---|---|
| DC1 | o decodificador: conceitos e confiança a partir do `motivo`, Python e TS, gabarito de paridade, no painel do DigiBrain | `digilab/digibrain/` ou módulo novo fora do pet, `web/app/motor/digibrain/` |
| DC2 | a voz: prompt `voz-v1` que recebe só intenção + conceitos; a página manda os conceitos no lugar do `estadoDoPet`; verificador contra os conceitos; chave desligada | `digilab_fala_livre/`, `servidor/`, `web/app/src/falaLivre.ts` |
| DC3 | só se I-b: as unidades de fala no modular, com plano de análise | `digilab/digibrain/`, espelho TS |
| DC4 | a avaliação: plano reescrito, calibração e validação únicas | `docs/PLANO_ANALISE_V3_CONVERSA_PET.md` (adendo) |

## 7. Decisões do Matheus (DECIDIDAS em 2026-11-06, todas pela recomendação)

- **DC-A. Só sinais do modular na fala?** O desejo e o caráter que o jogo mostra vêm do cérebro A parado, e a emoção com nome vem do Bandit;
  podem contradizer o modular. Recomendo **sim, só o modular**. Custo de errar: o pet perde, na fala, a emoção com nome e o desejo
  (ficam V, E e os conceitos acima); se você quiser emoção com nome, ela vira conceito novo sobre V e E.
- **DC-B. A intenção: I-a agora, I-b como pesquisa?** Recomendo **I-a na primeira versão e I-b em seguida, como pesquisa no Python**. Custo de
  errar: com só I-a, "o que dizer" é regra sobre a rede, não escolha dela; com I-b direto, a fala atrasa semanas e mexe no cérebro.
- **DC-C. A lembrança de luta passa a poder mudar escolhas?** Hoje ela nunca casa com uma opção, então "rancor do rival" só existe como
  registro. Recomendo **não nesta frente** (é mecânica do cérebro, fica para a ponte da luta); o decodificador fala da luta como lembrança.
- **DC-D. Afeto pelo dono:** não existe na rede. Recomendo **não inventar na fala**: a solidão e a falta de cuidado cobrem parte; um afeto
  pelo dono de verdade é mecânica nova do cérebro, com frente própria.
- **DC-E. O que fica do que já foi feito:** recomendo manter na `main`, atrás das chaves, o `conversa-v1`, o `verif-v6`, os fatos "o dono me
  disse" e o cliente Claude como a base da voz e da trava, e pausar a M6 e a avaliação antiga.

## 8. Literatura

Koh et al. 2020 (CBM, arXiv:2007.04612) está VERIFICADA na tabela do projeto. As outras do `decodificador_conceitos.md` (PCBM, post-hoc CBM,
Discover-then-Name, M-CBM, Turpin et al. 2023) estão como **pista**: verificar antes de citar. Nada aqui é novo: o gargalo de conceitos e a
fala por conceitos nomeados já estão publicados; Façade (2005) já separava "o que dizer" (decidido fora) de "como dizer".
