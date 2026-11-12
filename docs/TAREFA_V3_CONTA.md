# TAREFA V3 — CONTA (2026-11-11)

Coordenador: o Matheus, nesta sessão. Worker: Claude Code (Opus 5.5). Worktree e branch: `v3-conta`. Status: ABERTA (o plano entregue;
as CN-1 a CN-12 DECIDIDAS em 2026-11-11, a CN-12 revista e a CN-13 e a CN-14 DECIDIDAS em 2026-11-12; as CN-15 a CN-18 com o
Matheus).

Categoria: arquitetura. Origem: Matheus, 2026-11-11: planejar a conta (login, primeiro acesso, perfil), o save na nuvem entre aparelhos, a proteção contra raspagem e a infraestrutura de servidor.

O pedido, nas palavras dele: "o que a gente vai ter que adicionar em UX Design e também em infraestrutura do estado atual do projeto,
para, por exemplo, ter página de login, página de cadastro, essas coisas assim, que é padrão", e, sobre o save na nuvem entre aparelhos,
"Sim, entra".

## 1. Pergunta

O que o jogo web, que hoje é de um jogador e guarda o save no navegador, precisa ganhar em telas e em servidor para ter uma conta com
login, o mesmo pet em mais de um aparelho e uma proteção razoável contra a raspagem por robôs e agentes de IA, a um custo de projeto
pessoal?

Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é do produto (`docs/PRODUTO_VISAO.md`) e é a base do `docs/PLANO_V3_MMO.md`.
A pesquisa em Python não muda.

## 2. Depende de

- **Para o plano (esta entrega):** nada.
- **Para as etapas de código:** as decisões CN-1 a CN-14 (seção 12 do `docs/PLANO_V3_CONTA.md`); a CN-5 e a CN-6 mudam a MMO-4 e a
  MMO-2 aprovadas, e precisam do ok explícito do Matheus.

## 3. Mudança mínima

**Nesta entrega, só documentos:**
- `docs/PLANO_V3_CONTA.md`, o plano;
- esta tarefa;
- a seção do desvio em `docs/registro/2026-11.md`.

**O que não muda,** nesta entrega e em nenhuma etapa sem decisão própria: o `engine.py` e o Python; o motor do pet (`web/app/motor/`) e
o formato do save; as versões de pet antigas e os gabaritos; o `servidor/servidor_local.py` e as rotas dele.

## 4. Experimento e gate (se houver run)

Não há run. A etapa CN0 é uma medida de engenharia (o tamanho dos saves), não de pesquisa, e não usa faixa de sementes reservada.

## 5. Entrega

- Testes: nenhum nesta entrega (só documento). Cada etapa de código traz os seus.
- Registro: `docs/registro/2026-11.md`, seção "2026-11-11 — CONTA: o plano da conta e do save na nuvem". O índice
  `docs/REGISTRO_DESVIOS.md` fica com quem faz o merge (`python tools/gerar_indice_desvios.py`).
- PR contra a `main`, com o plano PROPOSTO e as decisões CN-n. Merge só pelo Matheus.

## 6. Fora desta tarefa

- **O código** de qualquer etapa: começa depois das decisões e das pranchas.
- **O ranking**, as sementes e as tabelas: são do `docs/PLANO_V3_MMO.md`.
- **Contratar** domínio, VPS ou qualquer serviço: é do Matheus, na CN5.
- **O parecer jurídico** sobre a LGPD.

## 7. Critérios de aceitação

- O `docs/PLANO_V3_CONTA.md` existe e tem: o que existe hoje; a conta e o login; as telas; a sessão e o banco; o save na nuvem (a
  sincronização, os dois aparelhos, a divergência, o que sincroniza, as versões, as cópias); a proteção; a infraestrutura com o custo
  estimado; o que muda no plano MMO; a privacidade; as etapas; os riscos; a monetização (os modelos, a receita e o lucro com 100 e 1 000 jogadores por dia); as decisões CN-n com a recomendação e o custo de errar.
- Cada número novo do plano está marcado PROPOSTO, SEM FONTE, ou tem a fonte dita.
- O corpo do PR passa em `python tools/verificar_relato.py --arquivo F --base origin/main`.

## 8. Precisa do Matheus

As decisões CN-1 a CN-14, na seção 12 do plano, cada uma com a recomendação e o custo de errar.
