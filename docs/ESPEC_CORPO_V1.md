# ESPEC — CORPO V1: o teto baixo num pet do jogo (C5, 2026-11-20, Claude Code, Fable 5.2)

**Status: PROPOSTA, com a D-EC-1 DECIDIDA** (Matheus, 2026-11-20: "Medir no v38 antes"). Nada aqui está implementado. As outras decisões são do Matheus (seção 8). A síntese que sustenta esta
especificação é a [SINTESE_CORPO.md](SINTESE_CORPO.md); as fontes e os sha256 estão na seção 0 dela.

**A primeira mudança:** um pet do jogo que nasce com o DTB, isto é, com a ponte da falta de combustível na fome e o teto em C/2. Os pets
que já existem não mudam.

**Por que ela não é só "ligar a chave":** a C4 validou o DTB no pet da bancada, que não tem o "sono que segura", o lance do dono nem o
equilíbrio do cuidado (`docs/SINTESE_CORPO.md`, seção 8). O pet v38 do jogo tem os três, e dois deles mexem no que o DTB muda: o sono e
a fome urgente. Por isso a mudança tem três etapas, e a primeira é uma medida.

## 1. A mudança, em uma tabela

| | o pet de hoje (v38, e o grupo v39) | o pet da V1 |
|---|---|---|
| a falta de combustível (abaixo de C/4) | sobe o cansaço em 500 por tick | sobe a fome em até 500 por tick, só até a fome chegar a T_B |
| acima de T_B | não se aplica | a falta não sobe a fome nem o cansaço; a fome sobe só pelo relógio dela (+375 por tick) |
| o resto do corpo | como hoje | igual: o reflexo do sono, a digestão, o metabolismo e o dano da privação não mudam |
| o cérebro | como hoje | igual: nenhuma mudança no modular |

- **T_B = 225 000** (C/2). PROPOSTO e SEM FONTE (D-EC-3).
- **Os 500 por tick** são o `falta_fome` da `ConfigAcoplamentoCorpo`, PROPOSTO e SEM FONTE (o mesmo 500 do `falta_cansaco` de hoje).
- **As duas chaves já existem,** desligadas, no Python e no TS, com paridade (#995 e #1024). A V1 não cria mecânica nova no corpo.

## 2. As etapas

Cada etapa é um PR. Uma etapa só começa com a anterior aceita pelo Matheus.

| etapa | o quê | tipo | muda algum pet do jogo? |
|---|---|---|---|
| **V1-a** | a conferência no pet do jogo: o v38 de hoje contra o v38 com o DTB, no Python | uma run, com plano próprio | não |
| **V1-b** | a versão nova do pet, no Python e no TS, com a paridade | código, sem run | não: nenhum ovo choca com ela |
| **V1-c** | os ovos novos passam a nascer com a versão nova | uma linha e os testes | sim, só os ovos novos |

**A ordem é V1-a, V1-b, V1-c** (D-EC-1). A V1-a vem antes do código do jogo porque não precisa dele, e porque um "não confirma" nela
poupa a V1-b.

## 3. V1-a, a conferência no pet do jogo

**A pergunta:** no pet v38, o DTB ainda faz o pet passar mais tempo bem, sem reprovar as guardas?

**O que já existe e é reusado:**
- o pet v38 no Python: `experiments/pv2.py`, `fabricas(..., v38=True)` (o `inatos_e1()`, a `CONFIG_SONO_SEGURA_LIGADA`, a
  `CONFIG_LANCE_DONO_LIGADA` e a `EQUILIBRIO_V38`). É o pet que a PET_VIVO usou na checagem do v38;
- as duas chaves do corpo, pelos argumentos do motor: `cfg_acoplamento_corpo=CONFIG_ACOPLAMENTO_CORPO_LIGADA` e
  `cfg_teto_fome_corpo=CONFIG_TETO_FOME_BAIXO` (`digilab/motor_corpo.py`);
- as medidas e a análise da C4: `experiments/run_v3_corpo_c4.py` (a primária, as guardas, a saúde por célula, as premissas, a leitura).

**O que a etapa escreve:**
- **o plano,** `docs/PLANO_ANALISE_V3_CORPO_V1.md`, commitado e aprovado antes da primeira vida, com a seção `PR-CORPO-V1` no
  `docs/PREREGISTRO.md`. O plano traz os quatro itens do planejamento de 2026-11-19 (as vidas gravadas, a contagem dos eventos com
  piso, a precisão calculada antes, o corpo e os donos distintos);
- **o orquestrador,** `experiments/run_v3_corpo_v1.py`: um arquivo próprio, para o da C4 ficar intacto. Ele monta o pet v38 e passa as
  chaves do braço ao motor;
- **a faixa** de sementes, pedida ao coordenador.

**O desenho que o plano deve seguir** (os números ficam PROPOSTOS no plano, não aqui):
- **os braços:** CTRL38 (o pet v38 de hoje) e DTB38 (o v38 com as duas chaves);
- **as células:** as 12 da C4 (4 donos × comedouro, longe e `longe_fixo`), lidas também nas 11 distintas;
- **a regra de leitura:** a da seção 6 do plano da C4, sem mudar: a primária é o "Tempo bem" (D-MP-1), as guardas são a saúde, a taxa
  por episódio, o "Tempo bem" por lugar e o S2, e a saúde por célula entra como ressalva;
- **o que é novo no descritivo:** a fração dos ticks dormindo e a duração dos sonos (o "sono que segura" faz o pet dormir até
  recuperar), e as medidas da rodada do cuidado que dependem da fome e do sono. O plano diz quais, a partir do
  `docs/PLANO_V3_EQUILIBRIO_CUIDADO.md`;
- **o bloco dos pares:** o plano decide se entra. Os pares da C4 usam o pet de hoje da SOCIAL_PAR A0 (o modular com a CO7), e o S2
  passou. Esse pet também não tem o "sono que segura" nem o equilíbrio do cuidado.

**O que ela não faz:** não muda o `digilab/`, não muda o web, não liga nada no jogo.

## 4. V1-b, a versão nova do pet

**O que muda no TS** (`web/app/motor/`):

```ts
// constantes.ts
export const VERSAO_Vxx = xx;   // o v38 com o DTB (um pet)
export const VERSAO_Vyy = yy;   // o v39 com o DTB (o grupo)
/** a versao nasce com o teto baixo (CORPO V1): a ponte da falta na fome, com o teto em C/2 */
export const nasceComTetoFome = (versao: number): boolean => versao === VERSAO_Vxx || versao === VERSAO_Vyy;
// VERSOES_PET ganha xx e yy; VERSAO_PET e VERSAO_GRUPO NAO mudam nesta etapa
```

```ts
// motor_corpo.ts e motor_corpo_mundo.ts: o construtor recebe as duas chaves e as passa ao corpo
this.corpo = Corpo.deEstado(estado, { cc, comMundo, tela, enjoo, acoplamento, tetoFome });
// sem as duas (o padrao), o objeto de opcoes e o de hoje, e o corpo sai byte a byte
```

```ts
// motor.ts: onde a versao vira as opcoes do corpo
const comTeto = nasceComTetoFome(versao);
const acoplamento = comTeto ? CONFIG_ACOPLAMENTO_CORPO_LIGADA : undefined;
const tetoFome = comTeto ? CONFIG_TETO_FOME_BAIXO : undefined;
```

- **xx e yy** são os dois números de versão livres na hora do PR (hoje a lista termina em 39). Cada versão nova herda todos os
  `nasceCom…` da versão de que parte (a v38 e a v39).
- **O corpo não muda:** `web/app/motor/corpo.ts` já tem `opcoes.acoplamento` e `opcoes.tetoFome`, e a regra da ponte com teto.

**O que muda no Python:**
- **nada no `digilab/`.** As chaves existem;
- **o exportador do gabarito,** `experiments/exportar_gabarito_corpo_v1.py`: uma vida inteira do pet da versão nova (o pet v38 do
  `pv2.fabricas(v38=True)` com as duas chaves), gravada em `tests/gabaritos/` e copiada para `web/app/test/gabaritos/`, como nas
  versões anteriores.

**A regra da ponte, para referência** (já implementada, `digilab/corpo.py`, a fase 2 do tick):

```
a cada tick, se combustivel < C/4:
    se o pet nasce com o teto:
        soma = min(500, max(0, T_B - fome))     # T_B = 225 000
        fome += soma                            # acima de T_B, soma = 0
    senao:
        cansaco += 500                          # o corpo de hoje
```

**O que não muda na tela:** nenhum nome, nenhum menu, nenhuma barra. O pet da versão nova mostra a mesma tela Pet.

## 5. V1-c, os ovos novos

```ts
// constantes.ts
export const VERSAO_PET = VERSAO_Vxx;       // era 38
export const VERSAO_GRUPO = VERSAO_Vyy;     // era VERSAO_V39
```

- **Só os ovos chocados depois** nascem com a V1. Os pets v38 e v39 que já existem seguem como estão, e o replay do save deles não muda.
- **A escolha em Ajustes** (o cérebro A v11 e o modular) não muda.
- **O T_B passa a DECIDIDO** nesta etapa, se o Matheus decidir (D-EC-3): o status em `PARAMETROS_TETO_FOME_CORPO` muda junto.

## 6. Os testes

| etapa | teste | o que confere |
|---|---|---|
| V1-a | `tests/test_run_v3_corpo_v1.py` | a regra de leitura caso a caso (a tabela da C4), as premissas, a trava do plano APROVADO, o pacote, e a fumaça duas vezes com o `medidas.json` igual byte a byte |
| V1-a | o mesmo | o braço CTRL38 refaz, byte a byte, uma vida do pet v38 de hoje (o log da vida, pelo sha256) |
| V1-b | `web/app/test/corpo_v1.test.ts` | a vida inteira da versão nova sai igual ao gabarito do Python, inteiro a inteiro |
| V1-b | os gabaritos das versões 21 a 39 | nenhum muda: "desligada, a vida de hoje sai byte a byte" |
| V1-b | `web/app/test/corpo_teto.test.ts` e `corpo_acoplamento.test.ts` | continuam passando sem mudança |
| V1-b | um teste de versão | `nasceComTetoFome` só vale para xx e yy; um save v38 reaberto continua v38 e refaz o mesmo estado pelo log |
| V1-c | os testes de ovo e de jornada | o ovo novo choca a versão xx (o grupo, a yy); um save antigo não muda de versão |
| todas | `npm test`, `npm run tipos`, `npm run e2e` (V1-b e V1-c); `python -m pytest` dos testes da frente | passam |

## 7. Os critérios de aceitação

**V1-a:**
- o plano está APROVADO e na `main` antes da primeira vida, com a faixa reservada e a seção no pré-registro;
- a run roda uma vez; o resultado tem o IC95 e a leitura pela regra escrita antes; os artefatos têm sha256;
- **"confirma"** ou **"confirma com ressalva"** (com a célula nomeada e aceita pelo Matheus) libera a V1-b;
- **"não confirma"** ou **"indeterminado"** fica registrado, a V1 para, e o pet do jogo fica como está.

**V1-b:**
- a vida da versão nova no TS sai igual ao gabarito do Python;
- nenhum gabarito das versões anteriores muda, e nenhum ovo choca com a versão nova;
- o `engine.py` não muda (o sha256 dele confere).

**V1-c:**
- só entra com a decisão do Matheus, depois da V1-a e da V1-b;
- os saves que já existem abrem e refazem o mesmo estado.

## 8. As decisões do Matheus

- **D-EC-1 (DECIDIDA pelo Matheus em 2026-11-20: "Medir no v38 antes", a opção 1), o caminho até o jogo.**
  1. **Medir antes no pet do jogo (recomendada):** V1-a, depois V1-b, depois V1-c.
  2. **Ligar direto:** só V1-b e V1-c, com a C4 como a evidência.
  3. **Não levar ao jogo agora:** o DTB fica como chave de pesquisa.
  - **Por que a 1:** a C4 mediu o pet da bancada. O "sono que segura" e o equilíbrio do cuidado mexem no sono e na fome urgente, que
    são o que o DTB muda. A V1-a custa uma run do tamanho da C4 (1 h 19 min).
  - **O custo de errar:** com a 2, os ovos novos podem nascer com um corpo que, no pet v38, não melhora ou piora. Com a 1, se a V1-a
    não confirmar, a V1 para depois de uma run. Com a 3, o pet do jogo segue com a exaustão e a privação que o DTB reduziu na bancada.
- **D-EC-2 (PROPOSTA), a ressalva no jogo.** O aleatório no comedouro perde saúde com o DTB (−0,049). A ressalva foi aceita para seguir
  à C5. Falta dizer se ela é aceita também para os ovos novos.
  - **A recomendação:** decidir depois da V1-a, com o número dessa célula no pet v38.
  - **O custo de errar:** decidir agora é decidir com o número do pet da bancada.
- **D-EC-3 (PROPOSTA), o T_B.** Passa de PROPOSTO a DECIDIDO?
  - **A recomendação:** só na V1-c, se a V1-a confirmar. Até lá continua PROPOSTO e SEM FONTE.
  - **O custo de errar:** decidir agora fixa um número que só foi medido contra outro (o limiar), no pet da bancada.
- **D-EC-4 (PROPOSTA), a baseline trivial.** A comparação da A1 (o modular contra a TRIV) não foi refeita com o DTB.
  - **A recomendação:** não refazer dentro da V1. Ela responde outra pergunta (o cérebro contra a baseline), e a primária de hoje é o
    "Tempo bem", em que a TRIV vive em privação. Se o Matheus quiser o número, é uma run à parte, com plano próprio.
  - **O custo de errar:** sem ela, o veredito da A1 ("a baseline vence no forrageio") fica como está, sem resposta com o corpo novo.
- **D-EC-5 (PROPOSTA), os números de versão.** A V1-b pega os dois números livres na hora do PR (hoje, 40 e 41).
  - **A recomendação:** pedir os números ao coordenador antes do PR, como as faixas de sementes.
  - **O custo de errar:** dois PRs de frentes diferentes com o mesmo número de versão.

## 9. Como a SOCIAL_PAR se beneficia

**O que a SOCIAL_PAR achou no pet de hoje** (`docs/OBSERVACAO_V3_SOCIAL_PAR.md`; o artefato
`artifacts_v3_social_par_s/s0/observacao.json`, sha256 `676a5ba758aa1201687dafba35a7deb187cf056dd4a05336e39ae44beebc8508`):
- **o bloqueio B3, o sono:** os dois pets dormem 45 % da vida cada um, e "o sono reduz as decisões em que algo pode acontecer". A fase
  S deixou esse bloqueio de fora.

**O que o DTB dá ao substrato** (`docs/SINTESE_CORPO.md`, seção 5):
- **menos sono:** a fração dos ticks dormindo vai de 0,465 para 0,377;
- **o reencontro mais cedo:** −3,30 decisões [−4,31; −2,29] nos pares, sem mecanismo social nenhum;
- **mais "brincar":** de 26,7 para 46,1 escolhas por vida.

**O que isso é e o que não é:**
- **É** mais tempo acordado em que os dois pets podem agir um sobre o outro. É o que o B3 pedia.
- **Não é** um efeito social medido. Nenhuma run pôs um mecanismo social (o M1 e o M2 da SOCIAL_PAR) sobre o DTB.
- **O que fica para a frente do social:** se o corpo da V1 entra como um fator nas runs dela. É uma decisão da SOCIAL_PAR e do Matheus,
  fora desta especificação. Os pares da C4 ficam versionados (`artifacts_v3_corpo/c4/pares.tar.gz`) para quem quiser olhar.

## 10. Fora desta especificação

- **Outro teto** além de C/2, a ponte dividida e o transbordo.
- **A opção E** (a digestão inteira) e **a C5 do mapa** (o reflexo suave): medidas sobre a D na ablação, as duas saíram em "perda".
- **Qualquer mecanismo social.**
- **A tela:** nenhum indicador novo do corpo.
- **Os pets que já existem:** nenhuma migração de save.
