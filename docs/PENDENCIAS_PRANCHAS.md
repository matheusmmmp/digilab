# Pendências das pranchas (telas, botões e ações ainda não implementados)

Levantado em 2026-09-28 na validação visual contra `Assets/Pranchas_UP/` (ver `docs/estilo_up/DIRETRIZES_REPLICAR.md`).
Para cada prancha: o que o app (`web/app/`) já tem e o que falta. **Não implementado ainda**; é lista para futura
implementação. A coluna "precisa" diz se dá para fazer só na interface ou se depende de regra, motor, save ou servidor
(que a validação visual não pode mexer).

Legenda: **existe** = tela e ações existem e foram comparadas; **parcial** = a tela existe mas faltam blocos/ações;
**não existe** = não há tela; **proposta** = a própria prancha marca como proposta (recurso novo).

## Pet

| prancha | estado | falta | precisa |
|---|---|---|---|
| PetTela, PetTelaDesktop | existe | "salvo" só diz se o save abriu (não há sincronização); peso não existe (fica humor); barra de saúde e o porquê aberto são extras do app | — |
| UpPet | substituída | pela PetTela | — |

## Crescer

| prancha | estado | falta | precisa |
|---|---|---|---|
| TreinoNormal, TreinoForcar | existe | cabeçalho com voltar (Treinar fica como aba de Crescer) | — |
| TreinoPausa | parcial | botão **Deixar descansar** | ação no motor (não há "descansar" como evento) |
| UpTreinar | substituída | pelas Treino* | — |
| EnsinarAgora, EnsinarPolitica, EnsinarDecisoes | existe | — | — |
| EnsinarRegras | parcial | a seção **Regras** do Aprendizado (hoje as regras ficam só em Lutar → Arena; no app a 5ª seção é "Jeito") | interface (reusar o editor de regras) |
| EvoArvore, EvoDesktop | existe | chips para ver a árvore das **outras espécies** (Cirro, Ferrugem, Limo) no desktop | interface |
| EvoPorque | parcial | tela "Por que esta linha" com o caráter na hora da evolução, "nasceu cauteloso → virou impetuoso" e o botão **Ver na árvore** | interface (dados do motor: carater das evolucoes) |
| EvoRumo | parcial | tela "Rumo ao adulto": os dois adultos da linha, "paciência hoje", o que falta (tempo, lutas de treino) | interface |
| EvoSombria | parcial | aviso "Caminho sombrio à vista" na árvore quando a sobrecarga se aproxima de 60 | interface |
| EvoCrianca, UpEvolucao | existe | tela cheia no celular e modal no desktop (decisão do Matheus); o "por que" do Champion mostra os 4 eixos (a prancha mostra 2) | — |
| AssetsEvolucao | parcial | metades do brasão se juntando e brilhos (o anel do Digivice girando e o anel de luz já entram) | interface |

## Lutar

| prancha | estado | falta | precisa |
|---|---|---|---|
| ArenaEscolha, UpLuta, BatAcao, BatDesktop | existe | botões **pausar** e **×2** no palco | interface (velocidade da animação) |
| ArenaAoVivo | parcial | ×2 e **Ver o fim** (pular a animação); "regra que ele vai usar" antes do turno | interface |
| ResVitoria, ResDerrota, ResCampanha, ResDesktop (substituem UpResultado) | existe | **Elogiar / Repreender** a ação do momento decisivo ("o que achou do recuo no turno 9?"): o motor não tem feedback do dono sobre uma ação de luta, então o bloco fica de fora (ResNota: bloco sem dado do motor não aparece). **Ver replay** abre a luta refeita do registro no Diário como lista de turnos; rever a animação no palco ainda não existe | elogio de ação de luta = evento novo no motor; animação do replay = interface |
| ArenaFim, BatDerrota | parcial | **Elogiar / Repreender** uma ação da luta (ver ResVitoria acima); **Outra luta**; experiência (×120) e vínculo (+3). Ver replay e "O que decidiu a luta" já existem no modal Resultado | elogio de ação de luta = regra nova no motor; XP não existe no motor; "outra luta" = interface |
| ArenaMelhor10 | parcial | grade V/D das 10 lutas, resumo (vitórias, turnos médios, fintas), "o que ele aprendeu", **Ver regras**, **Lutar de novo** | interface |
| ArenaRivalFixo | parcial | tela do rival fixo do Laboratório com a pergunta do Digilab e **Lutar uma / Melhor de 10** | interface |
| BatVS | não existe | pré-luta com as regras (travar/vetar antes de começar), **Trocar rival**, **Começar luta** | interface |
| BatTecnica, BatSombria, BatChefe | parcial | cards "técnica da linha" com o porquê, "passiva sombria", HUD de chefe com vida numérica | interface |
| CampMapa, CampDesktop, CampRivais | existe | imagens do oceano, moldura digital e bandeira (fora do atlas e da decoração) | asset |
| CampDesafio | parcial | tela de desafio com os stats lado a lado e "regra que pode pesar aqui" | interface |
| CampConquista | não existe | tela "lugar aberto" depois da vitória (**Voltar ao pet**, **Ver a Cidadela**) | interface |
| CampInicio | parcial | estado do bebê com "Desafiar (a partir de criança)" desabilitado | interface |

## Diário

| prancha | estado | falta | precisa |
|---|---|---|---|
| DiarioRegistro | existe | — | — |
| DiarioDesktop | parcial | filtros com várias marcações (o app usa um filtro por vez); o card da direita mostra o último evento, não o evento tocado (linhas de 32 px não passam no alvo de 44) | decisão |
| Abas do Diário | parcial | as pranchas têm Hoje, Registro, Lembranças, Catálogo, Lab; o app tem Registro, Catálogo, Cenários (Lab) | interface |
| DiarioHoje | não existe | linha do tempo do dia com ‹ › entre dias e contadores (cuidados, recusas, lutas, evolução) | interface (histórico do motor) |
| DiarioLembrancas | existe em outro lugar | no app, as lembranças estão em Crescer → Aprendizado, não no Diário | decisão (onde fica) |
| DiarioAlbum, AlbumGrade, AlbumDetalhe | não existe | álbum de falas guardadas com a estrela (por forma, filtros, detalhe com os fatos, **Tirar do álbum**, **Copiar texto**) | interface + nova chave de armazenamento só de apresentação (decidir) |
| DiarioLab | existe | os cenários prontos ficaram recolhidos em "Cenários prontos" (extra do app) | — |
| DiarioCatalogo | existe | as formas não vistas ficam em silhueta, mas o detalhe ainda mostra os stats (a CatNaoVisto esconde) | decisão |
| CatGrade, CatDesktop | parcial | contador "vistos N / 60" de todas as espécies, filtros por nível, **Buscar**, selo "SEU", ficha com a arte grande em listras (a ficha já fica ao lado no desktop) | interface |
| CatFicha | parcial | ficha com idle animado, "como se chega", técnica | interface |
| CatNaoVisto | parcial | ficha de forma não vista | interface |
| CatRivais | não existe | aba **Rivais** do catálogo (NPCs da campanha com vitórias) | interface |
| AssetsDiario | não existe | tiles do Explore (Catálogo, Laboratório, Registro) e placas de brasão no Diário | interface |

## Conversar

| prancha | estado | falta | precisa |
|---|---|---|---|
| UpConversar, ConvChat, ConvDesktop | existe | chips dos fatos citados em cada fala ("luta · T7", "memória · elogio"); **estrela** para guardar no álbum; botão do álbum no cabeçalho | interface (o log guarda os ids dos fatos) |
| ConvVerificador | não existe | folha do verificador ("mede, não troca a fala", afirmações sem base) com **Entendi** | interface |
| ConvEstados | parcial | estado "baixando o modelo" com progresso e **cancelar**; "estágio sem fala livre" | servidor (progresso do download) |
| ConvEstagios | — | referência de texto por estágio (não é tela) | — |

## Meus pets

| prancha | estado | falta | precisa |
|---|---|---|---|
| MpAtual | existe | selo "JÁ EXISTE" é marcação da prancha; Exportar registro é extra do app | — |
| UpParceiros, MpLista, MpDetalhe, MpTroca, MpDigitalizando, MpNovoOvo, MpImportar | proposta | vários pets com espaços, pet em espera congelado, troca, **Exportar / Importar** com conflito | save com vários pets = muda o formato/chave do save (decisão do Matheus) |

## Configurações

| prancha | estado | falta | precisa |
|---|---|---|---|
| CfgPrincipal | existe | cada linha abre o painel ali mesmo (a prancha abre uma tela por item); Som é proposta (linha desativada) | — |
| CfgAparencia | parcial | **tamanho do texto**, **reduzir movimento**, **mostrar dicas**, **Rever a primeira vez** | interface (preferência de tela) |
| CfgFala | parcial | **Testar** o modelo; chave "usar o modelo de linguagem"; descrição de cada modo | interface |
| CfgDados | parcial | **Exportar pet** (arquivo); Verificar/Copiar ficam no Registro | interface |
| CfgSobre | parcial | tela própria (versão, créditos) | interface |

## Primeira vez

| prancha | estado | falta | precisa |
|---|---|---|---|
| PvBoasVindas | existe | a frase "funciona sem internet" virou "o progresso fica neste navegador" (o jogo precisa do servidor local) | — |
| PvComoCuidar, PvComoEnsinar, PvComoCrescer | não existe | apresentação em 3 passos (**Pular**, **Próximo**, **Chocar meu ovo**) | interface |
| PvOvo | não existe | tela do ovo chocando | interface |
| PvChamado, PvEnsino, PvNavegacao | não existe | dicas na primeira vez (**Não mostrar dicas**, **Entendi**) | interface (preferência de tela) |
| PvVoltou | não existe | resumo "enquanto você esteve fora" | interface (dá para montar do registro) |

## Conexão

| prancha | estado | falta | precisa |
|---|---|---|---|
| OffErroSalvar | parcial | tela de erro com **Copiar registro / Tentar de novo** (hoje é um aviso no topo) | interface |
| OffRemoto | existe no servidor | — | — |
| OffEstados, OffJogando, OffSincronizando, OffConflito | proposta | sincronização entre aparelhos | servidor + save |

## Barra de navegação

Pet, Crescer, Lutar, Diário, **Conversar** (não está nas pranchas, mas fica: decisão do Matheus) e a engrenagem de
Configurações. Layout: celular abaixo de 900 px, barra lateral de 900 px, desktop das pranchas de 1100 px.
