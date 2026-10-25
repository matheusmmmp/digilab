# TAREFA V2 — DIGIBRAIN_MODULAR_PROTOTIPO: o protótipo e a avaliação dos mecanismos do DigiBrain modular (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: a definir. Worktree e branch: `v2-modular-prototipo-<etapa>`. Status: **ABERTA, só papel.**
**A revisão da especificação pelo Matheus aconteceu em 2026-10-25** (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC.md`, seção 10): a direção
aprovada, as PE "antes" decididas. **Começa depois do #407 entrar na `main`,** pela etapa 0 (os gabaritos e a chave desligada), com o
`lembranca` autorizado para a v13 atrás da chave e com G2 antes; a v12 e o A preservados; nenhuma medição do A além da pontual de
desempenho.

Categoria: implementacao (com a avaliação como experimento). Origem: Matheus, 2026-10-24, o PROMPT MESTRE (seções 1, 6 e 9).

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | um cérebro modular mínimo que percebe, mantém estado, sente o corpo, propõe, escolhe e aprende nos cenários do MVP |
| o marco que desbloqueia | a integração no produto (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`) e a avaliação do fallback (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`) |
| a evidência | os testes de mecanismo por módulo; a ablação por módulo nos cenários do MVP; a comparação com o A como baseline, com plano de análise antes |
| as dependências reais | a especificação aprovada; o mundo do motor com o contrato (na `main`); os cenários do MVP (na `main` desde 2026-10-24, #401, #403 e #404: o pet v12, o layout do produto e o E2E-COMIDA) |
| se o gate falhar | o diagnóstico segue os critérios de `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, que separam a falha de implementação (conserta-se) da limitação da arquitetura (vai ao Matheus). **Nunca um gate novo só para validar o A** |

## 1. Pergunta

**A evidência que motiva esta tarefa agora** (registro MVP-ETAPA2, 2026-10-24): com o MVP na `main`, o cérebro A no v12 come 1 ou 2 vezes
por vida em 20 vidas de 2 dias, e numa delas não vai à ração posta a 2 células em 10 h (diagnóstico, não resultado). A cadeia do produto
funciona; o que falta é o cérebro ir à comida. A decisão do Matheus: o limite vem para cá, sem alterar o A.

O cérebro modular mínimo faz o que o MVP pede (perceber a comida, ir, comer e aprender com a consequência) por meio dos próprios módulos, e
cada módulo pesa como a especificação diz?

## 2. Depende de

- `docs/ESPEC_DIGIBRAIN_MODULAR.md` aprovado;
- as DM-1 a DM-9 (DECIDIDAS em 2026-10-25; a versão do pet modular é a **v13**, DM-5);
- os critérios de `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, escritos **antes** da avaliação.

## 3. Mudança mínima (PROPOSTA)

1. **Os módulos da DM-3,** num pacote próprio (por exemplo `digilab/digibrain/`, um arquivo por módulo). Eles cumprem o `Protocol`
   `Politica` e ficam atrás de uma chave, com o A e o `engine.py` intactos.
2. **Os testes de mecanismo** de cada módulo, com resposta conhecida.
3. **Os cenários do MVP na bancada:** a comida posta num lugar, o pet sozinho, o corpo químico, o mundo com o contrato.
4. **A avaliação,** com um plano de análise próprio commitado antes:
   - a ablação por módulo (desligar, congelar, embaralhar o sinal);
   - o A como baseline;
   - o custo por decisão.

## 4. Experimento e gate

- **O plano:** `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, commitado antes da primeira vida.
- **As sementes:** faixas novas, pedidas ao coordenador quando o plano existir.
- **Os gates** (PROPOSTOS, no plano):
  - **o G-MECANISMO:** cada módulo passa nos seus testes;
  - **o G-ABLA:** desligar cada módulo muda o comportamento no sentido que a especificação prevê;
  - **o G-MVP:** a cadeia comida → corpo acontece com o cérebro modular numa fração das vidas que o plano fixa;
  - **o G-CUSTO.**

## 5. Entrega

- Um PR por etapa: o código, os testes e a suíte inteira com a contagem.
- O plano antes da run.
- O `RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` depois.

## 6. Fora desta tarefa

- a web;
- a memória autobiográfica completa (tarefa própria; aqui só o M-MEM mínimo da DM-3);
- o genoma;
- dois pets.

## 7. Critérios de aceitação

- Os testes de mecanismo passam.
- O replay é bit a bit.
- Com a chave desligada, as vidas de hoje saem byte a byte.
- O plano foi commitado antes da run.
- O resultado está registrado como está, inclusive se for negativo.

## 8. Precisa do Matheus

As decisões que a especificação e o plano abrirem (as faixas, os limiares dos gates, o que entra no primeiro protótipo).

## 9. Etapa 0, os gabaritos, a chave e o esqueleto (worker D, 2026-10-25)

- **Os gabaritos primeiro (commit 0b9130d):** `tests/gabaritos/digibrain_vidas_de_hoje.json`, 196 vidas com a lista de candidatos de
  cada sub-decisão do mundo. É o G2 do `lembranca`. 184 vidas reusam os casos dos gabaritos da bancada no mundo (o J1 do P4, os dois pets,
  o plano do J5 e os sentidos), e a impressão de cada uma é conferida contra a fonte. As outras 12 ligam o Olfato da comida. O v12 no
  layout do produto e o A no layout padrão ficam pelos gabaritos do MVP (#403), que já têm os candidatos.
- **A chave:** `ConfigDigibrain` em `digilab/config.py`, desligada, PROPOSTA, com as subchaves `modula_g_apr` (desligada, PE-4), `p2`,
  `m_mem` e `persistencia`. Nada fora do pacote a lê, e um teste confere.
- **O esqueleto:** `digilab/digibrain/`. O M-ADAPT (`adapt.py`) cumpre o `Politica`, com as falhas altas da seção 4.1. Os módulos (sens,
  afeto, estado, impulso, mem, arb, plast e os ganchos vazios) levantam NotImplementedError. Nenhuma equação.
- **Os gates:** o G2, o G-INT e a G-RECEPTOR pela AST, e o `engine.py` intacto, em `tests/test_digibrain_etapa0.py` e
  `tests/test_gabarito_digibrain.py`.
- **Fica para a etapa do `lembranca`:** o G2 das vidas v12 do jogo, no TS, antes da mudança TS; e o alvo `ponto` que o motor já aceita
  no explorar (o achado do registro).
- **Interpretações e achados** em `docs/registro/2026-10.md`.

## 10. A PE-14 revista e o que a etapa 1 precisa antes de rodar (Gerente, 2026-10-25)

**A decisão do Matheus, depois do achado da etapa 0:** adotar o `Alvo.ponto` já aceito pelo motor Python. O lugar lembrado é um alvo
produzido pelo M-MEM, não um candidato fornecido pelo explorar do motor. A validação especial aceita `ponto` só em EXPLORAR, com
coordenadas inteiras dentro do mapa; a validação dos demais alvos não relaxa. Antes de qualquer alteração no espelho TS, o gabarito das
vidas v12 em TS, gravado e conferido contra a versão atual. A v12 e o A preservados. A espec registra a revisão nas seções 4.1, 11 e 15,
com os testes T-PONTO-1 a T-PONTO-4.

**Antes da primeira vida do cérebro modular,** nesta ordem:
1. a espec atualizada (feito: #409 e este PR);
2. a linha da arquitetura sobre Hebb e os traços corrigida (feito: este PR);
3. o plano de análise `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` commitado, com as faixas de sementes pedidas ao coordenador,
   os gates G-MECANISMO, G-ABLA, G-MVP e G-CUSTO com os limiares PROPOSTOS, a leitura descritiva de Lengyel e Dayan (D-2) e a leitura
   secundária da PE-4 (D-1); **o plano vai ao Matheus antes da primeira vida.**

## 11. O plano de análise (o C, Claude Code, Opus 5.5, 2026-10-25)

- **Entregue:** `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` (#412).
- **Revisto pelo Matheus em 2026-10-25** (por relato do Gerente): as PPM-1 a PPM-7 e a PPM-9 aprovadas pelas recomendações; a PPM-8
  depois da correção do poder; os AF-1 a AF-6 decididos (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 8). As quatro correções pedidas
  estão na versão corrigida: o poder a 0,0125 por contraste, a regra do Holm pelo p do bootstrap, a ordem dos gates em dois trilhos (o
  TS não bloqueia o Python) e o G-MVP como condição necessária, não suficiente, do produto pronto. **Sem vidas e sem merge até o Matheus
  revisar a versão corrigida.**
- **As faixas** 63101…63505 (a calibração e o piloto) e 64101…64505 (a avaliação única), reservadas pelo Gerente e aprovadas pelo Matheus
  (PPM-1), estão em `experiments/bancada/faixas.py`.
- **O que o plano pressupõe da etapa 1a,** além dos módulos: uma subchave `p1` e o modo do `g_apr` na `ConfigDigibrain`, e o orquestrador
  na lista do teste do layout do MVP (PPM-3).
- **Interpretações e achados** em `docs/registro/2026-10.md`.

## 12. Etapa 1b, o trilho TS: o gabarito v12, o `ponto` no laço e o custo do A (worker A, 2026-10-25)

- **O gabarito das vidas v12 do jogo em TS primeiro, num commit próprio (36eb1bc), antes de qualquer mudança no espelho:**
  - `web/app/test/gabaritos/v12_jogo_ts.json`, de `web/app/test/v12_jogo_ts.test.ts`: cinco vidas do pet v12 como o jogo as roda (o
    `Motor`, o mundo do produto `CMU_MVP` e o A v11), de 3 e 4 dias, com quatro donos (o botão Alimentar, a ração perto do pet, os três
    lugares nomeados da tela e um roteiro com tapa, treino, medalha e lutas);
  - em cada vida: o log, a assinatura a cada 25 eventos e no fim, os candidatos e o alvo de cada sub-decisão do mundo (o sha256 da lista
    e as contagens por ação e por tipo de candidato no explorar, como no `tests/gabaritos/digibrain_vidas_de_hoje.json`), a impressão do
    mundo e o estado do cérebro no fim;
  - **o TS de antes da mudança o reproduz byte a byte** (8 testes, no próprio commit).
- **O `ponto` no espelho TS (6060a31):**
  - **achado:** o `Mundo` do TS já validava o `ponto` como o Python (`web/app/motor/mundo.ts`, `validarAlvo`): só em EXPLORAR, sem id e
    sem `de`, inteiro e dentro do mapa, senão o mesmo erro, e os outros alvos sem relaxar. O que faltava era o laço do jogo perguntar o
    alvo ao cérebro, como o `escolher_alvo` do Python: o `MotorCorpoMundo` passava sempre `null`;
  - **o que mudou:** a política ganhou o gancho opcional `escolherAlvo` (`motor/motor_corpo.ts`), e o laço só o pergunta com a chave
    `digibrain` (`OpcoesLacoMundo`, desligada; a v13). A validação do `Mundo` não mudou e não ganhou chave: é a do Python, que também não
    tem. O explorar não ganhou candidato;
  - **os testes** (`web/app/test/ponto_v13.test.ts`): desligada, o gancho nunca é chamado e a vida sai igual; ligada, o `ponto` entra só
    no explorar e se refaz pelo log; fora do mapa ou não inteiro, erro; no comer, no brincar, com id ou `de`, ou um candidato com a
    posição mudada, erro.
- **A medição pontual do A v11 no navegador (3e47a0a), só desempenho, uma vez:**
  - `web/app/test/custo_a_v11_navegador.json`, de `web/app/test/medir_custo_a.mjs`;
  - o pet v12 do jogo no Chrome 155 instalado, sem janela, com isolamento de origem, num i7-14700KF com Windows 11. Medianas de 7
    repetições de uma vida de 14 dias (1 344 decisões):
    - **37,19 µs** por decisão inteira (o motor, o mundo, o corpo e o cérebro);
    - **5,65 µs** dentro do cérebro A;
    - **49,47 ms** para refazer os 14 dias pelo log;
  - o log tem 23 759 bytes em JSON;
  - é a referência do orçamento: o cérebro da v13 até 2 × 5,65 µs, e o replay de 14 dias da v13 até 1,5 × o da v12, no mesmo aparelho e
    no mesmo navegador.
- **Os testes:**
  - `npm run tipos` sem erro;
  - `npm test` com 52 arquivos e 612 testes, dos quais 12 são novos (8 do gabarito v12 e 4 do `ponto`);
  - `npm run e2e` com 91 de 91;
  - `python tools/conferir_saude.py` passa.
- **Fica para depois, pela ordem do plano:** o porte dos módulos do cérebro para TS e o G-PAR, depois da 1a do D na `main` e dos
  gabaritos Python dela; a medição da v13.
- **Interpretações e achados** em `docs/registro/2026-10.md` (DIGIBRAIN-MODULAR-PROTOTIPO, etapa 1b).
