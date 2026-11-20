# Segunda revisão de literatura para a V2: seis perguntas

Entrega do Claude Science para o prompt `docs/TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_2.md` (#208), colada pelo Matheus em 2026-10-07 e
salva pelo coordenador. O texto é o da sessão, com uma correção do revisor já aplicada:
- **Akam et al. 2015:** só a página 1 de 25 foi lida, que é o resumo;
- **Kimmel e Terrant 1968:** só a página 1 de 4 foi lida.

As afirmações sobre esses dois artigos são do nível do que foi lido. Não se citam resultados empíricos deles.

## Limitações de busca, declaradas de saída

- **Não houve varredura por código.** O ambiente de execução da sessão falhou em todas as tentativas (seis, ~160 s cada). A verificação foi
  feita item a item, pelo resolvedor de DOI, Unpaywall, PMC e páginas de editor, e a descoberta foi por busca web.
- **Não houve auditoria da lista de autores** (Crossref × Europe PMC), que é passo fixo do projeto. Onde a autoria não apareceu no próprio
  registro, isso está marcado.
- **Três DOIs que a sessão trazia de memória estavam errados** e foram corrigidos por busca (seção 3).
- **A cobertura é desigual.** As perguntas 1, 2, 5 e 6 ficaram bem cobertas; a 3 e a 4, parciais (seção 4).
- **Nenhuma alegação de novidade** é feita neste documento.

## 1. Referências verificadas

| # | referência | tipo | DOI / id | texto lido | o que sustenta | P |
|---|---|---|---|---|---|---|
| 1 | Daw, Niv & Dayan 2005, Nat Neurosci | par | `10.1038/nn1560` | título/metadados | arbitragem entre os sistemas pré-frontal e estriatal por incerteza | 1 |
| 2 | Dolan & Dayan 2013, Goals and Habits in the Brain, Neuron | par | `10.1016/j.neuron.2013.09.007` | resumo | metas × hábitos como espectro, não dicotomia; revisa quatro gerações de paradigmas | 1 |
| 3 | Daw et al. 2011, Neuron | par | `10.1016/j.neuron.2011.02.027` | título/metadados | a origem da tarefa de dois passos | 1 |
| 4 | Akam, Costa & Dayan 2015, Simple Plans or Sophisticated Habits?, PLoS Comput Biol | par | `10.1371/journal.pcbi.1004648` | PDF obtido; 1 de 25 páginas lida (resumo) | estratégias sem modelo podem imitar a assinatura de modelo na tarefa de dois passos | 1 |
| 5 | Dayan 1993, The Successor Representation, Neural Computation | par | `10.1162/neco.1993.5.4.613` | resumo | generalização pela semelhança dos sucessores, aprendida por TD | 1 |
| 6 | Momennejad et al. 2017, Nat Hum Behav | par | `10.1038/s41562-017-0180-8` | resumo | a SR é intermediária: flexível a mudança de recompensa, insensível a mudança de transição | 1 |
| 7 | Pfeiffer & Foster 2013, Nature | par | `10.1038/nature12112` | resumo | sequências hipocampais antes do movimento traçam caminhos até a meta lembrada | 1 |
| 8 | Miller, Botvinick & Brody 2017, Nat Neurosci | par | `10.1038/nn.4613` | título/metadados | o hipocampo dorsal contribui para o planejamento com modelo | 1 |
| 9 | Church 1964, Psychol Bull 62:122-131 | par | `10.1037/h0042733` | título/metadados (PMID 14199645) | o erro aleatório no desenho acoplado gera efeito sistemático | 2 |
| 10 | Kimmel & Terrant 1968, Behav Res Meth & Instru 1:11-14 | par | `10.3758/BF03209860` | PDF obtido; 1 de 4 páginas lida | propõe o acoplado recíproco e critica as premissas de Church | 2 |
| 11 | Garcia & Koelling 1966, Psychon Sci | par | `10.3758/BF03342209` | PDF obtido | a relação entre pista e consequência na aprendizagem de evitação | 3 |
| 12 | Burn 2017, Bestial boredom, Animal Behaviour 130:141-151 | par (ensaio) | `10.1016/j.anbehav.2017.06.006` | resumo e destaques do editor | o tédio como excitação subótima mais aversão à monotonia, as duas mensuráveis | 4 |
| 13 | Meagher & Mason 2012, PLoS ONE | par | `10.1371/journal.pone.0049180` | PDF obtido | o enriquecimento reduz sinais de tédio em marta enjaulada | 4 |
| 14 | Meagher, Campbell & Mason 2017, Appl Anim Behav Sci 197:112-119 | par | `10.1016/j.applanim.2017.08.001` | PDF obtido | replicação dos estados tipo-tédio e de seus correlatos comportamentais | 4 |
| 15 | Charnov 1976, Optimal foraging, the marginal value theorem, Theor Popul Biol | par | `10.1016/0040-5809(76)90040-x` | só título/metadados | **conteúdo não confirmado** | 5 |
| 16 | Hayden, Pearson & Platt 2011, Nat Neurosci | par | `10.1038/nn.2856` | resumo | um tempo de viagem maior eleva o limiar neural de abandono da mancha | 5 |
| 17 | Constantino & Daw 2015, Cogn Affect Behav Neurosci | par | `10.3758/s13415-015-0350-y` | PDF obtido | o custo de oportunidade do tempo é aprendido numa tarefa de manchas | 5 |
| 18 | Ghirlanda & Enquist 2003, A century of generalization, Animal Behaviour | par | `10.1006/anbe.2003.2174` | título/metadados | revisão de um século de gradientes de generalização | 6 |
| 19 | Dymond et al. 2015, Behavior Therapy | par | `10.1016/j.beth.2014.10.001` | título/metadados | revisão sistemática da generalização do medo em humanos | 6 |

- **Autoria:** conferida no próprio registro nos itens 6, 9, 10, 12 e 14. Nos demais, ela vem de listas de referência de terceiros e não
  passou pela auditoria do projeto.
- **Correção ou retratação:** nenhum item apresentou aviso nos registros consultados. Nenhum é preprint.
- **Já verificadas em rodadas anteriores e reaproveitadas:**
  - Keramati & Gutkin, `10.7554/eLife.04811` (P4);
  - Oudeyer & Kaplan, `10.3389/neuro.12.006.2007` (P4);
  - Singh et al., `10.1109/TAMD.2010.2051031` (P4);
  - Garcia et al. 1955, `10.1126/science.122.3160.157` (P3);
  - Casey et al., `10.1038/s41598-021-97743-0` (P6);
  - Vieira de Castro et al., `10.1371/journal.pone.0225023` (P6);
  - China, Mills & Cooper, `10.3389/fvets.2020.00508` (P6);
  - Ziv, `10.1016/j.jveb.2017.02.004` (P6);
  - MacGlashan et al., arXiv:1701.06049 (contexto);
  - Grand & Cliff, `10.1023/A:1010042522104` (contexto).

## 2. Síntese por pergunta

### P1: planejamento com modelo × hábito

**O que a literatura sustenta:**
- **A oposição não é binária.** Dolan e Dayan tratam metas × hábitos como espectro. Eles descrevem a tradição experimental como gerações de
  paradigmas, e as mais recentes desafiam o próprio centro da distinção.
- **A arbitragem clássica é por incerteza relativa** entre os dois sistemas (Daw, Niv e Dayan 2005). O título e o DOI foram conferidos, o
  conteúdo não.

**O intermediário barato é a representação de sucessor (SR).**
- Dayan (1993) a define como generalização entre estados pela semelhança dos seus sucessores, aprendida pela própria maquinaria de TD.
- Momennejad et al. (2017) mostram uma assinatura comportamental própria: ela é flexível quando a recompensa muda e insensível quando a
  sequência de eventos muda.

**A evidência animal de simular antes de agir:**
- Pfeiffer e Foster (2013): antes da navegação até uma meta, o hipocampo gera sequências da posição atual até a meta conhecida, e elas
  preveem o comportamento imediato, inclusive com início e meta novos.
- Miller, Botvinick e Brody (2017) ligam o hipocampo dorsal ao planejamento com modelo (título conferido, conteúdo não).

**O problema da medida.** Akam, Costa e Dayan (2015), no nível do resumo: na tarefa de dois passos, interações entre estado, transição e
aprendizado fazem estratégias sem modelo produzirem a assinatura atribuída ao controle com modelo.

**Entregue.**
- **A arquitetura mínima defensável:**
  - o prior herdado;
  - um aprendiz sem modelo;
  - uma camada de SR sobre os estados do mapa, atualizada por TD.

  A SR é uma matriz de ocupância futura descontada: cabe em aritmética inteira, roda no navegador e não exige busca em árvore. Dyna e a busca
  de horizonte curto ficam como opção posterior.
- **A medida é um par de testes, e não a tarefa de dois passos sozinha:**
  1. **Revalorização da recompensa sem reexperiência.** Troca-se o efeito de uma fruta e mede-se a escolha na primeira oportunidade, sem
     o agente ter comido de novo. O hábito não muda; a SR e o modelo mudam.
  2. **Mudança de transição sem reexperiência.** Troca-se onde a fruta cai, mantendo os efeitos. A SR não acompanha, e o modelo acompanha.
     É este teste que separa a SR do planejamento.

### P2: o controle acoplado e as alternativas

- **Church (1964) é a fonte original da objeção** (só os metadados foram conferidos). O desenho acoplado pode confundir e rejeitar
  hipóteses nulas verdadeiras mais do que o nominal, quando os sujeitos diferem nas reações ao reforçador.
- **Kimmel e Terrant (1968), página 1,** descrevem o mecanismo com um exemplo:
  - se o sujeito experimental condiciona melhor, os dois recebem poucos choques, e o controle recebe menos do que precisaria;
  - se o controle condiciona melhor, os dois recebem muitos, e eles são desperdiçados nele;
  - nos dois casos aparece uma diferença espúria a favor do procedimento experimental.
- **O paralelo com o achado 2:** o acoplado em malha aberta cuidou pior, e a diferença não se lê como efeito do ensino.
- **A ressalva sobre a força da evidência.** Kimmel e Terrant criticam Church no mesmo artigo. Eles registram reservas sérias e consideram
  duas das premissas dele quase insustentáveis para respostas mediadas pelo sistema autônomo. A objeção é real como risco de desenho, mas a
  magnitude dela é contestada.

**Entregue: o acoplado recíproco.**
- **O desenho de Kimmel e Terrant:** cada sujeito do par recebe dois estímulos. Num, há contingência instrumental; no outro, ele está
  acoplado ao estímulo do parceiro. Cada um é o controle acoplado do outro, num 2×2 dentro do sujeito.
- **Traduzido para o Digilab:** cada pet tem dois canais, por exemplo duas frutas ou duas regiões.
  - Num canal, o dono responde ao que este pet faz.
  - No outro, o pet recebe o cuidado gerado pelo parceiro.
  - A comparação ensino × cuidado passa a ser dentro do mesmo pet e da mesma vida.

### P3: aprender o que faz mal sem alternativa (cobertura parcial)

- **Firme:** Garcia e Koelling (1966), em PDF.
  - A associabilidade depende do par pista e consequência: o gosto se associa ao mal-estar visceral, e o estímulo externo à dor periférica.
  - É isso que torna a aversão ao gosto possível com pouquíssimas experiências e com atraso longo.
- **Não localizado:** trabalho que compare aprender "não comer" sem alternativa com aprender "escolher a outra".

**Entregue: três mecanismos candidatos.** O segundo e o terceiro são leitura da sessão sobre o nosso aprendiz, não achados de fonte.
1. **Aversão gustativa condicionada (Garcia).** A rejeição é aprendida sem alternativa, porque muda o valor do item. Com esse mecanismo, o
   achado 1 não aconteceria.
2. **Aprendiz de escolha relativa.** Se a atualização só ocorre sobre o contraste entre as opções apresentadas, uma opção única não gera
   gradiente. Prevê o achado 1.
3. **Valor do item separado do valor do ato de comer.** O agente aprende sobre a fruta e come assim mesmo, porque a decisão de comer é
   dominada pela fome. É compatível com o achado 1.

**O teste que separa os três:** escolha única depois de treino com escolha. Se a rejeição transferir, o mecanismo é hedônico; se não
transferir, é relativo.

### P4: tédio, curiosidade e RL homeostático (cobertura parcial)

- **O tédio animal tem base empírica.**
  - Burn (2017) o trata por duas qualidades mensuráveis, valência e excitação: excitação subótima somada a aversão à monotonia.
  - Meagher e Mason (2012): o enriquecimento reduz os sinais de tédio em martas.
  - Meagher, Campbell e Mason (2017) replicam os estados tipo-tédio.
- **O ponto de desenho:** o tédio não é ausência de recompensa, é aversão à monotonia. Um drive que só sobe com o tempo sem estímulo não
  reproduz isso. A repetição do mesmo precisa ser aversiva.

**Entregue.**
- **O tédio** tem como variável a diversidade recente de estados ou de interações, e não o tempo parado. Brincar com a bola duas vezes
  seguidas reduz menos que brincar e depois explorar.
- **A curiosidade** reduz em proporção ao progresso de predição, e não à surpresa bruta. É a defesa clássica contra o agente ficar preso numa
  fonte de ruído.
- **Contra o vício de explorar:** o tédio é saciável como os outros drives. Em Keramati e Gutkin, a recompensa é a redução do desvio do ponto
  de ajuste, então um drive satisfeito deixa de pagar.
- **A arbitragem entre vários drives sem um dominar** não foi resolvida com fonte verificada (seção 4).

### P5: forrageio com manchas e mapa espacial

- **O conteúdo de Charnov 1976 não foi confirmado.** O DOI resolve e o título confere, mas o artigo é fechado. Continua só com os
  metadados conferidos.
- **Hayden, Pearson e Platt (2011)**, no resumo, registram no cingulado anterior dorsal de macacos, numa tarefa de manchas:
  - um sinal que cresce a cada decisão de ficar e atinge um limiar fixo no abandono;
  - com tempos de viagem maiores, o limiar sobe, e o animal fica mais na mancha quando viajar custa mais.

  *Leitura da sessão:* é o padrão que o teorema do valor marginal prevê. A ligação ao teorema é leitura, não citação de Charnov.
- **Constantino e Daw (2015):** o custo de oportunidade do tempo é aprendido, não dado.

**Entregue: as medidas de "explorar compensou" num mapa 2D**, em ordem de robustez:
1. **Tempo de permanência por região contra o tempo de deslocamento até a próxima.** A previsão de Hayden é que a permanência cresce com o
   custo de viagem.
2. **Taxa de ganho realizada contra a taxa média do ambiente no abandono.** O teorema prevê igualdade.
3. **Custo de oportunidade estimado pelo agente contra o real.** Mede se ele aprendeu o custo.

**A previsão concreta para o nosso mundo:** com as árvores mais distantes e nada mais mudado, o pet esvazia mais cada árvore antes de sair.
Se não muda, ele está seguindo o gradiente de cheiro, e não forrageando.

### P6: punição e generalização do medo

- **O espalhamento do achado 3 tem literatura própria.**
  - Ghirlanda e Enquist (2003; só metadados conferidos): os gradientes de generalização.
  - Dymond et al. (2015; só metadados conferidos): a generalização do medo em humanos.

  *Leitura da sessão:* a punição valendo para todas as frutas é um gradiente plano. A representação de fruta do cérebro C não teria
  dimensões que distingam as frutas no canal aversivo; não é que o aprendizado falhou.
- **Punição social × consequência natural.**
  - China, Mills e Cooper (2020), já verificado, estende Casey et al. e Vieira de Castro et al.
  - Nenhum trabalho que contradiga a direção deles foi localizado.

**Entregue: o tapa como estímulo no corpo.**
- **A favor:** um estímulo corporal tem dimensões (intensidade, lugar, momento) que uma nota escalar não tem. Dimensões permitem um
  gradiente não plano, então o tapa pode reduzir o espalhamento.
- **Contra:** o estímulo aversivo de um parceiro social é o que a literatura de treino aversivo em cães liga a custo de bem-estar.
- **Medir quatro coisas, separadas:**
  - **medo:** a resposta ao estímulo;
  - **estresse:** o estado de base fora do episódio;
  - **vínculo:** o comportamento dirigido ao dono em contexto neutro;
  - **generalização:** a inclinação do gradiente da aversão sobre as frutas não punidas, e não o valor numa só.

## 3. Divergências e riscos

| risco | força | o que fazer |
|---|---|---|
| A tarefa de dois passos não prova planejamento (Akam et al., no nível do resumo) | alta | usar o par revalorização + mudança de transição |
| O acoplado tem objeção clássica, mas contestada (Church; Kimmel e Terrant) | média | não escrever que o acoplado "é inválido"; o defensável é que ele é enviesável e que o recíproco remove a fonte do viés |
| O achado 1 seria uma propriedade do aprendiz de escolha relativa, não uma falha de treino | baixa a média (leitura, sem fonte) | não "consertar" antes de testar a transferência da escolha para o item único |
| O tédio como ausência de estímulo é a formalização errada (Burn; Meagher et al.) | média-alta | o tédio pela diversidade recente; um drive que sobe com o tempo parado faz o pet se contentar em repetir |
| Atribuir a Charnov um conteúdo não lido | regra do projeto | o padrão vem de Hayden et al.; a ligação ao teorema é leitura |
| DOIs de memória errados: `10.1037/h0042575` (psicanálise), `10.1016/j.anbehav.2017.05.006` (lateralização), `10.1038/nrn.2016.30` (outro artigo) | — | nenhum DOI entra no projeto sem resolver |

## 4. Lacunas e buscas feitas

**Não localizado:**
- a comparação direta entre a rejeição absoluta e a escolha relativa, com e sem alternativa (P3);
- a arbitragem entre vários drives homeostáticos sem dominância, além de Keramati e Gutkin (P4);
- Schmidhuber sobre progresso de aprendizado e os mapas espaciais em forrageadores: não verificados (P4, P5);
- trabalho que contradiga Casey et al. 2021 e Vieira de Castro et al. 2020 (P6);
- Nonacs 2001: o DOI que a sessão tinha (`10.1093/beheco/12.1.71`) não existe no Crossref;
- Redish, vicarious trial and error: o DOI estava errado, e o certo não foi buscado;
- Sutton 1990 (Dyna) e Adams & Dickinson (desvalorização): não verificados.

**Buscas feitas:**
- resolução direta de 20 DOIs candidatos por Unpaywall, Semantic Scholar, PMC, Crossref TDM e o resolvedor de DOI;
- duas buscas web dirigidas (Church 1964, Burn 2017);
- nenhuma busca sistemática por termos em base bibliográfica.

## 5. BibTeX das verificadas

```bibtex
@article{akam2015simple,
  title   = {Simple Plans or Sophisticated Habits? State, Transition and Learning
             Interactions in the Two-Step Task},
  journal = {PLOS Computational Biology}, year = {2015},
  doi     = {10.1371/journal.pcbi.1004648},
  note    = {PDF obtido; 1 de 25 paginas lida (resumo); autoria nao conferida no registro}
}
@article{dolan2013goals,
  title   = {Goals and Habits in the Brain}, journal = {Neuron}, year = {2013},
  doi     = {10.1016/j.neuron.2013.09.007},
  note    = {resumo lido; autoria nao conferida no registro}
}
@article{daw2005uncertainty,
  title   = {Uncertainty-based competition between prefrontal and dorsolateral
             striatal systems for behavioral control},
  journal = {Nature Neuroscience}, year = {2005}, doi = {10.1038/nn1560},
  note    = {apenas titulo e metadados conferidos}
}
@article{daw2011modelbased,
  title   = {Model-Based Influences on Humans' Choices and Striatal Prediction Errors},
  journal = {Neuron}, year = {2011}, doi = {10.1016/j.neuron.2011.02.027},
  note    = {apenas titulo e metadados conferidos}
}
@article{dayan1993successor,
  title   = {Improving Generalization for Temporal Difference Learning:
             The Successor Representation},
  journal = {Neural Computation}, year = {1993}, doi = {10.1162/neco.1993.5.4.613},
  note    = {resumo lido; autoria nao conferida no registro}
}
@article{momennejad2017successor,
  author  = {Momennejad, I. and others},
  title   = {The successor representation in human reinforcement learning},
  journal = {Nature Human Behaviour}, year = {2017}, doi = {10.1038/s41562-017-0180-8},
  note    = {resumo lido; primeiro autor confirmado no proprio resumo}
}
@article{pfeiffer2013hippocampal,
  title   = {Hippocampal place cell sequences depict future paths to remembered goals},
  journal = {Nature}, year = {2013}, doi = {10.1038/nature12112},
  note    = {resumo lido; autoria nao conferida no registro}
}
@article{miller2017dorsal,
  title   = {Dorsal hippocampus contributes to model-based planning},
  journal = {Nature Neuroscience}, year = {2017}, doi = {10.1038/nn.4613},
  note    = {apenas titulo e metadados conferidos}
}
@article{church1964systematic,
  author  = {Church, R. M.},
  title   = {Systematic effect of random error in the yoked control design},
  journal = {Psychological Bulletin}, volume = {62}, pages = {122--131}, year = {1964},
  doi     = {10.1037/h0042733}, note = {PMID 14199645; metadados conferidos}
}
@article{kimmel1968bias,
  author  = {Kimmel, H. D. and Terrant, F. R.},
  title   = {Bias due to individual differences in yoked control designs},
  journal = {Behavior Research Methods \& Instrumentation}, volume = {1}, year = {1968},
  doi     = {10.3758/BF03209860}, note = {PDF obtido; 1 de 4 paginas lida}
}
@article{garcia1966relation,
  author  = {Garcia, J. and Koelling, R. A.},
  title   = {Relation of cue to consequence in avoidance learning},
  journal = {Psychonomic Science}, year = {1966}, doi = {10.3758/BF03342209},
  note    = {PDF obtido}
}
@article{burn2017bestial,
  author  = {Burn, Charlotte C.},
  title   = {Bestial boredom: a biological perspective on animal boredom and
             suggestions for its scientific investigation},
  journal = {Animal Behaviour}, volume = {130}, pages = {141--151}, year = {2017},
  doi     = {10.1016/j.anbehav.2017.06.006},
  note    = {ensaio; resumo e destaques conferidos na pagina do editor}
}
@article{meagher2012environmental,
  title   = {Environmental Enrichment Reduces Signs of Boredom in Caged Mink},
  journal = {PLOS ONE}, year = {2012}, doi = {10.1371/journal.pone.0049180},
  note    = {PDF obtido; autoria nao conferida no registro}
}
@article{meagher2017boredomlike,
  author  = {Meagher, R. K. and Campbell, D. L. M. and Mason, G. J.},
  title   = {Boredom-like states in mink and their behavioural correlates: A replicate study},
  journal = {Applied Animal Behaviour Science}, volume = {197}, pages = {112--119}, year = {2017},
  doi     = {10.1016/j.applanim.2017.08.001}, note = {PDF obtido}
}
@article{charnov1976optimal,
  title   = {Optimal foraging, the marginal value theorem},
  journal = {Theoretical Population Biology}, year = {1976},
  doi     = {10.1016/0040-5809(76)90040-x},
  note    = {APENAS titulo e metadados; conteudo NAO confirmado}
}
@article{hayden2011neuronal,
  title   = {Neuronal basis of sequential foraging decisions in a patchy environment},
  journal = {Nature Neuroscience}, year = {2011}, doi = {10.1038/nn.2856},
  note    = {resumo lido; autoria nao conferida no registro}
}
@article{constantino2015learning,
  title   = {Learning the opportunity cost of time in a patch-foraging task},
  journal = {Cognitive, Affective, \& Behavioral Neuroscience}, year = {2015},
  doi     = {10.3758/s13415-015-0350-y},
  note    = {PDF obtido; autoria nao conferida no registro}
}
@article{ghirlanda2003century,
  title   = {A century of generalization}, journal = {Animal Behaviour}, year = {2003},
  doi     = {10.1006/anbe.2003.2174}, note = {apenas titulo e metadados conferidos}
}
@article{dymond2015fear,
  title   = {Fear Generalization in Humans: Systematic Review and Implications
             for Anxiety Disorder Research},
  journal = {Behavior Therapy}, year = {2015}, doi = {10.1016/j.beth.2014.10.001},
  note    = {apenas titulo e metadados conferidos}
}
```

## 6. Pistas para a próxima passada: NÃO verificadas

Nada desta lista sustenta afirmação de conteúdo.

| pista | onde | pergunta |
|---|---|---|
| Dunlap, Austin & Figueiredo 2019 | Anim Behav, `10.1016/j.anbehav.2018.05.024` | pendente da rodada anterior |
| Liedtke & Fromhage 2019 | Sci Rep, `10.1038/s41598-019-51652-5` | pendente da rodada anterior |
| Eliassen et al. 2009 | Am Nat, `10.1086/605370` | pendente da rodada anterior |
| Mason & Burn 2018, Frustration and boredom in impoverished environments | capítulo, sem DOI localizado | P4 |
| "Is boredom an animal welfare concern?" | Animal Welfare 2019, 28:21-32, `10.7120/09627286.28.1.021` | P4 |
| Nonacs, valor marginal dependente de estado | Behav Ecol 2001, DOI a localizar | P5 |
| Redish, vicarious trial and error | Nat Rev Neurosci 2016, DOI a localizar | P1 |
| Sutton 1990 (Dyna) e Adams & Dickinson (desvalorização) | a verificar | P1 |
| Schmidhuber, curiosidade e progresso de aprendizado | a verificar | P4 |
