import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import WelcomeScreen from './src/screens/auth/WelcomeScreen';

export default function TestApp() {
  // Mock navigation object
  const mockNavigation = {
    navigate: (screen) => console.log('Navigate to:', screen),
    goBack: () => console.log('Go back'),
  };

  return (
    <SafeAreaProvider>
      <WelcomeScreen navigation={mockNavigation} />
    </SafeAreaProvider>
  );
}
