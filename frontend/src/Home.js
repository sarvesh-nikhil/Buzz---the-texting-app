import React, { useState, useEffect } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import ChatWindow from "./ChatWindow";
import './styles/Home.css'; // Import the CSS file for Home component

function Home() {
    const [profile, setProfile] = useState(null);
    const [users, setUsers] = useState([]);
    const [selectedUsername, setSelectedUsername] = useState(null);
    const [conversationId, setConversationId] = useState(null);
    const [profileimageUrl, setProfileimageUrl] = useState(null);
    const navigate = useNavigate();

    const fetchProfile = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch('http://localhost:8000/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        
        if (response.ok) {
            const data = await response.json();
            // console.log("User Profile Data : ", data);
            setProfile(data);
        } else {
            console.error('Failed to fetch profile');
        }
    };

    const fetchUsersInConversations = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
    
        const response = await fetch('http://localhost:8000/conversations/users', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
    
        if (response.ok) {
            const data = await response.json();
            setUsers(data);  // Now data contains both username and profile picture
        } else {
            console.error('Failed to fetch users in conversations');
        }
    };    

    useEffect(() => {
        fetchProfile();
        fetchUsersInConversations();
    }, []);

    // Fetch profile image URL when the component loads
    const fetchProfileimage = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch('http://localhost:8000/users/profile-image', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const data = await response.json();
            setProfileimageUrl(data.profile_image_url);
        } else {
            console.error('Failed to fetch profile image');
        }
    };

    useEffect(() => {
        fetchProfileimage();
    }, []);

    // Handle image upload
    const handleImageUpload = async (event) => {
        const token = localStorage.getItem('token');
        const file = event.target.files[0];

        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/users/me/profile-image', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setProfileimageUrl(data.profile_image_url); // Update the profile image URL
            } else {
                console.error('Failed to upload image');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    };

    const fetchConversationId = async (username) => {
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`http://localhost:8000/conversations/get-conversation-id?recipient_username=${username}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const conversationId = await response.json();
                setConversationId(conversationId);
            } else {
                console.error('Failed to fetch conversation ID');
            }
        } catch (error) {
            console.error("Error fetching conversation ID:", error);
        }
    };

    const handleAddConversation = async () => {
        const token = localStorage.getItem('token');
        const username = document.getElementById('new-username').value;
        if (!username) {
            alert("Please enter a username");
            return;
        }

        const response = await fetch(`http://localhost:8000/new-conversation?recipient_username=${username}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            fetchUsersInConversations();
            document.getElementById('new-username').value = ''; // Clear input
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail}`);
        }
    };

    const handleUserClick = async (username) => {
        setSelectedUsername(username);
        await fetchConversationId(username);
    };

    // handle logout
    const logout = () => {
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
        navigate('/login');
    }

    return (
        <div className="home-container">
            {/* Left sidebar */}
            <div className="sidebar">
                <div className="profile-section">
                    {profileimageUrl ? (
                        <div className="profile-info">
                            {/* Display the profile image if URL is not placeholder */}
                            {profileimageUrl !== '/static/default-placeholder.png' ? (
                                <img src={profileimageUrl} alt="Profile" className="profile-pic" />
                            ) : (
                                <div className="upload-placeholder">
                                    <p>No profile image found</p>
                                    <input 
                                        type="file" 
                                        onChange={handleImageUpload} 
                                    />
                                </div>
                            )}
                            {/* Display username below the profile picture */}
                            {profile && profile.username && (
                                <p className="welcome-message">Welcome {profile.username}</p>
                            )}
                        </div>
                    ) : (
                        <p>Loading profile image...</p>
                    )}
                </div>
                <div className="add-chat-section">
                    <input type="text" placeholder="Add user by username" id="new-username" />
                    <button onClick={handleAddConversation}>Start Chat</button>
                </div>
                <div className="conversation-list">
                    <h3>Chats</h3>
                    {users.length > 0 ? (
                        <ul>
                            {users.map((user) => (
                                <li
                                    key={user.user_id}
                                    className={`conversation-item ${selectedUsername === user.username ? 'active' : ''}`}
                                    onClick={() => handleUserClick(user.username)}
                                >
                                    {/* Display user's profile picture */}
                                    <img 
                                        src={user.profile_image_url} 
                                        alt={`${user.username}'s profile`} 
                                        className="user-profile-pic" 
                                    />
                                    {user.username}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No conversations yet.</p>
                    )}
                </div>
                <div className="logout-button">
                    <button onClick={logout}>Logout</button>
                </div>
                {/* <div>
                    <button onClick={changePassword}>Change Password</button>
                </div> */}
            </div>

            {/* Right side chat window */}
            <div className="chat-window-container">
                {selectedUsername && conversationId ? (
                    <ChatWindow username={selectedUsername} conversationId={conversationId} />
                ) : (
                    <div className="no-chat-selected">
                        <h2>Welcome to Buzz!</h2>
                        <p>Select a chat to start messaging</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Home;
