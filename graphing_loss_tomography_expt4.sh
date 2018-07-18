#!/bin/sh

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
cat edited_$1.txt | sed -e 's/Depth = //' -e 's/expt_type = loss //' -e 's/ mean_delay_or_loss = /, /' -e 's/ dist_type =/,/' -e 's/ loss_probability = /, /' -e 's/ loss_type = /, /' -e 's/ num_probes = /, /' -e 's/ num_trials = /, /' -e 's/avg. tomography error =  /, /' -e 's/ %//' -e 's/avg. in-network error =  /, /' -e 's/ trials /,/' -e 's/ lower conf. int/,/' -e 's/ upper conf. int//' | sed -e 'N;N;s/\n/ /g' | sed -e 's/ //g' > final_$1.csv

# delete the "edited down" files - no longer needed
rm edited_$1.txt

# now to run individual experiments:

# Get unique loss probabilities - Working
lossprobs=( $(cat final_$1.csv | cut -d "," -f 2 | sort | uniq))

# Get unique num probes
numprobes_bern=( $(cat final_$1.csv | cut -d "," -f 4 | uniq | head -10))

# Separate based on distribution
cat final_$1.csv | grep "bernoulli" > tmp_bern_$1.csv

# Create graphs of probe convergence
for each in "${lossprobs[@]}"
do
	echo $each
	# bernoulli - create final file format then graph using gnuplot
	#cat tmp_bern_$1.csv | grep "$each,bernoulli" | cut -d "," -f 4,6,8 | sed -e 'N;N;s/\n/ /g' | sed -e 's/ /,/g' | cut -d "," -f-3,5-6,8- | grep -v "undef" > tmp_output.csv
	cat tmp_bern_$1.csv | cut -d "," -f 4,6,7,8,9,10,11,12,13 > tmp_output.csv

	gnuplot -persist <<-EOFMarker
		set term png
		set xlabel "Number of Packets"
		set ylabel "Error Rate (%)"
		set y2label "Number of Successful Trials (out of 100)"
		set key top right
		set datafile separator ","
		set yrange [0:]
		set y2range [0:100]
		set xrange [:1000]
		set y2tics
		set output "graphs_tmp/output.png"
		plot 'tmp_output.csv'  using 1:2:4:5  with yerrorlines axes x1y1 lw 3 lt 1 lc rgb "#e41a1c" title "Tomography error rate",\
			 'tmp_output.csv'  using 1:6:8:9  with yerrorlines axes x1y1 lw 3 lt 1 lc rgb "#041aac" title "in-network error rate" ,\
			 'tmp_output.csv'  using 1:3  with linespoints axes x1y2 lw 3 lt 1 lc rgb "#59A7ac" title "Tomography trial failures",\
		     'tmp_output.csv'  using 1:7  with linespoints axes x1y2 lw 3 lt 1 lc rgb "#faaaaa" title "in-network trial failures"
	EOFMarker
	#		     'tmp_output.csv'  using 1:4  with lines axes x1y1 lw 2 lt 1 lc rgb "#e41a1c" title "Upper confidence interval",\
	#			 'tmp_output.csv'  using 1:5  with lines axes x1y1 lw 2 lt 1 lc rgb "#e41a1c" title "Lower confidence interval",\

		#		     'tmp_output.csv'  using 1:8  with lines axes x1y1 lw 2 lt 1 lc rgb "#041aac" title "upper confidence interval" ,\
		#			 'tmp_output.csv'  using 1:9  with lines axes x1y1 lw 2 lt 1 lc rgb "#041aac" title "lower confidence interval" ,\
	
	mv graphs_tmp/output.png graphs_tmp/num_probes_with_bern_lossrate_$each.png
done

# Cleanup tmp files
#rm tmp*
rm final*

