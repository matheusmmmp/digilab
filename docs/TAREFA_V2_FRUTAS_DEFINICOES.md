# TAREFA V2 — FRUTAS-DEFINICOES (2026-10-01)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat C. Worktree e branch: `v2-frutas-definicoes`. Status:
ABERTA (começa depois de o C fechar o conflito do #114).

## 1. Pergunta

Definir, **só no papel**, as quatro variáveis operacionais das frutas (necessidade, gosto, efeito, vício) para o nó N4 do
`docs/ROADMAP_V2.md`. As frutas são a condição "descasado" da pergunta maior: sem elas não há ambiente que contradiga a
predisposição herdada.

## 2. Depende de

- Ler inteiros: `v1/docs/referencias/V3_SINTESE_FRUTAS_VICIO_V1_V6.md`, `v3_referencias_verificadas.csv` (38 linhas),
  `docs/referencias/REGRAS_CITACAO_DIGILAB.md`, `D:\Trab\digilab\docs\CONTEXTO_DIGILAB_2026-09-30.md`,
  `docs/research/digibrain/mechanisms/hedonic_system.md` (#118) e `docs/ARQUITETURA_V2_VALIDACAO.md` (#117).
- Os rótulos da coluna "verificada" são vinculantes. Nada NÃO LOCALIZADA é citado. Não inventar autor, ano, título ou DOI.

## 3. Mudança mínima

1. **Primeiro commit:** trazer para o repositório a busca V1–V6 (`V3_SINTESE_FRUTAS_VICIO_V1_V6.md`, `v3_referencias_verificadas.csv`,
   `v3_referencias.bib`, `v3_verificacao_crossref.json`) para `docs/referencias/`, como foi feito com a da V2 (D9).
2. **Segundo commit:** `docs/DEFINICOES_FRUTAS_V2.md`, resolvendo uma por uma as sete restrições. Para cada uma: a definição
   escolhida, a justificativa com a referência, e o **campo do log de eventos** que a registra.
   1. **Gostar e querer são dois registros**, não um escalar (Finlayson e Dalton, `10.1016/j.appet.2011.10.011`).
   2. **Vocabulário operacional:** nada no motor, no log ou na fala afirma que o pet sente prazer (Berridge,
      `10.1016/0149-7634(95)00033-b`).
   3. **Gosto não deriva de necessidade:** o gosto de **um** sabor cai com o consumo recente dele sem passar pela fome (Rolls et
      al., `10.1016/0031-9384(81)90310-3`, `10.1016/0031-9384(83)90003-3`).
   4. **Neofobia é traço (do ovo), gosto aprendido é estado** (Pliner e Hobden, `10.1016/0195-6663(92)90014-w`; Beauchamp e
      Moran, `10.1016/s0195-6663(82)80007-x`): onde cada um mora (genoma × estado).
   5. **Vício como assimetria** (Robinson e Berridge, `10.1016/0165-0173(93)90013-p`; Grigutsch et al.,
      `10.1016/j.jbtep.2019.01.002`; ressalva de Nutt et al., `10.1038/nrn3939`). Avaliar e registrar: derivar do RL
      homeostático (Keramati, Durand e Girardeau, `10.1037/rev0000046`) ou mecânica nova; forma funcional, se precisar, de Redish
      (`10.1126/science.1102384`). **Atenção:** o instinto do projeto é regra escrita à mão, sem aprendizado (`digilab/policy.py`);
      "derivar do que já existe" não é reaproveitamento, é aprendizado novo sobre os drives (validação V8 e A6 da arquitetura).
   6. **Confundidor de canal:** comida é canal de cuidado (fome → saúde → morte). Definir o braço de controle e o critério que
      decide se um efeito é ensino ou cuidado (usar o "só cuidado" acoplado e o modo acoplado da bancada).
   7. **Creatures não é precedente:** não escrever "como no Creatures" em lugar nenhum.
   - **Ressalva de ética:** a literatura que existe trata de mecânicas dirigidas ao jogador e não cobre dependência num personagem
     cuidado pelo jogador. O apoio é por analogia e tem de ser rotulado assim.
   - **Restrição de engenharia (validação V5 do roadmap):** `AcaoPet` não pode ganhar membros (o bandit da v1 usa
     `tuple(AcaoPet)`). As frutas entram como **sub-decisão** de comer, como a bola entrou em brincar. Os campos do log
     precisam respeitar isso.

## 4. Experimento

Nenhum. **Não rodar nada.** Nenhum número de balanceamento, equação final ou código: o desenho é do Matheus.

## 5. Entrega

- Dois commits na mesma branch (busca no repo; definições). PR contra a `main`.
- No fim do documento: a lista das decisões que só o Matheus pode tomar, cada uma com recomendação e custo de errar.
- Seção no fim do `docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

Implementação das frutas (N4, rodada 4, chat A), números, vício implementado, porte para a web, reabrir a v1 ou a pergunta do dono.
