import os

countries_order = ['Казахстан', 'Россия', 'Таджикистан', 'Узбекистан', 'Другие страны', 'Международные']
countries = ['Казахстан', 'Международные', 'Узбекистан', 'Таджикистан']
countries.sort(key=lambda x: countries_order.index(x))
print(countries)

os.remove('D:\\Projects\\Release\\Log.log')
f = open ('D:\\Projects\\Release\\Log.log', 'a')
f.write('src_path\tdst_path')
