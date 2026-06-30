import { LayoutGroup } from 'framer-motion';
import { useAtlasStore } from './store';
import { useAtlasContext } from './useAtlasContext';
import { AtlasOrb } from './components/AtlasOrb';
import { AtlasWorkspace } from './components/AtlasWorkspace';
import { SimulationProxy } from './components/SimulationProxy';
import { NavigationProxy } from './components/NavigationProxy';

export function AtlasAI() {
  const { isOpen } = useAtlasStore();
  const context = useAtlasContext();

  return (
    <LayoutGroup>
      <SimulationProxy />
      <NavigationProxy />
      {/* Orb returns null when isOpen — Framer Motion morphs via shared layoutId */}
      <AtlasOrb />
      {isOpen && <AtlasWorkspace context={context} />}
    </LayoutGroup>
  );
}
