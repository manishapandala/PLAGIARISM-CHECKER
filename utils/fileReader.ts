import * as pdfjsLib from 'pdfjs-dist';
import mammoth from 'mammoth';

// Set worker path for pdf.js, suppressing TypeScript error for dynamic import path.
// @ts-ignore
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://aistudiocdn.com/pdfjs-dist@^4.6.0/build/pdf.worker.mjs`;

const readTextFile = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => resolve(event.target?.result as string);
        reader.onerror = (error) => reject(error);
        reader.readAsText(file);
    });
};

const readPdfFile = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const pdf = await pdfjsLib.getDocument({ data: event.target?.result as ArrayBuffer }).promise;
                let content = '';
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    // Using `any` for item as the type from pdf.js is not easily available in this context
                    content += textContent.items.map((item: any) => item.str).join(' ') + '\n';
                }
                resolve(content);
            } catch (error) {
                console.error('Error reading PDF file:', error);
                reject(new Error('Failed to parse the PDF file. It might be corrupted or protected.'));
            }
        };
        reader.onerror = (error) => reject(error);
        reader.readAsArrayBuffer(file);
    });
};

const readDocxFile = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const result = await mammoth.extractRawText({ arrayBuffer: event.target?.result as ArrayBuffer });
                resolve(result.value);
            } catch (error) {
                console.error('Error reading DOCX file:', error);
                reject(new Error('Failed to parse the DOCX file.'));
            }
        };
        reader.onerror = (error) => reject(error);
        reader.readAsArrayBuffer(file);
    });
};

export const extractTextFromFile = (file: File): Promise<string> => {
    const fileType = file.type;
    const extension = file.name.split('.').pop()?.toLowerCase();

    if (fileType === 'text/plain' || extension === 'txt') {
        return readTextFile(file);
    } 
    
    if (fileType === 'application/pdf' || extension === 'pdf') {
        return readPdfFile(file);
    }
    
    if (fileType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || extension === 'docx') {
        return readDocxFile(file);
    }
    
    return Promise.reject(new Error(`File type "${file.name}" is not supported. Please upload a .txt, .pdf, or .docx file.`));
};
