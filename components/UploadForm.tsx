import React, { useState, useCallback, useRef } from 'react';
import type { DocumentMetadata } from '../types';
import { UploadIcon } from './icons/UploadIcon';
import { DocumentIcon } from './icons/DocumentIcon';

interface UploadFormProps {
    onCheck: (file: File, metadata: DocumentMetadata) => void;
}

const ALLOWED_MIME_TYPES = [
    'text/plain',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];
const ALLOWED_EXTENSIONS = ['txt', 'pdf', 'docx'];

const isFileAllowed = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    // Some browsers might not report the correct MIME type for docx, so we also check extension
    return ALLOWED_MIME_TYPES.includes(file.type) || (extension && ALLOWED_EXTENSIONS.includes(extension));
};


export const UploadForm: React.FC<UploadFormProps> = ({ onCheck }) => {
    const [file, setFile] = useState<File | null>(null);
    const [metadata, setMetadata] = useState<Omit<DocumentMetadata, 'filename'>>({
        docId: '',
        assignmentId: '',
        courseId: ''
    });
    const [error, setError] = useState<string>('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setMetadata(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (!isFileAllowed(selectedFile)) {
                setError('Invalid file type. Please upload a .txt, .pdf, or .docx file.');
                setFile(null);
            } else {
                setFile(selectedFile);
                setError('');
            }
        }
    };
    
    const handleDragOver = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDrop = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
             const droppedFile = e.dataTransfer.files[0];
            if (!isFileAllowed(droppedFile)) {
                setError('Invalid file type. Please upload a .txt, .pdf, or .docx file.');
                setFile(null);
            } else {
                setFile(droppedFile);
                setError('');
                if (fileInputRef.current) {
                    fileInputRef.current.files = e.dataTransfer.files;
                }
            }
        }
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!file || !metadata.docId || !metadata.assignmentId || !metadata.courseId) {
            setError('All fields and a file are required.');
            return;
        }
        setError('');
        onCheck(file, { ...metadata, filename: file.name });
    };

    return (
        <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Check Document for Plagiarism</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <input type="text" name="docId" placeholder="Document ID" onChange={handleInputChange} className="col-span-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent transition" required />
                    <input type="text" name="assignmentId" placeholder="Assignment ID" onChange={handleInputChange} className="col-span-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent transition" required />
                    <input type="text" name="courseId" placeholder="Course ID" onChange={handleInputChange} className="col-span-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent transition" required />
                </div>
                <div>
                     <label 
                        className="flex justify-center w-full h-48 px-4 transition bg-white border-2 border-gray-300 border-dashed rounded-md appearance-none cursor-pointer hover:border-primary focus:outline-none"
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                     >
                        <span className="flex flex-col items-center justify-center space-y-2 text-gray-600">
                             {file ? (
                                <>
                                    <DocumentIcon className="w-12 h-12 text-primary"/>
                                    <span className="font-medium">{file.name}</span>
                                    <span className="text-sm text-gray-500">{(file.size / 1024).toFixed(2)} KB</span>
                                </>
                            ) : (
                                <>
                                    <UploadIcon className="w-12 h-12 text-gray-400" />
                                    <span className="font-medium">
                                        Drop file here or <span className="text-primary underline">click to upload</span>
                                    </span>
                                    <span className="text-sm text-gray-500">.txt, .pdf, or .docx files only</span>
                                </>
                            )}
                        </span>
                        <input type="file" ref={fileInputRef} name="file_upload" className="hidden" accept=".txt,.pdf,.docx" onChange={handleFileChange} />
                    </label>
                </div>
                 {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                <button type="submit" className="w-full bg-primary text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors duration-300 text-lg">
                    Analyze Document
                </button>
            </form>
        </div>
    );
};