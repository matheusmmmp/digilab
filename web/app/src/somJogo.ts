/* O som do jogo na casca (SOM-UP, docs/TAREFA_V3_SOM_UP.md): liga os instantes de src/somEventos.ts ao SOM e pede a musica da ilha e a do
   ovo. So apresentacao: nada daqui entra no motor, no log nem no save.
   A musica da ilha (SD-6, Matheus 2026-11-10): baixa, so de dia e com o pet acordado; toca por um tempo e para por outro (o silencio entre as
   faixas), para nao cansar. A noite e o sono ficam em silencio ate o ambiente da ilha (fora desta etapa). */
import { useEffect } from "react";
import { eNoite, TPD } from "../motor/index.ts";
import { useJogo } from "./jogo.ts";
import { SOM } from "./som.ts";
import { ouvirSom, type InstanteSom } from "./somEventos.ts";

/** o ciclo da musica da ilha: toca tantos segundos e fica em silencio tantos (PROPOSTOS, SEM FONTE) */
export const CICLO_ILHA = { tocaS: 240, silencioS: 90 } as const;

/** a musica da ilha deve tocar agora? (dia, pet nascido, vivo e acordado; e a parte "toca" do ciclo desde `desde`) */
export function ilhaToca(o: { noite: boolean; nascendo: number; morto: boolean; dormindo: boolean }, agoraS: number, desdeS: number): boolean {
  if (o.noite || o.nascendo > 0 || o.morto || o.dormindo) return false;
  const t = (agoraS - desdeS) % (CICLO_ILHA.tocaS + CICLO_ILHA.silencioS);
  return t < CICLO_ILHA.tocaS;
}

const desde = performance.now() / 1000;

/** o instante emitido vira som (src/somEventos.ts) */
export function tocarInstante(i: InstanteSom): void {
  if (i.tipo === "efeito") void SOM.efeito(i.efeito);
  else if (i.tipo === "golpe") void SOM.tocar(i.evento, i.sprite, i.habilidade);
  else void SOM.pedirMusica(i.fonte, i.alvo);
}

let ouvindo = false;

export function useSomDoJogo(): void {
  /* liga no primeiro render da casca, nao num efeito: os filhos emitem nos efeitos deles, que rodam antes dos da casca */
  if (!ouvindo) { ouvindo = true; ouvirSom(tocarInstante); }
  const { motor: m, nascendo } = useJogo();
  const noite = eNoite(m.e.tick % TPD), morto = !!m.morte, dormindo = !!m.e.dormindo;
  /* o ovo chocando: a musica do nascimento do Digimon UP */
  useEffect(() => { void SOM.pedirMusica("nascimento", nascendo > 0 ? { lugar: "nascimento" } : null); }, [nascendo > 0]);
  /* a ilha: confere a cada segundo (o ciclo anda no relogio da tela; o dia e o sono, no motor) */
  useEffect(() => {
    const o = { noite, nascendo, morto, dormindo };
    const conferir = (): void => { void SOM.pedirMusica("ilha", ilhaToca(o, performance.now() / 1000, desde) ? { lugar: "ilha" } : null); };
    conferir();
    const t = setInterval(conferir, 1000);
    return () => clearInterval(t);
  }, [noite, nascendo, morto, dormindo]);
}
