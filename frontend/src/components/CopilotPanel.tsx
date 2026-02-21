"use client"

import * as Dialog from "@radix-ui/react-dialog"

interface CopilotPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CopilotPanel({ open, onOpenChange }: CopilotPanelProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-pencil/10 z-40" />
        <Dialog.Content
          className="fixed right-0 top-0 h-full w-96 bg-paper border-l-2 border-pencil shadow-hard-lg z-40 overflow-auto"
          style={{ borderLeft: '2px solid #2d2d2d' }}
        >
          <div className="p-6">
            <div className="flex items-center justify-between mb-6 border-b-2 border-pencil pb-4">
              <h2 className="font-kalam font-bold text-2xl text-pencil">AI Copilot</h2>
              <Dialog.Close className="font-patrick text-pencil/60 hover:text-pencil text-xl transition-colors">
                ✕
              </Dialog.Close>
            </div>

            <div className="space-y-4">
              <div
                className="p-4 bg-postit border-2 border-pencil shadow-hard rotate-[-0.5deg]"
                style={{ borderRadius: '4px' }}
              >
                <h3 className="font-kalam font-bold text-pencil mb-2">
                  What&apos;s happening
                </h3>
                <p className="font-patrick text-pencil/70 text-sm">
                  Monitoring system health and analyzing recent incidents...
                </p>
              </div>

              <div
                className="p-4 bg-white border-2 border-pencil shadow-hard rotate-[0.5deg]"
                style={{ borderRadius: '4px' }}
              >
                <h3 className="font-kalam font-bold text-pencil mb-2">
                  Suggested action
                </h3>
                <p className="font-patrick text-pencil/70 text-sm mb-3">
                  Review the latency spike in payment-service
                </p>
                <button
                  className="w-full px-4 py-2 bg-accent text-paper font-kalam font-bold border-2 border-pencil shadow-hard-red hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg transition-all active:translate-x-0 active:translate-y-0 active:shadow-none"
                  style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                >
                  Take action
                </button>
              </div>

              <div
                className="p-4 bg-white border-2 border-dashed border-muted-paper"
                style={{ borderRadius: '4px' }}
              >
                <h3 className="font-kalam text-pencil/60 mb-3 text-sm">Recent investigations</h3>
                <p className="font-patrick text-pencil/40 text-xs italic">
                  Your investigation patterns will appear here as you debug incidents.
                </p>
              </div>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
