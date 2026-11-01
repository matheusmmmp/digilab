/* O mapa e a camera do habitat em Ajustes > Aparencia (src/habitat.ts), no molde da escolha da pele (EscolhaPele.tsx): cartoes num
   radiogroup do WAI-ARIA (setas, Home e End movem e escolhem; so o escolhido entra na ordem de Tab). A troca vale na hora, com o jogo
   rodando: a cena 3D religa no mapa novo e o pet continua onde o motor diz. So vista, fora do save, do registro e do replay. Os pets sem
   o mundo fisico (v1-v11) ficam na sala: a escolha fica guardada, mas desligada. */
import { useRef, type KeyboardEvent } from "react";
import { indiceAbaPorTecla } from "../../componentes/hx/index.ts";
import {
  MAPAS_DEV, NOME_CAMERA, NOME_MAPA, escolherCamera, escolherMapa, habitatEscolhido, mapaCaido, mapasDisponiveis, useHabitat, type Camera, type Mapa,
} from "../../habitat.ts";

const DESCRICAO: Record<Mapa, string> = {
  ilha: "o estilo Animal Crossing, com o mundo curvo",
  voxel: "a mesma ilha em cubos, feita por código",
  floresta: "o kit Tiny Fantasy Forest",
  cassette: "as texturas e as árvores do Cassette Beasts",
};
const DESCRICAO_CAMERA: Record<Camera, string> = { atras: "de cima, atrás do pet", lateral: "de lado, quase sem perspectiva" };
const CAMERAS: readonly Camera[] = ["atras", "lateral"];

/** um grupo de cartoes de escolha unica */
function Grupo<T extends string>({ id, titulo, opcoes, atual, nome, descricao, escolher, desligado }: {
  id: string; titulo: string; opcoes: readonly T[]; atual: T; nome: Record<T, string>; descricao: (o: T) => string; escolher: (o: T) => void; desligado: boolean;
}) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  function aoTecla(e: KeyboardEvent<HTMLButtonElement>, i: number) {
    const alvo = indiceAbaPorTecla(e.key, i, opcoes.length);
    if (alvo === null) return;
    e.preventDefault();
    escolher(opcoes[alvo]);
    refs.current[alvo]?.focus();
  }
  return (
    <>
      <h3 className="mc-sec" id={id}>{titulo}</h3>
      <div className="mc-opcoes mc-opcoes--2" role="radiogroup" aria-labelledby={id} aria-disabled={desligado || undefined}>
        {opcoes.map((o, i) => (
          <button type="button" key={o} ref={el => { refs.current[i] = el; }} role="radio" aria-checked={atual === o} tabIndex={atual === o ? 0 : -1}
            disabled={desligado} className="mc-opcao" onClick={() => escolher(o)} onKeyDown={e => aoTecla(e, i)}>
            <b>{nome[o]}</b><small>{descricao(o)}</small>
          </button>
        ))}
      </div>
    </>
  );
}

export function EscolhaHabitat({ temMundo }: { temMundo: boolean }) {
  useHabitat();
  const { mapa, camera } = habitatEscolhido(), caido = mapaCaido(), mapas = mapasDisponiveis();
  const descMapa = (m: Mapa) => DESCRICAO[m] + (MAPAS_DEV.includes(m) ? " (só no modo dev)" : "");
  return (
    <>
      <Grupo id="cfg-mapa" titulo="Mapa do habitat" opcoes={mapas} atual={mapa} nome={NOME_MAPA} descricao={descMapa} escolher={escolherMapa} desligado={!temMundo} />
      <Grupo id="cfg-camera" titulo="Câmera do habitat" opcoes={CAMERAS} atual={camera} nome={NOME_CAMERA} descricao={c => DESCRICAO_CAMERA[c]} escolher={escolherCamera} desligado={!temMundo} />
      {caido && <p className="mc-apoio" role="status">O mapa {NOME_MAPA[caido]} não carregou nesta máquina (faltam os arquivos em Assets/kits3d); o habitat voltou para a Ilha.</p>}
      <p className="mc-apoio">{temMundo
        ? "Troca na hora, com o jogo rodando: é só a vista. O pet anda onde o motor manda em qualquer mapa; o registro e o replay não mudam."
        : "Este pet é de antes do mundo físico e fica na sala; o mapa e a câmera valem para os pets com mundo."}</p>
    </>
  );
}
