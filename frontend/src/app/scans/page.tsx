'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient, { type Scan } from '@/lib/api';
import ScanCard from '@/components/ScanCard';
import { configStore } from '@/lib/store';

export default function ScansPage() {
  const router = useRouter();
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load config defaults
  const config = configStore.getConfig();

  // New scan form state
  const [showNewScan, setShowNewScan] = useState(false);
  const [newScanPath, setNewScanPath] = useState('/mnt/data');
  const [maxDepth, setMaxDepth] = useState(config.defaultMaxDepth);
  const [includeHidden, setIncludeHidden] = useState(config.defaultIncludeHidden);
  const [followSymlinks, setFollowSymlinks] = useState(config.defaultFollowSymlinks);

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
        include_hidden: includeHidden,
        follow_symlinks: followSymlinks,
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

  async function deleteScan(scanId: number) {
    if (!confirm('Are you sure you want to delete this scan? This cannot be undone.')) {
      return;
    }

    try {
      await apiClient.deleteScan(scanId);
      await loadScans();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scan');
    }
  }

  async function deleteAllScans(status?: string) {
    const statusText = status ? ` with status "${status}"` : '';
    if (!confirm(`Are you sure you want to delete ALL scans${statusText}? This cannot be undone.`)) {
      return;
    }

    try {
      const scansToDelete = status
        ? scans.filter(s => s.status === status)
        : scans;

      for (const scan of scansToDelete) {
        await apiClient.deleteScan(scan.id);
      }

      await loadScans();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scans');
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
          <div className="flex gap-3">
            {scans.length > 0 && (
              <div className="relative group">
                <button className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium">
                  🗑️ Cleanup
                </button>
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                  <button
                    onClick={() => deleteAllScans('failed')}
                    className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded-t-lg"
                  >
                    Delete Failed Scans
                  </button>
                  <button
                    onClick={() => deleteAllScans('completed')}
                    className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Delete Completed Scans
                  </button>
                  <button
                    onClick={() => deleteAllScans()}
                    className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded-b-lg text-red-600"
                  >
                    Delete ALL Scans
                  </button>
                </div>
              </div>
            )}
            <button
              onClick={() => setShowNewScan(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              + New Scan
            </button>
          </div>
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

              <div className="flex gap-6">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="includeHidden"
                    checked={includeHidden}
                    onChange={(e) => setIncludeHidden(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label htmlFor="includeHidden" className="text-sm">
                    Include hidden files
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="followSymlinks"
                    checked={followSymlinks}
                    onChange={(e) => setFollowSymlinks(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <label htmlFor="followSymlinks" className="text-sm">
                    Follow symlinks
                  </label>
                </div>
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
                onDelete={() => deleteScan(scan.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
