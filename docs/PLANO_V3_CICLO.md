# Plano do ciclo: a vida como rodada, com legado (2026-11-12)

**Status:** PROPOSTO, sem código. O Matheus pediu em 2026-11-12 que o ciclo no estilo roguelike "já esteja desenhado". A direção é dele
(CR-0); o como e todos os números são **PROPOSTOS, SEM FONTE**, e se acertam na rodada de equilíbrio do fim.

**Origem:** o Matheus, em 2026-11-12: "o pet vai chegar num estágio onde o jogador vai poder herdar os stats e fazer como se fosse num
roguelike, que ele vai zerar o ciclo. Na próxima rodagem o pet vai estar com os stats melhorados e ele vai poder crescer."

**Só no jogo web.** O Tamer não existe no Python. A seção 6 diz o que conferir antes de mexer no evento de origem.

**Fora deste plano:** a jogress entre dois pets, que fica para frente ([`futuro/jogress_dois_pets.md`](futuro/jogress_dois_pets.md)).

## 1. Em uma frase

**Cada vida é uma rodada.** Quando ela acaba, o pet deixa um **legado**: uma parte do que treinou vira o ponto de partida do próximo ovo,
e o teto do que o próximo pode treinar sobe um pouco. O cérebro começa do zero: o que passa é o corpo, não a criação.

## 2. O que existe hoje (conferido na `main`, 2026-11-12)

| peça | onde | o que pesa |
|---|---|---|
| a nova geração por cruzamento | `web/app/src/heranca.ts`; o evento de origem `"o"` em `web/app/motor/motor.ts` (`_origem`) | o filho herda a **espécie** (de um dos pais) e o **temperamento** (a média dos pais, com ruído `CHE.sigma` 0,1). **Não herda stats** |
| o ovo novo depois da Liga | `web/app/src/jornada.ts` (`novoOvoGuardandoAtivo`) | o campeão vai para os guardados e um ovo começa do zero |
| os tetos do treino | `web/app/motor/constantes.ts`: `CTR.tetoStat` 10, `CTR.tetoEstagio` 10, 12 e 14, `CTR.tetoVida` 36; no Mega, `CMG.tetoEstagio` 16 e `CMG.tetoVida` 40 | o legado tem de caber nesses tetos, ou dizer por quanto os move |
| o teto dos chips | `bonusChipsStat` (`web/app/motor/itens.ts`): até 25 % do treino típico do estágio | o modelo de "bônus dentro de um teto" já existe |
| o que é do Tamer | medalhas, itens, títulos, Bits, o portão ★ | já atravessa as vidas |
| o reset do ranking | `docs/PLANO_V3_MMO.md`, MMO-17 e MMO-18 (APROVADAS): o reset é do pet; dá Respeito e Bits, **"sem herança de stats no motor"** | **este plano revê a MMO-18** (CR-7) |
| a morte | definitiva; por saúde no chão ou lesão sem tratar | é um dos dois fins do ciclo |

## 3. O ciclo

```
  o ovo ──▶ a vida (cuidar, treinar, lutar, evoluir) ──▶ o fim do ciclo ──▶ o legado ──▶ o memorial ──▶ o ovo seguinte
                                                             │                                              ▲
                                                 morte, ou a escolha do dono                    parte mais forte, cérebro novo
```

### 3.1 Como um ciclo acaba

| fim | quando | o que vale |
|---|---|---|
| **encerrar o ciclo** (a escolha do dono) | do **Ultimate** em diante, com o pet vivo e sem lesão | o legado cheio do nível a que ele chegou |
| **a morte bem cuidada** | o pet morre com o cuidado em dia (a regra exata na espec) | o legado cheio |
| **a morte por descuido** | saúde no chão ou lesão sem tratar | **a metade** do legado |
| **antes do Rookie** | qualquer fim | nenhum legado |

- **Por que a morte por descuido passa menos:** para matar o pet nunca ser o caminho mais rápido. O cuidado continua valendo até o fim.
- **Por que só do Ultimate em diante dá para encerrar:** o ciclo tem de ser uma vida inteira, não um atalho.
- O pet que encerra o ciclo vivo **se aposenta** em Gerações, como o pai do cruzamento de hoje. O que morre ganha o memorial.

### 3.2 O que o legado leva

| passa | quanto (PROPOSTO) | por quê |
|---|---|---|
| **uma parte dos pontos treinados,** stat a stat | 20 % se chegou ao Champion, 30 % ao Ultimate, 40 % ao Mega, 50 % ao Mega com o título da Liga | o pet seguinte nasce com a cara do anterior: quem treinou força deixa força |
| **o teto da vida** | +2 por geração, até +10 | é o "ele vai poder crescer": cada rodada pode ir um pouco mais longe |
| **o temperamento** | o do pet, com o ruído de hoje (`CHE.sigma`) | a linhagem tem um jeito, sem ser cópia |
| **a marca da geração** | o número da geração no ovo, na plaquinha e no memorial | o jogador vê o caminho |

| não passa | por quê |
|---|---|
| **o cérebro** (os hábitos, a memória, o que aprendeu) | cada vida é uma criação nova. É o que mantém o jogo vivo de rodada em rodada |
| **o vínculo e o caráter** | saem da relação e do cérebro desta vida |
| **a forma** | o ovo recomeça do bebê, e a linha depende de novo do caráter |
| **os chips equipados** | são do Tamer; equipam-se de novo |
| **as lesões e as digidoenças** | o ovo nasce limpo |

- **Onde o legado entra:** como pontos de partida do treino, **dentro do teto de cada estágio**. Ele adianta o caminho; não faz um Rookie
  mais forte do que um Rookie pode ser. Só o teto da vida cresce, e devagar.
- **O legado tem teto próprio:** o que passa de uma geração soma ao que ela mesma recebeu, mas o total herdado nunca passa de uma fração
  do teto da vida (PROPOSTO: a metade). Sem isso, a décima geração nasceria pronta.

### 3.3 O que muda de uma rodada para a outra

O roguelike pede que a rodada seguinte não seja a mesma, só mais fácil.

| peça | proposta |
|---|---|
| **o brasão** | o jogador escolhe de novo. Manter o brasão passa o legado inteiro; trocar passa a metade, e abre outra árvore de formas |
| **o que o Tamer já abriu** | as medalhas, os lugares, o portão ★ e os feitos ficam. O começo da rodada é mais curto |
| **os rivais** | os mesmos da campanha; o desafio maior fica no portão ★ e na Fronteira, que já escalam |
| **as metas de geração** | feitos que só uma linhagem alcança: uma forma de cada linha, o título com três brasões, a quinta geração |
| **a rodada com condição** (opcional, depois) | o dono escolhe uma condição para a vida (por exemplo, sem chips) em troca de um legado maior |

### 3.4 A tela do fim do ciclo

1. **O resumo da vida:** a forma final, os marcos, as lutas, o que o cuidado decidiu.
2. **O legado:** stat a stat, o que passa e por quê ("chegou ao Mega: 40 %"; "morreu por descuido: a metade").
3. **O memorial:** o pet ganha o lugar dele na ilha (a proposta WD-8 do plano da interação).
4. **O ovo seguinte:** o brasão, com o aviso do que muda se trocar. O ovo nasce com a marca da geração.

Nada disso é escondido: o jogador sempre sabe o que vai passar **antes** de encerrar o ciclo.

## 4. O que o ciclo não é

- **Não é o prestígio do Tamer:** o Tamer não zera (MMO-17).
- **Não é cruzamento:** tem um pai só. O cruzamento de hoje continua existindo, ao lado.
- **Não passa a criação:** o cérebro recomeça. Um legado de hábitos faria a segunda vida ser a primeira de novo.
- **Não se compra:** nem Bits nem dinheiro aumentam o legado.

## 5. O ranking (a revisão da MMO-18)

A MMO-18 recusou a herança de stats por um motivo: ela "dá ao veterano uma vantagem que o teto não segura". Este desenho responde assim:

- **o legado entra dentro do teto do estágio,** então nas tabelas por estágio o veterano chega ao teto mais cedo, mas não passa dele;
- **o teto da vida que cresce por geração não vale nas lutas ranqueadas:** nelas, os stats do pet são cortados no teto de base (CR-8);
- **o servidor refaz tudo:** o legado está no evento de origem, no começo do registro, e o registro do pai é conferível;
- **o Respeito e os Bits do reset continuam** como a MMO-18 definiu. O legado soma a eles, não os troca.

## 6. Engenharia

- **Um evento de origem novo:** hoje o `"o"` pede dois pais e sorteia a espécie e o temperamento. O ciclo pede uma origem de **um pai só**,
  com o legado (os pontos por stat, o bônus do teto da vida, a geração). Proposta de nome: `"oc"`. O `"o"` de hoje não muda.
- **Uma versão de pet nova,** com a chave desligada e o gabarito byte a byte das vidas de hoje antes.
- **O legado é uma conta pura sobre o registro do pai:** o estágio a que chegou, os pontos treinados, o fim. O app a faz ao encerrar, e o
  motor confere os limites ao ler a origem (legado acima do teto falha alto).
- **O registro do Tamer** ganha o evento do fim do ciclo, para a geração e as metas de linhagem.
- **Antes de mexer na origem, conferir:** se o evento de origem tem gêmeo no Python (a herança da v1). Se tiver, a origem nova fica só no
  jogo, como a jornada (PAR-14), e isso entra como exceção de paridade.
- **A morte por descuido** precisa de uma regra que o motor leia no registro. A causa da morte já é gravada (`morte.causa`).

## 7. Etapas (um PR por etapa)

| etapa | o que entrega | depende de |
|---|---|---|
| **CI0** | a espec, com as decisões CR e os números propostos | este plano aprovado |
| **CI1** | a conta do legado (pura, com testes) e a tela do fim do ciclo, sem gravar nada | CI0 |
| **CI2** | a origem de um pai com legado no motor, a versão de pet nova e o encerrar o ciclo | CI1 |
| **CI3** | o teto da vida por geração e a marca da geração | CI2 |
| **CI4** | o memorial e as metas de geração | CI2; os feitos (WD-2) |
| **CI5** | o corte do teto nas lutas ranqueadas | o ranking (MMO3 em diante) |

## 8. Decisões para o Matheus

| # | decisão | estado | recomendação | custo de errar |
|---|---|---|---|---|
| CR-0 | a vida é uma rodada, com legado de stats para o ovo seguinte | **DECIDIDO** (Matheus, 2026-11-12) | — | — |
| CR-1 | o ciclo acaba pela morte ou pela escolha do dono, do Ultimate em diante | PROPOSTO | sim | só pela morte faz o jogador matar o pet para avançar |
| CR-2 | a morte por descuido passa a metade do legado | PROPOSTO | sim | sem isso, descuidar no fim não custa nada |
| CR-3 | passa uma parte dos pontos treinados, maior quanto mais longe o pet chegou | PROPOSTO | sim | legado igual para todos tira o motivo de ir até o Mega |
| CR-4 | o legado entra dentro do teto do estágio; só o teto da vida cresce, +2 por geração até +10 | PROPOSTO | sim | sem teto, as gerações quebram o equilíbrio da campanha |
| CR-5 | o cérebro, o vínculo e o caráter **não** passam | PROPOSTO | sim | passando, a segunda vida repete a primeira, e o DigiBrain deixa de importar |
| CR-6 | trocar de brasão passa a metade do legado | PROPOSTO | sim | legado inteiro em qualquer brasão tira o peso da escolha; nenhum prende o jogador a uma árvore |
| CR-7 | rever a MMO-18: o legado de stats passa a existir, somado ao Respeito e aos Bits do reset | PROPOSTO | sim, com a CR-8 | manter a MMO-18 como está impede o ciclo que o Matheus pediu |
| CR-8 | nas lutas ranqueadas, os stats são cortados no teto de base | PROPOSTO | sim | sem o corte, o ranking vira contagem de gerações |
| CR-9 | o cruzamento de hoje continua, ao lado do ciclo | PROPOSTO | sim | tirar o cruzamento apaga uma mecânica que já está no jogo |
| CR-10 | a rodada com condição (legado maior em troca de uma restrição) | PROPOSTO | depois | cedo demais, complica a primeira volta do ciclo |
