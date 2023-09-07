#Fig1 

library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)
library(reshape2)
library(ggrepel)
library(randomcoloR)
library(ggnewscale)
library(cowplot)



bin_weights = function (Dataframe, band1, band2, band3, band4){
  
  Weight_Bin = c(rep(NaN,dim(Dataframe)[1]))
  
  for (idx in 1:nrow(Dataframe)) {
    
   if (is.na(Dataframe$RealWeight[idx])){
     print(Dataframe$Colony_label[idx])
   }
    
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


# Getting the path of your current open file
setwd("~/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/R_Scripts_Leo/")

# importing dataset
datapath="/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/MP_CompleteDatasetLeoFinal.xlsx" 

DF = read_excel(datapath, sheet = '1_InternalCalib_WeightTests')
DF$Scan_name = as.factor(DF$Scan_name)
DF$RealColonyDensity = as.numeric(DF$RealColonyDensity)
DF$RealWeight = as.numeric(DF$RealWeight)
DF$FitType =as.factor(DF$FitType)
DF$PhantomType =as.factor(DF$PhantomType)
DF$WeightOffset= as.numeric(DF$WeightOffset)
DF$WeightOffset = DF$WeightOffset*100 #change to percentage
#make the flagged 9999999 data NaN (spurious weights due to failing to find roots for inverse functions)
DF$WeightOffset[DF$WeightOffset ==9.999999e+08] = NaN 


#metadata
METADATA1 = read_excel(datapath, sheet = '1_InternalCalib_Metadata')
METADATA2 = read_excel(datapath, sheet = '2_MultipleSettings_Metadata')
METADATA_ALL = rbind(METADATA1,METADATA2)

#filter Fits so that spreads only have representative changes
DF_CleanFits = DF %>% filter(grepl('Ext_Complete|Ext_AllPoints_AirMod|Narrow_Raw|Narrow_AllPoints_AirMod|Narrow_NoAirWithAlu|Narrow_NoAluWithAir|Narrow_WithAirWithAlu', FitType))


#getting separate datasets for plot overlays in different groups
DF_Singletons_EXT= DF_CleanFits[DF_CleanFits$PhantomType == 'Extended',]
DF_Singletons_NORM= DF_CleanFits[DF_CleanFits$PhantomType == 'Narrow',]

#import multiple seetings dataset
DF2 = read_excel(datapath, sheet = '2_MultipleSettings_WeightTest')
DF2$Scan_name = as.factor(DF2$Scan_name)
DF2$RealColonyDensity = as.numeric(DF2$RealColonyDensity)
DF2$FitType =as.factor(DF2$FitType)
DF2$PhantomType =as.factor(DF2$PhantomType)
DF2$WeightOffset = DF2$WeightOffset*100 #change to percentage

                        
DF_Replicates_NoBH = DF2 %>% filter(!grepl('_BH', Scan_name))


#  BH dataset --------------------------------------------------------
DF_Replicates_BH = DF2 %>% filter(grepl('_BH', Scan_name))


#  FIGURE 1A  --------------------------------------------------------
FIG_1A = ggplot() +
  
  stat_summary(aes(x = RealColonyDensity ,
                   y = WeightOffset),
               data = DF_Singletons_NORM,
               fun.data = "mean_sdl", geom = "errorbar", fun.args = list(mult = 1), 
               width=.01, color = 'grey', alpha = 1, na.rm = TRUE) + # adding error bars
  
  
  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset),
                  data = DF_Singletons_NORM,
                  fun = "mean", 
                  geom = "point", 
                  size = 1, 
                  na.rm = TRUE,
                  color = 'grey', alpha = 1) +       
  
  stat_summary(aes(x = RealColonyDensity ,
                   y = WeightOffset),
               data = DF_Singletons_EXT,
               fun.data = "mean_sdl", geom = "errorbar", fun.args = list(mult = 1), 
               width=.01, color = 'black', alpha = .8, na.rm = TRUE) + # adding error bars
  
  stat_summary(aes(x = RealColonyDensity ,
                   y = WeightOffset),
               data = DF_Singletons_EXT,
               fun = "mean", 
               geom = "point", 
               size = 1, 
               na.rm = TRUE,
               color = 'black',
               alpha = .8) +       
  
  
stat_summary(aes(x = RealColonyDensity ,
                   y = WeightOffset,
                   group = Scan_name),
               data = DF_Replicates_NoBH,
               fun.data = "mean_sdl", geom = "errorbar", fun.args = list(mult = 1), 
               width=.01, color = 'purple', alpha = 0.5, na.rm = TRUE) + # adding error bars 
  
  
  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset,
                    group=Scan_name),
                    data = DF_Replicates_NoBH,
               fun = "mean",
               geom = "point",
               size = 1,
               na.rm = TRUE,
               alpha = 1, color = 'purple') +
  
  
  stat_summary(aes(x = RealColonyDensity ,
                   y = WeightOffset,
                   group = Scan_name),
               data = DF_Replicates_BH,
               fun.data = "mean_sdl", geom = "errorbar", fun.args = list(mult = 1), 
               width=.01, color = 'brown', alpha = 0.5, na.rm = TRUE) + # adding error bars

  stat_summary(aes( x = RealColonyDensity ,
                    y = WeightOffset,
                    group=Scan_name),
               data = DF_Replicates_BH,
               fun = "mean",
               geom = "point",
               size = 1,
               na.rm = TRUE,
               alpha = 1, color = 'brown') +
  
 
  
  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12), 
        panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .05),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .05), 
        legend.position = "none")+
  
  ylim(-15,30) +
  xlim(1, 1.6) +
  
  geom_hline(yintercept=0, color ='black') +
  
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('Colony density (g' ~cm^-3~')'))

#FIG_1A



#adding horizontal jitter points (indicative of linear correction if consistent spacing)
datapath="/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/Jitter_test/Grey_from_ROIS.xlsx" 

DF_Singletons_EXT
#dummy grouping
Dummy_group = DF_Replicates_NoBH %>%
  group_by(Scan_name) %>%
  summarise_at(c('WeightOffset'), list(mean = mean), na.rm=TRUE)
aaaa=distinct(Dummy_group)


DF_jitter = read_excel(datapath, sheet = 'HorizontalJitterPlot')
DF_jitter$Scan_slice = as.factor(DF_jitter$Scan_slice)

FIG_2A = FIG_1A + geom_point(aes(x = Colony_Density , 
                        y = Density_Offset_y_coord, 
                        group=Scan_slice),
                    data = DF_jitter, 
                    color = '#008080',
                    size = 0.3) + 
  
  geom_errorbarh( aes(xmax = Colony_Density+Diff_max, 
                      xmin = Colony_Density-Diff_min, 
                      y = Density_Offset_y_coord, 
                      group=Scan_slice),
  data = DF_jitter,
  color = '#008080',
  height = 2,
  linetype = 'dashed')+ 
  xlim(1, 1.75)


# FIGURE 1B ---------------------------------------------------------------

DF_ALL1 = DF
DF_ALL_1 = merge(DF_ALL1, METADATA_ALL, by='Scan_name') #single scans
DF_ALL_2 = merge(DF_Replicates_NoBH, METADATA_ALL, by='Scan_name') #replicate scans

DF_ALL = rbind(DF_ALL_1,DF_ALL_2) #all raw

GROUPED_ALL = DF_ALL %>%
  group_by(Colony_label) %>% summarise(
  WeightOffset = mean(WeightOffset,na.rm=TRUE),
  RealColonyDensity = mean(RealColonyDensity,na.rm=TRUE),
  AreaOverVol = mean(AreaOverVol.x, na.rm=TRUE),
  RealWeight = mean(RealWeight, na.rm=TRUE),
  Volume = mean(Volume_cm3, na.rm=TRUE),
  VoxelSize = mean(VoxelSize_mm, na.rm=TRUE),
)


#reporting grouped means
mean(GROUPED_ALL$WeightOffset, na.rm=TRUE)
sd(GROUPED_ALL$WeightOffset, na.rm=TRUE)

light_corals = GROUPED_ALL[GROUPED_ALL$RealColonyDensity<=1.2,]
mean(light_corals$WeightOffset)
sd(light_corals$WeightOffset)

dense_corals = GROUPED_ALL[GROUPED_ALL$RealColonyDensity>1.2,]
mean(dense_corals$WeightOffset)
sd(dense_corals$WeightOffset)


#adding size classes based on weight 
GROUPED_ALL = bin_weights(Dataframe = GROUPED_ALL, 
                          band1=500,
                          band2=1000,
                          band3=1500,
                          band4=2000)

#specify WeightBin in the order I want displayed in the legend
GROUPED_ALL$WeightBin = factor(GROUPED_ALL$WeightBin, levels = c('<=500g', '500-1000g', '1000-1500g' ,'1500-2000g', '>=2000g'))
#ADDING COL Multiple or Singleton
GROUPED_ALL$ScanType =  c(rep(NaN, dim(GROUPED_ALL)[1]))
for (row in 1:nrow(GROUPED_ALL)){
  if (grepl("NHMUK_1981-3-5_578-9|ZMA.Coel.6781|RMNH.Coel.10165|ZMA.Coel.6785|ZMA.Coel.1048|RMNH.Coel.10165",GROUPED_ALL$Colony_label[row]) ==T){
    GROUPED_ALL$ScanType[row] = 'MultiScan'
  }
  else{GROUPED_ALL$ScanType[row] = 'SingleScan'
}}
GROUPED_ALL$ScanType = as.factor(GROUPED_ALL$ScanType)



#color weight bins
my_colors = c('#a5cee8','#4575b4','#ffcccc','#ff9999','#d73027')
#my_colors = c('#4575b4','#4575b4','#d73027','#d73027','#d73027')

FIG_1B = ggplot()+

  geom_point(data = GROUPED_ALL, aes(x = RealColonyDensity, 
                               y = WeightOffset, 
                               size = AreaOverVol, 
                               fill = WeightBin,
                               colour=ScanType), shape=21, alpha=1,stroke=.5) + 
                              
                              scale_size_binned(range = c(1, 4)) + 
                              scale_fill_manual(values = my_colors)+ 
                              scale_colour_manual(values=c('black','white'))+

  
  
  theme_bw() + 
  ylim(-15,15) + 
  xlim(1, 1.6)+
  
  geom_hline(yintercept=0, color ='black')+
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('Colony density (g' ~cm^-3~')'))+
  
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05), 
        panel.grid.major  = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05),
        legend.position=c(.75,.81),
        legend.background = element_rect(fill = alpha('grey', 0.4)),
        legend.key = element_rect(fill = alpha('grey', 0.01)),
        legend.box = 'horizontal'
  )

#FIG_1B


# TESTING IF Light and Heavy corals show significant relationships --------
#ref https://eliocamp.github.io/codigo-r/2018/09/multiple-color-and-fill-scales-with-ggplot2/

#ADDING ROW WIEGHT CAT
GROUPED_ALL = GROUPED_ALL %>% mutate(WeightCat =
                        case_when(RealWeight <= 1000 ~ "Light (<1000g)", 
                                  RealWeight > 1000 ~ "Heavy (>1000g)"))
GROUPED_ALL$WeightCat = factor(GROUPED_ALL$WeightCat, levels = c("Light (<1000g)","Heavy (>1000g)"))
fit_colors = c('#020079','#ff6666')


FIG_1B = FIG_1B +  new_scale_color() + 
  
  geom_smooth(data=GROUPED_ALL, mapping= aes(
                 x=RealColonyDensity,
                 y=WeightOffset,
                 group=WeightCat,
                 color=WeightCat), 
                 method='lm', 
                 inherit.aes = F, 
                 fullrange=F, 
                 linetype='dashed',
                 size = .1,
                 se=T,
                 alpha = 0.1)+ scale_color_manual(values = fit_colors)+
  theme(legend.position = 'none')
#FIG_1B

# All figures in GRID -----------------------------------------------------
plot_grid(FIG_1A, FIG_1B, nrow=2, ncol=1, labels = c('a)', 'b)'))


###################################################################################################
#STATS

#Fitting a GLM with averaged data 
model = lm(WeightOffset~ RealColonyDensity + WeightCat+ AreaOverVol + RealColonyDensity*WeightCat , data=GROUPED_ALL )
summary(model)

###################################################################################################
#Fitting a GLMM to account for repeated measures. Colony id as random effect
DF_ALL$RealWeight = DF_ALL$Colony_Weight_g
#DF_ALL MOD
DF_ALL_MOD = bin_weights(Dataframe = DF_ALL, 
            band1=500,
            band2=1000,
            band3=1500,
            band4=2000)

DF_ALL_MOD$ScanType =  c(rep(NaN, dim(DF_ALL_MOD)[1]))
for (row in 1:nrow(DF_ALL_MOD)){
  if (grepl("NHMUK_1981-3-5_578-9|ZMA.Coel.6781|RMNH.Coel.10165|ZMA.Coel.6785|ZMA.Coel.1048|RMNH.Coel.10165",DF_ALL_MOD$Colony_label[row]) ==T){
    DF_ALL_MOD$ScanType[row] = 'MultiScan'
  }
  else{DF_ALL_MOD$ScanType[row] = 'SingleScan'
  }}
DF_ALL_MOD$ScanType = as.factor(DF_ALL_MOD$ScanType)

#ADDING ROW WIEGHT CAT
DF_ALL_MOD = DF_ALL_MOD %>% mutate(WeightCat =
                                       case_when(RealWeight <= 1000 ~ "Light (<1000g)", 
                                                 RealWeight > 1000 ~ "Heavy (>1000g)"))

DF_ALL_MOD$WeightCat = factor(DF_ALL_MOD$WeightCat, levels = c("Light (<1000g)","Heavy (>1000g)"))
# 
library(lme4)
model1 = lmer(formula = WeightOffset ~ RealColonyDensity + VoxelSize_mm + WeightCat + AreaOverVol.x + RealColonyDensity:WeightCat + (1|Colony_label), data=DF_ALL_MOD)
summary(model1)
library(MuMIn)
r.squaredGLMM(model1)
anova(model1)

###################################################################################################


##### voxel size effects -- no relationship found
FIG_2B = ggplot()+
  
  geom_point(data = GROUPED_ALL, aes(x = RealColonyDensity, 
                                     y = WeightOffset, 
                                     size = VoxelSize*1000, 
                                     fill = WeightBin,
                                     colour=ScanType), shape=21, alpha=1,stroke=.5) + 
  
  scale_size_binned() + 
  scale_fill_manual(values = my_colors)+ 
  scale_colour_manual(values=c('black','white'))+
  
  
  
  theme_bw() + 
  ylim(-15,15) + 
  xlim(1, 1.6)+
  
  geom_hline(yintercept=0, color ='black')+
  ylab(paste("Density offset",'(%)')) +
  xlab(bquote('Colony density (g' ~cm^-3~')'))+
  
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05), 
        panel.grid.major  = element_line(linetype = 'dotted', colour = "black", linewidth = 0.05),
        legend.position=c(.75,.81),
        legend.background = element_rect(fill = alpha('grey', 0.4)),
        legend.key = element_rect(fill = alpha('grey', 0.01)),
        legend.box = 'horizontal'
  )

#FIG_2B
