import React, { useEffect, useState, useRef } from 'react';
import './StatusTracker.css';

export interface StatusData {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'error';
  progress?: number;
  message?: string;
  result?: string;
  error?: string;
}

interface StatusTrackerProps {
  taskId: string | null;
  onStatusUpdate?: (data: StatusData) => void;
  onComplete?: (result: string) => void;
  onError?: (error: string) => void;
  pollInterval?: number; // in milliseconds, default 2000
}

const StatusTracker: React.FC<StatusTrackerProps> = ({
  taskId,
  onStatusUpdate,
  onComplete,
  onError,
  pollInterval = 2000,
}) => {
  const [currentStatus, setCurrentStatus] = useState<StatusData | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    if (!taskId) {
      // Clear intervals if no taskId
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
        timeIntervalRef.current = null;
      }
      setCurrentStatus(null);
      setElapsedTime(0);
      return;
    }

    startTimeRef.current = Date.now();

    // Start elapsed time counter
    timeIntervalRef.current = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTimeRef.current) / 1000));
    }, 1000);

    // Poll status endpoint
    const pollStatus = async () => {
      try {
        const response = await fetch(`/status/${taskId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data: StatusData = await response.json();
        setCurrentStatus(data);
        onStatusUpdate?.(data);

        // Handle completion
        if (data.status === 'completed') {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          if (timeIntervalRef.current) {
            clearInterval(timeIntervalRef.current);
            timeIntervalRef.current = null;
          }
          
          if (data.result) {
            onComplete?.(data.result);
          }
        }

        // Handle errors
        if (data.status === 'failed' || data.status === 'error') {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          if (timeIntervalRef.current) {
            clearInterval(timeIntervalRef.current);
            timeIntervalRef.current = null;
          }
          
          onError?.(data.error || data.message || 'Неизвестная ошибка');
        }
      } catch (error) {
        console.error('Status poll error:', error);
        onError?.(error instanceof Error ? error.message : 'Ошибка соединения');
        
        // Clear intervals on error
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        if (timeIntervalRef.current) {
          clearInterval(timeIntervalRef.current);
          timeIntervalRef.current = null;
        }
      }
    };

    // Start polling immediately and then every pollInterval
    pollStatus();
    intervalRef.current = setInterval(pollStatus, pollInterval);

    // Cleanup on unmount or taskId change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
    };
  }, [taskId, pollInterval, onStatusUpdate, onComplete, onError]);

  if (!taskId || !currentStatus) {
    return null;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'processing':
        return '🔄';
      case 'completed':
        return '✅';
      case 'failed':
      case 'error':
        return '❌';
      default:
        return '📊';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'В очереди';
      case 'processing':
        return 'Обработка';
      case 'completed':
        return 'Завершено';
      case 'failed':
      case 'error':
        return 'Ошибка';
      default:
        return 'Неизвестно';
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}м ${secs}с` : `${secs}с`;
  };

  return (
    <div className="status-tracker">
      <div className="status-header">
        <span className="status-icon">{getStatusIcon(currentStatus.status)}</span>
        <span className="status-label">{getStatusLabel(currentStatus.status)}</span>
        <span className="status-time">{formatTime(elapsedTime)}</span>
      </div>
      
      {currentStatus.message && (
        <div className="status-message">{currentStatus.message}</div>
      )}
      
      {currentStatus.progress !== undefined && currentStatus.progress > 0 && (
        <div className="status-progress">
          <div className="status-progress-bar">
            <div
              className="status-progress-fill"
              style={{ width: `${currentStatus.progress}%` }}
            />
          </div>
          <span className="status-progress-text">{currentStatus.progress}%</span>
        </div>
      )}
      
      {currentStatus.error && (
        <div className="status-error">⚠️ {currentStatus.error}</div>
      )}
    </div>
  );
};

export default StatusTracker;
