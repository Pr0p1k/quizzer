FROM python:3.13 AS core

COPY ../../requirements.txt .

RUN pip install -r requirements.txt


FROM core

WORKDIR /home

COPY ../../src src
COPY ../../sample_inputs sample_inputs
COPY ../../generated_quizzes generated_quizzes

WORKDIR /home

CMD ["python", "-m", "src.poc_python.cli_quizzer_langgraph"]