import {
  analysisCleared,
  interviewAnalyzed,
  interviewTextChanged,
} from './interviewAnalysisSlice'
import { jobStages } from '../../domain/jtbd/jtbdFramework'
import { useAppDispatch, useAppSelector } from '../../store/hooks'

const getStageLabel = (stageId: string): string =>
  jobStages.find((stage) => stage.id === stageId)?.label ?? stageId

export const InterviewWorkspace = () => {
  const dispatch = useAppDispatch()
  const { analysis, interviewText } = useAppSelector(
    (state) => state.interviewAnalysis,
  )

  return (
    <main className="workspace">
      <section className="input-pane" aria-labelledby="input-title">
        <div className="section-heading">
          <p className="eyebrow">JTBD interview input</p>
          <h1 id="input-title">Interview transformer</h1>
        </div>

        <textarea
          aria-label="Interview transcript"
          value={interviewText}
          onChange={(event) => dispatch(interviewTextChanged(event.target.value))}
          placeholder="Paste an interview transcript here..."
        />

        <div className="toolbar">
          <button type="button" onClick={() => dispatch(interviewAnalyzed())}>
            Analyze JTBD
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => dispatch(analysisCleared())}
          >
            Clear result
          </button>
        </div>
      </section>

      <section className="result-pane" aria-label="Analysis result">
        <div className="result-grid">
          <section className="panel" aria-labelledby="jobs-title">
            <div className="section-heading compact">
              <p className="eyebrow">Structured jobs</p>
              <h2 id="jobs-title">Jobs to be done</h2>
            </div>

            <div className="job-list">
              {analysis?.jobs.length ? (
                analysis.jobs.map((job) => (
                  <article className="job-card" key={job.id}>
                    <div className="job-card-header">
                      <h3>{job.title}</h3>
                      <span>{getStageLabel(job.stage)}</span>
                    </div>
                    <p className="job-statement">{job.statement}</p>
                    <dl>
                      <div>
                        <dt>Situation</dt>
                        <dd>{job.situation}</dd>
                      </div>
                      <div>
                        <dt>Motivation</dt>
                        <dd>{job.motivation}</dd>
                      </div>
                      <div>
                        <dt>Outcome</dt>
                        <dd>{job.expectedOutcome}</dd>
                      </div>
                    </dl>
                    <blockquote>{job.quotes[0]?.text}</blockquote>
                  </article>
                ))
              ) : (
                <p className="empty-state">
                  Paste an interview with customer situations, struggles, goals, or
                  outcomes to extract jobs.
                </p>
              )}
            </div>
          </section>

          <section className="panel" aria-labelledby="questions-title">
            <div className="section-heading compact">
              <p className="eyebrow">Next round</p>
              <h2 id="questions-title">Follow-up questions</h2>
            </div>

            <ol className="question-list">
              {analysis?.followUpQuestions.length ? (
                analysis.followUpQuestions.map((item) => (
                  <li key={item.id}>
                    <strong>{item.question}</strong>
                    <span>{item.reason}</span>
                  </li>
                ))
              ) : (
                <li className="empty-state">
                  Questions will appear after JTBD analysis.
                </li>
              )}
            </ol>
          </section>
        </div>
      </section>
    </main>
  )
}
