# Referências: conversa do pet por LLM com fala presa aos fatos

Data: 2026-11-06. Frente: o Digimon conversa com o jogador por LLM (hoje gemma2:9b local no Ollama, RTX 2060; alternativa: API do Claude), sem afrouxar a trava: a fala só alega causa, memória e estado que o registro do pet sustenta (bloco de FATOS com identificadores + verificador de afirmações sem fato).

Leia antes:

- **Status.** VERIFICADA = DOI resolvido no Crossref ou id resolvido na API do arXiv, com título, autores, ano e veículo conferidos.
- **Limite da conferência.** O conteúdo foi conferido sobre os metadados e o resumo, não sobre o texto completo. A coluna "o que sustenta" diz só o que o resumo afirma.
- **Veículo.** Quando o arXiv é a única fonte resolvida, o veículo registrado é "arXiv" e a versão publicada não foi conferida (ver a tabela no fim).
- **Repetições.** Nada desta lista estava em `docs/referencias/referencias_verificadas.csv` (79 linhas, todas de ALife, bandit, personalidade animal etc.). Park et al. 2023 aparecia só como "pista" em `docs/futuro/cognicao_social.md`; aqui ficou verificado.
- **Novidade.** Nenhuma alegação de novidade do Digilab é feita ou sustentada por estas referências.
- **Peso.** "Núcleo" = mais útil para a frente; "apoio" = cita se precisar.

---

## 1. Agentes com memória e reflexão

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Park, O'Brien, Cai, Morris, Liang & Bernstein (2023).** Generative Agents: Interactive Simulacra of Human Behavior. UIST '23 (ACM). — núcleo | 10.1145/3586183.3606763 · arXiv:2304.03442 | VERIFICADA | Arquitetura que guarda o registro completo das experiências do agente em linguagem natural, sintetiza reflexões de nível mais alto e as recupera para planejar. Na ablação, observação, planejamento e reflexão contribuem cada um para a credibilidade. | Recuperar do registro autobiográfico do pet só os FATOS relevantes ao turno. Uma "reflexão" só entra se apontar para os ids dos eventos de origem. |
| **Packer, Wooders, Lin, Fang, Patil, Stoica & Gonzalez (2023).** MemGPT: Towards LLMs as Operating Systems. arXiv. — núcleo | arXiv:2310.08560 | VERIFICADA (veículo: arXiv) | Gestão de contexto virtual em camadas de memória (rápida/lenta), inspirada em sistemas operacionais. No chat de várias sessões, permite agentes que lembram e evoluem em interações longas. | Separar memória de trabalho (bloco de FATOS no prompt, curto) de memória arquivada (log do pet), com busca explícita. Importa pela janela curta do gemma2:9b. |
| **Shinn, Cassano, Berman, Gopinath, Narasimhan & Yao (2023).** Reflexion: Language Agents with Verbal Reinforcement Learning. arXiv. — apoio | arXiv:2303.11366 | VERIFICADA (veículo: arXiv) | O agente reflete verbalmente sobre o retorno da tarefa e guarda essa reflexão num buffer episódico para decidir melhor depois, sem mudar pesos. | Pouco uso direto, porque quem decide é o DigiBrain, não o LLM. Serve no máximo para guardar entre sessões as rejeições do verificador ("frase X barrada por falta de fato") e evitar repeti-las. |

## 2. Consistência de persona em diálogo

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Zhang, Dinan, Urbanek, Szlam, Kiela & Weston (2018).** Personalizing Dialogue Agents: I have a dog, do you have pets too? ACL 2018. — núcleo | 10.18653/v1/P18-1205 · arXiv:1801.07243 | VERIFICADA | Condicionar o modelo a frases de perfil torna o chit-chat mais engajador e ataca a falta de personalidade consistente. Também treina o agente a puxar tópicos pessoais do parceiro. | Perfil do pet em frases curtas (espécie, temperamento, gostos) como parte fixa do prompt, separado dos FATOS do momento. |
| **Welleck, Weston, Szlam & Cho (2019).** Dialogue Natural Language Inference. ACL 2019. — núcleo | 10.18653/v1/P19-1363 · arXiv:1811.00671 | VERIFICADA | Trata a consistência do agente como inferência (NLI). Um modelo treinado no Dialogue NLI melhora a consistência, medida por avaliação humana e automática. | Dá base ao verificador: cada afirmação da fala é classificada como apoiada, contradita ou neutra contra os FATOS. Contradita ou neutra sobre causa/memória/estado é barrada. |
| **Kim, Kim & Kim (2020).** Will I Sound Like Me? Improving Persona Consistency in Dialogues through Pragmatic Self-Consciousness. EMNLP 2020. — apoio | 10.18653/v1/2020.emnlp-main.65 · arXiv:2004.05816 | VERIFICADA | Mesmo os melhores agentes com persona são insensíveis a palavras contraditórias. Um "ouvinte imaginário" (RSA) reduz contradições sem rótulos NLI extras. | Gerar 2–3 candidatas e escolher a que o verificador e o perfil aprovam (reranqueamento), em vez de aceitar a primeira saída. |
| **Li, Liu, Bashkansky, Bau, Viégas, Pfister & Wattenberg (2024).** Measuring and Controlling Instruction (In)Stability in Language Model Dialogs. arXiv. — núcleo | arXiv:2402.10962 | VERIFICADA (veículo: arXiv) | Mede deriva significativa das instruções do system prompt em até oito rodadas de conversa (LLaMA2-chat-70B, GPT-3.5) e a liga ao decaimento da atenção em trocas longas. | Reinjetar perfil e regras a cada turno (perto do fim do prompt), não só no início da sessão. Medir a deriva em conversas de 8+ turnos. |

## 3. Role-play de personagem com LLM

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Shanahan, McDonell & Reynolds (2023).** Role play with large language models. Nature. — núcleo | 10.1038/s41586-023-06647-8 | VERIFICADA (resumo pelo Europe PMC; o Crossref não traz resumo) | Descreve o comportamento do agente de diálogo como role-play, para usar termos de psicologia popular sem atribuir ao modelo características humanas que ele não tem. Aplica isso a (aparente) engano e (aparente) autoconsciência. | Enquadramento para o texto: o LLM interpreta o personagem; quem decide é o DigiBrain. A trava existe porque o "ator" inventa motivos que o pet não teve. |
| **Shao, Li, Dai & Qiu (2023).** Character-LLM: A Trainable Agent for Role-Playing. EMNLP 2023. — apoio | 10.18653/v1/2023.emnlp-main.814 · arXiv:2310.10158 | VERIFICADA | Treina modelos com o perfil, as experiências e os estados emocionais de um personagem, transformados em "experiências". Avalia por entrevista se o agente lembra do personagem e de suas experiências. | Caminho de ajuste fino futuro: diálogos montados a partir dos logs reais dos pets. Avaliar por "entrevista" com perguntas cuja resposta está no log. |
| **Wang, Peng, Que, Liu et al. (2024).** RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of Large Language Models. Findings of ACL 2024. — núcleo | 10.18653/v1/2024.findings-acl.878 · arXiv:2310.00746 | VERIFICADA | Quatro etapas: perfil de 100 papéis, extração de conhecimento do papel (Context-Instruct), prompting para imitar o estilo de fala (RoleGPT) e ajuste fino condicionado ao papel (RoCIT) para modelos abertos. | Separar estilo de fala (exemplos no prompt) de conhecimento do papel (FATOS). RoCIT é o modelo de ajuste fino leve num modelo aberto pequeno. |
| **Chen, Wang, Xu, Yuan et al. (2024).** From Persona to Personalization: A Survey on Role-Playing Language Agents. arXiv. — apoio | arXiv:2404.18231 | VERIFICADA (veículo: arXiv) | Survey de agentes de role-play (RPLAs), com aplicações como companheiros emocionais, jogos e personagens interativos. | Mapa da área para a seção de trabalho relacionado. Não sustenta decisão técnica sozinho. |

## 4. Memória de longo prazo e recuperação em conversa longa

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Xu, Szlam & Weston (2022).** Beyond Goldfish Memory: Long-Term Open-Domain Conversation. ACL 2022. — núcleo | 10.18653/v1/2022.acl-long.356 · arXiv:2107.07567 | VERIFICADA | Dataset multissessão (MSC). Modelos treinados em conversa curta vão mal. Métodos com recuperação e com resumo/recordação das conversas anteriores superam o encoder-decoder padrão. | Resumo da sessão anterior gravado no log ao fim da conversa e recuperado na próxima. É a memória entre sessões, ligada à autobiográfica do pet. |
| **Maharana, Lee, Tulyakov, Bansal, Barbieri & Fang (2024).** Evaluating Very Long-Term Conversational Memory of LLM Agents. ACL 2024. — núcleo | 10.18653/v1/2024.acl-long.747 · arXiv:2402.17753 | VERIFICADA | LoCoMo: conversas de ~300 turnos em até 35 sessões, ancoradas em grafos temporais de eventos. LLMs têm dificuldade com dinâmicas temporais e causais de longo alcance; contexto longo ou RAG ajudam, mas ficam abaixo do humano. | Testar perguntas temporais e causais ("por que você não comeu ontem?") com resposta conhecida no log. Usar como bateria de avaliação, não confiar no modelo para isso. |
| **Zhong, Guo, Gao, Ye & Wang (2024).** MemoryBank: Enhancing Large Language Models with Long-Term Memory. AAAI 2024. — apoio | 10.1609/aaai.v38i17.29946 · arXiv:2305.10250 | VERIFICADA | Memória de longo prazo para LLMs que esquece e reforça por tempo e importância (inspirada na curva de Ebbinghaus). Mostrada num companheiro de longo prazo (SiliconFriend). | O esquecimento da fala deve seguir a memória do próprio pet (o que o DigiBrain reteve), não uma curva à parte no LLM. A referência mostra a alternativa a não seguir. |
| **Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni & Liang (2024).** Lost in the Middle: How Language Models Use Long Contexts. TACL. — núcleo | 10.1162/tacl_a_00638 · arXiv:2307.03172 | VERIFICADA | O desempenho cai quando a informação relevante fica no meio do contexto e costuma ser melhor no início ou no fim, mesmo em modelos de contexto longo. | Bloco de FATOS curto, posto no fim do prompt (logo antes da fala do jogador). Não despejar o log inteiro. |

## 5. Avaliação de diálogo: humana e por juiz LLM

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Li, Weston & Roller (2019).** ACUTE-EVAL: Improved Dialogue Evaluation with Optimized Questions and Multi-turn Comparisons. arXiv. — núcleo | arXiv:1909.03087 | VERIFICADA (veículo: arXiv) | O par isolado de um turno e o Likert multi-turno têm falhas sérias. Propõe comparar dois diálogos inteiros, com o juiz olhando um só falante, e perguntas otimizadas para robustez entre anotadores. | Avaliação cega pareada: Matheus compara duas conversas inteiras (gemma vs. Claude, com e sem exemplos) com uma pergunta fixa ("qual pet parece mais vivo?"). |
| **Zheng, Chiang, Sheng, Zhuang et al. (2023).** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. arXiv. — núcleo | arXiv:2306.05685 | VERIFICADA (veículo: arXiv) | Juízes LLM fortes chegam a mais de 80 % de concordância com preferências humanas, o mesmo nível entre humanos. Documenta vieses de posição, verbosidade e autopromoção. | Juiz LLM só como triagem barata entre variantes de prompt. A decisão final fica na avaliação humana pareada. |
| **Wang, Li, Chen, Cai et al. (2024).** Large Language Models are not Fair Evaluators. ACL 2024. — núcleo | 10.18653/v1/2024.acl-long.511 · arXiv:2305.17926 | VERIFICADA | O ranking do juiz LLM muda só com a troca da ordem das respostas. Propõe calibração (várias evidências, troca de posição, humano no circuito). | Todo julgamento pareado roda nas duas ordens. Desempates vão ao humano. |
| **Liu, Iter, Xu, Wang, Xu & Zhu (2023).** G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. EMNLP 2023. — apoio | 10.18653/v1/2023.emnlp-main.153 · arXiv:2303.16634 | VERIFICADA | Métricas por referência (BLEU/ROUGE) correlacionam pouco com o julgamento humano. Um LLM com cadeia de raciocínio e formulário melhora o alinhamento. | Se usar juiz, dar critérios escritos (fidelidade aos FATOS, voz do personagem, iniciativa) em vez de uma nota única. |

## 6. Iniciativa e proatividade

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Deng, Lei, Lam & Chua (2023).** A Survey on Proactive Dialogue Systems: Problems, Methods, and Prospects. IJCAI 2023. — núcleo | 10.24963/ijcai.2023/738 · arXiv:2305.02750 | VERIFICADA | Proatividade como capacidade do agente de conduzir a conversa rumo a alvos ou objetivos do lado do sistema; panorama de problemas e métodos. | O "alvo" de cada fala proativa vem do estado do pet (fome, tédio, evento recente no log), nunca de um tema inventado pelo LLM. |
| **Deng, Liao, Chen, Wang, Lei & Chua (2023).** Prompting and Evaluating Large Language Models for Proactive Dialogues: Clarification, Target-guided, and Non-collaboration. Findings of EMNLP 2023. — núcleo | 10.18653/v1/2023.findings-emnlp.711 · arXiv:2305.13626 | VERIFICADA | LLMs chutam respostas para pedidos ambíguos e falham em recusar. Propõe o Proactive Chain-of-Thought (planejamento de objetivo antes da resposta). | Quando falta fato, o pet pergunta ou diz que não sabe, em vez de inventar. Isso é um "pedido de esclarecimento" no lugar da alegação barrada. |
| **Deng, Liao, Zheng, Yang & Chua (2024).** Towards Human-centered Proactive Conversational Agents. SIGIR 2024 (perspectiva). — apoio | 10.1145/3626772.3657843 | VERIFICADA (resumo pelo Semantic Scholar; o Crossref não traz resumo) | Sem desenho cuidadoso, agentes proativos parecem intrusivos. Propõe uma taxonomia em Inteligência, Adaptatividade e Civilidade. | Limitar a frequência de falas espontâneas (cooldown, horário de sono do pet) e medir se o jogador acha intrusivo. |
| **Tang, Zhao, Xiong, Liang, Xing & Hu (2019).** Target-Guided Open-Domain Conversation. ACL 2019. — apoio | 10.18653/v1/P19-1565 · arXiv:1905.11553 | VERIFICADA | Conduzir a conversa aberta, com naturalidade, até um tópico alvo, usando palavras-chave grossas para controlar o conteúdo das respostas. | O DigiBrain escolhe a intenção/palavra-chave (ex.: "quer brincar") e o LLM só a verbaliza. Mantém a decisão fora do LLM. |

## 7. Alucinação e fidelidade ao contexto em diálogo

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Dziri, Milton, Yu, Zaiane & Reddy (2022).** On the Origin of Hallucinations in Conversational Models: Is it the Datasets or the Models? NAACL 2022. — núcleo | 10.18653/v1/2022.naacl-main.387 · arXiv:2204.07931 | VERIFICADA | Os benchmarks padrão de diálogo ancorado em conhecimento têm mais de 60 % de respostas alucinadas, e os modelos treinados neles amplificam a alucinação. | Se houver ajuste fino, os diálogos de treino passam antes pelo verificador. Exemplos com alegação sem fato não entram nem no prompt few-shot. |
| **Dziri, Kamalloo, Milton, Zaiane, Yu, Ponti & Reddy (2022).** FaithDial: A Faithful Benchmark for Information-Seeking Dialogue. TACL. — núcleo | 10.1162/tacl_a_00529 · arXiv:2204.10757 | VERIFICADA | Edita respostas alucinadas do Wizard of Wikipedia. Os dados servem para treinar um crítico de alucinação e geram respostas vistas por humanos como mais interpretáveis, cooperativas e engajadoras. | Sustenta que fidelidade e engajamento não brigam necessariamente. Um crítico treinado é a evolução possível do verificador por regras. |
| **Dziri, Rashkin, Linzen & Reitter (2022).** Evaluating Attribution in Dialogue Systems: The BEGIN Benchmark. TACL. — núcleo | 10.1162/tacl_a_00506 · arXiv:2105.00071 | VERIFICADA | Métricas automáticas de atribuição dependem de correlações espúrias, não separam bem as respostas atribuíveis das não atribuíveis e pioram quando a fonte é longa. | Não confiar em métrica automática genérica para o verificador. Preferir checagem por ids dos FATOS e uma amostra anotada à mão. |
| **Honovich, Choshen, Aharoni, Neeman, Szpektor & Abend (2021).** Q²: Evaluating Factual Consistency in Knowledge-Grounded Dialogues via Question Generation and Question Answering. EMNLP 2021. — apoio | 10.18653/v1/2021.emnlp-main.619 · arXiv:2104.08202 | VERIFICADA | Mede a consistência factual gerando perguntas a partir da resposta, respondendo-as com o conhecimento e comparando por NLI. | Desenho alternativo do verificador: para cada afirmação, perguntar "qual fato sustenta isso?" e exigir um id dos FATOS. |
| **Shuster, Poff, Chen, Kiela & Weston (2021).** Retrieval Augmentation Reduces Hallucination in Conversation. Findings of EMNLP 2021. — apoio | 10.18653/v1/2021.findings-emnlp.320 · arXiv:2104.07567 | VERIFICADA | Arquiteturas com recuperação no circuito para diálogo ancorado em conhecimento, motivadas pela alucinação dos modelos de diálogo; a recuperação a reduz. | Base para a recuperação dos FATOS antes de gerar, em vez de esperar que o modelo "saiba" o estado do pet. |

## 8. Técnicas para modelo pequeno local

| Referência | DOI / id | Status | O que sustenta (pelo resumo) | O que muda no Digilab |
|---|---|---|---|---|
| **Tam, Wu, Tsai, Lin, Lee & Chen (2024).** Let Me Speak Freely? A Study on the Impact of Format Restrictions on Large Language Model Performance. EMNLP 2024 (Industry). — núcleo | 10.18653/v1/2024.emnlp-industry.91 · arXiv:2408.02442 | VERIFICADA | Restringir a saída a formatos estruturados (JSON, XML) reduz significativamente o raciocínio, e restrições mais rígidas pioram mais. | Saída JSON pode piorar a fala. Gerar a fala livre e só depois extrair as alegações (ou pedir uma lista curta de ids citados num segundo passo), em vez de forçar JSON na fala. |
| **Willard & Louf (2023).** Efficient Guided Generation for Large Language Models. arXiv. — apoio | arXiv:2307.09702 | VERIFICADA (veículo: arXiv) | Geração guiada por regex e gramáticas livres de contexto via máquina de estados, com pouca sobrecarga e estrutura garantida. | Gramática restrita só para a parte estrutural (ids citados, intenção), nunca para o texto da fala. Junto com Tam et al., sugere separar os dois. |
| **Brown, Mann, Ryder, Subbiah et al. (2020).** Language Models are Few-Shot Learners. NeurIPS 2020. — núcleo | arXiv:2005.14165 (sem DOI; página nos anais NeurIPS 33 conferida) | VERIFICADA | A escala melhora muito o desempenho few-shot independente de tarefa; o modelo aprende a tarefa por poucos exemplos no prompt. | Exemplos de diálogo no prompt (3–5 trocas do pet com FATOS → fala fiel). Alavanca mais barata no gemma2:9b antes de qualquer ajuste fino. |
| **Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang & Chen (2021).** LoRA: Low-Rank Adaptation of Large Language Models. arXiv. — núcleo | arXiv:2106.09685 | VERIFICADA (veículo: arXiv; versão publicada não conferida) | Congela os pesos e injeta matrizes de decomposição de baixo posto, reduzindo muito os parâmetros treináveis. | Ajuste fino leve possível na RTX 2060 (com quantização) sobre diálogos aprovados pelo verificador, se o few-shot não bastar. |
| **Hinton, Vinyals & Dean (2015).** Distilling the Knowledge in a Neural Network. arXiv. — apoio | arXiv:1503.02531 | VERIFICADA (veículo: arXiv) | Comprime o conhecimento de um modelo grande, ou de um ensemble, num modelo menor e mais fácil de servir. | Rota "Claude como professor": gerar falas fiéis com a API, filtrar pelo verificador e destilar no modelo local (via LoRA). |
| **Gemma Team (2024).** Gemma 2: Improving Open Language Models at a Practical Size. arXiv. — apoio | arXiv:2408.00118 | VERIFICADA (veículo: arXiv) | Família de 2B a 27B; os modelos de 2B e 9B foram treinados com destilação de conhecimento em vez de predição do próximo token; alega o melhor desempenho para o tamanho. | Documenta o modelo em uso (gemma2:9b). Citar ao registrar a escolha do modelo local. |

---

## Referências de produto (referência de produto, não científica)

Nada aqui sustenta afirmação científica. Serve para dizer o que já existe em jogos e apps.

| Produto | Fonte consultada | O que a fonte de fato mostra | Relação com a frente |
|---|---|---|---|
| **Façade** (Mateas & Stern, 2005) | Artigo GDC 2003, "Façade: An Experiment in Building a Fully-Realized Interactive Drama" (PDF hospedado na Georgia Tech, faculty.cc.gatech.edu/~isbell/.../MateasSternGDC03.pdf). Sem DOI. | O texto digitado pelo jogador é mapeado por regras de template em atos de discurso; outra camada decide a reação dos personagens. A fala é em tempo real e o jogador pode interromper. | Antecedente pré-LLM do padrão "entrada livre → ato de discurso → reação decidida fora da geração". Próximo da separação DigiBrain decide / LLM fala. |
| **Suck Up!** (Proxima) | Página na Steam (app 2726370) | Jogador fala por voz com personagens de IA que respondem em tempo real pelo tom e pela estratégia; a divulgação de IA cita o ChatGPT (OpenAI) como serviço terceiro. Lançamento listado: 1 out. 2025. | Mostra conversa LLM como mecânica central de jogo comercial, com dependência de API na nuvem. A página não diz nada sobre fidelidade a fatos. |
| **Covert Protocol** (NVIDIA + Inworld, demo da GDC 2024) e **NEO NPCs** (Ubisoft) | Página de notícias da NVIDIA ("NVIDIA Digital Human Technologies Bring AI Game Characters To Life", GDC/GTC 2024) | NPCs com história própria, base de conhecimento, estilo de conversa e "conhecimento intrínseco do entorno", respostas pelo LLM da Inworld; a página cita memória de conversa. Não descreve guardrails nem como a resposta é ancorada. | Personagem com base de conhecimento é a prática da indústria. A trava de verificação por fato não aparece na fonte. |
| **AI Desktop Pet** (42kami) | Página na Steam (app 4227700) | Pet de mesa com LLM local embutido, offline, sem chave de API; aceita modelos GGUF; "memória de longo prazo" no modo roleplay (sem explicar como); pode iniciar conversa quando o usuário está ocioso, com frequência e horário de silêncio configuráveis. Lançamento listado: 28 abr. 2026. | Mostra que pet com LLM local e fala espontânea já existe como produto. A persona vem de cartões, não de um cérebro que decide; a página não fala de verificação. |
| Replika, Character.AI, AI Dungeon, Inworld (produto em si) | SEM FONTE (não consultadas nesta rodada) | — | Não citar sem antes buscar a fonte oficial ou um postmortem. |

---

## Não localizadas ou não conferidas

Nenhuma referência buscada nesta rodada ficou NÃO LOCALIZADA: todos os ids e DOIs tentados resolveram. A tabela lista o que **não** foi confirmado e não deve ser citado como tal.

| Item | O que faltou | Situação |
|---|---|---|
| LoRA como artigo da ICLR 2022 | OpenReview pediu verificação de navegador; o OpenAlex só lista o arXiv | Citar como arXiv:2106.09685 |
| MT-Bench / Chatbot Arena como artigo da NeurIPS 2023 (Datasets & Benchmarks) | Versão publicada não buscada | Citar como arXiv:2306.05685 |
| Reflexion como artigo da NeurIPS 2023 | Versão publicada não buscada | Citar como arXiv:2303.11366 |
| MemGPT, ACUTE-Eval, Li et al. 2024 (deriva de instrução), Chen et al. 2024 (survey RPLA), Willard & Louf, Gemma 2 | Veículo publicado (se houver) não buscado | Citar pelo arXiv |
| CharacterEval (Tu et al. 2024, arXiv:2401.01275) | Resolveu no arXiv, mas ficou fora da lista (benchmark em chinês, pouco aplicável) | Não recomendado aqui |
| Replika, Character.AI, AI Dungeon | Fonte oficial não consultada | SEM FONTE |

## Nota de método

- **Data:** 2026-11-06.
- **APIs usadas:**
  - API do arXiv (`export.arxiv.org/api/query?id_list=...`) para título, autores, data e resumo de todos os ids.
  - API do Crossref (`api.crossref.org/works/<DOI>`) para título, autores, ano e veículo de todos os DOIs.
  - Europe PMC REST para o resumo de Shanahan et al. (o Crossref não o traz).
  - Semantic Scholar Graph API para o resumo de Deng et al. 2024 (SIGIR).
  - Anais da NeurIPS (proceedings.neurips.cc) para o veículo de Brown et al.
  - OpenAlex, tentado para o veículo do LoRA, sem sucesso.
- **Limite:** a conferência cobre metadados e resumo, não o texto completo. "O que sustenta" é paráfrase do resumo. Números (ex.: ">60 %", ">80 %", "oito rodadas") são os do resumo.
- **Produto:** as fontes de produto são páginas oficiais (Steam, NVIDIA) e um artigo de conferência da indústria (GDC 2003). Nada de fã.
- **Repetições:** antes da busca foram conferidos `docs/referencias/referencias_verificadas.csv` e um grep em `docs/` por "Generative Agents", "MemGPT", "role-play", "PersonaChat" e "persona". A única ocorrência prévia foi Park et al. 2023 como "pista" em `docs/futuro/cognicao_social.md`.
- **Pendente:** as referências não foram acrescentadas ao CSV `referencias_verificadas.csv`. Isso fica a critério da sessão dona.
