
import React, { useState, useCallback, useEffect } from 'react';
import { ResultsDisplay } from './components/ResultsDisplay';
import { Header } from './components/Header';
import { checkPlagiarism } from './services/geminiService';
import { EXTERNAL_KNOWLEDGE_BASE } from './constants';
import type { CheckResult, DocumentMetadata, StoredDocument } from './types';
import { extractTextFromFile } from './utils/fileReader';
import { Loader } from './components/Loader';
import { Dashboard } from './components/Dashboard';

const LOCAL_STORAGE_KEYS = {
    STORED_DOCS: 'plagiarism_checker_stored_docs',
    ALL_RESULTS: 'plagiarism_checker_all_results',
};

const safelyParseJSON = (item: string | null) => {
    if (!item) return null;
    try {
        return JSON.parse(item);
    } catch (error) {
        console.warn('Error parsing JSON from localStorage', error);
        return null;
    }
};

const App: React.FC = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const [storedDocuments, setStoredDocuments] = useState<StoredDocument[]>(
        () => safelyParseJSON(localStorage.getItem(LOCAL_STORAGE_KEYS.STORED_DOCS)) || []
    );
    const [allResults, setAllResults] = useState<Record<string, CheckResult>>(
        () => safelyParseJSON(localStorage.getItem(LOCAL_STORAGE_KEYS.ALL_RESULTS)) || {}
    );
    const [activeDocument, setActiveDocument] = useState<StoredDocument | null>(null);

    useEffect(() => {
        localStorage.setItem(LOCAL_STORAGE_KEYS.STORED_DOCS, JSON.stringify(storedDocuments));
    }, [storedDocuments]);

    useEffect(() => {
        localStorage.setItem(LOCAL_STORAGE_KEYS.ALL_RESULTS, JSON.stringify(allResults));
    }, [allResults]);

    const handleCheck = useCallback(async (file: File, metadata: DocumentMetadata) => {
        setIsLoading(true);
        setError(null);
        setActiveDocument(null);

        // Prevent duplicate docId
        if (storedDocuments.some(doc => doc.metadata.docId === metadata.docId)) {
             setError("A document with this ID already exists. Please use a unique Document ID.");
             setIsLoading(false);
             return;
        }

        try {
            const content = await extractTextFromFile(file);
            if (!content.trim()) {
                throw new Error("Could not extract text from the file or the file is empty.");
            }
            
            const newDocument: StoredDocument = { metadata, content, submissionDate: new Date().toISOString() };

            const comparisonDocs = [
                ...storedDocuments.map(doc => ({ id: doc.metadata.docId, content: doc.content, type: 'internal' as const })),
                ...EXTERNAL_KNOWLEDGE_BASE.map(doc => ({ ...doc, type: 'external' as const }))
            ];
            
            const plagiarismResults = await checkPlagiarism(content, comparisonDocs);
            
            setAllResults(prevResults => ({
                ...prevResults,
                [newDocument.metadata.docId]: plagiarismResults
            }));
            
            setStoredDocuments(prevDocs => [...prevDocs, newDocument]);
            setActiveDocument(newDocument);

        } catch (err) {
            console.error(err);
            setError(err instanceof Error ? err.message : 'An unknown error occurred.');
        } finally {
            setIsLoading(false);
        }
    }, [storedDocuments]);
    
    const handleViewHistory = (docId: string) => {
        const docToView = storedDocuments.find(d => d.metadata.docId === docId);
        if (docToView) {
            setActiveDocument(docToView);
            setError(null);
        }
    };

    const handleResetToDashboard = () => {
        setActiveDocument(null);
        setError(null);
    };

    const handleClearSession = () => {
        Object.values(LOCAL_STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
        setStoredDocuments([]);
        setAllResults({});
        setActiveDocument(null);
        setError(null);
    };


    const renderContent = () => {
        if (isLoading) {
            return <Loader message="Analyzing document... This may take a moment." />;
        }
        
        const activeResults = activeDocument ? allResults[activeDocument.metadata.docId] : null;

        if (activeDocument && activeResults) {
            return <ResultsDisplay results={activeResults} sourceDocument={activeDocument} onReset={handleResetToDashboard} />;
        }

        return (
            <>
             {error && (
                <div className="text-center mb-6">
                    <p className="text-red-500 bg-red-100 p-4 rounded-lg">{error}</p>
                </div>
            )}
            <Dashboard onCheck={handleCheck} storedDocuments={storedDocuments} onViewHistory={handleViewHistory} />
            </>
        )
    };

    return (
        <div className="min-h-screen font-sans">
            <Header onClearSession={handleClearSession} />
            <main className="container mx-auto px-4 py-8">
                {renderContent()}
            </main>
        </div>
    );
};

export default App;
