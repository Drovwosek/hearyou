export interface TranscriptionResult {
  text: string;
  task_id: string;
  filename: string;
  time: string;
  speaker_labeling: boolean;
  jtbd_analysis: boolean;
  jtbd?: JTBDResult;
  words_with_speakers?: Array<{
    word: string;
    speaker?: string;
    startTime?: string;
    endTime?: string;
  }>;
  speaker_segments?: Array<{
    speaker: string;
    start: number;
    end: number;
  }>;
}

export interface SpeakerMessage {
  speakerNum: number;
  text: string;
}

export interface SpeakerInfo {
  speakerNum: number;
  displayNum: number;
  color: string;
}

export interface JTBDResult {
  jobs?: Array<{
    job?: string;
    text?: string;
    context: string;
    outcome?: string;
    type?: string;
    quote: string;
    confidence?: string;
  }>;
  pains?: Array<{
    pain?: string;
    text?: string;
    severity?: string;
    context: string;
    quote: string;
    confidence?: string;
  }>;
  gains?: Array<{
    gain?: string;
    text?: string;
    value?: string;
    type?: string;
    context: string;
    quote: string;
    confidence?: string;
  }>;
  context?: Array<{
    text: string;
    quote: string;
    dimension?: string;
    confidence?: string;
  }>;
  triggers?: Array<{
    text: string;
    quote: string;
    type?: string;
    confidence?: string;
  }>;
  summary?: string;
  metadata?: Record<string, unknown>;
}

export interface StatusUpdate {
  status: 'processing' | 'completed' | 'failed' | 'error';
  message?: string;
  progress?: number;
  result?: string;
  error?: string;
  jtbd?: JTBDResult;
  words_with_speakers?: TranscriptionResult['words_with_speakers'];
  speaker_segments?: TranscriptionResult['speaker_segments'];
}

export interface HistoryItem {
  task_id: string;
  filename: string;
  timestamp: number;
  speaker_labeling: boolean;
  jtbd_analysis: boolean;
}
