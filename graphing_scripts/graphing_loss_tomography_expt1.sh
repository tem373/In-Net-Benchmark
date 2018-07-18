#!/bin/sh

#set -e

# COLUMNS:
# Depth,Loss%,Distr,Probes,Trials,tomo_err,tomo_trials,innet_err,innet_trials

# take file input (dont include file extension): 
# $./graphing.sh inputfile

# Handle user CLI
if [ ! -f $1.txt ]; then
	echo No input file;
	exit
fi

# to create the "edited down" version - removing extraneous lines
cat $1.txt | grep -v "sanity" | grep -v "Condition" | grep -v "succeeded with" | grep -v "^[[:space:]]*$" | grep -v "============" > edited_$1.txt

# now create the csv or whatever version files
cat edited_$1.txt | sed -e 's/Depth = //' -e 's/ loss_probability = /, /' -e 's/ loss_type = /, /' -e 's/ num_probes = /, /' -e 's/ num_trials = /, /' -e 's/avg. tomography error =  /, /' -e 's/ %//' -e 's/avg. in-network error =  /, /' -e 's/ trials//' | sed -e 'N;N;s/\n/ /g' | sed -e 's/ //g' > final_$1.csv

# delete the "edited down" files - no longer needed
rm edited_$1.txt

# now to run individual experiments:

# Get unique loss probabilities - Working
lossprobs=( $(cat final_$1.csv | cut -d "," -f 2 | uniq))

# Get unique num probes
numprobes=( $(cat final_$1.csv | cut -d "," -f 4 | sort | uniq))

# Separate based on distribution
cat final_$1.csv | grep "bernoulli" > tmp_bern_$1.csv
cat final_$1.csv | grep "gilbert_elliot" > tmp_ge_$1.csv

# Create graphs of probe convergence
# BERNOULLI - LOSS RATES
for each in "${numprobes[@]}"
do
	# bernoulli - create final file format then graph using gnuplot
	#TODO: prepend labels to file
	cat tmp_bern_$1.csv | grep "$each,100," | cut -d "," -f 2,6,8 | sed -e 'N;N;s/\n/ /g' | sed -e 's/ /,/g' | cut -d "," -f-3,5-6,8- | grep -v "undef" > tmp_output.csv
	
	gnuplot -persist <<-EOFMarker
		set terminal png
		set datafile separator ","
		set output "graphs/output.png" 
		plot 'tmp_output.csv' using 1:2 with lines title "Depth 3/Tomography", 'tmp_output.csv' using 1:3 with lines title "Depth 3/In-Network", 'tmp_output.csv' using 1:4 with lines title "Depth 4/Tomography", 'tmp_output.csv' using 1:5 with lines title "Depth 4/In-Network", 'tmp_output.csv' using 1:6 with lines title "Depth 5/Tomography", 'tmp_output.csv' using 1:7 with lines title "Depth 5/In-Network"
	EOFMarker
	
	mv graphs/output.png graphs/lossrates_with_bern_probes_$each.png
done
	
# GILBERT-ELLIOT - LOSS RATES
for each in "${numprobes[@]}"
do
	#TODO: prepend labels to file
	cat tmp_ge_$1.csv | grep "$each,100," | cut -d "," -f 2,6,8 | sed -e 'N;N;s/\n/ /g' | sed -e 's/ /,/g' | cut -d "," -f-3,5-6,8- | grep -v "undef" > tmp_output.csv
	
	gnuplot -persist <<-EOFMarker
		set terminal png
		set datafile separator ","
		set output "graphs/output.png" 
		plot 'tmp_output.csv' using 1:2 with lines title "Depth 3/Tomography", 'tmp_output.csv' using 1:3 with lines title "Depth 3/In-Network", 'tmp_output.csv' using 1:4 with lines title "Depth 4/Tomography", 'tmp_output.csv' using 1:5 with lines title "Depth 4/In-Network", 'tmp_output.csv' using 1:6 with lines title "Depth 5/Tomography", 'tmp_output.csv' using 1:7 with lines title "Depth 5/In-Network"
	EOFMarker
	
	mv graphs/output.png graphs/lossrates_with_GE_probes_$each.png

done

# BERNOULLI - PROBE COUNTS

for each in "${lossprobs[@]}"
do
	# bernoulli - create final file format then graph using gnuplot
	cat tmp_bern_$1.csv | grep "$each,bernoulli" | cut -d "," -f 4,6,8 | sed -e 'N;N;s/\n/ /g' | sed -e 's/ /,/g' | cut -d "," -f-3,5-6,8- | grep -v "undef" > tmp_output.csv

	gnuplot -persist <<-EOFMarker
		set terminal png
		set datafile separator ","
		set output "graphs/output.png" 
		plot 'tmp_output.csv' using 1:2 with lines title "Depth 3/Tomography", 'tmp_output.csv' using 1:3 with lines title "Depth 3/In-Network", 'tmp_output.csv' using 1:4 with lines title "Depth 4/Tomography", 'tmp_output.csv' using 1:5 with lines title "Depth 4/In-Network", 'tmp_output.csv' using 1:6 with lines title "Depth 5/Tomography", 'tmp_output.csv' using 1:7 with lines title "Depth 5/In-Network"
	EOFMarker
	
	mv graphs/output.png graphs/num_probes_with_bern_lossrate_$each.png
done

# GILBERT-ELLIOT - PROBE COUNTS
for each in "${lossprobs[@]}"
do
	cat tmp_ge_$1.csv | grep "$each,gilbert_elliot" | cut -d "," -f 4,6,8 | sed -e 'N;N;s/\n/ /g' | sed -e 's/ /,/g' | cut -d "," -f-3,5-6,8- | grep -v "undef" > tmp_output.csv

	gnuplot -persist <<-EOFMarker
		set terminal png
		set logscale
		set datafile separator ","
		set output "graphs/output.png" 
		plot 'tmp_output.csv' using 1:2 with lines title "Depth 3/Tomography", 'tmp_output.csv' using 1:3 with lines title "Depth 3/In-Network", 'tmp_output.csv' using 1:4 with lines title "Depth 4/Tomography", 'tmp_output.csv' using 1:5 with lines title "Depth 4/In-Network", 'tmp_output.csv' using 1:6 with lines title "Depth 5/Tomography", 'tmp_output.csv' using 1:7 with lines title "Depth 5/In-Network"
	EOFMarker

	mv graphs/output.png graphs/num_probes_with_ge_lossrate_$each.png
done

# Cleanup tmp files
rm tmp*
rm final*

