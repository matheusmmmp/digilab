# A fala do assistir: o pet comenta o que vê na TV, pelo que ele percebe

Status (2026-11-11): **PROPOSTO**, com duas direções do Matheus já DECIDIDAS (o caminho A e o órgão, sem léxico do pet). Só papel: nenhum código, nenhuma faixa, nenhuma vida, nenhum plano de
análise. A frente é a `docs/TAREFA_V3_GOSTO_VISUAL.md`. **Entra depois da GV3** (a run descritiva genoma × dono da
`docs/futuro/gosto_visual_pet.md`, seção 9, que é a P1e da `docs/ESPEC_GOSTO_VISUAL_P1.md`). A GV3 está em curso: o plano
`docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md` foi APROVADO pelo Matheus em 2026-11-11, e não há resultado ainda.

**A decisão do Matheus (2026-11-11), DECIDIDA:** "quero que siga o recomendado. Quero que os comentários tecidos venham da percepção do
pet" (ditado por voz; o "patch" do ditado é "pet"). Ficam decididos:
- **o caminho A** (seção 2): o comentário nasce da percepção do pet, isto é, do que ele vê pelos quatro números da visão e ouve pelos três
  do som, e do agrado, do interesse, da novidade e da habituação que a rede calcula. A LLM só dá voz ao conceito e nunca vê a tela;
- **o caminho B** (seção 3), um modelo de visão olhando a tela, fica **rejeitado**.

É a FA-1 (seção 7). Todo o resto deste documento continua PROPOSTO, inclusive o limite de frequência e o custo.

**A segunda direção do Matheus (2026-11-11), DECIDIDA:** perguntado se queria um léxico do pet (só as palavras ensinadas), ele recusou:
"Não, eu quero que mantenha do jeito que tá. Eu quero, na verdade, que ele fale mesmo coisas que eu não tenha ensinado, mas ele tenha
percebido. A ideia é que ele compreenda o que está passando nos pixels, não apenas recebendo um monte de pixels e não identificando nada
[...] minha ideia é que o órgão visão seja um módulo dedicado da IA para identificação de um estudo de visão computacional e passar os
conceitos para essa rede neural, para ela interpretar esses preceitos." Ficam decididos:
- **sem léxico do pet:** vale a regra atual da fala (os fatos citados e o estágio), e a LLM pode usar palavras que o dono não ensinou;
- **o caminho A ganha o órgão:** a percepção do pet passa a incluir um órgão que reconhece conceitos no quadro e no som (seção 10, a parte
  nova, PROPOSTA no desenho). O comentário continua nascendo da percepção do pet;
- **o caminho B rejeitado** é a LLM, ou um modelo de visão na nuvem, olhando a tela.

O desenho do órgão (a seção 10) é PROPOSTO, vem depois da GV3 e não tem código antes da revisão do Matheus. A GV3 em curso segue com os
quatro números.

**A terceira direção do Matheus (2026-11-11):** "Os conceitos, eles podem ser populados pela base de dados dos [corpus] do Digimundo?
[...] Aquela base de dados que envolve o Digimon World, o Digimon, os anime e tudo, os conceitos de Digimon. E criar uma mitologia em volta
e inserir dentro desses conceitos, dentro desse órgão. Ele identificar isso, pelo menos como um estado." E depois: "Vamos testar um braço
da pesquisa com isso". O desenho está na seção 10.10 (PROPOSTO, FA-14 a FA-20); o braço de pesquisa, no plano
`docs/PLANO_ANALISE_V3_GOSTO_VISUAL_FALA.md` (PROPOSTO, nenhuma run antes da aprovação do Matheus).

**Regras deste documento:**
- referências só as que o projeto já tem conferidas: as da nota do vault `BUSCA_GOSTO_VISUAL_2026-11-10.md` citadas na
  `docs/futuro/gosto_visual_pet.md` (ainda fora de `docs/referencias/`, até a GV-12) e as da `docs/futuro/decodificador_conceitos.md`, com o
  status que ela dá; o resto é **SEM FONTE**;
- todo número novo é PROPOSTO;
- **nenhuma alegação de novidade.** Pets e personagens que comentam o que acontece existem há muito tempo em jogos; nenhuma busca foi feita
  sobre um agente que comenta a tela pelo próprio estado interno, e a falta de busca não autoriza dizer nada;
- vocabulário de estímulo, de registro, de escolha e de medida: o pet que diz "gostei" não sente prazer por isso (F2,
  `docs/DEFINICOES_FRUTAS_V2.md`, 2.2). "Gostei" é o nome de um conceito com um limiar sobre o agrado;
- nada aqui muda `engine.py`, o cérebro A, o decodificador de hoje, a voz do jogo ou uma decisão já tomada. Tudo entra atrás de chave
  desligada.

## 0. Em uma página

- **O que é:** enquanto o pet olha a TV (ou a tela real, no modo livre gravado), ele às vezes diz uma frase curta sobre o que vê: "gostei",
  "de novo!", um susto, "que chato", "o que é isso?".
- **De onde vem o comentário (DECIDIDO, caminho A):** do sinal que o próprio pet já calcula (o agrado, a novidade, a adaptação, o susto),
  lido por conceitos novos do decodificador, como a fala da DC. A LLM recebe o conceito, a espécie e o humor, e escreve a frase. Ela nunca
  recebe a imagem, o áudio nem os números (GV-10).
- **O órgão da visão e do ouvido (seção 10, PROPOSTO, depois da GV3):** um módulo local de visão computacional que reconhece conceitos no
  quadro (gato, pessoa, rosto, texto…) e no som (música, fala, risada…), ao lado dos quatro números de hoje, que viram a "retina". Com ele
  o pet pode dizer "um gato!" sem que o dono tenha ensinado, porque o órgão dele percebeu. Nada sai da máquina.
- **A gravação:** o comentário segue a regra da fala de hoje. O texto vai para o log de apresentação da fala, nunca realimenta o pet; o
  conceito que o originou se refaz do log do pet pelo replay (FA-6).
- **O limite:** um comentário a cada poucos minutos reais (5 min, PROPOSTO), e só enquanto o pet olha.
- **O custo:** zero em dinheiro com o `gemma2:9b` local, o padrão do jogo; cerca de US$ 0,004 por hora de tela com o Claude Haiku, pela
  conta da seção 5, com as premissas PROPOSTAS.
- **As dependências:** a voz do jogo (`voz-v3`) segue sem validação com modelo de verdade; a DC5, que compara a voz do jogo com a
  `voz-v4b`, tem o plano APROVADO e a validação (DC5c) ainda não rodou. E o decodificador de hoje não conhece o `olhar`: ele falha alto num
  motivo com essa unidade (seção 4).

## 1. De onde vem e o que já existe

| peça | onde está | o que serve aqui |
|---|---|---|
| **a percepção da tela** | o corpo da P1b (`ConfigTela`): os receptores `tela_<canal>` (o nível de cada um dos sete canais) e `novidade_tela` (a soma das partes adaptadas); o susto no salto de volume (`salto_volume`) e o estresse acima do corte de volume e movimento | o susto, a habituação e a novidade, já no corpo |
| **o gosto** | a P1d: o `GenomaVisao` (o ótimo e a largura por canal, rng `visao-ovo`), o agrado em pico contra o alvo aprendido, o `agrado_inato`, o deslocamento da exposição; o canal `gosto_visual` no r da consequência | o pico de agrado e a distância ao esperado |
| **o motivo de cada decisão** | `digilab/digibrain/adapt.py`: com a subchave `olhar`, o motivo ganha o campo `olhar` (as telas à vista, a que o pet olhava, o `agrado`, o `agrado_inato`, o termo `gosto`) e, na consequência, o agrado e o `gosto_visual` | a entrada do decodificador, sem tocar o cérebro |
| **o decodificador de conceitos** | `digilab/digibrain/decodificador.py` (`dec-v1`, `dec-v2`) e o espelho `web/app/motor/digibrain/decodificador.ts`, com paridade | o molde: função pura, inteiros na escala S, falha alto, pesos e limiares PROPOSTOS na `ConfigDecodificador` |
| **a fala pela rede** | `web/app/src/falaRede.ts` (`conceitosDaVoz`), `web/app/src/falaLivre.ts` (a fala espontânea, hoje com intervalo mínimo de 20 s, `INTERVALO_ESPONTANEA_MS`), `servidor/` | a ponte conceito → LLM → texto, o teto de gasto e o log de apresentação |
| **a regra da fala** | `servidor/CLAUDE.md` | "a fala nunca entra no registro do pet"; o teto de gasto total; a fala livre aprovada só com o `gemma2:9b` local |
| **o P0** | `web/app/src/gostoVisual/` | a captura, o vetor de sete números por segundo e o descarte do quadro; ligado por padrão no jogo (D-GV-PADRAO-1), com a captura só no clique |

## 2. O caminho A (DECIDIDO): o comentário nasce do sinal do pet

### 2.1 A cadeia

```
TV ou tela → 7 números (o quadro e o áudio descartados) → corpo (receptores, adaptação, susto)
          → cérebro (agrado, novidade, olhar) → motivo → decodificador (conceitos do assistir)
          → [limite de frequência] → LLM (conceito + espécie + humor) → frase
```

e **nunca** `tela → LLM → frase`. É a mesma regra da `docs/futuro/decodificador_conceitos.md`, seção 1: a LLM não decide nada e não
inventa estado que o decodificador não mostrou.

### 2.2 Os conceitos do assistir (todos PROPOSTOS, SEM FONTE nos limiares)

Cada conceito tem valor e confiança em [0, S], como os 12 de hoje. Só vira fala um conceito acima do limiar dele, e só enquanto o pet olha
(a TV em `olhar.olhava`).

| conceito | o sinal que o acende | a frase de exemplo | limiar PROPOSTO |
|---|---|---|---|
| **`gostei`** | o pico de agrado: o `agrado` do que o pet olha acima de um limiar alto | "gostei disso" | `agrado ≥ 3S/4` |
| **`de_novo`** | o agrado alto num programa que o pet já tinha olhado antes e voltou a passar | "de novo!" | o mesmo de `gostei`, mais o programa já visto (FA-3) |
| **`susto`** | o salto brusco de som: o susto do corpo subindo no tick, pelo `salto_volume` de hoje. O salto de **brilho** não existe no corpo hoje (FA-4) | "ai!" | o susto subiu desde a decisão anterior |
| **`chato`** | a habituação: o `novidade_tela` baixo enquanto o pet ainda olha, com o tédio subindo | "que chato…" | `novidade_tela ≤ S/8` e tédio em alta, por algumas decisões seguidas |
| **`o_que_e`** | a distância grande do esperado: o `novidade_tela` alto e o agrado perto de zero (o nível fora da largura do pico em vários canais) | "o que é isso?" | `novidade_tela ≥ S/2` e `agrado ≤ S/8` |

- **A intenção do comentário** é um conceito só, o de maior valor entre os ativos, com a ordem do catálogo no empate, como a regra I-a do
  `dec-v1`. O susto vence os outros quando ativo (ele é o único que pede resposta imediata). PROPOSTO.
- **A incerteza manda na frase:** com confiança baixa, a voz fala em dúvida ("acho que gostei"), como na `decodificador_conceitos.md`,
  seção 1. O limiar de confiança é PROPOSTO.
- **Os limiares vêm dos dados da GV3**, não destes exemplos: a run descritiva mostra a distribuição do agrado e do `novidade_tela` nos
  pets, e só então os limiares se fixam, na calibração (FA-2). Daí "depois da GV3".

### 2.3 O que a LLM recebe e o que não recebe

- **Recebe:** o nome do conceito (de um catálogo fechado), a palavra de confiança ("certo" ou "acho"), a espécie (o estilo da espécie que a
  voz já usa) e o humor em palavras (o `bem_estar` e o `mal_estar` do decodificador de hoje, sem número).
- **Recebe também, com o órgão (seção 10):** o conceito que o órgão percebeu (de uma lista fixa), com a palavra de confiança, e o agrado, a
  novidade e a habituação que a rede calculou sobre esse conceito, em palavras.
- **Não recebe:** o quadro, o áudio, os sete números, o agrado em número, o nome do programa nem a fonte (`tv` ou `tela`). Dois motivos:
  - **a GV-10:** nada da captura vai ao servidor local, à LLM ou à rede; só os números ficam no log local. O conceito não é dado da
    captura: é um rótulo do estado do pet;
  - **o espírito da D-MM-8**, aqui por analogia (a D-MM-8 é da cooperação: a pontuação sem número na tela): a fala mostra o pet, não um
    número para o dono otimizar.
- **A consequência, sem o órgão:** o pet não diz o que está passando ("que gato fofo"). Ele diz o que sentiu do que viu, como a seção 12
  da `gosto_visual_pet.md` responde: o pet gosta das características, não do sentido.
- **Com o órgão (seção 10):** o pet diz o que está passando **até onde o órgão dele percebeu**: "um gato!" quando o órgão reconheceu gato
  com confiança, "acho que é um gato" com confiança baixa, e nada sobre o que a lista do órgão não tem. A LLM pode escolher as palavras
  (sem léxico, decisão de 2026-11-11), mas não pode acrescentar conceito que o órgão não deu.

### 2.4 A gravação no modo livre

- **O que diz a regra:** o `CLAUDE.md` da raiz aceita o modo livre gravado (a LLM decide ao vivo, a saída entra no log como evento). O
  `servidor/CLAUDE.md` é mais estrito para a fala: o texto vai para o log de apresentação (`<save>.fala.jsonl`, `web/app/src/falaLivre.ts`)
  e **nunca** para o registro do pet; motivo, decisões e replay ficam só com o que o motor calcula.
- **A proposta (FA-6):** o comentário segue a regra da fala de hoje. A linha do log de apresentação leva o conceito, a confiança, o tick, a
  versão do decodificador e da voz, o modelo, a semente e o texto. O conceito se recalcula do log do pet pelo replay (o `sentido_tela` da
  tela real já está lá, pela GV-15), e um teste confere que o conceito gravado é o que o replay dá. O texto nunca volta ao pet.

### 2.5 O limite de frequência (PROPOSTO)

- **Um comentário a cada 5 minutos reais**, no máximo, por pet, e só enquanto ele olha. O susto pode furar o limite uma vez, com o seu
  próprio intervalo de 1 minuto. Os dois números são PROPOSTOS, SEM FONTE.
- **Por que não o intervalo de hoje:** a fala espontânea de hoje tem 20 s de intervalo mínimo e dispara por gatilhos raros (decidir,
  evoluir, lutar). A tela muda o tempo todo: com 20 s, seriam até 180 comentários por hora, e a fala vira legenda.
- **A medida do incômodo** fica para o teste com o Matheus (FA-5).

## 3. O caminho B (REJEITADO): a LLM, ou um modelo de visão na nuvem, olhando a tela

O que seria: mandar quadros da tela à LLM multimodal, ou a um modelo de visão na nuvem, e pedir um comentário "como o pet". Rejeitado pela
decisão do Matheus de 2026-11-11, pelas três razões que a proposta já dava. A diferença para o órgão da seção 10 não é haver visão
computacional: é quem percebe. No órgão, o reconhecimento é um sentido do pet, local, com lista fixa, que vira receptor e passa pelo
cérebro dele; no caminho B, a LLM lê dados de fora e fala por cima do pet.

- **O pet "saberia" o que não percebe.** Um comentário sobre o conteúdo ("que filme triste") que não passou por nenhum receptor do pet fala
  de algo que ele não registra, e a fala deixa de ser do pet. É o risco de explicação plausível e infiel que a
  `decodificador_conceitos.md` cita (Turpin et al. 2023, arXiv:2305.04388, pista, não verificada).
- **A opinião passa a ser da LLM.** O gosto do pet é o pico inato mais a exposição e a consequência (GV-3, GV-14). Um modelo que olha a tela
  traz o gosto dele, e o dono ouviria o gosto do modelo como se fosse do pet: o mesmo risco da seção 6 da `gosto_visual_pet.md`, por outra
  porta.
- **Quadros iriam para fora do computador** (ou para um modelo local, mas fora da função do vetor), contra a GV-10: o quadro nunca sai da
  função que calcula o vetor.

## 4. As dependências e o estado delas (conferido nos documentos em 2026-11-11)

| dependência | o estado | o que pede |
|---|---|---|
| **a GV3** | em curso, sem resultado: o plano `PLANO_ANALISE_V3_GOSTO_VISUAL.md` APROVADO pelo Matheus em 2026-11-11, a faixa 89101…89505 reservada, o código da P1e no PR #863 ainda sem merge (D-GV-P1e-12) | os limiares da seção 2.2 vêm da distribuição que ela mostrar |
| **a voz-v3**, a voz do jogo no `dec-v3` | **não validada com modelo de verdade.** A DC4 validou a `voz-v3b` no laboratório e fechou sem os gates (D-DC4D-2); o aviso de `docs/RESULTADO_V3_CONVERSA_DC4.md` diz que a voz-v3 continua não validada | a fala do assistir não pode herdar uma fidelidade que a voz não mostrou |
| **a DC5**, voz-v4 contra a voz do jogo | o plano `PLANO_ANALISE_V3_CONVERSA_DC5.md` APROVADO (2026-11-10); a calibração (DC5b) e a recalibração com a `voz-v4b` (DC5b2) feitas; o adendo da DC5c (a validação: voz do jogo × `voz-v4b`, com espécie e com a `verif-v8b`/`verif-v9b`) escrito; **a validação ainda não rodou** e não há `RESULTADO_V3_CONVERSA_DC5.md` | a voz que a DC5c aprovar é a que dá voz aos conceitos do assistir (FA-7) |
| **o decodificador** | o `dec-v1`/`dec-v2` (Python e TS) tem a lista fechada de sete comportamentos, sem o `olhar`: um motivo com a unidade de olhar **levanta erro** em `_validar` | uma versão nova do decodificador (FA-2), com paridade; o `dec-v1`/`dec-v2` não muda |
| **a P1f** | o motor TS com paridade está feito; a ligação do P0 ao cérebro (o `sentido_tela` gravado no registro do jogo e o painel lendo o cérebro) ficou de fora e pede uma versão de pet nova (D-GV-P1f-6) | sem ela, o pet do jogo não tem o motivo com `olhar` para decodificar |

A conferir na implementação: se os receptores da tela aparecem nas `urgencias` do M-AFETO com a chave ligada. Se aparecerem, o `_validar` de
hoje também falha por receptor desconhecido.

## 5. O custo (a conta à vista; premissas PROPOSTAS)

- **Com o `gemma2:9b` local**, o padrão do jogo e o único aprovado para a fala livre (`servidor/CLAUDE.md`): US$ 0. O custo é a GPU: uma
  chamada por vez, e a fala espontânea com chamada em curso é descartada (`falaLivre.ts`), o que já serve de limite.
- **Com o Claude Haiku** (opcional, `DIGILAB_PROVEDOR_LIVRE`):
  - **o dado:** a recalibração DC5b2 gastou US$ 0,064 em 384 falas, das quais 192 eram do braço H (`claude-haiku-5-5`); o braço G e o
    verificador rodaram no `gemma2:9b` local, sem custo (TAREFA_V3_CONVERSA_PET, DC5b2; artefato
    `artifacts_v3_conversa_dc5/calibracao_v4b/meta.json`);
  - **a premissa 1 (PROPOSTA):** todo o gasto foi do H, então uma fala do H custa US$ 0,064 / 192 ≈ **US$ 0,00033**;
  - **a premissa 2 (PROPOSTA):** um comentário do assistir custa o mesmo que uma fala da DC5. É provável que custe menos (um conceito só,
    sem histórico de conversa), mas não foi medido;
  - **a premissa 3 (PROPOSTA):** o limite da seção 2.5 bate sempre, ou seja, 12 comentários por hora de tela, mais até 60 sustos no pior
    caso;
  - **a conta:** 12 × 0,00033 ≈ **US$ 0,004 por hora de tela**; no pior caso com sustos, 72 × 0,00033 ≈ US$ 0,024 por hora;
  - **contra o teto:** o teto padrão do servidor é de US$ 2 total (`--limite-usd`); a US$ 0,004 por hora, dá cerca de 500 horas de tela. Uma
    chamada que passaria do teto cai no template (regra de hoje).
- **Nenhum número de custo vira resultado:** é estimativa de ordem de grandeza, sem artefato próprio, até a primeira medição.

## 6. O que não se faz

- Nenhum quadro, áudio, miniatura ou número da captura vai à LLM (GV-10).
- O comentário não muda o pet: nem o corpo, nem o cérebro, nem o gosto. O dono que responde ao comentário pelo chat só mexe no pet pelo
  catálogo fechado de ações, como hoje.
- Nenhum comentário sobre um conteúdo que o órgão do pet não percebeu. Sem o órgão (antes da seção 10), nenhum comentário sobre o
  conteúdo ("que gato", "que jogo").
- Nenhuma fala do assistir no cérebro A: ele não tem o `olhar`.
- Nenhum número de comentário em resultado sem artefato.

## 7. As decisões (FA-1 DECIDIDA; as outras PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **FA-1** | De onde nasce o comentário. | **DECIDIDA (Matheus, 2026-11-11): o caminho A**, o comentário nasce da percepção do pet: "Quero que os comentários tecidos venham da percepção do pet." Na segunda direção do mesmo dia, a percepção inclui o órgão que reconhece conceitos (seção 10), e não há léxico do pet. O caminho B rejeitado é a LLM, ou um modelo de nuvem, olhando a tela. | — (decidida). O custo registrado: sem o órgão, o pet não comenta o conteúdo e a fala pode parecer pobre; com ele, o pet só comenta o que a lista do órgão tem, e um reconhecimento errado vira fala errada (seção 10.7). |
| **FA-2** | Onde ficam os conceitos do assistir. | **Numa versão nova do decodificador (`dec-v4`, nome PROPOSTO)**, no Python primeiro, com o `olhar` no catálogo e os cinco conceitos novos, e o espelho TS com paridade bit a bit; os limiares na `ConfigDecodificador`, calibrados nos dados da GV3. O `dec-v1`/`dec-v2` não mudam. | Uma regra solta no TS, fora do decodificador, é mais rápida, mas não tem paridade nem fidelidade medida, e o "gostei" vira um enfeite sem ligação conferida com o agrado. Limiares fixados antes da GV3 podem deixar o pet calado ou falando sem parar. |
| **FA-3** | O `de_novo` precisa de memória do programa. | **Fora da primeira versão;** só os quatro conceitos que o sinal de agora sustenta (`gostei`, `susto`, `chato`, `o_que_e`). O `de_novo` entra depois, lendo a memória autobiográfica, se ela registrar o olhar. | Com ele desde o início, o decodificador lê um estado que hoje não existe (o programa já visto) e o conceito fica sem base. Sem ele, perde-se a frase mais "de pet" da lista. |
| **FA-4** | O susto pela mudança brusca de brilho. | **Não na primeira versão:** o susto só do salto de volume, que o corpo de hoje tem. O susto de brilho só se o corpo ganhar o emissor, atrás de sub-chave, com o gabarito antes. | Fazer o decodificador falar de um susto de brilho que o corpo não registra é o pet "sabendo" o que não percebe, o defeito do caminho B por dentro. Sem o brilho, um corte de cena para o branco não assusta. |
| **FA-5** | O limite de frequência. | **Um comentário a cada 5 min reais, e o susto a cada 1 min, só enquanto o pet olha;** PROPOSTOS, ajustados uma vez num teste curto com o Matheus, com o número antes e depois no registro. | Curto demais, a fala vira legenda e cansa; longo demais, o dono não liga o comentário ao que viu. Ajustar o limite olhando o efeito que se quer medir contamina qualquer medida posterior. |
| **FA-6** | Onde o comentário é gravado. | **No log de apresentação da fala, como toda fala de hoje** (`servidor/CLAUDE.md`), com o conceito, a confiança, o tick, as versões, o modelo e a semente; o conceito se refaz do log do pet pelo replay, e um teste confere. | Gravar o texto no registro do pet contraria a regra da fala e abre a porta para o texto realimentar o pet. Não gravar o conceito impede de auditar se a frase saiu do sinal. |
| **FA-7** | Qual voz dá voz ao conceito. | **A que a DC5c aprovar** (a voz do jogo ou a `voz-v4b`), com um bloco novo de conceitos do assistir numa versão nova da voz; até lá, frases de template por conceito, sem LLM. | Ligar a fala do assistir na voz-v3, que não tem validação, empilha uma fala nova sobre uma voz que nunca mostrou fidelidade. Esperar a DC5c atrasa a parte com LLM, mas o template já mostra se o conceito acende na hora certa. |
| **FA-8** | Como se confere que a frase é fiel ao conceito (os do assistir e, com o órgão, os percebidos). | **O verificador da DC5 estendido aos conceitos do assistir e uma marcação cega curta do Matheus**, com plano de análise próprio (`PLANO_ANALISE_V3_*`) antes da primeira fala, e sem mostrar a ele os resultados de outro marcador antes da amostra dele. | Sem conferência, a LLM enfeita ("adorei as cores!") e afirma o que o conceito não diz. Uma rodada grande demais custa tempo do Matheus por uma fala curta. |

## 8. Riscos

- **O comentário parecer vazio.** Quatro conceitos repetidos cansam. Mitigação: a variedade da voz da DC5, o limite de frequência e a
  incerteza na frase; a medida da repetição que a DC5 já tem.
- **O conceito acender por ruído.** Um limiar baixo faz o pet "gostar" de tudo. Mitigação: os limiares calibrados nos dados da GV3, o
  genoma vazio como controle (nele, o `gostei` não deveria separar pets).
- **O dono ler o "gostei" como prova de gosto.** O pet diz "gostei" pelo agrado, que inclui a exposição ao que o dono mostrou. Mitigação: o
  painel da GV-14 (o inato, a exposição e a consequência separados) segue sendo onde o gosto se lê; a fala não é medida.
- **A privacidade por inferência.** O comentário não leva número, mas o padrão de comentários no log de apresentação revela quando a tela
  esteve ligada. Mitigação: o log de apresentação fica no navegador, como hoje, e a revisão de privacidade da GV5 inclui ele.
- **O custo escapar.** Mitigação: o teto de gasto total do servidor, o limite de frequência e o `gemma2:9b` como padrão.
- **A alegação de novidade.** Mitigação: as regras do topo.
- Os riscos próprios do órgão estão na seção 10.7.

As decisões do órgão são a FA-9 a FA-13, na seção 10.6 (a numeração continua a desta tabela, sem prefixo novo).

## 9. As etapas

| etapa | o quê | depende de | código |
|---|---|---|---|
| **FA0** | esta proposta revisada; as FA-2 a FA-8 decididas pelo Matheus | a GV3 (os limiares) | não |
| **FA1** | o decodificador novo no Python (o `olhar` no catálogo, os conceitos do assistir, os limiares na `ConfigDecodificador`), com testes e o `dec-v1`/`dec-v2` byte a byte | FA0; a P1d na `main` | sim |
| **FA2** | o espelho TS com paridade bit a bit, e a fala por template no jogo atrás de chave desligada, com o limite de frequência e a gravação da FA-6 | FA1; a ligação do P0 ao cérebro (D-GV-P1f-6) | sim |
| **FA3** | a voz: um bloco de conceitos do assistir na voz que a DC5c aprovar, numa versão nova; o verificador estendido | FA2; a DC5c | sim |
| **FA4** | o plano de análise da fidelidade (FA-8), commitado antes da primeira fala; a rodada curta; o resultado | FA3 | run |

## 10. O órgão da visão (e do ouvido) — PROPOSTO

Pedido do Matheus de 2026-11-11 (a segunda direção do topo). **Vem depois da GV3:** a GV3 em curso continua só com os quatro números da
visão e os três do som. **Nenhum código antes da revisão do Matheus.** Todo número desta seção é PROPOSTO; os nomes dos modelos são
exemplos de tipo, e os tamanhos, as licenças e o desempenho deles ficam **SEM FONTE** até a busca da 10.8.

**O vocabulário:** o órgão **reconhece** rótulos de uma lista com uma confiança. "Compreender o que passa nos pixels" é o desejo do
Matheus; o que o desenho entrega é reconhecimento por lista fixa, e o documento não diz mais que isso.

### 10.1 O que é

- **Um módulo de visão computacional dedicado,** um órgão do pet, que transforma o quadro em **conceitos com uma confiança em inteiros**
  em [0, S]. Exemplos de lista (PROPOSTA, FA-10): na visão, `gato`, `cachorro`, `pessoa`, `rosto`, `comida`, `carro`, `jogo`, `texto`; no
  som, `musica`, `fala`, `risada`, `latido`.
- **Fica ao lado dos números de hoje:** os quatro da visão (cor, brilho, movimento, complexidade) e os três do som passam a ser a
  **"retina"** e a **"cóclea"**, o nível baixo; o órgão é o nível do reconhecimento. Os dois seguem para o corpo, separados.
- **O quadro continua descartado** dentro da função, como na `gosto_visual_pet.md`, 2.3: dele saem só os sete números e os pares (conceito,
  confiança) acima de um corte.

### 10.2 Onde roda: local, no navegador (a recomendação, FA-9)

- **Na visão:** um modelo pequeno de vocabulário aberto, do tipo CLIP, SigLIP ou MobileCLIP, que casa o quadro reduzido contra a lista
  fixa de conceitos (a similaridade entre a imagem e o texto de cada conceito; os vetores de texto calculados uma vez, na carga da lista).
- **No som:** um classificador do tipo YAMNet, treinado nas classes do AudioSet, com as classes dele agrupadas nos conceitos da lista.
- **O motor de inferência:** ONNX Runtime Web (WebGPU, com WASM de reserva) ou transformers.js. A escolha é da espec, depois da busca.
- **A confiança em inteiros:** a pontuação do modelo (um float) vira um inteiro em [0, S] por uma regra fixa na borda do órgão (por
  exemplo, faixas de similaridade calibradas na lista). Dentro do pet, só entra o inteiro.
- **Nada sai da máquina.** Nenhum quadro, áudio, vetor do modelo ou conceito vai à rede, ao servidor local ou à LLM como dado da captura.
- **A alternativa rejeitada: um modelo de visão na nuvem.** É o caminho B por outra porta: quadros sairiam do computador (contra a GV-10), e
  cada quadro teria custo por chamada.
- **Uma ressalva sobre a GV-10:** a GV-10 recomenda guardar "só os quatro inteiros". O órgão guarda mais: pares (conceito, confiança). É
  estado derivado mais revelador (um `rosto` ou um `texto` frequentes dizem o que o usuário faz). A regra "nada sai da máquina" fica
  intacta, mas o que fica no log local muda, e isso entra na revisão de privacidade da GV5 (FA-10, FA-11).

### 10.3 A G-RECEPTOR: percepção do pet, não a LLM lendo dados de fora

- O cérebro do Digilab só lê receptores (a G-RECEPTOR do M-SENS). O órgão entrega os conceitos ao **corpo**, como o mundo entrega hoje a
  intensidade dos sete canais pelo `sentir_tela`; o corpo tem um receptor por conceito da lista (por exemplo `ver_gato`, `ouvir_risada`;
  nomes PROPOSTOS) com a sua adaptação, no molde do órgão da tela da P1b.
- **O conceito é percepção do próprio pet,** pelo órgão dele. A LLM continua só como voz: recebe o conceito percebido, a confiança em
  palavra, e o agrado, a novidade e a habituação que a rede calculou sobre ele, também em palavras (seção 2.3).
- A LLM não acrescenta conceito: o verificador (FA-8) confere que a fala só cita conceitos que o órgão entregou naquela janela.

### 10.4 O cérebro: os conceitos como estímulo no M-SENS

- **Os conceitos entram como estímulo no M-SENS,** lidos dos receptores do órgão, ao lado dos da tela.
- **O gosto, a novidade e a habituação passam a valer por conceito:** o pet pode gostar de `gato` e enjoar de `texto`.
  - **a habituação** por conceito é a adaptação do receptor dele no corpo (o molde da GV-18);
  - **a exposição** desloca um traço por conceito, como o alvo aprendido da P1d desloca o de cada canal;
  - **a consequência** de olhar segue o canal do corpo de hoje (o P1 do M-PLAST, a GV-8): o que o pet olhava com `gato` na tela, antes de um
    carinho, ganha crédito.
- **O inato por conceito** (um pet que nasce gostando mais de bichos) é a FA-12. Sem ele, o gosto por conceito nasce neutro e é todo
  aprendido.
- **A fala** ganha conceitos do assistir com alvo: o `gostei` com o alvo `gato`, o `chato` com o alvo `texto`, o `o_que_e` quando a
  confiança de todos os conceitos está baixa e a novidade alta (o pet viu algo que o órgão não reconhece).
- **O custo no corpo:** um receptor e um químico de adaptação por conceito. Com uma lista de 30 conceitos, são 30 químicos novos além dos 14
  da tela (a GV-18 já citava o custo do tick).

### 10.5 O determinismo e a pesquisa

- **O órgão é acaso do ponto de vista do motor:** o mesmo quadro pode dar uma confiança diferente em outra GPU, em outro navegador ou em
  outra versão do modelo. Por isso a saída do órgão é **gravada no log no modo livre**, como a da LLM: um evento novo (por exemplo
  `percepcao_tela`, `fonte|conceito:confianca|…`, PROPOSTO), com a versão do modelo e da lista, e o replay lê o evento. Um evento mal
  formado, sem a chave ou com conceito fora da lista levanta erro.
- **O Python lê o fluxo gravado.** Nenhum modelo entra no `digilab/` (só biblioteca padrão): o motor Python só conhece o evento.
- **Para as runs e a paridade, a TV do jogo usa um catálogo de cenas com conceitos fixos por script, sem modelo.** Cada programa da grade
  (`tv-programas`) ganha, além do perfil de sete números, uma lista de (conceito, confiança) por cena, fixa no script. É determinístico,
  serve para resultado e para a paridade Python/web, como a TV do jogo de hoje.
- **O modo livre não vale para resultado** (a regra do `CLAUDE.md`): o que o órgão reconhece na tela real nunca entra numa medida.
- **O tamanho do log:** o evento só na mudança, dentro do resumo de 10 s da GV-15, com no máximo os k conceitos mais confiantes (k = 3,
  PROPOSTO). A conta do tamanho é da espec.

### 10.6 As decisões do órgão (FA-9 a FA-13, todas PROPOSTAS)

A numeração continua a da seção 7, sem prefixo novo.

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **FA-9** | Local × nuvem. | **Local, no navegador**, com um modelo pequeno de vocabulário aberto na visão e um classificador do tipo YAMNet no som, por ONNX Runtime Web (WebGPU) ou transformers.js. A nuvem rejeitada. | Na nuvem, quadros saem do computador (contra a GV-10), cada quadro custa, e o pet passa a depender de rede. Local, o custo é o peso do modelo no navegador e a GPU dividida com o `gemma2:9b`; se o modelo for pesado demais, o órgão tem de amostrar menos (FA-11). |
| **FA-10** | A lista de conceitos: o tamanho e quem escolhe. | **Uma lista fixa e curta** (da ordem de 20 conceitos na visão e 8 no som, PROPOSTO), versionada, **escolhida pelo Matheus** a partir de uma proposta da espec; nenhum conceito que identifique pessoa (só `pessoa` e `rosto` como categorias, nunca quem é) nem que leia o texto (só `texto` como categoria). | Uma lista aberta (o dono escreve conceitos) devolve ao pet o gosto do dono (a GV-3) e abre conceitos sensíveis. Uma lista longa dilui a confiança do vocabulário aberto e enche o corpo de químicos. Curta demais, o pet "não identifica nada", que é a queixa do Matheus. Trocar a lista depois muda o evento e o gabarito. |
| **FA-11** | A taxa de amostragem. | **Uma classificação a cada 2 s reais** (PROPOSTO), resumida no evento de 10 s da GV-15, só quando o conjunto de conceitos muda. | Mais rápido, o órgão disputa a GPU com a fala e o log cresce. Mais lento, o pet perde o que passa rápido (um gato que aparece por 3 s). A taxa também é privacidade: quanto mais densa, mais o log revela do uso do computador. |
| **FA-12** | Se o órgão entra no genoma (a acuidade por pet) e se há gosto inato por conceito. | **Fora da primeira versão:** o mesmo órgão e o mesmo corte de confiança para todos os pets, e o gosto por conceito todo aprendido. Depois, se a run mostrar que serve, uma seção própria do genoma com rng própria (o corte de confiança por pet e um viés inato por grupo de conceito), como o `GenomaVisao`. | Com a acuidade desde o início, a diferença entre pets mistura o que eles percebem com o que eles gostam, e a medida genoma × dono perde a leitura. Sem ela, todos os pets enxergam igual, o que pode parecer pouco individual. |
| **FA-13** | Se os conceitos aparecem no painel. | **Sim, em palavras e sem número** (no espírito da D-MM-8): "viu: gato, pessoa"; "gosta de: gato"; "enjoou de: texto"; com o inato, a exposição e a consequência separados como na GV-14. | Com número, o painel convida o dono a otimizar o gosto do pet. Sem o painel, o dono não tem como saber se o "um gato!" saiu do órgão ou da LLM, e a confiança na fala cai. |

### 10.7 Os riscos do órgão

- **O reconhecimento errado vira fala errada.** Um modelo de vocabulário aberto erra, sobretudo em telas (texto, interface, desenho).
  Mitigação: o corte de confiança, a fala em dúvida com confiança baixa, a lista curta, e a medida de acerto no catálogo de cenas antes da
  tela real.
- **Os vieses do modelo viram o "olhar" do pet.** O que o modelo reconhece melhor o pet "vê" mais. Mitigação: a busca (10.8) inclui os
  vieses conhecidos, e o painel separa o que foi percebido do que foi gostado.
- **A privacidade do estado derivado** (10.2): `rosto` e `texto` frequentes no log local. Mitigação: as FA-10 e FA-11, e a revisão da GV5.
- **A máquina:** a inferência na GPU disputa com o `gemma2:9b` e, nas medições, com o combate. Mitigação: o órgão só no jogo, nunca numa
  run de pesquisa (as runs usam o catálogo por script).
- **O determinismo entre máquinas:** o mesmo quadro dá outra confiança noutra GPU. Mitigação: o evento gravado (10.5); nenhuma paridade
  sobre a saída do modelo.
- **A licença e o peso do modelo** (SEM FONTE até a busca). Mitigação: a busca antes da espec, e o modelo escolhido registrado com a
  licença e o sha256.
- **O escopo:** o órgão é uma frente grande. Mitigação: as etapas da 10.9, cada uma com PR próprio, e nada antes da GV3.

### 10.8 A busca a fazer antes de fechar (no vault DigiLab Research)

Nenhuma alegação de novidade: agentes e robôs com reconhecimento de objetos que alimenta motivação e linguagem existem, e a busca serve
para dizer o que já existe, não para achar uma lacuna. Pelas regras da nota `BUSCA_GOSTO_VISUAL_2026-11-10.md` (DOI e resumo conferidos,
com os rótulos [sem resumo] e [resumo parcial]), em seis trilhas:

1. **A classificação de vocabulário aberto:** CLIP, SigLIP e MobileCLIP (as fontes primárias, o tamanho, a licença e o acerto em conteúdo de
   tela e em classes curtas);
2. **O som:** YAMNet e o AudioSet (a fonte, as classes, a licença) e alternativas pequenas;
3. **A inferência no navegador:** ONNX Runtime Web, WebGPU e transformers.js (o desempenho em máquina comum, o determinismo entre GPUs);
4. **Os modos de falha e os vieses** da classificação de vocabulário aberto (texto na imagem que engana o modelo, vieses de categoria);
5. **O precedente de agente:** agentes ou pets virtuais com percepção de objetos ligada a motivação, habituação e fala ancorada (a
   linguagem ancorada na percepção); e o Creatures (Grand e Cliff, `10.1023/A:1010042522104`, já na tabela verificada) como ponto de partida
   do lado dos pets;
6. **A privacidade do reconhecimento no próprio aparelho** (o estado derivado; a continuação da seção 7 da `gosto_visual_pet.md`).

Até a busca, toda alegação desta seção sobre os modelos é SEM FONTE.

### 10.9 As etapas do órgão

| etapa | o quê | depende de | código |
|---|---|---|---|
| **OV0** | a busca da 10.8 no vault e as referências conferidas | — | não |
| **OV1** | a espec do órgão (a lista, a regra da confiança, o evento, os receptores, o M-SENS por conceito); as FA-9 a FA-13 decididas pelo Matheus | OV0; a GV3 | não |
| **OV2** | o Python atrás de chave desligada: o catálogo de cenas com conceitos fixos na TV do jogo, os receptores e a adaptação por conceito, o M-SENS por conceito, o evento gravado; o gabarito das vidas de hoje antes, num commit próprio | OV1 | sim |
| **OV3** | o web com paridade no catálogo de cenas; o órgão no navegador (o modelo local) gravando o evento no modo livre | OV2; a FA2 | sim |
| **OV4** | a fala com os conceitos percebidos (a voz da FA-7, o verificador da FA-8) e o painel da FA-13; a revisão de privacidade da GV5 incluindo o órgão | OV3 | sim |

### 10.10 Os conceitos do Digimundo — PROPOSTO

Pedido do Matheus de 2026-11-11 (a terceira direção do topo). O órgão, além dos conceitos genéricos da 10.1, reconhece **as espécies do
Digimundo**, e cada uma traz um **sentido mítico** da mitologia do jogo. O reconhecimento vira, pelo menos, um estado do pet. Tudo PROPOSTO,
SEM FONTE no desenho; nada antes da GV3 e da revisão do Matheus.

#### 10.10.1 A origem dos conceitos: o corpus das espécies

- **O arquivo:** `digilab_fala_livre/corpus_especies.json` (versão `corpus-auditado-1`, 60 espécies, as do jogo, `web/app/motor/nomes.ts`),
  lido pelo `digilab_fala_livre/corpus.py`. O carregador tira as espécies sem nenhuma obra apta e filtra cada item pela marca da auditoria.
- **O que o carregador deixa entrar, ao pé da letra** (o docstring e o `_entra` do `corpus.py`):
  - `VERIFICADO` e `VERIFICADO EM OUTRA FONTE`, só de obras com veredito `APTO` ou `APTO COM RESSALVAS`;
  - `PARCIAL` só reescrito na auditoria (`"reescrito": true`);
  - `OUTRA MIDIA` só anime e só com `meta.liberar_outra_midia` (liberado pelo Matheus em 2026-09-30, segundo a `meta` do arquivo);
  - fora: `INFERENCIA`, `DIVERGENTE`, `SEM FONTE`, `FONTE INVALIDA`, e o texto com letra fora do alfabeto latino.
- **O que sai hoje** (conferido com `corpus.carregar()` em 2026-11-11, sha256 do arquivo começando por `785f7834a2ee`; sem artefato gravado,
  é uma contagem do arquivo versionado): **56 espécies** de 60; entram 219 traços, 117 jeitos de falar, 106 interações e 62 citações; ficam
  fora 23 `INFERENCIA`, 9 `OUTRA MIDIA`, 5 `PARCIAL` e 1 `SEM FONTE`.
- **A diferença com o pedido da coordenação** ("só VERIFICADO e VERIFICADO EM OUTRA FONTE"): o carregador também deixa entrar `PARCIAL`
  reescrito e anime. A FA-14 decide qual dos dois filtros vale para o órgão.
- **O conceito é a espécie** (o nome, como `Agumon`). Os itens do corpus não viram conceito: eles alimentam o sentido mítico (10.10.3) e o
  estilo da voz, como já alimentam hoje, e **não sustentam afirmação** (a regra do `bloco_estilo`).
- **Uma lacuna:** o Piedmon (o deus da Diversão, D-MM-4) e o Myotismon (o termômetro fora do aro), que a MITOLOGIA já usa, **não estão**
  entre as 56 espécies do corpus. Pô-los na lista do órgão pede uma entrada nova no corpus, auditada, ou uma exceção (FA-15).

#### 10.10.2 Como o órgão reconhece: as imagens de referência e o som

- **Na visão:** além do texto com o nome, o órgão compara o quadro com **imagens de referência de cada espécie: os sprites do atlas** (os do
  Digimon UP, autorizados pelo Matheus, `docs/UI_GUIDELINES.md`, 5.1). Os vetores das imagens de referência são calculados no computador do
  usuário. **As imagens e os vetores ficam locais, fora do git** (FA-16).
- **No som:** os **nomes falados** ("Agumon!"), por um reconhecimento de fala local (do tipo Whisper; tamanho, licença e acerto em português
  e japonês SEM FONTE). Só o casamento com a lista fechada dos nomes sai da função, com a confiança em inteiros; **a transcrição é descartada
  na hora**, como o quadro (FA-17).
- **O limite de estilo:** o anime desenha as espécies de um jeito, os sprites de outro (pixel art pequena). Um órgão de referência por sprite
  pode não reconhecer o Agumon do anime. **Isso precisa ser medido:** uma bateria local, fora do git, com quadros de sprite e quadros de
  anime por espécie, e o acerto do órgão em cada um, em separado, antes de o órgão valer na tela real. É risco (10.10.6) e medida (na OV2;
  o plano da fala, que nesta fase não usa modelo, não mede isso).

#### 10.10.3 O sentido mítico: uma mitologia só, a da MITOLOGIA

- **Cada espécie ganha um sentido mítico,** combinado com a frente MITOLOGIA (`docs/TAREFA_V3_MITOLOGIA.md` e as D-MM-1 a D-MM-18). **Não
  se cria outra mitologia:** o sentido sai do que a MITOLOGIA já tem, isto é, os cinco deuses do aro (Coragem, Amizade, Conhecimento,
  Sinceridade e a Diversão, o macaco, encarnada pelo Piedmon, D-MM-4), o Myotismon fora do aro e a lenda do macaco sob a montanha.
- **A forma PROPOSTA:** cada espécie aponta para um deus (o "patrono") e, no máximo, para uma frase do Códice. O mapa é desenho, SEM FONTE,
  escrito pela frente MITOLOGIA e decidido pelo Matheus (FA-15). Os traços do corpus podem orientar o mapa (um traço de coragem verificado
  puxa para a Coragem), mas o mapa não é um fato do corpus e não pode ser dito como fato da obra.
- **A fala da MITOLOGIA espera o G-NATURAL da DC5** (D-MM-11, `TAREFA_V3_MITOLOGIA.md`, seção 6). O sentido mítico na fala do assistir
  segue a mesma espera.

#### 10.10.4 O reconhecimento vira um estado no afeto, não no corpo

- **A D-MM-10, no texto que os documentos dão:** "nenhuma correção mexe nos stats da luta nem no corpo" (`docs/TAREFA_V3_COOPERACAO.md`;
  `docs/futuro/kant_cooperacao.md`). Ela foi escrita para as correções morais; a COOPERACAO a aplicou à culpa e à inveja, que ficaram no
  M-AFETO pela valência (CO7-6, K-4). **Aqui ela vale por analogia**, não pela letra: a crença mítica é da mesma família, e a recomendação é
  tratá-la do mesmo jeito.
- **O desenho PROPOSTO:**
  - o órgão tem o receptor de cada espécie (é o sentido, a G-RECEPTOR da 10.3), mas **sem emissor químico** e sem adaptação química: o
    reconhecimento de uma espécie não mexe no tédio, no humor nem em nada do corpo;
  - o reconhecimento entra no **M-AFETO como um termo de valência**, com o sinal e o peso dados pelo sentido mítico (o patrono e o que o
    pet já viveu com o sinal daquele deus, nos eventos da MITOLOGIA); o peso é PROPOSTO, SEM FONTE;
  - a habituação ao reconhecimento fica no M-SENS (a habituação por classe, PE-11), não no corpo.
- **A consequência:** os conceitos genéricos da 10.4 mexem no corpo pela tela; os do Digimundo não. Um Agumon na TV muda o estado afetivo
  do pet sem virar química, e a D-MM-10 não reabre (FA-18).

#### 10.10.5 O painel e a pesquisa separam percepção e crença

- **No painel** (sem número, FA-13): "viu: Agumon" (a percepção do órgão, com a confiança em palavra) numa linha; "acredita: Agumon é do
  deus da Coragem" (a crença mítica) noutra. Nunca as duas numa frase só.
- **Na fala:** a percepção pode ser dita como percepção ("é o Agumon!"); a crença só como crença ("dizem que ele é da Coragem", "acho que
  isso é sinal da Coragem"). A crença dita como fato conta como sem sustento (FA-19).
- **Na pesquisa:** as medidas separam o que vem do órgão e o que vem do mito, por braço (`docs/PLANO_ANALISE_V3_GOSTO_VISUAL_FALA.md`).

#### 10.10.6 Os riscos próprios

- **O estilo do anime contra o dos sprites** (10.10.2). Mitigação: a bateria de acerto separada por estilo, e a confiança baixa dita como
  dúvida.
- **O mito dito como fato da obra.** Mitigação: a separação da 10.10.5 e a rubrica.
- **Os direitos das imagens.** Os sprites são autorizados para o jogo (UI_GUIDELINES 5.1); os quadros de anime da bateria não são, e ficam
  locais, fora do git, nunca publicados.
- **A fala ouvida do usuário.** O reconhecimento de fala ouve o que o usuário fala ou assiste. Mitigação: a lista fechada de nomes, a
  transcrição descartada na hora, e a FA-17 adiando o som.
- **Duas mitologias.** Mitigação: o mapa é da frente MITOLOGIA (FA-15).

#### 10.10.7 As decisões novas (FA-14 a FA-20)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **FA-14** | O filtro do corpus que vale para o órgão. | **A lista de conceitos é a das espécies que o `carregar()` deixa entrar (56 hoje); o sentido mítico só se apoia nos itens `VERIFICADO` e `VERIFICADO EM OUTRA FONTE`** (o filtro estrito, sem `PARCIAL` reescrito nem anime). | Com o filtro do carregador inteiro, o mito pode se apoiar num texto reescrito ou de anime que a auditoria só aceitou para o tom. Com o filtro estrito também na lista, espécies sem item estrito somem do órgão sem razão de percepção. |
| **FA-15** | Quem faz o mapa espécie → sentido mítico, e o Piedmon e o Myotismon. | **A frente MITOLOGIA escreve o mapa, um patrono por espécie, só com os deuses que ela já tem; o Matheus decide.** O Piedmon e o Myotismon entram na lista do órgão só com uma entrada nova no corpus, auditada como as outras. | Feito aqui, nasce uma segunda mitologia. Sem o Piedmon e o Myotismon, o pet não reconhece justamente os dois que a mitologia mais usa; com uma exceção sem auditoria, o corpus perde a regra. |
| **FA-16** | As imagens de referência. | **Só os sprites do atlas, com os vetores calculados no computador do usuário, locais e fora do git;** nenhum quadro de anime como referência. Os quadros de anime só na bateria de medida, locais. | Com quadros de anime na referência, o repositório ou o pacote do jogo carrega imagem sem autorização. Só com sprites, o órgão pode falhar no anime, e é por isso que a bateria mede. |
| **FA-17** | Os nomes falados no som. | **Depois da visão,** num passo próprio, com a revisão de privacidade da GV5: reconhecimento de fala local, só o casamento com a lista fechada, a transcrição descartada na hora. | Junto com a visão, o órgão ouve a fala do usuário antes de a privacidade da imagem estar revista. Sem o som, o pet não reconhece o "Agumon!" do anime, só o desenho. |
| **FA-18** | Onde o reconhecimento mexe no pet. | **No M-AFETO, pela valência, com o sinal do sentido mítico; nenhum emissor no corpo** (a D-MM-10 por analogia). | No corpo, reabre a D-MM-10 e mexe na química das vidas com a chave ligada. Sem estado nenhum, o reconhecimento vira só palavra, contra o "pelo menos como um estado" do pedido. |
| **FA-19** | Como a crença aparece na fala e no painel. | **Separada da percepção, sempre; a crença dita como crença; a crença dita como fato conta como sem sustento.** | Juntas, o dono lê o mito como o que o pet viu, e a fidelidade da fala não se mede. |
| **FA-20** | O braço de pesquisa ("Vamos testar um braço da pesquisa com isso"). | **Sim, pelo `docs/PLANO_ANALISE_V3_GOSTO_VISUAL_FALA.md`, sem modelo de visão,** com a TV do jogo e um catálogo de cenas roteirizadas; o plano aprovado pelo Matheus antes de qualquer fala. | Testar com o órgão de verdade mistura a pergunta da fala com o acerto do modelo e não é repetível. Sem o braço, o órgão entra no jogo sem saber se melhora a fala. |
