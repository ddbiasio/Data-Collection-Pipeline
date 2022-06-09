sudo docker pull siobhand/scraper:latest
sudo docker run -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_REGION=$AWS_REGION --name scraper --rm scraper --search=lobster --pages=1
