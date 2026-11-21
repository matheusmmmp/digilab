/* O Turnstile da Cloudflare (CN4, docs/PLANO_V3_CONTA.md seção 6): o desafio sem captcha na criação da conta e no primeiro pedido de assets
   de um visitante. A página resolve o desafio e manda o token; o servidor confere o token na Cloudflare (siteverify) com o segredo, que só
   vem do ambiente (TURNSTILE_SECRET_KEY), nunca do repositório.

   Os testes usam as chaves de teste oficiais da Cloudflare (as CHAVES_DE_TESTE abaixo, públicas na documentação do Turnstile) com um fetch
   falso que responde como a Cloudflare responde a elas: nenhuma chamada sai da máquina. */

export const URL_SITEVERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
/** o token do Turnstile tem até 2048 caracteres (a documentação do siteverify) */
export const TAMANHO_MAXIMO_TOKEN = 2048;
/** quanto o servidor espera a Cloudflare responder, em ms (PROPOSTO, SEM FONTE) */
export const ESPERA_SITEVERIFY_MS = 5000;

/** as chaves de teste oficiais (públicas): o segredo que sempre passa, o que sempre falha e o do token já usado; e as chaves do site */
export const CHAVES_DE_TESTE = {
  segredoPassa: "1x0000000000000000000000000000000AA",
  segredoFalha: "2x0000000000000000000000000000000AA",
  segredoUsado: "3x0000000000000000000000000000000AA",
  sitePassa: "1x00000000000000000000AA",
  siteBloqueia: "2x00000000000000000000AB",
  tokenFalso: "XXXX.DUMMY.TOKEN.XXXX",
} as const;

export type Buscar = (url: string, init: RequestInit) => Promise<Response>;

/** os pontos que pedem o desafio; o `action` do widget na página é o mesmo nome */
export type PontoTurnstile = "cadastro" | "visitante";

export interface Turnstile {
  /** a chave do site (pública: vai para a página desenhar o widget) */
  readonly chaveSite: string;
  conferir(token: unknown, ponto: PontoTurnstile): Promise<ResultadoTurnstile>;
}

export type ResultadoTurnstile =
  | { ok: true }
  | { ok: false; motivo: "sem_token" | "token_invalido" | "nao_passou" | "indisponivel"; codigos: string[] };

/** a conferência de verdade pelo siteverify; `buscar` é o fetch (o falso nos testes) */
export class TurnstileCloudflare implements Turnstile {
  readonly chaveSite: string;
  private readonly segredo: string;
  private readonly buscar: Buscar;

  constructor(segredo: string, chaveSite: string, buscar: Buscar = (u, i) => fetch(u, i)) {
    if (!segredo) throw new Error("o Turnstile ligado precisa do TURNSTILE_SECRET_KEY");
    if (!chaveSite) throw new Error("o Turnstile ligado precisa do TURNSTILE_SITE_KEY (a página desenha o widget com ela)");
    this.segredo = segredo;
    this.chaveSite = chaveSite;
    this.buscar = buscar;
  }

  async conferir(token: unknown, ponto: PontoTurnstile): Promise<ResultadoTurnstile> {
    if (token === undefined || token === null || token === "") return { ok: false, motivo: "sem_token", codigos: [] };
    if (typeof token !== "string" || token.length > TAMANHO_MAXIMO_TOKEN) return { ok: false, motivo: "token_invalido", codigos: [] };
    let d: { success?: unknown; "error-codes"?: unknown; action?: unknown };
    try {
      const r = await this.buscar(URL_SITEVERIFY, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ secret: this.segredo, response: token }).toString(), signal: AbortSignal.timeout(ESPERA_SITEVERIFY_MS) });
      if (!r.ok) return { ok: false, motivo: "indisponivel", codigos: [`http_${r.status}`] };
      d = await r.json() as typeof d;
    } catch (err) {
      /* a Cloudflare fora do ar: fecha (não deixa passar sem conferir) */
      return { ok: false, motivo: "indisponivel", codigos: [(err as Error)?.name ?? "Error"] };
    }
    const codigos = Array.isArray(d["error-codes"]) ? d["error-codes"].map(String) : [];
    if (d.success !== true) return { ok: false, motivo: "nao_passou", codigos };
    /* o token de um widget de outro ponto não serve aqui (a ação vazia é a das chaves de teste) */
    if (typeof d.action === "string" && d.action !== "" && d.action !== ponto) return { ok: false, motivo: "nao_passou", codigos: ["action_diferente"] };
    return { ok: true };
  }
}

/** o fetch falso que responde como o siteverify responde às chaves de teste oficiais (para os testes) */
export function siteverifyDeTeste(chamadas: { segredo: string; token: string }[] = []): Buscar {
  return async (url, init) => {
    if (url !== URL_SITEVERIFY) throw new Error(`fetch inesperado: ${url}`);
    const f = new URLSearchParams(String(init.body));
    const segredo = f.get("secret") ?? "", token = f.get("response") ?? "";
    chamadas.push({ segredo, token });
    const resposta = (dados: unknown) => new Response(JSON.stringify(dados), { status: 200, headers: { "Content-Type": "application/json" } });
    if (segredo === CHAVES_DE_TESTE.segredoPassa) return resposta({ success: true, "error-codes": [], hostname: "example.com", action: "", cdata: "" });
    if (segredo === CHAVES_DE_TESTE.segredoFalha) return resposta({ success: false, "error-codes": ["invalid-input-response"] });
    if (segredo === CHAVES_DE_TESTE.segredoUsado) return resposta({ success: false, "error-codes": ["timeout-or-duplicate"] });
    return resposta({ success: false, "error-codes": ["invalid-input-secret"] });
  };
}
