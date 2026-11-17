# PLANO DE ANÁLISE V3 — CONVERSA_PET, F2: a espera da voz no jogo (2026-11-17, Gerente das cinco frentes, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus** (2026-11-17, no chat da sessão da Gerente das cinco frentes). A pergunta foi "Aprova as cinco como recomendadas, ou quer discutir alguma?", e a resposta, "Aprovo". As decisões D-ES-1 a D-ES-3 (seção 7) ficam DECIDIDAS como recomendadas; a D-ES-4 continua para depois da medida.

**O papel:** uma medida descritiva do produto, sem gate. Ela não é uma run de pesquisa da bancada: não tem vida do Python, não tem
resultado sobre o pet e não tem paridade. Ela serve à escolha da saída para a espera (seção 6).

**De onde vem:**
- a síntese de 2026-11-16 (vault, `SINTESE_REFS_2026-11-16.md`, seção 1, "Latência da voz local" e "Verbalizar no tempo morto");
- a DC4, que mediu a latência por turno fora do jogo: p50 de 15,6 s no G e 11,4 s no H (`latencia_turno_s`, PR #750).

O levantamento das saídas, com as fontes, está no vault: `DigiLab — Revisão de escopo/LEVANTAMENTO_ESPERA_VOZ_2026-11-17.md`.

## 0. O que existe hoje (lido na `main` `a794c3ae`)

FATO VERIFICADO:
- **A fala chega inteira.** A voz pede JSON com esquema e `"stream": False` (`digilab_fala_livre/ollama.py:53`). Hoje, a primeira
  palavra e a frase inteira chegam juntas.
- **O verificador não segura a fala.** Ela aparece na hora, e o aviso chega depois (`web/app/src/falaLivre.ts:156-162`). Então **a espera
  que o jogador sente é a da voz.** O verificador atrasa o aviso e disputa a GPU com a chamada seguinte.
- **Uma chamada por vez.** A conversa entra na fila, e a espontânea que chega com uma chamada em curso é descartada
  (`falaLivre.ts:121-123`). A espontânea respeita um intervalo de 20 s (`falaLivre.ts:27`).
- **O que precisa estar ligado.** A voz pela rede só fala com o modo "livre" e com a chave `FALA_REDE`, e as duas vêm desligadas por
  padrão (`falaLivre.ts:49-51`). A medida liga as duas.
- **O registro da fala é de apresentação,** separado do registro do pet (`falaLivre.ts:3`, `:53-64`). Medir o tempo não toca o replay.
- **A linha de base fora do jogo** (calibrações da DC5, a tabela do levantamento no vault): a voz do G tem p50 de 6,4 a 7,3 s, e a do H
  de 1,4 a 1,5 s; o turno com o verificador fica entre 10 e 13 s no p50.

## 1. As medidas

Todas são do relógio de parede, pelo `performance.now()` da página, por turno.

| | o que se mede | de quando a quando |
|---|---|---|
| **T1, a primeira palavra** | a espera até o jogador ver algo do pet | do envio da frase do jogador até o balão aparecer |
| **T2, a frase inteira** | a espera até a fala completa | igual ao T1 hoje (sem streaming); fica separado para comparar com uma saída de streaming |
| **T3, o aviso** | o atraso do ⚠ ou do "Sem base" | do balão até a verificação chegar |
| **T4, a fila** | quanto a conversa esperou outra chamada | do envio até a chamada da voz sair (a espontânea ou a verificação em curso) |
| **T5, a espontânea** | quantas se perdem | as espontâneas descartadas ÷ as disparadas, e o pedido → balão das que saem |

- **Por medida:** o p50, o p95 e a fração acima do limite L, com o n.
- **Uma curva descritiva** da fração acima de 2, 5, 8 e 15 s.
- **O p95 com o N da seção 2** é o 114.º de 120 valores ordenados. O relato dá os valores vizinhos, porque o p95 de 120 é instável.

## 2. O desenho

- **O jogo de verdade:**
  - o build (`npm run build`) servido pelo servidor local, com o Ollama `gemma2:9b` na RTX 2060;
  - o verificador ligado, como o jogo vem (a verif-v8 e a verif-v9 do jogo, não as da DC5);
  - o modo livre e a `FALA_REDE` ligados;
  - um pet de teste modular semeado por uma página da mesma origem (a regra do `web/app/CLAUDE.md`), sempre o mesmo save.
- **Quem joga:** um teste Playwright no Chrome instalado, como o `npm run e2e`.
  - Ele abre a conversa, envia a frase, espera o balão e espera uma pausa fixa de 3 s antes de enviar a próxima (o tempo de ler; PROPOSTO,
    SEM FONTE).
  - O pet fica vivo durante a medida. As espontâneas acontecem como no jogo, e é isso que faz a fila do T4 aparecer.
- **O tamanho:** 20 conversas de 6 turnos, **120 turnos**. As frases são as dos roteiros da **calibração** da DC5
  (`experiments/configs/v3_conversa_dc5/roteiros_calibracao.json`, já públicos), em ordem fixa, repetidos na ordem até completar 20.
  - Os roteiros da validação da DC5 não são usados: eles ficam fechados até a DC5c.
  - N = 120 é PROPOSTO, SEM FONTE. O G leva cerca de 25 min, contando a pausa.
- **Frio e quente:** antes da primeira conversa, o modelo é descarregado (`keep_alive: 0`, o mesmo que o `ollama.py:73` já faz). A primeira
  conversa é relatada à parte (frio), e as 19 seguintes são o quente. Os números principais são os do quente.
- **O braço H (opcional, D-ES-3):** as mesmas 120 frases com `DIGILAB_PROVEDOR_LIVRE` no Claude Haiku. O verificador continua local.
- **O que fica gravado em `meta.json`:**
  - o nome e a VRAM da GPU (`nvidia-smi`);
  - o `ollama ps` no começo e no fim (quanto do modelo ficou na GPU e quanto na CPU);
  - a tag do modelo;
  - o sha256 do build e do servidor;
  - o commit.

## 3. O código (depois da aprovação, num PR próprio)

- **Uma medida desligada por padrão** em `web/app/src/falaLivre.ts`: com `?medir_espera=1` na URL, a página guarda os tempos do T1 ao T5
  numa lista na memória, que o teste lê. Nada vai para o log de apresentação nem para o registro do pet, o `VERSAO_LOG` não muda e, sem a
  chave, o jogo sai igual.
- **Um teste Playwright** em `web/app/e2e/`, que só roda à mão (precisa do Ollama). Ele grava `artifacts_v3_conversa_espera/<braco>/`
  com `turnos.jsonl` e `meta.json`.
- **Um script** que lê os artefatos e calcula os quantis, com o quantil em `digilab/metrics.py` se ainda não existir (a regra das métricas
  únicas). Os testes usam dados falsos.
- **Sem paridade Python × TS:** não é mecânica de jogo, e nada do motor muda.

## 4. A máquina

- **Uma medida por vez,** com no máximo 4 processos e nada mais no Ollama. A latência do G é a medida, e uma segunda carga a estraga.
- **Nunca junto com a validação da DC5c,** que usa o mesmo Ollama. A medida espera a DC5c terminar, ou roda antes dela, conforme a fila da
  Gerente da V3.
- Numa worktree própria, com `npm install` dentro dela (sem junção para o `node_modules` da v3).

## 5. A leitura e o que fica de fora

- **Descritiva.** O relato dá os números, compara com a linha de base fora do jogo e diz quanto a fila e a disputa da GPU somam.
- **O que este plano não afirma:**
  - nada sobre outra GPU, outro modelo ou o jogador de verdade: o roteiro é fixo e a pausa é fixa;
  - que uma espera é "aceitável". O limite L é uma referência para contar, não um alvo de UX com fonte;
  - nada sobre a fidelidade da fala. Isso é da DC5.

## 6. As saídas e a recomendação

O levantamento completo, com as fontes, está no vault. Em resumo:

| saída | o que resolve | o que custa | com o decodificador e o verificador |
|---|---|---|---|
| **pré-gerar** a fala logo depois da decisão da rede | a espontânea e a primeira fala ao abrir a conversa; **não** a resposta a uma frase do jogador | GPU ocupada a cada decisão, falas jogadas fora, prioridade da conversa na fila | a fala leva o id e o tick da decisão; uma decisão nova antes de mostrar descarta a fala; o verificador roda no tempo morto, então a fala chega verificada e uma trava (a P1 da F1) fica sem espera |
| **a API do Claude** como voz | a conversa: a voz cai para cerca de 1,5 s no p50 | cerca de US$ 0,00034 por fala, internet, uma chave, o estado do pet sai da máquina | a fidelidade do H com a voz do jogo sai da DC5d; o verificador local continua, sem pesar na espera de hoje |
| **streaming** com o verificador por frase | a primeira palavra, em tese | a fala vem dentro de um JSON e tem uma frase só, então o ganho é pequeno; mexe no cliente, no servidor e na página | mostrar antes de verificar derruba uma trava; com o aviso de hoje, funciona |
| **um modelo menor** para a voz | talvez a voz local | uma calibração e uma validação novas; o PacaPet, com 3B, ficou perto de 5,7 s de mediana; dois modelos disputam a VRAM | a fidelidade e a legibilidade tendem a cair (a DC4 já viu o G ler pior) |

**O precedente e o que ele não resolve** (GARP, texto completo, vault `LEITURA_GARP_2026-11-17.md`):
- o agente decide cerca de 20 s antes de a atividade acabar ("decisions taken ahead of need", p. 9), e o cache pelo hash do prompt
  permite o replay determinístico. Pré-gerar e cachear viram uma opção só, e o cache casa com o modo livre gravado, que já guarda a
  saída;
- o GARP não trata o estado que muda entre pré-gerar e mostrar: sem vazão, o agente só continua a atividade anterior (p. 10);
- **a regra proposta aqui:** se a decisão mudar antes de a fala aparecer, a fala pré-gerada é descartada, e o jogo volta ao que faz hoje
  (gera na hora, e o jogador espera como espera hoje). Uma fala de decisão velha nunca aparece.
- **Os números do GARP não servem de previsão:** os cerca de 13 s por geração e os 200 ms até a primeira palavra foram medidos num Apple
  M1 Max (p. 10), e os autores dizem que isso não estabelece a mesma vazão em outros aparelhos. Para a RTX 2060, vale só a medida desta
  F2.

**Atenção, a pré-geração muda quando a frase nasce.** Hoje a espontânea já nasce na decisão (o gatilho "acabei de decidir o que fazer",
`falaLivre.ts:177`). Pré-gerar estende isso à primeira fala da conversa e guarda a fala até ela ser mostrada. A intenção e os conceitos
continuam sendo os da decisão, e o que muda é o intervalo entre a decisão e a exibição. Por isso o registro grava os dois ticks, e uma fala
de uma decisão velha não aparece.

RECOMENDAÇÃO, para o Matheus decidir depois da medida: (1) a pré-geração; (2) a API como escolha em Ajustes, se a DC5d disser que o H é
fiel; (3) o streaming por último; (4) o modelo menor fora.

## 7. As decisões (DECIDIDAS pelo Matheus em 2026-11-17, todas como recomendadas)

- **D-ES-1, DECIDIDA pelo Matheus em 2026-11-17 como recomendada, aprovar a medida como está:** 120 turnos, os roteiros da calibração da DC5, a pausa de 3 s e o limite L = 8 s, com a curva de
  2, 5, 8 e 15 s. Recomendo sim.
  - **Custo de errar:** pequeno. É uma medida de tempo, e os números (N, pausa, L) só mudam a precisão.
  - **O L = 8 s** é PROPOSTO, SEM FONTE. É o prazo do PacaPet, usado só como referência de contagem.
- **D-ES-2, DECIDIDA pelo Matheus em 2026-11-17 como recomendada, a instrumentação fora do log:** a chave `?medir_espera=1`, só em memória, sem mudar o `VERSAO_LOG`. Recomendo sim.
  - **Custo de errar:** se a medida tiver de existir no jogo de verdade (com jogadores do beta), ela teria de ir para o log, e isso é outra
    decisão.
- **D-ES-3, DECIDIDA pelo Matheus em 2026-11-17 como recomendada, o braço H na medida:** as mesmas 120 frases com o Haiku, por cerca de US$ 0,04 pela conta de US$ 0,00034 por fala, dentro do
  teto da fala livre. Recomendo sim, depois da DC5c, para não disputar o teto.
  - **Custo de errar:** perto de US$ 0,04.
  - **A alternativa:** medir só o G, e a API fica com o número de fora do jogo.
- **D-ES-4, a saída:** fica para depois da medida, com a recomendação da seção 6.
