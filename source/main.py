import argparse
import json
from datetime import datetime
from collections import defaultdict
from tabulate import tabulate

from strateges import AverageReportStrategy


class LogAnalyzer:
    """
    Класс для анализа лог-файлов и генерации отчетов.
    
    Атрибуты:
        logs (list): Список загруженных логов
        args (argparse.Namespace): Аргументы командной строки
        date (datetime.datetime): Дата для фильтрации логов (опционально)
    """
    
    strateges = {
        'average': AverageReportStrategy,
    }
    
    def __init__(self):
        """Инициализирует анализатор, парсит аргументы командной строки."""
        self.args = self._parse_args()
        self.logs = []
    
    def _parse_args(self) -> argparse.Namespace:
        """
        Парсит аргументы командной строки.
        
        Возвращает:
            argparse.Namespace: Объект с разобранными аргументами
        """
        parser = argparse.ArgumentParser(description='Process log files and generate reports.')
        parser.add_argument('--file', nargs='+', required=True, help='Path to log file(s)')
        parser.add_argument('--report', choices=['average'], required=True, help='Type of report to generate')
        parser.add_argument('--date', help='Filter logs by date (format: YYYY-MM-DD)')
        return parser.parse_args()
    
    def load_logs(self) -> None:
        """Загружает логи из указанных файлов."""
        self.logs = []
        for file_path in self.args.file:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        self.logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    
    def filter_logs_by_date(self) -> None:
        """
        Фильтрует логи по дате, если указан параметр --date.
        
        Оставляет только логи, соответствующие указанной дате.
        """
        if not self.args.date:
            return
        
        try:
            target_date = datetime.strptime(self.args.date, '%Y-%m-%d').date()
        except ValueError:
            return
        
        filtered_logs = []
        for log in self.logs:
            if '@timestamp' not in log:
                continue
            try:
                log_time = datetime.fromisoformat(log['@timestamp']).date()
                if log_time == target_date:
                    filtered_logs.append(log)
            except ValueError:
                continue
        
        self.logs = filtered_logs
    
    def print_report(self, report_headers, report_data: list) -> None:
        """
        Выводит отчет в консоль в табличном формате.
        
        Аргументы:
            report_headers (list): Заголовки для отчета
            report_data (list): Данные для отчета
        """
        
        print(tabulate(report_data, headers=report_headers, tablefmt='grid'))
    
    def run(self) -> None:
        """Основной метод для запуска анализатора."""
        
        self.load_logs()
        self.filter_logs_by_date()
        
        strategy = self.strateges.get(self.args.report)()
        
        if strategy:
            report_headers = strategy.headers
            report_data = strategy.generate(self.logs)
            self.print_report(report_headers, report_data)


if __name__ == '__main__':
    analyzer = LogAnalyzer()
    analyzer.run()