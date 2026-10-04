# Escada de cognição social — da informação entre dois pets à protocultura

Status: **IDEIA / CONTEXTO** (2026-10-04). Proposta do Matheus. Este documento registra a ideia, o que ela toca no que já existe e a
literatura que a cerca. Ele **não autoriza implementação**, não é um desenho fechado e não muda nenhum experimento. É a ideia mais longe
no tempo das registradas em `docs/futuro/`.

## 1. A ideia

Não implementar "fofoca" como uma feature solta. Mapear uma **escada de cognição social**: dois pets começam trocando informação concreta
e, com memória, confiança e transmissão, **podem** chegar a reputação, normas e protocultura. Os degraus de cima não são programados: são a
**pergunta experimental**.

| degrau | entre humanos | entre pets | o que o DigiBrain precisaria |
|---|---|---|---|
| 1. Informação factual | "Há comida ali" | A avisa B que há comida em X | percepção, memória episódica, comunicação |
| 2. Experiência compartilhada | "Achei comida ali ontem" | A transmite algo que ele mesmo viveu | memória com fonte, tempo e contexto |
| 3. Informação de segunda mão | "João disse que há comida lá" | A transmite a B algo que aprendeu de C | memória da proveniência |
| 4. Reputação | "João costuma mentir" | B aprende que A informa mal | modelo dos outros e confiança |
| 5. Fofoca | "João roubou a comida de Maria" | A conta a B uma ação de C que muda como B vê C | memória social, transmissão sobre terceiros |
| 6. Alianças | "João é amigo de Maria" | A aprende relações entre outros pets | grafo social |
| 7. Normas | "Não roubamos comida" | ações passam a receber aprovação ou punição social | aprendizagem normativa |
| 8. Tradição | "Nosso grupo faz assim" | comportamento aprendido socialmente persiste entre gerações | transmissão cultural |
| 9. Símbolos | "Esse sinal significa perigo" | um sinal compartilhado ganha significado | associação simbólica |
| 10. Convenção simbólica | "Este lugar é especial" | o grupo atribui a algo um significado que não vem das propriedades físicas | representação simbólica e memória coletiva |

O paralelo com Harari (*Sapiens*) é **moldura**: livro de divulgação, sem DOI, não é evidência e não entra como citação de resultado.
Para o degrau 10 o nome defensável é **convenção simbólica emergente**, nunca "religião", "mito" ou "crença" no começo.

## 2. O experimento mínimo

**Informação com fonte.** A acha comida boa na árvore vermelha. A não transmite o vetor neural: o canal converte a experiência numa mensagem
social de vocabulário fechado, `COMIDA(arvore_vermelha)`. B nunca foi lá e passa a ter uma crença. A memória de B guarda
`conteúdo + fonte + confiança na fonte + direta ou indireta + tempo`. A sabe porque viu; B sabe porque A contou.

**Engano.** Com pouca comida e os dois com fome, A sabe `comida = árvore vermelha` e comunica `comida = pedra azul`. O engano fica
operacional: **estado do mundo na crença de A ≠ mensagem enviada**, com ganho esperado para A se B for embora. O episódio é classificado
depois como "engano instrumental" por critérios definidos antes, e não porque alguém escreveu que A quis mentir. O decodificador de
conceitos (`docs/futuro/decodificador_conceitos.md`) mostraria `crença(comida = árvore)`, `comunicou(comida = pedra)` e `ganho esperado alto`.

**Fofoca.** B descobre que A mentiu e conta a C. C nunca foi enganado e mesmo assim a confiança dele em A cai. É a estrutura mínima de
"experiência individual → comunicação → reputação coletiva". Se A disser a C que B mente, C tem relatos em conflito e precisa inferir em
quem confiar: começa uma epistemologia social artificial.

## 3. Modelo dos outros (hipótese de arquitetura, não decidida)

Não precisa ser um lobo novo; pode sair da interação dos que existem: a percepção identifica o pet, a memória recupera a história com ele,
a emoção dá a valência, uma camada social estima a relação e a decisão escolhe cooperar, competir ou comunicar. Por pet conhecido:
familiaridade, confiança, afinidade, estimativa de dominância e de agressividade, crenças sobre ele ("divide comida", "informa certo") e a
**evidência separada em direta e indireta**.

**Reputação ≠ relacionamento.** Dá para gostar de alguém e saber que ele mente, ou não gostar e reconhecer que ele informa certo. Os dois
ficam em variáveis separadas.

## 4. Da fofoca à cultura

Sequência a investigar, um degrau por vez: comunicação factual → aprendizado social (B muda o comportamento pelo que A disse) → confiança
→ informação sobre terceiros → reputação → normas → transmissão cultural → tradição.

**O teste forte: remover os fundadores.** Se o comportamento continua depois que os pets que o descobriram morrem, ele deixou de existir só
na memória individual e passou a existir na população.

**Tradição arbitrária.** Duas populações com o mesmo mundo e genomas controlados. Numa, por acaso, um pet toca duas vezes na árvore antes de
comer, sem benefício nenhum; outros imitam; depois de gerações a linhagem mantém o gesto. Na outra, nunca surge. A diferença entre grupos
sem diferença de ambiente nem de genoma é a pergunta: **agentes artificiais desenvolvem tradições persistentes por transmissão social?**
É o mesmo raciocínio de exclusão usado em culturas de chimpanzés (Whiten et al. 1999): descartar a explicação ecológica e a genética antes de
chamar de cultura.

**Convenção simbólica (muito longe no roteiro).** Escrever `pet.acredita("árvore_é_sagrada")` seria só um atributo do desenvolvedor. A
pergunta é se um símbolo arbitrário (um objeto ● sem bônus) pode ganhar significado compartilhado, por exemplo ser carregado antes das
lutas e associado a vitória, e se isso persiste depois que os pets originais saem: informação cultural que não está no ambiente nem no
genoma.

## 5. O que isso muda na pesquisa

A pergunta do Digilab foi de "um pet desenvolve personalidade e aprende na vida?" para a pergunta maior da V2 ("em que condições a
plasticidade durante a vida vale mais que o herdado?"). A escada abre uma terceira via de informação:

| via | o que passa | no Digilab |
|---|---|---|
| vertical biológica | genoma | herança, E1, fase 3 |
| individual | o que o pet viveu | o aprendiz da V2 (P1, consequência) |
| horizontal social | o que o pet aprendeu de outros pets | **esta ideia** |

O experimento forte é **separar o herdado, o vivido e o aprendido de outros** no mesmo agente, com controles. Isso cabe no programa de
natureza × criação e na pergunta maior como mais uma fonte de plasticidade (um braço social, além de P0–P3), sem abandonar o núcleo.

## 6. Onde encosta no que já existe

| peça | relação |
|---|---|
| **N5, dono informante** (`docs/ARQUITETURA_V2_VALIDACAO.md`, D-A) | é o degrau 1 com o dono no lugar de A: informação entra pela percepção, nunca como reforço, e o mundo valida. O P2e (dono que informa errado) é o caso "A mente". Trocar o dono por um **pet sintético informante** reaproveita a peça sem motor de vários pets |
| **N6, memória** (quatro marcos) | a memória com fonte, tempo e proveniência dos degraus 2 e 3 é extensão direta |
| **Mentira** (`ConfigMentira`, `digilab_fala_livre/mentira.py`, `web/app/motor/mentira.ts`) | hoje o pet mente ao dono por regra; aqui o engano é medido como crença ≠ mensagem, sem regra que o mande mentir |
| **Decodificador de conceitos** (`docs/futuro/decodificador_conceitos.md`) | classifica o episódio (engano, fofoca) sem antropomorfizar, com teste causal |
| **Aura do herói** (`docs/futuro/aura_do_heroi.md`) | transmissão horizontal por cópia, decidida pelo jogo; serve de contraste com a transmissão social aprendida |
| **Linhagem** (`docs/PLANO_LINHAGEM_ALIFE.md`, E1) | a via vertical; no E1 o genoma explicou 4,9% |
| **Convivência com outros pets** (`docs/TODO_INTERACAO_CORPO.md`) | já registrada como possibilidade distante; esta ideia dá a ela uma pergunta |

## 7. Medidas possíveis (PROPOSTO, sem número; cada degrau com o próprio plano antes da run)

- **Aprendizado social:** B muda de comportamento depois da mensagem de A, contra um controle acoplado com a mesma mensagem vinda de fonte
  sorteada, e contra B sem mensagem.
- **Confiança:** a confiança de B em cada informante acompanha a taxa de acerto dele.
- **Reputação:** a confiança de C em A muda sem contato direto, contra um controle sem transmissão.
- **Engano:** frequência de crença ≠ mensagem, contra a taxa de erro honesto do mesmo canal, e se ela sobe com a escassez.
- **Tradição:** persistência do comportamento depois de remover os fundadores; diferença entre populações com o mesmo mundo e genomas
  controlados.
- **Convenção simbólica:** associação ao símbolo sem bônus, persistente e transmitida, contra um símbolo nunca associado.

## 8. Literatura

Status pelo vocabulário da skill `literatura-digilab`. As marcadas **pista** tiveram metadados conferidos em 2026-10-04 (Crossref ou API do
arXiv: autores, ano, veículo e título), sem leitura do resumo nem do texto, e **não estão na tabela verificada**: ler antes de citar.

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Kirby, Griffiths e Smith 2014 | `10.1016/j.conb.2014.07.014` | VERIFICADA | aprendizagem iterada: transmissão entre gerações molda o que é transmitido |
| Griffiths e Kalish 2007 | `10.1080/15326900701326576` | VERIFICADA | aprendizagem iterada com agentes bayesianos |
| Floreano et al. 2007, *Current Biology* | `10.1016/j.cub.2007.01.058` | pista | condições evolutivas para comunicação surgir em robôs |
| Mitri, Floreano e Keller 2009, *PNAS* | `10.1073/pnas.0903152106` | pista | robôs com interesses em conflito evoluem para suprimir informação; o precedente mais próximo do experimento da seção 2 |
| Nowak e Sigmund 2005, *Nature* | `10.1038/nature04131` | pista | reciprocidade indireta e reputação |
| Sommerfeld et al. 2007, *PNAS* | `10.1073/pnas.0704598104` | pista | fofoca no lugar da observação direta, em jogos de reciprocidade indireta |
| Dunbar 2004 | `10.1037/1089-2680.8.2.100` | pista | fofoca em perspectiva evolutiva |
| Whiten et al. 1999, *Nature* | `10.1038/21415` | pista | culturas em chimpanzés, pelo método de exclusão |
| Whiten, Horner e de Waal 2005, *Nature* | `10.1038/nature04047` | pista | conformidade a normas culturais de uso de ferramenta |
| Shoham e Tennenholtz 1997, *Artificial Intelligence* | `10.1016/s0004-3702(97)00028-3` | pista | emergência de convenções sociais em agentes |
| Steels 2003, *Trends in Cognitive Sciences* | `10.1016/s1364-6613(03)00129-3` | pista | comunicação ancorada que evolui em robôs |
| Foerster et al. 2016 | arXiv:1605.06676 | pista | aprender a comunicar em RL multiagente |
| Lazaridou et al. 2017 | arXiv:1612.07182 | pista | linguagem emergente em cooperação multiagente |
| Mordatch e Abbeel 2018 | arXiv:1703.04908 | pista | linguagem composicional ancorada em populações |
| Rabinowitz et al. 2018 | arXiv:1802.07740 | pista | modelo de outros agentes (teoria da mente de máquina) |
| Bhoopchand et al. 2023, *Nature Communications* | `10.1038/s41467-023-42875-2` | pista | imitação rápida como transmissão cultural em agentes |
| Park et al. 2023 | arXiv:2304.03442 | pista | agentes com LLM em que informação se espalha socialmente |

**Limite de alegação.** Comunicação emergente, supressão de informação sobre comida em robôs, reputação por fofoca, convenções sociais e
transmissão cultural em agentes artificiais **já estão publicados**. Nada aqui pode ser dito como novo. O que talvez seja contribuição, só
depois de uma busca própria que permita dizer "não localizamos": separar no mesmo agente, com controles, o efeito do herdado, do vivido e
do aprendido de outros pets.

## 9. Riscos

- **Escopo.** O motor de hoje é um pet e um dono. Vários pets pedem determinismo multiagente, registro da população e replay de grupo: é
  mudança de motor, não de mecânica.
- **Antropomorfismo.** "Mentira", "fofoca" e "cultura" impressionam. Cada rótulo só vale com o critério operacional definido antes e o teste
  do decodificador de conceitos.
- **Rótulo escrito à mão.** Programar o degrau de cima (uma crença, uma norma) mata a pergunta. Os degraus altos só valem se surgirem.
- **LLM fora da decisão.** Mensagens entre pets em vocabulário fechado; a LLM, se entrar, só fala, como no decodificador.

## 10. Onde entra

Depois do marco da fase 1 e, para os degraus de tradição, depois da fase 3 (genoma e gerações). Um primeiro passo barato, se aprovado,
cabe antes: o **degrau 1 com um pet sintético informante** no lugar do dono do N5, que mede aprendizado social sem motor de vários pets.
Próximo passo: uma tarefa que escolha esse primeiro degrau, com plano de análise antes da run, e peça ao Claude Science a verificação das
pistas da seção 8.
