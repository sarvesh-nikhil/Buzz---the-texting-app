import React, { useState } from "react";
import ResetPasswordForm from "./ResetPasswordForm"; // Import the ResetPasswordForm component
import "./styles/ForgotPassword.css"; // Import the new CSS file
import Footer from "./Footer";

function ForgotPassword() {
    const [username, setUsername] = useState("");
    const [showResetForm, setShowResetForm] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleInputChange = (e) => {
        setUsername(e.target.value);
    };

    const handleGetOtp = async () => {
        try {
            const response = await fetch(`http://localhost:8000/forgot-password?username=${username}`, {
                method: "POST",
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.message);
                setShowResetForm(true); // Show the reset form component
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Failed to send OTP");
            }
        } catch (err) {
            alert("An error occurred while sending the OTP. Please try again.");
        }
    };

    return (
        <div className="forgot-password-container">
            {!showResetForm ? (
                <>
                    <h2>Enter your username to receive an OTP</h2>
                    <div className="input-container">
                        <input
                            type="text"
                            placeholder="Enter your username"
                            value={username}
                            onChange={handleInputChange}
                        />
                        <button onClick={handleGetOtp}>Get OTP</button>
                    </div>
                    {message && <p className="success-message">{message}</p>}
                    {error && <p className="error-message">{error}</p>}
                    <Footer />
                </>
            ) : (
                <>
                    <ResetPasswordForm username={username} />
                </>
            )}
        </div>
    );
}

export default ForgotPassword;
