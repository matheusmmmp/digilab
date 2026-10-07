# Convivência no mundo físico: dois pets no mesmo mapa

Status: **IDEIA** (Matheus, 2026-10-07). Registra o pedido de ter dois pets interagindo, ligando a escada de cognição social
(`docs/futuro/cognicao_social.md`) ao mundo físico (`docs/futuro/mundo_fisico.md`). **Não autoriza implementação**, não muda nenhum
experimento e não decide nenhum desenho: cada degrau entra com tarefa e plano de análise próprios, como sempre.

## 1. A ideia

Hoje cada vida é **um pet e um dono**. O mundo físico já tem o mapa, as árvores que derrubam frutas, a comida que o jogador solta e a bola
como objeto (`digilab/mundo.py`, `web/app/motor/mundo.ts`). A convivência põe **dois pets no mesmo mapa**, vendo um ao outro, disputando a
mesma fruta, brincando com a mesma bola e, mais tarde, avisando um ao outro.

O mapa dá à escada social o que ela não tinha: um lugar onde a informação é concreta ("tem fruta embaixo daquela árvore") e onde ver o
outro agir já é informação, antes de qualquer mensagem.

**De onde vem a ideia, como inspiração de desenho e não como evidência** (regra da skill `literatura-digilab`):
- **Creatures 3:** várias norns vivem no mesmo mundo, com drives de solidão e de aglomeração, e o cérebro reconhece outras norns como
  categoria de objeto (`docs/futuro/mundo_fisico.md`, seção 4).
- **Nintendogs:** o jogador tem mais de um cão em casa; nos passeios o cão encontra outros cães, e o encontro sem fio traz o cão de outro
  jogador de visita.
- **Animal Crossing:** o mapa é um lugar compartilhado, e o que um deixa no chão o outro pode pegar.

## 2. O que já existe e o que falta

**Já existe:**
- **O mapa e os objetos com posição,** em inteiros, com replay bit a bit (W-MUNDO-FISICO) e paridade com o TypeScript (W-MUNDO-WEB, G-PAR).
- **As quedas das árvores não dependem do pet** (G-NUMS): dois pets veriam as mesmas quedas, sorteadas pelo fluxo próprio do mundo.
- **No TypeScript o mundo já é um componente,** que recebe o estado do pet e devolve o estado depois. É a forma que um mundo com dois pets
  pede.
- **A percepção sem acesso privilegiado** (`PercepcaoMundo`: o que está a até 6 células e o cheiro), que é onde o outro pet entraria.
- **O cérebro escolhe o alvo, e o motor anda** (`escolher_alvo`), sem ação nova. As escolhas sociais caberiam como alvos.

**Falta, e é mudança de motor, não de mecânica** (o risco de escopo da `cognicao_social.md`, seção 10):
- **Um mundo compartilhado.** No Python o mundo vive dentro do `MotorMundo`, que é de um pet. Seria preciso separar o mundo (árvores,
  comidas, bola) num componente, como no TS, com o gate de que **um pet sozinho continua byte a byte**. `engine.py` não muda: cada pet
  continua com o próprio motor, e o mundo fica por fora.
- **A ordem dentro do tick.** Se os dois chegam à mesma fruta no mesmo tick, quem come? A regra tem de ser fixa e registrada: por exemplo,
  quem está mais perto; no empate, um sorteio do fluxo do mundo. Nunca a ordem em que o código chamou os pets.
- **O registro do grupo.** Cada pet tem o próprio log, mas a vida de um depende do que o outro fez. O replay passa a ser do grupo: os dois
  logs e o do mundo, rejogados juntos, passo a passo. É a mesma orquestração que o plano do mundo físico já registrou como custo do
  acoplado recíproco (`docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, A1.6).
- **O outro na percepção.** A posição do outro pet e o que ele está fazendo à vista (comendo, brincando, dormindo), dentro do raio de
  visão, e um cheiro do outro, como os cheiros de cada espécie do Creatures 3. Nunca o estado interno dele.
- **As escolhas sociais como alvos,** sem membro novo no `AcaoPet`:
  - **explorar:** um candidato a mais, "ir até onde o outro está" (seguir);
  - **comer:** a comida perto do outro já é candidata quando vista; o pet ir para onde o outro comeu é o que se quer medir, não uma regra
    escrita;
  - **brincar:** a bola com o outro perto (brincar junto);
  - **chamar atenção:** com o outro como alvo, o lugar do sinal nos degraus de comunicação.

## 3. A escada no mapa

Os degraus seguem a `cognicao_social.md` (seção 1), na ordem em que o mapa permite testar cada um. Os degraus de cima continuam sendo
**pergunta**, não feature: nada de crença, norma ou mentira escrita à mão.

| degrau | o que acontece no mapa | o que pede | o que se mede |
|---|---|---|---|
| **0. Parceiro sintético** | um "pet" do mundo, sem cérebro, anda até as árvores e come; o pet de verdade pode vê-lo | só o mundo de um pet, com um objeto que se move; sem motor de grupo | se o pet vai aonde viu o parceiro comer; com um parceiro **confiável** (vai aonde há fruta) e um **acoplado** (faz o mesmo trajeto, sem relação com a fruta) |
| **1. Dois pets, sem sinal** | os dois forrageiam no mesmo mapa; ver o outro comer é a única informação | o mundo compartilhado, a ordem no tick, o registro do grupo, o outro na percepção | seguir; chegar primeiro; dividir a fruta; brincar junto; o custo de ter um competidor |
| **2. Sinal** | chamar atenção com o outro como alvo, em vocabulário fechado (`COMIDA(aqui)`) | o sinal como evento do mundo; nunca o vetor neural (`cognicao_social.md`, seção 2) | se o sinal muda o que o outro faz; com pouca comida, se aparece o engano operacional da seção 2 |
| **3. Relação** | quem já dividiu, quem tomou, quem avisou certo | vínculo entre pets e memória do outro; os drives de solidão e aglomeração no corpo | escolha de parceiro pelo histórico (reputação, `cognicao_social.md`, 5.6) |
| **4. Tradição e acima** | o que um aprendeu do outro passa ao filho | gerações (fase 3) | fora do horizonte; fica como na `cognicao_social.md` |

**O degrau 0 é o primeiro passo barato.** Ele mede aprendizado social **sem motor de vários pets**: o parceiro é um objeto do mundo com
trajeto sorteado pelo fluxo do mundo, como as quedas. É a versão do mapa do "pet sintético informante" da `cognicao_social.md` (seção 11),
trocando a mensagem do N5 por um comportamento visível.

## 4. Para a pesquisa

- **A pergunta maior ganha uma fonte nova.** Até aqui o pet aprende do herdado (P0), do vivido (P1), do que o dono informa (P2) e do
  feedback do dono (P3). A convivência acrescenta **o aprendido de outro pet**. A `cognicao_social.md` já pede separar as três origens no
  mesmo agente; o mapa dá onde fazer isso.
- **As condições de hoje viram a pergunta clássica.** No **casado** e no **descasado**, o que o outro pet aprendeu vale para este. No
  **mutável**, depois da troca, copiar o outro pode levar à fruta que passou a fazer mal. É a forma do paradoxo de Rogers (1988): o
  aprendizado social só compensa enquanto alguém ainda aprende sozinho e o mundo não mudou demais. Laland (2004) organiza quando copiar.
- **Forragear junto tem teoria própria.** Num grupo, uns procuram comida e outros aproveitam a que os primeiros acharam (produtores e
  aproveitadores, Barnard e Sibly 1981). Ver o outro comer e ir lá é a influência social sobre o forrageio de Galef e Giraldeau (2001). É
  a continuação natural da pergunta do Charnov do mundo físico.
- **Os controles seguem o padrão do projeto.** O parceiro **acoplado** (o mesmo trajeto, sem relação com a fruta) separa "aprendeu do
  outro" de "só tinha companhia", como o P2a separa a informação do contato. Com dois pets reais, o pet sozinho no mesmo mapa e nas mesmas
  sementes é a referência.
- **O dono continua sendo cuidado.** O dono de dois pets solta comida para os dois. Onde ele solta (perto de um, entre os dois, no
  comedouro) vira parte do cuidado, como no mundo físico.

## 5. No jogo

- **Dois pets do mesmo jogador no mesmo mapa** é o caminho mais curto: o Meus pets já guarda vários, e hoje só um fica ativo.
- **A visita do pet de outro jogador** pede rede e uma cópia congelada do outro pet (cérebro e estado do momento). É a mesma peça técnica
  do PvP com ghost (`docs/TODO_INTERACAO_CORPO.md`) e da aura do herói (`docs/futuro/aura_do_heroi.md`). Fica depois.
- **Na tela:** a vista inclinada do mundo físico já comporta dois pets; o mapa da prancha (`docs/estilo_up/pranchas/MapaDesktop.html`,
  `Mapa390.html`) precisaria mostrar de quem é cada pet e, no arrastar da comida, para quem ela foi.
- **Pets v1 a v10 não mudam.** A convivência entraria numa versão de pet nova, como toda mecânica.

## 6. Riscos

- **Escopo.** É a primeira mudança que tira o motor de "um pet e um dono". O degrau 0 existe para medir algo antes de pagar esse custo.
- **Determinismo.** Dois pets no mesmo tick dão muitas ordens possíveis; qualquer regra que dependa da ordem de chamada quebra o replay.
  A regra de conflito e o G1 do grupo vêm antes de qualquer comportamento.
- **Rótulos.** "Seguiu", "dividiu", "enganou" e "amigo" só valem com critério operacional definido antes e medido no registro, como na
  `cognicao_social.md`.
- **Agressão.** O Creatures 3 tem a ação de bater, e disputar comida chama briga. A convivência começa **sem agressão** entre pets; a
  disputa é só quem chega primeiro. Bater entre pets, se um dia entrar, pede decisão própria, pelos mesmos cuidados do tapa
  (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, seção 4).
- **Dobro de cuidado.** Para o jogador, dois pets é o dobro de trabalho. O jogo precisa deixar isso opcional.

## 7. Literatura

Status pelo vocabulário da skill `literatura-digilab`. As marcadas **pista** tiveram os metadados conferidos no Crossref em 2026-10-07
(autores, ano, título e veículo), sem leitura do resumo nem do texto, e **não estão na tabela verificada**: ler antes de citar. As da
`cognicao_social.md` (seção 9) valem aqui com o mesmo status, em especial Mitri, Floreano e Keller 2009 (supressão de informação sobre
comida em robôs) e Bhoopchand et al. 2023 (imitação como transmissão cultural em agentes).

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Rogers 1988, *American Anthropologist* | `10.1525/aa.1988.90.4.02a00030` | pista | aprendizado social só compensa com aprendizes individuais e mundo estável (o mutável) |
| Laland 2004, *Learning & Behavior* | `10.3758/bf03196002` | pista | estratégias de quando e de quem copiar |
| Barnard e Sibly 1981, *Animal Behaviour* | `10.1016/s0003-3472(81)80117-0` | pista | produtores e aproveitadores no forrageio em grupo |
| Galef e Giraldeau 2001, *Animal Behaviour* | `10.1006/anbe.2000.1557` | pista | influência social no forrageio: mecanismos e funções |

**Limite de alegação.** Aprendizado social, forrageio em grupo e comunicação entre agentes artificiais já estão publicados. Nada aqui pode
ser dito como novo. O que talvez seja contribuição continua o da `cognicao_social.md`: separar no mesmo agente, com controles, o herdado,
o vivido e o aprendido de outros pets, depois de uma busca própria.

## 8. Decisões do Matheus

| # | decisão | recomendação |
|---|---|---|
| CV-1 | O primeiro passo | o degrau 0, o parceiro sintético no mapa, com o acoplado: mede aprendizado social sem motor de grupo |
| CV-2 | De onde vem o segundo pet no jogo | outro pet do mesmo jogador; a visita de outro jogador fica com o PvP com ghost |
| CV-3 | Disputa entre pets | só quem chega primeiro; bater entre pets fica fora até decisão própria |
| CV-4 | Sinal entre pets | nenhum no degrau 1; no degrau 2, vocabulário fechado, com a LLM fora da decisão |
| CV-5 | Solidão e aglomeração no corpo | no degrau 3, junto com a relação; antes, o pet com companhia não precisa de drive novo |
| CV-6 | Onde entra | depois da validação do mundo físico e do corpo (rodadas 17 e 18), porque o degrau 0 usa o mapa e a percepção deles |
