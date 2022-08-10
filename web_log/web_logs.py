import logging
from logging import handlers
from config import LOG_PATH


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename=LOG_PATH, level='debug', when='D', backCount=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        '''调用Logger类设定日志文件名称,以操作日志方法'''
        self.logger = logging.getLogger(filename)
        '''设置日志格式'''
        format_str = logging.Formatter(fmt)
        '''设置日志级别'''
        self.logger.setLevel(self.level_relations.get(level))
        '''屏幕输出日志信息'''
        sh = logging.StreamHandler()
        '''设置屏幕日志信息格式'''
        sh.setFormatter(format_str)
        '''指定间隔时间自动生成日志文件'''
        th = handlers.TimedRotatingFileHandler(filename=LOG_PATH, when=when, backupCount=backCount, encoding='utf-8')
        '''设定写入文件的日志格式'''
        th.setFormatter(format_str)
        '''日志信息添加到Logger类变量hanlers列表中'''
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


