import { useState } from 'react';

export default function Sidebar({ menuData, isOpen, onLeagueClick }) {
  const [expandedCountry, setExpandedCountry] = useState(null);
  
  const sidebarClass = isOpen ? 'sidebar open' : 'sidebar';

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
    <aside className={sidebarClass}>
      <div className="sidebar-home">
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
