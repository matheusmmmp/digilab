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
