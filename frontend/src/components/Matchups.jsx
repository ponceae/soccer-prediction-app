import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

import styles from './Matchups.module.css';

export default function Matchups() {
  const navigate = useNavigate();
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
    if (isLoading) return;

    const lastMatchId = sessionStorage.getItem('lastViewedMatchId');

    if (lastMatchId) {
      setTimeout(() => {
        const element = document.getElementById(`match-${lastMatchId}`);
        if (element) {
          element.scrollIntoView({ behavior: 'instant', block: 'center' });
        }
      }, 100);
      sessionStorage.removeItem('lastViewedMatchId');
    } else {
      const snapToPane = setTimeout(() => {
        const container = document.getElementById("matchup-container");
        if (container) {
          const yOffset = container.getBoundingClientRect().top + window.scrollY - 20;
          window.scrollTo({ top: yOffset, behavior: 'smooth' });
        }
      }, 100);
      return () => clearTimeout(snapToPane);
    }
  }, [compId, seasonId, isLoading]);

  const scrollToWeek = (week) => {
    setIsGridOpen(false)

    setTimeout(() => {
      const element = document.getElementById(`matchweek-${week}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 50);
  };

  const handleMatchClick = (matchId) => {
    sessionStorage.setItem('lastViewedMatchId', matchId);
    navigate(`/matchup/${compId}/${seasonId}/${matchId}`);
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
      className={styles['matchups-container']}
    >
    
      <div className={styles['matchweek-jumper']}>
        <button
          className={styles['grid-toggle-btn']}
          onClick={() => setIsGridOpen(!isGridOpen)}
        >
          Jump to Matchweek {isGridOpen ? '▲' : '▼'}
        </button>

        {isGridOpen && (
          <div className={styles['week-grid']}>
            {sortedMatchweeks.map((week) => (
              <button
                key={`grid-${week}`}
                className={styles['grid-square-btn']}
                onClick={() => scrollToWeek(week)}
              >
                {week}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className={styles['matchups-scroll-area']}>
        {sortedMatchweeks.map((week) => (
          <div key={week} id={`matchweek-${week}`} className={styles['matchweek-group']}>

            <div className={styles['matchweek-header']}>
              <h3>Matchweek {week}</h3>
            </div>

            <div className={styles['matchweek-games']}>
              {groupedMatchups[week].map((match) => (
                <div 
                  key={match.id} 
                  id={`match-${match.id}`}
                  className={styles['match-row']}
                  onClick={() => handleMatchClick(match.id)}
                >
                  <div className={styles['match-date']}>
                    {new Date(match.date).toLocaleDateString('en-US', {
                      month: 'short', day: 'numeric', year: 'numeric'
                    })}
                  </div>

                  <div className="match-scoreline">
                    
                    <div className={styles['team-home']}>
                      <span>
                        {match.home_team.name}
                        {match.home_red_cards > 0 && Array.from({ length: match.home_red_cards }).map((_, i) => (
                          <span key={`home-red-${i}`} className='red-card-icon' title='Red Card'></span>
                        ))}
                      </span>
                      <img
                        src={`/logos/teams/${match.home_team.id}.svg`}
                        alt="badge"
                        className={styles['score-badge']}
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>

                    <span className={styles['score']}>
                      {match.ft_home_goals} - {match.ft_away_goals}
                    </span>

                    <div className={styles['team-away']}>
                      <span>
                        {match.away_team.name}
                        {match.away_red_cards > 0 && Array.from({ length: match.away_red_cards }).map((_, i) => (
                          <span key={`away-red-${i}`} className='red-card-icon' title='Red Card'></span>
                        ))}
                      </span>
                      <img
                        src={`/logos/teams/${match.away_team.id}.svg`}
                        alt="badge"
                        className={styles['score-badge']}
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
