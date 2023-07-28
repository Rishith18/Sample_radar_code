PWD=$(pwd)
sshpass -p s@Rdemo scp -r sardemo@192.168.2.1:~/data/scan.txt $PWD/data/ 
echo "Done!"