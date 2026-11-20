# TAREFA V2 — TREINO (2026-10-22)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-treino`, a partir da `main` (d873327), com a `main` mesclada em 61336e7. Status: ENTREGUE (PR, espera o ok visual e o merge).

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

## 9. Entregue (2026-10-22)

**O que mudou.**
- **`src/telas/crescer/TelaTreinar.tsx`:**
  - **A sala:** clara, em CSS (parede, janela, chão). O fundo do UP só com o atlas local. O pet fica grande na plataforma de luz (o
    `PetGrande` da Evolução: atlas ou grade de reserva), com o chip do estado e o balão "pausa?".
  - **O stat em foco:** o principal do último exercício, "Mira +1,1 de 10", com a barra e "no estágio x de 10 · na vida y de 36". No
    Mega, os tetos são os de `CMG`.
  - **Cansaço:** fadiga e sobrecarga, os medidores de antes.
  - **Os exercícios:** a grade de antes. Os ícones do UP só com o atlas; sem ele, os do lucide (Dumbbell, Footprints, Crosshair, Wind,
    Flower2, Shield).
  - **O resto:** "Treinado na vida" stat a stat (de 0 a 10) e o total; o último treino (do evento "tr"), agora também no celular.
  - **A ordem no celular:** sala, stat em foco, cansaço, exercícios, treinado na vida, último treino e "Como o treino funciona".
  - **Desktop, na moldura:** à esquerda, a sala, o stat em foco e o treinado na vida; à direita, o cansaço, os exercícios, o último treino e
    o Forçar.
  - O cartão "Próximo treino em N min" do celular saiu: o chip da sala diz "descansando: próximo em N min".
- **`src/estilo/treino.css` (novo)**, e o `crescer.css` sem as regras da sala antiga.
- **`e2e/gerar_save_treino.mjs`, `e2e/save_treino_pausa.json` e `e2e/save_treino_forcar.json` (novos):** um Palmon v11 no Rookie que treinou
  3 vezes (fadiga 56,5: pede pausa) ou 4 (fadiga 74,8: só Forçar). Conferidos: refeitos do registro e com mais 10 min de jogo, continuam
  acordados e na faixa.

**Gate.**

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 46 arquivos, 565 testes, todos passam (depois de mesclar a `main`) |
| `npm run e2e` | 84 de 84: os 80 de antes e os 4 novos (a tela em 390 e em 1280 com a pausa; o Forçar com a folha e o registro; a reserva sem o atlas) |
| `npm run capturas`, 390 e 1280 px (referência: o build da `main` d873327; a `main` mesclada só muda o motor, nada em `src/`) | 17 telas iguais, pixel a pixel; muda `crescer-treinar` (o pedido); `treino-pausa` e `treino-forcar` são novas |
| `npm run capturas`, 360 px (mesma referência) | 17 iguais; muda `crescer-treinar`; `diario-registro` alterna entre dois estados (22 pixels) também no build da `main` (nota abaixo) |
| determinismo do branch | 60 capturas gravadas e conferidas duas vezes, sem nova tentativa: todas iguais |

Notas do gate:
- Três capturas da referência saíram anômalas na primeira gravação: `crescer-aprend` e `evolucao-momento` em 390 e `diario-registro` em 360.
  Rodado de novo, o próprio build da `main` diferia delas com os mesmos pixels que o branch (12, 304 e 22). As três foram regravadas a
  partir do build da `main`.
- `diario-registro` em 360 continua alternando entre dois estados (22 pixels) nos dois builds, a `main` e o branch. É uma instabilidade
  que já existia (vista também na Exploração) e não vem desta tarefa.

**As capturas** (em `docs/estilo_up/pranchas/capturas/`, sem o atlas e sem a decoração do UP: a sala em CSS, o pet da grade de reserva e os
ícones do lucide):
- `Treino_pausa_390.png`, `Treino_pausa_360.png` e `Treino_pausa_1280.png`: o pet que pede pausa;
- `Treino_pausa_390_inteira.png`: a página inteira;
- `Treino_forcar_390.png`, `Treino_forcar_390_folha.png` e `Treino_forcar_1280.png`: só Forçar, e a folha de confirmação.

A comparação com a terceira tela da referência fica fora do repositório, porque a referência não é versionada.

**Diferenças para a referência.**
- Não há saco de pancada nem pet golpeando: o motor não tem animação por exercício.
- Não há a barra "toque no momento certo", nem "Lv. 3 120/300", nem o "03".
- Os medidores, os exercícios e o treinado na vida vêm do motor e não estão na referência.
