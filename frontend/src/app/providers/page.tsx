'use client';

import { useEffect, useState } from 'react';
import apiClient, { type Provider } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

export default function ProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, any>>({});

  useEffect(() => {
    loadProviders();
    loadStats();
  }, []);

  async function loadProviders() {
    try {
      const data = await apiClient.listProviders();
      setProviders(data);
    } catch (err) {
      console.error('Failed to load providers:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadStats() {
    try {
      const data = await apiClient.getProviderStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  }

  async function testProvider(providerName: string) {
    setTesting(providerName);
    try {
      const result = await apiClient.testProvider(providerName);
      setTestResults((prev) => ({ ...prev, [providerName]: result }));
    } catch (err) {
      setTestResults((prev) => ({
        ...prev,
        [providerName]: { status: 'error', error: String(err) },
      }));
    } finally {
      setTesting(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-xl">Loading providers...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">LLM Providers</h1>
        <p className="text-xl text-gray-600 mb-8">
          Multi-model AI support for intelligent filesystem analysis
        </p>

        {/* Overall Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="p-6 border rounded-lg bg-blue-50">
              <p className="text-sm text-gray-600 mb-1">Total Requests</p>
              <p className="text-3xl font-bold">{formatNumber(stats.total_requests)}</p>
            </div>
            <div className="p-6 border rounded-lg bg-green-50">
              <p className="text-sm text-gray-600 mb-1">Total Tokens</p>
              <p className="text-3xl font-bold">{formatNumber(stats.total_tokens)}</p>
            </div>
            <div className="p-6 border rounded-lg bg-purple-50">
              <p className="text-sm text-gray-600 mb-1">Total Cost</p>
              <p className="text-3xl font-bold">${stats.total_cost.toFixed(2)}</p>
            </div>
            <div className="p-6 border rounded-lg bg-orange-50">
              <p className="text-sm text-gray-600 mb-1">Active Providers</p>
              <p className="text-3xl font-bold">{stats.total_providers}</p>
            </div>
          </div>
        )}

        {/* Providers */}
        <div className="space-y-6">
          {providers.map((provider) => (
            <div key={provider.name} className="border rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-2xl font-bold">{provider.name}</h3>
                    <span
                      className={`px-3 py-1 rounded-full text-sm ${
                        provider.enabled
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {provider.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                      {provider.type}
                    </span>
                  </div>
                  <p className="text-gray-600 mt-1">Model: {provider.model}</p>
                </div>
                <button
                  onClick={() => testProvider(provider.name)}
                  disabled={testing === provider.name || !provider.enabled}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    provider.enabled
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {testing === provider.name ? 'Testing...' : 'Test'}
                </button>
              </div>

              {/* Test Results */}
              {testResults[provider.name] && (
                <div
                  className={`mb-4 p-4 rounded-lg ${
                    testResults[provider.name].status === 'success'
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-red-50 border border-red-200'
                  }`}
                >
                  {testResults[provider.name].status === 'success' ? (
                    <div>
                      <p className="font-medium text-green-800 mb-2">✓ Test Successful</p>
                      <p className="text-sm text-gray-700">
                        {testResults[provider.name].response}
                      </p>
                      <div className="mt-2 text-sm text-gray-600">
                        Duration: {testResults[provider.name].duration?.toFixed(2)}s
                        {testResults[provider.name].tokens_used && (
                          <> • Tokens: {testResults[provider.name].tokens_used}</>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="font-medium text-red-800 mb-2">✗ Test Failed</p>
                      <p className="text-sm text-red-700">
                        {testResults[provider.name].error}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Requests</p>
                  <p className="text-lg font-semibold">
                    {formatNumber(provider.total_requests)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Tokens</p>
                  <p className="text-lg font-semibold">
                    {formatNumber(provider.total_tokens)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Cost</p>
                  <p className="text-lg font-semibold">${provider.total_cost.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Success Rate</p>
                  <p className="text-lg font-semibold">
                    {(provider.success_rate * 100).toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Avg Response</p>
                  <p className="text-lg font-semibold">
                    {provider.avg_response_time.toFixed(1)}s
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Info */}
        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h3 className="text-lg font-semibold mb-2">Provider Configuration</h3>
          <p className="text-gray-700 mb-3">
            LLM providers are configured in the backend <code className="bg-white px-2 py-1 rounded">backend/.env</code> file.
          </p>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• <strong>Ollama</strong>: Configure OLLAMA_BASE_URL and OLLAMA_DEFAULT_MODEL</li>
            <li>• <strong>Gemini</strong>: Set GEMINI_ENABLED=true and GEMINI_API_KEY</li>
            <li>• <strong>Claude</strong>: Set CLAUDE_ENABLED=true and CLAUDE_API_KEY</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
