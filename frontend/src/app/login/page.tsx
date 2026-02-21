"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { login } from "@/lib/auth"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      await login(email, password)
      router.push("/home")
    } catch (err: any) {
      setError(err.message || "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper font-patrick" style={{ backgroundImage: 'radial-gradient(#e5e0d8 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
      <div className="w-full max-w-md">
        <div className="bg-white border-2 border-pencil p-10 shadow-hard-lg rotate-[-0.5deg] relative">
          {/* Tape decoration */}
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 w-16 h-6 bg-postit border border-muted-paper opacity-80 rotate-[-2deg]" />

          <div className="text-center mb-8">
            <Link href="/" className="font-kalam font-bold text-3xl text-pencil hover:text-accent transition-colors">
              AIDog
            </Link>
            <p className="font-patrick text-pencil/60 mt-2">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block font-kalam text-pencil mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-paper border-2 border-pencil font-patrick text-pencil placeholder-pencil/30 focus:outline-none focus:border-blue-pen shadow-hard transition-all"
                style={{ borderRadius: '4px' }}
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block font-kalam text-pencil mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 bg-paper border-2 border-pencil font-patrick text-pencil placeholder-pencil/30 focus:outline-none focus:border-blue-pen shadow-hard transition-all"
                style={{ borderRadius: '4px' }}
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="p-3 bg-postit border-2 border-accent text-accent font-patrick text-sm shadow-hard-red">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-accent text-paper font-kalam font-bold text-lg border-2 border-pencil rounded-wobbly shadow-hard-red hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg transition-all active:translate-x-0 active:translate-y-0 active:shadow-none disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>

            <p className="text-center font-patrick text-pencil/60 text-sm">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-blue-pen hover:underline font-kalam">
                Sign up
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
