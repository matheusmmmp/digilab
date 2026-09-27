# Tarefa — análise de poder da hipótese central

Leia o `CLAUDE.md`, `docs/REGISTRO_DESVIOS.md` e os artefatos de
`artifacts/`, `artifacts_ablacao/`, `artifacts_treino/` e
`artifacts_combate_v21c/` antes de começar. Todas as regras do
`CLAUDE.md` valem.

## Por que esta tarefa existe

O resultado central oscila mais do que o efeito que queremos medir:

- run canônica: 0,72 [0,64; 0,82];
- mesmos pets, só trocando o sorteio das partidas: 0,61;
- personalidade completa: 0,615 [0,45; 0,77].

Enquanto isso não for resolvido, qualquer mecânica nova vai sair
inconclusiva, seja boa ou ruim. Esta tarefa decide **quantos ovos e
quantas partidas** são necessários para testar a hipótese, e **congela o
plano** antes da run confirmatória.

Esta tarefa **não muda o jogo**: não há nada a portar para a web.

## Fora de escopo

- Mudanças de regra de combate, treino, personalidade ou campanha.
- A run confirmatória em si (é a próxima tarefa, depois de o Matheus
  aprovar o plano).
- Redesenho do vínculo (tarefa própria).

---

## Etapa 0 — configuração fixa da pesquisa

Declarar num config próprio (`experiments/configs/poder_*.json`):

- Combate **V21C** com stats normalizados.
- Política: bandit com personalidade completa (a configuração em que o
  central ficou 0,615).
- **Condição física neutra na arena** (nova chave de configuração, padrão
  desligado, para não alterar runs antigas). Motivo: o G6b ficou como
  exceção (0,725), então a condição ainda decide espelhos, e os pets da
  pesquisa divergem pouco.
- **Teste de ordem da normalização:** um teste que prova que os pontos de
  treino são multiplicados por `peso_ponto_combate` **antes** de o total
  voltar ao orçamento da espécie. Se estiver ao contrário, pare e reporte.

## Etapa 1 — piloto

Sementes de **piloto**, disjuntas de todas as sementes já usadas e das
que serão usadas na confirmatória. Registrar as três listas no config.

- Braços: atencioso e aleatório (comparação principal) + os outros três
  (secundários).
- **Ovos pareados:** cada ovo gera um pet em cada braço.
- N₀ = 20 ovos; M₀ = 100 partidas por par, com lados trocados na metade.
- Rodar **duas vezes**: condição física neutra e condição real. A
  diferença mede quanto do resultado vem do cuidado.
- Usar `--processos 8` (com 20 houve erros instáveis na máquina).

## Etapa 2 — componentes de variância

A partir do piloto, para a comparação principal:

- **σ²_partida:** variância da taxa de vitória de um mesmo par devida só
  às partidas. Estimar reamostrando sementes de partida com os pets
  fixos (repetir o teste que derrubou 0,72 → 0,61).
- **σ²_ovo:** variância entre ovos da taxa média do par.
- ICC = σ²_ovo / (σ²_ovo + σ²_partida).

Variância do estimador com N ovos e M partidas por par:

`Var ≈ σ²_ovo / N + σ²_partida_1 / (N · M)`

(σ²_partida_1 = variância de uma partida isolada.) Conferir a fórmula
contra o bootstrap do piloto; se divergir, usar o bootstrap.

## Etapa 3 — dois desenhos de medida

Comparar o poder de dois estimadores com os mesmos dados do piloto:

- **A — confronto direto:** atencioso × aleatório do mesmo ovo (como
  hoje).
- **B — painel fixo:** cada pet enfrenta o mesmo painel de bots de
  referência da bateria V21C (todos os estilos, mesmas sementes); o
  efeito é a diferença pareada, por ovo, da taxa média contra o painel.

O B tende a ter menos variância e é mais fácil de interpretar ("o pet
ficou melhor contra o mundo", não só contra o outro braço). Reportar os
dois; a escolha do principal é do Matheus.

## Etapa 4 — curvas de poder

- Efeito mínimo de interesse: **Δ = 0,10** (taxa 0,60 no desenho A;
  diferença pareada de 0,10 no B). Reportar também para Δ = 0,05 e 0,15.
- Para cada desenho, poder para N ∈ {10, 20, 40, 80, 160} e
  M ∈ {50, 100, 200, 400}, com α = 0,05 bilateral.
- Calcular por fórmula **e** por simulação paramétrica a partir dos
  componentes do piloto (≥ 2000 réplicas por célula, semente fixa).
- **Custo:** tempo de execução estimado de cada célula, a partir do tempo
  medido no piloto com 8 processos.
- Recomendar a célula mais barata com poder ≥ 0,8 para Δ = 0,10.

## Etapa 5 — plano congelado

Escrever `docs/PLANO_ANALISE.md`, **antes** de qualquer run
confirmatória:

- desenho principal (A ou B, decisão do Matheus; deixar marcado como
  PENDENTE DE DECISÃO até ele escolher);
- hipótese principal: atencioso × aleatório; as outras comparações são
  secundárias, com correção de Holm;
- N, M, sementes confirmatórias, teste estatístico e IC (bootstrap sobre
  ovos);
- regra de parada: nenhuma olhada intermediária no resultado principal;
- o que conta como "hipótese sustentada", "refutada" e "inconclusiva".

Registrar em `docs/REGISTRO_DESVIOS.md` qualquer decisão que desvie
deste texto.

## Testes

- Sementes de piloto, confirmatórias e antigas são disjuntas (teste).
- Condição neutra desligada por padrão reproduz as runs antigas byte a
  byte.
- Ordem da normalização (Etapa 0).
- Reprodutibilidade do piloto: mesma semente, mesmos números.

## Artefatos

`artifacts_poder/`: piloto (neutra e real), componentes de variância,
curvas de poder dos dois desenhos, tempos, `recomendacao.json`.

## O que reportar

Sem rodeios, nesta ordem:

1. **N e M necessários para Δ = 0,10 com poder 0,8, em cada desenho, e
   quanto tempo a confirmatória levaria.** Se nenhum desenho for viável
   em até ~24 h de máquina, diga primeiro e proponha o que mudar.
2. σ²_ovo, σ²_partida e ICC. Qual dos dois domina: faltam ovos ou faltam
   partidas?
3. **Condição neutra × real:** quanto do efeito central some quando a
   condição física é neutralizada. Se quase todo o efeito sumir, a arena
   estava medindo cuidado: diga com destaque.
4. Efeito observado no piloto (só como estimativa para o cálculo, não
   como resultado).
5. O rascunho do `PLANO_ANALISE.md`.

Nenhum número sem o artefato que o gerou.
