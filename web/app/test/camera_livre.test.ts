/* A camera solta da ilha (L1 de "Lugares da ilha", src/telas/pet/cameraLivre.ts): so vista. Confere o WASD no plano da vista, o limite
   da grade, a transicao de volta ao pet, a distancia do "seguir o pet", o resumo que so muda quando um campo muda, e que nada disso
   toca o motor. */
import { beforeEach, describe, expect, test } from "vitest";
import {
  LIVRE, SEGUIR_DIST, TRANSICAO_MS, VEL_CELULAS_S, VISTA, andar, despublicarVista, focoDoQuadro, irPara, publicarVista, resumoCamera, seguirPet,
  type Limites, type Par, type VistaPublicada,
} from "../src/telas/pet/cameraLivre.ts";

const LIM: Limites = { x0: -10, z0: -12, x1: 78, z1: 40 };
const NORTE: Par = [0, -1];
const MAPA = { imagem: {} as ImageData, x0: -10, z0: -12, larg: 88, prof: 52, area: { w: 64, h: 30 } };
function vista(foco: Par, pet: Par, extra: Partial<VistaPublicada> = {}): VistaPublicada {
  return {
    foco, pet, bola: null, frente: NORTE, meiaAbertura: 0.6, comidas: [], ninho: [4, 15], comedouro: [10.5, 15.5], saco: [7, 11], portao: [15.5, 17], barraca: [1.8, 16.5], arvores: [],
    petFora: false, lado: "direita", pxPorCelula: 40, senoElevacao: 0.5, limites: LIM,
    mapa: MAPA, ...extra,
  };
}

beforeEach(() => despublicarVista());

describe("a camera solta", () => {
  test("seguindo, o ponto olhado e o pet", () => {
    expect(focoDoQuadro([8, 16], 0, 16, NORTE, LIM, true)).toEqual([8, 16]);
    expect(LIVRE.solta).toBe(false);
  });

  test("andar no plano da vista: a frente e para onde a camera olha, o lado e a direita dela", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    andar(2, 0, NORTE, LIM);
    expect(LIVRE.solta).toBe(true);
    expect(LIVRE.foco).toEqual([8, 14]);          /* a frente, para o norte */
    andar(0, 3, NORTE, LIM);
    expect(LIVRE.foco).toEqual([11, 14]);         /* a direita de quem olha para o norte e o leste */
    andar(0, 1, [1, 0], LIM);
    expect(LIVRE.foco).toEqual([11, 15]);         /* olhando para o leste, a direita e o sul */
  });

  test("o ponto olhado nao sai da grade da ilha", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    andar(500, -500, NORTE, LIM);
    expect(LIVRE.foco).toEqual([LIM.x0, LIM.z0]);
  });

  test("seguir o pet: a transicao vai ate o pet desenhado (mesmo andando) e a camera volta a segui-lo", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    andar(0, 20, NORTE, LIM);
    publicarVista(vista([...LIVRE.foco] as Par, [8, 16]), true, true);
    seguirPet(1000);
    const meio = focoDoQuadro([9, 16], 1000 + TRANSICAO_MS / 2, 16, NORTE, LIM, true);
    expect(meio[0]).toBeGreaterThan(9); expect(meio[0]).toBeLessThan(28);
    expect(LIVRE.solta).toBe(true);
    expect(focoDoQuadro([9, 16], 1000 + TRANSICAO_MS, 16, NORTE, LIM, true)).toEqual([9, 16]);
    expect(LIVRE.solta).toBe(false);
  });

  test("ir a um ponto do minimapa: com transicao chega no fim dela; sem transicao, na hora", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    irPara(40, 10, 0);
    expect(focoDoQuadro([8, 16], TRANSICAO_MS, 16, NORTE, LIM, true)).toEqual([40, 10]);
    irPara(30, 5, 0, false);
    expect(LIVRE.foco).toEqual([30, 5]);
    irPara(999, 999, 0, false);
    expect(LIVRE.foco).toEqual([LIM.x1, LIM.z1]);
  });

  test("sem poder soltar (a camera Fixa ou o celular), ela volta ao pet na hora", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    andar(5, 5, NORTE, LIM);
    expect(focoDoQuadro([8, 16], 0, 16, NORTE, LIM, false)).toEqual([8, 16]);
    expect(LIVRE.solta).toBe(false);
  });

  test("o 'seguir o pet' aparece longe do pet (mais de SEGUIR_DIST celulas) ou com o pet fora da tela", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    andar(0, SEGUIR_DIST - 1, NORTE, LIM);
    publicarVista(vista([...LIVRE.foco] as Par, [8, 16]), true, true);
    expect(resumoCamera()).toMatchObject({ solta: true, longe: false });
    andar(0, 2, NORTE, LIM);
    publicarVista(vista([...LIVRE.foco] as Par, [8, 16]), true, true);
    expect(resumoCamera()).toMatchObject({ solta: true, longe: true });
    andar(0, -(SEGUIR_DIST + 1), NORTE, LIM);
    publicarVista(vista([...LIVRE.foco] as Par, [8, 16], { petFora: true, lado: "baixo" }), true, true);
    expect(resumoCamera()).toMatchObject({ longe: true, petFora: true, lado: "baixo" });
  });

  test("o resumo da HUD so troca de objeto quando um campo muda (a HUD nao renderiza a cada quadro)", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    const r = resumoCamera();
    publicarVista(vista([8, 16], [8.2, 16]), true, true);
    expect(resumoCamera()).toBe(r);
    expect(VISTA.atual?.pet).toEqual([8.2, 16]);
  });

  test("a velocidade do WASD e a do PROPOSTO", () => {
    expect(VEL_CELULAS_S).toBe(12);
  });
});

describe("o minimapa so redesenha quando algo muda", () => {
  test("a mesma vista publicada de novo nao sobe a versao; o pet que anda, sim", () => {
    publicarVista(vista([8, 16], [8, 16]), true, true);
    const v0 = VISTA.versao;
    publicarVista(vista([8, 16], [8, 16]), true, true);
    expect(VISTA.versao).toBe(v0);
    publicarVista(vista([8, 16], [8.5, 16]), true, true);
    expect(VISTA.versao).toBe(v0 + 1);
    publicarVista(vista([8, 16], [8.5, 16], { comidas: [{ x: 3, z: 4, cor: 0xe8533f }] }), true, true);
    expect(VISTA.versao).toBe(v0 + 2);
  });
});
