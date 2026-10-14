import math

from services.base import BaseService, HomeAwayID
from services.team import TeamService

MAX_GOAL_THRESHOLD = 8

class PredictionEngine(BaseService):
    @staticmethod
    def generate_poisson_values(xg: float):
        """
        Generate and return a list of possion values from `0` goals to the model's 
        `MAX_GOAL_THRESHOLD` limit based on the given expected goals value.

        Args:
            xg (float): The expected goals of the team being evaluated.

        Returns:
            list[float]: The list of probabilities of scoring `0` to 
                `MAX_GOAL_THRESHOLD` goals.
        """
        pv = []
        
        for i in range(MAX_GOAL_THRESHOLD + 1):
            pv.append(((xg ** i) * (math.exp(-xg))) / math.factorial(i))
        
        return pv
    
    def expected_goals(self, team_ids: HomeAwayID):
        team_service = TeamService(self.session, self.competition_id, self.season_id)
        
        h_home_atk, h_home_def, _, _ = team_service.team_strengths(team_ids.home_team_id)
        _, _, a_away_atk, a_away_def = team_service.team_strengths(team_ids.away_team_id)
        
        league_h_goal_avg, league_a_goal_avg = self.league_goal_averages()
        
        home_xg = (h_home_atk * a_away_def) * league_h_goal_avg
        away_xg = (a_away_atk * h_home_def) * league_a_goal_avg
        
        return home_xg, away_xg
    
    def poisson_prediction(self, team_ids: HomeAwayID):
        """
        Find and return the probabilities of a win, draw, and loss.
        """         
        h_xg, a_xg = self.expected_goals(team_ids)
        
        h_poisson_values = self.generate_poisson_values(h_xg)
        a_poisson_values = self.generate_poisson_values(a_xg)
        
        score_matrix = []
        
        for home_pvs in h_poisson_values:
            pv_row = []
            for away_pvs in a_poisson_values:
                cell = home_pvs * away_pvs
                pv_row.append(cell)
            score_matrix.append(pv_row)
        
        home_win_p, away_win_p, draw_p = 0.0, 0.0, 0.0
        
        for row in range(len(score_matrix)):
            for col in range (len(score_matrix[row])):
                if row == col: # draw
                    draw_p += score_matrix[row][col]
                elif row > col: # win
                    home_win_p += score_matrix[row][col]
                else: # loss
                    away_win_p += score_matrix[row][col]
        
        total_sum = home_win_p + away_win_p + draw_p
        
        home_win_p /= total_sum
        draw_p /= total_sum
        away_win_p /= total_sum
                    
        return home_win_p, draw_p, away_win_p
    
    def scoreline_chance(self, team_ids: HomeAwayID):
        h_xg, a_xg = self.expected_goals(team_ids)
                
        h_poisson_values = self.generate_poisson_values(h_xg)
        a_poisson_values = self.generate_poisson_values(a_xg)
        
        score_matrix = []
        
        for home_pvs in h_poisson_values:
            pv_row = []
            for away_pvs in a_poisson_values:
                cell = home_pvs * away_pvs
                pv_row.append(cell)
            score_matrix.append(pv_row)
        
        m = 0
        scoreline = (0, 0) # home - away
        for row in range(len(score_matrix)):
            for col in range(len(score_matrix[row])):
                temp = max(m, score_matrix[row][col])
                if temp > m:
                    m = temp
                    scoreline = (row, col)
                
        return scoreline 
    
    def generate_matchup_prediction(self, teams: HomeAwayID):
        h_xg, a_xg = self.expected_goals(teams)
        home_win, draw, away_win = self.poisson_prediction(teams)
        
        return {
            'xg': {
                'home_expected_goals': h_xg,
                'away_expected_goals': a_xg,
            },
            'win_probability': {
                'home_win_probability': round((home_win * 100), 3),
                'away_win_probability': round((away_win * 100), 3),
                'draw_probability': round((draw * 100), 3),
            },
            'likely_scoreline': self.scoreline_chance(teams),
        }
    