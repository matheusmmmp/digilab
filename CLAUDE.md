# CLAUDE.md — Digilab

Contexto para o Claude Code. Leia inteiro antes de mexer em qualquer coisa.

## O que é

Pesquisa de mestrado paralela do Matheus (PPGCC/UFSC): um **pet virtual evolutivo e
competitivo com IA**, inspirado conceitualmente em Tamagotchi/Digimon. O dono treina o pet
por feedback; o pet tem memória/traços persistentes; pets treinados por donos diferentes
competem numa arena.

A hipótese científica central, testada **em simulação pura, sem humanos**:
> treino por um dono coerente produz um pet melhor que feedback aleatório com o mesmo volume de interação.

Se isso não se sustentar, o produto continua válido como jogo, mas a hipótese precisa ser reescrita.

## Regras do projeto — não negociáveis

- **Não aumentar escopo.** Nada de combate novo, multiplayer, LLM, interface gráfica ou modelos
  novos fora do que a tarefa pede.
- **Falhar alto, não em silêncio.** `raise` em vez de `dropna`, valor default ou `except: pass`.
  Evento desconhecido no log levanta erro.
- **Determinismo é requisito.** Mesma semente + mesmo log = mesmo resultado, até o último float.
  Se um teste de replay quebrar, pare tudo e conserte antes de qualquer outra coisa.
- **RNG de ambiente e de política separadas.** Trocar de política não pode mudar o clima do mundo.
- **Métricas existem uma vez só** (`digilab/metrics.py`) e são compartilhadas por todos os braços.
- **Nenhum número em resultado sem artefato em disco que o produza.**
- **Parâmetros ficam em `digilab/config.py`.** Nenhum número mágico espalhado.
- **`digilab/engine.py` não muda.** O sha256 dele está congelado em `protocol.py`
  (`ENGINE_SHA256_V0`); teste e preflight conferem.
- Português nos comentários e docstrings, **sem acentos em identificadores**.
- Só biblioteca padrão no pacote `digilab/` (o preflight verifica por AST). `pytest` só para testes.

## Arquitetura — três camadas com velocidades diferentes

1. **Estado e necessidades** (`state.py`) — determinístico, escrito à mão. É o ambiente, não o
   agente. Nunca aprende.
2. **Política de comportamento** (`policy.py`, `policies/`) — escolhe a ação do pet. Aprendizado
   entra aqui como troca de classe sob o `Protocol` `Politica` (`agir`, `observar`, `estado_interno`).
3. **Traços e evolução** (`tracos.py`) — EMA lenta da distribuição de ações. Lento de propósito:
   é o que impede persona drift. Hoje é a versão mínima que a arena precisa.

Event sourcing: o estado do pet **nunca é salvo**; só o log (ações do usuário + avanços de
tempo). A vida é reconstruída reprocessando o log.

## Mapa do repositório

| caminho | papel |
|---|---|
| `digilab/config.py` | todos os parâmetros (v0 + `ConfigBandit`, `ConfigDonos`, `ConfigTracos`, `ConfigArena`, `ConfigMetricas`) |
| `digilab/events.py`, `state.py`, `policy.py`, `engine.py` | v0: motor, log, `PoliticaInstinto` |
| `digilab/protocol.py` | protocolo congelado `PROTOCOLO_ARENA_V1`; cada campo DECIDIDO/PROPOSTO; hash cobre protocolo + configs + engine |
| `digilab/donos.py` | donos sintéticos: atencioso, relapso, aleatório (controle crítico), incoerente |
| `digilab/treino.py` | `CanalDeInteracao` impõe orçamento exato; `MotorComFeedback` (subclasse, só sobrescreve `_aplicar_acao_usuario`); `reproduzir_com_feedback`; `simular_vida` |
| `digilab/policies/bandit.py` | Thompson sampling linear; prior = distribuição exata da `PoliticaInstinto` via sonda de rng + Gumbel-max |
| `digilab/tracos.py` | camada 3 mínima |
| `digilab/arena.py` | 5 ações em ciclo (cada uma vence 2, perde 2); stats = afinidades soma-zero dos traços; disposição herdada da política; arena nunca chama `observar()` |
| `digilab/metrics.py` | taxa de vitória, Bradley-Terry (erro padrão projetado em soma-zero), JSD com números aleatórios comuns, bootstrap |
| `experiments/run_arena.py` | orquestrador: preflight → vidas → replay do disco → torneio → replay do disco → métricas → gate |
| `experiments/configs/` | `canonico.json` (o portão) e `fumaca.json` (NÃO canônico) |
| `artifacts/` | saída da run canônica (evidência; não editar à mão) |
| `web/digilab.html` | versão web jogável (porte JS; ver abaixo) |
| `tests/` | 56 testes |

## Comandos

```bash
python -m pytest tests/ -q                                                   # 56 testes, ~10 s
python experiments/run_arena.py --config experiments/configs/canonico.json   # portão, ~2 min; rc 0 APROVADA / 2 REPROVADA
python experiments/run_arena.py --config experiments/configs/fumaca.json     # fumaça, rápido, não canônico
python run_demo.py                                                            # demo do v0
```

Ambiente do usuário: Windows, pasta `D:\Trab\digilab\v1`. Python 3.10+.

## Estado atual (run canônica em `artifacts/`, protocolo `adce99fc3fdc…`)

Números abaixo vêm de `artifacts/metrics.json` e `artifacts/divergence.json`. Se reproduzir a
run, confira contra esses arquivos, não contra este texto.

- Run **APROVADA**, mas com 12 parâmetros ainda **PROPOSTOS** (orçamento, duração, definição
  de vitória, limiar etc.). O pesquisador ainda não os referendou.
- **Divergência entre políticas passou por margem mínima**: JSD média entre braços 0,0204 bits vs
  limiar 0,02. Dentro do braço 0,0131; piso de ruído 0,0125. Atencioso × relapso (0,0107) fica
  abaixo da divergência intra-braço. O aprendizado mexe pouco no comportamento (≈0,03–0,05 bits
  do instinto). O ambiente está no limite de profundidade.
- **Resultado central**: atencioso vence aleatório, 0,72 pontos, IC95 [0,64, 0,82], 5 sementes.
- **Confundidor não resolvido**: stats de combate vêm dos traços, e traços refletem também o
  *estado de vida* (fome etc.), não só aprendizado. Com políticas quase iguais, a vitória pode
  vir do cuidado, não do treino. **Próximo passo recomendado**: ablação com `PoliticaInstinto`
  (sem aprendizado) sob os mesmos donos. Não foi feita.
- Com 16 interações/dia o braço **relapso** mantém o pet saudável — não é relapso de fato nesse orçamento.
- Erro padrão do Bradley-Terry trata partidas como independentes (subestima); a incerteza honesta
  é o bootstrap sobre sementes.

## Versão web (`web/digilab.html`)

Porte em JavaScript com as mesmas regras e parâmetros de `config.py` (motor, instinto, bandit,
donos, arena). Usa outro gerador aleatório (mulberry32), então **não reproduz os artefatos
Python bit a bit**; não usar para resultado de pesquisa. Replay interno do log funciona e tem
botão de verificação. Arte é placeholder original, desenhada em código a partir de grades de
pixels no próprio arquivo. Se mudar um parâmetro em `config.py`, espelhe no objeto `C`/`CB`/`CD`/`CA` do HTML.

Publicado também como artifact privado em claude.ai (link com o usuário).

## Assets — importante

A pasta `D:\Trab\digilab\Assets` (fora deste repo) contém sprites recortados do Digimon World
(Bandai). É arte e personagens protegidos, **sem licença**. Regra revisada pelo Matheus em
2026-09-24:

- **Permitido**: usar esses sprites na versão web (`web/`) para uso pessoal e local, como
  protótipo de jogo.
- **Proibido**: usar no pacote `digilab/`, em `experiments/`, em `artifacts*/`, em figuras ou
  textos de publicação acadêmica, ou em qualquer build distribuído como produto. Não publicar
  a versão com sprites (artifact, site, repositório público).
- Manter a versão com placeholders originais funcionando: antes de publicar ou distribuir
  qualquer coisa, trocar por arte original ou licenciada.

Versão com sprites: `web/digilab_sprites.html` (no `.gitignore`), cópia de `digilab.html` que
lê `D:\Trab\digilab\Assets\digilab_atlas.png`. O atlas e o script que o gera
(`Assets\gerar_atlas.py`) ficam fora do repo. Precisa de servidor local, porque o caminho é
relativo: `python -m http.server 8765 --directory D:/Trab/digilab` e abrir
`http://localhost:8765/v1/web/digilab_sprites.html`. A linha evolutiva segue o traço de combate
dominante (bebê único; criança e adulto, um par por traço). Se o atlas não carregar, a página
mostra um aviso em vermelho e cai nos placeholders. Se mudar `digilab.html`, a cópia com
sprites não acompanha sozinha.

## Pendências conhecidas

- Referendar (ou alterar) os campos PROPOSTOS de `protocol.py` antes de citar qualquer resultado.
- Ablação instinto × bandit sob os mesmos donos (separar efeito de treino de efeito de cuidado).
- Revisar orçamento/visitas do braço relapso.
- O hash do protocolo não cobre o código de `metrics.py`; mudanças de métrica não alteram o hash.
- A pasta irmã `D:\Trab\digilab\v0` tem os arquivos soltos (sem subpasta `digilab/`); os imports
  dela não funcionam como estão. Este repo é a versão de referência.
