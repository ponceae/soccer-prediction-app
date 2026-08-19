import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export default function Matchups() {
  const { compId, seasonId } = useParams();
  const [matchups, setMatchups] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isGridOpen, setIsGridOpen] = useState(false);
  
  useEffect(() => {
    const fetchMatchups = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const url = `http://localhost:8000/leagues/${compId}/${seasonId}/matchups`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch league matchups.');
        const data = await response.json();
        setMatchups(data);
      } catch (err) {
        console.error(err);
        setError(`Error loading league matchups: ${err.message}`);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMatchups();
  }, [compId, seasonId]);

  useEffect(() => {
    const snapToPane = setTimeout(() => {
      const container = document.getElementById("matchup-container");
      if (container) {
        const yOffset = container.getBoundingClientRect().top + window.scrollY - 20;
        window.scrollTo({ top: yOffset, behavior: 'smooth' });
      }
    }, 100);
    return () => clearTimeout(snapToPane);
  }, [compId, seasonId]);

  const scrollToWeek = (week) => {
    setIsGridOpen(false)

    setTimeout(() => {
      const element = document.getElementById(`matchweek-${week}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 50);
  };

  if (error) {
    return <div className="status-message error">{error}</div>;
  }

  if (isLoading) {
    return <div className="loading-state">Loading league matchups...</div>;
  }

  const groupedMatchups = matchups.reduce((acc, match) => {
    if (!acc[match.matchweek]) acc[match.matchweek] = [];
    acc[match.matchweek].push(match);
    return acc;
  }, {});

  const sortedMatchweeks = Object.keys(groupedMatchups).sort((a, b) => b - a);

  return (
    <div 
    id="matchup-container"
    className="matchups-container"
    >
    
      <div className="matchweek-jumper">
        <button
          className="grid-toggle-btn"
          onClick={() => setIsGridOpen(!isGridOpen)}
        >
          Jump to Matchweek {isGridOpen ? '▲' : '▼'}
        </button>

        {isGridOpen && (
          <div className="week-grid">
            {sortedMatchweeks.map((week) => (
              <button
                key={`grid-${week}`}
                className="grid-square-btn"
                onClick={() => scrollToWeek(week)}
              >
                {week}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="matchups-scroll-area">
        {sortedMatchweeks.map((week) => (
          <div key={week} id={`matchweek-${week}`} className="matchweek-group">

            <div className="matchweek-header">
              <h3>Matchweek {week}</h3>
            </div>

            <div className="matchweek-games">
              {groupedMatchups[week].map((match) => (
                <div key={match.id} className="match-row">
                  <div className="match-date">
                    {new Date(match.date).toLocaleDateString('en-US', {
                      month: 'short', day: 'numeric', year: 'numeric'
                    })}
                  </div>

                  <div className="match-scoreline">
                    
                    <div className="team-home">
                      <span>{match.home_team.name}</span>
                      <img
                        src={`/logos/teams/${match.home_team.id}.svg`}
                        alt="badge"
                        className="score-badge"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>

                    <span className="score">
                      {match.ft_home_goals} - {match.ft_away_goals}
                    </span>

                    <div className="team-away">
                      <span>{match.away_team.name}</span>
                      <img
                        src={`/logos/teams/${match.away_team.id}.svg`}
                        alt="badge"
                        className="score-badge"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
