# Revisão da interface implementada (2026-09-28)

Revisão de `web/digilab_sprites.html?e=1` no navegador, em 360, 390 e 1280 px, temas claro e
escuro, comparada com `docs/UI_GUIDELINES.md` e o canvas (páginas Direção Digimon UP, Arena,
Campanha, Evolução, Diário, Treinar e ensinar). Save de teste: Togemon, dia 11.

**O que está bom:** barra de 4 destinos (inferior no celular, lateral no desktop), tokens e
tema escuro funcionando, diálogo Meus pets, ícones de treino, chip "? sem motivo registrado",
card de necessidade, sem erro no console, sem rolagem horizontal fora da Arena.

Cada item diz onde está, o que acontece e o que fazer. Ordem: primeiro bugs, depois regras do
guia, depois desvios do desenho.

---

## P0 · Bugs

1. **Arena: texto da campanha no palco da arena.** Em Lutar › Arena aparece
   "Seu pet × Gazimon: escolha um lugar no mapa e aperte Desafiar." A mensagem de status do
   palco é compartilhada entre os modos. Separar por modo (ou limpar ao trocar de aba).
2. **Arena em 360 px: dois elementos passam da borda.** `select#rival` e o nome do rival no
   topo da luta (`#nome-b`, ex.: "Monochromon (agre…"). Select com `width:100%`; nome com
   `text-overflow: ellipsis` e o estilo numa segunda linha.
3. **Registro: contagem não bate com a lista.** Diz "3 eventos no registro" e mostra dezenas
   de linhas. Se são coisas diferentes (ações do dono × histórico reconstruído), rotular as
   duas; se não, corrigir a contagem.
4. **Campanha: mapa cortado à direita** (a Cidadela some em 360 px, com barra de rolagem
   lateral). Fazer o mapa caber na largura.
5. **Alvo de toque pequeno:** checkbox "fala por LLM" tem 13×13 px; "O que o pet mudou",
   "Montar à mão" e "Como o treino funciona" têm 23 px de altura; bolha "chamar..." 40 px.
   Mínimo 44 px (guia 7).

## P1 · Regras do guia

6. ~~Estágios com nomes de Digimon~~ **Resolvido (2026-09-28): os níveis Digimon (Digi-Egg,
   In-Training, Rookie, Champion, Ultimate, Mega) são o certo**, decisão do Matheus (guia seção
   12). Continua valendo trocar o jargão técnico: "gambits" → "regras de combate"; "política
   atual" → "o que aprendeu com você"; "Jeito" → "temperamento". ("sparring" pode ficar como
   "lutas de treino" ou "sparring", à escolha.)
7. ~~Nomes de espécie e de forma~~ **Resolvido: brasões (Coragem, Amizade, Conhecimento,
   Sinceridade), formas e NPCs com nomes de Digimon estão aprovados.** Não trocar.
8. **Números crus e com ponto decimal:** "curiosidade -0.19, teimosia -0.74…",
   "impetuoso -0.07", "+0.050 · 0×", "vig 11.0 · fôl 12.0", "+0.0 de 36".
   Usar vírgula (pt-BR). Onde é traço/caráter, mostrar barra relativa ao pet comum com rótulo
   só nos extremos (guia 7.5); os valores exatos vão para um "Detalhes" recolhido.
9. **Informação só no hover:** Evolução diz "Passe o mouse num nó para ver o requisito".
   Proibido (guia 13). Tocar no nó abre o detalhe.
10. **Texto de pesquisa na tela do jogador:** "Combate V2.1", "PROVISÓRIO", "a bateria V2.1
    reprovou (ver CLAUDE.md)", "bandit contextual", "Dwarf Fortress", "5% das decisões são
    exploração", "|eixo| ≥ 0.2". Mover para um "Como funciona" recolhido ou para o Lab.

## P2 · Desvios do desenho

11. **Cabeçalho global** "DIGILAB + Crie, cuide e treine…" em toda tela, ~90 px. Trocar pelo
    cabeçalho de cada tela (faixa quadriculada + título em Rubik itálico, guia 7.11); o
    slogan fica só na primeira vez.
12. **Parágrafos longos no topo** de Campanha, Arena, Evolução, Catálogo e Aprendizado.
    Uma linha + "Como funciona" recolhido.
13. **Pet · palco:** é a cena antiga (céu, cocô em triângulos), sprite pequeno. Desenho
    `UpPet`: card hexagonal, anel de plataforma, sprite 3×, emote de emoção, balão de causa.
14. **Pet · chamado:** com "chamando você", falta a faixa "Chamado: fome · barra da janela ·
    Atender" (guia 7.9). Só aparece o "!" na cena.
15. **Pet · controles de tempo** (Pausa, 1x, 10 min/s, 1 h/s, 6 h/s, +1 h) na tela principal.
    São ferramenta de teste: recolher em "Tempo (teste)" ou mover para o Lab.
16. **Pet · fala por LLM:** checkbox + "(local: qwen2.5:3b, sem custo)". Trocar pela faixa de
    status da fala (`ConvEstados`): ponto + "modelo local · sem custo", liga/desliga à parte.
17. **Treinar:** falta a marca 40 "pede pausa" na fadiga e a 30 (aviso) na sobrecarga; falta o
    ganho no botão (+2 principal / +1 secundário) e o selo de aptidão da espécie; não há cena
    com o pet nem o balão "pausa?" (`TreinoNormal`, `TreinoPausa`). Conferir o estado acima de
    60 (botões FORÇAR listrados + confirmação, `TreinoForcar`).
18. **Arena · palco:** canvas pequeno, sem o fundo de arena (`PVP_Bg_Octagon`), sprites fora
    de 3×, "medio" solto. Desenho `ArenaAoVivo`/`BatAcao`: HUD com vida + guts, turno em
    hexágono, distância, balão de intenção do rival, regra em uso em card de malha.
19. **Arena · regras de combate:** lista de texto com pesos e botões "travar"/"vetar" em
    texto. Desenho `EnsinarRegras`/`BatVS`: cards SE/ENTÃO numerados, botões de ícone com
    estado (travada/vetada/livre), contador de espaços. O bloco "Regras" (parede de texto)
    vai para recolhido.
20. **Arena · escolha do rival:** select nativo. Desenho `ArenaEscolha`: lista de cards com
    sprite e uma linha de estilo, barra de lutas de treino, "Lutar" primário grande.
21. **Campanha · mapa:** mapa desenhado à mão, em vez das ilhas do Digimon UP
    (`Sprite/WorldMap_01/03/06.png`, nuvem `WorldMapCloud_01.png` nos lugares trancados,
    marcadores `Common_WorldMapStage_0*.png`). Desenho `CampMapa`.
22. **Evolução · árvore:** horizontal, muito espaço vazio, nós pequenos, rolagem lateral.
    Desenho `EvoArvore`: 4 colunas verticais que cabem em 360 px, estados percorrido/agora/
    possível/fechado/sombria com legenda, e card "por quê" (`EvoPorque`).
23. **Aprendizado · memória:** texto corrido. Desenho `DiarioLembrancas`: 4 espaços recentes
    + 2 duradouros, vazios aparecendo. **Instinto × aprendido:** barra do aprendido em malha
    ciano e rótulo só onde diverge (`EnsinarPolitica`).
24. **Registro:** sem filtros; "Novo ovo" ao lado de "Verificar replay". Desenho
    `DiarioRegistro`: filtros por tipo, etiqueta colorida por tipo, "Novo ovo" em área de
    risco separada.
25. **Catálogo:** cards com área vazia grande e stats abreviados. Desenho `DiarioCatalogo`:
    grade 5×3 e detalhe da forma com barras dos 6 stats.

## Perguntas para o Matheus

- ~~Item 7~~ resolvido: nomes em Digimon aprovados.
- Treinar ficou em Crescer (com Aprendizado e Evolução). No desenho `UpPet`, Treinar é uma
  ação da tela Pet. Manter em Crescer?
