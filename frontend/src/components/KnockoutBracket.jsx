import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";

import styles from './KnockoutBracket.module.css';

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
  let finalEliminatedId = null;

  if (finalMatches.length > 0) {
    const fm = finalMatches[0];
    const hasPens = fm.ps_home_goals !== null && fm.ps_away_goals !== null;
    const hasAET = fm.aet_home_goals !== null && fm.aet_away_goals !== null;

    const homeTotal = fm.ft_home_goals + (hasAET ? fm.aet_home_goals : 0);
    const awayTotal = fm.ft_away_goals + (hasAET ? fm.aet_away_goals: 0);

    const homeWins = hasPens ? fm.ps_home_goals > fm.ps_away_goals : homeTotal > awayTotal;

    championTeam = homeWins ? fm.home_team?.name : fm.away_team?.name;
    championId = homeWins ? fm.home_team_id : fm.away_team_id;

    finalEliminatedId = homeWins ? fm.away_team_id : fm.home_team_id;
  }

  const isDisqualified = (teamName) => {
    return (
      teamName === 'Southampton' && 
      currentLeague?.name === 'Championship' && 
      displayYear === '2025-26'
    );
  };

  const getAggregateTieData = (legMatches) => {
    if (!legMatches || legMatches.length === 0) return null;

    const teamA = legMatches[0].home_team;
    const teamB = legMatches[0].away_team;
    const teamAId = legMatches[0].home_team_id;
    const teamBId = legMatches[0].away_team_id;

    let scoreA = 0;
    let scoreB = 0;
    let subText = null;

    legMatches.forEach(m => {
      const hasAET = m.aet_home_goals !== null && m.aet_away_goals !== null;
      const hasPens = m.ps_home_goals !== null && m.ps_away_goals !== null;

      if (m.home_team_id === teamAId) {
        scoreA += m.ft_home_goals + (hasAET ? m.aet_home_goals : 0);
        scoreB += m.ft_away_goals + (hasAET ? m.aet_away_goals : 0);
      } else {
        scoreB += m.ft_home_goals + (hasAET ? m.aet_home_goals : 0);
        scoreA += m.ft_away_goals + (hasAET ? m.aet_away_goals : 0);
      }

      if (hasPens) {
        subText = `(${m.ps_home_goals}-${m.ps_away_goals} pens)`;
      } else if (hasAET && !subText) {
        subText = '(AET)';
      }
    });

    const eliminatedId = scoreA > scoreB ? teamBId : (scoreB > scoreA ? teamAId: null);

    return {teamA, teamB, teamAId, teamBId, scoreA, scoreB, subText, eliminatedId};
  }

  const tieA = getAggregateTieData(tiesArray[0]);
  const tieB = getAggregateTieData(tiesArray[1]);

  const finalMatch = finalMatches[0] || null;

  return (
    <div className="league-summary-container">
      <h3 className="section-title">Playoffs & Knockout Stage</h3>
    
      <div className={styles['bracket-tree-wrapper']}>
        
        {championTeam && (
          <div className={styles['champion-section']}>
            <div className={styles['trophy-icon']}>🏆</div>
            <div className={styles['champion-badge-container']}>
              <img
                src={`/logos/teams/${championId}.svg`}
                className={styles['champion-badge']}
                alt={`${championTeam} Champions`}
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            </div>
            <div className={styles['champion-text']}>
              <span className={styles['champion-year']}>{displayYear} CHAMPIONS</span>
              <span className={styles['champion-name']}>{championTeam}</span>
            </div>
          </div>
        )}

        <div className={styles['bracket-container']}>

          <div className={styles['bracket-column-group']}>
            <div className={styles['bracket-column']}>
              <h4 className={styles['bracket-column-title']}>Semi-Final A</h4>
              {tieA && (
                <div className={styles['bracket-node']}>
                  <div className="match-scoreline knockout">
                    <div className={`${styles['bracket-team']} ${styles['bracket-team-home']} ${
                      isDisqualified(tieA.teamA?.name) ? styles.disqualified : tieA.eliminatedId === tieA.teamAId ? styles.eliminated: ''
                    }`}>
                      <img
                        src={`/logos/teams/${tieA.teamAId}.svg`}
                        className={styles['bracket-badge']}
                        alt={tieA.teamA?.name}
                        onError={(e) => {e.target.style.display = 'none'; }}
                      />
                      <span className={styles['bracket-team-name']}>{tieA.teamA?.name}</span>
                    </div>
                    <div className={styles['bracket-score-wrapper']}>
                      <div className={styles['bracket-score']}>{tieA.scoreA} - {tieA.scoreB}</div>
                      {tieA.subText && <span className={styles['bracket-score-subtext']}>{tieA.subText}</span>}
                    </div>
                    <div className={`${styles['bracket-team']} ${styles['bracket-team-away']} ${
                      isDisqualified(tieA.teamB?.name) ? styles.disqualified : tieA.eliminatedId === tieA.teamBId ? styles.eliminated: ''
                    }`}>
                      <span className={styles['bracket-team-name']}>{tieA.teamB?.name}</span>
                        <img
                        src={`/logos/teams/${tieA.teamBId}.svg`}
                        className={styles['bracket-badge']}
                        alt={tieA.teamB?.name}
                        onError={(e) => {e.target.style.display = 'none'; }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className={styles['bracket-connectors']}>
              <div className={`${styles['connector-line']} ${styles.center}`}></div>
            </div>
          </div>

          <div className={styles['bracket-column-group']}>
            <div className={styles['bracket-column']}>
              <h4 className={styles['bracket-column-title']}>Final</h4>
              {finalMatch && (
                <div className={styles['bracket-node']}>
                  <div className="match-scoreline knockout">
                    <div className={`${styles['bracket-team']} ${styles['bracket-team-home']} ${
                      isDisqualified(finalMatch.home_team?.name) ? styles.disqualified : finalEliminatedId === finalMatch.home_team_id ? styles.eliminated: ''
                    }`}>
                      <img
                        src={`/logos/teams/${finalMatch.home_team_id}.svg`}
                        className={styles['bracket-badge']}
                        alt={finalMatch.home_team?.name}
                        onError={(e) => {e.target.style.display = 'none'; }}
                      />
                      <span className={styles['bracket-team-name']}>{finalMatch.home_team?.name}</span>
                    </div>
                    <div className={styles['bracket-score-wrapper']}>
                      <div className={styles['bracket-score']}>{finalMatch.ft_home_goals} - {finalMatch.ft_away_goals}</div>
                      {finalMatch.ps_home_goals !== null && (
                        <span className={styles['bracket-score-subtext']}>({finalMatch.ps_home_goals}-{finalMatch.ps_away_goals} pens)</span>
                      )}
                    </div>
                    <div className={`${styles['bracket-team']} ${styles['bracket-team-away']} ${
                      isDisqualified(finalMatch.away_team?.name) ? styles.disqualified : finalEliminatedId === finalMatch.away_team_id ? styles.eliminated: ''
                    }`}>
                      <span className={styles['bracket-team-name']}>{finalMatch.away_team?.name}</span>
                      <img
                        src={`/logos/teams/${finalMatch.away_team_id}.svg`}
                        className={styles['bracket-badge']}
                        alt={finalMatch.away_team?.name}
                        onError={(e) => {e.target.style.display = 'none'; }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className={styles['bracket-column-group']}>
            <div className={styles['bracket-connectors']}>
              <div className={`${styles['connector-line']} ${styles.center}`}></div>
            </div>
            <div className={styles['bracket-column']}>
              <h4 className={styles['bracket-column-title']}>Semi-Final B</h4>
              {tieB && (
                <div className={styles['bracket-node']}>
                  <div className="match-scoreline knockout">
                    <div className={`${styles['bracket-team']} ${styles['bracket-team-home']} ${
                      isDisqualified(tieB.teamA?.name) ? styles.disqualified : tieB.eliminatedId === tieB.teamAId ? styles.eliminated: ''
                    }`}>
                      <img
                        src={`/logos/teams/${tieB.teamAId}.svg`}
                        className={styles['bracket-badge']}
                        alt={tieB.teamA?.name}
                        onError={(e) => {e.target.style.display = 'none'; }}
                      />
                      <span className={styles['bracket-team-name']}>{tieB.teamA?.name}</span>
                    </div>
                    <div className={styles['bracket-score-wrapper']}>
                      <div className={styles['bracket-score']}>{tieB.scoreA} - {tieB.scoreB}</div>
                      {tieB.subText && <span className={styles['bracket-score-subtext']}>{tieB.subText}</span>}
                    </div>
                    <div className={`${styles['bracket-team']} ${styles['bracket-team-away']} ${
                      isDisqualified(tieB.teamB?.name) ? styles.disqualified : tieB.eliminatedId === tieB.teamBId ? styles.eliminated: ''
                    }`}>
                      <span className={styles['bracket-team-name']}>{tieB.teamB?.name}</span>
                      <img
                        src={`/logos/teams/${tieB.teamBId}.svg`}
                        className={styles['bracket-badge']}
                        alt={tieB.teamB?.name}
                        onError={(e) => {e.target.style.display = 'none'; }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
