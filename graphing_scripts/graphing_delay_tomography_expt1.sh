#!/bin/sh

# COLUMNS:
# depth, mean_delay, delay_distribution, error_tolerance, trials, i_max
#	$2		$3				$4								$5

# take file input (dont include file extension): 
# $./graphing_delay.sh inputfile depth mean_delay distribution num_samples

# Handle user CLI
if [ ! -f $1.txt ]; then
	echo No input file - dont include file extension;
	exit
fi

# Check user supplied 5 args
if [ ! $# -eq 5 ]; then
	echo Please provide the following arguments:
	echo inputfile depth mean_delay distribution num_samples
	echo depth - 2 3 or 4
	echo mean_delay - 1 2 3 4 5 6 7 or 8
	echo num_samples - 10000 50000 100000 500000 or 1000000
	exit
fi

# Check that num_trials is valid
if [ $5 != 10000 -a $5 != 50000 -a $5 != 100000 -a $5 != 500000 -a $5 != 1000000 ]; then
	echo Not a valid num of trials
	exit 0
fi

# to create the "edited down" version - removing extraneous lines (errors etc)
cat $1.txt | grep -v "stderr:" | grep -v "Traceback" | grep -v "======================" | grep -v "inferred probabilities" | grep -v "^[[:space:]]*$" > edited_$1.txt

# now create the csv with the comments/labels removed for gnuplot
cat edited_$1.txt | sed -e 's/python3 delay_tomography.py //' -e 's/  succeeded with stdout://' -e '/  failed with stdout:/ { d; }' | grep -v "i_max is" | sed -e 's/ \[/, /' -e 's/\]//' > final_$1.csv

# delete the "edited down" files - no longer needed
rm edited_$1.txt

# Create the tmp file with the specific experiment
let nodes=2**$2-1	# Nodes = 2^depth-1

# Get the N lines for each node AFTER the searched line - 1st line becomes label
cat final_$1.csv | grep "$2 $3 $4 0.5 $5" -A $nodes | grep -v "$2 $3 $4 0.5 $5" > tmp_$2_$3_$4_$5.csv

true_dist=()

# Generate Uniform true distribution
rm -rf delay_expt_results/*.png
if [[ $4 = "uniform" ]]; then

	res=$(awk -v d=$3 'BEGIN { print 1/ (2 * d) }')
	invres=$(awk -v d=$3 'BEGIN { print (2 * d) }')

	for ((i=1; i<=$nodes; i++)); do
		cat tmp_$2_$3_$4_$5.csv  | grep "^$i" | python3 preprocess.py $i | gnuplot -p -e "set term png; set title \"Node: $i\"; set xrange [0:$invres]; set yrange [0:*]; plot '-' u 1:2 w lines lw 3, ($res) lw 3" > delay_expt_results/Node_${i}_$2_$3_$4_$5.png 
		#| open -f -a /Applications/Preview.app

	done
	convert -append delay_expt_results/*.png output.png
fi

# Generate Geometric true distribution
if [[ $4 = "geometric" ]]; then
	p=$(awk -v d=$3 'BEGIN { print 1 / (d - 1) }')

	for ((i=1; i<=$nodes; i++)); do
		cat tmp_$2_$3_$4_$5.csv  | grep "^$i" | python3 preprocess.py $i | gnuplot -p -e "set term png; set title \"Node: $i\"; plot '-' u 1:2 w lines lw 3, ((1-$p)**x * $p) lw 3" > delay_expt_results/Node_${i}_$2_$3_$4_$5.png 
		#| open -f -a /Applications/Preview.app

	done
	convert -append delay_expt_results/*.png output.png
fi

# Cleanup tmp files
#rm tmp*
#rm final*