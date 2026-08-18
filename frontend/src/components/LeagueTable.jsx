import { useNavigate, useParams } from "react-router-dom";

export default function LeagueTable({ tableData, currentLeague }) {
  const navigate = useNavigate();
  const { compId, seasonId } = useParams();

  if (!tableData || !currentLeague) return null;

  return (
    <div className="table-container">

      <table className="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th></th>
            <th>Pl</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>+/-</th>
            <th>GD</th>
            <th>Pts</th>
          </tr>
        </thead>
        <tbody>
          {tableData.map((team, index) => {
            const rowClass = (index >= 0 && index <= 4) ? 'ucl' 
                          : (index === 5 || index === 6) ? 'uel' 
                          : (index === 7) ? 'ucfl'
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
                <td>{team.gf}-{team.ga}</td>
                <td>{team.gd > 0 ? `+${team.gd}` : team.gd}</td>
                <td><strong>{team.points}</strong></td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <div className="league-legend-container">
        <div className="legend-item">
          <span className="legend-square ucl"></span>
          <span>Champions League</span>
        </div>
        <div className="legend-item">
          <span className="legend-square uel"></span>
          <span>Europa League</span>
        </div>
        <div className="legend-item">
          <span className="legend-square ucfl"></span>
          <span>Conference League qualification</span>
        </div>
        <div className="legend-item">
          <span className="legend-square relegation"></span>
          <span>Relegation</span>
        </div>
      </div>

    </div>
  )
}
