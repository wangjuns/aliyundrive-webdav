FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install  -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple 

COPY . .

CMD [ "python", "app.py" ]
