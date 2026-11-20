// A ilha da prancha L1 em JSON: a grade (web/app/src/telas/pet/ilha/grade.ts) sobre a ConfigMundo do motor (CMU), o mesmo que a cena le.
// So para a prancha; nenhum codigo do jogo. Uso (Node 22.6 ou mais, que tira os tipos sozinho):
//   node docs/pranchas/ux-lugares/ilha_json.mts > D:/Trab/digilab/capturas_ux_lugares_aprovar/fundo/ilha.json
const raiz = new URL("../../../web/app/", import.meta.url);
const { CMU } = await import(new URL("motor/index.ts", raiz).href);
const { ilhaDe } = await import(new URL("src/telas/pet/ilha/grade.ts", raiz).href);
const i = ilhaDe(CMU), L = CMU.layout;
console.log(JSON.stringify({
  x0: i.x0, z0: i.z0, larg: i.larg, prof: i.prof, area: i.area,
  celulas: i.celulas.map((c: { tipo: string; nivel: number; regiao: string }) => [c.tipo, c.nivel, c.regiao]),
  objetos: i.objetos.map((o: { modelo: string; x: number; z: number; doMotor: string | null }) => [o.modelo, +o.x.toFixed(2), +o.z.toFixed(2), o.doMotor]),
  ninho: L.ninho, comedouro: L.comedouro, bola: L.bola_inicio, arvores: L.arvores, regioes: L.regioes,
}));
