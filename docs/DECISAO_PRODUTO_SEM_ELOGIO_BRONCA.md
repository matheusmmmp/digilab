# Decisão de produto: o pet aprende sozinho, sem os botões de elogiar e repreender (2026-10-07)

Status: **DECIDIDO pelo Matheus (2026-10-07)**. Era o item R8.1 do roadmap (PR #124, 2026-10-01: "decidir se o pet do produto aprende só
pela consequência", adiado para depois da escolha do cérebro do produto), que saiu da tabela na revisão 3 do `docs/ROADMAP_V2.md`. O cérebro
foi escolhido (M6: o A, 2026-10-07), e a decisão foi tomada. O **como** é PROPOSTO neste documento.

## 1. A decisão

Os botões de **elogiar** e **repreender** saem do jogo. Pela decisão do Matheus, o jogador dar nota ao pet "não faz sentido": o natural é o
pet ter esse retorno sozinho, por reforço, como no Creatures 3. O pet do produto aprende pela **consequência das próprias ações no corpo e no
mundo**.

## 2. Por quê

- **O critério do R8.1 foi cumprido.** O R8.1 pedia "P1 ≥ P3 no experimento maior". Na validação única, o P1 vence o P0 no descasado e no
  mutável, e o P3 fica abaixo do P0 (P3 − P0 −0,081 [−0,141; −0,007], `docs/RESULTADO_V2_VALIDACAO_UNICA.md`).
- **A pesquisa já mostrou que o dono pesa pelo cuidado, não pelo ensino** (`docs/LEITURA_CONSOLIDADA_DONO.md`). O feedback avaliativo deixou
  pouca marca na v1 e na V2.
- **É como o Creatures 3 faz** (seção 3).

## 3. Como o Creatures 3 faz o reforço

Fontes: o *Creatures 3 Genetics Kit Manual* (lido em 2026-10-07; documentação de produto, CORPUS) e a análise dos arquivos do jogo no
repositório NORNBRAIN (`docs/reference/game-files-analysis.md`, extraída dos arquivos do jogo pelo autor; pista, não fonte primária).

- **O reforço é químico e interno.** O manual descreve os químicos **Recompensa** ("usado pelo cérebro para reforçar ações boas") e
  **Punição** ("para desencorajar ações ruins"), e a **Decepção**, usada quando o pet tenta uma ação que não é permitida.
- **O ciclo é automático.** Cada ação dispara estímulos; os estímulos mudam químicos; os químicos mudam os drives; e é daí que saem a
  recompensa e a punição que ajustam o cérebro. Ninguém dá nota de fora.
- **A mão do jogador também entra, mas pelo corpo.** No Creatures 3 o jogador pode acariciar e dar um tapa no pet. Pela análise dos arquivos
  do jogo, esses gestos são estímulos como os outros ("acariciado pela mão", "levou tapa da mão"): mudam químicos do corpo, e o reforço sai do
  mesmo ciclo. Não são uma nota direta ao cérebro.

A leitura para o Digilab: **o jogador age sobre o corpo e o mundo do pet, e o cérebro aprende com o que isso provoca.** Não há botão de nota.

## 4. O que substitui os botões

- **A consequência como sinal** (o P1 da pesquisa, nó N3): o aprendiz recebe a redução do déficit homeostático causada pela própria ação.
  Com o corpo químico do Creatures 3 (`docs/futuro/ego_existencia.md`, seção 2), o sinal passa a sair da química: a recompensa e a punição
  internas.
- **Acariciar fica**, como gesto físico: no corpo, o carinho reduz um drive (estresse, solidão) e o reforço sai daí.
- **O tapa não entra.** A literatura verificada sobre métodos aversivos em cães mostra efeito ruim no bem-estar (Casey et al. 2021,
  `10.1038/s41598-021-97743-0`; Vieira de Castro et al. 2020, `10.1371/journal.pone.0225023`). E um botão de bater num pet virtual é um
  risco de produto.
- **O dono continua com os outros papéis:** cuidar, informar (N5), pedir (N7) e conversar. O pedido e a informação entram pela percepção,
  nunca como nota.

## 5. Um efeito colateral que precisa de resposta antes de ligar

**No mundo do jogo de hoje, a consequência sozinha faz um pet mais parado.** No mundo `padrao`, o sinal homeostático do N3 só vê fome,
higiene e energia. Comer dá sinal positivo; brincar e explorar dão negativo, porque gastam energia. Nada recompensa brincar. Na validação
do N3 o P1 passou a escolher ocioso e chamar em 47% e 27% do tempo livre; na calibração, brincar caiu de 35% para 10% e explorar de 28%
para 15% (`docs/RESULTADO_V2_N3.md`, seção "V2, N3" do `CLAUDE.md`).

No Creatures 3 isso não acontece porque há drives para tédio e solidão, e brincar ou estar perto de alguém os reduz. **Então a retirada dos
botões e o corpo do Creatures 3 andam juntos:** antes de ligar a consequência no produto, o corpo precisa de drives cuja redução recompense
brincar, explorar e o contato (tédio, curiosidade, solidão). Sem isso, o pet aprende a ficar parado.

## 6. O que depende dos botões hoje

| peça | onde | o que muda |
|---|---|---|
| tela do Pet, Aprendizado, Conversar | `web/app/src/telas/` | os botões saem nos pets novos |
| ações do dono e o catálogo do comando pelo chat | `web/app/src/acoes.ts`, `motor/tipos.ts`, prompt `livre-v8` | elogiar e repreender saem do catálogo dos pets novos |
| aprendizado do pet | `motor/bandit.ts` (pets v1 a v10); o cérebro A do v11 | o v11 aprende pela consequência (seção 7) |
| vínculo B | `motor/vinculo.ts`, `digilab/vinculo.py` | a coerência agrupa o feedback por ação e situação; sem feedback, o vínculo precisa de outra base (o desejo atendido, o cuidado no tempo certo) |
| disciplina das travessuras | educação (pets v4+) | a travessura hoje é repreendida; precisa de outra consequência |
| mentira repreendida | voz própria (pets v7+) | a reação do dono à mentira deixa de ser a bronca |
| memória e emoção | memória por espaços, emoção por categoria | elogio e bronca dominam as lembranças e o orgulho e a raiva de hoje; com eles fora, a memória lembra outras coisas |
| sensibilidade do temperamento | `digilab/temperamento.py` | a sensibilidade e a teimosia escalam elogio e bronca; passam a escalar a consequência |
| donos simulados da web | `motor/donos.ts` (Cenários) | sem elogiar e repreender nos pets novos |
| jornada e dicas do Bit | `docs/JORNADA_JOGADOR.md` | o "ensinar: elogiar e repreender" do Rookie sai |

**Os pets v1 a v10 não mudam:** os registros deles têm elogios e broncas e continuam se reproduzindo byte a byte.

## 7. O plano do porte (PR #201) precisa inverter duas recomendações

O `docs/PLANO_PORTE_V2_WEB.md` (PR #201, aberto) foi escrito antes desta decisão:
- **Seção 1.2:** recomenda levar "o aprendizado da L1 pelo dono" (elogio, bronca, chamado) para os pets v11. **Com esta decisão, sai.**
- **D-W1:** recomenda a consequência desligada no v11. **Com esta decisão, a consequência é o aprendizado do v11**, e só pode ligar
  depois da resposta à seção 5 (drives que recompensem brincar e o contato).
- **Gabaritos e gates:** os da paridade passam a usar a fonte consequência em vez da fonte dono.

**A pesquisa não muda:** o P3 (feedback do dono) continua como braço de referência no Python, e todos os resultados ficam como estão.

## 8. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| S-1 | Os pets v1 a v10 continuam com os botões? | sim, só os pets novos ficam sem; os antigos seguem iguais | tirar dos antigos muda o jogo deles no meio da vida |
| S-2 | O tapa do Creatures 3 entra? | não (seção 4) | botão de bater num pet virtual |
| S-3 | A consequência liga no v11 antes do corpo do Creatures 3? | não: primeiro os drives que recompensam brincar e o contato (seção 5) | um pet que aprende a ficar parado |
| S-4 | A base nova do vínculo | o desejo atendido e o cuidado no tempo certo, numa tarefa própria | o vínculo B fica sem a coerência e perde o sentido |
