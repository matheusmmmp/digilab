# Validação visual: app × canvas

Roteiro para conferir se `web/digilab_sprites.html` (ou `web/app/`, depois da
`TAREFA_FRONT_TS`) está igual ao desenho. Referências, nesta ordem de autoridade:

1. `docs/UI_GUIDELINES.md` (regra; vence a prancha quando divergirem);
2. canvas https://claude.ai/artifact/2XHKuofCpCfZeA1N6iVy9g, lido com a ferramenta Artifact
   (`action: "read"`, `path: "project/<Prancha>.dc.html"`); cada prancha tem 390×844 px;
3. `docs/REVISAO_INTERFACE_UP.md` (problemas já apontados).

Números, nomes de Digimon e textos das pranchas são **exemplo**. Compare **estrutura, ordem,
hierarquia, componentes, cores, tipografia, escala de sprite e estados**, não o conteúdo.

## Como comparar cada tela

1. Ler a prancha no canvas e anotar: blocos de cima para baixo, componente de cada bloco
   (seção 7 do guia), cores (tokens `--dl-*`), fonte de cada texto, escala de sprite.
2. Abrir o app em **390×844**, tema claro, com um save de teste no estado da prancha (usar os
   controles "Tempo (teste)" ou um registro preparado). Screenshot.
3. Preencher a tabela da tela: **igual / parecido / diferente / ausente**, com o motivo.
4. Corrigir o que for "diferente" ou "ausente", desde que haja dado no motor. Sem dado:
   não inventar, marcar como lacuna.
5. Screenshot depois. Conferir também 360 px (sem rolagem lateral), 1280 px e tema escuro.

## Checklist por tela

Em todas: cabeçalho da tela (faixa quadriculada + título Rubik itálico com contorno), barra de
4 destinos, fundo hexagonal, cards com borda branca + contorno azul + sombra dura, alvos
≥ 44 px, nomes como no app (níveis Digimon, formas pelo Digimon, espécies pelo brasão; os
nomes das pranchas são exemplo), números com vírgula.

| tela do app | pranchas | conferir |
|---|---|---|
| Pet | `UpPet`, `PvChamado` | cabeçalho com retrato redondo (abre Meus pets), plaquinha do nome, etiqueta de estágio, relógio; palco em card hexagonal com anel e sprite 3×; emote de emoção; balão de causa conforme o estágio; 4 necessidades em barra de 5; faixa de chamado com barra da janela e Atender; par necessidade (rosa sólido) × vontade (malha ciano tracejada); ações; tempo de teste recolhido |
| Treinar | `TreinoNormal`, `TreinoPausa`, `TreinoForcar` | cena com o pet e balão "pausa?"; fadiga com marcas 40 e 60; sobrecarga roxa com marcas 30 e 60; 6 exercícios em grade 3×2 com ícone hexagonal, ganho +2/+1 e selo de aptidão; acima de 60 todos em FORÇAR listrado; folha de confirmação com ganho × custo |
| Aprendizado | `EnsinarAgora`, `EnsinarPolitica`, `EnsinarDecisoes`, `DiarioLembrancas` | instinto (cinza) × aprendido (malha ciano) por ação, rótulo só onde diverge; decisões com chip de causa ou "? instinto e acaso"; memória em 4 + 2 espaços; métricas de desejo e obediência em blocos; texto técnico recolhido |
| Evolução | `EvoArvore`, `EvoPorque`, `EvoRumo`, `EvoSombria`, `EvoCrianca`, `UpEvolucao` | árvore vertical em 4 colunas que cabe em 360 px; estados percorrido (visto verde) / agora (anel amarelo) / possível (tracejado) / fechado (apagado) / sombria (roxo tracejado); legenda; tocar no nó abre o "por quê" (nada só no hover); revelação em tela cheia com listras e sprite 4× |
| Arena | `ArenaEscolha`, `ArenaAoVivo`, `ArenaFim`, `ArenaMelhor10`, `ArenaRivalFixo`, `BatVS` | card do seu pet com lutas de treino; rivais em cards (nome sem cortar e sem repetir); Lutar primário grande; palco com fundo de arena, sprites 3×, HUD vida + guts, turno em hexágono, distância com acento ("médio"); balão de intenção do rival; regra em uso em card de malha; regras de combate em cards SE/ENTÃO com travar/vetar em ícone |
| Campanha | `CampInicio`, `CampMapa`, `CampRivais`, `CampDesafio`, `CampConquista` | mapa com as ilhas do Digimon UP cabendo na largura; estados vencido (bandeira, caminho amarelo) / aberto (marcador roxo, "você está aqui") / trancado (nuvem + cadeado); card do lugar com rivais; lição de cada rival; comparação de stats seu × rival |
| Luta (palco) | `BatAcao`, `BatTecnica`, `BatChefe`, `BatSombria`, `BatDerrota` | ação em plaquinha, dano em número com contorno, técnica em malha, chefe com barra larga, sombria com contorno roxo e passiva escrita, derrota com "o que decidiu a luta" e ensinar |
| Diário | `DiarioRegistro`, `DiarioCatalogo`, `DiarioLab`, `DiarioHoje` | registro com filtros por tipo e etiqueta colorida; "Novo ovo" em área de risco; catálogo em grade 5×3 + detalhe com barras; Lab marcado como ferramenta de pesquisa |
| Catálogo | `CatGrade`, `CatFicha`, `CatNaoVisto`, `CatRivais`, `CatDesktop` | contador "vistos / total"; busca; filtros por estágio e por brasão; grade 4 colunas (8 no desktop) com número, sprite 1× e nome sem cortar; não vistos em silhueta com "???"; selo SEU; sombria com contorno roxo; ficha com idle animado 3× (120 ms), quadros da animação, "como se chega" em malha, técnica, 6 stats relativos ao pet comum, linha evolutiva; aba Rivais com NPCs da campanha e bots |
| Configurações | `CfgPrincipal`, `CfgAparencia`, `CfgFala`, `CfgDados`, `CfgSobre` | entrada pela engrenagem no Diário; lista em grupos (Jogo, Fala, Dados, Sobre) com ícones do `docs/ASSETS_UP.md`; tema com prévia; tamanho do texto com prévia; reduzir movimento; dicas; modo de fala em 3 opções + status do modelo; tempo de teste marcado TESTE; "Novo ovo" em área de risco; créditos e aviso de uso pessoal |
| Conversar | `ConvChat`, `ConvEstagios`, `ConvVerificador`, `ConvEstados` | faixa de status da fala (ponto + texto) em vez de checkbox técnico; balões por estágio; chips de fatos citados; fala "sem base" tracejada e riscada |
| Meus pets | `MpAtual` | só o que existe: ativo, texto "um pet por vez", voltar ao anterior, registro e novo ovo, exportar |
| Primeira vez | `PvBoasVindas` … `PvVoltou` | só se a tarefa incluir onboarding; senão, registrar como fora do escopo |

## Entrega

Para cada tela: tabela preenchida, screenshot antes e depois (390 px), itens corrigidos,
itens que ficaram diferentes **e por quê** (falta dado no motor, decisão do Matheus, custo).
No fim, um resumo: quantas telas iguais, parecidas e diferentes.
