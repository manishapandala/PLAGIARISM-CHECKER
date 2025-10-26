
import React from 'react';
import { UploadForm } from './UploadForm';
import { DocumentList } from './DocumentList';
import type { DocumentMetadata, StoredDocument } from '../types';

interface DashboardProps {
    onCheck: (file: File, metadata: DocumentMetadata) => void;
    storedDocuments: StoredDocument[];
    onViewHistory: (docId: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onCheck, storedDocuments, onViewHistory }) => {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
            <div className="lg:col-span-3">
                <UploadForm onCheck={onCheck} />
            </div>
            <div className="lg:col-span-2">
                <DocumentList documents={storedDocuments} onViewHistory={onViewHistory} />
            </div>
        </div>
    );
};
