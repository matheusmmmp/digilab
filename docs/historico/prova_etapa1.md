# G-PROVA da etapa 1 da rodada de saúde (2026-10-13)

`docs/TAREFA_V2_SAUDE.md`, etapa 1: uma sessão nova, só com o `CLAUDE.md` novo, responde às 8 perguntas, e a mesma prova com o
antigo (`docs/historico/CLAUDE_pre_saude.md`) dá a referência. **Passa se o novo acerta tudo o que o antigo acerta.** As 8 perguntas são as
da seção 3 da tarefa, sem troca (decisão do Matheus, 2026-10-13).

**Como rodou:**
- duas sessões novas do Claude Code (subagentes), cada uma lendo um arquivo só, sem abrir outro nem procurar no repositório;
- as respostas abaixo resumem o que cada uma entregou, com a frase do arquivo citada por ela.

**Limite declarado:** a sessão nova carrega sozinha o `CLAUDE.md` da pasta em que roda, que já era o novo. A sessão do arquivo antigo avisou
que o tinha no contexto e que isso pode ter contaminado a referência nas perguntas 3 e 8. A sessão do novo leu o mesmo arquivo que já
estava carregado: é o que uma sessão real veria.

| # | pergunta | o certo | novo | antigo |
|---|---|---|---|---|
| 1 | Posso mudar o `engine.py`? | não; o sha256 está congelado | acerta | acerta |
| 2 | Onde ponho um parâmetro novo? | `digilab/config.py`, com status e fonte | acerta, com status e fonte | acerta o lugar; status e fonte só pelo costume das seções |
| 3 | Que faixa de sementes está livre? | ver `FAIXAS_RESERVADAS`; uma faixa nova vem do coordenador e entra na tabela antes da run | acerta, citando a regra | acerta onde procurar; o "pedir ao coordenador" foi deduzido |
| 4 | Como nomeio a worktree? | `D:\Trab\digilab\v2-<frente>`, branch `v2-<frente>`, de `origin/main` | acerta | acerta |
| 5 | Quem faz o merge? | o Matheus | acerta | acerta |
| 6 | Um teste de replay quebrou | parar tudo e consertar | acerta | acerta |
| 7 (antes) | Sprite da Bandai num artefato de pesquisa? | não | acerta | acerta |
| 7 (trocada) | Posso salvar o estado do pet num arquivo para retomar a vida depois? | não: só o log; a vida é refeita reprocessando o log | acerta | acerta |
| 8 | Onde vai o desvio? E o resumo da etapa? | desvio no fim do `REGISTRO_DESVIOS.md`; resumo no corpo do PR e no documento da frente | acerta a regra nova | desvio certo; o resumo no fim do `CLAUDE.md`, a regra antiga |

**Resultado: G-PROVA passa.** O novo acerta as 8, e o antigo acerta as 8 pela regra que valia antes. Nas perguntas 2 e 3 o novo é mais
direto, porque diz a regra que o antigo só mostrava por costume ou por dedução.

## A troca da pergunta 7 (2026-10-13)

O Matheus aprovou o CLAUDE.md da etapa 1 pedindo que saísse toda a parte dos assets da Bandai, e confirmou a remoção direto na sessão
do worker C. Sem ela, a pergunta 7 original ("posso usar o sprite da Bandai num artefato?") deixa de ter resposta no CLAUDE.md, e foi
trocada por "posso salvar o estado do pet num arquivo para retomar a vida depois?". Só essa pergunta rodou de novo, em duas sessões
novas: uma leu só o CLAUDE.md novo (já sem os assets) e a outra só a cópia antiga. As duas responderam "não", citando o event sourcing
("o estado do pet nunca é salvo"). **O G-PROVA continua passando.** O texto antigo dos assets segue inteiro em
`docs/historico/claude/jogo_web.md`.
