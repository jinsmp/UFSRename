if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/ufscrazybotz/UFSRename /UFSBotz
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /UFSBotz
fi
cd /UFSBotz
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 main.py
