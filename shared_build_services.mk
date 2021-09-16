test: reqs
	python3 -m pytest -vv -s

reqs:
	pip3 install -r ../../base_requirements.txt

run:
	python3 -m $(SERVICE).app

docker:
	docker build --build-arg example=$(APP) -t $(APP):configuration ../../..
	docker build -t $(APP)_$(SERVICE) . 

docker-run: docker
	docker run -p $(PORT):$(PORT) -t $(APP)_$(SERVICE) 

docker-rebuild:
	docker build --rm=true --force-rm=true --no-cache=true -t $(APP)_$(SERVICE) .

start:
	tmux new-window -t application -n $(SERVICE) -d 'coverage run --parallel-mode -m $(SERVICE).app'