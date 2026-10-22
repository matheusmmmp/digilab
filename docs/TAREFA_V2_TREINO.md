# TAREFA V2 — TREINO (2026-10-22)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-treino`, a partir da `main` (d873327). Status: EM ANDAMENTO.

Categoria: implementacao. Origem: Matheus, 2026-10-22 (o "sim" à proposta do mapeamento enviado ao Gerente no mesmo dia). A referência é a
terceira tela de `D:\Trab\digilab\_ref\referencia_mobile_2026-10-19.png` (local, não versionada; só a composição): a sala de treino, o pet
golpeando o saco, a barra "toque no momento certo" e o cartão do stat.

## 1. Pergunta

A aba Crescer › Treinar pode ganhar composição própria, só com o que o motor registra, sem mudar o motor, o save nem o replay? Não vem de
uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- A moldura nova do desktop (#374) e a Evolução (#392), mergeadas: o `PetGrande` e a plataforma de luz vêm da Evolução.
- O mapeamento de 2026-10-22 e o "sim" do Matheus:
  - a composição proposta;
  - sem o minigame "toque no momento certo", que o motor não tem;
  - sem nível nem XP;
  - sem o "03" e sem japonês.

## 3. Mudança mínima

**A aba (`src/telas/crescer/TelaTreinar.tsx`):**
- **A sala:** própria em CSS (parede clara com janela, chão), com o pet grande e nítido na plataforma de luz (atlas ou grade de reserva). O
  fundo do UP só entra se o atlas local carregar. Ela traz o chip do estado ("pronto para treinar", "descansando: próximo em N min", "pediu
  pausa", "o In-Training ainda não treina") e o balão "pausa?".
- **O stat em foco:** o principal do último exercício (ou do primeiro, sem treino), com "+x de 10" e a barra. Embaixo, "no estágio x de N ·
  na vida y de 36".
- **Fadiga e sobrecarga:** as barras de hoje, com as marcas 40/60 e 30/60.
- **Os 6 exercícios:** como hoje (o selo "aptidão", o Forçar listrado acima de 60, a folha de confirmação). Os ícones do UP só locais; a
  reserva usa ícones do lucide.
- **Treinado na vida:** os 6 stats com barras de 0 a 10 e o total de 36.
- **O último treino:** o evento "tr" do registro e quando sai o próximo, agora também no celular.
- **Desktop, na moldura, com as abas de Crescer no topo:** à esquerda a sala, o stat em foco e "Treinado na vida"; à direita os medidores, os
  exercícios, o último treino e o Forçar.

**O teste.** Dois saves novos (`e2e/save_treino_pausa.json` e `e2e/save_treino_forcar.json`, gerados por `e2e/gerar_save_treino.mjs`):
um pet v11 no Rookie que já treinou e pede pausa (fadiga entre 40 e 60), e outro com fadiga acima de 60 (o Forçar).

**O que não muda:** o motor, o save, o replay e as rotas; as outras telas.

## 4. Gate

- `npm run tipos`, `npm test` e `npm run e2e` passam. O e2e soma:
  - a tela nova com os dois saves (a pausa, o Forçar e a folha);
  - a reserva sem o atlas;
  - nada de nível, XP ou japonês.
- `npm run capturas`:
  - `crescer-treinar` muda (é o pedido), e entram as capturas novas com os dois saves;
  - as outras telas ficam iguais em 390, 360 e 1280.
- Capturas individuais em 390×844, 360 e 1280.

## 5. Entrega

- PR com as capturas e o relato no corpo. Depois, parar. Sem merge.
- O relato também na seção 9 deste documento.

## 6. Fora desta tarefa

- O minigame de precisão: seria mecânica nova, com versão de pet.
- O treino mexer no corpo químico do v11: seria pesquisa e motor.
- O ganho de cada sessão no registro: hoje só sai na hora.

## 7. Critérios de aceitação

- A aba Treinar tem a composição da seção 3, no celular e no desktop, com o pet nítido mesmo sem o atlas.
- Nada na tela que o motor não tenha; nenhum caractere japonês.
- O gate da seção 4 passa.

## 8. Precisa do Matheus

O ok visual nas capturas.
