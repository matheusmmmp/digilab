/* MMO0: a entrada do pacote que vai para o Chrome (scripts/mmo0/empacotar.ts). Expoe a vida roteirizada em window.MMO0 */
import { viver } from "./vida.ts";

Object.assign(globalThis, { MMO0: { viver } });
