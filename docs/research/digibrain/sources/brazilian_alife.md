# Vida artificial e sistemas cognitivos no Brasil

Status: **CORPUS**, salvo indicação. Só Castro e Gudwin (2013) está na tabela verificada do projeto.

## A.L.I.V.E. (USP, 2003)

FONTE: dissertação de mestrado de R. P. O. Neves (`10.11606/D.3.2003.tde-21102024-120852`), uma plataforma em Java/Java3D de
experimentos e visualização de vida virtual, em contexto multiagente; o experimento das algas é adaptação genética.
**Não mostra** um par de controladores neurais herdado e individual, nem herança da capacidade de aprender. Para essas
duas ideias as fontes VERIFICADAS são Hallawa et al. (Evo-RL, `10.1145/3449726.3459475`: partição instinto × aprendido no
mesmo agente) e o efeito Baldwin (Hinton e Nowlan 1987; Fernando et al. 2018, `10.1145/3205651.3205763`).

## ALGA e aprendizado instrutivo

FONTE: o relatório *Implementação do Projeto ALGA* (E. P. C. Neves, USP, 2003) descreve peixes simulados que **transmitem
informação entre si**, acompanham confiança e sucesso das ações e depois se **autoavaliam**. É precedente real de
"informação social + revisão pela consequência". **Não é** tutor humano nem razão para reabrir a refutação da v1.
Netto, Cavalhieri e Rodrigues (2005, *RITA* 12(2), sem DOI) põem evolução genética, aprendizado instrutivo e persuasão em
cenários **separados**: motivam a hipótese de interação genótipo × aprendizado, não a demonstram.

## Motivação e drives

- Fróes e Gudwin 2017 (SBAI): subsistema motivacional do CST (*Cognitive Systems Toolkit*), com necessidades e prescrições
  concorrentes e subsunção dinâmica pela urgência, numa tarefa estreita (coleta de joias).
- Berto et al. 2024 (`10.1016/j.cogsys.2024.101278`): homeostase no estilo de Hull, com dimensões hedônicas e RL, em robôs
  móveis. Mostra que dá para **separar operacionalmente** necessidade e valor hedônico num modelo. Não é resultado biológico
  e **não estabelece preferência alimentar aprendida no DigiLab**.
- Rossi et al. 2024 (`10.1109/ICDL61372.2024.10645017`): drives duradouros × impulsos temporários em aprendizado
  procedimental de humanoide simulado. Não é teste de política única × modular.

## Memória e episódio

- **VERIFICADA:** Castro e Gudwin 2013 (`10.4018/jse.2013010102`): memória episódica por cenas numa criatura simulada; a cena
  recuperada informa a escolha de objeto na navegação (o episódio é feito para influenciar o comportamento, não só ser
  guardado).
- Sakabe et al. 2025 (`10.1016/j.cogsys.2025.101397`): detecção e codificação de episódios no CST, com tarefas de consulta.
- Nenhuma das duas estabelece identidade autobiográfica nem memória persistente de pet.

## Correções de leitura

"CST" = *Cognitive Systems Toolkit* (Unicamp, Gudwin); não existe fonte "CST" isolada identificada. "Berto" = Letícia Berto
et al. 2024. A afirmação "ALGA tutor" do ZIP original é ampla demais: usar só o escopo do relatório dos peixes.
