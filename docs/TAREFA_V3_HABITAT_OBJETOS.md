# TAREFA V3 — HABITAT_OBJETOS: os objetos do cuidado na ilha, o treino no saco e a bola física

Pedido do Matheus em 2026-11-01, na conversa: ao treinar, o pet vai até um equipamento e dá golpes; a bola é um objeto físico, o pet bate
nela e ela se mexe; o dono pode arrastar a bola, como a ração; e assets 3D para o cocô, a comida, a cama e o treino.

## Decisões do Matheus (2026-11-01, na conversa)

- **HO-1, a direção da bola: no motor.** Ela sai na direção do golpe, gravada no log, e não só na vista.
- **HO-2, o treino: coreografia na ilha.** O ganho continua instantâneo no motor (`Motor.treinar`). A ilha mostra o pet indo ao saco,
  batendo e voltando. Não muda o motor do treino nem o log.
- **HO-3, os assets: os que não existem em CC0 entram no código** (o saco de pancada, a bola e o kit médico). Os kits CC0 baixados (a
  comida, a carne, a cama, a luz, o banheiro e o cocô, em `Assets/kits3d/`, fora do git) ficam para quando a ilha os usar.

## O que entra

1. **O motor (pet v15).** A chave `bolaNoGolpe` do `Mundo` (`ConfigBolaNoGolpe` no Python), desligada: ligada, a bola sai na direção
   em que o pet vinha, de onde ele estava antes do passo até a bola (`direcaoDoGolpe`, das 16 do DIR16 a mais alinhada). A distância é a
   do sorteio de sempre: o sorteio da direção fica no fluxo `mundo-bola`, só não é usado. Parado em cima da bola, vale a direção sorteada.
   `VERSAO_PET = 15` é o v14 com a chave ligada; o v13 e o v14 seguem com a bola de antes, e a luta do v15 é a do v14 (`CV21E_TR14`).
2. **A bola do dono, o evento `db`.** `Motor.deixarBola(x, y)`, em qualquer pet com o mundo. Como o `deixar_bola` do Python, não é
   contato nem cuidado. Os logs de antes não têm o evento, então o replay deles não muda.
3. **A tela.**
   - Pegar a bola na cena e soltar no chão (`PorBola.tsx`, `ArrastoBola`).
   - O botão "Pôr bola" no menu Mais: arrastar até o chão, ou tocar ou Enter para pôr a bola perto do pet.
4. **A ilha.**
   - O saco de pancada perto do ninho, que balança a cada golpe.
   - O kit médico ao lado do ninho enquanto o pet está lesionado.
   - A bola desliza até onde o motor diz e gira ao rolar.
   - O golpe do pet usa o clipe `Attack_1` do atlas: no treino (CENA.treino, marcado pela tela Treinar) e quando o motor rola a bola.
   - Todos os números da vista estão em `ilha/constantes.ts`, PROPOSTO, SEM FONTE.

## Fora

- O cocô em 3D. A sujeira do motor é uma contagem, sem posição; o cocô continua o desenho 2D do palco.
- A cama e a comida dos kits CC0.
- A batida na bola não muda a distância nem o humor.

## Resultado (2026-11-01)

- Python: `tests/test_bola_no_golpe.py` (6) e os testes do mundo e dos gabaritos da web: 73 passam.
- Web: 658 testes passam, com os 7 novos de `test/bola_no_golpe.test.ts`; os testes que conferiam `VERSAO_PET` 14 passam a conferir 15.
  `npm run tipos` passa.
- Capturas no Chrome (Playwright, 1280 × 760, um save v15 de semente 4242):
  - o saco na ilha;
  - "Pôr bola" põe a bola perto do pet;
  - o arrasto leva a bola, que some da cena e reaparece onde caiu (dois `db` no log);
  - no treino, o pet vai ao saco e bate com o `Attack_1`, e o saco balança.
- Não conferido na tela:
  - a batida na bola, que depende de o cérebro decidir brincar;
  - o kit médico, porque o save não tem lesão.
