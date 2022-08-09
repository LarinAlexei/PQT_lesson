from subprocess import Popen, PIPE
import platform
from ipaddress import ip_address
import socket
from threading import Thread
import chardet


def ping_host(hosts: list, num_ping: int = 2):
    '''
    Проверка сетевых узлов которые доступны:
    :param hosts: списки сетевых узлов, представленных от имени хоста или IP-адресом.
    :param num_ping: кол-во совершаемых пингов, которое выполниться (два идет по умолчанию).
    :return: спсок с результатом их проверок.
    '''
    RESULTS = []  # список с результатами
    PARAM = '-n' if platform.system().lower() == 'windows' else '-c'
    threads = []  # список с потоками

    def worker_thread(host):
        '''
        Функция реализовывается в многопоточность и добавляет результат запросов в словарь RESULTS.
        В аргументе host можем поместить имя хоста, а также IP-адрес.
        Наша функция возможность пингов в локальной сети, где ответ Popen может не корректно интерпретироваться
        (а точнее, он будет 0 для несуществующих узлов).
        '''
        check_number_ip: int  # проверка кол-во IP-адресов в ответе
        ip = ''
        try:
            ip = ip_address(socket.gethostbyname(host))
            reachable = True
        except Exception:
            reachable = False
        if reachable:
            args = ['ping', PARAM, str(num_ping), str(ip)]
            reply = Popen(args, shell=True, stdout=PIPE)
            code = reply.wait()
            reachable = True if code == 0 else False
            # Если хост локальный, то ответ должен быть более двух значений пингуемого IP, если он доступен
            reply_text = reply.stdout.read()
            encoding = chardet.detect(reply_text).get('encoding', None)
            reply_text = reply_text.decode(encoding)
            check_number_ip = reply_text.count(str(ip)) > 2
        # добавим результат проверки в список
        RESULTS.append(f'Узел {host} ({ip})'
                       f"{'доступен' if reachable and check_number_ip else 'недоступен'}!\n")

    # создание потоков для проверки хоста
    for host in hosts:
        t = Thread(target=worker_thread, args=(host,))
        threads.append(t)
        t.start()
    # ждем завершения работы потоков
    [thread.join() for thread in threads]
    return RESULTS


# Проверяем решения
urls_list = ['google.com', 'yandex.ru', '8.8.8.8', '192.168.0.131']

print(*ping_host(urls_list), sep='')


'''
Получили на выходе:
Узел yandex.ru (5.255.255.77)доступен!
Узел 8.8.8.8 (8.8.8.8)доступен!
Узел google.com (64.233.164.100)доступен!
Узел 192.168.0.131 (192.168.0.131)недоступен!
'''


