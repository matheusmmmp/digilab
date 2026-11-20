# ESPEC — SOCIAL_PAR M2: a companhia no corpo

- **Status:** PROPOSTA, para o checkpoint do M2. Nenhum código entra antes do "aprovado" do Matheus.
- **Data:** 2026-11-19.
- **Fontes:**
  - o mapa dos mecanismos (`docs/INVESTIGACAO_V3_SOCIAL_PAR.md`, seção 5, a linha M2, e a SP-3);
  - a espec do M1 (`docs/ESPEC_SOCIAL_PAR_M1.md`) e o código dele (#1018);
  - o código lido em 2026-11-19, no `v3-social-par-m1`: `digilab/corpo.py` (a solidão, os emissores e o `passo`), `digilab/corpo_grafo.py`
    (o `Emissor`), `digilab/motor_corpo.py` (o tick do corpo) e `digilab/grupo.py` (o `_avancar` e o contato).

## 0. O que é o M2

**Hoje, estar com o outro não muda nada no corpo.**
- **A solidão** sobe 450 por tick acordado no corpo do pet da S (a `ConfigCorpo.solidao_sobe` desse corpo; C = 450000), e só o carinho
  do dono a baixa (−180000 por carinho).
- **O outro perto** não entra em nenhum emissor.
- **Por isso, com o M1,** o P1 do `seguir` não tem o que aprender: a espec do M1 prevê ≈ 0 para ele (seção 3.4).

**O M2 é um emissor novo no grafo do corpo, a `companhia`:** com outro pet em contato físico, a solidão baixa. O emissor lê só a posição
do outro, e nada do corpo dele (o G-RECEPTOR-SOCIAL). É a CV-5 e a DP-12 adiantadas, como a SP-3 já decidiu.

## 1. Por que agora

- **O M1 deu ao pet a ação** de ir até o outro. O M2 dá a razão no corpo para ela valer.
- **É o 4º passo do caminho** percepção → intenção → ação → consequência no corpo, o segundo ponto em que ele quebra hoje (a investigação,
  seção 5).
- **O M1-5 aprovou a ordem:** o código do M1, depois o do M2, e um plano com os dois braços.

## 2. A chave

- **`ConfigCompanhia(ligada: bool = False, raio_celulas: int = 1, alivio_solidao: int = 900)`**, em `digilab/config.py`. Todos os valores
  são PROPOSTOS, SEM FONTE; a seção 9 traz as decisões.
  - **Desligada,** toda vida de hoje sai byte a byte, a do pet sozinho e a do grupo (o G2), contra um gabarito gravado num commit próprio,
    antes do código.
  - **Ligada, com o pet sozinho,** a vida também sai byte a byte (o G2b): sem outro pet, a companhia é 0.
- **Ligada, ela exige a solidão no corpo:** a `ConfigCorpo` com os `drives_novos`. Sem eles, falha alto na montagem.
- **Ela é independente do M1.** A companhia é do corpo e vale com qualquer cérebro. O plano da medida combina as duas.
- **Fora do jogo nesta etapa:** o `GrupoDoJogo` não liga a chave (seção 9, M2-6).

## 3. As interfaces

### 3.1 O que conta como companhia (`digilab/grupo.py`)

**No começo de cada tick do grupo,** antes de qualquer pet andar, o grupo conta para cada pet presente quantos outros estão em contato:
- **o contato** é o de hoje, o `em_contato(a, b, cmf, raio_celulas)`: as células a até `raio_celulas` em Chebyshev (com 1, a mesma ou
  a vizinha). É o raio do toque (`ConfigGrupo.raio_toque_celulas`) e o do contato do primário da S;
- **a contagem** usa as posições do começo do tick, todas de uma vez. Assim, a ordem em que os pets andam dentro do tick não muda a
  companhia de nenhum;
- **o grupo entrega** a contagem ao motor de cada pet (`m._companhia = n`), e o motor a passa ao corpo nesse tick.

```python
# em Grupo._avancar, a cada tick, antes do laco dos pets (so com a ConfigCompanhia ligada)
pos = {i: self.motores[i].pet for i in presentes}
for i in presentes:
    self.motores[i]._companhia = sum(1 for j in presentes if j != i and em_contato(pos[i], pos[j], cmf, ccp.raio_celulas))
```

- **Hoje o contato só é conferido nos ticks com decisão** (`_toque_e_disputa`). A companhia é conferida em todo tick, porque a solidão anda
  por tick. Essa conta é nova e não mexe no registro do toque.
- **Sem o grupo** (o pet sozinho), o motor não recebe a contagem, e ela é 0.

### 3.2 O emissor (`digilab/corpo.py`, no grafo da seção 18)

```python
Emissor("companhia", "companhia", 1, (("solidao", -alivio_solidao),))    # fase 1; dispara so acordado e com n >= 1
```

- **O gatilho novo, `companhia`,** entra no `GATILHOS_TICK` do `digilab/corpo_grafo.py`, no molde do `necessidades` do banheiro (uma
  contagem que o motor entrega a cada tick). Ele dispara uma vez no tick, com o pet acordado e n ≥ 1.

- **O `Corpo.passo(antes, necessidades=..., companhia=n)`** ganha o argumento `companhia`, um inteiro ≥ 0:
  - com o pet acordado e n ≥ 1, a fase 1 soma `−alivio_solidao` à solidão, uma vez só, qualquer que seja n (seção 9, M2-4);
  - dormindo, nada (seção 9, M2-5): a solidão também só sobe acordada;
  - a soma entra na fase 1 com as subidas dos drives novos, e o corte é o de hoje, uma vez por químico. A solidão fica em [0, C].
- **Sem a chave,** o emissor não está no grafo, e um `companhia` diferente de 0 falha alto.
- **O emissor não lê nenhum químico** (o `le` vazio). A quantidade vem de fora, só da contagem física.

### 3.3 O motor (`digilab/motor_corpo.py`)

- O tick do corpo passa `companhia=self._companhia` ao `passo`, com o `_companhia` zerado depois de usado. Assim, um tick sem a entrega do
  grupo dá 0, e o motor não carrega a contagem para o tick seguinte.
- **Com a chave e o motor num grupo,** um tick sem a entrega falha alto. O grupo entrega sempre, então isso pega um erro de ordem.
- **O receptor não muda:** o `solidao` já vai à `PercepcaoCorpo`, e o modular já o lê (`RECEPTORES_DIGIBRAIN`).

### 3.4 O que o cérebro aprende com isso

**Nada no cérebro muda.** Com o M1 ligado:
- **o P1 do `seguir`** passa a ver a solidão subir menos, ou cair, depois de chegar ao outro;
- **o incentivo** (`valor_previsto` do desfecho, pelos drives) fica positivo quando a solidão está em falta. É o "irmão que vem quando
  chamam" da investigação: com a solidão alta, ir até o outro passa a valer;
- **o `onde_comeu`** segue pelo canal da comida, como no M1.

## 4. O laço entre os dois corpos

**A investigação pede um teste do laço de ganho entre os dois corpos.** Com o M2 não há laço:
- **a companhia de A** depende só das posições de A e de B, e não de nenhum químico de B. O mesmo vale para a de B;
- **por isso, o alívio de um** não entra no corpo do outro. Os dois aliviam juntos porque estão juntos, e não porque um sente o outro;
- **o contágio** (a DP-12, o humor de um passando ao outro) fica fora. É o que a SP-3 queria evitar: "o aprendido misturar o contágio com a
  companhia".

**O teste:** pela AST, o código novo do grupo só lê o `pet` (a posição) de cada motor, e o emissor tem o `le` vazio. Um teste de vida
confere que trocar o corpo do outro (outra semente de corpo, as mesmas posições pela gravação) não muda a companhia de A.

## 5. Os testes (`tests/test_corpo_companhia.py`)

| teste | o que confere |
|---|---|
| **G2, a chave desligada** | as vidas de hoje, do pet sozinho e do par da S, saem byte a byte contra o gabarito gravado antes do código |
| **G2b, ligada sem o outro** | o pet sozinho com a chave sai byte a byte igual ao desligado |
| **o emissor** | acordado e em contato, a solidão do tick é a de hoje menos `alivio_solidao`; com dois em contato, o mesmo; dormindo, a de hoje |
| **o corte** | a solidão não fica abaixo de 0 |
| **a contagem** | dois pets na mesma célula ou vizinhos contam 1; a duas células, 0; a contagem não depende da ordem dos pets no tick |
| **sem a solidão** | a chave ligada sem os `drives_novos` falha alto na montagem |
| **um tick sem a entrega** | com a chave, num grupo, falha alto |
| **o laço** | pela AST, o grupo só lê a posição; o emissor não lê químico; o corpo do outro trocado não muda a companhia |
| **o replay** | o `reproduzir_grupo` refaz a vida do grupo com a chave, byte a byte |
| **o determinismo** | a mesma semente dá o mesmo registro, com a chave |
| **com o M1** | numa vida do par com as duas chaves, o desfecho do `seguir` na solidão sai do 0 |

**O G-PAR (o espelho no TS)** só entra se o M2 for ao jogo (seção 9, M2-6). Ele pega o `corpo.ts`, o `grupo_jogo.ts` e o gabarito do grupo.
Como em toda peça, a paridade prova só que as duas implementações concordam.

## 6. Os critérios de aceitação

1. O gabarito das vidas de hoje está gravado num commit antes do código, e o G2 e o G2b passam.
2. Todos os testes da seção 5 passam, e a suíte inteira roda, com a contagem e as falhas conhecidas no corpo do PR.
3. O `engine.py` e o `mundo.py` não mudam (o diff). O `grupo.py`, o `corpo.py`, o `corpo_grafo.py` e o `motor_corpo.py` mudam só atrás da chave.
4. Os números novos estão em `digilab/config.py`, com status e fonte.
5. Nenhuma vida de pesquisa roda na etapa de código.

## 7. A medida (para o plano novo, depois do código)

- **O instrumento é o da S3, sem mudança:** os braços C, B1 e B2, o VIVO, a GRAV e a OUTRA, o G-DET e o primário T\*c.
- **Os braços do cérebro e do corpo,** propostos, pelo M1-5 e pelo D-SP-63:
  - **M1:** as unidades sociais, sem a companhia;
  - **M1-inc0:** o M1 com o incentivo social em 0, o controle do D-SP-63 (as unidades a mais, sem aprendizado);
  - **M1+M2:** as unidades e a companhia.
- **A GRAV também tem companhia:** a companhia é física. A gravação de P põe P nas mesmas posições, e o corpo de F sente P igual. Assim, o
  D_A segue medindo a resposta de P a F, e não a companhia em si.
- **O previsto, PROPOSTO:**
  - no M1+M2, o D_A sai de ≈ 0, no sentido de P chegar mais depressa a F quando P responde. O B1, com os dois longe da casa, é o braço mais
    provável;
  - no M1-inc0, o D_A que sobrar é o das unidades a mais.
- **O que essa medida não pode dizer:** se o pet "gosta" do outro além da solidão. O M2 dá ao outro só o valor de baixar a solidão.

## 8. O que fica fora

- **O contágio** (DP-12): o estado de um corpo passando ao outro.
- **O M3** (a memória por parceiro) e **o M4** (o som e os sentidos longos).
- **A companhia por perto** (até 6 células) e por som: só o contato, nesta etapa (seção 9, M2-1).
- **O jogo web**, até a decisão M2-6.
- **Qualquer mudança no `engine.py`, no `mundo.py`** e no registro do toque.

## 9. As decisões para o Matheus (o checkpoint do M2)

| id | o que decidir | recomendação | custo de errar |
|---|---|---|---|
| **M2-1** | o que conta como companhia | **o contato, até 1 célula em Chebyshev** (o raio do toque e o do primário da S) | "perto" (até 6 células) pega a casa: na S0, os dois ficam perto 64 % da vida porque a casa atrai os dois. A companhia viraria um bônus da casa, e não do outro |
| **M2-2** | o alívio por tick | **900 = 2 × a subida da solidão desse corpo (450)**: em contato, a solidão cai na mesma velocidade em que sobe sozinho | com 450, a solidão só para de subir, o delta do P1 fica perto de 0 e o `seguir` segue sem valor. Muito acima, o pet fica preso ao outro, e um carinho do dono passa a valer menos que alguns minutos juntos |
| **M2-3** | quando contar | **em todo tick, com as posições do começo do tick** | contar só nos ticks com decisão (como o toque de hoje) daria 1 tick em 15, e um alívio 15 vezes menor. Contar com as posições de depois de cada um andar faria a ordem dos pets mudar a companhia |
| **M2-4** | dois ou mais outros | **o mesmo alívio de um** | no par não faz diferença. Somar por outro antecipa a aglomeração (DP-12), que é outra mecânica |
| **M2-5** | dormindo | **sem alívio**, como a solidão, que só sobe acordada | com alívio dormindo, dormir juntos viraria a forma mais barata de baixar a solidão, sem ação nenhuma |
| **M2-6** | o M2 no jogo | **só no Python até a medida,** como o M1-4 | levar ao jogo antes da medida põe no ovo um corpo sem evidência e custa o G-PAR duas vezes, se a medida mudar o desenho |
