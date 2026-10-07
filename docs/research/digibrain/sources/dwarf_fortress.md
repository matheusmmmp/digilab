# Dwarf Fortress: precedente de desenho de jogo

## O que a fonte mostra

- **FONTE, VERIFICADA:** Adams 2021, "Characterization and Emergent Narrative in Dwarf Fortress" (`10.1515/9783839453452-007`):
  memórias, necessidades, preferências, reações emocionais e facetas de personalidade usadas para tornar anões simulados
  **legíveis como indivíduos com história**.
- **NÃO VERIFICADA EM FONTE PRIMÁRIA:** os detalhes de versão (slots de memória, conversão de memória curta em longa,
  estresse) vêm da wiki da comunidade (*Thoughts and preferences*, *Version history*). Conferir a versão do jogo antes de
  descrever implementação. O contexto completo das peças está em `docs/futuro/dwarf_fortress.md`.

## O que não mostra

Neurociência, arquitetura cognitiva validada ou prova de aprendizado. DF responde "como mostrar a história ao jogador",
não "como o agente aprende". A afirmação de que CST/Castro/Sakabe são fontes "melhores" que DF é interpretação: respondem a
perguntas diferentes.

## O que serve ao DigiBrain: memória autobiográfica de alto nível (INTERPRETAÇÃO)

Padrão possível (não decidido): registrar o evento → atribuir saliência e consequência emocional no contexto → reter ou
decair uma memória selecionada → expor o efeito dela no comportamento e no perfil. Confundidor principal: categoria do
evento, emoção atual e persistência da memória mudam juntas.

## Ligação com o repositório

- REPOSITÓRIO: o adendo DF da v1 já implementou memória por espaços (4 curtos + 2 longos), emoção por categoria ×
  temperamento e habituação (`docs/ADENDO_MEMORIA_EMOCAO_DF.md`; `artifacts_v1_memoria_espacos/`, `artifacts_v1_habituacao/`).
  A memória mudou pouco: 6,9% dos motivos citam memória.
- REPOSITÓRIO: a voz própria (pets v7) conta a história do pet a partir do registro (`digilab/historia.py`), mas **não
  decide nada**: é episódio armazenado e narrado, não causal.
- Decisão D7 (`docs/DEFINICOES_V2.md`): na V2, espaços só como regra de engenharia; relembrar (L2) e duas prioridades (L3)
  como candidatas; memória nuclear e estresse adiados (abrem outro canal de cuidado).


## Revisão de 2026-10-07 (pedido do Matheus)

- **Adams 2021** segue VERIFICADA (Crossref conferido de novo: capítulo de livro, `10.1515/9783839453452-007`).
- **Fonte nova a ler:** Short e Adams (orgs.), *Procedural Storytelling in Game Design*, CRC Press, 2019, `10.1201/9780429488337`
  (livro, metadados conferidos no Crossref em 2026-10-07; conteúdo não lido). Tem capítulos de Tarn Adams, o autor do Dwarf Fortress.
- **Para os detalhes de mecânica,** a fonte primária possível são os **arquivos de dados do próprio jogo** (as "raws", texto distribuído com
  ele), como o manual do Creatures 3: documentação de produto. A wiki da comunidade continua NÃO VERIFICADA EM FONTE PRIMÁRIA.
