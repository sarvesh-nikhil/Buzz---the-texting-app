import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import './styles/Login.css';
import Footer from './Footer'; // Import the Footer component

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [token, setToken] = useState('');

    const navigate = useNavigate();

    const handleUsernameChange = (e) => {
        setUsername(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
    
        if (!username.trim() || !password.trim()) {
            setError("Username and password cannot be empty.");
            return;
        }
    
        try {
            const response = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username.trim(),
                    password: password.trim(),
                }),
            });
    
            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                console.log("Login successful:", data);
                localStorage.setItem('token', data.access_token);
                navigate('/home');
            } else {
                const errorData = await response.json();
                
                // Check if detail is an array and process it
                if (Array.isArray(errorData.detail)) {
                    const messages = errorData.detail.map(err => err.msg).join(', ');
                    setError(messages);
                } else {
                    setError('Login failed. Please try again.');
                }
            }
        } catch (error) {
            setError('Network error. Please try again.');
        }
    };    

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Buzz!</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        value={username}
                        onChange={handleUsernameChange}
                    />
                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        value={password}
                        onChange={handlePasswordChange}
                    />
                    <button type="submit">Login</button>
                </form>
                {error && <p className="error-message">{error}</p>}
                {token && <p className="success-message">Login successful!</p>}

                <div>
                    <h4>Don't have an account?</h4>
                    <Link to="/signup">Sign up</Link>
                </div>
                <div className="reset-password">
                    <Link to="/reset-password" >Forgotten Password?</Link>
                </div>
                
            </div>
            <Footer />
        </div>
    );
}

export default Login;
