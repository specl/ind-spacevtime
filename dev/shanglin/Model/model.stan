data {
  int<lower=1> N;                                 
  int<lower=1> n_subj;
  int<lower=1> n_perc_task;                         
  int<lower=1> n_cog_task;                         
  int<lower=1> n_task;                              
  array[N] int<lower=1, upper=n_subj> id;
  array[N] int<lower=1, upper=n_perc_task> task;
  vector[N] x;                               
  array[N] int<lower=0> k;                             
  array[N] int<lower=1> ntrials;                
  matrix[n_subj, n_cog_task] cog;                  
  real<lower=n_task - 1> nu0;                        
  real<lower=0> sigma_obs;                        
}

transformed data {
  matrix[n_task, n_task] S0 = diag_matrix(rep_vector(1.0, n_task));
  vector[n_task] zero_vec = rep_vector(0.0, n_task);
}

parameters {
  vector[n_task] mu;
  vector[n_perc_task] beta;
  vector<lower=0>[n_task] xi;
  cov_matrix[n_task] Sigma_raw;
  matrix[n_subj, n_task] raw;                      
}

transformed parameters {
  matrix[n_subj, n_task] theta;
  for (t in 1:n_task) {
    theta[, t] = mu[t] + xi[t] * raw[, t];
  }
}

model {
  mu   ~ normal(0, 5);
  beta ~ normal(0, 5);
  xi   ~ student_t(3, 0, 2.5);
  Sigma_raw ~ inv_wishart(nu0, S0);

  for (i in 1:n_subj) {
    raw[i]' ~ multi_normal(zero_vec, Sigma_raw);
  }
  for (c in 1:n_cog_task) {
    cog[, c] ~ normal(theta[, n_perc_task + c], sigma_obs);
  }
  vector[N] eta;
  for (n in 1:N) {
    eta[n] = beta[task[n]] * (theta[id[n], task[n]] - x[n]);
  }
  k ~ binomial(ntrials, Phi(eta));
}

generated quantities {
  matrix[n_task, n_task] Sigma;
  matrix[n_task, n_task] Omega;
  vector[n_task] sigma_theta;
  {
    matrix[n_task, n_task] D = diag_matrix(xi);
    Sigma = D * Sigma_raw * D;
  }
  for (t in 1:n_task) sigma_theta[t] = sqrt(Sigma[t, t]);
  for (t1 in 1:n_task) {
    for (t2 in 1:n_task) {
      Omega[t1, t2] = Sigma[t1, t2] / sqrt(Sigma[t1, t1] * Sigma[t2, t2]);
    }
  }
}
