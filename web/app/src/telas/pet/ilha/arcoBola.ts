/* O arco da bola no lance do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB-9; a etapa BB3). SO VISTA: o motor ja pos a bola parada no ponto do
   lance (o `lances` do Mundo, BB-1); aqui ela so voa ate la, do lado da camera (de onde o dono joga), num arco no ar, em vez de aparecer
   no lugar. Nada daqui vai ao motor, ao log nem ao save. Sem DOM nem three: as contas sao testadas em node (test/bola_brincar_vista.test.ts).
   Os numeros sao da vista: PROPOSTO, SEM FONTE. */

/** o arco: quanto dura (ms), de quantas celulas do ponto do lance a bola sai (para o lado da camera), de que altura (a mao do dono) e quanto
    sobe acima da reta (celulas) */
export const ARCO_BOLA = { ms: 650, recuo: 5, alturaMao: 1.2, altura: 1.6 } as const;

export type Par = readonly [number, number];
/** um arco em curso: quando comecou (ms da vista), de onde sai e onde cai (celulas no chao), e quanto dura */
export interface ArcoBola { desde: number; de: Par; para: Par; ms: number }

/** de onde a bola sai: `recuo` celulas a partir do ponto do lance, na direcao do chao sob a camera (`camChao`, celulas); com a camera em cima
    do ponto (ou mais perto que o recuo), sai do chao sob a camera */
export function origemDoArco(para: Par, camChao: Par, recuo: number = ARCO_BOLA.recuo): [number, number] {
  if (!(recuo >= 0) || !Number.isFinite(recuo)) throw new Error(`origemDoArco: recuo invalido ${recuo}`);
  for (const v of [...para, ...camChao]) if (!Number.isFinite(v)) throw new Error("origemDoArco: ponto nao finito");
  const dx = camChao[0] - para[0], dz = camChao[1] - para[1], d = Math.hypot(dx, dz);
  if (d <= recuo) return [camChao[0], camChao[1]];
  return [para[0] + (dx / d) * recuo, para[1] + (dz / d) * recuo];
}

/** um arco novo, a partir de `agora`, do lado da camera ate `para` */
export function novoArco(agora: number, para: Par, camChao: Par, ms: number = ARCO_BOLA.ms): ArcoBola {
  if (!(ms > 0) || !Number.isFinite(ms)) throw new Error(`novoArco: duracao invalida ${ms}`);
  return { desde: agora, de: origemDoArco(para, camChao), para: [para[0], para[1]], ms };
}

/** onde a bola esta no arco em `agora`: x e z no chao (celulas) e a altura acima dele (celulas): sai da mao (`alturaMao`), sobe ate `altura`
    acima da reta e cai no chao em `para`. `acabou` quando o tempo passou (a bola no ponto do lance, no chao). Antes de `desde`, na mao */
export function pontoDoArco(a: ArcoBola, agora: number): { x: number; z: number; y: number; acabou: boolean } {
  const f = Math.min(1, Math.max(0, (agora - a.desde) / a.ms));
  const x = a.de[0] + (a.para[0] - a.de[0]) * f, z = a.de[1] + (a.para[1] - a.de[1]) * f;
  const y = ARCO_BOLA.alturaMao * (1 - f) + 4 * ARCO_BOLA.altura * f * (1 - f);
  return { x, z, y, acabou: f >= 1 };
}

/* ------------------------------------------------------------------ o chute (BB-9: "o pet corre e chuta", com o golpe que ja existe)
   O motor diz que o pet chutou (uma rolagem nova), mas o pet desenhado pode estar a uma ou duas celulas da bola desenhada (o Seguidor anda
   atras do motor). Para o chute aparecer na bola: o pet desenhado corre ate encostar nela (`corridaMs`), da o golpe (`golpeMs`, o
   BATER_BOLA_MS da vista), e volta suave para onde o motor o pos (`voltaMs`). A bola desenhada fica parada onde estava ate o braco chegar
   (`bateEm`), e so entao rola. So o desenho. PROPOSTO, SEM FONTE */
export const CHUTE_BOLA = { corridaMs: 260, encosto: 0.7, voltaMs: 300, bateFracao: 0.3 } as const;

/** um chute em curso: quando o motor rolou a bola (ms da vista), onde a bola estava (celulas), onde o pet desenhado estava, para onde ele olha
    no golpe, e quanto dura o golpe */
export interface ChuteBola { desde: number; bola: Par; partida: Par; alvo: Par; golpeMs: number }

/** onde o pet para para chutar: `encosto` celulas antes da bola, do lado de onde ele vem (ja perto, fica onde esta) */
export function pontoDoChute(bola: Par, partida: Par, encosto: number = CHUTE_BOLA.encosto): [number, number] {
  const dx = partida[0] - bola[0], dz = partida[1] - bola[1], d = Math.hypot(dx, dz);
  if (d <= encosto) return [partida[0], partida[1]];
  return [bola[0] + (dx / d) * encosto, bola[1] + (dz / d) * encosto];
}

/** quando o braco chega a bola (ms da vista): ate la a bola desenhada fica parada */
export const bateEm = (c: ChuteBola, reduzido: boolean): number =>
  (reduzido ? c.desde : c.desde + CHUTE_BOLA.corridaMs) + c.golpeMs * CHUTE_BOLA.bateFracao;

const suave = (f: number): number => f * f * (3 - 2 * f);
const entre = (a: Par, b: Par, f: number): [number, number] => [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];

/** o passo do chute em `agora`: onde desenhar o pet (`motorCel`: onde ele estaria sem o chute), o golpe (desde quando, olhando para onde) e se
    ele anda; `acabou` depois da volta. Com movimento reduzido, so o golpe, no lugar */
export function passoDoChute(c: ChuteBola, agora: number, motorCel: Par, reduzido: boolean)
    : { cel: [number, number]; golpe: { desde: number; alvo: [number, number] } | null; andando: boolean; acabou: boolean } {
  const alvo: [number, number] = [c.alvo[0], c.alvo[1]], dt = agora - c.desde;
  if (reduzido) return dt < c.golpeMs ? { cel: [motorCel[0], motorCel[1]], golpe: { desde: c.desde, alvo }, andando: false, acabou: false }
    : { cel: [motorCel[0], motorCel[1]], golpe: null, andando: false, acabou: true };
  const { corridaMs, voltaMs } = CHUTE_BOLA, ponto = pontoDoChute(c.bola, c.partida);
  if (dt < corridaMs) return { cel: entre(c.partida, ponto, suave(Math.max(0, dt) / corridaMs)), golpe: null, andando: true, acabou: false };
  if (dt < corridaMs + c.golpeMs) return { cel: ponto, golpe: { desde: c.desde + corridaMs, alvo }, andando: false, acabou: false };
  if (dt < corridaMs + c.golpeMs + voltaMs)
    return { cel: entre(ponto, motorCel, suave((dt - corridaMs - c.golpeMs) / voltaMs)), golpe: null, andando: true, acabou: false };
  return { cel: [motorCel[0], motorCel[1]], golpe: null, andando: false, acabou: true };
}
