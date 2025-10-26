
import React from 'react';
import type { StoredDocument } from '../types';
import { DocumentIcon } from './icons/DocumentIcon';

interface DocumentListProps {
    documents: StoredDocument[];
    onViewHistory: (docId: string) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, onViewHistory }) => {
    return (
        <div className="bg-white p-6 rounded-xl shadow-md h-full">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Document History</h3>
            {documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center text-center text-gray-500 h-full py-16 border-2 border-dashed rounded-lg">
                    <DocumentIcon className="w-16 h-16 text-gray-300 mb-4" />
                    <p className="font-semibold">No documents uploaded yet.</p>
                    <p className="text-sm">Uploaded documents will appear here. Click one to view its past report.</p>
                </div>
            ) : (
                <div className="space-y-3 max-h-[450px] overflow-y-auto pr-2">
                    {documents.slice().reverse().map((doc, index) => (
                        <button 
                            key={`${doc.metadata.docId}-${index}`} 
                            className="w-full text-left p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-primary-50 hover:border-primary-200 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
                            onClick={() => onViewHistory(doc.metadata.docId)}
                        >
                           <div className="flex justify-between items-center">
                                 <p className="font-semibold text-primary truncate" title={doc.metadata.filename}>
                                    {doc.metadata.docId}
                                </p>
                                <p className="text-xs text-gray-500 flex-shrink-0 ml-2">
                                    {new Date(doc.submissionDate).toLocaleString()}
                                </p>
                           </div>
                            <p className="text-sm text-gray-600 truncate">{doc.metadata.filename}</p>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};
