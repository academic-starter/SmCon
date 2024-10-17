for gz_file in $(ls mbt_rand_trial-*.tar.gz)
do 
echo $gz_file
tar -xf $gz_file
python3 coverage_count.py
mv cov_seq.csv cov_seq.csv.$gz_file
done 
