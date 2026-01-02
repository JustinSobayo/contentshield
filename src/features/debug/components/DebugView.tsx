import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Terminal, Shield, CheckCircle2, XCircle, Activity } from "lucide-react";

interface DebugInfo {
    status: string;
    environment: string;
    model_configured: string;
    api_key_status: string;
    frontend_origin_configured: string;
    request_origin: string;
    cors_check: string;
    timestamp: string;
}

export const DebugView: React.FC = () => {
    const [debugInfo, setDebugInfo] = useState<DebugInfo | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchDebugInfo = async () => {
        setLoading(true);
        setError(null);
        try {
            let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

            // Proactive Fix: Add https if protocol is missing
            if (API_URL && !API_URL.startsWith('http')) {
                API_URL = `https://${API_URL}`;
            }

            const response = await fetch(`${API_URL}/debug`);
            if (!response.ok) throw new Error(`Status: ${response.status}`);
            const data = await response.json();
            setDebugInfo(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDebugInfo();
    }, []);

    return (
        <div className="p-6 space-y-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Terminal className="w-6 h-6 text-primary" />
                    <h1 className="text-2xl font-bold tracking-tight">System Diagnostics</h1>
                </div>
                <Button variant="outline" onClick={fetchDebugInfo} disabled={loading}>
                    {loading ? "Refreshing..." : "Refresh Status"}
                </Button>
            </div>

            {error && (
                <div className="p-4 border border-destructive/50 bg-destructive/10 text-destructive rounded-lg flex items-center gap-3">
                    <XCircle className="w-5 h-5" />
                    <p className="font-medium text-sm">Failed to connect to backend: {error}</p>
                </div>
            )}

            <div className="grid gap-4 md:grid-cols-2">
                <Card className="bg-card/50 backdrop-blur">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                            <Shield className="w-4 h-4" /> Security & CORS
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">API Key Status</span>
                            <Badge variant={debugInfo?.api_key_status === 'present' ? 'default' : 'destructive'}>
                                {debugInfo?.api_key_status || 'Checking...'}
                            </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">CORS Check</span>
                            <Badge variant={debugInfo?.cors_check === 'Match' ? 'default' : 'secondary'}>
                                {debugInfo?.cors_check || 'Waiting...'}
                            </Badge>
                        </div>
                        <div className="pt-2 border-t border-border/50">
                            <p className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Allowed Origin</p>
                            <p className="text-xs font-mono break-all">{debugInfo?.frontend_origin_configured || 'N/A'}</p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="bg-card/50 backdrop-blur">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                            <Activity className="w-4 h-4" /> AI Model & Engine
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Active Model</span>
                            <span className="text-sm font-mono font-bold text-primary">{debugInfo?.model_configured || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Runtime Env</span>
                            <Badge variant="outline">{debugInfo?.environment || 'detecting...'}</Badge>
                        </div>
                        <div className="pt-2 border-t border-border/50">
                            <p className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Server Time</p>
                            <p className="text-xs font-mono">{debugInfo?.timestamp || 'Waiting for signal...'}</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-primary/20 bg-primary/5">
                <CardContent className="pt-6">
                    <div className="flex items-start gap-3">
                        <CheckCircle2 className="w-5 h-5 text-primary mt-0.5" />
                        <div>
                            <h4 className="font-semibold text-sm">System is {debugInfo?.status === 'online' ? 'Online' : 'Initializing'}</h4>
                            <p className="text-xs text-muted-foreground mt-1">
                                The diagnostic panel shows real-time data from the Google Railway instance. Use this to verify that your environment variables and CORS headers are properly synchronized.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};
