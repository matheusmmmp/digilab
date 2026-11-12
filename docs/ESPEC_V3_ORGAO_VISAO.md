# ESPEC V3 — GOSTO_VISUAL, OV1: o órgão da visão (e do ouvido) do pet (2026-11-12, Claude Code, Opus 5.5)

**Status: revisada pelo Matheus; as OV1-1 a OV1-14 (seção 12) DECIDIDAS em 2026-11-12, pela recomendação** ("Eu aprovo todas as
recomendações e segue em diante"). Os números continuam PROPOSTOS; onde não há fonte, SEM FONTE. Esta espec é só papel: nenhum código,
nenhuma faixa, nenhuma vida, nenhum plano de análise; o código é a OV2. **Nenhuma alegação de novidade.**

**De onde vem:**
- a proposta `docs/futuro/fala_do_assistir.md`, seção 10 (o órgão, as FA-9 a FA-13, a tabela OV0/OV1) e 10.10 (os conceitos do Digimundo,
  as FA-14 a FA-20), com as direções do Matheus de 2026-11-11 já DECIDIDAS: o caminho A (o comentário nasce da percepção do pet; a LLM só dá
  voz e nunca vê a tela), o caminho B rejeitado, o órgão como módulo dedicado de visão computacional, sem léxico do pet, e os conceitos do
  corpus do Digimundo com uma mitologia em volta, "pelo menos como um estado";
- a frente `docs/TAREFA_V3_GOSTO_VISUAL.md`, até a GV3b: as duas runs (GV3, `docs/RESULTADO_V3_GOSTO_VISUAL.md`; GV3b,
  `docs/RESULTADO_V3_GOSTO_VISUAL_ENJOO.md`) são negativas, o gosto dos sete números não aparece nem como do genoma nem como do dono com 36
  unidades;
- **a busca OV0**, no vault: `DigiLab Research\DigiLab — Revisão de escopo\BUSCA_ORGAO_VISAO_2026-11-12.md` (as referências e os dados de
  modelo citados aqui vêm de lá, com o status dela; elas ainda não estão em `docs/referencias/`).

**O vocabulário** (o da 10 da proposta): o órgão **reconhece** rótulos de uma lista com uma confiança. O pet que "vê um gato" tem um
receptor aceso pelo órgão; não há nisso compreensão, prazer nem crença no sentido humano. "Acredita" (seção 6) é o nome de um registro
derivado do mito, não um estado mental.

**O que esta espec não muda:** `digilab/engine.py`, o cérebro A, o decodificador de hoje, a voz do jogo, a GV3/GV3b e as decisões já
tomadas. Tudo entra atrás de chave desligada (seção 10).

## 0. Em uma página

- **O órgão** é uma função de borda, no navegador, que recebe o quadro reduzido da tela, devolve pares (conceito, nível em 0 a 15) de uma
  **lista fixa e versionada** e descarta o quadro. Dentro do pet só entram os inteiros.
- **A lista** tem duas partes (seção 2): **24 conceitos genéricos** (18 na visão, 6 no som) e **as espécies do Digimundo**, a recomendação
  sendo as 56 que o `corpus.carregar()` deixa entrar.
- **O modelo recomendado** (seção 3) é o **SigLIP base** (`google/siglip-base-patch16-224`, apache-2.0): o único candidato pequeno e
  preciso da OV0 com licença limpa e sem ressalva de uso no card. Só o codificador de imagem vai ao navegador; os vetores de texto e os
  protótipos dos sprites se calculam uma vez.
- **A confiança** vira um inteiro na borda, por faixas fixas sobre a pontuação sigmoide; abaixo do corte, o conceito não sai (seção 4).
- **O evento** `percepcao_tela` leva só números e nomes da lista, no resumo de 10 s da GV-15 e só quando muda (seção 5). Nada sai da
  máquina.
- **No pet** (seções 6 a 8): cada conceito acende um receptor de percepção sem química. O M-SENS habitua **por conceito** (o molde da
  PE-11); o gosto por conceito é aprendido pela exposição e pela consequência do olhar; as espécies, além disso, dão um **termo de
  valência no M-AFETO pelo mito** (o patrono), só na decisão, nunca no corpo (D-MM-10 por analogia, como a culpa e a inveja da CO7).
- **A percepção e a crença ficam separadas** em todo lugar: no registro, no painel e na fala (seção 6.4).
- **A taxa:** uma classificação a cada 2 s reais, resumida pelo máximo da janela de 10 s (seção 5.2).
- **O painel** mostra em palavras, sem número: "viu", "gosta de", "enjoou de" e, noutra linha, "acredita" (seção 9).
- **Fora da primeira versão** (seção 11): o som dos nomes (FA-17), a acuidade no genoma (FA-12), o Piedmon e o Myotismon, os quadros de
  anime como referência, a fala (OV4), qualquer reconhecimento de pessoa ou leitura de texto.

## 1. O que já existe e o que vale

| peça | onde | o que serve aqui |
|---|---|---|
| a retina e a cóclea: os sete níveis | o evento `sentido_tela` (`digilab/events.py`, `fonte|n1|…|n7`, níveis 0 a 15); o `ResumoTela` (`digilab/tv.py`, a média de 10 s, o evento só na mudança, GV-15) | o molde do evento novo e do resumo |
| o órgão da tela no corpo | a `ConfigTela` (`digilab/config.py`): os receptores `tela_<canal>` e `novidade_tela`, a adaptação no corpo (GV-18) | fica como está; o órgão não mexe nos sete canais |
| o enjoo | a `ConfigEnjooTela` (o #875 no web e o enjoo no cérebro do Python): 6 protótipos parados, cada um com o seu enjoo; o receptor `enjoo_tela` | o molde do enjoo por conceito (seção 7.3) |
| a habituação por classe | `digilab/digibrain/sens.py`: `hab[c] <- hab[c] + mul(k_hab, visto_c × S - hab[c])` (PE-11); a classe `tela` (`CLASSE_TELA`) | o molde da habituação por conceito |
| o olhar e o gosto | a `ConfigOlhar` e o `GenomaVisao` (P1d): o agrado em pico, o alvo aprendido pela exposição (`tau_exposicao`), o termo `gosto` da unidade de olhar, o canal `gosto_visual` no r | o molde do gosto por conceito |
| a valência sem corpo | `digilab/digibrain/afeto.py`, `ler`: a culpa e a inveja da CO7 tiram só da valência desta decisão, sem mexer no V guardado nem no corpo (CO7-6, K-4) | o molde do termo mítico (seção 6) |
| o corpus das espécies | `digilab_fala_livre/corpus_especies.json` (`corpus-auditado-1`, sha256 `785f7834a2ee…`) e `digilab_fala_livre/corpus.py` | a lista das espécies (FA-14) |
| o brasão de cada espécie | `web/app/motor/nomes.ts`, `DIGIMON_DA_FORMA` (a chave da forma começa pela espécie do jogo: `brasa`, `cirro`, `ferrugem`, `limo`) e `NOME_ESP` (Coragem, Amizade, Conhecimento, Sinceridade) | o patrono de cada espécie (seção 6.1) |
| os deuses da mitologia | `web/app/motor/lendas_e1.ts`: `DEUSES` (coragem, amizade, conhecimento, sinceridade, diversao), os sinais de cada deus; a E2 (o Piedmon, a Diversão, D-MM-4) | o sentido mítico, sem mitologia nova |
| o catálogo de cenas da fala | `docs/PLANO_ANALISE_V3_GOSTO_VISUAL_FALA.md`, seção 3 (12 programas × 8 cenas, cada cena com os sete números e uma lista fixa de (conceito, confiança); é da GVFa, ainda não existe) | o mesmo catálogo serve à OV2 (OV1-11) |

## 2. A lista de conceitos (FA-10, FA-14): a proposta para o Matheus escolher

**A regra da lista:**
- **fixa e versionada** (`ov-lista-1`), com o sha256 no registro de cada vida; trocar a lista é uma versão nova da lista e do gabarito;
- **nenhum conceito identifica uma pessoa** (só `pessoa` e `rosto` como categorias, nunca quem é) **nem lê texto** (só `texto` como
  categoria; nenhum OCR);
- cada conceito genérico tem o texto da lista em inglês para o modelo (os prompts do SigLIP; a frase exata é da OV2, PROPOSTA) e o nome em
  português para o painel e a voz;
- **a ordem da lista** é a do desempate (como a regra I-a do `dec-v1`).

### 2.1 Os conceitos genéricos (PROPOSTA; 18 na visão e 6 no som)

| grupo | conceitos da visão | por que entra |
|---|---|---|
| bichos | `gato`, `cachorro`, `passaro`, `peixe`, `outro_bicho` | o pet é um bicho; os exemplos da FA-10; `outro_bicho` evita que um cavalo acenda `cachorro` |
| gente | `pessoa`, `rosto` | categorias da FA-10; **sensíveis** (seção 5.4) |
| comida e natureza | `comida`, `planta`, `agua`, `ceu` | o mundo do pet (a fruta, a ilha, o mar) |
| coisas | `carro`, `cidade` | o que o pet não tem na ilha (a novidade) |
| telas | `jogo`, `desenho_animado`, `texto`, `interface` | a tela de computador é cheia de texto e janelas (o ataque tipográfico da OV0, seção 1.3): `texto` e `interface` dão nome ao que mais aparece, para não virar `o_que_e` toda hora; `desenho_animado` separa o anime do resto |
| outro | `fogo` | a Coragem (seção 6) e um susto visual possível |

| conceitos do som (FA-17 adia os **nomes falados**, não estes) | as classes do AudioSet que entram (agrupadas) |
|---|---|
| `musica` | `Music` e as filhas |
| `fala` | `Speech` e as filhas (a categoria, nunca o conteúdo) |
| `risada` | `Laughter` |
| `latido` | `Bark`, `Dog` |
| `miado` | `Meow`, `Cat` |
| `estouro` | `Explosion`, `Bang` e parecidas (o agrupamento exato é da OV2) |

- **Os nomes do AudioSet** (Gemmeke et al. 2017, `10.1109/ICASSP.2017.7952261`, VERIFICADA [sem resumo] na OV0): a ontologia é CC BY-SA 4.0;
  o agrupamento derivado dela vai com a atribuição.
- **O tamanho:** 24, perto dos "20 + 8" da FA-10. Curta o bastante para a confiança do vocabulário aberto não se diluir; longa o bastante
  para a tela comum não cair sempre em `o_que_e`. O acerto de cada conceito no catálogo e numa bateria da tela real é da OV2 (seção 10).

### 2.2 As espécies do Digimundo (FA-14): só o que o `corpus.py` aceita

A tabela inteira das 60 espécies do jogo, com o que o carregador deixa entrar. **A contagem é desta espec**, feita com o
`corpus.carregar()` na `main` (`e0c2c474`) e um script fora do repositório; **não há artefato gravado**, e a OV2 a refaz num teste. As colunas:
- **entra:** se o `carregar()` devolve a espécie (pelo menos uma obra apta);
- **estrito:** os itens `VERIFICADO` ou `VERIFICADO EM OUTRA FONTE`, de obras aptas e com texto latino (traços / jeitos de falar /
  interações), isto é, o filtro estrito da FA-14, sem `PARCIAL` reescrito nem anime;
- **patrono:** o brasão da espécie no jogo (seção 6.1).

| espécie | nível | patrono (o brasão no jogo) | entra no `carregar()` | estrito (t / f / i) | algum item estrito |
|---|---|---|---|---|---|
| Tsunomon | In-Training | Amizade | sim | 0 / 1 / 0 | sim |
| Gabumon | Rookie | Amizade | sim | 3 / 2 / 1 | sim |
| Patamon | Rookie | Amizade | sim | 6 / 2 / 1 | sim |
| Angemon | Champion | Amizade | sim | 4 / 2 / 2 | sim |
| Aquilamon | Champion | Amizade | sim | 0 / 0 / 0 | não |
| Garurumon | Champion | Amizade | sim | 4 / 1 / 0 | sim |
| Gatomon | Champion | Amizade | sim | 5 / 2 / 1 | sim |
| Angewomon | Ultimate | Amizade | sim | 1 / 0 / 0 | sim |
| MagnaAngemon | Ultimate | Amizade | sim | 0 / 0 / 0 | não |
| Silphymon | Ultimate | Amizade | sim | 0 / 0 / 0 | não |
| WereGarurumon | Ultimate | Amizade | sim | 0 / 0 / 0 | não |
| Magnadramon | Mega | Amizade | sim | 0 / 0 / 0 | não |
| MetalGarurumon | Mega | Amizade | sim | 0 / 2 / 1 | sim |
| Seraphimon | Mega | Amizade | sim | 1 / 0 / 1 | sim |
| Valkyrimon | Mega | Amizade | **não** | 0 / 0 / 0 | não |
| DemiVeemon | In-Training | Conhecimento | **não** | 0 / 0 / 0 | não |
| Armadillomon | Rookie | Conhecimento | sim | 1 / 1 / 1 | sim |
| Veemon | Rookie | Conhecimento | sim | 8 / 4 / 4 | sim |
| Ankylomon | Champion | Conhecimento | sim | 0 / 0 / 0 | não |
| ExVeemon | Champion | Conhecimento | sim | 1 / 0 / 1 | sim |
| Gargomon | Champion | Conhecimento | sim | 1 / 1 / 0 | sim |
| Kabuterimon | Champion | Conhecimento | sim | 2 / 3 / 1 | sim |
| MegaKabuterimon | Ultimate | Conhecimento | sim | 1 / 0 / 1 | sim |
| Paildramon | Ultimate | Conhecimento | sim | 1 / 0 / 0 | sim |
| Rapidmon | Ultimate | Conhecimento | sim | 0 / 0 / 0 | não |
| Shakkoumon | Ultimate | Conhecimento | sim | 0 / 0 / 0 | não |
| HerculesKabuterimon | Mega | Conhecimento | sim | 0 / 0 / 1 | sim |
| Imperialdramon Dragon Mode | Mega | Conhecimento | sim | 2 / 1 / 0 | sim |
| MegaGargomon | Mega | Conhecimento | sim | 0 / 0 / 0 | não |
| SlashAngemon | Mega | Conhecimento | **não** | 0 / 0 / 0 | não |
| Koromon | In-Training | Coragem | sim | 1 / 0 / 1 | sim |
| Agumon | Rookie | Coragem | sim | 15 / 6 / 6 | sim |
| Guilmon | Rookie | Coragem | sim | 7 / 4 / 2 | sim |
| Birdramon | Champion | Coragem | sim | 6 / 1 / 1 | sim |
| Greymon | Champion | Coragem | sim | 6 / 3 / 1 | sim |
| Growlmon | Champion | Coragem | sim | 0 / 0 / 0 | não |
| Kyubimon | Champion | Coragem | sim | 1 / 0 / 1 | sim |
| Garudamon | Ultimate | Coragem | sim | 3 / 0 / 0 | sim |
| MetalGreymon | Ultimate | Coragem | sim | 6 / 2 / 1 | sim |
| Taomon | Ultimate | Coragem | sim | 4 / 3 / 2 | sim |
| WarGrowlmon | Ultimate | Coragem | sim | 1 / 0 / 0 | sim |
| Gallantmon | Mega | Coragem | sim | 0 / 0 / 0 | não |
| Phoenixmon | Mega | Coragem | sim | 4 / 0 / 0 | sim |
| Sakuyamon | Mega | Coragem | sim | 0 / 0 / 2 | sim |
| WarGreymon | Mega | Coragem | sim | 1 / 1 / 0 | sim |
| Tanemon | In-Training | Sinceridade | sim | 0 / 0 / 0 | não |
| Gomamon | Rookie | Sinceridade | sim | 3 / 0 / 0 | sim |
| Palmon | Rookie | Sinceridade | sim | 5 / 0 / 1 | sim |
| Ikkakumon | Champion | Sinceridade | sim | 1 / 1 / 1 | sim |
| Seadramon | Champion | Sinceridade | sim | 2 / 1 / 0 | sim |
| Stingmon | Champion | Sinceridade | sim | 0 / 0 / 1 | sim |
| Togemon | Champion | Sinceridade | sim | 2 / 0 / 1 | sim |
| DinoBeemon | Ultimate | Sinceridade | **não** | 0 / 0 / 0 | não |
| Lillymon | Ultimate | Sinceridade | sim | 0 / 0 / 1 | sim |
| MegaSeadramon | Ultimate | Sinceridade | sim | 1 / 0 / 2 | sim |
| Zudomon | Ultimate | Sinceridade | sim | 1 / 0 / 1 | sim |
| Imperialdramon Fighter Mode | Mega | Sinceridade | sim | 2 / 1 / 0 | sim |
| MetalSeadramon | Mega | Sinceridade | sim | 3 / 1 / 0 | sim |
| Rosemon | Mega | Sinceridade | sim | 8 / 2 / 3 | sim |
| Vikemon | Mega | Sinceridade | sim | 0 / 1 / 0 | sim |

**O resumo:**
- **56 entram** no `carregar()` (14 Amizade, 13 Conhecimento, 15 Coragem, 14 Sinceridade); **4 ficam fora** (Valkyrimon, DemiVeemon,
  SlashAngemon, DinoBeemon), por não terem nenhuma obra apta. É a mesma contagem da proposta, seção 10.10.1.
- **44 das 56 têm algum item estrito**; 12 não têm nenhum (Aquilamon, MagnaAngemon, Silphymon, WereGarurumon, Magnadramon, Ankylomon,
  Rapidmon, Shakkoumon, MegaGargomon, Growlmon, Gallantmon, Tanemon).
- **A recomendação (OV1-1):** a lista do órgão é a das **56** (a FA-14 pela recomendação). O patrono não depende do corpus (seção 6.1), então
  as 12 sem item estrito entram com o patrono e **sem traço** no sentido mítico. As 4 de fora ficam fora até uma entrada nova no corpus,
  auditada (o mesmo caminho do Piedmon e do Myotismon, FA-15).
- **O custo de as 4 ficarem fora:** um pet pode virar DemiVeemon (o bebê do Conhecimento) e não se reconhecer na TV. É o preço da regra do
  corpus; a alternativa, uma exceção sem auditoria, faz o corpus perder a regra.
- **Os pares difíceis** (o CLIP é fraco em grão fino, Radford et al. 2021, arXiv:2103.00020, VERIFICADA (preprint) na OV0): as duas
  Imperialdramon (Dragon Mode no Conhecimento, Fighter Mode na Sinceridade), a linha Garurumon/WereGarurumon/MetalGarurumon, a linha
  Gargomon/Rapidmon/MegaGargomon, Angemon/MagnaAngemon/Seraphimon. Eles formam um subconjunto da bateria (seção 10), com a confusão medida.

## 3. O modelo e onde roda (FA-9)

**A recomendação (OV1-2): o SigLIP base, só o codificador de imagem no navegador, por transformers.js sobre ONNX Runtime Web, WebGPU com
WASM de reserva.** As razões vêm da OV0 (seção 1):

| candidato | licença dos pesos (consulta de 2026-11-12) | zero-shot ImageNet (a fonte) | o codificador de imagem no navegador | a leitura |
|---|---|---|---|---|
| **SigLIP base** (`google/siglip-base-patch16-224`) | **apache-2.0**; o card sem ressalva de uso | 76,2 % (o artigo, arXiv:2303.15343) | 54,6 MB q4f16, 94,1 MB int8 (a conversão `Xenova/siglip-base-patch16-224`) | **o recomendado** |
| CLIP B/32 da OpenAI | sem campo de licença; **o card põe todo uso implantado fora do escopo** | 63,2 % (arXiv:2103.00020) | 53,3 MB q4f16 (`Xenova/clip-vit-base-patch32`, "mit" na conversão) | fora, pela ressalva |
| OpenCLIP B/32 da LAION | mit, **com a mesma ressalva no card** | — | — | fora, pela ressalva |
| MobileCLIP S0 da Apple | **apple-amlr**, só pesquisa | 67,8 % (README da Apple) | 11,8 MB int8 (`Xenova/mobileclip_s0`, licença "other", não conciliada) | fora: a licença não serve a um jogo |
| SigLIP 2 base | apache-2.0 | 78,2 % (arXiv:2502.14786) | a conversão ONNX q4f16 tem cerca de 497 MB no total | fora da v1: o texto multilíngue pesa; pode entrar depois só com o codificador de imagem |

- **O texto fica fora do navegador.** A lista é fixa: os vetores de texto dos 18 conceitos genéricos da visão e das 56 espécies se calculam
  **uma vez**, numa ferramenta fora do jogo, e vão como um arquivo pequeno com o sha256 do modelo e da lista. O jogo só carrega o
  codificador de imagem.
- **Os protótipos das espécies** (FA-16): os vetores dos sprites do atlas de clipes (`digilab_atlas_up_clipes.json`, o Idle) se calculam
  **no computador do usuário**, na primeira carga do órgão, e ficam no armazenamento local do navegador, fora do git e fora do save.
- **A conversão:** a da Xenova não declara licença. A recomendação é converter do original apache-2.0 numa ferramenta do repositório, ou
  usar a da Xenova com o sha256 registrado e a licença do original anotada (OV1-2).
- **O peso e a máquina:** o modelo carrega só com a chave do órgão ligada (seção 10), nunca numa run de pesquisa, e disputa a GPU com o
  `gemma2:9b`. **A latência no navegador não tem fonte** (OV0, seção 1.2): a taxa da seção 5.2 é PROPOSTA e a OV3 a mede numa máquina comum.
- **O som** (seção 2.1): um classificador do tipo YAMNet (o código Apache 2.0, conferido na OV0; **a licença dos pesos ficou sem fonte
  primária**). A escolha do modelo do som fica para a OV3, depois de conferida a licença dos pesos (OV1-3); a lista do som já fica aqui.

## 4. A regra da confiança

### 4.1 Da pontuação ao nível

O SigLIP dá uma pontuação por rótulo pela sigmoide, independente dos outros rótulos (o exemplo do card usa `torch.sigmoid` sobre os
logits). É o que o órgão quer: vários conceitos podem estar acesos juntos, e nenhum aceso quer dizer "nada da lista".

- **Os genéricos:** `p_c = sigmoide(logit_c)`, o logit do quadro contra o vetor de texto do conceito.
- **As espécies** (a forma texto + protótipo, do tipo Tip-Adapter, Zhang et al. 2022, arXiv:2111.03930, VERIFICADA (preprint) na OV0):
  `logit_e = logit_texto_e + α × logit_proto_e`, com o `logit_proto_e` a semelhança máxima entre o quadro e os protótipos dos sprites da
  espécie, na mesma escala do logit de texto. `α` PROPOSTO, SEM FONTE, calibrado na bateria (seção 10). Sem treino e sem ajuste do modelo
  (o artigo do CLIP: adaptar a um domínio tira robustez a estilo).
- **O nível inteiro** em 0 a 15, por uma regra fixa na borda: `n_c = clamp(floor(16 × (p_c − p_min) / (p_max − p_min)), 0, 15)`, com
  `p_min` e `p_max` **por grupo** (genéricos da visão, espécies, som), fixados na calibração com o catálogo e a bateria e gravados na
  versão da lista. Dentro do pet só entra o `n_c`. PROPOSTO.
- **O corte de saída:** só sai um conceito com `n_c ≥ 4` (PROPOSTO, SEM FONTE). A rejeição pelo máximo da pontuação tem apoio em Vaze et
  al. 2022 (arXiv:2110.06207, VERIFICADA (preprint) na OV0): é uma linha de base forte quando o acerto no conjunto fechado é bom.
- **No máximo k = 3 conceitos** por evento, os de maior nível, com a ordem da lista no empate (a 10.5 da proposta).
- **As palavras da confiança** (painel e voz): `n ≥ 10` é "certo"; `4 ≤ n ≤ 9` é "acho". PROPOSTO.

### 4.2 O que nunca sai da função

O quadro, o vetor do quadro, as pontuações em float, os conceitos abaixo do corte e, no som, o áudio e qualquer transcrição. A função de
borda devolve só a lista de (conceito, `n_c`) e o `o_que_e` não é dela: "nada reconhecido" é a ausência de conceito, e quem o lê é o cérebro
(seção 7.4).

## 5. O evento no log, a taxa e a privacidade (GV-10, GV-15, FA-11)

### 5.1 O evento `percepcao_tela` (PROPOSTO)

- **O formato** do valor, no molde do `sentido_tela`: `fonte|lista|c1:n1|c2:n2|c3:n3`, com a `fonte` em `tela` ou `tv`, a `lista` a versão
  (`ov-lista-1`), cada `c` um nome da lista e cada `n` em 4 a 15; de zero a três pares. **Só números e nomes da lista.**
- **Falha alto:** um evento com conceito fora da lista, nível fora de 4 a 15, mais de três pares, par repetido, versão de lista
  desconhecida, ou num motor sem a chave do órgão, levanta erro (a regra do `CLAUDE.md`). O replay lê o evento; o motor nunca roda o
  modelo.
- **A versão do modelo** não vai em cada evento: a `ov-lista-1` fixa o sha256 do modelo, dos vetores de texto, das faixas `p_min`/`p_max` e
  do `α`. Um modelo novo é uma lista nova.
- **O par com o `sentido_tela`:** os dois saem da mesma janela de 10 s, mas são independentes. Um `percepcao_tela` sem conceito
  (`tela|ov-lista-1`) apaga a percepção anterior.

### 5.2 A taxa (FA-11)

- **Uma classificação a cada 2 s reais** enquanto a captura está ligada (PROPOSTO, SEM FONTE; a latência no navegador é da OV3).
- **O resumo da janela de 10 s** (as 5 classificações): **o máximo** do nível de cada conceito, não a média. Um gato que passa 3 s ainda
  aparece; a média o apagaria. PROPOSTO (OV1-6).
- **O evento só quando o conjunto ou algum nível muda**, como a GV-15.

### 5.3 O tamanho (a conta à vista, SEM FONTE como estimativa)

Um evento com três pares, `tela|ov-lista-1|gato:12|pessoa:7|texto:4`, tem uns 37 caracteres no valor; com o resto da linha do `para_jsonl`,
uns 95 bytes (contra os 74 do `sentido_tela`, conferidos na `ESPEC_GOSTO_VISUAL_P1.md`). No pior caso, um por janela: 360 por hora, cerca de
**34 KB por hora de tela**; numa tela parada, perto de 0. Somado ao `sentido_tela` (até 27 KB), o teto fica perto de 61 KB por hora, cerca de
80 horas de tela em 5 MB (o limite usual do `localStorage`, de ordem de grandeza).

### 5.4 A privacidade (a ressalva da 10.2 da proposta)

- **Nada sai da máquina:** nenhum quadro, áudio, vetor, pontuação ou conceito vai à rede, ao servidor local ou à LLM como dado da captura.
- **O que fica no log local muda:** além dos sete números, os conceitos. `rosto`, `pessoa`, `texto` e `interface` frequentes dizem o que o
  usuário faz no computador. Por isso:
  - a lista não tem nenhum conceito de identidade nem de conteúdo de texto (seção 2);
  - **a recomendação (OV1-7):** os conceitos `pessoa`, `rosto`, `texto` e `interface` **não entram no log da tela real** (fonte `tela`) na
    primeira versão: o órgão os reconhece, mas eles só valem com a fonte `tv` (a TV do jogo) e no catálogo. Com a fonte `tela`, saem do evento.
    O custo: o pet não "vê" gente nem texto na tela do Matheus;
  - a captura continua ligada a cada sessão e anunciada (GV-10), e a revisão de privacidade da GV5 inclui o órgão antes da tela real.

## 6. O sentido mítico e a crença (FA-15, FA-18, FA-19; D-MM)

### 6.1 O patrono de cada espécie: o brasão que o jogo já dá

**A recomendação (OV1-4):** o sentido mítico de cada espécie é **o patrono = o brasão da espécie no jogo**: a espécie do jogo que a carrega
no `DIGIMON_DA_FORMA` (`brasa` → Coragem, `cirro` → Amizade, `ferrugem` → Conhecimento, `limo` → Sinceridade). Por quê:
- **não cria mitologia nova** (o risco "duas mitologias" da 10.10.6): os quatro brasões são os quatro primeiros deuses do aro (`DEUSES`, a
  E1), com os mesmos nomes na tela (`NOME_ESP`, `NOME_DEUS`);
- **não depende do corpus:** é um fato do jogo, não da obra, e por isso não pode ser dito como fato da obra (seção 6.4);
- **é igual no Python e no web,** sem portar as lendas ao Python (o mapa é uma tabela de 60 linhas, conferida por teste contra o `nomes.ts`);
- **a Diversão fica sem espécie** na lista: o deus da Diversão é encarnado pelo Piedmon (D-MM-4), que não está no corpus (FA-15). O
  Myotismon, fora do aro, também não.

**O que o corpus acrescenta, sem virar fato:** para as 44 espécies com item estrito, até um traço estrito pode acompanhar o patrono como
**tom** para a voz (a regra do `bloco_estilo`: não sustenta afirmação). As 12 sem item estrito ficam só com o patrono. O mapa final, e se a
frente MITOLOGIA quer outro patrono para alguma espécie, é da frente MITOLOGIA e do Matheus (FA-15); esta espec só propõe a regra de
partida.

### 6.2 O sinal da valência: o parentesco (a primeira versão)

O termo mítico tem um sinal por (pet, espécie vista). **A recomendação (OV1-5), a regra mais simples que é função pura do pet:**
- `+1` quando o patrono da espécie vista é o brasão do próprio pet (o pet "vê um dos seus": um Agumon na TV para um pet da Coragem);
- `0` nos outros brasões, na primeira versão (nenhum deus "inimigo": a mitologia da E1 não tem deuses em conflito, e inventar um seria
  mitologia nova).

**A alternativa adiada:** o sinal pela história do pet com os sinais daquele deus (as vezes em que viu a chama da Coragem, a E1). É mais
rica, mas os sinais existem só no web (`lendas_e1.ts`, função pura da tela), e pô-la no cérebro pede portar as lendas ao Python com
paridade. Fica para depois, se a primeira versão servir.

### 6.3 O estado no afeto, nunca no corpo (FA-18)

No molde da culpa e da inveja da CO7 (`afeto.py`, `ler`):
- **o termo entra só na valência desta decisão** (o V que o M-IMPULSO lê), sem mexer no V guardado, na excitação nem no corpo;
- `termo_mito = div_arred(peso_mito × sinal × n_e × (S − hab_e), 15 × S)`, com `n_e` o nível da espécie no último `percepcao_tela`
  enquanto o pet olha, e `hab_e` a habituação da espécie no M-SENS (seção 7.2): o mesmo Agumon visto muitas vezes pesa menos;
- `peso_mito = S/8` (PROPOSTO, SEM FONTE): bem abaixo da culpa e da inveja, para o mito colorir a decisão e não a dirigir;
- só com o pet olhando a TV (`olhar.olhava`) e só para espécies acima do corte;
- **nenhum emissor químico**, nenhuma adaptação no corpo, nenhum stat da luta: a D-MM-10 por analogia não reabre.

**O que isso entrega ao pedido:** "pelo menos como um estado". O estado é o registro `mito_visto` (a última espécie, o patrono e o termo)
no `estado_interno` do M-AFETO, que o painel lê (seção 9) e a pesquisa mede.

### 6.4 A separação entre o que o órgão percebe e a crença (FA-19)

| camada | o que é | onde fica | como se diz |
|---|---|---|---|
| **a percepção** | o órgão reconheceu a espécie com um nível | o `percepcao_tela` no log; o receptor `ver_<conceito>` | "é o Agumon!" (certo); "acho que é o Agumon" (acho) |
| **a crença** | o patrono da espécie e o termo de valência | a tabela fixa (seção 6.1) e o `mito_visto` no M-AFETO | "dizem que ele é da Coragem"; "acho que é sinal da Coragem" — sempre como crença |

- Nunca as duas numa frase só do painel; a crença dita como fato conta como sem sustento no verificador da fala (FA-8, FA-19).
- **A pesquisa** mede as duas camadas em separado: o que vem do receptor (o gosto e a habituação por conceito, seção 7) e o que vem do
  termo mítico (a valência), cada um com a sua chave (seção 10).

## 7. O pet: os receptores, o M-SENS por conceito e o gosto

### 7.1 Os receptores de percepção (G-RECEPTOR)

- **Um receptor por conceito da lista**, `ver_<conceito>` na visão e `ouvir_<conceito>` no som (nomes PROPOSTOS; para as espécies,
  `ver_<id>` com um id sem espaço e sem acento, como `ver_imperialdramon_dragon`). O valor é `div_arred(n × S, 15)` do último
  `percepcao_tela` enquanto o pet olha, e 0 sem olhar.
- **Sem dinâmica no corpo:** o receptor de percepção é a leitura do evento, não um químico; não tem adaptação nem emissor. Isso difere do
  desenho da 10.4 da proposta ("um receptor e um químico de adaptação por conceito") e é a OV1-8. Por quê: 80 conceitos com 80 químicos de
  adaptação pesam no tick (a GV-18 já citava o custo de 14), e a habituação por categoria tem lugar natural no M-SENS, que já habitua por
  classe (PE-11).
- **O corpo não muda** com a percepção: o tédio, a curiosidade, o humor, o estresse e o susto da tela continuam vindo só dos sete números
  (a P1b e o enjoo). O conceito muda o cérebro, não a química.

### 7.2 A habituação e a novidade por conceito no M-SENS

- **Um integrador por conceito**, no molde da PE-11: `hab_c <- hab_c + mul(k_hab_c, a_c − hab_c)`, com `a_c = div_arred(n_c × S, 15)`
  olhando e `a_c = 0` sem olhar ou com o conceito apagado. A novidade do conceito na decisão é `nov_c = S − hab_c`, lida antes de a
  habituação andar (a regra de hoje).
- **Duas velocidades** (PROPOSTAS), no molde do enjoo do #875: sobe com uma meia-vida curta olhando (uma decisão, 15 ticks) e volta com uma
  longa sem ver o conceito (meio dia de jogo, 720 ticks). Assim "voltar ao gato" não desenjoa de imediato.
- **A especificidade e a generalização** (Rankin et al. 2009, `10.1016/j.nlm.2008.09.012`, VERIFICADA na OV0, características 7 e 8): a
  habituação do conceito é mais larga que a do protótipo de sete números (o enjoo de hoje) e mais estreita que a da classe `tela`. Os três
  ficam: o órgão não substitui o enjoo.
- **A primeira versão não generaliza entre conceitos** (gato não habitua cachorro). A generalização graduada que a literatura sugere
  (Quinn et al. 1993, `10.1068/p220463`; Gordon e Holyoak 1983, `10.1037/0022-3514.45.3.492`, ambas VERIFICADAS na OV0) fica fora (seção 11).

### 7.3 O gosto por conceito: a exposição e a consequência

- **Um traço de gosto por conceito,** `g_c` em [−S, S], que nasce 0 (todo aprendido; a FA-12 adia o inato por conceito).
- **A exposição** (a mera exposição de Zajonc 1968, `10.1037/h0025848`, na nota antecessora; a generalização à categoria de Gordon e
  Holyoak 1983): olhando, `g_c` anda devagar para cima na proporção de `a_c`, com saturação, como o alvo aprendido da P1d anda com o
  `tau_exposicao` (dois dias de jogo) e satura pelo enjoo (o U invertido da `ConfigEnjooTela`). Depois da saturação, a exposição vira
  habituação (7.2), não mais gosto.
- **A consequência** (o P1 do M-PLAST, a GV-8): no fim de uma opção de olhar, o `r_n` da consequência dá crédito a cada conceito visto,
  na proporção de `a_c`: `g_c <- g_c + mul(k_cons, mul(a_c, r_n))`. O gato que estava na tela antes de um carinho ganha.
- **O agrado do olhar** passa a somar o termo dos conceitos: `agrado' = agrado_retina + Σ_c div_arred(a_c × g_c × nov_c, S × S)`, cortado em
  [0, S]. O termo `gosto` da unidade de olhar e o canal `gosto_visual` no r leem o `agrado'`. Desligado, `agrado' = agrado_retina` (byte a
  byte).
- **Os números** (`k_exp`, `k_cons`, a saturação, as meias-vidas) são PROPOSTOS, SEM FONTE, e vão à `ConfigOrgao` (seção 10).
- **A leitura das GV3 negativas:** o gosto pelos sete números não apareceu com 36 unidades. O gosto por conceito é outro mecanismo e não
  herda nem o resultado negativo nem uma expectativa positiva; ele pede o seu plano de análise (seção 10).

### 7.4 O `o_que_e` e o enjoo de conceito na fala (a ligação com a FA-2)

- `o_que_e`: a novidade da retina alta (`novidade_tela ≥ S/2`) **e** nenhum conceito aceso acima do corte: o pet viu algo que o órgão não
  reconhece.
- `chato` com alvo: o conceito mais habituado entre os acesos (`hab_c ≥ 7S/8`) enquanto o pet ainda olha.
- `gostei` com alvo: o conceito de maior `a_c × g_c` quando o agrado passa do limiar.
- Os limiares são da FA-2 e do decodificador do assistir (a GVFa); a fala é da OV4.

## 8. O M-SENS por conceito: o contrato

O que o M-SENS entrega aos outros módulos, com a chave do órgão ligada (desligada, nada disso existe e o M-SENS é o de hoje):

| campo | o que é | quem lê |
|---|---|---|
| `percepcao` | a lista (conceito, `a_c`) acesa nesta decisão, só olhando | o M-AFETO (o termo mítico), o M-PLAST (o crédito), o decodificador |
| `nov_conceito` | `S − hab_c` de cada conceito aceso, antes de andar | a unidade de olhar (a novidade por conceito soma ao `w0_nov`), o decodificador |
| `hab_conceito` | o integrador de cada conceito da lista (todos, acesos ou não) | o `estado_interno`, o painel |
| `gosto_conceito` | o `g_c` de cada conceito | o agrado do olhar, o painel |

- **A G-RECEPTOR fica:** o M-SENS só lê os receptores `ver_*`/`ouvir_*`; nada do evento chega ao cérebro por outro caminho.
- **Falha alto:** um receptor de percepção sem a chave, um receptor fora da lista, ou a lista mudando no meio da vida levantam erro (como os
  receptores da tela hoje, `sens.py`, `_receptores`).
- **O custo:** um integrador e um traço por conceito, 80 de cada (24 + 56), em inteiros. Sem rng.

## 9. O painel em palavras (FA-13)

Sem número nenhum, no espírito da D-MM-8:
- **"viu:"** os conceitos acesos agora, com a palavra da confiança: "viu: um gato (certo), acho que uma pessoa";
- **"gosta de:"** até 3 conceitos de `g_c` mais alto, só os acima de um corte (PROPOSTO); **"enjoou de:"** até 3 de `hab_c` mais alto;
- **"aprendeu a gostar por:"** a exposição ou a consequência, separadas como na GV-14 (o painel do paladar de hoje);
- **"acredita:"** noutra linha, só para espécies: "acredita: o Agumon é da Coragem, como ele" (o parentesco); nunca na mesma linha do "viu";
- **com a fonte `tela`**, os conceitos sensíveis da OV1-7 não aparecem.

O painel lê o `estado_interno` do pet refeito do log (função pura), como o painel da TV de hoje.

## 10. As garantias e as etapas

- **A chave:** `ConfigOrgao` (`ligada: bool = False`, a lista, os números da seção 7), uma subchave do olhar: exige a `ConfigOlhar` e a TV.
  O termo mítico tem a sua própria subchave (`mito: bool = False`), para a pesquisa separar percepção e crença.
- **Desligada, byte a byte:** o gabarito das vidas de hoje (P1d, o enjoo, a v32) é gravado num commit próprio antes da mudança, e um teste
  confere.
- **O determinismo:** o Python nunca roda modelo (só biblioteca padrão no `digilab/`). Nas runs e na paridade, os conceitos vêm do
  **catálogo de cenas** com (conceito, nível) fixos por cena; a recomendação (OV1-11) é **um catálogo só**, o da GVFa
  (`PLANO_ANALISE_V3_GOSTO_VISUAL_FALA.md`, seção 3), estendido: cada cena ganha a lista do órgão, e a TV da grade (`digilab/tv.py`) sorteia
  a lista de cada cena por uma **rng própria** (`tv-conceitos`, por `derivar_semente`), sem consumir a `tv-programas` (a grade de hoje não
  muda).
- **O modo livre não vale para resultado:** o que o órgão reconhece na tela real nunca entra numa medida (a regra do `CLAUDE.md`).
- **A paridade Python/web** no catálogo, com gabarito, como a TV de hoje; **nenhuma paridade sobre a saída do modelo** (o determinismo entre
  GPUs não tem fonte, OV0).
- **A bateria de acerto** (a 10.10.2 e a 10.7 da proposta), **local, fora do git**, antes da tela real: quadros de sprite e de anime por
  espécie, os pares difíceis da seção 2.2, negativos (anime sem nenhuma das 56, telas comuns) e capturas de tela comuns para os genéricos.
  O acerto por estilo (sprite × anime), a confusão dos pares e a taxa de falso positivo nos negativos, em separado. Os quadros de anime nunca
  vão ao git nem ao pacote do jogo (FA-16). **Nenhuma fonte diz que acerto esperar** (a OV0, seção 3): o número que torna o órgão apto é
  PROPOSTO na OV3, antes de olhar a bateria.
- **Um plano de análise** antes de qualquer vida com a chave (a regra do método), com faixa nova pedida ao coordenador.

| etapa | o quê | depende de | código |
|---|---|---|---|
| **OV2** | o Python atrás da `ConfigOrgao` desligada: o gabarito antes; o evento `percepcao_tela`; os receptores `ver_*`; o M-SENS por conceito; o gosto por conceito; o termo mítico atrás da subchave `mito`; a tabela do patrono conferida contra o `nomes.ts`; o catálogo com a rng `tv-conceitos`; a contagem do corpus num teste | OV1 revisada; as decisões da seção 12 | sim |
| **OV3** | o web com paridade no catálogo; a ferramenta que calcula os vetores de texto; o órgão no navegador (o codificador de imagem, os protótipos dos sprites no armazenamento local) gravando o evento no modo livre; a medida da latência; a bateria local e o número de aptidão escrito antes | OV2 | sim |
| **OV4** | a fala com os conceitos percebidos (FA-7, FA-8) e o painel (seção 9); a revisão de privacidade da GV5 com o órgão | OV3; a DC5 | sim |

## 11. O que fica fora da primeira versão

- **os nomes falados** ("Agumon!") e todo reconhecimento de fala (FA-17): depois da visão e da revisão de privacidade; a OV0 mostra que o
  Whisper tiny erra muito em japonês (CER 36 a 37 % em fala corrida, o artigo, apêndice D.2) e que nomes raros pedem viés ou palavra-chave;
- **a acuidade no genoma e o gosto inato por conceito** (FA-12);
- **o Piedmon, o Myotismon e as 4 espécies fora do corpus** (FA-15), até uma entrada auditada;
- **os quadros de anime como referência** (FA-16): só na bateria, local;
- **o sinal mítico pela história com os sinais dos deuses** (seção 6.2);
- **a generalização entre conceitos vizinhos** (seção 7.2);
- **a fala** (OV4) e o limite de frequência dela (FA-5);
- **o grupo** (dois pets olhando a mesma TV);
- **onde está o conceito no quadro** (caixa, posição), quantos são, e qualquer identificação de pessoa ou leitura de texto;
- **a lista aberta** (o dono escrevendo conceitos): devolveria ao pet o gosto do dono (GV-3);
- **o SigLIP 2 e os modelos de licença de pesquisa.**

## 12. As decisões do Matheus (todas DECIDIDAS em 2026-11-12, pela recomendação)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **OV1-1** | Quais espécies entram (FA-14). | **As 56 do `carregar()`**; as 12 sem item estrito entram com o patrono e sem traço; as 4 de fora esperam uma entrada auditada. | Com só as 44 de item estrito, somem 12 espécies sem razão de percepção (o patrono não depende do corpus). Com as 60, entram 4 sem nenhuma obra apta, e o corpus perde a regra. |
| **OV1-2** | O modelo da visão (FA-9). | **O SigLIP base, só o codificador de imagem no navegador** (54,6 a 94,1 MB), os vetores de texto calculados fora; a conversão registrada com sha256 e a licença do original. | Com o CLIP da OpenAI ou o da LAION, o jogo usa pesos cujo card põe todo uso implantado fora do escopo. Com o MobileCLIP, pesos de licença de pesquisa num jogo. Com um modelo maior, o órgão disputa a GPU com o `gemma2:9b` e amostra menos. |
| **OV1-3** | O modelo do som. | **Escolher na OV3,** depois de conferida a licença dos pesos do YAMNet (sem fonte primária na OV0); a lista do som já fica aqui. | Escolher agora, sem a licença dos pesos, pode pôr no jogo pesos que não podem ir. Adiar demais deixa o pet surdo a `risada` e `musica`, que não têm o risco dos nomes. |
| **OV1-4** | O sentido mítico (FA-15). | **O patrono = o brasão da espécie no jogo**; a Diversão e o Myotismon sem espécie; a frente MITOLOGIA pode mudar o mapa, o Matheus decide. | Um mapa novo, feito aqui, cria uma segunda mitologia. O brasão é um fato do jogo, e o pet do mesmo brasão vê "um dos seus"; se a MITOLOGIA quiser outro patrono para alguma espécie, é uma linha a trocar na tabela, com versão nova. |
| **OV1-5** | O sinal da valência. | **O parentesco:** +1 para o patrono igual ao brasão do pet, 0 nos outros, na primeira versão. | A história com os sinais é mais rica, mas pede portar as lendas ao Python com paridade antes de saber se o termo serve. Com sinais negativos, nasce um conflito entre deuses que a mitologia não tem. |
| **OV1-6** | O resumo da janela de 10 s. | **O máximo** do nível de cada conceito nas 5 classificações. | Com a média, o que passa por 3 s some; com o máximo, um quadro errado isolado vira percepção por 10 s (o corte de nível segura parte disso). |
| **OV1-7** | Os conceitos sensíveis na tela real. | **`pessoa`, `rosto`, `texto` e `interface` fora do evento com a fonte `tela`** na primeira versão; valem na TV do jogo e no catálogo. | Com eles no log da tela real, o log diz quando o usuário está em chamada, lendo ou trabalhando. Sem eles, o pet não vê gente nem texto na tela do Matheus, e a tela comum cai mais vezes em `o_que_e`. |
| **OV1-8** | Onde fica a habituação por conceito. | **No M-SENS** (um integrador por conceito, duas velocidades), com o receptor de percepção sem química; o corpo só muda pelos sete números. | No corpo, 80 químicos de adaptação novos pesam no tick e a percepção vira química (para as espécies, contra a D-MM-10 por analogia). No M-SENS, o "efeito biológico" do conceito fica só no cérebro. |
| **OV1-9** | O gosto por conceito. | **Todo aprendido, pela exposição com saturação e pela consequência do olhar,** somado ao agrado da retina. | Só a exposição: o pet gosta do que o dono mais mostra (o risco da GV-3, o gosto do dono). Só a consequência: o gosto depende de o dono acertar o momento. Com o inato, a medida genoma × dono mistura o que o pet percebe com o que ele gosta (FA-12). |
| **OV1-10** | O peso do termo mítico. | **`peso_mito = S/8`,** só na valência da decisão, habituado pela espécie. | Alto, o pet persegue a TV por mito, e a crença dirige o comportamento. Baixo demais, o "pelo menos como um estado" vira só um registro sem efeito; a subchave `mito` permite medir os dois. |
| **OV1-11** | O catálogo de cenas. | **Um catálogo só, o da GVFa, estendido** com a lista do órgão; a TV da grade sorteia a lista por cena com a rng `tv-conceitos`. | Dois catálogos dão duas verdades sobre a mesma cena, e a fala e o cérebro deixam de ser comparáveis. Sortear com a `tv-programas` mudaria a grade de hoje e o gabarito. |
| **OV1-12** | O corte e as palavras da confiança. | **Sai com `n ≥ 4`; "certo" com `n ≥ 10`, "acho" de 4 a 9**, com as faixas `p_min`/`p_max` por grupo calibradas no catálogo e na bateria. | Um corte baixo enche a fala de "acho que é…" errados; alto, o pet quase nunca vê nada e a queixa "não identifica nada" volta. |
| **OV1-13** | A lista genérica. | **Os 24 da seção 2.1** (18 na visão, 6 no som), com `texto`, `interface` e `desenho_animado` para a tela de computador. | Sem os conceitos de tela, a tela comum vira `o_que_e` ou acende o conceito errado pelo texto escrito (o ataque tipográfico). Com uma lista maior, a confiança dilui e o painel enche. |
| **OV1-14** | O nome e o lugar desta espec. | **`docs/ESPEC_V3_ORGAO_VISAO.md`,** dentro da frente GOSTO_VISUAL, sem tarefa nova; a busca no vault. | Uma frente nova separaria o órgão da TV e do gosto, que ele usa; dentro da GOSTO_VISUAL, a tarefa fica longa. |

## 13. Os riscos

- **O reconhecimento errado vira percepção errada** (a 10.7 da proposta): o corte, as palavras da confiança, a bateria antes da tela real.
- **O ataque tipográfico na tela:** o `texto` e a `interface` na lista; a medida em capturas de tela comuns na bateria.
- **O domínio sprite × anime:** nenhuma fonte diz o acerto; a bateria separa por estilo; a confiança baixa vira dúvida.
- **Os vieses do modelo viram o "olhar" do pet:** o painel separa o percebido do gostado; a lista curta e fixa limita o alcance.
- **A licença muda:** a decisão final registra a licença e o sha256 dos pesos no dia.
- **O mito dito como fato:** a separação da 6.4 e a rubrica do verificador.
- **O escopo:** três etapas de código, cada uma com PR próprio e a sua chave; nada antes da revisão do Matheus.
