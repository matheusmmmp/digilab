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
- LLM. Só templates.
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

## Critério de pronto

- [ ] Parte A: V1 e combate V2 reproduzem artefatos idênticos; testes de
      honestidade e cobertura passando; diário gerado para um log de cada
      braço e para partidas entre bots em cada estágio
- [ ] Parte B (se a pré-condição existir): run `ARENA_V1_MEMORIA` com gate
      rodado e artefatos gravados
- [ ] Todos os testes anteriores passando
- [ ] `CLAUDE.md` atualizado (mapa, comandos, estado, pendências)

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
