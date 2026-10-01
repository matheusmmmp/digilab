---
name: literatura-digilab
description: "Fonte canônica de verdade sobre a literatura do Digilab (pet virtual evolutivo com bandit, temperamento inato, caráter aprendido e linhagem por procriação) — quais referências estão verificadas, o que cada uma sustenta de fato, quais alegações de novidade do projeto já foram publicadas por terceiros, e quais mecânicas de jogo só têm fonte de fã. Consulte SEMPRE que a tarefa mencionar literatura, referência, citação, DOI, bibliografia, estado da arte, trabalho relacionado, novidade, originalidade, contribuição, trilha de pesquisa, Artificial Life, ALife, efeito Baldwin, herdabilidade, evolução interativa, quality diversity, personalidade animal, efeito IKEA, legibilidade ou explicabilidade — e obrigatoriamente antes de escrever qualquer trecho que afirme que algo do Digilab é inédito."
---

# Literatura verificada do Digilab

Revisão de 2026-09-29, 79 referências. Este documento é a fonte de verdade sobre **o que a
literatura sustenta**; ele não descreve o estado do código nem das runs (isso está em
`docs/CONTEXTO_DIGILAB_*.md` e no `CLAUDE.md` do repositório).

## Onde estão os arquivos

- `docs/referencias/revisao_alife_linhagem.md` — revisão por trilha, análise da lacuna,
  afirmações sem suporte, nota de método e limites.
- `docs/referencias/referencias_verificadas.csv` — a tabela. Colunas: `referencia`,
  `tipo` (par/cinza), `verificada`, `o_que_sustenta`, `trilha`, `relevancia`, `doi_ou_id`.
- `docs/referencias/verificacao_crossref.json` — registro bruto por DOI, para auditoria.
- `referencias.bib` nesta skill — 72 entradas (70 da revisão + 2 conferidas depois), com `note` marcando os itens sem DOI e a cinza.

Ao citar, leia a linha da tabela antes: a coluna `o_que_sustenta` diz exatamente o que aquela fonte
autoriza afirmar.

## Referências conferidas depois da revisão

Duas entradas foram conferidas no Crossref em 2026-09-30 (status 200, autores, ano e veículo
conferidos, sem campo `update-to`) e **não constam** das 79 linhas de
`docs/referencias/referencias_verificadas.csv`. Estão no `referencias.bib` desta skill e podem ser
citadas como VERIFICADA, com a ressalva de que a conferência de conteúdo foi sobre metadados e
resumo, não texto completo:

- Lehman, J., Clune, J., Misevic, D. et al. (2020). The surprising creativity of digital evolution:
  a collection of anecdotes. *Artificial Life*. `10.1162/artl_a_00319` — precedente de gênero para
  relato honesto do que o sistema fez em vez do resultado desejado, e evidência de que a revista
  *Artificial Life* publica esse gênero.
- Pigliucci, M., Murren, C. J. e Schlichting, C. D. (2006). Phenotypic plasticity and evolution by
  genetic assimilation. *Journal of Experimental Biology*. `10.1242/jeb.02070` — entrada correta
  para canalização e assimilação genética, se a manipulação do mapa genótipo→fenótipo avançar.

## Vocabulário de status (idêntico ao do projeto)

- **VERIFICADA** — DOI resolve no Crossref (ou API do arXiv, para `10.48550/*`), metadados conferidos,
  e título/resumo sustentam a afirmação atribuída.
- **VERIFICADA (sem DOI)** — registro bibliográfico independente confirmado, sem DOI.
- **NÃO LOCALIZADA** — não foi possível confirmar o registro. Não citar.
- **NÃO VERIFICADA EM FONTE PRIMÁRIA** — só fonte de fã/enciclopédica. Pista, nunca evidência.

Verificação de conteúdo foi feita sobre metadados e resumos, **não** sobre texto completo. Para uso
em texto de dissertação ou artigo, ler o artigo.

## Regras duras

1. **Nunca afirmar que o Digilab é o primeiro a separar comportamento instintivo de aprendido.**
   Hallawa et al., Evo-RL, GECCO'21 Companion, `10.1145/3449726.3459475` já faz essa partição dentro
   de um mesmo agente e deixa a fronteira ser decidida pela evolução.
2. **Nunca afirmar que herdar o prior de aprendizado sem herdar o aprendido é desenho novo.** É o
   efeito Baldwin computacional (Hinton e Nowlan 1987, sem DOI; Whitley et al. 1994,
   `10.1007/3-540-58484-6_245`) e o resultado de Fernando et al. 2018, `10.1145/3205651.3205763`.
3. **Nunca afirmar que "comportamento ensinado, não roteirizado" é diferencial.** O postmortem de
   Black & White (Molyneux, Gamasutra, jun/2001) já afirma que a personalidade da criatura se forma no
   uso, sem elementos aleatórios. O que resta defensável é o teste falsificável com braço de controle.
4. **Nunca citar Monster Rancher, Digimon World Championship ou Pokémon como evidência de precedência
   ou de desenho.** As três estão NÃO VERIFICADAS EM FONTE PRIMÁRIA: só verbetes enciclopédicos,
   guias e fóruns de fã, e os relatos divergem sobre o efeito da reversão a ovo nos stats.
5. **Nunca citar Evans, "A semi-formal design review of the AI in Black and White" (gameai.com).**
   NÃO LOCALIZADA.
6. **Ackley e Littman (1991), Artificial Life II** não foi localizada. Substituto verificado com
   escopo semelhante: Arita e Suzuki (2000), `10.7551/mitpress/1432.003.0027`.
7. **Ao citar Tierra**, usar Ray (1993), `10.1162/artl.1993.1.1_2.179` — o capítulo de 1991 em
   Artificial Life II não tem DOI.
8. **Lacuna de fonte aberta:** Evans, "Varieties of Learning", em Rabin (ed.), AI Game Programming
   Wisdom, 2002, pp. 567-578. Existência e paginação confirmadas em três listas de referências
   revisadas por pares; texto não consultado. É a fonte técnica de primeira mão sobre o aprendizado
   em Black & White e a lacuna mais relevante da revisão.

## A lacuna central (o que de fato não existe)

Não foi localizado nenhum trabalho que **separe o efeito da criação pelo usuário do efeito da seleção
pelo usuário** em agentes artificiais. A razão é estrutural: as duas literaturas são disjuntas.

- Computação evolutiva interativa — Takagi `10.1109/5.949485`, Picbreeder `10.1162/EVCO_a_00030`,
  Galactic Arms Race `10.1109/TCIAIG.2009.2038365`, biomorphs `10.1142/9789812832061_0004` — tem o
  humano **apenas como operador de seleção**. Não há treino dentro da vida do indivíduo.
- Aprendizado interativo por feedback humano — TAMER `10.1145/1597735.1597738`, MacGlashan et al.
  `arXiv:1701.06049`, Thomaz e Breazeal `10.1016/j.artint.2007.09.009`, Christiano et al.
  `arXiv:1706.03741` — tem o humano **apenas como treinador**. Não há reprodução nem linhagem.
- Creatures (Grand e Cliff `10.1023/A:1010042522104`; Cliff e Grand `10.1162/106454699568683`) é o
  único sistema em que as duas coisas aconteceram juntas e em escala, e o registro é **descritivo**,
  não um desenho fatorial.

Ressalva obrigatória ao usar isso: é resultado negativo de busca lexical (106 consultas no OpenAlex,
mais arXiv). Ausência de resultado em busca por palavras-chave é evidência fraca.

## Números da literatura que servem de calibração

- **~52%** da variação de personalidade animal é atribuível a variação genética aditiva —
  Dochtermann, Schwab e Sih (2015), `10.1098/rspb.2014.2201`, meta-análise.
- **9%** apenas da variação comportamental individual em cães é explicada pela raça, apesar de
  h² > 25% na maioria dos traços — Morrill et al. (2022), `10.1126/science.abk0639`, 18.385 cães por
  questionário e 2.155 genotipados.
- Formalismo para separar temperamento de resposta ao treino: normas de reação (intercepto = nível do
  indivíduo, inclinação = plasticidade) — Dingemanse et al. (2010), `10.1016/j.tree.2009.07.013`.

Esses três são a referência externa para interpretar o gate de σ²_genoma do E1.

## Restrições de desenho que a literatura impõe

- **O contraste "dono coerente × aleatório" está mal escolhido como único contraste.** Thomaz e
  Breazeal (`10.1016/j.artint.2007.09.009`) documentam que pessoas reais dão recompensa
  antecipatória, tentam guiar em vez de avaliar, e são inconsistentes — o dono humano típico não é
  nenhum dos dois braços.
- **O feedback humano depende da política atual do agente** (é mais parecido com advantage que com
  recompensa fixa) — MacGlashan et al., `arXiv:1701.06049`. Isso muda qual algoritmo é o correto.
- **Fadiga do avaliador** é o gargalo de qualquer linhagem que dependa de escolha explícita do
  jogador — Takagi, `10.1109/5.949485`. Alternativa: extrair seleção do comportamento de uso
  (Galactic Arms Race).
- **Traços vêm em síndromes correlacionadas**, não independentes — Sih, Bell e Johnson,
  `10.1016/j.tree.2004.04.009`. Sortear traços do ovo independentemente contradiz isso.
- **O efeito IKEA depende de a tarefa ser concluída com sucesso** — Marsh, Kanngiesser e Hood,
  `10.1016/j.cognition.2017.10.012`. Um pet mal treinado pode valer menos, não mais.
- **Legibilidade tem de ser medida, não assumida** — Anderson et al., `10.24963/ijcai.2019/184`, mede
  compreensão de leigos; Madumal et al., `10.1609/aaai.v34i03.5631`, mostra ganho de ancorar a
  explicação num modelo causal.

## Afirmações do projeto sem suporte na literatura

Oito, detalhadas na seção "Afirmações sem suporte" do `revisao_alife_linhagem.md`. As de maior custo:
novidade de "ensinado, não roteirizado" (regra 3); novidade de herdar o prior (regra 2); apego entre
gerações de pet virtual (zero evidência revisada por pares localizada); "Artificial Life como lente
teórica acrescentando poder explicativo" (Bedau `10.1016/j.tics.2003.09.012` sustenta o vocabulário,
nada sustenta o ganho explicativo).

## O que esta revisão NÃO cobre

Não substitui a seção 9 do `CONTEXTO_DIGILAB`. Ficaram fora: iPET (ACL 2025), *Designing Virtual
Animal Companions*, *From Pixels to Partners* (2024), e os produtos vivos (AI Arena, Moflin, Sweekar,
Peridot, AI Tamago, Animal-AI Environment). Também ficou fora a trilha de avaliação de jogos
competitivos (não transitividade, equilíbrio, profundidade estratégica).
