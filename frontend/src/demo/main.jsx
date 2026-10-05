import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DemoApp from './DemoApp.jsx';

// Same caching rules as the main app.
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 10,   // 10 minutes: no refetch while data is fresh
            gcTime: 1000 * 60 * 30,      // 30 minutes: keep cache after leaving a page
            refetchOnWindowFocus: false,
            retry: 1,
        },
    },
});

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <DemoApp />
        </QueryClientProvider>
    </React.StrictMode>,
);
