# ROADMAP — Digilab V2 até a fase de experimentos completa

Status: **PROPOSTO** (coordenador, 2026-10-01). Este documento organiza as etapas a partir de agora. Ele não substitui o
`docs/PLANO_V2_PESQUISA.md` (as hipóteses e os gates) nem o `docs/DEFINICOES_V2.md` (as definições D1–D11): só põe tudo
numa ordem, com dependências, gates e decisões. Nenhuma etapa roda sem a tarefa e o plano de análise dela commitados antes.
Os números citados valem pelo artefato apontado, não por este texto.

"Fase de experimentos completa" quer dizer as fases 1, 2 e 3 do plano da V2, com gate e resultado registrados, positivos
ou negativos. A fase 4 (o jogo como produto) fica fora.

## 1. Os achados que dirigem o plano

| achado | fonte | consequência para o plano |
|---|---|---|
| Neste motor o dono pesa pelo cuidado, não pelo ensino; a H-central foi refutada (−0,034 [−0,072; +0,006]) | `docs/LEITURA_CONSOLIDADA_DONO.md`, `artifacts_confirmatoria/resultado.json` | toda marca nova tem de se separar do cuidado: o braço "só cuidado" acoplado é obrigatório em todo experimento (D4) |
| O instinto já dá fator explicável em 34–76% das decisões; o bandit, 13–18% | `artifacts_expressao/legibilidade.json` | o G4 mede só o aprendido (D3); o controle de capacidade sem lobos entra na validação (D2) |
| A L0 reproduz o instinto byte a byte (G1 e G2 passam) | `tests/test_lobos.py` (PR #108) | a base do aprendiz novo está pronta; a L1 pode ligar o aprendizado |
| O vínculo B passa: atencioso − aleatório +0,171 [+0,046; +0,280] na validação; o vínculo de hoje dá −0,066 nas mesmas sementes | `artifacts_v2_vinculo_novo/validacao/resumo.json` (PR #114, ainda não mesclado) | o defeito do vínculo está resolvido na pesquisa; no jogo curto o Mega não inverte (decisão do limiar 0,4 pendente) |
| A forma final explica 96% da taxa no painel; o genoma, 4,9% | `artifacts_linhagem/dono_ambiente/resultado.json`, `artifacts_linhagem/natureza_criacao/` | na fase 3 o dono é medido pela distribuição de formas, não pela força na arena; o genoma precisa de variância herdável antes |
| O estilo da espécie em português não gera rejeição (0 de 30); o comando com estilo passa na rodada 4 (falsos positivos 3,3%, imperativos 88,3%) | `artifacts_voz/estilo_portugues/resumo.json`, `artifacts_fala_livre/comando/rodada4_estilo/resumo.json` (PR #115, ainda não mesclado) | a fala com estilo pode ser ligada no jogo depois do merge |
| Gostar e querer exigem dois registros; a saciedade sensório-específica é canal distinto da fome; não há fonte primária do vício no Creatures; a ética de desenho existente só cobre mecânicas dirigidas ao jogador | `v1/docs/referencias/V3_SINTESE_FRUTAS_VICIO_V1_V6.md` (fora do git) | as frutas precisam das definições antes do desenho (seção 3, etapa P5) |
| **Correção:** a síntese V3 diz que o projeto "já usa RL homeostático para o instinto". O instinto é regra escrita à mão sobre drives homeostáticos, com zero aprendizado (`digilab/policy.py`, `PoliticaInstinto`). O RL homeostático (Keramati e Gutkin) é só a base teórica citada em `docs/MAPA_SISTEMA_2026-09-29.md` | código | derivar o vício de Keramati, Durand e Girardeau (`10.1037/rev0000046`) **não** é reaproveitar um mecanismo existente: seria aprendizado novo sobre os drives. Fica registrado na decisão M6 |

## 2. O caminho crítico

```
Rodada 2 (agora)        Rodada 3              Rodada 4               Rodada 5–6              Fase 2          Fase 3
─────────────────       ─────────────         ─────────────          ─────────────           ──────          ──────
referendo G3–G6 ──┐
L1 calibração ────┴──► L1 validação ──┬──► L1+A1 juntos ──┬──► A2 frutas ──► A3 vício ──┐
A1 desenho ───────────► A1 bola ──────┘                   ├──► L2 memória                ├──► marco F1 ──► humanos ──► criação × seleção
frutas: definições ───► frutas: desenho                   └──► L3 duas prioridades ──────┘   (ética,       (genoma com
                                                                                                arte)         variância)
```

Regra que vale em todo o grafo: **uma alavanca nova por vez**. Cada uma passa sozinha antes de entrar junto com outra
(`06_EXPERIMENT_DAG.md`, fronteiras). Se a L1 falhar na validação, a V2 registra o negativo e **para** (plano da V2, §3);
as etapas depois dela só existem se a L1 passar.

## 3. Trilha P: pesquisa (caminho crítico)

Cada etapa abre com `docs/TAREFA_V2_<FRENTE>.md` e `docs/PLANO_ANALISE_V2_<FRENTE>.md` commitados antes da run.

| etapa | depende de | entrega | gate | se falhar |
|---|---|---|---|---|
| **P1. L1 calibração** (chat B, em andamento) | L0 na `main` ✔ | código do lobo de decisão aprendendo (COACH, inteiros), plano rev. 2, calibração em 3101…3505 | nenhum (calibra passo e teto) | ajusta na calibração; nunca na validação |
| **P2. Referendo G3–G6** | nada | os gates do plano da V2 marcados DECIDIDO, com as definições D1–D4 | — | sem referendo, a validação da L1 não roda |
| **P3. L1 validação** | P1, P2 | uma run em 4101…4505, com os braços "só cuidado" acoplado, controle de capacidade sem lobos e bandit de referência | G3 (JSD ≥ 0,10 bit, IC fora de 0,02), G3-T ao lado, G4 só sobre o aprendido, G5 acima do acoplado e sem mortes/lesão, G6 sem deriva | negativo registrado; **a V2 para** e volta para o Matheus decidir |
| **P4. A1 bola** (desenho no PR #113) | aprovação do desenho; L0 | `MotorAmbiente` com a bola atrás de chave desligada; aprendizado **desligado** (a bola sozinha) | G1, G2 (chave desligada = vida de hoje byte a byte); 1a-pet: o comportamento muda com a bola, com o acoplado | a bola sai; a 1a volta para o inventário (`V2_INVENTARIO_JOGO.md`) |
| **P5. Frutas: definições** (tarefa pausada, `DEFINICOES_FRUTAS_V2.md`) | busca V1–V6 no repositório | as quatro variáveis (necessidade, gosto, efeito, vício) com as sete restrições da literatura, cada uma com o campo do log; nada de código ou número | revisão do Matheus | — |
| **P6. L1+A1 juntos** | P3 e P4 passando | o aprendiz numa vida com a bola | G1–G6 de novo; 1a-dono (sem apoio na literatura: reportar como pergunta aberta, D6) | fica registrado qual das duas não compõe |
| **P7. A2 frutas sem vício** | P5 aprovado, P6 | frutas com gosto e efeito separados, saciedade sensório-específica, neofobia do ovo; versão de pet própria | G1, G2; **critério ensino × cuidado** da P5 contra o "só cuidado" acoplado | as frutas ficam como mecânica de jogo, não de pesquisa |
| **P8. A3 vício** | P7 passando; decisão M6 (seção 7) | a assimetria "querer cresce, gostar não acompanha", atrás de chave | G1, G2; a assimetria aparece nos dois registros (não num escalar); nenhuma morte nova vinda do vício | o vício não entra |
| **P9. L2 memória e emoção** (peças do DF) | P3 | slots com categorias da 1a; desempate explícito | a memória muda a decisão além da recência (controle de recência e embaralhado); citação de memória acima dos 6,9% da v1 (`artifacts_v1_memoria_espacos/metrics.json`) | fica fora |
| **P10. L3 duas prioridades** | P3 | necessidade × pedido do dono, por cima do motor | G5 continua valendo | fica fora |
| **P11. Marco da fase 1** | P3–P10 (o que tiver passado) | `docs/LEITURA_CONSOLIDADA_V2_FASE1.md`: o que pesa, o que não pesa, o que vai para os humanos | G3, G4 e G5 da L1 são a condição da fase 2 | sem eles, não há fase 2 |

O que **não** entra na fase 1, pelas definições: memória nuclear e estresse de longo prazo (D7), recompensa
multidimensional e janela de crédito maior (fora da L1, uma mudança por vez).

## 4. Trilha J: jogo web (acompanha a pesquisa, nunca na frente)

| etapa | depende de | entrega |
|---|---|---|
| J1. Merges pendentes | conflito resolvido + suíte completa | #113 (desenho), #114 (vínculo B, pets v10), #115 (estilo e comando) |
| J2. Decisão do limiar do Mega nos v10 | J1 | manter 0,4, rever, ou tirar o vínculo do requisito (M3) |
| J3. Lobos na web (pets v11) | P3 passando | gabarito Python → web, como o M1 (`confianca.test.ts`) |
| J4. Bola na web (pets v12) | P4 passando | mesma regra |
| J5. Frutas e vício na web (versões seguintes, na ordem de chegada) | P7, P8 | idem; a fala do pet obedece ao vocabulário da P5 (nenhuma frase diz que ele sente prazer) |
| J6. M1 gates G3–G6 | plano de análise próprio (`docs/PLANO_ANALISE_M1.md`) | só se o M1 for usado em pesquisa; para o jogo pode esperar |

As reservas de versão são cumulativas pela ordem de chegada: v10 vínculo B, v11 lobos, v12 bola. As frutas e o vício
ficam com as próximas livres, nessa ordem, quando chegarem.

## 5. Trilha L: literatura (antes de cada desenho)

| etapa | para | estado |
|---|---|---|
| L-a. Busca Q1–Q7 (gates, legibilidade, DF) | P2, P3 | feita e no repositório (`docs/referencias/V2_SINTESE_Q1_Q7.md`) |
| L-b. Busca V1–V6 (frutas, gosto, vício) | P5 | feita; **fora do git** (`v1/docs/referencias/V3_*`): entra no repositório junto com a P5 |
| L-c. Ler *Creation* (Grand, 2001) | P8, só se o Matheus quiser o Creatures como referência | existência confirmada, conteúdo não lido; até lá, nada sobre vício pode ser atribuído a ele |
| L-d. Humanos: reconhecimento do próprio agente, efeito IKEA, ética de coleta | fase 2 | a pedir; o prompt sai junto com o desenho da fase 2 |
| L-e. Genoma com variância herdável (H-PLAST-001, canalização: Pigliucci et al., `10.1242/jeb.02070`) | fase 3 | a pedir |

## 6. Fases 2 e 3

**Fase 2, humanos (H2).** Começa só com G3, G4 e G5 da L1 passando.
1. Pré-condições:
   - aprovação de comitê de ética **antes de qualquer coleta**;
   - decisão da arte: os sprites da Bandai não podem sair do uso pessoal; ou arte própria, ou sessão local sem distribuição;
   - vínculo B no jogo (J1);
   - dono sintético calibrado no comportamento de cada participante.
2. Desenho: cada pessoa recebe dois ovos gêmeos (mesma semente de genoma e de ambiente). Um é cuidado por ela, o outro
   pelo dono sintético calibrado nela.
3. Plano de análise e piloto (com sementes e participantes separados da coleta).
4. Coleta de 2 semanas e análise: reconhecimento acima do acaso, preferência correlacionada ao sucesso do treino,
   nenhuma morte por regra nossa.

**Fase 3, criação × seleção (H3).** Começa depois da fase 2.
1. **Genoma com variância herdável.** No E1 o genoma pesava 4,9% e o gate falhou. Um genoma ajustado para passar o
   gate viciaria o teste (decisão de 2026-09-29), então o genoma novo precisa de plano próprio e gate antes do fatorial.
2. Desenho fatorial: dono (criação) × escolha de qual pet cruzar (seleção). O dono é medido pela distribuição de formas,
   não pela força na arena.
3. Gate: variância atribuível à criação e à seleção separadas, com IC fora de zero. É a lacuna que a revisão não
   encontrou publicada; registrar como "não localizamos", nunca como primazia (D5).

## 7. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| M1 | Referendar G3–G6 com as definições D1–D4 | Referendar agora, antes de a L1 terminar a calibração | Referendar depois de ver a calibração parece ajuste olhando dados; sem referendo a validação não roda |
| M2 | Aprovar o desenho da bola (#113): brincar com a bola conta como brincar, efeito só no humor, sem sorteio novo, bola sozinha antes da L1 | Aprovar | Uma ação nova do pet mudaria a lista de ações e quebraria a reprodução byte a byte da v1 |
| M3 | Limiar do Mega nos pets v10 (o vínculo B não inverte o Mega no jogo curto) | Manter 0,4 até haver medida com um dono humano; o vínculo B fica como medida de pesquisa | Mexer no limiar com donos sintéticos que quase não dão feedback calibra o jogo para quem não joga assim |
| M4 | Se a L1 falhar: parar a V2 ou abrir uma pergunta nova | Seguir o plano: registrar o negativo e parar; uma pergunta nova só com plano novo | Continuar ajustando depois da validação transforma um negativo limpo em busca até achar |
| M5 | Frutas: vêm depois da bola (D10) e passam sem vício antes do vício | Manter a ordem P7 → P8 | Vício junto com as frutas acopla gosto à saúde antes de saber se o gosto sozinho separa ensino de cuidado |
| M6 | Vício: derivar de RL homeostático (Keramati, Durand e Girardeau) ou mecânica nova | Decidir na P5, sabendo que **as duas são mecânica nova**: o instinto não aprende, então "derivar do que já existe" seria aprendizado novo sobre os drives | Escolher pela premissa errada vende como reaproveitamento algo que precisa de gate próprio |
| M7 | Fase 2: arte própria ou sessão local | Sessão local no piloto; decidir a arte só se a fase 2 for publicada | Publicar com os sprites da Bandai está proibido pelas regras do projeto |
| M8 | Fase 2: comitê de ética | Submeter assim que a L1 passar, porque o prazo do comitê é o gargalo da fase 2 | Coletar sem aprovação invalida os dados para publicação |
| M9 | Ler o livro do Grand ou abandonar o Creatures como referência | Abandonar: o desenho não precisa dele | Citar o Creatures sem fonte primária é desenhar por wiki de fã |

## 8. Reservas e convenções

- Sementes: L1 calibração 3101…3505, validação 4101…4505 (uma vez); vínculo B validação 5101…5505 (já usada); comando com
  estilo, rodada 4: 20261501, 20261601, 20261701 (já usadas). A1, frutas e vício: faixas próprias, definidas na tarefa de
  cada um, nunca reaproveitando faixas de validação já usadas.
- GPU: uma frente por vez. Só a fala usa GPU; a pesquisa da fase 1 é CPU.
- Cada frente trabalha numa worktree própria (`docs/V2_TRABALHO_PARALELO.md`), entrega um PR e para. O merge é do Matheus.
- Cada rodada fecha com `docs/V2_RODADA_<N>.md` (marco, PRs, decisões, divisão da seguinte).
