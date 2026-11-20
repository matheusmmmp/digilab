# Vida do pet: referências de pets virtuais e jogos de criação (2026-11-04)

**Status:** PROPOSTO. Pesquisa de referências, só documento (`docs/TAREFA_V3_VIDA_PET_REF.md`). Nenhum código, nenhuma tela, nenhum número
de jogo. A ordem da seção 5 é recomendação: decidir é do Matheus.

**O pedido (Matheus, 2026-11-04):** juntar referências de outros tamagotchis e sistemas de criação de pet, e de interações que atraem o
jogador e criam vínculo, para que ele "não fique só olhando uma tela de um cara parado e às vezes tem que fazer uma decisão".

**Para que serve:** alimentar a frente "Vida do pet" do Gerente da V3:
- **passo 1:** o pet se move na vista (outra sessão, em andamento);
- **passo 2:** cada ação com uma cena visível, e a reação ao toque, só na vista;
- **passo 3:** ações novas no cérebro, que é pesquisa, com plano e paridade Python/web.

A regra que vale em todo o documento: **a física e as decisões ficam no motor, e a tela só desenha o que o motor registra**
(`docs/PRODUTO_VISAO.md`, seção 1).

## 0. Como ler as fontes

**Os níveis de fonte de cada mecânica de jogo:**
- **oficial:** o fabricante ou o estúdio (site do produto, postmortem do estúdio);
- **imprensa:** veículo jornalístico ou de crítica (Engadget, TechCrunch, Kotaku, Siliconera, CGMagazine, AFP/Jakarta Post);
- **fã:** wiki colaborativa ou de fã (Wikipédia, Serebii) e datamine relatado pela imprensa de fã. Pista, nunca evidência
  (`literatura-digilab`: NÃO VERIFICADA EM FONTE PRIMÁRIA);
- **SEM FONTE:** lembrança comum sobre o jogo que não conferi numa página aberta nesta sessão. Fica marcado para não virar fato.

Todo link da seção 2 foi aberto nesta sessão (2026-11-04) e lido pelo resumo do WebFetch, não página a página. Os que não abriram (403,
404, tempo esgotado) não aparecem como fonte.

**A literatura acadêmica** só entra pela tabela verificada do projeto (`docs/referencias/referencias_verificadas.csv`, a skill
`literatura-digilab`), com o DOI, e diz só o que a coluna `o_que_sustenta` autoriza. A verificação dela foi por metadados e resumo, não por
texto completo. Ela está na seção 6.

**Nenhuma linha deste documento diz que algo do Digilab é inédito.** Onde um jogo já faz o que o Digilab faz, isso está escrito.

## 1. O que o Digilab já tem (o ponto de partida)

Levantado no motor do jogo (`web/app/motor/`), na `main` em `ddf1ef0`. Só o que existe; o que não achei está como "não encontrado".

| peça | o que existe | onde |
|---|---|---|
| ações do pet | `ocioso`, `dormir`, `comer`, `brincar`, `chamar_atencao`, `explorar`, `emburrar`; decididas pelo cérebro A (instinto + aprendizado); cada uma muda o estado (brincar sobe o humor e gasta energia, explorar gasta energia, emburrar baixa o humor) | `motor/constantes.ts:183`, `motor/lobos.ts:87`, `motor/estado.ts:46` |
| ações do dono | `alimentar` (desde a v12, a ração vai ao comedouro), `limpar`, `brincar`, `acariciar`, `tapa` (vai sair dos botões), `tratar_lesao` | `motor/constantes.ts:188`, `motor/motor.ts:677` |
| o toque | `acariciar` e `tapa` são gestos que só agem no corpo: o carinho baixa a solidão e o estresse, modulado pelo "medo da mão"; o tapa sobe a dor, o susto e o estresse. **Não há posição do toque** (é um botão) | `motor/motor_corpo.ts:213`, `motor/corpo.ts:568` |
| vínculo | valor em [0, 1] por média móvel: atendimento rápido, coerência do feedback, vontade atendida (comer→alimentar, brincar→brincar, chamar_atencao→acariciar) | `motor/vinculo.ts:13`, `:57` |
| chamados do bebê | fome, higiene e carinho; por relógio ou pelo corpo; a fração atendida decide o ramo do Rookie (sereno ou arisco) | `motor/motor.ts:864`, `:920` |
| corpo químico | fome, desconforto, cansaço, tristeza, dano, tédio, curiosidade, solidão, estresse, dor, susto | `motor/corpo.ts:27` |
| mundo físico | o pet tem posição; bola que rola; ração do jogador; ninho, comedouro e início da bola; visão e cheiro | `motor/mundo.ts`, `motor/constantes.ts:396` |
| intenções com alvo | **só no modular** (o pet de teste v16): comer → comida, brincar → bola, explorar → um ponto, e a busca pelo cheiro; com os fins meta, trocou, sumiu, desistiu e achou | `motor/digibrain/estado.ts:15`, `:120` |
| expressão e fala | o bebê mostra emote, o adulto fala; a fala diz a emoção com a causa ("quando você demorou"), o temperamento, a vontade; nunca inventa causa | `motor/expressao.ts:16`, `:104`, `:157` |
| memória | do dono: demora, bronca, elogio e carinho, filtrados pelo temperamento; no modular, o lugar lembrado e a memória autobiográfica (comida, bola, lugar) | `motor/memoria.ts:63`, `motor/digibrain/mem.ts:16` |
| crescimento e luta | bebê → Rookie → Champion → Ultimate → Mega; medalhas, liga, Salão da Fronteira, combate em tempo real; o pet pode morrer de lesão sem tratar | `motor/motor.ts:746`, `:906` |
| tempo | anda pelo relógio real, na velocidade escolhida; um chamado aberto freia o tempo para 1x | `src/tempo.ts:1` |
| **não encontrado** | o pet notar a presença do dono (abrir o jogo, tempo ausente); a reação a um toque com lugar no corpo; a identidade do dono na memória | — |

**Um achado que muda o passo 3:** duas das quatro ações que o Gerente cita para o passo 3, **investigar um objeto** (explorar → ponto) e
**brincar sozinho** (brincar → bola), já existem como intenções com alvo no modular, no pet de teste v16. Para esse pet, elas são só vista. Para
o pet padrão (o A v11), o cérebro não escolhe o alvo: o `escolher_alvo` dos lobos devolve nulo, e o alvo é o padrão do motor
(`motor/motor_corpo_mundo.ts:19`); aí uma escolha do pet é cérebro.

**Um achado do E0 que pesa no passo 3** (`docs/futuro/v3_espaco_acoes.md`, seção 0, [HIPÓTESE] do próprio documento): o que mais limita o
cérebro A é a arbitragem (a prioridade fixa das regras), não o número de verbos; somar ações ao enum sem abrir a arbitragem daria opções que o
pet quase nunca escolhe.

## 2. O catálogo por jogo ou sistema

Cada jogo em cinco perguntas: **apego** (as interações e os comportamentos que o criam), **sozinho** (o que o pet faz quando o jogador não faz
nada), **toque e presença**, **ritmo** (a volta, a saudade, as notificações) e **o que dá errado**. Depois, as fontes com o nível.

### 2.1 Tamagotchi (o original, 1996)

- **Apego:** medidores de fome e de felicidade; o pet chama a atenção mesmo alimentado e feliz, e o jogador decide se atende ou dá bronca
  (o antigo medidor de disciplina). O cuidado na infância decide o adulto: o bem cuidado sai "mais esperto, mais feliz e pede menos atenção".
- **Sozinho:** pouco além de fazer cocô, adoecer e chamar; o pet recusa comer ou brincar quando doente.
- **Toque e presença:** só botões; não há toque.
- **Ritmo:** relógio real; o estágio avança quando o pet acorda; o original só pausava pelo menu do relógio, e os modelos seguintes trocaram a
  pausa por uma babá paga.
- **O que dá errado:** a morte por descuido; crianças abaladas pela morte do pet, com enterros; escolas proibiram o brinquedo pela interrupção
  das aulas.
- **Fonte:** [Wikipédia, Tamagotchi](https://en.wikipedia.org/wiki/Tamagotchi) (fã).

### 2.2 Tamagotchi Connection, Uni e Paradise

- **Connection (2004):** dois aparelhos se ligam por infravermelho; os pets fazem amizade, jogam, trocam presentes e casam quando a relação
  sobe; o pai cuida do filho e vai embora depois. Fonte: [Wikipédia, Tamagotchi](https://en.wikipedia.org/wiki/Tamagotchi) (fã).
- **Uni (2023):** relógio de pulso com Wi-Fi e um mundo online (Tamaverse): passeios, casamento com outro pet, desfile; três minijogos; babá
  grátis; itens deixados do lado de fora atraem um pet visitante. Críticas: o Tamaverse demorou a mudar, os códigos de 16 dígitos são chatos de
  digitar, e as famílias são mais difíceis de acompanhar. Fonte:
  [Siliconera](https://www.siliconera.com/tamagotchi-uni-is-surprisingly-good-at-being-a-wearable-virtual-pet/) (imprensa).
- **Paradise (2025):** um disco de zoom vai do planeta inteiro ao pet e até a célula dentro dele; o jogador choca um planeta (o "Egg Bang"), o
  cocô vira combustível de viagem, e a doença é tratada no nível da célula; a mistura de genes volta. Fonte:
  [Engadget](https://www.engadget.com/gaming/tamagotchi-paradise-looks-like-the-most-exciting-virtual-pet-toy-in-years-155010892.html)
  (imprensa, prévia, não crítica).
- **O que a série ensina:** a mesma rotina de cuidado cresce para fora (outro pet, um mundo, gerações), não para dentro do pet.

### 2.3 Digimon V-Pet e Pendulum

- **Apego:** cuidado (comer, limpar o cocô, apagar a luz), treino que baixa o peso e sobe a força, e a luta contra o aparelho de outro dono,
  encostando os contatos.
- **Sozinho:** come, dorme, adoece com o cocô acumulado.
- **Toque e presença:** botões; no Pendulum (1998), um pêndulo conta quantas vezes o aparelho é sacudido. **Que a sacudida treina e luta é SEM
  FONTE:** a página aberta só diz que o pêndulo conta.
- **Ritmo:** relógio real, com o sono e a luz.
- **O que dá errado:** o "erro de cuidado" escondido (dormir com a luz acesa) baixa a chance de uma evolução forte; o jogador não vê o erro.
- **Fonte:** [Wikipédia, Digital Monster](https://en.wikipedia.org/wiki/Digital_Monster_(virtual_pet)) (fã). Já previsto pela skill: Digimon
  não serve como evidência de desenho.

### 2.4 Nintendogs (2005)

- **Apego:** acariciar e escovar o cão na tela de toque; dar nome e ensinar truques pela voz (o cão aprende o nome chamado no microfone);
  passear pelo bairro, com cães e presentes no caminho; treinar disco e agilidade.
- **Sozinho:** a página aberta não descreve; o cão fica com fome, sede e sujo pelo relógio real.
- **Toque e presença:** o toque é a interação principal; a voz do dono é a presença.
- **Ritmo:** relógio e calendário do console; o "Bark Mode" troca visitas com quem está perto.
- **O que dá errado:** o descuido piora a condição; a crítica notou a falta de um fim.
- **Fonte:** [Wikipédia, Nintendogs](https://en.wikipedia.org/wiki/Nintendogs) (fã).

### 2.5 Pokémon-Amie (X e Y, 2013) e Refresh (Sun e Moon, 2016)

- **Apego:** acariciar na tela sobe o afeto (de um a cinco corações); dar o doce na boca, e soltá-lo cedo desagrada; cada Pokémon prefere um
  sabor; minijogos.
- **Toque e presença:** **o toque tem lugar no corpo:** algumas partes irritam (os chifres do Charizard, as bochechas do Pikachu), e outras
  machucam (as chamas).
- **O vínculo vira consequência noutra parte do jogo:** o afeto aumenta a chance de efeitos na luta (fala que muda, mais crítico, mais esquiva);
  outros (aguentar um golpe fatal, curar estado, mais experiência) estão listados como não confirmados. Fora da luta online.
- **Sozinho:** Pokémon de amigos visitam; doces deixados no chão viram enfeites.
- **Refresh:** **SEM FONTE** (não abri página que o descreva; a lembrança comum é a limpeza e a cura depois da luta).
- **Fonte:** [Serebii, Pokémon-Amie](https://www.serebii.net/xy/pokemonamie.shtml) (fã). A skill proíbe Pokémon como evidência de precedência
  ou de desenho: aqui é só exemplo de interação.

### 2.6 Chao Garden (Sonic Adventure, 1998; Sonic Adventure 2, 2001)

- **Apego:** o Chao gosta de colo e de carinho e não gosta de ser sacudido, girado ou jogado; come frutas.
- **O fim depende do cuidado:** bem tratado, o casulo fica rosa e o Chao renasce de um ovo **lembrando do jogador**; maltratado, o casulo fica
  cinza e o Chao morre e some do jogo.
- **Sozinho:** no segundo jogo, os Chao interagem entre si e se reproduzem; viram "herói" ou "sombrio" pelo jeito de criar.
- **SEM FONTE:** a evolução pelas partes de animais e o balão de emoção sobre a cabeça (a página aberta não cobre).
- **Fonte:** [Wikipédia, Chao](https://en.wikipedia.org/wiki/Chao_(Sonic)) (fã).

### 2.7 Creatures (1996)

- **Apego:** a mão do jogador faz cócegas para recompensar e dá tapa para punir; o jogador ensina palavras; o norn decide se obedece.
- **Sozinho:** vida autônoma inteira (rede neural, bioquímica, ciclo de vida, reprodução); os Grendels roubam comida e espalham doença.
- **O que dá errado:** a morte permanente; a simulação complexa sem objetivo claro: "mais aquário que jogo" para alguns críticos.
- **Fontes:** [Wikipédia, Creatures](https://en.wikipedia.org/wiki/Creatures_(video_game_series)) (fã); e a literatura verificada:
  Grand e Cliff (1998), `10.1023/a:1010042522104`, e Cliff e Grand (1999), `10.1162/106454699568683` (par). **O corpo químico do Digilab tem
  precedente direto aqui** (o `corpo.ts:27` cita o estilo do Creatures 3).

### 2.8 Neopets (1999)

- **Apego:** criar e vestir o pet (espécie, cor, roupas, poções), o pet do pet, a comunidade (fóruns, guildas, correio).
- **Cuidado sem morte:** o pet não morre de descuido; a saúde ruim só limita o que se pode fazer. A lenda de que o pet sem comida vai para o
  canil é falsa, segundo a página.
- **O que dá errado:** a propaganda embutida em jogos e itens, criticada por mirar crianças.
- **Fonte:** [Wikipédia, Neopets](https://en.wikipedia.org/wiki/Neopets) (fã).

### 2.9 Pou (2012) e My Talking Tom (2013)

- **Pou:** alimentar, vestir, cuidar, no molde do Tamagotchi; cerca de 100 milhões de downloads; o criador conta fãs que tatuaram o Pou. A
  crítica citada: só crianças jogam por muito tempo. **O apagar da luz para dormir, os minijogos e as moedas são SEM FONTE** (a página aberta não
  cobre). Fonte: [Wikipédia, Pou](https://en.wikipedia.org/wiki/Pou_(video_game)) (fã).
- **My Talking Tom:** cuidar do gato enquanto cresce, dar nome e vestir; nos jogos do Tom, fazer cócegas, cutucar e brincar com ele; o Tom
  original repete a voz do jogador, mais aguda. **As reações por parte do corpo (puxar o rabo, o tapa) são SEM FONTE.** O que dá errado: em
  2015, a autoridade de propaganda do Reino Unido decidiu que um anúncio adulto apareceu a crianças pelo app. Fonte:
  [Wikipédia, Talking Tom & Friends](https://en.wikipedia.org/wiki/Talking_Tom_%26_Friends) (fã).

### 2.10 Seaman (1999)

- **Apego:** a conversa pela voz; no começo o bicho só repete o que se diz, e o vocabulário cresce com ele; pergunta o aniversário e conta o que
  aconteceu naquele dia; insulta e faz comentários antipáticos mesmo manso.
- **Toque e presença:** o microfone; a versão japonesa comentava os saves do cartão de memória, retirado da inglesa por privacidade.
- **Ritmo:** relógio real; é preciso voltar todo dia, senão ele pode morrer.
- **Sozinho:** os bichos da fase inicial se juntam num lado do aquário; os da fase seguinte se matam até sobrarem dois.
- **Fonte:** [Wikipédia, Seaman](https://en.wikipedia.org/wiki/Seaman_(video_game)) (fã).

### 2.11 Animal Crossing (os vizinhos)

- **Apego:** conversa, cartas, troca, esconde-esconde; o jogador escolhe o bordão de alguns vizinhos.
- **Sozinho:** a vila vive pelo relógio e pelo calendário real (feriados, a árvore que cresce, o músico de certas noites).
- **Presença e ausência:** **cada vizinho reage diferente à volta** depois de dois meses fora: um fica encantado, outro inseguro, outro
  compreensivo, um erra quanto tempo passou; aparecem baratas em casa e mato nas áreas não construídas; ninguém se mudou. Fonte:
  [Kotaku](https://kotaku.com/what-happens-when-you-abandon-your-animal-crossing-new-1844574997) (imprensa).
- **A amizade como número escondido:** pelo datamine relatado, a amizade vai de 0 a 255, começa em 25, e a chance de um vizinho pedir para se
  mudar cai com ela. Fonte:
  [Nintendo Everything](https://nintendoeverything.com/animal-crossing-new-horizons-datamine-provides-details-about-how-villagers-move-out/)
  (fã: datamine pela imprensa de fã).
- **O que dá errado:** o Mr. Resetti dava bronca em quem desligava sem salvar (saiu com o salvamento automático). Fonte:
  [Wikipédia, Animal Crossing](https://en.wikipedia.org/wiki/Animal_Crossing) (fã).
- **SEM FONTE:** que o vizinho lembra do jogador depois de se mudar (só fóruns e guias, não abertos).

### 2.12 Neko Atsume (2014)

- **Apego:** pôr comida e brinquedos no quintal, ver os gatos usarem, fotografar, montar o álbum; os gatos deixam peixes (a moeda) e lembranças.
- **Sozinho:** **os gatos vêm e vão por conta própria, mesmo com o app fechado**; sem comida, não vêm.
- **Ritmo:** a volta curta para conferir a comida, quem chegou e os peixes; adiantar o relógio do celular deu errado (os peixes sumiram).
- **O que dá errado:** lento; sem fim; sem punição.
- **Fontes:** [CGMagazine](https://www.cgmagonline.com/articles/neko-atsume-why-im-the-office-cat-lady) (imprensa);
  [Wikipédia, Neko Atsume](https://en.wikipedia.org/wiki/Neko_Atsume) (fã).

### 2.13 Finch (aplicativo de autocuidado)

- **Apego:** o pássaro cresce quando o jogador cumpre metas da vida real (beber água, escrever um pouco); as pedras ganhas compram roupas e
  móveis; o pássaro sai em "pequenas aventuras".
- **Presença:** o pássaro aparece durante o dia com incentivo e lembretes e comemora a meta cumprida.
- **O que dá errado (e o que evita):** **não há punição:** o app não dá bronca nem envergonha; a única perda é a sequência de dias.
- **Fonte:** [Engadget](https://www.engadget.com/apps/this-self-care-virtual-pet-is-helping-me-get-my-act-together-160027169.html) (imprensa).

### 2.14 Aibo e Moflin (robôs)

- **Aibo (ERS-1000, 2018):** reconhece até 100 rostos, sensores de toque na cabeça, no queixo e nas costas, aprende um truque; precisa de nuvem e
  assinatura. Fonte: [Wikipédia, Aibo](https://en.wikipedia.org/wiki/Aibo) (fã). A Sony fala dos olhos que mostram o sentimento e de centenas
  de gestos: [aibo, Features](https://us.aibo.com/feature/feature1.html) (oficial).
- **O apego que sobra quando o produto acaba:** a Sony fechou a clínica do aibo antigo em março de 2014; uma empresa de conserto fez cerimônias
  budistas para cerca de 800 aibos; os donos dizem alívio por haver uma prece. Fonte:
  [Jakarta Post (AFP), 2018](https://www.thejakartapost.com/life/2018/04/27/fido-funeral-in-japan-a-send-off-for-robot-dogs) (imprensa).
- **Moflin (Casio, 2024):** as emoções começam limitadas, com "movimentos imaturos", o apego vem por volta do dia 25 e uma gama clara de emoções
  por volta do dia 50 (segundo a Casio, pela crítica); o app mostra quatro traços (enérgico, alegre, tímido, carinhoso) e frases curtas ("parece
  relaxado"); não entende a fala, mas distingue a voz do dono; assusta com barulho alto; não gosta de ficar de barriga para cima. A crítica: "o
  maior problema é que não é um pet de verdade". Fonte:
  [TechCrunch, 2025](https://techcrunch.com/2025/10/21/i-spent-a-month-living-with-a-430-ai-pet-the-casio-moflin/) (imprensa).

### 2.15 Black & White (2001), a criatura

- **Apego:** o jogador acaricia para aprovar e dá tapa para desaprovar, e a criatura ajusta o que faz depois; lembra como foi tratada; aprende
  tarefas (abastecer o armazém, fazer milagres); as coleiras a prendem num lugar ou a puxam para o bem ou para o mal.
- **Personalidade visível no corpo:** a criatura má ganha olhos brilhantes, presas e garras; a boa fica roxa e brilha suave.
- **O que dá errado:** o microgerenciamento; a GameSpy a chamou de jogo mais superestimado (2003), citando o pouco uso das criaturas.
- **Fontes:** [Wikipédia, Black & White](https://en.wikipedia.org/wiki/Black_%26_White_(video_game)) (fã); o postmortem de Molyneux (Gamasutra,
  2001, cinza VERIFICADA na tabela). **A regra 3 da skill vale aqui:** "ensinado, não roteirizado" já foi dito por Black & White.

### 2.16 Spore (2008), a fase da criatura

- **Apego:** a criatura é desenhada pelo jogador no editor; imitar cantar e dançar torna outras espécies aliadas.
- **O que dá errado:** a crítica achou as primeiras fases rasas e passageiras.
- **Fonte:** [Wikipédia, Spore](https://en.wikipedia.org/wiki/Spore_(2008_video_game)) (fã). **A ligação entre autoria e apego é SEM FONTE
  para o Spore**; a fonte verificada para o efeito da autoria é o efeito IKEA (seção 6).

### 2.17 The Sims 4: Cats & Dogs (2017)

- **Apego:** os Sims alimentam, brincam e treinam o pet, e isso constrói um vínculo; três traços por pet mudam como ele age e reage.
- **Sozinho:** **o jogador não controla o pet** (nem por trapaça); o pet age por conta própria.
- **O que dá errado:** a clínica veterinária fica fácil e sem graça, segundo uma crítica.
- **Fonte:** [Wikipédia, The Sims 4: Cats & Dogs](https://en.wikipedia.org/wiki/The_Sims_4:_Cats_%26_Dogs) (fã).

## 3. Os padrões que se repetem

Cada padrão com os jogos da seção 2 que o mostram. A leitura do "por que funciona" é minha, SEM FONTE, salvo onde a seção 6 diz outra coisa.

| # | padrão | o que é | onde aparece |
|---|---|---|---|
| P1 | **o pet nota você** | a chegada, a voz ou o rosto do dono mudam o que o pet faz; a volta depois da ausência tem uma reação | Animal Crossing (cada vizinho reage à volta), aibo (rostos), Moflin (a voz do dono), Nintendogs (o nome pela voz), Finch (aparece com lembretes) |
| P2 | **rotina e surpresa** | o pet vive sem o jogador, com um ritmo legível (dormir, comer, passear) e coisas que acontecem sozinhas | Neko Atsume (os gatos vêm com o app fechado), Animal Crossing (a vila pelo relógio), Creatures e Chao (vida autônoma entre si), Sims (o pet não é controlado), Seaman (os bichos no aquário) |
| P3 | **o toque direto** | tocar o pet na tela ou no corpo, com reação imediata; muitas vezes com lugar: partes que agradam e partes que irritam | Pokémon-Amie (partes que irritam), Nintendogs, aibo (cabeça, queixo, costas), Moflin (não gosta de barriga para cima), Chao (colo sim, sacudir não), Talking Tom (cócegas, cutucar) |
| P4 | **a personalidade visível** | o temperamento e o jeito de criar aparecem no corpo e no comportamento, não só num número | Black & White (o corpo muda com o caráter), Chao (herói ou sombrio), Moflin (quatro traços no app), Sims (traços), Tamagotchi e V-Pet (o adulto depende do cuidado) |
| P5 | **a memória de você** | o pet lembra o que o dono fez e mostra isso | Chao (renasce lembrando), Black & White (lembra como foi tratada), Seaman (o aniversário), Animal Crossing (a amizade que segura o vizinho) |
| P6 | **as conquistas e a coleção** | álbum, formas, presentes, coleção de visitantes | Neko Atsume (álbum, lembranças), Tamagotchi e V-Pet (as formas), Amie (corações), Finch (roupas e móveis) |
| P7 | **o cuidado sem punição pesada** | descuidar tem consequência visível, mas não apaga o pet nem envergonha o jogador | Finch (sem bronca), Neopets (não morre), Neko Atsume (sem punição), Animal Crossing (baratas e mato, ninguém sai); o contrário: Tamagotchi, Seaman, Creatures e Chao (morte) |
| P8 | **a fala e as expressões** | o pet diz ou mostra o que sente e por quê | Seaman (fala que cresce), Moflin (frases curtas no app), aibo (os olhos), Talking Tom (repete a voz), Amie (a fala da luta muda com o afeto) |
| P9 | **o ensino visível** | o dono ensina e vê o pet usar o que aprendeu | Black & White (acariciar e tapa, tarefas), Creatures (palavras, cócegas e tapa), Nintendogs (truques pela voz), aibo (um truque) |
| P10 | **o vínculo com consequência fora do cuidado** | o apego muda outra parte do jogo | Amie (efeitos na luta), Chao (renascer ou morrer), Animal Crossing (quem fica na vila) |
| P11 | **o mundo maior que o pet** | outro pet, visitas, casamento, gerações | Tamagotchi Connection, Uni e Paradise, Chao (os Chao entre si), Neopets (comunidade), Creatures (troca de norns) |
| P12 | **o ritmo da volta** | relógio real, sessões curtas, o motivo para abrir de novo | todos os de relógio real; Neko Atsume e Finch com a volta curta e sem culpa; Tamagotchi e Seaman com a volta obrigatória |

**O que dá errado, junto (os avisos da seção 2):**
- **a culpa e a morte** (Tamagotchi, Seaman): apego forte, mas também abalo, e jogador que larga;
- **a regra escondida** (o erro de cuidado do V-Pet, a amizade do Animal Crossing): o jogador não sabe por que o resultado saiu;
- **o aquário** (Creatures, Neko Atsume): a vida autônoma sem o jogador ter o que fazer cansa; o oposto, o **microgerenciamento** (Black & White),
  também;
- **a casca rasa** (Spore, o Tamaverse do Uni, a clínica dos Sims): a mecânica nova que não fica com profundidade;
- **o dinheiro e a propaganda** (Neopets, Talking Tom): fora do escopo do Digilab, mas é o aviso do gênero;
- **a dependência do fabricante** (aibo antigo): o vínculo sobrevive ao produto; o Digilab, com save local e replay, não tem esse risco do mesmo jeito.

## 4. Cada padrão contra o Digilab

Três colunas: **só vista** (já está no motor e falta mostrar), **cérebro** (precisa de ação ou evento novo, Python primeiro, com plano e
paridade) e **não serve** (com o porquê).

| padrão | só vista (o motor já registra) | cérebro (ação ou evento novo) | não serve, e por quê |
|---|---|---|---|
| P1 o pet nota você | o pet que acorda ou chama quando um chamado abre; a reação depois de um chamado perdido (o motor tem o `tdc` e a regra `abandono` em `lobos.ts:93`, que já escolhe `chamar_atencao` ou `emburrar` quando o dono some) | **a presença do dono como evento** (abrir o jogo, o tempo fora): não existe; precisa entrar no log para o replay, e o cérebro precisaria reagir a ela | **a câmera e o rosto** (aibo): privacidade, e o navegador não é o lugar; **a voz** (Nintendogs, Seaman): o mesmo, e a fala já tem o caminho da LLM gravada |
| P2 rotina e surpresa | **cada ação do pet com uma cena** (ocioso, dormir, comer, brincar, explorar, emburrar, chamar_atencao) e a caminhada no mundo (o passo 1); no v16, as intenções com alvo (ir à bola, a um ponto, procurar pelo cheiro) e os fins delas (achou, desistiu, sumiu) já são eventos | **vaguear, seguir o dono, investigar, brincar sozinho** no A v11 (onde o alvo é o padrão do motor, não uma escolha do pet); a visita de fora (Neko Atsume) seria mundo novo | **a vida que acontece só na tela** (o pet "brinca" na vista sem o motor ter decidido): fere a regra de que a tela só desenha o que o motor registra |
| P3 o toque direto | **tocar o pet na tela dispara o `acariciar` que já existe** (o mesmo evento do botão, sem posição); a reação mostrada sai do que o corpo já calcula: a solidão e o estresse que caem, e o "medo da mão" que modula (`corpo.ts:568`) | **o toque com lugar no corpo** (partes que agradam e que irritam, Amie e aibo): evento novo com posição, e o corpo e o cérebro reagindo à parte; idem o "toque ruim" (sacudir, Chao) no lugar do tapa | **o tapa como gesto de toque** na tela: o tapa vai sair dos botões; trazê-lo de volta pelo toque desfaz a decisão |
| P4 a personalidade visível | o ramo sereno ou arisco, o temperamento e o caráter na postura e no ritmo da cena; o paladar (gostos por pet) na cena de comer | o corpo que muda com o caráter (Black & White) seria regra de jogo nova: motor e paridade | — |
| P5 a memória de você | a fala já diz a emoção com a causa ("quando você demorou"); a memória do dono (demora, bronca, elogio, carinho) e a do modular (o lugar onde achou comida) podem aparecer como lembrança na cena (o pet que vai direto ao lugar lembrado) | a identidade do dono (quem é o dono, não só o que ele fez): não existe | renascer lembrando (Chao) depende da genética e da linhagem: fica para o G0 e o resto |
| P6 conquistas e coleção | as formas já alcançadas, as medalhas, um **diário ou álbum dos momentos tirado do log** (o replay já refaz qualquer instante) | — | a moeda, a loja e a coleção paga (Neko Atsume, Finch): fora do escopo e do tom |
| P7 cuidado sem punição pesada | mostrar a consequência do descuido no corpo (o pet sujo, cansado, emburrado) antes da morte; a morte já é só por lesão (sem tratar, ou lesões demais nas lutas) | se o Matheus quiser trocar a morte por outra consequência, é regra de jogo (motor, paridade, versão de pet) | a culpa como motor da volta (Tamagotchi, Seaman): o que mais aparece como "o que dá errado" |
| P8 fala e expressões | os emotes do bebê e as falas do adulto já existem; a expressão no rosto ou no corpo pode sair do corpo químico (tédio, solidão, susto), que o motor já calcula mas não mapeia para expressão | uma fala nova só com o que o registro sustenta (a regra da M6) | a fala que inventa causa: proibida pela regra da expressão |
| P9 o ensino visível | o treino e o aprendizado já existem; a cena pode mostrar o pet repetindo o que o dono reforçou | uma ação ensinável nova (o truque) é cérebro | "ensinado, não roteirizado" como diferencial: proibido pela regra 3 da skill |
| P10 vínculo com consequência | o vínculo já existe no motor; mostrá-lo (a postura perto do dono) é vista | o vínculo mudando a luta (Amie) seria regra de combate nova, e o combate tem rodada de equilíbrio própria | — |
| P11 mundo maior | — | dois pets no mesmo mundo existem na pesquisa (`grupo.Grupo`), não no jogo | multiplayer, visitas online, casamento entre jogadores: fases posteriores (`docs/PRODUTO_VISAO.md`, seção 4) |
| P12 o ritmo da volta | o freio do tempo no chamado já existe (`src/tempo.ts`) | o tempo fora do jogo como evento (P1) | **as notificações** do navegador: fora do escopo agora; o pet que "cobra" a volta repete a culpa do P7 |

## 5. A recomendação para o Matheus

Ordenada por frente. Em cada item, o **custo de errar**: o que acontece se o item estiver errado ou for feito antes da hora.

### 5.1 O passo 2 da "Vida do pet": só vista

1. **Uma cena por ação do pet, a começar pelas sete do `ACOES_PET`.** É o que mais ataca o "cara parado": hoje o motor já decide e
   registra a ação a cada passo, e a tela não a mostra como cena. Ordem sugerida: dormir, comer, brincar, explorar, emburrar, chamar_atencao,
   ocioso (o ocioso por último, porque é o que mais tenta a inventar vida na tela). **Custo de errar:** baixo; é vista, sem log, sem save. O
   risco é a cena prometer mais do que o motor fez (o pet que "escolhe" a bola na tela quando, no A v11, o alvo é o padrão do motor). Regra:
   a cena desenha o verbo e o alvo que o motor registrou, e nada além.
2. **O toque no pet dispara o `acariciar` que já existe, com a reação tirada do corpo.** O padrão P3 está em quase todo jogo da seção 2.
   Sem lugar no corpo: um toque no pet é o mesmo evento do botão. A reação mostrada (relaxar, ou recuar quando o medo da mão está alto) sai
   do que o corpo calculou depois do evento. **Custo de errar:** baixo a médio. Se o toque gerar um evento diferente do botão, o replay e a
   paridade quebram; se a reação vier de uma regra da tela e não do corpo, a tela passa a decidir. O tapa não volta pelo toque (P3, não serve).
3. **A expressão pelo corpo químico** (tédio, solidão, susto, cansaço) e pelo ramo e temperamento na postura. **Custo de errar:** baixo, mas
   o mapa corpo → expressão é uma escolha de desenho com números (limiares): eles nascem PROPOSTOS e vão ao Matheus, não ficam escondidos no CSS.
4. **No pet de teste v16, as intenções com alvo como cena** (ir à bola, investigar um ponto, procurar pelo cheiro, desistir). Já são eventos do
   modular. **Custo de errar:** baixo; só o laboratório vê. É também o jeito barato de ver se "investigar" e "brincar sozinho" entusiasmam antes de
   levar ao cérebro do pet padrão.
5. **Um diário de momentos tirado do log** (o primeiro sono, a primeira bola, a forma nova), no padrão P6. **Custo de errar:** baixo; o log já é
   a fonte. Fica depois dos itens 1 a 3, porque não resolve o pet parado.

### 5.2 O passo 3: ações novas no cérebro (Python primeiro, plano e paridade)

1. **Antes de somar verbos, decidir se o passo 3 é o modular ou o A.** Dois dos quatro verbos (investigar e brincar sozinho) já existem como
   intenções com alvo no modular; o E0 diz que somar verbos ao A sem abrir a arbitragem dá opções quase nunca escolhidas
   (`docs/futuro/v3_espaco_acoes.md`, [HIPÓTESE]). **Recomendação:** o passo 3 parte do modular, com o v16 (item 5.1.4) como prova de vista.
   **Custo de errar:** alto. Somar ações ao `AcaoPet` do A muda o enum, o bandit congelado não pode mudar, e cada versão de pet nova fica para
   sempre; escolher o modular cedo demais amarra a vida do pet a um cérebro que ainda não é o padrão (a D-C1-3 está aberta).
2. **Vaguear** (andar sem alvo de necessidade, pelo tédio ou pela curiosidade que o corpo já tem). É o mais próximo do P2 e o que mais
   aparece na tela. **Custo de errar:** médio. Se o vaguear ganhar das necessidades, o pet some do comedouro; precisa de guarda (a do
   comedouro da C3 é o modelo).
3. **Seguir o dono** depende de um evento de presença do dono (P1) que não existe: o dono não tem posição no mundo. **Custo de errar:** alto se
   feito antes do evento de presença; o pet "seguiria" uma coisa que o motor não registra.
4. **O toque com lugar no corpo** (P3, a coluna cérebro). **Custo de errar:** médio; é evento novo no log, versão de pet nova e paridade, por
   um ganho que o item 5.1.2 já entrega em boa parte.

### 5.3 O resto

- **A presença do dono como evento** (abrir o jogo, o tempo fora): é o que destrava o P1 e o "seguir o dono", e o jeito de o pet "notar você"
  sem câmera nem voz. Precisa de decisão de desenho antes: o tempo fora entra no log como avanço comum ou como um evento próprio. **Custo de
  errar:** alto; mexe no replay.
- **A consequência do descuido sem a culpa** (P7): decidir se o descuido continua só no corpo e no ramo do Rookie, com a morte só por lesão (`motor/motor.ts:746`).
  **Custo de errar:** médio; é a regra de jogo que mais pesa na volta do jogador, segundo o catálogo (seção 3).
- **Dois pets no jogo, visitas, gerações** (P11): fases posteriores; o G0 da genética já anda.
- **As notificações:** não agora. **Custo de errar** de fazer cedo: o pet vira cobrança.
- **Não fazer:** câmera, microfone, moeda, loja, propaganda.

## 6. O que a literatura verificada sustenta

Só as linhas da tabela do projeto, no que a coluna `o_que_sustenta` autoriza.

| referência | DOI | o que autoriza dizer aqui |
|---|---|---|
| Dodd, Fowler e Lottridge (2025), revisão narrativa de pets virtuais | `10.1016/j.entcom.2025.100958` | é a porta de entrada do que já se estudou sobre apego, cuidado e abandono de pets virtuais; **não li o texto**: não tiro dela nenhuma mecânica |
| Chesney e Lawson (2007) | `10.1075/is.8.2.09che` | o vínculo com um pet virtual é mensurável, mas não equivale ao de um pet real |
| Rault (2015) | `10.3389/fvets.2015.00011` | compara pets vivos, robôs e virtuais; serve para não superestimar o apego a um agente de software |
| Kaplan (2000), sem DOI | — | a resistência e a inutilidade do pet artificial são parte do valor do vínculo; ecoa o "não controlar o pet" dos Sims e o Moflin que não obedece |
| Norton, Mochon e Ariely (2012), o efeito IKEA | `10.1016/j.jcps.2011.08.002` | o esforço próprio aumenta a valorização: a base do apego por autoria (o ensino, P9) |
| Marsh, Kanngiesser e Hood (2018) | `10.1016/j.cognition.2017.10.012` | o efeito IKEA depende de a tarefa dar certo: um pet mal treinado pode valer menos, não mais. Pesa no P9 e no P7 |
| Thomaz e Breazeal (2008) | `10.1016/j.artint.2007.09.009` | pessoas reais ensinam guiando e dando recompensa antecipatória: um toque que só "avalia" depois pode não ser como o jogador quer ensinar |
| Oudeyer e Kaplan (2007) | `10.3389/neuro.12.006.2007` | separa a motivação intrínseca (novidade, progresso) da recompensa externa: o vaguear e o investigar do passo 3 são do primeiro tipo |
| Grand e Cliff (1998); Cliff e Grand (1999) | `10.1023/a:1010042522104`; `10.1162/106454699568683` | o Creatures já tinha rede neural, bioquímica e reprodução num pet de entretenimento: precedente do corpo químico do Digilab |
| Molyneux (2001), postmortem de Black & White, cinza | — | a criatura que aprende e age sozinha, com a personalidade formada no uso |

**Não localizado nesta sessão:** estudo revisado por pares sobre qual mecânica (toque, rotina, memória) aumenta o apego a um pet virtual.
A revisão de Dodd et al. é o lugar para procurar; ler o texto completo dela é a lacuna desta pesquisa.

## 7. Limites

- **As fontes de jogo são quase todas de fã ou de imprensa,** e li o resumo das páginas, não o texto inteiro. Uma mecânica marcada (fã) é pista.
- **Não joguei nenhum dos jogos;** a experiência descrita é a das fontes.
- **Ficaram fora:** a página do Pokémon Refresh, a do Pendulum, a crítica do Tamagotchi Paradise (403) e a do Tamagotchi Uni no The Verge (bloqueada),
  e a do aibo na NPR (tempo esgotado).
- **O inventário do motor** (seção 1) foi feito por leitura do código na `main` `ddf1ef0`; não rodei o jogo. A seção 1 diz "não encontrado" onde
  não achei, o que não prova que não existe.
- **A leitura dos padrões e o "por que funciona"** são meus, SEM FONTE, salvo a seção 6.
