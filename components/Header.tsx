import React from 'react';
import { DocumentSearchIcon } from './icons/DocumentSearchIcon';

interface HeaderProps {
    onClearSession: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onClearSession }) => {
    return (
        <header className="bg-white dark:bg-gray-900/80 shadow-sm backdrop-blur-md sticky top-0 z-10">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <DocumentSearchIcon className="h-8 w-8 text-primary" />
                        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                            AI Plagiarism Checker
                        </h1>
                    </div>
                     <button
                        onClick={onClearSession}
                        className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                    >
                        Clear Session
                    </button>
                </div>
            </div>
        </header>
    );
};