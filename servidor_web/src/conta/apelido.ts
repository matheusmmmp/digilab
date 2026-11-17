/* O apelido (UX-CN-4 do docs/PLANO_UX_CONTA.md): um Digimon Rookie do Catálogo e um número, como "Agumon#4821". A troca é por uma lista
   fechada, a mesma para todos (não revela o progresso do jogador); o número sai por sorteio. Nada se digita.

   A lista são os Rookies do DIGIMON_DA_FORMA de web/app/motor/nomes.ts (o mapa da Etapa 0), na ordem dos brasões; o
   test/apelido.test.ts confere que ela não se afasta do jogo. O número tem 4 dígitos (1000 a 9999; PROPOSTO, SEM FONTE). */
import { randomInt } from "node:crypto";

export const ROOKIES: readonly string[] = ["Agumon", "Guilmon", "Patamon", "Gabumon", "Armadillomon", "Veemon", "Palmon", "Gomamon"];
export const NUMERO_MIN = 1000, NUMERO_MAX = 9999;

export const montarApelido = (digimon: string, numero: number): string => `${digimon}#${numero}`;

/** sorteia um apelido livre; `digimon` fixa o Digimon (a troca), senão sorteia também o Digimon */
export function sortearApelido(ocupado: (apelido: string) => boolean, digimon?: string, sortear: (min: number, max: number) => number = randomInt): string {
  if (digimon !== undefined && !ROOKIES.includes(digimon)) throw new Error(`Digimon fora da lista: ${digimon}`);
  for (let i = 0; i < 50; i++) {
    const d = digimon ?? ROOKIES[sortear(0, ROOKIES.length)]!;
    const a = montarApelido(d, sortear(NUMERO_MIN, NUMERO_MAX + 1));
    if (!ocupado(a)) return a;
  }
  throw new Error("não achei apelido livre em 50 sorteios");
}
