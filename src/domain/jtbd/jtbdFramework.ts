import type { JobForceType, JobStage } from './types'

export type JobTemplateField = {
  key: 'situation' | 'motivation' | 'expectedOutcome'
  label: string
  prompt: string
  fallback: string
}

export type JobStageDefinition = {
  id: JobStage
  label: string
  description: string
  markers: string[]
}

export type ForceDefinition = {
  id: JobForceType
  label: string
  markers: string[]
}

export const jobStatementTemplate =
  'When {situation}, I want to {motivation}, so I can {expectedOutcome}.'

export const jobTemplateFields: JobTemplateField[] = [
  {
    key: 'situation',
    label: 'Situation',
    prompt: 'When...',
    fallback: 'the customer faces this interview situation',
  },
  {
    key: 'motivation',
    label: 'Motivation',
    prompt: 'I want to...',
    fallback: 'make progress',
  },
  {
    key: 'expectedOutcome',
    label: 'Expected outcome',
    prompt: 'So I can...',
    fallback: 'achieve a better outcome',
  },
]

export const jobStages: JobStageDefinition[] = [
  {
    id: 'trigger',
    label: 'Trigger',
    description: 'What caused the person to start looking for a new way.',
    markers: ['когда', 'после того', 'столкнулся', 'начал', 'появилась', 'решил'],
  },
  {
    id: 'struggle',
    label: 'Struggle',
    description: 'What made the current way painful or insufficient.',
    markers: ['сложно', 'трудно', 'больно', 'мешает', 'проблема', 'не получается'],
  },
  {
    id: 'progress',
    label: 'Progress',
    description: 'What progress the person is trying to make.',
    markers: ['хочу', 'нужно', 'важно', 'цель', 'получить', 'сделать'],
  },
  {
    id: 'constraints',
    label: 'Constraints',
    description: 'What limits, risks, or switching anxieties shape the job.',
    markers: ['но', 'боюсь', 'риск', 'нет времени', 'дорого', 'нельзя'],
  },
  {
    id: 'outcome',
    label: 'Outcome',
    description: 'What result would make the solution worth adopting.',
    markers: ['чтобы', 'результат', 'успех', 'получилось', 'быстрее', 'лучше'],
  },
]

export const forceDefinitions: ForceDefinition[] = [
  {
    id: 'push',
    label: 'Push of the situation',
    markers: ['устал', 'надоело', 'проблема', 'мешает', 'не хватает'],
  },
  {
    id: 'pull',
    label: 'Pull of a better solution',
    markers: ['хочу', 'удобно', 'быстрее', 'лучше', 'идеально'],
  },
  {
    id: 'anxiety',
    label: 'Anxiety of change',
    markers: ['боюсь', 'сомневаюсь', 'риск', 'страшно', 'не уверен'],
  },
  {
    id: 'habit',
    label: 'Habit of the present',
    markers: ['обычно', 'всегда', 'привык', 'сейчас делаю', 'раньше'],
  },
]

export const followUpQuestionTemplates = [
  {
    question: 'What happened right before this became important?',
    reason: 'Clarifies the trigger and switching moment.',
  },
  {
    question: 'What did you try before, and why was it not enough?',
    reason: 'Separates real struggle from a surface-level feature request.',
  },
  {
    question: 'How would you know this job is successfully done?',
    reason: 'Turns the job into observable success criteria.',
  },
  {
    question: 'What would make you hesitate to adopt a new solution?',
    reason: 'Reveals anxieties, risks, and switching constraints.',
  },
]
