// import { useEffect, useState } from "react";
// import { useParams, useNavigate } from "react-router-dom";

// import Outcomes from "./Outcomes";
// import Strengths from "./Strengths";
// import StatRow from './StatRow';

// import styles from './MatchupProfile.module.css';

// export default function MatchupProfile() {
//   const { compId, seasonId, matchId } = useParams();
//   const navigate = useNavigate();

//   const [profile, setProfile] = useState(null);
//   const [isLoading, setIsLoading]= useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     async function fetchProfile() {
//       setIsLoading(true);
//       setError(null);
//       try {
//         const url = (
//           `http://localhost:8000/${compId}/${seasonId}/matchup/${matchId}/profile`
//         );
//         const response = await fetch(url);
//         if (!response.ok) throw new Error('Failed to fetch matchup profile.');
//         const data = await response.json();
//         setProfile(data);
//       } catch(err) {
//         console.error(err);
//         setError(`Error, unable to load team profile: ${err.message}`);
//       } finally {
//         setIsLoading(false);
//       }
//     }
//     fetchProfile();
//   }, [compId, seasonId, matchId]);

//   if (error) {
//     return <div className="status-message error">{error}</div>;
//   }

//   if (isLoading || !profile) {
//     return <div className="loading-state">Loading matchup profile...</div>;
//   }

//   const {
//     match,
//     predictions,
//     h2h_matches,
//     home_recent_form,
//     away_recent_form,
//     home_strengths,
//     away_strengths,
//   } = profile;

//   const outcomeData = predictions ? [{
//     name: 'Match Odds',
//     Win: predictions.win_probability.home_win_probability,
//     Draw: predictions.win_probability.draw_probability,
//     Loss: predictions.win_probability.away_win_probability,
//   }] : [];

//   const radarData = (home_strengths && away_strengths) ? [
//     { metric: 'Home Attack',  homeValue: home_strengths.home_attack,  awayValue: away_strengths.home_attack },
//     { metric: 'Home Defense', homeValue: home_strengths.home_defense, awayValue: away_strengths.home_defense },
//     { metric: 'Away Attack',  homeValue: home_strengths.away_attack,  awayValue: away_strengths.away_attack },
//     { metric: 'Away Defense', homeValue: home_strengths.away_defense, awayValue: away_strengths.away_defense },
//   ] : [];

//   const getFormResult = (teamId, matchRecord) => {
//     const isHome = matchRecord.home_team_id === teamId;
//     const goalsFor = isHome ? matchRecord.ft_home_goals : matchRecord.ft_away_goals;
//     const goalsAgainst = isHome ? matchRecord.ft_away_goals : matchRecord.ft_home_goals;
//     if (goalsFor > goalsAgainst) {
//       return { result: 'W', color: '#2ECC71' };
//     }
//     if (goalsFor < goalsAgainst) {
//       return { result: 'L', color: '#E74C3C' };
//     }
//     return { result: 'D', color: '#95A5A6' };
//   }
// }