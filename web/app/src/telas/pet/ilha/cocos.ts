/* O coco no chao da ilha (2026-11-04, pedido do Matheus: "que ele efetivamente faca o coco 3D no mapa"). Antes, a sujeira do motor
   (e.sujeira, uma contagem) virava a grade 2D do coco presa ao lado do sprite, no canvas por cima (PalcoPet.tsx). Agora cada unidade de
   sujeira e um coco 3D no chao, no lugar onde o pet estava quando a sujeira subiu, e fica ali quando o pet anda; o Limpar tira os cocos.
   So vista: o motor guarda so a contagem, sem o lugar, entao o lugar e da vista:
     - um coco novo cai perto de onde a vista desenha o pet naquele quadro, num anel em volta dele (lugarDoCoco), para dois cocos seguidos
       nao cairem um em cima do outro;
     - os cocos que ja estavam la quando a ilha abre (um save recarregado) aparecem em volta do pet, do mesmo jeito: o lugar de antes nao
       foi gravado (o log nao muda);
     - quando a contagem cai, saem os mais antigos primeiro.
   O desenho (procedural, no material toon da ilha: tres voltas achatadas e a ponta, com a sombra redonda) fica em itens.ts, que o passa
   ao construtor; este arquivo nao importa a cena (que cria canvas ao carregar), para o teste rodar sem DOM. Surge com um pulinho.
   Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { COCO } from "./constantes.ts";

/** o angulo de ouro (radianos): os cocos seguidos se espalham pelo anel sem repetir o lugar */
const OURO = Math.PI * (3 - Math.sqrt(5));

/** onde cai o coco de numero `i` (a contagem de cocos que a vista ja fez cair), em celulas, em volta do pet em `pet` (celulas) */
export function lugarDoCoco(pet: readonly [number, number], i: number): [number, number] {
  const a = 0.7 + i * OURO, r = COCO.raio + (i % 3) * COCO.passo;
  return [pet[0] + Math.cos(a) * r, pet[1] + Math.sin(a) * r];
}

/** o tamanho do pulinho ao surgir: 0 ate 1 em COCO.surgirMs, passando um pouco de 1 (um ease-out-back) */
export function escalaAoSurgir(desdeMs: number): number {
  if (desdeMs >= COCO.surgirMs) return 1;
  const t = Math.max(0, desdeMs) / COCO.surgirMs, c = 1.7, u = t - 1;
  return Math.max(0, 1 + (c + 1) * u * u * u + c * u * u);
}

export class Cocos {
  readonly raiz = new THREE.Group();
  private readonly lista: { g: THREE.Object3D; desde: number }[] = [];
  /** quantos cocos a vista ja fez cair (o numero do proximo, para lugarDoCoco) */
  private feitos = 0;
  /** o primeiro quadro: os cocos que ja estavam la nao fazem o pulinho */
  private primeiro = true;

  /** `criar(i)`: o desenho do coco de numero i */
  private readonly criar: (i: number) => THREE.Object3D;
  constructor(criar: (i: number) => THREE.Object3D) { this.criar = criar; }

  /** quantos cocos estao no chao */
  get quantos(): number { return this.lista.length; }
  /** onde estao (celulas), do mais antigo ao mais novo */
  get lugares(): [number, number][] { return this.lista.map(c => [c.g.position.x, c.g.position.z]); }

  /** a sujeira do motor (`n`) no chao: cai um coco por unidade nova, perto do pet (`pet`, celulas); saem os mais antigos quando ela cai */
  sincronizar(n: number, pet: readonly [number, number], agora: number, reduzido: boolean): void {
    if (!Number.isInteger(n) || n < 0) throw new Error("sujeira invalida para o coco na ilha: " + n);
    while (this.lista.length < n) {
      const i = this.feitos++, [x, z] = lugarDoCoco(pet, i), g = this.criar(i);
      g.position.set(x, 0, z);
      this.raiz.add(g);
      this.lista.push({ g, desde: this.primeiro || reduzido ? -Infinity : agora });
    }
    while (this.lista.length > n) {
      const c = this.lista.shift();
      if (c) this.raiz.remove(c.g);
    }
    this.primeiro = false;
    for (const c of this.lista) c.g.scale.setScalar(escalaAoSurgir(agora - c.desde));
  }
}
