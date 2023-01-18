library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)
# read data
datacoral <-read_xlsx('/Users/leonardobertini/PycharmProjects/CoralXOverStatAnalyses/Consolidated_file_XoverResults.xlsx',col_names=TRUE)
DF <- data.frame(datacoral)


# Box plot by group (check effects of phantom type on weight offset)
bp <- ggplot(DF, aes(x = PhantomType , y = WeightOffset, fill=CrossType1to4)) +
  geom_boxplot()
print(bp)


#filter only expanded phantom
GoodPhantomData=DF[DF$PhantomType == 'Expanded',]

# Box plot by group (check effects of phantom type on weight offset)
bp <- ggplot(GoodPhantomData, aes(x = CrossType1to4 , y = WeightOffset)) +
  geom_boxplot()
print(bp)


#exploring correlations
result_corr<-cor(DF[, unlist(lapply(DF, is.numeric))])    
library(corrplot)
corrplot(result_corr, type = "upper", order = "hclust", 
         tl.col = "black", tl.srt = 45)
#modelling weight offset effects

#standardizing numeric variables
datacoralMOD <- GoodPhantomData %>% mutate_at(c('Volume_estimate','WeightOffset','VirtualDensity','RealAreaOverVol','RealWeight','SurfaceArea','ShapeVA3d','Breadth3d','MeanRugosity','MeanShapeAP','MeanSymmetry','RealColonyDensity'), ~(scale(.) %>% as.vector))


coral.glmm1 <- lmer(WeightOffset ~ RealAreaOverVol + SurfaceArea + MeanSymmetry + ShapeVA3d + Breadth3d + MeanRugosity + MeanShapeAP + RealColonyDensity + CrossType1to4  +
                      (1|ColonyNickname) + (1|CrossType1to4), data=DF)
summary(coral.glmm1)
print(coral.glmm1, corr=F)


