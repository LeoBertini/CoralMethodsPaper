library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)
library(dplyr)
library(reshape2)

#function
remove_outliers = function(dataframe){
  quartiles = quantile(dataframe$Difference, probs=c(.25, .75), na.rm = FALSE)
  IQR = IQR(dataframe$Difference)
  
  Lower = quartiles[1] - 1.5*IQR
  Upper = quartiles[2] + 1.5*IQR
  
  DFNoOutliers = subset(dataframe, dataframe$Difference > Lower & dataframe$Difference < Upper)
  return (DFNoOutliers)
}

# Getting the path of your current open file
setwd("~/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/R_Scripts_Leo/")

# importing data
datapath = '/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/MP_CompleteDatasetLeoFinal.xlsx'
DF = read_excel(datapath, sheet = '3_XOver_WeightTests')
DF$Scan_name = as.factor(DF$Scan_name)
DF$RealColonyDensity = as.numeric(DF$RealColonyDensity)
DF$RealWeight = as.numeric(DF$RealWeight)
DF$FitType =as.factor(DF$FitType)
DF$PhantomType =as.factor(DF$PhantomType)
DF$WeightOffset = as.numeric(DF$WeightOffset)
DF$WeightOffset = DF$WeightOffset*100 #change to percentage
#make the flagged 9999999 data NaN (spurious weights due to failing to find roots for inverse functions)
DF$WeightOffset[DF$WeightOffset ==9.999999e+08] = NaN 


#metadata
METADATA1 = read_excel(datapath, sheet = '3_XOver_Metadata')
DF_merged = merge(DF,METADATA1, by='Scan_name')
DF_merged = DF_merged %>% filter(grepl('Ext_Complete|Ext_AllPoints_AirMod|Narrow_Raw|Narrow_AllPoints_AirMod|Narrow_NoAirWithAlu|Narrow_NoAluWithAir|Narrow_WithAirWithAlu', FitType))

# filter only Type1 and Type2 crosses and 6 true crossovers
require(tidyverse)
DF_merged = DF_merged %>%
  filter(str_detect(CalibrationApproach.x, "INTERNAL") | str_detect(CalibrationApproach.x, "EXTERNAL"))

DF_merged$CalibrationApproach.x = factor(DF_merged$CalibrationApproach.x,     # Reorder factor levels
                         c("EXTERNAL", "INTERNAL"))

DF_merged$PhantomType.x = factor(DF_merged$PhantomType.x,     # Reorder factor levels
                                          c("Narrow", "Extended"))



# FIGURES -----------------------------------------------------------------
#overlap with mean and standard error 

XOVER_PLOT = ggplot() +
  
  stat_summary(aes(x = CalibrationApproach.x:PhantomType.x,
                   y = WeightOffset,
                   colour= factor(Colony_label),
                   group =factor(Colony_label)),
               data = DF_merged,
               fun.data = "mean_sdl", geom = "errorbar", fun.args = list(mult = 1), 
               width=0.2, na.rm = TRUE, size=1) + # adding error bars
  
  
  stat_summary(aes( x = CalibrationApproach.x:PhantomType.x ,
                    y = WeightOffset,
                    colour= factor(Colony_label),
                    group = factor(Colony_label)),
               data = DF_merged,
               fun = "mean", 
               geom = "point", 
               size = 2, 
               na.rm = TRUE) +
  
  
  stat_summary(aes( x = CalibrationApproach.x:PhantomType.x ,
                    y = WeightOffset,
                    colour= factor(Colony_label),
                    group = factor(Colony_label):PhantomType.x),
               data = DF_merged,
               fun.data = "mean_sdl", geom = "line", linewidth=.5, fun.args = list(mult = 1 ))+ # adding error bars (standard error) +
  
  scale_color_manual(values = c('#e6194b', '#911eb4', '#ffe119', '#4363d8', '#f58231', '#3cb44b'))+

  
  ylim(-15,15) +
  geom_hline(yintercept=0, color ='black') +
  theme_bw() + 
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12), 
        panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .05),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .05), 
        legend.position = "none")
  

XOVER_PLOT

#STATS

# re-arranging the dataset to do paired-t tests on the mean values
DF_grouped_stats = DF_merged %>%
  group_by(Scan_name, Colony_label, CalibrationApproach.x, PhantomType.x) %>%
  summarise_at(vars(RealColonyDensity, WeightOffset), funs(mean=mean(., na.rm=T), sd=sd(., na.rm=T))) %>% 
  as.data.frame()


#REPORTING  normal and extended phantom design (max difference between 6 point calib. and 11 point calib.)
DF_Narrow6 = DF_merged %>% filter(grepl('Narrow_Raw_n6', FitType),na.rm=TRUE)
DF_Narrow6 = DF_Narrow6[order(DF_Narrow6$Scan_name,DF_Narrow6$FitType),]

DF_Ext11 =  DF_merged %>% filter(grepl('Ext_Complete_n11', FitType),na.rm=TRUE)
DF_Ext11 = DF_Ext11[order(DF_Ext11$Scan_name,DF_Ext11$FitType),]



diff1 = abs(DF_Ext11$WeightOffset-DF_Narrow6$WeightOffset)
max(diff1)

#REPORTING MEAN differences between poly 11 point calib. vs linear 7 point (with air and no alu, i.e. 7 point calib.)
DF_Poly11 = DF_merged %>% filter(grepl('Poly3_Ext_Complete', FitType))
DF_Linear7 = DF_merged %>% filter(grepl('Linear_Narrow_NoAluWithAir_n7', FitType))

diff2 = abs(DF_Poly11$WeightOffset - DF_Linear7$WeightOffset)
max(diff2)


####
#REPORTING MEAN AND SD in grouped data
mean(DF_grouped_stats$WeightOffset_mean[DF_grouped_stats$PhantomType.x=='Extended' & DF_grouped_stats$CalibrationApproach.x=='INTERNAL'],)
sd(DF_grouped_stats$WeightOffset_mean[DF_grouped_stats$PhantomType.x=='Extended' & DF_grouped_stats$CalibrationApproach.x=='INTERNAL'],)

mean(DF_grouped_stats$WeightOffset_sd[DF_grouped_stats$PhantomType.x=='Extended' & DF_grouped_stats$CalibrationApproach.x=='INTERNAL'],)
sd(DF_grouped_stats$WeightOffset_sd[DF_grouped_stats$PhantomType.x=='Extended' & DF_grouped_stats$CalibrationApproach.x=='INTERNAL'],)


mean(DF_grouped_stats$WeightOffset_mean[DF_grouped_stats$PhantomType.x=='Narrow'& DF_grouped_stats$CalibrationApproach.x=='EXTERNAL'],)
sd(DF_grouped_stats$WeightOffset_mean[DF_grouped_stats$PhantomType.x=='Narrow' & DF_grouped_stats$CalibrationApproach.x=='EXTERNAL'],)

mean(DF_grouped_stats$WeightOffset_sd[DF_grouped_stats$PhantomType.x=='Narrow'& DF_grouped_stats$CalibrationApproach.x=='EXTERNAL'],)
sd(DF_grouped_stats$WeightOffset_sd[DF_grouped_stats$PhantomType.x=='Narrow' & DF_grouped_stats$CalibrationApproach.x=='EXTERNAL'],)




#PAIRED TESTS FIXING CALIBRATION APPROACH
# test between means
InternalDATA = DF_grouped_stats[DF_grouped_stats$CalibrationApproach.x=='INTERNAL',]
t.test(WeightOffset_mean~PhantomType.x, paired=TRUE, data= InternalDATA )

ExternalDATA = DF_grouped_stats[DF_grouped_stats$CalibrationApproach.x=='EXTERNAL',]
t.test(WeightOffset_mean~PhantomType.x, paired=TRUE, data= ExternalDATA )

# test between spreads
t.test(WeightOffset_sd~PhantomType.x, paired=TRUE, data= InternalDATA )
t.test(WeightOffset_sd~PhantomType.x, paired=TRUE, data= ExternalDATA )



