import subprocess
import sys

# Program wrapper
# Takes a command line of program arguements,
# executes it, and prints something out whether it succeeds or fails
def program_wrapper(program, t_stdout = subprocess.PIPE, t_stderr = subprocess.PIPE):
  sp = subprocess.Popen(program, stdout = t_stdout, stderr = t_stderr)
  out, err = sp.communicate()
  if (sp.returncode != 0):
    print(" ".join(program), " failed with stdout:")
    print(out)
    print("stderr:")
    print(err)
    #sys.exit(sp.returncode)
    return (out, err)
  else :
    print(" ".join(program), " succeeded with stdout:")
    print(out.decode("utf-8"))
    sys.stdout.flush()
    return (out, err)

error_tolerance = 0.5

for delay_avg in [1, 2, 3, 4, 5, 6, 7, 8]:
  for num_samples in [10000, 50000, 100000, 500000, 1000000]:
    for depth in [2, 3, 4]:
      cmd1 = ["python3", "delay_tomography.py", str(depth), str(delay_avg), "geometric", str(error_tolerance), str(num_samples)]
      cmd2 = ["python3", "delay_tomography.py", str(depth), str(delay_avg), "uniform", str(error_tolerance), str(num_samples)]
      program_wrapper(cmd1)
      print("===========================================================================================")
      program_wrapper(cmd2)
      print("===========================================================================================")


