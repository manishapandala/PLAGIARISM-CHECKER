import { GoogleGenAI, Type } from "@google/genai";
import type { ComparisonDocument, SimilarityResult, CheckResult } from '../types';

// The API key is expected to be set in the environment variables.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const responseSchema = {
    type: Type.OBJECT,
    properties: {
        overall_similarity_score: {
            type: Type.NUMBER,
            description: "A single score from 0 to 100 representing the overall similarity between the two texts."
        },
        similarity_level: {
            type: Type.STRING,
            enum: ["none", "low", "moderate", "high", "exact"],
            description: "A classification of the similarity level. 'none' if score is below 10."
        },
        matched_lines: {
            type: Type.ARRAY,
            description: "An array of objects, where each object represents a pair of similar sentences or significant phrases.",
            items: {
                type: Type.OBJECT,
                properties: {
                    source_text: {
                        type: Type.STRING,
                        description: "The sentence from the source document."
                    },
                    match_text: {
                        type: Type.STRING,
                        description: "The corresponding similar sentence from the comparison document."
                    },
                    similarity: {
                        type: Type.NUMBER,
                        description: "A score from 0 to 100 indicating how similar this specific pair of sentences is."
                    }
                },
                 required: ["source_text", "match_text", "similarity"]
            }
        }
    },
    required: ["overall_similarity_score", "similarity_level", "matched_lines"]
};


async function analyzeSimilarity(sourceText: string, comparisonDoc: ComparisonDocument): Promise<SimilarityResult> {
    const prompt = `
        You are an advanced plagiarism detection AI. Analyze the two texts provided below and determine the degree of similarity.

        **Instructions:**
        1.  Compare the "Source Document" with the "Comparison Document".
        2.  Calculate an "overall_similarity_score" from 0 to 100.
        3.  Categorize the similarity into "none", "low" (10-49), "moderate" (50-74), "high" (75-94), or "exact" (95-100). Use "none" if the score is less than 10.
        4.  Identify and list specific pairs of sentences or significant phrases that are similar. For each pair, provide the text from both documents and a specific similarity score for that pair.
        5.  Return the analysis ONLY in the provided JSON format.

        **Source Document:**
        \`\`\`
        ${sourceText}
        \`\`\`

        **Comparison Document (ID: ${comparisonDoc.id}):**
        \`\`\`
        ${comparisonDoc.content}
        \`\`\`
    `;

    try {
        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: [{ parts: [{ text: prompt }] }],
            config: {
                responseMimeType: "application/json",
                responseSchema: responseSchema,
                temperature: 0.1,
            }
        });
        
        const jsonResponse = JSON.parse(response.text.trim());

        return {
            matched_doc_id: comparisonDoc.id,
            similarity_score: jsonResponse.overall_similarity_score || 0,
            similarity_level: jsonResponse.similarity_level || 'none',
            matched_lines: jsonResponse.matched_lines || [],
            type: comparisonDoc.type,
            retrieved_context: comparisonDoc.content
        };
    } catch (error) {
        console.error(`Error analyzing similarity with ${comparisonDoc.id}:`, error);
        // Re-throw the error to be caught by Promise.allSettled in the calling function.
        // This prevents the entire process from failing silently on an API error.
        throw error;
    }
}

export async function checkPlagiarism(sourceText: string, comparisonDocs: ComparisonDocument[]): Promise<CheckResult> {
    const promises = comparisonDocs.map(doc => analyzeSimilarity(sourceText, doc));
    const settledResults = await Promise.allSettled(promises);

    const successfulResults: SimilarityResult[] = [];
    let firstError: Error | null = null;

    for (const result of settledResults) {
        if (result.status === 'fulfilled') {
            successfulResults.push(result.value);
        } else {
            console.error('An individual similarity check failed:', result.reason);
            if (!firstError) {
                firstError = result.reason as Error;
            }
        }
    }

    // If all checks fail, it's likely a configuration issue (e.g., API key).
    // Propagate a clear error to the UI.
    if (successfulResults.length === 0 && firstError) {
        const errorMessage = firstError.message.toLowerCase().includes('api key')
            ? 'Failed to analyze documents. Please ensure the API key is configured correctly and has sufficient quota.'
            : `An API error occurred during analysis: ${firstError.message}`;
        throw new Error(errorMessage);
    }
    
    const validSimilarities = successfulResults.filter(res => res.similarity_level !== 'none' && res.similarity_score > 10);
    validSimilarities.sort((a, b) => b.similarity_score - a.similarity_score);
    
    const overallScore = validSimilarities.length > 0 ? Math.max(...validSimilarities.map(s => s.similarity_score)) : 0;

    return {
        overallScore: Math.round(overallScore),
        similarities: validSimilarities,
    };
}