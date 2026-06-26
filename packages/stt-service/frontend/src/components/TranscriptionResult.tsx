import React from 'react';
import SpeakerBlock from './SpeakerBlock';
import { aggregateSpeakerText } from '../utils/textFormatting';
import './TranscriptionResult.css';

interface TranscriptionResultProps {
  text: string;
  filename: string;
  taskId: string;
  speakerLabeling: boolean;
  wordsWithSpeakers?: Array<{
    word: string;
    speaker?: string;
  }>;
}

const TranscriptionResult: React.FC<TranscriptionResultProps> = ({
  text,
  wordsWithSpeakers,
  speakerLabeling,
}) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    alert('Текст скопирован в буфер обмена!');
  };

  const renderSpeakerBlocksFromWords = () => {
    if (!wordsWithSpeakers || wordsWithSpeakers.length === 0) {
      return null;
    }

    const blocks: Array<{ speakerNum: number; text: string }> = [];
    let currentSpeaker: string | undefined;
    let currentWords: string[] = [];

    const pushBlock = () => {
      if (!currentSpeaker || currentWords.length === 0) {
        return;
      }

      const speakerNum = Number.parseInt(currentSpeaker.replace(/\D/g, ''), 10) || 0;
      blocks.push({ speakerNum, text: currentWords.join(' ') });
    };

    wordsWithSpeakers.forEach((word) => {
      const speaker = word.speaker || 'UNKNOWN';
      if (speaker !== currentSpeaker) {
        pushBlock();
        currentSpeaker = speaker;
        currentWords = word.word ? [word.word] : [];
      } else if (word.word) {
        currentWords.push(word.word);
      }
    });

    pushBlock();

    if (blocks.length === 0) {
      return null;
    }

    return (
      <div className="speaker-view">
        <div className="speaker-blocks">
          {blocks.map((block, idx) => (
            <SpeakerBlock key={idx} speakerNum={block.speakerNum} text={block.text} />
          ))}
        </div>
      </div>
    );
  };

  const renderContent = () => {
    if (!text || text.trim() === '') {
      return (
        <div className="result-text">
          (Речь не обнаружена. Возможно, файл содержит только музыку или фоновый шум)
        </div>
      );
    }

    const structuredSpeakerView = renderSpeakerBlocksFromWords();
    if (speakerLabeling && structuredSpeakerView) {
      return structuredSpeakerView;
    }

    if (speakerLabeling && (text.includes('SPEAKER_') || text.includes('Спикер '))) {
      const aggregated = aggregateSpeakerText(text);
      const lines = aggregated.split(/\n\n/);

      return (
        <div className="speaker-view">
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

  return (
    <div className="result-section">
      <div className="result-header">
        <h2>📝 Результат транскрибации</h2>
        <button onClick={handleCopy} className="copy-btn">
          📋 Копировать
        </button>
      </div>

      {renderContent()}
    </div>
  );
};

export default TranscriptionResult;
