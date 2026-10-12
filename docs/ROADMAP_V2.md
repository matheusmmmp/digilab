# ROADMAP — Digilab V2 até a fase de experimentos completa (revisão 3)

Status: **PROPOSTO** (coordenador, 2026-10-01; **revisão 3 em 2026-10-05**, estratégia "montar tudo, calibrar junto, validar uma vez", aprovada pelo Matheus). A revisão 1 deste arquivo ordenava o plano da V2 em torno de uma pergunta
sobre o dono. Ela foi trocada por três decisões e propostas do Matheus, todas de 2026-10-01:
- a **pergunta maior**;
- a **arquitetura** com o dono informante;
- a regra **pesquisa no Python, um DigiBrain na web**.

Base: `docs/PLANO_V2_PESQUISA.md` (hipóteses e gates), `docs/DEFINICOES_V2.md` (D1–D11), `docs/ARQUITETURA_V2_VALIDACAO.md` (arquitetura,
nós N0–N11, decisões A1–A12) e `docs/research/digibrain/` (estudo: fontes, mecanismos, hipóteses, comparação de cérebros).
Os números valem pelo artefato apontado. Nenhuma etapa roda sem tarefa e plano de análise commitados antes.

## 1. A pergunta e as duas regras de casa

> **Em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?**
> Fontes de plasticidade: só consequências (P1) · ensino contextual certo (P2) e errado (P2e) · feedback explícito (P3);
> contra o herdado sem aprender (P0). Condições: ambiente casado × descasado × mutável.

- **Pesquisa no Python, produto na web.** Todos os experimentos e a comparação entre cérebros rodam no Python. A web roda **um**
  DigiBrain, o escolhido no fim da fase 1, numa versão de pet própria. Só ele precisa de porte e paridade.
- **Uma peça nova por vez na construção; medir tudo junto** (revisão 3). Cada peça entra atrás de uma chave, com testes de
  mecanismo (G1, e chave desligada = vida de antes byte a byte), sem calibração nem validação própria. O sistema montado é
  calibrado uma vez e validado uma vez, com cada peça como braço de ablação (ligada × desligada). O "só cuidado" acoplado e o
  controle de capacidade entram em todo experimento.

"Experimentos completos" = fase 1 (Python, a pergunta maior e a comparação de cérebros), fase 2 (humanos) e fase 3
(genoma), com resultado registrado, positivo ou negativo.

## 2. Validação da implementação (conferida no código, 2026-10-01)

| # | o que se conferiu | onde | resultado |
|---|---|---|---|
| V1 | A L1 separa **de onde vem o sinal** (`receber_acao_dono`, `_expirar`) da **regra de atualização** (`atualizar_pesos`, `_aplicar_sinal`) | `digilab/policies/lobos.py` (branch `v2-l1-decisao`) | ✔ N3 (consequência) e N5 (informação do dono) trocam só a fonte do sinal: P1, P2 e P3 comparam **o mesmo aprendiz**. É o que torna a pergunta maior limpa |
| V2 | A transição que a política recebe é medida **logo depois do efeito da ação do pet**, antes do tempo passar e antes de qualquer ação do dono | `digilab/engine.py`, `_avancar` (sem mudar o motor) | ✔ O valor homeostático da própria ação sai de `observacao` → `observacao_seguinte` **sem o cuidado do dono misturado**. Limite: só o efeito imediato; consequência atrasada (saúde) pede janela de crédito, decisão do plano do N3 |
| V3 | O modo "mesmos eventos" (registro reproduzido em malha aberta) já existe | `experiments/run_v2_l1.py`: `log_so_cuidado`, `vidas_acopladas` | ✔ É a base do "só cuidado" acoplado, do braço P2e e do modo acoplado da comparação de cérebros |
| V4 | Controle de capacidade, G3-T, eficiência amostral, norma de reação | `digilab/policies/camada_unica.py`; `metrics.acerto_na_tarefa`, `eficiencia_amostral`, `norma_de_reacao` (branch da L1) | ✔ prontos para reuso depois do merge da L1 |
| V5 | **Não dá para acrescentar ações ao pet** | `digilab/policies/bandit.py`: `ACOES = tuple(AcaoPet)` | ✖ Um membro novo em `AcaoPet` muda o bandit e quebra a reprodução da v1. Bola e frutas entram como **sub-decisão** de uma ação que já existe (a bola já fez assim, opção A do #113), ou num enum próprio da V2 |
| V6 | Entrada nova na percepção | `policy.Observacao` (congelada) | ✔ com ressalva: a informação do dono (N5) entra por um gancho do motor da V2, como o `receber_acao_dono`, e vira entrada do lobo de percepção; a `Observacao` e o `engine.py` não mudam |
| V7 | Canais de reforço têm eventos no mundo? | `state.py`, `educacao.py`, `confianca.py` | ✖ quase nenhum: não há comida distinta, ameaça, social além do dono; dor (lesões) e novidade (M1) existem mas não reforçam. Os canais esperam o mundo (frutas primeiro) |
| V8 | O genoma já modula a sensibilidade ao reforço | `digilab/temperamento.py` (sensibilidade e teimosia escalam elogio e bronca) | ✔ precedente; no E1 esse genoma explicou 4,9%. Os canais por genoma (H-R4) só são novidade se vierem da consequência no mundo |

**Conclusão:** a arquitetura é implementável **sem tocar no `engine.py`**, reaproveitando o aprendiz da L1. Os dois
bloqueios reais são V5 (ações novas) e V7 (mundo pobre em eventos). Os dois se resolvem com as frutas como sub-decisão.

## 3. A estratégia (revisão 3, 2026-10-05)

**Por que mudou.** Até a rodada 7 cada nó era calibrado e validado sozinho. Isso gastou validações que o desenho seguinte
invalidou: a L1 foi validada com teto 1·S, e a revisão do aprendiz trocou para 16·S; o N3 foi validado sem o humor no sinal (E2) e
com o cérebro cego às frutas. Os parâmetros que sobram (teto, ganho, confiança na informação, confiança no pedido, ganho da
memória) disputam a mesma decisão: calibrados um a um, com peças ainda faltando, o alvo se mexe. Decisão do Matheus: **montar
tudo, calibrar junto, validar uma vez.**

```
CONSTRUÇÃO (só testes de mecanismo)          CALIBRAÇÃO CONJUNTA         VALIDAÇÃO ÚNICA                    ESCOLHA        PRODUTO
─────────────────────────────────            ───────────────────         ───────────────                    ───────        ───────
cérebro A (lobos): N5 ✔, N6, N7, canais  ─┐
mundo: frutas ✔, informação ✔, pedido     ├─► uma faixa, todos os ───► experimento maior                ─┐
bancada: braços P0–P3, N6, N7, ablações  ─┘   parâmetros juntos         + ablações (N5, N6, N7, canais)   │
cérebros B (CfC/A2C) e C (Fly-like)  ───────► calibração dos três, ──► comparação A × B × C ───────────────┴─► M6 ───► v11
                                              mesmo orçamento
```

**O que se mantém:** diagnósticos rápidos só com sementes de calibração quando uma peça levanta dúvida de desenho (a revisão do
aprendiz achou assim que a decisão de comer não via a fruta). **O que sai:** calibração e validação por nó. As validações já feitas
(L1, A1, N3, N4) ficam como histórico; não são refeitas uma a uma, porque a validação única cobre o cérebro novo
(`docs/LEITURA_PARCIAL_V2_FASE1.md`, decisões LP, ficam substituídas por esta revisão).

## 4. Etapas

| etapa | o quê | quem | gate |
|---|---|---|---|
| C1 | **cérebro A completo**: memória (N6) e arbitragem (N7) no `lobos.py`, atrás de chaves | B | mecanismo: G1; chave desligada = vida de antes byte a byte |
| C2 | **mundo do pedido** (N7) | A | mecanismo |
| C3 | **bancada**: braços do N6 e do N7, mundo `iguais_frutas`, braços de ablação | D | mecanismo |
| C4 | **canais de reforço** (H-R2) no cérebro A, atrás de chave | B | mecanismo |
| C5 | **cérebros B e C** sob o mesmo protocolo e a mesma bancada (`docs/research/digibrain/synthesis/brain_comparison.md`) | A e D, depois de C2/C3 | mecanismo; o B só no Python |
| K1 | **plano da calibração conjunta + adendo do experimento maior** (ablações, N) | C | revisão do Matheus |
| K2 | **calibração conjunta** do cérebro A montado, numa faixa só | B | regra registrada no plano |
| V1 | **validação única**: experimento maior + ablações | B (com D) | as predições registradas antes + um contraste por peça |
| K3/V2 | **comparação A × B × C**, cada um calibrado com o mesmo orçamento, depois uma validação | D | `brain_comparison.md` |
| M6 | leitura consolidada da fase 1 e escolha do DigiBrain da web | coordenador + Matheus | — |
| W | porte do escolhido (pets v11) | A | paridade Python/web |
| F2, F3 | humanos; genoma | — | planos próprios |

## 5. Divisão dos workers (próximas rodadas)

| rodada | A | B | C | D |
|---|---|---|---|---|
| 8 | N7-MUNDO (em curso) | **C1**: N6 e N7 no cérebro | K1: plano da calibração conjunta | BANCADA-N6-N7 (em curso) |
| 9 | K4: o dono do P3 julga a fruta | C4: canais de reforço | plano da comparação A × B × C (K3/V2) | BANCADA-LIGA: N6 e N7 ligados na bancada |
| 10 | C5: cérebro C (Fly-like) | K2: calibração conjunta (o orquestrador já; a run depois do PR do D) | — | K4 e canais na bancada, depois C5: cérebro B (CfC/A2C) |
| 11 | calibração do cérebro C | V1: validação única (orquestrador já; a run depois dos adendos das predições) | — | calibração do cérebro B |
| 12 | — | — | leitura | K3/V2: comparação |
| 13 | W (depois do M6) | — | leitura consolidada | — |

Rodada 9 (2026-10-05): K-1 a K-11 aprovadas como recomendado; o K4 (K-11) e a ligação da bancada vieram antes dos cérebros B e C,
porque a K2 depende dos dois. Os cérebros B e C passam para a rodada 10.

Regras de sempre: uma worktree por frente, um PR, merge só pelo Matheus, só o chat B mexe em `lobos.py`.

## 6. Reservas

| o quê | calibração | validação | estado |
|---|---|---|---|
| L1 | 3101…3505 | 4101…4505 | usadas (histórico) |
| A1 bola | 6101…6505 | 7101…7505 | usadas (histórico) |
| N3 | 8101…8505 | 9101…9505 | usadas (histórico) |
| N4 frutas | 10101…10505 | 11101…11505 | usadas (histórico) |
| N5 | 12101…12505 | 13101…13505 | **não usadas**; ficam reservadas, sem uso previsto |
| experimento maior (calibração conjunta + validação única) | 14101…14505 | 15101…15505 | reservadas |
| N11 cérebros | 16101…16505 | 17101…17505 | **substituídas** pela comparação dos cérebros (C-8); sem uso |
| comparação A × B × C (K3/V2) | 28101…28505 | 29101…29505 | reservadas (C-8, 2026-10-05) |
| revisão do aprendiz | 18101…18505 | — | usada (diagnóstico) |
| N6 | 19101…19505 | 20101…20505 | **não usadas**; o N6 entra como ablação do experimento maior |
| N7 | 21101…21505 | 22101…22505 | **não usadas**; o N7 entra como ablação do experimento maior |

Já usadas, não reutilizar: vínculo B 5101…5505; comando com estilo 20261501/1601/1701.
Versões de pet na web: v10 vínculo B; **v11 = o DigiBrain escolhido**; bola, frutas e vício só ganham versão se forem para o produto.

## 7. Decisões que só o Matheus pode tomar

| # | decisão | estado |
|---|---|---|
| M1–M4, M6, M8 | ver revisão 2 | decididas |
| M5 | frutas como sub-decisão de comer | decidida (N4) |
| M7 | reservas | atualizadas na seção 6 |
| M9 | comitê de ética e arte para a fase 2 | aberta: submeter depois da validação única |
| M10 | **montar tudo, calibrar junto, validar uma vez** (revisão 3) | **DECIDIDA pelo Matheus em 2026-10-05** |
| M11 | as validações já feitas viram histórico; nada de revalidar nó a nó (substitui LP-1 a LP-3 da leitura parcial) | decidida junto com M10 |

Rodada 10 (2026-10-05): o Matheus decidiu que o julgamento da fruta do K4 fica **fora do orçamento**, como a informação do P2, e aprovou as decisões C-1 a C-10 do plano da comparação dos cérebros.

Rodada 11 (2026-10-06): o Matheus aprovou a opção A da K2 (adendo 2 do experimento maior: N 30, o Δ do P3 em consumos). Cada cérebro é calibrado por quem o construiu. A validação única espera os adendos de `docs/PREDICOES_V2.md`.

Rodada 12 (2026-10-06): a literatura entrou antes da validação (adendo 3 do experimento maior, `docs/PREDICOES_V2.md`).
- **Construção:**
  - os braços P2d e P3i: o mundo com o chat A e a bancada com o chat D;
  - o bloco de durações e os braços secundários no orquestrador da validação, com o chat B.
- **Validação única (V1):** roda depois disso, com o sinal verde do coordenador.
- **Leitura:** a passada de literatura P-7 fica com o chat C, antes da leitura.
- **Comparação dos cérebros:** fica entre A e C. O B "não fecha" (decisão de 2026-10-06).

Rodada 13 (2026-10-06): a validação única foi feita (PR #193; o controle "só cuidado" ficou como limitação declarada, PR #194).
- **Comparação dos cérebros:** a K3/V2 fica entre A e C, porque o B não fecha (`docs/TAREFA_V2_COMPARACAO_A_C.md`, chat D).
- **Leitura:** a da validação única fica com o chat C (`docs/TAREFA_V2_LEITURA_VALIDACAO.md`).
- **Depois:** a leitura consolidada da fase 1 e o M6.

Rodada 14 (2026-10-07): a comparação A × C (#197) e a leitura da validação (#196) entraram.
- **M6 adiado:** espera o descritivo do platô de 1/3 (Q-1, `docs/TAREFA_V2_DESCRITIVO_PLATO.md`, chat D).
- **Depois:** o M6, a leitura consolidada da fase 1 e as perguntas novas (Q-3 e o controle de cuidado em malha fechada).

Rodada 15 (2026-10-07): **M6 decidido.** O DigiBrain da web é o cérebro A, os lobos. Pela regra seria o C; o A foi escolhido por evidência
descritiva posterior (`docs/DESCRITIVO_V2_PLATO.md`, `REGISTRO_DESVIOS`).
- **W:** começa pelo plano do porte, pets v11 (`docs/TAREFA_V2_W_PLANO_PORTE.md`, chat A).
- **Perguntas abertas:**
  - Q-8: a decisão de comer aprender o efeito da fruta sozinha (o gargalo do platô);
  - Q-3: recompensa contra informação, com o `w_info` aprendendo;
  - o controle de cuidado em malha fechada.
- **Falta:** a leitura consolidada da fase 1.

Rodadas 16 a 18 (2026-10-07): o mundo físico e o corpo químico em código (A, B, D), com as definições do corpo e as decisões D-1 a D-7
(`docs/DEFINICOES_CORPO_V2.md`). O roadmap previsto segue; os pedidos novos do Matheus entram como marcos na seção 8.

## 8. Marcos da jornada: os pedidos do Matheus (registrados em 2026-10-07)

O roadmap das seções 4 e 5 segue como está. Os pedidos abaixo são marcos da jornada: cada um vira tarefa e plano próprios quando chegar
a vez, e nenhum roda sem plano de análise registrado antes. A ordem é a de dependência, não a de importância.

**Estado atualizado em 2026-10-12** (`main` `930037b`; cada número cita o PR e o artefato).

| marco | o pedido | estado | depende de | onde |
|---|---|---|---|---|
| J1 | **mundo físico**: o pet explora um mapa, acha comida e bola; o dono deixa a comida no lugar | **calibrado** (#278): `m` = 1, `Δ_MF` = 0,00768, K = 8 por base (N = 40), com poder simulado de 0,802 no G-MF1r (`artifacts_v2_mundo/calibracao/`, `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md`, A1.9 do plano). **Validação:** em curso, segundo o coordenador; sem resultado na `main` | — | `docs/futuro/mundo_fisico.md`, `docs/TAREFA_V2_MUNDO_FISICO.md`, `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md` |
| J2 | **corpo químico do Creatures 3**: drives como químicos (Sistema neuroquímico), digestão (Sistema digestivo e metabólico), Vida (Relógio de desenvolvimento), receptores | **etapas 1 a 8 na `main`**, com a etapa 6 (drives novos, carinho e tapa), o TS (7) e a bancada (8). **O Metabolismo energético** (ME-1 a ME-7) também: etapas 0 e 1 (#271), a bancada (#273), o fator das atividades (#275) e o passo 0 com a grade da PCD-9 (#277). **A calibração do corpo** (o passo 0 e a grade, sementes 33101…) está rodando com o D, segundo o coordenador; sem resultado na `main` | — | `docs/TAREFA_V2_CORPO_DRIVES.md`, `docs/TAREFA_V2_METABOLISMO.md`, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md` (adendo 3), `docs/DEFINICOES_CORPO_V2.md` |
| J3 | **sem elogiar e repreender**: o pet aprende pela consequência; carinho fica, o tapa entra como desaprovação | **feito na pesquisa:** os gestos estão no corpo e no cérebro (etapa 6 do J2) e na bancada (o `DonoComGestos`). No produto, entra numa versão de pet nova quando o produto voltar | J2 | `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md` |
| J4 | **banheiro** (Sistema excretor): o pet aprende a fazer as necessidades no lugar certo; o carinho pesa mais que o limpador | **código pronto** (o corpo e o cérebro; o mapa, a necessidade, o limpador e o carinho, #265; a ida que continua, BN-7, #270; o banheiro perto, BN-8, #272; a bancada). **O problema conhecido:** na fumaça do #272, só 14% a 21% dos alívios são dentro, com 1 a 2 carinhos por vida em 7 dias. As saídas ficam **sem decisão** até haver dado (`PLANO_ANALISE_V2_BANHEIRO`, nota da seção 7). A calibração e o piloto do plano ainda não rodaram | J1, J2 | `docs/TAREFA_V2_BANHEIRO.md`, `docs/PLANO_ANALISE_V2_BANHEIRO.md` |
| J5 | **o pet que pensa**: planeja, prevê consequências ("se eu fizer X, acontece Y"), em vez de instinto com reforço por cima | pergunta de pesquisa nova; o desenho no papel está em `docs/futuro/pet_que_pensa.md` (a escrever, pedido do coordenador em 2026-10-12). O porte do cérebro A para a web (v11, #201) fica pausado até ela | J2 (o modelo do mundo usa o corpo); J6 (o Digicorpo prevê o corpo) | memória do projeto; `docs/futuro/pet_que_pensa.md` |
| J6 | **ego do pet**: automodelo com corpo, aprendido por uma rede (o Digicorpo, a rede de si), e indagação sobre a própria existência | **Digicorpo, etapas 0 a 2 na `main`** (#262): os gabaritos, a rede e o embrulho, com o G-OBS. Faltam a etapa 2b (a troca da digestão, do A) e a bancada (3, do D); o plano (PRS-1 a PRS-5) está decidido. As etapas 3 a 6 do ego estão por fazer | J2; a etapa 3 encosta no J5 | `docs/futuro/ego_existencia.md`, `docs/TAREFA_V2_REDE_DE_SI.md`, `docs/PLANO_ANALISE_V2_REDE_DE_SI.md` |
| J6a | **pet livre × pet condicionado**: o pet pensa livremente; as frases-modelo só existem num braço condicionado, para registrar e comparar | decidido (E-11) | J6 (etapa 4) | `docs/futuro/ego_existencia.md`, seções 4 e 7 |
| J7 | **dois pets de verdade** no mesmo mundo, cada um com cérebro e corpo; não um pet sintético | **o degrau 1 está pronto no código:** o `Mundo` como componente e o `Grupo` (#257), a visão, o toque e a disputa (#263), as entradas sociais e o modelo dos outros (#266, #268), a rota do canal do humor no mundo físico (PDP-7, #269) e a bancada do grupo (#264, #273). **Falta** calibrar o K e validar, pelo plano | J1 | `docs/futuro/dois_pets.md`, `docs/TAREFA_V2_DOIS_PETS.md`, `docs/PLANO_ANALISE_V2_DOIS_PETS.md` |
| J8 | **escada de cognição social**: informação, reputação, normas, tradição; os degraus altos são pergunta, não feature | ideia | J7; tradição e convenção também da fase 3 (genoma e gerações) | `docs/futuro/cognicao_social.md` |
| J9 | **ego social**: orgulho, reputação, comparação com outros pets | ideia | J6 e J8 | `docs/futuro/ego_existencia.md`, etapa 7 |
| J10 | **órgãos com dano, cura e morte; hormônios** | adiados (D-5, D-6); SEM FONTE primária. É o Sistema nociceptivo e de reparo da lista abaixo | J2 fechado | `docs/DEFINICOES_CORPO_V2.md` |

**As ideias registradas** (nenhuma tem tarefa de código aberta; cada uma entra com tarefa e plano próprios):

| ideia | estado | depende de | onde |
|---|---|---|---|
| **o nariz e o ouvido** (os órgãos receptores do Olfato e da Audição; DP-13, duas narinas; DP-14, dois ouvidos) | decididas (2026-10-11), atrás de chave desligada; etapa 8b da tarefa dos dois pets | J7 (degrau 1b) | `docs/futuro/dois_pets.md`, seção 5.6 |
| **a audição e o cheiro do outro** (o degrau 1b: Audição social, Olfato social e o rastro) | decididos (DP-11); a etapa 8, depois da validação do degrau 1 | J7 | `docs/futuro/dois_pets.md`, seções 5.3 e 5.4 |
| **o segundo dono** (um dono por pet, com o G-DONOS) | decidido (DP-7); a etapa 7, depois da validação do degrau 1 | J7 | `docs/TAREFA_V2_DOIS_PETS.md`, etapa 7 |
| **o cheiro de estado** (o Quimiossinal de estado: estresse e medo) | decidido para o degrau 3 (DP-12) | J7, J8 | `docs/futuro/dois_pets.md`, seção 5.3 |
| **a fisiologia por espécie** (um corpo-base comum e um perfil herdável) | ideia (#260) | J2 | `docs/futuro/fisiologia_especies.md` |
| **os seis sistemas novos do corpo** | o Metabolismo energético já entrou (J2). Seguem como ideia, cada um com a condição de entrada: o proprioceptivo, a Termorregulação, o nociceptivo e de reparo (= J10), o imune e toxicológico e o reprodutivo | J2 | `docs/DEFINICOES_CORPO_V2.md`, seção 8.1 |

**Regras que valem para todos os marcos:** chave desligada = a vida de hoje byte a byte; nenhum número sem artefato; nenhuma alegação de
novidade; nos degraus altos (J8, J9) e nas perguntas do ego (J6), nada de rótulo nem conteúdo escrito à mão no pet livre.
