export interface TranscriptionResult {
  text: string;
  task_id: string;
  filename: string;
  time: string;
  speaker_labeling: boolean;
  jtbd_analysis: boolean;
  jtbd?: JTBDResult;
}

export interface JTBDResult {
  jobs?: Array<{
    job: string;
    context: string;
    outcome: string;
    quote: string;
  }>;
  pains?: Array<{
    pain: string;
    severity: string;
    context: string;
    quote: string;
  }>;
  gains?: Array<{
    gain: string;
    value: string;
    context: string;
    quote: string;
  }>;
}

export interface StatusUpdate {
  status: 'processing' | 'completed' | 'failed' | 'error';
  message?: string;
  progress?: number;
  result?: string;
  error?: string;
  jtbd?: JTBDResult;
}

export interface HistoryItem {
  task_id: string;
  filename: string;
  timestamp: number;
  speaker_labeling: boolean;
  jtbd_analysis: boolean;
}
