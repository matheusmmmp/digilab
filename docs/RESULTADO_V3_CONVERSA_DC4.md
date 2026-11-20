# RESULTADO V3 — CONVERSA_PET, DC4: a voz da rede com modelo de verdade, encerrada antes dos gates (2026-11-10, worker, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_CONVERSA_DC4.md](PLANO_ANALISE_V3_CONVERSA_DC4.md), APROVADO em 2026-11-08.

> **Aviso:** a **voz-v3, a do jogo, continua não validada.** A DC4 validou a voz-v3b no laboratório e foi encerrada antes dos gates. Nada
> aqui diz que a voz do jogo é fiel, legível ou resistente à injeção.

**O encerramento (D-DC4D-2):** o Matheus encerrou a DC4 em 2026-11-10 ("Sim, encerrar") com a legibilidade e os pares marcados, e sem a
referência nem a injeção. O motivo, nas palavras dele: "Não faz sentido eu analisar o DC4 se é nem isso que vai no jogo. Eu tenho que
analisar o DC5." A voz-v3b não vai para o jogo, e a DC5 muda a voz e a escolha dos conceitos.

- **Nenhum gate foi calculado como passa ou falha.** O G-FIEL, o G-VERIF e o G-INJ ficam **não medidos**. A legibilidade e os pares abaixo são
  só descritivos: não se comparam com o limiar do G-LEGIVEL, e a regra de leitura da seção 5 não se aplica.
- **O marcador Opus** da referência (as 486 falas, cego ao braço) fica guardado em `respostas/opus_referencia.jsonl` e `opus_motivos.jsonl` e
  não é usado aqui. A comparação dele com o Matheus (o kappa da 4.1) vai para a DC5.

## 1. O que rodou

- **A validação, uma vez** (DC4c, PR #750): 486 falas, 162 por braço, na subfaixa 20262500–20262899, com a voz-v3b no `dec-v3` e a voz-v2 no
  `dec-v2`. Os artefatos estão em `artifacts_v3_conversa_dc4/validacao/`. Ela rodou inteira na sexta tentativa; as cinco quedas estão no
  D-DC4C-1.
- **Os braços:** G `gemma2:9b` (local), H `claude-haiku-5-5` e S `claude-sonnet-5-5` (API).
- **O gasto** (`validacao/meta.json`, `gasto`): US$ 1,18 na rodada da validação; **US$ 2,08 acumulados na DC4**, dentro do teto de 3,00.

## 2. O que foi marcado

| tarefa (plano) | marcado | quem |
|---|---|---|
| legibilidade (4.2) | 180 de 180 | o Matheus, cego ao braço |
| pares (4.5) | 24 de 24 | o Matheus, cego ao braço e com os lados sorteados |
| amostra da referência (4.1) | 0 de 48 | — |
| injeção (4.4) | 0 de 36 | — |

As respostas estão em `artifacts_v3_conversa_dc4/validacao/marcacao/respostas/`. Os números abaixo saem do `resumo_marcacao.json` da mesma
pasta, gerado por `python experiments/resumo_marcacao_dc4.py --pasta artifacts_v3_conversa_dc4/validacao/marcacao`, que só lê o
`itens.json`, o `chave.json` e as respostas do Matheus.

## 3. A legibilidade (4.2, descritivo)

O Matheus leu cada fala espontânea do E3 sem o braço e escolheu o pedido entre comida, limpeza, companhia ou "não pede nada". O plano não
fixa um intervalo para esta medida, e nenhum vai aqui.

| braço | acertos | o acerto | "não pede nada" |
|---|---|---|---|
| G `gemma2:9b` | 44 de 60 | 0,733 | 14 de 60 (0,233) |
| H `claude-haiku-5-5` | 59 de 60 | 0,983 | 0 |
| S `claude-sonnet-5-5` | 56 de 60 | 0,933 | 0 |

- **A matriz do pedido da rede pela resposta** (20 falas por pedido em cada braço):

| braço | pedido da rede | comida | limpeza | companhia | nada |
|---|---|---|---|---|---|
| G | fome | 15 | 0 | 0 | 5 |
| G | higiene | 1 | 17 | 0 | 2 |
| G | solidão | 1 | 0 | 12 | 7 |
| H | fome | 20 | 0 | 0 | 0 |
| H | higiene | 0 | 19 | 1 | 0 |
| H | solidão | 0 | 0 | 20 | 0 |
| S | fome | 19 | 1 | 0 | 0 |
| S | higiene | 0 | 17 | 3 | 0 |
| S | solidão | 0 | 0 | 20 | 0 |

- Os erros do G são quase todos "não pede nada" (14 dos 16). Os do H e do S trocam um pedido pelo outro.

## 4. A preferência nos pares (4.5, descritivo)

A pergunta fixa: "Com qual pet parece que você está conversando de verdade?" (escolha forçada), em duas conversas inteiras do mesmo roteiro e
das mesmas entradas, lado a lado. O plano não fixa um intervalo nem um teste para esta medida.

| comparação | escolhido | o lado esquerdo escolhido |
|---|---|---|
| H × G | H em 11 de 12, G em 1 | 9 de 12 |
| S × G | S em 10 de 12, G em 2 | 6 de 12 |

## 5. O que não foi medido

- **O G-FIEL (4.1)** e **o G-VERIF (4.3)** dependem da referência, e a amostra de 48 do Matheus não foi marcada. Sem ela, o plano não
  aceita o marcador Opus como referência, porque o kappa não existe.
- **O G-INJ (4.4)** depende da marcação dos 36 turnos de injeção, e ela não foi feita.
- **O descritivo da reação ao dono (4.5)** é marcado na amostra da 4.1 e também não existe.
- O custo real, a latência e as falas genéricas da 4.5 já estão no relato da DC4c (PR #750) e não se repetem aqui.

## 6. Os desvios

`docs/registro/2026-11.md`, "CONVERSA_PET, DC4d":
- **D-DC4D-1:** as contagens e as leituras do marcador Opus chegaram ao Matheus antes da amostra dele. Ele declarou "Não li". Com o
  encerramento, o kappa não é calculado.
- **D-DC4D-2:** o encerramento por decisão do Matheus, com os gates não medidos.
