import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Auth Screens
import WelcomeScreen from '../screens/auth/WelcomeScreen';
import DoctorLoginScreen from '../screens/auth/DoctorLoginScreen';
import PatientLoginScreen from '../screens/auth/PatientLoginScreen';

// Doctor Screens
import DoctorDashboard from '../screens/doctor/DoctorDashboard';

// Patient Screens
import PatientDashboard from '../screens/patient/PatientDashboard';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Welcome"
        screenOptions={{
          headerShown: false,
        }}
      >
        {/* Auth Screens */}
        <Stack.Screen
          name="Welcome"
          component={WelcomeScreen}
        />
        <Stack.Screen
          name="DoctorLogin"
          component={DoctorLoginScreen}
        />
        <Stack.Screen
          name="PatientLogin"
          component={PatientLoginScreen}
        />

        {/* Doctor Screens */}
        <Stack.Screen
          name="DoctorDashboard"
          component={DoctorDashboard}
        />

        {/* Patient Screens */}
        <Stack.Screen
          name="PatientDashboard"
          component={PatientDashboard}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
