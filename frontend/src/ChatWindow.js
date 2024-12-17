import React, { useState, useEffect, useRef } from "react";
import './styles/ChatWindow.css'; // Import the CSS file for ChatWindow component
import {jwtDecode} from 'jwt-decode';  // Correct import for jwt-decode
import ImageIcon from '@mui/icons-material/ImageOutlined';

function ChatWindow({ username, conversationId }) {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]);
    const wsRef = useRef(null);
    const messageListRef = useRef(null);
    const token = localStorage.getItem('token');
    const decodedToken = jwtDecode(token); // Use jwtDecode instead of jwtDecode
    const current_user_Id = decodedToken.user_id;

    useEffect(() => {
        if (!conversationId) return;

        const fetchMessages = async () => {
            try {
                const response = await fetch(`http://localhost:8000/conversations/${conversationId}/messages`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setMessages(data); // Load initial messages
                } else {
                    console.error('Failed to fetch messages');
                }
            } catch (error) {
                console.error("Error fetching messages:", error);
            }
        };

        fetchMessages();

        const socket = new WebSocket(`ws://localhost:8000/ws/conversations/${conversationId}`);
        wsRef.current = socket;

        const handleMessage = (event) => {
            const newMessage = JSON.parse(event.data);
            setMessages((prevMessages) => {
                if (!prevMessages.find(msg => msg.message_id === newMessage.message_id)) {
                    return [...prevMessages, newMessage];
                }
                return prevMessages;
            });
        };

        socket.addEventListener('message', handleMessage);

        return () => {
            socket.removeEventListener('message', handleMessage);
            socket.close();
        };
    }, [conversationId, token]);

    useEffect(() => {
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        if (message.trim() === "" || !conversationId) return;

        try {
            const response = await fetch(`http://localhost:8000/send-message?conversation_id=${conversationId}&message_text=${message}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });
            if (response.ok) {
                const newMessage = await response.json();
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.send(JSON.stringify(newMessage));
                }
                setMessage(""); // Clear input
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error sending message:", error);
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (file.size > 2 * 1024 * 1024) { // Limit to 2 MB
            alert("File size exceeds 2 MB");
            return;
        }

        const reader = new FileReader();
        reader.onload = () => {
            const imageData = reader.result; // Base64 string
            sendImage(imageData);
        };
        reader.readAsDataURL(file);
        handleSendMessage();
    };

    const sendImage = (imageData) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            const newImageMessage = {
                type: 'image',
                data: imageData,
                sender_id: current_user_Id,
                conversation_id: conversationId,
                timestamp: new Date().toISOString(),
            };

            setMessages((prevMessages) => [...prevMessages, newImageMessage]); // Update UI immediately
            wsRef.current.send(JSON.stringify(newImageMessage));
        } else {
            console.error("WebSocket is not open");
        }
    };

    return (
        <div className="chat-window">
            <div className="chat-header">
                <h2>{username}</h2>
            </div>
            <div className="message-list" ref={messageListRef} style={{ height: '400px', overflowY: 'scroll' }}>
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.sender_id === current_user_Id ? "sent" : "received"}`}
                    >
                        {msg.type === 'image' ? (
                            <img src={msg.data} alt="Sent" style={{ maxWidth: '200px' }} />
                        ) : (
                            <span>{msg.message_text}</span>
                        )}
                    </div>
                ))}
            </div>
            <div className="message-input">
                <input
                    type="text"
                    value={message}
                    placeholder="Type a message... Use Windows + '.' key to enter emojis"
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => { if (e.key === 'Enter') handleSendMessage(); }}
                />
                <div>
                    <label htmlFor="image-upload">
                        <ImageIcon style={{ cursor: 'pointer' }} />
                    </label>
                    <input
                        id="image-upload"
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={handleImageChange}
                    />
                </div>
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
}

export default ChatWindow;
