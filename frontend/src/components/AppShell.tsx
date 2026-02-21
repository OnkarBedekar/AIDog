"use client"

import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { logout } from "@/lib/auth"
import Link from "next/link"
import { CommandMenu } from "./CommandMenu"
import { CopilotPanel } from "./CopilotPanel"

const navigation = [
  { name: "Home", href: "/home", icon: "🏠" },
  { name: "Incidents", href: "/incidents", icon: "🚨" },
  { name: "Studio", href: "/studio", icon: "⚙️" },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [copilotOpen, setCopilotOpen] = useState(false)

  if (pathname === "/login" || pathname === "/signup" || pathname === "/") {
    return <>{children}</>
  }

  return (
    <div
      className="min-h-screen bg-paper"
      style={{ backgroundImage: 'radial-gradient(#e5e0d8 1px, transparent 1px)', backgroundSize: '24px 24px' }}
    >
      <div className="flex h-screen">
        {/* Sidebar */}
        <aside className="w-64 bg-paper border-r-2 border-dashed border-pencil flex flex-col" style={{ borderRight: '2px dashed #2d2d2d' }}>
          <div className="p-6 border-b-2 border-pencil">
            <h1 className="font-kalam font-bold text-2xl text-pencil">
              AIDog
            </h1>
            <p className="font-patrick text-pencil/50 text-xs mt-1">Observability Copilot</p>
          </div>

          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 font-patrick transition-all ${
                  pathname === item.href
                    ? "bg-postit border-2 border-pencil shadow-hard text-pencil"
                    : "text-pencil/70 hover:bg-muted-paper hover:text-pencil"
                }`}
                style={pathname === item.href ? { borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' } : { borderRadius: '4px' }}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="font-kalam">{item.name}</span>
              </Link>
            ))}
          </nav>

          <div className="p-4 border-t-2 border-pencil">
            <button
              onClick={() => setCopilotOpen(!copilotOpen)}
              className="w-full px-4 py-2 mb-2 bg-blue-pen text-paper font-patrick border-2 border-pencil shadow-hard-blue hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all"
              style={{ borderRadius: '4px' }}
            >
              🤖 Copilot
            </button>
            <button
              onClick={() => {
                logout()
                router.push("/login")
              }}
              className="w-full px-4 py-2 text-pencil/60 hover:bg-muted-paper font-patrick transition-colors"
              style={{ borderRadius: '4px' }}
            >
              Logout
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            <CommandMenu />
            {children}
          </div>
        </main>

        {/* Copilot Panel */}
        <CopilotPanel open={copilotOpen} onOpenChange={setCopilotOpen} />
      </div>
    </div>
  )
}
