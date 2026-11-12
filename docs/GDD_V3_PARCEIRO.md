# GDD do parceiro: um Digimon, um cérebro, uma jornada (2026-11-12)

**Status:** PROPOSTO, sem código. Cinco decisões já são do Matheus (PAR-1 a PAR-3, PAR-6 e PAR-14, seção 11). As outras estão PROPOSTAS, com a recomendação
e o custo de errar. Todo número é **PROPOSTO, SEM FONTE**, e se acerta na rodada de equilíbrio do fim ("equilíbrio só no fim").

**Os três documentos da frente:**
- este, o desenho do jogo (o quê e por quê);
- [`ENGENHARIA_V3_PARCEIRO.md`](ENGENHARIA_V3_PARCEIRO.md), o desenho técnico (como, no motor de hoje);
- [`PLANO_V3_PARCEIRO.md`](PLANO_V3_PARCEIRO.md), o roadmap por fases.

**Origem:** o Matheus, em 2026-11-12, pediu uma mecânica de parceiro mais detalhada, que não seja nem um simulador de pets nem uma
montagem de equipe:
- o Digimon e a personalidade dele saem das interações desde o começo;
- há um tempo de camaradagem, com trocas espontâneas e eventos especiais na viagem;
- o parceiro aprende golpes e competências que dão profundidade à luta e à exploração;
- a próxima forma depende do progresso, dos inimigos, da estratégia e da relação;
- a jogress ou a fusão vêm da relação com personagens e Digimon encontrados;
- há personalização do humano e do Digimon, com peças que podem seguir até o Mega.

Depois da análise de viabilidade, ele aprovou a ordem recomendada e acrescentou:
- "o modo jornada seria explorando uma outra área, e nessa outra área dispara esses eventos que podem ser ou não roteirizados";
- "a ideia é tentar desenvolver um mundo digital mais vivo";
- "a gente pode fazer uma POC só, de um mundo simulado";
- "tem que ser o mesmo cérebro para a jornada e as experiências serem correlacionadas".

**O que este documento não é:** uma recriação de jogo existente. Os jogos que o Matheus citou (seção 13) são referência de sensação, não de
tela, texto, número ou nome de sistema. Nenhuma alegação de novidade.

## 1. Em uma frase

**Um parceiro só, com um cérebro só e um registro só, vive entre a casa (o habitat) e uma área viva que muda sem o jogador (a jornada).**
O roteiro e a simulação criam as situações. O pet responde com o que aprendeu, e o que ele vive numa área volta com ele para a outra.

## 2. Pilares

| pilar | o que quer dizer | o que ele proíbe |
|---|---|---|
| **P1. Um parceiro, uma vida** | O DigiBrain da jornada é o mesmo do habitat. A viagem entra no mesmo registro do pet, e o replay refaz as duas áreas juntas. | Um "cérebro de jornada" à parte; um save separado da viagem. |
| **P2. O mundo vive sem o jogador** | A área da jornada tem habitantes com rotina, recursos que crescem e acabam, dia e noite. Muitos eventos nascem disso. | Uma área que só reage quando o jogador chega. |
| **P3. O roteiro propõe, o cérebro responde** | Os eventos roteirizados criam a situação. A reação, a fala, a escolha do pet e a próxima forma saem do cérebro e do registro. | A resposta do pet escrita à mão. |
| **P4. Só o que o motor tem aparece** | Regra do produto que já vale (`PRODUTO_VISAO.md`). Nenhum texto diz o que o pet sente se o motor não tem esse estado. | Um balão de emoção sem estado por trás. |
| **P5. Relação, não nota** | O dono age no mundo e no corpo. Não existe resposta certa (decisão de 2026-10-07, `DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`). | Uma barra de disciplina que sobe quando o jogador "acerta". |
| **P6. Pequeno e jogável primeiro** | Uma POC de uma região antes de qualquer conteúdo grande. Toda mecânica entra atrás de chave desligada. | Construir dez regiões antes de saber se uma é viva. |

## 3. O que o jogo já tem (conferido na `main`, 2026-11-12)

| peça | onde | o que ela dá ao parceiro |
|---|---|---|
| um pet do ovo ao Mega, com o brasão escolhendo a linha | `web/app/motor/nomes.ts` (espécie → brasão, `DIGIMON_DA_FORMA`) | o "um parceiro só" já é o jogo de hoje |
| o cérebro que aprende sozinho pela consequência | o DigiBrain modular nos ovos novos (`web/app/src/cerebro.ts`); o A v11 como linha de base | a personalidade que nasce do que acontece |
| **a evolução** | `web/app/motor/motor.ts`, `_evoluir`: o cuidado decide o ramo do Rookie; o **caráter** (do cérebro) escolhe a linha do Champion; lutas, taxa de vitórias e sobrecarga de treino no Ultimate (a forma sombria); o **vínculo** ≥ 0,4 e as medalhas no Mega | boa parte do "a forma depende de como você progrediu" já existe |
| o vínculo | `web/app/motor/vinculo.ts` (espelho de `digilab/vinculo.py`): atendimento, coerência e vontades respeitadas | a base da relação; hoje só pesa no Mega e no teto da sombria |
| a troca de mapa no mesmo registro | o evento `mi` (`mudar_ilha`), que leva o pet do mundo de hoje para a ilha grande | a base técnica da viagem (só de ida, hoje) |
| a luta | a luta em tempo real da POC (`docs/TAREFA_V3_LUTA_POC.md`): um golpe por forma, a mesma IA nos dois lados, o pet traz só os stats (LP-3); o núcleo N0–N4 em curso | o combate existe, mas **não usa o cérebro do pet** nem tem golpe destravável |
| a Campanha e a Fronteira | 6 lugares com líderes que dão medalhas (`web/app/motor/medalhas.ts`); Liga, Torre, Salão e Fábrica | inimigos com identidade, sem área para explorar |
| a mitologia | `docs/TAREFA_V3_MITOLOGIA.md`: a hybris, os sinais, a pedra do macaco, o Piedmon na montanha | eventos especiais com sentido; o enigma fica fora do registro (D-E1-4) |
| a fala | o Conversar (LLM, modo livre gravado) e a fala pela rede (`src/falaRede.ts`, conceitos do decodificador); gatilhos: decidir, recusar, evoluir, lutar, vontade nova (`src/falaLivre.ts`) | a voz do parceiro; a fala vai para um registro de apresentação, nunca para o do pet |
| dois pets no mesmo mundo | `grupo.Grupo` e a cooperação (CO0–CO7) | a base para habitantes com cérebro |
| o Tamer | nível, medalhas, itens (chips de stat), títulos, Bits (`web/app/src/tamer.ts`) | **não há avatar, nome nem roupa do humano**; nenhuma personalização visual do Digimon |

## 4. O laço do jogo

```
        HABITAT (a casa)                                    JORNADA (a área viva)
  cuidar · descansar · conversar   ──── sair pelo cais ───▶   explorar · encontrar · lutar · escolher
  o corpo se recupera                                         a área segue a própria vida
  as trocas de camaradagem                                    eventos emergentes e roteirizados
              ▲                                                            │
              └──────────── voltar com o que viveu (o mesmo cérebro) ◀──────┘
                                         │
                                         ▼
                 a próxima forma, os golpes, a relação e o caráter mudam
```

- **O laço curto (minutos):** na jornada, o pet anda, percebe e escolhe. Algo acontece (um habitante, um recurso, um evento) e o dono responde
  com o que o jogo deixa: acompanhar, chamar, ajudar, sair, dar comida, elogiar ou repreender.
- **O laço médio (um dia de jogo):** sair, viver a área, voltar cansado e com fome. O habitat é onde o corpo se recupera e onde as trocas de
  camaradagem acontecem com calma.
- **O laço longo (a vida):** o que o pet viveu nas duas áreas vira caráter, golpes, relação e forma. Dois jogadores com o mesmo ovo chegam a
  parceiros diferentes, como já acontece hoje (a medida comum da individualidade).

## 5. A jornada: a área viva

**O que é:** uma região fora da ilha, de um bioma, onde o pet vai com o dono. Ela tem vida própria.

- **Habitantes:** Digimon selvagens com rotina (comer, dormir, defender um lugar, andar em grupo). Eles têm necessidades simples e
  memória curta. Não são o DigiBrain do parceiro (PAR-7).
- **Recursos:** frutas que amadurecem e apodrecem, água, abrigo. Os habitantes disputam os recursos, e o pet também.
- **Tempo:** dia e noite e um clima simples mudam quem está onde.
- **O habitat congela enquanto o pet está fora (PAR-6):** a casa volta exatamente como ficou.
- **Lugares:** pontos com nome (uma clareira, uma ruína, um ninho), onde os eventos roteirizados podem disparar.
- **O que torna a área "viva" (o gate da POC):** sem o jogador fazer nada, um dia na região tem acontecimentos diferentes de outro dia, e o
  pet que volta encontra a área mudada. A medida está no roadmap (fase J1).

**Por que funciona para o jogador:** a viagem tem surpresa sem precisar de roteiro para tudo. O roteiro fica para os momentos que pedem
sentido (um encontro, um mito), e a simulação preenche o resto.

## 6. Os eventos

| tipo | de onde vem | exemplo (só a forma) | entra no registro? |
|---|---|---|---|
| **emergente** | da simulação da área | dois habitantes disputam a última fruta; um habitante ferido fica para trás | não precisa: sai do registro por conta (determinístico) |
| **roteirizado** | de um catálogo fechado, com gatilho (lugar, hora, estágio, vínculo, o que já aconteceu) | um personagem pede ajuda numa ruína; um sinal da mitologia aparece | o disparo sai do registro; a escolha do dono entra |
| **de camaradagem** | do estado do pet e da memória dele, num momento calmo | o pet para perto de um lugar onde algo marcante aconteceu | não; a fala vai para o registro de apresentação, como hoje |

- **As escolhas do dono** são ações no mundo, nunca uma nota. Exemplos de forma: ajudar ou seguir em frente, dividir a comida ou guardar,
  chamar o pet de volta ou deixar que ele decida. A escolha entra no registro como evento. O pet aprende com o que ela provoca no corpo e
  no mundo, pelo caminho que o cérebro já tem (P5).
- **Uma escolha pode ter dono e pet discordando:** o pet pode recusar (a recusa já existe no motor). Isso é relação, não falha.
- **O que nunca se faz:** um evento que dá ou tira caráter direto ("+1 Coragem"). O caráter sai do cérebro (PAR-5).

## 7. Camaradagem e fala

- **As trocas espontâneas** nascem de três coisas que o motor já tem ou vai ter: o que o pet decidiu agora (os conceitos do decodificador),
  o que ele lembra (a memória autobiográfica) e onde ele está (o lugar da jornada ou do habitat).
- **A LLM é só a voz** (a regra da fala pelo decodificador). Ao vivo, só no modo livre gravado. A fala vai para o registro de apresentação.
- **Os gatilhos novos (PROPOSTOS):** chegar a um lugar marcado, voltar ao habitat depois de uma viagem, um evento roteirizado terminado, um
  momento calmo depois de um dia agitado.
- **O limite:** a voz do jogo ainda não está validada (a DC5 está em curso). A camaradagem falada depende dela. Até lá, as trocas aparecem
  como gesto e reação de rosto, que o jogo já tem.

## 8. O parceiro: espécie, caráter, golpes, evolução

### 8.1 Espécie e caráter

- **Hoje:** o jogador escolhe o brasão num menu, e o brasão decide a linha. O caráter sai do cérebro e escolhe o Champion.
- **Proposta (PAR-4):** o brasão sai das primeiras interações, numa abertura curta de escolhas no mundo. O menu sai, mas o resultado
  continua sendo um dos quatro brasões de hoje.
- **O caráter continua vindo do cérebro.** A jornada só dá a ele mais situações para aprender. Como o cérebro é o mesmo (P1), uma vida com
  muita jornada e uma com muito habitat levam a caracteres diferentes, sem regra nova.

### 8.2 Golpes e competências

- **Hoje:** um golpe por forma, e a luta usa a mesma IA nos dois lados (LP-3). O pet não escolhe golpe.
- **Proposta:**
  - **golpes que se destravam** pelo que o pet viveu: ver um golpe numa luta, derrotar um tipo de inimigo, treinar. O conjunto vai com ele de
    forma em forma (PAR-8);
  - **competências de exploração**, como atravessar água rasa, escalar, farejar ou cavar. Elas abrem partes da região e saem do corpo e do
    que o pet aprendeu, não de um menu.
- **A decisão grande (PAR-9):** se o cérebro do pet passa a escolher o golpe na luta. É o que dá "estratégia" ao parceiro, mas mexe na LP-3 e
  no núcleo da luta, que estão em curso.

### 8.3 Evolução

A tabela de hoje já usa cuidado, caráter, lutas, vitórias, sobrecarga, vínculo e medalhas. A proposta acrescenta entradas que saem do
registro:
- os tipos de inimigo derrotados e os golpes mais usados (o estilo);
- os eventos roteirizados vividos (marcos de história);
- o vínculo pesando também no Champion e no Ultimate, não só no Mega.

Cada entrada nova é uma versão de pet nova, com paridade. Os pets antigos não mudam.

## 9. Relação, personagens e jogress

- **O vínculo de hoje continua sendo a relação com o dono.** Ele ganha peso na evolução (8.3).
- **A relação com personagens (PAR-10):** personagens humanos e Digimon da jornada guardam uma afinidade com o pet. Ela é feita do que
  aconteceu entre eles: ajudou, disputou, lutou, dividiu comida. Não existe diálogo de "agradar".
- **Jogress e fusão (PAR-11):** só com afinidade alta com aquele personagem **e** vínculo alto com o dono. A recomendação é que a forma
  fundida seja **temporária** (uma luta, um evento), e não um segundo parceiro. Assim o pilar P1 fica de pé. A jogress entre dois pets
  está fora do escopo desde a `TAREFA_V2_UP_EVOLUCAO.md`, e esta proposta reabre o tema só para o parceiro com um personagem.

## 10. Personalização

- **O humano (PAR-12):** hoje não existe avatar. A proposta é um Tamer com nome, rosto e roupa, visto no perfil, nos lugares e na jornada.
- **O Digimon (PAR-13):** vale a regra **"poses sem acréscimos"**: nada de chapéu, asa ou braço a mais no desenho (a fonte curta está em
  `docs/PLANO_V3_MOEDA.md`). A personalização do Digimon fica fora do desenho:
  - a cor de uma aura ou de um rastro;
  - o efeito do golpe;
  - um emblema e um título na plaquinha;
  - um item equipado, como os chips de hoje.

  **Essas peças seguem de forma em forma até o Mega,** porque não dependem do desenho de cada forma.
- **Peça visual no desenho** só se o Matheus revisar a regra, e com custo alto: dezenas de espécies vezes cinco níveis.

## 11. Decisões

| # | decisão | estado | recomendação | custo de errar |
|---|---|---|---|---|
| PAR-1 | a jornada é um modo ao lado do habitat, numa outra área | **DECIDIDO** (Matheus, 2026-11-12) | — | — |
| PAR-2 | o cérebro e o registro da jornada são os do habitat | **DECIDIDO** (Matheus, 2026-11-12: "tem que ser o mesmo cérebro") | — | — |
| PAR-3 | começar por uma POC de um mundo simulado vivo, de uma região | **DECIDIDO** (Matheus, 2026-11-12) | — | — |
| PAR-4 | o brasão sai das primeiras interações, não de um menu | PROPOSTO | sim, numa abertura curta, ainda com os quatro brasões | um menu fica mais claro para quem joga pela primeira vez; uma abertura mal feita parece sorteio |
| PAR-5 | evento nenhum dá ou tira caráter direto | PROPOSTO | sim | um "+1 Coragem" vira a nota que a decisão de 2026-10-07 tirou, e o cérebro deixa de importar |
| PAR-6 | enquanto o pet está fora, o habitat congela | **DECIDIDO** (Matheus, 2026-11-12: "ele pode ficar congelado, não precisa ter alteração nenhuma no universo enquanto o pet está fora") | — | — |
| PAR-7 | os habitantes da área têm um controlador simples, não o DigiBrain | PROPOSTO | sim na POC; um cérebro de verdade só se a POC pedir | com o DigiBrain, o replay e o desempenho pesam N vezes; com regras pobres demais, a área não parece viva |
| PAR-8 | os golpes destravados ficam com o pet entre as formas | PROPOSTO | sim | sem isso, a evolução apaga o que o jogador construiu |
| PAR-9 | o cérebro do pet escolhe o golpe na luta | PROPOSTO, **depois do núcleo da luta** | decidir só quando o núcleo (N0–N4) fechar | mexer agora briga com a LP-3 e com o trabalho em curso |
| PAR-10 | personagens guardam afinidade feita de atos, sem diálogo de agradar | PROPOSTO | sim | diálogo de agradar vira uma árvore de respostas certas |
| PAR-11 | a jogress é temporária e pede afinidade com o personagem e vínculo com o dono | PROPOSTO | sim | permanente cria um segundo parceiro e quebra o P1 |
| PAR-12 | o Tamer ganha nome, rosto e roupa | PROPOSTO | sim, depois da jornada jogável | é custo de arte sem jornada para usar |
| PAR-13 | a personalização do Digimon fica fora do desenho (aura, rastro, efeito, emblema, item) | PROPOSTO | sim; a regra "sem acréscimos" fica | revisar a regra multiplica a arte por espécie e nível |
| PAR-14 | a jornada (a área aberta, os habitantes, os eventos) fica só no jogo web, sem Python e sem paridade com o Python | **DECIDIDO** (Matheus, 2026-11-12: "não vai fazer parte da pesquisa [...] fica só na parte web do jogo") | — | — |
| PAR-15 | a fala da camaradagem espera a voz validada; até lá, gesto e rosto | PROPOSTO | sim | uma fala ruim na hora mais íntima do jogo pesa mais que nenhuma fala |

## 12. Fora deste desenho

- A pesquisa em Python: a jornada é só do jogo web (PAR-14). Os critérios da POC são de produto, não gates de pesquisa.
- O multijogador e o ranking (`docs/PLANO_V3_MMO.md`), e a conta (`docs/PLANO_V3_CONTA*`): a jornada é do jogador sozinho.
- Venda de qualquer coisa: os Bits nunca são vendidos (CN-11/12).
- Mudar a pergunta do dono, encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`).
- Mudar o `engine.py`.

## 13. Referências de design

Os jogos citados pelo Matheus servem de **referência de sensação**: a camaradagem com trocas espontâneas (Dragon Age) e o contraste com o
simulador de pets e com a montagem de equipe (as séries Digimon World e Digimon Story). **NÃO VERIFICADO EM FONTE PRIMÁRIA**, nenhuma tela,
texto, número ou nome de sistema copiado, nenhuma alegação de precedência. A análise do cuidado do Next Order fica no vault (`DigiLab
Research/20 Temas/Comida, elogio e bronca (Next Order).md`).
