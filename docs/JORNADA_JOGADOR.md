# Jornada do jogador e escala de stats (Parte B, PROPOSTO)

Desenho para aprovação (`docs/TAREFA_PLANILHA_PROGRESSAO.md`, Parte B). Nada aqui muda regra: é documento e
planilha. Os números vêm de `artifacts_progressao/planilha_progressao.xlsx` (abas `jornada`, `portoes`, `escala`),
com a fonte de cada um ao lado. O que está marcado PROPOSTO é meta ou desenho meu, não medida.

## 1. De onde vêm o "9" do bebê e o "13" do ultimate

São **pontos do catálogo**, não vida. A ficha do Catálogo (web: `web/app/src/telas/diario/TelaCatalogo.tsx`; HTML
antigo: `web/digilab_sprites.html`, a mesma barra) mostra seis barras de stat, e a primeira é o **vigor**, desenhada
com o trilho de vida (`dl-vida-trilho`). Esses stats são o perfil da forma: espécie + ramo + linha + forma, com
modificadores de soma zero, **sempre somando 60** (`digilab/config.py > ConfigCatalogo.orcamento_especie`;
`digilab/combate_v2/v21/catalogo.py > stats`). A evolução não aumenta esse total; só redistribui.

- **9** = vigor do Koromon (Coragem/Brasa, In-Training): `ConfigCatalogo.especies['brasa']['vigor']`.
- **13** não aparece em nenhuma forma de Coragem (o máximo é 12: WarGrowlmon e Gallantmon). No Catálogo, 13 é o vigor
  do Imperialdramon Dragon Mode (Conhecimento/Ferrugem, Mega), e também do DemiVeemon, o bebê da mesma árvore. É o
  número de vigor mais provável de ter sido lido como "vida do ultimate".
- A **vida de combate** está na linha logo abaixo das barras ("vida 39 · guts …"): `(hp_base + hp_por_vigor × vigor) ×
  mult_estagio`, com V21C (`hp_base` 75, `hp_por_vigor` 2,5) e `mult_estagio` 0,4 / 0,6 / 0,8 / 1,0. Na Brasa ela vai de
  **39** (bebê) a **88–105** (adultos): 2,7×. No Python o número é o mesmo (`catalogo.perfil(..., cfg=CONFIG_COMBATE_V21C).hp_max`; o padrão da função é a V2.1 original, 70 + 3 × vigor).

Então o jogador vê duas coisas que quase não crescem: o stat de catálogo (≈1,3×, soma fixa) e a vida (≈2,7×). As
referências crescem ~50× (DW1: In-Training com atributos até ~100 → Ultimate com HP 3000–7000).

## 2. A jornada do primeiro pet

Tempos do Python e da web (iguais): In-Training 3 h, Rookie 12 h, Champion 18 h + 10 lutas de treino
(`ConfigEvolucaoPesquisa.dur_*_min`, `web/app/motor/constantes.ts > DUR_EVO`). Na web o tempo anda só com a página
aberta, na velocidade escolhida (padrão 10 min de pet por segundo; 1x com chamado aberto).

**Voz do tutorial (PROPOSTO): Bit, o zelador do laboratório.** Personagem original (não é da franquia): um robozinho de
manutenção do Digilab, sprite próprio a desenhar em 1x como os ícones. Aparece só no momento em que a mecânica surge, uma
frase por vez, e some ao tocar. O bebê não fala; do adulto em diante **o próprio pet** assume as explicações (ele já tem
fala com causa), e o Bit se aposenta. Alternativa sem personagem: dicas do sistema na faixa do topo.

| estágio | o jogador aprende (no máximo duas) | como é ensinado (contextual) | sinal de que aprendeu | liberado ao fim | meta (PROPOSTO) |
|---|---|---|---|---|---|
| ovo | o pet é dele; o tempo do pet anda com o app aberto | Bit, ao chocar: "é seu; enquanto a janela estiver aberta, ele vive" | tocou no ovo e escolheu a velocidade | nome, espécie (brasão) | — |
| In-Training (3 h) | chamados e a janela de 15 min; atender rápido importa | no primeiro chamado o tempo cai para 1x, o Bit aponta o balão e o botão certo | atendeu 3 chamados na janela | revelação sereno/arisco **com o porquê** ("você atendeu X de Y") | — |
| Rookie (12 h) | treino por botão; o primeiro rival pede treino | o Bit leva à sala de treino; no primeiro Desafiar perdido: "faltou força: treine e volte" | 3 sessões e vitória sobre o Brutamontes | Campina vencida; a Torre abre | Brutamontes: **≤ 0,3 sem treino, ≥ 0,8 com +8 pontos** |
| Rookie (cont.) | ensinar: elogiar/repreender o que ele acabou de fazer; necessidade × vontade; a primeira recusa | na primeira ação espontânea, Elogiar/Repreender com o "o que muda"; na primeira recusa, o balão com o porquê | elogiou ou repreendeu 3 vezes na janela de 2 min | linha pelo caráter + técnica | — |
| Champion (18 h) | a linha e a técnica; fadiga, "Forçar" e a sobrecarga | a revelação mostra o eixo que decidiu; na fadiga 40 o pet pede pausa (o Bit explica uma vez); no primeiro Forçar, a folha com o custo | leu o porquê da linha; atendeu uma pausa (ou forçou sabendo) | Torre (3 rivais à escolha) | Torre: **≤ 0,3 sem treino, ≥ 0,8 com +22** |
| Champion (cont.) | travar/vetar regras de combate; as 10 lutas de treino | depois da primeira luta, o Resultado mostra a regra nova com Travar/Vetar; o contador "x de 10" no topo | travou ou vetou uma regra; fez as 10 lutas | forma adulta + passiva | — |
| Ultimate/Mega | forma final e passiva; arena contra outros pets | o **pet** explica a passiva na revelação | desafiou o chefe | Cidadela (chefe); endgame | Soberano: **≤ 0,3 sem treino, ≥ 0,8 com +36** |

**O momento em que o jogador precisa treinar** é a Campina, desenhado de propósito: o Brutamontes vence o Rookie sem
treino (meta ≤ 0,3) e perde para o Rookie com o treino que cabe no estágio (+8 pontos, `ALCANCE['tier1']['crianca']`,
meta ≥ 0,8). **Hoje esse momento não existe**: o Rookie sem treino vence o Brutamontes **0,45** e com +8 vence **0,81**
(`experiments/configs/progressao/validacao_resultado.json`, sementes de validação). Nos cinco NPCs o pet sem treino
vence 0,39–0,66 (média por NPC).

**Tempo de tutorial (PROPOSTO):** 8 momentos, ~2 frases de ~5 s cada = **~1,5 min de leitura espalhados por ~33 h de
pet**, nunca mais de uma frase por tela.

### Onde um jogador novo pode travar

1. **Chamado perdido na velocidade 10 min/s.** O tempo cai para 1x quando o chamado abre (web), mas quem olha outra aba
   perde a janela de 15 min e o bebê vira arisco sem entender por quê. A revelação precisa dizer "atendeu X de Y".
2. **Fechar o app e esperar que o pet viva.** Na web o tempo **para** com a página fechada; num v-pet (e no Digital
   Monster Ver Web) ele continua. Quem volta no dia seguinte encontra o pet onde deixou: bom ou ruim, tem de ser dito no
   ovo.
3. **Rookie curto.** O Rookie dura 12 h e parte é sono: o dono atencioso fez **3,7 sessões** no estágio inteiro
   (`artifacts_treino/vidas`, contagem). Quem não sabe que o treino existe chega ao Champion sem treino.
4. **A janela de 2 min do ensinar.** Elogiar/Repreender só vale para o que ele acabou de fazer; sem o aviso do Bit,
   parece que o botão não faz nada.
5. **As 10 lutas de treino.** Sem elas o Champion não evolui, e o requisito está escondido na aba Evolução.
6. **Forçar sem entender a sobrecarga.** A forma sombria aparece dias depois do forçar; o aviso da fala fria (30) é
   sutil.
7. **Regras de combate.** Travar/Vetar é o conceito mais abstrato do jogo; os jogadores do Digital Tamers 2 reclamam de
   treino complicado, e aqui o treino + regras somam fadiga, forçar, sobrecarga, aptidão e gambits.
8. **Depois do chefe, nada pede nada.** O endgame não tem meta no tempo (ver 4.).

## 3. Nova escala de stats (B2)

### 3.1 Desenho: perfil × escala

- **Perfil** = os pontos do catálogo de hoje (soma zero). É o que a pesquisa compara. Não muda.
- **Escala E** = magnitude do lutador: `E = E_estágio × (1 + β × pontos treinados)`, β = 0,03 (PROPOSTO: 36 pontos →
  ×2,08). A vida exibida é a vida de hoje sem o multiplicador de estágio, × E.
- **No combate** cada lutador luta nas próprias unidades (vida e dano de hoje, sem o multiplicador de estágio), e o dano
  que A causa em B é multiplicado por **E_A / E_B**. Guts fica absoluto (é ritmo, não tamanho).
- **Invariância (requisito duro):** multiplicar E dos dois lados pelo mesmo fator dá a mesma razão E_A/E_B, **o mesmo
  float**, e a luta é idêntica bit a bit. Dois pets do mesmo estágio sem treino têm razão 1,0 exata: a bateria V21C não
  muda. O teste da Parte C multiplica E por 2, 10 e 37 nos dois lados e compara as lutas.
- **Pesquisa intocada:** a arena da pesquisa fixa E igual nos dois lados (adultos, treino normalizado ao orçamento).

### 3.2 Tabela (aba `escala`)

| estágio | vida hoje (Brasa) | vigor de catálogo hoje | vida proposta (E) | DW1 (HP de referência) |
|---|---|---|---|---|
| In-Training | 39 | 9 | 50 | ~100 (atributos) |
| Rookie | 58,5 | 9 | 200 | 1000 |
| Champion | 78 | 9 (brigão) | 600 | 1500 |
| Ultimate/Mega | 88–105 | 5–12 | 1500 | 3000–7000 |
| **crescimento** | **2,7×** | **~1,3×** | **30×** | **~50×** |

Degraus propostos: ×4, ×3, ×2,5 (DW1: ~10× do In-Training ao Rookie, ~4–6× do Rookie ao Ultimate). Comprimido para o
ritmo do Digilab (3 h + 12 h + 18 h, contra semanas no DW1).

### 3.3 Treino na escala (B2.5)

O ponto treinado vai para a escala (β) e para o perfil (proporções, como na arena normalizada). Um ponto rende a mesma
proporção em qualquer estágio, mas **no começo** ele é uma fatia maior do que o pet tem: com +8 no Rookie a escala sobe
24%; um ponto a mais no adulto com +36 rende 1,4% do que ele já tem. Em número exibido é o contrário (Rookie: +6 de vida
por ponto; adulto: +45), que é o "treinar cedo rende muito em proporção" do Next Order. O `peso_ponto_combate = 3` sai
da campanha: o ×3 absoluto era o jeito de o treino pesar como a evolução; com β ele pesa pela escala.

### 3.4 NPCs na mesma escala (B2.7)

Cada NPC na escala do estágio **sugerido** para ele, com um fator. Proposta da Parte B: Brutamontes ×1,15 do Rookie,
Torre ×1,2–1,3 do Champion, Soberano ×1,6 do adulto. **Calibrado na Parte C** (`ConfigEscala.fator_npc`): Brutamontes
1,1, Sentinela 1,6, Carcereiro 1,5, Porteiro 1,1, Soberano 1,2; validação em `experiments/configs/escala/validacao.json`
(a Sentinela não fecha as metas com nenhum fator). A razão pet/NPC passa a ficar abaixo de 1 sem treino e
acima com o treino típico **em todos os portões** (Brutamontes 0,87 → 1,08; Sentinela 0,83 → 1,38; Carcereiro e Porteiro
0,77 → 1,28; Soberano 0,62 → 1,30). Os NPCs da Torre **deixam de ter tamanho de adulto** (hoje lutam com vida de adulto
contra o Champion). A taxa de vitória que isso dá é SEM FONTE: só existe rodando (Parte C, `calibrar_progressao.py`
nas sementes de calibração, validação nas de validação). Proposta junto: ε dos NPCs de 0,4–0,5 para 0,2, porque o ε
alto é o que deixa o pet sem treino vencer.

### 3.5 Constantes absolutas do combate (B2.3)

Tornar relativas (× E_A/E_B): dano do golpe rápido (8), disparo (6), pesado (25), parry (5), investida (8), dano extra
do duelista (4). Saem da campanha: o multiplicador de estágio na vida (0,4–1,0). Ficam absolutos: custos e limiares de
guts, guts máximo e inicial, regeneração, carregar +25, defender +5 (ritmo). Multiplicadores de força, mira e guarda
(0,7 + 0,03 × stat) ficam, porque dependem do perfil, que não escala. Frações de vida nas condições já são relativas.
Lista com fonte na aba `escala`.

### 3.6 E4 redefinido (B2.6)

**Definição final (Matheus, depois da Parte C):** a evolução sempre importa. O adulto sem treino vence o adolescente da
mesma linha, sem treino e com o treino máximo do estágio (+22), em **pelo menos 0,60**; sem teto (esmagar é de
propósito). O E4′ e o E4″ abaixo foram a proposta da Parte B e reprovaram na bateria com a escala.

Com escala de franquia o adulto sem treino esmaga o adolescente sem treino de propósito (E_adulto/E_Champion = 2,5):
é um "stat check". Hoje o E4 já falha por esmagar (vigia 1,00, sentinela 1,00, muralha 1,00, titã 0,99, furioso 0,94;
`artifacts_combate_v21c/validacao/gates.json`). Proposta:

- **E4′:** adulto **sem treino** × adolescente da mesma linha **com o treino máximo do estágio** (22 pontos): taxa do
  adulto em **[0,60, 0,85]**. Mede se o treino do estágio anterior compensa parte da evolução (princípio 7).
- **E4″ (sanidade):** adulto × adolescente, os dois sem treino: taxa do adulto **≥ 0,90**.

## 4. O que os jogos de fãs mudam na jornada (referência pedida pelo Matheus)

Da aba `principios` (extras E1–E6), só propostas:

- **Luta sem substituir o cuidado** (Digital Monster Ver Web): o cuidado já decide o ramo; manter o cuidado como moeda
  do In-Training e fazer a campanha **exigir** treino (3.4) em vez de só a luta.
- **Tempo com o app fechado:** decidir de propósito. Hoje fechar = pausa, o que é o "modo produto" do cronograma
  (congelamento, `cronograma_interacoes.json > modo_produto`), mas sem o aviso no ovo.
- **Calendário como espinha** (ReBorn, 12 campeonatos): uma ideia para o endgame, que hoje não tem meta no tempo.
- **Renascimento com herança** (DT2: morte no nível 15+ com 4+ corações dá pontos): hoje o ovo novo apaga o pet; uma
  herança pequena (ex.: o brasão ou um ponto de treino) daria a segunda chance do princípio 4.
- **Treino simples:** o painel do treino junta fadiga, forçar, sobrecarga e aptidão; o tutorial deve apresentar um
  conceito por estágio (tabela da seção 2), não os quatro de uma vez.

## 5. Para aprovar

1. A jornada da seção 2 e o mentor Bit (ou dicas do sistema, sem personagem).
2. As metas da campanha: ≤ 0,3 sem treino e ≥ 0,8 com o treino típico em cada portão.
3. A escala 50 / 200 / 600 / 1500, o β = 0,03 e o desenho "dano × E_A/E_B".
4. NPCs na escala do estágio sugerido (Torre deixa de ser adulta) e ε 0,2.
5. O E4′ e o E4″.
6. Tempo com o app fechado: manter a pausa (e avisar) ou passar a correr.
