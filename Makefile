start:
	@make clean
	@docker build -t vlm_ds_toolbox -f Dockerfile .
	@docker run -p 8888:8888 \
	  -v $(PWD)/notebooks:/notebooks \
	  --name vlm-ds-notebook \
	  -d vlm_ds_toolbox
	@docker logs -f vlm-ds-notebook


clean:
	@docker stop vlm-ds-notebook || true && docker rm vlm-ds-notebook || true
