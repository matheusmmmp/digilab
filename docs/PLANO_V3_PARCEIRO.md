# Roadmap do parceiro: da POC do mundo vivo à personalização (2026-11-12)

**Status:** PROPOSTO, sem código. O desenho do jogo está no [`GDD_V3_PARCEIRO.md`](GDD_V3_PARCEIRO.md), e o técnico no
[`ENGENHARIA_V3_PARCEIRO.md`](ENGENHARIA_V3_PARCEIRO.md). Os tamanhos (P, M, G) são estimativas relativas, não prazos. Os números são
**PROPOSTOS, SEM FONTE**.

**A ordem aprovada pelo Matheus (2026-11-12):**
1. a evolução por progresso e relação;
2. as escolhas e os eventos;
3. os golpes que se destravam;
4. a viagem em regiões;
5. a jogress pela relação;
6. a personalização.

Com o acréscimo dele: começar por uma POC de um mundo simulado vivo, com o mesmo cérebro (PAR-2, PAR-3).

**Como as duas coisas se juntam:**
- **A POC (J1, J2) vem primeiro.** Ela é a fundação da viagem, e o item 4 vira a expansão de uma região que já funciona.
- **A evolução (J3) não depende da POC.** Ela mexe no habitat e pode correr em paralelo, numa worktree própria.

## 1. As fases

| fase | o que entrega | depende de | tamanho |
|---|---|---|---|
| **J0** | este desenho (GDD, engenharia, roadmap) e as decisões PAR-4 a PAR-15 | — | P |
| **J1** | a POC do mundo vivo no Python: uma região, habitantes, recursos, dia e noite, a viagem de ida e volta, o mesmo cérebro | J0; o plano de análise da J1 | G |
| **J2** | o porte da J1 para o TS, com paridade, e uma vista mínima: sair pelo cais, andar na região, voltar | J1 | G |
| **J3** | a evolução por progresso e relação (os contadores do log; o vínculo no Champion e no Ultimate) | J0 (corre em paralelo com a J1) | M |
| **J4** | os eventos roteirizados e as escolhas do dono na região; a abertura do brasão (PAR-4) | J2 | M |
| **J5** | a camaradagem: os gatilhos novos, primeiro com gesto e rosto, depois com a fala | J4; a voz validada (DC5) para a parte falada | M |
| **J6** | os golpes que se destravam e as competências de exploração | J2; o núcleo da luta fechado (N0–N4); PAR-9 | G |
| **J7** | mais regiões (biomas), com a memória por área | J4 | G (conteúdo) |
| **J8** | os personagens com afinidade e a jogress temporária | J4, J6 | G |
| **J9** | a personalização: o Tamer (PAR-12) e o Digimon fora do desenho (PAR-13) | J2 | M |

## 2. Cada fase

### J0. O desenho (este PR)

- **Entrega:** os três documentos e a lista de decisões.
- **Aceite:** o Matheus decide as PAR-4 a PAR-15, ou adia cada uma com o motivo.
- **Precisa do Matheus:** as decisões da seção 11 do GDD. As que travam a J1 são a PAR-6 (o habitat enquanto o pet está fora), a PAR-7 (o
  controlador dos habitantes) e a PAR-14 (Python primeiro).

### J1. A POC do mundo vivo (pesquisa, no Python)

- **Antes da primeira vida:**
  - a seção da J1 na tarefa ([`TAREFA_V3_PARCEIRO.md`](TAREFA_V3_PARCEIRO.md));
  - o plano de análise (`docs/PLANO_ANALISE_V3_PARCEIRO.md`);
  - a faixa de sementes pedida ao coordenador e posta em `FAIXAS_RESERVADAS`.
- **O que se constrói:**
  - `ConfigRegiao` (desligada) e o gabarito byte a byte das vidas de hoje, num commit próprio;
  - a região gerada da semente, com recursos em ciclos inteiros e dia e noite;
  - os habitantes com controlador simples (PAR-7);
  - o evento `vj` de ida e volta, e a memória espacial por área;
  - a bancada: vidas com e sem jornada, com o mesmo genoma e o mesmo dono.
- **Os critérios (PROPOSTOS, a fechar no plano de análise):**
  - **G-VIVO:** sem o dono agir, dias diferentes da região têm acontecimentos diferentes. A medida proposta é a diversidade de eventos
    emergentes por dia, contra uma região "parada" (os mesmos habitantes sem necessidades) como controle;
  - **G-MESMO-CEREBRO:** o que o pet viveu na região muda o que ele faz no habitat, e vice-versa. A comparação proposta é pareada por
    semente: com e sem viagem, a mesma medida de comportamento no habitat;
  - **G-IDA-VOLTA** e **G-BYTE** (seção 5 da engenharia);
  - **G-CUSTO:** o tempo do replay de uma vida com jornada, medido e gravado em disco.
- **Se um gate falhar:** a V3 não para. O resultado negativo é registrado, e a J2 decide com o Matheus.
- **Máquina:** no máximo 4 processos, uma run de pesquisa por vez.

### J2. O porte e a vista mínima (jogo)

- **O que se constrói:**
  - o porte da região, dos habitantes e do `vj` para o TS, com os gabaritos da J1;
  - uma `VERSAO_PET` nova;
  - na vista, a saída pelo cais, a região em 3D no estilo da ilha (objetos em cartoon), os habitantes com sprites que já existem, e a volta.
- **Aceite:**
  - G-PAR bit a bit no Node;
  - o e2e da ida e volta;
  - as capturas no desktop (1920×950) e no celular (390×844).
- **Fora:** eventos roteirizados, escolhas e fala. A região só vive.

### J3. A evolução por progresso e relação (jogo e Python)

- **O que se constrói:**
  - os contadores derivados do log: inimigos derrotados por tipo, golpes usados, marcos vividos;
  - na `_evoluir` de uma versão nova, essas entradas e o vínculo pesando no Champion e no Ultimate.
- **Aceite:**
  - os pets antigos continuam iguais (gabarito);
  - a paridade da nova tabela;
  - a tela da Evolução explica as entradas novas.
- **Precisa do Matheus:** a tabela nova (quais entradas pesam em cada estágio), com a recomendação na espec da fase.

### J4. Os eventos e as escolhas (jogo e Python)

- **O que se constrói:**
  - o catálogo fechado de eventos roteirizados, com versão;
  - o evento `es` com leitor estrito;
  - as consequências no mundo e no corpo;
  - a abertura do brasão por interações (PAR-4).
- **Aceite:**
  - G-ESTRITO;
  - nenhuma escolha mexe no caráter direto (um teste confere);
  - o replay de um log com escolhas refaz igual.
- **Conteúdo da primeira leva:** poucos eventos (PROPOSTO: de 6 a 10), escolhidos para cobrir os tipos da seção 6 do GDD.

### J5. A camaradagem (vista, depois fala)

- **J5a (vista):** os gatilhos novos (lugar marcado, volta para casa, calma depois de agito) com gesto e reação de rosto. Só vista.
- **J5b (fala):** os mesmos gatilhos pela fala da rede, com a LLM como voz, quando a voz do jogo estiver validada (PAR-15).
- **Aceite:** só aparece o que o motor tem (P4); a fala vai para o registro de apresentação.

### J6. Os golpes e as competências (jogo e Python)

- **Antes:** o núcleo da luta fechado e a PAR-9 decidida (o cérebro escolhe o golpe ou não).
- **O que se constrói:**
  - os golpes destravados pelo que o pet viveu, que ficam entre as formas (PAR-8);
  - as competências de exploração que abrem partes da região.
- **Aceite:**
  - a paridade;
  - a luta de hoje sai igual com a chave desligada;
  - nenhum desenho novo de Digimon (a regra "sem acréscimos").

### J7. Mais regiões

- **O que se constrói:** novos biomas na tabela de regiões, com os seus habitantes, recursos e eventos.
- **O custo** é de conteúdo (desenho, eventos, equilíbrio), não de motor. Cada região nova é uma entrada de tabela e uma leva de eventos.

### J8. Os personagens e a jogress

- **O que se constrói:**
  - a afinidade com personagens, feita de atos (PAR-10);
  - a jogress temporária, que pede afinidade com o personagem e vínculo com o dono (PAR-11).
- **Antes:** a lista de formas fundidas com sprite disponível no atlas. Nenhuma arte nova sem decisão.

### J9. A personalização

- **J9a:** o Tamer com nome, rosto e roupa (PAR-12).
- **J9b:** o Digimon fora do desenho (aura, rastro, efeito de golpe, emblema, título, item), que segue até o Mega (PAR-13).
- **Fora:** vender peças. Os Bits nunca são vendidos (CN-11/12).

## 3. O que pode correr em paralelo

| ao mesmo tempo | por quê |
|---|---|
| J1 e J3 | a J3 mexe só na evolução do habitat; a J1, numa região nova; os arquivos não se cruzam (a `_evoluir` só na J3) |
| J5a e J6 | a J5a é só vista; a J6 é motor da luta |
| J7 e J9 | conteúdo de região e personalização não se tocam |

**Sempre uma run de pesquisa por vez** (a J1 e qualquer medição do combate disputam a máquina).

## 4. Os riscos do roadmap

| risco | efeito | o que fazer |
|---|---|---|
| a J1 mostra que a região não parece viva | a jornada vira um mapa vazio | o G-VIVO falha alto; a J2 só começa com a decisão do Matheus |
| o G-MESMO-CEREBRO não aparece | o PAR-2 vale, mas o jogador não sente a ligação | medir antes de construir conteúdo; tornar visível o que já liga (a memória, a fala) |
| o núcleo da luta atrasa | a J6 espera | a J6 é a única fase presa à luta; o resto anda |
| a voz não valida | a camaradagem fica só em gesto | a J5a entrega o momento sem a fala |
| o conteúdo cresce mais rápido que o motor | regiões bonitas e rasas | uma região por vez, cada uma com o seu G-VIVO |
