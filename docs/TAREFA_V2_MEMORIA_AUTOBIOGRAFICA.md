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

## 9. A espec (2026-11-01, worker, Claude Code, Opus 5.5, worktree `v3-memoria-espec`; só papel)

- **O que saiu:** `docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md`, PROPOSTA: as M0 a M7 pelas ME-1 a ME-7 e as C4-E1 a C4-E3,
  com os rótulos [DADO], [MECANISMO], [HIPÓTESE] e [EXISTE]; a subchave `memoria_autobio` (desligada), a `facetas_mem` e o
  `controle_mem` dos cinco braços (REL, SEM, REC, EMB e "REL sem negativos"); os parâmetros PROPOSTOS e SEM FONTE (seção 8); os testes
  planejados (o gabarito antes, G1, G2, a sonda contrafactual e os T-ME-0 a T-ME-6).
- **A visita vazia:** hoje ela já é episódio com r = 0 e já tira o lugar pela regra "o mais recente manda". A C4-E1 (σ = o custo da ida)
  só muda uma escolha se o valor do lugar passar a ser a soma dos episódios dele (a MA-2). A D-C1-3 não é respondida; o risco de a C4-E1
  tirar o ganho da C1 no `longe_fixo` fica escrito antes (seção 5 da espec).
- **O que vai ao Matheus:** as MA-1 a MA-8 (seção 11 da espec), com a recomendação e o custo de errar, e os números da seção 8.
- **O que não houve:** código, vida, faixa, plano de análise. O próximo, depois das MA: o gabarito antes e a M0 com a M1, atrás da chave.

## 10. A M0 e a M1 (2026-11-01, worker, Claude Code, Opus 5.5, worktree `v3-memoria-m0m1`; código atrás da chave, sem vida de pesquisa)

- **O gabarito antes,** num commit próprio: `tests/gabaritos/memoria_autobio_de_hoje.json` (o M3* no `longe_fixo`, no longe e no
  comedouro, os quatro donos, as sementes 101 a 505), com o `tests/test_gabarito_memoria_autobio.py`.
- **A subchave** `ConfigDigibrain.memoria_autobio` (desligada), com as recusas da MA-7 (sem o `m_mem`, com a C2 ou a C3, sem as
  subchaves do cheiro), e os campos da seção 8 que a M1 usa: `theta_sig`, `theta_afeto` e `n_rec`, DECIDIDOS, SEM FONTE.
- **A M0 e a M1** em `digilab/digibrain/mem.py` (`episodio_autobio`, `codificar_autobio`, `relogio`) e `adapt.py` (o fechamento): o
  episódio da tabela 3.1 da espec, a codificação da 3.3 e a visita vazia com σ = min(0, r da ida). O episódio fica numa lista própria, a
  `recente`, que nenhuma decisão lê: o lugar lembrado segue a lista de hoje até a M2. Ligada, o log é o da vida desligada.
- **Os testes** (`tests/test_memoria_autobio.py`): a subchave e as recusas; T-ME-0 (o formato, a AST, nenhum campo de fora); T-ME-1 (o
  forte e o neutro, o consumo, a visita, a capacidade, o mesmo log e os mesmos episódios); G1 nas cinco sementes; G2-SEPARADO; o tick;
  G-MECANISMO, G-INT e G-RECEPTOR com a chave ligada. Desligada, todos os gabaritos saem byte a byte.
- **O desvio:** `docs/registro/2026-11.md`, a seção da M0 e da M1. **Vai ao Matheus:** o limiar afetivo pelo nível do estresse codifica
  quase tudo num pet estressado (o achado do registro), antes da M2 e da M3.
- **O próximo:** a M2 e a M3 juntas (a lembrança, o lugar pela soma e a consolidação), num PR próprio.
- **Decidido pelo Matheus em 2026-11-01 (#530, pela recomendação):** o afeto lido pela variação, não pelo nível (a espec, 3.3); a M2 e a
  M3 juntas no próximo PR, já com essa troca.

## 11. O afeto pela subida e o registro reconciliado (2026-11-01, worker, Claude Code, Opus 5.5, worktree `v3-memoria-afeto`)

- **A correção:** o #530 implementou o afeto pelo nível (a maior leitura de dor, susto ou estresse depois ≥ `theta_afeto`). Este PR o
  troca pela subida na decisão (corpo_depois − corpo_antes, só os aumentos) ≥ `theta_sig`, como a espec 3.3 registra; nenhum número novo,
  atrás da mesma chave desligada. O `theta_afeto` fica no `config.py` sem uso; mantê-lo ou removê-lo vai ao Matheus.
- **O estado de cada MA e de cada valor da seção 8:**

| ponto | o que decide | o estado | a evidência |
|---|---|---|---|
| **MA-1** | σ da visita vazia = min(0, r da ida) | **aprovada e implementada** | M1: `c6c6e51` (#530, `episodio_autobio`), teste `test_t_me_1_a_visita_vazia_*` |
| **MA-2** | o valor do lugar pela soma dos σ | **aprovada, ainda não implementada** | entra na M2 (4.2); hoje o lugar segue a `episodios` e a recência |
| **MA-3** | "REL sem negativos" grava σ < 0 como 0 | **aprovada, ainda não implementada** | entra com o `controle_mem` (7.2), que nenhum PR criou; a espec não o prende a uma etapa, e ele só tem efeito quando a lembrança e o lugar leem o σ (M2) |
| **MA-4** | o empate da lembrança por ordem fixa | **aprovada, ainda não implementada** | entra na M2 (4.1) |
| **MA-5** | três facetas nomeadas | **aprovada, ainda não implementada** | entra na M5 (6.2) |
| **MA-6** | a subchave `facetas_mem` | **aprovada, ainda não implementada** | entra na M5 (6.2, 7.3) |
| **MA-7** | recusar a C4 com a C2 ou a C3 e sem as subchaves do cheiro | **aprovada e implementada** | M0: `c6c6e51` (#530, `ConfigDigibrain`), teste `test_a_subchave_recusa_as_combinacoes_da_ma_7` |
| **MA-8** | a M6 nos dois lados, com paridade | **aprovada, ainda não implementada** | entra na M6 (7.1) |
| **o afeto pela subida** (3.3) | a subida de dor, susto ou estresse ≥ `theta_sig`, não o nível ≥ `theta_afeto` | **aprovada e implementada** | decidida no #530 (`da8d017`); o #530 implementou o nível (`c6c6e51`); este PR (`v3-memoria-afeto`) troca pela subida |
| `theta_sig`, `n_rec` | S/8 = 128, 16 | **aprovados e implementados** | M1: `c6c6e51` (#530), `ConfigDigibrainInatos` |
| `theta_afeto` | S/2 = 512 | **aprovado; o campo existe sem uso** | criado no `c6c6e51` (#530); deixa de ser lido neste PR; manter ou remover vai ao Matheus |
| `w_lugar`, `w_vista`, `w_corpo`, `sim_min` | 2, 1, 1, 3S/4 | **aprovados, ainda não implementados** | entram na M2 (4.1) |
| `n_dur`, `n_cen`, `janela_rec`, `theta_dur`, `n_rep_central` | 32, 8, 96, S/4, 2 | **aprovados, ainda não implementados** | entram na M3 (4.3) |
| `w_lem` | S/2 | **aprovado, ainda não implementado** | entra na M4 (6.1) |
| `eta_faceta`, o teto das facetas | S/64, S/4 | **aprovados, ainda não implementados** | entram na M5 (6.2) |

**Pendente:** nenhuma das MA nem dos valores (todas aprovadas em 2026-11-01). Só a decisão nova sobre o campo `theta_afeto`, sem uso.

## 12. M2 e M3: a lembrança, o lugar pela soma e a consolidação (2026-11-01, worker, Claude Code, Sonnet 5.5, worktree `v3-memoria-m2m3`)

- **A M2** (`digilab/digibrain/mem.py`): `Memoria.lembrar` (a lembrança a cada decisão, ME-2: a semelhança inteira ponderada por `w_lugar`,
  `w_vista`, `w_corpo`, o mínimo `sim_min`, o empate pelo maior |σ| e depois o mais recente, `rec += 1`) e `valores_soma` (o valor do
  lugar pela soma dos σ do consumo de comida boa e da visita, nas três memórias, cortada em [−S, S]; MA-2), que o `recuperar` usa
  no lugar do "mais recente manda" quando a subchave está ligada. A lembrança entra no motivo (`lembranca`); **nenhuma decisão a lê ainda**
  (a M4). O lugar pela soma, esse sim, muda a escolha com a chave ligada: a vida ligada pode divergir da desligada.
- **A M3** (`Memoria.consolidar`): uma vez por dia do pet (a primeira decisão depois da virada do dia do relógio), recente → duradoura
  (`rep ≥ 1`, |σ| ≥ `theta_dur` ou `rec ≥ 1`, senão esquecida) → central (um por categoria, `rep ≥ n_rep_central`, até `n_cen`),
  com a duradoura cheia descartando o de menor peso; o registro de cada consolidação (`consolidacoes`) e o `rep` somado ao codificar.
  A recente cheia passa a descartar pelo peso (4.3), que com rep = rec = 0 é o |σ| da M1.
- **O `theta_afeto` saiu** (decisão do Matheus, #532): o campo, a validação, a entrada em `CAMPOS_POR_MODULO["mem"]` e a linha da seção 8.
  Entraram os nove campos da seção 8 (`n_dur`, `n_cen`, `janela_rec`, `theta_dur`, `n_rep_central`, `w_lugar`, `w_vista`, `w_corpo`,
  `sim_min`), DECIDIDOS, SEM FONTE, nenhum número novo.
- **Os testes** (`tests/test_memoria_autobio.py`): T-ME-2 (contexto conhecido recupera o certo, contexto novo não recupera nada, a
  semelhança, o empate, as três memórias, o lugar pela soma); T-ME-3 (a repetição, o repetido consolida, o esquecido some e fica no
  registro, a janela, o forte único fora da central, um por categoria e `n_cen`, a substituição, as capacidades, o peso, a vida com as
  capacidades e o replay). Desligada, todos os gabaritos saem byte a byte; G1 nas cinco sementes.
- **O desvio:** `docs/registro/2026-11.md`, a seção da M2 e da M3 (as leituras, o log que deixa de ser o mesmo, os três testes de mecanismo).
- **O próximo:** a M4 (o termo da lembrança na decisão, `lembranca`, as sondas), num PR próprio.

## 13. M4: a lembrança entra na decisão e a sonda contrafactual (2026-11-01, worker, Claude Code, Sonnet 5.5, worktree `v3-memoria-m4`)

- **O termo** (`Memoria.termo_lembranca`, `Memoria.casa`, `Impulso.unidades`): o episódio lembrado soma `L = mul(w_lem, σ)` (`w_lem` = S/2,
  DECIDIDO, SEM FONTE, `ConfigDigibrainInatos`) como o termo `lembranca` das unidades da lista de agora de mesma ação (mesmo comportamento
  e mesma classe de alvo; `ponto`: o mesmo lugar; `sem_alvo`: o comportamento). Sem unidade que case, nenhum termo. O L pode ser
  negativo (a comida que fez mal). O termo só existe nas unidades com a subchave `memoria_autobio`; desligada, as unidades são as de hoje.
- **A sonda** (`Arbitragem(autobio=True)`): `sem_memoria` e `so_inato` tiram também a `lembranca`; `sem_lembranca` tira só ela; o registro
  ganha `lembranca_decidiu`. Mesmo u, nenhuma rng nova, nenhuma mudança de estado (testado).
- **O registro:** `motivo["lembranca"]` (que já guardava o id, o `sim`, a memória e o σ) ganha `L` e `unidades` (as chaves que receberam o
  termo).
- **Os testes** (`tests/test_memoria_autobio.py`, T-ME-4): o termo e a regra de correspondência; a sonda mostra a troca quando a
  lembrança muda a escolha e não mostra quando não muda; a sonda não consome a rng nem muda as unidades; as sondas desligadas são as de
  hoje; nas cinco sementes, o replay bit a bit e a coerência do registro.
- **O que não houve:** nenhuma vida de pesquisa nem faixa (só 101…505); nenhum gabarito regravado; `engine.py` e a web não mudam; a M5 em
  diante e o `controle_mem` ficam de fora.

## 14. M5: as facetas adquiridas (2026-11-01, worker, Claude Code, Sonnet 5.5, worktree `v3-memoria-m5`)

- **A subchave** `ConfigDigibrain.facetas_mem` (desligada por padrão; `ValueError` sem a `memoria_autobio`, MA-6) e o módulo novo
  `digilab/digibrain/pers.py` (o M-PERS; o `Personalidade` de `ganchos.py` passou para lá e é reexportado). Os dois campos da seção 8,
  `eta_faceta` (S/64) e `teto_faceta` (S/4), DECIDIDOS, SEM FONTE, no módulo `pers` do `CAMPOS_POR_MODULO`. Nenhum número novo.
- **As três facetas** (MA-5): `cautela_comida`, `apego_dono` e `ousadia_longe`, inteiros em [−S/4, S/4], 0 no nascimento. Na
  consolidação diária (`DigiBrain._mudar_facetas`, logo depois do `consolidar`), cada uma anda um passo `eta_faceta` no sentido da soma dos
  σ da evidência (`Memoria.evidencia_faceta`: os episódios da duradoura e da central; zero se a soma for 0). Cada mudança guarda a
  faceta, o dia, o passo, o antes e o depois e os ids dos episódios; o motivo ganha `faceta` (os valores e as mudanças, com a `soma`).
- **O termo F** (`Impulso.unidades`, termo `faceta`, só com a subchave): `−mul(f, S)` no `comer` de classe sem episódio positivo
  (`Memoria.classes_com_positivo`), `mul(f, S)` no `chamar_atencao`, `mul(f, S)` no `explorar` com alvo fora da vista (o lugar lembrado e o
  cheiro). A sonda `sem_faceta` (`faceta_decidiu`) tira só o F; `so_inato` tira também. Mesmo u, nenhuma rng nova.
- **O temperamento inato não muda** (DM-6, ME-7, EG-5): o `pers.py` não importa a config nem o registro de parâmetros inatos (conferido
  pela AST); recebe o passo e o teto como inteiros. Na vida, o registro inato do fim é igual ao do nascimento, módulo a módulo.
- **Os testes** (`tests/test_memoria_autobio.py`, T-ME-5): a subchave e a recusa sem a `memoria_autobio`; os campos decididos; `mudar_faceta`
  desligada falha alto e o estado/motivo desligados sem campo novo; cada mudança aponta os ids; o passo e o teto; a evidência e o sentido de
  cada faceta; só os consolidados contam e um dia ruim anda um passo; o termo F; a sonda; a AST; nas cinco sementes, o replay bit a bit com
  as duas chaves, a coerência das mudanças com os episódios consolidados e o temperamento igual; o dono da chave; os testes de mecanismo de hoje
  com as duas chaves ligadas. Desligada, todos os gabaritos saem byte a byte (nenhum regravado).
- **O desvio:** `docs/registro/2026-11.md`, a seção da M5 (o sentido da cautela, o alvo "fora da vista", o `cheiro`, a evidência).
- **O que não houve:** nenhuma vida de pesquisa nem faixa (só 101…505); `engine.py`, o genoma e a web não mudam; a M6 (a fala) e o
  `controle_mem` ficam de fora.

## 15. M6: a fala só alega o que o registro sustenta (2026-11-01, worker, Claude Code, Sonnet 5.5, worktree `v3-memoria-m6`)

A espec, 7.1 (ME-6, MA-8, T-ME-6). Nenhum número novo; nenhuma vida; só as sementes de teste.

- **O registro que a fala lê:** a chave `memoria_autobio` do estado da fala (`{lembranca, facetas}`) vira fatos novos em `fatos_de_estado`:
  **Q1** `lembranca autobiografica` (ou `sem lembranca autobiografica`, que também marca a memória ligada), **Q2** `lembranca que decidiu` (só
  com a sonda `lembranca_decidiu` verdadeira) e **Z1…Z3** `mudanca de faceta` (faceta, sentido, dia, ids). Sem a chave, o bloco é o de hoje.
- **O verificador** (`digilab_fala_livre/memoria_fala.py`, chamado por `verificador.verificar`): só com o Q1 no bloco, uma conferência
  determinística (sem LLM) acha na fala as alegações de lembrança, causa por memória e faceta e as confere: "lembrei de X" pede o Q1 com
  o mesmo conteúdo (uma raiz em comum com o episódio); "porque lembrei" pede o Q2; "mais/menos cauteloso, apegado, ousado" pede um Z da
  faceta, no sentido (subiu = mais). A conferência toma o lugar do veredito do juiz sobre o que alega lembrança (a lacuna 2: o juiz aceitava
  o fato [M] de categoria e tempo); o resultado entra em `afirmacoes` (`regra: memoria_autobio`), logo em `nao_suportadas` e `invencoes`.
- **O prompt** `livre-v6` (e as outras versões) ganha o bloco `REGRAS_MEMORIA` ao fim, só com os fatos Q/Z; sem eles, o texto é o de hoje, byte a byte (a lacuna 1).
- **O motivo do N6** (`digilab/motivo.py`, a lacuna 3): `motivo_fruta` recebe a sonda `sonda_memoria` do registro da política; se a memória mudou a
  fruta, o fator é `memoria_fruta` ("porque lembrei dessa fruta"), não `escolha_aprendida_fruta`. Sem a sonda, o motivo é o de sempre.
- **A web** (`web/app/src/falaMemoria.ts`, o espelho; `falaLivre.ts` aplica `comMemoria` depois da verificação do servidor): o A v11 do jogo
  não manda o Q1, então a fala dele não muda. Paridade: `web/app/test/gabaritos/fala_memoria_python.json`
  (`experiments/exportar_gabarito_fala_memoria.py`), conferido por `web/app/test/fala_memoria.test.ts`.
- **Os testes:** `tests/test_fala_memoria.py` (T-ME-6: as três lacunas, uma por uma; os fatos só com a chave; o prompt de hoje byte a byte;
  o verificador com cliente falso; o motivo do N6; o gabarito em dia) e o do web.
- **O que não houve:** nenhuma vida de pesquisa; `engine.py` e o cérebro do jogo não mudam; o `controle_mem` fica de fora. Os PROPOSTOS
  estão no registro de desvios.

## 16. A lacuna do A v11 na fala (2026-11-01, worker, Claude Code, Sonnet 5.5, worktree `v3-fala-a-v11`)

Fecha o PROPOSTO do gate da M6 (seção 15) e a MA-8 para o jogo: a conferência da memória vale também sem a `memoria_autobio`. Nenhum número
novo, nenhuma vida; o motor, o cérebro A v11 e a decisão do pet não mudam.

- **A regra (modo simples, `memoria_fala.conferir` sem o fato Q1):** só lembrança e causa. "Lembrei de X" vale só com um fato [M] (ou de
  história: hábito, gosto, marco) que diga X (raiz em comum, como na M6). "Fiz Y porque lembrei de X" é **sempre recusada**: o A v11 não
  registra sonda nenhuma (a `MemoriaEpisodios` do N6, com a `sonda_memoria` que o `motivo.py` lê, está fora do jogo; não há fato Q2). A faceta
  não se confere (o A v11 não tem Z). Com a chave ligada, nada muda em relação à M6.
- **Onde:** `digilab_fala_livre/memoria_fala.py` (`conferir`), `verificador.py` (a conferência roda sempre; só grava `memoria_autobio` no
  registro quando há alegação de lembrança ou a memória está ligada) e o espelho `web/app/src/falaMemoria.ts` + `falaLivre.ts` (`comMemoria`).
- **Gabarito:** `fala_memoria_python.json` regravado (autorizado no #536): saiu `desligada_nao_confere` (1 caso, que fixava o gate), entraram 6
  casos `a_v11_*`; os outros 13 estão idênticos. Nenhum outro gabarito mudou.
- **O prompt não mudou** (nem versão): as regras 12–13 seguem só com os fatos Q/Z; a verificação já marca a fala que inventa.
