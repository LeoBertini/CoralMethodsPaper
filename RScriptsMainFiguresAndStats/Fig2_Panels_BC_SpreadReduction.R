#Fig2 Spread Reduction with extended phantom

library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)
library(dplyr)
library(reshape2)
library(ggrepel)
library(randomcoloR)
library(datasets)
library(cowplot)
library(ggpubr)

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
DF = DF %>% filter(grepl('Ext_Complete|Ext_AllPoints_AirMod|Narrow_Raw|Narrow_AllPoints_AirMod|Narrow_NoAirWithAlu|Narrow_NoAluWithAir|Narrow_WithAirWithAlu', FitType))

#Fig2 Spread Reduction with extended phantom
library(readxl)
library(ggplot2)
library(dplyr)
library(lme4)
library(lmerTest)
library(dplyr)
library(reshape2)
library(ggrepel)
library(randomcoloR)
library(datasets)
library(cowplot)
library(ggpubr)

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
DF = DF %>% filter(grepl('Ext_Complete|Ext_AllPoints_AirMod|Narrow_Raw|Narrow_AllPoints_AirMod|Narrow_NoAluWithAir|Narrow_WithAirNoAlu|Narrow_WithAirWithAlu|Narrow_NoAirWithAlu', FitType))

#metadata
METADATA1 = read_excel(datapath, sheet = '1_InternalCalib_Metadata')
DF_merged = merge(DF,METADATA1, by='Scan_name')

DF_ExtendedPhantom = DF_merged[DF_merged$PhantomType.x =='Extended',]
DF_NormalPhantom = DF_merged[DF_merged$PhantomType.x =='Narrow',]


SD_EXT = DF_ExtendedPhantom %>%
  group_by(Scan_name) %>%
  summarise_at(c('WeightOffset','RealColonyDensity'), list(mean = mean, sd = sd, se = ~sd(.)/sqrt(.)), na.rm=TRUE)
SD_EXT = distinct(SD_EXT, 'Scan_name', .keep_all= TRUE)

SD_EXT.lm <- lm(WeightOffset_sd ~ RealColonyDensity_mean, SD_EXT)
summary(SD_EXT.lm)

Xoverpoints_Scanname=merge(SD_EXT,METADATA1, by='Scan_name')
Xoverpoints_EXT =Xoverpoints_Scanname[Xoverpoints_Scanname$Colony_label %in% c("RMNH.Coel.31990","RMNH.Coel.39103","RMNH.Coel.39104_P1", "RMNH.Coel.39162_P2","RMNH.Coel.39169", "ZMA.Coel.6779"),]

my_colors = c('#e6194b', '#911eb4', '#ffe119', '#4363d8', '#f58231', '#3cb44b')


EXTPLOT = ggplot(data = SD_EXT, aes( x = RealColonyDensity_mean ,
                      y = WeightOffset_sd))+ 
  
          geom_point(aes( x = RealColonyDensity_mean ,
                                        y = WeightOffset_sd),
                                   data = SD_EXT,
                                   size = 2,
                                   na.rm = TRUE,
                                   alpha = 1,
                                   shape = 20, color='black') + 
  
          geom_point(aes( x = RealColonyDensity_mean ,
                          y = WeightOffset_sd,
                          colour=Scan_name),
                     data = Xoverpoints_EXT,
                     size = 6,
                     na.rm = TRUE,
                     alpha = 1,
                     shape = 20) + scale_color_manual(values = my_colors) +
  
         geom_smooth(data =SD_EXT,  
                      aes( x = RealColonyDensity_mean ,
                           y = WeightOffset_sd), 
                      method='lm', fullrange=T, linetype='dashed', color='darkgrey',alpha=0.5)+
          
          stat_cor(aes(label = paste(..rr.label..)), 
                   r.accuracy = 0.01,
                   label.x = 1.5, label.y = 3, size = 4)+
  
          ylim(0, 5)+
          xlim(1,1.6)+
  
          ggtitle("Extended Phantom") +
          theme_bw() + 
          theme(axis.text = element_text(size = 12, color = 'black'), 
                axis.title = element_text(size = 12), 
                panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .05),
                panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .05), 
                legend.position = "none")+
  
        ylab(paste("")) +
        xlab(bquote('Colony density (g' ~cm^-3~')'))

#NORMAL SD DATA

SD_NORM = DF_NormalPhantom %>%
  group_by(Scan_name) %>%
  summarise_at(c('WeightOffset','RealColonyDensity'), list(mean = mean, sd = sd, se = ~sd(.)/sqrt(.)), na.rm=TRUE)

SD_NORM = distinct(SD_NORM, 'Scan_name', .keep_all= TRUE)
Xoverpoints_Scanname=merge(SD_NORM,METADATA1, by='Scan_name')
Xoverpoints_NORM =Xoverpoints_Scanname[Xoverpoints_Scanname$Colony_label %in% c("RMNH.Coel.31990","RMNH.Coel.39103","RMNH.Coel.39104_P1", "RMNH.Coel.39162_P2","RMNH.Coel.39169", "ZMA.Coel.6779"),]


NORMPLOT = ggplot(data = SD_NORM, aes( x = RealColonyDensity_mean ,
                       y = WeightOffset_sd))+   
  
           geom_point(aes( x = RealColonyDensity_mean ,
                          y = WeightOffset_sd),
                     data = SD_NORM,
                     size = 2,
                     na.rm = TRUE,
                     alpha = 1,
                     shape = 20, color='black') +
  
            geom_point(aes( x = RealColonyDensity_mean ,
                            y = WeightOffset_sd,
                            colour=Scan_name),
                       data = Xoverpoints_NORM,
                       size = 6,
                       na.rm = TRUE,
                       alpha = 1,
                       shape = 20) + scale_color_manual(values = my_colors) +
          
           geom_smooth(data =SD_NORM,  
                      aes( x = RealColonyDensity_mean ,
                      y = WeightOffset_sd), 
                      method='lm', fullrange=T, linetype='dashed', color='darkgrey',alpha=0.5)+
            
            stat_cor(aes(label = paste(..rr.label..)), 
                    # adds R^2 value
                     r.accuracy = 0.01,
                     label.x = 1.5, label.y = 3, size = 4)+
          
           ylim(0, 5) +
           xlim(1,1.6)+
          
           ggtitle("Narrow Phantom") +
          
           theme_bw() + 
           theme(axis.text = element_text(size = 12, color = 'black'), 
                axis.title = element_text(size = 12), 
                panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .05),
                panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .05), 
                legend.position = "none")+
  
          ylab(paste("Spread around density offsets (1sd [%])")) +
          xlab(bquote('Colony density (g' ~cm^-3~')'))


# All figures in GRID -----------------------------------------------------
plot_grid(NORMPLOT, EXTPLOT, nrow=1, ncol=2, labels = c('b)', 'c)'))


#paired t-test between means and spreads over larger population of scans
t.test(SD_EXT$WeightOffset_mean, SD_NORM$WeightOffset_mean, paired=TRUE)
t.test(SD_EXT$WeightOffset_sd, SD_NORM$WeightOffset_sd, paired=TRUE)


#population means
mean(SD_EXT$WeightOffset_mean)
sd(SD_EXT$WeightOffset_mean)

mean(SD_NORM$WeightOffset_mean)
sd(SD_NORM$WeightOffset_mean)





