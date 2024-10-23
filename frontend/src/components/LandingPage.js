import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <div className="left-side">
        <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXh6NWp6MWhvYzVveXphamZwczB5ZXZ4bGR5NDlxdjZ1bmZucjJwbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/w0Fy3hcQuZxxQgo0KR/giphy.webp" alt="Kid Animation" className="kid-animation" />
      </div>
      <div className="right-side">
        <h1 className="title">Welcome to Learning Analytics</h1>
        <div className="button-group">
          <button onClick={() => navigate('/signup')} className="get-started-button">Get Started</button>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
