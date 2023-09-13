# Fit examples and histograms
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

setwd("~/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/R_Scripts_Leo/")


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
xmin =0
xmax =3.5
#least_dense coral LB_0048 - EXTENDED 
target_coral=c('LB_0048', 'LB_0043')
myplots = list()

for (coral in target_coral) {
  idx=which(coral==target_coral)
  
  #TODO_COMPLETE Overlay histogram as secondary axis 
  
  histo_raw = read.csv(paste('/Users/leonardobertini/Library/CloudStorage/OneDrive-SharedLibraries-UniversityofBristol/grp-CT Methods paper - General/LB_Results/R_Scripts_Leo/Histogram-',coral,'.csv',sep=''), header=TRUE)
  histo_raw = histo_raw[1:65535,]
  colnames(histo_raw) = c('Grey', 'Count')
  histo_raw$Grey =seq(1,2^16-1, by=1)
  histo_raw[histo_raw$Count>100000,] = 0
  
  
  EXT_DATA_EXT= DF[DF$Scan_name==coral & DF$FitType=='Exponential_Ext_Complete_n11',] 
  LIN_DATA_EXT= DF[DF$Scan_name==coral & DF$FitType=='Linear_Ext_Complete_n11',] 
  POLY_DATA_EXT= DF[DF$Scan_name==coral & DF$FitType=='Poly3_Ext_Complete_n11',] 
  GAU_DATA_EXT= DF[DF$Scan_name==coral & DF$FitType=='Gaussian_Ext_Complete_n11',]
  
  Phantom_Greys = as.numeric(unlist(strsplit(gsub("\\[|\\]", "", EXT_DATA_EXT$Gray_vals), ',')))
  Phantom_Densities = as.numeric(unlist(strsplit(gsub("\\[|\\]", "", EXT_DATA_EXT$Density_vals), ',')))
  Phantom_DF = cbind.data.frame(Phantom_Greys,Phantom_Densities)
  colnames(Phantom_DF)= c('PhantomGreys','PhantomDensities')
  
  
  #histogram total area: sum of product between bin-width (always 1) and height.. therefore sum of counts
  AREA_TOTAL = sum(histo_raw$Count)
  #histogram areas between epoxy and i5
  epoxy_grey = floor(Phantom_DF$PhantomGreys[5])
  i5_grey = floor(Phantom_DF$PhantomGreys[10])
  narrow_hist = data.frame(histo_raw)
  narrow_hist2 = narrow_hist[narrow_hist$Grey > epoxy_grey  &  narrow_hist$Grey  <= i5_grey,]
  AREA_narrow = sum(narrow_hist2$Count)
  #printing values
  print(sprintf("Coral Histogram: %s", coral))
  print(sprintf("Narrow Phantom area covers: %s percent of total histogram", round(AREA_narrow/AREA_TOTAL,digits=3)*100))
  
  #histogram total area: sum of product between bin-width (always 1) and height. therefore sum of counts
  air_grey = floor(Phantom_DF$PhantomGreys[1])
  alu_grey = floor(Phantom_DF$PhantomGreys[11])
  exp_hist = data.frame(histo_raw)
  exp_hist2 = exp_hist[exp_hist$Grey > air_grey  &  exp_hist$Grey  < alu_grey,]
  AREA_exp = sum(exp_hist2$Count)
  #printing values
  print(sprintf("Coral Histogram: %s", coral))
  print(sprintf("Extended Phantom area covers: %s percent of total histogram", round(AREA_exp/AREA_TOTAL,digits=3)*100))
  
  
  
  fit_exp = function(Dataframe, xmin, xmax){
  a=gsub("\\[|\\]", "", Dataframe$Coefficients_High_Low_Order)
  b=as.numeric(unlist(strsplit(a,",")))
  Densities=seq(xmin, xmax,by=0.1)
  Greys=b[1]*exp(b[2]*(Densities)) + b[3]
  
  out = cbind.data.frame(Densities, 
                         Greys, 
                         factor(c(rep('Exponential', length(Densities)))), 
                         factor(c(rep(Dataframe$PhantomType, length(Densities))))
                         )
  colnames(out) = c('Densities', 'Greys', 'Fit', 'PhantomType')
  
  return(out)
  }
  
  fit_lin = function(Dataframe,xmin, xmax){
    a=gsub("\\[|\\]", "", Dataframe$Coefficients_High_Low_Order)
    b=as.numeric(unlist(strsplit(a,",")))
    
    Densities=seq(xmin, xmax,by=0.1)
    Greys=b[1]*Densities + b[2]
    
    out = cbind.data.frame(Densities, 
                           Greys, 
                           factor(c(rep('Linear', length(Densities)))),
                           factor(c(rep(Dataframe$PhantomType, length(Densities))))
                           )
    colnames(out) = c('Densities', 'Greys', 'Fit','PhantomType')
    
    return(out)
  }
  
  fit_gau = function(Dataframe,xmin, xmax){
    a=gsub("\\[|\\]", "", Dataframe$Coefficients_High_Low_Order)
    b=as.numeric(unlist(strsplit(a,",")))
    
    Densities=seq(xmin, xmax,by=0.1)
    Greys=b[1]*exp(-((Densities-b[2])^2)/(2*b[3]^2))
    
    out = cbind.data.frame(Densities, 
                           Greys, 
                           factor(c(rep('Gaussian', length(Densities)))),
                           factor(c(rep(Dataframe$PhantomType, length(Densities))))
                           )
    colnames(out) = c('Densities', 'Greys', 'Fit', 'PhantomType')
    
    return(out)
  }
  
  fit_poly3 = function(Dataframe,xmin, xmax){
    a=gsub("\\[|\\]", "", Dataframe$Coefficients_High_Low_Order)
    b=as.numeric(unlist(strsplit(a,",")))
    
    Densities=seq(xmin, xmax,by=0.1)
    Greys=b[1]*Densities^3 + b[2]*Densities^2 + b[3]*Densities^1 + b[4]
    
    out = cbind.data.frame(Densities, 
                           Greys, 
                           factor(c(rep('Poly3', length(Densities)))),
                           factor(c(rep(Dataframe$PhantomType, length(Densities)))))
    colnames(out) = c('Densities', 'Greys', 'Fit', 'PhantomType')
    
    return(out)
  }
  
  CURVES_EXT = rbind.data.frame(fit_exp(EXT_DATA_EXT, xmin, xmax),
                                fit_lin(LIN_DATA_EXT,xmin, xmax),
                                fit_gau(GAU_DATA_EXT,xmin, xmax),
                                fit_poly3(POLY_DATA_EXT,xmin, xmax)
                                )
  
  #least_dense coral LB_0048 - NORMAL
  EXT_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Exponential_Narrow_Raw_n6',] 
  LIN_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Linear_Narrow_Raw_n6',] 
  POLY_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Poly3_Narrow_Raw_n6',] 
  GAU_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Gaussian_Narrow_Raw_n6',]
  
  CURVES_48_NORM_RAW = rbind.data.frame(fit_exp(EXT_DATA_NORM,xmin, xmax),
                                    fit_lin(LIN_DATA_NORM,xmin, xmax),
                                    fit_gau(GAU_DATA_NORM,xmin, xmax),
                                    fit_poly3(POLY_DATA_NORM,xmin, xmax)
  )
  
  EXT_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Exponential_Narrow_NoAluWithAir_n7',] 
  LIN_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Linear_Narrow_NoAluWithAir_n7',] 
  POLY_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Poly3_Narrow_NoAluWithAir_n7',] 
  GAU_DATA_NORM= DF[DF$Scan_name==coral & DF$FitType=='Gaussian_Narrow_NoAluWithAir_n7',]
  
  CURVES_48_NORM_WithAir = rbind.data.frame(fit_exp(EXT_DATA_NORM,xmin, xmax),
                                        fit_lin(LIN_DATA_NORM,xmin, xmax),
                                        fit_gau(GAU_DATA_NORM,xmin, xmax),
                                        fit_poly3(POLY_DATA_NORM,xmin, xmax)
  )
  
  PLOT = ggplot()+
    
      geom_line(data=CURVES_EXT, aes(x=Densities, y=Greys, colour=Fit),
                linetype='solid',alpha=1, size=1) +
      
      geom_line(data=CURVES_48_NORM_RAW, aes(x=Densities, y=Greys, colour=Fit), 
                linetype='dotted',alpha=1, size=1)+
    
      geom_line(data=CURVES_48_NORM_WithAir, aes(x=Densities, y=Greys, colour=Fit), 
              linetype='dashed',alpha=1, size=1)+
      
      geom_point(data=Phantom_DF, aes(x=PhantomDensities,y=PhantomGreys), 
                 inherit.aes = F, shape=21, size=3)+
      
      ylim(10000,66000) +
      xlim(0, 3.5) 
    
    scaleFactor =  max(CURVES_EXT$Densities)/max(histo_raw$Count)
 
    HISTOGRAM_OVERLAY = PLOT + geom_path(data =histo_raw, 
                            aes(y = Grey, x = Count*scaleFactor), size=1, color = '#373737', fill =NA)+

    scale_x_continuous(name=bquote('Density (g' ~cm^-3~')'), sec.axis=sec_axis(~./scaleFactor, name=paste("Voxel Count  ",coral,sep='')))+
    
    geom_hline(aes(yintercept = which.max(histo_raw$Count)), linetype='dotted', col='#373737')+ 
    
    theme_bw()+
    theme(axis.text = element_text(size = 12, color = 'black'), 
          axis.title = element_text(size = 12), 
          panel.grid.major = element_line(linetype = 'dotted', colour = "black", linewidth = .05),
          panel.grid.minor = element_line(linetype = 'dotted', colour = "black", linewidth = .05), 
          legend.position = "none")+
    ylab('Greyscale intensity')
    print(HISTOGRAM_OVERLAY)
    myplots[[idx]]=HISTOGRAM_OVERLAY
}
  
plot_grid(myplots[[1]],myplots[[2]], ncol = 2, nrow = 1, labels = c('d)','e)'))



