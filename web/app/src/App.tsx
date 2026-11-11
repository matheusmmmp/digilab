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
  DESTINOS, NOME_ABA, NOME_DESTINO, ROTA_INICIAL, configDoEndereco, enderecoDaConfig, enderecoDaRota, gravarAbaLembrada, lerAbaLembrada,
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
import { TelaMedalhas } from "./telas/lutar/TelaMedalhas.tsx";
import { TelaFronteira } from "./telas/lutar/TelaFronteira.tsx";
import { AvisoSom } from "./componentes/AvisoSom.tsx";
import { AvisoPetsDescartados } from "./componentes/Medalha.tsx";
import { AvisoCombateTR, avisoTRPendente } from "./componentes/AvisoCombateTR.tsx";
import { AvisoLutaPoc, avisoPocPendente } from "./componentes/AvisoLutaPoc.tsx";
import { TelaLutaPoc } from "./telas/lutar/palcoPoc/TelaLutaPoc.tsx";
import { TelaArenaPoc, TelaCampanhaPoc } from "./telas/lutar/palcoPoc/TelaLugaresPoc.tsx";
import { assistirPoc, fimDoPet, lutaMontadaDoEndereco, useLutaPoc } from "./lutaPocTela.ts";
import { CHAVE_AVISO_V6 } from "./tamer.ts";
import { TelaConversar } from "./telas/conversar/TelaConversar.tsx";
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
import { AnuncioNivel, CartaoMotivo } from "./componentes/CartaoNivel.tsx";
import { useSomDoJogo } from "./somJogo.ts";
import { CadeadosDaIlha } from "./componentes/CadeadosDaIlha.tsx";
import { ObjetosDaIlha } from "./componentes/ObjetosDaIlha.tsx";
import { marcarDiarioVisto } from "./telas/pet/objetosIlha.ts";
import { abrirMotivo, jaConhecoOJogo, useNivelRaiz } from "./nivelTela.ts";
import { PECAS, nivelDaPeca, pecaAberta, pecaDaAba, pecaDoDestino, type EstadoNivel, type Peca } from "./nivel.ts";

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
/** a peca trancada de um destino (o menu inteiro: Diario, Crescer, Lutar, Conversar) ou null se esta aberto ou nao tem trava (Pet) */
const destinoTrancado = (n: EstadoNivel, d: Destino): Peca | null => { const p = pecaDoDestino(d); return p && !pecaAberta(n, p) ? p : null; };
/** a aba trancada (Itens no Nv 5, Fronteira no Nv 8; docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.3): o "Nv N" na ponta e o marco que falta na dica. Abre a aba
    mesmo assim (o motor segue dono das regras); o corpo traz a linha do motivo */
const abaTrancada = (n: EstadoNivel, a: Aba): { nivel: string; dica: string } | undefined => {
  const p = pecaDaAba(a);
  return p && !pecaAberta(n, p) ? { nivel: `Nv ${nivelDaPeca(p)}`, dica: PECAS[p].motivo } : undefined;
};

/* slogan so na primeira visita (preferencia de tela, chave propria; a chave do save nao muda) */
function primeiraVisita(): boolean {
  try { if (localStorage.getItem(CHAVE + "-boas-vindas") !== "1") { localStorage.setItem(CHAVE + "-boas-vindas", "1"); return true; } } catch { /* sem armazenamento */ }
  return false;
}

function rotaInicial(): Rota {
  return rotaDoEndereco(location.hash) ?? (configDoEndereco(location.hash) ? { destino: "diario", aba: "registro" } : null) ?? lerAbaLembrada(armaz()) ?? ROTA_INICIAL;
}
/** a rota de abertura: a de um lugar trancado vira o Pet. Se veio do endereco (quem o digitou quer saber), o cartao do motivo abre; a aba lembrada de uma sessao
    antiga so volta ao Pet, em silencio */
function rotaDeAbertura(n: EstadoNivel): Rota {
  const r = rotaInicial(), p = destinoTrancado(n, r.destino);
  if (!p) return r;
  if (rotaDoEndereco(location.hash)) abrirMotivo(p);
  return ROTA_INICIAL;
}

export function App() {
  const jogo = useJogo(), atlas = useAtlas(), deco = useDecoracao(), nivel = useNivelRaiz();
  useSomDoJogo();   /* SOM-UP: os efeitos e a musica da ilha e do ovo */
  /* a luta da POC (LP3): o palco a tela inteira enquanto ha luta para mostrar; ?luta_poc=1&palco_poc=... monta uma luta direto no nucleo */
  const lutaPoc = useLutaPoc();
  useEffect(() => {
    const l = lutaMontadaDoEndereco(); if (!l) return;
    assistirPoc([l], "Luta montada · conferência", L => fimDoPet(L, l.A, l.B, "Luta montada no núcleo: nada foi gravado."));
  }, []);
  const nivelRef = useRef(nivel);
  nivelRef.current = nivel;
  const [rota, setRota] = useState<Rota>(() => rotaDeAbertura(nivel));
  const rotaRef = useRef(rota);
  rotaRef.current = rota;
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
  /* o descarte 7 (a luta da POC, LP2): so aparece com a chave ligada; entra como o avisoTR nas mesmas condicoes */
  const [avisoPoc, setAvisoPoc] = useState(avisoPocPendente);
  const [conclusao, setConclusao] = useState(false), desk = useDesktop(), lado = usePainelLado(), [comoJogar, setComoJogar] = useState(false), importando = useImportar(), her = useHeranca();
  /* a jornada acabou (pets v6: a Liga dos Lideres; v1-v5: o chefe da campanha): a mensagem de conclusao, uma vez por pet, fora da luta
     e sem outra tela cheia */
  useEffect(() => {
    if (!conclusao && !lutaPoc.palco && !boasVindas && !comoJogar && !escolhendoBrasao && !descartados && !avisoTR && !avisoPoc && concluiuJornada(jogo.motor) && !conclusaoVista(jogo.motor)) setConclusao(true);
  });
  const [ultima, setUltima] = useState<Partial<Record<Destino, Aba>>>(() => ({ [rota.destino]: rota.aba }));

  /* endereco e aba lembrada acompanham a rota; voltar/avancar do navegador muda a rota */
  useEffect(() => {
    if (boasVindas) return;                      /* primeira vez aberta: o endereco e #/inicio */
    const alvo = config ? enderecoDaConfig(config) : enderecoDaRota(rota);
    if (location.hash !== alvo) history.replaceState(null, "", alvo);
    gravarAbaLembrada(armaz(), rota);
    document.body.dataset.destino = rota.destino;
    document.title = `${config ? "Configurações" : NOME_DESTINO[rota.destino]} · Digilab Pet`;
  }, [rota, config, boasVindas]);
  /* o Diario aberto marca o que o dono ja viu (o ponto de "diario novo" na barraca, ObjetosDaIlha.tsx; I1-5): so a tela, fora do save */
  const diarioAberto = rota.destino === "diario" && !config, tickAgora = jogo.motor.e.tick, sementeAgora = jogo.motor.semente;
  useEffect(() => { if (diarioAberto) marcarDiarioVisto(sementeAgora, tickAgora); }, [diarioAberto, sementeAgora, tickAgora]);
  useEffect(() => {
    const aoMudar = () => {
      const c = configDoEndereco(location.hash); if (c) { setConfig(c); return; }
      const r = rotaDoEndereco(location.hash);
      if (r) {
        /* o endereco de um lugar trancado abre o cartao do motivo, nao o painel; o endereco volta ao da rota de agora */
        const p = destinoTrancado(nivelRef.current, r.destino);
        if (p) { abrirMotivo(p); history.replaceState(null, "", enderecoDaRota(rotaRef.current)); return; }
        setConfig(null); setMeusPets(false); fecharImportar(); fecharHeranca(); setRota(r);
      }
    };
    addEventListener("hashchange", aoMudar);
    return () => removeEventListener("hashchange", aoMudar);
  }, []);

  /* um menu trancado (a tecla, o trilho, a coluna, o minimapa, o endereco) abre o cartao do motivo no lugar do painel (docs/PLANO_V3_PROGRESSAO_TUTORIAL.md, 3.4) */
  const ir = (r: Rota) => {
    const p = destinoTrancado(nivel, r.destino);
    if (p) { abrirMotivo(p); return; }
    setConfig(null); setMeusPets(false); fecharImportar(); fecharHeranca(); setRota(r); setUltima(u => ({ ...u, [r.destino]: r.aba }));
  };
  const irDestino = (d: Destino) => { ir({ destino: d, aba: ultima[d] ?? DESTINOS[d][0] }); scrollTo(0, 0); };
  const abrirConfig = (p: ParteConfig) => { setMeusPets(false); setConfig(p); scrollTo(0, 0); };
  const abas = DESTINOS[rota.destino];
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
  /* a Arena e a Campanha no palco da luta da POC (LP3); a Fronteira usa a tela dela, com o palco novo por baixo */
  const corpoDestino = (): ReactNode => rota.aba === "treinar" ? <TelaTreinar /> : rota.aba === "aprend" ? <TelaAprend /> : rota.aba === "evolucao" ? <TelaEvolucao /> : rota.aba === "itens" ? <TelaItens />
    : rota.aba === "arena" ? <TelaArenaPoc />
    : rota.aba === "campanha" ? <TelaCampanhaPoc />
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
        abas: abas.map((a, i) => ({ id: a, rotulo: NOME_ABA[a], icone: ICONE_ABA[a], atalho: String(i + 1), ...(abaTrancada(nivel, a) ? { trancada: abaTrancada(nivel, a)! } : {}) })),
        aba: rota.aba, irAba: id => ir({ destino: rota.destino, aba: id as Aba }), fechar: fecharPainel, destino: rota.destino },
      corpo: <>{abaTrancada(nivel, rota.aba) && <p className="lg-trava"><Lock aria-hidden="true" />{abaTrancada(nivel, rota.aba)!.dica}</p>}{corpoDestino()}</>,
    };
  }
  else if (rota.destino !== "pet") painel = {
    d: { titulo: NOME_DESTINO[rota.destino], abas: abas.map(a => ({ id: a, rotulo: NOME_ABA[a], ...(abaTrancada(nivel, a) ? { trancada: abaTrancada(nivel, a)! } : {}) })), aba: rota.aba, irAba: id => ir({ destino: rota.destino, aba: id as Aba }), fechar: fecharPainel, idBase },
    corpo: <>{abaTrancada(nivel, rota.aba) && <p className="lg-trava"><Lock aria-hidden="true" />{abaTrancada(nivel, rota.aba)!.dica}</p>}{corpoDestino()}</>,
  };
  /* a viagem da camera: entrar no lugar leva a camera e o pet ao saco, ao portao ou a barraca (uma troca direta parte do lugar de antes); sair os traz de volta
     (so vista, viagem.ts). Os Ajustes nao viajam */
  const idLugar: Lugar | null = lugar && !lugar.d.semLugar ? LUGAR_DO_DESTINO[rota.destino]!.lugar : null;
  useEffect(() => { if (idLugar) { soltarTeclas(); entrarLugar(performance.now(), idLugar); } else sairLugar(); }, [idLugar]);
  /* os atalhos diretos (atalhosLugar.ts): C, 1 a 4 e Esc; valem so com a casca livre (sem luta, boas-vindas, aviso ou tela por cima) */
  const ref = useRef({ ativo: false, lugar: null as Lugar | null, aba: "" });
  ref.current = { ativo: !lutaPoc.palco && !boasVindas && !comoJogar && !escolhendoBrasao && !descartados && !avisoTR && !avisoPoc && !conclusao && !config && !meusPets && !importando && !her,
    lugar: idLugar, aba: rota.aba };
  useEffect(() => ligarAtalhosLugar({
    ativo: () => ref.current.ativo, lugarAberto: () => ref.current.lugar,
    /* o D e o "direita" do WASD da camera solta: so abre o Diario com um lugar aberto (a camera esta parada) ou com a camera que nao solta */
    liberaD: dAbreDiario,
    abrirLugar: l => acoes.current.abrir(l), irAba: i => acoes.current.aba(i), sair: () => acoes.current.sair(),
  }), []);
  /* o cartao de destrave so aparece com a tela Pet a vista: fora da luta, das boas-vindas e de qualquer outra tela cheia, do painel de um lugar e dos Ajustes */
  const cartaoLivre = ref.current.ativo && rota.destino === "pet" && jogo.nascendo === 0;
  const acoes = useRef({ abrir: (_l: Lugar) => {}, aba: (_i: number) => {}, sair: () => {} });
  acoes.current = {
    abrir: l => irDestino(l === "saco" ? "crescer" : l === "portao" ? "lutar" : "diario"),
    aba: i => { const d = rota.destino, a = DESTINOS[d][i]; if (idLugar && a) ir({ destino: d, aba: a }); }, sair: fecharPainel,
  };
  if (lutaPoc.palco) return (
    <div className="app app--tela-cheia">
      <TelaLutaPoc sair={() => scrollTo(0, 0)} />
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
      <DicaBit livre={cartaoLivre} ir={r => { ir(r); scrollTo(0, 0); }} />
      <CartaoMotivo />
      <AnuncioNivel />
      {/* o habitat (a cena do Pet) e a camada de fundo de toda rota: fica montado, nao sobe nem desce ao trocar de destino */}
      <Habitat escurecer={!!painel} irLugar={irDestino} />
      <TopoHabitat lugar={idLugar ? rota.destino : null} abrirMeusPets={abrirMeusPets} irConversar={() => irDestino("conversar")} irDestino={irDestino} abrirConfig={() => abrirConfig("principal")} />
      {!painel && (!lugar || lugar.d.semLugar) && <TelaPet irRegistro={() => ir({ destino: "diario", aba: "registro" })} irEvolucao={() => { ir({ destino: "crescer", aba: "evolucao" }); scrollTo(0, 0); }}
        abrirConfig={() => abrirConfig("principal")} abrirMeusPets={abrirMeusPets} />}
      {idLugar && lado && <MarcasDoLugar lugar={idLugar} />}
      {!idLugar && !painel && <CadeadosDaIlha abrir={l => acoes.current.abrir(l)} />}
      {!idLugar && !painel && <ObjetosDaIlha />}
      {lugar && (lado ? <LugarLado d={lugar.d}>{lugar.corpo}</LugarLado> : <LugarFolha d={lugar.d}>{lugar.corpo}</LugarFolha>)}
      {painel && (lado ? <PainelLado d={painel.d}>{painel.corpo}</PainelLado> : <PainelModal d={painel.d}>{painel.corpo}</PainelModal>)}
      {lado && nav}
      <RevelacaoEvolucao continuar={() => { ir({ destino: "crescer", aba: "evolucao" }); scrollTo(0, 0); }} />
      {meusPets && !desk && <MeusPets fechar={() => setMeusPets(false)} irRegistro={() => { setMeusPets(false); ir({ destino: "diario", aba: "registro" }); }} />}
      {boasVindas && <BoasVindas fechar={jaConheco => {
        setBoasVindas(false); ir({ destino: "pet", aba: "estado" });
        /* "Ja conheco o jogo" (P-7): abre os niveis 1 a 4, sem os cartoes, e pula o Como jogar */
        if (jaConheco) { jaConhecoOJogo(); if (semPetNoInicio) abrirEscolhaBrasao(); } else if (semPetNoInicio) setComoJogar(true);
      }} />}
      {comoJogar && <ComoJogar fechar={() => { setComoJogar(false); abrirEscolhaBrasao(); }} />}
      {escolhendoBrasao && !boasVindas && !descartados && !avisoTR && !avisoPoc && <EscolherBrasao podeVoltar={!aindaSemPet} />}
      {descartados > 0 && !boasVindas && <AvisoPetsDescartados n={descartados} fechar={() => setDescartados(0)} />}
      {avisoTR && !boasVindas && !descartados && <AvisoCombateTR aviso={avisoTR} fechar={() => setAvisoTR(null)} />}
      {avisoPoc && !avisoTR && !boasVindas && !descartados && <AvisoLutaPoc aviso={avisoPoc} fechar={() => setAvisoPoc(null)} />}
      {her && !desk && <Heranca pai2={her.pai2} fim={irPet} />}
      {importando && !desk && <ImportarPet fechar={fecharImportar} />}
      {conclusao && <Conclusao m={jogo.motor} fechar={() => setConclusao(false)} />}
    </div>
  );
}
