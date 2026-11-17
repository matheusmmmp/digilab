/* As duas páginas HTML do local (nenhuma é tela do jogo; as telas são do app, no PR das telas):
   - a "autorização" do provedor falso, onde se escolhe o usuário de teste (ana está na lista de convidados padrão; bia não);
   - a /dev/conta, que percorre o fluxo inteiro pela API: entrar, o primeiro acesso, a conta, os aparelhos, baixar, sair e apagar.
   Só existem com o provedor falso ligado ou no local (rotas.ts). */

const esc = (s: string): string => s.replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]!);

const ESTILO = `body{font:15px system-ui,sans-serif;max-width:560px;margin:24px auto;padding:0 16px;background:#0f1a1f;color:#dfe9ec}
button,select,input{font:inherit}button{padding:8px 12px;margin:4px 4px 4px 0;min-height:44px}fieldset{border:1px solid #3a5560;margin:12px 0}
a{color:#7fd3da}.erro{color:#ff9b8a}.ok{color:#9be3a0}li{margin:6px 0}code{background:#1c2c33;padding:1px 4px}`;

export function paginaAutorizarFalso(state: string, desafio: string, redirectUri: string): string {
  return `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Provedor falso</title><style>${ESTILO}</style>
<h1>Provedor falso (só local)</h1>
<p>Escolha o usuário de teste. Nenhum dado sai desta máquina.</p>
<form method="post" action="/auth/falso/autorizar">
<input type="hidden" name="state" value="${esc(state)}"><input type="hidden" name="code_challenge" value="${esc(desafio)}">
<input type="hidden" name="redirect_uri" value="${esc(redirectUri)}">
<label>Usuário <input name="usuario" value="ana" pattern="[a-z0-9_-]{1,32}" required></label>
<p><button type="submit">Autorizar</button></p>
<p><small><code>ana</code> está na lista de convidados padrão; <code>bia</code> não (o estado "fora da lista").</small></p>
</form></html>`;
}

export function paginaDevConta(): string {
  return `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Conta (teste local)</title><style>${ESTILO}</style>
<h1>Conta: teste local da API</h1>
<p>Esta página não é tela do jogo: percorre o fluxo da CN2 com o provedor falso.</p>
<div id="estado" role="status"></div><div id="app"></div>
<script>
const app = document.getElementById("app"), estadoEl = document.getElementById("estado");
const el = (tag, props = {}, ...filhos) => { const e = Object.assign(document.createElement(tag), props); e.append(...filhos); return e; };
const aviso = (texto, classe = "") => { estadoEl.className = classe; estadoEl.textContent = texto; };
const api = async (metodo, caminho, csrf, corpo) => {
  const headers = {}; if (csrf) headers["X-CSRF-Token"] = csrf; if (corpo !== undefined) headers["Content-Type"] = "application/json";
  const r = await fetch(caminho, { method: metodo, headers, credentials: "include", body: corpo === undefined ? undefined : JSON.stringify(corpo) });
  return { status: r.status, dados: r.headers.get("content-type")?.includes("json") ? await r.json() : null };
};
const TEXTO = { entrou: "Entrou.", primeiro_acesso: "Primeiro acesso: crie a conta.", fora_da_lista: "Fora da lista de convidados. Nada foi guardado.",
  nao_deu: "Não deu para entrar. Nada foi guardado; o jogo continua." };
async function entrar() {
  const { dados } = await api("GET", "/auth/provedores");
  app.replaceChildren(el("h2", { textContent: "Entrar" }), ...dados.map(p => p.ligado
    ? el("p", {}, el("a", { href: "/auth/" + p.nome + "?volta=%23/dev", textContent: "Entrar com " + p.nome }))
    : el("p", { textContent: p.nome + ": desligado (" + p.motivo + ")" })));
}
async function primeiroAcesso() {
  const { status, dados: p } = await api("GET", "/conta/primeiro-acesso");
  if (status !== 200) return entrar();
  const apelido = el("strong", { textContent: p.apelido });
  const escolha = el("select", {}, ...p.digimons.map(d => el("option", { value: d, textContent: d })));
  const trocar = el("button", { type: "button", textContent: "Trocar", onclick: async () => {
    const r = await api("POST", "/conta/primeiro-acesso/apelido", p.csrf, { digimon: escolha.value });
    if (r.status === 200) apelido.textContent = r.dados.apelido; } });
  const idades = el("fieldset", {}, el("legend", { textContent: "Idade" }), ...p.idades.map(i => el("label", {},
    el("input", { type: "radio", name: "idade", value: i }), i === "18_ou_mais" ? " 18 anos ou mais " : " menos de 18 ")));
  const aceite = el("input", { type: "checkbox", id: "aceite" });
  const criar = el("button", { type: "button", textContent: "Criar a conta", onclick: async () => {
    const idade = app.querySelector("input[name=idade]:checked")?.value;
    if (!idade) return aviso("Escolha a idade.", "erro");
    if (!aceite.checked) return aviso("Marque o aceite.", "erro");
    const r = await api("POST", "/conta/primeiro-acesso", p.csrf, { idade, aceite: { termos: p.versao_termos, privacidade: p.versao_privacidade } });
    if (r.status === 201) { history.replaceState(null, "", "/dev/conta?conta=entrou"); aviso("Conta criada: " + r.dados.conta.apelido, "ok"); return conta(); }
    if (r.status === 403) { aviso("Só convidados com 18 anos ou mais, por enquanto. Nada foi guardado.", "erro"); return entrar(); }
    aviso(r.dados?.erro ?? "erro " + r.status, "erro"); } });
  const cancelar = el("button", { type: "button", textContent: "Cancelar", onclick: async () => {
    await api("POST", "/conta/primeiro-acesso/cancelar", p.csrf); aviso("Cancelado. Nada foi guardado."); entrar(); } });
  app.replaceChildren(el("h2", { textContent: "Primeiro acesso (" + p.provedor + ")" }), el("p", {}, "Apelido: ", apelido, " ", escolha, trocar),
    idades, el("p", {}, aceite, el("label", { htmlFor: "aceite", textContent: " Aceito os termos (" + p.versao_termos + ") e a privacidade (" + p.versao_privacidade + ")" })),
    criar, cancelar);
}
async function conta() {
  const { status, dados: d } = await api("GET", "/conta");
  if (status !== 200) return entrar();
  const { dados: aparelhos } = await api("GET", "/conta/aparelhos");
  const lista = el("ul", {}, ...aparelhos.map(a => el("li", {}, a.nome + (a.atual ? " (este)" : "") + " · visto " + a.visto_em + " ",
    el("button", { type: "button", textContent: "Desconectar", onclick: async () => {
      await api("DELETE", "/conta/aparelhos/" + a.id, d.csrf); conta(); } }))));
  const confirma = el("input", { type: "checkbox", id: "confirma" });
  app.replaceChildren(el("h2", { textContent: d.conta.apelido }),
    el("p", { textContent: "Provedor: " + d.provedores.join(", ") + " · criada " + d.conta.criada_em + " · termos " + d.consentimentos.map(x => x.versao_termos).join(", ") }),
    el("h3", { textContent: "Aparelhos" }), lista,
    el("p", {}, el("a", { href: "/conta/dados", textContent: "Baixar meus dados" })),
    el("button", { type: "button", textContent: "Sair", onclick: async () => { await api("POST", "/auth/sair", d.csrf); aviso("Saiu."); entrar(); } }),
    el("fieldset", {}, el("legend", { textContent: "Apagar a conta (sem volta)" }), confirma, el("label", { htmlFor: "confirma", textContent: " Entendi que não volta " }),
      el("button", { type: "button", textContent: "Apagar para sempre", onclick: async () => {
        if (!confirma.checked) return aviso("Marque que entendeu.", "erro");
        const r = await api("DELETE", "/conta", d.csrf, { confirmar: "apagar" });
        if (r.status === 200) { aviso("Conta apagada.", "ok"); entrar(); } } })));
}
const estado = new URLSearchParams(location.search).get("conta");
if (estado && TEXTO[estado]) aviso(TEXTO[estado], estado === "entrou" || estado === "primeiro_acesso" ? "ok" : "erro");
(estado === "primeiro_acesso" ? primeiroAcesso() : conta());
</script></html>`;
}
