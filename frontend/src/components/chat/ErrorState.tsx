/**
 * Error State UI Components
 * Feature: 009-chatkit-frontend
 * Task: T071 [Phase 9]
 *
 * Purpose: Reusable error state components for different error types
 * - NetworkError: Connection lost
 * - RateLimitError: Too many requests
 * - AuthError: Authentication required
 * - TimeoutError: Request timeout
 * - BackendUnavailable: 502/503 errors
 * - UnknownError: Generic fallback
 *
 * Based on: contracts/error-messages.yaml
 */

'use client';

import { ReactNode } from 'react';
import {
  WifiOff,
  Clock,
  Lock,
  Server,
  AlertTriangle,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorStateProps {
  title: string;
  message: string;
  icon: ReactNode;
  actions?: ReactNode;
  details?: string;
}

function ErrorStateBase({ title, message, icon, actions, details }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6 max-w-sm">
        {message}
      </p>
      {details && (
        <p className="text-xs text-gray-500 dark:text-gray-500 mb-4 font-mono">
          {details}
        </p>
      )}
      {actions && <div className="flex flex-col sm:flex-row gap-3">{actions}</div>}
    </div>
  );
}

/**
 * Network Error State
 * Shown when connection is lost
 */
export function NetworkError({ onRetry }: { onRetry: () => void }) {
  return (
    <ErrorStateBase
      icon={<WifiOff className="h-12 w-12 text-gray-400" />}
      title="Connection Lost"
      message="Unable to reach the server. Please check your internet connection and try again."
      actions={
        <Button onClick={onRetry} className="bg-orange-500 hover:bg-orange-600">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry Connection
        </Button>
      }
    />
  );
}

/**
 * Rate Limit Error State
 * Shown when too many requests (429)
 * T072: Countdown timer implementation
 */
export function RateLimitError({
  retryAfter: _retryAfter,
  countdown
}: {
  retryAfter: number;
  countdown: number;
}) {
  return (
    <ErrorStateBase
      icon={<Clock className="h-12 w-12 text-orange-400" />}
      title="Too Many Requests"
      message={`You've sent too many messages. Please wait ${countdown} seconds before trying again.`}
      details={`Rate limit: 20 requests per minute`}
      actions={
        <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Retry available in {countdown}s</span>
        </div>
      }
    />
  );
}

/**
 * Authentication Error State
 * Shown when session expires (401)
 * T074: Countdown before redirect
 */
export function AuthError({ countdown }: { countdown: number }) {
  return (
    <ErrorStateBase
      icon={<Lock className="h-12 w-12 text-red-400" />}
      title="Session Expired"
      message={`Your session has expired. You'll be redirected to sign in in ${countdown} seconds.`}
      actions={
        <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Redirecting in {countdown}s...</span>
        </div>
      }
    />
  );
}

/**
 * Timeout Error State
 * Shown when request takes >10 seconds
 * T075: Cancel and Keep Waiting options
 */
export function TimeoutError({
  onCancel,
  onKeepWaiting
}: {
  onCancel: () => void;
  onKeepWaiting: () => void;
}) {
  return (
    <ErrorStateBase
      icon={<Clock className="h-12 w-12 text-yellow-400" />}
      title="Request Taking Longer Than Expected"
      message="The server is taking a while to respond. You can keep waiting or cancel the request."
      actions={
        <>
          <Button onClick={onKeepWaiting} variant="default" className="bg-orange-500 hover:bg-orange-600">
            Keep Waiting
          </Button>
          <Button onClick={onCancel} variant="outline">
            Cancel Request
          </Button>
        </>
      }
    />
  );
}

/**
 * Backend Unavailable Error State
 * Shown for 502/503 errors
 */
export function BackendUnavailable({
  onRetry,
  correlationId
}: {
  onRetry: () => void;
  correlationId?: string;
}) {
  return (
    <ErrorStateBase
      icon={<Server className="h-12 w-12 text-gray-400" />}
      title="Service Temporarily Unavailable"
      message="The chat service is currently unavailable. Please try again in a few moments."
      details={correlationId ? `Reference: ${correlationId.slice(0, 8)}` : undefined}
      actions={
        <Button onClick={onRetry} variant="default" className="bg-orange-500 hover:bg-orange-600">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      }
    />
  );
}

/**
 * Unknown Error State
 * Generic fallback for unexpected errors
 */
export function UnknownError({
  onRetry,
  errorMessage,
  correlationId
}: {
  onRetry: () => void;
  errorMessage?: string;
  correlationId?: string;
}) {
  return (
    <ErrorStateBase
      icon={<AlertTriangle className="h-12 w-12 text-red-400" />}
      title="Something Went Wrong"
      message={errorMessage || "An unexpected error occurred. Please try again."}
      details={correlationId ? `Reference: ${correlationId.slice(0, 8)}` : undefined}
      actions={
        <Button onClick={onRetry} variant="default" className="bg-orange-500 hover:bg-orange-600">
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </Button>
      }
    />
  );
}
