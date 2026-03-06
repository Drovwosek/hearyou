import React from 'react';
import { getSpeakerColor } from '../lib/formatSpeakers';
import './SpeakerLegend.css';

interface SpeakerLegendProps {
  speakers: number[];
}

const SpeakerLegend: React.FC<SpeakerLegendProps> = ({ speakers }) => {
  return (
    <div className="speaker-legend">
      {speakers.map((speakerNum) => {
        const displayNum = speakerNum + 1;
        const color = getSpeakerColor(speakerNum);
        
        return (
          <div key={speakerNum} className="legend-item">
            <div 
              className="legend-avatar" 
              style={{ backgroundColor: color }}
            >
              S{displayNum}
            </div>
            <span className="legend-label">Спикер {displayNum}</span>
          </div>
        );
      })}
    </div>
  );
};

export default SpeakerLegend;
