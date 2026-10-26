export type RoleType = "WK" | "BAT" | "AR" | "BOWL";
export type BattingStyle = "RHB" | "LHB";
export type BowlingStyle = "Pace" | "Fast" | "Fast-Medium" | "Off-Spin" | "Leg-Spin" | "Left-Arm Orthodox" | "Chinaman";

export interface PlayerStats {
  matches: number;
  runs: number;
  balls_faced: number;
  strike_rate: number;
  batting_avg: number;
  wickets: number;
  overs_bowled: number;
  economy: number;
  bowling_sr: number;
  dot_ball_pct: number;
  boundary_pct: number;
  recent_scores: number[];
  recent_wickets: number[];
  recent_fantasy_pts: number[];
  avg_fantasy_pts: number;
  ceiling_pts: number;
  floor_pts: number;
}

export interface Player {
  id: string;
  name: string;
  team: string; // "IND" | "WI" | "CSK" | "MI" etc.
  role: RoleType;
  credits: number;
  batting_style: BattingStyle;
  bowling_style?: string;
  batting_order: number;
  expected_overs: number;
  projected_ownership: number;
  projected_points: number;
  ceiling_score: number;
  floor_score: number;
  stats: PlayerStats;
  is_confirmed_xi: boolean;
  differential_tag?: string;
}

export type CameraPreset = 
  | "broadcast" 
  | "top_down" 
  | "bowler_view" 
  | "batter_view" 
  | "pitch_heatmap" 
  | "stadium_orbit";

export interface BallTrajectory {
  id: string;
  over: number;
  ball: number;
  bowler: string;
  batter: string;
  speed_kmh: number;
  length: "Yorker" | "Full" | "Good Length" | "Short";
  line: "Outside Off" | "Stumps" | "Down Leg";
  pitch_x: number; // -1.5m to 1.5m
  pitch_y: number; // 0 to 20m from bowling crease
  bounce_height_m: number;
  outcome: "Dot" | "1 Run" | "2 Runs" | "Boundary 4" | "Six" | "Wicket";
  wicket_type?: string;
  phase: "Powerplay" | "Middle" | "Death";
}

export interface StadiumVenue {
  id: string;
  name: string;
  city: string;
  soil_type: string;
  avg_first_innings: number;
  avg_second_innings: number;
  chasing_win_pct: number;
  pace_wicket_pct: number;
  spin_wicket_pct: number;
  dew_factor: number;
  pitch_nature: string;
  boundaries: {
    square_leg: number;
    midwicket: number;
    long_on: number;
    straight: number;
    long_off: number;
    cover: number;
    point: number;
  };
}

export interface HeadToHeadBattle {
  batter_id: string;
  batter_name: string;
  bowler_id: string;
  bowler_name: string;
  balls: number;
  runs: number;
  dismissals: number;
  strike_rate: number;
  dot_pct: number;
  boundaries_count: number;
  advantage: "Batter Dominant" | "Bowler Dominant" | "Competitive Balance";
  tactical_notes: string;
  win_probability_batter: number | null;
}

export interface Lineup {
  team_name: string;
  scenario_tag: string;
  players: Player[];
  captain: Player;
  vice_captain: Player;
  total_credits: number;
  projected_points: number;
  simulated_ceiling: number;
  total_ownership_sum: number;
  differential_count: number;
  tactical_rationale: string;
  gl_rank_potential: string;
  uniqueness_score?: number | null;
  projected_field_duplicates?: number;
  credits_left?: number;
  p_top_0_1_pct?: number;
  csp?: number;
  mnc_summary?: string;
  cvc_combo_type?: string;
}

export interface MatchInfo {
  id: string;
  name: string;
  format: string;
  status: string;
  venue: StadiumVenue;
  teams: {
    home: { name: string; code: string; score?: string; overs?: string };
    away: { name: string; code: string; score?: string; overs?: string };
  };
  toss: {
    winner: string;
    choice: "bat" | "bowl";
    statement: string;
  };
  current_crr: number;
  projected_total: number;
  chasing_win_prob: number;
}

export interface DataProviderTelemetry {
  id: string;
  name: string;
  status: "ONLINE" | "ONLINE / AUTHENTICATED_LIVE" | "STANDBY" | "SIMULATED_FALLBACK" | "LOCAL_ARCHIVE_READY" | "CONFIGURED_UNVERIFIED";
  latency_ms: number | null;
  records_indexed: number | null;
  last_sync: string;
  best_use: string;
  endpoint: string;
}

export type WorkspaceTab = 
  | "unique-engine"
  | "command-center"
  | "match-studio"
  | "player-intel"
  | "battle-arena"
  | "field-strategy"
  | "ball-by-ball"
  | "pitch-lab"
  | "scenario-lab"
  | "game-plan"
  | "series-intelligence"
  | "fantasy-lab"
  | "ai-analyst"
  | "providers";

export interface FielderPosition {
  id: string;
  name: string;
  x: number; // percentage on field -50 to 50
  y: number; // percentage on field -50 to 50
  isInsideCircle: boolean;
  isCatching: boolean;
}

export interface FieldSettingPreset {
  id: string;
  name: string;
  category: "Powerplay" | "Middle" | "Death" | "Wicket-Taking";
  description: string;
  bowlingStyle: string;
  strikerHand: BattingStyle;
  fielders: FielderPosition[];
}

export interface DeliveryRecord {
  match_id: string;
  innings: number;
  over: number;
  ball: number;
  batter: string;
  bowler: string;
  non_striker: string;
  runs_batter: number;
  runs_extras: number;
  runs_total: number;
  is_wicket: boolean;
  wicket_type?: string;
  player_dismissed?: string;
  phase: "Powerplay" | "Middle" | "Death";
  shot_zone?: string;
  speed_kmh?: number;
}

export type TacticalObjective = "Wicket Strike" | "Run Containment" | "Matchup Strangle" | "Death Yorker Lock";

export interface OverPlan {
  overNumber: number; // 1 to 20
  phase: "Powerplay" | "Middle" | "Death";
  assignedBowlerId: string;
  assignedBowlerName: string;
  alternativeBowlerId?: string;
  alternativeBowlerName?: string;
  expectedBatters: string[];
  objective: TacticalObjective;
  targetLineLength: string;
  fieldPresetId: string;
  matchupRationale: string;
  riskRating: "Low" | "Moderate" | "High";
  confidencePct: number;
}

