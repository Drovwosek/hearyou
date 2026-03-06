import React from 'react';
import { getSpeakerColor } from '../lib/formatSpeakers';
import './SpeakerBlock.css';

interface SpeakerBlockProps {
  speakerNum: number;
  text: string;
}

const SpeakerBlock: React.FC<SpeakerBlockProps> = ({ speakerNum, text }) => {
  const displayNum = speakerNum + 1;
  const color = getSpeakerColor(speakerNum);

  return (
    <div 
      className={`speaker-block speaker-${speakerNum}`}
      style={{ '--speaker-color': color } as React.CSSProperties}
    ><div className="speaker-avatar">S{displayNum}</div><div className="speaker-content"><div className="speaker-label"><span className="speaker-name">Спикер {displayNum}</span><span className="speaker-badge">S{displayNum}</span></div><div className="speaker-bubble"><div className="speaker-text">{text}</div></div></div></div>
  );
};

export default SpeakerBlock;
