import React, { useState, useRef } from 'react';
import './UploadForm.css';

interface UploadFormProps {
  onUpload: (file: File, speakerLabeling: boolean, jtbdAnalysis: boolean) => void;
  disabled: boolean;
  status: string;
}

const UploadForm: React.FC<UploadFormProps> = ({ onUpload, disabled, status }) => {
  const [file, setFile] = useState<File | null>(null);
  const [speakerLabeling, setSpeakerLabeling] = useState(false);
  const [jtbdAnalysis, setJtbdAnalysis] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = () => {
    if (file) {
      onUpload(file, speakerLabeling, jtbdAnalysis);
    }
  };

  const handleReset = () => {
    setFile(null);
    setSpeakerLabeling(false);
    setJtbdAnalysis(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="upload-section">
      <h1>🎤 HearYou - Транскрибация</h1>
      <p className="subtitle">Загрузите аудио или видео файл для автоматической транскрибации</p>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*,video/*"
        onChange={handleFileChange}
        disabled={disabled}
      />

      {file && (
        <div className="file-info">
          📄 Выбран файл: <strong>{file.name}</strong> ({(file.size / 1024 / 1024).toFixed(2)} МБ)
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
          <span>🎯 Анализ JTBD (Jobs-to-be-Done)</span>
        </label>
      </div>

      <div className="button-group">
        <button onClick={handleSubmit} disabled={!file || disabled}>
          🚀 Транскрибировать
        </button>
        <button className="secondary" onClick={handleReset} disabled={disabled}>
          🔄 Сбросить
        </button>
      </div>

      {status && <div id="status" dangerouslySetInnerHTML={{ __html: status }} />}
    </div>
  );
};

export default UploadForm;
