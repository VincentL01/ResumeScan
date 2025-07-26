FROM python:3.12-alpine

WORKDIR /resume-scan

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]
