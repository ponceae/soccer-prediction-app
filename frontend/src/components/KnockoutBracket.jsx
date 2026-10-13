import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function KnockoutBracket() {
  const { compId, seasonId } = useParams();

  const [knockoutMatches, setKnockoutMatches] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

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

  const groupedMatches = knockoutMatches.reduce((acc, match) => {
    if (!acc[match.matchweek]) {
      acc[match.matchweek] = [];
    }
    acc[match.matchweek].push(match);
    return acc;
  }, {});

  const sortedMatchweeks = Object.keys(groupedMatches).sort((a, b) => Number(a) - Number(b));

  const getRoundName = (index, totalRounds) => {
    if (totalRounds === 3) {
      if (index === 0) return "Playoff Semi-Finals (Leg 1)";
      if (index === 1) return "Playoff Semi-Finals (Leg 2)";
      if (index === 2) return "Playoff Final";
    }
    return `Playoff Round ${index + 1}`;
  };

  return (
    <div className="league-summary-container knockout">
      <h3 className="section-title">Playoffs / Knockout Stage</h3>

      <div className="matchups-container knockout">
        {sortedMatchweeks.map((mw, index) => (
          <div key={mw} className="matchweek-group knockout">

            <div className="matchweek-header knockout">
              <h3>{getRoundName(index, sortedMatchweeks.length)}</h3>
            </div>

            <div className="matchweek-games knockout">
              {groupedMatches[mw].map((match) => {
                const hasPens = match.ps_home_goals !== null && match.ps_away_goals !== null;
                const hasAET = match.aet_home_goals !== null && match.aet_away_goals !== null;

                let homeScore = match.ft_home_goals;
                let awayScore = match.ft_away_goals;
                let subText = "";

                if (hasPens) {
                  homeScore = match.ft_home_goals + (hasAET ? match.aet_home_goals : 0);
                  awayScore = match.ft_haway_goals + (hasAET ? match.aet_away_goals : 0);
                  subText = `(${match.ps_home_goals} - ${match.ps_away_goals} pens)`;
                } else if (hasAET) {
                  homeScore = match.ft_home_goals + match.aet_home_goals;
                  awayScore = match.ft_away_goals + match.aet_away_goals;
                  subText = "(AET)";
                }

                return (
                  <div key={match.id} className="match-row knockout">
                    <div className="match-date knockout">{match.date}</div>

                    <div className="match-scoreline knockout">
                      <div className="team-home knockout">
                        {match.home_team?.name}
                        <img
                          src={`/logos/teams/${match.home_team_id}.svg`}
                          className="score-badge knockout"
                          alt={match.home_team?.name}
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      </div>

                      <div className="score-wrapper knockout">
                        <div className="score knockout">{homeScore} - {awayScore}</div>
                        {subText && (
                          <span className="score-subtext knockout">
                            {subText}
                          </span>
                        )}
                      </div>

                      <div className="team-away knockout">
                        <img
                          src={`/logos/teams/${match.away_team_id}.svg`}
                          className="score-badge knockout"
                          alt={match.away_team?.name}
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                        {match.away_team?.name}
                      </div>

                    </div>
                  </div>
                );
              })}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}
