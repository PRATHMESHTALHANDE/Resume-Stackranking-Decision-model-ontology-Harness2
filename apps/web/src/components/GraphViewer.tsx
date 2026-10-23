import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import type { Core } from 'cytoscape';
import { Network, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { fetchCytoscapeGraph } from '../api';

interface GraphViewerProps {
  jobId: string;
  selectedCandidateId?: string;
  darkMode: boolean;
}

export const GraphViewer: React.FC<GraphViewerProps> = ({ jobId, selectedCandidateId, darkMode }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    fetchCytoscapeGraph(jobId, selectedCandidateId)
      .then((data) => {
        if (!isMounted || !containerRef.current) return;

        // Clean previous instance
        if (cyRef.current) {
          cyRef.current.destroy();
        }

        const cy = cytoscape({
          container: containerRef.current,
          elements: data.elements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'font-size': '11px',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': darkMode ? '#F1F5F9' : '#1E293B',
                'background-color': darkMode ? '#2A303C' : '#E2E8F0',
                'border-width': 2,
                'border-color': darkMode ? '#4B5563' : '#CBD5E1',
                'width': 'label',
                'height': '36px',
                'padding': '10px',
                'shape': 'roundrectangle',
              },
            },
            {
              selector: 'node[type = "Job"]',
              style: {
                'background-color': '#3B82F6',
                'color': '#FFFFFF',
                'font-weight': 'bold',
                'border-color': '#1D4ED8',
              },
            },
            {
              selector: 'node[type = "Requirement"]',
              style: {
                'background-color': '#10B981',
                'color': '#FFFFFF',
                'border-color': '#047857',
              },
            },
            {
              selector: 'node[type = "Candidate"]',
              style: {
                'background-color': '#8B5CF6',
                'color': '#FFFFFF',
                'border-color': '#6D28D9',
              },
            },
            {
              selector: 'node[type = "Skill"]',
              style: {
                'background-color': darkMode ? '#374151' : '#F3F4F6',
                'border-color': '#3B82F6',
              },
            },
            {
              selector: 'edge',
              style: {
                'width': 1.5,
                'line-color': darkMode ? '#4B5563' : '#94A3B8',
                'target-arrow-color': darkMode ? '#4B5563' : '#94A3B8',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(relation)',
                'font-size': '8px',
                'color': darkMode ? '#9CA3AF' : '#64748B',
                'text-rotation': 'autorotate',
              },
            },
          ],
          layout: {
            name: 'cose',
            animate: false,
            padding: 40,
          },
        });

        cy.on('tap', 'node', (evt) => {
          setSelectedNode(evt.target.data());
        });

        cy.on('tap', (evt) => {
          if (evt.target === cy) {
            setSelectedNode(null);
          }
        });

        cyRef.current = cy;
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load Cytoscape graph:', err);
        setLoading(false);
      });

    return () => {
      isMounted = false;
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [jobId, selectedCandidateId, darkMode]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit();

  return (
    <div className="neu-flat p-6 flex flex-col gap-4 relative">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-base font-bold text-slate-800 dark:text-slate-100">
            Interactive Skill & Ontology Knowledge Topology
          </h2>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <button onClick={handleZoomIn} className="neu-button p-2" title="Zoom In">
            <ZoomIn className="w-4 h-4 text-slate-600 dark:text-slate-300" />
          </button>
          <button onClick={handleZoomOut} className="neu-button p-2" title="Zoom Out">
            <ZoomOut className="w-4 h-4 text-slate-600 dark:text-slate-300" />
          </button>
          <button onClick={handleFit} className="neu-button p-2" title="Fit to screen">
            <RotateCcw className="w-4 h-4 text-slate-600 dark:text-slate-300" />
          </button>
        </div>
      </div>

      {/* Canvas */}
      <div className="neu-inset w-full h-[540px] rounded-xl overflow-hidden relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900/10 dark:bg-black/30 z-10">
            <span className="text-sm font-semibold text-blue-600 animate-pulse">Loading Topology...</span>
          </div>
        )}
        <div ref={containerRef} className="w-full h-full" />
      </div>

      {/* Selected Node Inspector */}
      {selectedNode && (
        <div className="neu-raised-sm p-3 flex items-center justify-between text-xs">
          <div>
            <span className="font-bold text-slate-700 dark:text-slate-200">{selectedNode.label}</span>
            <span className="ml-2 text-slate-500">({selectedNode.type})</span>
          </div>
          <span className="font-mono text-slate-400">ID: {selectedNode.id}</span>
        </div>
      )}
    </div>
  );
};
