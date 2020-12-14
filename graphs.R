library("ggplot2")
library("scales")

df_data = data.frame(NbrSchedules = c(26, 55, 109, 216, 321),
                     UserTime = c(0.34, 2.59, 28.02, 206.65, 1283.44),
                     DetTime = c(0.10, 0.88, 5.82, 27.81, 47.12),
                     Bools = c(9600, 44160, 167400, 669600, 1506600),
                     Branches = c(25497, 117783, 260646, 1522395, 3333765),
                     Props = c(233703, 2355177, 7455604, 8087257, 8819655))

df = data.frame(DailyMtgs = c('1 Max', '2 Max', '3 Max', '4 Max'),
                UserTime = c(25.16, 28.96, 42.7, 52.74),
                MtgsMatch = c(184, 278, 278, 278))

# Line Graph
p = ggplot(df_data, aes_string("NbrSchedules", "DetTime"))
p = p + geom_point()
p = p + geom_line(linetype = "solid", color = "red")
p = p + labs(x = "Number of Schedules",
             y = "Time (seconds)")
p = p + theme_minimal()
p = p + scale_x_continuous(breaks = seq(0, 400, by = 100), limits = c(0,400))
p = p + scale_y_continuous(breaks = seq(0, 50, by = 5), limits = c(0,50))
p = p + ggtitle("Solver Runtime: Deterministic Time") + theme_classic() + theme(plot.title = element_text(hjust = 0.5))

# Bar Graph
g = ggplot(data=df_data, aes(x=NbrSchedules, y=Props))
g = g + xlab("Number of Schedules")
g = g + ylab("Number of Propagations")
g = g + geom_bar(stat="identity", fill="forestgreen", color="black")
g = g + scale_x_continuous(breaks = seq(0, 350, by = 50), limits = c(0,350))
g = g + scale_y_continuous(breaks = seq(0, 9000000, by = 500000), limits = c(0,9000000), expand = c(0, 0), labels = comma)
g = g + coord_cartesian(xlim=c(0,350), ylim=c(1,9000000))
g = g + ggtitle("Scaling the Solver:\nSchedules & Propagations") + theme_classic() + theme(plot.title = element_text(hjust = 0.5))

# Bar Graph with Group
b = ggplot(data=df, aes(x=UserTime, y=MtgsMatch, fill=DailyMtgs))
b = b + geom_bar(stat="identity", color="black") + theme_classic() + coord_flip()
b = b + xlab("User Time (seconds)")
b = b + ylab("Total Meetings Matched")
b = b + labs(fill="Max Daily Meetings")
b = b + theme(legend.position="bottom")
b = b + scale_x_continuous(breaks = seq(0, 60, by = 10), limits = c(0,60), expand = c(0, 0))
b = b + scale_y_continuous(breaks = seq(0, 300, by = 50), limits = c(0,300), expand = c(0, 0))
b = b + ggtitle("Total Meetings Matched vs\nMax Interpreter Meetings per Day") + theme_classic() + theme(plot.title = element_text(hjust = 0.5))
b = b + geom_hline(yintercept=279, linetype="dashed", color="red")
b = b + geom_text(aes(0,279,label="Total Meeting Requests", vjust=-20, hjust=1.05), size=3, color="red")             

