// firebase.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getDatabase, ref, onValue, set, update, get, child } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyBxQ4EiH_aTCyJm5_VT0cRSDD97F_ObG1o",
  authDomain: "bitdeen-a1ebe.firebaseapp.com",
  databaseURL: "https://bitdeen-a1ebe-default-rtdb.firebaseio.com",
  projectId: "bitdeen-a1ebe",
  storageBucket: "bitdeen-a1ebe.appspot.com",
  messagingSenderId: "957332775205",
  appId: "1:957332775205:web:e34cc38d4d5282adc43acc"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

export { db, ref, set, update, get, child, onValue }; 