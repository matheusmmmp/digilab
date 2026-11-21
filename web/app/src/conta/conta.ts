/* O cliente da conta (CN2 no jogo; docs/PLANO_UX_CONTA.md, UX-CN-1 a 6 APROVADAS em 2026-11-12): entrar, o primeiro acesso, o perfil,
   sair e apagar, contra as rotas do servidor_web (servidor_web/src/conta/rotas.ts). Sem React e sem DOM: a tela (telas/config/TelaConta.tsx)
   le o estado por `ouvirConta`/`revisaoConta` e chama as funcoes daqui; os testes ligam um `fetch` falso (test/conta.test.ts).

   A chave: sem `ligarConta` (a tela so liga com VITE_DIGILAB_API no build), nada daqui roda e os Ajustes sao os de sempre.

   A conta nao toca o motor, o registro nem o save (isso e a CN3). Aqui nao se guarda nada no navegador: a sessao e o cookie do servidor,
   e o apelido se le dele a cada abertura. O e-mail e o nome nunca chegam ao jogo. */

/** a espera de cada chamada, em milissegundos (PROPOSTA, SEM FONTE; a mesma do pedido da luta ranqueada) */
export const ESPERA_CONTA_MS = 15_000;
/** para onde o servidor devolve o jogador depois do provedor: a parte Conta dos Ajustes */
export const VOLTA_DA_CONTA = "#/config/conta";

export interface AmbienteConta {
  /** o endereco do servidor, sem a barra do fim */
  api: string;
  buscar: (url: string, init?: RequestInit) => Promise<Response>;
  /** sai do jogo para um endereco (a ida ao provedor, na mesma aba) */
  ir: (url: string) => void;
}

export interface Provedor { nome: string; ligado: boolean }
export interface Aparelho { id: string; nome: string; vistoEm: number; atual: boolean }
export interface Conta {
  apelido: string; criadaEm: number; provedores: string[];
  /** o aceite mais novo dos termos; null se o servidor nao devolveu nenhum */
  aceitoEm: number | null;
  aparelhos: Aparelho[];
}
export interface Primeiro {
  apelido: string; digimons: string[]; versaoTermos: string; versaoPrivacidade: string; provedor: string;
  /** a chave do site do Turnstile (CN4), se o servidor pede o desafio na criação da conta; null, sem desafio */
  turnstile: string | null;
}

/** o passo da conta que a tela mostra */
export type Passo =
  | { tipo: "conferindo" }
  | { tipo: "sem_conta" }
  | { tipo: "saindo"; provedor: string }
  | { tipo: "nao_deu" }
  | { tipo: "fora_da_lista" }
  | { tipo: "menos_de_18" }
  | { tipo: "primeiro"; dados: Primeiro }
  | { tipo: "conta"; conta: Conta }
  | { tipo: "apagada" };

export interface EstadoConta {
  /** null: ainda nao se perguntou ao servidor */
  passo: Passo | null;
  provedores: Provedor[];
  /** uma chamada que muda algo esta a caminho (os botoes ficam apagados) */
  ocupado: boolean;
  /** o que nao deu na ultima acao, em uma frase para a tela; null sem erro */
  erro: string | null;
}

export const CT: EstadoConta = { passo: null, provedores: [], ocupado: false, erro: null };
let amb: AmbienteConta | null = null, csrf: string | null = null, revisao = 0, pedido = 0, tentativasTurnstile = 0;
const ouvintes = new Set<() => void>();
const avisar = (): void => { revisao++; for (const f of ouvintes) f(); };

export function ligarConta(a: AmbienteConta): void {
  amb = { ...a, api: a.api.replace(/\/+$/, "") };
  CT.passo = null; CT.provedores = []; CT.ocupado = false; CT.erro = null; csrf = null;
  avisar();
}
export function desligarConta(): void { amb = null; CT.passo = null; CT.provedores = []; CT.ocupado = false; CT.erro = null; csrf = null; avisar(); }
export const contaLigada = (): boolean => amb !== null;
export const ouvirConta = (f: () => void): (() => void) => { ouvintes.add(f); return () => { ouvintes.delete(f); }; };
export const revisaoConta = (): number => revisao;
/** sobe quando o Turnstile não passou: a tela desenha o widget de novo (o token já foi gasto) */
export const tentativaTurnstile = (): number => tentativasTurnstile;
/** o apelido da conta aberta, para a linha dos Ajustes; null sem conta ou antes de perguntar */
export const apelidoDaConta = (): string | null => CT.passo?.tipo === "conta" ? CT.passo.conta.apelido : null;
/** o endereco do arquivo "Baixar meus dados" (a sessao vai no cookie) */
export const enderecoDosDados = (): string => `${exigir().api}/conta/dados`;

class SemResposta extends Error {}
function exigir(): AmbienteConta { if (!amb) throw new Error("a conta está desligada"); return amb; }

async function chamar(metodo: string, caminho: string, corpo?: unknown): Promise<{ status: number; corpo: unknown }> {
  const a = exigir(), controle = new AbortController(), relogio = setTimeout(() => controle.abort(), ESPERA_CONTA_MS);
  const headers: Record<string, string> = {};
  if (metodo !== "GET" && csrf !== null) headers["X-CSRF-Token"] = csrf;
  if (corpo !== undefined) headers["Content-Type"] = "application/json";
  try {
    const r = await a.buscar(a.api + caminho, { method: metodo, headers, credentials: "include", signal: controle.signal, body: corpo === undefined ? undefined : JSON.stringify(corpo) });
    const texto = await r.text();
    let dados: unknown = null;
    if (texto) { try { dados = JSON.parse(texto); } catch { throw new Error(`o servidor respondeu ${r.status} sem JSON em ${caminho}`); } }
    return { status: r.status, corpo: dados };
  } catch (err) {
    /* a rede caiu, o servidor esta fora ou a espera acabou: nada de erro alto, a tela diz "nao deu" */
    if (err instanceof TypeError || (err instanceof Error && err.name === "AbortError")) throw new SemResposta();
    throw err;
  } finally { clearTimeout(relogio); }
}
const objeto = (v: unknown): Record<string, unknown> => {
  if (typeof v !== "object" || v === null || Array.isArray(v)) throw new Error(`o servidor respondeu algo que o jogo não entende: ${JSON.stringify(v)}`);
  return v as Record<string, unknown>;
};
const texto = (v: unknown, campo: string): string => { if (typeof v !== "string" || !v) throw new Error(`a resposta do servidor veio sem "${campo}"`); return v; };
const hora = (v: unknown, campo: string): number => { const t = Date.parse(texto(v, campo)); if (!Number.isFinite(t)) throw new Error(`"${campo}" não é uma data: ${String(v)}`); return t; };

async function lerProvedores(): Promise<void> {
  const { status, corpo } = await chamar("GET", "/auth/provedores");
  if (status !== 200 || !Array.isArray(corpo)) throw new Error(`a lista dos provedores não veio (${status})`);
  CT.provedores = corpo.map(p => { const o = objeto(p); return { nome: texto(o.nome, "nome"), ligado: o.ligado === true }; });
}
async function lerConta(): Promise<Conta | null> {
  const r = await chamar("GET", "/conta");
  if (r.status === 401) { csrf = null; return null; }
  if (r.status !== 200) throw new Error(`a conta não veio (${r.status})`);
  const d = objeto(r.corpo), c = objeto(d.conta);
  csrf = texto(d.csrf, "csrf");
  const aceites = Array.isArray(d.consentimentos) ? d.consentimentos.map(x => hora(objeto(x).aceito_em, "aceito_em")) : [];
  const ap = await chamar("GET", "/conta/aparelhos");
  if (ap.status !== 200 || !Array.isArray(ap.corpo)) throw new Error(`os aparelhos não vieram (${ap.status})`);
  return {
    apelido: texto(c.apelido, "apelido"), criadaEm: hora(c.criada_em, "criada_em"),
    provedores: Array.isArray(d.provedores) ? d.provedores.map(p => texto(p, "provedor")) : [],
    aceitoEm: aceites.length ? Math.max(...aceites) : null,
    aparelhos: ap.corpo.map(x => { const o = objeto(x); return { id: texto(o.id, "id"), nome: texto(o.nome, "nome"), vistoEm: hora(o.visto_em, "visto_em"), atual: o.atual === true }; }),
  };
}
async function lerPrimeiro(): Promise<Primeiro | null> {
  const r = await chamar("GET", "/conta/primeiro-acesso");
  if (r.status === 401) return null;
  if (r.status !== 200) throw new Error(`o primeiro acesso não veio (${r.status})`);
  const d = objeto(r.corpo);
  csrf = texto(d.csrf, "csrf");
  if (!Array.isArray(d.digimons) || !d.digimons.length) throw new Error("o primeiro acesso veio sem a lista do apelido");
  return { apelido: texto(d.apelido, "apelido"), digimons: d.digimons.map(x => texto(x, "digimon")), versaoTermos: texto(d.versao_termos, "versao_termos"),
    versaoPrivacidade: texto(d.versao_privacidade, "versao_privacidade"), provedor: texto(d.provedor, "provedor"),
    turnstile: d.turnstile === undefined || d.turnstile === null ? null : texto(d.turnstile, "turnstile") };
}

/** o que o servidor pos em `?conta=` na volta do provedor */
export type Volta = "entrou" | "primeiro_acesso" | "fora_da_lista" | "nao_deu";
const VOLTAS: readonly string[] = ["entrou", "primeiro_acesso", "fora_da_lista", "nao_deu"];
/** le o `?conta=` de uma busca do endereco ("?conta=entrou"); null se nao ha ou nao e um estado conhecido */
export function voltaDaBusca(busca: string): Volta | null {
  const v = new URLSearchParams(busca).get("conta");
  return v !== null && VOLTAS.includes(v) ? v as Volta : null;
}

/** pergunta ao servidor em que pe a conta esta e poe o passo certo. `volta`: o estado que o servidor devolveu depois do provedor.
    A rede fora vira "nao_deu"; uma chamada mais nova ganha da mais velha */
export async function abrirConta(volta: Volta | null = null): Promise<void> {
  exigir();
  const meu = ++pedido, por = (p: Passo): void => { if (meu === pedido) { CT.passo = p; avisar(); } };
  CT.erro = null; CT.passo = { tipo: "conferindo" }; avisar();
  try {
    if (volta === "nao_deu" || volta === "fora_da_lista") { await lerProvedores(); return por({ tipo: volta }); }
    const conta = await lerConta();
    if (conta) return por({ tipo: "conta", conta });
    const primeiro = await lerPrimeiro();
    if (primeiro) return por({ tipo: "primeiro", dados: primeiro });
    await lerProvedores();
    /* o servidor disse que entrou e a sessao nao veio (o cookie foi barrado): nao deu */
    por(volta === "entrou" || volta === "primeiro_acesso" ? { tipo: "nao_deu" } : { tipo: "sem_conta" });
  } catch (err) {
    if (err instanceof SemResposta) return por({ tipo: "nao_deu" });
    if (meu === pedido) { CT.passo = { tipo: "nao_deu" }; avisar(); }
    throw err;
  }
}
/** a linha dos Ajustes: pergunta uma vez, calada (sem resposta, a linha diz "sem conta") */
export async function conferirConta(): Promise<void> {
  if (!amb || CT.passo !== null) return;
  try { await abrirConta(); } catch (err) { if (!(err instanceof SemResposta)) throw err; }
  if (CT.passo !== null && (CT.passo as Passo).tipo === "nao_deu") { CT.passo = null; avisar(); }
}

/** volta a tela Entrar (Tentar de novo, Usar outra conta, Cancelar a ida) */
export function voltarAEntrar(): void {
  /* sem a lista dos provedores (a pagina voltou do provedor direto para outro passo), pergunta ao servidor de novo */
  if (CT.provedores.length === 0) { void abrirConta().catch((err: unknown) => { console.error(err); }); return; }
  pedido++; CT.passo = { tipo: "sem_conta" }; CT.erro = null; CT.ocupado = false; avisar();
}

/** sai para o provedor, na mesma aba; o jogo ja gravou o pet (o save e por evento) */
export function entrarCom(provedor: string): void {
  const a = exigir();
  if (!CT.provedores.some(p => p.nome === provedor && p.ligado)) throw new Error(`o provedor ${provedor} não está ligado`);
  CT.passo = { tipo: "saindo", provedor }; CT.erro = null; avisar();
  a.ir(`${a.api}/auth/${encodeURIComponent(provedor)}?volta=${encodeURIComponent(VOLTA_DA_CONTA)}`);
}

/** uma acao que muda algo: marca `ocupado`, e a rede fora vira uma frase em `erro` */
async function mudar<T>(f: () => Promise<T>): Promise<T | undefined> {
  if (CT.ocupado) throw new Error("já há uma ação da conta a caminho");
  CT.ocupado = true; CT.erro = null; avisar();
  try { return await f(); }
  catch (err) {
    if (err instanceof SemResposta) { CT.erro = "Sem resposta do servidor. Nada mudou."; return undefined; }
    throw err;
  } finally { CT.ocupado = false; avisar(); }
}
const sessaoAcabou = (): void => { csrf = null; CT.passo = { tipo: "sem_conta" }; CT.erro = "A sessão acabou. Entre de novo."; };
const recusa = (status: number, corpo: unknown): Error =>
  new Error(`o servidor recusou (${status}): ${typeof corpo === "object" && corpo !== null && typeof (corpo as { erro?: unknown }).erro === "string" ? (corpo as { erro: string }).erro : JSON.stringify(corpo)}`);

/** troca o Digimon do apelido no primeiro acesso; o numero e sorteado pelo servidor */
export async function trocarApelido(digimon: string): Promise<void> {
  const p = CT.passo;
  if (p?.tipo !== "primeiro") throw new Error("trocar o apelido só no primeiro acesso");
  if (!p.dados.digimons.includes(digimon)) throw new Error(`Digimon fora da lista: ${digimon}`);
  await mudar(async () => {
    const r = await chamar("POST", "/conta/primeiro-acesso/apelido", { digimon });
    if (r.status === 401) return sessaoAcabou();
    if (r.status !== 200) throw recusa(r.status, r.corpo);
    CT.passo = { tipo: "primeiro", dados: { ...p.dados, apelido: texto(objeto(r.corpo).apelido, "apelido") } };
  });
}
/** cria a conta com a idade e o aceite da versao que a tela mostrou. "menos_de_18": o servidor nao guarda nada */
/** `turnstile`: o token do widget, quando o servidor pede o desafio (Primeiro.turnstile); sem desafio, nada vai no pedido */
export async function criarConta(idade: "18_ou_mais" | "menos_de_18", turnstile: string | null = null): Promise<void> {
  const p = CT.passo;
  if (p?.tipo !== "primeiro") throw new Error("criar a conta só no primeiro acesso");
  if (p.dados.turnstile !== null && !turnstile) throw new Error("criar a conta pede o token do Turnstile");
  await mudar(async () => {
    const r = await chamar("POST", "/conta/primeiro-acesso", { idade, aceite: { termos: p.dados.versaoTermos, privacidade: p.dados.versaoPrivacidade },
      ...(turnstile ? { turnstile } : {}) });
    if (r.status === 201) {
      const conta = await lerConta();
      if (!conta) throw new Error("a conta foi criada e a sessão não veio");
      CT.passo = { tipo: "conta", conta };
      return;
    }
    if (r.status === 403 && objeto(r.corpo).estado === "menos_de_18") { csrf = null; CT.passo = { tipo: "menos_de_18" }; return; }
    if ((r.status === 403 || r.status === 503) && objeto(r.corpo).estado === "turnstile") {
      /* o desafio não passou (ou a Cloudflare não respondeu): o acesso pendente fica; o widget volta para outra tentativa */
      tentativasTurnstile++;
      CT.erro = r.status === 503 ? "A verificação contra robôs não respondeu. Tente de novo em instantes." : "A verificação contra robôs não passou. Tente de novo.";
      return;
    }
    if (r.status === 401) return sessaoAcabou();
    if (r.status === 409) {
      /* os termos mudaram no meio, ou a identidade ja tem conta: pergunta de novo em que pe esta */
      const de_novo = await lerPrimeiro();
      if (de_novo) { CT.passo = { tipo: "primeiro", dados: de_novo }; CT.erro = "Os termos mudaram. Leia e aceite de novo."; return; }
      const conta = await lerConta();
      if (conta) { CT.passo = { tipo: "conta", conta }; return; }
      return sessaoAcabou();
    }
    throw recusa(r.status, r.corpo);
  });
}
/** sai do primeiro acesso sem criar nada */
export async function cancelarPrimeiro(): Promise<void> {
  if (CT.passo?.tipo !== "primeiro") throw new Error("cancelar só no primeiro acesso");
  await mudar(async () => {
    const r = await chamar("POST", "/conta/primeiro-acesso/cancelar");
    if (r.status !== 200 && r.status !== 401) throw recusa(r.status, r.corpo);
    csrf = null;
    await lerProvedores();
    CT.passo = { tipo: "sem_conta" };
  });
}
/** desconecta outro aparelho da conta */
export async function desconectar(id: string): Promise<void> {
  const p = CT.passo;
  if (p?.tipo !== "conta") throw new Error("desconectar só com a conta aberta");
  const alvo = p.conta.aparelhos.find(a => a.id === id);
  if (!alvo) throw new Error(`aparelho desconhecido: ${id}`);
  if (alvo.atual) throw new Error("este aparelho sai pelo Sair");
  await mudar(async () => {
    const r = await chamar("DELETE", `/conta/aparelhos/${encodeURIComponent(id)}`);
    if (r.status === 401) return sessaoAcabou();
    if (r.status !== 200 && r.status !== 404) throw recusa(r.status, r.corpo);
    CT.passo = { tipo: "conta", conta: { ...p.conta, aparelhos: p.conta.aparelhos.filter(a => a.id !== id) } };
  });
}
/** sai da conta neste aparelho; o pet continua aqui */
export async function sair(): Promise<void> {
  if (CT.passo?.tipo !== "conta") throw new Error("sair só com a conta aberta");
  await mudar(async () => {
    const r = await chamar("POST", "/auth/sair");
    if (r.status !== 200 && r.status !== 401) throw recusa(r.status, r.corpo);
    csrf = null;
    await lerProvedores();
    CT.passo = { tipo: "sem_conta" };
  });
}
/** apaga a conta no servidor; o pet deste aparelho fica */
export async function apagarConta(): Promise<void> {
  if (CT.passo?.tipo !== "conta") throw new Error("apagar só com a conta aberta");
  await mudar(async () => {
    const r = await chamar("DELETE", "/conta", { confirmar: "apagar" });
    if (r.status === 401) return sessaoAcabou();
    if (r.status !== 200) throw recusa(r.status, r.corpo);
    csrf = null;
    CT.passo = { tipo: "apagada" };
  });
}
/** a tela diz que uma acao nao deu (um erro alto ja foi para o console) */
export function avisarErroDaConta(frase: string): void { CT.erro = frase; avisar(); }
