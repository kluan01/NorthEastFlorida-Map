import React, { useState, useRef } from "react";

const Content = () => {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTakingLong, setIsTakingLong] = useState("");
  const API_URL = "http://localhost:5000/api/run-functions";

  const timerRef = useRef(null);
  const randomMessages = [
    "This was a personal project created by Kaden Luangsouphom and Devan Parekh!",
    "Did you know that penguins can't fly?",
    "Fun fact, there are a lot of dangerous creatures that live in Australia!",
    "Did you know Flamingos aren't born pink?",
    "Did you know Australia is wider than the moon?",
    "Did you know Ketchup was once medicine (in the 1830s)?",
  ];

  const displayMessage = () => {
    const randomIndex = Math.floor(Math.random() * randomMessages.length);
    return randomMessages[randomIndex];
  };

  const handleRunFunctions = async () => {
    setIsLoading(true);
    setError(null);
    setIsTakingLong("");

    timerRef.current = setTimeout(() => {
      setIsTakingLong(displayMessage());
    }, 1000);

    timerRef.current = setTimeout(() => {
      setIsTakingLong("Generating may take longer for the first click...");
    }, 12000);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        throw Error(`Fetch Error --> Status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setError(null);
    } catch (err) {
      console.error("Error running functions:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
      setIsTakingLong("");

      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  return (
    <div className="content-div">
      <h2 style={{ marginBottom: "15px" }}>Run Pathfinding Algorithms</h2>
      <button
        class="submit-button"
        onClick={handleRunFunctions}
        disabled={isLoading}
      >
        {isLoading ? "Generating..." : "Generate!"}
      </button>
      {isLoading && <div className="loading-spinner"></div>}
      {isTakingLong && (
        <p style={{ color: "rgb(0, 198, 205)" }}>{isTakingLong}</p>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!isLoading && results && (
        <div class="results-box-dix">
          <div class="results-text">
            <h3>Results:</h3>
            <p>
              <strong>A*:</strong> {results.a_star.time}s,{" "}
              {results.a_star.distance}m
            </p>
            <p>
              <strong>Dijkstra's:</strong> {results.dijkstra.time}s,{" "}
              {results.dijkstra.distance}m
            </p>
          </div>
          <img
            src="http://localhost:5000/api/route-image"
            alt="Route Visualization"
            className="map"
          />
        </div>
      )}
    </div>
  );
};

export default Content;
