/**
 * SimulationProxy — headless component that executes AI-issued simulation
 * commands against the active SimulationController.
 *
 * Mounted once inside AtlasAI. Watches pendingCommands in the store and
 * dispatches them to the controller, then clears the queue.
 */
import { useEffect } from 'react';
import { useAtlasStore } from '../store';
import { useSimulationStore } from '../../core/store/simulationStore';
import type { SimulationCommand } from '../types';

async function executeCommand(
  cmd: SimulationCommand,
  controller: NonNullable<ReturnType<typeof useSimulationStore.getState>['controller']>,
) {
  switch (cmd.action) {
    case 'play':          controller.play(); break;
    case 'pause':         controller.pause(); break;
    case 'reset':         await controller.reset(); break;
    case 'step_forward':  await controller.stepForward(); break;
    case 'step_backward': await controller.stepBackward(); break;
    case 'seek':          await controller.seek(cmd.frame); break;
    case 'set_speed':     controller.setSpeed(cmd.value); break;
  }
}

export function SimulationProxy() {
  const { pendingCommands, clearPendingCommands } = useAtlasStore();
  const controller = useSimulationStore((s) => s.controller);

  useEffect(() => {
    if (pendingCommands.length === 0 || !controller) return;

    const cmds = [...pendingCommands];
    clearPendingCommands();

    (async () => {
      for (const cmd of cmds) {
        try {
          await executeCommand(cmd, controller);
        } catch {
          // ignore individual command errors
        }
      }
    })();
  }, [pendingCommands, controller, clearPendingCommands]);

  return null;
}
