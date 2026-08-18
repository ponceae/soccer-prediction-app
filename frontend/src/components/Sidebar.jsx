import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Sidebar({ menuData, isOpen, onLeagueClick, closeSidebar }) {
  const [expandedCountry, setExpandedCountry] = useState(null);
  
  const navigate = useNavigate();
  const sidebarRef = useRef(null);
  const sidebarClass = isOpen ? 'sidebar open' : 'sidebar';

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
        <div className="sidebar-header">
          <p>Loading menu...</p>
        </div>
      </aside>
    );
  }  

  const toggleCountry = (country) => {
    if (expandedCountry === country) {
      setExpandedCountry(null);
    } else {
      setExpandedCountry(country);
    }
  };

  return (
    <aside className={sidebarClass} ref={sidebarRef}>
      <div 
        className="sidebar-home"
        onClick={() => {
          navigate('/')
          closeSidebar();
        }}
      >
        Home
      </div>

      <ul className="country-list">
        {Object.entries(menuData).map(([country, leagues]) => {
          const isExpanded = expandedCountry === country

          return (
            <li key={country} className="country-item">
              <div 
                className={`country-header ${isExpanded ? 'active' : ''}`}
                onClick={() => toggleCountry(country)}
                >
                  🏴󠁧󠁢󠁥󠁮󠁧󠁿 {country} <span className="arrow">▼</span>
              </div>
              <ul className={`league-list ${isExpanded ? 'show' : ''}`}>
                {Object.entries(leagues).map(([leagueName, seasons]) => {
                  const latestSeason = seasons[0];

                  return (
                    <li
                      key={leagueName}
                      className="league-item"
                      onClick={() => onLeagueClick(
                        latestSeason.competition_id,
                        latestSeason.season_id,
                        leagueName,
                        country,
                        seasons,
                      )}
                    >
                      <span className="league-item-text">{leagueName}</span>
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
