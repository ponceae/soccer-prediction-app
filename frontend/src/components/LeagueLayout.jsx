import { Outlet, NavLink, useNavigate, useParams } from 'react-router-dom';
import SeasonSelector from './SeasonSelector';

import styles from './LeagueLayout.module.css';

export default function LeagueLayout({ currentLeague }) {
  const { compId, seasonId } = useParams();
  const navigate = useNavigate();

  const activeSeason = currentLeague?.seasons?.find(
    (season) => season.season_id.toString() === seasonId.toString()
  );
  const displayYear = activeSeason ? activeSeason.season_year : '';
  const currentTab = location.pathname.split('/')[4] || 'table';

  return (
    <section className="league-layout">

      <div className="table-navigation">
        <button className="back-btn" onClick={() => navigate('/')}>
          &larr; Back to Home
        </button>
      </div>

      <header className={styles['league-header-container']}>
        <div className={styles['league-title-group']}>
          <img
            src={`/logos/competitions/${compId}.svg`}
            className={styles['competition-badge']}
            alt={`${currentLeague?.name} logo`}
            onError={(e) => { e.target.style.display= 'none' }}
          />
          <hgroup className={styles['league-text']}>
            <h2>{currentLeague?.name} {displayYear}</h2>
            <p className={styles['country-subtitle']}>{currentLeague.country}</p>
          </hgroup>
        </div>
        
        <SeasonSelector 
          seasons={currentLeague?.seasons || []}
          currSeasonId={seasonId}
          onSeasonChange={(newId) => 
            navigate(`/league/${compId}/${newId}/${currentTab}`, { 
              state: currentLeague 
            })
          }
        />
      </header>

      <nav className={styles['league-tabs']}>
        <NavLink 
          to="summary" 
          state={currentLeague} 
          className={({ isActive }) =>
            isActive ? `${styles['tab-link']} ${styles.active}` : styles['tab-link']
          }
        >
          Summary
        </NavLink>
        <NavLink 
          to="table" 
          state={currentLeague} 
          className={({ isActive }) =>
            isActive ? `${styles['tab-link']} ${styles.active}` : styles['tab-link']
          }
        >
          Table
        </NavLink>
        <NavLink 
          to="matchups" 
          state={currentLeague} 
          className={({ isActive }) =>
            isActive ? `${styles['tab-link']} ${styles.active}` : styles['tab-link']
          }
        >
          Matchups
        </NavLink>

        {activeSeason?.has_knockout && (
          <NavLink 
            to="knockout" 
            state={currentLeague} 
            className={({ isActive }) =>
              isActive ? `${styles['tab-link']} ${styles.active}` : styles['tab-link']
          }
          >
            Knockout
          </NavLink>
        )}
      </nav>

      <section className={styles['league-content']}>
        <Outlet/>
      </section>
    </section>
  );
}
