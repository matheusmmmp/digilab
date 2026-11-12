# Engenharia do parceiro: a jornada no mesmo cérebro e no mesmo registro (2026-11-12)

**Status:** PROPOSTO, sem código. É o desenho técnico do [`GDD_V3_PARCEIRO.md`](GDD_V3_PARCEIRO.md), e as fases estão no
[`PLANO_V3_PARCEIRO.md`](PLANO_V3_PARCEIRO.md). Os nomes de evento, de tipo e de chave abaixo são **propostas de nome**: cada um se fecha na
espec da fase que o usa. Os números são **PROPOSTOS, SEM FONTE**.

**A regra que manda em tudo (PAR-2, DECIDIDO pelo Matheus, 2026-11-12):** "tem que ser o mesmo cérebro para a jornada e as experiências
serem correlacionadas". Num projeto com event sourcing, isso quer dizer três coisas:
- **um registro:** a viagem é uma sequência de eventos no mesmo log do pet;
- **uma política:** a mesma instância de `Politica` age no habitat e na jornada;
- **um replay:** refazer o log refaz as duas áreas, na ordem, até o último float.

## 1. As regras da casa que este desenho segue

| regra | onde está | o que ela pede aqui |
|---|---|---|
| event sourcing: o estado nunca é salvo | `CLAUDE.md`, Arquitetura | a região, os habitantes e os eventos saem do log e da semente; nada da jornada vai para o save |
| determinismo; replay quebrado para tudo | `CLAUDE.md` | a simulação da região é inteira, ou em float com a mesma ordem nos dois motores |
| RNG de ambiente e de política separadas | `CLAUDE.md` | uma rng por fluxo novo (região, habitantes, eventos), por `derivar_semente` |
| mecânica nova atrás de chave desligada, com gabarito antes | `CLAUDE.md` | desligada, a vida de hoje sai byte a byte; o gabarito vai num commit próprio |
| uma versão de pet por mecânica | `web/app/CLAUDE.md` | os pets antigos não ganham a jornada sem uma decisão |
| paridade Python × TS, bit a bit no Node | `web/app/CLAUDE.md` | **não vale para a jornada** (PAR-14, exceção decidida pelo Matheus): a região existe só no TS. A paridade do cérebro nas vidas do habitat continua (seção 4.8) |
| evento desconhecido no log levanta erro | `CLAUDE.md` | cada evento novo tem leitor estrito, como o `mi` de hoje |
| `engine.py` não muda | `CLAUDE.md` | a região fica em subclasse ou módulo novo |

## 2. O que já existe e serve

- **A troca de mapa no mesmo registro: o evento `mi`.** `web/app/motor/motor.ts` (`case "mi"`) lê `{ilha}`, e o `Mundo` troca de layout
  (`trocarLayout`) ou passa para um mundo maior (`trocarParaMaior`). Os destinos ficam em `ILHAS_DE_TROCA` e `ILHAS_MAIORES`
  (`web/app/motor/mundo.ts`), espelhos do Python (`events.mudar_ilha`, `Mundo.trocar_layout`).
  - **O que falta:** hoje é só de ida, e a troca zera a orientação do pet e o registro das decisões do controlador
    (`docs/TAREFA_V3_ILHA_AGUA.md`, seção 12). A jornada precisa de ida e volta e de uma memória por área.
- **O mundo físico em inteiros** (`mundo.MotorMundo`, a decisão W de física no motor): a região reaproveita o mesmo motor de células.
- **Dois pets no mesmo mundo:** `grupo.Grupo` e a cooperação. O limite de hoje é explícito: "so dois pets nesta etapa"
  (`web/app/motor/grupo.ts`). Os habitantes da região são outro tipo de agente (seção 4.3), e não um terceiro pet do `Grupo`.
- **A luta pelo registro:** `["l", {r, s, m}]` (`Motor.lutarPoc`). Uma luta na jornada pode usar o mesmo caminho.
  - **O problema conhecido:** a semente da luta sai da posição no log (`docs/PLANO_V3_MMO.md`, seção 1). Na jornada, a semente sai por
    `derivar_semente` do evento.
- **A fala fora do registro:** o registro de apresentação `CHAVE.fala.jsonl` (`src/falaLivre.ts`). A camaradagem segue igual.
- **O que fica fora do registro, e tem de mudar:** o enigma da mitologia não é evento do log (D-E1-4, `src/mitologia.ts`). Na jornada,
  toda escolha que mexe no mundo ou no pet entra no log (seção 4.5).

## 3. A arquitetura, em uma figura

```
 log do pet (um só)
 ─┬─ t (tempo) ─ d (ação do dono) ─ ... ─ vj {ida, regiao} ─ t ─ es {evento, opcao} ─ l (luta) ─ t ─ vj {volta} ─ t ─ ...
  │
  ▼
 Motor ──┬── Mundo ativo:  habitat (layouts de hoje)  ⇄  região (layout novo, gerado da semente)
         ├── Corpo (o mesmo)
         ├── Política: o MESMO DigiBrain (percepção, memória, aprendizado)
         ├── Região: habitantes (controlador simples), recursos, dia e noite, catálogo de eventos
         └── Contadores derivados do log: inimigos derrotados, golpes usados, eventos vividos, afinidades
```

## 4. As peças

### 4.1 A viagem: um evento de ida e volta

- **Proposta:** um evento novo `vj` (`viagem`), com `{ida: <regiao>}` ou `{volta: true}`. O `mi` de hoje continua igual, para não mudar
  os pets que já o usam.
- **Um mundo ativo por vez.** Na ida, o habitat fica guardado no estado do motor (que sai do log), e a região é montada. Na volta, o
  contrário.
- **O habitat enquanto o pet está fora (PAR-6, DECIDIDO):** congela. Nada no habitat muda entre a ida e a volta: os objetos, a comida, a
  sujeira e os relógios do mundo da casa ficam como estavam. O tempo do pet (o corpo, a idade, o cérebro) continua andando na região pelo
  mesmo `t` do log.
- **A memória por área:** hoje a troca zera a orientação e o registro do controlador. Proposta: guardar a memória espacial por chave de área
  (`habitat`, `regiao:<id>`), para o pet lembrar de onde fica a água da região quando voltar a ela. O que ele aprendeu (pesos, hábitos)
  nunca zera: é o mesmo cérebro.

### 4.2 A região: um mundo gerado da semente

- **O layout** é gerado por uma rng própria, `derivar_semente(semente_do_pet, "regiao", id)`. A mesma região para o mesmo pet, sempre.
- **O tamanho e o bioma** ficam numa tabela fechada, como os `ILHAS_DE_TROCA`. A POC tem uma região só.
- **Os recursos** (fruta, água, abrigo) têm ciclos em ticks inteiros: amadurecer, apodrecer, renascer.
- **Dia, noite e clima:** funções do `t` e de uma rng do ambiente da região, nunca da política.

### 4.3 Os habitantes: agentes com controlador simples

- **PAR-7 (PROPOSTO):** na POC, cada habitante tem um controlador por regras com necessidades (fome, sono, território) e memória curta,
  com a sua rng derivada. Não é o DigiBrain.
- **Por quê:** o replay refaz cada habitante a cada tick. Um DigiBrain por habitante multiplica o custo e a superfície de paridade.
- **O orçamento (PROPOSTO, SEM FONTE):** o número de habitantes e o custo por tick saem da POC, medidos no Node e no Chrome do celular. A referência
  de hoje é o replay da luta (`web/app/scripts/medicoes/replay_lp2.json`), e o alvo é que o replay de uma vida com jornada continue na
  mesma ordem de grandeza.
- **O que o pet percebe dos habitantes:** entra pela percepção do cérebro (a `sens` do modular), como hoje o outro pet entra na cooperação.

### 4.4 Os eventos: emergentes, roteirizados e de camaradagem

- **Emergentes:** saem da simulação. Não precisam de evento no log, porque são função pura do estado. O motor emite um registro interno
  (como o `TrocaIlha` de hoje) para a vista mostrar.
- **Roteirizados:** um catálogo fechado em dados (JSON validado na carga, com versão). Cada entrada tem gatilho (lugar, hora, estágio,
  vínculo, eventos anteriores), opções e consequências no mundo ou no corpo. O disparo sai do estado. A escolha do dono entra no log
  (4.5). Um id de evento desconhecido levanta erro.
- **De camaradagem:** gatilhos da vista sobre o estado do motor (lugar marcado, volta para casa, calma depois de agito). A fala vai para o
  registro de apresentação, nunca para o do pet.

### 4.5 As escolhas do dono

- **Proposta:** um evento novo `es` (`escolha`), com `{evento: <id>, opcao: <id>}`. Leitor estrito: as chaves exatas, o evento precisa
  estar aberto e a opção precisa estar no catálogo.
- **A consequência** é sempre no mundo ou no corpo: um recurso muda de dono, um habitante muda de estado, o pet come, se cansa, se machuca.
  O cérebro aprende pelos ganchos de hoje (`consequencia_mundo`, `consequencia_corpo`). **Nenhuma escolha mexe no caráter direto** (PAR-5).
- **A recusa do pet** já existe no motor e vale aqui: a escolha do dono pode não virar ação do pet.

### 4.6 O cérebro: o mesmo, com mais mundo

- A instância de `Politica` não troca na viagem. O modular recebe percepções novas da região (habitantes, lugares, recursos) pelo mesmo
  `Protocol`.
- **A ponte de classes:** os objetos da região que não existem no habitat precisam de classe na percepção. Cada classe nova é uma mudança
  no cérebro, com paridade, como as classes de comida do paladar.
- **A pergunta de pesquisa que o PAR-2 cria (para a POC medir):** o que o pet aprende na região muda o que ele faz no habitat, e vice-versa?
  É o critério G-MESMO-CEREBRO do roadmap (fase J1).

### 4.7 Golpes, evolução e afinidades: contadores derivados

- Os golpes destravados, os inimigos derrotados por tipo, os golpes mais usados, os eventos vividos e a afinidade com cada personagem são
  **contadores derivados do log**. O motor os soma no replay, e nada disso é salvo.
- **A evolução** lê esses contadores na `_evoluir` de uma versão de pet nova. As versões antigas continuam com a tabela de hoje.
- **O cérebro escolhendo o golpe (PAR-9)** espera o núcleo da luta fechar. Até lá, a luta da jornada é a luta da POC de hoje.

### 4.8 Python e TS

- **PAR-14 (DECIDIDO pelo Matheus, 2026-11-12):** a jornada fica só no jogo web. Não há região, habitante, evento nem escolha no Python,
  nem exportador ou gabarito do Python para ela. É uma exceção à regra "toda regra de jogo nova entra no motor TS, com paridade", que
  vale para o que tem gêmeo no Python.
- **O que continua valendo:** o determinismo e o replay no TS (a mesma semente e o mesmo log dão a mesma vida, no mesmo runtime), as
  chaves desligadas e o byte a byte das vidas de hoje.
- **A fronteira com o cérebro:** o DigiBrain tem gêmeo no Python, com paridade. Por isso:
  - as vidas sem jornada continuam com a paridade do cérebro de hoje, intacta;
  - o que a região acrescenta ao cérebro (classes novas na percepção) entra só no TS, atrás da chave da jornada;
  - **uma vida com jornada não se refaz no Python.** É a consequência aceita do PAR-14: o pet viajante é um pet do jogo, não da pesquisa.
- **Os testes da região** são do Vitest: testes de propriedade (a região vive, a ida e volta refaz igual) e gabaritos gravados pelo
  próprio TS, para pegar mudança sem querer.
- **O que fica só na vista:** o desenho 3D da região, as animações, os balões e a câmera.

### 4.9 Versão, chave e save

- **A chave:** uma constante da jornada no motor TS (nome a fechar na espec), desligada por padrão. Desligada, a vida de hoje sai byte a byte.
- **A versão:** a jornada entra numa `VERSAO_PET` nova. Os pets antigos não ganham o botão de viajar sem uma decisão do Matheus.
- **O save** continua `{semente, log, versao}`. O log cresce com a viagem. O tamanho do save já foi medido na conta (CN0), e a jornada
  entra nessa conta antes de ligar.

## 5. Testes e gates técnicos

| gate | o que confere | onde |
|---|---|---|
| G-BYTE | com a chave desligada, as vidas de hoje saem byte a byte | um gabarito gravado antes, num commit próprio |
| G-IDA-VOLTA | um log com `vj` ida e volta refaz igual, duas vezes, no mesmo runtime, e o habitat volta idêntico (PAR-6) | teste de replay no Node (Vitest) |
| G-ESTAVEL | a região, os habitantes e os eventos não mudam sem querer | gabaritos gravados pelo próprio TS |
| G-PAR-CEREBRO | as vidas sem jornada continuam com a paridade do cérebro com o Python | os gabaritos de hoje |
| G-ESTRITO | `vj` e `es` com chave a mais, id desconhecido ou evento fechado levantam erro | testes de leitura |
| G-MESMO-CEREBRO | a política é a mesma instância nas duas áreas, e o que muda numa aparece na outra | o critério da POC (roadmap, J1) |
| G-CUSTO | o replay de uma vida com jornada fica dentro do orçamento PROPOSTO da POC | uma medição em disco, como `replay_lp2.json` |

## 6. Riscos técnicos

| risco | efeito | mitigação |
|---|---|---|
| a região em float diverge entre o Chrome e o Node | o replay do celular difere do Node no último bit | física e ciclos em inteiros, como o mundo de hoje |
| habitantes demais | o replay fica lento, e o celular sofre | controlador simples (PAR-7) e um teto medido na POC |
| a memória espacial por área cresce | o estado do cérebro pesa | chave por área e o alcance de hoje (128 células) |
| o catálogo de eventos muda e quebra logs antigos | o replay de um pet antigo falha | catálogo com versão, nunca editar uma entrada publicada |
| a semente da luta pela posição no log | o jogador "rola" a luta | semente por `derivar_semente` do evento da jornada |
| a fala na jornada pede a LLM ao vivo | custo e latência | modo livre gravado; sem a voz validada, gesto e rosto (PAR-15) |
