import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './Dashboard.css';

// Register Chart.js components
ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend
);

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();

  const {
    feedback,
    totalScore,
    rememberingScore,
    understandingScore,
    applyingScore,
    averageTimeTaken,
    numSessions, // Added to display the number of sessions
  } = location.state || {};

  const totalAccumulatedScore = rememberingScore + understandingScore + applyingScore;
  const rememberingPercentage = ((rememberingScore / totalAccumulatedScore) * 100).toFixed(1);
  const understandingPercentage = ((understandingScore / totalAccumulatedScore) * 100).toFixed(1);
  const applyingPercentage = ((applyingScore / totalAccumulatedScore) * 100).toFixed(1);

  const scoreData = {
    labels: ['Remembering', 'Understanding', 'Applying'],
    datasets: [
      {
        label: 'Scores',
        data: [rememberingScore, understandingScore, applyingScore],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        hoverBackgroundColor: 'rgba(54, 162, 235, 0.4)',
        hoverBorderColor: 'rgba(54, 162, 235, 1)',
      },
    ],
  };

  const timeData = {
    labels: ['Session 1', 'Session 2', 'Session 3', 'Session 4', 'Session 5'],
    datasets: [
      {
        label: 'Average Time Taken (ms)',
        data: [averageTimeTaken], // This should be an array of average times for each session
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
      },
    ],
  };

  const options = {
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(204, 204, 204, 0.1)',
        },
        ticks: {
          color: '#666',
        },
      },
      x: {
        grid: {
          color: 'rgba(204, 204, 204, 0.1)',
        },
        ticks: {
          color: '#666',
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        labels: {
          color: '#333',
          font: {
            size: 14,
          },
        },
      },
    },
  };

  return (
    <div className="dashboard-container">
      <div className="button-container">
        <button onClick={() => navigate('/questions')} className="retry-button">
          Retry
        </button>
        <button onClick={() => navigate('/')} className="logout-button">
          Logout
        </button>
      </div>
      <div className="feedback-container">
        <h2>Feedback</h2>
        <p>{feedback}</p>
      </div>
      <div className="score-container">
        <div className="score-box">
          <h3>Total Score</h3>
          <p>{totalScore ? totalScore.toFixed(1) : '0.0'}</p>
        </div>
        <div className="score-box">
          <h3>Remembering Score</h3>
          <p>{rememberingPercentage ? `${rememberingPercentage}%` : '0.0%'}</p>
        </div>
        <div className="score-box">
          <h3>Understanding Score</h3>
          <p>{understandingPercentage ? `${understandingPercentage}%` : '0.0%'}</p>
        </div>
        <div className="score-box">
          <h3>Applying Score</h3>
          <p>{applyingPercentage ? `${applyingPercentage}%` : '0.0%'}</p>
        </div>
      </div>
      <div className="chart-container">
        <div className="chart-box">
          <Line data={scoreData} options={options} />
        </div>
        <div className="chart-box">
          <Line data={timeData} options={options} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
