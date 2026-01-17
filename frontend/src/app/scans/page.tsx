'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient, { type Scan } from '@/lib/api';
import ScanCard from '@/components/ScanCard';

export default function ScansPage() {
  const router = useRouter();
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New scan form state
  const [showNewScan, setShowNewScan] = useState(false);
  const [newScanPath, setNewScanPath] = useState('/mnt/data');
  const [maxDepth, setMaxDepth] = useState(10);

  useEffect(() => {
    loadScans();
  }, []);

  async function loadScans() {
    try {
      setLoading(true);
      const response = await apiClient.listScans({ limit: 50 });
      setScans(response.scans);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scans');
    } finally {
      setLoading(false);
    }
  }

  async function createScan() {
    try {
      const scan = await apiClient.createScan({
        path: newScanPath,
        max_depth: maxDepth,
        include_hidden: false,
        follow_symlinks: false,
      });

      setShowNewScan(false);
      setNewScanPath('/mnt/data');
      await loadScans();

      // Navigate to scan detail
      router.push(`/scans/${scan.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create scan');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="text-xl">Loading scans...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold">Filesystem Scans</h1>
            <p className="text-gray-600 mt-2">
              Analyze and organize your filesystems with AI
            </p>
          </div>
          <button
            onClick={() => setShowNewScan(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + New Scan
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* New Scan Form */}
        {showNewScan && (
          <div className="mb-8 p-6 border-2 border-blue-200 rounded-lg bg-blue-50">
            <h2 className="text-2xl font-semibold mb-4">Create New Scan</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Directory Path
                </label>
                <input
                  type="text"
                  value={newScanPath}
                  onChange={(e) => setNewScanPath(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="/mnt/data/my-directory"
                />
                <p className="text-sm text-gray-600 mt-1">
                  Path must be mounted in Docker container
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Max Depth: {maxDepth}
                </label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={createScan}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Start Scan
                </button>
                <button
                  onClick={() => setShowNewScan(false)}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Scans List */}
        {scans.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-xl text-gray-500 mb-4">No scans yet</p>
            <button
              onClick={() => setShowNewScan(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Your First Scan
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scans.map((scan) => (
              <ScanCard
                key={scan.id}
                scan={scan}
                onClick={() => router.push(`/scans/${scan.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
