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
datacoral <-read_xlsx('/Users/leonardobertini/RProjects/CoralMethodsPaper/ConsolidadedResultsPhantomExpanded.xlsx',col_names=TRUE)
DF <- data.frame(datacoral)

DF$PhantomType = as.factor(DF$PhantomType)
DF$Equipment = as.factor(DF$Equipment)
DF$Group = as.factor(DF$Group)
DF$Scan_name = as.factor(DF$Scan_name)


#exploratory figure of equipment bias in density
ggplot(DF, aes(y =RealColonyDensity, x = VirtualDensity, color=PhantomType)) + 
  geom_point() + 
  geom_smooth(method = lm, se=TRUE)


model0 <- aov(WeightOffset ~ PhantomType, data = DF)
summary(model0)
#check for multicolinearity
vif(model0) # --> shows no multicolinearity as VIF values < 5

#exploratory boxplot of PhantomType VS WieghtOffset
bp <- ggplot(DF, aes(x = PhantomType , y = WeightOffset, fill=PhantomType)) +
  geom_boxplot()
print(bp)


#REMOVING OUTLIERS
DF_Normal= DF[(DF$PhantomType =='Normal'),] #subset Phantom Normal to bind later
DF_Expanded= DF[(DF$PhantomType =='Expanded'),] #subset Expanded to remove outliers
DF_ExpandedNoOut = remove_outliers(DF_Expanded)

DF_CLEAN = rbind(DF_ExpandedNoOut,DF_Normal) #bind data

#exploratory boxplot of PhantomType VS WieghtOffset
bp <- ggplot(DF_CLEAN, aes(x = PhantomType , y = WeightOffset, fill=PhantomType)) +
  geom_boxplot()
print(bp)


#Fit model again without outliers
model1 <- aov(WeightOffset ~ PhantomType*Equipment, data = DF_CLEAN)
summary(model1)

#checking assumption of homogeneous variance without main outliers
plot(model1, 1)
library(car)
leveneTest( WeightOffset ~ PhantomType*Equipment, data = DF_CLEAN)

# checking assumption of normality with new data without main outliers
plot(model1, 2)
# Extract the residuals
aov_residuals <- residuals(object = model1)
# Run Shapiro-Wilk test
shapiro.test(x = aov_residuals )

##reporting post hoc pairwise effects 
library(multcomp)
lsmeans(model1, pairwise ~ PhantomType|Equipment)

library("ggpubr")
ggline(DF_CLEAN, x = "Equipment", y = "WeightOffset", color = "PhantomType",
       add = c("mean_se", "dotplot"),)


#CONCLUSION --> 
#EXPANDED PHANTOM GIVES DIFFERENT OFFSETS ON AVERAGE WHEN COMPARED TO NORMAL PHANTOM


########

#Subset Data so that only expanded scans are changed
DF_FilteredBristol= DF[(DF$Group =='Bristol:Expanded'),]
DF_FilteredLondon= DF[(DF$Group =='London:Expanded'),]

DF_FilteredBristolNoOutliers=remove_outliers(DF_FilteredBristol)
DF_FilteredLondonNoOutliers=remove_outliers(DF_FilteredLondon)

#binding clean dataframes
CleanDF_NoOut=rbind(DF_FilteredBristolNoOutliers,DF_FilteredLondonNoOutliers,DF_Normal)

#exploratory boxplot of PhantomType VS WieghtOffset
bp <- ggplot(CleanDF_NoOut, aes(x = PhantomType , y = WeightOffset, fill=Group)) +
  geom_boxplot()
print(bp)


summary(glht(model1, linfct = mcp(Equipment = "Tukey")))


library(lsmeans)
lsmeans(model1, pairwise ~ PhantomType|Equipment)



#########
ggplot(DF, aes(x = VirtualDensity, y = RealColonyDensity, 
               fill = Equipment, color=PhantomType)) +
         geom_point(aes(shape=Equipment)) +
         geom_smooth(method = "lm", fill = PhantomType:Equpment, se=TRUE)
       


##########
#modelling if WeightOffsets are different between phantom types
model0 <- lm(WeightOffset ~ PhantomType*Equipment, data = DF)
summary(model0)
###
library(car)
Anova(model0, type = "III") #this is done as we have unbalanced design











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
