"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { AppShell } from "@/components/AppShell"
import { HomeOverview } from "@/components/HomeOverview"

export default function HomePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["home-overview"],
    queryFn: () => apiClient.get("/home/overview"),
    refetchInterval: 30_000, // refresh every 30 seconds
    refetchIntervalInBackground: false,
  })

  return (
    <AppShell>
      <HomeOverview data={data} isLoading={isLoading} />
    </AppShell>
  )
}
