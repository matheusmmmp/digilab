/* O efeito do chamado de fome pela fome do corpo no bebe (docs/TAREFA_V2_PRODUTO_FOME.md; pedido do Gerente, 2026-10-29): quantos chamados
   de fome abrem no ritmo rapido e no classico, com e sem as chaves do produto, e a fracao de cuidado com que o bebe evolui (o ramo da
   crianca: sereno com 0,8 ou mais, arisco abaixo; CAT.limiarCuidado). So le o motor; nao muda nada do jogo.

     node --experimental-strip-types test/medir_chamado_fome.ts     # grava test/efeito_chamado_fome.json

   Os donos sao roteiros simples (SEM FONTE; o dono sintetico de motor/donos.ts usa o elogio e a bronca, que o v12 nao tem):
     nada            nao faz nada;
     atende          atende todo chamado no tick em que ele abre (a fome com o alimentar, a racao no comedouro);
     atende_10min    atende todo chamado 10 min depois de abrir (ainda dentro da janela de 15);
     brinca_atende   brinca a cada 20 min na primeira hora (o brincar gasta fome) e atende todo chamado no tick em que ele abre;
     so_alimenta     atende so o chamado de fome, no tick em que ele abre;
     nao_alimenta    atende so os de higiene e de carinho, no tick em que eles abrem (nunca alimenta). */
import { writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { ACAO_CHAMADO, CHAMADO_FOME_CORPO, TICK_INICIAL } from "../motor/constantes.ts";
import { Motor } from "../motor/motor.ts";
import type { Chamado } from "../motor/tipos.ts";

const SEMENTES = [101, 202, 303];
const DONOS = ["nada", "atende", "atende_10min", "brinca_atende", "so_alimenta", "nao_alimenta"] as const;
type NomeDono = typeof DONOS[number];
const SAIDA = new URL("./efeito_chamado_fome.json", import.meta.url);

function vida(semente: number, ritmo: "rapida" | "classica", chave: boolean, dono: NomeDono) {
  const m = new Motor(semente, 12);
  if (ritmo === "classica") m.configurar("classica");
  if (chave) m.ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true });
  const abriu: Record<Chamado, number> = { fome: 0, higiene: 0, carinho: 0 };
  const visto: Partial<Record<Chamado, number>> = {}, fomeAoAbrir: number[] = [];
  const atrasados: [number, Chamado][] = [];
  while (m.estagioAtual === "bebe") {
    m.avancar(1);
    if (m.estagioAtual !== "bebe") break;
    const t = m.e.tick - TICK_INICIAL, ab = m.chamados.abertos;
    for (const c of Object.keys(ab) as Chamado[]) if (visto[c] !== ab[c]) {
      visto[c] = ab[c]; abriu[c]++;
      if (c === "fome") fomeAoAbrir.push(m.e.fome);
      if (dono === "atende" || dono === "brinca_atende" || (dono === "so_alimenta" && c === "fome") || (dono === "nao_alimenta" && c !== "fome"))
        m.observar(ACAO_CHAMADO[c][0]);
      else if (dono === "atende_10min") atrasados.push([m.e.tick + 10, c]);
    }
    for (let i = atrasados.length - 1; i >= 0; i--) if (atrasados[i][0] === m.e.tick) {
      const [, c] = atrasados.splice(i, 1)[0];
      if (c in m.chamados.abertos) m.observar(ACAO_CHAMADO[c][0]);
    }
    if (dono === "brinca_atende" && t <= 60 && t % 20 === 0) m.observar("brincar");
  }
  const ev = m.evolucoes[0] as { cuidado?: number; ramo?: string };
  return { chamados_abertos: abriu, fome_ao_abrir: fomeAoAbrir.map(f => Math.round(f * 1000) / 1000),
    cuidado: ev.cuidado ?? null, ramo: ev.ramo ?? null };
}

/** a medicao inteira (o test/produto_fome.test.ts confere que o arquivo gravado esta em dia) */
export function medirEfeito() {
  const vidas = [];
  for (const ritmo of ["rapida", "classica"] as const) for (const dono of DONOS) for (const chave of [false, true]) for (const s of SEMENTES)
    vidas.push({ ritmo, dono, chave, semente: s, ...vida(s, ritmo, chave, dono) });
  return {
    descricao: "o efeito do chamado de fome pela fome do corpo no bebe do pet v12: os chamados abertos no bebe e a fracao de cuidado da "
      + "evolucao para a crianca, com e sem as chaves do produto (o evento \"p\"), nos ritmos rapido (180 min) e classico (360 min)",
    limiar: CHAMADO_FOME_CORPO.limiar, sementes: SEMENTES, donos: DONOS, vidas,
  };
}
export const textoEfeito = (): string => JSON.stringify(medirEfeito(), null, 1) + "\n";

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  writeFileSync(SAIDA, textoEfeito());
  for (const l of medirEfeito().vidas) console.log(l.ritmo, l.dono.padEnd(13), l.chave ? "chave" : "hoje ", l.semente,
    JSON.stringify(l.chamados_abertos), "cuidado", l.cuidado?.toFixed(3), l.ramo);
}
