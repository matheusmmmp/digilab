/* O mapa do habitat (os pets v12, a ilha 3D): qual estilo desenha a mesma grade do motor e de onde a camera olha. E so vista, como a
   pele (pele.ts): o motor, a vida, o log e o replay nao mudam; o pet anda onde o motor diz em qualquer mapa (caminho A de 2026-10-31:
   cada mapa e uma vista da grade do motor). A escolha fica numa chave propria ao lado da do save; ?mapa= e ?camera= no endereco
   sobrepoem sem gravar (conferencia e capturas). Trocar com o jogo rodando religa a cena 3D (CenaPet escuta useHabitat).
   - Ilha: o estilo Animal Crossing da L4 (H0-H5), com o mundo curvo; o padrao.
   - Voxel: a mesma ilha em cubos, gerada por codigo (sem asset); vai no build.
   - Floresta e Cassette: os kits que nao se redistribuem (Tiny Fantasy Forest e o Cassette Beasts do Matheus, em Assets/kits3d/), so no
     modo dev (o vite.config os serve); fora dele nao aparecem, e se faltar arquivo a cena volta para a ilha sem gravar (voltarParaIlha).
   - Camera: atras (a da ilha, H-3) ou lateral (a do POC do campo lateral, #480: de lado e quase ortografica). */
import { useEffect, useState } from "react";
import { CHAVE } from "./save.ts";

export type Mapa = "ilha" | "voxel" | "floresta" | "cassette";
export type Camera = "atras" | "lateral";
export const CHAVE_HABITAT = CHAVE + "-habitat";
export const MAPA_PADRAO: Mapa = "ilha", CAMERA_PADRAO: Camera = "atras";
export const NOME_MAPA: Record<Mapa, string> = { ilha: "Ilha", voxel: "Voxel", floresta: "Floresta", cassette: "Cassette" };
export const NOME_CAMERA: Record<Camera, string> = { atras: "Atrás", lateral: "Lateral" };
/** os mapas com assets fora do repositorio: so no modo dev */
export const MAPAS_DEV: readonly Mapa[] = ["floresta", "cassette"];
const MAPAS: readonly Mapa[] = ["ilha", "voxel", "floresta", "cassette"];
/** modo dev do Vite (import.meta.env nao existe no vitest em node puro sem o Vite: conta como build) */
const DEV = (() => { try { return !!import.meta.env?.DEV; } catch { return false; } })();
/** os mapas que esta pagina oferece, na ordem da tela */
export function mapasDisponiveis(dev = DEV): Mapa[] { return MAPAS.filter(m => dev || !MAPAS_DEV.includes(m)); }
const ehMapa = (v: unknown, dev = DEV): v is Mapa => typeof v === "string" && mapasDisponiveis(dev).includes(v as Mapa);
const ehCamera = (v: unknown): v is Camera => v === "atras" || v === "lateral";

export interface Habitat { mapa: Mapa; camera: Camera }
let atual: Habitat = { mapa: MAPA_PADRAO, camera: CAMERA_PADRAO };
/** o mapa que falhou ao carregar nesta pagina: a cena volta para a ilha sem mexer na escolha gravada */
let caido: Mapa | null = null;
const ouvintes = new Set<() => void>();
const avisar = () => { for (const o of ouvintes) o(); };

export function iniciarHabitat(dev = DEV): void {
  const q = new URLSearchParams(location.search);
  let salvo: Partial<Habitat> = {};
  try { salvo = JSON.parse(localStorage.getItem(CHAVE_HABITAT) ?? "{}") ?? {}; } catch { /* sem armazenamento ou lixo: o padrao */ }
  const mq = q.get("mapa"), cq = q.get("camera");
  atual = {
    mapa: ehMapa(mq, dev) ? mq : ehMapa(salvo.mapa, dev) ? salvo.mapa : MAPA_PADRAO,
    camera: ehCamera(cq) ? cq : ehCamera(salvo.camera) ? salvo.camera : CAMERA_PADRAO,
  };
  caido = null;
}
function gravar(): void {
  try { localStorage.setItem(CHAVE_HABITAT, JSON.stringify(atual)); } catch { /* preferencia de tela */ }
  avisar();
}
/** o mapa escolhido em Ajustes > Aparencia (vale na hora e fica gravado) */
export function escolherMapa(m: Mapa): void { atual = { ...atual, mapa: m }; caido = null; gravar(); }
export function escolherCamera(c: Camera): void { atual = { ...atual, camera: c }; gravar(); }
/** a escolha gravada (o que a tela de Ajustes mostra) */
export function habitatEscolhido(): Habitat { return atual; }
/** o que a cena desenha: a escolha, ou a ilha se o mapa escolhido caiu nesta pagina */
export function habitatAtual(): Habitat { return caido === atual.mapa ? { ...atual, mapa: "ilha" } : atual; }
/** um mapa que nao carregou (assets faltando): a cena religa na ilha; a escolha gravada fica, e escolher de novo tenta outra vez */
export function voltarParaIlha(m: Mapa): void {
  if (m === "ilha" || caido === m) return;
  caido = m;
  avisar();
}
export function mapaCaido(): Mapa | null { return caido; }
export function useHabitat(): Habitat {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return habitatAtual();
}
