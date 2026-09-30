# Design — MVP, passo M1: confiança de combate e desgaste por rival repetido

Status: **ESPECIFICADO, para aprovação** (pedido do Matheus, 2026-09-29). Nenhum código foi alterado. Todo número é PROPOSTO, sem fonte.

**Origem.** É o passo M1 da seção 28 de `docs/PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md`, revisto contra a revisão bibliográfica verificada de 2026-09-29 (`D:\Trab\digilab\docs\revisao_alife_2026-09-29\`).

**Regra de citação deste documento.**
- Só entram referências marcadas **VERIFICADA** ou **VERIFICADA (sem DOI)** em `referencias_verificadas.csv`.
- Nenhum jogo comercial é usado como evidência.
- Nada aqui é apresentado como novidade: separar instinto de aprendizado, herdar o prior e "ensinado pelo dono" já têm precedente e estão fora deste passo.
- O que não tem referência verificada está marcado **[ESCOLHA DE DESIGN]**. É para ser testado em simulação, não afirmado.

## 1. O que o M1 resolve

Três problemas medidos ou visíveis no projeto:

1. **A luta comum não tem freio de repetição.**
   - Na web, cada luta ajusta as notas dos gambits (`GambitsPet.aprender`, passo `GA.alfa`) igual, seja o primeiro encontro com o rival ou o vigésimo.
   - A "experiência de combate" dos pets v4 (`vitoriasVida × CLE.expPorVitoria`, teto `CLE.expMax`; no Python, `educacao.epsilon_pet`) conta toda vitória igual. Vencer o mesmo bot fraco repetidamente é o caminho mais curto até o teto.
2. **A luta não muda nada visível no pet.** Só 13–18% das decisões do bandit têm um fator explicável (`artifacts_expressao/legibilidade.json`). Para o jogador, lutar muda o placar, não a criatura.
3. **A lição da V3b.** Quando a luta passou pela via do treino ("luta treina"), 577 de 640 pets viraram sombrios (`artifacts_educacao_v3b/`). O M1 **não** usa a fadiga, a sobrecarga nem o treino.

O M1 **não** resolve o vínculo (fica para o M3), as medalhas (M2) nem a herança (M4).

## 2. A mecânica

### 2.1 Novidade por rival (o freio de repetição) [ESCOLHA DE DESIGN]

Cada pet guarda, por rival, um contador de encontros recentes que decai com o tempo de jogo:

    m[rival] ← m[rival] · exp(−Δt / τ_hab) + 1            (depois de cada luta)
    novidade(rival) = exp(−λ · m[rival] antes da luta)      (1 no primeiro encontro)

- O rival é o nome que já está no evento da luta (`l.r` na web, `rival` no Python).
- Com λ = 0,7 e τ_hab = 48 h de jogo:

  | lutas seguidas contra o mesmo rival | novidade |
  |---|---|
  | 1ª | 1,0 |
  | 3ª | ≈ 0,25 |
  | 5ª | ≈ 0,06 |

  Dois dias sem enfrentar o rival devolvem parte da novidade: depois de 5 lutas seguidas, ela volta de ≈ 0,06 para ≈ 0,36.
- **Fundamentação:** tratar a novidade como sinal interno próprio do agente, separado da recompensa externa, segue a tipologia de motivação intrínseca de Oudeyer e Kaplan (2007). A forma da curva (exponencial com recuperação) **não** tem referência verificada.

### 2.2 Confiança de combate (um estado, não um traço)

A confiança `c` fica em [−1, 1] e começa em 0 no ovo. Ela decai para 0 entre as lutas e é empurrada pelo resultado de cada luta, ponderado pela novidade:

    c ← c · exp(−Δt / τ_conf)                                (antes da luta)
    c ← corte(c + η_s · novidade · sinal, −1, 1)              (sinal: vitória +1, derrota −1, empate 0)
    η_s = η                           se sinal > 0
    η_s = η · (1 + k_sens · sensibilidade)   se sinal < 0

- **Não é um eixo de personalidade novo.** É um estado derivado dos eventos de luta, na escala de horas a dias.
- **O temperamento dá a inclinação individual:** a `sensibilidade`, que já existe no temperamento, faz a derrota pesar mais. Isso usa o formalismo de norma de reação de Dingemanse et al. (2010), com o intercepto como nível médio e a inclinação como plasticidade. A personalidade que se desenvolve da interação entre o estado inicial e a experiência é o enquadramento de Stamps e Groothuis (2010).
- **[ESCOLHA DE DESIGN]:** o efeito "vitória aumenta a confiança, derrota diminui" e a sua duração não estão na revisão verificada. São hipóteses de design para a simulação testar (gates G3 e G5).
- **Contra a espiral:**
  - o decaimento para 0 limita a sequência de vitórias e a de derrotas;
  - a novidade limita a repetição;
  - o corte em ±1 limita o valor.

  O efeito do IKEA depende de a tarefa dar certo (Marsh et al., 2018). Um pet que só perde e só fica mais inseguro pode valer menos para o dono, e o M1 evita esse poço.

### 2.3 O que a confiança faz na luta

Só o **ε do lutador do pet** (a chance de ignorar os próprios gambits) muda, sem tocar na resolução do combate V21C:

    ε_v5 = ε_v4 + κ · max(0, −c)       (insegurança: hesita e erra mais)

- A confiança positiva **não** reduz o ε além do que o v4 já faz. O ganho de ser confiante fica na fala e no aprendizado dos gambits (2.4), e isso impede um efeito vencedor que se retroalimenta na força.
- Com κ = 0,10, um pet no fundo do poço (c = −1) tem +0,10 de ε. É da mesma ordem que um pet sem disciplina (`delta_epsilon_indisciplina` = 0,10).

### 2.4 Experiência e aprendizado de gambits, pesados pela novidade (pets v5)

- **Experiência de combate:** cada vitória soma `novidade` em vez de 1. O teto `CLE.expMax` continua. Nos dois lados (Python e web).
- **Gambits híbridos:** o passo de aprendizado de cada luta é `GA.alfa · novidade`. Os gambits híbridos existem só na web, e continuam só na web (`REGISTRO_DESVIOS`, como hoje).

É esse o fecho do ciclo **atividade → benefício → saturação → outra atividade**: lutar contra o mesmo rival deixa de ensinar e de dar experiência, e o pet diz isso (2.5).

### 2.5 O que o jogador vê: frases de estado

Quatro frases, com limiar e histerese (a frase só troca depois de 2 h de jogo na faixa nova), na tabela de `expressao.py` e `expressao.ts` (com marcador único e a cobertura conferida na carga, como as outras tabelas):

| estado | condição | exemplo de frase (adolescente em diante) |
|---|---|---|
| confiante | c ≥ 0,4 | "Tô confiante: ganhei as últimas." |
| inseguro | c ≤ −0,4 | "Ando inseguro depois daquelas derrotas." |
| entediado do rival | as 3 últimas lutas com novidade ≤ 0,3 | "De novo esse aí? Já sei tudo dele." |
| neutro | resto | (nenhuma frase de estado) |

- **Toda frase é ancorada no registro:** o "porquê" que aparece ao tocar na frase aponta para as lutas que puseram o pet naquele estado. É a restrição que Madumal et al. (2020) sustentam: a explicação ancorada num modelo causal é melhor que a narrativa livre.
- **O jogador percebe o efeito do que fez:** esse é o requisito que Amershi et al. (2014) formulam para o aprendizado interativo. Medir se o jogador **entende** exige um estudo com pessoas (Anderson et al., 2019), que continua **IDEIA** e pede comitê de ética.
- **Bebê e criança:** o bebê mostra só um emote. A criança usa a versão curta ("Ganhei!", "Perdi de novo…").

### 2.6 O que fica de fora do M1, de propósito

- **A técnica aprendida vendo o rival.** Ela mudaria o catálogo de técnicas do V21C e o hash do combate. Fica para depois, se for aprovada.
- **Qualquer eixo novo de personalidade** (ousadia, agressividade). O M1 só usa o temperamento que já existe.
- **O vínculo e a luta forçada** (M3). A economia, as medalhas e o Frontier.
- **Eventos novos no registro.** A confiança e a novidade são **funções dos eventos de luta que já existem**. O replay recalcula as duas, e o save não muda de formato.

## 3. Onde mexe

**Python** (`digilab/`, só biblioteca padrão):
- `digilab/confianca.py` (novo): funções puras `novidade`, `atualizar_confianca`, `epsilon_confianca` e o estado `ConfiancaCombate` (contadores por rival, `c`, último tick).
- `digilab/config.py`: `ConfigConfianca` (com `ligada = False`) e os parâmetros da seção 4.
- `digilab/educacao.py`:
  - o `MotorEducacao` atualiza a confiança no `lutar`, só com `ConfigConfianca.ligada`;
  - o `epsilon_pet` ganha o termo da confiança;
  - a experiência pesada pela novidade vale só com a chave ligada.
- `digilab/expressao.py`: a tabela `expressar_confianca`.
- `digilab/protocol.py`: os parâmetros novos no registro de parâmetros, com status e fonte.
- **Nada muda** no `engine.py`, no combate (`combate_v2/`), nas runs V3, E1 e confirmatória, nem nos protocolos com hash: com a chave desligada, tudo reproduz igual.

**Web** (`web/app/`):
- `motor/confianca.ts` (espelho).
- `motor/constantes.ts`: `CCF`, conferido contra o Python por `mapa_constantes.json` e `constantes.test.mjs`.
- `motor/motor.ts` e `gambits_pet.ts`: `VERSAO_PET = 5`. Os pets v1–v4 rejogam igual; só os ovos novos são v5.
- `motor/expressao.ts` e a tela do Pet: a frase de estado e o "porquê" com as lutas da causa.
- `Aprendizado`: uma linha "Confiança", só em palavras.

**Testes:**
- **Python:** as funções puras (curvas, decaimento, corte, histerese); a chave desligada reproduz a V3 e o E1 (log e resumo iguais); o replay recalcula a confiança igual.
- **Web:** a paridade da confiança com o Python numa sequência fixa de lutas (gabarito exportado do Python, como as constantes); os gabaritos v1–v4 intactos; e2e da frase.

## 4. Parâmetros (todos PROPOSTOS, sem fonte)

| parâmetro | valor | o que controla |
|---|---|---|
| `lambda_novidade` | 0,7 | quão rápido a repetição satura |
| `tau_habituacao_min` | 2880 (48 h) | quando a novidade volta |
| `eta_confianca` | 0,25 | quanto uma luta nova mexe na confiança |
| `k_sensibilidade` | 0,5 | quanto a sensibilidade pesa na derrota |
| `tau_confianca_min` | 1440 (24 h) | quanto dura a confiança |
| `kappa_eps` | 0,10 | quanto a insegurança aumenta o ε |
| `limiar_frase` | 0,4 | limiar das frases de confiante e inseguro |
| `histerese_frase_min` | 120 | tempo mínimo na faixa antes de trocar a frase |
| `limiar_tedio` / `n_tedio` | 0,3 / 3 | novidade das últimas n lutas para a frase de tédio |

## 5. Verificação (plano congelado antes de qualquer run)

| gate | o que mede | critério PROPOSTO |
|---|---|---|
| **G1** reprodução | com a chave desligada: V3, E1 e confirmatória; os gabaritos v1–v4 da web | byte a byte (teste) |
| **G2** paridade | a confiança e a novidade, Python × web, numa sequência fixa de 200 lutas | iguais até 1e−12 |
| **G3** teto de efeito | taxa contra o painel B (neutra) do mesmo pet com c = −1 e com c = 0, sementes de calibração | diferença ≤ 0,10 |
| **G4** freio de repetição | 20 lutas contra o mesmo bot × 20 contra 4 bots em rodízio: soma do ganho de confiança e do passo dos gambits | a repetição rende ≤ 35% do rodízio |
| **G5** sem poço nem espiral | nas vidas dos donos da V3, com a chave ligada: fração do tempo com \|c\| ≥ 0,9 | ≤ 10% por braço |
| **G6** frase honesta | cada frase mostrada tem no registro as lutas que a causaram; troca no máximo 1 vez a cada 2 h | 100% (teste) |

- **Sementes:** G3 e G5 rodam em sementes de calibração **separadas** das de validação, num plano de análise registrado antes (`docs/PLANO_ANALISE_M1.md`).
- **Se um gate reprovar:** vira achado registrado. Os números não são mexidos na mesma run.
- **A pergunta de pesquisa desta mecânica** (se o estado de confiança separa donos) **não** é objetivo do M1. O M1 é mecânica de jogo com trava de segurança. Se um dia virar pergunta, entra com plano próprio.

## 6. Riscos

- **O efeito do dono pode ficar ainda menor.** A confiança soma ruído ao ε, como o temperamento e a obediência já somaram na personalidade (`artifacts_v1_personalidade/`). É por isso que a confiança positiva não reduz o ε (2.3) e o G3 limita o efeito.
- **Frase repetitiva:** a histerese e a honestidade (G6) seguram, mas a variedade depende da voz própria (`DESIGN_VOZ_PROPRIA.md`), que é outro passo.
- **A campanha:** repetir a tentativa contra o mesmo NPC dá menos confiança e também tira menos. Perder dez vezes do Piedmon não afunda o pet, e isso é de propósito.
- **A não estacionariedade:** a confiança muda o ε ao longo do tempo. O bandit da vida não é afetado (a confiança só entra na luta). Os gambits web já lidam com notas que mudam.

## 7. Decisões para o Matheus

1. **Exceção de escopo** para o M1 (mecânica nova de jogo), com Python e web juntos, como pede a regra.
2. **A técnica vista fica fora do M1** (mudaria o catálogo e o hash do combate). Eu recomendo que sim.
3. **A experiência de combate e os gambits pesados pela novidade** nos pets v5 (2.4). Eu recomendo que sim: é o freio contra o grind que já existe hoje.
4. **Os números da seção 4.**

## 8. Referências (só VERIFICADA na revisão de 2026-09-29)

- Amershi, S., Cakmak, M., Knox, W. B. & Kulesza, T. (2014). Power to the people: the role of humans in interactive machine learning. *AI Magazine* 35(4), 105–120. https://doi.org/10.1609/aimag.v35i4.2513
- Anderson, A., Dodge, J., Sadarangani, A. et al. (2019). Explaining reinforcement learning to mere mortals: an empirical study. IJCAI. https://doi.org/10.24963/ijcai.2019/184
- Dingemanse, N. J., Kazem, A. J. N., Réale, D. & Wright, J. (2010). Behavioural reaction norms: animal personality meets individual plasticity. *TREE* 25(2), 81–89. https://doi.org/10.1016/j.tree.2009.07.013
- Madumal, P., Miller, T., Sonenberg, L. & Vetere, F. (2020). Explainable reinforcement learning through a causal lens. AAAI 34(3), 2493–2500. https://doi.org/10.1609/aaai.v34i03.5631
- Marsh, L. E., Kanngiesser, P. & Hood, B. (2018). When and how does labour lead to love? *Cognition* 170, 245–253. https://doi.org/10.1016/j.cognition.2017.10.012
- Oudeyer, P.-Y. & Kaplan, F. (2007). What is intrinsic motivation? A typology of computational approaches. *Frontiers in Neurorobotics* 1, 6. https://doi.org/10.3389/neuro.12.006.2007
- Stamps, J. & Groothuis, T. G. G. (2010). The development of animal personality: relevance, concepts and perspectives. *Biological Reviews* 85(2), 301–325. https://doi.org/10.1111/j.1469-185x.2009.00103.x
