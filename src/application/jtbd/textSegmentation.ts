export const splitIntoSentences = (text: string): string[] =>
  text
    .replace(/\s+/g, ' ')
    .split(/(?<=[.!?。！？])\s+|\n+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean)

export const countWords = (text: string): number =>
  text
    .trim()
    .split(/\s+/)
    .filter(Boolean).length

export const takeLeadingPhrase = (sentence: string): string => {
  const cleanSentence = sentence.trim().replace(/[.!?]+$/, '')
  const words = cleanSentence.split(/\s+/)

  return words.slice(0, 18).join(' ')
}
