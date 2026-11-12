/* A página de entrada do DigiLab (POC). A prancha aprovada é a página A (docs/pranchas/ux-pagina-inicial/, PR #891; PI-1 decidida
   pelo Matheus em 2026-11-12: "A, a clara"). Os textos são os da prancha, e a origem de cada afirmação está no cabeçalho do gerar.py dela.
   O que a POC acrescenta à prancha está em docs/pranchas/ux-pagina-inicial/POC.md.

   DECISÕES ABERTAS, aqui no padrão (PROPOSTO):
   - PI-2, a frase: "Crie um Digimon que decide sozinho";
   - PI-3, onde a página mora: na raiz do site, com o jogo num caminho próprio (JOGO, abaixo); nenhuma rota do app muda;
   - PI-4, a passagem do claro para o jogo escuro: a cortina (Cortina, abaixo).
   A página não diz "sem anúncios": a CN-12 prevê o vídeo pedido pelo jogador para a voz. */
import { useEffect, useRef, useState, type MouseEvent, type ReactNode } from "react";
import { Check, Play, User } from "lucide-react";
import { Pet, useReduzido, type Forma } from "./pet.tsx";

/** o endereço do jogo, com a página na raiz do site (PI-3, PROPOSTO). A conta ainda não existe no jogo (vem com a CN2): "Entrar" leva
    ao jogo também, até lá (PROPOSTO). */
export const JOGO = "/jogo/#/pet";
const JOGO_ENTRAR = JOGO;
/** o tempo da cortina até a navegação (PROPOSTO, SEM FONTE) */
const MS_CORTINA = 420;

const LINHA: [Forma, string][] = [
  ["Koromon", "In-Training"], ["Agumon", "Rookie"], ["Greymon", "Champion"], ["MetalGreymon", "Ultimate"], ["WarGreymon", "Mega"],
];
const GARANTIAS = ["No navegador", "Sem conta", "Sem instalar"];
/* EXEMPLO DE LAYOUT, NUNCA DADO (como na prancha): a ficha diz "exemplo" na tela */
const OPCOES: [string, number][] = [["explorar", 48], ["comer", 31], ["dormir", 21]];

function Garantias() {
  return (
    <ul className="garantias" aria-label="Para começar">
      {GARANTIAS.map(t => <li key={t}><Check className="ic" aria-hidden="true" />{t}</li>)}
    </ul>
  );
}

function Marca({ n, rotulo, titulo, id }: { n?: string; rotulo: string; titulo: string; id: string }) {
  return (
    <div className="marca-sec">
      {n && <span className="num" aria-hidden="true">{n}</span>}
      <span className="lcd">{rotulo}</span>
      <h2 id={id}>{titulo}</h2>
    </div>
  );
}

/** um bloco que entra ao rolar (uma vez); sem JS ou com movimento reduzido, já está no lugar */
function Entra({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`entra ${className}`} data-entra="">{children}</div>;
}

const TRILHAS = (
  <svg className="trilhas" viewBox="0 0 1080 560" aria-hidden="true">
    <path d="M470 60V0M540 26V0M610 60V20l40-20M410 110V40L360 0M670 110V70l60-40V0" />
    <path d="M470 500v60M540 534v26M610 500v40l-40 20M410 450v70l50 40M670 450v50l70 40v20" />
    <path d="M300 280H170l-40-40H0M780 280h130l40 40h130M335 200l-60-40H190M745 360l60 40h85" />
    <circle className="no" cx="470" cy="60" r="5" /><circle className="no" cx="610" cy="60" r="5" /><circle className="no" cx="540" cy="26" r="5" />
    <circle className="no" cx="470" cy="500" r="5" /><circle className="no" cx="610" cy="500" r="5" /><circle className="no" cx="540" cy="534" r="5" />
    <circle className="cheio" cx="410" cy="110" r="4" /><circle className="cheio" cx="670" cy="110" r="4" />
    <circle className="cheio" cx="410" cy="450" r="4" /><circle className="cheio" cx="670" cy="450" r="4" />
    <circle className="cheio" cx="300" cy="280" r="4" /><circle className="cheio" cx="780" cy="280" r="4" />
    <circle className="no" cx="190" cy="160" r="5" /><circle className="no" cx="890" cy="400" r="5" />
    <g className="cheio">
      <rect x="500" y="6" width="14" height="3" /><rect x="500" y="12" width="14" height="3" /><rect x="500" y="18" width="14" height="3" />
      <rect x="566" y="538" width="14" height="3" /><rect x="566" y="544" width="14" height="3" /><rect x="566" y="550" width="14" height="3" />
      <path d="M636 34l5 8h-10zM636 22l5 8h-10zM444 524l5 8h-10zM444 536l5 8h-10zM60 232l8 5-8 5zM1010 312l8 5-8 5z" />
    </g>
  </svg>
);

/** a passagem para o jogo (PI-4, PROPOSTO): uma cortina azul-marinho sobe com a borda em degrau, o Agumon no meio, e a página navega.
    Com movimento reduzido não há cortina (o link segue direto); sem JS, o link funciona do mesmo jeito. */
function Cortina({ aberta }: { aberta: boolean }) {
  return (
    <div className={aberta ? "cortina aberta" : "cortina"} aria-hidden={!aberta}>
      {aberta && (
        <div className="cortina-miolo">
          <Pet forma="Agumon" k={3} decorativo />
          <p className="lcd" role="status">Abrindo a ilha</p>
        </div>
      )}
    </div>
  );
}

export function Home() {
  const reduzido = useReduzido();
  const [cortina, setCortina] = useState(false);
  const ctaHeroi = useRef<HTMLDivElement>(null);
  const ctaFim = useRef<HTMLDivElement>(null);
  const [mostrarFixo, setMostrarFixo] = useState(false);

  /* as seções entram ao rolar, uma vez (180 ms, ease-out; guia, seção 11); a classe "mov" só entra com JS e sem movimento reduzido */
  useEffect(() => {
    const raiz = document.documentElement;
    if (reduzido) { raiz.classList.remove("mov"); return; }
    raiz.classList.add("mov");
    const io = new IntersectionObserver(es => {
      for (const e of es) if (e.isIntersecting) { e.target.classList.add("visto"); io.unobserve(e.target); }
    }, { rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll("[data-entra]:not(.visto)").forEach(el => io.observe(el));
    return () => io.disconnect();
  }, [reduzido]);

  /* a barra fixa do celular: só quando nenhum dos dois botões grandes está na tela */
  useEffect(() => {
    const vis = new Map<Element, boolean>();
    const io = new IntersectionObserver(es => {
      for (const e of es) vis.set(e.target, e.isIntersecting);
      setMostrarFixo(![...vis.values()].some(Boolean));
    });
    for (const r of [ctaHeroi.current, ctaFim.current]) if (r) { vis.set(r, true); io.observe(r); }
    return () => io.disconnect();
  }, []);

  /* voltar pelo histórico (bfcache) não deixa a cortina fechada */
  useEffect(() => {
    const f = (e: PageTransitionEvent) => { if (e.persisted) setCortina(false); };
    window.addEventListener("pageshow", f);
    return () => window.removeEventListener("pageshow", f);
  }, []);

  function irAoJogo(e: MouseEvent<HTMLAnchorElement>) {
    if (reduzido || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    const destino = e.currentTarget.href;
    setCortina(true);
    window.setTimeout(() => window.location.assign(destino), MS_CORTINA);
  }

  const jogar = (cls: string) => (
    <a className={`bt jogar ${cls}`} href={JOGO} onClick={irAoJogo}><Play className="ic" aria-hidden="true" />Começar agora</a>
  );

  return (
    <div className="pi">
      <a className="pular" href="#conteudo">Pular para o conteúdo</a>

      <header className="barra">
        <a className="marca" href="#topo" aria-label="DigiLab, início da página"><i aria-hidden="true" />DIGILAB</a>
        <nav aria-label="Nesta página">
          <a href="#lab">O laboratório</a><a href="#dia">Primeiro dia</a><a href="#jogo">O jogo</a>
        </nav>
        <a className="bt" href={JOGO_ENTRAR}><User className="ic" aria-hidden="true" />Entrar</a>
        <a className="bt acao" href={JOGO} onClick={irAoJogo}><Play className="ic" aria-hidden="true" />Jogar</a>
      </header>

      <main id="conteudo" tabIndex={-1}>
        <section className="heroi" id="topo" aria-labelledby="h1">
          <picture className="heroi-foto">
            <img src="./img/ilha_1920.webp" srcSet="./img/ilha_800.webp 800w, ./img/ilha_1280.webp 1280w, ./img/ilha_1920.webp 1920w"
              sizes="(max-width: 899px) 1600px, 100vw" alt="" fetchPriority="high" />
          </picture>
          <div className="heroi-txt">
            <span className="lcd olho">Laboratório de pets com IA</span>
            <h1 id="h1">Crie um Digimon<em>que decide sozinho</em></h1>
            <p className="sub">Você cuida, ensina e treina. Ele escolhe o que fazer, e o jogo mostra o porquê.</p>
            <div className="cta" ref={ctaHeroi}>
              {jogar("claro")}
              <Garantias />
              <a className="ja" href={JOGO_ENTRAR}>Já tenho conta: entrar</a>
            </div>
          </div>
          <div className="linha">
            <ul className="fila" aria-label="A linha do Agumon, do In-Training ao Mega">
              {LINHA.map(([f, nv]) => (
                <li key={f}>
                  <Pet forma={f} k={1} kLargo={2} vira decorativo />
                  <span className="lcd"><b>{f}</b><span className="nv"> · {nv}</span></span>
                </li>
              ))}
            </ul>
            <span className="regua" aria-hidden="true" />
          </div>
        </section>

        <section className="sec" id="lab" aria-labelledby="t1">
          <Entra><Marca n="01" rotulo="Laboratório aberto" titulo="Um cérebro que você pode ver" id="t1" /></Entra>
          <Entra className="duas">
            <p>Cada pet nasce com uma rede própria. Ela muda com o que ele vive: a comida que achou, o elogio, a bronca.</p>
            <p>Abra o DigiBrain a qualquer hora e veja a escolha de agora e a chance de cada opção. Nada ali é texto inventado.</p>
          </Entra>
          <Entra className="especime">
            {TRILHAS}
            <div className="anel">
              <i className="miolo" aria-hidden="true" /><span className="sombra" aria-hidden="true" />
              <Pet forma="Agumon" k={3} kLargo={4} />
            </div>
            <div className="ficha f1"><span className="lcd">Espécime</span><b>Agumon</b><span className="lcd">Rookie · Coragem</span></div>
            <figure className="ficha f2">
              <img src="./img/scan_420.webp" width={420} height={377} loading="lazy"
                alt="O DigiBrain aberto no jogo: a rede do pet e a escolha de agora" />
              <figcaption className="lcd">O DigiBrain, no jogo</figcaption>
            </figure>
            <div className="ficha f3">
              <span className="lcd cab">Escolha de agora <span className="exemplo">exemplo</span></span>
              {OPCOES.map(([o, p]) => (
                <span className="barra-op" key={o}>
                  <span>{o}</span>
                  <i role="img" aria-label={`${o}: ${p} de 100`}><b style={{ width: `${p}%` }} /></i>
                  <span aria-hidden="true">{p} %</span>
                </span>
              ))}
              <span className="etq-apr">aprendido com você</span>
            </div>
          </Entra>
        </section>

        <figure className="panorama">
          <img src="./img/treino_1440.webp" srcSet="./img/treino_800.webp 800w, ./img/treino_1440.webp 1440w" sizes="100vw" loading="lazy"
            alt="O jogo: a ilha, um Gomamon ao lado do saco de pancada e o menu de treino" />
          <figcaption className="lcd">Captura do jogo · a ilha e o treino</figcaption>
        </figure>

        <section className="sec" id="dia" aria-labelledby="t2">
          <div className="lado-a-lado">
            <Entra>
              <Marca n="02" rotulo="Primeiro dia" titulo="Do ovo ao primeiro cuidado" id="t2" />
              <p>Você escolhe um brasão e recebe um ovo. Ele choca num In-Training, que cresce com o que vive. Como ele vai evoluir depende de como foi criado.</p>
              <ul className="chips" aria-label="Os brasões">
                {["Coragem", "Amizade", "Conhecimento", "Sinceridade"].map(b => <li className="chip" key={b}>{b}</li>)}
              </ul>
            </Entra>
            <Entra className="agenda">
              <div className="agenda-cab"><span className="lcd">Em um minuto</span><span className="lcd">3 passos</span></div>
              <ol>
                <li><span className="n" aria-hidden="true">1</span><span><b>Escolha um brasão</b><small>Ele define o ovo.</small></span></li>
                <li><span className="n" aria-hidden="true">2</span><span><b>O ovo choca</b><small>Nasce um In-Training.</small></span>
                  <Pet forma="Koromon" k={1} decorativo /></li>
                <li><span className="n" aria-hidden="true">3</span><span><b>Cuide e ensine</b><small>Comida, brincadeira, elogio.</small></span></li>
              </ol>
            </Entra>
          </div>
        </section>

        <section className="azul" id="jogo" aria-labelledby="t3">
          <Entra><Marca n="03" rotulo="O jogo" titulo="O ovo está esperando" id="t3" /></Entra>
          <Entra>
            <ul className="tres">
              <li><span className="palco"><Pet forma="Tanemon" k={2} decorativo /></span><h3>Cuidar</h3>
                <p>Alimentar, brincar, limpar e dar carinho. Ele sente e responde.</p></li>
              <li><span className="palco"><Pet forma="Agumon" k={2} decorativo /></span><h3>Treinar</h3>
                <p>Seis exercícios no saco de pancada. O treino muda os golpes.</p></li>
              <li><span className="palco"><Pet forma="Greymon" k={2} decorativo /></span><h3>Lutar</h3>
                <p>Ele luta sozinho na arena. Seis medalhas até a Liga.</p></li>
            </ul>
          </Entra>
          <div className="fecho" ref={ctaFim}>{jogar("claro")}<Garantias /></div>
        </section>

        <section className="sec sec-nao" aria-labelledby="t4">
          <Entra><Marca rotulo="Sem pegadinha" titulo="O que o jogo não faz" id="t4" /></Entra>
          <Entra>
            <ul className="nao">
              <li><b>Sem gacha</b><span>Nada de caixa de prêmio nem sorteio pago.</span></li>
              <li><b>Sem vantagem à venda</b><span>Os Bits só se ganham jogando.</span></li>
              <li><b>Sem culpa</b><span>Nenhuma contagem nem aviso insistente.</span></li>
              <li><b>Conta opcional</b><span>Entrar é escolha, e você pode apagar tudo.</span></li>
            </ul>
          </Entra>
        </section>
      </main>

      <footer className="rodape">
        <nav aria-label="Rodapé"><a href="#termos">Termos</a><a href="#privacidade">Privacidade</a><a href="#creditos">Créditos</a></nav>
        <span>Sprites, ícones e fundos: Digimon UP (Bandai). DigiLab é um projeto pessoal.</span>
      </footer>

      <div className={mostrarFixo ? "fixo mostra" : "fixo"}>{jogar("acao")}</div>
      <Cortina aberta={cortina} />
    </div>
  );
}
