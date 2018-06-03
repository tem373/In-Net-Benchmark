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
    sys.exit(sp.returncode)
  else :
    print(out.decode("utf-8"))
    sys.stdout.flush()
    return (out, err)

for loss in range(1, 10, 1):
  for num_samples in [100, 1000, 10000, 100000]:
    for depth in [3, 4, 5]:
      cmd1 = ["./tomography.py", str(depth), str(loss/100.0), "bernoulli", str(num_samples), "100"]
      cmd2 = ["./tomography.py", str(depth), str(loss/100.0), "gilbert_elliot", str(num_samples), "100"]
      program_wrapper(cmd1)
      program_wrapper(cmd2)
