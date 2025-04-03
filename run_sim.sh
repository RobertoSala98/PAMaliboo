for seed in {20250301..20250310}
do 
    python3 ligen_simulated_campaign.py $seed &
done
wait