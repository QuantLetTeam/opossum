
from scipy import random, stats
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import make_spd_matrix
from helpers import standardize



class SimData:
    """
    Model: Refer to Paper in Readme

    # Y = Outcome (dependend variable). Either continuous or binary.
    # N = Number of observations (real number)
    # k = Number of covariates (real number). At least 10
    # random_d = treatment assignment: (Either T for random assignment or F for confounding on X)
    # theta = treatment effect: (Either real number for only one theta, or "binary" {0.1,0.3}, "con" for continuous values (0.1,0.3) or "big" for {1,0.4})
    # var = Size of the variance (Noise-level)

    """

    def __init__(self, N, k):
        random.seed(8) # For debugging
        self.N = N # Natural, number of observations
        self.k = k # Natural, number of covariates
        #self.p = 0.5

    def generate_outcome_variable(self):
        """
        Model-wise Y
        options: binary, multilevel(discrete), continuous

        Y = Theta_0 * D + g_0(X) + U
        D = m_0(X) + V
        Theta_0 = t_0(Z) + W

        """
        realized_treatment_effect = self.generate_realized_treatment_effect() # Theta_0 * D
        y = realized_treatment_effect + self.g_0_X + self.generate_noise()  # * g_0(x) + U

        return y, self.X, realized_treatment_effect

    def generate_covariates(self, plot = False, nonlinear = True):

        """
        Model-wise: g_0(X)

        Algorithm for Covariates

        1) Generate a random positive definite covariance matrix Sigma
        based on a uniform distribution over the space k*k of the correlation matrix

        2) Scale the covariance matrix. This equals the correlation matrix and can be seen as
        the covariance matrix of the standardized random variables sigma = x / sd(x)

        3) Generate random normal distributed variables X_{N*k} with mean = 0 and variance = sigma

        Create low- and high-dimensional dataset.
         Correlation between the covariates isrealistic.
         options:
            – continuous with some known distribution (e.g.  Normal()).
            – discrete (dummy and multilevel).
        """

        # 1)
        # Sigma
        # A = random.rand(self.k, self.k) # drawn from uniform distribution in [0,1]
        # sigma = np.dot(A,A.transpose()) # a matrix multiplied with its transposed is aaaalways positive definite
        sigma = make_spd_matrix(self.k, self.k) # Achtung: Fuer Cluster gedacht, deswegen lustige properties
        # 2)
        # Correlation Matrix P = Sigma * (1/sd)
        sd = 1
        # Todo:  Frage an Daniel: Wahl der SD?
        # Aktuell kriegen wir sehr hohe, positive Korrelationen aber
        # 1. unrealistisch, 2. Multikollinearitaet und numerische Instabilitaet wenn wir Modelle fitten wollen.
        # Ursache wsh. 1) durch A * A_transposed // versuchen zu fixen durch make_spd_matrix
        self.p = sigma * (1/sd)  # not used yet!

        # 3)
        mu = np.repeat(0, self.k)
        X = np.random.multivariate_normal(mu, sigma, self.N)
        self.X = X

        if nonlinear:
            b = 1/np.arange(1,self.k+1) # diminishing weight vector
            self.g_0_X = np.cos(np.dot(X,b))**2  # overwrite with nonlinear covariates
        else:
            # If not nonlinear, then g_0(X) is just the identity
            self.g_0_X = X  # dim(X) = n * k

        if plot:
            plt.interactive(False)
            plt.hist(X, bins=10)
            plt.ylabel('Test')
            plt.show(block=True)
        

        return None


# maybe changing bernoulli=True to random=True to make it clear that the options are random/not random?
    def generate_treatment_assignment(self, random = True):
        
        """
        Treatment assignment
        binary and multilevel (discrete).The generation should be
        –random (randomized control trial) with possible imbalanced assignment (e.g.  75% treatedand 25% control.

        :return:
        """

        #weight_vector = 1/np.arange(1,self.k+1)             # diminishing weights
        weight_vector_alt = np.random.uniform(0,1,self.k)   # random weights from U[0,1]
        
        # random treatment assignment
        if random:
            m_0 = 0.5  # probability

        # treatment assignment depending on covariates 
        # issue: assigning just about 25% because of m_0's ~ [0,0.4]
        # solution: adding 0.2 to each probability m_0?
        else:
            a = np.dot(self.X, weight_vector_alt)    # X*weights -> a (Nx1 vector)

            # Using empirical mean, sd
            a_mean = np.mean(a)
            a_sigma = np.std(a)
            z = (a - a_mean) / a_sigma          # normalizing 'a' vector
            
            # using normalized vector z to get probabilities from normal pdf
            # to later assign treatment with binomial in D
            m_0 = stats.norm.cdf(z)

        # creating array out of binomial distribution that assigns treatment according to probability m_0
        self.D = np.random.binomial(1, m_0, self.N)
        self.weight_vector = weight_vector_alt
        
        return None
        # Output self.D n * 1 vector of 0 and 1
        # Output self.weight_vector k * 1


    def visualize_correlation(self):
        """
        Generates Correlation Matrix of the Covariates
        :return:
        """

        df = pd.DataFrame(self.X)  # all highly correlated because essentially drawn from the same distribution
        # and NOT nonlinear at this point.
        # However, there should exist some negative correlation, too. This is obviously because all covariances have
        # a positive sign.
        corr = df.corr()
        corr.style.background_gradient(cmap='coolwarm') # requires HTML backend
        sns.heatmap(corr, annot = True)
        plt.show()
        return None

    def generate_treatment_effect(self, predefined_idx = None, constant = True, heterogeneity = True,
                                  negative = True, no_treatment = True):
        """
        options Theta(X), where X are covariates:
        –No treatment effect(for all or for some people).
        –Constant ( for all or for some people).
        –heterogeneity (discrete and continuous).
        –Even negative values seem realistic ( for some people).

        -predefined_idx:
        Instead of randomly assigning (drawing from a uniform distribution) the k covariates to an option,
        the user can choose a predefined index set upon which he whishes to apply the options.
        length = n
        Must be array-like type

        if not option in ['no treatment', 'constant', 'heterogeneity', 'negative']:
            raise ValueError('Wrong Options')

        :return: Vector Theta, length self.k (covariates), theta_0
        """

        # Process options
        options = []
        if constant:
            options.append(1)
        if heterogeneity:
            options.append(2)
        if negative:
            options.append(3)
        if no_treatment:
            options.append(4)
        
        if options ==[]:
            raise ValueError("At least one treatment effect option must be True")
        # assigning which individual gets which kind of treatment effect 
        # from options 1-4
        if predefined_idx is not None:
            # Example
            # s.generate_treatment_effect(predefined_idx=np.repeat(1, 100)) # in case of custom index
            if len(predefined_idx) == self.N and isinstance(predefined_idx, (np.ndarray)):
                n_idx = predefined_idx
            else:
                raise ValueError('Predefined Index must be ndarray and length of Predefined Index must be {}!'.format(self.N))
        else:
            n_idx = np.random.choice(options, self.N, True)
        
        # array to fill up with theta values         
        theta_combined = np.zeros(self.N)
        
        if constant:
            # Option 1
            # Rules: Theta_0 = constant  (c) with c = 0.2
            # constant is independent from covariates 
            con = 0.2 #  constant value for treatment effect
            
            theta_combined[n_idx == 1] = con


        if heterogeneity:
            # Option 2
            # Rules:
            # (1) Apply trigonometric function
            # (2) Standardize the treatment effet within the interval [0.1, 0.3].
            # theta_0 is to be at most 30% of the baseline outcome g_0(X)
            
            # assigning randomly which covariates affect treatment effect
            r_idx = np.random.choice(options, size = self.k, replace = True)
            
            #(1) Trigonometric
            X_option2 = self.X[:,r_idx == 2].copy()
            
            w = np.random.normal(0,0.25,self.N)
            # Need to adjust weight_vector such that it complies with the alternated k (dimension)
            weight_vector_adj = self.weight_vector[r_idx == 2]
            
            gamma = np.sin(np.dot(X_option2, weight_vector_adj)) + w  # one gamma for each observation in n

            # (2) Standardize
            theta_option2 = standardize(gamma)
            
            theta_combined[n_idx == 2] = theta_option2[n_idx == 2]
            
        if negative:
            theta_combined[n_idx == 3] = np.random.uniform(-1, 0, np.sum(n_idx == 3))

        if no_treatment:
            theta_combined[n_idx == 4] = 0 # not really necessary since vector was full of 0 
        
        self.treatment_effect = theta_combined

        return None

    def generate_realized_treatment_effect(self):
        """
        Model-wise: Theta_0 * D
        :return:  Extract Treatment Effect where Treatment has been assigned
        """

        return self.get_treatment_effect() * self.get_treatment_assignment()

    def generate_noise(self):
        """
        model-wise: U or V
        Restriction: Expectation must be zero conditional on X, D.
        However, the expectation is independent anyways.
        :return: One-dim. array of normally distributed rv with 0 and 1
        """
        return np.random.normal(0, 1, self.N)

    def __str__(self):
        return "N = " + str(self.N) + ", k = " + str(self.k)
    
    def get_N(self):
        return self.N

    def get_k(self):
        return self.k
    
    def set_N(self, new_N):
        self.N = new_N

    def set_k(self, new_k):
        self.k = new_k
        
    def get_X(self):
        return self.X

    def get_g_0_X(self):
        return self.g_0_X

    def get_treatment_assignment(self):
        return self.D
    
    def get_treatment_effect(self):
        return self.treatment_effect
    


##### New class that includes SimData class by initizilaizing it internally and 
##### only displays a few simple functions to user

class UserInterface:
    '''
    Class to wrap up all functionalities and give user just the functions that are 
    necessary to create the wanted variables y, X, and treatment
    '''
    def __init__(self, N, k):
        '''
        Input:  N, Int with number of observations
                k, Int with number of covariates 
        
        Initilizes UserInterface class with number of observations N and number of covariates k.
        Generates Nxk matrix "X" with values for each covariate for all observations and saves 
        it in object s
        '''
        self.s = SimData(N, k)
        self.s.generate_covariates()
        
    def generate_treatment(self, random_assignment = True, constant = True, heterogeneous = True,
                                  negative = True, no_treatment = True, predefined_idx = None):
        '''
        Input:  random_assignment, Boolean to indicate if treatment assignment should be random 
                or dependent on covariates
                
                constant, Boolean allow for constant treatment effect 
                
                heterogeneous, Boolean allow for heterogeneous treatment effects that 
                depend on covariates
                
                negetive, Boolean allow treatment effects to be negetive, drawn from U[-1,0]
                
                no_treatment, Boolean allow treatment effect to be zero when assigned
                
                predefined_idx, Array-like object of length N, to assign treatment options individually 
                with respectivly numbers 1 to 4 for constant to no_treatment 
                
        
        Generates treatment assignment array "D" and treatment effect array "treatment_effect"
        ans saves them as self. internal variables in s 
        
        return: None
        '''
        self.s.generate_treatment_assignment()
        self.s.generate_treatment_effect(predefined_idx, constant, heterogeneous, 
                                         negative, no_treatment)

        return None

    def output_data(self):
        '''
        Generates output array "y" the following way: Y = Theta_0 * D + g_0(X) + U,
        where Theta_O is the treatment effect of each observation, D the dummy vector
        for assigning treatment, g_0() the non_linear transformation function, and U
        a normal-distributed noise-/error term
        
        return: y, X, treatment_effect
         '''                
        return self.s.generate_outcome_variable()
    
    def plot_covariates_correlation(self):
        '''
        Shows a correlation heatmap of the covariates 
        '''
        self.s.visualize_correlation()
        return None



##### still need to combine assigning and generation of treatment effects #####
# theta_combined[D==1]

# Of the following goals, discrete heterogeneity is still missing
# – No treatment effect (for all or for some people).
# – Constant (for all or for some people).
# – heterogeneity (discrete and continuous).
# – Even negative values seem realistic (for some people).
        
##### Also: It is not possible yet to get a heterogenous treatment effect for all
    # assigned individuals that just dependes on some covariates
    # Either Some heterogenous effects and some others (non, constant, negative) and just 
    # dependence on some covariates or
    # All heterogenous effects and depending on all covariates








