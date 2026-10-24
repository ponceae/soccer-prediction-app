from sqlmodel import and_, or_, select

from backend.api.models import Match, TeamCompetition
from backend.services.base import BaseService

class TeamService(BaseService):
    
    def team_outcomes(self, team_id: int, up_to_mw: int | None = None):
        """ 
        Calculate and return the numer of wins, losses, or draws for the given team
        and number of matches.
        """
        max_matchweek = self.max_regular_season_matchweek()

        conditions = [
            Match.competition_id == self.competition_id,
            Match.season_id == self.season_id,
            Match.matchweek <= max_matchweek,
            or_(
                Match.home_team_id == team_id,
                Match.away_team_id == team_id,
            ),
        ]
        if up_to_mw is not None:
            conditions.append(Match.matchweek < up_to_mw)

        statement = select(Match).where(and_(*conditions))
        team_matches = self.session.exec(statement).all()
        total_matches = len(team_matches)
                
        if not total_matches:
            return 0, 0, 0, 0
        
        wins, draws, losses = 0, 0, 0
        
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
        """ 
        Calculate and return the rate of wins, losses, or draws in the given amount
        of games for the specified team.
        """
        wins, losses, draws, total_matches = self.team_outcomes(team_id)
        
        if not total_matches:
            return 0.0, 0.0, 0.0
                    
        wins /= total_matches
        draws /= total_matches
        losses /= total_matches
        
        return wins, draws, losses
    
    def ppg(self, team_id: int):
        """ 
        Calculate and return the points per game rate for the specified team.
        """
        wins, _, draws, total_matches = self.team_outcomes(team_id)
        total_points = (wins * 3) + draws
        
        return total_points / total_matches
    
    def team_clean_sheets(self, team_id: int):
        """ 
        Calculate and return the number of clean sheets for the given team in the
        specified competition season.
        """
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
    
    def team_strengths(self, team_id: int, up_to_mw: int | None = None):
        """ 
        Calculate a team's home and away attacking and defensive strengths.
        """
        max_matchweek = self.max_regular_season_matchweek()

        league_h_goal_avg, league_a_goal_avg = self.league_goal_averages(
            up_to_mw=up_to_mw
        )

        base_h_conditions = [
            Match.competition_id == self.competition_id,
            Match.season_id == self.season_id,
            Match.matchweek <= max_matchweek,
            Match.home_team_id == team_id,
        ]
        base_a_conditions = [
            Match.competition_id == self.competition_id,
            Match.season_id == self.season_id,
            Match.matchweek <= max_matchweek,
            Match.away_team_id == team_id,
        ]
        
        if up_to_mw is not None:
            base_h_conditions.append(Match.matchweek < up_to_mw)
            base_a_conditions.append(Match.matchweek < up_to_mw)
        
        h_matches = self.session.exec(select(Match).where(
            and_(*base_h_conditions)
        )).all()
        a_matches = self.session.exec(select(Match).where(
            and_(*base_a_conditions)
        )).all()
        
        total_h_matches = len(h_matches)
        total_a_matches = len(a_matches)
        
        if total_h_matches == 0:
            raw_h_atk, raw_h_def = 1.0, 1.0
        else:
            avg_h_goals = sum(m.ft_home_goals for m in h_matches) / total_h_matches
            avg_h_goals_conceeded = sum(m.ft_away_goals for m in h_matches) / total_h_matches
            raw_h_atk = (avg_h_goals / league_h_goal_avg) if league_h_goal_avg else 1.0
            raw_h_def = (avg_h_goals_conceeded / league_a_goal_avg) if league_a_goal_avg else 1.0

        if total_a_matches == 0:
            raw_a_atk, raw_a_def = 1.0, 1.0
        else:
            avg_a_goals = sum(m.ft_away_goals for m in a_matches) / total_a_matches
            avg_a_goals_conceeded = sum(m.ft_home_goals for m in a_matches) / total_a_matches
            raw_a_atk = (avg_a_goals / league_a_goal_avg) if league_a_goal_avg else 1.0
            raw_a_def = (avg_a_goals_conceeded / league_h_goal_avg) if league_h_goal_avg else 1.0
        
        (
            prior_h_atk, 
            prior_h_def, 
            prior_a_atk, 
            prior_a_def
        ) = self.get_team_prior_strengths(team_id)
        
        K = 6.0
        w_home_prior = max(0.0, (K - total_h_matches) / K)
        w_away_prior = max(0.0, (K - total_a_matches) / K)
        
        h_atk = (w_home_prior * prior_h_atk) + ((1.0 - w_home_prior) * raw_h_atk)
        h_def = (w_home_prior * prior_h_def) + ((1.0 - w_home_prior) * raw_h_def)
        a_atk = (w_away_prior * prior_a_atk) + ((1.0 - w_away_prior) * raw_a_atk)
        a_def = (w_away_prior * prior_a_def) + ((1.0 - w_away_prior) * raw_a_def)
        
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
        
    def get_team_prior_strengths(self, team_id: int):
        prev_season_id = self.get_previous_season_id()
        
        if not prev_season_id:
            # First season baseline
            return 1.0, 1.0, 1.0, 1.0
        
        was_in_comp = self.session.exec(
            select(
                TeamCompetition
            ).where(
                TeamCompetition.team_id == team_id,
                TeamCompetition.competition_id == self.competition_id,
                TeamCompetition.season_id == prev_season_id,
            )
        ).first()
        
        if not was_in_comp:
            # Promoted team (slight penalties)
            return 0.85, 1.15, 0.85, 1.15
        
        prev_service = TeamService(self.session, self.competition_id, prev_season_id)
        raw_h_atk, raw_h_def, raw_a_atk, raw_a_def = prev_service.team_strengths(team_id)
        
        R = 0.60
        return (
            (R * raw_h_atk) + ((1 - R) * 1.0),
            (R * raw_h_def) + ((1 - R) * 1.0),
            (R * raw_a_atk) + ((1 - R) * 1.0),
            (R * raw_a_def) + ((1 - R) * 1.0),
        )
        