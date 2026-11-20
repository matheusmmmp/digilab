/* De onde o jogo pede os assets que ficam fora do repositório (o atlas, a decoração, os sons, a cena da evolução e os cenários da luta):
   por padrão, o caminho relativo de sempre (a página em /v1/web/dist/ pede ../../../Assets/, que o servidor local serve e o dev do Vite
   também). No build publicado (CN5, docs/infra/DEPLOY_CN5.md), VITE_DIGILAB_ASSETS dá o endereço do R2 (RC-6: https://assets.<domínio>/),
   terminado em "/". Os kits do habitat que não se redistribuem (o Tiny Fantasy Forest e o Cassette Beasts) não passam por aqui: são só do dev. */
const lerBase = (): string => {
  let base = "";
  try { base = String(import.meta.env?.VITE_DIGILAB_ASSETS ?? "").trim(); } catch { base = ""; }
  if (base === "") return "../../../Assets/";
  if (!/^https:\/\/[^/]+\/(.*\/)?$/.test(base)) throw new Error(`VITE_DIGILAB_ASSETS precisa ser https:// e terminar em "/": ${base}`);
  return base;
};

export const BASE_ASSETS = lerBase();
