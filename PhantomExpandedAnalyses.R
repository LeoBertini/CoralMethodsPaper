library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)

# read data
datacoral <-read_xlsx('/Users/leonardobertini/RProjects/CoralMethodsPaper/ConsolidadedResultsPhantomExpanded.xlsx',col_names=TRUE)
DF <- data.frame(datacoral)
DF$Equipment = as.factor(DF$Equipment)

#exploratory figure
ggplot(DF, aes(y =RealColonyDensity, x = VirtualDensity, fill=Equipment, color=Equipment)) + 
  geom_point() + 
  geom_smooth(method = lm, aes(fill=Equipment))


#filtering
DF$PhantomType = as.factor(DF$PhantomType)
DF$ColonyNickname = as.factor(DF$ColonyNickname)
GoodPhantomData=DF[(DF$PhantomType == 'Expanded'),]

#####NEXT PART
#modelling weight offset effects
#First we standardize numeric variables
datacoralMOD <- GoodPhantomData %>% mutate_at(c('Volume_estimate','WeightOffset','VirtualDensity','RealAreaOverVol','RealWeight','SurfaceArea','ShapeVA3d','Breadth3d','MeanRugosity','MeanShapeAP','MeanSymmetry','RealColonyDensity'), ~(scale(.) %>% as.vector))


DF2 <- DF %>% mutate_at(c('Volume_estimate','WeightOffset','VirtualDensity','RealAreaOverVol','RealWeight','SurfaceArea','ShapeVA3d','Breadth3d','MeanRugosity','MeanShapeAP','MeanSymmetry','RealColonyDensity'), ~(scale(.) %>% as.vector))
coral.glmm1 <- lmer(WeightOffset ~ RealAreaOverVol + SurfaceArea + MeanSymmetry + ShapeVA3d + Breadth3d + MeanRugosity + MeanShapeAP + RealColonyDensity +
                      (1|Scan_name) + (1|PhantomType), data=DF2)
summary(coral.glmm1)
print(coral.glmm1, corr=F)
