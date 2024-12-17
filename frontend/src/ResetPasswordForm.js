import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./styles/ResetPassword.css"; // Import the new CSS file
import Footer from "./Footer";

function ResetPasswordForm() {
    const [otp, setOtp] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleOtpChange = (e) => setOtp(e.target.value);
    const handlePasswordChange = (e) => setNewPassword(e.target.value);

    const handleResetPassword = async () => {
        try {
            const response = await fetch("http://localhost:8000/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ reset_token: otp, new_password: newPassword }),
            });

            if (response.ok) {
                const data = await response.json();
                setMessage(data.message);
                setError("");
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Failed to reset password");
                setMessage("");
            }
        } catch {
            setError("An error occurred. Please try again.");
            setMessage("");
        }
    };

    const handleProceedToLogin = () => navigate("/login");

    return (
        <div className="reset-password-container">
            <div className="reset-password-box">
                {message && (
                    <div>
                        <p className="success-message">{message}</p>
                        <button onClick={handleProceedToLogin}>Proceed to Login</button>
                    </div>
                )}
                {error && <p className="error-message">{error}</p>}
                {!message && (
                    <>
                        <input
                            type="text"
                            placeholder="Enter OTP"
                            value={otp}
                            onChange={handleOtpChange}
                        />
                        <input
                            type="password"
                            placeholder="Enter New Password"
                            value={newPassword}
                            onChange={handlePasswordChange}
                        />
                        <button onClick={handleResetPassword}>Reset Password</button>
                    </>
                )}
            </div>
            <Footer />
        </div>
    );
}

export default ResetPasswordForm;
