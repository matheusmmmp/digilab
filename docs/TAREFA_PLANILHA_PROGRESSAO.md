# Tarefa — planilha de progressão, jornada do jogador e escala de stats

Leia o `CLAUDE.md` e `docs/REGISTRO_DESVIOS.md` antes de começar. Todas
as regras do `CLAUDE.md` valem, em especial: **nenhum número sem artefato
ou arquivo de configuração que o produza.**

## Objetivo

Montar a **planilha de progressão** do Digilab: a jornada do jogador do
ovo ao endgame, numa curva só, juntando peças que hoje estão espalhadas
(estágios, cronograma de interações, treino, evolução, campanha, arena).

A pergunta que a planilha precisa responder: **em cada ponto da jornada,
quanto poder o pet deveria ter, quanto o conteúdo exige, e a distância
entre os dois faz sentido?** Hoje sabemos de pelo menos um lugar onde não
faz: na campanha, o pet sem treino vence os NPCs de 0,39 a 0,66 das vezes.

A tarefa tem três partes, com parada para aprovação entre elas:

- **Parte A — planilha:** mede e aponta onde a curva não fecha. Não muda
  regra.
- **Parte B — desenho:** jornada do jogador com tutorial e proposta de
  nova escala de stats. Só documento e planilha. Não muda regra.
- **Parte C — implementação da escala:** muda regra, atrás de chave de
  configuração, **só depois de o Matheus aprovar a Parte B**.

---

## Contexto: referências pesquisadas

As planilhas internas desses jogos nunca foram publicadas. O que existe
são tabelas reconstruídas pela comunidade (guias, wikis, medições nos
aparelhos). Os números abaixo são dessas fontes e servem só como
referência de desenho; entram na aba `referencias` com a fonte indicada.

**Tamagotchi original (1996)** — fontes: guias de comunidade (Thaao's
Tamas, TamaVault, wiki do Tamagotchi).
- Bebê → criança em 65 min; adolescente aos 3 "anos"; adulto aos 6
  (1 ano = 1 dia real; a idade sobe ao acordar).
- Erro de cuidado: não atender o chamado em 15 min; não apagar a luz em
  15 min após dormir.
- Criança com 0–1 erro → adolescente "bom"; 2+ → "ruim". Adulto por duas
  colunas: erros de cuidado (0–2 × 3+) e de disciplina.
- **Tamagotchi Uni:** criança e adolescente ~24 h cada; erros acumulam
  entre as fases; **segunda chance**: o melhor adulto sai com 0 erros *ou*
  com 1–3 erros + pelo menos 3 passeios.

**V-pets de Digimon (Ver.20th / Color)** — fonte: guias do humulos.
- Estágios de ~10 min, 6–12 h, 24 h, 36 h, 48 h.
- Uma moeda por estágio (cuidado → treino e superalimentação → batalhas →
  cuidado); contadores zeram a cada evolução.

**Digimon World 1 (PS1)** — fonte: guias do GameFAQs.
- Requisitos em quatro grupos: stats, peso (faixa por forma), erros de
  cuidado, bônus. Cumprir mais grupos aumenta a chance; não é preciso
  cumprir todos.
- Exemplo (MetalGreymon): até 10 erros, peso 65 g, stats altos em seis
  atributos, bônus de 30+ batalhas.
- Vida de 15–20 dias de jogo; virar Ultimate soma 96 h de vida.
- **Fracasso vira forma, não fim:** sem requisito cumprido, vira Numemon.

**Digimon World: Next Order** — fontes: GameFAQs, PSNProfiles, Steam.
- Linha do tempo: bebê 1 h → In-Training 3–4 h → Rookie 3–7 dias →
  Champion 5–12 dias → Ultimate 10–16 dias → Mega 14–20 dias.
- Academia: +30–40 em um stat por hora de jogo; batalhas: +100–150 em
  cada stat por hora. Rookies ganham mais (treinar cedo rende mais).
- **Dificuldade como multiplicador de ganho:** inimigos iguais; o modo
  fácil dobra o ganho de stats e reduz requisitos.
- **Indicador de proximidade** por evolução: Fix / H (falta 1) / M
  (faltam 2) / L (faltam 3+).


**Escala de stats na franquia** (para a Parte B) — fontes: guia de evolução
do Digimon World 1 no GameFAQs (SydMontague), wiki Grindosaur, guias de
comunidade.
- **Digimon World 1:** bebês e In-Training são treinados até ~100 nos
  atributos e poucas centenas de HP/MP. O Rookie inicial mira HP 1000, MP
  500, ataque 100 e 50 nos demais; o primeiro Agumon selvagem tem 800 de
  HP. Um Champion "sólido" tem HP ~1500, MP ~1000 e ~100 nos demais; as
  exigências de Champion vão de ~1000 a 2000 de HP e 100–250 nos
  atributos. Ultimates exigem HP 3000–7000 e 400–600 nos atributos.
  Ordem de grandeza: **~10× do In-Training ao Rookie e ~4–6× do Rookie ao
  Ultimate.**
- **Next Order:** In-Training tem teto de stats muito baixo; Ultimates no
  começo do jogo ficam em ~1,2–1,8 mil por stat; no fim do jogo, 7–8 mil.
- **Digilab hoje (relato do Matheus):** o bebê mostra **9** de vida e o
  ultimate **13** — ~1,4× do primeiro ao último estágio. O jogador não
  sente o pet crescendo. Conferir de onde vêm esses números na web e no
  Python antes de propor (é o ponto do catálogo em pontos, com soma zero,
  sendo exibido como "vida"?).

**Jogos de fãs recentes** (referência de mercado e de jornada) — fontes:
páginas do itch.io e do próprio jogo, entrevista na Grindosaur,
comentários de jogadores.
- **Digital Tamers 2 (DragonRod, 2024)** e **Digital Tamers: ReBorn:**
  luta 1x1 em plataforma; o jogador dá comandos, o Digimon luta. ReBorn:
  meta de **12 campeonatos ao longo do ano** (calendário como espinha). DT2:
  progressão por **recrutar Digimon para a vila** (Jijimon no nível 3; modo
  desafios com 5+ recrutados); **renascimento com herança** (pontos de
  ReBorn exigem morte no nível 15+ com 4+ corações de amizade); 120+
  desafios, 50+ missões. Gratuito, com doação no jogo; sem online por custo
  de servidor e trapaça. Jogadores reclamam que o treino é complicado.
- **Digital Monster Ver Web (Aderek, ago/2026):** v-pet no navegador; o
  tempo continua com o navegador fechado; contas e salvamento na nuvem;
  **guia de campo** das espécies encontradas; conjuntos de espécies por
  aparelho + conjuntos criados pela comunidade; app Android com widget e
  anúncios. Princípio declarado: **a luta contribui para a progressão sem
  substituir o ciclo de cuidado.**

Princípios adicionais para a aba `principios`:
8. A luta testa o parceiro; não substitui o cuidado.
9. Progressão por coleção (vila, guia de campo), além de poder.
10. Calendário de metas dá ritmo (campeonatos ao longo do tempo).
11. Renascimento com herança (gerações mais fortes).

**Princípios extraídos** (vão para a aba `principios`):
1. Uma moeda por estágio; contadores zeram na evolução.
2. Limiares grossos e legíveis (faixas, não números exatos).
3. Fracasso vira forma, não game over.
4. Segunda chance para quem errou cedo.
5. Indicador de proximidade da próxima forma.
6. Dificuldade pelo ritmo de ganho, com inimigos fixos.
7. Treinar cedo rende mais.

---

## Fontes de dados do Digilab

Ler os valores **do código e dos artefatos**, nunca desta tarefa nem de
outro documento:

- `digilab/config.py` (treino, campanha, combate, estágios, cronograma,
  personalidade, cuidado corporal — o que existir);
- JSONs de dados em `docs/` (`cronograma_interacoes`, `pve_treino`,
  `arvore_evolucao`, `catalogo_pets`, `cuidado_corporal`), conferindo se
  batem com o `config.py`; divergência vai para a aba `alertas`;
- artefatos: `artifacts_treino/`, `artifacts_campanha/`, validação do
  `experiments/calibrar_progressao.py`, `artifacts_combate_v21c/`;
- a versão web (`web/digilab_sprites.html`) só para registrar onde os
  parâmetros diferem do Python (velocidade do tempo, etc.).

Se um número necessário não existir em nenhum artefato: **não rodar
experimento pesado para obtê-lo**. Marcar a célula como `SEM FONTE` e
listar, na aba `alertas`, qual run o produziria e quanto tempo levaria.

## Como gerar

- Script `tools/gerar_planilha_progressao.py` (fora de `digilab/`; pode
  usar `openpyxl`), que lê as fontes acima e escreve a planilha. A planilha
  é **regenerável**: rodar o script de novo depois de mudar o config
  atualiza tudo.
- Saída: `artifacts_progressao/planilha_progressao.xlsx`.
- Valores derivados como **fórmulas do Excel** (interações acumuladas,
  distância entre poder esperado e exigido), não números colados.
- Toda célula numérica de entrada tem ao lado a **fonte** (arquivo +
  campo, ou caminho do artefato) e o status: `CONFIG`, `ARTEFATO`,
  `REFERENCIA` ou `SEM FONTE`.
- Cores: verde = dentro da meta; amarelo = perto do limite; vermelho =
  curva não fecha. Legenda na primeira aba.

## Abas

1. **`leia_me`** — o que é cada aba, legenda de cores e status, data,
   commit do repositório e como regenerar.
2. **`referencias`** — os números dos jogos acima, com fonte.
3. **`jornada`** — uma linha por marco, do ovo ao endgame. Colunas:
   marco; estágio; tempo desde o ovo; interações acumuladas (por braço de
   dono simulado, se houver artefato); pontos de treino acumulados
   esperados; poder esperado em combate; conteúdo liberado; desafio;
   poder exigido; distância; taxa de vitória esperada sem treino e com
   treino típico; **meta** da taxa (proposta, marcada PROPOSTO); o que o
   jogador deve sentir ali.
4. **`estagios`** — duração; intervalos de cada necessidade; janela de
   chamado; moeda do estágio; contadores e se zeram; limiares; forma
   resultante; **forma de fracasso**; rota alternativa (se houver).
5. **`portoes`** — cada NPC da campanha (lugar, estágio sugerido, stats,
   estilo, ε) e a arena: requisito, distância, taxa de vitória medida sem
   e com treino (dos artefatos), meta proposta, status de cor.
6. **`economia_treino`** — ganho por sessão, retorno decrescente, tetos
   por stat/estágio/vida, fadiga, forçar, sobrecarga, peso do ponto em
   combate, custo em interações; curva de pontos acumulados por dia para
   o dono atencioso e para o exigente (dos artefatos).
7. **`endgame`** — o que existe depois do adulto (arena, campanha,
   galeria, formas sombrias, etc.) e o que está só especificado ou em
   ideia, com o status EXECUTADO / ESPECIFICADO / IDEIA.
8. **`principios`** — os 11 princípios × Digilab: já tem / parcial /
   falta, e onde no código.
9. **`escala`** — preenchida na Parte B (ver B2).
10. **`alertas`** — todo lugar onde a curva não fecha, com o número, a
   fonte e uma proposta de ajuste (só proposta). Incluir no mínimo:
   - pet sem treino vencendo NPCs de 0,39 a 0,66 (campanha não exige
     treino);
   - E4: adulto esmaga adolescente (0,94–1,0);
   - campanha que não separa mais os donos;
   - efeito das durações de estágio cortadas pela metade;
   - crescimento de ~1,4× do bebê ao ultimate na vida exibida (9 → 13);
   - divergências entre `config.py`, JSONs de `docs/` e web;
   - células `SEM FONTE` e a run que as produziria.

## Também entregar

`docs/PROGRESSAO.md`: uma página com a curva resumida (um gráfico gerado
pelo script: poder esperado × exigido ao longo da jornada), os 5 alertas
mais graves e as propostas de ajuste em ordem de prioridade.

---

## Parte B — jornada do jogador e escala de stats (desenho, sem mudar regra)

### B1. Jornada do primeiro pet, com tutorial

Documento `docs/JORNADA_JOGADOR.md` + aba `jornada` detalhada. Para **cada
estágio do primeiro pet**, definir:

- o que o jogador **deve aprender** ali (uma mecânica nova por momento,
  no máximo duas);
- como é ensinado: **tutorial contextual**, no momento em que a mecânica
  aparece, sem parede de texto. Como o bebê não fala, o tutorial precisa
  de uma voz: propor um **mentor original** (personagem próprio, não da
  franquia) ou dicas do sistema; a partir do adulto, o próprio pet pode
  explicar;
- o sinal de que o jogador aprendeu (ex.: atendeu 3 chamados na janela);
- o que é liberado ao fim;
- a meta de dificuldade (taxa de vitória esperada sem e com treino).

Esqueleto proposto (ajustar aos tempos e sistemas reais do repositório):

| estágio | o jogador aprende | é liberado ao fim |
|---|---|---|
| ovo | o pet é dele; o tempo passa mesmo com o app fechado (ou não, conforme o modo) | nome, espécie |
| bebê | chamados e janelas (fome, higiene, sono); atender rápido importa; ler emotes | revelação sereno/arisco **com o porquê** ("você atendeu X de Y chamados") |
| criança | ensinar: elogiar e repreender; desejo de necessidade × vontade; primeira recusa; treino por botão (sem forçar) | primeiro rival (Campina): vencível com cuidado e **algum** treino |
| adolescente | a linha que o caráter decidiu e por quê; técnica; fadiga, "Forçar" e o aviso de sobrecarga; travar/vetar regras de combate | Torre de pedra: um rival que exige stats, outro que exige estilo |
| adulto | forma final e por quê; passiva; arena contra outros pets | Cidadela (chefe); endgame |

**Ponto obrigatório:** o momento em que o jogador **precisa treinar para
subir na campanha** tem que ser desenhado de propósito, com a meta
explícita na planilha (ex.: rival da Campina sem treino ~0,3, com treino
típico ~0,8 — PROPOSTO). Hoje o pet sem treino vence 0,39–0,66, então esse
momento não existe.

Também registrar o tempo total de tutorial e os pontos onde um amigo que
nunca viu o jogo pode travar.

### B2. Nova escala de stats

Objetivo: o jogador **sentir** o pet crescer, na ordem de grandeza da
franquia, sem quebrar a pesquisa nem o combate aprovado.

Proposta de desenho a validar:

1. **Separar perfil de escala.**
   - **Perfil:** os pontos do catálogo (espécie + temperamento + caráter +
     arquétipos), com soma zero. Continua sendo o que a pesquisa compara.
   - **Escala:** um multiplicador por estágio e pelo treino, que dá a
     magnitude exibida e usada em combate na campanha.
2. **Tabela de escala por estágio** (PROPOSTO, calibrar): ordem de
   grandeza inspirada no DW1, mas comprimida para o ritmo do Digilab. Ex.:
   vida exibida bebê ~50, criança ~200, adolescente ~600, adulto ~1500;
   atributos na mesma proporção. O script da planilha deve mostrar a
   tabela atual × proposta × DW1 lado a lado.
3. **Invariância de escala no combate (requisito duro):** multiplicar
   todos os stats dos **dois** lutadores pelo mesmo fator tem que produzir
   **exatamente a mesma luta**. Com isso, lutas entre pets do mesmo estágio
   não mudam, e a aprovação da bateria V21C continua valendo. Onde houver
   constante absoluta no combate (ex.: parry de 5, custos de guts), propor
   como torná-la relativa.
4. **Pesquisa intocada:** a arena da pesquisa só coloca adultos contra
   adultos e normaliza pelo orçamento — a escala não entra lá.
5. **Treino na escala:** o ganho por sessão passa a ser proporcional à
   escala do estágio (treinar o bebê rende pouco em número absoluto, mas
   muito em proporção, como os Rookies do Next Order). Rever o
   `peso_ponto_combate = 3` nessa nova base.
6. **Lutas entre estágios:** com escala de franquia, adulto contra
   adolescente vira uma luta muito desigual **de propósito** (é um "stat
   check"). O gate E4 precisa ser redefinido para essa realidade; propor a
   nova definição.
7. **NPCs da campanha** passam a ser especificados na mesma escala, com a
   distância alvo da aba `portoes`.

Entregar na planilha a aba **`escala`**: tabela atual, proposta e DW1;
simulação do efeito da proposta nas metas da aba `portoes` usando o que
existir de artefato (sem run pesada); lista de constantes absolutas do
combate.

**Parar aqui e esperar a aprovação do Matheus.**

---

## Parte C — implementar a escala aprovada

Só depois da aprovação da Parte B.

- Nova chave de configuração (ex.: `ConfigEscala`), **desligada por
  padrão**; com ela desligada, todas as runs antigas reproduzem byte a
  byte.
- Teste de **invariância de escala**: para as sementes da bateria V21C,
  multiplicar os stats dos dois lados por fatores diferentes (ex.: 2, 10,
  37) dá lutas idênticas.
- Rodar a bateria V21C com a escala ligada: todos os gates que passavam
  continuam passando.
- Recalibrar os NPCs da campanha para as metas aprovadas, nas sementes de
  calibração; validar nas de validação.
- Tutorial e mentor implementados conforme o `JORNADA_JOGADOR.md`
  aprovado.
- **Portar para a web** (regra do projeto): números exibidos, escala,
  tutorial e mentor. Saves antigos abrem e passam a exibir a nova escala.
- Registrar tudo em `docs/REGISTRO_DESVIOS.md`.

## Testes

- O script roda do zero e gera a planilha sem erro.
- Nenhuma célula numérica de entrada sem fonte ou status.
- Rodar duas vezes sem mudar nada gera valores idênticos.
- Partes A e B: nada em `digilab/` alterado.
- Parte C: invariância de escala; bateria V21C com a escala ligada;
  runs antigas idênticas com a escala desligada.

## O que reportar

Ao fim da Parte A:
1. **Onde a curva não fecha**, em ordem de gravidade.
2. Quantas células ficaram `SEM FONTE` e quais runs as preencheriam.
3. Divergências encontradas entre `config.py`, documentos e web.
4. O status dos 11 princípios no Digilab.

Ao fim da Parte B:
5. De onde vêm o "9" do bebê e o "13" do ultimate.
6. A jornada proposta e onde um jogador novo pode travar.
7. A tabela de escala proposta × atual × DW1, as constantes absolutas do
   combate e a nova definição do E4.

Ao fim da Parte C:
8. Invariância de escala e bateria V21C com a escala ligada.
9. Metas da campanha atingidas nas sementes de validação.

Nenhum número sem a fonte que o gerou.
