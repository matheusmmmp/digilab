/* A camera de desenvolvimento (src/telas/pet/cameraDev.ts): a API da pagina leva a camera solta a um alvo pelo nome ou por um ponto, com a
   orbita pedida, na hora; um nome que nao existe falha alto com a lista dos alvos; `pet` volta a seguir o pet com a orbita de partida.
   Sem a pagina (vitest em node): a vista nao publica nada, entao o ponto vai como pedido (sem o limite da ilha). */
import { afterEach, describe, expect, test } from "vitest";
import { apiCameraDev, CAMERA_DEV } from "../src/telas/pet/cameraDev.ts";
import { LIVRE, zerarCamera } from "../src/telas/pet/cameraLivre.ts";
import { ORBITA, recentrar } from "../src/telas/pet/orbita.ts";

afterEach(() => { zerarCamera(); recentrar(); });

describe("a camera de desenvolvimento", () => {
  const api = apiCameraDev(() => ({ portao: [12, -3], carro: [-6.5, 4] }));

  test("desligada sem o ?cameradev=1", () => { expect(CAMERA_DEV).toBe(false); });

  test("ir: pelo nome e por um ponto, na hora, com a orbita", () => {
    expect(api.ir("portao", { zoom: 0.6, giro: 0.4, inclina: -0.1 })).toEqual([12, -3]);
    expect(LIVRE.solta).toBe(true); expect(LIVRE.foco).toEqual([12, -3]); expect(LIVRE.trans).toBeNull();
    expect([ORBITA.zoom, ORBITA.giro, ORBITA.inclina]).toEqual([0.6, 0.4, -0.1]);
    api.ir([1, 2]);
    expect(LIVRE.foco).toEqual([1, 2]);
    expect(ORBITA.zoom).toBe(0.6);
  });

  test("ir: um alvo que nao existe falha alto e diz os que existem", () => {
    expect(() => api.ir("cais")).toThrow(/alvo desconhecido "cais".*portao, carro/);
  });

  test("pet: volta a orbita de partida", () => {
    api.ir("carro", { zoom: 2, giro: 1 });
    api.pet();
    expect([ORBITA.zoom, ORBITA.giro, ORBITA.inclina]).toEqual([1, 0, 0]);
  });
});
