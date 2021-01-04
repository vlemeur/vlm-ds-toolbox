build:
	@docker build -t vlm_ds_toolbox -f Dockerfile .


start:
	@make clean
	@docker run -p 8888:8888 \
	  -v $(PWD)/notebooks:/notebooks \
	  --name vlm-ds-notebook \
	  -d vlm_ds_toolbox
	@docker logs -f vlm-ds-notebook


build_and_start:
	@make build
	@make start

clean:
	@docker stop vlm-ds-notebook || true && docker rm vlm-ds-notebook || true
