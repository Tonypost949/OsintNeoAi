import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyA5heqgR7H-D-HTKCFzzh4rBZQXIlLeiY8",
  authDomain: "blah-905ad.firebaseapp.com",
  projectId: "blah-905ad",
  storageBucket: "blah-905ad.firebasestorage.app",
  messagingSenderId: "200987655934",
  appId: "1:200987655934:web:f20d72dbc5e2078d0dafaf",
  measurementId: "G-V0YTVG5EX2"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };
