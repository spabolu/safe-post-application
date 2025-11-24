import { Card } from "@/components/ui/card"
import { CheckCircle2, AlertTriangle } from 'lucide-react'
import { cn } from "@/lib/utils"

interface ResultCardProps {
  result: {
    safe: boolean
    message: string
    reasoning?: string
    details?: string[]
  }
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <Card
      className={cn(
        "overflow-hidden border-2 transition-all duration-300 animate-in fade-in slide-in-from-bottom-4",
        result.safe ? "border-success bg-success/5" : "border-destructive bg-destructive/5",
      )}
    >
      <div className="p-6 space-y-4">
        <div className="flex items-start gap-4">
          <div className={cn("rounded-full p-2", result.safe ? "bg-success/10" : "bg-destructive/10")}>
            {result.safe ? (
              <CheckCircle2 className="h-6 w-6 text-success" />
            ) : (
              <AlertTriangle className="h-6 w-6 text-destructive" />
            )}
          </div>
          <div className="flex-1 space-y-2">
            <h3 className={cn("text-xl font-semibold", result.safe ? "text-success" : "text-destructive")}>
              {result.message}
            </h3>
            {result.reasoning && <p className="text-muted-foreground">{result.reasoning}</p>}
            {result.details && result.details.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-foreground">
                  {result.safe ? "Analysis complete:" : "Issues detected:"}
                </p>
                <ul className="space-y-1">
                  {result.details.map((detail, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-muted-foreground" />
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
