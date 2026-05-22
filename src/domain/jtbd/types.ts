export type JobStage =
  | 'trigger'
  | 'struggle'
  | 'progress'
  | 'constraints'
  | 'outcome'

export type JobForceType = 'push' | 'pull' | 'anxiety' | 'habit'

export type InterviewQuote = {
  id: string
  text: string
}

export type JobForce = {
  type: JobForceType
  label: string
  evidence: string[]
}

export type JtbdJob = {
  id: string
  title: string
  statement: string
  situation: string
  motivation: string
  expectedOutcome: string
  stage: JobStage
  confidence: number
  forces: JobForce[]
  quotes: InterviewQuote[]
}

export type FollowUpQuestion = {
  id: string
  jobId?: string
  question: string
  reason: string
}

export type InterviewAnalysis = {
  jobs: JtbdJob[]
  followUpQuestions: FollowUpQuestion[]
  sourceStats: {
    words: number
    sentences: number
  }
}
