export interface AnalyzedIssue {
    category: string;
    timestamp?: string;
    snippet: string;
    rationale: string;
    policy_citations: string[];
}

export interface AnalyzeResponse {
    platform: string;
    risk_level: string;
    summary_rationale?: string;
    issues: AnalyzedIssue[];
}
