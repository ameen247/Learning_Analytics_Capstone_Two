import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Questions.css';

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [response, setResponse] = useState('');
  const [startTime, setStartTime] = useState(null);
  const [allResponses, setAllResponses] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const username = localStorage.getItem('username');
    console.log('Sending request to fetch questions for user:', username);
    if (!username) {
      console.error('No username found in localStorage.');
      return;
    }
    axios.post('http://localhost:5000/questions', { username })
      .then(response => {
        console.log('Questions received:', response.data.questions);
        setQuestions(response.data.questions.slice(0, 5));  // Limit to 5 questions for testing
        setStartTime(new Date().getTime());
      })
      .catch(error => {
        console.error("There was an error fetching the questions!", error);
      });
  }, []);

  const handleNextQuestion = () => {
    const endTime = new Date().getTime();
    const timeTaken = endTime - startTime;
    const question = questions[currentQuestionIndex];

    setAllResponses([...allResponses, {
      question_id: question.id,
      user_response: response,
      start_time: startTime,
      end_time: endTime
    }]);

    setResponse('');
    setStartTime(new Date().getTime());

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    const username = localStorage.getItem('username');
    if (!username) {
      console.error('No username found in localStorage.');
      return;
    }
    console.log('Submitting answers:', allResponses);
    axios.post('http://localhost:5000/submit_answers', { username, answers: allResponses })
      .then(response => {
        console.log('Submission response:', response.data);
        navigate('/dashboard', {
          state: {
            feedback: response.data.feedback,
            totalScore: response.data.total_score,
            rememberingScore: response.data.remembering_score,
            understandingScore: response.data.understanding_score,
            applyingScore: response.data.applying_score,
            averageTimeTaken: response.data.average_time_taken
          }
        });
      })
      .catch(error => {
        console.error("There was an error submitting the answers!", error);
      });
  };

  if (questions.length === 0) {
    return <div>Loading questions...</div>;
  }

  return (
    <div className="questions-container">
      <div className="question-block">
        <p>{questions[currentQuestionIndex].Question}</p>
        <input
          type="text"
          value={response}
          onChange={(e) => setResponse(e.target.value)}
          placeholder="Your answer"
          required
        />
      </div>
      <button onClick={handleNextQuestion} className="next-button">
        {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Submit Answers'}
      </button>
    </div>
  );
}

export default Questions;
