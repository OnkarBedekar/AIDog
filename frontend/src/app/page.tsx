import Link from "next/link"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-paper font-patrick" style={{ backgroundImage: 'radial-gradient(#e5e0d8 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-6">
        <span className="font-kalam font-bold text-2xl text-pencil">AIDog</span>
        <div className="flex gap-4">
          <Link href="/login" className="px-4 py-2 text-pencil hover:text-blue-pen transition-colors font-patrick">
            Login
          </Link>
          <Link
            href="/signup"
            className="px-5 py-2 bg-pencil text-paper font-patrick rounded-wobbly shadow-hard hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg transition-all"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-8 pt-20 pb-32 text-center relative">
        {/* Decorative bouncing circle */}
        <div
          className="hidden lg:block absolute right-16 top-8 w-20 h-20 bg-postit border-2 border-pencil rounded-full shadow-hard animate-bounce"
          style={{ animationDuration: '3s' }}
        />

        <div className="inline-block bg-postit border-2 border-pencil px-4 py-1 rounded-wobbly shadow-hard mb-8 rotate-[-1deg]">
          <span className="font-patrick text-pencil text-sm">Beta — Now with real Datadog integration</span>
        </div>

        <h1 className="font-kalam font-bold text-6xl lg:text-7xl text-pencil leading-tight mb-6">
          Datadog that
          <br />
          <span className="text-accent">thinks like you</span>
        </h1>

        <p className="font-patrick text-xl text-pencil/70 max-w-2xl mx-auto mb-12 leading-relaxed">
          AIDog learns how <em>you</em> investigate incidents — your workflows, your patterns, your instincts —
          then guides you step by step when things break.
        </p>

        <div className="flex items-center justify-center gap-6 flex-wrap">
          <Link
            href="/signup"
            className="px-8 py-4 bg-accent text-paper font-kalam font-bold text-lg rounded-wobbly shadow-hard-red hover:translate-x-[-3px] hover:translate-y-[-3px] hover:shadow-hard-lg transition-all active:translate-x-0 active:translate-y-0 active:shadow-none"
          >
            Try Demo
          </Link>

          {/* Hand-drawn arrow */}
          <svg width="48" height="32" viewBox="0 0 48 32" className="hidden sm:block text-pencil" fill="none">
            <path d="M2 16 Q12 6 28 16 Q38 22 46 12" stroke="#2d2d2d" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
            <path d="M40 8 L46 12 L40 16" stroke="#2d2d2d" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
          </svg>

          <a
            href="#how-it-works"
            className="px-8 py-4 bg-paper text-pencil font-kalam font-bold text-lg border-2 border-pencil rounded-wobbly-alt shadow-hard hover:translate-x-[-3px] hover:translate-y-[-3px] hover:shadow-hard-lg transition-all active:translate-x-0 active:translate-y-0 active:shadow-none"
          >
            See How It Works
          </a>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="max-w-5xl mx-auto px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="font-kalam font-bold text-4xl text-pencil mb-3">How It Works</h2>
          <div className="w-24 h-1 bg-pencil mx-auto" style={{ borderRadius: '2px' }} />
        </div>

        <div className="relative">
          {/* Squiggly connecting line (desktop only) */}
          <svg
            className="hidden lg:block absolute top-16 left-[16%] w-[68%]"
            height="30"
            viewBox="0 0 400 30"
            fill="none"
            preserveAspectRatio="none"
          >
            <path
              d="M0 15 Q50 5 100 15 Q150 25 200 15 Q250 5 300 15 Q350 25 400 15"
              stroke="#2d2d2d"
              strokeWidth="2"
              strokeDasharray="6 4"
              fill="none"
            />
          </svg>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-12">
            {[
              {
                step: "01",
                icon: "👁",
                title: "Datadog watches your services",
                description: "We connect to your Datadog account and monitor your services, metrics, traces, and logs in real time.",
                rotate: "-rotate-1",
              },
              {
                step: "02",
                icon: "🧠",
                title: "We learn how YOU debug",
                description: "As you investigate incidents, AIDog observes your patterns — which queries you run first, what you check, what you skip.",
                rotate: "rotate-1",
              },
              {
                step: "03",
                icon: "🧭",
                title: "Get guided next steps during incidents",
                description: "When something breaks, AIDog gives you personalized investigation steps based on how you've worked before.",
                rotate: "-rotate-1",
              },
            ].map((card, idx) => (
              <div key={idx} className={`relative bg-white border-2 border-pencil p-8 shadow-hard-lg ${card.rotate} tape`}>
                {/* Step number in rough circle */}
                <div className="w-10 h-10 bg-postit border-2 border-pencil rounded-full flex items-center justify-center font-kalam font-bold text-pencil mb-4 shadow-hard">
                  {card.step}
                </div>
                <div className="text-4xl mb-4">{card.icon}</div>
                <h3 className="font-kalam font-bold text-xl text-pencil mb-3">{card.title}</h3>
                <p className="font-patrick text-pencil/70 leading-relaxed">{card.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="max-w-3xl mx-auto px-8 py-16 text-center">
        <div className="bg-postit border-2 border-pencil p-12 shadow-hard-lg rotate-[-0.5deg]">
          <h2 className="font-kalam font-bold text-4xl text-pencil mb-4">
            Ready to investigate smarter?
          </h2>
          <p className="font-patrick text-pencil/70 mb-8">
            Connect your Datadog in minutes. No credit card required.
          </p>
          <Link
            href="/signup"
            className="inline-block px-10 py-4 bg-accent text-paper font-kalam font-bold text-xl rounded-wobbly shadow-hard-red hover:translate-x-[-3px] hover:translate-y-[-3px] hover:shadow-hard-lg transition-all"
          >
            Start Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t-2 border-pencil/20 py-12 text-center">
        <p className="font-kalam text-pencil/50 text-lg">
          Built for engineers, by engineers
        </p>
        <p className="font-patrick text-pencil/30 text-sm mt-2">
          AIDog — Personalized Observability Copilot
        </p>
      </footer>
    </div>
  )
}
