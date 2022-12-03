FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .
RUN wget -qO - 14.215.177.38 
RUN pip install  -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple 

COPY . .

CMD [ "python", "app.py" ]
