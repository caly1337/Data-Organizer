'use client';

import { formatBytes, formatNumber, formatRelativeTime, getStatusColor } from '@/lib/utils';
import type { Scan } from '@/lib/api';

interface ScanCardProps {
  scan: Scan;
  onClick?: () => void;
  onDelete?: (e: React.MouseEvent) => void;
}

export default function ScanCard({ scan, onClick, onDelete }: ScanCardProps) {
  return (
    <div
      onClick={onClick}
      className={`border rounded-lg p-4 hover:shadow-lg transition-shadow ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-lg truncate">{scan.path}</h3>
          <p className="text-sm text-gray-500">
            {formatRelativeTime(scan.started_at)}
          </p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
            scan.status
          )}`}
        >
          {scan.status}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-4">
        <div>
          <p className="text-sm text-gray-500">Files</p>
          <p className="text-xl font-semibold">{formatNumber(scan.total_files)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Directories</p>
          <p className="text-xl font-semibold">
            {formatNumber(scan.total_directories)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Size</p>
          <p className="text-xl font-semibold">{formatBytes(scan.total_size)}</p>
        </div>
      </div>

      {scan.error_message && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {scan.error_message}
        </div>
      )}

      {scan.errors_count > 0 && !scan.error_message && (
        <div className="mt-3 text-sm text-orange-600">
          {scan.errors_count} error{scan.errors_count > 1 ? 's' : ''} during scan
        </div>
      )}

      {onDelete && (
        <div className="mt-4 pt-3 border-t">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(e);
            }}
            className="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            Delete Scan
          </button>
        </div>
      )}
    </div>
  );
}
