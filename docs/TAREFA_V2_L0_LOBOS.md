# TAREFA V2 — L0-LOBOS (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: a abrir. Worktree e branch: `v2-l0-lobos`.
Status: ABERTA.

## 1. Pergunta

Uma política com lobos nomeados (percepção, memória e emoção, impulsos, decisão), **com o aprendizado desligado**, reproduz o instinto byte a byte?
Nó L0 da fase 1b (hipótese H1 do `docs/PLANO_V2_PESQUISA.md`). É o esqueleto sobre o qual L1 (o lobo de decisão aprende) vai rodar.

**Decisão do Matheus (2026-10-01): a V2 abandona o bandit.** O aprendiz da V2 é esta política. O bandit (`digilab/policies/bandit.py` e subclasses) fica
congelado só para reproduzir a v1: não é apagado, não é usado nem estendido aqui.

## 2. Depende de

Nada além da `main`. Leitura obrigatória: `CLAUDE.md`, `docs/PLANO_V2_PESQUISA.md` (seção fase 1, aprendiz novo; se não estiver na `main`:
`git show origin/plano-v2-pesquisa:docs/PLANO_V2_PESQUISA.md`), `docs/futuro/dwarf_fortress.md` (seção 4: onde as peças cabem nos lobos; nada dele entra agora).
Insumo fora do repositório: `D:\Trab\digilab\docs\digibrain\integration\07_DIGIBRAIN_RESEARCH_ARCHITECTURE_v0.1.md` (esboço dos lobos, PROPOSTO).

## 3. Mudança mínima

- **Novo:** `digilab/policies/lobos.py` com `PoliticaLobos` sob o protocolo `Politica` (`digilab/policy.py:53`: `agir`, `observar`, `estado_interno`).
  - **Percepção:** as mesmas entradas que o instinto e o bandit usam hoje (`Observacao`, `Estado.vetor`).
  - **Impulsos:** as regras do `PoliticaInstinto` (`policy.py:66`).
  - **Memória e emoção:** presente como lobo nomeado, sem efeito na decisão nesta tarefa.
  - **Decisão:** pesos em **ponto fixo** (inteiros), iniciados no prior do instinto; ativação sem `exp`/`log`/funções transcendentais; < 1000 pesos.
  - `estado_interno()` expõe os pesos e, por decisão, a contribuição de cada lobo (o motivo; base do gate G4 da fase 1).
- **Config:** `ConfigLobos` em `digilab/config.py`, com `aprendizado_ligado = False` e status PROPOSTO em cada campo novo. Nada de número mágico.
- **Testes novos** em `tests/test_lobos.py`:
  - **G2:** com o aprendizado desligado, a vida com `PoliticaLobos` é **byte a byte** a vida com `PoliticaInstinto` (mesmo log, mesmas RNG consumidas,
    mesmo estado final), em várias sementes e nos motores `MotorComFeedback` e `MotorPersonalidade`;
  - **G1:** replay pelo log bit a bit;
  - a política nunca muda os pesos com o aprendizado desligado, mesmo recebendo feedback do dono;
  - os pesos são inteiros e a soma das contribuições do motivo fecha com a decisão.
- **Não muda:** `digilab/engine.py` (sha256 conferido), o bandit, qualquer protocolo ou run da v1, o jogo web. Sem versão de pet nova (a web vem depois do L1).

**Restrição de desenho que o worker tem de resolver e documentar:** a igualdade byte a byte exige que, com os pesos no prior, a decisão consuma a RNG
exatamente como o `PoliticaInstinto`. Se isso não for possível com a decisão em ponto fixo, **pare e reporte** ao coordenador com a alternativa, antes de
relaxar o gate.

## 4. Experimento e gate

- Sem run estatística: o gate é teste determinístico. Sem sementes reservadas além das dos testes. Sem GPU.
- Gate L0 (PROPOSTO): G1 e G2 passando; `python -m pytest tests/ -q` inteiro passando, inclusive `test_protocol.py::test_engine_nao_foi_alterado`.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`.
- Registro: seção própria no fim do `CLAUDE.md` (mapa do repositório: `policies/lobos.py`) e do `docs/REGISTRO_DESVIOS.md` (interpretações do desenho).
- PR contra a `main` com resumo. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Ligar o aprendizado (L1); peças do Dwarf Fortress (L2, L3); ambiente mínimo (A1); porte para a web e versão de pet; qualquer run de painel.
