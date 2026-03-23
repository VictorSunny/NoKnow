import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import NavigationProvider from "./contexts/NavigationContext";
import { UserProvider } from "./contexts/AuthContext";
import Router from "./Router";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 0,
      refetchOnWindowFocus: false,
      staleTime: 0,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NavigationProvider>
        <UserProvider>
          <Router/>
        </UserProvider>
      </NavigationProvider>
    </QueryClientProvider>
  );
}
