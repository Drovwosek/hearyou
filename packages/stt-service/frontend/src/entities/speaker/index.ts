/**
 * Speaker entity - public API
 * Handles speaker diarization display and formatting
 */

export { default as SpeakerBlock } from './ui/SpeakerBlock';
export { default as SpeakerLegend } from './ui/SpeakerLegend';
export { 
  aggregateSpeakerText, 
  extractSpeakers, 
  getSpeakerColor 
} from './lib/formatSpeakers';
