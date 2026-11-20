# Plano de análise — revisão do aprendiz: teto, janela de crédito ou exposição?

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status: **registrado antes de qualquer run** (2026-10-04). Tarefa `docs/TAREFA_V2_REVISAO_APRENDIZ.md` (rodada 6, chat B), linha R6.0
do `docs/ROADMAP_V2.md`. **Só sementes de calibração, 18101…18505** (faixa própria, `docs/V2_RODADA_5.md`). É um **diagnóstico para
escolher o ponto da calibração do N5 e do experimento maior**, não uma validação: não há gate, não há validação depois, e nenhum número
daqui é resultado de pesquisa sobre o aprendiz. Os números de desenho sem fonte estão marcados PROPOSTO.

## 1. A pergunta

O que segura o aprendiz da V2: o **teto** dos pesos, a **janela de crédito** ou a **exposição** à fruta? O que se sabe (artefatos):
- teto: pesos presos no limite em 12 de 20 vidas na L1 (`artifacts_v2_l1/validacao/`) e em 20 de 20 no N3 (`artifacts_v2_n3/validacao/`);
- o instinto decide cerca de 80% das decisões na L1 (G4 do aprendido 0,182, `docs/RESULTADO_V2_L1.md`);
- a janela do P1 é imediata: o sinal só vê o efeito da própria ação no mesmo passo (N3);
- exposição: p(comer | fruta no cenário) 0,208 no N4 (`artifacts_v2_n4/validacao/`).

Desde a rodada 6 os lobos veem as frutas e escolhem a fruta (#141, #148), e o P1 tem a E2 (o humor no sinal quando come fruta). É esse
aprendiz, no mundo das frutas, que o N5 e o experimento maior vão usar.

## 2. Desenho

| item | valor | de onde |
|---|---|---|
| mundos | `casado_frutas` e `descasado` (condições casado e descasado) | tarefa, seção 3 |
| braços | **P1** (consequência, com a E2) e **P3** (feedback do dono); **P0** (aprendizado desligado) como referência da mesma unidade | tarefa |
| dono | atencioso (o dono principal do experimento maior, E7) | `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` |
| vida | 14 dias, orçamento 224 (16 por dia) | E5; o de toda a V2 |
| unidades | as unidades derivadas da bancada (`unidades_derivadas`), bases 18101, 18202, 18303, 18404, 18505, **K = 4** por base: 20 unidades | regra E3; K PROPOSTO (custo: ~5 s por vida medida) |
| informação | nenhuma (P2 não roda; `w0_info` 0) | o N5 calibra a informação depois |
| sonda e bootstrap | sonda 64 estados × 200 amostras, semente 9001; bootstrap 10 000 reamostragens, semente 20261004, nível 0,95 | os do N3 |

**O ponto de hoje (a base):** `passo` 512, `teto` 1024 (1·S), sem traço, ganho do sinal 4, E2 ligada, `w_fruta` 6, ofertas nos 4
horários do N4 (9h, 12h, 15h, 18h). O orquestrador (`experiments/run_revisao_aprendiz.py`) monta cada ponto pela bancada
(`bancada_v2.rodar`, com as chaves `lobos` e `frutas` da config) e confere o replay de toda vida.

## 3. As alavancas, uma por vez

Cada ponto muda **uma** alavanca em relação à base; o resto fica na base. Todo campo novo tem padrão que reproduz a vida de hoje byte a
byte (testes em `tests/test_revisao_aprendiz.py`).

| alavanca | pontos | campo |
|---|---|---|
| **teto** (hoje 1·S = 1024) | T1 = 2048 (2·S); T2 = 4096 (4·S); T3 = 16384 (16·S, na prática sem teto: o diagnóstico do limite) | `ConfigLobos.teto` |
| **janela de crédito** (hoje imediata, só a decisão creditada) | J1 = traço de 2 decisões, λ = S/2; J2 = 4 decisões, λ = 3S/4; J3 = 8 decisões, λ = 7S/8 | `ConfigLobos.traco_decisoes`, `traco_fator` (novos) |
| **exposição** (hoje `w_fruta` 6, 4 ofertas por dia) | X1 = `w_fruta` 12; X2 = `w_fruta` 24; X3 = 8 ofertas por dia (9h às 19h30, de 1h30 em 1h30), `w_fruta` 6 | `ConfigFrutas.w_fruta`, `horarios_oferta` |

**O traço** (a "consequência atrasada" da tarefa, em inteiros): o sinal f_S creditado a uma decisão também chega às K decisões anteriores,
a k-ésima com `div_arred(f_S · λ^k, S^k)`. Vale para a consequência (P1, inclusive o sinal da fruta da E2) e para o elogio e a bronca (P3):
é o traço de elegibilidade do COACH (MacGlashan et al. 2017, arXiv:1701.06049, VERIFICADA no projeto). O crédito do chamado (latência,
chamado ignorado) continua preso ao chamado. Diferente da "consequência atrasada" declarada no plano do N3 (medir os drives até a decisão
seguinte), que mistura o cuidado do dono no sinal: o traço não muda o que o sinal mede, só a quem ele chega.

**A exposição** muda também o P0 (o instinto vê o mesmo `w_fruta` e as mesmas ofertas): o contraste de aprendizado é sempre contra o P0
do próprio ponto (seção 4, G_ap).

**Fora:** o teto relativo ao prior (o absoluto, até "sem teto", já diz se o teto segura), a janela estendida do N3 (mistura o dono),
mais frutas (variedade é fator do experimento maior), o passo, o ganho, a neofobia.

## 4. Medidas

Por ponto × mundo × braço; a unidade é a vida de uma unidade derivada (20 por célula).

| medida | o que é | de onde |
|---|---|---|
| **M1, aprendido decide** | fração das decisões em que o lobo de decisão decidiu (o impulso, com o mesmo u, daria outra ação) e a fração com fator | `motivo.motivos_de_vida` + `motivo_lobos` (inclui as regras do mundo desde o #149) |
| **M2, teto** | vidas com algum peso no teto (de 20) e pesos no teto por vida | `Aprendiz.pesos_no_teto` |
| **M3, deriva** | JSD ao prior no fim do dia 14 e a razão dia 14 / dia 7 (o G6 da L1) | `Bancada.deriva` |
| **M4, cuidado de si** | fração do tempo fora de privação, saúde média, humor médio | `metrics.desempenho_no_ambiente`, `privacao_nas_decisoes` |
| **M5, frutas** | `taxa_fruta_ruim` final (dias 8–14), consumos de fruta, p(comer \| fruta no cenário) = (decisões com fruta − ignoradas) / decisões com fruta | `metrics.taxa_fruta_ruim`, `contagem_frutas` |
| **G_ap, aprendizado da fruta** | `taxa_fruta_ruim` final do P0 − a do braço, na mesma unidade e no mesmo ponto (positivo = o braço evita a fruta ruim mais que o instinto) | M5 |
| M6 | acerto na tarefa do dono (P3) | `metrics.acerto_na_tarefa` |

Unidade sem consumo na janela final (taxa indefinida) fica fora do contraste daquela medida; o número de unidades usadas é relatado.

## 5. Contrastes e estatística

- **Contraste de alavanca:** Δ = medida no ponto − medida na base, **pareado na unidade** (mesma semente e genoma; as ofertas são as mesmas
  nos pontos do teto e da janela). IC 95% por bootstrap sobre as unidades (`metrics.bootstrap_ic`, parâmetros da seção 2).
- As unidades derivadas têm semente e genoma próprios; aqui cada uma conta sozinha (o agrupamento por base é do N5 e do experimento maior).
- **Sem correção de multiplicidade e sem gate:** são muitos contrastes (9 pontos × 2 mundos × 2 braços × medidas) num diagnóstico; o
  ponto recomendado é testado de novo na calibração do N5 e do experimento maior, com as sementes deles.

## 6. Leitura (registrada antes): o que segura

- **O teto segura** se, na base, metade ou mais das vidas do P1 ou do P3 têm peso no teto **e** algum ponto T aumenta M1 ou G_ap (P1,
  descasado) com IC inferior > 0.
- **A janela segura** se algum ponto J aumenta M1 ou G_ap (P1, descasado) com IC inferior > 0.
- **A exposição segura** se p(comer | fruta) na base fica abaixo de 0,30 (a faixa do N4) **e** algum ponto X aumenta os consumos e G_ap
  (P1, descasado) com IC inferior > 0.
- **Piora o cuidado de si** (o ponto fica fora da recomendação): Δ da fração fora de privação ou da saúde média, em P1 ou P3, em algum
  mundo, com IC 95% inteiro abaixo de 0.
- Nenhuma alavanca segurando: o diagnóstico diz isso, e a base fica como ponto recomendado.

## 7. O ponto recomendado (regra registrada antes)

1. **Por alavanca**, um ponto **ajuda** se não piora o cuidado de si e tem Δ G_ap (P1, descasado) com IC inferior > 0. Entre os que
   ajudam, o de maior IC inferior de Δ G_ap. Se nenhum ajuda por G_ap: o de maior IC inferior de Δ M1 (P1 e P3, descasado, média dos
   dois), se ele for > 0; senão a alavanca fica na base.
2. **O ponto recomendado** é a base com cada alavanca no ponto escolhido no passo 1.
3. **Conferência da combinação** (fase 2, só se duas alavancas ou mais saírem da base): o ponto combinado roda uma vez nas mesmas 20
   unidades. Se ele piora o cuidado de si, ou tem Δ G_ap menor que o da melhor alavanca sozinha, a recomendação é a melhor alavanca
   sozinha. A conferência é descritiva; não reabre a escolha das alavancas.
4. A recomendação vale para a calibração do N5 (o `w0_info` é calibrado nela, rodada 7) e do experimento maior; o relatório diz o que
   cada alavanca muda no P3 (M1, M6), que a regra do passo 1 não usa.

## 8. Saídas

`artifacts_v2_revisao/calibracao/<ponto>/` (`medidas.json`, `tabelas.json`, `meta.json` e `vidas/*.jsonl` da bancada; `resultado.json`
com as medidas da seção 4 e os contrastes da seção 5); `artifacts_v2_revisao/calibracao/diagnostico.json` (a leitura da seção 6),
`recomendacao.json` (a regra da seção 7) e `varredura.jsonl`. Os `vidas/*.politica.json` ficam fora do git (regeneráveis por replay).
Relatório em `docs/RESULTADO_V2_REVISAO_APRENDIZ.md`. Config `experiments/configs/v2_revisao/calibracao.json`.

## 9. Riscos registrados antes

1. **Poucos consumos de fruta**: com p(comer | fruta) ~0,2 e a neofobia, G_ap pode ter poucas unidades na janela final. O número de
   unidades usadas é relatado por célula; com menos de 10 o contraste é lido como **inconclusivo por exposição**.
2. **O teto sem teto (T3)** pode deixar pesos crescerem sem limite; é o diagnóstico do limite, não um candidato natural. Se ele for o
   escolhido, o relatório o compara com T2.
3. **O traço também mexe no P3** (elogio e bronca chegam às decisões anteriores): a leitura do P3 é descritiva.
4. **14 dias e 20 unidades** dão IC largo; um diagnóstico inconclusivo é resultado, e é dito assim.
