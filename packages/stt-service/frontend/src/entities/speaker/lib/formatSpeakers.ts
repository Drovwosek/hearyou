/**
 * Speaker formatting utilities for transcription display
 * Handles speaker diarization, color coding, and text aggregation
 */

/**
 * Aggregate word-by-word speaker labels into blocks separated by "\n\n"
 * Input: "SPEAKER_00: word1\nSPEAKER_00: word2\nSPEAKER_01: word3"
 * Output: "SPEAKER_00: word1 word2\n\nSPEAKER_01: word3"
 */
export const aggregateSpeakerText = (text: string): string => {
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

/**
 * Extract unique speaker numbers from formatted text
 * Returns array of speaker numbers (as strings) found in the text
 */
export const extractSpeakers = (text: string): string[] => {
  const speakerPattern = /(?:SPEAKER_(\d+)|Спикер (\d+)):/g;
  const matches = [...text.matchAll(speakerPattern)];
  const uniqueSpeakers = [...new Set(matches.map((m) => m[1] || m[2]))];
  return uniqueSpeakers;
};

/**
 * Get color for speaker by number
 * Uses 5-color palette that cycles for additional speakers
 */
export const getSpeakerColor = (speakerNum: number): string => {
  const colors = ['#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea'];
  return colors[speakerNum % colors.length];
};
