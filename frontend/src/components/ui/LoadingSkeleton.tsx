export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`skeleton h-4 ${className}`} />
}

export function CardSkeleton() {
  return (
    <div className="card space-y-3 animate-pulse">
      <Skeleton className="w-1/3 h-3" />
      <Skeleton className="w-2/3 h-6" />
      <Skeleton className="w-1/2 h-3" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 animate-pulse">
          <Skeleton className="flex-1 h-8" />
          <Skeleton className="w-24 h-8" />
          <Skeleton className="w-20 h-8" />
        </div>
      ))}
    </div>
  )
}
