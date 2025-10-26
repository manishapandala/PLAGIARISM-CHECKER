
import React, { useState, useEffect } from 'react';
import type { CheckResult, StoredDocument, SimilarityResult } from '../types';
import { SummaryCard } from './SummaryCard';
import { SimilarityList } from './SimilarityList';
import { ComparisonView } from './ComparisonView';
import { Visualizations } from './Visualizations';

interface ResultsDisplayProps {
    results: CheckResult;
    sourceDocument: StoredDocument;
    onReset: () => void;
}

type Tab = 'details' | 'visualizations';

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, sourceDocument, onReset }) => {
    const [selectedSimilarity, setSelectedSimilarity] = useState<SimilarityResult | null>(null);
    const [activeTab, setActiveTab] = useState<Tab>('details');

    useEffect(() => {
        // Automatically select the first similarity result when the results change
        if (results && results.similarities.length > 0) {
            setSelectedSimilarity(results.similarities[0]);
        } else {
            setSelectedSimilarity(null);
        }
        // Reset to details tab when results change
        setActiveTab('details');
    }, [results]);

    const handleSelectSimilarity = (similarity: SimilarityResult) => {
        setSelectedSimilarity(similarity);
        setActiveTab('details');
    };

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-3xl font-bold text-gray-800">Analysis Report</h2>
                    <p className="text-md text-gray-500 mt-1">
                        For: <span className="font-semibold text-gray-700">{sourceDocument.metadata.filename}</span>
                    </p>
                </div>
                 <button 
                    onClick={onReset}
                    className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                    Check Another Document
                </button>
            </div>
            
            <SummaryCard overallScore={results.overallScore} similarities={results.similarities} />
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1">
                    <SimilarityList
                        similarities={results.similarities}
                        onSelect={handleSelectSimilarity}
                        selectedId={selectedSimilarity?.matched_doc_id || ''}
                    />
                </div>
                <div className="lg:col-span-2 bg-white rounded-xl shadow-md overflow-hidden">
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-6 px-6">
                            <button
                                onClick={() => setActiveTab('details')}
                                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'details' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                            >
                                Detailed Comparison
                            </button>
                            <button
                                onClick={() => setActiveTab('visualizations')}
                                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'visualizations' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                            >
                                Visualizations
                            </button>
                        </nav>
                    </div>

                    <div className="p-6">
                        {activeTab === 'details' ? (
                            selectedSimilarity ? (
                                <ComparisonView
                                    sourceContent={sourceDocument.content}
                                    similarity={selectedSimilarity}
                                />
                            ) : (
                                <div className="flex items-center justify-center h-96 text-gray-500">
                                    <p>Select a document from the list to see the detailed comparison.</p>
                                </div>
                            )
                        ) : (
                            <Visualizations results={results} sourceDocId={sourceDocument.metadata.docId} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
