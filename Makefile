start:
	@make clean
	@docker build -t vlm_ds_toolbox -f Dockerfile .
	@docker run -p 8888:8888 \
	  -v $(PWD)/notebooks:/home/jovyan/work \
	  --name vlm-ds-notebook \
	  -d vlm_ds_toolbox
	  -e JUPYTER_ENABLE_LAB=yes
	@docker logs -f vlm-ds-notebook

clean:
	@docker stop vlm-ds-notebook || true && docker rm vlm-ds-notebook || true