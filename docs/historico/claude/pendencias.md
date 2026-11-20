# Pendências e ideias registradas até 2026-10-13

Seção movida inteira do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13). O estado de cada
marco e as decisões abertas estão em `docs/PAINEL_V2.md` e na seção 8 do `docs/ROADMAP_V2.md`.

## Pendências conhecidas

- **IDEIA: interação do jogador e corpo do pet** (`docs/TODO_INTERACAO_CORPO.md`, Matheus, 2026-09-30): ambiente 2D manipulável ao estilo do
  Championship (comida, bola, obstáculo, áreas), para criar decisões do pet com consequência onde o dono importa. Não autoriza
  implementação; o próximo passo é escolher a interação mínima e o gate antes de ampliar o ambiente.
- **DECIDIDO: mundo físico** (`docs/futuro/mundo_fisico.md`, Matheus, 2026-10-07): o jogador deixa a comida no lugar; ao explorar,
  o pet acha comida (deixada ou caída da árvore) e a bola, que é objeto físico no mapa. Dá a explorar uma recompensa e resolve o pet
  parado. Também DECIDIDO: mapa 2D contínuo com regiões como os cômodos do Creatures 3, vista inclinada do Animal Crossing,
  comida por arrastar e soltar, Animal Crossing e Nintendogs como referências de desenho. PROPOSTO: o motor anda até o alvo que o cérebro escolhe, posições inteiras,
  visão e cheiro; atividades do Creatures 3 e de outros jogos.
- **IDEIA: mecânicas de Dwarf Fortress → V2** (`docs/futuro/dwarf_fortress.md`, Matheus, 2026-10-01): contexto das peças (slots 8+8,
  memória nuclear, faceta × valor, duas prioridades, estresse em duas escalas) para o planejamento da V2; a v1 não recebe nada. O
  desenho (`docs/futuro/proposta_df.md`) só depois do gatilho da tarefa, junto com a fase 1b do plano da V2. DF é pista, não evidência.
- **IDEIA: decodificador de conceitos do DigiBrain** (`docs/futuro/decodificador_conceitos.md`, Matheus, 2026-10-04): os lobos
  decidem numericamente; uma camada lê o estado interno e extrai conceitos com incerteza; só então a LLM fala. Estende o motivo e a
  honestidade do fator; precedentes já publicados (CBM, Discover-then-Name, M-CBM): não alegar novidade. Não autoriza implementação.
- **IDEIA: escada de cognição social** (`docs/futuro/cognicao_social.md`, Matheus, 2026-10-04): dois pets trocando informação com
  fonte e confiança, podendo chegar a reputação, normas, tradição e convenção simbólica; os degraus altos são pergunta, não feature.
  Separa herdado, vivido e aprendido de outros. Primeiro passo possível: pet sintético informante no N5. Não autoriza implementação.
- **IDEIA: convivência no mundo físico** (`docs/futuro/convivencia_mundo_fisico.md`, Matheus, 2026-10-07): dois pets no mesmo mapa,
  vendo um ao outro, disputando a fruta e brincando com a bola; a escada social no mapa. Pede mundo compartilhado, regra de conflito no
  tick e replay do grupo (mudança de motor). Primeiro passo recomendado: parceiro sintético no mapa, sem motor de grupo. Não autoriza
  implementação.
- **IDEIA: doença de órgão e fruta-remédio** (`docs/futuro/doenca_remedio.md`, Matheus, 2026-10-07): uma doença tira um sentido
  (olfato primeiro); uma fruta amarga ajuda o órgão a se curar. Perguntas: o pet percebe a perda, descobre o remédio (com atraso e
  placebo) e passa a descoberta a outro pet (observação, sinal, entrega entre irmãos). Depende dos órgãos do corpo e da convivência.
  Não autoriza implementação.
- **IDEIA: fisiologia por espécie** (`docs/futuro/fisiologia_especies.md`, Matheus, 2026-10-08): um corpo-base comum e um perfil
  herdável por linhagem, em quatro camadas (órgãos presentes, configuração dos órgãos comuns, predisposições inatas; o aprendido fica
  com o indivíduo), como o Creatures 3 faz entre Norns, Ettins e Grendels. Rótulo ("aquático", "blindado") só com efeito no mundo.
  O perfil seria uma alteração declarada do grafo do corpo. DECIDIDAS (2026-10-08): o perfil pela espécie, com módulos por estágio na
  linha (FE-1); o primeiro passo é a configuração por espécie no corpo de hoje, começando pelo olfato (FE-2); variação individual só na
  fase 3 (FE-4); o combate não muda (FE-5); regiões novas só com o módulo (FE-6). Aberta: o perfil de cada brasão (FE-3). Não autoriza
  implementação.
- **DECIDIDO: o pet do produto aprende sozinho, sem elogiar e repreender** (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, Matheus,
  2026-10-07; era o R8.1): os botões saem dos pets novos (v1–v10 iguais); o pet aprende pela consequência, como o reforço químico do
  Creatures 3; acariciar fica e o tapa entra como
  desaprovação, os dois como estímulos no corpo. Antes de ligar: drives que recompensem brincar e o contato (senão o pet fica parado).
  O plano do porte (#201) precisa inverter a seção 1.2 e a D-W1.

- **DECIDIDO o objetivo: ego do pet** (`docs/futuro/ego_existencia.md`, Matheus, 2026-10-07): o pet tem ego, questiona a própria
  existência e fala sobre isso; o automodelo **tem corpo** e é **aprendido por uma rede** (a rede de si, por erro de previsão; o
  pet estima, o motor e as sondas avaliam). Implica rever a regra "só a Decisão aprende" (E-6). O corpo segue os conceitos do
  Creatures 3 (química, receptores, órgãos, Vida; E-7 decidido). O como é PROPOSTO, por etapas com tarefa e plano.
- **IDEIA: aura do herói** (`docs/futuro/aura_do_heroi.md`, Matheus, 2026-10-03): retrato da lista de gambits de um pet que lutou
  muito, vendido na loja como item de 2 lutas que empresta esse conhecimento a outro pet. Depende de loja e moeda (ainda ideia);
  divide a peça técnica com o PvP com ghost. Não autoriza implementação.
- **Pesquisa:** a pergunta do efeito do dono está encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`, 2026-10-01). **V2 = pesquisa
  primeiro** (decisão do Matheus, 2026-10-01): plano PROPOSTO em `docs/PLANO_V2_PESQUISA.md` (pergunta sobre o aprendiz e o
  ambiente; fase 0 fecha a v1, fase 1 testa ambiente mínimo e política com lobos, fase 2 humanos, fase 3 criação × seleção).
  Nenhuma run sem o plano de análise da fase registrado antes.

- **Stand-by: combate 1×1 em tempo real, como no Digimon Championship (DS)** (Matheus, 2026-09-29: guardar para o futuro, sem executar).
  - **A ideia:** o motor passa a simular espaço contínuo (posição, velocidade, alcance, tempo de recarga, passos fixos para continuar reproduzível) no lugar dos turnos e das 3 distâncias. O pet segue lutando sozinho, e o dono influencia pela criação.
  - **O que muda:**
    - `web/app/motor/combate.ts`, `gambits_pet.ts`, `bots.ts` e as constantes CV/CV21;
    - o `digilab/combate_v2` e a arena no Python (paridade);
    - as condições dos gambits (hoje "perto/médio/longe");
    - a bateria e a calibração do combate: vira um combate V3, com protocolo e gates novos;
    - a escala e os NPCs da campanha;
    - os pets antigos ficam no motor de hoje.
  - **Por que esperar:**
    - custo alto;
    - a diferença para o jogador é pequena perto de animar bem os turnos (a opção A, só visual, também descartada por ora);
    - mais variância nas lutas, e o sinal da pesquisa já é pequeno.
  - Os sprites têm quadros de animação (257 Digimon) e efeitos de ataque (187) em `Assets/Digimon Up Assets/Animacoes`.

- Evolução canônica: o vínculo foi redesenhado (vínculo B, pets v10, PR #114). **Decisão do Matheus (2026-10-01): o limiar do Mega
  fica em 0,4** nos pets v10 (no jogo curto o dono da web quase não dá feedback e o B não inverte o Mega,
  `artifacts_v2_vinculo_novo/mega_v10.json`); rever só com medida de dono humano.

- Fala por LLM: repetida com outra semente (2026-09-29, `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260929/`):
  92% aprovadas, nenhuma barrada por fator fora da lista. Pré-leitura (coluna própria no `revisao.csv`): nenhuma
  das 50 cita causa fora dos fatores (desde a v4 a LLM só escreve a moldura); 9 tinham caractere quebrado do
  qwen 2.5 3b, agora barrado na validação da moldura. Leitura do Matheus feita em 2026-10-01.

- Gambits híbridos existem só na web; levar para o Python exige protocolo próprio (arena V2),
  gate de que o aprendizado de gambits separa donos, e ablação trava/veto × sem intervenção. Adiado
  (2026-09-29): nenhuma pergunta de pesquisa atual depende disso.

- Motivo do bandit (resolvido em 2026-09-29, recomendação aceita pelo Matheus): na vida, sem fator e sem exploração
  quem decidiu foi o prior do instinto, e o adulto passa a dizer "Foi instinto: é o meu jeito." (antes "Não sei, só
  quis.", que fica para a exploração e o combate). Python (`expressao.GENERICO_INSTINTO`) e web.
- Memória: bootstrap sobre as 5 sementes feito (2026-09-29, `experiments/bootstrap_memoria.py`,
  `artifacts_v1_memoria/bootstrap_sementes.json`): separação entre − dentro do braço muda −0,0011 bit
  [−0,0039; +0,0029] com memória e −0,0005 [−0,0030; +0,0018] com memória por espaços — sem evidência de
  efeito (poucas sementes: IC largo). Recusa (B2) exige mudança no motor — decisão do pesquisador.

- Combate corrigido (V2C/V21C) aprovado com ressalvas e já na web (2026-09-25; oráculo da web segue de 1
  passo). E2 pede ciclo entre espécies; E4 pede redesenho do adolescente ou da passiva do adulto.
- Combate V2 original reprovado em G4/G5: decidir entre mudar bots passivos, regra de esquiva ou limiares
  (decisão do pesquisador); investigar a dominância do adaptativo antes de plugar pets.
- Combate V2.1 reprovado em E1–E5: falta a especificação das correções da base (finta, parry, fuga
  condicionada, morte súbita) e a `TAREFA_PERSONALIDADE_OBEDIENCIA`; espécies precisam de identidade
  que gere ciclo (E2); a resposta declarada do marcar não funciona com recuar anulando avançar (E3).

- Campos PROPOSTOS: referendados pelo Matheus em 2026-09-29 ("Referendar todos"), em `protocol.REFERENDO` (registro à parte:
  os status e os hashes das runs antigas não mudam; um valor novo volta a contar como não referendado). O aviso
  "PROPOSTOS não referendados" das runs antigas fica como está, porque faz parte dos artefatos reproduzíveis.
- Ablação treino × cuidado (arena v1): inconclusiva e **superada** (decisão de 2026-09-29): a pergunta foi
  respondida no desenho atual pela confirmatória (V21C, 160 ovos) e pelas exploratórias V3/V3b/V3c; não será
  rodada de novo.
- Sementes de partida derivam do nome do braço. Renomear um braço muda todas as partidas dele.
- O hash do protocolo não cobre o código de `metrics.py`; mudanças de métrica não alteram o hash.
- A pasta irmã `D:\Trab\digilab\v0` tem os arquivos soltos (sem subpasta `digilab/`); os imports
  dela não funcionam como estão. Este repo é a versão de referência.
