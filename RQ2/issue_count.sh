for gz_file in $(ls mbt_rand_trial-*.tar.gz)
do 
echo $gz_file
tar -xf $gz_file
for rand_file in $(ls random_myth*.log)
do 
    echo $rand_file
    cat $rand_file|grep "In file:"|sort|uniq|wc -l
done

for mbt_file in $(ls mbt_myth*.log)
do  
    echo $mbt_file
    cat $mbt_file|grep "In file:"|sort|uniq|wc -l
done 

done 
