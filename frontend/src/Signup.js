import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "./Footer";
import './styles/Login.css';

function Signup() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Client-side validation
        if (!email.trim() || !username.trim() || !password.trim()) {
            setError("All fields are required.");
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/create-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, username, password }),
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess("User created successfully! Redirecting to login...");
                setTimeout(() => navigate('/login'), 2000);
            } else {
                const errorData = await response.json();
                if (Array.isArray(errorData.detail)) {
                    const messages = errorData.detail.map(err => err.msg).join(', ');
                    setError(messages);
                } else if (typeof errorData.detail === "string") {
                    setError(errorData.detail);
                } else {
                    setError('Failed to create user. Please try again.');
                }
            }
        } catch (error) {
            setError('Network error. Please try again.');
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Create Your Buzz Account</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <input
                        type="text"
                        placeholder="Choose a username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Choose a strong password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <button type="submit">Sign Up</button>
                </form>
                {error && <p className="error-message">{error}</p>}
                {success && <p className="success-message">{success}</p>}
            </div>
            <Footer />
        </div>
    );
}

export default Signup;
