export interface DocumentMetadata {
    docId: string;
    assignmentId: string;
    courseId: string;
    filename: string;
}

export interface StoredDocument {
    metadata: DocumentMetadata;
    content: string;
    submissionDate: string;
}

export interface ComparisonDocument {
    id: string;
    content: string;
    type: 'internal' | 'external';
}

export interface MatchedLine {
    source_text: string;
    match_text: string;
    similarity: number;
}

export interface SimilarityResult {
    matched_doc_id: string;
    similarity_score: number;
    similarity_level: 'low' | 'moderate' | 'high' | 'exact' | 'none';
    matched_lines: MatchedLine[];
    type: 'internal' | 'external';
    retrieved_context?: string; 
}

export interface CheckResult {
    overallScore: number;
    similarities: SimilarityResult[];
}

export interface VisualizationData {
    doc_id: string;
    similarity: number;
    matched_segments: number;
    level: string;
}

export interface NetworkNode {
    id: string;
    group: number;
    similarity?: number;
    fx?: number | null;
    fy?: number | null;
}

export interface NetworkLink {
    source: string;
    target: string;
    value: number;
}

export interface NetworkData {
    nodes: NetworkNode[];
    links: NetworkLink[];
}
