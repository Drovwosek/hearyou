import type { StatusUpdate, HistoryItem } from '../types';

export const uploadFile = async (
  file: File,
  speakerLabeling: boolean,
  jtbdAnalysis: boolean,
  qualityMode: 'fast' | 'quality' = 'quality'
): Promise<string> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('speaker_labeling', speakerLabeling.toString());
  formData.append('jtbd_analysis', jtbdAnalysis.toString());
  formData.append('quality_mode', qualityMode);

  const response = await fetch('/transcribe', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }

  const data = await response.json();
  if (!data.task_id) {
    throw new Error('Не получен task_id');
  }

  return data.task_id;
};

export const createEventSource = (
  taskId: string,
  onMessage: (data: StatusUpdate) => void,
  onError: (error: Error) => void
): EventSource => {
  const eventSource = new EventSource(`/status/${taskId}/stream`);

  eventSource.onmessage = (event) => {
    try {
      const data: StatusUpdate = JSON.parse(event.data);
      if (data.error) {
        throw new Error(data.error);
      }
      onMessage(data);
    } catch (error) {
      onError(error as Error);
      eventSource.close();
    }
  };

  eventSource.onerror = () => {
    onError(new Error('Ошибка соединения с сервером'));
    eventSource.close();
  };

  return eventSource;
};

export const loadResult = async (taskId: string) => {
  const response = await fetch(`/result/${taskId}`);
  if (!response.ok) {
    throw new Error('Результат не найден');
  }
  return await response.json();
};

// History management
const HISTORY_KEY = 'transcription_history';
const MAX_HISTORY_ITEMS = 10;

export const saveToHistory = (
  taskId: string,
  filename: string,
  speakerLabeling: boolean,
  jtbdAnalysis: boolean
): void => {
  try {
    const history = getHistory();
    const newItem: HistoryItem = {
      task_id: taskId,
      filename,
      timestamp: Date.now(),
      speaker_labeling: speakerLabeling,
      jtbd_analysis: jtbdAnalysis,
    };

    // Remove duplicates and add new item
    const filtered = history.filter((item) => item.task_id !== taskId);
    filtered.unshift(newItem);

    // Keep only MAX_HISTORY_ITEMS
    const trimmed = filtered.slice(0, MAX_HISTORY_ITEMS);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
  } catch (error) {
    console.error('Failed to save history:', error);
  }
};

export const getHistory = (): HistoryItem[] => {
  try {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load history:', error);
    return [];
  }
};

export const clearHistory = (): void => {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch (error) {
    console.error('Failed to clear history:', error);
  }
};
