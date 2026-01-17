'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient, { type Provider } from '@/lib/api';
import { configStore, type AppConfig } from '@/lib/store';

export default function SettingsPage() {
  const router = useRouter();
  const [config, setConfig] = useState<AppConfig>(configStore.getConfig());
  const [providers, setProviders] = useState<Provider[]>([]);
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({});
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadProviders();
    loadModels();
  }, []);

  async function loadProviders() {
    try {
      const data = await apiClient.listProviders();
      setProviders(data);
    } catch (err) {
      console.error('Failed to load providers:', err);
    }
  }

  async function loadModels() {
    const providerNames = ['ollama', 'gemini', 'claude'];
    const models: Record<string, string[]> = {};

    for (const provider of providerNames) {
      try {
        const result = await apiClient.getProviderModels(provider);
        models[provider] = result.models;
      } catch (err) {
        console.error(`Failed to load models for ${provider}:`, err);
        models[provider] = [];
      }
    }

    setAvailableModels(models);
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

  function updateConfig(updates: Partial<AppConfig>) {
    const updated = { ...config, ...updates };
    setConfig(updated);
    configStore.saveConfig(updated);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function resetToDefaults() {
    configStore.resetConfig();
    const defaults = configStore.getConfig();
    setConfig(defaults);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="text-blue-600 hover:underline mb-4"
          >
            ← Back to Home
          </button>
          <h1 className="text-4xl font-bold mb-2">Settings</h1>
          <p className="text-xl text-gray-600">
            Configure your Data-Organizer preferences
          </p>
        </div>

        {saved && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            ✓ Settings saved successfully!
          </div>
        )}

        {/* LLM Provider Settings */}
        <div className="mb-8 p-6 border rounded-lg">
          <h2 className="text-2xl font-bold mb-4">LLM Provider Configuration</h2>

          {/* Default Provider */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">
              Default Provider
            </label>
            <select
              value={config.defaultProvider}
              onChange={(e) => updateConfig({ defaultProvider: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg"
            >
              {providers.filter(p => p.enabled).map((provider) => (
                <option key={provider.name} value={provider.name}>
                  {provider.name} ({provider.type})
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-500 mt-1">
              Default LLM provider for new analyses
            </p>
          </div>

          {/* Ollama Settings */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <span>Ollama (Local)</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                Free
              </span>
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Default Model
                </label>
                <select
                  value={config.ollamaModel}
                  onChange={(e) => updateConfig({ ollamaModel: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  {availableModels.ollama?.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => testProvider('ollama')}
                disabled={testing === 'ollama'}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                {testing === 'ollama' ? 'Testing...' : 'Test Connection'}
              </button>

              {testResults.ollama && (
                <div
                  className={`p-3 rounded-lg ${
                    testResults.ollama.status === 'success'
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-red-50 border border-red-200'
                  }`}
                >
                  {testResults.ollama.status === 'success' ? (
                    <div>
                      <p className="font-medium text-green-800 mb-1">✓ Connected</p>
                      <p className="text-sm text-gray-700">{testResults.ollama.response}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        {testResults.ollama.duration?.toFixed(2)}s
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="font-medium text-red-800 mb-1">✗ Failed</p>
                      <p className="text-sm text-red-700">{testResults.ollama.error}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Gemini Settings */}
          <div className="mb-6 p-4 bg-purple-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <span>Gemini (Cloud)</span>
              <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                Paid API
              </span>
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Default Model
                </label>
                <select
                  value={config.geminiModel}
                  onChange={(e) => updateConfig({ geminiModel: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                >
                  {availableModels.gemini?.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => testProvider('gemini')}
                disabled={testing === 'gemini'}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
              >
                {testing === 'gemini' ? 'Testing...' : 'Test Connection'}
              </button>

              {testResults.gemini && (
                <div
                  className={`p-3 rounded-lg ${
                    testResults.gemini.status === 'success'
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-red-50 border border-red-200'
                  }`}
                >
                  {testResults.gemini.status === 'success' ? (
                    <div>
                      <p className="font-medium text-green-800 mb-1">✓ Connected</p>
                      <p className="text-sm text-gray-700">{testResults.gemini.response}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        {testResults.gemini.duration?.toFixed(2)}s •
                        ${testResults.gemini.cost?.toFixed(4)} cost
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="font-medium text-red-800 mb-1">✗ Failed</p>
                      <p className="text-sm text-red-700">{testResults.gemini.error}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Analysis Settings */}
        <div className="mb-8 p-6 border rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Analysis Preferences</h2>

          <div className="space-y-6">
            {/* Default Mode */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Default Analysis Mode
              </label>
              <select
                value={config.defaultMode}
                onChange={(e) => updateConfig({ defaultMode: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg"
              >
                <option value="fast">Fast (~10s) - Quick insights</option>
                <option value="deep">Deep (~30s) - Comprehensive analysis</option>
                <option value="comparison">Comparison - Multi-model</option>
              </select>
            </div>
          </div>
        </div>

        {/* Scan Settings */}
        <div className="mb-8 p-6 border rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Scan Defaults</h2>

          <div className="space-y-6">
            {/* Max Depth */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Default Max Depth: {config.defaultMaxDepth}
              </label>
              <input
                type="range"
                min="1"
                max="20"
                value={config.defaultMaxDepth}
                onChange={(e) => updateConfig({ defaultMaxDepth: parseInt(e.target.value) })}
                className="w-full"
              />
              <p className="text-sm text-gray-500 mt-1">
                How deep to scan directory structures
              </p>
            </div>

            {/* Include Hidden */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="includeHidden"
                checked={config.defaultIncludeHidden}
                onChange={(e) => updateConfig({ defaultIncludeHidden: e.target.checked })}
                className="w-5 h-5"
              />
              <label htmlFor="includeHidden" className="text-sm font-medium">
                Include hidden files by default
              </label>
            </div>

            {/* Follow Symlinks */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="followSymlinks"
                checked={config.defaultFollowSymlinks}
                onChange={(e) => updateConfig({ defaultFollowSymlinks: e.target.checked })}
                className="w-5 h-5"
              />
              <label htmlFor="followSymlinks" className="text-sm font-medium">
                Follow symbolic links by default
              </label>
            </div>
          </div>
        </div>

        {/* UI Settings */}
        <div className="mb-8 p-6 border rounded-lg">
          <h2 className="text-2xl font-bold mb-4">UI Preferences</h2>

          <div className="space-y-6">
            {/* WebSocket */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="enableWebSocket"
                checked={config.enableWebSocket}
                onChange={(e) => updateConfig({ enableWebSocket: e.target.checked })}
                className="w-5 h-5"
              />
              <label htmlFor="enableWebSocket" className="text-sm font-medium">
                Enable WebSocket for real-time updates
              </label>
            </div>
            <p className="text-sm text-gray-500 ml-8 -mt-4">
              If disabled, uses polling instead (every {config.autoRefreshInterval}s)
            </p>

            {/* Auto-refresh Interval */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Auto-refresh Interval: {config.autoRefreshInterval}s
              </label>
              <input
                type="range"
                min="2"
                max="30"
                value={config.autoRefreshInterval}
                onChange={(e) => updateConfig({ autoRefreshInterval: parseInt(e.target.value) })}
                className="w-full"
              />
              <p className="text-sm text-gray-500 mt-1">
                How often to refresh data when not using WebSocket
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={resetToDefaults}
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Reset to Defaults
          </button>

          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Done
          </button>
        </div>

        {/* Info */}
        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> Settings are saved locally in your browser.
            Backend configuration (API keys, URLs) must be changed in the backend/.env file.
          </p>
        </div>
      </div>
    </div>
  );
}
