mysql = {'host': 'localhost',
         'user': 'root',
         'passwd': 'sparity@123',
         'db': 'productdb'}

redis={"host":"localhost", "port":"6379", "db":"0"}

model_dir="./models/model_20170710-064728"
Rest_url='http://34.205.176.103:3000/api/configurations/'
selectQuery='select id,title,link,image_link,size from productdb.ecommdemofeed  where '
countQuery='select count(*) from productdb.ecommdemofeed where '
topsTitle="title like '%T-Shirt%' and age_group='adult' "
bottomsTitle="title like '% pant%' and age_group='adult' "
sleepWearTitle="title like  '% union suit%' and age_group='adult'  "
blanketsTitle=" title like '% blanket%'  "
boysBottomsTitle=" title like '% Pant%'  and gender in ('male','unisex')  and age_group='kids'"
girlsBottomsTitle=" title like '% Pant%'  and gender in ('female','unisex')  and age_group='kids'"
girlsTopsTitle=" title like '% t-shirt%'  and gender in ('female','unisex')  and age_group='kids'"
boysTopsTitle=" title like '% t-shirt%'  and gender in ('male','unisex')  and age_group='kids'"
infantsTitle=" title like '% Onesies%'  "

