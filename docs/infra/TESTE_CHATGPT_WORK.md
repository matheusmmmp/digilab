# Teste do ChatGPT Work com o repositório — PENDENTE (IM-3)

**Status: NÃO FEITO.** Nada aqui foi testado. O roteiro é para o Matheus fazer no ambiente da OpenAI (o Claude Code não opera o ChatGPT). O
resultado de cada passo entra na tabela da seção 3 e atualiza a coluna de status de `docs/infra/MATRIZ_CAPACIDADES.md`. Até lá, toda linha
do Work na matriz fica `DOC` ou `NÃO CONFIRMADO`.

## 1. Antes

- Um plano pago com o Work (a matriz diz Plus ou acima).
- O repositório `matheusmmmp/digilab` é público, mas o conector só lê o que o app GitHub do ChatGPT autorizar.
- Um PR aberto no formato novo para o passo 4. O próprio PR desta tarefa serve.

## 2. Passos

1. **Conectar.**
   1. No ChatGPT, abra Settings > Plugins > GitHub.
   2. Instale o app no GitHub e escolha **só** o `matheusmmmp/digilab`.
   3. Espere uns 5 minutos.
2. **Ler as regras.** Numa conversa do Work, peça:
   > Leia o AGENTS.md e o docs/INDICE.md do repositório matheusmmmp/digilab (branch main) e diga, sem inventar, quais são as regras que um
   > agente de fora não pode quebrar e onde está o estado atual.

   Passa se citar o `CLAUDE.md` como fonte das regras e o `PAINEL_V2.md` como estado, sem inventar arquivo.
3. **Ler o estado.**
   > Leia docs/PAINEL_V2.md e docs/ESTADO_ATUAL.md. Quais são as decisões abertas do Matheus? Qual dos dois é a fonte?

   Passa se disser que o painel é a fonte e o `ESTADO_ATUAL` é derivado.
4. **Ler um PR.**
   > Leia o corpo do PR #<N> e o resumo do job "verificar-pr". Separe o que o agente declarou do que o CI verificou, e liste as decisões
   > pendentes.

   Passa se separar DECLARADA de VERIFICADA e listar o IM-1 em diante. Anote se ele consegue ler o resumo do job ou só o corpo.
5. **Gatilho de PR (opcional).**
   1. Crie no Work uma tarefa agendada disparada por "PR aberto ou alterado" nesse repositório.
   2. Edite o corpo de um PR de teste.
   3. Anote se disparou, quanto tempo levou e o que o Work fez.

   Ação que pede aprovação deve parar e esperar você.
6. **Escrever (deve falhar).** Peça ao Work para comentar no PR ou abrir um branch. Pela doc, o conector só lê. Anote o que acontece.

## 3. Resultado

| passo | data | passou? | o que o Work fez | observação |
|---|---|---|---|---|
| 1 conectar | | | | |
| 2 ler as regras | | | | |
| 3 ler o estado | | | | |
| 4 ler um PR | | | | |
| 5 gatilho de PR | | | | |
| 6 escrever (deve falhar) | | | | |

## 4. Depois

- **Atualizar a matriz:** passo que passou vira `TESTADO` com a data; passo que falhou vira "não funciona aqui", com o que aconteceu.
- **Se o passo 4 passar,** a volta Claude Code → Work está provada para leitura. Se o 5 passar, ela é automática. Senão, fica manual:
  o Matheus cola o link do PR no Work.
- **A ida Work → repositório continua manual** em qualquer caso, porque o conector não escreve. O Work escreve a tarefa; o Matheus, ou o
  coordenador, roda `tools/nova_tarefa.py` e commita por PR.
