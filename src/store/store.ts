import { configureStore } from '@reduxjs/toolkit'
import interviewAnalysisReducer from '../features/interviewAnalysis/interviewAnalysisSlice'

export const store = configureStore({
  reducer: {
    interviewAnalysis: interviewAnalysisReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
