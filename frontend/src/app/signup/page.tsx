"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { signup } from "@/lib/auth"

const ROLES = ["SRE", "Backend", "ML", "Product"]

export default function SignupPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [passwordConfirm, setPasswordConfirm] = useState("")
  const [role, setRole] = useState("SRE")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    if (password !== passwordConfirm) {
      setError("Passwords do not match")
      setLoading(false)
      return
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long")
      setLoading(false)
      return
    }

    try {
      await signup(email, password, role)
      router.push("/home")
    } catch (err: any) {
      setError(err.message || "Signup failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper font-patrick" style={{ backgroundImage: 'radial-gradient(#e5e0d8 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
      <div className="w-full max-w-md">
        <div className="bg-white border-2 border-pencil p-10 shadow-hard-lg rotate-[0.5deg] relative">
          {/* Tape decoration */}
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 w-16 h-6 bg-postit border border-muted-paper opacity-80 rotate-[2deg]" />

          <div className="text-center mb-8">
            <Link href="/" className="font-kalam font-bold text-3xl text-pencil hover:text-accent transition-colors">
              AIDog
            </Link>
            <p className="font-patrick text-pencil/60 mt-2">Create your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
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
                minLength={6}
                className="w-full px-4 py-3 bg-paper border-2 border-pencil font-patrick text-pencil placeholder-pencil/30 focus:outline-none focus:border-blue-pen shadow-hard transition-all"
                style={{ borderRadius: '4px' }}
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="passwordConfirm" className="block font-kalam text-pencil mb-2">
                Confirm Password
              </label>
              <input
                id="passwordConfirm"
                type="password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-3 bg-paper border-2 border-pencil font-patrick text-pencil placeholder-pencil/30 focus:outline-none focus:border-blue-pen shadow-hard transition-all"
                style={{ borderRadius: '4px' }}
                placeholder="••••••••"
              />
            </div>

            <div>
              <label className="block font-kalam text-pencil mb-3">
                Your Role
              </label>
              <div className="flex flex-wrap gap-2">
                {ROLES.map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setRole(r)}
                    className={`px-4 py-2 font-patrick border-2 border-pencil transition-all shadow-hard ${
                      role === r
                        ? "bg-pencil text-paper translate-x-[2px] translate-y-[2px] shadow-none"
                        : "bg-paper text-pencil hover:bg-muted-paper"
                    }`}
                    style={{ borderRadius: role === r ? '4px' : '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                  >
                    {r}
                  </button>
                ))}
              </div>
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
              {loading ? "Creating account..." : "Create Account"}
            </button>

            <p className="text-center font-patrick text-pencil/60 text-sm">
              Already have an account?{" "}
              <Link href="/login" className="text-blue-pen hover:underline font-kalam">
                Login
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
