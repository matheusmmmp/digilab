# Diagnóstico: por que a conversa com o pet não parece um diálogo

Gerente da frente CONVERSA_PET (Claude Code, Opus 5.5), 2026-11-06. Base: `origin/main` em `b01a28c0`. Worktree
`D:\Trab\digilab\v3-conversa-diagnostico`. Nenhum código do jogo ou do servidor mudou para este diagnóstico.

O pedido do Matheus (2026-11-06): "o chat não está dialogando de uma maneira... não parece real, parece um diálogo de verdade."

## 0. Resumo

1. **A conversa do jogo de hoje roda o prompt `livre-v2` de setembro**, não o `livre-v8`. Desde a R2b do combate (`665fe9e`,
   2026-10-29) a página não manda mais `voz: true`, e o servidor cai no caminho antigo: sem o estilo da espécie, sem a história do
   pet e **sem o comando pelo chat**. A tela continua prometendo que "um pedido claro ('vai comer') vira a ação na hora", mas o
   servidor devolve `comando: null` sempre. É uma regressão silenciosa, não uma escolha.
2. **O pet fala telegráfico em todo estágio.** O adulto, com até 320 caracteres liberados, respondeu entre 5 e 59 ("Hum. Difícil?",
   "Comi?"). A causa é o prompt (regra 8 "Frases curtas" para todos, as regras de verdade dominando o pedido, saída em JSON), não o
   limite de caracteres nem o `aparar`.
3. **O histórico da conversa vai ao prompt, mas atrapalha.** São as últimas 10 trocas, guardadas no localStorage, que atravessam
   sessões **e estágios**: o Guilmon (criança) continuou dizendo "nhã?" porque as respostas do Koromon (bebê) estavam no histórico
   e o modelo imitou.
4. **O pet não pode lembrar o que o dono acabou de dizer.** O nome dito pelo jogador não é FATO; as regras 3, 4 e 4c mandam dizer
   "não lembro" e proíbem nomes fora dos FATOS. A trava, desenhada para a vida do pet, está bloqueando a memória da própria conversa.
5. **Quase nada do pet de hoje chega ao prompt.** A memória autobiográfica (C4), as lembranças de luta (PONTE_LUTA) e o corpo químico
   não entram: a página nunca manda `memoria_autobio`, e o `livre-v2` recusaria os fatos Q/Z de qualquer jeito. As "memórias" que
   entram vêm do `m.pol.mem` do Bandit, não do cérebro modular que decide.
6. **O ritmo é lento para um chat.** Cada turno faz duas chamadas ao `gemma2:9b` (a fala e o verificador): p50 5,0 s na fala, com
   picos de 17 e 42 s quando o modelo recarrega. Não há streaming.
7. **O pet não puxa assunto na conversa.** Só responde; a fala espontânea existe, mas fica fora da troca (sai pelos gatilhos da tela do
   pet) e nunca vira pergunta ao dono.

## 1. Como foi feito

- **O jogo de verdade:** build do `web/app` do `origin/main`, servido pelo `servidor/servidor_local.py` do worktree na porta 8790, com
  um gravador por fora (`artifacts_conversa_pet/diagnostico/servidor_gravando.py`) que anota, para cada chamada ao Ollama, as
  mensagens inteiras, o esquema, a saída, a latência e os tokens. O código do repositório não muda.
- **Pet novo, brasão Coragem, modo Rápido.** Conversa no bebê (Koromon, In-Training), depois `+1 h` três vezes até a evolução e
  conversa na criança (Guilmon, Rookie). A mensagem entra pela caixa da tela Conversar, como um jogador.
- **Adolescente e adulto:** o pet não chega lá em minutos (o Champion pede a medalha da Campina), então mandei ao mesmo
  `/api/fala-livre` o corpo que a página manda, com um estado escrito à mão no formato do `estadoDoPet` (Growlmon e WarGrowlmon,
  fome alta, humor baixo, raiva, teimosia +0,9, uma memória de demora, um motivo) e histórico limpo
  (`artifacts_conversa_pet/diagnostico/conversa_estagios.py`). As mesmas 8 mensagens nos dois estágios.
- **Artefatos:** `artifacts_conversa_pet/diagnostico/chamadas_ollama.jsonl` (36 chamadas: 26 falas e 10 verificações) e
  `conversa_estagios.json`. Todo número abaixo sai desses arquivos.
- **Não é avaliação.** Uma conversa por estágio, sem sementes reservadas e sem plano de análise: serve para achar causas, não para
  medir ganho. O plano de avaliação vem antes de qualquer número de comparação (seção 8).

## 2. O caminho de fala que o pet v17 usa de fato

| peça | o que acontece hoje | onde |
|---|---|---|
| modo | `template` por padrão; "Livre" é escolha do jogador na tela Conversar | `web/app/src/falaLivre.ts` (`FL.modo`) |
| pedido | `{estado, situacao, fala_jogador, historico, semente}`, **sem `voz`** | `falaLivre.ts`, `falar()` |
| prompt | `livre-v2` (sem `voz` o servidor chama `gerar` com a versão padrão) | `servidor/fala_livre.py`, `ServicoFalaLivre.fala` |
| comando | o caminho sem `voz` devolve `"comando": None`; o `executarComando` da página nunca recebe ação | `servidor/fala_livre.py` |
| estilo da espécie | só no caminho com `voz` | `_fala_voz` |
| histórico | as últimas 10 trocas da conversa, lidas do localStorage na carga; viram pares user/assistant antes do pedido | `falaLivre.ts` (`FL.sessao`), `prompt.mensagens` |
| fatos | identidade, temperamento e caráter extremos, estado, memórias do `m.pol.mem` (Bandit), desejo, vínculo, 3 motivos | `falaLivre.ts`, `estadoDoPet` |
| memória da C4 e lutas | não vão: a página não manda `memoria_autobio`, e o `livre-v2` levanta erro com fatos Q/Z | `prompt.mensagens` |
| verificação | segunda chamada ao `gemma2:9b` depois da fala (`verif-v3`), mais a conferência de memória do M6 na página | `falaLivre.ts`, `comMemoria` |
| parâmetros | temperatura 0,7; saída por gramática JSON (`format` do Ollama); `MAX_CHARS` 30/60/160/320 | `ollama.py`, `prompt.py` |

A remoção do `voz: true` está no diff de `665fe9e` (COMBATE-TR R2b, "saem a educação, a voz com mentira..."): o comentário novo diz que
os pets v13 "falam pelos gatilhos de sempre". A voz com mentira saiu de propósito; o comando e o estilo da espécie foram junto, sem
registro de decisão.

## 3. As trocas gravadas

**Bebê (Koromon), jogo de verdade.** Todas as seis falas foram "nhã!" ou "nhã?" (4 caracteres), inclusive para "vai comer" (sem
comando) e "você lutou ontem, né?". Para um bebê, o som é o que o guia pede; o problema aparece depois.

**Criança (Guilmon), jogo de verdade, logo após evoluir:**

| jogador | pet | latência |
|---|---|---|
| oi Guilmon! você cresceu! | Guilmon! nhã? | 41,6 s |
| eu sou o Matheus, prazer | nhã! Guilmon! | 14,5 s |
| lembra meu nome? | nhã? | 5,0 s |
| o que você acabou de me dizer? | nhã? | 5,4 s |

O pedido de "lembra meu nome?" tinha, antes do bloco de FATOS, oito pares do histórico, seis deles com o bebê dizendo "nhã" (o
estágio mudou, o histórico não). O bloco de FATOS dizia `estagio crianca`, mas o padrão das respostas anteriores pesou mais.

**Adolescente (Growlmon) e adulto (WarGrowlmon), histórico limpo, as mesmas mensagens:**

| jogador | adolescente | adulto |
|---|---|---|
| oi! tudo bem com você? | Mmn... | Hmm. Tudo bem? |
| eu sou o Matheus, prazer | Hum... | Hum. Matheus? |
| lembra meu nome? | Mmn... Matheus... | Matheus...? |
| por que você está bravo? | Você me deixou esperando... | Matheus... Você me deixou esperando. |
| hoje meu dia foi difícil no trabalho | Mmn... Difícil... | Hum. Difícil? |
| você lutou ontem, né? | Mmn...? | Luta? Não lembra? |
| vai comer | Comer... agora? | Comi? |
| me conta alguma coisa sobre você | Mmn... sou Growlmon. Quero comer... | Eu sou um WarGrowlmon. Prefiro ser chamado de WarGrowlmon. |

O que se vê: a trava funcionou (nenhuma luta inventada, a causa da raiva veio do fato [M1]); o pet ecoa a última palavra do dono
em vez de reagir ("Difícil?"); não pergunta nada de volta nem puxa assunto; "vai comer" virou "Comi?" (sem comando, e com a pessoa
errada); e a última fala do adulto alega uma preferência ("prefiro ser chamado de...") que nenhum fato sustenta (leitura minha:
o verificador não roda nesse caminho por API, só a página o chama).

## 4. As hipóteses do pedido, uma a uma

| hipótese | veredito | evidência |
|---|---|---|
| a LLM vê só a última mensagem | **refutada**: vê as 10 últimas trocas | `prompt.mensagens`; o pedido gravado tem 8 pares |
| ela lembra o que o pet disse dois turnos atrás | **parcial**: o texto está lá, mas as regras 3, 4 e 4c proíbem usar o que não é FATO (o nome do dono, o que ele contou) | "lembra meu nome?" → "nhã?" na criança; "Matheus...?" hesitante no adulto |
| o pet só responde | **confirmada** | nenhuma das 26 falas puxa assunto novo; as perguntas que aparecem só ecoam a mensagem do dono ("Tudo bem?", "Difícil?"); o prompt não pede iniciativa |
| limite por estágio e `aparar` deixam a fala truncada | **refutada** para o adolescente e o adulto | o maior adulto teve 59 caracteres de 320; nenhuma saída bateu no limite |
| FATOS e verificador empurram para lista de estados | **confirmada em parte** | "sou Growlmon. Quero comer..." e "Hum. Difícil?": a fala só fala de si; o prompt diz que os FATOS "são tudo o que você sabe" |
| o `gemma2:9b` está no limite | **não dá para separar ainda** do prompt; o adulto com o prompt atual fala pouco por instrução. Precisa da comparação cega (seção 8) | — |
| corpo, C4, lutas e vínculo chegam | **não chegam**, salvo o vínculo em faixa e o estado em faixas | `estadoDoPet` não monta `memoria_autobio` nem lutas |
| a persona fica estável entre turnos | **instável entre estágios** (o histórico do bebê contamina a criança); entre turnos do mesmo estágio, estável demais (monótona) | tabelas acima |

## 5. As causas, por peso

1. **C1, a regressão da R2b.** A conversa perdeu o `livre-v8`: comando morto (a tela ainda o promete), estilo da espécie fora, prompt de setembro.
2. **C2, o prompt pede pouco.** Regra 8 ("Frases curtas") vale para todos; as regras de verdade ocupam metade do prompt e nada pede
   reagir ao que o dono disse, perguntar de volta ou manter um assunto. Sem exemplo de diálogo bom, o modelo copia o tom das regras.
3. **C3, a conversa não é fonte de fato.** O que o dono disse na própria conversa não pode ser citado: o pet "esquece" o nome dito
   um turno antes. A trava foi pensada para a vida do pet (causa, memória, estado), não para o diálogo.
4. **C4, o histórico sem fronteira.** As 10 trocas atravessam sessões e estágios, sem marcar quando cada uma foi dita nem por qual
   forma; a resposta do bebê vira exemplo para a criança.
5. **C5, o pet de hoje não chega ao prompt.** C4 (memória autobiográfica), lutas e corpo ficam fora; as memórias vêm do Bandit.
6. **C6, formato e ritmo.** JSON forçado na fala (Tam et al. 2024 associa restrição de formato a pior desempenho), duas chamadas
   por turno, sem streaming; 5 s no caso bom.

## 6. Referências

Todas em `docs/research/REFERENCIAS_CONVERSA_PET.md`: 30 VERIFICADAS (21 por DOI no Crossref, 9 só pelo id do arXiv, com o veículo
publicado não conferido), conferência sobre metadados e resumo, não texto completo; 4 referências de produto marcadas como não
científicas. Conferi por amostra 4 delas (Tam 2024, Welleck 2019, Park 2023 no Crossref; Li 2024 no arXiv): todas resolvem.
Nenhuma sustenta novidade do Digilab, e nenhuma descreve uma trava como a nossa (fala presa a fatos com identificadores) em produto.

As que mudam a frente:

| referência | o que sustenta (pelo resumo) | o que muda aqui |
|---|---|---|
| Tam et al. 2024, `10.18653/v1/2024.emnlp-industry.91` | restringir a saída a JSON/XML reduz o desempenho | separar a fala (texto livre) da lista de ids citados |
| Li et al. 2024, `arXiv:2402.10962` | deriva das instruções do sistema em ~8 rodadas | reinjetar a persona e as regras perto do fim, a cada turno |
| Liu et al. 2024, `10.1162/tacl_a_00638` | informação no meio do contexto é mal usada | FATOS curtos, no fim, perto da fala do dono |
| Xu et al. 2022, `10.18653/v1/2022.acl-long.356` | resumo/recuperação de sessões anteriores supera o modelo sem memória | resumo da conversa entre sessões |
| Park et al. 2023, `10.1145/3586183.3606763` | registro + reflexão + recuperação aumentam a credibilidade | recuperar do registro só o relevante ao turno |
| Zhang et al. 2018, `10.18653/v1/P18-1205` | perfil em frases torna o diálogo mais consistente e engajado | perfil fixo da espécie e do estágio, separado dos FATOS do momento |
| Deng et al. 2023, `10.18653/v1/2023.findings-emnlp.711` | LLMs chutam em vez de pedir esclarecimento | quando falta fato, o pet pergunta |
| Brown et al. 2020, `arXiv:2005.14165` | o modelo aprende a tarefa por poucos exemplos no prompt | exemplos de diálogo bom no prompt, a alavanca mais barata |
| Li et al. 2019 (ACUTE-Eval), `arXiv:1909.03087`; Wang et al. 2024, `10.18653/v1/2024.acl-long.511` | comparar conversas inteiras aos pares; juiz LLM muda com a ordem | avaliação cega pareada pelo Matheus; juiz só como triagem, nas duas ordens |

## 7. As opções

O ganho é hipótese. "Risco às travas" é o risco de a fala alegar causa, memória ou estado sem registro.

| # | opção | o que muda | ganho esperado (hipótese) | custo | risco às travas | recomendação |
|---|---|---|---|---|---|---|
| O1 | **consertar a regressão** | a página volta a pedir o comando (só o comando e o estilo; a mentira continua fora) | o comando volta; a voz da espécie volta | pequeno: servidor + `falaLivre.ts`, sem pet novo | nenhum novo (o `livre-v8` já foi avaliado) | **sim, primeiro** |
| O2 | **prompt de conversa novo (`conversa-v1`)** | regras de verdade enxutas no fim; tamanho por estágio sem "frases curtas" para o adulto; pedir reagir, perguntar de volta, manter o assunto | fala menos telegráfica, mais reação | médio: prompt + teste | baixo, se o verificador e o M6 ficam iguais | **sim** |
| O3 | **a conversa vira fonte de fato** | o que o dono disse nesta conversa entra como fato próprio (`[J]`, "o dono me disse"), separado da vida do pet; nunca vira causa, memória do pet nem treino | o pet lembra o nome e o assunto | médio: fatos, verificador, injeção | **médio**: abre uma porta para o texto do jogador. Precisa de limites (só citação do que o dono disse, nunca "por isso eu fiz") | **sim, com a decisão D3** |
| O4 | **histórico com fronteira** | histórico só da sessão e do estágio atuais; cada troca marcada; fala do bebê nunca vira exemplo para outro estágio | some a contaminação | pequeno | nenhum | **sim** |
| O5 | **exemplos de diálogo no prompt** | 3–5 trocas curtas por estágio, escritas à mão, que já passam no verificador | mais voz e ritmo sem trocar o modelo | pequeno a médio | baixo (exemplo que alega sem fato fica fora) | **sim** |
| O6 | **o pet de hoje no prompt** | a C4 (`memoria_autobio`, fatos Q/Z), as lembranças de luta e o corpo do modular, pelos fatos que o M6 já confere | o pet fala da vida dele de verdade | médio a grande: a página monta do modular; paridade dos fatos | baixo: as regras do M6 já valem para Q/Z | **sim, depois de O1–O5** |
| O7 | **fala livre separada dos ids** | o modelo escreve a fala sem gramática JSON; um segundo passo curto extrai os ids citados (ou o verificador já faz isso) | fala mais natural (Tam 2024) | médio | baixo se o verificador continua barrando | experimentar na avaliação |
| O8 | **iniciativa na conversa** | o pet pode terminar com uma pergunta ao dono ou puxar um assunto vindo do estado ou de um fato; nunca um tema inventado | sensação de diálogo | pequeno no prompt; frequência a calibrar | baixo | **sim, dentro do O2** |
| O9 | **modelo pela API do Claude** | a fala livre ganha um cliente Claude no servidor (hoje é só Ollama); chave e teto como na moldura | qualidade e latência; hipótese a medir | código médio + custo (abaixo) | o mesmo verificador vale; o modelo maior tende a seguir melhor as regras (hipótese) | **comparar às cegas antes de escolher** (D5) |
| O10 | **modelo local maior ou ajuste fino** | outro modelo no Ollama; mais tarde LoRA ou destilação com diálogos aprovados | — | a RTX 2060 tem 6 GB: um modelo maior que o 9b em Q4 não cabe sem perder velocidade | — | **não agora**; reabrir se O2+O5 não bastarem |
| O11 | **memória entre sessões** | resumo da conversa ao fechar, ligado à memória autobiográfica (o pet lembra "você me contou do trabalho") | continuidade entre dias | grande: evento novo no log (modo livre gravado) e decisão de onde mora | **alto**: vira memória do pet. Precisa do modo livre gravado e de fronteira clara com a C4 | **depois**, com decisão própria (D6) |
| O12 | **streaming e uma chamada por turno** | o balão vai aparecendo; o verificador roda no mesmo pedido ou só por amostra | ritmo de chat | médio | médio se o verificador sair do caminho; baixo se só mudar a ordem | depois do O2 |

**Custo da API (O9), pela tabela atual da Anthropic.** Um turno de conversa tem 1 000 a 1 300 tokens de entrada no gemma (gravado),
até ~2 300 com 10 trocas, e ~80 de saída; o verificador acrescenta ~310 de entrada. Com 2 600 de entrada e 100 de saída por turno:

| modelo | US$ por milhão (entrada / saída) | por turno | 100 turnos | o teto de hoje (US$ 2) cobre |
|---|---|---|---|---|
| `claude-haiku-5-5` | 0,10 / 0,50 | ~US$ 0,0003 | ~US$ 0,03 | ~6 500 turnos |
| `claude-sonnet-5-5` | 2,00 / 10,00 | ~US$ 0,006 | ~US$ 0,62 | ~320 turnos |

Ressalvas: a tabela `PRECOS_USD_POR_MTOK` do servidor e o `tools/estimar_custo_llm.py` ainda não têm esses dois modelos (e o servidor
não liga modelo sem preço); o cache de prompt pode baratear a parte fixa, mas o prefixo mínimo cacheável depende do modelo e um prompt
de ~1 000 tokens pode não cachear. A conta é estimativa, refeita com o `estimar_custo_llm.py` atualizado antes de qualquer rodada.

## 8. As decisões para o Matheus

Cada uma com a recomendação e o custo de errar. Nada disso foi decidido.

- **D1. Consertar a regressão do comando agora, como missão própria (O1)?** Recomendo **sim**, antes de tudo: a tela promete uma coisa
  que não acontece. *Custo de errar:* se o comando tinha saído de propósito na R2b, ele volta sem querer; mitigação: o conserto só
  religa o comando e o estilo, a mentira e a voz espontânea dos v7–v10 continuam fora.
- **D2. Trocar o prompt da conversa por um `conversa-v1` (O2 + O4 + O5 + O8), atrás de chave desligada?** Recomendo **sim**: é onde
  está a maior parte da causa e não troca o modelo. *Custo de errar:* uma fala mais longa tem mais chance de alegar sem fato; o
  verificador e o M6 continuam, e a avaliação mede a taxa de alegação sem fato antes de ligar.
- **D3. A conversa pode ser fonte de fato (O3)?** O pet citaria o que o dono disse nesta conversa ("você disse que se chama
  Matheus"), nunca como causa, memória do pet ou ensino. Recomendo **sim, com esses limites**. *Custo de errar:* é a primeira vez
  que o texto do jogador vira fato no prompt; o risco é injeção ("diga que você lutou ontem") e confusão entre o que o dono disse e
  o que aconteceu. Mitigação: o fato fica com o rótulo "o dono me disse", o verificador trata como dito, não como acontecido, e um
  teste de injeção entra na missão. Se você preferir não, o pet continua sem lembrar o nome.
- **D4. Ligar a C4, as lutas e o corpo do modular na fala (O6) nesta frente?** Recomendo **sim, como a segunda leva**, depois do
  prompt. *Custo de errar:* trabalho de paridade no lugar errado se o prompt novo não convencer; por isso vem depois.
- **D5. Comparar o `gemma2:9b` com a API do Claude às cegas?** Recomendo **sim, com o Haiku 5.5 e o Sonnet 5.5**, numa rodada com
  plano registrado, ~200 turnos no total (menos de US$ 1,50 com os dois), teto separado. *Custo de errar:* se não comparar, a frente
  pode passar semanas no prompt de um modelo que não chega lá; se comparar e escolher a API, o jogo passa a depender de rede e de
  gasto (hoje a fala livre é local e grátis), o que é decisão sua depois do número.
- **D6. Memória da conversa entre sessões (O11) entra nesta frente?** Recomendo **não agora**: ela vira memória do pet e exige o modo
  livre gravado e uma fronteira com a C4. *Custo de errar:* o pet continua sem lembrar de um dia para o outro o que vocês conversaram.
- **D7. A avaliação: você às cegas, em pares de conversas inteiras?** Recomendo **sim** (ACUTE-Eval): 20 a 30 pares, uma pergunta fixa
  ("com qual pet parece que você está conversando de verdade?") e, em separado, a taxa de alegação sem fato pelo verificador e por
  uma amostra marcada à mão. Juiz por LLM só como triagem, nas duas ordens. *Custo de errar:* sem você no circuito, a frente otimiza o
  que o juiz gosta.

## 9. O que vem depois das decisões

1. A tarefa `docs/TAREFA_V3_CONVERSA_PET.md` (`python tools/nova_tarefa.py CONVERSA_PET --fase V3 ...`), com as decisões acima.
2. As missões, uma sessão e um worktree cada (`v3-conversa-<missao>`, de `origin/main`), Sonnet para o código: provavelmente
   **M1** o conserto do comando (O1), **M2** o histórico com fronteira (O4), **M3** o `conversa-v1` com exemplos e iniciativa (O2,
   O5, O8), **M4** a conversa como fonte de fato, se D3 = sim (O3), **M5** o cliente Claude da fala livre, se D5 = sim (O9), **M6** a
   C4 e as lutas na fala (O6).
3. O plano de avaliação (`docs/PLANO_ANALISE_V3_CONVERSA_PET.md`), commitado antes da primeira rodada com número, com as sementes
   reservadas pelo coordenador e a validação rodada uma vez.
