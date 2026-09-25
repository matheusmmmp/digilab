# Tarefa — memória, motivo e expressão por estágio (revisada para o combate V2)

Leia o `CLAUDE.md` inteiro e `docs/ESPEC_COMBATE_V2.md` antes de começar.
Todas as regras do `CLAUDE.md` valem: `engine.py` não muda, determinismo
bit a bit, só stdlib em `digilab/`, parâmetros em `config.py`, falhar alto.

## Pré-condições

- **Parte A:** bateria do combate V2 **APROVADA** em
  `artifacts_combate_v2/gates.json`. Se não estiver, não comece: reporte.
- **Parte B:** além disso, ablação instinto × bandit registrada em disco.
  Se não existir, pare ao fim da Parte A e reporte.

## Objetivo

O pet lembra ações do dono, isso influencia o comportamento, e o jogador
vê o motivo — na vida e no combate — de forma que muda com o estágio: o
bebê só mostra humor; o adulto diz "hoje recusei comida porque você
demorou ontem" ou "esquivei porque você ia usar o golpe pesado".

Princípio que decide tudo: **a fala nunca inventa causa.** O motivo é um
registro estruturado produzido pela própria decisão; a expressão só pode
mostrar menos do que o motivo contém, nunca mais.

## Divisão

- **Parte A — motivo unificado + expressão.** Somente leitura: não muda
  nenhuma decisão, nem na vida nem no combate. Usa bots do combate V2 para
  testar a expressão de combate, já que pets ainda não lutam no V2.
- **Parte B — memória que muda comportamento.** Muda a política de vida e,
  portanto, o protocolo.

Não comece a Parte B antes de a Parte A passar em todos os testes.

## Fora de escopo

- Plugar pets no combate V2 (tarefa futura da arena V2).
- Memória de vida alterando gambits, `CondicaoFisica` ou qualquer coisa do
  combate. **A memória nunca entra em `CondicaoFisica`**: condição é
  cuidado, memória é estilo; misturar reabre o confundidor.
- Novas ações, novas condições no catálogo de gambits.
- `web/digilab.html`.

---

## Parte A — motivo unificado e expressão

### A1 — `Motivo` único para vida e combate

Dataclass frozen em `digilab/motivo.py`:

- `origem` ∈ {`vida`, `combate`}
- `tick` (vida) ou `turno` (combate)
- `acao`
- `fatores`: tupla de nomes (0 a 2 elementos)
- `evento_ref`: tupla de referências ao log de origem (índice de evento na
  vida; turno(s) na partida), pode ser vazia
- `intensidade` em [0, 1] (vida) ou `None` (combate, onde a regra é
  categórica)
- `exploracao`: bool

**Vida (bandit Thompson linear):** usar os pesos amostrados que de fato
decidiram. `contribuicao_i = x_i * (theta_escolhida_i - media dos theta_i
das demais acoes)`. Fator = maior |contribuição| se acima de
`LIMIAR_MOTIVO`; senão `fatores` vazio. **`PoliticaInstinto`:** a regra que
disparou. Calcular o motivo não consome rng nem altera estado. Não mudar a
assinatura do `Protocol` `Politica`; expor via `estado_interno()` ou
atributo somente leitura. Se impossível, pare e proponha.

**Combate:** converter o motivo que o combate V2 já registra (índice da
regra ou `exploracao`) por um **adaptador** em `digilab/motivo.py`. Não
alterar `digilab/combate_v2/`. `fatores` = condições da regra disparada
(a regra final `sempre` conta como sem fator). `evento_ref`:

- `oponente_preparando` → turno da preparação
- `oponente_repete` / `oponente_frequente` → turnos da janela que
  satisfizeram a condição
- condições de estado próprio (hp, guts, distância) → turno corrente

Exploração (ε) → `exploracao = True`, `fatores` vazio.

### A2 — estágio de vida (provisório)

Derivado da idade em dias simulados, limiares em `ConfigExpressao`:
`bebe`, `crianca`, `adolescente`, `adulto`. Marcado PROVISÓRIO no código e
no config: quando a evolução existir, o estágio vem dela. Em partidas entre
bots, o estágio é parâmetro explícito.

### A3 — `digilab/expressao.py`

Função pura `expressar(motivo, estagio, humor) -> Expressao`.
`Expressao` (frozen): `canal`, `conteudo`, `motivo_ref`.

| estágio | canal | o que pode revelar |
|---|---|---|
| bebê | `emote` | só humor (vida) ou reação (combate); **nunca** a causa |
| criança | `icones` | ação + ícone do fator |
| adolescente | `fragmento` | palavras soltas do fator |
| adulto | `frase` | frase completa com fator e evento referenciado |

Regras:

- Textos e ícones em tabela declarativa dentro do pacote. **Cobertura
  obrigatória:** toda feature de vida e toda condição do catálogo de
  gambits tem entrada para todos os estágios; faltando alguma, levanta erro
  na carga. Arte continua placeholder original, sem asset externo.
- Sem fator (ou exploração) → adulto responde de forma genérica
  ("não sei, só quis"). Nunca preencher com causa plausível.
- Com 2 fatores, o adulto pode citar os dois; estágios anteriores citam só
  o primeiro.

### A4 — diário

`experiments/diario.py`:

- `--log <arquivo>`: vida de um pet; expressão por tick com motivo ao lado
- `--partida <arquivo> --estagio <e>`: partida do combate V2; expressão por
  turno para cada lutador

Ferramenta de inspeção, não interface de jogo.

### A5 — testes da Parte A

- **Nada mudou:** run canônica V1 reproduz `artifacts/` idêntico; bateria
  canônica do combate V2 reproduz `artifacts_combate_v2/` idêntico.
  `ConfigExpressao` não pode entrar em nenhum desses hashes; verifique como
  são montados e reporte.
- Calcular motivo não altera estado de rng (vida e combate).
- **Honestidade:** para todo estágio e origem, o conteúdo só cita fatores e
  eventos presentes no motivo; bebê nunca cita fator; motivo sem fator
  nunca vira causa; no combate, todo fator citado é condição que de fato
  valia naquele turno (conferir contra o estado reproduzido do log).
- Cobertura da tabela de textos (falta levanta erro).
- Replay reproduz a mesma sequência de motivos e expressões.

---

## Parte B — memória que muda comportamento de vida

### B1 — `digilab/memoria.py`

Features de memória curta, **função pura dos eventos observados**. Nada
salvo fora do log; o replay reconstrói tudo. Parâmetros (janela,
decaimento, normalização) em `ConfigMemoria`. Candidatas:

- latência do dono no último pedido de cada necessidade
- repreensões e elogios recentes, com decaimento
- tempo desde a última interação

Cada feature carrega o índice do evento de origem (`evento_ref`).
Alimentada pelo que já chega à política (`observar()` e/ou contexto de
`agir()`). Se o evento necessário não chegar sem alterar `engine.py`, pare
e reporte o que falta.

A tabela de textos da A3 ganha entradas para as features novas (cobertura
continua obrigatória).

### B2 — a recusa

Exemplo-guia: "recusar comida porque o dono demorou". Verifique se o
espaço de ações da vida permite recusar uma ação do dono. **Se não
permitir, não crie a ação**: reporte o que seria preciso e onde.

### B3 — protocolo

- Novo protocolo `PROTOCOLO_ARENA_V1_MEMORIA`: arena V1 + features de
  memória, campos novos PROPOSTO. O nome `ARENA_V2` fica **reservado** para
  pets no combate V2.
- Features entram igualmente em todos os braços, inclusive o aleatório.
- Artefatos em `artifacts_v1_memoria/`. Não sobrescrever `artifacts/` nem
  `artifacts_combate_v2/`.
- O resultado principal aqui é a **divergência comportamental** (JSD); a
  vitória na arena V1 é secundária, porque o combate V1 será substituído.

### B4 — testes da Parte B

- Replay bit a bit.
- Orçamento de interações idêntico entre braços.
- Todo `evento_ref` aponta para evento existente e do tipo esperado.
- Nada em `digilab/combate_v2/` importa ou lê `memoria.py` (teste por AST).

---

## Parte C — fala por LLM (acrescentada em 2026-09-24, após as Partes A e B)

A proibição de LLM foi retirada do projeto. Esta parte troca o **texto** da fala do
adolescente e do adulto por uma frase gerada por LLM, sem mexer em nada do que
decide: motivo, política, gambits, combate e registro continuam exatamente como nas
Partes A e B. O princípio continua o mesmo — **a fala nunca inventa causa** — e agora
ele precisa ser garantido por validação, não só por construção.

### C1 — onde a LLM entra (e onde não entra)

- Entra **só** na camada de expressão, depois que o `Motivo` já existe.
- Estágios `adolescente` e `adulto` podem usar a LLM. `bebe` e `crianca` continuam só
  com emote e ícones da tabela (A3): não há texto livre para a LLM produzir ali.
- **Nunca** entra em `digilab/` (regra de só-stdlib), nas decisões, no registro, no
  replay, nos artefatos de pesquisa nem nos hashes de protocolo. Runs canônicas,
  bateria, diário e legibilidade continuam só com templates e bit a bit.
- A frase gerada é **exibição**: se a LLM falhar, demorar ou for reprovada na
  validação, mostra-se o template da A3, sem erro para o jogador.

### C2 — arquitetura

- `servidor/servidor_local.py` (fora de `digilab/`): substitui o `python -m http.server`.
  Serve os arquivos estáticos como hoje e expõe `POST /api/fala`.
- `servidor/fala_llm.py`: monta o pedido, chama a API do Claude pelo SDK oficial
  (`anthropic`, dependência só do servidor) e valida a resposta.
- A **chave da API fica só no servidor** (credencial do ambiente: `ANTHROPIC_API_KEY`
  ou perfil do `ant`). Nunca no HTML, no navegador ou no git.
- `web/digilab_sprites.html`: quando o servidor responde, usa a frase da LLM; senão,
  o template. Um interruptor na interface liga e desliga a fala por LLM.
- Modelo: parâmetro de configuração do servidor. Padrão `claude-haiku-4-5` (o mais barato
  e rápido; escolha do pesquisador em 2026-09-24). Com `claude-opus-5` usa esforço baixo e
  fallback de recusa; o Haiku não aceita `effort` e uma recusa nele cai no template.

### C3 — o que a LLM recebe

Só o que o jogador poderia legitimamente ouvir:

- o `Motivo` (ação, fatores, `evento_ref`, exploração), o estágio e o humor;
- o texto de cada fator e de cada ação vindo da tabela da A3 (o "significado" permitido);
- o template correspondente, como exemplo do que pode ser dito.

Nada de estado interno do bandit, pesos, log inteiro ou histórico de conversa. Cada
fala é um pedido independente.

### C4 — o que a LLM devolve e como é validado

Saída estruturada (`output_config.format`, esquema JSON):

- `texto`: a frase, em português, primeira pessoa, no máximo 1 frase (adolescente:
  fragmento curto, até 6 palavras);
- `fatores_citados`: lista dos nomes de fator que a frase menciona.

Validação no servidor (reprovou → template da A3):

1. `fatores_citados` ⊆ `motivo.fatores` (e vazio se exploração ou sem fator);
2. nenhum marcador de fator **ausente** do motivo aparece no `texto` (mesma varredura
   de marcadores da A5);
3. sem fator → o texto tem de dizer que não sabe o porquê (sem causa plausível);
4. adolescente cita no máximo o primeiro fator; adulto no máximo os dois;
5. números de evento/turno citados ⊆ `evento_ref`.

Limite honesto: a varredura de marcadores não pega sinônimos. Por isso a C6 exige uma
avaliação com juiz antes de ligar a LLM por padrão.

### C5 — determinismo e custo

- Cache por `(motivo, estágio, faixa de humor, modelo, versão do prompt)`: o mesmo
  motivo mostra a mesma frase na mesma sessão. A frase não é reproduzível entre
  execuções e isso é aceito, porque ela não entra em nada que precise de replay.
- Limite de chamadas por minuto no servidor e timeout curto; acima disso, template.
- **Teto de gasto total** (padrão US$ 2, persistido; decisão do pesquisador em 2026-09-24): reserva o
  custo máximo antes de chamar, acerta pelo uso real, conta o pior caso em erro; no teto, só template.
- Cada fala é uma chamada paga. O diário e a legibilidade não chamam a LLM.

### C6 — testes e avaliação

- Testes sem rede (cliente falso): validação reprova fator inventado, marcador
  ausente, causa em motivo sem fator, excesso de fatores e evento fora do
  `evento_ref`; qualquer falha cai no template; bebê e criança nunca chamam a LLM.
- Teste de fronteira: nada em `digilab/` importa `servidor/` nem `anthropic` (AST).
- Todos os testes anteriores continuam passando; runs canônicas intactas.
- **Avaliação com juiz (antes de ligar por padrão):** amostra de motivos reais dos
  diários (vida e combate, todos os estágios), gerar falas e medir, com um juiz,
  a fração que cita causa fora do motivo. Custo estimado e aprovado antes de rodar.

### C6b — provedor local (Ollama), acrescentado em 2026-09-24

- Interface de provedor em `servidor/fala_llm.py`: `disponivel()` e `gerar(sistema, pedido, esquema,
  semente)`. Validação, cache, limite por minuto e queda para o template ficam acima dela e valem
  para todos os provedores; o teto de gasto só para provedor com custo.
- `ProvedorOllama` (padrão; `qwen2.5:3b`, escolhido para a RTX 2060 de 6 GB do pesquisador): chama
  `POST /api/chat` do Ollama local só com a biblioteca padrão, com o esquema JSON em `format`,
  temperatura baixa, semente derivada do motivo (mesmo motivo, mesma frase), resposta curta e o
  modelo mantido carregado; aquecimento ao ligar o servidor. Sem custo por chamada.
- `ProvedorClaude`: o de antes (Haiku 4.5, teto de gasto).
- `--provedor auto|ollama|claude|nenhum`. `auto`: Ollama se estiver pronto; senão Claude se houver
  chave; senão fica com o Ollama, que passa a valer quando for ligado (status consultado ao vivo).
- Avaliação C6: `experiments/avaliar_fala.py` gera falas para 200 motivos reais (metade com fator),
  mede a fração barrada pela validação e sorteia 50 aprovadas em `revisao.csv` para revisão humana
  ("cita causa fora dos fatores?"). Com o Ollama não tem custo; com o Claude exige `--aceito-custo`.

### C7 — critério de pronto

- [x] servidor local servindo a página e `POST /api/fala`, chave só no servidor
- [x] validação C4 com testes sem rede; falha sempre cai no template
- [x] interruptor na web; sem servidor/chave a página funciona como hoje
- [x] avaliação C6 rodada e reportada (fração de causas inventadas): Ollama `qwen2.5:3b`, 200 motivos,
  `artifacts_fala/ollama_qwen2.5-3b_fala-v1/` e `..._fala-v2/`. Falta a revisão humana de
  `revisao.csv` (50 falas aprovadas), que mede o que a validação não pega (sinônimos).
- [x] `CLAUDE.md` atualizado

---

## Critério de pronto

- [x] Parte A: V1 e combate V2 reproduzem artefatos idênticos; testes de
      honestidade e cobertura passando; diário gerado para um log de cada
      braço e para partidas entre bots em cada estágio
- [x] Parte B (se a pré-condição existir): run `ARENA_V1_MEMORIA` com gate
      rodado e artefatos gravados
- [x] Todos os testes anteriores passando
- [x] `CLAUDE.md` atualizado (mapa, comandos, estado, pendências)

## O que reportar

Sem rodeios, nesta ordem:

1. **Legibilidade na vida:** fração de decisões com fator claro, por
   braço. Se for baixa, o pet adulto vai dizer "não sei" quase sempre —
   diga primeiro.
2. **Legibilidade no combate:** por bot, fração de decisões por regra com
   fator vs exploração vs regra final `sempre`; regras que nunca disparam.
3. Fatores mais frequentes por braço (atencioso vs aleatório).
4. Parte B: JSD entre braços com memória vs sem memória; o gate passou?
5. Onde parou por exigir mudança em `engine.py`, no `Protocol`, no espaço
   de ações ou em `combate_v2/`.

Nenhum número no relatório sem o artefato que o gerou.
