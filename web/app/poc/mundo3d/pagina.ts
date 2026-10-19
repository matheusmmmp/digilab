/* A página do WORLD-POC-01a, nesta etapa sem a vista: roda o mundo pela semente e pelos ticks, mostra o resumo e baixa o registro em
   JSON. A vista em Three.js (vista.ts) entra na etapa E3. */
import { Simulacao } from "./simulacao.ts";

const el = <T extends HTMLElement>(id: string): T => {
  const e = document.getElementById(id);
  if (!e) throw new Error(`#${id} nao existe na pagina`);
  return e as T;
};

let ultimo: Simulacao | null = null;

el<HTMLButtonElement>("rodar").addEventListener("click", () => {
  const semente = Number(el<HTMLInputElement>("semente").value), ticks = Number(el<HTMLInputElement>("ticks").value);
  const s = new Simulacao(semente);
  s.avancar(ticks);
  ultimo = s;
  const r = s.registros;
  const por = (k: string) => r.filter(x => x.intencao.tipo === k).length;
  el("saida").textContent = [
    `hash ${s.hash()}  tick ${s.mundo.tick}  decisoes ${r.length}`,
    `consumir ${por("consumir")}  empurrar ${por("empurrar")}  aproximar ${por("aproximar")}  descansar ${por("descansar")}`,
    `comeu ${r.reduce((a, x) => a + x.fisico.comeu, 0)}  empurroes ${r.reduce((a, x) => a + x.fisico.empurroes, 0)}`,
    "", JSON.stringify(s.estado(), null, 1),
  ].join("\n");
  el<HTMLButtonElement>("baixar").disabled = false;
});

el<HTMLButtonElement>("baixar").addEventListener("click", () => {
  if (!ultimo) return;
  const blob = new Blob([JSON.stringify({ semente: ultimo.semente, log: ultimo.log, registros: ultimo.registros }, null, 1)],
    { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `world_poc_01_${ultimo.semente}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
});
