# Plano de análise da run confirmatória (congelado antes da run)

Hipótese central do Digilab: treino por um dono coerente produz um pet melhor que feedback aleatório com o
mesmo volume de interação. Este plano vale para a próxima run (a confirmatória), que só roda depois de o
Matheus aprovar este texto. Números de apoio: `artifacts_poder/` (TAREFA_ANALISE_PODER).

## 1. Desenho principal — PENDENTE DE DECISÃO

| | A — confronto direto | B — painel fixo |
|---|---|---|
| medida por ovo | taxa do atencioso contra o aleatório do mesmo ovo | diferença (atencioso − aleatório) da taxa média contra o painel |
| hipótese nula | taxa = 0,50 | diferença = 0 |
| Δ mínimo de interesse | 0,10 (taxa 0,60) | 0,10 de diferença |
| partidas por ovo | M = 100 (par principal) | 50 por bot × 32 bots × 2 pets |
| poder em N = 160, Δ = 0,10 | 0,86 (neutra), 0,88 (real) | 1,00 |
| poder em N = 160, Δ = 0,05 | 0,33 | 0,82 (neutra), 0,78 (real) |
| tempo da run completa (5 braços) | ~15 min | ~17 min |

Painel B: as 8 formas adultas canônicas × 4 espécies da bateria V21C, as mesmas sementes para todos os
pets do ovo. Os dois Δ = 0,10 não são a mesma coisa: A mede "ganha do outro braço", B mede "ficou melhor
contra o mundo". **A escolha é do Matheus**; enquanto não houver, a run confirmatória não roda.

## 2. Configuração fixa

- Pets: pipeline do `run_treino` (personalidade completa + treino, 14 dias, orçamento 298 por vida,
  evolução até adulto), ovos pareados (cada ovo gera um pet em cada braço).
- Arena: combate V21C com stats normalizados (`experiments/configs/poder_pesquisa.json`), treino valendo
  `peso_ponto_combate` = 3 antes da normalização.
- **Condição física** — PROPOSTO (confirmar com o Matheus): principal com a condição **neutra**
  (`condicao_neutra = true`), para medir o que o pet aprendeu e não o cuidado da última hora; a condição
  real roda junto e é reportada como secundária. No piloto, neutralizar a condição tirou cerca de metade do
  efeito do desenho A (0,142 → 0,075).
- Sementes confirmatórias: 60001–60160 (N = 160), rótulo de partida `poder-confirmatoria`; disjuntas do
  piloto e das runs antigas (teste `tests/test_poder.py`).
- N = 160 e M como na tabela, nos dois desenhos (o custo é pequeno; N acima do mínimo de 137/44 dá folga
  para Δ um pouco menor). O componente de partida responde por menos de 1% da variância do estimador:
  aumentar M não ajuda, aumentar N ajuda.

## 3. Estatística

- Estimador: média sobre os N ovos da medida por ovo.
- IC 95%: bootstrap percentil sobre ovos, 10000 reamostragens, semente fixa (20260927).
- Teste principal: bilateral, α = 0,05; p-valor pelo bootstrap (proporção das médias reamostradas do lado
  oposto da nula, × 2), com o teste t de uma amostra como conferência.
- Comparações secundárias (correção de Holm, α = 0,05 no conjunto): relapso × aleatório, incoerente ×
  aleatório, exigente × aleatório e exigente × atencioso (forçar compensa?), no desenho escolhido; a
  condição real é descritiva.

## 4. Regra de parada

- Uma única análise, com todos os N ovos. Nenhuma olhada intermediária no resultado principal (nem parcial,
  nem por ovo) antes de a run terminar.
- A run é rejeitada e refeita do zero (com sementes novas, registradas antes) só por erro de execução
  (replay divergente, erro de programa), nunca pelo resultado.

## 5. Como ler o resultado

Sobre o IC 95% do efeito principal (A: taxa − 0,50; B: diferença):

- **Hipótese sustentada:** o IC inteiro acima de 0 **e** a estimativa ≥ Δ/2 (0,05).
- **Hipótese refutada:** o IC inteiro dentro de (−0,10, +0,10) (equivalência com a margem Δ) **ou** o IC
  inteiro abaixo de 0 (o aleatório melhor).
- **Inconclusiva:** qualquer outro caso. Com o poder planejado, isso só deve acontecer se o efeito real for
  menor que Δ.

## 6. O que o piloto já mostrou (só estimativa para o cálculo, não resultado)

Piloto: 20 ovos (50001–50020), 100 partidas por par. Desenho A: taxa 0,575 (neutra) e 0,642 (real);
desenho B: diferença −0,024 (neutra) e +0,027 (real). σ²_ovo domina (ICC 0,74 no A, 0,28–0,30 no B).
