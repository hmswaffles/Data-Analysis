//Stan model2 for bay to breakers as two gumbel distributions

data {
	int<lower=0> j; //   index/number of observations/years
	real y[j]; //winning time per each year

}

parameters {

	real<lower=1, upper=2700> mu_1 ;
	real<lower=1, upper=900> beta_1; //Beta should be reparameterized the same way
	

	real<lower=1> theta_m;
	real<lower=1> theta_b;

	real<lower=-.0001,upper=1.0001> z; //categorical indicator

}

transformed parameters{
	real<lower=1,upper=2800> mu[2];
	real<lower=1,upper=900> beta[2];

	mu[1] <- mu_1;
	mu[2] <- mu[1] + theta_m;

	beta[1]<- beta_1 ;
	beta[2]<- beta[1]+theta_b;

	


}

model{
	theta_m ~ normal(300,140); 
	theta_b ~ normal(170,120);
	mu_1 ~ student_t(1,2085,200);
	beta_1 ~ student_t(1,30,100);
	z ~ student_t(1,.5,200);
	

	{
		real log_p; //for categorical indicator
		real logm_p; //
		log_p <- log(z);
		logm_p <- log1m(z);
		for (n in 1:j)
			increment_log_prob(log_sum_exp(log_p
									+gumbel_log(y[j],mu[1],beta[1]),
									logm_p
									+gumbel_log(y[j],mu[2],beta[2])));

	}


}

