import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import DonutChart from "./DonutChart";

export default function LeagueSummary() {
  const { compId, seasonId } = useParams();

  const [summaryData, setSummaryData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const fetchSummaryStats = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/leagues/${compId}/${seasonId}/summary`);
        if (!response.ok) throw new Error('Failed to fetch summary data.');

        const data = await response.json();
        setSummaryData(data);
      } catch (error) {
        console.error('Error fetching summary data.');
      } finally {
        setIsLoading(false);
      }
    }; 
    fetchSummaryStats();
  }, [compId, seasonId]);

  if (isLoading || !summaryData) {
    return <div className="loading-state">Loading league summary...</div>;
  }

  const { goal_averages, btts_rate, over_rate }= summaryData;
  const { home_league_goal_avg, away_league_goal_avg } = goal_averages;

  const formatRate = (rate) => `${(rate * 100).toFixed(1)}%`;
  const totalAvg = (home_league_goal_avg + away_league_goal_avg).toFixed(2);

  const bttsData = [
    { name: 'BTTS (Yes)', value: Number((btts_rate * 100).toFixed(1)) },
    { name: 'BTTS (No)', value: Number(((1 - btts_rate)* 100).toFixed(1)) }
  ];

  const overData = [
    { name: 'Over 2.5', value: Number((btts_rate * 100).toFixed(1)) },
    { name: 'Under 2.5', value: Number(((1 - over_rate) * 100).toFixed(1)) },
  ];

  return (
    <div className="league-summary-container">
      <h3 className="section-title">
        Season Averages
      </h3>

      <div className="stats-grid">

        <div className="stat-card">
          <span className="stat-label">Avg Goals / Match</span>
          <span className="stat-value">{totalAvg}</span>
        </div>
      
        <div className="stat-card">
          <span className="stat-label">Home vs. Away Avg</span>
          <span className="stat-value">
            {home_league_goal_avg.toFixed(2)} - {away_league_goal_avg.toFixed(2)}
          </span>
        </div>

        <div className="stat-card">
          <span className="stat-label">BTTS Rate</span>
          <span className="stat-value">{formatRate(btts_rate)}</span>
        </div>

        <div className="stat-card">
          <span className="stat-label">Over 2.5 Rate</span>
          <span className="stat-value">{formatRate(over_rate)}</span>
        </div>
      </div>

      <h3 className="section-title">Outcome Probabilities</h3>
      <div  className="charts-container">
        <DonutChart title="Both Teams to Score" data={bttsData}/>
        <DonutChart title="Over/Under 2.5 Goals" data={overData}/>
      </div>
    </div>
  );
}