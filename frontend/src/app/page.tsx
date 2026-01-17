'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4">Data-Organizer</h1>
          <p className="text-2xl text-gray-600 mb-8">
            AI-powered filesystem analysis and optimization tool
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/scans"
              className="px-8 py-4 bg-blue-600 text-white text-lg rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Start Scanning
            </Link>
            <a
              href="http://localhost:8004/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-gray-200 text-gray-800 text-lg rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              API Docs
            </a>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="p-8 border rounded-lg hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">🔍</div>
            <h2 className="text-2xl font-semibold mb-3">Scan</h2>
            <p className="text-gray-600 mb-4">
              Analyze your filesystems with intelligent scanning. Extract metadata,
              detect duplicates, and categorize files automatically.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Fast recursive scanning</li>
              <li>• File hashing for deduplication</li>
              <li>• Automatic categorization</li>
            </ul>
          </div>

          <div className="p-8 border rounded-lg hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">🤖</div>
            <h2 className="text-2xl font-semibold mb-3">Analyze</h2>
            <p className="text-gray-600 mb-4">
              Get AI-powered insights using multiple LLM models. Choose between
              fast local analysis or deep cloud-based reasoning.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Ollama (local & free)</li>
              <li>• Gemini (cloud & powerful)</li>
              <li>• Multi-model comparison</li>
            </ul>
          </div>

          <div className="p-8 border rounded-lg hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-4">✨</div>
            <h2 className="text-2xl font-semibold mb-3">Optimize</h2>
            <p className="text-gray-600 mb-4">
              Execute recommendations safely with rollback support. Preview changes
              before applying them to your filesystem.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Dry-run mode</li>
              <li>• Full rollback capability</li>
              <li>• Safe file operations</li>
            </ul>
          </div>
        </div>

        {/* Workflow */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
          <div className="flex flex-col md:flex-row gap-6 items-center justify-center">
            <div className="flex-1 text-center p-6 border rounded-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">1</div>
              <h3 className="text-xl font-semibold mb-2">Create Scan</h3>
              <p className="text-gray-600">
                Select a directory to analyze and start the scan
              </p>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="flex-1 text-center p-6 border rounded-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">2</div>
              <h3 className="text-xl font-semibold mb-2">AI Analysis</h3>
              <p className="text-gray-600">
                Choose an LLM provider to analyze your files
              </p>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="flex-1 text-center p-6 border rounded-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">3</div>
              <h3 className="text-xl font-semibold mb-2">Review & Execute</h3>
              <p className="text-gray-600">
                Review recommendations and apply changes safely
              </p>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="bg-gray-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-4">Quick Links</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link
              href="/scans"
              className="p-4 bg-white border rounded-lg hover:shadow transition-shadow text-center"
            >
              <div className="text-2xl mb-2">📁</div>
              <div className="font-medium">My Scans</div>
            </Link>
            <a
              href="http://localhost:8004/docs"
              target="_blank"
              className="p-4 bg-white border rounded-lg hover:shadow transition-shadow text-center"
            >
              <div className="text-2xl mb-2">📖</div>
              <div className="font-medium">API Docs</div>
            </a>
            <a
              href="https://github.com/caly1337"
              target="_blank"
              className="p-4 bg-white border rounded-lg hover:shadow transition-shadow text-center"
            >
              <div className="text-2xl mb-2">💻</div>
              <div className="font-medium">GitHub</div>
            </a>
            <Link
              href="/providers"
              className="p-4 bg-white border rounded-lg hover:shadow transition-shadow text-center"
            >
              <div className="text-2xl mb-2">🤖</div>
              <div className="font-medium">LLM Providers</div>
            </Link>
            <Link
              href="/settings"
              className="p-4 bg-white border rounded-lg hover:shadow transition-shadow text-center"
            >
              <div className="text-2xl mb-2">⚙️</div>
              <div className="font-medium">Settings</div>
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
