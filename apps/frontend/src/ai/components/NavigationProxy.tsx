import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAtlasStore } from '../store';

export function NavigationProxy() {
  const navigate = useNavigate();

  useEffect(() => {
    return useAtlasStore.subscribe((state) => {
      const path = state.pendingNavigation;
      if (!path) return;
      useAtlasStore.getState().setPendingNavigation(null);
      navigate(path);
    });
  }, [navigate]);

  return null;
}
