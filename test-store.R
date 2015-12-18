#' ## Storing R Objects in a SQLite Database

#' Two packages we are using. The first is the ```RSQLite``` which will be used to create and manage an in-memory SQLite database. The second is ```igraph``` which I will use to create and visualize a random network. Some of the work I do is on network simulation. I often don't know the metrics I need from a simulated network when it's created, so I want to be able to store the networks that are created so that I can go back later and analyze them.
library(RSQLite)
library(igraph)

#' Create a database in memory.
con <- dbConnect(SQLite(), "test.db")

#' The table has two columns, an *id* column and a column called *graph* which is a **blob** type. This type just stores binary data.
dbGetQuery(con, 'create table if not exists graphs 
                 (_id integer primary key autoincrement, 
                  graph blob)')

#' Create a bunch of random graphs [Watts-Strogatz graphs](http://en.wikipedia.org/wiki/Watts_and_Strogatz_model).
gs <- list()
for(i in 1:10)
  gs[[i]] <- watts.strogatz.game(1, 100, 5, 0.05)

#' Here's the meaty part. The *serialize* function will take an object and convert it to a raw vector of bytes. Then the *I* function forces the data.frame to store the whole vector as an entry in the data.frame.
df <- data.frame(a = 1:10, 
                 g = I(lapply(gs, function(x) { serialize(x, NULL)})))

#' Now insert the data into the table.
dbGetPreparedQuery(con, 'insert into graphs (graph) values (:g)', 
                   bind.data=df)

#' Try getting the data out.
df2 <- dbGetQuery(con, "select * from graphs")

#' Convert it back to a list of graphs.
gs2 <- lapply(df2$graph, 'unserialize')

#' Compulsory picture of the network.
g <- gs2[[1]]
V(g)$size <- log(betweenness(g))
plot(g, vertex.label = NA)

dbDisconnect(con)