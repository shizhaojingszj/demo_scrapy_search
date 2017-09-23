import json
import codecs


class JsonLinePipeline(object):

    def open_spider(self, spider):

        self.file = codecs.open("test_utf8.jl", 'w', encoding="utf-8")

    def close_spider(self, spider):

        self.file.close()

    def process_item(self, item, spider):

        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
