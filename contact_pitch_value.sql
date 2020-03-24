select 
	pitch_type
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
	,play.play_result 
	,run_value
	,if_alignment
	,of_alignment
from 
	tm.play play
	inner join tm.pitch pit
		on pit.play_id = play.play_id
	inner join tm.pitch_measures pm
		on pm.pitch_id = pit.pitch_id
	inner join tm.play_result_run_value prrv
		on prrv.play_result = play.play_result
	inner join tm.play_defense def
		on def.play_id = play.play_id
where 
	pitch_result in ('hit_into_play','hit_into_play_score','hit_into_play_no_out') 