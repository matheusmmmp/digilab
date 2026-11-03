/* Ajustes > Laboratorio (docs/TAREFA_V3_LAB_MODULAR.md, LM5b; pranchas docs/pranchas/lab/ajustes_*): o que e o laboratorio, a chave (desligada),
   o botao de chocar o ovo de teste (v16, so um por vez), e o pet de teste vivo com Abrir (LM5-7: mostra na tela Pet sem trocar o pet ativo) e
   Descartar (LM5-8: confirmacao sem digitar, foco em Cancelar; apaga so o save do pet de teste). Sem opcao de baixar o log (LM5-9). */
import { useEffect, useMemo, useRef, useState } from "react";
import "../../estilo/lab.css";
import { VERSAO_PET_LAB, nomeEstagio, nomeForma, type Motor } from "../../../motor/index.ts";
import { BotaoContinuar, BotaoHx } from "../../componentes/hx/index.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { abrirLab, sairDoLab, useJogo } from "../../jogo.ts";
import { chocarOvoLab, descartarPetLab, labLigado, lerPetLab, ligarLab, useLab } from "../../lab.ts";
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
      <section className="mc-bloco" aria-labelledby="lab-que">
        <h3 className="mc-bloco__tit" id="lab-que">O que é o laboratório</h3>
        <p>Um pet de teste com o <b>DigiBrain modular</b>: cada decisão dele mostra qual módulo pesou. Os pets de hoje seguem com o cérebro A v11 e não mudam.</p>
      </section>
      <label className="mc-interruptor"><span><b>Modo laboratório · {ligado ? "ligado" : "desligado"}</b><small>desligado, o jogo é o de hoje e nada do laboratório aparece</small></span>
        <input type="checkbox" role="switch" checked={ligado} onChange={e => ligarLab((e.target as HTMLInputElement).checked)} /></label>
      {ligado && (
        <section className="mc-bloco" aria-labelledby="lab-pet">
          <h3 className="mc-bloco__tit" id="lab-pet">Pet de teste</h3>
          {lido.tipo === "erro" && <p className="mc-erro" role="alert">{lido.erro}. Nada foi apagado.</p>}
          {lido.tipo === "vazio" && <>
            <p>Nenhum pet de teste ainda. O ovo de teste nasce com o cérebro modular, no espaço próprio do save.</p>
            <BotaoContinuar onClick={chocar}>Chocar o ovo de teste</BotaoContinuar>
          </>}
          {m && <>
            <div className="lab-pet">
              <span className="lab-pet__ret"><Retrato m={m} ovo={false} /></span>
              <span className="lab-pet__txt"><b>{nomeForma(m.forma)}</b><SeloExperimental />
                <small>{nomeEstagio(m.forma)} · dia {diaDe(m.e.tick)}</small><small>cérebro modular · versão {VERSAO_PET_LAB}</small></span>
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
