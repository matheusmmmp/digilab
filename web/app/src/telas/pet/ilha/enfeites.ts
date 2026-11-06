/* Os enfeites do mundo humano na moldura da ilha (docs/TAREFA_V3_MUNDO_ENFEITES.md): so vista. A grade (grade.ts, porEnfeites) diz onde
   ficam; aqui cada modelo de ENFEITES_MODELOS (public/enfeites/<nome>/) entra pelo carregarVariante dos kits e vira um InstancedMesh por
   peca, como os objetos da grade: varios postes custam o de um (E-G9). Cada enfeite tem a sombra redonda. A noite, o que tem luz acende:
   as partes da mascara (ENFEITES_LUZ, o emissiveMap) brilham na cor da luz do ninho, e um brilho no chao sob a lampada (o raio e a cor
   de LUZ_NINHO) e um halo na lanterna (ENFEITE_HALO: cascas translucidas, um desenho por casca para todos), aditivos; nada disso ilumina o
   resto da cena.
   O giro da grade vira a frente do enfeite para a area andavel; num modelo com a lampada para um lado (o poste), a "frente" e o lado da
   lampada, achado pelo ponto mais alto do modelo. Os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { GEO_SOMBRA, carregarVariante, curvar, materialSombra } from "./cena.ts";
import { ENFEITE_HALO, LUZ_NINHO } from "./constantes.ts";
import type { Ilha } from "./grade.ts";
import { ENFEITES_LUZ, ENFEITES_MODELOS, type NomeEnfeite } from "./modelos.ts";

/** os enfeites prontos: o grupo e o que a vista chama quando a noite muda (acende ou apaga as luzes) */
export interface Enfeites { grupo: THREE.Group; noite: (noite: boolean) => void }

/** onde fica a lampada de um modelo (x, z depois da normalizacao): o vertice mais alto; [0, 0] se o modelo nao tem para que lado */
function lampada(pecas: { geo: THREE.BufferGeometry; local: THREE.Matrix4 }[]): [number, number] {
  let topo = -Infinity, x = 0, z = 0;
  const v = new THREE.Vector3();
  for (const p of pecas) {
    const pos = p.geo.getAttribute("position");
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).applyMatrix4(p.local);
      if (v.y > topo + 1e-6) { topo = v.y; x = v.x; z = v.z; }
    }
  }
  return [x, z];
}

/** o brilho no chao (a textura da luz do ninho) */
function texturaBrilho(): THREE.Texture {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const x = c.getContext("2d");
  if (!x) throw new Error("canvas 2d indisponível");
  const gr = x.createRadialGradient(32, 32, 2, 32, 32, 31);
  gr.addColorStop(0, `rgba(${LUZ_NINHO.cor},0.55)`); gr.addColorStop(1, `rgba(${LUZ_NINHO.cor},0)`);
  x.fillStyle = gr; x.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

/** carrega os modelos e poe os enfeites da ilha; falha alto se um arquivo nao carrega (a ilha cai na reserva, como sem os kits) */
export async function enfeites(ilha: Ilha, base: string): Promise<Enfeites> {
  const grupo = new THREE.Group(), luzes = new THREE.Group(), gltf = new GLTFLoader();
  const sombras: { x: number; z: number; r: number }[] = [], brilhos: [number, number][] = [], acesos: THREE.MeshToonMaterial[] = [];
  const halos: number[] = [];
  for (const nome of Object.keys(ENFEITES_MODELOS) as NomeEnfeite[]) {
    const lista = ilha.enfeites.filter(e => e.nome === nome);
    if (!lista.length) continue;
    const m = ENFEITES_MODELOS[nome];
    const { pecas } = await carregarVariante(gltf, new URL("enfeites/" + m.arquivos[0], base).href, m);
    /* so o que tem luz tem um lado (a lanterna); os outros viram a frente do glTF (+z) para a area */
    const [lx, lz] = ENFEITES_LUZ[nome] ? lampada(pecas) : [0, 0], lado = Math.hypot(lx, lz) > 1e-3 ? Math.atan2(lx, lz) : 0;
    const lugar = lista.map(e => {
      const giro = e.giro - lado, y = ilha.altura(e.x, e.z);
      if (ENFEITES_LUZ[nome]) {
        const bx = e.x + Math.sin(giro) * lz + Math.cos(giro) * lx, bz = e.z + Math.cos(giro) * lz - Math.sin(giro) * lx;
        brilhos.push([bx, bz]);
        halos.push(bx, ilha.altura(bx, bz) + m.altura * ENFEITE_HALO.altura, bz);
      }
      sombras.push({ x: e.x, z: e.z, r: m.sombra });
      return new THREE.Matrix4().compose(new THREE.Vector3(e.x, y, e.z), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), giro),
        new THREE.Vector3(1, 1, 1));
    });
    const luz = ENFEITES_LUZ[nome];
    if (luz) {
      /* a mascara usa os UVs do glTF: sem virar a imagem, como o GLTFLoader faz com as texturas dele */
      const t = await new THREE.TextureLoader().loadAsync(new URL("enfeites/" + luz, base).href);
      t.flipY = false;
      for (const p of pecas) {
        const m = p.mat as THREE.MeshToonMaterial;
        m.emissiveMap = t; m.emissive.setStyle(`rgb(${LUZ_NINHO.cor})`); m.emissiveIntensity = 0;
        m.needsUpdate = true;
        acesos.push(m);
      }
    }
    for (const p of pecas) {
      const im = new THREE.InstancedMesh(p.geo, p.mat, lista.length);
      lugar.forEach((l, i) => im.setMatrixAt(i, l.clone().multiply(p.local)));
      im.frustumCulled = false;     // a dobra muda onde a peca aparece; o volume do three nao sabe disso
      grupo.add(im);
    }
  }
  if (sombras.length) {
    const s = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), sombras.length);
    sombras.forEach((o, i) => s.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(o.x, ilha.altura(o.x, o.z) + 0.02, o.z),
      new THREE.Quaternion(), new THREE.Vector3(o.r * 2, 1, o.r * 2))));
    s.frustumCulled = false;
    s.renderOrder = 1;
    grupo.add(s);
  }
  if (brilhos.length) {
    const mat = curvar(new THREE.MeshBasicMaterial({ map: texturaBrilho(), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
    const b = new THREE.InstancedMesh(GEO_SOMBRA, mat, brilhos.length), d = LUZ_NINHO.raio * 2;
    brilhos.forEach(([x, z], i) => b.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(x, ilha.altura(x, z) + 0.05, z),
      new THREE.Quaternion(), new THREE.Vector3(d, 1, d))));
    b.frustumCulled = false;
    b.renderOrder = 1;
    luzes.add(b);
  }
  if (halos.length) {
    /* o halo: cascas translucidas e aditivas em volta da lanterna, uma dentro da outra (a soma cai do centro para a borda, sem a borda
       dura de uma esfera so); a frente delas passa na frente do vidro. Um desenho por casca, para todos os postes */
    const n = halos.length / 3, cor = new THREE.Color(`rgb(${LUZ_NINHO.cor})`);
    for (const f of ENFEITE_HALO.cascas) {
      const mat = curvar(new THREE.MeshBasicMaterial({ color: cor, transparent: true, opacity: ENFEITE_HALO.forca, depthWrite: false,
        blending: THREE.AdditiveBlending }));
      const h = new THREE.InstancedMesh(new THREE.SphereGeometry((ENFEITE_HALO.tamanho * f) / 2, 16, 12), mat, n);
      for (let i = 0; i < n; i++) h.setMatrixAt(i, new THREE.Matrix4().makeTranslation(halos[3 * i], halos[3 * i + 1], halos[3 * i + 2]));
      h.frustumCulled = false;
      h.renderOrder = 2;
      luzes.add(h);
    }
  }
  luzes.visible = false;
  grupo.add(luzes);
  return { grupo, noite: n => { luzes.visible = n; for (const m of acesos) m.emissiveIntensity = n ? ENFEITE_HALO.vidro : 0; } };
}
