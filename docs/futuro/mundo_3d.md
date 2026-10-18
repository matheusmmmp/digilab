# Mundo 3D: o mundo físico com câmera diagonal, sprites sobre corpos invisíveis e o contrato com o DigiBrain

Status: **RASCUNHO, PROPOSTO** (2026-10-18, worker A, pela especificação WORLD-POC-001 do Matheus). Só investigação: nada no código
mudou, e nenhum PR foi aberto. O Matheus confirma a localização antes de qualquer PR. Números, pesos e nomes novos são PROPOSTOS.
Nenhuma alegação de novidade.

**Os anexos:**
- `docs/futuro/mundo_3d/auditoria.md`: o anexo 1, o estado real do repositório (investigação A);
- `docs/futuro/mundo_3d/tecnologias.md`: o anexo 2, as engines e a matriz (investigação B);
- `docs/futuro/mundo_3d/poc_01.md`: o anexo 3, o WORLD-POC-01. Vira `docs/TAREFA_V2_WORLD_POC_01.md` só se for aprovado.

**O que já existe e não se repete aqui:**
- **a vista:** `docs/futuro/mundo_fisico.md`, com a M-1 (o mapa 2D contínuo, DECIDIDO), a M-2 (a vista inclinada como a do Animal
  Crossing, DECIDIDA), a seção 2.5 (a percepção sem acesso privilegiado) e a seção 2.6 ("a vista é só desenho");
- **o protótipo da vista:** `docs/futuro/mundo_fisico_vistas.html`, com as pranchas `docs/estilo_up/pranchas/MapaDesktop.html` e
  `Mapa390.html`;
- **dois pets:** `docs/futuro/dois_pets.md` (os órgãos com lado e a `PercepcaoSocial`) e `docs/futuro/convivencia_mundo_fisico.md`.

## 1. Resumo

- **Hoje não existe mundo 3D, nem física, nem tela do mapa.** Existe um mundo 2D de posições inteiras, sem paredes, no Python e no TS,
  com paridade. A bola "rola" uma distância sorteada (anexo 1).
- **O requisito que decide** não é gráfico: é o **determinismo com paridade Python/TS**. Uma física de engine em float (Rapier, Havok)
  só é determinística entre aparelhos no JS, não com o Python (anexo 2, seção 2).
- **A recomendação (PROPOSTA):**
  - **Three.js como renderizador**, num canvas dentro do Preact;
  - **a física no motor, em inteiros:** paredes, colisão do círculo do pet, empurrão da bola com velocidade e atrito inteiros. A vista 3D
    continua sendo só desenho, como a M-2 manda;
  - **o Rapier como experimento contido** (o POC-01b);
  - **não ao Godot.**
- **O aprendizado no mundo físico ainda não funciona** (J1 negativo, #285 e #296). O mundo 3D não é o gargalo da pesquisa. O P2 da
  especificação (aprender por consequência sem o 3D) vem antes e pode ser feito no mundo 2D de hoje.

## 2. As peças e quem é dono de quê

```
                 PESQUISA (Python)                          JOGO (navegador)
  dono / bancada ──► motor (engine + mundo + corpo) ◄──── log ────► motor TS (paridade bit a bit)
                        │  ▲                                          │
             Observação │  │ Intenção                                 │ estado (só leitura)
                        ▼  │                                          ▼
                     DigiBrain (lobos)                       vista 3D (Three.js): câmera, sprites,
                                                             sombras, oclusão, interpolação
```

- **O motor é a fonte da verdade.** O mundo, o corpo, a física inteira e os sorteios moram nele. O DigiBrain só lê a Observação e só
  devolve a Intenção.
- **A vista só lê.** Ela desenha o estado do motor, interpolando entre ticks, e transforma um gesto na tela num evento do log (o
  `deixar_comida(tipo, x, y)` de hoje). Ela nunca escreve no estado.
- **O log é a persistência** (seção 7). A câmera, a interpolação e os quadros de animação não entram nele.

## 3. Investigação C: o modelo físico mínimo da criatura

Tudo em inteiros, nas **subunidades** do mapa de hoje (`ConfigMundo.sub` = 16 por célula). Os nomes e os números são PROPOSTOS.

| campo | representação | de onde vem hoje |
|---|---|---|
| posição | `(x, y)` inteiros no chão; altura `z` = 0 para o pet | `(x, y)` do `Mundo` |
| orientação | um setor de 16 (`direcao_em_16`) ou de 8 (`direcao_em_8`) | as funções já existem em `mundo.py`; hoje só o olfato usa a direção do último passo (a propriocepção, #308) |
| corpo de colisão | um **círculo de raio `r_pet`** no chão (PROPOSTO: 6 subunidades). Na vista, uma cápsula invisível de altura só visual | não existe: hoje o pet é um ponto |
| velocidade | `(vx, vy)` inteiros por tick, com `\|v\|` ≤ `velocidade` (4) | hoje é o `passo_ate` em linha reta, sem velocidade guardada |
| movimento | **cinemático**: o controlador escolhe a velocidade do tick por um caminho na grade de células (A* inteiro, para contornar as paredes); a colisão resolve o círculo contra os retângulos e **desliza** pela parede | não existe o caminho: hoje não há obstáculo |
| alcance de interação | um raio inteiro (`raio_pegar_celulas` × `sub`) a partir da borda do círculo | `raio_pegar_celulas` = 1 |
| estado de animação | **não fica no motor.** A vista o deriva do estado (a ação, a velocidade, o contato, dormindo) e do relógio da tela | — |
| sensores espaciais | a visão num **cone** com raio e ângulo, com oclusão por parede (um raio na grade, DDA ou Bresenham em inteiros); o **contato** (o pet bateu ou encostou, e em quê); o cheiro e o ouvido de hoje | a visão de hoje é um disco sem oclusão; não há contato |

**Os objetos**, no mesmo modelo:

| objeto | colisão | o que faz |
|---|---|---|
| parede | retângulo estático | bloqueia o pet, a bola e a visão |
| obstáculo | retângulo ou círculo estático | bloqueia o pet e a bola; a visão passa por cima de um obstáculo baixo (uma flag `alto`) |
| bola | círculo de raio `r_bola` | tem velocidade inteira; perde `atrito` por tick; **reflete** na parede trocando o sinal da componente normal, com uma restituição em fração inteira; o **empurrão** do pet lhe passa uma velocidade na direção do contato |
| comida | ponto, sem colisão | some ao ser consumida; apodrece como hoje |

**Por que cinemático, e não dinâmico:** o pet não precisa de massa nem de força para andar. O cérebro escolhe para onde, e o motor leva
(`mundo_fisico.md`, 2.1). Só a bola precisa de dinâmica, e uma dinâmica de um corpo com atrito e reflexão cabe em inteiros. Com isso, a
paridade bit a bit se mantém. Um motor de corpos rígidos (pilhas, rotação, atrito entre corpos) só vale a pena se houver uma pergunta
de pesquisa que dependa dele (a W-1, seção 8).

**O sprite sobre o corpo invisível (a vista, Three.js):**
- **billboard:** o `THREE.Sprite` sempre olha para a câmera e não faz sombra (anexo 2, 2.1). Com a câmera fixa na diagonal, o pet
  aparece sempre de frente. A sombra é um disco no chão, sob o centro do círculo, como no protótipo `mundo_fisico_vistas.html`;
- **sprites direcionais:** a direção do movimento pede quadros de lado (esquerda e direita espelhadas) ou de costas. **Não verificado:**
  quais direções o atlas do Digimon UP tem;
- **a ordem de profundidade:** com a câmera fixa, a ordem de desenho é o `y` do pé no chão (o mais perto da câmera por cima, como manda a
  M-2). O sprite transparente com corte de alfa escreve a profundidade e evita o problema da ordenação por transparência (conhecimento
  do modelo, não verificado; é a métrica M2 do POC);
- **a oclusão:** a parede que fica entre a câmera e o pet o esconde. A saída comum é desenhar o pet escondido como uma silhueta (uma
  segunda passada sem teste de profundidade) ou deixar a parede da frente semitransparente. **É só desenho:** a oclusão da visão do pet
  é a do motor, não a da câmera;
- **o pixel art:** filtro nearest, e o tamanho na tela em múltiplo inteiro do pixel do sprite, como o `PalcoPet` faz. Com a câmera
  ortográfica, o tamanho do sprite não varia com a distância; com perspectiva, varia, e o múltiplo inteiro se perde. **Recomendação
  PROPOSTA:** a câmera ortográfica inclinada.
