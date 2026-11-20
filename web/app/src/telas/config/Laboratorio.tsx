/* Ajustes > Laboratorio. O cerebro do pet (docs/TAREFA_V3_CEREBRO_PRIMARIO.md; src/cerebro.ts): o do pet ativo, que troca na hora, e o dos
   ovos novos (o modular por padrao), sempre visiveis, com a chave do laboratorio ligada ou nao. Depois, o laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, LM5b; pranchas docs/pranchas/lab/ajustes_*): o que e o laboratorio, a chave (desligada),
   o botao de chocar o ovo de teste (v16, so um por vez), e o pet de teste vivo com Abrir (LM5-7: mostra na tela Pet sem trocar o pet ativo) e
   Descartar (LM5-8: confirmacao sem digitar, foco em Cancelar; apaga so o save do pet de teste). Sem opcao de baixar o log (LM5-9). */
import { useEffect, useMemo, useRef, useState } from "react";
import "../../estilo/lab.css";
import { VERSAO_PET_LAB, nomeEstagio, nomeForma, type Motor } from "../../../motor/index.ts";
import { BotaoContinuar, BotaoHx } from "../../componentes/hx/index.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { abrirLab, sairDoLab, trocarCerebroDoPet, useJogo } from "../../jogo.ts";
import { CEREBRO_PADRAO, NOME_CEREBRO, escolherCerebroDosOvos, podeTrocarCerebro, useCerebroDosOvos, type Cerebro } from "../../cerebro.ts";
import { chocarOvoLab, descartarPetLab, falaComConteudo, labLigado, lerPetLab, ligarFalaComConteudo, ligarLab, useLab } from "../../lab.ts";
import { Retrato, diaDe } from "../pet/TelaPet.tsx";

export function SeloExperimental({ className = "" }: { className?: string }) {
  return <span className={"lab-selo " + className}><span aria-hidden="true">◆</span> experimental</span>;
}

function ConfirmarDescarte({ m, cancelar, confirmar }: { m: Motor; cancelar: () => void; confirmar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  const nome = nomeForma(m.forma);
  return (
    <dialog className="mc-dialogo lab-conf" ref={ref} role="alertdialog" aria-labelledby="lab-conf-tit" onClose={cancelar}>
      <section className="mc lab-conf__corpo">
        <h3 className="mc-bloco__tit" id="lab-conf-tit">Descartar o {nome} de teste?</h3>
        <ul className="lab-conf__lista">
          <li><b>O save do {nome} de teste é apagado</b><small>Do ovo ao dia {diaDe(m.e.tick)}. Não volta.</small></li>
          <li><b>Seus pets de hoje não são tocados</b><small>O pet de teste fica num espaço próprio do save.</small></li>
        </ul>
        <p className="mc-erro">Não dá para desfazer.</p>
        <div className="mc-linha">
          <BotaoHx data-autofocus onClick={() => ref.current?.close()}>Cancelar</BotaoHx>
          <BotaoHx tom="perigo" onClick={confirmar}>Descartar</BotaoHx>
        </div>
      </section>
    </dialog>
  );
}

const CEREBROS_TELA: readonly Cerebro[] = ["modular", "a"];
const rotulo = (c: Cerebro): string => NOME_CEREBRO[c] + (c === CEREBRO_PADRAO ? " (padrão)" : "");

/** o cerebro do pet ativo e o dos ovos novos */
function CerebroDoPet() {
  const { motor: m, emLab } = useJogo(), ovos = useCerebroDosOvos(), [erro, setErro] = useState("");
  const atual = m.cerebroAtual, troca = !emLab && podeTrocarCerebro(m);
  const trocar = (c: Cerebro) => { try { setErro(""); trocarCerebroDoPet(c); } catch (err) { setErro(err instanceof Error ? err.message : String(err)); } };
  return (
    <section className="mc-bloco" aria-labelledby="lab-cerebro">
      <h3 className="mc-bloco__tit" id="lab-cerebro">Cérebro</h3>
      <p>O <b>DigiBrain modular</b> é o cérebro primário dos pets. O <b>cérebro A</b> (a linha de base) continua selecionável.</p>
      {emLab ? <p className="mc-apoio">Este é o pet de teste. Para trocar o cérebro do seu pet, volte a ele.</p> : <>
        <fieldset className="lab-cerebro" aria-describedby="lab-cerebro-pet">
          <legend><b>Seu pet decide com</b></legend>
          {CEREBROS_TELA.map(c => (
            <label key={c}><input type="radio" name="cerebro-pet" value={c} checked={atual === c} disabled={!troca}
              onChange={() => trocar(c)} /> {NOME_CEREBRO[c]}</label>))}
        </fieldset>
        <p className="mc-apoio" id="lab-cerebro-pet">{troca
          ? "A troca vale na hora e fica no registro do pet. Cada cérebro guarda o que aprendeu e fica parado enquanto o outro decide."
          : `Este pet é da versão ${m.versao} e não troca de cérebro: ele segue com o cérebro A.`}</p>
      </>}
      <fieldset className="lab-cerebro">
        <legend><b>Ovos novos nascem com</b></legend>
        {CEREBROS_TELA.map(c => (
          <label key={c}><input type="radio" name="cerebro-ovos" value={c} checked={ovos === c} onChange={() => escolherCerebroDosOvos(c)} /> {rotulo(c)}</label>))}
      </fieldset>
      {erro && <p className="mc-erro" role="alert">{erro}</p>}
    </section>
  );
}

export function Laboratorio({ irPet }: { irPet: () => void }) {
  const rev = useLab(), { emLab, motor } = useJogo(), ligado = labLigado();
  const [erro, setErro] = useState(""), [descartando, setDescartando] = useState(false);
  const lido = useMemo(() => lerPetLab(), [rev]);
  const m = lido.tipo === "ok" ? (emLab ? motor : lido.motor) : null;
  const chocar = () => { try { setErro(""); chocarOvoLab(); } catch (err) { setErro(err instanceof Error ? err.message : String(err)); } };
  const abrir = () => { if (!m) return; abrirLab(m); irPet(); };
  const descartar = () => { sairDoLab(); descartarPetLab(); setDescartando(false); };
  return (
    <>
      <CerebroDoPet />
      <section className="mc-bloco" aria-labelledby="lab-que">
        <h3 className="mc-bloco__tit" id="lab-que">O que é o laboratório</h3>
        <p>Um pet de teste com o <b>DigiBrain modular</b>, num espaço próprio do save: cada decisão dele mostra qual módulo pesou. Ele não troca o cérebro dos seus pets.</p>
      </section>
      <label className="mc-interruptor"><span><b>Modo laboratório · {ligado ? "ligado" : "desligado"}</b><small>desligado, o jogo é o de hoje e nada do laboratório aparece</small></span>
        <input type="checkbox" role="switch" checked={ligado} onChange={e => ligarLab((e.target as HTMLInputElement).checked)} /></label>
      {ligado && (
        <section className="mc-bloco" aria-labelledby="lab-pet">
          <h3 className="mc-bloco__tit" id="lab-pet">Pet de teste</h3>
          {lido.tipo === "erro" && <p className="mc-erro" role="alert">{lido.erro}. Nada foi apagado.</p>}
          {lido.tipo === "vazio" && <>
            <p>Nenhum pet de teste ainda. O ovo de teste nasce com o cérebro modular, no espaço próprio do save.</p>
            <label className="mc-interruptor"><span><b>Fala com conteúdo (teste) · {falaComConteudo() ? "ligada" : "desligada"}</b><small>ligada, o ovo de teste nasce com o chamar dividido em pedir comida, limpeza ou companhia, e a fala pela rede diz o pedido</small></span>
              <input type="checkbox" role="switch" checked={falaComConteudo()} onChange={e => ligarFalaComConteudo((e.target as HTMLInputElement).checked)} /></label>
            <BotaoContinuar onClick={chocar}>Chocar o ovo de teste</BotaoContinuar>
          </>}
          {m && <>
            <div className="lab-pet">
              <span className="lab-pet__ret"><Retrato m={m} ovo={false} /></span>
              <span className="lab-pet__txt"><b>{nomeForma(m.forma)}</b><SeloExperimental />
                <small>{nomeEstagio(m.forma)} · dia {diaDe(m.e.tick)}</small><small>cérebro modular · versão {VERSAO_PET_LAB}{m.falaUnidades ? " · fala com conteúdo" : ""}</small></span>
            </div>
            <div className="mc-linha">
              <BotaoContinuar onClick={abrir}>Abrir</BotaoContinuar>
              <BotaoHx tom="perigo" onClick={() => setDescartando(true)}>Descartar</BotaoHx>
            </div>
            <p className="mc-apoio">Só um pet de teste por vez. Para chocar outro ovo de teste, descarte este antes. Abrir mostra o pet na tela do Pet, com o selo “experimental”.</p>
          </>}
          {erro && <p className="mc-erro" role="alert">{erro}</p>}
        </section>
      )}
      <section className="mc-bloco lab-aviso" aria-label="Aviso">
        <b>Experimental</b>
        <p>O pet de teste fica num espaço próprio do save, ao lado dos seus pets, e não troca o cérebro de nenhum deles.</p>
      </section>
      {descartando && m && <ConfirmarDescarte m={m} cancelar={() => setDescartando(false)} confirmar={descartar} />}
    </>
  );
}
