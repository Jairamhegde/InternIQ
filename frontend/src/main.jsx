import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 10,  // 10 minutes — won't refetch while fresh
      gcTime: 1000 * 60 * 30,     // 30 minutes — keeps cache after unmount
      refetchOnWindowFocus: false, // don't refetch when tab regains focus
    },
  },
})
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />

    </QueryClientProvider>

  </React.StrictMode>,
)
