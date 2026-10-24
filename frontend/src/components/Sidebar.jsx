import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import styles from './Sidebar.module.css';

const countryFlags = {
  'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'Spain': '🇪🇸',
};

export default function Sidebar({ menuData, isOpen, onLeagueClick, closeSidebar }) {
  const [expandedCountry, setExpandedCountry] = useState(null);
  
  const navigate = useNavigate();
  const sidebarRef = useRef(null);
  const sidebarClass = isOpen ? `${styles.sidebar} ${styles.open}` : styles.sidebar;

  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event) {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        closeSidebar();
      }
    }
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [closeSidebar, isOpen]); 

  if (!menuData) {
    return (
      <aside className={sidebarClass}>
        <div className={styles['sidebar-header']}>
          <p>Loading menu...</p>
        </div>
      </aside>
    );
  }

  const toggleCountry = (country) => {
    setExpandedCountry(expandedCountry === country ? null : country);
  };

  return (
    <aside className={sidebarClass} ref={sidebarRef}>
      <button 
        className={styles['sidebar-home']}
        onClick={() => {
          navigate('/');
          closeSidebar();
        }}
      >
        Home
      </button>

      <ul className={styles['country-list']}>
        {Object.entries(menuData).map(([country, leagues]) => {
          const isExpanded = expandedCountry === country;

          return (
            <li key={country} className={styles['country-item']}>
              <button 
                className={`${styles['country-header']} ${isExpanded ? styles.active : ''}`}
                onClick={() => toggleCountry(country)}
              >
                {countryFlags[country] || '🌎'} {country} 
                <span className={styles['arrow']}>▼</span>
              </button>
              <ul className={`${styles['league-list']} ${isExpanded ? styles.show : ''}`}>
                {Object.entries(leagues).map(([leagueName, seasons]) => {
                  const latestSeason = seasons[0];

                  return (
                    <li
                      key={leagueName}
                      onClick={() => onLeagueClick(
                        latestSeason?.competition_id,
                        latestSeason?.season_id,
                        leagueName,
                        country,
                        seasons,
                      )}
                    >
                      <span className={styles['league-item-text']}>{leagueName}</span>
                    </li>
                  );
                })}
              </ul>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
