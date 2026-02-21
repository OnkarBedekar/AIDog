"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { AppShell } from "@/components/AppShell"
import { IncidentRoom } from "@/components/IncidentRoom"

export default function IncidentDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const { id } = params
  const { data, isLoading } = useQuery({
    queryKey: ["incident", id],
    queryFn: () => apiClient.get(`/incidents/${id}`),
  })

  return (
    <AppShell>
      <IncidentRoom data={data} isLoading={isLoading} incidentId={id} />
    </AppShell>
  )
}
