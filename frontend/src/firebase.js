// Firebase Web SDK initialization
// If you plan to commit this repo publicly, consider moving these values into env variables.
import { initializeApp } from 'firebase/app'
import { getAnalytics, isSupported } from 'firebase/analytics'

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: 'AIzaSyC5deuM4_XzBIHIf3UUSWuaTx4A-wXkztw',
  authDomain: 'cebimdekiveri.firebaseapp.com',
  projectId: 'cebimdekiveri',
  storageBucket: 'cebimdekiveri.firebasestorage.app',
  messagingSenderId: '260312651838',
  appId: '1:260312651838:web:cd11e407bd5670133f996f',
  measurementId: 'G-JLY3CZSXTB',
}

// Initialize Firebase
export const app = initializeApp(firebaseConfig)

// Initialize Analytics only when supported (avoids SSR/worker errors)
export let analytics = null
isSupported()
  .then((ok) => {
    if (ok) analytics = getAnalytics(app)
  })
  .catch(() => {
    // ignore analytics init errors
  })
