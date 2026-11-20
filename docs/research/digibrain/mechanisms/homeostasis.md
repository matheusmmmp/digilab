# Homeostase e necessidade

## Nas fontes

- **VERIFICADA:** RL homeostático: recompensa como redução de desvio homeostático; maximizar recompensa e manter a
  estabilidade passam a coincidir (Keramati e Gutkin 2014, `10.7554/elife.04811`). Extensão para adicção: Keramati, Durand e
  Girardeau 2017 (`10.1037/rev0000046`).
- **CORPUS:** na mosca, fome e saciedade mudam a busca por comida e a expressão de memória apetitiva (Tsao et al. 2018; Li et al.
  2009). No CST, necessidades e drives operacionalizados (Fróes e Gudwin 2017); Berto et al. 2024 com homeostase de Hull.
- **INTERPRETAÇÃO:** uma variável de estado pode mudar o valor das ações ou a expressão do aprendido **sem ser recompensa**.
  Um sinal homeostático não é, por si, uma regra de aprendizado.

## No DigiLab hoje (REPOSITÓRIO)

- Drives em `digilab/state.py`: fome (1 = saciado), higiene, energia, humor, saúde. Privação = mínimo de fome, higiene e energia
  abaixo de `Config.limiar_privacao` (0,15, lido desde o F0-LIMPEZA, PR #112); privação tira saúde, saúde zero é morte.
- O instinto (`policy.PoliticaInstinto`) decide por **regras escritas à mão** sobre os drives (sono, pedido de necessidade,
  abandono, fome moderada, tempo livre). **Nenhum aprendizado usa a redução de déficit como reforço.** O RL homeostático é
  só a base teórica citada (`docs/MAPA_SISTEMA_2026-09-29.md`).
- O cuidado do dono age direto nos drives (`state.aplicar_acao_usuario`): é o canal pelo qual o dono pesou na v1.

## Hipóteses

| ID | pergunta | teste mínimo |
|---|---|---|
| H-HOM-01 | a redução de déficit como reforço (sem dono) ensina o pet a cuidar de si melhor que o instinto | nó N3 de `ARQUITETURA_V2_VALIDACAO.md`; num ambiente em que a escolha mexe em drive; tempo fora de privação, saúde, sem mortes novas, G6 |
| H-HOM-02 | o estado de necessidade modula a expressão do aprendido (como na mosca), não só a escolha | mesmo aprendizado, necessidade diferente na hora do teste |

Antes de qualquer teste: separar geração do estado, escolha, resultado e atualização, e manter a política fixa quando se testa
um caminho causal. Nenhuma lista de drives nem fórmula decidida.
