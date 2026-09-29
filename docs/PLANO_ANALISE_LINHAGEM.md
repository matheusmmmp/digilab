# Plano de análise da linhagem — E1: natureza × criação

Status: **registrado antes da run** (2026-09-29). O Matheus autorizou como exceção de escopo **só o E1** de `docs/PLANO_LINHAGEM_ALIFE.md` (conflito 2.1). Nenhuma mecânica nova: nada de genoma, linhagem, procriação, aposentadoria, Baldwin ou estágio 5. Valores sem fonte estão marcados PROPOSTO.

**Natureza.** É o **gate do programa da linhagem**, não uma confirmatória da hipótese central (essa foi refutada em `PLANO_ANALISE.md`). A pergunta: o que vem no ovo explica parte do desempenho do pet, separado do dono e da sorte da vida? Se não explicar, a seleção entre gerações não tem sobre o que agir, e o E2 e o E3 não seguem com este genoma.

## 1. O que é genoma e o que é ambiente

Até hoje uma semente só (`s`) fazia as duas coisas, e o "efeito do ovo" misturava genética com sorte (conflito 2.4). Aqui elas se separam, **sem mexer no `engine.py`**:

| parte | vem de | o que inclui |
|---|---|---|
| **genoma** | a semente do genoma `g` | a espécie e o temperamento do ovo (os 4 eixos do catálogo, que mexem nos stats), de `evolucao.ovo(g)`; o temperamento do motor (4 eixos, que mexem no aprendizado), de `temperamento.sortear(g)` |
| **ambiente** | a semente do ambiente `r` | tudo o mais: o `engine.Motor` (ambiente e rng da política), o dono, as travessuras, a obediência, as lesões e as sementes do sparring |

- Na rodada de **espécie fixa**, a espécie de `ovo(g)` é trocada pela fixa. Os temperamentos continuam os de `g`.
- Com `g = r`, a vida é **exatamente** a da V3. Um teste prova isso: mesmo log byte a byte e mesmo resumo.

## 2. Desenho

| item | valor | status |
|---|---|---|
| vida | a da V3: `simular_vida_educacao`, 14 dias, duração teste, educação e lesões ligadas, 10 sparrings, orçamento igual | igual à V3 |
| donos (D = 4) | atencioso, aleatório, permissivo, relapso | PROPOSTO (os da seção 5 do plano da linhagem) |
| genomas (G = 40) | sementes **81001–81040** | PROPOSTO, sem cálculo de poder |
| ambientes (R = 4) | sementes **82001–82004** | PROPOSTO, sem cálculo de poder |
| células | G × D × R = 640 vidas por rodada, uma por célula, cruzamento completo | — |
| rodada 1, **espécie fixa** (principal) | brasa, a primeira de `CONFIG_CATALOGO.especies_ativas`, escolhida sem olhar dado | PROPOSTO |
| rodada 2, **espécies balanceadas** (descritiva) | os mesmos 40 genomas; a espécie do genoma de índice i (0 a 39) é `especies_ativas[i % 4]`, 10 por espécie | PROPOSTO |
| piloto | genomas 80001–80004 × ambientes 80101–80102 × os 4 donos = 32 vidas | só confere o pipeline e o tempo; os números não entram em nada |

As faixas de sementes não colidem com nenhuma config existente (conferido em `experiments/configs/`).

**Pet final** (como na V3):
- morto: não luta e conta 0 em todas as partidas;
- qualificado: forma adulta (ou sombria);
- senão: adolescente.

**Painel B** (como na V3):
- 8 formas adultas × 4 espécies;
- 50 partidas por bot, metade de cada lado;
- **condição neutra** (`ConfigArenaPesquisa.condicao_neutra`);
- sementes das partidas `derivar_semente("linhagem-e1|B|<g>:<r>", bot, k)`: dependem da célula (genoma, ambiente), do bot e de k, e são iguais entre os donos da célula (números aleatórios comuns).

**Resposta** Y(g, d, r) = a taxa média do pet contra o painel.

## 3. Análise

**Modelo.** ANOVA de 3 fatores cruzados, uma observação por célula, componentes pelo método dos momentos com as esperanças dos quadrados médios do modelo **aleatório sem restrição**. Com a = G, b = D e c = R:

    σ²_G  = (QM_G − QM_GD − QM_GR + QM_e) / (b·c)
    σ²_D  = (QM_D − QM_GD − QM_DR + QM_e) / (a·c)
    σ²_R  = (QM_R − QM_GR − QM_DR + QM_e) / (a·b)
    σ²_GD = (QM_GD − QM_e) / c      σ²_GR = (QM_GR − QM_e) / b      σ²_DR = (QM_DR − QM_e) / a
    σ²_e  = QM_e   (inclui a interação tripla)

- O dono é um fator fixo. O modelo sem restrição desconta o QM_GD de σ²_G, o que é o lado conservador.
- Os estimadores podem sair negativos. O gate usa o estimador **sem truncar**; as frações descritivas truncam em 0.
- A função entra no `digilab/metrics.py`: `decomposicao_cruzada`, que estende a `decomposicao_ovo_braco`.

**Incerteza** (bootstrap sobre ovos):
- **Principal:** o bootstrap "pigeonhole" (McCullagh, 2000), próprio para fatores cruzados. Os genomas e os ambientes são reamostrados com reposição, de forma independente (um genoma repetido conta como um nível novo), e os 4 donos ficam fixos.
- 10 000 reamostras, semente 20260930, IC95 percentil.
- **Secundário:** reamostrar só os genomas.

## 4. Gate (rodada 1, espécie fixa)

| resultado | condição | o que quer dizer |
|---|---|---|
| **PASSOU** | o limite inferior do IC95 principal de σ²_G é > 0 | há variação herdável de desempenho, e o E2 (herdabilidade pai-filho) faz sentido |
| **FALHOU** | o IC95 inclui 0, ou fica todo ≤ 0 | com este genoma (temperamentos) e esta vida, o ovo não explica o desempenho separado do dono e do ambiente. O E2 e o E3 não seguem sem mudar o genoma (por exemplo, com as aptidões por indivíduo), e isso volta para decisão |

O gate não tem "quase passou". Um resultado perto da fronteira é relatado como está.

## 5. Relatório (descritivo, sem gate)

- Os componentes e as frações da variância nas duas rodadas.
- **σ²_GD:** a interação natureza × criação, ou seja, se o melhor genoma depende do dono.
- As médias por dono e as diferenças atencioso − aleatório e atencioso − permissivo, com bootstrap pigeonhole, para comparar com a V3.
- **Rodada 2:** quanto da variância entre genomas vem da espécie (a soma de quadrados entre espécies sobre as médias dos genomas).
- As mortes, as qualificações e as formas, por dono e por rodada.

## 6. Saída

- **Onde:** `artifacts_linhagem/natureza_criacao/<rodada>/`, com as rodadas `piloto`, `especie_fixa` e `especies_balanceadas`. Cada uma tem `resultado.json`, `pets.json`, `meta.json` (a config, as sementes, o sha256 das fontes, os tempos e o ambiente), as partidas e as vidas.
- **O que vai para o git:** o `resultado.json`, o `pets.json` e o `meta.json`. As vidas e as partidas ficam fora, como na V3.
- **Script:** `experiments/run_natureza_criacao.py`. **Config:** `experiments/configs/linhagem/natureza_criacao.json`.
- **Desvios:** um desvio deste plano depois do registro vai para o `docs/REGISTRO_DESVIOS.md`, com o motivo.
