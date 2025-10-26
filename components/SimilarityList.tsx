
import React from 'react';
import type { SimilarityResult } from '../types';
import { DocumentIcon } from './icons/DocumentIcon';

interface SimilarityListProps {
    similarities: SimilarityResult[];
    onSelect: (similarity: SimilarityResult) => void;
    selectedId: string;
}

const getLevelClasses = (level: string) => {
    switch (level) {
        case 'exact':
        case 'high':
            return 'bg-red-100 text-red-800';
        case 'moderate':
            return 'bg-orange-100 text-orange-800';
        case 'low':
            return 'bg-yellow-100 text-yellow-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
};


export const SimilarityList: React.FC<SimilarityListProps> = ({ similarities, onSelect, selectedId }) => {
    if(similarities.length === 0) {
        return (
             <div className="bg-white p-6 rounded-xl shadow-md h-full flex flex-col items-center justify-center text-center">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">No Significant Similarities Found</h3>
                <p className="text-gray-500">The document appears to be original based on the analyzed sources.</p>
            </div>
        )
    }

    return (
        <div className="bg-white p-4 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold text-gray-800 px-2 pb-2">Similar Sources</h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {similarities.map((sim) => (
                    <button
                        key={sim.matched_doc_id}
                        onClick={() => onSelect(sim)}
                        className={`w-full text-left p-3 rounded-lg transition-colors duration-200 ${selectedId === sim.matched_doc_id ? 'bg-primary-50' : 'hover:bg-gray-100'}`}
                    >
                        <div className="flex items-start space-x-4">
                             <DocumentIcon className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
                            <div className="flex-grow">
                                <div className="flex justify-between items-center">
                                    <p className="font-semibold text-gray-800 truncate">{sim.matched_doc_id}</p>
                                    <p className="font-bold text-lg text-gray-700">{Math.round(sim.similarity_score)}%</p>
                                </div>
                                <div className="flex items-center space-x-2 mt-1 text-sm">
                                    <span className={`px-2 py-0.5 rounded-full font-medium text-xs ${getLevelClasses(sim.similarity_level)}`}>
                                        {sim.similarity_level}
                                    </span>
                                     <span className="text-gray-500 capitalize">&#8226; {sim.type}</span>
                                </div>
                            </div>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
};
