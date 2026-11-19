import gpxpy
import gpxpy.gpx

gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack(name="My Track")
gpx.tracks.append(gpx_track)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)
gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(52.485, 4.815))
gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(52.486, 4.817))
with open("output.gpx", "w", encoding="utf-8") as f:
    f.write(gpx.to_xml())
key = input("Wait")
