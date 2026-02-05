import { useEffect, useCallback, useRef } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { statsService } from '../services/api'
import { DashboardResponse, SystemStatsResponse } from '../types'

interface UseRealTimeDataOptions {
  enabled?: boolean
  interval?: number
  onError?: (error: Error) => void
}

export function useDashboardData(options: UseRealTimeDataOptions = {}) {
  const { enabled = true, interval = 5000, onError } = options
  const { data, isLoading, error, refetch } = useQuery<DashboardResponse>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await statsService.dashboard()
      return response
    },
    enabled,
    refetchInterval: interval,
    retry: 1,
    staleTime: interval - 1000,
  })

  useEffect(() => {
    if (error && onError) {
      onError(error as Error)
    }
  }, [error, onError])

  return {
    data,
    isLoading,
    error,
    refetch,
    isStale: !data,
  }
}

export function useSystemStats(options: UseRealTimeDataOptions = {}) {
  const { enabled = true, interval = 5000, onError } = options

  const { data, isLoading, error, refetch } = useQuery<SystemStatsResponse>({
    queryKey: ['system-stats'],
    queryFn: async () => {
      const response = await statsService.system()
      return response
    },
    enabled,
    refetchInterval: interval,
    retry: 1,
    staleTime: interval - 1000,
  })

  useEffect(() => {
    if (error && onError) {
      onError(error as Error)
    }
  }, [error, onError])

  return {
    data,
    isLoading,
    error,
    refetch,
  }
}

export function useHistoricalStats(
  period: string = '1h',
  options: UseRealTimeDataOptions = {}
) {
  const { enabled = true, onError } = options

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['system-stats-history', period],
    queryFn: async () => {
      const response = await statsService.history(period, false)
      return response
    },
    enabled,
    staleTime: 60000,
  })

  useEffect(() => {
    if (error && onError) {
      onError(error as Error)
    }
  }, [error, onError])

  return {
    data,
    isLoading,
    error,
    refetch,
  }
}

export function useAutoRefresh(
  enabled: boolean = true,
  interval: number = 5000
) {
  const queryClient = useQueryClient()
  const intervalRef = useRef<number | null>(null)

  const startRefresh = useCallback(() => {
    if (!enabled || intervalRef.current) return

    intervalRef.current = window.setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
    }, interval)
  }, [enabled, interval, queryClient])

  const stopRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  useEffect(() => {
    if (enabled) {
      startRefresh()
    } else {
      stopRefresh()
    }

    return () => {
      stopRefresh()
    }
  }, [enabled, startRefresh, stopRefresh])

  return {
    startRefresh,
    stopRefresh,
    refreshNow: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
    },
  }
}
