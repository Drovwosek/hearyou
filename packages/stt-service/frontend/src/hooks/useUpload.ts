import { useState, useRef, useCallback } from 'react';
import { uploadFile, createEventSource } from '../utils/api';
import type { TranscriptionResult, StatusUpdate } from '../types';

export interface UploadState {
  uploading: boolean;
  progress: number;
  status: string;
  error: string | null;
  result: TranscriptionResult | null;
  taskId: string | null;
}

export interface UploadOptions {
  onComplete?: (result: TranscriptionResult) => void;
  onError?: (error: Error) => void;
  onProgress?: (progress: number, message: string) => void;
}

export const useUpload = (options: UploadOptions = {}) => {
  const [state, setState] = useState<UploadState>({
    uploading: false,
    progress: 0,
    status: '',
    error: null,
    result: null,
    taskId: null,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const startTimeRef = useRef<number>(0);
  const uploadMetadataRef = useRef<{
    filename: string;
    speakerLabeling: boolean;
    jtbdAnalysis: boolean;
  } | null>(null);

  const updateState = useCallback((updates: Partial<UploadState>) => {
    setState((prev) => ({ ...prev, ...updates }));
  }, []);

  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const handleStatusUpdate = useCallback(
    (data: StatusUpdate) => {
      const elapsed = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);

      if (data.progress) {
        updateState({ progress: data.progress });
        options.onProgress?.(data.progress, data.message || '');
      }

      if (data.message) {
        const statusMsg = `<span class="info">🔄 ${data.message} (${elapsed}с)</span>`;
        updateState({ status: statusMsg });
      }

      if (data.status === 'completed') {
        cleanup();

        const totalTime = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);

        if (data.result && uploadMetadataRef.current) {
          const resultData: TranscriptionResult = {
            text: data.result,
            task_id: state.taskId || '',
            filename: uploadMetadataRef.current.filename,
            time: totalTime,
            speaker_labeling: uploadMetadataRef.current.speakerLabeling,
            jtbd_analysis: uploadMetadataRef.current.jtbdAnalysis,
            jtbd: data.jtbd,
          };

          updateState({
            result: resultData,
            uploading: false,
            status: `<span class="success">✅ Транскрибация завершена за ${totalTime} секунд</span>`,
            progress: 100,
          });

          options.onComplete?.(resultData);
        } else {
          const error = new Error('Результат не найден');
          handleError(error);
        }
      } else if (data.status === 'failed' || data.status === 'error') {
        const error = new Error(data.message || 'Ошибка обработки');
        handleError(error);
      }
    },
    [state.taskId, updateState, cleanup, options]
  );

  const handleError = useCallback(
    (error: Error) => {
      cleanup();
      const errorMsg = `<span class="error">❌ ${error.message}</span>`;
      updateState({
        status: errorMsg,
        error: error.message,
        uploading: false,
        progress: 0,
      });
      options.onError?.(error);
    },
    [cleanup, updateState, options]
  );

  const startUpload = useCallback(
    async (file: File, speakerLabeling: boolean, jtbdAnalysis: boolean) => {
      // Reset state
      cleanup();
      updateState({
        uploading: true,
        progress: 0,
        status: '',
        error: null,
        result: null,
        taskId: null,
      });

      startTimeRef.current = Date.now();
      uploadMetadataRef.current = {
        filename: file.name,
        speakerLabeling,
        jtbdAnalysis,
      };

      try {
        // Validate file size (max 25GB)
        const maxSize = 25 * 1024 * 1024 * 1024; // 25GB in bytes
        if (file.size > maxSize) {
          throw new Error('Размер файла превышает максимально допустимый (25GB)');
        }

        updateState({ status: '<span class="info">📤 Загрузка файла...</span>' });

        // Upload file
        const taskId = await uploadFile(file, speakerLabeling, jtbdAnalysis);

        const uploadTime = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);
        updateState({
          taskId,
          status: `<span class="success">✓ Файл загружен за ${uploadTime}с</span>`,
        });

        // Start status streaming
        eventSourceRef.current = createEventSource(
          taskId,
          handleStatusUpdate,
          handleError
        );
      } catch (error) {
        handleError(error as Error);
      }
    },
    [cleanup, updateState, handleStatusUpdate, handleError]
  );

  const reset = useCallback(() => {
    cleanup();
    setState({
      uploading: false,
      progress: 0,
      status: '',
      error: null,
      result: null,
      taskId: null,
    });
  }, [cleanup]);

  return {
    ...state,
    startUpload,
    reset,
    cleanup,
  };
};
