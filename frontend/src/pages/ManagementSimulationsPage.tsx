import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  FlaskConical,
  Play,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  Layers,
  ArrowRight,
  Info,
  CheckCircle2,
  Bookmark,
  History,
  RotateCcw,
  Sliders,
  Bus,
  Wifi,
  Wrench,
  Shield,
  HelpCircle,
  Clock,
  Zap,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  SimulationComparisonResponse,
  SavedSimulationResponse,
} from '../types';

export const ManagementSimulationsPage: React.FC = () => {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState<'LAB' | 'HISTORY'>('LAB');
  const [domain, setDomain] = useState<'TRANSPORT' | 'INFRASTRUCTURE' | 'MAINTENANCE'>('TRANSPORT');

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'what-if-lab';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state]);

  // Pre-populate scenario inputs from Ask VIGNAI navigation parameters
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const domainParam = searchParams.get('domain');
    if (domainParam) {
      const upper = domainParam.toUpperCase();
      if (upper === 'TRANSPORT' || upper === 'INFRASTRUCTURE' || upper === 'MAINTENANCE') {
        setDomain(upper as any);
      }
    }

    const locationParam = searchParams.get('location');
    if (locationParam) {
      if (
        locationParam.toLowerCase().includes('block') ||
        locationParam.toLowerCase().includes('wifi') ||
        locationParam.toLowerCase().includes('wi-fi') ||
        locationParam.toLowerCase().includes('library')
      ) {
        setDomain('INFRASTRUCTURE');
        setWifiLocation(locationParam);
      } else if (
        locationParam.toLowerCase().includes('bus') ||
        locationParam.toLowerCase().includes('route') ||
        locationParam.toLowerCase().includes('transport') ||
        locationParam.toLowerCase().includes('gate')
      ) {
        setDomain('TRANSPORT');
        setTransportRoute(locationParam);
      } else if (
        locationParam.toLowerCase().includes('maint') ||
        locationParam.toLowerCase().includes('repair') ||
        locationParam.toLowerCase().includes('water')
      ) {
        setDomain('MAINTENANCE');
      }
    }

    const busesParam = searchParams.get('buses');
    if (busesParam && !isNaN(Number(busesParam))) {
      setTransportAddBusesA(Number(busesParam));
    }

    const apsParam = searchParams.get('aps');
    if (apsParam && !isNaN(Number(apsParam))) {
      setWifiAddAPsA(Number(apsParam));
    }

    const techsParam = searchParams.get('techs');
    if (techsParam && !isNaN(Number(techsParam))) {
      setMaintAddTechsA(Number(techsParam));
    }
  }, [location.search]);

  // Transport inputs
  const [transportRoute, setTransportRoute] = useState('Route 4 (North Gate ↔ Hostels)');
  const [transportCurrentBuses, setTransportCurrentBuses] = useState(5);
  const [transportDemand, setTransportDemand] = useState(420);
  const [transportAddBusesA, setTransportAddBusesA] = useState(1);
  const [transportAddBusesB, setTransportAddBusesB] = useState(2);
  const [enableScenarioB, setEnableScenarioB] = useState(true);

  // Infrastructure inputs
  const [wifiLocation, setWifiLocation] = useState('Block A');
  const [wifiCurrentAPs, setWifiCurrentAPs] = useState(10);
  const [wifiAddAPsA, setWifiAddAPsA] = useState(3);
  const [wifiAddAPsB, setWifiAddAPsB] = useState(6);

  // Maintenance inputs
  const [maintCurrentTechs, setMaintCurrentTechs] = useState(5);
  const [maintAddTechsA, setMaintAddTechsA] = useState(2);
  const [maintAddTechsB, setMaintAddTechsB] = useState(4);

  // State machine: IDLE -> SIMULATING -> RESULT
  const [simState, setSimState] = useState<'IDLE' | 'SIMULATING' | 'RESULT'>('IDLE');
  const [simulationResult, setSimulationResult] = useState<SimulationComparisonResponse | null>(null);
  const [savedSimulations, setSavedSimulations] = useState<SavedSimulationResponse[]>([]);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [selectedScenarioIdx, setSelectedScenarioIdx] = useState<number>(0);

  const fetchSavedSimulations = async () => {
    try {
      const res = await client.get<SavedSimulationResponse[]>('/management/simulations');
      setSavedSimulations(res.data);
    } catch (err) {
      console.error('Failed to load saved simulations:', err);
    }
  };

  useEffect(() => {
    fetchSavedSimulations();
  }, []);

  const handleRunSimulation = async () => {
    setSimState('SIMULATING');
    setSimulationResult(null);

    // Build payload according to selected domain
    let baselineParams: Record<string, any> = {};
    let scenariosList: Array<{ scenario_id: string; name: string; parameters: Record<string, any> }> = [];

    if (domain === 'TRANSPORT') {
      baselineParams = {
        route: transportRoute,
        current_buses: transportCurrentBuses,
        current_demand: transportDemand,
        capacity_per_bus: 84.0,
        average_waiting_time: 22.0,
        current_operating_cost: 100.0,
      };

      scenariosList.push({
        scenario_id: 'scenario_a',
        name: `Scenario A (+${transportAddBusesA} Bus)`,
        parameters: { additional_buses: transportAddBusesA },
      });

      if (enableScenarioB) {
        scenariosList.push({
          scenario_id: 'scenario_b',
          name: `Scenario B (+${transportAddBusesB} Buses)`,
          parameters: { additional_buses: transportAddBusesB },
        });
      }
    } else if (domain === 'INFRASTRUCTURE') {
      baselineParams = {
        location: wifiLocation,
        current_access_points: wifiCurrentAPs,
        current_users: 450.0,
        current_utilization: 0.90,
        average_latency: 65.0,
      };

      scenariosList.push({
        scenario_id: 'scenario_a',
        name: `Scenario A (+${wifiAddAPsA} APs)`,
        parameters: { additional_access_points: wifiAddAPsA },
      });

      if (enableScenarioB) {
        scenariosList.push({
          scenario_id: 'scenario_b',
          name: `Scenario B (+${wifiAddAPsB} APs)`,
          parameters: { additional_access_points: wifiAddAPsB },
        });
      }
    } else if (domain === 'MAINTENANCE') {
      baselineParams = {
        current_technicians: maintCurrentTechs,
        open_maintenance_cases: 34,
        avg_resolution_capacity: 4.0,
        current_backlog_days: 12.0,
      };

      scenariosList.push({
        scenario_id: 'scenario_a',
        name: `Scenario A (+${maintAddTechsA} Techs)`,
        parameters: { additional_technicians: maintAddTechsA },
      });

      if (enableScenarioB) {
        scenariosList.push({
          scenario_id: 'scenario_b',
          name: `Scenario B (+${maintAddTechsB} Techs)`,
          parameters: { additional_technicians: maintAddTechsB },
        });
      }
    }

    try {
      // Artificial delay for smooth animated calculation transition
      await new Promise((r) => setTimeout(r, 600));

      const res = await client.post<SimulationComparisonResponse>('/management/simulations/run', {
        domain: domain,
        scenario_name: domain === 'TRANSPORT' ? 'Add buses to a route' : domain === 'INFRASTRUCTURE' ? 'Increase Wi-Fi access points' : 'Increase maintenance capacity',
        baseline_parameters: baselineParams,
        scenarios: scenariosList,
      });

      setSimulationResult(res.data);
      setSelectedScenarioIdx(0);
      setSimState('RESULT');
    } catch (err) {
      console.error('Simulation failed:', err);
      setSimState('IDLE');
    }
  };

  const handleSaveScenario = async () => {
    if (!simulationResult) return;
    try {
      const activeSc = simulationResult.scenarios[selectedScenarioIdx];
      await client.post('/management/simulations', {
        name: `${domain} Decision: ${activeSc.name}`,
        scenario_type: domain,
        input_data: simulationResult.baseline_overview,
        result_data: activeSc,
      });
      setSaveSuccessMsg('Scenario saved successfully to Decision History.');
      fetchSavedSimulations();
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err) {
      console.error('Failed to save simulation:', err);
    }
  };

  return (
    <div id="what-if-lab" className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 dark:from-black dark:via-[#050505] dark:to-[#0A0A0A] p-6 sm:p-8 text-white shadow-xl border border-indigo-900/40 dark:border-white/10">
        <div className="absolute right-0 top-0 -mt-8 -mr-8 h-64 w-64 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-400/30">
              <FlaskConical className="h-3.5 w-3.5 text-indigo-400" />
              <span>DETERMINISTIC DECISION LAB</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
              WHAT-IF LAB
            </h1>
            <p className="text-slate-300 dark:text-zinc-400 text-xs sm:text-sm max-w-2xl leading-relaxed">
              Explore possible decisions before acting on them. Calculations are 100% deterministic mathematical models. AI explains comparative trade-offs and operational implications.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant={activeTab === 'LAB' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('LAB')}
              className={activeTab === 'LAB' ? 'bg-indigo-600 text-white font-semibold' : 'bg-white/10 dark:bg-white/5 text-white hover:bg-white/20 dark:hover:bg-white/10'}
            >
              <Sliders className="h-4 w-4 mr-1.5" /> Simulation Lab
            </Button>
            <Button
              variant={activeTab === 'HISTORY' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('HISTORY')}
              className={activeTab === 'HISTORY' ? 'bg-indigo-600 text-white font-semibold' : 'bg-white/10 dark:bg-white/5 text-white hover:bg-white/20 dark:hover:bg-white/10'}
            >
              <History className="h-4 w-4 mr-1.5" /> Saved History ({savedSimulations.length})
            </Button>
          </div>
        </div>
      </div>

      {activeTab === 'HISTORY' ? (
        /* Saved Simulations History */
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Saved Decision Scenarios</h3>
            </div>
            <span className="text-xs text-slate-400 dark:text-zinc-500">Total: {savedSimulations.length} saved records</span>
          </div>

          {savedSimulations.length === 0 ? (
            <div className="text-center py-12 text-slate-400 dark:text-zinc-500 text-sm">
              No saved scenarios yet. Run a simulation in the lab and click "Save Scenario".
            </div>
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-white/5">
              {savedSimulations.map((sim) => (
                <div key={sim.id} className="py-4 flex items-center justify-between gap-4">
                  <div className="space-y-1 min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-slate-900 dark:text-white truncate">{sim.name}</span>
                      <span className="text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded uppercase">
                        {sim.scenario_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-zinc-400 line-clamp-1">
                      {sim.result_data?.ai_scenario_explanation || 'Saved simulation result'}
                    </p>
                    <span className="text-[10px] text-slate-400 dark:text-zinc-500 block">
                      Saved on {new Date(sim.created_at).toLocaleString()}
                    </span>
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-lg">
                      {sim.result_data?.estimated_complaint_reduction_pct}% estimated relief
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      ) : (
        /* What-If Simulation Lab */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Scenario Configuration */}
          <div className="lg:col-span-5 space-y-5">
            <Card padding="lg" className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
                <div className="flex items-center gap-2">
                  <Sliders className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">Scenario Configuration</h3>
                </div>
                <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
                  Prototype Model
                </span>
              </div>

              {/* Domain Category Selector */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-700 dark:text-zinc-300 block">Select Scenario Domain:</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => { setDomain('TRANSPORT'); setSimState('IDLE'); }}
                    className={`flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-semibold transition-all ${
                      domain === 'TRANSPORT'
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-500 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 shadow-sm'
                        : 'bg-slate-50 dark:bg-[#0A0A0A] border-slate-200 dark:border-white/10 text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010]'
                    }`}
                  >
                    <Bus className="h-4 w-4 mb-1" /> Transport
                  </button>

                  <button
                    type="button"
                    onClick={() => { setDomain('INFRASTRUCTURE'); setSimState('IDLE'); }}
                    className={`flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-semibold transition-all ${
                      domain === 'INFRASTRUCTURE'
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-500 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 shadow-sm'
                        : 'bg-slate-50 dark:bg-[#0A0A0A] border-slate-200 dark:border-white/10 text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010]'
                    }`}
                  >
                    <Wifi className="h-4 w-4 mb-1" /> Infrastructure
                  </button>

                  <button
                    type="button"
                    onClick={() => { setDomain('MAINTENANCE'); setSimState('IDLE'); }}
                    className={`flex flex-col items-center justify-center p-3 rounded-2xl border text-xs font-semibold transition-all ${
                      domain === 'MAINTENANCE'
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 border-indigo-500 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 shadow-sm'
                        : 'bg-slate-50 dark:bg-[#0A0A0A] border-slate-200 dark:border-white/10 text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010]'
                    }`}
                  >
                    <Wrench className="h-4 w-4 mb-1" /> Maintenance
                  </button>
                </div>
              </div>

              {/* Dynamic Inputs Based on Domain */}
              {domain === 'TRANSPORT' && (
                <div className="space-y-3.5 pt-2 border-t border-slate-100 dark:border-white/10 text-xs">
                  <div className="space-y-1">
                    <label className="font-semibold text-slate-700 dark:text-zinc-300">Target Transit Route:</label>
                    <input
                      type="text"
                      value={transportRoute}
                      onChange={(e) => setTransportRoute(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="font-semibold text-slate-700 dark:text-zinc-300">Current Fleet Buses:</label>
                      <input
                        type="number"
                        min="1"
                        max="20"
                        value={transportCurrentBuses}
                        onChange={(e) => setTransportCurrentBuses(Number(e.target.value))}
                        className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 font-medium text-slate-900 dark:text-white"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="font-semibold text-slate-700 dark:text-zinc-300">Peak Demand (Students):</label>
                      <input
                        type="number"
                        min="50"
                        max="2000"
                        value={transportDemand}
                        onChange={(e) => setTransportDemand(Number(e.target.value))}
                        className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 font-medium text-slate-900 dark:text-white"
                      />
                    </div>
                  </div>

                  {/* Scenario Variations */}
                  <div className="p-3 bg-slate-50 dark:bg-[#0A0A0A] rounded-2xl border border-slate-200 dark:border-white/10 space-y-2.5">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 block">Scenario Variations:</span>
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-700 dark:text-zinc-300">Scenario A Add Buses:</span>
                      <div className="flex items-center gap-2">
                        {[1, 2, 3].map((n) => (
                          <button
                            key={n}
                            type="button"
                            onClick={() => setTransportAddBusesA(n)}
                            className={`h-7 w-7 rounded-lg text-xs font-bold transition-all ${
                              transportAddBusesA === n ? 'bg-indigo-600 text-white' : 'bg-white dark:bg-[#161616] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300'
                            }`}
                          >
                            +{n}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-1 border-t border-slate-200 dark:border-white/10">
                      <span className="font-medium text-slate-700 dark:text-zinc-300">Scenario B Add Buses:</span>
                      <div className="flex items-center gap-2">
                        {[2, 3, 4].map((n) => (
                          <button
                            key={n}
                            type="button"
                            onClick={() => setTransportAddBusesB(n)}
                            className={`h-7 w-7 rounded-lg text-xs font-bold transition-all ${
                              transportAddBusesB === n ? 'bg-indigo-600 text-white' : 'bg-white dark:bg-[#161616] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300'
                            }`}
                          >
                            +{n}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {domain === 'INFRASTRUCTURE' && (
                <div className="space-y-3.5 pt-2 border-t border-slate-100 dark:border-white/10 text-xs">
                  <div className="space-y-1">
                    <label className="font-semibold text-slate-700 dark:text-zinc-300">Target Academic Zone:</label>
                    <input
                      type="text"
                      value={wifiLocation}
                      onChange={(e) => setWifiLocation(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 font-medium text-slate-900 dark:text-white"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="font-semibold text-slate-700 dark:text-zinc-300">Current Access Points in Zone:</label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={wifiCurrentAPs}
                      onChange={(e) => setWifiCurrentAPs(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 font-medium text-slate-900 dark:text-white"
                    />
                  </div>

                  <div className="p-3 bg-slate-50 dark:bg-[#0A0A0A] rounded-2xl border border-slate-200 dark:border-white/10 space-y-2.5">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 block">Scenario Expansion:</span>
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-700 dark:text-zinc-300">Scenario A Add APs:</span>
                      <span className="font-bold text-indigo-600 dark:text-indigo-400">+{wifiAddAPsA} Dual-Band APs</span>
                    </div>
                    <div className="flex items-center justify-between pt-1 border-t border-slate-200 dark:border-white/10">
                      <span className="font-medium text-slate-700 dark:text-zinc-300">Scenario B Add APs:</span>
                      <span className="font-bold text-indigo-600 dark:text-indigo-400">+{wifiAddAPsB} Dual-Band APs</span>
                    </div>
                  </div>
                </div>
              )}

              {domain === 'MAINTENANCE' && (
                <div className="space-y-3.5 pt-2 border-t border-slate-100 dark:border-white/10 text-xs">
                  <div className="space-y-1">
                    <label className="font-semibold text-slate-700 dark:text-zinc-300">Current Full-time Technicians:</label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={maintCurrentTechs}
                      onChange={(e) => setMaintCurrentTechs(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 font-medium text-slate-900 dark:text-white"
                    />
                  </div>

                  <div className="p-3 bg-slate-50 dark:bg-[#0A0A0A] rounded-2xl border border-slate-200 dark:border-white/10 space-y-2.5">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 block">Capacity Variations:</span>
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-700 dark:text-zinc-300">Scenario A Staffing:</span>
                      <span className="font-bold text-indigo-600 dark:text-indigo-400">+{maintAddTechsA} Technicians</span>
                    </div>
                    <div className="flex items-center justify-between pt-1 border-t border-slate-200 dark:border-white/10">
                      <span className="font-medium text-slate-700 dark:text-zinc-300">Scenario B Staffing:</span>
                      <span className="font-bold text-indigo-600 dark:text-indigo-400">+{maintAddTechsB} Technicians</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <Button
                type="button"
                onClick={handleRunSimulation}
                isLoading={simState === 'SIMULATING'}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-2xl shadow-lg shadow-indigo-600/30"
              >
                <Play className="h-4 w-4 mr-1.5 fill-current" /> RUN SIMULATION
              </Button>
            </Card>
          </div>

          {/* Right Column: Simulation Result & Multi-Scenario Comparison */}
          <div className="lg:col-span-7 space-y-5">
            {simState === 'SIMULATING' && (
              <Card padding="lg" className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 min-h-[420px] flex flex-col items-center justify-center space-y-4 text-center">
                <div className="h-12 w-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                <div>
                  <h4 className="font-bold text-base text-slate-900 dark:text-white">Calculating Deterministic Decision Equations...</h4>
                  <p className="text-xs text-slate-400 dark:text-zinc-500 mt-1">Simulating queuing dynamics, capacity ratios, and cost implications.</p>
                </div>
              </Card>
            )}

            {simState === 'IDLE' && (
              <Card padding="lg" className="bg-white dark:bg-[#050505] border-2 border-dashed border-slate-200 dark:border-white/15 min-h-[420px] flex flex-col items-center justify-center space-y-3 text-center p-8">
                <div className="h-12 w-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                  <FlaskConical className="h-6 w-6" />
                </div>
                <h4 className="font-bold text-base text-slate-800 dark:text-zinc-200">Ready to Explore Scenarios</h4>
                <p className="text-xs text-slate-500 dark:text-zinc-400 max-w-md leading-relaxed">
                  Configure the scenario parameters on the left and click <strong>RUN SIMULATION</strong>.
                  All numbers are computed by deterministic backend formulas before AI comparative trade-off analysis.
                </p>
              </Card>
            )}

            {simState === 'RESULT' && simulationResult && (
              <div className="space-y-5 animate-fade-in">
                {/* Human Authority Notice Banner */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-900 dark:bg-[#0A0A0A] text-white text-xs shadow-md border border-transparent dark:border-white/10">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-indigo-400 shrink-0" />
                    <span className="font-semibold">{simulationResult.ai_explanation.human_authority_notice}</span>
                  </div>
                  <span className="text-[10px] font-bold text-indigo-300 dark:text-indigo-400 uppercase tracking-wider bg-indigo-900/60 dark:bg-indigo-950/60 px-2 py-0.5 rounded">
                    Human Authority
                  </span>
                </div>

                {/* Scenario Toggle Pills */}
                <div className="flex items-center justify-between bg-white dark:bg-[#050505] p-2.5 rounded-2xl border border-slate-200 dark:border-white/10">
                  <div className="flex items-center gap-2">
                    {simulationResult.scenarios.map((sc, i) => (
                      <button
                        key={sc.scenario_id}
                        onClick={() => setSelectedScenarioIdx(i)}
                        className={`px-3.5 py-1.5 rounded-xl font-bold text-xs transition-all ${
                          selectedScenarioIdx === i
                            ? 'bg-indigo-600 text-white shadow-sm'
                            : 'bg-slate-100 dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-[#161616]'
                        }`}
                      >
                        {sc.name}
                      </button>
                    ))}
                  </div>

                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={handleSaveScenario}
                    className="text-xs border-indigo-200 dark:border-indigo-800/40 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-50 dark:hover:bg-indigo-950/40"
                  >
                    <Bookmark className="h-3.5 w-3.5 mr-1" /> Save Scenario
                  </Button>
                </div>

                {saveSuccessMsg && (
                  <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 text-emerald-800 dark:text-emerald-300 text-xs font-semibold flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    {saveSuccessMsg}
                  </div>
                )}

                {/* Key Metric Comparison Cards */}
                {(() => {
                  const activeSc = simulationResult.scenarios[selectedScenarioIdx];
                  return (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {activeSc.metrics.slice(0, 3).map((m, idx) => {
                        const isBetter = m.trend_direction === 'BETTER';
                        return (
                          <Card key={idx} padding="md" className="bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
                            <span className="text-[11px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block truncate">
                              {m.name}
                            </span>
                            <div className="flex items-baseline gap-2 mt-1">
                              <span className="text-2xl font-black text-slate-900 dark:text-white">{m.scenario_value}</span>
                              <span className="text-xs text-slate-500 dark:text-zinc-400 font-medium">{m.unit}</span>
                            </div>
                            <div className="flex items-center gap-1 mt-1 text-xs">
                              {m.difference < 0 ? (
                                <span className={`font-bold flex items-center ${isBetter ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                                  <TrendingDown className="h-3.5 w-3.5 mr-0.5" /> {m.percentage_change}%
                                </span>
                              ) : (
                                <span className={`font-bold flex items-center ${isBetter ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                                  <TrendingUp className="h-3.5 w-3.5 mr-0.5" /> +{m.percentage_change}%
                                </span>
                              )}
                              <span className="text-[10px] text-slate-400 dark:text-zinc-500">vs {m.baseline_value} baseline</span>
                            </div>
                          </Card>
                        );
                      })}
                    </div>
                  );
                })()}

                {/* Side-by-Side Multi-Scenario Comparison Table */}
                <Card padding="md" className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 space-y-3">
                  <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 uppercase tracking-wider block">
                    Comparative Scenario Matrix
                  </span>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="border-b border-slate-100 dark:border-white/10 text-slate-400 dark:text-zinc-500 font-semibold">
                          <th className="py-2 pr-4">Metric</th>
                          <th className="py-2 px-3">Current Baseline</th>
                          {simulationResult.scenarios.map((sc) => (
                            <th key={sc.scenario_id} className="py-2 px-3 text-indigo-600 dark:text-indigo-400">{sc.name}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                        {simulationResult.scenarios[0].metrics.map((m, mIdx) => (
                          <tr key={mIdx}>
                            <td className="py-2.5 pr-4 font-semibold text-slate-700 dark:text-zinc-300">{m.name}</td>
                            <td className="py-2.5 px-3 text-slate-500 dark:text-zinc-400">{m.baseline_value} {m.unit}</td>
                            {simulationResult.scenarios.map((sc) => {
                              const scMetric = sc.metrics[mIdx];
                              return (
                                <td key={sc.scenario_id} className="py-2.5 px-3 font-bold text-slate-900 dark:text-white">
                                  {scMetric.scenario_value} {scMetric.unit}
                                  <span className="text-[10px] font-normal text-slate-400 dark:text-zinc-500 ml-1">
                                    ({scMetric.percentage_change && scMetric.percentage_change > 0 ? `+${scMetric.percentage_change}%` : `${scMetric.percentage_change}%`})
                                  </span>
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>

                {/* AI Comparative Trade-off Explanation */}
                <Card padding="lg" className="bg-indigo-50/50 dark:bg-gradient-to-br dark:from-[#0A0A0A] dark:to-[#050505] border border-indigo-100 dark:border-white/10 space-y-4">
                  <div className="flex items-center justify-between border-b border-indigo-100/60 dark:border-white/10 pb-2.5">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                      <h4 className="font-bold text-sm text-indigo-950 dark:text-white">AI Trade-off & Operational Analysis</h4>
                    </div>
                    <span className="text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-100 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full">
                      AI-Assisted Synthesis
                    </span>
                  </div>

                  <p className="text-xs text-indigo-900 dark:text-zinc-300 leading-relaxed font-medium">
                    {simulationResult.ai_explanation.summary}
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    {/* Positive Benefits */}
                    <div className="p-3 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-emerald-200 dark:border-emerald-900/40 space-y-1.5">
                      <span className="font-bold text-emerald-800 dark:text-emerald-400 block flex items-center gap-1">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" /> Modeled Benefits:
                      </span>
                      <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-zinc-400 text-[11px]">
                        {simulationResult.ai_explanation.benefits.map((b, i) => (
                          <li key={i}>{b}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Trade-offs & Risks */}
                    <div className="p-3 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-amber-200 dark:border-amber-900/40 space-y-1.5">
                      <span className="font-bold text-amber-800 dark:text-amber-400 block flex items-center gap-1">
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" /> Operational Trade-offs:
                      </span>
                      <ul className="list-disc list-inside space-y-1 text-slate-600 dark:text-zinc-400 text-[11px]">
                        {simulationResult.ai_explanation.tradeoffs.map((t, i) => (
                          <li key={i}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>

                {/* Assumptions & Limitations Accordion */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  {/* Assumptions */}
                  <div className="p-3.5 rounded-2xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 space-y-1.5">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 block flex items-center gap-1">
                      <Info className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" /> Model Assumptions:
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-slate-600 dark:text-zinc-400 text-[11px]">
                      {simulationResult.assumptions_summary.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Limitations */}
                  <div className="p-3.5 rounded-2xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 space-y-1.5">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 block flex items-center gap-1">
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" /> Prototype Limitations:
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-slate-600 dark:text-zinc-400 text-[11px]">
                      {simulationResult.limitations_summary.map((l, i) => (
                        <li key={i}>{l}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ManagementSimulationsPage;
