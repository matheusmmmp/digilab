/* A voz do pet (docs/PLANO_V3_HABITAT_REACOES.md, HR2; HR-3 e HR-4 aprovadas pelo Matheus em 2026-11-11). Ate a voz por especie pelo genoma (S7,
   HR5), a voz e um arquivo so do Digimon UP (o efeito "voz", sfx_digimon_voice) com o tom mudado: pela especie, pelo estagio (o bebe mais agudo,
   o adulto mais grave) e pelo humor (contente, resmungo, susto, choro, bocejo, chamando). Entre duas falas, uma pausa minima, para o pet nao
   ficar tagarela. So apresentacao: nada daqui entra no motor, no log nem no save. Sem DOM e sem audio aqui (testado em node). */

/** os humores da voz */
export const HUMORES_VOZ = ["contente", "resmungo", "susto", "choro", "bocejo", "chamando"] as const;
export type HumorVoz = (typeof HUMORES_VOZ)[number];

/** os numeros da voz (PROPOSTOS, SEM FONTE; a rodada de equilibrio e o ouvido do Matheus acertam) */
export const VOZ = {
  /** a pausa minima entre duas falas do pet, em ms (HR-4): a resposta a um gesto do dono */
  pausaMs: 4000,
  /** a pausa antes da voz espontanea (o pet dorme, acorda, chama, muda de acao sozinho), em ms: com o tempo a 10 min/s ele muda de acao a cada
      ~1,5 s, e a pausa de 4 s deixava a voz tocando sem parar (Matheus, 2026-11-12: "irrita"). PROPOSTO, SEM FONTE */
  pausaEspontaneaMs: 30000,
  /** o tom de cada humor (a taxa de reproducao: 1 = o arquivo como e) */
  humor: { contente: 1.15, resmungo: 0.8, susto: 1.4, choro: 0.9, bocejo: 0.65, chamando: 1.25 } as Readonly<Record<HumorVoz, number>>,
  /** o tom de cada especie (o brasao: brasa Coragem, cirro Amizade, ferrugem Conhecimento, limo Sinceridade) */
  especie: { brasa: 1, cirro: 1.1, ferrugem: 0.9, limo: 1.05 } as Readonly<Record<string, number>>,
  /** o tom de cada estagio: o bebe mais agudo, o adulto mais grave */
  estagio: { bebe: 1.3, crianca: 1.15, adolescente: 1, adulto: 0.9, mega: 0.85 } as Readonly<Record<string, number>>,
  /** a taxa fica dentro disto (o arquivo distorce demais fora) */
  min: 0.5, max: 2,
} as const;

/** a taxa da voz: humor x especie x estagio, dentro de [min, max]. Especie ou estagio desconhecido falha alto */
export function taxaDaVoz(humor: HumorVoz, especie: string, estagio: string): number {
  const h = VOZ.humor[humor], e = VOZ.especie[especie], g = VOZ.estagio[estagio];
  if (h === undefined) throw new Error("humor de voz desconhecido: " + humor);
  if (e === undefined) throw new Error("especie sem tom de voz: " + especie);
  if (g === undefined) throw new Error("estagio sem tom de voz: " + estagio);
  return Math.min(VOZ.max, Math.max(VOZ.min, h * e * g));
}

/** a pausa da voz: devolve true (e marca) se o pet pode falar agora; false se falou ha menos de VOZ.pausaMs (a resposta ao dono) ou de
    VOZ.pausaEspontaneaMs (a voz espontanea) */
let ultima = -Infinity;
export function podeFalar(agora: number, espontanea = false): boolean {
  if (!Number.isFinite(agora)) throw new Error("podeFalar: agora nao finito");
  if (agora - ultima < (espontanea ? VOZ.pausaEspontaneaMs : VOZ.pausaMs)) return false;
  ultima = agora;
  return true;
}
/** so para os testes */
export function esquecerVoz(): void { ultima = -Infinity; }
