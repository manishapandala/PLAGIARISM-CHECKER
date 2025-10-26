
import React from 'react';
import type { SimilarityResult } from '../types';

interface SummaryCardProps {
    overallScore: number;
    similarities: SimilarityResult[];
}

const getScoreColor = (score: number) => {
    if (score > 75) return 'text-red-500';
    if (score > 50) return 'text-orange-500';
    if (score > 10) return 'text-yellow-500';
    return 'text-green-500';
};

const getBackgroundColor = (score: number) => {
    if (score > 75) return 'bg-red-100';
    if (score > 50) return 'bg-orange-100';
    if (score > 10) return 'bg-yellow-100';
    return 'bg-green-100';
};

export const SummaryCard: React.FC<SummaryCardProps> = ({ overallScore, similarities }) => {
    const internalSources = similarities.filter(s => s.type === 'internal').length;
    const externalSources = similarities.filter(s => s.type === 'external').length;
    
    const scoreColor = getScoreColor(overallScore);
    const bgColor = getBackgroundColor(overallScore);

    return (
        <div className="bg-white p-6 rounded-xl shadow-md flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="flex items-center space-x-6">
                <div className={`w-24 h-24 rounded-full flex items-center justify-center ${bgColor}`}>
                    <span className={`text-4xl font-bold ${scoreColor}`}>{overallScore}%</span>
                </div>
                <div>
                    <h3 className="text-xl font-bold text-gray-800">Overall Similarity Score</h3>
                    <p className="text-gray-500">Highest similarity found across all sources.</p>
                </div>
            </div>
            <div className="flex space-x-8 text-center">
                <div>
                    <p className="text-2xl font-bold text-primary">{similarities.length}</p>
                    <p className="text-sm text-gray-500">Total Sources</p>
                </div>
                 <div>
                    <p className="text-2xl font-bold text-primary">{internalSources}</p>
                    <p className="text-sm text-gray-500">Internal Sources</p>
                </div>
                 <div>
                    <p className="text-2xl font-bold text-primary">{externalSources}</p>
                    <p className="text-sm text-gray-500">External Sources</p>
                </div>
            </div>
        </div>
    );
};
