PWD=$(pwd)
sshpass -p s@Rdemo scp -r $PWD/src sardemo@192.168.2.1:~/sar/
echo "Done!"