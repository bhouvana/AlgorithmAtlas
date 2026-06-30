import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAtlasStore } from '../store';
import { useAtlasContext } from '../useAtlasContext';
import { AtlasWorkspace } from '../components/AtlasWorkspace';
import { SimulationProxy } from '../components/SimulationProxy';

export function AtlasPage() {
  const { open, isOpen, setMode } = useAtlasStore();
  const context = useAtlasContext();

  useEffect(() => {
    setMode('workspace');
    open('workspace');
  }, []);

  return (
    <div className="min-h-screen bg-[#07071000] flex flex-col" style={{ background: '#060611' }}>
      <SimulationProxy />
      {!isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center h-screen"
        >
          <div className="text-center">
            <div
              className="w-16 h-16 rounded-3xl flex items-center justify-center mx-auto mb-4"
              style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
            >
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M12 2.5L13.09 9.26L19.5 12L13.09 14.74L12 21.5L10.91 14.74L4.5 12L10.91 9.26L12 2.5Z"
                  fill="white" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white mb-1">Atlas AI</h1>
            <p className="text-zinc-500 text-sm">Your intelligent learning companion</p>
          </div>
        </motion.div>
      )}
      {isOpen && <AtlasWorkspace context={context} />}
    </div>
  );
}
