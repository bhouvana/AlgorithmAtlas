import { HeroSection } from './sections/Hero';
import { StatsSection } from './sections/Stats';
import { CapabilityBarSection } from './sections/CapabilityBar';
import { LiveVisualizationSection } from './sections/LiveVisualization';
import { AtlasCodeShowcaseSection } from './sections/AtlasCodeShowcase';
import { PolyglotSwitcherSection } from './sections/PolyglotSwitcher';
import { AtlasAIShowcaseSection } from './sections/AtlasAIShowcase';
import { LearningJourneySection } from './sections/LearningJourney';
import { ExecutionPipelineSection } from './sections/ExecutionPipeline';
import { AlgorithmMarqueeSection } from './sections/Marquee';
import { RoadmapCommunitySection } from './sections/RoadmapCommunity';
import { FinalCTASection } from './sections/FinalCTA';
import { FooterSection } from './sections/Footer';

export function LandingPage() {
  return (
    <div className="min-h-screen text-white">
      <HeroSection />
      <StatsSection />
      <CapabilityBarSection />
      <LiveVisualizationSection />
      <AtlasCodeShowcaseSection />
      <PolyglotSwitcherSection />
      <AtlasAIShowcaseSection />
      <LearningJourneySection />
      <ExecutionPipelineSection />
      <AlgorithmMarqueeSection />
      <RoadmapCommunitySection />
      <FinalCTASection />
      <FooterSection />
    </div>
  );
}
