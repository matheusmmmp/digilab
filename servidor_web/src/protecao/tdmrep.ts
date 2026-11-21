/* O aviso de mineração de texto e dados reservada (PI-6, docs/PLANO_V3_CONTA_PROTECAO.md; D-CONTA-231 a 234): o protocolo TDMRep, o
   "TDM Reservation Protocol (TDMRep)", Final Community Group Report de 10 de maio de 2024, do grupo do W3C
   (https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/). Não é norma do W3C; é o formato legível por máquina da
   reserva do artigo 4 da diretiva europeia 2019/790. Três formas, todas com o mesmo valor (1 = os direitos de mineração estão reservados):
     - o arquivo `/.well-known/tdmrep.json` de cada origem: uma lista de regras {location, tdm-reservation}; a lista é obrigatória mesmo
       com uma regra só (a seção 6.2 do relatório);
     - o cabeçalho `tdm-reservation: 1` na resposta a GET e HEAD (a seção 6.3); vale sem o `tdm-policy`;
     - a meta `<meta name="tdm-reservation" content="1">` no HTML (a seção 6.4).
   O `tdm-policy` (a URL da licença de mineração) fica de fora: não há licença a oferecer, e os termos de uso são da CN6 (PI-5;
   D-CONTA-232). Uma fonte só para as quatro saídas: o servidor (as rotas), o Worker dos assets, o build do jogo (gerado por
   `node scripts/gerar_robots.ts`) e a raiz do site montada pelo `deploy/montar_site.sh`. */

/** o valor da reserva: 1 = reservado (o relatório usa 1 e 0) */
export const TDM_RESERVA = 1;

/** o caminho do arquivo, em toda origem (o relatório: "MUST be hosted in the /.well-known repository") */
export const CAMINHO_TDMREP = "/.well-known/tdmrep.json";

/** o cabeçalho de toda resposta (o nome em minúsculas, como no relatório) */
export const CABECALHO_TDM = "tdm-reservation";

/** a meta das páginas HTML */
export const META_TDM = `<meta name="tdm-reservation" content="${TDM_RESERVA}">`;

/** o conteúdo do `/.well-known/tdmrep.json`: tudo da origem reservado */
export function tdmrepJson(): string {
  return JSON.stringify([{ location: "/", "tdm-reservation": TDM_RESERVA }], null, 2) + "\n";
}

/** o `_headers` do Cloudflare Pages: o cabeçalho em tudo do site (a raiz e o /jogo/) */
export function headersDoPages(): string {
  return [
    "# Digilab: os cabecalhos do Cloudflare Pages (PI-6, o aviso TDMRep; D-CONTA-233).",
    "# Gerado por servidor_web/scripts/gerar_robots.ts de servidor_web/src/protecao/tdmrep.ts; nao editar a mao.",
    "/*",
    `  ${CABECALHO_TDM}: ${TDM_RESERVA}`,
    "",
  ].join("\n");
}
