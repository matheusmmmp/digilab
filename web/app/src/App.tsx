/* Esqueleto do app (TAREFA_FRONT_TS, Etapa 3): cabecalho do pet, painel do destino com sub-abas, barra dos
   4 destinos e rodape. A rota vem do endereco (#/destino/aba) ou da aba lembrada, como no HTML. */
import { useEffect, useRef, useState, type ReactNode } from "react";
import { useAtlas } from "./atlas.ts";
import { useDecoracao } from "./decoracao.ts";
import { Nav } from "./componentes/Nav.tsx";
import { BoasVindas } from "./componentes/BoasVindas.tsx";
import { RevelacaoEvolucao } from "./componentes/Revelacao.tsx";
import { sairDoLab, useJogo } from "./jogo.ts";
import {
  DESTINOS, NOME_ABA, NOME_DESTINO, ROTA_INICIAL, ENDERECO_LUTA, configDoEndereco, ehLuta, enderecoDaConfig, enderecoDaRota, gravarAbaLembrada, lerAbaLembrada,
  rotaDoEndereco, type Aba, type Destino, type ParteConfig, type Rota,
} from "./rotas.ts";
import { TelaConfig } from "./telas/config/TelaConfig.tsx";
import { TelaCatalogo } from "./telas/diario/TelaCatalogo.tsx";
import { TelaCenarios } from "./telas/diario/TelaCenarios.tsx";
import { TelaRegistro } from "./telas/diario/TelaRegistro.tsx";
import { TelaAprend } from "./telas/crescer/TelaAprend.tsx";
import { TelaEvolucao } from "./telas/crescer/TelaEvolucao.tsx";
import { TelaTreinar } from "./telas/crescer/TelaTreinar.tsx";
import { TelaItens } from "./telas/crescer/TelaItens.tsx";
import { TelaArena } from "./telas/lutar/TelaArena.tsx";
import { TelaCampanha } from "./telas/lutar/TelaCampanha.tsx";
import { TelaMedalhas } from "./telas/lutar/TelaMedalhas.tsx";
import { TelaFronteira } from "./telas/lutar/TelaFronteira.tsx";
import { AvisoSom } from "./componentes/AvisoSom.tsx";
import { AvisoPetsDescartados } from "./componentes/Medalha.tsx";
import { AvisoCombateTR, avisoTRPendente } from "./componentes/AvisoCombateTR.tsx";
import { CHAVE_AVISO_V6 } from "./tamer.ts";
import { TelaConversar } from "./telas/conversar/TelaConversar.tsx";
import { TelaLuta } from "./telas/lutar/TelaLuta.tsx";
import { LUTA, REPLAY, previa, pularAnimacao, type Modo } from "./luta.ts";
import { TelaPet } from "./telas/pet/TelaPet.tsx";
import { MeusPets } from "./telas/pet/MeusPets.tsx";
import { TopoHabitat } from "./componentes/Topo.tsx";
import { Habitat } from "./componentes/Habitat.tsx";
import { PainelLado, PainelModal, type DadosPainel } from "./componentes/PainelTela.tsx";
import { LugarFolha, LugarLado, type DadosLugar } from "./componentes/PainelLugar.tsx";
import { BookMarked, BookOpen, Brain, Compass, Dna, Dumbbell, GitBranch, Lock, Medal, Mountain, Package, ScrollText, Sprout, Swords, Theater, type LucideIcon } from "lucide-react";
import { MarcasDoLugar } from "./componentes/MarcasDoLugar.tsx";
import { dAbreDiario, ligarAtalhosLugar } from "./atalhosLugar.ts";
import { entrarLugar, sairLugar, type Lugar } from "./viagem.ts";
import { soltarTeclas } from "./telas/pet/cameraLivre.ts";
import { DicaBit } from "./componentes/Bit.tsx";
import { AcoesMeusPets, MeusPetsDesktop } from "./telas/pet/MeusPetsDesktop.tsx";
import { useDesktop, usePainelLado } from "./desktop.ts";
import { ComoJogar, Conclusao, EscolherBrasao } from "./componentes/Jornada.tsx";
import { ImportarPet } from "./componentes/Importar.tsx";
import { fecharImportar, useImportar } from "./importar.ts";
import { Heranca } from "./componentes/Heranca.tsx";
import { TelaGeracoes } from "./telas/diario/TelaGeracoes.tsx";
import { fecharHeranca, useHeranca } from "./heranca.ts";
import { abrirEscolhaBrasao, concluiuJornada, conclusaoVista, useEscolhaBrasao } from "./jornada.ts";
import { dicasDoMomento, type IdDica } from "./dicas.ts";
import { CHAVE } from "./save.ts";

const armaz = (): Storage => localStorage;

/** os icones das abas do lugar (Crescer, L2; Lutar e Diario, L3): so a escolhida mostra o rotulo; as teclas 1 a 4 trocam de aba */
const ICONE_ABA: Partial<Record<Aba, ReactNode>> = {
  treinar: <Dumbbell aria-hidden="true" />, aprend: <Brain aria-hidden="true" />, evolucao: <GitBranch aria-hidden="true" />, itens: <Package aria-hidden="true" />,
  arena: <Swords aria-hidden="true" />, campanha: <Compass aria-hidden="true" />, fronteira: <Mountain aria-hidden="true" />, medalhas: <Medal aria-hidden="true" />,
  registro: <ScrollText aria-hidden="true" />, catalogo: <BookMarked aria-hidden="true" />, geracoes: <Dna aria-hidden="true" />, cenarios: <Theater aria-hidden="true" />,
};
/** o lugar de cada menu da ilha (Pet, Conversar e Ajustes nao tem), o nome dele no cabecalho e o icone do menu */
const LUGAR_DO_DESTINO: Partial<Record<Destino, { lugar: Lugar; sub: string; icone: LucideIcon }>> = {
  crescer: { lugar: "saco", sub: "saco de pancada", icone: Sprout }, lutar: { lugar: "portao", sub: "portão da arena", icone: Swords }, diario: { lugar: "barraca", sub: "barraca do Tamer", icone: BookOpen },
};
/** a Fronteira so aparece trancada (L3): o visual "Nv 8" e o motivo na dica. A trava de verdade (a regra e os niveis) e outra tarefa, e o conteudo segue aberto.
    PROPOSTO: o texto e o nivel sao da prancha (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, tabela 3.3, linha 8) */
const FRONTEIRA_TRANCADA = { nivel: "Nv 8", dica: "Abre com 6 medalhas" } as const;

/* slogan so na primeira visita (preferencia de tela, chave propria; a chave do save nao muda) */
function primeiraVisita(): boolean {
  try { if (localStorage.getItem(CHAVE + "-boas-vindas") !== "1") { localStorage.setItem(CHAVE + "-boas-vindas", "1"); return true; } } catch { /* sem armazenamento */ }
  return false;
}

function rotaInicial(): Rota {
  return rotaDoEndereco(location.hash) ?? (configDoEndereco(location.hash) ? { destino: "diario", aba: "registro" } : null) ?? lerAbaLembrada(armaz()) ?? ROTA_INICIAL;
}

export function App() {
  const jogo = useJogo(), atlas = useAtlas(), deco = useDecoracao();
  const [rota, setRota] = useState<Rota>(rotaInicial);
  /* Configuracoes: por cima do destino (engrenagem do Diario no celular, da barra lateral no desktop) */
  const [config, setConfig] = useState<ParteConfig | null>(() => configDoEndereco(location.hash));
  /* tutorial contextual (Bit): cada momento da jornada pede a sua dica uma vez */
  const { motor: mDica, nascendo: nascDica } = jogo;
  useEffect(() => {
    if (boasVindas) return;
    const est = mDica.estagioAtual, ids: IdDica[] = [];
    if (nascDica > 0 || (est === "bebe" && mDica.evolucoes.length === 0)) ids.push("ovo");
    if (est === "bebe" && mDica.chamadosAbertos().length) ids.push("chamado");
    if (est === "crianca") ids.push("rookie", "ensinar_v11");
    if (est === "adolescente") ids.push("champion", "lutas_treino");
    if (est === "adulto") ids.push(!mDica.sombria ? "ultimate" : "adulto");
    if (est === "mega") ids.push("adulto");
    if (nascDica === 0 && !mDica.morte && mDica.e.saude < .3) ids.push("saude");
    if (mDica.lesionadoDesde !== null) ids.push("lesao");
    if (est === "adolescente") ids.push("vitorias");
    dicasDoMomento(ids);
  });
  const [boasVindas, setBoasVindas] = useState(() => primeiraVisita() || location.hash === "#/inicio"), [meusPets, setMeusPets] = useState(false);
  /* jornada: sem pet proprio no comeco (so o de exemplo), o Comecar das boas-vindas leva a escolha do brasao */
  const [semPetNoInicio] = useState(() => jogo.origem === "exemplo"), escolhendoBrasao = useEscolhaBrasao();
  /* o pet de exemplo nao e do jogador: enquanto for ele o ativo, a escolha do brasao nao tem Voltar */
  const [sementeExemplo] = useState(() => jogo.motor.semente), aindaSemPet = semPetNoInicio && jogo.motor.semente === sementeExemplo;
  /* primeira abertura com as medalhas: os pets antigos sairam (main.tsx); o aviso fica ate o jogador ler */
  const [descartados, setDescartados] = useState(() => { try { return Number(localStorage.getItem(CHAVE_AVISO_V6) ?? 0); } catch { return 0; } });
  /* o descarte 6 (a luta em tempo real, pets v13): o aviso fica ate o jogador ler */
  const [avisoTR, setAvisoTR] = useState(avisoTRPendente);
  const [conclusao, setConclusao] = useState(false), desk = useDesktop(), lado = usePainelLado(), [comoJogar, setComoJogar] = useState(false), importando = useImportar(), her = useHeranca();
  /* a jornada acabou (pets v6: a Liga dos Lideres; v1-v5: o chefe da campanha): a mensagem de conclusao, uma vez por pet, fora da luta
     e sem outra tela cheia */
  useEffect(() => {
    if (!conclusao && !emLuta && !boasVindas && !comoJogar && !escolhendoBrasao && !descartados && !avisoTR && concluiuJornada(jogo.motor) && !conclusaoVista(jogo.motor)) setConclusao(true);
  });
  /* luta em tela cheia (#/lutar/luta); o Voltar do navegador durante a animacao vira pedido de Desistir */
  const [emLuta, setEmLuta] = useState(() => ehLuta(location.hash)), emLutaRef = useRef(emLuta), [pedidoDesistir, setPedidoDesistir] = useState(false);
  emLutaRef.current = emLuta;
  const [ultima, setUltima] = useState<Partial<Record<Destino, Aba>>>(() => ({ [rota.destino]: rota.aba }));

  /* endereco e aba lembrada acompanham a rota; voltar/avancar do navegador muda a rota */
  useEffect(() => {
    if (emLuta) { document.title = "Luta · Digilab Pet"; return; }
    if (boasVindas) return;                      /* primeira vez aberta: o endereco e #/inicio */
    const alvo = config ? enderecoDaConfig(config) : enderecoDaRota(rota);
    if (location.hash !== alvo) history.replaceState(null, "", alvo);
    gravarAbaLembrada(armaz(), rota);
    document.body.dataset.destino = rota.destino;
    document.title = `${config ? "Configurações" : NOME_DESTINO[rota.destino]} · Digilab Pet`;
  }, [rota, config, emLuta, boasVindas]);
  useEffect(() => {
    const aoMudar = () => {
      if (ehLuta(location.hash)) { setEmLuta(true); return; }
      if (emLutaRef.current) {
        /* saiu da luta pelo Voltar: com a animacao rodando, fica na luta e pergunta; ja no resultado, conta como Continuar */
        /* replay animado: o Voltar so sai (nada foi gravado) */
        if (LUTA.replay !== null) { REPLAY.pedido = LUTA.replay; pularAnimacao(); LUTA.replay = null; previa("arena"); }
        else if (LUTA.lutando) { history.pushState(null, "", ENDERECO_LUTA); setPedidoDesistir(true); return; }
        else previa(LUTA.palco?.modo ?? "arena");
        setEmLuta(false);
      }
      const c = configDoEndereco(location.hash); if (c) { setConfig(c); return; }
      const r = rotaDoEndereco(location.hash); if (r) { setConfig(null); setMeusPets(false); fecharImportar(); fecharHeranca(); setRota(r); }
    };
    addEventListener("hashchange", aoMudar);
    return () => removeEventListener("hashchange", aoMudar);
  }, []);

  const ir = (r: Rota) => { setConfig(null); setMeusPets(false); fecharImportar(); fecharHeranca(); setRota(r); setUltima(u => ({ ...u, [r.destino]: r.aba })); };
  const irDestino = (d: Destino) => { ir({ destino: d, aba: ultima[d] ?? DESTINOS[d][0] }); scrollTo(0, 0); };
  const abrirConfig = (p: ParteConfig) => { setMeusPets(false); setConfig(p); scrollTo(0, 0); };
  const abas = DESTINOS[rota.destino];
  /* fim da luta (Continuar ou Desistir): a entrada da luta no historico vira a aba de origem, e o foco volta ao botao */
  const sairDaLuta = (modo: Modo) => {
    history.replaceState(null, "", `#/lutar/${modo}`);
    setEmLuta(false); ir({ destino: "lutar", aba: modo });
    setTimeout(() => document.querySelector<HTMLElement>(modo === "arena" ? ".lutar-grande" : modo === "fronteira" ? ".fr-lutar" : ".camp-lutar")?.focus(), 60);
  };
  /* Ver replay (Resultado): a entrada da luta vira a aba de origem e o Diario abre por cima, com a luta refeita do registro;
     o Voltar do navegador leva de volta a aba de origem */
  /* fim ou saida do replay animado: volta ao Diario com a mesma luta aberta */
  const sairReplay = (idx: number) => {
    /* o replay entrou no historico por cima do Diario: voltar uma entrada leva ao Diario sem duplica-lo (o hashchange
       fecha a tela cheia e abre o Registro) */
    LUTA.replay = null; REPLAY.pedido = idx;
    history.back();
  };
  const verReplay = (modo: Modo, idx: number) => {
    REPLAY.pedido = idx;
    history.replaceState(null, "", `#/lutar/${modo}`);
    history.pushState(null, "", "#/diario/registro");
    setEmLuta(false); ir({ destino: "diario", aba: "registro" }); scrollTo(0, 0);
  };
  /* replay de uma luta do registro no Diario (card da ultima luta na Arena) */
  const abrirReplay = (idx: number) => { REPLAY.pedido = idx; ir({ destino: "diario", aba: "registro" }); scrollTo(0, 0); };
  /* o painel dos destinos que nao sao o Pet (PainelTela): Crescer, Lutar, Diario, Conversar, Ajustes e, no desktop, as paginas de
     Importar, Nova geracao e Meus pets. O "x" volta para #/pet/estado. */
  const irPet = () => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); };
  const fecharPainel = () => {
    irPet();
    /* abaixo de 900 px nao ha barra: se o foco nao foi para outro lugar (o modal devolve a quem abriu), ele volta ao retrato, de onde a tela Pet parte */
    setTimeout(() => {
      const barra = document.querySelector<HTMLElement>('.dl-nav .hx-nav__bt[aria-current="page"]');
      if (barra) barra.focus(); else if (document.activeElement === document.body) document.querySelector<HTMLElement>(".mm-retrato")?.focus();
    }, 60);
  };
  const corpoDestino = (): ReactNode => rota.aba === "treinar" ? <TelaTreinar /> : rota.aba === "aprend" ? <TelaAprend /> : rota.aba === "evolucao" ? <TelaEvolucao /> : rota.aba === "itens" ? <TelaItens />
    : rota.aba === "arena" ? <TelaArena voltarPet={irPet} verReplay={abrirReplay} />
    : rota.aba === "campanha" ? <TelaCampanha voltarPet={irPet} irTreinar={() => { ir({ destino: "crescer", aba: "treinar" }); scrollTo(0, 0); }} />
    : rota.aba === "medalhas" ? <TelaMedalhas />
    : rota.aba === "fronteira" ? <TelaFronteira />
    : rota.aba === "registro" ? <TelaRegistro irPet={irPet} />
    : rota.aba === "catalogo" ? <TelaCatalogo /> : rota.aba === "geracoes" ? <TelaGeracoes /> : rota.aba === "chat" ? <TelaConversar voltar={irPet} /> : <TelaCenarios />;
  const idBase = "painel-aba";
  let painel: { d: DadosPainel; corpo: ReactNode } | null = null;
  let lugar: { d: DadosLugar; corpo: ReactNode } | null = null;
  if (importando && desk) painel = { d: { titulo: "Importar pet", fechar: fecharImportar, idBase }, corpo: <ImportarPet pagina fechar={fecharImportar} /> };
  else if (her && desk) painel = { d: { titulo: "Nova geração", fechar: fecharHeranca, idBase }, corpo: <Heranca pagina pai2={her.pai2} fim={irPet} /> };
  else if (meusPets && desk) painel = { d: { titulo: "Meus pets", fechar: () => setMeusPets(false), idBase }, corpo: <><div className="painel-tela__acoes"><AcoesMeusPets /></div><MeusPetsDesktop fechar={() => setMeusPets(false)} /></> };
  /* Ajustes (config): nao e um lugar. O mesmo painel dos lugares, sem abas e sem viagem da camera: a 1920 perto do retrato, a 390 a folha de baixo sobre a ilha de sempre */
  else if (config) lugar = { d: { titulo: "Ajustes", sub: "", icone: null, abas: [], aba: "", irAba: () => {}, fechar: fecharPainel, idBase, semLugar: true },
    corpo: <TelaConfig parte={config} abrir={abrirConfig} fechar={() => { setConfig(null); scrollTo(0, 0); }} irPet={irPet} /> };
  /* Crescer, Lutar e o Diario sao lugares da ilha (L2 e L3): o painel ao lado do saco, do portao ou da barraca, com a ilha viva em volta; so com o mundo (os pets sem mundo ficam na sala) */
  else if (LUGAR_DO_DESTINO[rota.destino] && !!jogo.motor.mundo) {
    const L = LUGAR_DO_DESTINO[rota.destino]!, I = L.icone;
    lugar = {
      d: { titulo: NOME_DESTINO[rota.destino], sub: L.sub, icone: <I aria-hidden="true" />, idBase,
        abas: abas.map((a, i) => ({ id: a, rotulo: NOME_ABA[a], icone: ICONE_ABA[a], atalho: String(i + 1), ...(a === "fronteira" ? { trancada: FRONTEIRA_TRANCADA } : {}) })),
        aba: rota.aba, irAba: id => ir({ destino: rota.destino, aba: id as Aba }), fechar: fecharPainel, destino: rota.destino },
      corpo: <>{rota.aba === "fronteira" && <p className="lg-trava"><Lock aria-hidden="true" />{FRONTEIRA_TRANCADA.dica}</p>}{corpoDestino()}</>,
    };
  }
  else if (rota.destino !== "pet") painel = {
    d: { titulo: NOME_DESTINO[rota.destino], abas: abas.map(a => ({ id: a, rotulo: NOME_ABA[a] })), aba: rota.aba, irAba: id => ir({ destino: rota.destino, aba: id as Aba }), fechar: fecharPainel, idBase },
    corpo: corpoDestino(),
  };
  /* a viagem da camera: entrar no lugar leva a camera e o pet ao saco, ao portao ou a barraca (uma troca direta parte do lugar de antes); sair os traz de volta
     (so vista, viagem.ts). Os Ajustes nao viajam */
  const idLugar: Lugar | null = lugar && !lugar.d.semLugar ? LUGAR_DO_DESTINO[rota.destino]!.lugar : null;
  useEffect(() => { if (idLugar) { soltarTeclas(); entrarLugar(performance.now(), idLugar); } else sairLugar(); }, [idLugar]);
  /* os atalhos diretos (atalhosLugar.ts): C, 1 a 4 e Esc; valem so com a casca livre (sem luta, boas-vindas, aviso ou tela por cima) */
  const ref = useRef({ ativo: false, lugar: null as Lugar | null, aba: "" });
  ref.current = { ativo: !emLuta && !boasVindas && !comoJogar && !escolhendoBrasao && !descartados && !avisoTR && !conclusao && !config && !meusPets && !importando && !her,
    lugar: idLugar, aba: rota.aba };
  useEffect(() => ligarAtalhosLugar({
    ativo: () => ref.current.ativo, lugarAberto: () => ref.current.lugar,
    /* o D e o "direita" do WASD da camera solta: so abre o Diario com um lugar aberto (a camera esta parada) ou com a camera que nao solta */
    liberaD: dAbreDiario,
    abrirLugar: l => acoes.current.abrir(l), irAba: i => acoes.current.aba(i), sair: () => acoes.current.sair(),
  }), []);
  const acoes = useRef({ abrir: (_l: Lugar) => {}, aba: (_i: number) => {}, sair: () => {} });
  acoes.current = {
    abrir: l => irDestino(l === "saco" ? "crescer" : l === "portao" ? "lutar" : "diario"),
    aba: i => { const d = rota.destino, a = DESTINOS[d][i]; if (idLugar && a) ir({ destino: d, aba: a }); }, sair: fecharPainel,
  };
  if (emLuta) return (
    <div className="app app--tela-cheia">
      <TelaLuta sair={sairDaLuta} verReplay={verReplay} sairReplay={sairReplay} pedidoDesistir={pedidoDesistir} fecharPedido={() => setPedidoDesistir(false)} />
    </div>
  );
  const nav = <Nav atual={config ? null : rota.destino} ir={irDestino} configAberta={!!config} abrirConfig={() => abrirConfig("principal")} />;
  /* abaixo de 900 px nao ha barra de destinos (M1 do mobile minimo): Crescer, Lutar, Diario e Conversar sao a coluna do topo (Topo.tsx), e o painel e um
     modal que volta ao Pet pelo x, pelo Esc ou pelo toque fora */
  const abrirMeusPets = () => { sairDoLab(); setMeusPets(true); };

  return (
    <div className={"app app--habitat " + (lugar ? "app--painel app--lugar" : painel ? "app--painel" : "app--pet")}>
      <div className="avisos">
      <AvisoSom />
      {jogo.erroSave && (
        <div className="aviso" role="alert">
          O save deste navegador não abriu, e o app não vai gravar por cima dele.
          <p>{jogo.erroSave.erro}. Mostrando o pet de exemplo.</p>
        </div>
      )}
      {atlas.tipo === "erro" && (
        <div className="aviso" role="alert">
          Atlas de sprites não carregou.
          <p>{atlas.erro}. Rode <code>python gerar_atlas_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      {(deco.estado.tipo === "erro" || deco.falhas.size > 0) && (
        <div className="aviso" role="alert">
          Parte da decoração do Digimon UP não carregou; esses lugares ficam com o visual de antes.
          <p>{deco.estado.tipo === "erro" ? deco.estado.erro : [...deco.falhas].map(([n, e]) => `${n} (${e})`).join(", ")}.
            Rode <code>python gerar_decoracao_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      </div>
      <DicaBit />
      {/* o habitat (a cena do Pet) e a camada de fundo de toda rota: fica montado, nao sobe nem desce ao trocar de destino */}
      <Habitat escurecer={!!painel} />
      <TopoHabitat lugar={idLugar ? rota.destino : null} abrirMeusPets={abrirMeusPets} irConversar={() => irDestino("conversar")} irDestino={irDestino} abrirConfig={() => abrirConfig("principal")} />
      {!painel && (!lugar || lugar.d.semLugar) && <TelaPet irRegistro={() => ir({ destino: "diario", aba: "registro" })} irEvolucao={() => { ir({ destino: "crescer", aba: "evolucao" }); scrollTo(0, 0); }}
        abrirConfig={() => abrirConfig("principal")} abrirMeusPets={abrirMeusPets} />}
      {idLugar && lado && <MarcasDoLugar lugar={idLugar} />}
      {lugar && (lado ? <LugarLado d={lugar.d}>{lugar.corpo}</LugarLado> : <LugarFolha d={lugar.d}>{lugar.corpo}</LugarFolha>)}
      {painel && (lado ? <PainelLado d={painel.d}>{painel.corpo}</PainelLado> : <PainelModal d={painel.d}>{painel.corpo}</PainelModal>)}
      {lado && nav}
      <RevelacaoEvolucao continuar={() => { ir({ destino: "crescer", aba: "evolucao" }); scrollTo(0, 0); }} />
      {meusPets && !desk && <MeusPets fechar={() => setMeusPets(false)} irRegistro={() => { setMeusPets(false); ir({ destino: "diario", aba: "registro" }); }} />}
      {boasVindas && <BoasVindas fechar={() => { setBoasVindas(false); ir({ destino: "pet", aba: "estado" }); if (semPetNoInicio) setComoJogar(true); }} />}
      {comoJogar && <ComoJogar fechar={() => { setComoJogar(false); abrirEscolhaBrasao(); }} />}
      {escolhendoBrasao && !boasVindas && !descartados && !avisoTR && <EscolherBrasao podeVoltar={!aindaSemPet} />}
      {descartados > 0 && !boasVindas && <AvisoPetsDescartados n={descartados} fechar={() => setDescartados(0)} />}
      {avisoTR && !boasVindas && !descartados && <AvisoCombateTR aviso={avisoTR} fechar={() => setAvisoTR(null)} />}
      {her && !desk && <Heranca pai2={her.pai2} fim={irPet} />}
      {importando && !desk && <ImportarPet fechar={fecharImportar} />}
      {conclusao && <Conclusao m={jogo.motor} fechar={() => setConclusao(false)} />}
    </div>
  );
}
