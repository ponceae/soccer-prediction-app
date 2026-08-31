import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import SeasonSelector from "./SeasonSelector";
import Outcomes from "./Outcomes";
import Strengths from "./Strengths";

export default function TeamProfile() {
  const [teamData, setTeamData] = useState(null);
  const [loading, setLoading]= useState(true);
  const [error, setError] = useState(null);

  const { compId, seasonId, teamId} = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const teamName = location.state?.teamName || `Team ${teamId}`;
  const currentLeague = location.state?.currentLeague;

  useEffect(() => {
    async function loadTeamProfile() {
      try {
        const url = (
          `http://localhost:8000/teams/${teamId}/${compId}/${seasonId}/profile`
        );
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch team profile.');
        const data = await response.json();
        setTeamData(data);
        setLoading(false);
      } catch(err) {
        console.error(err);
        setError(`Error, unable to load team profile: ${err.message}`);
        setLoading(false);
      }
    }
    loadTeamProfile();
  }, [teamId, compId, seasonId]);

  if (loading) return (
    <div className="team-profile-container">
      <h2>Loading {teamName} profile...</h2>
    </div>
  );

  if (error) return (
    <div className="team-profile-container">
      <p>{error}</p>
      <button className="back-btn" onClick={() => navigate(-1)}>Go Back</button>
    </div>
  );

  const outcomeData = [{
    name: 'Match Probability',
    Win: parseFloat((teamData.outcomes.win_rate * 100).toFixed(1)),
    Draw: parseFloat((teamData.outcomes.draw_rate * 100).toFixed(1)),
    Loss: parseFloat((teamData.outcomes.loss_rate * 100).toFixed(1)),
  }]

  const radarData = [
    { metric: 'Home Attack', value: teamData.strengths.home_attack },
    { metric: 'Away Attack', value: teamData.strengths.away_attack },
    { metric: 'Home Defense', value: teamData.strengths.home_defense },
    { metric: 'Away Defense', value: teamData.strengths.away_defense },
  ]

  return (
    <div className="team-profile-container">

      <div className="table-navigation">
        <button className="back-btn" onClick={() => navigate(
          `/league/${compId}/${seasonId}/table`,
          { state: currentLeague }
        )}>
          &larr; Back to Standings
        </button>
      </div>

      <div className="profile-hero">
        <img
          src={`/logos/teams/${teamId}.svg`}
          className="profile-badge"
          alt={`${teamName} logo`}
          onError={(e) => e.target.style.display = 'none'}
        />
        <h2 className="profile-team-name">{teamName}</h2>
        <p className="profile-ppg">
          Season PPG: {teamData.points_per_game.toFixed(2)}
        </p>
        <p className="profile-clean-sheets">
          Season Clean Sheets: {teamData.clean_sheets.total_clean_sheets}
        </p>

        <SeasonSelector
          seasons={currentLeague?.seasons || []}
          currSeasonId={seasonId}
          onSeasonChange={(newId) => navigate(
            `/team/${compId}/${newId}/${teamId}`,
            {state: { teamName, currentLeague }}
          )}
        />
      </div>

      <div className="graphs-container">
        <Outcomes outcomeData={outcomeData}/>
        <Strengths radarData={radarData} teamName={teamName}/>
      </div>
    </div>
  );
}
