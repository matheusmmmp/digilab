/* O selo do painel DigiBrain (componentes/DigiBrain.tsx): "replay" num replay; "ao vivo" so com o motor correndo (o tempo do jogo
   andando: fora da pausa, do ovo chocando, da luta no palco, do save com erro e do pet que se foi); senao, "pausado". */
export type EstadoSelo = "vivo" | "replay" | "pausado";

export function estadoSelo(o: { replay: boolean; velocidade: number; nascendo: number; erroSave: boolean; lutaSegura: boolean; morto: boolean }): EstadoSelo {
  if (o.replay) return "replay";
  return o.velocidade > 0 && o.nascendo === 0 && !o.erroSave && !o.lutaSegura && !o.morto ? "vivo" : "pausado";
}
