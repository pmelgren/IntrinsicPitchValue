select 
	plate_x
	,plate_z
	,balls
	,strikes
	,bat_side
	,case when ball_strike = 'S' then 1.0 else 0.0 end S
from
	tm.pitch pit
	inner join tm.pitch_measures pm
		on pm.pitch_id = pit.pitch_id
	inner join tm.play play
		on play.play_id = pit.play_id
where 
	pitch_result in ('ball','called_strike')