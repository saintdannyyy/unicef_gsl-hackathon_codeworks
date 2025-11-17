import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Onboarding from "./pages/Onboarding.tsx";
import Learn from "./pages/Learn.tsx";
import Lesson from "./pages/Lesson.tsx";
import PracticeEnhanced from "./pages/PracticeEnhanced.tsx";
import TranslateEnhanced from "./pages/TranslateEnhanced.tsx";
import PracticeComplete from "./pages/PracticeComplete.tsx";
import Home from "./pages/Home.tsx";

function App() {
  // Check if onboarding is complete
  const onboardingComplete =
    localStorage.getItem("onboarding_complete") === "true";

  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route
              path="/onboarding"
              element={
                onboardingComplete ? <Navigate to="/learn" /> : <Onboarding />
              }
            />
            <Route path="/learn" element={<Learn />} />
            <Route path="/lesson/:category" element={<Lesson />} />
            <Route path="/practice" element={<PracticeEnhanced />} />
            <Route path="/translate" element={<TranslateEnhanced />} />
            <Route path="/practice-complete" element={<PracticeComplete />} />

            {/* Redirect old routes */}
            <Route path="/landing" element={<Navigate to="/" />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
