import React, { useState } from "react";

const Content = () => {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const API_URL = "http://localhost:5000/api/run-functions";

  const handleRunFunctions = async () => {
    setIsLoading(true);
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
    }
  };

  return (
    <div class="content-div">
      <h2>Run Pathfinding Algorithms</h2>
      <button onClick={handleRunFunctions} disabled={isLoading}>
        {isLoading ? "Generating..." : "Generate!"}
      </button>
      {isLoading && <div className="loading-spinner"></div>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {results && (
        <div>
          <h3>Results:</h3>
          <p>
            <strong>A*:</strong> {results.a_star.time}s,{" "}
            {results.a_star.distance}m
          </p>
          <p>
            <strong>Dijkstra's:</strong> {results.dijkstra.time}s,{" "}
            {results.dijkstra.distance}m
          </p>
          <img
            src="http://localhost:5000/api/route-image"
            alt="Route Visualization"
            class="map"
          />
        </div>
      )}
    </div>
  );
};

export default Content;
