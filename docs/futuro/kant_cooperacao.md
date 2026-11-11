# Kant na cooperação dos pets: a proposta (2026-11-11, PROPOSTA, Claude Code, Opus 5.5)

**Status: PROPOSTA.** Nada aqui é decidido nem tem código. Esta proposta liga a busca bibliográfica de 2026-11-11 às etapas que a
`docs/TAREFA_V3_COOPERACAO.md` já deixa para depois: a CO6 (a reputação na percepção do cérebro) e a CO7 (os deveres como escudo, por
estágio). Ela também deixa desenhada uma etapa futura, a dos pets de computadores diferentes. **A coordenação do código continua com a
frente COOPERACAO** (o Gerente da V3). Este documento é o insumo dela, não uma frente paralela.

**De onde vem:** o Matheus pediu, em 2026-11-11, um plano a partir da busca "Kant, cooperação e pets em rede" e que ele já começasse. A
busca está no vault, em `DigiLab — Revisão de escopo/BUSCA_KANT_COOPERACAO_2026-11-11.md` (fora do repositório), com 56 obras, cada uma
com o status. As referências abaixo são as dela, com o DOI. A nota tem os resumos e as ressalvas. **Nenhuma alegação de novidade.**

## 0. O que já está decidido e não muda aqui

- **D-MM-1:** a moral é híbrida. A felicidade do corpo escolhe entre as ações permitidas, e os deveres entram como restrição, crescendo até
  a lei kantiana no Mega.
- **D-MM-14, mantida pelo Matheus em 2026-11-11** ("Fica a D-MM-14"): a felicidade é lexicográfica. Primeiro o piso de cada pet, depois a
  média, nunca a soma. Isso vale para qualquer medida de "bem maior" desta proposta.
- **D-MM-8:** a pontuação é o efeito medido pelo motor, sem número na tela e sem nota do dono.
- **D-MM-10:** nenhuma correção mexe nos stats da luta nem no corpo.
- **D-MM-12:** a visita entre donos espera o modo multijogador. A etapa em rede (seção 5) só começa se o Matheus reabrir a D-MM-12.
- **CO-3:** a CO3 só mede. A decisão do pet muda só na CO6 e na CO7, cada uma com o ok do Matheus.
- **As regras do repositório:** mecânica nova atrás de chave desligada, com a vida de hoje saindo byte a byte e o gabarito num commit antes;
  o Python primeiro e a paridade no web; a LLM só como voz; nenhuma run sem plano.

## 1. O que a busca traz para o desenho

| ideia | a fonte (o status está na nota do vault) | o uso proposto |
|---|---|---|
| "e se todos fizessem isso?" é uma regra de decisão computável: escolher a regra cujas consequências seriam as melhores se todos a seguissem | Levine, Kleiman-Weiner, Schulz, Tenenbaum e Cushman (2020), *PNAS*, `10.1073/pnas.2014505117` | o teste de universalização da CO7 (2.2) |
| o equilíbrio kantiano: cada um escolhe como se todos mudassem na mesma proporção; o resultado é eficiente | Roemer (2010), *Scand. J. Econ.*, `10.1111/j.1467-9442.2009.01592.x` | a forma da conta do teste, em vez de simular cada pet |
| o grau estável de moral kantiana é igual à assortatividade dos encontros | Alger e Weibull (2013), *Econometrica*, `10.3982/ecta10637` | o peso kantiano que cresce com encontros repetidos com quem retribui (2.1) |
| a máquina kantiana testa a máxima por consistência | Powers (2006), *IEEE Intell. Syst.*, `10.1109/mis.2006.77` | o "fim, não meio" como proibição testável, não como pontuação |
| a aversão à desigualdade faz agentes que aprendem cooperarem e punirem quem trai | Hughes et al. (2018), arXiv 1803.08884, preprint | a culpa e a inveja como termos do afeto (2.3) |
| com recompensa e política não partilháveis, os eventos de sanção bastam para normas surgirem | Vinitsky et al., arXiv 2106.09012, preprint; Köster et al. (2022), *PNAS*, `10.1073/pnas.2106028118` | entre computadores, só os eventos viajam (5) |
| agentes LLM esgotam o recurso comum, e a universalização ajuda | Piatti et al. (2024), arXiv 2404.16698, preprint, e a reprodução, arXiv 2505.09289 | a regra de a conta ficar no cérebro e nunca na LLM |
| as pessoas querem que a IA priorize o pior situado | Weidinger et al. (2023), *PNAS*, `10.1073/pnas.2213709120` | apoio externo à D-MM-14 (o piso primeiro) |
| o placar entre jogadores tem de ser conferido por quem não joga | Baughman et al. (2007), *IEEE/ACM Trans. Netw.*, `10.1109/tnet.2006.886289` | o servidor recalcula o placar a partir dos eventos (5) |
| criaturas trocadas pela internet: escala grande, e relatos de abuso | Cliff e Grand (1999), *Artificial Life*, `10.1162/106454699568683`; o relato da "tortura de norns" é só de fã (NÃO VERIFICADA EM FONTE PRIMÁRIA) | o risco que a etapa em rede tem de tratar (5) |

## 2. As propostas para a CO6 e a CO7

### 2.1 A CO6: a reputação e a convivência na percepção

- **A reputação de *j* vista por *i*** já sai da CO3 como função do log. A CO6 a põe na percepção do cérebro de *i* como mais uma leitura do
  outro pet.
- **O peso kantiano cresce com a convivência** (Alger e Weibull): cada pet tem um peso `k` dos deveres que sobe com os encontros repetidos
  com um pet de reputação boa e decai sem eles. O estágio de Kohlberg (a roda da nota *Moral do pet*) dá o teto de `k` por idade, e o
  Mega pode chegar ao teto da lei kantiana (D-MM-1). Os dois ovos são o caso de assortatividade alta.
- **Fica de fora da CO6:** usar a reputação para escolher com quem cooperar. Essa escolha muda a decisão, e isso é da CO7.

### 2.2 A CO7: os deveres como escudo e o teste da universalização

- **O escudo, duro:** o "o outro pet é fim, nunca meio" vira uma lista de ações proibidas pelo motor, por estágio. Por exemplo, tirar a
  comida de um pet abaixo do piso de fome, que é a disputa "anti" da CO3. Uma ação proibida não entra entre as candidatas, e nenhuma
  felicidade a compra. É o *shielding* que a nota *Moral do pet* já cita (Alshiekh et al. 2018).
- **O teste, brando, a partir do estágio que o permite:** para cada ação candidata, o motor estima o efeito "se todos os pets da ilha
  fizessem isso" na felicidade lexicográfica da ilha (D-MM-14: o piso, depois a média). A forma é a do equilíbrio kantiano de Roemer, uma
  conta sobre o efeito proporcional, e não uma simulação de cada pet. As ações que reprovam no teste perdem peso no M-ARB, na proporção de
  `k`.
- **Por que as duas camadas:** o escudo garante o "nunca meio" (Kant), e o teste traz o "e se todos fizessem isso?" (Levine). O piso da
  D-MM-14 impede que o jogo premie sacrificar um pet pelos outros.

### 2.3 A culpa e a inveja, no cérebro e não no corpo

- **A aversão à desigualdade** (Hughes): um termo para "estou bem melhor que o outro" (a culpa) e outro para "estou bem pior" (a
  inveja), lidos da diferença de bem-estar visto entre os dois pets, com o peso de cada termo por personalidade.
- **Onde entra:** no M-AFETO do cérebro, e **não** como canal do corpo químico, por causa da D-MM-10 ("nenhuma correção mexe no corpo"). Se
  o Matheus quiser a culpa como química, isso reabre a D-MM-10 (a K-4).

## 3. O "bem maior" e a condição de vitória

- **A medida da ilha:** a felicidade lexicográfica de todos os pets (D-MM-14), calculada pelo motor ou pelo deus da mitologia, nunca por
  um pet.
- **O que a tela mostra:** sem número (D-MM-8). Por exemplo, a ilha floresce ou murcha, e o pet mais triste da ilha aparece em destaque. A
  forma é da frente de UX.
- **A "vitória":** a ilha se mantém com o piso acima de um limiar por um tempo. O limiar e o tempo são PROPOSTOS, SEM FONTE, e só se fixam
  na rodada de equilíbrio. Ela não é um fim de jogo, é um estado que se mantém, como no resto do Digilab.

## 4. O que fica de fora desta proposta

A hybris (D-MM-18), a aura, a luta (LP-3), a fala moral pela LLM (a fala nasce da rede, e a LLM é só voz) e a pergunta do dono (D-MM-17).

## 5. A etapa futura: os pets de computadores diferentes (só se a D-MM-12 for reaberta)

- **O que viaja:** só os eventos sociais (a partilha, a contenção, o encostar, a sanção) e o resumo do bem-estar visto, nunca o cérebro, o
  log inteiro ou o genoma. É o caso de Vinitsky et al.: as normas surgem com os eventos de sanção, sem partilhar política.
- **O placar:** o servidor recalcula a reputação e a felicidade da ilha a partir dos eventos, e não confia no número que cada cliente
  manda (Baughman et al. 2007).
- **O determinismo:** os eventos de fora entram no log de cada pet como eventos externos, como no modo livre gravado. O replay continua
  igual.
- **Os riscos, dos relatos:**
  - o abuso de criaturas alheias (o caso dos norns, só relato de fã);
  - a autopolícia que não bastou no Ultima Online (fonte cinza).

  O escudo da CO7 vale também para o pet visitante, e o dono do pet visitado pode encerrar a visita.
- **A infraestrutura:** o servidor local (`servidor/`) não é um servidor multijogador. A etapa em rede pede uma decisão de produto e de
  privacidade antes de qualquer código (a nota *Multijogador e rankings* do vault).

## 6. As etapas propostas

| etapa | o quê | quem |
|---|---|---|
| **K0** | esta proposta | esta sessão |
| **CO6** | a reputação e o peso kantiano na percepção (2.1): a espec, o gabarito, o Python atrás da chave e a paridade | a frente COOPERACAO, com o ok do Matheus |
| **CO7** | o escudo e o teste da universalização (2.2) e a culpa e a inveja no afeto (2.3): a espec, o gabarito, o Python atrás da chave e a paridade | a frente COOPERACAO, com o ok do Matheus |
| **CO-bancada** | o plano de análise da pergunta "a cooperação emerge e responde à reputação e ao peso kantiano?", antes de qualquer run | a frente COOPERACAO |
| **K-rede** | a etapa em rede (5) | depois de a D-MM-12 ser reaberta |

## 7. As decisões (PROPOSTAS, para o Matheus; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **K-1** | onde entra o plano | **como insumo da COOPERACAO** (a CO6 e a CO7), com o código coordenado pelo Gerente | uma frente paralela colide com os PRs abertos da cooperação nos mesmos arquivos |
| **K-2** | o escudo da CO7 | **duro, por estágio**: o "fim, nunca meio" como lista de ações proibidas pelo motor | só como peso, uma felicidade grande compraria a ação proibida, e o pet deixaria de ser kantiano |
| **K-3** | o teste da universalização | **brando, a partir de um estágio, na forma de Roemer**, julgado pela felicidade lexicográfica (D-MM-14) | simular cada pet custa caro e muda o replay por mais caminhos; sem o teste, a moral fica só nas proibições |
| **K-4** | a culpa e a inveja | **no M-AFETO, não no corpo** (D-MM-10) | no corpo, reabre a D-MM-10 e mexe na química de todas as vidas |
| **K-5** | a vitória | **um estado da ilha que se mantém**, com o piso acima de um limiar, mostrado sem número | um placar numérico contraria a D-MM-8 e convida a otimizar o número |
| **K-6** | a rede entre computadores | **continua esperando a D-MM-12**; quando reabrir, só os eventos viajam e o servidor recalcula | abrir agora pede um servidor multijogador e uma decisão de privacidade que ainda não existem |
