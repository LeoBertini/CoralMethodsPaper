library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)

#function
remove_outliers = function(dataframe){
quartiles = quantile(dataframe$WeightOffset, probs=c(.25, .75), na.rm = FALSE)
IQR = IQR(dataframe$WeightOffset)

Lower = quartiles[1] - 1.5*IQR
Upper = quartiles[2] + 1.5*IQR

DFNoOutliers = subset(dataframe, dataframe$WeightOffset > Lower & dataframe$WeightOffset < Upper)
return (DFNoOutliers)
}


# read data
datacoral <-read_xlsx('/Users/leonardobertini/RProjects/CoralMethodsPaper/InternalCalibAnalysis/ConsolidadedResultsPhantomExpanded.xlsx',col_names=TRUE)
DF <- data.frame(datacoral)

DF$PhantomType = as.factor(DF$PhantomType)
DF$Equipment = as.factor(DF$Equipment)
DF$Group = as.factor(DF$Group)
DF$Scan_name = as.factor(DF$Scan_name)
DF$CoralAlias = as.factor(DF$CoralAlias)


#exploratory figure of Phantom bias in density
ggplot(DF, aes(y =RealColonyDensity, x = VirtualDensity, color=PhantomType)) + 
  geom_point() + 
  geom_smooth(method = lm, se=TRUE)


model0 <- aov(WeightOffset ~ PhantomType, data = DF)
summary(model0)
#check for multicolinearity
#vif(model0) # --> shows no multicolinearity as VIF values < 5

#exploratory boxplot of PhantomType VS WieghtOffset
bp <- ggplot(DF, aes(x = PhantomType , y = WeightOffset, fill=PhantomType)) +
  geom_boxplot()
print(bp)


#REMOVING OUTLIERS
DF_ExpandedBristol= DF[(DF$Group =='Bristol:Expanded'),] #subset Expanded to remove outliers
DF_ExpandedLondon= DF[(DF$Group =='London:Expanded'),] #subset Expanded to remove outliers
DF_ExpandedNoOutB1 = remove_outliers(DF_ExpandedBristol)
DF_ExpandedNoOutL1 = remove_outliers(DF_ExpandedLondon)

DF_Normal= DF[(DF$PhantomType =='Normal'),] #subset Phantom Normal to bind later
DF_NormalNoOut=remove_outliers(DF_Normal)


DF_Expanded= DF[(DF$PhantomType =='Expanded'),] #subset Expanded to remove outliers
DF_ExpandedNoOut=remove_outliers(DF_Expanded)


DF_CLEAN = rbind(DF_ExpandedNoOut ,DF_NormalNoOut) #bind data

#exploratory boxplot of PhantomType VS WieghtOffset
bp <- ggplot(DF_CLEAN, aes(x = PhantomType , y = WeightOffset, fill=PhantomType)) +
  geom_boxplot()
print(bp)


#Fit model again without outliers
model1 <- aov(WeightOffset ~ PhantomType, data = DF_CLEAN)
summary(model1)

#checking assumption of homogeneous variance without main outliers
plot(model1, 1)
library(car)
leveneTest( WeightOffset ~ PhantomType, data = DF_CLEAN)

# checking assumption of normality with new data without main outliers
plot(model1, 2)
# Extract the residuals
aov_residuals <- residuals(object = model1)
# Run Shapiro-Wilk test
shapiro.test(x = aov_residuals )

##reporting post hoc pairwise effects 
library(multcomp)
library(lsmeans)
lsmeans(model1, pairwise ~ PhantomType)

library("ggpubr")
ggline(DF_CLEAN, x = "PhantomType", y = "WeightOffset", color='PhantomType',
       add = c("mean_se", "dotplot"),)


#CONCLUSION --> 
#EXPANDED PHANTOM GIVES DIFFERENT OFFSETS ON AVERAGE WHEN COMPARED TO NORMAL PHANTOM


#CORRELOGRAM WITH ALL NUMERIC VARS for EXPANDED PHANTOM
DF_CLEAN_EXP= DF_CLEAN[(DF_CLEAN$PhantomType =='Expanded'),] #subset Expanded to remove outliers
Corr_DF = subset(DF_CLEAN_EXP, select = -c(Least_Square_Sum_Residuals,RMSE, R2)) #keeping only meaningfull variables
result_corr<-cor(Corr_DF[, unlist(lapply(Corr_DF, is.numeric))])

library(corrplot)
corrplot(result_corr, type = "upper", order = "hclust", diag=F,
         tl.col = "black", tl.srt = 45)


#####NEXT PART
#modelling weight offset effects


#First we standardize numeric variables
DF2 <- DF_CLEAN %>% mutate_at(c('Volume_estimate','WeightOffset','VirtualDensity','RealAreaOverVol','RealWeight','SurfaceArea','ShapeVA3d','Breadth3d','MeanRugosity','MeanShapeAP','MeanSymmetry','RealColonyDensity'), ~(scale(.) %>% as.vector))
coral.glmm1 <- lmer(WeightOffset ~ PhantomType + RealAreaOverVol + SurfaceArea + MeanSymmetry + ShapeVA3d + Breadth3d + MeanRugosity + MeanShapeAP + RealColonyDensity  + (1|CoralAlias), data=DF2)
summary(coral.glmm1)
print(coral.glmm1, corr=F)
