import React, { useEffect, useState } from 'react';
import './GalaxyBackground.css';

const GalaxyBackground = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    const generateStars = () => {
      const starCount = Math.floor(Math.random() * 51) + 150; // 150-200 stars
      const newStars = [];
      
      for (let i = 0; i < starCount; i++) {
        const size = Math.random() * 2 + 2; // 2-4px
        const opacity = Math.random() * 0.7 + 0.3; // 0.3-1.0
        const left = Math.random() * 100; // 0-100%
        const animationDuration = Math.random() * 10 + 15; // 15-25 seconds
        const animationDelay = Math.random() * 10; // 0-10 seconds delay
        
        newStars.push({
          id: i,
          size,
          opacity,
          left,
          animationDuration,
          animationDelay
        });
      }
      
      setStars(newStars);
    };

    generateStars();
  }, []);

  return (
    <div className="galaxy-background">
      <div className="stars-container">
        {stars.map((star) => (
          <div
            key={star.id}
            className="star"
            style={{
              width: `${star.size}px`,
              height: `${star.size}px`,
              opacity: star.opacity,
              left: `${star.left}%`,
              animationDuration: `${star.animationDuration}s`,
              animationDelay: `${star.animationDelay}s`
            }}
          />
        ))}
      </div>
      <div className="gradient-overlay" />
    </div>
  );
};

export default GalaxyBackground;