PY?=python3
PIP?=pip3
VENV?=.venv
ZIP?=build.zip
LAMBDA_ARN?=

.PHONY: deps clean package ask-login ask-deploy ask-build backup-skill backup-lambda deploy-all

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

backup-skill:
	@if [ -z "$(SKILL_ID)" ]; then echo "SKILL_ID required" && exit 1; fi
	mkdir -p backups/skill
	npx ask-cli@2 smapi get-skill -s $(SKILL_ID) > backups/skill/skill.json
	npx ask-cli@2 smapi get-interaction-model -s $(SKILL_ID) -l en-US > backups/skill/en-US.json || true
	npx ask-cli@2 smapi get-interaction-model -s $(SKILL_ID) -l en-GB > backups/skill/en-GB.json || true
	npx ask-cli@2 smapi get-interaction-model -s $(SKILL_ID) -l en-CA > backups/skill/en-CA.json || true
	npx ask-cli@2 smapi get-interaction-model -s $(SKILL_ID) -l en-AU > backups/skill/en-AU.json || true

backup-lambda:
	@if [ -z "$(LAMBDA_FUNCTION_NAME)" ]; then echo "LAMBDA_FUNCTION_NAME required" && exit 1; fi
	mkdir -p backups/lambda
	aws lambda get-function --function-name $(LAMBDA_FUNCTION_NAME) > backups/lambda/get-function.json
	aws lambda get-function --function-name $(LAMBDA_FUNCTION_NAME) --query 'Code.Location' --output text | xargs curl -o backups/lambda/code.zip

deploy-all:
	@if [ -z "$(LAMBDA_ARN)" ]; then echo "LAMBDA_ARN required" && exit 1; fi
	$(MAKE) package
	aws lambda update-function-code --function-name $(LAMBDA_FUNCTION_NAME) --zip-file fileb://$(ZIP)
	LAMBDA_ARN=$(LAMBDA_ARN) $(PY) scripts/render_skill_manifest.py
	npx ask-cli@2 deploy -p default

