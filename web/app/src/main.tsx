/* Entrada do app. Tema: o do sistema; ?tema=claro|escuro sobrepoe (conferencia e screenshots; nao grava nada). Pele dos menus: a
   escolhida ou a Holografica; ?pele=xcom|vidro sobrepoe do mesmo jeito (pele.ts). */
import { createRoot } from "react-dom/client";
import { App } from "./App.tsx";
import { ATLAS_URL, CLIPES_UP, carregarAtlas } from "./atlas.ts";
import { carregarDecoracao } from "./decoracao.ts";
import { iniciarFalaLLM } from "./fala.ts";
import { iniciarFalaLivre } from "./falaLivre.ts";
import { gravarPendente, iniciarJogo, jogoAtual, ouvirOutrasAbas } from "./jogo.ts";
import { textoSave } from "./save.ts";
import { iniciarEscala } from "./escala.ts";
import { iniciarHabitat } from "./habitat.ts";
import { iniciarPele } from "./pele.ts";
import { iniciarTema } from "./tema.ts";
import { iniciarTempo } from "./tempo.ts";
import { CHAVE_GUARDADOS, semearGuardados } from "./pets.ts";
import { descartarPetsAntigos } from "./tamer.ts";
import { ligarEscala } from "../motor/index.ts";
import { CENA } from "./telas/pet/cenaEstado.ts";
import { lugaresNomeados } from "./telas/pet/vistaMundo.ts";
import "./estilo/tokens.css";
import "./estilo/base.css";
import "./estilo/pet.css";
import "./estilo/crescer.css";
import "./estilo/evolucao.css";
import "./estilo/treino.css";
import "./estilo/lutar.css";
import "./estilo/diario.css";
import "./estilo/decoracao.css";
import "./estilo/digibrain.css";
import "./estilo/pet_home.css";
import "./estilo/mundo.css";
import "./estilo/hud.css";
import "./estilo/casca.css";
import "./estilo/tailwind.css";
/* as peles por ultimo: os seletores levam :root[data-pele="xcom|vidro"] e vencem tambem os CSS importados pelas telas */
import "./estilo/pele-xcom.css";
import "./estilo/pele-vidro.css";

iniciarTema();
iniciarPele();
iniciarHabitat();
iniciarEscala();
/* escala de stats (ConfigEscala, TAREFA_PLANILHA_PROGRESSAO Parte C) ligada no jogo; ?escala=0 desliga so para a
   conferencia de paridade com o HTML antigo (e2e), que nao tem a escala */
ligarEscala(new URLSearchParams(location.search).get("escala") !== "0");

/* descarte unico dos pets antigos (decisoes do Matheus): os v1-v5 na chegada das medalhas do Tamer
   (docs/DESIGN_MEDALHAS_ARENAS.md) e os v6 de antes do combate V21D (docs/VALIDACAO_V21D.md); o aviso fica pendente para o
   App; roda uma vez por versao do descarte (tamer.CHAVE_DESCARTE). Antes de abrir o save */
try { descartarPetsAntigos(localStorage, CHAVE_GUARDADOS); } catch (err) { console.error("descarte dos pets antigos falhou", err); }
iniciarJogo(localStorage);
/* a constante CLIPES_UP (ligada desde a H1b da ilha) liga os clipes do UP; ?clipes_up=1 tambem os liga naquela aba, como antes */
carregarAtlas(ATLAS_URL, CLIPES_UP || new URLSearchParams(location.search).get("clipes_up") === "1");
carregarDecoracao();
ouvirOutrasAbas();
iniciarTempo();
iniciarFalaLLM();
iniciarFalaLivre();
/* o tempo grava no maximo a cada 2 s: o que ficou pendente sai ao esconder ou fechar a aba */
addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") gravarPendente(); });
addEventListener("pagehide", gravarPendente);
/* conferencia (teste ponta a ponta, Etapa 5): so leitura do pet vivo; nada aqui muda o motor */
/* o que os testes leem (so leitura): a assinatura, o registro, o tick, o DigiBrain e, nos pets v12, o mundo do motor e a vista dele
   (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2: o E2E-COMIDA e o E2E-CENA) */
const lerMundo = () => {
  const m = jogoAtual().motor, mu = m.mundo;
  return mu && { pet: [...mu.pet], comedouro: [...mu.comedouro], comidas: [...mu.comidas.values()].map(c => ({ id: c.id, x: c.x, y: c.y, situacao: mu.situacao(c, m.e.tick) })),
    consumos: mu.consumos.map(c => ({ id: c.id, tick: c.tick, situacao: c.situacao, fome_antes: c.fome_antes, fome_depois: c.fome_depois })), fome: m.e.fome, acao: m.acao,
    lugares: lugaresNomeados(mu) };
};
Object.assign(window, { __digilab: { assinatura: () => jogoAtual().motor.assinatura(), registro: () => textoSave(jogoAtual().motor), tick: () => jogoAtual().motor.e.tick, digibrain: () => jogoAtual().motor.digibrain(),
  mundo: lerMundo, cena: () => CENA.mundo && { pet: [...CENA.mundo.pet], modo3d: CENA.modo3d }, cenaPara: (x: number, y: number) => CENA.mundo?.paraTela(x, y) ?? null } });
/* varios pets: no primeiro acesso a esta versao, a escada de pets guardados de exemplo (fraco -> forte), depois da
   primeira pintura para nao atrasar a abertura */
setTimeout(() => { try { semearGuardados(); } catch (err) { console.error("pets guardados de exemplo:", err); } }, 400);
const raiz = document.getElementById("app");
if (!raiz) throw new Error("sem #app na página");
createRoot(raiz).render(<App />);
