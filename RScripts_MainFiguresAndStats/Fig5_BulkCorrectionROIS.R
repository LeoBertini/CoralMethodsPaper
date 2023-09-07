library(readxl)
library(ggplot2)
library(dplyr)
library(scales)
library(cowplot)

datapath="/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/Jitter_test/Grey_from_ROIS.xlsx" 
DF_jitter = read_excel(datapath, sheet = 'BulkCorrPlot')
DF_jitter$DensityROICat =as.factor(DF_jitter$DensityROICat)


DF_6785 = DF_jitter[DF_jitter$CoralReg=='ZMA-COEL-6785',]
DF_6781 = DF_jitter[DF_jitter$CoralReg=='ZMA-COEL-6781',]


FIG_5B1 = ggplot() +
  
  geom_point(aes(x=factor(SettingCat), 
                 y=DensityUncorr,
                 color=DensityROICat,
                 shape=CoralReg),
              size = 2,
              data = DF_jitter) +
  
  geom_smooth(data=DF_jitter, 
              mapping= aes(
                x=factor(SettingCat),
                y=DensityUncorr,
                group=LM_Group,
                color=DensityROICat,
                fill=DensityROICat), 
              method='lm', 
              inherit.aes = F, 
              fullrange=T, 
              linetype='dashed',
              size = .2,
              se=T,
              level=0.95,
              alpha = 0.1)+
  
  scale_shape_manual(values=c(22, 23))+
  scale_color_manual(values=c('red','blue'))+
  
  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12), 
        panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .1),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .1), 
        legend.position = "none") +
  
  ylab(bquote('Uncorrected density wihtin ROIs (g' ~cm^-3~')')) +
  xlab("X-ray scan settings (1:6, see panel 'a')") +
  
  
  scale_y_continuous(labels = label_number(accuracy = 0.01), 
                     limits = c(0.9, 1.85))
  
FIG_5B1


FIG_5B2 = ggplot() +
  
  geom_point(aes(x=factor(SettingCat), 
                 y=DensityCorr,
                 color=DensityROICat,
                 shape=CoralReg),
             size = 2,
             data = DF_jitter) +
  
  
  geom_smooth(data=DF_jitter, 
              mapping= aes(
    x=factor(SettingCat),
    y=DensityCorr,
    group=LM_Group,
    color=DensityROICat,
    fill=DensityROICat), 
    method='lm', 
    inherit.aes = F, 
    fullrange=T, 
    linetype='dashed',
    size = .2,
    se=T,
    level=0.95,
    alpha = 0.1)+
  
  scale_shape_manual(values=c(22, 23))+
  scale_color_manual(values=c('red','blue'))+

  
  theme_bw() + 
  theme(axis.text = element_text(size = 12, color = 'black'), 
        axis.title = element_text(size = 12), 
        panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .1),
        panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .1), 
        legend.position = "none")+
  
  ylab(bquote('Corrected density wihtin ROIs (g' ~cm^-3~')')) +
  xlab("X-ray scan settings (1:6, see panel 'a')") +

  
  scale_y_continuous(labels = label_number(accuracy = 0.01), 
                     limits = c(0.9, 1.85))

FIG_5B2


plot_grid(FIG_5B1, FIG_5B2, nrow=1, ncol=2, labels = c('b)', 'c)'))


file5A = "/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/R_Scripts_Leo/Fig5A.rdata"

load(file5A)
FIG_5A= FIG_C1

plot_grid(
  plot_grid(NULL, FIG_5A, NULL, nrow = 1, rel_widths = c(0.5, 1, 0.5), labels=c('','a)','')),
  plot_grid(FIG_5B1, FIG_5B2, nrow=1, ncol=2, labels = c('b)', 'c)')),
  nrow = 2
)



