'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import apiClient, { type Scan, type Analysis } from '@/lib/api';
import { formatBytes, formatNumber, formatDate, getStatusColor } from '@/lib/utils';

export default function ScanDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scanId = parseInt(params.id as string);

  const [scan, setScan] = useState<Scan | null>(null);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Analysis form
  const [showNewAnalysis, setShowNewAnalysis] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedMode, setSelectedMode] = useState('fast');

  useEffect(() => {
    loadScan();
    loadAnalyses();

    // Set up WebSocket for real-time updates (optional)
    let ws: WebSocket | null = null;
    let pollInterval: NodeJS.Timeout | null = null;

    try {
      ws = apiClient.createScanWebSocket(scanId);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'scan_update' || data.type === 'scan_complete') {
          setScan(data.data);
        }
      };

      ws.onerror = () => {
        // Silently fall back to polling (WebSocket optional)
      };

      ws.onclose = () => {
        // WebSocket closed, use polling instead
        if (!pollInterval) {
          pollInterval = setInterval(() => {
            loadScan();
          }, 3000);
        }
      };
    } catch (error) {
      // WebSocket not available, use polling
      pollInterval = setInterval(() => {
        loadScan();
      }, 3000);
    }

    return () => {
      if (ws) ws.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [scanId]);

  async function loadScan() {
    try {
      const data = await apiClient.getScan(scanId, false);
      setScan(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scan');
    } finally {
      setLoading(false);
    }
  }

  async function loadAnalyses() {
    try {
      const data = await apiClient.getScanAnalyses(scanId);
      setAnalyses(data);
    } catch (err) {
      console.error('Failed to load analyses:', err);
    }
  }

  async function createAnalysis() {
    try {
      const analysis = await apiClient.createAnalysis({
        scan_id: scanId,
        provider: selectedProvider,
        mode: selectedMode,
      });

      setShowNewAnalysis(false);
      router.push(`/analysis/${analysis.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create analysis');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-xl">Loading scan...</div>
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-xl text-red-600">Scan not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/scans')}
            className="text-blue-600 hover:underline mb-4"
          >
            ← Back to Scans
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold mb-2">Scan #{scan.id}</h1>
              <p className="text-xl text-gray-600">{scan.path}</p>
            </div>
            <span
              className={`px-4 py-2 rounded-full text-lg font-medium ${getStatusColor(
                scan.status
              )}`}
            >
              {scan.status}
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Total Files</p>
            <p className="text-3xl font-bold">{formatNumber(scan.total_files)}</p>
          </div>
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Directories</p>
            <p className="text-3xl font-bold">{formatNumber(scan.total_directories)}</p>
          </div>
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Total Size</p>
            <p className="text-3xl font-bold">{formatBytes(scan.total_size)}</p>
          </div>
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Started</p>
            <p className="text-lg font-semibold">{formatDate(scan.started_at)}</p>
          </div>
        </div>

        {/* Analyses Section */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">AI Analyses</h2>
            {scan.status === 'completed' && (
              <button
                onClick={() => setShowNewAnalysis(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                + New Analysis
              </button>
            )}
          </div>

          {/* New Analysis Form */}
          {showNewAnalysis && (
            <div className="mb-6 p-6 border-2 border-blue-200 rounded-lg bg-blue-50">
              <h3 className="text-xl font-semibold mb-4">Create Analysis</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Provider</label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="ollama">Ollama (Local - Fast & Free)</option>
                    <option value="gemini">Gemini (Cloud - Deep Analysis)</option>
                    <option value="claude">Claude (Cloud - Advanced)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Mode</label>
                  <select
                    value={selectedMode}
                    onChange={(e) => setSelectedMode(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="fast">Fast (~10s)</option>
                    <option value="deep">Deep (~30s)</option>
                    <option value="comparison">Comparison (Multiple Models)</option>
                  </select>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={createAnalysis}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Start Analysis
                  </button>
                  <button
                    onClick={() => setShowNewAnalysis(false)}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Analyses List */}
          {analyses.length === 0 ? (
            <div className="text-center py-8 border rounded-lg">
              <p className="text-gray-500 mb-4">No analyses yet</p>
              {scan.status === 'completed' && (
                <button
                  onClick={() => setShowNewAnalysis(true)}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create First Analysis
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {analyses.map((analysis) => (
                <div
                  key={analysis.id}
                  onClick={() => router.push(`/analysis/${analysis.id}`)}
                  className="p-4 border rounded-lg hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold">{analysis.provider}</span>
                        <span className="text-gray-500">({analysis.model})</span>
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                          {analysis.mode}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{formatDate(analysis.created_at)}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                        analysis.status
                      )}`}
                    >
                      {analysis.status}
                    </span>
                  </div>

                  {analysis.status === 'completed' && (
                    <div className="mt-3 flex gap-4 text-sm">
                      <span>Duration: {analysis.duration?.toFixed(1)}s</span>
                      <span>Tokens: {formatNumber(analysis.tokens_used || 0)}</span>
                      {analysis.cost && analysis.cost > 0 && (
                        <span>Cost: ${analysis.cost.toFixed(4)}</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
