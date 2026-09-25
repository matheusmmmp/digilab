# Adendo — memória, emoção e habituação inspiradas no Dwarf Fortress

Texto como recebido do pesquisador (2026-09-25).

Este adendo **altera** duas tarefas já escritas. Leia junto com elas:

- **Parte 1** substitui a seção B1 (features de memória) da
  `docs/TAREFA_MEMORIA_EXPRESSAO.md`. É executada dentro daquela tarefa.
- **Parte 2** complementa a `docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md` e é
  executada depois dela, porque usa o temperamento.

Todas as regras do `CLAUDE.md` valem. Em especial: nada de rng aqui. O
Dwarf Fortress sorteia quando um anão relembra algo; no Digilab, isso é um
cronograma determinístico.

---

## Parte 1 — memória por espaços (substitui a B1)

### Ideia

Em vez de um conjunto de features com decaimento, o pet tem **poucos
espaços de memória**, uma memória por categoria, e a mais forte vence.
Relembrar reaplica o efeito. É o mecanismo por trás de "recusei comida
porque você demorou ontem".

### Categorias (PROPOSTO, em `ConfigMemoria`)

| categoria | evento de origem | intensidade |
|---|---|---|
| `demora` | chamado atendido com atraso ou perdido | latência normalizada pela janela, limitada a 1 |
| `bronca` | repreensão | 1,0 |
| `elogio` | elogio | 1,0 |
| `carinho` | carinho/brincadeira atendidos | 0,5 |
| `sujeira` | cocô no chão | 0,5 (**inativa** até a `TAREFA_CUIDADO_CORPORAL`) |
| `treino_forcado` | treino forçado | 1,0 (**inativa** até a `TAREFA_TREINO_SOMBRIO`) |

Categoria inativa existe no catálogo, mas nunca recebe memória até a
tarefa correspondente ligá-la. Categoria desconhecida levanta erro.

### Espaços

- **Curto prazo:** `N_CURTO = 4` espaços; no máximo um por categoria.
  - Mesma categoria já presente: a nova substitui se for mais forte; senão
    é descartada.
  - Categoria ausente e espaços cheios: substitui a mais fraca se for mais
    forte que ela; senão é descartada.
- **Duração no curto prazo:** `D_CURTO_H = 12` horas simuladas (as
  durações de estágio foram cortadas pela metade).
- **Promoção:** ao fim de `D_CURTO_H`, a memória vai para o **longo
  prazo** (`N_LONGO = 2` espaços, mesma regra de uma por categoria) se for
  mais forte que a mais fraca de lá; senão é descartada. Longo prazo é
  permanente até ser substituído.
- **Relembrar:** a cada `R_H = 4` horas acordado, cada memória ativa é
  relembrada e sua ativação volta à intensidade original, decaindo até a
  próxima relembrança. Cronograma fixo, sem sorteio.
- Empates de intensidade: vence a mais recente. Documentar e testar.

### Features para o bandit

Uma feature por categoria ativa: ativação atual da memória daquela
categoria (0 se vazia), somando curto e longo prazo com teto 1. Cada
feature carrega `evento_ref` do evento que criou a memória, para o
`Motivo`.

Tudo continua sendo função pura dos eventos do log; o replay reconstrói os
espaços inteiros.

### Testes

- Nunca mais de `N_CURTO`/`N_LONGO` memórias; nunca duas da mesma
  categoria no mesmo prazo.
- Mais forte vence; descarte e promoção seguem as regras acima.
- Relembrança acontece exatamente no cronograma.
- Replay reproduz os espaços bit a bit.
- Motivo com fator de memória aponta para o evento que criou a memória.

### O que reportar (acrescentar ao relatório da tarefa de memória)

- Ocupação média dos espaços por braço e categorias mais frequentes.
- Fração de motivos que citam uma memória. Se for quase zero, a memória
  existe mas não muda comportamento: diga primeiro.

---

## Parte 2 — emoção, extremos e habituação (depois da personalidade)

### 2.1 Emoção filtrada pelo temperamento

Todo evento que gera memória também gera uma **emoção**, e a emoção
depende do temperamento: o mesmo atraso irrita o rancoroso e entristece o
sensível.

- Tabela declarativa `categoria × temperamento → emoção` com valência em
  [−1, 1]. Exemplo para `demora`: rancor > 0,2 → raiva; sensibilidade
  > 0,2 → tristeza; senão → incômodo. Se dois eixos passarem do limiar,
  vence o de maior módulo.
- A valência multiplica a intensidade da memória: emoção forte, memória
  forte.
- A emoção vai para a camada de expressão (emote no bebê, palavra no
  adolescente, frase no adulto). Cobertura obrigatória da tabela: toda
  categoria ativa tem emoção para todas as combinações.
- Sem efeito direto em stats nem em combate.

### 2.2 Só descrever o que é extremo

Um eixo de temperamento ou de caráter só gera descrição quando
`|valor| ≥ 0,2` (o Dwarf Fortress não descreve traços na faixa central).
Pet com eixo neutro não recebe texto sobre ele. Limiar em
`ConfigExpressao`.

### 2.3 Habituação

Eventos negativos repetidos da mesma categoria perdem efeito:

`intensidade_efetiva = intensidade * H ** repeticoes_recentes`

- `H = 0,8` (PROPOSTO); `repeticoes_recentes` = eventos da mesma categoria
  nas últimas 12 horas simuladas.
- A teimosia acelera a habituação a broncas (H menor quando teimosia > 0).
  Fórmula em config.
- **A habituação reduz também o sinal de recompensa que chega ao bandit**
  para aquela categoria. Isso muda o aprendizado, então fica atrás de uma
  flag `habituacao_ligada`.

### 2.4 Protocolo e runs

- Entra no `PROTOCOLO_ARENA_V1_PERSONALIDADE` como campos PROPOSTO.
- Rodar com `habituacao_ligada` verdadeiro e falso, com os mesmos ovos.
  A emoção e os extremos são somente leitura e não podem mudar nada.

### 2.5 Testes

- Emoção e descrição de extremos não alteram nenhum artefato (equivalência
  com a run sem elas).
- Tabela de emoções com cobertura completa (falta levanta erro).
- Habituação: intensidade cai como a fórmula; zera o efeito da flag
  desligada.
- Replay bit a bit.

### 2.6 O que reportar

1. **A habituação enfraquece o sinal do dono atencioso?** Compare a
   divergência entre braços (JSD) e o resultado da arena com e sem
   habituação. Se o atencioso perder vantagem, diga primeiro.
2. Distribuição de emoções por braço e por temperamento.
3. Fração de pets com pelo menos um eixo descrito (acima do limiar).

## Fora de escopo (ideias do Dwarf Fortress registradas para depois)

- Memórias mudando o temperamento ao longo da vida (reabre o confundidor
  cuidado × treino; exige desenho próprio).
- Preferências individuais (comida e brincadeira favoritas), com ovos
  pareados.

Nenhum número sem o artefato que o gerou.
