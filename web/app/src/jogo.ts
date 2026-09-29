/* Estado da interface: UM motor, uma fonte. Nenhuma tela guarda copia do estado do pet (revisao da interface,
   item 1): as telas leem o motor pelo useJogo() e so mudam o motor por aqui, que avisa todo mundo e grava o
   save. Duas abas no mesmo navegador (o HTML antigo e o app, ou dois apps) nao se sobrescrevem: quando o save
   muda em outra aba, esta relê o save em vez de gravar por cima. */
import { useEffect, useState } from "preact/hooks";
import { Motor, PetMorto } from "../motor/index.ts";
import { CHAVE, gravarSave, lerSave, petExemplo, textoSave, type Armazenamento } from "./save.ts";

export type Origem = "save" | "exemplo" | "novo";
export interface Jogo {
  motor: Motor;
  origem: Origem;
  /** save que existe e nao abriu: o app mostra o erro e nao grava por cima */
  erroSave: { erro: string; bruto: string } | null;
  /** muda a cada alteracao do motor (as telas rederivam tudo dele) */
  revisao: number;
  /** quadros restantes do ovo chocando (so apresentacao: o tempo nao anda enquanto choca) */
  nascendo: number;
}

let jogo: Jogo | null = null;
const ouvintes = new Set<() => void>();
let armazenamento: Armazenamento | null = null;
let ultimoGravado = 0, pendente = false;
const INTERVALO_GRAVAR_MS = 2000;

export function iniciarJogo(armaz: Armazenamento): Jogo {
  armazenamento = armaz;
  const l = lerSave(armaz);
  if (l.tipo === "ok") jogo = { motor: l.motor, origem: "save", erroSave: null, revisao: 0, nascendo: 0 };
  else jogo = { motor: petExemplo(), origem: "exemplo", erroSave: l.tipo === "erro" ? { erro: l.erro, bruto: l.bruto } : null, revisao: 0, nascendo: 0 };
  return jogo;
}
export function jogoAtual(): Jogo {
  if (!jogo) throw new Error("jogo nao iniciado");
  return jogo;
}
const avisar = (): void => { for (const o of ouvintes) o(); };

function gravar(): void {
  const j = jogoAtual();
  if (j.erroSave || !armazenamento) return;
  gravarSave(armazenamento, j.motor);
  ultimoGravado = performance.now(); pendente = false;
}
/** grava o que ficou pendente (fechar ou esconder a aba) */
export function gravarPendente(): void { if (pendente) gravar(); }

/** a unica porta de mudanca: aplica no motor, avisa as telas e grava. Acao do dono grava na hora; o tempo
    passando grava no maximo a cada 2 s (como o HTML), e o resto sai ao esconder ou fechar a aba. */
export function mudarMotor(f: (m: Motor) => void, quando: "agora" | "adiado" = "agora"): void {
  const j = jogoAtual();
  try { f(j.motor); } catch (err) {
    /* pet v4 morto: a acao nao entra no registro; a tela passa a mostrar a morte e quem chamou recebe o erro */
    if (err instanceof PetMorto) avisar();
    throw err;
  }
  j.revisao++;
  if (j.origem === "exemplo" && !j.erroSave) j.origem = "save";
  pendente = true;
  if (quando === "agora" || performance.now() - ultimoGravado > INTERVALO_GRAVAR_MS) gravar();
  avisar();
}
/** troca o pet inteiro (ovo novo, pet anterior, save mudado em outra aba) */
export function trocarMotor(m: Motor, origem: Origem, nascendo = 0): void {
  const j = jogoAtual();
  j.motor = m; j.origem = origem; j.erroSave = null; j.nascendo = nascendo; j.revisao++;
  gravar();
  avisar();
}
/** um ovo novo: semente do relogio (como o HTML) e 16 quadros chocando */
export function novoPet(): void {
  const s = (Date.now() ^ Math.floor(Math.random() * 1e9)) >>> 0;
  trocarMotor(new Motor(s), "novo", 16);
}
/** um quadro a menos do ovo chocando (chamado pelo palco a cada desenho) */
export function passarQuadroOvo(): void {
  const j = jogoAtual();
  if (j.nascendo > 0) { j.nascendo--; if (j.nascendo === 0) avisar(); }
}

/** outra aba mudou o save: relê em vez de gravar por cima depois */
export function ouvirOutrasAbas(): () => void {
  const aoMudar = (ev: StorageEvent) => {
    if (ev.key !== CHAVE || !armazenamento || !jogo) return;
    if (ev.newValue === null || ev.newValue === textoSave(jogo.motor)) return;
    const l = lerSave(armazenamento);
    if (l.tipo === "ok") { jogo.motor = l.motor; jogo.origem = "save"; jogo.erroSave = null; jogo.revisao++; pendente = false; avisar(); }
    else if (l.tipo === "erro") { jogo.erroSave = { erro: "outra aba gravou um save que não abre: " + l.erro, bruto: l.bruto }; avisar(); }
  };
  addEventListener("storage", aoMudar);
  return () => removeEventListener("storage", aoMudar);
}

/** hook: a tela redesenha quando o motor muda */
export function useJogo(): Jogo {
  const [, setRev] = useState(0);
  useEffect(() => {
    const o = () => setRev(r => r + 1);
    ouvintes.add(o);
    return () => { ouvintes.delete(o); };
  }, []);
  return jogoAtual();
}
