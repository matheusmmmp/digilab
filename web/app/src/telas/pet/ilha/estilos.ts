/* Os estilos do habitat (src/habitat.ts, caminho A de 2026-10-31): cada mapa e uma vista da MESMA grade do motor (grade.ts), so com outro
   terreno, outros modelos e outra dobra. A area andavel, a moldura, os objetos e o lugar do pet nao mudam; a vista (vista.ts) e a mesma.
     - ilha: a da L4 (cena.ts), com o mundo curvo (DOBRA_K) e os kits CC0 de public/kits3d;
     - digital: a ilha no fundo de anime (docs/TAREFA_V3_MAPA_DIGITAL.md), com o ceu pintado e os dois tons;
     - voxel: a ilha em cubos (voxel.ts), sem asset;
     - floresta: o kit Tiny Fantasy Forest (floresta.ts), so no dev;
     - cassette: as texturas e as arvores do Cassette Beasts (cassette.ts), so no dev.
   Os tres novos sao planos, como os POCs do #480 (a dobra e do estilo Animal Crossing). */
import type { Mapa } from "../../../habitat.ts";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { PALETA_DIGITAL, PALETA_ILHA, carregarVariante, doisTons, flores, montarCena, objetos, terreno, tufos, usarDoisTons, type CenaIlha, type Objetos,
  type PaletaTerreno } from "./cena.ts";
import { arquivosCassette, carregadorCassette, terrenoCassette } from "./cassette.ts";
import { CEU_DIGITAL, CEU_SEM_PINTURA, CONTORNO_DIGITAL, DOBRA_K } from "./constantes.ts";
import { ceuComGrade, ceuEmFaixas, fios, lata, nuvensDaPintura, particulas, separarNuvens, suavizarPintura } from "./digital.ts";
import { enfeites } from "./enfeites.ts";
import { lugares } from "./lugaresCena.ts";
import { PALETA_FLORESTA, arquivosFloresta, carregadorFloresta } from "./floresta.ts";
import type { Ilha } from "./grade.ts";
import type { Contorno } from "./pos.ts";
import { objetosVoxel, terrenoVoxel } from "./voxel.ts";

/** o ceu do estilo digital: o de CEU_SEM_PINTURA, ou o de `?ceu=pixel|suave|pintado` no endereco (so a pagina, para comparar; nao grava) */
function modoDoCeu(): "pixel" | "suave" | "pintado" {
  try {
    const q = new URLSearchParams(location.search).get("ceu");
    if (q === "pixel" || q === "suave" || q === "pintado") return q;
  } catch { /* sem endereco */ }
  return CEU_SEM_PINTURA.modo;
}

export interface Estilo {
  readonly id: Mapa;
  /** a dobra do mundo curvo, por celula (0: plano) */
  readonly dobra: number;
  /** a cena estatica: o ceu, as luzes, o terreno e a agua */
  montar(ilha: Ilha): CenaIlha;
  /** os objetos da grade (podem baixar arquivos; falham alto se faltar um) */
  objetos(ilha: Ilha): Promise<Objetos>;
  /** o traco de nanquim em tudo (pos.ts; o estilo digital, D5) */
  readonly contorno?: Contorno;
  /** as cores do minimapa (ilha/minimapa.ts): a paleta do terreno do estilo; o Voxel e o Cassette, que pintam o terreno por outro
      caminho, usam a da ilha (o mesmo layout, as mesmas regioes) */
  readonly paleta: PaletaTerreno;
}

/** o estilo de um mapa; `base` e a URL da pagina (document.baseURI), de onde saem os caminhos dos kits */
export function estiloDe(mapa: Mapa, base: string): Estilo {
  const e = estiloSemTons(mapa, base);
  /* os materiais toon que a vista cria depois de montar (os itens, os modelos) seguem os tons do estilo (cena.ts, usarDoisTons) */
  return { ...e, montar: i => { usarDoisTons(e.id === "digital"); return e.montar(i); } };
}

function estiloSemTons(mapa: Mapa, base: string): Estilo {
  switch (mapa) {
    case "ilha": return {
      id: mapa, dobra: DOBRA_K, paleta: PALETA_ILHA, montar: i => montarCena(i),
      /* os enfeites do mundo humano (enfeites.ts) so neste estilo (docs/TAREFA_V3_MUNDO_ENFEITES.md, D-EN-3), e os lugares (lugaresCena.ts) */
      objetos: async i => {
        const [o, e, g] = await Promise.all([objetos(i, base), enfeites(i, base), lugares(i, base)]);
        o.grupo.add(e.grupo, g.grupo);
        return { ...o, noite: e.noite, lugares: g.caixas, lugaresRaiz: g.raizes, abrirLugar: g.abrir };
      },
    };
    case "digital": {
      /* o estilo digital (docs/TAREFA_V3_MAPA_DIGITAL.md, D1 e D2): a mesma ilha e os mesmos objetos, no fundo de anime: o ceu pintado
         (public/mapa_digital/ceu.jpg), a paleta chapada com as flores, o barranco de pedra, os kits recoloridos e o toon de dois tons
         em tudo, os itens inclusive (usarDoisTons) */
      /* o ceu (CEU_SEM_PINTURA, 2026-11-08): em pixel (o padrao), suave ou o pintado de antes, com a grade digital por cima (D3, digital.ts) */
      const modo = modoDoCeu(), S = CEU_SEM_PINTURA, ceuDia = new THREE.Texture();
      /* no pintado, as nuvens saem da imagem e vao para o mundo (NUVENS_PINTADAS): o fundo fica so o degrade, e uma camada de nuvens so */
      const pintura = modo !== "pintado" ? null : new Promise<{ ceu: HTMLCanvasElement; nuvens: HTMLCanvasElement }>((ok, falha) => {
        new THREE.TextureLoader().load(new URL("mapa_digital/ceu.jpg", base).href, t => {
          const partes = separarNuvens(suavizarPintura(t.image, S.pintura.saturacao, S.pintura.clarear));
          ceuDia.image = ceuComGrade(partes.ceu); ceuDia.needsUpdate = true;
          ok(partes);
        }, undefined, falha);
      });
      if (pintura) {
      } else {
        const [w, h] = S.tela;
        ceuDia.image = ceuComGrade(ceuEmFaixas(S.cores, modo === "pixel" ? S.faixas : h, w, h));
        if (modo === "pixel") { ceuDia.magFilter = THREE.NearestFilter; ceuDia.minFilter = THREE.NearestFilter; ceuDia.generateMipmaps = false; }
        ceuDia.needsUpdate = true;
      }
      ceuDia.colorSpace = THREE.SRGBColorSpace;
      ceuDia.userData.cobrir = true;    /* cobre a tela sem esticar (cena.ts, cobrirFundo) */
      const horizonte = modo === "pintado" ? CEU_DIGITAL.horizonte : S.horizonte;
      return {
        id: mapa, dobra: DOBRA_K, paleta: PALETA_DIGITAL, contorno: CONTORNO_DIGITAL,
        montar: i => {
          const chao = new THREE.Group().add(terreno(i, PALETA_DIGITAL), flores(i), tufos(i));
          const nuvensPintura = new THREE.Group();
          if (pintura) {
            const parado = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
            pintura.then(p => nuvensDaPintura(nuvensPintura, p.nuvens, i, parado), e => { throw e; });
          }
          const c = montarCena(i, chao, { nuvens: pintura ? nuvensPintura : modo === "pixel" ? "pixel" : true, ceuDia, horizonteDia: horizonte, chaoHemi: CEU_DIGITAL.chaoHemi, nevoa: CEU_DIGITAL.nevoa });
          doisTons(c.cena);
          return c;
        },
        objetos: async i => {
          /* os kits com as texturas recoloridas do estilo (public/kits3d_digital/, docs/mapa_digital/kits_digital.py; D2) */
          const gltf = new GLTFLoader();
          const kits = (arq: string, _id: string, modelo: Parameters<typeof carregarVariante>[2]) =>
            carregarVariante(gltf, new URL("kits3d_digital/" + arq, base).href, modelo);
          const [o, e, l, g] = await Promise.all([objetos(i, base, kits), enfeites(i, base), lata(i, base), lugares(i, base)]);
          /* o toque digital (D3): as particulas e os fios dos postes; e a lata gigante no fundo (D4); os lugares (lugaresCena.ts) */
          const p = particulas(i);
          o.grupo.add(e.grupo, fios(i), l.grupo, g.grupo);
          doisTons(o.grupo);
          o.grupo.add(p.malha);
          return { ...o, noite: n => { e.noite(n); p.noite(n); }, quadro: l.quadro, lugares: g.caixas, lugaresRaiz: g.raizes, abrirLugar: g.abrir };
        },
      };
    }
    case "voxel": return { id: mapa, dobra: 0, paleta: PALETA_ILHA, montar: i => montarCena(i, terrenoVoxel(i)), objetos: async i => objetosVoxel(i) };
    case "floresta": return {
      id: mapa, dobra: 0, paleta: PALETA_FLORESTA, montar: i => montarCena(i, terreno(i, PALETA_FLORESTA)),
      objetos: async i => objetos(i, base, await carregadorFloresta(base), arquivosFloresta),
    };
    case "cassette": return {
      id: mapa, dobra: 0, paleta: PALETA_ILHA, montar: i => montarCena(i, terrenoCassette(i, base)),
      objetos: async i => objetos(i, base, await carregadorCassette(base), arquivosCassette, false),
    };
  }
}
