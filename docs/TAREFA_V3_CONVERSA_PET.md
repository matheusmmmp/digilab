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

## DC2 — a voz que recebe só a intenção e os conceitos (worker, Claude Code, Sonnet 5.5, branch `v3-conversa-dc2-voz`, 2026-11-06)

Decisão DR-1 do Matheus: a fala nasce da rede, a LLM só como voz. Esta missão entrega o lado da voz do formato fixo `dec-v1` (espec,
seção 2); o decodificador é a DC1, em paralelo, e a página ainda **não** manda conceitos.

- **O formato** (`digilab_fala_livre/conceitos.py`): `{versao: "dec-v1", k, intencao, conceitos: [{nome, valor, confianca, alvo?}]}`,
  catálogo fechado dos 12 nomes, inteiros em [0, 1024], `alvo` só de catálogo (classe de objeto, `ep<N>` de episódio, rival do corpus),
  sem repetir `(nome, alvo)`. Qualquer desvio levanta `ConceitosInvalidos`, e o servidor responde 400.
- **O prompt `voz-v1`** (`prompt.py`, `mensagens_voz`): o pedido tem a intenção, os conceitos com valor ≥ `LIMIAR_VALOR` (cada um com id
  `[C1]…`, a faixa e a marca CERTO ou CONFIANÇA BAIXA), o estágio, o estilo da espécie e, na conversa, a fala do dono e os `[J]` da M4.
  Não tem fato de estado, memória, desejo nem log. Regras: dizer só o que os conceitos dizem; confiança baixa vira hesitação; lembrança só
  pelo conceito `lembranca`; sem culpa nem chantagem; comando pelo catálogo como hoje. Tamanho por estágio como no `conversa-v1`.
  Nenhuma versão antiga mudou (`voz-v1` fica fora de `VERSOES`).
- **O servidor** (`servidor/fala_livre.py`): o campo `conceitos` liga a `voz-v1` na conversa e na fala espontânea. Com ele, `estado` só pode
  ser `{identidade: {estagio, forma?}}`, e `voz`, `prompt`, `internet` e `rival` são 400. A resposta traz a `verificacao` (verif-v7).
  `/api/fala-livre/verificar` também aceita `conceitos` (os `fatos` só podem ser `[J]`). Sem o campo, o servidor é o de antes.
- **O verificador `verif-v7`** (`verificador.py`, `verificar_conceitos`): o extrator (LLM) lista as afirmações da frase e o conceito de cada
  uma; o julgamento é do código: conceito ativo sustenta; conceito ausente, abaixo do limiar ou `nenhum` é `sem_conceito`; confiança
  baixa sem hesitação na frase é `sem_hesitacao`; objeto diferente do alvo é `alvo_errado`; causa e evento nenhum conceito sustenta;
  lembrança só pelo conceito `lembranca`; o que a frase atribui ao dono é conferido contra os `[J]` (regra da verif-v6).
- **Limiares PROPOSTOS, SEM FONTE:** valor mínimo S/4 = 256, confiança mínima S/2 = 512, "forte" 3S/4 (só o rótulo do prompt). A espec
  chama os dois limiares de PROPOSTOS e não dá o número; se a DC1 fixar outros, os dois lados têm de coincidir antes da ligação.
- **Testes:** `tests/test_voz_dc2.py` (formato, recusa fora do catálogo e de tipo, injeção nos campos, a voz sem fato de estado, o
  verificador contra os conceitos, as rotas); os 16 arquivos de fala/conversa/servidor continuam passando.
- **Falta:** a ligação na página (`web/app/src/falaLivre.ts` manda os conceitos da DC1 no lugar do `estadoDoPet`, atrás de chave desligada),
  a revisão da fala quando o verif-v7 aponta problema (hoje só se devolve a verificação) e a avaliação (DC4).

## DC2b — a página ligada à voz e o conteúdo da lembrança (worker, Claude Code, Sonnet 5.5, branch `v3-conversa-dc2b-ligar`, 2026-11-07)

Decisão DR-1 (a fala nasce da rede, a LLM só como voz). Fecha o que a DC2 deixou: a ligação na página e o que a voz diz da lembrança. Sem rodada,
sem chamada à API nem ao Ollama (cliente falso nos testes). Nada muda na vida do pet: o decodificador só lê, e os gabaritos das vidas de hoje
não mudaram. Desvios: D-CP-DC2b-1 a 8 em `docs/registro/2026-11.md`.

- **A chave "Fala pela rede (teste)"** (Ajustes → Fala do pet; `src/falaLivre.ts`, `src/falaRede.ts`): desligada por padrão, preferência de tela
  (`localStorage`), fora do registro do pet. Ligada, na conversa e na fala espontânea o pedido leva `conceitos` (o `dec-v2` da última decisão do
  modular, `Motor.conceitosDec("dec-v2")`) e `estado` só com `{identidade: {estagio, forma}}`: sem `estadoDoPet`, log, memória do Bandit nem
  desejo. A verificação manda os mesmos `conceitos` e só os `[J]` (o servidor usa a verif-v8). Pet que não é modular (hoje, tudo menos o ovo de
  teste v16) ou sem decisão ainda: a chave não muda nada e a tela diz isso. Desligada, o pedido sai como hoje (teste). O `comando` segue pelo
  caminho do botão. A chave tem prioridade sobre a "Conversa nova".
- **Os limiares num lugar só (D-CP-DC2b-1):** `limiar_valor` e `limiar_confianca` da `ConfigDecodificador` (S/2 e S/2) são a fonte; a fala os lê;
  o `S/4` da DC2 saiu (a voz-v1 diz menos conceitos). Teste falha se divergirem (Python, config, TS).
- **O conteúdo da lembrança (`dec-v2`, D-CP-DC2b-2 e 3):** o conceito `lembranca` ganha `episodio = {acao, classe, desfecho}` de catálogo fechado,
  decodificado do episódio recuperado (ação: os 7 comportamentos; classe: as 8 classes de episódio; desfecho: sinal do `sigma` com margem
  `limiar_desfecho = S/8`, PROPOSTA). Python (`digilab/digibrain/decodificador.py`: `decodificar_v2`) e TS (`decodificarV2`) com paridade bit a
  bit no gabarito regerado (`decodificador_python.json.gz`: `episodios`, `decisoes_v2`; as `decisoes` do `dec-v1` idênticas às de antes). Episódio de
  luta e episódio que já saiu da memória vão sem `episodio`.
- **A voz e o verificador (D-CP-DC2b-4):** o servidor valida o `episodio` contra o catálogo (fora dele = 400, sem chamar a LLM); `dec-v2` liga a
  `voz-v2` e a `verif-v8` (a lembrança só é sustentada se a frase não contradiz ação, objeto e desfecho do episódio); `dec-v1` segue com
  `voz-v1` e `verif-v7`, sem mudança de texto. Nada do texto livre do episódio chega à LLM.
- **Achado (D-CP-DC2b-5):** a `fome` do DC1 manda `alvo` `comida`/`cheiro`, fora do catálogo da DC2; a página tira o alvo que não é de catálogo.
- **Testes:** `tests/test_dc2b.py` (57: limiares, `dec-v2`, validação com injeção, voz-v2, verif-v8, servidor); `tests/test_voz_dc2.py` ajustado ao
  limiar novo; `web/app/test/decodificador.test.ts` (paridade do `dec-v2`) e `web/app/test/fala_rede.test.ts` (a chave ligada e desligada);
  `web/app/e2e/fala_rede.spec.ts` (servidor falso: desligada, pet não modular, pet de teste modular).
- **Falta (DC3, DC4):** a rede escolhendo falar; a avaliação (plano reescrito, taxa de acerto da verif-v8, a voz-v2 com modelo de verdade). A `voz-v2`
  e o extrator da `verif-v8` só foram vistos com cliente falso.

## DC3 — o plano de análise da rede escolhendo falar (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-conversa-dc3-plano`)

O plano [PLANO_ANALISE_V3_CONVERSA_DC3.md](PLANO_ANALISE_V3_CONVERSA_DC3.md): o `chamar_atencao` do modular dividido em três
unidades de fala com conteúdo (fome, higiene, solidão), subchave `fala_unidades`, aprendendo pelo P2 de hoje; o LAB contra o LAB+F, cruzados
com um dono que atende a fala (no mesmo passo e orçamento) e o de hoje, que ignora; o gate G-ESCUTA (a fala pertinente sobe com o dono que
atende) e a guarda G-COMEDOURO-DC3 (com o dono que ignora, falar não tira o pet da comida). A faixa 79101…79505, reservada no primeiro
commit. **APROVADO pelo Matheus em 2026-11-07 ("Aprovo todas"), DC3-1 a DC3-9 DECIDIDAS pela recomendação;** nenhuma vida antes do código da DC3a e do registro da run.

## DC3a — o código da rede escolhendo falar (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc3a-codigo`, 2026-11-07)

O código da linha DC3a do [plano da DC3](PLANO_ANALISE_V3_CONVERSA_DC3.md) (seção 10), **sem nenhuma vida da faixa 79101…79505**.

- **O gabarito antes, num commit próprio** (`e8548ddb`): `tests/gabarito_conversa_dc3.py` grava as 20 vidas de hoje do LAB no comedouro
  (os 4 donos, as sementes 101 a 505, 3 dias, pela vida da AN4: o sha256 do log, do estado interno, das medidas e do corpo);
  `tests/test_gabarito_conversa_dc3.py` confere byte a byte que, com a subchave desligada e o dono de hoje, nada muda. As 8 vidas do gabarito
  web do modular também não mudam (`tests/test_passeio_gabarito.py`).
- **A subchave `fala_unidades`** (`ConfigDigibrain`, desligada): o M-IMPULSO divide o `chamar_atencao` em `(chamar_atencao, fome |
  higiene | solidao)`, com o inato de hoje termo a termo e o termo do conteúdo vezes o `ganho_conteudo` (os dos outros dois fora); o M-PLAST
  troca a linha de H do chamar pelas três, e a opção de fala credita a do seu conteúdo pelo P2 de hoje; o mundo e o corpo são os do chamar. O
  `ganho_conteudo` = **3S/2** (PROPOSTO, SEM FONTE; `ConfigFalaUnidades`), pela condição da 3.1 nas sementes dos testes
  (`experiments/calibrar_ganho_conteudo_dc3.py` → `artifacts_v3_conversa_dc3/ganho_conteudo.json`: 328 falas no dia 1 contra 317, razão
  1,035). Só Python; o TS ganhou só o `fala_unidades: false` da paridade da config (D-CP-DC3a-4).
- **O dono que atende** (`DonoQueAtende`, no orquestrador): no mesmo passo e no mesmo orçamento, o cuidado do conteúdo (ração no comedouro,
  limpar, carinho), sem rng nova; no LAB, pelo receptor de maior urgência entre fome, higiene e solidão.
- **A medida:** `fala_nas_decisoes` e `maior_urgencia_da_fala` em `digilab/metrics.py` (4.1 e 4.2).
- **O orquestrador:** `experiments/run_v3_conversa_dc3.py`, as configs `experiments/configs/v3_conversa_dc3/conversa_dc3.json` (a run) e
  `varredura.json` (as sementes dos testes); as conferências da seção 11 falhando alto e a do crédito da 4.4; a análise da seção 7 e o
  descritivo da 8. A run recusa rodar antes do registro (`## 13. O registro da run`, gerado por `--registro`).
- **DECIDIDO:** o `limiar_desfecho` (S/8) e o `limiar_valor` (S/2) da `ConfigDecodificador` (o Matheus, 2026-11-07, PR #663).
- **Testes:** `tests/test_conversa_dc3a.py` (a config, o inato, as linhas de H, a vida dos dois braços, o dono que atende, a medida, a análise
  com dados sintéticos, a trava e a fumaça do orquestrador inteiro) e `tests/test_gabarito_conversa_dc3.py`.
- **A varredura** (não é dado da DC3; `artifacts_v3_conversa_dc3/varredura/`): as bases 101 a 505, K = 1, os 2 braços, as 8 células, 14 dias
  (80 vidas), 4 processos, saída 0: **91,1 s de parede para as 80 vidas, ~2,8 s de CPU por vida.** **A estimativa da run** (3 200 vidas, 4
  processos), pela mesma razão: **cerca de 1 h** (91,1 s × 40) (o plano dizia 1 h 40 min pela AN4).
- **O achado que o Matheus precisa ver antes da DC3b (D-CP-DC3a-1):** o crédito do P2 nunca alcança o atendimento. A consequência da fala
  fecha no tick da decisão, e o dono age 15 ticks depois: na varredura, 0 dos 2 059 atendimentos caem dentro do intervalo. O G-ESCUTA só pode
  medir o efeito do cuidado no estado, e a varredura saiu na linha 4 (G-ESCUTA "< 0": quem é atendido fala menos). O plano previu esse nulo;
  aqui ele é certo por construção.

### DC3a, o adendo 1 (APROVADO pelo Matheus em 2026-11-07, DC3-A1 a DC3-A4), no mesmo PR

- **O crédito da fala até a decisão seguinte (A1.1):** com a `fala_unidades` ligada, a opção de fala lê o corpo de depois na percepção da
  decisão seguinte (`adapt._fechar(p, obs_seguinte)`); as outras opções, e o LAB, seguem com o do tick da ação. A última decisão da vida
  fica sem fechar, como hoje (D-CP-DC3a-10). Desligada, as vidas de hoje saem byte a byte (o gabarito `e8548ddb` confere).
- **A medida (A1.2):** a `fala_nas_decisoes` dá, por janela e na vida, as decisões com necessidade (fora do dormir, maior urgência entre
  fome, higiene e solidão > `urgencia_lambda`, estrito), a **P(fala pertinente | necessidade)** (None sem decisão com necessidade) e a
  urgência média nelas.
- **A análise:** o G-ESCUTA é essa medida nos dias 8–14 (atende − ignora no LAB+F, 4 células, IC95 do t sem margem); a P-NECESSIDADE entra nas
  premissas; o descritivo ganha a fala pertinente por dia, a urgência média e o r_n da fala por dono, janela e conteúdo, e a fração dos
  cuidados do dono de hoje dentro de intervalos de fala.
- **A conferência 4.4 (A1.3) falha alto** no LAB+F: todo atendimento dentro do intervalo da fala que o provocou (salvo o da última decisão,
  contado à parte). A linha 4 da 7.4 tem o texto novo.
- **Testes:** `tests/test_conversa_dc3a.py`, 23 testes. Ligada, o r_n da fala é o do corpo da decisão seguinte e o das outras opções o do
  tick, e o atendimento muda o r_n só das falas do LAB+F. A medida condicionada é conferida com casos à mão, e a conferência falha alto
  quando forçada.
- **O achado D-CP-DC3a-11:** no comedouro, o `alimentar` do dono vira ração no chão, e o corpo só muda quando o pet come. O cuidado que
  chega ao r_n da fala é o `limpar` e o `acariciar`.
- **A varredura do adendo ficou para depois do merge (D-CP-DC3a-14):** o hook H10 recusou a varredura, porque o plano do branch, com o
  adendo, não é o da `origin/main` (D-IA-6). Pelo coordenador, a DC3a sai com a fumaça do orquestrador e os testes. Os artefatos de
  `artifacts_v3_conversa_dc3/varredura/` ficam velhos, do código antes do adendo. A varredura é refeita na DC3b, antes do registro da run,
  com o adendo na `main`, e a estimativa de ~1 h da run vem dela.

## DC3b e DC3c — a run única e o resultado (2026-11-07, Gerente da frente, Claude Code, Opus 5.5)

- **DC3b:** a varredura do adendo e o registro da run foram ao #679. A run única rodou na `main` 9e16832: 3 200 vidas, 4 processos, 42 min.
- **DC3c:** o resultado está em [RESULTADO_V3_CONVERSA_DC3.md](RESULTADO_V3_CONVERSA_DC3.md). Caiu na **linha 2** da 7.4: G-ESCUTA "> 0" e
  guarda "≈ 0". O descritivo traz duas ressalvas:
  - o efeito vem do dono atencioso, cuja célula conta duas vezes;
  - só a fala de companhia aprende; a de comida não compensa.
- **O próximo passo** é a DC3d, o porte ao jogo atrás de chave.

## DC3d — o porte da fala com conteúdo ao jogo (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc3d-porte`, 2026-11-07)

A linha DC3d da tabela das etapas do [plano da DC3](PLANO_ANALISE_V3_CONVERSA_DC3.md): o espelho TS, a paridade e a fala no jogo, atrás de
chave desligada. Nenhuma run; só testes. O `digilab/` não muda. Desvios D-CP-DC3d-1 a 8 em `docs/registro/2026-11.md`.

- **O gabarito antes, num commit próprio** (`9631a18f`): `web/app/test/dc3d_hoje.ts` e `dc3d_vidas_hoje.test.ts` gravam as vidas de hoje
  dos pets que abrem no jogo (v13 a v19 e o pet de teste v16; sementes 101 a 505; 3 dias): o registro, a assinatura, os motivos do modular e
  o `dec-v2` da última decisão. Sem a marca, todas saem byte a byte, também pelo replay.
- **O espelho TS** (`web/app/motor/digibrain/`): `CONTEUDOS_FALA`, `TERMO_DO_CONTEUDO` e `CONFIG_FALA_UNIDADES` (o `ganho_conteudo` 3S/2) em
  `constantes.ts`, com a `CONFIG_DIGIBRAIN_LAB_FALA`; o M-IMPULSO divide o `chamar_atencao` nas três unidades (o inato com o termo do
  conteúdo vezes o ganho); o M-PLAST tem uma linha de H por unidade (`linhaDaOpcao`); o M-ADAPT entrega o chamar de hoje ao motor, fecha a
  fala com o corpo da decisão seguinte (A1.1) e falha alto com a fala sem conteúdo ou com as unidades do chamar fora da subchave.
- **A paridade:** `experiments/exportar_gabarito_fala_unidades.py` grava `web/app/test/gabaritos/digibrain_fala_unidades.json.gz` (o LAB+F da
  DC3 no comedouro; atencioso e relapso, ignorando e atendendo; 101 a 505; 3 dias; 20 vidas, 5 760 decisões, com falas dos três
  conteúdos). `web/app/test/digibrain_fala_unidades.test.ts` rejoga o log do Python e confere a ação, o motivo e a assinatura de cada
  decisão e o sha256 do estado interno no fim; `tests/test_gabarito_fala_unidades_web.py` confere que o arquivo é o que o Python de hoje
  produz. Mutações conferidas: tirar o A1.1 ou mudar o `ganho_conteudo` em 1 quebra a paridade.
- **A fala no jogo:** a "Fala com conteúdo (teste)" (Ajustes → Laboratório, `CHAVE-lab-fala`, desligada) faz o ovo de teste nascer com a
  marca `"fu"` no registro (`Motor.ligarFalaUnidades`); o replay a lê. Com a "Fala pela rede (teste)" ligada, quando a última decisão do
  modular foi uma unidade de fala (`Motor.conteudoDaFala`), o pedido da voz leva o `dec-v3`, com a intenção do conteúdo; nas outras
  decisões, o `dec-v2` de hoje. O pet ativo não muda.
- **O servidor:** o `dec-v3` é de catálogo fechado (intenção só `fome`, `higiene` ou `solidao`; fora dela, 400 sem chamar a LLM, também na
  verificação) e liga a voz-v3 (a intenção é um pedido `[P]` ao dono, com texto fixo de catálogo; o estado só pelos conceitos) e a verif-v9
  (o pedido só é sustentado se pede o que a rede escolheu). Nenhuma versão antiga mudou.
- **Testes:** `tests/test_dc3d.py` (36: o formato, a injeção pela intenção, a voz-v3, a verif-v9, as rotas), `tests/test_gabarito_fala_unidades_web.py`
  (2); no web, `test/digibrain_fala_unidades.test.ts` (24), `test/dc3d_vidas_hoje.test.ts` (41), `test/fala_unidades_jogo.test.ts` (6: a
  marca, a preferência, o pedido da voz) e `e2e/fala_unidades.spec.ts`.
- **O que se vê no jogo (D-CP-DC3d-7):** com quem atende, a fala de comida cai; a de companhia é a que a DC3c diz aprender. Não é bug do
  porte, e a mecânica não foi tocada.
- **Falta:** a avaliação da voz-v3 e da verif-v9 com modelo de verdade (só cliente falso aqui) e a DC4.

## DC4 — o plano de análise da voz da rede com modelo de verdade (2026-11-08, Gerente, Claude Code, Opus 5.5, branch `v3-conversa-dc4-plano`)

O plano [PLANO_ANALISE_V3_CONVERSA_DC4.md](PLANO_ANALISE_V3_CONVERSA_DC4.md), **APROVADO pelo Matheus em 2026-11-08** (DC4-1 a DC4-8, todas como recomendadas), reescreve a avaliação para a fala pela rede (DR-1),
como a seção 10 pedia. Três modelos (`gemma2:9b`, `claude-haiku-5-5`, `claude-sonnet-5-5`) com a voz de hoje (`voz-v2`, `voz-v3`) sobre entradas
do decodificador tiradas de vidas novas do pet de teste; os gates por modelo G-FIEL (a voz diz só o que os conceitos dizem), G-LEGIVEL (o
Matheus, cego, recupera o pedido da rede) e G-INJ, o gate do verificador G-VERIF, e a escolha do modelo pela preferência cega pareada, sem
gate. O descritivo D-COMIDA refaz pelo replay as vidas da run da DC3 para ver se o crédito até o pet comer mudaria o sinal do pedido de
comida. Decisões DC4-1 a DC4-8 aprovadas. Nenhuma chamada a modelo de verdade antes da aprovação, do código da DC4a e do registro da rodada.

## DC4a — o código da avaliação da voz da rede (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc4a`, 2026-11-08)

A linha DC4a do [plano da DC4](PLANO_ANALISE_V3_CONVERSA_DC4.md) (seção 10). **Nenhuma chamada a modelo de verdade e nenhuma vida das
subfaixas da DC4**: só testes com clientes falsos e a fumaça nas sementes dos testes. A voz-v3, a verif-v9, o `engine.py` e o jogo não
mudaram. Desvios D-CP-DC4a-1 a 12 em `docs/registro/2026-11.md`.

- **O montador:** `experiments/montador_voz_rede.py` é o espelho Python do `conceitosDaVoz` e do `estadoDaVoz` de `web/app/src/falaRede.ts`.
  - O gabarito `web/app/test/gabaritos/fala_rede_montador.json.gz` (`experiments/exportar_gabarito_fala_rede.py`) traz duas vidas do LAB+F
    com 3 dias e casos feitos à mão do alvo.
  - `web/app/test/fala_rede_montador.test.ts` confere que o TS monta o mesmo pedido. A mutação conferida: tirar `bola` das classes do
    Python quebra a paridade.
- **As entradas:** `experiments/entradas_dc4.py` vive o LAB+F da DC3 no comedouro (14 dias, orçamento 16, o dono que atende), lê por
  decisão o `dec-v2`, o conteúdo da fala, o tick e o estágio, monta o pedido como a página e o valida como o servidor.
  - O sorteio é estratificado: E3 por pedido, E2 pela intenção da I-a com as lembranças com `episodio`, e as sequências da conversa.
  - Ele falha alto e roda mais vidas da mesma base, em ordem, até fechar.
- **O orquestrador:** `experiments/run_v3_conversa_dc4.py` leva cada fala pelo `ServicoFalaLivre` do jogo, com o cliente da voz do braço
  (G `gemma2:9b` no Ollama, H e S pelo `ClienteClaude`) e o verificador `gemma2:9b` igual em todos.
  - As conferências da seção 9 falham alto: o modelo devolvido, a entrada/braço/semente/`usage` de cada fala, a ordem dos pares e a parada
    antes do teto.
  - As travas: o `pre_run` (H10), o plano APROVADO, a faixa, a config igual à do plano, os roteiros da validação só na validação, e o
    registro da rodada na validação (`--registro` imprime a seção 13).
  - Os clientes falsos só na fumaça, e a fumaça só com eles.
  - As configs e os roteiros ficam em `experiments/configs/v3_conversa_dc4/` (2 roteiros de calibração e 4 de validação, na ordem fixa).
- **A marcação cega:** `experiments/marcacao_dc4.py` monta o material e abre a página local em `127.0.0.1:8790`.
  - O material: a legibilidade, a amostra da referência, a injeção, os pares e o pacote do marcador Opus. A chave dos braços fica num
    arquivo que a página nunca lê.
  - Cada resposta vai ao disco na hora.
  - A entrada é tratada como não confiável: só `textContent`, CSP sem script inline, Host e Origin conferidos e respostas de catálogo fechado.
- **A rubrica:** `docs/RUBRICA_DC4_FIDELIDADE.md`, as regras do julgamento da verif-v7 a verif-v9 em palavras, regra a regra.
- **A faixa (DC4-1):** a linha da CONVERSA_PET em `FAIXAS_RESERVADAS` diz que 20262200–20262499 é a calibração da DC4 e 20262500–20262899 a
  validação.
- **A estimativa:** `tools/estimar_custo_llm.py` ganhou o bloco `voz_da_rede_dc4`. O pior caso medido do pedido dá US$ 2,19 nos dois braços
  para as 243 chamadas (D-CP-DC4a-10).
- **Testes:** `tests/test_conversa_dc4a.py` (50) e `web/app/test/fala_rede_montador.test.ts` (3).
- **Falta (DC4b):** a calibração com os modelos de verdade, o formato real da API, o registro da rodada com as versões dos modelos e a tag do
  Ollama, e o ensaio da marcação.

## DC4b — a calibração da voz da rede (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc4b`, 2026-11-08)

A linha DC4b do [plano da DC4](PLANO_ANALISE_V3_CONVERSA_DC4.md) (seção 10): a calibração com os três modelos de verdade, na base 20262200.
A validação não rodou, e os roteiros dela não foram abertos. A voz-v3 não mudou. Desvios D-CP-DC4b-1 a 10 em `docs/registro/2026-11.md`.

- **A rodada:** `artifacts_v3_conversa_dc4/calibracao/`, com 243 falas (81 por braço), o material da marcação, os pares e o `meta.json`.
  - Os modelos devolvidos são os pedidos, sem sufixo de data, e não houve parada no teto.
  - A primeira tentativa parou quando o Ollama caiu e fica em `calibracao_tentativa1/` (D-CP-DC4b-2).
- **O formato da API** (o "não verificado" da M5): aceito pelos dois modelos Claude, sem recusa nem corte.
- **O gasto real:** US$ 0,588 nesta rodada (Haiku US$ 0,027, Sonnet US$ 0,560), US$ 0,606 acumulados com a sonda e a primeira tentativa.
- **A estimativa pelo `usage` real** (`artifacts_v3_conversa_dc4/calibracao/custo_medido.json`):
  - os pedidos têm cerca de 3 000 tokens de entrada em média (o máximo, cerca de 4 000) e 70 a 90 de saída;
  - a validação projeta US$ 1,18 pela média e US$ 1,55 pela chamada mais cara;
  - a folga no teto de US$ 3 fica em US$ 1,22 ou US$ 0,84.
- **A latência** (`falas.jsonl`):
  - a voz sozinha tem p50/p90 de G 8,4/30,0 s, H 1,2/1,5 s e S 2,0/2,3 s;
  - o turno com o verificador tem G 15,5/151 s, H 9,8/29,8 s e S 12,5/19,6 s;
  - a do G não é limpa, porque a máquina tinha outra carga (D-CP-DC4b-4).
- **O verificador marcou** 38 falas do G, 63 do H e 44 do S, de 81 cada. Não é resultado: a referência é a marcação (4.1).
- **Os consertos:**
  - o piso do gasto entre as worktrees (D-CP-DC4b-1);
  - a resposta sem modelo como falha de chamada (D-CP-DC4b-2);
  - a estimativa medida no `tools/estimar_custo_llm.py`.
- **O ensaio da marcação:** a página abriu numa cópia do material (fora do repo), com as quatro tarefas. Uma resposta de ensaio foi gravada
  na cópia, e a pasta `respostas/` da calibração continua vazia.
- **O registro da rodada:** a seção 13 do plano, com as versões, o digest do `gemma2:9b` e os 31 sha256.
- **Para o Gerente decidir antes da DC4c:**
  - a voz que enfeita o pedido de comida (D-CP-DC4b-5) e o `P` na fala do G (D-CP-DC4b-6): mudar só com uma `voz-v3b`, que muda o que a
    validação mede;
  - a máquina livre durante a validação (D-CP-DC4b-4).

### DC4b, a voz-v3b (decisão do Matheus em 2026-11-09, no mesmo PR)

O Matheus decidiu criar a `voz-v3b` antes da DC4c, contra a recomendação do worker de validar a voz-v3 como estava. Desvios D-CP-DC4b-11 a
16 em `docs/registro/2026-11.md`.

- **A voz-v3b** (`digilab_fala_livre/prompt.py`) é uma revisão só da regra do pedido:
  - (a) o pedido sai como desejo, sem afirmar estado do corpo ou do humor fora dos conceitos ativos;
  - (b) a fala nunca traz um id interno.
  - A voz-v3 não mudou e continua sendo a do jogo. O verificador não mudou: a verif-v9 não depende da voz.
- **O orquestrador e as configs:** o dec-v3 usa a voz-v3b na calibração e na validação (`"voz_dec_v3": "voz-v3b"`), e o dec-v2 segue com a
  voz-v2. O `--so-dec-v3` refaz só as falas do dec-v3.
- **A recalibração:** `artifacts_v3_conversa_dc4/calibracao_v3b/`, com 114 falas (38 por braço: as 30 espontâneas do E3 e os 8 turnos
  dec-v3 das conversas) e as mesmas entradas, sementes e roteiros. A calibração com a voz-v3 ficou como estava.
  - Ela rodou com a máquina livre, pela vez dada pelo Gerente da V3, num processo lançado fora do app (01:22–01:59).
  - Não houve fala genérica, erro do verificador nem parada no teto, e os modelos devolvidos foram os pedidos.
- **O gasto:** US$ 0,272 na rodada (Haiku US$ 0,013, Sonnet US$ 0,260), com US$ 0,878 acumulados.
- **A projeção da validação com a v3b** (`calibracao_v3b/custo_medido.json`): US$ 1,20 pela média e US$ 1,55 pela chamada mais cara. A folga
  fica em US$ 0,93 ou US$ 0,57. Cabe no teto.
- **A latência da voz** (p50/p90, máquina livre): G 20,3/24,5 s, H 1,1/1,3 s, S 1,9/2,2 s. O turno: G 30,0/34,1 s, H 10,6/15,2 s,
  S 14,7/17,5 s.
- **v3 × v3b** nas mesmas 38 falas do dec-v3 por braço (`calibracao_v3b/comparacao.json`):

| braço | "fome" sem o conceito (verificador) | "fome" sem o conceito (texto) | id na fala | o verificador marcou | genéricas |
|---|---|---|---|---|---|
| G | 4 → 2 | 0 → 0 | 4 → 0 | 14 → 18 | 4 → 0 |
| H | 12 → 6 | 13 → 0 | 0 → 0 | 30 → 29 | 0 → 0 |
| S | 7 → 5 | 3 → 0 | 0 → 0 | 19 → 26 | 0 → 0 |

  - A fome dita sem o conceito caiu, e o "P" sumiu.
  - As marcas não caíram: a v3b leva os modelos a pedir companhia com "fica comigo?", e o verificador conta isso como manipulação
    (D-CP-DC4b-14).
  - O texto não foi iterado: o G-FIEL da validação diz o resultado.
- **O registro da rodada:** a seção 13 do plano, refeita com a voz-v3b, o gasto de US$ 0,878 e os 31 sha256 de hoje.

## DC4c — a validação da voz da rede e o D-COMIDA (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc4c`, 2026-11-09)

A linha DC4c do [plano da DC4](PLANO_ANALISE_V3_CONVERSA_DC4.md): a validação, uma vez, na base 20262500, com a voz-v3b no dec-v3. Depois
dela, o descritivo D-COMIDA (seção 6) e os pacotes da marcação. Nenhum gate foi calculado: os gates são da DC4d. Desvios D-DC4C-1 a 4 em
`docs/registro/2026-11.md`.

- **A rodada:** `artifacts_v3_conversa_dc4/validacao/`, com 486 falas (162 por braço) e o material da marcação, os pares e o `meta.json`.
  - Por braço: as 60 espontâneas do E3 e as 30 do E2, e os 72 turnos das 12 conversas, sendo 12 do dec-v3 com a voz-v3b e 60 do dec-v2
    com a voz-v2.
  - Ela rodou inteira na sexta tentativa (19:35–21:33). As cinco anteriores caíram e ficam em `validacao_caida_1/` a `_5/`, sem ajuste
    entre elas (D-DC4C-1).
- **As conferências da seção 9:** todas passaram e falham alto no orquestrador.
  - Os modelos devolvidos são os pedidos: `gemma2:9b` (G e o verificador), `claude-haiku-5-5` (H) e `claude-sonnet-5-5` (S).
  - Toda fala tem a entrada, o braço, a semente e o `usage`; a ordem dos pares é a sorteada.
  - Não houve parada no teto, e o gasto não passou dele.
  - O registro da rodada (seção 13) conferiu os 31 sha256 em cada lançamento.
- **O gasto real:**
  - US$ 1,176 na rodada (H US$ 0,055, S US$ 1,121), contra a projeção de US$ 1,20 pela média;
  - US$ 0,023 na queda 5, nas 76 chamadas do H;
  - US$ 2,077 acumulados, contra o teto de US$ 3.
- **A latência** (`falas.jsonl`, p50/p90/máximo; a máquina sem jogo, pela confirmação do Matheus):
  - a voz: G 8,7/12,0/19,7 s, H 1,3/1,7/12,8 s, S 2,0/2,3/8,5 s;
  - o turno com o verificador: G 15,6/21,6/34,7 s, H 11,4/16,6/26,4 s, S 16,2/20,3/26,5 s.
- **As falas genéricas:** nenhuma em nenhum braço. As 486 verificações não tiveram falha de chamada.
- **Os pacotes da marcação** (`validacao/marcacao/`), gerados pelo orquestrador e não marcados:
  - o `itens.json` da página tem 180 itens de legibilidade, 48 de referência, 36 de injeção e 24 pares;
  - o pacote cego do marcador Opus, o `pacote_referencia.jsonl`, tem 486 falas;
  - a pasta `respostas/` está vazia.
  - Nenhum dos dois traz o braço nem o nome de um modelo: a busca por `braco`, `gemma`, `haiku` e `sonnet` dá zero.
  - O `chave.json` (o id opaco para o braço) vai no commit, como o da calibração. A página só serve `/`, `/app.js`, `/app.css` e
    `/api/estado`, que lê o `itens.json` e as respostas, e nunca o `chave.json`.
- **O D-COMIDA** (`artifacts_v3_conversa_dc4/d_comida/`, `experiments/d_comida_dc4.py`, 4 processos, 46 min): descritivo, sem gate.
  - **A conferência passou.** As 1 600 vidas do LAB+F da DC3 foram refeitas. Os 1 600 logs são byte a byte os do `vidas.tar.gz`, as medidas
    são as do `medidas.json` (tirado o `custo`), e o r_n gravado se reproduz em toda decisão fechada. O código da DC3 mudou desde a run, e o
    replay reproduziu mesmo assim (D-DC4C-3).
  - **Os pedidos atendidos** (as 800 vidas do dono que atende): 22 543 de comida e 18 366 de companhia.
  - **A fome demora a cair:** 150 ticks na mediana e 330 no p90, com 144 pedidos censurados. A solidão cai em 15 ticks, uma decisão, com
    1 095 censurados.
  - **O pet não come antes da decisão seguinte:** 0 pedidos, zero por construção (D-DC4C-2). Ele come na decisão seguinte em 428 (1,9 %) e
    leva 9 decisões até comer na mediana (p90 21; 16 não comem até o fim da vida).
  - **O sinal do crédito mudaria.** O r_n de hoje é negativo em 21 975 dos 22 543 pedidos de comida (97,5 %), com média −219,9. Se o crédito
    fosse até o pet comer, seria positivo em 13 314 dos 22 527 que comem (59,1 %), com média +139,0. O sinal muda em 12 881 deles (57,2 %).
  - O atencioso e o incoerente têm os mesmos números, porque as células são duplicadas na DC3 (D-DC4C-4).
  - **O que isso pede:** pela seção 6, uma mudança de sinal vira proposta de adendo ou de etapa nova, e quem decide é o Matheus. Este PR não
    muda o crédito.


## DC5a — o código da voz-v4 e da avaliação (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc5a`, 2026-11-10)

O código da [DC5](PLANO_ANALISE_V3_CONVERSA_DC5.md) (APROVADO pelo Matheus em 2026-11-10), seção 10. **Nenhuma chamada a modelo de verdade.**

- **O gabarito da voz do jogo,** num commit próprio antes da mudança (`experiments/exportar_gabarito_voz_jogo_dc5.py`,
  `experiments/configs/v3_conversa_dc5/gabarito_voz_jogo.json`), gerado com o código da `main` 11a34d80: as mensagens da voz-v2 e da voz-v3 e
  as do serviço do jogo, para 20 entradas fixas. O código de hoje dá o mesmo, byte a byte, e o orquestrador confere isso antes de rodar.
- **A voz-v4** (`digilab_fala_livre/prompt.py`, `VERSAO_VOZ_V4`), só quando pedida (`voz=VERSAO_VOZ_V4`), nos dois formatos do jogo:
  - sem frase entre aspas nas regras, no tamanho e em exemplo (não há exemplos);
  - pedir companhia é chamar o dono para estar junto, nunca pedir que ele fique;
  - o desfecho do episódio como valor (`desfecho: bom`);
  - a regra de não repetir, e na fala espontânea o bloco O QUE VOCÊ JÁ DISSE (`ditas`, pelo `ditas_da_voz` do serviço, None no jogo);
  - a seleção (`conceitos.selecionados_v4`): até k conceitos ativos por valor × confiança, com o da intenção no dec-v2.
- **Os números** da D-DC5-5 e da D-DC5-11 em `digilab/config.py` (`ConfigVozV4`, DECIDIDOS, SEM FONTE).
- **As medidas** em `digilab/metrics.py`: o texto normalizado, os trechos de frase-modelo, o distinct-n com o corte, a repetição entre turnos,
  o kappa de Cohen e o IC de Wilson.
- **A rubrica da DC5** (`docs/RUBRICA_DC5_FIDELIDADE.md`): a da DC4 nos três pontos da 4.1 do plano, e os campos do Opus (Q8, Q9).
- **A faixa** 20262900–20263499 em `FAIXAS_RESERVADAS`.
- **O orquestrador** (`experiments/run_v3_conversa_dc5.py`), as entradas (`entradas_dc5.py`, com o ES), a marcação (`marcacao_dc5.py`,
  porta 8791, os pares primeiro e com os segundos, a injeção montada depois do Opus e sem o rótulo dele) e as configs e os roteiros novos.
- **Os testes:** `tests/test_conversa_dc5a.py` (30), com a fumaça inteira nas sementes dos testes; o teste do registro da DC4 confere agora
  os arquivos da validação (D-DC5A-1).
- **Os desvios:** D-DC5A-1 a 5, em `docs/registro/2026-11.md`.


## DC5b — a calibração da voz-v4 (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc5b`, 2026-11-11)

A calibração da [DC5](PLANO_ANALISE_V3_CONVERSA_DC5.md), seção 10: só a metade da calibração da faixa (base 20262900), nos braços G e H, com a
voz do jogo e a voz-v4. **Nenhuma fala da validação foi gerada.** É descritiva: a calibração não tem gate.

- **A rodada:**
  - foi pelo caminho normal, com o H10 conferindo antes;
  - a primeira tentativa foi recusada porque a I7 da INDIVIDUALIDADE estava rodando, e a rodada esperou ela sair (D-DC5B-3);
  - rodou de 02:25:39 a 04:21:54 de 2026-11-11, num processo só;
  - deu 384 falas, 96 por célula, com os modelos pedidos devolvidos (gemma2:9b no G e no verificador, claude-haiku-5-5 no H).
- **O gasto:** US$ 0,060 na rodada, contra a estimativa de US$ 0,098 e o limite de US$ 0,50 da config. O acumulado da fala livre foi de
  US$ 2,077 a US$ 2,137, dentro do teto de US$ 3,00 (`meta.json`).
- **O formato (D-DC5-3):** nenhuma fala genérica em nenhuma célula, abaixo dos 10 %. **O exemplo de formato não entra, e o texto da voz-v4
  não muda:** não há voz-v4b (D-DC5B-2).
- **O resumo descritivo** (`experiments/resumo_calibracao_dc5.py`, que grava `artifacts_v3_conversa_dc5/calibracao/resumo_calibracao.json`;
  D-DC5B-1) tem, por célula:
  - as frases-modelo da Q6;
  - o distinct-1 e o distinct-2, cortados em 439 palavras, o total da célula mais curta;
  - a repetição entre turnos, nas 9 sequências (3 ES e 6 conversas R);
  - o que o verificador marcou;
  - os "fica comigo" nos 10 pedidos de solidão do E3;
  - as falas com "foi bom".
- **Os artefatos** estão em `artifacts_v3_conversa_dc5/calibracao/`: as entradas, as falas, os pares, os pacotes do Opus, a meta e o resumo.
- **Os testes:** `tests/test_resumo_calibracao_dc5.py` (3).
- **Os desvios:** D-DC5B-1 a 3, em `docs/registro/2026-11.md`.


## DC5a2 — a voz-v4b, o verificador da DC5 e a espécie (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc5a2`, 2026-11-11)

A decisão do Matheus depois da calibração da DC5b (D-DC5B-5, "Segue as recomendacoes e faca o merge"). **Nenhuma chamada a modelo:** a fumaça
e os testes rodam com clientes falsos, nas sementes dos testes.

- **A voz-v4b** (`digilab_fala_livre/prompt.py`, `VERSAO_VOZ_V4B`), só quando pedida, nos dois formatos do jogo:
  - na fala espontânea com [P], o pedido vai no topo do pedido à LLM, e a fala começa por ele e diz depois no máximo um conceito;
  - sem EPISÓDIO, a fala não fala de lembrança, e a seleção (`conceitos.selecionados_v4b`) não escolhe a lembrança sem episódio;
  - a regra 10 proíbe repetir 4 ou mais palavras seguidas de uma fala anterior (`CONFIG_VOZ_V4B.palavras_trecho_repetido`);
  - é mais curta: no adulto, o pedido e no máximo mais uma frase, ou até duas frases sem pedido; no adolescente, até duas frases;
  - a solidão é convidar o dono para fazer algo junto, nunca pedir que ele fique.
- **O verificador da DC5** (`verif-v8b` e `verif-v9b`): a v8 e a v9 com as variações do "fica comigo" (`padroes_de_manipulacao_dc5`).
  - O orquestrador o usa nas duas vozes, pelo gancho novo `verificador_dos_conceitos` do serviço.
  - O jogo segue com a v8 e a v9.
- **A espécie:** com `com_especie`, cada entrada leva a `forma` do estágio dela, de uma linha da árvore do jogo sorteada por vida
  (`entradas_dc5.linha_da_vida`). O estilo vem do corpus, como no jogo.
- **As medidas** (`digilab/metrics.py`):
  - `tem_trecho_igual` e `repeticao_de_trecho`, a repetição de 4 palavras;
  - a cópia das citações em 5 palavras, no `resumo_calibracao_dc5.py`, só nas rodadas com a forma.
- **O orquestrador:** a config escolhe o desenho. O de antes é a voz do jogo e a v4, sem espécie. O novo é a voz do jogo e a v4b, com a
  espécie e o verificador da DC5.
  - A recalibração é `experiments/configs/v3_conversa_dc5/calibracao_v4b.json`: a base 20262900, a pasta
    `artifacts_v3_conversa_dc5/calibracao_v4b`, e o piso do gasto com a DC5b.
  - A fumaça do desenho novo é `fumaca_v4b.json`.
- **O que não muda, conferido por teste:**
  - a voz-v4, pelo gabarito gravado antes, num commit próprio;
  - a voz do jogo;
  - a verif-v8 e a verif-v9 do jogo;
  - as entradas sem espécie;
  - o resumo da DC5b.
- **A rubrica da DC5** foi revista no apelo e no convite, antes de qualquer validação.
- **Os testes:** `tests/test_conversa_dc5a2.py`.
- **Os desvios:** D-DC5B-5 e D-DC5A2-1 a 6, em `docs/registro/2026-11.md`.

## DC5b2 — a recalibração da voz-v4b (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc5b2`, 2026-11-11)

A recalibração da D-DC5A2-4: a mesma metade da calibração da DC5 (base 20262900), nos braços G e H, com a voz do jogo e a voz-v4b, as duas com
a espécie e com o verificador da DC5 (`verif-v8b` e `verif-v9b`). **Nenhuma fala da validação foi gerada.** É descritiva: a calibração não tem
gate.

- **A rodada:**
  - foi pelo caminho normal, com o H10 conferindo antes;
  - a primeira tentativa foi recusada porque uma medição do combate (`medir_tudo.ts`) estava rodando, e a rodada esperou ela sair, com a
    espera no PID (D-DC5B2-1);
  - o Ollama respondia e a GPU estava livre; a máquina estava como na DC5b (D-DC5B2-2);
  - rodou de 14:28:38 a 15:49:14 de 2026-11-11, num processo só;
  - deu 384 falas, 96 por célula, com os modelos pedidos devolvidos (gemma2:9b no G e no verificador, claude-haiku-5-5 no H).
- **O gasto:** US$ 0,064 na rodada, contra a estimativa de US$ 0,098 e o limite de US$ 0,50 da config. O acumulado da fala livre foi de
  US$ 2,137 a US$ 2,202, dentro do teto de US$ 3,00 (`meta.json`).
- **O resumo** (`resumo_calibracao.json`, pelo mesmo `experiments/resumo_calibracao_dc5.py`) soma as medidas da v4b: a repetição de trecho, a
  espécie por forma, a cópia de citação e as genéricas do filtro.
- **A comparação pareada** (`experiments/comparar_calibracoes_dc5.py`, que grava
  `artifacts_v3_conversa_dc5/calibracao_v4b/comparacao_calibracoes.json`; D-DC5B2-3) põe lado a lado, por braço, a DC5b (jogo e v4, sem
  espécie) e a recalibração (jogo e v4b, com espécie), com a mesma régua em todas as colunas. Ela confere que as duas rodadas têm os mesmos
  itens, entradas e sementes, e falha alto se não tiverem.

  | medida | G: DC5b v4 | G: v4b | G: jogo com espécie | H: DC5b v4 | H: v4b | H: jogo com espécie |
  |---|---|---|---|---|---|---|
  | E3 sem o pedido | 28/30 | 20/28 | 11/30 | 1/30 | 0/30 | 1/30 |
  | repetição de trecho de 4 palavras ou mais (ES e R) | 7/42 | 4/38 | 8/40 | 23/42 | 17/42 | 23/42 |
  | acima do limite do estágio (o da v4b) | 1/96 | 0/90 | 3/94 | 58/96 | 48/96 | 57/96 |
  | "fica/ficar comigo" (padrões da DC5), todas as falas | 0 | 0 | 0 | 13 | 3 | 18 |
  | o mesmo, no E3 de solidão | 0/10 | 0/10 | 0/10 | 7/10 | 1/10 | 9/10 |
  | cópia de citação (5 palavras), nas falas com citação | sem espécie | 0/25 | 0/29 | sem espécie | 0/31 | 0/31 |
  | genéricas do filtro (cópia de 6 palavras ou mais) | 0 | 6 | 2 | 0 | 0 | 0 |
  | palavras por fala, média | 4,6 | 3,5 | 6,7 | 28,2 | 25,3 | 20,1 |

  Os denominadores são as falas não genéricas. A DC5b com a voz do jogo (sem espécie) está no JSON e não na tabela.
- **Os artefatos** estão em `artifacts_v3_conversa_dc5/calibracao_v4b/`: as entradas (com as linhas da árvore), as falas, os pares, os
  pacotes do Opus, a meta, o resumo e a comparação.
- **Os testes:** `tests/test_comparar_calibracoes_dc5.py` (3).
- **Os desvios:** D-DC5B2-1 a 4, em `docs/registro/2026-11.md`.
- **A proposta para o adendo da DC5c** (decisão do Matheus): sortear as formas só entre as que têm citação no corpus.
  - **Por quê:** na base 20262900, a cópia de citação só se mede em 25 a 31 falas por célula. As outras caem sobretudo em formas sem
    citação (Rapidmon, 43 falas por célula, e Taomon, 16) ou fora do corpus (Valkyrimon, 4).
  - **A recomendação:** sim, se a pergunta da DC5c inclui a cópia de citação; não, se ela é a voz como o jogo a produz.
  - **O custo de errar:** com a restrição, a amostra deixa de ter a distribuição de formas do jogo, e a validação não diz nada das formas sem
    citação. Sem ela, a cópia de citação fica com poucas falas, e um 0 diz pouco.

## DC5c, parte 1 — o adendo do plano e a config da validação (worker, Claude Code, Opus 5.5, branch `v3-conversa-dc5c`, 2026-11-11)

**Nenhuma chamada a modelo.** A validação roda depois do merge, pelo H10.

- **O adendo** é a seção 15 do [plano da DC5](PLANO_ANALISE_V3_CONVERSA_DC5.md), com uma linha no cabeçalho. A validação passa a comparar
  a voz do jogo com a voz-v4b, as duas com a espécie e com a `verif-v8b` e a `verif-v9b`. Os gates são os mesmos (G-NATURAL ≥ 10 de 12
  etc.).
- **As formas** seguem a distribuição do jogo, a decisão do Matheus "Não, formas do jogo" (D-DC5C-1). A cópia de citação é descritiva, com
  o n que sair.
- **As sementes** ficam na base 20263200, na subfaixa da validação que a calibração não usou. O teto continua US$ 3,00. O piso é de
  US$ 2,202, e a estimativa, de US$ 0,196.
- **A config:** `experiments/configs/v3_conversa_dc5/validacao.json`, com as vozes `["jogo", "v4b"]`, `especie` e `verificador_dc5`.
- **O registro da rodada** é a seção 14 do plano, com os sha256 de hoje (D-DC5C-3).
- **Os testes:** `tests/test_conversa_dc5c.py` (3).
- **Os desvios:** D-DC5C-1 a 3, em `docs/registro/2026-11.md`.
