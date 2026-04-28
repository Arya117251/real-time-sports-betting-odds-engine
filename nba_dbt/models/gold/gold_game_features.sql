{#
  gold_game_features — feature table for the NBA win-prediction model.

  Selects the exact set of columns consumed by scripts/train_model.py and
  adds a binary target column:
    home_win = 1  when home_team won  (score_diff > 0)
    home_win = 0  when away_team won  (score_diff <= 0)

  Source  : nba_silver.silver_games  (already cast, filtered, and deduped)
  Target  : nba_gold.gold_game_features
  Materializaton: table (full refresh each run)
#}

with silver as (

    select * from {{ ref('silver_games') }}

)

select
    game_id,
    date,
    home_team,
    away_team,

    -- season record
    home_wins,
    away_wins,
    home_losses,
    away_losses,

    -- win-percentage features
    season_home_win_pct,
    season_away_win_pct,

    -- rest / scheduling features
    home_rest_days,
    away_rest_days,
    home_is_back_to_back,
    away_is_back_to_back,

    -- raw outcome
    score_diff,

    -- binary target: 1 = home win, 0 = away win
    cast(score_diff > 0 as int64) as home_win

from silver
