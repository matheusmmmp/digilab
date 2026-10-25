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
