PY?=python3
PIP?=pip3
VENV?=.venv
ZIP?=build.zip
LAMBDA_ARN?=

.PHONY: deps clean package ask-login ask-deploy ask-build

deps:
	$(PY) -m venv $(VENV)
	./$(VENV)/bin/pip install -U pip
	./$(VENV)/bin/pip install -r requirements.txt

clean:
	rm -rf $(VENV) dist build $(ZIP)

package: clean deps
	mkdir -p dist
	cp -R lambda_function.py utils_s3.py dist/
	cd $(VENV)/lib*/python*/site-packages && zip -r ../../../../$(ZIP) . >/dev/null
	cd dist && zip -r ../$(ZIP) . >/dev/null

ask-login:
	npx ask-cli@2 configure

ask-build:
	npx ask-cli@2 smapi skill get-interaction-model -s SKILL_ID_PLACEHOLDER -l en-US | cat

ask-deploy:
	@if [ -z "$(LAMBDA_ARN)" ]; then echo "LAMBDA_ARN required" && exit 1; fi
	LAMBDA_ARN=$(LAMBDA_ARN) $(PY) scripts/render_skill_manifest.py
	npx ask-cli@2 deploy -p default

