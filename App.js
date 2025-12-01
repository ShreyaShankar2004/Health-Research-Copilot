import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState({});

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    setResults([]);

    try {
      const response = await axios.get("http://127.0.0.1:8000/fallback", {
        params: { q: query },
      });
      setResults(response.data.results || []);
    } catch (err) {
      console.error("Error fetching results:", err);
    }
    setLoading(false);
  };

  const toggleExpand = (index) => {
    setExpanded((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const sourceColors = {
  "PUBMED": "bg-green-100 text-green-700",
  "PUBMED / EUROPE PMC": "bg-green-100 text-green-700",
  "ARXIV": "bg-blue-100 text-blue-700",
  "SEMANTIC SCHOLAR": "bg-yellow-100 text-yellow-700",
  "CLINICALTRIALS.GOV": "bg-purple-100 text-purple-700",
  "WIKIPEDIA": "bg-gray-200 text-gray-800",
};


  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-600 to-green-500 flex flex-col items-center p-6 font-sans">
      <h1 className="text-4xl font-bold text-white mb-8 drop-shadow-lg">
        🧑‍⚕️ Health Research Copilot
      </h1>

      {/* Search Bar */}
      <div className="flex gap-2 w-full max-w-xl">
        <input
          type="text"
          placeholder="Search disease, drug, or treatment..."
          className="flex-grow p-3 rounded-lg shadow-md border border-gray-200 focus:ring-2 focus:ring-blue-400"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={handleSearch}
          className="px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg shadow-md hover:bg-gray-100 transition"
        >
          Go
        </button>
      </div>

      {/* Results */}
      <div className="mt-10 w-full max-w-4xl space-y-6">
        {loading && (
          <p className="text-white text-lg animate-pulse">⏳ Searching...</p>
        )}

        {!loading && results.length === 0 && (
          <p className="text-gray-200 text-center">No results found.</p>
        )}

        {results.map((item, idx) => {
          const isExpanded = expanded[idx];
          const text = item.text || "";

          return (
            <div
              key={idx}
              className="bg-white rounded-lg shadow-lg p-6 hover:shadow-2xl transition"
            >
              {/* Title */}
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-2xl font-semibold text-blue-700 hover:underline"
              >
                {item.title}
              </a>

              {/* Abstract with Read More */}
              <p className="text-gray-700 mt-3 whitespace-pre-line">
                {isExpanded || text.length <= 300
                  ? text
                  : text.slice(0, 300) + "..."}
              </p>
              {text.length > 300 && (
                <button
                  onClick={() => toggleExpand(idx)}
                  className="text-blue-600 mt-2 text-sm font-medium hover:underline"
                >
                  {isExpanded ? "Read Less ▲" : "Read More ▼"}
                </button>
              )}

              {/* Source tag */}
              <div className="mt-4">
                <span
                  className={`text-sm px-3 py-1 rounded-full font-medium ${
                    sourceColors[item.source?.toUpperCase()] || "bg-gray-100"
                  }`}
                >
                  📖 Source: {item.source?.toUpperCase()}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default App;
