DO
$$
DECLARE
  to_table varchar := 'fq_filtered_trajectory'; -- Table name
  traj_segment varchar := 'week'; -- Trajectory segmentation method: day, week, month
  min_checkin_count integer := 10; -- Minimum number of check-ins per trajectory
  min_traj_count integer := 10; -- Minimum number of trajectories per user
  row_count integer;
  check_point1 integer;
  check_point2 integer;
  check_point3 integer;
  small_traj_count integer;
  user_id integer;
  checkin_id integer;
  cur_date timestamp;
  last_segment integer;
  last_tid integer := 0;
  generic_count integer;
BEGIN

-- Creates the new table
EXECUTE 'CREATE TABLE ' || to_table || ' AS (SELECT * FROM fq_checkin);';
EXECUTE 'SELECT COUNT(*) FROM ' || to_table INTO row_count;
raise notice 'Table % created with % rows!', to_table, row_count;

-- Creates temporary table
EXECUTE 'CREATE TABLE temp_trajectory_filtering AS (SELECT * FROM ' || to_table || ')';
raise notice 'Temporary table temp_trajectory_filtering created!';

-- Creates column for trajectory segmentation
EXECUTE 'ALTER TABLE ' || to_table || ' ADD COLUMN wt_tid integer';
raise notice 'Column wt_tid created on table %!', to_table;

-- Segments trajectories
FOR user_id IN (SELECT DISTINCT(anonymized_user_id) FROM temp_trajectory_filtering ORDER BY anonymized_user_id ASC) LOOP
	last_segment := NULL;
	
	FOR checkin_id, cur_date IN (SELECT id, date_time FROM temp_trajectory_filtering WHERE anonymized_user_id = user_id ORDER BY date_time ASC) LOOP
		EXECUTE 'SELECT EXTRACT(' || traj_segment || ' FROM timestamp' || E'\'' || cur_date || E'\'' ||
			') FROM temp_trajectory_filtering LIMIT 1' INTO generic_count;
			
		IF (generic_count = last_segment) THEN
			EXECUTE 'UPDATE ' || to_table || ' SET wt_tid = ' || last_tid || ' WHERE id = ' || checkin_id;
		ELSE
			last_segment := generic_count;
			last_tid := last_tid + 1;
			EXECUTE 'UPDATE ' || to_table || ' SET wt_tid = ' || last_tid || ' WHERE id = ' || checkin_id;
		END IF;
	END LOOP;
	
	raise notice 'User % trajectory segmented!', user_id;
END LOOP;
raise notice '% trajectories created in the segmentation process!', last_tid;

-- Drops temporary table
EXECUTE 'DROP TABLE temp_trajectory_filtering';
raise notice 'Temporary table temp_trajectory_filtering dropped!';

-- Removes small trajectories
raise notice 'Removing trajectories with fewer than % check-ins!', min_checkin_count;
EXECUTE 'DELETE FROM ' || to_table || ' WHERE wt_tid IN (SELECT wt_tid FROM ' || to_table ||
	' GROUP BY wt_tid HAVING COUNT(*) < ' || min_checkin_count || ' ORDER BY wt_tid)';
EXECUTE 'SELECT COUNT(DISTINCT(wt_tid)) FROM ' || to_table INTO small_traj_count;
raise notice '% trajectories with fewer than % check-ins removed!', (last_tid - small_traj_count), min_checkin_count;

-- Removes users with too few trajectories
raise notice 'Removing users who have fewer than % trajectories!', min_traj_count;
FOR user_id IN (SELECT id FROM fq_anonymized_user ORDER BY id ASC) LOOP	
	EXECUTE 'DELETE FROM ' || to_table || ' WHERE
		(SELECT COUNT(DISTINCT(wt_tid)) < ' || min_traj_count || ' FROM ' || to_table || ' WHERE anonymized_user_id = ' || user_id || ') 
		AND anonymized_user_id = ' || user_id ;
END LOOP;
EXECUTE 'SELECT COUNT(DISTINCT(wt_tid)) FROM ' || to_table INTO generic_count;
raise notice '% trajectories removed of users who have fewer than % trajectories!', (small_traj_count - generic_count), min_traj_count;

EXECUTE 'SELECT COUNT(DISTINCT(anonymized_user_id)) FROM ' || to_table INTO generic_count;
raise notice 'Database has % different users!', generic_count;

EXECUTE 'SELECT COUNT(DISTINCT(wt_tid)) FROM ' || to_table INTO generic_count;
raise notice 'Database has % trajectories!', generic_count;

EXECUTE 'SELECT COUNT(*) FROM ' || to_table INTO generic_count;
raise notice 'Database has % check-ins!', generic_count;

END
$$
