# Plano de UX da conta: entrar e primeiro acesso (2026-11-12)

**Status: PROPOSTO.** Sem código. A prancha está em `docs/pranchas/ux-conta/` e espera a aprovação do Matheus; o código é da etapa CN2
do `docs/PLANO_V3_CONTA.md`, depois da CN1 (o servidor). Os tamanhos e os textos de interface são **PROPOSTO, SEM FONTE**.
Autor: Gerente da UX_TELA_PET (Claude Code, Fable 5.2), branch `v3-ux-conta-pranchas`.

**O pedido do Matheus (2026-11-12):** "revise daí e planeje telas de login e telas de cadastro que estejam condizentes com a arte e o
estilo do projeto. A proposta [...] dessa nova infra [...] está rodando em outra seção. Daí dá uma lida [...] nos MDs dessa outra seção,
para poder planejar essa questão. Daí desenvolva as pranchas das novas telas referentes a isso."

## 1. O que foi lido

- `docs/PLANO_V3_CONTA.md` (a sessão da conta; CN-1 a CN-18 DECIDIDAS) e `docs/TAREFA_V3_CONTA.md`;
- `docs/UI_GUIDELINES.md` (os princípios, o texto, o movimento, a acessibilidade);
- os Ajustes de hoje (`web/app/src/telas/config/TelaConfig.tsx`, `estilo/lugar_l3.css`) e o cais (`telas/pet/lugaresIlha.ts`);
- as pranchas `docs/pranchas/ux-lugares-menus/` e `ux-mobile/`, de onde vêm os tokens e os moldes.

## 2. O que as decisões já fixam

| a decisão | o que ela tira ou põe na tela |
|---|---|
| **CN-1:** o jogo primeiro, a conta depois | não há tela de login na entrada do jogo. A conta é uma escolha, dentro do jogo |
| **CN-2:** Google e GitHub, sem senha | não há campo de e-mail, de senha, "esqueci a senha" nem confirmação de e-mail |
| o cadastro é o primeiro acesso (seção 2 do plano) | o "cadastro" é uma tela só: o apelido, a idade e o aceite |
| **CN-10** e **CN-6:** só convidados adultos | a pergunta da idade; os estados "fora da lista" e "menos de 18" |
| a privacidade (seção 9) | a tela Entrar diz o que vai para o servidor antes dos botões; o e-mail não aparece em lugar nenhum |
| **CN-5:** a conta apagada some em até 30 dias | o texto da tela Apagar |

## 3. As telas

Todas na pele dos menus (`--hx-*`, Vidro por padrão e Militar), sem cor nova, com a ilha viva em volta.

| # | a tela | o objetivo do jogador | o que tem |
|---|---|---|---|
| 1 | **Ajustes, a linha Conta** | achar a conta sem ser cobrado | uma linha no topo dos Ajustes: "Conta · sem conta" (tracejada, como toda linha nova) ou "Conta · Agumon#4821" |
| 2 | **Entrar** | saber o que acontece e entrar em um toque | "O mesmo pet em outro aparelho"; três linhas do que vai e do que não vai; "Entrar com Google"; "Entrar com GitHub"; "Agora não"; Termos e Privacidade; "só convidados com 18 anos ou mais" |
| 3 | **Os estados de Entrar** | não ficar perdido na ida e na volta | saiu para o Google; conferindo; não deu; fora da lista de convidados; menos de 18 |
| 4 | **Primeiro acesso** | criar a conta em uma tela | o apelido pronto, com "Trocar"; a idade em duas opções; o aceite com a versão; "Criar a conta"; "Cancelar" |
| 5 | **Trocar o apelido** | escolher sem digitar | o Digimon por uma lista fechada; o número por sorteio |
| 6 | **Conta (o perfil)** | ver e cuidar da conta | o apelido e o provedor; os aparelhos, com "Desconectar"; "Baixar meus dados"; os termos aceitos; "Sair"; "Apagar a conta" |
| 7 | **Apagar a conta** | apagar sabendo o que perde | o que some, em quanto tempo e o que fica; "Baixar meus dados antes"; "Entendi que não volta"; "Manter a conta" (principal); "Apagar para sempre" |

**Fora desta prancha (são da CN3 e da CN6):** "levar o pet para a conta" (tela 3 do plano), o ícone de sincronização e os avisos do HUD
(tela 5), as cópias do save com "restaurar" (parte da tela 4) e as páginas públicas (tela 6). O ranking e os selos são do MMO.

## 4. A hierarquia e o estilo

- **A conta é uma parte dos Ajustes,** não um lugar e não uma página à parte: a mesma caixa (460 px no desktop, a folha no celular), com
  o voltar, como Visual, Fala e Registro. A câmera não se mexe e a ilha não escurece.
- **Sempre visível:** o título, a frase da tela e os botões. **Por gesto:** os balões com a explicação (o foco ou o toque longo).
- **Um botão principal por caixa** (`--hx-btn-*`). Na tela Entrar os dois provedores têm o mesmo peso e nenhum é o principal. Na tela
  Apagar, o principal é "Manter a conta".
- **O perigo** usa `--hx-perigo` e borda tracejada, e nunca só a cor: há o texto "Sem volta" e o ícone.
- **O texto:** frases curtas, verbo na frente, sem exclamação; os erros dizem o que houve, que nada foi guardado e que o jogo continua
  (guia, seções 1 e 12). Nenhuma frase de culpa nem de urgência para criar a conta (princípio 5).
- **O movimento:** os passos da ida ao provedor são três pontos parados. Nada gira nem pisca (guia, seção 11).
- **A acessibilidade:** alvos de 44 px ou mais; o foco visível; os estados em `role="status"` ou `role="alert"`; a idade como grupo de
  rádio; o aceite como caixa de marcar com rótulo; texto de 13 px ou mais.
- **Os nomes do Digimon** no apelido, como em todo o jogo.

## 5. O celular

A mesma folha dos Ajustes, que sobe da base. A altura muda por tela (de 280 a 530 px a 390 × 844): os estados usam a folha baixa, e o
pet fica à vista. O primeiro acesso cabe sem rolar a 390 e a 360.

## 6. O custo

- **No determinismo:** nenhum. A conta não toca o motor, o log nem o save (isso é a CN3, atrás de chave).
- **No e2e:** as telas novas pedem testes próprios na CN2, com o servidor falso; os testes de hoje não mudam, porque sem conta nada muda.

## 7. Decisões para o Matheus

- **UX-CN-1. A prancha inteira:** aprovar para a CN2 usá-la. Recomendo aprovar. Custo de errar: baixo; é desenho, e a CN2 ainda depende
  da CN1.
- **UX-CN-2. A porta da conta:** **só a linha em Ajustes agora;** o cais passa a levar à mesma tela quando o MMO abrir o menu dele. A
  outra opção é abrir o cais já, só para a conta. Custo de errar: baixo. Abrir o cais sem o ranking mostra um lugar quase vazio.
- **UX-CN-3. A marca dos provedores:** **o ícone em uma cor só, a do texto,** para não trazer cor nova. A regra de marca do Google para
  o botão de entrada **não foi conferida** e pode pedir o botão oficial, com as cores dele; confere-se na CN2. Custo de errar: médio, se o
  Google recusar o aplicativo por causa do botão.
- **UX-CN-4. A lista do apelido:** **os Rookies do Catálogo, a mesma lista para todos.** A outra opção é só os Digimon que o jogador já
  viu. Custo de errar: baixo. A lista por jogador revela o progresso dele no apelido.
- **UX-CN-5. A idade:** **uma pergunta de duas respostas,** sem data de nascimento. Custo de errar: médio; é o mínimo de dado, e a
  revisão da LGPD (CN-10) pode pedir outra forma.
- **UX-CN-6. Trocar o apelido depois:** a tela Conta mostra "Trocar". Recomendo **permitir, com um limite** que o plano MMO define (o
  apelido aparece no ranking). Custo de errar: baixo.

## 8. O que não foi feito

- Nenhum revisor (`rev-a11y`) viu a prancha, e o contraste não foi medido; os tokens são os de hoje.
- A lista dos Ajustes na prancha está encurtada; a de verdade é a do `TelaConfig.tsx`.
- "Agumon#4821", as datas, os aparelhos e os oito nomes são exemplo de layout, nunca dado.
