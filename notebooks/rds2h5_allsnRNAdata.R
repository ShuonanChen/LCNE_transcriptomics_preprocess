# created 08/19/2025 for LC paper 


################## metadata do the same thing ##################
metafile='/allen/programs/celltypes/workgroups/rnaseqanalysis/10x/v4/10xV4_Pilot/Neuromodulatory_Noradrenergic/10xV4_Neuromodulatory_Noradrenergic_complete_RTX-4134_CR8_samp.dat_241111.rda'
load(metafile). # samp.dat
outputfile = '~/scratch_shuonan/LC_scRNAseq/conversion_files/snRNAseq_LCNE_ALLCELLS_metadata.csv'
write.csv(samp.dat, outputfile, row.names = TRUE)




################## anndata part ##################
library(Matrix)

# laod the data (foo it not used!)
happytargetfile='/allen/programs/celltypes/workgroups/rnaseqanalysis/10x/v4/10xV4_Pilot/Neuromodulatory_Noradrenergic/10xV4_Neuromodulatory_Noradrenergic_complete_RTX-4134_mat_241111.rda'
foo =load(happytargetfile)

# conver to sce objects
library(SingleCellExperiment)
library(zellkonverter)
sce <- SingleCellExperiment(assays = list(X = mat))

# save the results..
outputfile = '~/scratch_shuonan/LC_scRNAseq/conversion_files/snRNAseq_LCNE_ALLCELLS.h5ad'
writeH5AD(sce, outputfile)

