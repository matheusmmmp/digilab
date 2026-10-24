# TAREFA_INTERFACE_UP — nova interface visual do jogo web

Trocar a pele e a navegação do jogo web (`web/digilab_sprites.html`) pela direção visual
"Digimon UP" desenhada no canvas, e trocar os sprites do Digimon World pelos quadros
extraídos do Digimon UP. **É uma tarefa de interface.** Nenhuma regra de jogo, número,
fórmula, motor ou log muda.

## 1. Fontes de verdade

| o quê | onde |
|---|---|
| **Guia de interface (regra)** | `docs/UI_GUIDELINES.md`: princípios, semântica fixa, tokens, componentes, estados e checklist. Quando guia e prancha divergirem, vale o guia. |
| Desenho (referência visual) | canvas https://claude.ai/artifact/2XHKuofCpCfZeA1N6iVy9g, página **Direção Digimon UP**. Ler com a ferramenta Artifact (`action: "read"`, `path: "project/<arquivo>"`), nunca por WebFetch. Pranchas: `UpPet`, `UpParceiros`, `UpEvolucao`, `UpLuta`, `UpResultado`, `UpTreinar`, `UpConversar` e **`UpComponentes` (tokens e componentes: é a especificação)**. A página **Batalhas** detalha a luta: `BatVS` (pré-luta, travar/vetar), `BatAcao`, `BatTecnica`, `BatChefe`, `BatSombria`, `BatDerrota` e `BatDesktop`. A página **Arena** segue o painel atual (rivais de estilo, 8 formas adultas, rival fixo do Laboratório, Lutar e Melhor de 10, lutas de treino do adolescente): `ArenaEscolha`, `ArenaAoVivo`, `ArenaFim`, `ArenaMelhor10`, `ArenaRivalFixo`. A página **Campanha** mostra o mapa (Campina → Torre de pedra → Cidadela) e seus estados: `CampInicio`, `CampMapa`, `CampRivais`, `CampDesafio`, `CampConquista`, `CampDesktop`; as ilhas vêm de `Sprite/WorldMap_01/03/06.png`, a névoa de `WorldMapCloud_01.png`, os marcadores de `Common_WorldMapStage_0*.png`. A página **Evolução** mostra a árvore real (bebê → Sereno/Arisco pelo cuidado → 4 linhas pelo caráter → 2 adultos por linha pelo caráter complementar, mais a sombria da linha): `EvoArvore`, `EvoPorque`, `EvoRumo`, `EvoSombria`, `EvoCrianca`, `EvoDesktop`. Formas não alcançadas aparecem só em silhueta. A página **Diário** cobre Registro, memória por espaços, álbum, Catálogo e Cenários: `DiarioHoje`, `DiarioRegistro`, `DiarioLembrancas`, `DiarioAlbum`, `DiarioCatalogo`, `DiarioLab`, `DiarioDesktop`. A página **Conversar e álbum** segue a `docs/TAREFA_FALA_LIVRE.md` (fala por LLM só no adolescente e no adulto, verificador que mede sem trocar, chat que não ensina): `ConvChat`, `ConvEstagios`, `ConvVerificador`, `ConvEstados`, `AlbumGrade`, `AlbumDetalhe`, `ConvDesktop`. A página **Treinar e ensinar** usa os 6 exercícios reais (`CTR.exercicios`) e os limiares de fadiga (40 pede pausa, 60 só forçar), e mostra o Aprendizado (instinto × política, decisões e porquê, desejo e obediência, regras de combate): `TreinoNormal`, `TreinoPausa`, `TreinoForcar`, `EnsinarAgora`, `EnsinarPolitica`, `EnsinarDecisoes`, `EnsinarRegras`; os ícones de treino são provisórios. A página **Meus pets** separa o que existe (`MpAtual`: um pet só, "voltar ao anterior", "registro e novo ovo") do que é **proposta, fora do escopo desta tarefa** (`MpLista`, `MpDetalhe`, `MpTroca`, `MpDigitalizando`, `MpNovoOvo`, `MpImportar`: vários pets congelados, troca, importar com conflito); implementar só `MpAtual` agora. A página **Primeira vez** cobre o onboarding: `PvBoasVindas`, `PvComoCuidar`, `PvComoEnsinar`, `PvComoCrescer`, `PvOvo`, dicas com recorte (`PvChamado`, `PvEnsino`, `PvNavegacao`, todas puláveis e com "não mostrar dicas") e o resumo sem culpa de quem volta depois de um tempo (`PvVoltou`). A página **Offline e sincronização** marca o que existe (save local, acesso remoto com senha, fala por frases prontas) e o que é **proposta fora do escopo** (offline com fila, sincronizar, conflito de registro, erro ao salvar): `OffEstados`, `OffJogando`, `OffSincronizando`, `OffConflito`, `OffRemoto`, `OffErroSalvar`. O álbum ainda não existe no motor: guardar uma fala é marcar um evento de apresentação do registro, sem efeito no pet. A página "Primeiras direções" é histórico; ignorar. |
| Quadros de animação | `D:\Trab\digilab\Assets\Digimon Up Assets\Animacoes\`: `indice.json` (15 linhas de parceiro, nível/categoria de cada um dos 257 Digimon), `<Digimon>/quadros.json`, `quadros/qNNN.png`, `efeitos/`, `ataques.json` + `ataques/<nome>/` (projétil e impacto quadro a quadro), `grupo_*.gif`. `LEIA-ME.md` explica os campos. Abrir `DOCUMENTACAO.html` para ver as animações. |
| Peças de interface | `D:\Trab\digilab\Assets\Digimon Up Assets\Digimon Up Assets\Sprite\`: `CustomEmoji_Digimon_*.png` (emotes pixel: 6 carne, 5 maçã, 9 joinha, 10 feliz, 11 surpreso, 12 coração, 13 nota, 14 "!", 15 estrela), `CustomEmoji_16.png` (espadas), `Common_Icon_Time_1.png`, `Common_Icon_Lock.png`, `Common_Create_Bg_Pattern.png` (hexágonos), `Common_Create_Cha_Bg_01.png` (anel de plataforma), `Egg_*.png`, ícones de treino `Punch_A_Lv1`, `Sandbag_A_Lv1`, `Rock_A_Lv1`, `Waterfall_A_Lv1`, `Dash_A_Lv1`, `Running_A_Lv1`, fundo `CampAssist_Bg_Training.png`; em `Texture2D/`: `PVP_Bg_Octagon.png` (arena). |
| Pipeline atual de sprites | `D:\Trab\digilab\Assets\gerar_atlas.py`, `catalogo_sprites.json` (forma → recorte), `digilab_atlas.png`; no HTML: `ATLAS_URL`, `sprite()`, `chaveSprite()`, `OVO`. |

## 2. Regras

1. **Só interface.** Não mexer em motor, `CV/CV21/CSO/CTR/CAMPANHA`, fórmulas, sementes, formato
   do log, chave do `localStorage` (`digilab-web-v21-sprites`) nem na ordem de consumo de RNG.
   Um save existente tem que abrir igual depois da troca. Nada no pacote Python muda.
2. **Honestidade acima de fofura.** A interface só mostra o que o motor registrou. Os números e
   textos das pranchas são **exemplos de layout**, não dados. Se um elemento do desenho não tiver
   fonte no motor web (ex.: chip de causa, fala "sem base" do verificador, janela de chamado,
   sobrecarga), **não inventar**: omitir o elemento e listar como lacuna no relatório.
3. **Sprites de terceiros: fora do repositório.** Nenhum PNG do Digimon UP entra no repositório.
   O atlas novo fica em `D:\Trab\digilab\Assets\` (como o atual) e o HTML o carrega por caminho
   relativo. Manter o crédito no rodapé. (Nota de 2026-10-24: o "uso pessoal" saiu; vale a regra de
   procedência de `docs/UI_GUIDELINES.md`, seção 5.1.)
4. **Layout independente do sprite.** O espaço de cada sprite vem do tamanho nativo do quadro,
   ampliado só em escala inteira (1× listas/retratos, 2× cards, 3× palco, 4× revelação), com
   `image-rendering: pixelated` / `imageSmoothingEnabled = false`. Trocar a arte não pode
   quebrar a tela.
5. **Falhar alto.** Quadro ou forma sem sprite mapeado levanta erro visível (como o
   `sprite desconhecido` de hoje), nunca cai num placeholder silencioso.
6. Celular primeiro (360–600 px), funcionando no computador. Alvos de toque ≥ 44 px, contraste
   4,5:1, nada comunicado só por cor, nada importante só no hover. Tema claro e escuro.
7. Sem padrões de culpa ou retenção (nada de "ele vai ficar triste se você sair", contadores
   ansiosos ou notificações insistentes).

## 3. Etapas (parar e mostrar ao fim de cada uma)

### Etapa 0: mapa de sprites (não codar antes da aprovação)

O jogo tem **4 espécies** (`brasa`, `cirro`, `ferrugem`, `limo`) × **15 formas** (1 bebê,
2 crianças `sereno/arisco`, 4 adolescentes `brigao/guardiao/cacador/colosso`, 8 adultos) +
formas sombrias (hoje desenhadas com o sprite da base). O Digimon UP tem 15 linhas lineares
de 6 níveis. Não existe correspondência direta.

Entregar uma **proposta de mapeamento**, sem codar:
- uma tabela forma → Digimon (nome da pasta em `Animacoes/`) para as 60 formas + os 4 ovos;
- critério usado (ex.: cada espécie puxa de 2–4 linhas do UP com a mesma paleta; nível do UP
  compatível com o estágio: Baby I/II → bebê, Rookie → criança, Champion → adolescente,
  Ultimate/Mega → adulto);
- como marcar a forma sombria (proposta: mesmo sprite com filtro/paleta roxa + contorno, ou
  um Digimon "virus" da mesma linha, se houver);
- NPCs e rivais (`sprite:` em `CAMPANHA`, `BOT_SPRITE`): proposta usando a categoria
  `inimigo` do `indice.json`;
- qual grupo de pose é o idle de cada um (normalmente `A`), e quais têm quadros com
  `orientacao: "revisar"` ou `parcial: true` que exigem conferência.

Salvar como `Assets/catalogo_sprites_up.json` (fora do repo) + tabela legível no relatório.
**Parar e esperar o Matheus aprovar ou trocar nomes.**

### Etapa 1: atlas e animação

- Novo gerador (`Assets/gerar_atlas_up.py`, biblioteca padrão + Pillow): lê
  `catalogo_sprites_up.json` e os `quadros.json`, empacota os quadros do grupo idle (e, se
  couber, um grupo de ataque e um de dano) + as peças de UI da seção 1 num atlas com um JSON de
  recortes. Tamanho nativo, sem redimensionar.
- No HTML: trocar `ATLAS_URL`/`sprite()` para o atlas novo, com animação de idle a 120 ms por
  quadro (o tempo documentado nas prévias; os clipes oficiais não foram exportados, registrar
  isso). Manter o caminho antigo funcionando atrás de uma constante até a Etapa 4, para
  comparar.
- Parar e mostrar: palco com os 4 bebês, 1 adulto por espécie e 1 sombria, animando.

### Etapa 2: tokens e componentes

Implementar como variáveis CSS (`:root` + tema escuro), com os nomes `--dl-*` da seção 4 de
`docs/UI_GUIDELINES.md`, e classes os itens da prancha `UpComponentes`: cores (marinho `#173A8A`, marinho fundo `#0F2A66`, azul ação `#2C73E0`,
borda `#9FC2EF`, fundo `#E8F0FB`, texto `#13244D`, necessidade `#E5489F`, aprendido
`#6FE3FF`/`#0F3A86`, destaque `#FFD23F`, ok `#3FCF6A`, forçar listrado `#FFCC33`/`#1A1A1A`,
sombrio `#7B3FB8`), tipografia (Rubik 900 itálico com contorno para números e títulos de tela,
M PLUS Rounded 1c para texto, DotGothic16 para detalhes de LCD, via Google Fonts com fallback
local), botões em 4 estados (normal, pressionado, foco, desativado), plaquinha de nome,
etiquetas, barra segmentada, barra relativa ao pet comum, card de desejo, balões de fala por
estágio, fundo hexagonal. Regra fixa: **necessidade = sólido rosa; vontade aprendida = malha
ciano tracejada.** Parar e mostrar uma página de teste com todos os componentes nos dois temas.

### Etapa 3: navegação

Reorganizar as 8 abas atuais em 4 destinos, com barra inferior no celular:

| destino | abas atuais |
|---|---|
| **Pet** | Estado |
| **Crescer** | Aprendizado + Evolução |
| **Lutar** | Arena + Campanha |
| **Diário** | Registro + Catálogo + Cenários (+ álbum de lembranças, se existir) |

"Meus pets" abre pelo retrato no topo da tela Pet. Toda função que existe hoje continua
alcançável; nenhum painel some. Manter o `localStorage` da aba lembrada (migrando o valor
antigo para o destino novo). Parar e mostrar.

### Etapa 4: telas

Aplicar o desenho de cada prancha ao painel correspondente, **com os dados reais do motor**:
`UpPet` (palco com anel, balão de causa por estágio, necessidades, chamado, desejo),
`UpParceiros` (grade de pets, ativo com cantos amarelos, em espera congelado), `UpEvolucao`
(revelação + linha evolutiva + "por quê" com os traços reais), `UpLuta` (fundo de arena,
barras de vida, turno, intenção telegrafada, regra usada com Travar/Vetar se o motor tiver),
`UpResultado` (ganhos + elogiar/repreender a jogada, se o motor aceitar), `UpTreinar`
(6 exercícios reais com os ícones de treino, fadiga, sobrecarga, botão Forçar só acima do
limite), `UpConversar` (fala LLM ou frases prontas, estado do modelo, fala marcada
"sem base" se o verificador existir). Os nomes dos exercícios nas pranchas são inventados:
usar os do jogo. Remover o caminho antigo de sprites ao fim.

## 4. Verificação

- Abrir no navegador em 390×844 e em desktop, temas claro e escuro; sem erro no console.
- Um save antigo abre e mostra o mesmo pet, no mesmo estado.
- Todas as funções das 8 abas antigas continuam alcançáveis (listar onde ficou cada uma).
- Testes Python e preflight continuam passando (nada no pacote deveria ter mudado).
- Cada tela passa no checklist da seção 14 de `docs/UI_GUIDELINES.md`.
- Screenshots de cada tela no relatório.

## 5. Relatório final

1. O que foi feito, por etapa, com os arquivos tocados.
2. Tabela de mapeamento de sprites aprovada.
3. **Lacunas:** cada elemento do desenho que ficou de fora por falta de dado no motor, e o que
   o motor precisaria registrar para ele existir.
4. Desvios do desenho e o motivo.
5. Limitações dos quadros (clipes não oficiais, quadros a revisar) e onde aparecem.
