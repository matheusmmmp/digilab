# Síntese da triagem de literatura de 2026-10-30 (C0 da V3)

Missão C0 da trilha C da V3 (`docs/TAREFA_V3_LITERATURA.md`). Escrita em 2026-10-30 pelo worker da C0 (Claude Code, Opus 5.5).

**O que é este documento.** A síntese, para dentro do repositório, de uma triagem de literatura feita fora dele em 2026-10-30
(`triagem_texto_completo/`, ao lado das worktrees: o relatório, a planilha de 138 registros, os pareceres por lote e a análise contra o
projeto). Os PDFs e o texto dos artigos não entram. As conclusões, as limitações L1–L11 e as recomendações R1–R7 são as da triagem,
reescritas aqui só com as fontes que a C0 verificou.

**Tudo aqui é PROPOSTO.** A triagem é uma leitura cruzada feita por IA, não uma decisão. Nenhuma conclusão daqui muda decisão já tomada:
o bandit continua congelado, a pergunta do dono continua encerrada e o cérebro A continua como linha de base.

**Como ler as citações.** Cada fonte citada abaixo está em `v3c0_referencias_verificadas.csv` (as novas) ou nas tabelas antigas de
`docs/referencias/`. A coluna `o_que_sustenta` diz até onde cada uma vai e por qual leitura (texto completo, tese ou versão-irmã,
resumo). O que não foi verificado aparece como **pista, SEM FONTE**, e não sustenta frase nenhuma.

## 1. A verificação (o passo 1 da C0)

Feita em 2026-10-30 na API do Crossref (DOI resolve, título, autores, ano, veículo e páginas conferidos, sem `update-to` nem
`updated-by`) e, para os sem DOI, no registro bibliográfico independente (OpenAlex, Semantic Scholar com a chave do DBLP, repositório da
Univ. de Hertfordshire). O registro bruto está em `v3c0_verificacao_crossref.json`; a tabela, em `v3c0_referencias_verificadas.csv`; o
BibTeX, em `v3c0_referencias.bib`.

| fonte | status | leitura que sustenta o conteúdo |
|---|---|---|
| Gadanho e Hallam 2001, *Adaptive Behavior* | VERIFICADA | tese de 1999 (versão-irmã) e resumo |
| Ho, Dautenhahn e Nehaniv 2003, IVA (LNCS) | VERIFICADA | só a tese de 2005 (caps. 3–4) |
| Ho, Dautenhahn, Nehaniv e te Boekhorst 2004, IAS-8 | VERIFICADA (sem DOI) | texto completo (pela triagem) e resumo |
| Ho, Dautenhahn e Nehaniv 2005, CEC | VERIFICADA | texto completo (pela triagem) |
| Ho 2005, tese (DOI do DataCite) | VERIFICADA | texto completo (pela triagem) |
| Ho, Dautenhahn e Nehaniv 2006, AISB | VERIFICADA (sem DOI), cinza | existência só; sem parecer de conteúdo |
| Ho, Dautenhahn e Nehaniv 2008, *Connection Science* | VERIFICADA | só a tese de 2005 (versão-irmã) |
| Khan e Cañamero 2018, *MTI* | VERIFICADA | texto completo (pela triagem) e resumo |
| Yoshida et al. 2024, *Neural Networks* | VERIFICADA | texto completo (pela triagem) |
| Strannegård et al. 2017, AGI (LNCS) | VERIFICADA | só a versão de 2018 |
| Strannegård et al. 2018, *JAGI* | VERIFICADA | texto completo (pela triagem) e resumo |
| Giannakakis et al. 2023, ALIFE | VERIFICADA | versão do arXiv |
| Giannakakis et al. 2024, *Artificial Life* (a triagem diz 2025) | VERIFICADA | preprint do arXiv e resumo |
| Goertzel et al. 2008, AGI-08 | VERIFICADA (sem DOI) | cópia do autor (pela triagem) |
| Francis, Mehta e Ram 2009 (PEPE) | VERIFICADA | versão dos autores e resumo |
| Francis, Mehta e Ram 2011 (a reimpressão) | **NÃO LOCALIZADA** | o DOI dá 404; não citar, citar o de 2009 |
| Blumberg et al. 2002, *ACM TOG* / SIGGRAPH | VERIFICADA | texto completo (pela triagem) e resumo |
| Yoon, Blumberg e Schneider 2000, AGENTS | VERIFICADA | texto completo (pela triagem) |
| Yoon, Burke, Blumberg e Schneider 2000, AAAI | VERIFICADA (sem DOI) | texto completo (pela triagem) |
| Curtis et al. 2022, MIG | VERIFICADA | texto completo (pela triagem) |
| Maroto-Gómez et al. 2025, *Electronics* | VERIFICADA | texto completo (pela triagem) e resumo |
| Maroto-Gómez et al. 2023, *Adv. Intell. Syst.* | VERIFICADA | só o resumo |

**A ressalva que vale para a tabela inteira.** A C0 conferiu os metadados e, quando o Crossref tem, o resumo. Quem leu o texto completo
foi a triagem (uma IA, numa sessão anterior, sem revisão humana dos pareceres). Para citar um número de uma dessas fontes num texto, ler
o artigo.

## 2. As conclusões da triagem

1. **A combinação "corpo com homeostase, aprendizado em vida e memória episódica num agente" já foi publicada várias vezes.** Creatures
   (Grand e Cliff 1998, `10.1023/A:1010042522104`), Gadanho e Hallam (2001, `10.1177/105971230200900102`), a linha de Ho, Dautenhahn e
   Nehaniv (2003–2008; a tese, `10.18745/th.14271`) e Goertzel et al. (2008, sem DOI). A triagem acrescenta Zamin (Halavati et al.
   2004) e a linha Rity do KAIST (2004–2008); essas duas são **pistas, SEM FONTE**, não verificadas aqui. Não serve como diferencial: a
   regra nova de `REGRAS_CITACAO_DIGILAB.md` (a 9) proíbe dizer que é novo.
2. **Quase nenhum desses trabalhos mede a contribuição de cada mecanismo com controle.**
   - Com controle: Gadanho e Hallam (ablação de um papel da emoção por vez, com IC95%, pela tese); Khan e Cañamero (2018,
     `10.3390/mti2040067`; 7 200 corridas, ANOVA); Ho et al. (arquiteturas de memória contra o agente reativo, 10 a 50 execuções por
     condição, **sem teste de hipótese**); Strannegård et al. (2018, `10.2478/jagi-2018-0002`; uma rodada por condição).
   - Sem controle: Creatures, Blumberg et al. (2002, `10.1145/566654.566597`), Yoon et al. (2000, `10.1145/336595.337537`), Goertzel et
     al. e o PEPE (Francis, Mehta e Ram 2009, `10.4018/978-1-60566-354-8.ch020`). A triagem põe no mesmo grupo Fujita (Sony, 2009), Lim
     et al. (FAtiMA-PSI, 2012) e PEPA (2026): **pistas, SEM FONTE**.
   - O que o Digilab pode mostrar e esses não mostraram: **teste causal com braço de controle, num pet persistente, com replay
     determinístico.** Isso descreve o método do projeto; **não é alegação de novidade**, e a ausência de outro trabalho assim é
     resultado de uma busca, não prova.
3. **Onde o aprendizado em vida funciona nessa literatura, ele quase sempre vem de memória ou de planejamento, não de um valor aprendido
   do zero para navegar.** Ho (a memória que guia a volta ao recurso) e Strannegård (os nós criados por surpresa). Yoshida et al. (2024,
   `10.1016/j.neunet.2024.106379`) só chegam a comportamento integrado com treino offline massivo e reinício a cada morte. A triagem cita
   também Burke e Blumberg (2002, a contingência temporal): **pista, SEM FONTE**.
4. **O valor de um mecanismo depende do ambiente.** Khan e Cañamero: a modulação pela oxitocina ajuda num mundo e atrapalha no outro.
   Giannakakis et al. (2023, `10.1162/isal_a_00606`): aprender na vida só compensa com variabilidade intermediária e recompensa confiável.
   Ho (CEC 2005, `10.1109/cec.2005.1554734`; e a tese): a memória de rota (STM) falha quando o mundo muda com as estações; a memória de
   eventos (LTM) resiste.
5. **Guardar não basta: a memória precisa ser buscada para decidir.** No PEPE, guardar casos não mudou nada até haver um reconhecedor
   que busca episódios o tempo todo. Em Ho (a tese), a memória só ganhou do agente reativo quando passou a lembrar também os eventos
   negativos.
6. **A busca da triagem (677 registros) teve uma lacuna:** a linha de Ho sobre sobrevivência com memória (IVA 2003, IAS-8 2004, CEC
   2005, AISB 2006, *Connection Science* 2008 e a tese) não entrou; só entraram os trabalhos narrativos dela. As strings da seção 5
   foram rodadas para medir esse buraco.

## 3. As limitações L1–L11: a literatura × o Digilab

A coluna "o Digilab hoje" é a leitura da análise da triagem sobre `docs/PAINEL_V2.md` (2026-10-24), `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`,
`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md` e `docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md`. A C0 não a reconferiu contra o código; os
números do projeto ficam nesses documentos e não são repetidos aqui.

| # | limitação vista na literatura | o Digilab hoje (pela análise) | fonte verificada | o que a literatura sugere (PROPOSTO) |
|---|---|---|---|---|
| L1 | memória guardada que não decide | sim, em grande parte: a memória autobiográfica não afeta decisões hoje; só o N6 (a fruta) e o lugar lembrado do M-MEM decidem | PEPE (2009); Ho, a tese | recuperar a cada decisão, pela pista do contexto (a ME-2 já recomenda); medir registrado → codificado → recuperado → causal |
| L2 | memória de lugar num mundo sem regularidade | sim: no longe a ração cai numa direção sorteada, e todos os braços falham | Ho, CEC 2005 e a tese; Giannakakis 2023 | o longe atual testa um caso em que nenhum aprendiz de lugar deveria ganhar; falta um cenário com regularidade (a C1) |
| L3 | decidir de novo a cada passo | sim: o sorteio refaz a escolha a cada decisão; a L-2 (suspender a intenção no cochilo) fechou negativa | Gadanho e Hallam (pela tese) | redecidir só quando o corpo ou o afeto muda de forma significativa; é diferente da L-2 (a C3) |
| L4 | crédito na escala da ação primitiva | sim: a janela imediata ensina a comer e a poupar energia, não a procurar | Gadanho e Hallam (pela tese) | crédito na escala da intenção ou da opção composta (a C2; reabre a DX-6 como hipótese) |
| L5 | efeito do modulador que troca de sinal com o ambiente | em parte: o projeto já separa perto, comedouro e longe | Khan e Cañamero 2018 | prever o sinal por ambiente nos planos; nos hormônios (J10), três níveis de dificuldade |
| L6 | medir só a refeição, não a viabilidade do corpo | sim: o G-MVP é por episódio de fome e por ração | Ho (a tese: tempo fora da faixa); Strannegård 2018 (vitalidade = mínimo das necessidades); Khan e Cañamero | medida secundária descritiva: fração do tempo com alguma variável fora da faixa e a menor necessidade, do replay (a C5) |
| L7 | aprendizado em vida que perde do inato | sim: no J1 o P1 perde do instinto | Yoshida 2024; Strannegård 2018 | [HIPÓTESE] o ganho em vida vem de memória e planejamento, não de mais variantes de valor aprendido para navegar |
| L8 | interação humana anedótica ou ausente | sim: só donos simulados | Yoon et al. 2000 (AAAI, o Sydney); Maroto-Gómez 2025 (o Mini); PEPE; Curtis 2022 (estudo com usuários sem controle); Anderson et al. 2019 (`10.24963/ijcai.2019/184`, já na tabela antiga) | depois do modular no jogo, um estudo pequeno de legibilidade (R7). Não reabre a pergunta do dono. A lição do Cobot (quem está satisfeito para de dar retorno) é **pista, SEM FONTE** |
| L9 | persistência não testada | não: event sourcing e vida única refeita pelo log | Maroto-Gómez 2025 (não testa); Yoshida 2024 (reinicia a cada morte) | ponto forte; falta a consolidação entre dias (a etapa M3 da memória) |
| L10 | trocar memória entre agentes não ajuda sem corrigir a perspectiva | a testar (J7, degrau 1) | Ho et al. 2004 (IAS-8) e a tese: o "problema do deslocamento" | o plano do J7 deve prever a tradução de perspectiva, ou esperar que copiar o episódio cru falhe |
| L11 | avaliação sem controle | não: gates com plano antes, ablações, Holm, validação única | a maioria das fontes acima | ponto forte e o eixo mais defensável, **sem alegar novidade** |

## 4. As recomendações R1–R7 (PROPOSTO; o plano da V3 já as transformou em missões)

| R | o quê | fonte verificada | missão da V3 |
|---|---|---|---|
| R1 | antes do hábito, um cenário do longe com regularidade (lugares fixos), com a previsão escrita antes: o MEM deveria ganhar lá e não no longe sorteado | Ho (CEC 2005, a tese); Giannakakis 2023 | C1 (`docs/TAREFA_V2_LONGE_REGULAR.md`) |
| R2 | no hábito, um braço com o crédito na intenção ou na opção composta contra o crédito no passo | Gadanho e Hallam 2001 (lido pela tese) | C2 |
| R3 | redecidir por evento: a intenção só é refeita quando um receptor cruza um limiar ou surge um evento sensorial novo; medir sem contar a retomada da busca como troca (a lição LP-2) | Gadanho e Hallam 2001 (lido pela tese) | C3 |
| R4 | três entradas para a memória autobiográfica: na ME-1, a significância é a variação do corpo; na ME-3, guardar o mais significativo de cada categoria; na validação, o braço "REL sem os episódios negativos"; e, do PEPE, a recuperação a cada decisão | Ho, a tese e *Connection Science* 2008 (pela tese); PEPE 2009 | C4 |
| R5 | a viabilidade do corpo como medida secundária descritiva, do replay das vidas gravadas | Ho (a tese); Strannegård 2018; Khan e Cañamero 2018 | C5 |
| R6 | verificar as fontes (o passo 1 desta C0) e rodar as strings que faltaram (a seção 5) | — | C0 |
| R7 | mais tarde: a perspectiva no J7; o desenho de Khan e Cañamero nos hormônios; um estudo pequeno de legibilidade, com o questionário de Curtis et al. como modelo | Ho 2004 (IAS-8) e a tese; Khan e Cañamero 2018; Curtis 2022; Anderson 2019 | backlog (PLANO_V3, 2.3) |

**O custo de errar, por recomendação, segue o da análise da triagem.** Na R1, se o modular falhar também no cenário com regularidade,
a falha está na decisão ou no crédito, não no cenário, e isso já informa. Nas R2 e R3, a fonte é uma só e foi lida pela tese: a
hipótese tem fonte, o tamanho do efeito não.

## 5. As strings que faltaram (R6): consultas, contagens e pistas

**Feito em 2026-10-30** nas APIs do OpenAlex (`/works?search=`, até 200 itens por relevância), do Semantic Scholar
(`/paper/search/bulk`) e do arXiv (`/api/query`, até 100). O registro, com cada consulta, a contagem e os itens devolvidos, está em
`v3c0_buscas_r6.json`. Sem captcha contornado nem site pago; o dblp.org respondeu com um desafio antibot e não foi usado.

| # | string | OpenAlex | Semantic Scholar | arXiv |
|---|---|---|---|---|
| Q1 | "autobiographic agent" | 67 | 24 | 0 |
| Q2 | "animat" AND (homeostasis OR survival) AND memory | 641 | 0 (a forma booleana); parciais: "animat memory" 53, "animat survival" 25, "animat homeostasis" 5 | 0 (o OR entre parênteses não funcionou; as duas formas sem OR também deram 0) |
| Q3 | "artificial creature" AND "episodic memory" | 30 | 2 | 0 |
| Q4 | "emotion" AND "reinforcement" AND "robot" AND survival | 3 630 | 6 | 0 (sem "survival": 25) |

**Como ler as contagens.** A busca do OpenAlex casa palavras com variação de forma e ordena por relevância, então 641 e 3 630 incluem
muito ruído (na Q4, quase tudo é reconhecimento de emoção e psicologia); só os 200 primeiros de cada uma foram olhados, e só pelo título.
O Semantic Scholar e o arXiv são estritos e trazem pouco. Ausência de resultado em busca por palavras-chave é evidência fraca.

**A lacuna da triagem se confirma:** a Q1 traz a linha de Ho inteira já no topo (IVA 2003, IAS-8 2004, CEC 2005, AISB 2006, *Connection
Science* 2008, a tese), que a busca original não tinha. A Q4 traz Gadanho e Hallam 2001 e a tese de Gadanho (1999) entre os primeiros.

**Os achados novos relevantes (pistas, NÃO VERIFICADAS, SEM FONTE).** Nenhum deles está entre os 138 registros levados ao texto completo
na triagem, salvo onde dito; a planilha dos 677 da primeira triagem não estava na pasta, e por isso não foi possível dizer se algum foi
excluído lá.

- **Ainda da linha de Ho e Dautenhahn:** Ho, Avila-García e Nehaniv, CEC 2005 (seleção de ação no mesmo ambiente, citado pela tese); Ho
  e Watson 2006 (LNCS), conhecimento autobiográfico para personagens críveis, e Ho et al., ICDL 2007 (o modelo AMIA); Ho et al., RO-MAN 2009 (memória para companheiros virtuais e robóticos com
  migração e interação longa); os textos teóricos de Nehaniv e Dautenhahn (1997–1999) que definem o agente autobiográfico. O RO-MAN 2009
  é o mais próximo do pet persistente.
- **Corpo, motivação e emoção com aprendizado:** Savage 2000, revisão de motivação em criaturas artificiais (*Connection Science*);
  Avila-García e Cañamero 2005, modulação hormonal da percepção na seleção de ação; a tese de O'Bryne 2013 (Hertfordshire), emoções e
  seleção de ação por motivação em ambientes dinâmicos; Moerland, Broekens et al. 2017, revisão de emoção em agentes de aprendizado por
  reforço (*Machine Learning*); Kırtay et al. 2019, emoção como regulação de energia (*Adaptive Behavior*); Maroto-Gómez et al. 2023,
  modelo motivacional por funções biológicas artificiais (*Memetic Computing*); Awais et al. 2022, Q-learning com neurotransmissores e
  tempo de sobrevivência; Khan 2025 (ALIFE), alostase social.
- **Homeostase no aprendizado por reforço profundo:** Yoshida 2017, agente homeostático para ambiente geral (*JAGI*); Yoshida et al.
  2024, comportamento nutricional de longo prazo (*PNAS Nexus*).
- **Memória episódica em criaturas artificiais:** Kuppuswamy, Cho e Kim 2006 (já na triagem como S0598, sem texto; a Q3 confirma o DOI
  do registro); Martin e Rosales 2021 (já na triagem como S0344); Borges e Reis 2014, estresse, memória e aprendizagem em animais
  simulados (trabalho brasileiro); Chang e Tan 2017 (IJCAI), memória episódica espaço-temporal; a tese de Nuxoll 2007 (memória episódica
  em agentes).

Para citar qualquer um desses, ele passa antes pelo passo 1 (Crossref ou registro independente) e entra numa tabela `*_verificadas.csv`.

## 6. As ressalvas que a C0 carrega

- **Versões-irmãs.** Quatro fontes de peso foram lidas pela triagem em outra versão: Gadanho (a tese de 1999, não o artigo de 2001), Ho
  2008 (a tese de 2005, não o artigo), Zamin (o Zamin II) e Nahodil (a dissertação). Das quatro, só as duas primeiras estão verificadas
  aqui. Para citar um número, ler o artigo publicado. O OpenAlex aponta uma cópia do autor do artigo de Ho 2008 no repositório da
  Univ. de Hertfordshire, o que tornaria a leitura possível sem acesso pago (não aberta nesta C0).
- **Ho et al. não fazem teste de hipótese** nas comparações entre arquiteturas, e a comparação principal tem 10 execuções. Servem como
  direção, não como tamanho de efeito.
- **Os critérios da triagem foram inferidos** das justificativas da primeira triagem, não lidos de um protocolo. Se a camada A exigir
  avaliação, vários itens (Creatures, Goertzel, Fujita, Burke e Blumberg) descem de nível.
- **Nove leituras da triagem foram parciais** (tese ou versão-irmã), e 53 dos 138 registros não tiveram texto completo (parecer só pelo
  resumo). Os 539 excluídos na primeira triagem não foram relidos.
- **A C0 não releu os artigos.** O que está em "o que sustenta" além do resumo do Crossref vem dos pareceres da triagem.

## 7. Fora desta síntese

A skill `literatura-digilab` (fica fora do repositório; o texto proposto para ela vai no corpo do PR); a revisão da
`docs/ESPEC_DIGIBRAIN_MODULAR.md` com as marcas [MECANISMO], [HIPÓTESE] e [EXISTE] (o fim da trilha C); a verificação das pistas da
seção 5; a leitura dos artigos publicados no lugar das versões-irmãs.
