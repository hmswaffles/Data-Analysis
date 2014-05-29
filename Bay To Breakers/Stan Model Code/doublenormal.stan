//Stan model2 for bay to breakers as two normal
data {
	int<lower=0> j; //   index/number of observations/years
	real y[j]; //winning time per each year

}

parameters {

	real<lower=1, upper=2700> mu_1 ;
	real<lower=1, upper=900> sigma_1; 

	real<lower=1> theta_m;
	real<lower=1> theta_b;

	real<lower=-.000000001,upper=1.000001> z; //categorical indicator

}

transformed parameters{
	real<lower=1,upper=2800> mu[2];
	real<lower=1,upper=900> sigma[2];

	mu[1] <- mu_1;
	mu[2] <- mu[1] + theta_m;

	sigma[1]<- sigma_1 ;
	sigma[2]<- sigma[1]+theta_b;

	


}

model{
	
	theta_m ~ normal(300,140); 
	theta_b ~ normal(170,120);
	mu_1 ~ student_t(1,2085,200);
	sigma_1 ~ student_t(1,30,100);
	z ~ normal(.5,100);
	

	{	

		real log_p; //for categorical indicator
		real logm_p; //
		log_p <- log(z);
		logm_p <- log1m(z);
		for (n in 1:j)
			increment_log_prob(log_sum_exp(log_p
									+student_t_log(y[j],1,mu[1],sigma[1]),
									logm_p
									+student_t_log(y[j],1,mu[2],sigma[2])));

	}


}

