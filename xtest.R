#install.packages("XML")
#install.packages("plotKML")
#install.packages("maptools")
#install.packages("gpsbabel")
cat("\014")
library(XML)


file = "Rik_Veenboer_2015-11-10_17-21-59.gpx"
file = "test.gpx"

data = xmlParse(file)


#y=as.data.frame(sapply(xml$trk$trkseg["trkpt"], rbind))
bla=head(xml$trk$trkseg)



result=data.frame(
  elevation = unlist(lapply(bla, '[', c('ele'))),
  time =  as.numeric(as.POSIXct(unlist(lapply(bla, '[', c('time'))), format="%Y-%m-%dT%H:%M:%S")))
  
  
latlon = t(matrix(as.numeric(unlist(lapply(bla, '[', c('.attrs')))), 2))
xx=as.data.frame(t(matrix(as.numeric(unlist(lapply(bla, '[', c('.attrs')))), 2)))
colnames(xx) = c("lat", "lon")


xxx=merge(result, xx)
