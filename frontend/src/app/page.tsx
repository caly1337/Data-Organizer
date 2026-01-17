export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Data-Organizer</h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered filesystem analysis and optimization tool
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Scan</h2>
            <p className="text-gray-600">
              Analyze your filesystems with intelligent scanning
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Analyze</h2>
            <p className="text-gray-600">
              Get AI-powered insights using multiple LLM models
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Optimize</h2>
            <p className="text-gray-600">
              Execute recommendations safely with rollback support
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
