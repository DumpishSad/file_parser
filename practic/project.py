import os
import csv
from operator import itemgetter


class PriceMachine:

    def __init__(self):
        self.data = []


    def load_prices(self, folder_path='.'):
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
        """
        files = [f for f in os.listdir(folder_path) if 'price' in f.lower() and f.endswith('.csv')]
        for file in files:
            file_path = os.path.join(folder_path, file)

            with open(file_path, 'r', encoding='utf-8', errors='replace') as csvfile:
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)

                reader = csv.reader(csvfile, delimiter=dialect.delimiter)
                headers = next(reader)

                name_col, price_col, weight_col = self._search_product_price_weight(headers)

                for row in reader:
                    try:
                        name = row[name_col].strip()
                        price = float(row[price_col].replace(',', '.').strip())
                        weight = float(row[weight_col].replace(',',
                                                               '.').strip())
                        price_per_kg = price / weight
                        self.data.append({
                            'name': name,
                            'price': price,
                            'weight': weight,
                            'file': file,
                            'price_per_kg': price_per_kg
                        })
                    except (ValueError, IndexError):
                        continue


    def _search_product_price_weight(self, headers):
        """
            Возвращает индексы столбцов: название товара, цена, вес.
        """
        name_variants = ['название', 'продукт', 'товар', 'наименование']
        price_variants = ['цена', 'розница']
        weight_variants = ['фасовка', 'масса', 'вес']

        name_col = price_col = weight_col = None

        for i, header in enumerate(headers):
            header_lower = header.strip().lower()
            if header_lower in name_variants:
                name_col = i
            elif header_lower in price_variants:
                price_col = i
            elif header_lower in weight_variants:
                weight_col = i

        return name_col, price_col, weight_col


    def export_to_html(self, fname='output.html'):
        """
            Экспортирует текущие данные в HTML-таблицу.
        """
        result = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table border="1">
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        """

        for i, item in enumerate(self.data, 1):
            result += f'''
                <tr>
                    <td>{i}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.1f}</td>
                </tr>
            '''

        result += """
            </table>
        </body>
        </html>
        """

        with open(fname, 'w') as f:
            f.write(result)
        print(f"Данные успешно экспортированы в файл {fname}")


    def find_text(self, text):
        """
            Находит товары, содержащие заданный фрагмент текста, и выводит результат.
        """
        search_results = [item for item in self.data if text.lower() in item['name'].lower()]
        search_results = sorted(search_results, key=itemgetter('price_per_kg'))

        if not search_results:
            print("Совпадений не найдено.")
            return

        print(f"{'№':<4} {'Наименование':<30} {'Цена':<8} {'Вес':<8} {'Файл':<15} {'Цена за кг.':<10}")
        for i, item in enumerate(search_results, 1):
            print(
                f"{i:<4}"
                f" {item['name']:<30}"
                f" {item['price']:<8}"
                f" {item['weight']:<8}"
                f" {item['file']:<15} "
                f"{item['price_per_kg']:<10.1f}"
            )


pm = PriceMachine()
pm.load_prices()

while True:
    search_query = input("Введите название товара для поиска (или 'exit' для выхода): ")
    if search_query.lower() == 'exit':
        print("Работа завершена.")
        break
    pm.find_text(search_query)

pm.export_to_html()
