import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SMSPage from "./pages/SMSPage";
import EmailPage from "./pages/EmailPage";
import URLPage from "./pages/URLPage";
import WebsitePage from "./pages/WebsitePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/sms" element={<SMSPage />} />
        <Route path="/email" element={<EmailPage />} />
        <Route path="/url" element={<URLPage />} />
        <Route path="/website" element={<WebsitePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;