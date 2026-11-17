# TAREFA V3 — PALAVRA_DONO (2026-11-17)

Coordenador: a Gerente das cinco frentes (Claude Code). Worker da PD0: Claude Code, Opus 5.5, worktree `v3-palavra-dono`. Status: **ABERTA;
PD0 (só papel) ENTREGUE.** D-PD-1 a D-PD-4 DECIDIDAS pelo Matheus em 2026-11-17, no chat da sessão F4, pela recomendação. D-PD-5 a D-PD-9
pendentes. Nenhum código, nenhuma faixa e nenhuma vida.

Categoria: arquitetura (depois, implementacao e experimento). Origem: Claude Code, 2026-11-17: a frente F4 das cinco frentes da síntese de
2026-11-16 (o PacaPet), "o dono inventa uma palavra e o pet aprende". A Gerente abriu a frente pelo prompt do vault,
`30 Decisões e protocolo/PROMPT_CINCO_FRENTES_2026-11-16.md`.

## 1. Pergunta

Uma palavra livre do dono pode virar, pela rede do pet (o hábito H do M-PLAST com o r do corpo) e não por uma tabela de contagem, uma
ligação palavra → comportamento que separa o dono coerente do inconsistente? Não vem de uma hipótese do `PLANO_V2_PESQUISA`: é mecânica nova
de interação. A espec é a [`ESPEC_V3_PALAVRA_DONO.md`](ESPEC_V3_PALAVRA_DONO.md).

## 2. Depende de

- **As decisões D-PD-1 a D-PD-4** (DECIDIDAS, seção 2 da espec).
- **Para a PD1, o código Python:** a LZ2a da LIMPEZA (o modular na base nova) e a etapa 2 do [`TAREFA_V3_ELOGIO.md`](TAREFA_V3_ELOGIO.md)
  (o crédito do carinho pelo corpo, a rota única do elogio até a palavra).
- **Para a PD3, a vista:** a IT3 (o arco do pet) e o painel de hábitos (WD-1) do [`PLANO_V3_INTERACAO.md`](PLANO_V3_INTERACAO.md).
- **Da F3:** nenhuma decisão. A palavra não é impulso. Se a F3 criar um predicado de "urgência crítica", a porta do 3.4 o lê (combinado por
  nota em 2026-11-17).

## 3. Mudança mínima

**Neste PR (a PD0), só papel:**
- a espec;
- a prancha em `docs/pranchas/ux-palavra-dono/`;
- esta tarefa;
- a seção no registro do mês.

Nada muda no código, no motor, no `engine.py` nem nos pets. A mudança das etapas seguintes está na seção 3.10 da espec.

## 4. Experimento e gate (se houver run)

- **Plano de análise:** `docs/PLANO_ANALISE_V3_PALAVRA_DONO.md`, commitado antes da run (PD2).
- **Sementes reservadas:** a pedir ao coordenador na PD2.
- **Métrica e gate:** o T-PALAVRA (seção 6 da espec). A H1 é `Δ_brincar(C) − Δ_brincar(I) > 0` pela sonda contrafactual, fora do contexto
  de ensino, com o IC 95 % por bootstrap acima de 0.
- **GPU:** não.

## 5. Entrega

- **Testes:** nenhum nesta etapa (só documentos). O CI confere os links (`tools/verificar_relato.py`, categoria arquitetura).
- **Registro:** a seção de 2026-11-17 no fim de `docs/registro/2026-11.md`.
- **PR** contra a `main`, com o relato. Merge só pelo Matheus.

## 6. Fora desta tarefa

- Todo código.
- A voz (PD4).
- O alvo da palavra (PD5, se a D-PD-6 abrir).
- A fala citar a palavra.
- O esquecimento (a PE-10 do modular).
- A calibração de qualquer número.

## 7. Critérios de aceitação

- A espec existe, com D-PD-1 a D-PD-4 e a resposta literal do Matheus.
- A prancha existe e é gerada pelo `gerar.py`, com as capturas nas duas peles, 1920×950 e 390×844, em `capturas/`.
- O teste falsificável está escrito antes, com braço de controle (seção 6 da espec).
- Os links relativos resolvem.

## 8. Precisa do Matheus

D-PD-5 a D-PD-9, na seção 8 da espec, cada uma com a recomendação e o custo de errar:
- **D-PD-5:** a prancha;
- **D-PD-6:** só o comportamento primeiro;
- **D-PD-7:** 4 vagas, sem esquecer;
- **D-PD-8:** a espec e o T-PALAVRA;
- **D-PD-9:** se a H1 cair, a palavra fica fora do jogo.

## 9. Resumo da PD0 (2026-11-17)

- **Os conflitos foram levados ao Matheus antes de qualquer desenho**, com aviso no celular. Os três do prompt (o sinal, a DC5 e a origem),
  mais um que a sessão achou: a EN-4 põe o pedido só no TS, e a regra comum põe mecânica nova no Python. Ele decidiu os quatro pela
  recomendação.
- **A espec** liga a palavra pela P2 sem mudança: uma característica nova de z (`pal_k`, com 4 vagas), com o inato 0, a porta do corpo
  acima de λ e o evento `pl` no registro. Ela mostra por que a tabela de contagem do PacaPet não basta (a seção 3.7).
- **A prancha** tem cinco telas: o Dizer… no arco, o balão do dono (com o caso do corpo que vence), o cartão "liga" e a seção Palavras no
  painel de hábitos. As capturas estão nas peles Vidro e Militar.
- **O teste:** C × I × S pela sonda contrafactual, sem rng nova.
