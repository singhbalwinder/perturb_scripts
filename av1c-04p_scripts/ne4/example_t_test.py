import numpy as np
from scipy.stats import ttest_ind, ttest_ind_from_stats
from scipy.special import stdtr


# Create sample data.
#a = np.random.randn(40)
#b = np.random.randn(40)

a = [10, 20, 30 ,40 ,50, 40, 30 ,20]
b = [100, 200, 300 ,400 ,500, 400, 300 ,200]

# Use scipy.stats.ttest_ind.
t, p = ttest_ind(a, b, equal_var=False)
print("ttest_ind:            t = %g  p = %g" % (t, p))
