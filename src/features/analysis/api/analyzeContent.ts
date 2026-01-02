import { AnalyzeResponse } from "../types/analysis.types";

export const analyzeContent = async (formData: FormData): Promise<AnalyzeResponse> => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
