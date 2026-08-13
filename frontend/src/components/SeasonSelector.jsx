export default function SeasonSelector({ seasons, currSeasonId, onSeasonChange }) {
    return (
			<div className="profile-season-wrapper">
				<select
					className="season-dropdown"
					value={currSeasonId}
					onChange={(e) => onSeasonChange(e.target.value)}
				>
					{seasons.map((season) => (
						<option key={season.season_id} value={season.season_id}>
							{season.season_year}
						</option>
					))}
				</select>
			</div>
		)
}
