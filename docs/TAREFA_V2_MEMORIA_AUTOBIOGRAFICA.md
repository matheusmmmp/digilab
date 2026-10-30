# TAREFA V2 — MEMORIA_AUTOBIOGRAFICA: a memória autobiográfica consolidada, com influência causal nas decisões e nas facetas (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: a definir. Worktree e branch: `v3-memoria-<etapa>` (V3-D2; a C4 da V3). Status: **ABERTA, só papel; as ME-1 a ME-7
DECIDIDAS pelo Matheus em 2026-10-30, pela recomendação, com as entradas da C0 e as C4-E1 a C4-E3** (seção 8). Nenhum código.

Categoria: implementacao (com a validação causal como experimento). Origem: Matheus, 2026-10-24, o PROMPT MESTRE (seção 4): a memória
é uma capacidade central do DigiBrain modular, e não só texto que o pet conta.

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | o pet guarda episódios do que viveu, os recupera pelo contexto, os consolida, e eles mudam decisões e, devagar e de forma rastreável, as facetas adquiridas; a fala conta só o que está registrado |
| o marco que desbloqueia | o M-MEM e o M-PERS do cérebro modular (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seções 2, 3 e 5); a fala fiel no jogo |
| a evidência | os testes de mecanismo por etapa; a validação causal com controles (seção 4), com plano antes; a fidelidade conferida por teste |
| as dependências reais | a especificação do modular (a interface do M-MEM); o mundo do motor (o contexto dos episódios). **Não depende do A** |
| se o gate falhar | o resultado é registrado; o diagnóstico separa a recuperação que não acontece da recuperação que acontece e não pesa. A memória não volta a ser validada só pelo N6 do A |

## 1. Pergunta

O pet modular guarda o que viveu, lembra o que importa no contexto, consolida o que se repete ou pesa, e isso muda o que ele faz e,
devagar, quem ele é, com cada mudança rastreável até os episódios e com a fala fiel a eles?

## 2. O que existe hoje (a auditoria, seção 4)

- **A memória por espaços** (só no bandit da v1) e o **N6** (só na escolha da fruta, desligado por padrão e fora do jogo): a promoção do
  curto para o longo por intensidade.
- **Não existe:**
  - a memória central;
  - a influência em personalidade ou facetas;
  - a recuperação contextual fora do N6;
  - o corpo no episódio (o N6 guarda só a variação do humor);
  - a checagem entre o episódio lembrado e a decisão.
- **A história** só alimenta a fala.

**As quatro marcas,** de `docs/research/digibrain/mechanisms/episodic_memory.md`:
- **registrado:** está no log;
- **codificado:** virou estrutura de memória;
- **recuperado:** volta a ser lido;
- **causal:** muda a decisão.

## 3. As etapas (PROPOSTAS)

| etapa | o que | testes planejados |
|---|---|---|
| **M0, o episódio** | o formato do episódio: o tick; o contexto (o lugar, o que estava à vista); os participantes (o dono, o outro pet, o objeto); o corpo e o afeto antes e depois (os receptores); a ação; a consequência. A referência ao evento do log | o episódio sai igual no replay; nenhum campo lê o estado privado do motor (só a Observação e os receptores) |
| **M1, a codificação** | quando um evento vira episódio (pela intensidade do afeto ou pela consequência no corpo) | um evento forte vira episódio, e um neutro não; o mesmo log codifica os mesmos episódios |
| **M2, a recuperação contextual** | a pista é o contexto atual; volta o episódio mais parecido, com o empate desfeito por uma ordem fixa ou por uma rng própria | um contexto conhecido recupera o episódio certo; um contexto novo não recupera nada; o replay é bit a bit |
| **M3, a consolidação** | recente → duradoura → central, por repetição, peso afetivo ou recuperação (a regra exata na especificação) | um episódio repetido consolida; um esquecido some; a memória central tem capacidade e regra de entrada declaradas |
| **M4, a influência nas decisões** | o episódio recuperado soma um termo na arbitragem, registrado no motivo | a sonda contrafactual (a mesma decisão sem a lembrança) mostra quando a lembrança mudou a escolha |
| **M5, a influência nas facetas** | as facetas adquiridas mudam devagar pelos episódios consolidados. **O temperamento inato não muda** (DM-6) | cada mudança de faceta aponta os episódios que a causaram; o temperamento fica igual ao do nascimento |
| **M6, a fidelidade da fala** | a fala só diz "lembrei de X" com um episódio recuperado, e "fiz Y porque lembrei de X" com a sonda mostrando que X mudou Y | um teste falha se a fala alega uma causa sem o registro; ele corrige as três lacunas da auditoria (o prompt `livre-v6`, o verificador que aceita causa por memória, o motivo do N6) |
| **M7, o determinismo** | todas as etapas | o G1 (replay bit a bit) e o G2 (a chave desligada = a vida de hoje) |

**Uma escolha de desenho própria:** a recuperação é contextual e determinística. As mecânicas do *Dwarf Fortress*, NÃO VERIFICADAS EM
FONTE PRIMÁRIA, são inspiração de desenho, e o DigiLab não copia os sorteios do jogo.

## 4. A validação causal futura (PROPOSTA; não roda agora)

**Um plano de análise próprio,** commitado antes. Os braços têm o mesmo pet, o mesmo mundo, o mesmo estado e as mesmas sementes:

| braço | o que muda |
|---|---|
| **REL** (a memória relevante) | a recuperação contextual (a de M2) |
| **SEM** | sem recuperação; o episódio é registrado e codificado, mas nunca lido |
| **REC** (a recência) | volta o episódio mais recente, sem olhar o contexto |
| **EMB** (embaralhada) | volta um episódio sorteado entre os guardados, por uma rng própria |

**As métricas candidatas** (PROPOSTAS; o plano as fixa):
- **a fração de decisões em que a lembrança mudou a escolha** (pela sonda), por braço;
- **o desempenho nos cenários em que a experiência passada importa,** por exemplo voltar ao lugar onde a comida esteve, ou evitar o que
  fez mal (como o T1 do J5);
- **a mudança das facetas,** e se ela segue os episódios;
- **a fidelidade da fala:** a fração das alegações de lembrança e de causa sustentadas pelo registro.

**O contraste primário candidato:** REL contra SEM, REC e EMB, com o Holm. As margens saem de um piloto.

**Os números são PROPOSTOS e SEM FONTE.** O N6 do A (`docs/RESULTADO_V2_VALIDACAO_UNICA.md`: o G-CAUSAL de +0,028) é o precedente de
desenho (os controles de recência e embaralhado), não a meta.

## 5. Entrega

- Um PR por etapa, com os testes e a suíte inteira.
- O plano antes da validação.
- O registro do mês.

## 6. Fora desta tarefa

- mudar o temperamento inato (DM-6);
- herdar o aprendido (a EG-5: nunca no genoma);
- a fala por LLM nova (só a fidelidade, M6);
- a memória social entre pets;
- o decodificador de conceitos.

## 7. Critérios de aceitação

- Cada etapa tem os testes da seção 3 passando.
- O replay é bit a bit.
- Desligada, a vida é a de hoje.
- O teste de fidelidade falha quando a fala alega o que não está registrado.

## 8. Decisões do Matheus

**Todas DECIDIDAS em 2026-10-30, pela recomendação** ("segue as recomendações", no chat do Gerente da V3), **com as entradas da
literatura** (a C0, `docs/referencias/v3c0_referencias_verificadas.csv`; `docs/PLANO_V3.md`, seções 2 e 2.3). Os limiares, as
capacidades e os passos continuam números PROPOSTOS, fixados na especificação.

**As entradas que valem junto da tabela abaixo:**
- **na ME-1:** a significância do episódio é a variação do corpo que o evento causou (a tese de Ho, `10.18745/th.14271`); e a visita
  vazia ao lugar lembrado vira episódio negativo (a C4-E1);
- **na ME-2:** a recuperação roda a cada decisão (o PEPE, Francis, Mehta e Ram 2009, `10.4018/978-1-60566-354-8.ch020`; já cabe na M2);
- **na ME-3:** guardar o mais significativo de cada categoria;
- **na validação (seção 4):** o braço "REL sem episódios negativos", que mede também a visita vazia (a C4-E2); se a C4-E1 e a L-3
  forem adiante, o plano diz qual é o braço e qual é o controle (a C4-E3).

Ho et al. usam de 10 a 50 execuções por condição, sem teste de hipótese: é direção, não tamanho de efeito.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **ME-1** | o que vira episódio (M1) | **pela consequência no corpo ou pelo afeto acima de um limiar,** fixado na especificação | tudo: a memória enche de ruído; só os gestos do dono, como na v1: o pet não lembra o mundo |
| **ME-2** | a pista da recuperação (M2) | **o contexto da Observação** (o lugar, o que está à vista) **e o estado do corpo** | só o objeto, como no N6: não lembra o lugar nem o estado |
| **ME-3** | a regra da consolidação (M3) | **por repetição e peso afetivo, com a memória central pequena e de capacidade declarada** | só por intensidade, como hoje: um episódio forte único ocupa a central para sempre |
| **ME-4** | as facetas adquiridas (M5) | **poucas, nomeadas na especificação, com passo pequeno e cada mudança rastreável** | muitas ou rápidas: o pet muda de "personalidade" por um dia ruim |
| **ME-5** | onde a memória entra primeiro | **no protótipo modular, nos cenários do MVP** (o lugar da comida) | no A: volta a validar o A |
| **ME-6** | a fidelidade da fala | **corrigir as três lacunas da auditoria** na etapa M6, antes de a fala citar a memória nova | deixar: a fala continua podendo dizer "porque lembrei" sem verdade |
| **ME-7** | o adendo DF | **manter a proteção do temperamento inato;** a influência vai só nas facetas adquiridas (DM-6) | mexer no temperamento: o inato e o adquirido se misturam |
