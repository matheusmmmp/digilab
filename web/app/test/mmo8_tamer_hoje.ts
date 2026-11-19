/* MMO8: os registros do Tamer de hoje (antes do evento "reset" e da versao 11). Cada caso monta um registro como o jogo monta, grava e le
   de novo; o gabarito (test/gabaritos/mmo8_tamer_hoje.json, por test/gerar_gabarito_mmo8.ts) guarda o texto gravado e o estado lido. Com a
   chave do reset desligada, o jogo tem de gravar e ler estes registros byte a byte iguais. */
import { MEDALHAS, Motor } from "../motor/index.ts";
import { marcosDoTamer } from "../src/marcosTamer.ts";
import { CHAVE_TAMER, MARCO_MEGA, Tamer, conferirBits, conferirBitsDoNivel, gravarTamer, lerTamer, textoTamer, type EventoTamer } from "../src/tamer.ts";

export interface CasoTamer { nome: string; texto: string; lido: { versao: number; eventos: number; medalhas: number; titulo: boolean; bits: number; marcos: number[] } }

const armaz = (dados: Record<string, string> = {}) => ({ dados, getItem: (k: string) => dados[k] ?? null, setItem: (k: string, v: string) => { dados[k] = v; } });
const Q = 1_763_000_000_000;   // uma hora de parede fixa

/** os casos: o vazio; tres medalhas; as seis e o titulo, com um recorde; os Bits de varias origens; o marco 10; um registro 9 de antes */
export function casosHoje(): { nome: string; t: Tamer | null; bruto?: string }[] {
  const m = new Motor(101), outro = new Motor(202);
  const tres = new Tamer();
  MEDALHAS.slice(0, 3).forEach((md, i) => tres.ganhar(md.id, i < 2 ? m : outro, Q + i));
  const liga = new Tamer();
  MEDALHAS.slice(0, 6).forEach((md, i) => liga.ganhar(md.id, m, Q + i));
  liga.ganharTitulo(m, Q + 10);
  liga.baterRecorde("torre_batalha", 3, m, Q + 11);
  const bits = new Tamer();
  bits.ganhar(MEDALHAS[0].id, m, Q);
  conferirBits(bits, m, Q + 1);
  bits.ganharBits({ id: "luta:0", pet: 101, valor: 10, origem: "luta", tick: 30 }, Q + 2);
  bits.ganharBits({ id: "evolucao:crianca", pet: 202, valor: 60, origem: "evolucao", tick: 900 }, Q + 3);
  conferirBitsDoNivel(bits, 4, Q + 4);
  const marco = new Tamer();
  marco.ganharMarco(MARCO_MEGA, m, 9000, "WarGreymon", Q + 5);
  const med: EventoTamer = ["medalha", { id: MEDALHAS[0].id, n: 1, quando: Q, pet: 7, forma: "Agumon", tick: 480 }];
  return [
    { nome: "vazio", t: new Tamer() }, { nome: "tres_medalhas", t: tres }, { nome: "liga_e_recorde", t: liga },
    { nome: "bits", t: bits }, { nome: "marco_10", t: marco },
    { nome: "registro_9", t: null, bruto: JSON.stringify({ versao: 9, log: [med] }) },
  ];
}

/** grava cada caso, le de novo e devolve o texto gravado e o estado lido */
export function jogarHoje(): CasoTamer[] {
  return casosHoje().map(({ nome, t, bruto }) => {
    const a = armaz(bruto ? { [CHAVE_TAMER]: bruto } : {});
    const x = t ?? lerTamer(a);
    gravarTamer(a, x);
    const texto = a.dados[CHAVE_TAMER];
    if (texto !== textoTamer(x)) throw new Error("gravarTamer e textoTamer diferem");
    const l = lerTamer(a), d = JSON.parse(texto) as { versao: number; log: unknown[] };
    return { nome, texto, lido: { versao: d.versao, eventos: l.log.length, medalhas: l.n, titulo: !!l.titulo, bits: l.bits, marcos: marcosDoTamer(l) } };
  });
}
