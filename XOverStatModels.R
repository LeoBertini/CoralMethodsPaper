library(readxl)
library(ggplot2)
# read data
data <-read_xlsx('/Users/leonardobertini/PycharmProjects/CoralXOverStatAnalyses/Consolidated_file_XoverResults.xlsx',col_names=TRUE)
DF <- data.frame(data)

Type1Data=DF[DF$CrossType1to4 == 'Type1',]

# Box plot by group
bp <- ggplot(DF, aes(x = PhantomType , y = WeightOffset, fill=CrossType1to4)) +
  geom_boxplot()

# Split in vertical direction
bp + facet_grid(ColonyNickname~ .)
