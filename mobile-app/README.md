# Bristol Stool Scale Mobile App

React Native mobile application for iOS and Android that connects doctors with patients for feces analysis using AI classification (Bristol Stool Scale).

## Features

### For Doctors
- Professional registration with CRM
- Unique invite code generation
- View all linked patients
- Access patient analysis history
- Monitor patient health progress

### For Patients
- Register using doctor's invite code
- Take photos directly from camera
- Upload photos from gallery
- Automatic Bristol Scale classification
- Personalized health recommendations
- Complete analysis history
- Progress tracking

## Project Structure

```
mobile-app/
├── App.js                          # Main app entry point
├── src/
│   ├── navigation/
│   │   └── AppNavigator.js         # Navigation configuration
│   ├── services/
│   │   └── api.js                  # API client (connects to FastAPI backend)
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── WelcomeScreen.js    # Landing page
│   │   │   ├── DoctorLoginScreen.js # Doctor login/register
│   │   │   └── PatientLoginScreen.js # Patient login/register
│   │   ├── doctor/
│   │   │   └── DoctorDashboard.js  # Doctor's patient management
│   │   └── patient/
│   │       └── PatientDashboard.js # Patient's analysis interface
│   └── components/                  # (Future reusable components)
└── package.json
```

## Prerequisites

- Node.js (v20+)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac) or Android Emulator
- Backend API running (see [../backend/README.md](../backend/README.md))

## Installation

1. Install dependencies:
```bash
cd mobile-app
npm install
```

2. Configure backend URL:

Edit [src/services/api.js](src/services/api.js) and change the API_URL:

```javascript
// For local development
const API_URL = 'http://localhost:8000';

// For physical device testing (use your computer's IP)
const API_URL = 'http://192.168.1.XXX:8000';

// For production
const API_URL = 'https://your-api-domain.com';
```

## Running the App

### Development Mode

Start the Expo development server:

```bash
npm start
```

This will open Expo DevTools in your browser.

### iOS Simulator (Mac only)

```bash
npm run ios
```

Or press `i` in the terminal after running `npm start`.

### Android Emulator

```bash
npm run android
```

Or press `a` in the terminal after running `npm start`.

### Physical Device

1. Install "Expo Go" app on your iOS/Android device
2. Run `npm start`
3. Scan the QR code with your device:
   - iOS: Use Camera app
   - Android: Use Expo Go app

**Important**: Your device and computer must be on the same WiFi network, and you need to use your computer's local IP address in the API_URL configuration.

## Testing Physical Device with Camera

The camera functionality requires testing on a physical device or simulator with camera access:

### iOS (Physical Device):
1. Update `API_URL` to your computer's IP (e.g., `http://192.168.1.5:8000`)
2. Ensure backend is running with `--host 0.0.0.0`:
   ```bash
   cd ../backend
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Run `npm start` and scan QR code with Expo Go
4. Allow camera permissions when prompted
5. Test taking photos and uploading

### Android (Physical Device):
Same steps as iOS above.

## Key Dependencies

- `expo`: ^53.0.0 - Development platform
- `react-navigation`: Navigation library
- `axios`: HTTP client for API calls
- `expo-camera`: Camera access
- `expo-image-picker`: Image selection from gallery/camera
- `@react-native-async-storage/async-storage`: Local storage for auth tokens

## API Integration

The app communicates with the FastAPI backend at `http://localhost:8000` by default.

### Main Endpoints Used:

- `POST /auth/login` - User authentication
- `POST /auth/registro-medico` - Doctor registration
- `POST /auth/registro-paciente` - Patient registration
- `GET /medicos/perfil` - Doctor profile
- `GET /medicos/pacientes` - Doctor's patients list
- `GET /medicos/paciente/{id}/analises` - Patient analysis history
- `GET /pacientes/perfil` - Patient profile
- `POST /pacientes/analise` - Create new feces analysis (with image upload)
- `GET /pacientes/analises` - Patient's own analysis history

## User Flow

### Doctor Flow:
1. Welcome Screen → Doctor Login
2. Register with CRM, email, password
3. Receive unique invite code (e.g., DR-ABC123)
4. Login and view dashboard
5. See all linked patients
6. View each patient's complete analysis history

### Patient Flow:
1. Welcome Screen → Patient Login
2. Register with doctor's invite code
3. Login and view dashboard
4. Go to "Nova Análise" tab
5. Take photo or select from gallery
6. Add optional observations
7. Click "Analisar Agora"
8. View results (Bristol type, confidence, recommendations)
9. Check history in "Histórico" tab

## Troubleshooting

### "Network request failed"
- Ensure backend is running on port 8000
- Check API_URL in [src/services/api.js](src/services/api.js)
- For physical devices, use your computer's local IP, not localhost
- Verify firewall isn't blocking port 8000

### "Cannot connect to Metro"
- Close other instances of Metro bundler
- Run `npm start -- --reset-cache`
- Clear Expo cache: `expo start -c`

### Camera not working
- Test only on physical device or simulator with camera support
- Grant camera permissions when prompted
- iOS: Check Settings → Expo Go → Camera
- Android: Check App Permissions → Expo Go → Camera

### Image upload fails
- Check file size (backend limit is 10MB)
- Ensure backend `uploads/` directory has write permissions
- Check network connection
- Verify image format (JPG, PNG supported)

### "401 Unauthorized" errors
- Token may have expired (30 min default)
- Logout and login again
- Check system date/time is correct

## Building for Production

### iOS (requires Mac + Apple Developer Account):

```bash
expo build:ios
```

Follow prompts to configure app signing.

### Android:

```bash
expo build:android
```

Generates APK or AAB file for Play Store.

## Environment Variables

Currently hardcoded in [src/services/api.js](src/services/api.js).

For production, consider using:
- `expo-constants` for environment-specific config
- `.env` files with `react-native-dotenv`

## Next Steps

- [ ] Add offline support with local database
- [ ] Implement push notifications for new analyses
- [ ] Add data visualization charts
- [ ] Export analysis reports to PDF
- [ ] Implement dark mode
- [ ] Add multi-language support
- [ ] Biometric authentication (fingerprint/face ID)
- [ ] Share results with doctor directly

## License

Private medical application.

## Support

For issues or questions, contact the development team or refer to the backend documentation at [../backend/README.md](../backend/README.md).
