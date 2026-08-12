import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { 
	ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
	Radar, RadarChart, PolarGrid, PolarAngleAxis
} from "recharts";

export default function TeamProfile({ team }) {
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
					const response = await fetch(`http://localhost:8000/teams/${teamId}/${compId}/${seasonId}/profile`)
					if (!response.ok) throw new Error('Failed to fetch team profile.');
					
					const data = await response.json();
					setTeamData(data);
					setLoading(false);
				} catch(err) {
					console.error(err);
					setError('Unable to load team profile.');
					setLoading(false);
				}
			}
			loadTeamProfile();
    }, [teamId, compId, seasonId]);

		if (loading) {
			return (
				<div className="team-profile-container">
					<h2>Loading {teamName} profile...</h2>
				</div>
			);
		}

		if (error) {
			return (
				<div className="team-profile-container">
					<p>{error}</p>
					<button className="back-btn" onClick={() => navigate(-1)}>Go Back</button>
				</div>
			)
		}

		const outcomeData = [{
			name: 'Match Probability',
			Win: parseFloat((teamData.outcomes.win_rate * 100).toFixed(1)),
			Draw: parseFloat((teamData.outcomes.draw_rate * 100).toFixed(1)),
			Loss: parseFloat((teamData.outcomes.loss_rate).toFixed(1)),
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
					<button className="back-btn" onClick={() => navigate(-1)}>
						&larr; Back to League
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

					{currentLeague?.seasons && (
						<div className="profile-season-wrapper">
							<select
								className="season-dropdown"
								value={seasonId}
								onChange={(e) => navigate(
									`/team/${compId}/${e.target.value}/${teamId}`,
									{state: { teamName, currentLeague }}
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

				<div className="graphs-container">
					
					<div className="chart-card outcomes-card">
						<h3 className="chart-title">Outcome Probabilities</h3>
						<ResponsiveContainer width="100%" height={100}>
							<BarChart layout="vertical" data={outcomeData} stackOffset="expand">
								<XAxis type="number" hide/>
								<YAxis type="category" dataKey="name" hide/>
								<Tooltip formatter={(value) => `${value}%`}/>
								<Bar dataKey="Win" stackId="a" fill="#2ECC71"/>
								<Bar dataKey="Draw" stackId="a" fill="#95A5A6"/>
								<Bar dataKey="Loss" stackId="a" fill="#E74C3C"/>
							</BarChart>
						</ResponsiveContainer>

						<div className="bar-legend">
							<span><strong className="legend-win">Win:</strong>{outcomeData[0].Win}%</span>
							<span><strong className="legend-draw">Draw:</strong>{outcomeData[0].Draw}%</span>
							<span><strong className="legend-loss">Loss:</strong>{outcomeData[0].Loss}%</span>
						</div>
					</div>

					<div className="chart-card strengths-card">
						<h3 className="chart-title-compact">Model Strengths</h3>
						<ResponsiveContainer width="100%" height={250}>
							<RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
								<PolarGrid/>
								<PolarAngleAxis dataKey="metric" tick={{ fill: '#2C3E50', fontSize: 12 }}/>
								<Tooltip/>
								<Radar name={teamName} dataKey="value" stroke="#3498DB" fill="#3498DB" fillOpacity={0.5}/>
							</RadarChart>
						</ResponsiveContainer>
					</div>
				</div>
			</div>
		);
}