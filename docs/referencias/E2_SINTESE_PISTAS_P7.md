# Segunda passada de literatura (P-7): as pistas de prioridade 1

Data: 2026-10-06. Tarefa `docs/TAREFA_V2_LITERATURA_P7.md`; decisão P-7 de `docs/PREDICOES_V2.md`; adendo 3, seção 3.4, de
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`.

**O que é:** só papel. Não roda nada e não muda código nem desenho. O desenho fica congelado até a validação. Onde uma fonte pesa, este
documento diz **o que muda na leitura**, nunca no desenho.

**Regras** (`docs/referencias/REGRAS_CITACAO_DIGILAB.md`):
- cada afirmação separa **"a fonte diz"** de **"leitura nossa"**;
- cada referência diz o que foi conferido: texto completo, resumo, ou só título e metadados;
- referência conferida só por título e metadados não sustenta conteúdo;
- nenhuma alegação de novidade.

## Como a conferência foi feita

- **Registro:** o DOI de cada item foi resolvido na API do Crossref (autores, ano, veículo, páginas, `update-to`, `updated-by` e
  `relation`). Nenhum dos itens tem correção nem retratação registrada.
- **Resumo e acesso:** pela API do OpenAlex (o resumo e o estado de acesso aberto) e, quando o OpenAlex não tinha o resumo, pela do
  Semantic Scholar. O resumo do Eliassen et al. foi conferido também no PubMed.
- **Texto completo:** quando o artigo é de acesso aberto, pelo Europe PMC.
- **Ressalva de cobertura:** foram consultas pontuais, item a item, por DOI e por título. Não houve varredura sistemática.

---

## Tabela

No formato de `docs/referencias/*.csv`, com uma coluna a mais: o que foi conferido. A trilha aponta as predições da V2 (P1 a P5 de
`docs/PREDICOES_V2.md`).

| referencia | tipo | verificada | o_que_sustenta | trilha | relevancia | doi_ou_id | o que foi conferido |
|---|---|---|---|---|---|---|---|
| Dunlap, A. S.; Austin, M. W.; Figueiredo, A. (2019). Components of change and the evolution of learning in theory and experiment. *Animal Behaviour* 147:157-166. | par | VERIFICADA | Revisão: o consenso teórico é que a previsibilidade e a escala de tempo da mudança ambiental decidem quando o aprendizado evolui; o que cada modelo chama de "mudança" varia muito; padronizar as medidas de mudança torna os modelos tratáveis. | P1, P2 | alta | `10.1016/j.anbehav.2018.05.024` | **resumo** (Semantic Scholar; o Crossref e o OpenAlex não têm o resumo); texto fechado, não lido |
| Liedtke, J.; Fromhage, L. (2019). Need for speed: Short lifespan selects for increased learning ability. *Scientific Reports* 9:15197. | par | VERIFICADA | Simulação individual com análise de apoio: a **velocidade** de aprendizado evolui com custo na fecundidade. O investimento nela é máximo quando a vida mal dá para dominar o desafio e cai com vidas mais longas. "Vida longa" não seleciona aprendizado; relaxa a seleção sobre a velocidade. | P1, P2 | alta | `10.1038/s41598-019-51652-5` (CC BY 4.0) | **texto completo** (Europe PMC, PMC6811680); o modelo analítico do material suplementar não foi lido |
| Eliassen, S.; Jørgensen, C.; Mangel, M.; Giske, J. (2009). Quantifying the adaptive value of learning in foraging behavior. *The American Naturalist* 174(4):478-489. | par | VERIFICADA | Modelo de forrageamento em manchas: a **eficiência** do aprendizado (perto da informação perfeita) e o **valor** dele (ganho sobre a regra fixa herdada) têm ótimos diferentes. Regras que atualizam rápido servem à mudança no tempo; as lentas resistem melhor à variação entre manchas. | P1, P2, P4 | alta | `10.1086/605370` (PMID 19694535) | **resumo** (OpenAlex e PubMed); texto fechado, não lido |
| Dwyer, D. M. (2015). Experimental evolution of sensitivity to a stimulus domain alone is not an example of prepared learning. *PNAS* 112(5):E385. | par | VERIFICADA (registro) | Carta publicada sobre Dunlap e Stephens 2014 (`10.1073/pnas.1404176111`; o PMC liga os dois como artigos relacionados). **Só o título**: sustenta que a carta existe e contesta o artigo, não o argumento. | — | baixa | `10.1073/pnas.1420871112` (PMID 25609674) | **título e metadados**; o PMC não tem o texto aberto e a página da PNAS bloqueou o acesso automático |
| Ackley, D.; Littman, M. (1991 ou 1992). Interactions between learning and evolution. Em: Langton, C. G. et al. (eds.), *Artificial Life II*, SFI Studies in the Sciences of Complexity, pp. 487-509. | cinza | **existência confirmada; conteúdo não lido** | Nada de conteúdo. O registro aparece em duas listas de referências revisadas por pares, com ano e título divergentes (tabela abaixo). | — | baixa | sem DOI | listas de referências de Kozielska e Weissing 2024 e de Nolfi e Floreano 1999, pelo Crossref |

**Registros do Ackley e Littman nas listas de referências:**

| lista | ano | título | onde | página |
|---|---|---|---|---|
| Kozielska e Weissing 2024, `10.1371/journal.pcbi.1011840` (ref044) | 1992 | "Interactions Between Learning and Evolution" | *Artificial Life II*, SFI Studies in the Sciences of Complexity | 487 |
| Nolfi e Floreano 1999, `10.1023/A:1008973931182` (CR1) | 1991 | "Interaction between learning and evolution" | *Proceedings of the Second Conference on Artificial Life*, Addison-Wesley | — |

**Duas correções à síntese anterior** (`E_SINTESE_VALOR_APRENDIZADO.md`):
- **O "comentário publicado contestando o artigo" de 2014.** No Crossref, a relação do artigo é `has-review`, que aponta para uma
  recomendação do Faculty Opinions (`10.3410/f.718509055.793521507`, Simon Reader, 2016), não para uma contestação. A carta que contesta é
  a do Dwyer (2015), acima, achada pela lista de citações e pela ligação do PMC.
  - Nenhuma resposta dos autores apareceu no PubMed nem no Crossref (busca por autor e por "Reply to Dwyer").
- **O ano e o título do Ackley e Littman divergem entre as duas listas** (tabela acima).
  - A síntese o dava como 1992; a regra 6 da skill de literatura, como "Ackley e Littman (1991), não localizada".
  - Com duas listas revisadas, a existência fica confirmada. O texto não foi lido, então ele **não** sustenta afirmação de conteúdo.
  - A mudança de status na skill e no CSV é do Matheus (decisão L-2).

---

## Liedtke e Fromhage: a vida curta contraria a predição 2?

**Não, como a predição está escrita.** A tarefa pedia atenção a este ponto.

**A fonte diz** (texto completo):
- **O que evolui é a velocidade de aprendizado** (L, um locus), sob custo proporcional na fecundidade: F = V_total × (1 − α·L).
- **Para que serve aprender:** reduz o tempo de manuseio de recursos que, sem aprender, não cabem num dia.
- **O investimento em L tem picos.** Cada pico fica na duração de vida que mal basta para dominar um recurso. A partir dali, o investimento
  cai com vidas mais longas: com vida longa, aprender devagar também chega lá, e o custo menor compensa.
- **Os próprios autores** dizem que o resultado não contradiz a ideia de que uma vida longa ajuda a recuperar o investimento. Há dois
  efeitos opostos, e qual domina depende da ecologia.
- **Nas palavras deles,** a longevidade em si não seleciona aprendizado: relaxa a seleção sobre a **velocidade** dele.

**Leitura nossa:**
- **Perguntas diferentes.** A predição 2 compara, dentro de uma vida, um aprendiz de taxa fixa (o P1, ganho 4 no ponto da K2) com o
  herdado sem aprender (P0). O Liedtke e Fromhage trata da evolução da velocidade de aprender ao longo de gerações, com custo. Na V2 a taxa
  não evolui e aprender não custa fecundidade.
- **Na mesma direção da condição "se a vida for longa".** No modelo, um aprendiz só colhe o benefício depois de dominar o desafio, e uma
  vida mais longa dá mais tempo de colheita.
- **Muda a leitura, não o teste, em dois pontos:**
  1. **Forma da curva do bloco de durações** (adendo 3, seção 3.1: 7, 14 e 21 ou 28 dias).
     - Além de crescente, platô e ótimo interior, o modelo descreve um **limiar**: abaixo de uma duração mínima, aprender não rende nada;
       acima dela, rende.
     - Com só três durações, um limiar abaixo de 7 dias aparece como "crescente" ou "platô", e um entre 7 e 14 dias, como um degrau.
     - A leitura deve nomear o limiar como possibilidade antes de escolher entre as três formas registradas.
  2. **Condicional à taxa.** Um P1 que não vence o P0 em 7 dias não diz que "aprender não compensa em vida curta". Pelo modelo, uma vida
     curta favorece aprender **mais depressa**, e a taxa do P1 é a da calibração conjunta, fixa. O resultado vale para essa taxa.

---

## Por predição

### Predição 1: no casado, P0 vence; aprender só custa

**Apoio teórico: segue APOIADA.** Os dois itens novos com conteúdo apoiam a direção por caminhos indiretos.

**A fonte diz:**
- **Eliassen et al. 2009** (resumo): o valor do aprendizado sobre a regra fixa herdada é menor quando não há mudança no tempo nem variação
  entre manchas.
- **Liedtke e Fromhage 2019** (texto completo): quando a vida é curta demais para dominar o desafio, o investimento em aprender cai. Os
  forrageadores seletivos ficam no recurso que não pede aprendizado.

**Leitura nossa:**
- No casado, o prior já escolhe a fruta boa. Não há recurso "inacessível sem aprender" nem diferença entre opções que o prior não
  resolva. É o regime em que os dois modelos dão pouco valor ao aprendizado.
- **O Eliassen não modela desencontro entre o herdado e o mundo;** é um paralelo de forma.
- **O custo nos dois modelos é diferente do da V2.** No Liedtke e Fromhage, o custo é constitutivo (fecundidade). Na V2 o custo é só
  exploração e deriva. Isso confirma a leitura já registrada no `PREDICOES_V2.md`: o mais provável no casado é empate ou pequena vantagem
  do P0, e um "refuta por empate" não é defeito do desenho.

### Predição 2: no descasado e no mutável, P1 vence P0 se a vida for longa

**Apoio teórico: segue APOIADA COM RESSALVA.** A ressalva ganha precisão: a relação com a duração pode ter **limiar**, além de platô ou
ótimo interior.

**A fonte diz:**
- **Dunlap, Austin e Figueiredo 2019** (resumo):
  - a previsibilidade e a escala de tempo da mudança decidem quando o aprendizado evolui;
  - "mudança" quer dizer coisas diferentes em modelos diferentes;
  - os autores pedem que cada estudo defina a mudança explicitamente.
- **Eliassen et al. 2009** (resumo):
  - o **valor** do aprendizado é maior quando há mudança no tempo (a estratégia flexível acompanha a tendência) e quando há variação
    entre opções (é preciso distinguir as boas das ruins);
  - a **eficiência** é maior com experiência confiável e pouca mudança no tempo.
- **Liedtke e Fromhage 2019** (texto completo): seção anterior.

**Leitura nossa:**
- **O relatório deve dizer que componente da mudança cada condição manipula, nos termos do Dunlap e Stephens 2009** (confiabilidade da
  experiência, previsibilidade da melhor ação), e não "a mudança" em geral:
  - **No descasado,** a experiência é confiável (o efeito de cada fruta é fixo) e a melhor ação é estável dentro da vida. O que muda é
    entre o mundo de origem do prior e o mundo da vida.
  - **No mutável,** a melhor ação troca uma vez, no meio da vida, num momento fixo.
  - Um resultado da predição 2 vale para esses componentes, não para "ambientes que mudam".
- **No mutável, separar valor de eficiência.** Pelo Eliassen, com mudança no tempo o **valor** do aprendizado é alto e a **eficiência**
  é baixa. Mesmo que o P1 vença o P0 depois da troca, não se deve esperar que ele chegue perto do ótimo (a taxa de fruta ruim 0). O
  contraste primário mede valor (P0 − P1). A distância ao ótimo é outra coisa e não deve ser lida como falha.
- **Do Liedtke e Fromhage:**
  - o limiar na forma da curva das durações;
  - a dependência da taxa de aprendizado fixa.
- **O que segue igual:** o mutável continua sem teoria dentro da vida. Os três modelos tratam mudança entre gerações ou entre manchas, não
  uma troca única no meio de uma vida. O adendo (b) segue valendo.

### Predição 4: P2e piora no começo e se recupera quando a consequência refuta a informação

**Apoio teórico: segue SEM APOIO DIRETO.** Nenhuma das três fontes trata informação errada vinda de outro indivíduo.

**A fonte diz:**
- **Eliassen et al. 2009** (resumo): regras com memória curta, que atualizam rápido, servem quando a informação é precisa e o ambiente
  muda. As que atualizam devagar são mais robustas à variação.

**Leitura nossa:**
- **Analogia, não apoio.** No P2e, o peso da informação (`w_info`) só aprende pela consequência, com o passo e o teto do ponto da K2. A
  velocidade com que a consequência desfaz a informação errada é a velocidade dessa atualização.
- **Uma recuperação que não vem nos 14 dias pode ser atualização lenta,** e não o mundo deixando de refutar. Pelo Eliassen, atualizar
  devagar é o que dá robustez em outras condições.
- **O que reportar ao lado:** o dia em que o P2e cruza o P0 (já registrado). Junto, a trajetória do `w_info` (o dia em que ele cruza o
  zero, medida do plano do N5). Isso permite distinguir "não refutou" de "refutou devagar".

### Predições 3 e 5

As três fontes não tratam ensino, informação de outro indivíduo nem feedback avaliativo. O apoio das predições 3 e 5 fica como está no
`PREDICOES_V2.md`.

---

## O que muda na leitura (resumo)

Nada aqui muda o desenho, os contrastes, o Holm, o N nem o Δ.

| onde | o que entra na leitura | fonte |
|---|---|---|
| predição 1 | o regime do casado é o de menor valor do aprendizado nos dois modelos; empate ou pequena vantagem do P0 seguem o esperado | Eliassen et al. 2009 (resumo); Liedtke e Fromhage 2019 (texto completo) |
| predição 2, condições | dizer que componente da mudança cada condição manipula (experiência confiável; melhor ação estável no descasado, trocada uma vez no mutável) | Dunlap, Austin e Figueiredo 2019 (resumo); Dunlap e Stephens 2009 (resumo) |
| predição 2, mutável | separar valor (P0 − P1) de eficiência (distância ao ótimo) | Eliassen et al. 2009 (resumo) |
| bloco de durações | considerar um **limiar** antes de escolher entre crescente, platô e ótimo interior | Liedtke e Fromhage 2019 (texto completo) |
| predição 2, 7 dias | o resultado vale para a taxa da calibração; vida curta favorece aprender mais depressa | Liedtke e Fromhage 2019 (texto completo) |
| predição 4 | reportar a trajetória do `w_info` ao lado do dia em que o P2e cruza o P0, para separar "não refutou" de "refutou devagar" | Eliassen et al. 2009 (resumo), por analogia |

---

## Pendências

- **Textos fechados.** O Dunlap, Austin e Figueiredo 2019 e o Eliassen et al. 2009 foram conferidos só pelo resumo; os textos não estão em
  acesso aberto.
  - O "flag model" de confiabilidade e certeza que o Dunlap descreve está no texto, não no resumo, e não foi usado.
  - Ler os dois textos completos é o próximo passo, se o Matheus quiser (decisão L-1).
- **Material suplementar do Liedtke e Fromhage** (o modelo analítico): não lido.
- **Dwyer 2015:** só título e metadados.
- **Ackley e Littman:** existência confirmada por duas listas; texto não consultado; o ano diverge.
- **Pistas de prioridade 2** da síntese anterior: não tocadas nesta passada.

## Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| L-1 | Buscar o texto completo do Dunlap, Austin e Figueiredo 2019 e do Eliassen et al. 2009 (acesso institucional ou pedido aos autores) antes da leitura dos resultados | **Sim**, para o Eliassen. Ele é o único com valor × eficiência e velocidade de atualização, que pesam na leitura do mutável e do P2e | sem o texto, as duas leituras ficam apoiadas só no resumo e não podem citar mecanismo nem número do modelo |
| L-2 | Mudar o status do Ackley e Littman na skill de literatura e no CSV, de "não localizada" para "existência confirmada; conteúdo não lido", com o ano em aberto (1991 ou 1992) | **Sim**, com a ressalva do ano | manter "não localizada" contradiz duas listas revisadas; marcar "verificada" sem ressalva deixa citar conteúdo que ninguém leu |
| L-3 | Incluir o **limiar** como forma possível na leitura do bloco de durações | **Sim**, só no texto da leitura; as três formas registradas e o teste não mudam | sem ele, um degrau entre 7 e 14 dias pode ser lido como "crescente" e confundido com "mais vida é sempre melhor" |
| L-4 | Reportar a trajetória do `w_info` do P2e ao lado do dia em que ele cruza o P0 | **Sim**, como descritivo: a medida já existe no plano do N5 | sem ela, uma recuperação lenta e uma recuperação que não vem ficam indistinguíveis |
