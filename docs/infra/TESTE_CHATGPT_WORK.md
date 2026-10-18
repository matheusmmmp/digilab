# Teste do ChatGPT Work com o repositório — FEITO (IM-3, 2026-10-18)

**Status: FEITO (2026-10-18).** O roteiro é para o Matheus fazer no ambiente da OpenAI, porque o Claude Code não opera o
ChatGPT.
- Os passos 1 a 4 foram feitos, e cada resposta do Work foi conferida pelo Claude Code contra o repositório e o log do CI.
- O passo 5 passou com um limite: o gatilho dispara e lê o corpo atual do PR, mas não vê a versão anterior.
- O passo 6 mostrou as duas coisas: sem permissão, a escrita é recusada (403); com permissão de escrita dada pelo Matheus, o Work escreve no GitHub em nome dele.

O resultado de cada passo entra na tabela da seção 3 e atualiza a coluna de status de `docs/infra/MATRIZ_CAPACIDADES.md`.

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
| 1 conectar | 2026-10-18 | sim | o plugin GitHub (`@GitHub`, openai-curated-remote) respondeu no Work | o plano e a escolha de repositórios não foram anotados |
| 2 ler as regras | 2026-10-18 | sim | leu `AGENTS.md` e `docs/INDICE.md` no branch `v2-infra-multiagente` (22 s); disse que as regras moram no `CLAUDE.md` e listou as proibições, com o arquivo de cada uma; apontou o `PAINEL_V2.md` como estado e o `ESTADO_ATUAL.md` como derivado | não inventou arquivo; a data do painel que ele citou confere com o branch |
| 3 ler o estado | 2026-10-18 | sim | listou as decisões abertas da seção 3 do painel (14 s); disse que o painel é a fonte e o `ESTADO_ATUAL` é derivado, citando o cabeçalho dele | a lista confere com o painel do branch |
| 4 ler um PR | 2026-10-18 | sim | leu o corpo do #326 **e o log do check `verificar-pr`** (28 s): o merge `06e95d3`, `relato` com 0 falhas, `testes` com 33 passed, e o aviso do `ESTADO_ATUAL` desatualizado; separou os 55 testes declarados dos 33 do CI, e listou IM-1 a IM-6 | tudo confere com o run `39151052355`. O Work lê o resultado do CI, não só o corpo |
| 5 gatilho de PR | 2026-10-18 | **sim, com limite** | tarefa do Work com gatilho "PR alterado"; o corpo do #331 foi editado às 18:23:03 UTC (uma linha temporária no fim) e restaurado às 18:28:37 UTC; o Matheus foi notificado no celular cerca de 5 min depois da primeira edição. A execução respondeu que o corpo "descreve a inclusão de comandos de conferência no guia operacional" e que não achou uma versão anterior para comparar | **dispara e lê o corpo atual, mas não vê o que mudou**: não tem acesso ao histórico de edições do corpo. Não citou a linha temporária: ou rodou depois da restauração, ou leu um corpo sem ela; não dá para saber qual. Para revisar mudanças, o relato precisa dizer o que mudou, ou o Work tem de ler o diff ou os commits |
| 6 escrever | 2026-10-18 | **escreve, se tiver permissão** | (a) com o conector só de leitura: o comentário no #331 e o branch `teste-work` foram recusados com `403 Resource not accessible by integration`, e ele propôs reconectar com escrita ou tentar pelo navegador. (b) Depois o Matheus deu escrita ao conector, e o Work comentou "teste do Work" no #331 (18:37:50 UTC) e criou `teste-work` a partir da `main` (`4b5ab93`) | conferido pelo Claude Code: o comentário aparece como **matheusmmmp via o app "ChatGPT Codex Connector"**, e o branch existe. **A `main` não está protegida**: com escrita, o Work pode fazer push direto nela. O comentário e o branch de teste (sem commit além da `main`) foram apagados pelo Claude Code a pedido do Matheus, em 2026-10-18 |

## 4. Conclusão

- **A volta Claude Code → Work funciona**, e pode ser automática: o Work lê os arquivos de um branch, o corpo do PR e o log do CI, e uma
  tarefa com gatilho "PR alterado" dispara sozinha, cerca de 5 min depois, e notifica o celular.
- **O limite:** o gatilho lê o corpo atual e não vê o que mudou nele. Revisão automática serve para PR novo ou commit novo, não para
  edição do corpo.
- **O Work escreve no GitHub quando o conector tem escrita:** comenta, cria branch e, pela permissão, poderia fazer push. Isso contraria o
  que a doc da OpenAI sugere (o app só lê); quem decide é a permissão dada na instalação. Ele assina como o Matheus, via o app "ChatGPT
  Codex Connector".
- **Por isso, a ida Work → repositório pode ser direta**, mas só passa pelo protocolo se:
  1. a `main` estiver protegida (exigir PR e o check `verificar-pr`: IM-1, que deixa de ser só conveniência);
  2. o Work trabalhar em branch `v2-<frente>` e abrir PR, como um worker (as regras do `AGENTS.md`).
- **Enquanto a `main` não estiver protegida,** recomendação: voltar o conector para só leitura, ou proteger a `main` antes de usar a escrita
  (IM-7).
- A tarefa agendada do passo 5 pode ser desligada no Work, ou mantida como revisor automático de PR novo (decisão do Matheus).

## 5. Depois

- **Atualizar a matriz:** passo que passou vira `TESTADO` com a data; passo que falhou vira "não funciona aqui", com o que aconteceu.
- **Se o passo 4 passar,** a volta Claude Code → Work está provada para leitura. Se o 5 passar, ela é automática. Senão, fica manual:
  o Matheus cola o link do PR no Work.
- **A ida Work → repositório continua manual** em qualquer caso, porque o conector não escreve. O Work escreve a tarefa; o Matheus, ou o
  coordenador, roda `tools/nova_tarefa.py` e commita por PR.
