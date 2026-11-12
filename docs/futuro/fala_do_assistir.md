# A fala do assistir: o pet comenta o que vê na TV, pelo que ele percebe

Status (2026-11-11): **PROPOSTO**, com uma decisão já tomada. Só papel: nenhum código, nenhuma faixa, nenhuma vida, nenhum plano de
análise. A frente é a `docs/TAREFA_V3_GOSTO_VISUAL.md`. **Entra depois da GV3** (a run descritiva genoma × dono da
`docs/futuro/gosto_visual_pet.md`, seção 9, que é a P1e da `docs/ESPEC_GOSTO_VISUAL_P1.md`). A GV3 ainda não rodou: o plano
`docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md` está PROPOSTO e a run espera o ok do Matheus.

**A decisão do Matheus (2026-11-11), DECIDIDA:** "quero que siga o recomendado. Quero que os comentários tecidos venham da percepção do
pet" (ditado por voz; o "patch" do ditado é "pet"). Ficam decididos:
- **o caminho A** (seção 2): o comentário nasce da percepção do pet, isto é, do que ele vê pelos quatro números da visão e ouve pelos três
  do som, e do agrado, do interesse, da novidade e da habituação que a rede calcula. A LLM só dá voz ao conceito e nunca vê a tela;
- **o caminho B** (seção 3), um modelo de visão olhando a tela, fica **rejeitado**.

É a FA-1 (seção 7). Todo o resto deste documento continua PROPOSTO, inclusive o limite de frequência e o custo.

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
- **Não recebe:** o quadro, o áudio, os sete números, o agrado em número, o nome do programa nem a fonte (`tv` ou `tela`). Dois motivos:
  - **a GV-10:** nada da captura vai ao servidor local, à LLM ou à rede; só os números ficam no log local. O conceito não é dado da
    captura: é um rótulo do estado do pet;
  - **o espírito da D-MM-8**, aqui por analogia (a D-MM-8 é da cooperação: a pontuação sem número na tela): a fala mostra o pet, não um
    número para o dono otimizar.
- **A consequência:** o pet nunca diz o que está passando ("que gato fofo"). Ele diz o que sentiu do que viu. É o que a seção 12 da
  `gosto_visual_pet.md` já responde: o pet gosta das características, não do sentido.

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

## 3. O caminho B (REJEITADO): um modelo de visão olhando a tela

O que seria: mandar quadros da tela a um modelo multimodal e pedir um comentário "como o pet". Rejeitado pela decisão do Matheus de
2026-11-11, pelas três razões que a proposta já dava:

- **O pet "saberia" o que não percebe.** O pet só tem sete números por amostra. Um comentário sobre o conteúdo ("que filme triste") fala de
  algo que nenhum receptor dele registra, e a fala deixa de ser do pet. É o risco de explicação plausível e infiel que a
  `decodificador_conceitos.md` cita (Turpin et al. 2023, arXiv:2305.04388, pista, não verificada).
- **A opinião passa a ser da LLM.** O gosto do pet é o pico inato mais a exposição e a consequência (GV-3, GV-14). Um modelo que olha a tela
  traz o gosto dele, e o dono ouviria o gosto do modelo como se fosse do pet: o mesmo risco da seção 6 da `gosto_visual_pet.md`, por outra
  porta.
- **Quadros iriam para fora do computador** (ou para um modelo local, mas fora da função do vetor), contra a GV-10: o quadro nunca sai da
  função que calcula o vetor.

## 4. As dependências e o estado delas (conferido nos documentos em 2026-11-11)

| dependência | o estado | o que pede |
|---|---|---|
| **a GV3** | não rodou: o plano `PLANO_ANALISE_V3_GOSTO_VISUAL.md` PROPOSTO, a faixa 89101…89505 reservada, o orquestrador pronto e não executado (TAREFA_V3_GOSTO_VISUAL, resultado da P1e) | os limiares da seção 2.2 vêm da distribuição que ela mostrar |
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
- Nenhum comentário sobre o conteúdo ("que gato", "que jogo").
- Nenhuma fala do assistir no cérebro A: ele não tem o `olhar`.
- Nenhum número de comentário em resultado sem artefato.

## 7. As decisões (FA-1 DECIDIDA; as outras PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **FA-1** | De onde nasce o comentário. | **DECIDIDA (Matheus, 2026-11-11): o caminho A.** "Quero que os comentários tecidos venham da percepção do pet." O caminho B fica rejeitado. | — (decidida). O custo registrado: o pet nunca comenta o conteúdo, e o dono que espera "ele entende o filme" pode achar a fala pobre. |
| **FA-2** | Onde ficam os conceitos do assistir. | **Numa versão nova do decodificador (`dec-v4`, nome PROPOSTO)**, no Python primeiro, com o `olhar` no catálogo e os cinco conceitos novos, e o espelho TS com paridade bit a bit; os limiares na `ConfigDecodificador`, calibrados nos dados da GV3. O `dec-v1`/`dec-v2` não mudam. | Uma regra solta no TS, fora do decodificador, é mais rápida, mas não tem paridade nem fidelidade medida, e o "gostei" vira um enfeite sem ligação conferida com o agrado. Limiares fixados antes da GV3 podem deixar o pet calado ou falando sem parar. |
| **FA-3** | O `de_novo` precisa de memória do programa. | **Fora da primeira versão;** só os quatro conceitos que o sinal de agora sustenta (`gostei`, `susto`, `chato`, `o_que_e`). O `de_novo` entra depois, lendo a memória autobiográfica, se ela registrar o olhar. | Com ele desde o início, o decodificador lê um estado que hoje não existe (o programa já visto) e o conceito fica sem base. Sem ele, perde-se a frase mais "de pet" da lista. |
| **FA-4** | O susto pela mudança brusca de brilho. | **Não na primeira versão:** o susto só do salto de volume, que o corpo de hoje tem. O susto de brilho só se o corpo ganhar o emissor, atrás de sub-chave, com o gabarito antes. | Fazer o decodificador falar de um susto de brilho que o corpo não registra é o pet "sabendo" o que não percebe, o defeito do caminho B por dentro. Sem o brilho, um corte de cena para o branco não assusta. |
| **FA-5** | O limite de frequência. | **Um comentário a cada 5 min reais, e o susto a cada 1 min, só enquanto o pet olha;** PROPOSTOS, ajustados uma vez num teste curto com o Matheus, com o número antes e depois no registro. | Curto demais, a fala vira legenda e cansa; longo demais, o dono não liga o comentário ao que viu. Ajustar o limite olhando o efeito que se quer medir contamina qualquer medida posterior. |
| **FA-6** | Onde o comentário é gravado. | **No log de apresentação da fala, como toda fala de hoje** (`servidor/CLAUDE.md`), com o conceito, a confiança, o tick, as versões, o modelo e a semente; o conceito se refaz do log do pet pelo replay, e um teste confere. | Gravar o texto no registro do pet contraria a regra da fala e abre a porta para o texto realimentar o pet. Não gravar o conceito impede de auditar se a frase saiu do sinal. |
| **FA-7** | Qual voz dá voz ao conceito. | **A que a DC5c aprovar** (a voz do jogo ou a `voz-v4b`), com um bloco novo de conceitos do assistir numa versão nova da voz; até lá, frases de template por conceito, sem LLM. | Ligar a fala do assistir na voz-v3, que não tem validação, empilha uma fala nova sobre uma voz que nunca mostrou fidelidade. Esperar a DC5c atrasa a parte com LLM, mas o template já mostra se o conceito acende na hora certa. |
| **FA-8** | Como se confere que a frase é fiel ao conceito. | **O verificador da DC5 estendido aos conceitos do assistir e uma marcação cega curta do Matheus**, com plano de análise próprio (`PLANO_ANALISE_V3_*`) antes da primeira fala, e sem mostrar a ele os resultados de outro marcador antes da amostra dele. | Sem conferência, a LLM enfeita ("adorei as cores!") e afirma o que o conceito não diz. Uma rodada grande demais custa tempo do Matheus por uma fala curta. |

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

## 9. As etapas

| etapa | o quê | depende de | código |
|---|---|---|---|
| **FA0** | esta proposta revisada; as FA-2 a FA-8 decididas pelo Matheus | a GV3 (os limiares) | não |
| **FA1** | o decodificador novo no Python (o `olhar` no catálogo, os conceitos do assistir, os limiares na `ConfigDecodificador`), com testes e o `dec-v1`/`dec-v2` byte a byte | FA0; a P1d na `main` | sim |
| **FA2** | o espelho TS com paridade bit a bit, e a fala por template no jogo atrás de chave desligada, com o limite de frequência e a gravação da FA-6 | FA1; a ligação do P0 ao cérebro (D-GV-P1f-6) | sim |
| **FA3** | a voz: um bloco de conceitos do assistir na voz que a DC5c aprovar, numa versão nova; o verificador estendido | FA2; a DC5c | sim |
| **FA4** | o plano de análise da fidelidade (FA-8), commitado antes da primeira fala; a rodada curta; o resultado | FA3 | run |
