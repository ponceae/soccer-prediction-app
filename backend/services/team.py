from sqlmodel import and_, or_, select

from models import Match
from services.base import BaseService

class TeamService(BaseService):
    def team_outcomes(self, team_id: int):
        max_matchweek = self.max_regular_season_matchweek()

        statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek,
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id,
                ),
            )
        )
        team_matches = self.session.exec(statement).all()
        total_matches = len(team_matches)
        wins, draws, losses = 0, 0, 0
        
        if not total_matches:
            return 0, 0, 0, 0
        
        for match in team_matches:
            if match.home_team_id == team_id:
                if match.ft_home_goals > match.ft_away_goals:
                    wins += 1
                elif match.ft_home_goals < match.ft_away_goals:
                    losses += 1
                else:
                    draws += 1
            elif match.away_team_id == team_id:
                if match.ft_away_goals > match.ft_home_goals:
                    wins += 1
                elif match.ft_away_goals < match.ft_home_goals:
                    losses += 1
                else:
                    draws += 1
                    
        return wins, losses, draws, total_matches
    
    def outcome_percentages(self, team_id: int):
        wins, losses, draws, total_matches = self.team_outcomes(team_id)
        
        if not total_matches:
            return 0.0, 0.0, 0.0
                    
        wins /= total_matches
        draws /= total_matches
        losses /= total_matches
        
        return wins, draws, losses
    
    def ppg(self, team_id: int):
        wins, _, draws, total_matches = self.team_outcomes(team_id)
        total_points = (wins * 3) + draws
        
        return total_points / total_matches
    
    def team_clean_sheets(self, team_id: int):
        max_matchweek = self.max_regular_season_matchweek()
        
        statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek,
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id,
                )
            )
        )
        
        matches = self.session.exec(statement).all()
        total_matches = len(matches)
        h_cs_counter, a_cs_counter = 0, 0
        
        if not total_matches:
            return 0, 0, 0
        
        for match in matches:
            if match.home_team_id == team_id and match.ft_away_goals == 0:
                h_cs_counter += 1
            elif match.away_team_id == team_id and match.ft_home_goals == 0:
                a_cs_counter += 1
            
        return h_cs_counter, a_cs_counter, (h_cs_counter + a_cs_counter)
    
    def team_strengths(self, team_id: int):
        max_matchweek = self.max_regular_season_matchweek()

        league_h_goal_avg, league_a_goal_avg = self.league_goal_averages()

        h_match_statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek,
                Match.home_team_id == team_id
            )
        )
        a_match_statement = select(Match).where(
            and_(
                Match.competition_id == self.competition_id,
                Match.season_id == self.season_id,
                Match.matchweek <= max_matchweek,
                Match.away_team_id == team_id
            )
        )
        
        h_matches = self.session.exec(h_match_statement).all()
        a_matches = self.session.exec(a_match_statement).all()
        
        total_h_matches = len(h_matches)
        total_a_matches = len(a_matches)

        if not total_h_matches and not total_a_matches:
            return 0.0, 0.0, 0.0, 0.0

        h_goals = sum(m.ft_home_goals for m in h_matches)
        a_goals = sum(m.ft_away_goals for m in a_matches)
        
        h_goals_conceeded = sum(m.ft_away_goals for m in h_matches)
        a_goals_conceeded = sum(m.ft_home_goals for m in a_matches)
        
        avg_h_goals = h_goals / total_h_matches
        avg_a_goals = a_goals / total_a_matches
        
        avg_h_goals_conceeded = h_goals_conceeded / total_h_matches
        avg_a_goals_conceeded = a_goals_conceeded / total_a_matches
        
        h_atk = avg_h_goals / league_h_goal_avg
        h_def = avg_h_goals_conceeded / league_a_goal_avg
        
        a_atk = avg_a_goals / league_a_goal_avg
        a_def = avg_a_goals_conceeded / league_h_goal_avg

        return h_atk, h_def, a_atk, a_def
    
    def generate_team_profile(self, team_id: int):
        h_atk, h_def, a_atk, a_def = self.team_strengths(team_id)
        wins, draws, losses = self.outcome_percentages(team_id)
        (
            h_clean_sheets, 
            a_clean_sheets, 
            total_clean_sheets,
        ) = self.team_clean_sheets(team_id)
        
        return {
            'strengths': {
                'home_attack': h_atk, 
                'home_defense': h_def, 
                'away_attack': a_atk, 
                'away_defense': a_def,
            },
            'outcomes': {
                'win_rate': wins,
                'loss_rate': losses,
                'draw_rate': draws,
            },
            'clean_sheets': {
                'home_clean_sheets': h_clean_sheets,
                'away_clean_sheets': a_clean_sheets,
                'total_clean_sheets': total_clean_sheets,
            },
            'points_per_game': self.ppg(team_id)
        }