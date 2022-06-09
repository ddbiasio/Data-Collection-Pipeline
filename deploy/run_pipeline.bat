sudo docker pull siobhand/scraper:latest
sudo docker run -v $HOME/.aws/credentials:/root/.aws/credentials --name scraper --rm siobhand/scraper:latest --search=salmon --pages=1 
