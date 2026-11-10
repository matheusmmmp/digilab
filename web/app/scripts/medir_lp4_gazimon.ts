/* LUTA_POC, LP4 (D-LP4-6 do registro de 2026-11): a taxa de vitoria de um Rookie v21 contra o Gazimon (o lider da Campina), na luta da POC, no
   Campo de treino (o mapa da Campina), sem treino e com o treino tipico do Rookie (8 pontos, CIT.tipico.crianca), em 200 sementes por pet.
   Descritivo, sem IC: e o achado que a LP5 (o equilibrio) tem de olhar. Nenhum numero do jogo muda aqui.
   uso (em web/app): node scripts/medir_lp4_gazimon.ts -> scripts/medicoes/lp4_gazimon.json */
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { CIT, DUR_EVO, Motor, lutarNucleoPoc, sorteiosPoc, statsNpc } from "../motor/index.ts";

const GAZIMON = "npc_tier1_brutamontes", LUTAS = 200, SEMENTES_PET = [11, 21, 23, 101, 202];
/* os 8 pontos do Rookie tipico, espalhados (a forca e o vigor primeiro) */
const TREINO_8 = { vigor: 2, folego: 1, recuperacao: 1, forca: 2, mira: 1, guarda: 1 };
if (Object.values(TREINO_8).reduce((a, b) => a + b, 0) !== CIT.tipico.crianca) throw new Error("o treino tipico do Rookie mudou");

const taxa = (a: { forma: string; stats: ReturnType<Motor["statsLutaPoc"]> }): number => {
  const b = { forma: GAZIMON, stats: statsNpc(GAZIMON) };
  let v = 0;
  for (let s = 0; s < LUTAS; s++) if (lutarNucleoPoc({ cena: "campo", semente: s, a, b }, sorteiosPoc(s)).vencedor === "a") v++;
  return v / LUTAS;
};
const pets = SEMENTES_PET.map(semente => {
  const m = new Motor(semente);
  m.avancar(DUR_EVO.bebe + 30);
  if (m.estagioAtual !== "crianca") throw new Error(`o pet ${semente} nao e Rookie`);
  const sem = { forma: m.formaLutaPoc, stats: m.statsLutaPoc() };
  m.treino.pontos = { ...TREINO_8 };
  const com = { forma: m.formaLutaPoc, stats: m.statsLutaPoc() };
  return { semente, especie: m.especie, forma: m.formaLutaPoc, hp_sem_treino: sem.stats.hp, vitoria_sem_treino: taxa(sem), hp_com_8: com.stats.hp, vitoria_com_8: taxa(com) };
});
const saida = { tarefa: "LUTA_POC, LP4, D-LP4-6", mapa: "campo", rival: GAZIMON, hp_rival: statsNpc(GAZIMON).hp, lutas_por_pet: LUTAS, treino_8: TREINO_8, pets };
const destino = fileURLToPath(new URL("./medicoes/lp4_gazimon.json", import.meta.url));
writeFileSync(destino, JSON.stringify(saida, null, 1) + "\n");
console.log(destino);
for (const p of pets) console.log(p.semente, p.especie, "sem treino", p.vitoria_sem_treino, "com 8", p.vitoria_com_8);
