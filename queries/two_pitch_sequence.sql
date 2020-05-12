with pitches as (
	select
		game_pk
		,at_bat_number
		,pitch_number
		,pitch_type
		,bat_side
		,pitch_side
		,balls
		,strikes
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
	from
		tm.pitch pit
		inner join tm.play play
			on play.play_id = pit.play_id
		inner join tm.pitch_measures pm
			on pm.pitch_id = pit.pitch_id
)
select
	p2.bat_side
	,p2.pitch_side
	,p2.pitch_type
	,p2.pitch_number
	,p1.pitch_type prev_pitch_type
	,p1.balls prev_balls
	,p1.strikes prev_strikes
	,p1.velocity prev_velocity
	,p1.spin_rate prev_spin_rate
	,p1.break_x prev_break_x
	,p1.break_z prev_break_z
	,p1.release_x prev_release_x
	,p1.release_z prev_release_z
	,p1.extension prev_extension
	,p1.plate_x prev_plate_x
	,p1.plate_z prev_plate_z
	,p1.sz_top prev_sz_top
	,p1.sz_bot prev_sz_bot
	,p1.vx50 prev_vx50
	,p1.vy50 prev_vy50
	,p1.vz50 prev_vz50
	,p1.ax50 prev_ax50
	,p1.ay50 prev_ay50
	,p1.az50 prev_az50	
	,p2.balls
	,p2.strikes
	,p2.velocity
	,p2.spin_rate
	,p2.break_x
	,p2.break_z
	,p2.release_x
	,p2.release_z
	,p2.extension
	,p2.plate_x
	,p2.plate_z
	,p2.sz_top
	,p2.sz_bot
	,p2.vx50
	,p2.vy50
	,p2.vz50
	,p2.ax50
	,p2.ay50
	,p2.az50
	,p2.swing
	,p2.contact
	,p2.fair
from pitches p2
	left join pitches p1
		on p2.game_pk = p1.game_pk
		and p2.at_bat_number = p1.at_bat_number
		and p2.pitch_number = p1.pitch_number+1
