library(XML)

args = commandArgs(trailingOnly = TRUE)
datadir = 'data'
session = args[1]
filename = paste(datadir, '/', session, '.gpx', sep = '')
print(filename)

shift.vec <- function (vec, shift) {
  if(length(vec) <= abs(shift)) {
    rep(NA ,length(vec))
  }else{
    if (shift >= 0) {
      c(rep(NA, shift), vec[1:(length(vec)-shift)]) }
    else {
      c(vec[(abs(shift)+1):length(vec)], rep(NA, abs(shift))) } } }

pfile <- htmlTreeParse("data/Rik_Veenboer_2015-11-10_17-21-59.gpx", useInternalNodes = T)

# Get all elevations, times and coordinates via the respective xpath
elevations <- as.numeric(xpathSApply(pfile, path = "//trkpt/ele", xmlValue))
times = xpathSApply(pfile, path = "//trkpt/time", xmlValue)
coords <- xpathSApply(pfile, path = "//trkpt", xmlAttrs)

# Extract latitude and longitude from the coordinates
lats <- as.numeric(coords["lat",])
lons <- as.numeric(coords["lon",])

# Put everything in a dataframe and get rid of old variables
geodf <- data.frame(lat = lats, lon = lons, ele = elevations, time = times)
rm(list=c("elevations", "lats", "lons", "pfile", "times", "coords"))

# Output head of frame
print(head(geodf))