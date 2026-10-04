import './_group.css';

export function Current() {
  return (
    <div
      className="min-h-[100dvh] flex flex-col"
      style={{
        backgroundColor: 'hsl(240 10% 4%)',
        color: 'hsl(0 0% 98%)',
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <header
        className="flex items-center justify-between px-6 py-4"
        style={{ borderBottom: '1px solid hsl(240 10% 12% / 0.5)' }}
      >
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-md flex items-center justify-center"
            style={{
              backgroundColor: 'hsl(30 100% 60% / 0.1)',
              color: 'hsl(30 100% 60%)',
            }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/></svg>
          </div>
          <span className="font-mono font-semibold tracking-tight text-lg">
            OpenCode<span style={{ color: 'hsl(30 100% 60%)' }}>_</span>
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            className="px-3 py-1.5 text-sm rounded-md"
            style={{ backgroundColor: 'transparent', color: 'hsl(0 0% 98%)' }}
          >
            Sign in
          </button>
          <button
            className="px-3 py-1.5 text-sm rounded-md"
            style={{
              backgroundColor: 'hsl(30 100% 60%)',
              color: 'hsl(240 10% 4%)',
            }}
          >
            Get started
          </button>
        </div>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center mb-8"
          style={{
            backgroundColor: 'hsl(30 100% 60% / 0.1)',
            color: 'hsl(30 100% 60%)',
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/></svg>
        </div>
        <h1 className="text-5xl font-bold tracking-tight mb-4">
          Think in code.
        </h1>
        <p
          className="text-lg max-w-lg mb-10"
          style={{ color: 'hsl(240 5% 65%)' }}
        >
          A focused workspace for coding conversations. Create sessions,
          ask questions, and keep your knowledge organized.
        </p>
        <div className="flex items-center gap-4">
          <button
            className="flex items-center gap-2 px-6 py-3 rounded-md text-base font-medium"
            style={{
              backgroundColor: 'hsl(30 100% 60%)',
              color: 'hsl(240 10% 4%)',
            }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Create your workspace
          </button>
          <button
            className="px-6 py-3 rounded-md text-base font-medium"
            style={{
              backgroundColor: 'transparent',
              color: 'hsl(0 0% 98%)',
              border: '1px solid hsl(240 10% 12%)',
            }}
          >
            Sign in
          </button>
        </div>
      </main>
    </div>
  );
}
