import { useNavigate, useParams } from "react-router-dom";

export default function LeagueTable({ tableData, currentLeague }) {
  const navigate = useNavigate();
  const { compId, seasonId } = useParams();
  
  if (!tableData || !currentLeague) return null;

  return (
    <div className="table-container">
      
      <div className="table-navigation">
        <button className="back-btn" onClick={() => navigate('/')}>
          &larr; Back to Home
        </button>
      </div>

      <div className="league-header-container">
        <div className="league-title-group">
          <img
            src={`/logos/competitions/${compId}.svg`}
            className="competition-badge"
            alt={`${currentLeague.name} logo`}
            onError={(e) => e.target.style.display= 'none'}
          />
          <div className="league-text">
            <h2>{currentLeague.name}</h2>
            <p className="country-subtitle">{currentLeague.country}</p>
          </div>
        </div>
        {currentLeague.seasons && (
          <div className="season-selector">
            <select
              className="season-dropdown"
              value={seasonId}
              onChange={(e) => navigate(
                `/league/${compId}/${e.target.value}`, { state: currentLeague }
              )}
            >
              {currentLeague.seasons.map((season) => (
                <option key={season.season_id} value={season.season_id}>
                  {season.season_year}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th></th>
            <th>Pl</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>GF</th>
            <th>GA</th>
            <th>GD</th>
            <th>Pts</th>
          </tr>
        </thead>
        <tbody>
          {tableData.map((team, index) => {
            const rowClass = (index >= 0 && index <= 3) ? 'ucl' 
                          : (index == 4) ? 'uel' 
                          : (index >= tableData.length- 3) ? 'relegation' 
                          : '';
            return (
              <tr 
                key={team.team_id} 
                className={rowClass}
                onClick={() => navigate(`/team/${compId}/${seasonId}/${team.team_id}`, {
                  state: { 
                    teamName: team.team_name,
                    currentLeague: currentLeague,
                  }
                })}
              >
                <td>{index + 1}</td>
                <td className="team-cell">
                  <img
                    src={`/logos/teams/${team.team_id}.svg`}
                    className="team-badge"
                    alt={`${team.team_name} logo`}
                    onError={(e) => e.target.style.display='none'}
                  />
                  <strong>{team.team_name}</strong>
                </td>
                <td>{team.matches_played}</td>
                <td>{team.wins}</td>
                <td>{team.draws}</td>
                <td>{team.losses}</td>
                <td>{team.gf}</td>
                <td>{team.ga}</td>
                <td>{team.gd}</td>
                <td><strong>{team.points}</strong></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  )
}
