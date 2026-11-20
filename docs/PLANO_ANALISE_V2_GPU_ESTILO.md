# Plano de análise — GPU-ESTILO: o estilo da espécie com o corpus em português (V2, fase 0)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status: **registrado antes da run** (2026-10-01). Tarefa `docs/TAREFA_V2_GPU_ESTILO.md`; depende do PR #107 (corpus reescrito em
português) na `main`. Fila da GPU: posição 1 (único Ollama nesta rodada). Valores sem fonte estão marcados PROPOSTO.

**Pergunta.** Com o corpus reescrito em português, o estilo da espécie volta a funcionar no gemma2:9b sem japonês e sem saída
rejeitada, e o comando pelo chat continua no gate com o estilo ligado?

## 1. O que não muda

Prompt (`livre-v6` na medida do estilo, `livre-v8` no comando), verificador, corpus (o da `main`, sha `785f7834…`), servidor,
`corpus.carregar` (filtro do alfabeto), as 30 mensagens da medida do estilo e as 60 do comando (`situacoes.MENSAGENS_COMANDO`), os
pets das duas medidas, o modelo (`gemma2:9b`, nenhum outro carregado). As rodadas 1–3 do comando e `artifacts_voz/estilo_latino/` não
são refeitas: medem o corpus de antes.

## 2. Medida A — o estilo na conversa (`experiments/medir_estilo_latino.py --saida estilo_portugues`)

- O mesmo desenho de `artifacts_voz/estilo_latino/`: 30 mensagens × 3 espécies (Angemon, Gabumon, Garurumon), uma semente por
  mensagem (`20261006 + i`), prompt `livre-v6`. Sai em `artifacts_voz/estilo_portugues/` (pasta nova).
- Com o corpus em português o filtro não tira nada (0 itens não latinos), então o bloco de estilo "com filtro" é igual ao "sem filtro"
  item a item: o script roda **um modo só** (o que o servidor manda) e registra que o outro é idêntico por construção. Rodar os dois
  seria gastar a GPU com o mesmo pedido.
- Métricas: respostas rejeitadas por letra fora do alfabeto latino (n / 30); outros erros; falas entregues com letra não latina
  (0 por construção, `saida.ler` rejeita a saída inteira; conferido no artefato).
- Comparação (descritiva): `estilo_latino` com o filtro 1/30 rejeitada, sem o filtro 26/30.
- **Critério (PROPOSTO):** o estilo "funciona sem japonês" se as rejeitadas por letra não latina ficam **≤ 1/30** (o nível do filtro
  de antes). Acima disso, a reescrita não resolveu e o relato diz quais espécies e mensagens.

## 3. Medida B — o comando com o estilo ligado (rodada 4, `python experiments/avaliar_fala.py --livre --comando --rodada 4`)

- `RODADAS_COMANDO[4]`: pasta `rodada4_estilo`, prompt `livre-v8`, **estilo da espécie ligado** (como o servidor manda no jogo), as
  mesmas 60 mensagens, 3 pets (Angemon, Greymon, Gabumon), **sementes 20261501, 20261601, 20261701** (reservadas pelo coordenador; a
  mensagem i usa semente + i; nenhuma cruza as rodadas 1–3: teste `test_rodada4_do_comando_com_estilo_e_sementes_novas`).
- **Gate (PROPOSTO, o de sempre):** falsos positivos nas negativas ≤ 5%; imperativos claros ≥ 80%. Sai de `resumo.json`.
- Comparação (descritiva, mesmas mensagens e sementes diferentes, sem teste estatístico): rodada 3 (sem estilo: 0/60 falsos positivos,
  51/60 imperativos, 0 saídas rejeitadas) e rodada 2 (com o estilo do corpus antigo: 160/180 saídas rejeitadas, imperativos 6,7%).
  Reporta-se também a matriz de confusão dos imperativos, as saídas rejeitadas pelo parser (n / 180) e a latência p50/p90.

## 4. Ordem, tempo e regras

1. Commit deste plano e das mudanças mínimas de código (rodada 4 em `avaliacao.py`, `--saida` no script do estilo, testes).
2. Medida A (~8 min), depois a Medida B (~20 min, pela latência da rodada 3); o modelo é descarregado no fim de cada uma.
3. Uma run de cada; nada se ajusta olhando a amostra. Se uma run cair no meio, roda de novo inteira na mesma pasta (os artefatos
   anteriores da pasta são apagados antes), e o registro diz que caiu.
4. Nenhum número no relatório sem o artefato (`resumo.json`, `respostas.jsonl`, `RELATORIO.md` de cada pasta).

## 5. Leitura

- A passa e B passa: os itens "corpus" e "rodada do comando com o estilo" da fase 0 fecham; o servidor segue como está (ele já manda o
  estilo com o filtro; com o corpus novo o filtro não tira nada).
- A passa e B falha: o estilo não quebra mais o parser, mas pesa no comando; a decisão (estilo desligado na conversa com comando, ou
  prompt novo em rodada própria) é do Matheus, fora desta tarefa.
- A falha: a reescrita não bastou; o relato lista espécies e mensagens, e o filtro de antes fica como está (ele não tira nada agora,
  então o servidor passaria a mandar o estilo sem proteção: isso vira pendência).
