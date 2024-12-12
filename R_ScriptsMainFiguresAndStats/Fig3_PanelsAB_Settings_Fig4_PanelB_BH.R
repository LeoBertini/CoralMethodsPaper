#Fig3

library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)
library(dplyr)
library(reshape2)
library(ggrepel)
library(randomcoloR)
library(ggnewscale)
library(colorspace)
library(cowplot)

bin_voltage = function(Dataframe){
  #append_text to scan conditions for grouping later (3 kV bands <170, 170-190, >190)
  
  ScanCondition = c(rep(NaN,dim(Dataframe)[1]))
  MatThick = c(rep(NaN,dim(Dataframe)[1]))
  
  for (line in 1:nrow(Dataframe)){
    
    kV_val = Dataframe$XraykV[line]
    
    if (kV_val <= 140){
      kV_cat = 'Low_kV (=140)'
    }
    if (kV_val > 170 & kV_val <= 190){
      kV_cat = 'Medium_kV (170-190)'
    }
    if (kV_val >190){
      kV_cat = 'High_kV (215-220)'
    }
    
    
    ScanCondition[line] = kV_cat
    MatThick[line] = paste(Dataframe$Filter_material[line],Dataframe$Filter_thickness_mm[line],sep ='_')
    #bind new column
  }
  Dataframe =cbind(Dataframe,ScanConditionStr=ScanCondition, MetalAndThick = MatThick)
  #make it as factor
  Dataframe$ScanConditionStr = as.factor(Dataframe$ScanConditionStr)
  Dataframe$MetalAndThick = as.factor(Dataframe$MetalAndThick)
  
  return(Dataframe)
  
}


bin_weights = function (Dataframe, band1, band2, band3, band4){
  
  
  Weight_Bin = c(rep(NaN,dim(Dataframe)[1]))
  for (idx in 1:nrow(Dataframe)) {
    
    if (Dataframe$RealWeight[idx] < band1){
      Weight_Bin[idx] = paste('<=',as.character(band1),'g',sep='')
    }
    
    if (Dataframe$RealWeight[idx] < band2 & Dataframe$RealWeight[idx] > band1){
      Weight_Bin[idx] = paste(as.character(band1),'-',as.character(band2),'g',sep='')
    }
    
    if (Dataframe$RealWeight[idx] < band3 & Dataframe$RealWeight[idx] > band2){
      Weight_Bin[idx] =  paste(as.character(band2),'-',as.character(band3),'g',sep='')
    }
    
    if (Dataframe$RealWeight[idx] < band4 & Dataframe$RealWeight[idx] > band3){
      Weight_Bin[idx] =  paste(as.character(band3),'-',as.character(band4),'g',sep='')
    }
    
    if (Dataframe$RealWeight[idx] > band4){
      Weight_Bin[idx] =  paste('>=',as.character(band4),'g',sep='')
    }
    
  }
  
  #append column do dataframe
  Dataframe = cbind(Dataframe, WeightBin=as.factor(Weight_Bin))
  
  return(Dataframe)
}


# importing dataset
datapath = "/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/MP_CompleteDataset_SuppMat.xlsx" 

#metadata
METADATA1 = read_excel(datapath, sheet = '1_InternalCalib_Metadata')
METADATA2 = read_excel(datapath, sheet = '2_MultipleSettings_Metadata')
METADATA_ALL = rbind(METADATA1,METADATA2)

#import multiple seetings dataset
DF2 = read_excel(datapath, sheet = '2_MultipleSettings_WeightTest')
DF2$Scan_name = as.factor(DF2$Scan_name)
DF2$RealColonyDensity = as.numeric(DF2$RealColonyDensity)
DF2$FitType =as.factor(DF2$FitType)
DF2$PhantomType =as.factor(DF2$PhantomType)
DF2$WeightOffset = as.numeric(DF2$WeightOffset)
DF2_merged = merge(DF2,METADATA_ALL, by='Scan_name')
DF2_merged=bin_voltage(DF2_merged)

DF_Replicates_NoBH = DF2_merged %>% filter(!grepl('_BH', Scan_name))
#DF_Replicates_NoBH = DF_Replicates_NoBH %>% filter(grepl('NoAir_n6', FitType))

#  BH dataset --------------------------------------------------------
DF_Replicates_BH = DF2_merged %>% filter(grepl('_BH', Scan_name))
#DF_Replicates_BH = DF_Replicates_BH %>% filter(grepl('NoAir_n6', FitType))


DF_Replicates_Tin = filter(DF_Replicates_NoBH,
                           Filter_material %in% 'Tin')

DF_Replicates_Copper1 =filter(DF_Replicates_NoBH,
                              Filter_material %in% 'Copper' & Filter_thickness_mm %in% '1')

DF_Replicates_Copper2 =filter(DF_Replicates_NoBH,
                              Filter_material %in% 'Copper' & Filter_thickness_mm %in% '2')

c1 = sequential_hcl(5, palette = "Mint") 
c2 = sequential_hcl(5, palette = "Blues 3") 
c3 =  sequential_hcl(5, palette = "Reds 3")  
# 
# my_colors = c( "#005D67", "#1B817F" ,"#64A79A" ,
#                "#00366C", "#0072B4", "#79ABE2" ,
#                "#CC1C2F", "#FF7078", "#FFBEC1")


# Figure 3A ----------------------------------------------------------------


FIG_3A = ggplot() +
  
  # # tin 1 mm 
  # stat_summary(aes(x = RealColonyDensity ,
  #                  y = WeightOffset,
  #                  group = Scan_name,
  #                  colour = ScanConditionStr),
  #              data = DF_Replicates_Tin,
  #              fun.data = "mean_sdl", geom = "errorbar", fun.args = list(mult = 1), 
  #              width=.01, alpha = 0.8, na.rm = TRUE) + 
  
  
stat_summary(aes( x = RealColonyDensity ,
                  y = WeightOffset,
                  group=Scan_name, 
                  fill = ScanConditionStr),
             data = DF_Replicates_Tin,
             fun = "mean",
             geom = "point",
             size = 4,
             na.rm = TRUE,
             alpha = 0.8,
             shape = 21,
             color = 'black') + 
  
  #copper 1mm - up triangle
  
  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset,
                    group=Scan_name,
                    fill = ScanConditionStr),
               data = DF_Replicates_Copper1,
               fun = "mean",
               geom = "point",
               size = 3,
               na.rm = TRUE,
               alpha = .8,
               shape = 24, #up triangle
               color='black') +
  
  
  #copper2mm - down trinangle
  
  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset,
                    group=Scan_name,
                    fill = ScanConditionStr),
               data = DF_Replicates_Copper2,
               fun = "mean",
               geom = "point",
               size = 3,
               na.rm = TRUE,
               alpha = .8,
               shape = 25, #down triangle
               color='black') +
  
  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05), 
        panel.grid.major  = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05),
        legend.position='none',
        legend.background = element_rect(fill = alpha('grey', 0.4)),
        legend.key = element_rect(fill = alpha('grey', 0.01)),
        legend.box = 'none'
  )+
  
  ylim(-12,12) +
  xlim(1.0, 1.6) +
  
  geom_hline(yintercept=0, color ='black') +
  
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('Colony density (g' ~cm^-3~')'))

FIG_3A

#saving base fig to be used as panel A in Figure 5
#save(FIG_3A, file = "/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/R_Scripts_Leo/Fig5A.rdata")


# Figure 4B ---------------------------------------------------------------

DF_KJ = DF2_merged %>% filter(grepl('KJ', Scan_name))
col_append=c(rep(NaN,dim(DF_KJ)[1]))
DF_KJ=cbind(DF_KJ,SettingString=col_append)

for (row in 1:nrow(DF_KJ)){
  string = paste(DF_KJ$XraykV[row],' kV :', DF_KJ$MetalAndThick[row], sep='')
  DF_KJ$SettingString[row]=string
}

DF_KJ$SettingString=as.factor(DF_KJ$SettingString)
DF_KJ=bin_voltage(DF_KJ)
colnames(DF_KJ) = make.unique(names(DF_KJ))
DF_KJ$BH_Corr=as.factor(DF_KJ$BH_Corr)

###Stats
#group by scan name
DF_KJ_Stats = DF_KJ %>% 
  group_by(Scan_name, BH_Corr) %>%
  summarise_at(c('WeightOffset','RealColonyDensity'), list(mean = mean, sd = sd, se = ~sd(.)/sqrt(.)), na.rm=TRUE)
DF_KJ_Stats = distinct(DF_KJ_Stats, 'Scan_name', .keep_all= TRUE)
DF_KJ_Stats <- DF_KJ_Stats[DF_KJ_Stats$Scan_name != 'KJ_Porites_1981-3-5_140kV_Sn1_new-fil_16-bit-perc_', ] #remove single 
DF_KJ_Stats$Scan_name=gsub("_BH", "", DF_KJ_Stats$Scan_name)
DF_KJ_Stats = DF_KJ_Stats[c("Scan_name", "WeightOffset_mean", "BH_Corr")]


DF_KJ_Stats$Scan_name=as.factor(DF_KJ_Stats$Scan_name)
#we can do a 2-way anova
t.test(DF_KJ_Stats$WeightOffset_mean[DF_KJ_Stats$BH_Corr=="YES"], 
       DF_KJ_Stats$WeightOffset_mean[DF_KJ_Stats$BH_Corr=="NO"], paired=TRUE)

summary(aov(WeightOffset_mean ~ BH_Corr, data=DF_KJ_Stats))


##figure
FIG_4B = ggplot()+ 
  
  geom_boxplot(data=DF_KJ, aes(x=BH_Corr, y=WeightOffset), width=0.2, alpha=0.8)+
  
  stat_summary(aes(x=BH_Corr, 
                   y=WeightOffset, 
                   shape=MetalAndThick.1, 
                   fill=ScanConditionStr.1, 
                   group = Scan_name),
               data = DF_KJ,
               fun = "mean",
               geom = "point",
               size = 4,
               na.rm = TRUE,
               alpha = 0.8) + 
  
  stat_summary(aes(x=BH_Corr, 
                   y=WeightOffset, 
                   shape=MetalAndThick.1, 
                   fill=ScanConditionStr.1, 
                   group = BH_Corr),
               data = DF_KJ,
               fun = "mean",
               geom = "line",
               size = 4,
               na.rm = TRUE,
               alpha = 0.8) + 
  
  scale_shape_manual(values=c('Copper_1'=24,'Copper_2'=25,'Tin_1'=21)) + 
  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05), 
        panel.grid.major  = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05),
        legend.position='none',
        legend.background = element_rect(fill = alpha('grey', 0.4)),
        legend.key = element_rect(fill = alpha('grey', 0.01)),
        legend.box = 'none')+
  
  geom_hline(yintercept=0, color ='black') +
  
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('BH Correction Applied?'))


FIG_4B        



# Figure 3B ---------------------------------------------------------------------
# importing dataset
datapath = "/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/MP_CompleteDataset_SuppMat.xlsx" 

DF = read_excel(datapath, sheet = '1_InternalCalib_WeightTests')
DF$Scan_name = as.factor(DF$Scan_name)
DF$RealColonyDensity = as.numeric(DF$RealColonyDensity)
DF$RealWeight = as.numeric(DF$RealWeight)
DF$FitType =as.factor(DF$FitType)
DF$PhantomType =as.factor(DF$PhantomType)
DF$WeightOffset = as.numeric(DF$WeightOffset)
#make the flagged 9999999 data NaN (spurious weights due to failing to find roots for inverse functions)
DF$WeightOffset[DF$WeightOffset ==9.999999e+08] = NaN 


#metadata
METADATA1 = read_excel(datapath, sheet = '1_InternalCalib_Metadata')
METADATA2 = read_excel(datapath, sheet = '2_MultipleSettings_Metadata')
METADATA_ALL = rbind(METADATA1,METADATA2)

#filter Fits so that spreads only have 'AllPoints_n11' and 'RawDisk_n6'
DF_CleanFits = DF #%>% filter(grepl('AllPoints_n11|RawDisk_n6', FitType))

DF_CleanFits=bin_voltage(merge(DF_CleanFits, METADATA_ALL, by='Scan_name'))

#getting separate datasets for plot overlays in different groups
DF_Singletons_NORM= DF_CleanFits[DF_CleanFits$PhantomType.x == 'Narrow',]
DF_Singletons_EXT= DF_CleanFits[DF_CleanFits$PhantomType.x == 'Extended',]


FIG_3B_NORM = ggplot() +
  
  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset,
                    fill=ScanConditionStr,
                    shape=MetalAndThick),
               data = DF_Singletons_NORM,
               fun = "mean", 
               geom = "point", 
               size = 4, 
               na.rm = TRUE,
               alpha = 0.7)+ 
  scale_shape_manual(values=c('Copper_1.5'=24,'Copper_2'=25,'Tin_1'=21)) + 
  scale_fill_manual(values=c('violetred3','deepskyblue4'))+
  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05), 
        panel.grid.major  = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05),
        legend.position='none',
        legend.background = element_rect(fill = alpha('grey', 0.4)),
        legend.key = element_rect(fill = alpha('grey', 0.01)),
        legend.box = 'horizontal')+
  
  geom_hline(yintercept=0, color ='black') +
  
  ylim(-15,12) +
  xlim(1.0, 1.6) +
  
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('Colony density (g' ~cm^-3~')'))

FIG_3B_NORM

FIG_3B_EXT = ggplot() +
  
  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset,
                    fill=ScanConditionStr,
                    shape=MetalAndThick),
               data = DF_Singletons_EXT,
               fun = "mean", 
               geom = "point", 
               size = 4, 
               na.rm = TRUE,
               alpha = 0.7)+ 
  scale_shape_manual(values=c('Copper_1.5'=24,'Copper_2'=25,'Tin_1'=21)) + 
  scale_fill_manual(values=c('violetred3','deepskyblue4'))+
  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05), 
        panel.grid.major  = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05),
        legend.position='none',
        legend.background = element_rect(fill = alpha('grey', 0.4)),
        legend.key = element_rect(fill = alpha('grey', 0.01)),
        legend.box = 'horizontal')+
  
  geom_hline(yintercept=0, color ='black') +
  
  ylim(-15,12) +
  xlim(1.0, 1.6) +
  
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('Colony density (g' ~cm^-3~')'))


plot_grid(FIG_3A, FIG_3B_EXT, nrow=2, ncol=1, labels = c('a)', 'b)'))


# Pairwise stats between Normal and Extended Phantom ---------------------------------------------------------------------

#subpopulation mean
NarrowSingleton= DF_Singletons_NORM[DF_Singletons_NORM$PhantomType.x=='Narrow' & DF_Singletons_NORM$ScanConditionStr == 'Medium_kV (170-190)' & DF_Singletons_NORM$MetalAndThick == 'Tin_1',]
NarrowSingleton_GROUPED = NarrowSingleton %>%
  group_by(Colony_label,ScanConditionStr,MetalAndThick) %>% summarise(
    WeightOffset = mean(WeightOffset,na.rm=TRUE),
    RealColonyDensity = mean(RealColonyDensity),
    AreaOverVol = mean(AreaOverVol.x),
    RealWeight = mean(RealWeight),
  )


mean(NarrowSingleton_GROUPED$WeightOffset, na.rm=TRUE)
sd(NarrowSingleton_GROUPED$WeightOffset, na.rm=TRUE)

ExtSingleton= DF_Singletons_EXT[DF_Singletons_EXT$PhantomType.x=='Extended' & 
                                  DF_Singletons_EXT$ScanConditionStr == 'Medium_kV (170-190)' & 
                                  DF_Singletons_EXT$MetalAndThick == 'Tin_1',]

ExtSingleton_GROUPED = ExtSingleton %>%
  group_by(Colony_label,ScanConditionStr,MetalAndThick) %>% summarise(
    WeightOffset = mean(WeightOffset,na.rm=TRUE),
    RealColonyDensity = mean(RealColonyDensity),
    AreaOverVol = mean(AreaOverVol.x),
    RealWeight = mean(RealWeight),
  )


mean(ExtSingleton_GROUPED$WeightOffset, na.rm=TRUE)
sd(ExtSingleton_GROUPED$WeightOffset, na.rm=TRUE)

pairedt= t.test(ExtSingleton_GROUPED$WeightOffset,NarrowSingleton_GROUPED$WeightOffset, paired=TRUE)
pairedt
