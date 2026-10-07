# Terceira revisão de literatura para a V2: o corpo digital

Entrega do Claude Science para o prompt `docs/TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_3.md` (#223), colada pelo Matheus em 2026-10-07 e salva
pelo coordenador. O texto é o da sessão, reorganizado sem mudar o conteúdo.

## Limitações de busca

- **Sem varredura por código.** O ambiente de execução falhou pela sétima vez seguida. Não houve acesso programático a Crossref, arXiv ou
  Europe PMC. A verificação foi feita item a item (Unpaywall, Semantic Scholar, PMC, Crossref TDM e o resolvedor de DOI), e a descoberta,
  por busca web.
- **Sem auditoria da lista de autores** (Crossref × Europe PMC). Onde a autoria não apareceu no registro consultado, está marcado.
- **Nenhum DOI de memória.** Os DOIs abaixo foram resolvidos nesta sessão. Cinco candidatos não eram o que a sessão supunha e foram
  descartados ou corrigidos.
- **A pergunta 5 ficou a mais fraca.**
- **Nenhuma alegação de novidade.**

## 1. Tabela

**Quanto foi lido limita o que se pode citar.** Itens com "só metadados" ou "PDF obtido, não lido" **não** sustentam afirmação de
conteúdo.

| # | referência | tipo | DOI | quanto foi lido | o que sustenta | P |
|---|---|---|---|---|---|---|
| 1 | Grand, Cliff & Malhotra 1997, *Creatures: artificial life autonomous software agents for home entertainment*, Proc. Agents '97 | par | `10.1145/267658.267663` | resumo | bioquímica artificial com metabolismo energético simples e sistema hormonal que modula a rede neural e o desenvolvimento por estágios | 1 |
| 2 | Grand & Cliff 1998, *Creatures: Entertainment Software Agents with Artificial Life*, Auton Agents Multi-Agent Syst | par | `10.1023/A:1010042522104` | só metadados | — (título conferido; conteúdo não acessado) | 1 |
| 3 | Cliff & Grand 1999, *The Creatures Global Digital Ecosystem*, Artificial Life | par | `10.1162/106454699568683` | resumo | rede recorrente modular com aprendizado hebbiano e modulação difusa por um sistema "hormonal" da bioquímica; rede e bioquímica especificadas geneticamente | 1 |
| 4 | Dittrich, Ziegler & Banzhaf 2001, *Artificial Chemistries — A Review*, Artificial Life | par | `10.1162/106454601753238636` | resumo | revisão do campo em três dimensões: modelagem, processamento de informação e otimização | 2 |
| 5 | Dittrich & Speroni di Fenizio 2007, *Chemical Organisation Theory*, Bull Math Biol | par | `10.1007/s11538-006-9130-8` | PDF obtido, não lido | — | 2 |
| 6 | Lones, Lewis & Cañamero 2018, *A Hormone-Driven Epigenetic Mechanism for Adaptation in Autonomous Robots*, IEEE TCDS 10(2):445-454 | par | `10.1109/TCDS.2017.2775620` | PDF obtido, não lido | — | 3 |
| 7 | Lewis & Cañamero 2016, *Hedonic quality or reward?*, Adaptive Behavior | par | `10.1177/1059712316666331` | resumo (PDF obtido) | prazer não ligado à satisfação de uma necessidade tem valor para a gestão homeostática: melhora a viabilidade e a flexibilidade | 3, 4 |
| 8 | Cañamero 2005, *Emotion understanding from the perspective of autonomous robots research*, Neural Networks | par | `10.1016/j.neunet.2005.03.003` | só metadados | — | 3 |
| 9 | Lones, Lewis & Cañamero 2014, ALIFE 14 | par (anais) | `10.1162/978-0-262-32621-6-ch031` | só metadados | — | 3 |
| 10 | Xu & Wang 2011, *Recent advances in the artificial endocrine system* | par | `10.1631/jzus.C1000044` | só metadados | — | 3 |
| 11 | Maroto-Gómez et al. 2023, *Modeling Neuroendocrine Autonomic Responses in Embodied Autonomous Robots*, Adv Intell Syst | par | `10.1002/aisy.202200288` | resumo (PDF obtido) | substâncias neuroendócrinas simuladas regulam processos autonômicos, com ritmo circadiano, por longos períodos | 3 |
| 12 | Roijers et al. 2013, *A Survey of Multi-Objective Sequential Decision-Making*, JAIR | par | `10.1613/jair.3987` | resumo (PDF obtido) | três cenários em que converter vários objetivos num só é impossível, inviável ou indesejável; taxonomia pela função de escalarização | 4 |
| 13 | Hulme, Morville & Gutkin 2019, *Neurocomputational theories of homeostatic control*, Phys Life Rev | par | `10.1016/j.plrev.2019.07.005` | PDF obtido, não lido | — | 4 |
| 14 | Juechems & Summerfield 2019, *Where Does Value Come From?*, Trends Cogn Sci | par | `10.1016/j.tics.2019.07.012` | só metadados | — | 4 |
| 15 | Bongard, Zykov & Lipson 2006, *Resilient Machines Through Continuous Self-Modeling*, Science | par | `10.1126/science.1133687` | resumo | o robô infere a própria estrutura pelas relações entre atuação e sensação e, com parte da perna removida, adapta o automodelo e gera outra marcha | 5, 6 |
| 16 | Kuehn & Haddadin, *An Artificial Robot Nervous System To Teach Robots How To Feel Pain…*, IEEE RA-L | par | `10.1109/LRA.2016.2536360` | só metadados | — | 5 |
| 17 | Seth & Friston 2016, *Active interoceptive inference and the emotional brain*, Phil Trans R Soc B | par | `10.1098/rstb.2016.0007` | resumo (texto completo em disco) | estados corporais regulados por reflexos autonômicos subordinados a predições de modelos generativos do meio interno e externo | 6 |

- **Autoria conferida no registro:** itens 11, 12, 15 e 17. Nos demais, a autoria vem de listas de referência de terceiros que
  concordam entre si.
- **Nenhum é preprint,** e nenhum tem aviso de correção ou retratação nos registros consultados.
- **Reaproveitados:** Keramati & Gutkin `10.7554/eLife.04811` (P4) e Burn `10.1016/j.anbehav.2017.06.006` (o tédio).

## 2. Síntese por pergunta

### P1: os órgãos do Creatures pela fonte primária

- **A fonte primária sustenta menos do que o desenho supõe.**
  - **Grand, Cliff e Malhotra (1997), resumo:**
    - uma rede neural coordena sensação, motricidade e seleção de comportamento;
    - uma "bioquímica artificial" modela um metabolismo energético simples;
    - um sistema hormonal modula difusamente a atividade neural e o desenvolvimento por estágios.
  - **Cliff e Grand (1999), resumo:**
    - a rede é recorrente e modular, com aprendizado hebbiano e a modulação hormonal;
    - a rede e a bioquímica são especificadas geneticamente, com mutação e duplicação de genes.
- **Fica confirmado pela fonte primária:**
  - os químicos;
  - as reações;
  - o acoplamento entre a bioquímica e a rede;
  - os drives como químicos;
  - o estágio acionado quimicamente.
- **Não confirmado em nenhuma fonte primária acessada:** a força vital do órgão, o dano, a cura, a energia de reparo e a morte por falência.
  - Grand & Cliff 1998 está fechado: só o título foi conferido.
  - O livro *Creation*, do Grand, também não foi verificado.
- **Entregue:** força vital, dano, cura e morte por órgão são, por ora, **detalhe de fã** (Creatures Wiki, CDN, openc2e), não do
  Creatures segundo a fonte primária.

### P2: química artificial estável

- **O enquadramento:** Dittrich, Ziegler e Banzhaf (2001) é a revisão do campo.
- **O critério de equilíbrio:** a teoria de organizações químicas (Dittrich e Speroni di Fenizio 2007) fala de conjuntos **fechados**
  (nenhuma reação produz algo de fora) e **automantidos** (nenhum membro é consumido sem ser reposto).
  - *Leitura da sessão, PDF não lido:* esse é o critério estrutural para o corpo não explodir nem zerar, e dá para checá-lo por inspeção,
    antes de rodar.
- **Os riscos de 10 a 20 químicos e poucos órgãos, em ordem:**
  1. **Acúmulo sem sumidouro:** todo químico precisa de um caminho de consumo.
  2. **Laço de ganho ≥ 1** entre receptor e emissor: proibir ciclos assim no grafo, verificável estaticamente.
  3. **Oscilação** por meias-vidas próximas entre químicos acoplados.
  4. **Saturação em inteiro:** o químico no teto deixa de responder e o drive congela.
- **A salvaguarda transversal:** o grafo de reações é um artefato a validar **antes** da run.

### P3: sistemas endócrinos artificiais

- **Lewis e Cañamero (2016):** o prazer desacoplado de necessidade melhorou a viabilidade e a flexibilidade de um robô. Isso apoia o
  conforto do carinho.
- **Maroto-Gómez et al. (2023):** ritmos neuroendócrinos estáveis por longos períodos.
- **Lones, Lewis e Cañamero (2018):** hormônio modulando o desenvolvimento. O PDF não foi lido, então o conteúdo não é afirmado.
- **Entregue: três mecanismos de modulação, do mais legível ao menos:**
  1. **ganho sobre a leitura do receptor;**
  2. **ganho sobre a taxa de aprendizado;**
  3. **deslocamento do limiar de disparo.**
- **O que medir:** a ablação com o hormônio fixado no basal, comparando três coisas:
  - a latência até a ação que reduz o drive;
  - a taxa de aquisição;
  - a variância entre episódios idênticos.

  Um hormônio que não muda nenhuma das três é parâmetro morto.

### P4: o corpo químico ajuda ou atrapalha o aprendizado?

- **Roijers et al. (2013):** há cenários em que converter vários objetivos num escalar é impossível, inviável ou indesejável. Nesses
  casos, a solução ótima pode ser uma fronteira de Pareto.
  - *Leitura da sessão:* somar os drives é escalarizar. O risco de "um drive dominar" é a consequência esperada de pesos errados, não um
    problema de calibração.
- **A favor de mais drives:** Lewis e Cañamero (2016) mostram que um canal hedônico a mais não degradou o desempenho.
- **Entregue:** com os pesos dos drives fixos, ajustados à mão, o corpo equivale a uma recompensa única de forma complicada, e não há
  ganho. O ganho aparece quando o peso **varia com o estado** (um drive saciado deixa de pesar), como no reforço homeostático de Keramati
  e Gutkin.

### P5: dano, dor, cura e morte (a mais fraca)

- **Bongard, Zykov e Lipson (2006):** dano com consequência funcional, mas permanente, sem cura, dor nem morte.
- **Kuehn e Haddadin:** só o título foi conferido.
- **Não localizado:** trabalho com dano de órgão, cura com custo e morte por falência num agente que aprende, nem sobre "medo
  excessivo" num agente que pode se ferir.
- **Entregue, SEM FONTE** (leitura por analogia):
  - **o órgão:** tem força vital inteira, e o processo dele degrada quando ela cai;
  - **o dano:** subtrai força vital;
  - **a cura:** soma força vital a uma taxa fixa, com custo de energia;
  - **a falência:** o processo para;
  - **a morte:** a falência de um órgão essencial;
  - **a dor:** um químico emitido em proporção ao dano recente.
- **As medidas de "o dano ensinou" × "o dano matou":**
  1. **sobrevivência contra evitação aprendida:** se a sobrevivência sobe sem a ação danosa cair, houve seleção, não aprendizado;
  2. **latência até a primeira evitação,** em episódios de dano, contra quantos danos o pet suporta;
  3. **generalização da evitação** sobre ações não punidas;
  4. **custo de oportunidade da cura:** a fração da vida gasta curando.

### P6: interocepção e automodelo

- **Seth e Friston (2016):** o enquadramento da inferência interoceptiva.
- **Bongard et al. (2006):** o automodelo inferido sem acesso ao estado real, útil depois de o corpo mudar.
- **Entregue:** o automodelo prevê **as leituras dos receptores**, não os químicos. Três avaliações:
  1. **a predição a n passos,** contra a persistência e a média histórica;
  2. **a transferência sob perturbação:** dano a um órgão e o tempo até o erro voltar;
  3. **a utilidade:** a política que consulta o automodelo contra a que não consulta, com a mesma capacidade.

## 3. Divergências e riscos

| risco | força | o que fazer |
|---|---|---|
| Força vital, dano e morte por órgão não estão na fonte primária acessada | alta quanto à ausência; média quanto à conclusão | tratar como desenho próprio inspirado no Creatures |
| Escalarizar os drives com pesos fixos anula o ganho do corpo químico | média-alta (leitura) | pesos que variam com o estado |
| "Combinar drives sem um dominar" pode não ter solução escalar | alta | estudar os pesos, não ajustá-los à mão |
| O prazer desacoplado de necessidade é defensável | média (um estudo, em robô) | apoia o conforto; contradiz "todo drive é falta" |
| O modelo de órgão com dano e cura não tem fonte | nenhuma | não citar como literatura |
| O automodelo pode ser trivialmente bom | inferida | sempre com a linha de base de persistência |

## 4. Lacunas e buscas feitas

**Não localizado:**
- fonte primária do Creatures sobre força vital, dano, cura, energia de reparo ou morte por falência;
- o conteúdo de Grand & Cliff 1998 e do livro *Creation*;
- práticas publicadas de calibração de taxas e meias-vidas em química artificial;
- trabalho com dano de órgão, cura com custo e morte num agente que aprende;
- medo excessivo em agente que pode se ferir;
- Avila-García & Cañamero 2004 e 2005, sem DOI localizado.

**Buscas feitas:** 21 DOIs candidatos resolvidos e uma busca web dirigida.

## 5. BibTeX

```bibtex
@inproceedings{grand1997creatures, author={Grand, Stephen and Cliff, Dave and Malhotra, Anil},
  title={Creatures: artificial life autonomous software agents for home entertainment},
  booktitle={Proceedings of the First International Conference on Autonomous Agents}, year={1997},
  doi={10.1145/267658.267663}, note={resumo lido}}
@article{grand1998creatures, author={Grand, Stephen and Cliff, Dave},
  title={Creatures: Entertainment Software Agents with Artificial Life},
  journal={Autonomous Agents and Multi-Agent Systems}, year={1998}, doi={10.1023/A:1010042522104},
  note={APENAS metadados; conteudo NAO acessado}}
@article{cliff1999creatures, author={Cliff, Dave and Grand, Stephen},
  title={The Creatures Global Digital Ecosystem}, journal={Artificial Life}, year={1999},
  doi={10.1162/106454699568683}, note={resumo lido}}
@article{dittrich2001artificial, author={Dittrich, Peter and Ziegler, Jens and Banzhaf, Wolfgang},
  title={Artificial Chemistries --- A Review}, journal={Artificial Life}, year={2001},
  doi={10.1162/106454601753238636}, note={resumo lido}}
@article{dittrich2007chemical, author={Dittrich, Peter and Speroni di Fenizio, Pietro},
  title={Chemical Organisation Theory}, journal={Bulletin of Mathematical Biology}, year={2007},
  doi={10.1007/s11538-006-9130-8}, note={PDF obtido, nao lido}}
@article{lones2018hormone, author={Lones, John and Lewis, Matthew and Ca{\~n}amero, Lola},
  title={A Hormone-Driven Epigenetic Mechanism for Adaptation in Autonomous Robots},
  journal={IEEE Transactions on Cognitive and Developmental Systems}, volume={10}, number={2}, pages={445--454},
  year={2018}, doi={10.1109/TCDS.2017.2775620}, note={PDF obtido, nao lido}}
@article{lewis2016hedonic, author={Lewis, Matthew and Ca{\~n}amero, Lola},
  title={Hedonic quality or reward? A study of basic pleasure in homeostasis and decision making of a motivated autonomous robot},
  journal={Adaptive Behavior}, year={2016}, doi={10.1177/1059712316666331}, note={resumo lido; PDF obtido}}
@article{canamero2005emotion, author={Ca{\~n}amero, Lola},
  title={Emotion understanding from the perspective of autonomous robots research}, journal={Neural Networks},
  year={2005}, doi={10.1016/j.neunet.2005.03.003}, note={APENAS metadados}}
@inproceedings{lones2014hormonal, author={Lones, John and Lewis, Matthew and Ca{\~n}amero, Lola},
  title={Hormonal Modulation of Development and Behaviour Permits a Robot to Adapt to Novel Interactions},
  booktitle={Proceedings of ALIFE 14}, year={2014}, doi={10.1162/978-0-262-32621-6-ch031}, note={APENAS metadados}}
@article{xu2011recent, author={Xu, Qingzheng and Wang, Lei}, title={Recent advances in the artificial endocrine system},
  year={2011}, doi={10.1631/jzus.C1000044}, note={APENAS metadados}}
@article{marotogomez2023modeling, author={Maroto-G{\'o}mez, M. and Castro-Gonz{\'a}lez, {\'A}. and Malfaz, M. and
  Fern{\'a}ndez-Rodicio, E. and Salichs, M. {\'A}.},
  title={Modeling Neuroendocrine Autonomic Responses in Embodied Autonomous Robots}, journal={Advanced Intelligent Systems},
  volume={5}, pages={2200288}, year={2023}, doi={10.1002/aisy.202200288}, note={resumo lido; PDF obtido}}
@article{roijers2013survey, author={Roijers, Diederik M. and others},
  title={A Survey of Multi-Objective Sequential Decision-Making}, journal={Journal of Artificial Intelligence Research},
  year={2013}, doi={10.1613/jair.3987}, note={resumo lido; PDF obtido}}
@article{hulme2019neurocomputational, author={Hulme, Oliver J. and Morville, Tobias and Gutkin, Boris},
  title={Neurocomputational theories of homeostatic control}, journal={Physics of Life Reviews}, year={2019},
  doi={10.1016/j.plrev.2019.07.005}, note={PDF obtido, nao lido}}
@article{juechems2019where, author={Juechems, Keno and Summerfield, Christopher}, title={Where Does Value Come From?},
  journal={Trends in Cognitive Sciences}, year={2019}, doi={10.1016/j.tics.2019.07.012}, note={APENAS metadados}}
@article{bongard2006resilient, author={Bongard, Josh and Zykov, Victor and Lipson, Hod},
  title={Resilient Machines Through Continuous Self-Modeling}, journal={Science}, year={2006},
  doi={10.1126/science.1133687}, note={resumo lido}}
@article{kuehn2016artificial, author={Kuehn, Johannes and Haddadin, Sami},
  title={An Artificial Robot Nervous System To Teach Robots How To Feel Pain And Reflexively React To Potentially Damaging Contacts},
  journal={IEEE Robotics and Automation Letters}, year={2016}, doi={10.1109/LRA.2016.2536360}, note={APENAS metadados}}
@article{seth2016active, author={Seth, Anil K. and Friston, Karl J.},
  title={Active interoceptive inference and the emotional brain}, journal={Philosophical Transactions of the Royal Society B},
  year={2016}, doi={10.1098/rstb.2016.0007}, note={resumo lido; texto completo em disco}}
```

## 6. Pistas: NÃO verificadas

| pista | onde | pergunta |
|---|---|---|
| Avila-García & Cañamero 2004, *Using hormonal feedback to modulate action selection in a competitive scenario* | SAB'04, pp. 243-252, sem DOI | P3 |
| Avila-García & Cañamero 2005, *Hormonal modulation of perception in motivation-based action selection architectures* | AISB'05, pp. 9-16, sem DOI | P3 |
| Stradner, Hamann, Schmickl & Crailsheim 2009, *Analysis and Implementation of an Artificial Homeostatic Hormone System* | IROS, `10.1109/IROS.2009.5354056` | P3 |
| Guerrero-Rosado & Verschure 2021, *Robot regulatory behaviour based on fundamental homeostatic and allostatic principles* | Procedia CS 190:292-300 | P4 |
| Khan & Cañamero 2018 | Multimodal Technol. Interact. 2:67, `10.3390/mti2040067` | P3 |
| Grand, S., *Creation: Life and How to Make It* (2000) | conteúdo nunca verificado | P1 |
| Pendências das rodadas anteriores | `10.1016/j.anbehav.2018.05.024`, `10.1038/s41598-019-51652-5`, `10.1086/605370` | — |
