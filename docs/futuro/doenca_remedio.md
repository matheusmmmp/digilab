# Doença de órgão, perda de um sentido e a fruta-remédio: o pet descobre a cura e passa adiante

Status: **IDEIA** (Matheus, 2026-10-07), registrada como implementação futura. **Não autoriza implementação** e não muda nenhum
experimento. O que está aqui é a ideia e um desenho PROPOSTO para discutir; cada etapa entra com tarefa e plano de análise próprios.

## 1. A ideia

Uma **doença** ataca um **órgão** do pet, e ele perde um **sentido** (olfato, audição ou visão). Uma **fruta-remédio** ajuda o órgão a se
curar. Ninguém diz ao pet que ele está doente nem que aquela fruta é remédio. Três perguntas:

1. **Perceber:** o pet percebe que perdeu o sentido? Quanto tempo leva?
2. **Descobrir o remédio:** o pet percebe que a fruta-remédio arruma isso? Depois de quanto tempo, e de quantas tentativas?
3. **Passar adiante:** quando outro pet comer a mesma coisa e tiver o mesmo problema no órgão, os dois detectam isso? O primeiro comunica
   e passa o remédio para o outro?

Junta três ideias já registradas: o corpo com órgãos do Creatures 3 (`docs/futuro/ego_existencia.md`, seção 2), o mundo físico com a fruta
que apodrece e faz mal (`docs/futuro/mundo_fisico.md`) e a convivência de dois pets no mapa (`docs/futuro/convivencia_mundo_fisico.md`).

## 2. A doença no corpo (PROPOSTO)

**De onde vem.** De comer uma fruta contaminada, por exemplo a podre ou uma fruta mofada específica. Assim a causa é a mesma para os dois
pets ("quando o outro comer"), e o pet pode também aprender a evitar a causa. **Sem contágio** no começo: um pet não passa a doença ao
outro.

**O órgão.** Um órgão de sentido no corpo químico, na etapa de órgãos e dano do corpo (`ego_existencia.md`, etapa 1b: força vital, dano,
cura). O dano baixa a força do órgão, e o receptor do sentido passa a responder na medida dessa força. O pet não recebe um sinal "estou
doente": recebe um sentido mais fraco.

**O que cada sentido faz no mundo de hoje:**

| sentido | no mundo físico | com o órgão doente |
|---|---|---|
| **olfato** | o cheiro da comida que o pet sente de longe, com intensidade e direção (`PercepcaoMundo`) | o cheiro fica fraco e perde a direção; o pet acha comida só quando a vê |
| **visão** | os objetos a até 6 células | o raio de visão encolhe |
| **audição** | **ainda não existe** no mundo. Seria ouvir a fruta cair da árvore, o chamado do dono e o sinal de outro pet (convivência, degrau 2) | o pet só ouve de perto |

O **olfato** é o primeiro candidato: já existe, pesa no forrageio e a perda dele é medida pelas medidas que o mundo físico já tem (o
déficit de fome e energia, as visitas às árvores, a distância até a comida).

**O curso.** O dano sobe por um tempo e depois o órgão se cura sozinho, devagar. **Sem morte.** A cura espontânea existe de propósito: é
ela que obriga a ter o controle do placebo (seção 4), porque "melhorou depois de comer" não prova que a fruta curou.

**O sintoma visível.** Uma ação involuntária, como o espirro do Creatures 3, que o jogador e outro pet podem ver. A perda do sentido não
se vê de fora; sem um sintoma visível, a pergunta 3 não tem como começar.

## 3. A fruta-remédio (PROPOSTO)

- **Uma fruta nova**, num lugar próprio do mapa (por exemplo, a mata), longe da casa.
- **Amarga para o pet saudável:** faz mal leve no humor e não alimenta. Um pet saudável aprende a evitá-la. Doente, ela acelera a cura do
  órgão. É o desenho da planta medicinal amarga dos chimpanzés (Huffman 2003) e das ovelhas que comem o que as alivia só quando estão
  mal (Villalba, Provenza e Shaw 2006). O que se testa é um aprendizado **condicional**: comer a fruta **só quando doente**.
- **O efeito chega com atraso.** O sentido volta horas depois, não na hora de comer. O pet precisa ligar o gosto da fruta a uma melhora
  que vem bem depois. A aversão gustativa mostra que animais ligam gosto e consequência com atraso longo quando a pista combina com a
  consequência (Garcia e Koelling 1966).

**O que o cérebro precisaria, como pergunta de desenho, não decidida:**
- **Saber que está doente sem acesso privilegiado:** a entrada é o próprio sentido mais fraco (o receptor) e, se houver, um mal-estar
  químico do corpo.
- **Crédito atrasado:** hoje a consequência do N3 credita só a decisão imediata, e o traço de elegibilidade da revisão do aprendiz
  piorou o aprendizado. A memória de episódios do N6 é o candidato natural: o episódio "comi a fruta amarga" fica guardado, e a melhora
  posterior o recupera.
- **Dependência de estado:** "comer X" com peso diferente conforme o sentido está fraco ou não. No cérebro C, a memória dependente de
  estado já faz isso com a fome.

Se nenhum cérebro de hoje aprender a fruta-remédio, isso é um resultado, não uma falha a esconder.

## 4. Perceber e descobrir: as perguntas 1 e 2

**Perceber que perdeu o sentido** pode ser medido de dois jeitos, e o motor sabe a verdade (o dano real do órgão) para comparar:
- **pelo comportamento:** o pet passa a depender menos do sentido perdido, por exemplo segue menos o cheiro e explora mais pela vista. O
  tempo até essa mudança, contado a partir do dano, é o tempo para perceber;
- **pela rede de si** (`ego_existencia.md`, seção 3): a cabeça do corpo prevê o que o pet vai sentir. Com o órgão doente, o erro de
  previsão sobe ("eu esperava sentir cheiro aqui"). O tempo até o erro passar de um limiar é o "percebeu". É a pergunta "por que meu corpo
  não reage mais como antes?" da seção 4 do ego, com uma causa concreta.

**Descobrir o remédio,** com medidas propostas:
- quantos dias e quantas tentativas até a primeira vez que o pet doente come a fruta-remédio;
- a preferência condicional: p(comer a fruta-remédio | doente) − p(comer | saudável);
- o tempo de cura dos pets que aprenderam contra os que não aprenderam;
- **a recaída:** na segunda doença, o pet vai direto à fruta? Quanto tempo leva, comparado à primeira vez?

**Os controles,** no padrão do projeto:
- **placebo:** uma fruta com o mesmo gosto e o mesmo lugar, sem efeito no órgão. Separa "aprendeu o remédio" de "comeu algo e melhorou
  sozinho";
- **remédio imediato × atrasado:** o mesmo efeito, na hora ou horas depois. Mede o custo do atraso para o cérebro;
- **sem a cura espontânea,** só como sensibilidade.

## 5. Passar adiante: a pergunta 3

Depende da convivência (`convivencia_mundo_fisico.md`). O pet B come a fruta contaminada e adoece do mesmo órgão. O pet A já teve a
doença e, talvez, aprendeu o remédio.

**Detectar.** B espirra, e A vê. A parte difícil é A ligar o sintoma do outro ao que ele mesmo viveu ("o que ele tem é o que eu tive").
Isso se mede; não se escreve.

**Os canais, do mais barato ao mais caro:**

| canal | o que acontece | o que pede |
|---|---|---|
| **observação** | B vê A comer a fruta-remédio, ou ver A doente comer e melhorar; B aprende mais rápido do que sozinho | a convivência, degraus 0 e 1. No degrau 0 é um parceiro sintético que espirra e come a fruta, sem motor de grupo |
| **sinal** | A, ao ver B espirrar, emite um sinal que aponta a fruta, em vocabulário fechado | o degrau 2. O sinal aponta a fruta; o sentido "remédio" não é escrito à mão |
| **entrega** | A leva a fruta até B | pegar e soltar (as ações do Creatures 3; hoje o pet não carrega nada) e **um motivo para ajudar**, que custa a A |

**O motivo para ajudar é a pergunta mais funda.** Nos animais, tratar o outro aparece sobretudo entre parentes e em sociedades de insetos.
Abelhas coletam mais resina quando a colmeia é infectada (Simone-Finstrom e Spivak 2012), formigas tratam as feridas de companheiras
com compostos antimicrobianos (Frank et al. 2023), e a imunidade social é o nome geral (Cremer, Armitage e Schmid-Hempel 2007). No
Digilab o parentesco existe: os **irmãos** do cruzamento em Meus pets. Pets irmãos são o caso natural para testar a entrega.

**Medidas propostas:**
- o tempo até B se curar, com A presente, sozinho e com um parceiro **acoplado** (que come a fruta-remédio sem relação com a doença);
- quantas vezes A sinaliza ou entrega diante do sintoma de B, contra as vezes sem sintoma.

**O mundo que muda.** Se o remédio troca de fruta no meio da vida, copiar o outro leva ao remédio velho: é o paradoxo de Rogers da
convivência, num caso concreto.

## 6. O dono

O jogador pode arrastar a fruta-remédio para perto do pet doente, como qualquer comida. Isso trata o pet, mas compete com o pet aprender
sozinho. Na pesquisa vira um braço próprio, "o dono trata", ao lado do pet que descobre sozinho. É o mesmo cuidado de separar o efeito do
dono do efeito do pet de sempre.

**No jogo:**
- a doença é leve, sempre tem cura e não mata;
- o espirro e o sentido fraco aparecem na tela para o jogador entender;
- o tratar do dono é opcional;
- o jogo mostra quando o pet descobriu o remédio sozinho, como um momento da história dele.

## 7. Ordem possível

1. **Os órgãos e o dano no corpo** (etapa 1b do corpo), com um órgão de sentido e o receptor que responde à força dele.
2. **A pergunta 2 num pet sozinho, com o olfato:** a doença pela fruta contaminada, a fruta-remédio, o placebo e o remédio imediato ×
   atrasado. A medida comportamental da pergunta 1 vem junto.
3. **A pergunta 1 pela rede de si**, quando ela existir (etapa 2 do ego).
4. **A pergunta 3 com o parceiro sintético** (degrau 0 da convivência): um parceiro que espirra e come a fruta-remédio.
5. **Dois pets** (degrau 1), depois o sinal (degrau 2) e, por último, a entrega entre irmãos.
6. **A audição,** se for escolhida, pede o som no mundo (a queda da fruta, o chamado, o sinal).

## 8. Riscos

- **A cura espontânea confunde.** Sem o placebo, qualquer melhora parece remédio.
- **Antropomorfismo.** "Ele sabe que é remédio", "ele quis ajudar": só com critério operacional definido antes e medido no registro.
- **Escrever a resposta.** Uma regra "doente → comer X" ou "viu espirro → levar X" mata a pergunta. O pet tem de descobrir.
- **O atraso pode ser longo demais** para os cérebros de hoje. Se for, é um resultado.
- **Escopo.** Órgãos, sentidos, a convivência e o carregar são quatro peças grandes; a ordem da seção 7 existe para medir algo a cada
  passo.
- **Bem-estar no jogo.** Doença em pet virtual precisa ser leve e ter saída. O jogador não pode sentir que o pet sofre sem poder fazer
  nada.

## 9. Literatura

Status pelo vocabulário da skill `literatura-digilab`. As marcadas **pista** tiveram os metadados conferidos no Crossref em 2026-10-07
(autores, ano, título e veículo), sem leitura do resumo nem do texto, e **não estão na tabela verificada**: ler antes de citar.

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Huffman 2003, *Proceedings of the Nutrition Society* | `10.1079/pns2003257` | pista | automedicação animal com plantas, inclusive a planta amarga dos chimpanzés |
| de Roode, Lefèvre e Hunter 2013, *Science* | `10.1126/science.1235824` | pista | automedicação em animais como fenômeno amplo; inclui medicar a prole |
| Villalba, Provenza e Shaw 2006, *Animal Behaviour* | `10.1016/j.anbehav.2005.09.012` | pista | ovelhas aprendem a comer o que alivia o mal-estar causado por um alimento: automedicação **aprendida** |
| Garcia e Koelling 1966, *Psychonomic Science* | `10.3758/bf03342209` | pista (PDF obtido na revisão F, `docs/referencias/F_REVISAO_V2_SEIS_PERGUNTAS.md`) | a ligação entre pista e consequência; gosto com mal-estar aprende com atraso |
| Simone-Finstrom e Spivak 2012, *PLoS ONE* | `10.1371/journal.pone.0034601` | pista | abelhas coletam mais resina depois da infecção da colônia |
| Cremer, Armitage e Schmid-Hempel 2007, *Current Biology* | `10.1016/j.cub.2007.06.008` | pista | imunidade social: o grupo se defende de doença junto |
| Frank et al. 2023, *Nature Communications* | `10.1038/s41467-023-43885-w` | pista | formigas tratam a ferida de companheiras com antimicrobianos: tratar o outro |
| Laumer et al. 2024, *Scientific Reports* | `10.1038/s41598-024-58988-7` | pista | um orangotango trata a própria ferida com uma planta ativa |

**Limite de alegação.** Automedicação animal, aversão gustativa condicionada, imunidade social e agentes artificiais que aprendem a
evitar o que faz mal já estão publicados. Nada aqui pode ser dito como novo sem uma busca própria. O que talvez seja contribuição: num
mesmo agente, com controles (placebo, acoplado), separar perceber o próprio dano, aprender o remédio com atraso e aprender o remédio de
outro pet.

## 10. Decisões do Matheus

| # | decisão | recomendação |
|---|---|---|
| DR-1 | O primeiro sentido | olfato: já existe no mapa e pesa no forrageio. Audição pede som no mundo; visão muda quase tudo de uma vez |
| DR-2 | De onde vem a doença | de comer uma fruta contaminada; sem contágio no começo |
| DR-3 | Cura espontânea | sim, lenta, e o remédio acelera. Por isso o placebo é obrigatório |
| DR-4 | O remédio é amargo no pet saudável | sim: é o que faz do aprendizado condicional um teste de verdade |
| DR-5 | Como passar adiante | observação primeiro, sinal depois, entrega por último e entre irmãos |
| DR-6 | O dono pode tratar | sim, como braço separado na pesquisa e opcional no jogo |
