import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AuthForm.css';

function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLogin) {
      // Login request
      axios.post('http://localhost:5000/login', { username: name, password })
        .then(response => {
          localStorage.setItem('username', name);  // Store username in localStorage
          alert(response.data.message);
          navigate('/questions');
        })
        .catch(error => {
          alert(error.response.data.message);
        });
    } else {
      // Signup request
      axios.post('http://localhost:5000/signup', { username: name, password })
        .then(response => {
          alert(response.data.message);
          navigate('/login');
        })
        .catch(error => {
          alert(error.response.data.message);
        });
    }
  };

  return (
    <div className="auth-form-container">
      <div className="auth-form">
        <div className="toggle-buttons">
          <button onClick={() => setIsLogin(true)} className={isLogin ? "active" : ""}>Login</button>
          <button onClick={() => setIsLogin(false)} className={!isLogin ? "active" : ""}>Signup</button>
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            required
          />
          {!isLogin && (
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email Address"
              required
            />
          )}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          {!isLogin && (
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm Password"
              required
            />
          )}
          <button type="submit">{isLogin ? "Login" : "Signup"}</button>
        </form>
      </div>
    </div>
  );
}

export default AuthForm;
