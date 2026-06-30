import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { CatalogPage } from './catalog/CatalogPage';
import { AlgorithmDetailPage } from './algorithm/AlgorithmDetailPage';
import { ComparisonPage } from './comparison/ComparisonPage';
import { EmbedPage } from './embed/EmbedPage';
import { NotebookPage } from './notebook/NotebookPage';
import { ExperimentsPage } from './experiments/ExperimentsPage';
import { NavBar } from './components/layout/NavBar';
import { LandingPage } from './landing/LandingPage';
import { GridBackground } from './components/ui/GridBackground';
import { LearningPage } from './learning/LearningPage';
import { LessonPage } from './learning/LessonPage';
import { AtlasAI } from './ai/AtlasAI';
import { AtlasPage } from './ai/page/AtlasPage';

function AppLayout() {
  return (
    <div className="min-h-screen bg-[#09090B] text-white relative">
      <GridBackground />
      {/* NavBar overlays all pages; pages use pt-20 to avoid overlap */}
      <NavBar />
      <main className="relative" style={{ zIndex: 1 }}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/algorithms" element={<div className="pt-20"><CatalogPage /></div>} />
          <Route path="/algorithms/:slug" element={<div className="pt-20"><AlgorithmDetailPage /></div>} />
          <Route path="/compare" element={<div className="pt-20"><ComparisonPage /></div>} />
          <Route path="/notebook" element={<div className="pt-20"><NotebookPage /></div>} />
          <Route path="/experiments" element={<div className="pt-20"><ExperimentsPage /></div>} />
          <Route path="/learning" element={<div className="pt-20"><LearningPage /></div>} />
          <Route path="/learning/:id" element={<div className="pt-20"><LessonPage /></div>} />
          <Route path="/atlas" element={<AtlasPage />} />
        </Routes>
      </main>
      {/* Atlas AI — mounted once, floats above all pages */}
      <AtlasAI />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Embed route — no navbar, full-screen iframe shell */}
        <Route path="/embed/:slug" element={<EmbedPage />} />

        {/* Main app — with floating navbar */}
        <Route path="*" element={<AppLayout />} />
      </Routes>
    </BrowserRouter>
  );
}
