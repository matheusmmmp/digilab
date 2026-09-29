# Design — evolução canônica: Champion → Ultimate → Mega

Status: **para aprovação** (pedido do Matheus, 2026-09-29: "tem que seguir o cânone"). Nada foi implementado. Todo número abaixo é PROPOSTO (sem fonte).

## 1. O problema

O jogo tem 4 estágios: In-Training, Rookie, Champion e adulto. Na passagem Champion → adulto, o sinal do eixo complementar do caráter escolhe uma de duas formas **irmãs**:

| linha | complementar ≥ 0 | complementar < 0 |
|---|---|---|
| brigão | duelista (MetalGreymon, Ultimate) | furioso (WarGreymon, Mega) |
| guardião | espelho (Taomon, Ultimate) | muralha (Sakuyamon, Mega) |
| caçador | sentinela (Garudamon, Ultimate) | emboscador (Phoenixmon, Mega) |
| colosso | vigia (WarGrowlmon, Ultimate) | titã (Gallantmon, Mega) |

(Os exemplos são da brasa; as outras espécies seguem igual.)

Isso fere o cânone de três jeitos:
- **Ultimate e Mega ficam no mesmo nível.** O Mega não vem depois do Ultimate e não é mais forte que ele.
- **O Mega sai do caráter "desequilibrado".** Um Greymon sem paciência vira WarGreymon; um paciente vira MetalGreymon.
- **A forma sombria herda o nível da base.** WarGreymon sombrio é Mega; Taomon sombrio é Ultimate.

**O que ajuda.** Em todas as linhas das 4 espécies, a forma "+" é o Ultimate e a forma "−" é o Mega da **mesma cadeia canônica**: Greymon → MetalGreymon → WarGreymon, Garurumon → WereGarurumon → MetalGarurumon, Togemon → Lillymon → Rosemon... Os 32 sprites já estão no atlas. Falta o motor tratar os dois como **estágios**, não como irmãos.

## 2. A proposta

Cinco estágios nos pets novos (**v5**). A forma mecânica continua sendo escolhida pelo caráter, como hoje; o que muda é o **nível** e o **sprite**.

| estágio (id interno) | nível na tela | como chega |
|---|---|---|
| bebe | In-Training | — |
| crianca | Rookie | como hoje (cuidado ≥ 80% → sereno) |
| adolescente | Champion | como hoje (eixo dominante → linha) |
| adulto | **Ultimate** | como hoje: o tempo, 10 lutas, 80% de vitória no estágio; o eixo complementar escolhe a **forma** (duelista ou furioso...) |
| **mega** (novo) | **Mega** | seção 3 |

**Os sprites saem da linha, não da forma.**
- No Ultimate, as duas formas da linha aparecem como o Ultimate canônico.
- No Mega, as duas aparecem como o Mega canônico.
- O arquétipo, que já aparece na tela, é o que distingue as duas: "MetalGreymon · Duelista" e "MetalGreymon · Furioso"; depois "WarGreymon · Duelista" e "WarGreymon · Furioso".
- Assim ficam as 8 formas mecânicas: as passivas, os bots da V21C, o combate e a pesquisa não mudam. Não é preciso nenhum sprite novo.

**No Mega, a forma não muda. O pet fica mais forte:**

| constante | Ultimate (hoje) | Mega (PROPOSTO) |
|---|---|---|
| multiplicador de estágio (`CAT.estagio`) | 1,0 | 1,15 |
| vida na escala da campanha (`CESC.vida`) | 1500 | 3000 |
| teto de treino do estágio (`CTR.tetoEstagio`) | 14 | 16 |
| teto de treino da vida (`CTR.tetoVida`) | 36 | 40 |
| regras de gambit (`CV21.maxRegras`) | 8 | 8 (o limite da tela) |
| intervalos das janelas da educação (`CED.intervalos`) | os do adulto | iguais aos do adulto |

A passiva continua a da forma. Fica em aberto se o Mega deve reforçar a passiva; eu recomendo que não, na primeira versão: primeiro medir só o ganho de estágio.

## 3. Ultimate → Mega

Três condições, as três PROPOSTAS:

1. **Tempo no Ultimate:** 24 h no ritmo rápido, 48 h no clássico. É um novo item em `DUR_EVO` e `DUR_CLASSICA`.
2. **Qualificação:** 10 lutas no estágio, com ≥ 80% de vitória. É a mesma regra da passagem para o Ultimate (`CLE.limiarTaxa`), reaproveitada.
3. **Vínculo ≥ 0,7:** a ligação com o parceiro, que é o que o cânone pede para o Mega (os brasões do Adventure).

**Consequência que vem de graça:** a forma sombria tem vínculo com teto de 0,6 (`CSO.tetoVinc`), **então ela nunca chega ao Mega**. O pet forçado à exaustão fica travado no Ultimate sombrio, como o SkullGreymon do cânone é um beco sem saída. Não precisa de regra própria.

## 4. A forma sombria

- **Quando:** decide-se na passagem Champion → Ultimate, com sobrecarga ≥ 60, como hoje.
- **Mecânica:** a de hoje (`CSO.formas`: stats, passiva sombria, vínculo com teto). Os ids não mudam.
- **Na tela:** o sprite é o do **Ultimate** da linha, com o nome "[Ultimate] sombrio" (exemplo: "MetalGreymon sombrio"). Todas as sombrias passam a ser Ultimate.
- **Mega:** nunca (seção 3).
- **Jornada:** uma sombria enfrenta o chefe da campanha como Ultimate. Com a escala, é muito difícil (seção 5), e esse é o preço da exaustão. Resta a herança: um ovo novo da geração seguinte.

## 5. A campanha

**Canonicamente, o Piedmon é Mega** (um dos Mestres das Trevas da Montanha Espiral). A proposta ganha um lugar novo, e os sprites existem no atlas:

| lugar | nível sugerido | rivais |
|---|---|---|
| Campina | Rookie | Gazimon (como hoje) |
| Torre de pedra | Champion | Tortomon, Guardromon, Devidramon (como hoje) |
| Cidadela | Ultimate | **Myotismon** (novo; vilão Ultimate do Adventure) |
| **Montanha Espiral** (nova) | Mega | **Puppetmon**, **Machinedramon** e o **Piedmon** (chefe final) |

- A regra de hoje continua: vencer qualquer rival de um lugar abre o próximo.
- A jornada termina ao **vencer o Piedmon**, como hoje. Os marcos da jornada passam a ser: "Virou Ultimate" → "Virou Mega" → "Venceu o Piedmon".
- O Mega não é exigido para vencer o chefe, mas a escala (vida 3000 contra 1500) faz dele o caminho natural.
- Os fatores dos NPCs novos (`CESC.fatorNpc`) são calibrados como os de hoje, com `experiments/calibrar_progressao.py`, para que todo pet bem treinado vença cada NPC do seu nível (a decisão de sempre).

## 6. Pets antigos, pesquisa e herança

- **Pets v1–v4:** o motor não muda; o replay e a assinatura ficam iguais. Dois caminhos para a **tela**:
  - **(A, recomendado):** os rótulos passam a seguir o cânone também para eles. Um furioso v4 aparece como "MetalGreymon · Furioso (Ultimate)", e o Meus pets avisa "pet de uma versão antiga: para no Ultimate".
  - **(B):** os pets antigos ficam com o rótulo de hoje ("WarGreymon, Mega").
- **Pesquisa (Python):** continua com 4 estágios. Os pets v5 existem só no jogo, como os gambits híbridos. As runs, os protocolos e os hashes não mudam. O desvio entre o jogo e o Python vai para o `REGISTRO_DESVIOS`. Levar o Mega para o Python só se uma pergunta de pesquisa pedir.
- **Herança:** cruzam Ultimate e Mega, como hoje ("só adultos cruzam" passa a ser "Ultimate ou Mega"). O ovo não herda o estágio.
- **Voz própria:** a honestidade da sombria (DESIGN_VOZ_PROPRIA, seção 9) não muda. A evolução para Mega entra como marco L.

## 7. As três cadeias frouxas

Três cadeias do mapa não são canônicas de ponta a ponta:
- Aquilamon → Silphymon → Valkyrimon;
- Ankylomon → Shakkoumon → SlashAngemon;
- Stingmon → DinoBeemon → Imperialdramon Fighter Mode.

O atlas não tem alternativas melhores para elas. Proponho mantê-las e revisar quando o corpus de personalidade auditado chegar (o outro chat do Matheus), porque ele cobre as linhas de evolução dos jogos de PS1 e WonderSwan.

## 8. Partes (um commit cada, depois da aprovação)

1. **Motor web:**
   - estágio `mega` e pets v5;
   - a condição da seção 3;
   - as constantes da seção 2;
   - o sprite pela linha;
   - os testes: os pets v1–v4 reproduzem bit a bit, e o v5 evolui, trava a sombria e o vínculo.
2. **Telas:**
   - Evolução (árvore com 5 níveis e a previsão do Mega);
   - Catálogo;
   - a revelação do Mega;
   - Meus pets;
   - os textos "Ultimate/Mega" separados;
   - as dicas do Professor Agumon.
3. **Campanha:** a Cidadela com o Myotismon, a Montanha Espiral e a calibração dos NPCs novos.
4. **Jornada:** os marcos novos, os e2e e o `CLAUDE.md`.

## 9. O que você precisa decidir

1. **A estrutura (seção 2):** 5 estágios, com a forma decidida pelo caráter no Ultimate e mantida no Mega. É a que não precisa de sprite novo. A alternativa é cada pet passar pelas duas formas da linha (Ultimate = forma "+", Mega = forma "−"). Ela perde a escolha pelo caráter e amarra o Mega às passivas "−" (o furioso não defende), por isso não recomendo.
2. **A condição do Mega (seção 3):** tempo + qualificação + vínculo ≥ 0,7. Com ela, a sombria nunca chega ao Mega.
3. **A campanha (seção 5):** o Piedmon vai para uma Montanha Espiral nova (Mega), e o Myotismon fica na Cidadela.
4. **Os pets antigos (seção 6):** rótulo canônico (A) ou o de hoje (B).
