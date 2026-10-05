# PLANO — Digilab V2: a pesquisa primeiro (revisão 2)

Status: a pergunta e a arquitetura estão **DECIDIDAS** pelo Matheus (2026-10-01); os gates e os números continuam **PROPOSTOS**.
Decisão anterior do Matheus que continua valendo: a V2 começa pela pesquisa; o jogo como produto (arte própria, servidor,
escala) vem depois e depende do que a pesquisa encontrar. Este é o plano de alto nível. Cada etapa ganha o próprio plano de
análise, congelado antes da run, e os números de cada gate só valem com artefato em disco. Ordem e divisão das etapas em
`docs/ROADMAP_V2.md`; arquitetura e desenho experimental em `docs/ARQUITETURA_V2_VALIDACAO.md`; estudo das fontes em
`docs/research/digibrain/`.

**O que mudou da revisão 1 (2026-10-01):** a pergunta deixou de ser só sobre o ensino do dono e virou a pergunta maior da
plasticidade (seção 2); a H1 antiga virou o braço P3; a arquitetura com o dono informante e o mundo validando é o alvo; a
pesquisa roda no Python e a web recebe um DigiBrain só; gates que falharem agora não param a V2.

## 1. De onde a V2 parte

A v1 fecha com uma leitura consolidada (`docs/LEITURA_CONSOLIDADA_DONO.md`): **neste motor o dono pesa pelo cuidado,
não pelo ensino.** A hipótese central foi refutada na confirmatória (atencioso − aleatório −0,034 [−0,072; +0,006],
`artifacts_confirmatoria/resultado.json`). A divergência entre os braços dos donos é de 0,02 bit (JSD,
`artifacts/divergence.json`; ao instinto, 0,03–0,05 bit). Só 13–18% das decisões têm fator explicável
(`artifacts_expressao/legibilidade.json`). O genoma explica 4,9%, e a forma final explica 96% da taxa no painel
(`artifacts_linhagem/`). O canal contínuo do caráter até a luta não abriu. A pergunta do efeito do dono está **encerrada**.

O que a v1 deixa de ativo e a V2 preserva:
- determinismo até o último float, com replay do log, e event sourcing;
- gates com artefato, plano de análise antes da run, sementes de calibração separadas das de validação, registro de desvios;
- uma versão de pet por mecânica;
- as regras da literatura (`literatura-digilab`): nunca alegar como novos instinto × aprendido, herdar o prior, nem "ensinado,
  não roteirizado".

## 2. A pergunta da V2 (DECIDIDA, 2026-10-01)

> **Em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?**

É a pergunta do efeito Baldwin (Hinton e Nowlan 1987; Fernando et al. 2018), e **não é nova**. O que pode ser contribuição é
separar a plasticidade **por fonte**, no mesmo aprendiz e com o cuidado controlado, e isso só se diz como "não localizamos"
depois de busca própria.

**Braços** (o mesmo aprendiz; só a fonte do sinal muda):

| braço | plasticidade | nó |
|---|---|---|
| P0 | nenhuma: só a predisposição herdada (o prior do instinto) | L0 |
| P1 | só consequências no mundo (valor homeostático da própria ação) | N3 |
| P2 | o dono informa certo, as consequências reforçam | N5 |
| P2e | o dono informa errado, o mundo tem de refutar | N5 |
| P3 | feedback explícito do dono como vantagem (a antiga H1) | L1 |

**Condições:** ambiente **casado** com o prior, **descasado** (o mundo contradiz o prior; as frutas fazem isso) e **mutável** (o
mundo muda no meio da vida).

**Vantagem adaptativa:** desempenho no próprio ambiente: tempo fora de privação, saúde e acerto na tarefa (G3-T). **Nunca** a força
na arena, que mede o arquétipo. O custo da plasticidade (exploração, deriva, tempo até aprender) é medido e reportado.

**Hipóteses por fase:**
- **H1 (fase 1):** a pergunta maior acima. A antiga H1 ("donos coerentes produzem políticas distinguíveis") vira o braço P3 e
  continua com os gates G3–G6.
- **H2 (fase 2, humanos):** o dono humano informa; o jogador reconhece o pet que ele mesmo criou entre dois gêmeos acima do acaso,
  e a preferência acompanha o sucesso (efeito IKEA condicionado ao sucesso).
- **H3 (fase 3, genoma):** um genoma com variância herdável (fisiologia, prior e sensibilidade por canal de reforço) separa
  criação de seleção num desenho fatorial. A separação criação × seleção é a lacuna que a revisão não encontrou publicada.
- **H0 de cuidado (controle permanente):** o "só cuidado" acoplado entra em todo experimento, porque é o único efeito robusto da
  v1, e qualquer marca nova tem de se separar dele.

## 3. A arquitetura (DECIDIDA como alvo, 2026-10-01)

O alvo é a arquitetura do Matheus (`docs/ARQUITETURA_V2_VALIDACAO.md`): genoma → fisiologia, cérebro inicial e plasticidade →
estado interno → percepção → contexto e memória → sistemas de comportamento → arbitragem → ação → corpo → consequência → valor
homeostático, hedônico e instrumental → reforço → aprendizado local. **Por fora, o dono dá informação e o mundo valida ou refuta.**

Três definições valem para toda a V2:
- **D-A.** A informação do dono entra pela percepção, nunca como reforço.
- **D-B.** O valor instrumental é "a ação conseguiu o que visava", sem o dono.
- **D-C.** Um canal de reforço primeiro (o homeostático); os outros, comparados com o escalar somado.

Validação contra o código (`ROADMAP_V2.md`, seção 2): cabe sem mudar o `engine.py` e reaproveita o aprendiz da L1. Os dois
bloqueios são estes:
- `AcaoPet` não pode ganhar membros, porque o bandit usa `tuple(AcaoPet)`: bola e frutas entram como sub-decisão.
- O mundo ainda tem poucos eventos para os canais.

**Pesquisa no Python, produto na web (decisão de 2026-10-01).** Todos os experimentos e a comparação entre cérebros (DigiBrain A
inspirado no Creatures, B com CfC e ator-crítico, C inspirado em circuitos da mosca) rodam no Python. A web recebe **um** DigiBrain,
o escolhido no fim da fase 1; só ele precisa de porte e paridade.

## 4. Fases e gates

### Fase 0 — fechar a v1 (FEITA)

Tag `v1-final`, inventário do jogo (`docs/V2_INVENTARIO_JOGO.md`), limpeza (#112), vínculo redesenhado (vínculo B, #114:
atencioso − aleatório +0,171 [+0,046; +0,280], `artifacts_v2_vinculo_novo/validacao/resumo.json`; limiar do Mega 0,4 mantido),
corpus em português (F0-CORPUS), comando com o estilo da espécie (#115), leitura do `revisao.csv` da moldura.

### Fase 1 — a pergunta maior, no Python

> **Atualização (2026-10-05, revisão 3 do roadmap, M10):** os nós da fase 1 passam a ter só gates de **mecanismo** (G1, chave
> desligada = vida de antes byte a byte, testes de comportamento). O cérebro A montado (N5, N6, N7 e canais) é calibrado **uma vez**
> (`docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`, 14101…14505) e validado **uma vez** no experimento maior com ablações (15101…15505). As
> validações por nó feitas antes (L1, A1, N3, N4) ficam como histórico. O texto abaixo descreve o desenho original.

Etapas (ordem e workers no `ROADMAP_V2.md`):
1. **Aprendiz:** L0 (aprendizado desligado = instinto byte a byte, **feito**); L1, feedback explícito (P3: calibração feita, #119;
   validação em curso).
2. **Ambiente:** bola (1a, desenho aprovado #113, implementação em curso); frutas (definições em curso, depois a implementação).
3. **Fontes de plasticidade:** N3, consequência (P1); N5, dono informante (P2, P2e).
4. **Bancada:** um orquestrador para P0–P3, modo acoplado e métricas da pergunta maior.
5. **Experimento maior:** P0, P1, P2, P2e, P3 × casado/descasado/mutável, com validação única.
6. **Memória, arbitragem, canais e genoma por canal:** N6, N7, H-R2/H-R4.
7. **Comparação de cérebros** A × B × C, só no Python, com ablação das peças.
8. **Marco:** `docs/LEITURA_CONSOLIDADA_V2_FASE1.md` e a escolha do DigiBrain da web.

Gates (PROPOSTOS; plano de análise congelado antes de cada run):

| gate | critério | onde vale |
|---|---|---|
| G1 replay | vida bit a bit pelo log (Python; e Python/web só para o DigiBrain do produto) | todo nó |
| G2 equivalência | chave desligada = vida de antes, byte a byte | todo nó |
| G3 divergência | JSD entre donos coerentes ≥ 0,10 bit, IC fora de 0,02 | braço P3 |
| G4 legibilidade | fator explicável em ≥ 50% das decisões, só sobre o aprendido | todos os braços que aprendem |
| G5 separação do cuidado | o efeito se mantém sem mortes e sem lesão e acima do "só cuidado" acoplado | todos |
| G6 sem deriva | distância ao prior não cresce sem limite em 14 dias; nenhum peso preso no teto | todos os braços que aprendem |
| pergunta maior | as predições registradas antes da run (`ARQUITETURA_V2_VALIDACAO.md`, seção 6) | experimento maior |

**Regra de parada (decisão do Matheus, 2026-10-01): a V2 segue mesmo com gates falhando agora.** O resultado de cada validação é
registrado tal como sair (negativo inclusive) e não bloqueia as etapas seguintes, porque o escopo futuro vai pedir que as
validações iniciais sejam revistas. Continuam valendo: plano antes da run, validação uma vez, nada de reajustar olhando a
validação.

### Fase 2 — humanos (H2)

Começa depois do marco da fase 1. 20 a 30 pessoas, 2 semanas, cada uma com dois ovos gêmeos (mesma semente de genoma e de
ambiente): um em que ela é o dono informante, outro com um dono sintético calibrado no comportamento dela. Medidas:
reconhecimento do próprio pet, preferência, sucesso do treino, tempo de uso.

Pré-condições:
- aprovação de comitê de ética **antes de qualquer coleta**;
- uma decisão sobre a arte: os sprites da Bandai não podem sair do uso pessoal, então ou arte própria, ou sessão local sem
  distribuição;
- o DigiBrain escolhido já portado para a web.

Gates: reconhecimento acima do acaso com IC fora de 0,5; preferência correlacionada ao sucesso; nenhum participante com o pet morto
por regra nossa.

### Fase 3 — genoma, criação × seleção (H3)

Primeiro um genoma com variância herdável, com plano e gate próprios (no E1 o genoma explicou 4,9%, e ajustar o genoma só para
passar o gate viciaria o teste). Depois, o desenho fatorial dono (criação) × escolha de qual pet cruzar (seleção). O dono é medido
pela **distribuição de formas** que produz, não pela força na arena. Gate: variância atribuível a criação e a seleção separadas,
com IC fora de zero; registrar como "não localizamos", nunca como primazia.

### Fase 4 — só depois: o jogo como produto

Arte própria ou licenciada, servidor com persistência do log, comparação com um produto vivo. Fora deste plano.

## 5. Fora do escopo da V2 de pesquisa

Mecânicas novas fora do que cada nó pede; corpo 2D completo; combate em tempo real; luta dentro do mesmo cérebro; PvP; memória
nuclear e estresse de longo prazo antes da memória (D7); vício antes das frutas sem vício; treino, luta e itens por comando; porte
para a web de qualquer cérebro que não seja o escolhido; execução de qualquer run sem plano de análise registrado antes.

## 6. Como se decide

Cada etapa abre com uma tarefa própria (`docs/TAREFA_V2_<FRENTE>.md`) e um plano de análise (`docs/PLANO_ANALISE_V2_<FRENTE>.md`)
commitado antes da run. Os números dos gates são PROPOSTOS até o Matheus referendar. A mudança de um número depois de uma run vai
para `docs/REGISTRO_DESVIOS.md`. Decisões ainda abertas: M5–M9 do `docs/ROADMAP_V2.md` (frutas como sub-decisão, reservas de
sementes, v11 como o DigiBrain escolhido, comitê de ética).
