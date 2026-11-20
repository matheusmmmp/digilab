# TAREFA V2 — CANAIS-REFORCO (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B (dono de `lobos.py`). Worktree e branch: `v2-canais-reforco`.
Status: ABERTA. Etapa C4 do `docs/ROADMAP_V2.md` (revisão 3); hipótese H-R2 de `docs/research/digibrain/mechanisms/reinforcement.md`;
decisão K-6 de `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (aprovada em 2026-10-05).

## 1. Pergunta

Hoje a consequência chega ao aprendiz como **um escalar** (`sinal_homeostatico`, `sinal_homeostatico_fruta`: drives e humor somados). H-R2:
o mesmo sinal **separado por canal** (fome, higiene, energia e humor/fruta, cada um com o próprio peso de crédito) muda a atribuição ou a
adaptação? Esta tarefa só **constrói** os canais, para a ablação "canais × escalar" da validação única.

## 2. Mudança mínima (só `lobos.py` e `config.py`)

- Chave `ConfigConsequencia` (ou `ConfigLobos`) `canais_ligados` (padrão False) e o que mais o desenho pedir, todos PROPOSTOS e registrados.
- **Contrato K-6, obrigatório:** com os canais ligados o **total de sinal** por decisão é o do escalar (mesma soma em inteiros); só a
  representação muda (o que cada canal credita a quê). Escreva no PR como isso foi garantido.
- **Canais desligados = escalar byte a byte** (gabarito gravado antes da mudança, como no #167).
- O genoma ainda **não** modula a sensibilidade por canal (é a H-R4, depois); deixe o ponto de entrada nomeado, sem uso.
- Parâmetro novo além disso só por adendo 2 do plano da calibração, varrido junto com o ganho (K-6): se precisar, proponha no PR.
- **Não muda:** `engine.py`, `AcaoPet`, o mundo (A), a bancada (D), a web.

## 3. Gates (mecanismo; só as sementes dos testes)

- G1 com os canais.
- Canais desligados = vida de hoje byte a byte (P1, P2 e P3, nos mundos das frutas e no padrão).
- Total de sinal igual ao escalar, decisão a decisão, numa vida com os canais ligados.
- Um teste em que a separação muda o crédito (por exemplo, uma fruta que mata a fome e piora o humor credita a escolha da fruta por
  um canal e o comer por outro), com a conta exata.

## 4. Entrega

Um PR, relato no corpo, um bloco "para o chat D" (como a bancada liga os canais). Suíte inteira. Seção no fim do `CLAUDE.md` e do
`docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus. Próximo para o B (rodada 10): a calibração conjunta (K2), depois do PR do D.
