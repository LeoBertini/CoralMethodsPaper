library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)

# read data
datacoral <-read_xlsx('/Users/leonardobertini/RProjects/CoralMethodsPaper/ConsolidatedResultsXover.xlsx',col_names=TRUE)
DF <- data.frame(datacoral)

# Box plot all data by groups (check effects of phantom type on weight offset)
bp <- ggplot(DF, aes(x = PhantomType , y = WeightOffset, fill=CrossType )) +
  geom_boxplot()
print(bp)


#explicitly defining variables as factors
DF$CrossType = as.factor(DF$CrossType)
DF$PhantomType = as.factor(DF$PhantomType)


#ANOVA to check for significant differences using entire dataset 
modelCrosses0 <- aov(WeightOffset ~ CrossType*PhantomType, data = DF)
library(car)
Anova(modelCrosses0, type = "III") #this is done as we have unbalanced design

summary(modelCrosses0)
model.tables(modelCrosses0, type="means", se = TRUE)

library(multcomp)
summary(glht(modelCrosses0, linfct = mcp(CrossType = "Tukey")))

library(lsmeans)
lsmeans(modelCrosses0, pairwise ~ CrossType:PhantomType)


#plotting mean effect of crossess
d <- summary(lsmeans(modelCrosses0, ~ CrossType))
library(ggplot2)

ggplot(d, aes(CrossType)) +
  geom_line(aes(y = lsmean, group = 1)) +
  geom_errorbar(aes(ymin = lower.CL, ymax = upper.CL), width = 0.2) +
  geom_point(aes(y = lsmean), size = 3, shape = 21, fill = "white") +
  labs(x = "CrossType", y = "ls mean WeightOffset", title = "ls mean result between CrossType") +
  theme_bw()




#### filtered DATA to include only crosstype 1 and 2
FilteredCrossesDF=DF[(DF$CrossType == 'Type1' | DF$CrossType == 'Type2'),]

#ANOVA to check for significant differences using whole data to get LSMEANS
modelCrosses1 <- aov(WeightOffset ~ CrossType*PhantomType, data = FilteredCrossesDF)
library(car)
Anova(modelCrosses1, type = "III") #this is done as we have unbalanced design
model.tables(modelCrosses1, type="means", se = TRUE)


#checking assumption of homogenous variance and normality
plot(modelCrosses1, 1)
library(car)
leveneTest(WeightOffset ~ CrossType*PhantomType, data = FilteredCrossesDF)

plot(modelCrosses1, 2)
# Extract the residuals
aov_residuals <- residuals(object = modelCrosses1)
# Run Shapiro-Wilk test
shapiro.test(x = aov_residuals )



#reporting post hoc pairwise effects 
library(multcomp)
summary(glht(modelCrosses1, linfct = mcp(CrossType = "Tukey")))
library(lsmeans)
lsmeans(modelCrosses1, pairwise ~ PhantomType | CrossType)





###########
library("ggpubr")
ggline(FilteredCrossesDF, x = "CrossType", y = "WeightOffset", color = "PhantomType",
       add = c("mean_se", "dotplot"),)



#filter only expanded phantom
GoodPhantomData=DF[DF$PhantomType == 'Expanded',]

# Box plot by group (check effects of phantom type on weight offset)
bp <- ggplot(FilteredCrossesDF, aes(x = CrossType , y = WeightOffset, fill=PhantomType)) +
  geom_boxplot()
print(bp)


modelCrosses <- aov(WeightOffset ~ PhantomType + CrossType, data = FilteredCrossesDF)
summary(modelCrosses)
model.tables(modelCrosses, type="means", se = TRUE)








# Box plot by group (check effects of phantom type on weight offset)
bp <- ggplot(GoodPhantomData, aes(x = CrossType , y = WeightOffset)) +
  geom_boxplot()
print(bp)


#exploring correlations
result_corr<-cor(DF[, unlist(lapply(DF, is.numeric))])    
library(corrplot)
corrplot(result_corr, type = "upper", order = "hclust", 
         tl.col = "black", tl.srt = 45)



#modelling weight offset effects
#First we standardize numeric variables
datacoralMOD <- GoodPhantomData %>% mutate_at(c('Volume_estimate','WeightOffset','VirtualDensity','RealAreaOverVol','RealWeight','SurfaceArea','ShapeVA3d','Breadth3d','MeanRugosity','MeanShapeAP','MeanSymmetry','RealColonyDensity'), ~(scale(.) %>% as.vector))


coral.glmm1 <- lmer(WeightOffset ~ RealAreaOverVol + SurfaceArea + MeanSymmetry + ShapeVA3d + Breadth3d + MeanRugosity + MeanShapeAP + RealColonyDensity + CrossType  +
                      (1|ColonyNickname) + (1|CrossType), data=DF)
summary(coral.glmm1)
print(coral.glmm1, corr=F)


