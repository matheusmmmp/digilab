/* Esqueleto do app (TAREFA_FRONT_TS, Etapa 3): cabecalho do pet, painel do destino com sub-abas, barra dos
   4 destinos e rodape. A rota vem do endereco (#/destino/aba) ou da aba lembrada, como no HTML. */
import { useEffect, useRef, useState } from "preact/hooks";
import { useAtlas } from "./atlas.ts";
import { useDecoracao } from "./decoracao.ts";
import { Nav } from "./componentes/Nav.tsx";
import { BoasVindas } from "./componentes/BoasVindas.tsx";
import { RevelacaoEvolucao } from "./componentes/Revelacao.tsx";
import { nomeForma } from "../motor/index.ts";
import { useJogo } from "./jogo.ts";
import {
  DESTINOS, NOME_ABA, NOME_DESTINO, ROTA_INICIAL, ENDERECO_LUTA, configDoEndereco, ehLuta, enderecoDaConfig, enderecoDaRota, gravarAbaLembrada, lerAbaLembrada,
  rotaDoEndereco, type Aba, type Destino, type ParteConfig, type Rota,
} from "./rotas.ts";
import { Deco } from "./componentes/Deco.tsx";
import { TelaConfig } from "./telas/config/TelaConfig.tsx";
import { TelaCatalogo } from "./telas/diario/TelaCatalogo.tsx";
import { TelaCenarios } from "./telas/diario/TelaCenarios.tsx";
import { TelaRegistro } from "./telas/diario/TelaRegistro.tsx";
import { TelaAprend } from "./telas/crescer/TelaAprend.tsx";
import { TelaEvolucao } from "./telas/crescer/TelaEvolucao.tsx";
import { TelaTreinar } from "./telas/crescer/TelaTreinar.tsx";
import { TelaArena } from "./telas/lutar/TelaArena.tsx";
import { TelaCampanha } from "./telas/lutar/TelaCampanha.tsx";
import { TelaConversar } from "./telas/conversar/TelaConversar.tsx";
import { TelaLuta } from "./telas/lutar/TelaLuta.tsx";
import { LUTA, REPLAY, previa, pularAnimacao, type Modo } from "./luta.ts";
import { TelaPet } from "./telas/pet/TelaPet.tsx";
import { MeusPets } from "./telas/pet/MeusPets.tsx";
import { TopoDesktop } from "./componentes/Topo.tsx";
import { DicaBit } from "./componentes/Bit.tsx";
import { AcoesMeusPets, MeusPetsDesktop } from "./telas/pet/MeusPetsDesktop.tsx";
import { useDesktop } from "./desktop.ts";
import { ComoJogar, Conclusao, EscolherBrasao } from "./componentes/Jornada.tsx";
import { ImportarPet } from "./componentes/Importar.tsx";
import { fecharImportar, useImportar } from "./importar.ts";
import { Heranca } from "./componentes/Heranca.tsx";
import { TelaGeracoes } from "./telas/diario/TelaGeracoes.tsx";
import { fecharHeranca, useHeranca } from "./heranca.ts";
import { abrirEscolhaBrasao, conclusaoVista, useEscolhaBrasao, venceuOChefe } from "./jornada.ts";
import { dicasDoMomento, type IdDica } from "./dicas.ts";
import { CHAVE } from "./save.ts";

const armaz = (): Storage => localStorage;

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
    if (est === "crianca") ids.push("rookie", "ensinar");
    if (est === "adolescente") ids.push("champion", "lutas_treino");
    if (est === "adulto") ids.push(mDica.versao >= 5 && !mDica.forma.mega && !mDica.sombria ? "ultimate" : "adulto");
    if (mDica.versao >= 4) {
      const j = mDica.janelaAberta();
      if (j?.tipo === "chamado") ids.push("manha");
      if (j?.tipo === "aviso") ids.push("banheiro");
      if (mDica.lesionadoDesde !== null) ids.push("lesao");
      if (est === "adolescente") ids.push("vitorias");
    }
    dicasDoMomento(ids);
  });
  const [boasVindas, setBoasVindas] = useState(() => primeiraVisita() || location.hash === "#/inicio"), [meusPets, setMeusPets] = useState(false);
  /* jornada: sem pet proprio no comeco (so o de exemplo), o Comecar das boas-vindas leva a escolha do brasao */
  const [semPetNoInicio] = useState(() => jogo.origem === "exemplo"), escolhendoBrasao = useEscolhaBrasao();
  /* o pet de exemplo nao e do jogador: enquanto for ele o ativo, a escolha do brasao nao tem Voltar */
  const [sementeExemplo] = useState(() => jogo.motor.semente), aindaSemPet = semPetNoInicio && jogo.motor.semente === sementeExemplo;
  const [conclusao, setConclusao] = useState(false), desk = useDesktop(), [comoJogar, setComoJogar] = useState(false), importando = useImportar(), her = useHeranca();
  /* venceu o chefe da campanha: a mensagem de conclusao, uma vez por pet, fora da luta e sem outra tela cheia */
  useEffect(() => {
    if (!conclusao && !emLuta && !boasVindas && !comoJogar && !escolhendoBrasao && venceuOChefe(jogo.motor) && !conclusaoVista(jogo.motor)) setConclusao(true);
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
    setTimeout(() => document.querySelector<HTMLElement>(modo === "arena" ? ".lutar-grande" : ".camp-lutar")?.focus(), 60);
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
  /* desktop (>= 1100 px): topo da casca com titulo, abas e o mini-card do pet */
  const topo = <TopoDesktop titulo={config ? "Configurações" : NOME_DESTINO[rota.destino]} abas={config ? [] : abas} aba={rota.aba} irAba={a => ir({ destino: rota.destino, aba: a })}
    abrirMeusPets={() => setMeusPets(true)} voltar={!config && rota.destino === "conversar" ? () => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); } : undefined} />;
  if (emLuta) return (
    <div class="app app--tela-cheia">
      <TelaLuta sair={sairDaLuta} verReplay={verReplay} sairReplay={sairReplay} pedidoDesistir={pedidoDesistir} fecharPedido={() => setPedidoDesistir(false)} />
    </div>
  );

  return (
    <div class="app">
      {jogo.erroSave && (
        <div class="aviso" role="alert">
          O save deste navegador não abriu, e o app não vai gravar por cima dele.
          <p>{jogo.erroSave.erro}. Mostrando o pet de exemplo.</p>
        </div>
      )}
      {atlas.tipo === "erro" && (
        <div class="aviso" role="alert">
          Atlas de sprites não carregou.
          <p>{atlas.erro}. Rode <code>python gerar_atlas_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      {(deco.estado.tipo === "erro" || deco.falhas.size > 0) && (
        <div class="aviso" role="alert">
          Parte da decoração do Digimon UP não carregou; esses lugares ficam com o visual de antes.
          <p>{deco.estado.tipo === "erro" ? deco.estado.erro : [...deco.falhas].map(([n, e]) => `${n} (${e})`).join(", ")}.
            Rode <code>python gerar_decoracao_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      <DicaBit />
      {importando && desk ? <><TopoDesktop titulo="Importar pet" abas={[]} aba={null} irAba={() => {}} abrirMeusPets={() => { fecharImportar(); setMeusPets(true); }}
          voltar={fecharImportar} /><ImportarPet pagina fechar={fecharImportar} /></>
      : her && desk ? <><TopoDesktop titulo="Nova geração" abas={[]} aba={null} irAba={() => {}} abrirMeusPets={() => { fecharHeranca(); setMeusPets(true); }}
          voltar={fecharHeranca} /><Heranca pagina pai2={her.pai2} fim={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} /></>
      : meusPets && desk ? <><TopoDesktop titulo="Meus pets" abas={[]} aba={null} irAba={() => {}} abrirMeusPets={() => {}} voltar={() => setMeusPets(false)}
          acoes={<AcoesMeusPets />} /><MeusPetsDesktop fechar={() => setMeusPets(false)} /></>
      : config ? <>{topo}<TelaConfig parte={config} abrir={abrirConfig} fechar={() => { setConfig(null); scrollTo(0, 0); }} irPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} /></>
      : rota.destino === "pet" ? <>{topo}<TelaPet abrirMeusPets={() => setMeusPets(true)} irConversar={() => irDestino("conversar")} abrirConfig={() => abrirConfig("principal")} irRegistro={() => ir({ destino: "diario", aba: "registro" })} /></>
      : rota.destino === "conversar" ? <>{topo}<TelaConversar voltar={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} /></> : (<>{topo}
      <section class="painel" aria-labelledby="tela-titulo">
        <div class="tela-cab dl-faixa">
          <Deco nome="TopDeco_Earth2_0" class="cab-globo" />
          <h1 class="dl-num" id="tela-titulo">{NOME_DESTINO[rota.destino]}</h1>
          <span class="tela-cab-pet">{jogo.nascendo > 0 ? "Digi-Egg" : nomeForma(jogo.motor.forma)}</span>
          {rota.destino === "diario" && (
            <button type="button" class="cab-engrenagem" aria-label="Configurações" onClick={() => abrirConfig("principal")}>
              <Deco nome="Common_Icon_Setting" /><span class="cab-engrenagem-reserva" aria-hidden="true">⚙</span>
            </button>
          )}
        </div>
        {abas.length > 1 && (
          <div class="tabs" role="tablist" aria-label={`Abas de ${NOME_DESTINO[rota.destino]}`}>
            {abas.map(a => (
              <button type="button" role="tab" key={a} class="tab" aria-selected={a === rota.aba} onClick={() => ir({ destino: rota.destino, aba: a })}>{NOME_ABA[a]}</button>
            ))}
          </div>
        )}
        <div role={abas.length > 1 ? "tabpanel" : undefined}>
          {rota.aba === "treinar" ? <TelaTreinar /> : rota.aba === "aprend" ? <TelaAprend /> : rota.aba === "evolucao" ? <TelaEvolucao />
            : rota.aba === "arena" ? <TelaArena voltarPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} verReplay={abrirReplay} />
            : rota.aba === "campanha" ? <TelaCampanha voltarPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} irTreinar={() => { ir({ destino: "crescer", aba: "treinar" }); scrollTo(0, 0); }} />
            : rota.aba === "registro" ? <TelaRegistro irPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} />
            : rota.aba === "catalogo" ? <TelaCatalogo /> : rota.aba === "geracoes" ? <TelaGeracoes /> : <TelaCenarios />}
        </div>
      </section></>)}
      <Nav atual={config ? null : rota.destino} ir={irDestino} configAberta={!!config} abrirConfig={() => abrirConfig("principal")} />
      <RevelacaoEvolucao continuar={() => { ir({ destino: "crescer", aba: "evolucao" }); scrollTo(0, 0); }} />
      {meusPets && !desk && <MeusPets fechar={() => setMeusPets(false)} irRegistro={() => { setMeusPets(false); ir({ destino: "diario", aba: "registro" }); }} />}
      {boasVindas && <BoasVindas fechar={() => { setBoasVindas(false); ir({ destino: "pet", aba: "estado" }); if (semPetNoInicio) setComoJogar(true); }} />}
      {comoJogar && <ComoJogar fechar={() => { setComoJogar(false); abrirEscolhaBrasao(); }} />}
      {escolhendoBrasao && !boasVindas && <EscolherBrasao podeVoltar={!aindaSemPet} />}
      {her && !desk && <Heranca pai2={her.pai2} fim={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} />}
      {importando && !desk && <ImportarPet fechar={fecharImportar} />}
      {conclusao && <Conclusao m={jogo.motor} fechar={() => setConclusao(false)} />}
    </div>
  );
}
