import scrapy


class Question(scrapy.Item):
    user_name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    vote = scrapy.Field()
    view = scrapy.Field()
    time = scrapy.Field()
    answer = scrapy.Field()
    user_url = scrapy.Field()

class QuestionContent(scrapy.Item):
    url = scrapy.Field()
    question = scrapy.Field()
    selected_answer = scrapy.Field()
    answers = scrapy.Field()
    status = scrapy.Field()
    question_tokens = scrapy.Field()
    selected_answer_to = scrapy.Field()
    answers_tokens = scrapy.Field()
    comments = scrapy.Field()


