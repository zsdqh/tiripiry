import functools
import time

from peewee import *

db = SqliteDatabase("Products.db")


class Product(Model):
    name = CharField()
    ID = IntegerField(null=False, primary_key=True)
    prots = FloatField(null=True)
    carbs = FloatField(null=True)
    fats = FloatField(null=True)
    callories = IntegerField(null=True)
    photo = CharField()

    class Meta:
        database = db

    def to_str(self, mul=1):
        return (f"{self.name} {int(mul * 100)}г"
                f"\n  Калории: {round(self.callories * mul, 2)}"
                f"\n    Белки: {round(self.prots * mul, 2)}"
                f"\n    Жиры: {round(self.fats * mul, 2)}"
                f"\n    Углеводы: {round(self.carbs * mul, 2)}")


# req = requests.get("https://www.sochetaizer.ru/goods/caloricity?page=28")
# soup = BeautifulSoup(req.text, 'html.parser')
# divs = soup.find_all('div', class_='goods-table-row')
# divs.pop(0)
#
# for div in divs[4:]:
#     div_image = div.find('div', class_="goods-table-image").get('style')
#     div_image= div_image[div_image.index('\'')+1:]
#     div_image=div_image[:div_image.index('\'')]
#     photo_URL = base+div_image
#     id_ = div['data-id']
#     with open(f"images\\{id_}.jpg", "wb") as file:
#         photo = requests.get(photo_URL)
#         file.write(photo.content)
#     text = div.get_text()
#     ind = text.find("ккал")
#     calories="".join(list(filter(lambda a: a.isdigit(),text[ind-3:ind])))
#     cfp = text[ind+4:-1]
#     name=text[:ind-len(calories)]
#     p, f, c = cfp.split("г")
#     Product.create(name=name, ID=id_,prots=p, carbs=c, fats=f, callories=calories, photo=f"images\\{id_}.jpg")

# for prod in Product.select().where(Product.name.contains(".")):
#     num=""
#     if prod.name.endswith("."):
#         prod.name = prod.name[:len(prod.name)-1]
#     while list(prod.name)[-1].isdigit():
#         num+=list(prod.name)[-1]
#         prod.name = prod.name[:len(prod.name)-1]
#     num = num[::-1]
#     if num!="":
#         prod.callories = int(num)
#     prod.save()


