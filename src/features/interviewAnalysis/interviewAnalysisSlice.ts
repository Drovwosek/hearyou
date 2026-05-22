import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { analyzeInterview } from '../../application/jtbd/analyzeInterview'
import type { InterviewAnalysis } from '../../domain/jtbd/types'

type InterviewAnalysisState = {
  interviewText: string
  analysis: InterviewAnalysis | null
}

const sampleInterview = `Когда мы проводим серию кастдевов, после третьего интервью становится сложно держать в голове, какие работы повторяются.
Обычно я выписываю цитаты вручную, но потом боюсь потерять важный контекст.
Мне нужно быстрее видеть список работ пользователя, чтобы спланировать следующий раунд интервью.
Хочу понимать, какие вопросы дозадать, чтобы не тратить следующий созвон на очевидные вещи.`

const initialState: InterviewAnalysisState = {
  interviewText: sampleInterview,
  analysis: analyzeInterview(sampleInterview),
}

const interviewAnalysisSlice = createSlice({
  name: 'interviewAnalysis',
  initialState,
  reducers: {
    interviewTextChanged: (state, action: PayloadAction<string>) => {
      state.interviewText = action.payload
    },
    interviewAnalyzed: (state) => {
      state.analysis = analyzeInterview(state.interviewText)
    },
    analysisCleared: (state) => {
      state.analysis = null
    },
  },
})

export const { analysisCleared, interviewAnalyzed, interviewTextChanged } =
  interviewAnalysisSlice.actions

export default interviewAnalysisSlice.reducer
