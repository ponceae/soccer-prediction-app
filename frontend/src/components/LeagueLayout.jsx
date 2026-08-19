import { Outlet, NavLink, useNavigate, useParams } from 'react-router-dom';
import SeasonSelector from './SeasonSelector';

export default function LeagueLayout({ currentLeague }) {
  const { compId, seasonId } = useParams();
  const navigate = useNavigate();

  const activeSeason = currentLeague?.seasons?.find(
    (season) => season.season_id.toString() === seasonId.toString()
  );
  const displayYear = activeSeason ? activeSeason.season_year : '';

  return (
    <div className="league-layout">

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
            alt={`${currentLeague?.name} logo`}
            onError={(e) => { e.target.style.display= 'none' }}
          />
          <div className="league-text">
            <h2>{currentLeague?.name} {displayYear}</h2>
            <p className="country-subtitle">{currentLeague.country}</p>
          </div>
        </div>
        
        <SeasonSelector 
          seasons={currentLeague?.seasons || []}
          currSeasonId={seasonId}
          onSeasonChange={(newId) => 
            navigate(`/league/${compId}/${newId}`, { 
              state: currentLeague 
            })
          }
        />
      </div>

      <nav className="league-tabs">
        <NavLink to="summary" state={currentLeague} className="tab-link">
          Summary
        </NavLink>
        <NavLink to="table" state={currentLeague} className="tab-link">
          Table
        </NavLink>
        <NavLink to="matchups" state={currentLeague} className="tab-link">
          Matchups
        </NavLink>
      </nav>

      <div className="league-content">
        <Outlet/>
      </div>
    </div>
  );
}
