import { useState } from 'react'
import { motion } from 'motion/react'
import { ArrowRight, CheckCircle2, Database, FileJson2, ShieldCheck, Workflow } from 'lucide-react'

const sourceSchemas = ['legacy_crm', 'hr_staging', 'finance_raw']
const targetSchemas = ['core_crm', 'hr_prod', 'finance_curated']
const migrationChecks = [
  'Entity mapping validated',
  'Data type compatibility review',
  'Compliance and retention checks',
  'Zero-downtime cutover plan',
]

function App() {
  const [planGenerated, setPlanGenerated] = useState(false)
  const schemaMappings = sourceSchemas.map((source, index) => ({
    source,
    target: targetSchemas[index] ?? 'Needs target schema',
  }))

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#f4efe9_0%,#f4efe9_35%,#eee7dc_100%)] px-6 py-10 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <motion.header
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
        >
          <div>
            <p className="mb-2 inline-flex items-center rounded-full border border-amber-200 bg-amber-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-amber-900">
              Schema migration blueprint
            </p>
            <h1 className="text-4xl font-black tracking-tight md:text-5xl">
              Data mapping for safe enterprise migration
            </h1>
          </div>
          <button
            type="button"
            onClick={() => setPlanGenerated(true)}
            className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-700"
          >
            {planGenerated ? 'Regenerate plan' : 'Generate plan'}
            <ArrowRight className="h-4 w-4" />
          </button>
        </motion.header>

        <section className="grid gap-6 md:grid-cols-3">
          <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm backdrop-blur-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-100 text-violet-700">
              <Database className="h-6 w-6" />
            </div>
            <p className="text-sm text-slate-500">Source schemas</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {sourceSchemas.map((schema) => (
                <span key={schema} className="rounded-full bg-violet-50 px-3 py-1 text-sm font-medium text-violet-700">
                  {schema}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm backdrop-blur-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700">
              <Workflow className="h-6 w-6" />
            </div>
            <p className="text-sm text-slate-500">Target schemas</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {targetSchemas.map((schema) => (
                <span key={schema} className="rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700">
                  {schema}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm backdrop-blur-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-100 text-amber-700">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <p className="text-sm text-slate-500">Platform</p>
            <div className="mt-3 rounded-2xl bg-slate-100 px-3 py-2 text-base font-semibold text-slate-800">
              PostgreSQL
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded-3xl border border-slate-200 bg-white/85 p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <FileJson2 className="h-5 w-5 text-slate-700" />
              <h2 className="text-xl font-bold">Business context</h2>
            </div>
            <p className="text-base leading-7 text-slate-700">
              Consolidate legacy CRM, HR, and finance data into a governed production platform to improve reporting quality,
              reduce operational drift, and preserve compliance controls during a controlled zero-downtime migration.
            </p>

            <div className="mt-6 rounded-2xl bg-slate-50 p-4">
              <p className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">Migration safeguards</p>
              <ul className="space-y-3">
                {migrationChecks.map((item) => (
                  <li key={item} className="flex items-center gap-3 text-slate-700">
                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-900 p-6 text-slate-100 shadow-lg shadow-slate-900/10">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Migration checklist</p>
            <div className="mt-5 space-y-4">
              {[
                'Inventory source-to-target mappings',
                'Normalize key identifiers and timestamps',
                'Review PII and retention constraints',
                'Establish reversible rollback snapshots',
              ].map((step, index) => (
                <div key={step} className="flex items-center gap-3 rounded-2xl bg-white/5 p-3">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-400 text-xs font-bold text-slate-900">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {planGenerated && (
          <motion.section
            aria-live="polite"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 rounded-3xl border border-emerald-200 bg-white/90 p-6 shadow-sm"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-emerald-700">
                  Draft migration plan
                </p>
                <h2 className="mt-1 text-2xl font-bold text-slate-900">Review mappings before execution</h2>
              </div>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-900">
                Example mappings - validate against real schemas
              </span>
            </div>

            <div className="mt-5 overflow-x-auto rounded-2xl border border-slate-200">
              <table className="w-full min-w-[30rem] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th scope="col" className="px-4 py-3">Source schema</th>
                    <th scope="col" className="px-4 py-3">Target schema</th>
                    <th scope="col" className="px-4 py-3">Mapping status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {schemaMappings.map(({ source, target }) => (
                    <tr key={source}>
                      <td className="px-4 py-3 font-medium text-slate-800">{source}</td>
                      <td className="px-4 py-3 font-medium text-slate-800">{target}</td>
                      <td className="px-4 py-3 text-amber-800">Proposed by position; confirm entity and column mappings</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <ol className="mt-5 grid gap-3 text-sm text-slate-700 md:grid-cols-2">
              <li className="rounded-xl bg-slate-50 p-4"><strong>1. Discover:</strong> inventory tables, columns, keys, and row counts.</li>
              <li className="rounded-xl bg-slate-50 p-4"><strong>2. Map:</strong> verify entity relationships, types, nullability, and transformations.</li>
              <li className="rounded-xl bg-slate-50 p-4"><strong>3. Validate:</strong> reconcile counts, sample records, constraints, and privacy rules.</li>
              <li className="rounded-xl bg-slate-50 p-4"><strong>4. Cut over:</strong> rehearse rollback, synchronize deltas, then switch traffic after approval.</li>
            </ol>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              This is a local planning draft only. It does not connect to databases, inspect actual schemas, or execute a migration.
            </p>
          </motion.section>
        )}
      </div>
    </main>
  )
}

export default App
