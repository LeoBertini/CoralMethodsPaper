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
DF$ColonyNickname = as.factor(DF$ColonyNickname)


#ANOVA to check for significant effects using entire dataset and all variables
modelCrosses0 <- aov(WeightOffset ~ ColonyNickname + CrossType*PhantomType, data = DF)
summary(modelCrosses0)
###
library(car)
Anova(modelCrosses0, type = "III") #this is done as we have unbalanced design

#check for multicolinearity
vif(modelCrosses0) # --> shows high multicolinearity of CrossType with another independent variable. 
#Need to account for this.
#I suspect high correlation with ColonyNickName. 
#We see that ColonyNickname is a variable that still significantly affects the results, 
#We can try to eliminate that effect by standardizing the data. 


#### First we filter the DATA to include only crosses of type 1 and 2, 
# as these are the ones we are interested in
FilteredCrossesDF=DF[(DF$CrossType == 'Type1' | DF$CrossType == 'Type2'),]

# Then modelling by  WeightOffsetUnitArea to 
#1) remove effects by individual colonies and multicolinearity with CrossType
#2) re-scale this metric because values are too small

FilteredCrossesDF['OffsetPerUnitArea']= FilteredCrossesDF$WeightOffset/FilteredCrossesDF$SurfaceArea
scaled_data = scale(FilteredCrossesDF$OffsetPerUnitArea, center = TRUE, scale = TRUE)
attributes(scaled_data) <- NULL
FilteredCrossesDF['OffsetPerUnitAreaScaled']=scaled_data
  

#Now we fit a model where ColonyNickname is included to check if its effect was removed or 
#if multicolinearity is at least controlled
modelCrosses1 <- aov(OffsetPerUnitAreaScaled~ ColonyNickname + CrossType*PhantomType, data = FilteredCrossesDF)
summary(modelCrosses1)
vif(modelCrosses1)
#it seems multicolinearity is not a problem anymore as VIF values are <5

######### Visualize data 
# Box plot all data by groups (check effects of phantom type on weight offset)
bp <- ggplot(FilteredCrossesDF, aes(x = PhantomType , y = OffsetPerUnitAreaScaled, fill=CrossType )) +
  geom_boxplot()
print(bp)

#REMOVING OUTLIERS - Step1

quartiles <- quantile(FilteredCrossesDF$OffsetPerUnitAreaScaled, probs=c(.25, .75), na.rm = FALSE)
IQR <- IQR(FilteredCrossesDF$OffsetPerUnitAreaScaled)

Lower <- quartiles[1] - 1.5*IQR
Upper <- quartiles[2] + 1.5*IQR

FilteredNoOutliers <- subset(FilteredCrossesDF, FilteredCrossesDF$OffsetPerUnitAreaScaled > Lower & FilteredCrossesDF$OffsetPerUnitAreaScaled < Upper)


#Fit model again without outliers
modelCrosses2 <- aov(OffsetPerUnitAreaScaled~ ColonyNickname + CrossType*PhantomType, data = FilteredNoOutliers)
summary(modelCrosses2)
vif(modelCrosses2)


#checking assumption of homogeneous variance without main outliers
plot(modelCrosses2, 1)
library(car)
leveneTest( OffsetPerUnitAreaScaled~ CrossType*PhantomType, data = FilteredNoOutliers)

# checking assumption of normality with new data without main outliers
plot(modelCrosses2, 2)
# Extract the residuals
aov_residuals <- residuals(object = modelCrosses2)
# Run Shapiro-Wilk test
shapiro.test(x = aov_residuals )



#doing type 3 as we have unbalanced design to make sure we have good coefficients and p-values are reliable
library(car)
Anova(modelCrosses2, type = "III") #this is done as we have unbalanced design
model.tables(modelCrosses2, type="means", se = TRUE)



##reporting post hoc pairwise effects 
library(multcomp)
summary(glht(modelCrosses2, linfct = mcp(CrossType = "Tukey")))
summary(glht(modelCrosses2, linfct = mcp(PhantomType = "Tukey")))

library(lsmeans)
lsmeans(modelCrosses2, pairwise ~ PhantomType|CrossType)




#####FIGURES######


#plotting mean effect of crosses
d <- summary(lsmeans(modelCrosses2, ~ PhantomType:CrossType))
library(ggplot2)

ggplot(d, aes(CrossType:PhantomType)) +
  geom_line(aes(y = lsmean, group = 1)) +
  geom_errorbar(aes(ymin = lower.CL, ymax = upper.CL), width = 0.2) +
  geom_point(aes(y = lsmean), size = 3, shape = 21, fill = "white") +
  labs(x = "CrossType:PhantomType", y = "ls mean WeightOffsetPerUnitAreaScaled", title = "ls mean result between CrossType") +
  theme_bw()




library("ggpubr")
ggline(FilteredNoOutliers, x = "CrossType", y = "OffsetPerUnitAreaScaled", color = "PhantomType",
       add = c("mean_se", "dotplot"),)

######### Visualize data 
# Box plot all data by groups (check effects of phantom type on weight offset)
bp <- ggplot(FilteredNoOutliers, aes(x = PhantomType , y = OffsetPerUnitAreaScaled, fill=CrossType )) +
  geom_boxplot()
print(bp)

#exploring correlations
result_corr<-cor(FilteredNoOutliers[, unlist(lapply(DF, is.numeric))])    
library(corrplot)
corrplot(result_corr, type = "upper", order = "hclust", 
         tl.col = "black", tl.srt = 45)



