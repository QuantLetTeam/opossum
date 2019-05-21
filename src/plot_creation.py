from SimulateData import UserInterface
from plot_functions import propensity_score_plt, all_treatment_effect_plt, single_treatment_effect_plt, output_difference_plt, avg_treatment_effect_plt 
import numpy as np
from sklearn.linear_model import LogisticRegression

"""
User Input: 
N, k, options / effect type, assignment type (random...)

Output:
Y, X, Treatment Effect = theta_0 * D
Correlation Matrix
if specified use get function for g_0(x), D

"""


    
##### propensity score plot
u = UserInterface(10000,10, seed=5)
u.generate_treatment(random_assignment=False, treatment_option_weights = [1, 0, 0, 0])
y, X, assignment, treatment = u.output_data()

prop_score_conditioned = u.s.propensity_score


u = UserInterface(10000,10, seed=5)
u.generate_treatment(random_assignment=True, assignment_prob = 0.5,  treatment_option_weights = [1, 0, 0, 0])
y, X, assignment, treatment = u.output_data()

prop_score_random = u.s.propensity_score

figure = propensity_score_plt(prop_score_conditioned, prop_score_random)


##### treatment effects plots

### Each option alone 
treatment_list = []
assignment_list = []

for i in range(4):
    treatment_option_weights = np.zeros(4)
    treatment_option_weights[i] = 1
    
    u = UserInterface(10000,10, seed=123)
    u.generate_treatment(random_assignment=True, treatment_option_weights = treatment_option_weights)
    y, X, assignment, treatment = u.output_data(binary=False)
    
    treatment_list.append(treatment)
    assignment_list.append(assignment)

all_treatment_effect_plt(treatment_list, assignment_list)

### All options at once 

# equally distributed
u = UserInterface(10000,10, seed=23)
u.generate_treatment(constant=True, heterogeneous=True, negative=True, no_treatment=True)
y, X, assignment, treatment = u.output_data(binary=False)
    
single_treatment_effect_plt(treatment, assignment, title = 'All 4 options at once equally distributed')

# more realistic case

u = UserInterface(10000,10, seed=23)
u.generate_treatment(treatment_option_weights = [0, 0.7, 0.1, 0.2])
y, X, assignment, treatment = u.output_data(binary=False)
    
single_treatment_effect_plt(treatment, assignment, 
                            title = 'More realistic case with [0, 0.7, 0.1, 0.2] distribution')


##### Output differences treated/not_treated plots

### continous 
u = UserInterface(10000,10, seed=7)
u.generate_treatment(random_assignment=True, treatment_option_weights = [0, 1, 0, 0])
y, X, assignment, treatment = u.output_data(False)

treatment_list.append(treatment)
assignment_list.append(assignment)

y_treated = y[assignment==1]
y_not_treated = y[assignment==0]

output_difference_plt(y_not_treated, y_treated)

### binary
u = UserInterface(10000,10, seed=15)
u.generate_treatment(random_assignment=True, treatment_option_weights = [0, 1, 0, 0])
y, X, assignment, treatment = u.output_data(True)



y_treated = y[assignment==1]
y_not_treated = y[assignment==0]

output_difference_plt(y_not_treated, y_treated, binary = True)

##### ATE examples

treatment_list = []
assignment_list = []

# constant
u = UserInterface(10000,10, seed=15)
u.generate_treatment(random_assignment=True, treatment_option_weights = [1, 0, 0, 0])
y, X, assignment, treatment = u.output_data(True)

treatment_list.append(treatment)
assignment_list.append(assignment)

ate_constant = np.mean(y[assignment==1]) - np.mean(y[assignment==0])

# positive negative
u = UserInterface(10000,10, seed=15)
u.generate_treatment(random_assignment=True, treatment_option_weights = [0.5, 0, 0.5, 0])
y, X, assignment, treatment = u.output_data(True)

treatment_list.append(treatment)
assignment_list.append(assignment)

ate_pos_neg = np.mean(y[assignment==1]) - np.mean(y[assignment==0])

# all mixed
u = UserInterface(10000,10, seed=15)
u.generate_treatment(random_assignment=True, treatment_option_weights = [0.2, 0.5, 0.1, 0.2])
y, X, assignment, treatment = u.output_data(True)

treatment_list.append(treatment)
assignment_list.append(assignment)

ate_mix = np.mean(y[assignment==1]) - np.mean(y[assignment==0])

# 80% no effect
u = UserInterface(10000,10, seed=15)
u.generate_treatment(random_assignment=True, treatment_option_weights = [0, 0.2, 0, 0.8])
y, X, assignment, treatment = u.output_data(True)

treatment_list.append(treatment)
assignment_list.append(assignment)

ate_non = np.mean(y[assignment==1]) - np.mean(y[assignment==0])


ate_list = [ate_constant, ate_pos_neg, ate_mix, ate_non]

avg_treatment_effect_plt(treatment_list, assignment_list, ate_list)















#
###### Inverse probability weighting
#u = UserInterface(10000,10, seed=12)
#u.generate_treatment(random_assignment=True, treatment_option_weights = [1, 0, 0, 0])
#y, X, assignment, treatment = u.output_data(False)
#
#
## setting up logistic regression    
#lr = LogisticRegression()
## fit model to data
#lr.fit(X, assignment)
## predict propensity scores D ~ X
#prop_score_predictions = lr.predict_proba(X)[:,1]
#
#
##    propensity_score_plt(prop_score_predictions, u.s.propensity_score )
#
#def inverse_probability_weighting(prop_score_predictions, assignment, y):
#    '''
#    
#    ATE = mu_1 - mu_0
#    ATE = E[ (D_i*Y_i) / e(x_i) ]   -   E[ ((1-D_i)*Y_i) / (1-e(x_i)) ] 
#    
#    '''
#    mu_1 = np.sum(y[assignment == 1] / prop_score_predictions[assignment == 1])/len(y)
#
#    mu_0 = np.sum(y[assignment == 0] / (1-prop_score_predictions[assignment == 0]))/len(y)
#
#    tau = mu_1 - mu_0
#    
#    return tau
#
#ipw_ate_estimate = inverse_probability_weighting(u.s.propensity_score, assignment, y)
#
#simple_ate_estimate = np.mean(y[assignment==1]) - np.mean(y[assignment==0])


