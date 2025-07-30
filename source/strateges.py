from collections import defaultdict
from abc import ABC, abstractmethod

class ReportStrategy(ABC):
    """Абстрактный базовый класс для стратегий генерации отчетов."""
    
    @abstractmethod
    def generate(self, logs: list) -> list:
        """Генерирует отчет на основе логов.
        
        Args:
            logs (list): Список логов для анализа
            
        Returns:
            list: Данные для отчета
        """
        pass
    
    @property
    @abstractmethod
    def headers(self) -> list:
        """Возвращает заголовки для отчета.
        
        Returns:
            list: Список заголовков
        """
        pass

class AverageReportStrategy(ReportStrategy):
    """Стратегия для генерации отчета о среднем времени ответа."""
    
    @property
    def headers(self) -> list:
        return ['Endpoint', 'Requests Count', 'Average Response Time']
    
    def generate(self, logs: list) -> list:
        endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0})
        
        for log in logs:
            if 'url' not in log or 'response_time' not in log:
                continue
            
            path = log['url']
            try:
                response_time = float(log['response_time'])
            except (ValueError, TypeError):
                continue
            
            endpoint_stats[path]['count'] += 1
            endpoint_stats[path]['total_time'] += response_time
        
        report_data = []
        for path, stats in endpoint_stats.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            report_data.append([path, stats['count'], f"{avg_time:.3f}"])

        return report_data