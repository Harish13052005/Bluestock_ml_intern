import React, { useState } from "react";
import axios from "axios";
import "./AnalysisDisplay.css";

function AnalysisDisplay() {
  const [companyInput, setCompanyInput] = useState("");
  const [companies, setCompanies] = useState(["TCS", "HDFCBANK"]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("ALL");

  const visibleResults =
    filter === "ALL"
      ? results
      : results.filter((r) => r.health_rating === filter);

  const addCompany = () => {
    const symbol = companyInput.trim().toUpperCase();
    if (!symbol) return;

    if (!companies.includes(symbol)) {
      setCompanies((prev) => [...prev, symbol]);
    }
    setCompanyInput("");
  };

  const removeCompany = (symbol) => {
    setCompanies((prev) => prev.filter((c) => c !== symbol));
  };

  const analyzeCompanies = async () => {
    if (companies.length === 0) {
      setError("Please add at least one company symbol.");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);

    try {
  const response = await axios.post(
    "/api/analyze/?format=json",
    { company_ids: companies },
    { headers: { "Content-Type": "application/json" } }
  );

  if (response.data && response.data.results) {
    setResults(response.data.results);
  } else {
    setError("Unexpected response from server.");
  }
} catch (err) {
  console.error(err);
  setError("Could not contact backend. Is Django running on port 8000?");
} finally {
  setLoading(false);
}

  };

  return (
    <div className="page">
      <div className="container">
        <h1 className="title">Bluestock ML Financial Analysis</h1>
        <p className="subtitle">
          Enter stock symbols and generate ML-style pros and cons.
        </p>

        <div className="input-card">
          <input
            type="text"
            value={companyInput}
            onChange={(e) => setCompanyInput(e.target.value)}
            placeholder="Enter symbol (e.g. INFY)"
            onKeyDown={(e) => e.key === "Enter" && addCompany()}
          />
          <button onClick={addCompany}>Add</button>
          <button
            className="analyze-btn"
            onClick={analyzeCompanies}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>

        <div className="chips">
          {companies.map((c) => (
            <span className="chip" key={c}>
              {c}
              <button onClick={() => removeCompany(c)}>×</button>
            </span>
          ))}
        </div>

        {error && <div className="error">{error}</div>}

        <div className="filter-bar">
          {['ALL', 'GOOD', 'NEUTRAL', 'BAD'].map((f) => (
            <button
              key={f}
              className={filter === f ? 'filter active' : 'filter'}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="grid">
          {visibleResults.map((item) => {
            const rating = item.health_rating?.toLowerCase() || "neutral";

            return (
              <div key={item.company_id} className={`card card-${rating}`}>
                <div className="card-header">
                  <h2>{item.company_name}</h2>
                  <span className={`badge badge-${rating}`}>
                    {item.health_rating}
                  </span>
                </div>

                {item.details_url && (
                  <a
                    href={item.details_url}
                    target="_blank"
                    rel="noreferrer"
                    className="details-link"
                  >
                    View full Bluestock analysis →
                  </a>
                )}

                <div className="card-body">
                  <div className="metrics">
                    {item.metrics_summary && (
                      <>
                        <p><strong>10Y Sales:</strong> {item.metrics_summary.sales_growth_10y}</p>
                        <p><strong>10Y ROE:</strong> {item.metrics_summary.roe_10y}</p>
                      </>
                    )}
                  </div>

                  <div className="pros-cons">
                    <div className="pros">
                      <h3>Pros</h3>
                      <ul>
                        {item.pros.map((p, idx) => (
                          <li key={idx}>{p}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="cons">
                      <h3>Cons</h3>
                      <ul>
                        {item.cons.map((c, idx) => (
                          <li key={idx}>{c}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {!loading && results.length === 0 && (
            <p className="hint">Run an analysis to see results.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalysisDisplay;
