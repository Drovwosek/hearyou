import React from 'react';
import { getSpeakerColor } from '../utils/textFormatting';
import './SpeakerBlock.css';

interface SpeakerBlockProps {
  speakerNum: number;
  text: string;
}

const SpeakerBlock: React.FC<SpeakerBlockProps> = ({ speakerNum, text }) => {
  const displayNum = speakerNum + 1;
  const color = getSpeakerColor(speakerNum);

  return (
    <div className="speaker-block" style={{ '--speaker-color': color } as React.CSSProperties}>
      <div className="speaker-avatar">S{displayNum}</div>
      <div className="speaker-bubble">
        <div className="speaker-name">Спикер {displayNum}</div>
        <div className="speaker-text">{text}</div>
      </div>
    </div>
  );
};

export default SpeakerBlock;
