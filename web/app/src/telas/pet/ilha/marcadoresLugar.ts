/* Os marcadores provisorios do portao da arena e da barraca do Tamer (L3 de "Lugares da ilha"; os pontos, o giro e a altura estao em lugares.ts).
   Enquanto o glTF de cada lugar nao chega (`modelo` null em lugares.ts), a vista desenha aqui um volume simples e neutro: pouca geometria (um
   punhado de caixas e uma piramide), um material toon por cor (compartilhado) e uma geometria por tamanho (compartilhada), e nenhum custo por quadro
   (o grupo e montado uma vez e fica parado). As cores sao as dos tokens da pele (--hx-rotulo, --hx-texto-2, --hx-sec), lidas do CSS na montagem;
   nenhuma cor nova. `montarMarcadores` devolve tambem o `dispose`, que a vista chama ao desligar (a GEO_SOMBRA e a textura da sombra sao do modulo
   cena.ts e ficam).
   A TROCA PELO MODELO e so apontar `modelo` em lugares.ts: a vista carrega o glTF (carregarVariante, cena.ts), redimensiona-o ate `altura`, poe o
   pivo no centro da base e o giro de `giro`. O MARCADOR FICA ATE O MODELO CARREGAR (so entao sai, `porLugar` dá o grupo de cada lugar), e a FALHA DO
   glTF DEVE SER ALTA (erro no console e na tela, como a dos kits em vista.ts; nunca um lugar sem nada e em silencio). O "trancado" e o mesmo desenho
   apagado (o `Apagador` abaixo escurece as cores dos materiais do lugar; cada lugar tem os seus), e o cadeado com o "Nv N" e DOM (CadeadosDaIlha.tsx); o
   modelo 3D do cadeado vem depois do ITENS_3D. So vista: o motor nao sabe dos lugares. */
import * as THREE from "three";
import { toon, GEO_SOMBRA, materialSombra } from "./cena.ts";
import { LUGARES, type BaseDoMundo, type IdLugar } from "./lugares.ts";

/** a cor de um token da pele de agora (--hx-*); falha alto se o token faltar */
export function corDoToken(nome: string): THREE.Color {
  const v = getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
  if (!v) throw new Error("token de pele sem valor: " + nome);
  return new THREE.Color().set(v);
}

/** quanto as cores escurecem num lugar trancado (1 = sem mudar). PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
export const FATOR_APAGADO = 0.4;
/** apaga (escurece) ou devolve as cores dos materiais toon de um lugar, no lugar mesmo (cada lugar tem os seus materiais: nao se partilham). Guarda a cor de antes */
export class Apagador {
  private readonly base = new Map<THREE.MeshToonMaterial, THREE.Color>();
  aplicar(raiz: THREE.Object3D, apagado: boolean): void {
    raiz.traverse(o => {
      if (!(o instanceof THREE.Mesh)) return;
      const m = o.material;
      if (Array.isArray(m)) throw new Error("Apagador: material em lista num lugar da ilha (nao esperado: cada malha tem um so)");
      if (!(m instanceof THREE.MeshToonMaterial)) return;      // a sombra (MeshBasic) fica como esta
      const antes = this.base.get(m);
      if (apagado && !antes) { this.base.set(m, m.color.clone()); m.color.multiplyScalar(FATOR_APAGADO); }
      else if (!apagado && antes) { m.color.copy(antes); this.base.delete(m); }
    });
  }
}

export interface Marcadores {
  raiz: THREE.Group;
  /** o grupo de cada lugar com marcador (so os que ainda nao tem modelo) */
  porLugar: Map<IdLugar, THREE.Group>;
  /** solta as geometrias e os materiais deste conjunto (nao toca na GEO_SOMBRA nem na textura da sombra, que sao do modulo) */
  dispose: () => void;
}

/** os marcadores (portao e barraca) nos pontos de lugares.ts, para a vista pôr na cena. O saco tem o desenho dele em itens.ts */
export function montarMarcadores(base: BaseDoMundo): Marcadores {
  const raiz = new THREE.Group(), porLugar = new Map<IdLugar, THREE.Group>();
  const materiais = new Map<string, THREE.Material>(), geometrias = new Map<string, THREE.BufferGeometry>(), sombras: THREE.Material[] = [];
  /* os materiais sao por lugar (o trancado escurece os de um lugar so) */
  let lugarAgora = "";
  const mat = (token: string): THREE.Material => {
    const chave = lugarAgora + ":" + token;
    let m = materiais.get(chave);
    if (!m) { m = toon({ color: corDoToken(token) }); materiais.set(chave, m); }
    return m;
  };
  const caixa = (l: number, a: number, p: number, token: string, x: number, y: number, z: number): THREE.Mesh => {
    const chave = `caixa:${l}:${a}:${p}`;
    let g = geometrias.get(chave);
    if (!g) { g = new THREE.BoxGeometry(l, a, p); geometrias.set(chave, g); }
    const m = new THREE.Mesh(g, mat(token));
    m.position.set(x, y, z);
    return m;
  };
  const sombra = (r: number): THREE.Mesh => {
    const mt = materialSombra(), s = new THREE.Mesh(GEO_SOMBRA, mt);
    sombras.push(mt);
    s.scale.set(r * 2, 1, r * 2); s.position.y = 0.02; s.renderOrder = 1;
    return s;
  };
  /* o portao: dois pilares e a viga de cima, com uma placa no meio (a altura de lugares.ts; a frente em +z) */
  const portao = (altura: number): THREE.Group => {
    const g = new THREE.Group(), vao = altura * 0.8, larg = altura * 0.9;
    g.add(sombra(larg * 0.7),
      caixa(0.5, altura, 0.5, "--hx-texto-2", -larg / 2, altura / 2, 0), caixa(0.5, altura, 0.5, "--hx-texto-2", larg / 2, altura / 2, 0),
      caixa(larg + 0.9, 0.5, 0.6, "--hx-texto-2", 0, vao + 0.1, 0), caixa(larg * 0.4, 0.5, 0.12, "--hx-rotulo", 0, vao + 0.1, 0.34));
    return g;
  };
  /* a barraca: uma piramide de quatro faces com a porta (uma caixa fina) na frente */
  const barraca = (altura: number): THREE.Group => {
    const g = new THREE.Group(), r = LUGARES.barraca.raio, chave = `cone:${r}:${altura}`;
    let geo = geometrias.get(chave);
    if (!geo) { geo = new THREE.ConeGeometry(r, altura, 4, 1).rotateY(Math.PI / 4); geometrias.set(chave, geo); }
    const corpo = new THREE.Mesh(geo, mat("--hx-sec"));
    corpo.position.y = altura / 2;
    g.add(sombra(r * 1.1), corpo, caixa(r * 0.4, altura * 0.45, 0.1, "--hx-rotulo", 0, altura * 0.225, r * 0.55));
    return g;
  };
  for (const id of ["portao", "barraca"] as const satisfies readonly IdLugar[]) {
    const l = LUGARES[id];
    if (l.modelo !== null) continue;                    // o modelo chegou: a vista o carrega (o marcador fica ate la)
    lugarAgora = id;
    const g = id === "portao" ? portao(l.altura) : barraca(l.altura), [x, z] = l.ponto(base);
    g.position.set(x, 0, z); g.rotation.y = l.giro; g.name = "lugar-" + id;
    raiz.add(g); porLugar.set(id, g);
  }
  const dispose = () => {
    for (const g of geometrias.values()) g.dispose();
    for (const m of materiais.values()) m.dispose();
    for (const m of sombras) m.dispose();
    geometrias.clear(); materiais.clear(); sombras.length = 0; porLugar.clear(); raiz.clear();
  };
  return { raiz, porLugar, dispose };
}
