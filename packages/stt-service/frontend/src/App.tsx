import { useState, useEffect, useRef } from 'react';
import UploadForm from './components/UploadForm';
import ProgressBar from './components/ProgressBar';
import TranscriptionResult from './components/TranscriptionResult';
import JTBDAnalysis from './components/JTBDAnalysis';
import History from './components/History';
import {
  uploadFile,
  createEventSource,
  loadResult,
} from './utils/api';
import type { TranscriptionResult as TResult } from './types';
import './App.css';

function App() {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [showProgress, setShowProgress] = useState(false);
  const [result, setResult] = useState<TResult | null>(null);
  const startTimeRef = useRef<number>(0);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Check URL for task_id (shared links)
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id');
    if (taskId) {
      handleLoadResult(taskId);
    }

    // Cleanup EventSource on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleLoadResult = async (taskId: string) => {
    try {
      setStatus('<span class="info">🔄 Загрузка результата...</span>');
      const data = await loadResult(taskId);

      const resultData: TResult = {
        text: data.result,
        task_id: taskId,
        filename: data.filename || 'Неизвестный файл',
        time: '(из истории)',
        speaker_labeling: data.speaker_labeling || false,
        jtbd_analysis: data.jtbd_analysis || false,
        jtbd: data.jtbd,
      };

      setResult(resultData);
      setStatus('<span class="success">✅ Результат загружен</span>');

      // Update URL
      const url = new URL(window.location.href);
      url.searchParams.set('task_id', taskId);
      window.history.pushState({}, '', url);
    } catch (error) {
      setStatus(
        `<span class="error">❌ Не удалось загрузить результат: ${
          error instanceof Error ? error.message : 'Неизвестная ошибка'
        }</span>`
      );
    }
  };

  const handleUpload = async (
    file: File,
    speakerLabeling: boolean,
    jtbdAnalysis: boolean
  ) => {
    setUploading(true);
    setResult(null);
    setProgress(0);
    setShowProgress(false);
    startTimeRef.current = Date.now();

    try {
      setStatus('<span class="info">📤 Загрузка файла...</span>');

      const taskId = await uploadFile(file, speakerLabeling, jtbdAnalysis);

      const uploadTime = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);
      setStatus(`<span class="success">✓ Файл загружен за ${uploadTime}с</span>`);
      setShowProgress(true);

      // Update URL
      const url = new URL(window.location.href);
      url.searchParams.set('task_id', taskId);
      window.history.pushState({}, '', url);

      // Start status streaming
      streamStatus(taskId, file.name, speakerLabeling, jtbdAnalysis);
    } catch (error) {
      setStatus(
        `<span class="error">❌ Ошибка: ${
          error instanceof Error ? error.message : 'Неизвестная ошибка'
        }</span>`
      );
      setUploading(false);
    }
  };

  const streamStatus = (
    taskId: string,
    filename: string,
    speakerLabeling: boolean,
    jtbdAnalysis: boolean
  ) => {
    eventSourceRef.current = createEventSource(
      taskId,
      (data) => {
        const elapsed = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);

        if (data.progress) {
          setProgress(data.progress);
        }

        if (data.message) {
          setStatus(`<span class="info">🔄 ${data.message} (${elapsed}с)</span>`);
        }

        if (data.status === 'completed') {
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
          }

          const totalTime = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);

          if (data.result) {
            const resultData: TResult = {
              text: data.result,
              task_id: taskId,
              filename,
              time: totalTime,
              speaker_labeling: speakerLabeling,
              jtbd_analysis: jtbdAnalysis,
              jtbd: data.jtbd,
            };

            setResult(resultData);
            setStatus(
              `<span class="success">✅ Транскрибация завершена за ${totalTime} секунд</span>`
            );
            setShowProgress(false);
            setUploading(false);

            // Save to history
            saveToHistory(taskId, filename, speakerLabeling, jtbdAnalysis);
            setHistory(getHistory());

            // Scroll to result
            setTimeout(() => {
              document
                .querySelector('.result-section')
                ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
          } else {
            throw new Error('Результат не найден');
          }
        } else if (data.status === 'failed' || data.status === 'error') {
          throw new Error(data.message || 'Ошибка обработки');
        }
      },
      (error) => {
        setStatus(`<span class="error">❌ ${error.message}</span>`);
        setUploading(false);
        setShowProgress(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
      }
    );
  };

  const handleLoadHistory = (item: HistoryItem) => {
    handleLoadResult(item.task_id);
  };

  const handleClearHistory = () => {
    if (confirm('Вы уверены, что хотите очистить историю?')) {
      clearHistory();
      setHistory([]);
    }
  };

  return (
    <div className="container">
      <UploadForm onUpload={handleUpload} disabled={uploading} status={status} />
      <ProgressBar progress={progress} visible={showProgress} />

      {result && (
        <div className={`results-grid ${result.jtbd ? '' : 'single-column'}`}>
          <TranscriptionResult
            text={result.text}
            filename={result.filename}
            taskId={result.task_id}
            speakerLabeling={result.speaker_labeling}
          />
          {result.jtbd && <JTBDAnalysis jtbd={result.jtbd} />}
        </div>
      )}

      <History items={history} onLoad={handleLoadHistory} onClear={handleClearHistory} />
    </div>
  );
}

export default App;
