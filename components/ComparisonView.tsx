
import React from 'react';
import type { SimilarityResult } from '../types';

interface ComparisonViewProps {
    sourceContent: string;
    similarity: SimilarityResult;
}

const HighlightedText: React.FC<{ content: string; matchedLines: string[] }> = ({ content, matchedLines }) => {
    if (!matchedLines || matchedLines.length === 0) {
        return <p>{content}</p>;
    }

    // Create a regex to find all matched lines
    const regex = new RegExp(`(${matchedLines.map(line => line.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')).join('|')})`, 'gi');
    
    const parts = content.split(regex);

    return (
        <span>
            {parts.map((part, index) => {
                const isMatch = matchedLines.some(line => part.toLowerCase() === line.toLowerCase());
                return isMatch ? (
                    <mark key={index} className="bg-yellow-200 px-1 rounded">
                        {part}
                    </mark>
                ) : (
                    <span key={index}>{part}</span>
                );
            })}
        </span>
    );
};


export const ComparisonView: React.FC<ComparisonViewProps> = ({ sourceContent, similarity }) => {
    const sourceMatchedLines = similarity.matched_lines.map(l => l.source_text);
    const comparisonMatchedLines = similarity.matched_lines.map(l => l.match_text);

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-bold text-gray-800">Comparison with <span className="text-primary">{similarity.matched_doc_id}</span></h3>
                <p className="text-gray-500">Highlighted sections indicate detected similarities.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <h4 className="font-semibold text-gray-700">Your Document</h4>
                    <div className="prose prose-sm max-w-none p-4 border rounded-md h-96 overflow-y-auto bg-gray-50">
                        <HighlightedText content={sourceContent} matchedLines={sourceMatchedLines} />
                    </div>
                </div>
                <div className="space-y-2">
                    <h4 className="font-semibold text-gray-700">Matched Source</h4>
                     <div className="prose prose-sm max-w-none p-4 border rounded-md h-96 overflow-y-auto bg-gray-50">
                        <HighlightedText content={similarity.retrieved_context || 'Content not available.'} matchedLines={comparisonMatchedLines} />
                    </div>
                </div>
            </div>
        </div>
    );
};
