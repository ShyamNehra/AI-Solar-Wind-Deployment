// WorkflowStepper.jsx — Reusable deployment workflow progress stepper
export const DEPLOYMENT_STEPS = [
  { id: 1, key: 'project_created',                    label: 'Project Created',            icon: '📁', color: 'emerald' },
  { id: 2, key: 'site_registered',                    label: 'Site Registration & GIS',    icon: '📍', color: 'teal' },
  { id: 3, key: 'assessment_completed',              label: 'AI Site Assessment',         icon: '🤖', color: 'violet' },
  { id: 4, key: 'site_ranking_completed',             label: 'Site Ranking',               icon: '🏆', color: 'amber' },
  { id: 5, key: 'deployment_optimization_completed', label: 'Deployment Optimization',     icon: '⚙️', color: 'blue' },
  { id: 6, key: 'forecasting_completed',              label: 'Energy Forecasting',          icon: '📈', color: 'cyan' },
  { id: 7, key: 'investment_completed',               label: 'Investment Recommendation', icon: '💰', color: 'green' },
  { id: 8, key: 'report_generated',                   label: 'Dashboard & Reports',        icon: '📊', color: 'purple' },
]

export function computeWorkflowState(workflowData, currentStep) {
  if (workflowData) {
    let firstIncompleteFound = false
    const steps = DEPLOYMENT_STEPS.map((step) => {
      const done = Boolean(workflowData[step.key])
      let active = false
      if (!done && !firstIncompleteFound) {
        active = true
        firstIncompleteFound = true
      }
      return {
        ...step,
        done,
        active,
        status: done ? 'Completed' : active ? 'In Progress' : 'Pending'
      }
    })
    const completedCount = steps.filter((s) => s.done).length
    const pct = workflowData.progress !== undefined
      ? workflowData.progress
      : Math.round((completedCount / DEPLOYMENT_STEPS.length) * 100)

    const activeStepObj = steps.find((s) => s.active) || steps.find((s) => !s.done) || steps[steps.length - 1]

    return { steps, completedCount, pct, activeStep: activeStepObj }
  }

  // Fallback to legacy currentStep
  const completedCount = Math.max(0, Math.min(DEPLOYMENT_STEPS.length, currentStep - 1))
  const pct = Math.round((completedCount / DEPLOYMENT_STEPS.length) * 100)
  const steps = DEPLOYMENT_STEPS.map((step) => {
    const done = step.id < currentStep
    const active = step.id === currentStep
    return {
      ...step,
      done,
      active,
      status: done ? 'Completed' : active ? 'In Progress' : 'Pending'
    }
  })
  const activeStepObj = steps[Math.min(currentStep - 1, DEPLOYMENT_STEPS.length - 1)]

  return { steps, completedCount, pct, activeStep: activeStepObj }
}

export default function WorkflowStepper({ workflowData = null, currentStep = 1, compact = false }) {
  const { steps, completedCount, pct, activeStep } = computeWorkflowState(workflowData, currentStep)

  if (compact) {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span className="font-semibold text-gray-700">{activeStep?.label}</span>
          <span className="font-bold text-emerald-600">{completedCount}/{DEPLOYMENT_STEPS.length} Completed</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-emerald-500 to-teal-500 h-2 rounded-full transition-all duration-700"
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="flex gap-1 flex-wrap">
          {steps.map((step) => (
            <div
              key={step.id}
              title={`${step.label} (${step.status})`}
              className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] transition-all ${
                step.done ? 'bg-emerald-500 text-white' :
                step.active ? 'bg-emerald-100 text-emerald-700 ring-2 ring-emerald-400' :
                'bg-gray-100 text-gray-400'
              }`}
            >
              {step.done ? '✓' : step.id}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-bold text-gray-700">Deployment Progress</span>
        <span className="text-sm font-bold text-emerald-600">{pct}%</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-3">
        <div
          className="bg-gradient-to-r from-emerald-500 to-teal-400 h-3 rounded-full transition-all duration-700 shadow-sm"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Step list */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-4 bottom-4 w-0.5 bg-gray-100" />
        <div className="space-y-2">
          {steps.map((step) => (
            <div key={step.id} className={`relative flex items-center gap-3 pl-10 py-2 rounded-xl transition-all ${
              step.active ? 'bg-emerald-50 border border-emerald-100' : ''
            }`}>
              {/* Circle */}
              <div className={`absolute left-2 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold border-2 transition-all ${
                step.done   ? 'bg-emerald-500 border-emerald-500 text-white' :
                step.active ? 'bg-white border-emerald-500 text-emerald-600' :
                         'bg-white border-gray-200 text-gray-400'
              }`}>
                {step.done ? '✓' : step.id}
              </div>
              <span className="text-base">{step.icon}</span>
              <span className={`text-sm font-medium ${
                step.done ? 'text-emerald-600' : step.active ? 'text-gray-900 font-semibold' : 'text-gray-400'
              }`}>
                {step.label}
              </span>
              {step.active && <span className="ml-auto mr-2 text-[10px] font-bold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full">IN PROGRESS</span>}
              {step.done && <span className="ml-auto mr-2 text-[10px] font-bold text-emerald-500">✓ Done</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
