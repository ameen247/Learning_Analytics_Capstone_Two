// src/components/BloomPyramid.js
import React, { useEffect } from 'react';
import './styles/BloomPyramid.css';

function BloomPyramid({ scores }) {
  useEffect(() => {
    // Trigger reflow to restart the animations
    document.querySelectorAll('.level').forEach(level => {
      level.style.height = '0%';
      level.getBoundingClientRect(); // Trigger reflow
      const score = scores[level.dataset.level];
      level.style.height = `${Math.min(score, 100)}%`;
    });
  }, [scores]);

  return (
    <div className="bloom-pyramid">
      <div className="level creating" data-level="creating">Creating</div>
      <div className="level evaluating" data-level="evaluating">Evaluating</div>
      <div className="level analyzing" data-level="analyzing">Analyzing</div>
      <div className="level applying" data-level="applying">Applying</div>
      <div className="level understanding" data-level="understanding">Understanding</div>
      <div className="level remembering" data-level="remembering">Remembering</div>
    </div>
  );
}

export default BloomPyramid;
