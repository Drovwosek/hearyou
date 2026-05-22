import {
  followUpQuestionTemplates,
  forceDefinitions,
  jobStages,
  jobStatementTemplate,
  jobTemplateFields,
} from '../../domain/jtbd/jtbdFramework'
import type {
  FollowUpQuestion,
  InterviewAnalysis,
  JobForce,
  JobStage,
  JtbdJob,
} from '../../domain/jtbd/types'
import { countWords, splitIntoSentences, takeLeadingPhrase } from './textSegmentation'

const includesAnyMarker = (sentence: string, markers: string[]): boolean => {
  const normalizedSentence = sentence.toLocaleLowerCase()

  return markers.some((marker) => normalizedSentence.includes(marker))
}

const detectStage = (sentence: string): JobStage => {
  const matchingStage = jobStages.find((stage) =>
    includesAnyMarker(sentence, stage.markers),
  )

  return matchingStage?.id ?? 'progress'
}

const buildStatement = (
  situation: string,
  motivation: string,
  expectedOutcome: string,
): string =>
  jobStatementTemplate
    .replace('{situation}', situation)
    .replace('{motivation}', motivation)
    .replace('{expectedOutcome}', expectedOutcome)

const extractForces = (sentence: string): JobForce[] =>
  forceDefinitions
    .map<JobForce | null>((force) => {
      if (!includesAnyMarker(sentence, force.markers)) {
        return null
      }

      return {
        type: force.id,
        label: force.label,
        evidence: [sentence],
      }
    })
    .filter((force): force is JobForce => force !== null)

const buildJob = (sentence: string, index: number): JtbdJob => {
  const stage = detectStage(sentence)
  const phrase = takeLeadingPhrase(sentence)
  const situation =
    stage === 'trigger' || stage === 'struggle'
      ? phrase
      : jobTemplateFields[0].fallback
  const motivation =
    stage === 'progress' ? phrase : `resolve: ${phrase.toLocaleLowerCase()}`
  const expectedOutcome =
    stage === 'outcome' ? phrase : jobTemplateFields[2].fallback

  return {
    id: `job-${index + 1}`,
    title: phrase,
    statement: buildStatement(situation, motivation, expectedOutcome),
    situation,
    motivation,
    expectedOutcome,
    stage,
    confidence: Math.min(95, 52 + extractForces(sentence).length * 12),
    forces: extractForces(sentence),
    quotes: [
      {
        id: `quote-${index + 1}`,
        text: sentence,
      },
    ],
  }
}

const isJobCandidate = (sentence: string): boolean =>
  jobStages.some((stage) => includesAnyMarker(sentence, stage.markers)) ||
  forceDefinitions.some((force) => includesAnyMarker(sentence, force.markers))

const buildFollowUpQuestions = (jobs: JtbdJob[]): FollowUpQuestion[] => {
  const jobQuestions = jobs.flatMap((job) =>
    followUpQuestionTemplates.slice(0, 2).map((template, index) => ({
      id: `${job.id}-question-${index + 1}`,
      jobId: job.id,
      question: `${template.question} (${job.title})`,
      reason: template.reason,
    })),
  )

  const generalQuestions = followUpQuestionTemplates.slice(2).map((template, index) => ({
    id: `general-question-${index + 1}`,
    question: template.question,
    reason: template.reason,
  }))

  return [...jobQuestions, ...generalQuestions].slice(0, 12)
}

export const analyzeInterview = (text: string): InterviewAnalysis => {
  const sentences = splitIntoSentences(text)
  const jobs = sentences.filter(isJobCandidate).slice(0, 6).map(buildJob)

  return {
    jobs,
    followUpQuestions: buildFollowUpQuestions(jobs),
    sourceStats: {
      words: countWords(text),
      sentences: sentences.length,
    },
  }
}
