'use client';

import { getConfidenceColor, getStatusColor } from '@/lib/utils';
import type { Recommendation } from '@/lib/api';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onApprove?: () => void;
  onReject?: () => void;
  onExecute?: () => void;
}

export default function RecommendationCard({
  recommendation,
  onApprove,
  onReject,
  onExecute,
}: RecommendationCardProps) {
  const confidencePercent = (recommendation.confidence * 100).toFixed(0);

  return (
    <div className="border rounded-lg p-5 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
              {recommendation.type}
            </span>
            <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded">
              {recommendation.action}
            </span>
          </div>
          <h3 className="font-semibold text-lg mt-2">{recommendation.title}</h3>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
              recommendation.status
            )}`}
          >
            {recommendation.status}
          </span>
          <span className={`text-sm font-medium ${getConfidenceColor(recommendation.confidence)}`}>
            {confidencePercent}% confident
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-700 mb-3">{recommendation.description}</p>

      {/* Reasoning */}
      {recommendation.reasoning && (
        <div className="mb-3 p-3 bg-gray-50 rounded text-sm">
          <p className="font-medium text-gray-700 mb-1">Reasoning:</p>
          <p className="text-gray-600">{recommendation.reasoning}</p>
        </div>
      )}

      {/* Stats */}
      <div className="flex gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500">Affected Files:</span>
          <span className="ml-2 font-semibold">{recommendation.affected_count}</span>
        </div>
        <div>
          <span className="text-gray-500">Priority:</span>
          <span className="ml-2 font-semibold">{recommendation.priority}/10</span>
        </div>
        {recommendation.impact_score && (
          <div>
            <span className="text-gray-500">Impact:</span>
            <span className="ml-2 font-semibold">
              {(recommendation.impact_score * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      {recommendation.status === 'pending' && (
        <div className="flex gap-2">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={onReject}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Reject
            </button>
          )}
        </div>
      )}

      {recommendation.status === 'approved' && onExecute && (
        <div className="flex gap-2">
          <button
            onClick={onExecute}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Execute
          </button>
          <button
            onClick={() => onExecute && onExecute()}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
          >
            Dry Run
          </button>
        </div>
      )}
    </div>
  );
}
