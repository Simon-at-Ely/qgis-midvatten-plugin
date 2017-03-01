# -*- coding: utf-8 -*- This line is just for your information, the python plugin will not use the first line

#CREATE TRIGGER IF NOT EXISTS 'after_insert_obs_points_geom_fr_coords' AFTER INSERT ON obs_points WHEN (0 < (select count() from obs_points where ((NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL)))) BEGIN UPDATE obs_points SET  geometry = MakePoint(NEW.east, NEW.north, (select srid from geometry_columns where f_table_name = 'obs_points')) WHERE (NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL) AND (NEW.obsid = obsid); END;
#Trigger for after_insert_obs_points_geom_fr_coords
CREATE FUNCTION after_insert_obs_points_geom_fr_coords()
  RETURNS trigger AS
$BODY$
BEGIN
  UPDATE obs_points SET geometry = MakePoint(NEW.east, NEW.north, (select srid from geometry_columns where f_table_name = 'obs_points'))
  WHERE (NEW.east is not null) AND (NEW.north is not null) AND (NEW.geometry IS NULL) AND (NEW.obsid = obsid);
  RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER trigger_after_insert_obs_points_geom_fr_coords
  AFTER INSERT
  ON obs_points
  FOR EACH ROW
  EXECUTE PROCEDURE after_insert_obs_points_geom_fr_coords();
#------------------------------------------------------------------------------

#CREATE TRIGGER IF NOT EXISTS 'after_insert_obs_points_coords_fr_geom' AFTER INSERT ON obs_points WHEN (0 < (select count() from obs_points where ((NEW.east is null) AND (NEW.north is null) AND (NEW.geometry is not NULL)))) BEGIN UPDATE obs_points SET  east = X(geometry), north = Y(geometry) WHERE (NEW.east is null) AND (NEW.north is null) AND (NEW.geometry is not NULL) AND (NEW.obsid = obsid); END;
#CREATE TRIGGER IF NOT EXISTS 'after_update_obs_points_geom_fr_coords' AFTER UPDATE ON obs_points WHEN (0 < (select count() from obs_points where ((NEW.east != OLD.east) OR (NEW.north != OLD.north)) OR (NEW.north IS NOT NULL AND OLD.north IS NULL) OR (NEW.east IS NOT NULL AND OLD.east IS NULL)) ) BEGIN UPDATE obs_points SET geometry = MakePoint(NEW.east, NEW.north, (select srid from geometry_columns where f_table_name = 'obs_points')) WHERE ((NEW.east != OLD.east) OR (NEW.north != OLD.north) OR (NEW.north IS NOT NULL AND OLD.north IS NULL) OR (NEW.east IS NOT NULL AND OLD.east IS NULL)) AND (NEW.obsid = obsid) AND (NEW.east is not null) AND (NEW.north is not null); END;
#CREATE TRIGGER IF NOT EXISTS 'after_update_obs_points_coords_fr_geom' AFTER UPDATE ON obs_points WHEN (0 < (select count() from obs_points where NEW.geometry != OLD.geometry) ) BEGIN UPDATE obs_points SET east = X(geometry), north = Y(geometry) WHERE (NEW.geometry != OLD.geometry) AND (NEW.obsid = obsid); END;