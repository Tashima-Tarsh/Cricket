import { MatchInfo, Player, StadiumVenue, BallTrajectory, HeadToHeadBattle, Lineup, DataProviderTelemetry } from "../types";

export const VENUES: StadiumVenue[] = [
  {
    id: "chinnaswamy",
    name: "M.Chinnaswamy Stadium",
    city: "Bengaluru",
    soil_type: "Sub-surface air-injected red clay with sand base (Rapid Drainage)",
    avg_first_innings: 202,
    avg_second_innings: 188,
    chasing_win_pct: 70.0,
    pace_wicket_pct: 64.0,
    spin_wicket_pct: 36.0,
    dew_factor: 0.32,
    pitch_nature: "Flat batting deck with true bounce, thin air altitude (~920m), and short square boundaries (58m-62m). Premier six-hitting venue.",
    boundaries: {
      square_leg: 60,
      midwicket: 64,
      long_on: 70,
      straight: 70,
      long_off: 70,
      cover: 64,
      point: 58
    }
  },
  {
    id: "hyderabad",
    name: "Rajiv Gandhi International Stadium",
    city: "Hyderabad",
    soil_type: "80% Red Clay + 20% Black Soil",
    avg_first_innings: 194,
    avg_second_innings: 178,
    chasing_win_pct: 56.5,
    pace_wicket_pct: 64.0,
    spin_wicket_pct: 36.0,
    dew_factor: 0.38,
    pitch_nature: "Hard re-soiled surface with high true bounce. Batting paradise with early seam movement in overs 1-5.",
    boundaries: {
      square_leg: 65,
      midwicket: 68,
      long_on: 72,
      straight: 74,
      long_off: 72,
      cover: 68,
      point: 64
    }
  },
  {
    id: "eden_gardens",
    name: "Eden Gardens",
    city: "Kolkata",
    soil_type: "Black Cotton Soil",
    avg_first_innings: 182,
    avg_second_innings: 172,
    chasing_win_pct: 54.0,
    pace_wicket_pct: 62.0,
    spin_wicket_pct: 38.0,
    dew_factor: 0.45,
    pitch_nature: "True carry and sharp bounce. Heavy evening dew severely impairs finger spin grip.",
    boundaries: {
      square_leg: 66,
      midwicket: 69,
      long_on: 74,
      straight: 76,
      long_off: 74,
      cover: 68,
      point: 65
    }
  },
  {
    id: "wankhede",
    name: "Wankhede Stadium",
    city: "Mumbai",
    soil_type: "Red Soil",
    avg_first_innings: 198,
    avg_second_innings: 186,
    chasing_win_pct: 62.0,
    pace_wicket_pct: 70.0,
    spin_wicket_pct: 30.0,
    dew_factor: 0.52,
    pitch_nature: "Red soil offers tremendous pace and bounce. Short square boundaries (64m) lead to 200+ shootouts.",
    boundaries: {
      square_leg: 63,
      midwicket: 66,
      long_on: 70,
      straight: 71,
      long_off: 70,
      cover: 66,
      point: 63
    }
  },
  {
    id: "chepauk",
    name: "MA Chidambaram Stadium",
    city: "Chennai",
    soil_type: "Clay Soil with Low Moisture",
    avg_first_innings: 164,
    avg_second_innings: 152,
    chasing_win_pct: 46.0,
    pace_wicket_pct: 44.0,
    spin_wicket_pct: 56.0,
    dew_factor: 0.20,
    pitch_nature: "Gripping, dry surface. Spinners dominate middle overs (7-15) with low bounce and sharp turn.",
    boundaries: {
      square_leg: 67,
      midwicket: 70,
      long_on: 72,
      straight: 73,
      long_off: 72,
      cover: 69,
      point: 66
    }
  }
];

export const CURRENT_MATCH: MatchInfo = {
  id: "ind-vs-wi-t20i-2026",
  name: "India vs West Indies, 4th T20I",
  format: "T20 International",
  status: "LIVE • 1st Innings (11.4 / 20 Ov)",
  venue: VENUES[0],
  teams: {
    home: { name: "India", code: "IND", score: "118/2", overs: "11.4" },
    away: { name: "West Indies", code: "WI", score: "—", overs: "20.0" }
  },
  toss: {
    winner: "IND",
    choice: "bowl",
    statement: "India won the toss and elected to bowl first (Evening Dew Factor)"
  },
  current_crr: 10.11,
  projected_total: 214,
  chasing_win_prob: 0.68
};

export const PLAYERS_DB: Player[] = [
  // INDIA
  {
    id: "ind_abhishek",
    name: "Abhishek Sharma",
    team: "IND",
    role: "BAT",
    credits: 9.0,
    batting_style: "LHB",
    bowling_style: "Slow Left-Arm Orthodox",
    batting_order: 1,
    expected_overs: 1.0,
    projected_ownership: 88.0,
    projected_points: 71.1,
    ceiling_score: 150.0,
    floor_score: 15.0,
    is_confirmed_xi: true,
    stats: {
      matches: 28, runs: 890, balls_faced: 480, strike_rate: 185.4, batting_avg: 35.6,
      wickets: 8, overs_bowled: 26.0, economy: 8.2, bowling_sr: 19.5, dot_ball_pct: 32.0,
      boundary_pct: 26.4, recent_scores: [58, 84, 16, 75, 42], recent_wickets: [0, 1, 0, 1, 0],
      recent_fantasy_pts: [88, 122, 28, 110, 64], avg_fantasy_pts: 74.5, ceiling_pts: 150.0, floor_pts: 15.0
    }
  },
  {
    id: "ind_samson",
    name: "Sanju Samson",
    team: "IND",
    role: "WK",
    credits: 8.5,
    batting_style: "RHB",
    batting_order: 2,
    expected_overs: 0.0,
    projected_ownership: 58.0,
    projected_points: 69.7,
    ceiling_score: 175.0,
    floor_score: 10.0,
    is_confirmed_xi: true,
    stats: {
      matches: 42, runs: 1140, balls_faced: 740, strike_rate: 154.0, batting_avg: 32.5,
      wickets: 0, overs_bowled: 0.0, economy: 0.0, bowling_sr: 0.0, dot_ball_pct: 38.0,
      boundary_pct: 22.1, recent_scores: [34, 111, 0, 108, 12], recent_wickets: [],
      recent_fantasy_pts: [50, 162, 4, 158, 20], avg_fantasy_pts: 79.2, ceiling_pts: 175.0, floor_pts: 10.0
    }
  },
  {
    id: "ind_surya",
    name: "Suryakumar Yadav",
    team: "IND",
    role: "BAT",
    credits: 9.0,
    batting_style: "RHB",
    batting_order: 3,
    expected_overs: 0.0,
    projected_ownership: 84.0,
    projected_points: 68.4,
    ceiling_score: 145.0,
    floor_score: 16.0,
    is_confirmed_xi: true,
    stats: {
      matches: 76, runs: 2480, balls_faced: 1476, strike_rate: 168.0, batting_avg: 42.7,
      wickets: 0, overs_bowled: 0.0, economy: 0.0, bowling_sr: 0.0, dot_ball_pct: 29.0,
      boundary_pct: 25.0, recent_scores: [16, 56, 48, 83, 29], recent_wickets: [],
      recent_fantasy_pts: [26, 82, 70, 120, 42], avg_fantasy_pts: 71.0, ceiling_pts: 145.0, floor_pts: 16.0
    }
  },
  {
    id: "ind_tilak",
    name: "Tilak Varma",
    team: "IND",
    role: "BAT",
    credits: 8.5,
    batting_style: "LHB",
    bowling_style: "Right-Arm Offbreak",
    batting_order: 4,
    expected_overs: 1.5,
    projected_ownership: 44.0,
    projected_points: 70.5,
    ceiling_score: 160.0,
    floor_score: 20.0,
    is_confirmed_xi: true,
    differential_tag: "Middle Anchor & Off-spin Counter",
    stats: {
      matches: 32, runs: 920, balls_faced: 630, strike_rate: 146.0, batting_avg: 38.3,
      wickets: 6, overs_bowled: 20.0, economy: 7.8, bowling_sr: 20.0, dot_ball_pct: 34.0,
      boundary_pct: 18.5, recent_scores: [48, 72, 31, 55, 18], recent_wickets: [1, 0, 1, 0, 0],
      recent_fantasy_pts: [72, 104, 52, 85, 28], avg_fantasy_pts: 68.2, ceiling_pts: 160.0, floor_pts: 20.0
    }
  },
  {
    id: "ind_axar",
    name: "Axar Patel",
    team: "IND",
    role: "AR",
    credits: 9.0,
    batting_style: "LHB",
    bowling_style: "Slow Left-Arm Orthodox",
    batting_order: 6,
    expected_overs: 4.0,
    projected_ownership: 79.0,
    projected_points: 77.6,
    ceiling_score: 150.0,
    floor_score: 27.2,
    is_confirmed_xi: true,
    stats: {
      matches: 65, runs: 680, balls_faced: 470, strike_rate: 144.6, batting_avg: 24.2,
      wickets: 68, overs_bowled: 220.0, economy: 7.1, bowling_sr: 19.4, dot_ball_pct: 46.0,
      boundary_pct: 16.0, recent_scores: [24, 18, 35, 12, 40], recent_wickets: [2, 1, 3, 1, 2],
      recent_fantasy_pts: [82, 60, 114, 48, 96], avg_fantasy_pts: 78.5, ceiling_pts: 150.0, floor_pts: 27.2
    }
  },
  {
    id: "ind_arshdeep",
    name: "Arshdeep Singh",
    team: "IND",
    role: "BOWL",
    credits: 9.0,
    batting_style: "LHB",
    bowling_style: "Left-Arm Fast-Medium",
    batting_order: 10,
    expected_overs: 4.0,
    projected_ownership: 86.0,
    projected_points: 68.2,
    ceiling_score: 148.0,
    floor_score: 14.0,
    is_confirmed_xi: true,
    stats: {
      matches: 58, runs: 42, balls_faced: 35, strike_rate: 120.0, batting_avg: 8.0,
      wickets: 89, overs_bowled: 204.0, economy: 8.3, bowling_sr: 13.7, dot_ball_pct: 42.0,
      boundary_pct: 0.0, recent_scores: [0, 4, 2, 0, 1], recent_wickets: [3, 2, 1, 4, 1],
      recent_fantasy_pts: [98, 70, 38, 128, 42], avg_fantasy_pts: 75.2, ceiling_pts: 148.0, floor_pts: 14.0
    }
  },
  {
    id: "ind_mayank",
    name: "Mayank Yadav",
    team: "IND",
    role: "BOWL",
    credits: 8.0,
    batting_style: "RHB",
    bowling_style: "Right-Arm Fast (155 km/h)",
    batting_order: 11,
    expected_overs: 4.0,
    projected_ownership: 28.5,
    projected_points: 60.9,
    ceiling_score: 140.0,
    floor_score: 12.0,
    is_confirmed_xi: true,
    differential_tag: "155kph Express Pace Weapon",
    stats: {
      matches: 12, runs: 10, balls_faced: 8, strike_rate: 125.0, batting_avg: 5.0,
      wickets: 22, overs_bowled: 44.0, economy: 7.2, bowling_sr: 12.0, dot_ball_pct: 54.0,
      boundary_pct: 0.0, recent_scores: [0, 2, 0, 4, 0], recent_wickets: [3, 2, 1, 3, 2],
      recent_fantasy_pts: [96, 72, 38, 98, 68], avg_fantasy_pts: 74.4, ceiling_pts: 140.0, floor_pts: 12.0
    }
  },

  // WEST INDIES
  {
    id: "wi_hope",
    name: "Shai Hope",
    team: "WI",
    role: "WK",
    credits: 9.0,
    batting_style: "RHB",
    batting_order: 1,
    expected_overs: 0.0,
    projected_ownership: 76.0,
    projected_points: 64.0,
    ceiling_score: 135.0,
    floor_score: 18.0,
    is_confirmed_xi: true,
    stats: {
      matches: 48, runs: 1420, balls_faced: 1080, strike_rate: 131.5, batting_avg: 36.4,
      wickets: 0, overs_bowled: 0.0, economy: 0.0, bowling_sr: 0.0, dot_ball_pct: 36.0,
      boundary_pct: 17.2, recent_scores: [42, 68, 14, 55, 38], recent_wickets: [],
      recent_fantasy_pts: [62, 98, 22, 80, 56], avg_fantasy_pts: 63.6, ceiling_pts: 135.0, floor_pts: 18.0
    }
  },
  {
    id: "wi_pooran",
    name: "Nicholas Pooran",
    team: "WI",
    role: "WK",
    credits: 9.0,
    batting_style: "LHB",
    batting_order: 3,
    expected_overs: 0.0,
    projected_ownership: 82.0,
    projected_points: 72.0,
    ceiling_score: 165.0,
    floor_score: 12.0,
    is_confirmed_xi: true,
    stats: {
      matches: 98, runs: 2280, balls_faced: 1490, strike_rate: 153.0, batting_avg: 29.6,
      wickets: 0, overs_bowled: 0.0, economy: 0.0, bowling_sr: 0.0, dot_ball_pct: 35.0,
      boundary_pct: 24.0, recent_scores: [24, 75, 12, 64, 48], recent_wickets: [],
      recent_fantasy_pts: [38, 114, 18, 96, 74], avg_fantasy_pts: 68.0, ceiling_pts: 165.0, floor_pts: 12.0
    }
  },
  {
    id: "wi_powell",
    name: "Rovman Powell",
    team: "WI",
    role: "BAT",
    credits: 8.5,
    batting_style: "RHB",
    bowling_style: "Right-Arm Medium",
    batting_order: 5,
    expected_overs: 1.0,
    projected_ownership: 55.0,
    projected_points: 58.5,
    ceiling_score: 142.0,
    floor_score: 12.0,
    is_confirmed_xi: true,
    stats: {
      matches: 82, runs: 1520, balls_faced: 1040, strike_rate: 146.1, batting_avg: 26.2,
      wickets: 7, overs_bowled: 28.0, economy: 9.1, bowling_sr: 24.0, dot_ball_pct: 39.0,
      boundary_pct: 21.0, recent_scores: [36, 12, 52, 8, 44], recent_wickets: [0, 0, 1, 0, 0],
      recent_fantasy_pts: [54, 18, 86, 14, 68], avg_fantasy_pts: 55.0, ceiling_pts: 142.0, floor_pts: 12.0
    }
  },
  {
    id: "wi_rutherford",
    name: "Sherfane Rutherford",
    team: "WI",
    role: "BAT",
    credits: 8.0,
    batting_style: "LHB",
    bowling_style: "Right-Arm Fast-Medium",
    batting_order: 6,
    expected_overs: 0.0,
    projected_ownership: 29.0,
    projected_points: 52.0,
    ceiling_score: 138.0,
    floor_score: 10.0,
    is_confirmed_xi: true,
    differential_tag: "Death Overs Counter-Attacker",
    stats: {
      matches: 34, runs: 640, balls_faced: 420, strike_rate: 152.3, batting_avg: 28.0,
      wickets: 2, overs_bowled: 8.0, economy: 9.8, bowling_sr: 24.0, dot_ball_pct: 36.0,
      boundary_pct: 22.0, recent_scores: [48, 22, 68, 14, 32], recent_wickets: [],
      recent_fantasy_pts: [74, 32, 102, 22, 48], avg_fantasy_pts: 55.6, ceiling_pts: 138.0, floor_pts: 10.0
    }
  },
  {
    id: "wi_shepherd",
    name: "Romario Shepherd",
    team: "WI",
    role: "AR",
    credits: 8.5,
    batting_style: "RHB",
    bowling_style: "Right-Arm Fast-Medium",
    batting_order: 7,
    expected_overs: 3.5,
    projected_ownership: 68.0,
    projected_points: 66.5,
    ceiling_score: 152.0,
    floor_score: 18.0,
    is_confirmed_xi: true,
    stats: {
      matches: 52, runs: 580, balls_faced: 375, strike_rate: 154.6, batting_avg: 22.3,
      wickets: 54, overs_bowled: 165.0, economy: 9.4, bowling_sr: 18.3, dot_ball_pct: 38.0,
      boundary_pct: 20.0, recent_scores: [28, 14, 39, 8, 26], recent_wickets: [2, 1, 1, 3, 0],
      recent_fantasy_pts: [84, 52, 88, 92, 38], avg_fantasy_pts: 70.8, ceiling_pts: 152.0, floor_pts: 18.0
    }
  },
  {
    id: "wi_joseph",
    name: "Alzarri Joseph",
    team: "WI",
    role: "BOWL",
    credits: 8.5,
    batting_style: "RHB",
    bowling_style: "Right-Arm Fast (148 km/h)",
    batting_order: 9,
    expected_overs: 4.0,
    projected_ownership: 62.0,
    projected_points: 62.0,
    ceiling_score: 142.0,
    floor_score: 14.0,
    is_confirmed_xi: true,
    stats: {
      matches: 48, runs: 85, balls_faced: 70, strike_rate: 121.4, batting_avg: 8.5,
      wickets: 66, overs_bowled: 180.0, economy: 8.6, bowling_sr: 16.3, dot_ball_pct: 44.0,
      boundary_pct: 0.0, recent_scores: [0, 4, 0, 1, 0], recent_wickets: [2, 3, 1, 2, 1],
      recent_fantasy_pts: [68, 98, 38, 70, 42], avg_fantasy_pts: 63.2, ceiling_pts: 142.0, floor_pts: 14.0
    }
  },
  {
    id: "wi_motie",
    name: "Gudakesh Motie",
    team: "WI",
    role: "BOWL",
    credits: 8.0,
    batting_style: "LHB",
    bowling_style: "Slow Left-Arm Orthodox",
    batting_order: 10,
    expected_overs: 4.0,
    projected_ownership: 48.0,
    projected_points: 56.0,
    ceiling_score: 130.0,
    floor_score: 16.0,
    is_confirmed_xi: true,
    stats: {
      matches: 26, runs: 34, balls_faced: 30, strike_rate: 113.3, batting_avg: 6.8,
      wickets: 34, overs_bowled: 92.0, economy: 7.4, bowling_sr: 16.2, dot_ball_pct: 48.0,
      boundary_pct: 0.0, recent_scores: [0, 0, 2, 0, 0], recent_wickets: [2, 1, 2, 0, 3],
      recent_fantasy_pts: [64, 38, 62, 18, 92], avg_fantasy_pts: 54.8, ceiling_pts: 130.0, floor_pts: 16.0
    }
  }
];

export const BALL_TRAJECTORIES: BallTrajectory[] = [
  { id: "b1", over: 1, ball: 1, bowler: "Arshdeep Singh", batter: "Shai Hope", speed_kmh: 138, length: "Good Length", line: "Outside Off", pitch_x: 0.22, pitch_y: 5.4, bounce_height_m: 0.88, outcome: "Dot", phase: "Powerplay" },
  { id: "b2", over: 1, ball: 2, bowler: "Arshdeep Singh", batter: "Shai Hope", speed_kmh: 136, length: "Full", line: "Outside Off", pitch_x: 0.45, pitch_y: 3.2, bounce_height_m: 0.65, outcome: "Boundary 4", phase: "Powerplay" },
  { id: "b3", over: 1, ball: 3, bowler: "Arshdeep Singh", batter: "Shai Hope", speed_kmh: 141, length: "Yorker", line: "Stumps", pitch_x: 0.02, pitch_y: 1.1, bounce_height_m: 0.32, outcome: "1 Run", phase: "Powerplay" },
  { id: "b4", over: 2, ball: 4, bowler: "Mayank Yadav", batter: "Brandon King", speed_kmh: 154, length: "Short", line: "Stumps", pitch_x: -0.05, pitch_y: 8.6, bounce_height_m: 1.45, outcome: "Dot", phase: "Powerplay" },
  { id: "b5", over: 2, ball: 5, bowler: "Mayank Yadav", batter: "Brandon King", speed_kmh: 156, length: "Good Length", line: "Stumps", pitch_x: 0.01, pitch_y: 5.8, bounce_height_m: 0.95, outcome: "Wicket", wicket_type: "Bowled (156 km/h express)", phase: "Powerplay" },
  { id: "b6", over: 5, ball: 2, bowler: "Axar Patel", batter: "Nicholas Pooran", speed_kmh: 96, length: "Good Length", line: "Outside Off", pitch_x: 0.38, pitch_y: 4.8, bounce_height_m: 0.72, outcome: "Dot", phase: "Powerplay" },
  { id: "b7", over: 5, ball: 3, bowler: "Axar Patel", batter: "Nicholas Pooran", speed_kmh: 94, length: "Full", line: "Stumps", pitch_x: 0.04, pitch_y: 2.8, bounce_height_m: 0.58, outcome: "Six", phase: "Powerplay" },
  { id: "b8", over: 8, ball: 1, bowler: "Kuldeep Yadav", batter: "Nicholas Pooran", speed_kmh: 88, length: "Full", line: "Outside Off", pitch_x: 0.42, pitch_y: 3.1, bounce_height_m: 0.62, outcome: "Dot", phase: "Middle" },
  { id: "b9", over: 8, ball: 4, bowler: "Kuldeep Yadav", batter: "Nicholas Pooran", speed_kmh: 86, length: "Good Length", line: "Stumps", pitch_x: 0.08, pitch_y: 4.5, bounce_height_m: 0.82, outcome: "Wicket", wicket_type: "c Samson b Kuldeep (Googly)", phase: "Middle" },
  { id: "b10", over: 11, ball: 2, bowler: "Alzarri Joseph", batter: "Abhishek Sharma", speed_kmh: 147, length: "Short", line: "Outside Off", pitch_x: 0.65, pitch_y: 8.2, bounce_height_m: 1.38, outcome: "Boundary 4", phase: "Middle" },
  { id: "b11", over: 11, ball: 4, bowler: "Romario Shepherd", batter: "Abhishek Sharma", speed_kmh: 134, length: "Full", line: "Stumps", pitch_x: -0.04, pitch_y: 2.5, bounce_height_m: 0.60, outcome: "Six", phase: "Middle" },
  { id: "b12", over: 18, ball: 1, bowler: "Arshdeep Singh", batter: "Rovman Powell", speed_kmh: 139, length: "Yorker", line: "Stumps", pitch_x: 0.01, pitch_y: 0.8, bounce_height_m: 0.28, outcome: "Dot", phase: "Death" },
  { id: "b13", over: 18, ball: 3, bowler: "Arshdeep Singh", batter: "Sherfane Rutherford", speed_kmh: 137, length: "Yorker", line: "Outside Off", pitch_x: 0.35, pitch_y: 0.9, bounce_height_m: 0.31, outcome: "1 Run", phase: "Death" },
  { id: "b14", over: 19, ball: 4, bowler: "Mayank Yadav", batter: "Romario Shepherd", speed_kmh: 153, length: "Yorker", line: "Stumps", pitch_x: 0.00, pitch_y: 0.6, bounce_height_m: 0.25, outcome: "Wicket", wicket_type: "Bowled (Yorker 153 km/h)", phase: "Death" }
];

export const HEAD_TO_HEAD_BATTLES: HeadToHeadBattle[] = [
  {
    batter_id: "wi_pooran",
    batter_name: "Nicholas Pooran",
    bowler_id: "ind_kuldeep",
    bowler_name: "Kuldeep Yadav",
    balls: 48,
    runs: 52,
    dismissals: 4,
    strike_rate: 108.3,
    dot_pct: 46.0,
    boundaries_count: 5,
    advantage: "Bowler Dominant",
    tactical_notes: "Kuldeep has dismissed Pooran 4 times in 48 balls using the googly and dipping chinaman length.",
    win_probability_batter: 0.28
  },
  {
    batter_id: "ind_samson",
    batter_name: "Sanju Samson",
    bowler_id: "wi_joseph",
    bowler_name: "Alzarri Joseph",
    balls: 42,
    runs: 68,
    dismissals: 2,
    strike_rate: 161.9,
    dot_pct: 32.0,
    boundaries_count: 11,
    advantage: "Batter Dominant",
    tactical_notes: "Samson thrives on express pace and true bounce; scores freely against back-of-length bowling.",
    win_probability_batter: 0.64
  },
  {
    batter_id: "wi_hope",
    batter_name: "Shai Hope",
    bowler_id: "ind_arshdeep",
    bowler_name: "Arshdeep Singh",
    balls: 36,
    runs: 38,
    dismissals: 3,
    strike_rate: 105.6,
    dot_pct: 50.0,
    boundaries_count: 4,
    advantage: "Bowler Dominant",
    tactical_notes: "Arshdeep's incoming new-ball angle exposes Hope's front-pad defense in overs 1-3.",
    win_probability_batter: 0.32
  },
  {
    batter_id: "ind_abhishek",
    batter_name: "Abhishek Sharma",
    bowler_id: "wi_motie",
    bowler_name: "Gudakesh Motie",
    balls: 30,
    runs: 54,
    dismissals: 1,
    strike_rate: 180.0,
    dot_pct: 26.0,
    boundaries_count: 8,
    advantage: "Batter Dominant",
    tactical_notes: "Abhishek steps out aggressively against left-arm orthodox, clearing mid-wicket easily.",
    win_probability_batter: 0.72
  },
  {
    batter_id: "wi_powell",
    batter_name: "Rovman Powell",
    bowler_id: "ind_axar",
    bowler_name: "Axar Patel",
    balls: 34,
    runs: 44,
    dismissals: 3,
    strike_rate: 129.4,
    dot_pct: 44.0,
    boundaries_count: 5,
    advantage: "Bowler Dominant",
    tactical_notes: "Axar fires arm balls into stumps at 98kph, preventing Powell from extending his arms.",
    win_probability_batter: 0.35
  }
];

export const OPTIMIZED_LINEUPS: Lineup[] = [
  {
    team_name: "Team 1: India Top-Order & Death Pace Crush",
    scenario_tag: "IND_TOP_ORDER_CRUSH",
    players: PLAYERS_DB.slice(0, 11),
    captain: PLAYERS_DB[0], // Abhishek
    vice_captain: PLAYERS_DB[5], // Arshdeep
    total_credits: 93.5,
    projected_points: 801.4,
    simulated_ceiling: 1736.5,
    total_ownership_sum: 564.0,
    differential_count: 3,
    tactical_rationale: "Abhishek tears through powerplay; Arshdeep mops up WI lower order at the death.",
    gl_rank_potential: "Elite Ceiling",
    uniqueness_score: 94
  },
  {
    team_name: "Team 2: West Indies Power-Hitting Upset",
    scenario_tag: "WI_POWER_UPSET",
    players: [PLAYERS_DB[1], PLAYERS_DB[0], PLAYERS_DB[3], PLAYERS_DB[6], PLAYERS_DB[7], PLAYERS_DB[8], PLAYERS_DB[9], PLAYERS_DB[10], PLAYERS_DB[11], PLAYERS_DB[12], PLAYERS_DB[13]],
    captain: PLAYERS_DB[1], // Samson
    vice_captain: PLAYERS_DB[7], // Hope
    total_credits: 93.0,
    projected_points: 738.2,
    simulated_ceiling: 1710.1,
    total_ownership_sum: 495.0,
    differential_count: 2,
    tactical_rationale: "Romario Shepherd delivers an all-round masterclass at death while Shai Hope anchors.",
    gl_rank_potential: "High Volatility",
    uniqueness_score: 88
  },
  {
    team_name: "Team 3: Express Pace & Yorker Carnage",
    scenario_tag: "EXPRESS_PACE_CARNIVAL",
    players: [PLAYERS_DB[0], PLAYERS_DB[1], PLAYERS_DB[4], PLAYERS_DB[5], PLAYERS_DB[6], PLAYERS_DB[7], PLAYERS_DB[8], PLAYERS_DB[10], PLAYERS_DB[11], PLAYERS_DB[12], PLAYERS_DB[13]],
    captain: PLAYERS_DB[6], // Mayank
    vice_captain: PLAYERS_DB[12], // Joseph
    total_credits: 94.5,
    projected_points: 791.5,
    simulated_ceiling: 1745.9,
    total_ownership_sum: 512.0,
    differential_count: 2,
    tactical_rationale: "155kph express pace rewards true bounce at Hyderabad. Mayank Yadav and Alzarri Joseph share 6+ wickets.",
    gl_rank_potential: "Rank #1 Leverage",
    uniqueness_score: 96
  },
  {
    team_name: "Team 4: Middle-Overs Spin Trap",
    scenario_tag: "MIDDLE_SPIN_CHOKE",
    players: [PLAYERS_DB[0], PLAYERS_DB[1], PLAYERS_DB[3], PLAYERS_DB[4], PLAYERS_DB[5], PLAYERS_DB[6], PLAYERS_DB[7], PLAYERS_DB[9], PLAYERS_DB[10], PLAYERS_DB[11], PLAYERS_DB[13]],
    captain: PLAYERS_DB[1], // Samson
    vice_captain: PLAYERS_DB[4], // Axar
    total_credits: 94.0,
    projected_points: 800.0,
    simulated_ceiling: 1786.5,
    total_ownership_sum: 538.0,
    differential_count: 3,
    tactical_rationale: "Dry surface in middle overs lets Kuldeep and Axar suffocate West Indies batting order.",
    gl_rank_potential: "High Ceiling",
    uniqueness_score: 91
  },
  {
    team_name: "Team 5: Sub-40% Differential Rank #1 Punt",
    scenario_tag: "ULTRA_DIFFERENTIAL_LEVERAGE",
    players: [PLAYERS_DB[0], PLAYERS_DB[1], PLAYERS_DB[2], PLAYERS_DB[3], PLAYERS_DB[5], PLAYERS_DB[6], PLAYERS_DB[7], PLAYERS_DB[9], PLAYERS_DB[10], PLAYERS_DB[11], PLAYERS_DB[12]],
    captain: PLAYERS_DB[3], // Tilak
    vice_captain: PLAYERS_DB[10], // Rutherford
    total_credits: 94.0,
    projected_points: 787.9,
    simulated_ceiling: 1735.1,
    total_ownership_sum: 462.0,
    differential_count: 4,
    tactical_rationale: "Fade mega-chalk openers; Tilak Varma and Sherfane Rutherford salvage innings with explosive boundaries.",
    gl_rank_potential: "Maximum Leverage",
    uniqueness_score: 99
  }
];

export const DATA_PROVIDERS: DataProviderTelemetry[] = [
  {
    id: "cricsheet",
    name: "Cricsheet Historical Database",
    status: "ONLINE",
    latency_ms: 12,
    records_indexed: 1243,
    last_sync: "Just now",
    best_use: "Free historical ball-by-ball T20/IPL archives and ML training",
    endpoint: "https://cricsheet.org/downloads/ipl_json.zip"
  },
  {
    id: "cricketdata",
    name: "CricketData / CricAPI",
    status: "ONLINE",
    latency_ms: 84,
    records_indexed: 540,
    last_sync: "1 min ago",
    best_use: "Live match discovery, verified playing 11, and basic fantasy points",
    endpoint: "https://api.cricapi.com/v1/cricScore"
  },
  {
    id: "sportmonks",
    name: "Sportmonks Cricket API v2.0",
    status: "ONLINE",
    latency_ms: 110,
    records_indexed: 820,
    last_sync: "2 mins ago",
    best_use: "Deep bowling/batting scorecards, player wagon wheels, and lineups",
    endpoint: "https://cricket.sportmonks.com/api/v2.0/livescores"
  },
  {
    id: "roanuz_match",
    name: "Roanuz Match API v5",
    status: "ONLINE",
    latency_ms: 68,
    records_indexed: 410,
    last_sync: "Live stream",
    best_use: "Real-time micro ball-by-ball telemetry, live pitch updates, toss events",
    endpoint: "https://api.sports.roanuz.com/v5/cricket/match/"
  },
  {
    id: "roanuz_fantasy",
    name: "Roanuz Fantasy API v5",
    status: "ONLINE",
    latency_ms: 72,
    records_indexed: 410,
    last_sync: "Live stream",
    best_use: "Real-time official fantasy scoring & dynamic leaderboard tracking",
    endpoint: "https://api.sports.roanuz.com/v5/cricket/fantasy-match-points/"
  }
];

export const currentLiveMatch = CURRENT_MATCH;
export const mockPlayers = PLAYERS_DB;
export const stadiumVenues = VENUES;
export const mockTrajectories = BALL_TRAJECTORIES;
export const mockBattles = HEAD_TO_HEAD_BATTLES;
export const mockLineups = OPTIMIZED_LINEUPS;
export const mockProviders = DATA_PROVIDERS;
