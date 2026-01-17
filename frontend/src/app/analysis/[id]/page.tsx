'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import apiClient, { type Analysis, type Recommendation } from '@/lib/api';
import RecommendationCard from '@/components/RecommendationCard';
import { formatDate, formatNumber, getStatusColor } from '@/lib/utils';

export default function AnalysisDetailPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = parseInt(params.id as string);

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysis();
    loadRecommendations();

    // WebSocket for real-time updates (optional with polling fallback)
    let ws: WebSocket | null = null;
    let pollInterval: NodeJS.Timeout | null = null;

    try {
      ws = apiClient.createAnalysisWebSocket(analysisId);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'analysis_update' || data.type === 'analysis_complete') {
          loadAnalysis();
          if (data.type === 'analysis_complete') {
            loadRecommendations();
          }
        }
      };

      ws.onerror = () => {
        // Fall back to polling
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(() => {
          loadAnalysis();
        }, 3000);
      };
    } catch (error) {
      // Use polling
      pollInterval = setInterval(() => {
        loadAnalysis();
      }, 3000);
    }

    return () => {
      if (ws) ws.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [analysisId]);

  async function loadAnalysis() {
    try {
      const data = await apiClient.getAnalysis(analysisId);
      setAnalysis(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analysis');
    } finally {
      setLoading(false);
    }
  }

  async function loadRecommendations() {
    try {
      const data = await apiClient.getAnalysisRecommendations(analysisId);
      setRecommendations(data);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    }
  }

  async function approveRecommendation(recId: number) {
    try {
      await apiClient.approveRecommendation(recId);
      await loadRecommendations();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve');
    }
  }

  async function rejectRecommendation(recId: number) {
    try {
      await apiClient.rejectRecommendation(recId);
      await loadRecommendations();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject');
    }
  }

  async function executeRecommendation(recId: number, dryRun = false) {
    try {
      const execution = await apiClient.createExecution({
        recommendation_id: recId,
        dry_run: dryRun,
      });
      router.push(`/execution/${execution.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-xl">Loading analysis...</div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-xl text-red-600">Analysis not found</div>
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
            onClick={() => router.push(`/scans/${analysis.scan_id}`)}
            className="text-blue-600 hover:underline mb-4"
          >
            ← Back to Scan
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold mb-2">Analysis #{analysis.id}</h1>
              <div className="flex items-center gap-3 text-lg">
                <span className="font-semibold">{analysis.provider}</span>
                <span className="text-gray-500">•</span>
                <span>{analysis.model}</span>
                <span className="text-gray-500">•</span>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-sm rounded">
                  {analysis.mode}
                </span>
              </div>
            </div>
            <span
              className={`px-4 py-2 rounded-full text-lg font-medium ${getStatusColor(
                analysis.status
              )}`}
            >
              {analysis.status}
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Analysis Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Duration</p>
            <p className="text-2xl font-bold">
              {analysis.duration ? `${analysis.duration.toFixed(1)}s` : 'N/A'}
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Tokens Used</p>
            <p className="text-2xl font-bold">{formatNumber(analysis.tokens_used || 0)}</p>
          </div>
          <div className="p-6 border rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Cost</p>
            <p className="text-2xl font-bold">
              {analysis.cost ? `$${analysis.cost.toFixed(4)}` : 'Free'}
            </p>
          </div>
        </div>

        {/* LLM Response */}
        {analysis.status === 'completed' && analysis.response && (
          <div className="mb-8 p-6 border rounded-lg bg-gray-50">
            <h3 className="text-xl font-semibold mb-4">AI Analysis</h3>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm">{analysis.response}</pre>
            </div>
          </div>
        )}

        {/* Recommendations */}
        <div>
          <h2 className="text-2xl font-bold mb-4">
            Recommendations ({recommendations.length})
          </h2>

          {recommendations.length === 0 ? (
            <div className="text-center py-8 border rounded-lg">
              <p className="text-gray-500">
                {analysis.status === 'completed'
                  ? 'No recommendations generated'
                  : 'Waiting for analysis to complete...'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {recommendations.map((rec) => (
                <RecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onApprove={() => approveRecommendation(rec.id)}
                  onReject={() => rejectRecommendation(rec.id)}
                  onExecute={() => executeRecommendation(rec.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
