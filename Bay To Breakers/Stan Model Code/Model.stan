//Stan model for bay to breakers

data {
	int<lower=0> j; //   index/number of observations/years
	real y[j]; //winning time per each year

}

parameters {
	real<lower=0> mu;
	real<lower=0> beta;

}

model{
	mu ~ student_t(1,2300,200);
	beta ~ student_t(1,25,100);
	y ~ gumbel(mu,beta);
}

