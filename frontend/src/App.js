import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
  
import Login from "./Login";
import SignupForm from "./Signup";
import Home from "./Home";
import ForgotPassword from "./ForgotPassowrd";

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignupForm />} />
      <Route path="/home" element={<Home />} />
      <Route path="/reset-password" element={<ForgotPassword />} />
    </Routes>
  </BrowserRouter>
);

export default App;
