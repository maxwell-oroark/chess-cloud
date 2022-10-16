deploy_container:
	docker build -t chess-cloud . && docker tag chess-cloud gcr.io/chess-365123/chess && docker push gcr.io/chess-365123/chess && gcloud run deploy chess --image gcr.io/chess-365123/chess:latest
deploy_function:
	cd scheduled && gcloud functions deploy scheduled --runtime=python39 --trigger-topic=lichess --entry-point=query_games