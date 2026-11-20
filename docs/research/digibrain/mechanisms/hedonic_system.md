# Sistema hedônico: necessidade, querer, gostar e nutrição

**NENHUM DESENHO ESCOLHIDO.** A mecânica de comida abaixo é **hipótese DigiLab**, não conclusão da literatura. As definições
operacionais com os campos do log ficam em `docs/DEFINICOES_FRUTAS_V2.md` (tarefa pendente).

## As quatro variáveis

| variável | leitura informal | definição operacional (proposta) | o que não é |
|---|---|---|---|
| **NECESSIDADE** | "meu corpo precisa" | déficit de um drive do estado (hoje `fome`, com 1 = saciado; `digilab/state.py`) | não é gosto |
| **QUERER** (*wanting*) | "quero obter" | tendência de aproximação, esforço e escolha **antes** de consumir | não é gostar; pode crescer sem ele |
| **GOSTAR** (*liking*) | "gosto da experiência" | resposta avaliativa **depois** do consumo, por item | não é experiência subjetiva; não é fome |
| **NUTRIÇÃO** | "o que isso faz fisiologicamente" | efeito do item sobre os drives e a saúde | não é gosto; é o canal de cuidado |

Os nomes informais ficam só neste estudo. No motor, no log e na fala: nomes operacionais, sem afirmar que o pet sente
prazer (regra 4 do `README.md`).

## O que a literatura sustenta (busca V1–V6, `V3_SINTESE_FRUTAS_VICIO_V1_V6.md`; todas VERIFICADA salvo indicação)

- Gostar, querer e aprender são componentes dissociáveis da recompensa (Berridge e Robinson 1998,
  `10.1016/s0165-0173(98)00019-8`; Berridge, Robinson e Aldridge 2009, `10.1016/j.coph.2008.12.014`; em comida, Morales e
  Berridge 2020, `10.1016/j.physbeh.2020.113152`). É neurociência de mamíferos.
- Medir gostar e querer exige **instrumentos separados** (Finlayson e Dalton 2012, `10.1016/j.appet.2011.10.011`): no simulador,
  dois registros, não um escalar.
- A literatura mede **reação hedônica**, não experiência; Berridge (1996, `10.1016/0149-7634(95)00033-b`) levanta a pergunta
  em vez de resolvê-la.
- **Saciedade sensório-específica:** o agradável cai mais para o alimento comido do que para os outros, independente da fome
  geral (Rolls et al. 1981, `10.1016/0031-9384(81)90310-3`; 1983, `10.1016/0031-9384(83)90003-3`).
- **Neofobia é traço** individual mensurável (Pliner e Hobden 1992, `10.1016/0195-6663(92)90014-w`); preferência inata é
  modulada por exposição (Beauchamp e Moran 1982, `10.1016/s0195-6663(82)80007-x`).
- **Preferência aprendida pela consequência pós-ingestiva**, separada do gosto oral (Sclafani 2001, `10.1006/appe.2000.0370`;
  de Araujo et al. 2008, `10.1016/j.neuron.2008.04.003`; Bodnar 2018, `10.1016/j.appet.2016.12.015`); **aversão condicionada**
  (Garcia et al. 1955, `10.1126/science.122.3160.157`; Bernstein 1999, `10.1016/s0899-9007(98)00192-0`).
- **Vício como assimetria:** o querer cresce com a exposição e o gostar não acompanha (Robinson e Berridge 1993,
  `10.1016/0165-0173(93)90013-p`; teste em humanos: Grigutsch et al. 2019, `10.1016/j.jbtep.2019.01.002`), teoria
  **contestada** quanto ao papel causal da dopamina (Nutt et al. 2015, `10.1038/nrn3939`). Modelos computacionais: Redish 2004
  (`10.1126/science.1102384`, erro de predição que não se extingue); Keramati, Durand e Girardeau 2017 (`10.1037/rev0000046`,
  RL homeostático). São modelos de droga, não de comida.
- **Fly (CORPUS):** fome e saciedade modulam a busca por comida e a expressão de memória apetitiva (Tsao et al. 2018; Li et
  al. 2009).
- **Berto et al. 2024 (CORPUS):** separação computacional de homeostase e hedonismo em robôs.

## No DigiLab hoje (REPOSITÓRIO)

Uma comida só. `ALIMENTAR` (dono) soma `ganho_alimentar` à fome; o pet `COMER` soma 0,05. Fome baixa leva a privação, e
privação tira saúde até a morte (`state.py`). Não há gosto, querer, nutrição separada nem preferência. O instinto come por
regra (`fome_moderada`, `pedido_necessidade`). Nada aprende com comida.

## Hipóteses DigiLab

```
DIGILAB HYPOTHESIS H-HED-01

Food may have independent:
  nutritional_effect
  hedonic_value

Future experiment may investigate:
  genetic predisposition
  +
  learned preference

IMPORTANT:
Berto's reported experiment does not establish
learned food liking in DigiLab.
```

| ID | pergunta | origem | teste mínimo |
|---|---|---|---|
| H-HED-01 | nutrição e valor hedônico independentes por item explicam escolhas estáveis além da necessidade | Matheus; antiga H-HED-001 | fatorial necessidade × item × efeito, com disponibilidade igual |
| H-HED-02 | a consequência pós-consumo atualiza a preferência (preferência aprendida e aversão) | antiga H-HED-002; Sclafani, Garcia | pareamento item → efeito controlado; escolha depois, com o mesmo estado |
| H-HED-03 | o gostar de **um** item cai com o consumo recente dele, sem passar pela fome (saciedade sensório-específica) | Rolls et al. | mesma fome, consumo recente diferente; o gostar dos outros itens não cai |
| H-HED-04 | neofobia é do ovo (traço), preferência aprendida é estado | Pliner e Hobden; Beauchamp e Moran | aprendizado desligado: genomas com neofobia diferente diferem só no primeiro contato |
| H-HED-05 | vício como assimetria: querer cresce com a exposição, gostar não acompanha | Robinson e Berridge; Redish; Keramati et al. | dois registros; o querer sobe e o gostar fica ou cai sob exposição repetida; com o efeito nutricional fixo |
| H-HED-06 | o genoma modula a sensibilidade ao canal hedônico (como em `reinforcement.md`, H-R4) | Matheus | experiência acoplada; divergência por genoma |

## Riscos e restrições

- **Comida é canal de cuidado.** Fome → saúde → morte. Um efeito que venha por aí não conta como ensino; o "só cuidado"
  acoplado é obrigatório em todo braço com frutas (`docs/DEFINICOES_V2.md`, seção 7).
- **Escolha não identifica gosto:** a taxa de escolha mistura fome, acesso, novidade, atração aprendida, hábito e efeito.
  Medir aproximação/esforço, consumo, avaliação depois e escolha posterior em separado.
- **Creatures não é precedente** do vício: não há fonte primária (`sources/creatures3.md`).
- **Ética (por analogia):** a literatura verificada de ética de desenho trata de mecânicas dirigidas ao jogador (loot boxes:
  Zendle e Cairns 2018, `10.1371/journal.pone.0206767`; Drummond e Sauer 2018, `10.1038/s41562-018-0360-1`; monetização
  predatória: King e Delfabbro 2018, `10.1111/add.14286`; padrões exploratórios: Karlsen 2019, Veiga et al. 2025). Ela **não
  cobre** dependência num personagem cuidado pelo jogador (resultado negativo de busca). Todo apoio aqui é por analogia e
  rotulado assim. Ausência de crítica não é aval.
