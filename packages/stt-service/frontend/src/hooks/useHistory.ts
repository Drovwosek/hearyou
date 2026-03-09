import { useState, useEffect, useCallback } from 'react';
import { loadResult } from '../utils/api';
import type { TranscriptionResult } from '../types';

export interface HistoryEntry {
  task_id: string;
  filename: string;
  status: string;
  created_at: string;
  user: string;
}

export const useHistory = () => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/history?limit=50');
      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }
      
      const data = await response.json();
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTranscription = async (taskId: string): Promise<TranscriptionResult> => {
    const data = await loadResult(taskId);
    
    return {
      text: data.result || data.text,
      task_id: taskId,
      filename: data.original_filename || data.filename || 'Unknown file',
      time: 'from history',
      speaker_labeling: data.options?.speaker_labeling || false,
      jtbd_analysis: data.options?.analyze_jtbd || false,
      jtbd: data.jtbd,
    };
  };

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    history,
    loading,
    error,
    fetchHistory,
    loadTranscription,
  };
};
