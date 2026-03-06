export const aggregateSpeakerText = (text: string): string => {
  // Aggregate word-by-word speaker labels into blocks separated by "\n\n"
  const lines = text.split('\n');
  let currentSpeaker: string | null = null;
  let currentWords: string[] = [];
  const blocks: string[] = [];

  lines.forEach((line) => {
    const match = line.match(/^(?:SPEAKER_(\d+)|Спикер (\d+)):\s*(.+)/);
    if (match) {
      const speakerNum = match[1] || match[2];
      const word = match[3].trim();

      if (speakerNum === currentSpeaker) {
        currentWords.push(word);
      } else {
        if (currentSpeaker !== null && currentWords.length > 0) {
          blocks.push(`SPEAKER_${currentSpeaker}: ${currentWords.join(' ')}`);
        }
        currentSpeaker = speakerNum;
        currentWords = [word];
      }
    }
  });

  if (currentSpeaker !== null && currentWords.length > 0) {
    blocks.push(`SPEAKER_${currentSpeaker}: ${currentWords.join(' ')}`);
  }

  return blocks.join('\n\n');
};

export const extractSpeakers = (text: string): string[] => {
  const speakerPattern = /(?:SPEAKER_(\d+)|Спикер (\d+)):/g;
  const matches = [...text.matchAll(speakerPattern)];
  const uniqueSpeakers = [...new Set(matches.map((m) => m[1] || m[2]))];
  return uniqueSpeakers;
};

export const getSpeakerColor = (speakerNum: number): string => {
  const colors = ['#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea'];
  return colors[speakerNum % colors.length];
};
