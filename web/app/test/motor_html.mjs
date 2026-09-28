// Carrega o motor do jogo web ATUAL (web/digilab_sprites.html) em Node, sem DOM.
// O motor e extraido pelas marcas /* @motor-inicio:<nome> */ ... /* @motor-fim:<nome> */ do HTML
// (TAREFA_FRONT_TS, Etapa 1). Serve de referencia para os gabaritos de paridade: o motor em
// TypeScript tem que reproduzir o que este motor produz.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const HTML = fileURLToPath(new URL("../../digilab_sprites.html", import.meta.url));

/** trechos do motor, na ordem do arquivo; falha alto se uma marca faltar ou estiver trocada */
export function extrairMotor(html = readFileSync(HTML, "utf8")) {
  const re = /\/\* @motor-inicio:([a-z-]+)[^*]*\*\/\n([\s\S]*?)\/\* @motor-fim:([a-z-]+) \*\//g;
  const trechos = [];
  for (const m of html.matchAll(re)) {
    if (m[1] !== m[3]) throw new Error(`marca trocada: inicio ${m[1]}, fim ${m[3]}`);
    trechos.push({ nome: m[1], codigo: m[2] });
  }
  const nomes = trechos.map(t => t.nome).join(",");
  if (nomes !== "nucleo,carater,gambits-pet") throw new Error("marcas do motor inesperadas: " + nomes);
  return trechos;
}

/** executa o motor extraido num contexto isolado e devolve os simbolos pedidos */
export function carregarMotor(simbolos) {
  const codigo = extrairMotor().map(t => t.codigo).join("\n");
  /* ajudantes de EXIBICAO que o motor do HTML chama ao montar um lutador (chave de sprite, cor do
     placeholder). Nao entram no estado nem na assinatura; no TS ficam fora do motor. */
  const exibicao = {
    digimon: m => "sprite:" + JSON.stringify(m.forma), corForma: () => "cor",
    spriteNPC: n => "npc:" + n.k, spriteBot: nome => "bot:" + nome, DIGIMON_BOT: {},
  };
  const ctx = vm.createContext({ console, ...exibicao });
  const saida = `\n;({${simbolos.join(", ")}})`;
  return new vm.Script(codigo + saida, { filename: "motor_html.js" }).runInContext(ctx);
}
