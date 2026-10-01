# PLANO — Digilab V2: a pesquisa primeiro

Status: **PROPOSTO** (2026-10-01). Decisão do Matheus: a V2 começa pela pesquisa; o jogo como produto (arte própria,
servidor, escala) vem depois e depende do que a pesquisa encontrar. Este documento é o plano de alto nível; cada fase
ganha o próprio plano de análise, congelado antes da run, e os números de cada gate só valem com artefato em disco.
Nada aqui está referendado: cada valor abaixo é PROPOSTO até o Matheus marcar.

## 1. De onde a V2 parte

A v1 fecha com uma leitura consolidada (`docs/LEITURA_CONSOLIDADA_DONO.md`): **neste motor o dono pesa pelo cuidado,
não pelo ensino.** A hipótese central foi refutada na confirmatória (atencioso − aleatório −0,034 [−0,072; +0,006]);
a divergência entre os braços dos donos é de 0,02 bit (JSD, `artifacts/divergence.json`; ao instinto, 0,03–0,05 bit); só 13–18% das decisões têm fator explicável; o genoma explica 4,9%;
a forma final explica 96% da taxa no painel; o canal contínuo do caráter até a luta não abriu. A pergunta do efeito do
dono está **encerrada**. O que sobra é a pergunta sobre o aprendiz e sobre o ambiente em que ele age.

O que a v1 deixa de ativo e a V2 preserva: determinismo até o último float com replay do log, event sourcing, paridade
Python/web, gates com artefato, plano de análise antes da run, sementes de calibração separadas das de validação,
registro de desvios, uma versão de pet por mecânica, e as regras da literatura (`literatura-digilab`: nunca alegar
como novo instinto × aprendido, herdar o prior, nem "ensinado, não roteirizado").

## 2. A pergunta da V2 (PROPOSTA)

> **Que aprendiz e que ambiente fazem o ensino do dono deixar uma marca mensurável e explicável no comportamento do
> pet, separável do efeito do cuidado?**

Quatro hipóteses, uma por fase:

- **H1 (aprendiz e ambiente):** com mais decisões em que o dono importa e um aprendiz cuja atualização depende da
  política atual, donos coerentes produzem políticas distinguíveis entre si e do aleatório.
- **H2 (legibilidade):** o jogador reconhece o pet que ele mesmo criou entre dois gêmeos, acima do acaso, e a
  preferência acompanha o sucesso do treino (efeito IKEA condicionado ao sucesso).
- **H3 (criação × seleção):** num desenho fatorial, o efeito da criação pelo usuário e o da seleção pelo usuário sobre
  a linhagem são separáveis, com intervalos fora de zero. É a lacuna que a revisão de literatura não encontrou publicada.
- **H0 de cuidado (controle permanente):** em toda fase, o braço "só cuidado" entra como controle, porque é o único
  efeito robusto da v1 e qualquer marca nova tem de se separar dele.

## 3. Fases e gates

### Fase 0 — fechar a v1 (sem pesquisa nova)

1. Tag `v1-final` na main; a pasta v1 vira só leitura; CLAUDE.md da V2 curto, apontando para o histórico.
2. Inventário do jogo: o que existe, o que a pesquisa usa, o que é provisório e o que foi validado (o passo 1 do
   `docs/TODO_INTERACAO_CORPO.md`).
3. Pendências pequenas: leitura do Matheus das 50 falas da moldura e da avaliação cega; redesenho do vínculo (hoje
   premia o dono aleatório: 5 de 6 Megas contra 3 de 6, `artifacts_campanha/mega/limiar_vinculo.json`); tradução dos
   49 itens em japonês do corpus; rodada do comando com o estilo da espécie ligado.

Gate 0: nenhum; é limpeza. Sai quando os quatro itens estiverem na main.

### Fase 1 — fazer o aprendizado pesar (H1)

Duas alavancas, testadas em separado e depois juntas, cada uma numa versão de pet:

- **Ambiente mínimo (1a):** uma interação só, escolhida no inventário, em que o pet decide e sofre consequência (o
  `TODO_INTERACAO_CORPO` propõe comida posta no cenário: perceber, aproximar, consumir ou recusar). O dono muda a
  situação; o pet decide. Sem corpo 2D completo.
- **Aprendiz novo (1b):** uma política com lobos nomeados (percepção, memória e emoção, impulsos, decisão), aprendizado
  só no lobo de decisão, atualização dependente da política atual (feedback como vantagem, não recompensa fixa), prior
  do instinto como pesos iniciais, traços como média lenta por fora. Ativação sem função transcendental e pesos em
  ponto fixo, para a paridade Python/web; abaixo de mil pesos, para o replay.

Gates da fase 1 (PROPOSTOS; plano de análise congelado antes; sementes de calibração 3101…3505, validação 4101…4505):

| gate | critério | referência da v1 |
|---|---|---|
| G1 replay | vida bit a bit pelo log, Python e web | já vale |
| G2 equivalência | aprendizado desligado = instinto, byte a byte | padrão das chaves |
| G3 divergência | JSD entre donos coerentes ≥ 0,10 bit, IC fora de 0,02 | 0,02 bit |
| G4 legibilidade | fator explicável em ≥ 50% das decisões, com a regra de honestidade de hoje | 13–18% |
| G5 separação do cuidado | a divergência de G3 se mantém no braço sem mortes e sem lesão | metade do efeito da V3 vinha das mortes |
| G6 sem deriva | distância da política ao instinto não cresce sem limite em 14 dias | traços como freio |

Só com G3, G4 e G5 passando a fase 2 começa. Falhando, a V2 registra o resultado negativo e para: é um resultado.

### Fase 2 — humanos (H2)

20 a 30 pessoas, 2 semanas, cada uma com dois ovos gêmeos (mesma semente de genoma e de ambiente): um cuidado por ela,
um por um dono sintético calibrado no comportamento dela. Medidas: reconhecimento do próprio pet entre os dois,
preferência, sucesso do treino, tempo de uso. Pré-condições: vínculo redesenhado (fase 0), equilíbrio já fechado, e uma
decisão sobre a arte, porque os sprites da Bandai não podem sair do uso pessoal: ou arte própria antes da fase 2, ou
participantes em sessão local, sem distribuição.

Gates: reconhecimento acima do acaso com IC fora de 0,5; preferência correlacionada ao sucesso; nenhum participante com
o pet morto por regra nossa (as mortes da v1 eram todas "lesão sem tratar").

### Fase 3 — criação × seleção (H3)

Desenho fatorial: dono (criação) × escolha de qual pet cruzar (seleção), com os humanos da fase 2 ou donos sintéticos
calibrados neles. Medir o dono pela **distribuição de formas** que ele produz, não pela força na arena (o E1 mostrou
que a força mede o arquétipo). Gate: variância atribuível a criação e a seleção separadas, com IC fora de zero.

### Fase 4 — só depois: o jogo como produto

Arte própria ou licenciada, servidor com persistência do log, comparação com um produto vivo. Fora deste plano.

## 4. Fora do escopo da V2 de pesquisa

Mecânicas de jogo novas fora do que a fase 1a pede; combate em tempo real; PvP; MCP real; treino, luta e itens por
comando; execução de qualquer run sem plano de análise registrado antes.

## 5. Como se decide

Cada fase abre com uma tarefa própria (`docs/TAREFA_V2_FASE<N>.md`) e um plano de análise (`docs/PLANO_ANALISE_V2_FASE<N>.md`)
commitado antes da run. Os números dos gates são PROPOSTOS até o Matheus referendar; a mudança de um número depois de
uma run vai para `docs/REGISTRO_DESVIOS.md`. O primeiro passo concreto é a fase 0, item 2: o inventário do jogo, que
decide qual é a interação mínima da fase 1a.
