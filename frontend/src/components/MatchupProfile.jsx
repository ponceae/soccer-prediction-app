import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import Outcomes from "./Outcomes";
import Strengths from "./Strengths";
import StatRow from './StatRow';

import styles from './MatchupProfile.module.css';

export default function MatchupProfile() {
  const { compId, seasonId, matchId } = useParams();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading]= useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchProfile() {
      setIsLoading(true);
      setError(null);
      try {
        const url = (
          `http://localhost:8000/${compId}/${seasonId}/matchup/${matchId}/profile`
        );
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch matchup profile.');
        const data = await response.json();
        setProfile(data);
      } catch(err) {
        console.error(err);
        setError(`Error, unable to load team profile: ${err.message}`);
      } finally {
        setIsLoading(false);
      }
    }
    fetchProfile();
  }, [compId, seasonId, matchId]);

  if (error) {
    return <div className="status-message error">{error}</div>;
  }

  if (isLoading || !profile) {
    return <div className="loading-state">Loading matchup profile...</div>;
  }

  const {
    match,
    predictions,
    h2h_matches,
    home_recent_form,
    away_recent_form,
    home_strengths,
    away_strengths,
  } = profile;

  const outcomeData = predictions ? [{
    name: 'Match Odds',
    Win: predictions.win_probability.home_win_probability,
    Draw: predictions.win_probability.draw_probability,
    Loss: predictions.win_probability.away_win_probability,
  }] : [];

  const radarData = (home_strengths && away_strengths) ? [
    { metric: 'Home Attack',  homeValue: home_strengths.home_attack,  awayValue: away_strengths.home_attack },
    { metric: 'Home Defense', homeValue: home_strengths.home_defense, awayValue: away_strengths.home_defense },
    { metric: 'Away Attack',  homeValue: home_strengths.away_attack,  awayValue: away_strengths.away_attack },
    { metric: 'Away Defense', homeValue: home_strengths.away_defense, awayValue: away_strengths.away_defense },
  ] : [];

  const getFormResult = (teamId, matchRecord) => {
    const isHome = matchRecord.home_team_id === teamId;
    const goalsFor = isHome ? matchRecord.ft_home_goals : matchRecord.ft_away_goals;
    const goalsAgainst = isHome ? matchRecord.ft_away_goals : matchRecord.ft_home_goals;
    if (goalsFor > goalsAgainst) {
      return { result: 'W', color: '#2ECC71' };
    }
    if (goalsFor < goalsAgainst) {
      return { result: 'L', color: '#E74C3C' };
    }
    return { result: 'D', color: '#95A5A6' };
  };

  const calcDerivedXG = (totalShots, shotsOnTarget) => {
    const offTargetShots = Math.max(0, totalShots - shotsOnTarget);
    const derivedXG = (shotsOnTarget * 0.30) + (offTargetShots * 0.05);
    return parseFloat(derivedXG.toFixed(2));
  }

  const actualHomeXG = calcDerivedXG(match.home_shots, match.home_sot);
  const actualAwayXG = calcDerivedXG(match.away_shots, match.away_sot);

  return (
    <div className={styles['matchup-profile-container']}>
      <button className='back-btn' onClick={() => navigate(-1)}>
        &larr; Back to Matchups
      </button>

      <div className={styles['matchup-profile-header']}>
        <div className={styles['matchup-profile-team']}>
          <img
            src={`/logos/teams/${match.home_team.id}.svg`}
            alt={match.home_team.name}
            className={styles['team-badge']}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <h2>{match.home_team.name}</h2>
        </div>

        {(() => {
          const isFirstLeg = match.matchweek === 39 || match.matchweek === 47;
          const isSecondLeg = match.matchweek === 40 || match.matchweek === 48;
          const isFinal = match.matchweek === 41 || match.matchweek === 49;
          const isKnockout = isFirstLeg || isSecondLeg || isFinal;

          let aggHome = match.ft_home_goals;
          let aggAway = match.ft_away_goals;
          let firstLegMatch = null;

          if (isSecondLeg) {
            firstLegMatch = h2h_matches.find(m => 
              m.season_id === match.season_id &&
              m.competition_id === match.competition_id &&
              (m.matchweek === 39 || m.matchweek === 47)
            );
            
            if (firstLegMatch) {
              aggHome += (firstLegMatch.home_team_id === match.home_team.id) ? firstLegMatch.ft_home_goals : firstLegMatch.ft_away_goals;
              aggAway += (firstLegMatch.away_team_id === match.away_team.id) ? firstLegMatch.ft_away_goals : firstLegMatch.ft_home_goals;
            }
          }

          return (
            <div className={styles['score-info']}>
              {isFirstLeg && (
                <div className={styles['aggregate-score']}>
                  1st Leg
                </div>
              )}

              {isSecondLeg && firstLegMatch && (
                <div className={styles['aggregate-score']}>
                  Agg {aggHome} - {aggAway}
                </div>
              )}

              <div className={styles['scoreline']}>
                {match.ft_home_goals} - {match.ft_away_goals}
              </div>

              <div className={styles['full-time-label']}>
                Full time
              </div>

              <div className={styles['matchup-date']}>
                {!isKnockout && `Round ${match.matchweek} • `}
                {new Date(match.date).toLocaleDateString()}
              </div>

              {match.referee && (
                <div className={styles['matchup-referee']}>
                  Match Official: {match.referee}
                </div>
              )}
            </div>
          );
        })()}

        <div className={styles['matchup-profile-team']}>
          <img
            src={`/logos/teams/${match.away_team.id}.svg`}
            alt={match.away_team.name}
            className={styles['team-badge']}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <h2>{match.away_team.name}</h2>
        </div>
      </div>

      <div className={styles['section-card']}>
        <h3 className={styles['section-title']}>Match Statistics</h3>
        <div className={styles['stats-container']}>
          <StatRow label='Total Shots' home={match.home_shots} away={match.away_shots} />
          <StatRow label='Shots on Target' home={match.home_sot} away={match.away_sot} />
          <StatRow label='xG' home={actualHomeXG} away={actualAwayXG} />
          <StatRow label='Corners' home={match.home_corners} away={match.away_corners} />
          <StatRow label='Total Fouls' home={match.home_fouls} away={match.away_fouls} />
          <StatRow label='Yellow Cards' home={match.home_yellow_cards} away={match.away_yellow_cards} />
          {(match.home_red_cards > 0 || match.away_red_cards > 0) && (
            <StatRow label='Red Cards' home={match.home_red_cards} away={match.away_red_cards} />
          )}
        </div>
      </div>

      {predictions && (
        <div className={styles['section-card']}>
          <h3 className={styles['section-title']}>Pre-Match Model Predictions</h3>
          <div className={styles['p-charts-grid']}>

            <div className={styles['left-column']}>
              <div className={styles['p-stats-card']}>
                <div className={styles['p-stats-box']}>
                  <h4>Expected Goals (xG)</h4>
                  <div className={styles['xg-display']}>
                    <span className={styles['xg-home']}>
                      {predictions.xg.home_expected_goals.toFixed(2)}
                    </span>
                    <span className={styles['xg-divider']}>-</span>
                    <span className={styles['xg-away']}>
                      {predictions.xg.away_expected_goals.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className={styles['p-stats-box']}>
                  <h4>Likely Scoreline</h4>
                  <div className={styles['big-score']}>
                    {predictions.likely_scoreline[0]} - {predictions.likely_scoreline[1]}
                  </div>
                </div>
              </div>
              <Outcomes outcomeData={outcomeData}/>
            </div>

            <div className={styles['right-column']}>
              <Strengths
                radarData={radarData}
                homeTeamName={match.home_team.name}
                awayTeamName={match.away_team.name}
              />
            </div>
          </div>
        </div>
      )}

      <div className={styles['bottom-grid']}>
        <div className={styles['bottom-card']}>
          <h3>Head to Head</h3>
          {h2h_matches.length === 0 ? <p className={styles['empty-text']}>No recent matchups</p> : (
            <ul className={styles['match-list']}>
              {h2h_matches.map(m => (
                <li key={m.id}>
                  <span className={styles['h2h-date']}>{new Date(m.date).getFullYear()}</span>
                  <span className={styles['h2h-teams']}>
                    {m.home_team.name} <strong>{m.ft_home_goals} - {m.ft_away_goals}</strong> {m.away_team.name}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={styles['bottom-card']}>
          <h3>Team Form</h3>
          <div className={styles['form-split']}>
            <div>
              <h4>{match.home_team.name}</h4>
              <ul className={styles['match-list']}>
                {home_recent_form.map(m => {
                  const form = getFormResult(match.home_team.id, m);
                  return (
                    <li key={m.id} className={styles['form-row']}>
                      <span className={styles['form-badge']} style={{ backgroundColor: form.color }}>{form.result}</span>
                      vs {m.home_team_id === match.home_team.id ? m.away_team.name : m.home_team.name}
                      <span className={styles['form-score']}>({m.ft_home_goals}-{m.ft_away_goals})</span>
                    </li>
                  );
                })}
              </ul>
            </div>

            <div>
              <h4>{match.away_team.name}</h4>
              <ul className={styles['match-list']}>
                {away_recent_form.map(m => {
                  const form = getFormResult(match.away_team.id, m);
                  return (
                    <li key={m.id} className={styles['form-row']}>
                      <span className={styles['form-badge']} style={{ backgroundColor: form.color }}>{form.result}</span>
                      vs {m.home_team_id === match.away_team.id ? m.away_team.name : m.home_team.name}
                      <span className={styles['form-score']}>({m.ft_home_goals}-{m.ft_away_goals})</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
