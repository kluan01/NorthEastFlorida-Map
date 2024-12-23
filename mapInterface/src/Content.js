import React, { useState, useRef } from "react";

const Content = () => {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTakingLong, setIsTakingLong] = useState("");
  const [randomMessage, setRandomMessage] = useState("");
  const API_GENERATE_MAP = "http://localhost:5000/api/generate-map";
  const API_RUN_ALGORITHMS = "http://localhost:5000/api/test-algorithms";

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
    setRandomMessage("");

    // display random message while waiting
    timerRef.current = setTimeout(() => {
      setRandomMessage(displayMessage());
    }, 1000);

    try {
      // generate the map
      setIsTakingLong("Generating map...");
      const mapResponse = await fetch(API_GENERATE_MAP, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!mapResponse.ok) {
        throw Error(`Map Generation Error --> Status: ${mapResponse.status}`);
      }

      const mapData = await mapResponse.json();
      console.log(mapData.message);

      // run the algorithms
      setIsTakingLong("Running algorithms...");
      const algoResponse = await fetch(API_RUN_ALGORITHMS, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!algoResponse.ok) {
        throw Error(`Algorithm Error --> Status: ${algoResponse.status}`);
      }

      const algoData = await algoResponse.json();
      setResults(algoData);
      setError(null);
    } catch (err) {
      console.error("Error in processing:", err);
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
        className="submit-button"
        onClick={handleRunFunctions}
        disabled={isLoading}
      >
        {isLoading ? "Generating..." : "Generate!"}
      </button>
      {isLoading && <div className="loading-spinner"></div>}
      {isTakingLong && (
        <p style={{ color: "rgb(0, 198, 205)" }}>{isTakingLong}</p>
      )}
      {isLoading && randomMessage && (
        <p style={{ color: "rgb(0, 150, 150)", fontStyle: "italic" }}>
          {randomMessage}
        </p>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!isLoading && results && (
        <div className="results-box-dix">
          <div className="results-text">
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
