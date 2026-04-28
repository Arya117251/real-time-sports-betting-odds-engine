{# Silver model: casts types, filters bad rows, deduplicates on game_id #}


with source as (

    select * from {{ source('nba_bronze', 'raw_games') }}

),

casted as (

    select
        game_id,
        parse_date('%Y-%m-%d', date)            as date,
        home_team,
        away_team,
        cast(home_score            as int64)    as home_score,
        cast(away_score            as int64)    as away_score,
        status,
        cast(home_wins             as int64)    as home_wins,
        cast(away_wins             as int64)    as away_wins,
        cast(home_losses           as int64)    as home_losses,
        cast(away_losses           as int64)    as away_losses,
        cast(season_home_win_pct   as float64)  as season_home_win_pct,
        cast(season_away_win_pct   as float64)  as season_away_win_pct,
        cast(home_rest_days        as int64)    as home_rest_days,
        cast(away_rest_days        as int64)    as away_rest_days,
        cast(home_is_back_to_back  as int64)    as home_is_back_to_back,
        cast(away_is_back_to_back  as int64)    as away_is_back_to_back,
        cast(score_diff            as int64)    as score_diff

    from source

),

filtered as (

    -- Exclude rows where both scores are 0; these represent games that have
    -- not yet been played or have a data-quality issue.
    select *
    from casted
    where not (home_score = 0 and away_score = 0)

),

deduped as (

    select
        *,
        row_number() over (
            partition by game_id
            order by date
        ) as rn

    from filtered

)

select
    game_id,
    date,
    home_team,
    away_team,
    home_score,
    away_score,
    status,
    home_wins,
    away_wins,
    home_losses,
    away_losses,
    season_home_win_pct,
    season_away_win_pct,
    home_rest_days,
    away_rest_days,
    home_is_back_to_back,
    away_is_back_to_back,
    score_diff

from deduped
where rn = 1
