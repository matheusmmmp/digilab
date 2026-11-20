# Reforço

**NENHUMA ARQUITETURA ESCOLHIDA.** Este arquivo compara fontes e registra hipóteses.

## Nas fontes

| família | o que reforça | onde muda | status |
|---|---|---|---|
| Creatures | química de recompensa e punição | plasticidade local (hebbiana) na rede | VERIFICADA (Grand et al. 1997; Grand e Cliff 1998) |
| *Drosophila* | sistemas moduladores dopaminérgicos heterogêneos | plasticidade **compartimentalizada**, com regras por tipo celular | CORPUS (Aso e Rubin 2016; Otto et al. 2020) |
| Berto et al. | valoração homeostática + hedônica | RL num robô móvel | CORPUS |
| NORNBRAIN | recompensa escalar (química do C3) | traço de elegibilidade → A2C | software, não evidência |
| RL homeostático | redução de desvio homeostático como recompensa | — | VERIFICADA (Keramati e Gutkin 2014, `10.7554/elife.04811`) |
| feedback humano | sinal do dono como vantagem, dependente da política | — | VERIFICADA (MacGlashan et al., COACH, `arXiv:1701.06049`) |

## No DigiLab hoje (REPOSITÓRIO)

- **v1, congelado:** o bandit aprende com elogio e bronca do dono como recompensa **escalar**, creditada só à última decisão
  (até 15 ticks; `digilab/policies/bandit.py`), mais a penalidade de chamado ignorado. O temperamento escala o peso do
  elogio e da bronca (`digilab/temperamento.py`: sensibilidade e teimosia). A habituação enfraquece bronca e penalidade, mas
  nunca o elogio (assimetria B5 da auditoria, não documentada como decisão).
- **V2, L0:** os lobos têm o aprendizado desligado. **L1** (em calibração): sinal escalar do dono como vantagem (COACH), em
  inteiros, só a última decisão (`docs/TAREFA_V2_L1_DECISAO.md`).
- **Jogo web:** os gambits híbridos aprendem pela **consequência** da luta (saldo de dano + bônus de resultado; nos pets v8 o
  passo é multiplicado pela novidade do rival, M1). É o único reforço por consequência que existe, e só na web.
- **Não existe:** reforço homeostático (o instinto são regras à mão), hedônico, de dor, de medo.
- **Aviso da v1:** quando a luta passou a treinar o pet ("luta treina", V3b), 577 de 640 pets viraram forma sombria
  (`artifacts_educacao_v3b/`). Reforço por combate sem freio próprio vira espiral.

## A proposta: canais em vez de um escalar (HIPÓTESE DIGILAB, Matheus 2026-10-01)

```
reward_food   reward_social   reward_combat   aversive_pain   novelty   fear
```
em vez de `reward`, com o **genoma modulando a sensibilidade a cada canal**. Mesma experiência (por exemplo, vencer uma luta),
aprendizado diferente:

```
GENOMA A: combate ALTO, social MÉDIO, dor BAIXA
GENOMA B: combate BAIXO, social ALTO, dor ALTA
```

Por que é mais interessante que `agressivo = 0.8`: o traço deixa de ser um número configurado e passa a ser **sensibilidade
× história**. Dois pets com o mesmo genoma e vidas diferentes divergem; dois genomas com a mesma vida também. A
personalidade sai do aprendizado (`personality.md`).

**O que cada canal teria hoje no repositório:**

| canal | existe algo? | onde |
|---|---|---|
| reward_food | não | as frutas (`hedonic_system.md`) |
| reward_social | ações do dono existem (acariciar, elogiar); só elogio e bronca reforçam | `events.AcaoUsuario`, bandit |
| reward_combat | só na web (gambits) | `web/app/motor/gambits_pet.ts`; risco da V3b |
| aversive_pain | lesões existem, mas não reforçam | `ConfigLesoes`, `digilab/educacao.py` |
| novelty | novidade por rival existe, chave desligada | M1, `digilab/confianca.py` |
| fear | não | — |

**Precedente que já existe e não pode ser esquecido:** o temperamento da v1 já é "sensibilidade herdada a dois canais"
(elogio, bronca). No E1, o genoma (espécie + temperamento) explicou 4,9% da variância e o gate falhou. A proposta nova só é
diferente se os canais vierem da **consequência no mundo**, não do dono, e se o mundo tiver eventos desses canais em
quantidade (hoje quase não tem: não há ameaça, nem comida distinta, nem social além do dono).

**Advertência:** os canais são abstrações do DigiLab. Não correspondem a neurotransmissores, e a heterogeneidade da dopamina
da mosca não prova que vários canais vencem um escalar (contradição 5 do corpus).

## Hipóteses

| ID | pergunta | dependências | teste mínimo |
|---|---|---|---|
| H-R1 | reforço escalar (a soma) basta | N3 de `ARQUITETURA_V2_VALIDACAO.md` | braço de referência das outras |
| H-R2 | reforço multidimensional melhora atribuição ou adaptação sobre o escalar (antiga H-REINF-001) | H-R1 rodando; capacidade igual | mesmo aprendiz, mesmas oportunidades, **mesmo total de sinal**; só a representação muda |
| H-R3 | decompor em homeostático + hedônico explica escolhas que a necessidade não explica | `hedonic_system.md` | fatorial necessidade × fruta × efeito |
| H-R4 | o genoma, modulando a sensibilidade por canal, produz divergência de aprendizado com a **mesma** experiência | H-R2 | (a) aprendizado desligado: genomas diferentes dão vidas **idênticas** (a sensibilidade só age pelo aprendizado); (b) experiência acoplada (o mesmo registro de eventos reproduzido em malha aberta): medir a divergência dos pesos e da política por genoma |
| H-R5 | canal de combate precisa de freio próprio | H-R4 | repetir a V3b com o canal e o freio; nenhuma espiral sombria |

Confundidores: parâmetros a mais, peso implícito entre canais, escala total do sinal, mudança na atribuição de crédito.
Ordem recomendada: um canal (o homeostático) antes de vários (D-C de `docs/ARQUITETURA_V2_VALIDACAO.md`).
