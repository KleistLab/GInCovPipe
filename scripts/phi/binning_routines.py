import numpy as np
import pandas as pd
from itertools import chain
from scipy import optimize


def get_phi(x, n_haplo, n_mut):
  """Objective function to be minimised inferring the optimal value for phi.

  :param x: The parameter to be minimised.
  :type x: float
  :param n_haplo: Number of haplotypes.
  :type n_haplo: int
  :param n_mut: Number of mutant sequences.
  :type n_mut: int
  :returns: The result of the objective function with the given parameters.
  :rtype: float
  """
  return (n_haplo-(x*np.log(1+n_mut/x)))**2 

def optim(n_haplo, n_mut):
  """
  Optimise function, calling the scipy optimizer with metheod "Nelder-Mead".

  :param n_haplo: Number of haplotypes.
  :type n_haplo: int
  :param n_mut: Number of mutant sequences.
  :type n_mut: int
  :returns: Optimal value of the objective function with the given parameters.
  :rtype: float
  """

  # If no data available -- set estimate to zero
  if (n_haplo==0) or (n_mut==0):
      return 0
  # If more haployptes than mutants, no clear answer can be given (very low sampling). Hence not evaluable
  elif n_haplo >= n_mut:
      return np.nan
  # Else optimize with Nelder-Mead
  else:
      x0 = 1
      sol = optimize.minimize(get_phi, x0=x0, method='Nelder-Mead', args=(n_haplo,n_mut))
      return sol.x[0]


def optim_2(n_haplo, n_mut):
  """
  Optimise function, calling the scipy optimizer with metheod "L-BFGS-B".

  :param n_haplo: Number of haplotypes.
  :type n_haplo: int
  :param n_mut: Number of mutant sequences.
  :type n_mut: int
  :returns: Optimal value of the objective function with the given parameters.
  :rtype: float
  """

  # If no data available -- set estimate to zero
  if n_haplo==0 or n_mut==0:
      return 0
  # If more haployptes than mutants, no clear answer can be given (very low sampling). Hence not evaluable
  elif n_haplo >= n_mut:
      return np.nan
  # Else optimize with trust-constr option to keep evaluation in feasible region
  else:
      x0 = 1
      #sol = optimize.minimize(self._fmle, x0=x0, method='trust-constr', args=(nu,ns), constraints=con1)
      # use least squares without MLE
      sol = optimize.minimize(get_phi, x0=x0, method='L-BFGS-B', args=(n_haplo,n_mut))
      return sol.x[0]

def optim_3(n_haplo, n_mut):
  """
  Optimise function, calling the scipy optimizer with metheod "trust-constr".

  :param n_haplo: Number of haplotypes.
  :type n_haplo: int
  :param n_mut: Number of mutant sequences.
  :type n_mut: int
  :returns: Optimal value of the objective function with the given parameters.
  :rtype: float
  """
  # Constraint
  con1 = {'type': 'ineq', 'fun': lambda x: x}
  # If no data available -- set estimate to zero
  if n_haplo==0 or n_mut==0:
      return 0
  # If more haployptes than mutants, no clear answer can be given (very low sampling). Hence not evaluable
  elif n_haplo >= n_mut:
      return np.nan
  # Else optimize with trust-constr option to keep evaluation in feasible region
  else:
      x0 = 1
      #sol = optimize.minimize(self._fmle, x0=x0, method='trust-constr', args=(nu,ns), constraints=con1)
      # use least squares without MLE
      sol = optimize.minimize(get_phi, x0=x0, method='trust-constr', args=(n_haplo,n_mut), constraints=con1)
      return sol.x[0]


def infer_bin_attributes(subsample_table): 
  """
  Infer the attributes for a bin according to the affiliated sequences.

  :param subsample_table: Table containing sequence information with (date), time t and snvs (in string format).
  :type subsample_table: pandas.dataFrame
  :returns: Table containing the attributes of the bin, including: TODO
  :rtype: dict
  """

  from_t = subsample_table['t'].dropna().min()
  to_t = subsample_table['t'].dropna().max()
  d = to_t-from_t+1 
  N_seq = len(subsample_table)
  num_mut = N_seq - (subsample_table['snvs'] == "").sum()
  haplos = set(subsample_table['snvs'])
  #new_haplos = haplos[!haplos %in% actual_haplos]
  n_haplos= len(haplos)
  #new_haplotypes = length(new_haplos)
  muts = set(list(chain.from_iterable(subsample_table['snvs'].str.split())))
  #new_muts = muts[!muts %in% actual_muts]
  n_mut_types = len(muts)
  #n_new_muts = length(new_muts)

  w=1/(np.log(np.sqrt(d))+1)
  bin_t = round(subsample_table['t'].mean())
  #bin_t_mid = from_t+round((to_t-from_t)/2)
  bin_t_sd = subsample_table['t'].std()
  phi = optim(n_haplo=n_haplos/d, n_mut=num_mut/d)
  #phi_2 = optim_2(n_haplo=n_haplos/d, n_mut=num_mut/d)
  #phi_3 = optim_3(n_haplo=n_haplos/d, n_mut=num_mut/d)

  return {'t': [bin_t],'t_sd': [bin_t_sd],'phi': [phi],'sampleSize': [N_seq],'num_mut': [num_mut],'daysPerBin': [d],'haplotypes': [n_haplos],'n_mut_types': [n_mut_types]}


def binning_equal_days(seq_info_short_table, days):
  
  #print("*************************\n")
  print(" ", days , " days\n")
  #print("*************************\n")
  
  phi_per_bin_table_days = pd.DataFrame()

  from_t=min(seq_info_short_table['t'])
  to_t=from_t+days-1

  while to_t < max(seq_info_short_table['t']):
    subsample_table = seq_info_short_table[(seq_info_short_table['t']>=from_t) & (seq_info_short_table['t']<=to_t)]
    # Add check for empty df
    if not subsample_table.empty:
      phi_per_bin = infer_bin_attributes(subsample_table)
      phi_per_bin.update({"binning": "eq_days_" + str(days)}) 
      phi_per_bin_table_days = pd.concat([phi_per_bin_table_days,pd.DataFrame(phi_per_bin)], ignore_index=True) 

    # next bin
    from_t+=days
    to_t+=days


  return phi_per_bin_table_days


def binning_equal_size(seq_info_short_table, s):
  
  #print("*************************\n")
  print(" ", s , " sequences\n")
  #print("*************************\n")

  # just in case, re-index the df
  seq_info_short_table = seq_info_short_table.reset_index()
  
  phi_per_bin_table_size = pd.DataFrame()
  
  from_t=0
  to_t=0
  actual_index = 0
  
  while (to_t < max(seq_info_short_table['t'])) & ((actual_index+s) <= len(seq_info_short_table)):
    
    #CHECK AGAIN or rather start at one t and add as many seqences from here? 
    #fastest way (numpy) to get the first occurrence of value "from"
    actual_index = seq_info_short_table['t'].values.searchsorted(from_t)
    subsample_table= seq_info_short_table.iloc[actual_index:min(actual_index+s, len(seq_info_short_table))]
    #actual_index <- actual_index + s
    to_t=max(subsample_table['t'])
    
    #TODO: maybe also subsample if one day has more than seq sequences? 
    # if bin is just a subset of one day, take all of the day
    if from_t == to_t:
      subsample_table = seq_info_short_table[seq_info_short_table['t'] == to_t] 
    
  
    phi_per_bin = infer_bin_attributes(subsample_table)
    phi_per_bin.update({"binning": "eq_size_" + str(s)}) 

    #phi_per_bin_table_size = phi_per_bin_table_size.append(phi_per_bin, ignore_index=True)
    phi_per_bin_table_size = pd.concat([phi_per_bin_table_size,pd.DataFrame(phi_per_bin)], ignore_index=True)
  
    from_t=to_t+1
  return phi_per_bin_table_size



def calculate_phi_per_bin(seq_info_short_table, seqs_per_bin, days_per_bin):

  minDate = min(seq_info_short_table['date'].dropna())

  phi_per_bin_table = pd.DataFrame()

  for days in days_per_bin:
    #phi_per_bin_table =  phi_per_bin_table.append(binning_equal_days(seq_info_short_table, days))
    phi_per_bin_table =  pd.concat([phi_per_bin_table,binning_equal_days(seq_info_short_table, days)])

  for s in seqs_per_bin:
    #phi_per_bin_table = phi_per_bin_table.append(binning_equal_size(seq_info_short_table, s))
    phi_per_bin_table = pd.concat([phi_per_bin_table,binning_equal_size(seq_info_short_table, s)])
  
  # remove invalid phi estimates
  phi_per_bin_table = phi_per_bin_table.dropna().reset_index(drop=True)
  #phi_per_bin.table <- phi_per_bin.table %>% mutate(date = ginpiper::daysAsDate(days = t, minDate = minDate))
  #calculate date from min date adding t days
  phi_per_bin_table['date'] = pd.to_timedelta(phi_per_bin_table['t'], 'days') + pd.to_datetime(minDate) 
  
  #sort by date
  phi_per_bin_table = phi_per_bin_table.sort_values(by='date')

  return phi_per_bin_table
