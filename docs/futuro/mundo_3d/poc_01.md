# Mundo 3D, anexo 3: a especificação do WORLD-POC-01

Status: **INVESTIGAÇÃO FEITA; W-1 a W-7 DECIDIDAS em 2026-10-18** (worker A). Anexo de `docs/futuro/mundo_3d.md`. **Não começa agora:** vem depois do Gate C (W-5), quando
virar `docs/TAREFA_V2_WORLD_POC_01.md`, pelo modelo `docs/modelos/TAREFA_V2_MODELO.md`. Os números e os nomes são PROPOSTOS.

## 1. A pergunta

O menor protótipo que valida a arquitetura do documento principal:
- a vista 3D (Three.js) só desenha;
- a física fica no motor, em inteiros;
- o DigiBrain recebe a Observação e devolve a Intenção sem conhecer a engine.

O POC **não é pesquisa** (não há run nem gate de hipótese) e **não entra no jogo** (não há versão de pet nova). Ele só reduz a incerteza
técnica, para o Gate A.

## 2. O escopo mínimo (os elementos da especificação)

| elemento | no POC-01a |
|---|---|
| uma sala 3D | um piso de 16 × 12 células de 16 subunidades, com quatro paredes |
| a câmera diagonal | ortográfica, inclinada como a M-2 (o ângulo é o do protótipo `docs/futuro/mundo_fisico_vistas.html`) |
| o pet com sprite real | um quadro do atlas do Digimon UP como `THREE.Sprite`, com filtro nearest e escala inteira, e a sombra como um disco. **A arte é de uso pessoal e fica fora do repositório (anexo 1, seção 6):** o POC roda só local; sem o atlas, entra um sprite de reserva desenhado à mão |
| piso e paredes | caixas de cor lisa; a parede da frente fica semitransparente quando cobre o pet |
| obstáculos estáticos | dois blocos retangulares, um alto (tapa a visão) e um baixo (não tapa) |
| uma bola com física | o círculo com velocidade inteira, atrito e reflexão na parede (o modelo do documento principal, seção 3) |
| um objeto de alimentação | uma comida parada, consumível |
| o movimento do pet | o controlador do motor: A* na grade, a colisão com deslize e o empurrão na bola |
| a observação de objetos | a Observação do contrato (seção 4.2 do principal): o cone com oclusão, os bigodes e o contato |
| o registro de ações e resultados | o log da sessão e, por decisão, um registro com a Observação, a Intenção, a ação executada e o resultado físico, exportável em JSON |

**Fica de fora:** o Python, a paridade, o corpo químico (só uma fome e um tédio de brinquedo, sem os receptores), o cérebro A
aprendendo, dois pets, o jogo, o save e as telas do app.

## 3. Os componentes

| componente | arquivo (PROPOSTO) | o que faz | conhece a engine? |
|---|---|---|---|
| o mundo do POC | `web/app/poc/mundo3d/mundo.ts` | o estado inteiro: a sala, os objetos e o pet; um `passo()` por tick | não |
| a física inteira | `web/app/poc/mundo3d/fisica.ts` | o círculo contra o retângulo, o deslize, a bola (atrito, reflexão, empurrão) e os sub-passos | não |
| o controlador | `web/app/poc/mundo3d/controlador.ts` | o A* e a execução da Intenção, até chegar, bloquear ou dar a hora | não |
| os sensores | `web/app/poc/mundo3d/sensores.ts` | a Observação: o cone com o raio na grade, os bigodes e o contato | não |
| o cérebro de teste | `web/app/poc/mundo3d/cerebro.ts` | um decisor de regras que escolhe a Intenção pela Observação (a fome leva à comida, o tédio à bola). Não é o cérebro A: só prova o contrato | **não, e um teste confere** |
| a vista | `web/app/poc/mundo3d/vista.ts` | o Three.js: a câmera, as caixas, o sprite, a sombra, a oclusão e a interpolação entre ticks | sim, e só ela |
| a página | `web/app/poc/mundo3d.html` | uma entrada própria do Vite, fora do app | — |

**A dependência nova:** `three`, só na página do POC. O app do jogo e o `motor/` não a importam, e um teste confere.

O **POC-01b**, opcional, troca o `fisica.ts` pelo `@dimforge/rapier3d-deterministic-compat` (anexo 2) com a mesma sala. Ele mede se a
física de verdade traz algo que a inteira não traz, e o custo em determinismo e tamanho. Só roda se o Matheus quiser medir antes da
decisão W-1.

## 4. Os testes

| teste | onde | o que confere |
|---|---|---|
| a geometria inteira | Vitest | o círculo contra o retângulo, o deslize sem atravessar e a bola rápida que não atravessa a parede com os sub-passos |
| a bola | Vitest | o empurrão dá velocidade na direção do contato; o atrito para a bola; a reflexão troca a componente normal |
| a navegação | Vitest | o pet chega ao alvo nos cenários com os dois obstáculos (a métrica M4) |
| os sensores | Vitest | o obstáculo alto tapa e o baixo não; nada fora do cone aparece; a Observação não traz nenhuma posição absoluta |
| o determinismo | Vitest | a mesma semente e o mesmo log dão o mesmo hash do estado, duas vezes, e no Node e no Chrome (o e2e) |
| a fronteira | Vitest (o fonte) | nenhum arquivo de `poc/mundo3d/` além do `vista.ts` importa `three`; nenhum arquivo de `motor/` nem de `src/` importa nada do POC |
| a arquitetura de hoje | `npm test`, `npm run tipos`, `npm run e2e`, `python -m pytest tests/ -q` | tudo passa igual: o POC não muda nada fora da pasta dele |
| a página | Playwright | a página abre, o WebGL desenha (o screenshot não é vazio), e o pet anda até a comida |

## 5. As métricas (PROPOSTAS)

| # | métrica | como medir | limite para aprovar |
|---|---|---|---|
| M1 | renderiza | o e2e abre a página e o screenshot tem a sala | abre no Chrome do desktop e no de um celular real |
| M2 | o sprite fica correto | os pixels do sprite na tela batem com os do quadro do atlas na escala inteira, sem borrar, nos quatro cantos da sala | todos os pixels conferidos iguais |
| M3 | o desempenho | os quadros por segundo e o tempo de quadro, no desktop e num celular médio real | PROPOSTO: 30 quadros por segundo no celular. A emulação do Playwright não vale como celular |
| M4 | a navegação | os cenários do teste | o pet chega em todos |
| M5 | o determinismo e o replay | o hash do estado em duas execuções, e no Node e no Chrome; o tempo do replay de 1 dia de sala | hashes iguais; o tempo é só descritivo |
| M6 | o tamanho | o bundle da página, gzip | só descritivo (SEM FONTE para um limite) |

## 6. Os critérios de aprovação (os da especificação, seção 8)

| critério | a métrica |
|---|---|
| o navegador renderiza o ambiente adequadamente | M1 e M3 |
| o sprite permanece visualmente correto | M2, e a oclusão vista no screenshot |
| o corpo físico colide com objetos | a geometria inteira e os testes da bola |
| o pet consegue navegar até um alvo | M4 |
| a física produz resultados observáveis | os testes da bola e o registro (a bola empurrada se move, e o registro mostra o quanto) |
| o DigiBrain recebe observações sem depender da engine | o teste da fronteira e o cérebro de teste |
| a arquitetura atual continua funcionando | as quatro suítes passam iguais |

## 7. A estimativa, com as hipóteses

**As hipóteses:**
- um worker por vez, numa worktree;
- o atlas disponível na máquina;
- a prancha do mapa (`MapaDesktop.html`) serve de referência visual, sem prancha nova;
- sem Python e sem paridade;
- um celular real disponível para a M3.

As durações são em dias de trabalho de uma sessão, PROPOSTAS, sem histórico para calibrar (SEM FONTE).

| parte | dias | o risco que pode estourar |
|---|---|---|
| a vista: a sala, a câmera, o sprite, a sombra e a oclusão | 1,5 a 2,5 | o pixel art nítido na câmera inclinada (M2) e a ordem dos sprites transparentes |
| a física inteira e o controlador (A*, deslize, bola) | 2 a 3 | a bola atravessando o canto da parede; o deslize em inteiros |
| os sensores, o contrato, o cérebro de teste e o registro | 1 a 1,5 | o cone com oclusão em inteiros |
| os testes, o e2e e as medições M1 a M6 | 1 a 1,5 | o WebGL no Chrome headless do e2e (Não verificado) |
| **o POC-01a** | **5,5 a 8,5** | — |
| o POC-01b (o Rapier), opcional | 1 a 2 | o wasm no Vite e o hash do snapshot no celular |

**O custo de errar:** se o POC-01a mostrar que a física inteira não basta, o descarte é a pasta `poc/` e a dependência `three` da página.
O jogo e a pesquisa não mudam.
