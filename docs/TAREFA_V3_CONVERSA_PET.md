# TAREFA V3 — CONVERSA_PET (2026-11-06)

Coordenador: Gerente da frente CONVERSA_PET (Claude Code, Opus 5.5). Worker: um por missão (seção 3). Worktree e branch: `v3-conversa-<missao>`,
criados de `origin/main` (enquanto o PR #618 não entra na `main`, de `origin/v3-conversa-diagnostico`, para a tarefa existir no branch).
Status: ABERTA. **D1 a D7 DECIDIDAS pelo Matheus em 2026-11-06, todas pela recomendação** (seção 8). Ordem das missões: leva 1 = M1, M3, M5;
leva 2 = M2, M4 (depois de M1 e M3); leva 3 = M6 (depois do prompt, D4).

Categoria: arquitetura. Origem: Matheus, 2026-11-06: "o chat não está dialogando de uma maneira... não parece real, parece um diálogo de verdade."

## 1. Pergunta

Como fazer a conversa com o pet parecer um diálogo de verdade (voz estável da espécie e do estágio, memória da conversa, reação ao que o
dono diz, iniciativa, ritmo) sem afrouxar a trava de que a fala só alega causa, memória e estado que o registro sustenta?

Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é frente de produto (`docs/PRODUTO_VISAO.md`), sobre a fala por LLM, que fica
fora do pacote do pet (`servidor/CLAUDE.md`).

**O diagnóstico** está em [docs/research/DIAGNOSTICO_CONVERSA_PET.md](research/DIAGNOSTICO_CONVERSA_PET.md), com as trocas gravadas no jogo
de verdade (`artifacts_conversa_pet/diagnostico/`). As causas, por peso:

1. **C1, regressão da R2b (`665fe9e`):** a página parou de mandar `voz: true`; a conversa voltou ao prompt `livre-v2` e perdeu o comando
   pelo chat (que a tela ainda promete) e o estilo da espécie.
2. **C2, o prompt pede pouco:** "frases curtas" para todo estágio, as regras de verdade dominando, nenhum pedido de reagir, perguntar ou
   manter o assunto. O adulto respondeu entre 5 e 59 caracteres de 320.
3. **C3, a conversa não é fonte de fato:** o pet não pode citar o que o dono disse um turno antes (o nome).
4. **C4, histórico sem fronteira:** as 10 trocas atravessam sessões e estágios; o "nhã" do bebê contaminou a criança.
5. **C5, o pet de hoje não chega ao prompt:** a memória autobiográfica (C4), as lutas e o corpo do modular ficam fora.
6. **C6, formato e ritmo:** JSON forçado na fala, duas chamadas por turno, p50 5,0 s e picos de 42 s, sem streaming.

**As referências** (30 verificadas, mais 4 de produto) estão em [docs/research/REFERENCIAS_CONVERSA_PET.md](research/REFERENCIAS_CONVERSA_PET.md).
Ainda não entraram em `docs/referencias/referencias_verificadas.csv`; isso fica para o PR de literatura da frente, se o Matheus quiser.

## 2. Depende de

- As decisões D1 a D7 do Matheus (seção 8).
- Nada de outra frente: a fala livre, o servidor e a tela Conversar estão na `main`. A M6 (abaixo) usa a C4 e a PONTE_LUTA, já na `main`.

## 3. Mudança mínima

PROPOSTA, depende das decisões. Uma missão por PR, cada uma num worktree próprio, Sonnet para o código.

| missão | o que muda | arquivos | depende de |
|---|---|---|---|
| M1 | religar o comando e o estilo da espécie na conversa (sem a mentira nem a voz espontânea dos v7–v10) | `servidor/fala_livre.py`, `web/app/src/falaLivre.ts` | D1 |
| M2 | histórico com fronteira: só a sessão e o estágio atuais, trocas marcadas | `web/app/src/falaLivre.ts`, `digilab_fala_livre/prompt.py` | D2 |
| M3 | prompt `conversa-v1`: regras enxutas no fim, tamanho por estágio, exemplos de diálogo, reação e iniciativa | `digilab_fala_livre/prompt.py`, testes | D2 |
| M4 | a conversa como fonte de fato rotulada ("o dono me disse"), com teste de injeção | `digilab_fala_livre/fatos.py`, `verificador.py`, `falaLivre.ts` | D3 |
| M5 | cliente Claude para a fala livre, com chave e teto como na moldura; preços dos modelos 5.5 na tabela | `servidor/`, `tools/estimar_custo_llm.py` | D5 |
| M6 | a C4, as lutas e o corpo do modular nos fatos da conversa | `web/app/src/falaLivre.ts`, `digilab_fala_livre/fatos.py` | D4 |

O que NÃO muda: o registro do pet (a fala nunca entra nele, salvo o comando pelo catálogo fechado e o evento de sempre), `digilab/engine.py`,
`digilab/`, as versões de pet, os gabaritos e a paridade. Toda mecânica nova fica atrás de chave desligada; desligada, a conversa de hoje sai
igual. O `livre-v2` e o `livre-v8` continuam no pacote e reproduzem.

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_CONVERSA_PET.md`, commitado antes de qualquer rodada com número.
- Sementes reservadas: calibração e validação pedidas ao coordenador da V3 e postas em `experiments/bancada/faixas.py` antes da rodada.
- Métrica e gate (PROPOSTOS): a preferência do Matheus em pares cegos de conversas inteiras (ACUTE-Eval) e a taxa de falas com alegação sem
  fato (verificador + amostra marcada à mão), que não pode subir em relação ao `livre-v2`.
- GPU: sim, o `gemma2:9b` na RTX 2060, uma rodada por vez, no máximo 4 processos.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a missão toca a web).
- Registro: seção própria no fim de `docs/registro/2026-11.md` e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`. O resumo da etapa
  vai no corpo do PR e numa seção no fim deste arquivo.
- PR contra a `main` com resumo e números (cada um com o artefato), relato conferido por
  `python tools/verificar_relato.py --arquivo <corpo> --base origin/main`. Merge só pelo Matheus.

## 6. Fora desta tarefa

- A memória da conversa entre sessões ligada à memória autobiográfica (O11 do diagnóstico), salvo decisão contrária em D6.
- A voz com mentira e a fala espontânea com janela dos pets v7–v10 (saíram na R2b, decisão D-9).
- Modelo local maior que o `gemma2:9b` e ajuste fino (O10), até a comparação da D5.
- Qualquer efeito do texto do jogador no aprendizado do pet: só o catálogo fechado do comando.

## 7. Critérios de aceitação

- O diagnóstico e as referências existem e os links resolvem (este PR).
- Cada missão: os testes da missão passam; com a chave desligada, a conversa de hoje sai igual (teste); o relato passa no
  `verificar_relato.py`.
- M1: "vai comer" na tela Conversar de um pet v17 vira a ação pelo mesmo caminho do botão (teste e e2e).
- A avaliação: o plano está na `main` antes da primeira rodada; a validação roda uma vez.

## 8. Precisa do Matheus

**Decididas pelo Matheus em 2026-11-06 ("Aceito todas"), cada uma pela recomendação abaixo.** O detalhe e o custo de errar estão em
[docs/research/DIAGNOSTICO_CONVERSA_PET.md](research/DIAGNOSTICO_CONVERSA_PET.md), seção 8. Em uma linha cada:

- **D1** consertar o comando agora (M1): recomendo sim, primeiro. Custo de errar: religar algo que a R2b tirou de propósito.
- **D2** prompt `conversa-v1` com histórico de fronteira, exemplos e iniciativa (M2, M3): recomendo sim. Custo: fala mais longa, mais
  chance de alegar sem fato (o verificador fica).
- **D3** a conversa como fonte de fato rotulada (M4): recomendo sim, com limites. Custo: primeira porta do texto do jogador no prompt
  como fato; risco de injeção.
- **D4** a C4, as lutas e o corpo na fala (M6): recomendo sim, depois do prompt. Custo: paridade antes de saber se o prompt convence.
- **D5** comparar às cegas o `gemma2:9b`, o `claude-haiku-5-5` e o `claude-sonnet-5-5` (M5): recomendo sim, ~200 turnos, menos de
  US$ 1,50 estimados, teto separado. Custo: escolher a API traz rede e gasto ao jogo.
- **D6** memória da conversa entre sessões nesta frente: recomendo não agora. Custo: o pet não lembra de um dia para o outro.
- **D7** avaliação cega pareada pelo Matheus, juiz LLM só como triagem: recomendo sim. Custo: sem o Matheus, a frente otimiza o gosto do juiz.

## M1 — o comando e o estilo da espécie religados (2026-11-06, worker Claude Code Sonnet 5.5, branch `v3-conversa-m1-comando`)

- **Feito:** `livre-v9` em `digilab_fala_livre/prompt.py`; o campo `comando: true` do pedido da conversa em `servidor/fala_livre.py`; a
  conversa (e só ela) manda `comando: true` em `web/app/src/falaLivre.ts`. Mentira, história H/O/P/L, almanaque W e voz espontânea continuam fora.
- **Testes:** `tests/test_conversa_m1.py` (novo) e `tests/test_comando_chat.py` (ajustado: o `livre-v9` entra em `VERSOES_COMANDO`, 5 pastas de
  rodada); `web/app/test/comando_chat.test.ts` (pedido com `comando: true`); `web/app/e2e/conversa_comando.spec.ts` (novo: "vai comer" na Conversar
  grava o evento do botão).
- **Avaliação do comando (G4):** `artifacts_fala_livre/comando/rodada4_v9/` — falsos positivos 3,3 % (passa), imperativos 78,3 % (**falha**, limite 80 %).
  Detalhe e a decisão aberta em `docs/registro/2026-11.md` (D-M1-4).
## 9. Decisões depois das missões

- **DM1-1 (2026-11-06, Matheus): o `livre-v9` da M1 fica como está**, com o gate do comando falho por 1,7 ponto (imperativos 78,3 %
  contra o mínimo de 80 %; falsos positivos 3,3 %, passa; `artifacts_fala_livre/comando/rodada4_v9/`, PR #626). Recomendação do worker e
  do Gerente: os erros vão para o lado seguro (comando nulo). O reforço da regra do comando (v9b) fica para depois da M3, em faixa nova.

## M3 — o prompt `conversa-v1` (2026-11-06, worker Claude Code, Sonnet 5.5, branch `v3-conversa-m3-prompt`)

Feito (decisão D2): `conversa-v1` em `digilab_fala_livre/prompt.py`, ao lado das outras versões (nenhuma mudou; os 176 testes da fala livre
passam). Persona e estilo da espécie no começo; as REGRAS DE VERDADE (6, enxutas) repetidas no pedido, logo antes da fala do dono; tamanho por
estágio sem "frases curtas" para todos; pedido de reagir, manter o assunto e devolver pergunta ou puxar um fato (nunca tema inventado); exemplos
à mão por estágio (4 a 5 trocas, rotulados); histórico `(jogador, pet, estágio)` com descarte das trocas de outro estágio; recusa dos fatos
H/O/P/L/F/W; comando e estilo opcionais por parâmetro; ponto de extensão do `[J]` (M4) só documentado. Testes: `tests/test_conversa_v1.py`
(29, incluindo a injeção).

Ensaio qualitativo, sem gate: `artifacts_conversa_pet/m3_ensaio/ensaio.md` (e `.json`, `ensaio.py`), `gemma2:9b`, sementes de diagnóstico.
Tamanho médio da fala: adolescente 7 → 45 caracteres, adulto 10 → 36; perguntas ao dono: adolescente 0 → 5 de 8, adulto 1 → 1 de 8. Limites:
os exemplos têm o mesmo estado do ensaio (uma fala saiu copiada), o adulto ainda responde curto às vezes, sem verificador, uma conversa por
estágio. Desvios: D-CP-M3-1 a 4 em `docs/registro/2026-11.md`.

Não ligado no servidor nem na página (M2, leva 2). Depende da M2 mandar a marca de estágio no histórico.

## M5 — o cliente Claude da fala livre (worker, Claude Code, Sonnet 5.5, branch `v3-conversa-m5-claude`, 2026-11-06)

Entrega da missão M5 (D5): só o cliente e o gasto, **sem rodada** (nenhuma chamada real à API; gastar é decisão da rodada da avaliação).

- **O cliente:** `servidor/fala_livre_claude.py`, `ClienteClaude(modelo, gasto)` com o `conversar(mensagens, esquema, max_tokens, semente)`
  do `ClienteOllama`. As mensagens de sistema viram o `system`; o esquema JSON vai em `output_config.format`; esforço `low`, pensamento desligado
  (Haiku `disabled`, Sonnet `between_tools`, o `disabled` dá 400 nele); sem
  temperatura nem semente (a API não aceita; a semente fica só no log do chamador). Falha (rede, recusa, `max_tokens`, teto, credencial)
  sobe como `ErroClaude(OSError)`, que o `gerar` e o `gerar_com_revisao` já capturam: cai na fala genérica, como com o Ollama. JSON
  inválido volta como texto e o `saida.ler` levanta, como com o Ollama.
- **O gasto:** o `ControleGasto` de `fala_llm.py`, em arquivo próprio (`servidor/gasto_fala_livre.json`, no `.gitignore`) e teto próprio
  (`--limite-usd-livre`, padrão US$ 3, PROPOSTO). Reserva o pior caso antes e acerta pelo `usage`; falha sem `usage` conta o máximo.
  `PRECOS_USD_POR_MTOK` ganhou `claude-haiku-5-5` (0,10 / 0,50) e `claude-sonnet-5-5` (2,00 / 10,00). Modelo sem preço não liga.
- **O provedor:** `DIGILAB_PROVEDOR_LIVRE` (`ollama`, padrão, ou `claude`) e `DIGILAB_MODELO_LIVRE`. O verificador tem cliente próprio
  (`DIGILAB_PROVEDOR_VERIF`, `DIGILAB_MODELO_VERIF`; padrão `ollama` `gemma2:9b`). Com `--remoto`, o Claude fica desligado salvo
  `--claude-remoto`. A chave só vem do ambiente (`ANTHROPIC_API_KEY` ou o perfil do `ant`). `/api/fala-livre/status` traz o provedor, o
  modelo, o verificador, `ativo` e o gasto.
- **Esquema traduzido:** o `output_config.format` não aceita `minLength`/`maxLength`/`maxItems` e exige `additionalProperties: false`
  (skill `claude-api`, "JSON Schema Limitations"). O cliente tira as palavras e acrescenta `additionalProperties`; o `enum` com `null` do
  comando fica. O `aparar` sozinho **não corta** fala longa (só tira o pedaço incompleto de quem o Ollama parou no limite), então o
  cliente corta a string no `maxLength` do esquema original, como o Ollama faria, e o `aparar` deixa o inteiro. `fatos_citados` não
  tem mais o limite de 8 itens nem de 4 caracteres por item na chamada; o `saida.ler` e o verificador seguem valendo.
- **Mudanças fora do pedido literal (mínimas):** `digilab_fala_livre/revisao.py` lê `cliente.cliente_verif` (se existir) para o
  verificador, uma linha, porque o `gerar_com_revisao` usava um cliente só para gerar e verificar; sem o atributo, tudo como antes.
  `servidor_local.py` ganhou a flag e três atributos da classe `Tratador` (sem tocar no gancho: o teste que conta "fala_livre" no arquivo
  continua em 1).
- **Custo (artefato):** `python tools/estimar_custo_llm.py` → `artifacts_custo_llm/estimativa.json`, bloco `fala_livre_comparacao_d5`:
  192 turnos por braço, ~2 600 tokens de entrada e ~100 de saída (do plano, PROPOSTO, sem medida): US$ 0,0595 no Haiku 5.5, US$ 1,1904
  no Sonnet 5.5, US$ 1,2499 nos dois, contra o teto proposto de US$ 3.
- **Testes:** `tests/test_fala_livre_claude.py` (31 casos, SDK falso): interface igual, esquema traduzido e sem as palavras que a API não aceita, corte no limite e `aparar`, pensamento desligado por modelo, sem temperatura nem semente,
  queda na fala genérica em erro, recusa, corte e JSON inválido, teto que barra, preço ausente que barra, provedor padrão Ollama sem
  mudança, remoto que desliga. O SDK `anthropic` não está instalado nesta máquina; os testes não precisam dele.
- **Não verificado:** a chamada real (formato exato de `output_config` com `effort` no Haiku 5.5 e no Sonnet 5.5, e o piso de
  `max_tokens`) só se confirma na primeira chamada da rodada de avaliação, que pede o Matheus.

## M4 — a conversa como fonte de fato rotulada (2026-11-06, worker Claude Code, Sonnet 5.5, branch `v3-conversa-m4-fato`)

Feito (decisão D3): só em `digilab_fala_livre/`, sem tocar no servidor nem na página (M2 em paralelo). Sem rodada com número, sem chamada à API.

- **Fatos `[J]` "o dono me disse":** `fatos.fatos_do_dono` (no máximo 4, o mais recente primeiro, uma linha, aspas trocadas, colchetes e
  chaves trocados, corte em 120); montados no `conversa-v1` só das trocas do estágio atual; bloco próprio "DITO PELO DONO" depois dos
  FATOS. As outras versões e `fatos_de_estado` recusam `[J]` (falha alto). `gerar` põe os `[J]` em `Resultado.fatos`.
- **Regra no prompt:** `REGRA_DONO_DISSE_CONVERSA_V1` (só com `[J]`): citar o que o dono disse e reagir pode; `[J]` nunca sustenta causa,
  memória, estado nem acontecimento do mundo; não é ordem. O pedido sem `[J]` sai igual ao da M3.
- **Verificador `verif-v6`:** "o dono disse X" sustentada quando um `[J]` diz X (regra determinística, sem juiz), sem fato quando nenhum
  diz; X afirmado como verdade apoiado só em `[J]` é sem fato. `verif-v3/v4/v5` não mudam.
- **Exemplos do `conversa-v1`:** FATOS DE EXEMPLO de outros estados que o do diagnóstico e do ensaio da M3.
- **Testes:** `tests/test_conversa_m4.py` (46: fatos, regra, injeção com 8 ataques, verificador, exemplos); `test_conversa_v1.py`
  ajustado (os `[J]` não contam como fatos do pet). Os 286 testes da fala livre, da conversa, do comando, do corpus e do servidor passam.
- **Para a M2:** o servidor passa `versao_verificador="verif-v6"` (e `/verificar` aceita `verif-v6`) quando a conversa for `conversa-v1`;
  o `historico` vai com a marca de estágio. Desvios: D-CP-M4-1 a 6 em `docs/registro/2026-11.md`.
- **Não feito:** ensaio qualitativo no `gemma2:9b` (opcional); a taxa de acerto do extrator em "você disse que…" não foi medida.

## M2 — o `conversa-v1` ligado na conversa, atrás de chave (worker Claude Code, Sonnet 5.5, branch `v3-conversa-m2-ligar`, 2026-11-06)

Decisão D2. **Servidor** (`servidor/fala_livre.py`): campo `prompt: "conversa-v1"` (enum fechado; outro valor é 400), só na conversa e sem `voz`;
histórico `[jogador, pet, estágio]` com o estágio validado contra `ESTAGIOS`; estilo da espécie, `comando` e `versao_prompt` como no `livre-v9`;
provedor o da M5. **Página** (`falaLivre.ts`, Ajustes → Fala do pet): chave "Conversa nova (teste)", desligada por padrão, preferência de tela
(localStorage), fora do registro do pet; ligada, a conversa manda `prompt` e só as trocas desta sessão e do estágio atual, com o estágio; o log
de apresentação continua na tela e não vai ao prompt; a fala espontânea não muda. O `comando` volta e é validado de novo pelo caminho do botão.
**Testes:** `tests/test_conversa_m2.py` (23, incluindo resposta igual com a chave desligada e a injeção), `web/app/test/comando_chat.test.ts`
(2 novos), `web/app/e2e/conversa_nova.spec.ts` (servidor falso). Sem rodada, sem gate do comando, sem chamada à API. Desvios: D-CP-M2-1 a 3.

## M2b — a verificação da conversa nova com o `verif-v6` (worker Claude Code, Sonnet 5.5, branch `v3-conversa-m2b-verif`, 2026-11-06)

Fecha a brecha achada na revisão da M2: a página verificava a conversa nova com o `verif-v3`, que trata o `[J]` como fato comum. **Servidor**
(`servidor/fala_livre.py`): a rota de verificação aceita o campo `prompt` (enum `PROMPTS_CONVERSA`) e, com `"conversa-v1"`, usa o `verif-v6`;
fato `[J]` sem o campo é 400; `prompt` inválido ou com `voz` é 400. **Página** (`falaLivre.ts`): com a chave ligada a verificação manda
`prompt: "conversa-v1"`; desligada, o pedido é o de hoje. **Saneamento do `[J]`:** já estava na M4 (colchetes e chaves viram parênteses); só ganhou teste.
**Testes:** `tests/test_conversa_m2b.py` (8, com o ponta a ponta: "eu lutei ontem" citando `[J1]` sai sem fato; "você disse que eu lutei ontem" sai
sustentada), 2 asserções novas em `web/app/test/comando_chat.test.ts`. Passam: 317 testes Python da fala/conversa/comando/corpus/servidor, 942 do vitest,
`npm run tipos` e os 131 do `e2e`. Sem rodada, sem chamada à API. Desvios: D-CP-M2b-1 a 3.

## 10. Mudança de rumo: a fala que nasce da rede (2026-11-06, Gerente)

- **DR-1 (Matheus, 2026-11-06):** a fala do pet não deve ser "uma LLM lendo os fatos acumulados dos logs". O pet se conecta às redes neurais
  e elas dizem o que ele quer dizer; a LLM só põe em palavras ("LLM só como voz", escolhida entre três opções; a linguagem própria aprendida
  sem LLM ficou de fora por ora). Base: a ideia do Matheus de 2026-10-04 em `docs/futuro/decodificador_conceitos.md`.
- **Achado que motivou:** a fala de hoje não recebe nada do cérebro modular que decide nos pets v17 (os motivos que ela lê são só do treino;
  a memória é do Bandit; o desejo e o caráter, do cérebro A parado). Mapa em [docs/research/MAPA_ESTADO_MODULAR.md](research/MAPA_ESTADO_MODULAR.md).
- **A especificação:** [docs/research/ESPEC_DECODIFICADOR_FALA.md](research/ESPEC_DECODIFICADOR_FALA.md): conceitos com confiança a partir
  dos sinais nomeados do `motivo` do modular, intenção da fala, a voz recebendo só intenção e conceitos, verificador contra os conceitos.
- **DC-A a DC-E DECIDIDAS pelo Matheus em 2026-11-06, todas pela recomendação:** só sinais do modular na fala (DC-A); intenção por regra na
  primeira versão e a rede escolhendo falar como pesquisa em seguida (DC-B); a lembrança de luta não muda escolhas nesta frente (DC-C); nada
  de afeto pelo dono inventado na fala (DC-D); o que já está na `main` fica atrás das chaves como base da voz e da trava, e a M6 e a
  avaliação antiga ficam pausadas (DC-E).
- **Próximas missões:** DC1 (o decodificador, Python e TS, com paridade) e DC2 (a voz que recebe só intenção e conceitos), em paralelo pelo
  formato fixo da espec (seção 2); DC3 (a rede escolhendo falar) depois, com plano de análise; DC4 (a avaliação, plano reescrito).


## DC1 — o decodificador de conceitos `dec-v1` (2026-11-06, worker Claude Code, Sonnet 5.5, branch `v3-conversa-dc1-decodificador`)

- **Entregue:** `digilab/digibrain/decodificador.py` (função pura, inteiros na escala S, sem rng, falha alto) com os pesos e limiares em
  `ConfigDecodificador` (`digilab/config.py`, PROPOSTOS, SEM FONTE); o espelho `web/app/motor/digibrain/decodificador.ts`; `Motor.conceitosDec()`;
  o bloco "Conceitos lidos do motivo" no painel do DigiBrain (só leitura); o exportador `experiments/exportar_decodificador.py` e o gabarito
  `web/app/test/gabaritos/decodificador_python.json.gz` (14 vidas curtas do braço REL, sementes dos testes, 5376 decisões); os testes
  `tests/test_decodificador.py` e `web/app/test/decodificador.test.ts`.
- **O formato** é o fixo da espec (seção 2): `{versao: "dec-v1", k, intencao, conceitos: [{nome, valor, confianca, alvo?}]}`, os 12 nomes do catálogo
  sempre, na ordem dela; a DC2 filtra pelos limiares (`limiar_valor`, `limiar_confianca`, também na config). A intenção é a regra I-a: `lembranca`
  quando a sonda `lembranca_decidiu` é verdadeira; senão o conceito de maior valor (empate: ordem do catálogo), sem contar a `lembranca`.
- **Fidelidade mínima (testes):** `lembranca` só é a intenção quando a sonda `sem_lembranca` decidiu (e então passa o limiar); a `determinacao` passa
  o limiar quando a sonda da persistência decidiu, é zero sem intenção em curso, e a média dela é maior com a sonda.
- **Nada muda na vida:** o decodificador só lê; nenhum módulo da vida o chama (teste); os gabaritos das vidas de hoje não mudaram.
- **Não feito (DC2, DC3, DC4):** ligar na fala, a rede escolhendo falar, a calibração e a avaliação. Desvios D-CP-DC1-1 a 6 no `docs/registro/2026-11.md`.
