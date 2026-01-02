import { AnalyzeResponse } from "../types/analysis.types";

export const analyzeContent = async (formData: FormData): Promise<AnalyzeResponse> => {
    let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Proactive Fix: Add https if protocol is missing (prevents relative path 404s on Vercel)
    if (API_URL && !API_URL.startsWith('http')) {
        API_URL = `https://${API_URL}`;
    }

    const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`);
    }

    return response.json();
};
