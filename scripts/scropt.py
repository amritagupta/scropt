#!/usr/bin/python
import argparse
import SCRoptProblem

def main():
	"""This is the command-line facing driver for working with SCRoptProblem. The script takes command line arguments (which can come from a batch script),
	parses them, checks them, and then supplies them to a create a single LP. The LP is then solved using cplex (currently this is the only option for solving).
	"""
	parser = argparse.ArgumentParser(description='Run home range optimization for given parameters.')
	# arguments starting with - are interpreted as optional, but those marked as 'required' are so
	# in order to be able to pass the arguments in any order (i.e. not positional)
	parser.add_argument("-objective", type=str, required=True, help="Objective for home range optimization problem.")
	parser.add_argument("-budget", type=float, required=True, help="Budget for purchasing pixels. Default = 200.")
	parser.add_argument("-hrprop", type=float, required=True, help="If hrprop<=1 : minimum proportion of 95%% home range that must be conserved. If q>1 : minimum number of pixels in 95%% home range that must be conserved.")
	parser.add_argument("-landscape", type=str, required=True, help="Which landscape surface to use for the problem")
	parser.add_argument("-method", type=str, default="cplex", required=True, help="Which method to use to solve the problem. Default is cplex.")
	parser.add_argument("-secondary", type=str, required=False, help="Secondary objective function for pareto frontier experiment constraint.")
	parser.add_argument("-sconstrval", type=float, required=False, help="Minimum value for secondary objective in pareto frontier experiment.")
	# parser.add_argument("-runtimeparams", type = json.loads, required=True, help="Runtime parameters for cplex.")
	arguments = parser.parse_args()
	objective = arguments.objective
	budget = arguments.budget
	hrprop = arguments.hrprop
	landscape = arguments.landscape
	method = arguments.method
	secondary = arguments.secondary
	sconstrval = arguments.sconstrval

	# check that arguments are valid
	if objective not in ("rd", "pc", "dwc"):
		raise ValueError("Invalid optimization objective requested. Please choose from: rd, pc, dwc.")
	if hrprop > 1:
		raise ValueError("Only hrprop <= 1 has been implemented.")
	if method not in ("cplex"):
		raise ValueError("Only cplex solve method has been implemented.")
	if secondary:
		if secondary not in ("rd", "pc", "dwc"):
			raise ValueError("Invalid secondary optimization objective requested. Please choose from: rd, pc, dwc.")
		elif secondary == objective:
			raise ValueError("Primary and secondary optimization objectives should not be the same.")
		elif not sconstrval:
			raise ValueError("Secondary optimization objective requires a constraint value.")
		print("Arguments parsed: objective=%s, budget=%s, hrprop=%s, landscape=%s, method=%s, secondary=%s, sconstrval=%s") %(objective, budget, hrprop, landscape, method, secondary, sconstrval)
	else:	
		print("Arguments parsed: objective=%s, budget=%s, hrprop=%s, landscape=%s, method=%s") %(objective, budget, hrprop, landscape, method)

	# create and solve an SCRoptExperiment.Problem
	if secondary:
		problem = SCRoptProblem.ParetoProblem(objective, budget, hrprop, landscape, method, secondary, sconstrval)
		runtimeparams = {'cplexpath':'/opt/ibm/ILOG/CPLEX_Studio126/cplex/bin/x86-64_linux/cplex', 'timelimit': 432000, 'randomseed': 15, 'workmem': 20000, 'logfiledir':'/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/logfiles/', 'logfilename':'/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/logfiles/'+landscape+'_'+objective+'_'+str(budget)+'_pareto_'+secondary+'_'+str(sconstrval)+'.log', 'resultfilename': '/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/results/pareto/'+landscape+'_'+objective+'_'+str(budget)+'_'+secondary+'_'+str(sconstrval)+'.txt', 'workdir': '/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/lpandsolfiles/'}
	else:
		problem = SCRoptProblem.Problem(objective, budget, hrprop, landscape, method)
		runtimeparams = {'cplexpath':'/opt/ibm/ILOG/CPLEX_Studio126/cplex/bin/x86-64_linux/cplex', 'timelimit': 432000, 'randomseed': 15, 'workmem': 20000, 'logfiledir':'/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/logfiles/', 'logfilename':'/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/logfiles/'+landscape+'_'+objective+'_'+str(budget)+'.log', 'resultfilename': '/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/results/budget/'+landscape+'_'+objective+'_'+str(budget)+'.txt', 'workdir': '/home/fs01/ag2373/LandscapeConnectivity/SCROPT/output/lpandsolfiles/'}
	if not all (k in runtimeparams.keys() for k in ('cplexpath', 'timelimit', 'randomseed', 'workmem', 'logfiledir', 'logfilename', 'resultfilename', 'workdir')):
		raise ValueError("One or more runtimeparams missing. Need to provide:\ncplexpath\ntimelimit\nrandomseed\nworkmem\nlogfiledir\nlogfilename\nresultfilename\nworkdir.")
	problem.runcplex(runtimeparams)

if __name__ == '__main__':
	main()