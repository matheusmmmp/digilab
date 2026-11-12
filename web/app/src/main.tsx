/* Entrada do app. Tema: o do sistema; ?tema=claro|escuro sobrepoe (conferencia e screenshots; nao grava nada). Pele dos menus: a
   escolhida ou a Holografica; ?pele=xcom|vidro sobrepoe do mesmo jeito (pele.ts). */
import { createRoot } from "react-dom/client";
import { App } from "./App.tsx";
import { ATLAS_URL, CLIPES_UP, carregarAtlas } from "./atlas.ts";
import { carregarDecoracao } from "./decoracao.ts";
import { iniciarFalaLLM } from "./fala.ts";
import { iniciarFalaLivre } from "./falaLivre.ts";
import { focar, gravarPendente, iniciarJogo, jogoAtual, ouvirOutrasAbas, textoDaTela } from "./jogo.ts";
import { textoSave } from "./save.ts";
import { iniciarEscala } from "./escala.ts";
import { iniciarHabitat } from "./habitat.ts";
import { iniciarPele } from "./pele.ts";
import { iniciarTema } from "./tema.ts";
import { iniciarTempo } from "./tempo.ts";
import { CHAVE_GUARDADOS, semearGuardados } from "./pets.ts";
import { descartarPetsAntigos } from "./tamer.ts";
import { lutaPocLigada } from "./lutaPoc.ts";
import { ligarEscala } from "../motor/index.ts";
import { comerAgora, dormirAgora, emburrarAgora, reacaoAtual } from "./telas/pet/cenaAcao.ts";
import { CENA } from "./telas/pet/cenaEstado.ts";
import { reacaoRostoAgora } from "./telas/pet/reacao.ts";
import { bolaVista, clipeMomentoAgora, motivoAgora } from "./telas/pet/momentos.ts";
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
import "./estilo/minimapa.css";
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
try { descartarPetsAntigos(localStorage, CHAVE_GUARDADOS, lutaPocLigada()); } catch (err) { console.error("descarte dos pets antigos falhou", err); }
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
/* o que os testes leem (so leitura): a assinatura, o registro, o tick, o DigiBrain, o corpo do comer e, nos pets v12, o mundo do motor e a vista dele
   (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2: o E2E-COMIDA e o E2E-CENA) */
const lerMundo = () => {
  const m = jogoAtual().motor, mu = m.mundo;
  return mu && { pet: [...mu.pet], comedouro: [...mu.comedouro], comidas: [...mu.comidas.values()].map(c => ({ id: c.id, x: c.x, y: c.y, situacao: mu.situacao(c, m.e.tick) })),
    consumos: mu.consumos.map(c => ({ id: c.id, tick: c.tick, situacao: c.situacao, fome_antes: c.fome_antes, fome_depois: c.fome_depois })), fome: m.e.fome, acao: m.acao,
    lugares: lugaresNomeados(mu), bola: mu.bolaEm(m.e.tick), rolagens: mu.rolagens.length,
    /* o lance do dono (BOLA_BRINCAR, BB3): os lances e os ticks das rolagens no relogio do mundo, e o tick de agora nele (null sem o lance) */
    lances: mu.lances && mu.lances.map(l => ({ tick: l.tick, para: [...l.para] })), rolagensTicks: mu.rolagens.map(r => (r as { tick: number }).tick), tickMundo: mu.tm(m.e.tick),
    versao: m.versao, cerebro: m.cerebroAtual };
};
Object.assign(window, { __digilab: { assinatura: () => jogoAtual().motor.assinatura(), registro: () => textoDaTela(), grupo: () => { const j = jogoAtual(); return j.grupo ? { foco: j.foco, ids: [...j.grupo.ids], ticks: j.grupo.ids.map(i => j.grupo!.motor(i).e.tick), especies: j.grupo.ids.map(i => j.grupo!.motor(i).especie), chamados: j.grupo.ids.map(i => j.grupo!.motor(i).chamadosAbertos()) } : null; }, focar: (i: string) => focar(i), tick: () => jogoAtual().motor.e.tick, digibrain: () => jogoAtual().motor.digibrain(),
  mundo: lerMundo, cena: () => CENA.mundo && { pet: [...CENA.mundo.pet], bola: CENA.mundo.bola ?? null, modo3d: CENA.modo3d, ret: CENA.ret },
  reacao: () => reacaoAtual(performance.now()),
  /* o que tocou no comer no ultimo quadro da ilha: "clipe", "gesto" ou null (cenaAcao.ts, escolherComer; docs/TAREFA_V3_SPRITES_ACOES.md, M4) */
  comer: () => comerAgora().tocou, emburrar: () => emburrarAgora(), dormir: () => dormirAgora(), reacaoRosto: () => reacaoRostoAgora(), clipeMomento: () => clipeMomentoAgora(), momento: () => motivoAgora(), bolaVista: () => bolaVista(), cenaPara: (x: number, y: number) => CENA.mundo?.paraTela(x, y) ?? null,
  /* o pet na mao (PegarPet.tsx; docs/TAREFA_V3_PEGAR_PET.md, P2) */
  petNaMao: () => CENA.petNaMao,
  /* o prototipo do gosto visual (so com `?gosto_visual=1`; sem ela, falso e null): a TV da ilha sob o ponto, e o sinal da reacao sobre o pet.
     `sinalTv` anda a fila do sinal como o palco faz (o minimo de 3 s conta desde a primeira leitura): e estado de vista, nada do motor */
  tvEm: (x: number, y: number) => CENA.mundo?.tvEm?.(x, y) ?? false, sinalTv: () => CENA.sinalTv?.(performance.now()) ?? null } });
/* varios pets: no primeiro acesso a esta versao, a escada de pets guardados de exemplo (fraco -> forte), depois da
   primeira pintura para nao atrasar a abertura */
setTimeout(() => { try { semearGuardados(); } catch (err) { console.error("pets guardados de exemplo:", err); } }, 400);
const raiz = document.getElementById("app");
if (!raiz) throw new Error("sem #app na página");
createRoot(raiz).render(<App />);
