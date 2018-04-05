DIR=$1

if [ ! -d $DIR ]; then
  mkdir $DIR
else
  echo "$DIR exists already"
  exit 1
fi

cd $DIR

scp pi@192.168.178.214:captures_ms/* ./

mkdir extracts
ffmpeg -i car.h264 extracts/%09d.jpg

python ../reconcile.py

