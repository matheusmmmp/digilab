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
