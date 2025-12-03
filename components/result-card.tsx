import { Card } from "@/components/ui/card"
import { CheckCircle2, AlertTriangle, Flag } from 'lucide-react'
import { cn } from "@/lib/utils"

interface ResultCardProps {
  result: {
    safe: boolean
    message: string
    reasoning?: string
    emails: boolean
    address: boolean
    phoneNumbers: boolean
    licensePlates: boolean
    redactionSuggestions?: string[]
  }
  onReport?: () => void
}

export function ResultCard({ result, onReport }: ResultCardProps) {
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
            <div className="space-y-3 mt-4">
              <p className="text-sm font-medium text-foreground">PII Detection Results:</p>
              <div className="grid grid-cols-2 gap-3">
                <div className={cn(
                  "flex items-center gap-2 p-2 rounded-md",
                  result.emails ? "bg-destructive/10" : "bg-success/10"
                )}>
                  <span className={cn(
                    "text-xs font-medium",
                    result.emails ? "text-destructive" : "text-success"
                  )}>
                    {result.emails ? "✗" : "✓"}
                  </span>
                  <span className="text-sm text-foreground">Emails</span>
                </div>
                <div className={cn(
                  "flex items-center gap-2 p-2 rounded-md",
                  result.address ? "bg-destructive/10" : "bg-success/10"
                )}>
                  <span className={cn(
                    "text-xs font-medium",
                    result.address ? "text-destructive" : "text-success"
                  )}>
                    {result.address ? "✗" : "✓"}
                  </span>
                  <span className="text-sm text-foreground">Address</span>
                </div>
                <div className={cn(
                  "flex items-center gap-2 p-2 rounded-md",
                  result.phoneNumbers ? "bg-destructive/10" : "bg-success/10"
                )}>
                  <span className={cn(
                    "text-xs font-medium",
                    result.phoneNumbers ? "text-destructive" : "text-success"
                  )}>
                    {result.phoneNumbers ? "✗" : "✓"}
                  </span>
                  <span className="text-sm text-foreground">Phone Numbers</span>
                </div>
                <div className={cn(
                  "flex items-center gap-2 p-2 rounded-md",
                  result.licensePlates ? "bg-destructive/10" : "bg-success/10"
                )}>
                  <span className={cn(
                    "text-xs font-medium",
                    result.licensePlates ? "text-destructive" : "text-success"
                  )}>
                    {result.licensePlates ? "✗" : "✓"}
                  </span>
                  <span className="text-sm text-foreground">License Plates</span>
                </div>
              </div>
            </div>
            {!result.safe && result.redactionSuggestions && result.redactionSuggestions.length > 0 && (
              <div className="space-y-2 mt-4 pt-4 border-t border-border">
                <p className="text-sm font-medium text-foreground">Redaction Suggestions:</p>
                <ul className="space-y-1.5">
                  {result.redactionSuggestions.map((suggestion, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-primary" />
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="mt-4 pt-4 border-t border-border">
              <button
                onClick={onReport}
                className="cursor-pointer flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors rounded-md hover:bg-muted/50"
                type="button"
              >
                <Flag className="h-4 w-4" />
                <span>Report Incorrect Analysis</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
