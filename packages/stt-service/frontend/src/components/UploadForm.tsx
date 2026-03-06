import React, { useState, useRef } from 'react';
import './UploadForm.css';

interface UploadFormProps {
  onUpload: (file: File, speakerLabeling: boolean, jtbdAnalysis: boolean) => void;
  disabled: boolean;
  status: string;
}

const MAX_FILE_SIZE = 25 * 1024 * 1024 * 1024; // 25GB in bytes

const UploadForm: React.FC<UploadFormProps> = ({ onUpload, disabled, status }) => {
  const [file, setFile] = useState<File | null>(null);
  const [speakerLabeling, setSpeakerLabeling] = useState(false);
  const [jtbdAnalysis, setJtbdAnalysis] = useState(false);
  const [validationError, setValidationError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValidationError('');
    
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Validate file size
      if (selectedFile.size > MAX_FILE_SIZE) {
        setValidationError(
          `Файл слишком большой (${formatFileSize(selectedFile.size)}). Максимальный размер: 25GB`
        );
        setFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }

      // Validate file type (audio or video)
      const fileType = selectedFile.type;
      const isValidType = 
        fileType.startsWith('audio/') || 
        fileType.startsWith('video/') ||
        // Allow common extensions even if MIME type is not set
        /\.(mp3|mp4|wav|m4a|ogg|flac|aac|wma|avi|mov|mkv|webm)$/i.test(selectedFile.name);

      if (!isValidType) {
        setValidationError(
          'Неподдерживаемый формат файла. Пожалуйста, выберите аудио или видео файл.'
        );
        setFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }

      setFile(selectedFile);
    }
  };

  const handleSubmit = () => {
    if (file && !validationError) {
      onUpload(file, speakerLabeling, jtbdAnalysis);
    }
  };

  const handleReset = () => {
    setFile(null);
    setSpeakerLabeling(false);
    setJtbdAnalysis(false);
    setValidationError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="upload-section">
      <h1>🎤 HearYou - Транскрибация</h1>
      <p className="subtitle">
        Загрузите аудио или видео файл для автоматической транскрибации (макс. 25GB)
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*,video/*,.mp3,.mp4,.wav,.m4a,.ogg,.flac,.aac,.wma,.avi,.mov,.mkv,.webm"
        onChange={handleFileChange}
        disabled={disabled}
        className="file-input"
      />

      {validationError && (
        <div className="validation-error">
          ⚠️ {validationError}
        </div>
      )}

      {file && !validationError && (
        <div className="file-info">
          📄 Выбран файл: <strong>{file.name}</strong> ({formatFileSize(file.size)})
        </div>
      )}

      <div className="toggles">
        <label className="toggle-item">
          <input
            type="checkbox"
            checked={speakerLabeling}
            onChange={(e) => setSpeakerLabeling(e.target.checked)}
            disabled={disabled}
          />
          <span>🎭 Определить спикеров</span>
        </label>

        <label className="toggle-item">
          <input
            type="checkbox"
            checked={jtbdAnalysis}
            onChange={(e) => setJtbdAnalysis(e.target.checked)}
            disabled={disabled}
          />
          <span>🎯 Анализ JTBD</span>
        </label>
      </div>

      <div className="button-group">
        <button 
          onClick={handleSubmit} 
          disabled={!file || disabled || !!validationError}
          className="primary-button"
        >
          🚀 Транскрибировать
        </button>
        <button 
          className="secondary" 
          onClick={handleReset} 
          disabled={disabled}
        >
          🔄 Сбросить
        </button>
      </div>

      {status && <div id="status" dangerouslySetInnerHTML={{ __html: status }} />}
    </div>
  );
};

export default UploadForm;
