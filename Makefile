start:
	@make clean
	@docker build -t vlm_ds_toolbox -f Dockerfile .
	@docker run -p 8888:8888 \
	  -v $(PWD)/notebooks:/home/jovyan/work \
	  --name vlm-ds-notebook \
	  -e JUPYTER_ENABLE_LAB=yes \
	  -d vlm_ds_toolbox



clean:
	@docker stop vlm-ds-notebook || true && docker rm vlm-ds-notebook || true