from dataclasses import dataclass
import math
from sqlmodel import Session, or_, select

from models import Match

MAX_GOAL_THRESHOLD = 8

@dataclass
class HomeAwayID:
    home_team_id: int
    away_team_id: int

@dataclass
class Analytics:
    session: Session
    competition_id: int
    season_id: int 

    def get_league_goal_averages(self) -> tuple[float, float]:
        """
        Find and return the home and away goal averages for a particular season in the 
        given competition.
        """
        filter = select(Match).where(
            or_(
                Match.competition_id == self.competition_id, 
                Match.season_id == self.season_id,
            )
        )
        competition_matches = self.session.exec(filter).all()
        total_matches = len(competition_matches)
        
        if not total_matches:
            return 0.0, 0.0
        
        h_goals = sum(m.home_goals for m in competition_matches)
        a_goals = sum(m.away_goals for m in competition_matches)
        
        h_goal_avg = h_goals / total_matches
        a_goal_avg = a_goals / total_matches
        
        return h_goal_avg, a_goal_avg

    def get_team_strengths(self, team_id: int) -> tuple[float, float, float, float]:
        """ 
        Find and return the attacking and defensive strengths for the given team at
        both home and away.
        """
        league_h_goal_avg, league_a_goal_avg = self.get_league_goal_averages()

        h_match_filter = select(Match).where(Match.home_team_id == team_id)
        a_match_filter = select(Match).where(Match.away_team_id == team_id)
        
        h_matches = self.session.exec(h_match_filter).all()
        a_matches = self.session.exec(a_match_filter).all()
        
        total_h_matches = len(h_matches)
        total_a_matches = len(a_matches)

        if not total_h_matches and not total_a_matches:
            return 0.0, 0.0, 0.0, 0.0

        h_goals = sum(m.home_goals for m in h_matches)
        a_goals = sum(m.away_goals for m in a_matches)
        
        h_goals_conceeded = sum(m.away_goals for m in h_matches)
        a_goals_conceeded = sum(m.home_goals for m in a_matches)
        
        avg_h_goals = h_goals / total_h_matches
        avg_a_goals = a_goals / total_a_matches
        
        avg_h_goals_conceeded = h_goals_conceeded / total_h_matches
        avg_a_goals_conceeded = a_goals_conceeded / total_a_matches
        
        h_atk = avg_h_goals / league_h_goal_avg
        h_def = avg_h_goals_conceeded / league_a_goal_avg
        
        a_atk = avg_a_goals / league_a_goal_avg
        a_def = avg_a_goals_conceeded / league_h_goal_avg

        return h_atk, h_def, a_atk, a_def

    def get_expected_goals(self, team_ids: HomeAwayID) -> tuple[float, float]:
        """ 
        Find and return the expected goal values for the given home and away teams.
        """
        h_home_atk, h_home_def, _, _ = self.get_team_strengths(team_ids.home_team_id)
        _, _, a_away_atk, a_away_def = self.get_team_strengths(team_ids.away_team_id)
        
        league_h_goal_avg, league_a_goal_avg = self.get_league_goal_averages()
        
        home_xg = (h_home_atk * a_away_def) * league_h_goal_avg
        away_xg = (a_away_atk * h_home_def) * league_a_goal_avg
        
        return home_xg, away_xg

    @staticmethod
    def generate_poisson_values(xg: float) -> list[float]:
        """ 
        Generate and return a list of possion values from `0` goals to the model's 
        `MAX_GOAL_THRESHOLD` limit based on the given expected goals value.
        """
        pv = []
        
        for i in range(MAX_GOAL_THRESHOLD + 1):
            pv.append(((xg ** i) * (math.exp(-xg))) / math.factorial(i))
        
        return pv

    def poisson_prediction(self, team_ids: HomeAwayID) -> tuple[float, float, float]:
        """ 
        Find and return the win, draw, and loss percentages between two teams.
        """
        h_xg, a_xg = self.get_expected_goals(team_ids)
        
        h_poisson_values = self.generate_poisson_values(h_xg)
        a_poisson_values = self.generate_poisson_values(a_xg)
        
        score_matrix = []
        
        for home_pvs in h_poisson_values:
            pv_row = []
            for away_pvs in a_poisson_values:
                cell = home_pvs * away_pvs
                pv_row.append(cell)
            score_matrix.append(pv_row)
        
        win, loss, draw = 0.0, 0.0, 0.0
        
        for row in range(len(score_matrix)):
            for col in range (len(score_matrix[row])):
                if row == col: # draw
                    draw += score_matrix[row][col]
                elif row > col: # win
                    win += score_matrix[row][col]
                else: # loss
                    loss += score_matrix[row][col]
        
        total_sum = win + loss + draw
        
        win /= total_sum
        draw /= total_sum
        loss /= total_sum
                    
        return win, loss, draw
            