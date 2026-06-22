from sqlmodel import Session, select
import math
from models import Match

MAX_GOAL_THRESHOLD = 8

def get_league_goal_averages(session: Session) -> tuple[float, float]:
    """Return the league's home and away goal average."""
    matches = session.exec(select(Match)).all()
    total_matches = len(matches)
    
    if total_matches == 0:
        return 0.0, 0.0
    
    h_goals = sum(m.home_goals for m in matches)
    a_goals = sum(m.away_goals for m in matches)
    
    h_goal_avg = h_goals / total_matches
    a_goal_avg = a_goals / total_matches
    
    return h_goal_avg, a_goal_avg

def get_team_strengths(
    session: Session, 
    team_id: int
) -> tuple[float, float, float, float]:
    league_h_goal_avg, league_a_goal_avg = get_league_goal_averages(session)

    h_match_statement = select(Match).where(Match.home_team_id == team_id)
    a_match_statement = select(Match).where(Match.away_team_id == team_id)
    
    h_matches = session.exec(h_match_statement).all()
    a_matches = session.exec(a_match_statement).all()
    
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

def get_expected_goals(
    session: Session, 
    h_team_id: int, 
    a_team_id
) -> tuple[float, float]:
    
    h_home_atk, h_home_def, _, _ = get_team_strengths(session, h_team_id)
    _, _, a_away_atk, a_away_def = get_team_strengths(session, a_team_id)
    
    league_h_goal_avg, league_a_goal_avg = get_league_goal_averages(session)
    
    home_xg = (h_home_atk * a_away_def) * league_h_goal_avg
    away_xg = (a_away_atk * h_home_def) * league_a_goal_avg
    
    return home_xg, away_xg

def get_poisson_value(xg: float) -> list[float]:
    p = []
    
    for i in range(MAX_GOAL_THRESHOLD + 1):
        p.append(((xg ** i) * (math.exp(-xg))) / math.factorial(i))
    
    return p

def poisson_prediction(
    session: Session, 
    h_team_id: int, 
    a_team_id: int
) -> tuple[float, float, float]:
    h_xg, a_xg = get_expected_goals(session, h_team_id, a_team_id)
    
    h_poisson_values = get_poisson_value(h_xg)
    a_poisson_values = get_poisson_value(a_xg)
    
    score_matrix = []
    
    for hp in h_poisson_values:
        p_row = []
        for ap in a_poisson_values:
            cell = hp * ap
            p_row.append(cell)
        score_matrix.append(p_row)
    
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
            