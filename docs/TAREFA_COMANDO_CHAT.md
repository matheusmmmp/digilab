# TAREFA — Comando pelo chat do pet (2026-09-30)

Decisão do Matheus (2026-09-30): o chat da fala livre passa a poder **agir no pet**. O jogador escreve "vai comer" e o
pet come, pelo mesmo caminho do botão Alimentar. Isso muda a regra de 2026-09-28 "o que o jogador escreve não ensina o
pet": o texto do jogador passa a agir, **mediado por um catálogo fechado**. Registrar a mudança no `CLAUDE.md`
(seção da fala livre) e em `docs/REGISTRO_DESVIOS.md`.

Só no jogo web (`web/app/`) e no servidor da fala livre. A pesquisa em Python não muda. Nenhuma mecânica nova de jogo:
o comando só dispara ações que já existem.

## 1. Princípio

- A LLM **propõe**; o app **valida**; o motor **executa** como ação do dono. A LLM nunca decide a ação do pet (isso é a
  política), nem escreve no registro.
- No registro do pet entra só o evento `d` de sempre (a ação do dono), pelo mesmo caminho do botão. A saída da LLM fica
  no log de apresentação (`<chave>.fala.jsonl`). **Replay, assinaturas dos pets v1–v8, gabaritos e paridade não mudam.**
  Não usa o modo livre gravado.
- Catálogo fechado = `AcaoDono` (`web/app/motor/tipos.ts`, linha 5): alimentar, limpar, brincar, acariciar, elogiar,
  repreender, petisco, levar_ao_banheiro, tratar_lesao. Nesta tarefa **só essas**. Treino, luta e itens ficam de fora
  (próxima tarefa, se a taxa de erro permitir).
- Qualquer coisa fora do catálogo vira `null`. Texto do jogador é entrada não confiável, como já é hoje.

## 2. Servidor (`digilab_fala_livre/`, `servidor/fala_livre.py`)

- Prompt novo `livre-v7` (ao lado das versões existentes; as anteriores não mudam e os artefatos das rodadas 1–4 da voz
  reproduzem). Na situação `conversa`, o pedido ganha o bloco COMANDO: a lista das ações com uma frase cada, a regra
  "só quando o dono mandou ou pediu de forma clara; dúvida = null; se o dono falou de não fazer = null".
- `prompt.esquema(est)` ganha o campo `comando` com `enum` = catálogo + `null` (o Ollama aceita esquema JSON; o gemma2:9b
  não tem chamada de ferramenta nativa). Fala espontânea: o campo não existe.
- `saida.FalaLivre` ganha `comando: str | None`; `ler` falha alto se o valor não está no catálogo (vira `SaidaInvalida`,
  a fala cai na genérica **e o comando é null**).
- A resposta de `/api/fala-livre` devolve `comando` (ou `null`). `versao_prompt` diz `livre-v7`.
- Só biblioteca padrão; `digilab/` não importa nada daqui (teste AST existente).

## 3. App (`web/app/src/`)

- `falaLivre.ts`: `RegistroFala` ganha `comando: AcaoDono | null` e `comando_executado: boolean`. O log de apresentação
  sobe para `VERSAO_LOG = 2` e continua lendo a 1 (campos ausentes = null/false).
- Validação no app, de novo: o valor tem que estar em `AcaoDono`; o pet não pode estar morto nem nascendo; as ações
  v4 (petisco, banheiro, tratar_lesao) só em pets `versao >= 4`; `tratar_lesao` só com lesão. Fora disso, não executa e
  o registro fica com `comando_executado: false`.
- **Confirmação (primeira versão; substituída pela execução direta em 2026-10-01, decisão do Matheus):** o comando não executa sozinho. O balão da resposta mostra um chip com a ação
  ("Alimentar?") e o toque executa. Ao tocar, o app chama o mesmo caminho do botão da tela do Pet
  (`TelaPet.tsx`, `agir`, linha 381: `mudarMotor(mm => mm.observar(a))`, flash e `ajustarVelocidadeChamado`).
  Extrair esse `agir` para um módulo compartilhado (`src/acoes.ts`) e usar nos dois lugares: não duplicar.
- O chip some quando o pet responde de novo, quando o jogador manda outra mensagem ou depois de 60 s de parede.
- A fala seguinte do pet vê a ação no estado (motivos, recusa pela obediência) como qualquer clique: nada a fazer aqui.
- Tela Conversar (`telas/conversar/TelaConversar.tsx`): o chip na última resposta; o histórico mostra "✓ alimentou"
  nas que foram executadas.

## 4. Testes e medição

- Vitest: `ler` do servidor não é testável em TS; testar a validação do app (catálogo, morte, versão do pet, lesão), o
  chip, o log versão 2 lendo a 1, e que o registro do pet recebe **exatamente** o evento `d` que o botão gravaria (mesma
  assinatura depois de "vai comer" + toque e depois do clique em Alimentar).
- Python: `tests/` para `ler` (valor fora do catálogo falha, null passa, ausência na espontânea passa) e para o esquema.
- Gabaritos `vidas_*.json`, `paridade_ts`, `constantes.test.mjs`, e2e: têm que passar iguais.
- Rodada de avaliação, `experiments/avaliar_fala.py --livre --comando` → `artifacts_fala_livre/comando/rodada1/`:
  60 mensagens escritas à mão em `digilab_fala_livre/situacoes.py` (20 imperativos claros, 20 negativas e perguntas
  que **não** devem virar comando, 20 conversa sem comando), gemma2:9b, 3 sementes. Métricas: acerto por classe,
  falsos positivos (o que importa). Gate PROPOSTO: falsos positivos ≤ 5% nas negativas; imperativos claros ≥ 80%.
  Só com o gate passando o Matheus decide se libera execução direta (sem chip) para os imperativos.
- Nenhum número no relatório sem artefato.

## 5. Fora do escopo

- Treino, luta, itens, evoluir, cruzar por comando. Comando na fala espontânea. LLM escolhendo ação do pet.
- MCP de verdade (expor o jogo a um cliente externo): ideia para os donos sintéticos com persona, outra tarefa.
- Custo: a chamada é a mesma do chat mais ~30 tokens de saída.
