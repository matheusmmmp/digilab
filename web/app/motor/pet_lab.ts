/* A fabrica do pet de teste do laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, LM4; LAB-2 e LAB-3): a v16, a v14 com o DigiBrain modular no lugar do
   cerebro A. So esta fabrica cria a v16; nenhum ovo padrao muda (`new Motor(semente)` segue v14). O replay e o do jogo (`Motor.reproduzir(semente,
   log, VERSAO_PET_LAB)`). A tela (Ajustes > Laboratorio, o ovo de teste, o selo "experimental") e a LM5b. */
import { VERSAO_PET_LAB } from "./constantes.ts";
import { Motor } from "./motor.ts";
import type { EventoRegistro } from "./tipos.ts";

/** o ovo de teste: um pet v16 da semente */
export function petDeTeste(semente: number): Motor {
  return new Motor(semente, VERSAO_PET_LAB);
}

/** o pet de teste refeito do registro (o replay) */
export function petDeTesteDoRegistro(semente: number, log: readonly EventoRegistro[]): Motor {
  return Motor.reproduzir(semente, log, VERSAO_PET_LAB);
}
