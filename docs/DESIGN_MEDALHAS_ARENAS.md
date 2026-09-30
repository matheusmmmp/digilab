# Design — medalhas, arenas, itens e a Fronteira de Batalha

Status: **aprovado** (Matheus, 2026-09-29), implementação **depois do diagnóstico dos arquétipos**. Nada foi implementado. Todo número é PROPOSTO, sem fonte.

**Decisões do Matheus (2026-09-29):**
1. Trava na evolução: **1, 3 e 5 medalhas** para Champion, Ultimate e Mega.
2. **6 arenas.**
3. O final é a **Fronteira de Batalha com os melhores Digimons**.
4. Começar **depois do diagnóstico** dos arquétipos.
5. Pets v6 para a trava: segue a recomendação da seção 5 (não houve objeção).

**O que ele junta.** Transforma em desenho concreto o passo M2 e as fases seguintes do `PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md` (seções 13, 14, 16, 17 e 24).

**Inspiração, não evidência.** A ideia vem do Digimon Championship (medalhas de chefes liberando fases e evoluções) e dos líderes de ginásio do Pokémon. Pela revisão bibliográfica de 2026-09-29, essas mecânicas não estão verificadas em fonte primária: servem de inspiração de design, não de precedente citado.

## 1. A ideia em uma frase

O jogador (Tamer) coleciona **medalhas** vencendo os **líderes** de cada arena. As medalhas são dele, não do pet, e sobrevivem à morte do pet. O número de medalhas é o **potencial do Tamer**: libera as próximas fases, as evoluções mais altas e os itens. No fim, a **Fronteira de Batalha** reúne os líderes na versão mais forte, e vencer todos faz do jogador o campeão.

## 2. O que já existe e como encaixa

- **A campanha v5** tem quatro lugares: Campina (Rookie), Torre de pedra (Champion), Cidadela (Ultimate) e Montanha Espiral (Mega). Os NPCs estão calibrados na escala da campanha.
- **A evolução** para Ultimate pede tempo, 10 lutas com 80% de vitória e o caráter. Para Mega pede tempo, lutas e vínculo ≥ 0,4.
- **O que não existe:** Tamer, medalhas, itens e Fronteira. Hoje tudo é do pet, e quando ele morre sobra só a herança.

## 3. Medalhas e arenas

Uma **arena por lugar** da campanha, cada uma com um **líder** que testa uma capacidade de criação diferente, não só números maiores (seção 16 da pesquisa). Os NPCs de hoje viram os desafiantes de cada lugar, e o líder é a luta que dá a medalha.

| # | arena (lugar) | nível | líder (sugestão) | o que ele testa | regra da arena |
|---|---|---|---|---|---|
| 1 | Campina | Rookie | Gazimon | o básico: cuidado e treino | nenhuma |
| 2 | Torre de pedra | Champion | Guardromon | paciência: pune regras impulsivas | o líder devolve golpe forte |
| 3 | Floresta (nova) | Champion | Kyubimon ou similar | leitura: o líder muda de padrão no meio da luta | vence quem tem regras condicionais |
| 4 | Cidadela | Ultimate | Myotismon | resistência: três lutas seguidas | sem cura entre as lutas |
| 5 | Lago (novo) | Ultimate | a definir | vínculo: o pet decide sozinho | travar e vetar regras não valem |
| 6 | Montanha Espiral | Mega | Piedmon | tudo junto | chefe final da campanha |

- **Os nomes dos líderes são sugestão.** Só entram Digimon que já estão no atlas; os lugares novos precisam de fundo no atlas.
- **Cada líder se calibra como a campanha de hoje:** sem treino vence ≤ 0,30, com o treino típico do estágio ≥ 0,80. Isso depende do **equilíbrio entre arquétipos** (diagnóstico em curso): com as formas como estão, um líder pode ficar impossível para um arquétipo inteiro.
- **Revanche liberada, sem punição por perder.** Perder de um líder não custa medalha nem dinheiro.

## 4. As medalhas liberam a evolução (o potencial do Tamer)

A regra fica **"o pet pode evoluir quando cumpre os requisitos dele E o Tamer tem medalhas suficientes"**:

| evolução | requisito do pet (hoje) | medalhas do Tamer (PROPOSTO) |
|---|---|---|
| In-Training → Rookie | cuidado do bebê | nenhuma |
| Rookie → Champion | tempo, caráter | **1** (Campina) |
| Champion → Ultimate | tempo, 10 lutas, 80% de vitória | **3** |
| Ultimate → Mega | tempo, lutas, vínculo ≥ 0,4 | **5** |

- **O pet pronto não perde nada.** Se ele já cumpre os requisitos e falta medalha, ele fica "pronto para evoluir" e a tela diz qual medalha falta. Quando o Tamer ganha a medalha, a evolução acontece na hora.
- **A medalha é do Tamer, não do pet.** Um pet novo, de um Tamer com 5 medalhas, evolui só pelos requisitos dele. As conquistas passadas encurtam o caminho das próximas gerações. É o que dá ritmo ao jogo: o primeiro pet aprende e abre caminho, e os seguintes vão mais longe.
- **As medalhas liberam mais coisas (seção 14 da pesquisa):**
  - mais regras de luta editáveis (hoje a capacidade é fixa por estágio);
  - os lugares seguintes do mapa;
  - espaços de item (seção 6);
  - a entrada na Fronteira.

**A decisão aberta mais importante:** a trava na evolução pode frustrar. O pet está pronto e não evolui porque o jogador ainda não venceu um líder. A alternativa mais branda é a medalha travar **só o Mega**, e as demais só liberarem lugares e itens. Recomendo a versão da tabela (1, 3, 5), porque é o que você pediu e dá ritmo, mas **com a mensagem clara do que falta**, e com o pet não perdendo nada enquanto espera.

## 5. Como isso entra no motor sem quebrar o replay

Este é o ponto técnico que decide a implementação.

- **O Tamer ganha um registro próprio**, como o pet, com os eventos `medalha` (qual, quando, com que pet) e, depois, `item`. Fica numa chave nova do save; o registro do pet não muda de formato.
- **O motor do pet não pode ler o Tamer por fora**, porque o replay do pet tem de dar o mesmo resultado sozinho. Então, quando o Tamer ganha a medalha que libera uma evolução, **entra um evento `u` (liberação) no registro do pet**: "o Tamer tem N medalhas a partir deste tick". O replay do pet lê esse evento, como já lê a luta e a origem.
- **Pets v5 existentes não mudam.** A trava vale para uma versão nova de pet (v6) ou só para pets criados depois de o Tamer existir. Recomendo **v6**, para ficar explícito no save.
- **A pesquisa em Python não muda.** Medalhas e Tamer são só do jogo, como os gambits híbridos. O desvio vai para o `REGISTRO_DESVIOS`.

## 6. Itens e cartas

Três tipos, cada um com teto próprio, para o equipamento **complementar** a criatura e não substituí-la:

| tipo | o que faz | teto (PROPOSTO) | de onde vem |
|---|---|---|---|
| **chip de stat** | + pontos num stat | até metade da diferença entre dois estágios; conta dentro do teto de treino da vida | medalhas e líderes |
| **chip de regra** | dá ao pet uma condição ou regra de luta nova (ex.: "não prepare o pesado se o rival defende") | 1 por pet; não pode ser a regra que define outro arquétipo | arenas específicas |
| **carta** | efeito de uma luta só (ex.: +20 guts no início, cura no meio) | 1 por luta; proibida na Fronteira, salvo regra da instalação | loja e líderes |

- **Sobre o desequilíbrio:** chips de stat ajudam pouco se a diferença entre as formas vier do comportamento, e o furioso equipado continua vencendo o titã equipado. O diagnóstico em curso mede quanto os stats pesam. **O chip de regra é o que mais pode compensar uma forma fraca**, porque mexe no que decide o confronto.
- **Sem economia no começo:** os itens vêm de medalhas e líderes. Dinheiro e loja ficam para depois; eles pedem fontes e escoadouros (seção 11 da pesquisa).

## 7. A Fronteira de Batalha (o final)

Liberada com as 6 medalhas. O objetivo: **vencer todos os líderes na versão mais forte e se tornar o campeão**.

- **A Liga dos Líderes, com os melhores Digimons** (decisão do Matheus): os 6 líderes em sequência, na versão de revanche, todos no estágio Mega e com os times mais fortes do jogo, sem cura entre as lutas. Vencer todos = **campeão**, com uma medalha de ouro e a mensagem de conclusão (a jornada de hoje termina no Piedmon; passaria a terminar aqui).
- **Depois do título**, instalações com regras próprias (seção 24 da pesquisa), para rejogar:
  - **Torre:** sequência de lutas, com recorde;
  - **Fábrica:** Digimon alugados, que testa o conhecimento do Tamer;
  - **Palácio:** o pet decide sozinho;
  - **Salão:** um pet por nível, que dá sentido a criar Rookies e Champions.
- **Contra o grind:** a recompensa da Fronteira é prestígio (títulos, recordes, a versão dourada da medalha), não força. Nada da Fronteira deixa o pet mais forte fora dela.

## 8. O ritmo esperado (a curva)

- **1º pet:** Campina e talvez a Torre (1–2 medalhas); aprende o jogo. Pode morrer ou envelhecer sem passar do Champion, e isso é esperado.
- **2º e 3º pets:** chegam a Ultimate mais rápido (as medalhas já estão com o Tamer), abrem a Cidadela e o Lago.
- **Pets seguintes:** Mega e Montanha Espiral; depois a Fronteira.
- **Nada fixo:** a curva sai da calibração dos líderes e do tempo de cada estágio (rápido ou clássico).

## 9. Ordem de implementação (um PR por parte)

1. **Tamer e medalhas:** o registro do Tamer, as medalhas dos lugares de hoje, a trava da evolução (pets v6, evento `u`), a tela de medalhas. Não depende do equilíbrio.
2. **Líderes das arenas:** as regras de arena, os dois lugares novos, a calibração. **Depende do equilíbrio entre arquétipos.**
3. **Itens:** chips e cartas com os tetos. Os números **dependem do diagnóstico**.
4. **Fronteira:** a Liga dos Líderes e o fim do jogo; as instalações depois.

## 10. O que você precisa decidir

1. **A trava na evolução:** 1/3/5 medalhas para Champion/Ultimate/Mega (a sua ideia), ou a medalha travando só o Mega.
2. **Número de arenas:** 6 (os 4 lugares de hoje mais 2 novos), ou só os 4 que existem.
3. **Pets v6** para a trava, deixando os v5 como estão.
4. **O fim do jogo passa a ser a Fronteira**, e não mais o Piedmon.
5. **A ordem:** Tamer e medalhas primeiro (não dependem do equilíbrio), com os líderes e os itens esperando o diagnóstico.
