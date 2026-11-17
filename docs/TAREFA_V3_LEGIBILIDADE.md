# TAREFA V3 — LEGIBILIDADE (2026-11-17)

Coordenador: Matheus, nesta sessão. Worker: Claude Code (Opus 5.5). Worktree e branch: `v3-sucesso-legibilidade`. Status: ABERTA.

Categoria: arquitetura. Origem: Matheus, 2026-11-17. Depois da rodada de literatura Dreyfus, o Matheus aprovou a recomendação: mapear quem define o sucesso no DigiBrain (Dreyfus 2002, p. 376) e planejar um teste cego de legibilidade com as vidas da ablação da A2 (Collins 1996, o erro sociológico).

## 1. Pergunta

São duas perguntas:
- **(a) De onde vem cada sinal que faz o pet aprender?** Do corpo, do dono, do mundo ou de uma regra nossa (Dreyfus 2002, p. 376)?
- **(b) O efeito do aprendizado que a ablação da A2 mediu ("muda") aparece para quem olha o pet?** Ou o dono completa o resto ao
  interpretar o comportamento (Collins 1996, pp. 106-108)?

As duas vêm da rodada de literatura `docs/referencias/V3_SINTESE_DREYFUS.md` (PR #954), não de uma hipótese do `PLANO_V2_PESQUISA.md`.

## 2. Depende de

- **A auditoria (a):** nada. Ela lê o código da `main` (136e6088).
- **O plano (b):**
  - depende da A2 (PR #952, ainda aberto): as vidas do teste são as da run da ablação, refeitas pelo SHA dela;
  - depende das decisões LG-1 a LG-6 do Matheus (seção 8);
  - nada roda antes da aprovação.

## 3. Mudança mínima

- **Novo:** `docs/AUDITORIA_V3_SUCESSO_CORPO.md`, a tabela dos sinais de aprendizado, com o arquivo e a linha de cada um.
- **Novo:** `docs/PLANO_ANALISE_V3_LEGIBILIDADE.md`, o plano do teste cego, com status PROPOSTO e sem a linha de trava.
- **Alterado:** `docs/registro/2026-11.md`, com uma seção própria.
- **O que não muda:** nenhum código (`digilab/`, `experiments/`, `web/app/`), nenhuma config e nenhuma faixa de sementes.

## 4. Experimento e gate (se houver run)

- **Plano de análise:** `docs/PLANO_ANALISE_V3_LEGIBILIDADE.md`, commitado antes de qualquer coleta. Esta tarefa só escreve o plano.
- **Sementes:** nenhuma faixa nova. Os estímulos são vidas já rodadas na A2 (98101…98300), refeitas de forma determinística. A seleção
  dos pares usa uma rng própria, com a semente escrita no plano.
- **Métrica e gate:** a taxa de acerto no teste de escolha forçada entre duas opções, com a margem δ = 0,10, PROPOSTA (a seção 5 do plano).
- **GPU:** não.

## 5. Entrega

- **Testes:** só mudam documentos. Rodar `python -m pytest tests/test_infra_verificar_relato.py tests/test_infra_indice_desvios.py -q`
  e conferir o relato com o `tools/verificar_relato.py`.
- **Registro:** uma seção no fim de `docs/registro/2026-11.md`. Não editar o `docs/REGISTRO_DESVIOS.md`.
- **PR** contra a `main`, na categoria arquitetura, com o relato no corpo. O worker para e espera o Matheus.

## 6. Fora desta tarefa

- **Dentro desta tarefa** fica só o roteiro dos estímulos e do formulário, descrito no plano. Fora dela:
  - gerar os estímulos (o roteiro de captura do replay) e montar o formulário: é implementação, e só depois da aprovação do plano;
  - recrutar os avaliadores e coletar;
  - mudar qualquer sinal de aprendizado que a auditoria aponte como regra nossa: é uma decisão de desenho, levada ao Matheus.
- **As peças 3 e 4 da recomendação** (a sonda de relevância e o teste contrafactual da fala) ficam para depois.

## 7. Critérios de aceitação

- O `docs/AUDITORIA_V3_SUCESSO_CORPO.md` existe, e cada sinal tem um `arquivo:linha` que resolve na `main` 136e6088.
- O `docs/PLANO_ANALISE_V3_LEGIBILIDADE.md` existe e tem: a pergunta, os estímulos, a tarefa, o N, a medida primária, a regra de
  leitura com a margem, a regra de parada, a exclusão, o que refutaria e as decisões LG-1 a LG-6.
- O `tools/verificar_relato.py` passa no corpo do PR.

## 8. Precisa do Matheus

As decisões LG-1 a LG-6 estão no plano (seção 9), cada uma com a recomendação e o custo de errar. Na auditoria, nenhuma decisão:
ela só descreve.
