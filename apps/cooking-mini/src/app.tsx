import { PropsWithChildren } from 'react';
import { AuthProvider } from '@/lib/auth/auth-context';
import { CookingProvider } from '@/lib/cooking/cooking-context';
import './app.scss';

function App({ children }: PropsWithChildren) {
  return (
    <AuthProvider>
      <CookingProvider>{children}</CookingProvider>
    </AuthProvider>
  );
}

export default App;
