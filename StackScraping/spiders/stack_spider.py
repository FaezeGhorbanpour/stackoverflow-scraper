import scrapy
import time

from scrapy import Spider
from scrapy.selector import Selector
from stemming.porter2 import stem
from Stack_Scraping.items import Question,QuestionContent
from spacy.en import English
import string

class StackSpider(Spider):
    name = "stack"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/questions",
    ]

    BASE_URL = 'http://stackoverflow.com'

    def parse(self, response):
        item = Question()
        questions = Selector(response).xpath('//div[@class="question-summary"]')
        for question in questions:
            try:
                item['title']=question.xpath('div[@class="summary"]/h3/a[@class="question-hyperlink"]/text()').extract()[0]
                question_url = question.xpath('div[@class="summary"]/h3/a[@class="question-hyperlink"]/@href').extract()[0]
                item['url']=question_url
                last_url = response
                absolute_url = self.BASE_URL + question_url
                yield scrapy.Request(absolute_url, callback=self.each_page_parse)
                time.sleep(2)
                item['view']=question.xpath('div[@class="statscontainer"]/div[@class="views "]/@title').extract()[0]
                item['vote']=question.xpath('div[@class="statscontainer"]/div[@class="stats"]/div[@class="vote"]/div[@class="votes"]/span[@class="vote-count-post "]/strong/text()').extract()[0]
                if(len(question.xpath('div[@class="statscontainer"]/div[@class="stats"]/div[@class="status answered"]/strong/text()').extract())!=0):
                    item['answer']=question.xpath('div[@class="statscontainer"]/div[@class="stats"]/div[@class="status answered"]/strong/text()').extract()[0]
                else :
                    item['answer']="0"
                if(len(question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info "]/div[@class="user-details"]/a/@href').extract())!=0):
                    item['user_url']=question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info "]/div[@class="user-details"]/a/@href').extract()[0]
                    item['user_name']=question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info "]/div[@class="user-details"]/a/text()').extract()[0]
                    item['time']=question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info "]/div[@class="user-action-time"]/span/@title').extract()[0]
                else:
                    item['user_url']=question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info user-hover"]/div[@class="user-details"]/a/@href').extract()[0]
                    item['user_name']=question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info user-hover"]/div[@class="user-details"]/a/text()').extract()[0]
                    item['time']=question.xpath('div[@class="summary"]/div[@class="started fr"]/div[@class="user-info user-hover"]/div[@class="user-action-time"]/span/@title').extract()[0]
            except :
                print('errorha')
            yield item
        next_page =Selector(response).xpath('//*[@id="mainbar"]/div[4]/a[last()]/@href').extract()[0]
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def each_page_parse(self,response):
        item = QuestionContent()
        item['url']=response.url[25:]
        if (len(Selector(response).xpath('//*[@id="mainbar-full"]/div[1]/h1').extract()) != 0):
            item['status'] = 'Page Not Found'
        elif (len(Selector(response).xpath('//*[@id="question"]/table/tbody//div[@class="question-status"]')) != 0):
            item['status'] = 'Duplicated'
        else:
            question_text = Selector(response).xpath('//*[@id="mainbar"]/div[@class="question"]/table//div[@class="post-text"]/descendant::text()').extract()
            item['question'] = question_text
            comments = Selector(response).xpath('//*[@id="mainbar"]/div[@class="question"]/table//div[@class="comments "]//tr[@class="comment "]')
            item['comments'] = list()
            i = 0
            for comment in comments:
                i += 1
                comment_dict = dict()
                comment_dict['text'] = Selector(response).xpath('//*[@id="mainbar"]/div[@class="question"]/table//div[@class="comments "]//tr[@class="comment "][position() =' +str(i) + ']//span[@class="comment-copy"]/descendant::text()').extract()
                comment_dict['author'] = Selector(response).xpath('//*[@id="mainbar"]/div[@class="question"]/table//div[@class="comments "]//tr[@class="comment "][position() =' +str(i) + ']//a[@class="comment-user"]/@href').extract()
                comment_dict['date'] = Selector(response).xpath('//*[@id="mainbar"]/div[@class="question"]/table//div[@class="comments "]//tr[@class="comment "][position() =' +str(i) + ']//span[@class="comment-date"]/descendant::text()').extract()
                item['comments'].append(comment_dict)
            selected = Selector(response).xpath('//*[@id="answers"]//div[@class="answer accepted-answer"]/table')
            if (len(selected) != 0 ):
                selected_answer_dict = dict()
                selected_answer_dict['answer'] = Selector(response).xpath('//*[@id="answers"]//div[@class="answer accepted-answer"]/table//div[@class="post-text"]/descendant::text()').extract()
                selected_answer_dict['vote'] = Selector(response).xpath('//*[@id="answers"]//div[@class="answer accepted-answer"]/table//div[@class="vote"]/span[@class="vote-count-post "]/text()').extract()
                selected_answer_dict['author'] =Selector(response).xpath('//*[@id="answers"]//div[@class="answer accepted-answer"]/table//table//td[@class="post-signature"]//div[@class="user-gravatar32"]/a/@href').extract()
                selected_answer_dict['date'] = Selector(response).xpath('//*[@id="answers"]//div[@class="answer accepted-answer"]/table//table//td[@class="post-signature"]//div[@class="user-action-time"]//span/text()').extract()
                item['selected_answer'] = selected_answer_dict
            answers = Selector(response).xpath('//*[@id="answers"]/div[@class="answer"]')
            item['answers'] = list()
            i = 0
            for answer in answers:
                i += 1
                answer_dict = dict()
                answer_dict['text'] = Selector(response).xpath('//*[@id="answers"]/div[@class="answer"][position() =' +str(i) + ']//table//div[@class="post-text"]/descendant::text()').extract()
                answer_dict['vote'] = Selector(response).xpath('//*[@id="answers"]/div[@class="answer"][position() =' +str(i) + ']//table//div[@class="vote"]/span[@class="vote-count-post "]/text()''').extract()
                answer_dict['author'] =Selector(response).xpath('//*[@id="answers"]/div[@class="answer"][position() =' +str(i) + ']//table//td[@class="post-signature"]//div[@class="user-gravatar32"]/a/@href').extract()
                answer_dict['date'] = Selector(response).xpath('//*[@id="answers"]/div[@class="answer"][position() =' +str(i) + ']//table//td[@class="post-signature"]//div[@class="user-action-time"]//span/text()').extract()
                item['answers'].append(answer_dict)
        return item

def preprocess(str):
    parser = English()
    temp_ans = ''.join(str)
    predicate = lambda x: x not in string.punctuation
    answer = list(filter(predicate, temp_ans.lower()))
    ans_u = answer.decode('utf-8', errors='ignore')
    tokens = parser(ans_u)
    tokens = [token.orth_ for token in tokens if not token.orth_.isspace()]
    answer_tokens = [stem(i) for i in tokens]
    return answer,answer_tokens

#random_forest