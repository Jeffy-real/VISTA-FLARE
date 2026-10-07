import { CareerRecommendation } from '../types';
import { Trophy, Star, TrendingUp } from 'lucide-react';

interface RecommendationCardProps {
  recommendation: CareerRecommendation;
}

const RANK_ICONS = {
  1: { icon: Trophy, color: 'text-yellow-500', bg: 'bg-yellow-50 border-yellow-200' },
  2: { icon: Star, color: 'text-gray-400', bg: 'bg-gray-50 border-gray-200' },
  3: { icon: TrendingUp, color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
};

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const rankStyle = RANK_ICONS[recommendation.rank as keyof typeof RANK_ICONS] || RANK_ICONS[3];
  const Icon = rankStyle.icon;
  const percentage = Math.round(recommendation.score * 100);

  return (
    <div className={`relative p-5 rounded-xl border-2 ${rankStyle.bg} animate-fade-in`}>
      {/* Rank Badge */}
      <div className="absolute -top-3 -left-3">
        <div className={`flex items-center justify-center w-8 h-8 rounded-full bg-white shadow-md ${rankStyle.color}`}>
          <span className="font-bold text-lg">{recommendation.rank}</span>
        </div>
      </div>

      {/* Role Name */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 pr-8">{recommendation.role}</h3>
        <Icon className={`h-5 w-5 ${rankStyle.color} flex-shrink-0`} />
      </div>

      {/* Score Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Match Score</span>
          <span className="font-semibold text-gray-900">{percentage}%</span>
        </div>
        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Raw Score */}
      <p className="mt-2 text-xs text-gray-500 text-right">
        Confidence: {(recommendation.score * 100).toFixed(2)}%
      </p>
    </div>
  );
}
