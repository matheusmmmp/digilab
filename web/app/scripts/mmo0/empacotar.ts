/* MMO0: empacota scripts/mmo0/pagina.ts (o motor, o produto e a vida roteirizada) num so arquivo para o Chrome, pela API do Vite, sem
   mexer no build do jogo. Sai em scripts/mmo0/dist/ (fora do git) */
import { build } from "vite";
import { fileURLToPath } from "node:url";

const AQUI = fileURLToPath(new URL("./", import.meta.url));
export const PACOTE = AQUI + "dist/mmo0.js";

export async function empacotar(): Promise<string> {
  await build({
    configFile: false, logLevel: "warn", root: AQUI, define: { "process.env.NODE_ENV": JSON.stringify("production") },   // o React do src/cerebro.ts
    build: { outDir: AQUI + "dist", emptyOutDir: true, minify: false, write: true,
      lib: { entry: AQUI + "pagina.ts", formats: ["iife"], name: "MMO0Pacote", fileName: () => "mmo0.js" } },
  });
  return PACOTE;
}
