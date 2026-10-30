# Plano de análise — o experimento maior (plasticidade por fonte × condição do mundo)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status: **registrado antes de qualquer dado** (2026-10-04). Tarefa `docs/TAREFA_V2_PLANO_EXPERIMENTO_MAIOR.md`; etapa R6.1 do
`docs/ROADMAP_V2.md`. **Só papel:** nenhuma run, nenhum código. A run só acontece depois de N3 (P1), N4 (frutas), N5 (P2, P2e) e da
bancada de mundos estarem na `main`, e depois do adendo da seção 7.3. Todo número citado aponta o artefato; os que não têm artefato estão
marcados PROPOSTO. **Decisões E1–E8 aprovadas pelo Matheus como recomendadas em 2026-10-04** (seção 11).

**A pergunta** (`docs/PLANO_V2_PESQUISA.md`, seção 2, DECIDIDA em 2026-10-01):

> Em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?

**Não é novidade e não se diz que é.** É a pergunta do efeito Baldwin: Hinton e Nowlan 1987 (VERIFICADA, sem DOI); Whitley, Gordon e
Mathias 1994, `10.1007/3-540-58484-6_245`; Turney, Whitley e Anderson 1996, `10.1162/evco.1996.4.3.iv`; Fernando et al. 2018,
`10.1145/3205651.3205763`; e a partição instinto × aprendido dentro do mesmo agente já está publicada em Hallawa et al. 2021,
`10.1145/3449726.3459475` (todas VERIFICADA; `docs/referencias/referencias_verificadas.csv`). O que pode ser contribuição é **decompor a
plasticidade por fonte no mesmo aprendiz, com o cuidado controlado**, e isso só se diz como "não localizamos" depois da busca do prompt 11
(decisão D5 de `docs/DEFINICOES_V2.md`).

**Não reabre nada.** A hipótese central da v1 segue refutada; a pergunta do dono neste motor segue encerrada
(`docs/LEITURA_CONSOLIDADA_DONO.md`); o resultado negativo da L1 (`docs/RESULTADO_V2_L1.md`) entra aqui como o braço P3, sem ser refeito.

---

## 1. Braços: o mesmo aprendiz, só a fonte do sinal muda

Tudo pela bancada (`experiments/bancada_v2.py`): vida = (genoma, mundo, dono, braço, semente), o cérebro `PoliticaLobos` com o mesmo prior e
a mesma `ConfigLobos` em todos os braços, só o que passa por `receber_acao_dono` (ou pelo gancho do sinal de consequência) muda.

| braço | fonte do sinal | o que o aprendiz recebe | nó que entrega |
|---|---|---|---|
| **P0** | nenhuma | nada; aprendizado desligado (o prior fixo, byte a byte o instinto) | L0 / bancada |
| **P1** | consequência | o valor homeostático da própria ação (redução de déficit; Keramati e Gutkin 2014, `10.7554/elife.04811`, VERIFICADA) | N3 |
| **P2** | informação certa + consequência | a informação do dono pela percepção (nunca como reforço: D-A) e o sinal do P1 | N5 |
| **P2e** | informação errada + consequência | a mesma informação, invertida; o mundo tem de refutar | N5 |
| **P3** | feedback explícito | elogio e bronca como vantagem (COACH; MacGlashan et al. 2017, arXiv:1701.06049, VERIFICADA) | L1 |

**Controles, em todo braço com dono:**
- **"Só cuidado" acoplado** (H0; `docs/DEFINICOES_V2.md`, seção 3; decisão D4): o registro da vida, sem os sinais de ensino e sem a
  informação do dono, com **as mesmas ações de cuidado e as mesmas ofertas de fruta nos mesmos ticks** (decisão F7 das frutas), rejogado em
  malha aberta pelo modo acoplado da bancada. Um efeito do dono só conta como ensino acima dele e sem diferença de saúde e de mortes (G5).
- **Controle de capacidade sem lobos** (`policies/camada_unica.py`, decisão D2): só nos braços P1 e P3, como secundário (decisão E6).

**Dono.** O dono principal é o **atencioso** em todos os braços: as mesmas ações de cuidado (a rng do dono é a mesma em todos os braços,
pela bancada), e cada braço só recebe a fonte dele. O P0 e o P1 recebem o mesmo cuidado sem nenhum sinal. Os outros donos são secundários.

**O que o dono sabe é o mesmo nos três braços com dono.** No P2 ele informa o efeito **real** da fruta; no P2e informa o contrário; no P3
ele julga a escolha de fruta pelo efeito real (elogia a fruta boa, repreende a ruim), além da tarefa de sempre (`donos.julgar_acao`). Assim
P2 e P3 diferem só no **canal** (percepção × reforço), não no conhecimento. É um contrato para o N5 e para os donos sintéticos (seção 3).

## 2. Condições: casado, descasado, mutável

O mundo é o campo `mundo` da bancada (`docs/TAREFA_V2_BANCADA_MUNDOS.md`). A tarefa fixa o **casado** como o mundo padrão; o descasado e o
mutável dependem das frutas (N4) e ficam aqui como **contrato** que o N4 e a bancada de mundos cumprem.

| condição | o que o mundo faz | quem constrói |
|---|---|---|
| **casado** | o mundo para o qual o prior foi feito: o mundo padrão (`padrao`) | bancada (já existe) |
| **casado com frutas** (o casado principal, decisão E1) | frutas no cenário, e **a fruta de maior preferência inata do pet tem o efeito bom** | N4 + bancada de mundos |
| **descasado** | frutas no cenário, e **a fruta de maior preferência inata do pet tem o efeito ruim** (por genoma: o descasado é relativo à preferência de cada pet, F5) | N4 + bancada de mundos |
| **mutável** | começa casado com frutas; **no meio da vida o efeito das frutas troca** (a boa vira ruim e vice-versa) | N4 + bancada de mundos |

**Por que o "casado com frutas".** Com o casado = mundo padrão, o casado e o descasado diferem em duas coisas ao mesmo tempo: a presença de
frutas e o desencontro entre o prior e o mundo. O contraste que a pergunta pede é só o segundo. Com o casado com frutas, as três condições
têm as mesmas ofertas e diferem só no sinal do efeito. O mundo padrão continua rodando como referência (decisão E1).

**Ofertas iguais em todos os braços.** O calendário das ofertas de fruta sai da semente, não do estado do pet nem do braço: o mesmo pet, em
qualquer braço, vê as mesmas frutas nos mesmos ticks (como a bola da 1a-pet, que aparecia em horários fixos). Se a oferta dependesse do
estado, os braços teriam exposições diferentes e o contraste mediria exposição. As ofertas ficam fora do orçamento e fora do sorteio do
dono aleatório (decisões B1 e B2 da bola, adotadas para as frutas no N4).

### 2.1 Fator a considerar: variedade de frutas (PROPOSTO, Matheus 2026-10-04)

Depois do diagnóstico de gargalos (o gargalo é o aprendiz e a densidade de consequências, não o número de objetos), o Matheus pediu para
considerar a **variedade de frutas** como fator: por exemplo, 2 × 6 tipos de fruta, com gostos e efeitos diferentes, dentro do mesmo
mundo das frutas (nenhum objeto novo). Pergunta: mais escolhas com consequência aumentam a vantagem de aprender sobre o herdado?
**Não entra nas predições registradas acima.** Se for adotado, entra por **adendo registrado antes da calibração**, com predição própria,
o custo em unidades (o fator multiplica as células) e a decisão do Matheus. Até lá, o experimento roda com o número de frutas do N4.

## 3. Contratos que precisam estar na `main` antes da calibração

Cada item é conferido por teste no PR que o entrega; sem ele, a calibração não começa.

| # | contrato | quem entrega |
|---|---|---|
| K1 | P0 pela bancada = instinto byte a byte, também nos mundos com frutas (o prior não lê as frutas além do que o instinto já lê) | bancada de mundos |
| K2 | P1: o sinal de consequência **enxerga o canal em que a fruta age** (seção 3.1) | N3 |
| K3 | P2 e P2e: a informação entra pela percepção, nunca pelo gancho do reforço; P2e = P2 com o conteúdo invertido, mesmos ticks | N5 |
| K4 | Os três braços com dono conhecem o mesmo efeito real (seção 1) | N5 e donos sintéticos |
| K5 | Calendário de ofertas por semente, igual em todos os braços; ofertas fora do orçamento e do sorteio do aleatório | N4 + bancada de mundos |
| K6 | Condições `casado_frutas`, `descasado`, `mutavel` montadas pela bancada, por genoma (preferência inata) | bancada de mundos |
| K7 | Modo acoplado com mundo: o "só cuidado" acoplado reproduz as ofertas de fruta | bancada de mundos |
| K8 | Registro derivado `consumo` (tick, fruta, efeito aplicado) e as medidas da seção 4.1 em `digilab/metrics.py`, uma vez só | N4 |
| K9 | G1: toda vida e todo acoplado rejogados do log, bit a bit | todos |

### 3.1 O conflito entre F6 e o sinal do N3 (decisão E2)

- **F6** (decidida em 2026-10-01): o efeito ruim de uma fruta fica no **humor**, fora de `Estado.em_privacao`, para não passar pela cadeia
  privação → saúde → morte.
- **A tarefa do N3** tira o humor do sinal do P1 ("por ser o canal da bola e o do efeito ruim das frutas").
- Juntas, as duas fazem o P1 **cego ao efeito da fruta**: no descasado ele não teria como aprender, e a predição 2 falharia por construção,
  não por resultado.
- **Decidido (E2, Matheus, 2026-10-04):** no experimento maior, o sinal do P1 inclui o humor quando a mudança vem de comer uma fruta (o
  canal em que o mundo descasado age). O N3 sozinho, sem frutas, continua como a tarefa dele define. A F6 não muda: o efeito ruim segue no
  humor, fora da cadeia privação → saúde → morte. A alternativa descartada era o efeito ruim nutricional.
- **Consequência para o N3 (chat B):** o sinal de consequência precisa aceitar o humor vindo do consumo de fruta como componente
  declarado, desligado sem frutas, para o contrato K2 valer quando o N4 e o N3 se juntarem. É ajuste de contrato, não de desenho do N3.

## 4. Medidas

### 4.1 Primária: a consequência que o pet sofre no mundo das frutas

A vantagem adaptativa é o desempenho no próprio ambiente, nunca a força na arena (A10 da arquitetura). Como o efeito das frutas fica no humor
(F6), **o tempo fora de privação e a saúde não mudam com a escolha de fruta** por construção. A medida primária é, então:

- **`taxa_fruta_ruim`**: a fração dos consumos de fruta em que o pet comeu a fruta que, **naquele momento**, tinha o efeito ruim (no mutável,
  a fruta ruim troca no meio da vida). Menor é melhor. Por vida e por janela de dias.

Ela entra em `digilab/metrics.py` (K8), calculada do registro `consumo`. É uma medida nova; nenhum número dela existe hoje.

### 4.2 Secundárias (já na bancada, `digilab/metrics.py`)

| medida | função | o que mostra aqui |
|---|---|---|
| tempo fora de privação, saúde média | `desempenho_no_ambiente` | o **canal de cuidado**: precisa ficar igual entre braços para um efeito valer como plasticidade, não cuidado |
| humor médio | (amostrado como a saúde; entra com K8) | o efeito agregado das frutas no corpo |
| acerto na tarefa do dono (G3-T) | `acerto_na_tarefa` | o que o P3 e o P2 ensinam além das frutas |
| deriva ao prior e tempo até a metade do caminho | `custo_da_plasticidade` | o **custo** da plasticidade (exploração, deriva, tempo até aprender), reportado sempre |
| consequências até a metade do caminho | `eficiencia_amostral` sobre a curva de `taxa_fruta_ruim` | a eficiência amostral da predição 3 (seção 5) |
| G4 do aprendido | `motivo.motivo_lobos` (como na L1) | quanto do comportamento é decidido pelo que foi aprendido |
| G6 (pesos no teto, razão da deriva) | como na L1 | se o aprendizado ficou preso no teto (na validação da L1, 12 de 20 vidas tinham peso no teto: `docs/RESULTADO_V2_L1.md`) |
| mortes, lesões | registro da vida | o canal de cuidado |

### 4.3 Janelas no tempo

Vida de **14 dias** (a duração de todas as runs da V2). Janela **inicial** = dias 1 a 7, janela **final** = dias 8 a 14 (a mesma janela de 7
dias do G3-T da L1). No mutável, as janelas são **antes** e **depois da troca**, com a troca no fim do dia 7.

## 5. Predições registradas antes

Todas são hipóteses do Digilab, não afirmações das fontes. Cada uma tem a medida, o contraste, o teste e o que conta como confirmar ou
refutar. Os contrastes são **pareados por unidade** (o mesmo pet, na mesma semente e genoma, em braços diferentes; seção 6). **Δ** é a margem
de relevância da seção 6.3.

### Predição 1 — P0 vence no casado

- **Por quê:** no mundo para o qual o prior foi feito, aprender só custa (exploração e deriva).
- **Medida:** `taxa_fruta_ruim` na janela final; no casado com frutas, ela mede o quanto a plasticidade tira o pet da escolha que já era certa.
- **Contraste primário:** P1 − P0 (positivo = P1 come mais a fruta ruim). Secundários: P2 − P0, P3 − P0.
- **Confirma:** o contraste primário é **positivo** pelo teste da seção 6.2. **Refuta:** IC 95% inteiro abaixo de 0 (a plasticidade
  melhora até o casado) **ou** IC 90% inteiro dentro de (−Δ, +Δ) (sem custo detectável: P0 não "vence", empata). **Inconclusiva:** o resto.
- **Ao lado, sempre:** `custo_da_plasticidade` (deriva e tempo) de cada braço no casado, que é o custo que esta predição atribui à
  plasticidade.

### Predição 2 — P1 vence P0 no descasado e no mutável, se a vida for longa

- **Medida:** `taxa_fruta_ruim` na janela final (descasado) e na janela depois da troca (mutável).
- **Contrastes primários:** P0 − P1 no descasado e P0 − P1 no mutável (positivo = P1 come menos a fruta ruim).
- **Confirma:** nas duas condições, contraste **positivo** pelo teste da seção 6.2. **Refuta:** em qualquer das duas, IC 95% inteiro abaixo
  de 0, **ou** IC 90% inteiro dentro de (−Δ, +Δ). **Confirma parcialmente:** só uma das duas.
- **"Se a vida for longa":** a curva diária P0 − P1 é reportada inteira. Se a predição não confirma, mas a diferença ainda cresce nos últimos
  dias (inclinação dos dias 11 a 14 com IC acima de 0), o resultado é **inconclusivo por duração**, não refutado. Uma vida mais longa seria
  um adendo novo, nunca uma troca depois da validação (decisão E5).
- **Requisito:** só é teste de verdade com o K2 (seção 3.1; decidido em E2). Se o K2 não estiver na `main` na hora da run, a predição fica
  registrada como **não testável** e não é reportada como
  refutada.

### Predição 3 — P2 chega lá com menos consequências que P1

- **Medida:** **consequências até a metade do caminho**: o número de consumos de fruta até o primeiro dia em que a `taxa_fruta_ruim` chega
  à metade do caminho entre o P0 da mesma unidade (o piso) e o melhor valor possível (0: nunca comer a fruta ruim), pela
  `eficiencia_amostral`. Condição: descasado.
- **Contraste primário:** P1 − P2 (positivo = P2 precisou de menos consumos).
- **Confirma:** contraste **positivo** pelo teste da seção 6.2. **Refuta:** IC 95% inteiro abaixo de 0 (a informação certa atrasou o
  aprendizado). **Inconclusiva:** o resto. Uma unidade em que o braço nunca chega à metade conta com o total de consumos da vida (censura à direita), e a fração de unidades
  censuradas é reportada por braço.
- **Leitura:** a literatura sustenta que pessoas ensinam guiando, não só avaliando (Thomaz e Breazeal 2008,
  `10.1016/j.artint.2007.09.009`, VERIFICADA); isso apoia ter o braço, não a predição.

### Predição 4 — P2e piora no começo e se recupera quando o mundo refuta

- **Medida:** `taxa_fruta_ruim`, janela inicial e janela final, no descasado.
- **Contrastes primários (os dois precisam valer):** (a) **piora:** P2e − P1 na janela inicial, positivo (a informação errada leva à
  fruta ruim mais que a consequência sozinha); (b) **recupera:** P0 − P2e na janela final, positivo (no fim, o P2e come menos a fruta ruim
  que o prior).
- **Confirma:** (a) e (b) **positivos** pelo teste da seção 6.2. **Refuta a recuperação:** (a) vale e (b) tem IC 95% inteiro abaixo de 0 ou
  IC 90% inteiro dentro de (−Δ, +Δ): o pet
  segue o dono contra o mundo, e o "mundo valida ou refuta" da arquitetura **não se sustenta** com este aprendiz. **Inconclusiva:** o resto.
- **Ao lado:** o dia em que a curva do P2e cruza a do P0 (quando cruza).

### Predição 5 — P3 fica perto de P0

- **Por quê:** é o que a v1 e a validação da L1 sugerem (o feedback avaliativo deixa pouca marca; `docs/RESULTADO_V2_L1.md`), e é a
  predição mais fácil de falhar.
- **Medida:** `taxa_fruta_ruim` na janela final, no descasado (onde há o que aprender).
- **Teste:** **equivalência** de P3 − P0 com a margem Δ (dois testes unilaterais, pelo IC de 90%).
- **Confirma:** IC 90% inteiro dentro de (−Δ, +Δ). **Refuta:** IC 95% inteiro fora da margem (P3 melhor ou pior que P0 por mais que Δ).
  **Inconclusiva:** o resto.
- **Ao lado:** o G3-T do P3 (o que ele aprende da tarefa de sempre) e o "só cuidado" acoplado do P3.

### 5.1 Separação do cuidado, em toda predição com dono

Para os contrastes que envolvem P2, P2e e P3: o efeito conta como **ensino** só se (a) o braço também difere do seu "só cuidado" acoplado na
mesma direção, com IC 95% fora de zero, e (b) não há diferença de saúde média, tempo fora de privação e mortes entre o braço e o acoplado (G5).
Se só (a) vale, o resultado é reportado como **ensino misturado com cuidado**.

## 6. Estatística

### 6.1 Unidade e pareamento

- **Unidade:** a vida de um par (genoma, semente) — um pet num ambiente. A mesma unidade roda em todos os braços e condições (desenho
  pareado): o genoma e a semente fixam o ovo, o ambiente, a rng do dono e o calendário de ofertas; os braços diferem só na fonte do sinal.
- **Contraste por unidade:** a diferença entre dois braços na mesma unidade e condição. A estatística é a média dos contrastes.

### 6.2 Intervalos e testes

- IC percentil por **bootstrap sobre unidades** (`metrics.bootstrap_ic`), com as reamostragens, a semente e o nível do `PROTOCOLO_ARENA_V1`,
  como no `run_treino` e na L1. Quando houver vários genomas por semente, o bootstrap reamostra **as sementes** (a unidade de ambiente), com os
  genomas dela juntos, porque o ambiente é a fonte de variância que a v1 mostrou dominar (E1: dono × ambiente 22% da variância,
  `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json`).
- **"Positivo pelo teste"** = p unilateral na direção predita, pelo bootstrap (a proporção das médias reamostradas do lado oposto de 0),
  abaixo do limiar de Holm, com α = 0,05 na família; o teste t pareado é conferência. Os ICs de 95% e 90% servem para refutar e para a
  equivalência, como escrito em cada predição.
- **Multiplicidade:** correção de **Holm** sobre os seis contrastes primários unilaterais (predição 1; predição 2 nas duas condições;
  predição 3; predição 4 (a) e (b)). A predição 5 (equivalência) fica fora da família, com o seu IC de 90%.
- Tudo o que não está na lista acima é **descritivo**: braços secundários, outros donos, o mundo padrão, as medidas secundárias.

### 6.3 A margem Δ

- **Regra (registrada agora, aplicada na calibração):** Δ = **metade da distância** entre a `taxa_fruta_ruim` do P0 no descasado e o melhor
  valor possível (0), medida na calibração. É a mesma convenção de "metade do caminho" do G3-T e da `eficiencia_amostral`.
- O valor numérico de Δ entra no adendo da seção 7.3, antes da validação, e não muda depois.
- É uma margem de relevância, não de ruído: ela não depende da variância vista na calibração. **Decidido (E4, 2026-10-04):** esta regra, e
  não um Δ fixo escolhido sem dado.

## 7. Tamanho da amostra

### 7.1 O que a análise de poder da v1 ensinou

Da análise de poder (`docs/PLANO_ANALISE.md`, `artifacts_poder/`), no desenho A com a condição neutra:

| achado | número | artefato |
|---|---|---|
| a variância entre unidades domina | ICC 0,745; σ²_ovo 0,171 contra σ²_partida 0,058 por partida | `artifacts_poder/variancia.json`, `neutra.A` |
| repetir medidas dentro da unidade quase não ajuda | com M = 100 partidas, só 0,34% da variância do estimador vem das partidas | idem, `fracao_var_estimador_por_partidas` |
| para Δ = 0,10 com poder 0,8 foi preciso N ≈ 137 unidades | N 137 (fórmula); N 160 deu poder simulado 0,864 | `artifacts_poder/recomendacao.json`, `neutra.A` |

E a validação da L1 mostrou o mesmo de outro jeito: com 5 sementes, o acerto do braço que aprende varia muito mais que o do prior. Atencioso,
últimos 7 dias: lobos 0,663, IC95 [0,532; 0,734]; instinto 0,577, IC95 [0,559; 0,595] (`artifacts_v2_l1/validacao/ponto/tarefa.json`). **Os
braços plásticos são os mais variáveis**, e são justamente os que as predições comparam.

Três lições para cá: (1) aumentar o número de **unidades**, não o comprimento ou a repetição dentro delas; (2) **5 unidades não bastam**
para os braços que aprendem; (3) calcular N a partir da variância de um piloto, com a fórmula conferida por simulação, como foi feito na v1.

### 7.2 Regra

1. **Piloto = calibração** (seção 8), com as unidades da seção 8.1.
2. Para cada contraste primário, a variância dos contrastes por unidade (σ²_d) na calibração.
3. N por contraste = ((z₁₋α + z₀,₈) × σ_d / Δ)², unilateral, α corrigido pelo passo mais exigente de Holm (α/6), poder 0,8; conferido por
   simulação com bootstrap das unidades da calibração (como `artifacts_poder/curvas_poder.json`).
4. **N da validação = o maior N entre os contrastes primários**, arredondado para cima ao múltiplo de 5 (as 5 bases de semente).
5. Se o N passar do que a máquina roda em tempo razoável, a decisão é do Matheus antes da validação (reduzir a família, aceitar poder menor
   declarado, ou rodar mesmo assim): nunca se reduz depois de ver a validação.

### 7.3 Adendo antes da validação

Depois da calibração e antes da validação, um adendo commitado neste arquivo com: Δ (seção 6.3), σ²_d e N de cada contraste, o N escolhido,
as unidades, e qualquer ajuste de calibração do aprendiz (nenhum previsto). A validação roda **uma vez**, com esse adendo.

## 8. Sementes

- **Calibração:** 14101, 14202, 14303, 14404, 14505.
- **Validação:** 15101, 15202, 15303, 15404, 15505, **uma vez**.
- Reservadas pelo coordenador (`docs/V2_RODADA_3.md`, `docs/ROADMAP_V2.md`, seção 6); disjuntas de todas as outras faixas.

### 8.1 Unidades a partir das sementes reservadas

Cinco sementes não dão as unidades que a seção 7 pede. **Decidido (E3, 2026-10-04):** cada semente reservada é uma **base**, e as unidades são
derivadas dela, sem tocar em nenhuma outra faixa:

- semente da unidade k da base b = `protocol.derivar_semente("experimento-maior", b, k)`, para k = 0, 1, …, K − 1;
- genoma da unidade: `derivar_semente("experimento-maior-genoma", b, k)`;
- K da calibração: o suficiente para estimar σ²_d (PROPOSTO: o mesmo K em todas as bases, decidido no plano de execução da bancada, sem
  olhar resultado); K da validação: N / 5, pelo adendo.

Calibração e validação continuam disjuntas porque as bases são. A bancada exige o campo `plano` com este arquivo para sementes fora de
101…505 (`SementeSemPlano`).

### 8.2 O que se calibra

Nada do aprendiz está previsto para calibrar aqui: o ponto da L1 (passo 512, teto 1024) é o de todos os braços, e o sinal do P1 vem calibrado
do N3. A calibração serve para: conferir os contratos da seção 3 em vida real, estimar σ²_d e fixar Δ. **Nenhum resultado das predições é
lido na calibração para decidir algo além disso**; os contrastes da calibração ficam no artefato como piloto, não como resultado.

## 9. Ordem e regra de parada

1. N3, N4, N5 e a bancada de mundos na `main`, com os contratos K1–K9.
2. Calibração (14101…14505) → adendo (seção 7.3) commitado.
3. Validação (15101…15505), uma vez. Análise única, sem olhada intermediária.
4. A run é refeita do zero, com sementes novas registradas antes, só por erro de execução (replay divergente, erro de programa), nunca pelo
   resultado (a regra do `docs/PLANO_ANALISE.md`, seção 4).
5. Uma predição refutada é registrada e **não para a V2** (decisão de 2026-10-01).

**Artefatos:** `artifacts_v2_experimento_maior/{calibracao,validacao}/` (resumo, tabela braço × condição de cada medida pela
`tabela_braco_condicao`, contrastes com IC, curvas por dia, vidas); relatório `docs/RESULTADO_V2_EXPERIMENTO_MAIOR.md`.

## 10. Fora deste plano

Vício (N9), memória (N6), arbitragem (N7), canais separados × escalar (H-R2), genoma evoluindo (fase 3), a comparação de cérebros (N11), a
web, humanos. Qualquer código.

## 11. Decisões do Matheus

**Todas aprovadas como recomendadas em 2026-10-04** ("segue o recomendado"). A tabela fica como registro do que foi decidido e do
custo que cada escolha evita.

| # | decisão | escolhido | custo de errar |
|---|---|---|---|
| E1 | O casado principal é o **casado com frutas** (a fruta de maior preferência inata tem o efeito bom), com o mundo padrão como referência; a tarefa fixava o padrão | Casado com frutas como principal | Com o padrão, casado × descasado mistura "ter frutas" com "o mundo contradiz o prior", e a predição 1 mede a presença de frutas |
| E2 | Resolver o conflito F6 × N3: o sinal do P1 inclui o humor quando a mudança vem de comer fruta, **ou** o efeito ruim passa a ser nutricional | Humor no sinal do P1 só para a fruta, no experimento maior | Sem nenhum dos dois, o P1 não vê o efeito da fruta e a predição 2 falha por construção, não por resultado |
| E3 | As unidades são derivadas das 5 sementes reservadas (base × k), com N do adendo | Sim | Com 5 unidades, os braços que aprendem têm IC largo demais (a L1: [0,532; 0,734]) e quase toda predição sai inconclusiva |
| E4 | Δ = metade da distância entre o P0 e o melhor possível no descasado, medida na calibração (seção 6.3), em vez de um número fixo agora | Sim | Um Δ fixo sem dado pode ser grande demais (tudo inconclusivo) ou pequeno demais (equivalência impossível de confirmar na predição 5) |
| E5 | Vida de 14 dias, com "inconclusivo por duração" na predição 2; vida mais longa só como adendo novo | Sim | Alongar a vida depois de ver a validação é ajustar olhando a amostra |
| E6 | O controle de capacidade sem lobos entra como secundário só no P1 e no P3 | Sim | Em todos os braços dobra o custo da run sem mudar nenhuma predição; em nenhum, a comparação de cérebros (N11) perde a referência |
| E7 | Dono principal = atencioso, com o mesmo conhecimento do efeito real nos três braços com dono (K4) | Sim | Se o P3 não julgar a fruta, P2 × P3 compara canal e conhecimento juntos, e a predição 5 mede só que o P3 não sabe das frutas |
| E8 | Correção de Holm sobre os seis contrastes primários; equivalência da predição 5 fora da família | Sim | Sem correção, com seis testes, uma confirmação por acaso fica provável; com Bonferroni, o poder cai à toa |

## Adendo 1 (2026-10-05, antes de qualquer dado): calibração conjunta e ablações

Decisão do Matheus (`docs/ROADMAP_V2.md`, revisão 3, M10): o cérebro A é montado inteiro (N5, N6, N7 e canais, cada um atrás de
chave) e calibrado **uma vez**, nas sementes 14101…14505; a validação é **uma só**, nas 15101…15505. Efeitos neste plano:

- As predições 1–5 e a estatística (seção 6) não mudam.
- **Ablações:** além dos braços P0–P3, cada peça entra como contraste "sistema completo × sistema sem a peça" (N5, N6, N7, canais),
  com a medida da peça no plano dela (`PLANO_ANALISE_V2_N5.md`, `_N6.md`, `_N7.md`). Esses contrastes são **secundários** e ficam
  **fora** da família de Holm das predições primárias (E8).
- As faixas próprias do N5 (12101…13505), do N6 (19101…20505) e do N7 (21101…22505) não são usadas.
- O plano da calibração conjunta (quais parâmetros, em que grade, com que regra de escolha, e o N do adendo de tamanho de amostra)
  é a tarefa K1 (`docs/TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA.md`) e entra antes de qualquer run.

## Adendo 2 (2026-10-06, antes da validação): o N e o Δ do P3 na escala da medida (opção A)

Decisão do Matheus (2026-10-06), sobre o resultado da calibração conjunta (`docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md`, PR #181).

**O problema.** A seção 5.3 do `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` aplicava a todos os primários o Δ da regra 6.3, que está em
**taxa**: 0,199 (`artifacts_v2_calibracao_conjunta/adendo.json`). Mas o contraste `p3_consumos` se mede em **consumos**. Com esse Δ, o N
saía 191.815 unidades, cerca de 28.760 h. O erro é de escala do plano, não de variância.

**O que muda (opção A).** Os números vêm de `artifacts_v2_calibracao_conjunta/adendo_opcao_a.json` e foram calculados das 20 unidades da
calibração.

- **O Δ de cada primário fica na escala da sua medida.** O do P3 passa a ser 17,5 consumos, pela mesma convenção de "metade": metade dos
  consumos do P1 no descasado (35,0). Os outros cinco primários ficam com o Δ 0,199 de antes.
- **O N vem da simulação de poder, não da fórmula.** É o maior N simulado que dá poder ≥ 0,8 entre os seis primários. Na calibração, a
  fórmula normal era otimista no piso de 5 unidades, onde o poder simulado de três primários ficou entre 0,73 e 0,77.
- **N = 30 unidades** (K = 6 por base, nas bases 15101…15505), cerca de 4,5 h. Fica abaixo do teto de 12 h (K-10).

**Poder simulado com N = 30:**
- **primários:** p1_casado, p2_descasado, p2_mutavel, p4a_piora e p4b_recupera com 1,0; p3_consumos com 0,862;
- **secundários com pouco poder** (abaixo de 0,5, lidos como subpotenciados, pela seção 5.3): G-MARCA (0,34) e G-MARCA-E (0,38), do N7;
- os demais secundários (N6, G-EROSAO e as ablações) ficam com poder 1,0.

**Fica igual:**
- as predições 1 a 5;
- os seis contrastes primários e o Holm;
- a equivalência da predição 5;
- a regra de decisão;
- o ponto do cérebro A: `g` S/2, `w0_pedido` S/4, ganho 4 e `w0_info` S/4 (`artifacts_v2_calibracao_conjunta/escolha.json`).

**Registrado ao lado, sem mudar regra:**
- **`w0_pedido`** não fechou na calibração (nenhum conflito na `fome_moderada`) e ficou pela reserva. O bloco N7 pode sair pouco testado.
- **O ganho do P1** também não fechou: todo ponto teve vida no teto, e a razão da deriva foi 2,72. O aprendizado ainda não assentou aos
  14 dias, o que reforça o risco "inconclusivo por duração" da predição 2.

**O que fica em aberto antes da run.** Os adendos de literatura (`docs/PREDICOES_V2.md`, em preparação) podem acrescentar a medida em
pelo menos três durações de vida. A validação **não roda** até eles serem registrados ou dispensados pelo Matheus.

## Adendo 3 (2026-10-06, antes da validação): o que a literatura muda no desenho

Fonte: `docs/PREDICOES_V2.md`, que se apoia na síntese `docs/referencias/E_SINTESE_VALOR_APRENDIZADO.md`. O Matheus aprovou as decisões
P-1 a P-7 em 2026-10-06. **Nada aqui muda as predições 1 a 5, os seis contrastes primários, o Holm, o N nem o Δ** (adendo 2).

**Apoio teórico das predições** (só para a leitura):

| predição | apoio |
|---|---|
| 1 | APOIADA |
| 2 | APOIADA COM RESSALVA (a relação com a duração da vida não é monotônica) |
| 3 | APOIADA (pela informação filtrada, não pela economia de tentativas) |
| 4 | SEM APOIO DIRETO |
| 5 | CONTESTADA (Ho et al. 2017, `10.1016/j.cognition.2017.03.006`): mantida como registrada (P-5) |

**3.1 Bloco de durações (adendo (a), P-1, P-2).** É secundário e descritivo, fora da família de Holm.
- **Braços:** P0 e P1. **Mundos:** descasado e mutável. **Unidades:** as da validação.
- **Durações:**
  - a principal, de 14 dias, sem mudança;
  - mais duas: **7 dias** e a maior entre **28 e 21 dias** que couber, junto com o resto da validação, no teto de 12 h (K-10).
- **O custo** é calculado pelo worker B a partir do tempo por vida da calibração conjunta, antes da run. Se nem 21 dias couber, o
  Matheus decide.
- **Leitura:** a forma da curva por braço e mundo (crescente, platô ou ótimo interior), com IC por bootstrap das unidades.
- **No mutável,** a troca acompanha a duração (`Bancada.tick_troca` = fim do dia `dias // 2`). Essa confusão vai declarada.

**3.2 O mutável sem precedente teórico direto (adendo (b), P-3).** Os modelos disponíveis tratam mudança entre gerações, não dentro da
vida (Kozielska e Weissing 2024, `10.1371/journal.pcbi.1011840`). No mutável, o resultado é descrição do que este motor faz. O teste não
muda; a limitação vai no relatório.

**3.3 Os braços P2d e P3i (P-4, P-6).** Secundários, fora da família de Holm, no descasado e no mutável, nas mesmas unidades da validação.
A validação espera esses braços.
- **P2d:** o P2 com a informação dada **depois** do consumo, no primeiro passo do dono, e só sobre a fruta consumida.
  - **Contraste** P2 × P2d: o **momento**.
- **P3i:** o P3 com o julgamento da fruta como **informação**: o evento `informar_fruta_*` na percepção, com o `w0_info` do ponto da K2,
  no lugar de elogio e bronca.
  - **Contraste** P3 × P3i: a **interpretação**.
  - No P3i o `w_info` não aprende, porque só a consequência o ajusta. Fica declarado.
- **Declarado:**
  - P2d × P3i não entra em contraste nenhum (difere na fonte do aprendizado);
  - o número e o multiconjunto das informações vão reportados por braço.
- **Contrastes secundários** (IC 95% por bootstrap das unidades, sem Holm):
  - P2 − P2d e P3 − P3i na `taxa_fruta_ruim` final, no descasado e no mutável;
  - os consumos até a metade, no descasado.

**3.4 Literatura (P-7).** A próxima passada (as pistas de prioridade 1 da síntese) é feita antes da **leitura** dos resultados, não antes
da run. Ela não muda o desenho.

## Adendo 4 (2026-10-06, antes da validação): faixa de validação nova e leitura da literatura P-7

**4.1 Faixa de validação nova: 30101…30505** (bases 30101, 30202, 30303, 30404, 30505). Substitui a 15101…15505.
- **Por quê:** antes da tarefa da validação chegar, uma run foi disparada nas sementes 15101…15505 (2026-10-06, das 09:47 às 10:12;
  relato no PR #183 e no #189). Ela foi parada, nada foi lido além da contagem de arquivos, e tudo foi apagado.
- **Decisão do Matheus:** trocar a faixa. Não há indício de leitura, mas a troca não custa tempo de máquina e tira a dúvida.
- **A faixa 15101…15505 fica queimada:** continua reservada e não pode ser usada para nada.
- **O que não muda:** as unidades derivadas (`derivar_semente("experimento-maior", b, k)`, K = 6), o N, o Δ e o resto.
- **Faixa livre:** conferido em 2026-10-06 que nenhuma referência a ela existe no repositório.

**4.2 Leitura, pela segunda passada de literatura** (`docs/referencias/E2_SINTESE_PISTAS_P7.md`, decisões L-1 a L-4, aprovadas). Nada
aqui muda teste nem regra de decisão.
- **L-3:** na leitura do bloco de durações, o **limiar** entra como forma possível da curva, ao lado de crescente, platô e ótimo interior.
  A regra registrada pelo worker B não muda.
- **L-4:** a trajetória do `w_info` do P2e vai reportada como descritivo, ao lado do dia em que o P2e cruza o P0.
- **Predição 2:** o relatório diz que componente da mudança cada condição manipula. No mutável, valor (P0 − P1) e eficiência são lidos
  separados.
- **L-1:** antes da leitura dos resultados, buscar o texto completo do Eliassen et al. 2009 (`10.1086/605370`). Isso não segura a run.
