import React from 'react';
import SpeakerBlock from './SpeakerBlock';
import { aggregateSpeakerText, extractSpeakers, getSpeakerColor } from '../utils/textFormatting';
import './TranscriptionResult.css';

interface TranscriptionResultProps {
  text: string;
  filename: string;
  taskId: string;
  speakerLabeling: boolean;
}

const TranscriptionResult: React.FC<TranscriptionResultProps> = ({
  text,
  filename,
  taskId,
  speakerLabeling,
}) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    alert('Текст скопирован в буфер обмена!');
  };

  const renderContent = () => {
    if (!text || text.trim() === '') {
      return (
        <div className="result-text">
          (Речь не обнаружена. Возможно, файл содержит только музыку или фоновый шум)
        </div>
      );
    }

    if (speakerLabeling && (text.includes('SPEAKER_') || text.includes('Спикер '))) {
      const aggregated = aggregateSpeakerText(text);
      const speakers = extractSpeakers(aggregated);
      const lines = aggregated.split(/\n\n/);

      return (
        <div className="speaker-view">
          {/* Speaker Legend */}
          <div className="speaker-legend">
            {speakers.map((speakerNum) => {
              const num = parseInt(speakerNum);
              const displayNum = num + 1;
              const color = getSpeakerColor(num);
              return (
                <div key={speakerNum} className="legend-item">
                  <div
                    className="legend-avatar"
                    style={{ backgroundColor: color }}
                  >
                    S{displayNum}
                  </div>
                  <span>Спикер {displayNum}</span>
                </div>
              );
            })}
          </div>

          {/* Speaker Blocks */}
          <div className="speaker-blocks">
            {lines.map((line, idx) => {
              const match = line.match(/(?:SPEAKER_(\d+)|Спикер (\d+)):\s*(.+)/s);
              if (match) {
                const speakerNum = parseInt(match[1] || match[2]);
                const speakerText = match[3];
                return (
                  <SpeakerBlock key={idx} speakerNum={speakerNum} text={speakerText} />
                );
              }
              return null;
            })}
          </div>
        </div>
      );
    }

    return <div className="result-text">{text}</div>;
  };

  const words = text.split(/\s+/).length;
  const chars = text.length;

  return (
    <div className="result-section">
      <div className="result-header">
        <h2>📝 Результат транскрибации</h2>
        <button onClick={handleCopy} className="copy-btn">
          📋 Копировать
        </button>
      </div>

      <div className="result-info">
        📄 Файл: {filename} | 📊 Слов: {words} | 📏 Символов: {chars}
        {speakerLabeling && ' | 🎭 По ролям'}
        {taskId && ` | 🔗 ID: ${taskId}`}
      </div>

      {renderContent()}
    </div>
  );
};

export default TranscriptionResult;
