import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";

export default function KnockoutBracket() {
  const { compId, seasonId } = useParams();

  const [knockoutMatches, setKnockoutMatches] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const location = useLocation();
  const currentLeague = location.state;

  const activeSeason = currentLeague?.seasons?.find(
    (season) => season.season_id.toString() === seasonId.toString()
  )
  const displayYear = activeSeason ? activeSeason.season_year: '';

  useEffect(() => {
    async function loadKnockoutMatches() {
      setIsLoading(true);
      try {
        const url = `http://localhost:8000/leagues/${compId}/${seasonId}/knockouts`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch knockout matches');
        const data = await response.json();
        setKnockoutMatches(data);
      } catch (err) {
        console.error(err);
        setError(`Error, unable to load knockout matches: ${err.message}`);
      } finally {
        setIsLoading(false);
      }
    }
    loadKnockoutMatches();
  }, [compId, seasonId]);

  if (error) {
    return <div className="status-message error">{error}</div>;
  }

  if (isLoading || !knockoutMatches) {
    return <div className="loading-state">Loading knockout bracket...</div>;
  }

  if (knockoutMatches.length === 0) {
    return (
      <div className="status-message">
        No knockout data available for this season.
      </div>
    );
  }

  const matchweeks = knockoutMatches.map(m => m.matchweek);
  const finalMatchweek = Math.max(...matchweeks);

  const semiFinalMatches = knockoutMatches.filter(m => m.matchweek < finalMatchweek);
  const finalMatches = knockoutMatches.filter(m => m.matchweek === finalMatchweek);

  const semiFinalTies = semiFinalMatches.reduce((acc, match) => {
    const tieKey = [match.home_team_id, match.away_team_id].sort().join('-');
    if (!acc[tieKey]) acc[tieKey] = [];
    acc[tieKey].push(match);
    return acc;
  }, {});

  const tiesArray = Object.values(semiFinalTies);

  let championTeam = null;
  let championId = null;

  if (finalMatches.length > 0) {
    const fm = finalMatches[0];
    const hasPens = fm.ps_home_goals !== null && fm.ps_away_goals !== null;
    const hasAET = fm.aet_home_goals !== null && fm.aet_away_goals !== null;

    const homeTotal = fm.ft_home_goals + (hasAET ? fm.aet_home_goals : 0);
    const awayTotal = fm.ft_away_goals + (hasAET ? fm.aet_away_goals: 0);

    const homeWins = hasPens ? fm.ps_home_goals > fm.ps_away_goals : homeTotal > awayTotal;

    championTeam = homeWins ? fm.home_team?.name : fm.away_team?.name;
    championId = homeWins ? fm.home_team_id : fm.away_team_id;
  }

  const isDisqualified = (teamName) => {
    return (
      teamName === 'Southampton' && 
      currentLeague?.name === 'Championship' && 
      displayYear === '2025-26'
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const columns = [
    { id: 'left', title: 'Semi-Final A', matches: tiesArray[0] || [], isFinal: false, connectorClass: 'left-connectors' },
    { id: 'center', title: 'Final', matches: finalMatches, isFinal: true, connectorClass: null },
    { id: 'right', title: 'Semi-Final B', matches: tiesArray[1] || [], isFinal: false, connectorClass: 'right-connectors' },
  ];

  return (
    <div className="league-summary-container">
      <h3 className="section-title">Playoffs & Knockout Stage</h3>

      <div className="bracket-tree-wrapper">

        {championTeam && (
          <div className="champion-section">
            <div className="trophy-icon">🏆</div>
            <div className="champion-badge-container">
              <img
                src={`/logos/teams/${championId}.svg`}
                className="champion-badge"
                alt={`${championTeam} Champions`}
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            </div>
            <div className="champion-text">
              <span className="champion-year">{displayYear} CHAMPIONS</span>
              <span className="champion-name">{championTeam}</span>
            </div>
          </div>
        )}

        <div className="bracket-container">
          {columns.map((col) => (
            <div key={col.id} className={`bracket-column-group ${col.isFinal ? 'center-group' : ''}`}>

              <div className={`bracket-column ${col.isFinal ? 'final-column' : ''}`}>
                <h4 className="bracket-column-title">{col.title}</h4>
                <div className={`bracket-node ${col.isFinal ? 'final-node' : ''}`}>
                  
                  {col.matches.map((match) => {
                    const hasPens = match.ps_home_goals !== null && match.ps_away_goals !== null;
                    const hasAET = match.aet_home_goals !== null && match.aet_away_goals !== null;

                    let homeScore = match.ft_home_goals;
                    let awayScore = match.ft_away_goals;
                    let subText = '';

                    if (hasPens) {
                      homeScore = match.ft_home_goals + (hasAET ? match.aet_home_goals : 0);
                      awayScore = match.ft_away_goals + (hasAET ? match.aet_away_goals : 0);
                      subText = `(${match.ps_home_goals} - ${match.ps_away_goals} pens)`;
                    } else if (hasAET) {
                      homeScore = match.ft_home_goals + match.aet_home_goals;
                      awayScore = match.ft_away_goals + match.aet_away_goals;
                      subText = '(AET)';
                    }

                    const homeDQ = isDisqualified(match.home_team?.name);
                    const awayDQ = isDisqualified(match.away_team?.name);

                    return (
                      <div key={match.id} className="bracket-match-row">
                        <div className="bracket-match-date">
                          {formatDate(match.date)}
                        </div>
                        <div className="match-scoreline knockout">
                          <div className={`bracket-team bracket-team-home ${homeDQ ? 'disqualified' : ''}`}>
                            <img
                              src={`/logos/teams/${match.home_team_id}.svg`}
                              className="bracket-badge"
                              alt={match.home_team?.name}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                            <span className="bracket-team-name">{match.home_team?.name}</span>
                          </div>

                          <div className="bracket-score-wrapper">
                            <div className="bracket-score">{homeScore} - {awayScore}</div>
                            {subText && <span className="bracket-score-subtext">{subText}</span>}
                          </div>

                          <div className={`bracket-team bracket-team-away ${awayDQ ? 'disqualified' : ''}`}>
                            <span className="bracket-team-name">{match.away_team?.name}</span>
                            <img
                              src={`/logos/teams/${match.away_team_id}.svg`}
                              className="bracket-badge"
                              alt={match.away_team?.name}
                              onError={(e) => { e.target.style.display = 'none'; }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}

                </div>
              </div>

              {col.connectorClass && (
                <div className={`bracket-connectors ${col.connectorClass}`}>
                  <div className="connector-line top"></div>
                  <div className="connector-line bottom"></div>
                </div>
              )}

            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
