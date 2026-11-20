/* A vitrine dos objetos (poc/vitrine.html, poc/vitrine/vitrine.ts): a ferramenta das pranchas do retrabalho dos objetos
   (docs/objetos3d/REFERENCIAS.md). O que as capturas dependem dela: desenhar todo modelo das tres tabelas (os lugares, os enfeites e os itens)
   com o traco do Digital, e avisar quando acabou (data-pronto="1" no body, que o Playwright espera). A pagina usa o DOM e o WebGL, entao o
   teste le o codigo, nao roda a pagina; os arquivos de cada modelo existirem e os testes das tabelas que conferem. */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";

const DIR = join(__dirname, "..", "poc");
const ts = readFileSync(join(DIR, "vitrine", "vitrine.ts"), "utf8");
const html = readFileSync(join(DIR, "vitrine.html"), "utf8");

describe("a vitrine dos objetos", () => {
  test("percorre as tres tabelas de modelos (a lata gigante e um enfeite desde 2026-11-10)", () => {
    for (const t of ["LUGARES_MODELOS", "ENFEITES_MODELOS", "ITENS_MODELOS"]) expect(ts).toContain(t);
  });
  test("desenha com o traco do Digital (o contorno da D5)", () => {
    expect(ts).toContain("CONTORNO_DIGITAL");
  });
  test("avisa a captura quando acaba (data-pronto)", () => {
    expect(ts).toContain(`document.body.setAttribute("data-pronto", "1")`);
  });
  test("a pagina carrega o script da vitrine", () => {
    expect(html).toContain("vitrine/vitrine.ts");
  });
});
