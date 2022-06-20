Install:

-> git clone https://github.com/matveyDev/order_tracker

-> docker-compose up --build

-> http://localhost:3000/

-> GoogleSheets: https://docs.google.com/spreadsheets/d/14Li0oPRY8LWMqmBZLruoR1BGX2zpBdSUoKQST-KQF54/edit#gid=0

<img width="508" alt="image" src="https://user-images.githubusercontent.com/99687428/174513026-1a9362f9-2b0f-47de-8187-b588b9c8de0b.png">

PS: Не упаковал в докер Celery (Через него отправляются уведомления в телегу (@orderNotifier)

Если возникают ошибки:

1) cd /backend/ -> В app.py на 49 строке убрать host='0.0.0.0' ;

2) Проблемы с портами (6379 , 3000, 5001 , 8080 , 5432):

-> sudo lsof -i :PORT_NUMBER (e.g. 3000) 

-> sudo kill PID_NUMBER



<img width="1786" alt="image" src="https://user-images.githubusercontent.com/99687428/174512848-9852f708-9d64-4f61-a42f-111b09777cb7.png">
