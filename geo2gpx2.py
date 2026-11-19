import gpxpy
import gpxpy.gpx

gpx = gpxpy.gpx.GPX()

# Create track (<trk>)
gpx_track = gpxpy.gpx.GPXTrack(name="My Track")
gpx.tracks.append(gpx_track)

# Create track segment (<trkseg>)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Add track points (<trkpt>) to the segment
gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(52.485, 4.815))
gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(52.486, 4.817))

# Write GPX XML to file
with open("output.gpx", "w", encoding="utf-8") as f:
    f.write(gpx.to_xml())
key = input("Wait")
