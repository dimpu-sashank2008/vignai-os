import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Search,
  Filter,
  Flame,
  Building2,
  MapPin,
  Tag,
  FileText,
  Shield,
  Layers,
  ArrowRight,
  Info,
  Sparkles,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import client from '../../api/client';
import { GraphNode, GraphEdge, IntelligenceGraphResponse } from '../../types';

interface IntelligenceGraphProps {
  onOpenWhyModal?: (insightType: string, insightId: string) => void;
}

export const IntelligenceGraph: React.FC<IntelligenceGraphProps> = ({ onOpenWhyModal }) => {
  const [graphData, setGraphData] = useState<IntelligenceGraphResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Graph interaction state
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Filter & Search state
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  const fetchGraph = async () => {
    setIsLoading(true);
    try {
      const res = await client.get<IntelligenceGraphResponse>('/intelligence/graph');
      setGraphData(res.data);
    } catch (err) {
      console.error('Failed to load intelligence graph:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  // Compute node positions using deterministic circular / force clustered layout
  const layout = useMemo(() => {
    if (!graphData) return { nodes: [], edges: [] };

    const width = 1100;
    const height = 650;
    const centerX = width / 2;
    const centerY = height / 2;

    const positionedNodes: Array<GraphNode & { x: number; y: number }> = [];
    const nodePosMap = new Map<string, { x: number; y: number }>();

    // Separate by type
    const patterns = graphData.nodes.filter((n: GraphNode) => n.type === 'PATTERN');
    const departments = graphData.nodes.filter((n: GraphNode) => n.type === 'DEPARTMENT');
    const categories = graphData.nodes.filter((n: GraphNode) => n.type === 'CATEGORY');
    const locations = graphData.nodes.filter((n: GraphNode) => n.type === 'LOCATION');
    const cases = graphData.nodes.filter((n: GraphNode) => n.type === 'CASE');

    // 1. Patterns in Center Ring (radius: 110)
    patterns.forEach((n: GraphNode, i: number) => {
      const angle = (i / Math.max(patterns.length, 1)) * 2 * Math.PI - Math.PI / 2;
      const x = centerX + Math.cos(angle) * 110;
      const y = centerY + Math.sin(angle) * 90;
      positionedNodes.push({ ...n, x, y });
      nodePosMap.set(n.id, { x, y });
    });

    // 2. Departments in Left/Upper Arc (radius: 240)
    departments.forEach((n: GraphNode, i: number) => {
      const angle = Math.PI * 0.6 + (i / Math.max(departments.length, 1)) * Math.PI * 0.8;
      const x = centerX + Math.cos(angle) * 260;
      const y = centerY + Math.sin(angle) * 220;
      positionedNodes.push({ ...n, x, y });
      nodePosMap.set(n.id, { x, y });
    });

    // 3. Locations in Right/Lower Arc (radius: 260)
    locations.forEach((n: GraphNode, i: number) => {
      const angle = -Math.PI * 0.3 + (i / Math.max(locations.length, 1)) * Math.PI * 0.8;
      const x = centerX + Math.cos(angle) * 290;
      const y = centerY + Math.sin(angle) * 240;
      positionedNodes.push({ ...n, x, y });
      nodePosMap.set(n.id, { x, y });
    });

    // 4. Categories in Upper Zone
    categories.forEach((n: GraphNode, i: number) => {
      const angle = -Math.PI * 0.8 + (i / Math.max(categories.length, 1)) * Math.PI * 0.5;
      const x = centerX + Math.cos(angle) * 350;
      const y = centerY + Math.sin(angle) * 270;
      positionedNodes.push({ ...n, x, y });
      nodePosMap.set(n.id, { x, y });
    });

    // 5. Cases orbit the outer perimeter with organic variation
    cases.forEach((n: GraphNode, i: number) => {
      const angle = (i / Math.max(cases.length, 1)) * 2 * Math.PI;
      const radius = 420 + (i % 3) * 35;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * (radius * 0.75);
      positionedNodes.push({ ...n, x, y });
      nodePosMap.set(n.id, { x, y });
    });

    // Connect edges with coordinates
    const positionedEdges = graphData.edges
      .map((e: GraphEdge) => {
        const sourcePos = nodePosMap.get(e.source);
        const targetPos = nodePosMap.get(e.target);
        if (!sourcePos || !targetPos) return null;
        return {
          ...e,
          x1: sourcePos.x,
          y1: sourcePos.y,
          x2: targetPos.x,
          y2: targetPos.y,
        };
      })
      .filter(Boolean) as Array<GraphEdge & { x1: number; y1: number; x2: number; y2: number }>;

    return { nodes: positionedNodes, edges: positionedEdges };
  }, [graphData]);

  // Connected nodes map for highlighting
  const connectedNodeIds = useMemo(() => {
    if (!selectedNodeId || !graphData) return null;
    const set = new Set<string>([selectedNodeId]);
    graphData.edges.forEach((e: GraphEdge) => {
      if (e.source === selectedNodeId) set.add(e.target);
      if (e.target === selectedNodeId) set.add(e.source);
    });
    return set;
  }, [selectedNodeId, graphData]);

  // Mouse pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'svg' || (e.target as HTMLElement).id === 'graph-canvas') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    setZoom((prev) => Math.max(0.4, Math.min(2.5, prev * zoomFactor)));
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNodeId(null);
  };

  const selectedNode = useMemo(() => {
    if (!selectedNodeId || !graphData) return null;
    return graphData.nodes.find((n: GraphNode) => n.id === selectedNodeId) || null;
  }, [selectedNodeId, graphData]);

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'PATTERN':
        return { bg: '#161616', stroke: '#f43f5e', text: '#ffffff', labelBg: '#ffe4e6', labelText: '#9f1239', glow: 'rgba(244, 63, 94, 0.4)' };
      case 'DEPARTMENT':
        return { bg: '#161616', stroke: '#f59e0b', text: '#ffffff', labelBg: '#fef3c7', labelText: '#92400e', glow: 'rgba(245, 158, 11, 0.4)' };
      case 'LOCATION':
        return { bg: '#161616', stroke: '#10b981', text: '#ffffff', labelBg: '#d1fae5', labelText: '#065f46', glow: 'rgba(16, 185, 129, 0.4)' };
      case 'CATEGORY':
        return { bg: '#161616', stroke: '#0ea5e9', text: '#ffffff', labelBg: '#e0f2fe', labelText: '#0369a1', glow: 'rgba(14, 165, 233, 0.4)' };
      case 'CASE':
        return { bg: '#161616', stroke: '#6366f1', text: '#ffffff', labelBg: '#eef2ff', labelText: '#3730a3', glow: 'rgba(99, 102, 241, 0.4)' };
      default:
        return { bg: '#161616', stroke: '#71717a', text: '#ffffff', labelBg: '#f1f5f9', labelText: '#334155', glow: 'rgba(113, 113, 122, 0.4)' };
    }
  };

  const getNodeRadius = (type: string) => {
    switch (type) {
      case 'PATTERN':
        return 22;
      case 'DEPARTMENT':
        return 18;
      case 'LOCATION':
        return 16;
      case 'CATEGORY':
        return 15;
      case 'CASE':
        return 12;
      default:
        return 14;
    }
  };

  // Filtered nodes
  const filteredNodes = useMemo(() => {
    return layout.nodes.filter((n) => {
      if (typeFilter !== 'ALL' && n.type !== typeFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return n.label.toLowerCase().includes(q) || (n.data.description && String(n.data.description).toLowerCase().includes(q));
      }
      return true;
    });
  }, [layout.nodes, typeFilter, searchQuery]);

  const filteredNodeIdSet = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  return (
    <div className={`overflow-hidden border border-slate-200 dark:border-white/10 bg-white dark:bg-black text-slate-900 dark:text-white rounded-3xl shadow-sm ${isFullscreen ? 'fixed inset-4 z-50 rounded-3xl shadow-2xl' : ''}`}>
      {/* Top Controls Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 sm:p-5 border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#050505] backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
              Campus Intelligence Knowledge Graph
              <span className="text-[10px] font-semibold bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-400/30 px-2 py-0.5 rounded-full">
                Relational Provenance
              </span>
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-zinc-400">
              Real links between cases, locations, categories, departments, and detected clusters.
            </p>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search nodes or cases..."
              className="pl-8 pr-3 py-1.5 text-xs bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:border-indigo-500 w-44"
            />
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="py-1.5 px-2.5 text-xs bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Nodes</option>
            <option value="PATTERN">Patterns</option>
            <option value="CASE">Cases</option>
            <option value="LOCATION">Locations</option>
            <option value="DEPARTMENT">Departments</option>
            <option value="CATEGORY">Categories</option>
          </select>

          {/* Zoom Controls */}
          <div className="flex items-center bg-white dark:bg-[#0A0A0A] rounded-xl border border-slate-200 dark:border-white/10 p-0.5">
            <button
              onClick={() => setZoom((z) => Math.min(2.5, z * 1.15))}
              className="p-1.5 hover:bg-slate-100 dark:hover:bg-[#161616] rounded-lg text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
              title="Zoom In"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setZoom((z) => Math.max(0.4, z * 0.85))}
              className="p-1.5 hover:bg-slate-100 dark:hover:bg-[#161616] rounded-lg text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
              title="Zoom Out"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={resetView}
              className="p-1.5 hover:bg-slate-100 dark:hover:bg-[#161616] rounded-lg text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
              title="Reset View"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 bg-white dark:bg-[#0A0A0A] hover:bg-slate-100 dark:hover:bg-[#161616] rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      {/* Legend & Metrics Bar */}
      <div className="flex items-center justify-between px-5 py-2.5 bg-slate-900/50 border-b border-slate-800/80 text-[11px] text-slate-400 overflow-x-auto gap-4">
        <div className="flex items-center gap-4 shrink-0">
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500" /> Pattern Cluster
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500" /> Department
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" /> Location
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-sky-500" /> Category
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-indigo-500" /> Case
          </span>
        </div>

        {graphData && (
          <div className="text-slate-500 font-mono text-[10px] shrink-0">
            {graphData.metrics.total_nodes} Nodes • {graphData.metrics.total_edges} Edges
          </div>
        )}
      </div>

      {/* Interactive Canvas */}
      <div
        ref={containerRef}
        id="graph-canvas"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={handleWheel}
        className="relative h-[550px] sm:h-[620px] w-full cursor-grab active:cursor-grabbing overflow-hidden bg-slate-900 dark:bg-black bg-[radial-gradient(rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:20px_20px]"
      >
        {isLoading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center space-y-3">
            <div className="h-8 w-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-slate-400">Loading Relational Knowledge Graph...</span>
          </div>
        ) : (
          <svg
            className="w-full h-full select-none"
            viewBox="0 0 1100 650"
            preserveAspectRatio="xMidYMid meet"
          >
            <g
              transform={`translate(${pan.x + 550 * (1 - zoom)}, ${pan.y + 325 * (1 - zoom)}) scale(${zoom})`}
            >
              {/* Edges */}
              {layout.edges.map((edge) => {
                const isConnected =
                  selectedNodeId &&
                  (edge.source === selectedNodeId || edge.target === selectedNodeId);
                const isDimmed =
                  selectedNodeId &&
                  edge.source !== selectedNodeId &&
                  edge.target !== selectedNodeId;

                const isVisible =
                  filteredNodeIdSet.has(edge.source) && filteredNodeIdSet.has(edge.target);

                if (!isVisible) return null;

                return (
                  <g key={edge.id}>
                    <line
                      x1={edge.x1}
                      y1={edge.y1}
                      x2={edge.x2}
                      y2={edge.y2}
                      stroke={isConnected ? '#818cf8' : '#27272a'}
                      strokeWidth={isConnected ? 2.5 : 1}
                      strokeOpacity={isDimmed ? 0.15 : isConnected ? 1 : 0.45}
                      strokeDasharray={edge.type === 'PATTERN_LINK' ? '4,4' : undefined}
                    />
                  </g>
                );
              })}

              {/* Nodes */}
              {filteredNodes.map((node) => {
                const colors = getNodeColor(node.type);
                const radius = getNodeRadius(node.type);
                const isSelected = selectedNodeId === node.id;
                const isConnected = connectedNodeIds?.has(node.id);
                const isDimmed = selectedNodeId && !isSelected && !isConnected;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedNodeId(node.id === selectedNodeId ? null : node.id);
                    }}
                    className="cursor-pointer transition-transform"
                    opacity={isDimmed ? 0.25 : 1}
                  >
                    {/* Glowing highlight ring */}
                    {isSelected && (
                      <circle
                        r={radius + 8}
                        fill="none"
                        stroke={colors.stroke}
                        strokeWidth={2.5}
                        className="animate-pulse"
                      />
                    )}

                    {/* Node circle */}
                    <circle
                      r={radius}
                      fill={colors.bg}
                      stroke={colors.stroke}
                      strokeWidth={isSelected ? 3 : 1.5}
                    />

                    {/* Node Label Text */}
                    <text
                      y={radius + 14}
                      textAnchor="middle"
                      className="text-[11px] font-bold fill-white pointer-events-none drop-shadow-md select-none"
                    >
                      {node.label.length > 18 ? node.label.substring(0, 16) + '…' : node.label}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        )}

        {/* Selected Node Inspector Drawer */}
        {selectedNode && (
          <div className="absolute right-4 top-4 bottom-4 w-80 sm:w-96 bg-white/95 dark:bg-[#0A0A0A]/95 backdrop-blur-md rounded-2xl border border-slate-200 dark:border-white/10 p-5 shadow-2xl overflow-y-auto space-y-4 animate-fade-in z-20">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-lg border border-indigo-200 dark:border-indigo-800/40">
                {selectedNode.type} NODE
              </span>
              <button
                onClick={() => setSelectedNodeId(null)}
                className="text-slate-400 hover:text-slate-700 dark:hover:text-white text-xs font-bold"
              >
                ✕ Close
              </button>
            </div>

            <div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white">{selectedNode.label}</h4>
              {selectedNode.data.description && (
                <p className="text-xs text-slate-600 dark:text-zinc-300 mt-1 leading-relaxed">
                  {selectedNode.data.description}
                </p>
              )}
            </div>

            {/* Metadata Fields */}
            <div className="space-y-2 text-xs bg-slate-50 dark:bg-[#101010] p-3.5 rounded-xl border border-slate-200 dark:border-white/10">
              {selectedNode.type === 'CASE' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Case ID:</span>
                    <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">{selectedNode.data.case_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Category:</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{selectedNode.data.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Location:</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{selectedNode.data.location}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Priority / Status:</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{selectedNode.data.priority} • {selectedNode.data.status}</span>
                  </div>
                </>
              )}

              {selectedNode.type === 'PATTERN' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Pattern Type:</span>
                    <span className="font-semibold text-rose-600 dark:text-rose-400">{selectedNode.data.pattern_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Severity:</span>
                    <span className="font-bold text-rose-600 dark:text-rose-400">{selectedNode.data.severity}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Corroborating Cases:</span>
                    <span className="font-bold text-slate-900 dark:text-white">{selectedNode.data.case_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500 dark:text-zinc-400">Affected Scope:</span>
                    <span className="font-semibold text-slate-800 dark:text-zinc-200">{selectedNode.data.affected_estimate}</span>
                  </div>
                </>
              )}

              {selectedNode.type === 'LOCATION' && (
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-zinc-400">Incidents at Location:</span>
                  <span className="font-bold text-emerald-600 dark:text-emerald-400">{selectedNode.data.count || 1} complaints</span>
                </div>
              )}

              {selectedNode.type === 'DEPARTMENT' && (
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-zinc-400">Department Load:</span>
                  <span className="font-bold text-amber-600 dark:text-amber-400">{selectedNode.data.count || 1} complaints</span>
                </div>
              )}
            </div>

            {/* Direct Actions */}
            <div className="pt-2 space-y-2">
              {selectedNode.type === 'CASE' && (
                <Link
                  to={`/management/issues/${selectedNode.data.case_id}`}
                  className="w-full flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors shadow-lg shadow-indigo-600/30"
                >
                  <FileText className="h-3.5 w-3.5" /> Inspect Case Details
                </Link>
              )}

              {selectedNode.type === 'PATTERN' && onOpenWhyModal && (
                <button
                  onClick={() => onOpenWhyModal('PATTERN', String(selectedNode.data.pattern_id))}
                  className="w-full flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-colors shadow-lg shadow-rose-600/30"
                >
                  <Sparkles className="h-3.5 w-3.5" /> Why this Pattern? (Evidence Breakdown)
                </button>
              )}

              {selectedNode.type === 'CASE' && onOpenWhyModal && (
                <button
                  onClick={() => onOpenWhyModal('PRIORITY_CASE', selectedNode.data.case_id)}
                  className="w-full flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-slate-100 dark:bg-[#161616] hover:bg-slate-200 dark:hover:bg-[#202020] text-slate-800 dark:text-zinc-200 font-semibold text-xs border border-slate-200 dark:border-white/10 transition-colors"
                >
                  <Info className="h-3.5 w-3.5" /> Why was this Case Prioritized?
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligenceGraph;
