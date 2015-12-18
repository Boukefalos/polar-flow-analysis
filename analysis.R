# Calculate distances (in metres) using the function pointDistance from the 'raster' package.
library(raster)

# Shift vectors for lat and lon so that each row also contains the next position.
geodf$lat.p1 <- shift.vec(geodf$lat, -1)
geodf$lon.p1 <- shift.vec(geodf$lon, -1)

# Parameter 'lonlat' has to be TRUE!
geodf$dist.to.prev <- apply(geodf, 1, FUN = function (row) {
  pointDistance(c(as.numeric(row["lat.p1"]),
                  as.numeric(row["lon.p1"])),
                c(as.numeric(row["lat"]), as.numeric(row["lon"])),
                lonlat = T)
})

# Transform the column 'time' so that R knows how to interpret it.
geodf$time <- strptime(geodf$time, format = "%Y-%m-%dT%H:%M:%OS")

# Shift the time vector, too.
geodf$time.p1 <- shift.vec(geodf$time, -1)

# Calculate the number of seconds between two positions.
geodf$time.diff.to.prev <- as.numeric(difftime(geodf$time.p1, geodf$time))

# Calculate metres per seconds, kilometres per hour and two LOWESS smoothers to get rid of some noise.
geodf$speed.m.per.sec <- geodf$dist.to.prev / geodf$time.diff.to.prev
geodf$speed.km.per.h <- geodf$speed.m.per.sec * 3.6
geodf$speed.km.per.h <- ifelse(is.na(geodf$speed.km.per.h), 0, geodf$speed.km.per.h)
geodf$speed.km.per.h <- ifelse(geodf$speed.km.per.h > 40, 0, geodf$speed.km.per.h)
geodf$lowess.speed <- lowess(geodf$speed.km.per.h, f = 0.01)$y
geodf$lowess.ele <- lowess(geodf$ele, f = 0.02)$y

# Plot elevations and smoother
plot(geodf$ele, type = "l", bty = "n", xaxt = "n", ylab = "Elevatio", xlab = "", col = "grey40")
lines(geodf$lowess.ele, col = "red", lwd = 3)
legend(x="bottomright", legend = c("GPS elevation", "LOWESS elevation"),
       col = c("grey40", "red"), lwd = c(1,3), bty = "n")


# Plot speeds and smoother
plot(geodf$speed.km.per.h, type = "l", bty = "n", xaxt = "n", ylab = "Speed (km/h)", xlab = "",
     col = "grey40")
lines(geodf$lowess.speed, col = "blue", lwd = 3)
legend(x="bottom", legend = c("GPS speed", "LOWESS speed"),
       col = c("grey40", "blue"), lwd = c(1,3), bty = "n")
abline(h = mean(geodf$speed.km.per.h), lty = 2, col = "blue")

# Plot the track without any map, the shape of the track is already visible.
plot(rev(geodf$lon), rev(geodf$lat), type = "l", col = "red", lwd = 3, bty = "n", ylab = "Latitude", xlab = "Longitude")
