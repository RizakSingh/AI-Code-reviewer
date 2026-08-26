export function Aurora() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-linear-to-br from-indigo-50 via-white to-pink-50">
      <div className="animate-blob absolute -top-32 -left-32 h-96 w-96 rounded-full bg-fuchsia-400/40 blur-3xl" />
      <div className="animate-blob absolute top-1/4 -right-32 h-112 w-md rounded-full bg-cyan-400/40 blur-3xl [animation-delay:4s]" />
      <div className="animate-blob absolute bottom-0 left-1/4 h-96 w-96 rounded-full bg-violet-400/40 blur-3xl [animation-delay:8s]" />
      <div className="animate-blob absolute bottom-1/3 right-1/4 h-72 w-72 rounded-full bg-amber-300/30 blur-3xl [animation-delay:12s]" />
    </div>
  )
}
