Data and analysis files for the paper "Fast Eyes, Sharp Eyes, or Good Eyes? What Links Visual Perception to Higher-Order Cognition".

Contents

RawData/: Raw data of the perceptual and cognitive tasks, recorded directly on the experimental computer.
SummaryData/: Trial-level perceptual data, cognitive scores, and summary scores derived from the raw data, plus the MCMC trace of the model.
Preprocessing.Rmd: Turns the raw data into the files in `SummaryData/`.
Model.Rmd: Fits the hierarchical psychometric structural equation model to the trial-level perceptual data and the cognitive scores, and computes the tables reported in the paper.
model.jags: JAGS specification of the model. It must be in the same directory as Model.Rmd.

Workflow

1. Run `Preprocessing.Rmd` to create the summary files in `SummaryData/`.
2. Run `Model.Rmd` to fit the model. It reads `model.jags` and saves the MCMC trace to `SummaryData/trace.rds`.