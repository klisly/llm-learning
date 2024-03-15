from transformers import pipeline
'''
将文本预处理为模型可以理解的格式；
将预处理好的文本送入模型；
对模型的预测值进行后处理，输出人类可以理解的格式。
'''
# print("sentiment-analysis")
# classifier = pipeline("sentiment-analysis")
# result = classifier("I've been waiting for a HuggingFace course my whole life.")
# print(result)
# results = classifier(
#   ["I've been waiting for a HuggingFace course my whole life.", "I hate this so much!"]
# )
# print(results)

# from transformers import pipeline

# print("零样本分类")
# classifier = pipeline("zero-shot-classification")
# result = classifier(
# "This is a course about the Transformers library",
# candidate_labels=["education", "politics", "business"],
# )
# print(result)

from transformers import pipeline

# print("文本生成")
# generator = pipeline("text-generation")
# results = generator("In this course, we will teach you how to")
# print(results)
# results = generator(
#     "In this course, we will teach you how to",
#     num_return_sequences=2,
#     max_length=50
# ) 
# print(results)

# from transformers import pipeline

# generator = pipeline("text-generation", model="uer/gpt2-chinese-poem")
# results = generator(
#     "[CLS] 你 再 看 着 我，",
#     max_length=40,
#     num_return_sequences=2,
# )
# print(results)

# 遮盖词填充
# print("遮盖词填充")
# from transformers import pipeline

# unmasker = pipeline("fill-mask")
# results = unmasker("This course will teach you all about <mask> models.", top_k=2)
# print(results)

# NER 
# from transformers import pipeline

# print("NER")
# ner = pipeline("ner", grouped_entities=True)
# results = ner("My name is Sylvain and I work at Hugging Face in Brooklyn.")
# print(results)


# from transformers import pipeline
# print("自动问答")
# question_answerer = pipeline("question-answering")
# answer = question_answerer(
#     question="Where do I work?",
#     context="My name is Sylvain and I work at Hugging Face in Brooklyn",
# )
# print(answer)

from transformers import pipeline
print("自动文本摘要")
summarizer = pipeline("summarization")
results = summarizer(
    """
    America has changed dramatically during recent years. Not only has the number of 
    graduates in traditional engineering disciplines such as mechanical, civil, 
    electrical, chemical, and aeronautical engineering declined, but in most of 
    the premier American universities engineering curricula now concentrate on 
    and encourage largely the study of engineering science. As a result, there 
    are declining offerings in engineering subjects dealing with infrastructure, 
    the environment, and related issues, and greater concentration on high 
    technology subjects, largely supporting increasingly complex scientific 
    developments. While the latter is important, it should not be at the expense 
    of more traditional engineering.

    Rapidly developing economies such as China and India, as well as other 
    industrial countries in Europe and Asia, continue to encourage and advance 
    the teaching of engineering. Both China and India, respectively, graduate 
    six and eight times as many traditional engineers as does the United States. 
    Other industrial countries at minimum maintain their output, while America 
    suffers an increasingly serious decline in the number of engineering graduates 
    and a lack of well-educated engineers.
    """
)
print(results)