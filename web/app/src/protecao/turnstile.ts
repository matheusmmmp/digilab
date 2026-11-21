/* O widget do Turnstile da Cloudflare (CN4): o script da Cloudflare, carregado só quando o servidor manda a chave do site (sem ela, nada
   daqui roda e a página não fala com a Cloudflare). O token sai do widget e vai ao servidor, que confere no siteverify
   (servidor_web/src/protecao/turnstile.ts). Só a chave do site (pública) passa pelo jogo; o segredo fica no servidor. */

export const URL_SCRIPT_TURNSTILE = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

/** o pedaço da API do widget que o jogo usa (a documentação do Turnstile, "explicit rendering") */
export interface ApiTurnstile {
  render(onde: HTMLElement, opcoes: {
    sitekey: string; action: string; callback: (token: string) => void;
    "expired-callback"?: () => void; "error-callback"?: () => void; theme?: "light" | "dark" | "auto";
  }): string;
  remove(id: string): void;
  reset(id: string): void;
}

let promessa: Promise<ApiTurnstile> | null = null;

/** carrega o script uma vez; falha alto se não carregar (a tela diz que a verificação não abriu) */
export function carregarTurnstile(): Promise<ApiTurnstile> {
  const w = window as unknown as { turnstile?: ApiTurnstile };
  if (w.turnstile) return Promise.resolve(w.turnstile);
  promessa ??= new Promise<ApiTurnstile>((ok, falha) => {
    const s = document.createElement("script");
    s.src = URL_SCRIPT_TURNSTILE;
    s.async = true;
    s.onload = () => (w.turnstile ? ok(w.turnstile) : falha(new Error("o script do Turnstile carregou sem a API")));
    s.onerror = () => falha(new Error("o script do Turnstile não carregou"));
    document.head.appendChild(s);
  });
  promessa.catch(() => { promessa = null; });
  return promessa;
}

/** um token sem tela própria (o visitante dos assets): o widget aparece num canto enquanto a Cloudflare decide, e some depois */
export async function tokenTurnstile(chaveSite: string, acao: string): Promise<string> {
  const api = await carregarTurnstile();
  const caixa = document.createElement("div");
  caixa.setAttribute("data-testid", "turnstile-visitante");
  caixa.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:9999";
  document.body.appendChild(caixa);
  let id: string | null = null;
  try {
    return await new Promise<string>((ok, falha) => {
      id = api.render(caixa, { sitekey: chaveSite, action: acao, callback: ok,
        "expired-callback": () => falha(new Error("a verificação do Turnstile venceu")),
        "error-callback": () => falha(new Error("a verificação do Turnstile não abriu")) });
    });
  } finally {
    if (id !== null) api.remove(id);
    caixa.remove();
  }
}
