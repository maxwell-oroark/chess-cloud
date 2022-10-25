deploy_container:
	docker build -t chess-cloud . && docker tag chess-cloud gcr.io/chess-365123/chess && docker push gcr.io/chess-365123/chess && gcloud run deploy chess --image gcr.io/chess-365123/chess:latest
deploy_scheduled:
	cd scheduled && gcloud functions deploy scheduled --runtime=python39 --trigger-topic=lichess --entry-point=query_games
deploy_report:
	cd report && gcloud functions deploy generateReport --runtime nodejs16 --trigger-resource analyzed_games --trigger-event google.storage.object.finalize --set-env-vars SLACK_URL=https://hooks.slack.com/services/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
