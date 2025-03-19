./lib/hq server start &

sleep 2

for i in {1..10}
do 
    ./lib/hq worker start &
done

for i in {20250301..20250310}
do 
    python3 ligen_simulated_campaign.py $seed &
    sleep 3
done
wait

./lib/hq server stop &