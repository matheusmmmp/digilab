# ROADMAP — Digilab V2 até a fase de experimentos completa (revisão 2)

Status: **PROPOSTO** (coordenador, 2026-10-01). A revisão 1 deste arquivo ordenava o plano da V2 em torno de uma pergunta
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
- **Uma peça nova por vez.** Cada peça passa sozinha antes de entrar junto com outra. O "só cuidado" acoplado e o controle
  de capacidade entram em todo experimento.

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

## 3. O caminho

```
RODADA 3            RODADA 4               RODADA 5                RODADA 6                 RODADA 7–8            FASE 2   FASE 3
──────────          ──────────             ──────────              ──────────               ──────────            ──────   ──────
L1 calib+valid ──┐
bancada P0–P3 ───┼─► N3 consequência ──┬─► N5 dono informante ──► EXPERIMENTO MAIOR ────► N11 cérebros ──┐
bola (A1) ───────┤   (P1, bola+drives) │   (P2, P2e)                P0–P3 × casado/        A × B × C        ├─► marco F1 ─► humanos ─► genoma
frutas: defs ────┴─► frutas (N4) ──────┘                            descasado/mutável      (só Python)      │   (escolhe o
                                                                    ──► N6 memória, N7 arbitragem ───────────┘    DigiBrain da web)
```

Se a L1 falhar na validação, o resultado negativo é registrado. A pergunta maior **não para**: a L1 é só o braço P3, que
a v1 já prevê fraco. Isto troca a regra de parada da revisão 1 e precisa de decisão do Matheus (M4).

## 4. Etapas

| etapa | nó | depende de | entrega | gate (PROPOSTO) |
|---|---|---|---|---|
| R3.1 | **L1** (P3) | referendo G3–G6 | calibração (PR 1) e validação (PR 2) | G3–G6, G3-T, G4 do aprendido |
| R3.2 | **bancada** | nada (infra) | um orquestrador dos braços P0–P3 sobre o mesmo aprendiz: troca só a fonte do sinal; modo acoplado; métricas da pergunta maior (desempenho no ambiente, eficiência, deriva, custo da plasticidade) em `metrics.py`; **sem mecânica nova** | P0 = instinto byte a byte; acoplado reproduz o registro |
| R3.3 | **A1 bola** | aprovação do #113 | `MotorAmbiente` com a bola, chave desligada; sub-decisão de brincar | G1, G2; 1a-pet com acoplado |
| R3.4 | **frutas: definições** | busca V1–V6 no repo | `docs/DEFINICOES_FRUTAS_V2.md`: necessidade, gosto, efeito, vício; os 7 itens da literatura; campos do log; critério ensino × cuidado | revisão do Matheus |
| R4.1 | **N3** (P1) | L1 mesclada, bancada | sinal = redução do déficit pela **própria ação** (V2); janela de crédito decidida no plano | aprende a reduzir déficit melhor que o instinto; G6; sem mortes novas |
| R4.2 | **N4 frutas** | definições aprovadas, V5 | frutas como sub-decisão de comer; gostar e querer em dois registros; nutrição separada; neofobia do ovo | G1, G2; os dois registros se separam; critério ensino × cuidado |
| R5.1 | **N5** (P2, P2e) | N3, N4 | evento "o dono informa" no motor da V2, entra pela percepção (V6), nunca como reforço | informação × acoplada × sem; G5; P2e se recupera |
| R6.0 | **revisão do aprendiz** (Matheus, 2026-10-04) | LOBOS-MUNDO | teto dos pesos, janela de crédito e exposição, uma alavanca por vez, só em sementes de calibração; escolhe o ponto do experimento maior (`docs/TAREFA_V2_REVISAO_APRENDIZ.md`) | diagnóstico, sem gate |
| R6.1 | **experimento maior** | N3, N4, N5, L1 | P0, P1, P2, P2e, P3 × casado/descasado/mutável, com o mesmo aprendiz | as predições registradas antes (`ARQUITETURA_V2_VALIDACAO.md`, seção 6) |
| R6.2 | N6 memória | N5 | quatro marcos (registrado, codificado, recuperado, causal) | controle de recência e embaralhado |
| R6.3 | N7 arbitragem | L1 | duas prioridades | G5 |
| R6.4 | H-R2/H-R4 canais e genoma | N4, R6.1 | canais separados × escalar somado; sensibilidade por genoma com experiência acoplada | aprendizado desligado = vidas idênticas entre genomas |
| R7 | **N11 cérebros** | R6.1 | DigiBrain A (C3-like), B (CfC/A2C, ponto flutuante) e C (Fly-like), **só no Python**, com ablação das peças | `docs/research/digibrain/synthesis/brain_comparison.md` |
| R8 | **marco da fase 1** | R6–R7 | `docs/LEITURA_CONSOLIDADA_V2_FASE1.md` e a **escolha do DigiBrain do produto** | — |
| R8.1 | **decisão de produto: tirar elogiar e repreender** (Matheus, 2026-10-01: adiada para cá) | R6 (P1 × P3), R8 | decidir se o pet do produto aprende só pela consequência. Se sim, redesenhar o que depende dos botões: vínculo B (a coerência agrupa o feedback), disciplina das travessuras, mentira repreendida, catálogo do comando pelo chat; versão de pet própria | P1 ≥ P3 no experimento maior |
| W | **web** | R8 | porte do DigiBrain escolhido (pets v11), com gabarito Python → web | paridade |
| F2 | **humanos** | R8, ética, arte | gêmeos: o dono humano informa; reconhecimento e preferência | plano próprio |
| F3 | **genoma** | F2 | genoma com variância herdável (fisiologia, prior, sensibilidade por canal) | plano próprio; E1 falhou com 4,9% |

Fora da fase de experimentos: corpo 2D, luta dentro do cérebro, memória nuclear e estresse (D7), vício antes das frutas sem vício.

## 5. Divisão dos workers

Mesmo esquema da rodada 1 (`docs/V2_TRABALHO_PARALELO.md`): uma worktree por frente, um PR, merge só pelo Matheus. Quatro
chats; o B continua no aprendiz; o D sai da fila da GPU (a pesquisa da fase 1 é toda CPU).

| rodada | chat A | chat B | chat C | chat D | coordenador |
|---|---|---|---|---|---|
| **3** | A1 bola (implementação) | L1 calibração → validação | frutas: definições (doc) | **bancada** (infra P0–P3, acoplado, métricas) | conflitos de #114/#115; `V2_RODADA_2.md`; prompts de verificação ao Claude Science |
| **4** | N4 frutas (implementação) | N3 consequência | revisão bibliográfica da decomposição da plasticidade (via Claude Science) + plano de análise do experimento maior | bancada: modos casado/descasado/mutável | reservas de sementes e versões |
| **5** | apoio ao N5 (eventos de informação no motor da V2) | N5 dono informante | N6 memória (plano) | N7 arbitragem | — |
| **6** | experimento maior: validação única | H-R2/H-R4 canais | N6 implementação | — | leitura do experimento maior |
| **7** | DigiBrain A | DigiBrain B (CfC/A2C, Python) | DigiBrain C | harness N11 + ablações | — |
| **8** | — | — | — | — | marco da fase 1; escolha do DigiBrain da web |

Regras que valem para todos: um nó por PR; o plano de análise vai no **primeiro** commit, antes de qualquer run; calibração e
validação em PRs separados; a frente que mexe em `lobos.py` é sempre a do B (os outros só usam a interface `Aprendiz`), para
não haver dois PRs no mesmo arquivo.

## 6. Reservas (PROPOSTAS; o coordenador fecha na tarefa de cada um)

| o quê | calibração | validação |
|---|---|---|
| L1 | 3101…3505 | 4101…4505 (uma vez) |
| A1 bola | 6101…6505 | 7101…7505 |
| N3 | 8101…8505 | 9101…9505 |
| N4 frutas | 10101…10505 | 11101…11505 |
| N5 | 12101…12505 | 13101…13505 |
| experimento maior | 14101…14505 | 15101…15505 |
| N11 cérebros | 16101…16505 | 17101…17505 |

Já usadas, não reutilizar: vínculo B 5101…5505; comando com estilo 20261501/1601/1701.
Versões de pet na web: v10 vínculo B (#114); **v11 = o DigiBrain escolhido** (antes "lobos na web"); v12 bola, se a bola for
para o produto. Frutas e vício só ganham versão se forem para o produto.

## 7. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| M1 | Referendar G3–G6 com D1–D4 | **substituído (2026-10-01):** a validação da L1 roda com os alvos do plano rev. 2 como estão, sem bloquear | — |
| M2 | Aprovar o desenho da bola (#113) | aprovar | ação nova do pet quebraria a v1 (V5) |
| M3 | Adotar a pergunta maior e a arquitetura (A1, A6 de `ARQUITETURA_V2_VALIDACAO.md`) | **DECIDIDO pelo Matheus (2026-10-01):** adotadas; `PLANO_V2_PESQUISA.md` revisão 2 | — |
| M4 | Falha da L1 não para a V2 (é só o braço P3) | **DECIDIDO pelo Matheus (2026-10-01)**, e ampliado: nenhuma validação que falhe agora bloqueia a V2; o escopo futuro vai pedir revisão de todas | — |
| M5 | Frutas como sub-decisão de comer (V5) | sim | ações novas quebram a reprodução da v1 |
| M6 | O chat D deixa a fila da GPU e faz a bancada | sim | sem a bancada, cada nó monta o próprio orquestrador e P1–P3 deixam de ser comparáveis |
| M7 | Reservas de sementes da seção 6 | aprovar | reusar validação vicia o teste |
| M8 | v11 passa a ser o DigiBrain escolhido | sim | portar a L1 antes de saber se ela é o cérebro do produto é trabalho jogado fora |
| M9 | Comitê de ética e arte para a fase 2 | submeter quando o experimento maior passar | coletar sem aprovação invalida os dados |
