import { useNavigate, useParams } from "react-router-dom";

const qualificationMap = {
  'England': [
    { cssClass: 'tier-1', label: 'Champions League', positions: [0, 1, 2, 3, 4] },
    { cssClass: 'tier-2', label: 'Europa League', positions: [5, 6]},
    { cssClass: 'tier-3', label: 'Conference League qualification', positions: [7]},
    { cssClass: 'relegation', label: 'Relegation', isRelegation: true, count: 3 },
  ],
  'Default': []
}

export default function LeagueTable({ tableData, currentLeague }) {
  const navigate = useNavigate();
  const { compId, seasonId } = useParams();

  if (!tableData || !currentLeague) return null;

  const rules = qualificationMap[currentLeague.country] || qualificationMap['Default'];

  const getRowClass = (index, totalTeams) => {
    for (const rule of rules) {
      if (rule.positions && rule.positions.includes(index)) {
        return rule.cssClass;
      }
      if (rule.isRelegation && index >= totalTeams - rule.count) {
        return rule.cssClass;
      }
    }
    return '';
  }

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
            const rowClass = getRowClass(index, tableData.length);
            return (
              <tr 
                key={team.team_id} 
                className={rowClass}
                onClick={() => 
                  navigate(`/team/${compId}/${seasonId}/${team.team_id}`, {
                    state: { 
                      teamName: team.team_name,
                      currentLeague: currentLeague,
                    }
                  })
                }
              >
                <td>{index + 1}</td>
                <td className="team-cell">
                  <img
                    src={`/logos/teams/${team.team_id}.svg`}
                    className="team-badge"
                    alt={`${team.team_name} logo`}
                    onError={(e) => { e.target.style.display= 'none' }}
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

      {rules.length > 0 && (
        <div className="league-legend-container">
        {rules.map((rule) => (
          <div key={rule.cssClass} className="legend-item">
            <span className={`legend-square ${rule.cssClass}`}></span>
            <span>{rule.label}</span>
          </div>
        ))}
      </div>
      )}
    </div>
  )
}
