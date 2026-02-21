"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import * as Dialog from "@radix-ui/react-dialog"
import { Command } from "cmdk"

export function CommandMenu() {
  const [open, setOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl bg-slate-800 border border-slate-700 rounded-lg shadow-2xl z-50">
          <Command className="p-2">
            <Command.Input
              placeholder="Search incidents, services, shortcuts..."
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Command.List className="max-h-96 overflow-y-auto p-2">
              <Command.Empty className="py-8 text-center text-slate-400">
                No results found.
              </Command.Empty>
              <Command.Group heading="Navigation">
                <Command.Item
                  onSelect={() => {
                    router.push("/home")
                    setOpen(false)
                  }}
                  className="px-4 py-2 rounded-lg hover:bg-slate-700 cursor-pointer"
                >
                  🏠 Home
                </Command.Item>
                <Command.Item
                  onSelect={() => {
                    router.push("/incidents")
                    setOpen(false)
                  }}
                  className="px-4 py-2 rounded-lg hover:bg-slate-700 cursor-pointer"
                >
                  🚨 Incidents
                </Command.Item>
                <Command.Item
                  onSelect={() => {
                    router.push("/studio")
                    setOpen(false)
                  }}
                  className="px-4 py-2 rounded-lg hover:bg-slate-700 cursor-pointer"
                >
                  ⚙️ Studio
                </Command.Item>
              </Command.Group>
            </Command.List>
          </Command>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
