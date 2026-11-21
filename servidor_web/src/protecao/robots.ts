/* O robots.txt (CN4, docs/PLANO_V3_CONTA.md seção 6): recusa os robôs de IA declarados. Só segura os honestos; os grandes respeitam.
   Duas versões, de uma fonte só (esta lista):
     - a do jogo (`web/app/public/robots.txt`, que o build do Vite copia para a raiz do site): os robôs de IA fora de tudo; os outros podem
       ver as páginas públicas (as da CN6), menos os assets. Gerado por `node scripts/gerar_robots.ts`; o teste reprova se esquecer;
     - a da API (`GET /robots.txt` deste servidor): ninguém indexa nada, porque a API não tem página.
   Os nomes dos robôs saem das páginas públicas de cada empresa e de listas de terceiros; NÃO CONFERIDOS um a um neste PR (D-CONTA-210). */

/** os robôs de IA declarados (o User-agent de cada um), por empresa */
export const ROBOS_DE_IA: readonly string[] = [
  /* OpenAI */ "GPTBot", "OAI-SearchBot", "ChatGPT-User",
  /* Anthropic */ "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
  /* Common Crawl (a base de muitos treinos) */ "CCBot",
  /* Google e Apple: o uso para IA, separado da busca */ "Google-Extended", "Applebot-Extended",
  /* Perplexity */ "PerplexityBot", "Perplexity-User",
  /* ByteDance */ "Bytespider",
  /* Amazon */ "Amazonbot",
  /* Meta */ "meta-externalagent", "meta-externalfetcher", "FacebookBot",
  /* Cohere */ "cohere-ai", "cohere-training-data-crawler",
  /* Mistral */ "MistralAI-User",
  /* Allen Institute */ "AI2Bot", "Ai2Bot-Dolma",
  /* outros que treinam ou respondem com IA */ "Diffbot", "ImagesiftBot", "Omgilibot", "Timpibot", "YouBot", "DuckAssistBot",
];

/** os caminhos de assets que nenhum robô precisa ver (o atlas, os sons, os pacotes e os modelos 3D) */
export const CAMINHOS_DE_ASSETS: readonly string[] = ["/assets/", "/enfeites/", "/itens/", "/kits3d/", "/kits3d_digital/", "/lugares/", "/mapa_digital/"];

export function robotsDoJogo(): string {
  const linhas = [
    "# Digilab: o jogo. Os robos de IA nao entram (CN4, docs/PLANO_V3_CONTA.md secao 6).",
    "# Gerado por servidor_web/scripts/gerar_robots.ts de servidor_web/src/protecao/robots.ts; nao editar a mao.",
    "",
    ...ROBOS_DE_IA.map(r => `User-agent: ${r}`),
    "Disallow: /",
    "",
    "User-agent: *",
    ...CAMINHOS_DE_ASSETS.map(c => `Disallow: ${c}`),
    "Allow: /",
    "",
  ];
  return linhas.join("\n");
}

export function robotsDaApi(): string {
  return ["# Digilab: a API. Nada aqui e pagina.", "User-agent: *", "Disallow: /", ""].join("\n");
}
