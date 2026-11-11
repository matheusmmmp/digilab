/* Estado da interface: UM motor, uma fonte. Nenhuma tela guarda copia do estado do pet (revisao da interface,
   item 1): as telas leem o motor pelo useJogo() e so mudam o motor por aqui, que avisa todo mundo e grava o
   save. Duas abas no mesmo navegador (o HTML antigo e o app, ou dois apps) nao se sobrescrevem: quando o save
   muda em outra aba, esta relê o save em vez de gravar por cima. */
import { passarParaIlhaComAgua } from "./ilhaAgua.ts";
import { useEffect, useState } from "react";
import { GrupoDoJogo, Motor, PetMorto, VERSOES_PET, ehCerebroTrocavel, ehDoGrupo } from "../motor/index.ts";
import { pedirAbertura } from "./abertura.ts";
import { ligarProduto } from "./produto.ts";
import { podeTrocarCerebro, type Cerebro } from "./cerebro.ts";
import { CHAVE_LAB } from "./lab.ts";
import { CHAVE, gravarSave, lerSave, petExemplo, textoSave, textoSaveGrupo, type Armazenamento } from "./save.ts";
import { CHAVE_TAMER, Tamer, conferirBits, conferirBitsDoNivel, conferirCampeao, conferirItensDasMedalhas, conferirMedalhas, conferirRecordes, gravarTamer, lerTamer, sincronizarPet, type MedalhaGanha } from "./tamer.ts";
import { versaoDoOvo } from "./lutaPoc.ts";
import { assinaturaIntocada } from "./nivel.ts";
import { emitirSom } from "./somEventos.ts";

export type Origem = "save" | "exemplo" | "novo";
export interface Jogo {
  /** o pet na tela: o de um pet so, ou, com os dois pets (v25, CO4c), o pet em foco do grupo */
  motor: Motor;
  /** os dois pets (v25; motor/grupo_jogo.ts), ou null com um pet so. O tempo e as acoes do dono vao ao grupo pelo pet em foco */
  grupo: GrupoDoJogo | null;
  /** o pet do grupo em foco na tela (quem recebe a acao do dono; CO-6); "A" sem grupo */
  foco: string;
  origem: Origem;
  /** save que existe e nao abriu: o app mostra o erro e nao grava por cima */
  erroSave: { erro: string; bruto: string } | null;
  /** muda a cada alteracao do motor (as telas rederivam tudo dele) */
  revisao: number;
  /** quadros restantes do ovo chocando (so apresentacao: o tempo nao anda enquanto choca) */
  nascendo: number;
  /** registro do Tamer que existe e nao abriu: o app mostra o erro, nao grava por cima e nao da medalha */
  erroTamer: string | null;
  /** o pet que acabou de voltar a ser o ativo evoluiu ao receber as medalhas: quantas evolucoes ele tinha antes (revelacao) */
  evolucoesAoTrocar: number | null;
  /** o laboratorio (LM5b, LM5-7): enquanto o pet de teste esta na tela, `motor` e ele e este e o pet de hoje, guardado como estava (nunca
      perde o lugar de ativo); null fora do laboratorio. Nada do pet de teste vai para o save do pet de hoje: ele grava em CHAVE-lab */
  emLab: Motor | null;
}

let jogo: Jogo | null = null;
const ouvintes = new Set<() => void>();
let armazenamento: Armazenamento | null = null;
let ultimoGravado = 0, pendente = false;
/** o Tamer (medalhas): um so, lido na abertura; so muda por aqui (tamer.ts) */
let tamer = new Tamer();
const INTERVALO_GRAVAR_MS = 2000;

export function iniciarJogo(armaz: Armazenamento): Jogo {
  armazenamento = armaz;
  let erroTamer: string | null = null;
  try { tamer = lerTamer(armaz); } catch (err) { tamer = new Tamer(); erroTamer = err instanceof Error ? err.message : String(err); }
  const l = lerSave(armaz), extra = { erroTamer, evolucoesAoTrocar: null, emLab: null, foco: "A" };
  /* o pet v21 salvo passa para a ilha com agua na abertura (IA4), e o registro com o evento e gravado na hora */
  const passou = l.tipo === "ok" && passarParaIlhaComAgua(l.motor);
  if (l.tipo === "ok") jogo = { motor: l.motor, grupo: l.grupo, origem: "save", erroSave: null, revisao: 0, nascendo: 0, ...extra,
                                foco: l.grupo ? focoDoMotor(l.grupo, l.motor) : "A" };
  else jogo = { motor: petExemplo(), grupo: null, origem: "exemplo", erroSave: l.tipo === "erro" ? { erro: l.erro, bruto: l.bruto } : null, revisao: 0, nascendo: 0, ...extra };
  /* o pet salvo pode estar atras do Tamer (medalha ganha com outro pet): recebe o "u" ja na abertura */
  if (l.tipo === "ok" && (medalhas(jogo).mudou || passou)) gravar();
  return jogo;
}
export const tamerAtual = (): Tamer => tamer;
/** depois de toda mudanca do pet: a vitoria nova contra um lider vira medalha do Tamer, com o item dela (gravados na hora), o primeiro
    titulo do pet na Liga dos Lideres vira o evento "campeao" do Tamer, a sequencia do pet numa instalacao da Fronteira que passa a do
    Tamer vira o evento "recorde", e o pet ativo passa a conhecer as medalhas que o Tamer tem (evento "u"; o motor re-verifica a evolucao)
    e, com o titulo, a Fronteira aberta (evento "f"). Nada disso com save ou registro do Tamer que nao abriu. */
function medalhas(j: Jogo): { novas: MedalhaGanha[]; mudou: boolean } {
  if (j.emLab) return { novas: [], mudou: false };       // o pet de teste nao recebe nem da medalha ao Tamer
  if (!armazenamento || j.erroSave || j.erroTamer) return { novas: [], mudou: false };
  const novas = conferirMedalhas(tamer, j.motor), itens = conferirItensDasMedalhas(tamer, j.motor), titulo = conferirCampeao(tamer, j.motor);
  const recordes = conferirRecordes(tamer, j.motor);
  /* os Bits (docs/PLANO_V3_MOEDA.md, MO1): os feitos novos do pet e a 1a medalha de cada lider. O pet de exemplo das boas-vindas, ainda nao
     do jogador, nao paga: nem com a origem "exemplo", nem intocado depois de um descarte (o criterio do nivel do Tamer, nivel.ts) */
  const bits = j.origem === "exemplo" || exemploIntocado(j.motor) ? [] : conferirBits(tamer, j.motor);
  if (novas.length || itens.length || titulo || recordes.length || bits.length) gravarTamer(armazenamento, tamer);
  return { novas, mudou: sincronizarPet(tamer, j.motor) };
}
const exemplos = new Map<number, { semente: number; assinatura: string }>();
/** o pet e o de exemplo das boas-vindas, ainda intocado (so o tempo passou): a mesma conta do nivel do Tamer (nivelTela.ts, ehPetDoJogador).
    O exemplo e o da versao do pet: quem abriu o jogo antes da v23 (ou da v22) e nunca tocou no pet tem o exemplo daquela versao, que
    passa para a ilha grande ao abrir e continua nao sendo do jogador (a assinatura intocada ignora o "mi") */
function exemploIntocado(m: Motor): boolean {
  if (!VERSOES_PET.includes(m.versao) || ehDoGrupo(m.versao)) return false;      // o pet do grupo (v25) nunca e o de exemplo
  let ex = exemplos.get(m.versao);
  if (!ex) { const e = petExemplo(m.versao); ex = { semente: e.semente, assinatura: assinaturaIntocada(e) }; exemplos.set(m.versao, ex); }
  return m.semente === ex.semente && assinaturaIntocada(m) === ex.assinatura;
}
/** a unica porta de mudanca do Tamer fora das medalhas (itens: a carta usada, a carta da revanche): aplica, grava e avisa. Com o
    registro do Tamer que nao abriu, falha (o app nao grava por cima dele) */
export function mudarTamer<T>(f: (t: Tamer) => T): T {
  const j = jogoAtual();
  if (!armazenamento || j.erroTamer) throw new Error("o registro do Tamer não abriu: " + (j.erroTamer ?? "sem armazenamento"));
  const r = f(tamer);
  gravarTamer(armazenamento, tamer);
  j.revisao++; avisar();
  return r;
}
/** os Bits dos niveis do Tamer (nivelTela.ts, quando o nivel confirmado sobe): paga os que faltam ate `nivel`, grava e avisa. Sem nada a
    pagar, ou com o registro do Tamer que nao abriu, nao faz nada (a vista chama a cada confirmacao) */
export function pagarNivel(nivel: number): void {
  const j = jogoAtual();
  if (!armazenamento || j.erroTamer || j.emLab) return;
  if (!conferirBitsDoNivel(tamer, nivel).length) return;
  gravarTamer(armazenamento, tamer);
  j.revisao++; avisar();
}
export function jogoAtual(): Jogo {
  if (!jogo) throw new Error("jogo nao iniciado");
  return jogo;
}
const avisar = (): void => { for (const o of ouvintes) o(); };

/** o id do pet do grupo (o save guarda o foco pelo id) */
function focoDoMotor(g: GrupoDoJogo, m: Motor): string {
  const i = g.ids.find(k => g.motor(k) === m);
  if (i === undefined) throw new Error("o pet na tela nao e do grupo");
  return i;
}
/** o texto do save de hoje: o do grupo (com o foco) ou o de um pet so */
const textoDoSave = (j: Jogo): string => (j.grupo ? textoSaveGrupo(j.grupo, j.foco) : textoSave(j.motor));

function gravar(): void {
  const j = jogoAtual();
  if (j.erroSave || !armazenamento) return;
  if (j.emLab) armazenamento.setItem(CHAVE_LAB, textoSave(j.motor));   // o pet de teste vai para o espaco dele, nunca para o save de hoje
  else if (j.grupo) armazenamento.setItem(CHAVE, textoDoSave(j));      // os dois pets: o registro do grupo
  else gravarSave(armazenamento, j.motor);
  ultimoGravado = performance.now(); pendente = false;
}
/** grava o que ficou pendente (fechar ou esconder a aba) */
export function gravarPendente(): void { if (pendente) gravar(); }

/** a unica porta de mudanca: aplica no motor, avisa as telas e grava. Acao do dono grava na hora; o tempo
    passando grava no maximo a cada 2 s (como o HTML), e o resto sai ao esconder ou fechar a aba. */
export function mudarMotor(f: (m: Motor) => void, quando: "agora" | "adiado" = "agora"): void {
  const j = jogoAtual();
  /* os dois pets (CO4c): a mudanca vai ao grupo pelo pet em foco, e o que ele grava entra no registro do grupo; o avancar dele anda os dois.
     Com o pet de teste na tela, o grupo fica parado, como o pet de hoje */
  try { if (j.grupo && !j.emLab) j.grupo.agir(j.foco, f); else f(j.motor); } catch (err) {
    /* pet v4 morto: a acao nao entra no registro; a tela passa a mostrar a morte e quem chamou recebe o erro */
    if (err instanceof PetMorto) avisar();
    throw err;
  }
  if (medalhas(j).novas.length) emitirSom("medalha");   /* SOM-UP: a medalha nova do Tamer */
  j.revisao++;
  if (j.origem === "exemplo" && !j.erroSave) j.origem = "save";
  pendente = true;
  if (quando === "agora" || performance.now() - ultimoGravado > INTERVALO_GRAVAR_MS) gravar();
  avisar();
}
/** troca o pet inteiro (ovo novo, pet anterior, save mudado em outra aba) */
export function trocarMotor(m: Motor, origem: Origem, nascendo = 0): void {
  sairDoLab();            // trocar o pet e sempre sobre o pet de hoje: o pet de teste sai da tela, com o save dele intacto
  const j = jogoAtual();
  passarParaIlhaComAgua(m);        // o pet v21 guardado ou importado chega a ilha com agua ao abrir (IA4); o gravar abaixo o salva
  j.motor = m; j.grupo = null; j.foco = "A"; j.origem = origem; j.erroSave = null; j.nascendo = nascendo; j.revisao++;
  /* pet guardado que estava pronto: recebe as medalhas agora e evolui (a revelacao conta a partir de antes) */
  const antes = m.evolucoes.length;
  medalhas(j);
  j.evolucoesAoTrocar = m.evolucoes.length > antes ? antes : null;
  gravar();
  avisar();
}
/** os dois ovos chocando (CO4c): o grupo inteiro passa a ser o de hoje, com o primeiro pet em foco */
export function trocarGrupo(g: GrupoDoJogo, origem: Origem, nascendo = 0): void {
  sairDoLab();
  const j = jogoAtual();
  j.grupo = g; j.foco = g.ids[0]; j.motor = g.motor(j.foco);
  j.origem = origem; j.erroSave = null; j.nascendo = nascendo; j.revisao++;
  medalhas(j);
  j.evolucoesAoTrocar = null;
  gravar();
  avisar();
}
/** muda o pet em foco do grupo (quem a tela mostra e quem recebe a acao do dono; CO-6). Sem grupo, falha */
export function focar(ident: string): void {
  const j = jogoAtual();
  if (!j.grupo) throw new Error("so os dois pets tem foco");
  if (j.emLab) throw new Error("volte ao seu pet antes de trocar o foco");
  j.motor = j.grupo.motor(ident); j.foco = ident; j.revisao++;
  pendente = true;
  avisar();
}
/** o pet de hoje: o ativo, mesmo com o pet de teste na tela */
export function motorReal(): Motor { const j = jogoAtual(); return j.emLab ?? j.motor; }
/** LM5-7: mostra o pet de teste na tela Pet sem trocar o pet ativo (o de hoje fica guardado em `emLab`, com o tempo parado como o de um guardado) */
export function abrirLab(m: Motor): void {
  const j = jogoAtual();
  j.emLab ??= j.motor;
  j.motor = m; j.origem = "save"; j.nascendo = 0; j.revisao++;
  avisar();
}
/** volta ao pet de hoje; o pet de teste ja esta gravado em CHAVE-lab. Sem pet de teste na tela, nao faz nada */
export function sairDoLab(): void {
  const j = jogoAtual();
  if (!j.emLab) return;
  if (armazenamento && !j.erroSave && pendente) armazenamento.setItem(CHAVE_LAB, textoSave(j.motor));
  pendente = false;
  j.motor = j.emLab; j.emLab = null; j.revisao++;
  avisar();
}
/** troca o cerebro do pet ativo (Ajustes > Laboratorio): um "cb" no registro dele, gravado na hora. O pet v15 passa a v17 antes (o mesmo
    registro refeito, conferido pela assinatura). Com o pet de teste na tela ou um save que nao abriu, falha */
export function trocarCerebroDoPet(c: Cerebro): void {
  const j = jogoAtual();
  if (j.emLab) throw new Error("volte ao seu pet para trocar o cérebro dele");
  if (j.erroSave) throw new Error("o save não abriu: o cérebro não troca");
  if (!podeTrocarCerebro(j.motor)) throw new Error(`este pet é da versão ${j.motor.versao} e não troca de cérebro`);
  if (j.motor.cerebroAtual === c) throw new Error(`o pet já decide com o cérebro ${c}`);
  mudarMotor(m => m.trocarCerebro(c));
}
/** quadros do palco (120 ms cada) com o ovo chocando: ~5 s, para o nascimento ser um momento e nao um corte. PROPOSTO, SEM FONTE */
export const QUADROS_CHOCANDO = 40;
/** um ovo novo: semente do relogio (como o HTML) e o ovo chocando */
export function novoPet(): void {
  const s = (Date.now() ^ Math.floor(Math.random() * 1e9)) >>> 0;
  trocarMotor(ligarProduto(new Motor(s, versaoDoOvo())), "novo", QUADROS_CHOCANDO);
}
/** o balanco do ovo de lado, em unidades (texel ou px), pelos quadros que faltam: parado no comeco, tremidas curtas no meio, e cada
    vez mais forte no fim (o ovo nao "anda": so treme no lugar). PROPOSTO, SEM FONTE */
export function balancoOvo(nascendo: number): number {
  const feito = QUADROS_CHOCANDO - nascendo, lado = nascendo % 2 ? 1 : -1;
  if (nascendo <= 0 || feito < 10) return 0;
  if (nascendo > 12) return feito % 8 < 3 ? lado : 0;
  return lado * (nascendo <= 4 ? 2 : 1);
}
/** um quadro a menos do ovo chocando (chamado pelo palco a cada desenho) */
export function passarQuadroOvo(): void {
  const j = jogoAtual();
  /* o ovo chocou: a camera do primeiro dia fica pedida (abertura.ts; AB-2, uma vez por pet) */
  if (j.nascendo > 0) { j.nascendo--; if (j.nascendo === 0) { pedirAbertura(j.motor.semente); avisar(); } }
}

/** outra aba mudou o save: relê em vez de gravar por cima depois */
export function ouvirOutrasAbas(): () => void {
  const aoMudar = (ev: StorageEvent) => {
    if (ev.key === CHAVE_TAMER && armazenamento && jogo) {
      /* outra aba ganhou medalha: relê o Tamer; o pet desta aba recebe o "u" na proxima mudanca */
      try { tamer = lerTamer(armazenamento); jogo.erroTamer = null; } catch (err) { jogo.erroTamer = "outra aba gravou um registro do Tamer que não abre: " + (err instanceof Error ? err.message : String(err)); }
      jogo.revisao++; avisar(); return;
    }
    if (ev.key !== CHAVE || !armazenamento || !jogo) return;
    if (ev.newValue === null || (!jogo.emLab && ev.newValue === textoDoSave(jogo)) || (jogo.emLab && !jogo.grupo && ev.newValue === textoSave(motorReal()))) return;
    const l = lerSave(armazenamento);
    /* a outra aba pode ser de antes da IG4: o pet chega a ilha grande aqui tambem, e o registro com o evento fica para gravar */
    const passou = l.tipo === "ok" && passarParaIlhaComAgua(l.motor);
    if (jogo.emLab) { if (l.tipo === "ok") { jogo.emLab = l.motor; jogo.grupo = l.grupo; if (l.grupo) jogo.foco = focoDoMotor(l.grupo, l.motor); } return; }    // o pet de hoje, guardado: relê ele, o de teste segue na tela
    if (l.tipo === "ok") {
      jogo.motor = l.motor; jogo.grupo = l.grupo; jogo.foco = l.grupo ? focoDoMotor(l.grupo, l.motor) : "A";
      jogo.origem = "save"; jogo.erroSave = null; jogo.revisao++; pendente = passou; avisar();
    }
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
