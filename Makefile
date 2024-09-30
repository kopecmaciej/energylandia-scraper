REPO_NAME=energylandia-scraper
VERSION=latest
PORT=8080

docker-build:
	- docker stop $(REPO_NAME)
	- docker rm $(REPO_NAME)
	- docker rmi $(REPO_NAME):$(VERSION) 
	- docker build -t $(REPO_NAME):$(VERSION) .

docker-run:
	docker run --name $(REPO_NAME) -p $(PORT):$(PORT) $(REPO_NAME):$(VERSION)

docker-push: require-repository
	docker tag $(REPO_NAME):$(VERSION) $(REPOSITORY)/$(REPO_NAME):$(VERSION)
	docker push $(REPOSITORY)/$(REPO_NAME):$(VERSION)

require-repository:
	@if (test -z $(REPOSITORY)); then echo "REPOSITORY is required"; exit 1; fi
