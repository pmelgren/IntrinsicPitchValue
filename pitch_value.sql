with pre_pitches as (
	select 
		* 
		,max(pitch_number) over(partition by game_pk, at_bat_number) max_pitch_no_in_ab
	from 
		tm.pitch pit
		inner join tm.play play
			on play.play_id = pit.play_id
	where
		date_part('year',pitch_date) = 2019
				 
), pitches as (
	select
		p1.pitch_id
		,p1.bat_side
		,p1.pitch_side
		,p1.pitch_type
		,p1.balls
		,p1.strikes
		,p2.balls post_balls
		,p2.strikes post_strikes
		,p1.pitch_result
		,p1.play_result
		,p1.game_pk 
		,p1.at_bat_number
		,p1.pitch_number
		,p1.max_pitch_no_in_ab
	from
		pre_pitches p1
		left join pre_pitches p2
			on p2.game_pk = p1.game_pk
			and p2.at_bat_number = p1.at_bat_number
			and p2.pitch_number = p1.pitch_number+1
)

select
	pitch_type
	,bat_side
	,pitch_side
	,p.balls
	,p.strikes
	,velocity
	,spin_rate
	,break_x
	,break_z
	,release_x
	,release_z
	,extension
	,plate_x
	,plate_z
	,sz_top
	,sz_bot
	,vx50
	,vy50
	,vz50
	,ax50
	,ay50
	,az50
	,case when pitch_result in ('ball','called_strike','blocked_ball','hit_by_pitch') then 0 else 1 end swing
	,case when pitch_result in ('swinging_strike','swinging_strike_blocked') then 0
		when pitch_result in ('foul','foul_tip','hit_into_play','hit_into_play_score','hit_into_play_no_out') then 1
		else null end contact
	,case when pitch_result in ('foul','foul_tip') then 0 
		when pitch_result in ('hit_into_play','hit_into_play_score','hit_into_play_no_out') then 1
		else null end fair
	,case when pitch_result in ('hit_into_play','hit_into_play_score','hit_into_play_no_out') 
			then rv.run_value else post_ct.run_value end - ct.run_value pitch_run_value
from
	pitches p
	inner join tm.pitch_measures pm
		on pm.pitch_id = p.pitch_id
	inner join tm.pitch_count_run_values ct
		on ct.balls = p.balls
		and ct.strikes = p.strikes
	left join tm.pitch_count_run_values post_ct
		on post_ct.balls = p.post_balls
		and post_ct.strikes = p.post_strikes
	left join tm.play_result_run_value rv
		on rv.play_result = p.play_result
