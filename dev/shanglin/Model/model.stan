data {
  int<lower=1> N;
  int<lower=1> I;                                 // n_subj
  int<lower=1> J;                                 // n_perc_task
  int<lower=1> C;                                 // n_cog_task
  int<lower=1> T;                                 // n_task
  array[N] int<lower=1, upper=I> id;
  array[N] int<lower=1, upper=J> task;
  vector[N] s;                                    // x
  array[N] int<lower=0> k;
  array[N] int<lower=1> ntrials;
  matrix[I, C] cog;
  real<lower=T - 1> nu0;
  real<lower=0> tau;                     
}

transformed data {
  matrix[T, T] S0 = diag_matrix(rep_vector(1.0, T));
  vector[T] zero_vec = rep_vector(0.0, T);
}

parameters {
  vector[T] mu;
  vector[J] beta;
  vector<lower=0>[T] sigma;                       
  cov_matrix[T] Sigma_raw;
  matrix[I, T] raw;
}

transformed parameters {
  matrix[I, T] theta;
  for (t in 1:T) {
    theta[, t] = mu[t] + sigma[t] * raw[, t];
  }
}

model {
  mu    ~ normal(0, 5);
  beta  ~ normal(0, 5);
  sigma ~ student_t(3, 0, 2.5);
  Sigma_raw ~ inv_wishart(nu0, S0);

  for (i in 1:I) {
    raw[i]' ~ multi_normal(zero_vec, Sigma_raw);
  }
  for (c in 1:C) {
    cog[, c] ~ normal(theta[, J + c], tau);
  }

  vector[N] eta;
  for (n in 1:N) {
    eta[n] = beta[task[n]] * (theta[id[n], task[n]] - s[n]);
  }
  k ~ binomial(ntrials, Phi(eta));
}

generated quantities {
  matrix[T, T] Sigma;
  matrix[T, T] Omega;
  vector[T] sigma_theta;
  {
    matrix[T, T] D = diag_matrix(sigma);
    Sigma = D * Sigma_raw * D;
  }
  for (t in 1:T) sigma_theta[t] = sqrt(Sigma[t, t]);
  for (t1 in 1:T) {
    for (t2 in 1:T) {
      Omega[t1, t2] = Sigma[t1, t2] / sqrt(Sigma[t1, t1] * Sigma[t2, t2]);
    }
  }
}
