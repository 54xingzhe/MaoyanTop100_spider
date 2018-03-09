import requests
from requests.exceptions import RequestException  # request异常处理
import re
import json
from multiprocessing import Pool

# 请求单页内容，将url当做参数传入
def get_one_page(url):
    try:  # request异常处理
        response = requests.get(url)  # 获取url请求
        if response.status_code == 200:  # 如果返回状态码是200，请求成功
            return response.text
        return None
    except RequestException:
        return None

# 对网页进行解析
def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)  # re.S 匹配任意字符包括换行符；只用“.”匹配不加re.S ，无法匹配到换行符
    items = re.findall(pattern, html)
    # print(items)  # 提取到的信息是一个列表，每个元素是一个元组
    for item in items:  # 将提取信息进行格式化
        yield{
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],  # 用切片方法将字符串前三个字符（主演：）去掉
            'time': item[4].strip()[5:],
            'score': item[5]+item[6]
        }  # 用yield写成一个生成器，将信息以字典的形式返回

# 写入到文件
def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:  # 利用with as 方法，'a'表示追加写入文件，encoding='utf-8'表示用utf-8编码
        f.write(json.dumps(content, ensure_ascii=False) + '\n')  # 传入的参数content是一个字典的形式，用json.dumps方法转变为字符串；json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False;
        f.close()

def main(offset):  # offset是页码参数，将offset传入，可以循环抓取每一页
    url = 'http://maoyan.com/board/4?offset=' + str(offset)  # 将页码参数拼接到url上
    html = get_one_page(url)
    # print(html)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)

if __name__ == '__main__':  # 该判断语句为真的时候，说明当前运行的脚本为主程序，而非主程序所引用的一个模块。这在当你想要运行一些只有在将模块当做程序运行时而非当做模块引用时才执行的命令，只要将它们放到if __name__ == "__main__:"判断语句之后就可以了。
    # for i in range(10):
    #     main(i*10)  # 利用for循环动态改变页码参数
    pool = Pool()  # 声明一个进程池,池没满的话就创建一个新的进程，池满的话就进行等待。
    pool.map(main, [i*10 for i in range(10)])  # map()方法将数组中每个元素拿出来，当做函数的参数创建一个个进程放入到进程池里面去运行，