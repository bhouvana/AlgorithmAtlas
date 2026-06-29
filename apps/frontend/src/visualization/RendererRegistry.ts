/**
 * RendererRegistry — maps VisualizationType → React component.
 *
 * Adding a new visualization type: add one entry here and create the component.
 * No other file needs to change.
 */

import { createElement, type ComponentType } from 'react';
import { ArrayBarRenderer } from './renderers/ArrayBarRenderer';
import { ArraySearchRenderer } from './renderers/ArraySearchRenderer';
import { GraphTraversalRenderer } from './renderers/GraphTraversalRenderer';
import { TreeRenderer } from './renderers/TreeRenderer';
import { DPTableRenderer } from './renderers/DPTableRenderer';
import { GridRenderer } from './renderers/GridRenderer';
import { CurveRenderer } from './renderers/CurveRenderer';
import { ParticleFieldRenderer } from './renderers/ParticleFieldRenderer';
import { ProbabilityRenderer } from './renderers/ProbabilityRenderer';
import { StateMachineRenderer } from './renderers/StateMachineRenderer';
import { NetworkTopologyRenderer } from './renderers/NetworkTopologyRenderer';
import { TimelineRenderer } from './renderers/TimelineRenderer';
import { GeometricRenderer } from './renderers/GeometricRenderer';

export type VisualizationType =
  | 'ARRAY_BARS'
  | 'ARRAY_BARS_SEARCH'
  | 'GRAPH'
  | 'TREE'
  | 'MATRIX'
  | 'GRID'
  | 'CURVE'
  | 'PARTICLE_FIELD'
  | 'NETWORK_TOPOLOGY'
  | 'GEOMETRIC'
  | 'STATE_MACHINE'
  | 'PROBABILITY_SPACE'
  | 'TIMELINE';

export interface RendererProps {
  state: Record<string, unknown>;
  width?: number;
  height?: number;
}

const RENDERER_MAP: Record<VisualizationType, ComponentType<RendererProps>> = {
  ARRAY_BARS:        ArrayBarRenderer,
  ARRAY_BARS_SEARCH: ArraySearchRenderer,
  GRAPH:             GraphTraversalRenderer,
  TREE:              TreeRenderer,
  MATRIX:            DPTableRenderer,
  GRID:              GridRenderer,
  CURVE:             CurveRenderer,
  PARTICLE_FIELD:    ParticleFieldRenderer,
  PROBABILITY_SPACE: ProbabilityRenderer,
  STATE_MACHINE:     StateMachineRenderer,
  NETWORK_TOPOLOGY:  NetworkTopologyRenderer,
  TIMELINE:          TimelineRenderer,
  GEOMETRIC:         GeometricRenderer,
};

export function getRenderer(
  type: VisualizationType,
): ComponentType<RendererProps> {
  return RENDERER_MAP[type] ?? (() =>
    createElement(
      'div',
      { className: 'flex items-center justify-center h-48 text-neutral-500 font-mono text-sm' },
      `Unknown renderer: "${type}"`,
    )
  );
}
